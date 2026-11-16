"""Build V6 in Onshape: upload the source, create V6-A / V6-B part studios (mode 5 + 'V6 weight reduction' + 'head cup fixes'),
check V5 is unchanged with both boxes off, cache meshes as fin_v6.pkl / fin_v6b.pkl."""
import sys, pickle, json
sys.path.insert(0, '.')
import run, osapi, geom
W = run.S
d = run.ids(); did, wid = d['did'], d['wid']
step = sys.argv[1]
def b(pid, v): return {"btType": "BTMParameterBoolean-144", "value": bool(v), "parameterId": pid}
def P(v6, fix, open_=False):
    p = run.params(mode=5, compact=True, **({'opening': 90, 'release': 65, 'button': 4.5} if open_ else {}))
    return p + [b('v6', v6), b('headfix', fix)]
def studio(name, params, keep_key=None):
    eid = osapi.new_element(did, wid, 'partstudio', name)
    mv = osapi.current_microversion(did, wid)
    osapi.add_feature(did, wid, eid, 'modularBrake', 'v6' if 'V6' in name else 'check', d['fs1'], mv, params)
    st, f = osapi.feature_states(did, wid, eid)
    print(name, json.dumps(st)[:300])
    parts = geom.fetch_parts(did, wid, eid)
    if keep_key: d[keep_key] = eid; run.save(d)
    return eid, parts
if step == 'upload':
    for e in osapi.get(f"/documents/d/{did}/w/{wid}/elements"):
        if e['name'].startswith('SCRATCH'): osapi.delete(f"/elements/d/{did}/w/{wid}/e/{e['id']}"); print('deleted', e['name'])
    run.upload_fs('../fs/airbrake_v1_v2.fs')
    specs = osapi.fs_specs(did, wid, d['fs1'])
    print('feature specs:', [s.get('featureType') for s in specs.get('featureSpecs', [])])
elif step == 'checkv5':
    eid, parts = studio('SCRATCH v5 check', P(False, False))
    pickle.dump(parts, open(W / 'v5check.pkl', 'wb'))
    osapi.delete(f"/elements/d/{did}/w/{wid}/e/{eid}")
elif step == 'build':
    _, pa = studio('V6-A - weight-reduced V5 (PDF cuts + head cup fixes), locked (closed)', P(True, True), 'ps_v6')
    pickle.dump(pa, open(W / 'fin_v6.pkl', 'wb'))
    _, pb = studio('V6-B - open (90 deg fins, 65 deg rotor)', P(True, True, True), 'ps_v6b')
    pickle.dump(pb, open(W / 'fin_v6b.pkl', 'wb'))
