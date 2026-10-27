#!/usr/bin/env python3
"""Build the V1 / V2 assembly guides (PDF) from the figure PNGs and the verification report."""
import json, pathlib, sys, shutil
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, Table, TableStyle,
                                Image, PageBreak, KeepTogether)
from PIL import Image as PILImage

ROOT = pathlib.Path(__file__).resolve().parent.parent
WORK = pathlib.Path(__import__('os').environ.get('AIRBRAKE_WORK', str(ROOT / '.work')))
FIG = WORK / 'fig'
VERIFY = json.load(open(WORK / 'verify.json'))
DOCS = ROOT / 'docs'
DOCS.mkdir(exist_ok=True)
(DOCS / 'img').mkdir(exist_ok=True)

DOC_URL = 'https://cad.onshape.com/documents/857ab7b483eda80939870e15/w/0766f9a969602884d82183a8'

ss = getSampleStyleSheet()
H1 = ParagraphStyle('H1', parent=ss['Heading1'], fontSize=20, spaceAfter=6, textColor=colors.HexColor('#1b3a57'))
H2 = ParagraphStyle('H2', parent=ss['Heading2'], fontSize=13.5, spaceBefore=10, spaceAfter=4, textColor=colors.HexColor('#1b3a57'), keepWithNext=1)
H3 = ParagraphStyle('H3', parent=ss['Heading3'], fontSize=11, spaceBefore=6, spaceAfter=2, keepWithNext=1)
B = ParagraphStyle('B', parent=ss['BodyText'], fontSize=9.4, leading=12.6, spaceAfter=3)
SM = ParagraphStyle('SM', parent=B, fontSize=8, leading=10, textColor=colors.HexColor('#444444'))
CAP = ParagraphStyle('CAP', parent=B, fontSize=8.3, leading=10.5, textColor=colors.HexColor('#333333'), alignment=1)
BUL = ParagraphStyle('BUL', parent=B, leftIndent=12, bulletIndent=2, spaceAfter=1.5)
WARN = ParagraphStyle('WARN', parent=B, backColor=colors.HexColor('#fff3d6'), borderColor=colors.HexColor('#e0b040'),
                      borderWidth=0.6, borderPadding=4, spaceBefore=4, spaceAfter=6)
NOTE = ParagraphStyle('NOTE', parent=B, backColor=colors.HexColor('#e8f1fa'), borderColor=colors.HexColor('#6fa3d1'),
                      borderWidth=0.6, borderPadding=4, spaceBefore=4, spaceAfter=6)


def P(t, s=B): return Paragraph(t, s)
def bullets(items): return [Paragraph(i, BUL, bulletText='•') for i in items]


def fig(name, width_mm, caption, max_h_mm=None):
    p = FIG / name
    im = PILImage.open(p)
    w, h = im.size
    wmm = width_mm
    hmm = wmm * h / w
    if max_h_mm and hmm > max_h_mm:
        hmm = max_h_mm; wmm = hmm * w / h
    shutil.copy(p, DOCS / 'img' / name)
    return KeepTogether([Image(str(p), width=wmm * mm, height=hmm * mm), P(caption, CAP), Spacer(1, 4)])


def table(rows, widths, header=True, font=8.3, zebra=True):
    t = Table([[Paragraph(str(c), ParagraphStyle('c', parent=B, fontSize=font, leading=font + 2, spaceAfter=0)) for c in r] for r in rows],
              colWidths=[w * mm for w in widths], repeatRows=1 if header else 0)
    st = [('GRID', (0, 0), (-1, -1), 0.3, colors.HexColor('#aaaaaa')), ('VALIGN', (0, 0), (-1, -1), 'TOP'),
          ('LEFTPADDING', (0, 0), (-1, -1), 3), ('RIGHTPADDING', (0, 0), (-1, -1), 3), ('TOPPADDING', (0, 0), (-1, -1), 2), ('BOTTOMPADDING', (0, 0), (-1, -1), 2)]
    if header: st.append(('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#dbe7f3')))
    if zebra:
        for i in range(1, len(rows)):
            if i % 2 == 0: st.append(('BACKGROUND', (0, i), (-1, i), colors.HexColor('#f6f8fa')))
    t.setStyle(TableStyle(st))
    return t


