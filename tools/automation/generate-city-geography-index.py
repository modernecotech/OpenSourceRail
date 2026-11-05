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

    candidate = register["candidate_id"]
    rows = []
    for city in sorted(register["cities"], key=lambda item: (item["country"], item["name"].casefold())):
        path = city["path"]
        frontdoor = quote(f"{path}/README.md", safe="/-._")
        current_hold = quote(f"{path}/engineering/current/README.md", safe="/-._")
        rows.append(
            f"| {city['country']} | [{city['name']}]({frontdoor}) "
            f"| [Engineering status]({current_hold}) "
            f"| {'available' if city['route_geography_available'] else 'not available'} |"
        )

    lines = [
        "# City geography and planning index",
        "",
        f"The current register contains **{register['city_count']} city geography records** for the selected v0.6 candidate `{candidate}`. Geography is planning context; it does not establish an adopted alignment or service result.",
        "",
        "The planning workspace edits route, stop, service and origin-destination proposals. Compile and verify an immutable handoff with:",
        "",
        "```bash",
        "./osr plan compile edits.json --output build/my-plan",
        "./osr plan verify build/my-plan",
        "```",
        "",
        "A handoff contains proposals only. It excludes vehicle, propulsion, fleet, civil quantity, cost, performance and cashflow results. The separate [priced city outlines](../../docs/design-engine/outline-completion/README.md) provide calculated service, budgets and provisional construction programmes with explicit assumptions. Engineering verification, prototype validation and deployment approval remain pending. Planning revisions do not grant movement authority.",
        "",
        "[Planning workspace](../../docs/workbench/planning/index.html) · [Current engineering status](../../docs/design-engine/current/README.md) · [Project introduction](../../README.md)",
        "",
        "| Country | City | Current packet | Route geography |",
        "|---|---|---|---|",
        *rows,
        "",
    ]
    return "\n".join(lines)


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
