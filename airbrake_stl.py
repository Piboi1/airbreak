#!/usr/bin/env python3
"""
MIT Rocket Team (Prometheus) air brake -- CDR configuration -- STL generator.

Reconstructed from the MIT Rocket Team wiki page "Air Brakes"
(wikis.mit.edu/confluence/display/RocketTeam/Air+Brakes) and its CAD screenshots.

What is taken directly from the wiki:
  * Sliding-plate design, 4 aluminium 6061-T6 leaves, one system on the sustainer
  * Leaf: 3.5 in wide x 2.25 in extended length  -> 7.875 (~7.88) in^2 per leaf,
    31.5 in^2 total
  * Leaves slide in SLA-printed trays, one tray per opposing pair of leaves, each
    tray spanning the full diameter; the two trays are stacked 90 deg apart
  * Leaves driven by a "hex connector" (double crank on a hex shaft) and a
    "leaf connector" (link) per leaf, with washers at every joint
  * CDR stack: frames that hold the trays and screw into the mission-package tube,
    spacers between the frames acting as guide rails, a servo bulkhead and a large
    industrial servo on top
  * Airframe from the MIT RT tube standard, 6 in series: 5.823 in ID x 6.00 in OD

Everything else (plate thicknesses, frame widths, stack heights, crank/link
lengths, servo size) was NOT published and is estimated from the screenshots.
All of those values are collected in the PARAMETERS block below so they can be
corrected once the real drawings/CAD are available.

Usage:
    python3 airbrake_stl.py                   # extended, writes airbrake_assembly.stl
    python3 airbrake_stl.py --deploy 0        # fully retracted
    python3 airbrake_stl.py --deploy 0.5      # half deployed
    python3 airbrake_stl.py --tube            # also add the slotted airframe tube
    python3 airbrake_stl.py --parts           # also write one STL per part in ./parts
    python3 airbrake_stl.py --units in        # write in inches instead of mm

Onshape: Create > Import, pick the .stl, and set the units to match --units
(millimeter by default). The STL imports as a mesh body.

Pure Python 3 standard library; no dependencies.
"""

import argparse
import math
import os
import struct

# ---------------------------------------------------------------------------
# PARAMETERS (inches). "wiki" = published value, everything else = estimate.
# ---------------------------------------------------------------------------
TUBE_ID = 5.823            # wiki (MIT RT tube standard, 6 in series)
TUBE_OD = 6.000            # wiki
FRAME_OD = 5.800           # slip fit inside the tube
FRAME_RING_W = 0.40        # radial width of the frame rings

LEAF_W = 3.50              # wiki
LEAF_EXT = 2.25            # wiki: extension beyond the airframe skin
LEAF_T = 0.125             # 1/8 in 6061-T6 plate
LEAF_R = TUBE_OD / 2.0     # outer edge arc = skin radius, so the leaf is flush when retracted
LEAF_GAP = 0.03            # straight inner edge sits this far from the axis when retracted
LEAF_L = LEAF_R - LEAF_GAP # leaf length on its centreline
LEAF_NOTCH_R = 0.17        # semicircular notch in the inner edge that clears the hex shaft
LEAF_PIN_OFFSET = 0.30     # leaf-connector pin hole, from the inner edge, next to the notch
LEAF_LIP_W = 0.15          # raised stop arc: hits the inside of the airframe at full extension
LEAF_LIP_H = 0.06

TRAY_BASE_T = 0.10         # SLA tray floor
TRAY_RAIL_W = 0.20         # guide rail width on each side of the leaf channel
TRAY_CLEAR = 0.01          # side clearance between leaf and rail
TRAY_H = 0.45              # floor + channel (leaf, link, crank)

CONN_T = 0.125             # hex connector / leaf connector thickness
CONN_W = 0.30              # leaf connector (link) width
CRANK_W = 0.50             # hex connector arm width
WASHER_T = 0.02
WASHER_R = 0.17            # #10 washer
PIN_D = 0.19               # #10 shoulder bolt
HEX_AF = 0.25              # 1/4 in hex shaft (across flats)

CRANK_EXT_DEG = 90.0       # crank angle with leaves fully extended
CRANK_SWEEP_DEG = 90.0     # servo travel from retracted to extended

FRAME_T = 0.25             # frame plate thickness
SPACER_H = 0.75            # spacer ("guide rail") height between frames
SPACER_SPAN_DEG = 30.0

