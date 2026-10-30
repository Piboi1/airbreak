"""Figures for the V3 mechanics document: staged half-section renders, plan sections, side schematic, charts, load path."""
import math, json, pickle, os, numpy as np, trimesh
from PIL import Image, ImageDraw
import figures as F, render, run

W = os.environ['AIRBRAKE_WORK']
DATA = json.load(open(f'{W}/mech_data.json'))
parts = {n: m for _, (n, m) in pickle.load(open(f'{W}/fin_v3_parts.pkl', 'rb')).items()}
Rz = lambda d: trimesh.transformations.rotation_matrix(math.radians(d), [0, 0, 1])
def hinge(op, az=0):
    T = trimesh.transformations.rotation_matrix(math.radians(op), [0, 1, 0], point=[25, 0, 0])
    return Rz(az) @ T @ Rz(-az)

ROT_TOK = lambda t: t in ('R', 'EH') or (t[:1] == 'L' and t[1:].isdigit()) or t.startswith(('HW_L', 'HW_horn'))
def fin_idx(t):
    if t[:1] == 'P' and t[1:].isdigit(): return int(t[1:])
    if t[:2] == 'TP': return int(t[2:])
    return None

def posed(rot, op):
    """Copy of all parts with the rotor group turned by rot deg and every fin (+ glued cut-out) opened by op deg."""
    out = {}
    for name, m in parts.items():
        t = F.tok(name); mm = m.copy()
        i = fin_idx(t)
        if ROT_TOK(t): mm.apply_transform(Rz(rot))
        elif i is not None: mm.apply_transform(hinge(op, 90 * (i - 1)))
        out[name] = mm
    return out

HIDE = ('REF', 'HW')
def half_section(rot, op, name, label_lines):
    """Cut-away: everything is cut by the plane y=0 and the y>0 half removed, looking at the cut face (fins 1 and 3 swing in the picture)."""
    P = posed(rot, op)
    keep = {}
    for nm, m in P.items():
        t = F.tok(nm)
        if t.startswith(HIDE) or t in ('P2', 'P4', 'TP2', 'TP4'): continue
        try:
            mm = trimesh.intersections.slice_mesh_plane(m, plane_normal=[0, -1, 0], plane_origin=[0, 0, 0], cap=True)
        except Exception:
            try: mm = trimesh.intersections.slice_mesh_plane(m, plane_normal=[0, -1, 0], plane_origin=[0, 0, 0], cap=False)
            except Exception: mm = m
        if len(mm.faces): keep[nm] = mm
    items = F.build(keep, lambda t, nm, m: ((0, 0, 0), None))
    img, meta = render.render(items, az=90, el=6, size=(1100, 1050), scale=6.3, center=np.array([0, 0, 2]))
    dr = ImageDraw.Draw(img)
    y = 14
    for txt, size in label_lines:
        dr.text((16, y), txt, font=render.font(size), fill=(20, 20, 20)); y += size + 8
    img = img.crop((0, 0, 1100, 840)); img.save(F.OUT + name)
    return img


STATES = [('mech_s0.png', 0, 0, [('1  LOCKED', 40), ('servo 0°, rotor 0°, fins closed', 28), ('finger holds each fin lug', 26)]),
          ('mech_s1.png', 14, 0, [('2  UNLATCHED', 40), ('rotor 14°: fingers have slid off the lugs', 26), ('cams not touching yet', 26)]),
          ('mech_s2.png', 40, 7.1, [('3  CAM KICK', 40), ('rotor 40°: cams push the fins', 26), ('fin opening 7° (cam-driven)', 26)]),
          ('mech_s3.png', 65, 14.2, [('4  KICKED', 40), ('rotor 65° (servo end of travel)', 26), ('cam holds fins open 14°', 26)]),
          ('mech_s4.png', 65, 90, [('5  AIRFLOW OPEN', 40), ('airflow carries the fins to 90°', 26), ('hard stop takes the drag', 26)])]


import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib.patches import FancyArrowPatch, Rectangle, FancyBboxPatch

def sec_segs(m, origin, normal, cols):
    try:
        sec = m.section(plane_origin=origin, plane_normal=normal)
    except Exception:
        return []
    if sec is None: return []
    return [sec.vertices[e.points][:, cols] for e in sec.entities]