def build_pdf(path, title, story):
    def footer(c, d):
        c.saveState(); c.setFont('Helvetica', 7.5); c.setFillColor(colors.grey)
        c.drawString(15 * mm, 9 * mm, title)
        c.drawRightString(A4[0] - 15 * mm, 9 * mm, f'page {d.page}')
        c.restoreState()
    doc = BaseDocTemplate(str(path), pagesize=A4, leftMargin=15 * mm, rightMargin=15 * mm, topMargin=14 * mm, bottomMargin=16 * mm,
                          title=title, author='Claude Code')
    doc.addPageTemplates([PageTemplate(id='p', frames=[Frame(15 * mm, 16 * mm, A4[0] - 30 * mm, A4[1] - 30 * mm, id='f')], onPage=footer)])
    doc.build(story)


# ------------------------------------------------------------------------------------------------ shared content
PRINT_ROWS = [
    ['File', 'Qty', 'Part', 'Notes'],
    ['C1_housing_half_1_x1', 1, 'C1 housing half (carries fins 1 and 4, the 4 pilot holes of the seam)', 'Pegs/sockets align it with C2. Print upright as exported.'],
    ['C2_housing_half_2_x1', 1, 'C2 housing half (carries fins 2 and 3, seam counterbores)', 'Mirror of C1 with pegs.'],
    ['P_fin_x4', 4, 'Fin (cam-driven panel, 90° stop)', 'Identical x4; hinge bore is 4.5 mm.'],
    ['L_catch_cap_x4', 4, 'Catch cap (open-top clip with screw boss)', 'Identical x4. Print the boss up so the 2.6 mm pilot is vertical.'],
    ['R_rotor_x1', 1, 'Rotor: shaft, 4 cams, crown arms, knob', 'Four 3.4 mm vertical holes in the crown arms.'],
    ['U_output_hub_x1', 1, 'Cartridge output hub', ''],
    ['Q_thrust_collar_x1', 1, 'Lower thrust collar', 'Stays bonded (2.5 mm tall ring).'],
    ['X_double_d_adapter_x1', 1, 'Double-D adapter', ''],
    ['T_winding_cap_x1', 1, 'Winding and latch cap', ''],
    ['D_cartridge_dock_x1', 1, 'Cartridge dock (3 ring pads, 4 feet)', 'Feet have 3.4 mm radial holes.'],
    ['N_bayonet_collar_x1', 1, 'Bayonet retaining collar', ''],
    ['I_locking_pin_x1', 1, 'Quarter-turn locking pin', ''],
    ['M_casing_x1', 1, 'Cartridge casing (3 lid bosses)', ''],
    ['F_lid_x1', 1, 'Cartridge lid (3 screw ears)', ''],
    ['A_pushrod_x1', 1, 'Short side pushrod', ''],
    ['B_release_yoke_x1', 1, 'Upward release yoke', ''],
    ['S_servo_cradle_x1', 1, 'SG90 cradle (4 pads, 2.6 mm pilots)', ''],
    ['G_servo_keeper_x1', 1, 'Servo keeper', 'Stays bonded (1.5 mm plate).'],
    ['J_horn_saddle_x1', 1, 'Double-arm horn saddle', 'Measure your horn first (as in your model).'],
    ['samples/S_unloaded_spiral_*_x1', '1 each', 'Unloaded spiral springs 1.6 / 2.0 / 2.4 mm beam', 'Print references from your Part Studio 24, unchanged.'],
    ['samples/W_unloaded_return_leaf_x1', 1, 'Return leaf (1 mm installation preload)', 'Root stays bonded.'],
]


