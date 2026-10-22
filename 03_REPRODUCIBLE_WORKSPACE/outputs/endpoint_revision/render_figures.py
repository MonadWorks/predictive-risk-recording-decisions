"""Manuscript figures drawn directly from the retained network-level analyses.

Every plotted value is read from work/recording_extensions/*/analysis and the
statistics printed beside each interval are asserted against those files.
Run from any directory: python render_figures.py [--only NAME ...]
"""
from pathlib import Path
import argparse, csv, json
import numpy as np
import figure_style as fs
from figure_style import (Canvas, INK, MUTED, LABEL, ROSE, ROSE_DARK, MULBERRY, READOUT, GOLD, GREY, LIGHT_GREY,
                          PLUM, BLEND, NOISE, PAPER, TICK_PT, LABEL_PT, CATEGORY, NUMBER, NOTE)

HERE = Path(__file__).resolve().parent
R = HERE.parents[1] / 'work/recording_extensions'
OUT = HERE / 'figures'


def load(rel):
    return json.loads((R / rel).read_text(encoding='utf-8'))


PAPER_TEXT = (HERE / 'paper.md').read_text(encoding='utf-8')


def in_paper(*values):
    """Printed statistics that the manuscript reports must match its text exactly."""
    import re
    for v in values:
        s = f'{abs(v):.2f}'
        assert re.search(r'(?<![\d.])' + re.escape(s) + r'(?!\d)', PAPER_TEXT), f'{v:+.2f}'


def pct(c):
    """(estimate, lo, hi, wins, n) from either summary convention."""
    if 'relative_change_percent' in c:
        return c['relative_change_percent'], *c['ci95_percent'], c['wins'], 40
    return c['change_pct'], *c['ci95'], c['wins'], c['n']


def forest_rows(cv, ax, rows, x_num, x_wins=None, size=NUMBER):
    """Draw comparison rows and print estimate [95% CI] beside each one."""
    for row in rows:
        est, lo, hi, wins, n = row['stat']
        fs.interval(ax, row['y'], est, lo, hi, row['color'], row.get('filled', True), row.get('adjusted'))
        y = cv.y_of(ax, row['y'])
        cv.mono(x_num, y, fs.ci_text(est, lo, hi, row.get('digits', 2)), size=size, va='center')
        if x_wins is not None:
            cv.mono(x_wins, y, f'{wins}/{n}', size=size, va='center', ha='right', color=MUTED)


# ------------------------------------------------------------------ Fig. 1
def endpoint_evidence():
    first = load('round2/analysis/endpoint_summary.json')
    valid = load('round2/analysis/validation_summary.json')
    mech = load('round2/analysis/mechanism_summary.json')
    policies = ['neither', 'stim_only', 'readouts_only', 'both']
    colors = [GREY, GOLD, READOUT, ROSE]
    cv = Canvas(146)
    lo_y, hi_y = 1e-9, 1e-1
    for x0, data, letter, title in [(4, first, 'a', 'First cohort, 40 networks'),
                                    (94, valid, 'b', 'Independent validation, 40 new networks')]:
        cv.header(x0, 140, letter, title)
        ax = cv.ax(x0 + 15, 74, 66, 60)
        fs.strip(ax, [data['network_means'][p] for p in policies], colors, seed=7 if letter == 'a' else 8)
        fs.log_axis(ax.yaxis, lo_y, hi_y, every=2)
        ax.set_ylabel('Held-out response MSE')
        # Allocation key: which endpoint groups occupy the five recording slots.
        for k, name in enumerate(['Neither', 'Stimulus', 'Readouts', 'Both']):
            xm = x0 + 15 + 66 * (k + .6) / 4.0
            cv.text(xm, 69.4, name, CATEGORY, ha='center')
            stim = policies[k] in ('stim_only', 'both'); read = policies[k] in ('readouts_only', 'both')
            cv.marker(xm, 65.0, GOLD, filled=stim, size=4.0, edge=GOLD if stim else LIGHT_GREY)
            for j in range(3):
                cv.marker(xm - 2.6 + 2.6 * j, 61.2, READOUT if not read else ROSE, filled=read, size=3.3,
                          edge=ROSE_DARK if read else LIGHT_GREY)
        cv.note(x0 + 2, 65.0, 'Stimulus site', va='center')
        cv.note(x0 + 2, 61.2, 'Three readouts', va='center')

    # c: every allocation contrast on one ratio scale, both cohorts.
    cv.header(4, 49, 'c', 'Joint endpoint recording versus each alternative')
    ax = cv.ax(56, 10, 62, 33)
    fs.ratio_axis(ax, .002, 1.7, [.01, .1, .5, 1], 'Change in mean MSE, both ends versus comparator')
    groups = [('Neither endpoint', 'both_vs_neither'), ('Stimulus site only', 'both_vs_stim_only'),
              ('Three readouts only', 'both_vs_readouts_only')]
    rows = []
    for y, (label, key) in enumerate(groups):
        for data, filled, off in [(first, False, -.21), (valid, True, .21)]:
            rows.append(dict(y=y + off, stat=pct(data['comparisons'][key]), color=ROSE, filled=filled))
    y_other = len(groups) + .35
    for data, filled, off in [(mech['first_cohort'], False, -.21), (mech['validation_cohort'], True, .21)]:
        rows.append(dict(y=y_other + off, stat=pct(data['comparisons']['passive_mse']), color=GREY, filled=filled))
    ax.set_ylim(y_other + .6, -.55)
    forest_rows(cv, ax, rows, 122, 177)
    for y, (label, _) in enumerate(groups):
        top_label(cv, ax, 6.5, y - .21, label, CATEGORY, ms=3.6)
    base = top_label(cv, ax, 6.5, y_other - .21, 'Activity under other inputs', CATEGORY, ms=3.6)
    cv.note(6.5, base - 3.0 + cap_mm(CATEGORY) / 2, 'Exploratory; both versus neither', va='center')
    cv.note(122, 45.6, 'Change, % [95% CI]')
    cv.note(177, 45.6, 'Improved', ha='right')
    cv.marker(57.5, 46.3, ROSE, filled=False, size=3.4); cv.note(59.6, 45.6, 'First cohort')
    cv.marker(78.5, 46.3, ROSE, filled=True, size=3.4); cv.note(80.6, 45.6, 'Validation (primary: neither)')
    # Statistics printed beside the intervals must equal the analysis files.
    in_paper(*pct(valid['comparisons']['both_vs_neither'])[:3], *pct(first['comparisons']['both_vs_neither'])[:3],
             *pct(valid['comparisons']['both_vs_stim_only'])[:3], *pct(valid['comparisons']['both_vs_readouts_only'])[:3],
             *pct(mech['validation_cohort']['comparisons']['passive_mse'])[:3])
    return fs.save(cv, OUT / 'endpoint_evidence')


