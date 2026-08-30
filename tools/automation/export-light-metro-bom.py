#!/usr/bin/env python3
"""Export the light-metro-3car procurement BOM markdown to CSV."""

from __future__ import annotations

import argparse
import csv
import io
import re
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SOURCE = REPO_ROOT / "docs/rolling-stock/light-metro-3car/bom-skeleton.md"
DEFAULT_OUT = REPO_ROOT / "build/bom/rolling_stock_bom.csv"
DEFAULT_FITOUT_OUT = REPO_ROOT / "build/bom/rolling_stock_cots_fitout_bom.csv"
MECH_SRC = REPO_ROOT / "design/component-catalogue/src"
if str(MECH_SRC) not in sys.path:
    sys.path.insert(0, str(MECH_SRC))

from osr_mech.rolling_stock.bom_trace import bom_scope, engineering_ids_for_bom_line

CSV_FIELDS = [
    "bucket",
    "line_id",
    "description",
    "quantity",
    "source",
    "bom_scope",
    "engineering_ids",
    "base_usd",
    "cost_low_usd",
    "cost_high_usd",
    "cost_basis",
    "notes",
]

FITOUT_CSV_FIELDS = [
    "category",
    "name",
    "reference",
    "qty_per_car",
    "qty_per_consist",
    "unit_cost_low_usd",
    "unit_cost_base_usd",
    "unit_cost_high_usd",
    "consist_cost_low_usd",
    "consist_cost_base_usd",
    "consist_cost_high_usd",
    "unit_mass_kg",
    "consist_mass_kg",
    "unit_power_w",
    "consist_power_w",
    "shape_source_url",
    "geometry_basis",
    "cost_basis",
]


_COST_BANDS = {
    "SOURCE": (0.85, 1.35, "Public catalogue/distributor or commodity quote band; replace with current supplier quote at procurement."),
    "MAKE": (0.80, 1.45, "Local fabrication estimate band; replace with shop-route quote and labour-rate pack."),
    "BID": (0.75, 1.65, "Tender-only rail component band; exact price requires supplier RFQ and certification scope."),
}


def _cells(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def _money(value: str) -> int:
    cleaned = value.replace(" ", "").replace(",", "").replace("_", "")
    return int(float(cleaned))


def _cost_band(source_kind: str, base_usd: int) -> tuple[int, int, str]:
    low_factor, high_factor, basis = _COST_BANDS.get(source_kind, _COST_BANDS["BID"])
    return round(base_usd * low_factor), round(base_usd * high_factor), basis


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
        base_value = _money(base_usd)
        low, high, cost_basis = _cost_band(source_kind, base_value)
        rows.append(
            {
                "bucket": bucket,
                "line_id": line_id,
                "description": desc,
                "quantity": qty,
                "source": source_kind,
                "bom_scope": bom_scope(line_id),
                "engineering_ids": ";".join(engineering_ids_for_bom_line(line_id)),
                "base_usd": str(base_value),
                "cost_low_usd": str(low),
                "cost_high_usd": str(high),
                "cost_basis": cost_basis,
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


def export_fitout_rows(car_count: int = 3) -> list[dict[str, str]]:
    """Return COTS fit-out catalogue rows with source and cost bands."""

    from osr_mech.rolling_stock.car_body import CarDimensions
    from osr_mech.rolling_stock.cots_equipment import bom_per_car

    rows: list[dict[str, str]] = []
    for item, qty_per_car in bom_per_car(CarDimensions()):
        qty_per_consist = qty_per_car * car_count
        rows.append(
            {
                "category": item.category.value,
                "name": item.name,
                "reference": item.sku_reference,
                "qty_per_car": str(qty_per_car),
                "qty_per_consist": str(qty_per_consist),
                "unit_cost_low_usd": f"{item.unit_cost_low_usd:.0f}",
                "unit_cost_base_usd": f"{item.unit_cost_base_usd:.0f}",
                "unit_cost_high_usd": f"{item.unit_cost_high_usd:.0f}",
                "consist_cost_low_usd": f"{item.unit_cost_low_usd * qty_per_consist:.0f}",
                "consist_cost_base_usd": f"{item.unit_cost_base_usd * qty_per_consist:.0f}",
                "consist_cost_high_usd": f"{item.unit_cost_high_usd * qty_per_consist:.0f}",
                "unit_mass_kg": f"{item.mass_kg:.1f}",
                "consist_mass_kg": f"{item.mass_kg * qty_per_consist:.1f}",
                "unit_power_w": f"{item.power_w:.1f}",
                "consist_power_w": f"{item.power_w * qty_per_consist:.1f}",
                "shape_source_url": item.supplier_reference_url,
                "geometry_basis": item.geometry_basis,
                "cost_basis": item.cost_basis,
            }
        )
    return rows


def render_fitout_csv(car_count: int = 3) -> str:
    out = io.StringIO()
    writer = csv.DictWriter(out, fieldnames=FITOUT_CSV_FIELDS, lineterminator="\n")
    writer.writeheader()
    writer.writerows(export_fitout_rows(car_count))
    return out.getvalue()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--fitout-out", type=Path, default=DEFAULT_FITOUT_OUT)
    parser.add_argument("--car-count", type=int, default=3)
    parser.add_argument(
        "--no-fitout",
        action="store_true",
        help="only export the procurement BOM CSV",
    )
    args = parser.parse_args()

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(render_csv(args.source))
    print(f"wrote {args.out}")
    if not args.no_fitout:
        args.fitout_out.parent.mkdir(parents=True, exist_ok=True)
        args.fitout_out.write_text(render_fitout_csv(args.car_count))
        print(f"wrote {args.fitout_out}")


if __name__ == "__main__":
    main()
