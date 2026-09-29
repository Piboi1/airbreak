# MIT Rocket Team air brake – STL / STEP generator

`airbrake_stl.py` rebuilds the MIT Rocket Team (Prometheus) sliding-plate air brake.
It's pure Python 3 and needs no packages.

```
python3 airbrake_stl.py                 # extended (default)
python3 airbrake_stl.py --deploy 0      # retracted (any value 0..1)
python3 airbrake_stl.py --tube          # add the slotted 6 in airframe tube
python3 airbrake_stl.py --units in      # inches instead of mm
```

| Output | What it is |
|---|---|
| `airbrake_assembly.stl` | Whole assembly as one mesh (extended) |
| `airbrake_retracted.stl` | Same, with the leaves retracted |
| `airbrake_assembly.step` | **Open this one in CAD.** Exact geometry (true arcs, circles and cylinders, not facets); every part is one connected solid; 44 part instances, ready for Onshape mates and motion |
| `print/<part>_xN.stl` | One print-ready file per unique part, lying flat on the bed. `xN` is how many to print |
| `preview/motion.gif` | Rendered deployment cycle |

All files are in **millimetres**.

## Printing

| File | Qty | Notes |
|---|---|---|
| `frame_bottom_x1` | 1 | spoked frame that mounts in the tube |
| `tray_frame_x4` | 4 | ring segment either side of each tray |
| `tray_x2` | 2 | leaf guide tray (SLA resin in the real build) |
| `frame_middle_x1` | 1 | thin ring between the two trays |
| `leaf_x4` | 4 | 6061-T6 1/8 in plate in the real build |
| `hex_connector_x2` | 2 | double crank with a 1/4 in hex bore |
| `leaf_connector_x4` | 4 | links |
| `spacer_x4` | 4 | guide spacers under the servo bulkhead |
| `servo_bulkhead_x1` | 1 | |
| `servo_bracket_x2` | 2 | servo standoffs |
| `shaft_coupler_x1` | 1 | hex shaft to servo horn |
| `hex_shaft_x1` | 1 | or cut from 1/4 in steel hex stock |

Hardware you'll need to buy:
* 8 × #10 shoulder bolts (4 leaf pins, 4 crank pins)
* 8 × #10 washers
* 1 × large servo, about 1500 oz-in

Printed holes have 0.005 in (0.13 mm) radial clearance; change `HOLE_CLEAR` if your printer needs more.

## Onshape FeatureScript (`airbrake.fs`)

`airbrake.fs` builds the same air brake natively in Onshape, as real Onshape parts in meters.

1. In an Onshape document, create a **Feature Studio**. Replace its contents with `airbrake.fs` and commit.
2. Open a **Part Studio**. Add **MyCustomPart** from the custom features menu on the toolbar.
3. Adjust the options:
   * **Deployment (0–1):** 0 is stowed, 1 is fully out. Changing it rebuilds the model with the cranks, links and leaves moved to that position.
   * **Include servo / pins and washers / airframe tube:** toggles for those parts.
   * **Add mate connectors:** puts mate connectors on the shaft axis, every pin hole, and each leaf's slide direction.
4. For mates, insert the Part Studio into an Assembly and snap the mate connectors together:
   * **Revolute:** shaft to bottom frame; each leaf connector to its hex connector pin and its leaf pin.
   * **Fastened:** hex connectors to the shaft.
   * **Slider:** each leaf's slide connector to its tray's.

If Onshape reports a version error, replace the first two lines with the header from a newly created Feature Studio.

## Making it move in Onshape (STEP import)

Import `airbrake_assembly.step`. Onshape creates an Assembly tab with every part in its extended position. Then add these mates:

1. Group the frames, trays, tray frames, spacers, bulkhead, brackets and servo together, and fix the group.
2. Add a **Revolute** mate between the hex shaft and the bottom frame's bore. Fasten both hex connectors and the shaft coupler to the shaft.
3. Add a **Slider** mate from each leaf to its tray, along the channel.
4. Add a **Revolute** mate from each leaf connector to its crank pin hole on the hex connector.
5. Add a **Revolute** mate from each leaf connector to its pin hole on the leaf.

Dragging the hex shaft then drives all four leaves. The crank sweeps 90°, and each leaf travels exactly 2.25 in. At full extension the crank and link line up (dead centre), so drag on the leaves can't back-drive the servo.

## Accuracy

Values published on the MIT wiki:
* 4 sliding 6061-T6 leaves, each 3.5 in wide with 2.25 in extended (7.875 in² each, 31.5 in² total)
* two SLA trays stacked 90° apart, each spanning the full diameter and holding one opposing pair of leaves
* a hex connector and leaf connectors, driven by a servo on a bulkhead, with washers at the joints
* frames, spacers and a servo bulkhead
* 6 in series airframe (5.823 in ID / 6.00 in OD)

The team never published the other dimensions: plate thicknesses, frame sizes, stack
heights, linkage lengths and the servo's size. Those are estimates taken from the CAD
screenshots. The stack follows the PDR image, with 0.63 in between the two leaf levels.
All estimates are in the `PARAMETERS` block at the top of the script. The linkage is
re-solved automatically when you change them, and the script warns if a link would
hit the shaft.

Not modelled: radial screw holes into the airframe, fasteners, and the servo horn.

STL files are always triangle meshes, so they show triangle lines in any CAD tool. Use
them for printing, and use the STEP file for viewing and editing in CAD.
