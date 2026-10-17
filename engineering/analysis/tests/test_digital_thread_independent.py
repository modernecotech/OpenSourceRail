"""Independent reviewer counterexamples: provenance, graph links and controls."""

from copy import deepcopy
import math

import pytest

from engineering.generative_design import digital_thread as thread
from engineering.generative_design import digital_thread_telemetry as telemetry
from engineering.generative_design.twin_software_factory import fault_suite, replay_precharge


def _observation_fixture():
    specification = dict(schema="osr-design-observation-contract/1",
        configuration_sha256="a"*64, maximum_records=10,
        required_fields=["id", "channel_id", "asset_id", "configuration_sha256", "timestamp",
            "value", "unit", "scenario_id", "sensor_id", "calibration_ref", "source_ref",
            "source_sha256", "evidence_kind"],
        channels=[dict(id="gauge", asset_id="rail", unit="m", scenario_id="static",
                       model_value=1.435, residual_limit=.002, minimum_value=.5,
                       maximum_value=3., model_time_s=1800.)])
    sample = dict(id="one", channel_id="gauge", asset_id="rail",
        configuration_sha256="a"*64, timestamp="2026-10-17T12:00:00Z",
        value=1.435, unit="m", scenario_id="static", sensor_id="claimed-sensor",
        calibration_ref="claimed-calibration", source_ref="claimed-source",
        source_sha256="0"*64, evidence_kind="field-observation-unverified", model_time_s=1800.)
    return specification, sample


def test_actual_package_relationships_resolve_to_actual_graph_nodes():
    graph = thread.specification_graph()
    nodes = {p["node_id"] for p in graph["packages"]} | {p["id"] for p in graph["items"]}
    assert all(r["parent_id"] in nodes and r["child_id"] in nodes
               for r in graph["relationships"])


def test_conflicting_frozen_source_revisions_cannot_be_overwritten():
    path = "engineering/generative_design/digital_thread.py"
    mapping = {path: "a"*64}
    with pytest.raises(ValueError, match="conflicting source"):
        thread.merge_sources(mapping, {path: "b"*64})
    assert mapping[path] == "a"*64


def test_matching_residual_and_claimed_provenance_do_not_authenticate_physical_twin():
    specification, sample = _observation_fixture()
    result = telemetry.replay([sample], specification)
    assert result["channels"][0]["within_provisional_residual_limit"]
    assert not result["source_authenticity_verified"]
    assert not result["calibration_authenticated"]
    assert not result["physical_validation"] and not result["physical_release"]


@pytest.mark.parametrize("value", [True, math.nan, math.inf, -.1, 100.])
def test_invalid_numeric_observations_cannot_enter_residual_statistics(value):
    specification, sample = _observation_fixture()
    sample["value"] = value
    with pytest.raises(ValueError):
        telemetry.replay([sample], specification)


@pytest.mark.parametrize("field,value", [
    ("configuration_sha256", "b"*64), ("asset_id", "different-rail"),
    ("unit", "mm"), ("scenario_id", "dynamic"),
    ("evidence_kind", "validated"), ("source_sha256", "not-a-sha"),
    ("timestamp", "2026-10-17T12:00:00+01:00")])
def test_revision_asset_units_scenario_and_source_claim_boundaries(field, value):
    specification, sample = _observation_fixture()
    sample[field] = value
    with pytest.raises(ValueError):
        telemetry.replay([sample], specification)


def test_fresh_message_cannot_conceal_frozen_elapsed_clock():
    first = deepcopy(fault_suite()[0]["frames"][0])
    delayed = deepcopy(first)
    delayed.update(sequence=2, observed_s=10000., received_s=10000.02)
    result = replay_precharge([first, delayed])
    assert not result["rows"][-1]["request_main_close"]
    assert result["final_state"] == "LOCKOUT"


def test_receipt_clock_regression_latches_despite_fresh_increasing_observation():
    first = deepcopy(fault_suite()[0]["frames"][0])
    first["received_s"] = 3.59
    second = deepcopy(first)
    second.update(sequence=2, observed_s=3.55, received_s=3.56)
    second["signals"]["elapsed_s"] = 3.55
    result = replay_precharge([first, second])
    assert not result["rows"][-1]["request_main_close"]
    assert result["final_state"] == "LOCKOUT"


@pytest.mark.parametrize("time", [None, True, 1799., math.nan])
def test_endpoint_observations_require_exact_finite_model_time(time):
    specification, sample = _observation_fixture()
    if time is None:
        sample.pop("model_time_s")
    else:
        sample["model_time_s"] = time
    with pytest.raises(ValueError):
        telemetry.replay([sample], specification)


def test_replay_keeps_sensor_time_calibration_source_and_configuration_provenance():
    specification, sample = _observation_fixture()
    expected = deepcopy(sample)
    result = telemetry.replay([sample], specification)
    row = result["channels"][0]["residuals"][0]
    provenance = {key: row[key] for key in expected}
    assert provenance == expected
    sample["source_ref"] = "later-mutation"
    assert {key: row[key] for key in expected} == expected
