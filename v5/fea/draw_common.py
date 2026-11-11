import numpy as np, trimesh, shapely
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MPoly, Rectangle, FancyArrowPatch, Circle
from shapely.geometry import Polygon, Point, box
INK='#1a1a1a'; CUT='#d62828'; ADD='#1c7ed6'; MUTE='#6b7280'; KEEP='#e9ecef'; WARN='#e8590c'; OKC='#2b8a3e'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'axes.linewidth':0.6,'pdf.fonttype':42})
PAGE=(16.54,11.69)   # A3 landscape, inches
def zsection(m,z):
    s=m.section(plane_origin=(0,0,z),plane_normal=(0,0,1)); p,T=s.to_2D()
    return [shapely.affinity.affine_transform(q,[T[0,0],T[0,1],T[1,0],T[1,1],T[0,3],T[1,3]]) for q in p.polygons_full]
def plane_section(m,origin,normal,u,v):
    """section polylines projected on (u,v) axes"""
    s=m.section(plane_origin=origin,plane_normal=normal)
    if s is None: return []
    u=np.asarray(u,float); v=np.asarray(v,float); o=np.asarray(origin,float)
    return [np.c_[(np.array(e)-o)@u,(np.array(e)-o)@v] for e in s.discrete]
def draw_poly(ax,q,fc=KEEP,ec=INK,lw=0.9,hatch=None,alpha=1,z=2,mirror=False):
    sx=-1 if mirror else 1
    def ring(c): c=np.array(c); return np.c_[sx*c[:,0],c[:,1]]
    from matplotlib.path import Path; from matplotlib.patches import PathPatch
    verts=[];codes=[]
    for r in [q.exterior]+list(q.interiors):
        c=ring(r.coords); verts+=list(c); codes+=[Path.MOVETO]+[Path.LINETO]*(len(c)-2)+[Path.CLOSEPOLY]
    ax.add_patch(PathPatch(Path(verts,codes),fc=fc,ec=ec,lw=lw,hatch=hatch,alpha=alpha,zorder=z))
def dim(ax,p0,p1,text,off=(0,0),color=INK,fs=8.5,ha='center',va='center',lw=0.7):
    ax.annotate('',xy=p0,xytext=p1,arrowprops=dict(arrowstyle='<|-|>',color=color,lw=lw,shrinkA=0,shrinkB=0,mutation_scale=8),zorder=9)
    m=((p0[0]+p1[0])/2+off[0],(p0[1]+p1[1])/2+off[1])
    ax.text(*m,text,color=color,fontsize=fs,ha=ha,va=va,zorder=10,bbox=dict(fc='white',ec='none',pad=1.0,alpha=0.92))
def leader(ax,xy,xytext,text,color=INK,fs=8.5,ha='left',va='center'):
    ax.annotate(text,xy=xy,xytext=xytext,fontsize=fs,color=color,ha=ha,va=va,zorder=10,
                arrowprops=dict(arrowstyle='-|>',color=color,lw=0.7,shrinkA=2,shrinkB=0,mutation_scale=8),bbox=dict(fc='white',ec='none',pad=1.2,alpha=0.92))
def clean(ax,title=None,lim=None):
    ax.set_aspect('equal'); ax.set_xticks([]); ax.set_yticks([])
    for s in ax.spines.values(): s.set_visible(False)
    if title: ax.set_title(title,fontsize=10.5,fontweight='bold',loc='left',color=INK,pad=6)
    if lim: ax.set_xlim(lim[0],lim[1]); ax.set_ylim(lim[2],lim[3])
def title_block(fig,doc,sheet,n,title,sub=''):
    fig.patches.append(Rectangle((0.02,0.02),0.96,0.96,transform=fig.transFigure,fill=False,ec=INK,lw=1.0))
    fig.patches.append(Rectangle((0.02,0.02),0.96,0.052,transform=fig.transFigure,fill=False,ec=INK,lw=1.0))
    fig.text(0.03,0.046,doc,fontsize=10.5,fontweight='bold',va='center',color=INK)
    fig.text(0.62,0.046,'Units: mm  |  PLA (FDM) basis  |  2026-11-11',fontsize=8,va='center',color=MUTE)
    fig.text(0.97,0.046,f'Sheet {sheet} / {n}',fontsize=10,va='center',ha='right',color=INK)
    fig.text(0.03,0.955,title,fontsize=15,fontweight='bold',va='top',color=INK)
    if sub: fig.text(0.03,0.925,sub,fontsize=9.5,va='top',color=MUTE)
def table(ax,rows,colw,header=True,fs=8.5,rowh=None,colors=None,x0=0.0,y0=1.0):
    """simple text table in axes coords; rows: list of lists of str; returns bottom y"""
    ax.axis('off'); n=len(rows); rowh=rowh or [0.07]*n; y=y0
    xs=np.concatenate([[x0],x0+np.cumsum(colw)])
    for i,r in enumerate(rows):
        h=rowh[i]
        if header and i==0: ax.add_patch(Rectangle((xs[0],y-h),xs[-1]-xs[0],h,transform=ax.transAxes,fc='#343a40',ec='none'))
        elif i%2==0: ax.add_patch(Rectangle((xs[0],y-h),xs[-1]-xs[0],h,transform=ax.transAxes,fc='#f5f6f7',ec='none'))
        for j,c in enumerate(r):
            col='white' if (header and i==0) else (colors[i][j] if colors and colors[i] and colors[i][j] else INK)
            ax.text(xs[j]+0.006,y-h/2,c,transform=ax.transAxes,fontsize=fs,va='center',ha='left',color=col,fontweight='bold' if (header and i==0) or (colors and colors[i] and colors[i][j]) else 'normal',linespacing=1.25)
        ax.plot([xs[0],xs[-1]],[y-h,y-h],transform=ax.transAxes,color='#ced4da',lw=0.5); y-=h
    return y
