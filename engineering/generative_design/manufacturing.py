"""Audit actual issued/measurement records, separate from generative geometry."""

from __future__ import annotations

from collections import Counter
import csv
import json
from pathlib import Path

from .coverage import ROOT, local, sha

PDR = "design/component-catalogue/catalog/buildable-trainset/production-data-release-register.json"
FAI = "design/component-catalogue/catalog/buildable-trainset/first-article-inspection-plan.json"
DEFAULTS = "design/component-catalogue/catalog/buildable-trainset/default-product-specifications.json"
TRAIN = "design/component-catalogue/catalog/buildable-trainset/buildable-trainset-manifest.json"
QUALIFICATION = (
    "engineering/civil_exploration/examples/baghdad-qualification/qualification.json"
)


def read(name):
    return json.loads((ROOT / name).read_text())


def artifact_record(record, *, root=ROOT):
    """Check bytes and completeness of a recorded claim; no authority invention."""
    required = (
        "artifact_ref",
        "artifact_sha256",
        "revision",
        "checked_by",
        "approved_by",
        "issued_at",
    )
    missing = [name for name in required if not record.get(name)]
    if missing:
        return dict(
            state="missing",
            missing_fields=missing,
            bytes_verified=False,
            authority_independently_verified=False,
            manufacturing_release=False,
        )
    target = local(record["artifact_ref"], root)
    if not target.is_file() or sha(target) != record["artifact_sha256"]:
        return dict(
            state="invalid-artifact-bytes",
            missing_fields=[],
            bytes_verified=False,
            authority_independently_verified=False,
            manufacturing_release=False,
        )
    status = record.get("status", "")
    return dict(
        state=(
            "complete-record-claim"
            if status in {"issued", "approved", "released"}
            else "unissued-record"
        ),
        missing_fields=[],
        bytes_verified=True,
        recorded_approver=record["approved_by"],
        authority_independently_verified=False,
        manufacturing_release=False,
        limitation="Byte integrity and populated fields do not authenticate an approver, engineering adequacy or physical release; use existing project authority controls.",
    )


def run():
    pdr, fai, defaults, train, q = [
        read(p) for p in (PDR, FAI, DEFAULTS, TRAIN, QUALIFICATION)
    ]
    products = []
    requests = []
    seen = set()
    # Bind every file read, including drawing definitions and present production
    # evidence. A populated issue/reference field alone grants no acceptance.
    source_files = {
        p: sha(local(p, ROOT)) for p in (PDR, FAI, DEFAULTS, TRAIN, QUALIFICATION)
    }
    missing_references = set()

    def capture_reference(name):
        if not name:
            return
        path = local(name, ROOT)
        if path.is_file():
            source_files[name] = sha(path)
        else:
            missing_references.add(name)

    for product in pdr["products"]:
        records = []
        for artifact in product["required_artifacts"]:
            identifier = artifact["artifact_id"]
            if identifier in seen:
                raise ValueError("duplicate production artifact ID")
            seen.add(identifier)
            capture_reference(artifact.get("artifact_ref"))
            observed = artifact_record(artifact, root=ROOT)
            records.append(
                dict(
                    artifact_id=identifier,
                    artifact_type=artifact["artifact_type"],
                    required_content=artifact["required_content"],
                    source_status=artifact["status"],
                    observed=observed,
                )
            )
            if observed["state"] != "complete-record-claim":
                requests.append(
                    dict(
                        id=identifier,
                        product_id=product["product_id"],
                        package_ids=product["factory_package_ids"],
                        kind=artifact["artifact_type"],
                        required=artifact["required_content"],
                        source=PDR,
                        state=observed["state"],
                        supplier_contacted=False,
                    )
                )
        products.append(
            dict(
                product_id=product["product_id"],
                title=product["title"],
                package_ids=product["factory_package_ids"],
                source_release_status=product["release_status"],
                planning_route=product["planning_route"],
                design_reference_envelope_mm=product["design_reference_envelope_mm"],
                production_data_requirements=product["production_data_requirements"],
                artifacts=records,
                all_record_claims_complete=all(
                    r["observed"]["state"] == "complete-record-claim" for r in records
                ),
                manufacturing_release=False,
            )
        )
    if (
        len(seen) != pdr["required_artifact_count"]
        or len(products) != pdr["make_product_count"]
    ):
        raise ValueError("production register counts differ from actual records")
    inspections = []
    for package in fai["packages"]:
        for characteristic in package["characteristics"]:
            performed = (
                characteristic["execution_status"]
                not in {"not-performed", "planned", ""}
                and bool(characteristic["result"])
                and bool(characteristic["performed_at"])
                and bool(characteristic["inspected_by"])
            )
            inspections.append(
                dict(
                    id=characteristic["characteristic_id"],
                    package_id=(
                        package["package_id"]
                        if "package_id" in package
                        else package["id"]
                    ),
                    requirement=characteristic["requirement"],
                    method=characteristic["method"],
                    source_execution_status=characteristic["execution_status"],
                    actual_result_record_present=performed,
                    accepted=False,
                    reason="Actual work-order-linked results and authority/NCR closure must be verified; a planned characteristic is not a result",
                )
            )
    if len(inspections) != fai["characteristic_count"]:
        raise ValueError("inspection characteristic count differs")
    supplier = []
    for row in defaults["defaults"]:
        supplier.append(
            dict(
                product_id=row["product_id"],
                proposed_default=row["default_name"],
                candidate_ids=row["candidate_ids"],
                use_class=row["use_class"],
                public_parameters=row["public_parameters"],
                required_before_freeze=row["must_close_before_freeze"],
                accepted_supplier_configuration=False,
                supplier_contacted=False,
            )
        )
    all_products = {p["id"] for p in train["product_items"]}
    allocation = {p["product_id"] for p in products} | {
        p["product_id"] for p in supplier
    }
    if allocation != all_products or {p["product_id"] for p in products} & {
        p["product_id"] for p in supplier
    }:
        raise ValueError(
            "make/supplier evidence allocation does not partition all vehicle products"
        )
    drawing_records = []
    for folder in ("buildable-trainset", "buildable-stations"):
        base = ROOT / "design/component-catalogue/catalog" / folder / "factory-drawings"
        for path in sorted(base.glob("*.json")):
            source_name = path.relative_to(ROOT).as_posix()
            source_files[source_name] = sha(local(source_name, ROOT))
            row = json.loads(path.read_text())
            if "drawing_id" not in row:
                continue
            issue = row.get("issue_record", {})
            capture_reference(issue.get("published_drawing_ref"))
            drawing_records.append(
                dict(
                    drawing_id=row["drawing_id"],
                    source=path.relative_to(ROOT).as_posix(),
                    source_status=row["issue_status"],
                    required_controls=row.get("mandatory_drawing_controls", []),
                    actual_issued_drawing_ref=issue.get("published_drawing_ref")
                    or None,
                    actual_issued_drawing_sha256=issue.get("published_drawing_sha256")
                    or None,
                    recorded_checked_by=issue.get("checked_by") or None,
                    recorded_approved_by=issue.get("approved_by") or None,
                    manufacturing_release=False,
                )
            )
    return dict(
        schema="osr-queued-manufacturing-evidence-audit/1",
        products=products,
        supplier_configuration_requests=supplier,
        inspection_characteristics=inspections,
        drawings=drawing_records,
        artifact_requests=requests,
        deployment_inputs=q["missing_inputs"],
        counts=dict(
            vehicle_products=len(all_products),
            local_production_products=len(products),
            supplier_configuration_products=len(supplier),
            required_production_artifacts=len(seen),
            missing_or_unissued_production_artifacts=len(requests),
            inspection_characteristics=len(inspections),
            actual_inspection_result_records=sum(
                i["actual_result_record_present"] for i in inspections
            ),
            drawing_definitions=len(drawing_records),
            issued_drawing_references=sum(
                bool(r["actual_issued_drawing_ref"]) for r in drawing_records
            ),
        ),
        sources_sha256=dict(sorted(source_files.items())),
        missing_referenced_artifacts=sorted(missing_references),
        manufacturing_release=False,
        physical_release=False,
    )


