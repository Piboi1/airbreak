#!/usr/bin/env python3
"""
MIT Rocket Team (Prometheus) air brake -- CDR configuration -- STL + STEP generator.

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
    spacers acting as guide rails, a servo bulkhead and a large industrial servo
  * Airframe from the MIT RT tube standard, 6 in series: 5.823 in ID x 6.00 in OD

Everything else (plate thicknesses, frame widths, stack heights, crank/link
lengths, servo size) was NOT published and is estimated from the screenshots.
All of those values are collected in the PARAMETERS block below.

Outputs:
    airbrake_assembly.step   exact B-rep assembly: one clean solid per part, true
                             arcs and cylinders, one occurrence per part instance
                             (open this one in Onshape / SolidWorks / Fusion)
    airbrake_assembly.stl    whole assembly as one triangle mesh
    print/<part>_xN.stl      one print-ready mesh per unique part, lying flat on
                             z = 0; N = how many the assembly needs

Usage:
    python3 airbrake_stl.py                   # extended
    python3 airbrake_stl.py --deploy 0        # fully retracted (0..1)
    python3 airbrake_stl.py --tube            # also add the slotted airframe tube
    python3 airbrake_stl.py --units in        # inches instead of mm

Pure Python 3 standard library; no dependencies.
"""

import argparse
import math
import os
import struct
import time

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
LEAF_NOTCH_R = 0.17        # semicircular notch in the inner edge that clears the hex shaft
LEAF_PIN = (0.40, 0.33)    # leaf-connector pin hole (x, y) in the leaf, beside the notch
LEAF_LIP_W = 0.10          # raised stop arc: hits the inside of the airframe at full extension
LEAF_LIP_H = 0.06
LEAF_LIP_INSET = 0.15      # lip stops short of the leaf's side edges

TRAY_FLOOR_T = 0.06        # SLA tray floor
TRAY_RAIL_W = 0.20         # guide rail on each side of the leaf channel
TRAY_CLEAR = 0.01          # side clearance between leaf and rail
TRAY_HOLE_R = 0.22         # shaft clearance in the tray floor
TRAY_LEDGE = 0.02          # floor ledge left around the outside of the rails

CONN_T = 0.125             # hex connector / leaf connector thickness
CONN_W = 0.30              # leaf connector (link) width
CRANK_W = 0.50             # hex connector width
WASHER_T = 0.02
WASHER_R = 0.17            # #10 washer
PIN_D = 0.19               # #10 shoulder bolt
HOLE_CLEAR = 0.005         # radial clearance on printed holes
HEX_AF = 0.25              # 1/4 in hex shaft (across flats)

CRANK_SWEEP_DEG = 90.0     # servo travel from retracted to extended; at full extension the
                           # crank pin, link and leaf pin line up (dead centre), so drag on
                           # the leaves cannot back-drive the servo

FRAME_T = 0.20             # bottom frame / servo bulkhead thickness
MID_FRAME_T = 0.125        # thin frame between the two trays
SPACER_H = 0.25            # guide spacers between the top tray and the servo bulkhead
SPACER_SPAN_DEG = 30.0

SERVO_BODY = (2.60, 1.50, 2.40)   # length, width, height of the industrial servo
SERVO_OUTPUT_OFFSET = 0.65        # output spline offset from the body centre
SERVO_EAR_LEN = 0.35              # mounting ear overhang at each end
SERVO_EAR_T = 0.12
SERVO_EAR_Z = 0.55                # ear height above the output face
SERVO_FINS = 9
BRACKET_H = 0.60                  # bulkhead top to servo output face
COUPLER_R = 0.30

SEG = 96                   # mesh facets per full circle (STL only; the STEP uses true arcs)

# Derived
TRAY_H = TRAY_FLOOR_T + LEAF_T + WASHER_T + CONN_T + WASHER_T + CONN_T + 0.03
CHANNEL_HW = LEAF_W / 2 + TRAY_CLEAR
TRAY_HW = CHANNEL_HW + TRAY_RAIL_W


# ---------------------------------------------------------------------------
# 2D profiles: closed loops of exact segments
#   ('L', p0, p1)              straight line
#   ('A', centre, r, a0, a1)   circular arc from angle a0 to a1 (CCW if a1 > a0)
# ---------------------------------------------------------------------------
def Ln(p, q):
    return ("L", (float(p[0]), float(p[1])), (float(q[0]), float(q[1])))


def Ar(c, r, a0, a1):
    return ("A", (float(c[0]), float(c[1])), float(r), float(a0), float(a1))


def seg_start(s):
    if s[0] == "L":
        return s[1]
    _, c, r, a0, _ = s
    return (c[0] + r * math.cos(a0), c[1] + r * math.sin(a0))


def seg_end(s):
    if s[0] == "L":
        return s[2]
    _, c, r, _, a1 = s
    return (c[0] + r * math.cos(a1), c[1] + r * math.sin(a1))


def seg_rev(s):
    return ("L", s[2], s[1]) if s[0] == "L" else ("A", s[1], s[2], s[4], s[3])


def seg_points(s):
    """Tessellation of a segment: start point included, end point excluded."""
    if s[0] == "L":
        return [s[1]]
    _, c, r, a0, a1 = s
    n = max(2, int(math.ceil(abs(a1 - a0) / (2 * math.pi) * SEG)))
    return [(c[0] + r * math.cos(a0 + (a1 - a0) * t / n),
             c[1] + r * math.sin(a0 + (a1 - a0) * t / n)) for t in range(n)]


def loop_poly(loop):
    return [p for s in loop for p in seg_points(s)]


def loop_rev(loop):
    return [seg_rev(s) for s in reversed(loop)]


def loop_xform(loop, ang=0.0, dx=0.0, dy=0.0):
    def tp(p):
        x, y = rot2(p[0], p[1], ang)
        return (x + dx, y + dy)
    out = []
    for s in loop:
        if s[0] == "L":
            out.append(Ln(tp(s[1]), tp(s[2])))
        else:
            out.append(Ar(tp(s[1]), s[2], s[3] + ang, s[4] + ang))
    return out


def poly_loop(pts):
    return [Ln(pts[i], pts[(i + 1) % len(pts)]) for i in range(len(pts))]


