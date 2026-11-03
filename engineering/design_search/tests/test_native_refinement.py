"""Bounded axial refinement: graph evidence is not whole-body qualification."""
from copy import deepcopy
import json
import os
import shutil

import pytest

from engineering.design_search import design_grammar, grammar_structure, native_refinement as refinement
from engineering.station_rail.common import encoded, identity


@pytest.fixture(scope="module")
def candidates():
    values = []
    for braced in (False, True):
        p = design_grammar.parameters()
        p["braced"] = braced
        values.append(design_grammar.build(p))
    return values


def reseal(value, key):
    value[key] = identity({k:v for k,v in value.items() if k != key})
    return value


def reseal_package(folder):
    manifest = json.loads((folder / "manifest.json").read_bytes())
    manifest["files"] = refinement._inventory(folder)
    manifest["directories"] = refinement._directories(folder)
    result = json.loads((folder / "result.json").read_bytes())
    manifest["evaluation_id"] = result["evaluation_id"]
    (folder / "manifest.json").write_bytes(encoded(reseal(manifest, "manifest_id")))


def test_axial_independent_analytical_controls():
    controls = grammar_structure.benchmark_plan()
    jobs = {j["id"]:j["graph"] for j in controls["native_jobs"]}
    axial = grammar_structure.linear_reference(jobs["axial-s1"])
    tripod = grammar_structure.linear_reference(jobs["tripod-s1"])
    assert axial["displacements_m"]["tip"][0] == pytest.approx(controls["analytical_checks"]["axial_tip_x_m"], rel=1e-12)
    assert axial["reactions_N"]["fixed"][0] == pytest.approx(-1200.0)
    assert tripod["displacements_m"]["3"][2] == pytest.approx(controls["analytical_checks"]["tripod_tip_z_m"], rel=1e-12)
    assert grammar_structure.diagnose_rigidity(controls["necessary_controls"][0]["graph"])["mechanism_count"] == 1


def test_pure_request_is_stable_and_resource_bound(candidates):
    a = refinement.request(candidates[1])
    b = refinement.request(candidates[1])
    changed = refinement.request(candidates[1], memory_mb=2048)
    assert a == b
    assert a["request_id"] == identity({k:v for k,v in a.items() if k != "request_id"})
    assert a["candidate_id"] == candidates[1]["candidate_id"]
    assert a["definition_id"] == candidates[1]["definition_id"]
    assert a["request_id"] != changed["request_id"]


def test_unavailable_tool_is_represented_in_request_but_cannot_dispatch(tmp_path, candidates, monkeypatch):
    monkeypatch.setattr(refinement, "_tool", lambda:dict(path="/usr/bin/ccx", sha256=None, available=False))
    request = refinement.request(candidates[1], native_jobs=1)
    assert request["tool"]["available"] is False
    assert request["tool"]["sha256"] is None
    monkeypatch.setattr(refinement.grammar_structure, "run", lambda *a, **k: pytest.fail("unavailable solver dispatched"))
    with pytest.raises(ValueError, match="CalculiX is unavailable"):
        refinement.evaluate(candidates[1], output=tmp_path / "axial", native_jobs=1)
    assert not (tmp_path / "axial").exists()


def test_excessive_analytical_load_is_held_before_native_dispatch(tmp_path, candidates, monkeypatch):
    candidate = deepcopy(candidates[1])
    for load in candidate["structure"]["loads"]:
        load["force_N"] = [1000 * force for force in load["force_N"]]
    candidate["definition_id"] = identity({k:v for k,v in candidate.items() if k != "definition_id"})
    assessment = refinement.assess(candidate)
    assert assessment["axial_status"] == "outside-linear-domain-analytical"
    assert assessment["axial_reference"] is not None
    assert assessment["analytical_maximum_member_relative_displacement_to_length"] >= 0.01
    assert any(task["kind"] == "nonlinear-or-revised-load-path-evaluator" for task in assessment["next_tasks"])
    assert assessment["whole_body_rejected"] is False
    monkeypatch.setattr(refinement.grammar_structure, "run", lambda *a, **k: pytest.fail("outside-domain solver dispatched"))
    out = tmp_path / "axial"
    result = refinement.evaluate(candidate, output=out, native_jobs=1)
    assert result["native_state"] == "held-by-axial-model-diagnostic"
    assert result["native_jobs_used"] == 0
    assert refinement.verify(out, candidate, native_jobs=1)["verified"]


