"""Generate source-linked Iraqi regional domestic-fabrication cost screens.

This module combines published material/wage benchmarks with explicit work-hour
recipes.  Its reports preserve candidate and takeoff identities but never claim
supplier offers, completed processes, installed cost, or physical acceptance.
"""
from argparse import ArgumentParser
from copy import deepcopy
from pathlib import Path
import json
import sys

from . import catalogue, inputs
from .fabrication import domestic_fabrication_estimate, domestic_fabrication_takeoff_estimate
from .model import encoded, identity

ROOT = Path(__file__).resolve().parents[2]
REGIONS = (
    ("nineveh", "Nineveh"), ("kirkuk", "Kirkuk"), ("diyala", "Diyala"),
    ("anbar", "Anbar"), ("baghdad", "Baghdad"), ("babil", "Babil"),
    ("karbala", "Karbala"), ("wasit", "Wasit"),
    ("salah-al-din", "Salah al-Din"), ("najaf", "Najaf"),
    ("al-qadisiyyah", "Al-Qadisiyyah"), ("al-muthanna", "Al-Muthanna"),
    ("dhi-qar", "Dhi Qar"), ("maysan", "Maysan"), ("basrah", "Basrah"),
)
CONCRETE_HOURS = ("2", "4", "8")
REBAR_HOURS = ("4", "8", "16")
ALUMINIUM_HOURS = ("8", "16", "32")
UR_ALUMINIUM_PROFILE_FORMS = (
    ("Non-oxidized aluminium profiles", "iq-ur-page-observation-2026-10-29:profile-non-oxidized"),
    ("Oxidized aluminium profiles", "iq-ur-page-observation-2026-10-29:profile-oxidized"),
    ("Spray-painted aluminium profiles", "iq-ur-page-observation-2026-10-29:profile-spray-painted"),
)
UR_ALUMINIUM_SHEET_FORMS = (
    ("Hard aluminium sheet, 0.6–0.9 mm", "iq-ur-page-observation-2026-10-29:sheet-hard-0.6-0.9mm"),
    ("Hard aluminium sheet, 1 mm and above", "iq-ur-page-observation-2026-10-29:sheet-hard-1mm-plus"),
    ("Annealed aluminium sheet, 0.6–0.9 mm", "iq-ur-page-observation-2026-10-29:sheet-annealed-0.6-0.9mm"),
    ("Annealed aluminium sheet, 1 mm and above", "iq-ur-page-observation-2026-10-29:sheet-annealed-1mm-plus"),
)
CONCRETE_MATERIALS = (
    ("Ordinary Iraqi cement; illustrative quantity per nominal m3", "0.35", "t", "cement-ordinary"),
    ("Red sand; illustrative quantity per nominal m3", "0.50", "m3", "sand-red"),
    ("Crushed gravel; illustrative quantity per nominal m3", "0.80", "m3", "gravel-crushed"),
)


def _benchmark_index(records):
    return {record["benchmark_key"]: record for record in records if record["kind"] == "benchmark"}


def _source_index(records):
    return {record["source_key"]: record for record in records if record["kind"] == "source"}


def _must_benchmark(index, key):
    value = index.get(key)
    if value is None:
        return None
    if value.get("is_manufactured_product_price") is not False:
        raise ValueError("Cost screen requires statistical/material benchmarks, not a supplier offer")
    return value


def _unit_rate_process(*, estimate_key, candidate_id, input_id, output_quantity,
                       output_unit, material_lines, labour_category, hours,
                       wage_benchmark, used_benchmarks):
    wage = wage_benchmark
    selected = {value["record_id"]: value for value in used_benchmarks.values()
                if value is not None}
    if wage is None:
        raise ValueError("Exact regional wage benchmark is missing")
    labor_line = dict(labour_category=labour_category, person_hours=hours,
                      benchmark_id=wage["record_id"])
    selected[wage["record_id"]] = wage
    return domestic_fabrication_estimate(
        estimate_key=estimate_key, candidate_id=candidate_id, input_id=input_id,
        output_quantity=output_quantity, output_unit=output_unit, currency="IQD",
        material_lines=material_lines, labour_lines=[labor_line],
        benchmarks=selected, uplift_fraction="0.20")


