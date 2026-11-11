import numpy as np, sys
from partstudy import *
def flap_bcsets():
    R=lambda x,y:np.hypot(x,y)
    bore=near_axis((25.0,0,0.19),(0,1,0),2.2)
    padfix=lambda x,y,z:(abs(x-23.0)<0.05)&(z>19.5)&(z<30)&(abs(y)<4.2)
    hookfix=lambda x,y,z:(abs(x-22.8)<0.08)&(z>41.5)&(z<48)&(abs(y)<3.2)
    outer=lambda M:M.facets_where(lambda x,y,z:(R(x,y)>32.0)&(z>3))
    top=lambda M:M.facets_where(lambda x,y,z:(z>54.0))
    rad=lambda s:(lambda x,y,z:np.stack([s*x/R(x,y),s*y/R(x,y),0*x]))
    A=([(bore,(0,1,2)),(padfix,(0,))],{'aero_deployed_20N':lambda M:[(outer(M),rad(-1.0),20.0)],'side_5N_top':lambda M:[(top(M),[0,5.,0])]})
    B=([(bore,(0,1,2)),(hookfix,(0,))],{'latched_pull_10N':lambda M:[(outer(M),rad(1.0),10.0)]})
    return [A,B]
if __name__=='__main__':
    nm=sys.argv[1]; d=np.load(sys.argv[2]); study(nm,d['p'],d['t'],flap_bcsets(),iso=True)