def hardware_rows(v2):
    rows = [['Ref in CAD', 'Fastener', 'Qty', 'Joint', 'Driver'],
            ['HW seam screw 1-4', 'M3 x 8 socket-head cap (ISO 4762)', 4, 'C2 counterbore → thread into C1 across the seam; 2 per seam at z=8 and z=44', '2.5 mm hex'],
            ['HW L1-L4 cap screw', 'M3 x 8 button head (ISO 7380)', 4, 'Rotor arm → catch cap boss (vertical)', '2.0 mm hex'],
            ['HW H1-H4 hinge screw', 'M4 x 25 button head (ISO 7380)', 4, 'Through -Y ear and fin barrel, threads into +Y ear (replaces printed pin H and cap K)', '2.5 mm hex']]
    if v2:
        rows.append(['HW top-tube support screw 1-8', 'M3 x 6 button head', 8, 'Upper BT80 tube → thick supports between the fins (z=12 and z=36)', '2.0 mm hex'])
    else:
        rows.append(['HW upper sleeve screw 1-4', 'M3 x 6 button head', 4, 'Upper BT80 tube → pads behind the upper sleeve (z=76)', '2.0 mm hex'])
    rows += [['HW dock ring screw 1-3', 'M3 x 10 button head', 3, 'Lower BT80 tube → housing sleeve → dock ring pad (z=-26.5)', '2.0 mm hex'],
             ['HW cradle screw 1-4', 'M3 x 10 button head', 4, 'Lower BT80 tube → dock foot → cradle pad (z=-67.2)', '2.0 mm hex'],
             ['HW lid screw 1-3', 'M3 x 10 button head', 3, 'Lid ear → casing boss (vertical)', '2.0 mm hex']]
    return rows


def hardware_totals(v2):
    m36 = 8 if v2 else 4
    return (f'<b>Totals:</b> M3x6 × {m36}, M3x8 × 8 (4 socket + 4 button), M3x10 × 10, M4x25 × 4 = {m36 + 8 + 10 + 4} screws. '
            'Not printed or screwed: 1 SG90 servo with horn, 2 BT80 airframe tubes, epoxy for Q, G, the return-leaf root and the horn saddle J.')


def verification_text(tag):
    v = VERIFY[tag]
    ov = 'none' if not v['printed_overlaps'] else str(v['printed_overlaps'])
    return f"{v['parts']} parts, all watertight; printed-part interference: {ov}; screw/thread engagement pairs: {v['hardware_pairs']} (intended)."