def _make_packet(records, takeoff, takeoff_path):
    benchmarks = _benchmark_index(records)
    source_records = _source_index(records)
    candidate_id = takeoff["candidate_id"]
    input_id = takeoff["source_input_id"]
    regional = []
    missing = []

    for region_slug, region_name in REGIONS:
        wage_key = f"iq-cso-2025-regional:{region_slug}:wage:skilled:hour-8h-day"
        wage = _must_benchmark(benchmarks, wage_key)
        concrete_materials = []
        concrete_selected = {}
        absent = []
        for label, quantity, unit, material_key in CONCRETE_MATERIALS:
            key = f"iq-cso-2025-regional:{region_slug}:material:{material_key}"
            benchmark = _must_benchmark(benchmarks, key)
            if benchmark is None:
                absent.append(key)
                continue
            concrete_selected[key] = benchmark
            concrete_materials.append(dict(material_key=label, quantity=quantity,
                                           quantity_unit=unit,
                                           benchmark_id=benchmark["record_id"]))
        if absent or wage is None:
            missing.append(dict(region=region_name, material_family="concrete batching",
                                unavailable_benchmark_keys=absent + ([wage_key] if wage is None else []),
                                explanation="A source-table zero/absent rate remains unknown; no estimate is emitted."))
        else:
            for hours in CONCRETE_HOURS:
                process = _unit_rate_process(
                    estimate_key=f"iraq-2025-{region_slug}-concrete-{hours}h-per-nominal-m3",
                    candidate_id=candidate_id, input_id=input_id,
                    output_quantity="1", output_unit="m3",
                    material_lines=deepcopy(concrete_materials),
                    labour_category=f"{region_name} skilled construction-worker base wage; recipe scenario",
                    hours=hours, wage_benchmark=wage,
                    used_benchmarks=concrete_selected)
                regional.append(dict(region=region_name, family="concrete batching",
                                     output_quantity="1", output_unit="nominal m3",
                                     labour_hours_per_output=hours, process=process))

        rebar_key = f"iq-cso-2025-regional:{region_slug}:material:rebar"
        rebar = _must_benchmark(benchmarks, rebar_key)
        if rebar is None or wage is None:
            missing.append(dict(region=region_name, material_family="rebar cut/bend",
                                unavailable_benchmark_keys=([rebar_key] if rebar is None else []) +
                                    ([wage_key] if wage is None else []),
                                explanation="A source-table zero/absent rate remains unknown; no estimate is emitted."))
        else:
            for hours in REBAR_HOURS:
                process = _unit_rate_process(
                    estimate_key=f"iraq-2025-{region_slug}-rebar-cut-bend-{hours}h-per-t",
                    candidate_id=candidate_id, input_id=input_id,
                    output_quantity="1", output_unit="t",
                    material_lines=[dict(material_key="Iraqi-origin rebar market statistic; grade and diameter unresolved",
                                         quantity="1", quantity_unit="t",
                                         benchmark_id=rebar["record_id"])],
                    labour_category=f"{region_name} skilled construction-worker base wage; recipe scenario",
                    hours=hours, wage_benchmark=wage,
                    used_benchmarks={rebar_key: rebar})
                regional.append(dict(region=region_name, family="rebar cut/bend",
                                     output_quantity="1", output_unit="input tonne",
                                     labour_hours_per_output=hours, process=process))

    # The Ur producer's posted profile and sheet rates are local-market leads.
    # The 2025 Baghdad wage is used as a base-wage proxy; the posted products'
    # alloy/temper, availability, delivery terms and factory routes are unknown.
    baghdad_wage_key = "iq-cso-2025-regional:baghdad:wage:skilled:hour-8h-day"
    baghdad_wage = _must_benchmark(benchmarks, baghdad_wage_key)
    if baghdad_wage is None:
        missing.append(dict(region="Baghdad", material_family="aluminium profile and sheet processing",
                            unavailable_benchmark_keys=[baghdad_wage_key],
                            explanation="The regional wage observation is absent; no fabrication scenarios are emitted."))
    else:
        for form_name, profile_key in UR_ALUMINIUM_PROFILE_FORMS:
            ur_profile = _must_benchmark(benchmarks, profile_key)
            if ur_profile is None:
                missing.append(dict(region="Baghdad", material_family=form_name,
                                    unavailable_benchmark_keys=[profile_key],
                                    explanation="The Ur Company profile observation is absent; no estimate is emitted."))
                continue
            for hours in ALUMINIUM_HOURS:
                process = _unit_rate_process(
                    estimate_key=("iraq-2026-baghdad-aluminium-profile-processing-" +
                                  profile_key.rsplit(":", 1)[-1] + f"-{hours}h-per-t"),
                    candidate_id=candidate_id, input_id=input_id,
                    output_quantity="1", output_unit="t",
                    material_lines=[dict(
                        material_key=f"Ur Company posted {form_name}; alloy/temper unverified",
                        quantity="1", quantity_unit="t",
                        benchmark_id=ur_profile["record_id"])],
                    labour_category="Baghdad skilled-worker base wage proxy; unmeasured profile-processing scenario",
                    hours=hours, wage_benchmark=baghdad_wage,
                    used_benchmarks={profile_key: ur_profile})
                regional.append(dict(region="Baghdad", family="aluminium profile processing",
                                     material_form=form_name,
                                     output_quantity="1", output_unit="profile input tonne",
                                     labour_hours_per_output=hours, process=process))

    if baghdad_wage is not None:
        for form_name, sheet_key in UR_ALUMINIUM_SHEET_FORMS:
            sheet_benchmark = _must_benchmark(benchmarks, sheet_key)
            if sheet_benchmark is None:
                missing.append(dict(region="Baghdad", material_family=form_name,
                                    unavailable_benchmark_keys=[sheet_key],
                                    explanation="The Ur Company sheet observation is absent; no estimate is emitted."))
                continue
            for hours in ALUMINIUM_HOURS:
                process = _unit_rate_process(
                    estimate_key=("iraq-2026-baghdad-aluminium-sheet-processing-" +
                                  sheet_key.rsplit(":", 1)[-1] + f"-{hours}h-per-t"),
                    candidate_id=candidate_id, input_id=input_id,
                    output_quantity="1", output_unit="t",
                    material_lines=[dict(
                        material_key=f"Ur Company posted {form_name}; alloy/temper unverified",
                        quantity="1", quantity_unit="t",
                        benchmark_id=sheet_benchmark["record_id"])],
                    labour_category="Baghdad skilled-worker base wage proxy; unmeasured sheet-processing scenario",
                    hours=hours, wage_benchmark=baghdad_wage,
                    used_benchmarks={sheet_key: sheet_benchmark})
                regional.append(dict(region="Baghdad", family="aluminium sheet processing",
                                     material_form=form_name,
                                     output_quantity="1", output_unit="sheet input tonne",
                                     labour_hours_per_output=hours, process=process))

    mapped_processes = []
    for hours in CONCRETE_HOURS:
        concrete_lines = []
        selected = {}
        for label, quantity, unit, material_key in CONCRETE_MATERIALS:
            key = f"iq-cso-2025-regional:baghdad:material:{material_key}"
            benchmark = _must_benchmark(benchmarks, key)
            if benchmark is None:
                raise ValueError("Baghdad concrete takeoff recipe needs a missing exact benchmark: " + key)
            selected[benchmark["record_id"]] = benchmark
            concrete_lines.append(dict(material_key=label, quantity=quantity,
                                       quantity_unit=unit, benchmark_id=benchmark["record_id"]))
        wage = _must_benchmark(benchmarks, baghdad_wage_key)
        selected[wage["record_id"]] = wage
        process = domestic_fabrication_takeoff_estimate(
            estimate_key=f"iraq-2025-baghdad-federated-concrete-takeoff-{hours}h-per-m3",
            takeoff=takeoff,
            target_rollup={"system": "civil/concrete", "material": "concrete-hypothesis",
                           "stock_scope": "nominal-stock"},
            recipe_output_quantity="1", currency="IQD",
            material_lines=concrete_lines,
            labour_lines=[dict(labour_category="Baghdad skilled-worker base wage; recipe scenario",
                               person_hours=hours, benchmark_id=wage["record_id"])],
            benchmarks=selected, uplift_fraction="0.20")
        mapped_processes.append(dict(labour_hours_per_nominal_m3=hours, process=process))

    takeoff_file = Path(takeoff_path).resolve()
    source_hashes = {
        "engineering/sourcing/iraq_cost_scenarios.py": inputs.digest(Path(__file__)),
        "engineering/sourcing/fabrication.py": inputs.digest(ROOT / "engineering/sourcing/fabrication.py"),
        "engineering/sourcing/model.py": inputs.digest(ROOT / "engineering/sourcing/model.py"),
        "engineering/sourcing/catalogue.py": inputs.digest(ROOT / "engineering/sourcing/catalogue.py"),
        "engineering/sourcing/data/supplier-catalogue.json": inputs.digest(ROOT / "engineering/sourcing/data/supplier-catalogue.json"),
        "engineering/sourcing/data/public-feeds.json": inputs.digest(ROOT / "engineering/sourcing/data/public-feeds.json"),
        "engineering/sourcing/data/iraq-domestic-2026-july.json": inputs.digest(ROOT / "engineering/sourcing/data/iraq-domestic-2026-july.json"),
        "takeoff_file": inputs.digest(takeoff_file),
    }
    source_id = source_records["iraq.cso.regional-materials-wages-2025"]["record_id"]
    takeoff_packets = []
    mapped = []
    for scenario in mapped_processes:
        process = scenario["process"]
        hours = scenario["labour_hours_per_nominal_m3"]
        estimate_packet = dict(
            schema="osr-domestic-fabrication-takeoff-estimate/1",
            candidate_id=takeoff["candidate_id"], source_input_id=takeoff["source_input_id"],
            takeoff_id=takeoff["takeoff_id"], source_ids=process["source_ids"],
            source_sha256=source_hashes, estimate=process,
            candidate_takeoff_mapped=True, complete_procurement_cost=None,
            complete_installed_cost=None, whole_life_cost=None,
            physical_qualification=None, engineering_accepted=False,
            procurement_approved=False, selected_reference_changed=False,
            unknown_is_zero=False)
        estimate_packet["estimate_packet_id"] = identity(estimate_packet)
        takeoff_packets.append((hours, estimate_packet))
        mapped.append(dict(
            labour_hours_per_nominal_m3=hours,
            estimate_packet_id=estimate_packet["estimate_packet_id"],
            process_record_id=process["record_id"],
            candidate_id=process["candidate_id"],
            source_input_id=process["input_id"],
            estimated_unit_cost_iqd_per_nominal_m3=process["estimated_unit_cost"],
            estimated_total_iqd=process["estimated_total"],
            mapped_group_count=process["candidate_takeoff_group_count"],
            mapped_occurrence_count=process["candidate_takeoff_occurrence_count"]))
    packet = dict(
        schema="osr-iraq-domestic-cost-reference/1",
        candidate_id=candidate_id, source_input_id=input_id,
        takeoff_id=takeoff["takeoff_id"],
        source_ids=sorted({source_id, source_records["iraq.ur.company-prices"]["record_id"]}),
        source_sha256=source_hashes,
        basis={
            "formula":"(material quantity x source rate + person-hours x hourly base wage) x 1.20",
            "uplift_fraction":"0.20",
            "uplift_scope":"direct materials plus direct labour only; composition of the allowance is unspecified",
            "concrete_recipe_per_nominal_m3":{
                "ordinary_cement_t":"0.35", "red_sand_m3":"0.50", "crushed_gravel_m3":"0.80"},
            "concrete_labour_scenarios_h_per_nominal_m3":["2","4","8"],
            "rebar_labour_scenarios_h_per_input_tonne":["4","8","16"],
            "aluminium_labour_scenarios_h_per_profile_input_tonne":["8","16","32"],
            "aluminium_profile_forms": [name for name, _key in UR_ALUMINIUM_PROFILE_FORMS],
            "aluminium_sheet_forms": [name for name, _key in UR_ALUMINIUM_SHEET_FORMS],
            "aluminium_sheet_labour_scenarios_h_per_input_tonne":["8","16","32"],
            "wage_normalization":"CSO daily average divided by an explicit 8-hour working day",
            "zero_source_observations":"treated as unavailable; no price or estimate is emitted",
            "regional_coverage":"15 governorates listed in the CSO bulletin; 12 have all inputs for the illustrative concrete recipe",
        },
        unit_rate_estimates=regional,
        unavailable_estimates=missing,
        baghdad_concrete_takeoff_estimates=mapped,
        candidate_takeoff_mapped_for_unit_rate_estimates=False,
        takeoff_mapped_for_baghdad_concrete_estimates=True,
        complete_procurement_cost=None, complete_process_cost=None,
        complete_installed_cost=None, whole_life_cost=None,
        physical_qualification=None, engineering_accepted=False,
        procurement_approved=False, selected_reference_changed=False,
        unknown_is_zero=False,
        limitations=[
            "The CSO rates are statistical annual market/wage observations, not supplier quotations or employer-loaded shop rates.",
            "The 0.35 t cement + 0.50 m3 red sand + 0.80 m3 crushed gravel recipe is an illustrative takeoff basis, not a mix design or a verified one-cubic-metre yield.",
            "The hour values are sensitivity scenarios, not timed local factory routes.",
            "The Baghdad takeoff applies its declared unit recipe to nominal concrete geometry while preserving the 81 group and 486 occurrence identities; it does not price complete beams, reinforcement, prestress, moulds, QA, transport, foundations, installation or maintenance.",
            "The Ur Company profile and sheet observations do not state structural alloy/temper, effective date, availability, quantity, delivery, tax, yield or installation basis; the aluminium screens are raw-stock plus assumed labour sensitivities, not a body-frame price, completed process route or approved design.",
            "The 20% uplift is an unallocated planning allowance and is not verified overhead, profit, tax or contingency.",
        ])
    packet["source_epoch_id"] = identity(records)
    packet["packet_id"] = identity(packet)
    return packet, takeoff_packets