def circle_loop(r, cx=0.0, cy=0.0):
    return [Ar((cx, cy), r, 0.0, math.pi), Ar((cx, cy), r, math.pi, 2 * math.pi)]


def rect_loop(x0, y0, x1, y1):
    return poly_loop([(x0, y0), (x1, y0), (x1, y1), (x0, y1)])


def hex_loop(af, cx=0.0, cy=0.0):
    r = af / math.sqrt(3)
    return poly_loop([(cx + r * math.cos(k * math.pi / 3), cy + r * math.sin(k * math.pi / 3))
                      for k in range(6)])


def stadium_loop(p, q, w):
    ang = math.atan2(q[1] - p[1], q[0] - p[0])
    r = w / 2
    n = (-math.sin(ang) * r, math.cos(ang) * r)
    return [Ar(p, r, ang + math.pi / 2, ang + 3 * math.pi / 2),
            Ln((p[0] - n[0], p[1] - n[1]), (q[0] - n[0], q[1] - n[1])),
            Ar(q, r, ang - math.pi / 2, ang + math.pi / 2),
            Ln((q[0] + n[0], q[1] + n[1]), (p[0] + n[0], p[1] + n[1]))]


def sector_loop(r_in, r_out, a0, a1):
    return [Ar((0, 0), r_out, a0, a1),
            Ln((r_out * math.cos(a1), r_out * math.sin(a1)), (r_in * math.cos(a1), r_in * math.sin(a1))),
            Ar((0, 0), r_in, a1, a0),
            Ln((r_in * math.cos(a0), r_in * math.sin(a0)), (r_out * math.cos(a0), r_out * math.sin(a0)))]


def cy_(x, r):
    """y on a circle of radius r at abscissa x."""
    return math.sqrt(max(r * r - x * x, 0.0))


def rot2(x, y, a):
    return x * math.cos(a) - y * math.sin(a), x * math.sin(a) + y * math.cos(a)


def _area2(poly):
    return sum(poly[i][0] * poly[(i + 1) % len(poly)][1] -
               poly[(i + 1) % len(poly)][0] * poly[i][1] for i in range(len(poly)))


def _cross(o, a, b):
    return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])


def _inside(p, poly):
    inside = False
    for i in range(len(poly)):
        a, b = poly[i], poly[i - 1]
        if (a[1] > p[1]) != (b[1] > p[1]):
            if p[0] < a[0] + (p[1] - a[1]) * (b[0] - a[0]) / (b[1] - a[1]):
                inside = not inside
    return inside


# ---------------------------------------------------------------------------
# Triangulation (STL only): ear clipping with holes bridged in
# ---------------------------------------------------------------------------
def _segments_cross(p1, p2, q1, q2):
    d1, d2 = _cross(q1, q2, p1), _cross(q1, q2, p2)
    d3, d4 = _cross(p1, p2, q1), _cross(p1, p2, q2)
    return ((d1 > 1e-12 and d2 < -1e-12) or (d1 < -1e-12 and d2 > 1e-12)) and \
           ((d3 > 1e-12 and d4 < -1e-12) or (d3 < -1e-12 and d4 > 1e-12))


def _on_segment(p, a, b):
    if p == a or p == b or abs(_cross(a, b, p)) > 1e-12:
        return False
    return min(a[0], b[0]) - 1e-12 <= p[0] <= max(a[0], b[0]) + 1e-12 and \
        min(a[1], b[1]) - 1e-12 <= p[1] <= max(a[1], b[1]) + 1e-12


def _bridge_holes(outer, holes):
    poly = list(outer)
    pending = sorted(holes, key=lambda h: -max(p[0] for p in h))
    for n, h in enumerate(pending):
        m = max(range(len(h)), key=lambda i: h[i][0])
        M = h[m]
        edges = [(poly[i], poly[(i + 1) % len(poly)]) for i in range(len(poly))]
        for hh in pending[n:]:
            edges += [(hh[i], hh[(i + 1) % len(hh)]) for i in range(len(hh))]
        verts = [a for a, _ in edges]
        order = sorted(range(len(poly)),
                       key=lambda i: (poly[i][0] - M[0]) ** 2 + (poly[i][1] - M[1]) ** 2)
        pick = None
        for i in order:
            P = poly[i]
            mid = ((M[0] + P[0]) / 2, (M[1] + P[1]) / 2)
            if not _inside(mid, outer) or any(_inside(mid, hh) for hh in holes):
                continue
            if any(_on_segment(v, M, P) for v in verts):
                continue
            if not any(_segments_cross(M, P, a, b) for a, b in edges):
                pick = i
                break
        if pick is None:
            raise ValueError("could not bridge a hole")
        poly = poly[:pick + 1] + h[m:] + h[:m + 1] + poly[pick:]
    return poly


def triangulate(outer, holes=()):
    """outer CCW, holes CW. Returns 2D triangles (CCW)."""
    poly = _bridge_holes(outer, holes) if holes else list(outer)
    n = len(poly)
    nxt = [(i + 1) % n for i in range(n)]
    prv = [(i - 1) % n for i in range(n)]

    def convex(i):
        return _cross(poly[prv[i]], poly[i], poly[nxt[i]]) > 1e-12

    reflex = {i for i in range(n) if not convex(i)}

    def ear(i):
        if not convex(i):
            return False
        a, b, c = poly[prv[i]], poly[i], poly[nxt[i]]
        for j in reflex:
            p = poly[j]
            if p == a or p == b or p == c:
                continue
            if _cross(a, b, p) >= 0 and _cross(b, c, p) >= 0 and _cross(c, a, p) >= 0:
                return False
        return True

    tris = []
    count, i, stall = n, 0, 0
    while count > 3:
        if ear(i):
            a, c = prv[i], nxt[i]
            tris.append((poly[a], poly[i], poly[c]))
            nxt[a], prv[c] = c, a
            reflex.discard(i)
            for j in (a, c):
                if j in reflex and convex(j):
                    reflex.discard(j)
            count -= 1
            i, stall = c, 0
        else:
            i = nxt[i]
            stall += 1
            if stall > 2 * count:
                raise ValueError("triangulation failed")
    tris.append((poly[prv[i]], poly[i], poly[nxt[i]]))
    return [t for t in tris if abs(_cross(*t)) > 1e-14]


