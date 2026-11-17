"""Rebuild the source-bound, explicitly unpriced v0.7 powered-vehicle cost bridge.

Only the same physical research child and the synthetic 30 km service control
are admitted. A new candidate or scope mapping requires a deliberate review.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = Path("docs/design-engine/v07-powered-cost")
SOURCES = {
    "architecture": Path("docs/design-engine/v07-architecture-decision/result.json"),
    "prototype": Path("docs/design-engine/v07-prototype-bundle/packet/result.json"),
    "line30": Path("docs/design-engine/line30-current-20261117/result.json"),
}
EXPECTED_CANDIDATE = "ac550fe8ff23f20cb1ae5b142f4ef6160afc9de6efe7850754bac96a7789327d"
BENCHMARK_URL = "https://openknowledge.worldbank.org/server/api/core/bitstreams/c3c239ef-4236-4510-976a-58f05ffc4e72/content"
DIRECT = {
    "rolling-stock-and-vehicle-interfaces", "guideway-beams-bearings-and-detail",
    "piers-foundations-and-groundworks", "span-haul-and-erection",
    "launch-machinery-and-converters", "traction-grid-and-protection",
    "auxiliary-charging-and-grid", "fleet-spares-and-recovery",
    "project-risk-contingency",
}
RFQ = {
    "rolling-stock-and-vehicle-interfaces": "Complete delivered and assembled 51-set powered vehicle quote: 1,224 motor/gear/axle installations, 612 cooled inverter racks, 306 roof collectors, 306 roof-HV boxes, 612 rail-brake modules, wiring/cooling/protection, spare assemblies; approved installed mass and interfaces; retire old launch interfaces only where itemised.",
    "guideway-beams-bearings-and-detail": "Matched 30 km two-track 20 m segmented versus new 10 m simply-supported beam/bearing/joint design, fatigue and OLE mount load; quote material, fabrication and QA per accepted span; no old 10 m segment price transfer.",
    "piers-foundations-and-groundworks": "Surveyed alignment and geotechnical schedule, foundation/pier count and load including OLE, bearing reactions and utility conflicts; unit rates by ground class.",
    "span-haul-and-erection": "Matched crane radius/hook load, segment haul, lifts, temporary towers or new 10 m lifts, crew/day and traffic management on actual site.",
    "rails-welding-and-protected-access": "Confirm reused track quantity and revised rail-brake wear/damage, return-current bond and evacuation/maintenance access; quote any changed rail or walkway scope.",
    "launch-machinery-and-converters": "Itemised credit for removed cable-capstan/launch units and their interfaces; new vehicle drive is priced in vehicle scope, no double count.",
    "traction-grid-and-protection": "60 track-km 1.5 kV rigid overhead/return, supports, isolation, sectioning, feeders, rectifier substations, grid connections, regen sink, protection, commissioning and access; interface schedule preventing overlap with vehicle/auxiliary grid.",
    "stations-platforms-and-access": "12 station powered-zone and OLE clearances, platform length/door datum, accessibility, barriers, evacuation and installation; quote changed station equipment and any removed launcher works.",
    "turnbacks-and-line-controls": "Two terminal turnback layouts and line-control changes for 51-set powered operation, protected section transitions, stopping and recovery; identify inherited controls and new ones.",
    "auxiliary-charging-and-grid": "Retained 82.8 kWh/car service battery and 35 s charging arrangement under actual supply architecture; separate auxiliary feeders/grid/chargers from traction-grid quote.",
    "production-depot-land-and-utilities": "Depot and tooling for 51 powered sets, motor/gear/brake/collector overhaul, isolation and roof access; surveyed land/utility works, make/buy and local QA.",
    "fleet-spares-and-recovery": "Fleet-specific spares, commissioning, failed-OLE rescue store/tow and recovery vehicles; no credit for unpriced active/spare change.",
    "prototypes-testing-and-tax": "Candidate-specific full-scale drive, hot-brake, OLE-loss, insulation, dynamic civil, independent tests; import duties/tax by actual bought parts and origin.",
    "project-risk-contingency": "Recalculate quantified risk from complete candidate direct-cost basis, site/ground, safety and supplier maturity; old contingency dollar amount not transferable.",
}


def canonical(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")


def encoded(value: object) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8")


def build(root: Path = ROOT) -> tuple[bytes, bytes]:
    raw = {name: (root / path).read_bytes() for name, path in SOURCES.items()}
    arch, proto, line = (json.loads(raw[name]) for name in SOURCES)
    candidate = proto["candidate"]["candidate_id"]
    if candidate != EXPECTED_CANDIDATE or proto["evaluation"]["physical_candidate_id"] != candidate:
        raise ValueError("powered cost research candidate changed; review and re-scope the price bridge")
    if proto["selection"]["candidate_id"] != candidate or proto["selection"]["selected_installed_reference"]:
        raise ValueError("powered candidate/selection continuity or research-only status differs")
    service = arch["same_assumption_service"]
    if (service["route_km"], service["trackways"], service["stations"], service["normal_places_per_train"], service["headway_s"], service["dwell_s"]) != (30, 2, 12, 276, 120, 35):
        raise ValueError("equal-service 30 km control changed; review all quotation quantities")
    rows = [r for r in arch["service_rows"] if r["architecture"] == "powered-wheel-continuous-supply" and r["grade_magnitude"] == 0]
    if len(rows) != 1 or (rows[0]["active_trainsets"], rows[0]["spare_trainsets"], rows[0]["total_trainsets"]) != (44, 7, 51):
        raise ValueError("powered fleet changed; review RFQ counts and lifecycle")
    fleet = rows[0]["total_trainsets"]
    physical = proto["candidate"]["physical_definition"]["mechanical_definition"]
    if physical["cars"] != 6 or physical["normal_places_per_car"] * 6 != 276:
        raise ValueError("powered vehicle formation changed")
    quote_counts = {r["item"]: r["count_six_car_train"] for r in proto["evaluation"]["engineering_BOM"]["quote_rows"]}
    required_counts = {"motor-gear-cartridge": 24, "inverter-cooled-rack": 12, "roof-collector": 6, "roof-hv-isolation": 6, "independent-rail-brake-bogie": 12}
    if any(quote_counts.get(key) != count for key, count in required_counts.items()):
        raise ValueError("powered BOM counts changed; review RFQ scope")
    source_hashes = {str(path): hashlib.sha256(raw[name]).hexdigest() for name, path in SOURCES.items()}
    source_hashes[str(Path("engineering/design_search/v07_powered_cost.py"))] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    base_variant = line["variants"][0]
    if base_variant["installed_capital_usd"]["base"] != arch["line30_base_installed_capital_proxy_usd"]:
        raise ValueError("line30 proxy no longer matches the architecture bridge")
    if base_variant["service"]["total_trainsets"] != 52:
        raise ValueError("line30 fleet comparator changed")
    input_doc = {
        "schema": "osr-v07-powered-cost-input/1", "source_sha256": source_hashes,
        "physical_candidate_id": candidate,
        "physical_evaluation_id": proto["evaluation"]["evaluation_id"],
        "selection_id": proto["selection"]["selection_id"],
        "equal_service_evaluation_id": arch["evaluation_id"],
        "base_other_candidate_evaluation_id": base_variant["evaluation_id"],
        "cost_question": "Can the 51-set powered-bogie, rigid 1.5 kV DC overhead child receive one defensible 14-scope installed and 30-year central planning price at the same synthetic 30 km service?",
        "pricing_rule": "Material unknown quantities or unit rates remain null, not zero. No passive-fleet price transfer, old launch credit, or proxy total relabel.",
        "service_control": {"route_km": 30, "track_km": 60, "stations": 12, "cars_per_train": 6,
                            "normal_places_per_train": 276, "headway_s_conditional": 120, "dwell_s": 35,
                            "fleet_active": 44, "fleet_spare": 7, "fleet_total": fleet,
                            "train_length_m": service["full_train_length_m"], "speed_cap_kmh": service["speed_cap_m_s"] * 3.6,
                            "moving_time_allowance_fraction": 0.05, "terminal_turnback_s": 180,
                            "lifecycle_years": base_variant["service"]["requirements"]["design_life_years"],
                            "discount_rate_real": base_variant["service"]["requirements"]["real_discount_rate"]},
        "budget": {"architecture_count": 1, "native_solves": 0, "large_artifacts": 0},
    }
    input_doc["input_id"] = hashlib.sha256(canonical(input_doc)).hexdigest()
    bridge = []
    for row in arch["capital_14_scope_bridge"]:
        scope = row["scope"]
        if scope not in RFQ or row["candidate_installed_usd"] is not None:
            raise ValueError("14-scope bridge changed or contains a candidate price")
        bridge.append({"scope": scope, "source_line_keys": row["source_line_keys"],
                       "base_other_candidate_proxy_usd": row["line30_base_proxy_usd"],
                       "candidate_installed_usd": None,
                       "pricing_status": "directly_changed_unpriced" if scope in DIRECT else "interface_or_quantity_check_required",
                       "minimum_RFQ": RFQ[scope]})
    if len(bridge) != len(RFQ) or len({r["scope"] for r in bridge}) != len(RFQ):
        raise ValueError("expected 14 unique procurement scopes")
    keys = [key for row in bridge for key in row["source_line_keys"]]
    if len(keys) != len(set(keys)) or set(keys) != {r["key"] for r in base_variant["capital_lines"]}:
        raise ValueError("capital line mapping does not exactly cover the base")
    base = sum(r["base_other_candidate_proxy_usd"] for r in bridge)
    changed = sum(r["base_other_candidate_proxy_usd"] for r in bridge if r["scope"] in DIRECT)
    if abs(base - arch["line30_base_installed_capital_proxy_usd"]) > 0.01:
        raise ValueError("14-scope proxy does not reconcile")
    quantities = {"fleet_trainsets": fleet, "fleet_cars": fleet * physical["cars"],
                  "motor_gear_axle_units": fleet * quote_counts["motor-gear-cartridge"],
                  "cooled_inverter_racks": fleet * quote_counts["inverter-cooled-rack"],
                  "roof_collectors": fleet * quote_counts["roof-collector"],
                  "roof_hv_isolation_boxes": fleet * quote_counts["roof-hv-isolation"],
                  "rail_brake_modules": fleet * quote_counts["independent-rail-brake-bogie"],
                  "rail_brake_shoes": fleet * quote_counts["independent-rail-brake-bogie"] * physical["track_brake_module"]["shoes_per_module"],
                  "rigid_overhead_track_km": service["route_km"] * service["trackways"],
                  "stations": service["stations"], "old_capstan_fleet_trainsets": 52,
                  "old_capstan_delivered_trainset_unit_proxy_usd_not_transferable": arch["line30_base_delivered_trainset_unit_proxy_usd"],
                  "station_launch_machinery_base_other_candidate_proxy_usd_not_credited": next(r["base_other_candidate_proxy_usd"] for r in bridge if r["scope"] == "launch-machinery-and-converters")}
    result = {
        "schema": "osr-v07-powered-cost-quote-hold/1", "input_id": input_doc["input_id"],
        "source_sha256": source_hashes, "physical_candidate_id": candidate,
        "physical_evaluation_id": input_doc["physical_evaluation_id"], "selection_id": input_doc["selection_id"],
        "cost_evidence_status": "held_unpriced_material_scopes", "evidence_maturity": "source-bound_analytical_price_gap",
        "engineering_accepted": False, "physical_accepted": False,
        "candidate_installed_capital_usd": None, "candidate_30_year_npv_usd": None,
        "base_other_candidate_proxy_installed_usd": base,
        "base_other_candidate_proxy_30_year_npv_usd": arch["line30_base_30_year_npv_proxy_usd"],
        "base_directly_changed_scope_proxy_usd": changed, "base_directly_changed_scope_share": changed / base,
        "capital_14_scope_bridge": bridge,
        "lifecycle_30_year": {"candidate_npv_usd": None,
                              "source_lines": [r["key"] for r in base_variant["lifecycle_lines"]],
                              "required_reprice": "Energy at measured traction/regen/auxiliary efficiency and tariff; 51-set operations; powered bogie and rail-brake maintenance; rigid OLE/rectifier maintenance and renewals; correction/disruption; rescue standby; vehicle, power, civil, brake and battery scheduled renewals; decommissioning. Preserve 4% real discount and 30 years, prevent renewal overlap."},
        "quantity_handoff": quantities,
        "cost_barrier": "The priced base is a different physical candidate. Directly changed scopes contain 77.5% of that price, and power and civil quantities are unselected. Public OLE analogues do not specify this 1.5 kV rigid-DC, elevated, site-installed package or lifecycle. A central total would be invented.",
        "public_benchmark_for_scale_only": {"source_url": BENCHMARK_URL,
                                            "straightforward_overhead_usd_per_track_km_approx": 1000000,
                                            "naive_60_track_km_usd_not_candidate_cost": 60000000,
                                            "source_annual_maintenance_usd_per_track_km_approx": 10000,
                                            "naive_annual_usd_not_candidate_cost": 600000,
                                            "non_transfer_reason": "Generic overhead system; no rigid 1.5 kV DC, route civil, Iraq grid/site, station protection, tax, date or package boundary."},
        "acceptance_gate": "Receive integrated itemised quotes and site/physical data for all 14 scopes and seven lifecycle lines; independently reconcile before issuing one candidate central estimate. This result does not release manufacture, operation or finance.",
    }
    result["evaluation_id"] = hashlib.sha256(canonical(result)).hexdigest()
    return encoded(input_doc), encoded(result)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true", help="atomically regenerate both source-bound records")
    mode.add_argument("--check", action="store_true", help="verify both records against current source bytes")
    args = parser.parse_args()
    generated = build()
    for name, raw in zip(("input.json", "result.json"), generated):
        path = ROOT / OUT / name
        if args.check:
            if not path.is_file() or path.read_bytes() != raw:
                parser.exit(1, f"stale powered cost evidence: {path}\n")
        else:
            temporary = path.with_name(path.name + ".tmp")
            temporary.write_bytes(raw)
            temporary.replace(path)
    print("powered cost quote hold current; candidate capital and 30-year NPV remain null")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
