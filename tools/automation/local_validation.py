"""Local validation with exact source, command and output bindings.

GitHub stores source/results; this runner never requests a hosted job. Receipts
are untrusted local execution records, not independent safety acceptance.
"""

from __future__ import annotations
import hashlib
import json
import os
import re
import signal
import socket
import subprocess
import time
import shlex
import shutil
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RELEASE_PROFILES = {"ci", "kani", "integrated-stack", "example-city"}
NATIVE_DESIGN_REQUIRED_TESTS = (
    "test_actual_boolean_cad_two_meshes_and_independent_cantilever",
    "test_actual_gmsh_rejects_invalid_brep_without_fallback",
    "test_actual_civil_rhs_uses_same_solid_and_fixed_service_screen",
    "test_timeout_inherits_worker_group_and_kills_only_owned_descendants",
    "test_actual_calculix_rejects_invalid_deck_without_fallback",
    "test_exhausted_budget_never_launches_native_subprocess",
)


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def encode(value):
    return json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n"


def git(root, *args):
    return subprocess.check_output(["git", *args], cwd=root, text=True).strip()


def snapshot(root=ROOT):
    names = (
        subprocess.check_output(
            ["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard"],
            cwd=root,
        )
        .decode()
        .split("\0")
    )
    hashes = {}
    for name in sorted(set(filter(None, names))):
        path = root / name
        if path.is_symlink():
            hashes[name] = hashlib.sha256(
                ("symlink:" + os.readlink(path)).encode()
            ).hexdigest()
        elif path.is_file():
            hashes[name] = digest(path)
    return dict(
        commit=git(root, "rev-parse", "HEAD"),
        tree=git(root, "rev-parse", "HEAD^{tree}"),
        clean=not bool(git(root, "status", "--porcelain", "--untracked-files=normal")),
        files=hashes,
    )


def command(name, *argv, timeout=3600):
    return dict(name=name, argv=list(argv), timeout_seconds=timeout)


def python(name, *argv, timeout=3600):
    return command(name, "tools/automation/osr-python", *argv, timeout=timeout)


CHROMIUM_PREREQUISITE = (
    "const {chromium}=require('@playwright/test'); "
    "(async()=>{const browser=await chromium.launch({headless:true}); "
    "try {const page=await browser.newPage(); "
    "await page.setContent('<h1>Installed Chromium prerequisite</h1>'); "
    "if(await page.textContent('h1')!=='Installed Chromium prerequisite') "
    "throw Error('Chromium prerequisite render failed'); "
    "console.log(JSON.stringify({installed_chromium:browser.version()}));} "
    "finally {await browser.close();}})().catch(error=>{console.error(error);process.exitCode=1;});"
)
PLAYWRIGHT_CACHE_PREFIX = 'PLAYWRIGHT_BROWSERS_PATH="$HOME/.local/share/opensource-rail/toolchains/playwright" '


def installed_setup(line, title):
    """Adapt reviewed inline setup only; preserve every verification command.

    Local validation inspects installed npm dependencies and actually launches
    the installed Chromium. Unknown inline installation forms need an explicit
    adapter, rather than running installers or silently discarding a test.
    """
    text = line.strip()
    replacement = None
    if text == "npm ci":
        replacement = "npm ls --depth=0"
    elif text in {
        "npx playwright install --with-deps chromium",
        PLAYWRIGHT_CACHE_PREFIX + "npx playwright install --with-deps chromium",
    }:
        prefix = (
            PLAYWRIGHT_CACHE_PREFIX if text.startswith(PLAYWRIGHT_CACHE_PREFIX) else ""
        )
        replacement = prefix + "node -e " + shlex.quote(CHROMIUM_PREREQUISITE)
    elif not text.startswith("#") and (
        re.search(r"\bnpm\b.*\b(?:ci|install)\b", text)
        or re.search(r"\bnpx\b.*\bplaywright\s+install\b", text)
        or re.search(r"\bpip\s+install\b", text)
    ):
        raise ValueError("unsupported inline local setup in " + title + ": " + text)
    if replacement is None:
        return line, None
    indentation = line[: len(line) - len(line.lstrip())]
    return indentation + replacement, dict(
        source_step=title,
        original=text,
        replacement=replacement,
        mode="installed-prerequisite-check; no installation",
    )


