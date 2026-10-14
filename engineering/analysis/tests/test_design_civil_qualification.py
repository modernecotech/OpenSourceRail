"""Independent published benchmark and adverse source/site/stage boundaries."""

from copy import deepcopy
import json
from pathlib import Path

import pytest

from engineering.design_consistency.demonstrators import viaduct
from engineering.design_engine.civil_qualification import (
    assess_site, elastic_shortening, foundation_geometry, input_templates, prestress_assessment,
)
from engineering.design_engine.civil_confirmation import support_contact_demands
from engineering.design_engine.contracts import fingerprint, identity

ROOT = Path(__file__).resolve().parents[3]


def context():
    return identity(dict(schema="osr-design-identity/1", city="samawah", project="samawah",
                         environment="simulation", configuration_revision="research-1",
                         baseline_sha256=None, run_id=None, asset_id=None, part_id=None))


def source():
    return dict(reference="Clearly labelled test fixture, not project evidence",
                sha256="a" * 64, basis="research-assumption")


def value(number, unit):
    return dict(value=number, unit=unit, source=source())


def test_independent_fhwa_published_elastic_shortening_example_in_si():
    # FHWA pscus054.cfm independently reports 13.7 ksi. Exact listed example
    # inputs are converted to SI, rather than reconstructing expected outputs
    # from this implementation. No example value becomes project material data.
    inch, ksi = 0.0254, 6_894_757.293168361
    group = dict(metallic_area_m2=44 * 0.153 * inch**2,
                 pretransfer_stress_pa=202.5 * ksi, steel_modulus_pa=28500 * ksi,
                 eccentricity_m=31.38 * inch)
    loss = elastic_shortening([group], area_m2=1085 * inch**2,
                              inertia_m4=733320 * inch**4,
                              concrete_modulus_pa=4200 * ksi,
                              self_weight_moment_nm=20142 * 4448.2216152605 * inch)
    assert loss[0] / ksi == pytest.approx(13.7, abs=0.05)
    split = [{**group, "metallic_area_m2": group["metallic_area_m2"] / 2} for _ in range(2)]
    assert elastic_shortening(split, area_m2=1085 * inch**2, inertia_m4=733320 * inch**4,
                              concrete_modulus_pa=4200 * ksi,
                              self_weight_moment_nm=20142 * 4448.2216152605 * inch) == pytest.approx(loss * 2)


def prestress_input(contract):
    return dict(schema="osr-civil-prestress-input/1", identity=context(),
                contract_sha256=fingerprint(contract), mode="pretensioned-straight",
                transfer_age=value(7 * 86400, "s"), service_age=value(365 * 86400, "s"),
                concrete_transfer_modulus=value(30e9, "Pa"),
                transfer_compression_limit=value(20e6, "Pa"), transfer_tension_limit=value(2e6, "Pa"),
                service_compression_limit=value(25e6, "Pa"), service_tension_limit=value(2e6, "Pa"),
                tendons=[dict(physical_part_id=p["id"], metallic_area=value(0.0006, "m2"),
                              pretransfer_stress=value(1.2e9, "Pa"), steel_modulus=value(195e9, "Pa"),
                              creep_loss=value(30e6, "Pa"), shrinkage_loss=value(25e6, "Pa"),
                              relaxation_loss=value(15e6, "Pa"))
                         for p in contract["parts"] if p["id"].startswith("tendon-")])


def trace():
    return json.loads((ROOT / "engineering/industrialisation/vehicle-civil-load-trace.json").read_text())


def test_default_does_not_credit_an_unmeasured_seed_prestress():
    result = prestress_assessment(viaduct(), trace())
    assert result["checks"]["transfer"] == result["checks"]["loss_history"] == "unknown"
    assert result["gross_demands"]["service"]["effective_prestress_force_n"] == 0
    assert result["physical_release"] is False


def test_conditional_transfer_service_and_missing_time_losses_remain_distinct():
    contract = viaduct()
    inputs = prestress_input(contract)
    result = prestress_assessment(contract, trace(), inputs, context=context())
    assert result["checks"]["transfer"] == "passed"
    assert result["checks"]["loss_history"] == "passed"
    assert result["checks"]["anchorage"] == "unknown"
    assert result["physical_release"] is result["site_qualified"] is False
    inputs["tendons"][0]["creep_loss"] = None
    result = prestress_assessment(contract, trace(), inputs, context=context())
    assert result["service_envelope_fibre_stress"] is None
    assert result["checks"]["loss_history"] == result["checks"]["service_cracking"] == "unknown"


@pytest.mark.parametrize("fault", ["scope", "contract", "unit", "area", "posttension", "duplicate", "loss"])
def test_prestress_mutations_do_not_gain_qualification(fault):
    contract = viaduct()
    inputs = prestress_input(contract)
    if fault == "scope":
        inputs["identity"]["city"] = "mosul"
    elif fault == "contract":
        inputs["contract_sha256"] = "b" * 64
    elif fault == "unit":
        inputs["tendons"][0]["metallic_area"]["unit"] = "mm2"
    elif fault == "area":
        inputs["tendons"][0]["metallic_area"]["value"] = 1
    elif fault == "posttension":
        inputs["mode"] = "post-tensioned"
    elif fault == "duplicate":
        inputs["tendons"][1] = deepcopy(inputs["tendons"][0])
    else:
        inputs["tendons"][0]["creep_loss"]["value"] = 2e9
    with pytest.raises(ValueError):
        prestress_assessment(contract, trace(), inputs, context=context())


