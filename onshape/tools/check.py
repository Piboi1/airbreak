import sys, json, pickle, numpy as np, trimesh
sys.path.insert(0, '.')
import geom, run
S = run.S

def load(ps_key, tag):
    d = run.ids()
    parts = geom.fetch_parts(d['did'], d['wid'], d[ps_key])
    pickle.dump(parts, open(S / f'{tag}_parts.pkl', 'wb'))
    return parts

def inventory(parts):
    rows = []
    for pid, (n, m) in parts.items():
        rows.append((n, m.is_watertight, round(m.volume, 0) if m.is_watertight else None, m.bounds.round(1).tolist()))
    return rows

def classify(parts, min_vol=0.3):
    res = geom.interference(parts, min_vol=min_vol)
    return res

if __name__ == '__main__':
    tag, key = sys.argv[1], sys.argv[2]
    parts = load(key, tag)
    print(len(parts), 'parts')
    hw = [n for n, m in [(n, m) for _, (n, m) in parts.items()] if n.startswith('HW')]
    print('hardware parts:', len(hw))
    for r in sorted(inventory(parts)):
        if not r[0].startswith('HW'):
            print(('  ' if r[1] else '! '), r[0][:70], r[2], r[3])
    allm = np.array([m.bounds for _, (n, m) in parts.items()])
    print('overall bounds', allm[:, 0].min(0).round(1), allm[:, 1].max(0).round(1))
