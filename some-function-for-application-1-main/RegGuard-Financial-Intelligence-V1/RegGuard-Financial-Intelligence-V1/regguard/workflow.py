"""Small single-user local prototype for traceable reviewer decisions.
Authentication, tenant isolation, permissions, scheduler and backup belong to Blocks.
This record is append-only via application methods, not tamper-proof legal evidence.
"""
from __future__ import annotations
import json
import sqlite3
import hashlib
from datetime import datetime, timezone
from urllib.parse import urlparse

ALLOWED_STATUSES={'unreviewed','in_review','confirmed_indicator','dismissed','escalated'}
ALLOWED_CASE_STATES={'not_checked','investigation','allegation','final_decision','dismissed','unknown'}

def init_case_store(con:sqlite3.Connection):
    con.execute('''CREATE TABLE IF NOT EXISTS cases (
        case_id TEXT PRIMARY KEY, ts_code TEXT NOT NULL, signal_type TEXT NOT NULL,
        observed_at TEXT NOT NULL, rule_version TEXT NOT NULL,
        status TEXT NOT NULL, created_at TEXT NOT NULL)''')
    con.execute('''CREATE TABLE IF NOT EXISTS case_events (
        event_id INTEGER PRIMARY KEY AUTOINCREMENT, case_id TEXT NOT NULL,
        actor TEXT NOT NULL, event_time TEXT NOT NULL, status TEXT NOT NULL,
        case_state TEXT NOT NULL, note TEXT NOT NULL,
        evidence_url TEXT, previous_digest TEXT, digest TEXT NOT NULL,
        FOREIGN KEY(case_id) REFERENCES cases(case_id))''')
    con.commit()

def _utc():return datetime.now(timezone.utc).isoformat()

def open_case(con:sqlite3.Connection,case_id:str,ts_code:str,signal_type:str,
              observed_at:str,rule_version:str='research-v1')->dict:
    if not all(str(x).strip() for x in [case_id,ts_code,signal_type,observed_at,rule_version]):
        raise ValueError('missing required case identity')
    stamp=_utc()
    con.execute('INSERT INTO cases VALUES(?,?,?,?,?,?,?)',
                (case_id,ts_code,signal_type,observed_at,rule_version,'unreviewed',stamp))
    con.commit()
    return {'case_id':case_id,'status':'unreviewed','created_at':stamp}

def review_case(con:sqlite3.Connection,case_id:str,actor:str,status:str,
                note:str,case_state:str='not_checked',evidence_url:str|None=None)->dict:
    if status not in ALLOWED_STATUSES or case_state not in ALLOWED_CASE_STATES:
        raise ValueError('unrecognised review status')
    if not actor.strip() or not note.strip():raise ValueError('reviewer and note are required')
    if status in {'confirmed_indicator','escalated'} and (not evidence_url or case_state=='not_checked'):
        raise ValueError('escalation requires evidence_url and documented case_state')
    if evidence_url:
        parsed=urlparse(evidence_url)
        if parsed.scheme != 'https' or not parsed.hostname:raise ValueError('evidence must be an HTTPS URL')
    curr=con.execute('SELECT status FROM cases WHERE case_id=?',(case_id,)).fetchone()
    if not curr:raise ValueError('unknown case_id')
    prev=con.execute('SELECT digest FROM case_events WHERE case_id=? ORDER BY event_id DESC LIMIT 1',(case_id,)).fetchone()
    old_hash=prev[0] if prev else ''
    stamp=_utc()
    payload=json.dumps({'case_id':case_id,'actor':actor,'time':stamp,'status':status,
                        'case_state':case_state,'note':note,'evidence_url':evidence_url,
                        'previous_digest':old_hash},ensure_ascii=False,sort_keys=True)
    digest=hashlib.sha256(payload.encode()).hexdigest()
    with con:
        con.execute('''INSERT INTO case_events
                  (case_id,actor,event_time,status,case_state,note,evidence_url,previous_digest,digest)
                  VALUES(?,?,?,?,?,?,?,?,?)''',
                  (case_id,actor,stamp,status,case_state,note,evidence_url,old_hash,digest))
        con.execute('UPDATE cases SET status=? WHERE case_id=?',(status,case_id))
    return {'case_id':case_id,'status':status,'actor':actor,'case_state':case_state,
            'event_time':stamp,'digest':digest}

def case_history(con:sqlite3.Connection,case_id:str)->list[dict]:
    data=con.execute('''SELECT actor,event_time,status,case_state,note,evidence_url,
                               previous_digest,digest FROM case_events WHERE case_id=? ORDER BY event_id''',
                     (case_id,)).fetchall()
    cols=['actor','event_time','status','case_state','note','evidence_url','previous_digest','digest']
    return [dict(zip(cols,r)) for r in data]