def package_evidence(package, audit):
    ids = {i for source in package["authoritative_sources"] for i in source["ids"]}
    products = [
        p
        for p in audit["products"]
        if package["id"] in p["package_ids"] or p["product_id"] in ids
    ]
    supplier = [
        p for p in audit["supplier_configuration_requests"] if p["product_id"] in ids
    ]
    inspections = [
        c
        for c in audit["inspection_characteristics"]
        if c["package_id"] == package["id"]
    ]
    return dict(
        local_product_ids=[p["product_id"] for p in products],
        required_artifact_ids=[
            r["artifact_id"] for p in products for r in p["artifacts"]
        ],
        missing_or_unissued_artifact_ids=[
            r["artifact_id"]
            for p in products
            for r in p["artifacts"]
            if r["observed"]["state"] != "complete-record-claim"
        ],
        supplier_product_ids=[p["product_id"] for p in supplier],
        inspection_characteristic_ids=[c["id"] for c in inspections],
        actual_inspection_result_records=sum(
            c["actual_result_record_present"] for c in inspections
        ),
        independent_design_acceptance=False,
        manufacturing_release=False,
    )


def write_artifacts(report, output):
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    for name, rows, fields in (
        (
            "production-artifact-requests.csv",
            report["artifact_requests"],
            (
                "id",
                "product_id",
                "package_ids",
                "kind",
                "required",
                "source",
                "state",
                "supplier_contacted",
            ),
        ),
        (
            "inspection-execution-register.csv",
            report["inspection_characteristics"],
            (
                "id",
                "package_id",
                "requirement",
                "method",
                "source_execution_status",
                "actual_result_record_present",
                "accepted",
                "reason",
            ),
        ),
        (
            "supplier-configuration-requests.csv",
            report["supplier_configuration_requests"],
            (
                "product_id",
                "proposed_default",
                "candidate_ids",
                "use_class",
                "public_parameters",
                "required_before_freeze",
                "accepted_supplier_configuration",
                "supplier_contacted",
            ),
        ),
    ):
        with (output / name).open("w", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=fields)
            writer.writeheader()
            for row in rows:
                writer.writerow(
                    {
                        k: (
                            json.dumps(row[k])
                            if isinstance(row[k], (list, dict))
                            else row[k]
                        )
                        for k in fields
                    }
                )
    return [
        output / name
        for name in (
            "production-artifact-requests.csv",
            "inspection-execution-register.csv",
            "supplier-configuration-requests.csv",
        )
    ]
