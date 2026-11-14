# Getting started

Everything here needs KiCad 10 and is tested with 10.0.6. Earlier 10.0
patches cannot create a project from a template folder.

There are two ways in: start a new module from a template, or add the library
to a project you already have.

## Start a module from a template

A template is a whole project: the board outline, the bus as connector J1, the
mounting holes and the board rules, with its own copy of the library. Choose
the pattern first; [Templates](templates.md) compares the two. If unsure, use
Slot 0.

1. Get the templates: download `cubesat-pc104-templates-<version>.zip` from the
   [releases page](https://github.com/CameronBrooks11/cubesat-pc104-kicad/releases)
   and unzip it, or clone the repository and use its `templates/` folder.
2. In KiCad choose **File → New Project from Template**, open the user
   templates tab and point it at the folder holding the templates. To list
   them every time, set `KICAD_USER_TEMPLATE_DIR` to that folder under
   **Preferences → Configure Paths**.
3. Pick `CubeSat_PC104_Slot0` or `CubeSat_PC104_Slot1` and name the project.
   KiCad copies the files and renames them after the project.
4. In the schematic, wire the bus pins the module uses and put a no-connect
   flag on the rest. [Bus pinout](pinout.md) lists what each pin carries.

ERC lists every bus pin as unconnected until step 4 is done; that is the
template's only ERC finding. The board passes DRC as it is.

## Add the library to an existing project

The library is one symbol file, `CubeSat_PC104.kicad_sym`, and one footprint
folder, `CubeSat_PC104.pretty`. Get them from `CubeSat_PC104-<version>.zip` on the
[releases page](https://github.com/CameronBrooks11/cubesat-pc104-kicad/releases),
or from `library/` in a clone.

The templates load the library with the nickname `CubeSat_PC104`. Use the same
nickname, so the symbols' footprint links (`CubeSat_PC104:CSK_PC104_Slot0`)
resolve.

=== "In the project (recommended)"

    The project keeps its own copy, so it opens anywhere without setup.

    1. Copy `CubeSat_PC104.kicad_sym` and `CubeSat_PC104.pretty/` into the
       project folder.
    2. **Preferences → Manage Symbol Libraries**, tab **Project Specific
       Libraries**: add `CubeSat_PC104.kicad_sym` with nickname
       `CubeSat_PC104`. KiCad writes the path as
       `${KIPRJMOD}/CubeSat_PC104.kicad_sym`, relative to the project.
    3. **Preferences → Manage Footprint Libraries**, same tab: add the
       `CubeSat_PC104.pretty` folder with nickname `CubeSat_PC104`.

=== "For every project"

    One copy on your machine, shared by every project.

    1. Unzip the library somewhere it will stay.
    2. Under **Preferences → Configure Paths**, add a variable such as
       `CUBESAT_PC104` pointing at that folder.
    3. In **Manage Symbol Libraries** and **Manage Footprint Libraries**, tab
       **Global Libraries**, add `${CUBESAT_PC104}/CubeSat_PC104.kicad_sym`
       and `${CUBESAT_PC104}/CubeSat_PC104.pretty`, each with nickname
       `CubeSat_PC104`.

    A project made this way opens only on a machine with the same setup.

Then place `CSK_Bus` from `CubeSat_PC104` in the schematic. Its footprint is
`CSK_PC104_Slot0`; change the footprint field to `CSK_PC104_Slot1` for a
Slot 1 board, or to `CSK_PC104_Bus` for a bus connector without the board
outline. [Library](library.md) describes each part.

!!! note "Board outline"
    `CSK_PC104_Slot0` and `CSK_PC104_Slot1` draw the board outline on
    `Edge.Cuts` as part of the footprint, with H1 pin 1 at the origin. Delete
    any outline the board already has, or use `CSK_PC104_Bus` and keep yours.
    The specification also asks for copper to stay 1.27 mm from the edge; set
    **Board Setup → Constraints → Copper to edge clearance** to 1.27 mm, as
    the templates do.