def native_design_prerequisites(folder):
    """Record installed native providers; an explicit acceptance never skips."""
    from engineering.design_engine.generated_parts_native import toolchain

    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=False)
    native = toolchain()
    missing = list(native["missing"])
    if not (
        hasattr(os, "pidfd_open")
        and hasattr(signal, "pidfd_send_signal")
        and Path("/proc/self/stat").is_file()
    ):
        missing.append("Linux /proc and PIDfd owned-descendant cleanup")
    result = dict(
        schema="osr-native-design-prerequisites/1",
        toolchain=native,
        available=not missing,
        missing=missing,
        physical_release=False,
    )
    (folder / "prerequisites.json").write_text(encode(result))
    print(encode(result), flush=True)
    if missing:
        raise RuntimeError(
            "Required native-design prerequisites unavailable: " + ", ".join(missing)
        )
    return result


def native_design_acceptance(folder):
    """Read mandatory executed reports; no generic zero-test/skip success."""
    from xml.etree import ElementTree

    folder = Path(folder).resolve()

    def retained(relative):
        path = folder / relative
        if (
            path.is_symlink()
            or not path.resolve().is_relative_to(folder)
            or not path.is_file()
        ):
            raise ValueError("missing or unsafe native-design artifact: " + relative)
        return path

    prerequisite = json.loads(retained("prerequisites.json").read_text())
    if prerequisite.get("available") is not True or prerequisite.get("missing") != []:
        raise ValueError("native-design prerequisites did not pass")
    junit = ElementTree.parse(retained("tests.xml"))
    cases = junit.findall(".//testcase")
    names = [case.get("name") for case in cases]
    if (
        len(names) != len(set(names))
        or not set(NATIVE_DESIGN_REQUIRED_TESTS) <= set(names)
        or any(
            case.find(tag) is not None
            for case in cases
            for tag in ("skipped", "failure", "error")
        )
    ):
        raise ValueError("mandatory native-design tests missing, skipped or failed")
    numerical = (
        "geometry",
        "mass_inertia",
        "linear_service",
        "load_equilibrium",
        "mesh_refinement",
        "independent_benchmark",
    )
    summaries = {}
    for name in ("cleat", "civil"):
        report = json.loads(retained(f"tests/{name}/native-result.json").read_text())
        if (
            report.get("failure")
            or report.get("physical_release") is not False
            or report.get("independently_accepted") is not False
            or any(
                report.get("checks", {}).get(key, {}).get("state") != "passed"
                for key in numerical
            )
            or any(
                report.get("checks", {}).get(key, {}).get("state") != "unknown"
                for key in ("physical_correlation", "independent_acceptance")
            )
            or len(report.get("meshes", [])) < 2
            or report.get("benchmark", {}).get("passed") is not True
        ):
            raise ValueError(
                "native-design case incomplete or outside numerical acceptance: " + name
            )
        expected = report.get("artifacts_sha256", {})
        base = folder / "tests" / name
        actual = {
            p.relative_to(base).as_posix()
            for p in base.rglob("*")
            if p.is_file() and p != base / "native-result.json"
        }
        if not expected or actual != set(expected):
            raise ValueError("native-design artifact membership changed: " + name)
        for relative, sha in expected.items():
            if digest(retained(f"tests/{name}/" + relative)) != sha:
                raise ValueError(
                    "native-design artifact changed: " + name + "/" + relative
                )
        summaries[name] = dict(
            definition_sha256=report["definition_sha256"],
            meshes=len(report["meshes"]),
            numerical_checks_passed=True,
            physical_correlation="unknown",
            independent_acceptance="unknown",
        )
    for relative in (
        "tests/bad-mesh/gmsh.log",
        "tests/bad-solver/calculix.log",
        "tests/owned-timeout/timeout.log",
        "tests/owned-timeout/owned.json",
    ):
        retained(relative)
    return dict(
        schema="osr-native-design-acceptance/1",
        passed=True,
        executed_tests=sorted(names),
        cases=summaries,
        numerical_only=True,
        physical_release=False,
        independent_acceptance=False,
    )


