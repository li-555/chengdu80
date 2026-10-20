"""Explicit provider field binding; no fuzzy guessing of financial data semantics."""
import pandas as pd

MAPPINGS={
 'cd80_anns_d':{'announcement_date':'ann_date','ticker':'ts_code','announcement_title':'title'},
 'tushare.fina_audit':{},
 'tushare.pledge_stat':{},
 'cd80_stock_refer_pledge_stat':{},
}
REQUIRED={
 'cd80_anns_d':{'ts_code','ann_date','title','url'},
 'tushare.fina_audit':{'ts_code','ann_date','audit_result'},
 'tushare.pledge_stat':{'ts_code','end_date','pledge_ratio'},
 'cd80_stock_refer_pledge_stat':{'ts_code','end_date','pledge_ratio'},
}

def normalize_source(frame:pd.DataFrame,source_name:str)->pd.DataFrame:
    if source_name not in MAPPINGS:raise ValueError('source mapping not approved; register fields explicitly')
    df=frame.rename(columns=MAPPINGS[source_name]).copy()
    missing=REQUIRED[source_name]-set(df.columns)
    if missing:raise ValueError(f'{source_name} missing required {sorted(missing)}')
    if df['ts_code'].isna().any():raise ValueError('missing security code')
    df['source']=source_name
    return df
