#!/usr/bin/env python3
"""Template-independent Markdown -> LaTeX fragment converter.

Reads the manuscript Markdown (source of truth), splits it into logical parts
and writes template-neutral LaTeX fragments into --outdir.  A template
(06_latex/<template>/main.tex) only has to \\input these fragments.
See 06_latex/common/README.md for the full interface.
"""
import argparse
import os
import re
import struct
import subprocess
import sys

SUP = {'⁰': '0', '¹': '1', '²': '2', '³': '3', '⁴': '4', '⁵': '5', '⁶': '6',
       '⁷': '7', '⁸': '8', '⁹': '9', '⁻': '−', '⁺': '+', 'ᵀ': 'T', 'ⁿ': 'n'}
SUB = {'₀': '0', '₁': '1', '₂': '2', '₃': '3', '₄': '4', '₅': '5', '₆': '6',
       '₇': '7', '₈': '8', '₉': '9', '₊': '+', '₋': '−', 'ₐ': 'a', 'ₑ': 'e',
       'ₒ': 'o', 'ₓ': 'x', 'ₕ': 'h', 'ₖ': 'k', 'ₗ': 'l', 'ₘ': 'm', 'ₙ': 'n',
       'ₚ': 'p', 'ₛ': 's', 'ₜ': 't', 'ᵢ': 'i', 'ⱼ': 'j'}
SUP_RE = re.compile('[' + ''.join(SUP) + ']+')
SUB_RE = re.compile('[' + ''.join(SUB) + ']+')
MARKCHARS = '¹²³⁴⁵⁶⁷⁸⁹*†‡§'


def warn(msg):
    print('md2tex: WARNING: ' + msg, file=sys.stderr)


def run_pandoc(args, text):
    r = subprocess.run(args, input=text, capture_output=True, text=True)
    if r.stderr.strip():
        sys.stderr.write(r.stderr)
    if r.returncode != 0:
        sys.exit('md2tex: pandoc failed: ' + ' '.join(args))
    return r.stdout


# ---------------------------------------------------------------- parsing --
def strip_comments(t):
    return re.sub(r'<!--.*?-->[ \t]*\n?', '', t, flags=re.S)


def split_document(t):
    """-> (title, header_paras, [(section_name, text)])"""
    lines = t.split('\n')
    title, i = '', 0
    while i < len(lines) and not lines[i].startswith('# '):
        i += 1
    if i < len(lines):
        title = lines[i][2:].strip()
        i += 1
    head, sections, cur, name = [], [], [], None
    in_code = False
    for ln in lines[i:]:
        if ln.startswith('```'):
            in_code = not in_code
        if not in_code and re.match(r'^## (?!#)', ln):
            if name is None:
                head = cur
            else:
                sections.append((name, '\n'.join(cur)))
            name, cur = ln[3:].strip(), []
        else:
            cur.append(ln)
    if name is None:
        head = cur
    else:
        sections.append((name, '\n'.join(cur)))
    paras = [p.strip() for p in re.split(r'\n\s*\n', '\n'.join(head)) if p.strip()]
    return title, paras, sections


def parse_refs(text):
    refs = {}
    for ln in text.split('\n'):
        m = re.match(r'^\s*(\d+)\.\s+(.*\S)\s*$', ln)
        if m:
            refs[int(m.group(1))] = m.group(2)
    return refs


# --------------------------------------------------------------- bibliography --
def _initials(tok):
    return ' '.join(c + '.' for c in tok if c.isalpha())


def _authors(s):
    s = s.strip().rstrip('.')
    others = False
    if re.search(r'\bet al$', s):
        s = re.sub(r',?\s*\bet al$', '', s).strip()
        others = True
    out = []
    for a in [x.strip() for x in s.split(',') if x.strip()]:
        parts = a.split()
        if len(parts) >= 2 and re.fullmatch(r'[A-Z]{1,4}', parts[-1]):
            out.append('%s, %s' % (' '.join(parts[:-1]), _initials(parts[-1])))
        else:
            out.append(a)
    if others:
        out.append('others')
    return ' and '.join(out)


def bib_escape(s):
    return s.replace('&', r'\&').replace('%', r'\%').replace('_', r'\_').replace('#', r'\#')


