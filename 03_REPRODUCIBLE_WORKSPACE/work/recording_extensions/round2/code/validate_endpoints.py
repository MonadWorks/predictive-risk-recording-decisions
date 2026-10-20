"""Independent validation of the same four fixed recording allocations."""
import json,time,sys
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor,as_completed
import explore

BASE=Path(__file__).resolve().parent.parent
# explore.ROOT stays the original research root. Only output destination changes.
explore.HERE=BASE/'validation'

def main():
    plan=json.loads((BASE/'validation/protocol.json').read_text())
    # Share resources with the first stage rather than creating a second full pool.
    while len(list((BASE/'runs/endpoint').glob('*.done.json')))<40:
        time.sleep(5)
    (explore.HERE/'runs/endpoint').mkdir(parents=True,exist_ok=True)
    with ProcessPoolExecutor(max_workers=4) as pool:
        futures=[pool.submit(explore.worker,n,'endpoint') for n in plan['network_ids']]
        for f in as_completed(futures):print(json.dumps(f.result()),flush=True)

if __name__=='__main__':main()
