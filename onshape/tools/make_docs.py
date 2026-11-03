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

SCAN = json.load(open(WORK / 'scan.json')) if (WORK / 'scan.json').exists() else {}


def latch_free_angle():
    free = [r for (o, r, ov) in SCAN.get('latch', []) if o == 3.0 and not ov]
    return min(free) if free else None


def latch_blocked_from():
    blocked = [o for (o, r, ov) in SCAN.get('latch', []) if r == 0 and ov]
    return min(blocked) if blocked else None


def cam_first_contact():
    hit = [r for (r, ov) in SCAN.get('cam', []) if ov]
    return min(hit) if hit else None


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
        rows.append(['HW top-tube support screw 1-8', 'M3 x 5 button head', 8, 'Upper BT80 tube → thick supports between the fins (z=12 and z=36)', '2.0 mm hex'])
    else:
        rows.append(['HW upper sleeve screw 1-4', 'M3 x 6 button head', 4, 'Upper BT80 tube → pads behind the upper sleeve (z=76)', '2.0 mm hex'])
    rows += [['HW dock ring screw 1-3', 'M3 x 10 button head', 3, 'Lower BT80 tube → housing sleeve → dock ring pad (z=-26.5)', '2.0 mm hex'],
             ['HW cradle screw 1-4', 'M3 x 10 button head', 4, 'Lower BT80 tube → dock foot → cradle pad (z=-67.2)', '2.0 mm hex'],
             ['HW lid screw 1-3', 'M3 x 10 button head', 3, 'Lid ear → casing boss (vertical)', '2.0 mm hex']]
    return rows


