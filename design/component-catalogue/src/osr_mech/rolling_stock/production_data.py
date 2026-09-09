"""Fail-closed production-data release register for locally made LM3 parts.

The register joins the EBOM, factory drawing packages, tooling/control registry
and first-article ITP.  It deliberately defines *which* manufacturing data must
exist without turning design-reference envelopes into cutting dimensions.
"""

from __future__ import annotations

from collections import Counter
from typing import Any, Iterable


BOUNDARY = (
    "This register assigns production-data ownership and evidence slots. Geometry envelopes, "
    "planning routes and blank artifact records are not shop dimensions, approved process data, "
    "inspection results or authority to manufacture. A competent design authority must issue the "
    "exact material, datums, tolerances, NC/flat-pattern or mould data and special-process controls."
)


COMPOSITE_FORMS = {"body-module", "cowl", "roof-fairing"}
EXTRUSION_FORMS = {"beam", "service-rail", "rail-kit", "adapter-kit", "window-frame", "door-frame"}
STRUCTURAL_FORMS = {
    "underframe", "cross-bearer-kit", "bolster", "coupler-pocket", "floor", "floor-deck",
    "side-frame", "roof-rack", "frame", "bogie-frame", "bogie-guards", "recovery-kit",
    "front-glass-carrier", "front-lamp-carrier", "link-kit",
}


def _route(form: str, title: str) -> tuple[str, list[str], list[tuple[str, str]]]:
    """Return a conservative planning route, controls and artifact additions."""

    text = title.lower()
    if form in COMPOSITE_FORMS or "fiberglass" in text or "frp" in text:
        return (
            "composite-mould-trim-and-fit",
            [
                "freeze laminate, core, insert, split-line and trim-datum definitions",
                "release mould surface, release-agent, material shelf-life and cure controls",
                "retain batch, cure, coupon, trim, sealed-edge and insert evidence",
            ],
            [
                ("laminate-schedule", "ply/core/solid-land/insert book with material and orientation"),
                ("mould-definition", "controlled mould surface, split line, datums and inspection file"),
                ("trim-drill-data", "datum-based trim/drill paths and sealed-edge requirements"),
                ("cure-coupon-plan", "cure cycle, witness coupon and acceptance schedule"),
            ],
        )
    if form == "harness":
        return (
            "harness-cut-terminate-formboard-and-test",
            [
                "freeze wire/cable, terminal, connector, seal, label and protection part numbers",
                "release cut lengths, pin allocation, formboard route, clamp spacing and bend limits",
                "record calibrated crimp results, continuity, insulation and configuration test",
            ],
            [
                ("wire-cut-and-terminal-schedule", "wire IDs, gauges, lengths, terminals, seals and labels"),
                ("connector-pinout", "connector views, cavity allocations, keying and backshell definition"),
                ("formboard-routing-data", "branch points, breakouts, protection, clamps and minimum bends"),
                ("electrical-test-schedule", "continuity, resistance, insulation and configuration limits"),
            ],
        )
    if form == "piping" or any(word in text for word in ("coolant", "tube", "pipe", "manifold")):
        return (
            "tube-cut-bend-bracket-and-pressure-test",
            [
                "freeze fluid-compatible tube, fitting, clamp and isolation materials",
                "release developed lengths, bend table, orientation datums and cleanliness limits",
                "record forming, cleanliness, pressure/leak and drain/bleed checks",
            ],
            [
                ("tube-cut-and-bend-schedule", "developed lengths, bend radii/angles and end orientation"),
                ("fitting-and-clamp-map", "fitting, clamp, isolation and torque authority by location"),
                ("pressure-test-schedule", "medium, pressure, duration, leakage and cleanliness criteria"),
            ],
        )
    if form in STRUCTURAL_FORMS:
        return (
            "cut-form-machine-fixture-and-join",
            [
                "release material thickness/section, datum scheme, tolerance stack and machining allowances",
                "release cut/nest or flat-pattern data, bend sequence and springback trial where applicable",
                "release joint map, WPS/adhesive/fastener authority, distortion control and NDT class",
            ],
            [
                ("cut-nest-and-flat-pattern-data", "revision-locked cut list, nesting/NC and developed blanks"),
                ("forming-and-machining-schedule", "bend order, springback trial, machining and datum transfers"),
                ("joint-and-weld-map", "joint IDs, sequence, WPS/fastener/adhesive authority and NDT class"),
                ("fixture-and-datum-plan", "fixture revision, set points, restraint, survey and release sequence"),
            ],
        )
    if form in EXTRUSION_FORMS:
        return (
            "section-cut-machine-drill-and-fit",
            [
                "freeze stock section/material and datum end before cutting",
                "release cut length, hole/slot, machining, deburr and mixed-metal isolation data",
                "gauge interfaces and retain stock heat/batch and dimensional evidence",
            ],
            [
                ("section-cut-list", "stock section, cut length, end preparation and yield allowance"),
                ("machining-and-drill-data", "datum-based holes, slots, inserts, threads and deburr notes"),
                ("interface-gauge-plan", "functional gauge definition and dimensional result schedule"),
            ],
        )
    return (
        "mixed-kit-cut-form-machine-and-fit",
        [
            "split the kit into controlled make/buy child positions before production release",
            "freeze material, datums, tolerances, joining and finish by child position",
            "release cut/form/machine data and functional gauges appropriate to each child",
        ],
        [
            ("kit-position-and-cut-list", "child IDs, quantities, stock forms, cuts and configuration rules"),
            ("forming-machining-and-fit-data", "child production data, datum transfers and fit sequence"),
            ("joint-and-interface-map", "joint IDs, authority, functional interfaces and gauge checks"),
        ],
    )