def _make_2026_july_reference(records, takeoff, takeoff_path):
    """Build same-period Iraq-origin material and governorate-wage scenarios.

    Material prices are the CSO's national-market Iraqi-origin row for July 2026;
    wages are the same bulletin's governorate-specific daily observations divided
    by an explicit eight-hour workday. Candidate takeoff estimates are emitted
    only for Baghdad and Al-Muthanna as transparent location comparisons; the
    railway route/location is not selected by this report.
    """
    benchmarks = _benchmark_index(records)
    source_records = _source_index(records)
    source = source_records.get("iraq.cso.regional-materials-wages-2026-07")
    if source is None:
        raise ValueError("Exact July 2026 CSO source record is required")

    material_map = (
        ("Ordinary Iraqi-origin cement", "0.35", "t", "cement-ordinary"),
        ("Iraqi-origin red sand", "0.50", "m3", "sand-red"),
        ("Iraqi-origin crushed gravel", "0.80", "m3", "gravel-crushed"),
    )
    concrete_keys = [f"iq-cso-2026-07:iraq-origin:material:{suffix}"
                     for _label, _quantity, _unit, suffix in material_map]
    concrete_rows = [_must_benchmark(benchmarks, key) for key in concrete_keys]
    if any(row is None for row in concrete_rows):
        raise ValueError("July 2026 CSO Iraqi-origin concrete material observations are incomplete")
    rebar_key = "iq-cso-2026-07:iraq-origin:material:rebar"
    rebar = _must_benchmark(benchmarks, rebar_key)
    if rebar is None:
        raise ValueError("July 2026 CSO Iraqi-origin rebar observation is missing")

    regional = []
    selected_by_region = {}
    for region_slug, region_name in REGIONS:
        wage_key = f"iq-cso-2026-07:{region_slug}:wage:skilled:hour-8h-day"
        wage = _must_benchmark(benchmarks, wage_key)
        if wage is None:
            raise ValueError("July 2026 regional skilled-wage observation is missing: " + wage_key)
        selected_by_region[region_slug] = wage
        selected_concrete = {row["record_id"]: row for row in concrete_rows}
        selected_concrete[wage["record_id"]] = wage
        concrete_lines = [dict(material_key=label, quantity=quantity,
                               quantity_unit=unit, benchmark_id=row["record_id"])
                          for (label, quantity, unit, _suffix), row
                          in zip(material_map, concrete_rows)]
        for hours in CONCRETE_HOURS:
            process = _unit_rate_process(
                estimate_key=f"iraq-2026-07-{region_slug}-concrete-{hours}h-per-nominal-m3",
                candidate_id=takeoff["candidate_id"], input_id=takeoff["source_input_id"],
                output_quantity="1", output_unit="m3",
                material_lines=deepcopy(concrete_lines),
                labour_category=f"{region_name} CSO skilled-worker base wage; July 2026 scenario",
                hours=hours, wage_benchmark=wage, used_benchmarks=selected_concrete)
            regional.append(dict(region=region_name, region_slug=region_slug,
                                 family="concrete batching", output_quantity="1",
                                 output_unit="nominal m3", labour_category="skilled",
                                 labour_hours_per_output=hours, process=process))

        selected_rebar = {rebar["record_id"]: rebar, wage["record_id"]: wage}
        for hours in REBAR_HOURS:
            process = _unit_rate_process(
                estimate_key=f"iraq-2026-07-{region_slug}-rebar-cut-bend-{hours}h-per-input-t",
                candidate_id=takeoff["candidate_id"], input_id=takeoff["source_input_id"],
                output_quantity="1", output_unit="t",
                material_lines=[dict(
                    material_key="Iraqi-origin July 2026 CSO reinforcing-bar statistic; grade/diameter unresolved",
                    quantity="1", quantity_unit="t", benchmark_id=rebar["record_id"])],
                labour_category=f"{region_name} CSO skilled-worker base wage; July 2026 scenario",
                hours=hours, wage_benchmark=wage, used_benchmarks=selected_rebar)
            regional.append(dict(region=region_name, region_slug=region_slug,
                                 family="rebar cut/bend", output_quantity="1",
                                 output_unit="input tonne", labour_category="skilled",
                                 labour_hours_per_output=hours, process=process))

    takeoff_file = Path(takeoff_path).resolve()
    source_hashes = {
        "engineering/sourcing/iraq_cost_scenarios.py": inputs.digest(Path(__file__)),
        "engineering/sourcing/fabrication.py": inputs.digest(ROOT / "engineering/sourcing/fabrication.py"),
        "engineering/sourcing/model.py": inputs.digest(ROOT / "engineering/sourcing/model.py"),
        "engineering/sourcing/catalogue.py": inputs.digest(ROOT / "engineering/sourcing/catalogue.py"),
        "engineering/sourcing/data/supplier-catalogue.json": inputs.digest(ROOT / "engineering/sourcing/data/supplier-catalogue.json"),
        "engineering/sourcing/data/public-feeds.json": inputs.digest(ROOT / "engineering/sourcing/data/public-feeds.json"),
        "engineering/sourcing/data/iraq-domestic-2026-july.json": inputs.digest(ROOT / "engineering/sourcing/data/iraq-domestic-2026-july.json"),
        "takeoff_file": inputs.digest(takeoff_file),
    }

    takeoff_estimates = []
    mapped_packets = []
    for region_slug in ("baghdad", "al-muthanna"):
        region_name = dict(REGIONS)[region_slug]
        wage = selected_by_region[region_slug]
        selected = {row["record_id"]: row for row in concrete_rows}
        selected[wage["record_id"]] = wage
        material_lines = [dict(material_key=label, quantity=quantity,
                               quantity_unit=unit, benchmark_id=row["record_id"])
                          for (label, quantity, unit, _suffix), row
                          in zip(material_map, concrete_rows)]
        for hours in CONCRETE_HOURS:
            process = domestic_fabrication_takeoff_estimate(
                estimate_key=f"iraq-2026-07-{region_slug}-federated-concrete-takeoff-{hours}h-per-m3",
                takeoff=takeoff,
                target_rollup={"system": "civil/concrete", "material": "concrete-hypothesis",
                               "stock_scope": "nominal-stock"},
                recipe_output_quantity="1", currency="IQD",
                material_lines=material_lines,
                labour_lines=[dict(
                    labour_category=f"{region_name} CSO skilled-worker base wage; July 2026 scenario",
                    person_hours=hours, benchmark_id=wage["record_id"])],
                benchmarks=selected, uplift_fraction="0.20")
            estimate_packet = dict(
                schema="osr-domestic-fabrication-takeoff-estimate/1",
                candidate_id=takeoff["candidate_id"], source_input_id=takeoff["source_input_id"],
                takeoff_id=takeoff["takeoff_id"], source_ids=process["source_ids"],
                source_sha256=source_hashes, estimate=process,
                candidate_takeoff_mapped=True, complete_procurement_cost=None,
                complete_installed_cost=None, whole_life_cost=None,
                physical_qualification=None, engineering_accepted=False,
                procurement_approved=False, selected_reference_changed=False,
                unknown_is_zero=False)
            estimate_packet["estimate_packet_id"] = identity(estimate_packet)
            filename = f"2026-07-{region_slug}-concrete-takeoff-{hours}h.json"
            row = dict(region=region_name, region_slug=region_slug,
                       labour_hours_per_nominal_m3=hours,
                       estimate_packet_id=estimate_packet["estimate_packet_id"],
                       process_record_id=process["record_id"],
                       estimate_file=filename,
                       estimated_unit_cost_iqd_per_nominal_m3=process["estimated_unit_cost"],
                       estimated_total_iqd=process["estimated_total"],
                       mapped_group_count=process["candidate_takeoff_group_count"],
                       mapped_occurrence_count=process["candidate_takeoff_occurrence_count"],
                       basis=f"CSO July 2026 national Iraqi-origin materials plus {region_name} governorate skilled base wage; 20% on direct material plus labour")
            takeoff_estimates.append(row)
            mapped_packets.append((region_name, hours, estimate_packet))

    baghdad_rows = [row for row in takeoff_estimates if row["region_slug"] == "baghdad"]
    packet = dict(
        schema="osr-iraq-domestic-cost-reference/2",
        candidate_id=takeoff["candidate_id"], source_input_id=takeoff["source_input_id"],
        takeoff_id=takeoff["takeoff_id"], source_ids=[source["record_id"]],
        source_sha256=source_hashes,
        basis={
            "formula":"(material quantity x source rate + person-hours x hourly base wage) x 1.20",
            "uplift_fraction":"0.20",
            "uplift_scope":"direct materials plus direct labour only; composition of the allowance is unspecified",
            "concrete_recipe_per_nominal_m3":{"ordinary_iraqi_origin_cement_t":"0.35",
                "iraqi_origin_red_sand_m3":"0.50","iraqi_origin_crushed_gravel_m3":"0.80"},
            "labour_hours_scenarios_per_nominal_m3":list(CONCRETE_HOURS),
            "rebar_labour_hours_scenarios_per_input_tonne":list(REBAR_HOURS),
            "material_source_basis":"CSO July 2026 national-market Iraqi-origin rows; not governorate-specific and not supplier quotes",
            "wage_source_basis":"CSO July 2026 governorate worker daily rate divided by explicit 8-hour workday; excludes employer burden",
            "candidate_takeoff_regions":["Baghdad","Al-Muthanna"],
            "candidate_takeoff_region_selection":"Comparison scenarios only; the candidate route and factory location are not selected",
        },
        unit_rate_estimates=regional,
        material_origin_comparisons=[
            {"material_family":family,"origin_class":origin,"benchmark_key":row["benchmark_key"],
             "unit_price_iqd":row["unit_price"],"quantity_unit":row["quantity_unit"],
             "source_id":row["source_id"],"supplier_quote":False}
            for row in records if row["kind"]=="benchmark"
            and row.get("benchmark_key","").startswith("iq-cso-2026-07:")
            and row.get("source_origin_class") is not None
            for _prefix, origin, _material, family in [row["benchmark_key"].split(":",3)]
        ],
        regional_concrete_takeoff_estimates=takeoff_estimates,
        baghdad_concrete_takeoff_estimates=baghdad_rows,
        takeoff_mapped_for_baghdad_concrete_estimates=True,
        takeoff_mapped_for_regional_concrete_estimates=True,
        candidate_takeoff_mapped_for_unit_rate_estimates=False,
        complete_procurement_cost=None, complete_process_cost=None,
        complete_installed_cost=None, whole_life_cost=None,
        physical_qualification=None, engineering_accepted=False,
        procurement_approved=False, selected_reference_changed=False,
        unknown_is_zero=False,
        limitations=[
            "CSO material values are national-market statistical rates broken out by reported origin; they are not governorate-specific delivered rates, exact grade quotations or installed prices.",
            "Worker wage values are per-person daily base averages normalized to an assumed 8-hour day; employer burden, overtime, shifts, training and shop charge-out costs are unknown.",
            "The one nominal-m3 concrete recipe and 2/4/8-hour labour scenarios are declared sensitivity assumptions, not a designed mix, verified yield or timed factory route.",
            "The candidate takeoff comparison applies the same declared recipe to 81 concrete manufacturing groups and 486 engineering occurrences in two location/wage scenarios. It does not establish the route or plant location, price reinforcement/prestress, moulds, QA, transport, foundations, installation, maintenance or a complete beam.",
            "Rebar cut/bend unit scenarios are not mapped to candidate reinforcement quantities because those quantities remain unresolved.",
            "Steel I-beam and aluminium-window benchmarks are construction-market item averages; section geometry, alloy, exact product scope and railway compatibility remain unresolved and are not used as prices for the selected rail/body stocks.",
            "The 20% uplift is an unallocated planning allowance on declared direct material plus labour; it is not verified overhead, profit, tax or contingency.",
        ])
    packet["source_epoch_id"] = identity(records)
    packet["packet_id"] = identity(packet)
    return packet, mapped_packets


