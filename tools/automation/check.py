#!/usr/bin/env python3
"""Select local verification tiers; an artifact failure cannot hide source tests."""

import argparse, json, sys, uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT), str(ROOT / "tools/automation")]
from local_validation import run
from engineering.design_engine.graph import build, affected

SCOPES = {
    "source": "quick",
    "unit": "python",
    "contracts": "quick",
    "rust": "rust",
    "evidence": "evidence",
    "browser": "browser",
    "stack": "integrated-stack",
    "city-stack": "example-city",
    "formal": "kani",
    "all": "ci",
}
NATIVE_ACCEPTANCE_SOURCES = {
    "engineering/analysis/tests/test_generated_parts_native.py",
    "tools/automation/tests/test_native_design_validation.py",
    "tools/automation/tests/test_impact_selection.py",
    "tools/automation/local_validation.py",
    "tools/automation/osr-python",
    "tools/automation/check.py",
}
p = argparse.ArgumentParser(description=__doc__)
p.add_argument("--scope", choices=[*SCOPES, "impact"], default="source")
p.add_argument("--changed", nargs="*", default=[])
p.add_argument("--output", type=Path)
p.add_argument("--plan", action="store_true")
a = p.parse_args()
a.changed = [Path(name).resolve().relative_to(ROOT).as_posix() for name in a.changed]
if a.scope == "impact":
    graph = build()
    selected = affected(graph, a.changed)
    profiles = ["quick"]
    if any(name.endswith(".py") for name in a.changed):
        profiles.append("python")
    if any(x.startswith("problem:") for x in selected):
        profiles += ["python", "evidence"]
    if {"problem:mechanical-cleat", "problem:civil-steel-beam"}.intersection(
        selected
    ) or NATIVE_ACCEPTANCE_SOURCES.intersection(a.changed):
        profiles.append("native-design")
    if any(
        name.endswith((".js", ".mjs", ".css", ".html"))
        or name.startswith(("docs/workbench/", "docs/design-engine/"))
        or name
        in {
            "engineering/design_engine/http.py",
            "tools/automation/workbench-server.py",
            "tools/automation/workbench_jobs.py",
        }
        for name in a.changed
    ):
        profiles.append("browser")
    if any(
        name.endswith(".rs")
        or name in {"Cargo.lock", "Cargo.toml", "rust-toolchain.toml"}
        for name in a.changed
    ):
        profiles.append("rust")
    if any(
        name.startswith(("deployment/", "services/integration/")) for name in a.changed
    ):
        profiles.append("integrated-stack")
else:
    profiles = [SCOPES[a.scope]]
    selected = []
profiles = list(dict.fromkeys(profiles))
if a.plan:
    print(
        json.dumps(
            dict(
                scope=a.scope,
                affected=selected,
                profiles=profiles,
                complete_periodic_profile="all",
                execution_location="local",
            ),
            indent=2,
        )
    )
    raise SystemExit(0)
output = a.output or ROOT / "build/validation" / ("scoped-" + uuid.uuid4().hex)
results = []
for profile in dict.fromkeys(profiles):
    try:
        results.append(run(profile, output / profile))
    except (ValueError, OSError) as error:
        results.append(dict(profile=profile, passed=False, error=str(error)))
print(
    json.dumps(
        [
            dict(profile=r["profile"], passed=r["passed"], error=r.get("error"))
            for r in results
        ],
        indent=2,
    )
)
raise SystemExit(0 if all(r["passed"] for r in results) else 1)
