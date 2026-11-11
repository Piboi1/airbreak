from draw_common import *
import variants as V, json, math
from PIL import Image
BASE=V.BASE; REC=trimesh.load('var_REC.stl')
DOC='V5 air-brake rotor ("inner green piece") — weight-reduction cut drawing & FEA check'
NS=6
def sheet_wheel():
    fig=plt.figure(figsize=PAGE); title_block(fig,DOC,2,NS,'Sheet 2 — Cut A: cam-lobe pockets (×4)','Through-pockets in the cam wheel, as marked on your photo 1.  Red hatch = material removed.  View from the tab/servo side (+Z); your photo is the mirrored view from the shaft end.')
    ax=fig.add_axes([0.03,0.09,0.60,0.80]); W=V.wheel_poly(); draw_poly(ax,W)
    P=V.pocket_polys(w_out=2.4)
    for g in P: draw_poly(ax,g,fc='#ffe3e3',ec=CUT,hatch='////',lw=1.2,z=3)
    th=np.linspace(0,2*np.pi,200)
    for r,ls in [(21.0,':'),(10.5,'--')]: ax.plot(r*np.cos(th),r*np.sin(th),ls,color=MUTE,lw=0.7,zorder=4)
    ax.plot([-30,30],[0,0],'-.',color=MUTE,lw=0.5); ax.plot([0,0],[-30,30],'-.',color=MUTE,lw=0.5)
    # pick pocket in +x,+y quadrant
    g=[q for q in P if q.centroid.x>0 and q.centroid.y>0][0]; c=np.array(g.exterior.coords)
    # wall dimension at lobe outer profile: nearest points between pocket and exterior
    ext=W.exterior; i=np.argmax(np.hypot(c[:,0],c[:,1])); p_in=c[i]; p_out=np.array(ext.interpolate(ext.project(Point(p_in))).coords[0])
    dim(ax,p_in,p_out,'2.4',off=(2.2,1.2),color=CUT)
    # wall to window: find pocket point closest to the window hole near angle ~10deg
    holes=[Polygon(h) for h in W.interiors if Polygon(h).area>50]
    hx=min(holes,key=lambda h:abs(math.atan2(h.centroid.y,h.centroid.x)))
    d=[hx.exterior.distance(Point(p)) for p in c]; j=int(np.argmin(d)); pj=c[j]; ph=np.array(hx.exterior.interpolate(hx.exterior.project(Point(pj))).coords[0])
    dim(ax,pj,ph,'2.4',off=(2.6,-0.2),color=CUT)
    hy=min(holes,key=lambda h:abs(math.atan2(h.centroid.y,h.centroid.x)-math.pi/2))
    d=[hy.exterior.distance(Point(p)) for p in c]; j=int(np.argmin(d)); pj=c[j]; ph=np.array(hy.exterior.interpolate(hy.exterior.project(Point(pj))).coords[0])
    dim(ax,pj,ph,'2.4',off=(-0.6,2.4),color=CUT)
    leader(ax,(g.centroid.x,g.centroid.y),(31,24),'POCKET ×4 (pattern 90°)\nthrough all, 5.5 deep (Z 32.5 → 38.0)\narea 76.5 mm² each\nall inside corners R1.0 min',color=CUT)
    leader(ax,(10.5*math.cos(math.radians(45)),10.5*math.sin(math.radians(45))),(31,10),'pocket inner limit R10.5\n(keeps hub ring Ø16 + 2.5 web)',color=MUTE)
    leader(ax,(21*math.cos(math.radians(-8)),21*math.sin(math.radians(-8))),(31,-8),'base circle R21.0 (existing)',color=MUTE)
    leader(ax,(18*math.cos(math.radians(-100)),18*math.sin(math.radians(-100))),(31,-20),'existing windows R8.0–R18.0, 60° each\n— unchanged',color=MUTE)
    leader(ax,(3*math.cos(2.4),3*math.sin(2.4)),(-36,8),'bore Ø6.0\nunchanged',color=MUTE,ha='right')
    k=[q for q in P if q.centroid.x<0 and q.centroid.y>0][0]
    leader(ax,(-26.13,-11.6),(-37,-22),'lobe tip & full outer cam profile\nUNCHANGED (cam surface)',color=INK,ha='right')
    dim(ax,(-26.13,-31),(26.13,-31),'52.25 (existing envelope)',off=(0,-1.5),color=MUTE)
    clean(ax,None,(-56,52,-34,32))
    # right column: photo + table
    ax2=fig.add_axes([0.66,0.50,0.30,0.38]); ax2.imshow(Image.open('fig/user_photo_1.jpg')); ax2.axis('off'); ax2.set_title('Your markup (photo 1, seen from shaft end)',fontsize=9.5,loc='left',color=MUTE)
    ax3=fig.add_axes([0.66,0.10,0.30,0.37])
    rows=[['Feature','Value'],['Pocket rule','offset 2.4 mm inside every existing edge of the\nwheel (outer cam profile + the four windows),\nthen keep only what lies outside R10.5'],['Wall left','2.4 mm everywhere (6 perimeters @ 0.4 nozzle)'],['Corner radius','R1.0 minimum on all pocket corners'],['Depth','through (full 5.5 mm wheel thickness)'],['Removed','4 × 421 mm³ = 1 684 mm³  (2.09 g PLA solid)'],['Do NOT touch','outer cam profile, lobe tips, hub, bore'],['Exact outline','inner_piece_pocket_profile.dxf (1:1, mm)']]
    table(ax3,rows,[0.27,0.73],rowh=[0.09,0.2,0.1,0.1,0.1,0.1,0.1,0.1],fs=8.3)
    return fig
