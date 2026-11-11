"""Fail-closed, source-bound v0.6 software-release readiness evaluator.

This validates the integrity and identity of recorded software acceptance
proofs. It does not judge engineering semantics or physical qualification.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import subprocess
import tomllib


CONTRACT = "campaigns/v06-software-release.toml"
STATUS = "docs/design-engine/v06-software-release/status.json"
CONTRACT_SCHEMA = "osr-v06-software-release-contract/1"
STATUS_SCHEMA = "osr-v06-software-release-status/1"
GATE_PROOF_SCHEMA = "osr-v06-software-gate-proof/1"
REVIEW_PROOF_SCHEMA = "osr-v06-software-release-review/1"
RELEASE_FLAGS = (
    "engineering_accepted",
    "physical_accepted",
    "manufacturing_release",
    "movement_authority",
    "operating_release",
)
GATE_IDS = ("SR-01", "SR-02", "SR-03", "SR-04", "SR-05", "SR-06")
_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_COMMIT = re.compile(r"^(?:[0-9a-f]{40}|[0-9a-f]{64})$")


def sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _ordinary_file(root: Path, relative: str, label: str) -> Path:
    if (not isinstance(relative, str) or not relative or "\\" in relative
            or PurePosixPath(relative).is_absolute()
            or ".." in PurePosixPath(relative).parts
            or PurePosixPath(relative).as_posix() != relative):
        raise ValueError(f"unsafe {label} path")
    path = root / relative
    if path.is_symlink() or not path.is_file() or not path.resolve().is_relative_to(root):
        raise ValueError(f"ordinary in-tree {label} file required: {relative}")
    current = path
    while current != root:
        if current.is_symlink():
            raise ValueError(f"symlink in {label} path: {relative}")
        current = current.parent
    return path


def _digest_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while block := stream.read(1024 * 1024):
            digest.update(block)
    return digest.hexdigest()


def _read_json(path: Path, label: str) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON object required for {label}")
    return value


def _source_commit(root: Path) -> str:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=root, check=True,
            capture_output=True, text=True, timeout=5,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        raise ValueError("source commit is required outside a Git checkout") from exc
    value = result.stdout.strip()
    if not _COMMIT.fullmatch(value):
        raise ValueError("Git returned an invalid source commit")
    return value


def _verify_proof(root: Path, row: dict, *, label: str, schema: str,
                  expected: dict) -> dict:
    if not isinstance(row, dict):
        raise ValueError(f"proof record required for {label}")
    path = _ordinary_file(root, row.get("path"), label)
    expected_hash = row.get("sha256")
    if not isinstance(expected_hash, str) or not _SHA256.fullmatch(expected_hash):
        raise ValueError(f"valid SHA-256 required for {label}")
    actual_hash = _digest_file(path)
    if actual_hash != expected_hash:
        raise ValueError(f"{label} content hash mismatch: {row['path']}")
    proof = _read_json(path, label)
    if proof.get("schema") != schema:
        raise ValueError(f"unexpected {label} proof schema")
    for key, value in expected.items():
        if proof.get(key) != value:
            raise ValueError(f"{label} proof {key} does not match the release record")
    return proof


def inspect(root: str | Path, *, contract_path: str = CONTRACT,
            status_path: str = STATUS, source_commit: str | None = None) -> dict:
    """Return verified software readiness without gating on design closure."""
    root = Path(root).resolve()
    contract_file = _ordinary_file(root, contract_path, "software release contract")
    status_file = _ordinary_file(root, status_path, "software release status")
    contract_bytes = contract_file.read_bytes()
    contract = tomllib.loads(contract_bytes.decode("utf-8"))
    status = _read_json(status_file, "software release status")
    if contract.get("schema") != CONTRACT_SCHEMA:
        raise ValueError("unexpected software release contract schema")
    if contract.get("status_path") != status_path:
        raise ValueError("software release contract points to a different status record")
    if (contract.get("release_commit_must_be_pinned") is not True
            or contract.get("independent_release_review_required") is not True):
        raise ValueError("software release contract must require a pinned commit and independent review")
    if status.get("schema") != STATUS_SCHEMA:
        raise ValueError("unexpected software release status schema")
    if status.get("contract_path") != contract_path:
        raise ValueError("software release status points to a different contract")
    contract_hash = sha256(contract_bytes)
    if status.get("contract_sha256") != contract_hash:
        raise ValueError("software release status is stale for its contract")
    gates = contract.get("gate", [])
    ids = [row.get("id") for row in gates if isinstance(row, dict)]
    required_ids = [row.get("id") for row in gates
                    if isinstance(row, dict) and row.get("required") is True]
    if ids != list(GATE_IDS) or required_ids != list(GATE_IDS):
        raise ValueError("software release contract must define each SR-01..SR-06 gate exactly once")
    for row in gates:
        kinds = row.get("required_evidence_kinds")
        if (not isinstance(row.get("name"), str) or not row["name"].strip()
                or not isinstance(row.get("acceptance"), str) or not row["acceptance"].strip()
                or not isinstance(kinds, list) or not kinds
                or any(not isinstance(kind, str) or not kind for kind in kinds)
                or len(kinds) != len(set(kinds))):
            raise ValueError(f"invalid required evidence contract for {row.get('id')}")
    by_id = {row["id"]: row for row in gates}
    source_commit = source_commit or _source_commit(root)
    if not isinstance(source_commit, str) or not _COMMIT.fullmatch(source_commit):
        raise ValueError("valid full source commit is required")

    release_commit = status.get("release_commit")
    if release_commit is not None:
        if not isinstance(release_commit, str) or not _COMMIT.fullmatch(release_commit):
            raise ValueError("invalid pinned software release commit")
        if release_commit != source_commit:
            raise ValueError("pinned software release commit does not match the inspected source")

    gate_status = status.get("gates")
    if not isinstance(gate_status, dict) or set(gate_status) != set(GATE_IDS):
        raise ValueError("software release status must cover each and only each SR gate")
    pending = []
    passed = 0
    for gate_id in GATE_IDS:
        row = gate_status[gate_id]
        if not isinstance(row, dict) or row.get("state") not in {"pending", "blocked", "passed"}:
            raise ValueError(f"invalid software release state for {gate_id}")
        if row["state"] != "passed":
            blocker = row.get("blocker")
            if not isinstance(blocker, str) or not blocker.strip():
                raise ValueError(f"non-passing software gate needs a visible blocker: {gate_id}")
            if row.get("evidence", []) not in ([], None):
                raise ValueError(f"non-passing software gate cannot publish passing evidence: {gate_id}")
            pending.append(dict(id=gate_id, state=row["state"], blocker=blocker))
            continue
        if release_commit != source_commit:
            raise ValueError("passing software gates require the inspected source to be pinned")
        proof_rows = row.get("evidence")
        if not isinstance(proof_rows, list) or not proof_rows:
            raise ValueError(f"passing software gate needs source-bound proof: {gate_id}")
        expected_kinds = set(by_id[gate_id].get("required_evidence_kinds", []))
        seen_kinds = set()
        for proof_row in proof_rows:
            if not isinstance(proof_row, dict):
                raise ValueError(f"invalid proof entry for {gate_id}")
            kind = proof_row.get("kind")
            if not isinstance(kind, str) or kind not in expected_kinds or kind in seen_kinds:
                raise ValueError(f"unexpected or duplicate proof kind for {gate_id}")
            _verify_proof(
                root, proof_row, label=f"{gate_id} evidence", schema=GATE_PROOF_SCHEMA,
                expected={"gate_id": gate_id, "source_commit": source_commit,
                          "contract_sha256": contract_hash, "result": "pass",
                          "evidence_kind": kind},
            )
            seen_kinds.add(kind)
        if seen_kinds != expected_kinds:
            missing = ", ".join(sorted(expected_kinds - seen_kinds))
            raise ValueError(f"{gate_id} lacks required proof kinds: {missing}")
        passed += 1

    release_review = status.get("release_review")
    if not isinstance(release_review, dict):
        raise ValueError("software release review record required")
    review_accepted = release_review.get("state") == "accepted"
    if review_accepted:
        if passed != len(GATE_IDS) or pending:
            raise ValueError("software release review cannot accept an incomplete gate set")
        reviewer = release_review.get("reviewer")
        if not isinstance(reviewer, str) or not reviewer.strip():
            raise ValueError("independent software release reviewer identity required")
        if release_commit != source_commit:
            raise ValueError("accepted software release review requires a pinned source commit")
        _verify_proof(
            root, release_review.get("evidence"), label="software release review",
            schema=REVIEW_PROOF_SCHEMA,
            expected={"decision": "approve", "reviewer": reviewer,
                      "source_commit": source_commit, "contract_sha256": contract_hash},
        )
    elif release_review.get("state") == "pending":
        blocker = release_review.get("blocker")
        if not isinstance(blocker, str) or not blocker.strip():
            raise ValueError("pending software release review needs a visible blocker")
    else:
        raise ValueError("software release review must be pending or accepted")

    flags = status.get("release_flags")
    if not isinstance(flags, dict) or any(flags.get(key) is not False for key in RELEASE_FLAGS):
        raise ValueError("software release cannot assert physical/manufacturing/operating approval")
    # A software readiness record must not author engineering-design closure.
    if status.get("engineering_design_complete") is not False:
        raise ValueError("software release status must leave engineering_design_complete false")
    if "software_release_ready" in status or "release_ready" in status:
        raise ValueError("software_release_ready is derived and must not be stored as an input claim")

    ready = passed == len(GATE_IDS) and review_accepted and release_commit == source_commit
    design = {"verified": False, "engineering_design_complete": False,
              "closed_gate_count": 0, "required_gate_count": 7}
    try:
        from engineering.v06_design_closure import release_gate as design_gate
        design_report = design_gate.inspect(root)
        design = {"verified": True,
                  "engineering_design_complete": design_report["release_ready"],
                  "closed_gate_count": design_report["closed_gate_count"],
                  "required_gate_count": design_report["required_gate_count"]}
    except (OSError, ValueError, KeyError, TypeError):
        # A failed independent design-closure audit is reported separately and
        # does not gate the software release result.
        pass

    return {
        "schema": "osr-v06-software-release-readiness/1",
        "contract_sha256": contract_hash,
        "source_commit": source_commit,
        "release_commit": release_commit,
        "required_gate_count": len(GATE_IDS),
        "passed_gate_count": passed,
        "open_gates": pending,
        "software_release_ready": ready,
        "engineering_design_complete": design["engineering_design_complete"],
        "design_closure_audit": design,
        "release_review_accepted": review_accepted,
        "release_flags": {key: False for key in RELEASE_FLAGS},
        "scope": "software proof record integrity and identity; not engineering semantic or physical qualification",
    }


def require_ready(root: str | Path, **kwargs) -> dict:
    report = inspect(root, **kwargs)
    if not report["software_release_ready"]:
        identifiers = ", ".join(row["id"] for row in report["open_gates"])
        if not identifiers:
            identifiers = "pinned release commit and independent release review"
        raise ValueError(f"v0.6 software release remains withheld: {identifiers}")
    return report
