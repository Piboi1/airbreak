"""Split the V5 print set (+4 spare fins) over TWO Bambu Lab P1S plates with an almost even filament split (model volume, then support area as tie-break)."""
import itertools, numpy as np, trimesh
from shapely.geometry import MultiPoint
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
P = '../exports/v5/print/'; OUT = '../exports/v5/'
BED = 256.0; MARGIN = 6.0; GAP = 6.0
L = lambda f: trimesh.load(P + f)
# overhang (support) areas from export_print, mm2
items = {'housing': (L('C_module_housing_x1.stl'), 1571.0), 'rotor': (L('R_rotor_x1.stl'), 2157.3), 'head cup': (L('H_head_cup_x1.stl'), 2982.8), 'head lid': (L('K_head_lid_x1.stl'), 97.4)}
fin = L('P_fin_x4.stl'); FIN_SUP = 1756.1
names = list(items) + [f'fin {i}' for i in range(1, 5)] + [f'spare fin {i}' for i in range(1, 5)]
vol = {n: (items[n][0].volume if n in items else fin.volume) / 1000 for n in names}
sup = {n: (items[n][1] if n in items else FIN_SUP) / 1000 for n in names}
best = None
for mask in range(1 << len(names)):
    A = [n for i, n in enumerate(names) if mask >> i & 1]
    if not A or len(A) == len(names): continue
    dv = abs(sum(vol[n] for n in A) - sum(vol[n] for n in names if n not in A))
    ds = abs(sum(sup[n] for n in A) - sum(sup[n] for n in names if n not in A))
    # filament estimate = model volume + a rough support allowance (1.5 cm3 per 1000 mm2 of overhang; an assumption, not measured)
    dest = abs(sum(vol[n] + 1.5 * sup[n] for n in A) - sum(vol[n] + 1.5 * sup[n] for n in names if n not in A))
    key = (round(dest, 1), dv)
    if best is None or key < best[0]: best = (key, A)
A = best[1]; B = [n for n in names if n not in A]
def pack(group, title):
    placed = []; x = y = MARGIN; rowh = 0
    order = sorted(group, key=lambda n: -(items[n][0].extents[1] if n in items else fin.extents[1]))
    for n in order:
        m = (items[n][0] if n in items else fin).copy(); b = m.bounds; w, h = b[1][0] - b[0][0], b[1][1] - b[0][1]
        if x + w > BED - MARGIN: x = MARGIN; y += rowh + GAP; rowh = 0
        m.apply_translation([x - b[0][0], y - b[0][1], -b[0][2]]); placed.append((n, m)); x += w + GAP; rowh = max(rowh, h)
    hulls = {n: MultiPoint(m.vertices[:, :2]).convex_hull for n, m in placed}
    ks = list(hulls); gap = min([hulls[ks[i]].distance(hulls[ks[j]]) for i in range(len(ks)) for j in range(i + 1, len(ks))] or [99])
    ext = np.array([m.bounds for _, m in placed])
    assert gap >= GAP - .01 and ext[:, 1, :2].max() <= BED - MARGIN, (title, gap, ext[:, 1, :2].max())
    return placed, hulls, gap, ext
res = []
for tag, g in (('plate1', A), ('plate2', B)):
    placed, hulls, gap, ext = pack(g, tag)
    sc = trimesh.Scene()
    for n, m in placed: sc.add_geometry(m, node_name=n.replace(' ', '_'), geom_name=n.replace(' ', '_'))
    sc.export(f'{OUT}P1S_{tag}.3mf')
    v = sum(vol[n] for n in g); s = sum(sup[n] for n in g)
    res.append((tag, g, v, s, ext[:, 1, 1].max(), ext[:, 1, 0].max(), ext[:, 1, 2].max()))
    fig, ax = plt.subplots(figsize=(6.2, 6.2)); ax.add_patch(plt.Rectangle((0, 0), BED, BED, fc='#f4f4f4', ec='k'))
    for n, m in placed:
        h = hulls[n]; xs, ys = h.exterior.xy
        ax.fill(xs, ys, alpha=.75, fc='#e8762b' if 'fin' in n else ('#2e8b57' if n == 'rotor' else '#4f8fd8'), ec='k', lw=.6)
        c = h.centroid; ax.text(c.x, c.y, n.replace('spare fin', 'spare\nfin'), ha='center', va='center', fontsize=6.5)
    ax.set_xlim(-4, BED + 4); ax.set_ylim(-4, BED + 4); ax.set_aspect('equal')
    ax.set_title(f'P1S plate {tag[-1]}: {v*1.24:.0f} g solid PLA + supports (about {(v+1.5*s)*1.24:.0f} g est.)', fontsize=8.5)
    fig.savefig(f'{OUT}P1S_{tag}_layout.png', dpi=130, bbox_inches='tight'); plt.close(fig)
for tag, g, v, s, ymax, xmax, zmax in res:
    print(f'{tag}: {len(g)} objects | {v:.1f} cm3 = {v*1.24:.0f} g solid PLA | support-area proxy {s*1000:.0f} mm2 | footprint to x {xmax:.0f} y {ymax:.0f} | tallest {zmax:.0f} mm\n   ', ', '.join(g))
e = [r[2] + 1.5 * r[3] for r in res]
print('estimated filament incl. supports (assumption): %.0f g / %.0f g' % (e[0] * 1.24, e[1] * 1.24))
print('volume split %.1f%% / %.1f%%' % (100 * res[0][2] / (res[0][2] + res[1][2]), 100 * res[1][2] / (res[0][2] + res[1][2])))
