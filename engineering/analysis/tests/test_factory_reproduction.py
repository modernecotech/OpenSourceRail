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
    nested = json.loads(fresh["report.json"])
    nested["development"]["numerical_toolchain"] = report["numerical_toolchain"]
    fresh["report.json"] = build.json_text(nested)
    errors, _ = r.compare_outputs(build.DEFAULT, fresh)
    assert errors == []


@pytest.fixture
def minimal_retained_evidence(tmp_path):
    producer = {
        "python": "original-python",
        "numpy": "original-numpy",
        "scipy": "original-scipy",
        "matplotlib": "original-matplotlib",
    }
    development = {
        "numerical_toolchain": producer,
        "force_n": 1000.0,
        "state": "unknown",
    }
    outputs = {
        "development.json": build.json_text(development),
        "report.json": build.json_text(
            {
                "source_sha256": {"producer.py": "original-source"},
                "development": development,
            }
        ),
    }
    for name, text in outputs.items():
        (tmp_path / name).write_text(text)
    sources = {"verifier.py": "current-verifier"}
    record = r.seal(tmp_path, outputs, {}, sources)
    (tmp_path / "reproduction.json").write_text(build.json_text(record))
    return tmp_path, outputs, sources


def test_both_recomputed_toolchain_copies_can_change_without_identity_loss(
    minimal_retained_evidence,
):
    folder, outputs, sources = minimal_retained_evidence
    fresh = dict(outputs)
    development = json.loads(fresh["development.json"])
    original = deepcopy(development["numerical_toolchain"])
    development["numerical_toolchain"] = {k: "independent-runtime" for k in original}
    report = json.loads(fresh["report.json"])
    report["development"]["numerical_toolchain"] = development["numerical_toolchain"]
    fresh["development.json"] = build.json_text(development)
    fresh["report.json"] = build.json_text(report)
    result = r.verify(folder, fresh, {}, sources)
    assert result["passed"] and result["exact_retained_integrity"]
    assert result["verifier_toolchain"] == development["numerical_toolchain"]
    assert result["original_producer_toolchain"] == original
    assert not result["original_artifacts_rewritten"]


def test_nested_metadata_exclusion_never_ignores_recomputed_physics_or_state(
    minimal_retained_evidence,
):
    folder, outputs, sources = minimal_retained_evidence
    for field, value in [("force_n", 1001.0), ("state", "passed")]:
        fresh = dict(outputs)
        report = json.loads(fresh["report.json"])
        report["development"][field] = value
        fresh["report.json"] = build.json_text(report)
        with pytest.raises(ValueError, match="numerical reproduction mismatch"):
            r.verify(folder, fresh, {}, sources)


def test_retained_nested_metadata_still_requires_exact_bytes(minimal_retained_evidence):
    folder, outputs, sources = minimal_retained_evidence
    path = folder / "report.json"
    report = json.loads(path.read_text())
    report["development"]["numerical_toolchain"]["python"] = "tampered-producer"
    path.write_text(build.json_text(report))
    with pytest.raises(ValueError, match="artifact integrity mismatch"):
        r.verify(folder, outputs, {}, sources)
    with pytest.raises(ValueError, match="cannot reseal changed original"):
        r.seal(folder, outputs, {}, sources)


@pytest.mark.parametrize(
    "target", ["nested", "standalone", "both", "producer-source", "seal-producer"]
)
def test_producer_identity_tamper_rejects_even_with_updated_file_hash(
    minimal_retained_evidence, target
):
    folder, outputs, sources = minimal_retained_evidence
    record = json.loads((folder / "reproduction.json").read_text())
    for name in ["report.json", "development.json"]:
        data = json.loads((folder / name).read_text())
        if name == "report.json" and target in {"nested", "both"}:
            data["development"]["numerical_toolchain"]["python"] = "tampered-producer"
        if name == "development.json" and target in {"standalone", "both"}:
            data["numerical_toolchain"]["python"] = "tampered-producer"
        if name == "report.json" and target == "producer-source":
            data["source_sha256"]["producer.py"] = "tampered-source"
        (folder / name).write_text(build.json_text(data))
        record["retained_files_sha256"][name] = r.digest(folder / name)
    if target == "seal-producer":
        record["original_producer_toolchain"]["python"] = "tampered-seal-producer"
    (folder / "reproduction.json").write_text(build.json_text(record))
    with pytest.raises(ValueError, match="original factory producer identity differs"):
        r.verify(folder, outputs, {}, sources)
    with pytest.raises(ValueError, match="original factory producer identity differs"):
        r.seal(folder, outputs, {}, sources)


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
