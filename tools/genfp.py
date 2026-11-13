"""Generate a CubeSat Kit footprint from Pumpkin's 810-00253 rev B2 DXF.

usage: genfp.py SLOT.DXF OUT.kicad_mod [CSK_PC104_Slot0 | CSK_PC104_Slot1]
The DXFs ship with the specification and are not in this repository;
`just footprints` runs this for both slots and compares with KiCad/.

- Edge.Cuts: the DXF outline. One mounting-hole pad ring is drawn as an arc
  clipped by the edge; it is dropped. Slot 0's outline is open at the
  bottom-left hole and is closed along that hole's r = 0.125" pad circle, the
  feature the drawing calls out for the 2nd separation switch. Slot 1's
  outline is already closed.
- Pins: H1 = pads 1-52, H2 = pads 53-104, odd pins on the lower row of each
  header (spec frame), 0.1" grid, SPEL's 1.6 mm pads on 1.016 mm drills.
- Holes: 3.18 mm. Plated 6.35 mm pads where the board edge allows the spec's
  1.27 mm copper setback; bare NPTH at the two holes where it does not.
- Rule areas: the closed boxes in the DXF (three on Slot 0, none on Slot 1).
Origin: H1 pin 1. KiCad y points down; the DXF's points up.
"""
import math
import sys
import uuid

sys.path.insert(0, __file__.rsplit("/", 1)[0])
import dxfloops as D

IN = 25.4
dxf, out = sys.argv[1], sys.argv[2]
NAME = sys.argv[3] if len(sys.argv) > 3 else "CSK_PC104_Slot0"
SLOT = "Slot 1" if NAME.endswith("Slot1") else "Slot 0"
KIND = "extended" if SLOT == "Slot 1" else "base"
es = D.edges(D.read(dxf))
# Pumpkin draws one mounting-hole pad ring as an ARC clipped where it meets the
# edge; it is copper, not outline. Drop arcs of r = 0.125" centred on a hole.
_holes_in = [(0.200, 0.200), (3.350, 0.200), (0.350, 3.575), (3.250, 3.575)]
_n = len(es)
_x0 = min(min(e["a"][0], e["b"][0]) for e in es); _y0 = min(min(e["a"][1], e["b"][1]) for e in es)
es = [e for e in es if not (e["kind"] == "arc" and abs(e["r"] - 0.125) < 1e-4 and any(math.dist((e["c"][0] - _x0, e["c"][1] - _y0), h) < 1e-3 for h in _holes_in))]
print(f"dropped {_n - len(es)} pad-ring arc(s) from the outline")
allp = [p for e in es for p in (e["a"], e["b"])]
X0, Y0 = min(p[0] for p in allp), min(p[1] for p in allp)
spec = lambda p: ((p[0] - X0) * IN, (p[1] - Y0) * IN)          # mm, y up, origin bottom-left
PIN1 = (0.550 * IN, 3.275 * IN)
kc = lambda p: (round(p[0] - PIN1[0], 4), round(-(p[1] - PIN1[1]), 4))  # KiCad, origin H1 pin 1
U = lambda: str(uuid.uuid4())
f = lambda v: f"{v:.4f}".rstrip("0").rstrip(".")

chains = D.chains(es)
closed, opened = [], []
for ch in chains:
    pts = D.polyline(es, ch)
    (closed if math.dist(pts[0], pts[-1]) < 1e-4 else opened).append(ch)
assert len(opened) in (0, 1), (len(opened), len(closed))

# outline edges in spec mm, as (kind, a, m, b)
outline = []
def emit(ch):
    for i, rev in ch:
        e = es[i]
        a, b = (e["b"], e["a"]) if rev else (e["a"], e["b"])
        outline.append(("line", spec(a), None, spec(b)) if e["kind"] == "line" else ("arc", spec(a), spec(e["m"]), spec(b)))

if opened:
    (c0,) = opened
else:
  # outline already closed: it is the largest closed chain; the rest are keepouts
  big = max(closed, key=lambda ch: len(ch))
  closed = [ch for ch in closed if ch is not big]
  emit(big)
