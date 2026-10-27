"""Fetch Onshape tessellation, build trimesh parts (mm), export STL, interference checks."""
import numpy as np, trimesh, json
import osapi


def fetch_parts(did, wid, eid, kind="partstudios", chord=0.03, ang=0.15):
    t = osapi.get(f"/{kind}/d/{did}/w/{wid}/e/{eid}/tessellatedfaces",
                  params={"chordTolerance": chord, "angleTolerance": ang})
    out = {}
    for b in t["bodies"]:
        if b.get("bodyType") != "SOLID":
            continue
        tris = []
        for f in b["faces"]:
            for fa in f["facets"]:
                v = fa["vertices"]
                tris.append([[p["x"], p["y"], p["z"]] for p in v])
        arr = np.array(tris, dtype=float).reshape(-1, 3) * 1000.0
        faces = np.arange(len(arr)).reshape(-1, 3)
        m = trimesh.Trimesh(arr, faces, process=True)
        m.merge_vertices()
        out[b["id"]] = (b["name"], m)
    return out


def write_stls(parts, folder):
    import os, re
    os.makedirs(folder, exist_ok=True)
    for pid, (name, m) in parts.items():
        safe = re.sub(r"[^A-Za-z0-9]+", "_", name)[:60].strip("_")
        m.export(f"{folder}/{safe}.stl")


def combined(parts):
    return trimesh.util.concatenate([m for _, m in parts.values()])


def interference(parts, min_vol=0.5):
    """Pairwise boolean-intersection volumes (mm^3) between watertight solids."""
    res = []
    items = [(pid, n, m) for pid, (n, m) in parts.items() if m.is_watertight and m.volume > 0]
    for i in range(len(items)):
        for j in range(i + 1, len(items)):
            a, b = items[i], items[j]
            if (a[2].bounds[1] < b[2].bounds[0]).any() or (b[2].bounds[1] < a[2].bounds[0]).any():
                continue
            try:
                inter = trimesh.boolean.intersection([a[2], b[2]], engine="manifold")
                v = inter.volume if len(inter.faces) else 0
            except Exception as e:
                v = -1
            if v > min_vol or v < 0:
                res.append((round(v, 2), a[1][:34], b[1][:34]))
    return sorted(res, reverse=True)