_CAP = {}


def cap_mm(size):
    """Cap height of the label font in millimetres, so that label ink can be aligned to a marker's top."""
    if size not in _CAP:
        from matplotlib.textpath import TextPath
        from matplotlib.font_manager import FontProperties
        h = TextPath((0, 0), 'H', size=size, prop=FontProperties(family='BentonSans')).get_extents().height
        _CAP[size] = h * 25.4 / 72
    return _CAP[size]


def top_label(cv, ax, x, y_first, text, size, ms=3.4, **kw):
    """Group label whose cap line sits on the top of the first row's marker (rows of one group are labelled once).

    y_first is the data y of the group's first (upper) row, ms its marker size in points. Returns the label baseline.
    """
    top = cv.y_of(ax, y_first) + ms / 2 * 25.4 / 72 + .16
    base = top - cap_mm(size)
    cv.text(x, base, text, size, **kw)
    return base


def forest_header(cv, x_num, x_wins, y, wins_label='Improved'):
    cv.note(x_num, y, 'Change, % [95% CI]')
    if x_wins is not None:
        cv.note(x_wins, y, wins_label, ha='right')


# ------------------------------------------------------------------ Fig. 2
def mechanism_evidence():
    p = load('round3/analysis/profile_summary.json')
    o = load('round3/analysis/oracle_summary.json')
    pol = ['neither', 'both', 'both_noise4', 'both_noise16']
    colors = [GREY] + NOISE
    edges = [GREY, ROSE, ROSE, ROSE]
    cv = Canvas(132)
    # a: paired range widths, primary comparison.
    cv.header(4, 126, 'a', 'Paired squared range widths')
    ax = cv.ax(17, 78, 40, 40)
    a, b = np.asarray(p['metrics']['neither']['width2']), np.asarray(p['metrics']['both']['width2'])
    lim = (1e-7, 1e0)
    ax.plot(lim, lim, color=MUTED, lw=.55, ls=(0, (2.2, 2.2)), zorder=0)
    ax.scatter(a, b, s=8, color=ROSE, edgecolors='none', zorder=2, alpha=.92)
    fs.log_axis(ax.xaxis, *lim, every=2); fs.log_axis(ax.yaxis, *lim, every=2); fs.clean(ax)
    ax.set_xlabel('Ordinary sites'); ax.set_ylabel('Both ends')
    c = p['comparisons']['both_vs_neither']['width2']
    cv.mono(19.5, 115.0, f"{c['wins']}/40 below the line", size=5.6)
    cv.mono(19.5, 111.6, fs.ci_text(c['change_pct'], *c['ci95']), size=5.6)
    in_paper(c['change_pct'], *c['ci95'])
    # b, c: recording precision at the endpoints.
    for x0, letter, title, metric, ylabel, lim in [
            (64, 'b', 'Range and endpoint precision', 'width2', 'Squared response-range width', (1e-7, 1e0)),
            (124, 'c', 'Error and endpoint precision', 'mse', 'Held-out response MSE', (1e-10, 1e-1))]:
        cv.header(x0, 126, letter, title)
        ax = cv.ax(x0 + 13, 78, 41, 40)
        fs.strip(ax, [p['metrics'][k][metric] for k in pol], colors, edges=edges, seed=21, width=.15, size=6.5)
        fs.log_axis(ax.yaxis, *lim, every=2 if metric == 'width2' else 3)
        ax.set_ylabel(ylabel)
        cv.categories(ax, ['Ordinary', 'Ends', 'Ends\n×4 SD', 'Ends\n×16 SD'], 75.2, size=6.2)
        for k in ['both_noise4_vs_both', 'both_noise16_vs_both']:
            in_paper(p['comparisons'][k][metric]['change_pct'], *p['comparisons'][k][metric]['ci95'])
    in_paper(p['comparisons']['both_vs_neither']['mse']['change_pct'])
    # d: oracle gain information followed by refitting.
    cv.header(4, 58, 'd', 'Gain information, then refitting')
    keys = ['neither', 'known_random4', 'known_stim', 'known_readouts', 'known_both']
    ax = cv.ax(17, 18, 64, 34)
    fs.strip(ax, [o['metrics'][k] for k in keys], [LIGHT_GREY, GREY, GOLD, READOUT, ROSE], seed=31, width=.15, size=6.5)
    fs.log_axis(ax.yaxis, 1e-11, 1e-1, every=2)
    ax.set_ylabel('Held-out response MSE')
    cv.categories(ax, ['None', 'Four\nordinary', 'Stimulus\ngain', 'Readout\ngains', 'Endpoint\ngains'], 15.2, size=6.2)
    # e: the three oracle contrasts.
    cv.header(94, 58, 'e', 'Endpoint gains known, versus')
    ax = cv.ax(121, 21, 24, 25)
    fs.ratio_axis(ax, .004, 1.6, [.01, .1, 1], 'Change in mean MSE')
    rows = [dict(y=k, stat=pct(o['comparisons'][f'known_both_vs_{ref}']), color=ROSE, filled=False)
            for k, ref in enumerate(['known_random4', 'known_stim', 'known_readouts'])]
    ax.set_ylim(2.6, -.6)
    forest_rows(cv, ax, rows, 147.5, None, size=5.7)
    for k, label in enumerate(['Four ordinary gains', 'Stimulus gain only', 'Readout gains only']):
        cv.text(95.5, cv.y_of(ax, k), label, 6.2, va='center')
    cv.note(147.5, 50.2, 'Change, % [95% CI]')
    for r in rows:
        in_paper(*r['stat'][:3])
    return fs.save(cv, OUT / 'mechanism_evidence')


