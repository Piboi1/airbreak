"""V4 concept sketch (NOT CAD): servo on top, thicker rotor parts, limiter at the bottom, electronics bay, screwed transition."""
import numpy as np, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyArrowPatch, Circle, Polygon
import figures as F
OUT = F.OUT

BLUE = '#8fb4d9'; BLUE_D = '#3d6fa3'; ORANGE = '#f0a060'; GREEN = '#58b07a'; GREEN_D = '#1f7a44'; GREY = '#9a9aa0'
RED = '#d33'; PURPLE = '#b58ad8'; YELLOW = '#f2d45c'; PINK = '#f08aa0'; TAN = '#e8d9a8'

def blk(ax, x0, x1, z0, z1, fc, ec='#333', lw=.7, sym=True, hatch=None, alpha=1.0, z=2):
    for s in ((1, -1) if sym else (1,)):
        a, b = sorted((s * x0, s * x1))
        ax.add_patch(Rectangle((a, z0), b - a, z1 - z0, fc=fc, ec=ec, lw=lw, hatch=hatch, alpha=alpha, zorder=z))

def side(ax, v4):
    ax.set_xlim(-48, 48); ax.set_ylim(-52 if v4 else -52, 66); ax.set_aspect('equal'); ax.grid(alpha=.15)
    # housing walls and base ring (same in both)
    blk(ax, 29.5, 33.02, -33, 58.8, BLUE, ec=BLUE_D)
    blk(ax, 26 if v4 else 18, 33.02, -15, -11, BLUE, ec=BLUE_D)         # base / stop ring (V4: opened to R26 for the bay)
    blk(ax, 29.9, 32.3, -33, -15, BLUE, ec=BLUE_D)                      # lower sleeve
    blk(ax, 29.9, 32.3, 4, 54, ORANGE, ec='#a05010', z=3)               # fins (z 4..54)
    ax.add_patch(Rectangle((-33.02, -33), 66.04, 91.8, fc='none', ec='#000', lw=1.2, ls='--', zorder=5))
    if not v4:
        blk(ax, 0, 5, -8.7, 56, GREEN, ec=GREEN_D, sym=True)               # rotor shaft
        blk(ax, 5, 28.6, 22, 25, GREEN, ec=GREEN_D)                        # cam web 3 mm
        blk(ax, 5, 24.1, 36.6, 39.6, GREEN, ec=RED, lw=1.4)                # crown arms 3 mm (thin)
        blk(ax, 18, 26, 31.4, 46, GREEN_D, ec='#000', lw=.6)               # catch caps
        blk(ax, 5.4, 18, 46, 51, BLUE, ec=BLUE_D)                          # top bearing
        blk(ax, 8, 16, 52, 56, GREEN, ec=RED, lw=1.4)                      # knob finger (thin)
        blk(ax, 12, 18, 50.5, 56.4, BLUE, ec=RED, lw=1.4)                  # knob stops (thin)
        blk(ax, 5.4, 8, -0.8, 2.2, BLUE, ec=BLUE_D); blk(ax, 8, 30, -0.8, 2.2, BLUE, ec=BLUE_D)     # lower bearing + spokes
        blk(ax, 0, 6.2, -8.7, -1.7, GREEN, ec=GREEN_D)                     # hub
        ax.add_patch(Rectangle((-11.5, -33), 23, 22.7, fc=GREY, ec='#333', lw=.8, zorder=4)); ax.text(0, -22, 'SG90', ha='center', fontsize=7)
        ax.set_title('V3 now: servo at the bottom', fontsize=9)
    else:
        blk(ax, 0, 5, -6, 32.5, GREEN, ec=GREEN_D)                         # rotor shaft hangs from the servo
        blk(ax, 5, 28.6, 22.5, 28.5, GREEN, ec=GREEN_D, lw=1.4)            # thicker cam web 6 mm
        blk(ax, 5, 24.1, 30.5, 35.5, GREEN, ec=GREEN_D, lw=1.4)            # thicker crown arms 5 mm
        blk(ax, 18, 26, 29.8, 46, GREEN_D, ec='#000', lw=.6)               # catch caps (finger unchanged)
        # servo flipped on top
        ax.add_patch(Rectangle((-11.5, 36.1), 23, 22.7, fc=GREY, ec='#333', lw=.8, zorder=4)); ax.text(0, 52, 'SG90', ha='center', fontsize=7)
        ax.add_patch(Rectangle((-16.25, 40.3), 32.5, 2.5, fc='#777', ec='#333', lw=.6, zorder=4))     # flange
        blk(ax, 0, 2.4, 32.4, 36.1, '#777', sym=True)                       # spline
        blk(ax, 0, 4, 32.4, 34.2, '#e6c24a')            # horn
        blk(ax, 17, 29.5, 38, 40.3, BLUE, ec=BLUE_D)                       # ledges that carry the flange
        # limiter (flipped, thick) at the bottom + lower bearing
        blk(ax, 5.4, 8, 0.4, 3.4, BLUE, ec=BLUE_D); blk(ax, 8, 30, 0.4, 3.4, BLUE, ec=BLUE_D)
        blk(ax, 5, 7, 3.9, 5.9, GREEN, ec=GREEN_D)                          # collar above the bearing
        blk(ax, 5, 16, -5.6, -0.4, GREEN, ec='#0a0', lw=1.6)                # thick limiter finger/disc
        blk(ax, 12, 20, -6.4, 0.0, BLUE, ec='#0a0', lw=1.6)                 # thick stops
        # electronics bay (two layers) and bay ceiling
        blk(ax, 0, 29.9, -9, -7, BLUE, ec=BLUE_D, sym=True)
        blk(ax, 0, 22.5, -20.5, -9.5, PURPLE, ec='#444', lw=.8, sym=True)                 # altimeter (layer B)
        ax.add_patch(Rectangle((-20, -31.5), 20, 9.5, fc=YELLOW, ec='#444', lw=.8, zorder=3))   # battery (layer A)
        ax.add_patch(Rectangle((2, -31.5), 12.5, 7.5, fc=PINK, ec='#444', lw=.8, zorder=3))     # regulator (layer A)
        # bottom flange + transition
        blk(ax, 22, 33.02, -33, -29, BLUE, ec=BLUE_D)
        blk(ax, 22, 33.02, -37, -33, TAN, ec='#a08040', hatch='///')
        for s in (1, -1): ax.add_patch(FancyArrowPatch((s * 27, -41), (s * 27, -30), arrowstyle='-|>', mutation_scale=9, color='#222', lw=1))
        ax.set_title('V4 proposal: servo on top, bay at the bottom', fontsize=9)
    ax.set_xlabel('x (mm), side section', fontsize=7); ax.set_ylabel('z (mm)', fontsize=7); ax.tick_params(labelsize=6)

