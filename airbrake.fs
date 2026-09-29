FeatureScript 2144;
import(path : "onshape/std/common.fs", version : "2144.0");

/*
 * MIT Rocket Team (Prometheus) sliding-plate air brake, CDR layout.
 *
 * Creates every part of the mechanism in its assembled position:
 *   bottom frame, 2 trays + 4 tray-frame segments, middle frame, 4 leaves,
 *   2 hex connectors, 4 leaf connectors, 4 spacers, servo bulkhead, 2 servo
 *   brackets, servo, hex shaft, shaft coupler, and optionally pins/washers
 *   and the slotted airframe tube.
 *
 * "Deployment" (0..1) drives the linkage: the hex connectors rotate, the leaf
 * connectors follow and the leaves slide out 2.25 in. Every joint gets a mate
 * connector so the parts can be mated quickly in an Assembly.
 *
 * Published on the MIT wiki: 4 leaves 3.5 in wide x 2.25 in extended, two
 * trays 90 deg apart each holding one pair, hex connector + leaf connectors,
 * 6 in airframe (5.823 in ID / 6.00 in OD). Everything else is estimated.
 *
 * All lengths are in meters (Onshape's internal unit); INCH converts.
 */

// ---------------------------------------------------------------------------
// Dimensions (meters)
// ---------------------------------------------------------------------------
const INCH = 0.0254;

const TUBE_ID = 5.823 * INCH;
const TUBE_OD = 6.000 * INCH;
const FRAME_OD = 5.800 * INCH;
const FRAME_RING_W = 0.40 * INCH;

const LEAF_W = 3.50 * INCH;
const LEAF_EXT = 2.25 * INCH;
const LEAF_T = 0.125 * INCH;
const LEAF_R = TUBE_OD / 2;
const LEAF_GAP = 0.03 * INCH;
const LEAF_NOTCH_R = 0.17 * INCH;
const LEAF_PIN_X = 0.40 * INCH;
const LEAF_PIN_Y = 0.33 * INCH;
const LEAF_LIP_W = 0.10 * INCH;
const LEAF_LIP_H = 0.06 * INCH;
const LEAF_LIP_INSET = 0.15 * INCH;

const TRAY_FLOOR_T = 0.06 * INCH;
const TRAY_RAIL_W = 0.20 * INCH;
const TRAY_CLEAR = 0.01 * INCH;
const TRAY_HOLE_R = 0.22 * INCH;
const TRAY_LEDGE = 0.02 * INCH;

const CONN_T = 0.125 * INCH;
const CONN_W = 0.30 * INCH;
const CRANK_W = 0.50 * INCH;
const WASHER_T = 0.02 * INCH;
const WASHER_R = 0.17 * INCH;
const PIN_R = 0.095 * INCH;
const HOLE_CLEAR = 0.005 * INCH;
const HEX_AF = 0.25 * INCH;

const CRANK_SWEEP = PI / 2;        // servo travel, stowed -> fully out

const FRAME_T = 0.20 * INCH;
const MID_FRAME_T = 0.125 * INCH;
const SPACER_H = 0.25 * INCH;
const SPACER_SPAN = 30 * PI / 180;

const SERVO_L = 2.60 * INCH;
const SERVO_W = 1.50 * INCH;
const SERVO_H = 2.40 * INCH;
const SERVO_OFFSET = 0.65 * INCH;  // output spline offset from the body centre
const SERVO_EAR_LEN = 0.35 * INCH;
const SERVO_EAR_T = 0.12 * INCH;
const SERVO_EAR_Z = 0.55 * INCH;
const SERVO_FINS = 9;
const BRACKET_H = 0.60 * INCH;
const COUPLER_R = 0.30 * INCH;

const TRAY_H = TRAY_FLOOR_T + LEAF_T + WASHER_T + CONN_T + WASHER_T + CONN_T + 0.03 * INCH;
const CHANNEL_HW = LEAF_W / 2 + TRAY_CLEAR;
const TRAY_HW = CHANNEL_HW + TRAY_RAIL_W;

