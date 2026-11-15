"""Printed nut ring for the BT80 / transition joint: a short ring that sits on the INSIDE, with 4 M3 nuts held in slots
open to the top, so 4 M3 bolts go in radially from the outside (through the BT80 tube, and through the transition's
shoulder if it is in between) and pull everything together. No glue, no inserts.

Usage: python3 nut_ring.py [OD_mm] [height_mm]
  OD = inside diameter of whatever the ring sits in, minus 0.6 mm (0.3 mm play per side).
  Default 64.4 = straight inside the BT80 tube (ID 65.0).
Print: flat on the bed, slots up, no supports. Nuts drop into the slots from the top before the ring goes in.
"""
import sys, numpy as np, trimesh
OD = float(sys.argv[1]) if len(sys.argv) > 1 else 64.4
H = float(sys.argv[2]) if len(sys.argv) > 2 else 12.0
WALL = 5.0                     # radial wall at the four nut bosses
BAND = 2.0                     # radial wall of the thin band between the bosses
BOSS_HALF = 15.0               # half-width of each boss, degrees
RO, RI = OD / 2, OD / 2 - WALL
ZB = H / 2                     # bolt height (middle of the ring)
NUT_AF, NUT_T = 5.5, 2.4       # M3 nut across flats, thickness
SLOT_W, SLOT_D = NUT_AF + 0.35, NUT_T + 0.35
SKIN = 1.4                     # wall between the nut and the outside face
CLR = 1.7                      # 3.4 mm clearance hole
E = lambda a, b: trimesh.boolean.difference([a, b], engine='manifold')
from shapely.geometry import Polygon
def sector(ri, ro, a0, a1, n=48):
    t = np.radians(np.linspace(a0, a1, n))
    return trimesh.creation.extrude_polygon(Polygon([(ro*np.cos(x), ro*np.sin(x)) for x in t] + [(ri*np.cos(x), ri*np.sin(x)) for x in t[::-1]]), H)
band = E(trimesh.creation.cylinder(radius=RO, height=H, sections=256), trimesh.creation.cylinder(radius=RO - BAND, height=H + 2, sections=256))
band.apply_translation([0, 0, H / 2])
ring = trimesh.boolean.union([band] + [sector(RI, RO - 0.5, 45 + 90*k - BOSS_HALF, 45 + 90*k + BOSS_HALF) for k in range(4)], engine='manifold')
cuts = []
for k in range(4):
    a = np.radians(45 + 90 * k)
    r1 = RO - SKIN; r0 = r1 - SLOT_D
    zlo = ZB - NUT_AF / np.sqrt(3)            # nut stands on a corner: half its across-corners below the bolt axis
    slot = trimesh.creation.box([SLOT_D, SLOT_W, H - zlo + 1]); slot.apply_translation([(r0 + r1) / 2, 0, (zlo + H + 1) / 2])
    hole = trimesh.creation.cylinder(radius=CLR, height=WALL + 4, sections=48)
    hole.apply_transform(trimesh.transformations.rotation_matrix(np.pi / 2, [0, 1, 0])); hole.apply_translation([(RO + RI) / 2, 0, ZB])
    for c in (slot, hole):
        c.apply_transform(trimesh.transformations.rotation_matrix(a, [0, 0, 1])); cuts.append(c)
ring = E(ring, trimesh.boolean.union(cuts, engine='manifold'))
name = f'../exports/nut_ring/nut_ring_OD{OD:.1f}_H{H:.0f}.stl'
ring.export(name)
print(name, 'volume %.0f mm3 = %.1f g PLA, watertight %s' % (ring.volume, ring.volume * 1.24e-3, ring.is_watertight))
print('ID %.1f, bolt holes at z %.1f (from the ring bottom), 45/135/225/315 deg; skin over the nut %.1f mm; slots %.2f wide x %.2f deep'
      % (2 * RI, ZB, SKIN, SLOT_W, SLOT_D))
