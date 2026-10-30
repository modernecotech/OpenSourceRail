"""Executable checks against repository-owned, source-bound twin inputs."""
from pathlib import Path
from collections import Counter

from engineering.sourcing.inputs import load_twin
from engineering.sourcing.requirements import extract_requirements


ROOT = Path(__file__).resolve().parents[3]


def test_real_vehicle_registry_resolves_without_claiming_the_whole_railway():
    value = load_twin(ROOT / "docs/design-engine/frame-refinement/packet")
    requirements = extract_requirements(value["payload"])
    assert len(requirements) == 3183
    assert all(item["namespace"] == "component_registry" for item in requirements)
    assert sum(len(item["occurrence_ids"]) for item in requirements) == 40488
    assert value["physical_qualification"] is None


def test_real_federated_cell_input_includes_more_than_the_vehicle():
    archive = ROOT / "docs/design-engine/digital-twin/3a07936303fe5d471a88c95875e55b73b13a5cda94e98d1169f168c647766a93.tar.gz"
    value = load_twin(archive, member="federated-bom.json.gz")
    requirements = extract_requirements(value["payload"])
    categories = Counter(item["category"] for item in requirements)
    assert len(value["payload"]["engineering_BOM"]) == 31989
    assert len(requirements) == 7042
    assert sum(len(item["occurrence_ids"]) for item in requirements) == 27216
    assert len(value["payload"]["unresolved_occurrence_ids"]) == 4773
    assert categories["propulsion"] > 0
    assert categories["civil"] > 0
    assert categories["body-materials"] > 0
    assert categories["running-gear"] > 0
    assert value["payload"]["physical_accepted"] is False
    assert value["payload"]["complete_installed_BOM"] is False


def test_sealed_sourcing_input_replays_without_rewrapping_or_relabeling_candidate():
    path = ROOT / "docs/design-engine/sourcing/packets/frame-vehicle-iraq-domestic-sources-v6/input.json.gz"
    value = load_twin(path)
    requirements = extract_requirements(value["payload"])
    assert value["schema"] == "osr-sourcing-twin-input/1"
    assert value["payload"]["candidate_id"] == "6fd30b694342266d60698018f14c492b90c25ac048c3ebfd7157a7031d3cef62"
    assert {row["candidate_id"] for row in requirements} == {value["payload"]["candidate_id"]}
    assert len(requirements) == 3183
    assert value["physical_qualification"] is None
