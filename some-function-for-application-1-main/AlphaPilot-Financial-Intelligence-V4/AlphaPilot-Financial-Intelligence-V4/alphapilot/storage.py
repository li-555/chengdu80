"""SQLite storage and upsert. All externally sourced data must keep provenance."""
from __future__ import annotations
import sqlite3
from pathlib import Path
import pandas as pd


def connect(path: str = 'alphapilot.sqlite') -> sqlite3.Connection:
    con=sqlite3.connect(path)
    con.execute('PRAGMA foreign_keys = ON')
    con.executescript((Path(__file__).parent/'schema.sql').read_text(encoding='utf-8'))
    return con


def save_prices(con: sqlite3.Connection, ts_code: str, prices: pd.DataFrame, name: str|None = None) -> int:
    required=['trade_date','open','high','low','close','vol','adj_factor']
    for field in required:
        if field not in prices.columns:
            raise ValueError(f'Missing: {field}')
    con.execute('INSERT INTO assets(ts_code,name) VALUES (?,?) ON CONFLICT(ts_code) DO UPDATE SET name=COALESCE(excluded.name, assets.name)',(ts_code,name))
    payload=[]
    for row in prices[required].itertuples(index=False,name=None):
        date,*nums=row
        dt=pd.to_datetime(date).strftime('%Y-%m-%d')
        payload.append((ts_code,dt,*[float(n) for n in nums]))
    with con:
        con.executemany('''INSERT INTO daily_bars
            (ts_code,trade_date,open,high,low,close,vol,adj_factor)
            VALUES (?,?,?,?,?,?,?,?)
            ON CONFLICT(ts_code,trade_date) DO UPDATE SET
                open=excluded.open,high=excluded.high,low=excluded.low,
                close=excluded.close,vol=excluded.vol,adj_factor=excluded.adj_factor,
                fetched_at=CURRENT_TIMESTAMP''',payload)
    return len(payload)


def load_prices(con: sqlite3.Connection, ts_code: str, end_date: str|None = None) -> pd.DataFrame:
    sql='SELECT ts_code,trade_date,open,high,low,close,vol,adj_factor FROM daily_bars WHERE ts_code=?'
    args=[ts_code]
    if end_date is not None:
        sql+=' AND trade_date<=?'
        args.append(end_date)
    sql+=' ORDER BY trade_date'
    return pd.read_sql_query(sql,con,params=args)


def save_valuations(con, ts_code: str, frame: pd.DataFrame):
    if frame.empty:
        return 0
    rows=[]
    for _,r in frame.iterrows():
        def f(v): return float(v) if pd.notna(v) else None
        rows.append((ts_code,pd.to_datetime(r.trade_date).strftime('%Y-%m-%d'),f(r.get('pe_ttm')),f(r.get('pb')),f(r.get('turnover_rate'))))
    with con:
        con.executemany('''INSERT INTO daily_valuations(ts_code,trade_date,pe_ttm,pb,turnover_rate)
            VALUES(?,?,?,?,?) ON CONFLICT(ts_code,trade_date) DO UPDATE SET
            pe_ttm=excluded.pe_ttm,pb=excluded.pb,turnover_rate=excluded.turnover_rate,fetched_at=CURRENT_TIMESTAMP''', rows)
    return len(rows)
