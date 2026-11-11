import pytetwild, trimesh, numpy as np, sys
def tw(stl,h,out,eps=0.05):
    m=trimesh.load(stl,process=False); diag=np.linalg.norm(m.extents)
    p,t=pytetwild.tetrahedralize(np.asarray(m.vertices,float),np.asarray(m.faces,np.int32),optimize=True,edge_length_fac=h/diag,epsilon=eps/diag)[:2]
    t=t[:,[0,2,1,3]].copy()
    v=np.einsum('ij,ij->i',np.cross(p[t[:,1]]-p[t[:,0]],p[t[:,2]]-p[t[:,0]]),p[t[:,3]]-p[t[:,0]])/6
    assert (v>0).all()
    np.savez(out,p=p,t=t); print(stl,len(p),len(t),'vol %.0f vs %.0f'%(v.sum(),m.volume),flush=True)
if __name__=='__main__': tw(sys.argv[1],float(sys.argv[2]),sys.argv[3])
