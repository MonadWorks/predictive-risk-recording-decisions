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
    # Accept an explicit supplementary-table label in the readable source while
    # retaining the inherited table renderer and the wrapper's S numbering.
    filter_path=WORK/'build/filter.lua'
    lua=(TEMPLATE/'common/filter.lua').read_text()
    lua=lua.replace("n = label:match('^Table%s*(%d+)%s*$')",
                    "n = label:match('^Table%s*(%d+)%s*$') or label:match('^Supplementary Table%s*(%d+)%s*$')")
    filter_path.write_text(lua)
    call([sys.executable,TEMPLATE/'common/md2tex.py','--md',HERE/'paper.md','--outdir',WORK/'build','--workdir',WORK,'--lua',filter_path,'--bib-real',HERE/'references.bib'])
    p=WORK/'build/references.bib';p.write_text(__import__('re').sub(r'(?m)^(\s*)note(\s*=)',r'\1xnote\2',p.read_text()))
    # The inherited sn-nature style underflows its stack for an editorless
    # proceedings entry. Render this proceedings series in article layout;
    # retain the canonical BibTeX type and all bibliographic facts upstream.
    import re
    bib=p.read_text()
    bib=re.sub(r'@inproceedings\{ref46,(.*?)\n\}',lambda m:'@article{ref46,'+m.group(1).replace('booktitle =','journal =')+'\n}',bib,flags=re.S)
    p.write_text(bib)
    call([sys.executable,WORK/'fix_floats.py'])
    call(['latexmk','-g','-pdf','-interaction=nonstopmode','-halt-on-error','-file-line-error','-outdir=build','main.tex'])
    shutil.copy2(WORK/'build/main.pdf',HERE/'paper.pdf')