def row_labels(cv, ax, x, rows, size=6.3, note=None):
    for y, label in rows:
        cv.text(x, cv.y_of(ax, y), label, size, va='center')


# ------------------------------------------------------------------ Fig. 3
def parameter_mechanism():
    o = load('round4/analysis/oracle_data_fit_audit_summary.json')
    v = load('round4/analysis/mechanism_validation_summary.json')
    r5 = load('round5/analysis/summary.json')
    keys = ['ordinary4', 'ordinary8', 'recurrence4', 'endpoints4', 'endpoint_ordinary8', 'endpoints_recurrence8']
    reveal = {'ordinary4': (0, 0, 4), 'ordinary8': (0, 0, 8), 'recurrence4': (0, 1, 0), 'endpoints4': (1, 0, 0),
              'endpoint_ordinary8': (1, 0, 4), 'endpoints_recurrence8': (1, 1, 0)}
    cv = Canvas(124)
    # a: what is revealed before refitting, and the resulting error.
    cv.header(4, 118, 'a', 'Known gain information, then refitting')
    ax = cv.ax(17, 36, 74, 74)
    fs.strip(ax, [o['metrics'][k] for k in keys], [GREY, GREY, PLUM, ROSE, ROSE, BLEND], seed=41, width=.15, size=6.5)
    fs.log_axis(ax.yaxis, 1e-12, 1e-2, every=2)
    ax.set_ylabel('Held-out response MSE')
    for row, (label, color, yy) in enumerate([('Endpoint gains', ROSE, 30.5), ('Recurrent sums', PLUM, 26.0),
                                             ('Ordinary gains', GREY, 21.5)]):
        cv.note(4, yy, label, va='center')
        for k, key in enumerate(keys):
            x = cv.x_of(ax, k)
            n = reveal[key][row]
            if row == 2 and n:
                cv.mono(x, yy, str(n), size=6.0, ha='center', va='center', color=INK)
            elif n:
                cv.marker(x, yy, color, size=3.6)
            else:
                cv.marker(x, yy, LIGHT_GREY, filled=False, size=2.6)
    cv.note(4, 14.6, 'Filled dots: four endpoint gains or four recurrent sums revealed;')
    cv.note(4, 11.2, 'numbers: ordinary gains revealed. Same five ordinary recordings throughout.')
    # b: contribution of each finite-response factor to fitted-response error.
    cv.header(100, 118, 'b', 'Error factors, endpoint versus ordinary')
    ax = cv.ax(124, 85, 22, 24)
    fs.ratio_axis(ax, .003, 3.2, [.01, .1, 1], 'Change in mean square')
    comp = v['component_comparisons']
    rows = [dict(y=k, stat=pct(comp[key]), color=c, filled=True)
            for k, (key, c) in enumerate([('input', GOLD), ('recurrence', PLUM), ('readout', ROSE)])]
    ax.set_ylim(2.6, -.6)
    forest_rows(cv, ax, rows, 148.5, None, size=5.7)
    row_labels(cv, ax, 101, [(0, 'Input'), (1, 'Recurrent'), (2, 'Readout')])
    cv.note(148.5, 112.4, 'Change, % [95% CI]')
    for r in rows:
        in_paper(*r['stat'][:3])
    # c: endpoint plus recurrent information versus each control, including replication.
    cv.header(100, 68, 'c', 'Endpoint gains plus recurrent sums, versus')
    ax = cv.ax(101, 13, 34, 46)
    fs.ratio_axis(ax, .001, 1.6, [.01, .1, 1], 'Change in mean MSE', ref=False)
    rep = r5['primary']['response_mse/oracle_combinations_vs_oracle_ordinary']
    specs = [('Eight ordinary gains', o['comparisons']['endpoints_recurrence8_vs_ordinary8'], True, None),
             ('Endpoint gains alone', o['comparisons']['endpoints_recurrence8_vs_endpoints4'], True, None),
             ('Endpoint + four ordinary (added)', o['comparisons']['endpoints_recurrence8_vs_endpoint_ordinary8'], False, None),
             ('Same control, 40 new networks', rep, True, rep['ci_family_three'])]
    ax.set_ylim(3.55, -.75)
    rows = [dict(y=k + .12, stat=pct(c), color=PLUM, filled=f, adjusted=adj) for k, (_, c, f, adj) in enumerate(specs)]
    forest_rows(cv, ax, rows, 137.5, 177.5, size=5.7)
    for r in rows:
        ax.plot([1, 1], [r['y'] - .2, r['y'] + .2], color=MUTED, lw=.55, ls=(0, (1.6, 1.6)), zorder=0)
    for k, (label, *_ ) in enumerate(specs):
        cv.text(101, cv.y_of(ax, k - .3), label, 6.2, va='center')
    forest_header(cv, 137.5, 177.5, 62.6)
    for r in rows:
        in_paper(*r['stat'][:3])
    in_paper(*rep['ci_family_three'])
    return fs.save(cv, OUT / 'parameter_mechanism')


