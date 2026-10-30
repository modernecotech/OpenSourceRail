from decimal import Decimal
from pathlib import Path

import pytest

from engineering.sourcing.catalogue import load_catalogue
from engineering.sourcing.iraq_gfrp_cost_scenarios import _build

ROOT = Path(__file__).resolve().parents[3]
PACKETS = ROOT / "docs/design-engine/sourcing/packets/laminate-materials-iraq-domestic-sources-v4"


def test_gfrp_local_fabrication_screens_keep_known_material_costs_and_open_unknowns():
    records = load_catalogue()
    packet = _build(records, PACKETS)
    assert packet["schema"] == "osr-iraq-gfrp-local-fabrication-cost-screens/2"
    assert packet["basis"]["study_area_m2"] == "10"
    assert packet["basis"]["fx_rate"] == "1692.216"
    assert packet["basis"]["executable_fx"] is False
    assert packet["basis"]["uplift_fraction"] == "0.20"
    assert len(packet["studies"]) == 3
    assert sum(len(row["scenarios"]) for row in packet["studies"]) == 9
    assert packet["basis"]["regional_governorates"] == [
        "Al-Muthanna", "Al-Qadisiyyah", "Anbar", "Babil", "Baghdad", "Basrah", "Dhi Qar",
        "Diyala", "Karbala", "Kirkuk", "Maysan", "Najaf", "Nineveh", "Salah al-Din", "Wasit"]
    assert packet["basis"]["regional_wage_rate_iqd_per_person_hour"] == ["6250", "9427.125"]
    assert packet["basis"]["regional_scenario_count"] == 135
    assert sum(len(row["regional_scenarios"]) for row in packet["studies"]) == 135

    expected_gbp = {
        "solid-600gsm": Decimal("726.6491688538932633420822398"),
        "sandwich-600gsm": Decimal("363.3245844269466316710411198"),
        "higher-fibre-sandwich-600gsm": Decimal("265.5468066491688538932633421"),
    }
    ids = {row["record_id"] for row in records}
    for study in packet["studies"]:
        assert study["parent_candidate_id"] == "9c7d0942c9de6056e6afd051549273d0f34a72edf301fdd680ba37d12da7879f"
        assert Decimal(study["listed_material_subtotal_gbp"]) == expected_gbp[study["recipe"]]
        assert Decimal(study["known_listed_material_subtotal_iqd_unrounded"]) == expected_gbp[study["recipe"]] * Decimal("1692.216")
        assert study["source_ids"] and set(study["source_ids"]) <= ids
        assert study["complete_material_cost_iqd"] is None
        assert study["complete_fabrication_cost_iqd"] is None
        assert study["unknown_is_zero"] is False
        assert [scenario["labour_hours_per_10m2"] for scenario in study["scenarios"]] == ["8", "16", "32"]
        material_iqd = expected_gbp[study["recipe"]] * Decimal("1692.216")
        for scenario in study["scenarios"]:
            hours = Decimal(scenario["labour_hours_per_10m2"])
            base = material_iqd + hours * Decimal("9375")
            assert Decimal(scenario["direct_labour_iqd"]) == hours * Decimal("9375")
            assert Decimal(scenario["partial_screen_iqd"]) == (base * Decimal("1.20")).quantize(Decimal("0.01"))
            assert scenario["complete_material_cost_iqd"] is None
            assert scenario["complete_fabrication_cost_iqd"] is None
            assert scenario["unknown_is_zero"] is False
        regional = study["regional_scenarios"]
        assert len(regional) == 45
        assert {row["governorate"] for row in regional} == set(packet["basis"]["regional_governorates"])
        assert {row["labour_hours_per_10m2"] for row in regional} == {"8", "16", "32"}
        assert all(row["wage_employer_burden_included"] is False for row in regional)
        for scenario in regional:
            base = (Decimal(study["known_listed_material_subtotal_iqd_unrounded"])
                    + Decimal(scenario["labour_hours_per_10m2"])
                    * Decimal(scenario["wage_rate_iqd_per_person_hour"]))
            assert Decimal(scenario["direct_labour_iqd_unrounded"]) == (
                Decimal(scenario["labour_hours_per_10m2"])
                * Decimal(scenario["wage_rate_iqd_per_person_hour"]))
            assert Decimal(scenario["direct_known_materials_plus_labour_iqd_unrounded"]) == base
            assert Decimal(scenario["partial_screen_iqd"]) == (base * Decimal("1.20")).quantize(Decimal("0.01"))
            assert scenario["complete_fabrication_cost_iqd"] is None
            assert scenario["unknown_is_zero"] is False

    solid, sandwich, higher = packet["studies"]
    assert {row["material_key"] for row in solid["unresolved_materials"]} == {"adhesive"}
    assert {row["material_key"] for row in sandwich["unresolved_materials"]} == {"core", "adhesive"}
    assert {row["material_key"] for row in higher["unresolved_materials"]} == {"core", "adhesive"}
    assert next(row for row in sandwich["unresolved_materials"] if row["material_key"] == "core")["known_material_mass_kg"] == "17"
    assert packet["complete_installed_cost_iqd"] is None
    assert packet["physical_qualification"] is None


def test_gfrp_screen_refuses_a_modified_source_packet(tmp_path):
    copied = tmp_path / "studies"
    copied.mkdir()
    for recipe in ("solid-600gsm", "sandwich-600gsm", "higher-fibre-sandwich-600gsm"):
        import shutil
        shutil.copytree(PACKETS / recipe, copied / recipe)
    path = copied / "solid-600gsm" / "summary.json"
    raw = path.read_bytes()
    path.write_bytes(b"X" + raw[1:])
    with pytest.raises(ValueError, match="hash differs"):
        _build(load_catalogue(), copied)
