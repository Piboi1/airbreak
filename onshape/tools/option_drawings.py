"""Drawings for the two modular-design choices: module skin (cut BT80 vs printed) and swap fastening (screws / thumb screws / collar bayonet).
Dimensions: V4 model for existing parts, concept values for the new ones."""
import math, os
import numpy as np
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, Wedge, Polygon
import figures as F

R_OD, R_ID = 33.02, 32.5          # BT80 outer / inner radius
FIN_HALF = 32.5                   # fin and tube cut-out span 65 deg
BLUE, GREEN, TAN, GREY = '#4f8fd8', '#4caf7a', '#c8a46a', '#9aa0a6'


def ring(ax, r0, r1, a0, a1, col, alpha=.85, ec='k', lw=.4):
    ax.add_patch(Wedge((0, 0), r1, a0, a1, width=r1 - r0, fc=col, ec=ec, lw=lw, alpha=alpha))


def skin_sections():
    fig, axs = plt.subplots(1, 2, figsize=(11.4, 6.0))
    for ax, opt in zip(axs, (1, 2)):
        for k in range(4):
            c = 90 * k
            # fin (65 deg) and strips (25 deg) in azimuth
            if opt == 1:
                ring(ax, 29.9, 32.3, c - 32.5 + 0.8, c + 32.5 - 0.8, GREEN)                # fin shell
                ring(ax, R_ID, R_OD, c - 32.5 + 0.8, c + 32.5 - 0.8, '#f2d9a6')            # glued tube cut-out
                ring(ax, 29.5, 32.3, c + 32.5, c + 57.5, GREEN)                            # housing strip
                ring(ax, R_ID, R_OD, c + 32.5 + 1.5, c + 57.5 - 1.5, '#cfcfcf')            # slit tube strip, kerf gaps
            else:
                ring(ax, 29.9, R_OD, c - 32.5 + 0.7, c + 32.5 - 0.7, GREEN)                # fin printed to the BT80 OD
                ring(ax, 29.5, R_OD, c + 32.5, c + 57.5, '#2f9a63')                        # strip printed to the BT80 OD
        ax.add_patch(Circle((0, 0), 29.5, fc='white', ec='k', lw=.4))
        ax.set_xlim(-38, 38); ax.set_ylim(-38, 38); ax.set_aspect('equal'); ax.tick_params(labelsize=6); ax.grid(alpha=.15)
    axs[0].set_title('Option 1  cut BT80 skin: section at z = 30', fontsize=8.5); axs[1].set_title('Option 2  printed skin: section at z = 30', fontsize=8.5)
    axs[0].annotate('glued tube cut-out\n(R32.5..33.02, 65 deg)', xy=(-9, 32.2), xytext=(-37, 34.5), fontsize=6.4, arrowprops=dict(arrowstyle='-', lw=.5))
    axs[0].annotate('slit tube strip (25 deg),\nkerf gaps about 1.5 deg each side', xy=(23.6, -23.6), xytext=(2, -35.5), fontsize=6.4, arrowprops=dict(arrowstyle='-', lw=.5))
    axs[0].text(-8, 0, 'housing\nR29.5..32.3', fontsize=6.2, ha='center')
    axs[1].annotate('fin printed out to R33.02:\n0.72 mm more than V4', xy=(-9, 32.2), xytext=(-37, 34.5), fontsize=6.4, arrowprops=dict(arrowstyle='-', lw=.5))
    axs[1].annotate('housing strip printed out to R33.02;\ndesigned gap fin to strip 0.4 mm', xy=(23.6, -23.6), xytext=(2, -35.5), fontsize=6.4, arrowprops=dict(arrowstyle='-', lw=.5))
    axs[1].text(-8, 0, 'no tube in the\nfin zone', fontsize=6.2, ha='center')
    plt.tight_layout(); fig.savefig(F.OUT + 'opt_skin_sections.png', dpi=190); plt.close(fig)


