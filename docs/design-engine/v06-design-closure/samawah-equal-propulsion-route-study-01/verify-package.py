#!/usr/bin/env python3
"""Verify the immutable Samawah route-study evidence package."""

from __future__ import annotations

import hashlib
import json
import tarfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent
RESULTS = ROOT / "results"


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def identity(value: dict) -> str:
    unsigned = {key: item for key, item in value.items() if key != "manifest_id"}
    canonical = json.dumps(unsigned, sort_keys=True, separators=(",", ":"), allow_nan=False).encode() + b"\n"
    return sha256(canonical)


def read_member(tf: tarfile.TarFile, name: str) -> bytes:
    stream = tf.extractfile(name)
    if stream is None:
        raise ValueError(f"missing archive member: {name}")
    return stream.read()


def main() -> int:
    receipt = json.loads((RESULTS / "package-receipt.json").read_text())
    package_id = receipt.pop("package_id")
    canonical = json.dumps(receipt, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
    if sha256(canonical) != package_id:
        raise SystemExit("package receipt identity mismatch")

    review = receipt.get("independent_review", {})
    review_path = ROOT / review.get("artifact", "")
    if (review.get("state") != "completed" or review.get("os_sandbox_enforced") is not False
            or not review_path.is_file() or sha256(review_path.read_bytes()) != review.get("sha256")):
        raise SystemExit("independent review receipt or artifact hash mismatch")

    archive = RESULTS / receipt["archive"]["path"]
    archive_bytes = archive.read_bytes()
    if len(archive_bytes) != receipt["archive"]["size_bytes"] or sha256(archive_bytes) != receipt["archive"]["sha256"]:
        raise SystemExit("archive size or SHA-256 mismatch")

    with tarfile.open(archive, "r:gz") as tf:
        members = {m.name: m for m in tf.getmembers() if m.isfile()}
        manifest_member = members.get("attempt-02/manifest.json")
        if manifest_member is None:
            raise SystemExit("attempt manifest missing")
        manifest = json.load(tf.extractfile(manifest_member))
        if manifest["manifest_id"] != receipt["attempt_manifest_id"] or manifest["comparison_id"] != receipt["comparison_id"]:
            raise SystemExit("attempt manifest identity mismatch")
        expected = {f"attempt-02/{name}": digest for name, digest in manifest["files_sha256"].items()}
        expected.update(receipt["supplemental_manifest_hashes"])
        expected["attempt-02/manifest.json"] = None
        if set(members) != set(expected):
            raise SystemExit("archive member list differs from sealed manifest")
        for name, digest in expected.items():
            if digest is None:
                continue
            with tf.extractfile(members[name]) as stream:
                if sha256(stream.read()) != digest:
                    raise SystemExit(f"artifact hash mismatch: {name}")
        summary_member = members.get("attempt-02/summary.json")
        if summary_member is None:
            raise SystemExit("summary missing")
        summary = json.load(tf.extractfile(summary_member))
        for manifest_path, manifest_digest in receipt["supplemental_manifest_hashes"].items():
            if "/business/" in manifest_path:
                continue
            study_prefix = manifest_path.removeprefix("attempt-02/").removesuffix("/manifest.json")
            study_key = study_prefix.removeprefix("studies/")
            study = json.loads(read_member(tf, manifest_path))
            row = summary["studies"].get(study_key)
            if (sha256(read_member(tf, manifest_path)) != manifest_digest or row is None
                    or study["manifest_id"] != row["manifest_id"] or identity(study) != study["manifest_id"]):
                raise SystemExit(f"study manifest identity mismatch: {study_key}")
            for relative, digest in study["files_sha256"].items():
                archive_name = f"attempt-02/{study_prefix}/{relative}"
                if archive_name not in expected or expected[archive_name] != digest:
                    raise SystemExit(f"study manifest does not bind its payload: {archive_name}")
            business_path = f"attempt-02/{study_prefix}/business/manifest.json"
            business = json.loads(read_member(tf, business_path))
            if (business_path not in receipt["supplemental_manifest_hashes"]
                    or sha256(read_member(tf, business_path)) != receipt["supplemental_manifest_hashes"][business_path]
                    or identity(business) != business["manifest_id"]
                    or study["files_sha256"].get("business/manifest.json") != expected[business_path]):
                raise SystemExit(f"business manifest identity or parent binding mismatch: {study_key}")
            for relative, digest in business["files_sha256"].items():
                archive_name = f"attempt-02/{study_prefix}/business/{relative}"
                if archive_name not in expected or expected[archive_name] != digest:
                    raise SystemExit(f"business manifest does not bind its payload: {archive_name}")
            if any(business[key] for key in ("business_records_submitted", "external_transactions_performed",
                                               "active_orders_mutated", "procurement_approved")):
                raise SystemExit(f"business draft contains an unexpected external-action flag: {study_key}")
        if receipt["attempt_total_files_including_all_manifests"] != len(members):
            raise SystemExit("total archive file count including nested manifests differs")

    staging = json.loads((RESULTS / "source-staging-receipt.json").read_text())
    if staging["receipt_id"] != receipt["source_staging_receipt_id"]:
        raise SystemExit("sparse source-staging receipt identity mismatch")
    replay = json.loads((RESULTS / "outline-publication-replay-receipt.json").read_text())
    if replay["result"]["manifest_id"] != receipt["outline_publication_manifest_id"] or not replay["result"]["verified"]:
        raise SystemExit("outline publication replay receipt mismatch")
    if any(receipt[key] for key in ("physical_accepted", "engineering_accepted", "manufacturing_release", "operating_release", "movement_authority")):
        raise SystemExit("package contains an unexpected acceptance/release flag")

    print(f"verified package {package_id}; {len(expected) - 1} sealed artifacts; archive SHA-256 {receipt['archive']['sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
