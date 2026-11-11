import numpy as np, sys
from partstudy import *
R=lambda x,y:np.hypot(x,y)
def screws(z,angs,r=30.5,rad=4.0,rmin=25.5):
    out=[]
    for a in angs:
        c,s=np.cos(np.radians(a)),np.sin(np.radians(a))
        out.append((near_axis((r*c,r*s,z),(c,s,0),rad,lambda x,y,zz:R(x,y)>rmin),(0,1,2)))
    return out
def cage_bcsets():
    fixS=screws(13.45,[45,135,-45,-135],rmin=28.5)
    def hinge(M):
        L=[]
        for k in range(4):
            c,s=round(np.cos(k*np.pi/2)),round(np.sin(k*np.pi/2))
            fac=cyl(M,(25*c,25*s,0.19),(-s,c,0),2.4,lambda x,y,z:(z>-2.5)&(z<3))
            L.append((fac,[-10*c,-10*s,-20.]))
        return L
    bear=lambda M:M.facets_where(lambda x,y,z:(R(x,y)<6.2)&(z>0.2)&(z<3.9))
    A=(fixS,{'hinge_4flaps_22N':hinge,'bearing_lateral_20N':lambda M:[(bear(M),[20.,0,0])],
             'stop_block_torque':lambda M:[(M.facets_where(lambda x,y,z:(z>6)&(z<15)&(R(x,y)<20)),[0,9.,0])]})
    B=([(lambda x,y,z:(z<-9.7)&(R(x,y)>27),(0,1,2))],{'stack_axial_200N':lambda M:[(M.facets_where(lambda x,y,z:z>58.9),[0,0,-200.])]})
    return [A,B]
def lower_bcsets():
    fixS=screws(-26.55,[45,135,-45,-135])
    rim=lambda M:M.facets_where(lambda x,y,z:z<-73.5)
    top=lambda M:M.facets_where(lambda x,y,z:z>-14.9)
    return [(fixS,{'axial_200N_aft_rim':lambda M:[(rim(M),[0,0,200.])],'lateral_50N_aft_rim':lambda M:[(rim(M),[50.,0,0])],'axial_200N_coupler':lambda M:[(top(M),[0,0,-200.])],'lateral_50N_coupler':lambda M:[(top(M),[50.,0,0])]})]
def upper_bcsets():
    fixS=screws(83.45,[45,135,-69,-111],r=30.3,rmin=29)
    return [(fixS,{'axial_200N_skirt':lambda M:[(M.facets_where(lambda x,y,z:(z<60.9)&(R(x,y)>28)),[0,0,200.])],
                   'floor_inertia_15N':lambda M:[(M.facets_where(lambda x,y,z:(abs(z-71.94)<0.08)&(R(x,y)<29)),[0,0,-15.])],
                   'servo_mount_10N':lambda M:[(M.facets_where(lambda x,y,z:(z<60.3)&(R(x,y)<25)),[7.07,-7.07,0])]})]
def cap_bcsets():
    return [([(lambda x,y,z:z<82.0,(0,1,2))],{'pressure_20N':lambda M:[(M.facets_where(lambda x,y,z:z>89.9),[0,0,-20.])]})]
CFG=dict(cage=cage_bcsets,lower=lower_bcsets,upper=upper_bcsets,cap=cap_bcsets)
if __name__=='__main__':
    kind,nm,mesh=sys.argv[1:4]; d=np.load(mesh); study(nm,d['p'],d['t'],CFG[kind]())
