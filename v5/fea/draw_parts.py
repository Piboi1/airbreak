from draw_common import *
import json, math, os
from shapely.ops import unary_union
def sec_polys(m,origin,normal,u,v):
    """filled cross-section (even-odd) as shapely geometry in (u,v) coords"""
    loops=plane_section(m,origin,normal,u,v); g=None
    for e in loops:
        if len(e)<4: continue
        q=Polygon(e)
        if not q.is_valid: q=q.buffer(0)
        if q.area<1e-4: continue
        g=q if g is None else g.symmetric_difference(q)
    return g
def geoms(g):
    if g is None or g.is_empty: return []
    return [q for q in (g.geoms if hasattr(g,'geoms') else [g]) if q.geom_type=='Polygon' and q.area>0.02]
def diff_view(ax,base,prop,origin,normal,u,v,min_area=0.15):
    b=sec_polys(base,origin,normal,u,v); p=sec_polys(prop,origin,normal,u,v)
    for q in geoms(b): draw_poly(ax,q,fc=KEEP,ec=INK,lw=0.9)
    rem=b.difference(p.buffer(0.01)) if p is not None else b
    out=[q for q in geoms(rem) if q.area>min_area]
    for q in out: draw_poly(ax,q,fc='#ffe3e3',ec=CUT,hatch='////',lw=1.1,z=3)
    return b,out
Z=(0,0,1)
def radial(a): c,s=math.cos(math.radians(a)),math.sin(math.radians(a)); return (c,s,0),(-s,c,0)
L={n:trimesh.load(f'part_{n}.stl') for n in ['flap','lower','cage','upper','cap']}
P={n:trimesh.load(f'prop_{n}.stl') for n in ['flap','lower','lowerL3','cage','upper','cap']}
def fig_flap(fig):
    ax=fig.add_axes([0.03,0.10,0.24,0.76])   # inside elevation: section plane x=28.9 gives the inner features; plus silhouette
    yz=((0,1,0),(0,0,1))
    b=sec_polys(L['flap'],(29.0,0,0),(1,0,0),*yz)
    sil=box(-17.3,4.2,17.3,54.2); draw_poly(ax,sil,fc='#f8f9fa',ec=INK,lw=0.9)
    for q in geoms(b): draw_poly(ax,q,fc=KEEP,ec=MUTE,lw=0.6)
    for s in (1,-1):
        y0,y1=sorted((s*3.8,s*10.5)); draw_poly(ax,box(y0,22.0,y1,51.0),fc='#ffe3e3',ec=CUT,hatch='////',lw=1.1,z=4)
        y0,y1=sorted((s*2.0,s*10.5)); draw_poly(ax,box(y0,11.5,y1,19.0),fc='#ffe3e3',ec=CUT,hatch='////',lw=1.1,z=4)
    ax.add_patch(Rectangle((-6,-4.8),12,10,fc='#f8f9fa',ec=INK,lw=0.9,zorder=2)); ax.text(0,0.2,'hinge knuckle',ha='center',va='center',fontsize=7.5,color=MUTE,zorder=5)
    ax.text(0,25,'cam\npad',ha='center',va='center',fontsize=7.5,color=MUTE,zorder=6); ax.text(0,46,'latch\nhook',ha='center',va='center',fontsize=7.5,color=MUTE,zorder=6)
    dim(ax,(3.8,52.6),(10.5,52.6),'6.7',off=(0,1.2),color=CUT); dim(ax,(-19.5,22),(-19.5,51),'29.0',off=(-2.4,0),color=CUT); dim(ax,(-19.5,11.5),(-19.5,19),'7.5',off=(-2.2,0),color=CUT)
    dim(ax,(2.0,9.8),(10.5,9.8),'8.5',off=(0,-1.3),color=CUT); dim(ax,(-3.8,56.2),(3.8,56.2),'7.6 web',off=(0,1.3),color=MUTE)
    leader(ax,(7,36),(21,40),'F1 ×2\nskin 2.5 → 1.5',color=CUT); leader(ax,(6,15),(21,15),'F2 ×2\nskin 4.7 → 2.0',color=CUT)
    clean(ax,'INSIDE FACE (seen from rocket axis)',(-24,31,-9,60))
    ax=fig.add_axes([0.27,0.10,0.14,0.76])   # vertical section at y=7
    b,rem=diff_view(ax,L['flap'],P['flap'],(0,7.0,0),(0,1,0),(1,0,0),Z)
    dim(ax,(30.7,54.9),(32.1,54.9),'1.5',off=(0,1.3),color=CUT); dim(ax,(30.2,8.6),(32.1,8.6),'2.0',off=(0,-1.3),color=CUT)
    leader(ax,(30.2,37),(21.5,37),'F1: 1.0 deep',color=CUT,ha='center'); leader(ax,(28.8,15.2),(21.5,22),'F2: 2.7 deep',color=CUT,ha='center')
    ax.text(33.3,30,'outer (aero) face — unchanged',rotation=90,fontsize=7.5,color=MUTE,va='center')
    clean(ax,'SECTION y = 7',(18,35,-9,60))
    ax=fig.add_axes([0.43,0.52,0.25,0.34]); b,rem=diff_view(ax,L['flap'],P['flap'],(0,0,40.0),Z,(0,1,0),(1,0,0)); clean(ax,'SECTION Z = 40 (through F1)',(-19,19,18.5,34))
    ax=fig.add_axes([0.43,0.14,0.25,0.34]); b,rem=diff_view(ax,L['flap'],P['flap'],(0,0,15.0),Z,(0,1,0),(1,0,0)); clean(ax,'SECTION Z = 15 (through F2)',(-19,19,18.5,34))
