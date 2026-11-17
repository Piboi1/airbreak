"""Offline rebuild of the V5 fin from its FeatureScript recipe (closed pose, azimuth 0) and stripped variants
that keep the V5 rotor interfaces (push pad, lock lug, tail, hinge root). No Onshape calls."""
import numpy as np, trimesh
from shapely.geometry import Polygon
U = lambda ms: trimesh.boolean.union(ms, engine='manifold')
D = lambda a, b: trimesh.boolean.difference([a, b], engine='manifold')
X = lambda a, b: trimesh.boolean.intersection([a, b], engine='manifold')
R_IN, R_OUT = 29.8, 32.2

def ext(poly_xy, z0, z1):
    m = trimesh.creation.extrude_polygon(Polygon(poly_xy), z1 - z0); m.apply_translation([0, 0, z0]); return m
def sector(ri, ro, half, z, h, a0=0.0, n=96):
    t = np.radians(np.linspace(a0 - half, a0 + half, n))
    return ext([(ro*np.cos(x), ro*np.sin(x)) for x in t] + [(ri*np.cos(x), ri*np.sin(x)) for x in t[::-1]], z, z + h)
def rbox(r0, r1, y0, y1, z, h):
    b = trimesh.creation.box([r1-r0, y1-y0, h]); b.apply_translation([(r0+r1)/2, (y0+y1)/2, z+h/2]); return b
def yc(r, y0, y1, x=25.0, z=0.0):
    c = trimesh.creation.cylinder(radius=r, height=y1-y0, sections=96)
    c.apply_transform(trimesh.transformations.rotation_matrix(np.pi/2, [1, 0, 0])); c.apply_translation([x, (y0+y1)/2, z]); return c
def xz_prism(pts, y0, y1):        # polygon in the (x, z) plane extruded along y
    m = trimesh.creation.extrude_polygon(Polygon(pts), y1 - y0)       # polygon in xy, extruded along +z
    m.apply_transform(np.array([[1, 0, 0, 0], [0, 0, 1, 0], [0, 1, 0, 0], [0, 0, 0, 1]]))  # (x, y, z) -> (x, z, y)
    m.apply_translation([0, y0, 0]); 
    if m.volume < 0: m.invert()
    return m
def tube(ro, ri, z0, z1):
    return D(trimesh.creation.cylinder(radius=ro, height=z1-z0, sections=256, transform=trimesh.transformations.translation_matrix([0, 0, (z0+z1)/2])),
             trimesh.creation.cylinder(radius=ri, height=z1-z0+2, sections=256, transform=trimesh.transformations.translation_matrix([0, 0, (z0+z1)/2])))

def panel_skin(taper=False, t_tip=1.2, uniform=None):
    skin = sector(R_IN, R_OUT, 32.5, 4, 50)
    if uniform:                                   # uniform thin skin above the root zone
        skin = D(skin, sector(10, R_OUT - uniform, 34, 11, 44))
    elif taper:                                   # inner face: R29.8 at z 11 -> R(32.2 - t_tip) at z 54
        z = np.linspace(11, 54.5, 40); r = R_IN + (R_OUT - t_tip - R_IN) * np.clip((z - 11) / 43, 0, 1)
        prof = [(0, 11)] + list(zip(r, z)) + [(0, 54.5)]
        cone = trimesh.creation.revolve(np.array(prof), sections=256)
        skin = D(skin, cone)
    return skin

