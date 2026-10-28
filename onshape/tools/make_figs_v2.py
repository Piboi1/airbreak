import gzip, shutil, pickle, os, numpy as np
import osapi, run, scan, figures as F, diagrams as D
d = run.ids(); did, wid = d['did'], d['wid']
# STEP (gz)
tmp = str(run.S / 'v2_closed.step')
osapi.export_step(did, wid, d['ps_v2'], tmp, name='airbrake_v2_compact_closed')
with open(tmp, 'rb') as a, gzip.open('../exports/v2/airbrake_v2_compact_closed.step.gz', 'wb') as b: shutil.copyfileobj(a, b)
print('step ok')
# Onshape renders
vm = osapi.view_matrix(-40, 24)
osapi.shaded_view(did, wid, d['ps_v2'], F.OUT + 'v2_assembled.png', vm, w=900, h=1300)
osapi.shaded_view(did, wid, d['ps_v2b'], F.OUT + 'v2_open.png', vm, w=1000, h=1300)
print('renders ok')
# released-latch state for the plan figure
parts_rel = {nm: m for _, (nm, m) in scan.state(3.0, 20).items()}
pickle.dump(parts_rel, open(str(run.S / 'v2_rel.pkl'), 'wb'))
osapi.delete(f"/elements/d/{did}/w/{wid}/e/{d['ps_scan']}"); print('scan studio removed')
