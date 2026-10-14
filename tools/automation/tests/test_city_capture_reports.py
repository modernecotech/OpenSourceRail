"""Retain the canonical city reports before fixture cleanup removes originals."""

import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parents[3]
SPEC = importlib.util.spec_from_file_location(
    "city_capture_local_validation", ROOT / "tools/automation/local_validation.py"
)
LOCAL = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(LOCAL)
EXTRA = (
    "engineering-change-samawah.json",
    "engineering-change-mosul.json",
    "recovery-checkpoint.json",
    "recovery-result.json",
)
LEGACY = (
    "report.json",
    "expansion-report.json",
    "contract-report.json",
    "business-report.json",
    "disposition-report.json",
    "ui-report.json",
    "full-network/report.json",
)


def encoded(value):
    return (json.dumps(value, indent=3, sort_keys=True) + "\n").encode()


@pytest.fixture
def city(tmp_path, monkeypatch):
    root = tmp_path / "checkout"
    root.mkdir()
    (root / ".gitignore").write_text("build/\n__pycache__/\n")
    for relative in (
        "deployment/example-city/evidence.py",
        "tools/automation/local_validation.py",
    ):
        target = root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / relative, target)
    subprocess.run(["git", "init", "-q", str(root)], check=True)
    subprocess.run(["git", "add", "."], cwd=root, check=True)
    subprocess.run(
        [
            "git",
            "-c",
            "user.name=Fixture",
            "-c",
            "user.email=fixture@example.invalid",
            "commit",
            "-qm",
            "capture fixture",
        ],
        cwd=root,
        check=True,
    )
    commit = LOCAL.git(root, "rev-parse", "HEAD")
    source = root / "build/city-example"
    payloads = {}
    for name in LEGACY:
        payloads[name] = encoded(
            {"passed": True, "checks": [{"name": "synthetic fixture", "passed": True}]}
        )
    for name in EXTRA:
        # Recovery reports deliberately have no generic checks list.
        payloads[name] = encoded(
            {"schema": "synthetic-" + name, "passed": True, "physical_release": False}
        )
    manifest = {
        "schema": "osr-city-release-evidence/1",
        "passed": True,
        "clean_source": True,
        "commit": commit,
        "scenario_source": {"commit": commit, "clean_source": True},
        "reports": {
            name: hashlib.sha256(payloads[name]).hexdigest() for name in LEGACY
        },
    }
    payloads["city-evidence.json"] = encoded(manifest)
    for name, raw in payloads.items():
        target = source / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(raw)
    output = root / "build/validation/capture"
    monkeypatch.setattr(LOCAL, "ROOT", root)
    monkeypatch.setattr(LOCAL, "guard_containers", lambda *args: None)
    script = (
        "from pathlib import Path; import sys; "
        + "sys.path.insert(0, 'tools/automation'); "
        + "from local_validation import capture_city; capture_city(Path("
        + repr(str(output / "city"))
        + "))"
    )
    monkeypatch.setattr(
        LOCAL,
        "plan",
        lambda *args: [
            LOCAL.command(
                "capture synthetic city reports", sys.executable, "-c", script
            )
        ],
    )
    return SimpleNamespace(
        root=root,
        source=source,
        output=output,
        payloads=payloads,
        manifest=manifest,
        commit=commit,
    )


def test_complete_copy_preserves_exact_bytes_and_recursive_hash_coverage(city):
    receipt = LOCAL.run("example-city", city.output, city.root)
    assert receipt["passed"] and receipt["source_unchanged"]
    assert receipt["source"]["clean"]
    expected = {
        "city/" + name: hashlib.sha256(raw).hexdigest()
        for name, raw in city.payloads.items()
    }
    assert receipt["artifacts"] == expected
    assert LOCAL.artifact_hashes("example-city", city.output) == expected
    for name, raw in city.payloads.items():
        assert (city.output / "city" / name).read_bytes() == raw
    assert LOCAL.verify(city.output, city.root, city.commit, clean=True) == receipt
    # The capture remains complete after the canonical fixture reset.
    shutil.rmtree(city.source)
    assert LOCAL.verify(city.output, city.root, city.commit, clean=True) == receipt


