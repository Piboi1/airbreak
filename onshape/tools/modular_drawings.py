"""Concept drawings for the modular V5 idea: swappable airbrake module + reusable electronics head.
Dimensions come from the V4 model; V5 values are concept numbers (not yet in CAD)."""
import math, os
import numpy as np
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, FancyArrowPatch, Polygon
import figures as F

HEAD, MOD, BASE, TUBE = '#4f8fd8', '#4caf7a', '#c8a46a', '#7a7a7a'
SERVO, BATT, MERC, REG = '#9aa0a6', '#e3c34a', '#9a6fd1', '#e57fa0'


def dim(ax, x, z0, z1, text, off=0, fs=6.2, col='k'):
    ax.annotate('', xy=(x + off, z1), xytext=(x + off, z0), arrowprops=dict(arrowstyle='<->', color=col, lw=.8))
    ax.text(x + off + 1.2, (z0 + z1) / 2, text, fontsize=fs, va='center', color=col)


def box(ax, x0, x1, z0, z1, col, alpha=.85, ec='k', lw=.6, label=None, fs=6.0, tc='k', ls='-'):
    ax.add_patch(Rectangle((x0, z0), x1 - x0, z1 - z0, fc=col, ec=ec, lw=lw, alpha=alpha, ls=ls))
    if label:
        ax.text((x0 + x1) / 2, (z0 + z1) / 2, label, fontsize=fs, ha='center', va='center', color=tc)


def sym(ax, r, z0, z1, col, label=None, **kw):
    box(ax, -r, r, z0, z1, col, label=label, **kw)


def elevation_stack(ax, kind, ox=0.0):
    """kind 'v4' or 'v5': half-width drawing around x=ox (both sides)."""
    def b(x0, x1, z0, z1, col, **k): box(ax, ox + x0, ox + x1, z0, z1, col, **k)
    if kind == 'v4':
        # lower tube, upper tube
        b(-33.5, -32.5, -97, -15, '#dddddd', alpha=1); b(32.5, 33.5, -97, -15, '#dddddd', alpha=1)
        b(-33.5, -32.5, -11, 100, '#dddddd', alpha=1); b(32.5, 33.5, -11, 100, '#dddddd', alpha=1)
        # transition ring
        b(-32.3, -23.5, -45.5, -37.5, BASE); b(23.5, 32.3, -45.5, -37.5, BASE)
        # housing
        b(-32.3, -29.9, -37.5, 58.8, MOD); b(29.9, 32.3, -37.5, 58.8, MOD)
        # bay
        b(-29.9, 29.9, -37.5, -10, HEAD, alpha=.35); ax.text(ox, -24, 'electronics\nbay (sled)', fontsize=6, ha='center', va='center')
        # rotor + servo
        b(-5, 5, -6.4, 44.6, '#7fd1a0'); b(-9, 9, 33.6, 44.6, '#7fd1a0'); b(-28, 28, 22.5, 28, '#7fd1a0')
        b(-6.1, 6.1, 45.2, 67.9, SERVO, label='SG90')
    else:
        # lower tube
        b(-33.5, -32.5, -97, -22, '#dddddd', alpha=1); b(32.5, 33.5, -97, -22, '#dddddd', alpha=1)
        # base ring (stays in the rocket)
        b(-32.3, -26.5, -30, -22, BASE); b(26.5, 32.3, -30, -22, BASE)
        # module skin + housing
        b(-33.5, -32.5, -22, 70.8, '#dddddd', alpha=1); b(32.5, 33.5, -22, 70.8, '#dddddd', alpha=1)
        b(-32.3, -29.9, -22, 58.8, MOD); b(29.9, 32.3, -22, 58.8, MOD)
        b(-29.9, 29.9, -10, -8, MOD)
        b(-5, 5, -6.4, 44.6, '#7fd1a0'); b(-9, 9, 33.6, 44.6, '#7fd1a0'); b(-28, 28, 22.5, 28, '#7fd1a0')
        # head: sleeve inside the skin top, cup around the servo, electronics layer, head tube
        b(-32.3, -29.9, 58.8, 82.8, HEAD); b(29.9, 32.3, 58.8, 82.8, HEAD)
        b(-33.5, -32.5, 70.8, 91, '#cfdff2', alpha=1); b(32.5, 33.5, 70.8, 91, '#cfdff2', alpha=1)
        b(-29.4, 29.4, 45.2, 46.6, HEAD, alpha=.5)        # cup floor with servo mount
        b(-6.1, 6.1, 45.2, 67.9, SERVO, label='SG90')
        b(-29.9, 29.9, 68.5, 70.0, HEAD, alpha=.5)         # plate
        b(-21, 2, 70.0, 82.0, BATT, label='battery'); b(2.5, 29.5, 70.0, 80.8, MERC, label='Mercury')
        b(-29.9, 29.9, 85, 89, HEAD, alpha=.6)