const DEPLOY_BOUNDS = { (unitless) : [0, 1, 1] } as RealBoundSpec;

// ---------------------------------------------------------------------------
// Feature
// ---------------------------------------------------------------------------
annotation { "Feature Type Name" : "MyCustomPart" }
export const myCustomPart = defineFeature(function(context is Context, id is Id, definition is map)
    precondition
    {
        annotation { "Name" : "Deployment (0 = stowed, 1 = fully out)" }
        isReal(definition.deploy, DEPLOY_BOUNDS);

        annotation { "Name" : "Include servo", "Default" : true }
        definition.includeServo is boolean;

        annotation { "Name" : "Include pins and washers", "Default" : true }
        definition.includeHardware is boolean;

        annotation { "Name" : "Include airframe tube", "Default" : false }
        definition.includeTube is boolean;

        annotation { "Name" : "Add mate connectors", "Default" : true }
        definition.mateConnectors is boolean;
    }
    {
        const lk = solveLinkage();
        const rc = lk.rc;
        const l = lk.l;
        const phi = lk.phiR + (lk.phiE - lk.phiR) * definition.deploy;
        const s = sliderPos(rc, l, phi, LEAF_PIN_X);
        const travel = s - LEAF_PIN_Y;
        const mc = definition.mateConnectors;

        var q;
        var z = 0;

        // bottom frame
        const baseFr = frameAt(0, 0, 0, 0);
        q = makePart(context, id + "frameBottom", baseFr, [stackBody(bottomFrameLoops(), 0, FRAME_T)], "Bottom frame");
        if (mc)
            addConnector(context, id + "mcFrameBottom", baseFr, q, [0, 0, FRAME_T], false);
        z += FRAME_T;

        var tubeSlots = [];
        for (var lv in [["A", 0], ["B", PI / 2]])
        {
            const tag = lv[0];
            const rot = lv[1];

            for (var k = 0; k < 2; k += 1)
                makePart(context, id + ("trayFrame" ~ tag ~ k), frameAt(0, 0, z, rot + k * PI),
                         [stackBody([trayFrameLoop()], 0, TRAY_H)], "Tray frame " ~ tag ~ (k + 1));

            const trayFr = frameAt(0, 0, z, rot);
            q = makePart(context, id + ("tray" ~ tag), trayFr, trayBodies(), "Tray " ~ tag);
            if (mc)
                addConnector(context, id + ("mcTray" ~ tag), trayFr, q, [0, 0, TRAY_FLOOR_T], true);

            const zf = z + TRAY_FLOOR_T;               // leaf bottom
            const zl = zf + LEAF_T + WASHER_T;         // leaf connector bottom
            const zc = zl + CONN_T + WASHER_T;         // hex connector bottom

            const hexFr = frameAt(0, 0, zc, rot + phi);
            q = makePart(context, id + ("hexConn" ~ tag), hexFr, [stackBody(hexConnectorLoops(rc), 0, CONN_T)],
                         "Hex connector " ~ tag);
            if (mc)
            {
                addConnector(context, id + ("mcHexAxis" ~ tag), hexFr, q, [0, 0, 0], false);
                addConnector(context, id + ("mcHexPinP" ~ tag), hexFr, q, [rc, 0, CONN_T], false);
                addConnector(context, id + ("mcHexPinN" ~ tag), hexFr, q, [-rc, 0, CONN_T], false);
            }

            for (var k = 0; k < 2; k += 1)
            {
                const a = rot + k * PI;
                const name = tag ~ (k + 1);
                const d = rot2([0, travel], a);
                const lp = rot2([LEAF_PIN_X, s], a);                        // leaf pin
                const cp = rot2([rc * cosr(phi), rc * sinr(phi)], a);           // crank pin
                const la = ang2(lp[1] - cp[1], lp[0] - cp[0]);

                const leafFr = frameAt(d[0], d[1], zf, a);
                q = makePart(context, id + ("leaf" ~ name), leafFr, leafBodies(), "Leaf " ~ name);
                if (mc)
                {
                    addConnector(context, id + ("mcLeafPin" ~ name), leafFr, q, [LEAF_PIN_X, LEAF_PIN_Y, LEAF_T], false);
                    addConnector(context, id + ("mcLeafSlide" ~ name), leafFr, q, [0, 0, 0], true);
                }

                const linkFr = frameAt(cp[0], cp[1], zl, la);
                q = makePart(context, id + ("leafConn" ~ name), linkFr, [stackBody(leafConnectorLoops(l), 0, CONN_T)],
                             "Leaf connector " ~ name);
                if (mc)
                {
                    addConnector(context, id + ("mcLinkCrank" ~ name), linkFr, q, [0, 0, 0], false);
                    addConnector(context, id + ("mcLinkLeaf" ~ name), linkFr, q, [l, 0, 0], false);
                }

                if (definition.includeHardware)
                {
                    makePart(context, id + ("pinLeaf" ~ name), frameAt(lp[0], lp[1], zf, 0),
                             [stackBody([circleLoop(PIN_R, 0, 0)], 0, LEAF_T + WASHER_T + CONN_T)], "Leaf pin " ~ name);
                    makePart(context, id + ("pinCrank" ~ name), frameAt(cp[0], cp[1], zl, 0),
                             [stackBody([circleLoop(PIN_R, 0, 0)], 0, CONN_T + WASHER_T + CONN_T)], "Crank pin " ~ name);
                    makePart(context, id + ("washerLeaf" ~ name), frameAt(lp[0], lp[1], zf + LEAF_T, 0),
                             [stackBody(washerLoops(), 0, WASHER_T)], "Washer leaf " ~ name);
                    makePart(context, id + ("washerCrank" ~ name), frameAt(cp[0], cp[1], zl + CONN_T, 0),
                             [stackBody(washerLoops(), 0, WASHER_T)], "Washer crank " ~ name);
                }
            }

            tubeSlots = append(tubeSlots, [zf - 0.02 * INCH, zf + LEAF_T + LEAF_LIP_H + 0.02 * INCH, rot]);
            z += TRAY_H;
            if (tag == "A")
            {
                makePart(context, id + "frameMiddle", frameAt(0, 0, z, 0),
                         [stackBody([circleLoop(FRAME_OD / 2, 0, 0), circleLoop(FRAME_OD / 2 - FRAME_RING_W, 0, 0)], 0, MID_FRAME_T)],
                         "Middle frame");
                z += MID_FRAME_T;
            }
        }

        for (var k = 0; k < 4; k += 1)
        {
            const h = SPACER_SPAN / 2;
            makePart(context, id + ("spacer" ~ k), frameAt(0, 0, z, PI / 4 + k * PI / 2),
                     [stackBody([sectorLoop(FRAME_OD / 2 - FRAME_RING_W, FRAME_OD / 2, -h, h)], 0, SPACER_H)],
                     "Spacer " ~ (k + 1));
        }
        z += SPACER_H;

        const zBulk = z;
        makePart(context, id + "bulkhead", frameAt(0, 0, z, 0), [stackBody(bulkheadLoops(), 0, FRAME_T)], "Servo bulkhead");
        z += FRAME_T;
        const zOut = z + BRACKET_H;

        if (definition.includeServo)
        {
            for (var k = 0; k < 2; k += 1)
            {
                const x = SERVO_OFFSET + (2 * k - 1) * (SERVO_L / 2 + SERVO_EAR_LEN / 2);
                makePart(context, id + ("bracket" ~ k), frameAt(x, 0, z, 0), bracketBodies(), "Servo bracket " ~ (k + 1));
            }
            makePart(context, id + "servo", frameAt(0, 0, zOut, 0), servoBodies(), "Servo");
        }

        const shaftFr = frameAt(0, 0, 0, 0);
        q = makePart(context, id + "hexShaft", shaftFr,
                     [stackBody([hexLoop(HEX_AF)], 0, zOut - 0.12 * INCH - 0.05 * INCH)], "Hex shaft");
        if (mc)
            addConnector(context, id + "mcShaft", shaftFr, q, [0, 0, FRAME_T], false);

        makePart(context, id + "coupler", frameAt(0, 0, zBulk, 0),
                 [stackBody([circleLoop(COUPLER_R, 0, 0), hexLoop(HEX_AF + 2 * HOLE_CLEAR)], 0, zOut - 0.12 * INCH - zBulk)],
                 "Shaft coupler");

        if (definition.includeTube)
            makePart(context, id + "tube", frameAt(0, 0, 0, 0),
                     tubeBodies(tubeSlots, -0.5 * INCH, zOut + SERVO_H + 0.5 * INCH), "Airframe tube");
    });