def sheet_arms():
    fig=plt.figure(figsize=PAGE); title_block(fig,DOC,3,NS,'Sheet 3 — Cuts B & C: latch-block wings and undersides (×4), tab-root gusset (added), arm holes (omitted)','Red hatch = removed.  Blue = material added.  Grey dashed = requested cut that is NOT recommended.  All features pattern ×4 at 90° about the shaft axis.')
    # --- plan view (z=46) of +X arm
    ax=fig.add_axes([0.03,0.20,0.41,0.62]); A=zsection(BASE,46)[0]; draw_poly(ax,A)
    for s in (1,-1):
        y0,y1=sorted((s*4.0,s*7.2)); draw_poly(ax,box(16.5,y0,26.0,y1),fc='#ffe3e3',ec=CUT,hatch='////',lw=1.2,z=3)
    ax.add_patch(Rectangle((23.6,-3),2.4,6,fill=False,ec=INK,lw=1.0,ls='-',zorder=5)); ax.text(24.8,0,'TAB',rotation=90,ha='center',va='center',fontsize=7.5,zorder=6)
    ax.add_patch(Rectangle((21.6,-3),2.0,6,fc='#d0ebff',ec=ADD,lw=1.2,zorder=5))
    ax.add_patch(Circle((12.5,0),1.5,fill=False,ec=MUTE,ls='--',lw=1.0,zorder=5)); ax.plot([11.2,13.8],[-1.3,1.3],color=CUT,lw=1.3,zorder=6); ax.plot([11.2,13.8],[1.3,-1.3],color=CUT,lw=1.3,zorder=6)
    ax.plot([-2,29],[0,0],'-.',color=MUTE,lw=0.5)
    dim(ax,(27.3,-4),(27.3,4),'8.0\nkeep',off=(1.6,0),fs=8.5); dim(ax,(32.0,-7.2),(32.0,7.2),'14.4\n(existing)',off=(2.4,0),color=MUTE)
    dim(ax,(16.5,9.0),(26.0,9.0),'9.5',off=(0,0.9),color=CUT); dim(ax,(15.3,4.0),(15.3,7.2),'3.2',off=(-1.3,0),color=CUT)
    dim(ax,(16.5,-9.0),(26.0,-9.0),'R16.5 → R26.0 from axis',off=(0,-1.0),color=MUTE)
    leader(ax,(21,5.6),(6,13.5),'CUT B: remove both side wings,\nfull block height (Z 38.6 → 48.6).\nSides become flush with the 8.0 mm arm.',color=CUT)
    leader(ax,(22.6,-1.5),(4,-13),'ADD G: tab-root gusset, 6.0 wide,\n2.0 × 2.0 (45° chamfer) on the hub side\nof each tab — see elevation',color=ADD)
    leader(ax,(12.5,1.5),(-4,9),'Ø3 arm hole (your photo-1 dots):\nOMIT — saves 0.04 g each,\nraises arm stress 30–60 %',color=MUTE)
    clean(ax,'PLAN — +X arm, viewed from the servo side (+Z), section at Z 46',(-9,38,-19,19))
    # --- elevation: radial section through the arm centre plane (y=0), x>0
    ax=fig.add_axes([0.45,0.47,0.27,0.41])
    for e in plane_section(BASE,(0,0.001,0),(0,1,0),(1,0,0),(0,0,1)):
        if e[:,0].max()>0: ax.plot(e[:,0],e[:,1],color=INK,lw=0.9,zorder=4)
    draw_poly(ax,box(16.5,38.6,26.0,43.6),fc='#ffe3e3',ec=CUT,hatch='////',lw=1.2,z=3)
    ax.add_patch(MPoly([[21.6,48.6],[23.6,48.6],[23.6,50.6]],fc='#d0ebff',ec=ADD,lw=1.2,zorder=6))
    dim(ax,(28.0,43.6),(28.0,48.6),'5.0\nkeep',off=(1.6,0)); dim(ax,(28.0,38.6),(28.0,43.6),'5.0',off=(1.3,0),color=CUT)
    dim(ax,(23.6,56.0),(26.0,56.0),'2.4',off=(0,0.9),color=MUTE); dim(ax,(30.6,48.6),(30.6,54.8),'6.2',off=(1.2,0),color=MUTE)
    leader(ax,(22.6,49.4),(12,53.5),'G: 2.0 × 2.0\nchamfer gusset',color=ADD,ha='center')
    leader(ax,(20,41),(4,40.7),'CUT C: remove everything\nbelow the arm underside\n(Z 43.6), incl. the 0.8 pad',color=CUT,ha='left')
    ax.text(13,35.2,'cam wheel (Z 32.5–38.0)',fontsize=7.5,color=MUTE,ha='center')
    clean(ax,'ELEVATION — radial section through arm centre',(-1,34,31,58))
    # --- front view of the block looking radially inward
    ax=fig.add_axes([0.74,0.47,0.23,0.41])
    ax.add_patch(Rectangle((-7.2,39.4),14.4,9.2,fc='#ffe3e3',ec=CUT,hatch='////',lw=1.2,zorder=2))
    ax.add_patch(Rectangle((-5.2,38.6),10.4,0.8,fc='#ffe3e3',ec=CUT,hatch='////',lw=1.0,zorder=2))
    ax.add_patch(Rectangle((-4,43.6),8,5.0,fc=KEEP,ec=INK,lw=1.1,zorder=3)); ax.add_patch(Rectangle((-3,48.6),6,6.2,fc=KEEP,ec=INK,lw=1.1,zorder=3))
    ax.text(0,46.1,'KEEP\n8.0 × 5.0',ha='center',va='center',fontsize=8.5,zorder=5); ax.text(0,51.7,'tab\n6.0 wide',ha='center',va='center',fontsize=8,zorder=5)
    dim(ax,(-7.2,37.4),(7.2,37.4),'14.4 existing',off=(0,-0.9),color=MUTE); dim(ax,(-4,49.6),(-7.2,49.6),'3.2',off=(-0.2,1.0),color=CUT); dim(ax,(4,49.6),(7.2,49.6),'3.2',off=(0.2,1.0),color=CUT)
    dim(ax,(9.0,39.4),(9.0,48.6),'9.2\nexisting',off=(1.9,0),color=MUTE)
    clean(ax,'END VIEW — block from outside (cf. photo 3)',(-11,13.5,35,57))
    # --- photos + notes
    for k,(i,x) in enumerate([(2,0.45),(3,0.585)]):
        a=fig.add_axes([x,0.10,0.125,0.33]); a.imshow(Image.open(f'fig/user_photo_{i}.jpg')); a.axis('off'); a.set_title(f'Your markup (photo {i})',fontsize=9,loc='left',color=MUTE)
    ax=fig.add_axes([0.725,0.10,0.245,0.33])
    rows=[['Cut','Removed (×4 total)','Verdict'],['B  side wings','2 281 mm³  (2.83 g)','OK — cut'],['C  undersides','2 488 mm³  (3.09 g)','OK — cut'],['B + C together','3 704 mm³  (4.59 g)',''],['D  arm holes Ø3','141 mm³  (0.17 g)','omit'],['G  tab gusset','+19 mm³  (+0.02 g)','add']]
    cols=[None,[None,None,OKC],[None,None,OKC],None,[None,None,CUT],[None,None,ADD]]
    table(ax,rows,[0.36,0.42,0.22],rowh=[0.12]*6,fs=8.3,colors=cols)
    ax.text(0,0.20,'After B + C each latch block is simply the 8.0 × 5.0 arm\ncontinued out to R26.0 with the tab on top.  Check: the\nblock underside sat 0.4 mm above the flap cam pad — no\ncontact, so removing it only adds clearance.',transform=ax.transAxes,fontsize=8.2,va='top',color=INK,linespacing=1.35)
    return fig
