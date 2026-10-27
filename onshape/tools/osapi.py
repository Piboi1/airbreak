"""Minimal Onshape REST helper. Credentials come from ONSHAPE_ACCESS_KEY / ONSHAPE_SECRET_KEY."""
import os, json, time, base64, requests

BASE = "https://cad.onshape.com/api/v10"
AUTH = (os.environ["ONSHAPE_ACCESS_KEY"], os.environ["ONSHAPE_SECRET_KEY"])
JSON = {"Accept": "application/json;charset=UTF-8; qs=0.09", "Content-Type": "application/json"}


def call(method, path, *, params=None, body=None, accept=None, raw=False, timeout=300):
    url = path if path.startswith("http") else BASE + path
    headers = dict(JSON)
    if accept:
        headers["Accept"] = accept
    for attempt in range(6):
        r = requests.request(method, url, auth=AUTH, headers=headers, params=params,
                             data=json.dumps(body) if body is not None else None,
                             timeout=timeout, allow_redirects=True)
        if r.status_code == 429:
            time.sleep(2 ** attempt)
            continue
        break
    if r.status_code >= 400:
        raise RuntimeError(f"{method} {path} -> {r.status_code}: {r.text[:1500]}")
    if raw:
        return r
    if not r.content:
        return None
    try:
        return r.json()
    except ValueError:
        return r.content


def get(path, **kw):  return call("GET", path, **kw)
def post(path, body=None, **kw): return call("POST", path, body=body, **kw)
def delete(path, **kw): return call("DELETE", path, **kw)


# ---------- higher level helpers ----------
def new_document(name, public=False):
    d = post("/documents", {"name": name, "isPublic": public})
    return d["id"], d["defaultWorkspace"]["id"], d


def new_element(did, wid, kind, name):
    """kind: partstudio | featurestudio | assembly"""
    path = {"partstudio": "partstudios", "featurestudio": "featurestudios", "assembly": "assemblies"}[kind]
    e = post(f"/{path}/d/{did}/w/{wid}", {"name": name})
    return e["id"]


def set_feature_studio(did, wid, eid, source):
    cur = get(f"/featurestudios/d/{did}/w/{wid}/e/{eid}")
    r = post(f"/featurestudios/d/{did}/w/{wid}/e/{eid}", {
        "contents": source, "serializationVersion": cur.get("serializationVersion", "1.2.23"),
        "sourceMicroversion": cur["sourceMicroversion"], "rejectMicroversionSkew": False})
    return r


def fs_specs(did, wid, eid):
    return get(f"/featurestudios/d/{did}/w/{wid}/e/{eid}/featurespecs")


def current_microversion(did, wid):
    return get(f"/documents/d/{did}/w/{wid}/currentmicroversion")["microversion"]


def qty(pid, value):
    return {"btType": "BTMParameterQuantity-147", "isInteger": False, "value": float(value),
            "units": "", "expression": str(value), "parameterId": pid}


def add_feature(did, wid, eid, ftype, name, fs_eid, microversion, params):
    feat = {"btType": "BTMFeature-134", "featureType": ftype, "name": name,
            "namespace": f"e{fs_eid}::m{microversion}", "parameters": params}
    return post(f"/partstudios/d/{did}/w/{wid}/e/{eid}/features", {
        "feature": feat, "serializationVersion": "1.2.23", "sourceMicroversion": "", "rejectMicroversionSkew": False})


def feature_states(did, wid, eid):
    f = get(f"/partstudios/d/{did}/w/{wid}/e/{eid}/features")
    return f.get("featureStates", {}), f


def export_stl(did, wid, eid, path, part_ids=None, kind="partstudios"):
    params = {"units": "millimeter", "mode": "binary", "grouping": "false", "scale": 1,
              "angleTolerance": 0.04, "chordTolerance": 0.02}
    if part_ids:
        params["partIds"] = ",".join(part_ids)
    r = call("GET", f"/{kind}/d/{did}/w/{wid}/e/{eid}/stl", params=params,
             accept="application/vnd.onshape.v1+octet-stream", raw=True)
    open(path, "wb").write(r.content)
    return len(r.content)


def shaded_view(did, wid, eid, path, view_matrix, w=1400, h=1400, pixel_size=0.0, kind="partstudios", extra=None):
    """view_matrix: 12 numbers (3x4 row-major world->view). pixel_size in meters/pixel (0 = auto fit)."""
    params = {"viewMatrix": ",".join(str(x) for x in view_matrix), "outputHeight": h, "outputWidth": w,
              "pixelSize": pixel_size, "edges": "show"}
    if extra: params.update(extra)
    r = get(f"/{kind}/d/{did}/w/{wid}/e/{eid}/shadedviews", params=params)
    import base64
    open(path, "wb").write(base64.b64decode(r["images"][0]))
    return r


def view_matrix(az_deg, el_deg):
    """World->view rows [right, up, back] for a camera at azimuth/elevation looking at the origin (Z up)."""
    import math
    az, el = math.radians(az_deg), math.radians(el_deg)
    back = (math.cos(el) * math.cos(az), math.cos(el) * math.sin(az), math.sin(el))   # toward the viewer
    up0 = (0, 0, 1)
    right = (up0[1] * back[2] - up0[2] * back[1], up0[2] * back[0] - up0[0] * back[2], up0[0] * back[1] - up0[1] * back[0])
    n = math.sqrt(sum(c * c for c in right)); right = tuple(c / n for c in right)
    up = (back[1] * right[2] - back[2] * right[1], back[2] * right[0] - back[0] * right[2], back[0] * right[1] - back[1] * right[0])
    return list(right) + [0] + list(up) + [0] + list(back) + [0]


def export_step(did, wid, eid, path, kind="partstudios", name="export"):
    """Run a STEP translation without storing it in the document and download the result."""
    import time
    r = post(f"/{kind}/d/{did}/w/{wid}/e/{eid}/translations",
             {"formatName": "STEP", "storeInDocument": False, "translationName": name, "yAxisIsUp": False,
              "flattenAssemblies": False})
    tid = r["id"]
    for _ in range(120):
        s = get(f"/translations/{tid}")
        if s["requestState"] == "DONE":
            break
        if s["requestState"] == "FAILED":
            raise RuntimeError(s.get("failureReason"))
        time.sleep(3)
    fid = s["resultExternalDataIds"][0]
    resp = call("GET", f"/documents/d/{did}/externaldata/{fid}", accept="application/octet-stream", raw=True)
    open(path, "wb").write(resp.content)
    return len(resp.content)
