"""Generate a fail-closed LM3 inspection and test plan from factory packages."""

from __future__ import annotations

from collections import Counter
from typing import Any


def _characteristic(
    characteristic_id: str,
    point_type: str,
    stage: str,
    subject_id: str,
    requirement: str,
    method: str,
    sampling: str,
    acceptance_authority: str,
) -> dict[str, Any]:
    return {
        "characteristic_id": characteristic_id,
        "point_type": point_type,
        "stage": stage,
        "subject_id": subject_id,
        "requirement": requirement,
        "method": method,
        "sampling": sampling,
        "acceptance_authority": acceptance_authority,
        "execution_status": "not-performed",
        "result": "",
        "result_ref": "",
        "inspected_by": "",
        "witnessed_by": "",
        "performed_at": "",
        "ncr_refs": [],
    }


def factory_inspection_plan_payload(factory_release: dict[str, Any]) -> dict[str, Any]:
    packages = []
    all_characteristic_ids: set[str] = set()
    for package in factory_release["packages"]:
        prefix = f"LM3-IP-{str(package['id']).split('-')[-1]}"
        rows: list[dict[str, Any]] = []

        def add(category: str, values: list[Any], build: Any) -> None:
            for index, value in enumerate(values, 1):
                characteristic_id = f"{prefix}-{category}-{index:02d}"
                if characteristic_id in all_characteristic_ids:
                    raise ValueError(f"duplicate LM3 inspection characteristic {characteristic_id}")
                all_characteristic_ids.add(characteristic_id)
                rows.append(build(characteristic_id, value))

        add(
            "PRE",
            list(package["frozen_inputs"]),
            lambda cid, value: _characteristic(
                cid, "H", "before-work-release", package["id"], str(value),
                "controlled-document and evidence review", "100% before package start",
                "design authority and manufacturing engineering",
            ),
        )
        add(
            "DRW",
            list(package["drawing_ids"]),
            lambda cid, value: _characteristic(
                cid, "R", "drawing-release", str(value),
                "issued drawing revision matches the work order and product configuration",
                "revision/status/signature and source-hash review", "100% of every drawing revision",
                "drawing checker and design authority",
            ),
        )
        add(
            "PRD",
            list(package["product_rows"]),
            lambda cid, value: _characteristic(
                cid, "H", "material-and-product-receipt", str(value["id"]),
                f"identity, quantity, revision/lot, traceability, condition and mass scope accepted for {value['title']}",
                "receipt inspection against released drawing, purchase order and certificate pack",
                "100% first article and safety/interface product; approved control plan may define later routine sampling",
                "quality and responsible product engineer",
            ),
        )
        add(
            "TOL",
            list(package["tooling_ids"]),
            lambda cid, value: _characteristic(
                cid, "H", "tooling-release", str(value),
                "tool identity/revision, condition, datum survey or calibration and operating range accepted",
                "tool register plus as-found/as-left survey or calibration review", "100% before first use, after move/repair and at defined interval",
                "manufacturing engineering and quality",
            ),
        )
        add(
            "CTL",
            list(package["reference_control_ids"]),
            lambda cid, value: _characteristic(
                cid, "W", "manufacturing-execution", str(value),
                "applicable steps performed or superseded by an approved procedure; stop conditions and NCRs dispositioned",
                "completed manufacturing-control record and witness evidence",
                "as specified by the referenced control; never less than 100% for first article and safety/interface characteristics",
                "cell lead and independent quality inspector",
            ),
        )
        add(
            "OUT",
            list(package["controlled_outputs"]),
            lambda cid, value: _characteristic(
                cid, "R", "controlled-output-review", package["id"], str(value),
                "artifact/revision/hash review against package requirement", "100% of required outputs",
                "responsible engineer and configuration control",
            ),
        )
        add(
            "VER",
            list(package["verification"]),
            lambda cid, value: _characteristic(
                cid, "H", "verification-and-handback", package["id"], str(value),
                "approved inspection/test procedure with calibrated evidence and NCR closure",
                "100% first article; later sampling only through an approved inspection plan",
                "quality, responsible engineer and independent witness where classified",
            ),
        )
        packages.append(
            {
                "package_id": package["id"],
                "title": package["title"],
                "plan_status": "unfilled-protocol-not-execution-evidence",
                "lot_definition": "one controlled first-article package; production lot/batch limits require an approved control plan",
                "release_boundary": package["release_boundary"],
                "characteristic_count": len(rows),
                "point_type_counts": dict(sorted(Counter(row["point_type"] for row in rows).items())),
                "characteristics": rows,
                "package_disposition": "open",
                "accepted_by": "",
                "accepted_at": "",
            }
        )
    return {
        "schema": "org.opensourcerail.lm3-first-article-inspection-plan.v1",
        "status": "unfilled-protocol-not-execution-evidence",
        "design_id": factory_release["design_id"],
        "source_factory_release": "factory-release-work-packages.json",
        "package_count": len(packages),
        "characteristic_count": sum(row["characteristic_count"] for row in packages),
        "point_types": {
            "H": "mandatory hold point; work may not pass until accepted",
            "W": "witness point; notify the named witness and record attendance or authorised waiver",
            "R": "document/record review point",
        },
        "common_rules": [
            "record actual results only while executing the identified work order and configuration",
            "a blank, planned or design-reference result does not satisfy a characteristic",
            "on failure stop, contain since the last accepted check, raise an NCR and extend inspection as the approved disposition requires",
            "do not waive a safety, structural, fire, braking, door, glazing, HV, lifting or recovery characteristic through routine sampling",
            "package acceptance requires every characteristic accepted, NCRs closed or expressly accepted, and named approvals recorded",
        ],
        "packages": packages,
        "validation": {
            "all_factory_packages_covered_once": True,
            "all_characteristic_ids_unique": True,
            "all_results_unperformed": all(
                row["execution_status"] == "not-performed"
                for package in packages
                for row in package["characteristics"]
            ),
            "all_package_dispositions_open": True,
        },
    }


def render_factory_inspection_plan(payload: dict[str, Any]) -> str:
    lines = [
        "# LM3 First-Article Inspection and Test Plan",
        "",
        "> Status: **unfilled protocol — not manufacturing, inspection or test evidence**.",
        "",
        "This plan converts every factory release package into uniquely identified hold,",
        "witness and record-review characteristics. Detailed result fields remain blank in",
        "the JSON until copied into an authorised first-article build record.",
        "",
        f"Packages: **{payload['package_count']}** · Characteristics: **{payload['characteristic_count']}**.",
        "",
        "Point types: **H** mandatory hold, **W** witness, **R** record review.",
        "",
        "## Package Index",
        "",
        "| Package | Characteristics | H | W | R | Status |",
        "|---|---:|---:|---:|---:|---|",
    ]
    for package in payload["packages"]:
        counts = package["point_type_counts"]
        lines.append(
            f"| `{package['package_id']}` — {package['title']} | {package['characteristic_count']} | "
            f"{counts.get('H', 0)} | {counts.get('W', 0)} | {counts.get('R', 0)} | `{package['package_disposition']}` |"
        )
    lines += ["", "## Execution Rules", ""]
    lines += [f"- {rule}" for rule in payload["common_rules"]]
    lines += [
        "",
        "Use [`manufacturing-control-record-template.json`](evidence/manufacturing-control-record-template.json)",
        "for the detailed operation record and retain characteristic IDs when importing this plan into a QMS.",
        "The factory release remains governed by [`factory-release-readiness.md`](factory-release-readiness.md).",
        "",
    ]
    return "\n".join(lines)
