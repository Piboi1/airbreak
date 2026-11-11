import pyvista as pv, numpy as np, trimesh, pickle, sys
from variants import to_man, to_tm
from viz import grid
pv.OFF_SCREEN=True
def shot(name,new,rem,pos,up,clip=None,zoom=1.2,ws=(1000,900),color='#b8c4d0'):
    p=pv.Plotter(off_screen=True,window_size=ws); p.set_background('white')
    a=pv.wrap(new); b=pv.wrap(rem) if rem is not None else None
    if clip: a=a.clip(normal=clip[0],origin=clip[1]); b=b.clip(normal=clip[0],origin=clip[1]) if b is not None else None
    p.add_mesh(a,color=color,split_sharp_edges=True)
    if b is not None and b.n_points: p.add_mesh(b,color='#e03131',opacity=0.55)
    c=np.array(new.bounds.mean(axis=0)); p.camera.focal_point=tuple(c); p.camera.position=tuple(c+300*np.array(pos)); p.camera.up=up; p.enable_parallel_projection(); p.reset_camera(); p.camera.zoom(zoom)
    p.screenshot(name); p.close()
V={'flap':[('in',(-1,-0.55,0.45),(0,0,1),None)],
   'lower':[('cut',(-1,-0.5,-0.55),(0,0,1),((1,0.0,0),(0,0,0))),('below',(0.35,-0.5,-1),(0,0,1),None)],
   'lowerL3':[('cut',(-1,-0.5,-0.55),(0,0,1),((1,0.0,0),(0,0,0)))],
   'cage':[('below',(0.4,-0.7,-1),(0,0,1),None)],
   'upper':[('top',(0.4,-0.9,1),(0,0,1),None)],
   'cap':[('below',(0.4,-0.7,-1),(0,0,1),None)]}
for n,views in V.items():
    b=n[:5] if n.startswith('lower') else n
    base=trimesh.load(f'part_{b}.stl'); new=trimesh.load(f'prop_{n}.stl'); rem=to_tm(to_man(base)-to_man(new))
    for vn,pos,up,clip in views: shot(f'fig/prop_{n}_{vn}.png',new,rem,pos,up,clip)
# utilisation maps of baseline parts
VU={'flap':[('in',(-1,-0.55,0.45))],'lower':[('iso',(1,-1.2,0.9))],'cage':[('iso',(1,-1.2,0.9)),('below',(0.4,-0.7,-1))],'upper':[('below',(0.4,-0.9,-1)),('top',(0.4,-0.9,1))],'cap':[('below',(0.4,-0.7,-1))]}
for n,views in VU.items():
    f=pickle.load(open(f'pfields_{n}.pkl','rb')); g=grid(f'pmesh_{n}.npz',f['_env'])
    for vn,pos in views:
        p=pv.Plotter(off_screen=True,window_size=(1000,900)); p.set_background('white')
        p.add_mesh(g,scalars='s',cmap='turbo',clim=(0,0.10),scalar_bar_args=dict(title='utilisation',vertical=True,position_x=0.87,position_y=0.25,height=0.5,width=0.05,label_font_size=16,title_font_size=16,fmt='%.2f',color='black'))
        c=np.array(g.center); p.camera.focal_point=tuple(c); p.camera.position=tuple(c+300*np.array(pos)); p.camera.up=(0,0,1); p.enable_parallel_projection(); p.reset_camera(); p.camera.zoom(1.2)
        p.screenshot(f'fig/util_{n}_{vn}.png'); p.close()
print('ok')
