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

## V2 = compact head inside the upper BT80 tube (`V2 compact head` = on)
* Outer skin group moves in 0.72 mm: fin shell R29.9..32.3 (64.6 mm, your sleeve OD). 0.2 mm glue gap + 0.52 mm BT80 wall = R33.02.
* Upper BT80 tube covers the whole fin zone and butts the 4 mm stop ring (z=-11). Four windows (38.6 x 60.2) are cut; the
  37.5 x 42 mm cut-outs trimmed from the waste are glued to the fins and ride with them (they start at z=8 so their lower
  edge clears the stop block at 90 deg).
* No upper sleeve; 6 mm top ring (z 66.9..73). 8 supports: 4 thick strips between the windows (R26.8..32.3, two pieces
  that leave the cam band z 18.5..29.5 clear) and the 4 under-fin stop blocks (R27..32.3). Top tube screwed to the strips with
  8 x M3x6, holes centred on each strip (offset holes left only ~1.3 mm of tube web beside the window).
* Bottom keeps the 18 mm sleeve fit. Cam peak 29 -> 28.6 mm for pillar clearance.
* Lengths: exposed airbrake 82 -> 4 mm; printed housing 118 -> 111.4 mm; whole printed assembly 178.5 -> 171.9 mm.

## Choices that were mine
* One public Onshape document (Free plan cannot make private ones).
* Where the user's bonded joint had under 3 mm of material, it stays bonded rather than adding a weak screw.
* Hinge: M4 screw into the printed ear rather than a nut (nut pocket would break through the pillar skin).
