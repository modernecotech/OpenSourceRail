"""Bounded design-stage sensitivity for the selected vehicle's mass reserves.

Positive accounting residuals already sit inside the accounted tare. Each case
replaces those residual balances with a declared sensitivity value; it never
adds a second allowance on top of them. The report does not close installed
mass, component locations, centre of gravity, inertia, or axle reactions.
"""
from __future__ import annotations

import argparse
import gzip
import json
import math
import tomllib
from pathlib import Path

from engineering.station_rail import ROOT, FLAGS
from engineering.station_rail.common import digest, encoded, identity
from engineering.design_search import model_cost
from . import mass_ledger_audit

PRODUCER = "engineering/mass_reserve_sensitivity.py"
CONFIG = "campaigns/mass-reserve-sensitivity.toml"
INPUT = "docs/design-engine/mass-reconciliation/current"
OUTPUT = "docs/design-engine/mass-reserve-sensitivity/current"


def _specification(root):
    root = Path(root)
    value = tomllib.loads((root / CONFIG).read_text())
    cases = value.get("cases", {})
    names, factors = cases.get("names", []), cases.get("reserve_factors", [])
    completion = value.get("component_completion", {})
    if (value.get("schema") != "osr-current-mass-reserve-sensitivity/2"
            or names != ["low", "base", "high"] or len(factors) != 3
            or any(not math.isfinite(float(f)) or float(f) <= 0 for f in factors)
            or factors[1] != 1.0
            or completion.get("vehicles_per_demonstrator") != 6
            or completion.get("production_shifts_per_day") != 2
            or completion.get("production_hours_per_shift") != 8
            or not 0 < float(completion.get("productive_utilisation", 0)) <= 1
            or completion.get("source_class") != "C"
            or completion.get("mass_equivalent_volume_only") is not True
            or completion.get("no_cross_account_cost_summation") is not True):
        raise ValueError("Mass sensitivity requires positive low/base/high factors with an exact base factor")
    value["config_sha256"] = digest(root / CONFIG)
    value["assumption_id"] = identity(value)
    return value


_OVERLAP_ACCOUNTS = {
    "attachments": ["retained-comfort/frame-joints", "roof-thermal", "passive-bogie-pair"],
    "retained-comfort/body": ["retained-comfort/HVAC", "services", "retained-comfort/seating",
                              "retained-comfort/doors", "retained-comfort/glazing",
                              "retained-comfort/frame-joints"],
    "retained-comfort/HVAC": ["retained-comfort/body"],
    "retained-comfort/doors": ["retained-comfort/body"],
    "retained-comfort/frame-joints": ["attachments", "retained-comfort/body"],
    "retained-comfort/glazing": ["retained-comfort/body"],
    "retained-comfort/seating": ["retained-comfort/body"],
    "services": ["retained-comfort/body"],
    "roof-thermal": ["attachments"],
    "passive-bogie-pair": ["attachments"],
}

_COMPONENT_DESCRIPTIONS = {
    "hardpoints/roof-spreader": "Roof-spreader plate stock",
    "hardpoints/GFRP-isolator": "GFRP hardpoint isolators",
    "joints/gusset": "Frame-joint gusset plates",
    "joints/crush-sleeve": "Crush sleeves",
    "joints/M8-shank": "M8 bolt shanks",
    "joints/M8-head-and-nut": "M8 head-and-nut stock envelopes",
    "joints/GFRP-isolation": "GFRP joint-isolation pads",
    "joints/bond-film": "Joint bond film",
}


def _component_key(account_id, row):
    part = str(row.get("source_part_id") or "")
    occurrence = str(row.get("occurrence_id") or "source-occurrence")
    if account_id == "retained-comfort/glazing":
        tail = occurrence.split("/")[-1]
        return "glazing/" + tail.lower()
    return part or occurrence


