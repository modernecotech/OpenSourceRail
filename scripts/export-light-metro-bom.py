#!/usr/bin/env python3
"""Export the light-metro-3car procurement BOM markdown to CSV."""

from __future__ import annotations

import argparse
import csv
import io
import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = REPO_ROOT / "docs/rolling-stock/light-metro-3car/bom-skeleton.md"
DEFAULT_OUT = REPO_ROOT / "build/bom/rolling_stock_bom.csv"

CSV_FIELDS = [
    "bucket",
    "line_id",
    "description",
    "quantity",
    "source",
    "base_usd",
    "notes",
]


def _cells(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def export_rows(source: Path = DEFAULT_SOURCE) -> list[dict[str, str]]:
    """Return canonical procurement BOM rows from the markdown tables."""

    rows: list[dict[str, str]] = []
    bucket = ""
    for raw in source.read_text().splitlines():
        line = raw.strip()
        if line.startswith("## "):
            bucket = line.removeprefix("## ").strip()
            continue
        if not line.startswith("|"):
            continue
        cells = _cells(line)
        if not cells or not re.fullmatch(r"[A-Z]\d+", cells[0]):
            continue
        if len(cells) != 6:
            raise ValueError(f"unexpected BOM row shape in {source}: {raw}")
        line_id, desc, qty, source_kind, base_usd, notes = cells
        rows.append(
            {
                "bucket": bucket,
                "line_id": line_id,
                "description": desc,
                "quantity": qty,
                "source": source_kind,
                "base_usd": base_usd.replace(" ", ""),
                "notes": notes,
            }
        )
    return rows


def render_csv(source: Path = DEFAULT_SOURCE) -> str:
    out = io.StringIO()
    writer = csv.DictWriter(out, fieldnames=CSV_FIELDS, lineterminator="\n")
    writer.writeheader()
    writer.writerows(export_rows(source))
    return out.getvalue()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(render_csv(args.source))
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