def build(ribs=True, lips=False, taper=False, uniform=None, gusset='wide', rod=False, pdf_pockets=False):
    parts = [panel_skin(taper, uniform=uniform), yc(4.8, -7.4, 7.4), rbox(24, 31.5, -7.4, 7.4, 0, 10), sector(27.8, 31.3, 27, 4, 16),
             xz_prism([(25.5, 1.5), (31.5, 4), (31.5, 18), (25.5, 5)], -7, 7),
             rbox(22.0, 26.5, -6, 6, -7.6, 4.6)]
    if gusset == 'wide': parts.append(xz_prism([(25.5, 6), (31.5, 6), (31.5, 22.5), (25.5, 9.2)], -12, 12))
    elif gusset == 'windowed':
        g = xz_prism([(25.5, 6), (31.5, 6), (31.5, 22.5), (25.5, 9.2)], -12, 12)
        for y0, y1 in ((-10.4, -1.6), (1.6, 10.4)):            # two pockets through the gusset, 1.6 mm side walls and centre web kept
            g = D(g, xz_prism([(27.1, 10.4), (29.8, 10.4), (29.8, 17.0)], y0, y1))
        parts.append(g)
    f = U(parts)
    f = D(f, tube(45, 32.21, 2, 26))                             # rootClip
    if ribs:
        r = [rbox(26.8, 30.0, -0.9, 0.9, 4, 16.5), rbox(27.5, 30.0, -0.9, 0.9, 28.5, 18.5)]
        for s in (27.5, -27.5):
            for z, h in ((4, 16), (30, 24)): r.append(sector(27.8, 30.0, 3.0, z, h, a0=s))
        f = U([f] + r)
    if lips:
        for s in (1, -1): f = U([f, sector(28.3, R_IN + 0.3, 1.2, 11, 43, a0=s * 31.3)])
    if rod:   # channel boss for a 1.5 mm rod at y = 0 on the inner face, z 11..52; the rod itself is returned separately
        f = U([f, rbox(R_OUT - 3.6, R_OUT - 0.9, -1.6, 1.6, 11, 41)])
    if pdf_pockets:
        cyl = lambda r: trimesh.creation.cylinder(radius=r, height=80, sections=256)
        for y0, y1, z, h, rf in ((3.8, 10.5, 21.8, 29.0, 30.7), (-10.5, -3.8, 21.8, 29.0, 30.7), (2.0, 10.5, 11.3, 7.5, 30.2), (-10.5, -2.0, 11.3, 7.5, 30.2)):
            f = D(f, X(rbox(15, 33, y0, y1, z, h), cyl(rf)))
    f = U([f, sector(29, 31.5, 24, 4, 4)])                       # landing
    f = D(f, rbox(31.58, 35, -6, 6, 4, 4))                       # landing flat
    f = D(f, yc(1.7, -7.5, 7.5)); f = D(f, yc(5.5, -12.3, -7.7)); f = D(f, yc(5.5, 7.7, 12.3))
    lug = U([rbox(20.0, 22.8, -3, 3, 41.6, 8.4), rbox(20.0, 30.6, -3, 3, 47, 3)])
    f = U([f, lug, rbox(23, 31.3, -4, 4, 20, 9)])                # lock lug + push pad (follower)
    rodm = None
    if rod:
        f = D(f, yc(0.8, 0, 1, x=0)) if False else f
        ch = trimesh.creation.cylinder(radius=0.8, height=41, sections=32); ch.apply_translation([R_OUT - 2.25, 0, 11 + 20.5])
        f = D(f, ch)
        rodm = trimesh.creation.cylinder(radius=0.75, height=41, sections=32); rodm.apply_translation([R_OUT - 2.25, 0, 11 + 20.5])
    return f, rodm

VARIANTS = {
    'V5 (as printed)':           dict(),
    'V6 (PDF pockets F1+F2)':    dict(pdf_pockets=True),
    'E: no ribs + edge lips':    dict(ribs=False, lips=True),
    'EF: + skin taper 2.4->1.2': dict(ribs=False, lips=True, taper=True),
    'EFI: + gusset windows':     dict(ribs=False, lips=True, taper=True, gusset='windowed'),
    'J: 1.2 skin + 1.5 CF rod':  dict(ribs=False, lips=True, uniform=1.2, rod=True),
}
OPEN = trimesh.transformations.rotation_matrix(np.pi / 2, [0, 1, 0], point=[25, 0, 0])

if __name__ == '__main__':
    import pickle, sys
    W = '/tmp/claude-0/-home-user-airbreak/2a03b965-bd6f-5144-bd29-b03796006798/scratchpad/work'
    ref = [m for _, (n, m) in pickle.load(open(W + '/fin_v5.pkl', 'rb')).items() if n.startswith('P1')][0]
    f, _ = build()
    print('rebuilt V5 fin %.0f mm3 vs Onshape %.0f mm3; symmetric difference %.0f mm3' % (f.volume, ref.volume, D(f, ref).volume + D(ref, f).volume))
