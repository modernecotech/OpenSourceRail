import json
from pathlib import Path

import pytest

from engineering.sourcing import cli
from engineering.sourcing.iraq_local_gfrp_cost_scenarios import build_packet

ROOT = Path(__file__).resolve().parents[3]
LAMINATE = ROOT / "docs/design-engine/sourcing/packets/laminate-materials-iraq-domestic-sources-v18/solid-600gsm"


def test_local_gfrp_screen_uses_listed_fabric_and_keeps_resin_unknown():
    packet = build_packet(LAMINATE)
    assert packet["source_candidate_id"] == "9c7d0942c9de6056e6afd051549273d0f34a72edf301fdd680ba37d12da7879f"
    assert packet["physical_hypothesis"]["same_physical_candidate_as_reference"] is False
    assert packet["physical_hypothesis"]["material_architecture_equivalence"] is False
    assert packet["priced_material"]["purchased_bag_count"] == 89
    assert packet["priced_material"]["purchased_area_m2"] == "89"
    assert packet["priced_material"]["purchased_mass_kg"] == "26.7"
    assert [row["partial_fabric_plus_labour_plus_20_iqd_per_10m2"] for row in packet["scenarios"]] == [
        "463800.00", "553800.00", "733800.00"]
    assert len(packet["local_resin_price_leads_not_applied"]) == 3
    assert all(row["included_in_partial_fabric_material_subtotal"] is False
               for row in packet["local_resin_price_leads_not_applied"])
    assert packet["complete_material_cost_iqd"] is None
    assert packet["complete_fabrication_cost_iqd"] is None
    assert packet["unknown_is_zero"] is False
    assert all(row["used_in_current_cost_scenarios"] is False
               for row in packet["historical_labour_references"])


def test_cli_publishes_a_source_bound_local_material_screen(tmp_path, capsys):
    output = tmp_path / "local-gfrp-screen"
    assert cli.main([
        "estimate", "iraq-local-gfrp", "--laminate-packet", str(LAMINATE),
        "--output", str(output),
    ]) == 0
    result = json.loads(capsys.readouterr().out)
    assert result["scenario_count"] == 3
    assert result["partial_cost_iqd"] == ["463800.00", "553800.00", "733800.00"]
    assert result["complete_installed_cost_iqd"] is None
    packet = json.loads((output / "iraq-local-gfrp-retail-screen.json").read_text())
    manifest = json.loads((output / "manifest.json").read_text())
    assert manifest["packet_id"] == packet["packet_id"]
    assert manifest["complete_installed_cost_iqd"] is None


def test_nonmatching_laminate_packet_is_rejected(tmp_path):
    with pytest.raises(ValueError, match="Regular 10 m2 laminate publication required"):
        build_packet(tmp_path)
