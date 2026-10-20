import json
import numpy as np
import pandas as pd
import pytest
from alphapilot.dataset_catalog import table_catalog,describe_table,validate_source_columns
from alphapilot.fundamentals import point_in_time_indicators,f10_cards,compare_fundamentals,announcement_watch
from alphapilot.advanced_fundamentals import cash_earnings_quality,top_holder_concentration
from alphapilot.macro_research import macro_release
from alphapilot.portfolio import portfolio_risk
from alphapilot.knowledge import connect_knowledge,seed_methods,knowledge_search,ingest_official_rss
from alphapilot.application_runtime import execute_app,validate_app,tools_for_ai
from alphapilot.backtest import sma_rule_backtest
from alphapilot.industry import industry_membership


def fake_bars(code='000001.SZ',seed=1,n=140):
    rng=np.random.default_rng(seed)
    close=100*np.cumprod(1+rng.normal(.001,.01,n))
    o=close*.998;h=close*1.02;l=close*.98
    return pd.DataFrame({'ts_code':code,'trade_date':pd.bdate_range('2025-01-01',periods=n),
                         'open':o,'high':h,'low':l,'close':close,'vol':10000,'adj_factor':1.0})


def fin():
    return pd.DataFrame([
        {'ts_code':'AAA','end_date':'2025-03-31','ann_date':'2025-04-30','roe':4,'gross_margin':24,'debt_to_assets':60,'or_yoy':10,'netprofit_yoy':11},
        {'ts_code':'AAA','end_date':'2025-06-30','ann_date':'2025-08-31','roe':7,'gross_margin':25,'debt_to_assets':58,'or_yoy':12,'netprofit_yoy':13},
        {'ts_code':'AAA','end_date':'2025-06-30','ann_date':'2025-11-30','roe':99,'gross_margin':99,'debt_to_assets':20,'or_yoy':99,'netprofit_yoy':99},
        {'ts_code':'BBB','end_date':'2025-06-30','ann_date':'2025-08-31','roe':8,'gross_margin':30,'debt_to_assets':50,'or_yoy':14,'netprofit_yoy':15},
        {'ts_code':'CCC','end_date':'2025-06-30','ann_date':'2025-08-31','roe':6,'gross_margin':26,'debt_to_assets':55,'or_yoy':13,'netprofit_yoy':14},
    ])

def test_catalog_from_exact_workbook():
    c=table_catalog();assert c['table_count']==37 and c['field_count']==856
    assert len(describe_table('cd80_stock_fin_indicator')['fields'])==110
    assert 'ann_date' in {x['field'] for x in describe_table('cd80_stock_fin_income')['fields']}
    assert 'n_cashflow_act' in {x['field'] for x in describe_table('cd80_stock_fin_cashflow')['fields']}
    assert validate_source_columns('cd80_daily',['close','open'])['recognized']==['close','open']

def test_financial_publication_prevents_future_data_leakage():
    c=f10_cards(fin(),'2025-09-01')
    a=next(x for x in c if x['ts_code']=='AAA')
    assert a['metrics']['roe']['value']==7
    c2=f10_cards(fin(),'2025-05-15')
    assert next(x for x in c2 if x['ts_code']=='AAA')['metrics']['roe']['value']==4
    assert not any(x['ts_code']=='BBB' for x in c2)

def test_financial_revision_f_ann_date_is_not_early():
    f=pd.DataFrame([{'ts_code':'A','ann_date':'2025-05-01','f_ann_date':'2025-07-01',
                     'end_date':'2025-03-31','roe':88}])
    assert point_in_time_indicators(f,'2025-06-01').empty

def test_peer_scoring_only_aligned_with_three_items():
    valuation=pd.DataFrame([{'ts_code':c,'trade_date':'2025-09-01','pe_ttm':10+i,'pb':1.2} for i,c in enumerate(['AAA','BBB','CCC'])])
    r=compare_fundamentals(fin(),valuation,'2025-09-01',['AAA','BBB','CCC'])
    assert r['score_available'] and len(r['companies'])==3
    r2=compare_fundamentals(fin(),valuation,'2025-05-01',['AAA','BBB','CCC'])
    assert not r2['score_available']


def test_macro_missing_consensus_fails_closed():
    m=macro_release('CES0000000001',actual=160000,prior=159700)
    assert m['surprise_to_consensus'] is None and len(m['warnings'])==2


def test_local_knowledge_citations_and_allowlist(tmp_path):
    con=connect_knowledge(tmp_path/'kb.sqlite')
    assert seed_methods(con)>=7
    hits=knowledge_search(con,'ROE')
    assert hits and all(h['url'].startswith('https://') for h in hits)
    with pytest.raises(ValueError):ingest_official_rss(con,'cnn_news')