def placeholder_bib(refs):
    ents = []
    for n in sorted(refs):
        raw = refs[n]
        doi = ''
        m = re.search(r'\[[^\]]*\]\((https?://[^)]+)\)', raw)
        if m:
            doi = m.group(1)
            raw = raw.replace(m.group(0), '')
        raw = re.sub(r'\s+', ' ', raw).strip()
        authors = ''
        m = re.search(r'^(.*?(?:\b[A-Z]{1,4}|\bal))\.\s+(?=\S)', raw)
        rest = raw
        if m and len(m.group(1)) < 200:
            authors = _authors(m.group(1))
            rest = raw[m.end():]
        jm = re.search(r'\*([^*]+)\*', rest)
        fields = []
        if authors:
            fields.append(('author', authors))
        key = 'ref%02d' % n
        if jm:
            title = rest[:jm.start()].strip().rstrip('.')
            tail = rest[jm.end():].strip().strip('.').strip()
            fields.append(('title', title))
            fields.append(('journal', jm.group(1)))
            ym = re.search(r'\((\d{4})\)', tail)
            if ym:
                fields.append(('year', ym.group(1)))
                tail = tail.replace(ym.group(0), '').strip()
            vm = re.match(r'^[,\s]*(\d+)(?:\((\d+)\))?[,:\s]*([\w\u2013\-]+)?', tail)
            if vm and not tail.lstrip(', ').startswith(('formal', 'reviewed')):
                fields.append(('volume', vm.group(1)))
                if vm.group(2):
                    fields.append(('number', vm.group(2)))
                if vm.group(3):
                    fields.append(('pages', vm.group(3).replace('\u2013', '--')))
            elif tail.strip(', '):
                fields.append(('note', tail.strip(', ')))
            etype = 'article'
        else:
            title = rest.strip().rstrip('.')
            fields.append(('title', title))
            etype = 'misc'
        if doi:
            fields.append(('url', doi))
        body = ',\n'.join('  %s = {%s}' % (k, bib_escape(v) if k != 'url' else v) for k, v in fields)
        ents.append('@%s{%s,\n%s\n}' % (etype, key, body))
    return '% PLACEHOLDER generated from the Markdown reference list - replaced by the real .bib when present.\n' + '\n\n'.join(ents) + '\n'


# ------------------------------------------------------------------ images --
def png_width_in(path):
    try:
        with open(path, 'rb') as f:
            d = f.read(4096)
        w = struct.unpack('>I', d[16:20])[0]
        dpi = 300.0
        i = d.find(b'pHYs')
        if i > 0:
            ppu = struct.unpack('>I', d[i + 4:i + 8])[0]
            if d[i + 12] == 1 and ppu:
                dpi = ppu * 0.0254
        return w / dpi
    except Exception:
        return None


def resolve_image(md_dir, rel, prefer_v4=True):
    base = os.path.normpath(os.path.join(md_dir, rel))
    d, fn = os.path.split(base)
    stem, ext = os.path.splitext(fn)
    cands = []
    if prefer_v4:
        vstem = stem if stem.endswith('_v4') else stem + '_v4'
        vdir = d if d.endswith('_v4') else d + '_v4'
        cands += [os.path.join(d, vstem + ext), os.path.join(vdir, fn),
                  os.path.join(vdir, vstem + ext)]
    cands.append(base)
    pick = next((c for c in cands if os.path.exists(c)), None)
    if pick is None:
        sys.exit('md2tex: image not found: %s' % base)
    s, e = os.path.splitext(pick)
    pdf = s + '.pdf'
    png = pick if e == '.png' else None
    if os.path.exists(pdf) and (png is None or os.path.getmtime(pdf) >= os.path.getmtime(png) - 120):
        pick_out = pdf
    else:
        pick_out = pick
    w = png_width_in(png) if png else (png_width_in(s + '.png') if os.path.exists(s + '.png') else None)
    return pick_out, w


# --------------------------------------------------------- markdown rewrite --
MATH_RE = re.compile(r'^[ \t]*\\\[(.*?)\\\][ \t]*$', re.S | re.M)


def cite_repl(nrefs):
    width = max(2, len(str(nrefs or 99)))

    def keys(spec):
        ns = []
        for part in re.split(r'\s*,\s*', spec):
            m = re.fullmatch(r'(\d+)\s*[–-]\s*(\d+)', part)
            if m:
                ns += list(range(int(m.group(1)), int(m.group(2)) + 1))
            else:
                ns.append(int(part))
        return ns

    def f(m):
        ns = keys(m.group(1))
        if not ns or min(ns) < 1 or (nrefs and max(ns) > nrefs):
            return m.group(0)
        ks = ','.join('ref%0*d' % (width, n) for n in ns)
        return '`\\cite{%s}`{=latex}' % ks
    return f


CITE_RE = re.compile(r'(?<![!\w])\[(\d{1,3}(?:\s*[–-]\s*\d{1,3})?(?:\s*,\s*\d{1,3}(?:\s*[–-]\s*\d{1,3})?)*)\](?!\()')


