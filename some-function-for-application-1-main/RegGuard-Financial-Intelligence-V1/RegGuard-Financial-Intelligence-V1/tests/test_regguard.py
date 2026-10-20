from __future__ import annotations
import sqlite3
import pandas as pd
import pytest
from regguard.normalize import normalize_source
from regguard.governance import audit_opinion_review,pledge_risk_review,filing_event_triage,controller_legal_checklist
from regguard.regulation import regulatory_change_tracker,classify_regulatory_topics
from regguard.reporting import build_evidence_pack,consolidate_alerts,build_digest
from regguard.registry import REGISTRY,run_named_operation,export_tool_catalogue
from regguard.datasets import dataset_coverage
from regguard.workflow import init_case_store,open_case,review_case,case_history
from regguard.ml import peer_outlier_screen


def test_registry_and_catalogue():
    assert len(REGISTRY)>=15
    assert len(export_tool_catalogue())==len(REGISTRY)
    with pytest.raises(ValueError):run_named_operation('os.system', command='echo oops')
    d=dataset_coverage()
    assert d['dictionary_tables']==37 and d['dictionary_fields']==856
    assert all(x['available_in_dictionary'] for group in d['core_groups'].values() for x in group)


def test_announcements_metadata_mapping():
    inp=pd.DataFrame([{'ticker':'DEMO.SZ','announcement_date':'20260801',
                       'announcement_title':'关于会计差错更正的公告','url':'https://example.org/x'}])
    out=normalize_source(inp,'cd80_anns_d')
    found=filing_event_triage(out,'2026-10-13')
    assert found[0]['categories']==['accounting_restatement']
    assert found[0]['evidence_level']=='title_only'
    assert filing_event_triage(out,'2026-01-01')==[]
    with pytest.raises(ValueError): normalize_source(inp,'invented_source')


def test_audit_pit_and_auditor_change():
    data=pd.DataFrame([
        {'ts_code':'X','ann_date':'20250501','end_date':'20241231','audit_result':'标准无保留意见','audit_agency':'A'},
        {'ts_code':'X','ann_date':'20260501','end_date':'20251231','audit_result':'保留意见','audit_agency':'B'},
        {'ts_code':'X','ann_date':'20270501','end_date':'20261231','audit_result':'否定意见','audit_agency':'C'},
    ])
    out=audit_opinion_review(data,'2026-10-13')
    assert len(out)==2
    assert out[0]['opinion_type']=='unmodified'
    assert out[1]['opinion_type']=='qualified' and out[1]['auditor_changed_vs_previous_observation']
    assert out[1]['status']=='requires_review'


def test_pledge_pct_and_pp():
    d=pd.DataFrame([{'ts_code':'X','end_date':'20240101','pledge_ratio':26},
                    {'ts_code':'X','end_date':'20260101','pledge_ratio':55},
                    {'ts_code':'X','end_date':'20280101','pledge_ratio':99}])
    out=pledge_risk_review(d,'2026-10-13')
    assert len(out)==2
    assert out[1]['issuer_pledge_ratio_pct']==55
    assert out[1]['change_pp']==29 and out[1]['status']=='triggered'
    assert out[0]['status']=='not_triggered'
    assert pledge_risk_review(d,'2023-01-01')==[]
    with pytest.raises(ValueError):pledge_risk_review(d,'2026-10-13', ratio_threshold_pct=150)


def test_checklist_not_auto_court_guilt():
    items=controller_legal_checklist([{'ts_code':'X','subject_name':'虚构王某','role':'董事长'}],'2026-10-13')
    assert len(items)>=4
    assert all(i['match_status']=='not_checked' and i['review_status']=='pending_human_verification' for i in items)
    with pytest.raises(ValueError):controller_legal_checklist([{'ts_code':'X','role':'董事'}],'2026-10-13')


