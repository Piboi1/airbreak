"""Ten ideas to cut fin weight: one combined lock+push feature, bare skin. Schematic drawings, not CAD. Writes docs/V6_fin_weight_ideas.pdf."""
import numpy as np, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.patches import Rectangle, Circle, Polygon, FancyArrowPatch, Arc

RHO = 1.24e-3  # g per mm3, solid PLA
V = dict(total=7197, skin=3283, push=483, lock=287, ribs=613, root=2531, tail=264)
SKIN, PUSH, LOCK, ROT, CUT, NEW = '#c9d3dc', '#e8762b', '#2e8b57', '#9aa7b5', '#d62728', '#1f77b4'
DOC = 'V6 fin: ten ideas to cut weight (schematic, not CAD)'

def frame(fig, title, sheet, n):
    fig.text(0.04, 0.955, title, fontsize=15, weight='bold')
    fig.add_artist(plt.Line2D([0.03, 0.97], [0.075, 0.075], color='k', lw=1))
    fig.text(0.04, 0.045, DOC, fontsize=9, weight='bold')
    fig.text(0.62, 0.045, 'units mm | masses solid PLA 1.24 g/cm3 | 2026-11-16', fontsize=7.5, color='#555')
    fig.text(0.96, 0.045, f'Sheet {sheet} / {n}', fontsize=9, ha='right')

def side(ax, title, push=True, lock=True, ribs=True, tail=True, skin_t=2.4, taper=False, rotor=True):
    """Side section in the radial plane: R to the right (outside = tube), z up. Hinge pin at (25, 0)."""
    ax.set_title(title, fontsize=9)
    if taper:
        ax.add_patch(Polygon([(32.2, 4), (32.2, 54), (32.2 - 1.2, 54), (32.2 - 2.4, 4)], fc=SKIN, ec='k', lw=.8))
    else:
        ax.add_patch(Rectangle((32.2 - skin_t, 4), skin_t, 50, fc=SKIN, ec='k', lw=.8))
    ax.add_patch(Circle((25, 0), 4.8, fc=SKIN, ec='k', lw=.8)); ax.add_patch(Circle((25, 0), 1.7, fc='w', ec='k', lw=.6))
    ax.add_patch(Polygon([(24, 0), (31.5, 0), (31.5, 10), (29.8, 14), (26, 4.5)], fc=SKIN, ec='k', lw=.8))
    if tail: ax.add_patch(Rectangle((22, -7.6), 4.5, 4.6, fc=SKIN, ec='k', lw=.8))
    if push: ax.add_patch(Rectangle((23, 20), 6.8, 9, fc=PUSH, ec='k', lw=.8)); ax.text(21.5, 24.5, 'push\npad', fontsize=6.5, ha='right', va='center', color=PUSH)
    if lock:
        ax.add_patch(Polygon([(20, 41.6), (22.8, 41.6), (22.8, 47), (29.8, 47), (29.8, 50), (20, 50)], fc=LOCK, ec='k', lw=.8))
        ax.text(19.5, 46, 'lock\nlug', fontsize=6.5, ha='right', va='center', color=LOCK)
    if ribs: ax.add_patch(Rectangle((27.5, 28.5), 2.3, 18.5, fc='#b0b9c3', ec='k', lw=.5, hatch='////'))
    if rotor:
        ax.add_patch(Rectangle((0, 10), 9, 34.6, fc=ROT, ec='none', alpha=.5)); ax.text(4.5, 30, 'rotor\nhub', fontsize=6.5, ha='center', va='center')
    ax.plot([32.51, 32.51], [-12, 58], color='#8a6d3b', lw=2); ax.text(32.9, 57, 'tube', fontsize=6.5, color='#8a6d3b')
    ax.plot([0, 0], [-12, 58], 'k-.', lw=.5); ax.text(0.5, -11.5, 'rotor axis', fontsize=6)
    ax.set_xlim(-1, 36); ax.set_ylim(-12, 58); ax.set_aspect('equal'); ax.tick_params(labelsize=6)
    ax.set_xlabel('R (mm)', fontsize=7); ax.set_ylabel('z (mm), hinge pin at z 0', fontsize=7)