# ---------------------------------------------------------------------------
# Solids. A Body is a z-extrusion of a profile (outline + holes). Bodies can be
# stacked: a child on the top (or bottom) face either sits strictly inside the
# parent's face (a boss) or strictly contains it (a flange), so every part is a
# single connected solid with exact planar and cylindrical faces.
# ---------------------------------------------------------------------------
class Body:
    def __init__(self, outline, z0, z1, holes=(), top=(), bottom=()):
        self.outline = outline if _area2(loop_poly(outline)) > 0 else loop_rev(outline)
        self.holes = [h if _area2(loop_poly(h)) < 0 else loop_rev(h) for h in holes]
        self.z0, self.z1 = float(z0), float(z1)
        self.parent, self.side, self.outer = None, None, False
        self.top, self.bottom = list(top), list(bottom)
        for side, kids in (("top", self.top), ("bottom", self.bottom)):
            for k in kids:
                k.parent, k.side = self, side
                k.outer = _inside(loop_poly(self.outline)[0], loop_poly(k.outline))
                assert abs((k.z0 if side == "top" else k.z1) - (self.z1 if side == "top" else self.z0)) < 1e-9
            if any(k.outer for k in kids):
                assert len(kids) == 1, "a flange must be the only child on that face"
        for loop in [self.outline] + self.holes:
            for i, s in enumerate(loop):
                e, b = seg_end(s), seg_start(loop[(i + 1) % len(loop)])
                assert math.hypot(e[0] - b[0], e[1] - b[1]) < 1e-7, "open profile"

    def nodes(self):
        out = [self]
        for k in self.top + self.bottom:
            out += k.nodes()
        return out

    def cap(self, which):
        """Loops (by owner) of the planar face on this body's top/bottom, or None.
        Returns list of (owner_body, loop_index, level) where level is 'z1' or 'z0'."""
        up = which == "top"
        parent_here = self.parent is not None and self.side == ("bottom" if up else "top")
        kids = self.top if up else self.bottom
        mine = "z1" if up else "z0"
        other = "z0" if up else "z1"
        if parent_here:
            if not self.outer:
                return None
            refs = [(self, i, mine) for i in range(1 + len(self.holes))]
            return refs + [(self.parent, 0, other)]
        if kids and kids[0].outer:
            return None
        refs = [(self, i, mine) for i in range(1 + len(self.holes))]
        return refs + [(k, 0, other) for k in kids]


def body_loops(b):
    return [b.outline] + b.holes


class Part:
    def __init__(self, name, bodies, printable=True, note=""):
        self.name, self.bodies, self.printable, self.note = name, bodies, printable, note
        self._mesh = None

    def mesh(self):
        if self._mesh is None:
            self._mesh = [t for b in self.bodies for t in body_mesh(b)]
        return self._mesh


def body_mesh(root):
    out = []
    for N in root.nodes():
        for loop in body_loops(N):
            pts = loop_poly(loop)
            for i in range(len(pts)):
                s, e = pts[i], pts[(i + 1) % len(pts)]
                a, b = (s[0], s[1], N.z0), (e[0], e[1], N.z0)
                c, d = (e[0], e[1], N.z1), (s[0], s[1], N.z1)
                out += [(a, b, c), (a, c, d)]
        for which in ("top", "bottom"):
            refs = N.cap(which)
            if refs is None:
                continue
            z = N.z1 if which == "top" else N.z0
            polys = [loop_poly(body_loops(o)[i]) for o, i, _ in refs]
            outer, inner = polys[0], polys[1:]
            # loops owned by another body are the far side of the step: flip them
            inner = [p if o is N else p[::-1] for p, (o, _, _) in zip(inner, refs[1:])]
            for t in triangulate(outer, inner):
                tri = tuple((p[0], p[1], z) for p in t)
                out.append(tri if which == "top" else tri[::-1])
    return out


class Instance:
    """A part placed by a rotation about Z followed by a translation."""
    def __init__(self, part, angle=0.0, x=0.0, y=0.0, z=0.0, label=None):
        self.part, self.angle, self.pos = part, angle, (x, y, z)
        self.label = label or part.name

    def apply(self, v):
        x, y = rot2(v[0], v[1], self.angle)
        return (x + self.pos[0], y + self.pos[1], v[2] + self.pos[2])


# ---------------------------------------------------------------------------
# Kinematics: offset slider-crank per leaf, solved so the leaf travels LEAF_EXT.
# Crank pin at rc*(cos phi, sin phi); the leaf pin runs along the line x = e.
# ---------------------------------------------------------------------------
def _slider(rc, l, phi, e):
    dx = rc * math.cos(phi) - e
    return rc * math.sin(phi) + math.sqrt(max(l * l - dx * dx, 0.0))


def solve_linkage():
    """Crank radius rc and link length l such that the leaf pin travels exactly
    LEAF_EXT over CRANK_SWEEP_DEG, ending at dead centre (crank pin on x = e)."""
    e, s_ret = LEAF_PIN
    s_ext = s_ret + LEAF_EXT
    sweep = math.radians(CRANK_SWEEP_DEG)

    def geometry(rc):
        phi_e = math.acos(e / rc)
        return phi_e, s_ext - rc * math.sin(phi_e)

    def err(rc):
        phi_e, l = geometry(rc)
        return _slider(rc, l, phi_e - sweep, e) - s_ret

    lo, hi = e + 1e-6, CHANNEL_HW - CRANK_W / 2
    if err(lo) * err(hi) > 0:
        raise ValueError("no crank radius fits in the tray channel; adjust the linkage parameters")
    for _ in range(200):
        mid = (lo + hi) / 2
        if err(lo) * err(mid) <= 0:
            hi = mid
        else:
            lo = mid
    rc = (lo + hi) / 2
    phi_e, l = geometry(rc)
    return rc, l, phi_e - sweep, phi_e


def shaft_clearance(rc, l, phi_r, phi_e):
    """Smallest gap between a leaf connector and the hex shaft over the stroke."""
    e = LEAF_PIN[0]
    worst = float("inf")
    for i in range(201):
        phi = phi_r + (phi_e - phi_r) * i / 200
        p = (rc * math.cos(phi), rc * math.sin(phi))
        q = (e, _slider(rc, l, phi, e))
        dx, dy = q[0] - p[0], q[1] - p[1]
        t = max(0.0, min(1.0, -(p[0] * dx + p[1] * dy) / (dx * dx + dy * dy)))
        d = math.hypot(p[0] + t * dx, p[1] + t * dy)
        worst = min(worst, d - CONN_W / 2 - HEX_AF / math.sqrt(3))
    return worst