RHO=1.24e-3; S_IN,S_Z=35.0,15.0
def load():
    R={}
    for v in ['BASE','A_full','B','C','D','G','ALL','REC']: R[v]=json.load(open(f'res_{v}.json'))
    return R
def sf(r,lc):
    best=(99,'',0,0)
    for reg,d in r['lc'][lc].items():
        if reg=='work': continue
        a=S_IN/max(d['vm_max'],1e-9); b=S_Z/max(d['szz_max'],1e-9); s=min(a,b)
        if s<best[0]: best=(s,reg,d['vm_max'],d['szz_max'])
    return best
LCN={'latch_radial_10N_x4':'Latch: 10 N radial on each tab','tab_tangential_10N_x1':'Jam: 10 N tangential on one tab','tab_axial_10N_x4':'Axial: 10 N down on each tab','cam_20deg_20N_x4':'Cam 20 N/lobe, early (20°)','cam_40deg_20N_x4':'Cam 20 N/lobe, mid (40°)','cam_58deg_20N_x4':'Cam 20 N/lobe, full (58°)'}
def sheet_summary(R):
    fig=plt.figure(figsize=PAGE); title_block(fig,DOC,1,NS,'Sheet 1 — Summary: which of the requested cuts are safe','Finite-element check of the three photo mark-ups on the V5 inner piece (file: V5_modular_assembly_inner_piece.stl).')
    vb=R['BASE']['vol']; g=lambda v:v*RHO
    def pc(a,b): return '%+.0f %%'%(100*(a/b-1))
    def reg(v,lc,rg,k): return R[v]['lc'][lc][rg][k]
    rows=[['Cut (your markup)','Solid mass removed','What the FEA shows (vs. the uncut part, same loads)','Verdict'],
     ['A  Lobe pockets ×4\n    (photo 1, black areas)','%.2f g  (%.1f %%)'%(g(vb-R['A_full']['vol']),100*(1-R['A_full']['vol']/vb)),
      'Cam load: rim stress %s (peak %.1f → %.1f MPa), wheel %s more flexible.\nSpokes, hub and shaft unchanged.  Rim keeps ≥ %.1f× margin at 20 N per lobe.'%(pc(reg('A_full','cam_40deg_20N_x4','wheel_rim','vm_p999'),reg('BASE','cam_40deg_20N_x4','wheel_rim','vm_p999')),reg('BASE','cam_20deg_20N_x4','wheel_rim','p1_max'),reg('A_full','cam_20deg_20N_x4','wheel_rim','p1_max'),pc(R['A_full']['lc']['cam_20deg_20N_x4']['work'],R['BASE']['lc']['cam_20deg_20N_x4']['work']),min(min(S_IN/R['A_full']['lc'][l]['wheel_rim']['vm_max'],S_Z/R['A_full']['lc'][l]['wheel_rim']['szz_max']) for l in LCN if l.startswith('cam'))),'SAFE — cut'],
     ['B  Block side wings ×8\n    (photo 2, scribbles)','%.2f g  (%.1f %%)'%(g(vb-R['B']['vol']),100*(1-R['B']['vol']/vb)),'No load path runs through the wings.  Tab-root, arm and hub stresses change\nby less than ±10 %% (mesh noise level); latch stiffness %s.'%pc(R['BASE']['lc']['latch_radial_10N_x4']['work'],R['B']['lc']['latch_radial_10N_x4']['work']),'SAFE — cut'],
     ['C  Block undersides ×4\n    (photo 3, scribbles)','%.2f g  (%.1f %%)'%(g(vb-R['C']['vol']),100*(1-R['C']['vol']/vb)),'Same: dead weight hanging under the arm.  Stresses within ±10 %%; latch\nstiffness %s.  Underside never touched the flap (0.4 mm gap).'%pc(R['BASE']['lc']['latch_radial_10N_x4']['work'],R['C']['lc']['latch_radial_10N_x4']['work']),'SAFE — cut'],
     ['D  Arm holes Ø3 ×4\n    (photo 1, circled dots)','%.2f g  (%.1f %%)'%(g(vb-R['D']['vol']),100*(1-R['D']['vol']/vb)),'Arm stress %s under tab (latch) load and %s under axial load, arm %s\nmore flexible — on the only load path to the tabs, for 0.17 g.'%(pc(reg('D','latch_radial_10N_x4','arm','vm_p999'),reg('BASE','latch_radial_10N_x4','arm','vm_p999')),pc(reg('D','tab_axial_10N_x4','arm','vm_p999'),reg('BASE','tab_axial_10N_x4','arm','vm_p999')),pc(R['D']['lc']['tab_axial_10N_x4']['work'],R['BASE']['lc']['tab_axial_10N_x4']['work'])),'KEEP material\n(do not drill)'],
     ['G  Tab-root gusset ×4\n    (our addition)','+%.2f g'%g(R['G']['vol']-vb),'The tab root is the weakest point of the part with or without the cuts\n(it is where your print broke).  A 2 × 2 mm gusset drops its peak cross-layer\nstress %s (%.1f → %.1f MPa per 10 N).'%(pc(reg('G','latch_radial_10N_x4','tab','szz_max'),reg('BASE','latch_radial_10N_x4','tab','szz_max')),reg('BASE','latch_radial_10N_x4','tab','szz_max'),reg('G','latch_radial_10N_x4','tab','szz_max')),'ADD']]
    cols=[None,[None,None,None,OKC],[None,None,None,OKC],[None,None,None,OKC],[None,None,None,CUT],[None,None,None,ADD]]
    ax=fig.add_axes([0.03,0.47,0.94,0.42]); table(ax,rows,[0.17,0.13,0.56,0.14],rowh=[0.10,0.18,0.18,0.18,0.18,0.18],fs=9,colors=cols)
    ax=fig.add_axes([0.03,0.09,0.36,0.36]); ax.axis('off')
    t=[['Version','Solid volume','Solid PLA mass','Saving'],['Original','%.0f mm³'%vb,'%.2f g'%g(vb),'—'],['As marked (A+B+C+D)','%.0f mm³'%R['ALL']['vol'],'%.2f g'%g(R['ALL']['vol']),'%.1f %%'%(100*(1-R['ALL']['vol']/vb))],['Recommended (A+B+C+G)','%.0f mm³'%R['REC']['vol'],'%.2f g'%g(R['REC']['vol']),'%.1f %%'%(100*(1-R['REC']['vol']/vb))]]
    y=table(ax,t,[0.36,0.22,0.22,0.20],rowh=[0.13]*4,fs=9,colors=[None,None,None,[ADD,None,None,ADD]])
    ax.text(0,y-0.05,'Masses are for 100 % solid PLA (1.24 g/cm³); the real saving scales with your\ninfill and wall settings.  The recommended version gives up 0.2 g versus the\nas-marked version and is the one supplied as the primary STL.\n\nBoth versions are delivered:\n  V5_inner_piece_lightened_recommended.stl\n  V5_inner_piece_lightened_as_marked.stl',transform=ax.transAxes,fontsize=9,va='top',linespacing=1.4)
    for k,(f,x) in enumerate([('fig/rotor_REC_top.png',0.41),('fig/rotor_REC_bottom.png',0.69)]):
        a=fig.add_axes([x,0.085,0.28,0.37]); a.imshow(Image.open(f).crop((120,20,1000,900))); a.axis('off')
    fig.text(0.97,0.455,'Recommended part.  Red = removed, blue = added.',fontsize=9,color=MUTE,ha='right')
    return fig
