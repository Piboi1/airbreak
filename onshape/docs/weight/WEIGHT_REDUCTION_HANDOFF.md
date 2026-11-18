# Weight reduction: handoff (BT80 cam kick-out airbrake, V5 -> V6)

Last updated 2026-11-18. Repo `piboi1/airbreak`, branch `claude/nice-maxwell-1lmh2h`, folder `onshape/`.
This file covers ONLY the weight-cutting work. The project as a whole is in `onshape/HANDOFF.md` (read sections 0.11-0.13 there too).

## 1. Where things stand (read this first)

**V6 = V5 + the thin fin "T" (+ the head-cup fixes made after the first print).** That is the user's decision of 2026-11-17:
"use the same design we have for V5, only change the fin, not the rotor; don't factor in the V6 (PDF) changes".

| Part (printed, solid PLA 1.24 g/cm3) | V5 as printed | V6 now | Change |
|---|---|---|---|
| Fin (x4) | 7,862 mm3 = 9.7 g | **6,202 mm3 = 7.7 g** | -8.2 g per set |
| Housing | 24,231 = 30.0 g | 24,231 | none |
| Rotor | 17,986 = 22.3 g | 17,986 | none |
| Head cup | 18,459 = 22.9 g (original V5) | 18,917 = 23.5 g (head-cup fixes, see HANDOFF 0.11) | +0.6 g |
| Lid | 6,506 = 8.1 g | 6,506 | none |
| **Printed set (module + head, no transition)** | **98,630 mm3 = 122.3 g** | **92,448 mm3 = 114.6 g** | **-7.7 g** |

The transition / "lower section" is NOT printed by the user and is out of scope.

## 2. Onshape (document "ARC BT80 Airbrake - V1 Screwed + V2 Compact", did `857ab7b483eda80939870e15`, wid `0766f9a969602884d82183a8`)

* **V6-A** (closed) `df77b0f7af03ef2f023357d9`, **V6-B** (open, fins 90, rotor 65) `a36e1a6855babe70de0cf59c`,
  **ASM-V6** `538c2a80795fcfa27d55859b` (32 features, all OK, same groups / 3 sliders / rotor + horn revolutes / 4 hinges as ASM-V5).
  Link: https://cad.onshape.com/documents/857ab7b483eda80939870e15/w/0766f9a969602884d82183a8/e/538c2a80795fcfa27d55859b
* V5-A / V5-B / ASM-V5 are untouched (their feature stays pinned to the old source microversion). Proof that V5 is unchanged by the new
  code: a fresh mode-5 build with all new options off matched the V5 meshes part by part (52/52).
* All ids: `docs/weight/onshape_ids.json` (copy it to `$AIRBRAKE_WORK/ids.json`). Credentials: env vars `ONSHAPE_ACCESS_KEY` / `ONSHAPE_SECRET_KEY` only.
* Tabs nobody uses: "Feature Studio 1" (user pasted the source there once; a part built from it defaults to mode 0) can be deleted.
  "V5_inner_piece_lightened_as_marked / _recommended" part studios + STL blobs were made by someone else (rotor lightening?) and were NOT reviewed.
* V6-A / V6-B tab names still say "PDF cuts + head cup fixes": rename them in the UI (the API helper has no rename).

### Options on the `modularBrake` feature (all default OFF, all need mode 5)
| Option (parameter id) | What it does | V6-A/B |
|---|---|---|
| "V6 weight reduction" (`v6`) | the PDF cuts: F1+F2 fin pockets, C1 housing floor windows, U1 head floor holes, U2 head wall relief, K1 lid recess | **OFF** |
| "Head cup fixes after the first print" (`headfix`) | wide servo arms, ledge 1.2 mm thinner, no M2 nut recess + O2.4 hole, cable slot beside the servo | **ON** |
| "Thin fin T" (`thinfin`) | 1.2 mm skin above z 11, no spine/edge ribs, two edge lips, lock-lug plate to R31.4 | **ON** |

To change a V6 option without breaking ASM-V6: `tools/v6_thinfin.py ps_v6` and `... ps_v6b` (edit the three values at the top).
It uses `POST /partstudios/.../features/updates` (BTUpdateFeaturesCall-1748). The single-feature endpoint
`.../features/featureid/{fid}` refuses a new feature-studio namespace ("Feature does not match"). Never delete and re-add the
feature: the part ids change and every assembly mate breaks (happened with V5 earlier).

