"""Candidate-bound gross material takeoff for a federated railway BOM.

This report converts already declared engineering stock masses and geometry
volumes into traceable material roll-ups. It does not infer order quantities,
manufacturing hours, yields, installed mass, or procurement approval.
"""
from collections import defaultdict
from decimal import Decimal, localcontext

from engineering.station_rail.common import identity as native_identity
from .model import day, decimal, decimal_text, identity
from .requirements import extract_requirements, validate_requirements


_COMMODITY_BENCHMARKS = {
    "copper-conductor": "Copper",
    "aluminium_reference": "Aluminum",
    "6082-T6-proposed": "Aluminum",
}


def _source_rows(records):
    sources = {row["record_id"]: row for row in records if row.get("kind") == "source"}
    benchmarks = {row["benchmark_key"]: row for row in records if row.get("kind") == "benchmark"}
    return sources, benchmarks


def material_takeoff(twin_input, *, catalogue_records, as_of):
    """Build a candidate-bound roll-up while preserving every stock occurrence."""
    as_of_date = day(as_of, "takeoff date").isoformat()
    if (not isinstance(twin_input, dict) or
            twin_input.get("schema") != "osr-sourcing-twin-input/1" or
            twin_input.get("payload_id") != identity(twin_input.get("payload"))):
        raise ValueError("Exact sealed sourcing twin input required")
    payload = twin_input["payload"]
    if not isinstance(payload, dict) or payload.get("schema") != "osr-federated-railway-BOM/1":
        raise ValueError("Material takeoff requires a federated railway BOM")
    if payload.get("evaluation_id") != native_identity(
            {key: value for key, value in payload.items() if key != "evaluation_id"}):
        raise ValueError("Federated BOM evaluation identity differs")

    requirements = extract_requirements(payload)
    candidate_id = validate_requirements(requirements)
    if candidate_id != payload.get("candidate_id"):
        raise ValueError("Takeoff candidate identity differs from its engineering BOM")

    occurrences = payload.get("engineering_BOM")
    groups = payload.get("manufacturing_BOM")
    if not isinstance(occurrences, list) or not isinstance(groups, list):
        raise ValueError("Located stock occurrences and source manufacturing groups are required")
    rows = {}
    unlocated = []
    for row in occurrences:
        if not isinstance(row, dict) or row.get("candidate_id") != candidate_id:
            raise ValueError("Mixed candidate or malformed engineering occurrence")
        row_id = row.get("id")
        if not isinstance(row_id, str) or row_id in rows:
            raise ValueError("Distinct engineering occurrence identities required")
        rows[row_id] = row
        if row.get("scope") == "unlocated-account-or-obligation":
            unlocated.append(row_id)

    seen = set()
    output_groups = []
    rollups = defaultdict(lambda: {
        "group_count": 0, "occurrence_count": 0, "mass_sum_kg": Decimal(0),
        "mass_missing_group_count": 0, "volume_sum_m3": Decimal(0),
        "volume_missing_group_count": 0, "labour_sum_h": Decimal(0),
        "labour_missing_group_count": 0, "gross_mass_reconciliation_max_abs_kg": Decimal(0),
    })
    with localcontext() as context:
        context.prec = 32
        for group in groups:
            if not isinstance(group, dict) or group.get("candidate_id") != candidate_id:
                raise ValueError("Mixed candidate or malformed manufacturing group")
            member_ids = group.get("engineering_occurrence_ids")
            if not isinstance(member_ids, list) or not member_ids or len(member_ids) != len(set(member_ids)):
                raise ValueError("Distinct located occurrence membership required")
            if any(member_id not in rows or member_id in seen for member_id in member_ids):
                raise ValueError("Manufacturing groups must partition located occurrences exactly once")
            members = [rows[member_id] for member_id in member_ids]
            if any(member.get("scope") == "unlocated-account-or-obligation" for member in members):
                raise ValueError("Unlocated accounts cannot be assigned to a material group")
            seen.update(member_ids)
            keys = {(member.get("system"), member.get("material"), member.get("scope"))
                    for member in members}
            if len(keys) != 1:
                raise ValueError("Takeoff group crosses system, material or stock scope")
            system, material, stock_scope = next(iter(keys))
            key = (system or "unclassified", material or "unclassified", stock_scope or "unclassified")

            gross = group.get("known_gross_stock_mass_kg")
            if gross is None:
                gross_decimal = None
                member_mass_decimal = None
                mass_residual = None
            else:
                gross_decimal = decimal(gross, "known gross stock mass", nonnegative=True)
                member_masses = [member.get("accounted_mass_kg") for member in members]
                if all(value is not None for value in member_masses):
                    member_mass_decimal = sum((decimal(value, "member accounted mass", nonnegative=True)
                                               for value in member_masses), Decimal(0))
                    mass_residual = gross_decimal - member_mass_decimal
                else:
                    member_mass_decimal = None
                    mass_residual = None

            member_volumes = [member.get("nominal_stock_volume_m3") for member in members]
            if all(value is not None for value in member_volumes):
                volume_decimal = sum((decimal(value, "nominal stock volume", nonnegative=True)
                                      for value in member_volumes), Decimal(0))
            else:
                volume_decimal = None

            labour = group.get("labour_h")
            labour_decimal = None if labour is None else decimal(labour, "declared labour hours", nonnegative=True)
            item = {
                "manufacturing_group_id": group["group_id"],
                "engineering_group_key": group["id"],
                "system": system,
                "material": material,
                "stock_scope": stock_scope,
                "engineering_occurrence_ids": sorted(member_ids),
                "component_definition_ids": sorted({member["component_definition_id"] for member in members}),
                "geometry_ids": sorted({member["geometry_id"] for member in members if member.get("geometry_id")}),
                "engineering_occurrence_count": len(member_ids),
                "known_gross_stock_mass_kg": None if gross_decimal is None else decimal_text(gross_decimal),
                "summed_member_accounted_mass_kg": None if member_mass_decimal is None else decimal_text(member_mass_decimal),
                "gross_mass_reconciliation_residual_kg": None if mass_residual is None else decimal_text(mass_residual, nonnegative=False),
                "nominal_stock_volume_m3": None if volume_decimal is None else decimal_text(volume_decimal),
                "purchased_stock_quantity": group.get("purchased_stock_quantity"),
                "purchase_unit": None,
                "yield_fraction": group.get("yield_fraction"),
                "labour_hours": None if labour_decimal is None else decimal_text(labour_decimal),
                "tooling": group.get("tooling"),
                "inspection_procedure": group.get("inspection_procedure"),
                "process_qualification": group.get("process_qualification"),
                "origin_country": group.get("origin_country"),
                "repair_and_removal_route": group.get("repair_and_removal_route"),
                "quantity_basis": "engineering gross-stock mass/nominal geometry; not order quantity or installed mass",
                "material_price": None,
                "direct_labour_cost": None,
                "uplift_amount": None,
                "complete_process_cost": None,
                "complete_installed_cost": None,
            }
            output_groups.append(item)

            acc = rollups[key]
            acc["group_count"] += 1
            acc["occurrence_count"] += len(member_ids)
            if gross_decimal is None:
                acc["mass_missing_group_count"] += 1
            else:
                acc["mass_sum_kg"] += gross_decimal
            if volume_decimal is None:
                acc["volume_missing_group_count"] += 1
            else:
                acc["volume_sum_m3"] += volume_decimal
            if labour_decimal is None:
                acc["labour_missing_group_count"] += 1
            else:
                acc["labour_sum_h"] += labour_decimal
            if mass_residual is not None:
                acc["gross_mass_reconciliation_max_abs_kg"] = max(
                    acc["gross_mass_reconciliation_max_abs_kg"], abs(mass_residual))

    located = {row_id for row_id, row in rows.items()
               if row.get("scope") != "unlocated-account-or-obligation"}
    if seen != located:
        raise ValueError("Takeoff does not preserve the complete located-occurrence partition")

    source_rows, benchmark_rows = _source_rows(catalogue_records)
    benchmark_series = {}
    wage_benchmark = benchmark_rows.get("iq-cso-2025:baghdad-wage:skilled:hour-8h-day")
    for key in _COMMODITY_BENCHMARKS.values():
        candidates = [row for row in benchmark_rows.values()
                      if row.get("series") == key and row.get("observation_date", "") <= as_of_date]
        if candidates:
            benchmark_series[key] = max(candidates, key=lambda row: (row["observation_date"], row["record_id"]))

    output_rollups = []
    total_known_gross_mass = Decimal(0)
    for key, acc in sorted(rollups.items()):
        system, material, stock_scope = key
        missing_mass = acc["mass_missing_group_count"]
        gross_mass = None if missing_mass else acc["mass_sum_kg"]
        total_known_gross_mass += acc["mass_sum_kg"]
        missing_volume = acc["volume_missing_group_count"]
        volume = None if missing_volume else acc["volume_sum_m3"]
        missing_labour = acc["labour_missing_group_count"]
        labour_hours = None if missing_labour else acc["labour_sum_h"]

        benchmark = None
        commodity_extension = None
        commodity_tonnes = None
        commodity_label = "no direct raw commodity benchmark mapped"
        series = _COMMODITY_BENCHMARKS.get(material)
        if series is not None and series in benchmark_series and gross_mass is not None:
            benchmark = benchmark_series[series]
            source = source_rows.get(benchmark["source_id"])
            commodity_tonnes = gross_mass / Decimal(1000)
            commodity_extension = commodity_tonnes * decimal(benchmark["unit_price"], "commodity benchmark")
            commodity_label = "raw commodity reference only; not a product match, purchasable order or process cost"

        output_rollups.append({
            "system": system,
            "material": material,
            "stock_scope": stock_scope,
            "manufacturing_group_count": acc["group_count"],
            "engineering_occurrence_count": acc["occurrence_count"],
            "known_gross_stock_mass_kg": None if gross_mass is None else decimal_text(gross_mass),
            "missing_gross_mass_group_count": missing_mass,
            "nominal_stock_volume_m3": None if volume is None else decimal_text(volume),
            "missing_nominal_stock_volume_group_count": missing_volume,
            "declared_labour_hours": None if labour_hours is None else decimal_text(labour_hours),
            "missing_labour_hours_group_count": missing_labour,
            "max_gross_mass_reconciliation_residual_kg": decimal_text(acc["gross_mass_reconciliation_max_abs_kg"]),
            "raw_commodity_reference": None if benchmark is None else {
                "benchmark_key": benchmark["benchmark_key"],
                "benchmark_id": benchmark["record_id"],
                "source_id": benchmark["source_id"],
                "publisher": None if source is None else source["publisher"],
                "source_url": None if source is None else source["url"],
                "observation_date": benchmark["observation_date"],
                "reference_quantity_t": decimal_text(commodity_tonnes),
                "reference_rate": benchmark["unit_price"],
                "currency": benchmark["currency"],
                "reference_extension": decimal_text(commodity_extension),
                "status": commodity_label,
            },
            "purchase_quantity": None,
            "purchase_unit": None,
            "direct_labour_cost": None,
            "domestic_fabrication_uplift_fraction": "0.20",
            "domestic_fabrication_uplift_amount": None,
            "complete_procurement_cost": None,
            "complete_installed_cost": None,
        })

    known_mass_groups = [group for group in output_groups if group["known_gross_stock_mass_kg"] is not None]
    total_occurrence_count = len(seen)
    result = {
        "schema": "osr-engineering-material-takeoff/1",
        "as_of": as_of_date,
        "candidate_id": candidate_id,
        "evaluation_id": payload["evaluation_id"],
        "source_input_id": twin_input["payload_id"],
        "selection_id": payload.get("selection_id"),
        "input_origin": twin_input.get("origin"),
        "input_provenance": {
            "input_schema": payload["schema"],
            "input_payload_id": twin_input["payload_id"],
            "engineering_occurrence_count": len(occurrences),
            "located_occurrence_count": total_occurrence_count,
            "unlocated_account_count": len(unlocated),
            "manufacturing_group_count": len(groups),
            "all_located_occurrences_partitioned_once": True,
        },
        "summary": {
            "known_gross_stock_mass_kg": decimal_text(total_known_gross_mass),
            "groups_with_known_gross_stock_mass": len(known_mass_groups),
            "gross_mass_missing_group_count": len(output_groups) - len(known_mass_groups),
            "located_occurrence_count": total_occurrence_count,
            "unlocated_account_count": len(unlocated),
            "complete_installed_mass_kg": None,
            "complete_installed_cost": None,
            "whole_life_cost": None,
        },
        "currency_reference": {
            "commodity_benchmarks_are_not_supplier_quotes": True,
            "labour_rate_benchmark": None if wage_benchmark is None else {
                "benchmark_key": wage_benchmark["benchmark_key"],
                "benchmark_id": wage_benchmark["record_id"],
                "source_id": wage_benchmark["source_id"],
                "publisher": source_rows.get(wage_benchmark["source_id"], {}).get("publisher"),
                "source_url": source_rows.get(wage_benchmark["source_id"], {}).get("url"),
                "observation_date": wage_benchmark["observation_date"],
                "unit_rate": wage_benchmark["unit_price"],
                "quantity_unit": wage_benchmark["quantity_unit"],
                "currency": wage_benchmark["currency"],
                "normalization_basis": wage_benchmark.get("normalization_basis"),
                "cost_scope": wage_benchmark.get("cost_scope"),
                "applied_to_groups": False,
            },
            "labour_hours_known_for_groups": sum(group["labour_hours"] is not None for group in output_groups),
            "labour_hours_missing_for_groups": sum(group["labour_hours"] is None for group in output_groups),
            "uplift_fraction": "0.20",
            "uplift_formula": "(source-priced material + declared direct labour) × (1 + 0.20)",
            "uplift_is_applied": False,
            "uplift_hold_reason": "Candidate manufacturing-group labour hours and compatible purchasing/form quantities are not declared; commodity references are not product prices.",
        },
        "material_rollups": output_rollups,
        "manufacturing_groups": sorted(output_groups, key=lambda row: row["engineering_group_key"]),
        "evidence_boundary": {
            "gross_stock_mass_is_installed_mass": False,
            "nominal_stock_volume_is_purchasing_quantity": False,
            "commodity_reference_is_compatible_offer": False,
            "physical_acceptance": False,
            "engineering_acceptance": False,
            "procurement_approval": False,
            "manufacturing_release": False,
            "selected_reference_changed": False,
            "unknown_is_zero": False,
        },
    }
    result["catalogue_record_set_id"] = identity(sorted(catalogue_records, key=lambda row: row["record_id"]))
    result["takeoff_id"] = identity(result)
    return result