def prep_text(seg, nrefs):
    seg = re.sub(r'(?<!\\)([~^])', r'\\\1', seg)
    seg = CITE_RE.sub(cite_repl(nrefs), seg)
    seg = SUP_RE.sub(lambda m: '^' + ''.join(SUP[c] for c in m.group(0)) + '^', seg)
    seg = SUB_RE.sub(lambda m: '~' + ''.join(SUB[c] for c in m.group(0)) + '~', seg)
    return seg


def prep_markdown(text, md_dir, workdir, nrefs, stats):
    # display math \[ ... \] -> $$ ... $$ (own paragraph); everything else processed
    out, pos = [], 0
    for m in MATH_RE.finditer(text):
        out.append(prep_text(text[pos:m.start()], nrefs))
        out.append('\n$$' + m.group(1).strip() + '$$\n')
        pos = m.end()
        stats['equations'] += 1
    out.append(prep_text(text[pos:], nrefs))
    text = ''.join(out)

    def img(m):
        alt, src, attr = m.group(1), m.group(2), m.group(3) or ''
        path, w = resolve_image(md_dir, src.replace('\\', ''))
        rel = os.path.relpath(path, workdir)
        wide = (w is None) or w > 4.2
        stats['images'].append((src, os.path.relpath(path, md_dir), w))
        cls = '.wide' if wide else '.narrow'
        return '![%s](%s){%s}' % (alt, rel, cls)
    text = re.sub(r'!\[([^\]]*)\]\(([^)\s]+)\)(\{[^}]*\})?', img, text)
    return text


# ------------------------------------------------------------------ header --
def inline_tex(md, pandoc, extra=()):
    s = run_pandoc([pandoc, '-f', 'markdown-smart', '-t', 'latex', '--wrap=none'] + list(extra), md)
    return s.strip()


def parse_authors(line):
    line = line.strip()
    names = re.split(r',\s*(?:and\s+)?|\s+and\s+', line)
    out = []
    for n in names:
        n = n.strip()
        if not n:
            continue
        m = re.match(r'^(.*?)([%s]*)$' % re.escape(MARKCHARS), n)
        name, marks = m.group(1).strip(), m.group(2)
        out.append((name, marks))
    return out


def marks_tex(marks):
    toks = []
    for c in marks:
        toks.append(SUP.get(c, c))
    # merge consecutive digits as separate marks only if distinct symbols
    return ','.join(toks)


def build_meta(title, paras, pandoc, flags):
    authors_tex, affils, notes, manuscript = '', [], [], ''
    authors = []
    for p in paras:
        flat = p.replace('\n', ' ')
        if re.match(r'^\*[^\s*]', flat) and flat.rstrip().endswith('*'):
            manuscript = flat.strip().strip('*')
        elif re.match(r'^[¹²³⁴⁵⁶⁷⁸⁹]', flat):
            parts = re.split(r'([¹²³⁴⁵⁶⁷⁸⁹]+)\s*', flat)
            for i in range(1, len(parts) - 1, 2):
                affils.append((''.join(SUP[c] for c in parts[i]), parts[i + 1].strip().rstrip('.')))
        elif re.match(r'^[†‡§]|^\*\s', flat):
            notes.append(flat)
        elif not authors:
            authors = parse_authors(flat)
    names = []
    for name, marks in authors:
        t = inline_tex(name, pandoc)
        if marks:
            t += '\\textsuperscript{%s}' % marks_tex(marks)
        names.append(t)
    if len(names) > 1:
        authors_tex = ', '.join(names[:-1]) + (',' if len(names) > 2 else '') + ' and ' + names[-1]
    else:
        authors_tex = ''.join(names)
    aff_tex = ' \\\\\n'.join('\\textsuperscript{%s}%s' % (n, inline_tex(t, pandoc)) for n, t in affils)
    notes_tex = '\\par '.join(inline_tex(re.sub(r'^\*\s', r'\\* ', n), pandoc) for n in notes)
    notes_tex = notes_tex.replace('\\textasteriskcentered{}', '\\textsuperscript{*}')
    notes_tex = re.sub(r'^(?:\\\*|\*)\s*', '\\\\textsuperscript{*}', notes_tex)
    notes_tex = notes_tex.replace('†', '\\textsuperscript{†}')
    man = inline_tex(manuscript, pandoc) if manuscript else ''
    lines = ['% generated by md2tex.py - do not edit',
             '\\newcommand{\\PaperTitle}{%s}' % inline_tex(title, pandoc),
             '\\newcommand{\\PaperAuthors}{%s}' % authors_tex,
             '\\newcommand{\\PaperAffiliations}{%s}' % aff_tex,
             '\\newcommand{\\PaperAuthorNotes}{%s}' % notes_tex,
             '\\newcommand{\\PaperManuscriptNote}{%s}' % man]
    for k, v in flags.items():
        lines.append('\\newif\\ifpaper%s' % k)
        if v:
            lines.append('\\paper%strue' % k)
    return '\n'.join(lines) + '\n'