def fig_lower(fig):
    ax=fig.add_axes([0.03,0.10,0.26,0.76]); u,n=radial(0)
    b,rem=diff_view(ax,L['lower'],P['lower'],(0,0,0),n,u,Z)
    # optional L3
    ax.add_patch(Rectangle((26.0,-38.5),1.2,23.7,fc='none',ec=WARN,hatch='\\\\\\\\',lw=1.0,zorder=5))
    dim(ax,(27.6,-41.2),(26.0,-41.2),'1.6',off=(-2.6,0),color=CUT); dim(ax,(30.2,-25.2),(32.2,-25.2),'2.0',off=(2.6,0),color=CUT)
    dim(ax,(24.2,-26.55),(24.2,-28.1),'1.6',off=(-2.0,0),color=CUT)
    leader(ax,(28.9,-33),(12,-31),'L1: core out shoulder\nR27.6 → R30.2\nfrom underside to Z −28.1',color=CUT,ha='center')
    leader(ax,(29.2,-55),(12,-55),'L2: cone wall\n2.0 → 1.5 (inside only)',color=CUT,ha='center')
    leader(ax,(26.6,-20),(12,-18),'L3 (optional, orange):\nopen bore Ø52 → Ø54.4\nonly if Ø52 is not a fit',color=WARN,ha='center')
    ax.text(33.2,-56,'outer surface unchanged',rotation=84,fontsize=7.5,color=MUTE,va='center')
    clean(ax,'HALF SECTION at 0° (between screws)',(2,38,-76,-12))
    ax=fig.add_axes([0.30,0.10,0.16,0.76]); u,n=radial(45)
    b,rem=diff_view(ax,L['lower'],P['lower'],(0,0,0),n,u,Z)
    leader(ax,(28.5,-32.5),(17,-22),'screw / nut boss\nkept solid\n(±17° about\neach screw)',color=INK,ha='center')
    clean(ax,'HALF SECTION at 45° (through screw)',(12,36,-76,-12))
    ax=fig.add_axes([0.47,0.30,0.22,0.56]); b,rem=diff_view(ax,L['lower'],P['lower'],(0,0,-33.0),Z,(1,0,0),(0,1,0))
    for a in (45,135,225,315): ax.plot([0,34*math.cos(math.radians(a))],[0,34*math.sin(math.radians(a))],'-.',color=MUTE,lw=0.5)
    ax.text(0,0,'4 pockets × 56°\n4 solid bosses × 34°\n(on the screw axes)',ha='center',va='center',fontsize=8.5)
    clean(ax,'SECTION Z = −33 (shoulder)',(-35,35,-35,35))
