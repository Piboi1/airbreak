"""Areas of one V5 fin from the exported meshes (no Onshape needed).
  python3 fin_area.py                          # uses exports/v5/print/P_fin_x4.stl (lying flat) and the open-fin mesh from $AIRBRAKE_WORK/fin_v5b.pkl if present
  python3 fin_area.py some_fin.stl             # any fin STL
Prints: total surface area, footprint (projection on the bed), and for the OPEN pose the planform the airflow sees and the part beyond the tube (x > 33)."""
import os, sys, pickle, numpy as np, trimesh
from shapely.geometry import Polygon, box
from shapely.ops import unary_union

def projected(m, axis):
    idx = [i for i in range(3) if i != axis]
    keep = np.abs(m.face_normals[:, axis]) > 1e-6
    polys = [Polygon(t[:, idx]).buffer(0.001) for t in m.triangles[keep] if Polygon(t[:, idx]).area > 1e-9]
    return unary_union(polys)

here = os.path.dirname(os.path.abspath(__file__))
stl = sys.argv[1] if len(sys.argv) > 1 else os.path.join(here, '..', 'exports', 'v5', 'print', 'P_fin_x4.stl')
fin = trimesh.load(stl)
print(f'{os.path.basename(stl)}: total surface area {fin.area:.0f} mm2 ({fin.area/100:.1f} cm2), volume {fin.volume:.0f} mm3, extents {np.round(fin.extents,1).tolist()} mm')
print(f'footprint on the bed (projection on z): {projected(fin, 2).area:.0f} mm2')
pk = os.path.join(os.environ.get('AIRBRAKE_WORK', '.'), 'fin_v5b.pkl')
if os.path.exists(pk):
    parts = pickle.load(open(pk, 'rb'))
    op = [m for _, (n, m) in parts.items() if n.startswith('P1 ')][0]
    g = projected(op, 2)
    print(f'open fin (90 deg), planform seen by the airflow: {g.area:.0f} mm2 ({g.area/100:.1f} cm2); beyond the tube (x > 33 mm): {g.intersection(box(33, -100, 200, 100)).area:.0f} mm2')