# -------------------------------------------------------------------- main --
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--md', required=True)
    ap.add_argument('--outdir', required=True)
    ap.add_argument('--workdir', default='.', help='directory LaTeX runs in (image paths are made relative to it)')
    ap.add_argument('--lua', required=True)
    ap.add_argument('--bib-real', default='')
    ap.add_argument('--pandoc', default='pandoc')
    ap.add_argument('--no-prefer-v4', action='store_true')
    a = ap.parse_args()

    os.makedirs(a.outdir, exist_ok=True)
    md_dir = os.path.dirname(os.path.abspath(a.md))
    workdir = os.path.abspath(a.workdir)
    text = strip_comments(open(a.md, encoding='utf-8').read())
    title, hparas, sections = split_document(text)

    parts = {'body': [], 'abstract': '', 'keypoints': '', 'keywords': '', 'appendix': ''}
    refs = {}
    for name, sec in sections:
        key = re.sub(r'^\d+[\.\s]+', '', name).strip().lower()
        if key == 'abstract':
            parts['abstract'] = sec
        elif key in ('key points', 'highlights'):
            parts['keypoints'] = sec
        elif key in ('keywords', 'index terms'):
            parts['keywords'] = sec
        elif key in ('contents', 'table of contents'):
            pass
        elif key in ('references', 'bibliography'):
            refs = parse_refs(sec)
        elif key.startswith('supplementary'):
            parts['appendix'] += sec + '\n'
        else:
            parts['body'].append('## %s\n%s' % (name, sec))
    nrefs = max(refs) if refs else 0

    stats = {'equations': 0, 'images': []}
    base = [a.pandoc, '-f', 'markdown-implicit_figures-auto_identifiers', '-t', 'latex',
            '--wrap=none', '--lua-filter=' + os.path.abspath(a.lua)]

    def render(md, mode, shift):
        md = prep_markdown(md, md_dir, workdir, nrefs, stats)
        args = base + ['-M', 'mode=' + mode]
        if shift:
            args.append('--shift-heading-level-by=-1')
        return run_pandoc(args, md)

    written = {}
    written['abstract.tex'] = render(parts['abstract'], 'abstract', False) if parts['abstract'].strip() else ''
    written['keypoints.tex'] = render(parts['keypoints'], 'keypoints', False) if parts['keypoints'].strip() else ''
    written['keywords.tex'] = render(parts['keywords'], 'keywords', False).strip().replace('\n', ' ') + '\n' if parts['keywords'].strip() else ''
    written['body.tex'] = render('\n\n'.join(parts['body']), 'body', True)
    written['appendix.tex'] = render(parts['appendix'], 'appendix', True) if parts['appendix'].strip() else ''
    flags = {'appendix': bool(written['appendix.tex'].strip()),
             'keypoints': bool(written['keypoints.tex'].strip()),
             'keywords': bool(written['keywords.tex'].strip()),
             'abstract': bool(written['abstract.tex'].strip())}
    written['meta.tex'] = build_meta(title, hparas, a.pandoc, flags)
    for fn, s in written.items():
        with open(os.path.join(a.outdir, fn), 'w', encoding='utf-8') as f:
            f.write(s)

    # bibliography: real file preferred, placeholder otherwise
    bib_out = os.path.join(a.outdir, 'references.bib')
    cited = set(int(n) for ks in re.findall(r'\\cite\{([^}]*)\}', written['body.tex'] + written['abstract.tex'] + written['appendix.tex'])
                for n in re.findall(r'\d+', ks))
    if a.bib_real and os.path.exists(a.bib_real):
        content = open(a.bib_real, encoding='utf-8').read()
        src = 'real (%s)' % a.bib_real
        have = set(int(n) for n in re.findall(r'@\w+\s*\{\s*ref(\d+)\s*,', content))
        miss = sorted(cited - have)
        if miss:
            warn('cited but missing in real .bib: ' + ', '.join('ref%02d' % n for n in miss))
    else:
        content = placeholder_bib(refs)
        src = 'PLACEHOLDER (generated from Markdown reference list)'
    with open(bib_out, 'w', encoding='utf-8') as f:
        f.write(content)
    uncited = sorted(set(refs) - cited)
    if uncited:
        warn('references in Markdown list never cited in text: %s' % uncited)
    print('md2tex: bibliography = %s; %d refs, %d cited; %d equations; %d images' %
          (src, len(refs), len(cited), stats['equations'], len(stats['images'])))
    for s, p, w in stats['images']:
        print('md2tex:   image %s -> %s (%.2f in wide)' % (s, p, w or -1))


if __name__ == '__main__':
    main()
