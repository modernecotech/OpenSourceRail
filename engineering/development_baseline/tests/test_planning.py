"""Candidate-bound planning handoff and tamper-refusal contracts."""
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import gzip
import pytest

from engineering.development_baseline import FLAGS
from engineering.development_baseline import entrypoint, planning


def test_current_planning_gzip_packets_use_platform_neutral_header():
    raw = planning.encoded(dict(city="fixture", values=[1, 2, 3]))
    member = planning._gzip_member(raw)

    assert member[:3] == b"\x1f\x8b\x08"
    assert member[4:8] == b"\x00\x00\x00\x00"
    assert member[9] == 255
    assert gzip.decompress(member) == raw


def _write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(planning.encoded(value))



def test_current_planning_base_binds_geographic_context_to_selected_candidate(tmp_path):
    root = tmp_path
    city_dir = root / "cities/catalogue/test/fixture-city"
    city_dir.mkdir(parents=True)
    (city_dir / "city.json").write_text(json.dumps({
        "lines": [{"name": "line-1"}],
        "stations": [
            {"id": "stop-a", "line": "line-1", "s_m": 0.0, "lon": 0.0, "lat": 0.0},
            {"id": "stop-b", "line": "line-1", "s_m": 1111.95, "lon": 0.01, "lat": 0.0},
        ],
        "interchanges": [],
    }))
    (city_dir / "fixture-city.corridor.geojson").write_text(json.dumps({
        "type": "FeatureCollection", "features": [{
            "type": "Feature", "properties": {"kind": "line", "name": "line-1"},
            "geometry": {"type": "LineString", "coordinates": [[0.0, 0.0], [0.01, 0.0]]},
        }],
    }))
    context_path = city_dir / "map-context.json.gz"
    context_path.write_bytes(gzip.compress(json.dumps({"layers": {"roads": []}}).encode(), mtime=0))
    for relative in (planning.CURRENT_CITY_INDEX, planning.CURRENT_CITY_RECEIPT,
                     planning.SELECTION_SOURCE, planning.BRIEF_SOURCE,
                     Path("engineering/development_baseline/planning.py")):
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("{}\n")
    baseline = {"selection_id": "a" * 64,
        "selection": {"service": {"headway_s": 120.0, "dwell_s": 35.0}}}
    row = {"slug": "fixture-city", "geography_path": "cities/catalogue/test/fixture-city/city.json",
        "route_geography_path": "cities/catalogue/test/fixture-city/fixture-city.corridor.geojson"}
    plan = planning._current_city_plan(root, row, baseline)
    relative = context_path.relative_to(root).as_posix()
    assert plan["map_context"]["path"] == relative
    assert plan["map_context"]["sha256"] == sha256(context_path.read_bytes()).hexdigest()
    assert plan["source_sha256"][relative] == plan["map_context"]["sha256"]
    assert all(plan[key] is False for key in planning.PLAN_DISPOSITIONS)

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
    context_path = root / 'cities/catalogue/test/fixture-city/map-context.json.gz'
    context_path.parent.mkdir(parents=True)
    context_path.write_bytes(gzip.compress(b'{"layers":{}}', mtime=0))
    source_sha256 = {
        "docs/planning/geography.json": sha256(geography.read_bytes()).hexdigest(),
        context_path.relative_to(root).as_posix(): sha256(context_path.read_bytes()).hexdigest(),
    }
    coordinates = [[0.0, 0.0], [0.01, 0.0]]
    length_m = planning._distance(*coordinates)
    base = dict(schema="osr-owner-builder-plan/1", environment="planning", city="fixture-city",
        revision=4, source_sha256=source_sha256,
        map_context=dict(path=context_path.relative_to(root).as_posix(),
            sha256=source_sha256[context_path.relative_to(root).as_posix()],
            role='Geographic context only; not survey, route-clearance, demand, engineering or operating evidence'),
        lines=[dict(id="line-1", coordinates=coordinates, length_m=length_m, headway_s=240.0,
            stops=[dict(id="stop-a", chainage_m=0.0, lon=0.0, lat=0.0, dwell_s=45.0),
                   dict(id="stop-mid", chainage_m=length_m / 2, lon=0.005, lat=0.0, dwell_s=45.0),
                   dict(id="stop-b", chainage_m=length_m, lon=0.01, lat=0.0, dwell_s=45.0)])],
        od=[dict(origin="stop-a", destination="stop-mid", trips_per_day=120, basis="synthetic")],
        **{key: False for key in planning.PLAN_DISPOSITIONS})
    base["revision_sha256"] = planning.digest_json(base)
    monkeypatch.setattr(planning, "_load_base", lambda _root, city: (deepcopy(base), source_sha256))
    monkeypatch.setattr(entrypoint, "selected", lambda _root: baseline)
    monkeypatch.setattr(entrypoint, "read_packet", lambda _root: (summary, current_manifest))

    with pytest.raises(planning.PlanningError, match="OD rows"):
        planning._apply_edits(base, [dict(kind="retire-stop", line="line-1", stop="stop-mid")], "reviewer")
    repeated_identity = [dict(kind="add-stop", line="line-1", stop="proposal-stop-001",
            chainage_m=length_m / 4, dwell_s=50.0), dict(kind="set-od", rows=[]),
        dict(kind="retire-stop", line="line-1", stop="stop-mid"),
        dict(kind="add-stop", line="line-1", stop="proposal-stop-001",
            chainage_m=length_m * .75, dwell_s=50.0)]
    with pytest.raises(planning.PlanningError, match="identity already exists"):
        planning._apply_edits(base, repeated_identity, "reviewer")
    _write_json(root / "build/edits.json", dict(schema=planning.EDIT_SCHEMA, city="fixture-city",
        base_revision_sha256=base["revision_sha256"], actor="reviewer",
        edits=[dict(kind="add-stop", line="line-1", stop="proposal-stop-001",
                    chainage_m=length_m / 4, dwell_s=50.0),
               dict(kind="set-od", rows=[dict(origin="stop-a", destination="proposal-stop-001",
                    trips_per_day=90, basis="synthetic")]),
               dict(kind="retire-stop", line="line-1", stop="stop-mid")]))
    output = "build/planning-handoff"
    assert entrypoint.main(["plan", "compile", "build/edits.json", "--output", output], root=root) == 0
    compiled = json.loads(capsys.readouterr().out)
    assert compiled["selection_id"] == selection_id
    handoff = json.loads((root / output / "planning-handoff.json").read_bytes())
    revised_line = handoff["planning_revision"]["network"]["lines"][0]
    assert [stop["id"] for stop in revised_line["stations"]] == ["stop-a", "proposal-stop-001", "stop-b"]
    assert handoff["planning_revision"]["network"]["origin_destination"][0]["destination"] == "proposal-stop-001"
    assert "map_context" not in handoff["planning_revision"]["network"]
    assert sha256(context_path.read_bytes()).hexdigest() == handoff["planning_revision"]["source_sha256"][context_path.relative_to(root).as_posix()]

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
    geography.write_text('{"source":"fixture"}\n')
    context_path.write_bytes(gzip.compress(b'{"layers":{"roads":[]}}', mtime=0))
    assert entrypoint.main(["plan", "verify", output], root=root) == 3
    held = json.loads(capsys.readouterr().out)
    assert held["execution"] == "held"
    assert context_path.relative_to(root).as_posix() in held["reason"]
