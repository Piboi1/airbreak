import json, scan, run
res = {'latch': [], 'cam': []}
for op, rel in [(3.0, 14), (3.0, 16)]:
    parts = scan.state(op, rel)
    ov = scan.overlap_pairs(parts, {'P1','P2','P3','P4'}, {'L1','L2','L3','L4'})
    res['latch'].append((op, rel, ov)); print('latch', op, rel, ov, flush=True)
for rel in [22, 26]:
    parts = scan.state(0, rel)
    ov = scan.overlap_pairs(parts, {'R'}, {'P1','P2','P3','P4'})
    res['cam'].append((rel, ov)); print('cam', rel, ov, flush=True)
json.dump(res, open(str(run.S / 'scan_final.json'), 'w'), indent=1)
print('DONE')
