"""Wrapper for optional refined rank-two execution; never invoked on import."""
import argparse,hashlib,json,shutil
from pathlib import Path
from datetime import datetime,timezone
import run
from rank2_refined import refined_case

def execute(protocol,out,substeps):
    cfg=json.loads(protocol.read_text())
    if cfg['family']!='rank2_tanh':raise ValueError('rank2 protocol required')
    if out.exists() and any(out.iterdir()):raise RuntimeError('fresh nonempty-free output directory required')
    out.mkdir(parents=True,exist_ok=True)
    root=Path(__file__).parent
    names=['models.py','design.py','inference.py','run.py','rank2_refined.py','run_rank2.py']
    hashes={n:hashlib.sha256((root/n).read_bytes()).hexdigest() for n in names}
    # Saved before running: includes auxiliary backend and wrapper, independent of core receipt.
    snapshot=out/'backend_source_snapshot';snapshot.mkdir()
    for n in names:shutil.copy2(root/n,snapshot/n)
    receipt=dict(backend='rank2 exact reduced state / RK4 stages / analytic ZOH input filter',
       substeps=substeps,timestamp_utc=datetime.now(timezone.utc).isoformat(),source_hashes=hashes,
       protocol_sha256=hashlib.sha256(protocol.read_bytes()).hexdigest(),
       response_integral='RK4 quadrature for all N output rows and all raw-gain derivatives')
    (out/'backend_execution_freeze.json').write_text(json.dumps(receipt,indent=2)+'\n')
    run.public_case=lambda network_id,cfg,condition:refined_case(network_id,cfg,condition,substeps)
    run.execute(protocol,out)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--protocol',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    p.add_argument('--substeps',type=int,choices=[1,2,4,8],required=True);a=p.parse_args()
    execute(a.protocol,a.out,a.substeps)
