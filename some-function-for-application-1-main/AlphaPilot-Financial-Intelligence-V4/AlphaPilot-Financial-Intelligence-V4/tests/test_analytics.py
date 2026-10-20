import numpy as np
import pandas as pd
import pytest
from alphapilot.analytics import prepare_prices, indicators, performance, observation_signals, compare_stocks, valuation_snapshot, price_threshold_signals
from alphapilot.operations import run_named_operation
from alphapilot.storage import connect, save_prices, load_prices


def sample(code='000001.SZ',n=100):
    x=np.linspace(10, 20, n)
    return pd.DataFrame({'ts_code':[code]*n,'trade_date':pd.bdate_range('2025-01-02',periods=n),
        'open':x,'high':x*1.01,'low':x*.99,'close':x,
        'vol':[1000]*n,'adj_factor':[1.0]*n})

def test_indicator_shapes_and_no_lookahead():
    df=indicators(sample())
    assert len(df)==100
    assert df.ma20.iloc[:19].isna().all()
    assert df.ma20.iloc[19]==pytest.approx(sample().close.iloc[:20].mean())
    assert df.volume_ratio_20.iloc[:20].isna().all()
    assert df.volume_ratio_20.iloc[20]==pytest.approx(1)
    assert df.rsi14.iloc[-1]==pytest.approx(100)

def test_adjustment_factor_applied():
    s=sample(n=21)
    s.loc[:10,'adj_factor']=.5
    p=prepare_prices(s)
    assert p.close_adj.iloc[0]==pytest.approx(s.close.iloc[0]*.5)

def test_price_validation_and_duplicates():
    x=sample()
    x.loc[0,'high']=1
    with pytest.raises(ValueError,match='OHLC'):
        prepare_prices(x)
    x=sample()
    x.loc[0,'trade_date']=x.loc[1,'trade_date']
    with pytest.raises(ValueError,match='Duplicate'):
        prepare_prices(x)

def test_perf_and_same_range_compare():
    x=sample()
    p=performance(x)
    assert p['period_return']==pytest.approx(1.0)
    assert p['max_drawdown']==pytest.approx(0)
    y=sample('600000.SH')
    y.close*=1.5
    y.open*=1.5
    y.high*=1.5
    y.low*=1.5
    res=compare_stocks({'a':x,'b':y})
    assert res.period_return.tolist()==pytest.approx([1.0,1.0])

def test_signals_trigger_volume_spike():
    x=sample()
    x.loc[len(x)-1,'vol']=5000
    events=observation_signals(x)
    assert 'volume_spike' in {e['signal'] for e in events}
    assert all(e['latency']=='EOD' for e in events)

def test_db_upsert_and_load(tmp_path):
    con=connect(str(tmp_path/'test.sqlite'))
    with con:
        save_prices(con,'000001.SZ',sample())
        save_prices(con,'000001.SZ',sample())
        r=load_prices(con,'000001.SZ')
        assert len(r)==100
        assert r.iloc[0].trade_date=='2025-01-02'
        assert len(load_prices(con,'000001.SZ',end_date='2025-01-03'))==2
    con.close()

def test_registry_disallows_unknown_operations():
    with pytest.raises(ValueError,match='Unsupported'):
        run_named_operation('python.exec', code='print(1)')
    assert 'max_drawdown' in run_named_operation('finance.performance',bars=sample())

def test_valuation_missing():
    data=pd.DataFrame({'trade_date':['2025-01-01'],'pe_ttm':[np.nan],'pb':[1.2]})
    v=valuation_snapshot(data)
    assert v['pe_ttm'] is None and v['pb']==pytest.approx(1.2)


def test_price_threshold_cross_uses_raw_close_and_completed_bar():
    x=sample(n=70)
    level=float((x.close.iloc[-2]+x.close.iloc[-1])/2)
    events=price_threshold_signals(x,above=level)
    assert len(events)==1 and events[0]['signal']=='close_crossed_above_price'
    assert price_threshold_signals(x,above=1e9)==[]
