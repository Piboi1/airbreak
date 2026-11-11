"""Proposed lightening cuts for the non-rotor parts (assembly frame, rocket axis = Z through origin, mm)."""
import numpy as np, trimesh, manifold3d as m3, math
from shapely.geometry import Polygon, Point, box
from variants import to_man, to_tm, extrude
RHO=1.24e-3
def cylz(r,z0,z1,n=180): return extrude(Point(0,0).buffer(r,resolution=n//4),z0,z1)
def ring(r0,r1,z0,z1): return cylz(r1,z0,z1)-cylz(r0,z0-1,z1+1)
def sector(r0,r1,a0,a1,z0,z1,n=40):
    a=np.radians(np.linspace(a0,a1,n)); pts=[(r1*math.cos(t),r1*math.sin(t)) for t in a]+[(r0*math.cos(t),r0*math.sin(t)) for t in a[::-1]]
    return extrude(Polygon(pts),z0,z1)
def boxm(x0,x1,y0,y1,z0,z1): return extrude(box(x0,y0,x1,y1),z0,z1)
def flap(tm):
    """F1 upper-panel pockets (skin 2.5->1.5), F2 lower-zone pockets (4.7->2.0 skin). Flap on +X."""
    m=to_man(tm); cuts=[]
    for s in (1,-1):
        y0,y1=sorted((s*3.8,s*10.5))
        cuts.append(boxm(0,40,y0,y1,22.0,51.0)^cylz(30.7,21,52))       # F1: remove r<30.7 -> 1.5 mm skin
        y0,y1=sorted((s*2.0,s*10.5))
        cuts.append(boxm(0,40,y0,y1,11.5,19.0)^cylz(30.2,11,20))       # F2: remove r<30.2 -> 2.0 mm skin
    for c in cuts: m=m-c
    return to_tm(m)
def lower(tm,L3=False):
    """L1 annular core-out of shoulder between screw bosses, L2 cone wall 2.0->1.5 from inside, L3 (optional) bore 52->54.4"""
    m=to_man(tm)
    for k in range(4):
        a=45+90*k; m=m-sector(27.6,30.2,a+17,a+73,-39.9,-28.1)       # L1: 56 deg pockets, 34 deg solid boss at each screw
    # L2: cone inner surface offset 0.5 mm outward: inner radius from 30.2 at z=-38.5 to 26.56 at z=-73.63
    ri=lambda z:26.56+0.1155*(z+70.0)+0.5          # original inner radius + 0.5 mm
    zb,zt=-73.8,-39.7
    prof=[(0,zb),(ri(zb),zb),(ri(zt),zt),(0,zt)]
    cs=m3.CrossSection([np.array(prof)],m3.FillRule.EvenOdd); m=m-m3.Manifold.revolve(cs,180)
    if L3: m=m-cylz(27.2,-40,-10)
    return to_tm(m)
def cage(tm):
    """C1: four sector windows in the 2 mm base plate under the rotor wheel"""
    m=to_man(tm)
    for k in range(4): m=m-sector(6.5,15.0,90*k-30,90*k+30,-10,-7.7)
    return to_tm(m)
def upper(tm):
    """U1: two dia 14 floor holes clear of the servo-mount band; U2: wall inner relief 0.5 mm between screw bosses"""
    m=to_man(tm)
    for c in [(8,9),(-10,-12)]: m=m-extrude(Point(*c).buffer(7,resolution=24),69.5,72.5)
    scr=[45,135,-69,-111]; edges=sorted([(a%360) for a in scr]); 
    for i,a in enumerate(edges):
        b=edges[(i+1)%4]+(360 if i==3 else 0)
        if b-a>32: m=m-sector(29.0,30.39,a+16,b-16,73.2,90.5,n=60)
    return to_tm(m)
def cap(tm):
    m=to_man(tm); return to_tm(m-cylz(23.5,87.0,88.74))
if __name__=='__main__':
    P={}
    for n,fn in [('flap',flap),('lower',lower),('lowerL3',lambda t:lower(t,True)),('cage',cage),('upper',upper),('cap',cap)]:
        base=trimesh.load(f'part_{n[:5] if n.startswith("lower") else n}.stl'); t=fn(base); t.export(f'prop_{n}.stl')
        print(n,'base %.0f -> %.0f mm3  (%.1f%%)  %.2f g -> %.2f g  watertight %s bodies %d'%(base.volume,t.volume,100*(t.volume/base.volume-1),base.volume*RHO,t.volume*RHO,t.is_watertight,len(t.split())))
