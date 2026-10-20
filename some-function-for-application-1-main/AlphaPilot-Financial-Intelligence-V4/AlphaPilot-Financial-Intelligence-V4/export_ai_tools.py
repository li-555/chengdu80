"""Expose operation capabilities for third-party LLMs and developers."""
from alphapilot.application_runtime import tools_for_ai
import json
from pathlib import Path

p=Path('catalog/ai_tools.json');p.parent.mkdir(exist_ok=True)
p.write_text(json.dumps({'schema_version':'0.2','note':'Prototype operation manifest, not official Blocks platform schema','tools':tools_for_ai()},ensure_ascii=False,indent=2),encoding='utf-8')
print('Exported',p)
