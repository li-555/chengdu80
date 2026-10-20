"""Opt-in integration with maintained financial libraries; core engine runs without extras."""
from __future__ import annotations
import pandas as pd
from .analytics import prepare_prices


def technical_indicators_external(bars:pd.DataFrame)->pd.DataFrame:
    """Native pandas-ta-classic RSI, MACD, Bollinger Bands (no auto trading)."""
    try: import pandas_ta_classic as ta
    except ImportError as exc:raise RuntimeError('pip install pandas-ta-classic') from exc
    df=prepare_prices(bars)
    close=df.close_adj.astype(float)
    rsi=ta.rsi(close,length=14,talib=False)
    macd=ta.macd(close,fast=12,slow=26,signal=9,talib=False)
    bbands=ta.bbands(close,length=20,std=2,talib=False)
    out=df[['trade_date','ts_code','close_adj']].copy() if 'ts_code' in df else df[['trade_date','close_adj']].copy()
    out['rsi_14']=rsi
    for prefix,source in [('macd_',macd),('bbands_',bbands)]:
        if source is not None:
            for col in source.columns: out[prefix+col]=source[col]
    return out


def performance_quantstats(bars:pd.DataFrame,risk_free_annual:float=0.0)->dict:
    """Compare mature library implementation. Not a substitute for documented assumptions."""
    try:import quantstats as qs
    except ImportError as exc:raise RuntimeError('pip install quantstats') from exc
    df=prepare_prices(bars)
    s=df.set_index('trade_date').close_adj.pct_change(fill_method=None).dropna()
    if len(s)<21:raise ValueError('Need >=21 daily observations')
    return {'sharpe':float(qs.stats.sharpe(s,rf=risk_free_annual,periods=252)),
            'max_drawdown':float(qs.stats.max_drawdown(s)),
            'volatility':float(qs.stats.volatility(s,periods=252)),
            'method':'quantstats','return_frequency':'daily','risk_free_annual':risk_free_annual}
