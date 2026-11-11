# V5 air brake – weight-reduction study

FEA-backed check of the cuts marked on the V5 rotor ("inner green piece"), plus proposed cuts for the rest of the V5 assembly. All files are in **millimetres**.

## Start here

| File | What it is |
|---|---|
| `inner_piece/inner_piece_cut_drawing_and_FEA.pdf` | Drawing document for the rotor: which requested cuts are safe, dimensioned cut sheets, FEA set-up and results |
| `inner_piece/V5_inner_piece_lightened_recommended.stl` | Rotor with lobe pockets, block wings and block undersides removed, **no** arm holes, tab-root gussets added (22.4 g → 15.8 g solid PLA) |
| `inner_piece/V5_inner_piece_lightened_as_marked.stl` | Rotor with every marked cut, including the Ø3 arm holes (15.6 g) |
| `inner_piece/inner_piece_pocket_profile.dxf` | 1:1 outline of the wheel and the four lobe pockets, for sketching in CAD |
| `assembly/assembly_weight_reduction_proposals.pdf` | Drawing document with proposed cuts for the lower section, flaps, cage, upper bay and cap (about 22 g of 175 g in total, rotor included) |
| `assembly/preview_stl/` | Preview solids of each proposal. These are **not** approved changes |
| `input/` | The two STLs the study was run on |

## Result in one paragraph

Lobe pockets, block side wings and block undersides are safe to remove: none of them is on a load path, and stresses change by less than mesh noise except in the lobe rim, which keeps more than 4× margin. The Ø3 arm holes save 0.17 g and raise arm stress 27–63 %, so the recommended part leaves them out. The tab root is the weakest feature with or without the cuts (predicted break at about 17 N of radial pull); a 2 × 2 mm gusset raises that to about 31 N.

## Assumptions to confirm

* PLA, printed with the shaft axis vertical. Allowables 35 MPa in the layer plane and 15 MPa across layers.
* Reference loads are estimates (10 N per tab, 20 N per cam lobe and per flap, 200 N axial on the body parts). Stress scales linearly with load.
* The four circled dots in photo 1 were read as Ø3 lightening holes through the arms.
* Masses are for 100 % solid PLA at 1.24 g/cm³.

## Reproducing (`fea/`)

Needs `numpy scipy trimesh shapely manifold3d pytetwild scikit-fem pypardiso pyvista matplotlib`. The scripts work on files in the current directory.

1. `variants.py` builds the rotor variants (`var_*.stl`) from `inner_base.stl`, the largest body of the input rotor STL.
2. `twmesh.py <stl> <edge> <out.npz>` makes the tetrahedral mesh; `run_inner.py <variant>` solves the six rotor load cases.
3. `props.py` builds the proposals for the other parts from `part_<name>.stl`; `st_flap.py` and `st_parts.py` solve them.
4. `figs_*.py`, `draw_rotor.py <out.pdf>` and `draw_parts.py <out.pdf>` make the figures and the two PDFs.

`fea/results/` holds the peak stresses, utilisations and deflections behind every number in the PDFs.