def skin_elevation():
    """Developed (unrolled) skin, option 1 pattern and option 2 joints, along the module length (bottom of skin = 0)."""
    L = 92.8; C = 2 * math.pi * R_OD
    fig, axs = plt.subplots(2, 1, figsize=(11.4, 7.6))
    ax = axs[0]
    ax.add_patch(Rectangle((0, 0), C, L, fc='#eeeeee', ec='k', lw=.8))
    arc = lambda deg: math.radians(deg) * R_OD
    for k in range(4):
        xx = arc(45 + 90 * k - 32.5)
        ax.add_patch(Rectangle((xx, 30), arc(65), 42, fc='#f2d9a6', ec='#aa7700', lw=.9, hatch='///'))
    ax.text(arc(45) , 51, 'window\n37.5 x 42\n(cut-out)', fontsize=6.4, color='#775500', ha='center', va='center')
    ax.set_xlim(-12, C + 30); ax.set_ylim(-14, L + 12); ax.set_aspect('equal')
    ax.annotate('', xy=(C + 6, 0), xytext=(C + 6, L), arrowprops=dict(arrowstyle='<->', lw=.7)); ax.text(C + 8, L / 2, '92.8 skin\nlength', fontsize=6.4, va='center')
    ax.annotate('', xy=(C + 20, 30), xytext=(C + 20, 72), arrowprops=dict(arrowstyle='<->', lw=.7)); ax.text(C + 21, 51, '42', fontsize=6.4, va='center')
    ax.annotate('', xy=(0, -6), xytext=(C, -6), arrowprops=dict(arrowstyle='<->', lw=.7)); ax.text(C / 2, -10.5, f'{C:.1f} mm (2 pi R33.02) around the OD', fontsize=6.4, ha='center')
    ax.plot([0, C], [80.8, 80.8], color='#c62828', lw=.8, ls='--'); ax.text(1, 82.2, 'housing top (z 58.8); the 12 mm above it is the head socket', fontsize=6.0, color='#c62828')
    ax.set_title('Option 1: the slit skin, developed flat, starting at the middle of a strip (1:1 template in its own file). Windows 37.5 x 42, centres 51.9 mm apart, strips 14.4 mm', fontsize=7.6)
    ax.axis('off')
    ax = axs[1]
    # elevation of the module outline for option 2 with joint lines
    ax.add_patch(Rectangle((-33.02, 0), 66.04, 92.8, fc='#dff0e6', ec='k', lw=.8))
    for k, (z0, z1) in enumerate(((30, 72),)):
        ax.add_patch(Rectangle((-17.7, z0), 35.4, z1 - z0, fc='#4caf7a', ec='k', lw=.7, alpha=.8)); ax.text(0, 51, 'fin printed with its own skin\n(no glue, no cut tube)', fontsize=6.4, ha='center')
    for z in (0.0, 80.8): ax.plot([-33.02, 33.02], [z, z], color='#c62828', lw=.8, ls='--')
    ax.text(36, 84, 'head joint I1: printed socket 12 mm,\nO66.04 = BT80 OD, so the\nhead tube butts flush', fontsize=6.2, color='#c62828')
    ax.text(36, 4, 'base joint I2: printed 12 mm\nsleeve with the same four pilots', fontsize=6.2, color='#c62828')
    ax.set_xlim(-45, 85); ax.set_ylim(-4, 100); ax.set_aspect('equal'); ax.axis('off')
    ax.set_title('Option 2: the printed module skin, elevation. Outside diameter 66.04 mm all the way, so it mates with the real BT80 above and below', fontsize=8)
    plt.tight_layout(); fig.savefig(F.OUT + 'opt_skin_elev.png', dpi=190); plt.close(fig)


