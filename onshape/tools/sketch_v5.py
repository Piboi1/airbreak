"""Quick concept sketch: module screws onto the BT80 transition, transition slides into the BT80 tube, fins open through the tube windows."""
import os
import numpy as np
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Polygon, Circle
import figures as F

R_OD, R_ID, R_MOD, R70 = 33.02, 32.5, 32.2, 56.3 / 2
BLUE, GREEN, TAN, GREY, RED = '#4f8fd8', '#4caf7a', '#c8a46a', '#9aa0a6', '#c62828'
WZ0, WZ1 = 1.0, 64.5


def box(ax, x0, x1, z0, z1, col, alpha=.85, ec='k', lw=.5, label=None, fs=5.6, ls='-'):
    ax.add_patch(Rectangle((x0, z0), x1 - x0, z1 - z0, fc=col, ec=ec, lw=lw, alpha=alpha, ls=ls))
    if label: ax.text((x0 + x1) / 2, (z0 + z1) / 2, label, fontsize=fs, ha='center', va='center')


def tube_and_head(ax):
    for sx in (-1, 1):
        x0, x1 = sorted((sx * R_ID, sx * R_OD))
        box(ax, x0, x1, -12, WZ0, '#cfcfcf', alpha=1); box(ax, x0, x1, WZ1, 118, '#cfcfcf', alpha=1)
        ax.add_patch(Rectangle((x0 - .15, WZ0), x1 - x0 + .3, WZ1 - WZ0, fc='white', ec=RED, lw=.6, ls='--'))
        box(ax, *sorted((sx * 29.9, sx * R_MOD)), 68.8, 92.8, BLUE)
    box(ax, -29.4, 29.4, 55.2, 56.6, BLUE, alpha=.5); box(ax, -6.1, 6.1, 55.2, 77.9, GREY, label='SG90')
    box(ax, -29.9, 29.9, 78.5, 80.0, BLUE, alpha=.5); box(ax, -21, 2, 80, 92, '#e3c34a'); box(ax, 2.5, 29.5, 80, 90.8, '#9a6fd1'); box(ax, -29.9, 29.9, 95, 99, BLUE, alpha=.6)
    box(ax, -4.0, 4.0, 51.5, 53.3, '#e8c547'); box(ax, -2.4, 2.4, 53.3, 55.2, '#e8c547')       # horn


def module_and_transition(ax, dz=0.0, fins='closed'):
    for sx in (-1, 1):
        # transition: spigot, cone, BT70 sleeve and tube
        box(ax, *sorted((sx * 26.0, sx * 32.3)), -12 + dz, 0 + dz, TAN)
        ax.add_patch(Polygon([(sx * R_OD, -12 + dz), (sx * R70, -47 + dz), (sx * (R70 - 2.0), -47 + dz), (sx * (R_OD - 2.0), -12 + dz)], closed=True, fc=TAN, ec='k', lw=.5, alpha=.85))
        box(ax, *sorted((sx * (R70 - .5), sx * R70)), -47 + dz - 40, -47 + dz, '#bbbbbb', alpha=1)
        # module wall
        box(ax, *sorted((sx * 29.9, sx * R_MOD)), 0 + dz, 68.8 + dz, GREEN)
        # fins
        if fins == 'open':
            x0, x1 = sorted((sx * 25.0, sx * 79.0)); box(ax, x0, x1, 2.7 + dz, 5.1 + dz, '#2f9a63', alpha=.95)
    box(ax, -29.9, 29.9, 0 + dz, 2 + dz, GREEN)
    box(ax, -5, 5, 3.6 + dz, 54.6 + dz, '#7fd1a0'); box(ax, -9, 9, 43.6 + dz, 54.6 + dz, '#7fd1a0'); box(ax, -28, 28, 32.5 + dz, 38 + dz, '#7fd1a0')
    for sx in (-1, 1):                                                       # module bosses with inserts
        box(ax, *sorted((sx * 23.5, sx * 30.2)), 2 + dz, 8 + dz, GREEN)
        ax.plot([sx * 27, sx * 27], [-12 + dz, 6.5 + dz], color='#222', lw=1.4)                  # M3 up from below
        ax.add_patch(Rectangle((sx * 27 - 2.0, -13.5 + dz), 4.0, 1.5, fc='#444', ec='k', lw=.4))     # screw head
        ax.add_patch(Circle((sx * 33.8, -6 + dz), 1.4, fc='#444'))                                    # radial screw in the tube


