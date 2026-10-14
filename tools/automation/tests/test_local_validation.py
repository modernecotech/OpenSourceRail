"""Local execution must preserve failures and bind evidence to exact source."""

import importlib.util
import json
import os
from pathlib import Path
import shlex
import socket
import subprocess
import sys
import time

import pytest

ROOT = Path(__file__).resolve().parents[3]
SPEC = importlib.util.spec_from_file_location(
    "local_validation", ROOT / "tools/automation/local_validation.py"
)
LOCAL = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(LOCAL)


@pytest.fixture
def checkout(tmp_path, monkeypatch):
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    (tmp_path / ".gitignore").write_text("build/\n")
    (tmp_path / "source.txt").write_text("original\n")
    subprocess.run(["git", "add", "."], cwd=tmp_path, check=True)
    subprocess.run(
        [
            "git",
            "-c",
            "user.name=Test",
            "-c",
            "user.email=test@example.invalid",
            "commit",
            "-qm",
            "fixture",
        ],
        cwd=tmp_path,
        check=True,
    )
    monkeypatch.setattr(
        LOCAL,
        "plan",
        lambda profile, output: [
            LOCAL.command("fixture check", sys.executable, "-c", 'print("checked")')
        ],
    )
    return tmp_path, tmp_path / "build/validation/fixture"


def test_success_is_verifiable_and_logs_stay_ignored(checkout):
    root, output = checkout
    receipt = LOCAL.run("quick", output, root)
    assert receipt["passed"] and receipt["source"]["clean"]
    assert receipt["physical_release"] is False
    assert (
        LOCAL.verify(output, root, receipt["source"]["commit"], clean=True) == receipt
    )
    assert not LOCAL.git(root, "status", "--porcelain")


@pytest.mark.parametrize("profile", ["ci", "kani"])
def test_independent_source_checks_still_run_after_a_coherence_failure(
    checkout, monkeypatch, profile
):
    root, output = checkout
    monkeypatch.setattr(
        LOCAL,
        "plan",
        lambda *args: [
            LOCAL.command(
                "failed artifact", sys.executable, "-c", "raise SystemExit(7)"
            ),
            LOCAL.command(
                "independent source suite",
                sys.executable,
                "-c",
                'print("independent suite executed")',
            ),
        ],
    )
    row = LOCAL.run(profile, output, root)
    assert row["passed"] is False
    assert [r["exit_code"] for r in row["results"]] == [7, 0]
    assert "independent suite executed" in (output / "001.log").read_text()


@pytest.mark.parametrize("mutation", ["tracked", "untracked", "new-commit"])
def test_receipts_cannot_cover_later_source_changes(checkout, mutation):
    root, output = checkout
    LOCAL.run("quick", output, root)
    (root / ("new.py" if mutation == "untracked" else "source.txt")).write_text(
        "changed"
    )
    if mutation == "new-commit":
        subprocess.run(["git", "add", "."], cwd=root, check=True)
        subprocess.run(
            [
                "git",
                "-c",
                "user.name=Test",
                "-c",
                "user.email=test@example.invalid",
                "commit",
                "-qm",
                "change",
            ],
            cwd=root,
            check=True,
        )
    with pytest.raises(ValueError, match="stale"):
        LOCAL.verify(output, root)


def test_source_changes_during_execution_fail(checkout, monkeypatch):
    root, output = checkout
    monkeypatch.setattr(
        LOCAL,
        "plan",
        lambda *args: [
            LOCAL.command(
                "mutating check",
                sys.executable,
                "-c",
                'from pathlib import Path; Path("source.txt").write_text("changed")',
            )
        ],
    )
    assert LOCAL.run("quick", output, root)["passed"] is False


def test_dirty_source_may_be_checked_but_cannot_release(checkout):
    root, output = checkout
    (root / "source.txt").write_text("work in progress")
    assert LOCAL.run("quick", output, root)["passed"]
    LOCAL.verify(output, root)
    with pytest.raises(ValueError, match="clean source"):
        LOCAL.verify(output, root, clean=True)