SERVO_BODY = (2.60, 1.50, 2.40)   # length, width, height of the industrial servo
SERVO_OUTPUT_OFFSET = 0.65        # output spline offset from the body centre
SERVO_EAR_LEN = 0.35              # mounting ear overhang at each end
SERVO_EAR_T = 0.12
SERVO_EAR_Z = 0.55                # ear height above the output face
BRACKET_H = 0.60                  # standoff height from bulkhead to output face

SEG = 96                   # facets per full circle


# ---------------------------------------------------------------------------
# Mesh primitives. A mesh is a list of triangles ((x,y,z),(x,y,z),(x,y,z)).
# ---------------------------------------------------------------------------
def _area2(poly):
    return sum(poly[i][0] * poly[(i + 1) % len(poly)][1] -
               poly[(i + 1) % len(poly)][0] * poly[i][1] for i in range(len(poly)))


def _cross(o, a, b):
    return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])


def _in_tri(p, a, b, c):
    return _cross(a, b, p) >= 0 and _cross(b, c, p) >= 0 and _cross(c, a, p) >= 0


def _dedupe(poly, eps=1e-9):
    out = []
    for p in poly:
        if not out or abs(p[0] - out[-1][0]) > eps or abs(p[1] - out[-1][1]) > eps:
            out.append(p)
    if len(out) > 1 and abs(out[0][0] - out[-1][0]) < eps and abs(out[0][1] - out[-1][1]) < eps:
        out.pop()
    return out


def triangulate(poly):
    """Ear-clip a simple polygon (CCW). Returns index triples."""
    idx = list(range(len(poly)))
    tris = []
    guard = 0
    while len(idx) > 3 and guard < 10 * len(poly) ** 2:
        guard += 1
        n = len(idx)
        for k in range(n):
            i0, i1, i2 = idx[(k - 1) % n], idx[k], idx[(k + 1) % n]
            a, b, c = poly[i0], poly[i1], poly[i2]
            if _cross(a, b, c) <= 1e-12:
                continue
            if any(_in_tri(poly[j], a, b, c) for j in idx if j not in (i0, i1, i2)):
                continue
            tris.append((i0, i1, i2))
            idx.pop(k)
            break
        else:
            raise ValueError("triangulation failed (polygon not simple?)")
    tris.append(tuple(idx))
    return tris


def extrude(poly, z0, z1):
    """Prism from a simple 2D polygon between z0 and z1."""
    poly = _dedupe(poly)
    if _area2(poly) < 0:
        poly = poly[::-1]
    out = []
    for i, j, k in triangulate(poly):
        a, b, c = poly[i], poly[j], poly[k]
        out.append(((a[0], a[1], z1), (b[0], b[1], z1), (c[0], c[1], z1)))
        out.append(((a[0], a[1], z0), (c[0], c[1], z0), (b[0], b[1], z0)))
    n = len(poly)
    for i in range(n):
        p, q = poly[i], poly[(i + 1) % n]
        a, b = (p[0], p[1], z0), (q[0], q[1], z0)
        c, d = (q[0], q[1], z1), (p[0], p[1], z1)
        out += [(a, b, c), (a, c, d)]
    return out


def arc(r, a0, a1, cx=0.0, cy=0.0, n=None):
    if n is None:
        n = max(2, int(math.ceil(abs(a1 - a0) / (2 * math.pi) * SEG)))
    return [(cx + r * math.cos(a0 + (a1 - a0) * t / n),
             cy + r * math.sin(a0 + (a1 - a0) * t / n)) for t in range(n + 1)]


def circle(r, cx=0.0, cy=0.0, n=SEG):
    return arc(r, 0, 2 * math.pi, cx, cy, n)[:-1]


def cylinder(r, z0, z1, cx=0.0, cy=0.0, n=SEG):
    return extrude(circle(r, cx, cy, n), z0, z1)


def annulus(r_in, r_out, z0, z1, a0=0.0, a1=2 * math.pi):
    """Ring or ring sector."""
    if abs(a1 - a0) < 2 * math.pi - 1e-9:
        return extrude(arc(r_out, a0, a1) + arc(r_in, a1, a0), z0, z1)
    o, i = circle(r_out), circle(r_in)
    out = []
    for k in range(len(o)):
        m = (k + 1) % len(o)
        for (p, q, top, bot) in ((o[k], o[m], z1, z0), (i[m], i[k], z1, z0)):
            out += [((p[0], p[1], bot), (q[0], q[1], bot), (q[0], q[1], top)),
                    ((p[0], p[1], bot), (q[0], q[1], top), (p[0], p[1], top))]
        for z, flip in ((z1, False), (z0, True)):
            a, b = (o[k][0], o[k][1], z), (o[m][0], o[m][1], z)
            c, d = (i[m][0], i[m][1], z), (i[k][0], i[k][1], z)
            t1, t2 = (a, b, c), (a, c, d)
            out += [t[::-1] if flip else t for t in (t1, t2)]
    return out


