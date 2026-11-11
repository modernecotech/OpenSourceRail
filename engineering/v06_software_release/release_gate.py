"""Fail-closed, source-bound v0.6 software-release readiness evaluator.

This validates the integrity and identity of recorded software acceptance
proofs. It does not judge engineering semantics or physical qualification.
"""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import subprocess
import tempfile
import tomllib


CONTRACT = "campaigns/v06-software-release.toml"
STATUS = "docs/design-engine/v06-software-release/status.json"
CONTRACT_SCHEMA = "osr-v06-software-release-contract/1"
STATUS_SCHEMA = "osr-v06-software-release-status/1"
GATE_PROOF_SCHEMA = "osr-v06-software-gate-proof/1"
ATTESTATION_SCHEMA = "osr-v06-software-release-attestation/1"
AUTHENTICATED_REVIEW_SCHEMA = "osr-v06-authenticated-release-review/1"
RELEASE_FLAGS = (
    "engineering_accepted",
    "physical_accepted",
    "manufacturing_release",
    "movement_authority",
    "operating_release",
)
GATE_IDS = ("SR-01", "SR-02", "SR-03", "SR-04", "SR-05", "SR-06")
CI_REQUIRED_RUNS = {
    ".github/workflows/v06-software-release.yml":
        "Selected v0.6 software and resource contracts",
    ".github/workflows/v06-software-journey.yml":
        "Samawah Workbench journey and bounded exports",
    ".github/workflows/v06-software-rust.yml":
        "Rust control contract tests",
}
_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_COMMIT = re.compile(r"^(?:[0-9a-f]{40}|[0-9a-f]{64})$")


def sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def identity(value: object) -> str:
    raw = (json.dumps(value, sort_keys=True, separators=(",", ":"),
                      allow_nan=False) + "\n").encode("utf-8")
    return sha256(raw)


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


def _read_ordinary_file(root: Path, relative: str, *, label: str) -> tuple[bytes, str]:
    _ordinary_file(root, relative, label)
    parts = PurePosixPath(relative).parts
    directory_fd = os.open(root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        for part in parts[:-1]:
            next_fd = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW,
                              dir_fd=directory_fd)
            os.close(directory_fd)
            directory_fd = next_fd
        file_fd = os.open(parts[-1], os.O_RDONLY | os.O_NOFOLLOW, dir_fd=directory_fd)
        try:
            if not stat.S_ISREG(os.fstat(file_fd).st_mode):
                raise ValueError(f"ordinary in-tree {label} file required: {relative}")
            chunks = []
            while chunk := os.read(file_fd, 1024 * 1024):
                chunks.append(chunk)
            raw = b"".join(chunks)
        finally:
            os.close(file_fd)
    finally:
        os.close(directory_fd)
    return raw, sha256(raw)


def _read_verified_file(root: Path, row: dict, *, label: str) -> tuple[bytes, str]:
    if not isinstance(row, dict) or not {"path", "sha256"}.issubset(row):
        raise ValueError(f"proof reference required for {label}")
    raw, actual_hash = _read_ordinary_file(root, row.get("path"), label=label)
    expected_hash = row.get("sha256")
    if not isinstance(expected_hash, str) or not _SHA256.fullmatch(expected_hash):
        raise ValueError(f"valid SHA-256 required for {label}")
    if actual_hash != expected_hash:
        raise ValueError(f"{label} content hash mismatch: {row['path']}")
    return raw, actual_hash


def _verify_ed25519(public_key: bytes, message: bytes, signature: bytes) -> str:
    """Verify a detached Ed25519 signature using the platform OpenSSL tool."""
    try:
        with tempfile.TemporaryDirectory(prefix="osr-release-signature-") as directory:
            root = Path(directory)
            key_path = root / "reviewer-public-key.pem"
            message_path = root / "review-proof.json"
            signature_path = root / "review-proof.sig"
            key_path.write_bytes(public_key)
            message_path.write_bytes(message)
            signature_path.write_bytes(signature)
            exported = subprocess.run(
                ["openssl", "pkey", "-pubin", "-in", str(key_path), "-outform", "DER"],
                check=True, capture_output=True, timeout=10,
            ).stdout
            if (not exported.startswith(bytes.fromhex("302a300506032b6570032100"))
                    or len(exported) != 44 or len(signature) != 64):
                raise ValueError("release-review signatures must use Ed25519")
            verified = subprocess.run(
                ["openssl", "pkeyutl", "-verify", "-pubin", "-inkey", str(key_path),
                 "-rawin", "-in", str(message_path), "-sigfile", str(signature_path)],
                check=False, capture_output=True, timeout=10,
            )
    except FileNotFoundError as exc:
        raise ValueError("OpenSSL is required to authenticate the release reviewer") from exc
    except subprocess.CalledProcessError as exc:
        raise ValueError("release reviewer public key is invalid") from exc
    except subprocess.TimeoutExpired as exc:
        raise ValueError("release reviewer signature verification timed out") from exc
    except (OSError, subprocess.SubprocessError) as exc:
        raise ValueError("release reviewer signature verification failed") from exc
    if verified.returncode != 0:
        raise ValueError("independent release-review signature is invalid")
    return sha256(exported)


