"""Offline opening sweep: rotate fin 1 (+ its glued tube cut-out) about the hinge axis (R25, z0, along y) and test against the rest."""
import pickle, os, sys, math, numpy as np, trimesh
W = os.environ['AIRBRAKE_WORK']

def tube_ref(win_h, z0=-11, z1=100, ri=32.5, ro=33.02):
    n = 256
    ang = np.linspace(0, 2*np.pi, n, endpoint=False)
    outer = np.c_[ro*np.cos(ang), ro*np.sin(ang)]; inner = np.c_[ri*np.cos(ang), ri*np.sin(ang)]
    from trimesh.creation import extrude_polygon
    import shapely.geometry as sg
    poly = sg.Polygon(outer, [inner])
    t = extrude_polygon(poly, z1 - z0); t.apply_translation([0, 0, z0])
    for k in range(4):
        half = math.radians(33.5)
        pts = [(34*math.cos(a), 34*math.sin(a)) for a in np.linspace(-half, half, 40)] + [(32.0*math.cos(a), 32.0*math.sin(a)) for a in np.linspace(half, -half, 40)]
        w = extrude_polygon(sg.Polygon(pts), win_h); w.apply_translation([0, 0, -9.2])
        w.apply_transform(trimesh.transformations.rotation_matrix(math.radians(90*k), [0, 0, 1]))
        t = trimesh.boolean.difference([t, w], engine='manifold')
    return t

def vol(a, b):
    if (a.bounds[1] < b.bounds[0]).any() or (b.bounds[1] < a.bounds[0]).any(): return 0.0
    try:
        it = trimesh.boolean.intersection([a, b], engine='manifold'); return float(it.volume) if len(it.faces) else 0.0
    except Exception: return -1.0

def main(win_hs=(60.2, 63.8), angles=(2, 5, 10, 15, 25, 40, 55, 70, 90)):
    parts = pickle.load(open(f'{W}/fin_v2.pkl', 'rb'))          # closed pose
    g = lambda p: [m for _, (n, m) in parts.items() if n.startswith(p)][0]
    fin = trimesh.util.concatenate([g('P1 '), g('TP1')])
    fixed = {'C1': g('C1 '), 'C2': g('C2 ')}
    for h in win_hs:
        tube = tube_ref(h)
        print(f'--- tube window height {h} mm (top z {-9.2+h:.1f})')
        for th in angles:
            f = fin.copy()
            T = trimesh.transformations.rotation_matrix(math.radians(th), [0, 1, 0], point=[25, 0, 0])
            f.apply_transform(T)
            res = {k: round(vol(f, m), 1) for k, m in {**fixed, 'tube': tube}.items()}
            print(f'  open {th:2d} deg: ' + ', '.join(f'{k} {v}' for k, v in res.items()))

if __name__ == '__main__':
    main()
