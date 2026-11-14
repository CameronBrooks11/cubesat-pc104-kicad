# Stack and mechanical

## Stack connectors

The footprints are pads only, so either way of mounting the bus connectors
fits them; choose the parts and the side to suit the stack.

**CubeSat Kit convention.** Each module has its sockets on the top side. A
module that plugs onto another uses a long-tail part whose tails pass through
the board into the sockets below: Samtec ESQ-126-39-G-D (extended tail) in
Pumpkin's example stacks. The specification's Slot 0 sheet lists
ESQ-126-37-G-D, a non-stack-through part.

**Socket on the bottom.** A bottom-mounted stack-through socket such as Samtec
SSQ-126-23-G-D (10.00 mm tails) leaves its pins standing up through the top.
That suits a stack whose boards present pins upward, and does not plug into
the top of a CubeSat Kit stack, whose modules present sockets.

## Spacing and component height

The specification gives two board-to-board spacings, each with a height limit
for parts:

| Spacing | Connectors | Top side, max height | Bottom side, max height |
| --- | --- | --- | --- |
| 15.24 mm to 17.00 mm | The stack connector alone | 13.0 mm | 3.8 mm |
| 24.00 mm to 26.00 mm | Plus a Samtec SSQ-126-22-G-D to span the gap | 21.5 mm | 3.8 mm |

Keep copper 1.27 mm from the board edge; the templates set this as the board's
copper-to-edge clearance.

## Against the specification

The footprints follow Pumpkin's *CubeSat Kit PCB Specification*, drawing
810-00253, revision B2 (2018-11-08). `tools/genfp.py` generates each from the
drawing's DXF for its slot, and the holes and all 104 pins land on the DXF's to
within 0.0001 mm. The specification itself is not in this repository.

Where Slot 0 departs from the drawing:

- **Bottom-left edge.** The DXF leaves the outline open at the bottom-left
  hole, where the drawing calls for the feature that lets the 2nd separation
  switch work. It is closed along that hole's 6.35 mm pad circle.
- **Two holes without pads.** The drawing gives each hole a 6.35 mm pad and
  also recommends keeping copper 1.27 mm from the edge. At the bottom-left and
  top-right holes the edge is 3.175 mm and 3.048 mm from the hole centre, so
  both can't hold. Those two are bare 3.18 mm holes; the other two have plated
  6.35 mm pads.
- **Keepouts.** The three boxes in the DXF are rule areas that allow no
  footprints: the "no parts placed here" patch on the right edge (top side)
  and the clearances for separation switches 1 and 2 (both sides). The
  bottom-side strips where the board rests on the structure's flange are
  hatched in the drawing but not dimensioned, so they are not included.
- **Edge setback.** The drawing recommends 1.27 mm from the edge for all
  copper. That is a board setting (copper to edge clearance), not part of the
  footprint.

Slot 1's outline is closed in its DXF and it has no keepout boxes. Its
top-right hole is bare for the same reason as Slot 0's; the other three have
plated 6.35 mm pads.

!!! note "No 3D models yet"
    The footprints carry no 3D models, so a STEP export shows the bare board.
    [Issue #11](https://github.com/CameronBrooks11/cubesat-pc104-kicad/issues/11)
    tracks adding them for fit checks.