def _unique(values: Iterable[str]) -> list[str]:
    return list(dict.fromkeys(values))


def production_data_release_payload(
    product_items: Iterable[Any],
    factory_release: dict[str, Any],
    inspection_plan: dict[str, Any],
    drawing_seeds: Iterable[dict[str, Any]],
) -> dict[str, Any]:
    """Join all locally made parts to required, deliberately unissued production data."""

    make_items = {item.id: item for item in product_items if item.route.value == "MAKE"}
    package_by_id = {row["id"]: row for row in factory_release["packages"]}
    inspection_by_package = {row["package_id"]: row for row in inspection_plan["packages"]}
    drawings_by_product: dict[str, list[str]] = {}
    for seed in drawing_seeds:
        for product in seed["product_rows"]:
            drawings_by_product.setdefault(product["id"], []).append(seed["drawing_id"])
    ownership: dict[str, dict[str, list[str]]] = {
        product_id: {"packages": [], "drawings": [], "tooling": [], "controls": [], "inspection": []}
        for product_id in make_items
    }
    geometry_rows: dict[str, dict[str, Any]] = {}

    for package_id, package in package_by_id.items():
        itp = inspection_by_package[package_id]
        for product in package["product_rows"]:
            product_id = product["id"]
            if product_id not in make_items:
                continue
            geometry_rows.setdefault(product_id, product)
            row = ownership[product_id]
            row["packages"].append(package_id)
            owned_drawings = [
                drawing_id for drawing_id in package["drawing_ids"]
                if drawing_id in drawings_by_product.get(product_id, [])
            ]
            row["drawings"].extend(owned_drawings)
            row["tooling"].extend(package["tooling_ids"])
            row["controls"].extend(package["reference_control_ids"])
            relevant_subjects = {product_id, *owned_drawings, *package["reference_control_ids"]}
            row["inspection"].extend(
                characteristic["characteristic_id"]
                for characteristic in itp["characteristics"]
                if characteristic["subject_id"] in relevant_subjects
            )

    rows: list[dict[str, Any]] = []
    for product_id, item in sorted(make_items.items()):
        if product_id not in geometry_rows:
            raise ValueError(f"locally made product has no factory drawing coverage: {product_id}")
        geometry = geometry_rows[product_id]
        links = {key: _unique(values) for key, values in ownership[product_id].items()}
        route, route_controls, additions = _route(str(geometry["geometry_form"]), item.title)
        requirements = [
            "issue a checked part/kit drawing with material, functional datums, tolerances, finish and mass scope",
            "bind the exact drawing and production-data revision to the work order and parent configuration",
            "retain material identity, lot/heat/batch certificates and approved substitution records",
            *route_controls,
            "release a finish, corrosion/fire/UV protection and repair-zone schedule",
            "close linked first-article inspection characteristics and NCRs before disposition",
        ]
        artifact_definitions = [
            ("released-drawing", "issued drawing with datum scheme, dimensions, tolerances and revision approvals"),
            ("material-and-lot-pack", "material specification, certificate, heat/batch/lot and substitution evidence"),
            *additions,
            ("finish-and-marking-schedule", "surface preparation, finish zones, labels and repair process"),
            ("inspection-and-release-record", "actual measurements/results against linked characteristic IDs"),
        ]
        artifacts = [
            {
                "artifact_id": f"PDR-{product_id}-{index:02d}",
                "artifact_type": artifact_type,
                "required_content": content,
                "status": "open-unissued",
                "revision": "",
                "artifact_ref": "",
                "artifact_sha256": "",
                "checked_by": "",
                "approved_by": "",
                "issued_at": "",
            }
            for index, (artifact_type, content) in enumerate(artifact_definitions, 1)
        ]
        rows.append(
            {
                "product_id": product_id,
                "title": item.title,
                "parent": item.parent,
                "quantity_per_trainset": item.quantity_per_trainset,
                "unit": item.unit,
                "geometry_form": geometry["geometry_form"],
                "geometry_representation": geometry["geometry_representation"],
                "design_reference_envelope_mm": geometry["design_reference_envelope_mm"],
                "planning_route": route,
                "factory_package_ids": links["packages"],
                "drawing_ids": links["drawings"],
                "tooling_ids": links["tooling"],
                "manufacturing_control_ids": links["controls"],
                "inspection_characteristic_ids": links["inspection"],
                "production_data_requirements": requirements,
                "required_artifacts": artifacts,
                "release_status": "open-unissued",
                "released_by": "",
                "released_at": "",
                "authority_boundary": BOUNDARY,
            }
        )

    artifact_ids = [artifact["artifact_id"] for row in rows for artifact in row["required_artifacts"]]
    validation = {
        "exact_make_product_set_covered_once": {row["product_id"] for row in rows} == set(make_items),
        "all_rows_have_factory_package_and_drawing_ownership": all(row["factory_package_ids"] and row["drawing_ids"] for row in rows),
        "all_rows_have_geometry_and_planning_route": all(row["geometry_form"] and row["planning_route"] for row in rows),
        "all_rows_have_tooling_controls_and_inspection_links": all(row["tooling_ids"] and row["manufacturing_control_ids"] and row["inspection_characteristic_ids"] for row in rows),
        "all_required_artifact_ids_unique": len(artifact_ids) == len(set(artifact_ids)),
        "all_release_states_fail_closed": all(
            row["release_status"] == "open-unissued"
            and not row["released_by"]
            and all(artifact["status"] == "open-unissued" and not artifact["artifact_ref"] for artifact in row["required_artifacts"])
            for row in rows
        ),
    }
    if len(rows) != 62 or not all(validation.values()):
        raise ValueError(f"invalid LM3 production-data coverage: rows={len(rows)}, validation={validation}")
    route_counts = dict(sorted(Counter(row["planning_route"] for row in rows).items()))
    return {
        "schema": "org.opensourcerail.lm3-production-data-release-register.v1",
        "design_id": factory_release["design_id"],
        "status": "all-locally-made-production-data-open-unissued",
        "source_factory_release": "factory-release-work-packages.json",
        "source_inspection_plan": "first-article-inspection-plan.json",
        "make_product_count": len(rows),
        "open_product_count": len(rows),
        "required_artifact_count": len(artifact_ids),
        "planning_route_counts": route_counts,
        "authority_boundary": BOUNDARY,
        "common_release_rule": (
            "No locally made product may enter production until every required artifact is issued, "
            "revision-compatible, hash-bound, checked and approved and its package hold points permit work."
        ),
        "products": rows,
        "validation": validation,
    }