# ---------------------------------------------------------------------------
# Part geometry (local frames, bottom face on z = 0)
# ---------------------------------------------------------------------------
def pin_hole(x, y):
    return circle_loop(PIN_D / 2 + HOLE_CLEAR, x, y)


def hex_hole():
    return hex_loop(HEX_AF + 2 * HOLE_CLEAR)


def make_leaf():
    """Outer edge: arc on the airframe OD (flush when stowed). Inner edge: straight,
    meeting the opposite leaf at the axis, with a notch around the shaft. A raised
    stop lip hits the inside of the airframe at full extension."""
    hw = LEAF_W / 2
    a = math.atan2(cy_(hw, LEAF_R), hw)
    rn = LEAF_NOTCH_R
    outline = [Ar((0, 0), LEAF_R, a, math.pi - a),
               Ln((-hw, cy_(hw, LEAF_R)), (-hw, LEAF_GAP)),
               Ln((-hw, LEAF_GAP), (-rn, LEAF_GAP)),
               Ar((0, LEAF_GAP), rn, math.pi, 0.0),
               Ln((rn, LEAF_GAP), (hw, LEAF_GAP)),
               Ln((hw, LEAF_GAP), (hw, cy_(hw, LEAF_R)))]
    d = LEAF_EXT + (TUBE_OD - TUBE_ID) / 2        # stop arc = skin arc moved inboard
    xl = hw - LEAF_LIP_INSET
    c1, c2 = (0.0, -d), (0.0, -d - LEAF_LIP_W)
    b1 = math.atan2(cy_(xl, LEAF_R), xl)
    lip = [Ar(c1, LEAF_R, b1, math.pi - b1),
           Ln((-xl, c1[1] + cy_(xl, LEAF_R)), (-xl, c2[1] + cy_(xl, LEAF_R))),
           Ar(c2, LEAF_R, math.pi - b1, b1),
           Ln((xl, c2[1] + cy_(xl, LEAF_R)), (xl, c1[1] + cy_(xl, LEAF_R)))]
    assert c2[1] + cy_(xl, LEAF_R) > LEAF_GAP + 0.02, "stop lip runs off the leaf"
    body = Body(outline, 0, LEAF_T, [pin_hole(*LEAF_PIN)],
                top=[Body(lip, LEAF_T, LEAF_T + LEAF_LIP_H)])
    return Part("leaf", [body], note="6061-T6 1/8 in plate in the real build")


def _clipped_rect(x0, x1, r):
    """Region x0 <= x <= x1 inside a circle of radius r (ends are true arcs)."""
    a0, a1 = math.atan2(cy_(x1, r), x1), math.atan2(cy_(x0, r), x0)
    return [Ln((x1, -cy_(x1, r)), (x1, cy_(x1, r))),
            Ar((0, 0), r, a0, a1),
            Ln((x0, cy_(x0, r)), (x0, -cy_(x0, r))),
            Ar((0, 0), r, -a1, -a0)]


def make_tray():
    r = FRAME_OD / 2
    rails = [Body(_clipped_rect(x0, x1, r - TRAY_LEDGE), TRAY_FLOOR_T, TRAY_H)
             for x0, x1 in ((-TRAY_HW + TRAY_LEDGE, -CHANNEL_HW), (CHANNEL_HW, TRAY_HW - TRAY_LEDGE))]
    floor = Body(_clipped_rect(-TRAY_HW, TRAY_HW, r), 0, TRAY_FLOOR_T,
                 [circle_loop(TRAY_HOLE_R)], top=rails)
    return Part("tray", [floor], note="SLA resin in the real build")


def make_tray_frame():
    a = math.acos(TRAY_HW / (FRAME_OD / 2))
    r0, r1 = FRAME_OD / 2 - FRAME_RING_W, FRAME_OD / 2
    return Part("tray_frame", [Body(sector_loop(r0, r1, -a, a), 0, TRAY_H)],
                note="ring segment either side of each tray")


def make_mid_frame():
    r1 = FRAME_OD / 2
    return Part("frame_middle", [Body(circle_loop(r1), 0, MID_FRAME_T,
                                      [circle_loop(r1 - FRAME_RING_W)])])


def make_bottom_frame(n=6, spoke=0.30, hub=0.60):
    r1 = FRAME_OD / 2
    r0 = r1 - FRAME_RING_W
    holes = [hex_hole()]
    do, di = math.asin(spoke / 2 / r0), math.asin(spoke / 2 / hub)
    for k in range(n):
        a, b = 2 * math.pi * k / n, 2 * math.pi * (k + 1) / n
        pa_o, pb_o = (r0 * math.cos(a + do), r0 * math.sin(a + do)), (r0 * math.cos(b - do), r0 * math.sin(b - do))
        pa_i, pb_i = (hub * math.cos(a + di), hub * math.sin(a + di)), (hub * math.cos(b - di), hub * math.sin(b - di))
        holes.append([Ar((0, 0), r0, a + do, b - do), Ln(pb_o, pb_i),
                      Ar((0, 0), hub, b - di, a + di), Ln(pa_i, pa_o)])
    return Part("frame_bottom", [Body(circle_loop(r1), 0, FRAME_T, holes)],
                note="screws into the mission-package tube")


def make_bulkhead(bar_x=0.85, bar_w=0.35, hub=0.55, yb=0.15):
    r1 = FRAME_OD / 2
    r0 = r1 - FRAME_RING_W
    xo, xi = bar_x + bar_w / 2, bar_x - bar_w / 2
    holes = [circle_loop(COUPLER_R + 0.03)]
    ao = math.atan2(cy_(xo, r0), xo)
    side = [Ln((xo, -cy_(xo, r0)), (xo, cy_(xo, r0))), Ar((0, 0), r0, ao, -ao)]
    a0 = math.asin(yb / hub)
    xh = hub * math.cos(a0)
    ai = math.atan2(cy_(xi, r0), xi)
    mid = [Ln((-xi, yb), (-xh, yb)), Ar((0, 0), hub, math.pi - a0, a0), Ln((xh, yb), (xi, yb)),
           Ln((xi, yb), (xi, cy_(xi, r0))), Ar((0, 0), r0, ai, math.pi - ai),
           Ln((-xi, cy_(xi, r0)), (-xi, yb))]
    for ang in (0.0, math.pi):
        holes.append(loop_xform(side, ang))
        holes.append(loop_xform(mid, ang))
    return Part("servo_bulkhead", [Body(circle_loop(r1), 0, FRAME_T, holes)])


