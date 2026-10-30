# Design notes

Source: `fs/v0_original.fs` (your FeatureScript, unchanged). `fs/airbrake_v1_v2.fs` is generated from it by
`tools/build_fs.py` (exact string patches, each asserted to match once). Set `AIRBRAKE_WORK` to a scratch folder for the tools.

## Hardware standard (M3 self-tapping, chosen by you)
| Item | Size |
|---|---|
| M3 clearance / pilot (thread-forming PLA/PETG) / socket-head counterbore | 3.4 / 2.6 / 6.0 mm |
| M4 hinge: clearance / pilot | 4.5 / 3.3 mm |

## V1 = your reinforced bottom-spring model + screws (`V2 compact head` = off)
| Joint (was) | Now |
|---|---|
| C1/C2 seam (bond) | 4 x M3x8 socket head across the seam on inward ribs at z=8 and z=44 (45/225 deg strips); straight hex-key access checked with fins 2 and 3 open |
| Hinge pin H + cap K (bond) | M4x25 button head per hinge, threads into the +Y ear; K removed; bores 4.5 mm |
| Catch cap L (bond; its closed socket could not slide on) | open-top clip + boss under the arm, 1 x M3x8 vertical; seam boss raised to z=63.5 |
| Upper sleeve to BT80 | 4 x M3x6 radial into pads (z=76) |
| Lower sleeve + dock ring to BT80 | 3 x M3x10 radial (z=-26.5, 90/200/340 deg) through tube and sleeve into dock-ring pads |
| Cradle S to dock feet (bond) | 4 x M3x10 radial (z=-67.2) through tube and foot into cradle pad (foot 1.5 mm longer, pad to R26) |
| Lid F to casing M (bond) | 3 x M3x10 vertical, lid ears at 145/215/335 deg into casing bosses |
| Q collar, G keeper, W root | stay bonded: sections under 3 mm |

## V2 = compact head inside the upper BT80 tube (`V2 compact head` = on), 22 mm latch drop
* Outer skin group moves in 0.72 mm: fin shell R29.9..32.3 (64.6 mm, your sleeve OD). 0.2 mm glue gap + 0.52 mm BT80 wall = R33.02.
* The fins stay put; everything under them moves up 22 mm (rotor stack, crown arms, top bearing, knob, catch caps). Fin top z 54, head top z 58.8
  (4.8 mm; V1: 28 mm).
* New latch (the V1 hook cannot fit inside the fin height): each fin carries an inward lug (plate R20..30.6 z 47..50, wall R20..22.8 z 41.6..50);
  the catch cap on each rotor arm carries a finger (R23.6..26, z 40.8..46) just outside that wall. Hold: the fin is blocked from 2 deg of opening at rotor 0.
  Release: free at rotor 16 deg, still held at 14. The cams do not touch the fins at 22 deg and do by 26 deg. Checked by interference in the CAD, not on a print.
* Upper BT80 tube covers the whole fin zone and butts the 4 mm stop ring (z=-11). Four windows (38.6 x 63.8, z -9.2..54.6) are cut; the
  37.5 x 42 mm cut-outs trimmed from the waste are glued to the fins and ride with them (they start at z=8).
* No upper sleeve; 4.2 mm top ring (z 54.6..58.8). 8 supports: 4 thick strips between the windows (R27.4..32.3, two pieces that leave the cam band
  z 18.5..29.5 clear) and the 4 under-fin stop blocks. Top tube screwed to the strips with 8 x M3x5, holes centred on each strip.
* Bottom keeps the 18 mm sleeve fit. Cam peak 29 -> 28.6 mm for pillar clearance.
* Lengths: exposed airbrake 82 -> 4 mm; printed housing 118 -> 91.8 mm; whole printed assembly 178.5 -> 152.3 mm.
* Checked: no printed-part overlaps closed or open; hex-key access to all four seam screws with fins open.

## V3 = SG90 straight on the rotor (module mode 3, `V2 compact head` on)
* Starts from the 22 mm V2 head unchanged (fins, cams, rotor-mounted latch, housing, tube slits). Everything between the rotor and the servo
  is removed: spring cartridge, trigger, pushrod, yoke, dock, casing, lid, hub, collar, pin, cradle, keeper, horn saddle (about 64 g printed).
* Rotor: bottom at z -8.7 with a 6.2 mm hub (z -8.7..-1.7) holding a horn pocket R4.5 + arm slot that opens into the bore (horn-screw access). Lower bearing (3 mm, z -0.8..2.2), thrust collar (z 2.7..4.7) and the four spokes (out to the support strips) are raised above the horn so the servo can sit flush.
  The horn arm starts at 100 deg so its 65 deg sweep clears the posts.
* Servo (reference body, shaft up, shaft end at z -10.3, bottom z -33.0 = flush with the housing bottom): long axis at 135 deg, hung by its flange (z -17..-14.5) from two posts (R16.3..21.3 at 135 deg and R-11.8..-6.8, i.e. at 315 deg) that
  hang from the raised spokes; a 0.7 mm relief in the base ring clears the tab; M2x8 self-tapping screws up through the tab holes (s = +18.8 and -9.3) into 1.6 mm pilots.
* Three pads on the inside of the lower glue sleeve (R23.2..30.4, z -30.5..-22.5, at 90/200/340 deg) take 3 x M3x10 through the BT80 tube and the sleeve.
* Printed set 106 g solid PLA (V2 169 g); overall 91.8 mm with the servo inside the housing (V2 152.3 mm; an earlier V3 layout with the servo hanging below was 105.5 mm). Checked: no printed overlaps closed or open, rotor swept 0..65 deg clear of housing and servo,
  latch holds from 1.5-2 deg of fin opening and releases at 15 deg of rotor travel, cams touch at about 26 deg, seam hex-key access clear.
* With the rotor at 65 deg the cam holds each fin open about 14 deg; the airflow does the rest to the 90 deg stop. Servo torque: `tools/torque_check.py` (latch friction under wind suction dominates).
* Assumed, not measured: SG90 and horn dimensions, wind-suction coefficient, friction.

## Correction made while building V3
The V2 reference upper tube in the CAD still had a 60.2 mm window (top z 51.0) while the fin top is at z 54: the fin tip would have hit the tube at the first degree of opening. The window is now 63.8 mm
(top z 54.6, as the guide always said); fin plus glued cut-out are clear of the tube at every opening angle 0.5..90 deg (`tools/sweep_open.py`). Printed parts were not affected.

## Choices that were mine
* One public Onshape document (Free plan cannot make private ones).
* Where the user's bonded joint had under 3 mm of material, it stays bonded rather than adding a weak screw.
* Hinge: M4 screw into the printed ear rather than a nut (nut pocket would break through the pillar skin).
