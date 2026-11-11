"""Check selected published-city hashes referenced by the v0.6 closure ledger.

This bounded contract covers only the four compact portfolio files used by the
release workflow. The full design-closure verifier remains responsible for the
complete evidence ledger and its engineering dispositions.
"""

import json
from collections import Counter
from pathlib import Path

from engineering.v06_design_closure import release_gate


ROOT = Path(__file__).resolve().parents[1]
STATUS = "docs/design-engine/v06-design-closure/status.json"
PORTFOLIO_PATHS = {
    "docs/design-engine/outline-completion/manifest.json",
    "docs/design-engine/outline-completion/summary.json",
    "docs/design-engine/city-atlas/manifest.json",
    "docs/design-engine/city-atlas/summary.json",
}
EXPECTED_REFERENCE_COUNTS = {
    "docs/design-engine/outline-completion/manifest.json": 2,
    "docs/design-engine/outline-completion/summary.json": 2,
    "docs/design-engine/city-atlas/manifest.json": 1,
    "docs/design-engine/city-atlas/summary.json": 1,
}


def test_closure_ledger_portfolio_pointers_match_published_bytes():
    status = json.loads((ROOT / STATUS).read_bytes())
    rows = [
        (gate_id, evidence)
        for gate_id, gate in status["gates"].items()
        for evidence in gate["evidence"]
        if evidence.get("path") in PORTFOLIO_PATHS
    ]

    assert len(rows) == 6
    assert Counter(evidence["path"] for _, evidence in rows) == EXPECTED_REFERENCE_COUNTS
    for gate_id, evidence in rows:
        release_gate._recorded_file(ROOT, evidence, f"{gate_id} evidence")