def make_spacer():
    r1 = FRAME_OD / 2
    h = math.radians(SPACER_SPAN_DEG) / 2
    return Part("spacer", [Body(sector_loop(r1 - FRAME_RING_W, r1, -h, h), 0, SPACER_H)],
                note="guide rails between the top tray and the servo bulkhead")


def make_hex_connector(rc):
    holes = [hex_hole(), pin_hole(rc, 0), pin_hole(-rc, 0)]
    return Part("hex_connector", [Body(stadium_loop((-rc, 0), (rc, 0), CRANK_W), 0, CONN_T, holes)])


def make_leaf_connector(l):
    return Part("leaf_connector", [Body(stadium_loop((0, 0), (l, 0), CONN_W), 0, CONN_T,
                                        [pin_hole(0, 0), pin_hole(l, 0)])])


def make_pin(length, name):
    return Part(name, [Body(circle_loop(PIN_D / 2), 0, length)], printable=False,
                note="#10 shoulder bolt")


def make_washer():
    return Part("washer", [Body(circle_loop(WASHER_R), 0, WASHER_T, [pin_hole(0, 0)])],
                printable=False, note="#10 washer")


def make_hex_shaft(length):
    return Part("hex_shaft", [Body(hex_loop(HEX_AF), 0, length)],
                note="or cut from 1/4 in steel hex stock")


def make_coupler(length):
    return Part("shaft_coupler", [Body(circle_loop(COUPLER_R), 0, length, [hex_hole()])],
                note="hex shaft to servo horn")


def make_servo():
    """One solid: body, mounting-ear flange, heat-sink fins, top cap, output boss."""
    L, W, H = SERVO_BODY
    cx = SERVO_OUTPUT_OFFSET
    body = rect_loop(cx - L / 2, -W / 2, cx + L / 2, W / 2)
    ears = rect_loop(cx - L / 2 - SERVO_EAR_LEN, -W / 2 - 0.02, cx + L / 2 + SERVO_EAR_LEN, W / 2 + 0.02)
    fin = rect_loop(cx - L / 2 - 0.08, -W / 2 - 0.10, cx + L / 2 + 0.08, W / 2 + 0.10)
    cap = rect_loop(cx - L / 2 + 0.3, -W / 2 + 0.2, cx + L / 2 - 0.3, W / 2 - 0.2)
    pitch = H * 0.6 / SERVO_FINS
    levels = [(ears, SERVO_EAR_Z, SERVO_EAR_Z + SERVO_EAR_T)]
    z = SERVO_EAR_Z + SERVO_EAR_T
    for i in range(SERVO_FINS):
        zf = H * 0.35 + i * pitch
        levels += [(body, z, zf), (fin, zf, zf + 0.08)]
        z = zf + 0.08
    levels.append((body, z, H))
    node = Body(cap, H, H + 0.12)
    for loop, z0, z1 in reversed(levels):
        node = Body(loop, z0, z1, top=[node])
    root = Body(body, 0, SERVO_EAR_Z, top=[node],
                bottom=[Body(circle_loop(0.35), -0.12, 0)])
    return Part("servo", [root], printable=False, note="industrial servo, ~1500 oz-in")


def make_bracket():
    W = SERVO_BODY[1]
    top = BRACKET_H + SERVO_EAR_Z
    posts = [Body(circle_loop(0.12, 0, sy * (W / 2 - 0.25)), 0.12, top) for sy in (-1, 1)]
    return Part("servo_bracket", [Body(rect_loop(-0.2, -W / 2, 0.2, W / 2), 0, 0.12, top=posts)],
                note="servo standoffs")


def make_tube(slots, z0, z1):
    ri, ro = TUBE_ID / 2, TUBE_OD / 2
    half = math.asin((LEAF_W / 2 + 0.02) / ro)
    bodies, z = [], z0
    for sz0, sz1, rot in sorted(slots):
        bodies.append(Body(circle_loop(ro), z, sz0, [circle_loop(ri)]))
        for k in range(2):
            c = rot + math.pi / 2 + k * math.pi
            bodies.append(Body(sector_loop(ri, ro, c + half, c + math.pi - half), sz0, sz1))
        z = sz1
    bodies.append(Body(circle_loop(ro), z, z1, [circle_loop(ri)]))
    return Part("airframe_tube", bodies, printable=False, note="mission-package tube")


