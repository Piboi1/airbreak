"""Generic part study: several boundary-condition sets, each with load cases; envelope utilisation."""
import numpy as np, pickle, json, time
from fea import Model
from scipy.spatial import cKDTree
S_IN, S_Z = 35.0, 15.0     # MPa allowables: in-layer (von Mises), across layers (tension)
def study(name, p, t, bcsets, iso=False, E=2300.):
    """bcsets: list of (fixed_selectors, {lc_name: fn(M)->loads}); returns dict with per-element envelopes"""
    t0=time.time(); M=Model(p,t,E=E); c=M.centroids(); vols=M.volumes()
    out=dict(name=name,vol=float(vols.sum()),ndof=int(M.K.shape[0]),lc={})
    env=np.zeros(len(vols)); envvm=np.zeros(len(vols)); fields={}; excl=np.zeros(len(vols),bool)
    for fixed,lcs in bcsets:
        M.set_fixed(fixed)
        # elements touching fixed dofs are excluded from peaks (constraint singularities)
        fx=np.zeros(M.K.shape[0],bool); fx[M.D]=True
        fixel=fx[M.basis.element_dofs].any(axis=0)
        for lc,fn in lcs.items():
            loads=fn(M); f=M.load_vec(loads); u=M.solve(f); s=M.stress(u)
            ex=fixel.copy()
            for L in loads:
                pc=M.mesh.p[:,M.mesh.facets[:,L[0]]].mean(axis=1); dd,_=cKDTree(pc.T).query(c.T); ex|=dd<1.0
            ten=s['p1'] if iso else s['szz']
            util=np.maximum(s['vm']/S_IN,np.clip(ten,0,None)/S_Z); utilm=np.where(ex,0,util)
            i=int(np.argmax(utilm)); o=np.argsort(utilm); cw=np.cumsum(vols[o])
            un=u[M.basis.nodal_dofs]; umax=float(np.linalg.norm(un,axis=0).max())
            out['lc'][lc]=dict(work=float(f@u),umax=umax,util_max=float(utilm[i]),util_at=c[:,i].round(2).tolist(),vm_max=float(np.where(ex,0,s['vm']).max()),
                               ten_max=float(np.where(ex,-1e9,ten).max()),util_p999=float(utilm[o][np.searchsorted(cw,0.999*cw[-1])]))
            env=np.maximum(env,utilm); envvm=np.maximum(envvm,s['vm']); excl|=ex
            fields[lc]=dict(vm=s['vm'].astype(np.float32),util=util.astype(np.float32),u=un.astype(np.float32))
            print(name,lc,{k:(round(v,3) if isinstance(v,float) else v) for k,v in out['lc'][lc].items()},flush=True)
    out['env_max']=float(env.max()); out['time']=time.time()-t0
    # fraction of volume below utilisation thresholds
    for th in (0.01,0.02,0.05,0.1): out[f'volfrac_util<{th}']=float(vols[env<th].sum()/vols.sum())
    fields['_env']=env.astype(np.float32); fields['_envvm']=envvm.astype(np.float32); fields['_vols']=vols.astype(np.float32)
    json.dump(out,open(f'pres_{name}.json','w')); pickle.dump(fields,open(f'pfields_{name}.pkl','wb'))
    print(name,'env max',out['env_max'],{k:round(v,3) for k,v in out.items() if k.startswith('volfrac')},'t',round(out['time']),flush=True)
    return out,fields
def cyl(M,ax_pt,ax_dir,rmax,extra=None):
    """boundary facets within rmax of an axis line"""
    a=np.asarray(ax_pt,float); d=np.asarray(ax_dir,float); d/=np.linalg.norm(d)
    def fn(x,y,z):
        P=np.stack([x-a[0],y-a[1],z-a[2]]); along=d@P; perp=P-np.outer(d,along); m=np.linalg.norm(perp,axis=0)<rmax
        return m&extra(x,y,z) if extra else m
    return M.facets_where(fn)
def near_axis(ax_pt,ax_dir,rmax,extra=None):
    a=np.asarray(ax_pt,float); d=np.asarray(ax_dir,float); d/=np.linalg.norm(d)
    def fn(x,y,z):
        P=np.stack([x-a[0],y-a[1],z-a[2]]); along=d@P; perp=P-np.outer(d,along); m=np.linalg.norm(perp,axis=0)<rmax
        return m&extra(x,y,z) if extra else m
    return fn
