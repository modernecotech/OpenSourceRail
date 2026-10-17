"""Execute and seal the bounded hierarchy pilot using actual common-store jobs."""

from hashlib import sha256
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys

import numpy

from . import agent_execution as workers, hierarchical_experiments as experiment
from engineering.design_engine.store import write_new

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / "tools/automation/fixtures/section-independent-acceptance.py"
CHECKOUT = [
    "engineering/generative_design",
    "engineering/design_engine",
    "engineering/industrialisation",
    "engineering/factory_examples/__init__.py",
    "engineering/factory_examples/models.py",
    "engineering/analysis/tests/test_mechanical_detail.py",
    "engineering/civil_exploration/examples/baghdad-qualification/qualification.json",
    "design/component-catalogue/src",
    "design/component-catalogue/catalog/buildable-trainset",
]
REGRESSION_ARGS = [
    "-m",
    "pytest",
    "engineering/analysis/tests/test_mechanical_detail.py",
    "-q",
    "-p",
    "no:cacheprovider",
]


def _sources():
    from . import hierarchical_review

    return [
        Path(__file__),
        Path(workers.__file__),
        Path(experiment.__file__),
        Path(hierarchical_review.__file__),
        FIXTURE,
    ]


def validate_software_policy(policy, source_sha256):
    """Bind trusted check labels to actual commands, independently of proposal data.

    Archived absolute tool paths remain provenance; they need not exist here.
    Tool versions are recorded, while the command semantics and fixture hash
    must match the declared acceptance specification.
    """
    commands = policy["commands"]
    expected_keys = {
        "checkout_paths",
        "allowed_paths",
        "acceptance_files",
        "commands",
        "timeout_seconds",
        "max_candidates",
        "max_log_bytes",
        "toolchain",
    }
    if set(policy) != expected_keys or len(commands) != 2:
        raise ValueError("software acceptance policy differs")
    fixture_name = FIXTURE.relative_to(ROOT).as_posix()
    if (
        not re.fullmatch(r"python(?:\d+(?:\.\d+)?)?", Path(commands[0][0]).name)
        or not re.fullmatch(
            r"[a-f0-9]{64}", policy["toolchain"].get("python_executable_sha256", "")
        )
        or commands[0][1:] != REGRESSION_ARGS
        or len(commands[1]) != 3
        or commands[1][0] != commands[0][0]
        or commands[1][2] != "{workspace}"
        or not commands[1][1].endswith("/" + fixture_name)
        or policy["acceptance_files"] != {commands[1][1]: source_sha256[fixture_name]}
        or policy["checkout_paths"] != CHECKOUT
        or policy["allowed_paths"]
        != ["engineering/generative_design/mechanical_detail.py"]
        or policy["timeout_seconds"] != 120
        or policy["max_candidates"] != 3
        or policy["max_log_bytes"] != 1024 * 1024
    ):
        raise ValueError("software acceptance policy differs")


def software_policy(root=ROOT):
    root = Path(root)
    fixture = root / FIXTURE.relative_to(ROOT)
    return dict(
        checkout_paths=list(CHECKOUT),
        allowed_paths=["engineering/generative_design/mechanical_detail.py"],
        acceptance_files={str(fixture): sha256(fixture.read_bytes()).hexdigest()},
        commands=[
            [
                sys.executable,
                *REGRESSION_ARGS,
            ],
            [sys.executable, str(fixture), "{workspace}"],
        ],
        timeout_seconds=120,
        max_candidates=3,
        max_log_bytes=1024 * 1024,
        toolchain=dict(
            python=sys.version,
            python_executable_sha256=sha256(
                Path(sys.executable).read_bytes()
            ).hexdigest(),
            numpy=numpy.__version__,
            git=subprocess.check_output(["git", "--version"], text=True).strip(),
        ),
    )


def software_decisions(execution, output):
    """Use actual test outcomes as counted, narrowly scoped reliability evidence."""
    output = Path(output)
    policy_hash = execution["policy_sha256"]
    context = experiment.comparison_context(
        "software-section-input-subsystem",
        "Reject nonphysical typed dimensions and preserve connected-frame calculations",
        [
            "Immutable independent section-input/closed-form fixture",
            "All existing connected mechanical detail regressions",
        ],
        [
            "Boolean/nonfinite/nonpositive/degenerate inputs",
            "Valid section closed forms",
            "Existing frame and beam regression cases",
        ],
    )
    candidates, evidence = {}, {}
    for row in execution["results"]:
        ident = row["proposal_id"]
        tools = row["tools"]
        complete = len(tools) == 2 and row["status"] == "completed"
        fixture_ok = len(tools) == 2 and tools[1]["state"] == "passed"
        ref = "execution/" + row["artifact_directory"] + "/evaluation.json"
        candidates[ident] = dict(
            id=ident,
            producer=row["role"],
            comparison_context=context,
            changed_paths=row["changed_paths"],
            source_revision=row["base_commit"],
            objectives={
                "observed_validation_defect": dict(
                    value=0 if fixture_ok else 1,
                    uncertainty=0,
                    units="ea",
                    state="counted",
                    basis="Binary failure of the declared independent validation fixture; not a population defect rate",
                    evidence_ref=ref,
                )
            },
            engineering_design_complete=False,
            manufacturing_release=False,
            physical_release=False,
        )
        checks = []
        for check_id, index in (
            ("original-regression-suite", 0),
            ("connected-frame-parent-regressions", 0),
            ("independent-section-input-and-closed-form", 1),
        ):
            tool = tools[index] if len(tools) > index else None
            checks.append(
                dict(
                    id=check_id,
                    state=(
                        "unknown"
                        if tool is None or tool["state"] == "inconclusive-timeout"
                        else "pass" if tool["state"] == "passed" else "fail"
                    ),
                    evidence_ref=ref + "#/tools/" + str(index),
                )
            )
        evidence[ident] = [
            experiment.evaluation(
                candidates[ident],
                worker="controller-independent-verification",
                checks=checks,
                execution_status=(
                    "completed"
                    if row["status"] in {"completed", "failed"} and tools
                    else row["status"]
                ),
            )
        ]
    baseline = candidates["unmodified-baseline"]
    adoption_policy = dict(
        mandatory_checks=["original-regression-suite"],
        independent_checks=["independent-section-input-and-closed-form"],
        parent_checks=["connected-frame-parent-regressions"],
        protected_paths=[
            "tools/automation/fixtures/",
            "engineering/analysis/tests/",
            "engineering/generative_design/hierarchical_",
            "engineering/design_engine/recursive_search.py",
        ],
        objective_axes=["observed_validation_defect"],
        execution_policy_sha256=policy_hash,
        scope="Existing connected-frame research regression suite; no whole-vehicle or operational software qualification",
    )
    decisions = [
        experiment.evaluate_promotion(
            baseline, c, adoption_policy, evidence=evidence[c["id"]]
        )
        for c in candidates.values()
    ]
    return dict(
        candidates=list(candidates.values()),
        evidence=evidence,
        policy=adoption_policy,
        decisions=decisions,
    )


