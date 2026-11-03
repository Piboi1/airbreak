"""Figures for the V5 assembly guide: Onshape shaded views, own exploded render, sections."""
import os, sys, math, numpy as np
import figures as F, render, run, osapi
W = os.environ['AIRBRAKE_WORK']
d = run.ids(); did, wid = d['did'], d['wid']
F.COL.update({'C': F.BLUE, 'H': F.TEAL, 'K': F.BLUE2, 'E': F.GREY, 'E2': F.PURPLE, 'E3': (.9, .5, .62), 'E4': F.GOLD, 'EH': F.GOLD})
p5 = F.load('fin_v5')

vm = osapi.view_matrix(-40, 22)
osapi.shaded_view(did, wid, d['ps_v5'], F.OUT + 'v5_assembled.png', vm, w=900, h=1500)
osapi.shaded_view(did, wid, d['ps_v5b'], F.OUT + 'v5_open.png', vm, w=1100, h=1500)


def spec_exploded(t, name, m):
    z = lambda v: ((0, 0, v), None)
    if t.startswith('REF'): return None                       # the tube is shown in the shaded views
    if t == 'K': return z(125)
    if t.startswith('HW_head'): return (F.rot_z((40, 0, 0), F.mesh_az(m)) + np.array([0, 0, 82 - 82 + 82]), None)
    if t in ('E2', 'E3', 'E4'): return z(95)
    if t == 'H': return z(60)
    if t == 'E': return z(60)
    if t.startswith('HW_servo'): return z(60)
    if t == 'EH': return z(28)
    if t == 'HW_horn': return z(-6)
    if t == 'R': return z(18)
    if t.startswith('P') and t[1:].isdigit(): return (F.rot_z((38, 0, 0), F.az_of(name, t)), None)
    if t.startswith('HW_H'): return (F.rot_z((38, 0, 0), F.az_of(name, t)) + F.rot_z((0, -22, 0), F.az_of(name, t)), None)
    if t.startswith('HW_module'): return (F.rot_z((26, 0, 0), F.mesh_az(m)), None)
    if t == 'T': return z(-60)
    if t.startswith('HW_transition'): return (F.rot_z((26, 0, 0), F.mesh_az(m)) + np.array([0, 0, -60]), None)
    return z(0)


items = F.build(p5, spec_exploded)
img, meta = render.render(items, az=-55, el=20, size=(1500, 2500))
img.save(F.OUT + 'v5_built_exploded.png')
print('ok')