@pytest.mark.parametrize(
    "fault",
    ["failed", "timeout", "omitted-command", "log", "symlink", "escape", "acceptance"],
)
def test_failures_incomplete_coverage_and_log_tampering_are_rejected(
    checkout, monkeypatch, fault
):
    root, output = checkout
    if fault in ("failed", "timeout"):
        code = (
            "raise SystemExit(3)"
            if fault == "failed"
            else "import time; time.sleep(30)"
        )
        monkeypatch.setattr(
            LOCAL,
            "plan",
            lambda *args: [
                LOCAL.command("bad check", sys.executable, "-c", code, timeout=0.1)
            ],
        )
    receipt = LOCAL.run("quick", output, root)
    if fault == "omitted-command":
        receipt["results"] = []
    elif fault == "acceptance":
        receipt["physical_release"] = True
    elif fault in ("log", "symlink", "escape"):
        log = output / receipt["results"][0]["log"]
        original = log.read_text()
        if fault == "log":
            log.write_text(original + "changed")
        else:
            external = root / "build/elsewhere.log"
            external.write_text(original)
            if fault == "symlink":
                log.unlink()
                log.symlink_to(external)
            else:
                receipt["results"][0]["log"] = "../elsewhere.log"
    (output / "receipt.json").write_text(LOCAL.encode(receipt))
    with pytest.raises(ValueError):
        LOCAL.verify(output, root)


def test_local_run_cannot_inherit_github_execution_identity(checkout, monkeypatch):
    root, output = checkout
    monkeypatch.setenv("GITHUB_ACTIONS", "true")
    monkeypatch.setenv("GITHUB_RUN_ID", "123")
    monkeypatch.setattr(
        LOCAL,
        "plan",
        lambda *args: [
            LOCAL.command(
                "identity",
                sys.executable,
                "-c",
                'import os; assert not any(k.startswith("GITHUB_") for k in os.environ)',
            )
        ],
    )
    assert LOCAL.run("quick", output, root)["passed"]


def test_local_run_uses_candidate_packages_instead_of_other_editable_checkout(
    checkout, monkeypatch
):
    root, output = checkout
    for relative, package in [
        ("tools/osr-aln-convert/src", "osr_aln"),
        ("tools/reference-ma/src", "reference_ma"),
    ]:
        folder = root / relative / package
        folder.mkdir(parents=True)
        (folder / "__init__.py").write_text("CANDIDATE_SOURCE = True\n")
    subprocess.run(["git", "add", "."], cwd=root, check=True)
    subprocess.run(
        [
            "git",
            "-c",
            "user.name=Test",
            "-c",
            "user.email=test@example.invalid",
            "commit",
            "-qm",
            "candidate source packages",
        ],
        cwd=root,
        check=True,
    )
    monkeypatch.setenv("PYTHONDONTWRITEBYTECODE", "1")
    code = (
        "from pathlib import Path; import osr_aln,reference_ma; "
        "assert osr_aln.CANDIDATE_SOURCE and reference_ma.CANDIDATE_SOURCE; "
        "assert all(Path(module.__file__).resolve().is_relative_to(Path.cwd()) for module in (osr_aln,reference_ma)); "
        "print(osr_aln.__file__); print(reference_ma.__file__)"
    )
    monkeypatch.setattr(
        LOCAL,
        "plan",
        lambda *args: [
            LOCAL.command(
                "private candidate import origins", sys.executable, "-c", code
            )
        ],
    )
    receipt = LOCAL.run("quick", output, root)
    assert receipt["passed"] and receipt["source"]["clean"]
    assert LOCAL.verify(output, root, clean=True) == receipt
    log = (output / "000.log").read_text()
    assert str(root / "tools/osr-aln-convert/src/osr_aln/__init__.py") in log
    assert str(root / "tools/reference-ma/src/reference_ma/__init__.py") in log


