"""Sketch 3: what 'the sleeve in the bolt path' means, the alternative, and a one-piece housing (no seam) with the limiter above the bearing ring."""
import os
import numpy as np
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, RegularPolygon
import figures as F

R_ID, R_OD, R_MOD = 32.5, 33.02, 32.2
BLUE, GREEN, TAN, GREY, RED = '#4f8fd8', '#4caf7a', '#c8a46a', '#9aa0a6', '#c62828'


def box(ax, x0, x1, z0, z1, col, alpha=.85, ec='k', lw=.5, ls='-'):
    ax.add_patch(Rectangle((x0, z0), x1 - x0, z1 - z0, fc=col, ec=ec, lw=lw, alpha=alpha, ls=ls))


def bolt(ax, x_head, x_tip, z):
    ax.add_patch(Rectangle((x_head, z - 1.7), 1.65, 3.4, fc='#444', ec='k', lw=.4)); ax.plot([x_head, x_tip], [z, z], color='#222', lw=2.0)


def nut(ax, x, z):
    ax.add_patch(RegularPolygon((x, z), 6, radius=2.9, orientation=np.pi / 2, fc='#bbb', ec='k', lw=.6))


def A(ax):
    box(ax, 32.5, 33.02, -24, 24, '#cfcfcf', alpha=1)
    box(ax, 29.9, 32.2, -12, 24, GREEN); box(ax, 26.0, 32.2, 0, 2, GREEN)
    box(ax, 26.0, 29.6, -12, 0, TAN); box(ax, 26.0, 32.3, -24, -12, TAN)
    box(ax, 26.2, 28.6, -8.6, 0, 'white', alpha=1, ec=RED, ls='--', lw=.7)
    nut(ax, 27.4, -6); bolt(ax, 33.02, 26.4, -6)
    ax.annotate('the module sleeve: 2.3 mm of printed\nwall between the tube and the plug.\nThe bolt clamps it and the module\nload goes through it', xy=(31.0, -6), xytext=(36, 6), fontsize=5.6, arrowprops=dict(arrowstyle='-', lw=.5), color=RED)
    ax.annotate('plug', xy=(27.8, -10), xytext=(8, -16), fontsize=5.6, arrowprops=dict(arrowstyle='-', lw=.5))
    ax.set_xlim(0, 62); ax.set_ylim(-30, 26); ax.set_aspect('equal'); ax.grid(alpha=.15); ax.tick_params(labelsize=5.5)
    ax.set_title('A  sleeve design (sketch 2): 4 bolts hold tube, module and transition', fontsize=7.2)


def B(ax):
    box(ax, 32.5, 33.02, -24, 30, '#cfcfcf', alpha=1)
    box(ax, 29.9, 32.2, 0, 30, GREEN); box(ax, 26.0, 32.2, 0, 2, GREEN)
    box(ax, 26.0, 29.6, -12, 0, TAN); box(ax, 26.0, 32.3, -24, -12, TAN)
    box(ax, 29.7, 32.1, -18.6, -12, 'white', alpha=1, ec=RED, ls='--', lw=.7); nut(ax, 30.9, -16); bolt(ax, 33.02, 29.8, -16)
    box(ax, 27.6, 29.9, 15.3, 22.5, 'white', alpha=1, ec=RED, ls='--', lw=.7); nut(ax, 28.7, 19); bolt(ax, 33.02, 27.8, 19)
    ax.text(36, -16, 'bolt 1: tube to the transition\nshoulder (4)', fontsize=5.6)
    ax.text(36, 19, 'bolt 2: tube to the module wall,\nnut in the module support (4)', fontsize=5.6)
    ax.text(36, 6, 'no sleeve: the module sits\non the plug top', fontsize=5.6, color='#2a7a52')
    ax.set_xlim(0, 62); ax.set_ylim(-30, 34); ax.set_aspect('equal'); ax.grid(alpha=.15); ax.tick_params(labelsize=5.5)
    ax.set_title('B  no sleeve: 8 bolts (4 + 4), nothing printed between tube and transition', fontsize=7.2)


