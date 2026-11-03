"""V5 offline checks on the cached meshes (no API calls): fin_v5 (closed) and fin_v5b (open) in $AIRBRAKE_WORK.
Run:  python3 check_v5.py [overlap|fins|rotor|latch|dropin|install|nuts|head|exit|all]
Frame: V4 frame (rotor axis z, module bottom z=-10). Fin 1 azimuth 0, hinge axis through (25,0,0) along y.
"""
import pickle, os, sys, math, numpy as np, trimesh
from sweep_open import vol
W = os.environ['AIRBRAKE_WORK']
Rz = lambda d: trimesh.transformations.rotation_matrix(math.radians(d), [0, 0, 1])
Tz = lambda z: trimesh.transformations.translation_matrix([0, 0, z])
Tx = lambda x: trimesh.transformations.translation_matrix([x, 0, 0])
Ty = lambda y: trimesh.transformations.translation_matrix([0, y, 0])


def load(tag):
    parts = pickle.load(open(f'{W}/{tag}.pkl', 'rb'))
    d = {}
    for _, (n, m) in parts.items():
        d[n] = m
    return d


def pick(d, prefix):
    r = [m for n, m in d.items() if n.startswith(prefix)]
    assert len(r) == 1, (prefix, len(r))
    return r[0]


def moved(m, T):
    mm = m.copy(); mm.apply_transform(T); return mm


def fin_open(f, deg, pivot=(25, 0, 0)):
    return moved(f, trimesh.transformations.rotation_matrix(math.radians(deg), [0, 1, 0], point=list(pivot)))


def overlaps(d, label, min_vol=0.05):
    print(f'--- interference {label}')
    printed = ['C ', 'R ', 'P1 ', 'P2 ', 'P3 ', 'P4 ', 'H ', 'K ', 'T ']
    ms = {k.strip(): pick(d, k) for k in printed}
    ms['tube'] = pick(d, 'REF BT80 tube')
    ms['servo'] = pick(d, 'E SG90'); ms['horn'] = pick(d, 'EH ')
    ms['batt'] = pick(d, 'E4 '); ms['merc'] = pick(d, 'E2 '); ms['reg'] = pick(d, 'E3 ')
    for n, m in d.items():
        if n.startswith('HW'):
            ms[n[:40]] = m
    keys = list(ms)
    bad = []
    for i in range(len(keys)):
        for j in range(i + 1, len(keys)):
            a, b = keys[i], keys[j]
            if a.startswith('HW') and b.startswith('HW'):
                continue
            v = vol(ms[a], ms[b])
            if v > min_vol or v < 0:
                bad.append((round(v, 2), a, b))
    for r in sorted(bad, reverse=True):
        print('  ', r)
    wt = [n[:40] for n, m in d.items() if not m.is_watertight]
    print('  non-watertight:', wt)
    return bad


