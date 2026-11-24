"""Reproduce the issued deck-fed erection comparison and CSV handoffs."""

import argparse
import csv
import io
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[5]
sys.path.insert(0, str(ROOT))

from cities.Baghdad.engineering.mechanical.civil import rail_fed_erection as study


def csv_text(rows):
    stream = io.StringIO(newline="")
    fieldnames = list(dict.fromkeys(field for row in rows for field in row))
    writer = csv.DictWriter(stream, fieldnames, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return stream.getvalue()


LABELS = {
    "road_day": "Road-crane · 8 h",
    "road_extended": "Road-crane · 16 h",
    "rail_extended": "Deck-fed · 16 h",
    "rail_24h": "Deck-fed · 24 h",
}


def markdown(reference, programmes):
    scope, geometry = reference["scope"], reference["geometry"]
    title = "# Erection prices, programme and traffic occupation"
    lines = [title, "", f"Evaluation `{reference['evaluation_id']}`.", "",
             f"The illustrative {scope['route_km']:g} km double-track corridor uses "
             f"{geometry['standard_bays']:,} paired standard bays and {geometry['standard_girders']:,} girders. "
             "Both methods carry the same permanent works and terminal casting capacity.", "",
             "## Compare the default methods", "",
             "| Method and allowed daily window | Calendar days | Labour h | Loaded public-road beam trips "
             "| Erection lane-hours | Erection cost low / base / high | Standard stock + erection base |",
             "|---|---:|---:|---:|---:|---:|---:|"]
    for row in programmes:
        if row["scenario"] != "illustrative baseline":
            continue
        costs = " / ".join(f"${row[f'method_{case}_usd'] / 1e6:.2f}m" for case in ("low", "base", "high"))
        lines.append(
            f"| {LABELS[row['method']]} | {row['calendar_days']:.1f} | {row['erection_scope_labour_hours']:,.0f} "
            f"| {row['public_road_loaded_beam_trips']:,} | {row['lane_hours']:,} | {costs} "
            f"| ${row['base_stock_and_erection_usd'] / 1e6:.2f}m |"
        )
    lines += ["", "Days cover preliminary release and the girder erection programme. Labour covers the "
              "method crews. Erection lane-hours exclude common substructure, utilities and station works. "
              "Rates are planning estimates in constant US dollars.", "",
              "## Test route length and overhead exclusions", "",
              "| Length and excluded share | Road-crane 8 h | Road-crane 16 h | Deck-fed 24 h "
              "| Base deck-fed saving vs road |",
              "|---|---:|---:|---:|---:|"]
    for start in range(0, len(programmes), len(LABELS)):
        by_method = {row["method"]: row for row in programmes[start:start + len(LABELS)]}
        day, extended, deck = (by_method[key] for key in ("road_day", "road_extended", "rail_24h"))
        delta = (day["method_base_usd"] - deck["method_base_usd"]) / 1e6
        price = f"${abs(delta):.2f}m {'saving' if delta >= 0 else 'extra'}"
        lines.append(f"| {day['route_km']:g} km · {day['overhead_exclusion_pct']}% "
                     f"| {day['calendar_days']:.1f} d | {extended['calendar_days']:.1f} d "
                     f"| {deck['calendar_days']:.1f} d | {price} |")
    return "\n".join([*lines, "", "[Read the workplan and holds](../RAIL-FED-ERECTION.md) · "
                      "[Exact cost and shift detail](comparison.json)", ""])


def build():
    reference = study.evaluate()
    trials = [("short corridor", 3, 5), ("illustrative baseline", 12, 5),
              ("survey-replacement length sensitivity", 17.461, 5),
              ("long corridor with more blocked lifts", 24, 10)]
    programmes = []
    for label, length, exclusion in trials:
        report = reference if length == 12 and exclusion == 5 else study.evaluate(length, exclusion)
        for key, method in report["methods"].items():
            costs = method["cases"]
            programmes.append({
                "scenario": label,
                "route_km": length,
                "overhead_exclusion_pct": exclusion,
                "method": key,
                "calendar_days": round(method["calendar_days"], 2),
                "erection_scope_labour_hours": round(method["labour_hours"], 1),
                "public_road_loaded_beam_trips": method["routine_public_road_beam_trips"],
                "lane_hours": method["road_lane_hours"],
                "method_low_usd": round(costs["low"]["method_scope_usd"], 2),
                "method_base_usd": round(costs["base"]["method_scope_usd"], 2),
                "method_high_usd": round(costs["high"]["method_scope_usd"], 2),
                "base_stock_and_erection_usd": round(costs["base"]["installed_standard_stock_usd"], 2),
                "evaluation_id": report["evaluation_id"],
            })
    crews = [
        {"method": key, **row, "evaluation_id": reference["evaluation_id"]}
        for key, method in reference["methods"].items()
        for row in method["crew_shifts"]
    ]
    return {
        "comparison.json": json.dumps(reference, indent=2, allow_nan=False) + "\n",
        "scenarios.csv": csv_text(programmes),
        "crew-workplan.csv": csv_text(crews),
        "comparison.md": markdown(reference, programmes),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--output", type=Path, default=HERE)
    args = parser.parse_args()
    if not args.check:
        args.output.mkdir(parents=True, exist_ok=True)
    for name, contents in build().items():
        target = args.output / name
        if args.check:
            if not target.is_file() or target.read_text() != contents:
                parser.error(f"Rebuild stale comparison file {target}")
        else:
            target.write_text(contents, encoding="utf-8")


if __name__ == "__main__":
    main()
