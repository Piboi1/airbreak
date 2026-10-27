"""Export one print-ready STL per unique printed part (auto-oriented, z-min = 0), mm."""
import sys, re, os, numpy as np, trimesh, json
import geom, run

NAMES = {
    'A': 'pushrod', 'B': 'release_yoke', 'C1': 'housing_half_1', 'C2': 'housing_half_2', 'D': 'cartridge_dock',
    'F': 'lid', 'G': 'servo_keeper', 'I': 'locking_pin', 'J': 'horn_saddle', 'L1': 'catch_cap', 'M': 'casing',
    'N': 'bayonet_collar', 'P1': 'fin', 'Q': 'thrust_collar', 'R': 'rotor', 'S': 'servo_cradle', 'T': 'winding_cap',
    'U': 'output_hub', 'X': 'double_d_adapter'}
REPEAT = {'P1': 4, 'L1': 4}
SKIP_TOK = {'E', 'V', 'W', 'J_'}   # reference parts


def orient(m):
    best = None
    for k, R in enumerate(candidates()):
        mm = m.copy(); mm.apply_transform(R)
        mm.apply_translation([0, 0, -mm.bounds[0][2]])
        n = mm.face_normals; a = mm.area_faces
        tri_z = mm.triangles[:, :, 2].min(1)
        over = a[(n[:, 2] < -0.7) & (tri_z > 0.15)].sum()
        h = mm.bounds[1][2]
        score = over + 0.05 * h
        if best is None or score < best[0]:
            best = (score, mm, over, h)
    return best


def candidates():
    I = np.eye(4)
    out = [I]
    for ax, ang in [([1, 0, 0], np.pi), ([1, 0, 0], np.pi / 2), ([1, 0, 0], -np.pi / 2), ([0, 1, 0], np.pi / 2), ([0, 1, 0], -np.pi / 2)]:
        out.append(trimesh.transformations.rotation_matrix(ang, ax))
    return out


def export(ps_key, outdir, tag):
    d = run.ids()
    parts = geom.fetch_parts(d['did'], d['wid'], d[ps_key], chord=0.015, ang=0.1)
    os.makedirs(outdir, exist_ok=True)
    rows = []
    for pid, (name, m) in parts.items():
        tok = name.split(' ')[0]
        if tok in NAMES and name.split(' ')[0] == tok and 'REFERENCE' not in name and not name.startswith(('HW', 'REF', 'TP')):
            sc, mm, over, h = orient(m)
            n = REPEAT.get(tok, 1)
            fn = f"{outdir}/{tok.rstrip('1234') if tok in ('P1','L1') else tok}_{NAMES[tok]}_x{n}.stl"
            fn = fn.replace('/P_', '/P_').replace('/L_', '/L_')
            mm.export(fn)
            rows.append((tok, NAMES[tok], n, round(m.volume), round(mm.bounds[1][2], 1), round(over, 1), fn.split('/')[-1]))
    return rows


if __name__ == '__main__':
    for key, out in [('ps_v1', '../exports/v1/print'), ('ps_v2', '../exports/v2/print')]:
        rows = export(key, out, key)
        print(key)
        for r in sorted(rows): print('  ', r)
