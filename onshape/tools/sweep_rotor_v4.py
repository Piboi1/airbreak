"""Offline rotor sweep for V4 + limiter engagement test."""
import pickle, os, math, numpy as np, trimesh
from sweep_open import vol
W = os.environ['AIRBRAKE_WORK']
parts = pickle.load(open(f'{W}/fin_v4_parts.pkl', 'rb'))
g = lambda p: [m for _, (n, m) in parts.items() if n.startswith(p)][0]
mov = {'R': g('R '), 'EH': g('EH '), 'L1': g('L1 '), 'L2': g('L2 '), 'L3': g('L3 '), 'L4': g('L4 ')}
fix = {'C1': g('C1 '), 'C2': g('C2 '), 'servo': g('E SG90'), 'sled': g('N '), 'trans': g('T ')}
Rz = lambda d: trimesh.transformations.rotation_matrix(math.radians(d), [0, 0, 1])
worst = {}
for th in [-3, -1.5, -1, 0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 64, 65, 66, 66.5, 67, 68]:
    row = []
    for mn, m in mov.items():
        mm = m.copy(); mm.apply_transform(Rz(th))
        for fn, f in fix.items():
            if mn == 'EH' and fn == 'servo': continue
            v = vol(mm, f)
            if v > 0.05: row.append(f'{mn}-{fn} {v:.1f}'); worst[(th, mn, fn)] = v
    print(f'rotor {th:5} deg:', ', '.join(row) if row else 'clear')
