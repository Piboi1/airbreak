"""Quick sketch 2: all fasteners are radial M3 bolts with nuts, from the outside, BT80 side only; BT70 side untouched."""
import os
import numpy as np
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Polygon, Circle, RegularPolygon
import figures as F

R_OD, R_ID, R_MOD, R70 = 33.02, 32.5, 32.2, 56.3 / 2
BLUE, GREEN, TAN, GREY, RED = '#4f8fd8', '#4caf7a', '#c8a46a', '#9aa0a6', '#c62828'
WZ0, WZ1 = 1.0, 64.5
# z_t: module seat (plug top) = 0. Plug z_t -12..0 (R26.0..29.6), shoulder z_t -24..-12 (R26..32.3), cone below.


def box(ax, x0, x1, z0, z1, col, alpha=.85, ec='k', lw=.5, label=None, fs=5.6, ls='-'):
    ax.add_patch(Rectangle((x0, z0), x1 - x0, z1 - z0, fc=col, ec=ec, lw=lw, alpha=alpha, ls=ls))
    if label: ax.text((x0 + x1) / 2, (z0 + z1) / 2, label, fontsize=fs, ha='center', va='center')


def stack(ax, fins='closed'):
    for sx in (-1, 1):
        x0, x1 = sorted((sx * R_ID, sx * R_OD))
        box(ax, x0, x1, -24, WZ0, '#cfcfcf', alpha=1); box(ax, x0, x1, WZ1, 118, '#cfcfcf', alpha=1)
        ax.add_patch(Rectangle((x0 - .15, WZ0), x1 - x0 + .3, WZ1 - WZ0, fc='white', ec=RED, lw=.6, ls='--'))
        # transition: plug, shoulder, cone
        box(ax, *sorted((sx * 26.0, sx * 29.6)), -12, 0, TAN)
        box(ax, *sorted((sx * 26.0, sx * 32.3)), -24, -12, TAN)
        ax.add_patch(Polygon([(sx * R_OD, -24), (sx * R70, -59), (sx * (R70 - 2.0), -59), (sx * (R_OD - 2.0), -24)], closed=True, fc='#e6d3b0', ec='#999', lw=.5, alpha=.9))
        box(ax, *sorted((sx * (R70 - .5), sx * R70)), -59 - 35, -59, '#dddddd', alpha=1)
        # module: bottom sleeve over the plug + wall + head
        box(ax, *sorted((sx * 29.9, sx * R_MOD)), -12, 68.8, GREEN)
        box(ax, *sorted((sx * 29.9, sx * R_MOD)), 68.8, 92.8, BLUE)
        if fins == 'open':
            x0f, x1f = sorted((sx * 25.0, sx * 79.0)); box(ax, x0f, x1f, 2.7, 5.1, '#2f9a63', alpha=.95)
        # bolts
        for z, col in ((-6.0, '#222'), (74.8, '#222')):
            ax.add_patch(Rectangle((sx * 33.02 - (0 if sx > 0 else 1.7), z - 1.5), 1.7, 3.0, fc='#444', ec='k', lw=.4))
            ax.plot([sx * 33.0, sx * 26.4 if z < 0 else sx * 29.0], [z, z], color=col, lw=1.2)
    box(ax, -29.9, 29.9, 0, 2, GREEN)
    box(ax, -5, 5, 3.6, 54.6, '#7fd1a0'); box(ax, -9, 9, 43.6, 54.6, '#7fd1a0'); box(ax, -28, 28, 32.5, 38, '#7fd1a0')
    box(ax, -29.4, 29.4, 55.2, 56.6, BLUE, alpha=.5); box(ax, -6.1, 6.1, 55.2, 77.9, GREY, label='SG90')
    box(ax, -29.9, 29.9, 78.5, 80.0, BLUE, alpha=.5); box(ax, -21, 2, 80, 92, '#e3c34a'); box(ax, 2.5, 29.5, 80, 90.8, '#9a6fd1'); box(ax, -29.9, 29.9, 95, 99, BLUE, alpha=.6)
    box(ax, -4.0, 4.0, 51.5, 53.3, '#e8c547'); box(ax, -2.4, 2.4, 53.3, 55.2, '#e8c547')


