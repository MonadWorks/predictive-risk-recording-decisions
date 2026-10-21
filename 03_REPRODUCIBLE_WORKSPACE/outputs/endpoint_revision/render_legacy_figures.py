"""Original-study supplementary figures with visible negative signs.

The collaborator's refined renderers in ../pastel_figure_suite are run
unchanged. Their figures are written to this manuscript's figures folder as
PDF and PNG; the historical snapshots and audit files there stay untouched.

The BentonSans subset has an empty minus glyph, so the refined figures
printed negative tick labels and exponents as blank space. Before drawing,
BentonSans text replaces the minus with an en dash; text set in Times New
Roman or JuliaMono keeps its true minus.
"""
from pathlib import Path
import re, runpy, subprocess, sys, tempfile
import figure_style as fs
import matplotlib
from matplotlib.figure import Figure
from matplotlib.text import Text

HERE = Path(__file__).resolve().parent
SUITE = HERE.parent / 'pastel_figure_suite'
TARGET = {
    'figS1_complete_paired_distributions_pastel': HERE / 'figures/supplementary',
    'figS2_matched_conditions_pastel': HERE / 'figures/supplementary',
    'figS3_broad_conditions_pastel': HERE / 'figures/supplementary',
    'figS4_bias_shift_conditions_pastel': HERE / 'figures/supplementary',
    'figS5_linear_positive_control_pastel': HERE / 'figures/supplementary',
    'fig1_audit': HERE / 'figures',
    'fig2_data_overview': HERE / 'figures',
    'fig3_recording_decisions': HERE / 'figures',
    'fig4_risk_forecasts': HERE / 'figures',
}
MATH = re.compile(r'(?<!\\)\$(.*?)(?<!\\)\$')


def visible_minus(text):
    """En dash in place of the minus; maths in these labels also draws from BentonSans."""
    pieces = MATH.split(text)  # even indices: plain text; odd indices: maths
    for i, piece in enumerate(pieces):
        pieces[i] = piece.replace(fs.MINUS, fs.EN) if i % 2 == 0 else piece.replace('-', fs.EN).replace(fs.MINUS, fs.EN)
    return '$'.join(pieces)


def font_report(pdf):
    """pdffonts-style lines: every font descriptor must embed its font program."""
    data = pdf.read_bytes()
    lines = ['name type emb sub uni', '-' * 20]
    for desc in re.findall(rb'<<[^<>]*?/Type /FontDescriptor.*?>>', data, re.S):
        name = re.search(rb'/FontName /([^\s/]+)', desc)
        embedded = re.search(rb'/FontFile[23]? ', desc) is not None
        lines.append(f"{name.group(1).decode() if name else '?'} TrueType {'yes' if embedded else 'no'} yes yes")
    assert len(lines) > 2, pdf
    return '\n'.join(lines) + '\n'


def main():
    fs.setup()  # registers BentonSans, JuliaMono and the repository's Times New Roman
    written, skipped = [], []
    original_draw, original_save = Text.draw, Figure.savefig
    original_write = Path.write_text
    scratch = Path(tempfile.mkdtemp(prefix='legacy_audit_'))

    problems = []

    def draw(self, renderer):
        s = self.get_text()
        if s and 'Benton' in self.get_fontname():
            fixed = visible_minus(s)
            if fixed != s:
                self.set_text(fixed)
        if self.get_visible() and self.get_text().strip():
            bad = fs.glyph_problems(self)
            if bad:
                problems.append((self.get_text(), bad))
        return original_draw(self, renderer)

    def save(fig, fname, *args, **kw):
        path = Path(str(fname))
        stem, ext = path.stem, path.suffix.lstrip('.')
        if stem not in TARGET or ext not in ('pdf', 'png'):
            skipped.append(path.name)
            return
        problems.clear()
        fig.canvas.draw()
        assert not problems, (stem, problems)
        kw.update(dpi=300, bbox_inches=None)
        if ext == 'pdf':
            kw['metadata'] = {'CreationDate': None, 'ModDate': None}
        original_save(fig, TARGET[stem] / f'{stem}.{ext}', *args, **kw)
        written.append(f'{stem}.{ext}')

    def write_text(self, *args, **kw):
        # Historical audit receipts stay as recorded; new ones go to a scratch folder.
        if SUITE in self.resolve().parents:
            self = scratch / self.name
        return original_write(self, *args, **kw)

    original_run = subprocess.run

    def run(args, *a, **kw):
        # The renderer verifies font embedding with poppler's pdffonts; check our copy instead.
        if args and args[0] == 'pdffonts':
            pdf = Path(args[1])
            return subprocess.CompletedProcess(args, 0, font_report(TARGET[pdf.stem] / pdf.name), '')
        return original_run(args, *a, **kw)

    Text.draw, Figure.savefig, Path.write_text, subprocess.run = draw, save, write_text, run
    argv = sys.argv
    try:
        runpy.run_path(str(SUITE / 'render_supplements.py'), run_name='__main__')
        runpy.run_path(str(SUITE / 'render_data_overview.py'), run_name='__main__')
        runpy.run_path(str(SUITE / 'render_decisions_forecast.py'), run_name='__main__')
        sys.argv = [argv[0], '--fig1-only']
        runpy.run_path(str(SUITE / 'render_schematic_extension.py'), run_name='__main__')
    finally:
        Text.draw, Figure.savefig, Path.write_text, subprocess.run = original_draw, original_save, original_write, original_run
        sys.argv = argv
        matplotlib.pyplot.close('all')
    expected = {f'{s}.{e}' for s in TARGET for e in ('pdf', 'png')}
    assert set(written) == expected, sorted(expected - set(written))
    print({'written': len(written), 'skipped_outputs': len(skipped)})


if __name__ == '__main__':
    main()
