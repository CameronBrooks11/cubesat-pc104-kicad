templates := "templates/CubeSat_PC104_Slot0 templates/CubeSat_PC104_Slot1"
breakout_pcb := "breakout/CSK_Bus_Breakout.kicad_pcb"
# Every project that carries its own copy of the library
projects := templates + " breakout"

default:
    @just --list

# Library copies, symbol and footprint generators, DRC with schematic parity and ERC on every board
check:
    #!/usr/bin/env bash
    set -uo pipefail
    tmp=$(mktemp -d); trap 'rm -rf "$tmp"' EXIT
    fail() { echo "FAIL: $1"; [ -n "${2:-}" ] && cat "$2"; exit 1; }
    for t in {{projects}}; do
      cmp -s KiCad/CubeSat_PC104.kicad_sym "$t/CubeSat_PC104.kicad_sym" && diff -r KiCad/CubeSat_PC104.pretty "$t/CubeSat_PC104.pretty" >/dev/null \
        || fail "$t: library copy differs from KiCad/ (run just sync-template)"
      echo "$t: library matches KiCad/"
    done
    python3 tools/gensym.py "$tmp/CubeSat_PC104.kicad_sym" >/dev/null && kicad-cli sym upgrade --force "$tmp/CubeSat_PC104.kicad_sym" >/dev/null || fail "tools/gensym.py did not run"
    cmp -s "$tmp/CubeSat_PC104.kicad_sym" KiCad/CubeSat_PC104.kicad_sym || fail "KiCad/CubeSat_PC104.kicad_sym is not what tools/gensym.py generates"
    echo "KiCad/CubeSat_PC104.kicad_sym matches tools/gensym.py"
    cp -r KiCad/CubeSat_PC104.pretty "$tmp/lib.pretty" && python3 tools/genbus.py "$tmp/lib.pretty" >/dev/null && kicad-cli fp upgrade --force "$tmp/lib.pretty" >/dev/null || fail "tools/genbus.py did not run"
    diff <(grep -v '(uuid ' KiCad/CubeSat_PC104.pretty/CSK_PC104_Bus.kicad_mod) <(grep -v '(uuid ' "$tmp/lib.pretty/CSK_PC104_Bus.kicad_mod") || fail "CSK_PC104_Bus.kicad_mod is not what tools/genbus.py generates"
    echo "CSK_PC104_Bus matches tools/genbus.py"
    for b in {{templates}} {{breakout_pcb}}; do
      [ -d "$b" ] && b="$b/$(basename "$b").kicad_pcb"
      kicad-cli pcb drc --severity-all --schematic-parity --refill-zones --exit-code-violations -o "$tmp/drc.rpt" "$b" >/dev/null || fail "$b: DRC" "$tmp/drc.rpt"
      echo "$b: DRC clean, schematic parity clean"
    done
    # A template's only ERC findings are its bus pins, unconnected until a project wires them
    for t in {{templates}}; do
      sch="$t/$(basename "$t").kicad_sch"
      kicad-cli sch erc --severity-all --format json -o "$tmp/erc.json" "$sch" >/dev/null
      other=$(python3 -c 'import json,sys; v=[x["type"] for s in json.load(open(sys.argv[1]))["sheets"] for x in s["violations"]]; print(len(v)-v.count("pin_not_connected"))' "$tmp/erc.json")
      [ "$other" = 0 ] || fail "$sch: $other ERC finding(s) besides unconnected bus pins" "$tmp/erc.json"
      echo "$sch: ERC finds only the unconnected bus pins"
    done
    sch="{{breakout_pcb}}"; sch="${sch%.kicad_pcb}.kicad_sch"
    kicad-cli sch erc --severity-all --exit-code-violations -o "$tmp/erc.rpt" "$sch" >/dev/null || fail "$sch: ERC" "$tmp/erc.rpt"
    echo "$sch: ERC clean"

