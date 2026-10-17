"""Inventory, revision isolation, evidence integrity and observation counterexamples."""
from copy import deepcopy
import json

import pytest

from engineering.generative_design import digital_thread as thread
from engineering.generative_design.digital_thread_telemetry import contract, replay


@pytest.fixture(scope="module")
def result():
    return thread.build(concurrency=1)


def test_complete_inventory_has_resolvable_relationships_and_no_false_design_closure(result):
    graph = result["specifications"]
    assert len(graph["items"]) == 345
    assert all(item["source_records"] for item in graph["items"])
    assert len(graph["packages"]) == 63
    nodes = {p["node_id"] for p in graph["packages"]} | {i["id"] for i in graph["items"]}
    assert all(e["parent_id"] in nodes and e["child_id"] in nodes for e in graph["relationships"])
    assert result["summary"]["reference_instances"] == 414
    assert result["summary"]["reference_interfaces"] == 545
    assert result["summary"]["completed_specifications"] == 0
    assert all(not item["detailed_specification_complete"] for item in graph["items"])
    assert any(r["kind"] == "physical-twin-correlation" for r in result["open_requests"])


def test_reference_and_architecture_variations_keep_distinct_configuration_instances(result):
    ids, configurations = [], []
    for packet in result["domains"].values():
        for system in packet["systems"]:
            for variant in system["variants"]:
                configurations.append(variant["configuration_sha256"])
                ids.extend(p["id"] for p in variant["parts"])
    assert len(ids) == len(set(ids))
    assert len(configurations) == len(set(configurations))
    assert result["summary"]["check_states"]["fail"] > 0
    assert result["summary"]["check_states"]["unknown"] > 0


def test_missing_component_and_dangling_edge_cannot_be_hidden(result):
    changed = deepcopy(result)
    changed["specifications"]["items"].pop()
    with pytest.raises(ValueError, match="inventory"):
        thread.validate(changed)
    changed = deepcopy(result)
    changed["specifications"]["relationships"][0]["child_id"] = "nonexistent"
    with pytest.raises(ValueError, match="relationship"):
        thread.validate(changed)


def test_source_conflicts_are_rejected_before_later_hashes_overwrite_them():
    sources = {"README.md": "a" * 64}
    with pytest.raises(ValueError, match="conflicting source"):
        thread.merge_sources(sources, {"README.md": "b" * 64})
    assert sources["README.md"] == "a" * 64


def test_changed_mechanical_mass_recomputes_exact_revision_civil_parents(result):
    studies = result["coupling"]["records"]
    assert len(studies) == 8
    systems = {s["id"]: s for s in result["domains"]["mechanical"]["systems"]}
    for study in studies:
        variant = next(v for v in systems[study["mechanical_system_id"]]["variants"]
                       if v["id"] == study["mechanical_variant_id"])
        assert study["mechanical_configuration_sha256"] == variant["configuration_sha256"]
        context = study["civil_context"]
        base = context["parent_source_case"]
        original_force = sum(a["force_n"] for a in base["axles"])
        changed_force = sum(a["force_n"] for a in context["source_case"]["axles"])
        expected = 1 + study["gross_added_train_mass_kg"] / base["total_mass_kg"]
        assert changed_force / original_force == pytest.approx(expected)
        assert study["removed_mass_kg"] is None and study["net_mass_change_kg"] is None
        assert study["adopted"] is False
        for index, attempt in enumerate(study["attempts"]):
            assert attempt["generation"] == index
            if index:
                assert attempt["parent_id"] == study["attempts"][index - 1]["id"]
                assert attempt["assessment"]["variables"] != study["attempts"][index - 1]["assessment"]["variables"]


def test_source_nulls_and_nested_fields_are_preserved_without_invented_units():
    rows = list(thread.attributes({"dimension_m": 2, "supplier": None, "a/b": {"x~y": []}}))
    assert rows[0]["unit"] == "m"
    assert rows[1]["state"] == "unknown" and rows[1]["value"] is None
    assert rows[2]["pointer"] == "/a~1b/x~0y" and rows[2]["unit"] is None
    assert all(r["unit"] == "mm" for r in thread.attributes({"dimensions_mm": [2, 3, 4]}))


def test_new_campaign_clears_material_load_and_context_caches():
    cleared = set(thread.reset_numerical_caches())
    assert {"engineering.generative_design.civil_detail._contexts",
            "engineering.generative_design.civil_detail._coupled",
            "engineering.generative_design.civil_detail._beam_response",
            "engineering.generative_design.integration.live_envelopes"} <= cleared


