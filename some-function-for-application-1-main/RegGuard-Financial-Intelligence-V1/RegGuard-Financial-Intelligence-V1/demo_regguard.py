"""Run an entirely invented case with no real firms, clients or allegations."""
import json
import sqlite3
from pathlib import Path
import pandas as pd

from regguard.registry import run_named_operation
from regguard.workflow import init_case_store,open_case,review_case,case_history

as_of='2026-10-13'
base=Path(__file__).parent/'examples'
filings=pd.read_csv(base/'fictional_filings.csv',dtype=str)
audit=pd.read_csv(base/'fictional_audit.csv',dtype=str)
pledges=pd.read_csv(base/'fictional_pledges.csv',dtype=str)
from regguard.normalize import normalize_source
filings=normalize_source(filings,'cd80_anns_d')

a=run_named_operation('regguard.audit_opinion_review',audits=audit,as_of=as_of)
p=run_named_operation('regguard.pledge_risk_review',pledges=pledges,as_of=as_of)
f=run_named_operation('regguard.filing_event_triage',filings=filings,as_of=as_of)
alerts=run_named_operation('regguard.consolidate_alerts',audit_reviews=a,pledge_reviews=p,filing_events=f,as_of=as_of)
digest=run_named_operation('regguard.build_digest',alerts=alerts,as_of=as_of)
with sqlite3.connect(':memory:') as con:
    init_case_store(con)
    open_case(con,'DEMO-001','DEMO001.SZ','AUDIT_REVIEW','2026-06-01')
    review_case(con,'DEMO-001','demo-reviewer','in_review','人工核对全文前保持待确认状态')
    digest['sample_case_history']=case_history(con,'DEMO-001')
print(json.dumps({'audit':a,'pledge':p,'filing_titles':f,'digest':digest},
                 ensure_ascii=False,indent=2,default=str))
