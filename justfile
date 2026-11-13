template := "templates/CubeSat_PC104_Slot0"

default:
    @just --list

# Check the template's library copy matches KiCad/, and its board passes DRC with schematic parity
check:
    @cmp KiCad/CubeSat_PC104.kicad_sym {{template}}/CubeSat_PC104.kicad_sym && cmp KiCad/CubeSat_PC104.pretty/CSK_PC104_Slot0.kicad_mod {{template}}/CubeSat_PC104.pretty/CSK_PC104_Slot0.kicad_mod && echo "template library matches KiCad/"
    @out=$(mktemp) && kicad-cli pcb drc --severity-all --schematic-parity --exit-code-violations -o "$out" {{template}}/CubeSat_PC104_Slot0.kicad_pcb; rc=$?; [ $rc -eq 0 ] || cat "$out"; rm -f "$out"; exit $rc

breakout := "PC104/StackBreakoutConnection_4layers_V1.0.kicad_pcb"

# Plot Gerbers and drill files for a board into fab/<board>/ and zip them; refuses if DRC finds anything
fab board=breakout copper="F.Cu,In1.Cu,In2.Cu,B.Cu":
    @rpt=$(mktemp) && kicad-cli pcb drc --severity-all --schematic-parity --refill-zones --exit-code-violations -o "$rpt" {{board}} >/dev/null; rc=$?; [ $rc -eq 0 ] || { cat "$rpt"; rm -f "$rpt"; echo "DRC must be clean before plotting"; exit $rc; }; rm -f "$rpt"
    @name=$(basename {{board}} .kicad_pcb) && rm -rf "fab/$name" && mkdir -p "fab/$name" && kicad-cli pcb export gerbers --check-zones --subtract-soldermask --layers {{copper}},F.Mask,B.Mask,F.Silkscreen,B.Silkscreen,F.Paste,B.Paste,Edge.Cuts -o "fab/$name" {{board}} >/dev/null && kicad-cli pcb export drill --excellon-separate-th --generate-map --map-format gerberx2 -o "fab/$name" {{board}} >/dev/null && (cd fab && rm -f "$name.zip" && zip -qr "$name.zip" "$name") && ls "fab/$name" && echo "fab/$name.zip"

# Copy the library into the template after changing it in KiCad/
sync-template:
    cp KiCad/CubeSat_PC104.kicad_sym {{template}}/
    cp KiCad/CubeSat_PC104.pretty/CSK_PC104_Slot0.kicad_mod {{template}}/CubeSat_PC104.pretty/