def run(output, *, base_commit=None, concurrency=2):
    output = Path(output).resolve()
    if output.exists():
        raise ValueError("fresh hierarchy pilot output required")
    base = (
        base_commit
        or subprocess.check_output(
            ["git", "-C", str(ROOT), "rev-parse", "HEAD"], text=True
        ).strip()
    )
    report = experiment.run_pilot(output)
    proposals = [
        {k: p[k] for k in ("id", "role", "base_commit", "patch", "allowed_paths")}
        for p in experiment.software_proposals(base)
    ]
    execution = workers.execute_proposals(
        ROOT,
        output / "execution",
        proposals,
        software_policy(),
        concurrency=concurrency,
    )
    software = software_decisions(execution, output)
    report["software"] = software
    report["software_execution"] = (
        "Actual isolated Git worktrees and common-store attempts; no LLM service invoked"
    )
    report["promotions"] = software["decisions"]
    report["execution_report"] = "execution/execution.json"
    report["source_sha256"] = {
        str(p.relative_to(ROOT)): sha256(p.read_bytes()).hexdigest()
        for p in [
            *_sources(),
        ]
    }
    (output / "report.json").write_text(
        json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n"
    )
    from .hierarchical_review import render

    (output / "index.html").write_text(render(report, execution))
    _seal(output)
    verify(output)
    return report


def _files(output):
    return {
        p.relative_to(output).as_posix(): sha256(p.read_bytes()).hexdigest()
        for p in sorted(output.rglob("*"))
        if p.is_file() and p != output / "receipt.json"
    }


def _seal(output):
    write_new(
        output / "receipt.json",
        dict(
            schema="osr-hierarchy-pilot-receipt/1",
            artifacts=_files(output),
            physical_release=False,
        ),
    )


def verify(output, *, current=True):
    output = Path(output).resolve()
    receipt = json.loads((output / "receipt.json").read_text())
    if (
        any(p.is_symlink() for p in output.rglob("*"))
        or receipt["physical_release"] is not False
        or receipt["artifacts"] != _files(output)
    ):
        raise ValueError("changed or missing hierarchy pilot artifact")
    report = json.loads((output / "report.json").read_text())
    for flag in (
        "physical_release",
        "manufacturing_release",
        "engineering_design_complete",
    ):
        if report[flag] is not False:
            raise ValueError("hierarchy pilot cannot claim release")
    workers.verify_execution(output / "execution")
    execution = json.loads((output / "execution/execution.json").read_text())
    expected_sources = {str(p.relative_to(ROOT)) for p in _sources()}
    if set(report["source_sha256"]) != expected_sources:
        raise ValueError("hierarchy source membership differs")
    execution_policy = json.loads((output / "execution/policy.json").read_text())
    validate_software_policy(execution_policy, report["source_sha256"])
    software = software_decisions(execution, output)
    if software != report["software"] or report["promotions"] != software["decisions"]:
        raise ValueError("changed experimental adoption decision")
    experiment.validate_plan(report["plan"])
    if current:
        if (
            execution_policy["toolchain"]["python_executable_sha256"]
            != sha256(Path(sys.executable).read_bytes()).hexdigest()
        ):
            raise ValueError("changed Python execution toolchain")
        if any(
            sha256((ROOT / p).read_bytes()).hexdigest() != digest
            for p, digest in report["source_sha256"].items()
        ):
            raise ValueError("changed hierarchy pilot sources")
        if (
            report["plan"] != experiment.plan()
            or report["engineering"] != experiment.engineering_pilot()
        ):
            raise ValueError("hierarchy numerical evidence replay differs")
    return dict(
        verified=True,
        current_sources_checked=current,
        work_packages=report["plan"]["work_package_count"],
        software_jobs=len(execution["results"]),
        physical_release=False,
    )


def publish(source, destination):
    source, destination = Path(source), Path(destination)
    verify(source)
    if destination.exists():
        raise ValueError("fresh publication destination required")
    shutil.copytree(source, destination)
    return verify(destination)
