"""Final-plan drawings for V5: corrected stack with the BT80 -> BT70 transition, and the transition seat detail."""
import math, os
import numpy as np
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Polygon
import figures as F

R_OD, R_ID, R_MOD = 33.02, 32.5, 32.2
R70 = 56.3 / 2                                   # BT-70 outside radius
BLUE, GREEN, TAN, GREY = '#4f8fd8', '#4caf7a', '#c8a46a', '#9aa0a6'


def box(ax, x0, x1, z0, z1, col, alpha=.85, ec='k', lw=.6, label=None, fs=6.0, tc='k'):
    ax.add_patch(Rectangle((x0, z0), x1 - x0, z1 - z0, fc=col, ec=ec, lw=lw, alpha=alpha))
    if label: ax.text((x0 + x1) / 2, (z0 + z1) / 2, label, fontsize=fs, ha='center', va='center', color=tc)


def layout():
    fig, ax = plt.subplots(1, 1, figsize=(10.6, 10.0))
    CONE = 35.0
    # z_t: seat = 0; transition spigot z_t -12..0; cone z_t -12 - 35 .. -12 ; BT70 below
    for sx in (-1, 1):
        # BT80 tube (airbrake section) with windows
        x0, x1 = sorted((sx * R_ID, sx * R_OD))
        box(ax, x0, x1, -12, 1.0, '#cfcfcf', alpha=1); box(ax, x0, x1, 64.5, 132, '#cfcfcf', alpha=1)
        ax.add_patch(Rectangle((x0 - .2, 1.0), x1 - x0 + .4, 63.5, fc='white', ec='#c62828', lw=.8, ls='--'))
        # upper airframe (BT80, continues)
        box(ax, x0, x1, 132, 160, '#e8e8e8', alpha=1)
        # transition: spigot inside tube, cone outside
        box(ax, *sorted((sx * 26.0, sx * 32.3)), -12, 0, TAN)
        pts = [(sx * R_OD, -12), (sx * R70, -12 - CONE), (sx * (R70 - 2.0), -12 - CONE), (sx * (R_OD - 2.0), -12)]
        ax.add_patch(Polygon(pts, closed=True, fc=TAN, ec='k', lw=.6, alpha=.85))
        # BT70 tube
        box(ax, *sorted((sx * (R70 - 0.5), sx * R70)), -12 - CONE - 55, -12 - CONE, '#bbbbbb', alpha=1)
        # module
        box(ax, *sorted((sx * 29.9, sx * R_MOD)), 0, 68.8, GREEN)
        # head
        box(ax, *sorted((sx * 29.9, sx * R_MOD)), 68.8, 92.8, BLUE)
    box(ax, -29.9, 29.9, 0, 2, GREEN)
    box(ax, -5, 5, 3.6, 54.6, '#7fd1a0'); box(ax, -9, 9, 43.6, 54.6, '#7fd1a0'); box(ax, -28, 28, 32.5, 38, '#7fd1a0')
    box(ax, -29.4, 29.4, 55.2, 56.6, BLUE, alpha=.5); box(ax, -6.1, 6.1, 55.2, 77.9, GREY, label='SG90')
    box(ax, -29.9, 29.9, 78.5, 80.0, BLUE, alpha=.5); box(ax, -21, 2, 80, 92, '#e3c34a', label='battery'); box(ax, 2.5, 29.5, 80, 90.8, '#9a6fd1', label='Mercury'); box(ax, -29.9, 29.9, 95, 99, BLUE, alpha=.6)
    # labels
    ax.text(-78, 150, 'upper airframe, BT80\n(nose, recovery, payload)', fontsize=6.6, color='#555')
    ax.text(-78, 118, 'airbrake section: one BT80 tube,\ncut once (windows, screws,\nvents, switch, USB-C)', fontsize=6.6)
    ax.text(-78, 45, 'MODULE insert', fontsize=6.8, color='#2a7a52', weight='bold'); ax.text(-78, 85, 'HEAD insert', fontsize=6.8, color='#1f5fa8', weight='bold')
    ax.text(-78, -30, 'TRANSITION\nBT80 to BT70\n(the module seat)', fontsize=6.8, color='#8a6a30', weight='bold')
    ax.text(40, -75, 'BT70 tube (OD 56.3,\nID to confirm)', fontsize=6.6, color='#666')
    ax.plot([-80, 80], [0, 0], color='#c62828', lw=.8, ls=':'); ax.text(46, 1.8, 'module seat, z_t 0', fontsize=6, color='#c62828')
    ax.plot([-80, 80], [132, 132], color='#c62828', lw=.8, ls=':'); ax.text(46, 133.8, 'top joint: the section opens here', fontsize=6, color='#c62828')
    ax.annotate('', xy=(-47, -12), xytext=(-47, 132), arrowprops=dict(arrowstyle='<->', lw=.7)); ax.text(-52, 60, 'tube section 144 mm', fontsize=6, rotation=90, va='center')
    ax.annotate('', xy=(58, -12), xytext=(58, -47), arrowprops=dict(arrowstyle='<->', lw=.7)); ax.text(60, -30, 'cone 35\n(to set)', fontsize=5.8)
    ax.set_xlim(-80, 80); ax.set_ylim(-110, 166); ax.set_aspect('equal'); ax.grid(alpha=.15); ax.tick_params(labelsize=6)
    ax.set_title('Final stack, nose up: upper BT80, the airbrake section, the transition, then BT70 (concept, to scale)', fontsize=8.5)
    plt.tight_layout(); fig.savefig(F.OUT + 'fin_layout.png', dpi=190); plt.close(fig)


