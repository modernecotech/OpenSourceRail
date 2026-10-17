"""Controller policy cannot relabel unrelated tools as trusted acceptance."""

from copy import deepcopy
from hashlib import sha256
import json
import shutil

import pytest

from engineering.generative_design import hierarchical_controller as c


def sources():
    return {
        str(p.relative_to(c.ROOT)): sha256(p.read_bytes()).hexdigest()
        for p in c._sources()
    }


def test_declared_policy_binds_fixture_commands_and_limits():
    policy = c.software_policy()
    c.validate_software_policy(policy, sources())
    # Recorded absolute paths remain valid historical provenance after relocation.
    moved = deepcopy(policy)
    old = moved["commands"][1][1]
    new = "/archive/other-checkout/" + c.FIXTURE.relative_to(c.ROOT).as_posix()
    moved["commands"][1][1] = new
    moved["acceptance_files"] = {new: moved["acceptance_files"][old]}
    c.validate_software_policy(moved, sources())


@pytest.mark.parametrize(
    "change", ["command", "fixture", "limit", "allowed", "checkout", "executable"]
)
def test_changed_acceptance_cannot_acquire_trusted_labels(change):
    policy = c.software_policy()
    if change == "command":
        policy["commands"][0] = ["python", "-c", "pass"]
    elif change == "fixture":
        policy["acceptance_files"][str(c.FIXTURE)] = "0" * 64
    elif change == "limit":
        policy["timeout_seconds"] = 1
    elif change == "executable":
        policy["commands"][0][0] = policy["commands"][1][0] = "/bin/true"
    elif change == "allowed":
        policy["allowed_paths"].append(
            "engineering/analysis/tests/test_mechanical_detail.py"
        )
    else:
        policy["checkout_paths"] = ["README.md"]
    with pytest.raises(ValueError, match="acceptance policy differs"):
        c.validate_software_policy(policy, sources())


def test_decisions_use_actual_fixture_and_parent_test_outcomes(tmp_path):
    rows = []
    for identity, states in [
        ("unmodified-baseline", ["passed", "failed"]),
        ("strict-section-dimensions", ["passed", "passed"]),
        ("attractive-zero-deflection-regression", ["failed"]),
    ]:
        rows.append(
            dict(
                proposal_id=identity,
                role="software-developer",
                status="completed" if all(s == "passed" for s in states) else "failed",
                tools=[dict(state=s) for s in states],
                artifact_directory="jobs/runs/" + identity,
                changed_paths=["engineering/generative_design/mechanical_detail.py"],
                base_commit="a" * 40,
            )
        )
    result = c.software_decisions(dict(results=rows, policy_sha256="b" * 64), tmp_path)
    assert [r["disposition"] for r in result["decisions"]] == [
        "REJECT",
        "ADOPT-EXPERIMENTAL",
        "REJECT",
    ]
    revision = result["decisions"][1]["experimental_revision"]
    assert revision["state"] == "experimental-computational-baseline"
    assert revision["manufacturing_release"] is False


def test_resealed_report_cannot_omit_required_source_membership(tmp_path):
    source = c.ROOT / "docs/design-engine/hierarchical-pilot-2026-10-17"
    target = tmp_path / "packet"
    shutil.copytree(source, target)
    report = json.loads((target / "report.json").read_text())
    report["source_sha256"] = {}
    (target / "report.json").write_text(json.dumps(report))
    (target / "receipt.json").unlink()
    c._seal(target)
    with pytest.raises(ValueError, match="source membership differs"):
        c.verify(target, current=False)
