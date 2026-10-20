"""Document-grounded corporate-governance and audit triage.

No automatic identity matches, judicial accusations or legal conclusions.
All rows are supplied by the authorised platform data catalogue.
"""
from __future__ import annotations

from collections import defaultdict
from urllib.parse import urlparse
import pandas as pd


def _date(s):
    v = pd.to_datetime(s, errors='coerce')
    return None if pd.isna(v) else v.date().isoformat()


def _url(s):
    s = str(s or '').strip()
    p = urlparse(s)
    return s if p.scheme == 'https' and p.hostname else None


def audit_opinion_review(audits: pd.DataFrame, as_of: str) -> list[dict]:
    """Audit reports from Tushare `fina_audit`; evidence is structured field, not extracted PDFs.
    Supported classes are keyword heuristics requiring reviewer confirmation.
    """
    required = {'ts_code', 'ann_date', 'audit_result'}
    missing = required-set(audits.columns)
    if missing: raise ValueError(f'audit_opinion_review missing {sorted(missing)}')
    cutoff = pd.Timestamp(as_of)
    df=audits.copy()
    df['ann_date']=pd.to_datetime(df.ann_date.astype(str),errors='coerce')
    df=df[df.ann_date.notna() & (df.ann_date <= cutoff)]
    df=df.sort_values(['ts_code','ann_date'])
    out=[]
    for code, g in df.groupby('ts_code',sort=True):
        prev_agency=None
        for _, row in g.iterrows():
            opinion=str(row.get('audit_result') or '').strip()
            # Order matters: '非标准无保留' contains '无保留'; unknown terms stay unknown.
            if any(w in opinion for w in ['无法表示意见','无法发表意见','拒绝表示意见']): kind='disclaimer'
            elif '否定意见' in opinion: kind='adverse'
            elif '保留意见' in opinion and '无保留' not in opinion: kind='qualified'
            elif any(w in opinion for w in ['带强调事项段','强调事项段','持续经营重大不确定性']): kind='emphasis_or_uncertainty'
            elif '标准无保留' in opinion or '无保留意见' in opinion: kind='unmodified'
            else: kind='unknown'
            agency=str(row.get('audit_agency') or '').strip()
            change = bool(agency and prev_agency and agency != prev_agency)
            if agency:prev_agency=agency
            out.append({
                'ts_code':str(code), 'report_period':_date(row.get('end_date')),
                'available_at':row.ann_date.date().isoformat(),'opinion_original':opinion,
                'opinion_type':kind,'audit_agency':agency or None,
                'auditor_changed_vs_previous_observation':change,
                'status':'requires_review' if change or kind in ('qualified','adverse','disclaimer','emphasis_or_uncertainty','unknown') else 'observation',
                'evidence_level':'structured_provider_field',
                'source':str(row.get('source','tushare.fina_audit')),
                'source_url':_url(row.get('source_url')),
                'caution':'审计意见文字分类不代表法律或舞弊认定；审计机构变更要结合原因与报告期核实。'
            })
    return out


