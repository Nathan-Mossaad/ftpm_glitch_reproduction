#!/usr/bin/env python3
"""Convert a binary blob or hexdump text into a CSV compatible with:

    float(row['Time [s]'])
    int(row['Packet ID'])
    int(row['MOSI'], 16)

The converter writes one CSV row per byte. Time is generated from a
constant byte rate and Packet ID increments from 0.
"""

from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path
from typing import Iterable

CSV_FIELDS = ["Time [s]", "Packet ID", "MOSI"]
BYTE_RATE_HZ = 100_000_000.0
HEX_PAIR_RE = re.compile(r"\b[0-9a-fA-F]{2}\b")


def parse_hexdump_text(text: str) -> bytes:
    """Extract bytes from a text hexdump.

    Supported forms include:
    - `5a 00 01 ff`
    - `00000000: 5a 00 01 ff  ....`
    - xxd/hexdump-style output with an ASCII column on the right
    """

    data = bytearray()
    for line in text.splitlines():
        candidate = line
        if ":" in candidate:
            candidate = candidate.split(":", 1)[1]
        if "  " in candidate:
            # Drop the ASCII column from common hexdump formats.
            candidate = candidate.split("  ", 1)[0]
        for token in HEX_PAIR_RE.findall(candidate):
            data.append(int(token, 16))
    return bytes(data)


def read_input(path: Path) -> bytes:
    raw = path.read_bytes()
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        return raw

    # Heuristic: if the file is mostly printable text, try to parse it as a
    # hexdump. Otherwise treat it as raw binary data.
    printable = sum(ch.isprintable() or ch in "\r\n\t" for ch in text)
    if printable >= len(text) * 0.9:
        parsed = parse_hexdump_text(text)
        if parsed:
            return parsed
    return raw


def bytes_to_rows(data: bytes) -> Iterable[dict[str, str]]:
    for packet_id, byte in enumerate(data):
        yield {
            "Time [s]": f"{packet_id / BYTE_RATE_HZ:.10f}",
            "Packet ID": str(packet_id),
            "MOSI": f"{byte:02x}",
        }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Convert binary/hexdump input into CSV compatible with the target reader."
    )
    parser.add_argument("input", type=Path, help="Input binary file or text hexdump")
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Output CSV path (defaults to <input>.csv)",
    )
    args = parser.parse_args()

    input_path: Path = args.input
    output_path = args.output or input_path.with_suffix(input_path.suffix + ".csv")

    data = read_input(input_path)

    with output_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
        writer.writeheader()
        writer.writerows(bytes_to_rows(data))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
