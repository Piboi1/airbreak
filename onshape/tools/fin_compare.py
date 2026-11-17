"""Stress check of the stripped-fin variants (fin_variants.py) with the same FEA as fea_fin.py (open pose, pin + stop supports,
12 N / 30 N air load on the face, 15 N on the tip). A carbon rod (variant J) is modelled as stiffer elements (E 100 GPa)."""
import sys, pickle, json, time, numpy as np, trimesh
sys.path.insert(0, '.')
import fea_fin, fin_variants as fv
from skfem import Basis, ElementVector, ElementHex1, asm
from skfem.models.elasticity import linear_elasticity, lame_parameters
W = '/tmp/claude-0/-home-user-airbreak/2a03b965-bd6f-5144-bd29-b03796006798/scratchpad/work'
hous = [m for _, (n, m) in pickle.load(open(W + '/fin_v5b.pkl', 'rb')).items() if n.startswith('C ')][0]

_orig_asm = fea_fin.asm
ROD = {'mesh': None}
def asm_with_rod(form, basis, *a, **k):        # wraps the stiffness assembly in fea_fin.run: adds (E_rod - E_pla) on rod elements
    K = _orig_asm(form, basis, *a, **k)
    if ROD['mesh'] is not None and not a and not k:
        mesh = basis.mesh; elc = mesh.p[:, mesh.t].mean(axis=1).T
        inside = np.where(ROD['mesh'].contains(elc))[0]
        if len(inside):
            lam, mu = lame_parameters(100000.0 - 3000.0, 0.3)
            K = K + _orig_asm(linear_elasticity(lam, mu), Basis(mesh, ElementVector(ElementHex1()), elements=inside))
            print('   rod elements', len(inside))
    return K
fea_fin.asm = asm_with_rod

out = []
for name, kw in [(n, k) for n, k in fv.VARIANTS.items() if (len(sys.argv) < 2 or n.startswith(sys.argv[1]))]:
    t0 = time.time()
    fin, rod = fv.build(**kw)
    vol = fin.volume
    geo = fin if rod is None else fv.U([fin, rod])
    geo = geo.copy(); geo.apply_transform(fv.OPEN)
    if rod is not None: rod = rod.copy(); rod.apply_transform(fv.OPEN)
    ROD['mesh'] = rod
    row = dict(name=name, vol=round(vol), g=round(vol * 1.24e-3, 2), rod_g=round(rod.volume * 1.6e-3, 2) if rod is not None else 0)
    for F, ld in ((12.0, 'face'), (30.0, 'face'), (15.0, 'tip')):
        r, _ = fea_fin.run(geo, hous, F=F, load=ld, label=name, verbose=False)
        row[f'{ld}{int(F)}'] = dict(vm_max=round(r['vm_max'], 1), p99=round(r['vm_p99'], 1), tip=round(r['tip_mm'], 2), at=r['at'])
    out.append(row); print(json.dumps(row), round(time.time() - t0), 's', flush=True)
json.dump(out, open(W + '/fin_compare%s.json' % ('_' + sys.argv[1][0] if len(sys.argv) > 1 else ''), 'w'), indent=1)
