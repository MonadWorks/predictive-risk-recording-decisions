"""Graphical abstract: the original v5 layout with the current manuscript's evidence.

The v5 renderer in ../graphical_abstract/source runs unchanged and its finished
figure is captured before saving. Title, network illustration, the three
numbered evidence frames, formula box and summary box keep their geometry,
palette and type; only the contents of the frames change. Values are read from
the analysis files and checked against the manuscript text.
"""
from pathlib import Path
import io, json, os, re, shutil, sys, tempfile
import numpy as np
import figure_style as fs
import matplotlib
import matplotlib.figure
from matplotlib.patches import Circle
from matplotlib.text import Text
from matplotlib.ticker import FixedLocator, FuncFormatter

HERE = Path(__file__).resolve().parent
GA = HERE.parent / 'graphical_abstract'
R = HERE.parents[1] / 'work/recording_extensions'
READ = HERE.parents[2] / '01_READ_CURRENT'
KEY = 'Record endpoints for prediction; target the remaining internal information.'
# v5 palette
INK, MUTED, ROSE, PLUM, FORECAST, GOLD, SAME = '#2E2531', '#655D69', '#CA799A', '#65566F', '#9C537C', '#D4A239', '#D6D0D5'
ROSE_TEXT, KEY_TEXT, GREY_NODE, GREY_EDGE = '#A34E79', '#984775', '#E3E8EC', '#B4BDC5'
PAPER_TEXT = (HERE / 'paper.md').read_text(encoding='utf-8')


def load(rel):
    return json.loads((R / rel).read_text(encoding='utf-8'))


def stat(c):
    if 'relative_change_percent' in c:
        return c['relative_change_percent'], *c['ci95_percent'], c['wins']
    return c['change_pct'], *c['ci95'], c['wins']


def mono(v, digits=1):
    return f'{v:+.{digits}f}'.replace('-', fs.MINUS)


def evidence():
    valid = load('round2/analysis/validation_summary.json')['comparisons']['both_vs_neither']
    width = load('round3/analysis/profile_summary.json')['comparisons']['both_vs_neither']['width2']
    factors = load('round4/analysis/mechanism_validation_summary.json')['component_comparisons']
    comb = load('round6/analysis/summary.json')['diagnostic_contrasts']['combination_mse/combination5_vs_random5']
    e = dict(valid=stat(valid), width=stat(width), comb=stat(comb),
             factors={k: stat(factors[k]) for k in ('input', 'recurrence', 'readout')})
    for v in [*e['valid'][:3], *e['width'][:3], *e['comb'][:3], *[x for f in e['factors'].values() for x in f[:3]]]:
        assert re.search(r'(?<![\d.])' + re.escape(f'{abs(v):.2f}') + r'(?!\d)', PAPER_TEXT), v
    return e


def capture():
    """Run the untouched v5 renderer and return its finished figure and save options."""
    state = {}
    original = matplotlib.figure.Figure.savefig

    def hold(fig, fname, *a, **kw):
        state.setdefault('fig', fig)
        state.setdefault('kw', dict(kw))

    scratch = Path(tempfile.mkdtemp(prefix='ga_v5_'))
    os.environ.setdefault('MPLCONFIGDIR', str(scratch / 'mpl'))
    src = GA / 'source/render_graphical_abstract.py'
    code = src.read_text(encoding='utf-8').replace("O=ROOT.parent/'rendered'", f'O=Path({str(scratch)!r})')
    matplotlib.figure.Figure.savefig = hold
    try:
        exec(compile(code, str(src), 'exec'), {'__file__': str(src), '__name__': '__main__'})
    finally:
        matplotlib.figure.Figure.savefig = original
    return state['fig'], state['kw'], original