def template_pdf(path):
    """1:1 cutting template, landscape A4: the unrolled skin (option 1)."""
    C = 2 * math.pi * R_OD; L = 92.8
    fig = plt.figure(figsize=(297 / 25.4, 210 / 25.4))
    ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, 297); ax.set_ylim(0, 210); ax.axis('off')
    x0, y0 = 45.0, 62.0
    ax.add_patch(Rectangle((x0, y0), C, L, fc='none', ec='k', lw=.8))
    arc = lambda deg: math.radians(deg) * R_OD
    for k in range(4):
        xx = x0 + arc(45 + 90 * k - 32.5)
        ax.add_patch(Rectangle((xx, y0 + 30), arc(65), 42, fc='#e8e8e8', ec='k', lw=1.0))
        ax.text(xx + arc(65) / 2, y0 + 51, 'CUT OUT\n(keep: glues to the fin)', fontsize=6.5, ha='center', va='center')
    for mm_ in range(0, int(C) + 1, 10):
        ax.plot([x0 + mm_] * 2, [y0 - 3, y0], color='k', lw=.5); ax.text(x0 + mm_, y0 - 7, str(mm_), fontsize=5, ha='center')
    for mm_ in range(0, int(L) + 1, 10):
        ax.plot([x0 - 3, x0], [y0 + mm_] * 2, color='k', lw=.5); ax.text(x0 - 5, y0 + mm_, str(mm_), fontsize=5, ha='right', va='center')
    ax.text(x0 + C / 2, y0 + L + 6, 'V5 module skin, cutting template 1:1 (BT80, outside diameter 66.04 mm): wrap the long edge round the tube, tape, mark through the corners', fontsize=7.5, ha='center')
    ax.text(x0, y0 + L + 14, 'The left and right short edges meet at the middle of a strip (seam): join them on the tube before marking.', fontsize=6.5)
    ax.plot([20, 120], [25, 25], color='k', lw=2); ax.plot([20, 20], [23, 27], color='k', lw=1); ax.plot([120, 120], [23, 27], color='k', lw=1)
    ax.text(70, 29, '100 mm check bar: print at 100 %, measure it before you cut', fontsize=6.5, ha='center')
    ax.text(20, 14, 'Derived from the V4 model (windows 65 deg wide centred on 0/90/180/270, z 8..50 in the housing frame; skin bottom 22 mm below that frame, length 92.8; sheet starts at az -45). Check against your own tube before cutting.', fontsize=5.8)
    fig.savefig(path); plt.close(fig)


def fast_screws():
    fig, ax = plt.subplots(1, 2, figsize=(11.4, 5.4))
    a = ax[0]
    # radial section: skin (outer), head sleeve with insert boss inside; x = radius, y = z
    a.add_patch(Rectangle((32.3, 55), 0.72, 30, fc='#dddddd', ec='k', lw=.6))        # skin (printed option) outer layer
    a.add_patch(Rectangle((29.9, 55), 2.4, 30, fc=BLUE, ec='k', lw=.6))              # head sleeve wall
    a.add_patch(Rectangle((23.0, 66), 6.9, 8, fc=BLUE, ec='k', lw=.6))               # inner boss (7 mm) for the insert
    a.add_patch(Rectangle((23.0, 68.2), 9.9, 3.6, fc='#e8c547', ec='k', lw=.5, alpha=.9)); a.text(24.0, 69.8, 'brass insert', fontsize=5.6)
    a.add_patch(Rectangle((31.8, 69.0), 2.2, 2.0, fc='#444', ec='k', lw=.4))            # screw head
    a.plot([24.0, 31.8], [70.0, 70.0], color='#444', lw=1.8)
    a.text(21.5, 76.5, 'M3x5 button head screw,\nthrough the skin and the sleeve wall\ninto a heat-set M3 insert\n(hole O4.0-4.2 in a 7 mm boss, depth\ninsert length + 1 mm)', fontsize=6.0)
    a.text(33.6, 78, 'skin: 0.52 mm real tube\nor 0.72 mm printed', fontsize=5.8)
    a.text(30.2, 57.0, 'sleeve wall 2.4', fontsize=5.6, color='white', rotation=90)
    a.set_xlim(20, 44); a.set_ylim(54, 88); a.set_aspect('equal'); a.tick_params(labelsize=6); a.grid(alpha=.15)
    a.set_title('Option A: screws, section through the I1 joint (concept)', fontsize=8)
    b = ax[1]
    # plan: four boss positions inside O59.8 and the battery layer
    b.add_patch(Circle((0, 0), 33.02, fill=False, ec='#999')); b.add_patch(Circle((0, 0), 29.9, fill=False, ec=BLUE, lw=1.4))
    for az_ in (45, 135, 250, 290):
        ang = math.radians(az_); b.add_patch(Circle((26.5 * math.cos(ang), 26.5 * math.sin(ang)), 3.4, fc=BLUE, ec='k', lw=.5, alpha=.8)); b.text(33.5 * math.cos(ang), 33.5 * math.sin(ang), f'{az_}', fontsize=5.4, ha='center', va='center')
    b.add_patch(Rectangle((-21, -20), 42, 19, fc='#e3c34a', ec='k', alpha=.6)); b.add_patch(Rectangle((-15, 1.6), 30, 16.9, fc='#9a6fd1', ec='k', alpha=.5))
    b.text(0, -10, 'battery layer', fontsize=6, ha='center'); b.text(0, 10, 'Mercury', fontsize=6, ha='center')
    b.text(-40, 36, 'four 7 mm boss circles at 45, 135, 250 and 290 deg (not 90 deg apart): at 225/315 they would hit\nthe battery corners (R29.0); here they clear the battery by 1.5 mm and the Mercury by 0.7 mm', fontsize=6.0)
    b.set_xlim(-42, 42); b.set_ylim(-42, 42); b.set_aspect('equal'); b.tick_params(labelsize=6); b.grid(alpha=.15)
    b.set_title('Where the four insert bosses sit (plan, z 66..74)', fontsize=8)
    plt.tight_layout(); fig.savefig(F.OUT + 'opt_fast_screws.png', dpi=190); plt.close(fig)


