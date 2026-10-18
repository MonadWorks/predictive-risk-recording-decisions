"""Read-only delivery checks, using the Python standard library only.

Checks file integrity and selected presentation contracts, not scientific
novelty, biological validity, author consent or conference acceptance.
"""
from pathlib import Path
import csv,hashlib,json,math,re

ROOT=Path(__file__).resolve().parent
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def rows(path):
    with path.open(newline='') as f:return list(csv.DictReader(f))

def main():
    manifest=json.loads((ROOT/'SHA256SUMS.json').read_text())
    for name,expected in manifest.items():
        assert (ROOT/name).is_file() and digest(ROOT/name)==expected,name
    origins=json.loads((ROOT/'source_data/origin_manifest.json').read_text())
    for name,record in origins.items():assert digest(ROOT/'source_data'/name)==record['sha256'],name
    meta=json.loads((ROOT/'submission/submission_metadata.json').read_text())
    abstract=(ROOT/'submission/abstract_body.txt').read_text().strip()
    words=len(abstract.split());conservative=len(re.findall(r"\b[\w]+(?:[’'][\w]+)*\b",abstract))
    assert max(words,conservative)<=500 and len(abstract)<=5000
    assert len(meta['title'].split())<=15
    keys=meta['keywords'];assert 2<=len(keys.split(';'))<=5 and len(keys)<=125
    assert meta['funding']=='None' and meta['conflicts_of_interest']=='None'
    assert meta['authors'][0]['email']=='jiayi.du@mail.louisenlund.de'
    assert meta['authors'][1]['institutional_affiliation']=='Department of Computing, Harbin Institute of Technology'
    assert all(a['equal_contribution'] for a in meta['authors'])
    assert meta['coauthor_submission_approval_verified'] is None and meta['submission_id'] is None
    ga=ROOT/'submission'/meta['graphical_abstract_file']
    assert ga.suffix=='.pdf' and 0<ga.stat().st_size<10_000_000
    paper=(ROOT/'paper/论文研究稿_v3.md').read_text()
    assert paper.splitlines()[0]=='# '+meta['title'] and abstract in paper
    body,refs=paper.split('## References',1)
    cited={int(n) for group in re.findall(r'\[(\d+(?:,\d+)*)\]',body) for n in group.split(',')}
    listed={int(n) for n in re.findall(r'^(\d+)\. ',refs,re.M)}
    assert cited==listed==set(range(1,18))
    main_effects=rows(ROOT/'source_data/holdout_paired_effects.csv')
    for displayed in rows(ROOT/'figures/fig2_effects.csv'):
        original=next(r for r in main_effects if all(r[k]==displayed[k] for k in ['condition','pool','budget','contrast','metric']))
        assert displayed==original
    pairs=rows(ROOT/'figures/fig2_network_pairs.csv');assert len(pairs)==80
    for objective in ['Single response','Three responses']:
        own=[r for r in pairs if r['objective']==objective]
        assert len(own)==40 and len({r['network_id'] for r in own})==40
        for r in own:
            expected=math.log2(float(r['ensemble_mse'])/float(r['nominal_mse']))
            assert math.isclose(expected,float(r['descriptive_log2_ratio']),rel_tol=1e-11,abs_tol=1e-14)
    forecasts=rows(ROOT/'figures/fig3_networks.csv');assert len(forecasts)==40
    expected=json.loads((ROOT/'source_data/forecast_summary.json').read_text())['primary']
    assert math.isclose(sum(float(r['score_difference']) for r in forecasts)/40,expected['score_difference'],rel_tol=1e-12)
    agreement=rows(ROOT/'source_data/holdout_design_agreement.csv')
    for objective,total,same in [('single_response',120,82),('three_responses',40,26)]:
        own=[r for r in agreement if r['objective']==objective]
        assert len(own)==total and len({r['network_id'] for r in own})==40
        assert sum(r['identical']=='True' for r in own)==same
        assert all((r['nominal_nodes']==r['ensemble_nodes'])==(r['identical']=='True') for r in own)
    figures=json.loads((ROOT/'figures/figure_manifest.json').read_text())['figures'];assert len(figures)==9
    for name,record in figures.items():
        for ext,expected_hash in record['output_sha256'].items():
            assert digest(ROOT/'figures'/f'{name}.{ext}')==expected_hash
    print(json.dumps(dict(status='PASS',manifest_files=len(manifest),article_references=len(listed),
        main_and_supplementary_figures=len(figures),abstract_words=words,conservative_words=conservative,
        abstract_characters=len(abstract),graphical_abstract_bytes=ga.stat().st_size,
        scientific_validity='not certified by presentation or integrity checks',submitted=False),indent=2))

if __name__=='__main__':main()
