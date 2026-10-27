import numpy as np, trimesh, pickle, sys
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection

PALETTE = ["#1f77b4","#ff7f0e","#2ca02c","#d62728","#9467bd","#8c564b","#e377c2","#7f7f7f","#bcbd22","#17becf"]

def section_plot(parts, origin, normal, up, path, xlim=None, ylim=None, title="", size=(9,9), label=True):
    """Slice every part with plane (origin, normal); draw in 2D using basis (u=up x normal, v=up)."""
    n = np.array(normal, float); n /= np.linalg.norm(n)
    v = np.array(up, float); v -= v.dot(n) * n; v /= np.linalg.norm(v)
    u = np.cross(v, n)
    fig, ax = plt.subplots(figsize=size)
    for i, (pid, (name, m)) in enumerate(parts.items()):
        try:
            sec = m.section(plane_origin=origin, plane_normal=n)
        except Exception:
            sec = None
        if sec is None: continue
        segs = []
        for ent in sec.entities:
            pts = sec.vertices[ent.points]
            p2 = np.stack([(pts - origin) @ u, (pts - origin) @ v], 1)
            segs.append(p2)
        lc = LineCollection(segs, colors=PALETTE[i % 10], linewidths=0.9)
        ax.add_collection(lc)
        if label and segs:
            c = np.concatenate(segs).mean(0)
            ax.text(c[0], c[1], name.split()[0], fontsize=6, color=PALETTE[i % 10])
    ax.set_aspect("equal"); ax.set_title(title)
    if xlim: ax.set_xlim(*xlim)
    if ylim: ax.set_ylim(*ylim)
    ax.autoscale_view() if not xlim else None
    ax.grid(True, lw=0.2)
    fig.savefig(path, dpi=110, bbox_inches="tight"); plt.close(fig)
