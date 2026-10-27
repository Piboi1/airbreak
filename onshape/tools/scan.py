import sys, json, trimesh, numpy as np
import run, geom, osapi

def overlap_pairs(parts, names_a, names_b, min_vol=0.05):
    out = []
    A = [(n, m) for _, (n, m) in parts.items() if n.split(' ')[0] in names_a]
    B = [(n, m) for _, (n, m) in parts.items() if n.split(' ')[0] in names_b]
    for na, ma in A:
        for nb, mb in B:
            if na == nb: continue
            if (ma.bounds[1] < mb.bounds[0]).any() or (mb.bounds[1] < ma.bounds[0]).any(): continue
            try:
                it = trimesh.boolean.intersection([ma, mb], engine='manifold')
                v = it.volume if len(it.faces) else 0
            except Exception:
                v = -1
            if v > min_vol: out.append((na.split(' ')[0], nb.split(' ')[0], round(float(v), 2)))
    return out

def state(opening, release, button=0):
    run.build('ps_scan', 'fs1', 'modularBrake', 'scan', run.params(opening=opening, release=release, button=button, compact=True), ps_name='SCRATCH - angle scan (delete)')
    d = run.ids()
    return geom.fetch_parts(d['did'], d['wid'], d['ps_scan'], chord=0.05, ang=0.2)