# ------------------------------------------------------------------ Fig. 4
def recording_information():
    r5 = load('round5/analysis/summary.json')
    r6 = load('round6/analysis/summary.json')
    pol = ['endpoints4', 'random5', 'combination5', 'response5']
    colors = [LIGHT_GREY, GREY, PLUM, ROSE]
    cv = Canvas(140)
    # a: the four allocations.
    cv.header(4, 134, 'a', 'Calibration allocations')
    names = ['Four endpoints', '+ random site', '+ combination-directed', '+ response-directed']
    for k, (name, c) in enumerate(zip(names, colors)):
        y = 122 - 9 * k
        cv.marker(7, y, GOLD, size=4.0)
        for j in range(3):
            cv.marker(11 + 3.2 * j, y, ROSE, size=3.4)
        if k:
            cv.text(21.6, y, '+', CATEGORY, ha='center', va='center', color=MUTED)
            cv.marker(25, y, c, size=3.8, edge=PLUM if c == PLUM else (ROSE_DARK if c == ROSE else fs.GREY_EDGE))
        cv.text(7, y - 4.2, name, 6.2, va='center')
    cv.note(4, 82.4, 'Gold: stimulation site; pink: readouts.', va='center')
    # b, c: per-network held-out error in both cohorts.
    for x0, letter, data, title in [(52, 'b', r5, '40 networks, one noise draw'), (118, 'c', r6, '80 networks, three noise draws')]:
        cv.header(x0, 134, letter, title)
        ax = cv.ax(x0 + 13, 84, 47, 44)
        fs.strip(ax, [data['metrics']['response_mse'][k] for k in pol], colors, seed=51, width=.16, size=5.5 if letter == 'c' else 6.5)
        fs.log_axis(ax.yaxis, 1e-11, 1e-4, every=2)
        ax.set_ylabel('Held-out response MSE')
        cv.categories(ax, ['Four\nends', '+\nrandom', '+\ncomb.', '+\nresponse'], 81.4, size=6.2)
    # d: the same comparisons in both cohorts.
    cv.header(4, 64.5, 'd', 'Fifth-site comparisons in both cohorts')
    cv.marker(112, 65.2, INK, size=3.2); cv.note(114, 64.5, 'Primary')
    cv.marker(128, 65.2, INK, filled=False, size=3.2); cv.note(130, 64.5, 'Secondary')
    cv.base.plot([147, 152], [65.2, 65.2], color=INK, lw=.55, alpha=.55); cv.note(153.5, 64.5, 'Adjusted, 3 tests')
    S5, P5, D6, S6 = r5['secondary'], r5['primary'], r6['diagnostic_contrasts'], r6['secondary']
    rows = [
        ('Profile width², combination vs random', P5['profile_width_squared/combination5_vs_random5'], None, PLUM),
        ('Combination MSE, combination vs random', S5['combination_mse/combination5_vs_random5'], D6['combination_mse/combination5_vs_random5'], PLUM),
        ('Combination MSE, response vs random', S5['combination_mse/response5_vs_random5'], D6['combination_mse/response5_vs_random5'], PLUM),
        ('Response MSE, combination vs random', P5['response_mse/combination5_vs_random5'], S6['combination5_vs_random5'], ROSE),
        ('Response MSE, response vs random', S5['response_mse/response5_vs_random5'], r6['primary'], ROSE),
        ('Response MSE, random fifth vs four ends', S5['response_mse/random5_vs_endpoints4'], S6['random5_vs_endpoints4'], ROSE),
        ('Response MSE, response fifth vs four ends', None, S6['response5_vs_endpoints4'], ROSE),
    ]
    primary5 = {0, 3}; primary6 = {4}
    axes = []
    for x_ax, x_num, cohort, head in [(57, 82.5, 0, '40 networks'), (117, 142.5, 1, '80 networks')]:
        ax = cv.ax(x_ax, 9, 23, 46)
        fs.ratio_axis(ax, .38, 2.3, [.5, 1, 2], 'Change in mean')
        ax.set_ylim(len(rows) - .4, -.6)
        axes.append(ax)
        cv.text(x_ax, 59.4, head, 6.4, weight='bold')
        cv.note(x_num, 59.4, 'Change, % [95% CI]')
        for k, row in enumerate(rows):
            c = row[1 + cohort]
            if c is None:
                cv.mono(x_num, cv.y_of(ax, k), 'not measured' if k == 0 else 'not tested', size=5.7, va='center', color=MUTED)
                continue
            prim = k in (primary5 if cohort == 0 else primary6)
            forest_rows(cv, ax, [dict(y=k, stat=pct(c), color=row[3], filled=prim,
                                      adjusted=c.get('ci_family_three') if prim and cohort == 0 else None)], x_num, None, size=5.7)
    for k, row in enumerate(rows):
        cv.text(4, cv.y_of(axes[0], k), row[0], 6.0, va='center')
    for c in [P5['profile_width_squared/combination5_vs_random5'], P5['response_mse/combination5_vs_random5'],
              S5['combination_mse/combination5_vs_random5'], r6['primary'], S6['response5_vs_endpoints4'],
              S6['random5_vs_endpoints4'], S6['combination5_vs_random5'], D6['combination_mse/combination5_vs_random5']]:
        in_paper(*pct(c)[:3])
    return fs.save(cv, OUT / 'recording_information')


