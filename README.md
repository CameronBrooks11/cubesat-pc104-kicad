# cubesat-pc104-kicad

KiCad parts and boards for CubeSat Kit modules on the PC/104 form factor: two
2×26 stack headers (H1 and H2) and four mounting holes.

The library is generated from, and checked against, the CubeSat Kit
specification. Two project templates and a worked 4-layer example board are
built from it.

## Releases

Each [release](https://github.com/CameronBrooks11/cubesat-pc104-kicad/releases)
carries:

| Asset | Contents |
| --- | --- |
| `CubeSat_PC104-<version>.zip` | The symbol and footprint library, to add to any project |
| `cubesat-pc104-templates-<version>.zip` | Both project templates |
| `CSK_Bus_Breakout-<version>.zip` | The breakout board's KiCad project |
| `CSK_Bus_Breakout-fab-<version>.zip` | The breakout's Gerbers and drill files, ready to order |

Changes are listed in [CHANGELOG.md](CHANGELOG.md). Everything needs KiCad 10.

## Project templates

KiCad 10 project templates for a CubeSat Kit user module: the board outline, the
H1/H2 bus as connector J1 and the mounting holes, with copper kept 1.27 mm from
the edge. Each passes DRC with schematic parity; ERC lists the 104 bus pins as
unconnected until you wire them or flag them.

| Template | Pattern |
| --- | --- |
| [`templates/CubeSat_PC104_Slot0`](templates/CubeSat_PC104_Slot0/) | Base "Slot 0": the separation switch cutouts and keepouts. Pumpkin's example stack uses this pattern at both positions, so it is the default choice. |
| [`templates/CubeSat_PC104_Slot1`](templates/CubeSat_PC104_Slot1/) | Extended "Slot 1": the same holes and headers with a fuller bottom-left corner and no keepouts. |

<p>
  <img src="templates/CubeSat_PC104_Slot0/meta/brd.png" alt="Slot 0 template, top view" width="48%" />
  <img src="templates/CubeSat_PC104_Slot1/meta/brd.png" alt="Slot 1 template, top view" width="48%" />
</p>

1. Clone this repository, or copy a template directory out of it.
2. In KiCad choose **File → New Project from Template**, open the user
   templates tab and point it at `templates/`.
3. Pick the template and name the project. KiCad copies the files and renames
   them after the project.
4. In the schematic, wire the bus pins the module uses and put a no-connect
   flag on the others.

Each template carries its own copy of the `CubeSat_PC104` library, so a new
project needs nothing else installed.

## Stack connectors

The footprints are pads only, so either way of mounting the bus connectors fits
them; choose the parts and the side to suit the stack.

- **CubeSat Kit convention.** Each module has its sockets on the top side. A
  module that plugs onto another uses a long-tail part whose tails pass through
  the board into the sockets below: ESQ-126-39-G-D (extended tail) in Pumpkin's
  example stacks. The specification's Slot 0 sheet lists ESQ-126-37-G-D, a
  non-stack-through part. The specification gives two board spacings,
  15.24 mm to 17.00 mm, or 24.00 mm to 26.00 mm with an extra Samtec
  SSQ-126-22-G-D to span the gap, and recommends components no taller than
  13.0 mm (15.24 mm spacing) or 21.5 mm (24 mm spacing) on the top side and
  3.8 mm on the bottom.
- **Socket on the bottom.** A bottom-mounted stack-through socket such as
  Samtec SSQ-126-23-G-D (10.00 mm tails) leaves its pins standing up through
  the top. That suits a stack whose boards present pins upward, and does not
  plug into the top of a CubeSat Kit stack, whose modules present sockets.

## Library

`KiCad/CubeSat_PC104.kicad_sym` and `KiCad/CubeSat_PC104.pretty/`. Add them to
a project as the symbol and footprint libraries `CubeSat_PC104`.

| Part | What it is |
| --- | --- |
| `CSK_PC104_Slot0` (footprint) | A CubeSat Kit user module in the base "Slot 0" pattern: board outline, H1 and H2 headers, mounting holes, and keepout areas. Origin at H1 pin 1. |
| `CSK_PC104_Slot1` (footprint) | The same in the extended "Slot 1" pattern, without the 2nd switch cutout or keepouts. |
| `CSK_PC104_Bus` (footprint) | The H1 and H2 header pads alone, as on `CSK_PC104_Slot0`: for a second bus connector on a board. Generated from `CSK_PC104_Slot0` by `tools/genbus.py`. |
| `CSK_Bus` (symbol) | The bus headers for any payload: unit A is H1 (pins 1–52), unit B is H2 (pins 53–104), all passive. |
| `SUCHAI_Payload` (symbol) | The SUCHAI 2 and 3 payload pinout on the same two units, with supply pins as power inputs. Unused pins are named as on `CSK_Bus`. |

<img src="img/CSK_PC104_Slot0.png" alt="CSK_PC104_Slot0 footprint" width="400" />
<img src="img/CSK_Bus_H1.png" alt="CSK_Bus unit A, H1" height="400" />
<img src="img/SUCHAI_Payload.png" alt="SUCHAI_Payload symbol, units A and B" width="400" />

`tools/gensym.py` generates the symbol library; the SUCHAI pinout is the table
in `tools/suchai_pins.csv`.

### Against the specification

The footprints follow Pumpkin's *CubeSat Kit PCB Specification*, drawing
810-00253, revision B2 (2018-11-08). Each is generated from the drawing's DXF
for its slot by `tools/genfp.py` (see `just footprints`); the holes and all 104
pins land on the DXF's to within 0.0001 mm.
Where Slot 0 departs from the drawing:

- **Bottom-left edge.** The DXF leaves the outline open at the bottom-left hole,
  where the drawing calls for the feature that lets the 2nd separation switch
  work. It is closed along that hole's 6.35 mm pad circle.
- **Two holes without pads.** The drawing gives each hole a 6.35 mm pad and also
  recommends keeping copper 1.27 mm from the edge. At the bottom-left and
  top-right holes the edge is 3.175 mm and 3.048 mm from the hole centre, so
  both can't hold. Those two are bare 3.18 mm holes; the other two have plated
  6.35 mm pads.
- **Keepouts.** The three boxes in the DXF are rule areas that allow no
  footprints: the "no parts placed here" patch on the right edge (top side) and
  the clearances for separation switches 1 and 2 (both sides). The bottom-side
  strips where the board rests on the structure's flange are hatched in the
  drawing but not dimensioned, so they are not included.
- **Edge setback.** The drawing recommends 1.27 mm from the edge for all copper.
  That is a board setting (copper to edge clearance), not part of the footprint.

Slot 1's outline is closed in its DXF and it has no keepout boxes. Its top-right
hole is bare for the same reason as Slot 0's; the other three have plated
6.35 mm pads.

The specification documents are not in this repository.

## Bus breakout board

[`breakout/`](breakout/) is a 4-layer example board built from the Slot 0
template: J1 sits on the stack position, and J2, a second H1/H2 header pair
(`CSK_PC104_Bus`) mounted on the bottom 38.1 mm below it, carries every bus pin,
pin for pin. Use it to reach the bus from below a stack, or as a starting point
for a board that needs a second bus connector.

- **Routing.** Mounting J2 on the bottom mirrors its rows, so in each of the 26
  columns the four tracks nest without crossing: H1's odd row drops straight
  down on F.Cu, and the other three rows each take the gap beside their column
  on one layer (F.Cu, In2.Cu, B.Cu). No vias; 0.25 mm tracks, 0.2 mm
  clearance, copper 1.27 mm from the edge.
- **Ground.** In1.Cu is a plane on the bus ground pins H2.29, H2.30 and H2.32
  (net `GND`). Every other net is named after its pin, `H1.1` to `H2.52`.
- **Stackup.** Generic 1.6 mm 4-layer: 35 µm copper on all layers, FR4.
- **Checks.** In KiCad 10.0.6: ERC clean; DRC 0 violations, 0 unconnected
  items, 0 schematic parity issues.

`tools/genbreakout.py` generates it (`just breakout`), so it follows the
template and the library when they change.

<p>
  <img src="img/breakout_top.png" alt="Bus breakout, top view" width="48%" />
  <img src="img/breakout_bottom.png" alt="Bus breakout, bottom view" width="48%" />
</p>

## Development

With [just](https://just.systems/), Python 3 and KiCad 10's `kicad-cli`:

- `just check` is the gate. CI runs it in the official `kicad/kicad:10.0.6`
  image on every pull request and push to `main`. It confirms:
  - the library copy in each template and in `breakout/` matches `KiCad/`;
  - `KiCad/CubeSat_PC104.kicad_sym` is exactly what `tools/gensym.py`
    generates, and `CSK_PC104_Bus` what `tools/genbus.py` generates;
  - DRC with schematic parity is clean on both templates and the breakout;
  - ERC on each template finds nothing but the unconnected bus pins, and on
    the breakout nothing at all.
- `just footprints` regenerates both footprints from the specification's DXFs
  with `tools/genfp.py` and compares them with `KiCad/`, ignoring UUIDs. The
  DXFs ship with Pumpkin's specification and are not in this repository; put
  `CSK_PCB_Slot0_B2_20180823.DXF` and `CSK_PCB_Slot1_B2_20180823.DXF` in a
  folder and pass it as `just footprints spec=<folder>`. CI cannot run this.
- To change a footprint, edit `tools/genfp.py`, regenerate with
  `python3 tools/genfp.py <dxf> KiCad/CubeSat_PC104.pretty/<name>.kicad_mod <name>`
  and `kicad-cli fp upgrade --force KiCad/CubeSat_PC104.pretty`. To change a
  symbol, edit `tools/gensym.py` or `tools/suchai_pins.csv`, then run
  `python3 tools/gensym.py KiCad/CubeSat_PC104.kicad_sym` and
  `kicad-cli sym upgrade --force KiCad/CubeSat_PC104.kicad_sym`. Follow either
  with `just sync-template`, then `just breakout`.
- `just sync-template` copies the library into every template and `breakout/`.
- `just breakout` regenerates the breakout board and fills its ground plane.
- `just dist <version>` builds the release assets into `dist/`. Pushing a
  `v*` tag runs it in CI and publishes a GitHub release with them, using that
  version's section of `CHANGELOG.md` as the notes.
- `just fab` plots the breakout board's Gerbers and drill files into
  `fab/` and zips them, and refuses if DRC finds anything. For another board,
  `just fab board=templates/CubeSat_PC104_Slot0/CubeSat_PC104_Slot0.kicad_pcb copper=F.Cu,B.Cu`.

## Credits

The SUCHAI payload pinout is from SPEL at the Universidad de Chile,
[spel-uchile/Payload-PC104](https://github.com/spel-uchile/Payload-PC104)
(matvidal, EliasObreque and Alex Becerra, 2018 to 2022). This repository began
as a KiCad import of their Eagle stack breakout; that board and the Eagle
files were removed when the library, templates and breakout were redone, and
remain in this repository's history under SPEL's GPL-3.0.

The CubeSat Kit is Pumpkin, Inc.'s. PC/104 is a standard of the
[RMS Consortium](https://www.rmsconsortium.org/), formerly the PC/104
Consortium. This project is not affiliated with either.

## License

[CERN-OHL-P-2.0](./LICENSE): a permissive open-hardware licence. You can use
the library, templates and breakout in your own boards, open or closed, and
modify them, without sharing your design. Keep the licence notice with any copy
of these files. The source is
<https://github.com/CameronBrooks11/cubesat-pc104-kicad>.

Commits before the relicensing carried SPEL's GPL-3.0 and remain under it.
