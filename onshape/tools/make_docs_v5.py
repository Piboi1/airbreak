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
                 ['Module', 'housing z -10 .. 58.8 (68.8 mm), OD 64.4 (R32.2) in the 65.02 bore; one piece, no seam; 4 free fins; rotor with integral catch caps; about 91 g solid PLA'],
                 ['Head', 'cup + lid z 59.0 .. 88.3 (29.3 mm above the module), OD 63.9; about 31 g solid PLA plus electronics'],
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
                 ['C_module_housing_x1', 1, 'one-piece housing, floor plate, 4 nut bosses, limiter stops above the bearing ring', '30 g', 'upright, supports (about 1600 mm2 overhang)'],
                 ['R_rotor_x1', 1, 'rotor: shaft, 4 cams, 4 integral catch caps, limiter finger, horn socket with taper', '22 g', 'hub down (205 mm2 on the bed), supports (about 2200 mm2)'],
                 ['P_fin_x4', 4, 'fin (identical, M3 hinge bore, ribs, hinge tail)', '9.8 g each', 'on its flat side, supports; print in PETG or PLA+ with 4+ walls and 100% infill if you can'],
                 ['H_head_cup_x1', 1, 'sleeve, floor, servo ledges, 3 electronics pockets, vents, USB-C window, switch slot', '23 g', 'upside down, supports under the floor and ledges (about 3000 mm2)'],
                 ['K_head_lid_x1', 1, 'lid disc with 4 nut bosses', '8.1 g', 'disc on the bed, almost no supports'],
                 ['T_transition_BT80_side_PLACEHOLDER_cone_x1', 1, 'plug + shoulder + 4 nut pockets (BT80 side); the cone is a placeholder', '41 g', 'cone is not final; do not print before the BT70 side is known']],
                [52, 9, 63, 18, 38], font=7.6),
          Spacer(1, 6),
          table([['Hardware', 'Qty', 'Where'],
                 ['M3x8 button head bolt + M3 nut', '12 + 12', 'sets 1, 2, 3 (4 each)'],
                 ['M3x25 button head bolt + M3 nut', '4 + 4', 'fin hinges; the nut sits in the +Y ear slot'],
                 ['M2x8 button head bolt + M2 nut (any length up to about 15 mm clears)', '2 + 2', 'SG90 flange to the head ledges; nut in a pocket in the ledge top (the tab covers it)'],
                 ['M2x6 screw (the one supplied with the servo)', '1', 'horn screw']],
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
              'Head cup on the bench: drop the two M2 nuts into the hex recesses on the UNDERSIDE of the ledges, push the servo (horn off) up into the cup from below until its tabs touch the ledge undersides, then two M2x8 bolts from below through the tab holes into the nuts. Do this before the head goes near the module: the screw heads end up 3.5 mm above the rotor hub.',
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
                 ['Fin with tail, ribs, wide gusset: opening 0..90 deg, all four fins, vs housing', 'clear; the keeper meets the tail at about 91 deg, the stop at about 90 deg'],
                 ['Rotor sweep, latch and cam timing after the fin changes', 'unchanged (holds from 1.5 deg, frees at about 14 deg, cam from about 25.5 deg); rotor clear of the ribs'],
                 ['Servo with gear boss and spline: clearance to the rotor', '0.6 mm or more everywhere; the head cup lands on the housing first (0.2 mm)'],
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
    s += [PageBreak(), P('9  After the first print: what the photos showed and what changed', H2),
          P('Your friend printed the other V5 (same base as this one) and you sent photos. Three problems were reported; this section is what I did about each. '
            '<b>All of it is CAD and calculation only: nothing here has been printed, and the FEA numbers are an estimate, not a test.</b>', md.B),
          P('Problem 1: the fins are flimsy and nearly snap when pushed past 90 deg', H3),
          P('Why it matters: in flight the airflow pushes an open fin into its 90 deg stop, so "past 90" is a real load case, not only a hand push. '
            'I built a finite-element model of the open fin (<font face="Courier">tools/fea_fin.py</font>: voxel hex mesh, PLA E 3 GPa, pin and stop as rigid supports, '
            '12 N airflow, 30 N airflow, 15 N at the tip). It showed (a) the peak stress sat where the narrow root gusset ends, a 14 mm wide root feeding a 34 mm wide shell; '
            'with the fin printed flat that gusset is loaded across the layers, which is the weak direction; (b) with the fin open, the stop contact is almost directly under the pin, '
            'so a tip push is multiplied several times at the pin.', md.B),
          P('What changed on the fin (V5 mode only; V1 to V4 untouched): a wide tapered root gusset (14 to 24 mm wide, up to z 22.5, clear of the cam), a thicker and wider root pad, '
            'an arc-shaped landing and stop block spreading the 90 deg contact over about 27 mm instead of 12, a spine rib and two edge ribs on the inner face (broken only where the follower already fills the cam band), '
            'and a root clipped to the housing radius.', md.B),
          P('The lock (adapted from the mentor picture): I read the mentor CAD as a cross-shaped hub with a deep U-shaped pocket under each hinge and a wide tab from the flap sitting in it. '
            'Here there is only 3.5 mm under the hinge, so it is a <b>tail</b> on each fin (4.5 x 12 x 4.6 mm) that sits in a U pocket cut into the stop blocks, plus two small <b>keeper pads</b> carried by towers beside the tail path. '
            'As the fin opens the tail swings inboard and up; at about 91 deg its top face meets the pads. The stop (outboard, below the pin) and the keeper (inboard, above the tail) then form a force couple, '
            'so the pin stops carrying the push. It is rigid: no snap hook, no band, nothing flexes. If I misread the mentor picture, tell me what the lock in it actually does.', md.B),
          fig('v5_lock.png', 170, 'The lock, section through the tail and a keeper pad (y = 5.4 mm). Left: closed, tail in its U pocket. Right: 90 deg, tail swung inboard under the pad, web resting on the stop.', 90),
          fig('v5_fea.png', 170, 'FEA of the open fin pushed into its stop. Left: peak stress, first V5 against this version (about half). Right: load on the hinge pin with and without the keeper (about ten times lower with it).', 85),
          table([['Load case', 'Peak stress before', 'after', 'Pin load, stop only', 'with keeper'],
                 ['12 N airflow (about 100 m/s)', '8.0 MPa', '4.0 MPa', '10 N', '1 N'],
                 ['30 N airflow', '20.1 MPa', '9.9 MPa', '25 N', '3 N'],
                 ['15 N at the tip (by hand)', '15.8 MPa', '9.6 MPa', '22 N', '1 N']], [52, 32, 22, 38, 26]),
          WARN_('<b>How to read these numbers.</b> Printed PLA fails between layers at roughly 15 to 20 MPa, so the first V5 sat at about its limit at 15 N, which fits "almost snaps"; this version has about 1.5 to 2 times margin at the same loads, '
                'not a large one. The model uses isotropic PLA, rigid supports and 0.8 mm voxels, whose stair-steps over-state corner stress; compare the two columns, do not trust the absolute values. '
                'The remaining peak is at the notch where the ear clearance cuts the gusset (airflow case) and at the long shell edge in the gap where the cam band prevents an edge rib (tip case). '
                'The hinge ears, the bolt and the housing were not in the model (my hand estimate says they are loaded in compression along the arm, a few MPa). '
                'Print the fins in PETG or PLA+ if you can, with 4 or more walls, and test by hand before flying.'),
          P('Problem 2: the part that houses the servo does not go far enough into the hole', H3),
          P('My best explanation (I could not see inside your print): a real SG90 has a raised gear boss, about O11.8 x 4.5 mm, around the output shaft and a spline about 4 mm long, '
            'while my servo was a plain box with a 3.7 mm stub and only 0.2 to 0.6 mm of slack. With the shaft pointing down the real boss lands on the rotor hub top and holds the head up by about the 4 to 5 mm visible in your photos. '
            'Changes: the servo model now has the boss and the longer spline; the hub is counterbored for the boss (O13.2, stepped lead-in) and the horn socket is 10 mm deep (floor at z 35.0); the hub grew to R10.5 to keep wall around the counterbore; '
            'the head sleeve is R31.95 (0.56 mm to the tube, was 0.31) with a 0.8 mm lead-in chamfer, and the module has the same chamfer. '
            'The stack is now ordered so that the head cup lands on the housing top (0.2 mm gap) before anything in the servo and rotor stack can touch (0.6 mm or more).', md.B),
          fig('v5_socket.png', 170, 'Left: servo boss, spline and horn in the counterbored hub socket. Right: the head cup resting on the housing top.', 100),
          WARN_('<b>Please measure your servo</b> (boss diameter and height above the case, spline length, tab hole spacing and the distance from the tab to the shaft end). '
                'If the head still stands proud after reprinting, the cause is something else: tell me how far it stands proud and whether it rocks, and measure whether the head sleeve or the housing is the tight fit in the tube (a 0.3 mm print swell would do it; the sleeve now has 0.56 mm).'),
          P('Problem 3: the mentor lock', H3),
          P('Used for problem 1 (the tail and U pocket above). The mentor picture was a bottom view of a cross hub; my reading of it is stated above and should be confirmed.', md.B)]
    s += [PageBreak(), P('10  The servo screws: what was really wrong, the redesign, and a screw clearance audit', H2),
          P('Your screenshot of the earlier V5 showed a servo screw standing over the stepped rim of the rotor hub, which is where the screw heads hit when the servo is fixed to the head cup. '
            'I checked how the servo gets into the cup in my CAD and found the real fault: <b>the servo could not be assembled at all as I had drawn it</b>. '
            'I had put the servo tabs ON TOP of the ledges. Pushed up from below, the tab runs into the ledge (blocked 6 mm before the final position); lowered from above, the cup floor blocks it (36 mm before). '
            'So the servo had to be hung with its tabs UNDER the ledges, which puts the screw heads under the tabs, directly over the hub rim. My first fix ("raise everything 3.2 mm") assumed the wrong arrangement and has been replaced.', md.B),
          P('The redesign (head cup only, nothing else changes): the ledges are now ABOVE the tabs. The servo is pushed up into the cup from below until its tabs touch the underside of the ledges (checked: zero interference along the whole path). '
            'Each ledge has a hex recess on its underside for an M2 nut (put the nut in before the servo, the tab then covers it) and a hole up through it; the bolts go in from below through the tab into the nut. '
            'The screw heads sit 3.5 mm above the rotor hub, so the hub rim cannot be hit, and the screws can be any length up to about 15 mm because the tips go up into free space under the cup floor. '
            'The little screwdriver holes in the cup floor are gone. The cup is assembled on the bench first (screwdriver straight in from below), then goes onto the module. '
            'The servo itself is in the same place as before, so the horn socket, hub and rotor are untouched: <b>you do not need to reprint the rotor.</b>', md.B),
          fig('v5_socket.png', 170, 'Left: servo tab against the underside of the ledge, bolt from below, nut in the ledge recess, heads clear of the hub. Right: boss, spline and horn in the hub socket.', 100),
          P('Screw audit across the design (grows each bolt past its tip until it touches a part; <font face="Courier">tools/check_screws.py</font>; shank length you can buy, head extra):', md.B),
          table([['Fastener', 'Modelled', 'Longest that clears', 'First thing it would hit'],
                 ['Servo flange bolts (2)', 'M2x8, from below', 'about M2x19', 'the cup floor above the ledges'],
                 ['Head bolts (4)', 'M3x8', 'M3x10', 'the Mercury corner'],
                 ['Module bolts (4)', 'M3x8', 'M3x16', 'the limiter stop on the neighbouring spoke'],
                 ['Transition bolts (4)', 'M3x8', 'more than M3x20', 'nothing within 14 mm (open bore)'],
                 ['Fin hinge bolts (4)', 'M3x25', 'about M3x27', 'the housing wall past the ear'],
                 ['Horn screw (1)', 'M2x6', 'blind: it screws into the spline', 'not applicable']],
                [46, 28, 40, 66], font=7.6),
          P('Also checked and clear: 2.0 mm hex key straight in to all 12 radial bolts from outside; a driver column straight in from below to both servo screws (head plus driver, 4.8 mm wide); the hinge bolt head and key along the hinge axis through the wall channel; '
            'hinge nuts loading from the window; the head bolt heads against the switch slot, vents and USB-C window (at least 2.6 mm of wall); the module bolt heads against the window edges (about 3.7 mm).', md.B),
          WARN_('<b>Not checked:</b> the real SG90 screws, boss and horn (measure them), screwdriver handle swing (only the straight column), and any real print. '
                'If the head bolts are M3x12 or longer their tips touch the Mercury corner.'),
          P('Fin area', H3),
          P('One fin: 1,894 mm2 planform seen by the airflow when open (1,592 mm2 of it beyond the tube), 5,631 mm2 of surface in total. Script: <font face="Courier">tools/fin_area.py</font> (any fin STL, no Onshape needed). '
            'In Onshape there is no projected-area button: sketch the outline on the Top plane in V5-B, extrude it 0.1 mm as a new part and Measure its face.', md.B)]
    return s


def WARN_(t):
    return P(t, WARN)


if __name__ == '__main__':
    build_pdf(OUT, 'V5 assembly guide - ARC BT80 airbrake', story())
    print('wrote', OUT)
