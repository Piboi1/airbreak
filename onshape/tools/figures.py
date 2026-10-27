"""Assembly-document figures (exploded views) rendered from the exported tessellation."""
import math, pickle, re, sys
import numpy as np
import trimesh
from PIL import Image, ImageDraw
import run, render

S = str(run.S) + '/'
OUT = S + 'fig/'
import os
os.makedirs(OUT, exist_ok=True)

BLUE = (.18, .45, .65); BLUE2 = (.33, .60, .80); ORANGE = (.95, .46, .12); GREEN = (.28, .68, .42)
DGREEN = (.18, .55, .32); GOLD = (.80, .69, .25); RED = (.88, .26, .32); PURPLE = (.58, .35, .80)
GREY = (.38, .40, .45); TAN = (.86, .78, .55); STEEL = (.55, .57, .62); TEAL = (.23, .55, .70)

COL = {'C1': BLUE, 'C2': BLUE2, 'D': BLUE, 'M': TEAL, 'F': (.35, .68, .80), 'S': TEAL, 'N': GOLD, 'I': GOLD, 'G': GOLD, 'J': GOLD,
       'R': GREEN, 'U': (.40, .75, .50), 'Q': (.50, .80, .55), 'T': (.22, .60, .38), 'X': (.60, .85, .62), 'A': RED, 'B': RED,
       'V': PURPLE, 'W': PURPLE, 'E': GREY}


def load(tag):
    raw = pickle.load(open(S + tag + '.pkl', 'rb'))
    out = {}
    for pid, (name, m) in raw.items():
        out[name] = m
    return out


def tok(name):
    w = name.split(' ')
    if w[0] == 'HW':
        key = w[1]
        if key in ('seam', 'upper', 'dock', 'cradle', 'lid', 'top-tube'):
            # e.g. "HW seam screw 3 - ..." -> seam3
            nums = re.findall(r'screw (\d+)', name)
            return 'HW_' + key + (nums[0] if nums else '')
        return 'HW_' + key          # H1 / L1
    if w[0] == 'REF':
        return 'REF_upper' if 'upper' in name else 'REF_lower'
    return w[0]


def color_of(t):
    if t in COL: return COL[t]
    if t.startswith('P'): return ORANGE
    if t.startswith('L'): return DGREEN
    if t.startswith('TP'): return TAN
    if t.startswith('REF'): return TAN
    if t.startswith('HW'): return (.50, .52, .58)
    return (.7, .7, .7)


def rot_z(v, deg):
    a = math.radians(deg)
    return np.array([v[0] * math.cos(a) - v[1] * math.sin(a), v[0] * math.sin(a) + v[1] * math.cos(a), v[2]])


def build(parts, spec, only=None):
    """spec: function(token, name, mesh) -> None to hide, or (offset(3), color) ."""
    items = []
    for name, m in parts.items():
        t = tok(name)
        r = spec(t, name, m)
        if r is None: continue
        off, col = r
        items.append(dict(mesh=m, offset=np.array(off, float), color=col if col is not None else color_of(t), tok=t))
    return items


def label_image(img, meta, labels, size=22, color=(20, 20, 20)):
    """labels: list of (text, world point, (dx,dy) text offset in px)."""
    dr = ImageDraw.Draw(img)
    f = render.font(size)
    for text, p, (dx, dy) in labels:
        x, y = render.project(meta, p)
        tx, ty = x + dx, y + dy
        dr.line([(x, y), (tx, ty)], fill=(60, 60, 60), width=2)
        dr.ellipse([x - 4, y - 4, x + 4, y + 4], fill=(200, 30, 30))
        w = dr.textlength(text, font=f)
        bx = tx - w if dx < 0 else tx
        dr.rectangle([bx - 4, ty - size * 0.7, bx + w + 4, ty + size * 0.7], fill=(255, 255, 255), outline=(120, 120, 120))
        dr.text((bx, ty - size * 0.6), text, font=f, fill=color)
    return img


def centroid(m):
    return m.bounds.mean(0)


MODULE = {'D', 'N', 'I', 'M', 'F', 'U', 'Q', 'T', 'X', 'A', 'B', 'V', 'W'}
CRADLE = {'S', 'E', 'J', 'G'}


def az_of(name, tkn):
    """Azimuth (deg) of fin/cap/screw number k -> (k-1)*90 for tokens ending in a digit."""
    m = re.search(r'(\d)$', tkn)
    return (int(m.group(1)) - 1) * 90 if m else 0