def face(ax, title, ribs=True, push=True, lock=True, pockets=True):
    """Inner face of the fin, seen from the rocket axis: y across (+-17.3), z up."""
    ax.set_title(title, fontsize=9)
    ax.add_patch(Rectangle((-17.3, 4), 34.6, 50, fc=SKIN, ec='k', lw=.8))
    ax.add_patch(Rectangle((-7.4, -4.8), 14.8, 9.6, fc=SKIN, ec='k', lw=.8)); ax.text(0, -1, 'hinge knuckle', fontsize=6, ha='center')
    if pockets:
        for y0 in (3.8, -10.5): ax.add_patch(Rectangle((y0, 21.8), 6.7, 29, fc='w', ec='#777', lw=.5, ls='--'))
        for y0 in (2.0, -10.5): ax.add_patch(Rectangle((y0, 11.3), 8.5, 7.5, fc='w', ec='#777', lw=.5, ls='--'))
    if ribs:
        for y in (-14.8, 14.8): ax.add_patch(Rectangle((y - 1.5, 4), 3, 16, fc='#b0b9c3', ec='k', lw=.5, hatch='////')); ax.add_patch(Rectangle((y - 1.5, 30), 3, 24, fc='#b0b9c3', ec='k', lw=.5, hatch='////'))
        ax.add_patch(Rectangle((-0.9, 4), 1.8, 16.5, fc='#b0b9c3', ec='k', lw=.5, hatch='////')); ax.add_patch(Rectangle((-0.9, 28.5), 1.8, 18.5, fc='#b0b9c3', ec='k', lw=.5, hatch='////'))
    if push: ax.add_patch(Rectangle((-4, 20), 8, 9, fc=PUSH, ec='k', lw=.8))
    if lock: ax.add_patch(Rectangle((-3, 41.6), 6, 8.4, fc=LOCK, ec='k', lw=.8))
    ax.set_xlim(-20, 20); ax.set_ylim(-8, 58); ax.set_aspect('equal'); ax.tick_params(labelsize=6); ax.set_xlabel('y (mm)', fontsize=7)

def text(fig, x, y, w, lines, size=8.2):
    fig.text(x, y, '\n'.join(lines), fontsize=size, va='top', wrap=True, family='DejaVu Sans')

def arrow(ax, p, q, c=NEW, txt=None, tp=None):
    ax.add_patch(FancyArrowPatch(p, q, arrowstyle='-|>', mutation_scale=9, color=c, lw=1.2))
    if txt: ax.text(*(tp or q), txt, fontsize=6.5, color=c)

IDEAS = []
def idea(code, name, save_mm3, risk, rotor_change, fn, why, how, cons):
    IDEAS.append(dict(code=code, name=name, save=save_mm3, risk=risk, rotor=rotor_change, fn=fn, why=why, how=how, cons=cons))

# ---------------------------------------------------------------- the ten ideas
def d1(a1, a2):
    side(a1, 'today: push pad z 20..29 and lock lug z 41.6..50 are separate', rotor=True)
    side(a2, 'A1: one "cam-latch lug" does both', push=False, lock=False)
    a2.add_patch(Polygon([(21, 38), (29.8, 38), (29.8, 50), (21, 50), (21, 44), (23.5, 44), (23.5, 41)], fc=NEW, ec='k', lw=.8))
    a2.add_patch(Rectangle((14, 36), 6, 4, fc=ROT, ec='k', lw=.6)); a2.text(13.5, 35, 'rotor cam lobe\nmoved up to z 36..40', fontsize=6, ha='right')
    arrow(a2, (17, 41), (21.5, 41), txt='lobe pushes the\nunderside: OPEN', tp=(8, 52))
