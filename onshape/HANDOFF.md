# HANDOFF: BT80 cam kick-out airbrake CAD project (V1 to V5 built; V5 = modular, not printed)

Read this first. It is written so a new agent can continue with no other context. Repo: `piboi1/airbreak`, branch
`claude/nice-maxwell-1lmh2h`, folder `onshape/`. Everything described here is committed and pushed. Do not open a pull request unless the user asks.

## 0. Where we are now: V5 (modular design) is BUILT and checked in CAD (not printed). Read this section first.

V1 to V4 are built (sections 2 to 7). The user wanted a **modular** version because the airbrake will break every flight and they want to swap the whole module. After a long design conversation and the go-ahead
("go ahead and build V5") it was built as **mode 5** of the same FeatureScript. Current picture: `docs/V5_assembly_guide.pdf` (what is built) and `docs/V5_complete_concept.pdf` (the idea and the decisions).

### 0.1 What V5 is (all numbers from the CAD model; V4 frame: rotor axis z, module bottom z = -10, housing top 58.8)

* **Stack, nose up:** upper airframe, then **one BT80 tube cut once** (R32.51/R33.02, the skin) around the **head** (z 59.0..88.3) and the **module** (z -10..58.8), then the **transition** (BT80 side: shoulder R26.0..32.2 z -34..-22, plug R26.0..29.6 z -22..-10.2 = the module seat). The BT70 side is **not touched**; the cone is a placeholder.
* **Module** (the part that breaks, about 85 g solid PLA): one-piece housing (OD 64.4, no seam, no pegs, no seam screws, floor plate with an 8 mm hole), rotor with **integral catch caps** (no cap screws), 4 fins (same shape, **M3x25 hinge bolt + nut** in the +Y ear slot). The **limiter finger and its two stops are above the bearing ring** (finger z 6.4..11.6, stops z 0.4..14), which is what makes the one-piece housing possible: the rotor drops in from the top at any angle 0..60 deg.
* **Head** (reusable, about 33 g + electronics): cup (sleeve, floor z 68.5..70.3, two servo ledge posts at 135/315 deg hanging to z 45.1, pockets for the 2S battery, Mercury V1 and the regulator stood on its edge, vents, USB-C window, switch slot, cable slot) + lid (disc + 4 nut bosses). The SG90 horn drops into the rotor hub socket (tapered lead-in, about +-10 deg): no wire crosses a joint.
* **Fasteners (user's rules kept):** 12 radial **M3x8 button head bolts + nuts** from the outside through the tube, BT80 side only, in **three independent sets of 4**: set 1 head (z 82, azimuth 45/135/250/290; the nuts are in the **lid** bosses, the bolts clamp cup and lid together), set 2 module (z 12, azimuth 45+90k, nuts in hex pockets in wall bosses), set 3 transition (z -28, azimuth 45+90k, nuts in hex pockets in the shoulder). All pockets are hexagons open to the inside. Tube holes are plain clearance holes cut once; a new module reuses the same 12. Plus 4 hinge M3x25 + nut, 2 M2x6 servo bolts + M2 nuts, 1 horn screw: **19 fasteners** (V4: 27). No heat-set inserts, no self-tapping, no snap hooks, no bands.
* **Swap (8 bolts, the head stays):** route 1 (main) out of the bottom: transition bolts, transition out, module bolts, module out. Route 2 (the user asked for it too): head bolts, head out of the top, module bolts, module out of the top (needs the upper airframe separated at the top of the tube: **assumption, not confirmed by the user**). Both routes are collision-free in the CAD.
* **Windows** stay open (67 deg x 63.8 mm, z -9.2..54.6, tape optional, not decided). USB-C window (9.2 x 3.4), switch slot (12 x 6) and 3 vents O3 (z 74..75) are provisional.
* Solid PLA: (first version; see 0.8 for the current masses) housing 29.4 g, rotor 22.4 g, fins 4 x 8.3 g, head cup 25.0 g, lid 8.1 g, transition 41.3 g (placeholder cone). Overall module bottom to head top 98.3 mm.

### 0.2 Onshape, repo, and how to rebuild V5

* Onshape (same document, section 3): `ps_v5` = **V5-A** closed `ec80a21d010785fb8bbefb14`, `ps_v5b` = **V5-B** open (fins 90, rotor 65) `5e34f91d2af57a906275e874`, `asm_v5` = **ASM-V5** `c947dbebb0f6cd9d5c33ae21` (17 features, all OK). Add these to `ids.json`.
* **Elements in the document that were NOT made by this build** and were left untouched: `V5 isolated modular source - preserves V1 to V4` (`08a1a1ab4b63f93ea25787b8`), `V5 - removable module and reusable head` (`2854463aa1ae4b58be7d12f4`), and an assembly `V5 modular assembly` with its BOM, created 2026-11-03 15:55 to 15:58 UTC by another Onshape user id. The user says a friend made them. Compared with this build on 2026-11-03 (section 0.7). An earlier version of this note claimed a battery-corner clash in their head; that was wrong (their cup is only 12.6 mm tall and the electronics sit above it, inside the tube). Ask the user what to do with them.
* Source: `tools/build_fs.py` now ends with `exec(tools/build_fs_v5.py)` (the mode-5 patches, 118 patches in all). Mode 5 = `mono` flag in `camKickBrake` (module) plus a `definition.mode==5` block in `modularBrake` (head, transition, tube, hardware). V1..V4 are guarded off and stay volume-identical.
* Rebuild and check: `export AIRBRAKE_WORK=<scratch>` (needs `ids.json`, section 4), `python3 tools/rebuild_v5.py` (generate, upload, build V5-A and V5-B, cache `fin_v5.pkl` and `fin_v5b.pkl`), `python3 tools/check_v5.py all` (offline), `python3 tools/regress_v1v4.py` (rebuilds V1..V4 in scratch studios and compares every part volume with baselines `base_<tag>_parts.pkl` taken with `check.py` BEFORE changing the script; deletes the scratch studios), `python3 tools/v5_sections.py`, `python3 tools/make_figs_v5.py`, `python3 tools/make_docs_v5.py`.
* Export used: `export_print.export('ps_v5','../exports/v5/print','v5',names={'C':'module_housing','R':'rotor','P1':'fin','H':'head_cup','K':'head_lid','T':'transition_BT80_side_PLACEHOLDER_cone'},force={'R':1})` (rotor forced hub-down), STEP with `osapi.export_step`.
* Pip packages the scripts need in a fresh container: trimesh manifold3d scipy shapely networkx rtree numba matplotlib reportlab pillow requests.

### 0.3 What was checked (offline on the exported meshes unless stated)

No printed overlaps closed or open (only the SG90 spline in the horn and the horn screw in horn and servo, reference parts); no non-watertight bodies; fin opening 0..90 clear of housing, tube, head; latch holds from about 1.5 deg of fin opening, frees at about 14 deg of rotor travel, cam first touches at about 25.5 deg, limiter stops at about -2 and +66.5 deg (the V4 margin); rotor drop-in from the top free for 0..60 deg; fins install radially through the windows only with the rotor parked at about 14..24 deg; hinge nut loading, hinge bolt and key lines clear; head lowers onto the module clear with the horn within +-3 deg (the tapered socket must do the rest, not measurable offline); both exit routes clear; 2.0 mm key reaches all 12 radial bolts; V1..V4 volumes identical in all 8 states (checked after the last mode-5 change that touches shared code; re-run `regress_v1v4.py` after any further edit). ASM-V5 mates are built (OK) but **mate motion has not been driven** (the API cannot): tell the user to drag a fin and the rotor.

### 0.4 Findings and design choices that surprised

* The hinge bolts cannot be tightened through the tube windows with a straight key (it would need about 40 deg of tilt), so each hinge has a 6.6 mm channel through the housing wall along the hinge axis: **hinge bolts are bench-only (module out of the tube)**.
* The lid has no snap hook, so the set-1 bolts pass through the cup wall into nuts in **lid** bosses (not into bosses of the sleeve as the concept sheets say). Until bolted the lid just lies on the cup (hold it with masking tape while sliding the head in).
* V4 had the hinge ears (R5.2 about x=25, out to y=12) and the hard-stop block corner reaching R32.5 to R32.6, i.e. touching the tube; V5 trims them (ears R4.9, block R31.6) so the housing stays inside R32.2.
* The catch finger was 0.2 mm proud of the hub top; V5 makes it flush so the rotor prints hub-down on one plane.
* The rotor is **not axially retained** in the module (the head holds it down, 0.6 mm above the hub). A keeper would have to be a snap hook or a band, so none was added: carry the module upright.
* Assembly order that works: nuts into the housing wall pockets, rotor in from the top (park at about 18 deg), fins in through the windows with hinge nuts and bolts, rotor back to 0. Head cup: M2 nuts into the ledge pockets, servo, electronics, lid nuts, lid. Then head into the tube from the bottom, module from the bottom, transition from the bottom.

### 0.5 Open items for the next agent and the user

1. **Confirm route 2** (the upper airframe separates at the top of this tube).
2. The **transition**: the user does not know its diameters. The cone and the BT70 side are placeholders; the BT70 ID is needed.
3. **Windows open or taped** (still undecided).
4. **Delete or keep** the two other-session V5 elements (see 0.2).
5. Electronics layout is from catalogue sizes (battery 42 x 19 x 12, Mercury 30 x 16.9 x 10.8, regulator 25 x 15 x 8 placeholder); USB-C window, switch slot, vents, servo cable slot positions are provisional; SG90 and horn numbers are standard values (measure the real ones).
6. Nothing has been printed. Ground-impact FEA has still not been done. First places to look: lid bosses, nut bosses in the 2.7 mm housing wall, servo ledges (2.4 mm under the nut pocket), limiter stops, hinge ears and bolts.
7. Possible improvement: a printed keeper for the rotor would need a rule exception (snap hook or band).

### 0.7 Comparison with the friend's V5 (elements `V5 isolated modular source...`, `V5 - removable module and reusable head`, `V5 modular assembly`)

Same checks run on their part studio (50 parts, mesh shifted by -10 z to the V4 frame; script was in the scratchpad, same functions as `check_v5.py`).
* **Same base and almost the same numbers:** both derive from V4 with R32.2 / inner R29.48 housing, limiter above the ring, integral catches, M3 hinge nut slot at the same place (x 22.1..27.9, y 9.2..12.2), 12 radial bolts, plug R26.0..29.6 and shoulder R26.0..32.3. Results are the same to the digit where the geometry is shared: limiter stops at -2 / +66.5 deg, cam first contact 25.5 deg, latch holds from 1.5 deg and frees at about 14 deg, rotor drop-in free at any angle, fin install needs the rotor at about 14..24 deg, head insertion clear within +-3 deg, both exit routes clear, no printed overlaps, no non-watertight bodies, housing clear of the tube.
* **Theirs is better at:** the assembly (29 features: head-removal and transition-removal slide mates, a module service slide, rotor 0..65, horn angle, four fin hinges 0..90; mine has only the 4 hinges and the rotor revolute), the datum (module bottom z = 0 like the concept sheets; mine stays in the V4 frame), a lighter head (cup 15 g + cap 10 g + tray 5 g), and simplicity of isolation (a separate studio, V1..V4 untouched by construction).
* **Mine is better at:** hinge bolt access (theirs has no channel: the line along the hinge axis from outside is blocked by the housing wall, 77 mm3 for the head and 15 mm3 for a 2.4 mm key, so their hinge bolts cannot be fitted or tightened with a straight key); a full sleeve around the electronics with pockets, vents, USB-C window and switch slot cut in the cup as well as the tube (theirs: electronics sit in the tube above a short cup, a tray with adhesive retention, only the tube is cut); a placeholder transition cone; a regression proof (V1..V4 volumes identical in 8 states), offline mechanism checks, STL and STEP exports, drawings, documents and this handoff in the repo (theirs exists only inside Onshape, no exports or docs).
* **Different choices, neither clearly better:** their cap legs run in tracks in the sleeve and are captured by the head bolts (mine: lid bosses with nuts); square nut slots with an entry (mine: hex pockets); servo M2 nut pocket from below (mine: from the top under the tab); head bolts at z 64.8 (mine z 82); they copied `camKickBrake` into a second function (`v5Core`, about 380 lines duplicated), I patched the shared one.
* Obvious merge: add their service-slide mates to `asm.build_v5`, and add my hinge access channels to their housing.

### 0.8 After the first print (friend's V5 was printed; photos received 2026-11-04) and what was changed

Problems reported by the user: (1) fins very flimsy, nearly snap when pushed past 90 deg, they want more tension or a lock under the hinge, with a mentor CAD picture as inspiration; (2) the part that houses the servo does not go far enough into the hole, so it stands proud of flush.
* **Mentor picture (not certain):** a bottom view of a cross-shaped hub; each arm has two hinge lugs and a deep U-shaped pocket under the hinge with a wide dark-blue tab from the flap sitting in it. I read it as "tab in a U pocket under the hinge". **Ask the user whether that is what the lock does.**
* **FEA first** (`tools/fea_fin.py`; voxel hex mesh, scikit-fem, pyamg, PLA E 3 GPa, nu 0.35, 0.8 mm voxels, pin and stop rigid; flight airflow pushes an open fin INTO its stop, so past-90 is a real load): first V5 peak 8.0 / 20.1 / 15.8 MPa at 12 N airflow / 30 N airflow / 15 N tip push, hot spot where the narrow root gusset ends (loaded across layers when printed flat; stop contact almost under the pin). Now 4.0 / 9.9 / 9.6 MPa. Pin load with the keeper engaged drops from 10 / 25 / 22 N to 1 / 3 / 1 N. Caveats: isotropic, rigid supports, voxel stair-steps, ears/bolt/housing not modelled; the remaining peaks are at the ear-clearance notch in the gusset and at the shell edge in the cam-band gap. **No physical test.**
* **Fin changes (mono only, `build_fs_v5.py` sections V5.1, V5.2, V5.4):** wide tapered gusset (14 to 24 mm, wings start z 6.0 so the ear-clearance cut does not notch them, top z 22.5), root pad R27.8..31.3 +-27 deg z 4..20, arc landing, arc outer stop block (R27..31.9, +-24 deg, top z -6.6), root clipped to R32.21, spine rib (z 4..20.5 and 28.5..47, upper part inner face R27.5 because the cap corner reaches R27.0) and two edge ribs (+-27.5 deg, z 4..20 and 30..54). **Lock:** tail on each fin (x 22..26.5, y +-6, z -7.6..-3), U pocket in the stop blocks (x 21.6..33.5, y +-6.5, z -8.3..-6.4; the floor plate top at z -8.0 limits the tail to z -7.6), keeper towers (x 17.5..21.4, |y| 7.8..11.2, z -9..6.4) and pads (x 17.5..20.0, |y| 4.6..7.8, z 3.4..6.4). Tail meets the pads at about 91 deg. Limiter stop 2 trimmed to R10..16.5 and y 3.4..8.0 (its corner reached R18 and hit fin 3's tail).
* **Head changes (section V5.3):** most likely cause of problem 2 (not seen in the print): a real SG90 has a raised gear boss (about O11.8 x 4.5) and a longer spline (about 4 mm) that the model did not have, so the boss sat on the rotor hub top. Now modelled; hub R10.5 with a O13.2 counterbore (stepped lead-in), horn socket floor at z 35.0 (10 mm deep), head sleeve R31.95 (was 32.2) with 0.8 mm chamfer, module lower outer edge chamfered. Head cup lands on the housing first (0.2 mm), everything in the servo/rotor stack has 0.6 mm or more. **Ask the user for their servo's real dimensions and, if it still stands proud, by how much and whether it rocks.**
* **Checks after the changes:** `check_v5.py all` pass (no overlaps closed or open, fin 1..4 opening sweep clear, keeper meets tail at about 91 deg, timing unchanged, drop-in free, install window unchanged, exit routes clear, key access clear); `regress_v1v4.py` identical in 8 states. New solid PLA masses: housing 30.0 g, rotor 22.3 g, fins 4 x 9.8 g (module about 91 g), head cup 23.1 g + lid 8.1 g.
* **Onshape ids changed:** V5-A / V5-B were rebuilt in place (same ids), which regenerates part ids and breaks every mate in the assembly, so **ASM-V5 was deleted and recreated: new id `c947dbebb0f6cd9d5c33ae21`**. Any later in-place rebuild of V5-A needs the same (`asm.build_v5`).
* **RATE LIMIT WARNING:** `GET /partstudios/.../features` is limited to about 100 calls per session window (429 with a very long Retry-After). This session used almost all of it (`run.go`/`run.build` make 2 per build). Use `tools/lean_v5.py` (builds in new scratch studios, no such calls, deletes them) for exploration and `regress_v1v4.py` (also lean now). Only rebuild the real V5-A/B once at the end. If the limit is hit, create new studios instead of rebuilding in place.
* New tools: `fea_fin.py` (`python3 fea_fin.py fin_v5b keeper`, about 12 min, run it in the background), `lean_v5.py`, `proto_lock.py` / `proto_lock2.py` (mesh-space prototype of the lock). Extra pip packages: gmsh (needs `apt-get install libglu1-mesa`, not actually used), scikit-fem, pyamg, meshio.
* Open: confirm the lock reading; servo dimensions; reprint the fins (PETG or PLA+, 4+ walls) and hand-test; hinge ears/bolt/housing FEA still not done; edge rib in the cam-band gap is missing (shell edge is the tip-case peak); electronics and the transition are unchanged from section 0.1.

### 0.6 Superseded concept documents (kept in `docs/` for the history)

`V5_sketch4_how_it_fits.pdf`, `V5_sketch3_*`, `V5_sketch2_*`, `V5_final_plan.pdf`, `V5_insert_*`, `V5_modular_concept.pdf`, `V5_choice*`, `V5_skin_cutting_template_1to1.pdf`, `V5_sketch_transition.pdf`: concept sheets from before the build (see the old list in the git history of this file). `V5_complete_concept.pdf` is the one-document summary of the idea and decisions; `V5_assembly_guide.pdf` is current.


## 1. The project and the user

* The user is building a **BT80 (66.04 mm OD, 65 mm ID) rocket airbrake**: four fins hinged at the bottom, opened by a
  four-lobe cam rotor, held shut by a rotor-mounted latch, finished open by the airflow against a 90 deg hard stop.
* Their original FeatureScript is `onshape/fs/v0_original.fs` ("REINFORCED BOTTOM SPRING - 90 DEG", unchanged). Everything
  else is generated from it. They also have wind-tunnel logs and an SG90 servo.
* What the user wants and how they work: short plain answers, files they can open (PDFs, STL/STEP, Onshape links), honest
  statements of what was and was not verified. They make the design decisions; ask only when blocked, otherwise state the
  assumption and proceed. They prefer small overall size and light weight. They sometimes type quickly with typos.
* The user's own Onshape document (ARC) is read-only for us and is only used as a mate template (see `asm.py`).

## 2. State: five design versions, all built, verified and exported (V5 not printed)

| Version | What it is | Housing | Overall | Printed (solid PLA) | Status |
|---|---|---|---|---|---|
| Original | user's bonded model | 118 mm | 178.5 mm | 177 g | reference only |
| **V1** | same machine, screwed (M3/M4), assembly doc | 118 | 178.5 | 180 g | done, unchanged since |
| **V2** | compact head inside the upper BT80 tube, tube slits with cut-outs glued to fins, new inward-lug + finger latch, fin top at head rim (22 mm latch drop) | 91.8 | 152.3 | 169 g | done |
| **V3** | SG90 straight on the rotor (no spring cartridge/trigger), servo inside the housing, flush with the bottom | 91.8 | 91.8 | 106 g | done |
| **V5** (latest) | modular: one BT80 tube is the skin; one-piece module (limiter above the ring, integral caps, M3 hinges) + head (SG90, electronics) + transition, 12 radial M3 bolts + nuts | 68.8 (module) | 98.3 (module bottom to head top) | module 85 g + head 33 g + transition 41 g (placeholder cone) | built, checked, awaiting print and the user's open items (0.5) |
| **V4** | servo flipped on top, thicker limiter/rotor parts, limiter moved to the bottom, electronics bay + sled, screwed transition ring | 96.3 | 105.4 (housing bottom to servo top) | 144 g (114 core + 16 sled + 15 transition) | done, awaiting user decisions below |

Why each switch happened is in `docs/Design_history.pdf` (decision log, problems and fixes). Read it.

## 3. Onshape

* Document (public: the Free plan cannot make private ones; the user agreed): did `857ab7b483eda80939870e15`, workspace
  `0766f9a969602884d82183a8`. Base URL: `https://cad.onshape.com/documents/<did>/w/<wid>/e/<element>`.
* Credentials: environment variables `ONSHAPE_ACCESS_KEY`, `ONSHAPE_SECRET_KEY`. Never write them to files.

| Element | Id |
|---|---|
| Feature Studio (generated script, mode 0..4) `fs1` | `5ff432bb0bc45131b59976ae` |
| baseline source studio `fs0` / baseline part studio `ps0` | `f8f79c29ea4c3b2eabd8bfc8` / `23745d0155ceb52b2585ff4d` |
| V1-A closed `ps_v1` / V1-B open `ps_v1b` | `5111d252de0ed0294a57f7b6` / `0ad5bd05e1b6d6ab296876e3` |
| V2-A `ps_v2` / V2-B `ps_v2b` | `2cae62bce6e566d22a9c55a9` / `649143a0df69740fc7fdfcd9` |
| V3-A `ps_v3` / V3-B `ps_v3b` | `10228180fc79ac2c18e92fee` / `e85dec97c151bc7f26e20bb2` |
| V4-A `ps_v4` / V4-B `ps_v4b` | `19b7c72543265f4ef8c3ee68` / `5e42421044190c404c738332` |
| samples (unloaded springs, return leaf) `ps_samples` | `0cc7c62affc5473c214dffff` |
| ASM-V1 / ASM-V2 | `2cc2089145215269219759e4` / `c123d3b7a80e1ab4ae20ec9f` |
| V5-A closed `ps_v5` / V5-B open `ps_v5b` | `ec80a21d010785fb8bbefb14` / `5e34f91d2af57a906275e874` |
| **ASM-V5 (current)** `asm_v5` | `c947dbebb0f6cd9d5c33ae21` |
| ASM-V3 / ASM-V4 | `d071de26baa2e2f9ef97f361` / `0f89bdc00682e78b6530c87f` (rebuilt after the wiring changes) |

**Correction:** an ASM-V3 link given to the user earlier in the session (`...a9209e15056d0ed7042f93da`) is dead: the
assembly was deleted and recreated when V3 was rebuilt flush. Give the user the id above.

* The user's template assembly (read-only, mates are cloned from it by `tools/asm.py`):
  `did 6193289111e752b62699c37d / wid ac364bd1a753715c132e3c3c / eid 3e8c606f5c7627b828b8947f`.

### API rules learned the hard way

* `GET /partstudios/.../features` is **rate limited** (about 100 calls, then HTTP 429 with a `Retry-After` of about 20 h; it
  happened once after a scan polled it dozens of times). One build costs about 2 to 4 of these calls. **Never poll it or loop
  on it; make one test call first; prefer offline checks on cached meshes.** Tessellation, shaded views, STEP translations,
  assembly and element endpoints were not limited.
* Direct STL export is blocked by the proxy: STLs are built from `tessellatedfaces` (`geom.fetch_parts`), STEP through
  `osapi.export_step`. `ps_scan`-style scratch studios must be deleted when done.
* Mate values cannot be driven through the API (a POST did nothing). Mate motion has never been verified by script: tell the
  user to drag the rotor and a fin in the assembly.
* The session's WebFetch cannot reach `altimetercloud.com` or `pololu.com` (blocked hosts); WebSearch works. Ask the user to
  paste or screenshot manuals if you need them.

## 4. Repository map (`onshape/`)

* `fs/v0_original.fs` (user's, untouched), `fs/airbrake_v1_v2.fs` (**generated, do not edit by hand**).
* `tools/build_fs.py` generates the script from the original by exact, asserted string patches `P(old, new)`; every patch must
  match exactly once. `PATCH_LIMIT=n python3 build_fs.py` applies only the first n patches (used to bisect a compile error).
* `tools/osapi.py` (REST), `run.py` (upload FS, build a studio, params), `check.py` (fetch parts to a pickle),
  `geom.py` (tessellation to trimesh, interference), `asm.py` (`build`, `build_v3`, `build_v4`: groups + mates cloned from the
  user's assembly), `pipeline.py` (rebuild V1/V2 studios, assemblies, verify), `export_print.py` (print STLs; pass `names=` for
  V4), `render.py` + `figures.py` (own z-buffer renderer and figure helpers), `diagrams.py` (tube templates),
  `sweep_open.py`, `sweep_rotor.py`, `sweep_rotor_v4.py`, `timing_offline.py` (offline checks), `mech_*.py`, `history_figs.py`,
  `v4_sketch.py`, `wiring_schematic.py`, `make_figs_v2/v3/v4.py`, `make_docs.py` (all PDFs), `torque_check.py`.
* V5 tools: `build_fs_v5.py` (mode-5 patches, exec'd by `build_fs.py`), `rebuild_v5.py`, `check_v5.py`, `regress_v1v4.py`, `v5_sections.py`, `make_figs_v5.py`, `make_docs_v5.py`, `v5_overview.py`; `asm.build_v5`; `export_print.export(..., force={tok: candidate})`. `exports/v5/` (STEP + print STLs).
* `docs/*.pdf`: `V1/V2/V3/V4_assembly_guide`, `V3_mechanics_diagrams`, `Design_history`, `V4_concept_sketch`,
  `V4_power_and_wiring`, `V4_wiring_layout_plan`, and the `V5_*` concept sheets (section 0.4). `docs/img` holds figures. `exports/v1..v4/print/*.stl` (one file per unique part, `_xN` = quantity)
  and `exports/v*/*.step.gz` (closed state with hardware and reference tubes).
* `DESIGN_NOTES.md` (numbers per version), `README.md`, `V2_22mm_BUILD_PROMPT.md` (a design-only prompt for the V2).

### Working directory

Scripts need `export AIRBRAKE_WORK=<scratch folder>`. It holds `ids.json` (the Onshape ids above: recreate it from the table,
keys `did wid fs0 ps0 fs1 ps_v1 ps_v2 ps_v1b ps_v2b ps_samples asm_v1 asm_v2 ps_v3 ps_v3b asm_v3 ps_v4 ps_v4b asm_v4`), cached
meshes (`fin_v1.pkl`, `fin_v2.pkl`, `fin_v3.pkl`, `fin_v4.pkl`, `*b.pkl` for open states, `*_parts.pkl` are the same data),
`mech_data.json`, `scan.json` (read by `make_docs.py` for the V2 latch numbers) and `fig/` (figure PNGs). **The previous scratch
folder is not in the repo and will be gone:** regenerate pickles with `python3 check.py fin_v4 ps_v4` then
`cp <work>/fin_v4_parts.pkl <work>/fin_v4.pkl` (same for the others), and the figures with the `make_figs_*.py` scripts.

## 5. FeatureScript architecture and the traps

* One feature `modularBrake` with `mode`: 0 spring cartridge (user's), 1 user's direct servo, 2 spring samples,
  **3 = V3, 4 = V4, 5 = V5** (`mono` flag, see section 0). Boolean `compact` = V2 head (always on for V2/V3/V4). `camKickBrake` takes `direct` (mode 3) and `flip`
  (mode 4) so shared geometry changes only under those flags. V1/V2/V3 geometry must stay **volume-identical** after any change:
  rebuild them and compare part volumes against the cached pickles (done after the V4 work, all identical).
* Traps that already cost time: (1) `flip?[a,b]:[c]` fails to compile because `?[` is one token: write `flip ? [a] : [b]`;
  an empty `featureSpecs` from `osapi.fs_specs(...)` means the script does not compile (the part studio still says OK with
  zero bodies); (2) a box whose face is only tangent to a cylinder does not union (stray `Part N` bodies): overlap them;
  (3) any new body must overlap what it should join, and floating bodies show up as unnamed `Part N`; (4) the seam
  pegs, the support strips and the base ring interact with every change near z = -15..-11; (5) `radialBox(r0,r1,y0,y1,z,h,a)`
  is x = radial, y = tangential, z = start and height.
* Key coordinates (mm, z up, rotor axis = z): fin hinge axis at R25, z 0; fins z 4..54; cam follower on the fin z 20..29;
  fin lug wall R20..22.8 z 41.6..50 and plate z 47..50; windows z -9.2..54.6 (63.8 tall: the reference tube once had 60.2, a bug,
  fixed); housing top 58.8; supports in the strips between fins; seam plane at 45/225 deg.
* **V4 specifics:** servo flipped on top, long axis at 135/315 deg, tabs z 49.4..51.9 on ledges z 45.1..49.4 at 135/315 deg
  (they must sit above the catch-cap fingers, which sweep every azimuth), servo body z 45.2..67.9 (9.1 mm above the housing).
  Rotor shaft z -6.4..44.6, hub R9 z 33.6..44.6 with a horn pocket open at the top, arms 8 x 5 mm z 33.6..38.6, cam web 5.5 mm
  z 22.5..28, collar z 3.9..5.9 above a 3 mm bearing z 0.4..3.4, limiter finger 6 mm z -5.6..-0.4 (rest az 60 deg) with two
  7.6 mm stops hung from the lower spokes (engages at -3 and 67 deg). Bay ceiling z -10..-8 with a centre wire hole; lower sleeve
  to z -35.5; four bosses with M3x10 into a transition ring (R23.5..32.3, z -43.5..-35.5, bonded in the lower BT80 tube).
  Electronics are reference bodies: Mercury V1 30 x 16.9 x 10.8, a 25 x 15 x 8 regulator, a Spektrum 300 mAh 2S battery 42 x 19 x 12 (sled pocket 42.8 x 19.8 x 12.4; regulator is still a placeholder).

## 6. How to rebuild and verify

1. `python3 build_fs.py` (check the patch count and "wrote ..."), then `run.go(key, 'fs1', 'modularBrake', name, run.params(mode=.., opening=.., release=.., button=.., compact=True))`.
   Closed state = defaults; open state = `opening=90, release=65, button=4.5`.
2. `check.py` to cache meshes, then `geom.interference(parts, min_vol=0.05)`: expect only the servo spline inside the horn (32.45 mm3)
   and the reference upper tube touching the housing (0.86 mm3), no printed-part overlaps, no non-watertight bodies.
3. Offline sweeps (no API): `sweep_rotor_v4.py` (rotor angles -3..68), `timing_offline.py fin_v4_parts` (latch holds from about 1.5 deg of
   fin opening, frees at about 15 deg of rotor travel, cam first touches at about 26 deg and kicks the fin to about 14 deg), fin sweep with `sweep_open.py`.
   Seam hex-key access ray test is in `pipeline.verify` and was repeated in the V3/V4 builds.
4. Assembly: delete and recreate the assembly element, insert the whole part studio, `asm.build_v4(aid)` (21 features, all OK).
5. Export: `export_print.export('ps_v4', '../exports/v4/print', 'v4', names={...})` and `osapi.export_step`; figures with `make_figs_v4.py`;
   documents with `python3 make_docs.py v1 v2 v3 mech history sketch v4 wiring` (any subset).
6. Update `DESIGN_NOTES.md`, `README.md`, `docs/Design_history.pdf` if numbers change. Commit with the attribution trailers your
   session instructs, push to the branch above.

## 7. Open items and decisions waiting on the user

1. **Battery: resized for the Spektrum 300 mAh 2S (42 x 19 x 12 mm as listed by one retailer).** Sled pocket 42.8 x 19.8 x 12.4, lower sled block 46.8 x 23.8 clipped to R25.5,
   floor between the layers 1.8 mm (the housing later grew 2 mm for wiring, see 1c). Measure the real pack. The pocket is open at the bottom: a belly band (nylon tie or hook-and-loop strap up to 4 mm x 1.5 mm) runs under the pack and over a 1 mm groove in the sled top
   at x = +-17.0..21.4 (two channels; ribs notched there; transition ring has two 6.3 x 29 x 1.8 notches). A band swept in the model touches nothing; the real strap is untested.
   Plug and 3-pin balance lead are not modelled. The Pololu regulator and the wiring are unchanged (the Spektrum is a standard 4.2 V/cell pack, not HV).
1b. **Design review (docs: see the PDF in the chat; changes applied):** bearing spokes 7 mm wide with a 9 mm flared root (CAD width was 5 mm, not the scanned 3.7), limiter stop 1 shortened to R10..12.8, enclosed voids under the ceiling filled, catch-cap finger stepped root fillet, ledge pilots O1.8, transition screws M3x10, export orientation fixed (`export_print.orient` now needs >= 100 mm2 bed contact; rotor hub down, fin on its flat side).
1c. **Wiring paths are cut into the model** (`docs/V4_wiring_layout_plan.pdf`, tools/wiring_plan.py), from the user's Mercury photo (pads GND, GP6, GP7, OUT, IN, 3V along the long edge; pitch and position estimated): bay 2.0 mm longer (housing 96.3, ring z -45.5..-37.5), groove + hole at az 126.5 deg, centre-wall trough, lead notch, vents. The horn blocks the rotor bore, so the cable cannot go down the rotor. Still to confirm on the real board: header position/pitch, servo cable exit, signal level.
2. **Mercury V1 servo header** (GP6/GP7): pin order and signal voltage unverified (site not reachable). The wiring schematic assumes the servo red wire is
   powered only by the 5 V regulator and the Mercury header power pin is left unconnected. Needs the manual page from the user.
3. Servo and horn dimensions are standard SG90 numbers (tab holes 28.1 mm apart, horn 1.8 mm thick): the user must measure theirs.
4. (Resolved in V4: vents and a servo-cable groove were cut into the V4 housing; the hollow-rotor cable route does not work because the horn closes the bore. All of this goes away in V5, where the electronics sit in the head.)
5. **Ground-impact FEA** was asked for and has not been done. First places to look: servo ledges, limiter stops, 1.4 mm sled walls, hinge screws and the
   fin hinges.
6. Latch, horn pocket and servo mount have never been tested on a print. The V4 limiter has about 1.5 deg margin at each end of the 65 deg travel.
7. Torque check (`torque_check.py`): SG90 is fine to roughly 77-109 m/s in a pessimistic wind-suction case and 134-188 m/s in a typical one; the user's top
   speed is needed. Assumes 5 V; 6 V needs the D24V10F6 regulator (min input 6.1 V).
8. "Stay out": the cam only holds the fins at about 14 deg; the airflow does the rest and the 90 deg stop takes the drag. A detent is needed if the user wants fins held at 90 deg with no airflow.
9. The user once planned to lighten a design with a "cutweight" skill (uploaded STLs `V2 - FIXED WINDOW - 90 DEG assembly.stl` and `V2 - 22 mm DROP ...`); a design-only prompt for that is in
   the conversation, not in the repo. Weight numbers by part are in `DESIGN_NOTES.md` and `docs/Design_history.pdf`.

## 8. Rules that apply

* No pull request unless the user asks. Commit only on the designated branch. Keep commit messages free of model identifiers.
* Report faithfully: what was measured on the CAD (interference, sweeps, timing), what is assumed (sizes, wind model), what is untested (prints, mates, FEA).
* Never push credentials. Do not poll the Onshape features endpoint. Delete scratch studios you create.