def seat():
    fig, ax = plt.subplots(1, 1, figsize=(9.6, 5.6))
    # radial section, x = radius, y = z_t
    box(ax, 32.5, 33.02, -12, 20, '#cfcfcf', alpha=1)                               # tube
    box(ax, 26.0, 32.3, -12, 0, TAN)                                                 # spigot + seat ring
    pts = [(33.02, -12), (28.15, -47), (26.15, -47), (31.02, -12)]
    ax.add_patch(Polygon(pts, closed=True, fc=TAN, ec='k', lw=.6, alpha=.85))        # cone wall
    box(ax, 26.0, 32.2, 0, 2.0, GREEN, label='')                                      # module bottom plate on the seat
    box(ax, 29.9, 32.2, 2.0, 20, GREEN)                                               # module wall
    ax.annotate('seat face z_t 0: R26.0 to R32.3\n(module bottom plate rests here)', xy=(29.0, 0), xytext=(8, 12), fontsize=6.2, arrowprops=dict(arrowstyle='-', lw=.5))
    ax.annotate('spigot: OD 64.6, 12 mm long,\nglued into the tube bottom', xy=(30, -7), xytext=(5, -14), fontsize=6.2, arrowprops=dict(arrowstyle='-', lw=.5))
    ax.annotate('cone wall 2 mm, BT80 outside\ndown to BT70 outside (R28.15)', xy=(30.5, -30), xytext=(5, -32), fontsize=6.2, arrowprops=dict(arrowstyle='-', lw=.5))
    ax.annotate('BT70 coupler sleeve below\n(OD = BT70 ID - 0.4, to confirm)', xy=(27.1, -47), xytext=(5, -45), fontsize=6.2, arrowprops=dict(arrowstyle='-', lw=.5))
    ax.annotate('module wall R29.9..32.2', xy=(31.0, 14), xytext=(36, 14), fontsize=6.2, arrowprops=dict(arrowstyle='-', lw=.5))
    ax.annotate('tube R32.5..33.02', xy=(32.8, 6), xytext=(36, 6), fontsize=6.2, arrowprops=dict(arrowstyle='-', lw=.5))
    ax.set_xlim(0, 50); ax.set_ylim(-52, 24); ax.set_aspect('equal'); ax.grid(alpha=.15); ax.tick_params(labelsize=6)
    ax.set_title('Transition top, radial section: the module seat (concept)', fontsize=8.5)
    plt.tight_layout(); fig.savefig(F.OUT + 'fin_seat.png', dpi=190); plt.close(fig)


if __name__ == '__main__':
    layout(); seat(); print('ok')