idea('A1', 'Cam-latch lug: one lug both pushes and locks', V['push'] + V['lock'] - 330, 'low-medium', 'cam lobes move up beside the catch caps',
     d1, ['The rotor catch finger already sits at the lug height. Move the four kick-cam lobes up to the same height,',
          'so the same lug is held closed by the finger and kicked open by the lobe a few degrees later.'],
     ['One lug R21..29.8, y +-4, z 38..50 with a ramped underside (the follower face) and the existing',
      'hook face on top. The separate push pad at z 20..29 is deleted.'],
     ['The kick now acts higher up, further from the hinge: less force needed (longer lever) but',
      'more rotor travel per degree of fin; the rotor cams have to be re-drawn.'])

def d2(a1, a2):
    side(a1, 'B: one pin on the fin, a groove in the rotor', push=False, lock=False, tail=False)
    a1.add_patch(Circle((26.5, 35), 2.0, fc=NEW, ec='k', lw=.8)); a1.add_patch(Rectangle((26.5, 33.6), 3.3, 2.8, fc=NEW, ec='k', lw=.6))
    a1.text(24, 39, 'O4 pin boss', fontsize=6.5, color=NEW, ha='right')
    ax = a2; ax.set_title('rotor groove, unrolled (angle across, fin pin radius out)', fontsize=9)
    t = np.linspace(0, 65, 200); r = np.where(t < 15, 0, np.where(t < 50, (t - 15) / 35, 1))
    ax.fill_between(t, r * 10 - 2, r * 10 + 2, color='#dbe9f6', ec=NEW); ax.plot(t, r * 10, color=NEW)
    ax.text(2, -5, 'dwell 0..15 deg:\nLOCKED closed', fontsize=7); ax.text(22, 6.5, 'ramp 15..50 deg:\npushed OPEN', fontsize=7); ax.text(51, 13, 'dwell:\nHELD open', fontsize=7)
    ax.set_xlim(-2, 68); ax.set_ylim(-9, 18); ax.set_xlabel('rotor angle (deg)', fontsize=7); ax.set_ylabel('pin travel (mm)', fontsize=7); ax.tick_params(labelsize=6)
idea('B', 'Desmodromic pin-in-groove: lock, push AND hold open with one pin', V['push'] + V['lock'] + V['tail'] - 70, 'medium', 'new groove track on the rotor (replaces lobes and caps)',
     d2, ['A groove is positive both ways: the pin cannot leave it. One small boss on the fin replaces',
          'the push pad, the lock lug and the under-hinge tail lock (the groove end-dwell holds the fin at 90 deg).'],
     ['O4 pin boss on the inner face about 10 mm above the hinge. Rotor gets a curved slot (face cam) per fin:',
      'dwell (locked) / ramp (push) / dwell (held open). The servo also pulls the fins CLOSED again.'],
     ['Biggest saving and fewest features, but a new rotor and a new assembly order (pin enters the groove',
      'as the fin goes in). Groove wear and friction in PLA: needs a test print.'])

def d3(a1, a2):
    side(a1, 'C: everything below the hinge (tail lever)', push=False, lock=False, ribs=False, tail=False)
    a1.add_patch(Polygon([(20, -2), (25, -4.8), (25, -11), (20, -11)], fc=NEW, ec='k', lw=.8)); a1.text(19.5, -9, 'tail lever', fontsize=6.5, ha='right', color=NEW)
    arrow(a1, (12, -8), (19.5, -8), txt='rotor ring\npushes in', tp=(2, -5))
    ax = a2; ax.set_title('lever: pushing the tail IN swings the fin OUT', fontsize=9)
    ax.plot([0, 0], [0, 50], color=SKIN, lw=6); ax.plot([0, 6], [0, -6], color=NEW, lw=6); ax.plot(0, 0, 'ko')
    ax.plot([0, 35], [0, 35], color=SKIN, lw=6, alpha=.4); ax.plot([0, -6], [0, -6], color=NEW, lw=6, alpha=.4)
    ax.text(2, 46, 'closed', fontsize=7); ax.text(28, 26, 'open', fontsize=7); ax.set_xlim(-12, 45); ax.set_ylim(-12, 52); ax.set_aspect('equal'); ax.axis('off')