def tag(ax, x, z, n, col='#000'):
    ax.add_patch(Circle((x, z), 3.0, fc='white', ec=col, lw=1, zorder=9)); ax.text(x, z, str(n), ha='center', va='center', fontsize=6.5, color=col, zorder=10)

def fig_elevation(path):
    fig, axs = plt.subplots(1, 2, figsize=(7.6, 5.4))
    side(axs[0], False); side(axs[1], True)
    for ax in axs: ax.set_ylim(-48, 62)
    a, b = axs
    tag(a, -23, 56, 1, RED); tag(a, -12, 42.5, 2, RED); tag(a, 0, -22, 3)
    tag(b, 0, 52, 1); tag(b, -24, 41.5, 2, BLUE_D); tag(b, -12, 33, 3, GREEN_D); tag(b, -20, 25.3, 4, GREEN_D)
    tag(b, -25, 2, 5, BLUE_D); tag(b, -19, -3, 6, '#0a0'); tag(b, 12, -15, 7); tag(b, 26, -36, 8, '#806020')
    fig.text(0.5, 0.005, '', fontsize=6)
    fig.suptitle('Same overall size: 91.8 mm tall, 66 mm OD (dashed box), fins unchanged (orange). SKETCH, not CAD', fontsize=8.5)
    fig.tight_layout(rect=(0, 0.0, 1, 0.97)); fig.savefig(path, dpi=220); plt.close(fig)

