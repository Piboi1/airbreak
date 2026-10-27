"""Upload FeatureScript, (re)build a Part Studio feature, report status."""
import json, sys, time, pathlib
import osapi

import os
S = pathlib.Path(os.environ.get('AIRBRAKE_WORK', str(pathlib.Path(__file__).resolve().parent.parent / '.work')))
S.mkdir(parents=True, exist_ok=True)
IDS = S / 'ids.json'


def ids():
    return json.load(open(IDS))


def save(d):
    json.dump(d, open(IDS, 'w'))


def upload_fs(path, key='fs1', name="01 - V1 screwed + V2 compact (source)"):
    d = ids()
    if key not in d:
        d[key] = osapi.new_element(d['did'], d['wid'], 'featurestudio', name)
        save(d)
    src = open(path).read()
    r = osapi.set_feature_studio(d['did'], d['wid'], d[key], src)
    return d[key]


def clear_features(did, wid, ps):
    f = osapi.get(f'/partstudios/d/{did}/w/{wid}/e/{ps}/features')
    for ft in f['features']:
        if ft.get('btType') == 'BTMFeature-134' and ft.get('featureType') in ('modularBrake', 'camKickBrake'):
            osapi.delete(f"/partstudios/d/{did}/w/{wid}/e/{ps}/features/featureid/{ft['featureId']}")


def build(ps_key, fs_key, ftype, name, params, ps_name=None):
    d = ids()
    if ps_key not in d:
        d[ps_key] = osapi.new_element(d['did'], d['wid'], 'partstudio', ps_name or name)
        save(d)
    did, wid, ps, fs = d['did'], d['wid'], d[ps_key], d[fs_key]
    clear_features(did, wid, ps)
    mv = osapi.current_microversion(did, wid)
    t = time.time()
    osapi.add_feature(did, wid, ps, ftype, name, fs, mv, params)
    dt = time.time() - t
    return report(did, wid, ps, dt)


def report(did, wid, ps, dt=0):
    f = osapi.get(f'/partstudios/d/{did}/w/{wid}/e/{ps}/features')
    out = []
    for ft in f['features']:
        if ft.get('btType') != 'BTMFeature-134' or ft.get('featureType') not in ('modularBrake', 'camKickBrake'):
            continue
        st = f['featureStates'].get(ft['featureId'], {})
        out.append((ft['name'], st))
    print(f'regen {dt:.1f}s', json.dumps(out, indent=1)[:1800])
    return out


def params(mode=0, opening=0, release=0, button=0, compact=False, hardware=True, tubes=True):
    def b(pid, v):
        return {"btType": "BTMParameterBoolean-144", "value": bool(v), "parameterId": pid}
    return [osapi.qty('mode', mode), osapi.qty('opening', opening), osapi.qty('release', release),
            osapi.qty('button', button), b('compact', compact), b('hardware', hardware), b('tubes', tubes)]


if __name__ == '__main__':
    fs = upload_fs('../fs/airbrake_v1_v2.fs')
    print('FS element', fs)
    build('ps_v1', 'fs1', 'modularBrake', 'V1 screwed modular brake', params(compact=False),
          ps_name='V1-A - screwed, locked (closed)')


def eval_fs(ps_key, fs_key, call_src, fs_mv=None):
    """Evaluate FS in a part studio context. call_src is the body of function(context, queries)."""
    d = ids()
    did, wid, ps, fs = d['did'], d['wid'], d[ps_key], d[fs_key]
    mv = fs_mv or osapi.current_microversion(did, wid)
    script = ('FeatureScript 3095;\nimport(path : "onshape/std/geometry.fs", version : "3095.0");\n'
              f'import(path : "{fs}", version : "{mv}");\n'
              'function(context is Context, queries is map)\n{\n' + call_src + '\n}')
    r = osapi.post(f"/partstudios/d/{did}/w/{wid}/e/{ps}/featurescript", {"script": script, "queries": {}})
    return r


def diagnose(ps_key='ps_v1', fs_key='fs1', **kw):
    p = dict(mode=0, opening=0, release=0, button=0, compact=False, hardware=True, tubes=True)
    p.update(kw)
    call = ('try { modularBrake(context, newId() + "dbg", {"mode":%d,"opening":%s,"release":%s,"button":%s,"compact":%s,"hardware":%s,"tubes":%s}); return "OK"; }\n'
            'catch(e) { return "ERR: " ~ toString(e); }' %
            (p['mode'], p['opening'], p['release'], p['button'], str(p['compact']).lower(), str(p['hardware']).lower(), str(p['tubes']).lower()))
    r = eval_fs(ps_key, fs_key, call)
    return r


def feature_error(ps_key):
    d = ids()
    did, wid, ps = d['did'], d['wid'], d[ps_key]
    f = osapi.get(f'/partstudios/d/{did}/w/{wid}/e/{ps}/features')
    res = []
    for ft in f['features']:
        if ft.get('btType') == 'BTMFeature-134' and ft.get('featureType') in ('modularBrake', 'camKickBrake'):
            script = 'function(context is Context, queries is map) { return [getFeatureError(context, makeId("%s")), getFeatureWarning(context, makeId("%s"))]; }' % (ft['featureId'], ft['featureId'])
            r = osapi.post(f"/partstudios/d/{did}/w/{wid}/e/{ps}/featurescript", {"script": script, "queries": {}})
            res.append(r['result'])
    return res


def go(ps_key, fs_key, ftype, name, p, ps_name=None, fs_path='../fs/airbrake_v1_v2.fs'):
    import subprocess
    subprocess.check_call([sys.executable, 'build_fs.py'])
    upload_fs(fs_path)
    out = build(ps_key, fs_key, ftype, name, p, ps_name)
    st = out[0][1].get('featureStatus') if out else None
    if st != 'OK':
        r = feature_error(ps_key)
        def flat(v):
            if isinstance(v, dict):
                if 'value' in v and isinstance(v['value'], (str, int, float, bool)): return v['value']
                if 'value' in v: return [flat(x) for x in v['value']]
            return v
        print('ERROR DETAIL:', json.dumps([flat(x) for x in r])[:800])
    return st
