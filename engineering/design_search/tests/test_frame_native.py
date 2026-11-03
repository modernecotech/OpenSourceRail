from copy import deepcopy
import json
import os

import pytest

from engineering.design_search import frame_analysis as f, frame_native as n
from engineering.station_rail.common import encoded, identity


def model():
    return dict(schema=f.SCHEMA, joint_hypothesis=f.JOINT,
        nodes=[dict(id="fixed", at_m=[0., 0., 0.]), dict(id="tip", at_m=[3., 0., 0.])],
        members=[dict(id="beam", start_node="fixed", end_node="tip", material_id="al",
            local_y=[0., 1., 0.], section=dict(width_m=.08, height_m=.16, wall_m=.004))],
        materials=dict(al=dict(law=f.LAW, E_Pa=70e9, nu=.33, density_kg_m3=2700.,
            source_basis="Declared method control, no delivered material qualification")),
        supports=[dict(node_id="fixed", dofs=[1, 2, 3, 4, 5, 6])],
        loads=[dict(node_id="tip", force_N=[0., 0., 10.], moment_Nm=[0., 0., 0.])])


def test_actual_hollow_section_and_roll_orientation_are_explicit():
    value = model()
    text, definition = n.deck(value, 4)
    assert "*ELEMENT,TYPE=B32R" in text and "SECTION=BOX" in text
    assert "0.08,0.16,0.004,0.004,0.004,0.004\n0,1,0" in text
    assert "SECTION=RECT" not in text
    assert definition["element_count"] == 4
    assert definition["model_id"] == identity(value)
    assert definition["original_node_numbers"] == {"fixed": 1, "tip": 2}
    different = deepcopy(value); different["members"][0]["local_y"] = [0., 0., 1.]
    changed, other = n.deck(different, 4)
    assert changed != text and other["model_id"] != definition["model_id"]


@pytest.mark.parametrize("subdivisions", [0, 3, True, 32])
def test_invalid_mesh_budgets_are_rejected_before_execution(subdivisions):
    with pytest.raises(ValueError, match="subdivisions"):
        n.deck(model(), subdivisions)


def test_unsupported_material_and_singular_models_do_not_receive_native_decks():
    value = model(); value["materials"]["al"]["law"] = "unknown-GFRP"
    with pytest.raises(ValueError, match="isotropic"):
        n.deck(value)
    value = model(); value["supports"] = []
    with pytest.raises(ValueError):
        n.deck(value)


