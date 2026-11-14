# Bus pinout

The CubeSat Kit bus runs through every module on two 2×26 headers, H1 and H2.
These are the names `CSK_Bus` gives its pins, laid out as the header: odd
pins in one row, even pins in the other. In the symbol and footprint, H1 is
pins 1 to 52 and H2 is pins 53 to 104, so H2 pin *n* is symbol pin *n* + 52.

## H1

<!-- table: csk-bus H1 -->

## H2

<!-- table: csk-bus H2 -->

## The groups

| Signals | Pins | What they are |
| --- | --- | --- |
| `IO.0` to `IO.47` | H1.1–24, H2.1–24 | General-purpose I/O. What each carries (SPI, UARTs, GPIO, analog) is set by the module that drives it. |
| `+5V_SYS`, `VCC_SYS` | H2.25–28 | System power: +5 V and VCC (normally +3.3 V). |
| `DGND`, `AGND` | H2.29, H2.30, H2.32; H2.31 | Digital and analog ground. |
| `VBATT` | H2.45–46 | Battery voltage. |
| `+5V_USB`, `VBACKUP`, `PWR_MHX` | H1.32, H1.42, H1.33 | USB power, backup (RTC) battery, transceiver power. |
| `S0` to `S5` | H2.33–44 | Remove-before-flight and separation switch terminals, two pins each. |
| `SDA_SYS`, `SCL_SYS` | H1.41, H1.43 | The system I²C bus. |
| `-FAULT`, `SENSE`, `-RESET`, `OFF_VCC`, `PPS` | H1.25, 27, 29, 31, 46 | Control and status. |
| `VREF0` to `VREF2` | H1.26, 28, 30 | Analog references. |
| `-RST_MHX` to `RXD_MHX` | H1.34–40 | The radio transceiver interface. |
| `USER0` to `USER11` | H1.47–52, H2.47–52 | User-defined. |
| `RSVD0`, `RSVD1` | H1.44, H1.45 | Reserved. |

!!! warning "A name is the bus's, not the module's"
    The names are the bus definition. A module may use a pin differently:
    Pumpkin's EPS Module 1, for one, puts battery and +12 V power on some
    `S0`–`S5` and `USER` pins. Check each module's datasheet for what it
    actually puts on a pin before wiring to it.

## Sources

The table is `tools/csk_bus_pins.csv`, from Pumpkin's *Motherboard Module
(MBM) 2* datasheet,
[710-01362 rev E](https://www.pumpkininc.com/space/datasheet/710-01362-E_DS_MBM_2.pdf)
(December 2017). Its connector drawing and its pin description tables agree,
and Pumpkin's *EPS Module 1* datasheet,
[710-01952 rev C](https://www.pumpkininc.com/space/datasheet/710-01952-C_DS_EPSM_1.pdf)
(February 2023), agrees wherever it gives the bus name.

The older *CubeSat Kit FM430 Flight Motherboard* datasheet,
[710-00484 rev D](http://www.cubesatkit.com/docs/datasheet/DS_CSK_MB_710-00484-D.pdf)
(September 2009), differs in two places. Its pin table puts `VREF1` on H1.30
and `VREF2` on H1.28, against its own connector drawing; and it names H1.46
`RSVD2`, which later sheets call `PPS`. The table follows the later sheets.