def workflow_commands(name, output, selected_jobs=None, *, omit_unit_tests=False):
    import yaml

    path = ROOT / ".github/workflows" / (name + ".yml")
    data = yaml.safe_load(path.read_text())
    jobs = data["jobs"]
    if selected_jobs is not None and (
        set(jobs) != {"rust", "python-and-generated", "frontend", "tacs-formal"}
        or not selected_jobs <= set(jobs)
    ):
        raise ValueError("CI job coverage changed; update the explicit local adapter")
    # Native setup is an explicit prerequisite, never silently installed by checks.
    rows = []
    for job_name, job in jobs.items():
        if selected_jobs is not None and job_name not in selected_jobs:
            continue
        if job.get("strategy") or job.get("if") or job.get("defaults"):
            raise ValueError(
                "job execution needs an explicit local adapter: " + job_name
            )
        scripts = []
        cleanup = []
        setup_prerequisites = []
        for i, step in enumerate(job["steps"]):
            if "run" not in step:
                allowed_actions = (
                    "actions/checkout@",
                    "dtolnay/rust-toolchain@",
                    "Swatinem/rust-cache@",
                    "actions/setup-node@",
                    "actions/setup-python@",
                    "actions/setup-java@",
                    "actions/upload-artifact@",
                )
                if not step.get("uses", "").startswith(allowed_actions):
                    raise ValueError(
                        "unsupported local action: "
                        + step.get("uses", "missing run/uses")
                    )
                continue  # only known checkout/setup/cache/upload actions
            title = step.get("name", f"{name} step {i}")
            if title.startswith("Install "):
                continue  # require ./install.sh instead
            script = step["run"]
            if not isinstance(script, str):
                raise ValueError("workflow run must be a shell string: " + title)
            # Advisory auditing still runs; installing its tool is a prerequisite.
            script = "\n".join(
                line
                for line in script.splitlines()
                if not line.strip().startswith("cargo install ")
                and not (
                    omit_unit_tests and line.strip().startswith("python -m pytest ")
                )
            )
            if "${{" in script:
                raise ValueError(
                    "unsupported workflow expression in local command: " + title
                )
            adapted = []
            for line in script.splitlines():
                replacement, metadata = installed_setup(line, title)
                adapted.append(replacement)
                if metadata is not None:
                    setup_prerequisites.append(metadata)
            script = "\n".join(adapted)
            if any(
                key in step
                for key in ("env", "working-directory", "shell", "continue-on-error")
            ):
                raise ValueError(
                    "step execution needs an explicit local adapter: " + title
                )
            script = 'printf "%s\\n" ' + shlex.quote(title) + "\n" + script
            condition = step.get("if")
            if condition == "always()":
                cleanup.append(script)
            elif condition:
                raise ValueError("unsupported local condition: " + condition)
            else:
                if cleanup:
                    raise ValueError(
                        "always() steps must follow validation steps: " + title
                    )
                scripts.append(script)
        # One process group keeps background services alive between steps. The
        # trap runs cleanup on failure too, without swallowing the failing exit.
        exports = []
        for key, value in job.get("env", {}).items():
            if not key.replace("_", "").isalnum() or "${{" in str(value):
                raise ValueError("unsupported job environment")
            exports.append("export " + key + "=" + shlex.quote(str(value)))
        trap = ""
        if cleanup:
            cleanup_commands = []
            for script in cleanup:
                cleanup_commands.append(
                    "bash -euo pipefail -c "
                    + shlex.quote(script)
                    + '\nlocal cleanup_result=$?\nif [[ "$result" == 0 ]]; then result=$cleanup_result; fi'
                )
            trap = (
                "cleanup() {\nlocal result=$?\ntrap - EXIT\nset +e\n"
                + "\n".join(cleanup_commands)
                + '\nexit "$result"\n}\ntrap cleanup EXIT\ntrap "exit 143" TERM\ntrap "exit 130" INT\n'
            )
        if name == "example-city":
            scripts.append(
                "python3 -c "
                + shlex.quote(
                    "from pathlib import Path; from local_validation import capture_city; capture_city(Path("
                    + repr(str(output / "city"))
                    + "))"
                )
            )
        rows.append(
            dict(
                **command(
                    name + "/" + job_name,
                    "bash",
                    "-euo",
                    "pipefail",
                    "-c",
                    "\n".join(exports) + "\n" + trap + "\n".join(scripts),
                    timeout=7200,
                ),
                setup_prerequisites=setup_prerequisites,
            )
        )
    if not rows:
        raise ValueError("empty local integration recipe")
    return rows