def sheet_setup(R):
    fig=plt.figure(figsize=PAGE); title_block(fig,DOC,4,NS,'Sheet 4 — How the check was run (FEA set-up and assumptions)','Please correct any assumption that is wrong — the conclusions on Sheet 1 depend on them.')
    ax=fig.add_axes([0.03,0.10,0.42,0.78]); W=V.wheel_poly(); draw_poly(ax,W)
    A=zsection(BASE,46)[0]; ax.plot(*A.exterior.xy,color=MUTE,lw=0.7,ls='--',zorder=4)
    pat=R['BASE']['patches']
    for a,colr in zip(['20','40','58'],['#1c7ed6','#e8590c','#2b8a3e']):
        pt=np.array(pat[a]['pt']); n=np.array(pat[a]['normal'])
        for k in range(4):
            c,s=round(math.cos(k*math.pi/2)),round(math.sin(k*math.pi/2)); p=np.array([c*pt[0]-s*pt[1],s*pt[0]+c*pt[1]]); d=np.array([c*n[0]-s*n[1],s*n[0]+c*n[1]])
            ax.annotate('',xy=p,xytext=p-9*d,arrowprops=dict(arrowstyle='-|>',color=colr,lw=1.6,mutation_scale=12),zorder=8)
        ax.text(*(pt-11.5*n),f'{a}°',color=colr,fontsize=9,ha='center',va='center',fontweight='bold')
    for k in range(4):
        c,s=round(math.cos(k*math.pi/2)),round(math.sin(k*math.pi/2)); p=np.array([23.6*c,23.6*s]); ax.annotate('',xy=p+8*np.array([c,s]),xytext=p,arrowprops=dict(arrowstyle='-|>',color=CUT,lw=1.6,mutation_scale=12),zorder=8)
    ax.text(33,3,'latch\n10 N',color=CUT,fontsize=8.5,ha='center')
    clean(ax,'Load application points (plan view)',(-38,40,-36,36))
    ax=fig.add_axes([0.48,0.10,0.49,0.78]); ax.axis('off')
    tq=pat['40']['torque_Nmm']/1000
    txt=f'''MODEL
• Solver: linear-elastic FEA, 10-node (quadratic) tetrahedra, ≈ 75 000–93 000 elements / 0.37–0.43 M unknowns per variant,
  1.3 mm target edge.  Every variant re-meshed and re-solved with identical loads and supports.
• Material: PLA, E = 2.3 GPa, ν = 0.35.  Allowable stress 35 MPa in the layer plane (von Mises) and 15 MPa in tension
  across layers (σzz) — conservative FDM values.  Layers assumed normal to the shaft axis, as in your photos.
• Supports: top hub (servo-horn socket, Z > 51.3) fully held; lower shaft journal (Z < 12) held radially only, free to
  rotate, so all torque goes up the shaft to the servo.

LOAD CASES (reference loads — stresses scale linearly with load)
1. Latch: 10 N radially outward on the inner face of each tab (flap hook pulling on the tab, flaps stowed).
2. Jam: 10 N tangential on the side of one tab (≈ stall torque of a 9 g-class servo, 0.22 N·m, acting at R24.8).
3. Axial: 10 N pressing down on the top of each tab (handling / assembly / flap pushed down on the latch).
4–6. Cam: flap pad pushing each lobe with 20 N normal + 0.3 friction, at 20°, 40° and 58° of rotor travel
  (contact point marked left).  This equals {abs(tq):.2f} N·m at the shaft, i.e. several times what a micro servo can hold,
  so it is an upper bound for flight load carried through the cam.  20 N ≈ full stagnation pressure on one
  34.6 × 61.6 mm flap at ~105 m/s.

HOW "SAFE" WAS JUDGED
A cut passes if (a) peak stress in every region stays well inside the allowables at the reference loads, (b) it does
not raise stress on the tab → arm → hub load path that failed in your earlier print, and (c) the stiffness loss is small.
Peak values exclude elements within 1 mm of load patches and clamps (numerical hot spots).

LIMITS OF THIS CHECK
• Loads are estimates: we do not know your flight speed, servo or flap spring forces.  Compare the "load to reach
  allowable" column on Sheet 5 with your real numbers.
• Linear static analysis: no impact, fatigue, creep or heat-softening, and FDM strength varies ±30 % with print
  settings.  Sharp inside corners read mesh-dependent peaks; that is why every cut corner gets R1.0.
• Fit/function of faces we could not see being used (block underside, wings) was checked only for clearance against
  the flaps and cage in asm-v5-acc.stl (stowed position).'''
    ax.text(0,1,txt,transform=ax.transAxes,fontsize=9.2,va='top',linespacing=1.45)
    return fig
