"""Evidence-first research alerts and LLM factual evidence packs."""
from __future__ import annotations
from datetime import date
from urllib.parse import urlparse
from collections import Counter
import pandas as pd

PRIORITIES={'critical_review':4,'high':3,'medium':2,'low':1,'review':1}

def consolidate_alerts(financial_scans:list[dict]|None=None,
                       audit_reviews:list[dict]|None=None,
                       pledge_reviews:list[dict]|None=None,
                       filing_events:list[dict]|None=None,
                       as_of:str='2026-10-13')->list[dict]:
    """No composite 'fraud score'; retain independent findings with evidence level."""
    cutoff=pd.Timestamp(as_of)
    out=[]
    for scan in financial_scans or []:
        code=scan.get('ts_code')
        if scan.get('status')=='unsupported_financial_company':continue
        for rule in scan.get('rules',[]):
            if rule.get('status')!='triggered':continue
            stamp=scan.get('available_at')
            if not stamp or pd.Timestamp(stamp)>cutoff:continue
            out.append({'ts_code':code,'alert_id':rule['rule_id'],'available_at':stamp,
                        'source_type':'financial_rule','evidence_level':'structured_calculation',
                        'detail':rule.get('reason'),'rule_version':rule.get('rule_version'),
                        'observed':rule.get('observed'),'threshold':rule.get('threshold'),
                        'source_url':None,'review_priority':rule.get('review_priority') or 'review',
                        'review_status':'unreviewed'})
    for r in audit_reviews or []:
        if r.get('status')!='requires_review':continue
        stamp=r.get('available_at')
        if not stamp or pd.Timestamp(stamp)>cutoff:continue
        out.append({'ts_code':r.get('ts_code'),'alert_id':'AUDIT_REVIEW','available_at':stamp,
                    'source_type':'audit','evidence_level':r.get('evidence_level'),
                    'detail':r.get('opinion_original'),'source_url':r.get('source_url'),
                    'review_priority':'high' if r.get('opinion_type') in ('adverse','disclaimer') else 'medium',
                    'review_status':'unreviewed'})
    for r in pledge_reviews or []:
        if r.get('status')!='triggered':continue
        stamp=r.get('available_at')
        if not stamp or pd.Timestamp(stamp)>cutoff:continue
        out.append({'ts_code':r.get('ts_code'),'alert_id':'SHARE_PLEDGE','available_at':stamp,
                    'source_type':'pledge','evidence_level':r.get('evidence_level'),
                    'detail':r.get('flags'),'observed':r.get('issuer_pledge_ratio_pct'),
                    'source_url':None,'review_priority':'medium','review_status':'unreviewed'})
    for r in filing_events or []:
        stamp=r.get('published_at')
        if not stamp or pd.Timestamp(stamp)>cutoff:continue
        out.append({'ts_code':r.get('ts_code'),'alert_id':'DISCLOSURE_TITLE','available_at':stamp,
                    'source_type':'filing_title','evidence_level':'title_only',
                    'detail':r.get('categories'),'source_url':r.get('source_url'),
                    'review_priority':'review','review_status':'unreviewed'})
    return sorted(out,key=lambda r:(PRIORITIES.get(r.get('review_priority'),0),r['available_at']),reverse=True)


def build_digest(alerts:list[dict],as_of:str,period_label:str='daily')->dict:
    valid=[a for a in alerts if a.get('available_at') and pd.Timestamp(a['available_at'])<=pd.Timestamp(as_of)]
    return {'as_of':as_of,'period':period_label,'alert_count':len(valid),
            'issuer_count':len(set(a['ts_code'] for a in valid)),
            'by_type':dict(Counter(a['source_type'] for a in valid)),
            'needs_human_review':sum(a.get('review_status')=='unreviewed' for a in valid),
            'alerts':valid,
            'caution':'此表是已披露证据的待查线索汇总，不构成舞弊定论、违法认定或投资建议。'}


def build_evidence_pack(company:str,question:str,evidence:list[dict],as_of:str)->dict:
    """Only validated source-anchored facts. LLM summarizer invoked by approved Blocks interface."""
    if not company.strip() or len(question.strip())<3:raise ValueError('company/question required')
    cutoff=pd.Timestamp(as_of)
    items=[]
    for i,r in enumerate(evidence):
        url=str(r.get('source_url') or '')
        p=urlparse(url)
        stamp=pd.to_datetime(r.get('published_at'),errors='coerce')
        excerpt=str(r.get('excerpt') or '').strip()
        if p.scheme!='https' or not p.hostname or pd.isna(stamp) or stamp>cutoff or not excerpt:
            continue
        items.append({'evidence_id':str(r.get('id') or f'EV-{i+1}'),
                      'published_at':stamp.date().isoformat(),
                      'source_url':url,'excerpt':excerpt[:1200],
                      'page':r.get('page'),'evidence_level':str(r.get('evidence_level') or 'provided_excerpt')})
    return {'company':company,'question':question,'as_of':as_of,
            'evidence':items,'evidence_count':len(items),'status':'ready_for_approved_llm' if items else 'insufficient_evidence',
            'llm_instructions':'仅使用证据片段并引用 evidence_id；区分财务指标、推断、调查、行政处罚和生效裁判。若无证据，答无法核实；不得补写未给出的全文。',
            'output_schema':{'findings':'array','citations':'array','unknowns':'array','human_review_required':'boolean'}}