def drawing1():
    fig, axs = plt.subplots(1, 2, figsize=(11.0, 8.6))
    for ax, kind, ttl in ((axs[0], 'v4', 'V4 today: electronics in the bay at the bottom'), (axs[1], 'v5', 'Modular concept: electronics head on top')):
        elevation_stack(ax, kind)
        ax.set_xlim(-62, 95); ax.set_ylim(-100, 105); ax.set_aspect('equal'); ax.grid(alpha=.2); ax.set_title(ttl, fontsize=8.5); ax.tick_params(labelsize=6)
    ax = axs[0]
    dim(ax, 35, -37.5, 67.9, '105.4 mm\nbay to servo top', off=14); ax.text(-60, 80, 'bay wiring, servo cable and\nbattery leads: 5 routed paths', fontsize=6.2, color='#aa3333')
    ax = axs[1]
    dim(ax, 35, -22, 58.8, 'module 80.8 mm', off=3); dim(ax, 35, 58.8, 89, 'head above module', off=3)
    dim(ax, 35, -22, 89, '111 mm overall', off=22)
    ax.text(-60, 100, 'HEAD (blue): servo cup, servo, Mercury,\nregulator, battery, switch, USB-C, vents', fontsize=6.2, color='#1f5fa8')
    ax.text(-60, 38, 'MODULE (green): housing,\nrotor, fins, catch caps,\nslit skin: the part that breaks', fontsize=6.2, color='#2a7a52')
    ax.text(-60, -50, 'BASE (tan): ring bonded in the\nlower tube, stays', fontsize=6.2, color='#8a6a30')
    ax.text(-60, 62, 'no wire crosses\nthe joints', fontsize=6.6, color='#2a7a52', weight='bold')
    plt.tight_layout(); fig.savefig(F.OUT + 'v5_stack_compare.png', dpi=190); plt.close(fig)


