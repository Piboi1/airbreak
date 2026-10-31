import math, pickle, os, numpy as np, trimesh
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
import figures as F, render, run, osapi
from mech_figs import draw_part, by_tok, Rz

W = os.environ['AIRBRAKE_WORK']
d = run.ids(); did, wid = d['did'], d['wid']
p4 = F.load('fin_v4'); p3 = F.load('fin_v3')
raw4 = {n: m for _, (n, m) in pickle.load(open(f'{W}/fin_v4_parts.pkl', 'rb')).items()}
raw3 = {n: m for _, (n, m) in pickle.load(open(f'{W}/fin_v3_parts.pkl', 'rb')).items()}

# --- Onshape renders
vm = osapi.view_matrix(-40, 22)
osapi.shaded_view(did, wid, d['ps_v4'], F.OUT + 'v4_assembled.png', vm, w=900, h=1400)
osapi.shaded_view(did, wid, d['ps_v4b'], F.OUT + 'v4_open.png', vm, w=1000, h=1400)

# --- exploded view
def overview_v4(parts):
    def spec(t, name, m):
        if t == 'REF_upper': return ((0, 0, 150), None)
        if t.startswith('HW_top-tube'): return (F.rot_z((16, 0, 0), F.mesh_az(m)) + np.array([0, 0, 150]), None)
        if t == 'E': return ((0, 0, 58), None)
        if t.startswith('HW_servo'): return ((0, 0, 58), None)
        if t == 'EH': return ((0, 0, 40), None)
        if t == 'HW_horn': return ((0, 0, -30), None)
        if t.startswith('TP'): return (F.rot_z((58, 0, 0), F.az_of(name, t)), None)
        if t.startswith('P') and t[1:].isdigit(): return (F.rot_z((30, 0, 0), F.az_of(name, t)), None)
        if t.startswith('HW_H'): return (F.rot_z((30, 0, 0), F.az_of(name, t)) + F.rot_z((0, -26, 0), F.az_of(name, t)), None)
        if t.startswith('HW_seam'): return (np.array([-20, 20, 0]) * 1.0, None)
        if t == 'N': return ((0, 0, -45), None)
        if t in ('E2', 'E3', 'E4'): return ((0, 0, -45), None)
        if t == 'T': return ((0, 0, -95), None)
        if t.startswith('HW_transition'): return ((0, 0, -20), None)
        if t == 'REF_lower': return ((0, 0, -125), None)
        return ((0, 0, 0), None)
    return spec
items = F.build(p4, overview_v4(p4)); img, meta = render.render(items, az=-55, el=20, size=(1500, 2600)); img.save(F.OUT + 'v4_overview_exploded.png')

