from pathlib import Path
import json
from regguard.registry import export_tool_catalogue
root=Path(__file__).parent
manifest=export_tool_catalogue()
(root/'catalog'/'regguard_ai_tools.json').write_text(json.dumps({'format':'regguard-tool-metadata-v1','tools':manifest},ensure_ascii=False,indent=2,default=str),encoding='utf-8')
print('Exported',len(manifest),'tools')
