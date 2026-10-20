"""Auditable, end-of-day research indicators for Tushare-shaped OHLCV data.

Input: trade_date, open, high, low, close, vol, adj_factor.
No investment recommendation or automatic order placement.
"""
from __future__ import annotations
import math
import numpy as np
import pandas as pd

REQUIRED = {'trade_date', 'open', 'high', 'low', 'close', 'vol', 'adj_factor'}


def prepare_prices(bars: pd.DataFrame) -> pd.DataFrame:
    """Prepare as-of-end-date forward-adjusted OHLC prices; filter one stock per call.

    Tushare qfq-style normalization: raw_price * adj_factor / latest_adj_factor.
    We retain adjusted prices and unadjusted input OHLC for audit. Historical
    backtests require point-in-time recalculation and cannot reuse future factors.
    """
    missing = REQUIRED - set(bars.columns)
    if missing:
        raise ValueError(f'Missing columns: {sorted(missing)}')
    if 'ts_code' in bars and bars.ts_code.nunique(dropna=False) != 1:
        raise ValueError('prepare_prices expects exactly one ts_code')
    df = bars.copy()
    df['trade_date'] = pd.to_datetime(df['trade_date'], format='mixed', errors='raise')
    df = df.sort_values('trade_date')
    if df.trade_date.duplicated().any():
        raise ValueError('Duplicate trade_date in stock data')
    for col in ['open', 'high', 'low', 'close', 'vol', 'adj_factor']:
        df[col] = pd.to_numeric(df[col], errors='raise')
    if df[['open','high','low','close','adj_factor']].isna().any().any():
        raise ValueError('Prices and adjustment factors must be complete')
    if (df[['open','high','low','close','adj_factor']] <= 0).any().any() or (df['vol'] < 0).any():
        raise ValueError('Invalid OHLC/adjustment factor/volume')
    if (df.high < df[['open', 'close', 'low']].max(axis=1)).any() or (df.low > df[['open', 'close','high']].min(axis=1)).any():
        raise ValueError('OHLC inconsistent (high/low bounds)')
    anchor = df.adj_factor.iloc[-1]
    for c in ['open', 'high', 'low', 'close']:
        df[c + '_adj'] = df[c] * df.adj_factor / anchor
    return df.reset_index(drop=True)


def _rsi(close: pd.Series, n: int = 14) -> pd.Series:
    """RSI with Wilder initial n-day SMA followed by Wilder recursive average."""
    diff = close.diff()
    gain = diff.clip(lower=0).to_numpy(dtype=float)
    loss = (-diff.clip(upper=0)).to_numpy(dtype=float)
    result = np.full(len(close), np.nan)
    if len(close) <= n:
        return pd.Series(result, index=close.index)
    ag = float(np.mean(gain[1:n+1]))
    al = float(np.mean(loss[1:n+1]))
    for i in range(n, len(close)):
        if i > n:
            ag = (ag*(n-1) + gain[i])/n
            al = (al*(n-1) + loss[i])/n
        if al == 0 and ag == 0:
            result[i] = 50.0
        elif al == 0:
            result[i] = 100.0
        else:
            result[i] = 100.0 - (100.0 / (1.0 + ag/al))
    return pd.Series(result, index=close.index)


def indicators(bars: pd.DataFrame) -> pd.DataFrame:
    """Compute trend, momentum, risk and volume without same-bar lookahead."""
    df = prepare_prices(bars)
    close = df['close_adj']
    df['daily_return'] = close.pct_change(fill_method=None)
    df['ma20'] = close.rolling(20, min_periods=20).mean()
    df['ma60'] = close.rolling(60, min_periods=60).mean()
    df['rsi14'] = _rsi(close, 14)
    ema12 = close.ewm(span=12, adjust=False).mean()
    ema26 = close.ewm(span=26, adjust=False).mean()
    df['macd_diff'] = ema12 - ema26
    df['macd_signal'] = df.macd_diff.ewm(span=9, adjust=False).mean()
    df['macd_hist'] = df.macd_diff - df.macd_signal
    prev = close.shift(1)
    tr = pd.concat([
        df.high_adj - df.low_adj,
        (df.high_adj - prev).abs(),
        (df.low_adj - prev).abs(),
    ], axis=1).max(axis=1)
    df['atr14'] = tr.ewm(alpha=1/14, adjust=False, min_periods=14).mean()
    df['annual_volatility_20'] = df.daily_return.rolling(20, min_periods=20).std(ddof=1) * math.sqrt(252)
    df['drawdown'] = close / close.cummax() - 1
    df['volume_ratio_20'] = df.vol / df.vol.shift(1).rolling(20, min_periods=20).mean().replace(0, np.nan)
    return df


def performance(bars: pd.DataFrame, risk_free_annual: float = 0.0) -> dict:
    """Sample performance summary. Annualization assumes 252 trading days."""
    df = indicators(bars)
    ret = df.daily_return.dropna()
    if len(ret) < 20:
        raise ValueError('At least 21 daily closing prices are required')
    annual_vol = float(ret.std(ddof=1)*math.sqrt(252))
    annual_excess = float(ret.mean()*252 - risk_free_annual)
    return {
        'start': df.trade_date.iloc[0].date().isoformat(),
        'end': df.trade_date.iloc[-1].date().isoformat(),
        'observations': len(df),
        'period_return': float(df.close_adj.iloc[-1]/df.close_adj.iloc[0] - 1),
        'annual_volatility': annual_vol,
        'max_drawdown': float(df.drawdown.min()),
        'sharpe_annualized': (annual_excess/annual_vol if annual_vol > 0 else None),
        'risk_free_rate_assumption': risk_free_annual,
        'data_frequency': 'EOD',
        'annualization_days': 252,
    }


