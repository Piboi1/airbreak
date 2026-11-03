"""Concept drawings: one BT80 tube cut once, swappable module and head inserted from the top.
Tube coordinate z_t = module-frame z + 10 (z_t = 0 at the module seat, the base-ring top at module z -10)."""
import math, os
import numpy as np
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, Wedge, FancyArrowPatch
import figures as F

R_OD, R_ID, R_MOD = 33.02, 32.5, 32.2
BLUE, GREEN, TAN, GREY = '#4f8fd8', '#4caf7a', '#c8a46a', '#9aa0a6'
WIN_Z0, WIN_Z1 = 1.0, 64.5            # window, z_t: measured on the V4 reference tube, z -9.0 .. 54.5 in the module frame
WIN_W = 38.6                          # 67 deg at R33.02 (measured on the V4 reference tube)


def box(ax, x0, x1, z0, z1, col, alpha=.85, ec='k', lw=.6, label=None, fs=6.0, tc='k', ls='-', hatch=None):
    ax.add_patch(Rectangle((x0, z0), x1 - x0, z1 - z0, fc=col, ec=ec, lw=lw, alpha=alpha, ls=ls, hatch=hatch))
    if label:
        ax.text((x0 + x1) / 2, (z0 + z1) / 2, label, fontsize=fs, ha='center', va='center', color=tc)


def architecture():
    fig, ax = plt.subplots(1, 1, figsize=(10.6, 9.4))
    TOP = 112.0
    # tube wall with windows (section through az 0 / 180)
    for sx in (-1, 1):
        x0, x1 = sorted((sx * R_ID, sx * R_OD))
        box(ax, x0, x1, -8, WIN_Z0, '#cfcfcf', alpha=1); box(ax, x0, x1, WIN_Z1, TOP, '#cfcfcf', alpha=1)
        ax.add_patch(Rectangle((x0 - 0.2, WIN_Z0), x1 - x0 + 0.4, WIN_Z1 - WIN_Z0, fc='white', ec='#c62828', lw=.8, ls='--'))
    ax.text(36, 30, 'window 38.6 x 63.5\n(cut once in the tube)', fontsize=6.4, color='#c62828')
    # base ring bonded in the tube bottom
    for sx in (-1, 1):
        x0, x1 = sorted((sx * 26.5, sx * R_ID)); box(ax, x0, x1, -8, 0, TAN)
    ax.text(-62, -4, 'base ring, bonded in the tube\n(the module seat, stays)', fontsize=6.2, color='#8a6a30')
    # module insert
    for sx in (-1, 1):
        x0, x1 = sorted((sx * 29.9, sx * R_MOD)); box(ax, x0, x1, 0, 68.8, GREEN)
    box(ax, -29.9, 29.9, 0, 2, GREEN)
    box(ax, -5, 5, 3.6, 54.6, '#7fd1a0'); box(ax, -9, 9, 43.6, 54.6, '#7fd1a0'); box(ax, -28, 28, 32.5, 38, '#7fd1a0')
    ax.text(-62, 32, 'MODULE insert (green)\nhousing, rotor, fins, caps\nOD 64.4 in the 65.0 bore\n(0.3 mm clear), rests on\nthe base ring, 68.8 long', fontsize=6.3, color='#2a7a52')
    # head insert
    for sx in (-1, 1):
        x0, x1 = sorted((sx * 29.9, sx * R_MOD)); box(ax, x0, x1, 68.8, 92.8, BLUE)
    box(ax, -29.4, 29.4, 55.2, 56.6, BLUE, alpha=.5); box(ax, -6.1, 6.1, 55.2, 77.9, GREY, label='SG90')
    box(ax, -29.9, 29.9, 78.5, 80.0, BLUE, alpha=.5); box(ax, -21, 2, 80, 92, '#e3c34a', label='battery'); box(ax, 2.5, 29.5, 80, 90.8, '#9a6fd1', label='Mercury'); box(ax, -29.9, 29.9, 95, 99, BLUE, alpha=.6)
    ax.text(-62, 85, 'HEAD insert (blue)\nservo, Mercury, regulator,\nbattery; rests on the module\ntop and clamps it', fontsize=6.3, color='#1f5fa8')
    # holes
    for z, lab in ((22, 'index / retention screw (module)'), (74.8, 'head screws x4 (heat-set inserts)')):
        ax.add_patch(Circle((R_OD + 0.6, z), 1.5, fc='#444')); ax.text(R_OD + 3, z, lab, fontsize=5.8, va='center')
    ax.text(R_OD + 3, 88, 'switch slot, USB-C window,\n3 vent holes O3', fontsize=5.8, va='center')
    # removal arrows
    ax.annotate('', xy=(68, 110), xytext=(68, 96), arrowprops=dict(arrowstyle='-|>', color=BLUE, lw=2.2)); ax.text(70, 103, '2  head out', fontsize=6.4, color='#1f5fa8')
    ax.annotate('', xy=(68, 62), xytext=(68, 40), arrowprops=dict(arrowstyle='-|>', color=GREEN, lw=2.2)); ax.text(70, 50, '3  module out', fontsize=6.4, color='#2a7a52')
    ax.text(-72, 118, '1  open the top of the tube section (separate it from the upper airframe)', fontsize=6.4)
    ax.plot([-70, 70], [0, 0], color='#c62828', lw=.8, ls=':'); ax.text(-70, 1.5, 'module seat (z_t 0)', fontsize=5.8, color='#c62828')
    ax.annotate('', xy=(-40, 0), xytext=(-40, 112), arrowprops=dict(arrowstyle='<->', lw=.7)); ax.text(-39, 56, 'tube section\n120 mm', fontsize=6, rotation=90, va='center')
    ax.set_xlim(-75, 100); ax.set_ylim(-14, 124); ax.set_aspect('equal'); ax.grid(alpha=.15); ax.tick_params(labelsize=6)
    ax.set_title('One BT80 tube, cut once; the module and the head are inserts (concept, z_t from the module seat)', fontsize=8.5)
    plt.tight_layout(); fig.savefig(F.OUT + 'ins_architecture.png', dpi=190); plt.close(fig)