def fig_cage(fig):
    ax=fig.add_axes([0.03,0.12,0.66,0.74]); b,rem=diff_view(ax,L['cage'],P['cage'],(0,0,-8.8),Z,(1,0,0),(0,1,0))
    up=sec_polys(L['cage'],(0,0,-6.0),Z,(1,0,0),(0,1,0))
    for q in geoms(up): draw_poly(ax,q,fc='#dee2e6',ec=MUTE,lw=0.6,z=4)
    cp=sec_polys(L['cage'],(0,0,2.0),Z,(1,0,0),(0,1,0))
    for q in geoms(cp): ax.plot(*q.exterior.xy,color=ADD,lw=0.7,ls='--',zorder=5)
    dim(ax,(0,0),(15*math.cos(math.radians(22)),15*math.sin(math.radians(22))),'R15.0',off=(1.5,2.0),color=CUT); dim(ax,(0,0),(6.5*math.cos(math.radians(-150)),6.5*math.sin(math.radians(-150))),'R6.5',off=(-3.5,-2.2),color=CUT)
    leader(ax,(11,-3),(37,-12),'C1: sector window ×4\n60° wide, centred on the\nflap axes (0/90/180/270°)\nthrough the 2.0 mm plate',color=CUT)
    leader(ax,(22,10),(37,14),'hinge lugs + flap stops (grey):\nDO NOT lighten — highest stress\nin the whole assembly',color=INK)
    leader(ax,(13,13),(37,30),'bearing cross-plate above\n(blue dashed) — unchanged',color=ADD)
    clean(ax,'BASE PLATE — plan (section Z −8.8), features above shown grey',(-36,78,-35,35))
def fig_upper(fig):
    ax=fig.add_axes([0.03,0.10,0.30,0.76]); b,rem=diff_view(ax,L['upper'],P['upper'],(0,0,71.2),Z,(1,0,0),(0,1,0))
    rb=sec_polys(L['upper'],(0,0,73.5),Z,(1,0,0),(0,1,0))
    for q in geoms(rb):
        ax.plot(*q.exterior.xy,color=MUTE,lw=0.6,zorder=5)
        for h in q.interiors: ax.plot(*h.xy,color=MUTE,lw=0.6,zorder=5)
    sv=sec_polys(L['upper'],(0,0,57.0),Z,(1,0,0),(0,1,0))
    for q in geoms(sv): ax.plot(*q.exterior.xy,color=ADD,lw=0.8,ls='--',zorder=6)
    for c in [(8,9),(-10,-12)]: ax.plot(*c,'+',color=CUT,ms=8,zorder=7)
    leader(ax,(8,9),(20,38),'U1: Ø14 hole at (8, 9)',color=CUT,ha='center'); leader(ax,(-10,-12),(-12,-39),'U1: Ø14 hole at (−10, −12)',color=CUT,ha='center')
    leader(ax,(14,-14),(34,-37),'servo mount tabs below floor\n(blue dashed): keep floor solid here',color=ADD,ha='center')
    clean(ax,'FLOOR — plan (section Z 71.2), ribs above in grey',(-36,46,-43,42))
    ax=fig.add_axes([0.36,0.10,0.30,0.76]); b,rem=diff_view(ax,L['upper'],P['upper'],(0,0,80.0),Z,(1,0,0),(0,1,0),min_area=0.05)
    for a in (45,135,-69,-111): ax.plot([0,34*math.cos(math.radians(a))],[0,34*math.sin(math.radians(a))],'-.',color=MUTE,lw=0.5)
    ax.text(0,0,'U2: wall 2.06 → 1.56\n(0.5 off the inside, Z 73.2 → top)\nexcept ±16° about each\nscrew axis',ha='center',va='center',fontsize=8.5,color=CUT)
    clean(ax,'WALL — section Z = 80',(-36,36,-43,42))
