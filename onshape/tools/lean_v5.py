"""Exploration build that avoids the rate-limited 'GET features' call: upload the FeatureScript, build V5-A and V5-B in NEW scratch studios,
cache their meshes as fin_v5 / fin_v5b (and optionally a tag), delete the scratch studios. The real V5-A / V5-B elements are not touched."""
import sys, shutil, subprocess, pickle
sys.path.insert(0, '.')
import run, osapi, geom
W = run.S
tag = sys.argv[1] if len(sys.argv) > 1 else None
subprocess.check_call([sys.executable, 'build_fs.py'])
run.upload_fs('../fs/airbrake_v1_v2.fs')
d = run.ids()
for key, p, name in (('tmp_a', run.params(mode=5, compact=True), 'A'), ('tmp_b', run.params(mode=5, compact=True, opening=90, release=65, button=4.5), 'B')):
    eid = osapi.new_element(d['did'], d['wid'], 'partstudio', 'SCRATCH v5 ' + name)
    mv = osapi.current_microversion(d['did'], d['wid'])
    osapi.add_feature(d['did'], d['wid'], eid, 'modularBrake', 'v5 ' + name, d['fs1'], mv, p)
    parts = geom.fetch_parts(d['did'], d['wid'], eid)
    n = 'fin_v5' if name == 'A' else 'fin_v5b'
    pickle.dump(parts, open(W / f'{n}.pkl', 'wb'))
    if tag: pickle.dump(parts, open(W / f'{n}_{tag}.pkl', 'wb'))
    print(name, len(parts), 'parts')
    osapi.delete(f"/elements/d/{d['did']}/w/{d['wid']}/e/{eid}")