@pytest.mark.parametrize("name", EXTRA)
def test_missing_executed_report_rejects_capture_before_any_copy(city, name):
    (city.source / name).unlink()
    with pytest.raises(ValueError, match="missing mandatory city report"):
        LOCAL.capture_city(city.output / "city")
    assert not city.output.exists()


@pytest.mark.parametrize("name", EXTRA)
def test_unparseable_executed_report_rejects_capture_before_any_copy(city, name):
    (city.source / name).write_bytes(b'{"passed": true,')
    with pytest.raises(json.JSONDecodeError):
        LOCAL.capture_city(city.output / "city")
    assert not city.output.exists()


@pytest.mark.parametrize("name", EXTRA)
@pytest.mark.parametrize("outside", [False, True])
def test_executed_report_symlinks_are_rejected_even_with_identical_bytes(
    city, name, outside
):
    target = city.source / name
    retained = (city.root.parent if outside else city.source) / "retained.json"
    retained.write_bytes(target.read_bytes())
    target.unlink()
    target.symlink_to(retained)
    with pytest.raises(ValueError, match="unsafe city report"):
        LOCAL.capture_city(city.output / "city")
    assert not city.output.exists()


@pytest.mark.parametrize("name", EXTRA)
def test_existing_receipt_rejects_tampered_captured_reports(city, name):
    assert LOCAL.run("example-city", city.output, city.root)["passed"]
    target = city.output / "city" / name
    target.write_bytes(target.read_bytes() + b" ")
    with pytest.raises(ValueError, match="changed local proof/city artifacts"):
        LOCAL.verify(city.output, city.root, city.commit, clean=True)


@pytest.mark.parametrize("name", ["../outside.json", "/absolute-report.json"])
def test_report_path_escape_is_rejected(city, name):
    city.manifest["reports"][name] = "a" * 64
    (city.source / "city-evidence.json").write_bytes(encoded(city.manifest))
    with pytest.raises(ValueError, match="unsafe city report path"):
        LOCAL.capture_city(city.output / "city")
    assert not city.output.exists()


def test_source_manifest_symlink_is_rejected(city):
    target = city.source / "city-evidence.json"
    retained = city.source / "retained-manifest.json"
    target.rename(retained)
    target.symlink_to(retained.name)
    with pytest.raises(ValueError, match="unsafe city report link"):
        LOCAL.capture_city(city.output / "city")


def test_destination_symlink_cannot_overwrite_another_report(city):
    destination = city.output / "city"
    destination.mkdir(parents=True)
    target = destination / EXTRA[0]
    retained = city.root / "build/keep.json"
    retained.write_bytes(b'"preserve this record"\n')
    target.symlink_to(retained)
    with pytest.raises(ValueError, match="unsafe city report"):
        LOCAL.capture_city(destination)
    assert retained.read_bytes() == b'"preserve this record"\n'


def test_current_commit_binding_is_still_required(city):
    city.manifest["commit"] = "b" * 40
    (city.source / "city-evidence.json").write_bytes(encoded(city.manifest))
    with pytest.raises(ValueError, match="clean release commit"):
        LOCAL.capture_city(city.output / "city")
    assert not city.output.exists()


def test_original_report_pass_checks_are_still_required(city):
    name = LEGACY[0]
    raw = encoded({"passed": False, "checks": []})
    (city.source / name).write_bytes(raw)
    city.manifest["reports"][name] = hashlib.sha256(raw).hexdigest()
    (city.source / "city-evidence.json").write_bytes(encoded(city.manifest))
    with pytest.raises(ValueError, match="City report failed/incomplete"):
        LOCAL.capture_city(city.output / "city")
    assert not city.output.exists()
