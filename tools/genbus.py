"""Generate CSK_PC104_Bus: the H1/H2 header pads of CSK_PC104_Slot0, alone.

usage: python3 tools/genbus.py KiCad/CubeSat_PC104.pretty
then:  kicad-cli fp upgrade --force KiCad/CubeSat_PC104.pretty

Takes pads 1-104, the two F.Fab header outlines and the H1/H2 silkscreen
labels from CSK_PC104_Slot0.kicad_mod, so the two footprints cannot drift
apart, and leaves out the board outline, mounting holes and keepouts. For a
second bus connector on a board, such as the one in breakout/.
"""
import os
import re
import sys
import uuid

lib = sys.argv[1]
src = open(os.path.join(lib, "CSK_PC104_Slot0.kicad_mod")).read()


def blocks(kind):
    """Top-level (kind ...) blocks of the footprint, in file order."""
    out = []
    for m in re.finditer(r"\n\t\(%s[ \n]" % re.escape(kind), src):
        depth, i = 0, m.start() + 2
        for j in range(i, len(src)):
            if src[j] == "(":
                depth += 1
            elif src[j] == ")":
                depth -= 1
                if depth == 0:
                    out.append(src[i:j + 1])
                    break
    return out


pads = [b for b in blocks("pad") if re.match(r'\(pad "\d+"', b)]
assert len(pads) == 104, len(pads)
fab = [b for b in blocks("fp_rect") if '(layer "F.Fab")' in b]
assert len(fab) == 2, len(fab)
labels = [b for b in blocks("fp_text") if re.match(r'\(fp_text user "H[12]"', b)]
assert len(labels) == 2, len(labels)


def fresh(b):
    return re.sub(r'\(uuid "[^"]+"\)', lambda _: f'(uuid "{uuid.uuid4()}")', b)


def prop(name, value, x, y, layer, hide=False):
    h = "(hide yes) " if hide else ""
    return (f'\t(property "{name}" "{value}" (at {x} {y} 0) (layer "{layer}") {h}(uuid "{uuid.uuid4()}")'
            ' (effects (font (size 1 1) (thickness 0.15))))')


parts = [
    '(footprint "CSK_PC104_Bus"',
    "\t(version 20260206)",
    '\t(generator "pcbnew")',
    '\t(generator_version "10.0")',
    '\t(layer "F.Cu")',
    '\t(descr "CubeSat Kit bus headers H1 and H2 (2x26 each, 0.1 in grid) as on CSK_PC104_Slot0, without the board outline, holes or keepouts. Origin at H1 pin 1.")',
    '\t(tags "CubeSat PC104 CSK H1 H2 bus header")',
    prop("Reference", "J", 6, -12, "F.SilkS"),
    prop("Value", "CSK_PC104_Bus", 31.75, 3, "F.Fab"),
    prop("Datasheet", "", 0, 0, "F.Fab", hide=True),
    prop("Description", "", 0, 0, "F.Fab", hide=True),
    "\t(attr through_hole)",
]
parts += ["\t" + fresh(b) for b in fab + labels + pads]
parts += ["\t(embedded_fonts no)", ")"]
out = os.path.join(lib, "CSK_PC104_Bus.kicad_mod")
open(out, "w").write("\n".join(parts) + "\n")
print(f"wrote {out}: {len(pads)} pads")