def hardware_totals(v2):
    short = 'M3x5 × 8' if v2 else 'M3x6 × 4'
    n = 8 if v2 else 4
    return (f'<b>Totals:</b> {short}, M3x8 × 8 (4 socket + 4 button), M3x10 × 10, M4x25 × 4 = {n + 8 + 10 + 4} screws. '
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
def print_rows_v2():
    rows = [list(r) for r in PRINT_ROWS]
    for r in rows:
        if r[0].startswith('P_fin'): r[3] = 'Identical x4; hinge bore 4.5 mm; inward catch lug (plate + wall) on the top of the shell.'
        if r[0].startswith('L_catch_cap'): r[3] = 'Identical x4; open-top clip with an upward hook finger; print boss down so the 2.6 mm pilot is vertical.'
        if r[0].startswith('C1_'): r[2] = 'C1 housing half (fins 1 and 4, pilot holes of the seam, 4 thick strips)'
    return rows


def v2():
    free = latch_free_angle(); blocked = latch_blocked_from(); cam = cam_first_contact()
    s = []
    s += [P('V2 – Compact head assembly guide', H1),
          P('Same mechanism, hardware and fins as V1, but the fins live in a smaller-diameter head that slides <i>inside</i> the upper BT80 tube, '
            'and the whole latch stack (hook, crown arms, top bearing, knob) now sits <b>inside the fin height</b>: the fin top is only 4.8 mm below the head top. '
            'You cut four slits in the tube; each cut-out piece is glued onto its fin and rides with it.', B),
          P(f'Onshape: <a href="{DOC_URL}" color="blue">ARC BT80 Airbrake - V1 Screwed + V2 Compact (Claude build)</a>. Elements: <b>V2-A</b> closed, <b>V2-B</b> fully open, <b>ASM-V2</b> assembly, '
            'Feature Studio parameter <i>V2 compact head</i> = on.', SM),
          fig('v2_assembled.png', 70, 'V2 closed. The upper tube covers the fin zone; only a 4 mm stop ring of the airbrake is exposed between the tubes.', 110)]
    s += [P('1 &nbsp; The idea and the numbers', H2),
          P('Your sketches: slit the upper BT80 tube around the fins, glue the cut-outs to the fins, keep the sleeve fit at the bottom, put supports in the solid strips between the fins. '
            'Your fin-position drawing: the fin goes up to the top rim and everything under it moves up with it, so the whole piece is shorter than V1.', B),
          table([['Item', 'V1', 'V2 (22 mm drop)'],
                 ['Fin shell radii (printed)', 'R30.62 – 33.02', 'R29.9 – 32.3 (64.6 mm OD = your sleeve OD)'],
                 ['Outer skin', 'printed, flush with the tube (66.04 mm)', 'glued BT80 cut-out R32.5 – 33.02 (0.52 mm wall); 0.2 mm glue gap to the fin'],
                 ['Head OD', '66.04 mm (flush)', '64.6 mm inside the tube (tube ID 65.0 mm)'],
                 ['Fin catch', 'tab above the fin tip, hook outside the skin (z 51–63)', 'inward lug on the fin (plate z 47–50, inner wall z 41.6–50) hooked from inside by a finger on the catch cap (z 40.8–46)'],
                 ['Latch stack on the rotor', 'crown arms z 58.6–61.6, top bearing 68–73, knob 74–78', 'all 22 mm lower: arms 36.6–39.6, top bearing 46–51, knob 52–56'],
                 ['Upper sleeve', '18 mm, z 67..85', 'removed; 4.2 mm top ring z 54.6..58.8'],
                 ['Supports', 'none (thin 2.8 mm pillars)', '4 thick strips between the fins R27.4–32.3 (two pieces, clear of the cam band z 18.5..29.5) + the 4 under-fin stop blocks R27–32.3'],
                 ['Lower sleeve', '18 mm, OD 64.6 mm', 'unchanged (sleeve fit)'],
                 ['Fin top to head top', '28 mm', '4.8 mm'],
                 ['Exposed airbrake between tubes', '82 mm (z −15..67)', '<b>4 mm</b> stop ring (z −15..−11)'],
                 ['Printed housing incl. sleeve', '118 mm (z −33..85)', '91.8 mm (z −33..58.8)'],
                 ['Whole printed assembly incl. cradle', '178.5 mm', '<b>152.3 mm</b> (26.2 mm shorter than V1)'],
                 ['Cam peak radius', '29.0', '28.6 (keeps 0.9 mm to the pillars)']], [44, 54, 82]),
          Spacer(1, 4), fig('compare_length.png', 165, 'V1 vs V2 side by side (tubes cut in half for the view). The exposed band drops from 82 mm to 4 mm and the printed housing from 118 to 91.8 mm.', 110),
          P('<b>Why supports are still needed:</b> a flush butt joint between two tubes has no load path and nothing to retain it. In V1 the pillar wall and the 18 mm glue sleeves carry that; in V2 the thin wall is gone, so the thick strips (screwed to the tube) and the sleeve fit take over.', NOTE),
          fig('v2_radial.png', 110, 'Radial stack at a seam strip (z=36): fin, 0.2 mm glue gap, glued tube piece, support strip.', 100)]
    s += [PageBreak(), P('2 &nbsp; The new latch (what changed to get the fin to the rim)', H2),
          P('In V1 the fin tip carried a tab that a hook on the rotor grabbed from outside, above the fin. That hook swings sideways through the fin’s own window, so it cannot sit inside the fin height. '
            'In V2 the catch is turned inside out: the fin carries a small <b>lug</b> that reaches inward (plate at z 47–50 and an inner wall to z 41.6). '
            'The catch cap on each rotor arm carries a <b>finger</b> that stands just outside that wall (0.8 mm gap). The fin cannot move out until the rotor swings the finger away; '
            'the finger runs at R23.6–26, inside the support strips (R27.4+), so it can sweep past them.', B)]
    bullets_l = [f'Hold: at rotor 0° the fin can move about 1° (0.8 mm at the lug) and is blocked from {blocked:g}° (interference scan of the CAD).' if blocked else 'Hold: see scan.',
                 f'Release: with the fin held at 3°, the fin is free once the rotor is at {free:g}° or more (on the final model: still held at 14°, free at 16°).' if free else 'Release: see scan.',
                 f'Timing: the cams first touch the fins between 22° and {cam:g}° of rotor travel (on the final model: no contact at 22°, contact at 26°), so the fins are released before they are pushed.' if cam else 'Timing: see scan.',
                 'Finger and wall are 6 mm wide, finger 2.4 mm thick: the latch is a printed hook, so it is thinner than the V1 hook was strong; run it empty first.']
    s += bullets(bullets_l)
    s += [fig('v2_latch_plan.png', 175, 'Plan section at z=43.5: locked (left) and released (right). Orange: fin lug wall; green: finger on the catch cap and the rotor arm.', 90)]
    s += [P('3 &nbsp; Print list', H2),
          P('STLs: <font face="Courier">onshape/exports/v2/print</font>. Same files as V1 except the housing halves, fins (lug) and catch caps (finger). Cut-outs TP1–TP4 are <b>not printed</b>.', B),
          table(print_rows_v2(), [48, 11, 62, 59], font=7.8)]
    s += [P('4 &nbsp; Hardware and tools', H2), table(hardware_rows(True), [36, 40, 9, 77, 18], font=7.8), Spacer(1, 3), P(hardware_totals(True), B)]
    s += [P('5 &nbsp; Prepare the upper tube (slits) and the cut-outs', H2),
          P('Cut the four windows (38.6 × 63.8 mm, centred on 0/90/180/270°, starting 1.8 mm from the end that meets the airbrake). '
            'From each piece of waste trim a <b>37.5 × 42 mm</b> cut-out (the dashed outline), edges square, ~0.3 mm sanded off the corners. '
            'That leaves about 0.6 mm of kerf at each side and about 4.6 mm above, and about 17 mm of open window below the cut-out so the fin can swing down and out. '
            'Drill the eight 3.4 mm screw holes (the strips between the windows). The lower tube is drilled exactly as in V1.', B),
          fig('v2_upper_tube.png', 180, 'Upper tube template (unrolled): windows to cut, the cut-out piece trimmed from each waste, and the eight holes.', 110),
          fig('lower_tube.png', 180, 'Lower tube template, same as V1.', 90),
          table([['Tube', 'Feature', 'd (mm)', 'Azimuth', 'Note'],
                 ['Upper', '4 windows', '1.8 → 65.6', '0, 90, 180, 270° ±33.5°', '38.6 wide at the OD'],
                 ['Upper', '4 cut-outs', '19 → 61', 'same centres, ±32.5°', '37.5 × 42 mm, glued to the fins'],
                 ['Upper', '8 holes (M3x5)', '23 and 47', '45, 135, 225, 315° (both rows)', 'centred on each strip'],
                 ['Lower', '3 holes (M3x10)', '11.5', '90, 200, 340°', 'ring screws'],
                 ['Lower', '4 holes (M3x10)', '52.2', '45, 135, 225, 315°', 'cradle screws']], [18, 32, 30, 55, 45]),
          fig('v2_tube_cutout.png', 105, 'The upper tube with its four slits, the four cut-out pieces (tan) and the fins (orange) they are glued to.', 100)]
    s += [PageBreak(), P('6 &nbsp; Assembly sequence', H2),
          P('The order is the same as the V1 guide (rotor group, fins on the halves, close the housing, cartridge and cradle, module into the lower tube). Differences:', B)]
    s += bullets(['<b>Catch caps:</b> the finger points up. Offer each cap from below with the finger on the <b>outer</b> side of the arm tip; the screw is M3x8 at R20.4 (a clip with the arm in the open-top socket, boss under it).',
                  '<b>Latch set-up:</b> with the rotor at 0° each finger must stand outside the lug wall of its fin. Swing a fin out by hand: it should stop after about 1 mm. Turn the rotor to the release angle: the fin must then swing free.',
                  '<b>Seam screws:</b> the lower pair sit on ribs at z=8 as in V1; the upper pair (z=44) are M3x8 in the thick strips at R29.6, counterbore in the strip face at the window edge of the C2 side. Swing fin 2 (for the 45° seam) and fin 3 (225° seam) open to reach them.',
                  '<b>Fins</b> have R29.9–32.3 shells with the lug at the top; the cut-out pieces are added in step 7.',
                  '<b>Top ring</b> (z 54.6–58.8) replaces the 18 mm upper sleeve; the rotor knob (z 52–56) sits in it and the top bearing is at z 46–51.'])
    s += [fig('v2_rotor_caps.png', 120, 'Caps offered up under the arms (fingers up), screws above.', 85),
          fig('v2_halves.png', 130, 'V2 housing halves apart: the thick strips and the short top ring replace the upper sleeve.', 100),
          P('Step 5 – Module and lower tube', H3),
          P('Exactly as V1 step 5 (3 ring screws and 4 cradle screws M3x10 through the lower tube).', B),
          P('Step 7 – Upper tube and the glued cut-outs', H3),
          P('Close all four fins and lock the latch (rotor at 0°). Slide the airbrake head into the <b>upper tube from its cut end</b> (the tube butts the 4 mm stop ring at z=−11) and rotate it so the windows sit over the fins. '
            'Fit the 8 M3x5 button-head screws through the tube into the strips: with the tube on you should see all eight pilot holes through the tube holes.', B),
          P('Now glue each cut-out onto its fin: wipe the fin’s outer face, put a thin layer of epoxy or CA gel on the fin (0.2 mm gap = glue line), place the cut-out in the window, '
            'and hold it with masking tape across the window until cured. <b>Keep glue off the window edges and the surrounding tube</b> (a strip of tape or wax on the tube edges) '
            'or the fin will be glued shut. After curing, cut any glue bridge and check that the fin lifts out of its window.', WARN),
          P('Step 8 – Function check', H3)]
    s += bullets(['Fins open to 90° carrying their cut-outs: the cut-out lower edge swings down through the open lower part of the window and clears the tube (checked at 15/40/65/90°, no interference).',
                  'Latch: rotor 0° holds the fins; at the release angle the fins are free; the cams then kick them (rotor up to 65°).',
                  'Eight tube screws and seven lower-tube screws snug (15 screws touch the tubes in total).'])
    s += [fig('v2_overview_exploded.png', 100, 'V2 exploded: upper tube with its eight screws, rotor, fins with hinge screws and glued cut-outs, housing with supports, cartridge, cradle, lower tube.', 215),
          fig('v2_open.png', 75, 'V2-B: fins at 90° carrying their cut-outs, rotor at 65° (Onshape render).', 120)]
    s += [P('7 &nbsp; Checks run on this model', H2),
          table([['Check', 'Result'],
                 ['V2-A closed', verification_text('V2 closed')],
                 ['V2-B open (90°, 65°, 4.5 mm)', verification_text('V2 open')],
                 ['Latch hold / release / cam timing', (f'blocked from {blocked:g}° fin opening at rotor 0°; free from rotor {free:g}°; cams touch by {cam:g}° (not at 22°)' if (blocked and free and cam) else 'see scan')],
                 ['Cut-outs TP1–4 vs housing, fins and tube at 15/40/65/90°', 'No overlap (they start at z=8 so the lower edge clears the stop block)'],
                 ['Diameters', 'Fin OD 64.6; tube ID 65.0; tube OD 66.04; support OD 64.6; stop ring OD 66.04 (all read from the CAD)'],
                 ['Seam screw access', 'Straight 2.5 mm hex key reaches all four heads with fins 2 and 3 open (ray test)'],
                 ['Assembly mates', '28 features (adds a group per fin with its cut-out): all solve OK']], [60, 120]),
          P('<b>Open points for you:</b> (1) The new catch is a different mechanism from your tab-and-hook; its strength and the 16° release angle have not been tested on a print. '
            '(2) The tube keeps only a 1.8 mm ring below the windows: epoxy it to the stop ring and rely on the eight screws. '
            '(3) Cam peak was reduced 29 → 28.6 mm for pillar clearance, which trims the kick slightly. (4) Mate motion not scripted: drag a fin in ASM-V2 to confirm.', WARN)]
    build_pdf(DOCS / 'V2_assembly_guide.pdf', 'V2 compact head assembly guide - ARC BT80 airbrake', s)


def WARN_P(t):
    return Paragraph(t, WARN)


def torque_table():
    A, ZS, ZL, RF, RHO = 1.785e-3, 0.029, 0.0458, 0.0248, 1.1
    rows = [['Speed', 'Typical wind suction (Cp -0.2)', 'Pessimistic (Cp -0.6)']]
    for V in (50, 100, 150, 200):
        q = 0.5 * RHO * V * V
        cells = []
        for cp in (0.2, 0.6):
            N = q * cp * A * ZS / ZL
            cells.append('%.1f N on the finger, %.3f–%.3f N·m' % (N, 4 * 0.2 * N * RF, 4 * 0.4 * N * RF))
        rows.append(['%d m/s' % V] + cells)
    return rows


def v3():
    s = []
    s += [P('V3 – SG90 straight on the rotor: assembly guide', H1),
          P('Built from the 22 mm V2. The spring cartridge, trigger, pushrod, yoke, cradle and all the layers between the servo and the rotor are gone: '
            'one SG90 hangs under the rotor and turns it through its own horn. The fins, cams, rotor-mounted latch, housing and tube slits are the V2 ones.', B),
          P(f'Onshape: <a href="{DOC_URL}" color="blue">ARC BT80 Airbrake - V1 Screwed + V2 Compact (Claude build)</a>. Elements: <b>V3-A</b> closed, <b>V3-B</b> fully open, <b>ASM-V3</b> assembly. '
            'Feature Studio: module mode <i>3</i> with <i>V2 compact head</i> on.', SM),
          fig('v3_assembled.png', 62, 'V3 closed. Same upper tube and slits as V2; the servo is inside the housing, flush with its bottom edge.', 105),
          P('1 &nbsp; What changed', H2),
          table([['Item', 'V1', 'V2 (22 mm drop)', 'V3 (servo on rotor)'],
                 ['Printed housing incl. sleeve', '118 mm', '91.8 mm', '91.8 mm (same housing)'],
                 ['Everything below the housing', 'cartridge, dock, cradle (to z −93.5)', 'same', '<b>nothing</b>: the SG90 sits inside the housing, bottom flush at z −33'],
                 ['Whole assembly, top to bottom', '178.5 mm', '152.3 mm', '<b>91.8 mm</b> (servo inside the housing)'],
                 ['Printed parts (solid, PLA 1.24 g/cm³)', '180 g', '169 g', '<b>106 g</b> (−37 % vs V2)'],
                 ['Printed part count', '19 types', '19 types', '<b>5 types</b>: 2 housing halves, 4 fins, 4 catch caps, rotor'],
                 ['Drive', 'wound spiral spring + SG90 trigger', 'same', 'SG90 turns the rotor 0 → 65°'],
                 ['Latch', 'tab and hook on the rotor', 'lug + finger on the rotor', 'same as V2']], [50, 38, 38, 54]),
          Spacer(1, 4), fig('compare_length_v3.png', 175, 'V1, V2 and V3 side by side (tubes cut in half). V3 keeps the V2 head; everything under it is replaced by the servo.', 95),
          P('Removed printed parts: dock D, casing M, lid F, output hub U, bayonet collar N, locking pin I, winding cap T, double-D adapter X, thrust collar Q, '
            'pushrod A, release yoke B, servo cradle S, keeper G and horn saddle J (about 64 g), plus the spiral spring and return leaf.', B)]
    s += [P('2 &nbsp; How it works now', H2),
          P('The servo horn sits in a socket in the underside of the rotor hub, so rotating the servo rotates the rotor. At 0° the finger on each catch cap holds the fin lug (the V2 latch). '
            'The latch lets go between 14° and 15° of rotor travel; the cams first touch the fins at about 26° and finish the kick at 65°. '
            'With the rotor at 65° the cam holds each fin open about 14° and the airflow carries it the rest of the way to the 90° hard stop, as in V1 and V2. '
            'The servo only has to move the rotor and slide the finger off the lug: it does not carry the airbrake drag, because at 90° the fins rest on the stop.', B),
          fig('v3_overview_exploded.png', 100, 'Exploded V3. Top to bottom: upper tube with its screws, horn screw, rotor with catch caps and tube cut-outs, housing with fins, horn, servo with its two flange screws, lower tube with sleeve screws.', 175)]
    s += [P('3 &nbsp; Servo mount', H2),
          P('The SG90 sits <b>inside the housing with its bottom flush with the housing bottom edge (z −33)</b>, so nothing sticks out below. It hangs by its flange from two posts (azimuth 135° and 315°, off the seam) that grow out of the lower spokes: M2×8 self-tapping screws go up through the two tab holes into 1.6 mm pilots in the posts. '
            'To make room, the rotor’s lower bearing, its thrust collar and the four spokes that carry it moved <b>up</b> above the horn (bearing now z −0.8…2.2, spokes out to the support strips), and the rotor bottom stops at z −8.7. '
            'The shaft sits on the rotor axis, the horn lies in a round pocket and arm slot in the rotor hub, and the horn screw is dropped down through the rotor bore. '
            'The base ring has a 0.7 mm relief where the servo tab meets it. Three pads on the inside of the lower sleeve take the three M3×10 screws that hold the lower tube.', B),
          fig('v3_mount_sections.png', 165, 'Plan sections: left through the horn socket (z −7.6), middle through the two servo posts (z −12), right through the servo body and the sleeve pads (z −26).', 66),
          WARN_P('The servo, horn and tab-hole positions are standard SG90 numbers (body 22.7 × 12.2 × 22.7, tab holes 28.1 mm apart, horn arm 3.4 mm wide, 1.8 mm thick). '
                 '<b>Measure your own servo and horn before printing</b>; the post pilots and the horn pocket are the two places that must match.')]
    s += [P('4 &nbsp; Torque check (SG90)', H2),
          P('The load that matters is friction at the latch while the wind pulls the closed fins outward: the finger has to slide off the lug under that load. '
            'Fin area 1785 mm², latch 45.8 mm and skin centre 29 mm above the hinge, friction 0.2–0.4, finger at R24.8. '
            'The SG90 stall torque is 0.176 N·m at 4.8 V (0.216 at 6 V); I would only rely on about half of it (0.09 N·m). '
            'Rotor spin-up and the cam kick are negligible (about 0.001 N·m): the wind assists the opening.', B),
          table(torque_table(), [28, 76, 76]),
          P('So the stock SG90 has margin to roughly <b>77–109 m/s</b> if the wind suction on the closed fins is as bad as the pessimistic case, and to roughly <b>134–188 m/s</b> in the typical case. '
            'Above that, use a metal-gear servo (about 0.22–0.25 N·m), polish the finger and lug, or add a ramp. The suction coefficient is an assumption: it needs a wind-tunnel or CFD number, or a ground test of the closed fins in a fan. '
            'The script is <font face="Courier">tools/torque_check.py</font>.', B)]
    s += [P('5 &nbsp; Print list and hardware', H2),
          table([['File', 'Qty', 'Part', 'Notes'],
                 ['C1_housing_half_1_x1 / C2_housing_half_2_x1', '1 + 1', 'Housing halves', 'Servo posts, sleeve pads and strips are part of the halves. Same print orientation as V2.'],
                 ['P_fin_x4', '4', 'Fin', 'Same as V2.'],
                 ['L_catch_cap_x4', '4', 'Catch cap', 'Same as V2.'],
                 ['R_rotor_x1', '1', 'Rotor with horn socket', 'Hub with horn pocket and arm slot on the underside; the pocket opens into the bore (horn-screw access). Print upright.']], [62, 12, 40, 66]),
          Spacer(1, 3),
          table([['Ref in CAD', 'Fastener', 'Qty', 'Joint', 'Driver'],
                 ['HW seam screw 1-4', 'M3 × 8 socket-head cap', 4, 'C2 counterbore → C1, z=8 and z=44', '2.5 mm hex'],
                 ['HW L1-L4 cap screw', 'M3 × 8 button head', 4, 'Rotor arm → catch cap boss', '2.0 mm hex'],
                 ['HW H1-H4 hinge screw', 'M4 × 25 button head', 4, 'Fin hinge, threads into the +Y ear', '2.5 mm hex'],
                 ['HW top-tube support screw 1-8', 'M3 × 5 button head', 8, 'Upper BT80 tube → strips between the fins', '2.0 mm hex'],
                 ['HW sleeve screw 1-3', 'M3 × 10 button head', 3, 'Lower BT80 tube → sleeve → pad (z=-26.5)', '2.0 mm hex'],
                 ['HW servo flange screw 1-2', 'M2 × 8 button head, self-tapping', 2, 'Servo tabs → housing posts', '1.5 mm hex or PH0'],
                 ['HW horn screw', 'M2 × 6 (the one supplied with the servo)', 1, 'Horn → servo spline, from above through the rotor bore', 'PH0 / 1.5 mm hex']], [38, 40, 9, 63, 22], font=7.8),
          P('<b>Totals:</b> M3×5 × 8, M3×8 × 8, M3×10 × 3, M4×25 × 4, M2×8 × 2 plus the horn screw = 26 screws. Not printed or screwed: 1 SG90 servo with horn, 2 BT80 airframe tubes, epoxy for the tube cut-outs.', B)]
    s += [P('6 &nbsp; Tubes', H2),
          P('The upper tube is cut exactly as in the V2 guide (four windows 38.6 × 63.8 mm, four 37.5 × 42 mm cut-outs glued to the fins, eight M3 holes). '
            'The lower tube needs only three 3.4 mm holes.', B),
          fig('v3_lower_tube.png', 165, 'Lower tube template.', 55)]
    s += [P('7 &nbsp; Assembly sequence', H2)]
    s += bullets([
        'Steps 1–4 as in V2: hinge screws, catch caps (M3×8) on the rotor arms, rotor into one half, fins, second half, four seam screws (2.5 mm hex).',
        '<b>Set the servo to its 0° position first</b> (servo tester or the flight computer), then press the horn on the spline so that the arm points where the pocket slot is when the rotor is locked at 0°.',
        'Drop the horn into the socket in the rotor hub from below, arm in its slot; slide the servo spline into the horn, flange under the two posts, long axis along the 135°/315° line.',
        'Drive the two M2×8 flange screws up through the tab holes. Then put the M2×6 horn screw down through the rotor bore and access hole (1.5 mm hex or small Phillips).',
        'Route the servo lead down the lower tube. Slide the lower tube over the sleeve and fit the three M3×10 screws.',
        'Glue the tube cut-outs to the fins, slide the upper tube on and fit the eight M3×5 screws, as in V2.',
        'Function check with the servo only: command 0° → 70° and back; the fins should unlatch around 15°, be kicked from about 26° and stop at 65° of horn travel.'])
    s += [P('8 &nbsp; Checks run on this model', H2),
          table([['Check', 'Result'],
                 ['V3-A closed / V3-B open (90°, 65°)', '45 bodies, all watertight; no printed-part overlap; the only overlap among references is the servo spline inside the horn (intended)'],
                 ['Rotor, horn and catch caps turned 0 → 65° (5° steps)', 'clear of both housing halves and the servo at every step'],
                 ['Latch hold / release', 'fin blocked from 1.5–2° opening at rotor 0°; free from rotor 15° (14° still overlaps by 0.4 mm³)'],
                 ['Cam timing', 'cams first touch the closed fin at about 26° of rotor travel'],
                 ['Fin + glued cut-out swept 0.5 → 90° against the upper tube', 'clear at every angle'],
                 ['Seam screw access', 'straight 2.5 mm hex key reaches all four heads with the fins open'],
                 ['Assembly mates', '21 features (fin groups, four hinges, rotor revolute): all solve OK']], [64, 116]),
          WARN_P('<b>Open points for you:</b> (1) Not tested on a print: the latch and the horn pocket. (2) The servo and horn dimensions are assumed. '
                 '(3) The wind-suction number behind the torque check is an assumption; give me your top speed. (4) Mate motion is not scripted: drag the rotor and a fin in ASM-V3. '
                 '(5) After the cam kick the fins stay out only while air flows; with no airflow they can fall back to about 14°. A positive hold open at 90° needs a detent or a longer cam. '
                 '(6) Ground-impact strength is not analysed: that is the FEA you mentioned (the posts, sleeve pads and fin hinges are the first places to look).')]
    build_pdf(DOCS / 'V3_assembly_guide.pdf', 'V3 servo-on-rotor assembly guide - ARC BT80 airbrake', s)


def mech():
    import math
    s = []
    r_f = 24.8
    s += [P('V3 mechanics: how it works and how every part moves', H1),
          P('Diagram companion to the V3 assembly guide (SG90 straight on the rotor). All pictures are made from the CAD model: the staged views pose the real meshes, '
            'and the timing numbers are measured on them, not drawn by hand.', B),
          fig('mech_map.png', 140, 'What moves. Green: the rotor group (rotor, horn, four catch caps, their screws) turns about the vertical axis. Orange: the four fins and their glued tube cut-outs hinge outward. Blue and grey: everything else is fixed, including the servo body.', 130),
          P('1 &nbsp; The idea in five sentences', H2)]
    s += bullets([
        '<b>Latched.</b> At 0° the finger on each catch cap sits just outside the lug on its fin, so the fin cannot open more than about 1°, however hard the wind pulls.',
        '<b>Unlatched.</b> The servo turns the rotor counter-clockwise (seen from the nose). By about 14° the fingers have slid sideways off the lugs: the fins are free.',
        '<b>Cam kick.</b> From about 26° the four cam lobes on the rotor push the four fin followers outward; the fins reach about 14° open at the end of the servo travel (65°).',
        '<b>Airflow.</b> From about 14° open the relative wind gets under the fin tip and pushes each fin the rest of the way until it lands on its 90° hard stop.',
        '<b>Stays deployed</b> while air flows: the stop carries the drag, not the servo. The cam keeps the fins from closing below about 14° as long as the servo stays at 65°.'])
    s += [P('2 &nbsp; The five stages', H2),
          P('Cut-away through the plane y = 0 looking at the cut face: fins 1 (right) and 3 (left) swing in the picture; the rotor and catch caps are cut open.', SM)]
    pics = [('mech_s0.png', 'Servo 0°, rotor 0°, fins closed. Latch holds.'), ('mech_s1.png', 'Rotor 14°. Fingers off the lugs.'),
            ('mech_s2.png', 'Rotor 40°. Cams push, fins 7°.'), ('mech_s3.png', 'Rotor 65°. Cams hold fins at 14°.'), ('mech_s4.png', 'Airflow has opened the fins to 90°, on the stop.')]
    from reportlab.platypus import Table as RT, TableStyle as RTS
    def img_cell(name, cap):
        from reportlab.platypus import Image as RI
        p = FIG / name; im = PILImage.open(p); w = 84 * mm; h = w * im.size[1] / im.size[0]
        return [RI(str(p), width=w, height=h), Paragraph(cap, CAP)]
    rows = [[img_cell(*pics[0]), img_cell(*pics[1])], [img_cell(*pics[2]), img_cell(*pics[3])], [img_cell(*pics[4]), '']]
    t = RT(rows, colWidths=[88 * mm, 88 * mm]); t.setStyle(RTS([('VALIGN', (0, 0), (-1, -1), 'TOP')]))
    s += [t]
    s += [PageBreak(), P('3 &nbsp; Geometry of the fin and its two contacts', H2),
          fig('mech_side.png', 140, 'Side section. The fin turns about a hinge axis at R25, z0 (an M4 screw through the fin barrel). The latch lug is 46 mm above that axis, the cam follower 24.5 mm above it, so the cam needs only about 6 mm of lift to open the fin 14°. '
              'The tip swings outward and ends at R58.4 at 90°.', 135),
          P('The wind direction matters: the hinge is at the <i>bottom</i> of the fin and the tip opens up into the oncoming air, so airflow pushes the fin open once it has started. '
            'That is presumably why the design uses a latch plus a short cam kick instead of a motor that has to hold the fins open.', B)]
    s += [PageBreak(), P('4 &nbsp; Latch and cam, up close', H2),
          fig('mech_latch.png', 176, 'The finger travels on an arc of radius 24.8 mm: 6 mm at 14°, 28 mm at 65°. The lug cannot follow it because the lug moves on the fin\'s own hinge arc.', 62),
          fig('mech_cam.png', 176, 'Four lobes, four followers. The rotor profile rises from R21 (base) to R28.6 over 36° of rotor travel, with a dwell, so each lobe pushes its fin about 14°.', 66),
          fig('mech_curve.png', 170, 'Measured on the CAD. Left of 14° the latch lets a fin open only about 1° (its free play). The cam first moves a fin at about 26° and reaches about 14° at 55°, then dwells.', 90)]
    s += [P('5 &nbsp; Every part and how it moves', H2),
          table([['Part (CAD name)', 'Qty', 'Motion', 'Range', 'Driven by'],
                 ['R rotor (shaft, hub, 4 cams, 4 crown arms, knob)', 1, 'Rotates about the vertical axis in the top and low bearings', '0 → 65°, counter-clockwise from the nose', 'Servo horn, through the horn socket in the hub'],
                 ['EH SG90 horn, HW horn screw M2', '1 + 1', 'Rotates with the rotor (horn is clamped on the servo spline)', '0 → 65°', 'Servo spline'],
                 ['E SG90 servo body', 1, 'Fixed, hung from two housing posts by its flange. Only the output shaft turns', 'Shaft 0 → 65° commanded', 'Flight computer'],
                 ['L1–L4 catch caps, HW L1–L4 M3×8', '4 + 4', 'Rotate with the rotor; the finger moves on a 24.8 mm radius arc', 'Finger travel 6 mm to unlatch (14°), 28 mm at 65°', 'Rotor'],
                 ['P1–P4 fins', 4, 'Hinge about an axis at R25, z0, tangent to the housing, on an M4 screw', '0 → 90°: about 1° free play when latched, 14° from the cam, the rest from the airflow', 'Cam, then airflow; the latch holds them closed'],
                 ['TP1–TP4 BT80 cut-outs', 4, 'Glued to the fins; swing out through the tube windows with them', '0 → 90°', 'Their fin'],
                 ['HW H1–H4 hinge screws M4×25', 4, 'Fixed in the housing; the fin barrel turns around the shank', 'none', ''],
                 ['C1, C2 housing halves (bearings, hinge ears, stop blocks, strips, servo posts, sleeve pads)', '1 + 1', 'Fixed. The 90° stop is the landing flat on the fin against the stop block', 'none', ''],
                 ['REF upper and lower BT80 tubes', '1 + 1', 'Fixed. The upper tube has four windows for the fins', 'none', ''],
                 ['Seam M3×8, support M3×5, sleeve M3×10, servo flange M2×8', '4 + 8 + 3 + 2', 'Fixed', 'none', '']],
                [52, 12, 56, 38, 26], font=7.4),
          P('In the Onshape assembly (ASM-V3) these motions are the rotor revolute (0 → 65°) and the four hinge revolutes (0 → 90°, hard stop). The mate values could not be driven by script, so drag the rotor and a fin to see them move.', SM)]
    s += [P('6 &nbsp; Who pushes on whom', H2),
          fig('mech_loadpath.png', 160, 'Load path. The servo only supplies torque to the rotor. The fin loads (suction when closed, drag at 90°) end in the housing through the finger-lug contact, the hinge screws and the hard stop.', 120),
          P('<b>What the servo feels.</b> Closed: friction at the finger-lug contact while the wind pulls the fins outward (the dominant load, see the torque check in the V3 guide). During the kick: almost nothing, because the wind helps. '
            'At 90°: nothing, the stop takes the drag. Its own inertia and the rotor\'s are negligible.', B),
          WARN_P('Everything in this document is derived from the CAD geometry and a simple wind model. Latch behaviour, friction and the real wind load have not been tested on a print or in flight.')]
    build_pdf(DOCS / 'V3_mechanics_diagrams.pdf', 'V3 mechanics diagrams - ARC BT80 airbrake', s)


def history():
    from reportlab.platypus import Table as RT, TableStyle as RTS, Image as RI
    def side(img, flow, img_w=58):
        p = FIG / img; im = PILImage.open(p); w = img_w * mm; h = w * im.size[1] / im.size[0]
        if h > 120 * mm: h = 120 * mm; w = h * im.size[0] / im.size[1]
        t = RT([[RI(str(p), width=w, height=h), flow]], colWidths=[(img_w + 2) * mm, (176 - img_w - 2) * mm])
        t.setStyle(RTS([('VALIGN', (0, 0), (-1, -1), 'TOP'), ('LEFTPADDING', (0, 0), (-1, -1), 2), ('RIGHTPADDING', (0, 0), (-1, -1), 2)]))
        return t
    def bl(items): return [Paragraph(i, BUL, bulletText='•') for i in items]
    s = []
    s += [P('Design history: every iteration and why we switched', H1),
          P('From your original FeatureScript to the servo-on-top V4 with its electronics bay. Numbers are measured on the CAD models (printed mass = solid PLA at 1.24 g/cm³; the original and the first V2 were measured from their saved models and STL exports).', B),
          fig('hist_timeline.png', 150, 'The path: seven steps, each triggered by a request or a finding.', 225)]
    s += [PageBreak(), P('1 &nbsp; Side by side', H2),
          fig('hist_scale.png', 150, 'To scale. The fins never moved (z 4..54). What changed is what sits above and below them.', 140),
          fig('hist_metrics.png', 176, 'Length, mass and number of printed parts for each iteration.', 60),
          table([['', 'Printed housing', 'Overall length', 'Printed mass', 'Printed parts', 'Drive and latch'],
                 ['Original', '118 mm', '178.5 mm', '177 g', '33 bodies (glued pins, caps)', 'wound spring + SG90 trigger; tab-and-hook latch on the rotor'],
                 ['V1 screwed', '118 mm', '178.5 mm', '180 g', '19 types', 'same'],
                 ['V2 first (compact head)', '111.4 mm', '171.9 mm', '177 g', '19 types', 'same'],
                 ['V2 22 mm drop', '91.8 mm', '152.3 mm', '169 g', '19 types', 'spring + SG90 trigger; inward lug + finger latch'],
                 ['V3 first (servo below)', '91.8 mm', '105.5 mm incl. servo', '108 g', '5 types', 'SG90 on the rotor; same lug + finger latch'],
                 ['V3 flush (servo inside)', '91.8 mm', '91.8 mm', '106 g', '5 types', 'same; bearing and spokes raised'],
                 ['V4 (servo on top, bay)', '96.3 mm', '105.4 mm (servo top above the housing)', '144 g incl. sled + transition', '7 types', 'servo on top, thick limiter at the bottom']], [32, 24, 26, 20, 30, 44], font=7.6)]
    # --- iteration 0
    s += [PageBreak(), P('2 &nbsp; The original: your FeatureScript', H2),
          side('hist_baseline.png', bl([
              'Source: your “Positive cam kick-out / modular brake” FeatureScript, with your unloaded-spring print references; I rebuilt it in a new Onshape document and matched its size (z −93.5…85) and part count before changing anything.',
              'How it works: a wound spiral spring in a cartridge drives a four-lobe cam rotor; an SG90 pulls a trigger through a pushrod and yoke; a hook on the rotor holds a tab on each fin; the cams kick the fins and the airflow finishes opening them.',
              'Fastening: glue. Hinge pins H and caps K, the catch caps, the housing seam, the glue sleeves, the lid.',
              '<b>178.5 mm overall, 177 g, 33 printed bodies.</b>',
              '<b>Why we moved on:</b> you asked for screw holes in place of the bonds, and an assembly document.']))]
    # --- iteration 1
    s += [Spacer(1, 8), P('3 &nbsp; V1: the same machine, screwed together', H2),
          side('v1_assembled.png', bl([
              'Seam: 4 × M3×8 socket-head screws across the housing seam on inward ribs at z = 8 and z = 44. Hinges: M4×25 screw per fin instead of pin and cap. Catch caps: open-top clip with an M3×8 into the rotor arm. Sleeves, dock ring, cradle and lid: M3×6 and M3×10 radial or vertical screws.',
              'Stayed bonded: the thrust collar, servo keeper and return-leaf root (under 3 mm of material, a screw would be weaker than the glue).',
              'Checked: no overlaps, straight hex-key access to the seam screws with the fins open.',
              '<b>178.5 mm overall, 180 g, 26 screws, 56 bodies incl. hardware.</b>',
              'Found and fixed on the way: a casing boss that made a non-manifold boolean; lid ears that hit the pushrod (moved to 145/215/335°); seam screws at z = 6 blocked by hinge-ear tops (moved to z = 8).',
              '<b>Why we moved on:</b> you wanted a shorter airbrake: fins higher, a smaller head (fin thickness adds to the diameter), thick supports, screw holes.']), 52)]
    # --- iteration 2
    s += [PageBreak(), P('4 &nbsp; V2 first: compact head inside the upper BT80 tube', H2),
          side('hist_v2first.png', bl([
              'Your first brief asked for 4 supports between the fins and 4 under them. You then proposed something simpler and better: cut slits in the upper BT80 tube, glue each cut-out to its fin so it rides with the fin, keep supports only in the solid strips between the slits, and keep the sleeve fit at the bottom.',
              'Fin shell R29.9–32.3 (64.6 mm OD), 0.2 mm glue gap, then the 0.52 mm BT80 wall: back to 66.04 mm flush. The upper sleeve is gone; 8 supports (4 strips, 4 stop blocks) take 8 × M3 into the tube.',
              'Cam peak 29 → 28.6 mm for pillar clearance. Tube windows 38.6 mm wide; cut-outs start at z = 8 so they clear the stop block at 90°; tube holes centred on the strips (offset ones left only 1.3 mm of web).',
              '<b>Exposed airbrake 82 → 4 mm. Housing 111.4 mm, overall 171.9 mm, 177 g.</b>',
              '<b>Why we moved on:</b> your white-outline drawing on a screenshot: the fins should sit up at the rim of the head, so everything under the fin moves up and the whole piece is shorter than V1.']), 58),
          Spacer(1, 6),
          fig('hist_compare_v1_v2first.png', 150, 'V1 (left) and the first V2 (right), as built at the time.', 80)]
    # --- iteration 3
    s += [PageBreak(), P('5 &nbsp; V2 at 22 mm: the latch stack moves up into the fin height', H2),
          fig('hist_dz_preview.png', 176, 'The preview I made so you could choose: the real V2 with the top trimmed by 0, 14 and 22 mm. You chose 22 mm. (The mm figures in the picture were the estimate; the final build is 152.3 mm overall.)', 95),
          side('v2_assembled.png', bl([
              'Problem: the V1 hook swings sideways through the fin’s own window, so it cannot fit inside the fin height. New latch: each fin carries a lug that reaches inward (plate + wall), and the catch cap on the rotor arm carries a finger just outside that wall. Measured on the CAD: held from 2° of opening, released by 16° of rotor travel, before the cams touch at about 26°.',
              'Everything below the fin (rotor stack, bearings, knob, caps) moved up 22 mm. Fin top z 54, head top z 58.8 (4.8 mm).',
              '<b>91.8 mm housing, 152.3 mm overall, 169 g.</b>',
              'Corrections after the first 22 mm build: the window was 60.4 mm tall and the top ring overlapped the fin top by 231 mm³ (window now 63.8 mm, ring raised: 89.4 → 91.8 mm); a 0.1 mm skin in the catch-cap socket; and, found later, the reference tube still had a 60.2 mm window, which the fin tip would have hit (now 63.8 mm; swept 0.5–90°, clear).',
              '<b>Why we moved on:</b> an experienced person you talked to: make it a direct motor drive and drop the layers; shorter and lighter.']), 50)]
    # --- iteration 4 and 5
    s += [PageBreak(), P('6 &nbsp; V3 first: the SG90 drives the rotor directly', H2),
          P('Removed: spring cartridge, trigger, pushrod, yoke, dock, casing, lid, hub, collar, pin, cradle, keeper, horn saddle (about 64 g printed), plus the spring and return leaf. '
            'Added: a horn socket in the rotor underside, two posts that hold the SG90 by its flange, three pads for the lower tube. Latch, cams, fins and tube slits are the V2 ones, so the same checks apply.', B)]
    s += bl(['Torque (SG90): the load that matters is friction at the latch while the wind pulls the closed fins outward; roughly fine up to 77–109 m/s in a pessimistic case, 134–188 m/s in the typical one.',
             'Deploy once and stay out: the 90° hard stop is in the fin geometry; the cam only holds the fins at about 14°, the airflow does the rest.',
             '<b>105.5 mm overall, 108 g, 5 printed part types.</b> The servo hung about 13.7 mm below the bottom of the housing.',
             '<b>Why we moved on:</b> you asked for the servo to be moved up so it sits flush with the bottom and does not stick out, while still working.'])
    s += [P('7 &nbsp; V3 flush: the servo inside the housing', H2),
          side('v3_assembled.png', bl([
              'Moving the servo up alone was not possible: the rotor’s lower bearing and its four spokes sat exactly where the servo has to go (z −15…−6).',
              'So the lower bearing (now 3 mm, z −0.8…2.2), the thrust collar and the spokes moved <b>up</b> above the horn, the rotor now ends at z −8.7, the horn pocket sits at z −8.5…−6.7, and the servo posts hang from the raised spokes. The servo’s bottom is exactly at the housing bottom (z −33).',
              'A 0.7 mm relief in the base ring clears the servo tab. Latch, cam timing and the fin motion are unchanged (checked again on the new model).',
              'Checked: no printed-part overlaps closed or open; rotor, horn and caps swept 0–65° clear of housing and servo; hex-key access to the seam screws clear; ASM-V3 mates (21) all solve.',
              '<b>91.8 mm overall, 106 g, 5 printed part types</b> (V2: 152.3 mm and 169 g).',
              '<b>Next:</b> measure your own servo and horn, run the ground-impact FEA you asked about, print and test the latch.']), 52),
          Spacer(1, 6),
          fig('compare_length_v3.png', 170, 'V1, V2 and V3 side by side (V3 is the flush layout).', 90)]
    s += [PageBreak(), P('8 &nbsp; V4: servo on top, thicker parts, electronics bay', H2),
          side('v4_assembled.png', bl([
              'You noticed the limiter stops and the green rotor parts were thin, and asked for the servo on top with the limiter moved to the bottom, a screwed bottom joint on the BT80 transition, and a bay for the altimeter, a servo battery and a regulator, keeping the size small.',
              'I drew a sketch first (no CAD) and you picked Option B (a little more length), the Mercury V1 altimeter, and my battery assumption.',
              'Thicker: limiter finger 2 → 6 mm, stops 2 → 7.6 mm, crown arms 3 × 5 → 5 × 8 mm (walls at the screw 0.8 → 2.3 mm), cam web 3 → 5.5 mm.',
              'Bay: sled with the Mercury and a regulator on one layer and the battery on the other; four vertical M3 into a transition ring.',
              'The interference sweep showed the servo ledges were hit by the catch-cap fingers, so the ledges moved above them and the servo now stands 9.1 mm above the housing.',
              '<b>Housing 96.3 mm, 105.4 mm from housing bottom to servo top, printed set 144 g</b> (114 g core + sled + transition ring).']), 52),
          Spacer(1, 6),
          fig('v4_side.png', 120, 'V4 section from the CAD model.', 110)]
    # --- problems and decisions
    s += [PageBreak(), P('9 &nbsp; Problems found along the way and what fixed them', H2),
          table([['Step', 'Problem', 'Fix'],
                 ['Setup', 'Free Onshape plan forces public documents; your own document was read-only', 'New public document (you chose to keep it public)'],
                 ['Setup', 'Direct STL export was blocked by the proxy', 'STLs built from the model’s tessellation; STEP through Onshape’s translation'],
                 ['V1', 'Casing boss tangent to the cylinder gave a non-manifold boolean', 'Boss embedded into the casing (r0 = 22.0)'],
                 ['V1', 'Lid ears hit the pushrod; one boss 0.1 mm too tall', 'Ears at 145/215/335°, boss height 4.0 mm'],
                 ['V1', 'Seam screws at z = 6 blocked by hinge-ear tops', 'Moved to z = 8 (hex-key ray test now clear)'],
                 ['V2 first', 'Tube cut-outs clipped the stop block at 90°; offset tube holes left a 1.3 mm web', 'Cut-outs start at z = 8; holes centred on the strips'],
                 ['V2 22 mm', 'V1 hook cannot fit inside the fin height', 'Inward lug on the fin + finger on the catch cap'],
                 ['V2 22 mm', 'Fin window too short: ring overlapped the fin top by 231 mm³', 'Window 63.8 mm, ring raised (housing 91.8 mm)'],
                 ['V2 22 mm', 'Reference tube window still 60.2 mm; fin tip would hit it while opening', 'Window 63.8 mm; opening sweep 0.5–90° clear'],
                 ['V2 22 mm', 'My angle scan polled Onshape too hard and was blocked for about 20 h', 'Waited; later checks done offline on the meshes (no API calls)'],
                 ['V3 flush', 'Servo cannot just move up: rotor bearing and spokes were in the way; tab 0.5 mm into the base ring', 'Bearing, collar and spokes raised above the horn; 0.7 mm ring relief'],
                 ['V4', 'Catch-cap fingers hit the servo flange ledges between 30° and 60° of rotor travel (63 mm³)', 'Ledges raised above the fingers; servo stands 9.1 mm above the housing'],
                 ['V4', 'Limiter finger only touched the shaft (stayed a separate body); seam pegs floated after the base ring was opened; sled overlapped the hinge ears', 'Finger overlapped into the shaft, pegs moved to R28.5, sled ribs trimmed to the lower bay'],
                 ['All', 'Assembly mate values cannot be driven from a script', 'Not verified by script; drag the rotor and a fin in ASM-V3 / ASM-V4']], [20, 90, 66], font=7.6),
          P('10 &nbsp; Who decided what', H2),
          table([['Decision', 'By'],
                 ['Screws instead of glue, M3 self-tapping, M4 for the hinge, public Onshape document', 'You'],
                 ['Shorter airbrake with the fins higher and a smaller head', 'You'],
                 ['Slit the upper tube and glue the cut-outs to the fins; supports only in the strips; sleeve fit at the bottom', 'You (replaced my first 8-support plan)'],
                 ['Fin top at the rim of the head; 22 mm drop rather than 14 mm', 'You'],
                 ['New lug-and-finger latch, 63.8 mm window, 4.2 mm top ring', 'Me (needed to make your layout work)'],
                 ['Direct SG90 drive, deploy once, 90° mechanical stop, FEA later', 'You (from the expert’s advice)'],
                 ['Servo flush with the housing bottom, not sticking out', 'You'],
                 ['Servo on top, limiter to the bottom, thicker parts, screwed transition, electronics bay, Option B, Mercury V1', 'You'],
                 ['Servo posts and pads, horn pocket, cam peak 28.6 mm, small joints left bonded', 'Me; please check the servo and horn dimensions'],
                 ['Moving the lower bearing and spokes up to make the flush servo fit', 'Me'],
                 ['Raising the servo ledges above the finger sweep; sled, transition ring, regulator placeholder', 'Me'],
                 ['Battery strap channels in the sled and notches in the transition ring', 'You asked; me'],
                 ['Battery pocket resized for the Spektrum 300 mAh 2S (42 × 19 × 12 mm)', 'You asked; me']], [130, 46], font=7.8),
          WARN_P('Mass is solid PLA; the slicer’s infill will lower the real weights. The latch, horn pocket and servo mount have not been tested on a print.')]
    build_pdf(DOCS / 'Design_history.pdf', 'Design history - ARC BT80 airbrake', s)


def sketch_v4():
    s = []
    s += [P('V4 concept sketch: servo on top, thicker parts, electronics bay', H1),
          WARN_P('<b>This is a sketch for you to inspect, not a CAD model.</b> Nothing in Onshape has changed. Dimensions are to scale where they come from the current V3 model; the new parts are placeholders. Please read the questions on the last page before I start the CAD.'),
          P('1 &nbsp; How I read your request', H2)]
    s += bullets([
        '<b>Thin parts:</b> the knob finger and the two knob stops that limit the rotor (about 2 mm wide), and the green rotor: the crown arms (3 mm thick, only 0.8 mm of material beside the screw hole) and the cam web (3 mm). All get thicker.',
        '<b>Flip:</b> the servo goes on <b>top</b> of the airbrake (output shaft pointing down). The rotation limiter (finger + stops) therefore moves to the <b>bottom</b> of the rotor, flipped.',
        '<b>Bottom end:</b> the module screws onto the top of the transition on the BT80 side, with vertical screws.',
        '<b>New bay</b> at the bottom for the altimeter, a small battery for the servo, and a regulator giving the servo the right voltage and current.',
        '<b>Same size:</b> 91.8 mm tall, 66 mm OD (the dashed box). Fins, cams, latch and tube slits stay as they are.'])
    s += [fig('v4_sketch_elevation.png', 138, 'Side sections to scale. Left: V3 now. Right: V4 proposal.', 98),
          table([['#', 'V3 now (left)', '#', 'V4 proposal (right)'],
                 ['1', 'knob finger and stops: about 2 mm wide', '1', 'SG90 flipped on top, its top flush with the housing top (z 58.8), shaft pointing down'],
                 ['2', 'crown arms: 3 mm thick, 0.8 mm walls at the screw', '2', 'ledges from the support strips carry the servo flange (M2 screws)'],
                 ['3', 'SG90 at the bottom, flush with the housing bottom', '3', 'crown arms 5 mm thick with a 10 mm boss round the screw, now just below the servo'],
                 ['', '', '4', 'cam web 6 mm thick (the fin follower is 9 mm tall)'],
                 ['', '', '5', 'lower bearing (3 mm) with a collar above it: the rotor now hangs from the servo horn, the collar stops it dropping'],
                 ['', '', '6', 'limiter moved to the bottom, flipped and thick: finger 6 mm, stops 8 mm, full-height webs'],
                 ['', '', '7', 'bay ceiling and two electronics layers (altimeter above, battery + regulator below); base ring opened to R26'],
                 ['', '', '8', 'bottom flange, 4 M3 up through the transition on the BT80 side']], [8, 62, 8, 98], font=7.4)]
    s += [PageBreak(), P('2 &nbsp; The thicker parts', H2),
          fig('v4_sketch_thicken.png', 160, 'Plan views. The 65° travel is kept: the finger touches one stop at rest and the other at the end of travel.', 100),
          P('3 &nbsp; The electronics bay', H2),
          fig('v4_sketch_bay.png', 160, 'Plan views from below. All sizes are placeholders for typical parts.', 64),
          PageBreak(), P('4 &nbsp; The screwed transition', H2),
          fig('v4_sketch_transition.png', 160, 'The module bottom face with four vertical M3 bosses, and the stack.', 66)]
    s += [P('5 &nbsp; Two options for the bay height', H2),
          table([['', 'Option A: keep 91.8 mm (my default)', 'Option B: allow a little more'],
                 ['Bay height', 'z −33 to −9 = 24 mm, base ring opened to R26', 'about 24 mm + whatever your parts need, in 1 mm steps'],
                 ['Fits', 'typical parts need about 25 mm (battery 10 + altimeter 12 + trays 3): <b>borderline</b>', 'comfortable'],
                 ['Overall', '91.8 mm × 66 mm, unchanged', 'about 92–96 mm × 66 mm'],
                 ['Depends on', 'your real altimeter and battery sizes', 'same']], [28, 76, 72], font=7.8),
          P('6 &nbsp; Power for the servo (suggestion)', H2)]
    s += bullets([
        'SG90 (4.8–6 V): about 0.1–0.25 A moving, about 0.7 A at stall. A 5 V regulator rated 3 A (a small step-down “UBEC” module) gives about four times the stall current.',
        'Battery: a 2S LiPo (7.4 V, roughly 300–450 mAh) feeding that regulator is the usual choice; a 1S cell would need a boost converter. A capacitor (about 470–1000 µF) at the servo supply and a power switch or arming jumper reachable through the transition are cheap additions.',
        'At 5 V the SG90 stall torque is 0.176 N·m (0.216 N·m at 6 V); the torque check in the V3 guide assumed 5 V.',
        'Most altimeters have no servo output. If yours does not, a small microcontroller board has to sit between the altimeter and the servo: it takes bay space too (about 20 × 10 mm).'])
    s += [P('7 &nbsp; Risks I can already see', H2)]
    s += bullets([
        'With the servo flipped, the rotor <b>hangs from the horn</b> and the top bearing is gone; the lower bearing, the collar and the limiter have to keep it in place and centred. I will check this in CAD.',
        'The catch caps move down about 6 mm at the arm end and become taller clips; their screw boss has to move inboard to clear the fin follower. The latch and cam timing must be re-measured afterwards.',
        'The servo cable exits at the top of the case and has to run down a channel inside the support strip to the bay.',
        'The bay is only about 1.4 mm of wall away from the outer skin all round; very little room for anything I have not listed.'])
    s += [P('8 &nbsp; Questions before I build it', H2)]
    s += bullets([
        '<b>Which parts are “the part at the top that restricts rotation”?</b> I assumed the knob finger and the two stops. If you meant something else, say so.',
        '<b>What is “the transition on the BT80 side”?</b> A printed coupler ring that you already have (dimensions?), or something I should design? I assumed a flat ring with four M3 holes, bonded in the BT80 tube, with the module screwed down onto it.',
        '<b>Which altimeter</b> (make, size) and <b>how should it command the servo</b>? Does it need its own small battery?',
        '<b>Which battery</b> (type, mAh, size)? If it is bigger than 40 × 18 × 10 mm, Option B is probably needed.',
        '<b>Is the servo end (top) the nose side?</b> I assumed yes.',
        '<b>Option A or B</b> for the bay height?'])
    s += [P('If you do not answer, I will use the assumptions above, Option A, and typical part sizes, and tell you exactly where they do not fit.', SM)]
    build_pdf(DOCS / 'V4_concept_sketch.pdf', 'V4 concept sketch - ARC BT80 airbrake', s)


def v4():
    s = []
    s += [P('V4 – servo on top, thicker parts, electronics bay: assembly guide', H1),
          P('Built from the sketch you reviewed, with Option B (a little more length), the Mercury V1 altimeter, and my assumptions for the battery and regulator. '
            'The fins, cams, hinge, tube slits and rotor-mounted latch are the V3 ones; what changed is below.', B),
          P(f'Onshape: <a href="{DOC_URL}" color="blue">ARC BT80 Airbrake - V1 Screwed + V2 Compact (Claude build)</a>. Elements: <b>V4-A</b> closed, <b>V4-B</b> fully open, <b>ASM-V4</b> assembly. '
            'Feature Studio: module mode <i>4</i> with <i>V2 compact head</i> on.', SM),
          WARN_P('<b>Where it differs from the sketch:</b> (1) the servo top is <b>9.1 mm above the housing</b>, not flush: the catch-cap fingers sweep under the servo’s flange ledges, so the ledges had to move above them, which lifts the servo; it sits in the upper BT80 tube. '
                 '(2) The crown arm is 8 mm wide and 5 mm thick with no separate boss (walls beside the screw 2.3 mm, not 3.3). (3) Limiter stops are 7.6 mm wide, the cam web 5.5 mm. '
                 '(4) The housing is 96.3 mm (Option B: +2.5 mm over V3, plus 2.0 mm of wiring headroom), and 105.4 mm from the housing bottom to the top of the servo.'),
          fig('v4_assembled.png', 55, 'V4 closed. The upper tube, with the servo showing through its window zone, covers the head as before.', 112),
          P('1 &nbsp; The numbers', H2),
          table([['', 'V3 flush', 'V4'],
                 ['Printed housing', '91.8 mm', '96.3 mm (z −37.5 … 58.8)'],
                 ['Housing bottom to servo top', '91.8 mm (servo inside)', '105.4 mm (servo top 9.1 mm above the housing)'],
                 ['Printed set, solid PLA', '106 g', '<b>144 g</b>: 114 g core + 16 g sled + 15 g transition ring'],
                 ['Printed part types', '5', '7 (adds the electronics sled and the transition ring)'],
                 ['Servo', 'inside, shaft up, bottom flush', 'on top, flipped, shaft down'],
                 ['Rotation limiter', 'top: finger and stops about 2 mm wide', 'bottom: finger 6 mm, stops 7.6 mm'],
                 ['Crown arms', '5 × 3 mm, 0.8 mm walls at the screw', '8 × 5 mm, 2.3 mm walls (cap body 14 mm wide)'],
                 ['Cam web', '3 mm', '5.5 mm'],
                 ['Electronics', 'none', 'Mercury V1 + 2S LiPo + 5 V regulator in the bay'],
                 ['Tube joint at the bottom', '3 radial M3 into sleeve pads', '4 vertical M3×10 into the transition ring']], [52, 52, 72], font=7.8),
          fig('v4_side.png', 138, 'Side section from the CAD model, to scale.', 128)]
    s += [PageBreak(), P('2 &nbsp; What you asked for, and what I did', H2)]
    s += bullets([
        '<b>Thicker limiter and rotor parts.</b> Limiter finger 2 → 6 mm wide and 5.2 mm tall; stops 2 → 7.6 mm, 9.8 mm tall, hung from the lower spokes; arms 3 → 5 mm thick and 5 → 8 mm wide; cam web 3 → 5.5 mm. The catch caps got a 14 mm wide body to carry the wider arm.',
        '<b>Flipped.</b> The servo is on top with the shaft down into a pocket on the rotor hub; the limiter moved to the bottom of the rotor. The old top bearing is gone: the rotor is held by the servo horn and the lower bearing, with a collar above the bearing and the limiter finger below it.',
        '<b>Bottom end.</b> Four bosses on the housing take M3×10 screws that go down into the transition ring (heads in counterbores, reached from inside the bay with the sled out).',
        '<b>Bay.</b> A ceiling at z −10 closes the mechanism; below it a skeletal sled holds the Mercury and regulator in the upper layer and the battery in the lower layer, clamped between the ceiling and the transition.'])
    s += [fig('v4_thicker.png', 150, 'Before and after, sections taken from the V3 and V4 models.', 120),
          PageBreak(), P('3 &nbsp; The electronics bay', H2),
          fig('v4_bay.png', 172, 'Plan sections of the V4 model. Mercury V1 is the real size (30 × 16.9 × 10.8 mm); the battery is the Spektrum 300 mAh 2S as listed (42 × 19 × 12 mm); the regulator is a placeholder.', 72),
          table([['Part', 'Size', 'Source'],
                 ['Mercury V1 altimeter', '30 × 16.9 × 10.8 mm, 7.2 g in case, onboard 50 mAh battery, USB-C, Wi-Fi, 2 direct servo outputs', 'Altimeter Cloud specification you sent'],
                 ['Servo battery', 'Spektrum 300 mAh 2S LiPo, 7.4 V, 42 × 19 × 12 mm, about 17 g; pocket 42.8 × 19.8 × 12.4 mm', 'retailer listings (measure your pack)'],
                 ['Regulator', '5 V, 3 A step-down module, about 25 × 15 × 8 mm (placeholder)', 'my assumption']], [38, 96, 42], font=7.6),
          fig('v4_wiring.png', 150, 'Power and signal. The Mercury has its own battery and drives the servo through a direct servo output; the servo is powered separately.', 80)]
    s += [PageBreak(), P('4 &nbsp; Why the servo stands 9.1 mm above the housing', H2),
          P('The four catch-cap fingers sweep 65° around the axis and pass under every azimuth, so a servo ledge that sits below the fingers is hit between 30° and 60° of rotor travel (found in the interference sweep, 63 mm³ at 45°). '
            'Raising the ledges above the fingers fixes that for good, and lifts the servo 6 mm; then I brought the housing top back down to 58.8 mm because it no longer needs to enclose the servo. '
            'Alternatives, if you do not want the servo above the ring: lower the whole latch (needs a redesign of the fin lug), or hold the servo by a yoke at its top end (adds a lid and moves the support above the nose-side ring).', B),
          P('5 &nbsp; Hardware', H2),
          table([['Ref in CAD', 'Fastener', 'Qty', 'Joint', 'Driver'],
                 ['HW seam screw 1-4', 'M3 × 8 socket-head cap', 4, 'Seam, z = 8 and z = 44', '2.5 mm hex'],
                 ['HW L1-L4 cap screw', 'M3 × 10 button head', 4, 'Rotor arm → catch cap boss', '2.0 mm hex'],
                 ['HW H1-H4 hinge screw', 'M4 × 25 button head', 4, 'Fin hinge', '2.5 mm hex'],
                 ['HW top-tube support screw 1-8', 'M3 × 5 button head', 8, 'Upper BT80 tube → strips', '2.0 mm hex'],
                 ['HW servo flange screw 1-2', 'M2 × 6 button head, self-tapping', 2, 'Servo tabs → ledges (from above)', '1.5 mm hex or PH0'],
                 ['HW horn screw', 'M2 × 6 (supplied with the servo)', 1, 'Horn → spline, from below through the rotor bore', 'PH0 / 1.5 mm hex'],
                 ['HW transition screw 1-4', 'M3 × 12 button head', 4, 'Module bosses → transition ring (from the bay side)', '2.0 mm hex']], [40, 42, 9, 60, 25], font=7.6),
          P('<b>Totals:</b> 27 screws: M3×5 × 8, M3×8 × 4, M3×10 × 8 (4 cap + 4 transition), M4×25 × 4, M2×6 × 3.', B),
          P('Print list (STLs in <font face="Courier">onshape/exports/v4/print</font>): housing halves C1 and C2, fin ×4, catch cap ×4, rotor, <b>electronics sled</b>, <b>transition ring</b>. The sled and the transition ring are new; the transition ring is yours to bond into the lower BT80 tube.', B),
          fig('v4_overview_exploded.png', 92, 'Exploded V4. Top to bottom: upper tube, servo with horn, housing with rotor and fins, electronics sled with its parts, transition ring, lower tube.', 170)]
    s += [P('<b>Print orientation</b> (the STLs are exported in these orientations; from the design review): <b>rotor</b> hub end down (the end with the horn pocket on the bed, 170 mm² of contact), 5 mm brim, supports under the crown arms, cam web and limiter finger; <b>fins</b> lying on their flat side (337 mm² contact) with supports under the latch lug and hinge ear; <b>housing halves</b> upright, with supports under two interior levels (the bay ceiling half-disc and the bearing spokes; supports touching everywhere, open seam face for removal); <b>catch caps</b> upright; <b>sled</b> and <b>transition ring</b> flat on their wide face.', B)]
    s += [PageBreak(), P('6 &nbsp; Assembly sequence', H2)]
    s += bullets([
        'Hinge screws, catch caps (M3×10 into the arm bosses), rotor into one housing half, fins, second half, four seam screws, as in V3.',
        'Set the servo to its 0° position, press the horn on so that its arm lies in the slot at 45° to the crown arms, and lower the servo with its horn into the pocket on the rotor hub from above.',
        'Screw the servo tabs to the two ledges with the M2×6 screws from above. Put the horn screw in from below through the rotor bore and the ceiling hole (R3 bore, small driver).',
        'Fill the sled: Mercury and regulator in the top pockets, battery in the bottom pocket and strap it in (see below); run the servo cable down the outer groove, through the side hole into the bay and along the wire trough (see the wiring layout document); slide the sled up into the bay.',
        'Bond the transition ring into the lower BT80 tube, set the module on it, and fit the four M3×10 screws down through the bosses from inside the bay (before the sled goes in, or with the sled out).',
        'Glue the tube cut-outs to the fins and slide the upper tube on with its eight M3×5 screws, as in V2 and V3. The top of the servo sits inside this tube.'])
    s += [P('Changes from the design review', H2)]
    s += bullets([
        'Bearing spokes widened from 5 to 7 mm with a 9 mm flared root block (the first review used a scanned width of 3.7 mm; the CAD width was 5 mm; with 5 mm the screening gave 4.4 N to break one spoke, with the new spokes about 11 N).',
        'Limiter stop 1 shortened to R10..12.8 so the seam plane no longer leaves a 0.85 mm wedge on its face; the finger still engages at −3° and 67° (rotor sweep unchanged: clear from −1.5° to 66.5°).',
        'Eight tiny enclosed voids under the bay ceiling filled (the review had called them sliver bodies: they were closed cavities); each housing half is now one solid body.',
        'Catch-cap finger: stepped 1 mm root fillet on its inner face. Servo-ledge pilots O1.8 (were O1.6). Transition screws M3×10 (were M3×12).',
        'Print orientation fixed in the export for the rotor and fins (a bed-contact rule was added to the export script).'])
    s += [P('7 &nbsp; Checks run on this model', H2),
          table([['Check', 'Result'],
                 ['V4-A closed and V4-B open (90°, 65°)', '51 bodies, all watertight; no printed-part overlap; the only overlaps are the servo spline inside the horn and the reference tube touching the housing (as in V2/V3)'],
                 ['Rotor sweep −1.5° … 66.5°', 'clear of both housing halves, the servo, the sled and the transition ring at every step'],
                 ['Limiter', 'engages at −3° and 67°: the 0–65° travel has about 1.5° of margin at each end'],
                 ['Latch and cam', 'latch holds from about 1.5° of fin opening and frees by 15° of rotor travel; cams first touch at about 26° (same as V3)'],
                 ['Fin + cut-out swept 0.5 … 90°', 'clear of the upper tube and the housing'],
                 ['Seam screws, servo screws, horn screw, transition screws', 'a hex key reaches all of them (servo screws from above, horn screw through the bore, transition screws from inside the bay)'],
                 ['V1, V2, V3 rebuilt', 'volumes identical to before: nothing in them changed'],
                 ['ASM-V4 mates', '21 features: fin groups, four hinges, rotor revolute: all solve']], [62, 114], font=7.6),
          WARN_P('<b>Not verified, and what I need from you:</b> (1) your servo and horn dimensions (the ledge pilots and the horn pocket must match). (2) The Mercury’s servo output: which pad, and whether its 3.3 V signal level drives the SG90 (check the manual). '
                 '(3) The regulator size is a placeholder, and the battery pocket is sized for the Spektrum 300 mAh 2S as listed (42 × 19 × 12 mm): measure your pack before printing the sled, and hold it in with a strap or tape (the pocket is open at the bottom). (4) <b>Pressure:</b> the Mercury reads static pressure, so the bay needs vent holes to the outside (not modelled): about three 3 mm holes through the lower tube at the Mercury level. '
                 '(5) The servo cable runs in the outer groove on the 135° strip (the horn closes the rotor bore); the Mercury header position comes from a photo, so confirm it on the board. (6) USB-C access to the Mercury is with the sled out. '
                 '(7) Latch and horn pocket not tested on a print; ground-impact FEA not run (the ledges, limiter stops and the 1.4 mm sled walls are the first places to look).')]
    build_pdf(DOCS / 'V4_assembly_guide.pdf', 'V4 servo-on-top assembly guide - ARC BT80 airbrake', s)


def wiring():
    s = []
    s += [P('V4 power and wiring: battery, regulator and schematic', H1),
          P('The Mercury V1 sends the servo position signal; a small 2S battery and a 5 V regulator power the SG90. '
            'Part sizes below come from the sellers’ listings I could reach; I could <b>not</b> read the Mercury manual (the Altimeter Cloud site is not reachable from this session), so its servo-header pin order and signal voltage are the items to confirm.', B),
          P('1 &nbsp; Recommended parts', H2),
          table([['Part', 'Recommendation', 'Size / weight (from listings)', 'Why'],
                 ['Battery', '<b>Spektrum 300 mAh 2S, 30C</b> (7.4 V nominal, 8.4 V full, PH plug)', '42 × 19 × 12 mm, about 17 g (one retailer’s listing; measure yours)', 'Small 2S pack that fits the V4 pocket; 6.0–8.4 V in, which the regulator below accepts; 300 mAh is far more than a flight needs (about 7–12 flights per charge on my estimate)'],
                 ['', 'Alternatives: Tattu 300 mAh 2S HV; EMAX Tinyhawk S 2S', '47 × 17 × 13 mm; 42 × 16.2 × 12.7 mm (listings)', 'The Tattu is 4.6 mm too long for the new pocket; the EMAX would fit the length and width but is 0.3 mm too tall'],
                 ['Regulator', '<b>Pololu D24V10F5</b>: 5 V, 1 A step-down', '0.5 × 0.7 × 0.14 in (about 13 × 18 × 4 mm), 1 g', 'Input 5.1–36 V; the SG90 takes 4.8–6 V and draws roughly 0.3–0.55 A at stall (sources vary), so 1 A is about 2× headroom'],
                 ['', 'Option for more torque: D24V10F6 (6 V, 1 A)', 'same footprint', 'SG90 torque rises with voltage (one source: 1.2 → 1.6 kg·cm from 4.8 → 6 V; another lists 1.8 kg·cm at 4.8 V), but this board needs at least 6.1 V in: keep the pack above about 6.5 V'],
                 ['Capacitor C1', '470–1000 µF, 10 V, low-ESR electrolytic', 'about 6.3 mm diameter × 11 mm', 'Absorbs the servo’s current spikes so the regulator and the Mercury do not brown out'],
                 ['Arming', 'SPST switch ≥ 1 A, or a JST pull-pin / jumper', 'small slide switch', 'Keeps the servo dead while you handle it; reach it through the transition ring'],
                 ['Fuse (optional)', '1.1 A resettable (polyfuse)', '—', 'Limits a short; the LiPo can deliver far more than the wires should carry'],
                 ['Wire and plugs', '24 AWG silicone for power, 28 AWG for the signal; JST-PH 2-pin on the battery (match the plug on the pack you buy)', '—', 'Flexible, heat-tolerant, small']], [24, 52, 44, 56], font=7.4),
          P('Estimated load: the servo idles near 10 mA and draws about 100–250 mA while moving; one deployment is under a second. A 300 mAh pack therefore lasts many hours of standby (estimate: the regulator’s own draw I could not confirm).', SM),
          PageBreak(), P('2 &nbsp; Wiring schematic', H2),
          fig('v4_wiring_schematic.png', 178, 'Servo power and signal. The Mercury has its own 50 mAh battery and does not power the servo.', 150),
          P('How it is wired', H3)]
    s += bullets([
        '<b>Power path:</b> battery + → fuse → arming switch → regulator VIN; regulator VOUT (+5 V) → servo red wire and C1; regulator GND, C1 and the servo brown wire all return to the battery −.',
        '<b>Signal path:</b> one Mercury servo header (GP6 or GP7, set in the Mercury configuration as the air-brake servo channel) → servo orange wire. The Mercury GND goes to the same ground rail.',
        '<b>The one rule:</b> the servo’s red wire takes power from the regulator only. If the Mercury servo header has a power pin, leave it unconnected (pull the red wire out of the Mercury-side connector shell, or use a servo lead with the red wire cut on that side). Two supplies tied together can damage the Mercury or the regulator.',
        '<b>Order of assembly:</b> bench-test with the servo and a 5 V supply first, then the regulator on the battery, with the switch off until the last step.'])
    s += [PageBreak(), P('3 &nbsp; What I could not verify, and what it means for the CAD', H2),
          WARN_P('<b>The V4 battery pocket is now sized for the Spektrum 300 mAh 2S.</b> Pocket 42.8 × 19.8 × 12.4 mm (0.4 mm clear per side, 0.2 mm above and below the 42 × 19 × 12 mm pack); the sled’s lower block grew from 44.8 × 22.8 to 46.8 × 23.8 mm with its corners trimmed to R25.5 so they clear the opened base ring. The floor between the two layers is 1.8 mm thick. (Later the whole battery layer moved down 2.0 mm for wiring headroom: housing 96.3 mm.) '
                 '<b>Battery strap.</b> The pocket is open at the bottom, so a belly band holds the pack: a nylon tie or narrow hook-and-loop strap (up to 4 mm wide, 1.5 mm thick, about 90 mm long) runs under the pack, up the outside of the lower sled block and across a 1 mm groove in its top. Two channels are modelled, at x = ±17.0…21.4 mm (between the upper block and the end wall); use one or both. The small ribs are notched there, and the transition ring has two notches (6.3 mm × 29 mm, 1.8 mm deep) so the band has room under the sled. I checked a 3.4 mm band in the model: it does not touch the sled, the transition ring or the housing. ''Still to do on your side: <b>measure the real pack</b> (the 42 × 19 × 12 mm figure is one retailer’s listing) and allow for the plug and the 3-pin balance lead (fold them beside or on the pack).')]
    s += bullets([
        '<b>Mercury servo header:</b> the Altimeter Cloud flight page I found says the two onboard servo headers are GP6 and GP7, but I could not read the pin order or the signal voltage. Check its manual (the “Mercury V1 schematic” page). The SG90 usually accepts a 3.3 V signal when powered at 5 V, but test it on the bench before flying.',
        '<b>SG90 figures vary by source:</b> stall current 0.3 to 0.55 A, torque 1.2 to 1.8 kg·cm at 4.8 V depending on the version. The V3/V4 torque check used 0.176 N·m (1.8 kg·cm) at 5 V; measure your own servo.',
        '<b>Regulator input:</b> Pololu warns of voltage spikes above its 36 V maximum with long leads at high input voltages; with a 2S pack (8.4 V full) this is not a concern. The D24V10F5 needs at least 5.1 V in, so stop flying a 2S pack that has sagged near 6 V.',
        '<b>LiPo safety:</b> the Spektrum is a standard LiPo (charge to 4.2 V per cell; an HV pack such as the Tattu needs a 4.35 V setting); do not discharge below about 3.3 V per cell; keep the pack away from the ejection-charge heat and from crushing; use a fire-safe bag for charging.',
        '<b>Altimeter pressure:</b> the Mercury reads static pressure, so the bay needs vent holes to the outside (not modelled in the CAD).'])
    s += [P('Sources', H2)]
    s += bullets([
        '<a href="https://www.altimetercloud.com/flights/1560/" color="blue">Altimeter Cloud flight page (GP6/GP7 servo headers, air-brake channel)</a> and the <a href="https://www.altimetercloud.com/support/mercuryv1/schematic/" color="blue">Mercury V1 schematic page</a> (not readable from this session).',
        '<a href="https://www.pololu.com/product/2831/specs" color="blue">Pololu D24V10F5 5 V, 1 A step-down regulator</a> and <a href="https://www.pololu.com/product/2832" color="blue">D24V10F6 6 V version</a>.',
        'Spektrum 300 mAh 2S listings: <a href="https://www.readymaderc.com/products/details/85690-spektrum-7-4v-300mah-2s-30c-lipo-battery-ph" color="blue">Readymade RC</a>. Other packs considered: Tattu 300 mAh 2S listings: <a href="https://www.getfpv.com/tattu-300mah-hv-7-4v-75c-2s1p-lipo-battery-jst-phr.html" color="blue">GetFPV</a>, <a href="https://alofthobbies.com/products/tattu-2s-hv-300mah-75c-jst-phr" color="blue">Aloft Hobbies</a>, <a href="https://www.gensace.de/tattu-300mah-2s-75c-7-6v-lipo-battery.html" color="blue">Gens Ace</a>; Turnigy nano-tech 2S 300 mAh: <a href="https://botland.com.pl/en/products-withdrawn/1581-turnigy-nano-tech-li-pol-battery-pack-300mah-35c-2s-74v.html" color="blue">Botland</a>.',
        'SG90 figures: <a href="https://bit.nkust.edu.tw/~csshieh/teach/111A/mc/datasheet/SG90.pdf" color="blue">SG90 datasheet copy</a> and <a href="https://protosupplies.com/product/servo-motor-micro-sg90/" color="blue">ProtoSupplies</a>.'])
    build_pdf(DOCS / 'V4_power_and_wiring.pdf', 'V4 power and wiring - ARC BT80 airbrake', s)


def wiring_plan():
    s = []
    s += [P('V4 wiring layout (applied to the CAD)', H1),
          P('Where each wire runs inside and around the rebuilt V4 model, drawn on sections of the CAD. The Mercury V1 photo you sent gave the header pad order, and the wire paths below are now cut into the model. '
            'The electrical schematic is unchanged (see the power and wiring document).', B),
          WARN_P('<b>What the check found, and what was done:</b> the horn closes the top of the rotor bore, so the servo cable cannot go down the hollow rotor. The cable now runs in an <b>outer groove</b> on the 135° strip and through a hole into the bay. '
                 'To give the Mercury’s soldered wires headroom the bay was made <b>2.0 mm longer</b> (housing 96.3 mm). <b>Pad positions are estimated from a photo</b> (6 pads at about 2.54 mm pitch, GND at x −3.5 mm with the button end at −x): check them on the real board before printing.'),
          P('1 &nbsp; Mercury header and harness', H2),
          P('From your photo, the pads along the right-hand long edge are, from the button end: <b>GND, GP6, GP7, OUT, IN, 3V</b>. The servo needs only <b>GND</b> and <b>GP6</b> (adjacent pads); the servo’s +5 V comes from the regulator, not from the 3V pad. '
            'The Mercury sits with this edge toward the centre wall of the sled and the button end at −x, so GND and GP6 are the pads closest to the end where the servo cable arrives.', B),
          fig('v4_wiring_schematic.png', 165, 'Reference schematic (battery label now Spektrum 300 mAh 2S).', 110),
          table([['Wire', 'Function', 'From → to', 'Wire', 'Length (est.)'],
                 ['W1', 'Battery + through the arming jumper', 'pack plug → polyfuse → J1 (lower tube) → regulator VIN', '24 AWG red', '60 mm + 110 mm'],
                 ['W2', 'Battery −', 'pack plug → regulator GND (the ground rail)', '24 AWG black', '105 mm'],
                 ['W3', '+5 V', 'regulator VOUT → C1+ → servo red (inside the servo cable)', '24 AWG red', '40 mm + cable'],
                 ['W4', 'Ground rail', 'regulator GND → C1− → Mercury GND pad → servo brown', '24 AWG black', '40 mm + cable'],
                 ['W5', 'Servo cable (3 cores)', 'servo → groove (z 58.8 → −21.5) → hole → bay → trough', 'servo’s own lead', 'about 190 mm'],
                 ['W6', 'Signal', 'Mercury GP6 pad → servo orange', '28 AWG', '25 mm'],
                 ['J1', 'Arming jumper', 'remove-before-flight 2-pin plug in the lower tube, just below the ring wire hole', 'JST-PH or header', '—']],
                [11, 34, 78, 26, 26], font=7.4),
          P('Lengths are read off the drawn routes (±15 mm) without slack: add about 20 mm each. The servo’s own lead is usually 200–250 mm (seller dependent): cut it at the bay end. Cap C1 (470–1000 µF, 6.3 × 11 mm) stands beside the regulator; the pocket is now 13.3 mm deep.', SM),
          PageBreak(), P('2 &nbsp; Layout drawings', H2),
          fig('v4_wiring_plan_views.png', 178, 'Plan sections of the rebuilt model with the routes (orange: servo cable, red: +5 V and battery +, black: battery −, blue: GP6). The trough, lead notch, strap channels and ring notches are cut in the model.', 100),
          fig('v4_wiring_plan_elev.png', 120, 'Elevation through the 126.5° plane. Orange: the servo-cable route (groove and hole). Red dashed with a cross: the rotor bore, which does not work as a cable route.', 205),
          PageBreak(), P('3 &nbsp; What was cut into the V4 model', H2),
          table([['Item', 'Problem', 'Change in the model', 'Touches'],
                 ['Bay 2.0 mm longer', 'Wires soldered to the Mercury’s through-hole pads need 2 mm of headroom; the Mercury top was 0.4 mm below the ceiling.',
                  'Battery layer and everything below moved down 2.0 mm; the Mercury and regulator pockets lowered 2.0 mm (floor between the layers stays 1.8 mm). Housing 94.3 → 96.3 mm (z −37.5 … 58.8), transition ring z −45.5 … −37.5.', 'housing, sled, ring'],
                 ['P1 cable groove + hole', 'Horn blocks the rotor bore; the wall is too thin for a hole; the 0.7 mm gap under the upper tube is too small.',
                  'Outer groove 3.2 wide × 1.6 deep at azimuth 126.5° on the 135° strip, z −21.5 … 58.8; hole 3.2 × 4.5 into the bay at z −21.5 … −17.0. The strips are only 25° wide between the 65° fins, and the 135°/315° strips carry no seam screws. A 3 mm ribbon fits the groove and the hole without touching any part (checked).', 'housing halves'],
                 ['P2 wire trough', 'Pocket tops were 0.2 mm under the ceiling: no way in.',
                  'Trough along the centre wall of the sled, y −0.35 … 2.3, x ±17.5, z −13.4 … −9.8; it joins the Mercury and regulator pockets and is open at both ends. A route from the groove hole round the sled corner to the trough keeps at least 0.8 mm from every part (checked).', 'sled'],
                 ['P3 lead notch', 'Battery leads had 0.4 mm at the pack end.', 'Notch 6 wide × 6 tall in the +x pocket end wall (y ±3, z −37.5 … −31.4), open to the bottom.', 'sled'],
                 ['P5 vents', 'Mercury reads static pressure.', 'Three 3 × 3 mm holes through the lower sleeve at z −18.5 … −15.5, azimuths 0°, 120°, 240°, and three O3 holes in the reference lower tube.', 'housing, tube']],
                [26, 52, 76, 22], font=7.2),
          P('P4 (a riser groove on the sled) is no longer needed: the battery leads come up the open side of the sled to z −14 and round the sled corner into the trough.', SM),
          P('4 &nbsp; Harness assembly order', H2)]
    s += bullets([
        'Bench-test first: servo, regulator and Mercury on a table with a 5 V supply; confirm the servo moves from the Mercury signal alone (power only from the regulator).',
        'Prepare the servo lead: pull the red wire out of the Mercury side and keep it for the +5 V line; solder 28 AWG leads from the brown and orange to the Mercury GND and GP6 pads, from the top, bending them flat toward the centre wall.',
        'Fit the servo to the ledges (M2×6, O1.8 pilots), feed the cable down the outer groove, through the hole, round the sled corner and into the trough.',
        'Fill the sled: regulator and C1 in their pocket, Mercury in its pocket (header edge to the trough), wires in the trough; battery in the bottom pocket with its leads folded out through the notch; strap it (two ties or one hook-and-loop strap).',
        'Run battery + and − down through the ring wire hole to J1 in the lower tube and back up; leave J1 open (disarmed).',
        'Slide the sled up, fit the transition ring, check that no wire is pinched between the sled and the ring (the ring has strap notches), and only then close the jumper.'])
    s += [P('5 &nbsp; Still open', H2)]
    s += bullets([
        'The pad positions come from a photo: confirm the header position and pad pitch on the real Mercury (and its case: it has a loop tab) before printing the sled.',
        'Where the servo cable leaves your SG90 (the drawing assumes the end that is on top) and its length.',
        'The Spektrum pack’s plug type (PH 2.0 listed) and its lead length.',
        'Not printed or tried: groove depth against your wire, and whether the cable bends easily at the sled corner.'])
    build_pdf(DOCS / 'V4_wiring_layout_plan.pdf', 'V4 wiring layout - ARC BT80 airbrake', s)


def modular():
    s = []
    s += [P('Modular airbrake concept: swappable module, reusable electronics head', H1),
          P('A concept for review, in the same spirit as the V4 sketch: <b>nothing is built in CAD yet</b>. Dimensions come from the V4 model; V5 values are concept numbers to be set in CAD once you pick the options at the end.', B),
          WARN_P('<b>Answer:</b> yes. Put the servo, Mercury, regulator and battery in a <b>head</b> on top of the airbrake. The head carries the servo with its horn pointing down, and the horn already drops into the rotor hub slot in V4, so <b>no wire crosses any joint</b> and the groove, hole and trough of the V4 wiring plan disappear. '
                 'The part that breaks (housing, rotor, fins, catch caps, slit skin) becomes the <b>module</b>, a bolt-on consumable that costs about 105 g of PLA; the head and the base ring stay.'),
          P('1 &nbsp; The three groups', H2),
          table([['Group', 'Contains', 'Fate', 'Joint'],
                 ['<b>Head</b> (reusable)', 'servo cup with the two servo ledges, SG90, plate, Mercury V1, regulator + C1, 2S battery, slide switch, USB-C window, vent holes, head sleeve and head tube', 'moves to the next module', 'I1 (to the module), I3 (to the upper airframe)'],
                 ['<b>Module</b> (consumable)', 'housing halves, rotor, 4 fins with their tube cut-outs, 4 catch caps, hinge screws, slit skin tube', 'replaced after a rough flight', 'I1 (top), I2 (bottom)'],
                 ['<b>Base</b> (stays)', 'transition ring bonded in the lower tube (the strap notches and sled features go away)', 'never moves', 'I2']], [30, 85, 32, 35], font=7.6),
          fig('v5_stack_compare.png', 172, 'V4 today and the modular concept at the same scale. Green is the module, blue the head, tan the base.', 118),
          PageBreak(), P('2 &nbsp; Swap procedure and the two interfaces', H2),
          fig('v5_exploded.png', 120, 'Swap: unscrew I1 and lift the head, unscrew I2 and lift the module, drop in the new module, refit both. The horn re-enters the hub slot as the head goes back down.', 175),
          P('<b>I1 head to module</b>, z 58.8: the module skin extends 12 mm above the housing top and the head sleeve slides into it; four radial M3×5 screws, one off-centre dowel (O2.5) so it fits only one way. The head’s servo cup goes down inside the housing top (its two ledges replace the ones that are in the housing now). '
            '<b>I2 module to base</b>, z −22: the same four-screw pattern (or four captive thumb screws) onto the ring that stays bonded in the lower tube. <b>I3 head to upper airframe</b>: the same coupler again, so the head is one section you can lift out.', B),
          PageBreak(), P('3 &nbsp; Interface details', H2),
          fig('v5_interface.png', 178, 'I1 detail: sleeve, screws, key and the horn-in-slot drive (left); plan of the screw circle, key and drive axis (right).', 100),
          P('<b>Drive coupling.</b> The horn stays on the servo in the head; the rotor hub slot (4.4 mm wide, horn arm 3.4 mm) gets a 45° lead-in 1.8 × 1.8 mm. With the rotor parked at its closed stop (−3°) and the servo parked at the same angle, the funnel absorbs about ±8° of error. '
            '<b>Rotor park:</b> add a light detent at the closed position so the rotor does not wander while the head is off. <b>Rotor keeper:</b> V4 holds the rotor with the horn from above; with the head off the rotor can lift out, so add a clip or printed collar on the module. '
            '<b>Drive fuse:</b> make the horn arm a printed dog that breaks before the SG90 gears do (the failing torque is to be tested; an idea, not a verified number).', B),
          PageBreak(), P('4 &nbsp; The head', H2),
          fig('v5_head.png', 178, 'Head, elevation and plan of the electronics layer (concept). The servo is below the plate; battery and Mercury sit side by side in one layer inside O59.8, the regulator beside the Mercury.', 100),
          P('Battery (42 × 19) and Mercury (30 × 16.9) fit side by side inside O59.8 (corner radii 29.0 and 23.7 mm); the 13 × 18 regulator stands at the side of the Mercury, and the layer is 16 mm high. Servo lead (3 cores, ~40 mm) goes to the Mercury GND and GP6 pads and the regulator; the longest wire in the head is the battery lead (~50 mm). '
            'The slide switch (arming) and USB-C window are in the head tube wall, so you can arm and charge without opening anything; three O3 vent holes at the Mercury level. These all sit in the head, so the module never needs an opening for them.', B),
          PageBreak(), P('5 &nbsp; Where the V4 design changes', H2),
          table([['V4 part', 'Change for the modular design', 'Where'],
                 ['Electronics bay and sled (z −37.5 … −10)', '<b>Delete.</b> The sled, strap channels, wire trough, lead notch and the 2 mm of headroom go away; the bay ceiling becomes the module’s bottom plate with the horn-screw hole.', 'housing, sled, ring'],
                 ['Cable groove, hole and vents in the housing wall', '<b>Delete.</b> No cable leaves the head.', 'housing halves'],
                 ['Housing lower shoulder and four bosses (z −37.5 … −31.5)', 'Shorten to a 12 mm bottom sleeve (z −22 … −10) with I2 screw pilots; or a quarter-turn bayonet for tool-free swaps.', 'housing halves'],
                 ['Transition ring', 'Moves up to z −30 … −22, keeps its four pilots; becomes the permanent base. Strap notches and sled seat removed.', 'transition ring'],
                 ['Servo ledges in the housing (z 45.1 … 49.4)', '<b>Move to the head cup.</b> The housing loses its ledges and the two M2 pilots.', 'housing, new cup'],
                 ['Housing top and skin', 'Skin tube extends 12 mm above the housing top as the I1 socket; four M3×5 pilots plus the key hole.', 'housing, skin'],
                 ['Upper tube', 'Splits in two: a slit skin that belongs to the module, and a head tube that belongs to the head.', 'tubes'],
                 ['Rotor', 'Lead-in on the hub slot, closed-position detent, lift-off keeper. Everything else stays (limiter, cam, caps).', 'rotor'],
                 ['Fins, catch caps, hinge screws', 'No change in shape; they are part of the module and swap with it. Optional: make the cut-outs printed so no tube has to be cut each time.', 'fins'],
                 ['Mercury, regulator, battery, servo', 'Move into the head; no change to the parts or the schematic (wire lengths drop to 25–50 mm).', 'head']], [46, 100, 30], font=7.4),
          P('6 &nbsp; Breakage strategy and numbers', H2),
          table([['Item', 'V4', 'Modular concept (estimates from V4 dimensions)'],
                 ['Parts that break and are replaced', 'housing, rotor, fins, caps, tube pieces, sled screwed in with the electronics', 'module only: about 105 g of PLA (housing ~50 g, rotor 17 g, fins 33 g, caps 5 g)'],
                 ['Parts that must survive', 'servo, Mercury, regulator, battery all inside the bay beneath the impact', 'head about 55 g, away from the fin zone, foam-mounted; plus one cheap sacrificial drive dog'],
                 ['Length', '105.4 mm (bay to servo top)', 'module 80.8 mm; head adds 30 mm above the module; overall about 111 mm (+5.6 mm)'],
                 ['Wires crossing a joint', 'servo cable, battery leads, pressure vents', 'none'],
                 ['Swap time', 'not designed for it', 'about 5 minutes with 8 M3 screws; about 1 minute with captive thumb screws or a bayonet (to be tried)']], [44, 62, 70], font=7.6),
          P('7 &nbsp; Risks and choices for you', H2)]
    s += bullets([
        '<b>Overall length</b> grows about 5.6 mm because the electronics sit above the servo. Putting them beside the servo is not possible: the fin latch lugs and catch fingers fill the space around it.',
        '<b>Head hangs over the module.</b> The head’s mass sits 60–90 mm above the module, which is fine for the rocket’s balance but adds a 55 g load on the I1 screws in a rough landing: use four M3 and a foam seat, and test it.',
        '<b>Alignment on assembly.</b> The horn has to find the slot blind. The lead-in and the closed-position detent handle ±8°; a drop of 0.2 mm clearance each side keeps it from binding. Not tested on a print.',
        '<b>Skin tube:</b> keep cutting a real BT80 piece for the module (cheap, strong, but a chore), or print the skin and fin cut-outs (no cutting, more PLA). Your choice.',
        '<b>Swap method:</b> screws at I1/I2/I3 (simple), or thumb screws or a bayonet (faster, more parts and more tolerance).',
        '<b>Other airbrakes:</b> the head fits another brake if that brake offers the same I1: O64.6 sleeve socket, four M3 pilots with the key, the horn slot on the tube axis, closed stop at −3° and 65° of travel. Those numbers are the interface drawing in section 3; write them down before you design the other brake.',
        '<b>Not verified:</b> every V5 number here is a concept dimension from the V4 model, not a CAD result; the Mercury pad position and the SG90 cable exit are still from a photo and standard figures.'])
    build_pdf(DOCS / 'V5_modular_concept.pdf', 'Modular airbrake concept - ARC BT80', s)


def option_skin():
    s = []
    s += [P('Choice 1: the module skin, cut BT80 or printed', H1),
          P('The <b>skin</b> is the outer surface of the swappable module. In V4 it is a real BT80 tube (outside diameter 66.04 mm) with four windows cut in it; each cut-out piece is glued to a fin so the fin closes flush with the tube. For the modular design the module has to be rebuilt after every rough flight, so how the skin is made decides how long a swap takes. '
            'Everything below is a concept drawn from the V4 model; the printed-skin numbers are my calculations, not a CAD result.', B),
          P('1 &nbsp; The two options', H2),
          table([['', 'Option 1: cut BT80 skin (as V4)', 'Option 2: printed skin'],
                 ['What it is', 'A 92.8 mm piece of real BT80 with four windows 37.5 × 42 mm. The four cut-outs are glued to the fins. The skin is screwed to the housing.', 'The housing strips and the fins are printed out to the BT80 outside diameter, R33.02 (0.72 mm more than V4). No tube in the fin zone; the real BT80 above and below butts against it.'],
                 ['What you do per module', 'Cut a tube piece to length, mark and cut four windows (template supplied), cut-outs glued to the fins, wait for the glue, screw the skin on.', 'Print the module. Optionally sand and paint. No cutting, no glue, no cut-outs to line up.'],
                 ['Why it can be better', 'The surface is the real tube, smooth and the right diameter; no extra PLA; the tube is cheap and strong.', 'Repeatable and fast to rebuild; no glue joint between fin and cut-out (that joint is a place a fin can fail); the walls get thicker (strips 3.5 mm, fins 3.1 mm) so the module is stiffer.'],
                 ['Why it can be worse', 'Hand cutting four 65° windows to a sub-millimetre fit takes time and the gap varies; glue needs cure time; every module consumes a tube piece and a gluing session.', 'About +17 g of PLA per module (see the numbers); layer lines need sanding for a smooth finish (drag not measured); the printed OD may be ±0.2 mm, which matters where it butts the real tube.'],
                 ['Works with which fastening', 'Screws only: a 0.52 mm tube wall cannot take a recess or a bayonet slot.', 'Screws, or thumb screws, or a bayonet (see the fastening document).']], [26, 74, 76], font=7.4),
          P('2 &nbsp; The numbers', H2),
          table([['Item', 'Option 1', 'Option 2'],
                 ['Skin outside diameter', '66.04 mm (real tube)', '66.04 mm (printed, same)'],
                 ['Skin length', '92.8 mm (z −22 … 70.8: 12 mm base sleeve, mechanism, 12 mm head socket)', '92.8 mm'],
                 ['Windows / fin interface', 'four 37.5 × 42 mm cut-outs, glued; gaps equal to the saw kerf (assume 1.5° each side)', 'designed gap 0.4 mm all round; the fin carries its own skin'],
                 ['Wall at the fin zone', 'tube 0.52 + fin shell 2.4 (two parts joined by glue)', 'one printed part 3.1 mm (fin), 3.5 mm (strip)'],
                 ['Extra printed mass', '0 g (the tube is a separate purchase: weigh yours)', 'about +17 g per module: π × (33.02² − 32.3²) × 92.8 mm × 1.24 g/cm³ (module about 122 g instead of 105 g)'],
                 ['Hands-on work per module', 'cutting plus gluing plus cure time (not timed: my guess is tens of minutes plus the cure)', 'none beyond optional sanding; print time is unattended'],
                 ['Risk', 'fit of the cut-outs; glue failure', 'printed OD tolerance; surface finish; the first print will need a fit check']], [38, 70, 68], font=7.4),
          PageBreak(), P('3 &nbsp; Drawings', H2),
          fig('opt_skin_sections.png', 172, 'Section at z = 30 through the fin zone. Left: V4 style, real tube strips and glued cut-outs outside the fins and strips. Right: printed skin, fins and strips printed out to the BT80 outside diameter.', 98),
          fig('opt_skin_elev.png', 172, 'Top: the Option 1 skin developed flat (window sizes and spacing). Bottom: the Option 2 module outline with the head and base joints, outside diameter 66.04 mm all the way.', 118),
          PageBreak(), P('4 &nbsp; What I recommend', H2)]
    s += bullets([
        '<b>Go with the printed skin (Option 2) for the module</b>, because the module is the part you will rebuild after every rough flight and cutting and gluing four fin cut-outs each time is the slowest, most variable step. It also lets the swap joints be built into the printed module (next document).',
        '<b>First test:</b> print one fin and a 60 mm skin sector and check three things: the fin-to-strip gap closes without binding, the printed outside diameter (66.04 ±0.2) against a real BT80 end, and the surface after sanding. Do this before printing a whole module.',
        '<b>Keep Option 1 available.</b> The 1:1 cutting template (a separate file) lets you build a V4-style skin from a real tube in the meantime; it is derived from the V4 windows and should be checked against your own tube before cutting.',
        '<b>Not verified:</b> drag of a printed surface against the tube, the effect of the extra 17 g on the rocket’s balance and apogee, and whether the printed fin skin cracks at the hinge ears on a hard landing (it is thicker than V4, so it should not be worse, but nothing has been tested).'])
    build_pdf(DOCS / 'V5_choice1_skin.pdf', 'V5 choice 1: module skin - ARC BT80', s)


def option_fasteners():
    s = []
    s += [P('Choice 2: how the head and the module are fastened', H1),
          P('The swap points are the joints I1 (head to module) and I2 (module to base). To swap the module you open both; to move the head to another brake you open I1 and the joint above it. '
            'There are three ways to make these joints. The drawings show why the third is awkward: the space between the electronics and the outside of the rocket is only <b>3.1 mm</b> in the radial direction. Concept numbers, not CAD.', B),
          P('1 &nbsp; The three options', H2),
          table([['', 'A: screws (with heat-set inserts)', 'B: captive thumb screws', 'C: collar bayonet'],
                 ['What it is', 'Four M3×5 button-head screws, radial, through the skin and the head sleeve into brass inserts in four 7 mm bosses inside the sleeve. Same at I2.', 'The same four bosses and inserts, but with knurled M3 thumb screws that you turn by hand.', 'Three lugs on a ring (collar) that turns 24.5° in three L-slots in a raised socket. The collar turns; the head body does not.'],
                 ['Tools', '2.0 mm hex driver', 'none', 'none (one safety screw or pin as a secondary lock)'],
                 ['Swap effort (estimate, not timed)', '8 screws out and in: about 5 minutes', 'about 1 minute', 'about 1 minute'],
                 ['Strength', 'best: steel screws in brass inserts carry shear and tension; used in V4 already', 'about the same as A if the thumb screw is steel; the heads stand 3.5 mm proud', 'weakest: three 6 mm printed lugs in a 1.2 mm collar; it needs testing'],
                 ['Wear', 'printed threads strip after repeated swaps, so use heat-set inserts (the checklist’s advice for parts assembled many times)', 'same as A (inserts)', 'lugs and slots wear; a detent bump wears'],
                 ['Surface', 'screw heads 1.7 mm proud', 'heads about 3.5 mm proud: a flush recess does not fit (the wall is 3.1 mm)', 'a 1 mm raised band round the joint (R34.0), or 1 mm of electronics radius given up'],
                 ['Main catch', 'the slowest to swap and screws can be lost', 'bigger heads in the airstream; hardware choice must be checked', 'the whole head cannot be twisted (see drawing): the rotor would move']], [26, 54, 48, 48], font=7.2),
          P('2 &nbsp; What each one costs in the design', H2),
          fig('opt_radial.png', 172, 'Radial budget at I1: the head sleeve, the skin and the fastener between R29.9 (the electronics’ inside limit) and R33.02 (the BT80 outside).', 74),
          PageBreak(), P('3 &nbsp; Drawings', H2),
          fig('opt_fast_screws.png', 172, 'Option A: section through the joint (left) and the four insert bosses in plan (right). The bosses are at 45, 135, 250 and 290° so they clear the battery and the Mercury; at 225/315° they would hit the battery corners. The earlier concept sheet drew them 90° apart: this plan corrects it.', 82),
          fig('opt_fast_thumb.png', 172, 'Option B: the same bosses with captive thumb screws; the heads stand proud because a recess does not fit.', 74),
          PageBreak(),
          fig('opt_fast_bayonet.png', 172, 'Option C: one L-slot developed flat (left) and the collar with three lugs in plan (right).', 96),
          fig('opt_twist.png', 120, 'A bayonet must turn a collar, not the head: the horn is engaged in the rotor, so turning the whole head would turn the rotor past the point where the fin latch lets go.', 60),
          PageBreak(), P('4 &nbsp; What I recommend', H2)]
    s += bullets([
        '<b>Start with Option A, screws into heat-set inserts.</b> It uses hardware V4 already has, it is the strongest, and the inserts survive many swaps. The four bosses go in the head sleeve at 45, 135, 250 and 290°.',
        '<b>Option B is a screw swap, not a redesign.</b> It uses the same bosses and inserts, so you can try thumb screws on the same parts. Check the real head height: if the heads stand 3.5 mm proud it is a trade of speed for a small obstacle in the airstream.',
        '<b>Leave Option C for later.</b> It needs a raised 1 mm band or less electronics radius, three 6 mm printed lugs in thin walls, and a collar that has to be tested; the drive coupling stays safe only if the collar, not the head, turns.',
        '<b>Decide where the rocket separates for recovery.</b> If the airbrake joints are where the airframe comes apart, they must carry the parachute shock, which favours screws. If the rocket separates elsewhere, the joints see only compression and handling loads.',
        '<b>First test (cheap):</b> print a 20 mm slice of the sleeve and skin with one boss, press in one insert, and screw it ten times. If the insert holds, build the full I1 sleeve.',
        '<b>Not verified:</b> every number is a concept dimension (3.1 mm radial space, boss sizes, lug sizes, swap times). The 24.5° turn of Option C and the latch-release angle of about 15° of rotor travel come from the V4 model; the rest is estimated.'])
    build_pdf(DOCS / 'V5_choice2_fastening.pdf', 'V5 choice 2: head and module fastening - ARC BT80', s)


def insert_concept():
    s = []
    s += [P('V5 insert concept: one BT80 tube, swappable module and head', H1),
          P('Your plan, in my words: the rocket gets <b>one BT80 tube</b>, cut once. The airbrake module slides into it; when it breaks you take it out and put another in, and <b>no piece of BT80 is glued to any fin</b>. '
            'The electronics head goes in the same tube, on top of the module. Concept only; the numbers come from the V4 model, not from tested CAD.', B),
          WARN_P('<b>The one catch:</b> the tube windows stay open. A fin that carries its own skin out to the tube’s outside diameter cannot slide into the tube, because the skin would hit the tube wall on the way in. '
                 'So the fins stay inside the tube (R32.2) and the four windows are left open or covered. Three ways to deal with that are drawn below; I suggest covering them with tape.'),
          P('1 &nbsp; What gets simpler', H2)]
    s += bullets([
        'The <b>module skin disappears</b>: the tube is the skin. No cut tube pieces per module, no glue, no printed skin (choice 1 from the earlier sheet is settled).',
        'No sockets, sleeves or raised bands at the joints, and no bayonet question: the module and the head are plain cylinders (OD 64.4 mm) that slide into the 65.0 mm bore with 0.3 mm clearance.',
        'The head and the module are <b>both inserts from the top</b>. Swapping a module is: open the top of the tube section, lift the head out (4 screws), lift the module out, drop in the new one, refit the head.',
        'The module <b>rests on the base ring</b> (bonded in the tube) and is clamped by the head from above, so it needs only two index screws, not eight.',
        'The tube carries everything else once: the windows, the screw holes, the vent holes, the switch slot and the USB-C window. The module and the head carry no skin and no vent features.'])
    s += [fig('ins_architecture.png', 150, 'The tube section with the base ring, the module insert and the head insert; the arrows show the removal path (concept, heights from the module seat).', 170),
          PageBreak(), P('2 &nbsp; The windows', H2),
          P('The windows are the same 65° × 42 mm openings as the V4 cut-outs (38.5 × 43 mm with 0.5 mm clearance). With no cut-outs glued to the fins, they have to be dealt with on their own.', B),
          fig('ins_clash.png', 160, 'Why the fins cannot carry a skin: left, a fin without skin slides past the tube wall; right, a skin on the fin would hit the tube wall.', 75),
          fig('ins_windows.png', 172, 'Section at the fin zone: windows left open, covered with tape, or a fin skin (which blocks insertion).', 80),
          table([['Option', 'What it is', 'Good', 'Bad'],
                 ['S1 open windows', 'four 38.5 × 43 mm holes in the tube, fins closed behind them', 'simplest; the Mercury sees outside static pressure through the open windows', 'about 6.6 cm² of holes, 27 % of this tube section’s skin; the drag cost is not measured; the fins can be seen and hit through the holes'],
                 ['<b>S1+ tape</b>', 'S1 plus a patch of foil or Kapton tape over each window, renewed every flight; the fins burst it when they open (the system deploys once)', 'smooth outside surface; no glue on the fins; renewing is seconds', 'wind suction (about 2.3 kPa at 80 m/s with the torque-check assumption) pulls about 3.8 N on each patch: it could bulge or tear early; needs a test'],
                 ['S2 slotted tube', 'windows open to the tube end as U-slots, fin skin to R33.02 slides through them', 'flush skin, nothing to tape', 'the tube becomes four fingers: weak; the end must be closed by the head sleeve']], [30, 56, 40, 50], font=7.3),
          PageBreak(), P('3 &nbsp; Swap procedure', H2),
          fig('ins_swap.png', 178, 'Swap in five steps (concept).', 85),
          P('<b>Index and retention:</b> the module is keyed by two radial M3 index screws through the tube into the module supports (at 45° and 225°, z_t 22), and by the windows: a module turned the wrong way puts its fins behind the tube strips and the screw holes do not line up. The head is held by four radial M3 screws into heat-set inserts in its sleeve (45, 135, 250, 290°), so the electronics layer clears the bosses. '
            '<b>Opening the top:</b> the tube section must be separable from the airframe above it; your recovery layout decides where.', B),
          P('4 &nbsp; Numbers', H2),
          table([['Item', 'Value (concept)'],
                 ['Tube', 'one BT80 section, OD 66.04, ID 65.0, about 120 mm long (windows, screws, vents cut once; template supplied 1:1)'],
                 ['Module insert', 'OD 64.4 (0.3 mm clearance), 68.8 mm long (module frame z −10 … 58.8), about 105 g of PLA (estimate)'],
                 ['Head insert', 'sleeve and cup, servo, Mercury, regulator, battery, about 55 g, 30 mm above the module top'],
                 ['Base ring', 'R26.5 … 32.5, 8 mm thick, bonded in the tube bottom; it is the module seat'],
                 ['Windows', '4 × 38.5 × 43 mm, centres at 0/90/180/270°, heights 17.5 … 60.5 above the seat'],
                 ['Stack inside the tube', 'base 8 + module 68.8 + head 30 = about 107 mm (V4 was 105.4 mm)'],
                 ['Swap effort', '4 head screws + 2 index screws (6 screws); not timed']], [40, 136], font=7.6),
          P('5 &nbsp; What changes in the V4 model', H2),
          table([['V4 part', 'Change'],
                 ['Housing (C1/C2)', 'outside radius 32.3 → 32.2; the bay, the lower shoulder, the four bosses, the cable groove, the cable hole and the vent holes are all <b>deleted</b>; the bottom becomes a plate on the base ring; the support strips keep two M3 index pilots.'],
                 ['Servo ledges', 'move into the head cup (the head carries the servo), as in the modular concept.'],
                 ['Fins and catch caps', 'unchanged shape; outer face at R32.2 (no skin, no glue); the 0.5 mm window clearance replaces the saw kerf.'],
                 ['Upper tube', 'becomes the one tube, cut once with the template; its windows and holes replace the glued cut-outs.'],
                 ['Transition ring', 'becomes the base ring bonded inside the tube bottom.'],
                 ['Electronics', 'as in the modular concept: all in the head, no wire crosses a joint.']], [42, 134], font=7.6),
          P('6 &nbsp; Risks and what to test first', H2)]
    s += bullets([
        '<b>Open or taped windows</b> are the main unknown (drag, suction on the tape, appearance). Test: print one fin and a 60 mm module slice, put them in a real BT80 piece with one window, and check that the module slides in and out, the fin opens through the window, and a tape patch survives a fan.',
        '<b>Slip fit after a crash:</b> a module that has been hit may be stuck in the tube. Print the module OD at R32.2 (0.3 clearance), not tighter, and add two finger notches at the top to pull it out.',
        '<b>Tube alignment:</b> the windows must sit exactly over the fins. The index screws take this up; check it on the first assembly.',
        '<b>The square holes in V4</b> (the vents and the cable hole) are gone in this concept: the vents move to the tube above the head, and nothing needs a cable hole any more.',
        '<b>Not verified:</b> the printed fit, the tape, the drag of the open windows, and the 3.8 N suction (it uses the Cp −0.6 assumption from the torque check).'])
    build_pdf(DOCS / 'V5_insert_concept.pdf', 'V5 insert concept - ARC BT80', s)


def final_plan():
    s = []
    s += [P('V5 final plan, before the CAD', H1),
          P('Your two questions first, then the plan I will build V5 from. Concept numbers, not yet in CAD.', B),
          P('1 &nbsp; Why tape the windows?', H2),
          P('Because the tube windows are <b>holes in the airframe</b> while the fins sit closed behind them: with no BT80 glued to the fins, nothing fills the four 38.5 × 43 mm openings (about 27 % of this tube section’s skin). Tape is there only to close them until the fins open. What it buys:', B)]
    s += bullets([
        '<b>A smooth outside surface.</b> Air flowing over open cavities adds drag and turbulence. I have <b>not measured</b> how much, and for a short airbrake section it may be small.',
        '<b>No air through the section.</b> Open windows let outside air in and out of the airbrake section, so the pressure inside follows the airflow. The altimeter should be protected from that by its own vent holes, but I cannot prove it without a test.',
        '<b>Clean fins and mechanism.</b> Dust and grit stay out until the fins are out.',
        '<b>It costs nothing at deployment.</b> The brake deploys once and stays out, so tape that the fins burst through never has to be closed again; you put a fresh strip on for the next flight in seconds. One wrap of foil or Kapton tape round the tube covers all four windows at once.'])
    s += [P('<b>It is optional.</b> The brake works with open windows. I recommended tape as the default to keep the outside clean; the risks are that wind suction (about 2.3 kPa, about 3.8 N per window by the torque-check assumption) could lift or tear it early, and that I do not know the drag of open windows. If you would rather not tape, we leave them open and decide after a test.', B),
          PageBreak(), P('2 &nbsp; The layout, corrected', H2),
          P('You are right about the stack, and it corrects my V4 drawing. The airbrake’s BT80 tube sits <b>directly on the transition</b>, and the transition tapers down to the BT70 tube below it. In V4 I had drawn a lower BT80 tube with a flat ring bonded inside it; there is no lower BT80 tube. What I called the transition ring is really the top of the transition. '
            'BT80 is 66.04 mm outside and 65.02 mm inside (Estes listings); BT70 is 56.3 mm outside (2.217 in); I could not confirm the BT70 inside diameter, which I need for the lower sleeve of the transition.', B),
          fig('fin_layout.png', 150, 'Final stack, nose up (concept, to scale). The airbrake section is one BT80 tube cut once; the module sits on the transition top; the head sits on the module; the section opens at its top.', 175),
          PageBreak(),
          fig('fin_seat.png', 150, 'The transition top: spigot glued into the tube bottom, seat face under the module, cone down to BT70. The cone length and the BT70 sleeve are placeholders.', 100),
          P('3 &nbsp; The decisions', H2),
          table([['Topic', 'Decision'],
                 ['Architecture', 'one BT80 tube cut once; <b>module</b> and <b>head</b> are inserts from the top; the base is the transition.'],
                 ['Skin', 'the tube is the skin. No glued BT80 on the fins, no printed skin. Fin outer face at R32.2.'],
                 ['Windows', '4 × 38.5 × 43 mm at 0/90/180/270°, 17.5 … 60.5 above the seat. Default open, or one wrap of tape: your call (section 1).'],
                 ['Fastening', 'radial M3×5 button screws into heat-set inserts: <b>4 for the head</b> (45, 135, 250, 290°) and <b>2 index screws</b> for the module (45, 225°). The module is also clamped between the transition seat and the head.'],
                 ['Wiring', 'servo, Mercury, regulator and battery all in the head; no wire crosses a joint; the cable groove, cable hole and V4 vents are deleted.'],
                 ['Tube features', 'switch slot, USB-C window and three O3 vents are cut in the tube above the head, once.'],
                 ['Drive', 'horn on the servo, in the rotor hub slot; add a 45° lead-in, a closed-position detent and a rotor lift-off keeper.'],
                 ['Module fit', 'OD 64.4 in the 65.0 bore (0.3 mm), two finger notches at the top to pull it out.'],
                 ['Swap', 'open the top of the tube section; 4 head screws; lift the head; 2 index screws; lift the module; reverse. Six screws, not timed.'],
                 ['Print orientation', 'as in the design review (rotor hub down with supports, fins flat, housing upright with supports at two levels).']], [32, 144], font=7.6),
          P('4 &nbsp; The V5 CAD build plan', H2),
          table([['Part', 'Work', 'Based on'],
                 ['Tube (reference)', 'BT80 ID 65.02, OD 66.04, 144 mm: windows, 6 screw holes, 4 head holes, vents, switch, USB-C, from the 1:1 template', 'V4 upper tube'],
                 ['Transition (new)', 'spigot 12 mm, seat face R26.0 … 32.3, cone 35 mm, BT70 sleeve (OD placeholder until you give me the BT70 ID)', 'V4 ring, redone'],
                 ['Module housing C1/C2', 'OD R32.2; remove the bay, bosses, cable groove and hole, vents; bottom plate on the seat; two index pilots; finger notches', 'V4 housing'],
                 ['Rotor', 'lead-in on the hub slot, closed detent, lift-off keeper', 'V4 rotor'],
                 ['Fins, catch caps, hardware', 'fin outer face to R32.2; the rest unchanged', 'V4'],
                 ['Head (new)', 'sleeve R29.9 … 32.2 with four insert bosses, cup with the two servo ledges, plate, single-layer sled (battery + Mercury + regulator), top cap', 'V4 sled, ledges, wiring plan'],
                 ['Assembly', 'module on the seat, head on the module, tube around; mates as before', 'asm V4']], [34, 106, 36], font=7.4),
          P('<b>Checks before I call V5 done:</b> no overlaps closed or open; the module slides along the tube and the fins open through the windows; the head goes down and the horn finds the slot at ±8°; rotor sweep −1.5° to 66.5° clear; latch and cam timing unchanged; V1–V3 volumes identical; hex-key access to the six screws; STL and STEP export; guide and head layout documents updated.', B),
          P('5 &nbsp; What I need from you', H2)]
    s += bullets([
        '<b>BT70 inside diameter</b> (or the tube’s part number) and the <b>length of the cone</b> you want (I draw 35 mm). Until then the BT70 sleeve is a placeholder.',
        '<b>Windows:</b> open, or one wrap of tape. I will model them the same either way; the tape is not in the CAD.',
        '<b>Where the section opens</b> (the top joint): this decides the top coupler, which I will leave as an open reference until you tell me.',
        '<b>Go-ahead for the V5 build</b> from V4. It is several hours of work: FeatureScript changes, the new transition and head, the assembly and the checks.'])
    s += [P('6 &nbsp; Risks', H2)]
    s += bullets([
        'The open or taped windows: drag and tape suction are unmeasured.',
        'The slip fit after a crash: a hit module may stick; the 0.3 mm clearance and the finger notches are meant to help.',
        'The BT70 sleeve and the cone are placeholders until the tube is measured.',
        'Nothing here has been printed or tested; every V5 dimension is a concept number.'])
    build_pdf(DOCS / 'V5_final_plan.pdf', 'V5 final plan - ARC BT80', s)


if __name__ == '__main__':
    which = sys.argv[1:] or ['v1', 'v2', 'v3']
    if 'v1' in which: v1()
    if 'v2' in which: v2()
    if 'v3' in which: v3()
    if 'mech' in which: mech()
    if 'history' in which: history()
    if 'sketch' in which: sketch_v4()
    if 'v4' in which: v4()
    if 'wiring' in which: wiring()
    if 'wiringplan' in which: wiring_plan()
    if 'modular' in which: modular()
    if 'optskin' in which: option_skin()
    if 'optfast' in which: option_fasteners()
    if 'insert' in which: insert_concept()
    if 'finalplan' in which: final_plan()
    print('docs written', list(DOCS.glob('*.pdf')))
