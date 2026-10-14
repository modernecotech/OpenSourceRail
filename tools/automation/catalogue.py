#!/usr/bin/env python3
"""Index retained city payloads or regenerate only named local cities."""

import argparse, json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from engineering.design_engine.catalogue import index, selected_plan, run_selected

p = argparse.ArgumentParser(description=__doc__)
sub = p.add_subparsers(dest="action", required=True)
a = sub.add_parser("index")
a.add_argument(
    "--output", type=Path, default=ROOT / "docs/capabilities/city-artifacts.json"
)
a.add_argument("--check", action="store_true")
a = sub.add_parser("plan")
a.add_argument("--city", nargs="+", required=True)
a = sub.add_parser("run")
a.add_argument("--city", nargs="+", required=True)
a = p.parse_args()
if a.action == "index":
    value = index()
    text = json.dumps(value, indent=2, sort_keys=True) + "\n"
    if a.check:
        if not a.output.is_file() or a.output.read_text() != text:
            raise SystemExit("stale city artifact index")
    else:
        a.output.parent.mkdir(parents=True, exist_ok=True)
        a.output.write_text(text)
    print(
        len(value["cities"]),
        "cities;",
        value["total_retained_files"],
        "retained payloads",
    )
else:
    print(
        json.dumps(
            selected_plan(a.city) if a.action == "plan" else run_selected(a.city),
            indent=2,
        )
    )
