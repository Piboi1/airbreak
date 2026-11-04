"""Section pictures of the V5 model from the cached meshes: plan slices at several heights and axial slices through bolt axes."""
import os, sys, math, numpy as np, trimesh
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MPoly
from check_v5 import load, pick
W = os.environ['AIRBRAKE_WORK']
OUT = os.path.join(W, 'fig'); os.makedirs(OUT, exist_ok=True)
COL = {'C ': '#4caf7a', 'R ': '#7fd1a0', 'P1': '#e8a23a', 'P2': '#e8a23a', 'P3': '#e8a23a', 'P4': '#e8a23a', 'H ': '#4f8fd8', 'K ': '#2f6fb8', 'T ': '#c8a46a',
       'REF': '#cfcfcf', 'E ': '#8a8f98', 'EH': '#d6b640', 'E2': '#9a6fd1', 'E3': '#e07a9a', 'E4': '#e3c34a', 'HW': '#333333'}


def colour(n):
    for k in ('REF', 'HW', 'EH', 'E2', 'E3', 'E4', 'E ', 'P1', 'P2', 'P3', 'P4', 'C ', 'R ', 'H ', 'K ', 'T '):
        if n.startswith(k): return COL[k]
    return '#999'


def slice_parts(d, origin, normal, M, ax, skip=()):
    for n, m in d.items():
        if any(n.startswith(s) for s in skip): continue
        try:
            sec = m.section(plane_origin=origin, plane_normal=normal)
        except Exception:
            sec = None
        if sec is None: continue
        p2, _ = sec.to_planar(to_2D=M)
        for poly in p2.polygons_full:
            xs, ys = poly.exterior.xy
            ax.add_patch(MPoly(np.c_[xs, ys], closed=True, fc=colour(n), ec='k', lw=.3, alpha=.9))
            for h in poly.interiors:
                hx, hy = h.xy
                ax.add_patch(MPoly(np.c_[hx, hy], closed=True, fc='white', ec='k', lw=.3))


def plan(d, z, ax, title, lim=38):
    slice_parts(d, [0, 0, z], [0, 0, 1], np.eye(4), ax)
    ax.set_xlim(-lim, lim); ax.set_ylim(-lim, lim); ax.set_aspect('equal'); ax.set_title(title, fontsize=7); ax.tick_params(labelsize=5)
    ax.grid(alpha=.15)


def axial(d, az, ax, title, xlim, zlim, skip=(), off=0.0):
    a = math.radians(az)
    M = np.array([[math.cos(a), math.sin(a), 0, 0], [0, 0, 1, 0], [-math.sin(a), math.cos(a), 0, 0], [0, 0, 0, 1]])
    slice_parts(d, [-off * math.sin(a), off * math.cos(a), 0], [-math.sin(a), math.cos(a), 0], M, ax, skip)
    ax.set_xlim(*xlim); ax.set_ylim(*zlim); ax.set_aspect('equal'); ax.set_title(title, fontsize=7); ax.tick_params(labelsize=5); ax.grid(alpha=.15)


if __name__ == '__main__':
    d = load('fin_v5')
    fig, axs = plt.subplots(2, 4, figsize=(16, 8.4))
    for ax, (z, t) in zip(axs.flat, [(-28, 'z -28: transition shoulder + set 3'), (-9.5, 'z -9.5: housing base ring'), (0, 'z 0: hinges (ears, bolts, nuts)'), (12, 'z 12: set 2 nut bosses'),
                                      (25, 'z 25: cam and fin followers'), (48, 'z 48: servo ledges, lugs, rotor finger'), (75, 'z 75: electronics layer'), (82, 'z 82: set 1 lid bosses')]):
        plan(d, z, ax, t)
    fig.tight_layout(); fig.savefig(os.path.join(OUT, 'v5_plans.png'), dpi=120); plt.close(fig)
    fig, axs = plt.subplots(1, 3, figsize=(16, 9))
    axial(d, 45, axs[0], 'axial section at 45 deg (bolt azimuth: sets 1 (no), 2, 3)', (0, 40), (-72, 102))
    axial(d, 0, axs[1], 'axial section at 0 deg (fin 1 window, hinge, latch)', (-40, 40), (-72, 102))
    axial(d, 135, axs[2], 'axial section at 135 deg (servo ledge posts, lid boss)', (-40, 40), (-72, 102))
    fig.tight_layout(); fig.savefig(os.path.join(OUT, 'v5_axial.png'), dpi=120); plt.close(fig)
    print('ok')
