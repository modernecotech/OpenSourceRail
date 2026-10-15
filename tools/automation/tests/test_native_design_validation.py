"""Required native-profile protocol; fixtures never stand in for native physics."""

import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
from xml.etree import ElementTree

import pytest

ROOT = Path(__file__).resolve().parents[3]
SPEC = importlib.util.spec_from_file_location(
    "native_profile_local_validation", ROOT / "tools/automation/local_validation.py"
)
LOCAL = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(LOCAL)


def checkout(path):
    subprocess.run(["git", "init", "-q", str(path)], check=True)
    (path / ".gitignore").write_text("build/\n__pycache__/\n")
    subprocess.run(["git", "add", "."], cwd=path, check=True)
    subprocess.run(
        [
            "git",
            "-c",
            "user.name=Test",
            "-c",
            "user.email=test@example.invalid",
            "commit",
            "-qm",
            "explicit protocol fixture",
        ],
        cwd=path,
        check=True,
    )


def test_native_profile_requests_installed_tests_explicitly_and_preserves_release_profiles():
    output = ROOT / "build/validation/profile-protocol-preview"
    rows = LOCAL.plan("native-design", output)
    assert "native-design" in LOCAL.PROFILES
    assert LOCAL.RELEASE_PROFILES == {"ci", "kani", "integrated-stack", "example-city"}
    assert len(rows) == 3
    assert "native_design_prerequisites" in rows[0]["argv"][-2]
    argv = rows[1]["argv"]
    assert argv[:2] == ["env", "OSR_RUN_NATIVE_PARTS=1"]
    assert "OSR_NATIVE_PARTS_OUTPUT=" + str(output / "native-design/tests") in argv
    assert "engineering/analysis/tests/test_generated_parts_native.py" in argv
    assert "--junitxml=" + str(output / "native-design/tests.xml") in argv
    assert "native_design_acceptance" in rows[2]["argv"][-2]
    assert not any(
        "install" in arg or "docker" in arg for row in rows for arg in row["argv"]
    )


