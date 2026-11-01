"""Deterministic, non-submittable factory plan for a verified v0.6 proposal.

The plan reuses the selected vehicle's Class C cost ledger. It converts only
the ledger's existing process-hour proxies into a serialized two-shift factory
work plan and explicit aggregate staffing sensitivities. No measured capacity,
ERPNext record or engineering release follows from these planning assumptions.
"""
from __future__ import annotations

from copy import deepcopy
import json
import math
from pathlib import Path
import shutil
import tempfile

from engineering.station_rail.common import digest, encoded, identity
from . import FLAGS, OUTPUT, ROOT
from . import entrypoint, planning

SCHEMA = "osr-v06-factory-work-package-draft/1"
MANIFEST_SCHEMA = "osr-v06-factory-work-package-manifest/1"
PAYLOAD_NAME = "factory-work-package.json"
CASES = ("low", "base", "high")
IDS = ("selection_id", "candidate_id", "body_candidate_id",
       "support_component_id", "propulsion_component_id")
PRODUCER_PATHS = (
    "engineering/development_baseline/factory_draft.py",
    "engineering/development_baseline/planning.py",
    "engineering/development_baseline/entrypoint.py",
    "engineering/development_baseline/vehicle_cost.py",
)


class FactoryDraftError(ValueError):
    """Missing, changed, or incompatible factory draft evidence."""


def _safe_file(root, relative):
    try:
        return planning._safe_file(root, relative)
    except (OSError, ValueError) as error:
        raise FactoryDraftError(str(error)) from error


def _safe_output(root, path):
    try:
        return planning._safe_output_dir(root, path)
    except (OSError, ValueError) as error:
        raise FactoryDraftError(str(error)) from error


def _read_json(path, maximum=planning.MAX_PLAN_BYTES):
    try:
        return planning._read_json(path, maximum=maximum)
    except (OSError, ValueError) as error:
        raise FactoryDraftError(str(error)) from error


def _add_source(sources, name, expected, root):
    if not isinstance(name, str) or not isinstance(expected, str) or len(expected) != 64:
        raise FactoryDraftError("Source paths and SHA-256 values are required")
    path = _safe_file(root, name)
    actual = digest(path)
    if actual != expected:
        raise FactoryDraftError("Source hash differs: " + name)
    previous = sources.get(name)
    if previous is not None and previous != actual:
        raise FactoryDraftError("Conflicting source bindings: " + name)
    sources[name] = actual


def _scenario(value, label):
    if not isinstance(value, dict) or set(value) != set(CASES):
        raise FactoryDraftError(label + " requires low/base/high values")
    result = {}
    for case in CASES:
        number = value[case]
        if isinstance(number, bool) or not isinstance(number, (int, float)):
            raise FactoryDraftError(label + " values must be finite numbers")
        number = float(number)
        if not math.isfinite(number) or number < 0:
            raise FactoryDraftError(label + " values must be finite and nonnegative")
        result[case] = number
    if not result["low"] <= result["base"] <= result["high"]:
        raise FactoryDraftError(label + " low/base/high order differs")
    return result


def _line_hours(line, cars):
    stage = line.get("stage")
    quantity = line.get("quantity")
    if not isinstance(quantity, dict):
        raise FactoryDraftError("Cost ledger line has no quantity record")
    if stage == "factory-gate":
        per_car = _scenario(dict(zip(CASES, quantity.get("process_hours_per_car", []))),
                             "Per-car process hours")
        return {case: per_car[case] * cars for case in CASES}, "per-car process-hour proxy × six cars"
    if stage == "factory-gate-equipment-allowance":
        hours = _scenario(dict(zip(CASES, quantity.get("process_hours_per_train", []))),
                          "Equipment-allowance process hours")
        return hours, "per-train equipment process-hour proxy"
    if stage == "final-assembly":
        per_car = _scenario(dict(zip(CASES, quantity.get("labour_hours_per_car", []))),
                             "Final-assembly labour hours")
        return {case: per_car[case] * cars for case in CASES}, "per-car final-assembly hours × six cars"
    raise FactoryDraftError("Unsupported factory cost stage: " + str(stage))