def fast_thumb():
    fig, ax = plt.subplots(1, 2, figsize=(11.4, 5.0))
    a = ax[0]
    a.add_patch(Rectangle((32.3, 55), 0.72, 30, fc='#dddddd', ec='k', lw=.6)); a.add_patch(Rectangle((29.9, 55), 2.4, 30, fc=BLUE, ec='k', lw=.6))
    a.add_patch(Rectangle((23.0, 66), 6.9, 8, fc=BLUE, ec='k', lw=.6)); a.add_patch(Rectangle((23.0, 68.2), 9.9, 3.6, fc='#e8c547', ec='k', lw=.5, alpha=.9))
    a.plot([24.0, 36.5], [70.0, 70.0], color='#444', lw=1.8)
    a.add_patch(Rectangle((33.02, 66.0), 3.5, 8.0, fc='#777', ec='k', lw=.5, alpha=.9, hatch='||'))
    a.add_patch(Rectangle((33.02, 61.0), 3.0, 18.0, fc='none', ec='#c62828', lw=.8, ls='--'))
    a.text(37.0, 78, 'knurled head 8 mm wide, stands\nabout 3.5 mm above the skin\n(typical: check the part you buy)', fontsize=5.8)
    a.text(21.0, 79, 'a flush recess does not fit:\nthe wall at the joint is only\n3.1 mm in total (sleeve 2.4 +\nskin 0.7), a 3 mm recess would\nleave nothing', fontsize=6.0, color='#c62828')
    a.set_xlim(20, 46); a.set_ylim(54, 88); a.set_aspect('equal'); a.tick_params(labelsize=6); a.grid(alpha=.15)
    a.set_title('Option B: captive thumb screw, section (concept)', fontsize=8)
    b = ax[1]
    b.add_patch(Circle((0, 0), 33.02, fill=False, ec='k', lw=1))
    for az_ in (45, 135, 250, 290):
        ang = math.radians(az_); b.add_patch(Circle((33.02 * math.cos(ang), 33.02 * math.sin(ang)), 4.0, fc='#777', ec='k', lw=.5)); b.text(39 * math.cos(ang), 39 * math.sin(ang), f'{az_}', fontsize=5.4, ha='center', va='center')
    b.text(-40, -41, 'same four boss positions as the plain screws: the insert bosses are shared,\nso A and B differ only by the screw. Four heads, each 8 x 3.5 mm proud.', fontsize=6.0)
    b.set_xlim(-45, 45); b.set_ylim(-45, 45); b.set_aspect('equal'); b.tick_params(labelsize=6); b.grid(alpha=.15)
    b.set_title('Plan view: four heads standing proud of the O66.04 skin', fontsize=8)
    plt.tight_layout(); fig.savefig(F.OUT + 'opt_fast_thumb.png', dpi=190); plt.close(fig)


