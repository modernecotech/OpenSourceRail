"""Check source-bound replay, coupled loads and the exported decision boundary."""
from hashlib import sha256
from io import BytesIO
import json
from zipfile import ZipFile

import pytest

from cities.Baghdad.engineering.simulation import scenario as sim


def test_reuse_depends_on_the_stage_inputs_and_source_digests(tmp_path):
    calls = []
    def calculate(args):
        calls.append(args["load"])
        return {"load": args["load"]}
    runs = {}
    for version, load in (("old", 1), ("old", 1), ("new", 1), ("new", 2)):
        sim.stage("case", {"load": load}, {"file": version}, calculate, tmp_path, runs)
    assert calls == [1, 1, 2]
    key = runs["case"]["key"]
    path = tmp_path / "case" / (key + ".json")
    record = json.loads(path.read_bytes())
    record["value"]["load"] = 999
    path.write_text(json.dumps(record))
    with pytest.raises(ValueError, match="Damaged"):
        sim.stage("case", {"load": 2}, {"file": "new"}, calculate, tmp_path, runs)


def test_joined_result_and_issue_follow_the_selected_vehicle_and_duty():
    result = sim.run_case()
    stages = result["stages"]
    motion, vehicle, production = (stages[k] for k in ("motion", "vehicle", "production"))
    assert result["identity"]["parent_candidate_id"] == production["candidate_id"] == motion["source_publication_candidate_id"]
    assert vehicle["loaded_train_kg"] == motion["scenario"]["loaded_train_kg"]
    assert stages["passengers"]["auxiliary_kw"] == motion["scenario"]["auxiliary_kw"]
    assert motion["energy_kwh_per_train_km"] == production["inputs"]["energy_kwh_per_train_km"]
    assert motion["metrics"]["fleet_sets_required"] * result["inputs"]["cars"] == production["quantities"]["cars"]
    assert sim.compact(result) == json.loads((sim.HERE / "baseline.json").read_bytes())
    with ZipFile(BytesIO(sim.dossier(result))) as issue:
        manifest = json.loads(issue.read("manifest.json"))
        assert manifest["identity"] == result["identity"]
        assert manifest["fabrication_released"] is False and result["decision"]["eligible"] is False
        assert all(sha256(issue.read(k)).hexdigest() == v for k, v in manifest["sha256"].items())
        assert json.loads(issue.read("comparison-evidence/external-default.json"))["coupled_evaluation_id"] == motion["evaluation_id"]


def test_reject_out_of_domain_and_unknown_inputs():
    for invalid in ({"grade_pct": True}, {"cars": 4}, {"headway_min": 2.5}, {"schedule": "unexpected"}):
        with pytest.raises(ValueError):
            sim.selections(invalid)