def _validate_cost(cost, candidate):
    if not isinstance(cost, dict) or cost.get("schema") != "osr-v06-selected-vehicle-class-c-cost/1":
        raise FactoryDraftError("Selected Class C vehicle cost record required")
    for key in IDS:
        if cost.get(key) != candidate.get(key):
            raise FactoryDraftError("Cost record uses a different " + key)
    if cost.get("evaluation_id") != candidate.get("evaluation_id"):
        raise FactoryDraftError("Cost record uses a different candidate evaluation")
    if cost.get("development_default") is not True or cost.get("estimate_class") != "C":
        raise FactoryDraftError("A provisional Class C estimate for the selected development candidate is required")
    if cost.get("currency") != "IQD" or not isinstance(cost.get("cost_estimate_id"), str):
        raise FactoryDraftError("Selected vehicle cost identity or currency differs")
    if identity({key: value for key, value in cost.items() if key != "cost_estimate_id"}) != cost["cost_estimate_id"]:
        raise FactoryDraftError("Selected vehicle cost identity is stale")
    if any(cost.get(key) is not False for key in FLAGS):
        raise FactoryDraftError("Cost input cannot grant an engineering or operating disposition")
    cars = cost.get("vehicle_account", {}).get("cars_per_train")
    if cars != 6:
        raise FactoryDraftError("The current factory plan requires the selected six-car formation")
    shift = cost.get("shifts", {}).get("production_per_day", {})
    util = cost.get("assumption_values", {}).get("productive_utilisation")
    if (shift.get("shifts") != 2 or shift.get("hours_per_shift") != 8
            or isinstance(util, bool) or not isinstance(util, (int, float))
            or not math.isfinite(float(util)) or not 0 < float(util) <= 1
            or abs(float(shift.get("productive_hours_per_day", -1)) - 16 * float(util)) > 1e-8):
        raise FactoryDraftError("Declared two × eight-hour production shift basis required")
    civil = cost.get("shifts", {}).get("civil_per_day", {})
    operations = cost.get("shifts", {}).get("operations_cases", [])
    if civil != {"shifts": 2, "hours_per_shift": 8}:
        raise FactoryDraftError("Declared two × eight-hour civil shift assumption required")
    expected_operations = [
        {"hours_per_day": 16, "shifts_per_day": 2, "hours_per_shift": 8},
        {"hours_per_day": 18, "shifts_per_day": 2, "hours_per_shift": 9},
        {"hours_per_day": 24, "shifts_per_day": 3, "hours_per_shift": 8},
    ]
    if operations != expected_operations:
        raise FactoryDraftError("Declared two/three-shift railway operations cases required")
    if cost.get("source_sha256") is None or not isinstance(cost["source_sha256"], dict):
        raise FactoryDraftError("Source-bound selected vehicle cost ledger required")
    for name, value in cost["source_sha256"].items():
        if not isinstance(name, str) or not isinstance(value, str) or len(value) != 64:
            raise FactoryDraftError("Invalid vehicle-cost source binding")
    lines = cost.get("lines")
    if not isinstance(lines, list) or not lines:
        raise FactoryDraftError("Selected vehicle cost ledger lines are required")
    return cars, float(util), lines


