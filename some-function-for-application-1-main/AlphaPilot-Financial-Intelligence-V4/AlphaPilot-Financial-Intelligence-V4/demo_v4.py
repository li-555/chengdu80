"""Entirely synthetic data; no genuine price/security data or provider keys."""
from __future__ import annotations
import json
import pandas as pd
from alphapilot.research_rules import screen_accounting_red_flags, compare_peer_scores


def fake_rows():
    bal=[]; income=[]; cash=[]
    for yr in [2023,2024,2025]:
        base=dict(ts_code='DEMO001',end_date=f'{yr}1231',ann_date=f'{yr+1}0430',comp_type='1',report_type=1)
        bal.append({**base,'total_assets':100,'total_cur_assets':30,'total_cur_liab':55,
                    'accounts_receiv':10 if yr < 2025 else 24,'oth_receiv':12,
                    'money_cap':30,'st_borr':10,'lt_borr':20,'bond_payable':2})
        income.append({**base,'revenue':100 if yr < 2025 else 110,'n_income':20})
        cash.append({**base,'n_cashflow_act':4})
    return map(pd.DataFrame,[bal,income,cash])

if __name__=='__main__':
    b,i,c=fake_rows()
    result=screen_accounting_red_flags(b,i,c,'2026-10-13')
    print('ALL DATA BELOW ARE INVENTED / 以下所有财务数据均为虚构演示：')
    print(json.dumps(result,ensure_ascii=False,indent=2))
    peers=[{'ts_code':f'DEMO{k:02d}','industry':'虚构行业','report_period':'2025-12-31',
            'available_at':'2026-04-30','score':k/10,'status':'ok'} for k in range(8)]
    print('\nFictitious peers:')
    print(json.dumps(compare_peer_scores(peers,'2026-10-13'),ensure_ascii=False,indent=2))