def fig_cap(fig):
    ax=fig.add_axes([0.03,0.45,0.60,0.30]); u,n=radial(20)
    b,rem=diff_view(ax,L['cap'],P['cap'],(0,0,0),n,u,Z)
    dim(ax,(26.5,88.74),(26.5,89.94),'1.2',off=(2.2,0),color=CUT); dim(ax,(0,87.2),(23.5,87.2),'R23.5',off=(0,-0.8),color=CUT)
    leader(ax,(-8,88.3),(-8,84),'K1: recess underside 0.8 deep inside R23.5 (disc 2.0 → 1.2); clips and rim untouched',color=CUT,ha='center')
    clean(ax,'SECTION through cap centre',(-32,34,82,91.5))
FIGS=dict(flap=fig_flap,lower=fig_lower,cage=fig_cage,upper=fig_upper,cap=fig_cap)

# ------------------------------------------------------------------ PDF assembly
from PIL import Image
DOC2='V5 air-brake assembly (asm-v5-acc.stl, all parts except the rotor) — proposed weight-reduction cuts'
NS2=8; RHO=1.24e-3
def J(n): return json.load(open(f'pres_{n}.json'))
NICE={'aero_deployed_20N':'Deployed, 20 N air load','side_5N_top':'5 N sideways at flap tip','latched_pull_10N':'Latched, 10 N pulling outward',
 'axial_200N_aft_rim':'200 N axial on small-end rim','lateral_50N_aft_rim':'50 N sideways on small-end rim','axial_200N_coupler':'200 N axial on coupler lip','lateral_50N_coupler':'50 N sideways on coupler lip',
 'hinge_4flaps_22N':'4 flaps, 22 N into each hinge','bearing_lateral_20N':'20 N sideways at rotor bearing','stop_block_torque':'Servo stall on rotation stop (9 N)','stack_axial_200N':'200 N stack compression via posts',
 'axial_200N_skirt':'200 N axial on skirt','floor_inertia_15N':'15 N on floor (electronics × 20 g)','servo_mount_10N':'10 N on servo mount tabs','pressure_20N':'20 N on cap face'}
def cmp_table(ax,base,prop,extra=None,fs=8.3):
    b=J(base); p=J(prop); rows=[['Load case','Peak utilisation\nbefore → after','Max deflection\nbefore → after']]
    for lc in b['lc']:
        rows.append([NICE.get(lc,lc),'%.0f %% → %.0f %%'%(100*b['lc'][lc]['util_max'],100*p['lc'][lc]['util_max']),'%.3f → %.3f mm'%(b['lc'][lc]['umax'],p['lc'][lc]['umax'])])
    y=table(ax,rows,[0.50,0.26,0.24],rowh=[0.16]+[0.11]*(len(rows)-1),fs=fs)
    ax.text(0,y-0.04,'Solid mass %.2f g → %.2f g  (−%.2f g, −%.1f %%)'%(b['vol']*RHO,p['vol']*RHO,(b['vol']-p['vol'])*RHO,100*(1-p['vol']/b['vol']))+(extra or ''),transform=ax.transAxes,fontsize=fs+0.6,va='top',fontweight='bold',color=INK,linespacing=1.4)
    return y
def part_page(sheet,title,sub,figfn,base,prop,renders,note,extra=None):
    fig=plt.figure(figsize=PAGE); title_block(fig,DOC2,sheet,NS2,title,sub)
    figfn(fig)
    for k,(f,t) in enumerate(renders):
        a=fig.add_axes([0.71,0.635-0.275*k,0.26,0.255]); a.imshow(Image.open(f).crop((80,60,940,860))); a.axis('off'); a.set_title(t,fontsize=8.8,loc='left',color=MUTE,pad=2)
    a=fig.add_axes([0.71,0.085,0.265,0.26]); a.axis('off'); y=cmp_table(a,base,prop,extra)
    fig.text(0.03,0.085,note,fontsize=8.8,va='bottom',color=INK,linespacing=1.4)
    return fig
