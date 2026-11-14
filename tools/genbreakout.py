"""Generate breakout/: a 4-layer CubeSat Kit bus breakout board.

usage: python3 tools/genbreakout.py
then:  kicad-cli sch upgrade --force breakout/CSK_Bus_Breakout.kicad_sch
       kicad-cli pcb drc --refill-zones --save-board ... breakout/CSK_Bus_Breakout.kicad_pcb

Starts from templates/CubeSat_PC104_Slot0 (Slot 0 outline, J1 on the stack
position) and adds J2, a second H1/H2 header pair (CSK_PC104_Bus) mounted on
the bottom 38.1 mm below J1, joined to J1 pin for pin.

Routing: mounting J2 on the bottom mirrors its rows, so in each of the 26
columns the four J1-J2 tracks nest. H1's odd row (nearest J2) drops straight
down on F.Cu. The other three rows leave their pads at 45 degrees into the gap
right of their column and run down it, one per layer: H1 even on F.Cu, H2 odd
on In2.Cu, H2 even on B.Cu. No vias. In1.Cu is a ground plane on the bus
ground pins H2.29, H2.30 and H2.32 (net GND); every other net is named after
its pin, H1.1 to H2.52 (/H1.1 on the board, as KiCad names a root-sheet label).
"""
import json
import os
import re
import shutil
import uuid

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TPL = os.path.join(ROOT, "templates", "CubeSat_PC104_Slot0")
OUT = os.path.join(ROOT, "breakout")
NAME = "CSK_Bus_Breakout"
TPL_NAME = "CubeSat_PC104_Slot0"
PITCH = 2.54
DROP = 15 * PITCH            # J2's H1 pin 1 sits this far below J1's
TRACK = 0.25
GND_PINS = {81, 82, 84}      # H2.29, H2.30, H2.32
TITLE_BLOCK = '(title_block (title "CSK bus breakout") (rev "1.0") (comment 1 "J2 (bottom) carries J1 pin for pin"))'
# A3 schematic layout: the four units on one row, centred in the space above the title block
SHEET_Y = 129.54
SHEET_AT = {("J1", 1): (86.36, SHEET_Y), ("J1", 2): (162.56, SHEET_Y),
            ("J2", 1): (264.16, SHEET_Y), ("J2", 2): (340.36, SHEET_Y)}
SHEET_PAIR_AT = {"J1": (124.46, SHEET_Y - 43.18), "J2": (302.26, SHEET_Y - 43.18)}
SHEET_NOTE_AT = (63.5, 50.8)
ROW_LAYER = {0: "F.Cu", 1: "F.Cu", 2: "In2.Cu", 3: "B.Cu"}


def U():
    return str(uuid.uuid4())


def net(pin):
    if pin in GND_PINS:
        return "GND"
    return f"H1.{pin}" if pin <= 52 else f"H2.{pin - 52}"


def board_net(pin):
    """Local labels on the root sheet name their nets with a leading slash."""
    return "/" + net(pin)


def pin_place(pin):
    """Column and row (0 = H1 odd, 1 = H1 even, 2 = H2 odd, 3 = H2 even) of a bus pin."""
    k = (pin - 1) % 52
    return k // 2, (0 if pin <= 52 else 2) + k % 2


def f(v):
    return f"{v:.4f}".rstrip("0").rstrip(".")


def block_at(text, start):
    depth = 0
    for j in range(start, len(text)):
        if text[j] == "(":
            depth += 1
        elif text[j] == ")":
            depth -= 1
            if depth == 0:
                return text[start:j + 1]
    raise ValueError("unbalanced")