def windows():
    fig, axs = plt.subplots(1, 3, figsize=(11.8, 4.9))
    def base(ax, title):
        ax.add_patch(Wedge((0, 0), R_OD, 0, 360, width=R_OD - R_ID, fc='#d5d5d5', ec='k', lw=.4))
        for k in range(4):
            c = 90 * k
            ax.add_patch(Wedge((0, 0), R_OD + .3, c - 33.7, c + 33.7, width=R_OD - R_ID + .6, fc='white', ec='none'))
            ax.add_patch(Wedge((0, 0), R_MOD, c - 32.5 + .8, c + 32.5 - .8, width=R_MOD - 29.9, fc=GREEN, ec='k', lw=.4))
            ax.add_patch(Wedge((0, 0), R_MOD, c + 32.5, c + 57.5, width=R_MOD - 29.5, fc='#2f9a63', ec='k', lw=.4))
        ax.set_xlim(-38, 38); ax.set_ylim(-38, 38); ax.set_aspect('equal'); ax.tick_params(labelsize=5); ax.set_title(title, fontsize=7.6)
    base(axs[0], 'S1  windows left open')
    axs[0].text(0, 0, 'fins closed at R32.2,\ninside the tube', fontsize=6.2, ha='center')
    base(axs[1], 'S1+  windows covered by tape')
    for k in range(4):
        c = 90 * k
        axs[1].add_patch(Wedge((0, 0), R_OD + .5, c - 33.7, c + 33.7, width=.35, fc='#e8730c', ec='none'))
    axs[1].text(0, 0, 'foil or Kapton tape over\neach window, fins burst it\nwhen they open', fontsize=6.2, ha='center')
    base(axs[2], 'S2  fin skin to R33.02')
    for k in range(4):
        c = 90 * k
        axs[2].add_patch(Wedge((0, 0), R_OD, c - 32.5 + .8, c + 32.5 - .8, width=R_OD - R_ID, fc='#c62828', ec='k', lw=.4, alpha=.8))
    axs[2].text(0, 0, 'skin sits in the tube wall:\nthe module cannot slide in\nalong the tube', fontsize=6.2, ha='center', color='#c62828')
    plt.tight_layout(); fig.savefig(F.OUT + 'ins_windows.png', dpi=190); plt.close(fig)


