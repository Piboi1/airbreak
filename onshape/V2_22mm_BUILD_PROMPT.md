# Prompt: design the 22 mm-drop V2 (compact head inside the upper BT80 tube)

Start from the BT80 cam kick-out airbrake FeatureScript "REINFORCED BOTTOM SPRING - 90 DEG". Design **V2**, a shorter version
whose head sits inside the upper BT80 tube. V1 (the original with screw holes added) stays exactly as it is.

## Concept
* The upper BT80 tube covers the fin zone. Slits are cut in the tube; each cut-out piece is glued to its fin and rides
  with it, and fills the slit again when the fin closes.
* The fins stay where they are. Everything under the fin (rotor, latch stack, bearings, knob, catch cap) moves up
  by **22 mm**, so the fin top ends at the head's top rim and the whole housing is much shorter than V1.
* The head is smaller in diameter: fin shell R29.9..32.3 (64.6 mm OD, the sleeve OD of the original). 0.2 mm glue gap
  plus 0.52 mm BT80 wall puts the tube inner surface at R33.02 (tube ID R32.5). Outer skin group shift: dr = -0.72.
* No upper sleeve. Four thick supports sit in the solid strips between the four fin windows and the top tube is
  screwed into them. The bottom keeps the 18 mm sleeve fit (OD 64.6).
* Hardware: M3 self-tapping (clearance O3.4, pilot O2.6, counterbore O6.0); M4 for the hinge (clearance O4.5, pilot O3.3).
  Screws are separate "HW" parts.

## Result targets
* Printed housing about 91.8 mm (z -33 to 58.8) versus 118 mm for V1; whole printed assembly about 152 mm versus 178.5 mm.
* No overlaps between printed parts, closed or open; every body watertight.
* Hex-key access to every seam screw with the fins open.
* The latch holds the fin shut at rotor 0 deg (fin can open no more than about 2 deg) and releases by about 16 deg of
  rotor travel, before the cam first touches the follower at about 23.7 deg.

## Geometry (V2 only; let dzT = 22)
* **Carrier tube:** top at z 58.8. No upper shoulder, belt, tip slot, crown slot or hook track.
* **Fin windows:** radial sector from R29.5+dr to 34, 33.5 deg wide, from z -9.2 up 63.8 mm (top at z 54.6, just above the
  fin top at z 54). A shorter window makes the top ring overlap the fin.
* **Rotor stack, all shifted down by dzT relative to the original:** rotor shaft, crown hub, high thrust washer, knob, finger,
  top bearing, bearing spokes, knob stops, bearing relief and rotor light bore.
* **Rotor arm to catch cap:** arm ends at R24.1, centred at z 58.6 - 22 = 36.6; cap radius 20.4.
* **Catch cap (open-top clip):**
  * body: radial box R18.0..26.0, +-4.2 wide, z 35.4, 5.4 tall
  * finger: R23.6..26.0, +-3.0, z 40.8, 5.2 tall
  * boss: R18.0..24.2, +-4.2, z 31.4, 4.0 tall
  * socket for the arm: R17.9..24.2, +-2.75, z 36.4, 5.0 tall (starts at R17.9 so the arm never meets a thin skin)
  * pilot hole for the vertical M3 from z 32.0 to 36.5
* **Fin latch lug** (replaces the original tab and tip root): wall R20.0..22.8, +-3, z 41.6, 8.4 tall, plus a plate
  R20.0..30.6, +-3, z 47, 3 tall.
* **Supports:** sector R27.4..30.6+dr, 11 deg wide, one in each strip between fins, in two pieces that leave the cam band
  z 18.5..29.5 clear; plus the four under-fin stop blocks (R27..32.3). Pilot holes end at R28.0, screws M3x5.
* **Seam (the two halves of the housing):** ribs only at the lower level. Lower seam screws at z 8, upper at z 44, the
  upper one placed in the strip at R29.6. Seam boss at z 51.5 (3.5 tall), peg at z 53.
* **Cam:** peak 28.6 mm (down from 29) for pillar clearance.
* **Top ring:** 4.2 mm thick (z 54.6..58.8) replaces the 18 mm upper sleeve; the knob sits in it and the top bearing is lower, at z 46..51.
* **Tube cut-outs:** start at z 8 and are 42 mm tall so their lower edge clears the stop block at 90 deg; the upper tube butts
  the 4 mm stop ring at z -11; screw holes in the tube are centred on each strip.

## Checks while designing
1. Closed state: no overlaps among printed parts, in particular fin top versus the top ring (z 51..54) and catch cap versus the rotor arm.
2. Open state (fins 90 deg, rotor 65 deg, button up): no overlaps, straight line of sight for a hex key to all four seam screws.
3. Latch: with the fin open 2 deg or more and the rotor at 0 deg the latch overlaps the fin lug (held); at 16 deg of rotor travel
   it is clear; the rotor arm only touches the follower pin after that (18 deg onward).
4. V1 volumes identical to before the change.
5. Whatever is not tested physically (latch action, mate motion) is stated as untested.
