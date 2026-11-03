"""V5 complete concept document: the whole V5 idea as drawings plus the recent decisions (concept, NOT CAD).

Writes docs/V5_complete_concept.pdf (5 pages, A4 landscape). Standalone: needs only numpy and matplotlib.
All numbers are the concept numbers in HANDOFF.md section 0 (module frame: z = 0 at the module bottom = the transition plug top).
"""
import os
import textwrap
import numpy as np
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.patches import Rectangle, Polygon, RegularPolygon, Circle, Wedge, FancyArrowPatch

R_ID, R_OD, R_MOD, R70 = 32.51, 33.02, 32.2, 56.3 / 2
BLUE, GREEN, TAN, GREY, RED = '#4f8fd8', '#4caf7a', '#c8a46a', '#9aa0a6', '#c62828'
C1, C2, C3 = '#1565c0', '#2e7d32', '#e65100'          # bolt sets: head, module, transition
WZ0, WZ1 = 1.0, 64.5                                  # window z range (module frame)
Z_B1, Z_B2, Z_B3 = 92.0, 22.0, -18.0                  # bolt heights: head, module, transition
A4 = (11.69, 8.27)


def box(ax, x0, x1, z0, z1, col, alpha=.85, ec='k', lw=.5, ls='-', **k):
    ax.add_patch(Rectangle((x0, z0), x1 - x0, z1 - z0, fc=col, ec=ec, lw=lw, alpha=alpha, ls=ls, **k))


def bolt(ax, sx, z, col, tip, scale=1.0):
    ax.add_patch(Rectangle((sx * R_OD - (0 if sx > 0 else 1.9), z - 1.9), 1.9, 3.8, fc=col, ec='k', lw=.4))
    ax.plot([sx * R_OD, sx * tip], [z, z], color=col, lw=2.2 * scale)


def page(title, sub=None):
    fig = plt.figure(figsize=A4)
    fig.text(0.03, 0.965, title, fontsize=13, weight='bold', va='top')
    if sub:
        fig.text(0.03, 0.935, sub, fontsize=8, color='#555', va='top')
    fig.text(0.03, 0.012, 'V5 complete concept - ARC BT80 airbrake. Concept drawings and estimates, not CAD; nothing here has been built or tested.', fontsize=6, color='#777')
    return fig


def text(fig, x, y, s, fs=7.6, **k):
    fig.text(x, y, s, fontsize=fs, va='top', linespacing=1.38, **k)


def wtext(fig, x, y, s, width_frac, fs=7.0, **k):
    """Text wrapped to a width given as a fraction of the page width; paragraphs split on newlines."""
    n = int(width_frac * 11.69 * 72 / (fs * 0.50))
    lines = []
    for para in s.split('\n'):
        lines += textwrap.wrap(para, n, subsequent_indent='   ') or ['']
    fig.text(x, y, '\n'.join(lines), fontsize=fs, va='top', linespacing=1.38, **k)


def table(fig, x, y, rows, widths, fs=7, rh=0.034, head=True, colors=None):
    """Simple table in figure coordinates. rows[0] is the header row when head=True."""
    for i, row in enumerate(rows):
        xx = x
        yy = y - i * rh
        if head and i == 0:
            fig.patches.append(Rectangle((x, yy - rh + .004), sum(widths), rh, transform=fig.transFigure, fc='#e8eef7', ec='none'))
        else:
            fig.add_artist(plt.Line2D([x, x + sum(widths)], [yy - rh + .004] * 2, color='#ddd', lw=.5, transform=fig.transFigure))
        for j, cell in enumerate(row):
            c = (colors or {}).get((i, j), 'k')
            n = max(8, int((widths[j] - .008) * 11.69 * 72 / (fs * 0.50)))
            cell = '\n'.join(textwrap.wrap(cell, n)) if cell else cell
            fig.text(xx + .004, yy - .004, cell, fontsize=fs, va='top', color=c, weight='bold' if (head and i == 0) else 'normal', linespacing=1.25)
            xx += widths[j]