def test_real_braced_and_unbraced_graphs_have_separate_model_holds(candidates):
    unbraced, braced = [refinement.assess(c) for c in candidates]
    assert unbraced["candidate_id"] != braced["candidate_id"]
    assert unbraced["axial_diagnostic"]["mechanism_count"] > 0
    assert unbraced["axial_status"] == "graph-mechanism-model-only"
    assert unbraced["axial_reference"] is None
    assert braced["axial_diagnostic"]["mechanism_count"] == 0
    assert braced["axial_status"] == "rigid-axial-graph-analytical-only"
    assert braced["axial_reference"] is not None
    for result in (unbraced, braced):
        assert result["shell_admission"]["status"] == "held-by-shell-model-domain"
        assert result["whole_body_rejected"] is False
        assert result["integrated_selection"] is None
        assert all(result[k] is False for k in refinement.FLAGS)
        assert result["assessment_id"] == identity({k:v for k,v in result.items() if k != "assessment_id"})


def test_solid_topology_is_held_in_axial_domain_and_assessed_separately(candidates):
    from engineering.design_search import system_body

    candidate = system_body.build(candidates[0], topology="aluminium_frame", profile_policy="aligned")
    assert "configuration_adopted" not in candidate
    result = refinement.assess(candidate)
    assert result["axial_status"] == "axial-model-domain-unavailable"
    assert result["axial_diagnostic"] is None
    assert result["shell_admission"]["status"] == "admitted-for-separate-method-check"
    assert result["whole_body_rejected"] is False
    assert result["physical_accepted"] is False


def test_zero_budget_never_dispatches_and_packages_are_immutable(tmp_path, candidates, monkeypatch):
    def forbidden(*args, **kwargs):
        pytest.fail("native solver was dispatched with zero budget")
    monkeypatch.setattr(refinement.grammar_structure, "run", forbidden)
    out = tmp_path / "axial"
    result = refinement.evaluate(candidates[1], output=out)
    assert result["native_state"] == "not-requested" and result["native_jobs_used"] == 0
    assert refinement.verify(out, candidates[1])["verified"]
    with pytest.raises(FileExistsError):
        refinement.evaluate(candidates[1], output=out)
    with pytest.raises(ValueError, match="candidate, source, resource"):
        refinement.verify(out, candidates[1], memory_mb=2048)


def test_requested_job_is_held_on_mechanism_without_dispatch(tmp_path, candidates, monkeypatch):
    if not refinement._tool()["available"]:
        pytest.skip("CalculiX not installed")
    monkeypatch.setattr(refinement.grammar_structure, "run", lambda *a, **k: pytest.fail("mechanism was dispatched"))
    out = tmp_path / "axial"
    result = refinement.evaluate(candidates[0], output=out, native_jobs=1)
    assert result["native_state"] == "held-by-axial-model-diagnostic"
    assert result["native_jobs_used"] == 0
    assert refinement.verify(out, candidates[0], native_jobs=1)["verified"]


def test_resealed_result_and_request_changes_are_rejected(tmp_path, candidates):
    out = tmp_path / "axial"
    refinement.evaluate(candidates[0], output=out)
    result_path = out / "result.json"
    value = json.loads(result_path.read_bytes())
    value["axial_status"] = "rigid-axial-graph-analytical-only"
    result_path.write_bytes(encoded(reseal(value, "evaluation_id")))
    reseal_package(out)
    with pytest.raises(ValueError, match="exact bound assessment"):
        refinement.verify(out, candidates[0])


