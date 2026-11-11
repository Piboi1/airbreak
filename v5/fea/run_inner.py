import numpy as np, sys, json, time, pickle, math
import variants as V
from fea import Model
name=sys.argv[1]
t0=time.time(); d=np.load(f'mesh_{name}.npz'); p,t=d['p'],d['t']
vol=abs(np.einsum('ij,ij->i',np.cross(p[t[:,1]]-p[t[:,0]],p[t[:,2]]-p[t[:,0]]),p[t[:,3]]-p[t[:,0]])/6).sum()
print(name,'mesh',len(p),len(t),'vol',round(vol),time.time()-t0,flush=True)
M=Model(p,t); print('ndof',M.K.shape[0],time.time()-t0,flush=True)
R=lambda x,y:np.hypot(x,y)
M.set_fixed([(lambda x,y,z:(z>51.3)&(R(x,y)<9.1),(0,1,2))],radial=[(lambda x,y,z:(z<12)&(R(x,y)>4.9),2.0e4)])
# ---- cam contact points from the BASE outline (same for every variant)
W=V.wheel_poly(); E=np.array(W.exterior.coords)
import shapely
E=np.array([W.exterior.interpolate(d).coords[0] for d in np.arange(0,W.exterior.length,0.05)])
def support(psi):  # rotor turned +psi (CCW): flat pad face of the +x flap touches the outline point with max projection on d
    d=np.array([math.cos(-psi),math.sin(-psi)]); i=np.argmax(E@d); return E[i],d,(E@d)[i]
lift=[support(math.radians(a))[2] for a in range(0,91)]
PSI=[20,40,58]
def rotz(v,k): c,s=round(math.cos(k*math.pi/2)),round(math.sin(k*math.pi/2)); return np.array([c*v[0]-s*v[1],s*v[0]+c*v[1]])
LC={}; patches={}
def tab_face(k):
    def fn(x,y,z):
        c,s=round(math.cos(k*math.pi/2)),round(math.sin(k*math.pi/2)); xr=c*x+s*y; yr=-s*x+c*y
        return (z>51.8)&(abs(xr-23.6)<0.03)&(abs(yr)<3.01)
    return M.facets_where(fn)
def tab_side(k):
    def fn(x,y,z):
        c,s=round(math.cos(k*math.pi/2)),round(math.sin(k*math.pi/2)); xr=c*x+s*y; yr=-s*x+c*y
        return (z>49.9)&(xr>23.5)&(abs(yr+3.0)<0.03)
    return M.facets_where(fn)
def tab_top(k):
    def fn(x,y,z):
        c,s=round(math.cos(k*math.pi/2)),round(math.sin(k*math.pi/2)); xr=c*x+s*y; yr=-s*x+c*y
        return (z>54.5)&(xr>23.5)&(abs(yr)<3.01)
    return M.facets_where(fn)
def er(k): return np.array([*rotz([1,0],k),0.])
def et(k): return np.array([*rotz([0,1],k),0.])
LC['latch_radial_10N_x4']=[(tab_face(k),10*er(k)) for k in range(4)]
LC['tab_tangential_10N_x1']=[(tab_side(0),10*et(0))]
LC['tab_axial_10N_x4']=[(tab_top(k),[0,0,-10.]) for k in range(4)]
for a in PSI:
    pt,d,h=support(math.radians(a)); tdir=np.array([-d[1],d[0]])
    L=[]
    for k in range(4):
        pk=rotz(pt,k); dk=rotz(d,k); tk=rotz(tdir,k)
        fac=M.facets_where(lambda x,y,z:(np.hypot(x-pk[0],y-pk[1])<1.6)&(z>32.4)&(z<38.1)&(R(x,y)>R(*pk)-1.0))
        F=20*(-dk)+0.3*20*(-tk)
        if k==0: F0=F.copy()
        L.append((fac,[F[0],F[1],0.]))
    LC[f'cam_{a}deg_20N_x4']=L; patches[a]=dict(pt=pt.tolist(),normal=(-d).tolist(),torque_Nmm=float(4*(pt[0]*F0[1]-pt[1]*F0[0])))
res=dict(name=name,vol=float(vol),ndof=int(M.K.shape[0]),lift=lift,patches=patches,lc={})
c=M.centroids(); vols=M.volumes(); rc=R(c[0],c[1]); z=c[2]
REG={'tab':(rc>22.5)&(z>48.6),'tab_root_block':(rc>16.5)&(z>38.2)&(z<=48.6),'arm':(rc>9.3)&(rc<=16.5)&(z>43),'hub':(rc<=9.3)&(z>38.2)&(z<50.8),
     'wheel_rim':(z>32)&(z<=38.2)&(rc>18),'wheel_spoke':(z>32)&(z<=38.2)&(rc>8)&(rc<=18),'wheel_hub':(z>32)&(z<=38.2)&(rc<=8),'shaft':(z<=32)&(z>12.5)}
fields={}
for lc,loads in LC.items():
    f=M.load_vec(loads); u=M.solve(f); s=M.stress(u)
    # exclude elements within 1.0 mm of a load patch
    ex=np.zeros(len(vols),bool)
    for L in loads:
        pc=M.mesh.p[:,M.mesh.facets[:,L[0]]].mean(axis=1)
        from scipy.spatial import cKDTree
        dd,_=cKDTree(pc.T).query(c.T); ex|=dd<1.0
    out={'work':float(f@u)}
    for rn,m in REG.items():
        mm=m&~ex
        if mm.sum()==0: continue
        def pct(v,q=0.999):
            o=np.argsort(v[mm]); cw=np.cumsum(vols[mm][o]); return float(v[mm][o][np.searchsorted(cw,q*cw[-1])])
        i=np.argmax(np.where(mm,s['vm'],-1)); j=np.argmax(np.where(mm,s['szz'],-1e9))
        out[rn]=dict(vm_max=float(s['vm'][i]),vm_p999=pct(s['vm']),vm_at=c[:,i].round(2).tolist(),szz_max=float(s['szz'][j]),szz_p999=pct(s['szz']),szz_at=c[:,j].round(2).tolist(),p1_max=float(s['p1'][mm].max()),p1_p999=pct(s['p1']))
    res['lc'][lc]=out; fields[lc]=dict(vm=s['vm'].astype(np.float32),szz=s['szz'].astype(np.float32),p1=s['p1'].astype(np.float32),u=u[M.basis.nodal_dofs].astype(np.float32))
    print(lc,'work %.4f'%out['work'],{k:(round(v['vm_p999'],2),round(v['szz_max'],2)) for k,v in out.items() if k!='work'},flush=True)
json.dump(res,open(f'res_{name}.json','w')); pickle.dump(fields,open(f'fields_{name}.pkl','wb'))
print('done',time.time()-t0)