def C(ax):
    # one-piece housing with the rotor installed (z_t); limiter above the bearing ring
    for sx in (-1, 1):
        box(ax, *sorted((sx * 29.9, sx * 32.2)), 0, 68.8, GREEN)
        box(ax, *sorted((sx * 5.4, sx * 8.0)), 10.4, 13.4, GREEN)
        box(ax, *sorted((sx * 8.0, sx * 29.9)), 10.4, 13.4, GREEN, alpha=.6)
        box(ax, *sorted((sx * 10, sx * 19)), 13.4, 24.0, '#2f9a63')
    box(ax, -5, 5, 3.6, 54.6, '#7fd1a0'); box(ax, -9, 9, 43.6, 54.6, '#7fd1a0'); box(ax, -28, 28, 32.5, 38, '#7fd1a0')
    box(ax, -8.5, 8.5, 13.9, 15.9, '#7fd1a0'); box(ax, -16, 16, 16.5, 21.7, '#e3a53a')
    ax.annotate('', xy=(0, 60), xytext=(0, 100), arrowprops=dict(arrowstyle='-|>', color='#2a7a52', lw=2.4))
    ax.text(40, 100, 'rotor enters from the top;\neverything on it is smaller\nthan the housing interior', fontsize=5.6, color='#2a7a52', va='center')
    ax.text(40, 62, 'ONE-PIECE HOUSING\nno seam, no seam screws,\nno band, no snap hooks', fontsize=5.8, color='#1b5e20', weight='bold', va='center')
    ax.text(40, 30, 'limiter stops (dark green, on the\nspokes) and the finger (orange, on\nthe shaft) are above the bearing\nring; V4 had them below', fontsize=5.6, color='#8a5a00', va='center')
    ax.annotate('', xy=(14, 19), xytext=(39, 24), arrowprops=dict(arrowstyle='-', lw=.5, color='#8a5a00'))
    ax.set_xlim(-40, 85); ax.set_ylim(-4, 125); ax.set_aspect('equal'); ax.tick_params(labelsize=5.5); ax.grid(alpha=.15)
    ax.set_title('C  one-piece housing: the rotor goes in from the top (concept)', fontsize=7.2)


def sketch(png, pdf):
    fig = plt.figure(figsize=(11.7, 8.3))
    a = fig.add_axes([0.03, 0.52, 0.30, 0.40]); b = fig.add_axes([0.35, 0.52, 0.30, 0.40]); c = fig.add_axes([0.67, 0.05, 0.31, 0.87]); t = fig.add_axes([0.03, 0.04, 0.62, 0.42])
    A(a); B(b); C(c); t.axis('off')
    txt = ('What "sleeve in the bolt path" means\n'
           'In sketch 2 the module has a bottom sleeve that wraps the transition plug. The bolt goes through the tube, then through that\n'
           'printed sleeve wall, then into the nut in the plug. So the sleeve is clamped between tube and plug, and the module load\n'
           'passes through it. It is the module (the part that breaks), so it is the first thing to crush or creep loose; it also adds 12 mm.\n'
           'Rough numbers: a 100 g shock on a 105 g module is about 100 N, 25 N per bolt; an M3 bolt in a 2.3 mm printed wall bears about\n'
           '100 to 240 N (screening values), so it should hold, but there is little margin.\n\n'
           'Option B has no sleeve: the transition is bolted to the tube, and the module has its own four bolts (8 in all, +4 compared with A).\n\n'
           'The housing seam, without snap hooks or a band\n'
           'The seam exists only because the rotor, which has a limiter finger below the bearing ring, must be fitted from the top. If the\n'
           'limiter moves above the ring (mirror of V4), the rotor drops in from the top and the housing can be one piece: no seam, no seam\n'
           'screws, nothing to hold together. Fins fit through the open windows; the catch caps are printed with the rotor.\n'
           'Risk: it changes the V4 geometry; the limiter clearance, the rotor sweep and the hinge access through the windows must be\n'
           'checked. Fallback: keep the two halves and join them with a sliding dovetail along the seam (no flexing parts).')
    t.text(0.0, 1.0, txt, fontsize=6.4, va='top', family='DejaVu Sans')
    plt.suptitle('V5 sketch 3 (concept, not CAD): the sleeve question, the no-sleeve option, and a one-piece housing', fontsize=9, y=0.985)
    fig.savefig(png, dpi=170); fig.savefig(pdf); plt.close(fig)


if __name__ == '__main__':
    d = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'docs')
    sketch(F.OUT + 'v5_sketch3.png', os.path.join(d, 'V5_sketch3_sleeve_and_seam.pdf')); print('ok')