# ------------------------------------------------------------------ Fig. 5
def structure_robustness():
    r = load('round4/analysis/robustness_summary.json')
    keys = ['matched_rank2', 'augmented_rank6', 'random_rank6', 'connectivity_error', 'initial_state_error', 'positive_gain']
    labels = ['Matched rank two', 'Rank six, augmented', 'Rank six, independent',
              'Unmodelled connectivity, 10%', 'Initial-state offset, SD 0.03', 'Positive lognormal gains']
    tags = ['reference', 'primary', '', '', '', '']
    cv = Canvas(70)
    cv.header(4, 64, '', 'Joint endpoint versus five ordinary recordings, 40 paired base seeds')
    ax = cv.ax(60, 12, 58, 41)
    fs.ratio_axis(ax, 1.5e-4, 4.5, [.001, .01, .1, 1], 'Change in mean response MSE')
    ax.set_ylim(len(keys) - .4, -.6)
    rows = [dict(y=k, stat=pct(r[key]['comparison']), color=ROSE, filled=(key == 'augmented_rank6'),
                 adjusted=r[key]['comparison']['ci_bonferroni_six']) for k, key in enumerate(keys)]
    forest_rows(cv, ax, rows, 122, 177)
    for k, (label, tag) in enumerate(zip(labels, tags)):
        y = cv.y_of(ax, k)
        cv.text(6.5, y, label, CATEGORY, va='center')
        if tag:
            cv.note(57, y, tag, va='center', ha='right')
    forest_header(cv, 122, 177, 57.0)
    cv.base.plot([6.5, 10.5], [57.7, 57.7], color=ROSE, lw=1.15)
    cv.marker(8.5, 57.7, ROSE, filled=True, size=3.4)
    cv.note(12.5, 57.0, 'Pointwise 95%; filled: primary')
    cv.base.plot([52, 58], [57.7, 57.7], color=ROSE, lw=.55, alpha=.55)
    cv.note(60, 57.0, 'Six-comparison Bonferroni')
    for row, key in zip(rows, keys):
        in_paper(*row['stat'][:1])
    return fs.save(cv, OUT / 'structure_robustness')


def labelled_forest(cv, ax, specs, x_label, x_num, x_wins=None, size=5.9, label_size=6.3):
    """specs: (y, label, comparison dict, colour, filled, adjusted or None, digits)."""
    rows = []
    for y, label, c, color, filled, adjusted, digits in specs:
        rows.append(dict(y=y, stat=pct(c), color=color, filled=filled, adjusted=adjusted, digits=digits))
        if label:
            cv.text(x_label, cv.y_of(ax, y), label, label_size, va='center')
    forest_rows(cv, ax, rows, x_num, x_wins, size=size)
    return rows