def page_summary():
    fig=plt.figure(figsize=PAGE); title_block(fig,DOC2,1,NS2,'Sheet 1 — Where the weight is, and what can come off','Every proposal below was built as a modified solid and re-run through the same FEA load cases as the original part.  Nothing here has been applied to your CAD yet.')
    parts=[('Lower section (tail cone + shoulder)','lower','prop_lower','L1 core out shoulder between screw bosses; L2 cone wall 2.0 → 1.5',1,'Sheet 3'),
           ('Flaps ×4','flap','prop_flap','F1 thin upper skin panels 2.5 → 1.5; F2 pocket the 4.7 mm lower zone to 2.0',4,'Sheet 4'),
           ('Cage / flap frame','cage','prop_cage','C1 four windows in the base plate.  Lugs, posts, ring: leave alone',1,'Sheet 5'),
           ('Upper bay (electronics + servo)','upper','prop_upper','U1 two Ø14 floor holes; U2 wall 2.06 → 1.56 between screw bosses',1,'Sheet 6'),
           ('Top cap','cap','prop_cap','K1 recess underside 0.8 mm (disc 2.0 → 1.2)',1,'Sheet 7')]
    rows=[['Part','Solid mass now','Proposed cut','Saving','Peak utilisation\nbefore → after','Detail']]; tot=0; sav=0
    for nm,b,p,desc,q,sh in parts:
        jb=J(b); jp=J(p); m0=jb['vol']*RHO*q; m1=jp['vol']*RHO*q; tot+=m0; sav+=m0-m1
        rows.append([nm,'%.1f g'%m0,desc,'−%.1f g (%.0f %%)'%(m0-m1,100*(1-m1/m0)),'%.0f %% → %.0f %%'%(100*jb['env_max'],100*jp['env_max']),sh])
    jr=json.load(open('res_BASE.json')); jrr=json.load(open('res_REC.json')); m0=jr['vol']*RHO; m1=jrr['vol']*RHO; tot+=m0; sav+=m0-m1
    rows.append(['Rotor (inner green piece)','%.1f g'%m0,'Lobe pockets, block wings + undersides, tab gusset (separate document)','−%.1f g (%.0f %%)'%(m0-m1,100*(1-m1/m0)),'see rotor doc','rotor doc'])
    skin=8960*RHO; tot+=skin; rows.append(['Outer skin tube (0.52 mm wall)','%.1f g'%skin,'None — already minimum; it carries the loads between modules','—','not analysed','—'])
    rows.append(['TOTAL printed parts','%.1f g'%tot,'','−%.1f g (%.0f %%)'%(sav,100*sav/tot),'',''])
    jl=J('prop_lowerL3'); extra=(J('prop_lower')['vol']-jl['vol'])*RHO
    ax=fig.add_axes([0.03,0.42,0.94,0.47]); cols=[None]*(len(rows)-1)+[[INK,INK,None,OKC,None,None]]
    y=table(ax,rows,[0.20,0.09,0.42,0.11,0.11,0.07],rowh=[0.12]+[0.105]*(len(rows)-1),fs=8.8,colors=cols)
    ax=fig.add_axes([0.03,0.09,0.94,0.31]); ax.axis('off')
    ax.text(0,1,f'''HOW TO READ THIS
• "Utilisation" = peak stress ÷ allowable under the reference loads on Sheet 2 (35 MPa in-plane, 15 MPa across layers for PLA).  100 % = at the limit; we kept every proposal under about 60 %.
• Masses are 100 % solid PLA (1.24 g/cm³).  Printed parts with sparse infill weigh less, and the saving shrinks in proportion — wall-thickness cuts (L2, F1, U2, K1) keep their full value because walls print solid.
• The biggest single item is the lower section: its shoulder ring is 6.2 mm thick and works at about 7 % of its strength.  An optional further step (L3, Sheet 3) opens its bore from Ø52 to Ø54.4 for another −{extra:.1f} g,
  but only if nothing locates on that Ø52 bore — we could not tell from the STL.
• The cage is the opposite case: its hinge lugs and posts are the hardest-working features in the assembly (≈ 50–56 % utilisation), so only a token cut is proposed there.
• Battery / electronics / servo blocks, screws, nuts and pins in the STL are bought parts and were not considered.

NEXT STEP
Tell us which proposals you want (by code: L1, L2, L3, F1, F2, C1, U1, U2, K1) and correct any wrong assumption on Sheet 2; we will then cut the STLs.  Preview STLs of every proposal are in v5/assembly/preview_stl/.''',transform=ax.transAxes,fontsize=9.2,va='top',linespacing=1.5)
    return fig
