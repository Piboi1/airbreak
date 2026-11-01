"""Wiring layout drawings for V4: sections of the model with the harness routes drawn on top."""
import pickle, math, os, numpy as np, trimesh
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle, FancyArrowPatch
import figures as F

W = os.environ['AIRBRAKE_WORK']
parts = pickle.load(open(f'{W}/fin_v4_parts.pkl', 'rb'))
COL = {'R ': '#3a9a5b', 'EH': '#c9a227', 'E ': '#8a8f98', 'N ': '#2f9e8a', 'T ': '#b08a4a', 'C1': '#3b6ea5', 'C2': '#3b6ea5',
       'L1': '#2c8f5a', 'L2': '#2c8f5a', 'L3': '#2c8f5a', 'L4': '#2c8f5a', 'E4': '#d8b020', 'E2': '#8a5bc4', 'E3': '#e07a9a'}
ORG, RED, BLK, BLU = '#e8730c', '#c62828', '#222222', '#1565c0'


def outline(ax, name, m, plane_o, plane_n, u, v, fill=None, lw=.8):
    col = COL.get(name[:2], '#aaaaaa')
    try:
        s = m.section(plane_origin=plane_o, plane_normal=plane_n)
    except Exception:
        s = None
    if s is None:
        return
    for e in s.entities:
        p = s.vertices[e.points]
        ax.plot(p @ u, p @ v, color=col, lw=lw)
    if fill:
        try:
            pl, T = s.to_planar()
            for poly in pl.polygons_full:
                xy = np.array(poly.exterior.coords)
                p3 = trimesh.transformations.transform_points(np.c_[xy, np.zeros(len(xy))], T)
                ax.fill(p3 @ u, p3 @ v, color=fill, alpha=.55, lw=0)
        except Exception:
            pass


def plan(ax, z, title, xlim=(-36, 36), ylim=(-36, 36)):
    for _, (name, m) in parts.items():
        if name.startswith(('HW', 'REF', 'TP', 'P1', 'P2', 'P3', 'P4')):
            continue
        k = name[:2]
        fill = COL.get(k) if k in ('E2', 'E3', 'E4') else None
        outline(ax, name, m, [0, 0, z], [0, 0, 1], np.array([1, 0, 0]), np.array([0, 1, 0]), fill=fill)
    ax.set_xlim(*xlim); ax.set_ylim(*ylim); ax.set_aspect('equal'); ax.grid(alpha=.2); ax.set_title(title, fontsize=8)
    ax.tick_params(labelsize=6)


def arrow(ax, pts, col, lw=1.6, ls='-', head=True):
    pts = np.array(pts)
    ax.plot(pts[:, 0], pts[:, 1], color=col, lw=lw, ls=ls, solid_capstyle='round')
    if head:
        ax.annotate('', xy=pts[-1], xytext=pts[-2], arrowprops=dict(arrowstyle='-|>', color=col, lw=lw))


def tag(ax, x, y, t, col='k', fs=6.2, **kw):
    ax.text(x, y, t, fontsize=fs, color=col, ha=kw.pop('ha', 'left'), va=kw.pop('va', 'center'), **kw)