# ---------------------------------------------------------------------------
# Assembly
# ---------------------------------------------------------------------------
def build(deploy, with_tube=False):
    rc, l, phi_r, phi_e = solve_linkage()
    phi = phi_r + (phi_e - phi_r) * deploy
    e = LEAF_PIN[0]
    s = _slider(rc, l, phi, e)
    travel = s - LEAF_PIN[1]

    leaf, tray, tframe = make_leaf(), make_tray(), make_tray_frame()
    hexc, link, washer = make_hex_connector(rc), make_leaf_connector(l), make_washer()
    leaf_pin = make_pin(LEAF_T + WASHER_T + CONN_T, "pin_leaf")
    crank_pin = make_pin(CONN_T + WASHER_T + CONN_T, "pin_crank")

    inst = []
    z = 0.0
    inst.append(Instance(make_bottom_frame(), z=z))
    z += FRAME_T
    tube_slots = []
    for level, rot in (("A", 0.0), ("B", math.pi / 2)):
        inst.append(Instance(tframe, rot, z=z, label="tray_frame_%s1" % level))
        inst.append(Instance(tframe, rot + math.pi, z=z, label="tray_frame_%s2" % level))
        inst.append(Instance(tray, rot, z=z, label="tray_" + level))
        zf = z + TRAY_FLOOR_T                 # leaf bottom
        zl = zf + LEAF_T + WASHER_T           # leaf connector bottom
        zc = zl + CONN_T + WASHER_T           # hex connector bottom
        inst.append(Instance(hexc, rot + phi, z=zc, label="hex_connector_" + level))
        for k, sgn in enumerate((1, -1)):
            a = rot + (0 if sgn > 0 else math.pi)
            tag = "%s%d" % (level, k + 1)
            dx, dy = rot2(0, travel, a)
            lp = rot2(e, s, a)                                   # leaf pin
            c = rot2(rc * math.cos(phi), rc * math.sin(phi), a)  # crank pin
            ang = math.atan2(lp[1] - c[1], lp[0] - c[0])
            inst.append(Instance(leaf, a, dx, dy, zf, label="leaf_" + tag))
            inst.append(Instance(link, ang, c[0], c[1], zl, label="leaf_connector_" + tag))
            inst.append(Instance(leaf_pin, 0, lp[0], lp[1], zf, label="pin_leaf_" + tag))
            inst.append(Instance(crank_pin, 0, c[0], c[1], zl, label="pin_crank_" + tag))
            inst.append(Instance(washer, 0, lp[0], lp[1], zf + LEAF_T, label="washer_leaf_" + tag))
            inst.append(Instance(washer, 0, c[0], c[1], zl + CONN_T, label="washer_crank_" + tag))
        tube_slots.append((zf - 0.02, zf + LEAF_T + LEAF_LIP_H + 0.02, rot))
        z += TRAY_H
        if level == "A":
            inst.append(Instance(make_mid_frame(), z=z))
            z += MID_FRAME_T
    spacer = make_spacer()
    for k in range(4):
        inst.append(Instance(spacer, math.pi / 4 + k * math.pi / 2, z=z, label="spacer_%d" % (k + 1)))
    z += SPACER_H
    inst.append(Instance(make_bulkhead(), z=z))
    z_bulk = z
    z += FRAME_T
    z_out = z + BRACKET_H
    bracket = make_bracket()
    for k, sx in enumerate((-1, 1)):
        x = SERVO_OUTPUT_OFFSET + sx * (SERVO_BODY[0] / 2 + SERVO_EAR_LEN / 2)
        inst.append(Instance(bracket, 0, x, 0, z, label="servo_bracket_%d" % (k + 1)))
    inst.append(Instance(make_servo(), z=z_out))
    inst.append(Instance(make_hex_shaft(z_out - 0.12 - 0.05), z=0.0))
    inst.append(Instance(make_coupler(z_out - 0.12 - z_bulk), z=z_bulk))
    if with_tube:
        inst.append(Instance(make_tube(tube_slots, -0.5, z_out + SERVO_BODY[2] + 0.5)))

    info = dict(crank_radius=rc, link_length=l, crank_angle_deg=math.degrees(phi),
                leaf_travel=travel, stack_height=z_out + SERVO_BODY[2] + 0.12,
                leaf_pitch=TRAY_H + MID_FRAME_T,
                shaft_clearance=shaft_clearance(rc, l, phi_r, phi_e))
    return inst, info


# ---------------------------------------------------------------------------
# STL
# ---------------------------------------------------------------------------
def write_stl(path, tris, scale, name):
    with open(path, "wb") as f:
        f.write(name.encode()[:80].ljust(80, b" "))
        f.write(struct.pack("<I", len(tris)))
        for a, b, c in tris:
            ux, uy, uz = b[0] - a[0], b[1] - a[1], b[2] - a[2]
            vx, vy, vz = c[0] - a[0], c[1] - a[1], c[2] - a[2]
            nx, ny, nz = uy * vz - uz * vy, uz * vx - ux * vz, ux * vy - uy * vx
            n = math.sqrt(nx * nx + ny * ny + nz * nz) or 1.0
            f.write(struct.pack("<12fH", nx / n, ny / n, nz / n,
                                *(k * scale for k in a), *(k * scale for k in b),
                                *(k * scale for k in c), 0))


def assembly_mesh(instances):
    return [tuple(i.apply(v) for v in t) for i in instances for t in i.part.mesh()]


def write_print_parts(outdir, instances, scale):
    counts, parts = {}, {}
    for i in instances:
        counts[i.part.name] = counts.get(i.part.name, 0) + 1
        parts[i.part.name] = i.part
    os.makedirs(outdir, exist_ok=True)
    written = []
    for name, part in parts.items():
        if not part.printable:
            continue
        mesh = part.mesh()
        xs = [v[0] for t in mesh for v in t]
        ys = [v[1] for t in mesh for v in t]
        zs = [v[2] for t in mesh for v in t]
        dx, dy, dz = -(min(xs) + max(xs)) / 2, -(min(ys) + max(ys)) / 2, -min(zs)
        mesh = [tuple((v[0] + dx, v[1] + dy, v[2] + dz) for v in t) for t in mesh]
        fn = "%s_x%d.stl" % (name, counts[name])
        write_stl(os.path.join(outdir, fn), mesh, scale, name)
        written.append((fn, part.note))
    hardware = [(n, counts[n], p.note) for n, p in parts.items() if not p.printable]
    return written, hardware


