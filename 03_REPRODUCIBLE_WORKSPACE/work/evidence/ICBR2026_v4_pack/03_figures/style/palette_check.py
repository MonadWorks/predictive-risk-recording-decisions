"""Quantitative check of candidate accent colours (no plotting).

For each accent we report: WCAG contrast against the paper ground, luminance (L*)
gap to the neutral greys used for 'nominal' marks (so greyscale prints still
separate them), and CIE76 colour difference to those greys after simulating
protanopia, deuteranopia and tritanopia (Machado et al. 2009, severity 1.0,
applied in linear sRGB). A CIE76 delta-E of about 20 or more is easily separable.
"""
import numpy as np
PAPER = '#F7F4EE'; INK = '#15202B'; GREY = '#8A939B'
CANDIDATES = {'signal vermilion': '#DC4F1E', 'ultramarine': '#2A3BCC', 'verdigris': '#0B7A75',
              'Okabe-Ito blue (reference)': '#0072B2', 'Okabe-Ito vermilion (reference)': '#D55E00'}
M = {'protanopia': [[0.152286, 1.052583, -0.204868], [0.114503, 0.786281, 0.099216], [-0.003882, -0.048116, 1.051998]],
     'deuteranopia': [[0.367322, 0.860646, -0.227968], [0.280085, 0.672501, 0.047413], [-0.011820, 0.042940, 0.968881]],
     'tritanopia': [[1.255528, -0.076749, -0.178779], [-0.078411, 0.930809, 0.147602], [0.004733, 0.691367, 0.303900]]}
def rgb(h): return np.array([int(h[i:i + 2], 16) for i in (1, 3, 5)]) / 255
def lin(c): return np.where(c <= .04045, c / 12.92, ((c + .055) / 1.055) ** 2.4)
def unlin(c): c = np.clip(c, 0, 1); return np.where(c <= .0031308, 12.92 * c, 1.055 * c ** (1 / 2.4) - .055)
def lum(c): return float(lin(c) @ [.2126, .7152, .0722])
def contrast(a, b): la, lb = sorted([lum(a), lum(b)], reverse=True); return (la + .05) / (lb + .05)
def lab(c):
    X = np.array([[.4124564, .3575761, .1804375], [.2126729, .7151522, .0721750], [.0193339, .1191920, .9503041]]) @ lin(c)
    X = X / [.95047, 1, 1.08883]; f = np.where(X > .008856, np.cbrt(X), 7.787 * X + 16 / 116)
    return np.array([116 * f[1] - 16, 500 * (f[0] - f[1]), 200 * (f[1] - f[2])])
def sim(c, m): return unlin(np.array(M[m]) @ lin(c))
def dE(a, b): return float(np.linalg.norm(lab(a) - lab(b)))
if __name__ == '__main__':
    p, ink, g = rgb(PAPER), rgb(INK), rgb(GREY)
    print(f'{"colour":34s} contrast/paper  L*gap(grey)  dE vs grey: normal  prot  deut  trit   dE vs ink (min over CVD)')
    for name, h in CANDIDATES.items():
        a = rgb(h)
        row = [dE(a, g)] + [dE(sim(a, m), sim(g, m)) for m in M]
        inkmin = min([dE(a, ink)] + [dE(sim(a, m), sim(ink, m)) for m in M])
        print(f'{name:34s} {contrast(a, p):6.2f}         {abs(lab(a)[0] - lab(g)[0]):5.1f}        '
              + '  '.join(f'{v:5.1f}' for v in row) + f'      {inkmin:5.1f}')