def make():
    fig, axs = plt.subplots(1, 2, figsize=(11.6, 6.0))
    # ---------- upper layer (z -14)
    ax = axs[0]
    plan(ax, -14.0, 'A  z = -14: upper layer (Mercury V1 + regulator)')
    ax.add_patch(Circle((0, 0), 4, fill=False, ls='--', ec='k', lw=.8)); tag(ax, 5.2, 3.2, 'ceiling hole R4 (centre)', fs=5.6)
    tag(ax, 0, -9, 'Mercury V1\n30 x 16.9', fs=6, ha='center', col='#4a2a7a'); tag(ax, 0, 10, 'Regulator\nD24V10F5 (13 x 18)\nin a 25 x 15 pocket', fs=5.4, ha='center', col='#8a2848')
    # proposed cable hole at azimuth 225
    cx, cy = 30.0 * math.cos(math.radians(225)), 30.0 * math.sin(math.radians(225))
    ax.add_patch(Circle((cx, cy), 2.3, fc='none', ec=RED, lw=1.2)); tag(ax, -35, -34.2, 'P1: O4.5 radial hole (z -13) from the outer groove', col=RED, fs=5.6)
    arrow(ax, [(cx, cy), (-19, -15), (-15, -9.5)], ORG, lw=2.0)
    tag(ax, -35, -30.2, 'servo cable (3 wires) arrives from the outer groove, 225 deg strip', col=ORG, fs=5.6)
    # P2 trough
    ax.add_patch(Rectangle((-17.2, -12), 3.0, 4.0, fc='none', ec=RED, lw=1.2, ls='--')); tag(ax, -34.5, -2.5, 'P2: 4 wide trough through the\nsled wall, z -16..-12', col=RED, fs=5.6)
    arrow(ax, [(-12, 10), (-12, 3.0), (-9, 1.2), (-9.5, -4)], RED, lw=1.2)
    tag(ax, -34.5, 31.5, 'red wire: regulator +5 V to the servo cable (joined in the 3 mm centre wall channel)', col=RED, fs=5.4)
    ax.add_patch(Rectangle((-14.5, -2.6), 9, 2.0, fc='none', ec=BLU, lw=1.0, ls=':')); tag(ax, 3, -17.2, 'servo header: pad position to confirm', col=BLU, fs=5.4, ha='center')
    # ---------- battery layer (z -28) + under-sled marks
    ax = axs[1]
    plan(ax, -28.0, 'B  z = -28: battery layer; dotted = transition ring below (z -35.5)')
    # ring notches
    for sx in (1, -1):
        x0, x1 = sorted((sx * 16.5, sx * 22.8))
        ax.add_patch(Rectangle((x0, -14.5), x1 - x0, 29, fc='none', ec='#b08a4a', ls=':', lw=1.0))
        x0, x1 = sorted((sx * 17.0, sx * 21.4))
        ax.add_patch(Rectangle((x0, -12.6), x1 - x0, 25.2, fc='none', ec='#2f9e8a', ls='--', lw=0.9))
    ax.add_patch(Circle((0, -26), 4, fill=False, ec='#b08a4a', ls='-', lw=1.2)); tag(ax, 5, -28.8, 'ring wire hole R4\n(0, -26)', fs=5.6, col='#7a5a20')
    tag(ax, 0, 0, 'Spektrum 300 mAh 2S\n42 x 19 x 12', fs=6, ha='center', col='#6a5500')
    # battery leads: exit +x end, fold under the pack, out to the ring hole
    arrow(ax, [(21.2, 0), (23.0, -3), (14, -12.5), (4, -22), (0, -26)], BLK, lw=2.0)
    arrow(ax, [(21.2, 1.5), (23.6, -2), (15, -13.5), (5, -23), (1, -26)], RED, lw=2.0)
    tag(ax, 24.5, 5.5, 'P3: 6 x 6 lead notch\nin the +x pocket wall', col=RED, fs=5.6)
    ax.add_patch(Rectangle((21.4, -3.0), 2.0, 6.0, fc='none', ec=RED, lw=1.2, ls='--'))
    tag(ax, -34, -33.5, 'leads fold under the pack and leave through the ring hole to the arming jumper J1 in the lower tube', fs=5.4, col='k')
    tag(ax, -34, 32.5, 'strap channels (dashed teal) x = +-17.0..21.4', fs=5.4, col='#1d7a6a'); tag(ax, -34, 29.5, 'ring strap notches (dotted tan) 6.3 x 29', fs=5.4, col='#7a5a20')
    # riser
    ax.add_patch(Rectangle((-5.5, -13.2), 11, 1.3, fc='none', ec=RED, lw=1.0, ls='--'))
    tag(ax, 0, -15.6, 'P4: wire riser groove 4 wide on the -y outer face of the lower block\n(z -35 to -23), then up the trough to the upper layer', fs=5.0, col=RED, ha='center')
    plt.tight_layout(); fig.savefig(F.OUT + 'v4_wiring_plan_views.png', dpi=210); plt.close(fig)

    # ---------- elevation through the 225 / 45 deg plane
    fig, ax = plt.subplots(1, 1, figsize=(7.2, 9.6))
    az = 45
    n = np.array([-math.sin(math.radians(az)), math.cos(math.radians(az)), 0]); u = np.array([math.cos(math.radians(az)), math.sin(math.radians(az)), 0]); v = np.array([0, 0, 1])
    for _, (name, m) in parts.items():
        if name.startswith(('HW', 'REF', 'TP', 'P1', 'P2', 'P3', 'P4')):
            continue
        outline(ax, name, m, [0, 0, 0], n, u, v, fill=COL.get(name[:2]) if name[:2] in ('E2', 'E3', 'E4') else None, lw=.7)
    # blocked route through the rotor
    ax.plot([0, 0], [-9, 41], color=RED, lw=2.0, ls='--'); ax.plot([-2.2, 2.2], [43.2, 46.6], color=RED, lw=2.4); ax.plot([-2.2, 2.2], [46.6, 43.2], color=RED, lw=2.4)
    tag(ax, 5.5, 52.5, 'X  rotor bore route is blocked:\nthe horn (z 41.5-43.3) closes the\nbore top, 0.2-0.5 mm gaps only', col=RED, fs=6.2)
    # P1 groove on the 225 strip (negative u side)
    gx = -31.6
    ax.plot([gx, gx], [-13, 58.8], color=ORG, lw=3.0)
    ax.plot([gx, -25.5], [-13, -13], color=ORG, lw=3.0)
    ax.plot([gx, -22], [58.8, 62], color=ORG, lw=3.0, ls='-'); ax.plot([-22, -10], [62, 62], color=ORG, lw=3.0)
    tag(ax, -35, 20, 'P1: outer groove\n4.0 wide x 1.6 deep,\nz -13 to 58.8,\non the 225 deg strip\n(offset 10 mm from the\nstrip centre line, clear\nof the tube screws)', col=ORG, fs=6.2, ha='right')
    tag(ax, -34.5, -12.2, 'radial hole O4.5 at z -13\ninto the bay', col=ORG, fs=5.6, ha='right')
    tag(ax, -9, 63.7, 'servo cable exit (check your servo)', col=ORG, fs=5.8)
    tag(ax, 7, 66, 'SG90 servo', fs=6, col='#444')
    ax.text(0, -46.5, 'Lower tube / J1 arming jumper below the transition ring (via the ring wire hole)', fontsize=6, ha='center', color='k')
    ax.set_xlim(-37, 37); ax.set_ylim(-49, 72); ax.set_aspect('equal'); ax.grid(alpha=.2)
    ax.set_title('C  elevation through the 225 / 45 deg plane (model frame, mm)', fontsize=8); ax.tick_params(labelsize=6)
    plt.tight_layout(); fig.savefig(F.OUT + 'v4_wiring_plan_elev.png', dpi=200); plt.close(fig)


if __name__ == '__main__':
    make(); print('ok')
