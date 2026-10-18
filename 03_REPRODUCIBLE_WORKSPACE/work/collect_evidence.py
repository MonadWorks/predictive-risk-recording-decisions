from pathlib import Path
import json,hashlib,shutil,subprocess,datetime
src=Path('/Users/dujiayi/Documents/Codex/2026-10-16/ic-1-range-2-3-agent')
root=Path('/Users/dujiayi/Documents/Codex/2026-10-18/icbr-2026')
dst=root/'work/evidence'
exclude={'__pycache__','.DS_Store','.cache','baseline'}
for name in ['outputs','ICBR2026_v4_pack']:
 shutil.copytree(src/name,dst/name,dirs_exist_ok=True,ignore=shutil.ignore_patterns(*exclude))
cp=Path('/Users/dujiayi/.claude/projects/-Users-dujiayi-Documents-Codex-2026-10-16-ic-1-range-2-3-agent')
conversations=[]
for f in cp.glob('*.jsonl'):
 for line in f.open():
  try:d=json.loads(line)
  except:continue
  if d.get('type') not in ['user','assistant']:continue
  c=d.get('message',{}).get('content',[])
  text=c if isinstance(c,str) else '\n'.join(x.get('text','') for x in c if x.get('type')=='text')
  if text:conversations.append({'session':f.stem,'timestamp':d.get('timestamp'),'type':d['type'],'text':text})
(dst/'claude_conversation_text.json').write_text(json.dumps(conversations,ensure_ascii=False,indent=2))
manifest=[]
for base in [src/'outputs',src/'ICBR2026_v4_pack',src/'work']:
 for p in base.rglob('*'):
  if not p.is_file() or any(x in p.parts for x in ['uv-cache','pip-cache','research-v2-env','__pycache__','.cache']):continue
  manifest.append({'path':str(p),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
(root/'outputs/local_evidence_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
checks={}
for n,p in [('v2','outputs/research_v2/validate_package.py'),('v3','outputs/research_craft_v3/validate_delivery.py'),('v4','ICBR2026_v4_pack/validate_pack.py')]:
 r=subprocess.run(['python3',str(dst/p)],capture_output=True,text=True)
 checks[n]={'returncode':r.returncode,'stdout':r.stdout,'stderr':r.stderr}
v4=dst/'ICBR2026_v4_pack/05_data_and_code/source_data'
v2=dst/'outputs/research_v2'
checks['v4_origin_to_v2']={n:hashlib.sha256((v4/n).read_bytes()).hexdigest()==r['sha256']==hashlib.sha256((v2/r['companion_v2_path']).read_bytes()).hexdigest() for n,r in json.loads((v4/'origin_manifest.json').read_text()).items()}
(root/'outputs/verification_receipt.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2))
print(json.dumps({'manifest_files':len(manifest),'claude_text_messages':len(conversations),'checks':{k:v['returncode'] for k,v in checks.items() if 'returncode' in v},'v4_v2_origins_all_match':all(checks['v4_origin_to_v2'].values())}))
