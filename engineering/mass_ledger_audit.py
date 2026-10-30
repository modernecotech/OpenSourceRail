"""Occurrence-to-account reconciliation for the selected v0.6 vehicle.

This is a reporting layer. It does not create missing installed mass, locations,
or qualification evidence.
"""
from __future__ import annotations

import argparse
import gzip
import io
import json
import os
import tomllib
from collections import defaultdict
from hashlib import sha256
from pathlib import Path

from engineering.station_rail import evaluation, vehicle
from engineering.station_rail.common import encoded, identity

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = "docs/design-engine/mass-reconciliation/current"
FLAGS = dict(
    engineering_accepted=False,
    physical_accepted=False,
    installed_mass_complete=False,
    manufacturing_release=False,
    operating_release=False,
)


def _digest(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def _deterministic_gzip(data: bytes) -> bytes:
    """Write a gzip member with a fixed header across supported Python versions."""
    target = io.BytesIO()
    with gzip.GzipFile(fileobj=target, filename="", mode="wb", mtime=0) as stream:
        stream.write(data)
    return target.getvalue()


def _row(**fields):
    fields["row_id"] = identity(fields)
    return fields


def _retained_source_rows(parent):
    excluded = {"magnetics", "propulsion", "protection", "hardpoints"}
    return [
        row for row in parent["inventory"]
        if row["system"] not in excluded
        and "replacement-frame/extrusion/frame/lower-stringer" not in row["id"]
    ]


def reconcile(candidate, parent):
    """Map source accounts and candidate geometry by explicit parent account."""
    geometry = candidate["geometry_parts"]
    geometry_ids = [part["id"] for part in geometry]
    if len(geometry_ids) != len(set(geometry_ids)):
        raise ValueError("Duplicate candidate geometry occurrence ID")
    retained = _retained_source_rows(parent)
    retained_ids = [row["id"] for row in retained]
    if len(set(retained_ids)) != len(retained):
        raise ValueError("Duplicate retained source inventory occurrence ID")
    retained_accounts = defaultdict(list)
    for source in retained:
        retained_accounts[source["system"]].append(source)
    retained_geometry = defaultdict(list)
    new_geometry = defaultdict(list)
    geometry_parent = {}
    for part in geometry:
        part_id = part["id"]
        if part_id.startswith("comfort-shell/"):
            family = part_id[len("comfort-shell/"):].split("/", 1)[0]
            if family == "seat-unit":
                system = "seating"
            elif family == "door":
                system = "doors"
            elif family in ("fixed-window", "door-window"):
                system = "glazing"
            else:
                system = "body"
            group = "retained-comfort/" + system
            retained_geometry[system].append(part)
        elif part_id.startswith("bogie/"):
            group = "passive-bogie-pair"
            new_geometry[group].append(part)
        elif part_id.startswith("wheel-underframe/"):
            group = "wheel-underframe"
            new_geometry[group].append(part)
        elif part_id.startswith("station-secondary/"):
            group = "passive-secondary"
            new_geometry[group].append(part)
        else:
            raise ValueError("Candidate geometry is not assigned to a mass account: " + part_id)
        geometry_parent[part_id] = group

    source_occurrences = []
    accounts = []
    for system in sorted(retained_accounts):
        source_rows = retained_accounts[system]
        account_mass = sum(float(row["mass_kg"]) for row in source_rows)
        parts = retained_geometry[system]
        geometry_mass = sum(float(part["mass_kg"]) for part in parts)
        residual = account_mass - geometry_mass
        if residual < -1e-7:
            raise ValueError("Located geometry exceeds retained system account: " + system)
        if residual < 0:
            residual = 0.0
        account_id = "retained-comfort/" + system
        accounts.append(dict(
            account_id=account_id,
            source_system=system,
            accounted_mass_kg=account_mass,
            located_geometry_mass_kg=geometry_mass,
            residual_account_mass_kg=residual,
            source_occurrence_ids=[row["id"] for row in source_rows],
            candidate_geometry_occurrence_ids=[part["id"] for part in parts],
            mapping_method="system-account plus explicit geometry-family classification; no row-to-row match is claimed",
            disposition="retained-source-account-with-candidate-geometry-subset" if parts else "retained-source-account-without-candidate-geometry",
        ))
        for source in source_rows:
            source_occurrences.append(dict(
                account_id=account_id,
                occurrence_id=source["id"],
                occurrence_definition_id=source.get("occurrence_definition_id"),
                source_part_id=source.get("source_part_id"),
                source_system=system,
                role=source.get("role"),
                evidence_class=source.get("evidence_class"),
                source_location_known=source.get("global_installation_location_known"),
                mass_kg=float(source["mass_kg"]),
            ))

    inventory = {item["id"]: item for item in candidate["inventory"]}
    bogie_account = inventory["passive-bogie-pair"]
    bogie_geometry = new_geometry["passive-bogie-pair"]
    bogie_located = sum(float(part["mass_kg"]) for part in bogie_geometry)
    bogie_residual = float(bogie_account["mass_kg"]) - bogie_located
    if bogie_residual < -1e-7 or abs(bogie_located - float(bogie_account["located_stock_kg"])) > 1e-7:
        raise ValueError("Bogie geometry does not reconcile with its explicit account")
    if abs(bogie_residual - float(bogie_account["unlocated_remainder_kg"])) > 1e-7:
        raise ValueError("Bogie residual differs from the declared unlocated remainder")
    accounts.append(dict(
        account_id="passive-bogie-pair",
        source_system="bogies",
        accounted_mass_kg=float(bogie_account["mass_kg"]),
        located_geometry_mass_kg=bogie_located,
        residual_account_mass_kg=bogie_residual,
        source_occurrence_ids=[],
        candidate_geometry_occurrence_ids=[part["id"] for part in bogie_geometry],
        mapping_method="candidate geometry parts plus retained bogie category balance",
        disposition="partial-proposed-material-with-explicit-reference-residual",
    ))

    scalar_accounts = (
        ("service-battery", "services", "supplier-cell-and-installed-pack-account",
         "Service-cell and installed-pack estimate; geometry, mounts, wiring and cooling are not located."),
        ("white-roof-finish", "roof-thermal", "counted-coating-stock",
         "Coating takeoff; no solid occurrence or installed centre of gravity is represented."),
        ("new-frame-joints-and-fin-retention", "attachments", "explicit-unlocated-allocation",
         "Unlocated allowance for body/bogie joints, fin retention and thermal joints."),
    )
    for item_id, group, evidence, basis in scalar_accounts:
        item = inventory[item_id]
        mass = float(item["mass_kg"])
        accounts.append(dict(
            account_id=group,
            source_system=item["system"],
            accounted_mass_kg=mass,
            located_geometry_mass_kg=0.0,
            residual_account_mass_kg=mass,
            source_occurrence_ids=[item_id],
            candidate_geometry_occurrence_ids=[],
            mapping_method="declared scalar account; no candidate solid occurrence",
            disposition="retained-account-without-candidate-geometry",
        ))
        source_occurrences.append(dict(
            account_id=group,
            occurrence_id=item_id,
            occurrence_definition_id=None,
            source_part_id=None,
            source_system=item["system"],
            role=basis,
            evidence_class=evidence,
            source_location_known=False,
            mass_kg=mass,
        ))

    accounts.extend([
        dict(account_id=group, source_system=group, accounted_mass_kg=sum(float(part["mass_kg"]) for part in parts),
             located_geometry_mass_kg=sum(float(part["mass_kg"]) for part in parts), residual_account_mass_kg=0.0,
             source_occurrence_ids=[], candidate_geometry_occurrence_ids=[part["id"] for part in parts],
             mapping_method="exact candidate geometry occurrence mass", disposition="candidate-geometry-accounted-once")
        for group, parts in (("wheel-underframe", new_geometry["wheel-underframe"]),
                             ("passive-secondary", new_geometry["passive-secondary"]))
    ])

    candidate_ids = set(geometry_ids)
    mapped_ids = [part_id for account in accounts for part_id in account["candidate_geometry_occurrence_ids"]]
    if len(mapped_ids) != len(set(mapped_ids)) or set(mapped_ids) != candidate_ids:
        raise ValueError("Candidate geometry occurrences are not assigned exactly once to mass accounts")

    geometry_occurrences = []
    for part in geometry:
        group = geometry_parent[part["id"]]
        geometry_occurrences.append(dict(
            occurrence_id=part["id"],
            account_id=group,
            geometry_kind=part.get("kind"),
            material=part.get("material"),
            system=part.get("system"),
            mass_kg=float(part["mass_kg"]),
            cg_m=part.get("cg_m"),
            mapping_method="geometry-family-to-system-account" if group.startswith("retained-comfort/") else "exact-candidate-component-account",
        ))
    accounted = sum(float(account["accounted_mass_kg"]) for account in accounts)
    located = sum(float(part["mass_kg"]) for part in geometry_occurrences)
    residual = sum(float(account["residual_account_mass_kg"]) for account in accounts)
    if abs(accounted - float(candidate["mass"]["accounted_tare_kg_per_car"])) > 1e-6:
        raise ValueError("Mass ledger rows do not reconcile to accounted vehicle tare")
    if abs(located - float(candidate["mass"]["located_material_kg"])) > 1e-6:
        raise ValueError("Mass ledger rows do not reconcile to located material subtotal")
    if abs(residual - float(candidate["mass"]["unlocated_or_reference_account_kg"])) > 1e-6:
        raise ValueError("Mass ledger residual does not reconcile to the reported account remainder")
    if abs(accounted - located - residual) > 1e-6:
        raise ValueError("Accounted, located and residual mass subtotals do not close")

    account_index = {account["account_id"]: account for account in accounts}
    if len(account_index) != len(accounts):
        raise ValueError("Duplicate top-level mass account ID")
    for group in accounts:
        group["account_id"] = group["account_id"]
    accounts.sort(key=lambda account: account["account_id"])
    source_occurrences.sort(key=lambda row: (row["account_id"], row["occurrence_id"]))
    geometry_occurrences.sort(key=lambda row: row["occurrence_id"])
    return dict(
        schema="osr-v06-mass-reconciliation/1",
        candidate_id=candidate["candidate_id"],
        body_candidate_id=candidate["body_candidate_id"],
        support_component_id=candidate["support_component_id"],
        propulsion_component_id=candidate["propulsion_component_id"],
        accounts=accounts,
        source_account_occurrences=source_occurrences,
        candidate_geometry_occurrences=geometry_occurrences,
        summary=dict(
            account_row_count=len(accounts),
            source_account_occurrence_count=len(source_occurrences),
            retained_source_occurrence_count=len(retained),
            located_geometry_occurrence_count=len(geometry),
            accounted_tare_kg_per_car=accounted,
            located_geometry_mass_kg=located,
            residual_reference_or_unlocated_mass_kg=residual,
            located_material_CG_m=candidate["mass"]["located_material_CG_m"],
            located_material_CG_scope="Candidate geometry subtotal only; excludes account residuals and non-solid equipment.",
            complete_installed_mass_kg=None,
            complete_installed_CG_m=None,
            complete_installed_inertia_kg_m2=None,
            axle_reactions=None,
            all_candidate_geometry_occurrences_assigned_once=True,
            all_account_rows_reconciled=True,
        ),
        **FLAGS,
    )


def _readme(ledger, selected):
    summary = ledger["summary"]
    closure = build_closure_worksheet(ledger)["summary"]
    lines = [
        "# v0.6 vehicle mass reconciliation",
        "",
        f"Physical candidate `{ledger['candidate_id']}`; body `{ledger['body_candidate_id']}`; selection `{selected['selection_id']}`.",
        "",
        "This report preserves every retained source-account occurrence in its system account, then assigns each candidate geometry occurrence to one parent account using explicit component-family rules. Inherited source occurrences and current geometry do not have a row-to-row identity join, so the report does not claim one. Newly modelled underframe, bogie, and passive-secondary geometry is assigned once. This is an accounting reconciliation, not a complete installed-mass claim.",
        "",
        "| Ledger result | Value |",
        "|---|---:|",
        f"| Accounted tare | {summary['accounted_tare_kg_per_car']:,.3f} kg/car |",
        f"| Candidate located geometry | {summary['located_geometry_mass_kg']:,.3f} kg/car |",
        f"| Reference or unlocated account residual | {summary['residual_reference_or_unlocated_mass_kg']:,.3f} kg/car |",
        f"| Account rows | {summary['account_row_count']:,} |",
        f"| Located geometry occurrences assigned once | {summary['located_geometry_occurrence_count']:,} |",
        f"| Closure worksheet rows (source / geometry / account) | {closure['record_count']:,} ({closure['source_account_occurrence_count']:,} / {closure['candidate_geometry_occurrence_count']:,} / {summary['account_row_count']:,}) |",
        "| Complete installed mass, CG, inertia, axle reactions | Unknown |",
        "",
        "## Account groups",
        "",
        "| Account group | Accounted kg | Geometry kg | Residual kg | Source occurrences | Geometry occurrences |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for group in ledger["accounts"]:
        lines.append(
            f"| {group['account_id']} | {group['accounted_mass_kg']:,.3f} | {group['located_geometry_mass_kg']:,.3f} | "
            f"{group['residual_account_mass_kg']:,.3f} | {len(group['source_occurrence_ids']):,} | "
            f"{len(group['candidate_geometry_occurrence_ids']):,} |"
        )
    lines.extend([
        "",
        "The located-material centre of gravity is calculated from the represented geometry subset only. It excludes all residual accounts, including the service pack, HVAC, unlocated bogie balance, roof coating takeoff, attachment allowance, and source-account mass without candidate geometry. It is not the installed vehicle CG. Average axle masses are not axle reactions; longitudinal balance and dynamic wheel loads remain unresolved.",
        "",
        "The [mass closure worksheet](mass-closure-worksheet.json.gz) has one row for every retained source-account occurrence, candidate geometry occurrence, and account closure. It keeps source-accounted mass, CAD-derived mass, and account residuals in separate fields. Every row's physically installed mass and installed position remain null; a candidate geometry centroid is not an installed position, and a positive accounting residual is not a physical part.",
        "",
        "Source occurrences keep their source IDs and occurrence-definition IDs in [mass-ledger.json.gz](mass-ledger.json.gz). The report is bound by [manifest.json](manifest.json). Regenerate with `python3 -m engineering.mass_ledger_audit build` and verify with `python3 -m engineering.mass_ledger_audit verify`.",
        "",
        "No physical acceptance, manufacturing release, or operating release is asserted.",
        "",
    ])
    return "\n".join(lines).encode()


def _inputs(root):
    root = Path(root)
    candidate = vehicle.build(root)
    parent, parent_sha = vehicle._read_parent(root)
    selected = evaluation.build(root)
    baseline = tomllib.loads((root / "engineering/development-baseline.toml").read_text())
    expected = {
        "vehicle_candidate_id": candidate["candidate_id"],
        "body_candidate_id": candidate["body_candidate_id"],
        "support_component_id": candidate["support_component_id"],
        "propulsion_component_id": candidate["propulsion_component_id"],
    }
    if any(baseline.get(key) != value for key, value in expected.items()):
        raise ValueError("Vehicle mass ledger does not match the selected development candidate")
    selected_expected = dict(
        candidate_id=candidate["candidate_id"],
        body_candidate_id=candidate["body_candidate_id"],
        support_component_id=candidate["support_component_id"],
        propulsion_component_id=candidate["propulsion_component_id"],
    )
    if any(selected.get(key) != value for key, value in selected_expected.items()):
        raise ValueError("Selected evaluation and vehicle mass ledger identities differ")
    ledger = reconcile(candidate, parent)
    ledger["vehicle_evaluation_id"] = candidate.get("evaluation_id")
    ledger["selected_evaluation_id"] = selected["evaluation_id"]
    ledger["selection_id"] = selected["selection_id"]
    ledger["summary"]["vehicle_evaluation_id"] = candidate.get("evaluation_id")
    ledger["summary"]["selected_evaluation_id"] = selected["evaluation_id"]
    ledger["summary"]["selection_id"] = selected["selection_id"]
    sources = {}
    for source_map in (candidate["source_sha256"], selected["source_sha256"]):
        for name, expected_sha in source_map.items():
            if name in sources and sources[name] != expected_sha:
                raise ValueError("Candidate and selected evaluation source receipts differ: " + name)
            sources[name] = expected_sha
    sources.update({
        "engineering/mass_ledger_audit.py": _digest(Path(__file__)),
        "engineering/development-baseline.toml": _digest(root / "engineering/development-baseline.toml"),
        "engineering/station_rail/evaluation.py": _digest(root / "engineering/station_rail/evaluation.py"),
        "engineering/station_rail/vehicle.py": _digest(root / "engineering/station_rail/vehicle.py"),
        "docs/design-engine/ferrite-maglev/comfort-design/manifest.json": _digest(root / vehicle.PARENT_MANIFEST),
    })
    sources[vehicle.PARENT] = parent_sha
    return ledger, selected, sources


def _payloads(root):
    ledger, selected, sources = _inputs(root)
    worksheet = build_closure_worksheet(ledger)
    ledger_raw = _deterministic_gzip(encoded(ledger))
    summary = dict(schema="osr-v06-mass-reconciliation-summary/1", **ledger["summary"],
                   candidate_id=ledger["candidate_id"], body_candidate_id=ledger["body_candidate_id"],
                   closure_worksheet_id=worksheet["worksheet_id"],
                   closure_worksheet_record_count=worksheet["summary"]["record_count"],
                   closure_worksheet_source_account_occurrence_count=worksheet["summary"]["source_account_occurrence_count"],
                   closure_worksheet_geometry_occurrence_count=worksheet["summary"]["candidate_geometry_occurrence_count"],
                   closure_worksheet_account_residual_count=worksheet["summary"]["account_residual_count"],
                   **FLAGS)
    return {
        "mass-ledger.json.gz": ledger_raw,
        "mass-closure-worksheet.json.gz": _deterministic_gzip(encoded(worksheet)),
        "summary.json": encoded(summary),
        "README.md": _readme(ledger, selected),
    }, sources, ledger, selected


def build_closure_worksheet(ledger):
    """Separate source-account, candidate-geometry, and unresolved installation rows."""
    candidate_id = ledger["candidate_id"]
    evaluation_id = ledger["selected_evaluation_id"]
    selection_id = ledger["selection_id"]
    rows = []
    for source in ledger["source_account_occurrences"]:
        rows.append(_row(
            record_kind="source-account-occurrence",
            candidate_id=candidate_id,
            evaluation_id=evaluation_id,
            selection_id=selection_id,
            account_id=source["account_id"],
            occurrence_id=source["occurrence_id"],
            occurrence_definition_id=source.get("occurrence_definition_id"),
            source_part_id=source.get("source_part_id"),
            mass_evidence_class=source.get("evidence_class"),
            accounted_source_mass_kg=source["mass_kg"],
            candidate_geometry_mass_kg=None,
            candidate_geometry_centroid_m=None,
            physically_installed_mass_kg=None,
            installed_position_m=None,
            lower_mass_bound_kg=None,
            upper_mass_bound_kg=None,
            installation_status="not-physically-verified",
            source_location_known=source.get("source_location_known"),
            overlap_or_replacement_status="unresolved",
            accounting_mapping="source occurrence retained in its parent system account; no row-to-row match with candidate geometry is claimed",
            evidence_needed=[
                "supplier or measurement evidence for installed mass",
                "reviewed installation location in the candidate vehicle coordinate frame",
                "identity-level overlap, replacement, and shared-membership review",
            ],
        ))
    for geometry in ledger["candidate_geometry_occurrences"]:
        rows.append(_row(
            record_kind="candidate-geometry-occurrence",
            candidate_id=candidate_id,
            evaluation_id=evaluation_id,
            selection_id=selection_id,
            account_id=geometry["account_id"],
            occurrence_id=geometry["occurrence_id"],
            occurrence_definition_id=None,
            source_part_id=None,
            mass_evidence_class="candidate-geometry-derived",
            accounted_source_mass_kg=None,
            candidate_geometry_mass_kg=geometry["mass_kg"],
            candidate_geometry_centroid_m=geometry.get("cg_m"),
            physically_installed_mass_kg=None,
            installed_position_m=None,
            lower_mass_bound_kg=None,
            upper_mass_bound_kg=None,
            installation_status="not-physically-verified",
            source_location_known=False,
            overlap_or_replacement_status="unresolved",
            accounting_mapping=geometry["mapping_method"],
            evidence_needed=[
                "manufactured-part weigh record or supplier-documented mass",
                "confirmation that the candidate geometry is installed as modelled",
                "reviewed installation location, overlap, and replacement mapping",
            ],
        ))
    for account in ledger["accounts"]:
        residual = float(account["residual_account_mass_kg"])
        rows.append(_row(
            record_kind="account-closure",
            candidate_id=candidate_id,
            evaluation_id=evaluation_id,
            selection_id=selection_id,
            account_id=account["account_id"],
            occurrence_id=None,
            occurrence_definition_id=None,
            source_part_id=None,
            mass_evidence_class=("accounting-residual-not-physical-component"
                                 if residual > 1e-9 else "accounting-subtotal-reconciled-to-candidate-geometry"),
            accounted_source_mass_kg=account["accounted_mass_kg"],
            candidate_geometry_mass_kg=account["located_geometry_mass_kg"],
            candidate_geometry_centroid_m=None,
            accounting_residual_kg=residual,
            physically_installed_mass_kg=None,
            installed_position_m=None,
            lower_mass_bound_kg=None,
            upper_mass_bound_kg=None,
            installation_status="not-physically-verified",
            source_location_known=False,
            overlap_or_replacement_status="unresolved",
            source_occurrence_ids=list(account["source_occurrence_ids"]),
            candidate_geometry_occurrence_ids=list(account["candidate_geometry_occurrence_ids"]),
            accounting_mapping=account["mapping_method"],
            evidence_needed=[
                "disaggregate the account into exact physical component identities",
                "supplier or measurement evidence for installed mass",
                "reviewed installation location in the candidate vehicle coordinate frame",
                "identity-level overlap, replacement, and shared-membership review",
            ],
        ))
    record_ids = [row["row_id"] for row in rows]
    if len(record_ids) != len(set(record_ids)):
        raise ValueError("Mass closure worksheet record identities must be unique")
    if (len(rows) != (len(ledger["source_account_occurrences"])
                      + len(ledger["candidate_geometry_occurrences"])
                      + len(ledger["accounts"]))
            or any(row["physically_installed_mass_kg"] is not None for row in rows)):
        raise ValueError("Mass closure worksheet lost an account/occurrence or inferred installed mass")
    body = dict(
        schema="osr-v06-mass-closure-worksheet/1",
        candidate_id=candidate_id,
        body_candidate_id=ledger["body_candidate_id"],
        support_component_id=ledger["support_component_id"],
        propulsion_component_id=ledger["propulsion_component_id"],
        evaluation_id=evaluation_id,
        vehicle_evaluation_id=ledger["vehicle_evaluation_id"],
        selection_id=selection_id,
        ledger_payload_id=identity(ledger),
        rows=rows,
        summary=dict(
            record_count=len(rows),
            source_account_occurrence_count=len(ledger["source_account_occurrences"]),
            candidate_geometry_occurrence_count=len(ledger["candidate_geometry_occurrences"]),
            account_residual_count=sum(float(row["accounting_residual_kg"]) > 1e-9 for row in rows
                                       if row["record_kind"] == "account-closure"),
            accounted_tare_kg_per_car=ledger["summary"]["accounted_tare_kg_per_car"],
            located_geometry_mass_kg=ledger["summary"]["located_geometry_mass_kg"],
            accounting_residual_kg=ledger["summary"]["residual_reference_or_unlocated_mass_kg"],
            physically_installed_mass_kg=None,
            complete_installed_mass_kg=None,
            complete_installed_CG_m=None,
            complete_installed_inertia_kg_m2=None,
            axle_reactions=None,
        ),
        unknown_is_zero=False,
        physical_acceptance=None,
        **FLAGS,
    )
    body["worksheet_id"] = identity(body)
    return body


def publish(root=ROOT, output=None):
    root = Path(root).resolve()
    output = root / OUTPUT if output is None else Path(output)
    payloads, sources, ledger, selected = _payloads(root)
    output.mkdir(parents=True, exist_ok=True)
    for name, raw in payloads.items():
        path = output / name
        tmp = path.with_name(path.name + ".tmp")
        tmp.write_bytes(raw)
        os.replace(tmp, path)
    manifest = dict(
        schema="osr-v06-mass-reconciliation-publication/1",
        candidate_id=ledger["candidate_id"],
        evaluation_id=selected["evaluation_id"],
        vehicle_evaluation_id=ledger["vehicle_evaluation_id"],
        selection_id=selected["selection_id"],
        source_sha256=sources,
        files_sha256={name: sha256(raw).hexdigest() for name, raw in payloads.items()},
        **FLAGS,
    )
    manifest["manifest_id"] = identity(manifest)
    raw = encoded(manifest)
    tmp = output / "manifest.json.tmp"
    tmp.write_bytes(raw)
    os.replace(tmp, output / "manifest.json")
    return dict(published=True, path=str(output), manifest_id=manifest["manifest_id"],
                account_row_count=ledger["summary"]["account_row_count"],
                closure_worksheet_id=build_closure_worksheet(ledger)["worksheet_id"],
                closure_worksheet_record_count=len(ledger["source_account_occurrences"])
                    + len(ledger["candidate_geometry_occurrences"]) + len(ledger["accounts"]),
                accounted_tare_kg_per_car=ledger["summary"]["accounted_tare_kg_per_car"],
                located_geometry_mass_kg=ledger["summary"]["located_geometry_mass_kg"],
                residual_reference_or_unlocated_mass_kg=ledger["summary"]["residual_reference_or_unlocated_mass_kg"],
                complete_installed_mass_kg=None, **FLAGS)


def verify(root=ROOT, output=None):
    root = Path(root).resolve()
    output = root / OUTPUT if output is None else Path(output)
    manifest_path = output / "manifest.json"
    manifest = json.loads(manifest_path.read_bytes())
    if manifest.get("manifest_id") != identity({key: value for key, value in manifest.items() if key != "manifest_id"}):
        raise ValueError("Mass reconciliation manifest identity differs")
    for name, expected in manifest["source_sha256"].items():
        if _digest(root / name) != expected:
            raise ValueError("Mass reconciliation source differs: " + name)
    payloads, sources, ledger, selected = _payloads(root)
    if manifest["source_sha256"] != sources:
        raise ValueError("Mass reconciliation source set differs")
    if (manifest["candidate_id"] != ledger["candidate_id"]
            or manifest["evaluation_id"] != selected["evaluation_id"]
            or manifest["vehicle_evaluation_id"] != ledger["vehicle_evaluation_id"]
            or manifest["selection_id"] != selected["selection_id"]):
        raise ValueError("Mass reconciliation candidate or evaluation identity differs")
    actual_files = {path.name: _digest(path) for path in output.iterdir() if path.is_file() and path.name != "manifest.json"}
    expected_files = {name: sha256(raw).hexdigest() for name, raw in payloads.items()}
    if manifest["files_sha256"] != expected_files or actual_files != expected_files:
        raise ValueError("Mass reconciliation payload differs")
    for name, raw in payloads.items():
        if (output / name).read_bytes() != raw:
            raise ValueError("Mass reconciliation generated output differs: " + name)
    if any(manifest.get(key) is not value for key, value in FLAGS.items()):
        raise ValueError("Mass reconciliation cannot grant release")
    return dict(verified=True, replayed=True, manifest_id=manifest["manifest_id"],
                candidate_id=ledger["candidate_id"], evaluation_id=selected["evaluation_id"],
                selection_id=selected["selection_id"], account_row_count=ledger["summary"]["account_row_count"],
                closure_worksheet_id=build_closure_worksheet(ledger)["worksheet_id"],
                closure_worksheet_record_count=len(ledger["source_account_occurrences"])
                    + len(ledger["candidate_geometry_occurrences"]) + len(ledger["accounts"]),
                accounted_tare_kg_per_car=ledger["summary"]["accounted_tare_kg_per_car"],
                located_geometry_mass_kg=ledger["summary"]["located_geometry_mass_kg"],
                residual_reference_or_unlocated_mass_kg=ledger["summary"]["residual_reference_or_unlocated_mass_kg"],
                complete_installed_mass_kg=None, **FLAGS)


def main(argv=None):
    parser = argparse.ArgumentParser(prog="python3 -m engineering.mass_ledger_audit")
    parser.add_argument("action", choices=("build", "verify"))
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    result = publish(args.root, args.output) if args.action == "build" else verify(args.root, args.output)
    print(json.dumps(result, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
