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
KEY = 'Better risk estimates do not necessarily make better recording decisions.'
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

    BADGE_Y, NUM_DY, TITLE_DY = 106.3, -0.15, -0.86
    # ---- network illustration: the original v5 node colours are kept as drawn.
    retext('12 simulated units · M=3', '100 simulated units · M = 5')
    retext('Uncertain gains and biases', 'Uncertain neuronal gains')
    retext('Response readout (one shown)', 'Response readout (one of three)')

    def dots(rows, n_on, color):
        for k in range(40):
            row, col = divmod(k, 15)
            base.add_patch(Circle((xs[col], rows[row]), .78, facecolor=color if k < n_on else SAME,
                                  edgecolor='none', zorder=3))

    # One vertical rhythm for every frame: header 106, subtitle 102.6, first row 97 downwards.
    # ---- frame 1: endpoint recording (two blocks with identical internal spacing).
    retext('Recording agreement', 'Endpoint recording')
    retext('40 independent networks', 'Stimulation site and readouts')
    for p in [p for p in base.patches if isinstance(p, Circle) and p.radius < 1.0]:
        p.remove()
    for old in ['68%', '82 of 120 designs', '65%', '26 of 40 designs', 'Single-response designs',
                'Shared three-response designs', 'same recording set']:
        texts[old].remove()
    for t in [t for t in base.texts if t.get_text() == 'identical recording sets']:
        t.remove()
    xs = 60.08 + 2.345 * np.arange(15)
    X1, XR = 59.3, 70.5

    def block(top, label, color_text, color, big, line1, line2, n_on, caption, ci):
        add(X1, top, label, 8.3, color_text, 'bold')
        add(X1, top - 4.5, big, 16.0, color, 'bold')
        add(XR, top - 2.9, line1, 8.0)
        add(XR, top - 5.7, line2, 8.0)
        dots([top - 8.9, top - 10.95, top - 13.0], n_on, color)
        add(X1, top - 16.5, caption, 7.2, MUTED)
        add(X1, top - 19.2, ci, 7.2, INK, family='JuliaMono')

    def ci_text(est, lo, hi):
        return f'{mono(est, 2)}% [{mono(lo, 2)}, {mono(hi, 2)}]'

    est, lo, hi, wins = e['valid']
    block(93.87, 'Lower held-out error', ROSE_TEXT, ROSE, f'{abs(est):.0f}%', f'{wins} of 40 networks', 'improved',
          wins, 'Both endpoints vs neither, mean MSE', ci_text(est, lo, hi))
    est, lo, hi, wins = e['width']
    block(68.24, 'Narrower feasible range', PLUM, PLUM, f'{abs(est):.0f}%', f'{wins} of 40 networks', 'narrowed',
          wins, 'Mean squared width, both vs neither', ci_text(est, lo, hi))
    LEG_Y = 42.9                                  # same row as the CI notes of frames 2 and 3
    base.add_patch(Circle((60.08, LEG_Y - .06), .85, facecolor=SAME, edgecolor='none', zorder=1))
    add(62.1, LEG_Y, 'Network not improved', 7.2, MUTED)

    # ---- frame 2: finite-response error factors.
    retext('Response error', 'Error factors')
    retext('Common MAP fit and budget', 'Endpoint vs ordinary recording')
    retext('Same 40 networks', 'Exact three-factor split')
    retext('97.5% paired network-cluster CI', '95% paired network-bootstrap CI')
    ax = fig.axes[1]
    for a in list(ax.lines) + list(ax.texts):
        a.remove()
    ax.set_xlim(-112, 150); ax.set_ylim(0, 36)
    rows = [('Input factor', 'input', GOLD, 'o'), ('Readout factor', 'readout', ROSE, '^'),
            ('Recurrent factor', 'recurrence', PLUM, 's')]
    for k, (label, key, color, marker) in enumerate(rows):
        est, lo, hi, _ = e['factors'][key]
        y_label = 94.2 - 12.2 * k                 # label, value 3.3 below, interval 3.5 further below
        add(101.3, y_label, label, 8.8, color, 'bold')
        add(101.3, y_label - 3.3, f'{mono(est)}%  [{mono(lo)}, {mono(hi)}]', 8.0, INK, family='JuliaMono')
        y = y_label - 6.8 - 56                    # axes origin sits at page y = 56
        ax.plot([lo, hi], [y, y], color=color, lw=1.6, solid_capstyle='butt')
        for end in (lo, hi):
            ax.plot([end, end], [y - .9, y + .9], color=color, lw=1.0)
        ax.plot([est], [y], marker=marker, ms=5.0 if marker == '^' else 4.6, color=color, mec=color)
        ax.plot([0, 0], [y - 1.6, y + 1.6], color='#7D7280', lw=.75, ls=(0, (2, 2)), zorder=0)
    ax.xaxis.set_major_locator(FixedLocator([-100, 0, 100]))
    ax.xaxis.set_major_formatter(FuncFormatter(lambda x, p: mono(x, 0).replace('+0', '0')))
    ax.set_xlabel('Mean-square change vs ordinary (%)')

    # ---- frame 3: a fifth recording acquires internal information.
    est, lo, hi, wins = e['comb']
    retext('Risk forecasts', 'Fifth recording')
    retext('Fixed data and point prediction', 'Endpoints kept, one site added')
    retext('40 new independent networks', '80 new independent networks')
    retext('19', f'{wins}', color=FORECAST)
    retext('of 40 favour prior averaging;', 'of 80 networks improved')
    retext('21 favour nominal', 'combination estimates')
    texts['$S(v,e)=\\log v+e^2/v$'].remove()
    # Recorded sites in the node styles of the illustration: stimulation site, three readouts, one added site.
    node_y = 86.9
    for x, face, edge, lw in [(144.6, '#FFF6DD', GOLD, 1.1), (148.4, '#FFFFFF', PLUM, 1.1),
                              (152.2, '#FFFFFF', PLUM, 1.1), (156.0, '#FFFFFF', PLUM, 1.1)]:
        base.add_patch(Circle((x, node_y), 1.45, facecolor=face, edgecolor=edge, lw=lw, zorder=3))
    add(159.6, node_y - .1, '+', 9.0, MUTED, ha='center')
    base.add_patch(Circle((163.2, node_y), 1.45, facecolor=ROSE, edgecolor='#FFFFFF', lw=.6, zorder=3))
    texts['v: MSE forecast; e: response error'].remove()
    retext('One network accounts for 64%\nof the summed score difference',
           'Fifth site chosen for recurrent\ngain sums, compared with a\nrandom fifth site',
           y=83.3, linespacing=1.25)
    retext('95% paired network-cluster CI', '95% paired network-bootstrap CI')
    ax = fig.axes[2]
    for a in list(ax.lines) + list(ax.texts):
        a.remove()
    ax.set_xlim(-55, 12)
    add(143.3, 73.25, 'Combination estimation MSE', 8.8, KEY_TEXT, 'bold')
    add(143.3, 69.95, f'{mono(est)}%  [{mono(lo)}, {mono(hi)}]', 8.0, INK, family='JuliaMono')
    yb = .291                                # interval sits 3.5 below the value line, as in frame 2
    ax.plot([lo, hi], [yb, yb], color=FORECAST, lw=1.6, solid_capstyle='butt')
    for end in (lo, hi):
        ax.plot([end, end], [yb - .16, yb + .16], color=FORECAST, lw=1.0)
    ax.plot([est], [yb], marker='D', ms=4.4, color=FORECAST)
    ax.plot([0, 0], [yb - .28, yb + .28], color='#7D7280', lw=.75, ls=(0, (2, 2)), zorder=0)
    ax.xaxis.set_major_locator(FixedLocator([-40, -20, 0]))
    ax.xaxis.set_major_formatter(FuncFormatter(lambda x, p: mono(x, 0).replace('+0', '0')))
    ax.set_xlabel('Change vs random fifth site (%)')

    # ---- frame headers: a numbered badge whose left edge sits on the content edge, then the title.
    for t in [t for t in base.texts if t.get_text() in ('1', '2', '3')]:
        t.remove()
    for left, n, title in [(59.3, '1', 'Recording agreement'), (101.3, '2', 'Response error'), (143.3, '3', 'Risk forecasts')]:
        base.add_patch(Circle((left + 2.1, BADGE_Y), 2.1, facecolor=INK, edgecolor='none', zorder=3))
        add(left + 2.1, BADGE_Y + NUM_DY, n, 8.4, '#FFFFFF', 'bold', ha='center', zorder=4)
        t = texts[title]
        t.set_x(left + 5.5)
        t.set_y(BADGE_Y + TITLE_DY)
    add(59.3, 99.9, 'Five recordings per allocation', 8.1, MUTED)

    # ---- summary frame: the key finding (v5 wording and spacing), then four lines in two pairs.
    retext('Better risk estimates do not necessarily make better recording decisions.', KEY, y=32.9)
    for old in ['We use a', 'common MAP estimator', '. Identical recording sets and data yield identical predictions.']:
        texts[old].remove()
    for t in [t for t in base.texts if t.get_text().startswith(('Primary error', 'Exploratory 100-unit', 'All four favour'))]:
        t.remove()
    fig.canvas.draw()
    r = fig.canvas.get_renderer()
    sentences = [
        (28.4, [('We used a ', 'normal'), ('common MAP estimator', 'bold'),
                (' in 12-unit networks, so identical recordings and data yield identical predictions.', 'normal')]),
        (25.2, [('The two criteria chose identical recordings in 68% and 65% of designs, with no clear change in error (\u22123.7%, +2.7%).', 'normal')]),
        (20.7, [(f"Endpoint recording lowered held-out response error by {abs(e['valid'][0]):.0f}%, and a fifth site improved gain-sum estimates by {abs(e['comb'][0]):.0f}%.", 'normal')]),
        (17.5, [('Better estimation did not clearly improve prediction, and ', 'normal'), ('endpoint coverage', 'bold'),
                (' is an informative baseline.', 'normal')]),
    ]
    for y_line, parts in sentences:
        x = 59.0
        for s_, weight in parts:
            t = add(x, y_line, s_, 8.2, INK, weight)
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

