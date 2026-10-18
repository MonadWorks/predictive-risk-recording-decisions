"""Re-derive every headline number in paper_v4.md / the abstract from the bundled frozen tables.

Run from anywhere:  python validate_pack.py        (standard library only)
Exit code 0 = all checks pass. It does not re-fit anything and adds no statistics.
"""
import csv, json, sys
from pathlib import Path

D = Path(__file__).resolve().parent / '05_data_and_code/source_data'
fails = []


def check(name, got, want, tol=0):
    ok = abs(got - want) <= tol
    print(('PASS ' if ok else 'FAIL ') + f'{name}: got {got}, expected {want}')
    if not ok: fails.append(name)


rows = lambda n: list(csv.DictReader((D / n).open()))

agree = rows('holdout_design_agreement.csv')
s = [r for r in agree if r['objective'] == 'single_response']; v = [r for r in agree if r['objective'] == 'three_responses']
check('single-target designs', len(s), 120); check('single identical', sum(r['identical'] == 'True' for r in s), 82)
check('shared designs', len(v), 40); check('shared identical', sum(r['identical'] == 'True' for r in v), 26)

for r in rows('holdout_paired_effects.csv'):
    if r['primary'] == 'True' and r['metric'] == 'mse':
        key = 'scalar' if 'scalar' in r['contrast'] else 'vector'
        want = {'scalar': (-3.74, -18.48, 12.12), 'vector': (2.69, -2.95, 11.51)}[key]
        got = tuple(round(100 * float(r[k]), 2) for k in ('relative_mse_difference', 'relative_mse_ci_low', 'relative_mse_ci_high'))
        check(f'primary {key} relative MSE and 97.5% CI', 0 if got == want else 1, 0)
        check(f'primary {key} confidence level', float(r['confidence_level']), .975)
        check(f'primary {key} networks', int(r['networks']), 40)

pairs = rows('fig2_network_pairs.csv')
check('network-objective cells', len(pairs), 80)
check('exactly equal MSE cells', sum(float(r['descriptive_log2_ratio']) == 0 for r in pairs), 39)

f = json.loads((D / 'forecast_summary.json').read_text())['primary']
check('forecast score difference', round(f['score_difference'], 5), -.45565)
check('forecast CI low', round(f['score_difference_ci_low'], 5), -1.15857)
check('forecast CI high', round(f['score_difference_ci_high'], 5), .02367)
net = rows('fig3_networks.csv')
check('forecast networks', len(net), 40)
check('networks favouring ensemble', sum(float(r['score_difference']) < 0 for r in net), 19)
check('networks favouring nominal', sum(float(r['score_difference']) > 0 for r in net), 21)

ext = [r for r in rows('n100_paired_effects.csv') if r['metric'] == 'mse' and r['condition'] == 'published_gain'
       and r['contrast'] in ('ensemble_scalar - local_scalar', 'ensemble_vector - local_vector')]
check('extension settings', len(ext), 8)
below = sum(float(r['relative_mse_ci_high']) < 0 for r in ext); above = sum(float(r['relative_mse_ci_low']) > 0 for r in ext)
check('extension intervals excluding zero, favouring ensemble', below, 4)
check('extension intervals excluding zero, favouring nominal', above, 0)
check('extension independent networks', {int(r['networks']) for r in ext}.pop(), 8)

print('\nALL CHECKS PASSED' if not fails else f'\n{len(fails)} FAILED: {fails}')
sys.exit(1 if fails else 0)