def main(which):
    dc = load('fin_v5'); do = load('fin_v5b')
    C, R, H, K, T, tube = (pick(dc, 'C '), pick(dc, 'R '), pick(dc, 'H '), pick(dc, 'K '), pick(dc, 'T '), pick(dc, 'REF BT80 tube'))
    P = [pick(dc, f'P{i} ') for i in range(1, 5)]
    servo, horn = pick(dc, 'E SG90'), pick(dc, 'EH ')
    if which in ('overlap', 'all'):
        overlaps(dc, 'closed (locked)')
        overlaps(do, 'open (fins 90, rotor 65)')
    if which in ('fins', 'all'):
        print('--- fin 1 opening sweep (fin vs housing / tube / rotor / head)')
        for th in (1, 3, 5, 10, 15, 25, 40, 55, 70, 90):
            f = fin_open(P[0], th)
            print(f'  open {th:2d}:', {k: round(vol(f, m), 1) for k, m in dict(C=C, tube=tube, R=R, H=H).items()})
    if which in ('rotor', 'all'):
        print('--- rotor sweep (rotor turned by deg vs housing / servo / horn-slot parts / closed fins)')
        for th in (-5, -3, -2, -1, 0, 5, 15, 25, 30, 40, 55, 65, 66, 67, 68, 70):
            r = moved(R, Rz(th))
            row = {k: round(vol(r, m), 1) for k, m in dict(C=C, servo=servo, P1=P[0], P2=P[1]).items()}
            print(f'  rotor {th:3}:', {k: v for k, v in row.items() if v > 0.05} or 'clear')
    if which in ('latch', 'all'):
        print('--- latch and cam timing (rotor integral catch vs fin 1; cam vs closed fin)')
        print('  hold at rotor 0 (fin opening -> overlap mm3):', {op: round(vol(fin_open(P[0], op), R), 2) for op in (0.5, 1, 1.5, 2, 3)})
        f3 = fin_open(P[0], 3.0)
        print('  release, fin held at 3 deg (overlap by rotor deg):', {rot: round(vol(f3, moved(R, Rz(rot))), 2) for rot in (8, 10, 12, 14, 16, 18, 20)})
        print('  cam contact (rotor vs closed fin mm3 by rotor deg):', {rot: round(vol(moved(R, Rz(rot)), P[0]), 2) for rot in (18, 20, 22, 24, 25, 26, 28, 30, 35)})
    if which in ('dropin', 'all'):
        print('--- rotor drop-in from the top, fins NOT yet fitted: max overlap vs housing over the descent')
        for rho in (-3, 0, 5, 10, 14, 18, 22, 26, 30, 40, 60, 67):
            worst = 0
            for z in range(120, -1, -4):
                r = moved(R, Rz(rho) @ Tz(z))
                worst = max(worst, vol(r, C))
                if worst > 0.5: break
            # final seat check
            print(f'  rotor angle {rho:3}: max overlap {worst:.1f} mm3', '(free)' if worst <= 0.05 else '')
    if which in ('install', 'all'):
        print('--- fin 1 installed radially through its window (module outside the tube): overlap vs housing / rotor')
        for rho in (0, 8, 14, 18, 22, 26):
            row = []
            r = moved(R, Rz(rho))
            for x in range(40, -1, -3):
                f = moved(P[0], Tx(x))
                row.append((vol(f, C), vol(f, r)))
            print(f'  rotor {rho:2} deg: worst housing {max(a for a, b in row):.1f}, worst rotor {max(b for a, b in row):.1f} mm3')
    if which in ('nuts', 'all'):
        print('--- hinge nut loading (nut box 5.5 x 2.4 x 6.35 mm) from outside through the window, then slid -Y into the +Y ear slot')
        nut = trimesh.creation.box(extents=[5.5, 2.4, 6.35])
        worst = 0
        for x in np.arange(42, 24.9, -1.5):
            worst = max(worst, vol(moved(nut, trimesh.transformations.translation_matrix([x, 14.0, 0])), C))
        w2 = 0
        for y in np.arange(14.0, 10.9, -0.5):
            w2 = max(w2, vol(moved(nut, trimesh.transformations.translation_matrix([25.0, y, 0])), C))
        print(f'  approach along -x at y=14: {worst:.2f} mm3; slide -y into slot: {w2:.2f} mm3 (small = nut fits the pocket)')
        print('--- hinge bolt access channel: head cylinder r=2.9 and key r=1.2 along +Y from y=-60 to the head, housing only')
        for rr, nm in ((2.9, 'head'), (1.2, 'key')):
            cyl = trimesh.creation.cylinder(radius=rr, height=48, sections=24)
            cyl.apply_transform(trimesh.transformations.rotation_matrix(math.pi / 2, [1, 0, 0]))
            cyl.apply_translation([25, -12.2 - 24, 0])
            print(f'  {nm}: overlap with housing {vol(cyl, C):.2f} mm3 (0 = straight line clear)')
    if which in ('head', 'all'):
        print('--- head insertion from above (cup + servo + horn + lid + electronics) vs housing / rotor / fins / tube')
        grp = trimesh.util.concatenate([H, K, servo, horn, pick(dc, 'E4 '), pick(dc, 'E2 '), pick(dc, 'E3 ')])
        for rho in (0, 3, 6, 9, 12, 15):
            worst = {'C': 0, 'R': 0, 'fins': 0, 'tube': 0}
            zfirst = None
            for dz in range(30, -1, -2):
                g = moved(grp, Tz(dz))
                r = moved(R, Rz(rho))
                v = {'C': vol(g, C), 'R': vol(g, r), 'fins': max(vol(g, p) for p in P), 'tube': vol(g, tube)}
                for k in v: worst[k] = max(worst[k], v[k])
            print(f'  rotor offset {rho:2} deg:', {k: round(v, 1) for k, v in worst.items() if v > 0.05} or 'clear')
    if which in ('access', 'all'):
        print('--- hex-key / screwdriver access')
        allm = {n: m for n, m in dc.items() if not n.startswith('HW')}
        worst = 0
        for n, m in dc.items():
            if n.startswith('HW') and 'bolt - M3x8' in n:
                # axis from the bolt mesh: head end is the outer end; key r=1.0 from R=35 to R=80 along the radial direction
                ctr = m.bounds.mean(0); az = math.atan2(ctr[1], ctr[0])
                z = ctr[2]
                key = trimesh.creation.cylinder(radius=1.0, height=45, sections=16)
                key.apply_transform(trimesh.transformations.rotation_matrix(math.pi / 2, [0, 1, 0]))
                key.apply_translation([35 + 22.5, 0, 0]); key.apply_transform(Rz(math.degrees(az))); key.apply_translation([0, 0, z])
                v = max(vol(key, mm) for mm in allm.values())
                worst = max(worst, v)
        print(f'  12 radial bolts: 2 mm key along the radial axis from outside, worst overlap with any part: {worst:.2f} mm3')
        for s, (R_, azd) in {'servo bolt 1': (18.8, 135), 'servo bolt 2': (9.3, 315)}.items():
            drv = trimesh.creation.cylinder(radius=1.5, height=60, sections=16)
            drv.apply_translation([R_ * math.cos(math.radians(azd)), R_ * math.sin(math.radians(azd)), 52 + 30 + 0.3 + 20])
            print(f'  {s}: screwdriver down from above vs head cup {vol(drv, H):.2f}, lid {vol(drv, K):.2f} mm3 (lid and electronics fitted AFTER the servo)')
    if which in ('exit', 'all'):
        print('--- module exit routes (module = housing + rotor + 4 fins, fully latched)')
        mod = trimesh.util.concatenate([C, R] + P)
        horn_h = trimesh.util.concatenate([servo, horn, H, K])
        b = {'tube': 0, 'head': 0}
        for dz in range(0, 125, 5):
            m = moved(mod, Tz(-dz))
            b['tube'] = max(b['tube'], vol(m, tube))
            b['head'] = max(b['head'], vol(m, horn_h))
        print('  bottom route (transition removed): worst overlap', {k: round(v, 2) for k, v in b.items()})
        t = {'tube': 0}
        for dz in range(0, 125, 5):
            t['tube'] = max(t['tube'], vol(moved(mod, Tz(dz)), tube))
        print('  top route (head removed): worst overlap vs tube', round(t['tube'], 2))
        tr = max(vol(moved(T, Tz(-dz)), tube) for dz in range(0, 100, 5))
        print('  transition out of the bottom: worst overlap vs tube', round(tr, 2))
        tr2 = max(vol(moved(horn_h, Tz(dz)), tube) for dz in range(0, 100, 5))
        print('  head out of the top: worst overlap vs tube', round(tr2, 2))


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else 'all')