def box(x0, y0, x1, y1, z0, z1):
    return extrude([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], z0, z1)


def slot(p, q, w, z0, z1):
    """Stadium (rounded bar) from p to q, width w."""
    ang = math.atan2(q[1] - p[1], q[0] - p[0])
    r = w / 2
    return extrude(arc(r, ang + math.pi / 2, ang + 3 * math.pi / 2, *p, n=SEG // 2) +
                   arc(r, ang - math.pi / 2, ang + math.pi / 2, *q, n=SEG // 2), z0, z1)


def hexagon(af, z0, z1):
    r = af / math.sqrt(3)
    return extrude([(r * math.cos(k * math.pi / 3), r * math.sin(k * math.pi / 3))
                    for k in range(6)], z0, z1)


def rotz(mesh, ang):
    c, s = math.cos(ang), math.sin(ang)
    return [tuple((v[0] * c - v[1] * s, v[0] * s + v[1] * c, v[2]) for v in t) for t in mesh]


def move(mesh, dx=0.0, dy=0.0, dz=0.0):
    return [tuple((v[0] + dx, v[1] + dy, v[2] + dz) for v in t) for t in mesh]


def clip_x_to_circle(x, r):
    return math.sqrt(max(r * r - x * x, 0.0))


# ---------------------------------------------------------------------------
# Kinematics: slider-crank per leaf, solved so the leaf travels exactly LEAF_EXT.
# ---------------------------------------------------------------------------
def _pin_retracted():
    return LEAF_GAP + LEAF_PIN_OFFSET


def _slider(rc, l, phi):
    return rc * math.sin(phi) + math.sqrt(max(l * l - (rc * math.cos(phi)) ** 2, 0.0))


def shaft_clearance(rc, l, phi_r, phi_e):
    """Smallest gap between a leaf connector and the hex shaft over the stroke."""
    worst = float("inf")
    for i in range(201):
        phi = phi_r + (phi_e - phi_r) * i / 200
        p = (rc * math.cos(phi), rc * math.sin(phi))
        q = (0.0, _slider(rc, l, phi))
        dx, dy = q[0] - p[0], q[1] - p[1]
        t = max(0.0, min(1.0, -(p[0] * dx + p[1] * dy) / (dx * dx + dy * dy)))
        d = math.hypot(p[0] + t * dx, p[1] + t * dy)
        worst = min(worst, d - CONN_W / 2 - HEX_AF / math.sqrt(3))
    return worst


def solve_linkage():
    s_ret = _pin_retracted()
    s_ext = s_ret + LEAF_EXT
    phi_e = math.radians(CRANK_EXT_DEG)
    phi_r = phi_e - math.radians(CRANK_SWEEP_DEG)
    lo, hi = 0.05, s_ext / 2 - 1e-6       # crank radius; link = s_ext - rc at phi = 90
    for _ in range(200):
        rc = (lo + hi) / 2
        if _slider(rc, s_ext - rc, phi_r) > s_ret:
            lo = rc
        else:
            hi = rc
    rc = (lo + hi) / 2
    return rc, s_ext - rc, phi_r, phi_e


# ---------------------------------------------------------------------------
# Parts (built with the leaf axis along +/-Y, then rotated per tray level).
# ---------------------------------------------------------------------------
def leaf_outline():
    """Leaf in the local frame, extension along +Y, retracted position.

    Outer edge: arc on the airframe OD (flush when stowed). Inner edge: straight,
    meeting the opposite leaf of the pair at the axis, with a notch for the shaft.
    """
    hw = LEAF_W / 2
    top = [(x, clip_x_to_circle(x, LEAF_R)) for x in
           [hw - LEAF_W * i / 48 for i in range(49)]]              # outer arc, right->left
    notch = arc(LEAF_NOTCH_R, math.pi, 0.0, 0.0, LEAF_GAP, n=24)    # bites into the leaf
    return top + [(-hw, LEAF_GAP)] + notch + [(hw, LEAF_GAP)]


def leaf(z0, travel):
    m = extrude(leaf_outline(), z0, z0 + LEAF_T)
    hw = LEAF_W / 2
    wall = (TUBE_OD - TUBE_ID) / 2
    xs = [-hw + LEAF_W * i / 48 for i in range(49)]
    stop = [(x, clip_x_to_circle(x, LEAF_R) - LEAF_EXT - wall) for x in xs]
    back = [(x, max(y - LEAF_LIP_W, LEAF_GAP)) for x, y in stop][::-1]
    m += extrude(stop[::-1] + back[::-1], z0 + LEAF_T, z0 + LEAF_T + LEAF_LIP_H)
    return move(m, dy=travel)


def tray(z0):
    """SLA tray: floor + two guide rails, full diameter, split at the shaft."""
    r = FRAME_OD / 2
    ch = LEAF_W / 2 + TRAY_CLEAR
    hw = ch + TRAY_RAIL_W
    fw = ch + TRAY_RAIL_W / 2      # floor runs under the rails so the shells overlap
    m = []
    for sgn in (1, -1):
        ends = [(x, sgn * clip_x_to_circle(x, r)) for x in
                [fw - 2 * fw * i / 24 for i in range(25)]]
        d = math.asin(0.01 / 0.22)   # the two halves overlap slightly at the split
        hole = [(x, sgn * y) for x, y in arc(0.22, math.pi + d, -d, n=16)]
        floor = ends + [(-fw, -sgn * 0.02)] + hole + [(fw, -sgn * 0.02)]
        m += extrude(floor, z0, z0 + TRAY_BASE_T)
    for x0, x1 in ((-hw, -ch), (ch, hw)):
        ya, yb = clip_x_to_circle(x0, r), clip_x_to_circle(x1, r)
        rail = [(x0, -ya), (x1, -yb), (x1, yb), (x0, ya)]
        m += extrude(rail, z0, z0 + TRAY_H)
    return m


def tray_frame(z0):
    """Frame ring that holds a tray (open where the tray passes)."""
    hw = LEAF_W / 2 + TRAY_CLEAR + TRAY_RAIL_W
    a = math.acos(hw / (FRAME_OD / 2))
    r0 = FRAME_OD / 2 - FRAME_RING_W
    return (annulus(r0, FRAME_OD / 2, z0, z0 + TRAY_H, -a, a) +
            annulus(r0, FRAME_OD / 2, z0, z0 + TRAY_H, math.pi - a, math.pi + a))


def connectors(z_leaf_top, phi, rc, l, travel):
    """Hex connector (double crank) + two leaf connectors + pins/washers."""
    m = []
    zl0 = z_leaf_top + WASHER_T
    zl1 = zl0 + CONN_T
    zc0 = zl1 + WASHER_T
    zc1 = zc0 + CONN_T
    p = (rc * math.cos(phi), rc * math.sin(phi))
    m += slot(p, (-p[0], -p[1]), CRANK_W, zc0, zc1)                 # hex connector
    m += cylinder(0.30, zc0, zc1)                                   # hub
    s = _pin_retracted() + travel
    for sgn in (1, -1):
        cp = (sgn * p[0], sgn * p[1])
        lp = (0.0, sgn * s)
        m += slot(cp, lp, CONN_W, zl0, zl1)                         # leaf connector
        m += cylinder(PIN_D / 2, z_leaf_top - LEAF_T - LEAF_LIP_H, zl1 + 0.08, *lp, n=24)
        m += cylinder(PIN_D / 2, zl0, zc1 + 0.08, *cp, n=24)
        m += move(annulus(PIN_D / 2, WASHER_R, z_leaf_top, zl0), *lp)
        m += move(annulus(PIN_D / 2, WASHER_R, zl1, zc0), *cp)
    return m


def frame_spoked(z0, n_spokes=6):
    """Bottom frame (mounts to the mission-package tube), spoked / trussed."""
    r1 = FRAME_OD / 2
    r0 = r1 - FRAME_RING_W
    m = annulus(r0, r1, z0, z0 + FRAME_T) + annulus(0.16, 0.60, z0, z0 + FRAME_T)
    for k in range(n_spokes):
        a = 2 * math.pi * k / n_spokes + math.pi / n_spokes
        b = 2 * math.pi * (k + 1) / n_spokes + math.pi / n_spokes
        p0 = (0.45 * math.cos(a), 0.45 * math.sin(a))
        p1 = ((r0 + 0.1) * math.cos(a), (r0 + 0.1) * math.sin(a))
        p2 = ((r0 + 0.1) * math.cos(b), (r0 + 0.1) * math.sin(b))
        m += slot(p0, p1, 0.22, z0, z0 + FRAME_T)
        m += slot(p1, ((p1[0] + p2[0]) * 0.35, (p1[1] + p2[1]) * 0.35), 0.18, z0, z0 + FRAME_T)
    return m


def frame_barred(z0, bar_x=0.85, bar_w=0.35):
    """Frame ring with two parallel cross bars and a centre hub."""
    r1 = FRAME_OD / 2
    r0 = r1 - FRAME_RING_W
    m = annulus(r0, r1, z0, z0 + FRAME_T) + annulus(0.16, 0.50, z0, z0 + FRAME_T)
    for x in (-bar_x, bar_x):
        y = clip_x_to_circle(abs(x) + bar_w / 2, r0 + 0.1)
        m += box(x - bar_w / 2, -y, x + bar_w / 2, y, z0, z0 + FRAME_T)
    m += box(-bar_x, -0.15, -0.45, 0.15, z0, z0 + FRAME_T)
    m += box(0.45, -0.15, bar_x, 0.15, z0, z0 + FRAME_T)
    return m


def spacers(z0, z1, rot):
    r1 = FRAME_OD / 2
    r0 = r1 - FRAME_RING_W
    half = math.radians(SPACER_SPAN_DEG) / 2
    m = []
    for k in range(4):
        a = rot + math.pi / 4 + k * math.pi / 2
        m += annulus(r0, r1, z0, z1, a - half, a + half)
    return m


def servo(z_out):
    """Industrial servo, output face down, spline on the system axis."""
    L, W, H = SERVO_BODY
    cx = SERVO_OUTPUT_OFFSET
    m = box(cx - L / 2, -W / 2, cx + L / 2, W / 2, z_out, z_out + H)
    ze = z_out + SERVO_EAR_Z
    m += box(cx - L / 2 - SERVO_EAR_LEN, -W / 2, cx + L / 2 + SERVO_EAR_LEN, W / 2,
             ze, ze + SERVO_EAR_T)
    for i in range(9):                                              # heat-sink fins
        z = z_out + H * 0.35 + i * (H * 0.6 / 9)
        m += box(cx - L / 2 + 0.25, -W / 2 - 0.10, cx + L / 2 - 0.25, W / 2 + 0.10,
                 z, z + 0.08)
    m += box(cx - L / 2 + 0.3, -W / 2 + 0.2, cx + L / 2 - 0.3, W / 2 - 0.2,
             z_out + H, z_out + H + 0.12)                           # cap
    m += cylinder(0.35, z_out - 0.12, z_out)                        # output boss
    return m


def servo_bracket(z0, z_out):
    L, W, _ = SERVO_BODY
    cx = SERVO_OUTPUT_OFFSET
    ze = z_out + SERVO_EAR_Z
    m = []
    for sx in (-1, 1):
        x = cx + sx * (L / 2 + SERVO_EAR_LEN / 2)
        for sy in (-1, 1):
            m += cylinder(0.12, z0, ze, x, sy * (W / 2 - 0.25), n=24)
        m += box(x - 0.2, -W / 2, x + 0.2, W / 2, z0, z0 + 0.12)
    return m


def tube_with_slots(z_levels, z0, z1):
    """Mission-package tube, slotted where the leaves pass through."""
    ri, ro = TUBE_ID / 2, TUBE_OD / 2
    half = math.asin((LEAF_W / 2 + 0.02) / ro)
    cuts = sorted(z_levels, key=lambda t: t[0])
    m = []
    z = z0
    for (sz0, sz1, rot) in cuts:
        if sz0 > z:
            m += annulus(ri, ro, z, sz0)
        for k in range(2):
            c = rot + math.pi / 2 + k * math.pi
            m += annulus(ri, ro, sz0, sz1, c + half, c + math.pi - half)
        z = sz1
    m += annulus(ri, ro, z, z1)
    return m


# ---------------------------------------------------------------------------
# Assembly
# ---------------------------------------------------------------------------
def build(deploy, with_tube):
    rc, l, phi_r, phi_e = solve_linkage()
    phi = phi_r + (phi_e - phi_r) * deploy
    travel = _slider(rc, l, phi) - _pin_retracted()

    parts = {}
    z = 0.0
    parts["frame_bottom"] = frame_spoked(z)
    z += FRAME_T

    tube_slots = []
    for level, rot in (("A", 0.0), ("B", math.pi / 2)):
        zt = z
        parts["tray_frame_" + level] = rotz(tray_frame(zt), rot)
        parts["tray_" + level] = rotz(tray(zt), rot)
        zl = zt + TRAY_BASE_T
        for sgn, tag in ((1, "1"), (-1, "2")):
            parts["leaf_%s%s" % (level, tag)] = rotz(rotz(leaf(zl, travel), 0 if sgn > 0 else math.pi), rot)
        parts["connectors_" + level] = rotz(connectors(zl + LEAF_T, phi, rc, l, travel), rot)
        tube_slots.append((zl - 0.02, zl + LEAF_T + LEAF_LIP_H + 0.02, rot))
        z = zt + TRAY_H
        parts["spacers_" + level] = spacers(z, z + SPACER_H, rot)
        z += SPACER_H
        parts["frame_" + ("middle" if level == "A" else "servo_bulkhead")] = frame_barred(z)
        z += FRAME_T

    z_out = z + BRACKET_H
    parts["servo_bracket"] = servo_bracket(z, z_out)
    parts["servo"] = servo(z_out)
    parts["hex_shaft"] = hexagon(HEX_AF, 0.0, z_out - 0.12)
    parts["shaft_coupler"] = cylinder(0.30, z_out - 0.55, z_out - 0.12)
    if with_tube:
        parts["airframe_tube"] = tube_with_slots(tube_slots, -0.5, z_out + SERVO_BODY[2] + 0.5)
    info = dict(shaft_clearance=shaft_clearance(rc, l, phi_r, phi_e), crank_radius=rc, link_length=l, crank_angle_deg=math.degrees(phi),
                leaf_travel=travel, stack_height=z_out + SERVO_BODY[2] + 0.12)
    return parts, info


def write_stl(path, mesh, scale, name):
    with open(path, "wb") as f:
        f.write(name.encode()[:80].ljust(80, b" "))
        f.write(struct.pack("<I", len(mesh)))
        for a, b, c in mesh:
            ux, uy, uz = b[0] - a[0], b[1] - a[1], b[2] - a[2]
            vx, vy, vz = c[0] - a[0], c[1] - a[1], c[2] - a[2]
            nx, ny, nz = uy * vz - uz * vy, uz * vx - ux * vz, ux * vy - uy * vx
            n = math.sqrt(nx * nx + ny * ny + nz * nz) or 1.0
            f.write(struct.pack("<12fH", nx / n, ny / n, nz / n,
                                *(k * scale for k in a), *(k * scale for k in b),
                                *(k * scale for k in c), 0))


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    ap.add_argument("--deploy", type=float, default=1.0, help="0 = retracted, 1 = fully extended")
    ap.add_argument("--tube", action="store_true", help="include the slotted airframe tube")
    ap.add_argument("--parts", action="store_true", help="also write one STL per part")
    ap.add_argument("--units", choices=("mm", "in"), default="mm")
    ap.add_argument("-o", "--output", default="airbrake_assembly.stl")
    args = ap.parse_args()

    deploy = min(max(args.deploy, 0.0), 1.0)
    parts, info = build(deploy, args.tube)
    scale = 25.4 if args.units == "mm" else 1.0

    everything = [t for m in parts.values() for t in m]
    write_stl(args.output, everything, scale, "MIT RT air brake CDR (%s)" % args.units)
    print("wrote %s  (%d triangles, units: %s)" % (args.output, len(everything), args.units))
    if args.parts:
        outdir = os.path.join(os.path.dirname(os.path.abspath(args.output)), "parts")
        os.makedirs(outdir, exist_ok=True)
        for name, mesh in parts.items():
            write_stl(os.path.join(outdir, name + ".stl"), mesh, scale, name)
        print("wrote %d part files to %s" % (len(parts), outdir))

    leaf_area = LEAF_W * LEAF_EXT
    print("leaf extended area: %.3f in^2 each, %.2f in^2 total" % (leaf_area, 4 * leaf_area))
    print("crank radius %.3f in, link %.3f in, crank angle %.1f deg, leaf travel %.3f in"
          % (info["crank_radius"], info["link_length"], info["crank_angle_deg"], info["leaf_travel"]))
    print("stack height %.2f in" % info["stack_height"])
    if info["shaft_clearance"] < 0:
        print("WARNING: leaf connector hits the hex shaft (%.3f in interference)"
              % -info["shaft_clearance"])
    else:
        print("leaf connector / shaft clearance %.3f in" % info["shaft_clearance"])


if __name__ == "__main__":
    main()
