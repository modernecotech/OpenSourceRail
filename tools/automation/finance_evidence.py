"""Check all declared finance input bindings, including funding schedule CSVs."""
from __future__ import annotations

import hashlib
from pathlib import Path


def stale_finance_sources(report: dict, root: Path) -> list[dict]:
    findings = []
    sources = report.get("sources", {})
    required = {name+"_sha256" for name in ("design", "scenario", "generator", "capital_model", "network_finance_model", "capex_costs", "civil_cost_model", "country_finance")}
    for key in sorted(required | {k for k in sources if k.endswith("_sha256")}):
        recorded = sources.get(key)
        relative = sources.get(key[:-7])
        path = root / relative if isinstance(relative, str) else None
        expected = hashlib.sha256(path.read_bytes()).hexdigest() if path and path.is_file() else None
        if expected is None or expected != recorded:
            findings.append({"artifact": "engineering/finance/summary.json", "source": key,
                             "expected_sha256": expected, "recorded_sha256": recorded})
    return findings
