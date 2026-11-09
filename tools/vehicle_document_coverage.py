#!/usr/bin/env python3
"""Build a source-pinned, deliberately incomplete vehicle document inventory."""

from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import json
import struct
from pathlib import Path
from typing import Any


PACKET = Path("docs/design-engine/reconciled-pilot-bogie-detail")
EXPECTED_SCHEMA = "osr-vehicle-document-coverage/1"
CONTROLLED_PART_DOCUMENTS = (
    "controlled_drawing",
    "controlled_production_bom",
    "manufacturing_conversion_rule",
    "material_specification_and_traceability",
    "interface_and_tolerance_definition",
    "inspection_and_acceptance_record",
    "fabrication_routing_and_tooling_instruction",
)
CONTROLLED_ASSEMBLY_DOCUMENTS = (
    "assembly_instruction",
    "interface_and_tolerance_definition",
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _read_gzip_json(path: Path) -> dict[str, Any]:
    with gzip.open(path, "rt", encoding="utf-8") as stream:
        return json.load(stream)


def _check_identity(actual: dict[str, Any], expected: dict[str, str], label: str) -> None:
    for key, value in expected.items():
        if actual.get(key) != value:
            raise ValueError(f"{label} identity {key} does not match the frozen pilot identity")


def _check_pin(path: Path, digest: str, pins: list[tuple[str, str | None]]) -> list[str]:
    if not pins or any(value is None for _, value in pins):
        missing = [name for name, value in pins if value is None] or ["manifest pin"]
        raise ValueError(f"{path.name} is missing required manifest pin(s): {', '.join(missing)}")
    for name, value in pins:
        if value != digest:
            raise ValueError(f"{path.name} SHA-256 does not match {name} pin")
    return [name for name, _ in pins]


def _glb_inventory(path: Path) -> dict[str, Any]:
    data = path.read_bytes()
    if len(data) < 20:
        raise ValueError("GLB is shorter than its header and JSON chunk")
    magic, version, declared_length = struct.unpack_from("<4sII", data)
    if magic != b"glTF" or version != 2 or declared_length != len(data):
        raise ValueError("assembly GLB header is invalid or length does not match")
    json_length, chunk_type = struct.unpack_from("<II", data, 12)
    if chunk_type != 0x4E4F534A or 20 + json_length > len(data):
        raise ValueError("assembly GLB does not start with a valid JSON chunk")
    gltf = json.loads(data[20 : 20 + json_length].decode("utf-8").rstrip(" \t\r\n\0"))
    return {
        "glb_version": version,
        "mesh_definition_count": len(gltf.get("meshes", [])),
        "node_count": len(gltf.get("nodes", [])),
    }


def build_report(repo_root: Path) -> dict[str, Any]:
    folder = repo_root / PACKET
    manifest_path = folder / "vehicle/manifest.json"
    manifest = _read_json(manifest_path)
    pilot_manifest = _read_json(folder / "manifest.json")
    bundle = _read_json(folder / "bundle.json")

    candidate_id = "9f6d223074b3438a546d5b3d71cd9b970807387ef0542023bed79bef46dbdeba"
    evaluation_id = "dfb48ca3fac6ee9b702ae13b2e5e4e0c112d734263750deefb25ad5718fdb272"
    if manifest.get("candidate_id") != candidate_id or manifest.get("evaluation_id") != evaluation_id:
        raise ValueError("vehicle manifest identity does not match the frozen pilot candidate/evaluation")
    if manifest.get("engineering_accepted") is not False or manifest.get("manufacturing_release") is not False:
        raise ValueError("vehicle manifest has unexpected acceptance or release state")
    if pilot_manifest.get("schema") != "osr-railway-closure-publication/1":
        raise ValueError("unexpected top-level pilot publication schema")
    delivery_manifest = _read_json(folder / "delivery/manifest.json")
    delivery = _read_json(folder / "delivery/execution-mapping-draft.json")
    proposal = _read_gzip_json(folder / "delivery/proposal.json.gz")
    delivery_body = _read_gzip_json(folder / "delivery/inputs/body.json.gz")
    delivery_study = _read_gzip_json(folder / "delivery/inputs/study.json.gz")

    frozen_bundle_candidate = "cde8e4595d365b31d169cf452d1efc1b9f0c96225ca3bbccf8bf51b5a2480c7f"
    frozen_bundle_evaluation = "b0d332a0fe3883e5a0783057bf0bc93f99f5235fc9b9af3e83a5cb7cc7909c78"
    frozen_study_id = "abc42ebe77496d5c16fe30622ade179b02141bde5feacadd7497abe0b83cc710"
    frozen_service_evaluation = "830ee18500b3c4c192f74fb61a9f8079adc1ef7eb3e3f3a9db96cdee8bf4a4c2"
    if pilot_manifest.get("study_id") != frozen_study_id:
        raise ValueError("top-level pilot study identity does not match the frozen study")
    _check_identity(
        bundle,
        {"candidate_id": frozen_bundle_candidate, "evaluation_id": frozen_bundle_evaluation, "body_evaluation_id": evaluation_id},
        "bundle",
    )
    _check_identity(
        bundle.get("physical_definition", {}),
        {"body_candidate_id": candidate_id},
        "bundle physical definition",
    )
    expected_delivery_ids = {
        "body_candidate_id": candidate_id,
        "bundle_evaluation_id": frozen_bundle_evaluation,
        "candidate_id": frozen_bundle_candidate,
        "engineering_revision": evaluation_id,
        "service_evaluation_id": frozen_service_evaluation,
        "study_id": frozen_study_id,
    }
    _check_identity(delivery.get("identities", {}), expected_delivery_ids, "delivery mapping")
    _check_identity(delivery_manifest.get("identities", {}), expected_delivery_ids, "delivery manifest")
    _check_identity(proposal.get("identities", {}), expected_delivery_ids, "delivery proposal")
    if delivery_manifest.get("identities") != delivery.get("identities") or proposal.get("identities") != delivery.get("identities"):
        raise ValueError("delivery manifest, proposal and execution mapping carry different identity sets")
    if delivery_body.get("candidate_id") != candidate_id or delivery_body.get("evaluation_id") != evaluation_id:
        raise ValueError("delivery body input candidate/evaluation does not match the frozen vehicle identity")
    if delivery_study.get("study_id") != frozen_study_id:
        raise ValueError("delivery study input does not match the frozen pilot study identity")
    delivery_inputs = {item.get("path"): item.get("content_identity") for item in delivery_manifest.get("inputs", [])}
    if delivery_inputs.get("inputs/body.json.gz") != evaluation_id:
        raise ValueError("delivery manifest body input identity does not match the frozen vehicle evaluation")
    if delivery_inputs.get("inputs/study.json.gz") != frozen_study_id:
        raise ValueError("delivery manifest study input identity does not match the frozen pilot study")
    if delivery_manifest.get("proposal_id") != proposal.get("proposal_id"):
        raise ValueError("delivery manifest proposal identity does not match its proposal payload")

    source_manifest_specs = [
        ("pilot_publication_manifest", "manifest.json", None),
        ("vehicle_manifest", "vehicle/manifest.json", "vehicle/manifest.json"),
        ("delivery_manifest", "delivery/manifest.json", "delivery/manifest.json"),
    ]
    source_manifests: dict[str, dict[str, str]] = {}
    for key, relpath, top_pin_key in source_manifest_specs:
        path = folder / relpath
        digest = sha256(path)
        pins = [] if top_pin_key is None else [("top publication manifest", pilot_manifest.get("files_sha256", {}).get(top_pin_key))]
        pin_sources = _check_pin(path, digest, pins) if pins else []
        source_manifests[key] = {
            "path": str(PACKET / relpath),
            "sha256": digest,
            "pin_sources": pin_sources,
            "pin_state": "root anchor; no self-pin expected" if key == "pilot_publication_manifest" else "pinned",
        }

    payload_specs = [
        ("vehicle_bom", "vehicle/bom.csv", [("top publication manifest", "vehicle/bom.csv", pilot_manifest.get("files_sha256", {}).get("vehicle/bom.csv")), ("vehicle manifest", "bom.csv", manifest.get("files_sha256", {}).get("bom.csv"))]),
        ("vehicle_installation", "vehicle/installation.json.gz", [("top publication manifest", "vehicle/installation.json.gz", pilot_manifest.get("files_sha256", {}).get("vehicle/installation.json.gz")), ("vehicle manifest", "installation.json.gz", manifest.get("files_sha256", {}).get("installation.json.gz")), ("delivery manifest", "inputs/body.json.gz", delivery_manifest.get("files_sha256", {}).get("inputs/body.json.gz"))]),
        ("vehicle_assembly_glb", "vehicle/assembly.glb", [("top publication manifest", "vehicle/assembly.glb", pilot_manifest.get("files_sha256", {}).get("vehicle/assembly.glb")), ("vehicle manifest", "assembly.glb", manifest.get("files_sha256", {}).get("assembly.glb"))]),
        ("delivery_mapping", "delivery/execution-mapping-draft.json", [("top publication manifest", "delivery/execution-mapping-draft.json", pilot_manifest.get("files_sha256", {}).get("delivery/execution-mapping-draft.json")), ("delivery manifest", "execution-mapping-draft.json", delivery_manifest.get("files_sha256", {}).get("execution-mapping-draft.json"))]),
        ("delivery_proposal", "delivery/proposal.json.gz", [("top publication manifest", "delivery/proposal.json.gz", pilot_manifest.get("files_sha256", {}).get("delivery/proposal.json.gz")), ("delivery manifest", "proposal.json.gz", delivery_manifest.get("files_sha256", {}).get("proposal.json.gz"))]),
        ("delivery_body_input", "delivery/inputs/body.json.gz", [("top publication manifest", "delivery/inputs/body.json.gz", pilot_manifest.get("files_sha256", {}).get("delivery/inputs/body.json.gz")), ("delivery manifest", "inputs/body.json.gz", delivery_manifest.get("files_sha256", {}).get("inputs/body.json.gz"))]),
        ("delivery_study_input", "delivery/inputs/study.json.gz", [("top publication manifest", "delivery/inputs/study.json.gz", pilot_manifest.get("files_sha256", {}).get("delivery/inputs/study.json.gz")), ("delivery manifest", "inputs/study.json.gz", delivery_manifest.get("files_sha256", {}).get("inputs/study.json.gz"))]),
        ("pilot_bundle", "bundle.json", [("top publication manifest", "bundle.json", pilot_manifest.get("files_sha256", {}).get("bundle.json"))]),
    ]
    payloads: dict[str, dict[str, Any]] = {}
    for key, relpath, pin_specs in payload_specs:
        path = folder / relpath
        digest = sha256(path)
        pin_sources = _check_pin(path, digest, [(f"{label} ({pin_path})", pin_value) for label, pin_path, pin_value in pin_specs])
        payloads[key] = {"path": str(PACKET / relpath), "sha256": digest, "pin_sources": pin_sources}

    with (folder / "vehicle/bom.csv").open(newline="", encoding="utf-8") as stream:
        bom_rows = list(csv.DictReader(stream))
    installation = _read_gzip_json(folder / "vehicle/installation.json.gz")
    if installation.get("candidate_id") != candidate_id or installation.get("evaluation_id") != evaluation_id:
        raise ValueError("installation payload identity does not match the frozen vehicle packet")

    installation_parts = {part["id"]: part for part in installation.get("parts", [])}
    delivery_items = {item["source_part_id"]: item for item in delivery.get("items", [])}
    part_ids = [row["part_id"] for row in bom_rows]
    if len(part_ids) != len(set(part_ids)) or set(part_ids) != set(installation_parts) or set(part_ids) != set(delivery_items):
        raise ValueError("BOM, installation and delivery mapping do not contain the same unique part IDs")
    if delivery.get("status") != "held" or delivery.get("automatic_order_release") is not False:
        raise ValueError("delivery mapping is not in the expected held/no-release state")

    null_counts = {
        field: sum(item.get(field) is None for item in delivery["items"])
        for field in ("drawing_reference", "inspection_reference", "production_bom", "conversion_rule")
    }
    if len(bom_rows) != 668 or len(delivery["items"]) != 668 or any(n != 668 for n in null_counts.values()):
        raise ValueError("expected 668 mapped parts and four null delivery-document references per part")

    part_inventory = []
    for row in bom_rows:
        part_id = row["part_id"]
        install = installation_parts[part_id]
        mapped = delivery_items[part_id]
        part_inventory.append(
            {
                "part_id": part_id,
                "assembly_id": row["assembly_id"],
                "quantity_per_train": int(row["quantity_per_train"]),
                "material_id": row["material_id"],
                "component_type_id": mapped.get("component_type_id"),
                "installation_component_definition_id": install.get("component_definition_id"),
                "source_evidence_payloads": ["vehicle_bom", "vehicle_installation", "delivery_mapping"],
                "assembly_glb_correspondence": "not asserted; this inventory does not map GLB mesh definitions to part IDs",
                "declaration_fields_are_controlled_documents": False,
                "controlled_documents": {
                    name: {"status": "missing", "reference": None} for name in CONTROLLED_PART_DOCUMENTS
                },
                "delivery_references": {
                    name: mapped.get(name)
                    for name in ("drawing_reference", "inspection_reference", "production_bom", "conversion_rule")
                },
            }
        )

    assembly_ids = sorted({row["assembly_id"] for row in bom_rows})
    installation_assemblies = set(installation.get("assembly_occurrences", {}))
    if set(assembly_ids) != installation_assemblies:
        raise ValueError("BOM assembly groups do not match installation assembly occurrence groups")
    assemblies = [
        {
            "assembly_id": assembly_id,
            "part_count": sum(row["assembly_id"] == assembly_id for row in bom_rows),
            "source_evidence_payloads": ["vehicle_bom", "vehicle_installation", "vehicle_assembly_glb"],
            "controlled_documents": {
                name: {"status": "missing", "reference": None} for name in CONTROLLED_ASSEMBLY_DOCUMENTS
            },
        }
        for assembly_id in assembly_ids
    ]
    if len(assemblies) != 41:
        raise ValueError("expected 41 source assembly groups")

    return {
        "schema": EXPECTED_SCHEMA,
        "purpose": "Source-linked manufacturing-document coverage draft; records gaps and does not release manufacture.",
        "identity": {
            "vehicle_candidate_id": candidate_id,
            "vehicle_evaluation_id": evaluation_id,
            "vehicle_manifest_id": manifest["manifest_id"],
            "pilot_publication_manifest_id": pilot_manifest["manifest_id"],
            "pilot_run_manifest_id": pilot_manifest["run_manifest_id"],
            "study_id": pilot_manifest["study_id"],
            "bundle_candidate_id": bundle["candidate_id"],
            "bundle_evaluation_id": bundle["evaluation_id"],
            "bundle_body_evaluation_id": bundle["body_evaluation_id"],
            "delivery_manifest_id": delivery_manifest["manifest_id"],
            "delivery_proposal_id": proposal["proposal_id"],
            "body_candidate_id": delivery_body["candidate_id"],
            "body_evaluation_id": delivery_body["evaluation_id"],
            "engineering_revision": delivery["identities"]["engineering_revision"],
            "service_evaluation_id": delivery["identities"]["service_evaluation_id"],
        },
        "delivery_identity_set": delivery["identities"],
        "source_manifests": source_manifests,
        "source_payloads": payloads,
        "source_payload_interpretation": "These are engineering BOM, installation, mapping and visualization payloads. Their presence does not make them controlled manufacturing documents.",
        "assembly_visualization_inventory": _glb_inventory(folder / "vehicle/assembly.glb"),
        "counts": {
            "parts": len(part_inventory),
            "assemblies": len(assemblies),
            "delivery_mapping_items": len(delivery["items"]),
            "delivery_status": delivery["status"],
            "null_delivery_reference_counts": null_counts,
            "per_part_missing_controlled_document_slots": len(part_inventory) * len(CONTROLLED_PART_DOCUMENTS),
            "per_assembly_missing_controlled_document_slots": len(assemblies) * len(CONTROLLED_ASSEMBLY_DOCUMENTS),
        },
        "missing_document_rationale": {
            "controlled_part_documents": list(CONTROLLED_PART_DOCUMENTS),
            "controlled_assembly_documents": list(CONTROLLED_ASSEMBLY_DOCUMENTS),
            "rule": "Only explicit controlled document payload references count. BOM prose, installation declarations, assembly mesh geometry, and null or invented references do not count.",
            "scope": "Missing means no controlled reference is present in the checked delivery mapping schema for this frozen packet. This is not a repository-wide search for other document payloads.",
        },
        "closure": {
            "manufacturing_documentation_complete": False,
            "manufacturing_release": False,
            "engineering_accepted": False,
            "physical_accepted": False,
            "erp_ready": False,
            "status": "held; controlled manufacturing documentation incomplete",
        },
        "parts": part_inventory,
        "assemblies": assemblies,
    }


def write_report(report: dict[str, Any], destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("docs/design-engine/reconciled-pilot-bogie-detail/vehicle/document-coverage.json"),
    )
    args = parser.parse_args()
    report = build_report(args.repo_root.resolve())
    destination = args.output if args.output.is_absolute() else args.repo_root / args.output
    write_report(report, destination)
    print(f"wrote {destination}: {report['counts']['parts']} parts, {report['counts']['assemblies']} assemblies; held")


if __name__ == "__main__":
    main()
