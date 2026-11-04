"""Linear-elastic FEA of one V5 fin in the open pose (fin 1, 90 deg), on a voxel hex mesh (scikit-fem).

Load case: the relative airflow hits the upstream (upward-facing) face of the open fin and pushes it past 90 deg, i.e. INTO its stop.
  F is spread uniformly over the upstream face outboard of the tube (x > 34).
Supports (rigid pin and stop): nodes within 2.2 mm of the hinge axis (x=25, z=0) fixed in x and z; nodes on the stop contact patch fixed in z.
Material: printed PLA, E 3000 MPa, nu 0.35 (isotropic; real prints are weaker across layers). Voxel stair-steps over-state peak stress at corners,
so compare variants with the same pitch, and read the 99th percentile as well as the max.

Usage: python3 fea_fin.py [tag]        (tag = fin_v5b default; needs $AIRBRAKE_WORK/<tag>.pkl)
"""
import os, sys, pickle, numpy as np, trimesh
import scipy.sparse as sp
import skfem
from skfem import Basis, ElementVector, ElementHex1, MeshHex, asm, solve, condense
from skfem.models.elasticity import linear_elasticity, lame_parameters

W = os.environ.get('AIRBRAKE_WORK', '.')


def load_fin(tag='fin_v5b'):
    parts = pickle.load(open(f'{W}/{tag}.pkl', 'rb'))
    d = {n: m for _, (n, m) in parts.items()}
    pick = lambda p: [m for n, m in d.items() if n.startswith(p)][0]
    return pick('P1 '), pick('C ')


