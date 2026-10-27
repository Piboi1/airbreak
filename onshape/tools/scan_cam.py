import json, time, scan, run
p = str(run.S / 'scan.json'); res = json.load(open(p))
res['cam'] = []
for release in [18, 22, 26, 30]:
    for t in range(4):
        try:
            parts = scan.state(0, release); break
        except Exception as e:
            print('retry', e, flush=True); time.sleep(30)
    ov = scan.overlap_pairs(parts, {'R'}, {'P1','P2','P3','P4'})
    res['cam'].append((release, ov)); json.dump(res, open(p,'w'), indent=1); print('cam', release, ov, flush=True)
print('DONE', flush=True)
