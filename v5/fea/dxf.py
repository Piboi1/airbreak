import numpy as np, variants as V
def write(path,layers):
    L=['0','SECTION','2','ENTITIES']
    for name,rings in layers.items():
        for r in rings:
            r=np.asarray(r)[:-1] if np.allclose(r[0],r[-1]) else np.asarray(r)
            L+=['0','POLYLINE','8',name,'66','1','70','1']
            for x,y in r: L+=['0','VERTEX','8',name,'10','%.4f'%x,'20','%.4f'%y,'30','0.0']
            L+=['0','SEQEND']
    L+=['0','ENDSEC','0','EOF']; open(path,'w').write('\n'.join(L)+'\n')
W=V.wheel_poly(); P=V.pocket_polys(w_out=2.4)
write('inner_piece_pocket_profile.dxf',{'WHEEL_EXISTING':[W.exterior.coords]+[h.coords for h in W.interiors],'POCKET_CUT':[g.exterior.coords for g in P]})
print('dxf ok',len(P))