def test_resealed_request_source_cannot_be_attributed_to_current_candidate(tmp_path, candidates):
    out = tmp_path / "axial"
    refinement.evaluate(candidates[0], output=out)
    request_path = out / "request.json"
    request = json.loads(request_path.read_bytes())
    request["source_sha256"][design_grammar.PRODUCER] = "0" * 64
    request_path.write_bytes(encoded(reseal(request, "request_id")))
    result_path = out / "result.json"
    value = json.loads(result_path.read_bytes())
    value["request"] = request
    result_path.write_bytes(encoded(reseal(value, "evaluation_id")))
    reseal_package(out)
    manifest_path = out / "manifest.json"
    manifest = json.loads(manifest_path.read_bytes())
    manifest["request_id"] = request["request_id"]
    manifest_path.write_bytes(encoded(reseal(manifest, "manifest_id")))
    with pytest.raises(ValueError, match="candidate, source, resource"):
        refinement.verify(out, candidates[0])


def test_held_mechanism_is_recorded_even_if_solver_is_unavailable(tmp_path, candidates, monkeypatch):
    monkeypatch.setattr(refinement, "_tool", lambda:dict(path="/usr/bin/ccx", sha256=None, available=False))
    out = tmp_path / "axial"
    result = refinement.evaluate(candidates[0], output=out, native_jobs=1)
    assert result["native_state"] == "held-by-axial-model-diagnostic"
    assert result["native_jobs_used"] == 0
    assert refinement.verify(out, candidates[0], native_jobs=1)["verified"]


def test_source_load_and_candidate_swaps_are_rejected(tmp_path, candidates):
    out = tmp_path / "axial"
    refinement.evaluate(candidates[0], output=out)
    with pytest.raises(ValueError, match="candidate, source, resource"):
        refinement.verify(out, candidates[1])
    changed = deepcopy(candidates[0])
    changed["structure"]["loads"][0]["force_N"][2] -= 1
    changed["definition_id"] = identity({k:v for k,v in changed.items() if k != "definition_id"})
    with pytest.raises(ValueError, match="candidate, source, resource"):
        refinement.verify(out, changed)
    altered = deepcopy(candidates[0])
    altered["sources"][design_grammar.PRODUCER] = "0" * 64
    altered["definition_id"] = identity({k:v for k,v in altered.items() if k != "definition_id"})
    with pytest.raises(ValueError, match="source"):
        refinement.verify(out, altered)


@pytest.mark.parametrize("kwargs", [dict(native_jobs=True), dict(native_jobs=2), dict(memory_mb=512),
                                     dict(timeout_s=90), dict(subdivisions=3)])
def test_invalid_budgets_are_refused(tmp_path, candidates, kwargs):
    with pytest.raises(ValueError):
        refinement.evaluate(candidates[0], output=tmp_path / "axial", **kwargs)


def test_symlink_fifo_and_extra_directory_rejected(tmp_path, candidates):
    out = tmp_path / "axial"
    refinement.evaluate(candidates[0], output=out)
    (out / "extra").mkdir()
    with pytest.raises(ValueError, match="manifest or payload"):
        refinement.verify(out, candidates[0])
    (out / "extra").rmdir()
    (out / "result.json").unlink()
    os.mkfifo(out / "result.json")
    with pytest.raises(ValueError, match="regular"):
        refinement.verify(out, candidates[0])


@pytest.mark.skipif(os.environ.get("OSR_TEST_NATIVE_AXIAL") != "1" or not shutil.which("ccx"),
                    reason="explicitly opt in to the bounded native axial integration control")
def test_native_axial_run_and_read_only_replay(tmp_path, candidates, monkeypatch):
    out = tmp_path / "axial"
    result = refinement.evaluate(candidates[1], output=out, native_jobs=1)
    assert result["native_jobs_used"] == 1
    native = json.loads((out / "native" / "result.json").read_bytes())
    assert native["execution"] == "completed"
    assert native["numerical_validity"] == "verified_axial_method"
    def forbidden(*args, **kwargs):
        pytest.fail("verification dispatched a solver")
    monkeypatch.setattr(refinement.grammar_structure, "run", forbidden)
    assert refinement.verify(out, candidates[1], native_jobs=1)["verified"]