def test_explicit_opt_in_missing_tools_raises_instead_of_skipping(monkeypatch):
    monkeypatch.setenv("OSR_RUN_NATIVE_PARTS", "1")
    spec = importlib.util.spec_from_file_location(
        "missing_native_acceptance_fixture",
        ROOT / "engineering/analysis/tests/test_generated_parts_native.py",
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    assert not getattr(module.NativeGeneratedPartsTests, "__unittest_skip__", False)
    monkeypatch.setattr(
        module,
        "toolchain",
        lambda: {"available": False, "missing": ["FreeCAD", "Gmsh", "CalculiX"]},
    )
    with pytest.raises(
        RuntimeError,
        match="Explicit native part acceptance requires.*FreeCAD, Gmsh, CalculiX",
    ):
        module.NativeGeneratedPartsTests.setUpClass()


def test_broad_default_retains_optional_native_tests(monkeypatch):
    monkeypatch.delenv("OSR_RUN_NATIVE_PARTS", raising=False)
    spec = importlib.util.spec_from_file_location(
        "optional_native_acceptance_fixture",
        ROOT / "engineering/analysis/tests/test_generated_parts_native.py",
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    assert module.NativeGeneratedPartsTests.__unittest_skip__


def test_real_profile_missing_tool_command_keeps_failed_receipt(tmp_path):
    """Use the actual planned first command with an explicitly fake missing provider."""
    checkout(tmp_path)
    scripts = tmp_path / "tools/automation"
    scripts.mkdir(parents=True)
    for name in ("local_validation.py", "osr-python"):
        shutil.copy2(ROOT / "tools/automation" / name, scripts / name)
    package = tmp_path / "engineering/design_engine"
    package.mkdir(parents=True)
    (tmp_path / "engineering/__init__.py").write_text("")
    (package / "__init__.py").write_text("")
    (package / "generated_parts_native.py").write_text(
        "def toolchain():\n return {'available':False,'missing':['FreeCAD (explicit missing-provider fixture)']}\n"
    )
    output = tmp_path / "build/validation/missing-native"
    receipt = LOCAL.run("native-design", output, tmp_path)
    assert not receipt["passed"] and receipt["source_unchanged"]
    assert len(receipt["results"]) == 1
    assert receipt["results"][0]["exit_code"] != 0
    assert (
        "Required native-design prerequisites unavailable: FreeCAD"
        in (output / "000.log").read_text()
    )
    retained = json.loads((output / "native-design/prerequisites.json").read_text())
    assert retained["available"] is False
    assert receipt["physical_release"] is False and "artifacts" not in receipt
    with pytest.raises(ValueError, match="local validation failed"):
        LOCAL.verify(output, tmp_path)


def fixture_artifacts(folder):
    """Protocol fixture only: no CAD, mesh or physical acceptance is claimed."""
    folder.mkdir(parents=True)
    (folder / "prerequisites.json").write_text(
        LOCAL.encode({"available": True, "missing": []})
    )
    suite = ElementTree.Element("testsuite")
    for name in LOCAL.NATIVE_DESIGN_REQUIRED_TESTS:
        ElementTree.SubElement(suite, "testcase", name=name)
    ElementTree.ElementTree(suite).write(folder / "tests.xml")
    checks = {
        name: {"state": "passed"}
        for name in (
            "geometry",
            "mass_inertia",
            "linear_service",
            "load_equilibrium",
            "mesh_refinement",
            "independent_benchmark",
        )
    }
    checks.update(
        {
            name: {"state": "unknown"}
            for name in ("physical_correlation", "independent_acceptance")
        }
    )
    for case in ("cleat", "civil"):
        base = folder / "tests" / case
        (base / "cad").mkdir(parents=True)
        geometry = base / "cad/part.step"
        geometry.write_text("Explicit receipt-protocol fixture; not actual CAD\n")
        report = dict(
            physical_release=False,
            independently_accepted=False,
            checks=checks,
            meshes=[{}, {}],
            benchmark={"passed": True},
            definition_sha256="a" * 64,
            artifacts_sha256={"cad/part.step": LOCAL.digest(geometry)},
        )
        (base / "native-result.json").write_text(LOCAL.encode(report))
    for name in (
        "bad-mesh/gmsh.log",
        "bad-solver/calculix.log",
        "owned-timeout/timeout.log",
        "owned-timeout/owned.json",
    ):
        path = folder / "tests" / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("Explicit test protocol fixture\n")
    (folder / "acceptance.json").write_text(
        LOCAL.encode(LOCAL.native_design_acceptance(folder))
    )


def test_native_receipt_seals_full_tree_and_detects_tampering(tmp_path, monkeypatch):
    checkout(tmp_path)
    source = tmp_path / "build/protocol-input"
    fixture_artifacts(source)
    output = tmp_path / "build/validation/protocol-only"
    monkeypatch.setattr(
        LOCAL,
        "plan",
        lambda *args: [
            LOCAL.command(
                "Explicit receipt protocol fixture, no native physics",
                sys.executable,
                "-c",
                "import shutil; shutil.copytree("
                + repr(str(source))
                + ","
                + repr(str(output / "native-design"))
                + ")",
            )
        ],
    )
    receipt = LOCAL.run("native-design", output, tmp_path)
    assert receipt["passed"]
    assert "native-design/tests/cleat/cad/part.step" in receipt["artifacts"]
    assert "native-design/tests.xml" in receipt["artifacts"]
    assert "native-design/prerequisites.json" in receipt["artifacts"]
    assert LOCAL.verify(output, tmp_path) == receipt
    (output / "native-design/tests/cleat/cad/part.step").write_text(
        "changed fixture bytes"
    )
    with pytest.raises(ValueError, match="artifact changed"):
        LOCAL.verify(output, tmp_path)


@pytest.mark.parametrize(
    "fault",
    [
        "missing-test",
        "skipped",
        "failed",
        "missing-report",
        "missing-acceptance",
        "linked-artifact",
    ],
)
def test_native_acceptance_rejects_omissions_skips_and_links(tmp_path, fault):
    native = tmp_path / "native-design"
    fixture_artifacts(native)
    if fault in {"missing-test", "skipped", "failed"}:
        tree = ElementTree.parse(native / "tests.xml")
        case = tree.getroot().find("testcase")
        if fault == "missing-test":
            tree.getroot().remove(case)
        else:
            ElementTree.SubElement(case, "skipped" if fault == "skipped" else "failure")
        tree.write(native / "tests.xml")
    elif fault == "missing-report":
        (native / "tests/civil/native-result.json").unlink()
    elif fault == "missing-acceptance":
        (native / "acceptance.json").unlink()
    else:
        path = native / "tests/cleat/cad/part.step"
        external = tmp_path / "external.step"
        external.write_bytes(path.read_bytes())
        path.unlink()
        path.symlink_to(external)
    with pytest.raises(ValueError):
        LOCAL.artifact_hashes("native-design", tmp_path)
