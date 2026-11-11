from pathlib import Path

from engineering.design_search import compact_launch_retained


ROOT = Path(__file__).resolve().parents[3]


def test_compact_launch_is_verified_as_historical_without_replay():
    report = compact_launch_retained.verify(ROOT)

    assert report["verified"] is True
    assert report["source_epoch"] == "historical"
    assert report["historical_source_paths"] == ["engineering/station_rail/braking.py"]
    assert report["analytical_replay"] is False
    assert report["numerical_reexecuted"] is False
    assert report["native_solver_jobs"] == 0
    assert report["physical_accepted"] is False
    assert report["engineering_accepted"] is False
    assert report["current_evaluator_admission"] is False