# ---------------------------------------------------------------------------
# STEP (AP214). One product per part, one occurrence per instance, so CAD tools
# import it as an assembly. Each part is one MANIFOLD_SOLID_BREP with exact
# geometry: PLANE / CYLINDRICAL_SURFACE faces, LINE / CIRCLE edges.
# ---------------------------------------------------------------------------
class _Step:
    def __init__(self, scale):
        self.lines, self.scale = [], scale

    def add(self, s):
        self.lines.append(s)
        return "#%d" % len(self.lines)

    @staticmethod
    def r(v):
        if abs(v) < 1e-12:
            v = 0.0
        s = "%.10g" % v
        if "e" in s:
            m, x = s.split("e")
            return (m if "." in m else m + ".") + "E" + x
        return s if "." in s else s + "."

    def pt(self, p):
        return self.add("CARTESIAN_POINT('',(%s));" % ",".join(self.r(c * self.scale) for c in p))

    def dir(self, d):
        return self.add("DIRECTION('',(%s));" % ",".join(self.r(c) for c in d))

    def axis(self, p, z=(0.0, 0.0, 1.0), x=(1.0, 0.0, 0.0)):
        return self.add("AXIS2_PLACEMENT_3D('',%s,%s,%s);" % (self.pt(p), self.dir(z), self.dir(x)))

    def line_edge(self, pa, pb, va, vb):
        d = [pb[k] - pa[k] for k in range(3)]
        ln = math.sqrt(sum(c * c for c in d))
        vec = self.add("VECTOR('',%s,%s);" % (self.dir([c / ln for c in d]), self.r(ln * self.scale)))
        line = self.add("LINE('',%s,%s);" % (self.pt(pa), vec))
        return self.add("EDGE_CURVE('',%s,%s,%s,.T.);" % (va, vb, line))

    def arc_edge(self, seg, z, va, vb):
        _, c, r, a0, a1 = seg
        circ = self.add("CIRCLE('',%s,%s);" % (self.axis((c[0], c[1], z)), self.r(r * self.scale)))
        return self.add("EDGE_CURVE('',%s,%s,%s,%s);" % (va, vb, circ, ".T." if a1 > a0 else ".F."))

    def face(self, loops, surface, sense=True):
        bounds = []
        for k, oes in enumerate(loops):
            refs = [self.add("ORIENTED_EDGE('',*,*,%s,%s);" % (e, ".T." if fwd else ".F."))
                    for e, fwd in oes]
            el = self.add("EDGE_LOOP('',(%s));" % ",".join(refs))
            kind = "FACE_OUTER_BOUND" if k == 0 else "FACE_BOUND"
            bounds.append(self.add("%s('',%s,.T.);" % (kind, el)))
        return self.add("ADVANCED_FACE('',(%s),%s,%s);" % (",".join(bounds), surface,
                                                           ".T." if sense else ".F."))

    def body(self, root, name):
        """Write one connected solid (a Body tree) and return its MANIFOLD_SOLID_BREP."""
        edges = {}   # (id(node), loop index) -> dict(z0=[...], z1=[...], v=[...])
        faces = []
        for N in root.nodes():
            for li, loop in enumerate(body_loops(N)):
                n = len(loop)
                starts = [seg_start(s) for s in loop]
                vb = [self.add("VERTEX_POINT('',%s);" % self.pt((p[0], p[1], N.z0))) for p in starts]
                vt = [self.add("VERTEX_POINT('',%s);" % self.pt((p[0], p[1], N.z1))) for p in starts]
                eb, et, ev = [], [], []
                for i, s in enumerate(loop):
                    j = (i + 1) % n
                    for z, vv, lst in ((N.z0, vb, eb), (N.z1, vt, et)):
                        if s[0] == "L":
                            lst.append(self.line_edge((s[1][0], s[1][1], z), (s[2][0], s[2][1], z), vv[i], vv[j]))
                        else:
                            lst.append(self.arc_edge(s, z, vv[i], vv[j]))
                    p = starts[i]
                    ev.append(self.line_edge((p[0], p[1], N.z0), (p[0], p[1], N.z1), vb[i], vt[i]))
                edges[(id(N), li)] = {"z0": eb, "z1": et}
                for i, s in enumerate(loop):
                    j = (i + 1) % n
                    loop_edges = [(eb[i], True), (ev[j], True), (et[i], False), (ev[i], False)]
                    if s[0] == "L":
                        (x0, y0), (x1, y1) = s[1], s[2]
                        dx, dy = x1 - x0, y1 - y0
                        ln = math.hypot(dx, dy)
                        surf = self.add("PLANE('',%s);" % self.axis((x0, y0, N.z0), (dy / ln, -dx / ln, 0.0),
                                                                    (dx / ln, dy / ln, 0.0)))
                        faces.append(self.face([loop_edges], surf))
                    else:
                        _, c, r, a0, a1 = s
                        surf = self.add("CYLINDRICAL_SURFACE('',%s,%s);"
                                        % (self.axis((c[0], c[1], N.z0)), self.r(r * self.scale)))
                        faces.append(self.face([loop_edges], surf, sense=a1 > a0))
        for N in root.nodes():
            for which in ("top", "bottom"):
                refs = N.cap(which)
                if refs is None:
                    continue
                up = which == "top"
                loops = []
                for owner, li, level in refs:
                    es = edges[(id(owner), li)][level]
                    # the face's own loops run forward seen from outside; loops borrowed
                    # from the body across the step run the other way
                    fwd = (owner is N) == up
                    loops.append([(e, True) for e in es] if fwd else
                                 [(e, False) for e in reversed(es)])
                z = N.z1 if up else N.z0
                surf = self.add("PLANE('',%s);" % self.axis((0.0, 0.0, z), (0.0, 0.0, 1.0 if up else -1.0)))
                faces.append(self.face(loops, surf))
        shell = self.add("CLOSED_SHELL('',(%s));" % ",".join(faces))
        return self.add("MANIFOLD_SOLID_BREP('%s',%s);" % (name, shell))