# ---------------------------------------------------------------- drawings
def stack(ax, labels=True, dz_head=0, dz_mod=0, dz_tr=0, tube=True, sets=(1, 2, 3)):
    """Full section, nose up. dz_* shift head / module / transition vertically (for the exploded drawings)."""
    if tube:
        for sx in (-1, 1):
            x0, x1 = sorted((sx * R_ID, sx * R_OD))
            box(ax, x0, x1, -24, WZ0, '#cfcfcf', alpha=1); box(ax, x0, x1, WZ1, 125, '#cfcfcf', alpha=1)
            ax.add_patch(Rectangle((x0 - .15, WZ0), x1 - x0 + .3, WZ1 - WZ0, fc='white', ec=RED, lw=.6, ls='--'))
    for sx in (-1, 1):
        box(ax, *sorted((sx * 26.0, sx * 29.6)), -12 + dz_tr, 0 + dz_tr, TAN); box(ax, *sorted((sx * 26.0, sx * 32.3)), -24 + dz_tr, -12 + dz_tr, TAN)
        ax.add_patch(Polygon([(sx * R_OD, -24 + dz_tr), (sx * R70, -59 + dz_tr), (sx * (R70 - 2.0), -59 + dz_tr), (sx * (R_OD - 2.0), -24 + dz_tr)], closed=True, fc='#e6d3b0', ec='#999', lw=.5, alpha=.9))
        box(ax, *sorted((sx * 29.9, sx * R_MOD)), 0 + dz_mod, 68.8 + dz_mod, GREEN)
        box(ax, *sorted((sx * 29.9, sx * R_MOD)), 68.8 + dz_head, 92.8 + dz_head, BLUE)
    d = dz_mod
    box(ax, -29.9, 29.9, 0 + d, 2 + d, GREEN)
    box(ax, -5, 5, 3.6 + d, 54.6 + d, '#7fd1a0'); box(ax, -9, 9, 43.6 + d, 54.6 + d, '#7fd1a0'); box(ax, -28, 28, 32.5 + d, 38 + d, '#7fd1a0')
    box(ax, -16, 16, 16.5 + d, 21.7 + d, '#e3a53a')
    h = dz_head
    box(ax, -29.4, 29.4, 55.2 + d, 56.6 + d, BLUE, alpha=.5)
    box(ax, -6.1, 6.1, 55.2 + h, 77.9 + h, GREY)
    box(ax, -29.9, 29.9, 78.5 + h, 80.0 + h, BLUE, alpha=.5); box(ax, -21, 2, 80 + h, 92 + h, '#e3c34a'); box(ax, 2.5, 29.5, 80 + h, 90.8 + h, '#9a6fd1'); box(ax, -29.9, 29.9, 95 + h, 99 + h, BLUE, alpha=.6)
    box(ax, -4.0, 4.0, 51.5 + h, 53.3 + h, '#e8c547'); box(ax, -2.4, 2.4, 53.3 + h, 55.2 + h, '#e8c547')
    for sx in (-1, 1):
        if 1 in sets: bolt(ax, sx, Z_B1, C1, 28.6)
        if 2 in sets: bolt(ax, sx, Z_B2, C2, 28.3)
        if 3 in sets: bolt(ax, sx, Z_B3, C3, 29.8)
    ax.set_aspect('equal'); ax.axis('off')


def p_stack(fig):
    a = fig.add_axes([0.03, 0.04, 0.34, 0.86])
    stack(a); a.set_xlim(-48, 98); a.set_ylim(-64, 130)
    T = lambda x, z, t, c='k', fs=6.6, **k: a.text(x, z, t, fontsize=fs, color=c, va='center', **k)
    T(36, 118, 'BT80 TUBE (66.04 OD, 65.02 ID)\none piece, cut once; the skin', '#444')
    T(36, 97, 'top cap, vents, switch,\nUSB-C window (in the tube)', '#555')
    T(36, 84, 'HEAD: SG90, Mercury V1, 2S\nbattery, regulator. Reusable.', C1, weight='bold')
    T(36, 72, 'set 1: 4 radial M3 bolts', C1)
    T(36, 49, '4 open windows 67 deg\n(38.6 x 63.5 mm), z 1 .. 64.5', RED)
    T(36, 33, 'MODULE: housing (one piece),\nrotor, 4 fins. The part that breaks.', C2, weight='bold')
    T(36, 22, 'set 2: 4 radial M3 bolts', C2)
    T(36, -2, 'plug top = the module seat', '#7a5a20')
    T(36, -18, 'set 3: 4 radial M3 bolts\ninto the transition shoulder', C3)
    T(36, -34, 'TRANSITION (BT80 side modelled here)', '#7a5a20', weight='bold')
    T(36, -50, 'BT70 side: not touched, falls off\nat recovery (recovery system in it)', '#8a6a30')
    a.annotate('', xy=(-41, 0), xytext=(-41, 68.8), arrowprops=dict(arrowstyle='<->', lw=.6)); a.text(-43.5, 34, 'module 68.8', rotation=90, fontsize=6, va='center', ha='center')
    a.annotate('', xy=(-41, 68.8), xytext=(-41, 99), arrowprops=dict(arrowstyle='<->', lw=.6, color=C1)); a.text(-43.5, 84, 'head about 30', rotation=90, fontsize=6, va='center', ha='center', color=C1)
    a.set_title('The stack, nose up (full section, concept; z = 0 at the module bottom)', fontsize=7.5)