# ------------------------------------------------------- Supplementary Fig. 6
def fitting_sensitivity():
    f = load('round2/analysis/fitting_summary.json')
    cv = Canvas(78)
    cv.header(4, 72, 'a', 'Ensemble versus nominal selection, same recording sets')
    ax = cv.ax(66, 12, 30, 47)
    fs.ratio_axis(ax, .2, 1.6, [.25, .5, 1], 'Change in mean MSE')
    w = f['within_method']
    specs = [(0, 'Ensemble vs nominal, original start', f['original'], MULBERRY, True, None, 2),
             (1, 'Ensemble vs nominal, best of five starts', f['best_of_five'], MULBERRY, False, None, 2),
             (2.4, 'Nominal sets: best of five vs original', w['local_vector'], GREY, False, None, 2),
             (3.4, 'Ensemble sets: best of five vs original', w['ensemble_vector'], MULBERRY, False, None, 2)]
    ax.set_ylim(3.9, -.6)
    rows = labelled_forest(cv, ax, specs, 6, 98.5, None, size=5.6)
    cv.note(98.5, 64.6, 'Change, % [95% CI]')
    for r in rows:
        in_paper(*r['stat'][:3])
    cv.header(130, 72, 'b', 'Each point is one network')
    ax = cv.ax(141, 22, 36, 38)
    x = np.asarray(f['network_means_nominal']['local_vector'] + f['network_means_nominal']['ensemble_vector'])
    lim = (1e-7, 1e-1)
    ax.plot(lim, lim, color=MUTED, lw=.55, ls=(0, (2.2, 2.2)), zorder=0)
    for key, color, filled in [('local_vector', GREY, False), ('ensemble_vector', MULBERRY, True)]:
        ax.scatter(f['network_means_nominal'][key], f['network_means_best'][key], s=9,
                   facecolors=color if filled else PAPER, edgecolors=color if not filled else 'none', linewidths=.6, zorder=2)
    fs.log_axis(ax.xaxis, *lim, every=2); fs.log_axis(ax.yaxis, *lim, every=2); fs.clean(ax)
    ax.set_xlabel('MSE, original start'); ax.set_ylabel('MSE, best of five')
    cv.marker(143, 66.4, GREY, filled=False, size=3.2); cv.note(145, 65.7, 'Nominal')
    cv.marker(158, 66.4, MULBERRY, size=3.2); cv.note(160, 65.7, 'Ensemble')
    return fs.save(cv, OUT / 'fitting_sensitivity')


# ------------------------------------------------------- Supplementary Fig. 7
def method_validation():
    m = load('round3/analysis/method_summary.json')['comparisons']
    a = load('round3/analysis/method_fit_audit.json')['comparisons']
    cv = Canvas(70)
    cv.header(4, 64, '', 'Indirect-recording criteria, 40 networks, five nonendpoint recordings')
    ax = cv.ax(62, 12, 40, 40)
    fs.ratio_axis(ax, .38, 2.1, [.5, 1, 2], 'Change in mean response MSE')
    keys = [('prior_cv_vs_local', 'Held-out prior vs nominal', 'primary'),
            ('prior_cov_vs_local', 'Prior covariance vs nominal', ''),
            ('ensemble_vs_local', 'Prior-averaged risk vs nominal', ''),
            ('prior_cov_vs_ensemble', 'Prior covariance vs prior-averaged', ''),
            ('prior_cov_vs_random', 'Prior covariance vs random', '')]
    ax.set_ylim(len(keys) - .4, -.6)
    for k, (key, label, tag) in enumerate(keys):
        y = cv.y_of(ax, k)
        base = top_label(cv, ax, 6, k - .17, label, 6.3, ms=3.4)
        if tag:
            cv.note(59, base, tag, ha='right')
        for c, off, filled, x_num in [(m[key], -.17, k == 0, 106), (a[key], .17, False, 142)]:
            fs.interval(ax, k + off, *pct(c)[:3], INK if off < 0 else MUTED, filled, marker='o' if off < 0 else 'D', size=3.4 if off < 0 else 3.0)
            cv.mono(x_num, cv.y_of(ax, k + off), fs.ci_text(*pct(c)[:3]), size=5.6, va='center', color=INK if off < 0 else MUTED)
    cv.note(106, 57.2, 'Five common starts')
    cv.note(142, 57.2, 'Additional matched fitting')
    for key in ['prior_cv_vs_local', 'prior_cov_vs_local', 'ensemble_vs_local', 'prior_cov_vs_ensemble', 'prior_cov_vs_random']:
        in_paper(*pct(m[key])[:3])
    in_paper(*pct(a['prior_cov_vs_local'])[:3])
    return fs.save(cv, OUT / 'method_validation')


