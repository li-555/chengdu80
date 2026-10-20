"""Explicit, finite set of RegGuard finance tools; discoverable by external AI and Blocks.
Function calls require trusted platform-bound data; no code-string evaluation.
"""
from __future__ import annotations
import inspect
from alphapilot.financial_forensics import altman_em_score,piotroski_f_score,beneish_m_score,accrual_quality
from alphapilot.research_rules import screen_accounting_red_flags,compare_peer_scores
from regguard.governance import audit_opinion_review,pledge_risk_review,filing_event_triage,controller_legal_checklist,disclosed_ownership_graph
from regguard.regulation import regulatory_change_tracker,classify_regulatory_topics
from regguard.ml import peer_outlier_screen
from regguard.reporting import consolidate_alerts,build_digest,build_evidence_pack
from regguard.datasets import dataset_coverage
from regguard.knowledge import knowledge_search

REGISTRY={
 'regguard.screen_financials':screen_accounting_red_flags,
 'regguard.altman_em_z':altman_em_score,
 'regguard.piotroski_f':piotroski_f_score,
 'regguard.beneish_m':beneish_m_score,
 'regguard.accrual_quality':accrual_quality,
 'regguard.compare_peer_scores':compare_peer_scores,
 'regguard.audit_opinion_review':audit_opinion_review,
 'regguard.pledge_risk_review':pledge_risk_review,
 'regguard.filing_event_triage':filing_event_triage,
 'regguard.controller_legal_checklist':controller_legal_checklist,
 'regguard.disclosed_ownership_graph':disclosed_ownership_graph,
 'regguard.regulatory_change_tracker':regulatory_change_tracker,
 'regguard.classify_regulatory_topics':classify_regulatory_topics,
 'regguard.peer_outlier_screen':peer_outlier_screen,
 'regguard.consolidate_alerts':consolidate_alerts,
 'regguard.build_digest':build_digest,
 'regguard.build_evidence_pack':build_evidence_pack,
 'regguard.dataset_coverage':dataset_coverage,
 'regguard.knowledge_search':knowledge_search,
}

TOOL_INFO={
 'regguard.screen_financials':('跨报告期财务红旗 R1/R2/R3/R4/R7/R11','财务报表已披露日期','R3数据不齐时不可计算；不判定舞弊','research'),
 'regguard.altman_em_z':('Altman 新兴市场 Z双撇描述性偿债评分','两张年报','非金融企业，禁止混用阈值版本','research'),
 'regguard.piotroski_f':('Piotroski 九项财务健康信号','连续两期年报/增发标记','不是欺诈检测；9项不全只输出部分分数','research'),
 'regguard.beneish_m':('Beneish 八因子财务操纵模式研究评分','两期合并财报','非舞弊概率；对A股适用性未经验证','research'),
 'regguard.accrual_quality':('经营应计质量比率','两期资产和经营现金流','有多种Sloan口径，不混同','research'),
 'regguard.compare_peer_scores':('同业同报告期评分样本内百分位','至少8家已披露同类企业','非概率，排序不代表结论','research'),
 'regguard.audit_opinion_review':('Tushare审计意见结构化字段分类及变更提醒','fina_audit数据表','文字分类仅供人工核实','review'),
 'regguard.pledge_risk_review':('公司整体质押比例和百分点变化','pledge_stat/公司统计','不等于实控人个人质押风险','review'),
 'regguard.filing_event_triage':('公告标题级监管、诉讼、重述、担保初筛','公告标题、日期、链接','必须打开原公告复核，禁止假装阅读全文','review'),
 'regguard.controller_legal_checklist':('生成实控人/董监高官方核查清单','已授权主体身份与角色','禁止同名自动认定；不爬验证码网站','manual'),
 'regguard.disclosed_ownership_graph':('前十大股东历史关系网络和已人工核实控制关系','公告时间+前十大股东/人工核实链接','持股不等于控制，需核对主体身份和时间','review'),
 'regguard.regulatory_change_tracker':('已授权监管文件快照新旧版本对比','官方文件两版全文和发布时间','缺失不等于废止；法律效力需人工核查','review'),
 'regguard.classify_regulatory_topics':('对监管文本按关键词分类','一段原文','非法律效力或合规义务结论','research'),
 'regguard.peer_outlier_screen':('稳健标准化+IsolationForest同业异常评分','同一期已披露完整指标>=30企业','非舞弊概率/非预测，需可选sklearn','optional_ml'),
 'regguard.consolidate_alerts':('合并独立风险线索并按复核优先级排列','已计算的规则与事件','不要合成黑盒总舞弊分','research'),
 'regguard.build_digest':('每日/每周风险线索事实汇总','已有风险事件与观察日期','不负责实际任务调度','research'),
 'regguard.build_evidence_pack':('供受控LLM解读的引用证据包','HTTPS来源/披露日期/原文摘录','无原文则不可编造；不负责调用外部模型','research'),
 'regguard.dataset_coverage':('查看比赛数据字典与RegGuard字段覆盖','catalog元数据','不是实际数据行或token授权证明','research'),
 'regguard.knowledge_search':('查询离线人工整理的会计/监管研究知识卡及引用','用户研究问题','不是实时法规库，不代表某法现行有效','research'),
}

def run_named_operation(operation:str,**kwargs):
    if operation not in REGISTRY:raise ValueError('Unapproved RegGuard operation')
    return REGISTRY[operation](**kwargs)


def export_tool_catalogue()->list[dict]:
    tools=[]
    for key,func in REGISTRY.items():
        description,inputs,limitations,kind=TOOL_INFO[key]
        params=[]
        for name,p in inspect.signature(func).parameters.items():
            params.append({'name':name,'required':p.default is inspect.Signature.empty,
                           'default':None if p.default is inspect.Signature.empty else p.default,
                           'type_hint':str(p.annotation) if p.annotation is not inspect.Signature.empty else 'unspecified'})
        tools.append({'name':key,'description_zh':description,'expected_data':inputs,
                      'limitations_zh':limitations,'execution_class':kind,'parameters':params,
                      'registered':True,
                      'side_effects':'none','blocks_compatible':'adapter_required'})
    return tools
