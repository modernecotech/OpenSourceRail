"""Candidate-bound planning handoff and tamper-refusal contracts."""
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import gzip
import pytest

from engineering.development_baseline import FLAGS
from engineering.development_baseline import entrypoint, factory_draft, planning
from engineering.station_rail.common import identity


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


def _cost_line(candidate_id, line_key, stage, quantity, costs, components=None):
    row = dict(candidate_id=candidate_id, line_key=line_key, stage=stage, quantity=quantity,
        unit="test-unit", currency="IQD", cost_iqd=dict(zip(factory_draft.CASES, costs)),
        estimate_class="C", rate_evidence_class="C", process_template="test process",
        source_ids=["fixture-source"], occurrence_ids=[], calculation_basis="synthetic test ledger",
        components_iqd=components)
    row["line_id"] = identity(row)
    return row


def _factory_cost_fixture(root, baseline, evaluation_id):
    from hashlib import sha256 as _sha256

    source = root / "engineering/fixture/factory-cost-source.json"
    source.parent.mkdir(parents=True, exist_ok=True)
    source.write_text('{"basis":"fixture"}\n')
    candidate_id = baseline["vehicle"]["candidate_id"]
    source_sha = {source.relative_to(root).as_posix(): _sha256(source.read_bytes()).hexdigest()}
    located = _cost_line(candidate_id, "located-stock/body/aluminium", "factory-gate",
        dict(process_hours_per_car=[1.0, 2.0, 4.0], net_mass_kg_per_car=10.0), [600.0, 1200.0, 2400.0],
        dict(material=dict(low=500.0, base=1000.0, high=2000.0),
             labour=dict(low=100.0, base=200.0, high=400.0)))
    residual = _cost_line(candidate_id, "unlocated-account/services", "factory-gate-equipment-allowance",
        dict(process_hours_per_train=[2.0, 4.0, 8.0], residual_account_mass_kg_per_car=1.0),
        [60.0, 120.0, 240.0])
    assembly = _cost_line(candidate_id, "six-car-final-vehicle-assembly", "final-assembly",
        dict(labour_hours_per_car=[8.0, 16.0, 24.0]), [400.0, 800.0, 1600.0],
        dict(labour=dict(low=300.0, base=600.0, high=1200.0),
             equipment=dict(low=100.0, base=200.0, high=400.0)))
    delivery = _cost_line(candidate_id, "reference-factory-to-assembly-delivery", "reference-delivery",
        dict(reference_distance_km=50), [10.0, 20.0, 30.0])
    cost = dict(schema="osr-v06-selected-vehicle-class-c-cost/1",
        selection_id=baseline["selection_id"], **baseline["vehicle"], evaluation_id=evaluation_id,
        development_default=True, estimate_class="C", currency="IQD", estimate_date="2026-10-31",
        assumptions_id="f" * 64, assumption_values=dict(productive_utilisation=0.75),
        shifts=dict(production_per_day=dict(shifts=2, hours_per_shift=8, productive_hours_per_day=12.0),
            civil_per_day=dict(shifts=2, hours_per_shift=8),
            operations_cases=[dict(hours_per_day=hours, shifts_per_day=shifts, hours_per_shift=hours_per_shift)
                for hours, shifts, hours_per_shift in ((16, 2, 8), (18, 2, 9), (24, 3, 8))]),
        vehicle_account=dict(cars_per_train=6, accounted_tare_kg_per_car=20.0,
            located_geometry_kg_per_car=10.0, residual_account_kg_per_car=10.0,
            complete_installed_mass=False),
        lines=[located, residual, assembly, delivery],
        factory_gate_cost_iqd_per_train=dict(low=660.0, base=1320.0, high=2640.0),
        final_vehicle_assembly_cost_iqd_per_train=dict(low=400.0, base=800.0, high=1600.0),
        separate_unamortized_factory_tooling_capital_iqd=dict(low=100.0, base=200.0, high=300.0),
        source_sha256=source_sha, **FLAGS)
    cost["cost_estimate_id"] = identity(cost)
    cost_path = root / "docs/design-engine/current/exports/selected-vehicle-cost.json"
    _write_json(cost_path, cost)
    export_source = root / "engineering/fixture/factory-export-source.json"
    export_source.write_text('{"basis":"fixture export"}\n')
    export_manifest = dict(schema="osr-v06-delivery-manifest/1",
        selection_id=baseline["selection_id"], **baseline["vehicle"], evaluation_id=evaluation_id,
        development_default=True,
        source_sha256={export_source.relative_to(root).as_posix(): _sha256(export_source.read_bytes()).hexdigest()},
        files_sha256={cost_path.name: _sha256(cost_path.read_bytes()).hexdigest()}, **FLAGS)
    export_manifest["manifest_id"] = identity(export_manifest)
    export_path = root / "docs/design-engine/current/exports/manifest.json"
    _write_json(export_path, export_manifest)
    return cost, export_manifest, export_path



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
        "engineering/development_baseline/factory_draft.py",
        "engineering/development_baseline/vehicle_cost.py",
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
    current_manifest = dict(schema="osr-current-publication-fixture/1", selection_id=selection_id,
        files_sha256={})
    _, _, selected_export_path = _factory_cost_fixture(root, baseline, evaluation_id)
    current_manifest["files_sha256"]["exports/manifest.json"] = sha256(selected_export_path.read_bytes()).hexdigest()
    current_manifest["manifest_id"] = identity(current_manifest)
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

    draft_output = "build/factory-plan"
    assert entrypoint.main(["twin", "factory-draft", "compile", output, "--output", draft_output], root=root) == 0
    draft_result = json.loads(capsys.readouterr().out)
    assert draft_result["candidate_evaluation_id"] == evaluation_id
    assert draft_result["planning_revision_id"] == handoff["planning_revision"]["planning_revision_id"]
    assert entrypoint.main(["twin", "factory-draft", "verify", output, draft_output], root=root) == 0
    draft_verified = json.loads(capsys.readouterr().out)
    assert draft_verified["verified"] is True
    assert draft_verified["submittable"] is False
    assert draft_verified["erpnext_admitted"] is False
    draft = json.loads((root / draft_output / factory_draft.PAYLOAD_NAME).read_bytes())
    factory = draft["factory_plan"]
    assert factory["production_shifts"] == dict(shifts_per_day=2, hours_per_shift=8,
        productive_utilisation=0.75, productive_hours_per_day=12.0,
        source="Selected vehicle Class C cost assumptions")
    assert factory["deferred_shift_assumptions"]["civil"] == {
        "shifts": 2, "hours_per_shift": 8, "state": "held", "schedule_costed": False}
    assert [row["shifts_per_day"] for row in factory["deferred_shift_assumptions"]["railway_operations_cases"]] == [2, 2, 3]
    assert [row["process_hours_per_train"] for row in factory["work_packages"]] == [
        dict(low=6.0, base=12.0, high=24.0),
        dict(low=2.0, base=4.0, high=8.0),
        dict(low=48.0, base=96.0, high=144.0),
    ]
    assert factory["serialized_factory_duration_productive_workdays"] == dict(low=4.666667, base=9.333333, high=14.666667)
    assert factory["factory_and_final_assembly_cost_iqd_per_train"] == dict(low=1060.0, base=2120.0, high=4240.0)
    assert all(value["state"] == "held" for value in draft["held_scopes"].values())
    assert {"procurement", "civil_and_site_schedule", "supplier_orders", "staffing", "railway_operations"} <= set(draft["held_scopes"])
    assert all(draft[key] is False for key in FLAGS)
    with pytest.raises(factory_draft.FactoryDraftError, match="already exists"):
        factory_draft.compile_bundle(root=root, handoff_directory=output, output_path=draft_output)

    from engineering.development_baseline import factory_draft as draft_module
    payload_path = root / draft_output / draft_module.PAYLOAD_NAME
    original_payload = payload_path.read_bytes()
    tampered = json.loads(original_payload)
    tampered["factory_plan"]["production_shifts"]["shifts_per_day"] = 3
    payload_path.write_bytes(draft_module.encoded(tampered))
    with pytest.raises(factory_draft.FactoryDraftError, match="payload hash differs"):
        factory_draft.verify_bundle(root=root, handoff_directory=output, output_path=draft_output)
    payload_path.write_bytes(original_payload)

    cost_path = root / "docs/design-engine/current/exports/selected-vehicle-cost.json"
    cost = json.loads(cost_path.read_bytes())
    wrong_candidate = deepcopy(cost)
    wrong_candidate["candidate_id"] = "9" * 64
    wrong_candidate["cost_estimate_id"] = identity({key: value for key, value in wrong_candidate.items()
                                                        if key != "cost_estimate_id"})
    with pytest.raises(factory_draft.FactoryDraftError, match="different candidate_id"):
        factory_draft._build_work_packages(wrong_candidate, {**vehicle, "selection_id": selection_id,
            "evaluation_id": evaluation_id}, handoff["planning_revision"])

    geography.write_text('{"source":"changed"}\n')
    assert entrypoint.main(["plan", "verify", output], root=root) == 3
    held = json.loads(capsys.readouterr().out)
    assert held["execution"] == "held"
    assert "source changed" in held["reason"]
    with pytest.raises(factory_draft.FactoryDraftError, match="Planning revision is not current and verified"):
        factory_draft.verify_bundle(root=root, handoff_directory=output, output_path=draft_output)
    geography.write_text('{"source":"fixture"}\n')
    context_path.write_bytes(gzip.compress(b'{"layers":{"roads":[]}}', mtime=0))
    assert entrypoint.main(["plan", "verify", output], root=root) == 3
    held = json.loads(capsys.readouterr().out)
    assert held["execution"] == "held"
    assert context_path.relative_to(root).as_posix() in held["reason"]