def nut(ax, x, z, r=2.9):
    ax.add_patch(RegularPolygon((x, z), 6, radius=r, orientation=np.pi / 2, fc='#bbb', ec='k', lw=.6))


def p_joint(ax):
    """Radial section through one bolt joint: set 2 (module) and set 3 (transition)."""
    box(ax, R_ID, R_OD, -26, 30, '#cfcfcf', alpha=1)
    box(ax, 29.9, R_MOD, 0, 30, GREEN); box(ax, 26.0, R_MOD, 0, 2, GREEN)
    box(ax, 26.0, 29.6, -12, 0, TAN); box(ax, 26.0, 32.3, -24, -12, TAN)
    # module bolt (set 2): nut boss on the inside of the module wall, slot open to the inside
    box(ax, 27.6, 29.9, 15.3, 22.5 + 3.5, GREEN, alpha=.9)
    box(ax, 27.6, 29.9, Z_B2 - 3.0, Z_B2 + 3.0, 'white', alpha=1, ec=RED, ls='--', lw=.7)
    nut(ax, 28.7, Z_B2, 2.6); ax.plot([R_OD + 1.6, 27.3], [Z_B2, Z_B2], color=C2, lw=2.2); box(ax, R_OD, R_OD + 1.9, Z_B2 - 1.9, Z_B2 + 1.9, C2, ec='k')
    # transition bolt (set 3)
    box(ax, 29.7, 32.1, Z_B3 - 3.0, Z_B3 + 3.0, 'white', alpha=1, ec=RED, ls='--', lw=.7)
    nut(ax, 30.9, Z_B3, 2.6); ax.plot([R_OD + 1.6, 29.5], [Z_B3, Z_B3], color=C3, lw=2.2); box(ax, R_OD, R_OD + 1.9, Z_B3 - 1.9, Z_B3 + 1.9, C3, ec='k')
    ax.text(36.5, Z_B2, 'set 2: M3x8 button head from outside,\nthrough the tube and the module wall,\nnut in a slot open to the inside', fontsize=6, va='center', color=C2)
    ax.text(36.5, Z_B3, 'set 3: same, into the transition shoulder\n(nut slot R29.7..32.1)', fontsize=6, va='center', color=C3)
    ax.text(36.5, 4, 'no sleeve: the module sits on the plug top;\nthe two joints are independent', fontsize=6, va='center', color='#2a7a52')
    ax.text(21.5, -6, 'plug\nR26.0..29.6', fontsize=6, va='center', ha='center')
    ax.set_xlim(18, 68); ax.set_ylim(-26, 32); ax.set_aspect('equal'); ax.grid(alpha=.15); ax.tick_params(labelsize=5.5)
    ax.set_title('A  Axial section through two bolts (module and transition)', fontsize=7.2, loc='left')


def p_plan_module(ax):
    """Plan section at the module bolt height: tube, wall, four nut bosses; cam circle dashed."""
    ax.add_patch(Wedge((0, 0), R_OD, 0, 360, width=R_OD - R_ID, fc='#cfcfcf', ec='k', lw=.4))
    ax.add_patch(Wedge((0, 0), R_MOD, 0, 360, width=R_MOD - 29.9, fc=GREEN, ec='k', lw=.4, alpha=.85))
    for k in range(4):
        a = np.radians(45 + 90 * k)
        c, s = np.cos(a), np.sin(a)
        # boss: radial R27.6..29.9, 7 mm tangential
        pts = [(r * c - t * s, r * s + t * c) for r, t in ((27.6, -3.5), (29.95, -3.5), (29.95, 3.5), (27.6, 3.5))]
        ax.add_patch(Polygon(pts, closed=True, fc=GREEN, ec='k', lw=.4, alpha=.95))
        nx, ny = 28.7 * c, 28.7 * s
        ax.add_patch(RegularPolygon((nx, ny), 6, radius=2.6, orientation=a, fc='#bbb', ec='k', lw=.5))
        ax.plot([R_OD * c, 27.6 * c - 1 * c], [R_OD * s, 27.6 * s - 1 * s], color=C2, lw=1.8)
    ax.add_patch(Circle((0, 0), 28.6, fc='none', ec='#c0392b', ls='--', lw=.8))
    ax.add_patch(Circle((0, 0), 9, fc='#7fd1a0', ec='k', lw=.4))
    ax.text(0, 0, 'hub', fontsize=6, ha='center', va='center')
    ax.text(0, -39.5, 'dashed: cam peak R28.6 (module wall inside R29.9; bosses R27.6)\nthe cam lobes pass the boss height only while the rotor drops in:\nlobe azimuth vs boss azimuth (45 + 90k) is a CAD check', fontsize=5.6, ha='center', va='top', color='#c0392b')
    ax.set_xlim(-37, 37); ax.set_ylim(-46, 37); ax.set_aspect('equal'); ax.axis('off')
    ax.set_title('B  Plan section at the module bolts (z 22)', fontsize=7.2, loc='left')


