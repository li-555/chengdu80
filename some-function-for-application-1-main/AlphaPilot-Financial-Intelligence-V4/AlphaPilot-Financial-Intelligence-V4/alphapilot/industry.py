"""Point-in-time industry membership, avoiding knowledge of future index component entries."""
from __future__ import annotations
import pandas as pd

def industry_membership(frame:pd.DataFrame,as_of:str,level:int=1)->list[dict]:
    if level not in [1,2,3]:raise ValueError('level is 1–3')
    fields={'ts_code','in_date','out_date',f'l{level}_name'}
    if not fields.issubset(frame.columns):raise ValueError(f'Missing fields: {sorted(fields-set(frame))}')
    f=frame.copy()
    f['in_date']=pd.to_datetime(f['in_date'],errors='coerce')
    f['out_date']=pd.to_datetime(f['out_date'],errors='coerce')
    t=pd.Timestamp(as_of)
    active=f[(f.in_date<=t)&(f.out_date.isna()|(f.out_date>t))]
    return [{'ts_code':str(r.ts_code),'industry':str(getattr(r,f'l{level}_name')),'level':level,'as_of':as_of}
            for r in active.itertuples()]