## 3. History of the weight work (what was tried, what was decided)

1. **User PDF** `docs/weight/assembly_weight_reduction_proposals.pdf` (third-party FEA on our V5 STL; codes L1-L3 lower section,
   F1/F2 fins, C1 cage = housing, U1/U2 upper bay = head cup, K1 cap = lid; rotor in a separate document we never received).
   Implemented as the `v6` option (L* skipped, rotor skipped). Removed volumes matched the PDF: fin 676 (PDF 702; Onshape keeps
   the cam-pad sides the PDF pocket shaved by 0.4 mm), housing 765 (766), lid 1,385 (1,395), head U1 554 + U2 ~790
   (U2 stopped at z 86.0 so the lid keeps its full-thickness seat, and starts at z 73.1 above the rims). About 7.7 g per set.
   **Now OFF by user decision.** It still works and can be switched on together with `thinfin` (the pockets then cut nothing
   in the thin skin; the housing/head/lid cuts would add about -4.3 g).
2. **Ten fin ideas** `docs/weight/V6_fin_weight_ideas.pdf` (schematic, script `tools/fin_ideas_pdf.py`): A1 cam-latch lug,
   B pin-in-groove, C tail lever, D toggle link, K magnet lock (merge lock + push); E no ribs, F tapered skin, G/H isogrid or beads,
   I truss root, J carbon-rod spine (strip the fin). Today's fin mass split: skin 46 %, root (knuckle, web, pads, gusset, tail) 35 %,
   push pad 7 %, lock lug 4 %, ribs 9 %.
3. **Option B simulated** `docs/weight/option_B_simulation.mp4|gif|_still.png` (script `tools/sim_option_b.py`, kinematics only).
   Findings: the pin must sit on a ~6.8 mm lever under the hinge (high on the fin it travels out of the tube); the rotor track
   must twist 90 deg along its length; peak 4.5 fin-deg per rotor-deg, so closing against airflow would need ~15x the SG90 torque.
   Works on paper, needs a new rotor. **User then chose: no rotor change.**
4. **Fin study with the V5 rotor** (`tools/fin_variants.py` rebuilds the V5 fin offline from the FeatureScript recipe, within 4 mm3
   of Onshape; `tools/fin_compare.py` runs the voxel FEA of `tools/fea_fin.py`: open fin, pin + stop supports, PLA E 3 GPa,
   0.8 mm voxels). Results `docs/weight/fin_compare_results.json`:

| Variant | Solid g | Peak von Mises 12 N / 30 N face, 15 N tip (MPa) | Tip deflection at 30 N |
|---|---|---|---|
| V5 as printed | 9.75 | 4.1 / 10.2 / 9.7 | 0.72 mm |
| PDF pockets F1+F2 | 9.07 | 6.4 / **16.0** / 15.5 (pocket corner) | 0.79 |
| E no ribs + edge lips | 9.34 | 3.9 / 9.7 / 9.0 | 0.68 |
| EF + skin taper 2.4->1.2 | 8.37 | 4.1 / 10.3 / 8.9 | 0.74 |
| EFI + gusset windows | 8.37 | same as EF (windows removed 2 mm3: the gusset overlaps other root solids) | |
| J 1.2 skin + 1.5 mm carbon rod | 7.78 + 0.12 rod | 4.1 / 10.3 / 9.6 | 0.68 |
| **T 1.2 skin, no ribs, no rod (CHOSEN)** | **7.68** | **4.2 / 10.5 / 10.2** | **0.77** |

   Key finding: in every variant the peak is at the hinge root on the 90-deg stop (x 30.4, y 7.2, z 0.8 in the open pose); the skin
   and ribs carry little. All are well under the ~15 MPa across-layer strength assumed for PLA. Caveat: 0.8 mm voxels resolve a 1.2 mm
   skin with 1-2 elements, so the thin-skin numbers are approximate; impact, handling and layer adhesion are not modelled.
5. **Built T in Onshape** (2026-11-17). Bug found and fixed: with the 1.2 mm skin (inner face R31.0) the lock-lug plate (to R30.6)
   no longer touched the skin and Onshape made four loose "Part N" bodies; the plate now goes to R31.4 when `thinfin` is on.

## 4. Files

