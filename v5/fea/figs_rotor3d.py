import pyvista as pv, numpy as np, trimesh, pickle, json
import variants as V
from viz import grid
pv.OFF_SCREEN=True
base=V.to_man(V.BASE)
def removed(name): return V.to_tm(base-V.to_man(trimesh.load(f'var_{name}.stl')))
def added(name): return V.to_tm(V.to_man(trimesh.load(f'var_{name}.stl'))-base)
VIEWS={'top':((1,-1.1,1.0),(0,0,1)),'bottom':((1,-1.1,-1.0),(0,0,1))}
for name in ['ALL','REC']:
    new=trimesh.load(f'var_{name}.stl'); rem=removed(name); add=added(name)
    for vn,(pos,up) in VIEWS.items():
        p=pv.Plotter(off_screen=True,window_size=(1100,1000)); p.set_background('white')
        p.add_mesh(pv.wrap(new),color='#5fcf80',split_sharp_edges=True,smooth_shading=False)
        p.add_mesh(pv.wrap(rem),color='#e03131',opacity=0.38)
        if add.volume>1: p.add_mesh(pv.wrap(add),color='#1c7ed6')
        c=np.array([0,0,34.]); p.camera.focal_point=tuple(c); p.camera.position=tuple(c+200*np.array(pos)); p.camera.up=up; p.enable_parallel_projection(); p.reset_camera(); p.camera.zoom(1.25)
        p.screenshot(f'fig/rotor_{name}_{vn}.png'); p.close()
# stress plots
for name in ['BASE','ALL','REC']:
    try: f=pickle.load(open(f'fields_{name}.pkl','rb'))
    except Exception as e: print('skip',name); continue
    for lc,(vn,clim) in {'latch_radial_10N_x4':('top',(0,6)),'cam_40deg_20N_x4':('bottom',(0,10)),'tab_axial_10N_x4':('top',(0,6))}.items():
        g=grid(f'mesh_{name}.npz',f[lc]['vm']); pos,up=VIEWS[vn]
        p=pv.Plotter(off_screen=True,window_size=(1000,900)); p.set_background('white')
        p.add_mesh(g,scalars='s',cmap='turbo',clim=clim,scalar_bar_args=dict(title='von Mises [MPa]',vertical=True,position_x=0.87,position_y=0.25,height=0.5,width=0.05,label_font_size=16,title_font_size=16,fmt='%.0f',color='black'))
        c=np.array([0,0,34.]); p.camera.focal_point=tuple(c); p.camera.position=tuple(c+200*np.array(pos)); p.camera.up=up; p.enable_parallel_projection(); p.reset_camera(); p.camera.zoom(1.2)
        p.screenshot(f'fig/vm_{name}_{lc.split("_")[0]}_{lc.split("_")[1]}.png'); p.close()
print('ok')