def sheet_results(R):
    fig=plt.figure(figsize=PAGE); title_block(fig,DOC,5,NS,'Sheet 5 — FEA results: original vs. as-marked vs. recommended','Minimum safety factor = allowable ÷ peak stress at the reference load.  "Load to allowable" = reference load × safety factor.')
    rows=[['Load case','Original\nmin SF (where)','As marked\nmin SF (where)','Recommended\nmin SF (where)','Recommended:\nload to allowable']]
    nice={'tab':'tab root','tab_root_block':'block','arm':'arm','hub':'hub/shaft','wheel_rim':'lobe rim','wheel_spoke':'wheel spoke','wheel_hub':'wheel hub','shaft':'shaft'}
    for lc,nm in LCN.items():
        r=[nm]
        for v in ['BASE','ALL','REC']:
            s=sf(R[v],lc); r.append('%.1f  (%s)'%(s[0],nice[s[1]]))
        ref=10 if 'cam' not in lc else 20; r.append('≈ %.0f N %s'%(ref*sf(R['REC'],lc)[0],'per tab' if 'x4' in lc and 'cam' not in lc else ('per lobe' if 'cam' in lc else 'on one tab')))
        rows.append(r)
    ax=fig.add_axes([0.03,0.60,0.56,0.28]); table(ax,rows,[0.30,0.17,0.17,0.19,0.17],rowh=[0.19]+[0.135]*6,fs=8.8)
    ax=fig.add_axes([0.61,0.60,0.36,0.28]); ax.axis('off')
    b=R['BASE']['lc']['latch_radial_10N_x4']['tab']['szz_max']; a=R['ALL']['lc']['latch_radial_10N_x4']['tab']['szz_max']; r_=R['REC']['lc']['latch_radial_10N_x4']['tab']['szz_max']
    ax.text(0,1,f'''READING THE TABLE
• The tab root governs the tab load cases in every version: the
  cuts do not make it worse (peak cross-layer stress per 10 N:
  original {b:.1f}, as marked {a:.1f}, recommended {r_:.1f} MPa).
• Predicted tab break load (radial pull): original ≈ {150/b:.0f} N,
  recommended ≈ {150/r_:.0f} N.  A finger can exceed either —
  handle the tabs with care and print them hot / slow.
• Cam cases are governed by torque in the Ø10/Ø6 hollow shaft
  and wheel hub, which none of the cuts touch.
• The lobe pockets raise rim stress, but the rim stays far from
  governing.
• Differences of ±15 % between versions on the same feature
  are mesh noise, not a real change.''',transform=ax.transAxes,fontsize=9,va='top',linespacing=1.42)
    for k,(f,t) in enumerate([('fig/vm_BASE_latch_radial.png','Original — latch 10 N/tab'),('fig/vm_REC_latch_radial.png','Recommended — latch 10 N/tab'),('fig/vm_BASE_cam_40deg.png','Original — cam 20 N/lobe (40°)'),('fig/vm_REC_cam_40deg.png','Recommended — cam 20 N/lobe (40°)')]):
        a=fig.add_axes([0.03+k*0.237,0.09,0.23,0.47]); a.imshow(Image.open(f).crop((60,40,1000,800))); a.axis('off'); a.set_title(t,fontsize=9.5,loc='left',color=INK)
    return fig
