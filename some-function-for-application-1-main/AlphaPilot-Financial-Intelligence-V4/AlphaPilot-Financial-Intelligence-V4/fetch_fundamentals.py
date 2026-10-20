"""Operator-run: pull permitted Tushare F10 and valuation rows. Does not embed credentials.

Usage: TUSHARE_TOKEN=... python fetch_fundamentals.py 000001.SZ 20240101 20261001
"""
from __future__ import annotations
import os,sys
from pathlib import Path

def fetch(code:str,start:str,end:str,outdir:str='data/downloaded'):
    try:import tushare as ts
    except ImportError as exc:raise SystemExit('pip install tushare') from exc
    token=os.environ.get('TUSHARE_TOKEN')
    if not token:raise SystemExit('Environment variable TUSHARE_TOKEN missing')
    if not code.endswith(('.SZ','.SH','.BJ')):raise SystemExit('Invalid Tushare code suffix')
    pro=ts.pro_api(token)
    results={}
    for endpoint,params in [
        ('fina_indicator',dict(ts_code=code,start_date=start,end_date=end)),
        ('daily_basic',dict(ts_code=code,start_date=start,end_date=end,
                            fields='ts_code,trade_date,pe_ttm,pb,ps_ttm,total_mv,turnover_rate')),
        ('income',dict(ts_code=code,start_date=start,end_date=end)),
        ('cashflow',dict(ts_code=code,start_date=start,end_date=end)),
    ]:
        try:
            df=getattr(pro,endpoint)(**params)
            if df is None or df.empty:
                print(f'{endpoint}: empty response; check coverage/permissions')
                continue
            p=Path(outdir);p.mkdir(parents=True,exist_ok=True)
            f=p/f'{endpoint}_{code}_{start}_{end}.csv'
            df.to_csv(f,index=False,encoding='utf-8-sig')
            results[endpoint]=(len(df),str(f))
        except Exception as exc:
            # Do not leak credentials or API headers into logs.
            print(f'{endpoint}: failed ({type(exc).__name__}); verify permissions/endpoint')
    return results

if __name__=='__main__':
    if len(sys.argv)!=4:raise SystemExit('Usage: python fetch_fundamentals.py CODE YYYYMMDD YYYYMMDD')
    print(fetch(*sys.argv[1:]))