def p_plan_head(ax):
    ax.add_patch(Wedge((0, 0), R_OD, 0, 360, width=R_OD - R_ID, fc='#cfcfcf', ec='k', lw=.4))
    ax.add_patch(Wedge((0, 0), R_MOD, 0, 360, width=R_MOD - 29.9, fc=BLUE, ec='k', lw=.4, alpha=.8))
    for az in (45, 135, 250, 290):
        a = np.radians(az)
        c, s = np.cos(a), np.sin(a)
        pts = [(r * c - t * s, r * s + t * c) for r, t in ((24.5, -3.5), (29.95, -3.5), (29.95, 3.5), (24.5, 3.5))]
        ax.add_patch(Polygon(pts, closed=True, fc=BLUE, ec='k', lw=.4, alpha=.95))
        ax.add_patch(RegularPolygon((26.6 * c, 26.6 * s), 6, radius=2.6, orientation=a, fc='#bbb', ec='k', lw=.5))
        ax.plot([R_OD * c, 25.5 * c], [R_OD * s, 25.5 * s], color=C1, lw=1.8)
        ax.text(38.5 * c, 38.5 * s, f'{az} deg', fontsize=5.6, ha='center', va='center', color=C1)
    ax.text(0, 0, 'servo, Mercury, battery\nand regulator sit in the\nmiddle (layout is a CAD step;\nthe bosses are placed to\nclear the battery and Mercury)', fontsize=5.8, ha='center', va='center', color='#444')
    ax.set_xlim(-44, 44); ax.set_ylim(-44, 44); ax.set_aspect('equal'); ax.axis('off')
    ax.set_title('C  Plan section at the head bolts (set 1, z 74.8)', fontsize=7.2, loc='left')


def p_unroll(ax):
    """Tube unrolled: azimuth vs z, windows and the 12 holes (the 1:1 template idea)."""
    for k in range(4):
        c = 90 * k
        for off in (0, 360):
            ax.add_patch(Rectangle((c - 33.5 + off - 360 * (c > 180) * 0, WZ0), 67, WZ1 - WZ0, fc='#fde8e8', ec=RED, lw=.8, ls='--'))
    ax.add_patch(Rectangle((-30, WZ0), 0.001, 0.001))
    for az in (45, 135, 225, 315):
        ax.plot(az, Z_B2, 'o', color=C2, ms=5); ax.plot(az, Z_B3, 'o', color=C3, ms=5)
    for az in (45, 135, 250, 290):
        ax.plot(az, Z_B1, 'o', color=C1, ms=5)
    ax.add_patch(Rectangle((0, 83), 360, 9, fc='#f2f2f2', ec='#888', lw=.5, ls=':'))
    ax.text(180, 87, 'switch slot, USB-C window, 3 vents (above the head, positions set in CAD)', fontsize=5.6, ha='center', va='center', color='#555')
    for az, z, t, col in ((45, Z_B2 + 5, 'set 2', C2), (45, Z_B3 + 5, 'set 3', C3), (250, Z_B1 + 5, 'set 1', C1)):
        ax.text(az, z, t, fontsize=5.6, color=col, ha='center')
    ax.text(0, 33, 'window', fontsize=5.6, color=RED, ha='center'); ax.text(90, 33, 'window', fontsize=5.6, color=RED, ha='center')
    ax.set_xlim(0, 360); ax.set_ylim(-26, 104); ax.set_xticks(range(0, 361, 45)); ax.grid(alpha=.15); ax.tick_params(labelsize=5.5)
    ax.set_xlabel('azimuth (deg), unrolled', fontsize=6); ax.set_ylabel('z from the module seat (mm)', fontsize=6)
    ax.set_title('D  The tube unrolled: 4 windows and the 12 clearance holes, cut once', fontsize=7.2, loc='left')
    # windows centered at 0 wrap: draw the wrap-around part
    ax.add_patch(Rectangle((360 - 33.5, WZ0), 33.5, WZ1 - WZ0, fc='#fde8e8', ec=RED, lw=.8, ls='--'))


