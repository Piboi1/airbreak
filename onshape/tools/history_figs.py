"""Figures for the iteration-history document."""
import os, numpy as np, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle
from PIL import Image
import figures as F, render, run

OUT = F.OUT
W = os.environ['AIRBRAKE_WORK']

ITER = [  # name, short, housing mm, overall mm, mass g, part types, housing top z
    ('Original', 'bonded', 118.0, 178.5, 177, 33, 85.0),
    ('V1', 'screwed', 118.0, 178.5, 180, 19, 85.0),
    ('V2 first', 'compact head', 111.4, 171.9, 177, 19, 78.4),
    ('V2 22 mm', 'latch dropped', 91.8, 152.3, 169, 19, 58.8),
    ('V3', 'servo on rotor', 91.8, 105.5, 108, 5, 58.8)]

def fig_timeline(path):
    fig, ax = plt.subplots(figsize=(7.4, 8.4)); ax.axis('off'); ax.set_xlim(0, 100); ax.set_ylim(0, 112)
    cols = ['#e3e3e3', '#cfe0f2', '#d8ecd2', '#fbe3c2', '#e1d4f0']
    boxes = [
        (3, 90, 'ORIGINAL', 'your FeatureScript\nbonded pins, caps, seams\n178.5 mm  |  177 g'),
        (3, 68, 'V1  screwed', 'M3/M4 screws replace bonds,\nassembly document\n178.5 mm  |  180 g'),
        (3, 46, 'V2 first  compact head', 'head inside the upper BT80 tube,\nslit tube cut-outs glued to fins,\nthick strips between fins\n171.9 mm  |  177 g'),
        (3, 24, 'V2 22 mm drop', 'fins up to the head rim, new\ninward-lug latch, ring + window fixed\n152.3 mm  |  169 g'),
        (3, 2, 'V3  servo on rotor', 'SG90 straight on the rotor,\ncartridge + trigger removed\n105.5 mm  |  108 g')]
    for (x, y, t, d), c in zip(boxes, cols):
        ax.add_patch(FancyBboxPatch((x, y), 40, 17, boxstyle='round,pad=0.5', fc=c, ec='#444', lw=.9))
        ax.text(x + 1.5, y + 14.2, t, fontsize=8.5, fontweight='bold', va='center'); ax.text(x + 1.5, y + 6.5, d, fontsize=6.6, va='center')
    why = ['Why we moved on:\nyou wanted screw holes and an\nassembly document instead of glue',
           'Why we moved on:\nyou wanted it shorter: fins higher,\nsmaller head, supports, screws',
           'Why we moved on:\nyour white-outline drawing: fin top at\nthe head rim, everything under it\nmoves up (needs a new latch)',
           'Why we moved on:\nthe expert: a direct motor, fewer\nlayers, shorter and lighter']
    for i, w in enumerate(why):
        y0 = 90 - 22 * i
        ax.add_patch(FancyArrowPatch((23, y0), (23, y0 - 5), arrowstyle='-|>', mutation_scale=12, color='#444'))
        ax.text(48, y0 - 8.5, w, fontsize=6.8, va='center', color='#a02020')
        ax.plot([44, 46], [y0 - 2.5, y0 - 6.5], color='#a02020', lw=.8)
    ax.text(50, 105, 'Iteration history', fontsize=11, fontweight='bold')
    ax.text(50, 100.5, 'printed housing and overall length shown for every step;\nmass = printed parts, solid PLA', fontsize=6.8)
    ax.text(50, 8, 'Next: measure your SG90 and horn, ground-impact FEA,\nprint and test the latch.', fontsize=6.8, color='#1c6b3c')
    fig.tight_layout(); fig.savefig(path, dpi=220); plt.close(fig)