def draw_part(ax, m, origin, normal, cols, color, lw=1.2, label=None, fill=None):
    segs = sec_segs(m, origin, normal, cols)
    if not segs: return None
    ax.add_collection(LineCollection(segs, colors=color, linewidths=lw))
    return np.concatenate(segs).mean(0)

def by_tok(P):
    return {F.tok(n): m for n, m in P.items()}

def fig_side(path):
    """Side view (section y=0, fin 1 on the right, fin 3 on the left): closed, kicked 14 deg, airflow-open 90 deg."""
    fig, ax = plt.subplots(figsize=(7.4, 6.2))
    cols = [0, 2]
    for rot, op, col, lw, ls in [(0, 0, '#222222', 1.4, '-'), (65, 14.2, '#e8762b', 1.1, '-'), (65, 90, '#e8b48a', 1.0, '-')]:
        T = by_tok(posed(rot, op))
        for t in ('P1', 'TP1'):
            draw_part(ax, T[t], [0, 0, 0], [0, 1, 0], cols, col, lw)
        if (rot, op) != (65, 90):
            draw_part(ax, T['R'], [0, 0, 0], [0, 1, 0], cols, '#2e8b57' if rot == 0 else '#8fcfa8', lw)
            draw_part(ax, T['L1'], [0, 0, 0], [0, 1, 0], cols, '#1c6b3c' if rot == 0 else '#9cc7ad', lw)
    T0 = by_tok(posed(0, 0))
    for t in ('C1', 'C2'): draw_part(ax, T0[t], [0, 0, 0], [0, 1, 0], cols, '#6a9fcf', 0.9)
    draw_part(ax, T0['E'], [0, 0, 0], [0, 1, 0], cols, '#777777', 1.0)
    ax.plot([25], [0], 'o', color='crimson', ms=7)
    ax.annotate('hinge axis (R25, z0)\nscrew H, fin turns about it', (25, 0), (36, -16), fontsize=7, color='crimson', arrowprops=dict(arrowstyle='->', color='crimson', lw=.8))
    ax.annotate('fin tip (closed)', (31.5, 54), (38, 63), fontsize=7, arrowprops=dict(arrowstyle='->', lw=.7))
    ax.annotate('cam follower on the fin\n(z 20..29)', (30, 24.5), (47, 18), fontsize=7, color='#b04a00', arrowprops=dict(arrowstyle='->', color='#b04a00', lw=.7))
    ax.annotate('kick cam on the rotor', (-24, 23.5), (-52, 12), fontsize=7, color='#1c6b3c', arrowprops=dict(arrowstyle='->', color='#1c6b3c', lw=.7))
    ax.annotate('fin lug (latch)', (21.5, 45), (-6, 58), fontsize=7, color='#b04a00', arrowprops=dict(arrowstyle='->', color='#b04a00', lw=.7))
    ax.annotate('catch-cap finger', (26, 43.5), (47, 38), fontsize=7, color='#1c6b3c', arrowprops=dict(arrowstyle='->', color='#1c6b3c', lw=.7))
    ax.annotate('SG90 (fixed, flush with housing bottom)', (0, -22), (12, -40), fontsize=7, color='#555555', arrowprops=dict(arrowstyle='->', lw=.6, color='#555555'))
    ax.annotate('rotor + horn turn about z', (0, 66), (-26, 70), fontsize=7, color='#1c6b3c')
    ax.text(-58, 84, 'black = closed (locked)   orange = cam-kicked 14\u00b0 (rotor 65\u00b0)   light orange = airflow-open 90\u00b0 (stopped)', fontsize=7)
    # wind arrow
    ax.add_patch(FancyArrowPatch((70, 80), (70, 56), arrowstyle='-|>', mutation_scale=12, color='#3366cc'))
    ax.text(72, 68, 'relative wind\n(rocket climbing)', fontsize=7, color='#3366cc')
    ax.set_xlim(-60, 84); ax.set_ylim(-45, 88); ax.set_aspect('equal'); ax.grid(alpha=.2)
    ax.set_xlabel('x (mm)', fontsize=8); ax.set_ylabel('z (mm)', fontsize=8); ax.tick_params(labelsize=6)
    ax.set_title('Side section through fin 1 (right) and fin 3 (left); housing and servo outlined', fontsize=9)
    fig.tight_layout(); fig.savefig(path, dpi=220); plt.close(fig)

