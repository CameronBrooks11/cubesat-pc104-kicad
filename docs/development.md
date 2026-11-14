# Development

The library, the breakout board and these docs are generated from scripts and
tables, and CI checks that what is committed matches them. To change a part,
change its generator or table, regenerate, and let `just check` confirm.

You need [just](https://just.systems/), Python 3 and KiCad 10's `kicad-cli`;
the docs also need [uv](https://docs.astral.sh/uv/).

## Layout

| Folder | What it holds |
| --- | --- |
| `library/` | The `CubeSat_PC104` symbol and footprint library. This is the source; edit it here. |
| `templates/` | The two project templates, each with a copy of the library. |
| `breakout/` | The bus breakout board, with a copy of the library. |
| `tools/` | The generators and the pin tables they read. |
| `docs/` | This site. |

Each template and `breakout/` carries its own copy of the library, because
KiCad copies a template folder as it is and the breakout ships as its own zip:
a project that pointed back at `library/` would lose its parts once copied.
`just sync-template` writes the copies and `just check` fails if one differs.

## Recipes

| Recipe | What it does |
| --- | --- |
| `just check` | The gate; see below. CI runs it in the `kicad/kicad:10.0.6` image on every pull request and push to `main`. |
| `just sync-template` | Copies `library/` into each template and `breakout/`. |
| `just breakout` | Regenerates the breakout from the Slot 0 template and the library, and fills its ground plane. |
| `just footprints spec=<folder>` | Regenerates both board footprints from the specification's DXFs and compares them with `library/`. |
| `just fab` | Plots the breakout's Gerbers and drill files into `fab/` and zips them; refuses if DRC finds anything. |
| `just dist <version>` | Builds the release assets into `dist/`. |
| `just renders` | Renders the pictures for these docs into `docs/renders/`. |
| `just docs` | Builds this site into `site/`, failing on any warning. |
| `just serve` | Serves this site at <http://127.0.0.1:8000> while you edit. |

`just check` confirms that:

- the library copy in each template and in `breakout/` matches `library/`;
- `library/CubeSat_PC104.kicad_sym` is exactly what `tools/gensym.py`
  generates, and `CSK_PC104_Bus` what `tools/genbus.py` generates;
- DRC with schematic parity is clean on both templates and the breakout;
- ERC on each template finds nothing but the unconnected bus pins, and on the
  breakout nothing at all.

## Changing a part

**A symbol.** Edit `tools/gensym.py`, or the pin tables
`tools/csk_bus_pins.csv` and `tools/suchai_pins.csv`, then:

```sh
python3 tools/gensym.py library/CubeSat_PC104.kicad_sym
kicad-cli sym upgrade --force library/CubeSat_PC104.kicad_sym
```

**A footprint.** Edit `tools/genfp.py`, then regenerate from the slot's DXF:

```sh
python3 tools/genfp.py <dxf> library/CubeSat_PC104.pretty/<name>.kicad_mod <name>
kicad-cli fp upgrade --force library/CubeSat_PC104.pretty
```

The DXFs ship with Pumpkin's specification and are not in this repository; put
`CSK_PCB_Slot0_B2_20180823.DXF` and `CSK_PCB_Slot1_B2_20180823.DXF` in a
folder and pass it to `just footprints spec=<folder>`. CI cannot run this.

Follow either change with `just sync-template`, then `just breakout`.

A symbol change also has to reach the copy of the symbol each schematic embeds:
in each template, **Tools → Update Symbols from Library**, then **Update PCB
from Schematic** on its board. `just check` fails on schematic parity until
they agree.

## Releases

Pushing a `v*` tag runs `just check` and `just dist` in CI and publishes a
GitHub release with the assets, using that version's section of
`CHANGELOG.md` as the notes. Versions follow semantic versioning: a footprint
change that moves a pad, hole or outline is a major version.

## These docs

The site is [MkDocs](https://www.mkdocs.org/) with the
[Material](https://squidfunk.github.io/mkdocs-material/) theme, built from
`docs/` by `mkdocs.yml`. The pin tables on [Bus pinout](pinout.md) and
[SUCHAI payload](suchai.md) are written at build time from the same CSVs as
the symbols, by `tools/mkdocs_hooks.py`; the pictures come from `just renders`.
CI builds the site on every pull request and publishes it from `main`.

```sh
just renders
just serve
```
