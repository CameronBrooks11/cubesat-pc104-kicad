templates := "templates/CubeSat_PC104_Slot0 templates/CubeSat_PC104_Slot1"
breakout := "PC104/StackBreakoutConnection_4layers_V1.0.kicad_pcb"

default:
    @just --list

# Check each template's library copy matches KiCad/, and each template board passes DRC with schematic parity
check:
    @for t in {{templates}}; do cmp KiCad/CubeSat_PC104.kicad_sym "$t/CubeSat_PC104.kicad_sym" && diff -r KiCad/CubeSat_PC104.pretty "$t/CubeSat_PC104.pretty" && echo "$t: library matches KiCad/" || exit 1; done
    @for t in {{templates}}; do out=$(mktemp); kicad-cli pcb drc --severity-all --schematic-parity --exit-code-violations -o "$out" "$t/$(basename $t).kicad_pcb" >/dev/null; rc=$?; [ $rc -eq 0 ] && echo "$t: DRC clean" || { cat "$out"; rm -f "$out"; exit $rc; }; rm -f "$out"; done

# Plot Gerbers and drill files for a board into fab/<board>/ and zip them; refuses if DRC finds anything
fab board=breakout copper="F.Cu,In1.Cu,In2.Cu,B.Cu":
    @rpt=$(mktemp) && kicad-cli pcb drc --severity-all --schematic-parity --refill-zones --exit-code-violations -o "$rpt" {{board}} >/dev/null; rc=$?; [ $rc -eq 0 ] || { cat "$rpt"; rm -f "$rpt"; echo "DRC must be clean before plotting"; exit $rc; }; rm -f "$rpt"
    @name=$(basename {{board}} .kicad_pcb) && rm -rf "fab/$name" && mkdir -p "fab/$name" && kicad-cli pcb export gerbers --check-zones --subtract-soldermask --layers {{copper}},F.Mask,B.Mask,F.Silkscreen,B.Silkscreen,F.Paste,B.Paste,Edge.Cuts -o "fab/$name" {{board}} >/dev/null && kicad-cli pcb export drill --excellon-separate-th --generate-map --map-format gerberx2 -o "fab/$name" {{board}} >/dev/null && (cd fab && rm -f "$name.zip" && zip -qr "$name.zip" "$name") && ls "fab/$name" && echo "fab/$name.zip"

# Copy the library into every template after changing it in KiCad/
sync-template:
    @for t in {{templates}}; do cp KiCad/CubeSat_PC104.kicad_sym "$t/" && rm -f "$t"/CubeSat_PC104.pretty/*.kicad_mod && cp KiCad/CubeSat_PC104.pretty/*.kicad_mod "$t/CubeSat_PC104.pretty/" && echo "synced $t"; done
