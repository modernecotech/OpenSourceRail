"""Round-trip test: design.toml → scenario.toml → parses as valid TOML
with all the wire-schema fields osr-sim expects."""

from __future__ import annotations

import tomllib
from pathlib import Path

import pytest

from osr_scenario import generate_from_path, generate_scenario

REPO_ROOT = Path(__file__).resolve().parents[2]
SAMAWAH_DESIGN = REPO_ROOT / "designs/middle-east/iraq/samawah/design.toml"
TEMPLATES = REPO_ROOT / "designs/templates"


def _parse(text: str) -> dict:
    return tomllib.loads(text)


def test_samawah_design_generates_valid_scenario() -> None:
    text = generate_from_path(SAMAWAH_DESIGN)
    doc = _parse(text)
    # Top-level sections.
    assert "scenario" in doc
    assert "climate" in doc
    assert "consist" in doc
    assert "stations" in doc
    assert "lines" in doc
    assert "fleets" in doc
    assert "sites" in doc


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
    """Interchange stations must emit charging_power_kw=500; terminals 1000;
    standard stations emit no charging_power_kw entry."""
    scenario = _parse(generate_from_path(SAMAWAH_DESIGN))
    by_id = {s["id"]: s for s in scenario["stations"]}

    central = by_id["samawah-central"]
    # Archetype 'major' in design.toml with canopy override — charging stays.
    assert central.get("charging_power_kw") == 500
    assert central["dwell_seconds"] == 45

    univ = by_id["al-muthanna-university"]
    assert univ.get("charging_power_kw") == 1000
    assert univ["is_terminal"] is True

    std = by_id["al-hakam"]
    assert "charging_power_kw" not in std
    assert std["dwell_seconds"] == 30


def test_site_tier_expanded() -> None:
    """`tier = "depot-main"` must expand to the big-depot kWh/kW figures."""
    scenario = _parse(generate_from_path(SAMAWAH_DESIGN))
    by_station = {s["station"]: s for s in scenario["sites"]}
    # Al-Maali is a depot-main in design.toml.
    maali = by_station["al-maali"]
    assert maali["pv_nameplate_kw"] >= 1000.0
    assert maali["storage_capacity_kwh"] >= 10_000.0


def test_generator_is_deterministic() -> None:
    """Same input → byte-identical output."""
    a = generate_from_path(SAMAWAH_DESIGN)
    b = generate_from_path(SAMAWAH_DESIGN)
    assert a == b


def test_generated_file_in_repo_matches_regenerated() -> None:
    """The committed scenarios/samawah.toml must match what the generator
    would produce today — catches the "someone hand-edited the generated
    file" regression."""
    committed = (REPO_ROOT / "scenarios/samawah.toml").read_text()
    regenerated = generate_from_path(SAMAWAH_DESIGN)
    assert committed == regenerated, (
        "scenarios/samawah.toml is out of sync with design.toml; run "
        "`python -m osr_scenario` to regenerate."
    )


def test_consist_matches_light_metro_family() -> None:
    scenario = _parse(generate_from_path(SAMAWAH_DESIGN))
    consist = scenario["consist"]
    assert consist["car_count"] == 3
    assert 50 < consist["length_m"] < 80
    # Battery sized for Samawah line-length per RFC 0021.
    assert 200 <= consist["battery_capacity_kwh"] <= 500