# --- side section to scale
def fig_side_v4(path):
    fig, ax = plt.subplots(figsize=(7.6, 7.0)); cols = [0, 2]
    T = by_tok({n: m for n, m in raw4.items()})
    for t, c, lw in (('C1', '#6a9fcf', .9), ('C2', '#6a9fcf', .9), ('R', '#2e8b57', 1.2), ('L1', '#1f6b3c', 1.1), ('L3', '#1f6b3c', 1.1), ('P1', '#e8762b', 1.2), ('P3', '#e8762b', 1.2),
                     ('TP1', '#e8762b', .8), ('E', '#777777', 1.0), ('EH', '#c9a227', 1.0), ('E2', '#8a5bc4', 1.0), ('E3', '#d06a80', 1.0), ('E4', '#d4b020', 1.0), ('N', '#2a9d8f', .8), ('T', '#a08040', 1.0)):
        if t in T: draw_part(ax, T[t], [0, 0, 0], [0, 1, 0], cols, c, lw)
    for lab, xy, tx, c in (('SG90, flipped, top 9.1 mm above the housing', (0, 64), (-30, 78), '#555'), ('flange ledges (z 45.1-49.4)', (24, 47), (36, 60), '#3d6fa3'), ('thick arms 5 mm + cap clips', (-16, 36), (-62, 52), '#1f6b3c'),
                           ('cam web 5.5 mm', (-24, 25), (-62, 22), '#1f6b3c'), ('limiter finger (bottom, 6 mm)', (-9, -3), (-62, 4), '#0a0'), ('bay ceiling', (-20, -9), (-62, -14), '#3d6fa3'),
                           ('Mercury V1 + regulator', (0, -16), (14, -4), '#8a5bc4'), ('2S battery', (0, -30), (24, -22), '#a08000'), ('transition (BT80 side)', (-28, -39.5), (-62, -48), '#806020')):
        ax.annotate(lab, xy, tx, fontsize=6.6, color=c, arrowprops=dict(arrowstyle='->', color=c, lw=.6))
    ax.plot([-33, 33, 33, -33, -33], [-35.5, -35.5, 58.8, 58.8, -35.5], 'k--', lw=1)
    ax.text(-62, 80, 'dashed box: housing, 94.3 mm tall, 66 mm OD', fontsize=7)
    ax.set_xlim(-66, 66); ax.set_ylim(-56, 86); ax.set_aspect('equal'); ax.grid(alpha=.15); ax.tick_params(labelsize=6)
    ax.set_xlabel('x (mm)', fontsize=7); ax.set_ylabel('z (mm)', fontsize=7); ax.set_title('V4 side section from the CAD model (fins 1 and 3 closed)', fontsize=9)
    fig.tight_layout(); fig.savefig(path, dpi=220); plt.close(fig)
fig_side_v4(F.OUT + 'v4_side.png')

# --- bay plan sections from the model
def fig_bay_v4(path):
    fig, axs = plt.subplots(1, 3, figsize=(7.6, 3.1))
    for ax, z, title in zip(axs, (-14.0, -28.0, -33.0), ('z = -14: upper layer', 'z = -28: battery layer', 'z = -33: bosses, sled ribs')):
        for nm, m in raw4.items():
            t = F.tok(nm)
            if t.startswith(('REF', 'TP', 'HW')) or (t[:1] == 'P' and t[1:].isdigit()) or (t[:1] == 'L' and t[1:].isdigit()) or t in ('R', 'E', 'EH'): continue
            col = {'C1': '#2f6fa8', 'C2': '#5a9bd0', 'N': '#2a9d8f', 'E2': '#8a5bc4', 'E3': '#d06a80', 'E4': '#d4b020', 'T': '#a08040'}.get(t, '#555')
            draw_part(ax, m, [0, 0, z], [0, 0, 1], [0, 1], col, 1.2)
        ax.set_xlim(-36, 36); ax.set_ylim(-36, 36); ax.set_aspect('equal'); ax.grid(alpha=.2); ax.set_title(title, fontsize=7.5); ax.tick_params(labelsize=5.5)
    fig.suptitle('Electronics bay, plan sections of the V4 model (mm). Teal: sled, purple: Mercury V1, pink: regulator, yellow: battery', fontsize=7)
    fig.tight_layout(); fig.savefig(path, dpi=220); plt.close(fig)
fig_bay_v4(F.OUT + 'v4_bay.png')

