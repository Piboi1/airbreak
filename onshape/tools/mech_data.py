"""Measured motion data for the V3 mechanics document (offline, from the closed-state meshes)."""
import pickle, os, math, json, numpy as np, trimesh
from sweep_open import vol
W = os.environ['AIRBRAKE_WORK']
parts = pickle.load(open(f'{W}/fin_v3_parts.pkl', 'rb'))
g = lambda p: [m for _, (n, m) in parts.items() if n.startswith(p)][0]
P1, R, L1 = g('P1 '), g('R '), g('L1 ')
Rz = lambda d: trimesh.transformations.rotation_matrix(math.radians(d), [0, 0, 1])
hinge = lambda op: trimesh.transformations.rotation_matrix(math.radians(op), [0, 1, 0], point=[25, 0, 0])
def fin_at(op): f = P1.copy(); f.apply_transform(hinge(op)); return f
def rot_at(m, r): x = m.copy(); x.apply_transform(Rz(r)); return x

out = {'cam': [], 'latch_max_open': []}
# cam: smallest fin opening that clears the rotor at each rotor angle
for r in range(0, 70, 5):
    rr = rot_at(R, r)
    lo, hi = 0.0, 30.0
    if vol(fin_at(0.0), rr) < 0.05: lo = 0.0; hi = 0.0
    else:
        for _ in range(9):
            mid = (lo + hi) / 2
            if vol(fin_at(mid), rr) < 0.05: hi = mid
            else: lo = mid
    out['cam'].append((r, round(hi, 2)))
# latch: largest fin opening the catch cap lets through at each rotor angle
for r in range(0, 21, 1):
    ll = rot_at(L1, r)
    lo, hi = 0.0, 6.0
    if vol(fin_at(6.0), ll) < 0.05: lo = 6.0
    else:
        for _ in range(8):
            mid = (lo + hi) / 2
            if vol(fin_at(mid), ll) < 0.05: lo = mid
            else: hi = mid
    out['latch_max_open'].append((r, round(lo, 2)))
json.dump(out, open(f'{W}/mech_data.json', 'w'), indent=1)
print('cam (rotor deg, min fin opening deg):', out['cam'])
print('latch (rotor deg, max fin opening deg):', out['latch_max_open'])
