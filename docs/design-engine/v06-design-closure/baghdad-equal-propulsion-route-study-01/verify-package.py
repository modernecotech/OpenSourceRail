#!/usr/bin/env python3
"""Verify Baghdad route-study archive lineage, current attempt, and sidecars."""

from __future__ import annotations

import hashlib
import json
import math
import tarfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent
RESULTS = ROOT / "results"
PREFIX = ""


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def canonical_id(value: dict, field: str) -> str:
    unsigned = {key: item for key, item in value.items() if key != field}
    raw = (json.dumps(unsigned, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n").encode()
    return sha(raw)


def read_member(tf: tarfile.TarFile, name: str) -> bytes:
    stream = tf.extractfile(name)
    if stream is None:
        raise ValueError(f"missing archive member: {name}")
    return stream.read()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


def check_archive_digest(path: Path, expected_sha: str, expected_size: int | None = None) -> bytes:
    raw = path.read_bytes()
    require(sha(raw) == expected_sha, f"archive digest mismatch: {path.name}")
    if expected_size is not None:
        require(len(raw) == expected_size, f"archive size mismatch: {path.name}")
    return raw


def verify_success(receipt: dict) -> tuple[int, dict]:
    archive_record = receipt["archive"]
    success_path = RESULTS / archive_record["path"]
    success_raw = check_archive_digest(success_path, archive_record["sha256"], archive_record["size_bytes"])
    with tarfile.open(success_path, "r:gz") as tf:
        members = {member.name: member for member in tf.getmembers() if member.isfile()}
        root_manifest = json.loads(read_member(tf, PREFIX + "manifest.json"))
        require(root_manifest["manifest_id"] == receipt["attempt_manifest_id"], "successful attempt manifest identity mismatch")
        require(root_manifest["manifest_id"] == canonical_id(root_manifest, "manifest_id"), "successful attempt manifest hash mismatch")
        require(root_manifest["comparison_id"] == receipt["comparison_id"], "successful comparison identity mismatch")
        require(root_manifest["source_commit"] == receipt["source_commit"], "successful source commit mismatch")
        expected = {PREFIX + name: digest for name, digest in root_manifest["files_sha256"].items()}
        expected[PREFIX + "manifest.json"] = None
        require(root_manifest["file_count"] == len(root_manifest["files_sha256"]), "root manifest file count mismatch")
        supplemental = receipt["supplemental_manifest_hashes"]
        expected.update(supplemental)
        require(set(members) == set(expected), "successful archive members differ from root manifest")
        for name, digest in expected.items():
            if digest is not None:
                require(sha(read_member(tf, name)) == digest, f"successful payload hash mismatch: {name}")

        expected_nested_paths = {
            name.removeprefix(PREFIX) for name in members
            if name.endswith("/manifest.json") and name != PREFIX + "manifest.json"
        }
        actual_nested_paths = {path.removeprefix(PREFIX) for path in supplemental}
        require(actual_nested_paths == expected_nested_paths, "supplemental nested-manifest inventory mismatch")

        summary = json.loads(read_member(tf, PREFIX + "summary.json"))
        execution = json.loads(read_member(tf, PREFIX + "execution.json"))
        route_generation = json.loads(read_member(tf, PREFIX + "route-generation.json"))
        require(summary["comparison_id"] == receipt["comparison_id"], "summary comparison mismatch")
        require(summary["all_studies_replayed"] is True, "one or more study replays are incomplete")
        require(summary["force_map_available"] is False, "attempt incorrectly claims an available force map")
        require(summary["selected"] is False, "research sensitivity was silently selected")
        require(summary["outline_publication_manifest_id"] == receipt["outline_publication_manifest_id"], "published outline identity mismatch")
        require(route_generation["generation_id"] == receipt["route_generation_id"], "route-generation identity mismatch")
        require(route_generation["distance_kernel_check"]["engine"] == f"Shapely {receipt['execution_limits']['geometry_runtime_shapely']} / GEOS point-to-LineString", "route-geometry runtime mismatch")
        require(receipt["execution_limits"]["geometry_runtime_shapely"] == receipt["execution_limits"]["project_pinned_shapely"], "current route run is not on the pinned geometry version")
        require(receipt["outline_publication_manifest_id"] != receipt["outline_replay_run_manifest_id"], "publication manifest and replay-run identity were conflated")
        require(len(members) == receipt["attempt_total_files_including_all_manifests"], "total archived file count differs")
        require(root_manifest["file_count"] == receipt["attempt_root_payload_files"], "root payload count differs")

        for label, row in receipt["successful_attempt_studies"].items():
            study = summary["studies"].get(label)
            require(study is not None, f"receipt study missing from summary: {label}")
            require(study["study_id"] == row["study_id"], f"study ID mismatch: {label}")
            require(study["manifest_id"] == row["manifest_id"], f"study manifest mismatch: {label}")
            require(study["exact_cached_study_reused"] is row["exact_cached_study_reused"], f"cache disposition mismatch: {label}")
            require(study["replay_verified"] is True, f"study is not replay verified: {label}")
            execution_study = execution["studies"].get(label)
            require(execution_study is not None and execution_study["replay_verified"] is True, f"execution replay record missing: {label}")
            require(execution_study["study_id"] == row["study_id"], f"execution study ID mismatch: {label}")

        for full_path, digest in supplemental.items():
            require(full_path in members, f"nested manifest missing: {full_path}")
            raw = read_member(tf, full_path)
            require(sha(raw) == digest, f"nested manifest hash mismatch: {full_path}")
            manifest = json.loads(raw)
            require(manifest["manifest_id"] == canonical_id(manifest, "manifest_id"), f"nested identity mismatch: {full_path}")
            suffix = full_path.removeprefix(PREFIX)
            if "/business/" in suffix:
                require(not any(manifest.get(flag, False) for flag in (
                    "business_records_submitted", "external_transactions_performed",
                    "active_orders_mutated", "procurement_approved",
                )), f"unexpected business side effect flag: {full_path}")
                study_prefix = suffix.split("/business/", 1)[0]
                parent_study = json.loads(read_member(tf, PREFIX + study_prefix + "/manifest.json"))
                require(parent_study["files_sha256"].get("business/manifest.json") == digest, f"study manifest does not bind business manifest: {full_path}")
                for relative, file_digest in manifest["files_sha256"].items():
                    archive_name = PREFIX + study_prefix + "/business/" + relative
                    require(archive_name in expected and expected[archive_name] == file_digest, f"business payload not bound by root manifest: {archive_name}")
                continue
            study_prefix = suffix.removesuffix("/manifest.json")
            study_key = study_prefix.removeprefix("studies/")
            study = manifest
            require(study_key in summary["studies"], f"study manifest belongs to unknown study: {full_path}")
            require(summary["studies"][study_key]["manifest_id"] == study["manifest_id"], f"study manifest identity differs from summary: {study_key}")
            for relative, file_digest in study["files_sha256"].items():
                archive_name = PREFIX + study_prefix + "/" + relative
                require(archive_name in expected and expected[archive_name] == file_digest, f"business payload not bound by root manifest: {archive_name}")

        return len(members), summary


def verify_failure_archive(record: dict) -> None:
    archive_path = RESULTS / record["archive"]
    check_archive_digest(archive_path, record["archive_sha256"], record["size_bytes"])
    with tarfile.open(archive_path, "r:gz") as tf:
        failure = json.loads(read_member(tf, record["member"]))
    require(failure.get("failure_record_id") == record["failure_record_id"], f"failure record identity mismatch: {record['archive']}")
    require(failure.get("source_commit") == record["source_commit"], f"failure source mismatch: {record['archive']}")
    require(failure.get("physical_accepted") is False and failure.get("engineering_accepted") is False, f"failure acceptance flags mismatch: {record['archive']}")


def main() -> int:
    global PREFIX
    receipt_path = RESULTS / "package-receipt.json"
    receipt = json.loads(receipt_path.read_text())
    package_id = receipt.get("package_id")
    package_unsigned = {key: value for key, value in receipt.items() if key != "package_id"}
    package_bytes = json.dumps(package_unsigned, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
    require(package_id == sha(package_bytes), "package receipt identity mismatch")
    require(receipt["current_attempt"] == 5, "package does not identify attempt 05 as current")
    PREFIX = f"attempt-{receipt['current_attempt']:02}/"

    review = receipt["independent_review"]
    review_path = ROOT / review["artifact"]
    require(review["state"] == "completed", "independent review is not complete")
    require(review["os_sandbox_enforced"] is False, "review isolation status must report the actual unsandboxed environment")
    require(review_path.is_file() and sha(review_path.read_bytes()) == review["sha256"], "independent review artifact hash mismatch")

    sensitivity_record = receipt["row_bridge_risk_sensitivity"]
    sensitivity_path = ROOT / sensitivity_record["path"]
    sensitivity_raw = sensitivity_path.read_bytes()
    require(sha(sensitivity_raw) == sensitivity_record["sha256"], "ROW/bridge sensitivity artifact hash mismatch")
    sensitivity = json.loads(sensitivity_raw)
    require(sensitivity["sensitivity_id"] == canonical_id(sensitivity, "sensitivity_id"), "ROW/bridge sensitivity identity mismatch")
    require(sensitivity["sensitivity_id"] == sensitivity_record["sensitivity_id"], "ROW/bridge sensitivity receipt identity mismatch")
    require(sensitivity["source_archive_sha256"] == receipt["archive"]["sha256"], "risk sensitivity is bound to a different archive")
    require(sensitivity["attempt_manifest_id"] == receipt["attempt_manifest_id"], "risk sensitivity is bound to a different attempt manifest")
    require(sensitivity["comparison_id"] == receipt["comparison_id"], "risk sensitivity is bound to a different comparison")
    require(sensitivity["revised_study_id"] == receipt["successful_attempt_studies"]["simplified-radials-from-published-baseline"]["study_id"], "risk sensitivity is bound to a different revised study")
    require(sensitivity["baseline_study_id"] == receipt["successful_attempt_studies"]["baseline-published-anchor-preserving-chord-research-powered-axle"]["study_id"], "risk sensitivity is bound to a different baseline study")
    require(sensitivity["geometry_runtime_shapely"] == receipt["execution_limits"]["geometry_runtime_shapely"], "risk sensitivity geometry runtime mismatch")
    require(sensitivity["assumptions_are_site_evidence"] is False and sensitivity["not_city_recalculation"] is True, "risk sensitivity maturity flags mismatch")
    route_m = sensitivity["new_geometry_changed_route_m"]
    p = sensitivity["base_parameters"]
    require(sensitivity["formula"] == "(additional_row_area_m2 * land_iqd_per_m2 / exchange_iqd_per_usd + changed_route_m * site_risk_usd_per_changed_route_m + additional_access_walkway_m * station_repair_walkway_usd_per_m + unverified_bridge_route_m * bridge_risk_usd_per_bridge_route_m) * foreign_local_rate_transfer", "risk sensitivity formula does not match source terms")
    for row in sensitivity["sensitivity"]:
        for case in row["bridge_cases"]:
            added_row_area = route_m * row["row_width_m"]
            added_bridge_route = route_m * case["bridge_fraction"]
            expected_increment = (
                added_row_area * p["land_iqd_per_m2"] / p["exchange_iqd_per_usd"]
                + route_m * p["site_risk_usd_per_changed_route_m"]
                + p["additional_access_walkway_m"] * p["station_repair_walkway_usd_per_m"]
                + added_bridge_route * p["bridge_risk_usd_per_bridge_route_m"]
            ) * p["foreign_local_transfer_multiplier"]
            require(math.isclose(case["incremental_reserve_usd"], expected_increment, rel_tol=1e-12), "risk sensitivity arithmetic mismatch")

    count, summary = verify_success(receipt)
    for key in ("attempt-01", "attempt-03"):
        verify_failure_archive(receipt["failed_attempts"][key])

    prior = receipt["prior_successful_attempts"]["attempt-04"]
    prior_path = RESULTS / prior["archive"]
    check_archive_digest(prior_path, prior["archive_sha256"], prior["size_bytes"])
    with tarfile.open(prior_path, "r:gz") as tf:
        prior_manifest = json.loads(read_member(tf, "attempt-04/manifest.json"))
        require(prior_manifest["manifest_id"] == prior["manifest_id"], "prior successful attempt manifest mismatch")
        require(prior_manifest["comparison_id"] == prior["comparison_id"], "prior successful attempt comparison mismatch")
        require(prior_manifest["source_commit"] == receipt["source_commit"], "prior successful attempt source mismatch")
        prior_route = json.loads(read_member(tf, "attempt-04/route-generation.json"))
        require(prior_route["distance_kernel_check"]["engine"].startswith("Shapely 2.1.2 "), "prior attempt runtime is not the recorded pre-pin version")
        with tarfile.open(RESULTS / receipt["archive"]["path"], "r:gz") as current_tf:
            current_route = json.loads(read_member(current_tf, PREFIX + "route-generation.json"))
            require(current_route["distance_kernel_check"]["engine"].startswith("Shapely 2.2.0 "), "current attempt does not use the project-pinned Shapely version")
            for study_dir in (
                "baseline-published-anchor-preserving-chord-research-powered-axle",
                "simplified-radials-from-published-baseline",
            ):
                member = f"studies/{study_dir}/alignments.geojson"
                require(read_member(tf, "attempt-04/" + member) == read_member(current_tf, PREFIX + member), f"pinned-version rerun changed route coordinates: {study_dir}")

    superseded = receipt["superseded_attempts"]["attempt-02"]
    superseded_path = RESULTS / superseded["archive"]
    check_archive_digest(superseded_path, superseded["archive_sha256"], superseded["size_bytes"])
    with tarfile.open(superseded_path, "r:gz") as tf:
        old_manifest = json.loads(read_member(tf, "attempt-02/manifest.json"))
        require(old_manifest["comparison_id"] == superseded["comparison_id"], "superseded attempt comparison identity mismatch")
        require(old_manifest["source_commit"] == receipt["source_commit"], "superseded attempt source mismatch")
        require(superseded["is_current_comparison"] is False, "superseded attempt marked current")

    staging = json.loads((RESULTS / "source-staging-receipt.json").read_text())
    require(staging["receipt_id"] == receipt["source_staging_receipt_id"], "source staging receipt mismatch")
    require(staging["source_commit"] == receipt["source_commit"], "staging source commit mismatch")
    replay = json.loads((RESULTS / "outline-publication-replay-receipt.json").read_text())
    require(replay["result"]["manifest_id"] == receipt["outline_replay_run_manifest_id"], "outline replay-run manifest mismatch")
    require(replay["result"]["verified"] is True and replay["result"]["completed_cities"] == receipt["outline_publication_cities"], "outline publication replay is incomplete")
    require(summary["outline_publication_manifest_id"] == receipt["outline_publication_manifest_id"], "attempt and receipt publication manifest mismatch")
    companion = receipt["companion_artifacts"]
    companion_payloads: dict[str, bytes] = {}
    for relative, expected_hash in companion.items():
        companion_path = ROOT.parents[3] / relative
        require(companion_path.is_file(), f"companion publication artifact missing: {relative}")
        raw = companion_path.read_bytes()
        require(sha(raw) == expected_hash, f"companion publication artifact hash mismatch: {relative}")
        companion_payloads[relative] = raw
    publication = json.loads(companion_payloads["docs/design-engine/outline-completion/manifest.json"])
    city = json.loads(__import__("gzip").decompress(companion_payloads["docs/design-engine/outline-completion/cities/baghdad.json.gz"]))
    require(publication["manifest_id"] == receipt["outline_publication_manifest_id"], "companion outline manifest identity mismatch")
    require(publication["canonical_run_manifest_id"] == receipt["outline_replay_run_manifest_id"], "companion outline run manifest mismatch")
    require(publication["files_sha256"]["cities/baghdad.json.gz"] == sha(companion_payloads["docs/design-engine/outline-completion/cities/baghdad.json.gz"]), "outline manifest does not bind its Baghdad record")
    require(city["evaluation_id"] == receipt["published_baghdad_outline_evaluation_id"], "published Baghdad evaluation identity mismatch")
    require(city["selected_alignment_id"] == receipt["published_baghdad_selected_alignment_id"], "published Baghdad alignment identity mismatch")
    require(city["selected_alignment_kind"] == "anchor-preserving-chord-research", "published Baghdad geometry selection mismatch")
    require(not any(receipt[name] for name in ("physical_accepted", "engineering_accepted", "manufacturing_release", "operating_release", "movement_authority")), "unexpected physical acceptance or release flag")
    print(f"verified {package_id}; attempt 05 has {count} sealed members and both studies replay-verified; attempts 01/03 failed, attempt 04 is retained prior evidence, and attempt 02 is preserved as superseded")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