def _make_2024_material_crosscheck(records, takeoff, takeoff_path):
    """Compare the 2024 CSO estimated building-material basis with 2025 inputs.

    This deliberately produces a separate historical packet: the 2024 report is
    an estimated construction-use/cost ratio, not a transaction series. Labour
    stays on the 2025 Baghdad CSO wage basis so the two material scenarios can
    be compared at identical assumed hours.
    """
    benchmarks = _benchmark_index(records)
    source_records = _source_index(records)
    current_source = "iraq.cso.private-construction-estimates-2024"
    wage_key = "iq-cso-2025-regional:baghdad:wage:skilled:hour-8h-day"
    wage = _must_benchmark(benchmarks, wage_key)
    if wage is None:
        raise ValueError("Historical cross-check requires the exact 2025 Baghdad wage benchmark")

    material_map = (
        ("Ordinary cement", "cement-ordinary", "0.35", "t",
         "iq-cso-2025-regional:baghdad:material:cement-ordinary"),
        ("Red sand", "sand-red", "0.50", "m3",
         "iq-cso-2025-regional:baghdad:material:sand-red"),
        ("2024 normal grit / 2025 crushed gravel; grading correspondence unverified",
         "grit-normal", "0.80", "m3",
         "iq-cso-2025-regional:baghdad:material:gravel-crushed"),
    )
    historical_lines = []
    current_lines = []
    selected_historical = {wage["record_id"]: wage}
    selected_current = {wage["record_id"]: wage}
    rate_comparisons = []
    for label, suffix, quantity, unit, current_key in material_map:
        historical_key = f"iq-cso-2024-private-building-estimate:baghdad:{suffix}"
        historical = _must_benchmark(benchmarks, historical_key)
        if historical is None:
            raise ValueError("Historical CSO source benchmark is missing: " + historical_key)
        if historical["quantity_unit"] != unit:
            raise ValueError("Historical CSO material quantity unit differs: " + historical_key)
        historical_lines.append(dict(material_key=label + "; 2024 estimated-building ratio",
                                     quantity=quantity, quantity_unit=unit,
                                     benchmark_id=historical["record_id"]))
        selected_historical[historical["record_id"]] = historical

        comparison = dict(material=label, quantity_unit=unit,
                          historical_2024_baghdad=dict(
                              benchmark_id=historical["record_id"],
                              unit_rate_iqd=historical["unit_price"],
                              estimated_table_cost_thousand_iqd=historical["source_table_estimated_cost_thousand_iqd"],
                              estimated_table_quantity=historical["source_table_estimated_quantity"]))
        if current_key is not None:
            current = _must_benchmark(benchmarks, current_key)
            if current is not None:
                if current["quantity_unit"] != unit:
                    raise ValueError("2025 CSO material quantity unit differs: " + current_key)
                current_lines.append(dict(material_key=label + "; 2025 CSO annual market benchmark",
                                          quantity=quantity, quantity_unit=unit,
                                          benchmark_id=current["record_id"]))
                selected_current[current["record_id"]] = current
                comparison["annual_2025_baghdad"] = dict(
                    benchmark_id=current["record_id"], unit_rate_iqd=current["unit_price"],
                    product_scope_correspondence=("not established; 2024 normal grit is not proven equivalent to 2025 crushed gravel"
                                                  if suffix == "grit-normal" else "material names and units align; grade remains unspecified"))
        rate_comparisons.append(comparison)

    # The 2024 and 2025 building ratios use unlike methods and sample bases. The
    # side-by-side cost screens hold the 2025 wage and assumed work hours fixed.
    historical_scenarios = []
    current_scenarios = []
    for hours in CONCRETE_HOURS:
        historical_process = domestic_fabrication_estimate(
            estimate_key=f"iraq-historical-2024-materials-baghdad-concrete-{hours}h",
            candidate_id=takeoff["candidate_id"], input_id=takeoff["source_input_id"],
            output_quantity="1", output_unit="m3", currency="IQD",
            material_lines=deepcopy(historical_lines),
            labour_lines=[dict(labour_category="2025 Baghdad skilled construction-worker base wage proxy",
                               person_hours=hours, benchmark_id=wage["record_id"])],
            benchmarks=selected_historical, uplift_fraction="0.20")
        current_process = domestic_fabrication_estimate(
            estimate_key=f"iraq-2025-materials-baghdad-concrete-{hours}h",
            candidate_id=takeoff["candidate_id"], input_id=takeoff["source_input_id"],
            output_quantity="1", output_unit="m3", currency="IQD",
            material_lines=deepcopy(current_lines),
            labour_lines=[dict(labour_category="2025 Baghdad skilled construction-worker base wage proxy",
                               person_hours=hours, benchmark_id=wage["record_id"])],
            benchmarks=selected_current, uplift_fraction="0.20")
        historical_scenarios.append(dict(labour_hours_per_nominal_m3=hours,
                                         process=historical_process))
        current_scenarios.append(dict(labour_hours_per_nominal_m3=hours,
                                      process=current_process))

    takeoff_file = Path(takeoff_path).resolve()
    source_hashes = {
        "engineering/sourcing/iraq_cost_scenarios.py": inputs.digest(Path(__file__)),
        "engineering/sourcing/fabrication.py": inputs.digest(ROOT / "engineering/sourcing/fabrication.py"),
        "engineering/sourcing/model.py": inputs.digest(ROOT / "engineering/sourcing/model.py"),
        "engineering/sourcing/catalogue.py": inputs.digest(ROOT / "engineering/sourcing/catalogue.py"),
        "engineering/sourcing/data/supplier-catalogue.json": inputs.digest(ROOT / "engineering/sourcing/data/supplier-catalogue.json"),
        "engineering/sourcing/data/public-feeds.json": inputs.digest(ROOT / "engineering/sourcing/data/public-feeds.json"),
        "engineering/sourcing/data/iraq-domestic-2026-july.json": inputs.digest(ROOT / "engineering/sourcing/data/iraq-domestic-2026-july.json"),
        "takeoff_file": inputs.digest(takeoff_file),
    }
    packet = dict(
        schema="osr-iraq-material-cost-history-crosscheck/1",
        candidate_id=takeoff["candidate_id"], source_input_id=takeoff["source_input_id"],
        takeoff_id=takeoff["takeoff_id"],
        source_ids=sorted({source_records[current_source]["record_id"],
                           source_records["iraq.cso.regional-materials-wages-2025"]["record_id"]}),
        source_sha256=source_hashes,
        basis={
            "formula":"(material quantity x source rate + person-hours x hourly wage) x 1.20",
            "uplift_fraction":"0.20",
            "uplift_scope":"direct material plus direct labour only; composition of the allowance is unspecified",
            "recipe_per_nominal_m3":{"ordinary_cement_t":"0.35", "red_sand_m3":"0.50", "normal_grit_m3":"0.80"},
            "labour_hours_scenarios_per_nominal_m3":list(CONCRETE_HOURS),
            "historical_material_basis":"2024 CSO private-sector building estimated Table 15 cost-to-quantity ratios; modeled using 2024 market bulletin and material-use ratios last surveyed in 2012",
            "labour_basis":"2025 CSO Baghdad skilled-worker daily wage divided by explicit 8-hour day; held fixed across material scenarios",
            "current_comparison_basis":"2025 CSO Baghdad annual statistical market rates; not supplier quotations",
        },
        material_rate_comparisons=rate_comparisons,
        historical_2024_material_2025_wage_scenarios=historical_scenarios,
        current_2025_material_2025_wage_scenarios=current_scenarios,
        candidate_takeoff_mapped=False,
        complete_procurement_cost=None, complete_process_cost=None,
        complete_installed_cost=None, whole_life_cost=None,
        physical_qualification=None, engineering_accepted=False,
        procurement_approved=False, selected_reference_changed=False,
        unknown_is_zero=False,
        limitations=[
            "The 2024 CSO report is a modeled private-building estimate that uses 2024 permits and price/wage bulletins with material-use ratios from a 2012 survey; its cost/quantity ratios are historical statistical indicators, not observed supplier transactions.",
            "The 2024 report excludes Kurdistan Region; the 2025 wage comparator uses the Baghdad governorate annual construction-worker average.",
            "Normal grit is not confirmed to be interchangeable with the 2025 CSO crushed-gravel category; grading, strength and delivery scope are unknown.",
            "The concrete recipe and labour hours are sensitivity assumptions, not a mix design, verified yield, timed factory route or candidate-specific bill of quantities.",
            "The 20% uplift applies only to declared material plus direct labour and is an unallocated planning allowance, not verified overhead, profit, tax or contingency.",
        ])
    packet["source_epoch_id"] = identity(records)
    packet["packet_id"] = identity(packet)
    return packet