idea('C', 'Tail-lever drive: push and lock both below the hinge', V['push'] + V['lock'] + V['ribs'] - 200, 'medium', 'cam ring at the bottom of the rotor instead of the top caps',
     d3, ['The fin already has a tail below the hinge (the 90 deg lock). Drive the fin through that tail: a rotor',
          'cam ring pushes the tail inward to swing the fin out, and the same ring traps the tail when closed.'],
     ['Fin above the hinge becomes plain skin; all mechanism stays in the stiff root zone.',
      'Tail grows to about 6 x 12 x 9 mm; the U-pocket/keepers in the housing are reused as the lock.'],
     ['Short lever (about 6-8 mm) means high tail force; the root and hinge ears carry it.',
      'Rotor cams move to the bottom: rotor and housing floor redesign.'])

def d4(a1, a2):
    side(a1, 'D: over-centre toggle link', push=False, lock=False, tail=False)
    a1.add_patch(Circle((27, 30), 1.6, fc=NEW, ec='k')); a1.plot([27, 12], [30, 22], color=NEW, lw=3); a1.add_patch(Circle((12, 22), 1.6, fc=NEW, ec='k'))
    a1.text(13, 26, 'link (printed\nor steel wire)', fontsize=6.5, color=NEW)
    ax = a2; ax.set_title('toggle: past dead centre it locks both ways', fontsize=9)
    for ang, lab in ((200, 'locked closed (just past centre)'), (110, 'pushing'), (30, 'locked open')):
        x, y = 10 * np.cos(np.radians(ang)), 10 * np.sin(np.radians(ang)); ax.plot([0, x], [0, y], 'k', lw=2); ax.plot([x, 30], [y, 0], color=NEW, lw=2); ax.text(x - 2, y + 1.5, lab, fontsize=6.5)
    ax.plot(0, 0, 'ko'); ax.plot(30, 0, 'o', color=NEW); ax.set_xlim(-22, 36); ax.set_ylim(-14, 16); ax.set_aspect('equal'); ax.axis('off')
idea('D', 'Over-centre toggle link (crank on the rotor, link to a fin pin)', V['push'] + V['lock'] + V['tail'] - 60 - 120, 'medium', 'four crank pins on the rotor; 4 small links (new parts)',
     d4, ['A crank-and-link locks itself past dead centre, so the same link holds the fin closed, pushes it open',
          'and holds it open. The fin only needs one pin hole.'],
     ['Link: 2 mm steel wire bent to a Z, or a printed 3 mm bar with two M2 pins. The fin keeps a small boss.'],
     ['Four extra parts (links) to lose or fit; slop in the pins shows up as fin rattle.'])

def d5(a1, a2):
    face(a1, 'today: spine + two edge ribs (hatched) + pockets')
    face(a2, 'E: no ribs, a 1.2 mm turned-in lip on the two long edges', ribs=False)
    for y in (-17.3, 16.1): a2.add_patch(Rectangle((y, 4), 1.2, 50, fc=NEW, ec='k', lw=.5))
idea('E', 'Bare shell with edge lips (delete spine and edge ribs)', 430, 'medium-high', 'none',
     d5, ['The fin is a curved shell: curvature already makes it stiff across the span. A thin lip on the two',
          'free edges (like a sheet-metal flange) stops the edges flapping, which is what the ribs mainly do.'],
     ['Delete the spine and both edge ribs; add a 1.2 x 1.5 mm lip on each long edge, inside only.'],
     ['The ribs were added after the friend\'s print nearly snapped: this one MUST be FEA-checked and',
      'hand-tested. Best combined with F (thicker at the root).'])