def detail(ax):
    # radial section x = radius, y = z_t, around the bolt joint
    box(ax, 32.5, 33.02, -24, 20, '#cfcfcf', alpha=1)                         # tube
    box(ax, 29.9, 32.2, -12, 20, GREEN)                                       # module sleeve and wall
    box(ax, 26.0, 32.2, 0, 2, GREEN)                                          # module bottom plate on the plug
    box(ax, 26.0, 29.6, -12, 0, TAN)                                          # plug
    box(ax, 26.0, 32.3, -24, -12, TAN)                                        # shoulder (inside the tube)
    box(ax, 26.2, 28.6, -8.6, -3.4 + 0.0, 'white', alpha=1, ec='#c62828', ls='--')   # nut slot, open to the plug top face
    box(ax, 26.2, 28.6, -8.6, 0.0, 'white', alpha=1, ec='#c62828', ls='--', lw=.7)
    ax.add_patch(RegularPolygon((27.4, -6.0), 6, radius=2.9, orientation=np.pi / 2, fc='#bbb', ec='k', lw=.6))
    ax.plot([34.2, 26.4], [-6, -6], color='#222', lw=2.0); ax.add_patch(Rectangle((33.02, -7.7), 1.65, 3.4, fc='#444', ec='k', lw=.4))
    ax.annotate('M3x8 button-head bolt from the\noutside, through the tube, the\nmodule sleeve and the plug wall', xy=(33.5, -6), xytext=(36, 8), fontsize=5.6, arrowprops=dict(arrowstyle='-', lw=.5))
    ax.annotate('M3 nut in a slot that opens at the plug\ntop face; the module plate covers it', xy=(27.4, -2), xytext=(3, 12), fontsize=5.6, arrowprops=dict(arrowstyle='-', lw=.5))
    ax.annotate('module sleeve R29.9..32.2\n(12 mm below its plate)', xy=(31.0, -10), xytext=(36, -14), fontsize=5.6, arrowprops=dict(arrowstyle='-', lw=.5))
    ax.annotate('plug R26.0..29.6: BT80 side\nonly, nothing below it changes', xy=(27.8, -10), xytext=(2, -17), fontsize=5.6, arrowprops=dict(arrowstyle='-', lw=.5))
    ax.annotate('shoulder inside the tube', xy=(30, -20), xytext=(36, -23), fontsize=5.6, arrowprops=dict(arrowstyle='-', lw=.5))
    ax.text(2, -29, 'BT70 side: untouched', fontsize=6.0, color='#8a6a30', weight='bold')
    ax.set_xlim(0, 60); ax.set_ylim(-32, 24); ax.set_aspect('equal'); ax.tick_params(labelsize=5.5); ax.grid(alpha=.15)
    ax.set_title('Bolt joint, radial section (concept)', fontsize=7.6)


