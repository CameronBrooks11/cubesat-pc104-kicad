# Library

The `CubeSat_PC104` library: one symbol file, `CubeSat_PC104.kicad_sym`, and
one footprint folder, `CubeSat_PC104.pretty`. In the repository they are in
`library/`; on the
[releases page](https://github.com/CameronBrooks11/cubesat-pc104-kicad/releases)
they are `CubeSat_PC104-<version>.zip`.
[Getting started](getting-started.md#add-the-library-to-an-existing-project)
shows how to add them to a project.

The library is named for the form factor; its parts are named for the CubeSat
Kit specification they follow, hence `CSK_`.

| Part | Kind | What it is |
| --- | --- | --- |
| [`CSK_PC104_Slot0`](#csk_pc104_slot0) | Footprint | A whole Slot 0 board: outline, bus headers, mounting holes, keepouts |
| [`CSK_PC104_Slot1`](#csk_pc104_slot1) | Footprint | A whole Slot 1 board: outline, bus headers, mounting holes |
| [`CSK_PC104_Bus`](#csk_pc104_bus) | Footprint | The bus header pads alone |
| [`CSK_Bus`](#csk_bus) | Symbol | The 104 bus pins, named by signal |
| [`SUCHAI_Payload`](#suchai_payload) | Symbol | The bus as the SUCHAI 2 and 3 payloads use it |

Both symbols use the same pin numbers as the footprints: H1 is pins 1 to 52,
H2 is pins 53 to 104, odd pins on one row and even on the other as on the
header. Either symbol fits any of the three footprints.

## Footprints

### `CSK_PC104_Slot0`

A CubeSat Kit user module in the base "Slot 0" pattern: the board outline on
`Edge.Cuts`, the H1 and H2 2×26 headers on the 2.54 mm grid, four mounting
holes, and rule areas that keep footprints off the right-edge patch and the
separation-switch clearances. The origin is H1 pin 1.

![CSK_PC104_Slot0 footprint](renders/CSK_PC104_Slot0.svg){ .plot width="480" }

The keepouts are rule areas, so they appear in the board editor but not in
this plot. [Stack and mechanical](mechanical.md#against-the-specification)
lists where the footprint departs from the specification's drawing.

### `CSK_PC104_Slot1`

The same headers and holes in the extended "Slot 1" pattern: a full
bottom-left corner and no keepouts.

![CSK_PC104_Slot1 footprint](renders/CSK_PC104_Slot1.svg){ .plot width="480" }

### `CSK_PC104_Bus`

The H1 and H2 pads alone, placed exactly as on `CSK_PC104_Slot0`, with no
outline or holes. Use it for a second bus connector on a board, as the
[bus breakout](breakout.md) does, or to put the bus on a board whose outline
you draw yourself.

![CSK_PC104_Bus footprint](renders/CSK_PC104_Bus.svg){ .plot width="480" }

## Symbols

### `CSK_Bus`

The bus for any module. Unit A is H1, unit B is H2. Every pin is passive and
named by its CubeSat Kit bus signal; [Bus pinout](pinout.md) lists them and
where the names come from. Its footprint field defaults to `CSK_PC104_Slot0`.

<div class="grid" markdown>

![CSK_Bus unit A, H1](renders/CSK_Bus_unit1.svg){ .plot }

![CSK_Bus unit B, H2](renders/CSK_Bus_unit2.svg){ .plot }

</div>

Passive pins never trip ERC's driver checks, whatever a module connects. The
bus's direction depends on the module: `IO.0` is an output on one board and an
input on the next.

### `SUCHAI_Payload`

The same two units with the SUCHAI 2 and 3 payload's own names and electrical
types: power pins are power inputs, UART and I²C pins have directions. Pins
the payload does not use keep their `CSK_Bus` names and stay passive.
[SUCHAI payload](suchai.md) lists its pins.

<div class="grid" markdown>

![SUCHAI_Payload unit A, H1](renders/SUCHAI_Payload_unit1.svg){ .plot }

![SUCHAI_Payload unit B, H2](renders/SUCHAI_Payload_unit2.svg){ .plot }

</div>

## How the library is made

None of the parts is drawn by hand. `tools/genfp.py` generates the two board
footprints from the specification's DXF drawings, `tools/genbus.py` cuts
`CSK_PC104_Bus` from `CSK_PC104_Slot0`, and `tools/gensym.py` writes both
symbols from the pin tables `tools/csk_bus_pins.csv` and
`tools/suchai_pins.csv`. CI checks that the committed library is what the
generators produce. [Development](development.md) has the details.
