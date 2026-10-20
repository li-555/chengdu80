"""Point-in-time F10 and industry peer analysis. Indicator units are vendor-defined percentages.

Conservative publication timestamp max(ann_date,f_ann_date); no post-asof revisions.
"""
from __future__ import annotations
import math
import pandas as pd
import numpy as np

F10_METRICS = {
    'roe': {'label':'净资产收益率 ROE', 'direction':'higher','unit':'percent'},
    'gross_margin': {'label':'毛利率', 'direction':'higher','unit':'percent'},
    'debt_to_assets': {'label':'资产负债率', 'direction':'lower','unit':'percent'},
    'or_yoy': {'label':'营业收入同比增速', 'direction':'higher','unit':'percent'},
    'netprofit_yoy': {'label':'净利润同比增速', 'direction':'higher','unit':'percent'},
    'ocf_yoy': {'label':'经营现金流同比增速', 'direction':'higher','unit':'percent'},
    'current_ratio': {'label':'流动比率', 'direction':'higher','unit':'ratio'},
    'ocf_to_debt': {'label':'经营现金流/负债', 'direction':'higher','unit':'vendor-defined'},
    'net_profit_ratio': {'label':'销售净利率', 'direction':'higher','unit':'percent'},
}


def point_in_time_indicators(frame: pd.DataFrame, as_of: str) -> pd.DataFrame:
    """One *as-known-at-as_of* row per company and reporting period.

    Report end and publication dates are distinct. For revisions, take last release
    available by `as_of` for each (ts_code,end_date); then latest period per stock.
    """
    required={'ts_code','end_date','ann_date'}
    if not required.issubset(frame.columns):
        raise ValueError(f'Missing financial fields: {sorted(required - set(frame.columns))}')
    if frame.empty:
        return frame.copy()
    f=frame.copy()
    f['end_date']=pd.to_datetime(f['end_date'],errors='coerce')
    f['ann_date']=pd.to_datetime(f['ann_date'],errors='coerce')
    if 'f_ann_date' in f:
        actual=pd.to_datetime(f['f_ann_date'],errors='coerce')
        f['available_at']=pd.concat([f['ann_date'],actual],axis=1).max(axis=1)
    else:
        f['available_at']=f['ann_date']
    cutoff=pd.Timestamp(as_of)
    f=f.loc[f.available_at.notna() & (f.available_at <= cutoff) & (f.end_date <= cutoff)]
    f=f.sort_values(['ts_code','end_date','available_at'])
    return f.drop_duplicates(['ts_code','end_date'],keep='last').groupby('ts_code',group_keys=False).tail(1).reset_index(drop=True)


def f10_cards(indicators:pd.DataFrame, as_of:str) -> list[dict]:
    """F10 cards with missing fields / publication dates and explicit metrics."""
    snap=point_in_time_indicators(indicators,as_of)
    cards=[]
    for _,row in snap.iterrows():
        measures={}
        for key,meta in F10_METRICS.items():
            value=pd.to_numeric(row.get(key),errors='coerce')
            measures[key]={**meta,'value':float(value) if pd.notna(value) and np.isfinite(value) else None}
        cards.append({'ts_code':str(row.ts_code),'period':row.end_date.date().isoformat(),
                      'published_at':row.available_at.date().isoformat(),
                      'data_asof':str(as_of),'source':'Tushare fina_indicator / cd80_stock_fin_indicator',
                      'metrics':measures, 'missing_metrics':[k for k,v in measures.items() if v['value'] is None],
                      'investment_advice':False})
    return cards