def p_oneplece(ax):
    for sx in (-1, 1):
        box(ax, *sorted((sx * 29.9, sx * 32.2)), 0, 68.8, GREEN)
        box(ax, *sorted((sx * 5.4, sx * 8.0)), 10.4, 13.4, GREEN)
        box(ax, *sorted((sx * 8.0, sx * 29.9)), 10.4, 13.4, GREEN, alpha=.6)
        box(ax, *sorted((sx * 10, sx * 19)), 13.4, 24.0, '#2f9a63')
    box(ax, -29.9, 29.9, 0, 2, GREEN)
    box(ax, -5, 5, 3.6, 54.6, '#7fd1a0'); box(ax, -9, 9, 43.6, 54.6, '#7fd1a0'); box(ax, -28, 28, 32.5, 38, '#7fd1a0')
    box(ax, -8.5, 8.5, 13.9, 15.9, '#7fd1a0'); box(ax, -16, 16, 16.5, 21.7, '#e3a53a')
    ax.annotate('', xy=(0, 62), xytext=(0, 100), arrowprops=dict(arrowstyle='-|>', color='#2a7a52', lw=2.4))
    ax.text(0, 105, 'rotor drops in from the top', fontsize=6.4, ha='center', color='#2a7a52')
    ax.text(36, 62, 'cam peak R28.6 is 0.9 mm\nsmaller than the housing\ninterior R29.48 (paper check)', fontsize=5.8, va='center', color='#c0392b')
    ax.text(36, 19, 'limiter finger (orange) and stops\n(dark green) ABOVE the bearing ring\n(V4 had them below)', fontsize=5.8, va='center')
    ax.text(36, 4, 'no seam, no seam screws, no pegs,\nno snap hooks, no band', fontsize=5.8, va='center', color='#2a7a52', weight='bold')
    ax.set_xlim(-45, 80); ax.set_ylim(-4, 112); ax.set_aspect('equal'); ax.axis('off')
    ax.set_title('Housing in one piece: the rotor goes in from the top (concept)', fontsize=7.2)


def p_route(ax, which):
    """Exploded removal route. which = 'bottom' or 'top'. Only the bolts still fitted are drawn."""
    if which == 'bottom':
        stack(ax, dz_head=0, dz_mod=-85, dz_tr=-135, sets=(1,))
        ax.annotate('', xy=(-44, -125), xytext=(-44, -30), arrowprops=dict(arrowstyle='-|>', color=C3, lw=2))
        ax.text(-47, -75, '1  transition out\n(set 3 bolts out first)', fontsize=6, color=C3, ha='right', va='center')
        ax.annotate('', xy=(46, -50), xytext=(46, 34), arrowprops=dict(arrowstyle='-|>', color=C2, lw=2))
        ax.text(50, -8, '2  module out (set 2 bolts out)\nthe horn leaves the hub slot', fontsize=6, color=C2, va='center')
        ax.text(0, 104, 'HEAD stays; set 1 never touched', fontsize=6.4, color=C1, ha='center', weight='bold')
        ax.set_xlim(-70, 130); ax.set_ylim(-200, 125)
        ax.set_title('Route 1 (main): out of the BOTTOM', fontsize=8, color='#2a7a52')
    else:
        stack(ax, dz_head=140, dz_mod=60, dz_tr=0, sets=(3,))
        ax.annotate('', xy=(46, 180), xytext=(46, 105), arrowprops=dict(arrowstyle='-|>', color=C1, lw=2))
        ax.text(50, 140, '1  head out (set 1 bolts out)\nthe horn leaves with it', fontsize=6, color=C1, va='center')
        ax.annotate('', xy=(-44, 95), xytext=(-44, 30), arrowprops=dict(arrowstyle='-|>', color=C2, lw=2))
        ax.text(-47, 62, '2  module out\n(set 2 bolts out)', fontsize=6, color=C2, ha='right', va='center')
        ax.text(0, -66, 'TRANSITION stays; set 3 never touched', fontsize=6.4, color=C3, ha='center', weight='bold')
        ax.set_xlim(-70, 130); ax.set_ylim(-80, 245)
        ax.set_title('Route 2 (alternative): out of the TOP', fontsize=8, color=C1)


