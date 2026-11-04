"""Prototype the under-hinge tail lock on the cached meshes (closed pose): tail on the fin, pocket + keeper pads in the housing; sweep the opening."""
import sys, math, numpy as np, trimesh
sys.path.insert(0, '.')
from check_v5 import load, pick, fin_open, vol, moved, Rz, Tz

def box(x0, x1, y0, y1, z0, z1):
    b = trimesh.creation.box(extents=[x1 - x0, y1 - y0, z1 - z0]); b.apply_translation([(x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2]); return b

def U(a, b): return trimesh.boolean.union([a, b], engine='manifold')
def S(a, b): return trimesh.boolean.difference([a, b], engine='manifold')

def build(params):
    d = load('fin_v5'); C = pick(d, 'C '); P = pick(d, 'P1 ')
    p = params
    tail = box(p['tx0'], p['tx1'], -p['ty'], p['ty'], p['tz0'], p['tz1'])
    fin = U(P, tail)
    C2 = S(C, box(p['tx0'] - .4, 33, -(p['ty'] + .5), p['ty'] + .5, p['tz0'] - .3, -6.4 if p.get('slot') is None else p['slot']))
    keep = []
    for sy in (-1, 1):
        keep.append(box(p['kx0'], p['kx1'], min(sy * 7.8, sy * 11.2), max(sy * 7.8, sy * 11.2), 0, p['kz1']))           # towers
        keep.append(box(p['kx0'], p['px1'], min(sy * 4.6, sy * 7.8), max(sy * 4.6, sy * 7.8), p['pz0'], p['kz1']))       # pads over the tail
    for k in keep: C2 = U(C2, k)
    return fin, C2

if __name__ == '__main__':
    params = dict(tx0=22.0, tx1=26.5, ty=6.0, tz0=-8.0, tz1=-3.0, kx0=17.5, kx1=21.4, px1=20.0, pz0=3.4, kz1=6.4)
    fin, C2 = build(params)
    print('fin vol', round(fin.volume), 'housing vol', round(C2.volume))
    res = {}
    for th in (0, 5, 10, 20, 30, 45, 60, 75, 85, 90, 92):
        res[th] = round(vol(fin_open(fin, th), C2), 2)
    print('fin (with tail) vs housing (pocket + keepers), overlap mm3 by opening angle:', res)
