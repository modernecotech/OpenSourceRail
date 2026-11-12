from pathlib import Path
from copy import deepcopy
import json
import pytest
from engineering.station_rail.common import identity

from engineering.design_search import line_benchmark_retained


ROOT = Path(__file__).resolve().parents[3]


def test_line30_benchmark_is_integrity_verified_under_its_historical_source_epoch():
    report = line_benchmark_retained.verify(ROOT)

    assert report["verified"] is True
    assert report["current_source_valid"] is False
    result=json.loads((ROOT/line_benchmark_retained.PACKAGE/"result.json").read_bytes())
    assert report["requirements_id"]==result["requirements_id"]
    assert report["requirements_id"]==identity(result["functional_requirements"])
    assert report["source_epoch"] == "historical"
    assert report["historical_source_paths"] == ["engineering/station_rail/braking.py"]
    assert report["analytical_replay"] is False
    assert report["numerical_reexecuted"] is False
    assert report["native_solver_jobs"] == 0
    assert report["physical_accepted"] is False
    assert report["engineering_accepted"] is False
    assert report["current_evaluator_admission"] is False


def test_retained_requirement_identity_cannot_be_relabelled(monkeypatch):
    original=line_benchmark_retained.line_benchmark.validate_result
    def reject_changed_requirement(value,root,**kwargs):
        bad=deepcopy(value);bad['requirements_id']='0'*64
        bad['evaluation_id']=identity({k:v for k,v in bad.items() if k!='evaluation_id'})
        original(bad,root,**kwargs)
    monkeypatch.setattr(line_benchmark_retained.line_benchmark,'validate_result',reject_changed_requirement)
    with pytest.raises(ValueError,match='requirements identity differs'):line_benchmark_retained.verify(ROOT)


def test_explicit_retained_cli_does_not_claim_current_replay(capsys):
    line_benchmark_retained.main([])
    report=json.loads(capsys.readouterr().out)
    assert report['source_epoch']=='historical' and report['current_source_valid'] is False
    assert report['analytical_replay'] is False and report['native_solver_jobs']==0
