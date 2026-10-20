"""Cross-asset watchlist risk based on aligned adjusted end-of-day closing prices."""
from __future__ import annotations
import math
import pandas as pd
import numpy as np
from .analytics import prepare_prices


def portfolio_risk(bars_by_code:dict[str,pd.DataFrame],weights:dict[str,float]|None=None,
                   risk_free_annual:float=0.0)->dict:
    if len(bars_by_code)<2:raise ValueError('At least 2 assets needed')
    codes=list(bars_by_code)
    w=weights or {c:1.0/len(codes) for c in codes}
    if set(w)!=set(codes) or any(not np.isfinite(float(x)) or float(x)<0 for x in w.values()) or abs(sum(w.values())-1)>1e-6:
        raise ValueError('Weights must cover all assets, be nonnegative, and sum to 1')
    px=pd.concat({c:prepare_prices(df).set_index('trade_date').close_adj for c,df in bars_by_code.items()},axis=1).dropna()
    if len(px)<61:raise ValueError('Need >=61 common trading dates')
    ret=px.pct_change(fill_method=None).dropna()
    weights_array=np.array([w[c] for c in codes])
    daily=(ret*weights_array).sum(axis=1) # daily rebalanced portfolio approximation
    annual_vol=float(daily.std(ddof=1)*math.sqrt(252))
    annual_ret=float(daily.mean()*252)
    nav=(1+daily).cumprod()
    cov=ret.cov()*252
    return {'start':px.index[0].date().isoformat(),'end':px.index[-1].date().isoformat(),
            'observations':len(ret),'weights':w, 'weight_hhi':float(np.sum(weights_array**2)),
            'annual_volatility':annual_vol,'annualized_mean_return':annual_ret,
            'max_drawdown':float((nav/nav.cummax()-1).min()),
            'sharpe':(annual_ret-risk_free_annual)/annual_vol if annual_vol>0 else None,
            'correlations':{c:{d:float(ret[c].corr(ret[d])) for d in codes} for c in codes},
            'annual_covariance':cov.to_dict(),
            'assumptions':['日频、每日再平衡的模型组合','未计交易费用、税费、现金与滑点','仅用共同交易日期','历史风险不保证未来表现']}
