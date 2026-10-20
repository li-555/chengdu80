"""Completely offline, synthetic demonstrator. NOT real market prices or investment advice."""
import json
import tempfile
from datetime import date
import numpy as np,pandas as pd
from alphapilot.fundamentals import f10_cards,compare_fundamentals
from alphapilot.portfolio import portfolio_risk
from alphapilot.knowledge import connect_knowledge,seed_methods,knowledge_search
from alphapilot.application_runtime import execute_app,tools_for_ai

def fake_bars(code,drift):
    rng=np.random.default_rng(abs(sum(ord(c) for c in code)))
    dates=pd.bdate_range('2025-07-01',periods=170)
    close=100*np.cumprod(1+drift+rng.normal(0,0.011,len(dates)))
    open_=close*(1+rng.normal(0,.003,len(close)))
    high=np.maximum(open_,close)*1.01;low=np.minimum(open_,close)*.99
    return pd.DataFrame({'ts_code':code,'trade_date':dates,'open':open_,'high':high,'low':low,
                         'close':close,'vol':rng.integers(5000,10000,len(close)),'adj_factor':1.0})

if __name__=='__main__':
    codes=['000001.SZ','600000.SH','000002.SZ']
    f10=pd.DataFrame([{'ts_code':c,'end_date':'2025-09-30','ann_date':'2025-10-30',
                       'roe':7+i*2,'gross_margin':24+i*4,'debt_to_assets':55-i*3,
                       'or_yoy':10+i*5,'netprofit_yoy':4+i*3}
                      for i,c in enumerate(codes)])
    val=pd.DataFrame([{'ts_code':c,'trade_date':'2025-11-05','pe_ttm':15+i*3,'pb':1.2+i*.4}
                      for i,c in enumerate(codes)])
    bars={c:fake_bars(c,i*.0001) for i,c in enumerate(codes)}
    app={'version':'prototype-0.2','steps':[
        {'id':'cards','operation':'finance.f10_cards','arguments':{'indicators':{'$ref':'f10_data'},'as_of':'2025-11-05'}},
        {'id':'peers','operation':'finance.compare_fundamentals','arguments':{
            'indicators':{'$ref':'f10_data'},'valuation':{'$ref':'valuation_data'},'as_of':'2025-11-05','codes':codes}},
        {'id':'risk','operation':'finance.portfolio_risk','arguments':{'bars_by_code':{'$ref':'historical_bars'}}},
    ]}
    result=execute_app(app,{'f10_data':f10,'valuation_data':val,'historical_bars':bars})
    with tempfile.TemporaryDirectory() as folder:
        db=connect_knowledge(folder+'/knowledge.sqlite');seed_methods(db)
        evidence=knowledge_search(db,'ROE')
    print('SYNTHETIC DEMONSTRATION; NO REAL MARKET DATA OR LIVE APIS')
    print(json.dumps({'tool_count':len(tools_for_ai()),'f10_card_count':len(result['cards']),
                      'fundamental_comparison':result['peers'],'portfolio_risk':{
                        k:result['risk'][k] for k in ['annual_volatility','max_drawdown','weight_hhi']},
                      'knowledge_matches':evidence},ensure_ascii=False,indent=2,default=str))
