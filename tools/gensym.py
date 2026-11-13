"""Generate KiCad/CubeSat_PC104.kicad_sym.

usage: python3 tools/gensym.py KiCad/CubeSat_PC104.kicad_sym
then:  kicad-cli sym upgrade --force KiCad/CubeSat_PC104.kicad_sym

Both symbols have two units, H1 (pins 1-52) and H2 (pins 53-104), with odd
pins on the left and even on the right as on the header, numbered as on the
CSK_PC104_* footprints.

- CSK_Bus: every pin passive, named H1.n / H2.n.
- SUCHAI_Payload: names and electrical types from tools/suchai_pins.csv;
  pins the table leaves unnamed are passive and named like CSK_Bus's.

The file is written in KiCad's 20211014 format; `sym upgrade` saves it in
the current one.
"""
import csv
import os
import sys

FP = "CubeSat_PC104:CSK_PC104_Slot0"
HERE = os.path.dirname(os.path.abspath(__file__))


def prop(name, value, x, y, pid, hide=False):
    h = " hide" if hide else ""
    return (f'    (property "{name}" "{value}" (id {pid}) (at {x} {y} 0)\n'
            f'      (effects (font (size 1.27 1.27)){h})\n    )')


def symbol(name, ref, keywords, description, pins, half_width):
    """pins: {number: (name, type)} for 1..104."""
    edge = half_width + 3.81
    out = [f'  (symbol "{name}" (pin_names (offset 1.016)) (in_bom yes) (on_board yes)',
           prop("Reference", ref, 0, 36.83, 0),
           prop("Value", name, 0, -35.56, 1),
           prop("Footprint", FP, 0, -38.1, 2, hide=True),
           prop("Datasheet", "", 0, 0, 3, hide=True),
           prop("ki_keywords", keywords, 0, 0, 4, hide=True),
           prop("ki_description", description, 0, 0, 5, hide=True)]
    for unit, base in ((1, 0), (2, 52)):
        out.append(f'    (symbol "{name}_{unit}_1"')
        out.append(f'      (rectangle (start -{half_width} 34.29) (end {half_width} -34.29)'
                   ' (stroke (width 0.254) (type default)) (fill (type background)))')
        for k in range(52):
            number = base + k + 1
            pname, ptype = pins[number]
            y = 31.75 - 2.54 * (k // 2)
            x, ang = (-edge, 0) if k % 2 == 0 else (edge, 180)
            out.append(f'      (pin {ptype} line (at {x:.2f} {y:.2f} {ang}) (length 3.81)\n'
                       f'        (name "{pname}" (effects (font (size 1.016 1.016))))\n'
                       f'        (number "{number}" (effects (font (size 1.016 1.016))))\n      )')
        out.append("    )")
    out.append("  )")
    return "\n".join(out)


def bus_name(number):
    return f"H1.{number}" if number <= 52 else f"H2.{number - 52}"


def suchai_pins():
    pins = {}
    with open(os.path.join(HERE, "suchai_pins.csv"), newline="") as f:
        for row in csv.DictReader(f):
            n = int(row["pin"])
            pins[n] = (row["signal"] or bus_name(n), row["type"])
    assert sorted(pins) == list(range(1, 105)), "suchai_pins.csv must list pins 1-104 once each"
    return pins


def main(out):
    generic = {n: (bus_name(n), "passive") for n in range(1, 105)}
    text = "\n".join([
        "(kicad_symbol_lib (version 20211014) (generator kicad_symbol_editor)",
        symbol("CSK_Bus", "J", "CubeSat Kit PC104 bus H1 H2 header",
               "CubeSat Kit bus: H1 and H2 2x26 headers, pins numbered as on the CSK_PC104 footprints"
               " (H1 = 1-52, H2 = 53-104)", generic, 7.62),
        symbol("SUCHAI_Payload", "J", "CubeSat Kit PC104 bus SUCHAI payload",
               "SUCHAI 2 and 3 payload pinout on the CubeSat Kit H1 and H2 headers"
               " (H1 = 1-52, H2 = 53-104)", suchai_pins(), 10.16),
        ")\n"])
    open(out, "w").write(text)
    print("wrote", out)


if __name__ == "__main__":
    main(sys.argv[1])
