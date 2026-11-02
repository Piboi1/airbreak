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
    AZ = math.radians(126.5); ur = np.array([math.cos(AZ), math.sin(AZ)])
    fig, axs = plt.subplots(1, 2, figsize=(11.6, 6.0))
    # ---------- upper layer (z -13: below the Mercury top, inside the wire trough)
    ax = axs[0]
    plan(ax, -13.0, 'A  z = -13: upper layer, Mercury V1 + regulator + wire trough')
    ax.add_patch(Rectangle((-17.5, -0.35), 35.0, 2.65, fc='#cfe8d5', ec='#2c8f5a', lw=1.0, ls='--', alpha=.8))
    tag(ax, 18.3, 0.9, 'wire trough\n(z -13.4..-9.8)', fs=5.4, col='#1d7a4a')
    tag(ax, 0, -9.5, 'Mercury V1\n30 x 16.9', fs=6, ha='center', col='#4a2a7a'); tag(ax, 0, 11, 'Regulator D24V10F5 + C1\nin a 25 x 15 pocket', fs=5.6, ha='center', col='#8a2848')
    names = ['GND', 'GP6', 'GP7', 'OUT', 'IN', '3V']
    for k, nm in enumerate(names):
        x = -3.5 + 2.54 * k
        ax.add_patch(Circle((x, -2.1), 0.55, fc='#f2c14e' if k < 2 else 'white', ec='k', lw=.6, zorder=5))
        tag(ax, x, -3.7, nm, fs=4.6, ha='center', col='#0b3d91' if k in (1, 2) else 'k', rotation=90, va='top')
    tag(ax, 11.8, -2.2, '<- header pads (position estimated from the photo)', fs=4.9, col='#0b3d91')
    # servo cable path
    W = [(ur[0] * 33, ur[1] * 33), (ur[0] * 27.5, ur[1] * 27.5), (-19.4, 17.5), (-20.0, 8.0), (-20.0, 2.8), (-17.6, 1.4), (-8.0, 1.4), (-4.0, 1.0)]
    W = np.array(W); ax.plot(W[:, 0], W[:, 1], color=ORG, lw=2.2); ax.annotate('', xy=W[-1], xytext=W[-2], arrowprops=dict(arrowstyle='-|>', color=ORG, lw=2.0))
    arrow(ax, [(-3.8, 1.0), (-3.5, -1.8)], BLK, lw=1.2); arrow(ax, [(-3.2, 1.2), (-1.0, -1.8)], BLU, lw=1.2)
    tag(ax, ur[0] * 33 - 2, ur[1] * 33 + 3.0, 'P1: groove + hole\n(az 126.5 deg)', col=ORG, fs=5.6, ha='center')
    ax.add_patch(Rectangle((-1.5, 2.2), 6, 0.0001, fc='none'))
    arrow(ax, [(-8, 3.0), (-10, 1.6), (-13, 1.3)], RED, lw=1.2, head=False)
    tag(ax, -34.5, -30.5, 'orange: servo cable (red, brown, orange), cut to length;\nblack GND and blue GP6 go to the Mercury pads, the red +5 V wire\ngoes along the trough to the regulator VOUT and C1', fs=5.2, col='k')
    # ---------- battery layer
    ax = axs[1]
    plan(ax, -33.0, 'B  z = -33: battery layer, lead notch, strap channels, ring below')
    for sx in (1, -1):
        x0, x1 = sorted((sx * 16.5, sx * 22.8)); ax.add_patch(Rectangle((x0, -14.5), x1 - x0, 29, fc='none', ec='#b08a4a', ls=':', lw=1.0))
        x0, x1 = sorted((sx * 17.0, sx * 21.4)); ax.add_patch(Rectangle((x0, -12.6), x1 - x0, 25.2, fc='none', ec='#2f9e8a', ls='--', lw=0.9))
    ax.add_patch(Circle((0, -26), 4, fill=False, ec='#b08a4a', lw=1.2)); tag(ax, 5, -28.8, 'ring wire hole R4\n(0, -26)', fs=5.6, col='#7a5a20')
    tag(ax, -2, 0, 'Spektrum 300 mAh 2S\n42 x 19 x 12', fs=6, ha='center', col='#6a5500')
    ax.add_patch(Rectangle((21.0, -3.0), 3.0, 6.0, fc='none', ec=RED, lw=1.2, ls='--')); tag(ax, 24.5, 5.5, 'lead notch 6 x 6\n(z -37.5..-31.4)', col=RED, fs=5.6)
    arrow(ax, [(21.2, 0), (23.0, -3), (14, -12.5), (4, -22), (0, -26)], BLK, lw=2.0)
    arrow(ax, [(21.2, 1.5), (23.6, -2), (15, -13.5), (5, -23), (1, -26)], RED, lw=2.0)
    tag(ax, -34, -33.5, 'leads fold under the pack and leave through the ring hole to the arming jumper J1; both come back up the open side\nof the sled (-y) to z -14, round the sled corner and into the trough at its -x end', fs=5.0, col='k')
    tag(ax, -34, 32.5, 'strap channels (dashed teal) x = +-17.0..21.4', fs=5.4, col='#1d7a6a'); tag(ax, -34, 29.5, 'ring strap notches (dotted tan) 6.3 x 29', fs=5.4, col='#7a5a20')
    plt.tight_layout(); fig.savefig(F.OUT + 'v4_wiring_plan_views.png', dpi=210); plt.close(fig)

    # ---------- elevation through the 126.5 / -53.5 deg plane
    fig, ax = plt.subplots(1, 1, figsize=(7.2, 9.8))
    n = np.array([-math.sin(AZ), math.cos(AZ), 0]); u = np.array([math.cos(AZ), math.sin(AZ), 0]); v = np.array([0, 0, 1])
    for _, (name, m) in parts.items():
        if name.startswith(('HW', 'REF', 'TP', 'P1', 'P2', 'P3', 'P4')):
            continue
        outline(ax, name, m, [0, 0, 0], n, u, v, fill=COL.get(name[:2]) if name[:2] in ('E2', 'E3', 'E4') else None, lw=.7)
    ax.plot([0, 0], [-12, 41], color=RED, lw=2.0, ls='--'); ax.plot([-2.2, 2.2], [43.2, 46.6], color=RED, lw=2.4); ax.plot([-2.2, 2.2], [46.6, 43.2], color=RED, lw=2.4)
    tag(ax, -34, 52, 'X  the rotor bore is not a cable route:\nthe horn (z 41.5-43.3) closes its top', col=RED, fs=6.2)
    gx = 31.5
    ax.plot([gx, gx], [-19.3, 58.8], color=ORG, lw=3.0); ax.plot([gx, 25], [-19.3, -19.3], color=ORG, lw=3.0)
    ax.plot([gx, 24], [58.8, 62], color=ORG, lw=3.0); ax.plot([24, 10], [62, 62], color=ORG, lw=3.0)
    tag(ax, 36, 20, 'P1 groove\n3.2 wide x 1.6 deep,\nz -21.5 to 58.8,\nstrip at az 126.5 deg', col=ORG, fs=6.2, ha='right')
    tag(ax, 36, -22.5, 'hole 3.2 x 4.5\nz -21.5..-17.0', col=ORG, fs=5.8, ha='right')
    tag(ax, -20, 63.5, 'to the servo cable exit (check your servo)', col=ORG, fs=5.8); tag(ax, -12, 66, 'SG90 servo', fs=6, col='#444')
    ax.text(0, -50.5, 'lower tube: J1 arming jumper below the ring; ring wire hole at (0, -26)', fontsize=6, ha='center')
    ax.set_xlim(-37, 37); ax.set_ylim(-53, 72); ax.set_aspect('equal'); ax.grid(alpha=.2)
    ax.set_title('C  elevation through the 126.5 deg plane (model frame, mm)', fontsize=8); ax.tick_params(labelsize=6)
    plt.tight_layout(); fig.savefig(F.OUT + 'v4_wiring_plan_elev.png', dpi=200); plt.close(fig)


if __name__ == '__main__':
    make(); print('ok')
