# cubesat-pc104-kicad

KiCad parts and boards for CubeSat Kit modules on the PC/104 form factor: two
2×26 stack headers (H1 and H2) and four mounting holes.

Work in progress: the library and the project template are checked against the
CubeSat Kit specification; the stack breakout board's outline is next.

## Project template

[`templates/CubeSat_PC104_Slot0`](templates/CubeSat_PC104_Slot0/) is a KiCad 10
project template for a CubeSat Kit user module: the Slot 0 board outline, the
H1/H2 bus as connector J1, the mounting holes and the keepouts, with copper
kept 1.27 mm from the edge. It passes DRC with schematic parity; ERC lists the
104 bus pins as unconnected until you wire them or flag them.

<img src="templates/CubeSat_PC104_Slot0/meta/brd.png" alt="Template board, top view" width="400" />

1. Clone this repository, or copy the template directory out of it.
2. In KiCad choose **File → New Project from Template**, open the user
   templates tab and point it at `templates/`.
3. Pick the template and name the project. KiCad copies the files and renames
   them after the project.
4. In the schematic, wire the bus pins the module uses and put a no-connect
   flag on the others.

The template carries its own copy of the `CubeSat_PC104` library, so a new
project needs nothing else installed.

## Library

`KiCad/CubeSat_PC104.kicad_sym` and `KiCad/CubeSat_PC104.pretty/`. Add them to
a project as the symbol and footprint libraries `CubeSat_PC104`.

| Part | What it is |
| --- | --- |
| `CSK_PC104_Slot0` (footprint) | A CubeSat Kit user module in the base "Slot 0" pattern: board outline, H1 and H2 headers, mounting holes, and keepout areas. Origin at H1 pin 1. |
| `CSK_Bus` (symbol) | The bus headers for any payload: unit A is H1 (pins 1–52), unit B is H2 (pins 53–104), all passive. |
| `SUCHAI_Payload` (symbol) | The SUCHAI 2 and 3 payload pinout on the same headers, with supply pins as power inputs. |

<img src="img/CSK_PC104_Slot0.png" alt="CSK_PC104_Slot0 footprint" width="400" />
<img src="img/CSK_Bus_H1.png" alt="CSK_Bus unit A, H1" height="400" />
<img src="img/SUCHAI_Payload.png" alt="SUCHAI_Payload symbol" width="400" />

### Against the specification

The footprint follows Pumpkin's *CubeSat Kit PCB Specification*, drawing
810-00253, revision B2 (2018-11-08), Slot 0. It was generated from the drawing's
Slot 0 DXF; its holes and all 104 pins land on the DXF's to within 0.0001 mm.
Where it departs from the drawing:

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

The specification documents are not in this repository.

## Stack breakout board

`PC104/` is the 4-layer stack breakout board, imported from the Eagle design in
`Eagle/`. It carries every bus pin from the stack headers to a second pair of
headers 16.9 mm over. In KiCad 10.0.6 format, ERC is clean, schematic parity is
clean, and with the zones filled DRC finds no unconnected items. It still has
SPEL's outline, which extends past the CubeSat Kit outline, and 12 DRC findings
that need placement in the editor:

- J2 pin 52's track on F.Cu passes through the keep-out ring of the top-left
  mounting hole, probably room for a screw head (2 errors). The inner layers are
  taken at that height, so it needs a new route.
- Silkscreen overlaps copper in 10 places: the rings around the mounting
  holes, two pin labels next to holes, and the back outlines of J2 and J4 over
  the pads of the headers beside them.

The ground pours are saved unfilled; fill them (B) before plotting.

## Development

With [just](https://just.systems/) and KiCad 10's `kicad-cli`, `just check`
confirms the template's library copy matches `KiCad/` and runs DRC with
schematic parity on the template board. After changing the library, run
`just sync-template`.

## Credits

The SUCHAI pinout, the Eagle designs and the stack breakout board are by SPEL at
the Universidad de Chile, from
[spel-uchile/Payload-PC104](https://github.com/spel-uchile/Payload-PC104)
(matvidal, EliasObreque and Alex Becerra, 2018 to 2022). Its history is kept in
this repository; the KiCad import of the stack breakout board is from 2024.

The CubeSat Kit is Pumpkin, Inc.'s. PC/104 is a standard of the
[RMS Consortium](https://www.rmsconsortium.org/), formerly the PC/104
Consortium. This project is not affiliated with either.

## License

GPL-3.0, as published by SPEL. See [LICENSE](./LICENSE).
