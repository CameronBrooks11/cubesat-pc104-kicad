"""MkDocs hook: write the pin tables into the docs from the CSVs the symbols are generated from.

A page asks for a table with a marker on a line of its own:

    <!-- table: csk-bus H1 -->     the CubeSat Kit bus, laid out as header H1 or H2
    <!-- table: suchai -->         the pins the SUCHAI payload assigns

so the docs show the same names the symbols carry, from one source.
"""
import csv
import os
import re

TOOLS = os.path.dirname(os.path.abspath(__file__))
MARKER = re.compile(r"^<!-- table: (\S+)(?: (\S+))? -->$", re.M)


def read(name):
    with open(os.path.join(TOOLS, name), newline="") as f:
        return list(csv.DictReader(f))


def bus_table(header):
    rows = [r for r in read("csk_bus_pins.csv") if r["header_pin"].startswith(header + ".")]
    assert len(rows) == 52, f"csk_bus_pins.csv: {header} has {len(rows)} pins, not 52"
    out = [f"| {header} pin | Signal | {header} pin | Signal |", "| ---: | --- | ---: | --- |"]
    for odd, even in zip(rows[0::2], rows[1::2]):
        out.append(f"| {odd['header_pin'].split('.')[1]} | `{odd['signal']}` "
                   f"| {even['header_pin'].split('.')[1]} | `{even['signal']}` |")
    return "\n".join(out)


def suchai_table():
    bus = {r["pin"]: r for r in read("csk_bus_pins.csv")}
    out = ["| Header pin | Bus signal | SUCHAI signal | Type |", "| --- | --- | --- | --- |"]
    for r in read("suchai_pins.csv"):
        if r["signal"]:
            b = bus[r["pin"]]
            out.append(f"| {b['header_pin']} | `{b['signal']}` | `{r['signal']}` | {r['type'].replace('_', ' ')} |")
    return "\n".join(out)


def table(m):
    kind, arg = m.group(1), m.group(2)
    if kind == "csk-bus" and arg in ("H1", "H2"):
        return bus_table(arg)
    if kind == "suchai" and arg is None:
        return suchai_table()
    raise ValueError(f"unknown table marker: {m.group(0)}")


def on_page_markdown(markdown, **kwargs):
    return MARKER.sub(table, markdown)
