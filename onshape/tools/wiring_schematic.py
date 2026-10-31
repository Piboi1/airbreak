"""Wiring schematic: 2S LiPo -> fuse -> switch -> 5 V buck regulator -> SG90 (with bulk capacitor); Mercury V1 -> servo signal; common ground."""
import numpy as np, matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, FancyBboxPatch
import figures as F

fig, ax = plt.subplots(figsize=(10.4, 6.8)); ax.set_xlim(0, 112); ax.set_ylim(-7, 72); ax.axis('off')
K = '#222'; RED = '#c01010'; BLU = '#1a56b0'; GRY = '#666'; BRN = '#5a3a20'; ORG = '#e08a00'
def wire(pts, c=K, lw=1.8, ls='-'): ax.plot([p[0] for p in pts], [p[1] for p in pts], color=c, lw=lw, ls=ls, solid_capstyle='round', zorder=2)
def dot(x, y, c=K): ax.add_patch(Circle((x, y), .85, fc=c, ec=c, zorder=5))
def label(x, y, t, fs=7.5, c=K, ha='center', va='center', w='normal'): ax.text(x, y, t, fontsize=fs, color=c, ha=ha, va=va, fontweight=w, zorder=6)
def box(x0, y0, x1, y1, fc, t, fs=7.5, ty=None):
    ax.add_patch(FancyBboxPatch((x0, y0), x1 - x0, y1 - y0, boxstyle='round,pad=0.3', fc=fc, ec=K, lw=1.3, zorder=3)); label((x0 + x1) / 2, (y0 + y1) / 2 if ty is None else ty, t, fs)
def hop_h(x0, x1, y, xc, c, r=1.6, lw=2.0):
    """horizontal wire from x0 to x1 at y that hops over a vertical wire at xc"""
    wire([(x0, y), (xc - r, y)], c=c, lw=lw); wire([(xc + r, y), (x1, y)], c=c, lw=lw)
    t = np.linspace(np.pi, 0, 30); ax.plot(xc + r * np.cos(t), y + r * np.sin(t), color=c, lw=lw, zorder=4)

GY = 10; TY = 54
# ---- ground rail
wire([(8, GY), (101, GY)]); 
for i, w in enumerate((3.4, 2.1, .8)): ax.plot([101 - w, 101 + w], [GY - 2.2 - i * 1.2] * 2, color=K, lw=1.8)
wire([(101, GY), (101, GY - 2.2)]); label(30, GY - 4.3, 'GND rail: common to the battery, regulator, servo and Mercury', 7.0, GRY)
# ---- battery (2S: two cells, long plate = +)
bx = 8
wire([(bx, 40), (bx, TY)]); wire([(bx, GY), (bx, 22)])
for y, w, lw in ((40, 5.0, 2.4), (37.4, 2.6, 3.6), (33.4, 5.0, 2.4), (30.8, 2.6, 3.6), (26.8, 5.0, 2.4), (24.2, 2.6, 3.6)):
    ax.plot([bx - w, bx + w], [y, y], color=K, lw=lw)
