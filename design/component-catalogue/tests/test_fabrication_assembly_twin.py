"""Regression checks for the fabrication and assembly digital twin."""

from __future__ import annotations

import json

from osr_mech.fabrication_assembly_twin import (
    ANIMATION_DURATION_S,
    VISUAL_TOUR_DURATION_S,
    VISUAL_TOUR_PHASES,
    assembly_state,
    fabrication_assembly_manifest,
    fabrication_streams,
    trainset_assembly_graph,
    twin_checks,
    write_manifest,
)


def test_twin_covers_all_four_product_streams_and_controlled_routes() -> None:
    streams = fabrication_streams()
    assert [stream.id for stream in streams] == ["track", "station", "viaduct", "train"]
    assert [len(stream.stages) for stream in streams] == [5, 5, 8, 7]
    assert sum(len(stream.stages) for stream in streams) == 25
    viaduct = next(stream for stream in streams if stream.id == "viaduct")
    assert "Pi25" in viaduct.exemplar
    assert any(stage.id == "VIA-05" for stage in viaduct.stages)
    assert any(stage.id == "VIA-55" for stage in viaduct.stages)


def test_every_stage_has_dependency_quality_evidence_and_sources() -> None:
    streams = fabrication_streams()
    for stream in streams:
        assert stream.stages[0].predecessor is None
        for previous, stage in zip(stream.stages, stream.stages[1:]):
            assert stage.predecessor == previous.id
        assert all(stage.qa_hold and stage.evidence and stage.source_refs for stage in stream.stages)
    assert all(check["passed"] for check in twin_checks(streams))


def test_animation_state_advances_concurrent_work_without_losing_streams() -> None:
    start = assembly_state(0)
    middle = assembly_state(ANIMATION_DURATION_S / 2)
    finish = assembly_state(ANIMATION_DURATION_S)
    assert len(start) == len(middle) == len(finish) == 4
    assert all(state.progress_percent == 0.0 for state in start)
    assert all(state.status == "active" for state in middle)
    assert all(state.progress_percent == 100.0 for state in finish)
    assert all(state.qa_status == "released" for state in finish)


def test_manifest_embeds_source_hashes_snapshots_interfaces_and_limitations() -> None:
    manifest = fabrication_assembly_manifest()
    assert manifest["passed"] is True
    assert manifest["schema"].endswith("fabrication-assembly-twin.v1")
    assert len(manifest["source_register"]) >= 10
    assert len(manifest["integration_dependencies"]) == 3
    assert set(manifest["state_snapshots"]) == {"0", "12", "24", "36", "48"}
    assert manifest["visual_tour"]["duration_s"] == VISUAL_TOUR_DURATION_S == 88.0
    assert [phase["stream_id"] for phase in VISUAL_TOUR_PHASES] == [
        "track",
        "station",
        "viaduct",
        "train",
    ]
    assert all(
        current["end_s"] < following["start_s"]
        for current, following in zip(VISUAL_TOUR_PHASES, VISUAL_TOUR_PHASES[1:])
    )
    assert manifest["limitations"]


def test_complete_trainset_product_dag_is_dependency_animated() -> None:
    graph = trainset_assembly_graph()
    assert graph["animated_product_count"] == 101
    assert graph["animated_assembly_count"] == 26
    assert graph["animated_node_count"] == 127
    assert graph["root_id"] == "LM3-TRAINSET-A000"
    assert graph["dependency_timing_valid"] is True
    assert set(graph["timing"]) == {
        *(item["id"] for item in graph["product_rows"]),
        *(item["id"] for item in graph["assemblies"]),
    }
    for assembly in graph["assemblies"]:
        assert graph["timing"][assembly["id"]]["start_s"] >= max(
            graph["timing"][child]["end_s"] for child in assembly["children"]
        )


def test_manifest_writer_round_trips_machine_readable_register(tmp_path) -> None:
    target = write_manifest(tmp_path / "fabrication-twin.json")
    written = json.loads(target.read_text())
    assert written["passed"] is True
    assert len(written["streams"]) == 4