def page_setup():
    fig=plt.figure(figsize=PAGE); title_block(fig,DOC2,2,NS2,'Sheet 2 — Assumptions, supports and reference loads','These are engineering estimates.  Stress scales linearly with load, so if your real load is twice ours, double the utilisation.')
    ax=fig.add_axes([0.03,0.09,0.50,0.80]); ax.axis('off')
    ax.text(0,1,'''WHAT WAS IDENTIFIED IN asm-v5-acc.stl (52 bodies)
• Printed structure: lower section, cage, upper bay, cap, 4 flaps, rotor, thin outer skin.
• Hardware: 12 radial M3-size screws + nuts (three rings of four: Z −26.6, +13.5, +83.5), 4 hinge pins,
  a 9 g-class micro servo with horn, 3 rectangular blocks (battery / electronics).
• Mechanism: the servo turns the rotor; cam lobes push a pad on each flap outward about a hinge pin at the bottom
  of the cage; tabs on the rotor hook each flap shut when stowed; a key on the rotor shaft hits a stop block on
  the cage to limit rotation.

METHOD
• Same solver as the rotor study: linear-elastic FEA, quadratic tetrahedra (28 000–96 000 elements per part),
  PLA E = 2.3 GPa, ν = 0.35.  Allowables 35 MPa (von Mises, in-plane) and 15 MPa (tension across layers).
  Axisymmetric parts assumed printed with the rocket axis vertical; the flap was checked against the weaker
  15 MPa value in every direction because its print orientation is unknown.
• Peak values ignore elements within 1 mm of load patches and supports.
• A region is a candidate for cutting when it stays below ~5 % utilisation in every load case AND is not a mating,
  sealing, aerodynamic or fastener surface.  Each proposal was then modelled and re-solved.

WHAT WE COULD NOT KNOW
• Flight speed, motor thrust, recovery shock, and how axial load actually passes between modules (through the
  skin screws, or by the parts stacking on each other) — both paths were loaded.
• Whether internal faces (lower-section bore Ø52, upper-bay floor, cap underside, cage base plate) seal against
  ejection gas, locate another part or carry wiring.  Each sheet flags the faces to confirm.
• Buckling and impact (landing) were not analysed; wall-thinning proposals were kept ≥ 1.5 mm for that reason.''',transform=ax.transAxes,fontsize=9.1,va='top',linespacing=1.48)
    ax=fig.add_axes([0.55,0.12,0.42,0.77])
    rows=[['Part','Held at','Reference load cases'],
      ['Flap','hinge bore; cam pad (deployed) or\nlatch hook (stowed)','20 N air load on outer face (≈ full stagnation\npressure at ~105 m/s); 10 N outward while\nlatched; 5 N sideways at the tip'],
      ['Cage','4 screw bosses in the posts\n(stack case: base-plate rim)','per flap 20 N axial + 10 N radial into the hinge\nlugs; 20 N sideways at rotor bearing; 9 N on the\nrotation stop (servo stall); 200 N stack compression'],
      ['Lower section','4 screw positions in the shoulder','200 N axial and 50 N sideways, applied at the\nsmall-end rim and at the coupler lip'],
      ['Upper bay','4 screw bosses in the wall','200 N axial on the skirt; 15 N on the floor\n(≈ 75 g of electronics at 20 g); 10 N on the\nservo mount tabs (stall torque reaction)'],
      ['Cap','its 4 clip tabs','20 N spread over the face']]
    table(ax,rows,[0.17,0.33,0.50],rowh=[0.07,0.15,0.18,0.12,0.15,0.08],fs=8.6)
    return fig