def plan(profile, output):
    py = python
    quick = [
        command("Rust format", "cargo", "fmt", "--all", "--", "--check"),
        py(
            "Local validation and release tests",
            "-m",
            "pytest",
            "-q",
            "tools/automation/tests/test_local_validation.py",
            "tools/automation/tests/test_kani_release.py",
            "tools/automation/tests/test_release_evidence.py",
        ),
        py("README limits", "tools/automation/check-readmes.py"),
        py("Markdown links", "tools/automation/check-markdown-links.py"),
        py("Artifact sizes", "tools/automation/check-tracked-file-sizes.py"),
        py(
            "Current provenance",
            "tools/automation/dependency-impact.py",
            "--check-current",
        ),
        command("Whitespace", "git", "diff", "--check"),
    ]
    rust = [
        command("Rust format", "cargo", "fmt", "--all", "--", "--check"),
        command(
            "Clippy all features",
            "cargo",
            "clippy",
            "--workspace",
            "--all-targets",
            "--all-features",
            "--",
            "-D",
            "warnings",
        ),
        command(
            "Rust all features",
            "cargo",
            "test",
            "--workspace",
            "--all-targets",
            "--all-features",
        ),
        command(
            "Rust documentation",
            "cargo",
            "test",
            "--workspace",
            "--all-features",
            "--doc",
        ),
        command("Runtime binaries", "cargo", "check", "-p", "osr-runtime", "--bins"),
        command("RustSec advisories", "cargo", "audit", "--deny", "warnings"),
        py("City projects", "tools/automation/validate-city-projects.py"),
    ]
    python_checks = [
        py(
            "Python tests",
            "-m",
            "pytest",
            "-q",
            "design/city-generation/tests",
            "design/component-catalogue/tests",
            "engineering/analysis/tests",
            "tools/osr-aln-convert/tests",
            "tools/reference-ma/tests",
            "tools/automation/tests",
            timeout=7200,
        )
    ]
    evidence = [
        py(
            "Repository health",
            "tools/automation/repo-health.py",
            "--quiet",
            timeout=7200,
        ),
        py(
            "Current provenance",
            "tools/automation/dependency-impact.py",
            "--check-current",
        ),
        py(
            "Engineering baseline",
            "engineering/toolchain/baseline_assurance.py",
            "--check",
        ),
        py(
            "Design twin",
            "tools/automation/design-best-practice-twin.py",
            "check-public",
        ),
        py(
            "Panel definitions",
            "tools/automation/design-consistency-study.py",
            "--check",
        ),
        py("Panel responses", "tools/automation/panel-response-study.py", "--check"),
        py("GFRP study", "tools/automation/composite-panel-study.py", "--check"),
        py("Digital assurance", "tools/automation/digital-assurance.py", "--check"),
        py("Component assurance", "tools/automation/component_assurance.py", "--check"),
        py("Operating readiness", "tools/automation/operating-readiness.py", "--check"),
        py("Markdown links", "tools/automation/check-markdown-links.py"),
        py("Artifact sizes", "tools/automation/check-tracked-file-sizes.py"),
    ]
    browser = [
        command(
            "WASM GUI libraries",
            "cargo",
            "check",
            "--target",
            "wasm32-unknown-unknown",
            "-p",
            "osr-sim-gui",
            "-p",
            "osr-occ-gui",
            "--no-default-features",
        ),
        command("Browser acceptance", "npm", "run", "test:frontend", timeout=7200),
        command(
            "Offline operations browser",
            "node",
            "deployment/workbench/tests/verify-operations.mjs",
        ),
    ]
    formal = [
        py(
            "TACS replay",
            "tools/automation/tacs_assurance.py",
            "--check",
            "--verify-replay",
        ),
        py(
            "Pinned TLC verification",
            "-c",
            'from pathlib import Path; import hashlib; from tacs_assurance import JAR_SHA256; assert hashlib.sha256(Path("engineering/toolchain/tla/tla2tools-1.8.0.jar").read_bytes()).hexdigest() == JAR_SHA256',
        ),
        command(
            "Bounded TLC resource model",
            "bash",
            "-euo",
            "pipefail",
            "-c",
            "cd engineering/assurance/formal/tla\nexec java -cp ../../../toolchain/tla/tla2tools-1.8.0.jar tlc2.TLC -workers 1 -metadir "
            + shlex.quote(str(output / "tlc-state"))
            + " -config TACSResources.cfg TACSResources.tla",
            timeout=600,
        ),
    ]
    if profile == "quick":
        return quick
    if profile == "rust":
        return rust
    if profile == "python":
        return python_checks
    if profile == "evidence":
        return evidence
    if profile == "browser":
        return browser
    if profile == "native-design":
        native = output / "native-design"
        return [
            py(
                "Required native design prerequisites",
                "-c",
                "from pathlib import Path; import sys; from local_validation import native_design_prerequisites; native_design_prerequisites(Path(sys.argv[1]))",
                str(native),
                timeout=90,
            ),
            command(
                "Installed native design acceptance",
                "env",
                "OSR_RUN_NATIVE_PARTS=1",
                "OSR_NATIVE_PARTS_OUTPUT=" + str(native / "tests"),
                "tools/automation/osr-python",
                "-m",
                "pytest",
                "-q",
                "engineering/analysis/tests/test_generated_parts_native.py",
                "--junitxml=" + str(native / "tests.xml"),
                timeout=900,
            ),
            py(
                "Validate mandatory native design evidence",
                "-c",
                "from pathlib import Path; import sys; from local_validation import native_design_acceptance, encode; p=Path(sys.argv[1]); (p/'acceptance.json').write_text(encode(native_design_acceptance(p)))",
                str(native),
                timeout=90,
            ),
        ]
    if profile == "ci":
        return (
            # Broad independent source suites run before publication coherence;
            # later failures cannot suppress their recorded results.
            rust
            + [
                py(
                    "Restore ignored Baghdad test input",
                    "tools/automation/bootstrap_baghdad_tests.py",
                ),
                command(
                    "Generate station BOM test prerequisites",
                    "tools/automation/buildable-stations.sh",
                ),
            ]
            + python_checks
            + workflow_commands(
                "ci", output, {"python-and-generated", "frontend"}, omit_unit_tests=True
            )
            + formal
        )
    if profile == "kani":
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "local_proofs", ROOT / "tools/automation/assurance-evidence.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        packages = sorted({r["path"].split("/")[1] for r in module.declared()})
        rows = []
        for package in packages:
            folder = output / ("safety-execution-" + package)
            rows.append(
                py(
                    "Declared Kani " + package,
                    "tools/automation/assurance-evidence.py",
                    "run",
                    "--package",
                    package,
                    "--timeout",
                    "600",
                    "--memory-mib",
                    "4096",
                    "--output",
                    str(folder),
                    timeout=18000,
                )
            )
        rows += [
            command(
                "Kani MA arithmetic",
                "cargo",
                "kani",
                "-p",
                "osr-interlocking",
                "--harness",
                "kani_p5_time_bounded_arithmetic",
                timeout=1200,
            ),
            command(
                "Kani timestamped deadline",
                "cargo",
                "kani",
                "-p",
                "osr-brake",
                "--harness",
                "tacs_timestamped_output_rejects_invalid_source_age",
                timeout=1200,
            ),
            command(
                "Kani expired MA",
                "cargo",
                "kani",
                "-p",
                "osr-atp",
                "--harness",
                "kani_a2_expired_ma_trips",
                timeout=1200,
            ),
        ]
        return rows
    if profile in ("integrated-stack", "example-city"):
        return workflow_commands(profile, output)
    raise ValueError("unknown local validation profile: " + profile)


