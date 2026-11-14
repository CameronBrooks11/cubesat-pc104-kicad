# SUCHAI payload

`SUCHAI_Payload` is the CubeSat Kit bus as the payload boards of the SUCHAI 2
and SUCHAI 3 satellites use it, from SPEL at the Universidad de Chile
([spel-uchile/Payload-PC104](https://github.com/spel-uchile/Payload-PC104)).
It is the same two units as [`CSK_Bus`](library.md#csk_bus), with the
payload's names and electrical types on the pins it uses, so ERC can check
power and signal direction on a SUCHAI payload board.

These are the pins the payload assigns. Every other pin keeps its
[bus name](pinout.md) and stays passive.

<!-- table: suchai -->

The table is `tools/suchai_pins.csv`; `tools/gensym.py` builds the symbol from
it.