The layout keeps the original graphical abstract: network illustration, three numbered evidence frames, the integrated-response definition and a summary frame. The illustration is a schematic in its original colours (pink recorded nodes, a gold ring for the stimulation site, a dark ring for a response readout). The simulated networks have 100 units, known connectivity and uncertain gains, and every allocation records five sites (M = 5).

- **1 Endpoint recording.** In forty independent validation networks, recording both endpoints changed held-out response MSE by {v[0]:.2f}% (95% CI {v[1]:.2f}% to {v[2]:.2f}%) relative to five ordinary sites; {v[3]} of 40 networks improved. In a further forty networks, the mean squared width of the feasible response range changed by {w[0]:.2f}% (95% CI {w[1]:.2f}% to {w[2]:.2f}%) and narrowed in {w[3]} of 40. Dots are networks; grey dots did not improve.
- **2 Error factors.** The exact factorization separates input, recurrent propagation and readout. Endpoint relative to ordinary recording changed the mean squared input contribution by {f['input'][0]:.2f}%, the readout contribution by {f['readout'][0]:.2f}% and the recurrent contribution by {f['recurrence'][0]:+.2f}% (95% CI {f['recurrence'][1]:.2f}% to {f['recurrence'][2]:+.2f}%).
- **3 Fifth recording.** With the four endpoints kept, a fifth site chosen for the recurrent gain sums changed combination-estimation MSE by {c[0]:.2f}% (95% CI {c[1]:.2f}% to {c[2]:.2f}%) relative to a random fifth site in eighty new networks; {c[3]} of 80 improved.
- **Summary.** The key finding leads. Four sentences follow in two pairs: the common-estimator control and the 12-unit risk comparison (identical recordings in 68% and 65% of designs, error changes of -3.7% and +2.7% with intervals including zero), then the endpoint and fifth-site results and a closing statement that better estimation did not clearly improve prediction while endpoint coverage is an informative baseline. Marker shapes distinguish the three factors because the input and readout intervals nearly coincide.

{KEY}
"""
    (READ / 'graphical_abstract_copy.md').write_text(copy, encoding='utf-8', newline='\n')
    print(json.dumps({'texts_checked': len(visible), 'outputs': 3}))


if __name__ == '__main__':
    main()