PROFILES = (
    "quick",
    "rust",
    "python",
    "evidence",
    "browser",
    "native-design",
    "ci",
    "kani",
    "integrated-stack",
    "example-city",
)


def guard_containers(profile, root=ROOT):
    if profile not in ("integrated-stack", "example-city"):
        return
    paths = (
        ["var/erpnext", "var/supervision", "build/integrated-stack"]
        if profile == "integrated-stack"
        else ["var/example-city", "var/city-example", "build/city-example"]
    )
    for relative in paths:
        folder = root / relative
        if folder.exists() and any(folder.iterdir()):
            raise ValueError(f"{profile} refuses existing fixture files: " + relative)
    # Canonical scenarios have fixed ports/project names. Never collide with a
    # user's existing deployment; run them on an otherwise disposable host.
    ports = (
        [8080, 8090, 8091, 8092, 1881]
        if profile == "integrated-stack"
        else [8180, 8190, 8191, 8192, 1981, 28880]
    )
    for port in ports:
        with socket.socket() as probe:
            try:
                probe.bind(("127.0.0.1", port))
            except OSError:
                raise ValueError(
                    f"{profile} requires a disposable host; port {port} is occupied"
                )
    docker = "docker"
    labels = (
        ["osr-erpnext", "osr-supervision"]
        if profile == "integrated-stack"
        else ["osr-example-erp", "osr-example-supervision"]
    )
    for project in labels:
        ids = subprocess.check_output(
            [
                docker,
                "ps",
                "-aq",
                "--filter",
                "label=com.docker.compose.project=" + project,
            ],
            text=True,
        ).strip()
        volumes = subprocess.check_output(
            [
                docker,
                "volume",
                "ls",
                "-q",
                "--filter",
                "label=com.docker.compose.project=" + project,
            ],
            text=True,
        ).strip()
        if ids or volumes:
            raise ValueError(f"{profile} refuses existing deployment data: " + project)