# --- thicker parts, before (V3) and after (V4), from the models
def fig_thick_v4(path):
    fig, axs = plt.subplots(2, 2, figsize=(7.6, 6.0))
    def sec(ax, parts, toks, z, lim, title):
        T = by_tok(parts)
        for t, c in toks:
            if t in T: draw_part(ax, T[t], [0, 0, z], [0, 0, 1], [0, 1], c, 1.4)
        ax.set_xlim(*lim[0]); ax.set_ylim(*lim[1]); ax.set_aspect('equal'); ax.grid(alpha=.2); ax.set_title(title, fontsize=7.5); ax.tick_params(labelsize=5.5)
    sec(axs[0, 0], raw3, (('R', '#2e8b57'), ('L1', '#1f6b3c')), 38.0, ((-2, 30), (-12, 12)), 'V3 crown arm + cap, section z = 38 (arm 3 mm thick, 5 mm wide)')
    sec(axs[0, 1], raw4, (('R', '#2e8b57'), ('L1', '#1f6b3c')), 36.0, ((-2, 30), (-12, 12)), 'V4 crown arm + cap, section z = 36 (arm 5 mm thick, 8 mm wide)')
    sec(axs[1, 0], raw3, (('R', '#2e8b57'), ('C1', '#2f6fa8'), ('C2', '#5a9bd0')), 54.0, ((-22, 22), (-22, 22)), 'V3 knob finger + stops (top), section z = 54')
    sec(axs[1, 1], raw4, (('R', '#2e8b57'), ('C1', '#2f6fa8'), ('C2', '#5a9bd0')), -3.0, ((-22, 22), (-22, 22)), 'V4 limiter (bottom), section z = -3 (finger 6 mm, stops 7.6 mm)')
    fig.tight_layout(); fig.savefig(path, dpi=220); plt.close(fig)
fig_thick_v4(F.OUT + 'v4_thicker.png')
print('v4 figs ok')

# --- wiring / power diagram
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
def fig_wiring(path):
    fig, ax = plt.subplots(figsize=(7.4, 3.9)); ax.axis('off'); ax.set_xlim(0, 100); ax.set_ylim(0, 54)
    def box(x, y, w, h, t, fc):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle='round,pad=0.4', fc=fc, ec='#444', lw=.9)); ax.text(x + w / 2, y + h / 2, t, ha='center', va='center', fontsize=6.6)
    def arr(a, b, t='', c='#333', ty=1.2, ls='-'):
        ax.add_patch(FancyArrowPatch(a, b, arrowstyle='-|>', mutation_scale=10, color=c, lw=1.2, linestyle=ls))
        if t: ax.text((a[0] + b[0]) / 2, (a[1] + b[1]) / 2 + ty, t, fontsize=6, color=c, ha='center')
    box(1, 30, 20, 14, '2S LiPo\n7.4 V\n(placeholder 40x18x10)', '#f6e7a0')
    box(28, 30, 18, 14, 'switch / arming\njumper\n(reach it through\nthe transition)', '#e3e3e3')
    box(53, 30, 20, 14, '5 V, 3 A regulator\n(placeholder 25x15x8)\n+ 470-1000 uF at the servo', '#f3b3c0')
    box(80, 30, 19, 14, 'SG90 servo\nred: 5 V\nbrown: GND\norange: signal', '#c8c8cc')
    box(30, 4, 40, 15, 'Mercury V1 altimeter\n(own 50 mAh cell, USB-C charge)\ndirect servo output + GND', '#d9c4ee')
    arr((21, 37), (28, 37), '7.4 V'); arr((46, 37), (53, 37)); arr((73, 40), (80, 40), '+5 V', '#c00')
    arr((73, 34), (80, 34), 'GND', '#555')
    arr((70, 14), (89.5, 30), '', '#1a56b0'); ax.text(44, 23.5, 'servo signal (direct servo pad: check the Mercury manual)', fontsize=6, color='#1a56b0')
    ax.plot([50, 50, 84], [4, 1.5, 1.5], color='#555', lw=1, ls='--'); ax.plot([84, 84], [1.5, 30], color='#555', lw=1, ls='--')
    ax.text(51, 2.6, 'common ground: regulator, servo, Mercury', fontsize=6, color='#555')
    ax.text(1, 50, 'Power and signal (sketch). The servo is powered by the regulator, not by the Mercury; the Mercury only sends the position signal.', fontsize=7)
    fig.tight_layout(); fig.savefig(path, dpi=220); plt.close(fig)
fig_wiring(F.OUT + 'v4_wiring.png')
print('wiring ok')