def d6(a1, a2):
    side(a1, 'F: skin tapers 2.4 mm at the hinge to 1.2 mm at the tip', ribs=False, taper=True)
    ax = a2; ax.set_title('why: bending in the skin grows toward the hinge', fontsize=9)
    z = np.linspace(4, 54, 50); ax.plot((54 - z) ** 2 / (50 ** 2), z, color=CUT, label='air-load bending moment (relative)')
    ax.plot(np.sqrt((54 - z) / 50) * 2.4 + 0.0, z, color=NEW, label='thickness for equal stress (mm)')
    ax.legend(fontsize=6.5, loc='upper right'); ax.set_xlabel('relative / mm', fontsize=7); ax.set_ylabel('z (mm)', fontsize=7); ax.tick_params(labelsize=6)
idea('F', 'Tapered skin: thick at the hinge, thin at the tip', 600, 'medium', 'none',
     d6, ['The air load bends the fin about the hinge, so the moment is largest at the root and zero at the tip.',
          'A skin that thins toward the tip has the same peak stress with much less plastic.'],
     ['Inner face becomes a cone: 2.4 mm at z 11 down to 1.2 mm at z 54. Outer (aero) face unchanged.',
      'Replaces the F1/F2 pockets.'],
     ['Thin tip edge is fragile in handling; keep 1.2 mm minimum (3 perimeters at 0.4).'])

def d7(a1, a2):
    face(a1, 'G: isogrid inner face', ribs=False, pockets=False)
    for z0 in range(12, 54, 10):
        for y0 in range(-16, 16, 8):
            a1.add_patch(Polygon([(y0, z0), (y0 + 8, z0), (y0 + 4, z0 + 8)], fc='none', ec=NEW, lw=.8))
    face(a2, 'H: corrugated (beaded) skin', ribs=False, pockets=False)
    for y in (-9, 0, 9): a2.add_patch(Rectangle((y - 2, 8), 4, 44, fc='#dbe9f6', ec=NEW, lw=.8))
idea('G/H', 'Isogrid or beaded skin: 1.0 mm skin + a light grid or 3 beads', 1300, 'medium-high', 'none',
     d7, ['Material is moved away from the middle of the skin into a grid (G) or into three shallow inward beads (H):',
          'much more stiffness per gram than a flat plate.'],
     ['G: 1.0 mm skin + 0.8 mm wide x 2 mm tall triangular grid. H: 1.2 mm skin with three 4 mm wide beads',
      'standing 1.5 mm inward. Outer face stays smooth.'],
     ['Fine features print slowly and are sensitive to layer adhesion; needs FEA and a print test.'])

def d8(a1, a2):
    side(a1, 'I: open truss root instead of a solid web + gusset', push=True, lock=True, ribs=False)
    a1.add_patch(Polygon([(26, 3), (30, 3), (28.5, 8)], fc='w', ec=CUT, lw=.8)); a1.add_patch(Polygon([(27, 9), (30.5, 9), (30.5, 12)], fc='w', ec=CUT, lw=.8))
    a1.text(33.5, 6, 'triangular\nwindows', fontsize=6.5, color=CUT)
    ax = a2; ax.set_title('where the fin mass is today (V6, 8.9 g)', fontsize=9)
    labels = ['skin z 11..54', 'root: knuckle, web,\npads, gusset, tail', 'push pad', 'lock lug', 'ribs + rims']
    vals = [V['skin'], V['root'], V['push'], V['lock'], V['ribs']]
    ax.barh(labels, [v * RHO for v in vals], color=[SKIN, '#7f8c99', PUSH, LOCK, '#b0b9c3'], ec='k')
    for i, v in enumerate(vals): ax.text(v * RHO + .05, i, f'{v*RHO:.1f} g', va='center', fontsize=7)
    ax.tick_params(labelsize=6.5); ax.set_xlim(0, 5)
idea('I', 'Lighter root: truss windows in the web and gusset', 600, 'medium', 'none',
     d8, ['A third of the fin (3.1 g) is the root: hinge knuckle, web, pads, gusset and tail. Much of the web',
          'and gusset is solid where only its edges carry load.'],
     ['Triangular windows through the web/gusset (keep 1.6 mm members); keep the knuckle, landing and tail solid.'],
     ['The root carries the 90 deg stop load: check with FEA (tools/fea_fin.py) before printing.'])