def radial_budget():
    fig, ax = plt.subplots(1, 1, figsize=(11.0, 4.6))
    rows = [('A  screws', [(29.9, 32.3, BLUE, 'head sleeve 2.4'), (32.3, 32.5, 'white', ''), (32.5, 33.02, '#dddddd', 'skin 0.52'), (33.02, 34.7, '#444444', 'button head 1.7')]),
            ('B  thumb screws', [(29.9, 32.3, BLUE, 'head sleeve 2.4'), (32.3, 32.5, 'white', ''), (32.5, 33.02, '#dddddd', 'skin'), (33.02, 36.5, '#777777', 'knurled head 3.5')]),
            ('C  collar bayonet', [(29.9, 31.1, BLUE, 'sleeve 1.2'), (31.1, 31.3, 'white', ''), (31.3, 32.5, '#4f8fd8', 'collar 1.2'), (32.5, 34.0, '#e57fa0', 'lug in a raised socket 1.5')])]
    for k, (name, segs) in enumerate(rows):
        y = 3.4 - 1.5 * k
        for r0, r1, col, lab in segs:
            ax.add_patch(Rectangle((r0, y - 0.3), r1 - r0, 0.6, fc=col, ec='k', lw=.5))
            if lab: ax.text((r0 + r1) / 2, y - 0.38, lab, fontsize=5.8, ha='center', va='top')
        ax.text(29.6, y, name, fontsize=7.2, ha='right', va='center')
    ax.axvline(33.02, color='#c62828', lw=1.2, ls='--'); ax.text(33.1, 4.3, 'BT80 outside, R33.02', fontsize=6.4, color='#c62828')
    ax.axvline(29.9, color='#1f5fa8', lw=1.0, ls=':'); ax.text(29.95, 4.3, 'inside limit R29.9 (electronics)', fontsize=6.2, color='#1f5fa8')
    ax.text(34.4, 0.4, 'C reaches R34.0: a 1 mm raised\nband round the joint, or give up\n1 mm of electronics radius', fontsize=6.2, color='#aa3333', va='center')
    ax.set_xlim(24.5, 41); ax.set_ylim(-0.6, 4.6); ax.set_xlabel('radius from the rocket axis (mm)', fontsize=7); ax.set_yticks([]); ax.tick_params(labelsize=6)
    ax.set_title('Radial budget at the I1 joint: what each option needs between R29.9 and the BT80 outside', fontsize=8.5)
    plt.tight_layout(); fig.savefig(F.OUT + 'opt_radial.png', dpi=190); plt.close(fig)