def site_input():
    return dict(schema="osr-civil-site-input/1", identity=context(),
                survey=dict(crs="EPSG:32638", vertical_datum="Explicit fixture datum", date="2025-01-01",
                            source=source(), horizontal_uncertainty=value(0.02, "m"), vertical_uncertainty=value(0.03, "m")),
                layers=[dict(top=value(0, "m"), bottom=value(15, "m"), description="Fixture stratum", source=source())],
                groundwater=dict(source=source(), observations=[{"depth_m": 3}]),
                utilities=dict(source=source(), observations=[{"status": "fixture utility located"}]),
                calibration=dict(source=source(), training_records=["training-fixture"], holdout_records=["holdout-fixture"],
                                 model_domain="Fixture pile axial demand", uncertainty=value(0.1, "1")),
                route_station_constraints=[dict(id="access-fixture", kind="station_access", available=value(2, "m"),
                                                required=value(1.8, "m"), uncertainty=value(0.3, "m"), source=source())])


def test_site_unknowns_are_distinct_from_input_completeness_and_clearance_failures():
    unknown = assess_site(None, context=context(), required_depth_m=15)
    assert set(unknown["checks"].values()) == {"unknown"}
    row = assess_site(site_input(), context=context(), required_depth_m=20)
    assert row["checks"]["survey"] == "passed"
    assert row["checks"]["ground_depth_coverage"] == row["checks"]["route_station_constraints"] == "failed"
    assert row["site_qualified"] is row["physical_release"] is row["source_files_verified"] is False
    assert row["independent_acceptance"] == "unknown"


@pytest.mark.parametrize("fault", ["layer-gap", "overlap", "empty-utilities", "missing-source", "scope", "vertical-datum"])
def test_site_adverse_records_reject(fault):
    row = site_input()
    if fault == "layer-gap":
        row["layers"][0]["top"]["value"] = 1
    elif fault == "overlap":
        row["calibration"]["holdout_records"] = row["calibration"]["training_records"]
    elif fault == "empty-utilities":
        row["utilities"]["observations"] = []
    elif fault == "missing-source":
        row["layers"][0]["source"]["sha256"] = "fake"
    elif fault == "scope":
        row["identity"]["environment"] = "physical"
    else:
        row["survey"]["vertical_datum"] = ""
    with pytest.raises(ValueError):
        assess_site(row, context=context(), required_depth_m=15)


def test_actual_bearing_contacts_do_not_supply_missing_jack_insert_resistance():
    contract = viaduct()
    service = support_contact_demands(contract, "service", {1: 300000, 81: 600000})
    assert len(service) == 4
    assert sum(r["reaction_n"] for r in service) == 900000
    assert service[0]["contact_area_m2"] == pytest.approx(0.3 * 0.25)
    assert service[0]["average_contact_pressure_pa"] == pytest.approx(2e6)
    assert all(r["local_resistance"] == "unknown" for r in service)
    for stage in ("lifting", "bearing-replacement"):
        result = support_contact_demands(contract, stage, {1: 300000, 81: 600000})
        assert all(r["contact_area_m2"] is r["average_contact_pressure_pa"] is None for r in result)


def test_editable_templates_carry_actual_foundation_scope_but_no_fabricated_values():
    contract = viaduct()
    templates = input_templates(contract, context())
    assert templates["site_input"]["contract_sha256"] == fingerprint(contract)
    assert templates["site_input"]["survey"]["crs"] is None
    assert templates["prestress_input"]["tendons"][0]["metallic_area"]["value"] is None
    assert len(templates["foundation_geometry"]["piles"]) == 8
    assert templates["foundation_geometry"]["minimum_investigation_depth_m"] == pytest.approx(15.8)
    with pytest.raises(ValueError):
        assess_site(templates["site_input"], context=context(), required_depth_m=12, contract=contract)


def test_actual_pile_footprint_and_toe_depth_control_survey_coverage():
    contract = viaduct()
    row = site_input()
    row["contract_sha256"] = fingerprint(contract)
    geometry = foundation_geometry(contract)
    row["survey"].update(coverage_bounds_m=[-5, -5, 25, 5], design_origin_in_crs_m=[500000, 3300000, 10],
                         design_axes_in_crs=[[1, 0, 0], [0, 1, 0], [0, 0, 1]])
    result = assess_site(row, context=context(), required_depth_m=5, contract=contract)
    assert result["required_investigation_depth_m"] == geometry["minimum_investigation_depth_m"]
    assert result["checks"]["foundation_survey_footprint"] == "passed"
    row["survey"]["coverage_bounds_m"][2] = 15
    assert assess_site(row, context=context(), required_depth_m=5, contract=contract)["checks"]["foundation_survey_footprint"] == "failed"
    row["survey"]["design_axes_in_crs"][0][0] = 2
    with pytest.raises(ValueError, match="orthonormal"):
        assess_site(row, context=context(), required_depth_m=5, contract=contract)