def d9(a1, a2):
    side(a1, 'J: carbon rod spine, 1.2 mm skin', push=True, lock=True, ribs=False, skin_t=1.2)
    a1.add_patch(Rectangle((29.2, 6), 1.5, 46, fc='k', ec='k')); a1.text(28.6, 52, 'O1.5 carbon rod\nin a channel', fontsize=6.5, ha='right')
    face(a2, 'J: rod along the centre line, skin 1.2 mm', ribs=False, pockets=False)
    a2.add_patch(Rectangle((-0.75, 2), 1.5, 50, fc='k'))
idea('J', 'Carbon-rod spine: a 1.5 mm CF rod carries the bending, skin to 1.2 mm', 1500, 'medium', 'none',
     d9, ['A 1.5 mm carbon rod is about 30x stiffer than PLA. Pressed into a channel on the inner face it takes',
          'the bending and the skin only has to span between the rod and the edges.'],
     ['Channel 1.6 mm, rod from just above the knuckle to the tip (about 50 mm, 0.15 g). Glue or press-fit.'],
     ['A bought part per fin (cheap: kite/RC rod). Rod must not stick out into the tube or the rotor path.'])

def d10(a1, a2):
    side(a1, 'K: magnet holds the fin closed; cam only pushes', lock=False)
    a1.add_patch(Rectangle((29.8 - 2, 48), 2, 3, fc=NEW, ec='k')); a1.text(27, 52.5, '3x2 mm magnet', fontsize=6.5, ha='right', color=NEW)
    face(a2, 'K: magnets at the tip, lug and catch caps deleted', lock=False)
    a2.add_patch(Circle((0, 50), 1.5, fc=NEW, ec='k'))
idea('K', 'Magnet lock: a 3 x 2 mm magnet replaces the lock lug (and the rotor catch caps)', V['lock'] - 60, 'low', 'catch caps deleted from the rotor (rotor lighter too)',
     d10, ['The lock only has to stop the fins drifting open before the kick; the air pushes them shut in flight.',
          'A small neodymium magnet in the fin tip and a steel disc (or magnet) in the housing rim does that.'],
     ['3 x 2 mm magnet glued in the fin tip; matching magnet in the housing; the cam still kicks the fin open',
      'and easily beats the magnet. Rotor loses its four catch caps.'],
     ['Your rule says no snap hooks or bands; magnets are neither, but confirm you are OK with them.',
      'Glue must survive the kick.'])