def _read_json(path: Path, label: str) -> dict:
    return _json_object(path.read_bytes(), label)


def _json_object(raw: bytes, label: str) -> dict:
    def reject_duplicate_keys(pairs):
        value = {}
        for key, item in pairs:
            if key in value:
                raise ValueError(f"duplicate JSON key in {label}: {key}")
            value[key] = item
        return value

    value = json.loads(raw.decode("utf-8"), object_pairs_hook=reject_duplicate_keys)
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


def _source_tree(root: Path, commit: str) -> str:
    try:
        result = subprocess.run(
            ["git", "rev-parse", f"{commit}^{{tree}}"], cwd=root, check=True,
            capture_output=True, text=True, timeout=5,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        raise ValueError("source tree is required for release attestation") from exc
    value = result.stdout.strip()
    if not _COMMIT.fullmatch(value):
        raise ValueError("Git returned an invalid source tree")
    return value


def _require_clean_checkout(root: Path) -> None:
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain", "--untracked-files=all"],
            cwd=root, check=True, capture_output=True, text=True, timeout=10,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        raise ValueError("a clean Git checkout is required for release attestation") from exc
    if result.stdout.strip():
        raise ValueError("clean Git checkout required for external release attestation")
    try:
        entries = subprocess.run(
            ["git", "ls-files", "-v", "-z"], cwd=root, check=True,
            capture_output=True, timeout=10,
        ).stdout.split(b"\0")
    except (OSError, subprocess.SubprocessError) as exc:
        raise ValueError("tracked Git index state is required for release attestation") from exc
    if any(entry and (len(entry) < 2 or entry[0:1] != b"H" or entry[1:2] != b" ")
           for entry in entries):
        raise ValueError("full checkout without assume-unchanged or sparse index flags required")


def _bundle_directory(source_root: Path, supplied: str | Path) -> Path:
    candidate = Path(supplied).expanduser()
    if not candidate.is_absolute():
        candidate = source_root / candidate
    candidate = candidate.absolute()
    for part in (candidate, *candidate.parents):
        if part.is_symlink():
            raise ValueError("symlink in external release attestation path")
    try:
        bundle_root = candidate.resolve(strict=True)
    except OSError as exc:
        raise ValueError("external release attestation directory is unavailable") from exc
    if not bundle_root.is_dir():
        raise ValueError("external release attestation directory required")
    if (bundle_root.is_relative_to(source_root)
            or source_root.is_relative_to(bundle_root)):
        raise ValueError("release attestation bundle must be separate from the source checkout")
    return bundle_root


def _verify_proof(root: Path, row: dict, *, label: str, schema: str,
                  expected: dict) -> dict:
    raw, _ = _read_verified_file(root, row, label=label)
    proof = _json_object(raw, label)
    if proof.get("schema") != schema:
        raise ValueError(f"unexpected {label} proof schema")
    for key, value in expected.items():
        if proof.get(key) != value:
            raise ValueError(f"{label} proof {key} does not match the release record")
    return proof


def _verify_required_ci_proof(proof: dict, *, repository: str,
                              source_commit: str) -> None:
    required = {"schema", "gate_id", "source_commit", "contract_sha256", "result",
                "evidence_kind", "ci_provider", "repository", "workflow_runs"}
    if set(proof) != required:
        raise ValueError("SR-02 proof must identify the required GitHub Actions runs")
    if proof.get("ci_provider") != "github-actions" or proof.get("repository") != repository:
        raise ValueError("SR-02 proof must name the trusted GitHub repository and provider")
    runs = proof.get("workflow_runs")
    if not isinstance(runs, list) or len(runs) != len(CI_REQUIRED_RUNS):
        raise ValueError("SR-02 proof must include each required v0.6 workflow run")
    seen = set()
    for run in runs:
        fields = {"workflow_file", "run_id", "run_attempt", "run_url", "check_name",
                  "head_sha", "conclusion"}
        if not isinstance(run, dict) or set(run) != fields:
            raise ValueError("SR-02 workflow run reference fields differ")
        workflow_file = run.get("workflow_file")
        if workflow_file not in CI_REQUIRED_RUNS or workflow_file in seen:
            raise ValueError("SR-02 proof contains an unexpected or duplicate workflow")
        seen.add(workflow_file)
        run_id, attempt = run.get("run_id"), run.get("run_attempt")
        if (not isinstance(run_id, int) or isinstance(run_id, bool) or run_id <= 0
                or not isinstance(attempt, int) or isinstance(attempt, bool) or attempt <= 0):
            raise ValueError("SR-02 workflow run ID and attempt must be positive integers")
        expected_url = f"https://github.com/{repository}/actions/runs/{run_id}"
        if run.get("run_url") != expected_url:
            raise ValueError("SR-02 workflow run URL does not match the trusted repository and ID")
        if run.get("check_name") != CI_REQUIRED_RUNS[workflow_file]:
            raise ValueError("SR-02 workflow check name differs from the release contract")
        if run.get("head_sha") != source_commit or run.get("conclusion") != "success":
            raise ValueError("SR-02 workflow run must pass on the exact release commit")
    if seen != set(CI_REQUIRED_RUNS):
        raise ValueError("SR-02 proof lacks a required release workflow")


def _verify_external_attestation(source_root: Path, supplied: str | Path, *,
                                 contract: dict, contract_hash: str,
                                 source_commit: str, source_tree: str,
                                 by_id: dict, expected_repository: str | None,
                                 trusted_reviewer: str | None,
                                 trusted_reviewer_key_sha256: str | None) -> dict:
    bundle_root = _bundle_directory(source_root, supplied)
    _require_clean_checkout(source_root)
    manifest_bytes, manifest_hash = _read_ordinary_file(
        bundle_root, "attestation.json", label="release attestation manifest")
    manifest = _json_object(manifest_bytes, "release attestation manifest")
    required_fields = {
        "schema", "repository", "release", "source_commit", "source_tree", "contract_sha256",
        "gates", "release_review", "release_flags", "engineering_design_complete",
        "attestation_id",
    }
    if set(manifest) != required_fields:
        raise ValueError("external release attestation fields differ from the schema")
    if manifest.get("schema") != ATTESTATION_SCHEMA:
        raise ValueError("unexpected external release attestation schema")
    repository = contract.get("repository")
    if not isinstance(repository, str) or not repository.strip():
        raise ValueError("release contract must pin its canonical repository identity")
    if not isinstance(expected_repository, str) or not expected_repository.strip():
        raise ValueError("out-of-band expected repository identity is required")
    if repository != expected_repository:
        raise ValueError("release contract repository differs from out-of-band expected repository")
    if manifest.get("repository") != repository:
        raise ValueError("external release attestation names a different repository")
    subject = {key: value for key, value in manifest.items()
               if key in {"schema", "repository", "release", "source_commit", "source_tree",
                          "contract_sha256", "gates", "release_flags",
                          "engineering_design_complete"}}
    if manifest.get("attestation_id") != identity(subject):
        raise ValueError("external release attestation identity differs")
    if manifest.get("release") != contract.get("release"):
        raise ValueError("external release attestation names a different release")
    if manifest.get("source_commit") != source_commit:
        raise ValueError("external release attestation source commit differs from Git HEAD")
    if manifest.get("source_tree") != source_tree:
        raise ValueError("external release attestation source tree differs from Git HEAD")
    if manifest.get("contract_sha256") != contract_hash:
        raise ValueError("external release attestation contract hash differs")
    flags = manifest.get("release_flags")
    if (not isinstance(flags, dict)
            or set(flags) != set(RELEASE_FLAGS)
            or any(flags.get(key) is not False for key in RELEASE_FLAGS)
            or manifest.get("engineering_design_complete") is not False):
        raise ValueError("external software attestation cannot assert engineering or physical acceptance")

    gates = manifest.get("gates")
    if not isinstance(gates, dict) or set(gates) != set(GATE_IDS):
        raise ValueError("external release attestation must cover each and only each SR gate")
    for gate_id in GATE_IDS:
        row = gates[gate_id]
        if not isinstance(row, dict) or set(row) != {"state", "evidence"} or row.get("state") != "passed":
            raise ValueError(f"external release attestation does not pass {gate_id}")
        proof_rows = row.get("evidence")
        if not isinstance(proof_rows, list):
            raise ValueError(f"external release attestation evidence list required for {gate_id}")
        expected_kinds = set(by_id[gate_id].get("required_evidence_kinds", []))
        seen_kinds = set()
        for proof_row in proof_rows:
            if not isinstance(proof_row, dict) or set(proof_row) != {"kind", "path", "sha256"}:
                raise ValueError(f"invalid external proof entry for {gate_id}")
            kind = proof_row.get("kind")
            if not isinstance(kind, str) or kind not in expected_kinds or kind in seen_kinds:
                raise ValueError(f"unexpected or duplicate external proof kind for {gate_id}")
            proof = _verify_proof(
                bundle_root, proof_row, label=f"{gate_id} evidence", schema=GATE_PROOF_SCHEMA,
                expected={"gate_id": gate_id, "source_commit": source_commit,
                          "contract_sha256": contract_hash, "result": "pass",
                          "evidence_kind": kind},
            )
            if gate_id == "SR-02" and kind == "same-commit-required-ci":
                _verify_required_ci_proof(proof, repository=repository,
                                          source_commit=source_commit)
            seen_kinds.add(kind)
        if seen_kinds != expected_kinds:
            missing = ", ".join(sorted(expected_kinds - seen_kinds))
            raise ValueError(f"{gate_id} lacks required external proof kinds: {missing}")

    review = manifest.get("release_review")
    if (not isinstance(review, dict)
            or set(review) != {"state", "reviewer", "evidence", "public_key", "signature"}
            or review.get("state") != "accepted"):
        raise ValueError("accepted external independent software release review required")
    reviewer = review.get("reviewer")
    if not isinstance(reviewer, str) or not reviewer.strip():
        raise ValueError("independent software release reviewer identity required")
    if not isinstance(trusted_reviewer, str) or not trusted_reviewer.strip():
        raise ValueError("out-of-band trusted reviewer identity is required")
    if reviewer != trusted_reviewer:
        raise ValueError("release reviewer identity does not match the out-of-band trusted reviewer")
    if (not isinstance(trusted_reviewer_key_sha256, str)
            or not _SHA256.fullmatch(trusted_reviewer_key_sha256)):
        raise ValueError("trusted reviewer public-key SHA-256 fingerprint is required")
    evidence_raw, evidence_hash = _read_verified_file(
        bundle_root, review.get("evidence"), label="software release review")
    proof = _json_object(evidence_raw, "software release review proof")
    if proof.get("schema") != AUTHENTICATED_REVIEW_SCHEMA:
        raise ValueError("authenticated software release review proof required")
    expected_review = {
        "decision": "approve", "reviewer": reviewer, "repository": repository,
        "source_commit": source_commit, "source_tree": source_tree,
        "contract_sha256": contract_hash, "attestation_id": manifest["attestation_id"],
        "scope": "independent-software-release-review",
    }
    if proof != expected_review | {"schema": AUTHENTICATED_REVIEW_SCHEMA}:
        raise ValueError("software release review proof does not bind the exact attestation")
    public_key, key_file_hash = _read_verified_file(
        bundle_root, review.get("public_key"), label="release reviewer public key")
    if review.get("public_key", {}).get("sha256") != key_file_hash:
        raise ValueError("release reviewer public-key file hash differs")
    signature, _ = _read_verified_file(
        bundle_root, review.get("signature"), label="release reviewer signature")
    key_fingerprint = _verify_ed25519(public_key, evidence_raw, signature)
    if key_fingerprint != trusted_reviewer_key_sha256:
        raise ValueError("release reviewer key does not match the out-of-band trusted fingerprint")
    return {
        "attestation_id": manifest["attestation_id"],
        "attestation_sha256": manifest_hash,
        "reviewer": reviewer,
        "reviewer_identity": reviewer,
        "reviewer_key_sha256": key_fingerprint,
        "review_proof_sha256": evidence_hash,
        "review_authenticated": True,
    }


def inspect(root: str | Path, *, contract_path: str = CONTRACT,
            status_path: str = STATUS, source_commit: str | None = None,
            attestation_bundle: str | Path | None = None,
            expected_repository: str | None = None,
            trusted_reviewer: str | None = None,
            trusted_reviewer_key_sha256: str | None = None) -> dict:
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
    actual_source_commit = _source_commit(root)
    if source_commit is not None and source_commit != actual_source_commit:
        raise ValueError("requested source commit does not match Git HEAD")
    source_commit = actual_source_commit
    source_tree = _source_tree(root, source_commit)

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
    release_review = status.get("release_review")
    if not isinstance(release_review, dict):
        raise ValueError("software release review record required")
    attestation = None
    if attestation_bundle is not None:
        if release_commit is not None:
            raise ValueError("development dashboard must remain unpinned when using an external attestation")
        for gate_id in GATE_IDS:
            row = gate_status[gate_id]
            if (not isinstance(row, dict) or row.get("state") not in {"pending", "blocked"}
                    or not isinstance(row.get("blocker"), str) or not row["blocker"].strip()
                    or row.get("evidence", []) not in ([], None)):
                raise ValueError("in-tree release dashboard must remain pending during external attestation")
        if (release_review.get("state") != "pending"
                or not isinstance(release_review.get("blocker"), str)
                or not release_review["blocker"].strip()):
            raise ValueError("in-tree release review dashboard must remain pending during external attestation")
        attestation = _verify_external_attestation(
            root, attestation_bundle, contract=contract, contract_hash=contract_hash,
            source_commit=source_commit, source_tree=source_tree, by_id=by_id,
            expected_repository=expected_repository,
            trusted_reviewer=trusted_reviewer,
            trusted_reviewer_key_sha256=trusted_reviewer_key_sha256)
        passed = len(GATE_IDS)
        review_accepted = True
        release_commit = source_commit
    else:
        for gate_id in GATE_IDS:
            row = gate_status[gate_id]
            if not isinstance(row, dict) or row.get("state") not in {"pending", "blocked", "passed"}:
                raise ValueError(f"invalid software release state for {gate_id}")
            if row["state"] == "passed":
                raise ValueError("passing proofs must be supplied in an external release attestation bundle")
            blocker = row.get("blocker")
            if not isinstance(blocker, str) or not blocker.strip():
                raise ValueError(f"non-passing software gate needs a visible blocker: {gate_id}")
            if row.get("evidence", []) not in ([], None):
                raise ValueError(f"non-passing software gate cannot publish passing evidence: {gate_id}")
            pending.append(dict(id=gate_id, state=row["state"], blocker=blocker))
        if release_review.get("state") != "pending":
            raise ValueError("passing software review must be supplied in an external release attestation bundle")
        blocker = release_review.get("blocker")
        if not isinstance(blocker, str) or not blocker.strip():
            raise ValueError("pending software release review needs a visible blocker")
        review_accepted = False

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
    except (ImportError, OSError, ValueError, KeyError, TypeError):
        # A failed independent design-closure audit is reported separately and
        # does not gate the software release result.
        pass

    return {
        "schema": "osr-v06-software-release-readiness/1",
        "contract_sha256": contract_hash,
        "source_commit": source_commit,
        "source_tree": source_tree,
        "release_commit": release_commit,
        "required_gate_count": len(GATE_IDS),
        "passed_gate_count": passed,
        "open_gates": pending,
        "software_release_ready": ready,
        "engineering_design_complete": design["engineering_design_complete"],
        "design_closure_audit": design,
        "release_review_accepted": review_accepted,
        "release_review_authenticated": bool(attestation and attestation.get("review_authenticated")),
        "attestation": attestation,
        "release_flags": {key: False for key in RELEASE_FLAGS},
        "scope": "source-bound software proof integrity and required Actions run references plus reviewer identity/key matched to out-of-band trusted values; reviewer semantics and physical qualification remain separate",
    }


def require_ready(root: str | Path, **kwargs) -> dict:
    report = inspect(root, **kwargs)
    if not report["software_release_ready"]:
        identifiers = ", ".join(row["id"] for row in report["open_gates"])
        if not identifiers:
            identifiers = "pinned release commit and independent release review"
        raise ValueError(f"v0.6 software release remains withheld: {identifiers}")
    return report