def test_default_prepares_immutable_package_and_verify_never_executes_a_solver(tmp_path, monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError("Verification/preparation must not execute a solver")
    monkeypatch.setattr(n.subprocess, "run", forbidden)
    path = tmp_path / "prepared"
    result = n.run(model(), path)
    assert result["verified"] and result["native_jobs_used"] == 0
    assert result["native_state"] == "prepared-not-dispatched"
    assert result["comparison"] is None
    assert all(result[key] is False for key in n.FLAGS)
    request = json.loads((path/"input.json").read_bytes())
    assert request["resources"] == n._resources()
    assert request["model_id"] == identity(model())
    assert n.verify(path)["evaluation_id"] == result["evaluation_id"]
    with pytest.raises(FileExistsError):
        n.run(model(), path)


def test_missing_native_dependency_is_held_without_dispatch(tmp_path, monkeypatch):
    monkeypatch.setattr(n.shutil, "which", lambda _: None)
    result = n.run(model(), tmp_path/"missing", execute=True)
    assert result["native_state"] == "held-native-tool-unavailable"
    assert result["execution"] == "held" and result["native_jobs_used"] == 0


def test_payload_or_deck_tampering_cannot_verify(tmp_path):
    path = tmp_path / "prepared"
    n.run(model(), path)
    with (path/"frame.inp").open("a") as handle:
        handle.write("\n** unbound model change\n")
    with pytest.raises(ValueError, match="payload"):
        n.verify(path)


def test_resealed_physical_promotion_is_rejected(tmp_path):
    path = tmp_path / "prepared"
    n.run(model(), path)
    value = json.loads((path/"result.json").read_bytes())
    value["physical_accepted"] = True
    value.pop("evaluation_id"); value["evaluation_id"] = identity(value)
    (path/"result.json").write_bytes(encoded(value))
    manifest = json.loads((path/"manifest.json").read_bytes())
    manifest["evaluation_id"] = value["evaluation_id"]
    manifest["files_sha256"]["result.json"] = n.digest(path/"result.json")
    manifest.pop("manifest_id"); manifest["manifest_id"] = identity(manifest)
    (path/"manifest.json").write_bytes(encoded(manifest))
    with pytest.raises(ValueError, match="non-promoting"):
        n.verify(path)


def test_dat_parser_requires_finite_displacement_and_total_energy(tmp_path):
    path = tmp_path/"sample.dat"
    path.write_text("displacements\n1 0 0 0.001\nforces\n1 0 0 10\ntotal internal energy\n0.005\n")
    u, forces, energy = n.parse_dat(path)
    assert u == {1: [0., 0., .001]} and forces == {1: [0., 0., 10.]}
    assert energy == .005
    path.write_text("displacements\n1 0 0 nan\ntotal internal energy\n0.005\n")
    with pytest.raises(ValueError, match="nonfinite"):
        n.parse_dat(path)


def reseal(path, name, value, identity_key):
    value.pop(identity_key); value[identity_key] = identity(value)
    (path/name).write_bytes(encoded(value))
    manifest = json.loads((path/"manifest.json").read_bytes())
    manifest["files_sha256"][name] = n.digest(path/name)
    if name == "result.json": manifest["evaluation_id"] = value[identity_key]
    if name == "input.json": manifest["request_id"] = value[identity_key]
    manifest.pop("manifest_id"); manifest["manifest_id"] = identity(manifest)
    (path/"manifest.json").write_bytes(encoded(manifest))


@pytest.mark.parametrize("jobs", [0, 1])
def test_resealed_preparation_cannot_claim_completed_native_execution(tmp_path, jobs):
    path = tmp_path/"prepared"; n.run(model(), path)
    result = json.loads((path/"result.json").read_bytes())
    result.update(execution="completed", native_state="completed-native-frame-comparison", native_jobs_used=jobs)
    reseal(path, "result.json", result, "evaluation_id")
    with pytest.raises(ValueError, match="execution state"):
        n.verify(path)


@pytest.mark.parametrize("field", ["tool", "resources", "runtime"])
def test_resealed_native_tool_runtime_or_resource_substitution_is_rejected(tmp_path, field):
    path = tmp_path/"prepared"; n.run(model(), path)
    request = json.loads((path/"input.json").read_bytes())
    if field == "tool": request[field] = {"path":"/not-the-current-ccx", "sha256":"0"*64}
    elif field == "runtime": request[field]["python_version"] = "different"
    else: request[field]["effective_memory_bytes"] *= 2
    reseal(path, "input.json", request, "request_id")
    with pytest.raises(ValueError, match="tool, runtime or bounded resource"):
        n.verify(path)


def test_effective_resources_never_raise_lower_parent_caps(monkeypatch):
    monkeypatch.setattr(n.resource, "getrlimit", lambda kind: (512*1024**2, 768*1024**2)
        if kind == n.resource.RLIMIT_AS else (5, 8))
    result = n._resources()
    assert result["effective_memory_bytes"] == 512*1024**2
    assert result["effective_cpu_seconds"] == 5


def test_preexec_failure_is_retained_as_a_failed_attempt(tmp_path, monkeypatch):
    tool = tmp_path/"synthetic-ccx"
    tool.write_text("Synthetic tool bytes; subprocess is mocked and this file is never executed.\n")
    monkeypatch.setattr(n, "_tool", lambda: dict(path=str(tool), sha256=n.digest(tool)))
    def fail(*args, **kwargs):
        raise n.subprocess.SubprocessError("synthetic preexec failure")
    monkeypatch.setattr(n.subprocess, "run", fail)
    result = n.run(model(), tmp_path/"preexec", execute=True)
    assert result["execution"] == "failed" and result["native_jobs_used"] == 1
    assert "synthetic preexec failure" in result["failure"]
    assert result["comparison"] is None


def test_conflicting_source_context_or_non_boolean_execute_is_rejected(tmp_path):
    with pytest.raises(ValueError, match="Conflicting"):
        n.run(model(), tmp_path/"conflict", source_sha256={n.PRODUCER:"0"*64})
    with pytest.raises(ValueError, match="Boolean"):
        n.run(model(), tmp_path/"truthy", execute="yes")


def test_parent_thread_runtime_change_cannot_reuse_comparison(tmp_path, monkeypatch):
    path = tmp_path/"prepared"; n.run(model(), path)
    monkeypatch.setenv("OMP_NUM_THREADS", "different")
    with pytest.raises(ValueError, match="runtime"):
        n.verify(path)


@pytest.mark.skipif(os.environ.get("OSR_TEST_NATIVE_FRAME") != "1",
    reason="Set OSR_TEST_NATIVE_FRAME=1 for one bounded CalculiX bending method control")
def test_optional_native_bending_control_and_readonly_replay(tmp_path, monkeypatch):
    if n.shutil.which("ccx") is None:
        pytest.fail("Explicit native frame test requires CalculiX on PATH")
    value = model()
    length, force, modulus = 3.0, 10.0, 70e9
    width, height, wall = .08, .16, .004
    inertia = (width*height**3-(width-2*wall)*(height-2*wall)**3)/12
    expected = force*length**3/(3*modulus*inertia)
    path = tmp_path/"native-bending"
    result = n.run(value, path, execute=True, subdivisions=8)
    assert result["execution"] == "completed" and result["native_jobs_used"] == 1
    assert result["numerical_validity"] == "unqualified-native-frame-comparison"
    # A declared method sanity screen between different beam approximations;
    # this threshold does not establish a vehicle or material acceptance limit.
    assert result["comparison"]["displacements_m"]["tip"][2] == pytest.approx(expected, rel=.05)
    assert all(result[key] is False for key in n.FLAGS)
    before = {p.name:n.digest(p) for p in path.iterdir()}
    def forbidden(*args, **kwargs):
        raise AssertionError("Read-only native verification must not run a second solve")
    monkeypatch.setattr(n.subprocess, "run", forbidden)
    assert n.verify(path)["evaluation_id"] == result["evaluation_id"]
    assert before == {p.name:n.digest(p) for p in path.iterdir()}