def observation_signals(bars: pd.DataFrame, volume_multiplier: float = 2.0) -> list[dict]:
    """Emit transparent EOD watch signals, not buy/sell recommendations."""
    df = indicators(bars)
    if len(df) < 61:
        raise ValueError('Need 61 trading sessions for MA20/MA60 signals')
    prev, now = df.iloc[-2], df.iloc[-1]
    events = []
    dt = now.trade_date.date().isoformat()
    def add(kind: str, detail: str, value: float):
        events.append({'signal':kind, 'date':dt, 'value':float(value), 'detail':detail, 'latency':'EOD', 'investment_advice':False})
    # Only signal when the actual crossover happened between two completed sessions.
    if pd.notna(prev.ma20) and pd.notna(prev.ma60):
        if prev.ma20 <= prev.ma60 and now.ma20 > now.ma60:
            add('ma20_cross_above_ma60', '20日均线上穿60日均线（收盘后确认）', now.ma20-now.ma60)
        if prev.ma20 >= prev.ma60 and now.ma20 < now.ma60:
            add('ma20_cross_below_ma60', '20日均线下穿60日均线（收盘后确认）', now.ma20-now.ma60)
    if pd.notna(now.volume_ratio_20) and now.volume_ratio_20 >= volume_multiplier:
        add('volume_spike', '成交量大于此前20日均量的设定倍数', now.volume_ratio_20)
    if pd.notna(now.rsi14) and now.rsi14 > 70:
        add('rsi_over_70', 'RSI14 > 70（仅代表动量状态）', now.rsi14)
    elif pd.notna(now.rsi14) and now.rsi14 < 30:
        add('rsi_under_30', 'RSI14 < 30（仅代表动量状态）', now.rsi14)
    return events


def compare_stocks(bars_by_code: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Compare same-window total returns, volatility and drawdown; no ranking by invented score."""
    if len(bars_by_code) < 2:
        raise ValueError('Supply at least two stocks')
    each = {code:prepare_prices(bars).set_index('trade_date').close_adj for code,bars in bars_by_code.items()}
    aligned = pd.concat(each, axis=1, join='inner').dropna()
    if len(aligned)<21:
        raise ValueError('Insufficient overlapping close dates')
    rows=[]
    for code in aligned.columns:
        s=aligned[code]
        r=s.pct_change(fill_method=None).dropna()
        rows.append({
            'ts_code': code,
            'start':s.index[0].date().isoformat(),
            'end':s.index[-1].date().isoformat(),
            'period_return':float(s.iloc[-1]/s.iloc[0]-1),
            'annual_volatility':float(r.std(ddof=1)*math.sqrt(252)),
            'max_drawdown':float((s/s.cummax()-1).min()),
        })
    return pd.DataFrame(rows).sort_values('ts_code').reset_index(drop=True)


def valuation_snapshot(daily_basic: pd.DataFrame) -> dict:
    """Vendor-supplied PE_TTM / PB, avoid recalc without financial-period data."""
    required={'trade_date','pe_ttm','pb'}
    if not required.issubset(daily_basic.columns):
        raise ValueError(f'Missing daily_basic: {sorted(required-set(daily_basic.columns))}')
    db=daily_basic.sort_values('trade_date').iloc[-1]
    def as_optional(v):
        return float(v) if pd.notna(v) and np.isfinite(float(v)) else None
    return {'as_of':str(db.trade_date), 'pe_ttm':as_optional(db.pe_ttm), 'pb':as_optional(db.pb), 'source':'Tushare daily_basic', 'notes':'Negative PE is not comparable to positive profitable peers; align date and industry.'}


def price_threshold_signals(bars: pd.DataFrame, *, above: float | None = None,
                            below: float | None = None) -> list[dict]:
    """Observe EOD crosses of literal, unadjusted price levels; no intraday claims.

    Crossing is close-to-close; it does not imply executable entry/exit price.
    """
    df = prepare_prices(bars)
    if len(df) < 2:
        raise ValueError('Need at least two sessions')
    last, now = df.iloc[-2], df.iloc[-1]
    events=[]
    dt=now.trade_date.date().isoformat()
    if above is not None:
        if above <= 0:
            raise ValueError('above price threshold must be positive')
        if last.close <= above < now.close:
            events.append({'signal':'close_crossed_above_price', 'date':dt, 'price':float(now.close), 'threshold':float(above), 'latency':'EOD', 'investment_advice':False})
    if below is not None:
        if below <= 0:
            raise ValueError('below price threshold must be positive')
        if last.close >= below > now.close:
            events.append({'signal':'close_crossed_below_price', 'date':dt, 'price':float(now.close), 'threshold':float(below), 'latency':'EOD', 'investment_advice':False})
    return events