def resource_envelope(work_packages, candidate, cost_estimate_id, utilisation):
    """Calculate declared labour-capacity scenarios, without inferring a factory.

    A process hour is treated as one person-hour only in this planning sensitivity.
    Every person covers one eight-hour shift; the second shift requires a second
    set of staffed positions. Process families are accounting groups, not proved
    workstations, competencies, concurrent operations or supplier capacity.
    """
    if (not work_packages or not isinstance(cost_estimate_id, str) or len(cost_estimate_id) != 64
            or isinstance(utilisation, bool) or not isinstance(utilisation, (int, float))
            or not math.isfinite(utilisation) or not 0 < utilisation <= 1):
        raise FactoryDraftError("Source-linked work packages and productive utilisation required")
    if any(not isinstance(candidate.get(key), str) or len(candidate[key]) != 64
           for key in (*IDS, "evaluation_id")):
        raise FactoryDraftError("Resource envelope requires exact candidate, selection and evaluation identities")
    projection = []
    seen = set()
    groups = {}
    for row in work_packages:
        line_id = row.get("line_id")
        process = row.get("process_template")
        if (not isinstance(line_id, str) or len(line_id) != 64 or line_id in seen
                or not isinstance(process, str) or not process):
            raise FactoryDraftError("Unique source cost lines and declared process templates required")
        seen.add(line_id)
        hours = _scenario(row.get("process_hours_per_train"), "Resource work-package hours")
        source = dict(line_id=line_id, line_key=row.get("line_key"),
            process_template=process, process_hours_per_train=hours,
            occurrence_ids=deepcopy(row.get("occurrence_ids", [])),
            source_ids=deepcopy(row.get("source_ids", [])))
        projection.append(source)
        groups.setdefault(process, []).append(source)
    totals = {case: sum(row["process_hours_per_train"][case] for row in projection) for case in CASES}
    assumptions = dict(schema="osr-provisional-factory-resource-assumptions/1",
        batch_trainsets=[1, 6, 12], horizon_workdays=[60, 125, 250],
        shifts_per_day=2, hours_per_shift=8, productive_utilisation=float(utilisation),
        person_hours_per_process_hour_hypothesis=1.0,
        worker_shift_coverage="One eight-hour shift per person per workday; two distinct sets of staffed positions for two shifts",
        material_availability="Conditional after required inputs are available; procurement lead times and arrival dates remain unknown",
        calendar_basis="Working days only; no dates, holidays or weekend calendar inferred")
    assumptions["assumption_id"] = identity(assumptions)
    per_worker_day = 8 * float(utilisation)
    per_lane_day = 2 * per_worker_day
    families = [dict(process_family_id=identity(process), process_template=process,
        cost_line_ids=sorted(row["line_id"] for row in rows),
        process_hours_per_train={case: round(sum(row["process_hours_per_train"][case]
            for row in rows), 6) for case in CASES}) for process, rows in sorted(groups.items())]
    scenarios = []
    for trains in assumptions["batch_trainsets"]:
        for days in assumptions["horizon_workdays"]:
            for case in CASES:
                demand = totals[case] * trains
                equal_shift_positions = demand / (days * per_lane_day)
                positions = math.ceil(equal_shift_positions)
                family_rows = []
                for family in families:
                    family_hours = family["process_hours_per_train"][case] * trains
                    family_rows.append(dict(process_family_id=family["process_family_id"],
                        required_person_hours_hypothesis=round(family_hours, 6),
                        pooled_positions_per_shift_unrounded=family_hours / (days * per_lane_day),
                        separately_staffed_positions_per_shift=math.ceil(family_hours / (days * per_lane_day))))
                scenarios.append(dict(batch_trainsets=trains, horizon_workdays=days,
                    process_hour_case=case, required_person_hours_hypothesis=round(demand, 6),
                    productive_hours_per_worker_shift_day=per_worker_day,
                    productive_hours_per_equal_two_shift_lane_day=per_lane_day,
                    pooled_positions_per_shift_unrounded=equal_shift_positions,
                    pooled_positions_per_shift_rounded_up=positions,
                    total_positions_across_two_shifts_excluding_relief=2 * positions,
                    pooled_productive_capacity_person_hours=positions * days * per_lane_day,
                    separately_staffed_process_family_positions_per_shift=sum(
                        row["separately_staffed_positions_per_shift"] for row in family_rows),
                    process_families=family_rows,
                    physical_workstations_required=None, verified_throughput_trainsets_per_year=None,
                    actual_headcount_including_relief=None, calendar_completion_date=None))
    value = dict(schema="osr-v06-provisional-factory-resource-envelope/1",
        **{key: candidate[key] for key in (*IDS, "evaluation_id")},
        cost_estimate_id=cost_estimate_id, package_projection_id=identity(projection),
        source_cost_line_ids=sorted(seen), source_package_count=len(projection),
        source_package_projection=projection, assumptions=assumptions,
        process_hours_per_train={case: round(totals[case], 6) for case in CASES},
        process_families=families, scenarios=scenarios,
        scenario_count=len(scenarios), actual_factory_capacity_verified=False,
        measured_process_hours=False, staffing_approved=False,
        physical_operation_inventory_complete=False, accounting_overlap_resolved=False,
        accounting_scope="Each source cost package counted once, with no additional hours or overlap credit. Physical account membership and process overlap remain unresolved in the input ledger.",
        scope="Aggregate Class C workforce/capacity sensitivity only. Pooled staffing is an arithmetic lower bound with perfect skill/resource interchangeability; separate-family figures assume dedicated staffing, not proven parallel production.",
        external_holds=["Measured person/machine/cure times and process-hour interpretation",
            "Crew competency, skill mix, supervision, relief and shift roster",
            "Physical workstations, tools, machine cycles and safe parallel working",
            "Assembly precedence, curing/storage space, QA capacity and rework",
            "Procurement lead times, input arrival dates and site calendar"], **FLAGS)
    value["resource_envelope_id"] = identity(value)
    return value