def fig_thicken(path):
    fig, axs = plt.subplots(2, 3, figsize=(7.6, 5.4))
    # (a) limiter plan: current vs proposed (finger drawn at rest, ghost at the end of its 65 deg travel)
    def rot(pts, deg):
        t = np.radians(deg); R = np.array([[np.cos(t), -np.sin(t)], [np.sin(t), np.cos(t)]]); return pts @ R.T
    def rectp(x0, x1, y0, y1): return np.array([[x0, y0], [x1, y0], [x1, y1], [x0, y1]])
    for ax, (title, fw, sw, sh_) in zip(axs[0, :2], (('now: finger %.1f mm, stops %.1f mm' % (2.1, 2.0), 2.1, 2.0, 5.9), ('proposed: finger 6 mm, stops 8 mm', 6.0, 8.0, 9.0))):
        ax.set_xlim(-22, 22); ax.set_ylim(-14, 24); ax.set_aspect('equal'); ax.axis('off'); ax.set_title(title, fontsize=7)
        ax.add_patch(Circle((0, 0), 18, fc='none', ec='#999', lw=.8, ls=':'))
        fing = rectp(7.5, 16, -fw / 2, fw / 2)
        ax.add_patch(Polygon(fing, fc=GREEN, ec=GREEN_D, lw=1.2))
        ax.add_patch(Polygon(rot(fing, 65), fc='none', ec=GREEN_D, lw=.9, ls='--'))
        st1 = rectp(10, 19, -fw / 2 - sw, -fw / 2)          # stop that the finger rests against at 0 deg
        st2 = rot(rectp(10, 19, fw / 2, fw / 2 + sw), 65)   # stop it reaches at 65 deg
        ax.add_patch(Polygon(st1, fc=BLUE, ec=BLUE_D, lw=1.2)); ax.add_patch(Polygon(st2, fc=BLUE, ec=BLUE_D, lw=1.2))
        ax.text(0, -12.5, 'travel kept at 65 deg (finger dashed at the far end)', ha='center', fontsize=5.8)
    ax = axs[0, 2]; ax.axis('off'); ax.set_xlim(0, 10); ax.set_ylim(0, 10)
    ax.text(0, 9.2, 'Why they snap', fontsize=8, fontweight='bold')
    ax.text(0, 4.2, '- finger and stops are about 2 mm wide\n  in the printed layer direction: a\n  single impact at the end of travel\n  loads them like a small cantilever\n- the crown arm is 5 mm wide and 3 mm\n  thick with a 3.4 mm screw hole: only\n  0.8 mm of material each side\n- the cam web is 3 mm thick', fontsize=6.4, va='center')
    # (b) crown arm, plan view (looking along the screw): now vs proposed
    for ax, (title, w, boss, t) in zip(axs[1, :2], (('crown arm now: 5 mm wide, 3 mm thick', 5.0, 0, 3), ('proposed: 6 mm arm, 10 mm boss, 5 mm thick', 6.0, 10.0, 5))):
        ax.set_xlim(-13, 9); ax.set_ylim(-9, 13); ax.set_aspect('equal'); ax.axis('off'); ax.set_title(title, fontsize=7)
        ax.add_patch(Rectangle((-w / 2, -9), w, 21, fc=GREEN, ec=GREEN_D, lw=1.2))
        if boss: ax.add_patch(Circle((0, 0), boss / 2, fc=GREEN, ec=GREEN_D, lw=1.2))
        ax.add_patch(Circle((0, 0), 1.7, fc='white', ec='#333', lw=1))
        wall = (boss or w) / 2 - 1.7
        x0 = -(boss or w) / 2
        ax.annotate('', (x0, 4.5), (-1.7, 4.5), arrowprops=dict(arrowstyle='<->', lw=.7, color='#fff' if False else '#222')); ax.text(x0 - 0.4, 4.5, 'wall\n%.1f mm' % wall, ha='right', va='center', fontsize=6.3, color=RED if wall < 1.5 else '#0a6')
        ax.text(0, 12.3, 'plan view, along the M3 screw, thickness %d mm' % t, ha='center', fontsize=5.8)
    ax = axs[1, 2]; ax.axis('off'); ax.set_xlim(0, 10); ax.set_ylim(0, 10)
    ax.text(0, 9.2, 'What gets thicker', fontsize=8, fontweight='bold')
    ax.text(0, 4.2, '- limiter finger: 2 -> 6 mm wide, 4 -> 5 mm tall\n- limiter stops: 2 -> 8 mm wide, 6 -> 9 mm tall,\n  with a full-height web into the housing\n- crown arms: 3 -> 5 mm thick, 10 mm boss\n  round the screw, fillets into the shaft\n- cam web: 3 -> 6 mm (follower is 9 mm)\n- (printed so the layers run along the arm)', fontsize=6.4, va='center')
    fig.tight_layout(); fig.savefig(path, dpi=220); plt.close(fig)

