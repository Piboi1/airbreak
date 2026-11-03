#!/usr/bin/env python3
"""Build docs/V5_assembly_guide.pdf (what is built and verified in CAD). Needs the figures from make_figs_v5.py and v5_sections.py."""
import os, sys, json, pathlib
W = pathlib.Path(os.environ['AIRBRAKE_WORK'])
if not (W / 'verify.json').exists():
    (W / 'verify.json').write_text('{}')
import make_docs as md
from make_docs import P, bullets, fig, table, build_pdf, H1, H2, H3, WARN, NOTE, SM, DOC_URL
from reportlab.platypus import PageBreak, Spacer

OUT = md.DOCS / 'V5_assembly_guide.pdf'


def story():
    s = []
    s += [P('V5 assembly guide: the modular airbrake', H1),
          P('Module (housing, rotor, four fins) and head (SG90, Mercury V1, regulator, 2S battery) slide into one BT80 tube. Everything is held by '
            'radial M3 bolts and nuts from the outside. Built in Onshape as <b>mode 5</b> of the same FeatureScript, checked offline on the exported meshes, '
            'exported as STL and STEP. <b>Not printed or flown yet.</b>', md.B),
          P(f'Onshape document: <a href="{DOC_URL}" color="blue">{DOC_URL}</a>. Part studios <b>V5-A</b> (closed) and <b>V5-B</b> (fins 90 deg, rotor 65 deg), assembly <b>ASM-V5</b>.', md.SM),
          WARN_('<b>Placeholders and unknowns.</b> The transition cone and the BT70 side are placeholders (you do not know their diameters; the BT70 side was not touched). The Mercury, regulator '
                'and battery are reference boxes from catalogue sizes; the USB-C window, switch slot, three vents and the servo cable slot are provisional positions. The SG90 horn and tab '
                'holes are standard numbers. Nothing here has been printed.')]
    s += [P('1  What was built', H2),
          table([['Item', 'Value (from the CAD model)'],
                 ['Module', 'housing z -10 .. 58.8 (68.8 mm), OD 64.4 (R32.2) in the 65.02 bore; one piece, no seam; 4 free fins; rotor with integral catch caps; about 85 g solid PLA'],
                 ['Head', 'cup + lid z 59.0 .. 88.3 (29.3 mm above the module), OD 64.4; about 33 g solid PLA plus electronics'],
                 ['Overall', 'module bottom to head top 98.3 mm; with the transition shoulder 122.3 mm (the cone and BT70 side are placeholders)'],
                 ['Tube', 'BT80 R32.51 / R33.02, one piece: 4 windows 67 deg x 63.8 mm (z -9.2 .. 54.6), 12 bolt holes, 3 vents, USB-C window, switch slot'],
                 ['Fasteners', '19 bolts in all: 12 radial M3x8 (sets 1, 2, 3) + 4 hinge M3x25 + 2 servo flange M2x6 + 1 horn screw M2x6. 18 nuts (16 M3, 2 M2). No heat-set inserts, no self-tapping, no snap hooks, no bands.']],
                [30, 150]),
          fig('v5_built_exploded.png', 78, 'Exploded view from the CAD meshes (tube hidden): lid, electronics, head cup, fins, module housing with rotor, transition. Bolts and nuts shown as hardware.', 200)]
    s += [PageBreak(), P('2  The stack and the three bolt sets', H2),
          fig('v5_assembled.png', 70, 'V5-A as Onshape renders it: one tube, four open windows, head bolts at the top, module bolts in the middle, transition bolts at the bottom (BT70 side not drawn).', 175),
          table([['Set', 'Joint', 'Height z', 'Azimuths', 'Nut'],
                 ['1 head', 'tube + head cup wall + LID boss (the bolts clamp cup and lid together)', '82', '45, 135, 250, 290', 'hex pocket in the lid boss, open inward'],
                 ['2 module', 'tube + module wall (boss R27.6..30.2)', '12', '45, 135, 225, 315', 'hex pocket in the wall boss, open inward'],
                 ['3 transition', 'tube + transition shoulder (R26.0..32.2)', '-28', '45, 135, 225, 315', 'hex pocket in the shoulder, open inward']],
                [20, 62, 18, 32, 48]),
          P('Every bolt is M3x8 button head (ISO 7380, 2.0 mm hex), radial, from the outside, BT80 side only. The 12 holes in the tube are plain clearance holes cut once; a new module reuses the same 12 holes. '
            'The nut pockets are hexagons (5.7 mm across flats, 2.6 mm deep) so nobody has to hold a nut.', md.B)]
    s += [PageBreak(), P('3  Parts, print files and hardware', H2),
          table([['File (exports/v5/print)', 'Qty', 'Part', 'Solid PLA', 'Print note'],
                 ['C_module_housing_x1', 1, 'one-piece housing, floor plate, 4 nut bosses, limiter stops above the bearing ring', '29 g', 'upright, supports (about 1500 mm2 overhang)'],
                 ['R_rotor_x1', 1, 'rotor: shaft, 4 cams, 4 integral catch caps, limiter finger, horn socket with taper', '22 g', 'hub down (205 mm2 on the bed), supports (about 2100 mm2)'],
                 ['P_fin_x4', 4, 'fin (identical, M3 hinge bore)', '8.3 g each', 'on its flat side, supports'],
                 ['H_head_cup_x1', 1, 'sleeve, floor, servo ledges, 3 electronics pockets, vents, USB-C window, switch slot', '25 g', 'upside down, supports under the floor and ledges (about 3000 mm2)'],
                 ['K_head_lid_x1', 1, 'lid disc with 4 nut bosses', '8.1 g', 'disc on the bed, almost no supports'],
                 ['T_transition_BT80_side_PLACEHOLDER_cone_x1', 1, 'plug + shoulder + 4 nut pockets (BT80 side); the cone is a placeholder', '41 g', 'cone is not final; do not print before the BT70 side is known']],
                [52, 9, 63, 18, 38], font=7.6),
          Spacer(1, 6),
          table([['Hardware', 'Qty', 'Where'],
                 ['M3x8 button head bolt + M3 nut', '12 + 12', 'sets 1, 2, 3 (4 each)'],
                 ['M3x25 button head bolt + M3 nut', '4 + 4', 'fin hinges; the nut sits in the +Y ear slot'],
                 ['M2x6 button head bolt + M2 nut', '2 + 2', 'SG90 flange to the head ledges; nut in a pocket in the ledge top (the tab covers it)'],
                 ['M2x6 screw (supplied with the servo)', '1', 'horn screw']],
                [70, 20, 90]),
          P('V4 used 27 screws (4 seam, 4 cap, 4 hinge M4, 4 boss, 8 tube support, 3 M2). V5 uses 19 fasteners, all bolts with nuts; the seam, cap, boss and support screws are gone.', md.B)]
    s += [PageBreak(), P('4  Sections from the model', H2),
          fig('v5_plans.png', 180, 'Plan sections at eight heights: transition shoulder, housing floor, hinges, module bolts, cam and fin followers, servo ledges and lugs, electronics, lid bosses.', 120),
          fig('v5_axial.png', 180, 'Axial sections at 45 deg (bolt azimuth: head, module and transition bolts), 0 deg (fin window, hinge, latch) and 135 deg (servo ledge post, lid boss).', 150)]
    s += [PageBreak(), P('5  Assembly on the bench', H2),
          P('<b>Module (outside the tube).</b>', md.B)] + bullets([
              'Drop four M3 nuts into the hex pockets in the housing wall from the inside (set 2, z 12). Do this before the rotor goes in.',
              'Drop the rotor in from the top. It goes in at any rotor angle from 0 to 60 deg (checked); the limiter finger lands between the two stops. Turn it to about 18 deg and leave it there.',
              'For each fin: slide an M3 nut into the +Y ear slot from the window side (it enters radially, then slides -Y). Push the fin radially in through its window, barrel between the ears. '
              'Push an M3x25 bolt in along +Y through the channel in the housing wall (the channel is 6.6 mm wide and runs along the hinge axis), and tighten with a 2.0 mm hex key. '
              'The fins only go in with the rotor between about 14 and 24 deg: the cam touches from about 25 deg, the catch finger blocks below about 14 deg.',
              'Turn the rotor back to 0 (locked). The catch fingers now stand outside the fin lugs.'])
    s += [P('<b>Head (outside the tube).</b>', md.B)] + bullets([
              'Fit the two M2 nuts into the ledge pockets (from the top), put the servo on the ledges, two M2x6 bolts down through the tab holes (screwdriver access through the floor).',
              'Horn on the servo spline with its screw (from below). Put the Mercury, regulator and battery into their pockets; wire them (nothing leaves the head). Put four M3 nuts into the lid bosses, lay the lid on.',
              'The lid is only held by the four set-1 bolts, so hold it with a strip of masking tape while the head slides into the tube.'])
    s += [P('<b>Into the tube.</b>', md.B)] + bullets([
              'Slide the head into the tube from the bottom to the set-1 holes (z 82 from the module seat); four bolts. Then slide the module in from the bottom, nuts already in: the horn arm enters the tapered socket and turns the free rotor into line (about +-10 deg). Four bolts (set 2).',
              'Slide the transition in from the bottom with its nuts in (set 3), four bolts. The BT70 section goes on below as before.'])
    s += [P('6  Swapping the module (8 bolts, the head stays)', H2),
          P('<b>Route 1, out of the bottom (main).</b> Pull the 4 transition bolts and slide the transition out; pull the 4 module bolts and slide the module out (the horn arm leaves the socket upward through its open top). New module: nuts in, slide in, 4 bolts; transition back, 4 bolts. The head is never touched.', md.B),
          P('<b>Route 2, out of the top.</b> Pull the 4 head bolts and lift the head out; pull the 4 module bolts and lift the module out; the transition stays. It needs the upper airframe separated from the top of this tube. Both routes are collision-free in the CAD (nothing on the module or head is wider than the bore).', md.B),
          WARN_('<b>The rotor is not locked into the module.</b> With the module out of the tube the rotor can lift out of the top (the head holds it down, 0.6 mm above the hub, when installed). Carry the module upright. '
                'I did not add a keeper because a keeper would have to be a snap hook or a band.')]
    s += [P('7  What was checked, and what was not', H2),
          table([['Check (offline, on the exported meshes)', 'Result'],
                 ['Printed parts overlapping, closed and open (fins 90, rotor 65)', 'none; only the SG90 spline inside the horn (32.45 mm3) and the horn screw in horn and servo (reference parts)'],
                 ['Non-watertight bodies', 'none'],
                 ['Fin opening sweep 0..90 deg against housing, tube, head', 'clear; the latch holds from about 1.5 deg of opening'],
                 ['Rotor sweep -5..70 deg', 'limiter stops at about -2 and +66.5 deg (the V4 margin of about 1.5 deg each side of the 65 deg travel); cam first touches the fins at about 25.5 deg; latch frees at about 14 deg'],
                 ['Rotor dropped in from the top, any angle 0..60 deg', 'free (the one-piece housing works)'],
                 ['Fin installed radially, rotor parked at 14..26 deg', 'clear of housing and rotor; below 14 deg the catch finger blocks it'],
                 ['Hinge nut loading, hinge bolt and key along the hinge axis', 'clear straight lines'],
                 ['Head lowered onto the module with the horn aligned within +-3 deg', 'clear; beyond that the tapered socket must turn the free rotor (not measurable offline)'],
                 ['Module out of the bottom and the top, transition and head out of the tube', 'clear (0.00 mm3 against the tube)'],
                 ['2.0 mm hex key from outside to all 12 radial bolts', 'clear'],
                 ['V1 to V4 volumes after adding mode 5', 'identical in all 8 states (closed and open of V1, V2, V3, V4), rebuilt in scratch studios']],
                [75, 105], font=7.8),
          P('<b>Not checked:</b> anything physical (print, fit, flight); strength (ground-impact FEA is still not done); the electronics layout against the real parts; mate motion in ASM-V5 (drag a fin and the rotor to try it; mates cannot be driven through the API); '
            'the real wire routing; the transition cone and BT70 side.', md.B),
          P('8  Where this differs from the concept sheets', H2)] + bullets([
              'Set-1 nuts are in the <b>lid</b> bosses, not in bosses of the sleeve: the lid needs holding without a snap hook, and the same four bolts then clamp cup and lid together.',
              'Hinge bolts are tightened on the bench through a 6.6 mm channel in the housing wall, because a hex key cannot reach them through the tube windows at less than about 40 deg.',
              'Hinge ears were trimmed from R5.2 to R4.9 and the hard-stop block corner from R32.6 to R32.1 so that the housing stays inside R32.2 (V4 touched the tube there).',
              'The catch fingers are flush with the hub top (V4 stood 0.2 mm proud) so the rotor prints hub-down on one plane.',
              'The regulator stands on its 8 mm edge so that battery, Mercury and regulator fit one layer inside the R29.9 sleeve.'])
    return s


def WARN_(t):
    return P(t, WARN)


if __name__ == '__main__':
    build_pdf(OUT, 'V5 assembly guide - ARC BT80 airbrake', story())
    print('wrote', OUT)