def make(path):
    with PdfPages(path) as pdf:
        # ------------------------------------------------ page 1
        f = page('V5 complete concept: the modular airbrake', 'The whole idea on five pages (concept drawings). Status: BUILT in CAD as mode 5 and checked, not printed. What is built: V5_assembly_guide.pdf.')
        text(f, 0.03, 0.89, 'What V5 is, in one paragraph', 8.6, weight='bold')
        text(f, 0.03, 0.865,
             'The airbrake will break every flight, so V5 is built to swap the part that breaks. One BT80 tube, cut once, is the skin. Two inserts slide into it: the MODULE (housing,\n'
             'rotor, four fins: the part that breaks) and the HEAD (SG90 servo, Mercury V1, regulator, 2S battery, switch: reusable). The head sits above the module and stays in\n'
             'the tube; the servo horn drops into the rotor hub slot, so no wire crosses a joint. Below sits the TRANSITION (BT80 to BT70). Everything is held by plain M3 bolts and\n'
             'nuts, radial, from the outside through the tube, on the BT80 side only. The BT70 side is not touched.', 7.6)
        text(f, 0.03, 0.765, 'Your hard rules (they decide the design)', 8.6, weight='bold')
        rules = [('M3 bolts and nuts wherever possible', 'no heat-set inserts, no self-tapping into plastic'),
                 ('All bolts radial, from the outside', 'through the BT80 tube; BT80 side only; nothing from below'),
                 ('Never touch the BT70 side', 'the transition below the BT80 plug and shoulder is yours; cone and sleeve here are placeholders'),
                 ('No snap hooks, no bands', 'nothing that flexes or wraps around to hold a part'),
                 ('Housing in one piece', 'no seam, no seam screws: the rotor drops in from the top')]
        table(f, 0.03, 0.74, [('Rule', 'What it means here')] + rules, [0.22, 0.43], fs=7, rh=0.031)
        text(f, 0.03, 0.545, 'What changes from V4 to V5', 8.6, weight='bold')
        rows = [('', 'V4 (built)', 'V5 (planned)'),
                ('Where the skin is', 'BT80 pieces glued to the fins', 'one BT80 tube is the skin; windows left open (tape optional)'),
                ('Swap', 'cut and rebuild the whole airbrake', 'slide out the module; 8 bolts; the head is never touched'),
                ('Housing', 'two halves, 4 seam screws, pegs', 'one piece; limiter moved above the bearing ring'),
                ('Electronics', 'bay and sled inside the housing, wires cross the housing', 'in the head: no wire crosses a joint; V4 vents and cable hole disappear'),
                ('Fasteners', '27 screws (4 seam, 4 cap, 4 hinge M4, 4 boss, 8 tube support, 3 M2)', 'about 15: 12 radial M3 + nut, hinges M3 + nut (counted in the 12), 3 M2 servo'),
                ('Bottom', 'bay, lower sleeve, bonded ring', 'transition plug and shoulder (BT80 side), bolted'),
                ('Size and weight', '105.4 mm overall, 144 g (estimate)', 'about 107 mm overall; module about 105 g, head about 55 g (estimates)')]
        table(f, 0.03, 0.52, rows, [0.13, 0.26, 0.31], fs=6.8, rh=0.04)
        fig_ax = f.add_axes([0.76, 0.06, 0.22, 0.82]); stack(fig_ax); fig_ax.set_xlim(-48, 48); fig_ax.set_ylim(-62, 125); fig_ax.set_title('Concept, to scale', fontsize=7)
        pdf.savefig(f); plt.close(f)

        # ------------------------------------------------ page 2
        f = page('The stack and the three bolt sets', 'Source of truth for the numbers: HANDOFF.md section 0 (concept values; the CAD may move them).')
        p_stack(f)
        text(f, 0.40, 0.89, 'The three independent bolt sets (bolt path B, no sleeve)', 8.6, weight='bold')
        rows = [('Set', 'What it holds', 'Where', 'Nut', 'Azimuths'),
                ('1  head', 'head and lid to tube', 'tube + head cup wall + lid boss', 'hex pocket in the lid boss', '45, 135, 250, 290'),
                ('2  module', 'module to tube', 'tube + module wall (nut boss R27.6..29.9)', 'slot open inward', '45, 135, 225, 315'),
                ('3  transition', 'transition to tube', 'tube + transition shoulder (R26.0..32.3)', 'slot in the shoulder', '45, 135, 225, 315')]
        table(f, 0.40, 0.865, rows, [0.075, 0.095, 0.185, 0.1, 0.1], fs=6.6, rh=0.04,
              colors={(1, 0): C1, (2, 0): C2, (3, 0): C3})
        wtext(f, 0.40, 0.69,
              'All 12 holes are plain M3 clearance holes in the tube (final size set in CAD), cut once from the 1:1 template. A hole is only a hole: a new module reuses the same 12 holes, so holes are reused, never multiplied. What wears is the bolts and nuts (cheap). Bolt: M3x8 button head, 2.0 mm hex key, nut slot 5.7 wide x 2.6 deep.\n'
              'The module seat is the plug top (R26.0..29.6, 12 mm). The module does not wrap the plug, so the module load goes into the four module-wall bolts only. Estimated shock: 100 g on a 105 g module is about 100 N, 25 N per bolt; an M3 bolt in a 2.7 mm printed wall bears about 100 to 240 N (screening values, not tested).', 0.58, 6.8)
        text(f, 0.40, 0.575, 'Parts and what is new', 8.6, weight='bold')
        rows = [('Part', 'Work', 'Based on'),
                ('Tube (reference)', '4 windows 67 deg x 63.5 mm, 12 clearance holes, switch, USB-C, 3 vents', 'V4 upper tube'),
                ('Module housing', 'one piece; no bay, bosses, supports, ledges, seam; 4 nut bosses; limiter above the ring', 'V4 housing'),
                ('Rotor', 'integral catch caps (no cap screws), hub slot with a lead-in', 'V4 rotor'),
                ('Fins', 'same shape; M3 hinge bolt + nut slots instead of M4', 'V4 fins'),
                ('Head', 'sleeve with 4 bosses and nut slots, cup with servo ledges, plate, single-layer sled, top cap', 'new (V4 sled, ledges)'),
                ('Transition (BT80 side)', 'plug, shoulder, 4 nut slots; cone and BT70 sleeve are placeholders', 'new'),
                ('Assembly', 'mates: module slides along the tube, fins open, horn finds the slot', 'asm.py')]
        table(f, 0.40, 0.55, rows, [0.135, 0.34, 0.1], fs=6.5, rh=0.047)
        pdf.savefig(f); plt.close(f)

        # ------------------------------------------------ page 3
        f = page('How it fits: the joints, the holes and the tube', 'Detail sections (concept). Every bolt is radial, from the outside, through the BT80 tube.')
        a = f.add_axes([0.04, 0.50, 0.45, 0.40]); p_joint(a)
        b = f.add_axes([0.52, 0.47, 0.22, 0.43]); p_plan_module(b)
        c = f.add_axes([0.75, 0.47, 0.23, 0.43]); p_plan_head(c)
        d = f.add_axes([0.06, 0.09, 0.48, 0.32]); p_unroll(d)
        text(f, 0.58, 0.40, 'Why nothing is multiplied', 8.6, weight='bold')
        text(f, 0.58, 0.375,
             'Nothing is screwed into plastic. Every hole is a plain M3 clearance hole and every bolt ends in a nut.\n'
             '  The tube has 12 holes: 4 head, 4 module, 4 transition. They are cut once.\n'
             '  The transition has 4 holes and 4 nut slots, the same 4 every time.\n'
             '  Each new module is printed with its own 4 nut slots at the same positions,\n'
             '  so it lines up with the existing tube holes.\n'
             'Unbolting leaves nothing damaged. The transition is not used up.\n\n'
             'Tube features: 4 windows (open; one wrap of foil or Kapton tape is optional,\n'
             'about 5.6 N suction per window at 80 m/s by the torque-check assumption),\n'
             'a switch slot, a USB-C window and 3 vents above the head.\n'
             'Fins stay inside R32.2: a fin with its own skin would not slide into the tube.', 7.2)
        pdf.savefig(f); plt.close(f)

        # ------------------------------------------------ page 4
        f = page('One-piece housing and the two ways out', 'Bottom is the main route; the top works too once all the screws are out (your answer today).')
        a = f.add_axes([0.03, 0.15, 0.27, 0.73]); p_oneplece(a)
        b = f.add_axes([0.31, 0.15, 0.34, 0.75]); p_route(b, 'bottom')
        c = f.add_axes([0.66, 0.15, 0.32, 0.75]); p_route(c, 'top')
        wtext(f, 0.03, 0.115,
              'Route 1 (main; the BT70 section is already off): 1 pull the 4 transition bolts and slide the transition out of the bottom. 2 pull the 4 module bolts and slide the module out of the bottom (the horn leaves the hub slot). 3 new module in, nuts in the slots first, 4 bolts. 4 transition back, 4 bolts. 8 bolts; the head is never touched.\n'
              'Route 2 (alternative): pull the 4 head bolts and lift the head out; pull the 4 module bolts and lift the module out of the top. 8 bolts; the transition stays on. It needs the upper airframe separated from the top of this tube (assumption, please confirm). Both routes work because nothing on the module or the head is wider than the bore or acts as a flange.', 0.94, 6.5)
        pdf.savefig(f); plt.close(f)

        # ------------------------------------------------ page 5
        f = page('Recent decisions, what they replaced, and what is open', 'Order follows the repository history; the user\'s own words are in quotes where the handoff recorded them.')
        rows = [('#', 'Decision', 'Why', 'Status'),
                ('1', 'Make the airbrake modular: swap the whole module', '"it will break every flight"', 'decided'),
                ('2', 'One BT80 tube cut once is the skin; no BT80 glued to the fins; windows open (tape optional)', 'a fin with its own skin cannot slide into the tube', 'decided'),
                ('3', 'Window size is 67 deg x 63.5 mm (38.6 x 63.5), not 43 mm tall', 'measured on the V4 reference tube; earlier drafts were wrong', 'corrected'),
                ('4', 'No lower BT80 tube; the "transition ring" is the top of the transition; BT70 OD 56.3', 'the BT70 side holds the recovery system and falls off', 'corrected'),
                ('5', 'M3 bolts + nuts, no heat-set inserts, no self-tapping', 'rule', 'decided'),
                ('6', 'All bolts radial, from outside, BT80 side only; screws from below rejected', 'rule: "I do not have much space in the transition"', 'decided'),
                ('7', 'Bolt path B: three independent sets of 4, no module sleeve over the plug', 'sleeve adds 12 mm, clamps the part that breaks', 'decided'),
                ('8', 'Housing in one piece ("ok ye try the housing one piece"); no snap hooks, no band', 'removes seam, 4 seam screws, pegs', 'verified in CAD: rotor drops in at any angle 0..60 deg'),
                ('9', 'Head is a separate reusable insert; no wire crosses a joint', 'V4 vents and cable hole disappear', 'decided'),
                ('10', 'Module comes out of the bottom mainly; also out of the top when all screws are out', 'your answer today', 'decided; design rule added'),
                ('11', 'Go-ahead for the CAD build', 'you asked for this document first, then "go ahead and build V5"', 'given; V5 built, not printed')]
        table(f, 0.03, 0.915, rows, [0.03, 0.42, 0.31, 0.19], fs=6.4, rh=0.033)
        text(f, 0.03, 0.49, 'Replaced along the way', 7.8, weight='bold')
        wtext(f, 0.03, 0.468,
              'heat-set inserts with 4 head + 2 index screws (V5_final_plan)\nmodule skin and bayonet options (choice 1 and 2 sheets)\nscrews from below (transition sketch)\nbolt path A with a module sleeve (sketch 2; its screw table and nut-in-slot detail still hold)\n"open the top only" as the single swap route (insert concept; now bottom is the main route)', 0.46, 6.8)
        text(f, 0.03, 0.345, 'Still open (I will not guess these)', 7.8, weight='bold')
        wtext(f, 0.03, 0.323,
              '1  (done) V5 CAD built: FeatureScript mode 5, transition BT80 side, head, assembly, checks, exports. Print and fit tests are next.\n'
              '2  Transition diameters unknown: I model the BT80 plug and shoulder; cone and BT70 sleeve are placeholders; the BT70 ID is needed later.\n'
              '3  Windows open or taped (tape is optional).\n'
              '4  Route 2 needs the upper airframe to open at the top of this tube: please confirm this matches your recovery layout.\n'
              '5  Carried over from V4: battery size, Mercury servo header pins, SG90 horn dimensions, ground-impact FEA, a real print test.', 0.46, 6.8)
        text(f, 0.52, 0.49, 'Checks before I call V5 done', 7.8, weight='bold')
        wtext(f, 0.52, 0.468,
              'V1 to V4 stay volume-identical (regression rebuild)\nno printed overlaps, closed or open; the module slides along the tube\nfins open through the windows; hinge bolts reachable through them\nhead goes on and the horn finds the slot (about +-8 deg); both exit routes clear\nrotor sweep, latch and cam timing; one-piece drop-in clearances\nnut slots clear of the cam during the rotor drop-in\nhex key (2.0 mm) reaches all 12 bolts\nSTL (print orientations: rotor hub down, fins flat, housing upright) and STEP', 0.46, 6.8)
        wtext(f, 0.52, 0.28, 'Fallback if the one-piece housing fails: two halves joined by a sliding dovetail along the seam (no flexing parts, no snap hooks).\nDesign rules added by today\'s answer: nothing on the module or the head wider than the bore, no flange or lip that blocks either direction, hub slot open toward the head.', 0.46, 6.8)
        pdf.savefig(f); plt.close(f)


if __name__ == '__main__':
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'docs', 'V5_complete_concept.pdf')
    make(out); print('wrote', os.path.normpath(out))