def fast_bayonet():
    fig, axs = plt.subplots(1, 2, figsize=(11.6, 6.2), gridspec_kw={'width_ratios': [1.25, 1]})
    a = axs[0]
    # developed view of the skin socket: three L-slots (circumference at R32.7)
    C = 2 * math.pi * 32.7; h = 14.0
    a.add_patch(Rectangle((0, 0), 52, h, fc='#eeeeee', ec='k', lw=.8))
    for k in range(1):
        x = k * C / 3 + 8
        a.add_patch(Polygon([[x, h], [x + 7.0, h], [x + 7.0, 6.0], [x + 7.0 + 14.0, 6.0], [x + 7.0 + 14.0, 3.0], [x, 3.0]], closed=True, fc='white', ec='#c62828', lw=1.0))
        a.add_patch(Rectangle((x + 0.5, 3.6), 6.0, 2.0, fc=BLUE, ec='k', lw=.5, alpha=.9)); a.text(x + 3.5, 4.6, 'lug', fontsize=5.2, ha='center')
        a.add_patch(Rectangle((x + 7.0 + 8.0, 3.6), 6.0, 2.0, fc=BLUE, ec='k', lw=.5, alpha=.4)); a.text(x + 7.0 + 11.0, 4.6, 'locked', fontsize=5.2, ha='center')
    a.annotate('', xy=(8, 11.5), xytext=(15, 11.5), arrowprops=dict(arrowstyle='<->', lw=.6)); a.text(11.5, 12.4, '7.0 entry', fontsize=5.8, ha='center')
    a.annotate('', xy=(15, 6.6), xytext=(29, 6.6), arrowprops=dict(arrowstyle='<->', lw=.6)); a.text(22, 7.5, '14 run = 24.5 deg', fontsize=5.8, ha='center')
    a.text(1, -4.2, f'one L-slot of three (68 mm apart round the {C:.0f} mm circle); lugs 6 x 2.0 x 2.2 (concept).\nSlot 3.0 high for a 2.0 lug (0.5 clear each side).', fontsize=6.0)
    a.text(1, 17, 'the collar ring turns, the head body does not:\nthe horn stays engaged and the rotor does not move', fontsize=6.4, color='#c62828')
    a.set_xlim(-2, 54); a.set_ylim(-8, 20); a.set_aspect('equal'); a.axis('off')
    a.set_title('Option C: collar bayonet, developed view of one slot', fontsize=8)
    b = axs[1]
    b.add_patch(Circle((0, 0), 33.02, fill=False, ec='k', lw=1)); b.add_patch(Circle((0, 0), 32.3, fill=False, ec=BLUE, lw=1.4)); b.add_patch(Circle((0, 0), 30.9, fill=False, ec=BLUE, lw=.8, ls='--'))
    for k in range(3):
        ang = math.radians(15 + 120 * k); b.add_patch(Wedge((0, 0), 34.5, math.degrees(ang) - 5, math.degrees(ang) + 5, width=2.7, fc=BLUE, ec='k', lw=.4))
        b.annotate('', xy=(30 * math.cos(ang + .45), 30 * math.sin(ang + .45)), xytext=(30 * math.cos(ang + .05), 30 * math.sin(ang + .05)), arrowprops=dict(arrowstyle='-|>', color='#c62828', lw=1.2))
    b.plot([-11, 11], [0, 0], color='#e8c547', lw=4); b.text(0, -3.5, 'horn stays still', fontsize=6, ha='center')
    b.text(-40, -40, 'sleeve (body) R29.9..30.9 stays put; collar R30.9..32.3 turns 24.5 deg\n(1.4 mm wall: test it). A secondary lock: one M3 screw or a pull pin.', fontsize=6.0)
    b.set_xlim(-42, 42); b.set_ylim(-42, 42); b.set_aspect('equal'); b.tick_params(labelsize=6); b.grid(alpha=.15)
    b.set_title('Plan: collar with three lugs (concept)', fontsize=8)
    plt.tight_layout(); fig.savefig(F.OUT + 'opt_fast_bayonet.png', dpi=190); plt.close(fig)


def twist_problem():
    fig, ax = plt.subplots(1, 1, figsize=(8.6, 3.6))
    ang = np.linspace(-3, 67, 100)
    ax.fill_between([0, 65], 0, 1, color='#e6f2ea', label='rotor travel 0-65 deg')
    ax.axvline(-3, color='k', lw=1); ax.text(-2.7, 0.9, 'closed stop -3', fontsize=6.2)
    ax.axvline(15, color='#c62828', lw=1.4); ax.text(15.5, 0.82, 'fin latch frees at about 15 deg of rotor travel', fontsize=6.4, color='#c62828')
    ax.axvline(26, color='#aa6600', lw=1.2); ax.text(26.5, 0.62, 'cam first touches at about 26 deg', fontsize=6.4, color='#aa6600')
    ax.axvline(24.5, color='#1f5fa8', lw=2.2); ax.text(2.0, 0.40, 'twisting the whole head by the 24.5 deg bayonet turn\nwith the horn engaged would turn the rotor 24.5 deg:\nthe latch is released before the head is even locked.', fontsize=6.6, color='#1f5fa8')
    ax.set_xlim(-6, 70); ax.set_ylim(0, 1.05); ax.set_yticks([]); ax.set_xlabel('rotor angle from the closed position (deg)', fontsize=7); ax.tick_params(labelsize=6)
    ax.set_title('Why a bayonet must turn a collar, not the head', fontsize=8.5)
    plt.tight_layout(); fig.savefig(F.OUT + 'opt_twist.png', dpi=190); plt.close(fig)


if __name__ == '__main__':
    skin_sections(); skin_elevation(); fast_screws(); fast_thumb(); fast_bayonet(); twist_problem(); radial_budget()
    template_pdf(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'docs', 'V5_skin_cutting_template_1to1.pdf'))
    print('ok')
