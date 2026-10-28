import math
import numpy as np
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, Wedge, Arc
import figures as F

OD = 66.04
CIRC = math.pi * OD


def az_to_x(a):
    return (a % 360) / 360 * CIRC


def tube_panel(ax, length, title, holes=(), windows=(), pieces=(), end_label='END THAT MEETS THE AIRBRAKE (d = 0)', down=True):
    """Unrolled tube. y = distance d from the airbrake end (d grows downward)."""
    ax.add_patch(Rectangle((0, 0), CIRC, length, fill=False, lw=2, ec='k'))
    for a in range(0, 360, 15):
        x = az_to_x(a)
        ax.plot([x, x], [0, -3], 'k', lw=0.8)
        if a % 45 == 0:
            ax.text(x, -6, f'{a}°', ha='center', va='bottom', fontsize=8)
    for (az0, az1, d0, d1, label, col) in windows:
        x0, x1 = az_to_x(az0), az_to_x(az1)
        if x1 < x0:
            ax.add_patch(Rectangle((x0, d0), CIRC - x0, d1 - d0, fc=col, ec='k', alpha=.5))
            ax.add_patch(Rectangle((0, d0), x1, d1 - d0, fc=col, ec='k', alpha=.5))
        else:
            ax.add_patch(Rectangle((x0, d0), x1 - x0, d1 - d0, fc=col, ec='k', alpha=.5))
    for (az, d, label) in holes:
        x = az_to_x(az)
        ax.add_patch(Circle((x, d), 1.7, fc='white', ec='crimson', lw=1.6))
        ax.plot([x - 4, x + 4], [d, d], color='crimson', lw=.6); ax.plot([x, x], [d - 4, d + 4], color='crimson', lw=.6)
        ax.annotate(label, (x, d), xytext=(x + 3, d - 5), fontsize=7, color='crimson')
    ax.set_xlim(-12, CIRC + 12); ax.set_ylim(length + 6, -14)
    ax.set_aspect('equal'); ax.set_title(title, fontsize=11, loc='left')
    ax.set_xlabel(f'around the tube (mm); full circumference = {CIRC:.1f} mm; azimuth 0° = fin 1, counter-clockwise seen from the nose', fontsize=8)
    ax.set_ylabel('d from airbrake end (mm)', fontsize=8)
    ax.text(CIRC / 2, -11, end_label, ha='center', fontsize=7, color='gray')
    ax.tick_params(labelsize=7)


def _save(fig, path):
    fig.tight_layout(); fig.savefig(path, dpi=220); plt.close(fig)


def v1_templates(prefix):
    fig, ax = plt.subplots(figsize=(7.1, 2.4))
    tube_panel(ax, 43, 'V1 upper BT80 tube (butts the housing top at z=67): 4 x \u00d83.4 holes for M3x6',
               holes=[(a, 9.0, f'{a}\u00b0, d=9') for a in (0, 90, 180, 270)])
    _save(fig, prefix + 'v1_upper_tube.png')
    fig, ax = plt.subplots(figsize=(7.1, 3.0))
    holes_l = [(a, 11.5, f'{a}\u00b0, d=11.5') for a in (90, 200, 340)] + [(a, 52.2, f'{a}\u00b0, d=52.2') for a in (45, 135, 225, 315)]
    tube_panel(ax, 85, 'Lower BT80 tube (butts the housing bottom at z=-15)\n3 x \u00d83.4 dock-ring holes + 4 x \u00d83.4 cradle holes (M3x10)', holes=holes_l)
    _save(fig, prefix + 'lower_tube.png')


def v2_templates(prefix):
    fig, ax = plt.subplots(figsize=(7.1, 4.4))
    wins = [((a - 33.5) % 360, (a + 33.5) % 360, 1.8, 65.6, '', '#f4d29a') for a in (0, 90, 180, 270)]
    holes = []
    for s in range(4):
        for lv in range(2):
            az = (45 + 90 * s) % 360
            d_ = 23.0 if lv == 0 else 47.0
            holes.append((az, d_, f'{az:.0f}\u00b0, d={d_:g}'))
    tube_panel(ax, 100, 'V2 upper BT80 tube (butts the 4 mm stop ring at z=-11)', holes=holes, windows=wins)
    for a in (0, 90, 180, 270):
        x0 = az_to_x(a - 32.5)
        if x0 + 37.5 > CIRC:
            ax.add_patch(Rectangle((x0, 19), CIRC - x0, 42, fill=False, ec='teal', lw=1.4, ls='--'))
            ax.add_patch(Rectangle((0, 19), 37.5 - (CIRC - x0), 42, fill=False, ec='teal', lw=1.4, ls='--'))
        else:
            ax.add_patch(Rectangle((x0, 19), 37.5, 42, fill=False, ec='teal', lw=1.4, ls='--'))
    ax.text(CIRC * .02, 74, 'orange = window to cut (38.6 x 63.8); dashed teal = 37.5 x 42 cut-out trimmed from the waste and glued to the fin\n'
            'at the same azimuth (fin 1 = 0\u00b0, fin 2 = 90\u00b0 ...); red = 8 x \u00d83.4 holes for M3x6, centred on each strip', fontsize=6.5, color='teal')
    _save(fig, prefix + 'v2_upper_tube.png')


def v2_radial(path):
    fig, ax = plt.subplots(figsize=(6.4, 5.6))
    def arc(r0, r1, a0, a1, fc, label=None, alpha=1):
        ax.add_patch(Wedge((0, 0), r1, a0, a1, width=r1 - r0, fc=fc, ec='k', lw=.8, alpha=alpha, label=label))
    arc(29.9, 32.3, -32.5, 32.5, '#e8762b', 'fin shell (printed) R29.9-32.3')
    arc(32.5, 33.02, -32.5, 32.5, '#e1c98b', 'glued BT80 cut-out R32.5-33.02')
    arc(32.5, 33.02, 34.2, 55.8, '#c9b06b', 'BT80 tube (strip between slits)')
    arc(26.8, 32.3, 34.5, 55.5, '#3f7fb0', 'support strip (printed) R26.8-32.3')
    arc(0, 0.01, 0, 1, 'k')
    ax.plot([0, 40], [0, 40], 'k--', lw=.6)
    ax.text(31, 4, 'fin 1 (0°)', fontsize=8)
    ax.text(22, 24.5, 'seam\n(45°)', fontsize=9, rotation=-45)
    for r, t, ang in ((32.3, 'R32.3 = 64.6 mm OD (your sleeve OD)', 12), (32.5, 'tube ID R32.5 (65.0 mm)', 20), (33.02, 'tube OD R33.02 (66.04 mm)', 28)):
        a = math.radians(ang)
        ax.annotate(t, (r * math.cos(a), r * math.sin(a)), (36 * math.cos(a) + 3, 36 * math.sin(a) + 2), arrowprops=dict(arrowstyle='-', lw=.7), fontsize=8)
    ax.set_xlim(20, 44); ax.set_ylim(-4, 40); ax.set_aspect('equal')
    ax.set_title('V2 radial stack-up (section, quarter view): 0.2 mm glue gap between fin and tube piece', fontsize=10)
    ax.legend(loc='lower left', fontsize=8)
    ax.grid(alpha=.2)
    fig.tight_layout(); fig.savefig(path, dpi=220); plt.close(fig)


if __name__ == '__main__':
    v1_templates(F.OUT)
    v2_templates(F.OUT)
    v2_radial(F.OUT + 'v2_radial.png')
    print('ok')