def main():
    e = evidence()
    fig, kw, save = capture()
    base = fig.axes[0]
    texts = {t.get_text(): t for t in base.texts}

    def retext(old, new, **props):
        t = texts[old]
        t.set_text(new)
        for k, v in props.items():
            getattr(t, 'set_' + k)(v)
        return t

    def add(x, y, s, size=8.0, color=INK, weight='normal', family='BentonSans', **kw2):
        return base.text(x, y, s if family != 'BentonSans' else fs.dash(s), fontsize=size, color=color,
                         fontweight=weight, fontfamily=family, va='center', **kw2)

    # ---- network illustration: the stimulation site and readout are recorded.
    for p in base.patches:
        if isinstance(p, Circle) and p.get_zorder() == 3:
            c = tuple(np.round(p.center, 2))
            if c in [(30.0, 107.0), (46.45, 78.5)]:
                p.set_facecolor(ROSE)
            elif c in [(13.55, 78.5), (20.5, 104.45)]:
                p.set_radius(2.5); p.set_facecolor(GREY_NODE); p.set_edgecolor(GREY_EDGE); p.set_linewidth(.6)
    retext('12 simulated units · M=3', '100-unit networks · 5 recordings')
    retext('Uncertain gains and biases', 'Known connectivity; uncertain gains')
    retext('Response readout (one shown)', 'Response readout (one of three)')

    # ---- frame 1: endpoint recording.
    retext('Recording agreement', 'Endpoint recording')
    retext('40 independent networks', 'Five recordings per allocation')
    for p in [p for p in base.patches if isinstance(p, Circle) and p.radius < 1.0]:
        p.remove()
    for old in ['68%', '82 of 120 designs', '65%', '26 of 40 designs', 'Single-response designs',
                'Shared three-response designs', 'same recording set']:
        texts[old].remove()
    for t in [t for t in base.texts if t.get_text() == 'identical recording sets']:
        t.remove()
    xs = 60.08 + 2.345 * np.arange(15)

    def dots(rows, n_on, color):
        for k in range(40):
            row, col = divmod(k, 15)
            base.add_patch(Circle((xs[col], rows[row]), .78, facecolor=color if k < n_on else SAME,
                                  edgecolor='none', zorder=3))

    est, lo, hi, wins = e['valid']
    add(59.3, 95.6, 'Held-out response error', 8.3, ROSE_TEXT, 'bold')
    add(59.3, 90.4, f'{est:.0f}%', 16.0, ROSE, 'bold')
    add(72.5, 92.0, f'{wins} of 40 networks', 8.0)
    add(72.5, 89.2, 'improved', 8.0)
    dots([85.0, 82.95, 80.9], wins, ROSE)
    add(59.3, 76.6, 'Both ends vs neither, mean MSE', 7.2, MUTED)
    add(59.3, 73.6, f'{mono(est, 2)}% [{mono(lo, 2)}, {mono(hi, 2)}]', 7.2, INK, family='JuliaMono')
    est, lo, hi, wins = e['width']
    add(59.3, 66.0, 'Compatible response range', 8.3, PLUM, 'bold')
    add(59.3, 60.8, f'{est:.0f}%', 16.0, PLUM, 'bold')
    add(72.5, 62.4, f'{wins} of 40 networks', 8.0)
    add(72.5, 59.6, 'narrower', 8.0)
    dots([56.33, 54.28, 52.23], wins, PLUM)
    add(59.3, 43.2, 'One dot per network', 7.2, MUTED)

    # ---- frame 2: finite-response error factors.
    retext('Response error', 'Error factors')
    retext('Common MAP fit and budget', 'Endpoint vs ordinary recording')
    retext('Same 40 networks', 'Exact three-factor split')
    retext('97.5% paired network-cluster CI', '95% paired network-bootstrap CI')
    ax = fig.axes[1]
    for a in list(ax.lines) + list(ax.texts):
        a.remove()
    ax.set_xlim(-112, 150); ax.set_ylim(0, 36)
    rows = [('Input factor', 'input', GOLD, 'o'), ('Readout factor', 'readout', ROSE, 'o'),
            ('Recurrent factor', 'recurrence', PLUM, 's')]
    for k, (label, key, color, marker) in enumerate(rows):
        est, lo, hi, _ = e['factors'][key]
        y_label = 90.5 - 11.5 * k
        add(101.3, y_label, label, 8.8, color, 'bold')
        add(101.3, y_label - 3.5, f'{mono(est)}%  [{mono(lo)}, {mono(hi)}]', 8.0, INK, family='JuliaMono')
        y = y_label - 7.6 - 56
        ax.plot([lo, hi], [y, y], color=color, lw=1.6, solid_capstyle='butt')
        for end in (lo, hi):
            ax.plot([end, end], [y - .9, y + .9], color=color, lw=1.0)
        ax.plot([est], [y], marker=marker, ms=4.6, color=color, mec=color)
        ax.plot([0, 0], [y - 1.6, y + 1.6], color='#7D7280', lw=.75, ls=(0, (2, 2)), zorder=0)
    ax.xaxis.set_major_locator(FixedLocator([-100, 0, 100]))
    ax.xaxis.set_major_formatter(FuncFormatter(lambda x, p: mono(x, 0).replace('+0', '0')))
    ax.set_xlabel('Change in mean square (%)')

    # ---- frame 3: a fifth recording acquires internal information.
    est, lo, hi, wins = e['comb']
    retext('Risk forecasts', 'Fifth recording')
    retext('Fixed data and point prediction', 'Endpoints kept; one site added')
    retext('40 new independent networks', '80 new independent networks')
    retext('19', f'{wins}', color=FORECAST)
    retext('of 40 favour prior averaging;', 'of 80 networks: better')
    retext('21 favour nominal', 'internal-combination estimates')
    texts['$S(v,e)=\\log v+e^2/v$'].remove()
    for x, face, edge in [(144.6, ROSE, GOLD), (148.4, ROSE, '#FFFFFF'), (152.2, ROSE, '#FFFFFF'), (156.0, ROSE, '#FFFFFF')]:
        base.add_patch(Circle((x, 86.3), 1.45, facecolor=face, edgecolor=edge, lw=1.1 if edge == GOLD else .6, zorder=3))
    add(159.4, 86.2, '+', 9.0, MUTED, ha='center')
    base.add_patch(Circle((162.8, 86.3), 1.45, facecolor=PLUM, edgecolor='#FFFFFF', lw=.6, zorder=3))
    texts['v: MSE forecast; e: response error'].remove()
    retext('One network accounts for 64%\nof the summed score difference',
           'Fifth site chosen for recurrent sums,\nversus a random fifth site;\nresponse-prediction gain uncertain',
           y=78.6, linespacing=1.25)
    retext('95% paired network-cluster CI', '95% paired network-bootstrap CI')
    ax = fig.axes[2]
    for a in list(ax.lines) + list(ax.texts):
        a.remove()
    ax.set_xlim(-55, 12)
    add(143.3, 68.0, 'Combination estimation MSE', 8.8, KEY_TEXT, 'bold')
    add(143.3, 64.5, f'{mono(est)}%  [{mono(lo)}, {mono(hi)}]', 8.0, INK, family='JuliaMono')
    ax.plot([lo, hi], [-.2, -.2], color=FORECAST, lw=1.6, solid_capstyle='butt')
    for end in (lo, hi):
        ax.plot([end, end], [-.36, -.04], color=FORECAST, lw=1.0)
    ax.plot([est], [-.2], marker='D', ms=4.4, color=FORECAST)
    ax.plot([0, 0], [-.48, .08], color='#7D7280', lw=.75, ls=(0, (2, 2)), zorder=0)
    ax.xaxis.set_major_locator(FixedLocator([-40, -20, 0]))
    ax.xaxis.set_major_formatter(FuncFormatter(lambda x, p: mono(x, 0).replace('+0', '0')))
    ax.set_xlabel('Change vs random fifth site (%)')

    # ---- summary frame.
    retext('Better risk estimates do not necessarily make better recording decisions.', KEY)
    for old in ['We use a', 'common MAP estimator', '. Identical recording sets and data yield identical predictions.']:
        texts[old].remove()
    y1 = texts['Primary error and forecast-score intervals include zero.'].get_position()[1] + 3.2
    first = [('Every allocation uses ', 'normal'), ('five recordings', 'bold'),
             (' and a common MAP fit; the stimulus response is withheld from calibration.', 'normal')]
    retext('Primary error and forecast-score intervals include zero.',
           'Endpoint recording narrows compatible responses and contracts the input and readout error factors.')
    line3 = [t for t in base.texts if t.get_text().startswith('Exploratory 100-unit')][0]
    line3.set_text('A fifth site chosen for recurrent gain sums improves their estimates on independent networks.')
    line4 = [t for t in base.texts if t.get_text().startswith('All four favour prior averaging')][0]
    line4.set_text('Its response-prediction gain remains uncertain. All networks are simulated; no biological validation.')
    fig.canvas.draw()
    r = fig.canvas.get_renderer()
    x = 59.0
    for s, weight in first:
        t = add(x, y1, s, 8.2, INK, weight)
        x += t.get_window_extent(r).width / base.bbox.width * 190

    # ---- checks: every visible text inside its frame, no overlaps, no empty glyphs.
    fig.canvas.draw()
    r = fig.canvas.get_renderer()
    visible = [t for t in fig.findobj(Text) if t.get_visible() and t.get_text().strip()]
    problems = [(t.get_text(), fs.glyph_problems(t)) for t in visible if fs.glyph_problems(t)]
    boxes = [(t.get_text(), t.get_window_extent(r)) for t in visible]
    for i, (a, b) in enumerate(boxes):
        for c, d in boxes[i + 1:]:
            if min(b.x1, d.x1) - max(b.x0, d.x0) > 1 and min(b.y1, d.y1) - max(b.y0, d.y0) > 1:
                problems.append(('overlap', a, c))
    # Text inside the three evidence frames and the summary frame stays within them.
    frames = [(56.5, 96.5, 39.5, 111.5), (98.5, 138.5, 39.5, 111.5), (140.5, 180.5, 39.5, 111.5), (56.5, 180.5, 12.5, 36.8)]
    inv = base.transData.inverted()
    for t in base.texts:
        if not (t.get_visible() and t.get_text().strip()):
            continue
        (x0, y0), (x1, y1) = inv.transform(t.get_window_extent(r).get_points())
        for fx0, fx1, fy0, fy1 in frames:
            if fx0 <= (x0 + x1) / 2 <= fx1 and fy0 <= (y0 + y1) / 2 <= fy1 and (x0 < fx0 + 1 or x1 > fx1 - 1):
                problems.append(('beyond frame', t.get_text()))
    assert not problems, problems
    kw.update(dpi=300)
    matplotlib.rcParams['svg.hashsalt'] = 'graphical-abstract'  # stable SVG element ids
    for ext in ('pdf', 'png', 'svg'):
        opts = dict(kw)
        if ext == 'pdf':
            opts['metadata'] = {'CreationDate': None, 'ModDate': None}
        if ext == 'svg':
            # Write through a string buffer so the SVG has LF line endings on every platform.
            buffer = io.StringIO()
            save(fig, buffer, format='svg', **opts, metadata={'Date': None})
            (HERE / 'graphical_abstract.svg').write_bytes(buffer.getvalue().encode('utf-8'))
        else:
            save(fig, HERE / f'graphical_abstract.{ext}', **opts)
        shutil.copy2(HERE / f'graphical_abstract.{ext}', READ / f'graphical_abstract.{ext}')
    (READ / 'graphical_abstract_text.txt').write_text(
        '\n'.join(t.get_text() for t in visible) + '\n', encoding='utf-8', newline='\n')
    v, w, c, f = e['valid'], e['width'], e['comb'], e['factors']
    copy = f"""# Graphical abstract

Predictive risk and recording decisions in partially observed neural networks

The layout keeps the original graphical abstract: network illustration, three numbered evidence frames, the integrated-response definition and a summary frame. Simulated 100-unit networks have known connectivity and uncertain gains; every allocation records five sites.

- **Network.** Pink nodes are recorded. The stimulation site (gold ring) and a readout (dark ring, one of three) are recorded together with one further site.
- **1 Endpoint recording.** In forty independent validation networks, recording both endpoints changed held-out response MSE by {v[0]:.2f}% (95% CI {v[1]:.2f}% to {v[2]:.2f}%) relative to five ordinary sites; {v[3]} of 40 networks improved. In a further forty networks, the squared compatible response range changed by {w[0]:.2f}% and narrowed in {w[3]} of 40. Dots are networks.
- **2 Error factors.** The exact factorization separates input, recurrent propagation and readout. Endpoint relative to ordinary recording changed the mean squared input contribution by {f['input'][0]:.2f}%, the readout contribution by {f['readout'][0]:.2f}% and the recurrent contribution by {f['recurrence'][0]:+.2f}% (95% CI {f['recurrence'][1]:.2f}% to {f['recurrence'][2]:+.2f}%).
- **3 Fifth recording.** With the four endpoints kept, a fifth site chosen for the recurrent gain sums changed internal-combination estimation MSE by {c[0]:.2f}% (95% CI {c[1]:.2f}% to {c[2]:.2f}%) relative to a random fifth site in eighty new networks; {c[3]} of 80 improved. Its response-prediction change remained uncertain.

{KEY}
"""
    (READ / 'graphical_abstract_copy.md').write_text(copy, encoding='utf-8', newline='\n')
    print(json.dumps({'texts_checked': len(visible), 'outputs': 3}))


if __name__ == '__main__':
    main()