def fig_latch_stages(path):
    """Plan sections at z=43.5: finger vs lug at rotor 0, 10, 14, 20 deg (fin 3 deg out once free)."""
    fig, axs = plt.subplots(1, 4, figsize=(7.6, 2.5))
    for ax, (rot, op) in zip(axs, [(0, 0), (10, 0), (15, 0), (20, 4)]):
        T = by_tok(posed(rot, op))
        for t, c in (('P1', '#e8762b'), ('L1', '#2e8b57'), ('R', '#9bc9a9')):
            draw_part(ax, T[t], [0, 0, 43.5], [0, 0, 1], [0, 1], c, 1.5)
        ax.set_xlim(14, 36); ax.set_ylim(-12, 14); ax.set_aspect('equal'); ax.grid(alpha=.25)
        ax.set_title(f'rotor {rot}\u00b0' + (f', fin {op}\u00b0' if op else ''), fontsize=7.5); ax.tick_params(labelsize=5)
    fig.suptitle('Latch, plan section z = 43.5 (orange: fin lug wall and shell, green: catch-cap finger). The finger slides off the lug between 10\u00b0 and 15\u00b0.', fontsize=7)
    fig.tight_layout(); fig.savefig(path, dpi=220); plt.close(fig)

def fig_cam_stages(path):
    """Plan sections at z=23.5 through the cams and the fin followers."""
    fig, axs = plt.subplots(1, 4, figsize=(7.6, 2.7))
    cam = dict(DATA['cam'])
    for ax, rot in zip(axs, (0, 30, 45, 65)):
        op = np.interp(rot, [c[0] for c in DATA['cam']], [c[1] for c in DATA['cam']])
        T = posed(rot, op)
        for nm, m in T.items():
            t = F.tok(nm)
            if t == 'R': draw_part(ax, m, [0, 0, 23.5], [0, 0, 1], [0, 1], '#2e8b57', 1.4)
            elif t[:1] == 'P' and t[1:].isdigit(): draw_part(ax, m, [0, 0, 23.5], [0, 0, 1], [0, 1], '#e8762b', 1.2)
            elif t in ('C1', 'C2'): draw_part(ax, m, [0, 0, 23.5], [0, 0, 1], [0, 1], '#6a9fcf', .7)
        ax.set_xlim(-36, 36); ax.set_ylim(-36, 36); ax.set_aspect('equal'); ax.grid(alpha=.2)
        ax.set_title(f'rotor {rot}\u00b0, fins {op:.0f}\u00b0', fontsize=7.5); ax.tick_params(labelsize=5)
    fig.suptitle('Cam, plan section z = 23.5 (green: four-lobe rotor cam, orange: fin shell + follower). The lobes push the four followers outward.', fontsize=7)
    fig.tight_layout(); fig.savefig(path, dpi=220); plt.close(fig)

def fig_curve(path):
    fig, ax = plt.subplots(figsize=(7.2, 3.6))
    r_c = [c[0] for c in DATA['cam']]; o_c = [c[1] for c in DATA['cam']]
    ax.plot(r_c, o_c, '-o', color='#e8762b', ms=3, label='fin opening forced by the cam (minimum)')
    r_l = [c[0] for c in DATA['latch_max_open']]; o_l = [min(c[1], 3) for c in DATA['latch_max_open']]
    ax.plot(r_l, o_l, '-', color='#2e8b57', label='fin opening the latch allows (capped at 3\u00b0 in the plot)')
    ax.axvspan(0, 14, color='#2e8b57', alpha=.08); ax.axvspan(26, 55, color='#e8762b', alpha=.08); ax.axvspan(55, 65, color='#999999', alpha=.15)
    ax.text(1, 15.2, 'LATCHED\nfingers hold the lugs', fontsize=7, color='#1c6b3c'); ax.text(26.5, 3.0, 'CAM KICK\n~0.5\u00b0 fin per 1\u00b0 rotor', fontsize=7, color='#b04a00')
    ax.text(55.5, 6.5, 'DWELL\nrotor at end\nof travel', fontsize=7, color='#555555')
    ax.axvline(14, color='#2e8b57', ls='--', lw=.8); ax.axvline(26, color='#e8762b', ls='--', lw=.8)
    ax.text(14.4, 10.5, 'latch lets go ~14\u00b0', fontsize=7, color='#1c6b3c'); ax.text(26.4, 10.5, 'cam first moves fin ~26\u00b0', fontsize=7, color='#b04a00')
    ax.set_xlim(0, 70); ax.set_ylim(0, 17); ax.set_xlabel('servo / rotor angle (deg), counter-clockwise seen from the nose', fontsize=8); ax.set_ylabel('fin opening (deg)', fontsize=8)
    ax.grid(alpha=.25); ax.legend(fontsize=7, loc='upper left', bbox_to_anchor=(0.0, 0.8)); ax.tick_params(labelsize=7)
    ax.set_title('Timing measured on the CAD: latch window and cam kick against rotor angle (airflow takes the fin from ~14\u00b0 to 90\u00b0)', fontsize=8)
    fig.tight_layout(); fig.savefig(path, dpi=220); plt.close(fig)