def test_timeout_terminates_owned_child(checkout, monkeypatch):
    root, output = checkout
    code = (
        "import subprocess,sys,time; from pathlib import Path; "
        'p=subprocess.Popen([sys.executable,"-c","import time; time.sleep(30)"]); '
        'Path("build/child.pid").write_text(str(p.pid)); time.sleep(30)'
    )
    monkeypatch.setattr(
        LOCAL,
        "plan",
        lambda *args: [
            LOCAL.command("child timeout", sys.executable, "-c", code, timeout=0.5)
        ],
    )
    receipt = LOCAL.run("quick", output, root)
    assert receipt["results"][0]["exit_code"] == 124
    pid = int((root / "build/child.pid").read_text())
    # Reparented processes can briefly be zombies while init reaps them.
    deadline = time.monotonic() + 2
    while Path(f"/proc/{pid}/stat").exists() and time.monotonic() < deadline:
        if Path(f"/proc/{pid}/stat").read_text().split()[2] == "Z":
            break
        time.sleep(0.02)
    assert (
        not Path(f"/proc/{pid}/stat").exists()
        or Path(f"/proc/{pid}/stat").read_text().split()[2] == "Z"
    )


def test_release_requires_all_four_distinct_profiles(checkout, monkeypatch):
    root, base = checkout
    monkeypatch.setattr(LOCAL, "guard_containers", lambda *args: None)
    monkeypatch.setattr(LOCAL, "artifact_hashes", lambda *args: {})
    folders = []
    for profile in sorted(LOCAL.RELEASE_PROFILES):
        folder = base.parent / profile
        LOCAL.run(profile, folder, root)
        folders.append(folder)
    commit = LOCAL.git(root, "rev-parse", "HEAD")
    assert set(LOCAL.release_receipts(folders, commit, root)) == LOCAL.RELEASE_PROFILES
    for invalid in (folders[:-1], [*folders, folders[0]]):
        with pytest.raises(ValueError):
            LOCAL.release_receipts(invalid, commit, root)


@pytest.mark.parametrize("relative", ["var/example-city", "var/city-example"])
def test_destructive_scenarios_refuse_existing_fixture_files(
    tmp_path, monkeypatch, relative
):
    folder = tmp_path / relative
    folder.mkdir(parents=True)
    retained = folder / "operator-data"
    retained.write_text("preserve me")
    before = retained.stat()
    monkeypatch.setattr(
        LOCAL.subprocess,
        "check_output",
        lambda *args, **kwargs: pytest.fail(
            "Existing fixture guard must refuse before contacting Docker"
        ),
    )
    with pytest.raises(ValueError, match="existing fixture files"):
        LOCAL.guard_containers("example-city", tmp_path)
    assert retained.read_text() == "preserve me"
    assert retained.stat().st_mtime_ns == before.st_mtime_ns
    assert sorted(
        p.relative_to(tmp_path).as_posix() for p in tmp_path.rglob("*") if p.is_file()
    ) == [relative + "/operator-data"]


def test_example_city_refuses_an_actually_bound_recovery_port_before_docker(
    tmp_path, monkeypatch
):
    real_socket = socket.socket
    retained = tmp_path / "operator-data"
    retained.write_text("retain this unrelated operator file")
    before = retained.stat()
    with real_socket() as owner:
        owner.bind(("127.0.0.1", 28880))

        class PortProbe(real_socket):
            def bind(self, address):
                # Other canonical ports may belong to user services. Only those
                # unrelated probes use real ephemeral sockets in this test; the
                # recovery probe must hit the actual occupied canonical port.
                return super().bind(address if address[1] == 28880 else (address[0], 0))

        monkeypatch.setattr(LOCAL.socket, "socket", PortProbe)
        monkeypatch.setattr(
            LOCAL.subprocess,
            "check_output",
            lambda *args, **kwargs: pytest.fail(
                "Occupied recovery port must refuse before contacting Docker"
            ),
        )
        with pytest.raises(ValueError, match="port 28880 is occupied"):
            LOCAL.guard_containers("example-city", tmp_path)
    assert retained.read_text() == "retain this unrelated operator file"
    assert retained.stat().st_mtime_ns == before.st_mtime_ns


