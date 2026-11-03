from copy import deepcopy
import json
import os
import shutil

import pytest

from engineering.design_search import selected_reference_journey, station_demonstrator as s
from engineering.station_rail.common import encoded, identity


@pytest.fixture(scope="module")
def bundle():
    return selected_reference_journey.build()


@pytest.fixture(scope="module")
def record(bundle):
    return s.build(bundle)


def reseal(value, field):
    value.pop(field)
    value[field] = identity(value)
    return value


def test_exact_selected_schema_binds_three_distinct_subjects(bundle, record):
    subject = record["subject_binding"]
    assert subject["vehicle_candidate_id"] == bundle["reference_candidate_id"]
    assert subject["journey_adapter_id"] == bundle["candidate_id"]
    assert subject["vehicle_candidate_id"] != subject["journey_adapter_id"]
    assert subject["body_candidate_id"] == bundle["body_candidate_id"]
    assert subject["bundle_definition_id"] == bundle["definition_id"]
    assert {p["id"] for p in record["protocols"]} == {"T05", "T07", "T08"}
    for protocol in record["protocols"]:
        assert all(protocol["subject_binding"][k] == v for k, v in subject.items())
        assert protocol["measured_channels"] and protocol["next_requests"]
        assert protocol["requirement_policy_links"]
        assert protocol["article_binding"]["as_built_candidate_id"] is None
        assert protocol["executed"] is False
        assert protocol["native_dispatch_allowed"] is False
        assert all(c["limit"] is None and c["approval_status"] == "unassigned"
                   for c in protocol["acceptance_criteria"])
    motor = next(p for p in record["protocols"] if p["id"] == "T05")
    journey = next(p for p in record["protocols"] if p["id"] == "T08")
    assert motor["subject_binding"]["passive_secondary_component_id"] == bundle["propulsion_component_id"]
    assert motor["subject_binding"]["wayside_primary_candidate_id"] is None
    assert motor["subject_binding"]["complete_primary_secondary_article_defined"] is False
    assert "Secondary longitudinal start" in motor["coordinate_definition"]["position"]
    assert "leading-nose route chainage" in journey["coordinate_definition"]["position"]
    assert "transforms" in motor["coordinate_definition"]["conversion_to_train_route"]


def test_full_train_geometry_is_not_point_train_command_or_available_thrust(record):
    zone = record["reference_shared_winding"]
    context = record["conditional_journey_context"]
    assert zone["length_m"] == 900.0
    assert zone["required_shared_winding_m"] > 800.0
    assert context["commanded_leading_point_windows_m"] == [[0.0, 500.0]]
    assert context["reference_geometry_equivalence_established"] is False
    assert context["journey_results_imported"] is False
    assert context["available_motor_map_id"] is None
    assert record["accepted_available_force_map_id"] is None
    demand = record["analytical_demand"]
    assert demand["peak_launch_force_N_per_car"] == pytest.approx(11102.794909827868)
    assert demand["actual_traction_force_available_N"] is None
    assert not demand["physical_journey_completed"]
    assert not zone["physical_headway_qualified"]
    assert not zone["section_handoff_qualified"]
    assert record["complete_installed_mass_kg"] is None
    assert record["service_targets"] == dict(headway_s=120.0, normal_people_per_train=276,
        normal_passengers_per_hour_per_direction_arithmetic=8280.0,
        protected_headway_demonstrated=False)
    assert record["integrated_selection"] is None
    assert all(record[k] is False for k in s.FLAGS)
    assert all(name in record["source_sha256"] for name in (
        s.railway_architecture.SPEC, s.civil.PRODUCER,
        "engineering/design_search/capabilities.py"))


def test_civil_load_and_station_demonstrators_share_exact_selected_vehicle(record):
    from engineering.design_search import civil_demonstrator
    civil = civil_demonstrator.calculate(maximum_tasks=0)
    subject = record["subject_binding"]
    for key in ("vehicle_candidate_id", "vehicle_evaluation_id", "selection_id"):
        assert civil[key] == subject[key]
    # Civil alternatives remain distinct from the station journey adapter and
    # neither handoff can select a combined railway from this identity match.
    assert subject["journey_adapter_id"] not in {r["candidate_id"] for r in civil["evidence"]}
    assert civil["integrated_selection"] is record["integrated_selection"] is None


@pytest.fixture
def relocated_root(tmp_path, record):
    root = tmp_path / "sources"
    for name in record["source_sha256"]:
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(s.ROOT / name, path)
    return root


