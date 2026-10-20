"""Seed/refresh local knowledge with manually written method cards and official Fed RSS.

Requires network when --online; fails visibly, never silently invents news.
"""
import argparse
from alphapilot.knowledge import connect_knowledge,seed_methods,ingest_official_rss

p=argparse.ArgumentParser();p.add_argument('--db',default='knowledge.sqlite');p.add_argument('--online',action='store_true')
a=p.parse_args()
con=connect_knowledge(a.db)
print('method cards seeded:',seed_methods(con))
if a.online:
    try:print('official Fed entries indexed:',ingest_official_rss(con,'fed_monetary'))
    except Exception as exc:raise SystemExit(f'Official feed update failed: {type(exc).__name__}: {exc}')
print('database:',a.db)
