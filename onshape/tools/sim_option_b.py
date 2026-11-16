"""Kinematic simulation of fin idea B (one follower locks, pushes and holds open), corrected version B':
a ball on a short lever under the hinge runs in a 3D track on the rotor. Writes docs/option_B_simulation.gif and .mp4 + a summary PNG.
Pure geometry (no Onshape). Fin azimuth 0 (x = radial), hinge axis along y at R25, z0; z up (nose); fins open outward."""
import numpy as np, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import animation
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

H = np.array([25.0, 0.0])                    # hinge (R, z)
D0 = np.array([-4.0, -5.5])                  # ball centre relative to the hinge, fin closed (on the tail, under the hinge)
LEV = np.hypot(*D0)
BALL = 1.5                                   # ball radius
PH = (12.0, 52.0, 65.0)                      # lock dwell end, push end, rotor stop

def theta(phi):                              # fin angle (deg) vs rotor angle (deg): dwell, cycloidal rise, dwell
    u = np.clip((phi - PH[0]) / (PH[1] - PH[0]), 0, 1)
    return 90.0 * (u - np.sin(2 * np.pi * u) / (2 * np.pi))

def dtheta(phi, e=1e-3): return (theta(phi + e) - theta(phi - e)) / (2 * e)

def rot(v, th):                              # fin rotation in the (R, z) plane: top swings outward
    c, s = np.cos(np.radians(th)), np.sin(np.radians(th))
    return np.array([v[0] * c + v[1] * s, -v[0] * s + v[1] * c])

def ball(phi): return H + rot(D0, theta(phi))

# track centre-line in the ROTOR frame: the point that meets the fin plane when the rotor is at phi sits at rotor angle -phi
PHI = np.linspace(-3, 68, 300)
TR = np.array([ball(p) for p in PHI])
track_rotor = np.c_[TR[:, 0] * np.cos(np.radians(-PHI)), TR[:, 0] * np.sin(np.radians(-PHI)), TR[:, 1]]

def fin_polys(th):
    """Simplified B fin: curved skin R29.8..32.2, +-32.5 deg, z 4..54; hinge knuckle; tail lever + ball. Returns polygons (world frame)."""
    polys = []
    a = np.radians(np.linspace(-32.5, 32.5, 9))
    def P(R, y, z):                          # point in the fin's own frame (closed) -> rotate about hinge -> world
        r, zz = H + rot(np.array([R, z]) - H, th)
        return (r, y, zz)
    for z0, z1 in ((4, 54),):
        for i in range(len(a) - 1):
            for R in (32.2, 29.8):
                y0, y1 = R * np.sin(a[i]), R * np.sin(a[i + 1]); x0, x1 = R * np.cos(a[i]), R * np.cos(a[i + 1])
                polys.append([P(x0, y0, z0), P(x1, y1, z0), P(x1, y1, z1), P(x0, y0, z1)])
    # knuckle (box approx) and lever
    for (r0, r1, z0, z1, yy) in ((20.5, 29.5, -4.5, 4.5, 7.4), (H[0] + D0[0] - 1, 26, H[1] + D0[1] - 1, 1, 2.0)):
        for (ra, rb, za, zb) in ((r0, r1, z0, z0), (r0, r1, z1, z1), (r0, r0, z0, z1), (r1, r1, z0, z1)):
            polys.append([P(ra, -yy, za), P(rb, -yy, zb), P(rb, yy, zb), P(ra, yy, za)])
    return polys

def sphere(c, r, n=10):
    u, v = np.meshgrid(np.linspace(0, 2 * np.pi, n), np.linspace(0, np.pi, n))
    return c[0] + r * np.cos(u) * np.sin(v), c[1] + r * np.sin(u) * np.sin(v), c[2] + r * np.cos(v)

