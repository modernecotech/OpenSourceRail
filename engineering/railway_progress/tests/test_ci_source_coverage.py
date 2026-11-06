"""Changes to every published numerical dependency must trigger its CI gate."""
import fnmatch
import json

from engineering.railway_progress import ROOT
from engineering.railway_progress.coordinator import sources


def test_push_and_pull_request_cover_the_actual_numerical_source_inventory():
    workflow = (ROOT / '.github/workflows/continuing-cell.yml').read_text()
    # The two flow-style path arrays are JSON-compatible; avoid adding a YAML
    # runtime dependency to the numerical test environment.
    filters = [json.loads(line.split(':', 1)[1])
               for line in workflow.splitlines() if line.strip().startswith('paths: [')]
    assert len(filters) == 2, 'Expected push and pull_request path filters'
    for patterns in filters:
        missing = [name for name in sources()
                   if not any(fnmatch.fnmatchcase(name, pattern) for pattern in patterns)]
        assert not missing, 'Numerical source changes would skip verification: ' + ', '.join(missing)


def test_verification_log_pipeline_keeps_nonzero_exit_status():
    workflow = (ROOT / '.github/workflows/continuing-cell.yml').read_text()
    step = workflow.split('name: Reconstruct all physical candidates, trajectories, production and civil loads', 1)[1].split('\n      - ', 1)[0]
    # Explicit GitHub Bash uses -e -o pipefail, so tee cannot hide a failed gate.
    assert 'shell: bash' in step
    assert 'continue-on-error' not in step