def render_production_data_release(payload: dict[str, Any]) -> str:
    lines = [
        "# LM3 Production-Data Release Register",
        "",
        "> Status: **all locally made production data open and unissued**.",
        "",
        "This register connects every locally made product to its drawing package, planning",
        "route, tooling, work instruction, inspection characteristics and required production",
        "artifacts. Fill the JSON records only in a controlled project copy.",
        "",
        f"Products: **{payload['make_product_count']}** · Open: **{payload['open_product_count']}** · Required artifact slots: **{payload['required_artifact_count']}**.",
        "",
        "## Planning Route Summary",
        "",
        "| Route | Products |",
        "|---|---:|",
    ]
    for route, count in payload["planning_route_counts"].items():
        lines.append(f"| `{route}` | {count} |")
    lines += [
        "",
        "## Per-Product Ownership",
        "",
        "| Product | Planning route | Packages | Drawings | Artifacts | Inspection links | Status |",
        "|---|---|---|---:|---:|---:|---|",
    ]
    for row in payload["products"]:
        packages = ", ".join(f"`{value}`" for value in row["factory_package_ids"])
        lines.append(
            f"| `{row['product_id']}` — {row['title']} | `{row['planning_route']}` | {packages} | "
            f"{len(row['drawing_ids'])} | {len(row['required_artifacts'])} | "
            f"{len(row['inspection_characteristic_ids'])} | `{row['release_status']}` |"
        )
    lines += [
        "",
        "## Release Rule",
        "",
        payload["common_release_rule"],
        "",
        "Use the [drawing seeds](factory-drawings/index.md) to develop the issued drawings,",
        "the [manufacturing controls](manufacturing-and-assembly-controls.md) for work execution,",
        "and the [first-article ITP](first-article-inspection-plan.md) for actual acceptance results.",
        "",
        f"Boundary: {payload['authority_boundary']}",
        "",
    ]
    return "\n".join(lines)


__all__ = ["production_data_release_payload", "render_production_data_release"]
