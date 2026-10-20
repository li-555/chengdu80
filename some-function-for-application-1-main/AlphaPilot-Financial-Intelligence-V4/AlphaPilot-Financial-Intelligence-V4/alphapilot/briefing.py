"""Deterministic evidence bundle for LLM, keeping factual numbers separate from narrative."""
from __future__ import annotations
import pandas as pd
from .analytics import performance,observation_signals


def daily_briefing(bars_by_code:dict,as_of:str,document_events:list[dict]|None=None,
                   max_events:int=15)->dict:
    items=[]
    for code,bars in bars_by_code.items():
        price=bars.copy()
        price['trade_date']=pd.to_datetime(price.trade_date)
        price=price[price.trade_date<=pd.Timestamp(as_of)]
        if len(price)<61:continue
        p=performance(price)
        signal=observation_signals(price)
        items.append({'ts_code':code,'latest_trade_date':p['end'],'period_return':p['period_return'],
                      'annual_volatility':p['annual_volatility'], 'max_drawdown':p['max_drawdown'],
                      'observation_signals':signal})
    events=[e for e in (document_events or []) if e.get('date','')<=as_of][:max_events]
    return {'research_asof':as_of,'market_data_frequency':'EOD','watchlist':items,
            'source_events':events,'claims_policy':{
                'numbers':'Only reference values in this payload; cite source identifiers',
                'evidence':'Headline classifications are not full-document findings',
                'causality':'Event-price correlation is not proof of causation',
                'disallowed':'No fabricated realtime quotes, forecast consensus, buy/sell certainty'},
            'status':'evidence_ready','summary':'Use a configured authorised LLM endpoint to produce prose from this bundle.'}