def _build_work_packages(cost, candidate, planning_revision):
    cars, utilisation, lines = _validate_cost(cost, candidate)
    included = []
    excluded = []
    for line in lines:
        if not isinstance(line, dict):
            raise FactoryDraftError("Invalid selected vehicle cost line")
        stage = line.get("stage")
        if stage == "reference-delivery":
            excluded.append(dict(line_id=line.get("line_id"), line_key=line.get("line_key"),
                                 reason="Factory plan excludes transport and installation beyond final vehicle assembly"))
            continue
        if stage not in ("factory-gate", "factory-gate-equipment-allowance", "final-assembly"):
            raise FactoryDraftError("Unexpected cost line in selected vehicle ledger: " + str(stage))
        if line.get("candidate_id") != candidate["candidate_id"] or line.get("estimate_class") != "C":
            raise FactoryDraftError("Cost line uses a different candidate or estimate class")
        line_identity = line.get("line_id")
        if not isinstance(line_identity, str) or identity({key: value for key, value in line.items() if key != "line_id"}) != line_identity:
            raise FactoryDraftError("Selected vehicle cost line identity is stale")
        hours, hours_basis = _line_hours(line, cars)
        cost_values = _scenario(line.get("cost_iqd"), "Cost ledger line cost")
        components = line.get("components_iqd")
        if components is not None:
            if not isinstance(components, dict):
                raise FactoryDraftError("Cost components must be an object or explicitly unknown")
            components = {name: _scenario(value, "Cost component " + str(name))
                          for name, value in sorted(components.items())}
            for case in CASES:
                if abs(sum(value[case] for value in components.values()) - cost_values[case]) > 2.0:
                    raise FactoryDraftError("Cost component rollup differs from the cost line")
        included.append((stage, line.get("line_key", ""), line, hours, hours_basis, cost_values, components))

    stage_order = {"factory-gate": 0, "factory-gate-equipment-allowance": 1, "final-assembly": 2}
    included.sort(key=lambda row: (stage_order[row[0]], str(row[1]), row[2]["line_id"]))
    if not included:
        raise FactoryDraftError("No factory production work packages could be derived")

    productive_hours_per_day = 16 * utilisation
    cumulative = {case: 0.0 for case in CASES}
    work_packages = []
    for number, (stage, line_key, line, hours, hours_basis, costs, components) in enumerate(included, 1):
        operation_id = "OSR-FW-%03d-%s" % (number, line["line_id"][:10])
        start = dict(cumulative)
        duration = {case: hours[case] / productive_hours_per_day for case in CASES}
        finish = {case: start[case] + duration[case] for case in CASES}
        cumulative = finish
        kind = {
            "factory-gate": "located-material-family-process",
            "factory-gate-equipment-allowance": "bounded-unlocated-equipment-allowance",
            "final-assembly": "six-car-final-assembly",
        }[stage]
        work_packages.append(dict(
            operation_id=operation_id,
            predecessor_ids=[] if number == 1 else [work_packages[-1]["operation_id"]],
            sequence=number,
            kind=kind,
            line_id=line["line_id"],
            line_key=line_key,
            process_template=line.get("process_template"),
            quantity=deepcopy(line.get("quantity")),
            process_hours_per_train={case: round(hours[case], 6) for case in CASES},
            process_hours_basis=hours_basis,
            duration_productive_workdays={case: round(duration[case], 6) for case in CASES},
            planned_start_workday={case: round(start[case], 6) for case in CASES},
            planned_finish_workday={case: round(finish[case], 6) for case in CASES},
            cost_iqd_per_train={case: round(costs[case], 2) for case in CASES},
            cost_components_iqd_per_train=components,
            currency="IQD",
            estimate_class="C",
            rate_evidence_class=line.get("rate_evidence_class"),
            source_ids=deepcopy(line.get("source_ids", [])),
            occurrence_ids=deepcopy(line.get("occurrence_ids", [])),
            basis=line.get("calculation_basis"),
            engineering_process_qualified=False,
        ))

    expected = cost.get("factory_gate_cost_iqd_per_train", {})
    assembly = cost.get("final_vehicle_assembly_cost_iqd_per_train", {})
    totals = {case: round(expected.get(case, 0) + assembly.get(case, 0), 2) for case in CASES}
    actual = {case: round(sum(row["cost_iqd_per_train"][case] for row in work_packages), 2) for case in CASES}
    if any(abs(actual[case] - totals[case]) > 2.0 for case in CASES):
        raise FactoryDraftError("Factory work-package costs do not reconcile to the selected cost ledger")

    return dict(
        cars_per_train=cars,
        currency="IQD",
        estimate_class="C",
        cost_estimate_id=cost["cost_estimate_id"],
        cost_assumptions_id=cost["assumptions_id"],
        estimate_date=cost.get("estimate_date"),
        production_shifts=dict(
            shifts_per_day=2,
            hours_per_shift=8,
            productive_utilisation=utilisation,
            productive_hours_per_day=round(productive_hours_per_day, 6),
            source="Selected vehicle Class C cost assumptions",
        ),
        deferred_shift_assumptions=dict(
            civil=dict(cost["shifts"]["civil_per_day"], state="held", schedule_costed=False),
            railway_operations_cases=[dict(row, state="held", schedule_costed=False)
                                      for row in cost["shifts"]["operations_cases"]],
            reason="These shift cases are preserved for later civil and whole-railway operating plans; this package costs and schedules factory production only.",
        ),
        schedule_basis=("One serialized planning lane; ledger process hours divided by two 8-hour shifts/day and the declared productive utilisation. "
                        "No crew count, parallel-cell capacity, calendar dates, or factory capacity is inferred."),
        schedule_unit="productive workday from a hypothetical factory start; not a calendar commitment",
        total_process_hours_per_train={case: round(sum(row["process_hours_per_train"][case] for row in work_packages), 6)
                                       for case in CASES},
        serialized_factory_duration_productive_workdays={case: round(cumulative[case], 6) for case in CASES},
        factory_and_final_assembly_cost_iqd_per_train=totals,
        separate_unamortized_factory_tooling_capital_iqd=deepcopy(
            cost.get("separate_unamortized_factory_tooling_capital_iqd")),
        work_packages=work_packages,
        provisional_resource_envelope=resource_envelope(work_packages, candidate,
            cost["cost_estimate_id"], utilisation),
        excluded_cost_lines=excluded,
        inventory_disposition=dict(
            accounted_tare_kg_per_car=cost["vehicle_account"]["accounted_tare_kg_per_car"],
            located_geometry_kg_per_car=cost["vehicle_account"]["located_geometry_kg_per_car"],
            residual_account_kg_per_car=cost["vehicle_account"]["residual_account_kg_per_car"],
            complete_installed_mass=False,
            residual_equipment_allowances_remain_unlocated=True,
        ),
        planning_revision=dict(
            city=planning_revision["city"],
            planning_revision_id=planning_revision["planning_revision_id"],
            network_proposal_id=planning_revision["network_proposal_id"],
            selected_for_development=False,
        ),
    )


