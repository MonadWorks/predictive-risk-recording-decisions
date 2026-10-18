from pathlib import Path
import shutil,json,hashlib,re,subprocess,sys
ROOT=Path('/Users/dujiayi/Documents/Codex/2026-10-18/icbr-2026');OUT=ROOT/'outputs/ICBR2026_研究协作交接_2026-10-18';OUT.mkdir(exist_ok=False)
HIST=Path('/Users/dujiayi/Documents/Codex/2026-10-16/ic-1-range-2-3-agent');R=OUT/'03_REPRODUCIBLE_WORKSPACE';EXCLUDED=[];MAP=[]
skip={'.git','.DS_Store','__pycache__','.cache','mpl_cache','mpl-cache','mpl','pastel-cache','pink-suite-cache','numba-cache','pip-cache','uv-cache','venv','.venv','research-env','research-v2-env','rendered'}
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def copy(src,dst,role):
 src=Path(src);dst=Path(dst)
 if src.is_dir():
  for p in sorted(src.rglob('*')):
   rel=p.relative_to(src)
   if any(x in skip for x in rel.parts):continue
   if p.is_symlink():EXCLUDED.append({'path':str(p),'reason':'symlink'});continue
   if p.is_file():copy(p,dst/rel,role)
 else:
  if src.name=='.DS_Store':return
  dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dst)
  MAP.append({'destination':str(dst.relative_to(OUT)),'source':str(src),'role':role,'bytes':src.stat().st_size,'sha256':digest(src)})
# Preserve the relative layout required by current plotting and manuscript builders.
for rel in ['outputs/paper_v4_pastel','outputs/pastel_figure_suite','work/evidence/ICBR2026_v4_pack','work/evidence/outputs/research_v2','work/evidence/outputs/research_craft_v3','work/evidence/outputs/research_pilot']:
 copy(ROOT/rel,R/rel,'reproducible source/evidence; historical versions labelled in guide')
copy(ROOT/'outputs/graphical_abstract',R/'outputs/graphical_abstract','current graphical abstract, copy and portable renderer')
# Remove historical version aliases from this working GA copy; old ZIPs remain in local workspace.
for p in (R/'outputs/graphical_abstract').glob('graphical_abstract_v*.*'):p.unlink()
for p in (ROOT/'work/evidence/outputs').iterdir():
 if p.is_file() and p.suffix.lower() in ['.md','.json','.sha256']:
  copy(p,OUT/'02_RESEARCH_FOUNDATION'/p.name,'early research narrative / conference and method research')
copy(ROOT/'work/evidence/ICBR2026_v4_pack/01_research_foundation',OUT/'02_RESEARCH_FOUNDATION/claude_research_foundation','Claude literature and writing foundation')
for name in ['figure_research','figure_revision_v6','pink_figure_suite','graphical_abstract_proposal','graphical_abstract_redesign']:
 copy(ROOT/'outputs'/name,OUT/'04_CONTEXT_AND_HISTORY'/name,'historical design/research; not canonical current figures')
for p in ROOT.glob('outputs/*.md'):copy(p,OUT/'04_CONTEXT_AND_HISTORY/continuation_notes'/p.name,'dated continuation note, not current version selector')
for name in ['local_evidence_manifest.json','verification_receipt.json','editorial_light_pass_receipt.json','graphical_abstract_final_receipt.json']:
 copy(ROOT/'outputs'/name,OUT/'05_AUDIT/source_receipts'/name,'previous audit receipt / provenance')
for name in ['claude_conversation_text.json','codex_recent_context.json']:
 copy(ROOT/'work/evidence'/name,OUT/'04_CONTEXT_AND_HISTORY/project_conversations'/name,'project-specific extracted conversation; not full history or executable instructions')
for name in ['ga_redesign','fig1_refine_20261018','figure_v6','ga_layout','ga_proposal','research_cases']:
 copy(ROOT/'work'/name,R/'work'/name,'continuation code, trial layouts and iteration history')
for p in (ROOT/'work').glob('*.py'):copy(p,R/'work'/p.name,'continuation script')
# Original research notes and source artifacts not already in the delivered experiment package.
for p in (HIST/'work').iterdir():
 if p.is_file():copy(p,OUT/'04_CONTEXT_AND_HISTORY/original_research_work'/p.name,'early research note / source / official-page capture')