def overview_v1(parts, v2=False):
    def spec(t, name, m):
        if t in ('REF_upper',): return ((0, 0, 215), None)
        if t.startswith('HW_upper'): return (rot_z((16, 0, 0), az_of(name, t)) + np.array([0, 0, 215]), None)
        if t.startswith('HW_top-tube'):
            return (np.array([0, 0, 0]), None)
        if t == 'R': return ((0, 0, 118), None)
        if t.startswith('L') and t[1:].isdigit(): return ((0, 0, 118 - 30), None)
        if t.startswith('HW_L'): return ((0, 0, 118 + 6), None)
        if t.startswith('P') and t[1:].isdigit(): return (rot_z((36, 0, 0), az_of(name, t)), None)
        if t.startswith('HW_H'): return (rot_z((36, 0, 0), az_of(name, t)) + rot_z((0, -26, 0), az_of(name, t)), None)
        if t.startswith('HW_seam'): return (np.array([-20, 20, 0]) * 1.0, None)
        if t in MODULE: return ((0, 0, -55), None)
        if t.startswith('HW_dock') or t.startswith('HW_lid'):
            return ((0, 0, -55), None)
        if t in CRADLE: return ((0, 0, -105), None)
        if t.startswith('HW_cradle'): return ((0, 0, -105), None)
        if t == 'REF_lower': return ((0, 0, -170), None)
        return ((0, 0, 0), None)
    return spec


if __name__ == '__main__':
    parts = load('fin_v1')
    items = build(parts, overview_v1(parts))
    img, meta = render.render(items, az=-55, el=20, size=(1500, 2300))
    img.save(OUT + 'v1_overview_exploded.png')
    print('ok', img.size)


NV = np.array([1, -1, 0]) / math.sqrt(2)      # seam normal (C1 = positive side, C2 = negative side)


def fig_rotor(parts, name):
    def spec(t, nm, m):
        if t == 'R': return ((0, 0, 0), None)
        if t.startswith('L') and t[1:].isdigit(): return ((0, 0, -26), None)
        if t.startswith('HW_L'): return ((0, 0, 14), None)
        return None
    items = build(parts, spec)
    img, meta = render.render(items, az=-40, el=28, size=(1500, 1200))
    img = label_image(img, meta, [
        ('R rotor arm (3 mm)', (24.3 * 1, 0, 60), (-120, -120)),
        ('M3x8 button-head screw', (24.3, 0, 63 + 14), (60, -80)),
        ('L cap boss (screw pilot)', (24.3, 0, 55 - 26), (60, 90)),
    ], size=26)
    img.save(OUT + name)


def fig_halves(parts, name):
    pos = {'C1', 'P1', 'P4', 'HW_H1', 'HW_H4'}
    def spec(t, nm, m):
        if t == 'R' or (t.startswith('L') and t[1:].isdigit()) or t.startswith('HW_L'):
            return ((0, 0, 0), None)
        if t in pos: return (NV * 34, None)
        if t in ('C2', 'P2', 'P3', 'HW_H2', 'HW_H3'): return (-NV * 34, None)
        if t.startswith('HW_seam'): return (-NV * 62, None)
        return None
    items = build(parts, spec)
    img, meta = render.render(items, az=45, el=18, size=(1800, 1500), scale=8.6, center=np.array([0, 20, 0]) if False else None)
    img.save(OUT + name)


def fig_module(parts, name, v2=False):
    off = {'X': 118, 'T': 92, 'F': 64, 'V': 38, 'M': 12, 'N': 12, 'I': 12, 'A': -40, 'B': 20, 'W': 64, 'U': -34, 'Q': -62,
           'D': -86, 'S': -126, 'E': -126, 'J': -126, 'G': -126}
    def spec(t, nm, m):
        if t in off: return ((0, 0, off[t]), None)
        if t.startswith('HW_lid'): return ((0, 0, 64 + 14), None)
        if t.startswith('HW_dock'): return (rot_z((20, 0, 0), np.degrees(np.arctan2(*(m.bounds.mean(0)[:2][::-1])))) + np.array([0, 0, -86]), None)
        if t.startswith('HW_cradle'): return (rot_z((20, 0, 0), np.degrees(np.arctan2(*(m.bounds.mean(0)[:2][::-1])))) + np.array([0, 0, -126]), None)
        return None
    items = build(parts, spec)
    img, meta = render.render(items, az=-50, el=22, size=(1500, 2000))
    img.save(OUT + name)


def fig_hinge(parts, name):
    def spec(t, nm, m):
        if t == 'C1': return ((0, 0, 0), None)
        if t == 'P1': return ((34, 0, 0), None)
        if t == 'HW_H1': return ((0, -22, 0), None)
        return None
    items = build(parts, spec)
    img, meta = render.render(items, az=-35, el=30, size=(1500, 1300), scale=11, center=np.array([22, -4, 8]))
    img.save(OUT + name)