def test_changed_loaded_code_requires_new_interpreter(monkeypatch):
    changed = dict(thread._IMPORTED_CODE_SOURCES)
    changed["engineering/generative_design/digital_thread.py"] = "0" * 64
    monkeypatch.setattr(thread, "runtime_code_sources", lambda: changed)
    with pytest.raises(ValueError, match="fresh Python process"):
        thread.freeze_sources({"source_hashes": {}})


def test_manifest_detects_changed_and_extra_outputs(tmp_path, monkeypatch, result):
    monkeypatch.setattr(thread, "build", lambda **kwargs: deepcopy(result))
    folder = tmp_path / "packet"
    thread.run(folder)
    assert thread.verify(folder, replay=True)["numerical_replay_verified"]
    with pytest.raises(ValueError, match="fresh"):
        thread.run(folder)
    summary = folder / "summary.json"
    original = summary.read_bytes()
    summary.write_bytes(original + b" ")
    with pytest.raises(ValueError, match="changed output"):
        thread.verify(folder)
    summary.write_bytes(original)
    (folder / "unrecorded.json").write_text("{}")
    with pytest.raises(ValueError, match="member"):
        thread.verify(folder)
    (folder / "unrecorded.json").unlink()
    assert not thread.verify(folder, current=False)["current_sources_checked"]
    with pytest.raises(ValueError, match="historical"):
        thread.verify(folder, current=False, replay=True)


@pytest.fixture
def specification():
    return contract(dict(features=[dict(instance_id="car-1/hvac-1", role="replaceable-hvac-module")],
        review=dict(configuration_sha256="a" * 64),
        studies=dict(hvac_nominal=dict(final_temperature_c=26.0)),
        inputs=dict(hvac=dict(thermal_assumptions=dict(duration_s=1800))),
        infrastructure=dict(measured_surrogate_gauge_m=1.435)))


def observation(specification, **changes):
    channel = specification["channels"][0]
    row = dict(id="obs-1", channel_id=channel["id"], asset_id=channel["asset_id"],
        configuration_sha256=specification["configuration_sha256"],
        timestamp="2026-10-17T20:00:00Z", value=26.0, unit="degC",
        scenario_id=channel["scenario_id"], sensor_id="unverified-sensor-1",
        calibration_ref="unverified-certificate", source_ref="test-synthetic-record",
        source_sha256="b" * 64, evidence_kind="synthetic", model_time_s=1800.)
    row.update(changes)
    return row


def test_observation_residual_statistics_preserve_bad_fit_and_unverified_provenance(specification):
    rows = [observation(specification, value=27),
            observation(specification, id="obs-2", timestamp="2026-10-17T20:01:00Z", value=25)]
    review = replay(rows, specification)
    channel = review["channels"][0]
    assert channel["bias"] == 0 and channel["rmse"] == 1
    assert not channel["within_provisional_residual_limit"]
    assert channel["includes_synthetic"]
    assert not review["physical_validation"] and not review["calibration_authenticated"]
    assert review["unobserved_channels"] == ["infra.static-gauge"]
    retained = channel["residuals"][0]
    assert retained["source_sha256"] == "b" * 64 and retained["sensor_id"] == "unverified-sensor-1"


@pytest.mark.parametrize("changes", [
    {"configuration_sha256": "c" * 64}, {"asset_id": "wrong-asset"},
    {"unit": "K"}, {"scenario_id": "degraded"}, {"value": True},
    {"value": float("nan")}, {"value": float("inf")}, {"value": 200},
    {"evidence_kind": "validated"}, {"source_sha256": "xyz"},
    {"timestamp": "2026-10-17T20:00:00"}, {"sensor_id": ""},
    {"model_time_s": 10}, {"model_time_s": True},
])
def test_invalid_or_incompatible_observations_are_rejected(specification, changes):
    with pytest.raises(ValueError):
        replay([observation(specification, **changes)], specification)


def test_duplicate_and_backward_sensor_observations_rejected(specification):
    sample = observation(specification)
    with pytest.raises(ValueError, match="duplicate"):
        replay([sample, sample], specification)
    earlier = observation(specification, id="obs-2", timestamp="2026-10-17T19:59:00Z")
    with pytest.raises(ValueError, match="chronological"):
        replay([sample, earlier], specification)


def test_no_synthetic_observation_can_authenticate_a_physical_twin(specification):
    review = replay([observation(specification)], specification)
    assert review["channels"][0]["within_provisional_residual_limit"]
    assert review["physical_validation"] is False
    assert review["source_authenticity_verified"] is False
    assert review["physical_release"] is False
    json.dumps(review, allow_nan=False)
