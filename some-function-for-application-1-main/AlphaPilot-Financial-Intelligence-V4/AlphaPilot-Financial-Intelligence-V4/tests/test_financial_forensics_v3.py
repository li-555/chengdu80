"""Synthetic test cases only. Do NOT interpret as actual listed-company results."""
import pandas as pd
import pytest
from alphapilot.financial_forensics import (altman_em_score,piotroski_f_score,
                                              accrual_quality,regguard_red_flags,audit_filing_triage)
from alphapilot.competition_tushare import fetch_authorized,probe_permissions
from alphapilot.application_runtime import tools_for_ai, validate_app, execute_app


def make_statements():
    balance=[];income=[];cash=[]
    years=[2023,2024,2025]
    for idx,year in enumerate(years):
        base={'ts_code':'000001.SZ','end_date':f'{year}1231','ann_date':f'{year+1}0430', 'comp_type':'1','report_type':1}
        balance.append({**base,'total_assets':100+20*idx,'total_liab':60+5*idx,
            'total_cur_assets':50+10*idx,'total_cur_liab':30+2*idx,
            'total_hldr_eqy_inc_min_int':40+15*idx,'undistr_porfit':10+8*idx,
            'lt_borr':20-5*idx,'accounts_receiv':15+3*idx})
        income.append({**base,'revenue':100+30*idx,'oper_cost':75+20*idx,
                       'n_income':10+5*idx,'ebit':15+5*idx})
        cash.append({**base,'n_cashflow_act':12+8*idx})
    return pd.DataFrame(balance),pd.DataFrame(income),pd.DataFrame(cash)


def test_em_z_correct_terms():
    b,i,_=make_statements()
    r=altman_em_score(b,i,'2026-10-13')[0]
    assert r['status']=='ok'
    assert r['score']==pytest.approx(3.25+6.56*((70-34)/140)+3.26*(26/140)+6.72*(25/140)+1.05*(70/70))
    assert 'risk_level' not in r


def test_no_future_reports_used():
    b,i,c=make_statements()
    old=altman_em_score(b,i,'2025-03-31')[0]
    assert old['report_period']=='2023-12-31'  # 2024 report published 2025-04-30
    assert accrual_quality(b,i,c,'2025-03-31')==[]


def test_em_z_rejects_banks():
    b,i,_=make_statements();b['comp_type']='2'
    r=altman_em_score(b,i,'2026-10-13')[0]
    assert r['score'] is None
    assert r['status']=='unsupported_financial_company'


def test_missing_inputs_are_not_zero():
    b,i,c=make_statements();b['undistr_porfit']=float('nan')
    r=altman_em_score(b,i,'2026-10-13')[0]
    assert r['score'] is None and r['status']=='insufficient_inputs'


def test_piotro_issuance_signal_unknown_without_evidence():
    b,i,c=make_statements()
    s=piotroski_f_score(b,i,c,'2026-10-13')[0]
    assert s['score'] is None
    assert 'no_new_share_issuance' in s['missing_signals']
    s2=piotroski_f_score(b,i,c,'2026-10-13',issuance_flags={'000001.SZ':False})[0]
    assert s2['status']=='complete' and 0<=s2['score']<=9


def test_accrual_not_fraud_probability():
    b,i,c=make_statements();r=accrual_quality(b,i,c,'2026-10-13')[-1]
    assert r['accruals_to_average_assets']==pytest.approx((20-28)/130)
    assert 'fraud_probability' not in r


def test_rule_evidence_no_fraud_label():
    b,i,c=make_statements()
    c.loc[c.end_date=='20251231','n_cashflow_act']=2
    r=regguard_red_flags(b,i,c,'2026-10-13')[0]
    assert 'R1_cash_earnings_gap' in [x['rule_id'] for x in r['review_flags']]
    assert all(x['review_status']=='unreviewed' for x in r['review_flags'])


def test_rule_thresholds_bounded():
    b,i,c=make_statements()
    with pytest.raises(ValueError):regguard_red_flags(b,i,c,'2026-10-13',current_ratio_threshold=1e12)


def test_filing_title_no_original_body_assumptions():
    f=pd.DataFrame([{'announcement_date':'20260401','ticker':'000001.SZ',
                     'announcement_title':'关于会计差错更正的公告','url':'https://example.org/file.pdf'}])
    result=audit_filing_triage(f,'2026-04-02')
    assert 'restatement' in result[0]['categories']
    assert result[0]['evidence_level']=='title_only'
    assert audit_filing_triage(f,'2026-03-31')==[]


def test_allowlist_and_probe_mock():
    class Client:
        def fina_audit(self,**kw):return pd.DataFrame([{'audit_result':'标准无保留意见'}])
        def pledge_stat(self,**kw):return pd.DataFrame()
        def fina_indicator(self,**kw):raise PermissionError('not allowed')
    mock=Client()
    assert probe_permissions('000001.SZ',client=mock)['pledge_stat']['status']=='empty_ambiguous'
    assert probe_permissions('000001.SZ',client=mock)['fina_indicator']['status']=='error_check_entitlement_or_network'
    with pytest.raises(ValueError):fetch_authorized('arbitrary_api',client=mock,ts_code='000001.SZ')
    with pytest.raises(ValueError):fetch_authorized('fina_audit',client=mock,ts_code='000001.SZ',evil='x')


def test_ai_exposes_and_runs_new_op():
    b,i,_=make_statements()
    tools={x['name'] for x in tools_for_ai()}
    assert {'finance.altman_em_z','regguard.red_flag_rules'}<=tools
    doc={'steps':[{'id':'z','operation':'finance.altman_em_z',
                   'arguments':{'balance':{'$ref':'bal'},'income':{'$ref':'inc'},'as_of':'2026-10-13'}}]}
    assert validate_app(doc,['bal','inc'])==[]
    result=execute_app(doc,{'bal':b,'inc':i})
    assert result['z'][0]['score']>0


def test_beneish_with_exact_required_fields_only():
    from alphapilot.financial_forensics import beneish_m_score
    b,i,c=make_statements()
    b['fix_assets']=[20,22,24]
    b['bond_payable']=[1,1,1]
    i['sell_exp']=[3,4,5];i['admin_exp']=[4,5,6]
    c['depr_fa_coga_dpba']=[3,4,5]
    r=beneish_m_score(b,i,c,'2026-10-13')[0]
    assert r['status']=='ok'
    assert len(r['contributions'])==8
    assert sum(r['contributions'].values())-4.84==pytest.approx(r['score'])
    assert 'fraud_probability' not in r


def test_beneish_refuses_missing_depreciation():
    from alphapilot.financial_forensics import beneish_m_score
    b,i,c=make_statements();b['fix_assets']=10;b['bond_payable']=1
    i['sell_exp']=3;i['admin_exp']=4
    result=beneish_m_score(b,i,c,'2026-10-13')[0]
    assert result['status']=='insufficient_inputs'
    assert result['score'] is None
