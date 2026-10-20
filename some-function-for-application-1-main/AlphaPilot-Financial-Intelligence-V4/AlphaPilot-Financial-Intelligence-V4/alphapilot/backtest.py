"""Transparent EOD SMA research backtest with one-bar lag, not a trading recommendation."""
from __future__ import annotations
import pandas as pd
import numpy as np
from .analytics import prepare_prices


def sma_rule_backtest(bars:pd.DataFrame,fast:int=20,slow:int=60,transaction_cost_bps:float=10.0)->dict:
    if not 2<=fast<slow<=250:raise ValueError('Require 2<=fast<slow<=250')
    if not 0<=transaction_cost_bps<=1000:raise ValueError('Cost out of range')
    x=prepare_prices(bars)
    if len(x)<slow+22:raise ValueError('Not enough prices for warmup and evaluation')
    close=x.close_adj
    fast_ma=close.rolling(fast,min_periods=fast).mean()
    slow_ma=close.rolling(slow,min_periods=slow).mean()
    raw=(fast_ma>slow_ma).astype(int)
    raw[slow_ma.isna()]=0
    pos=raw.shift(1).fillna(0) # Today's position only from yesterday's completed close
    ret=close.pct_change(fill_method=None).fillna(0)
    trading_cost=pos.diff().abs().fillna(pos.abs())*transaction_cost_bps/10000
    strategy=pos*ret-trading_cost
    start=slow
    s=strategy.iloc[start:];b=ret.iloc[start:]
    equity=(1+s).cumprod()
    benchmark=(1+b).cumprod()
    return {'start':x.trade_date.iloc[start].date().isoformat(),
            'end':x.trade_date.iloc[-1].date().isoformat(),
            'strategy_return':float(equity.iloc[-1]-1),
            'buy_hold_return':float(benchmark.iloc[-1]-1),
            'strategy_max_drawdown':float((equity/equity.cummax()-1).min()),
            'turnover_events':int((pos.diff().abs().iloc[start:]>0).sum()),
            'fast':fast,'slow':slow,'cost_bps_per_position_change':transaction_cost_bps,
            'method':'A股日终信号翌日持有、close-to-close模拟；不建模涨跌停、停牌、实际成交和滑点；不用于承诺收益',
            'overfit_warning':'此函数是策略研究工具；需额外进行样本外、滚动回测和多重检验'}
