# V5 print set (module + head only)

Generated from the final V5 CAD (V5-A closed state). **Not included on purpose:** the BT80 tube and the transition (use your real tube and your own transition).
Everything is already oriented for printing (z = 0 is the bed). Nothing here has been printed yet: do one fin and the head cup first and check the fit.

| File | Qty | Size (mm) | Bed side | Supports | Notes |
|---|---|---|---|---|---|
| `C_module_housing_x1.stl` | 1 | 64.4 x 64.4 x 68.8 | floor plate down, upright | yes (hinge ears, nut bosses, spokes) | one piece, no seam |
| `R_rotor_x1.stl` | 1 | 52.3 x 52.3 x 51.0 | hub down | yes | catch caps and limiter finger are part of it |
| `P_fin_x4.stl` | 4 | 61.6 x 34.6 x 12.2 | flat side down | yes (root, tail) | this file is ONE fin, print it four times |
| `P_fin_plate_4_fins.stl` | 1 plate | 129.2 x 75.2 x 12.2 | same | yes | the same four fins on one plate, use this instead of the single file if you want |
| `H_head_cup_x1.stl` | 1 | 63.9 x 63.9 x 43.2 | upside down (rim down) | yes (under the floor and the servo ledges) | electronics pockets, vents, USB-C window, switch slot |
| `K_head_lid_x1.stl` | 1 | 59.4 x 59.4 x 10.6 | disc down | almost none | four nut bosses on the underside |

Material and settings (from the FEA, not from a test): the fins are the part that nearly snapped, so print them in PETG or PLA+ with 4 or more walls and as dense an infill as you can (100% if possible);
the rest can be whatever you used for the friend's print. Layer 0.2 mm or finer. Do not scale the parts.

## Hardware to buy (all M3 unless noted)
* 12 x M3x8 button head bolts and 12 x M3 nuts: the radial bolts (4 head, 4 module, 4 transition)
* 4 x M3x25 button head bolts and 4 x M3 nuts: fin hinges
* 2 x M2x6 bolts and 2 x M2 nuts: servo flange; 1 x the horn screw that came with the servo
* SG90 servo (measure the gear boss and spline if the head does not seat: see the assembly guide, section 9)

## Order (details in `docs/V5_assembly_guide.pdf`, section 5)
Nuts into the housing wall pockets, rotor in from the top and parked at about 18 deg, hinge nuts into the +Y ear slots, fins in through the windows,
hinge bolts through the 6.6 mm channels in the housing wall (module out of the tube), rotor back to 0. Head: M2 nuts in the ledges, servo, electronics, lid nuts, lid.

## What you still have to cut yourself (real BT80 tube)
4 windows 67 deg x 63.8 mm (z -9.2 .. 54.6 from the module bottom at z -10), and 12 M3 clearance holes: 4 head at z 82, 4 module at z 12, 4 transition at z -28 (module bottom is z -10).
Say if you want a 1:1 paper template for that.

## One-plate version for a Bambu Lab P1S (256 x 256 x 256 mm)
`../P1S_one_plate_full_set.3mf` has everything on one plate: housing, rotor, 4 fins, head cup, head lid and 4 SPARE fins (12 objects, 6 mm apart, nothing taller than 69 mm).
Open it in Bambu Studio (objects stay at their positions). To drop the spare fins, delete the four objects at the top of the plate. `../P1S_one_plate_full_set.stl` is the same layout as one STL (use "split to objects").
