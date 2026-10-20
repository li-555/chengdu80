"""Sector research without inventing causal explanations.

Daily pct_chg from cd80_daily is **percent**, not a fraction. Membership must
already be filtered to as-of date by `industry_membership`.
"""
from __future__ import annotations
import pandas as pd
import numpy as np
from .industry import industry_membership


def industry_daily_breadth(daily:pd.DataFrame,members:pd.DataFrame,as_of:str,level:int=1)->list[dict]:
    req={'ts_code','trade_date','pct_chg','amount'}
    if not req.issubset(daily):raise ValueError(f'Missing price data: {sorted(req-set(daily))}')
    mapping=industry_membership(members,as_of,level=level)
    if not mapping:return []
    f=daily.copy();f['trade_date']=pd.to_datetime(f.trade_date)
    f=f[f.trade_date<=pd.Timestamp(as_of)]
    if f.empty:return []
    date=f.trade_date.max();f=f[f.trade_date==date]
    f=f.merge(pd.DataFrame(mapping)[['ts_code','industry']],on='ts_code',how='inner')
    f['pct_chg']=pd.to_numeric(f.pct_chg,errors='coerce')
    f['amount']=pd.to_numeric(f.amount,errors='coerce')
    out=[]
    for name,g in f.groupby('industry'):
        valid=g.pct_chg.dropna()
        out.append({'industry':name,'as_of_trade_date':date.date().isoformat(),
                    'covered_stocks':len(valid),'breadth_positive_pct':float((valid>0).mean()*100) if len(valid) else None,
                    'median_daily_return_pct':float(valid.median()) if len(valid) else None,
                    'equal_weight_mean_return_pct':float(valid.mean()) if len(valid) else None,
                    'sample_turnover_1000cny':float(g.amount.sum()) if g.amount.notna().any() else None,
                    'caveat':'未覆盖的成分股和停牌会影响统计；未证明行业变化的宏观原因'})
    return sorted(out,key=lambda v:v['industry'])
