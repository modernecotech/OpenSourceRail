"""Keep the resource-contract test in the bounded release CI lane."""

from ast import literal_eval
from fnmatch import fnmatchcase
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
STORAGE_TEST = "engineering/development_baseline/tests/test_performance_storage.py"
SOURCE_CONTROL = "engineering/development_baseline/vehicle_cost.py"
HEAVY_WORKFLOWS = (
    ".github/workflows/v06-software-journey.yml",
    ".github/workflows/digital-twin.yml",
    ".github/workflows/frame-refinement.yml",
    ".github/workflows/reference-cell.yml",
    ".github/workflows/engineering-closure.yml",
    ".github/workflows/reconciled-pilot.yml",
    ".github/workflows/development-baseline.yml",
    ".github/workflows/shared-software.yml",
)


def _event_paths(workflow: Path, event: str) -> list[str]:
    lines = workflow.read_text().splitlines()
    start = next(i for i, line in enumerate(lines) if line == f"  {event}:")
    end = next((i for i in range(start + 1, len(lines))
                if ((lines[i].startswith("  ") and not lines[i].startswith("    "))
                    or lines[i] == "jobs:")), len(lines))
    paths_line = next((i for i in range(start + 1, end)
                       if lines[i].startswith("    paths:")), None)
    assert paths_line is not None, f"{workflow} {event} has no paths filter"
    inline = lines[paths_line].split("paths:", 1)[1].strip()
    if inline:
        return list(literal_eval(inline))

    patterns = []
    for line in lines[paths_line + 1:end]:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if not line.startswith("      - "):
            break
        patterns.append(literal_eval(line.split("-", 1)[1].strip()))
    return patterns


def _matches(path: str, patterns: list[str]) -> bool:
    included = False
    for pattern in patterns:
        if pattern.startswith("!"):
            if fnmatchcase(path, pattern[1:]):
                included = False
        elif fnmatchcase(path, pattern):
            included = True
    return included


def test_storage_resource_contract_runs_only_in_bounded_fast_lane():
    for relative in HEAVY_WORKFLOWS:
        workflow = ROOT / relative
        for event in ("push", "pull_request"):
            patterns = _event_paths(workflow, event)
            assert patterns[-1] == f"!{STORAGE_TEST}", f"{relative} exclusion must remain last"
            assert not _matches(STORAGE_TEST, patterns), f"{relative} still selects the storage test"
            assert _matches(SOURCE_CONTROL, patterns), f"{relative} lost its source-change trigger"

    release = ROOT / ".github/workflows/v06-software-release.yml"
    for event in ("push", "pull_request"):
        assert _matches(STORAGE_TEST, _event_paths(release, event))

    smoke_tests = (ROOT / ".github/release-smoke-tests.txt").read_text().splitlines()
    assert STORAGE_TEST in smoke_tests
    assert ".github/tests/test_workflow_path_filters.py" in smoke_tests
    workflow_text = release.read_text()
    assert "/.github/tests/test_workflow_path_filters.py" in workflow_text
    for relative in (*HEAVY_WORKFLOWS, ".github/workflows/v06-software-release.yml"):
        assert f"/{relative}" in workflow_text, f"fast lane sparse checkout omits {relative}"


def test_every_selected_test_is_available_in_fast_lane_sparse_checkout():
    workflow = ROOT / ".github/workflows/v06-software-release.yml"
    lines = workflow.read_text().splitlines()
    start = lines.index("          sparse-checkout: |")
    patterns = []
    for line in lines[start + 1:]:
        if not line.startswith("            "):
            break
        patterns.append(line.strip().lstrip("/"))
    selected = [line.strip() for line in
                (ROOT / ".github/release-smoke-tests.txt").read_text().splitlines()
                if line.strip() and not line.lstrip().startswith("#")]
    missing = [path for path in selected if not _matches(path, patterns)]
    assert not missing, f"Selected tests missing from sparse checkout: {missing}"
    for event in ("push", "pull_request"):
        for path in ("tests/test_corridor_revision.py", "tests/test_corridor_revision_api.py",
                     "engineering/outline/corridor_revision.py", "engineering/outline/city_jobs.py"):
            assert _matches(path, _event_paths(workflow, event))