# Regenerate the footprints from the specification's DXFs and compare them with KiCad/
footprints spec="reference/CSK_PCB_Spec_B2_20181108":
    #!/usr/bin/env bash
    set -uo pipefail
    tmp=$(mktemp -d); trap 'rm -rf "$tmp"' EXIT
    out="$tmp/CubeSat_PC104.pretty"; mkdir "$out"
    for s in 0 1; do
      python3 tools/genfp.py "{{spec}}/CSK_PCB_Slot${s}_B2_20180823.DXF" "$out/CSK_PC104_Slot$s.kicad_mod" "CSK_PC104_Slot$s" >/dev/null || exit 1
    done
    kicad-cli fp upgrade --force "$out" >/dev/null || exit 1
    rc=0
    for s in 0 1; do
      f="CSK_PC104_Slot$s.kicad_mod"
      if diff <(grep -v '(uuid ' "KiCad/CubeSat_PC104.pretty/$f") <(grep -v '(uuid ' "$out/$f"); then echo "$f matches the specification's DXF"; else echo "FAIL: $f differs from the DXF"; rc=1; fi
    done
    exit $rc

# Plot Gerbers and drill files for a board into fab/<board>/ and zip them; refuses if DRC finds anything
fab board=breakout_pcb copper="F.Cu,In1.Cu,In2.Cu,B.Cu":
    @rpt=$(mktemp) && kicad-cli pcb drc --severity-all --schematic-parity --refill-zones --exit-code-violations -o "$rpt" {{board}} >/dev/null; rc=$?; [ $rc -eq 0 ] || { cat "$rpt"; rm -f "$rpt"; echo "DRC must be clean before plotting"; exit $rc; }; rm -f "$rpt"
    @name=$(basename {{board}} .kicad_pcb) && rm -rf "fab/$name" && mkdir -p "fab/$name" && kicad-cli pcb export gerbers --check-zones --subtract-soldermask --layers {{copper}},F.Mask,B.Mask,F.Silkscreen,B.Silkscreen,F.Paste,B.Paste,Edge.Cuts -o "fab/$name" {{board}} >/dev/null && kicad-cli pcb export drill --excellon-separate-th --generate-map --map-format gerberx2 -o "fab/$name" {{board}} >/dev/null && (cd fab && rm -f "$name.zip" && zip -qr "$name.zip" "$name") && ls "fab/$name" && echo "fab/$name.zip"

# Build the release assets into dist/: library, templates, breakout project and its fab files
dist version="dev":
    #!/usr/bin/env bash
    set -euo pipefail
    rm -rf dist && mkdir dist
    stage=$(mktemp -d); trap 'rm -rf "$stage"' EXIT
    pack() { find "$stage/$1" -name '*.kicad_prl' -delete; (cd "$stage" && zip -qr "$OLDPWD/dist/$1.zip" "$1") && rm -rf "${stage:?}/$1"; echo "dist/$1.zip"; }
    d="$stage/CubeSat_PC104-{{version}}"; mkdir -p "$d"
    cp -r KiCad/CubeSat_PC104.kicad_sym KiCad/CubeSat_PC104.pretty LICENSE "$d/"
    pack "CubeSat_PC104-{{version}}"
    d="$stage/cubesat-pc104-templates-{{version}}"; mkdir -p "$d"
    cp -r templates/. LICENSE "$d/"
    pack "cubesat-pc104-templates-{{version}}"
    d="$stage/CSK_Bus_Breakout-{{version}}"; mkdir -p "$d"
    cp -r breakout/. LICENSE "$d/"
    pack "CSK_Bus_Breakout-{{version}}"
    just fab >/dev/null
    cp fab/CSK_Bus_Breakout.zip "dist/CSK_Bus_Breakout-fab-{{version}}.zip"
    echo "dist/CSK_Bus_Breakout-fab-{{version}}.zip"

# Regenerate the breakout board from the Slot 0 template and the library, then fill its zones
breakout:
    python3 tools/genbreakout.py
    kicad-cli sch upgrade --force breakout/CSK_Bus_Breakout.kicad_sch
    kicad-cli pcb drc --severity-all --schematic-parity --refill-zones --save-board --exit-code-violations -o /dev/null {{breakout_pcb}}

# Copy the library into every template and the breakout after changing it in KiCad/
sync-template:
    @for t in {{projects}}; do cp KiCad/CubeSat_PC104.kicad_sym "$t/" && rm -f "$t"/CubeSat_PC104.pretty/*.kicad_mod && cp KiCad/CubeSat_PC104.pretty/*.kicad_mod "$t/CubeSat_PC104.pretty/" && echo "synced $t"; done