def _component_profile(account_id, source_part_id, occurrence_id, description):
    token = " ".join(str(v or "") for v in (account_id, source_part_id, occurrence_id, description)).lower()
    if "/closure-remainder" in str(occurrence_id):
        family, density, method = "finished-equipment", None, "mixed-package"
        if account_id == "retained-comfort/doors":
            route = ["trim and finish leaf edges", "fit seals, guides and fixings", "match the leaf to the operator envelope", "cycle and inspect the assembled door"]
        elif account_id == "retained-comfort/seating":
            route = ["fabricate or procure seat supports and back supports", "fit upholstery, bonds and fasteners", "assemble modules at saloon interfaces", "proof-load and inspect fixtures"]
        elif account_id == "passive-bogie-pair":
            route = ["fabricate bogie frames and crossmembers", "machine or procure wheelsets, axles and axleboxes", "fit bearings, suspension and independent brakes", "assemble, gauge, inspect and run-in the bogie pair"]
        else:
            route = ["partition the account balance into non-overlapping parts", "assign materials and make/buy routes", "generate geometry and assembly interfaces", "inspect and record component masses"]
    elif any(v in token for v in ("roof-spreader", "gusset", "retention-aluminium")):
        family, density, method = "aluminium", 2700.0, "fabricate"
        route = ["cut or blank plate", "form or machine interface", "deburr and join", "dimensional inspection"]
    elif any(v in token for v in ("m8", "crush-sleeve")):
        family, density, method = "steel", 7850.0, "fabricate"
        route = ["purchase steel stock", "cut or machine fastener envelope", "apply corrosion protection", "inspect thread and fit"]
    elif "gfrp" in token:
        family, density, method = "gfrp", 1900.0, "fabricate"
        route = ["cut GFRP sheet or laminate", "finish edges and holes", "bond or mechanically retain", "inspect dimensions"]
    elif "bond" in token or "adhesive" in token or "film" in token:
        family, density, method = "adhesive", 1200.0, "fabricate"
        route = ["select compatible adhesive", "meter and apply", "cure under controlled conditions", "inspect bond witness samples"]
    elif "epdm" in token or "seal" in token:
        family, density, method = "elastomer", 1200.0, "fabricate"
        route = ["cut or mould seal stock", "prepare retaining groove", "fit and splice", "inspect continuity"]
    elif "glass" in token:
        family, density, method = "glass", 2500.0, "fabricate"
        route = ["cut glass to reviewed aperture", "edge finish", "laminate or temper as specified", "inspect optical and impact quality"]
    elif "pvb" in token:
        family, density, method = "polymer-film", 1070.0, "fabricate"
        route = ["cut interlayer film", "laminate to glass", "condition and inspect"]
    elif "roof-thermal" in token or "white-roof-finish" in token or "coating" in token:
        family, density, method = "coating", 1326.56, "fabricate"
        route = ["prepare roof surface", "apply declared coating thickness", "cure", "inspect coverage and adhesion"]
    elif "hvac" in token or "konvekta" in token or "wabtec" in token or "battery" in token or "module-reference" in token:
        family, density, method = "finished-equipment", None, "buy-and-integrate"
        route = ["procure or obtain a bounded equipment estimate", "receive and inspect", "define mounting and service interfaces", "bench or fit-check the package"]
    elif account_id == "passive-bogie-pair":
        family, density, method = "finished-equipment", None, "mixed-package"
        route = ["fabricate bogie frames and crossmembers", "machine or procure wheelsets, axles and axleboxes", "fit bearings, suspension and independent brakes", "assemble, gauge, inspect and run-in the bogie pair"]
    elif account_id == "attachments":
        family, density, method = "finished-equipment", None, "mixed-package"
        route = ["prepare joint, fin-retention and thermal-interface stock", "cut, drill, form or mould metal/composite parts", "fit isolation and fastener stacks to a reviewed joint detail", "inspect torque, bond and maintenance access"]
    elif account_id in ("retained-comfort/body", "retained-comfort/seating"):
        family, density, method = "finished-equipment", None, "mixed-package"
        route = ["separate the inherited reserve into equipment and fitout packages", "procure catalogued equipment and locally fabricate supports or trim", "assemble wiring, ducts, panels and interior fixtures at reviewed interfaces", "inspect and record package mass and function"]
    else:
        family, density, method = "finished-equipment", None, "buy-and-integrate"
        route = ["procure or calculate a bounded component package", "receive and inspect", "define assembly interface", "bench or fit-check the package"]
    return dict(material_family=family, assumed_density_kg_m3=density,
        cost_method=method, provisional_process_route=route,
        material_spec_status=("material-family and density hypothesis only; not a released material specification"
            if density else "material composition unresolved; mass-based equipment rate used"),
        process_route_status="Class C process hypothesis; durations are estimated and not manufacturing-released",
        dimension_status="unknown; no physical dimensions inferred from the mass account",
        location_status="vehicle-zone hypothesis only; installed coordinates and clearances are unknown")


def _description(account_id, source_part_id, occurrence_id, role=""):
    part = str(source_part_id or "")
    occurrence = str(occurrence_id or "")
    tail = occurrence.split("/")[-1]
    if part in _COMPONENT_DESCRIPTIONS:
        return _COMPONENT_DESCRIPTIONS[part]
    if account_id == "retained-comfort/glazing":
        return {"EPDM-seal": "EPDM glazing seal stock", "bond": "Glazing bond allowance",
            "retention-aluminium": "Aluminium glazing retention stock", "glass": "Glass pane stock",
            "PVB": "PVB interlayer stock"}.get(tail, "Unlocated glazing source material")
    if account_id == "retained-comfort/HVAC":
        return "Supplier-reference HVAC package"
    if account_id == "retained-comfort/doors" and "Wabtec" in part:
        return "Wabtec 1300 mm door-operator reference package"
    if account_id == "retained-comfort/body":
        return "Inherited unlocated body, services, interior, cooling, electronics and contingency reserve"
    if account_id == "retained-comfort/seating":
        return "Inherited unlocated interior and seating reserve"
    if account_id == "attachments":
        return "Body/bogie joints, fin-retention and thermal-joint reserve"
    if account_id == "roof-thermal":
        return "White roof coating takeoff"
    if account_id == "services":
        return part.replace("allowance/", "").replace("-", " ") or "Service equipment package"
    return str(part or role or occurrence or "Account residual reserve")


