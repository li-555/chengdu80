"""All values synthetic. Tests the contracts, not regulatory truth or model performance."""
import pandas as pd
import pytest

from alphapilot.application_runtime import execute_app, tools_for_ai, validate_app
from alphapilot.research_rules import screen_accounting_red_flags, compare_peer_scores


def statements():
    b, i, c = [], [], []
    for yr in (2022, 2023, 2024, 2025):
        base = {"ts_code":"000001.SZ", "end_date":f"{yr}1231", "ann_date":f"{yr+1}0430",
                "comp_type":"1", "report_type":1}
        b.append({**base,"total_assets":100.0,"total_liab":80.0,
                  "total_cur_assets":50.0,"total_cur_liab":75.0,
                  "accounts_receiv": 10.0 if yr < 2025 else 24.0,
                  "oth_receiv":12.0, "money_cap":18.0,
                  "st_borr":10.0,"lt_borr":20.0,"bond_payable":5.0})
        i.append({**base,"revenue":100.0 if yr < 2025 else 110.0,"n_income":20.0})
        c.append({**base,"n_cashflow_act":3.0})
    return pd.DataFrame(b),pd.DataFrame(i),pd.DataFrame(c)


def test_qwen_rulebook_r1_r2_r4_r7_r11_honest_states():
    b,i,c=statements()
    result=screen_accounting_red_flags(b,i,c,'2026-10-13')[0]
    flags={x['rule_id']:x for x in result['rules']}
    assert {'R1_cash_earnings_gap','R2_receivables_vs_sales','R4_other_receivables_concentration',
            'R7_low_current_ratio','R11_joint_receivables_pattern'} <= {
               n for n,f in flags.items() if f['status']=='triggered'}
    assert flags['R3_high_cash_high_debt']['status']=='not_evaluable'
    assert result['trigger_count']==5
    assert all('fraud_probability' not in f for f in result['rules'])
    assert all(f['rule_version'] for f in result['rules'])


def test_pit_blocks_future_financials():
    b,i,c=statements()
    result=screen_accounting_red_flags(b,i,c,'2025-03-31')[0]
    assert result['report_period']=='2023-12-31'
    flags={x['rule_id']:x for x in result['rules']}
    assert flags['R2_receivables_vs_sales']['status']=='not_triggered'


def test_r1_requires_consecutive_positive_profit_and_known_cashflow():
    b,i,c=statements(); c.loc[c.end_date=='20251231','n_cashflow_act']=None
    result=screen_accounting_red_flags(b,i,c,'2026-10-13')[0]
    f={r['rule_id']:r for r in result['rules']}
    assert f['R1_cash_earnings_gap']['status']=='not_evaluable'
    assert result['trigger_count']>=1


def test_financial_firms_not_assumed_nonfinancial():
    b,i,c=statements();b['comp_type']='2'
    assert screen_accounting_red_flags(b,i,c,'2026-10-13')[0]['status']=='unsupported_financial_company'


def test_peer_rank_8_rule_and_time_comparability():
    recs=[{'ts_code':str(k),'industry':'制造业','report_period':'2025-12-31',
           'available_at':'2026-04-30','score':k,'status':'ok'} for k in range(8)]
    ranked=compare_peer_scores(recs,'2026-10-13')
    assert len(ranked)==8
    assert next(x for x in ranked if x['ts_code']=='7')['sample_percentile']==1.0
    assert compare_peer_scores(recs[:7],'2026-10-13')[0]['status']=='insufficient_peers'
    assert compare_peer_scores(recs,'2026-03-31')==[]  # all reports still unpublished
    recs.append({'ts_code':'another','industry':'金融业','report_period':'2024-12-31','available_at':'2025-04-30','score':0,'status':'ok'})
    assert len([x for x in compare_peer_scores(recs,'2026-10-13') if x['status']=='ok'])==8


def test_peer_duplicate_and_malformed_params_fail():
    x={'ts_code':'x','industry':'ind','report_period':'2025','available_at':'2026-04-01','score':1,'status':'ok'}
    with pytest.raises(ValueError):compare_peer_scores([x,x],'2026-10-13')
    with pytest.raises(ValueError):compare_peer_scores([x],'2026-10-13',min_peers=2)
    with pytest.raises(ValueError):screen_accounting_red_flags(*statements(),'2026-10-13',consecutive_years=1)


def test_ai_registry_validation_executes_new_screen():
    b,i,c=statements()
    tools={t['name'] for t in tools_for_ai()}
    assert {'regguard.screen_accounting_v2','finance.compare_peer_scores'} <= tools
    app={'steps':[{'id':'flags','operation':'regguard.screen_accounting_v2',
                   'arguments':{'balance':{'$ref':'b'},'income':{'$ref':'i'},
                                'cashflow':{'$ref':'c'},'as_of':'2026-10-13'}}]}
    assert validate_app(app,['b','i','c'])==[]
    result=execute_app(app,{'b':b,'i':i,'c':c})
    assert result['flags'][0]['trigger_count']==5


def test_auditor_change_uses_title_only_not_audit_opinion():
    from alphapilot.financial_forensics import audit_filing_triage
    docs=pd.DataFrame([{'announcement_date':'20260501','ticker':'DEMO001',
                        'announcement_title':'关于变更会计师事务所的公告',
                        'url':'https://example.org/notice.pdf'}])
    result=audit_filing_triage(docs,'2026-05-02')
    assert result[0]['categories']==['auditor_change']
    assert result[0]['evidence_level']=='title_only'
