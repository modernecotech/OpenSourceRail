#!/usr/bin/env python3
"""Run validation on this machine; GitHub is used only for storage/publication."""

import argparse, json, uuid
from pathlib import Path
from local_validation import ROOT, PROFILES, plan, run, verify

p = argparse.ArgumentParser(description=__doc__)
sub = p.add_subparsers(dest="action", required=True)
a = sub.add_parser("run")
a.add_argument("--profile", choices=PROFILES, default="quick")
a.add_argument("--output", type=Path)
a = sub.add_parser("plan")
a.add_argument("--profile", choices=PROFILES, default="quick")
a.add_argument("--output", type=Path, default=ROOT / "build/validation/preview")
a = sub.add_parser("verify")
a.add_argument("directory", type=Path)
a = p.parse_args()
if a.action == "plan":
    print(json.dumps(plan(a.profile, a.output.resolve()), indent=2))
elif a.action == "verify":
    verify(a.directory)
    print("Local source, command coverage and output hashes match")
else:
    if a.output is None:
        a.output = ROOT / "build/validation" / str(uuid.uuid4())
    r = run(a.profile, a.output)
    print("Local validation receipt:", a.output / "receipt.json")
    if not r["passed"]:
        raise SystemExit(1)
