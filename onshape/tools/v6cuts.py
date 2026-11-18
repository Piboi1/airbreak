import pickle, numpy as np, trimesh
from shapely.geometry import Polygon, Point
W='/tmp/claude-0/-home-user-airbreak/2a03b965-bd6f-5144-bd29-b03796006798/scratchpad/work'
B=lambda ms: trimesh.boolean.union(ms,engine='manifold') if len(ms)>1 else ms[0]
def box(x0,x1,y0,y1,z0,z1):
    b=trimesh.creation.box([x1-x0,y1-y0,z1-z0]); b.apply_translation([(x0+x1)/2,(y0+y1)/2,(z0+z1)/2]); return b
def cyl(r,z0,z1,x=0,y=0,sec=128):
    c=trimesh.creation.cylinder(radius=r,height=z1-z0,sections=sec); c.apply_translation([x,y,(z0+z1)/2]); return c
def sector(ri,ro,a0,a1,z0,z1,n=64):
    t=np.radians(np.linspace(a0,a1,n))
    pts=[(ro*np.cos(a),ro*np.sin(a)) for a in t]+[(ri*np.cos(a),ri*np.sin(a)) for a in t[::-1]]
    m=trimesh.creation.extrude_polygon(Polygon(pts),z1-z0); m.apply_translation([0,0,z0]); return m
def rotz(m,deg):
    m=m.copy(); m.apply_transform(trimesh.transformations.rotation_matrix(np.radians(deg),[0,0,1])); return m
# ---- tools in the CAD frame (fin at azimuth 0, x radial) ----
def fin_tool(dz=0.0):
    # F1: two pockets y +-3.8..10.5, z 21.8..50.8, everything inside R30.7 (1.5 mm skin to the outer face R32.2)
    # F2: two pockets y +-2.0..10.5, z 11.3..18.8, inside R30.2 (2.0 mm skin)
    t=[]
    for s in (1,-1):
        y0,y1=sorted((3.8*s,10.5*s)); t.append(trimesh.boolean.intersection([box(15,33,y0,y1,21.8+dz,50.8+dz),cyl(30.7,0,80)],engine='manifold'))
        y0,y1=sorted((2.0*s,10.5*s)); t.append(trimesh.boolean.intersection([box(15,33,y0,y1,11.3+dz,18.8+dz),cyl(30.2,0,80)],engine='manifold'))
    return B(t)
def cage_tool(z0,z1):
    return B([sector(6.5,15.0,a-30,a+30,z0,z1) for a in (0,90,180,270)])
def head_tool(ztop_u2=86.0):
    t=[cyl(7.0,68.0,70.8,8,9),cyl(7.0,68.0,70.8,-10,-12)]
    # U2: wall 0.5 mm off the inside (R29.9 -> R30.4) from z 71.7 to ztop, except +-16 deg about the 4 bolt axes
    bolts=[45,135,250,290]; edges=sorted([(b-16)%360 for b in bolts]+[(b+16)%360 for b in bolts])
    spans=[(45+16,135-16),(135+16,250-16),(250+16,290-16),(290+16,360+45-16)]
    for a0,a1 in spans:
        if a1>a0: t.append(sector(29.0,30.4,a0,a1,71.7,ztop_u2))
    return B(t)
def lid_tool(zbot):
    return cyl(23.5,zbot-0.5,zbot+0.8)