def fig_loadpath(path):
    fig, ax = plt.subplots(figsize=(7.4, 5.4)); ax.axis('off'); ax.set_xlim(0, 100); ax.set_ylim(-1, 78)
    def box(x, y, w, h, t, fc):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle='round,pad=0.4', fc=fc, ec='#444', lw=.8)); ax.text(x + w / 2, y + h / 2, t, ha='center', va='center', fontsize=6.6)
    def arr(a, b, t='', c='#333', tx=0, ty=0.8):
        ax.add_patch(FancyArrowPatch(a, b, arrowstyle='-|>', mutation_scale=10, color=c, lw=1))
        if t: ax.text((a[0] + b[0]) / 2 + 1 + tx, (a[1] + b[1]) / 2 + ty, t, fontsize=5.8, color=c)
    GR, OR, BL, GY, WI = '#cfe8d8', '#fbd9bd', '#cfe0f2', '#e3e3e3', '#e6e6ff'
    ax.text(1, 76, 'Who pushes on whom (arrows point to the part that receives the force or torque)', fontsize=8)
    # row 1: drive chain
    box(1, 62, 17, 9, 'Flight computer\nservo command', GY); box(24, 62, 17, 9, 'SG90 servo\n(body fixed)', GY)
    box(47, 62, 17, 9, 'Horn + M2 screw', GR); box(70, 62, 28, 9, 'Rotor: hub, shaft, 4 cams,\n4 crown arms + catch caps', GR)
    arr((18, 66.5), (24, 66.5)); arr((41, 66.5), (47, 66.5), 'torque'); arr((64, 66.5), (70, 66.5), 'torque')
    # row 2: the two rotor jobs
    box(60, 42, 18, 9, 'Catch-cap fingers\n(rotor angle 0 → 14°)', GR); box(82, 42, 16, 9, 'Kick cams\n(26 → 65°)', GR)
    arr((79, 62), (70, 51), 'holds'); arr((90, 62), (90, 51), 'pushes')
    # row 3: fins
    box(60, 22, 18, 9, 'Fin lugs', OR); box(82, 22, 16, 9, 'Fin followers', OR)
    arr((69, 42), (69, 31), 'finger stops lug'); arr((90, 42), (90, 31), 'cam pushes follower')
    box(30, 22, 22, 9, 'Fins P1-P4 + glued\nBT80 cut-outs', OR)
    arr((60, 26.5), (52, 26.5), c='#aa5500'); arr((82, 26.5), (78, 26.5), c='#aa5500', ty=3)
    box(30, 42, 22, 9, 'Airflow\n(opens fins; suction pulls\nclosed fins outward)', WI); arr((41, 42), (41, 31), 'pushes fins', c='#3355bb')
    # row 4: structure
    box(2, 22, 22, 9, '90° hard stop\n(landing flat + stop block)', BL); arr((30, 26.5), (24, 26.5), 'at 90°', c='#335588')
    box(30, 4, 22, 9, 'M4 hinge screws\n(fins turn on them)', BL); arr((41, 22), (41, 13), 'hinge reaction', c='#335588')
    box(2, 4, 22, 9, 'Housing halves C1 / C2\n(seam screws, bearings)', BL); arr((30, 8.5), (24, 8.5), c='#335588'); arr((13, 22), (13, 13), c='#335588')
    box(60, 4, 38, 9, 'Posts → servo flange (servo reaction)\nSleeve pads → lower tube; strips → upper tube', BL)
    ax.plot([13, 13, 79], [4, 1, 1], color='#335588', lw=1); arr((79, 1), (79, 3.6), c='#335588'); ax.text(30, 1.6, 'housing carries every reaction to the posts, pads and strips', fontsize=5.8, color='#335588')
    ax.text(60, 17, 'finger reaction goes straight\nthrough the rotor axis (no torque)', fontsize=5.8, color='#1c6b3c')
    fig.tight_layout(); fig.savefig(path, dpi=220); plt.close(fig)

