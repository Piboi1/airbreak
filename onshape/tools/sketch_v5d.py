"""Sketch 4: how the sections connect (tube, head, module, transition) and why the holes are reused, not multiplied (bolt path B)."""
import os
import numpy as np
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Polygon, RegularPolygon
import figures as F

R_ID, R_OD, R_MOD, R70 = 32.5, 33.02, 32.2, 56.3 / 2
BLUE, GREEN, TAN, GREY, RED = '#4f8fd8', '#4caf7a', '#c8a46a', '#9aa0a6', '#c62828'
C1, C2, C3 = '#1565c0', '#2e7d32', '#e65100'      # bolt set colours: head, module, transition
WZ0, WZ1 = 1.0, 64.5


def box(ax, x0, x1, z0, z1, col, alpha=.85, ec='k', lw=.5, ls='-'):
    ax.add_patch(Rectangle((x0, z0), x1 - x0, z1 - z0, fc=col, ec=ec, lw=lw, alpha=alpha, ls=ls))


def bolt(ax, sx, z, col, tip):
    ax.add_patch(Rectangle((sx * R_OD - (0 if sx > 0 else 1.9), z - 1.9), 1.9, 3.8, fc=col, ec='k', lw=.4))
    ax.plot([sx * R_OD, sx * tip], [z, z], color=col, lw=2.2)


def stack(ax):
    for sx in (-1, 1):
        x0, x1 = sorted((sx * R_ID, sx * R_OD))
        box(ax, x0, x1, -24, WZ0, '#cfcfcf', alpha=1); box(ax, x0, x1, WZ1, 150, '#cfcfcf', alpha=1)
        ax.add_patch(Rectangle((x0 - .15, WZ0), x1 - x0 + .3, WZ1 - WZ0, fc='white', ec=RED, lw=.6, ls='--'))
        box(ax, *sorted((sx * 26.0, sx * 29.6)), -12, 0, TAN); box(ax, *sorted((sx * 26.0, sx * 32.3)), -24, -12, TAN)
        ax.add_patch(Polygon([(sx * R_OD, -24), (sx * R70, -59), (sx * (R70 - 2.0), -59), (sx * (R_OD - 2.0), -24)], closed=True, fc='#e6d3b0', ec='#999', lw=.5, alpha=.9))
        box(ax, *sorted((sx * 29.9, sx * R_MOD)), 0, 68.8, GREEN)
        box(ax, *sorted((sx * 29.9, sx * R_MOD)), 68.8, 92.8, BLUE)
        bolt(ax, sx, 74.8, C1, 28.6); bolt(ax, sx, 22, C2, 28.3); bolt(ax, sx, -18, C3, 29.8)
    box(ax, -29.9, 29.9, 0, 2, GREEN)
    box(ax, -5, 5, 3.6, 54.6, '#7fd1a0'); box(ax, -9, 9, 43.6, 54.6, '#7fd1a0'); box(ax, -28, 28, 32.5, 38, '#7fd1a0')
    box(ax, -16, 16, 16.5, 21.7, '#e3a53a')
    box(ax, -29.4, 29.4, 55.2, 56.6, BLUE, alpha=.5); box(ax, -6.1, 6.1, 55.2, 77.9, GREY)
    box(ax, -29.9, 29.9, 78.5, 80.0, BLUE, alpha=.5); box(ax, -21, 2, 80, 92, '#e3c34a'); box(ax, 2.5, 29.5, 80, 90.8, '#9a6fd1'); box(ax, -29.9, 29.9, 95, 99, BLUE, alpha=.6)
    box(ax, -4.0, 4.0, 51.5, 53.3, '#e8c547'); box(ax, -2.4, 2.4, 53.3, 55.2, '#e8c547')


def sketch(png, pdf):
    fig = plt.figure(figsize=(11.7, 8.3))
    a = fig.add_axes([0.02, 0.05, 0.40, 0.88]); b = fig.add_axes([0.44, 0.05, 0.54, 0.88]); b.axis('off')
    stack(a); a.set_xlim(-45, 95); a.set_ylim(-100, 155); a.set_aspect('equal'); a.axis('off')
    a.set_title('How it fits, nose up (concept)', fontsize=8)
    T = lambda x, z, t, c='k', fs=5.8, **k: a.text(x, z, t, fontsize=fs, color=c, va='center', **k)
    T(37, 140, 'BT80 TUBE: one piece, from the nose end\ndown past the module; it is the skin', '#444'); T(37, 86, 'HEAD, bolted to the tube\n(set 1: 4 bolts)', C1, weight='bold')
    T(37, 50, 'open windows (tube cut once)', RED); T(37, 22, 'MODULE, bolted to the tube\n(set 2: 4 bolts, nuts in its wall)', C2, weight='bold')
    T(37, -18, 'TRANSITION, bolted to the tube\n(set 3: 4 bolts, nuts in the\nshoulder)', C3, weight='bold')
    T(37, -50, 'BT70 side: separate, falls\noff at recovery; not touched', '#8a6a30')
    # right side: the swap and the holes
    b.set_xlim(0, 1); b.set_ylim(0, 1)
    txt = ('Your picture is right: the top of the airbrake joins a BT80 tube, the bottom sits on the transition top,\n'
           'and the BT70 below falls off. The difference is that the BT80 tube goes round the module (it is the skin).\n\n'
           'Why the holes are reused, not multiplied\n'
           'Nothing is screwed into plastic. Every hole is a plain M3 clearance hole, and every bolt ends in a nut:\n'
           '  the tube has 12 holes (4 head, 4 module, 4 transition), cut once, never used for anything else\n'
           '  the transition has 4 holes and 4 nut slots, the same 4 every time\n'
           '  each new module is printed with its own 4 nut slots in the same positions, so it lines up with the tube holes\n'
           'Unbolting leaves nothing damaged: a hole is only a hole. What wears is the bolts and nuts, which are cheap.\n'
           'The transition is not used up: a new module never needs a new hole in it.\n\n'
           'Swap on the ground (the BT70 section is already off)\n'
           '  1  pull the 4 transition bolts (set 3), slide the transition out of the tube bottom\n'
           '  2  pull the 4 module bolts (set 2), slide the module out of the bottom (horn leaves the hub slot)\n'
           '  3  slide the new module in, drop four nuts in its slots first, 4 bolts (set 2)\n'
           '  4  slide the transition back in, 4 bolts (set 3). The head (set 1) is never touched\n'
           '  8 bolts per swap. The same 8 holes in the tube, every time.\n\n'
           'What I still need\n'
           '  the transition: I do not know its diameters. I will build the BT80 side (plug and shoulder) myself and leave\n'
           '  the cone and the BT70 sleeve as placeholders; the BT70 side stays exactly as you have it.\n'
           '  Question: does the module come out of the bottom (as above, needs the transition off) or the top (needs the\n'
           '  head off, and the top end of the tube open)? The bottom is simpler and matches what you said.')
    b.text(0.0, 1.0, txt, fontsize=6.9, va='top', linespacing=1.35)
    plt.suptitle('V5 sketch 4 (concept, not CAD): how the tube, head, module and transition connect, and why the holes are reused', fontsize=9, y=0.985)
    fig.savefig(png, dpi=170); fig.savefig(pdf); plt.close(fig)


if __name__ == '__main__':
    d = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'docs')
    sketch(F.OUT + 'v5_sketch4.png', os.path.join(d, 'V5_sketch4_how_it_fits.pdf')); print('ok')