def fig_scale(path):
    """To-scale side bars: housing, fins, lower module / servo, for every iteration (mm, z up)."""
    fig, ax = plt.subplots(figsize=(7.4, 6.2))
    for i, (name, sub, hous, overall, mass, parts, top) in enumerate(ITER):
        x = i * 1.6
        ax.add_patch(Rectangle((x, -33), 1.0, top + 33, fc='#cfe0f2', ec='#335588', lw=1))                # printed housing
        ax.add_patch(Rectangle((x + .1, 4), 0.8, 50, fc='#f0a060', ec='#a05010', lw=.8))                  # fins (z 4..54, same in every version)
        if name == 'V3':
            ax.add_patch(Rectangle((x + .15, -46.7), .7, 22.7, fc='#9a9aa0', ec='#444', lw=.8)); low = -46.7
        else:
            ax.add_patch(Rectangle((x + .05, -93.5), .9, 60.5, fc='#d9d9d9', ec='#777', lw=.8)); low = -93.5   # cartridge, dock, cradle, servo
        ax.text(x + .5, top + 5, name, ha='center', fontsize=8, fontweight='bold')
        ax.text(x + .5, top + 14, f'{mass} g', ha='center', fontsize=7, color='#444')
        ax.annotate('', (x + 1.15, low), (x + 1.15, top), arrowprops=dict(arrowstyle='<->', lw=.8, color='#a02020'))
        ax.text(x + 1.2, (low + top) / 2, f'{overall:g} mm', rotation=90, va='center', fontsize=7, color='#a02020')
    ax.plot([-0.2, 8], [85, 85], color='#bbbbbb', lw=.6, ls=':')
    ax.text(8.1, 85, 'V1 head top', fontsize=6, va='center', color='#888888')
    ax.text(0, -104, 'blue: printed housing (z -33 up)   orange: fins (z 4..54, never moved)   grey: spring cartridge, dock, cradle, servo (V1, V2) / servo only (V3)', fontsize=6.4)
    ax.set_xlim(-0.4, 9.2); ax.set_ylim(-108, 108); ax.axis('off')
    ax.set_title('Every iteration to scale (z in mm; red = whole assembly length)', fontsize=9)
    fig.tight_layout(); fig.savefig(path, dpi=220); plt.close(fig)

def fig_metrics(path):
    fig, axs = plt.subplots(1, 3, figsize=(7.4, 2.6))
    names = [i[0] for i in ITER]; col = ['#999999', '#4a7fb5', '#79b45c', '#e8933a', '#8a5bc4']
    for ax, idx, title, unit in ((axs[0], 3, 'overall length', 'mm'), (axs[1], 4, 'printed mass (solid PLA)', 'g'), (axs[2], 5, 'printed bodies / types', '')):
        vals = [i[idx] for i in ITER]
        ax.bar(range(5), vals, color=col)
        for k, v in enumerate(vals): ax.text(k, v + max(vals) * .02, f'{v:g}', ha='center', fontsize=6.5)
        ax.set_xticks(range(5)); ax.set_xticklabels(names, rotation=35, ha='right', fontsize=6); ax.tick_params(labelsize=6)
        ax.set_title(f'{title} {("(" + unit + ")") if unit else ""}', fontsize=7.5); ax.set_ylim(0, max(vals) * 1.15)
    fig.tight_layout(); fig.savefig(path, dpi=220); plt.close(fig)

def render_baseline(path):
    parts = F.load('base_parts')
    def spec(t, nm, m):
        if t.startswith(('V', 'REF')) and not t.startswith('V') is False and t == 'V': return None
        return ((0, 0, 0), None)
    items = F.build(parts, lambda t, nm, m: None if t == 'V' else ((0, 0, 0), None))
    img, meta = render.render(items, az=-40, el=22, size=(900, 1300), scale=6.0, center=np.array([0, 0, -4]))
    img.save(path)

if __name__ == '__main__':
    fig_timeline(OUT + 'hist_timeline.png'); fig_scale(OUT + 'hist_scale.png'); fig_metrics(OUT + 'hist_metrics.png'); render_baseline(OUT + 'hist_baseline.png')
    import shutil
    H = '/tmp/claude-0/-home-user-airbreak/0f7dd06f-57bf-592d-965e-0ed0ad356493/scratchpad/hist/'
    for a, b in (('old_v2_assembled.png', 'hist_v2first.png'), ('dz_preview.png', 'hist_dz_preview.png'), ('old_compare_length.png', 'hist_compare_v1_v2first.png')):
        shutil.copy(H + a, OUT + b)
    print('history figs ok')