// ---------------------------------------------------------------------------
// Linkage: offset slider-crank per leaf. Crank pin at rc*(cos phi, sin phi),
// leaf pin on the line x = LEAF_PIN_X. Solved so the leaf travels LEAF_EXT over
// CRANK_SWEEP and ends at dead centre (drag cannot back-drive the servo).
// ---------------------------------------------------------------------------
function sliderPos(rc is number, l is number, phi is number, px is number) returns number
{
    const dx = rc * cosr(phi) - px;
    return rc * sinr(phi) + sqrt(max(l * l - dx * dx, 0));
}

function linkGeom(rc is number) returns map
{
    const phiE = acos(LEAF_PIN_X / rc) / radian;
    return { "phiE" : phiE, "l" : LEAF_PIN_Y + LEAF_EXT - rc * sinr(phiE) };
}

function linkErr(rc is number) returns number
{
    const g = linkGeom(rc);
    return sliderPos(rc, g.l, g.phiE - CRANK_SWEEP, LEAF_PIN_X) - LEAF_PIN_Y;
}

function solveLinkage() returns map
{
    var lo = LEAF_PIN_X * 1.000001;
    var hi = CHANNEL_HW - CRANK_W / 2;
    for (var i = 0; i < 100; i += 1)
    {
        const mid = (lo + hi) / 2;
        if (linkErr(lo) * linkErr(mid) <= 0)
            hi = mid;
        else
            lo = mid;
    }
    const rc = (lo + hi) / 2;
    const g = linkGeom(rc);
    return { "rc" : rc, "l" : g.l, "phiE" : g.phiE, "phiR" : g.phiE - CRANK_SWEEP };
}

