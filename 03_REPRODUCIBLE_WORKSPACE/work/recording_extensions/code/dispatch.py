"""Run independent protocol shards with bounded CPU concurrency."""
import argparse
import concurrent.futures
import json
import os
from pathlib import Path
import subprocess
import sys
import time


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('group', choices=['confirmation', 'mechanism'])
    parser.add_argument('--workers', type=int, default=4)
    parser.add_argument('--adopt-existing', action='store_true')
    args = parser.parse_args()
    root = Path(__file__).resolve().parent.parent
    protocols = sorted((root/'protocols').glob(args.group+'_shard_*.json'))
    if not protocols:
        raise RuntimeError('no protocols')
    (root/'logs').mkdir(exist_ok=True)
    start = time.time()
    env = os.environ.copy()
    env.update(OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', VECLIB_MAXIMUM_THREADS='1',
               NUMBA_CACHE_DIR=str(root/'scratch/numba'))

    def launch(protocol):
        stem = protocol.stem
        out = root/'runs'/stem
        if out.exists():
            status_file = out/'status.json'
            if status_file.exists() and json.loads(status_file.read_text()).get('complete'):
                return dict(shard=stem, returncode=0, already_complete=True)
            if args.adopt_existing:
                processes=subprocess.check_output(['ps','-axo','pid,command'], text=True)
                found=[int(line.strip().split(None,1)[0]) for line in processes.splitlines()
                       if f'--protocol {protocol}' in line and 'run_mechanism.py' in line]
                if len(found)!=1:
                    raise RuntimeError(f'expected one active worker for {stem}, found {found}')
                pid=found[0]
                while True:
                    if status_file.exists():
                        try: state=json.loads(status_file.read_text())
                        except json.JSONDecodeError:state={}
                        if state.get('complete'):
                            return dict(shard=stem,returncode=0,adopted_pid=pid)
                    try:os.kill(pid,0)
                    except ProcessLookupError:
                        raise RuntimeError(f'adopted worker {pid} exited before completion')
                    time.sleep(5)
            raise RuntimeError(f'incomplete output needs explicit recovery: {out}')
        script = 'run_rank2.py' if args.group == 'confirmation' else 'run_mechanism.py'
        cmd = [sys.executable, str(root/'code'/script), '--protocol', str(protocol), '--out', str(out)]
        if args.group == 'confirmation':
            cmd += ['--substeps', '2']
        with (root/'logs'/(stem+'.log')).open('w') as log:
            result = subprocess.run(cmd, stdout=log, stderr=subprocess.STDOUT, env=env)
        return dict(shard=stem, returncode=result.returncode)

    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = [executor.submit(launch, protocol) for protocol in protocols]
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            results.append(result)
            print(json.dumps(result), flush=True)
            (root/'logs'/(args.group+'_dispatch.json')).write_text(json.dumps(
                dict(elapsed_seconds=time.time()-start, shards=results,
                     complete=len(results)==len(protocols), workers=args.workers), indent=2))
    if any(r['returncode'] for r in results):
        raise RuntimeError('at least one shard failed; inspect retained logs')


if __name__ == '__main__':
    main()