def _material_rates(assumptions_record, family):
    values = assumptions_record["assumptions"]
    if family == "aluminium":
        return values["aluminium_iqd_per_kg"]
    if family in ("gfrp", "glass", "polymer-film", "coating"):
        return values["composite_iqd_per_kg"]
    if family == "steel":
        return values["steel_iqd_per_kg"]
    if family in ("adhesive", "elastomer"):
        return values["generic_material_iqd_per_kg"]
    return values["finished_equipment_iqd_per_kg"]


def _component_cost(component, mass_kg, index, assumptions_record):
    a = assumptions_record["assumptions"]
    material_rates = _material_rates(assumptions_record, component["material_family"])
    if component["cost_method"] == "buy-and-integrate" or component["cost_method"] == "mixed-package":
        material_iqd = mass_kg * material_rates[index]
        process_hours = mass_kg * a["equipment_process_hours_per_kg"][index]
        machine_cost = 0.0
    else:
        purchase_mass_kg = mass_kg / a["body_purchase_yield"][index]
        material_iqd = purchase_mass_kg * material_rates[index]
        process_hours = (mass_kg * a["body_process_hours_per_kg"][index]
            + float(component["quantity"]) * a["body_process_setup_hours_per_stock"][index])
        machine_hours = mass_kg * a["body_machine_hours_per_kg"][index]
        machine_cost = machine_hours * a["machine_rate_iqd_per_h"][index]
    wage = assumptions_record["benchmark_rates_iqd"]["wage_skilled_iqd_per_h"]
    burden = a["wage_burden_multipliers"][index]
    shift_premium = a["second_shift_wage_premium"][index]
    production_wage = wage * burden * (1 + shift_premium / assumptions_record["production_shifts_per_day"])
    labour_iqd = process_hours * production_wage
    qa_iqd = material_iqd * a["body_qa_fraction"][index]
    direct_iqd = material_iqd + labour_iqd + machine_cost + qa_iqd
    overhead_iqd = direct_iqd * a["factory_overhead_fraction"][index]
    return dict(net_mass_kg=mass_kg,
        material_or_equipment_iqd=material_iqd, process_hours=process_hours,
        labour_iqd=labour_iqd, machine_and_tool_iqd=machine_cost,
        QA_iqd=qa_iqd, factory_overhead_iqd=overhead_iqd,
        total_factory_gate_iqd=direct_iqd + overhead_iqd,
        cost_class="C", currency="IQD")


