"""Offline curated compliance and financial-method knowledge search.
Not a live-law feed, vector database, or substitute for current regulatory text.
"""
from __future__ import annotations
import json
import re
from pathlib import Path
from urllib.parse import urlparse


def knowledge_search(query:str,limit:int=5,cards:list[dict]|None=None)->list[dict]:
    if len(query.strip())<2:raise ValueError('query must have at least two characters')
    if not 1<=limit<=20:raise ValueError('limit must be 1..20')
    if cards is None:
        cards=json.loads((Path(__file__).resolve().parents[1]/'catalog'/'knowledge_cards.json').read_text(encoding='utf8'))
    words=re.findall(r'[a-zA-Z]{2,}|[\u4e00-\u9fff]{2,}',query.lower())[:12]
    # Chinese ngrams support natural-language queries without requiring a tokenizer.
    units=[]
    for w in words:
        if re.fullmatch(r'[\u4e00-\u9fff]+',w):
            units.extend([w[k:k+2] for k in range(len(w)-1)])
        else:units.append(w)
    matches=[]
    for row in cards:
        domain=' '.join(str(row.get(k,'')) for k in ('title','concept','operational_consequence')).lower()
        score=sum(u in domain for u in set(units))
        source=str(row.get('source_url') or '')
        p=urlparse(source)
        if score>0 and p.scheme=='https' and p.hostname:
            matches.append({'id':row.get('id'),'title':row.get('title'),
                            'concept':row.get('concept'),
                            'usage_limit':row.get('operational_consequence'),
                            'reference':row.get('source'),
                            'source_url':source,'match_count':score,
                            'status':'curated_offline_reference_not_live_update'})
    return sorted(matches,key=lambda x:(-x['match_count'],str(x['id'])))[:limit]
