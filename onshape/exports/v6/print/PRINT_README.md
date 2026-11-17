# V6 print set = V5 + the thin fin "T" (built in Onshape V6-A, 2026-11-17)

Only the fins differ from V5. Housing, rotor, lid and transition are exactly V5; the head cup is V5 with the post-print fixes
(wide servo arms, thinner ledge, no M2 nut recess, cable slot beside the servo). The PDF weight cuts (V6 option) are OFF.

| Part | Volume (mm3) | Solid PLA |
|---|---|---|
| Fin T (x4): 1.2 mm skin above the root, no ribs, two edge lips; push pad, lock lug, tail, hinge root as V5 | 6,202 (V5: 7,862) | 7.7 g each (V5 9.7 g), set 8.2 g lighter |
| Housing | 24,231 | 30.0 g |
| Rotor | 17,986 | 22.3 g |
| Head cup | 18,917 | 23.5 g |
| Lid | 6,506 | 8.1 g |

Stress check (offline, same method as before, open fin, 30 N air load): 10.5 MPa peak (V5 10.2), tip bend 0.77 mm (V5 0.72); the peak is at the hinge root in every variant.
Print the fins flat, at least 3 walls with a 0.4 mm nozzle so the 1.2 mm skin is solid; hand-test one before flight.
Plates: `../P1S_plate1.3mf`, `../P1S_plate2.3mf`. Hardware and orientation as in `../../v5/print/PRINT_README.md` (servo screws go straight into the servo, no M2 nuts).