def run(fin, housing, F=12.0, load='face', keeper=False, pitch=0.8, E=3000.0, nu=0.35, verbose=True, label=''):
    vox = fin.voxelized(pitch).fill()
    occ = vox.matrix.astype(bool)
    T = vox.transform                      # index -> centre of voxel
    idx = np.argwhere(occ)
    off = np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0], [1, 1, 0], [0, 0, 1], [1, 0, 1], [0, 1, 1], [1, 1, 1]])
    corners = idx[:, None, :] + off[None, :, :]                 # (nel, 8, 3) node grid indices
    flat = corners.reshape(-1, 3)
    uniq, inv = np.unique(flat, axis=0, return_inverse=True)
    t = inv.reshape(-1, 8).T                                    # (8, nel)
    p = (uniq - 0.5) * pitch @ np.eye(3) + T[:3, 3]             # node coordinates (voxel centres sit at integer indices)
    p = (uniq @ T[:3, :3].T) + T[:3, 3] - 0.5 * pitch           # lower corner of the voxel at that index
    mesh = MeshHex(p.T.copy(), t)
    basis = Basis(mesh, ElementVector(ElementHex1()))
    lam, mu = lame_parameters(E, nu)
    K = asm(linear_elasticity(lam, mu), basis)
    nn = p.shape[0]
    nd = basis.nodal_dofs                                       # (3, nn)
    # --- supports
    X, Y, Z = p[:, 0], p[:, 1], p[:, 2]
    r_pin = np.hypot(X - 25.0, Z - 0.0)
    pin = np.where(r_pin < 2.2)[0]
    qd = trimesh.proximity.closest_point(housing, p)[1]
    contact = np.where((qd < 0.6) & (X > 26.5) & (Z < -4.5) & (r_pin > 3.5))[0]
    keep_nodes = np.where((qd < 0.7) & (X < 24.0) & (Z > 1.0) & (np.abs(Y) < 6.5))[0] if keeper else np.array([], int)
    contact = np.concatenate([contact, keep_nodes]) if keeper else contact
    fixed = np.concatenate([nd[0, pin], nd[2, pin], nd[2, contact], [nd[1, pin[0]]]])
    # --- load: upstream (upward-facing, +z) surface nodes outboard of x = 34
    top_vox = occ.copy()
    top_vox[:, :, :-1] &= ~occ[:, :, 1:]                        # voxels whose +z neighbour is empty
    top_vox[:, :, -1] = occ[:, :, -1]
    tidx = np.argwhere(top_vox)
    cen = tidx @ T[:3, :3].T + T[:3, 3]
    tidx = tidx[cen[:, 0] > (34.0 if load == 'face' else float(fin.bounds[1][0]) - 8.0)]
    topnodes = np.unique(((tidx[:, None, :] + off[None, 4:, :]).reshape(-1, 3)), axis=0)
    # map grid index -> node number
    lookup = {tuple(g): i for i, g in enumerate(uniq)}
    tn = np.array([lookup[tuple(g)] for g in topnodes if tuple(g) in lookup])
    f = np.zeros(basis.N)
    f[nd[2, tn]] = -F / len(tn)
    D = np.unique(fixed)
    Kc, fc, xc, I = condense(K, f, D=D)
    import pyamg
    Kc = Kc.tocsr()
    # near-null space: rigid-body modes are removed by the supports, so a plain smoothed-aggregation hierarchy is enough
    ml = pyamg.smoothed_aggregation_solver(Kc, max_coarse=2000)
    res_hist = []
    uI = ml.solve(fc, tol=1e-7, maxiter=300, accel='cg', residuals=res_hist)
    u = np.zeros(basis.N); u[I] = uI
    U = u[nd]                                                   # (3, nn)
    react = K @ u - f                                           # nodal reaction forces (N)
    Rz_pin = float(react[nd[2, pin]].sum()); Rx_pin = float(react[nd[0, pin]].sum())
    stop_nodes = np.setdiff1d(contact, keep_nodes)
    Rz_stop = float(react[nd[2, stop_nodes]].sum()) if len(stop_nodes) else 0.0
    Rz_keep = float(react[nd[2, keep_nodes]].sum()) if len(keep_nodes) else 0.0
    disp = np.linalg.norm(U, axis=0)
    # --- stress at element centres
    g = basis.interpolate(u).grad                               # (3,3,nel,nqp)
    eps = 0.5 * (g + g.transpose(1, 0, 2, 3))
    tr = eps[0, 0] + eps[1, 1] + eps[2, 2]
    sig = 2 * mu * eps
    for i in range(3): sig[i, i] += lam * tr
    sxx, syy, szz, sxy, syz, szx = sig[0, 0], sig[1, 1], sig[2, 2], sig[0, 1], sig[1, 2], sig[2, 0]
    vm = np.sqrt(0.5 * ((sxx - syy) ** 2 + (syy - szz) ** 2 + (szz - sxx) ** 2) + 3 * (sxy ** 2 + syz ** 2 + szx ** 2)).mean(axis=1)
    elc = p[t].mean(axis=0)                                     # element centroids (nel, 3)
    # exclude elements touching a support node (contact singularities)
    near_sup = np.zeros(len(vm), bool)
    supn = np.unique(np.concatenate([pin, contact]))
    msk = np.zeros(nn, bool); msk[supn] = True
    near_sup = msk[t].any(axis=0)
    free = ~near_sup
    order = np.argsort(-vm * free)[:400]
    spots = []
    for i in order:
        c = elc[i]
        if all(np.linalg.norm(c - q) > 6 for q, _ in spots): spots.append((c, vm[i]))
        if len(spots) >= 4: break
    res = dict(label=label, F=F, load=load, Rz_pin=Rz_pin, Rx_pin=Rx_pin, Rz_stop=Rz_stop, Rz_keep=Rz_keep, spots=[(q.round(1).tolist(), round(float(v), 1)) for q, v in spots], nel=mesh.t.shape[1], dofs=basis.N, tip_mm=float(np.abs(U[2]).max()),
               vm_max=float(vm[free].max()), vm_p99=float(np.percentile(vm[free], 99)), vm_max_all=float(vm.max()),
               at=elc[free][np.argmax(vm[free])].round(1).tolist(), pin=len(pin), contact=len(contact), loaded=len(tn),
               volume=float(basis.dx.sum()))
    if verbose:
        print(f'{label} [{load}{"+keeper" if keeper else ""}]: F={F} N  tip deflection {res["tip_mm"]:.2f} mm  von Mises max {res["vm_max"]:.1f} MPa  p99 {res["vm_p99"]:.1f} MPa'
              f'  reactions [N]: pin z {Rz_pin:.0f} x {Rx_pin:.0f}, stop {Rz_stop:.0f}, keeper {Rz_keep:.0f}'
              f'  (at x,y,z = {res["at"]})  [elements {res["nel"]}, supports pin {res["pin"]} contact {res["contact"]}, loaded nodes {res["loaded"]}]')
    return res, (p, t, vm, U)


if __name__ == '__main__':
    tag = sys.argv[1] if len(sys.argv) > 1 else 'fin_v5b'
    fin, hous = load_fin(tag)
    kp = [False, True] if (len(sys.argv) > 2 and sys.argv[2] == 'keeper') else [False]
    for k in kp:
        for F, ld in ((12.0, 'face'), (30.0, 'face'), (15.0, 'tip')):
            r, _ = run(fin, hous, F=F, load=ld, keeper=k, label=tag)
            print('    hot spots (x,y,z mm : MPa):', r['spots'])
