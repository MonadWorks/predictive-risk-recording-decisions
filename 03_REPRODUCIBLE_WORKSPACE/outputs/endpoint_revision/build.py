"""Build the manuscript with the repository's existing Springer template."""
from pathlib import Path
import os,subprocess,sys,shutil
HERE=Path(__file__).resolve().parent
TEMPLATE=HERE.parent/'paper_v4_pastel/06_latex'
WORK=HERE/'latex'
def call(args):subprocess.run([str(x) for x in args],cwd=WORK,env=env,check=True)
if __name__=='__main__':
    (WORK/'build').mkdir(exist_ok=True)
    env=os.environ.copy();env['PATH']='/Library/TeX/texbin:/opt/homebrew/bin:'+env['PATH']
    env['TEXINPUTS']=str(TEMPLATE/'common')+':'+str(TEMPLATE/'biomed/sn-template')+':'+env.get('TEXINPUTS','')+':'
    env['BSTINPUTS']=str(TEMPLATE/'biomed/sn-template')+':'+env.get('BSTINPUTS','')+':'
    (WORK/'build/clsopts.tex').write_text(r'\def\clsopts{pdflatex,sn-nature}'+'\n')
    call([sys.executable,TEMPLATE/'common/md2tex.py','--md',HERE/'paper.md','--outdir',WORK/'build','--workdir',WORK,'--lua',TEMPLATE/'common/filter.lua','--bib-real',HERE/'references.bib'])
    p=WORK/'build/references.bib';p.write_text(__import__('re').sub(r'(?m)^(\s*)note(\s*=)',r'\1xnote\2',p.read_text()))
    call([sys.executable,WORK/'fix_floats.py'])
    call(['latexmk','-g','-pdf','-interaction=nonstopmode','-halt-on-error','-file-line-error','-outdir=build','main.tex'])
    shutil.copy2(WORK/'build/main.pdf',HERE/'paper.pdf')
