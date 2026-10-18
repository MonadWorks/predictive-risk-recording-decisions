"""Assemble delivered records without caches, virtual environments or upstream code."""
from pathlib import Path
import hashlib,json,shutil,csv,zipfile

ROOT=Path(__file__).resolve().parent.parent
SRC=ROOT/'work/research_v2'
OUT=ROOT/'outputs/research_v2'
OUT.mkdir(parents=True,exist_ok=True)

def copy(src,dest):
    dest.parent.mkdir(parents=True,exist_ok=True)
    shutil.copy2(src,dest)

def ignored(path,names):
    return [n for n in names if n=='__pycache__' or 'cache' in n.lower() or n.endswith(('.pyc','.nbc','.nbi'))]

for name in ['models.py','design.py','inference.py','run.py','run_rank2.py',
             'rank2_refined.py','checks.py','diagnostics.py','analyze.py',
             'forecast_analysis.py','mechanism.py','svd_reference.py','linear_risk_control.py',
             'requirements.lock','smoke.json','development.json','holdout.json',
             'rank2_n100_refined.json','risk_forecast_followup.json',
             'final_holdout_freeze.json','risk_forecast_followup_freeze.json',
             'checks.json','checks_clean.log','diagnostics_results.json','diagnostics.log',
             'rank2_refined_checks.json','rank2_refined.log','rank2_refined_benchmark.log']:
    copy(SRC/name,OUT/name)

for name in ['package_smoke_run','development_run','holdout_run','risk_forecast_followup_run',
             'rank2_n100_refined_run','development_analysis','holdout_analysis',
             'forecast_followup_analysis','rank2_n100_refined_analysis',
             'mechanism_results','svd_reference_results','linear_risk_control_results']:
    shutil.copytree(SRC/name,OUT/name,dirs_exist_ok=True,ignore=ignored)
for name in ['development_run.log','holdout_run.log','risk_forecast_followup_run.log','rank2_n100_refined_run.log']:
    copy(SRC/name,OUT/'logs'/name)
for name in ['standards_v2.md','design_review_v2.md','baseline_v2.md','v2_code_audit.md',
             'holdout_results_audit.md','n100_final_audit.md','deep_writing_references.md',
             'analysis_reporting_audit.md']:
    if (ROOT/'work'/name).exists():copy(ROOT/'work'/name,OUT/'reviews'/name)
for name in ['ICBR2026_调研报告.md','ICBR2026_代表论文与相邻会议.md','研究收敛与纵向调研.md',
             '纵向方法文献审查.md','高水平论文结构参照.md','模型与数据来源审计.md',
             '阶段二研究报告.md','论文研究稿_v2.md','实验方法与报告规范_v2.md']:
    copy(ROOT/'outputs'/name,OUT/'documents'/name)

sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
audit=[]
for name in ['package_smoke_run','development_run','holdout_run','risk_forecast_followup_run','rank2_n100_refined_run']:
    p=OUT/name;s=json.loads((p/'status.json').read_text());cfg=json.loads((p/'protocol.json').read_text())
    assert s['complete'] is True
    assert sha(p/'protocol.json')==(p/'protocol.sha256').read_text().strip()
    for file,digest in json.loads((p/'source_hashes.json').read_text()).items():
        assert sha(p/'source_snapshot'/file)==digest
        assert sha(OUT/file)==digest
    backend=p/'backend_execution_freeze.json'
    if backend.exists():
        b=json.loads(backend.read_text())
        for file,digest in b['source_hashes'].items():
            assert sha(p/'backend_source_snapshot'/file)==digest
            assert sha(OUT/file)==digest
    with (p/'results.csv').open() as f:
        rows=list(csv.DictReader(f))
    assert len(rows)==s['evaluated_rows']
    assert sorted(set(int(r['network_id']) for r in rows))==sorted(cfg['network_ids'])
    audit.append(dict(run=name,networks=len(cfg['network_ids']),rows=len(rows),
                      actual_optimizer_calls=s['actual_optimizer_calls'],complete=True,
                      protocol_sha256=sha(p/'protocol.json'),results_sha256=sha(p/'results.csv'),
                      source_snapshot_verified=True))
(OUT/'package_integrity.json').write_text(json.dumps(dict(runs=audit,scope='simulation only; no external submission',
    statement='file and count integrity is not scientific validity certification'),indent=2)+'\n')

manifest={str(p.relative_to(OUT)):sha(p) for p in sorted(OUT.rglob('*'))
          if p.is_file() and p.name!='SHA256SUMS.json'}
(OUT/'SHA256SUMS.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+'\n')
zip_path=ROOT/'outputs/研究资料与实验包_v2.zip'
with zipfile.ZipFile(zip_path,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
    for p in sorted(OUT.rglob('*')):
        if p.is_file():z.write(p,Path('research_v2')/p.relative_to(OUT))
with zipfile.ZipFile(zip_path) as z:assert z.testzip() is None
(ROOT/'outputs/研究资料与实验包_v2.sha256').write_text(sha(zip_path)+'  '+zip_path.name+'\n')
print(json.dumps(dict(files=len(manifest),zip_bytes=zip_path.stat().st_size,runs=audit),indent=2))