def test_declarative_runtime_rejects_unknown_op_and_unbound_data():
    invalid={'steps':[{'id':'step1','operation':'python.exec','arguments':{}}]}
    assert validate_app(invalid,[]) and validate_app(invalid,[])[0]['code']=='NOT_ALLOWED'
    good={'steps':[{'id':'p','operation':'finance.macro_release','arguments':{'series_id':'LPR','actual':3.5,'prior':3.45}}]}
    assert execute_app(good,{})['p']['change_from_prior']==pytest.approx(.05)
    broken={'steps':[{'id':'p','operation':'finance.performance','arguments':{'bars':{'$ref':'private_bars'}}}]}
    assert validate_app(broken,[]) and 'UNBOUND_REF' in [e['code'] for e in validate_app(broken,[])]
    assert len(tools_for_ai())>=17


def test_announcement_title_only_and_industry_at_time():
    a=pd.DataFrame([{'announcement_date':'2025-05-01','ticker':'AAA','announcement_title':'股东减持计划','url':'https://example.com/a'},
                    {'announcement_date':'2025-07-01','ticker':'AAA','announcement_title':'股东减持完成','url':'https://example.com/b'}])
    events=announcement_watch(a,'2025-06-01',['AAA'])
    assert len(events)==1 and events[0]['evidence_level']=='title_only'
    ind=pd.DataFrame([{'ts_code':'AAA','in_date':'2025-01-01','out_date':'2025-06-01','l1_name':'电子'},
                      {'ts_code':'BBB','in_date':'2025-07-01','out_date':None,'l1_name':'电子'}])
    assert [x['ts_code'] for x in industry_membership(ind,'2025-05-01')]==['AAA']


def test_cashflow_alignment_and_concentration():
    income=pd.DataFrame([{'ts_code':'AAA','ann_date':'2025-04-30','end_date':'2025-03-31','n_income_attr_p':100},
                         {'ts_code':'AAA','ann_date':'2025-11-01','end_date':'2025-06-30','n_income_attr_p':200}])
    cf=pd.DataFrame([{'ts_code':'AAA','ann_date':'2025-04-30','end_date':'2025-03-31','n_cashflow_act':40},
                     {'ts_code':'AAA','ann_date':'2025-07-01','end_date':'2025-06-30','n_cashflow_act':70}])
    q=cash_earnings_quality(income,cf,'2025-08-01')
    assert len(q)==1 and q[0]['ocf_to_net_income']==pytest.approx(.4)
    h=pd.DataFrame([{'ts_code':'AAA','ann_date':'2025-05-01','end_date':'2025-03-31',
                     'holder_name':'A','hold_ratio':22.0},
                    {'ts_code':'AAA','ann_date':'2025-05-01','end_date':'2025-03-31',
                     'holder_name':'B','hold_ratio':15.0}])
    assert top_holder_concentration(h,'2025-06-01')[0]['total_top10_percent']==pytest.approx(37)


def test_portfolio_and_no_lookahead_sma():
    bars={'AAA':fake_bars('AAA',1),'BBB':fake_bars('BBB',2)}
    r=portfolio_risk(bars)
    assert r['weight_hhi']==pytest.approx(.5)
    b=sma_rule_backtest(bars['AAA'],transaction_cost_bps=0)
    assert isinstance(b['strategy_return'],float)
    with pytest.raises(ValueError):portfolio_risk(bars,weights={'AAA':.6,'BBB':.6})


def test_industry_breadth_percent_not_fraction():
    from alphapilot.industry_breadth import industry_daily_breadth
    daily=pd.DataFrame([{'ts_code':'AAA','trade_date':'2025-05-01','pct_chg':2.0,'amount':100},
                        {'ts_code':'BBB','trade_date':'2025-05-01','pct_chg':-1.0,'amount':200}])
    members=pd.DataFrame([{'ts_code':c,'l1_name':'半导体','in_date':'2025-01-01','out_date':None} for c in ['AAA','BBB']])
    out=industry_daily_breadth(daily,members,'2025-05-01')
    assert out[0]['breadth_positive_pct']==50
    assert out[0]['equal_weight_mean_return_pct']==pytest.approx(.5)


def test_news_adapter_query_validation_no_network():
    from alphapilot.news_adapter import gdelt_headlines
    with pytest.raises(ValueError):gdelt_headlines('a')
    with pytest.raises(ValueError):gdelt_headlines('CPI',timespan='allhistory')


def test_sec_api_has_strict_user_agent_and_cik():
    from alphapilot.sec_data_adapter import sec_companyfacts
    with pytest.raises(ValueError):sec_companyfacts('oops',user_agent='research contact@example.com')
    with pytest.raises(RuntimeError):sec_companyfacts('1234567890',user_agent='none')


def test_isolation_forest_out_of_sample():
    from alphapilot.ml_anomaly import detect_market_anomalies
    pytest.importorskip('sklearn')
    bars=fake_bars('AAA',5,200)
    result=detect_market_anomalies(bars)
    assert result['train_end']<result['test_start']
    assert result['model']=='IsolationForest'
    assert len(result['holdout'])>=20