def _component_completion(root, config, ledger, residual_rows):
    settings = config["component_completion"]
    cost_basis = model_cost.assumptions(root)
    component_rows = []
    account_summaries = []
    residual_by_id = {r["account_id"]: r for r in residual_rows}
    source_by_account = {}
    for row in ledger["source_account_occurrences"]:
        source_by_account.setdefault(row["account_id"], []).append(row)
    analytical_by_account = {r["account_id"]: r for r in ledger["analytical_occurrence_estimates"]}
    for account_id, balance in residual_by_id.items():
        sources = source_by_account.get(account_id, [])
        proposals = []
        source_groups = {}
        for source in sources:
            if source.get("candidate_geometry_links"):
                continue
            source_groups.setdefault(_component_key(account_id, source), []).append(source)
        for key, group in source_groups.items():
            source = group[0]
            breakdown = source.get("calculated_component_mass_breakdown")
            if breakdown:
                if (breakdown.get("additive_to_source_account") is not False
                        or abs(float(breakdown.get("calculated_account_mass_kg", 0))
                               - sum(float(r["mass_kg"]) for r in group)) > 1e-6):
                    raise ValueError("Nested source component breakdown is not a non-additive exact replacement")
                for item in breakdown.get("components", []):
                    component_id = str(item["component_id"])
                    part = component_id
                    description = str(item.get("description") or component_id)
                    profile = _component_profile(account_id, part, source["occurrence_id"], description)
                    proposals.append(dict(component_id=component_id, account_id=account_id,
                        description=description, base_mass_kg=float(item["accounted_mass_kg"]),
                        quantity=float(item.get("quantity", 1)), unit=item.get("unit", "item"),
                        unit_mass_kg=float(item.get("unit_mass_kg", item["accounted_mass_kg"])),
                        source_occurrence_ids=[r["occurrence_id"] for r in group], source_component_id=component_id,
                        source_reference_ids=item.get("source_reference_ids", []),
                        mass_basis=item.get("mass_basis", "Nested source-account component breakdown"),
                        component_identity_status="source component identity; physical installation open",
                        **profile))
                continue
            group_mass = sum(float(r["mass_kg"]) for r in group)
            proposals.append(dict(component_id=key, account_id=account_id,
                description=_description(account_id, source.get("source_part_id"), source.get("occurrence_id"), source.get("role", "")),
                base_mass_kg=group_mass, quantity=float(len(group)), unit="source occurrence",
                unit_mass_kg=group_mass / len(group),
                source_occurrence_ids=[r["occurrence_id"] for r in group], source_part_id=source.get("source_part_id"),
                source_evidence_class=source.get("evidence_class"),
                mass_basis=source.get("role") or source.get("evidence_class") or "Unlocated source-account occurrence",
                component_identity_status="source-account identity; physical installation open",
                **_component_profile(account_id, source.get("source_part_id"), source.get("occurrence_id"), source.get("role", ""))))
        analytical = analytical_by_account.get(account_id)
        if analytical and not proposals:
            mass = float(analytical["estimated_mass_kg"])
            proposals.append(dict(component_id=analytical["source_account_occurrence_id"], account_id=account_id,
                description=_description(account_id, analytical["source_account_occurrence_id"], analytical["source_account_occurrence_id"]),
                base_mass_kg=mass, quantity=1.0, unit="analytical takeoff", unit_mass_kg=mass,
                source_occurrence_ids=[analytical["source_account_occurrence_id"]],
                source_geometry_part_ids=analytical["source_geometry_part_ids"],
                mass_basis=analytical["calculation"], component_identity_status="analytical material takeoff; coating geometry and installation open",
                **_component_profile(account_id, analytical["source_account_occurrence_id"], analytical["source_account_occurrence_id"], "coating")))
        itemized_mass = sum(float(p["base_mass_kg"]) for p in proposals)
        residual = float(balance["existing_residual_kg"])
        if itemized_mass > residual + 1e-6:
            raise ValueError(f"Unlocated source components exceed closure residual for {account_id}")
        remainder = residual - itemized_mass
        if remainder > 1e-7:
            remainder_id = account_id + "/closure-remainder"
            if account_id == "retained-comfort/doors":
                description = "Door-leaf edges, seals, guides and fixings closure reserve"
            elif account_id == "retained-comfort/seating":
                description = "Seat supports, back supports, upholstery, bonds and fixings closure reserve"
            elif account_id == "retained-comfort/body":
                description = "Unmatched inherited body-account balance; disaggregation and overlap review required"
            elif account_id == "passive-bogie-pair":
                description = "Passive bogie frames, wheelsets, bearings, suspension and brakes reserve"
            else:
                description = "Unitemized account-closure reserve"
            proposals.append(dict(component_id=remainder_id, account_id=account_id,
                description=description, base_mass_kg=remainder, quantity=1.0, unit="bounded account reserve",
                unit_mass_kg=remainder,
                source_occurrence_ids=[], source_part_id=None,
                source_evidence_class="closure-balance-derived", mass_basis="Exact difference between the canonical account residual and non-geometric source occurrences; not additional mass",
                component_identity_status="provisional reserve package; part identity open",
                **_component_profile(account_id, None, remainder_id, description)))
        if not proposals:
            description = _description(account_id, None, account_id)
            proposals.append(dict(component_id=account_id + "/provisional-reserve", account_id=account_id,
                description=description, base_mass_kg=residual, quantity=1.0, unit="bounded account reserve",
                unit_mass_kg=residual,
                source_occurrence_ids=[], source_part_id=None,
                source_evidence_class="closure-balance-derived", mass_basis="Exact canonical account residual; provisional package only",
                component_identity_status="provisional reserve package; part identity open",
                **_component_profile(account_id, None, account_id, description)))
        if abs(sum(p["base_mass_kg"] for p in proposals) - residual) > 1e-6:
            raise ValueError("Component completion proposals must replace each account residual exactly once")
        related = _OVERLAP_ACCOUNTS.get(account_id, [])
        acc_cases = {name: dict(mass_kg=0.0, cost_iqd=0.0, process_hours=0.0)
                     for name in config["cases"]["names"]}
        for proposal in proposals:
            profile = {k: proposal.pop(k) for k in ("material_family", "assumed_density_kg_m3",
                "cost_method", "provisional_process_route", "material_spec_status",
                "process_route_status", "dimension_status", "location_status")}
            proposal.update(profile)
            proposal.update(candidate_id=config["source_candidate_id"],
                selection_id=config["source_selection_id"], evaluation_id=ledger["selected_evaluation_id"],
                replaces_account_id=account_id, added_on_top_of_account=False,
                cross_account_overlap_status="unresolved; do not sum across accounts as independent installed mass",
                potentially_overlapping_accounts=related,
                installed_position_m=None, physical_installed_mass_kg=None,
                physical_acceptance=False, manufacturing_release=False, operating_release=False)
            scenario_mass, scenario_cost, process_hours = {}, {}, {}
            density = proposal["assumed_density_kg_m3"]
            equivalent_volume = {}
            for i, name in enumerate(config["cases"]["names"]):
                mass = float(proposal["base_mass_kg"]) * float(config["cases"]["reserve_factors"][i])
                estimate = _component_cost(proposal, mass, i, cost_basis)
                scenario_mass[name] = mass
                scenario_cost[name] = estimate
                process_hours[name] = estimate["process_hours"]
                equivalent_volume[name] = (mass / float(density)) if density else None
                acc_cases[name]["mass_kg"] += mass
                acc_cases[name]["cost_iqd"] += estimate["total_factory_gate_iqd"]
                acc_cases[name]["process_hours"] += estimate["process_hours"]
            proposal["scenario_mass_kg"] = scenario_mass
            proposal["mass_equivalent_volume_m3"] = equivalent_volume
            proposal["estimated_factory_process_hours"] = process_hours
            proposal["class_c_factory_gate_cost"] = scenario_cost
            proposal["six_car_class_c_factory_gate_cost_iqd"] = {
                name: estimate["total_factory_gate_iqd"] * settings["vehicles_per_demonstrator"]
                for name, estimate in scenario_cost.items()}
            proposal["mass_equivalent_volume_is_not_geometry"] = True
            component_rows.append(proposal)
        if any(acc_cases[name]["cost_iqd"] > acc_cases[next_name]["cost_iqd"] + 1e-6
               for name, next_name in zip(config["cases"]["names"], config["cases"]["names"][1:])):
            raise ValueError("Low/base/high component cost cases must remain ordered")
        account_summaries.append(dict(account_id=account_id,
            source_residual_kg_per_car=residual, component_count=len(proposals),
            low_base_high=acc_cases,
            six_car_cost_iqd_by_case={name: acc_cases[name]["cost_iqd"] * settings["vehicles_per_demonstrator"]
                for name in config["cases"]["names"]},
            replaces_source_account=True, added_on_top_of_account=False,
            potentially_overlapping_accounts=related,
            cross_account_overlap_status="unresolved"))
    return dict(schema="osr-selected-component-completion/1",
        candidate_id=config["source_candidate_id"], selection_id=config["source_selection_id"],
        evaluation_id=ledger["selected_evaluation_id"], vehicles_per_demonstrator=settings["vehicles_per_demonstrator"],
        production_shift_basis=dict(shifts_per_day=settings["production_shifts_per_day"],
            hours_per_shift=settings["production_hours_per_shift"],
            productive_utilisation=settings["productive_utilisation"],
            civil_shifts_per_day=cost_basis["civil_shifts_per_day"],
            operations_shifts_per_day_cases=cost_basis["operations_shifts_per_day_cases"],
            basis="The vehicle-package factory estimates use the two-shift production case. Civil work uses two shifts. City operating-cost cases retain two, two and three shifts/day."),
        cost_basis=dict(source_class="C", currency=cost_basis["currency"], estimate_date=cost_basis["estimate_date"],
            cost_assumption_id=cost_basis["assumption_id"], rate_dataset=cost_basis["benchmark_dataset"]),
        account_count=len(account_summaries), component_count=len(component_rows),
        account_packages=account_summaries, components=component_rows,
        all_account_residuals_partitioned=True,
        cross_account_overlap_closed=False,
        all_account_cost_total_iqd=None,
        integrated_into_city_cost_model=False,
        accounting_rule="Each component package partitions and replaces one existing account residual. Proposals are not additional mass. Cross-account overlap remains unresolved, so account costs are not summed into a new all-in train or corridor price.",
        dimensions_and_locations="No unverified physical dimensions or installation coordinates are invented. Material-equivalent volume is reported only where a declared density exists; generic reserves retain unknown material and dimensions.",
        process_hours_scope="Process hours are estimated factory labour-hours, not elapsed production schedule; crew size, parallel workstations, tooling capacity, precedence and procurement lead times remain outside this component-level decomposition.",
        whole_system_cost_integration="Not added to the 112-bundle city model. These selected-candidate component estimates are a decomposition/replacement view; integrating them requires suppressing the corresponding aggregate account cost lines and closing cross-account overlap first.",
        physical_acceptance=False, installed_mass_complete=False, manufacturing_release=False, operating_release=False)