def sheet_notes(R):
    fig=plt.figure(figsize=PAGE); title_block(fig,DOC,6,NS,'Sheet 6 — Build notes and open questions','')
    ax=fig.add_axes([0.03,0.10,0.50,0.80]); ax.axis('off')
    ax.text(0,1,'''CHANGE LIST FOR CAD (inner piece, STL coordinates, Z along shaft, tabs at Z 48.6–54.8)
1. Cam wheel (Z 32.5–38.0): cut four through-pockets per Sheet 2 — 2.4 mm wall to the outer cam profile and to
   the four windows, nothing inside R10.5, R1.0 corners.  Outline supplied as DXF.
2. Latch blocks ×4: remove both side wings so the block is 8.0 wide (flush with the arm), from R16.5 to R26.0.
3. Latch blocks ×4: remove everything below Z 43.6 (the arm underside), including the 0.8 mm pad, from R16.5 outward.
4. Do not drill the Ø3 holes in the arms.
5. Add a 2.0 × 2.0 mm, 6.0 wide 45° gusset at the hub-side root of each tab (R21.6–R23.6, Z 48.6–50.6).

PRINTING
• The tabs are the weak link: 6.0 × 2.4 mm, loaded across the layers when printed shaft-vertical.  Use ≥ 4 perimeters
  so the tab and gusset are solid, print PLA at the hot end of its range with low fan for those layers, or switch the
  part to PETG / PLA+ for better layer adhesion.
• After cuts B + C the arm ends and the pockets need the same supports as today (the arms already overhang the wheel).
• The wheel pockets print without support (vertical walls).

PLEASE CONFIRM
a) The four circled dots in photo 1: we read them as Ø3 lightening holes through the arms.  If they mean something
   else (e.g. screw or pin holes that are needed), tell us and we will add them back with a local boss.
b) The gusset uses the space under the flap hook: the hook leg bottom sits 3.2 mm above the block top in the
   assembly STL and the gusset is 2.0 mm high, leaving 1.2 mm.  Check on the real parts before printing four.
c) Flight speed / servo model, so the reference loads on Sheet 4 can be replaced by real ones.
d) Rotor balance is unaffected (all cuts are 4-fold symmetric); inertia drops, which helps the servo.''',transform=ax.transAxes,fontsize=9.3,va='top',linespacing=1.5)
    for k,(f,t,y) in enumerate([('fig/rotor_ALL_top.png','As-marked version (includes arm holes)',0.50),('fig/rotor_REC_top.png','Recommended version (no holes, gussets)',0.10)]):
        a=fig.add_axes([0.56,y,0.40,0.38]); a.imshow(Image.open(f).crop((120,20,1000,900))); a.axis('off'); a.set_title(t,fontsize=9.5,loc='left')
    return fig
if __name__=='__main__':
    import sys
    if len(sys.argv)>1:
        from matplotlib.backends.backend_pdf import PdfPages
        R=load()
        with PdfPages(sys.argv[1]) as pdf:
            for f in [sheet_summary(R),sheet_wheel(),sheet_arms(),sheet_setup(R),sheet_results(R),sheet_notes(R)]: pdf.savefig(f,dpi=150); plt.close(f)
        sys.exit()
    sheet_wheel().savefig('fig/sheet_wheel.png',dpi=70); sheet_arms().savefig('fig/sheet_arms.png',dpi=70)
