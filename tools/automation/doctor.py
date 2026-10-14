#!/usr/bin/env python3
"""Inspect a named local OSR environment without installing or dispatching jobs."""

import argparse, json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from engineering.design_engine.doctor import PROFILES, inspect, write_receipt

p = argparse.ArgumentParser(description=__doc__)
p.add_argument("--profile", choices=PROFILES, default="minimal")
p.add_argument("--output", type=Path)
a = p.parse_args()
result = write_receipt(a.profile, a.output) if a.output else inspect(a.profile)
print(json.dumps(result, indent=2))
raise SystemExit(0 if result["available"] else 1)
