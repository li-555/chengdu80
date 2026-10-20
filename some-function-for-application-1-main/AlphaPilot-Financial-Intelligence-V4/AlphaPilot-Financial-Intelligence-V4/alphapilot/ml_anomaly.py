"""Optional unsupervised anomaly research. Scores are not fraud probabilities or trade signals."""
from __future__ import annotations
import pandas as pd
import numpy as np
from .analytics import indicators


def detect_market_anomalies(bars:pd.DataFrame,holdout_ratio:float=0.20,contamination:float=0.05)->dict:
    try:
        from sklearn.ensemble import IsolationForest
        from sklearn.preprocessing import StandardScaler
        from sklearn.pipeline import make_pipeline
    except ImportError as exc: raise RuntimeError('Install optional: pip install scikit-learn') from exc
    if not (0.1<=holdout_ratio<=0.4) or not (0.001<=contamination<=0.25):raise ValueError('Invalid parameters')
    f=indicators(bars)
    use=['daily_return','annual_volatility_20','volume_ratio_20']
    f=f[['trade_date']+use].replace([np.inf,-np.inf],np.nan).dropna().copy()
    if len(f)<140:raise ValueError('Need 140 or more complete dated observations')
    split=int(len(f)*(1-holdout_ratio))
    train,test=f.iloc[:split],f.iloc[split:].copy()
    model=make_pipeline(StandardScaler(),IsolationForest(n_estimators=200,contamination=contamination,random_state=42))
    model.fit(train[use]);test['anomaly_score']=-model.decision_function(test[use]);test['anomalous']=model.predict(test[use])==-1
    return {'train_end':train.trade_date.iloc[-1].date().isoformat(),
            'test_start':test.trade_date.iloc[0].date().isoformat(),
            'features':use,'model':'IsolationForest','contamination_assumption':contamination,
            'holdout':test.assign(trade_date=test.trade_date.dt.strftime('%Y-%m-%d')).to_dict('records'),
            'disclaimer':'异常程度不是亏损概率；结果需经样本外和事件层面的人工验证'}