def test_regulatory_diff_missing_is_not_repeal():
    doc={'document_id':'REG-1','title':'关于信息披露的规定','published_at':'2026-01-01','effective_at':'2026-02-01',
         'authority':'虚构监管机关','source_url':'https://example.org/reg','text':'需披露事项A'}
    out=regulatory_change_tracker([],[doc],'2026-10-13')
    assert out[0]['change_type']=='new' and '信息披露' in out[0]['topics']
    out=regulatory_change_tracker([doc],[{**doc,'text':'需披露事项B'}],'2026-10-13')
    assert out[0]['change_type']=='amended'
    out=regulatory_change_tracker([doc],[],'2026-10-13')
    assert out[0]['change_type']=='missing_from_latest_snapshot'
    assert '信息披露' in classify_regulatory_topics('年度信息披露')


def test_evidence_pack_prevents_future_and_missing():
    ev=[{'published_at':'2026-03-01','source_url':'https://example.org/r','excerpt':'Example excerpt','page':3},
        {'published_at':'2027-03-01','source_url':'https://example.org/late','excerpt':'future'},
        {'published_at':'2026-01-01','source_url':'http://invalid.example','excerpt':'untrusted'}]
    pack=build_evidence_pack('Demo','What is the accounting concern?',ev,'2026-10-13')
    assert pack['evidence_count']==1 and pack['evidence'][0]['page']==3
    assert build_evidence_pack('Demo','Why is it concerning?',[],'2026-10-13')['status']=='insufficient_evidence'


def test_case_immutable_history_and_evidence_checks():
    c=sqlite3.connect(':memory:')
    init_case_store(c)
    open_case(c,'K1','X','R2','2026-04-01')
    with pytest.raises(ValueError):review_case(c,'K1','reviewer','escalated','found something')
    x=review_case(c,'K1','reviewer','in_review','waiting for original filing')
    y=review_case(c,'K1','reviewer','confirmed_indicator','document reviewed','investigation',
                  'https://example.org/document')
    h=case_history(c,'K1')
    assert len(h)==2 and h[1]['previous_digest']==h[0]['digest']
    assert h[1]['digest']==y['digest']


def test_digest_independent_signals_no_fake_probability():
    audit=[{'ts_code':'X','available_at':'2026-05-01','status':'requires_review','opinion_type':'qualified',
            'opinion_original':'保留意见','evidence_level':'structured_provider_field'}]
    alerts=consolidate_alerts(audit_reviews=audit,as_of='2026-10-13')
    report=build_digest(alerts,'2026-10-13')
    assert report['alert_count']==1 and 'fraud_probability' not in str(report)


def test_ml_refuses_small_groups():
    sklearn=pytest.importorskip('sklearn')
    x=[{'ts_code':str(i),'industry':'制造','report_period':'2025-12-31',
        'available_at':'2026-04-30','cfo_to_ni':1+i*.01,'accruals_to_assets':.01,
        'receivables_growth_gap':.02,'debt_to_assets':.3,'other_receivables_to_assets':.05} for i in range(15)]
    assert peer_outlier_screen(x,'2026-10-13')[0]['status']=='insufficient_comparable_peers'


def test_ml_outlier_is_not_probability():
    pytest.importorskip('sklearn')
    x=[{'ts_code':str(i),'industry':'制造','report_period':'2025-12-31','available_at':'2026-04-30',
        'cfo_to_ni':1+i*.02,'accruals_to_assets':.01+i*.001,
        'receivables_growth_gap':.02+i*.001,'debt_to_assets':.3+i*.002,
        'other_receivables_to_assets':.05+i*.0001} for i in range(35)]
    result=peer_outlier_screen(x,'2026-10-13')
    assert len(result)==35 and all(r['status']=='ok' for r in result)
    assert all('fraud_probability' not in r for r in result)