def drawing2():
    fig, ax = plt.subplots(1, 1, figsize=(10.4, 9.2))
    gap = 28
    # base + lower tube
    box(ax, -33.5, -32.5, -97, -22, '#dddddd', alpha=1); box(ax, 32.5, 33.5, -97, -22, '#dddddd', alpha=1)
    box(ax, -32.3, -26.5, -30, -22, BASE); box(ax, 26.5, 32.3, -30, -22, BASE)
    # module lifted by gap
    g = gap
    def m(x0, x1, z0, z1, col, **k): box(ax, x0, x1, z0 + g, z1 + g, col, **k)
    m(-33.5, -32.5, -22, 70.8, '#dddddd', alpha=1); m(32.5, 33.5, -22, 70.8, '#dddddd', alpha=1)
    m(-32.3, -29.9, -22, 58.8, MOD); m(29.9, 32.3, -22, 58.8, MOD); m(-29.9, 29.9, -10, -8, MOD)
    m(-5, 5, -6.4, 44.6, '#7fd1a0'); m(-9, 9, 33.6, 44.6, '#7fd1a0'); m(-28, 28, 22.5, 28, '#7fd1a0')
    # head lifted by 2*gap
    h = 2 * gap + 22
    def hd(x0, x1, z0, z1, col, **k): box(ax, x0, x1, z0 + h, z1 + h, col, **k)
    hd(-32.3, -29.9, 58.8, 82.8, HEAD); hd(29.9, 32.3, 58.8, 82.8, HEAD)
    hd(-33.5, -32.5, 70.8, 91, '#cfdff2', alpha=1); hd(32.5, 33.5, 70.8, 91, '#cfdff2', alpha=1)
    hd(-29.4, 29.4, 45.2, 46.6, HEAD, alpha=.5); hd(-6.1, 6.1, 45.2, 67.9, SERVO, label='SG90')
    hd(-29.9, 29.9, 68.5, 70.0, HEAD, alpha=.5); hd(-21, 2, 70.0, 82.0, BATT, label='battery'); hd(2.5, 29.5, 70.0, 80.8, MERC, label='Mercury'); hd(-29.9, 29.9, 85, 89, HEAD, alpha=.6)
    # interface planes
    for z, name, col in ((58.8 + g + 0, 'I1  head to module  (z 58.8)', '#c62828'), (-22 + 0.0, 'I2  module to base  (z -22)', '#c62828')):
        ax.plot([-62, 62], [z, z], color=col, lw=.9, ls='--')
        ax.text(-62, z + 2.0, name, fontsize=6.6, color=col, weight='bold')
    ax.plot([-62, 62], [91 + h - 0 + 2, 91 + h + 2], color='#c62828', lw=0)
    # arrows
    ax.annotate('', xy=(-52, 58.8 + g + 24), xytext=(-52, 58.8 + g + 2), arrowprops=dict(arrowstyle='-|>', color=HEAD, lw=2.2)); ax.text(-50, 58.8 + g + 13, '1  unscrew I1 (4 x M3),\n    lift the head off', fontsize=6.4, color='#1f5fa8')
    ax.annotate('', xy=(-52, -22 + g + 24 - 8), xytext=(-52, -22 + 4), arrowprops=dict(arrowstyle='-|>', color=MOD, lw=2.2)); ax.text(-50, 0, '2  unscrew I2 (4 x M3),\n    lift the module off', fontsize=6.4, color='#2a7a52')
    ax.text(40, 10, '3  drop in a new module,\n    refit I2, refit the head:\n    horn slides into the hub slot', fontsize=6.4, color='k')
    ax.text(40, -50, 'the base ring and the lower\ntube never move', fontsize=6.4, color='#8a6a30')
    ax.text(40, 135, 'upper airframe: joins the head with the\nsame 4-screw coupler (I3)', fontsize=6.2, color='#555')
    ax.set_xlim(-65, 85); ax.set_ylim(-100, 175); ax.set_aspect('equal'); ax.grid(alpha=.15); ax.tick_params(labelsize=6)
    ax.set_title('Swap procedure (exploded elevation, not to scale between the three groups)', fontsize=8.5)
    plt.tight_layout(); fig.savefig(F.OUT + 'v5_exploded.png', dpi=190); plt.close(fig)