// ---------------------------------------------------------------------------
// Math helpers (angles are plain numbers in radians, lengths plain meters)
// ---------------------------------------------------------------------------
function cosr(a is number) returns number
{
    return cos(a * radian);
}

function sinr(a is number) returns number
{
    return sin(a * radian);
}

function ang2(y is number, x is number) returns number
{
    return atan2(y, x) / radian;
}

function circY(x is number, r is number) returns number
{
    return sqrt(max(r * r - x * x, 0));
}

function rot2(p is array, a is number) returns array
{
    return [p[0] * cosr(a) - p[1] * sinr(a), p[0] * sinr(a) + p[1] * cosr(a)];
}

// ---------------------------------------------------------------------------
// Profiles: a loop is an array of segments (line, arc or full circle)
// ---------------------------------------------------------------------------
function segL(p0 is array, p1 is array) returns map
{
    return { "t" : "L", "p0" : p0, "p1" : p1 };
}

function segA(c is array, r is number, a0 is number, a1 is number) returns map
{
    return { "t" : "A", "c" : c, "r" : r, "a0" : a0, "a1" : a1 };
}

function onArc(c is array, r is number, a is number) returns array
{
    return [c[0] + r * cosr(a), c[1] + r * sinr(a)];
}

function circleLoop(r is number, x is number, y is number) returns array
{
    return [{ "t" : "C", "c" : [x, y], "r" : r }];
}