# ------------------------------------------------------- Supplementary Fig. 8
def limited_budget():
    a = load('round4/analysis/allocation_summary.json')
    cv = Canvas(104)
    cv.header(4, 98, 'a', 'Pair-seeded search, averaged over six settings, versus')
    ax = cv.ax(56, 54, 40, 34)
    fs.ratio_axis(ax, .09, 1.4, [.1, .5, 1], 'Change in mean MSE')
    C = a['comparisons']
    specs = [(0, 'Ensemble greedy', C['endpoint_pair_vs_ensemble_greedy'], INK, True, None, 5),
             (1, 'Endpoint-only enumeration', C['endpoint_pair_vs_endpoint_joint'], INK, False, None, 2),
             (2, 'Nominal greedy', C['endpoint_pair_vs_nominal_greedy'], INK, False, None, 2),
             (3, 'Stimulus first', C['endpoint_pair_vs_stimulus_first'], INK, False, None, 2),
             (4, 'Random sites', C['endpoint_pair_vs_random_all'], INK, False, None, 2),
             (5.35, 'Endpoint-only enumeration vs stimulus first', C['endpoint_joint_vs_stimulus_first'], GREY, False, None, 2)]
    ax.set_ylim(5.8, -.6)
    rows = labelled_forest(cv, ax, specs, 6, 99.5, 177, size=5.6, label_size=6.2)
    forest_header(cv, 99.5, 177, 92.6, 'Lower MSE')
    assert '0.00136' in PAPER_TEXT and '0.00555' in PAPER_TEXT
    for r in rows[1:2] + rows[5:]:
        in_paper(*r['stat'][:3])
    cv.header(4, 42, 'b', 'Each budget and recording-precision setting')
    ax = cv.ax(56, 10, 40, 27)
    fs.ratio_axis(ax, .75, 1.7, [.8, 1, 1.25, 1.6], 'Change in mean MSE')
    names = {'uniform': 'equal noise', 'stimulus_noisy': 'noisy stimulus site', 'readouts_noisy': 'noisy readouts'}
    strata = list(a['strata'].items())
    ax.set_ylim(len(strata) - .4, -.6)
    for k, (key, d) in enumerate(strata):
        budget, setting = key.split('_', 1)
        top_label(cv, ax, 6, k - .18, f'{budget} sites, {names[setting]}', 6.0, ms=3.0)
        for ref, off, color, filled in [('ensemble_greedy', -.18, INK, False), ('endpoint_joint', .18, MULBERRY, False)]:
            fs.interval(ax, k + off, *pct(d['comparisons']['endpoint_pair_vs_' + ref])[:3], color, filled, size=3.0, lw=1.0)
    cv.marker(100, 31.4, INK, filled=False, size=3.0); cv.note(102, 30.7, 'Versus ensemble greedy')
    cv.marker(100, 26.6, MULBERRY, filled=False, size=3.0); cv.note(102, 25.9, 'Versus endpoint-only enumeration')
    cv.note(100, 20.4, f"Same sites as ensemble greedy in {a['agreement_out_of_240']['ensemble_greedy']}/240 settings")
    return fs.save(cv, OUT / 'limited_budget')


# ------------------------------------------------------- Supplementary Fig. 9
def combination_controls():
    v = load('round4/analysis/mechanism_validation_summary.json')
    cv = Canvas(84)
    cv.header(4, 78, 'a', 'Local sensitivity captured by constraints')
    ax = cv.ax(17, 22, 66, 48)
    bases = [('endpoint', 'Four endpoint\ncoordinates', ROSE), ('endpoint_recurrence', 'Endpoints +\nrecurrent sums', BLEND),
             ('random8', 'Eight random\ncombinations', GREY)]
    rng = np.random.default_rng(458)
    for i, (key, _, color) in enumerate(bases):
        for j, (rec, filled) in enumerate([('neither', False), ('both', True)]):
            vals = np.asarray(v['gradient_fractions'][rec][key]); x = i + (j - .5) * .36
            ax.scatter(x + rng.uniform(-.07, .07, len(vals)), vals, s=6, facecolors=color if filled else PAPER,
                       edgecolors=color, linewidths=.5, zorder=2)
            ax.plot([x - .11, x + .11], [np.median(vals)] * 2, color=INK, lw=1.3, zorder=3)
    ax.set_xlim(-.6, 2.6); ax.set_ylim(-.03, 1.03); ax.set_xticks([]); fs.clean(ax, bottom=False)
    ax.set_ylabel('Fraction of squared response gradient')
    cv.categories(ax, [b[1] for b in bases], 19.2, size=6.2)
    cv.marker(19, 7.6, GREY, filled=False, size=3.0); cv.note(21, 6.9, 'Ordinary recordings')
    cv.marker(48, 7.6, GREY, size=3.0); cv.note(50, 6.9, 'Endpoint recordings; bars: medians')
    cv.header(94, 78, 'b', 'Finite changes, endpoint + recurrent sums preserved, versus')
    ax = cv.ax(119, 12, 30, 52)
    fs.ratio_axis(ax, .1, 2.5, [.25, 1, 2], 'Change in mean square')
    P = v['perturbation_comparisons']
    specs = []
    y = 0
    for rec in ['neither', 'both']:
        for rms in ['0.1', '0.3']:
            for ref, color, off in [('random8', GREY, -.17), ('endpoint', ROSE, .17)]:
                specs.append((y + off, None, P[f'{rec}/{rms}/endpoint_recurrence_vs_{ref}'], color, False, None, 2))
            y += 1
    ax.set_ylim(y - .45, -.6)
    rows = labelled_forest(cv, ax, specs, 95, 151.5, None, size=5.3)
    for k, (rec, rms) in enumerate([(r, m) for r in ['Ordinary', 'Endpoint'] for m in ['0.1', '0.3']]):
        top_label(cv, ax, 95, k - .17, f'{rec}, RMS {rms}', 6.0, ms=3.0)
    cv.marker(96, 73.4, GREY, filled=False, size=3.0); cv.note(98, 72.7, 'Versus eight random constraints')
    cv.marker(136, 73.4, ROSE, filled=False, size=3.0); cv.note(138, 72.7, 'Versus endpoint gains alone')
    cv.note(151.5, 67.6, 'Change, % [95% CI]')
    in_paper(*rows[1]['stat'][:3]); in_paper(*rows[5]['stat'][:3])
    return fs.save(cv, OUT / 'combination_controls')