def _held_scopes():
    reasons = {
        "procurement": "Quantities beyond the selected vehicle cost ledger are not a purchasing BOM; no supplier items or orders are created.",
        "civil_and_site_schedule": "Route-specific spans, foundations, access, ground conditions, crew resources and work durations remain unmodelled.",
        "supplier_orders": "No supplier, quote, currency, lead time, availability or order approval is inferred.",
        "staffing": "Aggregate staffing sensitivities are planning hypotheses only; actual crew size, skill mix, relief, individual rosters, payroll and HR records remain unknown.",
        "railway_operations": "Service, fleet, energy, operations, maintenance and three-shift operating costs remain outside this factory plan.",
        "erpnext_admission": "The package is a local draft only; no ERPNext import or document creation is supported.",
        "manufacturing_release": "Provisional cost/process estimates are not approved production instructions.",
        "engineering_acceptance": "Analytical design evidence and assumptions remain distinct from engineering acceptance.",
        "physical_acceptance": "No authenticated physical test or independent review is carried by this package.",
        "operating_release": "No operating release or movement authority is created.",
    }
    return {key: dict(state="held", reason=value) for key, value in reasons.items()}


def _load_inputs(root, handoff_directory):
    root = Path(root).resolve()
    handoff = _safe_output(root, handoff_directory)
    baseline = entrypoint.selected(root)
    current_summary, publication = entrypoint.read_packet(root)
    if identity({key: value for key, value in publication.items() if key != "manifest_id"}) != publication.get("manifest_id"):
        raise FactoryDraftError("Current selected publication manifest identity is stale")
    try:
        verified = planning.verify_handoff(handoff, root=root, baseline=baseline,
                                           current_summary=current_summary)
    except (OSError, ValueError, KeyError) as error:
        raise FactoryDraftError("Planning revision is not current and verified: " + str(error)) from error
    if verified.get("verified") is not True:
        raise FactoryDraftError("Verified planning revision required")
    candidate = {key: baseline[key] if key == "selection_id" else baseline["vehicle"][key]
                 for key in IDS}
    candidate["evaluation_id"] = current_summary.get("evaluation_id")
    if verified.get("selection_id") != candidate["selection_id"]:
        raise FactoryDraftError("Planning handoff uses a different selected selection")
    for key in IDS[1:]:
        if verified.get("physical_candidate", {}).get(key) != candidate[key]:
            raise FactoryDraftError("Planning handoff uses a different selected " + key)
    revision_path = _safe_file(root, handoff.relative_to(root) / "planning-revision.json")
    revision = _read_json(revision_path)
    handoff_payload_path = _safe_file(root, handoff.relative_to(root) / "planning-handoff.json")
    handoff_payload = _read_json(handoff_payload_path)
    planning_manifest_path = _safe_file(root, handoff.relative_to(root) / "manifest.json")
    planning_manifest = _read_json(planning_manifest_path)
    if revision.get("planning_revision_id") != verified.get("planning_revision_id"):
        raise FactoryDraftError("Verified planning revision identity differs")
    if (revision.get("selection_id") != candidate["selection_id"]
            or revision.get("selected_candidate") != {key: candidate[key] for key in IDS[1:]}
            or revision.get("selected_for_development") is not False):
        raise FactoryDraftError("Planning revision is not bound to this selected candidate")
    if handoff_payload.get("base_candidate_evaluation_id") != current_summary.get("evaluation_id"):
        raise FactoryDraftError("Planning revision uses a different selected evaluation")
    if planning_manifest.get("planning_revision_id") != revision.get("planning_revision_id"):
        raise FactoryDraftError("Planning package manifest and revision differ")

    current_directory = _safe_file(root, Path(OUTPUT) / "exports/manifest.json")
    delivery_manifest_path = current_directory
    delivery_manifest = _read_json(delivery_manifest_path)
    delivery_rel = delivery_manifest_path.relative_to(root).as_posix()
    if publication.get("files_sha256", {}).get("exports/manifest.json") != digest(delivery_manifest_path):
        raise FactoryDraftError("Selected delivery manifest is not bound to the current publication")
    for key in (*IDS, "evaluation_id"):
        expected = candidate.get(key) if key != "evaluation_id" else current_summary.get("evaluation_id")
        if delivery_manifest.get(key) != expected:
            raise FactoryDraftError("Selected delivery manifest uses a different " + key)
    if identity({key: value for key, value in delivery_manifest.items() if key != "manifest_id"}) != delivery_manifest.get("manifest_id"):
        raise FactoryDraftError("Selected delivery manifest identity is stale")
    if any(delivery_manifest.get(key) is not value for key, value in FLAGS.items()):
        raise FactoryDraftError("Selected delivery manifest cannot grant acceptance")
    for name, expected in delivery_manifest.get("files_sha256", {}).items():
        actual = digest(_safe_file(root, Path(OUTPUT) / "exports" / name))
        if actual != expected:
            raise FactoryDraftError("Selected delivery payload changed: " + name)

    cost_path = _safe_file(root, Path(OUTPUT) / "exports/selected-vehicle-cost.json")
    cost = _read_json(cost_path)
    if delivery_manifest.get("files_sha256", {}).get(cost_path.name) != digest(cost_path):
        raise FactoryDraftError("Selected cost ledger is not bound to the selected delivery manifest")
    _validate_cost(cost, candidate)
    if cost.get("evaluation_id") != current_summary.get("evaluation_id"):
        raise FactoryDraftError("Selected cost ledger uses a different engineering evaluation")

    sources = {}
    for name in PRODUCER_PATHS:
        _add_source(sources, name, digest(_safe_file(root, name)), root)
    _add_source(sources, "docs/design-engine/current/manifest.json",
                digest(_safe_file(root, "docs/design-engine/current/manifest.json")), root)
    _add_source(sources, delivery_rel, digest(delivery_manifest_path), root)
    _add_source(sources, cost_path.relative_to(root).as_posix(), digest(cost_path), root)
    for mapping in (delivery_manifest.get("source_sha256", {}), cost.get("source_sha256", {}),
                    planning_manifest.get("source_sha256", {})):
        if not isinstance(mapping, dict):
            raise FactoryDraftError("Source-bound delivery and planning manifests required")
        for name, expected in mapping.items():
            _add_source(sources, name, expected, root)
    for name, expected in planning_manifest.get("files_sha256", {}).items():
        _add_source(sources, (handoff.relative_to(root) / name).as_posix(), expected, root)
    _add_source(sources, (handoff.relative_to(root) / "manifest.json").as_posix(),
                digest(planning_manifest_path), root)
    _add_source(sources, (handoff.relative_to(root) / "planning-revision.json").as_posix(),
                digest(revision_path), root)
    return dict(root=root, baseline=baseline, current_summary=current_summary,
                publication=publication, candidate=candidate, delivery_manifest=delivery_manifest,
                cost=cost, planning_revision=revision, planning_manifest=planning_manifest,
                planning_handoff=handoff_payload, planning_verification=verified,
                handoff=handoff, source_sha256=dict(sorted(sources.items())))


