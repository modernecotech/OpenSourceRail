#!/usr/bin/env python3
"""Generate the current city geography and planning index."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "docs/design-engine/current/cities.json"
OUTPUT = ROOT / "cities/catalogue/README.md"


def generate() -> str:
    register = json.loads(SOURCE.read_text(encoding="utf-8"))
    if register.get("schema") != "osr-current-city-catalogue/1":
        raise ValueError("current candidate-bound city register is required")
    if register.get("family") != "wheel_rail_vehicle_reference":
        raise ValueError("city register does not match the selected v0.6 family")
    if register.get("city_count") != len(register.get("cities", [])):
        raise ValueError("city register count is inconsistent")

    import hashlib
    report_index = ROOT / "docs/design-engine/city-dossiers/index.json"
    report_manifest = report_index.with_name("manifest.json")
    reports = {}
    if report_index.is_file() and report_manifest.is_file():
        manifest = json.loads(report_manifest.read_bytes())
        expected = manifest.get("files_sha256", {}).get(report_index.relative_to(ROOT).as_posix())
        if hashlib.sha256(report_index.read_bytes()).hexdigest() != expected:
            raise ValueError("City dossier index differs from its publication")
        data = json.loads(report_index.read_bytes())
        reports = {r["city"]["slug"]:r for r in data["cities"]}
        if set(reports) != {r["slug"] for r in register["cities"]}:
            raise ValueError("City dossier index coverage differs")
    rows = []
    for city in sorted(register["cities"], key=lambda item: (item["country"], item["name"].casefold())):
        # A README target is relative to this catalogue, not repository root.
        path = Path(city["path"]).relative_to("cities/catalogue").as_posix()
        frontdoor = quote(f"{path}/README.md", safe="/-._")
        hold = quote(f"{path}/engineering/current/README.md", safe="/-._")
        r = reports.get(city["slug"])
        if r:
            capital = r["installed_capital_usd"]["base"] / 1e6
            rows.append(f"| {city['country']} | [{city['name']}]({frontdoor}) | {r['route_km']:,.1f} | {r['lines']} | {r['station_complexes']} | {r['trainsets']} | ${capital:,.1f}m | [Review]({hold}) |")
        else:
            rows.append(f"| {city['country']} | [{city['name']}]({frontdoor}) | — | — | — | — | — | [Review]({hold}) |")
    return "\n".join([
        "# City railway designs and maps", "",
        f"Explore **{register['city_count']} city network outlines**. Each city dossier brings together its visible network map, line and station tables, service and fleet, civil and factory quantities, workforce, energy accounting, capital and whole-life costs, finance scenarios, site requirements and downloads.", "",
        "The figures use the exact selected calculated outline and explicit Class C estimates. A complete outline supports comparison and development; engineering verification and manufacturing or operating approval remain separate.", "",
        "[Baghdad](west-asia/Iraq/Baghdad/README.md) · [Samawah](west-asia/Iraq/Samawah/README.md) · [Interactive city atlas](../../docs/workbench/current/index.html?outlineCity=baghdad) · [Dossier methods](../../docs/design-engine/city-dossiers/README.md) · [Planning workspace](../../docs/workbench/planning/index.html) · [Project introduction](../../README.md)", "",
        "Station groups are operational line/platform groups; shared access sites and interchanges are reported separately inside each dossier. Capital is the base installed estimate for each standalone city programme. Programme totals do not assume shared factories or imply verified local prices.", "",
        "| Country | City dossier and map | Route km | Lines | Station groups | Trainsets incl. reserve | Base installed US$ | Physical evidence |",
        "|---|---|---:|---:|---:|---:|---:|---|", *rows, "",
    ])



def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="check the generated index without writing")
    args = parser.parse_args()
    text = generate()
    if args.check:
        if not OUTPUT.is_file() or OUTPUT.read_text(encoding="utf-8") != text:
            raise SystemExit("stale city geography index")
        print("current: cities/catalogue/README.md")
    else:
        OUTPUT.write_text(text, encoding="utf-8")
        print("wrote cities/catalogue/README.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
