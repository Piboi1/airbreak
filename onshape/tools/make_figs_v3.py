import pickle, numpy as np, figures as F, render, run, osapi
d = run.ids(); did, wid = d['did'], d['wid']
p1 = F.load('fin_v1'); p2 = F.load('fin_v2'); p3 = F.load('fin_v3')
items = F.build(p3, F.overview_v3(p3)); img, meta = render.render(items, az=-55, el=20, size=(1500, 2500)); img.save(F.OUT + 'v3_overview_exploded.png')
F.fig_v3_mount(F.OUT + 'v3_mount_sections.png', p3)
B = (40, 40, 200); Rr = (200, 40, 40); G = (30, 130, 60)
F.fig_compare3([p1, p2, p3], ['V1 (inline)', 'V2 (22 mm drop)', 'V3 (servo on rotor)'],
  [[(-33, 85, 'printed 118', B, 0)], [(-33, 58.8, 'printed 91.8', B, 0), (-15, -11, 'exposed 4', Rr, 330)],
   [(-33, 58.8, 'printed 91.8', B, 0), (-46.7, 58.8, 'with servo 105.5', G, 330)]], 'compare_length_v3.png')
vm = osapi.view_matrix(-40, 24)
osapi.shaded_view(did, wid, d['ps_v3'], F.OUT + 'v3_assembled.png', vm, w=900, h=1300)
osapi.shaded_view(did, wid, d['ps_v3b'], F.OUT + 'v3_open.png', vm, w=1000, h=1300)
# refresh the V2 renders and figures that show the corrected reference tube
osapi.shaded_view(did, wid, d['ps_v2'], F.OUT + 'v2_assembled.png', vm, w=900, h=1300)
osapi.shaded_view(did, wid, d['ps_v2b'], F.OUT + 'v2_open.png', vm, w=1000, h=1300)
print('v3 figs ok')
