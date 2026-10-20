"""Unsupervised cross-sectional outlier ranks, not fraud probabilities."""
from __future__ import annotations
import numpy as np
import pandas as pd

DEFAULT_FEATURES=('cfo_to_ni','accruals_to_assets','receivables_growth_gap',
                  'debt_to_assets','other_receivables_to_assets')

def peer_outlier_screen(records:list[dict],as_of:str,features:list[str]|None=None,
                        min_peers:int=30,contamination:float=0.05)->list[dict]:
    if min_peers<20 or min_peers>10000:raise ValueError('min_peers must be 20..10000')
    if not 0<contamination<=0.25:raise ValueError('contamination must be (0,0.25]')
    features=features or list(DEFAULT_FEATURES)
    if not features or len(features)>20 or len(features)!=len(set(features)) or any(not x.isidentifier() for x in features):
        raise ValueError('invalid features')
    try:
        from sklearn.ensemble import IsolationForest
        from sklearn.preprocessing import RobustScaler
    except ImportError as e:
        raise RuntimeError('Install requirements-optional.txt for unsupervised inference') from e
    df=pd.DataFrame(records)
    required={'ts_code','industry','report_period','available_at'} | set(features)
    if not required.issubset(df.columns):raise ValueError(f'missing features {sorted(required-set(df))}')
    if df.duplicated(['ts_code','report_period','industry']).any():
        raise ValueError('duplicate company/period/industry')
    df['available_at']=pd.to_datetime(df.available_at,errors='coerce')
    cutoff=pd.Timestamp(as_of)
    df=df[df.available_at.notna() & (df.available_at<=cutoff) & df.industry.notna() & df.report_period.notna()].copy()
    for field in features:df[field]=pd.to_numeric(df[field],errors='coerce')
    df=df.replace([np.inf,-np.inf],np.nan)
    out=[]
    for (industry,period),g in df.groupby(['industry','report_period'],sort=True):
        valid=g.dropna(subset=features).copy()
        if len(valid)<min_peers:
            out.append({'industry':str(industry),'report_period':str(period),
                        'status':'insufficient_comparable_peers','peer_count':len(valid),'minimum':min_peers})
            continue
        X=valid[features].to_numpy(dtype=float)
        scaled=RobustScaler().fit_transform(X)
        forest=IsolationForest(n_estimators=150,random_state=42,contamination=contamination)
        forest.fit(scaled)
        raw=-forest.decision_function(scaled)
        med=np.median(X,axis=0)
        mad=np.median(abs(X-med),axis=0)
        mad=np.where(mad<1e-9,np.nan,mad)
        for j,(_,r) in enumerate(valid.iterrows()):
            contrib={f:round(float(abs(X[j,k]-med[k])/mad[k]),5) for k,f in enumerate(features) if np.isfinite(mad[k])}
            top=sorted(contrib.items(),key=lambda kv:kv[1],reverse=True)[:3]
            out.append({'ts_code':str(r.ts_code),'industry':str(industry),
                        'report_period':str(period),'available_at':r.available_at.date().isoformat(),
                        'outlier_score':round(float(raw[j]),6),
                        'sample_percentile':round(float((raw<=raw[j]).mean()),6),
                        'top_deviation_features':[{'feature':k,'robust_deviation':v} for k,v in top],
                        'peer_count':len(valid),'status':'ok','model':'IsolationForest_RobustScaler_v1',
                        'caution':'样本内异常程度，不是舞弊概率、违约概率；贡献字段为相对中位数偏离，并非精确模型归因。'})
    return out
