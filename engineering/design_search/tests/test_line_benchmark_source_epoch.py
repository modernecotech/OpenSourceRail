from pathlib import Path

from engineering.design_search import line_benchmark_retained


ROOT = Path(__file__).resolve().parents[3]


def test_line30_benchmark_is_integrity_verified_under_its_historical_source_epoch():
    report = line_benchmark_retained.verify(ROOT)

    assert report["verified"] is True
    assert report["source_epoch"] == "historical"
    assert report["historical_source_paths"] == ["engineering/station_rail/braking.py"]
    assert report["analytical_replay"] is False
    assert report["numerical_reexecuted"] is False
    assert report["native_solver_jobs"] == 0
    assert report["physical_accepted"] is False
    assert report["engineering_accepted"] is False
    assert report["current_evaluator_admission"] is False
