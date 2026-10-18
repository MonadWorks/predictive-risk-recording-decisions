"""Recompute reported statistics and figures from the retained simulation records."""
from pathlib import Path
import subprocess,sys
ROOT=Path(__file__).resolve().parent
STEPS=[
 ['code/analyze_supplement.py','confirmation'],
 ['code/analyze_supplement.py','mechanism'],
 ['round2/code/analyze.py'],['round2/code/validation_analysis.py'],
 ['round2/code/mechanism_summary.py'],['round2/code/figures.py'],
 ['round3/code/final_audit.py'],
 ['round3/code/analyze.py','profiles'],['round3/code/analyze.py','methods'],['round3/code/analyze.py','oracle'],
 ['round3/code/method_fit_audit.py'],['round3/code/figures.py'],['validate.py']]
if __name__=='__main__':
    for args in STEPS:
        print('Running '+args[0],flush=True)
        subprocess.run([sys.executable,str(ROOT/args[0]),*args[1:]],cwd=ROOT,check=True)
