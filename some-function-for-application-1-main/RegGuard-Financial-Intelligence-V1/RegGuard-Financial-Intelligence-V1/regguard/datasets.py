"""Dataset coverage source of truth: contest table metadata, NOT raw holdings."""
import json
from pathlib import Path

REGGUARD_TABLES={
 'company_reference':['cd80_stock_basic','cd80_stock_basic_calendar'],
 'financial_statements':['cd80_stock_fin_income','cd80_stock_fin_balancesheet','cd80_stock_fin_cashflow','cd80_stock_fin_indicator'],
 'ownership_governance':['cd80_stock_refer_holders_top10','cd80_stock_basic_managers','cd80_stock_refer_pledge_stat'],
 'disclosures':['cd80_anns_d'],
 'trading_events':['cd80_margin_data','cd80_lhb_summary','cd80_limit_surge','cd80_limit_down'],
}
ADDITIONAL_APIS={
 'fina_audit':'审计意见/事务所; 比赛Token实际权限待测',
 'pledge_stat':'更近股权质押统计; 核心旧表2015-2017不能代表现状',
 'pledge_detail':'质押主体和交易明细',
 'disclosure_date':'预约披露日期; 需核实API字段',
 'stk_holdertrade':'股东增减持; 需核实API字段',
 'top10_holders':'补充股东信息; 需核实API权限',
}

def dataset_coverage(catalog_path:str|None=None)->dict:
    path=Path(catalog_path) if catalog_path else Path(__file__).resolve().parents[1]/'catalog'/'competition_tables.json'
    meta=json.loads(path.read_text(encoding='utf-8'))
    table_map=meta.get('tables',{})
    groups={}
    for category,tables in REGGUARD_TABLES.items():
        groups[category]=[{'table':name,'available_in_dictionary':name in table_map,
                           'coverage':table_map.get(name,{}).get('time_range'),
                           'fields':[r.get('field') for r in table_map.get(name,{}).get('fields',[])]}
                          for name in tables]
    return {'dictionary_tables':meta.get('table_count'),'dictionary_fields':meta.get('field_count'),
            'core_groups':groups,'extra_tushare_apis':ADDITIONAL_APIS,
            'limitation':'目录是字段元信息；不证明本地已有数据行、token 权限或实时更新。'}