def page_dont():
    fig=plt.figure(figsize=PAGE); title_block(fig,DOC2,8,NS2,'Sheet 8 — What NOT to cut, and open questions','')
    ax=fig.add_axes([0.03,0.10,0.52,0.80]); ax.axis('off')
    ax.text(0,1,'''LEAVE THESE ALONE (highest stress in the assembly at the reference loads)
• Cage hinge lugs and the plate around them — 56 % utilisation with 22 N per flap; the peak is at the lug-to-plate
  corner.  If anything, add a R1.5 fillet there.  This, not the rotor, is the next place we would expect a crack.
• Cage posts and top ring — 51 % under 200 N stack compression (the posts bend because the screws sit off-centre).
• Flap hinge knuckle and the web between knuckle and cam pad — the flap's whole load path.
• Flap tail below the hinge — it sits 0.4 mm above the cage plate and looks like the open/closed stop.
• Rotor tabs — see the rotor document; they are the weakest feature in the mechanism.
• Outer skin — 0.52 mm, nothing to give.
• All outer (aerodynamic) surfaces — every proposal removes material from the inside only.

OPEN QUESTIONS THAT CHANGE THE ANSWER
1. Lower section: does anything fit inside the Ø52 bore or against the internal ledge at Z −38.5 (motor tube, retainer,
   coupler)?  If not, L3 is the largest single saving available.
2. Does the cage base plate or the upper-bay floor need to be gas-tight (ejection charge) or keep debris out of the
   mechanism?  If yes, drop C1 and U1, or replace the through-holes by 1.2 mm-deep pockets.
3. Are the three blocks in the upper bay glued/taped to the floor?  U1 puts holes under two of them.
4. What is the real maximum deploy speed?  All utilisation numbers scale with (speed / 105 m/s)².
5. Print material for the flaps and print orientation — the flap check used the weak-direction strength throughout.

FURTHER SAVINGS WE DID NOT MODEL (bigger design changes)
• Flap skin to 1.2 mm with two extra vertical ribs (≈ −1.5 g more per flap).
• Lower section printed as a 1.2 mm shell with internal ribs instead of a solid 6.2 mm shoulder.
• Replace the 2 mm cap by a 0.8 mm disc with a rim bead if it only keeps dust out.''',transform=ax.transAxes,fontsize=9.2,va='top',linespacing=1.5)
    for k,(f,t,y) in enumerate([('fig/util_cage_iso.png','Cage utilisation — the hard-working part',0.50),('fig/util_lower_iso.png','Lower section utilisation — nearly idle',0.10)]):
        a=fig.add_axes([0.58,y,0.38,0.38]); a.imshow(Image.open(f).crop((80,40,1000,860))); a.axis('off'); a.set_title(t,fontsize=9.5,loc='left')
    return fig
