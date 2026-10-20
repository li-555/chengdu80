"""Authorized contest Tushare access: explicit allowlist and credential isolation.

IMPORTANT: returned empty datasets do not prove lack of entitlement.
M2 app documents should contain only data requirements; never token strings.
"""
from __future__ import annotations
import os
from typing import Any

# Explicitly documented endpoints; no model-generated arbitrary api_name.
API_REGISTRY={
    'fina_audit': {'params':{'ts_code','start_date','end_date','period'},'description':'审计结果及会计师事务所'},
    'pledge_stat': {'params':{'ts_code','end_date'},'description':'股权质押数量/比例'},
    'pledge_detail': {'params':{'ts_code','start_date','end_date','ann_date'},'description':'股权质押明细'},
    'income': {'params':{'ts_code','start_date','end_date','period','report_type'},'description':'利润表'},
    'balancesheet': {'params':{'ts_code','start_date','end_date','period','report_type'},'description':'资产负债表'},
    'cashflow': {'params':{'ts_code','start_date','end_date','period','report_type'},'description':'现金流量表'},
    'fina_indicator': {'params':{'ts_code','start_date','end_date','period'},'description':'财务指标'},
}


def authorized_client():
    token=os.environ.get('TUSHARE_TOKEN')
    if not token:raise RuntimeError('Set TUSHARE_TOKEN privately in environment')
    try:import tushare as ts
    except ImportError as exc:raise RuntimeError('pip install tushare') from exc
    return ts.pro_api(token)


def fetch_authorized(api_name: str, *, client=None, **params):
    if api_name not in API_REGISTRY:raise ValueError(f'Unapproved data endpoint: {api_name}')
    invalid=set(params)-API_REGISTRY[api_name]['params']
    if invalid:raise ValueError(f'Unknown {api_name} arguments: {sorted(invalid)}')
    if api_name!='pledge_stat' and not params.get('ts_code'):
        raise ValueError('Require explicit ts_code; no broad unbounded table pulls')
    if client is None:client=authorized_client()
    # Test mock and real Tushare Pro both support the standard endpoint calls.
    frame = getattr(client,api_name)(**params)
    if frame is None:raise RuntimeError(f'{api_name} returned no data object')
    return frame


def probe_permissions(ts_code: str, *, client=None) -> dict[str,dict]:
    """One bounded diagnostic request per API; distinguishes error from empty results.
    Treat empty response as ambiguous, not 'authorized' or 'denied'.
    """
    if client is None:client=authorized_client()
    checks = [('fina_audit',{'ts_code':ts_code,'start_date':'20240101','end_date':'20261231'}),
              ('pledge_stat',{'ts_code':ts_code}),
              ('fina_indicator',{'ts_code':ts_code,'start_date':'20250101','end_date':'20251231'})]
    results={}
    for api,args in checks:
        try:
            df=fetch_authorized(api,client=client,**args)
            results[api]={'status':'returned_rows' if not df.empty else 'empty_ambiguous',
                          'rows':int(len(df))}
        except Exception as exc:
            # Never write possible sensitive provider response/token into application logs.
            results[api]={'status':'error_check_entitlement_or_network',
                          'error_type':type(exc).__name__}
    return results