def test_architecture_source_bytes_affect_handoff_without_changing_hardware(relocated_root, record):
    path = relocated_root / s.railway_architecture.SPEC
    path.write_bytes(path.read_bytes() + b"\n# Byte-only source revision.\n")
    changed = s.build(root=relocated_root)
    assert changed["subject_binding"] == record["subject_binding"]
    assert changed["evaluation_id"] != record["evaluation_id"]


@pytest.mark.parametrize("module,name", s.MODULES, ids=[name for _, name in s.MODULES])
def test_different_executing_dependency_is_rejected(module, name, tmp_path, monkeypatch):
    different = tmp_path / "different.py"
    different.write_bytes(b'raise RuntimeError("wrong producer")\n')
    monkeypatch.setattr(module, "__file__", str(different))
    with pytest.raises(ValueError, match="Executing station dependency"):
        s.build()


def test_relocated_root_cannot_attribute_other_architecture_code(relocated_root):
    path = relocated_root / s.railway_architecture.PRODUCER
    path.write_bytes(path.read_bytes() + b'\nraise RuntimeError("different producer")\n')
    with pytest.raises(ValueError, match="Executing station dependency"):
        s.build(root=relocated_root)


def test_verification_rejects_symlink_and_fifo_without_reading(tmp_path, record):
    target = tmp_path / "station"
    target.mkdir()
    source = tmp_path / "source.json"
    source.write_bytes(encoded(record))
    path = target / "result.json"
    path.symlink_to(source)
    with pytest.raises(ValueError, match="Regular non-symlink"):
        s.verify(target)
    path.unlink()
    os.mkfifo(path)
    with pytest.raises(ValueError, match="Regular non-symlink"):
        s.verify(target)


def test_oversized_record_is_rejected_before_loading(tmp_path):
    target = tmp_path / "station"
    target.mkdir()
    with (target / "result.json").open("wb") as handle:
        handle.truncate(s.MAX_RESULT_BYTES + 1)
    with pytest.raises(ValueError, match="size budget"):
        s.verify(target)


@pytest.mark.parametrize("field", ["reference_candidate_id", "candidate_id", "selection_id",
                                   "vehicle_evaluation_id", "propulsion_component_id",
                                   "requirement_revision"])
def test_resealed_mixed_selected_identity_is_rejected(bundle, field):
    changed = deepcopy(bundle)
    changed[field] = "0" * 64
    reseal(changed, "definition_id")
    with pytest.raises(ValueError, match="current selection"):
        s.build(changed)


def test_resealed_geometry_swap_cannot_reuse_selected_adapter(bundle):
    changed = deepcopy(bundle)
    changed["architecture_case"]["commanded_power_windows_m"] = [[0.0, 900.0]]
    reseal(changed, "definition_id")
    with pytest.raises(ValueError, match="architecture_case"):
        s.build(changed)


def test_immutable_output_verified_against_current_sources_and_selection(tmp_path, record, monkeypatch):
    # Build once; verification below still executes the real source/selection build.
    target = tmp_path / "station"
    s.write(target)
    assert s.verify(target)["verified"]
    with pytest.raises(FileExistsError):
        s.write(target)
    path = target / "result.json"
    original = path.read_bytes()
    changed = json.loads(original)
    changed["physical_accepted"] = True
    path.write_bytes(encoded(reseal(changed, "evaluation_id")))
    with pytest.raises(ValueError, match="Station handoff differs"):
        s.verify(target)
    path.write_bytes(original)
    build = s.build
    def different_source(*args, **kwargs):
        value = build(*args, **kwargs)
        value["source_sha256"][s.PRODUCER] = "0" * 64
        return reseal(value, "evaluation_id")
    monkeypatch.setattr(s, "build", different_source)
    with pytest.raises(ValueError, match="Station handoff differs"):
        s.verify(target)


def test_resealed_synthetic_geometry_or_source_edit_is_not_accepted(tmp_path, record):
    target = tmp_path / "station"
    target.mkdir()
    path = target / "result.json"
    changes = []
    value = deepcopy(record)
    value["reference_shared_winding"]["length_m"] = 500.0
    changes.append(value)
    value = deepcopy(record)
    value["accepted_available_force_map_id"] = "synthetic-map"
    changes.append(value)
    value = deepcopy(record)
    value["source_sha256"][s.PRODUCER] = "0" * 64
    changes.append(value)
    for value in changes:
        path.write_bytes(encoded(reseal(value, "evaluation_id")))
        with pytest.raises(ValueError, match="Station handoff differs"):
            s.verify(target)
