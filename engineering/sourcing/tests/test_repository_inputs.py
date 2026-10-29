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
    assert len(requirements) == 31989
    assert categories["propulsion"] > 0
    assert categories["civil"] > 0
    assert categories["body-materials"] > 0
    assert categories["running-gear"] > 0
    assert value["payload"]["physical_accepted"] is False
    assert value["payload"]["complete_installed_BOM"] is False
