"""Linear-elastic tet FEA (quadratic tets) on scikit-fem. Units: mm, N, MPa."""
import numpy as np, time
from skfem import MeshTet, ElementVector, ElementTetP2, ElementTetP1, Basis, FacetBasis, LinearForm, asm, condense, solve
from skfem.models.elasticity import linear_elasticity, lame_parameters
from skfem.helpers import dot
import pypardiso, scipy.sparse as sp

class Model:
    def __init__(self,p,t,E=2300.,nu=0.35,order=2):
        self.mesh=MeshTet(p.T.copy(),t.T.copy())
        self.E,self.nu=E,nu
        self.elem=ElementVector(ElementTetP2() if order==2 else ElementTetP1())
        self.basis=Basis(self.mesh,self.elem,intorder=2 if order==2 else 1)
        lam,mu=lame_parameters(E,nu); self.lam,self.mu=lam,mu
        self.K=asm(linear_elasticity(lam,mu),self.basis)
        self.fc=self.mesh.p[:,self.mesh.facets[:,self.mesh.boundary_facets()]].mean(axis=1)  # boundary facet centroids
        self.bf=self.mesh.boundary_facets()
        self.X=self.basis.doflocs  # 3 x ndof
        self._fac=None
    def facets_where(self,fn):
        return self.bf[fn(self.fc[0],self.fc[1],self.fc[2])]
    def set_fixed(self,sel,radial=None):
        """sel: list of (fn(x,y,z)->mask over dofs' locations, components tuple)"""
        X=self.X; comp=np.arange(X.shape[1])%3
        # dof ordering in skfem ElementVector: nodal dofs interleaved; determine component via basis.nodal_dofs / edge_dofs
        D=[]
        nd=self.basis.nodal_dofs; ed=self.basis.edge_dofs
        for fn,comps in sel:
            for arr in (nd,ed):
                if arr.size==0: continue
                loc=X[:,arr[0]]
                msk=fn(loc[0],loc[1],loc[2])
                for c in comps: D.append(arr[c][msk])
        self.D=np.unique(np.concatenate(D)); self.I=np.setdiff1d(np.arange(self.K.shape[0]),self.D)
        K=self.K
        if radial:   # journal bearing: stiff radial springs about the Z axis, free to rotate and slide axially
            r_,c_,v_=[],[],[]
            for fn,k in radial:
                for arr in (nd,ed):
                    if arr.size==0: continue
                    loc=X[:,arr[0]]; msk=fn(loc[0],loc[1],loc[2]); x,y=loc[0][msk],loc[1][msk]; rr=np.hypot(x,y); nx,ny=x/rr,y/rr
                    dx,dy=arr[0][msk],arr[1][msk]
                    r_+= [dx,dx,dy,dy]; c_+=[dx,dy,dx,dy]; v_+=[k*nx*nx,k*nx*ny,k*nx*ny,k*ny*ny]
            K=K+sp.coo_matrix((np.concatenate(v_),(np.concatenate(r_),np.concatenate(c_))),shape=K.shape).tocsr()
        self.Kii=K[self.I][:,self.I].tocsr(); self._fac=None
    def load_vec(self,loads):
        """loads: list of (facet index array, total force 3-vector) or (facets, callable traction dir(x,y,z)->3xN, total magnitude)"""
        f=np.zeros(self.K.shape[0])
        for L in loads:
            fac=L[0]
            if len(fac)==0: raise RuntimeError('empty load patch')
            fb=FacetBasis(self.mesh,self.elem,facets=fac,intorder=3)
            one=asm(LinearForm(lambda v,w: v[0]*0+1.0*(v[0]*0+1)), FacetBasis(self.mesh,ElementTetP1(),facets=fac,intorder=3)) if False else None
            # area of patch
            pts=self.mesh.p[:,self.mesh.facets[:,fac]]
            A=0.5*np.linalg.norm(np.cross((pts[:,1]-pts[:,0]).T,(pts[:,2]-pts[:,0]).T),axis=1).sum()
            if callable(L[1]):
                dirf,mag=L[1],L[2]
                # normalise so resultant magnitude scale = mag (integral of |dir| = A)
                f+=asm(LinearForm(lambda v,w: (mag/A)*sum(dirf(*w.x)[i]*v[i] for i in range(3))),fb)
            else:
                F=np.asarray(L[1],float)
                f+=asm(LinearForm(lambda v,w: (F[0]*v[0]+F[1]*v[1]+F[2]*v[2])/A),fb)
        return f
    def solve(self,f):
        if self._fac is None:
            self._fac=pypardiso.PyPardisoSolver(); self._fac.factorize(self.Kii)
        u=np.zeros(self.K.shape[0]); u[self.I]=self._fac.solve(self.Kii,f[self.I]); return u
    def stress(self,u):
        """element-mean stress tensors (nel x 6: xx,yy,zz,xy,yz,xz), von Mises, max principal"""
        g=self.basis.interpolate(u).grad  # [3][3][nel][nq]
        G=np.array([[g[i][j].mean(axis=1) for j in range(3)] for i in range(3)])  # 3x3xnel
        eps=0.5*(G+G.transpose(1,0,2)); tr=eps[0,0]+eps[1,1]+eps[2,2]
        s=2*self.mu*eps; 
        for i in range(3): s[i,i]+=self.lam*tr
        vm=np.sqrt(0.5*((s[0,0]-s[1,1])**2+(s[1,1]-s[2,2])**2+(s[2,2]-s[0,0])**2)+3*(s[0,1]**2+s[1,2]**2+s[0,2]**2))
        S=s.transpose(2,0,1); pr=np.linalg.eigvalsh(S)
        return dict(s=s,vm=vm,p1=pr[:,2],szz=s[2,2],tz=np.sqrt(s[0,2]**2+s[1,2]**2))
    def centroids(self): return self.mesh.p[:,self.mesh.t].mean(axis=1)
    def volumes(self):
        p=self.mesh.p; t=self.mesh.t
        a=p[:,t[1]]-p[:,t[0]]; b=p[:,t[2]]-p[:,t[0]]; c=p[:,t[3]]-p[:,t[0]]
        return np.abs(np.einsum('ij,ij->j',np.cross(a.T,b.T).T,c))/6