function polyLoop(pts is array) returns array
{
    var loop = [];
    for (var i = 0; i < size(pts); i += 1)
        loop = append(loop, segL(pts[i], pts[(i + 1) % size(pts)]));
    return loop;
}

function rectLoop(x0 is number, y0 is number, x1 is number, y1 is number) returns array
{
    return polyLoop([[x0, y0], [x1, y0], [x1, y1], [x0, y1]]);
}

function hexLoop(af is number) returns array
{
    const r = af / sqrt(3);
    var pts = [];
    for (var k = 0; k < 6; k += 1)
        pts = append(pts, [r * cosr(k * PI / 3), r * sinr(k * PI / 3)]);
    return polyLoop(pts);
}

function stadiumLoop(p is array, q is array, w is number) returns array
{
    const a = ang2(q[1] - p[1], q[0] - p[0]);
    const r = w / 2;
    const n = [-sinr(a) * r, cosr(a) * r];
    return [segA(p, r, a + PI / 2, a + 3 * PI / 2),
            segL([p[0] - n[0], p[1] - n[1]], [q[0] - n[0], q[1] - n[1]]),
            segA(q, r, a - PI / 2, a + PI / 2),
            segL([q[0] + n[0], q[1] + n[1]], [p[0] + n[0], p[1] + n[1]])];
}

function sectorLoop(ri is number, ro is number, a0 is number, a1 is number) returns array
{
    return [segA([0, 0], ro, a0, a1),
            segL(onArc([0, 0], ro, a1), onArc([0, 0], ri, a1)),
            segA([0, 0], ri, a1, a0),
            segL(onArc([0, 0], ri, a0), onArc([0, 0], ro, a0))];
}

// region x0 <= x <= x1 inside a circle of radius r (ends are arcs)
function clippedRect(x0 is number, x1 is number, r is number) returns array
{
    const a0 = ang2(circY(x1, r), x1);
    const a1 = ang2(circY(x0, r), x0);
    return [segL([x1, -circY(x1, r)], [x1, circY(x1, r)]),
            segA([0, 0], r, a0, a1),
            segL([x0, circY(x0, r)], [x0, -circY(x0, r)]),
            segA([0, 0], r, -a1, -a0)];
}

function rotLoop(loop is array, a is number) returns array
{
    var out = [];
    for (var s in loop)
    {
        if (s.t == "L")
            out = append(out, segL(rot2(s.p0, a), rot2(s.p1, a)));
        else if (s.t == "A")
            out = append(out, segA(rot2(s.c, a), s.r, s.a0 + a, s.a1 + a));
        else
            out = append(out, { "t" : "C", "c" : rot2(s.c, a), "r" : s.r });
    }
    return out;
}

function stackBody(loops is array, z0 is number, z1 is number) returns map
{
    return { "loops" : loops, "z0" : z0, "z1" : z1 };
}