def write_step(path, instances, scale):
    st = _Step(scale)
    app = st.add("APPLICATION_CONTEXT('core data for automotive mechanical design processes');")
    st.add("APPLICATION_PROTOCOL_DEFINITION('international standard','automotive_design',2000,%s);" % app)
    pctx = st.add("PRODUCT_CONTEXT('',%s,'mechanical');" % app)
    pdctx = st.add("PRODUCT_DEFINITION_CONTEXT('part definition',%s,'design');" % app)
    if scale == 1.0:
        m = st.add("(LENGTH_UNIT()NAMED_UNIT(*)SI_UNIT(.MILLI.,.METRE.));")
        lmu = st.add("LENGTH_MEASURE_WITH_UNIT(LENGTH_MEASURE(25.4),%s);" % m)
        dim = st.add("DIMENSIONAL_EXPONENTS(1.,0.,0.,0.,0.,0.,0.);")
        lu = st.add("(CONVERSION_BASED_UNIT('INCH',%s)LENGTH_UNIT()NAMED_UNIT(%s));" % (lmu, dim))
    else:
        lu = st.add("(LENGTH_UNIT()NAMED_UNIT(*)SI_UNIT(.MILLI.,.METRE.));")
    au = st.add("(NAMED_UNIT(*)PLANE_ANGLE_UNIT()SI_UNIT($,.RADIAN.));")
    su = st.add("(NAMED_UNIT(*)SI_UNIT($,.STERADIAN.)SOLID_ANGLE_UNIT());")
    unc = st.add("UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(1.E-05),%s,'distance_accuracy_value','');" % lu)
    ctx = st.add("(GEOMETRIC_REPRESENTATION_CONTEXT(3)GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT((%s))"
                 "GLOBAL_UNIT_ASSIGNED_CONTEXT((%s,%s,%s))REPRESENTATION_CONTEXT('Context3D','3D'));"
                 % (unc, lu, au, su))

    def product(name):
        p = st.add("PRODUCT('%s','%s','',(%s));" % (name, name, pctx))
        st.add("PRODUCT_RELATED_PRODUCT_CATEGORY('part',$,(%s));" % p)
        f = st.add("PRODUCT_DEFINITION_FORMATION('','',%s);" % p)
        pd = st.add("PRODUCT_DEFINITION('design','',%s,%s);" % (f, pdctx))
        return pd, st.add("PRODUCT_DEFINITION_SHAPE('','',%s);" % pd)

    root_pd, root_pds = product("airbrake_assembly")
    reps = {}
    for inst in instances:
        part = inst.part
        if part.name in reps:
            continue
        pd, pds = product(part.name)
        origin = st.axis((0.0, 0.0, 0.0))
        solids = [st.body(b, part.name) for b in part.bodies]
        rep = st.add("ADVANCED_BREP_SHAPE_REPRESENTATION('%s',(%s),%s);"
                     % (part.name, ",".join([origin] + solids), ctx))
        st.add("SHAPE_DEFINITION_REPRESENTATION(%s,%s);" % (pds, rep))
        reps[part.name] = (pd, rep, origin)

    root_origin = st.axis((0.0, 0.0, 0.0))
    places = [st.axis(i.pos, (0.0, 0.0, 1.0), (math.cos(i.angle), math.sin(i.angle), 0.0))
              for i in instances]
    root_rep = st.add("SHAPE_REPRESENTATION('airbrake_assembly',(%s),%s);"
                      % (",".join([root_origin] + places), ctx))
    st.add("SHAPE_DEFINITION_REPRESENTATION(%s,%s);" % (root_pds, root_rep))
    for k, inst in enumerate(instances):
        pd, rep, origin = reps[inst.part.name]
        nauo = st.add("NEXT_ASSEMBLY_USAGE_OCCURRENCE('%d','%s','',%s,%s,$);"
                      % (k + 1, inst.label, root_pd, pd))
        pds = st.add("PRODUCT_DEFINITION_SHAPE('','',%s);" % nauo)
        idt = st.add("ITEM_DEFINED_TRANSFORMATION('','',%s,%s);" % (origin, places[k]))
        rr = st.add("(REPRESENTATION_RELATIONSHIP('','',%s,%s)"
                    "REPRESENTATION_RELATIONSHIP_WITH_TRANSFORMATION(%s)"
                    "SHAPE_REPRESENTATION_RELATIONSHIP());" % (rep, root_rep, idt))
        st.add("CONTEXT_DEPENDENT_SHAPE_REPRESENTATION(%s,%s);" % (rr, pds))

    with open(path, "w") as f:
        f.write("ISO-10303-21;\nHEADER;\n")
        f.write("FILE_DESCRIPTION(('MIT Rocket Team air brake reconstruction'),'2;1');\n")
        f.write("FILE_NAME('%s','%s',(''),(''),'airbrake_stl.py','airbrake_stl.py','');\n"
                % (os.path.basename(path), time.strftime("%Y-%m-%dT%H:%M:%S")))
        f.write("FILE_SCHEMA(('AUTOMOTIVE_DESIGN { 1 0 10303 214 1 1 1 1 }'));\nENDSEC;\nDATA;\n")
        for n, line in enumerate(st.lines, 1):
            f.write("#%d=%s\n" % (n, line))
        f.write("ENDSEC;\nEND-ISO-10303-21;\n")


# ---------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser(description="MIT RT air brake STL/STEP generator")
    ap.add_argument("--deploy", type=float, default=1.0, help="0 = retracted, 1 = fully extended")
    ap.add_argument("--tube", action="store_true", help="include the slotted airframe tube")
    ap.add_argument("--units", choices=("mm", "in"), default="mm")
    ap.add_argument("--outdir", default=".", help="where to write the files")
    ap.add_argument("--no-step", action="store_true", help="skip the STEP assembly")
    ap.add_argument("--no-print", action="store_true", help="skip the per-part print STLs")
    args = ap.parse_args()

    inst, info = build(min(max(args.deploy, 0.0), 1.0), args.tube)
    scale = 25.4 if args.units == "mm" else 1.0
    os.makedirs(args.outdir, exist_ok=True)

    path = os.path.join(args.outdir, "airbrake_assembly.stl")
    mesh = assembly_mesh(inst)
    write_stl(path, mesh, scale, "MIT RT air brake (%s)" % args.units)
    print("wrote %s  (%d triangles)" % (path, len(mesh)))
    if not args.no_step:
        path = os.path.join(args.outdir, "airbrake_assembly.step")
        write_step(path, inst, scale)
        print("wrote %s  (%d part instances)" % (path, len(inst)))
    if not args.no_print:
        outdir = os.path.join(args.outdir, "print")
        written, hardware = write_print_parts(outdir, inst, scale)
        print("wrote %d print files to %s:" % (len(written), outdir))
        for fn, note in written:
            print("    %-28s %s" % (fn, note))
        print("hardware (not printed): " + ", ".join("%s x%d" % (n, c) for n, c, _ in hardware))

    print("units: %s" % args.units)
    print("leaf extended area: %.3f in^2 each, %.2f in^2 total" % (LEAF_W * LEAF_EXT, 4 * LEAF_W * LEAF_EXT))
    print("crank radius %.3f in, link %.3f in, crank angle %.1f deg, leaf travel %.3f in"
          % (info["crank_radius"], info["link_length"], info["crank_angle_deg"], info["leaf_travel"]))
    print("leaf level pitch %.3f in, stack height %.2f in" % (info["leaf_pitch"], info["stack_height"]))
    if info["shaft_clearance"] < 0:
        print("WARNING: leaf connector hits the hex shaft (%.3f in interference)" % -info["shaft_clearance"])
    else:
        print("leaf connector / shaft clearance %.3f in" % info["shaft_clearance"])


if __name__ == "__main__":
    main()
