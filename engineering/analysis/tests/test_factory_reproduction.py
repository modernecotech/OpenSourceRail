"""Portable recomputation never weakens retained byte or identity integrity."""

from copy import deepcopy
import json
import shutil

import pytest

from engineering.factory_examples import build, reproduction as r


@pytest.fixture(scope="module")
def outputs():
    return build.make_outputs()


def test_platform_roundoff_and_environment_are_separate_from_physics(outputs):
    fresh = deepcopy(outputs[0])
    report = json.loads(fresh["development.json"])
    report["bed"]["cases"][0]["critical_force_per_side_n"] *= 1 + 8.3e-13
    report["numerical_toolchain"] = {
        k: "independent-platform" for k in report["numerical_toolchain"]
    }
    fresh["development.json"] = build.json_text(report)
    errors, _ = r.compare_outputs(build.DEFAULT, fresh)
    assert errors == []


@pytest.mark.parametrize("bad", [None, True, float("inf"), float("nan"), 1001.0])
def test_missing_nonfinite_state_and_material_numerical_changes_reject(bad):
    assert r.differences({"force_n": 1000.0}, {"force_n": bad})


def test_integer_states_unknowns_and_geometry_are_exact():
    for a, b in ((4, 4.0), (False, 0), (None, 0), ("failed", "passed")):
        assert r.differences(a, b)
    assert not r.differences(1e6, 1e6 + 1e-6, path=("critical_force_n",))
    assert r.differences(0.0, 1e-6, path=("deflection_m",))
    assert r.differences(0.001, 0.001 + 1e-14, numeric=False)


def test_new_geometry_is_not_excused_as_solver_roundoff(outputs):
    fresh = dict(outputs[0])
    model = json.loads(fresh["fixture/model.json"])
    model["parts"][0]["size_m"][0] += 1e-13
    fresh["fixture/model.json"] = build.json_text(model)
    errors, _ = r.compare_outputs(build.DEFAULT, fresh)
    assert any("fixture/model.json" in error for error in errors)


def test_retained_roundoff_edit_still_fails_exact_integrity(tmp_path, outputs):
    shutil.copytree(
        build.DEFAULT,
        tmp_path / "evidence",
        ignore=shutil.ignore_patterns("*.step", "*.FCBak"),
    )
    folder = tmp_path / "evidence"
    file = folder / "development.json"
    data = json.loads(file.read_text())
    data["bed"]["cases"][0]["critical_force_per_side_n"] += 1e-7
    file.write_text(build.json_text(data))
    with pytest.raises(ValueError, match="integrity mismatch"):
        r.verify(folder, *outputs, build.source_hashes())
    with pytest.raises(ValueError, match="cannot reseal changed original"):
        r.seal(folder, *outputs, build.source_hashes())


def test_source_mutation_requires_explicit_reverification(outputs):
    changed = {
        **build.source_hashes(),
        "engineering/factory_examples/models.py": "0" * 64,
    }
    with pytest.raises(ValueError, match="source/input mismatch"):
        r.verify(build.DEFAULT, *outputs, changed)


def test_duplicate_and_nonfinite_json_are_rejected():
    for text in ('{"x":1,"x":2}', '{"x":NaN}'):
        with pytest.raises(ValueError):
            r.load(text)


def test_normal_build_cannot_overwrite_sealed_originals(monkeypatch):
    monkeypatch.setattr("sys.argv", ["factory-build", "--native"])
    monkeypatch.setattr(
        build,
        "make_outputs",
        lambda: pytest.fail("sealed originals reached generation"),
    )
    with pytest.raises(SystemExit, match="2"):
        build.main()
