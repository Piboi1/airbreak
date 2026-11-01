# HANDOFF: BT80 cam kick-out airbrake CAD project (V1 to V4)

Read this first. It is written so a new agent can continue with no other context. Repo: `piboi1/airbreak`, branch
`claude/nice-maxwell-1lmh2h`, folder `onshape/`. Everything described here is committed and pushed (last commit when this
was written: "Add V4 power and wiring document"). Do not open a pull request unless the user asks.

## 1. The project and the user

* The user is building a **BT80 (66.04 mm OD, 65 mm ID) rocket airbrake**: four fins hinged at the bottom, opened by a
  four-lobe cam rotor, held shut by a rotor-mounted latch, finished open by the airflow against a 90 deg hard stop.
* Their original FeatureScript is `onshape/fs/v0_original.fs` ("REINFORCED BOTTOM SPRING - 90 DEG", unchanged). Everything
  else is generated from it. They also have wind-tunnel logs and an SG90 servo.
* What the user wants and how they work: short plain answers, files they can open (PDFs, STL/STEP, Onshape links), honest
  statements of what was and was not verified. They make the design decisions; ask only when blocked, otherwise state the
  assumption and proceed. They prefer small overall size and light weight. They sometimes type quickly with typos.
* The user's own Onshape document (ARC) is read-only for us and is only used as a mate template (see `asm.py`).

## 2. State: four design versions, all built, verified and exported

| Version | What it is | Housing | Overall | Printed (solid PLA) | Status |
|---|---|---|---|---|---|
| Original | user's bonded model | 118 mm | 178.5 mm | 177 g | reference only |
| **V1** | same machine, screwed (M3/M4), assembly doc | 118 | 178.5 | 180 g | done, unchanged since |
| **V2** | compact head inside the upper BT80 tube, tube slits with cut-outs glued to fins, new inward-lug + finger latch, fin top at head rim (22 mm latch drop) | 91.8 | 152.3 | 169 g | done |
| **V3** | SG90 straight on the rotor (no spring cartridge/trigger), servo inside the housing, flush with the bottom | 91.8 | 91.8 | 106 g | done |
| **V4** (latest) | servo flipped on top, thicker limiter/rotor parts, limiter moved to the bottom, electronics bay + sled, screwed transition ring | 94.3 | 103.4 (housing bottom to servo top) | 142 g (113 core + 15 sled + 15 transition) | done, awaiting user decisions below |

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
| **ASM-V3 (current)** / ASM-V4 | `d071de26baa2e2f9ef97f361` / `06e1790389ded1411a7f25aa` (rebuilt after the design-review changes) |

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
* `docs/*.pdf`: `V1/V2/V3/V4_assembly_guide`, `V3_mechanics_diagrams`, `Design_history`, `V4_concept_sketch`,
  `V4_power_and_wiring`. `docs/img` holds figures. `exports/v1..v4/print/*.stl` (one file per unique part, `_xN` = quantity)
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
  **3 = V3, 4 = V4**. Boolean `compact` = V2 head (always on for V2/V3/V4). `camKickBrake` takes `direct` (mode 3) and `flip`
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
   housing unchanged at 94.3 mm (the floor between the layers is now 1.8 mm). Measure the real pack. The pocket is open at the bottom: a belly band (nylon tie or hook-and-loop strap up to 4 mm x 1.5 mm) runs under the pack and over a 1 mm groove in the sled top
   at x = +-17.0..21.4 (two channels; ribs notched there; transition ring has two 6.3 x 29 x 1.8 notches). A band swept in the model touches nothing; the real strap is untested.
   Plug and 3-pin balance lead are not modelled. The Pololu regulator and the wiring are unchanged (the Spektrum is a standard 4.2 V/cell pack, not HV).
1b. **Design review (docs: see the PDF in the chat; changes applied):** bearing spokes 7 mm wide with a 9 mm flared root (CAD width was 5 mm, not the scanned 3.7), limiter stop 1 shortened to R10..12.8, enclosed voids under the ceiling filled, catch-cap finger stepped root fillet, ledge pilots O1.8, transition screws M3x10, export orientation fixed (`export_print.orient` now needs >= 100 mm2 bed contact; rotor hub down, fin on its flat side).
1c. **Wiring has no route yet** (`docs/V4_wiring_layout_plan.pdf`, tools/wiring_plan.py): the horn blocks the rotor bore, the pocket tops are 0.2 mm under the ceiling, the pack leads have 0.4 mm at the pocket end. Proposed P1 outer strip groove + radial hole, P2 sled trough, P3 lead notch, P4 riser groove, P5 vent holes: NOT applied; waiting for the user and the Mercury header position.
2. **Mercury V1 servo header** (GP6/GP7): pin order and signal voltage unverified (site not reachable). The wiring schematic assumes the servo red wire is
   powered only by the 5 V regulator and the Mercury header power pin is left unconnected. Needs the manual page from the user.
3. Servo and horn dimensions are standard SG90 numbers (tab holes 28.1 mm apart, horn 1.8 mm thick): the user must measure theirs.
4. Static-pressure vent holes for the altimeter and the servo cable route (down the hollow R3 rotor bore, beside the horn-screw head) are not modelled.
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