# ---------------------------------------------------------------- schematic
def schematic(tpl_root, new_root):
    s = open(os.path.join(TPL, TPL_NAME + ".kicad_sch")).read()
    s = s.replace(tpl_root, new_root).replace(f'(project "{TPL_NAME}"', f'(project "{NAME}"')
    s = s.replace('(paper "A4")', '(paper "A3")\n' + TITLE_BLOCK, 1)
    syms = [m.start() + 1 for m in re.finditer(r"\n\t\(symbol\n\t\t\(lib_id", s)]
    units = {}
    for st in syms:
        b = block_at(s, st)
        unit = int(re.search(r"\(unit (\d)\)", b).group(1))
        units[unit] = b
    assert sorted(units) == [1, 2], units.keys()

    def moved(block, to):
        x, y = map(float, re.search(r"\(at ([-\d.]+) ([-\d.]+) 0\)", block).groups())
        dx, dy = to[0] - x, to[1] - y
        return re.sub(r"\(at ([-\d.]+) ([-\d.]+) (\d+)\)",
                      lambda m: f"(at {f(float(m[1]) + dx)} {f(float(m[2]) + dy)} {m[3]})", block)

    new_blocks = []
    j2a_uuid = None
    for unit, b in sorted(units.items()):
        s = s.replace(b, moved(b, SHEET_AT[("J1", unit)]), 1)
        c = b.replace('(property "Reference" "J1"', '(property "Reference" "J2"').replace('(reference "J1")', '(reference "J2")')
        c = c.replace('"CubeSat_PC104:CSK_PC104_Slot0"', '"CubeSat_PC104:CSK_PC104_Bus"')
        c = moved(c, SHEET_AT[("J2", unit)])
        c = re.sub(r'\(uuid "[^"]+"\)', lambda _: f'(uuid "{U()}")', c)
        if unit == 1:
            j2a_uuid = re.search(r'\(uuid "([^"]+)"\)', c).group(1)
        new_blocks.append(c)
    placed = SHEET_AT

    # The template's note tells a module designer to wire the bus; this board's notes say what it is.
    note = re.search(r'\n\t\(text "CubeSat Kit bus.*?\n\t\)', s, re.S)
    assert note, "template note not found"
    texts = [
        (SHEET_NOTE_AT, "left", "Every J1 bus pin is carried to the same pin of J2. Nets are named after the pin, H1.1 to H2.52;\\n"
                                "H2.29, H2.30 and H2.32 are GND, joined to the In1.Cu plane.\\n"
                                "Board: CubeSat Kit Slot 0 per Pumpkin 810-00253 rev B2, 4 layers, copper to edge clearance 1.27 mm."),
        (SHEET_PAIR_AT["J1"], "center", "J1: stack connector (CSK_PC104_Slot0), top side"),
        (SHEET_PAIR_AT["J2"], "center", "J2: second H1/H2 header pair (CSK_PC104_Bus), bottom side, 38.1 mm below J1"),
    ]
    blocks = []
    for (x, y), just, text in texts:
        j = "(justify left bottom)" if just == "left" else "(justify bottom)"
        blocks.append(f'\t(text "{text}" (exclude_from_sim no) (at {f(x)} {f(y)} 0)\n'
                      f'\t\t(effects (font (size 1.27 1.27)) {j})\n\t\t(uuid "{U()}")\n\t)')
    s = s[:note.start()] + "\n" + "\n".join(blocks) + s[note.end():]
    labels = []
    for (ref, unit), (x, y) in sorted(placed.items()):
        for k in range(52):
            pin = (unit - 1) * 52 + k + 1
            lx = -11.43 if k % 2 == 0 else 11.43
            ly = 31.75 - PITCH * (k // 2)
            ang, just = (180, "right") if lx < 0 else (0, "left")
            labels.append(f'\t(label "{net(pin)}" (at {f(x + lx)} {f(y - ly)} {ang}) (fields_autoplaced yes)\n'
                          f'\t\t(effects (font (size 1.27 1.27)) (justify {just} bottom))\n\t\t(uuid "{U()}")\n\t)')
    anchor = "\t(sheet_instances"
    assert s.count(anchor) == 1
    s = s.replace(anchor, "\n".join(new_blocks) + "\n" + "\n".join(labels) + "\n" + anchor)
    return s, j2a_uuid, len(labels)


# -------------------------------------------------------------------- board
STACKUP = """\t\t(stackup
\t\t\t(layer "F.SilkS" (type "Top Silk Screen") (color "White"))
\t\t\t(layer "F.Paste" (type "Top Solder Paste"))
\t\t\t(layer "F.Mask" (type "Top Solder Mask") (color "Green") (thickness 0.01) (epsilon_r 3.3) (loss_tangent 0))
\t\t\t(layer "F.Cu" (type "copper") (thickness 0.035))
\t\t\t(layer "dielectric 1" (type "prepreg") (thickness 0.48) (material "FR4") (epsilon_r 4.5) (loss_tangent 0.02))
\t\t\t(layer "In1.Cu" (type "copper") (thickness 0.035))
\t\t\t(layer "dielectric 2" (type "core") (thickness 0.48) (material "FR4") (epsilon_r 4.5) (loss_tangent 0.02))
\t\t\t(layer "In2.Cu" (type "copper") (thickness 0.035))
\t\t\t(layer "dielectric 3" (type "prepreg") (thickness 0.48) (material "FR4") (epsilon_r 4.5) (loss_tangent 0.02))
\t\t\t(layer "B.Cu" (type "copper") (thickness 0.035))
\t\t\t(layer "B.Mask" (type "Bottom Solder Mask") (color "Green") (thickness 0.01) (epsilon_r 3.3) (loss_tangent 0))
\t\t\t(layer "B.Paste" (type "Bottom Solder Paste"))
\t\t\t(layer "B.SilkS" (type "Bottom Silk Screen") (color "White"))
\t\t\t(copper_finish "None")
\t\t\t(dielectric_constraints no)
\t\t)
"""


def flipped_footprint(lib_text, at, ref, value, path_uuid):
    """A library footprint as placed on the bottom at rotation 0: local y negated, F layers to B, text mirrored."""
    t = lib_text
    t = re.sub(r'^\(footprint "([^"]+)"', r'(footprint "CubeSat_PC104:\1"', t)
    t = re.sub(r'\n\t\((version|generator|generator_version) [^\n]*', "", t)
    t = t.replace('(property "Reference" "J"', f'(property "Reference" "{ref}"', 1)
    t = re.sub(r'\(property "Value" "[^"]*"', f'(property "Value" "{value}"', t, count=1)
    t = re.sub(r"\((at|start|end) ([-\d.]+) ([-\d.]+)", lambda m: f"({m[1]} {m[2]} {f(-float(m[3]) + 0.0)}", t)
    t = t.replace('\n\t(layer "F.Cu")', f'\n\t(layer "B.Cu")\n\t(uuid "{U()}")\n\t(at {f(at[0])} {f(at[1])})', 1)
    t = t.replace('(layer "F.SilkS")', '(layer "B.SilkS")').replace('(layer "F.Fab")', '(layer "B.Fab")')
    t = t.replace("(justify left)", "(justify left mirror)")
    t = re.sub(r"(\t\t\t\)\n)(\t\t\)\n\t\))", lambda m: m[1] + "\t\t\t(justify mirror)\n" + m[2], t)
    t = re.sub(r'(\(pad "(\d+)"[^\n]*\n(?:\t\t[^\n]*\n)*?)(\t\t\(uuid)', lambda m: m[1] + f'\t\t(net "{board_net(int(m[2]))}")\n' + m[3], t)
    t = t.replace("\t(attr through_hole)", f'\t(path "/{path_uuid}")\n\t(sheetname "/")\n\t(sheetfile "{NAME}.kicad_sch")\n\t(attr through_hole)', 1)
    return "\n".join("\t" + line for line in t.rstrip("\n").split("\n"))


def board(j2a_uuid):
    b = open(os.path.join(TPL, TPL_NAME + ".kicad_pcb")).read()
    fx, fy = map(float, re.search(r'\(footprint "CubeSat_PC104:CSK_PC104_Slot0"\n\t\t\(layer "F.Cu"\)\n\t\t\(uuid "[^"]+"\)\n\t\t\(at ([-\d.]+) ([-\d.]+)\)', b).groups())
    b = b.replace(f'(sheetfile "{TPL_NAME}.kicad_sch")', f'(sheetfile "{NAME}.kicad_sch")')
    b = b.replace('\t\t(0 "F.Cu" signal)\n', '\t\t(0 "F.Cu" signal)\n\t\t(4 "In1.Cu" signal)\n\t\t(6 "In2.Cu" signal)\n', 1)
    assert "(stackup" not in b and "(title_block" not in b
    b = b.replace('\t(paper "A4")\n', '\t(paper "A4")\n\t' + TITLE_BLOCK + '\n', 1)
    b = b.replace("\t(setup\n", "\t(setup\n" + STACKUP, 1)
    b, n = re.subn(r'\(net "unconnected-\(J1[AB]-[^)]*-Pad(\d+)\)"\)', lambda m: f'(net "{board_net(int(m[1]))}")', b)
    assert n == 104, n

    lib = open(os.path.join(ROOT, "KiCad", "CubeSat_PC104.pretty", "CSK_PC104_Bus.kicad_mod")).read()
    items = [flipped_footprint(lib, (fx, fy + DROP), "J2", "CSK_Bus", j2a_uuid)]

    seg = lambda a, c, layer, nn: (f'\t(segment (start {f(a[0])} {f(a[1])}) (end {f(c[0])} {f(c[1])}) '
                                   f'(width {TRACK}) (layer "{layer}") (net "{nn}") (uuid "{U()}"))')
    count = 0
    for pin in range(1, 105):
        col, row = pin_place(pin)
        x = fx + PITCH * col
        y1, y2 = fy - PITCH * row, fy + DROP + PITCH * row
        layer, nn = ROW_LAYER[row], board_net(pin)
        if row == 0:
            pts = [(x, y1), (x, y2)]
        else:
            g = x + PITCH / 2
            pts = [(x, y1), (g, y1 + PITCH / 2), (g, y2 - PITCH / 2), (x, y2)]
        for a, c in zip(pts, pts[1:]):
            items.append(seg(a, c, layer, nn))
            count += 1

    # In1.Cu ground plane over the whole board; the fill follows the edge clearance
    x0, y0, x1, y1 = fx - 13.97 - 2, fy - 12.7 - 2, fx + 76.2 + 2, fy + 83.185 + 2
    items.append(f'\t(zone (net "/GND") (layer "In1.Cu") (uuid "{U()}") (name "GND plane") (hatch edge 0.5) '
                 f'(connect_pads (clearance 0.2)) (min_thickness 0.25) (filled_areas_thickness no) '
                 f'(fill yes (thermal_gap 0.5) (thermal_bridge_width 0.5)) '
                 f'(polygon (pts (xy {f(x0)} {f(y0)}) (xy {f(x1)} {f(y0)}) (xy {f(x1)} {f(y1)}) (xy {f(x0)} {f(y1)}))))')
    items.append(f'\t(gr_text "CSK BUS BREAKOUT\\nJ2 (BACK) = J1, PIN FOR PIN" (at {f(fx + 31.75)} {f(fy + 62)} 0) '
                 f'(layer "F.SilkS") (uuid "{U()}") (effects (font (size 1.5 1.5) (thickness 0.2))))')
    end = b.rstrip().rfind(")")
    b = b[:end] + "\n".join(items) + "\n)\n"
    return b, count


def project(tpl_root, new_root):
    d = json.load(open(os.path.join(TPL, TPL_NAME + ".kicad_pro")))
    d["meta"]["filename"] = NAME + ".kicad_pro"
    d["sheets"] = [[new_root, "Root"]]
    d["schematic"]["top_level_sheets"] = [{"filename": NAME + ".kicad_sch", "name": NAME, "uuid": new_root}]
    return json.dumps(d, indent=2) + "\n"


def main():
    s = open(os.path.join(TPL, TPL_NAME + ".kicad_sch")).read()
    tpl_root = re.search(r'\(uuid "([^"]+)"\)', s).group(1)
    new_root = U()
    os.makedirs(OUT, exist_ok=True)
    sch, j2a, nlabels = schematic(tpl_root, new_root)
    open(os.path.join(OUT, NAME + ".kicad_sch"), "w").write(sch)
    pcb, nseg = board(j2a)
    open(os.path.join(OUT, NAME + ".kicad_pcb"), "w").write(pcb)
    open(os.path.join(OUT, NAME + ".kicad_pro"), "w").write(project(tpl_root, new_root))
    for name in ("fp-lib-table", "sym-lib-table"):
        shutil.copy(os.path.join(TPL, name), OUT)
    print(f"wrote {OUT}: {nlabels} labels, {nseg} track segments")


if __name__ == "__main__":
    main()