def build(path):
    from matplotlib.backends.backend_pdf import PdfPages
    jl=J('prop_lowerL3'); jb=J('lower')
    pages=[page_summary(),page_setup(),
      part_page(3,'Sheet 3 — Lower section: L1 shoulder core-out, L2 cone wall, L3 optional bore','Heaviest printed part (41 g solid) and the least stressed.  Red hatch = proposed removal; orange = optional.',fig_lower,'lower','prop_lower',
        [('fig/prop_lower_below.png','Proposal seen from the small end (red = removed)'),('fig/util_lower_iso.png','Original: utilisation, all load cases (scale 0–10 %)')],
        'L1: four 56° pockets, R27.6–R30.2, open to the cone interior, closed by a 1.6 mm top flange (Z −28.1 → −26.5).  Leaves 1.6 mm inner and 2.0 mm outer walls.\nL2: offset the cone inner surface 0.5 mm outward from Z −39.7 to the small end.  Outer surface, coupler OD, screw holes and nut slots unchanged.',
        extra='\nWith optional L3: %.2f g (−%.1f %%), peak utilisation %.0f %%'%(jl['vol']*RHO,100*(1-jl['vol']/jb['vol']),100*jl['env_max'])),
      part_page(4,'Sheet 4 — Flaps (×4): F1 upper skin panels, F2 lower-zone pockets','All removal is on the inside face; the outer aerodynamic surface, side rails, hinge, cam pad, hook and centre web are untouched.',fig_flap,'flap','prop_flap',
        [('fig/prop_flap_in.png','Proposal, inside face (red = removed)'),('fig/util_flap_in.png','Original: utilisation, all load cases (scale 0–10 %)')],
        'F1: two pockets 6.7 × 29.0 (y ±3.8…±10.5, Z 22–51), floor concentric with the outer face at R30.7 → 1.5 mm skin.   F2: two pockets 8.5 × 7.5 (y ±2.0…±10.5, Z 11.5–19), floor at R30.2 → 2.0 mm skin.\nSaving shown in the table is per flap; ×4 for the set.  Z is measured in the assembly STL (hinge pin axis at Z 0.19).'),
      part_page(5,'Sheet 5 — Cage: C1 base-plate windows only','The cage is the most highly stressed printed part.  Only the centre of the base plate, under the rotor wheel, is idle.',fig_cage,'cage','prop_cage',
        [('fig/prop_cage_below.png','Proposal from below (red = removed)'),('fig/util_cage_below.png','Original: utilisation from below (scale 0–10 %)')],
        'C1: four 60° sector windows R6.5–R15.0 through the 2.0 mm plate, centred on the flap axes, leaving a Ø13 hub ring and four 30° spokes under the bearing cross-plate arms.\nCosts about 25 % more deflection at the hinges (0.25 → 0.32 mm at 22 N per flap); stress is unchanged.  Skip C1 if the plate must stay closed.'),
      part_page(6,'Sheet 6 — Upper bay: U1 floor holes, U2 wall relief','Lightly loaded, but it carries the servo and the electronics, so the cuts stay away from the servo mount and the screw bosses.',fig_upper,'upper','prop_upper',
        [('fig/prop_upper_top.png','Proposal from above (red = removed)'),('fig/util_upper_below.png','Original: utilisation from below (scale 0–10 %)')],
        'U1: two Ø14 through-holes in the 2.0 mm floor at (8, 9) and (−10, −12) (assembly XY, rocket axis at origin), clear of the servo-mount band and the partition ribs.\nU2: remove 0.5 mm from the inside of the wall above the floor (Z 73.2 → 89.9), leaving full thickness for ±16° around each of the four screw axes (45°, 135°, −69°, −111°).'),
      part_page(7,'Sheet 7 — Top cap: K1 underside recess','A 2 mm lid carrying almost nothing.',fig_cap,'cap','prop_cap',
        [('fig/prop_cap_below.png','Proposal from below (red = removed)'),('fig/util_cap_below.png','Original: utilisation from below (scale 0–10 %)')],
        'K1: recess the underside 0.8 mm deep inside R23.5, leaving a 1.2 mm disc and the full 2.0 mm rim where the four clip tabs attach.  Top face unchanged.'),
      page_dont()]
    with PdfPages(path) as pdf:
        for f in pages: pdf.savefig(f,dpi=150); plt.close(f)
if __name__=='__main__' and len(__import__('sys').argv)>1: build(__import__('sys').argv[1])