// ---------------------------------------------------------------------------
// Part profiles (local frame, bottom face on z = 0)
// ---------------------------------------------------------------------------
function leafBodies() returns array
{
    const hw = LEAF_W / 2;
    const a = ang2(circY(hw, LEAF_R), hw);
    const rn = LEAF_NOTCH_R;
    // outer edge on the airframe OD (flush when stowed); straight inner edge with a shaft notch
    const outline = [segA([0, 0], LEAF_R, a, PI - a),
                     segL([-hw, circY(hw, LEAF_R)], [-hw, LEAF_GAP]),
                     segL([-hw, LEAF_GAP], [-rn, LEAF_GAP]),
                     segA([0, LEAF_GAP], rn, PI, 0),
                     segL([rn, LEAF_GAP], [hw, LEAF_GAP]),
                     segL([hw, LEAF_GAP], [hw, circY(hw, LEAF_R)])];
    // raised stop lip: the skin arc moved inboard; it hits the tube wall at full extension
    const d = LEAF_EXT + (TUBE_OD - TUBE_ID) / 2;
    const xl = hw - LEAF_LIP_INSET;
    const b1 = ang2(circY(xl, LEAF_R), xl);
    const yTop = -d + circY(xl, LEAF_R);
    const yBot = yTop - LEAF_LIP_W;
    const lip = [segA([0, -d], LEAF_R, b1, PI - b1),
                 segL([-xl, yTop], [-xl, yBot]),
                 segA([0, -d - LEAF_LIP_W], LEAF_R, PI - b1, b1),
                 segL([xl, yBot], [xl, yTop])];
    return [stackBody([outline, circleLoop(PIN_R + HOLE_CLEAR, LEAF_PIN_X, LEAF_PIN_Y)], 0, LEAF_T),
            stackBody([lip], LEAF_T, LEAF_T + LEAF_LIP_H)];
}

function trayBodies() returns array
{
    const r = FRAME_OD / 2;
    return [stackBody([clippedRect(-TRAY_HW, TRAY_HW, r), circleLoop(TRAY_HOLE_R, 0, 0)], 0, TRAY_FLOOR_T),
            stackBody([clippedRect(-TRAY_HW + TRAY_LEDGE, -CHANNEL_HW, r - TRAY_LEDGE),
                  clippedRect(CHANNEL_HW, TRAY_HW - TRAY_LEDGE, r - TRAY_LEDGE)], TRAY_FLOOR_T, TRAY_H)];
}

function trayFrameLoop() returns array
{
    const r1 = FRAME_OD / 2;
    const a = acos(TRAY_HW / r1) / radian;
    return sectorLoop(r1 - FRAME_RING_W, r1, -a, a);
}

function bottomFrameLoops() returns array
{
    const r1 = FRAME_OD / 2;
    const r0 = r1 - FRAME_RING_W;
    const hub = 0.60 * INCH;
    const spoke = 0.30 * INCH;
    const dOut = asin(spoke / 2 / r0) / radian;
    const dIn = asin(spoke / 2 / hub) / radian;
    var loops = [circleLoop(r1, 0, 0), hexLoop(HEX_AF + 2 * HOLE_CLEAR)];
    for (var k = 0; k < 6; k += 1)
    {
        const a = 2 * PI * k / 6;
        const b = 2 * PI * (k + 1) / 6;
        loops = append(loops, [segA([0, 0], r0, a + dOut, b - dOut),
                               segL(onArc([0, 0], r0, b - dOut), onArc([0, 0], hub, b - dIn)),
                               segA([0, 0], hub, b - dIn, a + dIn),
                               segL(onArc([0, 0], hub, a + dIn), onArc([0, 0], r0, a + dOut))]);
    }
    return loops;
}

function bulkheadLoops() returns array
{
    const r1 = FRAME_OD / 2;
    const r0 = r1 - FRAME_RING_W;
    const barX = 0.85 * INCH;
    const barW = 0.35 * INCH;
    const hub = 0.55 * INCH;
    const yb = 0.15 * INCH;
    const xo = barX + barW / 2;
    const xi = barX - barW / 2;
    const ao = ang2(circY(xo, r0), xo);
    const side = [segL([xo, -circY(xo, r0)], [xo, circY(xo, r0)]),
                  segA([0, 0], r0, ao, -ao)];
    const a0 = asin(yb / hub) / radian;
    const xh = hub * cosr(a0);
    const ai = ang2(circY(xi, r0), xi);
    const middle = [segL([-xi, yb], [-xh, yb]),
                    segA([0, 0], hub, PI - a0, a0),
                    segL([xh, yb], [xi, yb]),
                    segL([xi, yb], [xi, circY(xi, r0)]),
                    segA([0, 0], r0, ai, PI - ai),
                    segL([-xi, circY(xi, r0)], [-xi, yb])];
    var loops = [circleLoop(r1, 0, 0), circleLoop(COUPLER_R + 0.03 * INCH, 0, 0)];
    for (var a in [0, PI])
    {
        loops = append(loops, rotLoop(side, a));
        loops = append(loops, rotLoop(middle, a));
    }
    return loops;
}