if opened:
    pts0 = D.polyline(es, c0)
    s0, e0 = spec(pts0[0]), spec(pts0[-1])
    hole_bl = (0.200 * IN, 0.200 * IN)
    r_pad = 0.125 * IN
    # the one gap: both ends lie on the bottom-left hole's pad circle
    assert abs(math.dist(s0, hole_bl) - r_pad) < 0.01 and abs(math.dist(e0, hole_bl) - r_pad) < 0.01, (s0, e0)
    emit(c0)                                   # s0 -> e0
    # close e0 -> s0 along the pad circle, the way that passes below the hole
    angle = lambda p: math.atan2(p[1] - hole_bl[1], p[0] - hole_bl[0])
    mids = []
    for direction in (1, -1):
        a_from, a_to = angle(e0), angle(s0)
        span = ((a_to - a_from) * direction) % (2 * math.pi)
        am = a_from + direction * span / 2
        mids.append((hole_bl[0] + r_pad * math.cos(am), hole_bl[1] + r_pad * math.sin(am)))
    mid = min(mids, key=lambda q: q[1])
    assert mid[1] < hole_bl[1] - r_pad / 2, mid
    outline.append(("arc", e0, mid, s0))
for (_, _, _, b), (_, a, _, _) in zip(outline, outline[1:] + outline[:1]):
    assert math.dist(a, b) < 1e-3, (a, b)

holes = [(0.200, 0.200), (3.350, 0.200), (0.350, 3.575), (3.250, 3.575)]
holes = [(x * IN, y * IN) for x, y in holes]

def arc_points(a, m, b, n=90):
    """Points on the circular arc from a through m to b."""
    ax, ay = a; bx, by = m; cx, cy = b
    d = 2 * (ax * (by - cy) + bx * (cy - ay) + cx * (ay - by))
    ux = ((ax * ax + ay * ay) * (by - cy) + (bx * bx + by * by) * (cy - ay) + (cx * cx + cy * cy) * (ay - by)) / d
    uy = ((ax * ax + ay * ay) * (cx - bx) + (bx * bx + by * by) * (ax - cx) + (cx * cx + cy * cy) * (bx - ax)) / d
    r = math.dist((ux, uy), a)
    t0, tm, t1 = (math.atan2(q[1] - uy, q[0] - ux) for q in (a, m, b))
    # go from t0 to t1 in the direction that passes tm
    def ccw(x, y):
        return (y - x) % (2 * math.pi)
    span = ccw(t0, t1)
    if ccw(t0, tm) > span:
        span -= 2 * math.pi
    return [(ux + r * math.cos(t0 + span * k / n), uy + r * math.sin(t0 + span * k / n)) for k in range(n + 1)]

def edge_dist(p):
    best = 1e9
    for kind, a, m, b in outline:
        if kind == "line":
            dx, dy = b[0] - a[0], b[1] - a[1]
            t = max(0, min(1, ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / (dx * dx + dy * dy)))
            best = min(best, math.hypot(p[0] - a[0] - t * dx, p[1] - a[1] - t * dy))
        else:
            for q in arc_points(a, m, b):
                best = min(best, math.dist(p, q))
    return best

lines = [
    f'(footprint "{NAME}"',
    "\t(version 20260206)",
    '\t(generator "pcbnew")',
    '\t(generator_version "10.0")',
    '\t(layer "F.Cu")',
    f'\t(descr "CubeSat Kit bus board, {KIND} {SLOT} pattern per Pumpkin 810-00253 rev B2: outline, H1/H2 2x26 headers (0.1 in grid, 0.025 in square pins), 4x 3.18 mm mounting holes' + (', and keepouts' if SLOT == 'Slot 0' else '') + '. Origin at H1 pin 1.")',
    '\t(tags "CubeSat PC104 CSK Pumpkin H1 H2")',
    '\t(property "Reference" "J" (at 6 5) (layer "F.SilkS") (uuid "%s") (effects (font (size 1 1) (thickness 0.15))))' % U(),
    f'\t(property "Value" "{NAME}" (at 31.75 40) (layer "F.Fab") (uuid "%s") (effects (font (size 1 1) (thickness 0.15))))' % U(),
    '\t(property "Datasheet" "" (at 0 0) (layer "F.Fab") (hide yes) (uuid "%s") (effects (font (size 1.27 1.27) (thickness 0.15))))' % U(),
    '\t(property "Description" "" (at 0 0) (layer "F.Fab") (hide yes) (uuid "%s") (effects (font (size 1.27 1.27) (thickness 0.15))))' % U(),
    "\t(attr through_hole)",
]
stroke = '(stroke (width 0.05) (type solid))'
for kind, a, m, b in outline:
    A, B = kc(a), kc(b)
    if kind == "line":
        lines.append(f'\t(fp_line (start {f(A[0])} {f(A[1])}) (end {f(B[0])} {f(B[1])}) {stroke} (layer "Edge.Cuts") (uuid "{U()}"))')
    else:
        M = kc(m)
        lines.append(f'\t(fp_arc (start {f(A[0])} {f(A[1])}) (mid {f(M[0])} {f(M[1])}) (end {f(B[0])} {f(B[1])}) {stroke} (layer "Edge.Cuts") (uuid "{U()}"))')