def test_disclosed_ownership_graph_never_auto_controller():
    from regguard.governance import disclosed_ownership_graph
    d=pd.DataFrame([{'ts_code':'DEMO.SZ','holder_name':'虚构机构A','hold_ratio':18.2,
                     'ann_date':'20260501','end_date':'20251231'},
                    {'ts_code':'DEMO.SZ','holder_name':'虚构机构B','hold_ratio':40.0,
                     'ann_date':'20280501','end_date':'20271231'}])
    network=disclosed_ownership_graph(d,'2026-10-13')
    assert len(network['edges'])==1 and not network['edges'][0]['human_verified_control']
    assert network['edges'][0]['relationship']=='disclosed_shareholder'
    link=[{'subject_name':'虚构控股人','ts_code':'DEMO.SZ','relationship':'documented_controller',
           'human_verified':True,'evidence_url':'https://example.org/filing','published_at':'2026-01-01','verified_by':'demo'}]
    augmented=disclosed_ownership_graph(d,'2026-10-13',link)
    assert len(augmented['edges'])==2
    assert augmented['edges'][-1]['human_verified_control']


def _financial_frames():
    b=[];i=[];c=[]
    for y in (2023,2024,2025):
        base={'ts_code':'DEMO001.SZ','end_date':f'{y}1231','ann_date':f'{y+1}0430','comp_type':'1','report_type':1}
        b.append({**base,'total_assets':100,'total_liab':70,'total_cur_assets':40,'total_cur_liab':65,
                  'accounts_receiv':10 if y<2025 else 30,'oth_receiv':15,'st_borr':10,'lt_borr':20,
                  'money_cap':20,'bond_payable':10,'undistr_porfit':8,'total_hldr_eqy_inc_min_int':30})
        i.append({**base,'revenue':100 if y<2025 else 115,'n_income':20,'ebit':15,'oper_cost':70,
                  'sell_exp':3,'admin_exp':4})
        c.append({**base,'n_cashflow_act':4,'depr_fa_coga_dpba':3})
    return pd.DataFrame(b),pd.DataFrame(i),pd.DataFrame(c)


def test_reused_red_flags_pit_and_missing():
    b,i,c=_financial_frames()
    out=run_named_operation('regguard.screen_financials',balance=b,income=i,cashflow=c,as_of='2026-10-13')
    flags={r['rule_id']:r for r in out[0]['rules']}
    assert flags['R1_cash_earnings_gap']['status']=='triggered'
    assert flags['R2_receivables_vs_sales']['status']=='triggered'
    assert flags['R3_high_cash_high_debt']['status']=='not_evaluable'
    assert out[0]['available_at']<='2026-10-13'
    older=run_named_operation('regguard.screen_financials',balance=b,income=i,cashflow=c,as_of='2025-03-31')
    assert older[0]['report_period']=='2023-12-31'


def test_reused_score_does_not_fabricate_missing_factors():
    b,i,c=_financial_frames()
    em=run_named_operation('regguard.altman_em_z',balance=b,income=i,as_of='2026-10-13')[0]
    assert em['status']=='ok'
    beneish=run_named_operation('regguard.beneish_m',balance=b,income=i,cashflow=c,as_of='2026-10-13')[0]
    assert beneish['score'] is None and beneish['status']=='insufficient_inputs'
    f=run_named_operation('regguard.piotroski_f',balance=b,income=i,cashflow=c,as_of='2026-10-13')[0]
    assert f['score'] is None and 'no_new_share_issuance' in f['missing_signals']


def test_tushare_probe_not_credential_leak():
    from alphapilot.competition_tushare import probe_permissions,fetch_authorized
    class Demo:
        def fina_audit(self,**kw):return pd.DataFrame([{'audit_result':'标准无保留意见'}])
        def pledge_stat(self,**kw):return pd.DataFrame()
        def fina_indicator(self,**kw):raise PermissionError('secret token forbidden')
    d=probe_permissions('DEMO001.SZ',client=Demo())
    assert d['pledge_stat']['status']=='empty_ambiguous'
    assert d['fina_indicator']['error_type']=='PermissionError'
    assert 'secret' not in str(d)
    with pytest.raises(ValueError):fetch_authorized('web_request',client=Demo(),ts_code='X')


def test_knowledge_search_curated_and_sourced():
    from regguard.knowledge import knowledge_search
    results=knowledge_search('审计意见和审计师变化')
    assert results and any('审计' in d['title'] for d in results)
    assert all(d['source_url'].startswith('https://') and 'live_update' in d['status'] for d in results)