def pledge_risk_review(pledges:pd.DataFrame,as_of:str,ratio_threshold_pct:float=50,
                       change_threshold_pp:float=15) -> list[dict]:
    """Share pledge ratio: provider percentages are in percent, NOT fractional.
    Never infer *controller's* personal pledge ratio from issuer-level data.
    """
    if not 0<=ratio_threshold_pct<=100 or not 0<change_threshold_pp<=100:
        raise ValueError('invalid percentage thresholds')
    if not {'ts_code','end_date','pledge_ratio'}.issubset(pledges.columns):
        raise ValueError('pledges needs ts_code, end_date, pledge_ratio')
    df=pledges.copy()
    df['end_date']=pd.to_datetime(df.end_date.astype(str),errors='coerce')
    df['pledge_ratio']=pd.to_numeric(df.pledge_ratio,errors='coerce')
    cutoff=pd.Timestamp(as_of)
    df=df[df.end_date.notna() & (df.end_date<=cutoff)].sort_values(['ts_code','end_date'])
    out=[]
    for code,g in df.groupby('ts_code'):
        prev=None
        for _,r in g.iterrows():
            val=float(r.pledge_ratio) if pd.notna(r.pledge_ratio) else None
            valid=val is not None and 0<=val<=100
            delta=val-prev if valid and prev is not None else None
            flags=[]
            if valid and val>=ratio_threshold_pct:flags.append('high_issuer_pledge_ratio')
            if delta is not None and delta>=change_threshold_pp:flags.append('large_issuer_pledge_increase')
            out.append({'ts_code':str(code),'available_at':r.end_date.date().isoformat(),
                        'issuer_pledge_ratio_pct':val if valid else None,
                        'change_pp':delta,'flags':flags,
                        'status':'not_evaluable' if not valid else 'triggered' if flags else 'not_triggered',
                        'thresholds':{'ratio_pct':ratio_threshold_pct,'increase_pp':change_threshold_pp},
                        'evidence_level':'structured_provider_field','data_source':str(r.get('source','tushare.pledge_stat')),
                        'caution':'公司整体质押比例≠控股股东个人质押比例；阈值仅为研究初值，非监管结论。'})
            if valid:prev=val
    return out


TAGS={
 'accounting_restatement':['会计差错更正','追溯重述','前期会计差错'],
 'auditor_change':['变更会计师事务所','改聘会计师事务所','更换审计机构'],
 'nonstandard_audit':['非标准审计意见','保留意见','无法表示意见','否定意见'],
 'guarantee':['对外担保','违规担保','担保进展'],
 'share_freeze':['司法冻结','股份被冻结','轮候冻结'],
 'share_sale':['减持计划','减持股份','股东减持'],
 'litigation':['重大诉讼','重大仲裁','诉讼进展'],
 'regulatory_action':['行政处罚','纪律处分','监管措施','立案调查','监管问询'],
 'related_party':['关联交易','关联方资金占用','非经营性资金占用'],
 'debt_stress':['债务逾期','债务违约','偿债风险','贷款逾期'],
}

def filing_event_triage(filings:pd.DataFrame, as_of:str)->list[dict]:
    required={'ts_code','ann_date','title','url'}
    missing=required-set(filings.columns)
    if missing:raise ValueError(f'filing_event_triage missing {sorted(missing)}')
    cutoff=pd.Timestamp(as_of)
    result=[]
    for r in filings.to_dict('records'):
        dt=_date(r['ann_date']); link=_url(r['url'])
        if not dt or pd.Timestamp(dt)>cutoff:continue
        title=str(r['title'] or '').strip()
        categories=[tag for tag,terms in TAGS.items() if any(t in title for t in terms)]
        if not categories:continue
        result.append({'ts_code':str(r['ts_code']),'published_at':dt,'title':title,
                       'source_url':link,'categories':categories,'evidence_level':'title_only',
                       'review_status':'unreviewed','requires_primary_document':True,
                       'caution':'仅标题关键词初筛；并未阅读全文，不能断言公告内容、违法事实或案件结论。'})
    return sorted(result,key=lambda x:(x['published_at'],x['ts_code']),reverse=True)


OFFICIAL_CHECKLIST=[
    ('证监会公开信息','https://www.csrc.gov.cn/','监管措施/行政处罚，以真实公布内容为准'),
    ('上交所','https://www.sse.com.cn/','交易所纪律处分/问询函'),
    ('深交所','https://www.szse.cn/','交易所纪律处分/问询函'),
    ('中国执行信息公开网','https://zxgk.court.gov.cn/','执行案件查询需人工核实身份'),
    ('国家企业信用信息公示系统','https://www.gsxt.gov.cn/','企业登记与关联主体，留意同名误匹配'),
]

