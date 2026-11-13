# cubesat-pc104-kicad

KiCad parts and boards for CubeSat modules on the PC/104 form factor: two 2×26
stack headers (H1 and H2) and four mounting holes.

Work in progress. Nothing here has been checked against the PC/104 or CubeSat
Kit drawings yet.

## Contents

| Path | What it is |
| --- | --- |
| `KiCad/Payload/` | A symbol with the SUCHAI 2 and 3 bus pinout and the `PC104-Standard` footprint: both headers, the mounting holes and a board outline with room for cables. |
| `PC104/` | The 4-layer stack breakout board in KiCad, imported from the Eagle design below. It carries every bus pin from the stack headers to a second pair of headers 16.9 mm over. |
| `Eagle/` | The original Eagle libraries and stack breakout boards, with and without extra connectors. |
| `img/` | The schematic and 3D view of the payload template. |

![Payload schematic](img/KiCAD_schematic.png)
![Payload footprint in 3D](img/KiCAD_3D_view.png)

## Status

The stack breakout board in `PC104/`, opened in KiCad 10.0.6:

- Its connections match the schematic: the board and the schematic group the
  same pads into the same 99 nets. The board's nets still carry Eagle's names,
  so the schematic parity check lists 199 name mismatches.
- With the zones filled, DRC finds three nets each routed in two halves:
  stack pins 25 and 26 (5V0), 27 and 28 (3V3) and 45 and 46 (V_BAT) are not
  joined on the board.
- One track crosses a keep-out area, and the imported silkscreen text is
  thinner than the board's minimum.

Planned: fix the board, give the symbols the right pin types and link them to
the footprint, add a generic H1/H2 header symbol beside the SUCHAI one, check
the footprint against the CubeSat Kit dimensions, and add a project template.

## Credits

The library, the Eagle designs and the payload template are by SPEL at the
Universidad de Chile, from
[spel-uchile/Payload-PC104](https://github.com/spel-uchile/Payload-PC104)
(matvidal, EliasObreque and Alex Becerra, 2018 to 2022). Its history is kept
in this repository; the KiCad import of the stack breakout board is from 2024. Derived from, although not affiliated with,
[pc104.org](https://pc104.org/).

## License

GPL-3.0, as published by SPEL. See [LICENSE](./LICENSE).