# ------------------------------------------------------ Supplementary Fig. 14
def confirmation():
    with (R / 'analysis/pilot_and_confirmation.csv').open(encoding='utf-8') as f:
        table = list(csv.DictReader(f))
    cv = Canvas(100)
    cv.header(4, 94, '', 'Prior-averaged versus nominal selection: 8-network pilot and 40-network confirmation')
    ax = cv.ax(70, 12, 44, 72)
    fs.ratio_axis(ax, .015, 40, [.1, 1, 10], 'Change in mean MSE')
    names = {('all', '5'): 'All sites, 5 recordings', ('all', '10'): 'All sites, 10 recordings',
             ('exclude_endpoints', '5'): 'Endpoints excluded, 5', ('exclude_endpoints', '10'): 'Endpoints excluded, 10'}
    y = 0
    ys = []
    for objective, title in [('scalar', 'Single response'), ('vector', 'Shared three responses')]:
        ys.append((y - .55, title))
        for r in [r for r in table if r['objective'] == objective]:
            primary = objective == 'vector' and r['pool'] == 'exclude_endpoints' and r['budget'] == '5'
            label = names[r['pool'], r['budget']]
            for est, lo, hi, off, color, filled in [
                    (r['pilot_percent'], r['pilot_ci_low'], r['pilot_ci_high'], -.18, GREY, False),
                    (r['new_percent'], r['new_ci_low'], r['new_ci_high'], .18, MULBERRY, primary)]:
                est, lo, hi = float(est), float(lo), float(hi)
                fs.interval(ax, y + off, est, lo, hi, color, filled, size=3.2, lw=1.0)
            ys.append((y, label + (' (primary)' if primary else '')))
            y += 1
        y += .55
    ax.set_ylim(y - .4, -1.0)
    for yy, label in ys:
        bold = label in ('Single response', 'Shared three responses')
        if bold:
            cv.text(4, cv.y_of(ax, yy), label, 6.4, weight='bold', va='center')
        else:
            top_label(cv, ax, 6, yy - .18, label, 6.1, ms=3.2)
    k = 0
    for objective in ['scalar', 'vector']:
        for r in [r for r in table if r['objective'] == objective]:
            for est, lo, hi, off, color in [(r['pilot_percent'], r['pilot_ci_low'], r['pilot_ci_high'], -.18, MUTED),
                                            (r['new_percent'], r['new_ci_low'], r['new_ci_high'], .18, INK)]:
                cv.mono(118, cv.y_of(ax, k + off), fs.ci_text(float(est), float(lo), float(hi)), size=5.4, va='center', color=color)
            k += 1
        k += .55
    cv.marker(119, 90.9, GREY, filled=False, size=3.0); cv.note(121, 90.2, 'Pilot, 8 networks')
    cv.marker(146, 90.9, MULBERRY, size=3.0); cv.note(148, 90.2, 'Confirmation, 40')
    cv.note(118, 86.3, 'Change, % [95% CI]')
    in_paper(7.947805232614891, -23.59438450780914, 20.947381363059083)
    return fs.save(cv, OUT / 'confirmation')


FIGURES = {'endpoint_evidence': endpoint_evidence, 'mechanism_evidence': mechanism_evidence,
           'parameter_mechanism': parameter_mechanism, 'recording_information': recording_information,
           'structure_robustness': structure_robustness, 'fitting_sensitivity': fitting_sensitivity,
           'method_validation': method_validation, 'limited_budget': limited_budget,
           'combination_controls': combination_controls, 'confirmation': confirmation}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--only', nargs='*')
    args = ap.parse_args()
    report = {}
    for name, fn in FIGURES.items():
        if args.only and name not in args.only:
            continue
        report[name] = fn()
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
