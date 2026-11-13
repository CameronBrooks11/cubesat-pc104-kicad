template := "templates/CubeSat_PC104_Slot0"

default:
    @just --list

# Check the template's library copy matches KiCad/, and its board passes DRC with schematic parity
check:
    @cmp KiCad/CubeSat_PC104.kicad_sym {{template}}/CubeSat_PC104.kicad_sym && cmp KiCad/CubeSat_PC104.pretty/CSK_PC104_Slot0.kicad_mod {{template}}/CubeSat_PC104.pretty/CSK_PC104_Slot0.kicad_mod && echo "template library matches KiCad/"
    @out=$(mktemp) && kicad-cli pcb drc --severity-all --schematic-parity --exit-code-violations -o "$out" {{template}}/CubeSat_PC104_Slot0.kicad_pcb; rc=$?; [ $rc -eq 0 ] || cat "$out"; rm -f "$out"; exit $rc

# Copy the library into the template after changing it in KiCad/
sync-template:
    cp KiCad/CubeSat_PC104.kicad_sym {{template}}/
    cp KiCad/CubeSat_PC104.pretty/CSK_PC104_Slot0.kicad_mod {{template}}/CubeSat_PC104.pretty/
