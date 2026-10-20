"""Rule-based release comparisons; market effect is a hypothesis, not a measured causality."""
from __future__ import annotations
import math

def macro_release(series_id:str,actual:float,prior:float|None=None,consensus:float|None=None,
                  unit:str='',published_at:str|None=None,source_url:str|None=None)->dict:
    if not series_id or not math.isfinite(float(actual)) or (prior is not None and not math.isfinite(float(prior))) or (consensus is not None and not math.isfinite(float(consensus))):
        raise ValueError('Invalid macro observation')
    return {'series_id':series_id,'actual':actual,'prior':prior,'consensus':consensus,
            'change_from_prior':(actual-prior if prior is not None else None),
            'surprise_to_consensus':(actual-consensus if consensus is not None else None),
            'published_at':published_at,'unit':unit,'source_url':source_url,
            'interpretation_policy':'Only same-unit, comparable seasonally-adjusted releases may be compared',
            'warnings':(['未提供市场一致预期，不得声称高于/低于预期。'] if consensus is None else [])+
                       (['需核对首次公布与修订数据的版本。'] if published_at is None else []),
            'investment_advice':False}
