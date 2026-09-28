# MIT Rocket Team air brake – STL generator

`airbrake_stl.py` rebuilds the MIT Rocket Team (Prometheus) CDR air brake as an STL.
It's pure Python 3 and needs no packages.

```
python3 airbrake_stl.py                 # extended   -> airbrake_assembly.stl (mm)
python3 airbrake_stl.py --deploy 0      # retracted
python3 airbrake_stl.py --tube          # add the slotted 6 in airframe tube
python3 airbrake_stl.py --parts         # also write one STL per part in ./parts
python3 airbrake_stl.py --units in      # inches instead of mm
```

To open it in Onshape, use **Create → Import** and set the units to **Millimeter**.

## Accuracy

Values published on the MIT wiki:
* 4 sliding 6061-T6 leaves, each 3.5 in wide with 2.25 in extended (7.875 in² each, 31.5 in² total)
* two SLA trays stacked 90° apart, each spanning the full diameter and holding one opposing pair of leaves
* a hex connector and leaf connectors, driven by a servo on a bulkhead, with frames and guide spacers
* 6 in series airframe (5.823 in ID / 6.00 in OD)

The team never published the other dimensions: plate thicknesses, frame and spacer
sizes, stack heights, crank and link lengths, and the servo's size. Those are estimates
taken from the CAD screenshots, and they're grouped in the `PARAMETERS` block at the
top of the script so you can correct them. Screw holes and fasteners aren't modelled.