FR = list(np.arange(0, 65.01, 2.5)) + [65] * 8 + list(np.arange(65, -0.01, -2.5)) + [0] * 8
fig = plt.figure(figsize=(16, 9), dpi=80)
ax3 = fig.add_axes([0.0, 0.08, 0.42, 0.84], projection='3d')
axs = fig.add_axes([0.44, 0.40, 0.22, 0.52]); axu = fig.add_axes([0.71, 0.55, 0.27, 0.37]); axt = fig.add_axes([0.71, 0.10, 0.27, 0.32])
title = fig.text(0.02, 0.95, '', fontsize=15, weight='bold')
note = fig.text(0.44, 0.05, '', fontsize=10, va='bottom')
fig.text(0.02, 0.02, 'Idea B (corrected): ball on a 6.8 mm lever under the hinge runs in a twisted track on the rotor. Schematic kinematics, not CAD; sizes are a first guess.', fontsize=9, color='#555')

def phase(phi):
    return ('LOCKED: track is level, the fin cannot move', '#2e8b57') if phi <= PH[0] else (('PUSHING: track ramps, ball and fin swing out', '#e8762b') if phi < PH[1] else ('HELD OPEN at 90 deg: track is level again', '#1f77b4'))

def draw(k):
    phi = FR[k]; th = theta(phi); b = ball(phi); lab, col = phase(phi)
    back = k > len(FR) / 2
    title.set_text(f'rotor {phi:4.1f} deg   ->   fin {th:4.1f} deg      {lab}' + ('   (servo turning back: the track PULLS the fin shut)' if back and 0 < phi < 65 else ''))
    title.set_color(col)
    # ---- 3D
    ax3.cla()
    ax3.add_collection3d(Poly3DCollection(fin_polys(th), facecolor='#e8a26b', edgecolor='#7a4a2a', lw=.3, alpha=.9))
    c, s = np.cos(np.radians(phi)), np.sin(np.radians(phi))
    tr = track_rotor @ np.array([[c, s, 0], [-s, c, 0], [0, 0, 1]])  # rotor frame -> world (rotate by +phi)
    ax3.plot(tr[:, 0], tr[:, 1], tr[:, 2], color='#2e8b57', lw=6, alpha=.75)
    t = np.linspace(0, 2 * np.pi, 40)
    for zz in (-8, 14):
        ax3.plot(10 * np.cos(t), 10 * np.sin(t), zz, color='#7f8c99', lw=1)
    for a in np.radians(np.arange(0, 360, 45)): ax3.plot([10 * np.cos(a)] * 2, [10 * np.sin(a)] * 2, [-8, 14], color='#7f8c99', lw=.6)
    arm = np.radians(-phi * 0 + 0)
    xs, ys, zs = sphere([b[0], 0, b[1]], BALL); ax3.plot_surface(xs, ys, zs, color='k')
    ax3.plot([H[0]] * 2, [-12, 12], [0, 0], 'k--', lw=1)
    ax3.text(H[0], 13, 0, 'hinge', fontsize=8)
    ax3.text(-10, -10, 15, 'rotor (turned by the servo)', fontsize=8, color='#555')
    ax3.set_xlim(-5, 60); ax3.set_ylim(-32, 32); ax3.set_zlim(-12, 56); ax3.set_box_aspect((65, 64, 68))
    ax3.view_init(elev=18, azim=-62); ax3.set_xlabel('R'); ax3.set_ylabel('y'); ax3.set_zlabel('z')
    # ---- side section in the fin plane
    axs.cla(); axs.set_title('side section through the fin', fontsize=10)
    sk = [H + rot(np.array(p) - H, th) for p in ((29.8, 4), (32.2, 4), (32.2, 54), (29.8, 54))]
    axs.add_patch(plt.Polygon(sk, fc='#e8a26b', ec='k'))
    axs.add_patch(plt.Circle(H, 4.8, fc='#e8a26b', ec='k')); axs.add_patch(plt.Circle(H, 1.7, fc='w', ec='k'))
    axs.plot([H[0], b[0]], [H[1], b[1]], color='#7a4a2a', lw=5, solid_capstyle='round')
    ang = np.linspace(0, 90, 50); pth = np.array([H + rot(D0, a) for a in ang]); axs.plot(pth[:, 0], pth[:, 1], ':', color='#2e8b57')
    axs.add_patch(plt.Circle(b, BALL + 0.3, fc='#cfe8d6', ec='#2e8b57', lw=1.5)); axs.add_patch(plt.Circle(b, BALL, fc='k'))
    axs.plot([32.51, 32.51], [-12, 60], color='#8a6d3b', lw=2); axs.text(33, 56, 'tube', fontsize=7, color='#8a6d3b')
    axs.plot([0, 30], [-8, -8], color='#7f8c99', lw=2); axs.text(1, -7.3, 'housing floor', fontsize=7)
    axs.add_patch(plt.Rectangle((0, -8), 10, 22, fc='#9aa7b5', alpha=.5)); axs.text(5, 3, 'rotor', fontsize=7, ha='center')
    axs.set_xlim(-1, 62); axs.set_ylim(-12, 60); axs.set_aspect('equal'); axs.tick_params(labelsize=7)
    axs.text(1, 56, f'ball at R {b[0]:.1f}, z {b[1]:.1f}', fontsize=8)
    # ---- unrolled track
    axu.cla(); axu.set_title('the track on the rotor (unrolled), green = ball centre line', fontsize=10)
    axu.axvspan(0, PH[0], color='#2e8b57', alpha=.12); axu.axvspan(PH[0], PH[1], color='#e8762b', alpha=.12); axu.axvspan(PH[1], 65, color='#1f77b4', alpha=.12)
    axu.plot(PHI, TR[:, 1], color='#2e8b57', lw=8, alpha=.35); axu.plot(PHI, TR[:, 1], color='#2e8b57', lw=1)
    axu.plot(PHI, TR[:, 0] - 20, color='#555', lw=1, ls='--'); axu.text(40, TR[-1, 0] - 20 + .6, 'track radius - 20 mm', fontsize=7, color='#555')
    axu.plot(phi, b[1], 'ko', ms=9)
    for x, t_ in ((1, 'LOCK'), (25, 'PUSH'), (53, 'HOLD')): axu.text(x, 6.5, t_, fontsize=8, weight='bold')
    axu.set_xlim(-3, 68); axu.set_ylim(-8, 8); axu.set_xlabel('position along the rotor (deg)', fontsize=8); axu.set_ylabel('height z (mm)', fontsize=8); axu.tick_params(labelsize=7)
    # ---- fin angle and gear ratio
    axt.cla(); pp = np.linspace(0, 65, 200)
    axt.plot(pp, theta(pp), color='#e8762b'); axt.plot(phi, th, 'ko'); axt.set_ylabel('fin angle (deg)', fontsize=8, color='#e8762b')
    axt.set_xlabel('rotor angle (deg)', fontsize=8); axt.tick_params(labelsize=7); axt.set_xlim(0, 65); axt.set_ylim(-5, 95)
    a2 = axt.twinx(); a2.plot(pp, [dtheta(p) for p in pp], color='#555', ls='--'); a2.set_ylabel('fin deg per rotor deg', fontsize=8); a2.tick_params(labelsize=7); a2.set_ylim(0, 5)
    note.set_text(f'In the green and blue zones a push on the fin (air load) only presses the ball against a LEVEL track wall:\n'
                  f'it cannot turn the rotor, so the fin is locked with no servo torque. One ball replaces the push pad, the lock lug and the tail lock.')
    return []

ani = animation.FuncAnimation(fig, draw, frames=len(FR), interval=90, blit=False)
ani.save('../docs/option_B_simulation.gif', writer=animation.PillowWriter(fps=11))
ani.save('../docs/option_B_simulation.mp4', writer=animation.FFMpegWriter(fps=11, bitrate=2400))
draw(14); fig.savefig('../docs/option_B_simulation_still.png', dpi=80)
# numbers for the write-up
twist = 90.0
print('lever %.2f mm; ball closed R %.1f z %.1f, open R %.1f z %.1f; peak fin deg per rotor deg %.2f; neck direction twists %d deg along the track'
      % (LEV, *ball(0), *ball(65), max(dtheta(p) for p in np.linspace(0, 65, 400)), twist))