def plan(root=ROOT):
    root = Path(root).resolve()
    verified = mass_ledger_audit.verify(root)
    folder = root / INPUT
    manifest = json.loads((folder / "manifest.json").read_bytes())
    worksheet = json.loads(gzip.decompress((folder / "mass-closure-worksheet.json.gz").read_bytes()))
    ledger = json.loads(gzip.decompress((folder / "mass-ledger.json.gz").read_bytes()))
    summary = json.loads((folder / "summary.json").read_bytes())
    config = _specification(root)
    if (verified.get("verified") is not True
            or worksheet.get("candidate_id") != config["source_candidate_id"]
            or worksheet.get("selection_id") != config["source_selection_id"]
            or worksheet.get("worksheet_id") != summary.get("closure_worksheet_id")
            or worksheet.get("unknown_is_zero") is not False
            or summary.get("installed_mass_complete") is not False):
        raise ValueError("Selected mass ledger/worksheet identity or open-evidence state differs")
    closures = [r for r in worksheet["rows"] if r.get("record_kind") == "account-closure"]
    if len(closures) != summary.get("account_row_count"):
        raise ValueError("Mass reserve requires every canonical account closure exactly once")
    residual_rows = []
    reconciled_geometry_accounts = []
    for row in closures:
        accounted = float(row["accounted_source_mass_kg"])
        geometry = float(row["candidate_geometry_mass_kg"])
        residual = float(row["accounting_residual_kg"])
        if (not all(math.isfinite(v) for v in (accounted, geometry, residual))
                or min(accounted, geometry, residual) < -1e-8
                or abs(accounted - geometry - residual) > 1e-6):
            raise ValueError("Accounted mass must reconcile once into geometry plus residual reserve")
        if residual > 1e-8:
            residual_rows.append(dict(account_id=row["account_id"],
                accounted_source_mass_kg=accounted,
                candidate_geometry_mass_kg=geometry,
                existing_residual_kg=residual,
                mass_evidence_class=row["mass_evidence_class"],
                scenario_reserve_kg={name: residual * factor for name, factor
                    in zip(config["cases"]["names"], config["cases"]["reserve_factors"])},
                added_instead_of_replaced=False,
                physically_installed_mass_kg=None, installed_position_m=None,
                component_identity_resolved=False))
        else:
            reconciled_geometry_accounts.append(dict(account_id=row["account_id"],
                accounted_source_mass_kg=accounted,
                candidate_geometry_mass_kg=geometry,
                accounting_residual_kg=0.0,
                note="Accounting subtotal matches represented geometry. This does not verify installation or exclude unmodelled joints, fasteners, or interfaces."))
    if len(residual_rows) != summary.get("closure_worksheet_account_residual_count"):
        raise ValueError("Positive residual account count differs from the exact closure worksheet")
    factors = config["cases"]["reserve_factors"]
    names = config["cases"]["names"]
    located = float(summary["located_geometry_mass_kg"])
    accounted_tare = float(summary["accounted_tare_kg_per_car"])
    residual_total = float(summary["residual_reference_or_unlocated_mass_kg"])
    if (abs(sum(r["existing_residual_kg"] for r in residual_rows) - residual_total) > 1e-6
            or abs(located + residual_total - accounted_tare) > 1e-6):
        raise ValueError("Per-account reserves do not close to the existing selected-candidate tare")
    completion = _component_completion(root, config, ledger, residual_rows)
    cases = []
    for name, factor in zip(names, factors):
        reserve = sum(r["scenario_reserve_kg"][name] for r in residual_rows)
        tare = located + reserve
        cases.append(dict(name=name, reserve_factor=factor,
            existing_unlocated_reserve_kg=residual_total,
            sensitivity_reserve_kg=reserve,
            located_geometry_subtotal_kg=located,
            scenario_tare_mass_kg_per_car=tare,
            six_car_scenario_tare_mass_kg=6.0 * tare,
            change_from_accounted_tare_kg_per_car=tare - accounted_tare,
            scenario_basis="Located candidate geometry subtotal plus the re-scaled existing residual accounts; no duplicate reserve added."))
    source_files = {name: digest(root / name) for name in (
        "engineering/mass_ledger_audit.py", CONFIG,
        "engineering/vehicle_optimisation/equipment.py",
        "engineering/design_search/model_cost.py",
        "engineering/sourcing/data/iraq-domestic-2026-july.json",
        f"{INPUT}/manifest.json", f"{INPUT}/mass-closure-worksheet.json.gz",
        f"{INPUT}/mass-ledger.json.gz", f"{INPUT}/summary.json")}
    result = dict(schema="osr-current-mass-reserve-sensitivity-result/2",
        assumption_id=config["assumption_id"], ledger_manifest_id=manifest["manifest_id"],
        worksheet_id=worksheet["worksheet_id"], candidate_id=worksheet["candidate_id"],
        body_candidate_id=worksheet["body_candidate_id"], selection_id=worksheet["selection_id"],
        evaluation_id=worksheet["evaluation_id"], vehicle_evaluation_id=worksheet["vehicle_evaluation_id"],
        accounted_tare_mass_kg_per_car=accounted_tare,
        located_geometry_mass_kg_per_car=located,
        existing_unlocated_residual_kg_per_car=residual_total,
        residual_account_count=len(residual_rows), reserve_accounts=residual_rows,
        component_completion=completion,
        geometry_reconciled_accounts=reconciled_geometry_accounts,
        sensitivity_cases=cases,
        complete_installed_mass_kg_per_car=None, installed_centre_of_gravity_m=None,
        installed_inertia_kg_m2=None, axle_reactions=None,
        mass_scenario_complete_for_declared_scope=True,
        physically_installed_mass_known=False,
        physical_acceptance=False, interpretation=(
            "This is a provisional sensitivity of the existing selected-candidate mass account. "
            "The low/base/high factors are declared scenarios, not probability bounds. Positive "
            "residuals are replaced within each scenario; they are not added twice. Equipment, "
            "joint, fastener, cooling, wiring, and installation identities/locations remain open "
            "where the source worksheet has no physical component evidence."),
        source_sha256=source_files, **FLAGS)
    result["result_id"] = identity(result)
    return result


