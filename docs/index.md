# cubesat-pc104-kicad

KiCad parts and boards for CubeSat Kit modules on the PC/104 form factor: two
2×26 stack headers (H1 and H2) and four mounting holes on a 90.17 mm ×
95.89 mm board.

![Slot 0 template, top view](renders/Slot0_top.png){ width="49%" }
![Bus breakout, top view](renders/breakout_top.png){ width="49%" }

The footprints are generated from, and checked against, Pumpkin's *CubeSat Kit
PCB Specification* (810-00253 rev B2). The symbols name every pin by its
CubeSat Kit bus signal. Two project templates and a finished 4-layer example
board are built from the library, and each passes DRC and ERC in KiCad 10.

## What is here

| Page | What it covers |
| --- | --- |
| [**Library**](library.md) | The `CubeSat_PC104` symbol and footprint library: both board patterns, a bare bus connector, the bus symbol and the SUCHAI payload symbol. |
| [**Templates**](templates.md) | Two KiCad project templates, one per board pattern: start a module from one and wire the pins you use. |
| [**Bus breakout**](breakout.md) | A finished board that carries every bus pin to a second connector on the bottom, with fabrication files ready to order. |
| [**Bus pinout**](pinout.md) | The signal on each of the 104 bus pins. |

## Start here

- **Starting a new module?** [Create a project from a template](getting-started.md#start-a-module-from-a-template).
- **Adding the bus to a board you already have?** [Add the library to a project](getting-started.md#add-the-library-to-an-existing-project).
- **Choosing connectors and spacing for a stack?** See [Stack and mechanical](mechanical.md).

Everything needs KiCad 10 and is tested with 10.0.6. Downloads are on the
[releases page](https://github.com/CameronBrooks11/cubesat-pc104-kicad/releases).

## Credits and licence

The SUCHAI payload pinout is from SPEL at the Universidad de Chile,
[spel-uchile/Payload-PC104](https://github.com/spel-uchile/Payload-PC104)
(matvidal, EliasObreque and Alex Becerra, 2018 to 2022). This project began as
a KiCad import of their Eagle stack breakout; that board and the Eagle files
were removed when the library, templates and breakout were redone, and remain
in the repository's history under SPEL's GPL-3.0.

The CubeSat Kit is Pumpkin, Inc.'s. PC/104 is a standard of the
[RMS Consortium](https://www.rmsconsortium.org/), formerly the PC/104
Consortium. This project is not affiliated with either.

The library, templates and breakout are under
[CERN-OHL-P-2.0](https://github.com/CameronBrooks11/cubesat-pc104-kicad/blob/main/LICENSE),
a permissive open-hardware licence: use and modify them in your own boards,
open or closed, without sharing your design, and keep the licence notice with
any copy of these files.