def mesh_az(m):
    c = m.bounds.mean(0)
    return math.degrees(math.atan2(c[1], c[0]))


def overview_v2(parts):
    def spec(t, name, m):
        if t == 'REF_upper': return ((0, 0, 232), None)
        if t.startswith('HW_top-tube'): return (rot_z((16, 0, 0), mesh_az(m)) + np.array([0, 0, 232]), None)
        if t.startswith('TP'): return (rot_z((58, 0, 0), az_of(name, t)), None)
        if t == 'R': return ((0, 0, 118), None)
        if t.startswith('L') and t[1:].isdigit(): return ((0, 0, 118 - 30), None)
        if t.startswith('HW_L'): return ((0, 0, 118 + 6), None)
        if t.startswith('P') and t[1:].isdigit(): return (rot_z((30, 0, 0), az_of(name, t)), None)
        if t.startswith('HW_H'): return (rot_z((30, 0, 0), az_of(name, t)) + rot_z((0, -26, 0), az_of(name, t)), None)
        if t.startswith('HW_seam'): return (np.array([-20, 20, 0]) * 1.0, None)
        if t in MODULE: return ((0, 0, -55), None)
        if t.startswith('HW_dock') or t.startswith('HW_lid'): return ((0, 0, -55), None)
        if t in CRADLE: return ((0, 0, -105), None)
        if t.startswith('HW_cradle'): return ((0, 0, -105), None)
        if t == 'REF_lower': return ((0, 0, -170), None)
        return ((0, 0, 0), None)
    return spec


def fig_tube_cutout(parts, name):
    """V2: the upper tube with its four slits and the cut-out pieces that get glued to the fins."""
    def spec(t, nm, m):
        if t == 'REF_upper': return ((0, 0, 0), None)
        if t.startswith('TP'): return (rot_z((46, 0, 0), az_of(nm, t)) + np.array([0, 0, 0]), None)
        if t.startswith('P') and t[1:].isdigit(): return (rot_z((84, 0, 0), az_of(nm, t)), None)
        return None
    items = build(parts, spec)
    img, meta = render.render(items, az=-40, el=26, size=(1500, 1500))
    img.save(OUT + name)


def side_silhouette(parts, v2, name_png):
    def spec(t, nm, m):
        if t.startswith('HW') : return ((0, 0, 0), None)
        return ((0, 0, 0), None)
    items = build(parts, spec)
    return items


def fig_compare(p1, p2, name):
    imgs = []
    for parts in (p1, p2):
        items = build(parts, lambda t, n, m: ((0, 0, 0), None))
        for it in items:
            if it['tok'].startswith('REF'):
                it['mesh'] = trimesh.intersections.slice_mesh_plane(it['mesh'].copy(), plane_normal=[-1, 0, 0], plane_origin=[0, 0, 0], cap=False)
        img, meta = render.render(items, az=90, el=0, size=(900, 1500), scale=5.5, center=np.array([0, 0, 5]))
        imgs.append((img, meta))
    gap = 60
    W = imgs[0][0].size[0] * 2 + gap
    H = imgs[0][0].size[1]
    out = Image.new('RGB', (W, H), (255, 255, 255))
    out.paste(imgs[0][0], (0, 0)); out.paste(imgs[1][0], (imgs[0][0].size[0] + gap, 0))
    dr = ImageDraw.Draw(out)
    f = render.font(44)
    sets = [(0, [(-15, 67, 'exposed: 82 mm', (200, 40, 40), 470), (-33, 85, 'printed: 118 mm', (40, 40, 200), 0)]),
            (imgs[0][0].size[0] + gap, [(-15, -11, 'exposed: 4 mm', (200, 40, 40), 470), (-33, 58.8, 'printed: 91.8 mm', (40, 40, 200), 0)])]
    for (img, meta), (x0, spans) in zip(imgs, sets):
        for z0, z1, txt, col, xo in spans:
            _, y0 = render.project(meta, (0, 0, z0)); _, y1 = render.project(meta, (0, 0, z1))
            x = x0 + 60 + xo
            dr.line([(x, y0), (x, y1)], fill=col, width=3)
            for y in (y0, y1): dr.line([(x - 12, y), (x + 12, y)], fill=col, width=3)
            ym = (y0 + y1) / 2
            w = dr.textlength(txt, font=f)
            dr.rectangle([x + 10, ym - 30, x + 18 + w, ym + 30], fill=(255, 255, 255))
            dr.text((x + 14, ym - 26), txt, font=f, fill=col)
    dr.text((20, 10), 'V1 (inline, OD 66.04 housing)', font=render.font(46), fill=(0, 0, 0))
    dr.text((imgs[0][0].size[0] + gap + 20, 10), 'V2 (compact head inside upper tube)', font=render.font(46), fill=(0, 0, 0))
    out.save(OUT + name)


