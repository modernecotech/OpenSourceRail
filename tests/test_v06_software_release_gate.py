import hashlib
import json
from pathlib import Path
import subprocess
import tomllib

import pytest

from engineering.v06_software_release import release_gate


ROOT = Path(__file__).resolve().parents[1]
TRUSTED_REPOSITORY = "modernecotech/OpenSourceRail"
TRUSTED_REVIEWER = "Release Review Key Example"


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def _git(root, *args):
    result = subprocess.run(
        ["git", *args], cwd=root, check=True, capture_output=True, text=True,
    )
    return result.stdout.strip()


def _write_json(path, value):
    raw = (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(raw)
    return raw


def _write_proof(root, relative, body):
    path = root / relative
    raw = _write_json(path, body)
    return {"path": relative, "sha256": digest(raw)}


def _clean_checkout(tmp_path):
    root = tmp_path / "checkout"
    contract_path = "campaigns/v06-software-release.toml"
    status_path = "docs/design-engine/v06-software-release/status.json"
    (root / contract_path).parent.mkdir(parents=True)
    (root / contract_path).write_bytes((ROOT / contract_path).read_bytes())
    (root / status_path).parent.mkdir(parents=True)
    (root / status_path).write_bytes((ROOT / status_path).read_bytes())
    _git(root, "init", "-q")
    _git(root, "config", "user.name", "OpenSourceRail test")
    _git(root, "config", "user.email", "osr-test@example.invalid")
    _git(root, "add", contract_path, status_path)
    _git(root, "commit", "-qm", "Create pending software release dashboard")
    return root, _git(root, "rev-parse", "HEAD")


def _attestation_fixture(tmp_path):
    root, source = _clean_checkout(tmp_path)
    bundle_root = tmp_path / "external-attestation"
    contract_path = "campaigns/v06-software-release.toml"
    contract_bytes = (root / contract_path).read_bytes()
    contract = tomllib.loads(contract_bytes.decode())
    contract_hash = digest(contract_bytes)
    source_tree = _git(root, "rev-parse", "HEAD^{tree}")
    gates = {}
    for gate in contract["gate"]:
        evidence = []
        for index, kind in enumerate(gate["required_evidence_kinds"]):
            relative = f"proofs/{gate['id'].lower()}-{index}.json"
            proof = {
                "schema": release_gate.GATE_PROOF_SCHEMA,
                "gate_id": gate["id"],
                "source_commit": source,
                "contract_sha256": contract_hash,
                "result": "pass",
                "evidence_kind": kind,
            }
            if gate["id"] == "SR-02":
                proof.update({
                    "ci_provider": "github-actions",
                    "repository": contract["repository"],
                    "workflow_runs": [
                        {
                            "workflow_file": workflow,
                            "run_id": index + 120000,
                            "run_attempt": 1,
                            "run_url": f"https://github.com/{contract['repository']}/actions/runs/{index + 120000}",
                            "check_name": name,
                            "head_sha": source,
                            "conclusion": "success",
                        }
                        for index, (workflow, name) in enumerate(
                            release_gate.CI_REQUIRED_RUNS.items())
                    ],
                })
            evidence.append({"kind": kind, **_write_proof(bundle_root, relative, proof)})
        gates[gate["id"]] = {"state": "passed", "evidence": evidence}

    reviewer = TRUSTED_REVIEWER
    bundle = {
        "schema": release_gate.ATTESTATION_SCHEMA,
        "repository": contract["repository"],
        "release": contract["release"],
        "source_commit": source,
        "source_tree": source_tree,
        "contract_sha256": contract_hash,
        "gates": gates,
        "release_flags": {name: False for name in release_gate.RELEASE_FLAGS},
        "engineering_design_complete": False,
    }
    bundle["attestation_id"] = release_gate.identity(bundle)
    private_key = tmp_path / "reviewer-private.pem"
    public_key_path = bundle_root / "proofs" / "reviewer-public.pem"
    signature_path = bundle_root / "proofs" / "release-review.sig"
    subprocess.run(["openssl", "genpkey", "-algorithm", "ED25519", "-out", str(private_key)],
                   check=True, capture_output=True)
    subprocess.run(["openssl", "pkey", "-in", str(private_key), "-pubout", "-out",
                    str(public_key_path)], check=True, capture_output=True)
    review_proof = {
        "schema": release_gate.AUTHENTICATED_REVIEW_SCHEMA,
        "decision": "approve",
        "reviewer": reviewer,
        "repository": contract["repository"],
        "source_commit": source,
        "source_tree": source_tree,
        "contract_sha256": contract_hash,
        "attestation_id": bundle["attestation_id"],
        "scope": "independent-software-release-review",
    }
    review_bytes = (json.dumps(review_proof, sort_keys=True, separators=(",", ":")) + "\n").encode()
    review_path = bundle_root / "proofs" / "release-review.json"
    review_path.parent.mkdir(parents=True, exist_ok=True)
    review_path.write_bytes(review_bytes)
    subprocess.run(["openssl", "pkeyutl", "-sign", "-inkey", str(private_key), "-rawin",
                    "-in", str(review_path), "-out", str(signature_path)],
                   check=True, capture_output=True)
    bundle["release_review"] = {
        "state": "accepted",
        "reviewer": reviewer,
        "evidence": {"path": "proofs/release-review.json", "sha256": digest(review_bytes)},
        "public_key": {"path": "proofs/reviewer-public.pem", "sha256": digest(public_key_path.read_bytes())},
        "signature": {"path": "proofs/release-review.sig", "sha256": digest(signature_path.read_bytes())},
    }
    _write_json(bundle_root / "attestation.json", bundle)
    fingerprint = release_gate._verify_ed25519(
        public_key_path.read_bytes(), review_bytes, signature_path.read_bytes())
    return root, source, bundle_root, bundle, fingerprint


def _inspect_attestation(root, bundle_root, **kwargs):
    kwargs.setdefault("expected_repository", TRUSTED_REPOSITORY)
    kwargs.setdefault("trusted_reviewer", TRUSTED_REVIEWER)
    return release_gate.inspect(root, attestation_bundle=bundle_root, **kwargs)


def _rewrite_bundle(bundle_root, bundle):
    bundle = {key: value for key, value in bundle.items() if key != "attestation_id"}
    subject = {key: value for key, value in bundle.items()
               if key in {"schema", "repository", "release", "source_commit", "source_tree",
                          "contract_sha256", "gates", "release_flags",
                          "engineering_design_complete"}}
    bundle["attestation_id"] = release_gate.identity(subject)
    _write_json(bundle_root / "attestation.json", bundle)
    return bundle


def test_current_software_release_status_is_truthfully_pending_and_separate():
    report = release_gate.inspect(ROOT)
    assert report["required_gate_count"] == 6
    assert report["passed_gate_count"] == 0
    assert report["software_release_ready"] is False
    assert [row["id"] for row in report["open_gates"]] == list(release_gate.GATE_IDS)
    assert report["engineering_design_complete"] is False
    assert report["attestation"] is None
    assert all(value is False for value in report["release_flags"].values())
    with pytest.raises(ValueError, match="software release remains withheld"):
        release_gate.require_ready(ROOT)


def test_external_attestation_passes_without_changing_pending_dashboard(tmp_path):
    root, source, bundle_root, bundle, fingerprint = _attestation_fixture(tmp_path)
    report = _inspect_attestation(root, bundle_root,
                                  trusted_reviewer_key_sha256=fingerprint)
    assert report["software_release_ready"] is True
    assert report["passed_gate_count"] == 6
    assert report["open_gates"] == []
    assert report["source_commit"] == source
    assert report["release_commit"] == source
    assert report["attestation"]["attestation_id"] == bundle["attestation_id"]
    assert report["release_review_accepted"] is True
    assert report["release_review_authenticated"] is True
    assert report["attestation"]["reviewer_key_sha256"] == fingerprint
    assert report["engineering_design_complete"] is False
    assert report["design_closure_audit"]["verified"] is False
    assert all(value is False for value in report["release_flags"].values())
    status = json.loads((root / release_gate.STATUS).read_bytes())
    assert status["release_commit"] is None
    assert all(row["state"] == "pending" and row["evidence"] == []
               for row in status["gates"].values())
    assert release_gate.require_ready(
        root, attestation_bundle=bundle_root,
        expected_repository=TRUSTED_REPOSITORY,
        trusted_reviewer=TRUSTED_REVIEWER,
        trusted_reviewer_key_sha256=fingerprint)["software_release_ready"]


def test_external_attestation_requires_out_of_band_reviewer_key_pin(tmp_path):
    root, _, bundle_root, _, fingerprint = _attestation_fixture(tmp_path)
    with pytest.raises(ValueError, match="trusted reviewer public-key SHA-256 fingerprint"):
        _inspect_attestation(root, bundle_root)
    with pytest.raises(ValueError, match="out-of-band trusted fingerprint"):
        _inspect_attestation(root, bundle_root,
                             trusted_reviewer_key_sha256="0" * 64)


def test_arbitrary_source_commit_cannot_override_git_head(tmp_path):
    root, _, bundle_root, _, fingerprint = _attestation_fixture(tmp_path)
    with pytest.raises(ValueError, match="does not match Git HEAD"):
        release_gate.inspect(root, source_commit="2" * 40, attestation_bundle=bundle_root,
                             trusted_reviewer_key_sha256=fingerprint)


def test_external_attestation_rejects_a_different_commit_or_tree(tmp_path):
    root, _, bundle_root, bundle, _ = _attestation_fixture(tmp_path)
    bundle["source_commit"] = "2" * 40
    _rewrite_bundle(bundle_root, bundle)
    with pytest.raises(ValueError, match="source commit differs"):
        _inspect_attestation(root, bundle_root)

    root, _, bundle_root, bundle, _ = _attestation_fixture(tmp_path / "tree")
    bundle["source_tree"] = "3" * 40
    _rewrite_bundle(bundle_root, bundle)
    with pytest.raises(ValueError, match="source tree differs"):
        _inspect_attestation(root, bundle_root)


def test_tampered_external_proof_fails_closed(tmp_path):
    root, _, bundle_root, bundle, _ = _attestation_fixture(tmp_path)
    proof = bundle_root / bundle["gates"]["SR-01"]["evidence"][0]["path"]
    proof.write_text("tampered", encoding="utf-8")
    with pytest.raises(ValueError, match="content hash mismatch"):
        _inspect_attestation(root, bundle_root)


def test_external_reviewer_signature_is_verified_against_trusted_key(tmp_path):
    root, _, bundle_root, bundle, fingerprint = _attestation_fixture(tmp_path)
    signature_path = bundle_root / bundle["release_review"]["signature"]["path"]
    signature = bytearray(signature_path.read_bytes())
    signature[0] ^= 1
    signature_path.write_bytes(signature)
    bundle["release_review"]["signature"]["sha256"] = digest(signature)
    _rewrite_bundle(bundle_root, bundle)
    with pytest.raises(ValueError, match="signature is invalid"):
        _inspect_attestation(root, bundle_root,
                             trusted_reviewer_key_sha256=fingerprint)


def test_duplicate_json_keys_are_rejected_in_attestation(tmp_path):
    root, _, bundle_root, _, _ = _attestation_fixture(tmp_path)
    (bundle_root / "attestation.json").write_text(
        '{"schema":"osr-v06-software-release-attestation/1",'
        '"schema":"osr-v06-software-release-attestation/1"}\n',
        encoding="utf-8")
    with pytest.raises(ValueError, match="duplicate JSON key"):
        _inspect_attestation(root, bundle_root,
                             trusted_reviewer_key_sha256="0" * 64)


def test_external_bundle_inside_checkout_is_rejected(tmp_path):
    root, _, _, _, _ = _attestation_fixture(tmp_path)
    inside = root / "attestation"
    inside.mkdir()
    with pytest.raises(ValueError, match="separate from the source checkout"):
        _inspect_attestation(root, inside)


def test_external_proof_paths_reject_traversal_and_symlinks(tmp_path):
    root, _, bundle_root, bundle, _ = _attestation_fixture(tmp_path)
    first = bundle["gates"]["SR-01"]["evidence"][0]
    first["path"] = "../outside.json"
    _rewrite_bundle(bundle_root, bundle)
    with pytest.raises(ValueError, match="unsafe SR-01 evidence path"):
        _inspect_attestation(root, bundle_root)

    root, _, bundle_root, bundle, _ = _attestation_fixture(tmp_path / "symlink")
    first = bundle["gates"]["SR-01"]["evidence"][0]
    link = bundle_root / "proofs" / "linked-proof.json"
    link.symlink_to(Path(first["path"]).name)
    first["path"] = "proofs/linked-proof.json"
    _rewrite_bundle(bundle_root, bundle)
    with pytest.raises(ValueError, match="ordinary in-tree SR-01 evidence file required"):
        _inspect_attestation(root, bundle_root)


def test_dirty_checkout_cannot_be_attested(tmp_path):
    root, _, bundle_root, _, _ = _attestation_fixture(tmp_path)
    (root / "untracked.txt").write_text("working tree changed", encoding="utf-8")
    with pytest.raises(ValueError, match="clean Git checkout"):
        _inspect_attestation(root, bundle_root)


def test_external_bundle_must_match_contract_and_required_proof_kinds(tmp_path):
    root, _, bundle_root, bundle, _ = _attestation_fixture(tmp_path)
    bundle["contract_sha256"] = "0" * 64
    _rewrite_bundle(bundle_root, bundle)
    with pytest.raises(ValueError, match="contract hash differs"):
        _inspect_attestation(root, bundle_root)

    root, _, bundle_root, bundle, _ = _attestation_fixture(tmp_path / "missing-kind")
    bundle["gates"]["SR-03"]["evidence"].pop()
    _rewrite_bundle(bundle_root, bundle)
    with pytest.raises(ValueError, match="lacks required external proof kinds"):
        _inspect_attestation(root, bundle_root)


def test_required_ci_evidence_binds_both_workflows_to_the_release_commit(tmp_path):
    root, _, bundle_root, bundle, _ = _attestation_fixture(tmp_path)
    row = bundle["gates"]["SR-02"]["evidence"][0]
    proof_path = bundle_root / row["path"]
    proof = json.loads(proof_path.read_bytes())
    proof["workflow_runs"][0]["head_sha"] = "2" * 40
    raw = _write_json(proof_path, proof)
    row["sha256"] = digest(raw)
    _rewrite_bundle(bundle_root, bundle)
    with pytest.raises(ValueError, match="exact release commit"):
        _inspect_attestation(root, bundle_root)

    root, _, bundle_root, bundle, _ = _attestation_fixture(tmp_path / "missing-run")
    row = bundle["gates"]["SR-02"]["evidence"][0]
    proof_path = bundle_root / row["path"]
    proof = json.loads(proof_path.read_bytes())
    proof["workflow_runs"].pop()
    raw = _write_json(proof_path, proof)
    row["sha256"] = digest(raw)
    _rewrite_bundle(bundle_root, bundle)
    with pytest.raises(ValueError, match="each required v0.6 workflow run"):
        _inspect_attestation(root, bundle_root)


def test_external_attestation_repository_and_reviewer_match_trusted_inputs(tmp_path):
    root, _, bundle_root, _, fingerprint = _attestation_fixture(tmp_path)
    with pytest.raises(ValueError, match="out-of-band expected repository"):
        _inspect_attestation(root, bundle_root,
                             expected_repository="example/fork",
                             trusted_reviewer_key_sha256=fingerprint)
    with pytest.raises(ValueError, match="out-of-band trusted reviewer"):
        _inspect_attestation(root, bundle_root,
                             trusted_reviewer="Untrusted Alias",
                             trusted_reviewer_key_sha256=fingerprint)


def test_external_attestation_rejects_hidden_index_changes(tmp_path):
    root, _, _, _, _ = _attestation_fixture(tmp_path)
    relative = "campaigns/v06-software-release.toml"
    _git(root, "update-index", "--assume-unchanged", relative)
    with pytest.raises(ValueError, match="full checkout without assume-unchanged"):
        release_gate._require_clean_checkout(root)

    root, _, _, _, _ = _attestation_fixture(tmp_path / "sparse")
    _git(root, "update-index", "--skip-worktree", relative)
    with pytest.raises(ValueError, match="full checkout without assume-unchanged"):
        release_gate._require_clean_checkout(root)


def test_external_bundle_cannot_assert_physical_or_design_acceptance(tmp_path):
    root, _, bundle_root, bundle, _ = _attestation_fixture(tmp_path)
    bundle["release_flags"]["physical_accepted"] = True
    _rewrite_bundle(bundle_root, bundle)
    with pytest.raises(ValueError, match="cannot assert engineering or physical"):
        _inspect_attestation(root, bundle_root)


def test_in_tree_passing_dashboard_is_rejected(tmp_path):
    root, _ = _clean_checkout(tmp_path)
    status_path = root / release_gate.STATUS
    status = json.loads(status_path.read_bytes())
    status["gates"]["SR-01"].update(state="passed", evidence=[{"kind": "tamper-rejection"}])
    status_path.write_text(json.dumps(status), encoding="utf-8")
    with pytest.raises(ValueError, match="external release attestation bundle"):
        release_gate.inspect(root)