def sketch(path_png, path_pdf):
    fig, axs = plt.subplots(1, 3, figsize=(11.7, 8.3), gridspec_kw={'width_ratios': [118, 170, 118]})
    lims = [(-38, 80), (-85, 85), (-38, 80)]
    for ax, ttl, xl in zip(axs, ('A  closed, assembled', 'B  open: fins out through the open tube windows', 'C  swap: slide the module and transition out of the bottom'), lims):
        ax.set_xlim(*xl); ax.set_ylim(-165, 125); ax.set_aspect('equal'); ax.axis('off'); ax.set_title(ttl, fontsize=8)
    T = lambda ax, x, z, t, c='k', fs=5.8, **k: ax.text(x, z, t, fontsize=fs, color=c, va='center', **k)
    ax = axs[0]; tube_and_head(ax); module_and_transition(ax)
    T(ax, 37, 108, 'upper BT80 continues', '#555'); T(ax, 37, 86, 'HEAD, fixed in the tube:\nservo, Mercury, battery', '#1f5fa8')
    T(ax, 37, 52, 'horn in the hub slot', '#8a6a00'); T(ax, 37, 28, 'open windows\n38.6 x 63.5 (tube cut once)', RED)
    T(ax, 37, 12, 'MODULE', '#2a7a52', fs=6.6, weight='bold')
    T(ax, 37, -4, 'radial M3 x4: tube to\ntransition spigot (dots)')
    T(ax, 37, -22, 'TRANSITION BT80 to BT70', '#8a6a30', fs=6.4, weight='bold')
    T(ax, 37, -36, 'M3 x4 from below, up through\nthe transition into inserts in\nthe module bosses: screw the\nmodule on and off')
    T(ax, 37, -100, 'BT70 tube', '#666')
    ax = axs[1]; tube_and_head(ax); module_and_transition(ax, fins='open')
    T(ax, -84, 108, 'the tube is cut once:\nno BT80 glued to the fins', fs=6.2)
    T(ax, 40, 20, 'fins hinge at the bottom\nand swing out through the\nopen windows (90 degrees)', '#1d7a4a')
    ax = axs[2]; tube_and_head(ax); module_and_transition(ax, dz=-62)
    ax.annotate('', xy=(0, -34), xytext=(0, 4), arrowprops=dict(arrowstyle='-|>', color=GREEN, lw=2.2))
    T(ax, 37, 86, 'HEAD stays in the tube', '#1f5fa8'); T(ax, 37, 52, 'horn pulls out of the\nhub slot as the module\nslides down', '#2a7a52')
    T(ax, 37, -40, 'module + transition leave\nfrom the bottom (tube is\nfixed to the rocket above)', '#2a7a52')
    T(ax, 37, -112, 'then, outside the tube:\nunscrew the 4 M3 from below\n(ball-end hex key), fit the\nnext module, slide it back in', fs=5.6)
    plt.suptitle('V5 quick sketch (concept, not CAD): the module screws onto the BT80 transition; the transition slides into the BT80 tube; windows left open', fontsize=9, y=0.985)
    plt.tight_layout(rect=(0, 0, 1, 0.96)); fig.savefig(path_png, dpi=170); fig.savefig(path_pdf); plt.close(fig)


if __name__ == '__main__':
    d = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'docs')
    sketch(F.OUT + 'v5_sketch.png', os.path.join(d, 'V5_sketch_transition.pdf')); print('ok')
