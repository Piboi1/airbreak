"""Offline latch / cam timing from the closed-state meshes (no API calls).
Latch: fin opened by `op` deg about the hinge (R25, z0, y axis) vs catch caps turned by `rot` deg about z.
Cam: rotor turned by rot deg vs closed fins."""
import pickle, os, math, sys, numpy as np, trimesh
from sweep_open import vol
W = os.environ['AIRBRAKE_WORK']
parts = pickle.load(open(f'{W}/{sys.argv[1] if len(sys.argv) > 1 else "fin_v3_parts"}.pkl', 'rb'))
g = lambda p: [m for _, (n, m) in parts.items() if n.startswith(p)][0]
Rz = lambda d: trimesh.transformations.rotation_matrix(math.radians(d), [0, 0, 1])
P1, L1, R = g('P1 '), g('L1 '), g('R ')
def fin_open(op):
    f = P1.copy(); f.apply_transform(trimesh.transformations.rotation_matrix(math.radians(op), [0, 1, 0], point=[25, 0, 0])); return f
print('hold at rotor 0 (fin opening -> latch overlap mm3):', {op: round(vol(fin_open(op), L1), 2) for op in (0.5, 1, 1.5, 2, 3)})
rows = {}
f3 = fin_open(3.0)
for rot in (10, 12, 14, 15, 16, 17, 18, 20):
    l = L1.copy(); l.apply_transform(Rz(rot)); rows[rot] = round(vol(f3, l), 2)
print('release, fin held at 3 deg (latch overlap mm3 by rotor deg):', rows)
cam = {}
for rot in (18, 20, 22, 23, 24, 25, 26, 28, 30, 35):
    r = R.copy(); r.apply_transform(Rz(rot)); cam[rot] = round(vol(r, P1), 2)
print('cam contact (rotor vs closed fin mm3 by rotor deg):', cam)