def drawing3():
    fig, axs = plt.subplots(1, 2, figsize=(11.2, 6.4), gridspec_kw={'width_ratios': [1.15, 1]})
    ax = axs[0]
    # detail of I1 and the drive coupling (elevation, z 38..75, x 0..36)
    box(ax, 29.9, 32.3, 38, 58.8, MOD); box(ax, 32.5, 33.5, 30, 70.8, '#dddddd', alpha=1)
    box(ax, 29.9, 32.3, 58.8, 70.8, HEAD); ax.text(34.2, 64.5, 'head sleeve\n12 mm into the skin', fontsize=5.8, va='center')
    ax.plot([33.5, 29.2], [64.8, 64.8], color='#c62828', lw=1.6); ax.text(8.0, 70.5, '4 x M3x5 radial, 90 deg apart (keyed:\none dowel O2.5 at R31, 30 deg off)', fontsize=5.6, color='#c62828')
    # rotor hub + pocket + horn + servo
    box(ax, 0, 9, 33.6, 44.6, '#7fd1a0'); box(ax, 0, 4.5, 41.3, 45.0, 'white', alpha=1, ec='#7fd1a0')
    box(ax, 0, 4.0, 41.5, 43.3, '#e8c547', ec='k'); box(ax, 0, 2.4, 43.3, 45.2, '#e8c547')
    box(ax, 0, 6.1, 45.2, 67.9, SERVO)
    box(ax, 0, 28.8, 45.2, 46.6, HEAD, alpha=.55); ax.text(12.5, 48.2, 'cup floor with the two\nservo ledges (moved from the housing)', fontsize=5.6)
    box(ax, 4.0, 11, 41.5, 43.3, '#e8c547')       # horn arm
    ax.annotate('', xy=(9.5, 44.4), xytext=(13.5, 51), arrowprops=dict(arrowstyle='-', lw=.6)); 
    ax.text(13.6, 52, 'hub slot: 4.4 wide now,\nadd 45 deg lead-in 1.8 x 1.8\n(funnel 8.0 wide at the top)', fontsize=5.6)
    ax.add_patch(Polygon([[4.0, 45.0], [2.2 + 4.0, 45.0 - 0], [4.0, 45.0]], fc='none'))
    ax.text(0.4, 36.0, 'rotor hub', fontsize=5.8, color='#2a7a52'); ax.text(7.6, 60, 'SG90', fontsize=6)
    ax.text(1.0, 31.2, 'keeper: add a lift-off stop (clip or\nprinted collar) so the rotor cannot\nfall out when the head is off', fontsize=5.6, color='#aa3333')
    ax.set_xlim(-1, 52); ax.set_ylim(28, 75); ax.set_aspect('equal'); ax.grid(alpha=.2); ax.tick_params(labelsize=6)
    ax.set_title('I1 detail: coupler sleeve, screws, key and the horn-in-slot drive', fontsize=8)
    # plan of the interface: bolt circle + key + slot angle
    ax = axs[1]
    ax.add_patch(Circle((0, 0), 33.5, fill=False, ec='#999', lw=1.0)); ax.add_patch(Circle((0, 0), 32.3, fill=False, ec=HEAD, lw=1.5)); ax.add_patch(Circle((0, 0), 29.9, fill=False, ec=MOD, lw=1.5))
    for k in range(4):
        a = math.radians(45 + 90 * k); ax.add_patch(Circle((33.0 * math.cos(a), 33.0 * math.sin(a)), 1.7, fc='#c62828', ec='k', lw=.4))
    ka = math.radians(75); ax.add_patch(Circle((31.1 * math.cos(ka), 31.1 * math.sin(ka)), 1.25, fc='k')); ax.text(31 * math.cos(ka) - 2, 31 * math.sin(ka) + 4.5, 'key dowel O2.5', fontsize=6, ha='right')
    ax.plot([-11, 11], [0, 0], color='#e8c547', lw=4); ax.text(0, -3.5, 'horn arm / hub slot', fontsize=6, ha='center')
    ax.add_patch(Rectangle((-6.1, -6.1), 12.2, 12.2, fc='none', ec=SERVO, lw=1.0, ls='--')); ax.text(0, 8, 'servo\n(above)', fontsize=5.8, ha='center', color='#555')
    ax.annotate('rest angle: rotor at its closed stop\n(-3 deg), horn parked at the same angle.\nFunnel absorbs about +-8 deg of error.', xy=(8, 1), xytext=(-37, -37), fontsize=6.0, arrowprops=dict(arrowstyle='-', lw=.5))
    ax.text(-37, 36, 'red: 4 x M3x5 screws, 90 deg apart,\nthrough the skin into the head sleeve', fontsize=6.0, color='#c62828')
    ax.set_xlim(-40, 40); ax.set_ylim(-40, 40); ax.set_aspect('equal'); ax.grid(alpha=.2); ax.tick_params(labelsize=6)
    ax.set_title('I1 plan: screws, key, drive axis', fontsize=8)
    plt.tight_layout(); fig.savefig(F.OUT + 'v5_interface.png', dpi=190); plt.close(fig)


