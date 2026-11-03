"""Regression: rebuild V1..V4 (closed + open) with the current FeatureScript in scratch part studios and compare every part
volume with the cached baselines base_<tag>_parts.pkl (taken from the original studios before the V5 change). Deletes the scratch studios."""
import sys, pickle, collections
sys.path.insert(0, '.')
import run, osapi, geom
W = run.S
CASES = {  # tag: (mode, compact, open)
    'v1': (0, False, False), 'v1b': (0, False, True), 'v2': (0, True, False), 'v2b': (0, True, True),
    'v3': (3, True, False), 'v3b': (3, True, True), 'v4': (4, True, False), 'v4b': (4, True, True)}
only = sys.argv[1:] or list(CASES)
ok_all = True
for tag in only:
    mode, compact, opened = CASES[tag]
    key = 'tmp_' + tag
    p = run.params(mode=mode, compact=compact, opening=90 if opened else 0, release=65 if opened else 0, button=4.5 if opened else 0)
    out = run.build(key, 'fs1', 'modularBrake', 'regress ' + tag, p, ps_name='SCRATCH regression ' + tag)
    st = out[0][1].get('featureStatus') if out else None
    d = run.ids()
    parts = geom.fetch_parts(d['did'], d['wid'], d[key])
    base = pickle.load(open(W / f'base_{tag}_parts.pkl', 'rb'))
    vb = collections.Counter((n, round(m.volume, 1)) for _, (n, m) in base.items())
    vn = collections.Counter((n, round(m.volume, 1)) for _, (n, m) in parts.items())
    diff_b = vb - vn; diff_n = vn - vb
    same = (st == 'OK' and not diff_b and not diff_n)
    ok_all &= same
    print(f'{tag}: status {st}, parts {len(base)} -> {len(parts)}, {"IDENTICAL volumes" if same else "DIFFERENT"}')
    for k, v in list(diff_b.items())[:6]: print('   baseline only:', k)
    for k, v in list(diff_n.items())[:6]: print('   new only     :', k)
    osapi.delete(f"/elements/d/{d['did']}/w/{d['wid']}/e/{d[key]}")
    del d[key]; run.save(d)
print('ALL IDENTICAL' if ok_all else 'REGRESSION FOUND')