def fig_bay(path):
    fig, axs = plt.subplots(1, 3, figsize=(7.6, 3.4))
    Rb = 29.9
    for ax, (title, items) in zip(axs[:2], (('layer A (lower): battery + regulator', [('2S battery 40x18x10', -6, -8, 40, 18, YELLOW), ('regulator 5 V 3 A 25x15x8', 4, 14, 25, 15, PINK)]),
                                              ('layer B (upper): altimeter', [('altimeter 45x25x12', 0, 0, 45, 25, PURPLE), ('optional cell', 0, -22, 22, 8, '#d9d9d9')]))):
        ax.set_xlim(-34, 34); ax.set_ylim(-34, 34); ax.set_aspect('equal'); ax.axis('off'); ax.set_title(title, fontsize=7)
        ax.add_patch(Circle((0, 0), Rb, fc='none', ec=BLUE_D, lw=1.6)); ax.add_patch(Circle((0, 0), 26, fc='none', ec='#999', lw=.8, ls=':'))
        for n, cx, cy, w, h, c in items:
            ax.add_patch(Rectangle((cx - w / 2, cy - h / 2), w, h, fc=c, ec='#333', lw=.9)); ax.text(cx, cy, n, ha='center', va='center', fontsize=5.6)
        ax.text(0, -33.5, 'solid ring: bay wall R29.9; dotted: opened base ring R26', ha='center', fontsize=5.4, color=BLUE_D)
    ax = axs[2]; ax.axis('off'); ax.set_xlim(0, 10); ax.set_ylim(0, 10)
    ax.text(0, 9.4, 'Will it fit?', fontsize=8, fontweight='bold')
    ax.text(0, 4.6, 'All parts side by side use about 90 %\nof the bay floor: impossible in one\nlayer, so two layers.\n\nHeight needed (typical parts):\n 10 (battery) + 12 (altimeter)\n + 3 (trays and gaps) = 25 mm\n\nAvailable at the same overall\nlength: z -33 to -9 = 24 mm\n(base ring opened up to R26).\n\nSo it is borderline: it depends\non YOUR altimeter and battery.\nOption B below if it does not fit.', fontsize=6.2, va='center')
    fig.suptitle('Electronics bay (plan views from below). Sizes are placeholders: tell me your real parts', fontsize=8)
    fig.tight_layout(); fig.savefig(path, dpi=220); plt.close(fig)

def fig_transition(path):
    fig, axs = plt.subplots(1, 2, figsize=(7.6, 3.6))
    ax = axs[0]; ax.set_xlim(-36, 36); ax.set_ylim(-39, 40); ax.set_aspect('equal'); ax.axis('off'); ax.set_title('module bottom face, seen from below', fontsize=8)
    ax.add_patch(Circle((0, 0), 33.02, fc='none', ec='#000', lw=1.2)); ax.add_patch(Circle((0, 0), 29.5, fc=BLUE, ec=BLUE_D, alpha=.5)); ax.add_patch(Circle((0, 0), 24, fc='white', ec=BLUE_D))
    for a in (45, 135, 225, 315):
        x, y = 27 * np.cos(np.radians(a)), 27 * np.sin(np.radians(a)); ax.add_patch(Circle((x, y), 1.3, fc='white', ec='#333')); ax.add_patch(Circle((x, y), 3.2, fc='none', ec=RED, lw=.8))
    ax.add_patch(Rectangle((-5, -33), 10, 7, fc='white', ec='#333', lw=.9)); ax.text(0, -36, 'wire / switch pass', ha='center', fontsize=6)
    ax.text(0, 0, 'bay opening\n(electronics slide in\nfrom below)', ha='center', va='center', fontsize=6.5)
    ax.text(0, 36.5, '4 x M3 pilots in thick bosses (R27, red rings)', ha='center', fontsize=6, color=RED)
    ax = axs[1]; ax.set_xlim(-45, 45); ax.set_ylim(-70, 12); ax.set_aspect('equal'); ax.axis('off'); ax.set_title('stack, side view (exploded)', fontsize=8)
    ax.add_patch(Rectangle((-33.02, -16), 66.04, 16, fc=BLUE, ec=BLUE_D)); ax.text(0, -8, 'module bottom (flange + bay)', ha='center', fontsize=6.5)
    ax.add_patch(Rectangle((-33.02, -34), 66.04, 8, fc=TAN, ec='#a08040', hatch='///')); ax.text(0, -30, 'transition (BT80 side)', ha='center', fontsize=6.5, bbox=dict(fc='white', ec='none', pad=1))
    ax.add_patch(Rectangle((-33.02, -62), 66.04, 22, fc='#e8e0c0', ec='#a08040')); ax.text(0, -51, 'lower BT80 tube\n(electronics / recovery below)', ha='center', fontsize=6.5)
    for s in (1, -1):
        ax.add_patch(FancyArrowPatch((s * 27, -40), (s * 27, -14), arrowstyle='-|>', mutation_scale=9, color='#222', lw=1))
    ax.text(0, 5, 'M3 screws go up from below, through the transition, into the module', ha='center', fontsize=6)
    fig.tight_layout(); fig.savefig(path, dpi=220); plt.close(fig)

if __name__ == '__main__':
    fig_elevation(OUT + 'v4_sketch_elevation.png'); fig_thicken(OUT + 'v4_sketch_thicken.png'); fig_bay(OUT + 'v4_sketch_bay.png'); fig_transition(OUT + 'v4_sketch_transition.png')
    print('sketch figs ok')
