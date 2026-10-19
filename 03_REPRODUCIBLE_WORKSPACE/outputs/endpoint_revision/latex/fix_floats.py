#!/usr/bin/env python3
"""Single-column adaptation of the neutral float markup produced by ../common/md2tex.py.
figure*/table* -> figure/table (starred floats only reach page tops in one column);
captioned floats get [!tbp]; uncaptioned (notation/design) tables are typeset in place (no float);
appendix figures are pinned with [H]."""
import re, sys
pat = re.compile(r'\\begin\{(figure|table)\*\}(\[[^\]]*\])?(.*?)\\end\{\1\*\}', re.S)
for path, pin_all in (('build/body.tex', False), ('build/appendix.tex', True)):
    try: s = open(path, encoding='utf-8').read()
    except FileNotFoundError: continue
    def sub(m):
        kind, body = m.group(1), m.group(3)
        if kind == 'table' and '\\caption' not in body:   # uncaptioned data table: typeset in place
            return '\\begin{center}\n' + body + '\\end{center}'
        pin = pin_all
        return '\\begin{%s}%s%s\\end{%s}' % (kind, '[H]' if pin else '[!tbp]', body, kind)
    open(path, 'w', encoding='utf-8').write(pat.sub(sub, s))

# Local table typography: give long header words enough width rather than
# accepting the inherited overfull boxes. No numerical contents are changed.
p='build/body.tex'
s=open(p,encoding='utf-8').read()
for marker,weights in [('Stage & Independent J & Physiological truths/J',[.20,.16,.18,.16,.12,.18]),('Stage & Independent J & Truth × noise × readouts per J',[.24,.15,.17,.16,.14,.14])]:
    at=s.find(marker)
    if at<0:continue
    begin=s.rfind('\\setlength{\\tblw}',0,at)
    tab=s.index('\\begin{tabular}',begin)
    end=s.index('\n',tab)
    cols=''.join('>{\\raggedright\\arraybackslash}p{%.4f\\tblw}'%w for w in weights)
    s=s[:begin]+'\\setlength{\\tabcolsep}{4pt}\n'+s[begin:tab]+'\\begin{tabular}{'+cols+'}'+s[end:]
open(p,'w',encoding='utf-8').write(s)

# Keep the added supplementary analysis together and outside main-text numbering.
p='build/appendix.tex'
s=open(p,encoding='utf-8').read()
s=s.replace(r'\subsection{Additional indirect-recording comparison}',
            r'\clearpage'+'\n'+r'\subsection*{Additional indirect-recording comparison}')
open(p,'w',encoding='utf-8').write(s)

# The inherited Markdown preprocessor escapes literal carets outside its
# bracket-delimited display syntax. Restore TeX exponents inside math only,
# and remove paragraph breaks from display equations.
for p in ['build/body.tex','build/appendix.tex','build/abstract.tex']:
    s=open(p,encoding='utf-8').read()
    s=re.sub(r'\\\((.*?)\\\)',lambda m:m.group(0).replace(r'\^','^'),s,flags=re.S)
    def clean_equation(m):
        body=re.sub(r'\n\s*\n','\n',m.group(1).strip()).replace(r'\^','^')
        return '\\begin{equation}\n'+body+'\n\\end{equation}'
    s=re.sub(r'\\begin\{equation\}(.*?)\\end\{equation\}',clean_equation,s,flags=re.S)
    open(p,'w',encoding='utf-8').write(s)

p='build/appendix.tex'
s=open(p,encoding='utf-8').read()
for title in ['Limited-budget recording comparison','Static combination controls']:
    s=s.replace('\\subsection{'+title+'}','\\clearpage\n\\subsection*{'+title+'}')
open(p,'w',encoding='utf-8').write(s)
