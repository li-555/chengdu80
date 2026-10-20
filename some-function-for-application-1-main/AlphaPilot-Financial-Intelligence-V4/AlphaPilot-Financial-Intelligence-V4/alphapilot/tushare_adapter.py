"""Optional adapter to an existing Tushare Pro account. Never store API tokens in documents."""
from __future__ import annotations
import os
import pandas as pd


def fetch_equity(ts_code: str, start: str, end: str, include_valuation: bool = True):
    try:
        import tushare as ts
    except ImportError as exc:
        raise RuntimeError('pip install tushare') from exc
    token=os.environ.get('TUSHARE_TOKEN')
    if not token:
        raise RuntimeError('Set TUSHARE_TOKEN environment variable; never put it in an app JSON')
    pro=ts.pro_api(token)
    daily=pro.daily(ts_code=ts_code, start_date=start, end_date=end,
                    fields='ts_code,trade_date,open,high,low,close,vol')
    factors=pro.adj_factor(ts_code=ts_code,start_date=start,end_date=end)
    if daily is None or daily.empty or factors is None or factors.empty:
        raise RuntimeError('Tushare returned empty prices or factors; check date and entitlement')
    prices=daily.merge(factors[['trade_date','adj_factor']], on='trade_date', how='left', validate='one_to_one')
    if prices.adj_factor.isna().any():
        raise ValueError('Missing factor on a price date; refusing to calculate misleading returns')
    prices=prices.sort_values('trade_date').reset_index(drop=True)
    valuation=None
    if include_valuation:
        try:
            valuation=pro.daily_basic(ts_code=ts_code,start_date=start,end_date=end,
                                fields='ts_code,trade_date,pe_ttm,pb,turnover_rate')
        except Exception:
            # Missing entitlement is normal, but must be visible to the caller.
            raise RuntimeError('Could not fetch daily_basic: verify your Tushare points/rights or run with --no-valuation')
    return prices, valuation
