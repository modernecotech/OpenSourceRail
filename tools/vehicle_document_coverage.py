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
    if bundle.get("body_evaluation_id") != evaluation_id:
        raise ValueError("top-level pilot bundle does not reference the frozen vehicle evaluation")

    source_specs = [
        ("pilot_publication_manifest", "manifest.json", None),
        ("vehicle_manifest", "vehicle/manifest.json", None),
        ("vehicle_bom", "vehicle/bom.csv", "bom.csv"),
        ("vehicle_installation", "vehicle/installation.json.gz", "installation.json.gz"),
        ("vehicle_assembly_glb", "vehicle/assembly.glb", "assembly.glb"),
        ("delivery_mapping", "delivery/execution-mapping-draft.json", None),
        ("pilot_bundle", "bundle.json", None),
    ]
    payloads: dict[str, dict[str, str]] = {}
    for key, relpath, manifest_key in source_specs:
        path = folder / relpath
        digest = sha256(path)
        if manifest_key and manifest["files_sha256"].get(manifest_key) != digest:
            raise ValueError(f"{relpath} does not match the vehicle manifest SHA-256 pin")
        payloads[key] = {"path": str(PACKET / relpath), "sha256": digest}

    with (folder / "vehicle/bom.csv").open(newline="", encoding="utf-8") as stream:
        bom_rows = list(csv.DictReader(stream))
    with gzip.open(folder / "vehicle/installation.json.gz", "rt", encoding="utf-8") as stream:
        installation = json.load(stream)
    delivery = _read_json(folder / "delivery/execution-mapping-draft.json")
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
        },
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