def drawing4():
    fig = plt.figure(figsize=(11.2, 6.8))
    ax = fig.add_axes([0.04, 0.07, 0.40, 0.86])
    # head elevation
    box(ax, -33.5, -32.5, 40, 92, '#cfdff2', alpha=1); box(ax, 32.5, 33.5, 70.8, 92, '#cfdff2', alpha=1)
    box(ax, -33.5, -32.5, 40, 70.8, '#dddddd', alpha=1); box(ax, 32.5, 33.5, 40, 70.8, '#dddddd', alpha=1)
    box(ax, -32.3, -29.9, 58.8, 82.8, HEAD); box(ax, 29.9, 32.3, 58.8, 82.8, HEAD)
    box(ax, -29.4, 29.4, 45.2, 46.6, HEAD, alpha=.5); box(ax, -6.1, 6.1, 45.2, 67.9, SERVO, label='SG90')
    box(ax, -29.9, 29.9, 68.5, 70.0, HEAD, alpha=.5)
    box(ax, -21, 21, 70.0, 82.0, BATT, label='battery 42 x 19 x 12'); box(ax, -15, 15, 70.0, 80.8, MERC, alpha=.0)
    box(ax, -29.9, 29.9, 85, 89, HEAD, alpha=.6)
    ax.text(0, 76, '', fontsize=6)
    ax.annotate('slide switch (arming)\nthrough the tube wall', xy=(33.5, 76), xytext=(36, 64), fontsize=6, arrowprops=dict(arrowstyle='-', lw=.6))
    ax.annotate('USB-C window', xy=(-33.5, 78), xytext=(-60, 88), fontsize=6, arrowprops=dict(arrowstyle='-', lw=.6))
    ax.annotate('3 vent holes O3', xy=(-33.5, 74), xytext=(-60, 66), fontsize=6, arrowprops=dict(arrowstyle='-', lw=.6))
    ax.plot([0, 0], [67.9, 70.0], color='#e8730c', lw=2.0); ax.text(1.2, 68.3, 'servo lead\n~40 mm', fontsize=5.4, color='#e8730c')
    dim(ax, -45, 45.2, 67.9, 'servo\n22.7', off=0); dim(ax, -45, 69, 85, '16', off=0)
    ax.set_xlim(-65, 52); ax.set_ylim(38, 95); ax.set_aspect('equal'); ax.grid(alpha=.15); ax.tick_params(labelsize=6)
    ax.set_title('Head, elevation (concept)', fontsize=8)
    # plan of electronics layer (z 70..85) inside O59.8
    ax = fig.add_axes([0.50, 0.07, 0.47, 0.86])
    ax.add_patch(Circle((0, 0), 33.0, fill=False, ec='#999')); ax.add_patch(Circle((0, 0), 29.9, fill=False, ec=HEAD, lw=1.5))
    ax.add_patch(Rectangle((-21, -20), 42, 19, fc=BATT, ec='k', alpha=.8)); ax.text(0, -10.5, 'battery 42 x 19\n(Spektrum 2S)', fontsize=6.4, ha='center')
    ax.add_patch(Rectangle((-15, 1.6), 30, 16.9, fc=MERC, ec='k', alpha=.7)); ax.text(0, 9.5, 'Mercury V1  30 x 16.9', fontsize=6.4, ha='center')
    ax.add_patch(Rectangle((-24, 3.5), 9, 13, fc=REG, ec='k', alpha=.8)); ax.text(-19.5, 10, 'reg.\n13 x 18\n(side)', fontsize=5.0, ha='center')
    for xy, c in (((-15.5, 18.2), 'k'),):
        pass
    ax.add_patch(Rectangle((-6.1, -6.1), 12.2, 12.2, fc='none', ec=SERVO, ls='--')); ax.text(8.0, -4, 'servo below', fontsize=5.6, color='#555')
    def w(pts, col, lw=1.4): 
        p = np.array(pts); ax.plot(p[:, 0], p[:, 1], color=col, lw=lw)
    w([(0, 0.5), (-3.5, 3.0)], '#222'); w([(0, 0.5), (-1.0, 3.0)], '#1565c0'); w([(0, 0.5), (-12, 6.5), (-15.5, 8)], '#c62828')
    w([(-21, -1), (-21, 3.5)], '#c62828'); w([(-19.5, -1), (-19.5, 3.5)], '#222')
    ax.text(-39, -26, 'wires: servo lead 3 cores (~40 mm) to the Mercury GND and GP6 pads and to the regulator;\nbattery to switch to regulator: ~50 mm. Nothing leaves the head.', fontsize=6.2)
    ax.annotate('slide switch', xy=(29.0, 3), xytext=(33, 12), fontsize=6, arrowprops=dict(arrowstyle='-', lw=.6)); ax.add_patch(Rectangle((28.5, 1.5), 3.4, 3.4, fc='#555'))
    ax.annotate('USB-C end of the Mercury', xy=(-15, 14), xytext=(-39, 27), fontsize=6, arrowprops=dict(arrowstyle='-', lw=.6))
    ax.set_xlim(-42, 42); ax.set_ylim(-30, 38); ax.set_aspect('equal'); ax.grid(alpha=.15); ax.tick_params(labelsize=6)
    ax.set_title('Head, plan of the electronics layer (z 70-85, concept)', fontsize=8)
    fig.savefig(F.OUT + 'v5_head.png', dpi=190); plt.close(fig)


if __name__ == '__main__':
    drawing1(); drawing2(); drawing3(); drawing4(); print('ok')
