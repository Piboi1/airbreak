"""Rough SG90 torque check for the direct-drive V3 (rotor driven straight by the servo, no spring, latch on the rotor).
All inputs are assumptions printed below; geometry is read from the V2 CAD (fin area, hinge at R25 z0, lug and cam levers)."""
import math
A = 1.785e-3            # fin outer skin area, m2 (CAD: 1785 mm2)
Z_SKIN = 0.029          # centre of the skin above the hinge axis, m (skin z 4..54)
Z_LUG = 0.0458          # mean z of the fin lug wall (41.6..50), m
R_FINGER = 0.0248       # radius of the catch-cap finger, m
Z_FOLLOW = 0.0245       # centre of the cam follower above the hinge (z 20..29), m
DRDTH = 0.0127          # cam rise, m per rad (8 mm over 36 deg -> peak 28.6 version ~7.6 mm)
I_ROTOR = 2.04e-6 + 4 * 0.00058 * 0.0245**2   # kg m2: rotor + 4 catch caps
RHO = 1.1
SERVO = {'SG90 @4.8V stall': 0.176, 'SG90 @6V stall': 0.216}
USABLE = 0.5            # fraction of stall torque I would rely on (plastic gears, voltage sag)
print('Assumptions: rho %.1f, area %.0f mm2, friction mu 0.20 / 0.40, usable servo torque = %.0f%% of stall' % (RHO, A*1e6, USABLE*100))
print('Case A: suction coefficient Cp=-0.2 (typical cylinder side, windows), Case B: Cp=-0.6 (pessimistic, gap lift/turbulence)')
print()
print('%6s | %5s | %-34s | %-34s' % ('V m/s', 'q Pa', 'A: lug force / hold-release torque', 'B: lug force / hold-release torque'))
for V in (50, 100, 150, 200, 250):
    q = 0.5 * RHO * V * V
    cells = []
    for cp in (0.2, 0.6):
        F = q * cp * A                   # outward suction force per fin (N)
        M = F * Z_SKIN                   # moment about hinge (N m)
        N = M / Z_LUG                    # finger/lug normal force (N)
        lo = 4 * 0.20 * N * R_FINGER     # rotor torque to slide finger free, mu 0.20
        hi = 4 * 0.40 * N * R_FINGER
        cells.append('%.1f N / %.3f-%.3f N m' % (N, lo, hi))
    print('%6d | %5.0f | %-34s | %-34s' % (V, q, cells[0], cells[1]))
print()
for k, t in SERVO.items():
    print('%s = %.3f N m (usable %.3f)' % (k, t, t * USABLE))
# inertia / speed
t_move, ang = 0.11, math.radians(65)
alpha = 4 * ang / t_move ** 2
print('\nRotor spin-up (65 deg in %.2f s, triangular profile): alpha %.0f rad/s2 -> %.4f N m  (negligible)' % (t_move, alpha, I_ROTOR * alpha))
# fin kick: wind assists opening, so cam work is only inertia + friction; show worst case if the wind pressed the fin shut
for cp in (0.2, 0.6):
    for V in (100, 150):
        q = 0.5 * RHO * V * V
        M = q * cp * A * Z_SKIN
        Ff = M / Z_FOLLOW
        T = 4 * Ff * DRDTH
        print('Adverse case (wind pressing the fins shut, Cp=+%.1f, %d m/s): follower force %.1f N, cam torque %.3f N m' % (cp, V, Ff, T))
