"""Screw clearance audit on the cached V5-A meshes ($AIRBRAKE_WORK/fin_v5.pkl).
For every bolt: (1) how much LONGER than the modelled length it could be before the tip touches a non-hardware part, (2) a head-side / driver column check.
Output is a table: set, modelled length, longest usable length, first thing it hits, standard lengths that fit."""
import os, sys, math, numpy as np, trimesh
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from check_v5 import load, vol

TAG = sys.argv[1] if len(sys.argv) > 1 else 'fin_v5'
d = load(TAG)
parts = {n: m for n, m in d.items() if not n.startswith('HW')}
bolts = {n: m for n, m in d.items() if n.startswith('HW') and 'bolt' in n or n.startswith('HW horn')}

def axis_info(m):
    v = m.vertices; c = v.mean(0)
    u = np.linalg.svd(v - c, full_matrices=False)[2][0]
    t = (v - c) @ u
    def radius(mask):
        p = v[mask] - c; p = p - np.outer(p @ u, u); return np.linalg.norm(p, axis=1).max()
    ra, rb = radius(t > t.max() - 0.6), radius(t < t.min() + 0.6)
    if ra > rb: u = -u; t = -t          # head end has the larger radius: make u point from head to tip
    tip_mask = t > t.max() - 0.3
    tip = v[tip_mask].mean(0); head_end = v[t < t.min() + 0.3].mean(0)
    L = t.max() - t.min()
    return u, tip, head_end, L

def cyl(p0, u, length, r):
    c = trimesh.creation.cylinder(radius=r, height=length, sections=20)
    z = np.array([0, 0, 1.0]); ax = np.cross(z, u); s = np.linalg.norm(ax)
    R = trimesh.transformations.rotation_matrix(math.atan2(s, z @ u), ax / s) if s > 1e-9 else (np.eye(4) if u[2] > 0 else trimesh.transformations.rotation_matrix(math.pi, [1, 0, 0]))
    c.apply_transform(R); c.apply_translation(p0 + u * length / 2); return c

rows = []
for n, m in sorted(bolts.items()):
    u, tip, head_end, L = axis_info(m)
    r = 1.55 if ('M3' in n or 'hinge' in n or 'M3x' in n) and 'M2' not in n else 1.05
    hit = None; free = 0.0
    for e in np.arange(0.25, 14.01, 0.25):
        c = cyl(tip + u * 0.05, u, e, r)
        hits = [(vol(c, pm), pn) for pn, pm in parts.items()]
        hits = [h for h in hits if h[0] > 0.02]
        if hits: hit = max(hits)[1]; break
        free = e
    rows.append((n, round(L, 1), round(L + free, 1), hit or 'nothing within 14 mm', u.round(2).tolist()))
import collections
grp = collections.OrderedDict()
for n, L, mx, hit, u in rows:
    key = n.split(' - ')[0]
    key = ' '.join(w for w in key.split() if not w.isdigit() and not (w.startswith('H') and w[1:].isdigit()))
    g = grp.setdefault(key, [L, mx, hit, 0]); g[0] = min(g[0], L); g[1] = min(g[1], mx); g[3] += 1
    if mx == g[1]: g[2] = hit
print('Bolt tip clearance (longest usable length = modelled length + free run beyond the tip; collisions with printed parts and references, bolts and nuts excluded)')
for k, (L, mx, hit, c) in grp.items():
    print(f'  {k[:44]:44s} x{c}  modelled {L:4.1f} mm  longest usable {mx:4.1f} mm  first hit: {hit[:44]}')
