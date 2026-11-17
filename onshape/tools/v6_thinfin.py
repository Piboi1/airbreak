"""Switch V6-A / V6-B in place (features/updates endpoint) to: V5 + thin fin T + head cup fixes, PDF cuts off. Usage: python3 v6_thinfin.py ps_v6b"""
import sys, json, copy
sys.path.insert(0, '.')
import run, osapi
d = run.ids(); did, wid = d['did'], d['wid']; eid = d[sys.argv[1]]
def b(pid, v): return {"btType": "BTMParameterBoolean-144", "value": bool(v), "parameterId": pid}
f = osapi.get(f"/partstudios/d/{did}/w/{wid}/e/{eid}/features")
ft = copy.deepcopy([x for x in f['features'] if x.get('featureType') == 'modularBrake'][0])
ft['namespace'] = f"e{d['fs1']}::m{f['sourceMicroversion']}"
old = {q['parameterId']: q for q in ft['parameters']}
for pid, v in (('v6', False), ('headfix', True), ('thinfin', True)):
    if pid in old: old[pid]['value'] = v
    else: old[pid] = b(pid, v)
ft['parameters'] = list(old.values())
r = osapi.post(f"/partstudios/d/{did}/w/{wid}/e/{eid}/features/updates", {"btType": "BTUpdateFeaturesCall-1748", "features": [ft],
               "serializationVersion": "1.2.23", "sourceMicroversion": f['sourceMicroversion'], "rejectMicroversionSkew": False})
print(sys.argv[1], r['featureStates'])
