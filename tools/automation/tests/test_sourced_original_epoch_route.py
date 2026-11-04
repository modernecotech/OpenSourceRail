"""Keep original sourced evidence bound to its original producer, not HEAD."""
from pathlib import Path
import re

import pytest


ROOT = Path(__file__).resolve().parents[3]
WORKFLOW = ROOT / '.github/workflows/sourced-hardware.yml'
REPRODUCTION_WORKFLOW = ROOT / '.github/workflows/reproduce-sourced-geometry.yml'
COMMIT = '32263d93a034bb12edaad395552e37671aef1b23'


def validate_original_routes(text):
    jobs = text.split('\njobs:\n', 1)[1]
    matches = list(re.finditer(r'^  ([a-z][a-z0-9-]*):\n', jobs, re.M))
    blocks = {match[1]: jobs[match.end():matches[i+1].start() if i+1 < len(matches) else len(jobs)]
              for i, match in enumerate(matches)}
    for name in ('semantic-replay', 'geometry-and-recorded-methods'):
        block = blocks[name]
        steps = re.split(r'(?=^      - (?:name|uses|run):)', block, flags=re.M)
        prepared = [s for s in steps if s.startswith('      - name: Prepare the authenticated original sourced producer epoch\n')]
        assert len(prepared) == 1
        preparation = prepared[0]
        for line in (
            'git fetch --no-tags --depth=1 origin ' + COMMIT,
            'git worktree add --detach --no-checkout "$original_root" ' + COMMIT,
            'git -C "$original_root" sparse-checkout set --cone engineering campaigns services/integration/osr_integration tools/automation docs/design-engine/ferrite-maglev/comfort-design docs/design-engine/digital-twin',
            'git -C "$original_root" checkout --detach ' + COMMIT,
            'test "$(git -C "$original_root" rev-parse HEAD)" = ' + COMMIT,
            'echo "OSR_SOURCED_ORIGINAL_ROOT=$original_root" >> "$GITHUB_ENV"',
        ):
            assert line in preparation
        consumer_name = ('Rebuild all five registries and actually replay every coupled case'
                         if name == 'semantic-replay' else 'Reopen all five full-train occurrence inventories')
        consumers = [s for s in steps if s.startswith('      - name: ' + consumer_name + '\n')]
        assert len(consumers) == 1
        consumer = consumers[0]
        assert steps.index(preparation) < steps.index(consumer)
        for step in (preparation, consumer):
            assert not re.search(r'^        (?:if|continue-on-error|shell):', step, re.M)
            assert 'set +e' not in step and '|| true' not in step
        if name == 'semantic-replay':
            assert 'tools/automation/sourced-verify.py docs/design-engine/sourced-case --root "$OSR_SOURCED_ORIGINAL_ROOT" --workers 3' in consumer
            assert '--audit "$GITHUB_WORKSPACE/build/sourced-replay-audit"' in consumer
        else:
            assert 'cd -- "$OSR_SOURCED_ORIGINAL_ROOT"' in consumer
            assert '"$GITHUB_WORKSPACE/.venv/bin/python" -m engineering.sourced_case.cli verify-geometry --output "$GITHUB_WORKSPACE/docs/design-engine/sourced-case"' in consumer


def test_original_routes_verify_current_evidence_with_pinned_producers():
    validate_original_routes(WORKFLOW.read_text())


@pytest.mark.parametrize('before,after', [
    (' --root "$OSR_SOURCED_ORIGINAL_ROOT"', ''),
    (COMMIT, 'HEAD'),
    ('git fetch --no-tags --depth=1 origin ' + COMMIT, 'true'),
    ('cd -- "$OSR_SOURCED_ORIGINAL_ROOT"', 'cd -- "$GITHUB_WORKSPACE"'),
    ('--output "$GITHUB_WORKSPACE/docs/design-engine/sourced-case"', '--output "$OSR_SOURCED_ORIGINAL_ROOT/docs/design-engine/sourced-case"'),
    ('test "$(git -C "$original_root" rev-parse HEAD)" = ' + COMMIT, 'true'),
    ('--workers 3', '--workers 3 || true'),
])
def test_original_route_rejects_source_or_payload_substitution(before, after):
    text = WORKFLOW.read_text()
    assert before in text
    with pytest.raises(AssertionError):
        validate_original_routes(text.replace(before, after))


def validate_original_reproduction(text):
    steps = re.split(r'(?=^      - (?:name|uses|run):)', text, flags=re.M)
    prepare = next(s for s in steps if s.startswith('      - name: Prepare the authenticated original sourced producer epoch\n'))
    consumer = next(s for s in steps if s.startswith('      - name: Export and reopen all five source-bound vehicle IFCs\n'))
    assert steps.index(prepare) < steps.index(consumer)
    for line in (
        'git fetch --no-tags --depth=1 origin ' + COMMIT,
        'git worktree add --detach --no-checkout "$original_root" ' + COMMIT,
        'git -C "$original_root" checkout --detach ' + COMMIT,
        'test "$(git -C "$original_root" rev-parse HEAD)" = ' + COMMIT,
        'echo "OSR_SOURCED_ORIGINAL_ROOT=$original_root" >> "$GITHUB_ENV"',
    ):
        assert line in prepare
    for step in (prepare, consumer):
        assert not re.search(r'^        (?:if|continue-on-error|shell):', step, re.M)
        assert 'set +e' not in step and '|| true' not in step
    for line in (
        "workspace = Path(os.environ['GITHUB_WORKSPACE'])",
        "root = Path(os.environ['OSR_SOURCED_ORIGINAL_ROOT'])",
        'coordinator = archive._executor(root).modules(root)',
        "original = workspace / 'docs/design-engine/sourced-case'",
        "manifest['source_sha256'] != coordinator.sources(root)",
        "manifest['files_sha256'] != {name:coordinator.digest(original/name) for name in ('sourced-cell.tar.gz','summary.json')}",
        "archive._extract(original / 'sourced-cell.tar.gz', state)",
        "output = workspace / 'build/sourced-geometry-reproduction'",
        'publication = geometry.publish(state, output, root=root)',
        "coordinator.sources(root) != manifest['source_sha256']",
        "coordinator.read(original/'manifest.json') != manifest",
    ):
        assert line in consumer
    assert 'tools/automation/tests/test_sourced_original_epoch_route.py' in text


def test_reproduction_uses_original_input_epoch_and_separate_output():
    validate_original_reproduction(REPRODUCTION_WORKFLOW.read_text())


@pytest.mark.parametrize('before,after', [
    (COMMIT, 'HEAD'),
    ('coordinator = archive._executor(root).modules(root)', 'from engineering.sourced_case import coordinator'),
    ("root = Path(os.environ['OSR_SOURCED_ORIGINAL_ROOT'])", 'root = workspace'),
    ("manifest['source_sha256'] != coordinator.sources(root)", 'False'),
    ("original = workspace / 'docs/design-engine/sourced-case'", "original = root / 'docs/design-engine/sourced-case'"),
    ("output = workspace / 'build/sourced-geometry-reproduction'", 'output = original'),
    ("coordinator.read(original/'manifest.json') != manifest", 'False'),
])
def test_reproduction_rejects_mixed_sources_or_overwritten_original(before, after):
    text = REPRODUCTION_WORKFLOW.read_text()
    assert before in text
    with pytest.raises(AssertionError):
        validate_original_reproduction(text.replace(before, after))