def _compile_payload(inputs):
    candidate = inputs["candidate"]
    cost = inputs["cost"]
    revision = inputs["planning_revision"]
    verification = inputs["planning_verification"]
    if verification.get("evaluation_id") != planning.digest_json(dict(
        selection_id=candidate["selection_id"],
        candidate={key: candidate[key] for key in IDS[1:]},
        v06_evaluation_id=inputs["current_summary"]["evaluation_id"],
        network_proposal_id=revision["network_proposal_id"],
    )):
        raise FactoryDraftError("Planning evaluation identity does not match the selected candidate and revision")
    plan = _build_work_packages(cost, candidate, revision)
    value = dict(
        schema=SCHEMA,
        execution="completed-provisional-factory-plan",
        purpose="Research and factory work-package estimation only",
        development_default=True,
        physical_candidate={key: candidate[key] for key in IDS[1:]},
        selection_id=candidate["selection_id"],
        candidate_evaluation_id=inputs["current_summary"]["evaluation_id"],
        selection_purpose=inputs["baseline"].get("selection", {}).get("purpose",
            "Selected v0.6 development reference; not a physical acceptance"),
        selected_delivery_manifest_id=inputs["delivery_manifest"]["manifest_id"],
        planning_evaluation_id=verification["evaluation_id"],
        planning_revision_id=revision["planning_revision_id"],
        planning_network_proposal_id=revision["network_proposal_id"],
        planning_city=revision["city"],
        planning_revision=deepcopy(revision),
        factory_plan=plan,
        held_scopes=_held_scopes(),
        import_policy=dict(submittable=False, erpnext_admitted=False,
            mutation_performed=False, movement_authority=False,
            note="This immutable export is not an ERPNext import package."),
        **FLAGS,
    )
    value["factory_draft_id"] = identity(value)
    return value


