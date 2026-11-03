"""Regenerate the FeatureScript, upload it, rebuild the V5-A (closed) and V5-B (open) part studios and cache their meshes as fin_v5 / fin_v5b."""
import sys, shutil, os
sys.path.insert(0, '.')
import run, check
W = run.S
st = run.go('ps_v5', 'fs1', 'modularBrake', 'V5 modular airbrake', run.params(mode=5, compact=True), ps_name='V5-A - modular: module + head + transition + tube, locked (closed)')
print('V5-A', st)
if st == 'OK':
    check.load('ps_v5', 'v5'); shutil.copy(W / 'v5_parts.pkl', W / 'fin_v5.pkl')
if len(sys.argv) > 1 and sys.argv[1] == 'both' or st == 'OK':
    st = run.go('ps_v5b', 'fs1', 'modularBrake', 'V5 modular airbrake (open)', run.params(mode=5, compact=True, opening=90, release=65, button=4.5), ps_name='V5-B - open (90 deg fins, 65 deg rotor)')
    print('V5-B', st)
    if st == 'OK':
        check.load('ps_v5b', 'v5b'); shutil.copy(W / 'v5b_parts.pkl', W / 'fin_v5b.pkl')
