"""Local auditable keyword knowledge base, plus operator-triggered whitelisted official RSS metadata updates.

No embeddings/LLM needed; does not copy paywalled articles or make unbounded web requests.
"""
from __future__ import annotations
import hashlib
import html
import re
import sqlite3
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import urlopen,Request
import xml.etree.ElementTree as ET

OFFICIAL_FEEDS={
    'fed_monetary':'https://www.federalreserve.gov/feeds/press_monetary.xml',
    'fed_all_press':'https://www.federalreserve.gov/feeds/press_all.xml',
}

METHODS=[
    {'id':'f10_roe','title':'ROE 净资产收益率','body':'ROE 反映利润相对权益资本的关系。横向比较需统一报告期、是否扣非、行业和资本结构；高杠杆可以推高 ROE。','topic':'fundamental','url':'https://tushare.pro/document/2'},
    {'id':'cash_quality','title':'现金流与利润质量','body':'比较经营现金流、净利润和应收账款变化，但单期差异并不自动构成财务问题。需要结合业务周期与行业特点。','topic':'fundamental','url':'https://www.sec.gov/search-filings/edgar-application-programming-interfaces'},
    {'id':'macd','title':'MACD 指数平滑异同移动平均线','body':'基于短期和长期指数移动平均计算趋势动量；交叉与背离是描述历史走势的指标，不能保证未来价格。','topic':'technical','url':'https://github.com/xgboosted/pandas-ta-classic'},
    {'id':'rsi','title':'RSI 相对强弱指数','body':'RSI 描述一定时间窗口内上涨与下跌幅度的相对强弱；RSI>70不等于股票一定下跌。','topic':'technical','url':'https://github.com/xgboosted/pandas-ta-classic'},
    {'id':'sharpe','title':'夏普比率与投资组合风险','body':'Sharpe 衡量超额收益与收益波动的比率，计算必须注明收益率频率、年化因子、无风险利率和样本区间。','topic':'risk','url':'https://github.com/ranaroussi/quantstats'},
    {'id':'nonfarm','title':'非农就业数据及市场传导','body':'美国非农就业来源应首先核对 BLS 官方数据；就业增加不直接推出股市涨跌，需要结合市场预期、工资、失业率及货币政策路径。','topic':'macro','url':'https://www.bls.gov/developers/home.htm'},
    {'id':'rate_policy','title':'FOMC 货币政策与行业敞口','body':'政策利率预期可能影响折现率、汇率和融资成本；对公司股价影响取决于市场预期、资本结构、行业和时间范围。','topic':'macro','url':'https://www.federalreserve.gov/feeds/feeds.htm'},
    {'id':'piotroski_f','title':'Piotroski F-Score 九项财务健康信号','body':'九项0/1年度信号用于研究企业基本面变化，原始研究聚焦价值股的财务强弱。不能当成财务造假判断。年度口径必须一致，缺失增发证据时得分不完整。','topic':'fundamental','url':'https://link.springer.com/article/10.1057/s41260-020-00157-2'},
    {'id':'beneish_m','title':'Beneish M-Score 财务操纵模式研究指标','body':'八项指标及美国历史样本系数是一种研究参考，不等于A股舞弊概率。严禁未经本土校准使用原始阈值做违法认定；必须列出各因子贡献和缺失字段。','topic':'risk','url':'https://www.aaii.com/journal/article/83450-detecting-earnings-manipulation-with-the-m-score'},
    {'id':'altman_em','title':'Altman 新兴市场 Z双撇模型','body':'包含新兴市场3.25常数项的版本用于描述部分非金融企业财务结构，不是违约概率；不同版本阈值不可混用，行业与会计制度需要考虑。','topic':'risk','url':'https://github.com/fabioc-aloha/Altman-Z-Score/blob/main/MODELS.md'},
    {'id':'receivables_quality','title':'应收与现金流质量：R1/R2/R4','body':'观察现金流转化、应收相对营收增长、其他应收占资产比例。工程阈值需要针对行业与业务周期校准，不应从单一比率直接推断财务舞弊。','topic':'risk','url':'https://tushare.pro/document/2'},
    {'id':'point_in_time','title':'财报发布日期和防止未来信息泄漏','body':'必须区分 end_date 财务报告期和 ann_date 披露日期；历史模拟不能在披露前使用未来财报或修订数据。','topic':'methodology','url':'https://tushare.pro/document/2'},
]


