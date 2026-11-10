import json
from pathlib import Path

import pytest

from engineering.railway_project.city_cost_bridge import (
    CITY_RESULT, RATE_PACKET, ROOT, _verify_packet, build,
)
from engineering.station_rail.common import digest, identity


def _inputs():
    city = json.loads((ROOT / CITY_RESULT).read_bytes())
    packet = ROOT / RATE_PACKET
    manifest = _verify_packet(packet)
    cost = json.loads((packet / "cost-project-make-buy.json").read_bytes())
    china_cost = json.loads((packet / "cost-china-bulk-buy.json").read_bytes())
    source = {
        CITY_RESULT.as_posix(): digest(ROOT / CITY_RESULT),
        (RATE_PACKET / "manifest.json").as_posix(): digest(packet / "manifest.json"),
        (RATE_PACKET / "cost-project-make-buy.json").as_posix(): digest(packet / "cost-project-make-buy.json"),
        (RATE_PACKET / "cost-china-bulk-buy.json").as_posix(): digest(packet / "cost-china-bulk-buy.json"),
        "engineering/outline/city_civil.py": digest(ROOT / "engineering/outline/city_civil.py"),
    }
    return city, cost, china_cost, manifest, source


def test_candidate_cost_bridge_prices_only_matched_quantity_fragments():
    city, cost, china_cost, manifest, source = _inputs()
    result = build(city, cost, china_cost, manifest, source_sha256=source)

    assert result["city_candidate_id"] == city["candidate_id"]
    assert result["body_candidate_id"] == city["body_candidate_id"]
    assert result["ratebook_source_candidate_id"] != result["city_candidate_id"]
    assert result["ratebook_source_body_candidate_id"] != result["body_candidate_id"]
    assert len(result["matched_rate_lines"]) == 5
    assert result["china_bulk_rate_comparison"]["all_selected_rows_identical_to_project_make_buy"] is True
    assert result["china_bulk_rate_comparison"]["additional_volume_discount_applied"] is False
    assert result["quantity_basis"]["rail_mass_kg_at_60E1_60_21kg_per_m"] == pytest.approx(
        city["quantities"]["running_rail_m"] * 60.21
    )
    assert result["known_candidate_bom_subtotal_usd"] == city["known_counted_BOM_process_subtotal_usd"]
    for case in ("low", "base", "high"):
        expected = city["known_counted_BOM_process_subtotal_usd"][case] + sum(
            row["cost_usd"][case] for row in result["matched_rate_lines"]
        )
        assert result["partial_priced_fragment_sum_usd"][case] == pytest.approx(expected)
    assert result["installed_capex_usd"] is None
    assert result["whole_life_npv_usd"] is None
    assert result["cost_complete"] is False
    assert result["physical_accepted"] is False


def test_ratebook_is_integrity_checked_before_use():
    packet = ROOT / RATE_PACKET
    manifest = _verify_packet(packet)
    broken = dict(manifest)
    broken["files_sha256"] = dict(manifest["files_sha256"])
    name = next(iter(broken["files_sha256"]))
    broken["files_sha256"][name] = "0" * 64
    # The tampered in-memory manifest cannot be admitted as a packet because
    # its packet ID no longer seals those hashes.
    broken["manifest_id"] = identity({k: v for k, v in broken.items() if k != "manifest_id"})
    assert broken["manifest_id"] != manifest["manifest_id"]
    with pytest.raises(ValueError, match="content hash mismatch"):
        _verify_packet(packet, manifest_override=broken)


def test_cost_bridge_refuses_a_mismatched_geography_or_candidate_rate_identity():
    city, cost, china_cost, manifest, source = _inputs()
    changed = dict(cost)
    changed["city_input_id"] = "not-the-same-city-input"
    changed["evaluation_id"] = identity({k: v for k, v in changed.items() if k != "evaluation_id"})
    with pytest.raises(ValueError, match="exact authenticated city input"):
        build(city, changed, china_cost, manifest, source_sha256=source)


def test_published_bridge_packet_integrity():
    packet = ROOT / "docs/design-engine/v06-design-closure/samawah-candidate-cost-bridge-current-source"
    manifest = json.loads((packet / "manifest.json").read_bytes())
    assert manifest["manifest_id"] == identity({k: v for k, v in manifest.items() if k != "manifest_id"})
    assert manifest["file_count"] == len(manifest["files_sha256"])
    for name, expected in manifest["files_sha256"].items():
        assert digest(packet / name) == expected
    bridge = json.loads((packet / "bridge.json").read_bytes())
    assert bridge["evaluation_id"] == identity({k: v for k, v in bridge.items() if k != "evaluation_id"})
    assert bridge["evaluation_id"] == manifest["evaluation_id"]


def test_prior_bridge_packet_is_retained_with_its_metadata_discrepancy():
    packet = ROOT / "docs/design-engine/v06-design-closure/samawah-candidate-cost-bridge"
    manifest = json.loads((packet / "manifest.json").read_bytes())
    assert manifest["manifest_id"] == identity({k: v for k, v in manifest.items() if k != "manifest_id"})
    for name, expected in manifest["files_sha256"].items():
        assert digest(packet / name) == expected
    request = json.loads((packet / "request.json").read_bytes())
    bridge = json.loads((packet / "bridge.json").read_bytes())
    assert len(bridge["matched_rate_lines"]) == 5
    assert "six matching" in request["ratebook_scenario"]

