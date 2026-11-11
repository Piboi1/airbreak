import numpy as np, trimesh, manifold3d as m3, shapely, math
from shapely.geometry import Polygon, Point, box
from shapely.ops import unary_union
BASE=trimesh.load('inner_base.stl')
def to_man(tm): return m3.Manifold(m3.Mesh(np.asarray(tm.vertices,np.float32),np.asarray(tm.faces,np.uint32)))
def to_tm(man):
    me=man.to_mesh(); t=trimesh.Trimesh(np.asarray(me.vert_properties)[:,:3],np.asarray(me.tri_verts),process=False); return t
def wheel_poly():
    s=BASE.section(plane_origin=(0,0,35),plane_normal=(0,0,1)); p,T=s.to_2D()
    return shapely.affinity.affine_transform(p.polygons_full[0],[T[0,0],T[0,1],T[1,0],T[1,1],T[0,3],T[1,3]])
def extrude(poly,z0,z1):
    polys=[poly] if poly.geom_type=='Polygon' else list(poly.geoms)
    out=None
    for q in polys:
        rings=[np.array(q.exterior.coords)[:-1]]+[np.array(h.coords)[:-1] for h in q.interiors]
        cs=m3.CrossSection([r.astype(np.float64) for r in rings],m3.FillRule.EvenOdd)
        b=m3.Manifold.extrude(cs,z1-z0).translate((0,0,z0)); out=b if out is None else out+b
    return out
def rot(poly,deg): return shapely.affinity.rotate(poly,deg,origin=(0,0))
def pocket_polys(w_out=2.4,rf=1.0,mode='full',r_in=10.5,r_ring=21.0,rib=None):
    """mode 'full': as marked on the photo - lobe + outer spoke core, wall w_out left to every edge/window.
       mode 'lobe': only the lobe outside the r_ring base circle (spokes and 3 mm ring stay solid)."""
    W=wheel_poly(); ext=Polygon(W.exterior)
    if mode=='full': lob=W.buffer(-w_out).difference(Point(0,0).buffer(r_in,resolution=180))
    else: lob=ext.buffer(-w_out).difference(Point(0,0).buffer(r_ring,resolution=180))
    lob=lob.buffer(-rf).buffer(rf)
    polys=[g for g in (lob.geoms if lob.geom_type!='Polygon' else [lob]) if g.area>3]
    if rib:  # (width, r_mid): circumferential rib re-instating the base ring through each pocket
        ring=Point(0,0).buffer(rib[1]+rib[0]/2,resolution=180).difference(Point(0,0).buffer(rib[1]-rib[0]/2,resolution=180))
        out=[]
        for g in polys:
            d=g.difference(ring).buffer(-rf).buffer(rf)
            out+=[h for h in (d.geoms if d.geom_type!='Polygon' else [d]) if h.area>2]
        polys=out
    return polys
def build(A=None,B=None,C=False,D=None,G=None):
    """A: dict for pocket_polys; B: keep half-width of block (wings removed beyond); C: remove block below z=43.6;
       D: (dia, radius) vertical arm holes; G: (h, t) tab root gusset height, radial depth"""
    man=to_man(BASE)
    if A is not None:
        for g in pocket_polys(**A): man=man-extrude(g,32.0,38.3)
    for k in range(4):
        cuts=[]; adds=[]
        if B is not None:
            cuts.append(extrude(box(15.0,B,26.6,8),38.3,48.6)); cuts.append(extrude(box(15.0,-8,26.6,-B),38.3,48.6))
        if C: cuts.append(extrude(box(16.0,-8,26.6,8),38.3,43.6))
        if D is not None:
            cuts.append(extrude(Point(D[1],0).buffer(D[0]/2,resolution=24),43.0,49.0))
        if G is not None:
            h,t=G; prof=np.array([[23.6-t,48.6],[23.61,48.6],[23.61,48.6+h]])  # triangle in (r,z)
            cs=m3.CrossSection([prof],m3.FillRule.EvenOdd)
            g=m3.Manifold.extrude(cs,6.0).translate((0,0,-3.0)).rotate((90,0,0))  # extrude along y: map (x,y,z)->(x,-z,y)
            adds.append(g)
        for c in cuts: man=man-c.rotate((0,0,90*k))
        for a in adds: man=man+a.rotate((0,0,90*k))
    t=to_tm(man); assert t.is_watertight; return t
VARS={'BASE':{}, 'A_full':dict(A=dict(w_out=2.4)), 'A_lobe':dict(A=dict(w_out=2.4,mode='lobe')), 'A_rib':dict(A=dict(w_out=2.4,rib=(3.0,19.5))),
 'B':dict(B=4.0),'C':dict(C=True),'D':dict(D=(3.0,12.5)),'ALL':dict(A=dict(w_out=2.4),B=4.0,C=True,D=(3.0,12.5)),'G':dict(G=(2.0,2.0)),'REC':dict(A=dict(w_out=2.4),B=4.0,C=True,G=(2.0,2.0))}
if __name__=='__main__':
    import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
    W=wheel_poly(); fig,ax=plt.subplots(1,3,figsize=(24,8))
    for a,k in zip(ax,['A_full','A_lobe','A_rib']):
        x,y=W.exterior.xy; a.plot(x,y,'k')
        for h in W.interiors: x,y=h.xy; a.plot(x,y,'k')
        P=pocket_polys(**VARS[k]['A'])
        for g in P: x,y=g.exterior.xy; a.fill(x,y,'k',alpha=.6)
        a.set_title(f'{k} pocket areas {[round(g.area,1) for g in P[:3]]}'); a.set_aspect('equal'); a.grid()
    plt.savefig('pockets.png',dpi=55)
    for name,kw in VARS.items():
        t=build(**kw); print(name,'vol %.0f  d=%.0f mm3 (%.1f%%)  bodies %d'%(t.volume,t.volume-BASE.volume,100*(t.volume/BASE.volume-1),len(t.split())))
        t.export(f'var_{name}.stl')
