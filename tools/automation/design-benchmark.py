#!/usr/bin/env python3
import argparse, json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT), str(ROOT / "design/component-catalogue/src")]
from engineering.design_engine.benchmarks import CASES, run

p = argparse.ArgumentParser(
    description="Run an independent bounded numerical/native reference without granting physical acceptance"
)
p.add_argument("--case", choices=CASES, required=True)
p.add_argument("--output", type=Path, required=True)
a = p.parse_args()
r = run(a.case, a.output)
print(json.dumps(r, indent=2))
raise SystemExit(0 if r["passed"] else 1)
