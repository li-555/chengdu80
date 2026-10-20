"""Accounting quality checks and holdings concentration using delivered Tushare field dictionary."""
from __future__ import annotations
import pandas as pd
import numpy as np
from .fundamentals import point_in_time_indicators


def cash_earnings_quality(income:pd.DataFrame,cashflow:pd.DataFrame,as_of:str)->list[dict]:
    """Compare attributable net income to operating cash flows, aligned fiscal period.

    Tushare income.n_income_attr_p and cashflow.n_cashflow_act are cumulative
    reporting period amounts (typically YTD for quarters): compare like periods.
    """
    for name,df,columns in [('income',income,{'ts_code','end_date','ann_date','n_income_attr_p'}),
                             ('cashflow',cashflow,{'ts_code','end_date','ann_date','n_cashflow_act'})]:
        if not columns.issubset(df.columns):raise ValueError(f'{name} missing fields: {sorted(columns-set(df.columns))}')
    def latest(df):
        x=df.copy()
        x['end_date']=pd.to_datetime(x.end_date)
        x['ann_date']=pd.to_datetime(x.ann_date)
        x['f_ann_date']=pd.to_datetime(x.get('f_ann_date',x.ann_date),errors='coerce')
        x['available_at']=pd.concat([x.ann_date,x.f_ann_date],axis=1).max(axis=1)
        x=x[(x.available_at<=pd.Timestamp(as_of))&(x.end_date<=pd.Timestamp(as_of))]
        return x.sort_values('available_at').drop_duplicates(['ts_code','end_date'],keep='last')
    inc=latest(income)[['ts_code','end_date','available_at','n_income_attr_p']].rename(columns={'available_at':'income_available_at'})
    cf=latest(cashflow)[['ts_code','end_date','available_at','n_cashflow_act']].rename(columns={'available_at':'cashflow_available_at'})
    merged=inc.merge(cf,on=['ts_code','end_date'],validate='one_to_one')
    if merged.empty:return []
    merged=merged.sort_values('end_date').drop_duplicates('ts_code',keep='last')
    out=[]
    for _,r in merged.iterrows():
        ni=pd.to_numeric(r.n_income_attr_p,errors='coerce');ocf=pd.to_numeric(r.n_cashflow_act,errors='coerce')
        ratio=float(ocf/ni) if pd.notna(ni) and pd.notna(ocf) and ni>0 else None
        out.append({'ts_code':str(r.ts_code),'report_period':r.end_date.date().isoformat(),
                    'income_available_at':r.income_available_at.date().isoformat(),
                    'cashflow_available_at':r.cashflow_available_at.date().isoformat(),
                    'attributable_net_income':float(ni) if pd.notna(ni) else None,
                    'operating_cashflow':float(ocf) if pd.notna(ocf) else None,
                    'ocf_to_net_income':ratio,
                    'review_flag':bool(ratio is not None and ratio<0.5),
                    'limitations':'<0.5为用户可调的研究阈值示例，不能推断财务舞弊；收入及现金流指标须核对报告类型/会计单位'})
    return out


def top_holder_concentration(holdings:pd.DataFrame,as_of:str)->list[dict]:
    """Top-10 shareholder concentration, not controller identity resolution."""
    req={'ts_code','ann_date','end_date','holder_name','hold_ratio'}
    if not req.issubset(holdings):raise ValueError(f'Missing: {sorted(req-set(holdings))}')
    x=holdings.copy();x['ann_date']=pd.to_datetime(x.ann_date);x['end_date']=pd.to_datetime(x.end_date)
    x=x[(x.ann_date<=pd.Timestamp(as_of))&(x.end_date<=pd.Timestamp(as_of))]
    if x.empty:return []
    last=x.groupby('ts_code')['end_date'].transform('max');x=x[x.end_date==last]
    rows=[]
    for code,g in x.groupby('ts_code'):
        if g['ann_date'].nunique()>1:g=g[g.ann_date==g.ann_date.max()]
        ratios=pd.to_numeric(g.hold_ratio,errors='coerce').dropna()
        rows.append({'ts_code':code,'report_period':g.end_date.max().date().isoformat(),
                     'published_at':g.ann_date.max().date().isoformat(),
                     'total_top10_percent':float(ratios.sum()) if len(ratios) else None,
                     'holder_count':len(g),'warning':'股权集中度不是法律意义上的实控人识别'})
    return rows
