"""Read-only collaboration-package checks; Python standard library only."""
from pathlib import Path
import hashlib,json,subprocess,sys
ROOT=Path(__file__).resolve().parent;W=ROOT/'03_REPRODUCIBLE_WORKSPACE'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 manifest=json.loads((ROOT/'SHA256SUMS.json').read_text())
 for rel,expected in manifest.items():
  p=ROOT/rel
  assert p.is_file() and sha(p)==expected,rel
 results={}
 for name,rel in [('research_v2','work/evidence/outputs/research_v2/validate_package.py'),('writing_v3','work/evidence/outputs/research_craft_v3/validate_delivery.py'),('claude_v4','work/evidence/ICBR2026_v4_pack/validate_pack.py')]:
  run=subprocess.run([sys.executable,str(W/rel)],text=True,capture_output=True)
  assert run.returncode==0,(name,run.stderr,run.stdout)
  results[name]='PASS'
 a=json.loads((ROOT/'05_AUDIT/current_alignment.json').read_text());assert all(a['lineage_tables'].values())
 cleanup=json.loads((ROOT/'05_AUDIT/manuscript_cleanup_receipt.json').read_text())
 assert a['current_manuscript_matches_cleanup_receipt'] and a['current_pdf_matches_cleanup_receipt']
 # These receipts describe the preserved original 22-page manuscript.
 assert sha(W/'outputs/paper_v4_pastel/02_paper/paper_v4.md')==cleanup['manuscript_sha256']
 assert sha(W/'outputs/paper_v4_pastel/06_latex/biomed/paper_v4_biomed.pdf')==cleanup['paper_pdf_sha256']==a['current_pdf_sha256']
 current=(ROOT/'01_READ_CURRENT/paper_current.md').read_text()
 canonical=(W/'outputs/endpoint_revision/paper.md').read_text()
 assert current==canonical.replace('(figures/','(../03_REPRODUCIBLE_WORKSPACE/outputs/endpoint_revision/figures/')
 assert 'Research manuscript v4' not in current and '<!--' not in current
 assert sha(ROOT/'01_READ_CURRENT/paper_current.pdf')==sha(W/'outputs/endpoint_revision/paper.pdf')
 abstract=canonical.split('## Abstract\n',1)[1].split('\n## Introduction',1)[0].strip()
 assert (ROOT/'01_READ_CURRENT/abstract_from_current_manuscript.txt').read_text().strip()==abstract
 run=subprocess.run([sys.executable,str(W/'work/recording_extensions/validate.py')],text=True,capture_output=True)
 assert run.returncode==0,(run.stderr,run.stdout)
 results['recording_extensions']=json.loads(run.stdout)
 run=subprocess.run([sys.executable,str(W/'work/recording_extensions/round4/code/validate4.py')],text=True,capture_output=True)
 assert run.returncode==0,(run.stderr,run.stdout)
 results['parameter_mechanism_and_robustness']=json.loads(run.stdout)
 run=subprocess.run([sys.executable,str(W/'work/recording_extensions/round5/code/validate5.py')],text=True,capture_output=True)
 assert run.returncode==0,(run.stderr,run.stdout)
 results['recording_information_confirmation']=json.loads(run.stdout)
 receipt=json.loads((ROOT/'05_AUDIT/supplementary_legend_revision_receipt.json').read_text());assert receipt['numerical_geometry_identical'] and receipt['pages']==22
 assert json.loads((ROOT/'05_AUDIT/geometry_before.json').read_text())==json.loads((ROOT/'05_AUDIT/geometry_after.json').read_text())
 for stem in ['figS2_matched_conditions_pastel','figS3_broad_conditions_pastel','figS4_bias_shift_conditions_pastel']:
  for ext in ['pdf','png','svg']:
   assert sha(W/'outputs/pastel_figure_suite/supplementary'/f'{stem}.{ext}')==sha(W/'outputs/paper_v4_pastel/03_figures/supplementary'/f'{stem}.{ext}')
 for ext in ['pdf','png','svg']:assert sha(ROOT/'01_READ_CURRENT'/f'graphical_abstract.{ext}')==sha(W/'outputs/graphical_abstract'/f'graphical_abstract.{ext}')
 for folder in [W/'outputs/pastel_figure_suite',W/'outputs/paper_v4_pastel']:
  for rel,h in json.loads((folder/'CURRENT_SHA256SUMS.json').read_text()).items():assert sha(folder/rel)==h
 for rel,v in json.loads((W/'work/evidence/ICBR2026_v4_pack/05_data_and_code/source_data/origin_manifest.json').read_text()).items():
  assert sha(W/'work/evidence/ICBR2026_v4_pack/05_data_and_code/source_data'/rel)==v['sha256']==sha(W/'work/evidence/outputs/research_v2'/v['companion_v2_path'])
 return {'status':'PASS','checks':results,'current_manuscript_and_assets':'PASS','frozen_table_lineage':'PASS','historical_supplementary_plot_data_geometry':'unchanged','historical_paper_pages':22,'not_submitted':True,'scope':'File integrity, raw-result aggregation and manuscript consistency; not full experiment rerun or scientific acceptance'}
if __name__=='__main__':print(json.dumps(main(),indent=2))
