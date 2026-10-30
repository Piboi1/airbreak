"""Offline rotor sweep for V3: turn rotor + horn + catch caps about z and test against the housing halves and the servo."""
import pickle, os, math, sys, numpy as np, trimesh
from sweep_open import vol
W = os.environ['AIRBRAKE_WORK']
parts = pickle.load(open(f'{W}/{sys.argv[1] if len(sys.argv) > 1 else "fin_v3_parts"}.pkl', 'rb'))
g = lambda p: [m for _, (n, m) in parts.items() if n.startswith(p)][0]
mov = {'R': g('R '), 'EH': g('EH '), 'L1': g('L1 '), 'L2': g('L2 '), 'L3': g('L3 '), 'L4': g('L4 ')}
fix = {'C1': g('C1 '), 'C2': g('C2 '), 'E': g('E SG90 servo')}
worst = {}
for th in list(range(0, 70, 5)) + [65]:
    row = []
    T = trimesh.transformations.rotation_matrix(math.radians(th), [0, 0, 1])
    for mn, m in mov.items():
        mm = m.copy(); mm.apply_transform(T)
        for fn, f in fix.items():
            if mn == 'EH' and fn == 'E': continue
            v = vol(mm, f)
            if v > 0.05: row.append(f'{mn}-{fn} {v:.1f}'); worst[(mn, fn)] = max(worst.get((mn, fn), 0), v)
    print(f'rotor {th:2d} deg:', ', '.join(row) if row else 'clear')
print('worst', {f'{a}-{b}': round(v, 1) for (a, b), v in worst.items()})
