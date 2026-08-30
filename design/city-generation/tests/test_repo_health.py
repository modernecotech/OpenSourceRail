"""Repository-wide drift guard for generated catalogue artifacts."""

from __future__ import annotations

import runpy
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
HEALTH_SCRIPT = REPO_ROOT / "tools/automation/repo-health.py"


def test_repo_health_checks_pass() -> None:
    module = runpy.run_path(str(HEALTH_SCRIPT))
    findings = module["run_checks"]()
    assert not findings, "\n".join(f.render() for f in findings)
