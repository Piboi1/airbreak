import pyvista as pv, numpy as np, pickle
pv.OFF_SCREEN=True
def grid(meshfile,scal):
    d=np.load(meshfile); p,t=d['p'],d['t']
    cells=np.hstack([np.full((len(t),1),4),t]).ravel()
    g=pv.UnstructuredGrid(cells,np.full(len(t),pv.CellType.TETRA),p); g.cell_data['s']=scal; return g
def render(g,name,views,clim,title='',cmap='turbo',ws=(900,900),clip=None,log=False,bar='utilisation'):
    for vn,(pos,up) in views.items():
        p=pv.Plotter(off_screen=True,window_size=ws)
        gg=g.clip(normal=clip[0],origin=clip[1]) if clip else g
        p.add_mesh(gg,scalars='s',cmap=cmap,clim=clim,log_scale=log,show_edges=False,scalar_bar_args=dict(title=bar,vertical=True,position_x=0.86,position_y=0.25,height=0.5,width=0.06,label_font_size=14,title_font_size=14,fmt='%.2f'))
        c=np.array(g.center); p.camera.focal_point=tuple(c); p.camera.position=tuple(c+np.array(pos)); p.camera.up=up; p.enable_parallel_projection(); p.reset_camera(); p.camera.zoom(1.15)
        if title: p.add_text(title,font_size=11,color='black')
        p.set_background('white'); p.screenshot(f'{name}_{vn}.png'); p.close()
ISO={'iso':((1,-1.2,0.9),(0,0,1)),'iso2':((-1,1.2,-0.9),(0,0,1))}
if __name__=='__main__':
    import sys
    for nm in sys.argv[1:]:
        f=pickle.load(open(f'pfields_{nm}.pkl','rb')); g=grid(f'pmesh_{nm}.npz',f['_env'])
        v=dict(ISO)
        if nm=='flap': v={'in':((-1,-0.6,0.5),(0,0,1)),'out':((1,-0.6,0.5),(0,0,1))}
        render(g,f'env_{nm}',v,(0,0.1),f'{nm}: envelope utilisation (all load cases)')
