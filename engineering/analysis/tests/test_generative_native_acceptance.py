"""Mandatory native evidence protocol fixtures, never substitute physics tests."""

from copy import deepcopy
import json
from pathlib import Path
import shutil

import pytest
from engineering.generative_design import native_acceptance as n
from engineering.factory_examples.models import part, volume, global_size


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


@pytest.fixture
def evidence(tmp_path, monkeypatch):
    folder = tmp_path / "evidence"
    folder.mkdir()
    targets = [
        dict(id="required-LM3-heavy", architecture_id="LM3", total_mass_kg=200000),
        dict(
            id="required-sixcar-heavy-cg-positive",
            architecture_id="metro-6car-planning",
            total_mass_kg=460800,
        ),
    ]
    sources = {"explicit-protocol-source": "a" * 64}
    tools = dict(available=True, missing=[])
    definitions = {
        c["id"]: dict(
            id="beam-" + c["architecture_id"],
            parts=[part("single-protocol-box", [1, 2, 3], [0, 0, 0])],
            physical_release=False,
        )
        for c in targets
    }
    monkeypatch.setattr(n, "current_targets", lambda: deepcopy(targets))
    monkeypatch.setattr(
        n,
        "current_selection",
        lambda c: ("selected-" + c["id"], deepcopy(definitions[c["id"]])),
    )
    monkeypatch.setattr(n.architecture, "sources", lambda: dict(sources))
    monkeypatch.setattr(
        n.architecture,
        "verify",
        lambda folder, current=True: dict(
            integrity_verified=True, current_sources_checked=current
        ),
    )
    monkeypatch.setattr(n.factory, "toolchain", lambda: dict(tools))
    write(
        folder / "request.json",
        dict(
            schema="osr-architecture-native-request/1",
            native=True,
            required_case_ids=[c["id"] for c in targets],
            source_sha256=sources,
            engineering_design_complete=False,
            manufacturing_release=False,
            physical_release=False,
        ),
    )
    write(folder / "prerequisites.json", tools)
    base = folder / "campaign"
    write(base / "request.json", dict(native=True))
    report = dict(
        cases=[],
        native_geometry=[],
        engineering_design_complete=False,
        manufacturing_release=False,
        physical_release=False,
    )
    for case in targets:
        rel = Path("models") / case["architecture_id"]
        model = definitions[case["id"]]
        write(base / rel / "model.json", model)
        for name in ("model.FCStd", "model.step"):
            (base / rel / name).write_text(
                "Explicit protocol fixture; not actual native CAD\n"
            )
        p = model["parts"][0]
        proof = dict(
            schema="osr-factory-native-cad/1",
            input_sha256=n.sha(base / rel / "model.json"),
            exporter_sha256=n.sha(n.native.__file__),
            geometry_helpers_sha256=n.sha(
                Path(n.native.__file__).with_name("models.py")
            ),
            fcstd_reopened=True,
            step_reopened=True,
            part_count=1,
            parts=[
                dict(
                    id=p["id"],
                    volume_m3=volume(p),
                    bounds_m=p["at_m"]
                    + [p["at_m"][j] + global_size(p)[j] for j in range(3)],
                )
            ],
            volume_sum_m3=volume(p),
            files_sha256={
                name: n.sha(base / rel / name) for name in ("model.FCStd", "model.step")
            },
            physical_release=False,
        )
        write(base / rel / "native-cad.json", proof)
        report["cases"].append(
            dict(
                id=case["id"],
                case=case,
                selected_local_beam_ids=["selected-" + case["id"]],
            )
        )
        report["native_geometry"].append(
            dict(
                case_id=case["id"],
                candidate_id="selected-" + case["id"],
                model=(rel / "model.json").as_posix(),
                receipt=(rel / "native-cad.json").as_posix(),
                status="passed",
                part_count=1,
                physical_release=False,
            )
        )
    write(base / "report.json", report)
    return folder, targets


def test_complete_protocol_requires_two_cases_and_preserves_release_boundary(evidence):
    folder, targets = evidence
    result = n.acceptance(folder)
    assert result["schema"] == n.SCHEMA and result["passed"]
    assert result["required_case_ids"] == [c["id"] for c in targets]
    assert result["required_model_count"] == 2
    assert len(result["native_models"]) == 2
    assert all(
        r["fcstd_reopened"] and r["step_reopened"] for r in result["native_models"]
    )
    assert all(result[k] is False for k in n.FLAGS)
    write(folder / "acceptance.json", result)
    assert n.verify(folder) == result