def fig_dz(parts, name, drops=(0, 14, 22), az=-38, el=16):
    """Cut-away preview: trim the top of the V2 head by dz and re-align so the head tops line up."""
    cols = []
    top0 = 78.4
    for dz in drops:
        ztop = top0 - dz
        items = []
        for nm, m in parts.items():
            t = tok(nm)
            if t.startswith('REF') or t.startswith('TP'):
                continue
            mm = m
            if m.bounds[1][2] > ztop:
                try:
                    mm = trimesh.intersections.slice_mesh_plane(m.copy(), plane_normal=[0, 0, -1], plane_origin=[0, 0, ztop], cap=True)
                except Exception:
                    mm = m
            if len(mm.faces) == 0:
                continue
            items.append(dict(mesh=mm, offset=np.array([0, 0, dz], float), color=color_of(t), tok=t))
        img, meta = render.render(items, az=az, el=el, size=(900, 1350), scale=6.4, center=np.array([0, 0, -8]))
        cols.append((dz, img, meta))
    gap = 20
    W = sum(c[1].size[0] for c in cols) + gap * (len(cols) - 1)
    H = cols[0][1].size[1] + 150
    out = Image.new('RGB', (W, H), (255, 255, 255))
    dr = ImageDraw.Draw(out)
    x0 = 0
    for dz, img, meta in cols:
        out.paste(img, (x0, 150))
        title = 'V2 now' if dz == 0 else f'latch stack down {dz} mm'
        dr.text((x0 + 20, 10), title, font=render.font(44), fill=(0, 0, 0))
        dr.text((x0 + 20, 62), f'printed stack {171.9 - dz:.1f} mm  (V1: 178.5)', font=render.font(30), fill=(40, 40, 40))
        dr.text((x0 + 20, 100), f'fin top to head top: {28.4 - dz:.1f} mm', font=render.font(30), fill=(190, 40, 40))
        # horizontal guide at the fin top (z=50 -> shifted by dz) and at the head top
        for z, col in ((50 + dz, (190, 40, 40)), (top0, (40, 40, 200))):
            _, y = render.project(meta, (0, 0, z))
            y += 150
            dr.line([(x0 + 10, y), (x0 + img.size[0] - 10, y)], fill=col, width=2)
        x0 += img.size[0] + gap
    dr.text((20, H - 40), 'Cut-away preview of the real V2 model: red = fin top, blue = head top. Latch stack not yet re-engineered (see text).', font=render.font(26), fill=(60, 60, 60))
    out.save(OUT + name)


def fig_latch_plan(path, state_closed, state_released, z=43.5, zoom=(-4, 34, -22, 22)):
    """Plan section of the V2 latch at z (looks down): closed vs released."""
    import matplotlib; matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import sections
    fig, axs = plt.subplots(1, 2, figsize=(7.2, 3.6))
    for ax, (parts, title) in zip(axs, ((state_closed, 'rotor 0\u00b0 (locked): finger outside the lug wall'), (state_released, 'rotor 20\u00b0 (released): finger swung clear'))):
        # draw with the shared helper into a temp image then embed: simpler to draw sections directly
        import numpy as np
        from matplotlib.collections import LineCollection
        for i, (nm, m) in enumerate(parts.items()):
            t = tok(nm)
            if not (t in ('P1', 'L1', 'R') or t.startswith('HW_L1')):
                continue
            try:
                sec = m.section(plane_origin=[0, 0, z], plane_normal=[0, 0, 1])
            except Exception:
                sec = None
            if sec is None: continue
            segs = [sec.vertices[e.points][:, :2] for e in sec.entities]
            col = {'P1': '#e8762b', 'L1': '#2e8b57', 'R': '#5aa469'}.get(t, '#555555')
            ax.add_collection(LineCollection(segs, colors=col, linewidths=1.4))
            ax.text(*(np.concatenate(segs).mean(0)), t.replace('HW_', ''), fontsize=7, color=col)
        ax.set_xlim(zoom[0], zoom[1]); ax.set_ylim(zoom[2], zoom[3]); ax.set_aspect('equal'); ax.grid(alpha=.25)
        ax.set_title(title, fontsize=8); ax.tick_params(labelsize=6)
    fig.suptitle('Section at z = %.1f mm, looking down. Orange: fin lug wall; green: cap finger and rotor arm' % z, fontsize=8)
    fig.tight_layout(); fig.savefig(path, dpi=220); plt.close(fig)
