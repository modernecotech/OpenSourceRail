"""Round-trip test: design.toml → scenario.toml → parses as valid TOML
with all the wire-schema fields osr-sim expects."""

from __future__ import annotations

import tomllib
from pathlib import Path

import pytest

from osr_scenario import generate_from_path, generate_scenario
from osr_scenario.network_readme import (
    _funding_stack,
    _load_country_finance,
    render_readme,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
SAMAWAH_DESIGN = REPO_ROOT / "designs/west-asia/Iraq/Samawah/design.toml"
SAMAWAH_SCENARIO = REPO_ROOT / "designs/west-asia/Iraq/Samawah/samawah.toml"
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


def test_scenario_fleet_count_matches_design() -> None:
    design = tomllib.loads(SAMAWAH_DESIGN.read_text())
    scenario = _parse(generate_from_path(SAMAWAH_DESIGN))
    assert len(scenario["fleets"]) == len(design["fleets"])


def test_archetype_defaults_applied() -> None:
    """Interchange stations emit charging_power_kw=500; terminals 1000;
    standard stations emit no charging_power_kw entry. Test by archetype
    category, not specific IDs, so the test works with both hand-crafted
    and auto-planned designs."""
    import tomllib
    design = tomllib.loads(SAMAWAH_DESIGN.read_text())
    design_by_id = {s["id"]: s for s in design["stations"]}
    scenario = _parse(generate_from_path(SAMAWAH_DESIGN))
    scen_by_id = {s["id"]: s for s in scenario["stations"]}

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
        assert scen.get("charging_power_kw") == 500
        assert scen["dwell_seconds"] == 60

    # Terminals get the full 1000 kW + is_terminal=true.
    terminals = [
        s for s in design["stations"]
        if s.get("archetype") in ("terminal", "depot-terminal")
    ]
    assert terminals, "design should have ≥1 terminal"
    for t in terminals:
        scen = scen_by_id[t["id"]]
        assert scen.get("charging_power_kw") == 1000
        assert scen.get("is_terminal") is True


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


def test_finance_stack_defaults_are_grant_free() -> None:
    stack = _funding_stack({})
    assert stack.grant_frac == pytest.approx(0.00)
    assert stack.multi_frac == pytest.approx(0.80)
    assert stack.bond_frac == pytest.approx(0.0)
    assert stack.equity_frac == pytest.approx(0.20)
    assert stack.multi_rate == pytest.approx(0.020)
    assert stack.tenor == 40


def test_country_finance_inherits_grant_free_defaults() -> None:
    stack = _funding_stack(_load_country_finance("IQ"))
    assert stack.grant_frac == pytest.approx(0.00)
    assert stack.multi_frac == pytest.approx(0.80)
    assert stack.bond_frac == pytest.approx(0.0)
    assert stack.equity_frac == pytest.approx(0.20)
    assert stack.multi_rate == pytest.approx(0.020)


def test_readme_nets_operating_surplus_against_gov_debt_support() -> None:
    text = render_readme(
        design_path=SAMAWAH_DESIGN,
        scenario_path=SAMAWAH_SCENARIO,
        population=373_770,
    )

    assert "| Gross repayable-debt service + residual OPEX subsidy |" in text
    assert "| Operating surplus applied to debt support |" in text
    assert (
        "| **Net gov repayable-debt support + residual OPEX subsidy** |"
        in text
    )
    assert (
        "| Operating surplus applied to debt support | "
        "-$28 M / yr | -$28 M / yr | **$0 k / yr** |"
        in text
    )
    assert (
        "| **Net gov repayable-debt support + residual OPEX subsidy** | "
        "$0 k / yr | $0 k / yr | **$28 M / yr** |"
        in text
    )
    assert (
        "| Green concessional loan | 80% | $708 M | 2.0% | "
        "40 y, 5 y grace | $28 M / yr |"
        in text
    )
    assert (
        "| Government equity (no debt service) | 20% | $177 M |"
        in text
    )
    assert "| Climate / development grant" not in text
    assert (
        "Dedicated utility-scale solar plant / contracted offsite PPA asset: "
        "**63.3 MW**"
        in text
    )
    assert (
        "| Dedicated solar plant | 63.3 MW / 317 MWh/day |"
        in text
    )
    assert (
        "| Residual grid/PPA top-up need | 0 MWh/day |"
        in text
    )
    assert (
        "| **CAPEX total** | **$885 M** |"
        in text
    )
    assert (
        "| Traction energy (131.2 GWh / yr) |"
        in text
    )
    assert (
        "on-site PV 30.7 GWh/yr + dedicated solar plant 63.3 MW / "
        "115.6 GWh/yr (100% coverage); residual grid/PPA top-up 0.0 GWh/yr"
        in text
    )
    assert (
        "| Labour (408 FTE) | driverless roster: OCC/remote 65, "
        "station/platform 127, passenger service 44, fleet maintenance 64"
        in text
    )
    assert (
        "| Practical service capacity used | 50% | 80% | 17% |"
        in text
    )
    assert (
        "| Annual paid trips | 63.1 M | 100.9 M | 20.8 M |"
        in text
    )
    assert "| Daily active riders |" not in text
    assert "| Daily paid trips |" not in text
    assert "| Paid trips / active rider |" not in text
    assert "## Broad economic benefits (planning proxy)" in text
    assert (
        "| **Annual quantified benefit / activity proxy** | "
        "**$80 M / yr** | **$129 M / yr** |"
        in text
    )
    assert (
        "| Education | 3 education anchors | 9,065 trips/school day; "
        "2.0 M access-events/yr | 14,505 trips/school day; "
        "3.2 M access-events/yr |"
        in text
    )
    assert (
        "| Healthcare | 10 healthcare anchors | 15,951 trips/day; "
        "5.8 M access-events/yr | 25,521 trips/day; "
        "9.3 M access-events/yr |"
        in text
    )
    assert (
        "| CAPEX retained in local procurement / payroll | $466 M | "
        "53% of $885 M CAPEX using bucket local-content shares |"
        in text
    )
    assert (
        "| Construction employment supported | 25,536 job-years |"
        in text
    )
    assert (
        "| Gov repayable-debt service + residual OPEX subsidy |"
        not in text
    )


def test_consist_matches_light_metro_family() -> None:
    scenario = _parse(generate_from_path(SAMAWAH_DESIGN))
    assert scenario["scenario"]["name"] == "Samawah"
    consist = scenario["consist"]
    assert consist["car_count"] == 3
    assert 50 < consist["length_m"] < 80
    # Battery sized for Samawah line-length per RFC 0021.
    assert 200 <= consist["battery_capacity_kwh"] <= 500
    assert consist["roof_pv"]["nameplate_kw"] == 19.2
    assert consist["roof_pv"]["usable_factor"] == 0.65
    assert consist["roof_pv"]["air_cleaner"]["enabled"] is True
    assert consist["roof_pv"]["air_cleaner"]["compressor_power_kw"] == 0.9
    assert consist["roof_pv"]["air_cleaner"]["dust_loss_recovery_frac"] == 0.75
