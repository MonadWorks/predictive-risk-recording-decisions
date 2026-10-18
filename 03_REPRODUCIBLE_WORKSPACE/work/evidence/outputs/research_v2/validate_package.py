"""Read-only delivery integrity audit; Python standard library only."""
from pathlib import Path
import csv,hashlib,json

def main():
    root=Path(__file__).resolve().parent
    digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    manifest=json.loads((root/'SHA256SUMS.json').read_text())
    errors=[]
    for relative,expected in manifest.items():
        p=root/relative
        if not p.is_file() or digest(p)!=expected:errors.append(relative)
    if errors:raise RuntimeError('Changed or missing delivery files: '+repr(errors))
    runs=json.loads((root/'package_integrity.json').read_text())['runs']
    for r in runs:
        p=root/r['run'];state=json.loads((p/'status.json').read_text())
        assert state['complete'] and digest(p/'protocol.json')==r['protocol_sha256']
        assert digest(p/'results.csv')==r['results_sha256']
        with (p/'results.csv').open() as f:
            rows=0;ids=set()
            for row in csv.DictReader(f):rows+=1;ids.add(int(row['network_id']))
        assert rows==r['rows'] and len(ids)==r['networks']
        assert state['actual_optimizer_calls']==r['actual_optimizer_calls']
        for name,h in json.loads((p/'source_hashes.json').read_text()).items():
            assert digest(p/'source_snapshot'/name)==h
        extra=p/'backend_execution_freeze.json'
        if extra.exists():
            for name,h in json.loads(extra.read_text())['source_hashes'].items():
                assert digest(p/'backend_source_snapshot'/name)==h
    print(json.dumps(dict(manifest_files=len(manifest),run_records=len(runs),integrity='PASS',
                          scientific_validity='not certified by file integrity'),indent=2))

if __name__=='__main__':main()
