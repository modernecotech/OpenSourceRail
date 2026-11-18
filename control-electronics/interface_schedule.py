#!/usr/bin/env python3
"""Selected v0.7 logical control boundaries, without physical wiring claims."""

from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
import tomllib


ROOT = Path(__file__).resolve().parents[1]
SELECTED = Path("docs/reference-v07/digital/selected.toml")
EQUIPMENT = Path("control-electronics/reference-v07.toml")
OUTPUT = Path("control-electronics/interface-schedule.json")

# Each loss response is a required design behavior, not a qualified implementation.
INTERFACES = (
    dict(id="occupancy-to-interlocking", source="train-detection", sink="interlocking",
         role="safety_feedback", required_equipment=("train-detection-route-km", "section-control-gateway"),
         on_missing="Treat section occupancy as unknown; withhold new movement authority"),
    dict(id="authority-to-atp", source="interlocking", sink="train-atp",
         role="safety_authority", required_equipment=("atp-channel", "train-radio-link"),
         on_missing="Inhibit traction and request a protected stop within the valid authority envelope"),
    dict(id="door-lock-to-atp", source="door-control", sink="train-atp",
         role="safety_feedback", required_equipment=("door-controller", "atp-channel"),
         on_missing="Withhold traction permission and prevent departure"),
    dict(id="atp-to-independent-brake", source="train-atp", sink="bogie-brake-control",
         role="safety_command", required_equipment=("atp-channel", "bogie-brake-controller",
                                            "train-service-power-unit"),
         on_missing="Request protected stop; brake energy and physical response require qualification"),
    dict(id="station-dispatch-request", source="station-dispatch", sink="interlocking",
         role="safety_request", required_equipment=("station-dispatch-controller", "section-control-gateway"),
         on_missing="Withhold departure; station request cannot create movement authority"),
    dict(id="supply-protection-status", source="grid-protection", sink="train-control",
         role="safety_feedback", required_equipment=("grid-protection-gateway", "car-control-node"),
         on_missing="Inhibit powered traction; retain independent stopping provision"),
    dict(id="train-status-to-fuxa", source="train-control", sink="fuxa-gateway",
         role="observation", required_equipment=("car-control-node", "train-radio-link"),
         on_missing="Display status as unavailable; no movement or brake authority transferred"),
    dict(id="station-status-to-fuxa", source="station-dispatch", sink="fuxa-gateway",
         role="observation", required_equipment=("station-dispatch-controller",),
         on_missing="Display station status as unavailable; protected departure stays local"),
    dict(id="incident-to-erp", source="fuxa-gateway", sink="erpnext",
         role="business_record", required_equipment=(),
         on_missing="Mark lifecycle record pending; do not infer equipment acceptance"),
    dict(id="service-to-passenger-display", source="train-control", sink="passenger-information",
         role="passenger_information", required_equipment=("car-control-node",),
         on_missing="Display service information as unavailable; protection remains independent"),
)


def _encoded(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, indent=2, ensure_ascii=False) + "\n").encode()


def _inputs(root: Path) -> tuple[dict, dict, dict]:
    selected_path, equipment_path = root / SELECTED, root / EQUIPMENT
    selected = tomllib.loads(selected_path.read_text())
    equipment = tomllib.loads(equipment_path.read_text())
    if selected.get("schema") != "opensourcerail.v07.digital-selection.1":
        raise ValueError("Selected v0.7 schema differs")
    candidate = selected.get("physical_candidate_id")
    if (not candidate or equipment.get("schema") != "osr-v07-wheel-control-equipment/1"
            or equipment.get("selected_physical_candidate_id") != candidate):
        raise ValueError("Control equipment and selected physical candidate differ")
    if any(selected.get(key) is not False for key in
           ("physical_accepted", "manufacturing_release", "operating_release")):
        raise ValueError("Logical interfaces cannot promote physical or operating release")
    items = equipment.get("items", {})
    required = {name for row in INTERFACES for name in row["required_equipment"]}
    if not required <= items.keys():
        raise ValueError("Required control equipment is missing: " + ", ".join(sorted(required - items.keys())))
    for name in required:
        quantity_keys = [key for key in items[name] if key.startswith("count_per_")]
        if len(quantity_keys) != 1 or items[name][quantity_keys[0]] <= 0:
            raise ValueError("Positive count basis required for " + name)
    hashes = {str(path): sha256((root / path).read_bytes()).hexdigest()
              for path in (SELECTED, EQUIPMENT)}
    return selected, equipment, hashes


def build(root: Path = ROOT) -> dict:
    selected, equipment, hashes = _inputs(Path(root))
    rows = [dict(row, required_equipment=list(row["required_equipment"])) for row in INTERFACES]
    result = {
        "schema": "osr-v07-logical-control-interfaces/1",
        "physical_candidate_id": selected["physical_candidate_id"],
        "source_selection_evaluation_id": selected["evaluation_id"],
        "selection_id": selected["selection_id"],
        "source_sha256": hashes,
        "interfaces": rows,
        "equipment_item_count": len(equipment["items"]),
        "passenger_display_equipment_quantity": None,
        "passenger_display_price_usd_m": None,
        "physical_connector_pinout": None,
        "communication_transport_and_protocol": None,
        "installed_software_versions": None,
        "safety_qualification": False,
        "live_control_enabled": False,
    }
    result["evaluation_id"] = sha256(_encoded(result)).hexdigest()
    return result


def validate(value: dict, root: Path = ROOT) -> None:
    expected = build(root)
    if value.get("physical_candidate_id") != expected["physical_candidate_id"]:
        raise ValueError("Mixed physical candidate in control interface schedule")
    actual_ids = [row.get("id") for row in value.get("interfaces", [])]
    expected_ids = [row["id"] for row in expected["interfaces"]]
    if len(actual_ids) != len(set(actual_ids)) or set(actual_ids) != set(expected_ids):
        raise ValueError("Required logical interface missing or duplicated")
    if value != expected:
        raise ValueError("Logical interface or source evaluation differs from selected candidate")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    value = build()
    target = ROOT / OUTPUT
    if args.check:
        validate(json.loads(target.read_text()))
        print("current", OUTPUT, value["evaluation_id"])
    else:
        target.write_bytes(_encoded(value))
        print("wrote", OUTPUT, value["evaluation_id"])


if __name__ == "__main__":
    main()