def compare_fundamentals(indicators:pd.DataFrame, valuation:pd.DataFrame, as_of:str,
                         codes:list[str], metric_weights:dict[str,float]|None=None) -> dict:
    """Transparent peer-percentiles, *not* a model-predicted buy rating.

    Only stocks with a matching report period are scored. Valuations are as-of
    the latest available <= as_of; negative/zero PE excluded from ranking.
    """
    if not 2 <= len(codes) <= 5 or len(set(codes)) != len(codes):
        raise ValueError('Compare 2–5 distinct stocks')
    selected=point_in_time_indicators(indicators,as_of)
    selected=selected[selected.ts_code.isin(codes)].copy()
    periods=selected.set_index('ts_code')['end_date'].to_dict()
    common_period=None
    if len(periods)==len(codes) and len(set(periods.values()))==1:
        common_period=next(iter(periods.values())).date().isoformat()
    weights=metric_weights or {'roe':0.35,'gross_margin':0.15,'debt_to_assets':0.20,
                                 'or_yoy':0.15,'netprofit_yoy':0.15}
    if any(k not in F10_METRICS for k in weights) or any(float(v)<0 for v in weights.values()) or sum(weights.values())<=0:
        raise ValueError('Unsupported metric or invalid weights')
    score_allowed=common_period is not None and len(codes)>=3
    val=valuation.copy()
    required={'ts_code','trade_date','pe_ttm','pb'}
    if not val.empty and not required.issubset(val.columns):
        raise ValueError(f'Missing valuation fields: {sorted(required-set(val.columns))}')
    if not val.empty:
        val['trade_date']=pd.to_datetime(val['trade_date'])
        val=val[val.ts_code.isin(codes)&(val.trade_date<=pd.Timestamp(as_of))]
        val=val.sort_values('trade_date').drop_duplicates('ts_code',keep='last').set_index('ts_code')
    results=[]
    for code in codes:
        q=selected[selected.ts_code==code]
        row=q.iloc[0] if not q.empty else None
        metrics={}
        for field in weights:
            x=pd.to_numeric(row.get(field),errors='coerce') if row is not None else np.nan
            metrics[field]=float(x) if pd.notna(x) and np.isfinite(x) else None
        valuation_info={'pe_ttm':None,'pb':None,'date':None}
        if not val.empty and code in val.index:
            v=val.loc[code]
            if pd.notna(v.pe_ttm) and 0 < float(v.pe_ttm) < 1e5: valuation_info['pe_ttm']=float(v.pe_ttm)
            if pd.notna(v.pb) and float(v.pb)>0: valuation_info['pb']=float(v.pb)
            valuation_info['date']=v.trade_date.date().isoformat()
        results.append({'ts_code':code,'fiscal_period':row.end_date.date().isoformat() if row is not None else None,
                        'published_at':row.available_at.date().isoformat() if row is not None else None,
                        'metrics':metrics,'valuation':valuation_info,'peer_score':None})
    # Scores for exactly same reported period only; rank is cohort relative and missing values never imputed.
    if score_allowed:
        for field,weight in weights.items():
            values=[r['metrics'][field] for r in results]
            if any(v is None for v in values):
                score_allowed=False
                break
        if score_allowed:
            percentiles={}
            for field in weights:
                x=pd.Series([r['metrics'][field] for r in results])
                rank=x.rank(method='average',pct=True)
                if F10_METRICS[field]['direction']=='lower': rank=(len(x)+1-x.rank(method='average'))/len(x)
                percentiles[field]=rank.to_list()
            for i,r in enumerate(results):
                r['peer_score']=round(sum(weights[f]*percentiles[f][i] for f in weights)/sum(weights.values())*100,2)
    return {'as_of':as_of,'period_aligned':common_period is not None,'common_period':common_period,
            'cohort_size':len(codes),'score_available':score_allowed,'score_method':'weighted within-sample percentile (n>=3), no predictive meaning',
            'weights':weights,'companies':results,
            'warnings': ([] if score_allowed else ['缺少统一报告期、指标或足够同业样本：不计算综合得分；仅展示可得指标。']),
            'notes':['2–5股仅为小样本相对比较，不代表全行业分位','金融/非金融企业不可直接套用同一权重','必须核对单位、行业及财报披露时间']}


def announcement_watch(announcements:pd.DataFrame, as_of:str, codes:list[str]|None=None) -> list[dict]:
    """Keyword-based triage from provided title/link; not full-text judgement."""
    need={'announcement_date','ticker','announcement_title','url'}
    if not need.issubset(announcements.columns):raise ValueError(f'Missing: {sorted(need-set(announcements))}')
    patterns={'earnings':['业绩预告','年度报告','季度报告','盈利预测'],
              'shareholding':['减持','增持','股份回购','控股股东'],
              'debt':['债务','违约','融资','偿债'],
              'governance':['诉讼','处罚','立案','审计意见','关联交易','担保']}
    f=announcements.copy();f['date']=pd.to_datetime(f.announcement_date,errors='coerce')
    f=f[f.date.notna()&(f.date<=pd.Timestamp(as_of))]
    if codes is not None:f=f[f.ticker.isin(codes)]
    out=[]
    for _,r in f.iterrows():
        categories=[k for k,terms in patterns.items() if any(t in str(r.announcement_title) for t in terms)]
        if categories:
            out.append({'ticker':str(r.ticker),'date':r.date.date().isoformat(),'title':str(r.announcement_title),
                        'categories':categories,'source_url':str(r.url),'evidence_level':'title_only',
                        'note':'关键词命中仅为检索线索，不代表风险已证实'})
    return sorted(out,key=lambda r:r['date'],reverse=True)
