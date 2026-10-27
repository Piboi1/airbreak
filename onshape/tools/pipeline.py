"""Rebuild everything from fs source: studios, assemblies, verification, exports, figures."""
import sys, subprocess, pickle, math, json
import numpy as np, trimesh
import run, osapi, asm, check, geom

d = run.ids()


def studios():
    ok = True
    for key, name, p in [
        ('ps_v1', 'V1 screwed modular brake', run.params(compact=False)),
        ('ps_v2', 'V2 compact modular brake', run.params(compact=True)),
        ('ps_v1b', 'Open state (90 deg panels, 65 deg rotor, button up)', run.params(opening=90, release=65, button=4.5, compact=False)),
        ('ps_v2b', 'Open state (90 deg panels, 65 deg rotor, button up)', run.params(opening=90, release=65, button=4.5, compact=True)),
        ('ps_samples', 'Unloaded spiral samples + return leaf', run.params(mode=2))]:
        st = run.go(key, 'fs1', 'modularBrake', name, p)
        print(key, st); ok &= (st == 'OK')
    return ok


def assemblies():
    d = run.ids()
    for key, ps, title, compact in [('asm_v1', 'ps_v1', 'ASM-V1 - Screwed reinforced bottom spring - assembly (mates + hardware)', False),
                                    ('asm_v2', 'ps_v2', 'ASM-V2 - Compact head inside upper BT80 tube - assembly (mates + hardware)', True)]:
        if key in d:
            try: osapi.delete(f"/elements/d/{d['did']}/w/{d['wid']}/e/{d[key]}")
            except Exception as e: print('delete skip', str(e)[:80])
        d[key] = osapi.new_element(d['did'], d['wid'], 'assembly', title); run.save(d)
        osapi.post(f"/assemblies/d/{d['did']}/w/{d['wid']}/e/{d[key]}/instances", {"documentId": d['did'], "elementId": d[ps], "isWholePartStudio": True, "isAssembly": False, "configuration": ""})
        bad = asm.build(d[key], compact)
        print(key, 'non-OK mates:', bad)


def verify():
    NV = np.array([1, -1, 0]) / math.sqrt(2)
    report = {}
    for key, tag in [('ps_v1', 'V1 closed'), ('ps_v2', 'V2 closed'), ('ps_v1b', 'V1 open'), ('ps_v2b', 'V2 open')]:
        parts = check.load(key, 'fin_' + key.replace('ps_', ''))
        res = geom.interference(parts, min_vol=0.3)
        printed = [(round(float(r[0]), 2), r[1][:20], r[2][:20]) for r in res
                   if not r[1].startswith('HW') and not r[2].startswith('HW') and not ('REF' in r[1] or 'REF' in r[2])
                   and not (r[1][:2] in ('C1', 'C2') and r[2][:2] in ('C1', 'C2'))
                   and not ({r[1][:2], r[2][:2]} == {'W ', 'B '})]
        wt = [n[:20] for _, (n, m) in parts.items() if not m.is_watertight]
        hw = sum(1 for r in res if r[1].startswith('HW') or r[2].startswith('HW'))
        # hex-key access to the seam screws with the fins open (key level, no tilt)
        acc = None
        if tag.endswith('open'):
            allm = trimesh.util.concatenate([m for _, (n, m) in parts.items() if not n.startswith(('HW', 'REF'))])
            ray = trimesh.ray.ray_triangle.RayMeshIntersector(allm)
            acc = []
            for side in (0, 1):
                for zc in (8, 44):
                    sa = math.radians(45 + 180 * side)
                    p0 = np.array([27 * math.cos(sa), 27 * math.sin(sa), zc]); d0 = -NV
                    tip = p0 + d0 * 5.0
                    u = np.cross(d0, [0, 0, 1]); u /= np.linalg.norm(u); v = np.cross(d0, u)
                    pts = [tip + d0 * 1.5] + [tip + d0 * 1.5 + 1.25 * (math.cos(a) * u + math.sin(a) * v) for a in np.linspace(0, 2 * math.pi, 8, endpoint=False)]
                    loc, idx, _ = ray.intersects_location(np.array(pts), np.array([d0] * len(pts)), multiple_hits=False)
                    acc.append('clear' if len(loc) == 0 else 'BLOCKED')
        report[tag] = dict(parts=len(parts), printed_overlaps=printed, non_watertight=wt, hardware_pairs=hw, seam_key_access=acc)
        print(tag, report[tag])
    json.dump(report, open(str(run.S / 'verify.json'), 'w'), indent=1)
    return report


if __name__ == '__main__':
    steps = sys.argv[1:] or ['studios', 'assemblies', 'verify']
    if 'studios' in steps and not studios(): sys.exit('studio failed')
    if 'assemblies' in steps: assemblies()
    if 'verify' in steps: verify()
