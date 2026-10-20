"""Reproducible synthetic demo: no API, no investment signals or real-market claims."""
import json
import numpy as np
import pandas as pd
from alphapilot.storage import connect, save_prices, load_prices
from alphapilot.analytics import performance, observation_signals, compare_stocks


def sample(code: str, seed: int):
    rng=np.random.default_rng(seed)
    dates=pd.bdate_range('2025-01-02', periods=180)  # DEMO: not a Chinese exchange holiday calendar
    rets=np.clip(rng.normal(0.0005,0.012,len(dates)), -.08,.08)
    prices=100*np.cumprod(1+rets)
    high=prices*1.012
    low=prices*.988
    return pd.DataFrame({'ts_code':code,'trade_date':dates,
      'open':prices, 'high':high, 'low':low, 'close':prices,
      'vol':rng.integers(10000,50000,len(dates)), 'adj_factor':np.ones(len(dates))})

if __name__=='__main__':
    with connect('alphapilot_demo.sqlite') as db:
        a=sample('000001.SZ',2026)
        b=sample('600000.SH',2027)
        save_prices(db,'000001.SZ',a,'DEMO A')
        save_prices(db,'600000.SH',b,'DEMO B')
        a=load_prices(db,'000001.SZ')
        b=load_prices(db,'600000.SH')
        print('SYNTHETIC DATA, NOT A REAL MARKET RESULT')
        print(json.dumps({'performance':performance(a),'watch_signals':observation_signals(a)},indent=2,ensure_ascii=False))
        print(compare_stocks({'000001.SZ':a,'600000.SH':b}).to_string(index=False))