wire([(bx, 24.2), (bx, 22)])
label(bx + 3.5, TY - 3.2, '+', 12, RED, w='bold'); label(bx + 3.5, GY + 4.5, '–', 13, K, w='bold')
label(bx, 63, '2S LiPo, 7.4 V\nTattu 300 mAh 2S\n≈ 46 x 16 x 12 mm, 17 g', 7.2)
dot(bx, GY)
# ---- fuse + switch on the + line
wire([(bx, TY), (22, TY)])
ax.add_patch(Rectangle((22, TY - 1.7), 8, 3.4, fc='white', ec=K, lw=1.5, zorder=3)); wire([(22, TY), (30, TY)], lw=.9)
label(26, TY + 5.0, 'F1 (optional)\n1.1 A resettable', 6.8); wire([(30, TY), (38, TY)])
dot(38, TY); ax.plot([38, 46], [TY, TY + 4.6], color=K, lw=2.0, zorder=3); dot(47, TY); wire([(47, TY), (54, TY)])
label(43, TY + 8.6, 'SW1 arming switch\nor pull-pin (>= 1 A)', 6.8)
# ---- regulator
box(54, 42, 76, 62, '#f7d1da', 'Pololu D24V10F5\n5 V buck, 1 A\n18 x 13 x 4 mm\nVIN 5.1 – 36 V', 7.2, ty=53)
label(55.5, TY, 'VIN', 6.6, K, 'left'); label(74.5, TY, 'VOUT', 6.6, K, 'right')
wire([(54, 46), (30, 46)]); label(55.5, 46, 'GND', 6.6, K, 'left'); wire([(30, 46), (30, GY)]); dot(30, GY)
# ---- +5 V rail, capacitor, servo supply
RY = TY
wire([(76, RY), (96, RY)], c=RED, lw=2.2); label(88, RY + 2.9, '+5 V servo supply', 7.2, RED)
CX = 82
dot(CX, RY); wire([(CX, RY), (CX, 33.5)]); wire([(CX, 30.0), (CX, GY)]); dot(CX, GY)
ax.plot([CX - 2.6, CX + 2.6], [33.5, 33.5], color=K, lw=2.6); ax.plot([CX - 2.6, CX + 2.6], [30.0, 30.0], color=K, lw=1.5)
label(CX + 4.6, 35.2, '+', 8, RED, w='bold'); label(CX + 5.2, 31.8, 'C1', 8, K, 'left', w='bold')
# ---- servo
box(96, 25, 110, 61, '#d4d4d8', 'SG90\nservo', 8, ty=57)
for y, c, t in ((RY, RED, 'V+ (red)'), (44, ORG, 'signal (orange)'), (31, BRN, 'GND (brown)')):
    wire([(96, y), (93.5, y)], c=c, lw=2.4); label(96.9, y, t, 5.6, c, 'left')
wire([(93.5, 31), (90, 31)], c=BRN, lw=2.2); wire([(90, 31), (90, GY)], c=BRN, lw=2.2); dot(90, GY)
# ---- Mercury
box(38, 14.5, 66, 36, '#e3d3f2', 'Mercury V1 altimeter\nown 50 mAh cell, USB-C, Wi-Fi\nservo header GP6 (or GP7)', 7.0)
wire([(66, 30), (77.4, 30)], c=BLU, lw=2.2); wire([(77.4, 30), (77.4, 44)], c=BLU, lw=2.2)
hop_h(77.4, 96, 44, CX, BLU)
label(66.6, 32.3, 'GP6 signal', 6.8, BLU, 'left')
wire([(66, 22), (70, 22)], c=GRY, lw=1.3, ls='--'); ax.plot([70.4, 72.6], [20.9, 23.1], color=RED, lw=2.2); ax.plot([70.4, 72.6], [23.1, 20.9], color=RED, lw=2.2)
label(66.6, 26.6, 'servo-header V+ pin:\nleave unconnected', 5.8, GRY, 'left')
wire([(46, 14.5), (46, GY)]); dot(46, GY); label(48, 12.4, 'GND', 6.6, K, 'left')
# ---- title and rules
label(2, 70, 'V4 airbrake: servo power and signal (wiring schematic)', 11.5, K, 'left', w='bold')
label(2, -2.0, 'C1 = 470 - 1000 uF, 10 V, low-ESR, wired right at the servo pins.   The regulator powers the servo; the Mercury only sends the position signal.', 6.8, K, 'left')
label(2, -5.0, 'Ground is shared. Never join the servo red wire to a Mercury pin; confirm the Mercury servo-header pin order in its manual before wiring.', 6.8, K, 'left')
fig.tight_layout(); fig.savefig(F.OUT + 'v4_wiring_schematic.png', dpi=220); plt.close(fig)
print('schematic ok')