function hexConnectorLoops(rc is number) returns array
{
    return [stadiumLoop([-rc, 0], [rc, 0], CRANK_W),
            hexLoop(HEX_AF + 2 * HOLE_CLEAR),
            circleLoop(PIN_R + HOLE_CLEAR, rc, 0),
            circleLoop(PIN_R + HOLE_CLEAR, -rc, 0)];
}

function leafConnectorLoops(l is number) returns array
{
    return [stadiumLoop([0, 0], [l, 0], CONN_W),
            circleLoop(PIN_R + HOLE_CLEAR, 0, 0),
            circleLoop(PIN_R + HOLE_CLEAR, l, 0)];
}

function washerLoops() returns array
{
    return [circleLoop(WASHER_R, 0, 0), circleLoop(PIN_R + HOLE_CLEAR, 0, 0)];
}

function bracketBodies() returns array
{
    const top = BRACKET_H + SERVO_EAR_Z;
    const py = SERVO_W / 2 - 0.25 * INCH;
    return [stackBody([rectLoop(-0.2 * INCH, -SERVO_W / 2, 0.2 * INCH, SERVO_W / 2)], 0, 0.12 * INCH),
            stackBody([circleLoop(0.12 * INCH, 0, py), circleLoop(0.12 * INCH, 0, -py)], 0.12 * INCH, top)];
}

function servoBodies() returns array
{
    const cx = SERVO_OFFSET;
    const hl = SERVO_L / 2;
    const hw = SERVO_W / 2;
    var out = [stackBody([rectLoop(cx - hl, -hw, cx + hl, hw)], 0, SERVO_H),
               stackBody([circleLoop(0.35 * INCH, 0, 0)], -0.12 * INCH, 0),
               stackBody([rectLoop(cx - hl - SERVO_EAR_LEN, -hw - 0.02 * INCH, cx + hl + SERVO_EAR_LEN, hw + 0.02 * INCH)],
                    SERVO_EAR_Z, SERVO_EAR_Z + SERVO_EAR_T),
               stackBody([rectLoop(cx - hl + 0.3 * INCH, -hw + 0.2 * INCH, cx + hl - 0.3 * INCH, hw - 0.2 * INCH)],
                    SERVO_H, SERVO_H + 0.12 * INCH)];
    const pitch = SERVO_H * 0.6 / SERVO_FINS;
    for (var i = 0; i < SERVO_FINS; i += 1)
    {
        const zf = SERVO_H * 0.35 + i * pitch;
        out = append(out, stackBody([rectLoop(cx - hl - 0.08 * INCH, -hw - 0.10 * INCH, cx + hl + 0.08 * INCH, hw + 0.10 * INCH)],
                               zf, zf + 0.08 * INCH));
    }
    return out;
}

function tubeBodies(slots is array, z0 is number, z1 is number) returns array
{
    const ri = TUBE_ID / 2;
    const ro = TUBE_OD / 2;
    const half = asin((LEAF_W / 2 + 0.02 * INCH) / ro) / radian;
    var out = [];
    var z = z0;
    for (var sl in slots)
    {
        out = append(out, stackBody([circleLoop(ro, 0, 0), circleLoop(ri, 0, 0)], z, sl[0]));
        for (var k = 0; k < 2; k += 1)
        {
            const c = sl[2] + PI / 2 + k * PI;
            out = append(out, stackBody([sectorLoop(ri, ro, c + half, c + PI - half)], sl[0], sl[1]));
        }
        z = sl[1];
    }
    return append(out, stackBody([circleLoop(ro, 0, 0), circleLoop(ri, 0, 0)], z, z1));
}