def _package_manifest(inputs, payload_raw):
    candidate = inputs["candidate"]
    manifest = dict(
        schema=MANIFEST_SCHEMA,
        factory_draft_id=json.loads(payload_raw)["factory_draft_id"],
        selection_id=candidate["selection_id"],
        **{key: candidate[key] for key in IDS[1:]},
        candidate_evaluation_id=inputs["current_summary"]["evaluation_id"],
        planning_evaluation_id=inputs["planning_verification"]["evaluation_id"],
        planning_revision_id=inputs["planning_revision"]["planning_revision_id"],
        selected_delivery_manifest_id=inputs["delivery_manifest"]["manifest_id"],
        source_sha256=inputs["source_sha256"],
        files_sha256={PAYLOAD_NAME: planning.digest_bytes(payload_raw)},
        immutable=True,
        **FLAGS,
    )
    manifest["manifest_id"] = identity(manifest)
    return manifest


def _validate_output_path(root, handoff, output):
    output = _safe_output(root, output)
    if output == handoff or output in handoff.parents or handoff in output.parents:
        raise FactoryDraftError("Factory output and verified planning handoff must use separate directories")
    if output.exists():
        raise FactoryDraftError("Factory draft output already exists; choose a new directory")
    return output


def compile_bundle(*, root=ROOT, handoff_directory, output_path):
    """Write a new immutable draft bound to a current, verified planning revision."""
    root = Path(root).resolve()
    inputs = _load_inputs(root, handoff_directory)
    output = _validate_output_path(root, inputs["handoff"], output_path)
    payload = _compile_payload(inputs)
    payload_raw = encoded(payload)
    manifest = _package_manifest(inputs, payload_raw)
    manifest_raw = encoded(manifest)

    # Recheck every input before publication so a concurrent edit cannot be
    # recorded as a verified immutable handoff.
    for relative, expected in inputs["source_sha256"].items():
        if digest(_safe_file(root, relative)) != expected:
            raise FactoryDraftError("Source changed during factory draft compilation: " + relative)

    output.parent.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix=".osr-factory-draft-", dir=output.parent))
    try:
        (stage / PAYLOAD_NAME).write_bytes(payload_raw)
        (stage / "manifest.json").write_bytes(manifest_raw)
        stage.rename(output)
    except BaseException:
        shutil.rmtree(stage, ignore_errors=True)
        raise
    return dict(schema=MANIFEST_SCHEMA, execution="completed-immutable-draft",
                manifest_id=manifest["manifest_id"], factory_draft_id=payload["factory_draft_id"],
                selection_id=payload["selection_id"], **payload["physical_candidate"],
                candidate_evaluation_id=payload["candidate_evaluation_id"],
                planning_revision_id=payload["planning_revision_id"],
                planning_evaluation_id=payload["planning_evaluation_id"],
                output=output.relative_to(root).as_posix(), **FLAGS)


