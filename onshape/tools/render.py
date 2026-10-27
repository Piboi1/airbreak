"""Tiny numba z-buffer renderer for exploded assembly figures (orthographic, flat Lambert shading + outlines)."""
import math
import numpy as np
from numba import njit
from PIL import Image, ImageDraw, ImageFont


def view_rows(az_deg, el_deg):
    az, el = math.radians(az_deg), math.radians(el_deg)
    back = np.array([math.cos(el) * math.cos(az), math.cos(el) * math.sin(az), math.sin(el)])
    right = np.cross([0, 0, 1], back); right /= np.linalg.norm(right)
    up = np.cross(back, right)
    return np.stack([right, up, back])          # world -> view rows


@njit(cache=True)
def _raster(tris, cols, ids, W, H, zbuf, cbuf, ibuf):
    n = tris.shape[0]
    for t in range(n):
        x0, y0, z0 = tris[t, 0, 0], tris[t, 0, 1], tris[t, 0, 2]
        x1, y1, z1 = tris[t, 1, 0], tris[t, 1, 1], tris[t, 1, 2]
        x2, y2, z2 = tris[t, 2, 0], tris[t, 2, 1], tris[t, 2, 2]
        minx = int(max(0, math.floor(min(x0, min(x1, x2)))))
        maxx = int(min(W - 1, math.ceil(max(x0, max(x1, x2)))))
        miny = int(max(0, math.floor(min(y0, min(y1, y2)))))
        maxy = int(min(H - 1, math.ceil(max(y0, max(y1, y2)))))
        den = (y1 - y2) * (x0 - x2) + (x2 - x1) * (y0 - y2)
        if abs(den) < 1e-12:
            continue
        for py in range(miny, maxy + 1):
            for px in range(minx, maxx + 1):
                fx = px + 0.5
                fy = py + 0.5
                a = ((y1 - y2) * (fx - x2) + (x2 - x1) * (fy - y2)) / den
                b = ((y2 - y0) * (fx - x2) + (x0 - x2) * (fy - y2)) / den
                c = 1.0 - a - b
                if a < -1e-6 or b < -1e-6 or c < -1e-6:
                    continue
                z = a * z0 + b * z1 + c * z2
                if z > zbuf[py, px]:
                    zbuf[py, px] = z
                    cbuf[py, px, 0] = cols[t, 0]
                    cbuf[py, px, 1] = cols[t, 1]
                    cbuf[py, px, 2] = cols[t, 2]
                    ibuf[py, px] = ids[t]


def render(items, az=-50, el=22, size=(1400, 1700), scale=None, center=None, ssaa=2, bg=(255, 255, 255),
           light=(-0.45, 0.55, 0.75), outline=True):
    """items: list of dict(mesh, color(0-1 rgb), offset(3), alpha=1 unused, id)."""
    R = view_rows(az, el)
    allv = []
    T, C, I = [], [], []
    Ldir = np.array(light); Ldir = Ldir / np.linalg.norm(Ldir)
    for k, it in enumerate(items):
        m = it['mesh']
        v = (m.vertices + np.array(it.get('offset', (0, 0, 0)))) @ R.T
        f = m.faces
        tri = v[f]
        n = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
        ln = np.linalg.norm(n, axis=1, keepdims=True); ln[ln == 0] = 1
        n = n / ln
        facing = n[:, 2] > 0
        tri, n = tri[facing], n[facing]
        inten = 0.30 + 0.70 * np.clip(n @ (Ldir), 0, 1)
        col = np.array(it['color'])[None, :] * inten[:, None] * 255
        T.append(tri); C.append(col); I.append(np.full(len(tri), k + 1))
        allv.append(v)
    allv = np.concatenate(allv)
    if center is None:
        lo, hi = allv.min(0), allv.max(0)
        center = (lo + hi) / 2
    W, H = size[0] * ssaa, size[1] * ssaa
    if scale is None:
        ext = allv.max(0) - allv.min(0)
        scale = min(size[0] / (ext[0] * 1.06), size[1] / (ext[1] * 1.06))
    s = scale * ssaa
    tris = np.concatenate(T)
    tris = tris.copy()
    tris[:, :, 0] = W / 2 + s * (tris[:, :, 0] - center[0])
    tris[:, :, 1] = H / 2 - s * (tris[:, :, 1] - center[1])
    cols = np.concatenate(C).astype(np.float64)
    ids = np.concatenate(I).astype(np.int32)
    zbuf = np.full((H, W), -1e9)
    cbuf = np.zeros((H, W, 3))
    ibuf = np.zeros((H, W), dtype=np.int32)
    _raster(tris, cols, ids, W, H, zbuf, cbuf, ibuf)
    img = np.where((ibuf > 0)[:, :, None], cbuf, np.array(bg, dtype=float))
    if outline:
        edge = np.zeros((H, W), bool)
        for dy, dx in ((0, 1), (1, 0)):
            a = ibuf[:H - dy, :W - dx]; b = ibuf[dy:, dx:]
            za = zbuf[:H - dy, :W - dx]; zb = zbuf[dy:, dx:]
            e = (a != b) | ((a > 0) & (np.abs(za - zb) > 0.9))
            edge[:H - dy, :W - dx] |= e
            edge[dy:, dx:] |= e
        img[edge] = img[edge] * 0.25
    img = img.reshape(size[1], ssaa, size[0], ssaa, 3).mean((1, 3))
    meta = dict(R=R, center=center, scale=scale, size=size)
    return Image.fromarray(img.clip(0, 255).astype(np.uint8)), meta


def project(meta, p):
    """World point -> pixel (x, y) in the rendered image."""
    v = meta['R'] @ np.asarray(p, float)
    return (meta['size'][0] / 2 + meta['scale'] * (v[0] - meta['center'][0]),
            meta['size'][1] / 2 - meta['scale'] * (v[1] - meta['center'][1]))


def font(sz):
    for f in ('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', '/usr/share/fonts/dejavu/DejaVuSans.ttf'):
        try:
            return ImageFont.truetype(f, sz)
        except Exception:
            pass
    return ImageFont.load_default()