def clash():
    fig, axs = plt.subplots(1, 2, figsize=(10.6, 4.8))
    for ax, skin in zip(axs, (False, True)):
        box(ax, R_ID, R_OD, -4, WIN_Z0, '#cfcfcf', alpha=1); box(ax, R_ID, R_OD, WIN_Z1, 70, '#cfcfcf', alpha=1)
        ax.add_patch(Rectangle((R_ID - 0.1, WIN_Z0), R_OD - R_ID + .2, WIN_Z1 - WIN_Z0, fc='white', ec='#c62828', lw=.7, ls='--'))
        box(ax, 29.9, R_MOD, 0, 68.8, GREEN, alpha=.5)
        box(ax, 29.9, R_MOD, 6, 62, '#4caf7a')
        if skin:
            box(ax, R_ID, R_OD, 6, 62, '#c62828', alpha=.8)
            ax.annotate('', xy=(35.5, 24), xytext=(35.5, 8), arrowprops=dict(arrowstyle='-|>', lw=1.5))
            ax.text(36, 14, 'module moves up\nor down along\nthe tube', fontsize=6.2)
            ax.plot([R_ID + .2, R_OD - .2], [19, 21], color='k', lw=0); ax.text(24.5, 62, 'fin skin R32.5..33.02 hits the\ntube wall below the window', fontsize=6.4, color='#c62828')
            ax.plot([R_ID - 1, R_OD + 1], [WIN_Z0 - .5, WIN_Z0 - .5], color='#c62828', lw=2.0)
            ax.set_title('S2: fin with its own skin: blocked on insertion', fontsize=8)
        else:
            ax.annotate('', xy=(35.5, 24), xytext=(35.5, 8), arrowprops=dict(arrowstyle='-|>', lw=1.5))
            ax.text(36, 14, 'module moves up\nor down along\nthe tube', fontsize=6.2)
            ax.text(24.5, 62, 'fin shell stays inside R32.2:\npasses the tube freely', fontsize=6.4, color='#2a7a52')
            ax.set_title('S1: fin without skin: slides in', fontsize=8)
        ax.set_xlim(24, 44); ax.set_ylim(-2, 72); ax.set_aspect('equal'); ax.tick_params(labelsize=6); ax.grid(alpha=.15)
    plt.tight_layout(); fig.savefig(F.OUT + 'ins_clash.png', dpi=190); plt.close(fig)


def swap():
    fig, axs = plt.subplots(1, 5, figsize=(11.8, 5.6))
    steps = ['1 open the top end of\nthe tube section', '2 unscrew the 4 head\nscrews, lift the head', '3 lift the module out\n(2 index screws)', '4 drop in the new\nmodule: holes line up,\nit rests on the base ring', '5 head back in, 4\nscrews, close the top']
    for i, ax in enumerate(axs):
        for sx in (-1, 1):
            x0, x1 = sorted((sx * R_ID, sx * R_OD)); box(ax, x0, x1, -8, 112 if i != 0 else 112, '#cfcfcf', alpha=1)
            x0, x1 = sorted((sx * 26.5, sx * R_ID)); box(ax, x0, x1, -8, 0, TAN)
        if i in (0, 1):
            for sx in (-1, 1):
                x0, x1 = sorted((sx * 29.9, sx * R_MOD)); box(ax, x0, x1, 0, 68.8, GREEN)
        if i == 0:
            for sx in (-1, 1):
                x0, x1 = sorted((sx * 29.9, sx * R_MOD)); box(ax, x0, x1, 68.8, 92.8, BLUE)
            ax.text(0, 118, 'upper airframe\nlifts off', fontsize=6, ha='center', color='#555')
            ax.annotate('', xy=(0, 130), xytext=(0, 114), arrowprops=dict(arrowstyle='-|>', lw=1.4))
        if i == 1:
            for sx in (-1, 1):
                x0, x1 = sorted((sx * 29.9, sx * R_MOD)); box(ax, x0, x1, 68.8 + 40, 92.8 + 40, BLUE)
            ax.annotate('', xy=(0, 125), xytext=(0, 100), arrowprops=dict(arrowstyle='-|>', color=BLUE, lw=1.8))
        if i == 2:
            for sx in (-1, 1):
                x0, x1 = sorted((sx * 29.9, sx * R_MOD)); box(ax, x0, x1, 40, 108.8, GREEN)
            ax.annotate('', xy=(0, 125), xytext=(0, 112), arrowprops=dict(arrowstyle='-|>', color=GREEN, lw=1.8))
        if i == 3:
            for sx in (-1, 1):
                x0, x1 = sorted((sx * 29.9, sx * R_MOD)); box(ax, x0, x1, 12, 80.8, GREEN, alpha=.6)
            ax.annotate('', xy=(0, 4), xytext=(0, 26), arrowprops=dict(arrowstyle='-|>', color=GREEN, lw=1.8))
        if i == 4:
            for sx in (-1, 1):
                x0, x1 = sorted((sx * 29.9, sx * R_MOD)); box(ax, x0, x1, 0, 68.8, GREEN)
                box(ax, x0, x1, 68.8, 92.8, BLUE)
            box(ax, -29.9, 29.9, 95, 99, BLUE, alpha=.6)
        ax.set_xlim(-45, 45); ax.set_ylim(-12, 135); ax.set_aspect('equal'); ax.axis('off'); ax.set_title(steps[i], fontsize=6.6)
    plt.tight_layout(); fig.savefig(F.OUT + 'ins_swap.png', dpi=190); plt.close(fig)