# ------------------------------------------------------------------------------------------------ V1
def v1():
    s = []
    s += [P('V1 – Screwed assembly guide', H1),
          P('ARC BT80 airbrake, <i>reinforced bottom spring, 90° stop</i> – your Assembly 23 model with every bonded joint turned into a screw joint.', B),
          P(f'Onshape document (public, Free plan): <a href="{DOC_URL}" color="blue">ARC BT80 Airbrake - V1 Screwed + V2 Compact (Claude build)</a><br/>'
            'Elements: <b>V1-A</b> closed state, <b>V1-B</b> fully open (90° / rotor 65° / trigger up), <b>ASM-V1</b> assembly with mates and hardware, '
            '<b>SAMPLES</b> unloaded spirals, <b>01 - V1 screwed + V2 compact (source)</b> Feature Studio (parameter <i>V2 compact head</i> = off).', SM),
          fig('v1_assembled.png', 70, 'V1 closed (Onshape render). Tan = reference BT80 tubes with the drill holes; dark grey = hardware.', 110)]
    s += [P('1 &nbsp; What changed from your model', H2),
          table([['Joint (your model)', 'Now'],
                 ['C1 / C2 housing seam: bond', '4 × M3x8 across the seam, on inward ribs at z=8 and z=44 (peg alignment kept)'],
                 ['Hinge pin H + end cap K: printed pin, bond', 'M4x25 button-head screw per hinge; thread into the +Y ear; bores are now 4.5 mm; K removed'],
                 ['Catch cap L: bond to rotor arm (could not slide on: closed socket)', 'Open-top clip with a screw boss under the arm; 1 × M3x8 each. Crown arm gets a 3.4 mm hole'],
                 ['Sleeves: glue to BT80', 'Upper sleeve: 4 × M3x6 into pads. Lower sleeve + dock ring + tube: 3 × M3x10'],
                 ['Cradle S to dock feet: bond', '4 × M3x10 radial through tube, foot, cradle pad (foot extended 1.5 mm lower, pad thickened to R26)'],
                 ['Lid F to casing M: bond', '3 × M3x10 vertical through lid ears into casing bosses'],
                 ['Q collar, G keeper, W return-leaf root', 'Still bonded: sections are under 3 mm, no room for a screw'],
                 ['Seam boss z 63..67', 'Raised to z 63.5..67 so the new cap screw heads clear it at every rotor angle']], [62, 118]),
          PageBreak(), fig('v1_overview_exploded.png', 105, 'Exploded overview. Order top to bottom: upper tube + sleeve screws, rotor with caps and cap screws, fins with hinge screws around the housing, cartridge, cradle, lower tube.', 235), PageBreak()]
    s += [P('2 &nbsp; Print list', H2),
          P('STLs are in <font face="Courier">onshape/exports/v1/print</font>. Each file is auto-oriented (least overhang of the 6 axis orientations) with z-min at 0; check orientation in your slicer. '
            'The 2.6 mm pilot holes and 3.4 mm clearance holes are printed as modelled: do not scale them, and do not add supports inside them.', B),
          table(PRINT_ROWS, [48, 11, 62, 59], font=7.8)]
    s += [PageBreak(), P('3 &nbsp; Hardware and tools', H2), table(hardware_rows(False), [36, 40, 9, 77, 18], font=7.8), Spacer(1, 3), P(hardware_totals(False), B)]
    s += bullets(['Self-tapping into PLA/PETG: run each screw once into its pilot hole before final assembly (this cuts the thread), then back it out.',
                  'Snug plus about 1/8 turn. Over-tightening strips a printed thread long before the screw yields; M3 into a 2.6 mm pilot gives a few N·m of strip torque at best.',
                  'The tube screws only pass through the 0.5 mm tube wall and thread into printed pads. Use a drop of thread-lock only on steel-to-steel joints (none here).'])
    s += [P('4 &nbsp; Prepare the BT80 tubes', H2),
          P('BT80 is OD 66.04 mm, ID about 65.0 mm. The sleeves are 64.6 mm OD. Azimuth 0° is fin 1; angles run counter-clockwise looking down the rocket from the nose. '
            'Distances d are measured from the tube end that meets the airbrake. Drill 3.4 mm holes.', B),
          fig('v1_upper_tube.png', 180, 'Upper tube template (unrolled, 1:1 horizontal scale).', 70),
          fig('lower_tube.png', 180, 'Lower tube template. Mark directly, or drill through the printed sleeve holes while the tube is on.', 90),
          table([['Tube', 'Hole', 'd (mm)', 'Azimuth', 'Screw'],
                 ['Upper', '4 holes', '9.0', '0, 90, 180, 270°', 'M3x6'],
                 ['Lower', '3 holes', '11.5', '90, 200, 340°', 'M3x10 (dock ring)'],
                 ['Lower', '4 holes', '52.2', '45, 135, 225, 315°', 'M3x10 (cradle)']], [25, 25, 25, 60, 45]),
          P('The lower tube needs at least 85 mm of length below the housing to cover the cradle; the upper tube needs at least 43 mm above the housing (the reference tubes in the CAD are 85 and 43 mm).', SM)]
    # steps
    s += [PageBreak(), P('5 &nbsp; Assembly sequence', H2)]
    s += [P('Step 1 – Rotor group (catch caps)', H3),
          P('Hold the rotor with the arms at 0/90/180/270°. Offer each catch cap <b>from below</b>: the 3 mm arm sits in the open-top slot, the hook points outward, '
            'the boss with the 2.6 mm pilot is directly under the arm. Drive one M3x8 button-head screw per cap from above through the arm hole into the boss. '
            'Do this with the housing halves still apart: the closed housing leaves no access.', B),
          fig('v1_rotor_caps.png', 120, 'Caps L1–L4 offered up under the arms, screws above. The rotor arms carry the screw holes.', 85)]
    s += [P('Step 2 – Fins on the housing halves', H3),
          P('C1 carries fins 1 and 4, C2 carries fins 2 and 3 (fin n sits at (n−1) × 90°). For each fin, seat the barrel between the two ears and run an M4x25 button-head screw through the ear on the '
            '<b>clockwise side</b> (seen from the nose), through the barrel, and into the other ear. The head sits in the pocket; stop when it seats. '
            'The fin must swing 0–90° with no drag. If it binds, back the screw off a quarter turn and re-check that the barrel sits centred between the ears (0.4 mm each side).', B),
          fig('v1_hinge.png', 120, 'Hinge detail: M4x25 screw in line with the ear bores; fin barrel goes between the ears.', 85)]
    s += [P('Step 3 – Close the housing around the rotor', H3),
          P('Lay the rotor with its caps between the open halves, drop its shaft into the two bearing bores, and close the halves; the two pegs on C2 locate in the sockets of C1. '
            'Fit the four <b>M3x8 socket-head seam screws</b> (2.5 mm hex): heads go into the counterbores on the C2 ribs and thread into C1. '
            'Swing <b>fin 2 open</b> to reach the two screws at the 45° seam and <b>fin 3 open</b> for the two at the 225° seam. '
            f"I ray-checked the key path in the open-fin CAD state: all four screw heads are reachable by a straight 2.5 mm hex key (V1-B). Turn the rotor through 0–65° afterwards; it must move freely.", B),
          fig('v1_halves.png', 130, 'Halves apart: C1 (left) with fins 1 and 4, C2 (right) with fins 2 and 3, rotor and caps between, seam screws out to the right.', 100)]
    s += [PageBreak(), P('Step 4 – Cartridge and servo cradle (bench sub-assemblies)', H3),
          P('The cartridge mechanism is unchanged from your design. The order below follows your part labels (“fit last”, “attach after lid”, “bond after insertion”) and the geometry; '
            'I have not run the mechanism physically.', B)]
    s += bullets(['<b>Cradle S:</b> slide the SG90 into the cradle, bond keeper G, fit horn saddle J over the horn.',
                  '<b>Casing M:</b> insert hub U from the top; bond Q to the hub from below after insertion; place the printed spiral on the D stem with its three tabs in the casing slots.',
                  '<b>Lid F:</b> add the lid and fasten with three M3x10 button-head screws through the lid ears into the casing bosses (ears at 145°, 215° and 335°, chosen to stay clear of the pushrod, latch guide, return leaf and locking pin).',
                  '<b>Then</b> winding cap T, yoke B with pushrod A, return leaf W (root bonded), and the double-D adapter X last.',
                  '<b>Dock D:</b> seat the casing in the dock and lock it with bayonet collar N and pin I (quarter turn, unchanged).',
                  '<b>Cradle to dock:</b> the cradle pads sit against the dock feet. The four M3x10 screws go in through the lower tube in Step 5.'])
    s += [fig('v1_module.png', 105, 'Cartridge exploded top to bottom: adapter X, cap T, lid F with its three screws, spring V, casing M, hub U and collar Q, dock D with ring screws, cradle S with the four cradle screws.', 170)]
    s += [P('Step 5 – Join module, housing and lower tube', H3),
          P('Push rotor D-key into the hub socket while sliding the dock ring into the lower sleeve (0.5 mm radial gap). Insert this assembly, module end first, into the top of the lower BT80 tube until the '
            'housing base ring seats on the tube end. Align the tube holes with the sleeve holes and fit <b>3 × M3x10</b> (dock ring, 90/200/340°) and <b>4 × M3x10</b> (cradle pads, 45/135/225/315°). '
            'Each of the 3 ring screws passes through the tube wall, the sleeve (3.4 mm clearance) and threads into a pad inside the dock ring; the cradle screws pass through the tube and the dock foot into the cradle pad.', B),
          P('Step 6 – Upper tube', H3),
          P('Slide the upper tube down over the upper sleeve until it butts the housing top (z=67). Fit 4 × M3x6 button-head screws (0/90/180/270°, 9 mm from the tube end) into the pads behind the sleeve.', B),
          P('Step 7 – Function check', H3)]
    s += bullets(['Each fin swings 0–90° and stops hard at 90° on the outer compression stop.',
                  'Rotor turns 0–65°; at 65° the catch hooks clear the fin tabs and the cams kick the fins open.',
                  'Trigger lifts 4.5 mm and releases the latch; the return leaf brings it back.',
                  'All 26 screws are snug; no screw head proud of the tube except the button heads (1.65 mm).'])
    s += [fig('v1_open.png', 75, 'V1-B: all fins at 90°, rotor at 65°, trigger up (Onshape render).', 120)]
    s += [P('6 &nbsp; Checks run on this model', H2),
          table([['Check', 'Result'],
                 ['Feature regeneration (Part Studio + FeatureScript)', 'OK, about 3–8 s'],
                 ['V1-A closed', verification_text('V1 closed')],
                 ['V1-B open (90°, 65°, 4.5 mm)', verification_text('V1 open')],
                 ['Interference known from your original', 'Return leaf W reference vs yoke B in the pressed-trigger state (10 mm³); latch disk T vs yoke B at some rotor angles; both are in your model and unchanged'],
                 ['Seam screw access', 'Straight 2.5 mm hex key reaches all four heads with fins 2 and 3 open (ray test)'],
                 ['Assembly mates', '24 features (3 mate groups, 4 hinge revolutes 0–90°, rotor revolute 0–65°, trigger slider 0–4.5 mm, servo-pusher revolute): all solve OK']], [60, 120]),
          P('<b>Not verified:</b> physical print fit and thread strength, servo torque and latch behaviour (unchanged from your design), and the mate motion itself (the Onshape API accepted the mates but would not move them from a script, so open the assembly and drag a fin to confirm).', WARN)]
    build_pdf(DOCS / 'V1_assembly_guide.pdf', 'V1 screwed assembly guide - ARC BT80 airbrake', s)