def capture_city(destination):
    import importlib.util

    destination = Path(destination).absolute()
    source = ROOT / "build/city-example"

    def report_path(folder, name):
        relative = Path(name)
        if relative.is_absolute() or ".." in relative.parts:
            raise ValueError("unsafe city report path: " + name)
        path = folder / relative
        if not path.resolve().is_relative_to(folder.resolve()):
            raise ValueError("unsafe city report path: " + name)
        for part in (path, *path.parents):
            if part.is_symlink():
                raise ValueError("unsafe city report link: " + name)
            if part == ROOT:
                break
        return path

    for folder in (source, destination):
        if not folder.resolve().is_relative_to(ROOT.resolve()):
            raise ValueError("city capture must remain inside the checkout")
        report_path(folder, ".")
    manifest_path = report_path(source, "city-evidence.json")
    manifest = json.loads(manifest_path.read_bytes())
    additional = (
        "engineering-change-samawah.json",
        "engineering-change-mosul.json",
        "recovery-checkpoint.json",
        "recovery-result.json",
    )
    payloads = {}
    for name in dict.fromkeys(
        ["city-evidence.json", *manifest["reports"], *additional]
    ):
        path = report_path(source, name)
        if not path.is_file():
            raise ValueError("missing mandatory city report: " + name)
        raw = path.read_bytes()
        json.loads(raw)
        payloads[name] = raw
        report_path(destination, name)
    spec = importlib.util.spec_from_file_location(
        "local_city_evidence", ROOT / "deployment/example-city/evidence.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    validated = module.validate(source, git(ROOT, "rev-parse", "HEAD"))
    if manifest != validated or any(
        hashlib.sha256(payloads[name]).hexdigest() != expected
        for name, expected in validated["reports"].items()
    ):
        raise ValueError("city report changed during capture")
    for name, raw in payloads.items():
        target = destination / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(raw)


def artifact_hashes(profile, folder):
    if profile == "native-design":
        native = folder / "native-design"
        if native.is_symlink() or not native.is_dir():
            raise ValueError("missing or unsafe native-design artifact folder")
        accepted = native / "acceptance.json"
        if (
            accepted.is_symlink()
            or not accepted.is_file()
            or json.loads(accepted.read_text()) != native_design_acceptance(native)
        ):
            raise ValueError("missing or changed native-design acceptance report")
    subfolders = (
        list(folder.glob("safety-execution-*"))
        if profile == "kani"
        else (
            [folder / "city"]
            if profile == "example-city"
            else [folder / "native-design"] if profile == "native-design" else []
        )
    )
    files = {}
    for subfolder in subfolders:
        if subfolder.is_symlink() or not subfolder.is_dir():
            raise ValueError("unsafe local artifact folder")
        for path in sorted(subfolder.rglob("*")):
            if path.is_symlink():
                raise ValueError("unsafe local artifact link")
            if path.is_file():
                files[path.relative_to(folder).as_posix()] = digest(path)
    return files


def execute(argv, root, log, seconds, env):
    with log.open("w") as stream:
        stream.write(encode(dict(command=argv)))
        stream.flush()
        proc = subprocess.Popen(
            argv,
            cwd=root,
            env=env,
            stdout=stream,
            stderr=subprocess.STDOUT,
            start_new_session=True,
        )
        try:
            try:
                return proc.wait(timeout=seconds)
            except subprocess.TimeoutExpired:
                os.killpg(proc.pid, signal.SIGTERM)
                try:
                    proc.wait(timeout=20)
                except subprocess.TimeoutExpired:
                    pass
                return 124
        finally:
            # Kill the owned group, including children that outlive their driver.
            try:
                os.killpg(proc.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            proc.wait()


def run(profile, output, root=ROOT):
    output = Path(output).resolve()
    if output.exists():
        raise ValueError("use a fresh local validation directory")
    if not output.is_relative_to(root.resolve()):
        raise ValueError("local outputs must be in this checkout")
    relative = output.relative_to(root).as_posix()
    if (
        subprocess.run(
            ["git", "check-ignore", "-q", relative + "/receipt.json"], cwd=root
        ).returncode
        != 0
    ):
        raise ValueError(
            "run receipts/logs must be Git-ignored; use build/validation/..."
        )
    guard_containers(profile, root)
    commands = plan(profile, output)
    output.mkdir(parents=True)
    before = snapshot(root)
    rows = []
    env = dict(os.environ)
    env["PYTHONPATH"] = os.pathsep.join(
        [
            str(root),
            str(root / "design/component-catalogue/src"),
            str(root / "design/city-generation/src"),
            str(root / "tools/osr-aln-convert/src"),
            str(root / "tools/reference-ma/src"),
            str(root / "tools/automation"),
        ]
    )
    # Genuine local provenance, even if invoked inside an action-emulating shell.
    for key in list(env):
        if key.startswith("GITHUB_"):
            env.pop(key)
    env.update(OPENBLAS_NUM_THREADS="1", OMP_NUM_THREADS="1", MKL_NUM_THREADS="1")
    receipt = dict(
        schema="osr-local-validation/1",
        profile=profile,
        execution_location="local",
        source=before,
        commands=commands,
        results=rows,
        passed=False,
        source_unchanged=None,
        started_at=datetime.now(timezone.utc).isoformat(),
        independent_acceptance=False,
        physical_release=False,
    )
    path = output / "receipt.json"
    path.write_text(encode(receipt))
    for i, item in enumerate(commands):
        log = output / (f"{i:03d}.log")
        started = time.monotonic()
        try:
            code = execute(item["argv"], root, log, item["timeout_seconds"], env)
        except OSError as error:
            log.write_text(
                encode(dict(command=item["argv"]))
                + "Cannot execute: "
                + str(error)
                + "\n"
            )
            code = 127
        rows.append(
            dict(
                name=item["name"],
                argv=item["argv"],
                exit_code=code,
                status=(
                    "passed" if code == 0 else "timeout" if code == 124 else "failed"
                ),
                duration_seconds=round(time.monotonic() - started, 3),
                log=log.name,
                log_sha256=digest(log),
            )
        )
        path.write_text(encode(receipt))
        print(item["name"], rows[-1]["status"], flush=True)
        if code and profile not in {
            "ci",
            "python",
            "evidence",
            "rust",
            "browser",
            "kani",
        }:
            break
    after = snapshot(root)
    receipt["source_unchanged"] = before == after
    receipt["passed"] = (
        len(rows) == len(commands)
        and all(r["exit_code"] == 0 for r in rows)
        and before == after
    )
    if receipt["passed"]:
        receipt["artifacts"] = artifact_hashes(profile, output)
    receipt["completed_at"] = datetime.now(timezone.utc).isoformat()
    path.write_text(encode(receipt))
    return receipt


def verify(folder, root=ROOT, commit=None, clean=False):
    folder = Path(folder).resolve()
    path = folder / "receipt.json"
    receipt = json.loads(path.read_text())
    if (
        receipt.get("schema") != "osr-local-validation/1"
        or receipt.get("execution_location") != "local"
        or receipt.get("passed") is not True
        or receipt.get("source_unchanged") is not True
    ):
        raise ValueError("local validation failed, incomplete or changed source")
    if (
        receipt.get("physical_release") is not False
        or receipt.get("independent_acceptance") is not False
    ):
        raise ValueError("local check cannot grant physical/independent acceptance")
    current = snapshot(root)
    if receipt["source"] != current:
        raise ValueError("stale local source/commit/tree/working state")
    if commit and receipt["source"]["commit"] != commit:
        raise ValueError("local validation belongs to another commit")
    if clean and not receipt["source"]["clean"]:
        raise ValueError("local release validation requires clean source")
    commands = plan(receipt["profile"], folder)
    if receipt["commands"] != commands or len(receipt["results"]) != len(commands):
        raise ValueError("local command coverage differs")
    for expected, row in zip(commands, receipt["results"]):
        if (
            row["name"] != expected["name"]
            or row["argv"] != expected["argv"]
            or row["status"] != "passed"
            or row["exit_code"] != 0
        ):
            raise ValueError("failed/mismatched local check")
        log = folder / row["log"]
        if (
            log.is_symlink()
            or not log.resolve().is_relative_to(folder)
            or digest(log) != row["log_sha256"]
        ):
            raise ValueError("unsafe/changed local log")
        text = log.read_text()
        header = encode(dict(command=expected["argv"]))
        if not text.startswith(header):
            raise ValueError("local log has another command")
    if receipt.get("artifacts") != artifact_hashes(receipt["profile"], folder):
        raise ValueError("changed local proof/city artifacts")
    return receipt


def release_receipts(folders, commit, root=ROOT):
    records = {}
    for folder in folders:
        row = verify(folder, root, commit, clean=True)
        if row["profile"] in records:
            raise ValueError("duplicate local release profile")
        records[row["profile"]] = row
    missing = RELEASE_PROFILES - records.keys()
    if missing:
        raise ValueError(
            "local release checks incomplete: " + ", ".join(sorted(missing))
        )
    return records
