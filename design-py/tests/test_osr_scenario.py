"""Round-trip test: design.toml → scenario.toml → parses as valid TOML
with all the wire-schema fields osr-sim expects."""

from __future__ import annotations

import re
import tomllib
from copy import deepcopy
from pathlib import Path

import pytest

from osr_scenario import GeneratorError, generate_from_path, generate_scenario
from osr_scenario.capital import (
    city_capital_breakdown,
    foreign_turnkey_cases,
    funding_plan,
)
from osr_scenario.network_readme import (
    _load_country_finance,
    render_readme,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
SAMAWAH_DESIGN = REPO_ROOT / "designs/west-asia/Iraq/Samawah/design.toml"
SAMAWAH_SCENARIO = REPO_ROOT / "designs/west-asia/Iraq/Samawah/samawah.toml"
MOSUL_DESIGN = REPO_ROOT / "designs/west-asia/Iraq/Mosul/design.toml"
BASRA_DESIGN = REPO_ROOT / "designs/west-asia/Iraq/Basra/design.toml"
TEMPLATES = REPO_ROOT / "lib/templates"


def _parse(text: str) -> dict:
    return tomllib.loads(text)


def test_samawah_design_generates_valid_scenario() -> None:
    text = generate_from_path(SAMAWAH_DESIGN)
    doc = _parse(text)
    # Top-level sections that are *always* present.
    assert "scenario" in doc
    assert "climate" in doc
    assert "consist" in doc
    assert "stations" in doc
    assert "lines" in doc
    assert "fleets" in doc
    # Sites are optional — auto-generated designs without committed
    # trackside energy infrastructure legitimately omit them.


def test_scenario_station_count_matches_design() -> None:
    design = tomllib.loads(SAMAWAH_DESIGN.read_text())
    scenario = _parse(generate_from_path(SAMAWAH_DESIGN))
    assert len(scenario["stations"]) == len(design["stations"])


def test_scenario_line_count_matches_design() -> None:
    design = tomllib.loads(SAMAWAH_DESIGN.read_text())
    scenario = _parse(generate_from_path(SAMAWAH_DESIGN))
    assert len(scenario["lines"]) == len(design["lines"])


def test_catalog_ring_with_repeated_closing_station_becomes_wrap_segment() -> None:
    lyon_design = REPO_ROOT / "designs/europe/France/Lyon/design.toml"
    scenario = _parse(generate_from_path(lyon_design))
    ring = next(line for line in scenario["lines"] if line["id"] == "line-6")
    station_ids = [station["id"] for station in ring["stations"]]
    assert ring["is_ring"] is True
    assert ring["ring_wrap_length_m"] > 0
    assert station_ids[0] != station_ids[-1]
    assert len(station_ids) == len(set(station_ids))


def test_scenario_fleet_count_matches_design() -> None:
    design = tomllib.loads(SAMAWAH_DESIGN.read_text())
    scenario = _parse(generate_from_path(SAMAWAH_DESIGN))
    assert len(scenario["fleets"]) == len(design["fleets"])


def test_generated_peak_windows_and_depot_service_policy() -> None:
    """Every auto-generated line uses the shared peak-priority timetable,
    and exactly one depot per line is selected for off-peak service."""
    design = tomllib.loads(SAMAWAH_DESIGN.read_text())
    scenario = _parse(generate_from_path(SAMAWAH_DESIGN))
    expected = [
        ("05:30", "07:00", 6),
        ("07:00", "09:00", 3),
        ("09:00", "15:00", 6),
        ("15:00", "17:00", 3),
        ("17:00", "23:30", 6),
        ("23:30", "02:00", 12),
    ]
    for fleet in scenario["fleets"]:
        actual = [
            (window["from"], window["to"], window["headway_min"])
            for window in fleet["schedule"]
        ]
        assert actual == expected

    service_stations = {
        station["id"]
        for station in scenario["stations"]
        if station.get("depot_service")
    }
    assert len(service_stations) == len(scenario["lines"])
    assert scenario["scenario"]["depot_service_seconds"] == 720
    assert scenario["scenario"]["energy_adaptive_service"] is True
    assert scenario["scenario"]["normal_service_soc"] == 0.40
    assert scenario["scenario"]["maximum_headway_multiplier"] == 3.0
    assert scenario["scenario"]["protected_peak_headway_min"] == 3
    policy = design["operations"]["energy_adaptive_service"]
    assert scenario["scenario"]["energy_adaptive_service"] == policy["enabled"]
    assert scenario["scenario"]["normal_service_soc"] == policy["normal_service_soc"]
    assert scenario["scenario"]["maximum_headway_multiplier"] == policy["maximum_headway_multiplier"]
    assert scenario["scenario"]["protected_peak_headway_min"] == policy["protected_peak_headway_min"]


def test_archetype_defaults_applied() -> None:
    """Every charging stop uses the family charging-cabinet count.

    Longer inter-station distances are handled by dwell and onboard energy,
    while high-throughput families repeat the standard 500 kW cabinet.
    """
    import tomllib
    design = tomllib.loads(SAMAWAH_DESIGN.read_text())
    family = str(design.get("network", {}).get("rolling_stock", "light-metro-3car"))
    expected_cabinets = {"metro-4car": 3, "metro-6car": 4}.get(
        family, 1
    )
    expected_power_kw = expected_cabinets * 500
    design_by_id = {s["id"]: s for s in design["stations"]}
    scenario = _parse(generate_from_path(SAMAWAH_DESIGN))
    scen_by_id = {s["id"]: s for s in scenario["stations"]}

    radial_charging_dwell = int(
        design.get("operations", {})
        .get("radial_service", {})
        .get("minimum_charging_dwell_seconds", 120)
    )

    # Interchange archetype defaults are validated when ≥1 exists.
    # The auto-generator does not guarantee an interchange — line
    # endpoints can avoid intersecting on small networks (Samawah
    # at the 373 k 2024-census population produces 3 disjoint
    # radials with no interchange complex). When the design happens
    # to include one, validate the charging + dwell defaults; when
    # it doesn't, this branch is a no-op. Both `interchange` and
    # `interchange-elevated` (the auto-gen's elevated-junction-pass
    # variant) share these defaults.
    interchanges = [
        s for s in design["stations"]
        if s.get("archetype") in ("interchange", "interchange-elevated")
    ]
    for ix in interchanges:
        scen = scen_by_id[ix["id"]]
        assert scen.get("charging_power_kw") == expected_power_kw
        assert scen["dwell_seconds"] >= radial_charging_dwell

    # Terminals use the same family cabinet count. The three-minute turnback is
    # the floor; the line energy calculation may lengthen it to restore the
    # planned energy margin.
    terminals = [
        s for s in design["stations"]
        if s.get("archetype") in ("terminal", "depot-terminal")
    ]
    assert terminals, "design should have ≥1 terminal"
    for t in terminals:
        scen = scen_by_id[t["id"]]
        assert scen.get("charging_power_kw") == expected_power_kw
        if t.get("archetype") == "terminal":
            assert scen["dwell_seconds"] >= 180
        assert scen.get("is_terminal") is True


@pytest.mark.parametrize(
    ("design_path", "expected_car_count", "expected_battery_kwh", "module_count"),
    [
        (MOSUL_DESIGN, 4, 900, 3),
        (BASRA_DESIGN, 6, 1350, 4),
    ],
)
def test_high_throughput_families_repeat_standard_charging_modules(
    design_path: Path,
    expected_car_count: int,
    expected_battery_kwh: int,
    module_count: int,
) -> None:
    """High-throughput consists scale by repeating, not uprating, modules."""
    scenario = _parse(generate_from_path(design_path))
    assert scenario["consist"]["car_count"] == expected_car_count
    assert scenario["consist"]["battery_capacity_kwh"] == expected_battery_kwh

    charging_stations = [
        station for station in scenario["stations"]
        if station.get("charging_power_kw", 0) > 0
    ]
    assert charging_stations
    assert {station["charging_power_kw"] for station in charging_stations} == {
        500 * module_count
    }

    passenger_sites = [
        site for site in scenario["sites"]
        if site.get("tier") in {
            "standard", "major", "interchange", "interchange-elevated", "terminal"
        }
    ]
    assert passenger_sites
    for site in passenger_sites:
        assert site["storage_capacity_kwh"] == 500 * module_count
        assert site["storage_module_kwh"] == 500
        assert site["charger_max_kw"] == 500 * module_count
        assert site["charger_max_current_a"] == 825 * module_count
        assert site["charger_contact_count"] == 2 * module_count
        assert site["grid_import_kw"] >= 500 * module_count
        assert site["grid_export_kw"] >= 500 * module_count


def test_mosul_ring_dwell_covers_complete_circuit_energy() -> None:
    """Ring dwell must replenish one loop without a terminal top-up."""
    design = tomllib.loads(MOSUL_DESIGN.read_text())
    scenario = _parse(generate_from_path(MOSUL_DESIGN))
    ring_ids = {
        str(line.get("id") or line.get("name"))
        for line in design["lines"]
        if line.get("shape") == "ring" or line.get("is_ring")
    }
    assert ring_ids == {"line-6"}

    ring_policy = design["operations"]["ring_service"]
    assert ring_policy["minimum_dwell_seconds"] == 120
    ring_stations = [
        station
        for station in scenario["stations"]
        if any(
            station["id"] == line_station["id"]
            for line in scenario["lines"]
            if line["id"] in ring_ids
            for line_station in line["stations"]
        )
    ]
    assert ring_stations

    ring_line = next(line for line in design["lines"] if line["name"] in ring_ids)
    consist = scenario["consist"]
    ambient_c = float(scenario["climate"]["ambient_c"])
    hvac_uplift = float(
        scenario["climate"].get(
            "hvac_uplift_frac", min(max((ambient_c - 25.0) / 25.0, 0.0), 0.25)
        )
    )
    circuit_use_kwh = (
        float(ring_line["length_m"])
        / 1000.0
        * int(consist["car_count"])
        * float(consist["energy_kwh_per_car_km"])
        * (1.0 + hvac_uplift)
    )
    planned_dwell = int(ring_line["charging_dwell_seconds"])
    charging_stations = [
        station
        for station in ring_stations
        if int(station.get("charging_power_kw", 0)) > 0
    ]
    assert charging_stations
    assert all(
        station["dwell_seconds"] >= planned_dwell
        for station in charging_stations
    )
    # A full battery covers the initial condition. Repeating all-day service
    # is stricter: one loop's dwell must replace one loop's energy, including
    # the design's 10% charging margin. Halts are deliberately excluded.
    charge_per_circuit_kwh = (
        sum(int(station["charging_power_kw"]) for station in charging_stations)
        * planned_dwell
        / 3600.0
    )
    assert charge_per_circuit_kwh >= circuit_use_kwh * 1.10


def test_generator_rejects_explicitly_energy_deficient_ring_default() -> None:
    design = tomllib.loads(MOSUL_DESIGN.read_text())
    broken = deepcopy(design)
    ring_policy = broken["operations"]["ring_service"]
    ring_policy["opportunity_charging_required"] = True
    ring_policy["minimum_dwell_seconds"] = 1
    ring = next(line for line in broken["lines"] if line.get("shape") == "ring")
    ring["charging_dwell_seconds"] = 1
    with pytest.raises(GeneratorError, match="opportunity charging delivers"):
        generate_scenario(broken, MOSUL_DESIGN, TEMPLATES)


def test_mosul_uses_modern_drive_energy_policy() -> None:
    design = tomllib.loads(MOSUL_DESIGN.read_text())
    scenario = _parse(generate_from_path(MOSUL_DESIGN))
    policy = design["operations"]["traction_energy"]
    assert policy["reference_energy_kwh_per_car_km"] == 3.0
    assert policy["modern_drive_energy_factor"] == 0.80
    assert policy["nominal_energy_kwh_per_car_km"] == 2.4
    assert scenario["consist"]["energy_kwh_per_car_km"] == 2.4


def test_site_tier_expanded() -> None:
    """Any depot-main site must expand to the big-depot kWh/kW figures."""
    import tomllib
    design = tomllib.loads(SAMAWAH_DESIGN.read_text())
    depot_main_sites = [
        s for s in design.get("sites", []) if s.get("tier") == "depot-main"
    ]
    if not depot_main_sites:
        # Auto-planner may not emit depot-main sites — skip when absent.
        return
    scenario = _parse(generate_from_path(SAMAWAH_DESIGN))
    by_station = {s["station"]: s for s in scenario["sites"]}
    for d in depot_main_sites:
        s = by_station[d["station"]]
        assert s["pv_nameplate_kw"] >= 1000.0
        assert s["storage_capacity_kwh"] >= 10_000.0


def test_generator_is_deterministic() -> None:
    """Same input → byte-identical output."""
    a = generate_from_path(SAMAWAH_DESIGN)
    b = generate_from_path(SAMAWAH_DESIGN)
    assert a == b


def test_generated_file_in_repo_matches_regenerated() -> None:
    """The committed designs/west-asia/Iraq/Samawah/samawah.toml must match what the generator
    would produce today — catches the "someone hand-edited the generated
    file" regression."""
    committed = (REPO_ROOT / "designs/west-asia/Iraq/Samawah/samawah.toml").read_text()
    regenerated = generate_from_path(SAMAWAH_DESIGN)
    assert committed == regenerated, (
        "designs/west-asia/Iraq/Samawah/samawah.toml is out of sync with design.toml; run "
        "`python -m osr_scenario` to regenerate."
    )


def test_imported_and_local_capital_reconcile_city_capex() -> None:
    design = _parse(SAMAWAH_DESIGN.read_text())
    capital = city_capital_breakdown(design["costs"])
    plan = funding_plan(capital, _load_country_finance("IQ"))
    assert capital.imported_usd + capital.local_usd == pytest.approx(
        capital.total_usd
    )
    assert 0.0 < capital.imported_share < 1.0
    assert plan.external_debt_usd == pytest.approx(capital.imported_usd)
    assert plan.local_bond_usd + plan.local_equity_usd == pytest.approx(
        capital.local_usd
    )
    assert plan.annual_external_capital_draw_usd * plan.construction_years == pytest.approx(
        capital.imported_usd
    )
    assert capital.imported_share < 0.40


def test_foreign_turnkey_comparator_reconciles_savings_and_annual_draw() -> None:
    design = _parse(SAMAWAH_DESIGN.read_text())
    capital = city_capital_breakdown(design["costs"])
    plan = funding_plan(capital, _load_country_finance("IQ"))
    cases = foreign_turnkey_cases(capital, plan)
    comparison = cases["default"]

    assert list(cases) == ["low", "default", "high"]
    assert comparison.cost_multiplier == pytest.approx(2.0)
    assert comparison.foreign_total_usd == pytest.approx(2.0 * capital.total_usd)
    assert comparison.external_capital_avoided_usd == pytest.approx(
        comparison.foreign_external_usd - capital.imported_usd
    )
    assert comparison.annual_external_capital_avoided_usd * plan.construction_years == pytest.approx(
        comparison.external_capital_avoided_usd
    )
    assert comparison.external_capital_reduction > comparison.total_capex_reduction
    assert comparison.external_interest_avoided_usd > 0.0
    assert comparison.osr_lifetime_external_interest_usd == pytest.approx(
        plan.lifetime_external_interest_usd
    )
    assert comparison.lifetime_external_financing_avoided_usd == pytest.approx(
        comparison.external_capital_avoided_usd
        + comparison.external_interest_avoided_usd
    )


def test_readme_is_concise_local_summary_with_common_reference() -> None:
    text = render_readme(
        design_path=SAMAWAH_DESIGN,
        scenario_path=SAMAWAH_SCENARIO,
    )

    assert "[deployment planning reference]" in text
    assert "Auto-planned by the OpenSourceRail design pipeline" in text
    assert "## Network" in text
    assert "## Energy" in text
    assert "## Capital And Funding" in text
    assert "## Local Evidence" in text
    assert "## Local Files And Regeneration" in text
    assert "External capital saved vs default turnkey sensitivity" in text
    assert "Capital + lifetime external interest saved" in text
    assert "| Finance | pass |" in text
    assert "| Native simulation + degraded cases | pass |" in text
    assert "| SUMO timetable | pass |" in text
    assert "| GIS package | pass |" in text
    assert "| Grid/charging/solar | pass |" in text
    assert "| Lowest traversal charging margin |" in text
    assert len(text.splitlines()) < 140
    assert "## Construction QA system" not in text
    assert "## Broad economic benefits (planning proxy)" not in text


def test_consist_matches_light_metro_family() -> None:
    scenario = _parse(generate_from_path(SAMAWAH_DESIGN))
    assert scenario["scenario"]["name"] == "Samawah"
    consist = scenario["consist"]
    assert consist["car_count"] == 3
    assert consist["length_m"] == 49.5
    # 675 kWh nameplate retains the promoted 180 kWh usable per car.
    assert consist["battery_capacity_kwh"] == 675
    assert consist["energy_kwh_per_car_km"] == 2.4
    assert consist["roof_pv"]["nameplate_kw"] == 15.12
    assert consist["roof_pv"]["usable_factor"] == 0.65
    assert consist["roof_pv"]["air_cleaner"]["enabled"] is True
    assert consist["roof_pv"]["air_cleaner"]["compressor_power_kw"] == 0.9
    assert consist["roof_pv"]["air_cleaner"]["dust_loss_recovery_frac"] == 0.75