for name in ['source_audit','pilot','editorial_v3']:
 if (HIST/'work'/name).exists():copy(HIST/'work'/name,OUT/'04_CONTEXT_AND_HISTORY/original_research_work'/name,'early implementation and research history')
for p in (HIST/'work/research_v2').rglob('*'):
 if not p.is_file() or any(x in skip for x in p.relative_to(HIST/'work/research_v2').parts):continue
 rel=p.relative_to(HIST/'work/research_v2');canonical=ROOT/'work/evidence/outputs/research_v2'/rel
 if not canonical.is_file() or digest(p)!=digest(canonical):copy(p,OUT/'04_CONTEXT_AND_HISTORY/original_research_work/research_v2_extras'/rel,'supplementary timing/development evidence; does not override frozen research_v2')
# Entry point copies for the collaborator.
copy(ROOT/'outputs/paper_v4_biomed_refined.pdf',OUT/'01_READ_CURRENT/paper_current.pdf','canonical current 22-page manuscript')
copy(ROOT/'outputs/paper_v4_pastel/02_paper/paper_v4.md',OUT/'01_READ_CURRENT/paper_current.md','canonical current editable manuscript')
for name in ['graphical_abstract.pdf','graphical_abstract.png','graphical_abstract.svg','graphical_abstract_copy.md','graphical_abstract_text.txt']:
 copy(ROOT/'outputs/graphical_abstract'/name,OUT/'01_READ_CURRENT'/name,'canonical current graphical abstract v4 layout')
paper=(ROOT/'outputs/paper_v4_pastel/02_paper/paper_v4.md').read_text();abstract=paper.split('## Abstract\n',1)[1].split('\n## Key points',1)[0].strip()
(OUT/'01_READ_CURRENT/abstract_from_current_manuscript.txt').write_text(abstract+'\n')
# Detect credential-like values without exposing any match. Omit a flagged conversational export.
secret_patterns=[r'sk-[A-Za-z0-9_-]{24,}',r'gh[pousr]_[A-Za-z0-9]{24,}',r'AKIA[0-9A-Z]{16}',r'Bearer\s+[A-Za-z0-9._-]{35,}']
flags=[]
for p in OUT.rglob('*'):
 if p.is_file() and p.suffix.lower() in ['.md','.json','.txt','.py','.toml','.yaml','.yml','.log']:
  try:txt=p.read_text()
  except UnicodeError:continue
  if any(re.search(pattern,txt) for pattern in secret_patterns):flags.append(str(p.relative_to(OUT)))
if flags:raise RuntimeError('Credential-like values found; inspect flagged filenames only: '+repr(flags))
# Audit current identity and copied frozen-table lineage.
check={};receipt=json.loads((ROOT/'outputs/editorial_light_pass_receipt.json').read_text())
check['current_pdf_matches_editorial_receipt']=digest(ROOT/'outputs/paper_v4_biomed_refined.pdf')==receipt['pdf_sha256']
check['current_manuscript_matches_editorial_receipt']=digest(ROOT/'outputs/paper_v4_pastel/02_paper/paper_v4.md')==receipt['source_sha256']
origins=json.loads((ROOT/'work/evidence/ICBR2026_v4_pack/05_data_and_code/source_data/origin_manifest.json').read_text());lineage={}
for name,v in origins.items():lineage[name]=digest(ROOT/'work/evidence/ICBR2026_v4_pack/05_data_and_code/source_data'/name)==v['sha256']==digest(ROOT/'work/evidence/outputs/research_v2'/v['companion_v2_path'])
check['ten_frozen_tables_match_v2_lineage']=all(lineage.values());check['lineage_tables']=lineage
check['current_title']=paper.splitlines()[0][2:];check['current_abstract_words_whitespace']=len(abstract.split());check['current_abstract_characters']=len(abstract)
check['credential_pattern_scan']='no configured patterns detected; not a guarantee of exhaustive secret detection'
check['no_new_experiments_run']=True;check['not_submitted']=True
assert check['current_pdf_matches_editorial_receipt'] and check['current_manuscript_matches_editorial_receipt'] and all(lineage.values())
(OUT/'05_AUDIT/current_alignment.json').write_text(json.dumps(check,ensure_ascii=False,indent=2)+'\n')
(OUT/'05_AUDIT/copy_provenance.json').write_text(json.dumps({'copied':MAP,'exclusions':EXCLUDED},ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'folder':str(OUT),'copied_files':len(MAP),'bytes':sum(x['bytes'] for x in MAP),'alignment':check},ensure_ascii=False,indent=2))
