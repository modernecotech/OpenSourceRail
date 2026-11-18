"""Selected v0.7 equipment preview for the existing read-only FUXA adapter."""

import argparse
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import tomllib

from .config import build_package, digest, validate_package
from .fuxa import project


ROOT = Path(__file__).resolve().parents[3]
SELECTION = Path("docs/reference-v07/digital/selected.toml")
HANDOFF = Path("docs/reference-v07/digital/production/handoff.json")
INTERFACES = Path("control-electronics/interface-schedule.json")
INTERFACE_GENERATOR = Path("control-electronics/interface_schedule.py")


def _logical_interfaces(root):
    spec = importlib.util.spec_from_file_location("osr_v07_logical_interfaces", root / INTERFACE_GENERATOR)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    value = json.loads((root / INTERFACES).read_text())
    module.validate(value, root)
    return value


def simulation_package(root: Path = ROOT) -> dict:
    """Build a candidate-bound display package; no live device is configured."""
    root = Path(root)
    selected = tomllib.loads((root / SELECTION).read_text())
    handoff = json.loads((root / HANDOFF).read_text())
    interfaces = _logical_interfaces(root)
    handoff_body = {key: value for key, value in handoff.items() if key != "evaluation_id"}
    handoff_id = sha256(json.dumps(handoff_body, sort_keys=True, separators=(",", ":"),
                                  ensure_ascii=False, allow_nan=False).encode()).hexdigest()
    physical = selected["physical_candidate_id"]
    if (selected.get("schema") != "opensourcerail.v07.digital-selection.1"
            or handoff.get("schema") != "osr-v07-digital-production-handoff/1"
            or handoff.get("evaluation_id") != handoff_id
            or any(value.get("physical_candidate_id") != physical for value in (handoff, interfaces))
            or handoff.get("selection_id") != selected.get("selection_id")
            or handoff.get("source_selection_evaluation_id") != selected.get("evaluation_id")
            or interfaces.get("source_selection_evaluation_id") != selected.get("evaluation_id")
            or handoff.get("source_sha256", {}).get("selected_overlay") != sha256((root / SELECTION).read_bytes()).hexdigest()):
        raise ValueError("Selected production, controls and supervision identities differ")
    equipment = handoff["control_electronics"]["equipment"]
    expected = {"station-dispatch-controller": 12, "grid-protection-gateway": 6,
                "section-control-gateway": 22}
    if any(equipment.get(name, {}).get("quantity") != count for name, count in expected.items()):
        raise ValueError("Selected station, grid or section equipment count differs")
    types = (
        ("station", "station-dispatch-controller", 12, "Station", "osr-station-scada"),
        ("grid", "grid-protection-gateway", 6, "Grid site", "osr-station-scada"),
        ("section", "section-control-gateway", 22, "Line section", "osr-interlocking"),
    )
    assets = [dict(asset_id=f"{kind}-{i:02d}", asset_type=kind, name=f"{label} {i:02d}")
              for kind, _, count, label, _ in types for i in range(1, count + 1)]
    templates = {
        name: {"asset_types": [kind], "label": label, "component_type_id": name,
               "source_crates": [crate], "measurements": {
                   "protection_trip": {"min": 0, "max": 1, "unit": "state", "stale_seconds": 30}},
               "alarms": [{"id": "protection-trip", "measurement": "protection_trip",
                           "high": 0.5, "clear_below": 0.1, "delay_seconds": 0,
                           "repeat_seconds": 60, "priority": "high", "maintenance": False,
                           "response": "Inspect the protected local system; this display cannot reset it"}],
               "commands": {}}
        for kind, name, _, label, crate in types}
    generic = {"template_revision": interfaces["evaluation_id"],
               "rolling_stock_family": physical,
               "historian": {"owner": "osr-integration", "retention_days": 30,
                             "sampling_seconds": 2}, "templates": templates}
    package = build_package(generic, {"city": "reference-30km"}, assets,
                            handoff["evaluation_id"], environment="simulation")
    package.update(physical_candidate_id=physical, selection_id=selected["selection_id"],
                   source_selection_evaluation_id=selected["evaluation_id"],
                   production_handoff_evaluation_id=handoff["evaluation_id"],
                   control_interface_evaluation_id=interfaces["evaluation_id"],
                   source_sha256={str(path): sha256((root / path).read_bytes()).hexdigest()
                                  for path in (SELECTION, HANDOFF, INTERFACES)})
    package["sha256"] = digest({key: value for key, value in package.items() if key != "sha256"})
    validate_package(package)
    return package


def simulation_view(root: Path = ROOT) -> dict:
    """Generate FUXA import preview from the selected simulation package."""
    package = simulation_package(root)
    result = project([package])
    if len(result["devices"]) != 40 or len(result["hmi"]["views"]) != 40:
        raise ValueError("Selected FUXA equipment view count differs")
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-out", type=Path, required=True,
                        help="Write a FUXA simulation project preview")
    args = parser.parse_args(argv)
    result = simulation_view()
    args.project_out.parent.mkdir(parents=True, exist_ok=True)
    args.project_out.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n")
    print(f"wrote {args.project_out} with {len(result['hmi']['views'])} read-only views")


if __name__ == "__main__":
    main()