def connect_knowledge(db_path:str|Path='alphapilot_knowledge.sqlite')->sqlite3.Connection:
    c=sqlite3.connect(str(db_path))
    c.execute('''CREATE TABLE IF NOT EXISTS knowledge (
        doc_id TEXT PRIMARY KEY,title TEXT NOT NULL, body TEXT NOT NULL,
        topic TEXT NOT NULL,source_url TEXT NOT NULL, published_at TEXT,
        observed_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP, content_type TEXT NOT NULL)''')
    c.execute('CREATE INDEX IF NOT EXISTS idx_knowledge_topic ON knowledge(topic)')
    c.commit();return c


def upsert_knowledge(con:sqlite3.Connection,doc_id:str,title:str,body:str,topic:str,source_url:str,
                     published_at:str|None=None,content_type:str='methodology'):
    if not source_url.startswith('https://'):raise ValueError('Source URL must be HTTPS')
    if not title or not doc_id:raise ValueError('Missing document identity')
    con.execute('''INSERT INTO knowledge(doc_id,title,body,topic,source_url,published_at,content_type)
                VALUES(?,?,?,?,?,?,?) ON CONFLICT(doc_id) DO UPDATE SET title=excluded.title,
                body=excluded.body,topic=excluded.topic,source_url=excluded.source_url,
                published_at=excluded.published_at,content_type=excluded.content_type,
                observed_at=CURRENT_TIMESTAMP''',(doc_id,title,body,topic,source_url,published_at,content_type))
    con.commit()


def seed_methods(con:sqlite3.Connection)->int:
    for row in METHODS:
        upsert_knowledge(con,row['id'],row['title'],row['body'],row['topic'],row['url'])
    return len(METHODS)


def knowledge_search(con:sqlite3.Connection,query:str,limit:int=8,topic:str|None=None)->list[dict]:
    """Transparent bilingual lexical search; no claim of semantic vector embeddings."""
    if len(query.strip())<2:raise ValueError('Query must have at least 2 characters')
    if not 1<=limit<=20:raise ValueError('limit 1–20 only')
    tokens=re.findall(r'[a-zA-Z0-9]{2,}|[\u4e00-\u9fff]{2,}',query.lower())[:8]
    if not tokens: return []
    clauses=['(LOWER(title) LIKE ? OR LOWER(body) LIKE ?)' for _ in tokens]
    args=[]
    for word in tokens:args.extend(['%'+word+'%','%'+word+'%'])
    sql='SELECT doc_id,title,body,topic,source_url,published_at,content_type FROM knowledge WHERE ('+' OR '.join(clauses)+')'
    if topic:sql+=' AND topic=?';args.append(topic)
    sql+=' ORDER BY CASE content_type WHEN \'official_feed\' THEN 0 ELSE 1 END, observed_at DESC LIMIT ?';args.append(limit)
    return [dict(zip(['id','title','snippet','topic','url','published_at','content_type'],r)) for r in con.execute(sql,args).fetchall()]


def ingest_official_rss(con:sqlite3.Connection,feed_name:str,max_items:int=30,timeout:int=12)->int:
    """Fetch *only* predefined Fed feed. Store title, short official description and original link."""
    if feed_name not in OFFICIAL_FEEDS:raise ValueError('Feed not explicitly allowlisted')
    if not 1<=max_items<=100:raise ValueError('max_items must be 1–100')
    url=OFFICIAL_FEEDS[feed_name]
    with urlopen(Request(url,headers={'User-Agent':'AlphaPilot-Research-MVP/0.2 (team-operator)'}),timeout=timeout) as r:
        payload=r.read(1024*1024+1)
    if len(payload)>1024*1024:raise ValueError('Feed too large')
    root=ET.fromstring(payload)
    count=0
    for item in root.findall('.//item')[:max_items]:
        title=(item.findtext('title') or '').strip()
        link=(item.findtext('link') or '').strip()
        if not title or urlparse(link).hostname!='www.federalreserve.gov' or not link.startswith('https://'):continue
        abstract=html.unescape(re.sub('<[^>]+>',' ',item.findtext('description') or ''))[:600].strip()
        published=item.findtext('pubDate')
        doc_id='fed_'+hashlib.sha256(link.encode()).hexdigest()[:24]
        upsert_knowledge(con,doc_id,title,abstract,'macro',link,published,'official_feed');count+=1
    return count
