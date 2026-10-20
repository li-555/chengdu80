"""Regulatory horizon scanning on authorised/supplied documents, not website scraping.
Never claims that a modified rule legally applies to a specific firm automatically.
"""
from __future__ import annotations
import hashlib
from urllib.parse import urlparse
import pandas as pd

TOPICS={
 '信息披露':['信息披露','年度报告','临时公告','披露义务'],
 '上市与退市':['退市','上市规则','退市风险'],
 '公司治理':['独立董事','关联交易','董事会','股东大会'],
 '证券发行':['再融资','定向增发','证券发行','IPO'],
 '投资者保护':['投资者保护','投资者适当性','投资者权益'],
 '反洗钱与合规':['反洗钱','客户身份识别','反商业贿赂'],
 '资产管理':['资产管理','基金管理','资管产品'],
}

def classify_regulatory_topics(text:str)->list[str]:
    return [k for k,v in TOPICS.items() if any(w in (text or '') for w in v)] or ['未分类_需人工处理']


def _date(x):
    v=pd.to_datetime(x,errors='coerce')
    return None if pd.isna(v) else v.date().isoformat()


def _approved_url(x):
    parsed=urlparse(str(x or ''))
    return str(x) if parsed.scheme == 'https' and parsed.hostname else None


def regulatory_change_tracker(previous:list[dict], current:list[dict],as_of:str)->list[dict]:
    """Compare two operator-supplied snapshots by stable document ID.
    No inferred repeal from an absent record: disappearance might be collection failure.
    Published and effective dates are input facts, not LLM guesses.
    """
    cutoff=_date(as_of)
    if not cutoff:raise ValueError('invalid cutoff')
    def prepare(rows):
        d={}
        for r in rows:
            required=('document_id','title','published_at','authority','source_url','text')
            if not all(str(r.get(k,'')).strip() for k in required):
                raise ValueError(f'regulation needs {required}')
            pub=_date(r['published_at']); url=_approved_url(r['source_url'])
            if not pub or not url:raise ValueError('invalid publication date or HTTPS source URL')
            if pub>cutoff:continue
            rid=str(r['document_id'])
            if rid in d:raise ValueError('duplicate regulation document_id')
            d[rid]={**r,'published_at':pub,'source_url':url,'effective_at':_date(r.get('effective_at')),
                    'digest':hashlib.sha256(str(r['text']).encode()).hexdigest()}
        return d
    before,after=prepare(previous),prepare(current)
    result=[]
    for key,row in after.items():
        old=before.get(key)
        status='new' if old is None else 'amended' if old['digest']!=row['digest'] else 'unchanged'
        if status=='unchanged':continue
        result.append({'document_id':key,'change_type':status,'title':row['title'],
                       'authority':row['authority'],'source_url':row['source_url'],
                       'published_at':row['published_at'],'effective_at':row['effective_at'],
                       'effective_date_status':'provided' if row['effective_at'] else 'unknown_needs_review',
                       'topics':classify_regulatory_topics(row['title']+' '+str(row['text'])[:2000]),
                       'old_digest':old['digest'] if old else None,'new_digest':row['digest'],
                       'review_status':'unreviewed',
                       'caution':'仅版本差异；适用主体、法律效力和实际义务需由合规人员核实。'})
    for key,row in before.items():
        if key not in after:
            result.append({'document_id':key,'change_type':'missing_from_latest_snapshot',
                           'title':row['title'],'source_url':row['source_url'],
                           'review_status':'verify_collection_completeness',
                           'caution':'新版数据缺失不代表法规废止，须核验采集覆盖。'})
    return sorted(result,key=lambda r:r['document_id'])