def _write_fresh(path, payload):
    path = Path(path).expanduser().resolve()
    if path.exists() or path.is_symlink():
        raise ValueError("Fresh output path required: " + str(path))
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as stream:
        stream.write(json.dumps(payload, ensure_ascii=False, indent=2, allow_nan=False) + "\n")


def main(argv=None):
    parser = ArgumentParser(description="Create source-bound Iraqi material + labour + 20% domestic fabrication screens")
    parser.add_argument("--takeoff", type=Path, required=True,
                        help="Exact sealed candidate-bound material takeoff JSON or .json.gz")
    parser.add_argument("--output", type=Path, required=True,
                        help="Fresh output directory for historical and July 2026 regional reports/estimates")
    args = parser.parse_args(argv)
    destination = args.output.expanduser().resolve()
    if destination.exists() or destination.is_symlink():
        raise ValueError("Fresh output directory required: " + str(destination))
    destination.mkdir(parents=True)
    records = catalogue.load_catalogue()
    takeoff = inputs.read_json(args.takeoff)
    packet, takeoff_packets = _make_packet(records, takeoff, args.takeoff)
    _write_fresh(destination / "iraq-domestic-cost-reference-2025.json", packet)
    current_2026, current_2026_packets = _make_2026_july_reference(records, takeoff, args.takeoff)
    _write_fresh(destination / "iraq-domestic-cost-reference-2026-07.json", current_2026)
    historical = _make_2024_material_crosscheck(records, takeoff, args.takeoff)
    _write_fresh(destination / "iraq-material-cost-history-crosscheck-2024.json", historical)
    for hours, estimate_packet in takeoff_packets:
        _write_fresh(destination / ("baghdad-concrete-takeoff-" + hours + "h.json"), estimate_packet)
    for region, hours, estimate_packet in current_2026_packets:
        region_slug = next(slug for slug, name in REGIONS if name == region)
        _write_fresh(destination / ("2026-07-" + region_slug + "-concrete-takeoff-" + hours + "h.json"), estimate_packet)
    print(json.dumps({
        "output": str(destination), "packet_id": packet["packet_id"],
        "candidate_id": packet["candidate_id"], "takeoff_id": packet["takeoff_id"],
        "regional_unit_rate_scenarios": len(packet["unit_rate_estimates"]),
        "historical_material_crosscheck_scenarios": len(historical["historical_2024_material_2025_wage_scenarios"]),
        "unavailable_scenarios": len(packet["unavailable_estimates"]),
        "baghdad_takeoff_scenarios": len(packet["baghdad_concrete_takeoff_estimates"]),
        "july_2026_unit_rate_scenarios": len(current_2026["unit_rate_estimates"]),
        "july_2026_candidate_takeoff_scenarios": len(current_2026["regional_concrete_takeoff_estimates"]),
        "july_2026_candidate_takeoff_mapped_groups": sorted({row["mapped_group_count"] for row in current_2026["regional_concrete_takeoff_estimates"]}),
        "july_2026_candidate_takeoff_mapped_occurrences": sorted({row["mapped_occurrence_count"] for row in current_2026["regional_concrete_takeoff_estimates"]}),
        "complete_installed_cost": None, "physical_qualification": None,
    }, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    raise SystemExit(main())