def test_workflow_adapter_preserves_background_services_and_always_cleanup(
    tmp_path, monkeypatch
):
    folder = tmp_path / ".github/workflows"
    folder.mkdir(parents=True)
    (folder / "fixture.yml").write_text("""jobs:
  test:
    steps:
      - name: Start worker
        run: sleep 60 & echo $! > build/worker.pid
      - name: Fail validation
        run: kill -0 "$(cat build/worker.pid)"; exit 9
      - name: Clean fixture
        if: always()
        run: touch build/cleaned; kill "$(cat build/worker.pid)"
""")
    monkeypatch.setattr(LOCAL, "ROOT", tmp_path)
    (tmp_path / "build").mkdir()
    commands = LOCAL.workflow_commands("fixture", tmp_path / "build")
    assert len(commands) == 1
    code = LOCAL.execute(
        commands[0]["argv"], tmp_path, tmp_path / "build/log", 5, dict(os.environ)
    )
    assert code == 9 and (tmp_path / "build/cleaned").is_file()


@pytest.mark.parametrize("missing", [None, "npm", "chromium"])
def test_mixed_setup_step_inspects_installed_tools_and_preserves_actual_pilot(
    tmp_path, monkeypatch, missing
):
    folder = tmp_path / ".github/workflows"
    folder.mkdir(parents=True)
    (tmp_path / "build").mkdir()
    pilot = (
        shlex.quote(sys.executable)
        + " -c "
        + shlex.quote(
            "from pathlib import Path; Path('build/pilot-ran').write_text('actual verification command executed')"
        )
    )
    (folder / "fixture.yml").write_text(
        "jobs:\n  test:\n    steps:\n      - name: Verify installed operations pilot\n        run: |\n"
        "          npm ci\n          npx playwright install --with-deps chromium\n          "
        + pilot
        + "\n"
    )
    binary = tmp_path / "bin"
    binary.mkdir()
    # Stand-ins enforce the allowed prerequisite protocol. They cannot install;
    # the real installed browser is exercised by the release prerequisite probe.
    scripts = {
        "npm": '#!/bin/sh\n[ "$*" = "ls --depth=0" ] || exit 99\n[ "$OSR_MISSING_SETUP" != "npm" ] || exit 6\nprintf inspected > build/npm-inspected\n',
        "node": '#!/bin/sh\n[ "$1" = "-e" ] || exit 99\nprintf "%s" "$2" > build/browser-probe-source\n[ "$OSR_MISSING_SETUP" != "chromium" ] || exit 7\n',
        "npx": "#!/bin/sh\nexit 99\n",
    }
    for name, content in scripts.items():
        path = binary / name
        path.write_text(content)
        path.chmod(0o755)
    monkeypatch.setattr(LOCAL, "ROOT", tmp_path)
    commands = LOCAL.workflow_commands("fixture", tmp_path / "build")
    assert len(commands) == 1
    row = commands[0]
    assert [entry["original"] for entry in row["setup_prerequisites"]] == [
        "npm ci",
        "npx playwright install --with-deps chromium",
    ]
    assert pilot in row["argv"][-1]
    assert "npx playwright install" not in row["argv"][-1]
    environment = dict(
        os.environ,
        PATH=str(binary) + os.pathsep + os.environ["PATH"],
        OSR_MISSING_SETUP=missing or "",
    )
    code = LOCAL.execute(row["argv"], tmp_path, tmp_path / "build/log", 10, environment)
    assert code == (6 if missing == "npm" else 7 if missing == "chromium" else 0)
    assert (tmp_path / "build/pilot-ran").exists() is (missing is None)
    if missing != "npm":
        assert (
            "chromium.launch({headless:true})"
            in (tmp_path / "build/browser-probe-source").read_text()
        )
    if missing is None:
        assert (
            tmp_path / "build/pilot-ran"
        ).read_text() == "actual verification command executed"