def verify_bundle(*, root=ROOT, handoff_directory, output_path):
    """Verify bytes, sources, planning identity and deterministic regeneration."""
    root = Path(root).resolve()
    inputs = _load_inputs(root, handoff_directory)
    output = _safe_output(root, output_path)
    if not output.is_dir():
        raise FactoryDraftError("Factory draft directory is required")
    expected_files = {PAYLOAD_NAME, "manifest.json"}
    actual_files = {path.relative_to(output).as_posix() for path in output.rglob("*") if path.is_file()}
    if actual_files != expected_files or any(path.is_symlink() for path in output.rglob("*")):
        raise FactoryDraftError("Factory draft file inventory differs")
    manifest_path = _safe_file(root, output.relative_to(root) / "manifest.json")
    payload_path = _safe_file(root, output.relative_to(root) / PAYLOAD_NAME)
    manifest = _read_json(manifest_path)
    payload_raw = payload_path.read_bytes()
    if manifest.get("schema") != MANIFEST_SCHEMA or manifest.get("immutable") is not True:
        raise FactoryDraftError("Factory draft manifest schema or immutability marker differs")
    if any(manifest.get(key) is not value for key, value in FLAGS.items()):
        raise FactoryDraftError("Factory draft cannot grant acceptance")
    if identity({key: value for key, value in manifest.items() if key != "manifest_id"}) != manifest.get("manifest_id"):
        raise FactoryDraftError("Factory draft manifest identity is stale")
    if manifest.get("files_sha256") != {PAYLOAD_NAME: planning.digest_bytes(payload_raw)}:
        raise FactoryDraftError("Factory draft payload hash differs")
    if manifest.get("source_sha256") != inputs["source_sha256"]:
        raise FactoryDraftError("Factory draft source inventory differs")
    for relative, expected in manifest["source_sha256"].items():
        if digest(_safe_file(root, relative)) != expected:
            raise FactoryDraftError("Factory draft source changed: " + relative)
    expected_payload = _compile_payload(inputs)
    if payload_raw != encoded(expected_payload):
        raise FactoryDraftError("Factory draft calculations or identity differ")
    for key in ("factory_draft_id", "selection_id", "candidate_id", "body_candidate_id",
                "support_component_id", "propulsion_component_id", "candidate_evaluation_id",
                "planning_evaluation_id", "planning_revision_id", "selected_delivery_manifest_id"):
        expected = expected_payload.get("physical_candidate", {}).get(key) if key in expected_payload.get("physical_candidate", {}) else expected_payload.get(key)
        if key in ("candidate_id", "body_candidate_id", "support_component_id", "propulsion_component_id"):
            expected = expected_payload["physical_candidate"][key]
        if manifest.get(key) != expected:
            raise FactoryDraftError("Factory draft manifest uses a different " + key)
    return dict(verified=True, manifest_id=manifest["manifest_id"],
                factory_draft_id=expected_payload["factory_draft_id"],
                selection_id=expected_payload["selection_id"],
                physical_candidate=expected_payload["physical_candidate"],
                candidate_evaluation_id=expected_payload["candidate_evaluation_id"],
                planning_revision_id=expected_payload["planning_revision_id"],
                planning_evaluation_id=expected_payload["planning_evaluation_id"],
                submittable=False, erpnext_admitted=False, **FLAGS)