def controller_legal_checklist(entities:list[dict],as_of:str)->list[dict]:
    """Generate manual verification tasks, NEVER auto-attribute a court record to a person.
    Requires supplied issuer/subject/role; URLs are navigation targets, not fetched results.
    """
    cutoff=_date(as_of)
    if not cutoff: raise ValueError('invalid as_of')
    out=[]
    for entity in entities:
        if not all(str(entity.get(k,'')).strip() for k in ('ts_code','subject_name','role')):
            raise ValueError('requires ts_code,subject_name,role')
        for source,link,purpose in OFFICIAL_CHECKLIST:
            out.append({'ts_code':str(entity['ts_code']),'subject_name':str(entity['subject_name']),
                        'role':str(entity['role']),'jurisdiction':str(entity.get('jurisdiction','中国')),
                        'as_of':cutoff,'official_source':source,'official_url':link,
                        'check_purpose':purpose,'match_status':'not_checked',
                        'case_status':'not_checked','review_status':'pending_human_verification',
                        'identity_disambiguation_required':True,
                        'caution':'同名并非同一人；调查、指控和生效裁决必须分开记录；未核查不代表无风险。'})
    return out


def disclosed_ownership_graph(holders:pd.DataFrame,as_of:str,controller_links:list[dict]|None=None)->dict:
    """Disclosed shareholding relationships with PIT; never assert control from a top-ten holder.
    `controller_links` only admitted if `human_verified=True` and HTTPS primary evidence given.
    """
    required={'ts_code','holder_name','hold_ratio','ann_date'}
    if not required.issubset(holders.columns):
        raise ValueError(f'missing holder columns {sorted(required-set(holders.columns))}')
    cutoff=pd.Timestamp(as_of)
    x=holders.copy()
    x['ann_date']=pd.to_datetime(x.ann_date.astype(str),errors='coerce')
    x['hold_ratio']=pd.to_numeric(x.hold_ratio,errors='coerce')
    x=x[x.ann_date.notna() & (x.ann_date<=cutoff)]
    # Retain only most recently disclosed *report period* per issuer to avoid duplicated stale edges.
    if 'end_date' in x:
        x['end_date']=pd.to_datetime(x.end_date.astype(str),errors='coerce')
        x=x[x.end_date.notna() & (x.end_date<=cutoff)]
        latest=x.groupby('ts_code')['end_date'].transform('max')
        x=x[x.end_date==latest]
    edges=[]
    for r in x.to_dict('records'):
        share=r['hold_ratio']
        if pd.isna(share) or not 0<=share<=100:continue
        if not str(r['holder_name']).strip():continue
        edges.append({'source_subject':str(r['holder_name']),'target_issuer':str(r['ts_code']),
                      'relationship':'disclosed_shareholder','shareholding_pct':float(share),
                      'available_at':r['ann_date'].date().isoformat(),
                      'report_period':_date(r.get('end_date')) if r.get('end_date') is not None else None,
                      'human_verified_control':False,
                      'caution':'前十大股东记录不能自行证明实际控制或最终受益所有权。'})
    for link in controller_links or []:
        if link.get('human_verified') is not True:continue
        url=_url(link.get('evidence_url'))
        avail=_date(link.get('published_at'))
        if not url or not avail or pd.Timestamp(avail)>cutoff:continue
        if not all(str(link.get(k) or '').strip() for k in ('subject_name','ts_code','relationship')):continue
        edges.append({'source_subject':str(link['subject_name']),'target_issuer':str(link['ts_code']),
                      'relationship':str(link['relationship']),'shareholding_pct':None,
                      'available_at':avail,'source_url':url,
                      'human_verified_control':True,'verified_by':link.get('verified_by'),
                      'caution':'人工审核的历史关系，需确认任职期间和身份一致性。'})
    return {'as_of':as_of,'edges':edges,'edge_count':len(edges),
            'limitations':'持股关系≠实际控制，未核实人员身份不得归属司法案件。'}