def _readme(result):
    lines = ["# Selected vehicle residual mass completion", "",
        f"Candidate `{result['candidate_id']}` and selection `{result['selection_id']}` retain the source ledger's accounted tare of **{result['accounted_tare_mass_kg_per_car']:,.3f} kg/car**. Candidate geometry represents **{result['located_geometry_mass_kg_per_car']:,.3f} kg/car**. The existing positive accounting residual is **{result['existing_unlocated_residual_kg_per_car']:,.3f} kg/car** across {result['residual_account_count']} accounts.", "",
        "Each low/base/high case replaces that existing residual reserve with a declared 0.8×/1.0×/1.2× sensitivity. The reserve is not added again on top of the accounted tare.", "",
        "| Case | Reserve sensitivity (kg/car) | Scenario tare (kg/car) | Six-car scenario tare (kg) | Change from existing tare (kg/car) |",
        "|---|---:|---:|---:|---:|"]
    for row in result["sensitivity_cases"]:
        lines.append(f"| {row['name']} ({row['reserve_factor']:.1f}×) | {row['sensitivity_reserve_kg']:,.3f} | {row['scenario_tare_mass_kg_per_car']:,.3f} | {row['six_car_scenario_tare_mass_kg']:,.3f} | {row['change_from_accounted_tare_kg_per_car']:+,.3f} |")
    lines += ["", "## Account-level reserves", "",
        "| Account | Existing residual (kg/car) | Low (kg/car) | Base (kg/car) | High (kg/car) |",
        "|---|---:|---:|---:|---:|"]
    for row in result["reserve_accounts"]:
        s = row["scenario_reserve_kg"]
        lines.append(f"| {row['account_id']} | {row['existing_residual_kg']:,.3f} | {s['low']:,.3f} | {s['base']:,.3f} | {s['high']:,.3f} |")
    completion = result["component_completion"]
    lines += ["", "## Provisional component completion", "",
        f"The completion routine partitions all {completion['account_count']} positive residual accounts into {completion['component_count']} source-linked or explicitly provisional component packages. The base case replaces each existing account balance exactly; no package is added on top. Candidate `{completion['candidate_id']}` and selection `{completion['selection_id']}` bind the estimates.", "",
        "The package-cost ranges are Class C factory-gate calculations from the dated Iraqi rate dataset plus declared process, burden, yield, QA, overhead and equipment proxies. They exclude delivery, final vehicle installation, commissioning and field civil works. Costs are reported per account because overlaps remain unresolved; they are not summed into a new train total or added to the 112-bundle corridor model. Use the account components only as a replacement for their matching aggregate account estimate.", "",
        f"Production uses {completion['production_shift_basis']['shifts_per_day']} eight-hour shifts/day at {completion['production_shift_basis']['productive_utilisation']:.0%} productive utilisation. The same cost basis retains two civil shifts/day and operating cases of {', '.join(str(x) for x in completion['production_shift_basis']['operations_shifts_per_day_cases'])} shifts/day, including the eventual three-shift operations case. Process hours are labour-hour estimates, not an elapsed production schedule; crew size, concurrent cells, precedence, tooling capacity and procurement lead times remain open.", "",
        "| Residual account | Base mass (kg/car) | Packages | Base factory labour (h/car; six-car) | Class C factory-gate cost (IQD/car, low/base/high) | Six-car base cost (IQD) | Overlap review |",
        "|---|---:|---:|---:|---:|---:|---|"]
    for account in completion["account_packages"]:
        base = account["low_base_high"]["base"]["cost_iqd"]
        costs = [account["low_base_high"][name]["cost_iqd"] for name in ("low", "base", "high")]
        hours = account["low_base_high"]["base"]["process_hours"]
        train_cars = completion["vehicles_per_demonstrator"]
        lines.append(f"| {account['account_id']} | {account['source_residual_kg_per_car']:,.3f} | {account['component_count']} | {hours:,.1f}; {train_cars * hours:,.1f} | {costs[0]:,.0f} / {costs[1]:,.0f} / {costs[2]:,.0f} | {account['six_car_cost_iqd_by_case']['base']:,.0f} | unresolved |")
    lines += ["", "### Component proposals", "",
        "| Account | Component proposal | Base mass (kg/car) | Material family | Provisional process route | Base cost (IQD/car) |",
        "|---|---|---:|---|---|---:|"]
    for component in completion["components"]:
        base_mass = component["scenario_mass_kg"]["base"]
        base_cost = component["class_c_factory_gate_cost"]["base"]["total_factory_gate_iqd"]
        lines.append(f"| {component['account_id']} | {component['description']} | {base_mass:,.3f} | {component['material_family']} | {'; '.join(component['provisional_process_route'])} | {base_cost:,.0f} |")
    lines += ["", "Dimensions and installed positions remain explicitly open. Known-density values produce only mass-equivalent material volume, never a geometric envelope. Equipment and inherited balances use Class C mass-based estimates. The body account includes inherited services/interior/cooling/electronics/contingency, so its cross-account overlap with separately named systems remains unresolved. The 180 kg attachment reserve can overlap frame joints, bogie interfaces and roof treatment. Component packages therefore replace only their own account and must not be summed across those overlaps as independent installed mass.", "",
        completion["whole_system_cost_integration"], "",
        "## Scope and evidence", "",
        result["interpretation"], "",
        "The two accounts with no accounting residual reconcile to represented geometry mass; this does not prove installation or reserve additional physical joints, fasteners and interfaces. The account totals therefore remain incomplete as an installed inventory.", "",
        "The 0.8×/1.0×/1.2× factors are sensitivity assumptions only. They are not statistical confidence limits or supplier-confirmed ranges. Replace them with component-specific calculated mass or measured procurement/installation evidence when available.", "",
        "The selected reference, CAD, and release states are unchanged. Centre of gravity, inertia, axle reactions, and complete installed mass remain unknown.", "",
        "Reproduce with `python3 -m engineering.mass_reserve_sensitivity build` and `python3 -m engineering.mass_reserve_sensitivity verify`.", "",
        "[Exact result](result.json) · [Manifest](manifest.json)", ""]
    return "\n".join(lines)


