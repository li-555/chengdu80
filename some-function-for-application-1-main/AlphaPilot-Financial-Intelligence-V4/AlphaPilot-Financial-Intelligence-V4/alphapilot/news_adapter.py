"""Optional GDELT DOC metadata discovery for geopolitical/industry news.

Searches open index and returns titles/links/dates. The underlying articles may
require publisher subscriptions; we NEVER fetch or copy their full text.
"""
from __future__ import annotations
import json
from urllib.request import Request,urlopen
from urllib.parse import urlencode, urlparse

ENDPOINT='https://api.gdeltproject.org/api/v2/doc/doc'

def gdelt_headlines(query:str,timespan:str='1week',max_records:int=20)->list[dict]:
    if not 2<=len(query.strip())<=150:raise ValueError('Search 2–150 characters')
    if timespan not in ('1day','1week','2weeks','1month'):raise ValueError('Unsupported time span')
    if not 1<=max_records<=50:raise ValueError('Too many results')
    url=ENDPOINT+'?'+urlencode({'query':query,'mode':'ArtList','format':'json',
                               'timespan':timespan,'maxrecords':max_records})
    with urlopen(Request(url,headers={'User-Agent':'AlphaPilot/0.2 academic demo'}),timeout=15) as r:
        payload=r.read(2*1024*1024)
    data=json.loads(payload)
    out=[]
    for a in data.get('articles',[]):
        link=str(a.get('url',''))
        if urlparse(link).scheme!='https':continue
        out.append({'title':a.get('title'),'url':link,'published_at':a.get('seendate'),
                    'source_domain':a.get('domain'),'language':a.get('language'),
                    'source':'GDELT DOC search index','evidence_level':'article_metadata_only',
                    'verified_event':False})
    return out
