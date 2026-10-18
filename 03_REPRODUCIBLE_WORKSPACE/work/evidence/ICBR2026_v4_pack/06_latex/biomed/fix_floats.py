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
