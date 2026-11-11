import hashlib
import json
from pathlib import Path
import tomllib

import pytest

from engineering.v06_software_release import release_gate


ROOT = Path(__file__).resolve().parents[1]
SOURCE = "1" * 40


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def _write_proof(root, relative, body):
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    raw = (json.dumps(body, sort_keys=True, separators=(",", ":")) + "\n").encode()
    path.write_bytes(raw)
    return {"path": relative, "sha256": digest(raw)}


def _ready_fixture(tmp_path):
    root = tmp_path
    contract_path = "campaigns/v06-software-release.toml"
    contract_bytes = (ROOT / contract_path).read_bytes()
    (root / contract_path).parent.mkdir(parents=True)
    (root / contract_path).write_bytes(contract_bytes)
    contract = tomllib.loads(contract_bytes.decode())
    contract_hash = digest(contract_bytes)
    gates = {}
    for gate in contract["gate"]:
        evidence = []
        for index, kind in enumerate(gate["required_evidence_kinds"]):
            relative = f"docs/proofs/{gate['id'].lower()}-{index}.json"
            proof = {
                "schema": release_gate.GATE_PROOF_SCHEMA,
                "gate_id": gate["id"],
                "source_commit": SOURCE,
                "contract_sha256": contract_hash,
                "result": "pass",
                "evidence_kind": kind,
            }
            evidence.append({"kind": kind, **_write_proof(root, relative, proof)})
        gates[gate["id"]] = {"state": "passed", "evidence": evidence}
    review_relative = "docs/proofs/software-release-review.json"
    review_proof = {
        "schema": release_gate.REVIEW_PROOF_SCHEMA,
        "decision": "approve",
        "reviewer": "independent-reviewer",
        "source_commit": SOURCE,
        "contract_sha256": contract_hash,
    }
    review = {
        "state": "accepted",
        "reviewer": "independent-reviewer",
        "evidence": _write_proof(root, review_relative, review_proof),
    }
    status = {
        "schema": release_gate.STATUS_SCHEMA,
        "contract_path": contract_path,
        "contract_sha256": contract_hash,
        "release_commit": SOURCE,
        "engineering_design_complete": False,
        "release_flags": {name: False for name in release_gate.RELEASE_FLAGS},
        "gates": gates,
        "release_review": review,
    }
    status_path = "docs/design-engine/v06-software-release/status.json"
    target = root / status_path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")
    return root, status_path, status


def test_current_software_release_status_is_truthfully_pending_and_separate():
    report = release_gate.inspect(ROOT)
    assert report["required_gate_count"] == 6
    assert report["passed_gate_count"] == 0
    assert report["software_release_ready"] is False
    assert [row["id"] for row in report["open_gates"]] == list(release_gate.GATE_IDS)
    assert report["engineering_design_complete"] is False
    assert all(value is False for value in report["release_flags"].values())
    with pytest.raises(ValueError, match="software release remains withheld"):
        release_gate.require_ready(ROOT)


def test_software_release_can_pass_while_design_closure_is_unavailable(tmp_path):
    root, _, _ = _ready_fixture(tmp_path)
    report = release_gate.inspect(root, source_commit=SOURCE)
    assert report["software_release_ready"] is True
    assert report["passed_gate_count"] == 6
    assert report["engineering_design_complete"] is False
    assert report["design_closure_audit"]["verified"] is False
    assert all(value is False for value in report["release_flags"].values())


def test_stale_commit_and_tampered_proof_fail_closed(tmp_path):
    root, status_path, status = _ready_fixture(tmp_path)
    with pytest.raises(ValueError, match="does not match the inspected source"):
        release_gate.inspect(root, source_commit="2" * 40)

    first = status["gates"]["SR-01"]["evidence"][0]["path"]
    (root / first).write_text("tampered", encoding="utf-8")
    with pytest.raises(ValueError, match="content hash mismatch"):
        release_gate.inspect(root, source_commit=SOURCE)

def test_direct_readiness_claim_is_rejected(tmp_path):
    root, status_path, status = _ready_fixture(tmp_path)
    status["software_release_ready"] = True
    (root / status_path).write_text(json.dumps(status), encoding="utf-8")
    with pytest.raises(ValueError, match="derived"):
        release_gate.inspect(root, source_commit=SOURCE)


def test_missing_required_proof_kind_blocks_software_readiness(tmp_path):
    root, status_path, status = _ready_fixture(tmp_path)
    status["gates"]["SR-03"]["evidence"].pop()
    (root / status_path).write_text(json.dumps(status), encoding="utf-8")
    with pytest.raises(ValueError, match="lacks required proof kinds"):
        release_gate.inspect(root, source_commit=SOURCE)


def test_true_physical_or_operating_flag_is_rejected(tmp_path):
    root, status_path, status = _ready_fixture(tmp_path)
    status["release_flags"]["physical_accepted"] = True
    (root / status_path).write_text(json.dumps(status), encoding="utf-8")
    with pytest.raises(ValueError, match="cannot assert physical"):
        release_gate.inspect(root, source_commit=SOURCE)


def test_contract_hash_mismatch_is_rejected(tmp_path):
    root, _, status = _ready_fixture(tmp_path)
    status["contract_sha256"] = "0" * 64
    (root / "docs/design-engine/v06-software-release/status.json").write_text(
        json.dumps(status), encoding="utf-8")
    with pytest.raises(ValueError, match="stale for its contract"):
        release_gate.inspect(root, source_commit=SOURCE)