@pytest.mark.parametrize(
    "mutation",
    ["none", "missing-one", "duplicate", "wrong-case", "failed", "not-requested"],
)
def test_native_omissions_and_failures_cannot_pass_permissive_campaign_verifier(
    evidence, mutation
):
    folder, _ = evidence
    path = folder / "campaign/report.json"
    report = json.loads(path.read_text())
    if mutation == "none":
        report["native_geometry"] = []
    elif mutation == "missing-one":
        report["native_geometry"].pop()
    elif mutation == "duplicate":
        report["native_geometry"][1] = deepcopy(report["native_geometry"][0])
    elif mutation == "wrong-case":
        report["native_geometry"][0]["case_id"] = "some-other-case"
    else:
        report["native_geometry"][0]["status"] = mutation
    write(path, report)
    with pytest.raises(ValueError, match="membership|did not pass"):
        n.acceptance(folder)


@pytest.mark.parametrize(
    "mutation",
    [
        "missing-step",
        "changed-fcstd",
        "wrong-model",
        "schema",
        "reopen",
        "exporter",
        "proof-count",
        "primitive-volume",
        "source-drift",
        "simulation-only",
    ],
)
def test_exact_geometry_proof_and_current_source_binding_are_mandatory(
    evidence, mutation
):
    folder, _ = evidence
    model = folder / "campaign/models/LM3/model.json"
    receipt = model.parent / "native-cad.json"
    if mutation == "missing-step":
        (model.parent / "model.step").unlink()
    elif mutation == "changed-fcstd":
        (model.parent / "model.FCStd").write_text("changed")
    elif mutation == "wrong-model":
        doc = json.loads(model.read_text())
        doc["parts"][0]["size_m"][0] = 2
        write(model, doc)
    elif mutation == "source-drift":
        doc = json.loads((folder / "request.json").read_text())
        doc["source_sha256"] = {}
        write(folder / "request.json", doc)
    elif mutation == "simulation-only":
        write(folder / "campaign/request.json", dict(native=False))
    else:
        doc = json.loads(receipt.read_text())
        if mutation == "schema":
            doc["schema"] = "unrecognised"
        elif mutation == "reopen":
            doc["step_reopened"] = False
        elif mutation == "exporter":
            doc["exporter_sha256"] = "b" * 64
        elif mutation == "proof-count":
            doc["part_count"] = 0
        elif mutation == "primitive-volume":
            doc["parts"][0]["volume_m3"] = 1
        write(receipt, doc)
    with pytest.raises(ValueError):
        n.acceptance(folder)


def test_fresh_runner_requests_real_native_campaign_and_seals_required_results(
    evidence, tmp_path, monkeypatch
):
    template, _ = evidence
    monkeypatch.setattr(n, "ROOT", tmp_path)
    calls = []

    def execute(path, *, native):
        calls.append(native)
        shutil.copytree(template / "campaign", path)

    monkeypatch.setattr(n.architecture, "run", execute)
    output = tmp_path / "build/fresh"
    result = n.run(output)
    assert calls == [True] and result["passed"]
    assert n.verify(output) == result
    with pytest.raises(ValueError, match="fresh build"):
        n.run(output)


def test_runner_source_failure_retains_request_failed_model_and_nonzero_cli(
    evidence, tmp_path, monkeypatch
):
    monkeypatch.setattr(n, "ROOT", tmp_path)

    def failed(path, *, native):
        assert native is True
        write(
            path / "models/failed-model/model.json", dict(id="failed-attempt", parts=[])
        )
        raise ValueError("source/environment changed during native execution")

    monkeypatch.setattr(n.architecture, "run", failed)
    output = tmp_path / "build/failed"
    assert n.main(["run", "--output", str(output)]) == 1
    assert (output / "request.json").is_file()
    assert (output / "campaign/models/failed-model/model.json").is_file()
    failure = json.loads((output / "failure.json").read_text())
    assert failure["passed"] is False and failure["retained_campaign"]
    assert json.loads((output / "acceptance.json").read_text()) == failure
    with pytest.raises((ValueError, KeyError)):
        n.verify(output)


def test_required_targets_come_from_current_input_cases_not_native_observations(
    monkeypatch,
):
    lm3 = [
        dict(id="LM3-light", architecture_id="LM3", total_mass_kg=1),
        dict(id="LM3-heavy-a", architecture_id="LM3", total_mass_kg=2),
        dict(id="LM3-heavy-z", architecture_id="LM3", total_mass_kg=2),
    ]
    six = [
        dict(id="six-light", architecture_id="metro-6car-planning", total_mass_kg=3),
        dict(id="six-heavy", architecture_id="metro-6car-planning", total_mass_kg=4),
    ]
    monkeypatch.setattr(n.architecture_mechanical, "run", lambda: dict(cases=lm3))
    monkeypatch.setattr(n.architecture, "read", lambda path: {})
    monkeypatch.setattr(n.architecture, "six_car_cases", lambda basis: six)
    monkeypatch.setattr(n.architecture, "validate_case", lambda case, current: None)
    assert [c["id"] for c in n.current_targets()] == ["LM3-heavy-z", "six-heavy"]