# header outlines on F.Fab and silkscreen pin-1 marks
for name, ylow in (("H1", 3.275), ("H2", 3.475)):
    x1, y1 = kc((0.500 * IN, (ylow + 0.150) * IN))
    x2, y2 = kc((3.100 * IN, (ylow - 0.050) * IN))
    lines.append(f'\t(fp_rect (start {f(x1)} {f(y1)}) (end {f(x2)} {f(y2)}) (stroke (width 0.1) (type solid)) (fill no) (layer "F.Fab") (uuid "{U()}"))')
    # H1 below its lower row; H2 above its upper row, between the top-left hole and the top notch
    tx, ty = kc((0.550 * IN, 3.180 * IN)) if name == "H1" else kc((0.650 * IN, 3.680 * IN))
    lines.append(f'\t(fp_text user "{name}" (at {f(tx)} {f(ty)}) (layer "F.SilkS") (uuid "{U()}") (effects (font (size 1 1) (thickness 0.15)) (justify left)))')

pad_report = []
for n in range(1, 105):
    hdr, k = divmod(n - 1, 52)
    col, odd = k // 2, k % 2 == 0
    y = (3.275 if hdr == 0 else 3.475) + (0 if odd else 0.100)
    x = 0.550 + 0.100 * col
    X, Y = kc((x * IN, y * IN))
    shape = "rect" if k == 0 else "circle"
    lines.append(f'\t(pad "{n}" thru_hole {shape} (at {f(X)} {f(Y)}) (size 1.6 1.6) (drill 1.016) (layers "*.Cu" "*.Mask") (remove_unused_layers no) (uuid "{U()}"))')
for h in holes:
    X, Y = kc(h)
    room = edge_dist(h)
    if room - 6.35 / 2 >= 1.27:
        lines.append(f'\t(pad "" thru_hole circle (at {f(X)} {f(Y)}) (size 6.35 6.35) (drill 3.18) (layers "*.Cu" "*.Mask") (remove_unused_layers no) (uuid "{U()}"))')
        pad_report.append((h, room, "plated, 6.35 mm pad"))
    else:
        lines.append(f'\t(pad "" np_thru_hole circle (at {f(X)} {f(Y)}) (size 3.18 3.18) (drill 3.18) (layers "*.Cu" "*.Mask") (uuid "{U()}"))')
        pad_report.append((h, room, "NPTH, no pad"))

def rule_area(ch, label, layers, footprints_side):
    pts = [kc(spec(p)) for p in D.polyline(es, ch)][:-1]
    xy = " ".join(f"(xy {f(x)} {f(y)})" for x, y in pts)
    lay = " ".join(f'"{l}"' for l in layers)
    return (f'\t(zone (layers {lay}) (uuid "{U()}") (name "{label}") (hatch edge 0.5) (connect_pads (clearance 0)) (min_thickness 0.25) '
            f'(keepout (tracks allowed) (vias allowed) (pads allowed) (copperpour allowed) (footprints not_allowed)) '
            f'(placement (enabled no) (sheetname "")) (fill (thermal_gap 0.5) (thermal_bridge_width 0.5) (island_removal_mode 0)) '
            f'(polygon (pts {xy})))')

areas = []
for ch in closed:
    pts = [spec(p) for p in D.polyline(es, ch)]
    xs = [p[0] for p in pts]
    if max(xs) <= 90.18 and min(xs) > 80:
        areas.append(rule_area(ch, "CSK no parts (traces OK)", ["F.Cu"], "F"))
    elif min(xs) > 85:
        areas.append(rule_area(ch, "CSK clearance for separation switch 1", ["F.Cu", "B.Cu"], "both"))
    else:
        areas.append(rule_area(ch, "CSK clearance for separation switch 2", ["F.Cu", "B.Cu"], "both"))
lines += areas
lines.append('\t(embedded_fonts no)')
lines.append(")")
open(out, "w").write("\n".join(lines) + "\n")

xs = [p for e in outline for p in (e[1], e[3])]
print(f"outline: {len(outline)} edges ({sum(1 for e in outline if e[0]=='arc')} arcs), x {min(p[0] for p in xs):.3f}..{max(p[0] for p in xs):.3f}, y {min(p[1] for p in xs):.3f}..{max(p[1] for p in xs):.3f} mm (spec frame)")
for h, room, what in pad_report:
    print(f"hole at ({h[0]:.3f}, {h[1]:.3f}) mm: {room:.3f} mm from the edge -> {what}")
print(f"rule areas: {len(areas)}; pads: 104 + {len(holes)} holes")
