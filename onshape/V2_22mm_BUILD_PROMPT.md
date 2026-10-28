# Prompt: build the 22 mm-drop V2 (compact head inside the upper BT80 tube)

Paste this into a fresh Claude Code session that has the repo `piboi1/airbreak` and Onshape API keys
(`ONSHAPE_ACCESS_KEY`, `ONSHAPE_SECRET_KEY`) as environment variables.

---

## Goal
Take the BT80 cam kick-out airbrake FeatureScript ("REINFORCED BOTTOM SPRING - 90 DEG", unchanged copy in
`onshape/fs/v0_original.fs`) and produce **V2**, a shorter version that lives inside the upper BT80 tube.
**V1 (screwed version of the original) must stay exactly as it is.**

V2 concept (the user's own design):
* The upper BT80 tube covers the fin zone. Slits are cut in the tube; each cut-out piece is glued to its fin and
  rides with it. When the fin closes, the piece fills the slit again.
* Fins stay where they are. **Everything under the fin (rotor, latch stack, bearings, knob, cap) is moved up by
  22 mm**, so the fin top ends at the head's top rim and the whole printed housing is much shorter than V1.
* The head is smaller in diameter: the fin shell is R29.9..32.3 (64.6 mm OD = the user's sleeve OD).
  Glue gap 0.2 mm + BT80 wall 0.52 mm = R33.02. Tube ID R32.5.
* Top connection: no upper sleeve. Four thick supports sit in the solid strips between the fin windows and the
  top tube is screwed into them. The bottom keeps the 18 mm sleeve fit.
* Hardware: M3 self-tapping (clearance O3.4, pilot O2.6, counterbore O6.0); M4 for the hinge (clearance O4.5,
  pilot O3.3). Screws are modelled as separate "HW" parts.

## Result targets
* Printed housing about 91.8 mm (z -33 .. 58.8) versus V1 118 mm; whole printed assembly about 152 mm versus 178.5 mm.
* No printed-part overlaps in the closed or the open state; no non-watertight bodies.
* Hex-key access to every seam screw with the fins open.
* Latch holds the fin shut at rotor 0 deg and lets go by about 16 deg of rotor travel, **before** the cam first
  touches the follower (about 23.7 deg).

## Where things are
* `onshape/tools/build_fs.py` generates `onshape/fs/airbrake_v1_v2.fs` from `v0_original.fs` using asserted
  string patches `P(old,new)`. Every patch must match exactly once. The `compact` boolean selects V2.
* `onshape/tools/` has `osapi.py` (REST), `run.py` (build and regen), `pipeline.py` (studios / assemblies /
  verify), `asm.py` (mates cloned from the user's Assembly 23), `geom.py`, `check.py`, `scan.py`, `export_print.py`,
  `render.py`, `figures.py`, `make_docs.py`.
* Set `export AIRBRAKE_WORK=<scratch folder>`; it holds `ids.json` (Onshape ids), cached `.pkl` meshes, figures.
* Onshape: public document `857ab7b483eda80939870e15`, workspace `0766f9a969602884d82183a8` (the Free plan forces
  public documents). Feature Studio `fs1` holds the generated script.

## 22 mm design, in `build_fs.py` (compact only)
Set `dzT = compact ? 22 : 0`.
* `topZ = compact ? 58.8 : 67` (carrier tube top). No upper shoulder or belt, tip slot, crown slot or hook track.
* Fin window: `sector(window, 29.5+dr, 34, 33.5, -9.2, 63.8)` (top at z 54.6, above the fin top at 54). `dr = -0.72`.
  The earlier 60.4 mm window left the ring overlapping the fin top by 231 mm3 - do not reduce it.
* Rotor shaft, crown hub, high thrust, knob, finger, top bearing, spokes, knob stops, bearing relief and
  rotor light bore all shift down by `dzT`.
* Cap arm: `armEnd = compact ? 24.1 : 30+dr`, `armZ = compact ? 58.6 - dzT : 58.6`, `capR = compact ? 20.4 : 24.3`.
* V2 catch cap (open-top clip): body `radialBox(18.0,26.0,+-4.2,35.4,5.4)`,
  finger `radialBox(23.6,26.0,+-3.0,40.8,5.2)`, boss `radialBox(18.0,24.2,+-4.2,31.4,4.0)`,
  socket `radialBox(17.9,24.2,+-2.75,36.4,5.0)` (17.9 so the rotor arm does not hit a 0.1 mm skin), pilot z 32.0..36.5.
* Fin latch lug: `lugWall radialBox(20.0,22.8,+-3,41.6,8.4)` plus `lugPlate radialBox(20.0,30.6,+-3,47,3)`,
  replacing the V1 tab and tip root.
* Supports: `sector(27.4, 30.6+dr, 11.0, ...)`; support pilots end at R28.0; support screws M3x5
  (`"M3BH",5`). Keep the cam band z 18.5..29.5 clear.
* Seam: ribs only at the lower level when compact. Lower seam screws z=8, upper z=44. The upper seam screw sits in
  the strip at R29.6 (`srr = (compact && lv==1) ? 29.6 : 27`). Seam boss z `compact ? 51.5 : 63.5`; peg z `compact ? 53 : 65`.
* Tube cut-outs (docs only): start at z=8, height 42, so their lower edge clears the stop block at 90 deg; the upper
  tube butts the 4 mm stop ring at z=-11. Tube holes are centred on each strip.
* Cam peak 29 -> 28.6 mm for pillar clearance.

## Procedure
1. `python3 build_fs.py` - must report all patches (49 at last count) and V1 volumes must be identical to before.
2. `python3 pipeline.py studios` - rebuilds V1-A/V2-A (closed), V1-B/V2-B (open: 90 deg panels, 65 deg rotor, button
   up) and the samples studio. All must be feature status OK.
3. `python3 pipeline.py assemblies` - deletes and recreates ASM-V1 / ASM-V2 and clones the user's mates.
4. `python3 pipeline.py verify` - expect no printed overlaps in any of the four states, all four seam key rays "clear".
5. Latch/cam timing (keep to about 3 builds): in `scan.py` call `state(opening, release)` for
   (3 deg open, 14 deg release) -> latch still overlaps the fin lug; (3, 16) -> clear; then rotor-versus-pin
   overlap at 18/22/26 deg to confirm the cam only touches after the latch lets go.
6. Delete the scratch studio "SCRATCH - angle scan (delete)" if it exists.
7. Export: STEP (gz) and print STLs for V2 via `export_print.py` (direct STL export is blocked by the proxy, so STLs
   come from tessellation). Re-cache `fin_v2*.pkl`.
8. Figures (`figures.py`) and PDF (`python3 make_docs.py`); check the layout. Update `DESIGN_NOTES.md` and `README.md`
   with the numbers above. Remove or relabel `docs/img/v2_dz_preview.png`.
9. Commit and push to the designated branch. Do not open a pull request unless asked.

## Hard rules
* **Onshape rate limit:** the `GET /partstudios/.../features` endpoint is limited (a 429 with `Retry-After` of about
  20 h hit when an angle scan polled it dozens of times). Do one test call first. If it returns 429, report the
  `Retry-After` and stop; do not loop, and do not create throwaway studios to dodge it. Keep builds to the minimum.
* Never change V1 geometry; regression volumes must match.
* Mate values POSTed through the API did nothing and cannot be verified by script; tell the user to test the mates
  by dragging in Onshape.
* Report honestly: the latch has not been tested physically, only checked by interference geometry.
* Keep the attribution trailers on commits.