# ---------------------------------------------------------------- write
pages = [IDEAS[i:i + 2] for i in range(0, len(IDEAS), 2)]
N = 2 + len(pages)
with PdfPages('../docs/V6_fin_weight_ideas.pdf') as pdf:
    fig = plt.figure(figsize=(16.5, 11.7)); frame(fig, 'Sheet 1: today\'s fin and where its 8.9 g is', 1, N)
    a1 = fig.add_axes([0.05, 0.12, 0.27, 0.78]); side(a1, 'side section (fin closed)')
    a2 = fig.add_axes([0.36, 0.12, 0.27, 0.78]); face(a2, 'inner face (ribs hatched, V6 pockets dashed)')
    text(fig, 0.67, 0.9, 0.3, [
        'Fin V6 = 7,197 mm3 = 8.9 g solid PLA (each; 4 per set)', '',
        f'  skin z 11..54 ............ {V["skin"]*RHO:.1f} g  (46 %)',
        f'  root (knuckle, web, pads,  {V["root"]*RHO:.1f} g  (35 %)', '     gusset, under-hinge tail)',
        f'  push pad (cam follower) .. {V["push"]*RHO:.1f} g  ( 7 %)',
        f'  lock lug (catch) ......... {V["lock"]*RHO:.1f} g  ( 4 %)',
        f'  ribs + pocket rims ....... {V["ribs"]*RHO:.1f} g  ( 9 %)', '',
        'How it works today:',
        ' * LOCK: the rotor catch finger stands inside the lug at z 41.6..50,',
        '   so the fin cannot swing out.',
        ' * PUSH: the servo turns the rotor; after the finger has moved away,',
        '   a kick-cam lobe hits the push pad at z 20..29 and throws the fin open.',
        ' * HOLD OPEN: the tail under the hinge drops into the U-pocket at 90 deg.', '',
        'So the push and the lock are two separate features (plus the tail).',
        'The ideas on sheets 2-6 merge them (A1, B, C, D, K) and strip the skin',
        '(E, F, G/H, I, J). Savings are estimates from these volumes, not FEA.'], size=9.5)
    pdf.savefig(fig); plt.close(fig)
    for k, pg in enumerate(pages):
        fig = plt.figure(figsize=(16.5, 11.7)); frame(fig, f'Sheet {k+2}: ideas ' + ' and '.join(i['code'] for i in pg), k + 2, N)
        for j, it in enumerate(pg):
            y0 = 0.52 if j == 0 else 0.10
            a1 = fig.add_axes([0.03, y0, 0.2, 0.37]); a2 = fig.add_axes([0.25, y0, 0.2, 0.37]); it['fn'](a1, a2)
            fig.text(0.49, y0 + 0.37, f"{it['code']}: {it['name']}", fontsize=11, weight='bold', va='top')
            fig.text(0.49, y0 + 0.33, f"saves about {it['save']*RHO:.1f} g per fin ({4*it['save']*RHO:.1f} g per set)   |   risk: {it['risk']}   |   rotor: {it['rotor']}",
                     fontsize=8.5, color=NEW, va='top')
            text(fig, 0.49, y0 + 0.29, 0.48, ['IDEA'] + it['why'] + ['', 'WHAT CHANGES'] + it['how'] + ['', 'CATCH'] + it['cons'], size=8.2)
        pdf.savefig(fig); plt.close(fig)
        if k == 0: pass
    fig = plt.figure(figsize=(16.5, 11.7)); frame(fig, f'Sheet {N}: comparison and the combinations worth building', N, N)
    ax = fig.add_axes([0.04, 0.42, 0.92, 0.48]); ax.axis('off')
    rows = [[i['code'], i['name'], f"{i['save']*RHO:.1f}", f"{4*i['save']*RHO:.1f}", i['risk'], i['rotor']] for i in IDEAS]
    tb = ax.table(cellText=rows, colLabels=['', 'idea', 'g / fin', 'g / set', 'risk', 'rotor / other parts'], loc='upper left',
                  colWidths=[.04, .46, .06, .06, .09, .29], cellLoc='left')
    tb.auto_set_font_size(False); tb.set_fontsize(8.5); tb.scale(1, 1.9)
    text(fig, 0.05, 0.38, 0.9, [
        'COMBINATIONS (savings do not simply add; estimates):',
        ' 1. "Bare fin" (closest to what you asked):  B (one pin locks, pushes and holds open)  +  J (1.2 mm skin on a carbon rod, no ribs)  +  I (truss root)',
        '      fin about 8.9 g -> about 5.1 g, set about 15 g lighter. Biggest change: new rotor with grooves, a bought rod per fin.',
        ' 2. Low-risk step first:  A1 (cam-latch lug)  +  F (tapered skin)          fin about 8.9 g -> about 7.6 g. Rotor cams move up, rest unchanged.',
        ' 3. No rotor change at all:  I + J (truss root, carbon rod, 1.2 mm skin)    fin about 8.9 g -> about 6.3 g. Push pad and lug stay as they are.', '',
        'NEXT STEP: pick 1-3 ideas. I model them offline (no Onshape calls), run the same FEA as before (tools/fea_fin.py: 12 N / 30 N air load and 15 N tip)',
        'and compare stress and deflection with today\'s fin, then build only the chosen one in Onshape (about 10 requests).'], size=10)
    pdf.savefig(fig); plt.close(fig)
print('ok', N, 'sheets')
