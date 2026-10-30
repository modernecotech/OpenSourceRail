import gzip
import json
from decimal import Decimal
from pathlib import Path

import pytest

from engineering.sourcing import catalogue
from engineering.sourcing.iraq_logistics_scenarios import build_packet
from engineering.sourcing import cli

ROOT = Path(__file__).resolve().parents[3]
SEED = ROOT / "engineering/sourcing/data/iraq-transport-rental-2026-09.json"
PROCUREMENT = ROOT / "docs/design-engine/sourcing/procurement-bom/federated-v06-research-packages-v16.json.gz"
REGIONAL = ROOT / "docs/design-engine/sourcing/domestic-fabrication/regional-estimates-2026-september-v6/iraq-domestic-cost-reference-2026-09.json"


def packet():
    procurement = json.loads(gzip.decompress(PROCUREMENT.read_bytes()))
    regional = json.loads(REGIONAL.read_text())
    return build_packet(catalogue.load_catalogue([SEED]), procurement, regional,
                        procurement_path=PROCUREMENT, regional_cost_path=REGIONAL)


def test_fao_contract_rates_are_typed_and_trace_to_exact_candidate_packages():
    value = packet()
    assert value["span_package_count"] == 81
    assert value["engineering_occurrence_count"] == 486
    assert len(value["package_trace"]) == 81
    assert len(value["engineering_occurrence_ids"]) == 486
    assert value["rental_rate_evidence"]["contract_number"] == "18"
    assert value["rental_rate_evidence"]["trailer_rate_iqd_per_trip"] == "1150000"
    assert value["rental_rate_evidence"]["crane_rate_iqd_per_day"] == "500000"
    assert value["rental_rate_evidence"]["not_a_quote_or_capacity_proof"] is True
    first = value["logistics_scenarios"][0]
    assert first["assumed_trailer_trip_count"] == first["assumed_crane_day_count"] == 81
    assert Decimal(first["conditional_logistics_subtotal_iqd"]) == Decimal("133650000")
    assert first["uplift_fraction"] == "0"
    assert first["physical_lift_capacity_verified"] is False
    assert len(value["separate_material_labour_20_scenarios"]) == 6
    assert len(value["combined_partial_subtotals"]) == 24
    assert value["complete_installed_cost"] is None
    assert value["physical_qualification"] is None
    assert value["unknown_is_zero"] is False


def test_logistics_screen_rejects_mixed_candidate_or_missing_span_scope():
    procurement = json.loads(gzip.decompress(PROCUREMENT.read_bytes()))
    regional = json.loads(REGIONAL.read_text())
    regional["candidate_id"] = "f" * 64
    with pytest.raises(ValueError, match="candidates differ"):
        build_packet(catalogue.load_catalogue([SEED]), procurement, regional,
                     procurement_path=PROCUREMENT, regional_cost_path=REGIONAL)

    regional["candidate_id"] = procurement["candidate_id"]
    del procurement["packages"]
    with pytest.raises(ValueError, match="81 concrete packages"):
        build_packet(catalogue.load_catalogue([SEED]), procurement, regional,
                     procurement_path=PROCUREMENT, regional_cost_path=REGIONAL)


def test_estimate_cli_publishes_source_and_candidate_bound_packet(tmp_path, capsys):
    output = tmp_path / "logistics"
    assert cli.main([
        "estimate", "iraq-logistics",
        "--procurement-bom", str(PROCUREMENT),
        "--regional-cost-reference", str(REGIONAL),
        "--output", str(output),
    ]) == 0
    result = json.loads(capsys.readouterr().out)
    payload = json.loads((output / "iraq-span-logistics-sensitivity.json").read_text())
    manifest = json.loads((output / "manifest.json").read_text())
    assert result["packet_id"] == payload["packet_id"] == manifest["packet_id"]
    assert manifest["complete_installed_cost"] is None
    assert manifest["unknown_is_zero"] is False