def table(ax):
    ax.axis('off')
    rows = [('fastener', 'V4', 'V5'),
            ('seam screws (housing halves)', '4', '0 (tube clamps)'),
            ('catch-cap screws (rotor)', '4', '0 (integral caps)'),
            ('hinge screws (fins)', '4 M4', '4 M3+nut'),
            ('bottom boss screws', '4', '0'),
            ('tube support screws', '8', '0'),
            ('radial bolts: tube + module + transition', '0', '4 M3+nut'),
            ('radial bolts: head to tube', '0', '4 M3+nut'),
            ('servo M2 (SG90 parts)', '3', '3 M2'),
            ('total', '27', '15')]
    y = 0.97
    for k, (a, b, c) in enumerate(rows):
        w = 'bold' if k in (0, len(rows) - 1) else 'normal'
        ax.text(0.0, y, a, fontsize=6.3, weight=w, va='top'); ax.text(0.60, y, b, fontsize=6.3, weight=w, va='top'); ax.text(0.70, y, c, fontsize=6.3, weight=w, va='top')
        y -= 0.062
    ax.text(0.0, y - 0.01, 'Seam without screws: the tube clamps the halves; snap hooks or a\nband hold them while the module slides in. Total 15 = 12 M3 + nut\nand 3 M2. Print-in-place hinge pins would remove 4 more (11), but\nthe hinge gets weaker and harder to repair.', fontsize=5.8, va='top')
    ax.text(0.0, y - 0.19, 'All nuts sit in slots open to the inside of the module or the\nhead, filled while the parts are still outside the tube.', fontsize=5.8, va='top')
    ax.text(0.0, y - 0.29, 'Swap on the ground, after the sections have separated:\n1  pull the 4 bolts (tube + module + transition)\n2  slide the transition and module out of the tube bottom\n3  lift the module off the plug, set the new one on it\n4  slide back in, 4 bolts. BT70 side never touched.', fontsize=5.8, va='top')
    ax.set_title('Screws, before and after', fontsize=7.6)


def sketch(png, pdf):
    fig = plt.figure(figsize=(11.7, 8.3))
    a1 = fig.add_axes([0.02, 0.06, 0.34, 0.86]); a2 = fig.add_axes([0.38, 0.40, 0.30, 0.52]); a3 = fig.add_axes([0.69, 0.06, 0.30, 0.86])
    a4 = fig.add_axes([0.38, 0.06, 0.30, 0.30])
    stack(a1); a1.set_xlim(-40, 90); a1.set_ylim(-100, 125); a1.set_aspect('equal'); a1.axis('off'); a1.set_title('Assembled (concept): every bolt is radial, from the outside, BT80 side only', fontsize=7.6)
    def T(x, z, t, c='k', fs=5.8, **k): a1.text(x, z, t, fontsize=fs, color=c, va='center', **k)
    T(36, 108, 'upper BT80 continues', '#555'); T(36, 86, 'HEAD: servo, Mercury, battery\n4 radial M3 + nut', '#1f5fa8')
    T(36, 52, 'horn in the hub slot', '#8a6a00'); T(36, 28, 'open windows 38.6 x 63.5', RED); T(36, 10, 'MODULE', '#2a7a52', fs=6.6, weight='bold')
    T(36, -6, '4 radial M3 + nut: tube, module\nsleeve and transition plug', '#222'); T(36, -30, 'TRANSITION BT80 to BT70', '#8a6a30', fs=6.2, weight='bold')
    T(36, -48, 'BT70 side: nothing changes', '#8a6a30')
    detail(a2)
    a3.set_xlim(0, 1); a3.set_ylim(0, 1); table(a3)
    a4.axis('off'); a4.set_xlim(-85, 85); a4.set_ylim(-20, 40); a4.set_aspect('equal')
    a4.set_title('B  open: fins out through the open windows', fontsize=7.0)
    # open state mini view of the fin zone
    box(a4, -33.02, -32.5, -20, 40, '#cfcfcf', alpha=1); box(a4, 32.5, 33.02, -20, 40, '#cfcfcf', alpha=1)
    box(a4, -32.2, -29.9, 0, 40, GREEN); box(a4, 29.9, 32.2, 0, 40, GREEN)
    box(a4, -79, -25, 2.7, 5.1, '#2f9a63', alpha=.95); box(a4, 25, 79, 2.7, 5.1, '#2f9a63', alpha=.95)
    plt.suptitle('V5 sketch 2 (concept, not CAD): module bolts to the BT80 transition from the outside; BT70 side untouched', fontsize=9, y=0.985)
    fig.savefig(png, dpi=170); fig.savefig(pdf); plt.close(fig)


if __name__ == '__main__':
    d = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'docs')
    sketch(F.OUT + 'v5_sketch2.png', os.path.join(d, 'V5_sketch2_fasteners.pdf')); print('ok')
