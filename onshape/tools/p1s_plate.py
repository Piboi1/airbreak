"""Lay the V5 print set out on ONE Bambu Lab P1S plate (256 x 256 mm bed): module housing, rotor, 4 fins, head cup, head lid + 4 spare fins.
Writes exports/v5/P1S_one_plate_full_set.3mf (separate objects at their plate positions), the same as one STL, and a layout picture."""
import os, sys, glob, numpy as np, trimesh
from shapely.geometry import MultiPoint, box
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
P = '../exports/v5/print/'
BED = 256.0; MARGIN = 6.0; GAP = 6.0
L = lambda f: trimesh.load(P + f)
fin = L('P_fin_x4.stl')
parts = [  # name, mesh, lower-left corner (x, y) of its bounding box on the plate
    ('housing', L('C_module_housing_x1.stl'), (MARGIN, MARGIN)),
    ('head cup', L('H_head_cup_x1.stl'), None), ('head lid', L('K_head_lid_x1.stl'), None),
    ('rotor', L('R_rotor_x1.stl'), None)]
# row A: housing, cup, lid left to right; row B: fin 2x2 + rotor; row C: spare fins 2x2
placed = []
def put(name, m, x, y):
    m = m.copy(); b = m.bounds; m.apply_translation([x - b[0][0], y - b[0][1], -b[0][2]]); placed.append((name, m)); return m
hw = put('housing', parts[0][1], MARGIN, MARGIN); x = hw.bounds[1][0] + GAP
cup = put('head cup', parts[1][1], x, MARGIN); x = cup.bounds[1][0] + GAP
lid = put('head lid', parts[2][1], x, MARGIN)
rowB = max(m.bounds[1][1] for _, m in placed) + GAP
fw, fh = fin.extents[0], fin.extents[1]
def fins(tag, y0):
    for i in range(4):
        put(f'{tag} {i+1}', fin, MARGIN + (i % 2) * (fw + GAP), y0 + (i // 2) * (fh + GAP))
fins('fin', rowB)
rotor = put('rotor', parts[3][1], MARGIN + 2 * fw + 2 * GAP, rowB)
y0C = rowB + 2 * fh + 2 * GAP
fins('spare fin', y0C)
# checks
hulls = {n: MultiPoint(m.vertices[:, :2]).convex_hull for n, m in placed}
names = list(hulls); worst = 1e9
for i in range(len(names)):
    for j in range(i + 1, len(names)):
        worst = min(worst, hulls[names[i]].distance(hulls[names[j]]))
allb = np.array([m.bounds for _, m in placed])
print('parts', len(placed), '| min gap between footprints %.1f mm' % worst, '| plate extents x %.0f..%.0f y %.0f..%.0f (bed 0..%d)' % (allb[:, 0, 0].min(), allb[:, 1, 0].max(), allb[:, 0, 1].min(), allb[:, 1, 1].max(), BED),
      '| tallest %.1f mm (bed 256)' % allb[:, 1, 2].max())
assert worst >= GAP - 0.01 and allb[:, 0, :2].min() >= MARGIN - 0.01 and allb[:, 1, :2].max() <= BED - MARGIN
vol = sum(m.volume for _, m in placed) / 1000
print('total solid volume %.0f cm3 = %.0f g if 100%% PLA (real prints use less)' % (vol, vol * 1.24))
sc = trimesh.Scene()
for n, m in placed: sc.add_geometry(m, node_name=n.replace(' ', '_'), geom_name=n.replace(' ', '_'))
sc.export('../exports/v5/P1S_one_plate_full_set.3mf')
trimesh.util.concatenate([m for _, m in placed]).export('../exports/v5/P1S_one_plate_full_set.stl')
fig, ax = plt.subplots(figsize=(7.5, 7.5)); ax.add_patch(plt.Rectangle((0, 0), BED, BED, fc='#f4f4f4', ec='k'))
for n, m in placed:
    h = hulls[n]; xs, ys = h.exterior.xy; ax.fill(xs, ys, alpha=.75, fc='#e8762b' if 'fin' in n else ('#2e8b57' if n == 'rotor' else '#4f8fd8'), ec='k', lw=.6)
    c = h.centroid; ax.text(c.x, c.y, n.replace('spare fin', 'spare\nfin'), ha='center', va='center', fontsize=6.5)
ax.set_xlim(-4, BED + 4); ax.set_ylim(-4, BED + 4); ax.set_aspect('equal'); ax.set_title('Bambu Lab P1S plate (256 x 256 mm): V5 set + 4 spare fins, all on one plate', fontsize=9)
fig.savefig('../exports/v5/P1S_plate_layout.png', dpi=140, bbox_inches='tight')