def fig_motion_map(path):
    """Cut-away at rest recoloured by motion class, with rotation / hinge arrows."""
    P = posed(0, 0); keep = {}
    for nm, m in P.items():
        t = F.tok(nm)
        if t.startswith(HIDE) or t in ('P2', 'P4', 'TP2', 'TP4'): continue
        try: mm = trimesh.intersections.slice_mesh_plane(m, plane_normal=[0, -1, 0], plane_origin=[0, 0, 0], cap=True)
        except Exception: mm = m
        if len(mm.faces): keep[nm] = mm
    FIX = (.45, .62, .82); ROTC = (.30, .72, .45); FINC = (.95, .50, .18); SERVO = (.40, .42, .48)
    def spec(t, nm, m):
        if t == 'E': return ((0, 0, 0), SERVO)
        if ROT_TOK(t): return ((0, 0, 0), ROTC)
        if fin_idx(t) is not None: return ((0, 0, 0), FINC)
        return ((0, 0, 0), FIX)
    items = F.build(keep, spec)
    img, meta = render.render(items, az=90, el=6, size=(1100, 1050), scale=6.3, center=np.array([0, 0, 2]))
    dr = ImageDraw.Draw(img)
    def arc(center, r, a0, a1, plane, col, w=5):
        pts = []
        for a in np.linspace(a0, a1, 40):
            ar = math.radians(a)
            if plane == 'xz': p = (center[0] + r * math.cos(ar), 0, center[2] + r * math.sin(ar))
            else: p = (center[0] + r * math.cos(ar), center[1] + r * math.sin(ar), center[2])
            pts.append(render.project(meta, p))
        dr.line(pts, fill=col, width=w)
        (x0, y0), (x1, y1) = pts[-2], pts[-1]
        ang = math.atan2(y1 - y0, x1 - x0)
        for da in (2.6, -2.6):
            dr.line([(x1, y1), (x1 - 22 * math.cos(ang + da * 0.2), y1 - 22 * math.sin(ang + da * 0.2))], fill=col, width=w)
    arc((0, 0, 62), 14, 10, 300, 'xy', (20, 120, 60))
    arc((25, 0, 0), 62, 88, 12, 'xz', (210, 90, 0))
    arc((-25, 0, 0), 62, 92, 168, 'xz', (210, 90, 0))
    f = render.font(30)
    dr.text((380, 60), 'rotor + horn + 4 catch caps:', font=f, fill=(20, 120, 60)); dr.text((380, 96), 'turn 0\u219265\u00b0 about z', font=f, fill=(20, 120, 60))
    dr.text((20, 520), 'fins + glued cut-outs:', font=f, fill=(210, 90, 0)); dr.text((20, 556), 'hinge 0\u219290\u00b0', font=f, fill=(210, 90, 0))
    dr.text((20, 860), 'housing, tubes, screws, posts, pads: fixed', font=f, fill=(40, 90, 150))
    dr.text((430, 905), 'servo: fixed (only its shaft turns)', font=f, fill=(60, 60, 70))
    dr.text((16, 14), 'What moves in V3', font=render.font(40), fill=(20, 20, 20))
    img = img.crop((0, 0, 1100, 950)); img.save(path)

def all_figs():
    for fn, rot, op, lab in STATES: half_section(rot, op, fn, lab)
    fig_side(F.OUT + 'mech_side.png'); fig_latch_stages(F.OUT + 'mech_latch.png'); fig_cam_stages(F.OUT + 'mech_cam.png')
    fig_curve(F.OUT + 'mech_curve.png'); fig_loadpath(F.OUT + 'mech_loadpath.png'); fig_motion_map(F.OUT + 'mech_map.png')
    print('all mech figs ok')

if __name__ == '__main__':
    all_figs()