@pytest.mark.parametrize(
    "line",
    [
        "npm ci --ignore-scripts",
        "npm install",
        "npm --prefix somewhere ci",
        "npx playwright install firefox",
        "npx --yes playwright install --with-deps chromium",
        "npx playwright install --with-deps chromium && node actual-test.mjs",
        "PLAYWRIGHT_BROWSERS_PATH=/tmp/other npx playwright install --with-deps chromium",
        "python -m pip install unreviewed-package",
    ],
)
def test_unreviewed_inline_setup_forms_fail_instead_of_installing_or_skipping(line):
    with pytest.raises(ValueError, match="unsupported inline local setup"):
        LOCAL.installed_setup(line, "Verification step")


def test_reviewed_inline_browser_cache_prefix_is_preserved():
    prefix = LOCAL.PLAYWRIGHT_CACHE_PREFIX
    line, metadata = LOCAL.installed_setup(
        prefix + "npx playwright install --with-deps chromium", "Pilot"
    )
    assert line.startswith(prefix + "node -e ")
    assert metadata["original"].startswith(prefix)
    assert metadata["mode"] == "installed-prerequisite-check; no installation"


def test_every_production_profile_can_be_planned():
    for profile in LOCAL.PROFILES:
        assert LOCAL.plan(profile, ROOT / "build/validation/preview")
    ci = "\n".join(
        " ".join(row["argv"])
        for row in LOCAL.plan("ci", ROOT / "build/validation/preview")
    )
    assert (
        "audit-city-geography" in ci
        and "test:frontend" in ci
        and "cargo audit --deny warnings" in ci
    )


def test_clean_ci_generates_station_boms_before_their_reconciliation_tests():
    rows = LOCAL.plan("ci", ROOT / "build/validation/preview")
    names = [row["name"] for row in rows]
    prerequisite = names.index("Generate station BOM test prerequisites")
    assert rows[prerequisite]["argv"] == ["tools/automation/buildable-stations.sh"]
    assert prerequisite < names.index("Python tests")


def test_unknown_workflow_actions_cannot_silently_skip_verification(
    tmp_path, monkeypatch
):
    folder = tmp_path / ".github/workflows"
    folder.mkdir(parents=True)
    (folder / "fixture.yml").write_text(
        "jobs:\n  proof:\n    steps:\n      - uses: vendor/proof-checker@v1\n"
    )
    monkeypatch.setattr(LOCAL, "ROOT", tmp_path)
    with pytest.raises(ValueError, match="unsupported local action"):
        LOCAL.workflow_commands("fixture", tmp_path / "build")


def test_local_proof_artifact_tampering_invalidates_receipt(checkout, monkeypatch):
    root, output = checkout
    code = (
        "from pathlib import Path; p=Path("
        + repr(str(output / "safety-execution-fixture"))
        + '); p.mkdir(); (p/"proof.log").write_text("original")'
    )
    monkeypatch.setattr(
        LOCAL,
        "plan",
        lambda *args: [LOCAL.command("proof output", sys.executable, "-c", code)],
    )
    assert LOCAL.run("kani", output, root)["passed"]
    LOCAL.verify(output, root)
    (output / "safety-execution-fixture/proof.log").write_text("changed")
    with pytest.raises(ValueError, match="artifacts"):
        LOCAL.verify(output, root)


@pytest.mark.parametrize("timeout", [False, True])
def test_workflow_cleanup_runs_on_timeout_and_its_failure_blocks_success(
    tmp_path, monkeypatch, timeout
):
    folder = tmp_path / ".github/workflows"
    folder.mkdir(parents=True)
    (folder / "fixture.yml").write_text(
        """jobs:
  test:
    steps:
      - run: """
        + ("sleep 60" if timeout else "'true'")
        + """
      - name: Cleanup
        if: always()
        run: touch build/cleaned; exit 23
"""
    )
    monkeypatch.setattr(LOCAL, "ROOT", tmp_path)
    (tmp_path / "build").mkdir()
    row = LOCAL.workflow_commands("fixture", tmp_path / "build")[0]
    code = LOCAL.execute(
        row["argv"],
        tmp_path,
        tmp_path / "build/log",
        0.3 if timeout else 5,
        dict(os.environ),
    )
    assert code == (124 if timeout else 23)
    assert (tmp_path / "build/cleaned").is_file()