// ---------------------------------------------------------------------------
// Geometry builders
// ---------------------------------------------------------------------------
// A frame is a local coordinate system: origin (meters), x axis rotated by a about Z.
function frameAt(x is number, y is number, z is number, a is number) returns map
{
    return { "origin" : vector(x, y, z) * meter, "x" : vector(cosr(a), sinr(a), 0), "z" : vector(0, 0, 1) };
}

function drawLoop(sk is Sketch, tag is string, loop is array)
{
    for (var i = 0; i < size(loop); i += 1)
    {
        const s = loop[i];
        const name = tag ~ "e" ~ i;
        if (s.t == "L")
        {
            skLineSegment(sk, name, { "start" : vector(s.p0[0], s.p0[1]) * meter,
                                      "end" : vector(s.p1[0], s.p1[1]) * meter });
        }
        else if (s.t == "A")
        {
            const p0 = onArc(s.c, s.r, s.a0);
            const pm = onArc(s.c, s.r, (s.a0 + s.a1) / 2);
            const p1 = onArc(s.c, s.r, s.a1);
            skArc(sk, name, { "start" : vector(p0[0], p0[1]) * meter,
                              "mid" : vector(pm[0], pm[1]) * meter,
                              "end" : vector(p1[0], p1[1]) * meter });
        }
        else
        {
            skCircle(sk, name, { "center" : vector(s.c[0], s.c[1]) * meter, "radius" : s.r * meter });
        }
    }
}

// Sketch the loops on a plane z0 above the frame origin and extrude them to z1.
// Loops nested inside another loop become holes.
function extrudeLoops(context is Context, id is Id, fr is map, z0 is number, z1 is number, loops is array) returns Query
{
    const pl = plane(fr.origin + fr.z * z0 * meter, fr.z, fr.x);
    const sk = newSketchOnPlane(context, id + "sk", { "sketchPlane" : pl });
    for (var k = 0; k < size(loops); k += 1)
        drawLoop(sk, "g" ~ k, loops[k]);
    skSolve(sk);
    opExtrude(context, id + "ex", {
                "entities" : qSketchRegion(id + "sk", true),
                "direction" : fr.z,
                "endBound" : BoundingType.BLIND,
                "endDepth" : (z1 - z0) * meter
            });
    opDeleteBodies(context, id + "del", { "entities" : qCreatedBy(id + "sk", EntityType.BODY) });
    return qCreatedBy(id + "ex", EntityType.BODY);
}

// Build a part from one or more stacked bodies, merge them into one solid and name it.
function makePart(context is Context, id is Id, fr is map, bodies is array, name is string) returns Query
{
    var qs = [];
    for (var k = 0; k < size(bodies); k += 1)
        qs = append(qs, extrudeLoops(context, id + ("b" ~ k), fr, bodies[k].z0, bodies[k].z1, bodies[k].loops));
    if (size(qs) > 1)
        opBoolean(context, id + "join", { "tools" : qUnion(qs), "operationType" : BooleanOperationType.UNION });
    const part = qBodyType(qCreatedBy(id, EntityType.BODY), BodyType.SOLID);
    setProperty(context, { "entities" : part, "propertyType" : PropertyType.NAME, "value" : name });
    return part;
}

// Mate connector at local point p. slide = true points its Z axis along the local
// +Y (the leaf's travel direction) for slider mates; otherwise Z is vertical.
function addConnector(context is Context, id is Id, fr is map, part is Query, p is array, slide is boolean)
{
    const yv = cross(fr.z, fr.x);
    const origin = fr.origin + (fr.x * p[0] + yv * p[1] + fr.z * p[2]) * meter;
    const cSys = slide ? coordSystem(origin, fr.x, yv) : coordSystem(origin, fr.x, fr.z);
    opMateConnector(context, id, { "coordSystem" : cSys, "owner" : part });
}