def template_pdf(path):
    C = 2 * math.pi * R_OD; H = 132.0
    arc = lambda az: math.radians((az + 45) % 360) * R_OD      # sheet starts at az -45 (middle of a strip)
    fig = plt.figure(figsize=(297 / 25.4, 210 / 25.4)); ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, 297); ax.set_ylim(0, 210); ax.axis('off')
    x0, y0 = 45.0, 40.0                        # sheet origin; y = z_t + 12 (bottom edge of the tube = z_t -12)
    Y = lambda zt: y0 + zt + 12.0
    ax.add_patch(Rectangle((x0, y0), C, H, fc='none', ec='k', lw=.8))
    for k in range(4):
        xc = x0 + arc(90 * k)
        ax.add_patch(Rectangle((xc - WIN_W / 2, Y(WIN_Z0)), WIN_W, WIN_Z1 - WIN_Z0, fc='#e8e8e8', ec='k', lw=1.0))
        ax.text(xc, Y(33), 'WINDOW\n38.6 x 63.5', fontsize=6.5, ha='center', va='center')
    def hole(az, zt, d, lab=None):
        xc = x0 + arc(az); ax.add_patch(Circle((xc, Y(zt)), d / 2, fc='none', ec='k', lw=1.0)); ax.plot([xc - 4, xc + 4], [Y(zt)] * 2, color='k', lw=.4); ax.plot([xc] * 2, [Y(zt) - 4, Y(zt) + 4], color='k', lw=.4)
        if lab: ax.text(xc + 4.5, Y(zt) + 3.5, lab, fontsize=5.0)
    hole(45, 22, 3.4, 'index M3'); hole(225, 22, 3.4, 'index M3')
    for az in (45, 135, 250, 290): hole(az, 74.8, 3.4, f'head M3 az {az}')
    for az in (90, 210, 330): hole(az, 87, 3.0, 'vent O3')
    xc = x0 + arc(0); ax.add_patch(Rectangle((xc - 6, Y(86) - 2), 12, 4, fc='none', ec='k', lw=1.0)); ax.text(xc + 7, Y(86), 'switch slot 12 x 4', fontsize=5.0, va='center')
    xc = x0 + arc(180); ax.add_patch(Rectangle((xc - 5, Y(88) - 2.5), 10, 5, fc='none', ec='k', lw=1.0)); ax.text(xc + 6, Y(88), 'USB-C window 10 x 5', fontsize=5.0, va='center')
    ax.plot([x0, x0 + C], [Y(0), Y(0)], color='#c62828', lw=.8, ls='--'); ax.text(x0 + 1.5, Y(0) + 1.5, 'module seat (z_t 0): the top of the transition; its 12 mm spigot is glued in the tube bottom', fontsize=5.4, color='#c62828')
    for mm_ in range(0, int(C) + 1, 10):
        ax.plot([x0 + mm_] * 2, [y0 - 3, y0], color='k', lw=.5); ax.text(x0 + mm_, y0 - 7, str(mm_), fontsize=4.8, ha='center')
    for mm_ in range(0, int(H) + 1, 10):
        ax.plot([x0 - 3, x0], [y0 + mm_] * 2, color='k', lw=.5); ax.text(x0 - 5, y0 + mm_, str(mm_), fontsize=4.8, ha='right', va='center')
    ax.text(x0 + C / 2, y0 + H + 8, 'V5 insert concept: BT80 drilling and cutting template 1:1 (OD 66.04). Wrap the long edge round the tube, tape, mark through the centres.', fontsize=7.2, ha='center')
    ax.text(x0, y0 + H + 16, 'Bottom edge of this sheet = the bottom end of the tube. The left and right edges meet at the middle of a strip. Heights are marked from the tube bottom.', fontsize=6.0)
    ax.plot([20, 120], [22, 22], color='k', lw=2); ax.plot([20, 20], [20, 24], color='k', lw=1); ax.plot([120, 120], [20, 24], color='k', lw=1)
    ax.text(70, 26, '100 mm check bar: print at 100 %, measure it before you cut', fontsize=6.5, ha='center')
    ax.text(20, 11, 'Concept hole positions (head screws at 45/135/250/290 deg, index screws, vents, switch, USB-C) come from the V5 drawings, not from tested CAD: move them with the real parts in hand.', fontsize=5.6)
    fig.savefig(path); plt.close(fig)


if __name__ == '__main__':
    architecture(); windows(); clash(); swap()
    template_pdf(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'docs', 'V5_insert_tube_template_1to1.pdf'))
    print('ok')