| What | Where |
|---|---|
| This handoff | `docs/weight/WEIGHT_REDUCTION_HANDOFF.md` |
| User's PDF (input) | `docs/weight/assembly_weight_reduction_proposals.pdf` |
| Ten ideas (drawing) | `docs/weight/V6_fin_weight_ideas.pdf` |
| Option B simulation | `docs/weight/option_B_simulation.mp4`, `.gif`, `_still.png` |
| Fin FEA results | `docs/weight/fin_compare_results.json` |
| Onshape ids | `docs/weight/onshape_ids.json` |
| V6 print set (from Onshape V6-A) | `exports/v6/print/*.stl` + `PRINT_README.md`; plates `exports/v6/P1S_plate1.3mf`, `P1S_plate2.3mf` (about 92 g each with supports, estimate) |
| FeatureScript source (generated) | `fs/airbrake_v1_v2.fs` from `tools/build_fs.py` + `tools/build_fs_v5.py` (V6 patches at the end of build_fs_v5.py) |
| Onshape scripts | `tools/v6_onshape.py` (first V6 build), `tools/v6_thinfin.py` (in-place option update), `tools/export_print.py`, `tools/p1s_two_plates.py` (`PRINT_SET=v6`) |
| Offline scripts | `tools/v6cuts.py` (the PDF cut tools on meshes, used for the first offline V6 STLs; superseded by the FeatureScript), `tools/fin_variants.py`, `tools/fin_compare.py [name]`, `tools/fea_fin.py`, `tools/fin_ideas_pdf.py`, `tools/sim_option_b.py` |
| API budget rules + call log | `docs/ONSHAPE_API_BUDGET.md`, `api_calls.log` (one line per request, committed) |

## 5. How to resume

```bash
cd onshape/tools && export AIRBRAKE_WORK=<scratch dir> && mkdir -p $AIRBRAKE_WORK && cp ../docs/weight/onshape_ids.json $AIRBRAKE_WORK/ids.json
python3 build_fs.py                         # regenerate fs/airbrake_v1_v2.fs (offline)
python3 fin_variants.py                     # offline: rebuilt V5 fin vs Onshape needs $AIRBRAKE_WORK/fin_v5.pkl (download costs 1 request)
python3 fin_compare.py "T:"                 # offline FEA of one variant (~7 min); needs fin_v5b.pkl for the housing supports
```
Cached meshes (`fin_v5.pkl`, `fin_v5b.pkl`, `fin_v6t.pkl`) are NOT in the repo; `geom.fetch_parts(did, wid, eid)` downloads one part studio in 1 request.
Python deps used: trimesh + manifold3d, shapely, scikit-fem, pyamg, matplotlib.

## 6. Onshape API budget (hard limit)

The user has **2,500 requests in total, no more will be granted**. About 28 used so far by logged runs (`wc -l onshape/api_calls.log`;
the first V6 build, ~70, happened before logging). `tools/osapi.py` prints used/left each run, stops a run at 100 requests, and refuses the
last 200 unless `ONSHAPE_USE_RESERVE=yes` after the user agrees. Rules (full text `docs/ONSHAPE_API_BUDGET.md`): offline first, one build
per batch, say the cost first and ask above 30, update features in place, never rebuild an assembly from scratch without asking.
Typical costs: upload source 3, update one part studio in place 2-3, download meshes 1, STL export of a studio 1.

## 7. Open items and ideas not done

* **Print and hand-test fin T** (at least 3 walls with a 0.4 mm nozzle; the 1.2 mm skin must print solid). Nothing V6 has been printed.
* Optional finer FEA of T (0.4-0.5 mm voxels) to firm up the thin-skin numbers (offline, slow).
* The root zone is 35 % of the fin and carries the peak stress: the obvious next target, but only with an FEA check (the simple
  "gusset windows" try removed almost nothing).
* PDF cuts on housing / head / lid (`v6` option) are ready if the user changes their mind: about -4.3 g more.
* Rotor: the PDF's rotor proposals (separate document) were never received; the user said the rotor stays as V5.
* Bigger ideas that need a new rotor (B, C, D, A1) are documented but parked.

## 8. User rules that apply to any weight change

M3 bolts and nuts wherever possible (no heat-set inserts); all bolts radial from the outside through the BT80 tube, BT80 side only;
never touch the BT70 side; no snap hooks or bands (ask before using magnets); housing in one piece; never write the Onshape keys to files;
no pull request unless asked; outer (aero) surfaces stay as they are.
