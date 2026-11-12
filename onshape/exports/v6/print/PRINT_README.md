# V6 print set (V5 + the weight-reduction cuts from assembly_weight_reduction_proposals.pdf)

Same parts, orientation and hardware as `../../v5/print/PRINT_README.md`. Made by cutting the V5 print STLs offline (Onshape API quota exhausted, HTTP 402);
the matching FeatureScript is the "V6 weight reduction" checkbox in `fs/airbrake_v1_v2.fs` (not yet built in Onshape).

| Part | Cut (PDF code) | V5 -> V6 volume (mm3) | saved (solid PLA) |
|---|---|---|---|
| Housing | C1: four 60 deg windows R6.5..15 in the floor plate | 24,231 -> 23,466 | 0.9 g |
| Fin (each, x4) | F1 + F2 inner-face pockets (1.5 / 2.0 mm skin) | 7,863 -> 7,160 | 0.9 g each, 3.5 g set |
| Head cup | U1 two O14 floor holes, U2 wall 0.5 mm thinner (z 73.1..86.0, not under the lid, +-16 deg kept at the bolts) | 18,923 -> 17,589 | 1.7 g |
| Lid | K1 0.8 mm underside recess inside R23.5 | 6,506 -> 5,119 | 1.7 g |
| Rotor | unchanged (the rotor proposals were in a separate document) | 17,986 | - |

Total about 7.8 g less (solid PLA). The head cup also has the stronger servo arms, thinner ledge, no nut recess and the moved cable slot.
Not done: L1/L2/L3 (lower section, not printed). U2 stops at z 86.0 so the lid still locates in the full-thickness wall.
P1S plates: `../P1S_plate1.3mf`, `../P1S_plate2.3mf` (about 95 g each with supports, estimate).
