import sys, math, numpy as np, trimesh
sys.path.insert(0,'.')
from proto_lock import *
params = dict(tx0=22.0, tx1=26.5, ty=6.0, tz0=-8.0, tz1=-3.0, kx0=17.5, kx1=21.4, px1=20.0, pz0=3.4, kz1=6.4)
d = load('fin_v5'); C = pick(d, 'C '); R = pick(d, 'R '); Pf = [pick(d, f'P{i} ') for i in range(1, 5)]
p = params
C2 = S(C, moved(box(16.5, 19.5, 3.4, 11, 3.1, 14.5), Rz(125)))   # trim limiter stop 2 to R16.5 (finger reaches R16)
print('stop2 trim removed', round(C.volume - C2.volume, 1), 'mm3')
tail = box(p['tx0'], p['tx1'], -p['ty'], p['ty'], p['tz0'], p['tz1'])
fins = [U(P, moved(tail, Rz(90 * i))) for i, P in enumerate(Pf)]
for i in range(4):
    C2 = S(C2, moved(box(p['tx0'] - .4, 33, -(p['ty'] + .5), p['ty'] + .5, p['tz0'] - .3, -6.4), Rz(90 * i)))
for i in range(4):
    for sy in (-1, 1):
        for b in (box(p['kx0'], p['kx1'], min(sy*7.8, sy*11.2), max(sy*7.8, sy*11.2), 0, p['kz1']), box(p['kx0'], p['px1'], min(sy*4.6, sy*7.8), max(sy*4.6, sy*7.8), p['pz0'], p['kz1'])):
            C2 = U(C2, moved(b, Rz(90 * i)))
print('housing with 4 locks vol', round(C2.volume), 'vs', round(C.volume))
print('rotor sweep vs housing:', {th: round(vol(moved(R, Rz(th)), C2), 2) for th in (-3, -2, 0, 10, 30, 60, 66, 67)})
print('rotor vs housing, rotor angle 0..65 with fins open 90: skipped (open pose checked via V5-B after the CAD build)')
print('closed fins vs housing:', [round(vol(f, C2), 2) for f in fins])
# opening sweep, every fin
for i, f in enumerate(fins):
    worst = 0
    for th in range(0, 91, 3):
        T = trimesh.transformations.rotation_matrix(math.radians(th), [0, 1, 0], point=[25, 0, 0])
        ff = moved(f, Rz(-90 * i)); ff.apply_transform(T); ff.apply_transform(Rz(90 * i))
        worst = max(worst, vol(ff, C2))
    print(f'fin {i+1} opening sweep 0..90 step 3: worst overlap vs housing {worst:.2f} mm3')
# drop-in of rotor
w = 0
for rho in (0, 18, 40):
    for z in range(120, -1, -6): w = max(w, vol(moved(R, Rz(rho) @ Tz(z)), C2))
print('rotor drop-in vs housing, max overlap', round(w, 2))
# fin install radially, rotor at 18
r = moved(R, Rz(18)); worst_h = worst_r = 0
for x in range(40, -1, -2):
    ff = moved(fins[0], Tx(x)) if False else moved(fins[0], trimesh.transformations.translation_matrix([x, 0, 0]))
    worst_h = max(worst_h, vol(ff, C2)); worst_r = max(worst_r, vol(ff, r))
print('fin 1 installed radially: worst overlap housing', round(worst_h, 2), 'rotor', round(worst_r, 2))
import pickle
pickle.dump((C2, fins, params), open(__import__('os').environ['AIRBRAKE_WORK'] + '/proto_lock.pkl', 'wb'))
