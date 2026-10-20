"""Official U.S. macro series adapters; network requests are operator-side jobs only.

No press articles, paywalled content, or unverified geopolitical event scoring.
"""
from __future__ import annotations
import json
import os
from urllib.parse import urlencode
from urllib.request import Request, urlopen

BLS_NONFARM_PAYROLLS = 'CES0000000001'  # All employees, total nonfarm, seasonally adjusted, thousands


def bls_series(series_id: str = BLS_NONFARM_PAYROLLS) -> list[dict]:
    """Read official BLS observations (NOT consensus estimates, actual NFP surprises or exact release timestamps)."""
    if not series_id or len(series_id)>50 or not all(c.isupper() or c.isdigit() or c in '_-#' for c in series_id):
        raise ValueError('Unexpected series ID')
    url=f'https://api.bls.gov/publicAPI/v1/timeseries/data/{series_id}'
    with urlopen(Request(url, headers={'User-Agent': 'AlphaPilot-research-demo/0.2'}), timeout=15) as r:
        payload=json.load(r)
    if payload.get('status') != 'REQUEST_SUCCEEDED':
        raise RuntimeError('BLS request failed: '+str(payload.get('message')))
    out=[]
    for item in payload['Results']['series'][0]['data']:
        period=item.get('period','')
        if not (len(period)==3 and period.startswith('M') and period[1:].isdigit() and 1<=int(period[1:])<=12):
            continue
        out.append({'series_id':series_id,'observation_date':f"{item['year']}-{period[1:]}-01",
                    'value':float(item['value'].replace(',','')),'source':'U.S. BLS',
                    'unit':'thousands' if series_id==BLS_NONFARM_PAYROLLS else 'source-defined',
                    'published_at':None})  # Must enrich with release schedule before storing as event
    return out


def fred_observations(series_id: str, vintage_asof: str | None = None) -> list[dict]:
    """Fetch FRED series with its vintage metadata. Uses operator-owned key."""
    key=os.getenv('FRED_API_KEY')
    if not key:
        raise RuntimeError('FRED_API_KEY not configured')
    params={'series_id':series_id, 'api_key':key, 'file_type':'json'}
    if vintage_asof:
        import datetime
        datetime.date.fromisoformat(vintage_asof) # enforce ISO date
        params.update({'realtime_start':vintage_asof,'realtime_end':vintage_asof})
    query=urlencode(params)
    url=f'https://api.stlouisfed.org/fred/series/observations?{query}'
    with urlopen(Request(url,headers={'User-Agent':'AlphaPilot-research-demo/0.1'}),timeout=15) as r:
        payload=json.load(r)
    return [{'series_id':series_id,'observation_date':item['date'],
             'value':float(item['value']) if item['value']!='.' else None,
             'vintage_start':item.get('realtime_start'), 'vintage_end':item.get('realtime_end'),
             'source':'FRED', 'published_at':None} for item in payload['observations']]
