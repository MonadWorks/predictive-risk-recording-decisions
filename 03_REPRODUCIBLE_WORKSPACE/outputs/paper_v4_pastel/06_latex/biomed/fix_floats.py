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
