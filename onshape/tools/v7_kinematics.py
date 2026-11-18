import pickle, numpy as np, trimesh, json
W='/tmp/claude-0/-home-user-airbreak/2a03b965-bd6f-5144-bd29-b03796006798/scratchpad/work'
p=pickle.load(open(W+'/v7.pkl','rb')); g=lambda k:[m for _,(n,m) in p.items() if n.startswith(k)][0]
F=g('P1 '); R=g('V7 lower'); C=g('C V5')
X=lambda a,b: trimesh.boolean.intersection([a,b],engine='manifold').volume
def fin(th):
    m=F.copy(); m.apply_transform(trimesh.transformations.rotation_matrix(np.radians(th),[0,1,0],point=[25,0,0])); return m
def rot(ph):
    m=R.copy(); m.apply_transform(trimesh.transformations.rotation_matrix(np.radians(ph),[0,0,1])); return m
out={}
# 1) latch: at rotor 0, how far can the fin open before it hits the rotor?
for ph in (0,):
    r=rot(ph); free=None
    for th in np.arange(0,20.5,0.5):
        if X(fin(th),r)>0.3: free=th; break
    print('rotor %d deg: fin can open only to %s deg before touching the rotor (latch)'%(ph,free))
# 2) sweep: smallest fin angle that clears the rotor at each rotor angle (the push), and does the rotor clear the housing
res=[]
for ph in np.arange(0,65.1,5):
    r=rot(ph); thmin=None
    for th in np.arange(0,91,1.0):
        if X(fin(th),r)<0.3: thmin=th; break
    hc=X(r,C)
    res.append((ph,thmin,round(hc,2))); print('rotor %4.1f  fin pushed to >= %s deg   rotor-housing overlap %.2f mm3'%(ph,thmin,hc),flush=True)
# 3) fully open fin vs housing and vs rotor at 65
print('fin at 90 vs housing overlap %.2f, vs rotor at 65 %.2f'%(X(fin(90),C),X(fin(90),rot(65))))
json.dump(res,open(W+'/v7_kin.json','w'))
