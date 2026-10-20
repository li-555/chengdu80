"""Fetch authorised Tushare data and persist. Example: python fetch_real.py 000001.SZ 20250101 20261010"""
import argparse
from alphapilot.tushare_adapter import fetch_equity
from alphapilot.storage import connect, save_prices, save_valuations, load_prices
from alphapilot.analytics import performance, observation_signals

if __name__ == '__main__':
    p=argparse.ArgumentParser()
    p.add_argument('ts_code')
    p.add_argument('start')
    p.add_argument('end')
    p.add_argument('--no-valuation',action='store_true')
    args=p.parse_args()
    bars,val=fetch_equity(args.ts_code,args.start,args.end,include_valuation=not args.no_valuation)
    with connect('alphapilot.sqlite') as db:
        save_prices(db,args.ts_code,bars)
        if val is not None:
            save_valuations(db,args.ts_code,val)
        stock=load_prices(db,args.ts_code)
    print('EOD as of',stock.trade_date.iloc[-1])
    print(performance(stock))
    print(observation_signals(stock))