def publish(root=ROOT, output=None):
    root = Path(root).resolve()
    out = root / OUTPUT if output is None else Path(output)
    result = plan(root)
    out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_bytes(encoded(result))
    (out / "README.md").write_text(_readme(result))
    sources = dict(result["source_sha256"], **{PRODUCER: digest(root / PRODUCER)})
    manifest = dict(schema="osr-current-mass-reserve-sensitivity-manifest/2",
        result_id=result["result_id"], source_sha256=sources,
        files_sha256={p.relative_to(out).as_posix(): digest(p) for p in out.rglob("*")
                      if p.is_file() and p.name != "manifest.json"},
        physical_acceptance=False, **FLAGS)
    manifest["manifest_id"] = identity(manifest)
    (out / "manifest.json").write_bytes(encoded(manifest))
    return verify(root, out)


def verify(root=ROOT, output=None):
    root = Path(root).resolve()
    out = root / OUTPUT if output is None else Path(output)
    manifest = json.loads((out / "manifest.json").read_bytes())
    actual = {p.relative_to(out).as_posix(): digest(p) for p in out.rglob("*")
              if p.is_file() and p.name != "manifest.json"}
    if (manifest.get("manifest_id") != identity({k: v for k, v in manifest.items()
                                                   if k != "manifest_id"})
            or manifest.get("files_sha256") != actual
            or any(digest(root / name) != value for name, value in manifest.get("source_sha256", {}).items())):
        raise ValueError("Mass reserve sensitivity manifest, payload or source epoch differs")
    result = json.loads((out / "result.json").read_bytes())
    expected = plan(root)
    if result != expected or manifest.get("result_id") != expected.get("result_id"):
        raise ValueError("Mass reserve sensitivity does not replay from the selected exact worksheet")
    if (result.get("installed_mass_complete") is not False
            or result.get("complete_installed_mass_kg_per_car") is not None
            or result.get("physical_acceptance") is not False):
        raise ValueError("Mass sensitivity cannot grant installed-mass or physical acceptance")
    return dict(verified=True, result_id=result["result_id"],
        candidate_id=result["candidate_id"], selection_id=result["selection_id"],
        residual_account_count=result["residual_account_count"],
        low_tare_kg_per_car=result["sensitivity_cases"][0]["scenario_tare_mass_kg_per_car"],
        base_tare_kg_per_car=result["sensitivity_cases"][1]["scenario_tare_mass_kg_per_car"],
        high_tare_kg_per_car=result["sensitivity_cases"][2]["scenario_tare_mass_kg_per_car"],
        complete_installed_mass_kg_per_car=None, **FLAGS)


def main(argv=None):
    parser = argparse.ArgumentParser(prog="python3 -m engineering.mass_reserve_sensitivity")
    parser.add_argument("action", choices=("build", "verify"))
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    result = publish(args.root, args.output) if args.action == "build" else verify(args.root, args.output)
    print(json.dumps(result, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
