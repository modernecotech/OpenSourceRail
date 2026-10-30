from decimal import Decimal

from engineering.sourcing.federated_span_rebar_cost import (
    build_packet,
    verify_packet,
)
from engineering.station_rail import ROOT


def test_candidate_bound_rebar_screen_preserves_exact_open_span_accounts():
    packet = build_packet(ROOT)

    assert packet["schema"] == "osr-federated-span-domestic-rebar-screen/1"
    assert packet["candidate_id"] == "9c7d0942c9de6056e6afd051549273d0f34a72edf301fdd680ba37d12da7879f"
    assert packet["evaluation_id"] == "1491f90b02485e6ad9df63ac79b528e9c30e9e6d87041a3dc46b02efd364077b"
    assert packet["selection_id"] is None
    assert packet["span_count"] == 81
    assert Decimal(packet["nominal_concrete_volume_m3"]) == Decimal("1804.8096")
    assert Decimal(packet["reinforcement_mass_proxy_kg"]) == Decimal("216577.152")
    assert packet["estimated_purchase_quantity_t"] is None
    assert len(packet["span_packages"]) == 81
    assert len(packet["network_scenarios"]) == 6

    span = packet["span_packages"][0]
    assert span["package_key"] == "span/0"
    assert span["unlocated_reinforcement_obligation_id"] == "span/0/reinforcement_kg"
    assert span["unlocated_scope_quantity"] is None
    assert span["unlocated_scope_link_id"]
    assert len(span["concrete_engineering_occurrence_ids"]) == 6
    assert len(span["scenarios"]) == 6
    assert all(row["purchase_order_quantity_t"] is None for row in span["scenarios"])


def test_rebar_estimate_uses_material_plus_assumed_hours_then_one_20_percent():
    packet = build_packet(ROOT)
    rows = {(row["region"], row["hours_per_input_tonne"]): row
            for row in packet["network_scenarios"]}

    baghdad_four = rows[("Baghdad", "4")]
    assert Decimal(baghdad_four["direct_material_cost_iqd"]) == Decimal("214194803.328")
    assert Decimal(baghdad_four["direct_labour_cost_iqd"]) == Decimal("8121643.2")
    assert Decimal(baghdad_four["partial_material_labour_plus_20pct_iqd"]) == Decimal("266779735.8336")
    assert baghdad_four["material_benchmark_id"]
    assert baghdad_four["wage_benchmark_id"]
    assert baghdad_four["supplier_offer"] is False
    assert baghdad_four["compatible_product_match"] is False
    assert baghdad_four["installed_cost_iqd"] is None

    muthanna_four = rows[("Al-Muthanna", "4")]
    assert Decimal(muthanna_four["direct_labour_cost_iqd"]) == Decimal("6497314.56")
    assert Decimal(muthanna_four["partial_material_labour_plus_20pct_iqd"]) == Decimal("264830541.4656")


def test_local_rebar_sources_are_discovery_only_and_packet_replays():
    packet = build_packet(ROOT)

    assert {row["source_key"] for row in packet["domestic_supplier_discovery_leads"]} == {
        "iraq.alpha-steel.rebar-range-2026",
        "iraq.hadeediraq.rebar-marketplace",
        "iraq-darin-steel-rebar",
        "iraq.al-anmaa-rebar",
        "iraq.qaiwan-steel-rebar",
    }
    assert all(row["discovery_only"] is True
               and row["compatible_product_match"] is False
               and row["supplier_offer"] is False
               and row["price"] is None
               for row in packet["domestic_supplier_discovery_leads"])

    result = verify_packet(root=ROOT)
    assert result["verified"] is True
    assert result["packet_id"] == packet["packet_id"]
    assert result["complete_fabrication_cost_iqd"] is None
