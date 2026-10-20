"""Optional operator-side US company facts snapshot via SEC EDGAR public API.

Applicable only to entities with a US SEC CIK; official US filings, not A-share F10.
Respect SEC Fair Access, set a descriptive user agent, use a cache, never scrape paywalls.
"""
from __future__ import annotations
import json
import os
from urllib.request import Request,urlopen


def sec_companyfacts(cik:str, user_agent:str|None=None)->dict:
    digits=str(cik).strip()
    if not digits.isdigit() or len(digits)>10:raise ValueError('CIK must be numeric and <= 10 digits')
    ua=user_agent or os.getenv('SEC_USER_AGENT')
    if not ua or '@' not in ua or len(ua)<12:raise RuntimeError('SEC_USER_AGENT must identify application and contact email')
    url=f'https://data.sec.gov/api/xbrl/companyfacts/CIK{int(digits):010d}.json'
    with urlopen(Request(url,headers={'User-Agent':ua,'Accept':'application/json'}),timeout=20) as r:
        payload=r.read(12*1024*1024)
    data=json.loads(payload)
    return {'source':'SEC EDGAR companyfacts','source_url':url,'cik':data.get('cik'),
            'entityName':data.get('entityName'),'facts':data.get('facts',{}),
            'note':'SEC disclosures use company-specific XBRL taxonomy and filed/period date. Normalize before peer comparison.'}
