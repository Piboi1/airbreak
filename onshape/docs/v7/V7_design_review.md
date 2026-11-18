# V7 design review (friend's "V7 - transition servo and electronics", reviewed 2026-11-18)

Source: Onshape Feature Studio "V7 transition electronics airbrake" (`1c9e9aa49bb48d875ac0681f`, copy in `v7_friend_source.fs`),
Part Studio "V7 - transition servo and electronics" (`9416d95628efd3b4e509dde4`). Reviewed offline on the downloaded meshes (4 API requests).

## What V7 is
No head cup or lid. The SG90 sits in a longer printed transition, output shaft UP, and drives the rotor from below through a keyed
horn socket on a new rotor hub (coupling R12.5, z -14.5..-5.8). Electronics (Mercury, regulator, 300 mAh) sit on a removable tray at the
bottom of the transition. The module (housing, rotor, 4 fins) is built on the friend's older copy of the V5 core, not the V5 that was printed.
Fins are pushed by hook ramps on the rotor acting on the lock lug (no separate push pad).

| Printed part | V7 | Comparable V5/V6 part |
|---|---|---|
| Housing (no floor plate) | 25.2 g | 30.0 g |
| Rotor (hook-ramp, bottom drive) | 16.8 g | 22.3 g |
| Fins x4 | 4 x 7.7 g | V5 4 x 9.7 g, fin T 4 x 7.7 g |
| Transition (servo ledges, cone, BT70 coupler) | 50.9 g | user prints their own (not modelled) |
| Electronics tray | 9.8 g | head cup 23.5 g + lid 8.1 g |
| **Total printed** | **133.6 g** | V6 114.6 g + the user's own transition |

## Checks run
* Interference of every pair of parts (closed): none.
* Mechanism sweep (rotor 0..65 deg, fin swung about its hinge): locked at 0 deg (a fin can open only 1.5 deg); lock lets go between 10 and 20 deg;
  hook ramps kick the fin from 45 deg to 8 deg by 55-65 deg; the airflow does the rest (same principle as V5). No rotor/housing clash; an open fin clears everything.
* Fin stress (same FEA as all earlier fins: open fin on its stop, 0.8 mm voxels, PLA): 12 N 8.7 MPa, **30 N 21.9 MPa**, 15 N tip 17.1 MPa;
  tip deflection 0.97 mm at 30 N. V5: 10.2 MPa / 0.72 mm; fin T: 10.5 MPa / 0.77 mm. Peak at the fin root next to the stop.

## Findings
| # | Severity | Finding |
|---|---|---|
| 1 | Critical | **Fin root about 2x weaker than V5**: root gusset, root pad and ribs are gone; 21.9 MPa at 30 N is above the ~15 MPa across-layer strength used for PLA. This is the "fins nearly snap past 90 deg" problem again. |
| 2 | Critical | **No 90-deg tail lock**: the fin tail and the housing U-pocket/keepers (the fix for that problem) are not in V7; the open fin rests on its stop only. |
| 3 | High | **Rotor not held down**: nothing above the rotor (no head). The horn sits only 2.6 mm deep in the rotor socket. When the brakes deploy the rocket decelerates and the rotor wants to lift; once the fins are open nothing stops it sliding off the horn. |
| 4 | Rule | **BT70 side touched**: the printed transition includes the cone and a coupler into the BT70 tube (R25.5..27.45, z -88..-72.7). Your rule was never to touch the BT70 side, and you use your own transition (62 mm bore). |
| 5 | Rule | **Tray screws**: two radial M2 self-tapping screws at z -78 go through the BT70-side coupler (and the BT70 tube) into 1.7 mm pilots; rules ask for M3 bolts + nuts, BT80 side only. Boards are on adhesive. |
| 6 | Medium | **No arming switch or USB-C access**: to switch on or charge, the transition has to come out of the BT70 tube. |
| 7 | Medium | **Static ports**: 3 x O1.6 vents at z -56 are in the exposed cone (good), but the bay is open upward through the servo bay into the module, whose fin windows are open to the airflow; the altimeter may read flow pressure, not static. |
| 8 | Low | Transition is heavy (50.9 g): the BT80 shoulder is a solid 5.5 mm wall for 20 mm. |
| 9 | Low | Servo ledge 0.4 mm from the servo body; servo screws are M2 self-tapping into the ledge from below (only reachable with the tray out). |

## Good
Module comes off the servo by sliding (horn socket), so the servo and electronics stay put when the module is swapped; lighter rotor and housing;
mechanism timing is right (lock, release, kick); all module and tube bolts are radial M3 + nut on the BT80 side; FS checks payload clearances itself.

## Proposed changes (need approval)
| Code | Change | Effect |
|---|---|---|
| A | Put the V5 fin root back on the V7 fin (root gusset + root pad), keep everything else of the V7 fin (no push pad, no ribs) | fin stress back to about V5 level (to be confirmed by FEA), about +0.6 g per fin |
| B | Put the 90-deg tail lock back: fin tail + housing U-pocket and keeper towers (as in V5) | restores the fix for problem #1 |
| C | Rotor retainer: a light printed ring over the rotor top (0.5 mm gap) held by 4 radial M3 bolts + nuts through the BT80 tube | rotor cannot lift off the horn; about +4 g and 4 new tube holes |
| D | Transition: EITHER (D1) keep V7's printed transition (accept the BT70-side change), OR (D2) keep your own transition and turn V7's servo/electronics bay into an insert that slides into your 62 mm bore and bolts BT80-side only (nut-ring style) | D2 follows your rules |
| E | Electronics tray: replace the M2 self-tapping screws with M3 bolts + nuts on the BT80 side (depends on D) | rule-compliant, serviceable |
| F | Switch slot + USB-C window in the bay wall (and the tube) | arm and charge without disassembly |
| G | Thin diaphragm between the servo bay and the electronics bay (wire hole only) so the vents read static pressure | better altitude data |
| H | Lighten the transition shoulder (pockets between the bolt bosses), only if D1 | about -10 g |

Implementation would be a NEW feature studio "V7.1" (the friend's V7 stays untouched), about 10-15 Onshape requests, plus offline FEA/kinematics re-checks.