# ------------------------------------------------------------------------------------------------ V2
def v2():
    s = []
    s += [P('V2 – Compact head assembly guide', H1),
          P('Same mechanism and fins as V1, but the fins live in a smaller-diameter head that slides <i>inside</i> the upper BT80 tube. '
            'You cut four slits in that tube; each cut-out piece is glued onto its fin and rides with it.', B),
          P(f'Onshape: <a href="{DOC_URL}" color="blue">ARC BT80 Airbrake - V1 Screwed + V2 Compact (Claude build)</a>. Elements: <b>V2-A</b> closed, <b>V2-B</b> fully open, <b>ASM-V2</b> assembly, '
            'Feature Studio parameter <i>V2 compact head</i> = on.', SM),
          fig('v2_assembled.png', 70, 'V2 closed. The upper tube covers the fin zone; only a 4 mm stop ring of the airbrake is exposed between the tubes.', 110)]
    s += [P('1 &nbsp; The idea and the numbers', H2),
          P('Your sketches: the upper BT80 tube is cut with slits around the fins, the cut-out pieces are glued to the fins and the sleeve fit stays at the bottom. '
            'For the top connection, supports come back in the four solid strips between the fins.', B),
          table([['Item', 'V1', 'V2'],
                 ['Fin shell radii (printed)', 'R30.62 – 33.02', 'R29.9 – 32.3 (64.6 mm OD = your sleeve OD)'],
                 ['Outer skin', 'printed, flush with the tube (66.04 mm)', 'glued BT80 cut-out R32.5 – 33.02 (0.52 mm wall); 0.2 mm glue gap to the fin'],
                 ['Head / housing OD', '66.04 mm (flush)', '64.6 mm inside the tube (tube ID 65.0 mm, 0.2 mm radial clearance)'],
                 ['Upper sleeve', '18 mm, z=67..85', 'removed: replaced by the 8 supports + 6 mm top ring (z 66.9..73)'],
                 ['Supports', 'none (thin 2.8 mm pillars)', '4 thick strips between the fins R26.8–32.3 (two pieces, clear of the cam band z 18.5..29.5) + the 4 under-fin stop blocks R27–32.3'],
                 ['Lower sleeve', '18 mm, OD 64.6 mm', 'unchanged (sleeve fit)'],
                 ['Exposed airbrake between tubes', '82 mm (z −15..67)', '<b>4 mm</b> stop ring (z −15..−11)'],
                 ['Printed stack, housing incl. sleeve', '118 mm (z −33..85)', '111.4 mm (z −33..78.4)'],
                 ['Whole printed assembly incl. cradle', '178.5 mm', '171.9 mm'],
                 ['Cam peak radius', '29.0', '28.6 (keeps 0.9 mm to the pillars)']], [46, 52, 82]),
          Spacer(1, 4), fig('compare_length.png', 165, 'V1 vs V2 side by side (tubes cut in half for the view). The exposed band the airbrake takes up in the rocket drops from 82 mm to 4 mm because the upper tube now covers the fins.', 110),
          P('<b>Why supports are still needed:</b> a flush butt joint between two tubes has no load path and nothing to retain it. In V1 the pillar wall and the 18 mm glue sleeves carry that; in V2 the thin wall is gone, so the thick strips (screwed to the tube) and the sleeve fit take over.', NOTE),
          fig('v2_radial.png', 110, 'Radial stack at a seam strip (z=36): fin, 0.2 mm gap, glued tube piece, support strip. All radii in the CAD are checked against this.', 100)]
    s += [PageBreak(), P('2 &nbsp; Print list', H2),
          P('STLs: <font face="Courier">onshape/exports/v2/print</font>. Identical to V1 except the housing halves (supports and top ring) and the fins (thinner shell). Cut-out pieces TP1–TP4 are <b>not printed</b>.', B),
          table(PRINT_ROWS, [48, 11, 62, 59], font=7.8)]
    s += [P('3 &nbsp; Hardware and tools', H2), table(hardware_rows(True), [36, 40, 9, 77, 18], font=7.8), Spacer(1, 3), P(hardware_totals(True), B)]
    s += [P('4 &nbsp; Prepare the upper tube (slits) and the cut-outs', H2),
          P('Cut the four windows (38.6 × 60.2 mm, centred on 0/90/180/270°, starting 1.8 mm from the end that meets the airbrake). '
            'From each piece of waste trim a <b>37.5 × 42 mm</b> cut-out (the dashed outline), edges square, ~0.3 mm sanded off the corners. '
            'That leaves about 0.6 mm of kerf at each side and 1 mm above, and about 17 mm of open window below the cut-out so the fin can swing down and out. '
            'Drill the eight 3.4 mm screw holes (the strips between the windows). The lower tube is drilled exactly as in V1.', B),
          fig('v2_upper_tube.png', 180, 'Upper tube template (unrolled): windows to cut, the cut-out piece trimmed from each waste, and the eight holes.', 110),
          fig('lower_tube.png', 180, 'Lower tube template, same as V1.', 90),
          table([['Tube', 'Feature', 'd (mm)', 'Azimuth', 'Note'],
                 ['Upper', '4 windows', '1.8 → 62.0', '0, 90, 180, 270° ±33.5°', '38.6 wide at the OD'],
                 ['Upper', '4 cut-outs', '19 → 61', 'same centres, ±32.5°', '37.5 × 42 mm, glued to the fins'],
                 ['Upper', '8 holes (M3x6)', '23 and 47', '45, 135, 225, 315° (both rows)', 'centred on each strip'],
                 ['Lower', '3 holes (M3x10)', '11.5', '90, 200, 340°', 'ring screws'],
                 ['Lower', '4 holes (M3x10)', '52.2', '45, 135, 225, 315°', 'cradle screws']], [18, 32, 30, 55, 45]),
          fig('v2_tube_cutout.png', 105, 'The upper tube with its four slits, the four cut-out pieces (tan) and the fins (orange) they are glued to.', 100)]
    s += [PageBreak(), P('5 &nbsp; Assembly sequence', H2),
          P('Steps 1–4 are the same as V1 (rotor group, fins on the halves, close the housing, cartridge and cradle): see the V1 guide for the rotor/cap, hinge and seam-screw procedure; '
            'the parts and screw positions are identical. Differences:', B)]
    s += bullets(['<b>Seam screws</b> are at z=8 and z=44 inside the thick strips; both seam strips also take the tube screws at z=12 and z=36 centred on the seam, so those threads bite across the clamped halves.',
                  '<b>Fins</b> have R29.9–32.3 shells: the cut-out pieces are added later (step 6), not now.',
                  '<b>Top ring</b> (z 66.9–73) replaces the 18 mm upper sleeve; the rotor knob sits 5 mm above it inside the tube.'])
    s += [fig('v2_halves.png', 130, 'V2 housing halves apart: the thick strips and the short top ring replace the upper sleeve.', 100),
          P('Step 5 – Module and lower tube', H3),
          P('Exactly as V1 step 5 (3 ring screws and 4 cradle screws M3x10 through the lower tube).', B),
          P('Step 6 – Upper tube and the glued cut-outs', H3),
          P('Close all four fins. Slide the airbrake head into the <b>upper tube from its cut end</b> (the tube butts the 4 mm stop ring at z=−11) and rotate it so the windows sit over the fins. '
            'Fit the 8 M3x6 button-head screws through the tube into the strips: with the tube on, you should be able to see all eight pilot holes through the tube holes.', B),
          P('Now glue each cut-out onto its fin: wipe the fin’s outer face, put a thin layer of epoxy or CA gel on the fin (0.2 mm gap = glue line), place the cut-out in the window, '
            'and hold it with masking tape across the window until cured. <b>Keep glue off the window edges and the surrounding tube</b> (a strip of tape or wax on the tube edges) '
            'or the fin will be glued shut. After curing, cut any glue bridge and check that the fin lifts out of its window.', WARN),
          P('Step 7 – Function check', H3)]
    s += bullets(['Fins open to 90° carrying their cut-outs: the cut-out lower edge swings down through the open lower part of the window and clears the tube (checked at 15/40/65/90°, no interference).',
                  'Rotor 0–65°; hooks release the tabs; cams kick the fins; trigger and return leaf as in V1.',
                  'Eight tube screws and seven lower-tube screws snug (15 screws touch the tubes in total).'])
    s += [fig('v2_overview_exploded.png', 100, 'V2 exploded: upper tube with its eight screws, rotor, fins with hinge screws and glued cut-outs, housing with supports, cartridge, cradle, lower tube.', 215),
          fig('v2_open.png', 75, 'V2-B: fins at 90° carrying their cut-outs, rotor at 65° (Onshape render).', 120)]
    s += [P('6 &nbsp; Checks run on this model', H2),
          table([['Check', 'Result'],
                 ['V2-A closed', verification_text('V2 closed')],
                 ['V2-B open (90°, 65°, 4.5 mm)', verification_text('V2 open')],
                 ['Cut-outs TP1–4 vs housing, fins and tube at 15/40/65/90°', 'No overlap (they start at z=8 so the lower edge clears the stop block)'],
                 ['Diameters', 'Fin OD 64.6; tube ID 65.0; tube OD 66.04; support OD 64.6; stop ring OD 66.04 (all read from the CAD)'],
                 ['Seam screw access', 'Straight 2.5 mm hex key reaches all four heads with fins 2 and 3 open (ray test)'],
                 ['Assembly mates', '28 features (adds a group per fin with its cut-out): all solve OK']], [60, 120]),
          P('<b>Open points for you:</b> (1) exposed band 4 mm vs printed stack 111 mm: the printed stack only shortens by 6.6 mm because the housing still has to carry the same mechanism. '
            '(2) The tube keeps only a 1.8 mm ring below the windows: epoxy it to the stop ring and rely on the eight screws. '
            '(3) Cam peak was reduced 29 → 28.6 mm for pillar clearance, which trims the kick slightly. (4) Mate motion not scripted: drag a fin in ASM-V2 to confirm.', WARN)]
    build_pdf(DOCS / 'V2_assembly_guide.pdf', 'V2 compact head assembly guide - ARC BT80 airbrake', s)


if __name__ == '__main__':
    which = sys.argv[1:] or ['v1', 'v2']
    if 'v1' in which: v1()
    if 'v2' in which: v2()
    print('docs written', list(DOCS.glob('*.pdf')))
