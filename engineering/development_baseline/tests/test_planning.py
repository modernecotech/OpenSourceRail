"""Candidate-bound planning handoff and tamper-refusal contracts."""
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path

from engineering.development_baseline import FLAGS
from engineering.development_baseline import entrypoint, planning


def _write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(planning.encoded(value))


def test_plan_cli_compiles_and_verifies_current_candidate_handoff(tmp_path, monkeypatch, capsys):
    repository = Path(__file__).resolve().parents[3]
    root = tmp_path / "repo"
    for relative in (
        "engineering/development_baseline/planning.py",
        "engineering/development_baseline/entrypoint.py",
        "engineering/development-baseline.toml",
        "docs/workbench/planning/index.html",
        "docs/workbench/planning/planning.js",
    ):
        target = root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes((repository / relative).read_bytes())

    selection_id = "a" * 64
    evaluation_id = "e" * 64
    vehicle = dict(candidate_id="1" * 64, body_candidate_id="2" * 64,
        support_component_id="3" * 64, propulsion_component_id="4" * 64)
    baseline = dict(selection_id=selection_id, vehicle=vehicle,
        selection=dict(network_proposal_id="5" * 64))
    summary = dict(selection_id=selection_id, evaluation_id=evaluation_id)
    current_manifest = dict(schema="osr-current-publication-fixture/1", selection_id=selection_id)
    _write_json(root / "docs/design-engine/current/manifest.json", current_manifest)

    geography = root / "docs/planning/geography.json"
    geography.parent.mkdir(parents=True)
    geography.write_text('{"source":"fixture"}\n')
    source_sha256 = {"docs/planning/geography.json": sha256(geography.read_bytes()).hexdigest()}
    coordinates = [[0.0, 0.0], [0.01, 0.0]]
    length_m = planning._distance(*coordinates)
    base = dict(schema="osr-owner-builder-plan/1", environment="planning", city="fixture-city",
        revision=4, source_sha256=source_sha256,
        lines=[dict(id="line-1", coordinates=coordinates, length_m=length_m, headway_s=240.0,
            stops=[dict(id="stop-a", chainage_m=0.0, lon=0.0, lat=0.0, dwell_s=45.0),
                   dict(id="stop-b", chainage_m=length_m, lon=0.01, lat=0.0, dwell_s=45.0)])],
        od=[], **{key: False for key in planning.RETAINED_PLAN_DISPOSITIONS})
    base["revision_sha256"] = planning.digest_json(base)
    monkeypatch.setattr(planning, "_load_base", lambda _root, city: (deepcopy(base), source_sha256))
    monkeypatch.setattr(entrypoint, "selected", lambda _root: baseline)
    monkeypatch.setattr(entrypoint, "read_packet", lambda _root: (summary, current_manifest))

    _write_json(root / "build/edits.json", dict(schema=planning.EDIT_SCHEMA, city="fixture-city",
        base_revision_sha256=base["revision_sha256"], actor="reviewer",
        edits=[dict(kind="set-service", line="line-1", headway_s=300.0, dwell_s=60.0)]))
    output = "build/planning-handoff"
    assert entrypoint.main(["plan", "compile", "build/edits.json", "--output", output], root=root) == 0
    compiled = json.loads(capsys.readouterr().out)
    assert compiled["selection_id"] == selection_id

    assert entrypoint.main(["plan", "verify", output], root=root) == 0
    verified = json.loads(capsys.readouterr().out)
    assert verified["verified"] is True
    assert verified["physical_candidate"] == vehicle
    assert verified["route_performance_evaluated"] is False
    assert verified["complete_cost_known"] is False
    assert all(verified[key] is False for key in FLAGS)

    geography.write_text('{"source":"changed"}\n')
    assert entrypoint.main(["plan", "verify", output], root=root) == 3
    held = json.loads(capsys.readouterr().out)
    assert held["execution"] == "held"
    assert "source changed" in held["reason"]
