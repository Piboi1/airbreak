import json, scan, run
res = {'latch': [], 'cam': []}
def log(): json.dump(res, open(str(run.S / 'scan.json'), 'w'), indent=1)
for opening, release in [(0.5,0),(1.0,0),(2.0,0),(3.0,0),(3.0,10),(3.0,14),(3.0,16),(3.0,18),(3.0,20)]:
    parts = scan.state(opening, release)
    ov = scan.overlap_pairs(parts, {'P1','P2','P3','P4'}, {'L1','L2','L3','L4'})
    res['latch'].append((opening, release, ov)); log(); print('latch', opening, release, ov, flush=True)
for release in [18, 20, 22, 24, 26, 30]:
    parts = scan.state(0, release)
    ov = scan.overlap_pairs(parts, {'R'}, {'P1','P2','P3','P4'})
    res['cam'].append((release, ov)); log(); print('cam', release, ov, flush=True)
print('DONE', flush=True)
