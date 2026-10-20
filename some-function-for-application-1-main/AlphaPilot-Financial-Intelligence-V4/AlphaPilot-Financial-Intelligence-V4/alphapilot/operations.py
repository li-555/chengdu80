"""Typed naming convention for registered Blocks-style operations, never arbitrary code execution."""
from .analytics import performance, indicators, observation_signals, compare_stocks, valuation_snapshot, price_threshold_signals
from .fundamentals import f10_cards,compare_fundamentals,announcement_watch
from .industry import industry_membership
from .portfolio import portfolio_risk
from .ml_anomaly import detect_market_anomalies
from .macro_research import macro_release
from .briefing import daily_briefing
from .mature_algorithms import technical_indicators_external, performance_quantstats
from .knowledge import knowledge_search
from .advanced_fundamentals import cash_earnings_quality,top_holder_concentration
from .backtest import sma_rule_backtest
from .industry_breadth import industry_daily_breadth
from .financial_forensics import altman_em_score, piotroski_f_score, accrual_quality, regguard_red_flags, audit_filing_triage, beneish_m_score
from .research_rules import screen_accounting_red_flags, compare_peer_scores

ALLOWED_OPERATIONS={
    'finance.performance': performance,
    'finance.technical_indicators': indicators,
    'finance.observation_signals': observation_signals,
    'finance.compare_stocks': compare_stocks,
    'finance.valuation_snapshot': valuation_snapshot,
    'finance.price_threshold_signals': price_threshold_signals,
    'finance.f10_cards': f10_cards,
    'finance.compare_fundamentals': compare_fundamentals,
    'finance.announcement_watch': announcement_watch,
    'finance.industry_membership': industry_membership,
    'finance.portfolio_risk': portfolio_risk,
    'finance.daily_briefing': daily_briefing,
    'finance.macro_release': macro_release,
    'finance.technical_indicators_external': technical_indicators_external,
    'finance.performance_quantstats': performance_quantstats,
    'ml.anomaly_isolation_forest': detect_market_anomalies,
    'knowledge.search': knowledge_search,
    'finance.cash_earnings_quality': cash_earnings_quality,
    'finance.top_holder_concentration': top_holder_concentration,
    'finance.sma_rule_backtest': sma_rule_backtest,
    'finance.industry_daily_breadth': industry_daily_breadth,
    'finance.altman_em_z': altman_em_score,
    'finance.piotroski_f': piotroski_f_score,
    'finance.accrual_quality': accrual_quality,
    'regguard.red_flag_rules': regguard_red_flags,
    'regguard.beneish_m': beneish_m_score,
    'regguard.audit_title_triage': audit_filing_triage,
    'regguard.screen_accounting_v2': screen_accounting_red_flags,
    'finance.compare_peer_scores': compare_peer_scores,
}

# Only signatures below are advertised to AI: expected args and semantics.
OPERATION_METADATA={
    'finance.performance':('历史风险绩效：收益、波动率、最大回撤、Sharpe','bars'),
    'finance.technical_indicators':('价格技术指标：MA20/60、RSI14、MACD、ATR14、成交量倍数','bars'),
    'finance.observation_signals':('收盘后技术观察：均线交叉、RSI、放量；不是买卖建议','bars'),
    'finance.compare_stocks':('同日期窗口股票收益和历史风险比较','bars_by_code'),
    'finance.valuation_snapshot':('估值快照：PE_TTM、PB，注明日期','daily_basic'),
    'finance.price_threshold_signals':('收盘价阈值交叉观察信号（不是实时提醒）','bars'),
    'finance.f10_cards':('依据披露日期的F10财务指标卡，防止未来信息泄漏','indicators,as_of'),
    'finance.compare_fundamentals':('2–5股票基本面和估值对比，报告期校验','indicators,valuation,as_of,codes'),
    'finance.announcement_watch':('公告标题关键词检索，必须提示非全文分析','announcements,as_of'),
    'finance.industry_membership':('行业成员查询，使用纳入/剔除日期','frame,as_of'),
    'finance.portfolio_risk':('组合权重、集中度、相关性、历史波动、回撤','bars_by_code'),
    'finance.daily_briefing':('组合收盘后研究事实包，供LLM写报告','bars_by_code,as_of'),
    'finance.macro_release':('宏观发布实际、前值、预期差比较，不编造预期','series_id,actual'),
    'finance.technical_indicators_external':('第三方 pandas-ta-classic 的RSI/MACD/布林带','bars'),
    'finance.performance_quantstats':('第三方 QuantStats 的 Sharpe/波动率/回撤','bars'),
    'ml.anomaly_isolation_forest':('机器学习历史异常检测；非收益预测/风险概率','bars'),
    'knowledge.search':('依据官方出处检索金融方法和资讯摘要','con,query'),
    'finance.cash_earnings_quality':('按披露时间与报告期对齐，比较经营现金流与归母净利润','income,cashflow,as_of'),
    'finance.top_holder_concentration':('前十大股东集中度，不能等同实控人','holdings,as_of'),
    'finance.sma_rule_backtest':('均线信号下一交易日生效的历史策略模拟，含交易费假设','bars'),
    'finance.industry_daily_breadth':('行业市场广度：上涨比例、中位收益、等权收益和成交额','daily,members,as_of'),
    'finance.altman_em_z':('Altman 新兴市场 Z双撇：非金融企业偿债能力描述分数，不输出统一风险等级','balance,income,as_of'),
    'finance.piotroski_f':('Piotroski 财务健康九信号；无增发数据则标记不完整；非舞弊模型','balance,income,cashflow,as_of'),
    'finance.accrual_quality':('净利润与经营现金流背离程度，以平均资产归一；明确变量口径','balance,income,cashflow,as_of'),
    'regguard.red_flag_rules':('待复核风险线索 R1/R2/R7，非违法或舞弊事实','balance,income,cashflow,as_of'),
    'regguard.beneish_m':('Beneish 八因子财务操纵模式参考分数；未经 A 股校准，非舞弊概率','balance,income,cashflow,as_of'),
    'regguard.audit_title_triage':('公告标题级财报/审计/质押/司法线索筛选，不代表读取正文','filings,as_of'),
    'regguard.screen_accounting_v2':('研究规则R1/R2/R3/R4/R7/R11，明确标记不可计算的项目；非财务舞弊判定','balance,income,cashflow,as_of'),
    'finance.compare_peer_scores':('同一行业、同一报告期且已披露的样本内金融评分百分位；至少8家且非概率','records,as_of'),
}

def run_named_operation(operation: str, **kwargs):
    if operation not in ALLOWED_OPERATIONS:
        raise ValueError(f'Unsupported operation: {operation}')
    return ALLOWED_OPERATIONS[operation](**kwargs)
