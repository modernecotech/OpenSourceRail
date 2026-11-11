#!/usr/bin/env python3
"""Guard CI source routing: frozen v0.5 replay and current shared regressions."""
from copy import deepcopy
import ast
from hashlib import sha256
from fnmatch import fnmatchcase
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[3]
HISTORICAL_WORKFLOW = ROOT / '.github/workflows/historical-v05.yml'
SHARED_WORKFLOW = ROOT / '.github/workflows/shared-software.yml'
CURRENT_WORKFLOW = ROOT / '.github/workflows/development-baseline.yml'
SOURCED_WORKFLOW = ROOT / '.github/workflows/sourced-hardware.yml'
SOURCED_GEOMETRY_WORKFLOW = ROOT / '.github/workflows/reproduce-sourced-geometry.yml'
DIGITAL_TWIN_WORKFLOW = ROOT / '.github/workflows/digital-twin.yml'
RETAINED_PERIODIC_HELPER = ROOT / 'engineering/design_search/retained_periodic_thermal.py'
ARCHIVE = ROOT / 'docs/archives/v0.5-maglev/manifest.json'
OLD_COMMIT = 'dad8c4bedb2361d3e621e9def312273167279027'
EXTRA_COMMIT = '5cd6b8ff9b2fdf3c705f0d68073543c58e6dec76'
OLD_ARCHIVE_ID = '478479a93642c464cc2be318bbc5b45b9c5c3fec2e9cecb02318d53bd4fb568e'
EXTRA_ARCHIVE_ID = 'd2f4511f180592083945bb993658353218b9efcf91d0dd3f21d02e58399967b9'
EXTRA_PINS_ID = '91d8be8f7893aea692e90683c214bbda0d35c4dbe1a652c7cb8908e3d3a4f050'
OLD_ARCHIVE_ARGS = ('--archive-directory docs/design-engine/retained-battery-source-epoch/archive '
                    '--pins docs/design-engine/retained-battery-source-epoch/pins.json')
EXTRA_ARCHIVE_ARGS = ('--archive-directory docs/design-engine/retained-service-energy-extra/original/worker-v7/archive '
                      '--pins docs/design-engine/retained-service-energy-extra/original/worker-v7/pins.json')
OLD_MATERIALIZE = ('.venv/bin/python -m engineering.design_search.retained_packet_materialize --git-repo . '
                   '--output "$retained_packet_parent/packets" ' + OLD_ARCHIVE_ARGS +
                   ' --expected-commit ' + OLD_COMMIT + ' --expected-archive-id ' + OLD_ARCHIVE_ID)
OLD_VERIFY = ('.venv/bin/python -m engineering.design_search.retained_source_epoch verify '
              '--root "$retained_packet_parent/packets/root" ' + OLD_ARCHIVE_ARGS +
              ' --expected-archive-id ' + OLD_ARCHIVE_ID)
EXTRA_MATERIALIZE = ('.venv/bin/python -m engineering.design_search.retained_service_energy_materialize materialize '
                     '--git-repo . --output "$retained_extra_parent/packets" ' + EXTRA_ARCHIVE_ARGS +
                     ' --expected-commit ' + EXTRA_COMMIT + ' --expected-pins-id ' + EXTRA_PINS_ID +
                     ' --expected-archive-id ' + EXTRA_ARCHIVE_ID)
EXTRA_VERIFY = ('.venv/bin/python -m engineering.design_search.retained_service_energy_epoch verify '
                '--root "$retained_extra_parent/packets/root" ' + EXTRA_ARCHIVE_ARGS +
                ' --expected-pins-id ' + EXTRA_PINS_ID + ' --expected-archive-id ' + EXTRA_ARCHIVE_ID)
OLD_SCRIPT = [
    '.venv/bin/python -m pytest -q --import-mode=importlib engineering/design_search/tests/test_retained_packet_materialize.py',
    'git fetch --no-tags --depth=1 origin '+OLD_COMMIT,
    'retained_packet_parent=$(mktemp -d "$RUNNER_TEMP/osr-retained-packets.XXXXXX")',
    'ulimit -v 1048576', OLD_MATERIALIZE, OLD_VERIFY,
]
EXTRA_SCRIPT = [
    '.venv/bin/python -m pytest -q --import-mode=importlib engineering/design_search/tests/test_retained_service_energy_epoch.py engineering/design_search/tests/test_retained_service_energy_handoff.py engineering/design_search/tests/test_retained_service_energy_materialize.py engineering/design_search/tests/test_retained_service_energy_materialize_handoff.py',
    'git fetch --no-tags --depth=1 origin '+EXTRA_COMMIT,
    'git fetch --no-tags --depth=1 origin '+OLD_COMMIT,
    'git fetch --no-tags --depth=1 origin be03a8436a7b5b307840514e05146f98b3ee2574',
    '.venv/bin/python -m pytest -q --import-mode=importlib engineering/design_search/tests/test_service_energy_migration_inventory.py',
    'ulimit -v 1048576',
    'retained_extra_parent=$(mktemp -d "$RUNNER_TEMP/osr-service-energy.XXXXXX")',
    EXTRA_MATERIALIZE, EXTRA_VERIFY,
]


def job_blocks(text):
    # Read only top-level job blocks, retaining nested step text unchanged.
    jobs = text.split('\njobs:\n', 1)[1]
    matches = list(re.finditer(r'^  ([a-z][a-z0-9-]*):\n', jobs, re.M))
    return {m[1]: jobs[m.end():matches[i+1].start() if i+1 < len(matches) else len(jobs)]
            for i, m in enumerate(matches)}


def path_filters_include(path, patterns):
    included = False
    for pattern in patterns:
        excluded = pattern.startswith('!')
        if fnmatchcase(path, pattern[1:] if excluded else pattern):
            included = not excluded
    return included


def twin_storage_steps(text):
    """Require disk preparation while preserving the pinned CAD verification."""
    block = job_blocks(text)['contracts-and-semantic-replay']
    assert re.search(r'^    runs-on: ubuntu-24\.04$', block, re.M)
    steps = re.split(r'(?=^      - (?:name|uses|run):)', block, flags=re.M)
    def one(header):
        matches = [step for step in steps if step.startswith('      - '+header+'\n')]
        assert len(matches) == 1, header
        assert not re.search(r'^        (?:if|continue-on-error|shell):', matches[0], re.M)
        assert 'set +e' not in matches[0] and '|| true' not in matches[0]
        return matches[0]
    cleanup = one('name: Reserve disk on the disposable GitHub-hosted runner')
    checkout = one('uses: actions/checkout@v4')
    install = one('name: Install the pinned headless CAD tool for actual file reopening')
    verify = one('name: Verify current semantic packets and reopen published IFC, CAD and STEP')
    assert steps.index(cleanup) < steps.index(checkout) < steps.index(install) < steps.index(verify)
    assert re.search(r'^        run: \|$', cleanup, re.M) and re.search(r'^        run: \|$', install, re.M)
    active_cleanup = [line.strip() for line in cleanup.splitlines() if not line.lstrip().startswith('#')]
    for line in ('test "${RUNNER_ENVIRONMENT:-}" = github-hosted', 'test "${RUNNER_OS:-}" = Linux',
                 "for path in map(Path, ('/usr/local/lib/android', '/opt/ghc', '/usr/share/dotnet')):",
                 'if path.is_symlink():', 'shutil.rmtree(path)',
                 "for path, required in ((workspace, 16 * 1024**3), (Path(os.environ['RUNNER_TEMP']), 2 * 1024**3)):",
                 'if free < required:'):
        assert line in active_cleanup, line
    assert cleanup.count('shutil.rmtree(') == 1
    expected = ('required = 8 * 1024**3', 'sudo apt-get update', 'required = 6 * 1024**3',
                '.venv/bin/python tools/automation/download-pinned-tool.py freecad --output build/twin-tools/freecad.AppImage',
                '.venv/bin/python tools/automation/install-historical-freecad.py --archive build/twin-tools/freecad.AppImage --output build/twin-tools/freecad',
                'test -s build/twin-tools/freecad/install.json', 'test -x build/twin-tools/freecad/bin/FreeCADCmd',
                "archive = Path('build/twin-tools/freecad.AppImage')", 'archive.unlink()',
                'echo "$PWD/build/twin-tools/freecad/bin" >> "$GITHUB_PATH"')
    lines = [line.strip() for line in install.splitlines()]
    assert all(line in lines for line in expected)
    positions = [lines.index(line) for line in expected]
    assert positions == sorted(positions) and install.count('archive.unlink()') == 1
    assert lines.count('if free < required:') == 2
    assert re.search(r'^        run: \./osr-twin verify-publication$', verify, re.M)
    return cleanup, install


def twin_python_blocks(step):
    """Extract the actual Python here-documents from one GitHub run step."""
    return [re.sub(r'^ {10}', '', body, flags=re.M) for body in
            re.findall(r"^          (?:sudo )?/usr/bin/python3 - <<'PYCODE'\n(.*?)^          PYCODE$",
                       step, re.M | re.S)]


def isolated_rust_path_script(block, prefix, *, target=False):
    """Validate the fail-fast environment step and return its executable shell."""
    job_env = block.split('    steps:\n', 1)[0]
    assert not re.search(r'\$\{\{\s*runner\.', job_env, re.I), 'runner context is unavailable in job env'
    header = '      - name: Initialize isolated Rust paths\n'
    action = '      - uses: dtolnay/rust-toolchain@1.92.0\n'
    assert block.count(header) == block.count(action) == 1
    assert block.index(header) < block.index(action)
    step = block.split(header, 1)[1].split('      - ', 1)[0]
    assert not re.search(r'^        (?:if|continue-on-error|shell):', step, re.M)
    match = re.fullmatch(r'        run: \|\n((?: {10}[^\n]*\n)+)', step)
    assert match, 'Rust path initialization must be an unconditional shell step'
    lines = [line[10:] for line in match.group(1).splitlines()]
    expected = ['test -n "${RUNNER_TEMP:-}"', 'test -n "${GITHUB_ENV:-}"',
        f'printf \'RUSTUP_HOME=%s\\n\' "$RUNNER_TEMP/osr-{prefix}-rustup" >> "$GITHUB_ENV"',
        f'printf \'CARGO_HOME=%s\\n\' "$RUNNER_TEMP/osr-{prefix}-cargo" >> "$GITHUB_ENV"']
    if target:
        expected.append(f'printf \'CARGO_TARGET_DIR=%s\\n\' "$RUNNER_TEMP/osr-{prefix}-target" >> "$GITHUB_ENV"')
    assert lines == expected
    return '\n'.join(lines) + '\n'


def validate_native_control_toolchain(text):
    """Keep native Rust control tests on a fresh pinned toolchain, without skips."""
    native = job_blocks(text)['native-methods']
    for line in (
        '      RUSTUP_TOOLCHAIN: "1.92.0"',
        '      CARGO_BUILD_JOBS: "2"',
    ):
        assert re.search(r'^'+re.escape(line)+r'$', native, re.M), line
    isolated_rust_path_script(native, 'native', target=True)
    action='      - uses: dtolnay/rust-toolchain@1.92.0\n'
    header='      - name: Verify isolated Rust toolchain\n'
    cargo='      - run: cargo test --locked -p osr-atp -p osr-interlocking -p osr-door-control -p osr-tcms -p osr-station-scada\n'
    assert native.count(action)==native.count(header)==native.count(cargo)==1
    block=native.split(header,1)[1].split('      - ',1)[0]
    assert re.search(r'^        run: \|$',block,re.M)
    assert not re.search(r'^        (?:if|continue-on-error|shell):',block,re.M)
    lines=[line.strip() for line in block.splitlines() if not line.lstrip().startswith('#')]
    assert 'test "$(rustc --version --verbose | sed -n \'s/^release: //p\')" = 1.92.0' in lines
    assert 'test "$(cargo --version | awk \'{print $2}\')" = 1.92.0' in lines
    assert native.index(action)<native.index(header)<native.index(cargo)
    assert cargo+'      - uses: actions/upload-artifact@v4\n' in native


def validate_native_canonical_job(text):
    """The optional ABI matrix must actually build and execute both backends."""
    jobs=job_blocks(text)
    assert 'native-canonical-parity' in jobs
    block=jobs['native-canonical-parity']
    for required in ('python: ["3.12", "3.13"]', 'timeout-minutes: 15',
            'RUSTUP_TOOLCHAIN: "1.92.0"', 'CARGO_BUILD_JOBS: "2"',
            'OSR_TEST_NATIVE_CANONICAL: "1"', 'uses: dtolnay/rust-toolchain@1.92.0'):
        assert required in block, required
    isolated_rust_path_script(block, 'canonical')
    assert ('      - uses: dtolnay/rust-toolchain@1.92.0\n'
            '        with:\n          components: clippy\n') in block
    build='      - name: Build explicit source-bound kernel and interpreter-specific extension\n'
    verify='      - name: Require exact canonical parity and unchanged campaign results\n'
    assert block.count(build)==block.count(verify)==1
    assert block.index(build)<block.index(verify)
    preparation=block.split(build,1)[1].split(verify,1)[0]
    assert '          python -m engineering.design_search.native_search build\n' in preparation
    assert '          python -m engineering.design_search.native_canonical build\n' in preparation
    command='        run: python -m pytest -q --import-mode=importlib engineering/design_search/tests/test_native_canonical.py engineering/design_search/tests/test_campaign_canonical_backend.py engineering/design_search/tests/test_native_sealing.py engineering/design_search/tests/test_interface_validation_performance.py\n'
    assert block.count(command)==1
    assert '        run: cargo clippy --locked -p osr-design-search --lib --features python-extension -- -D warnings\n' in block
    assert not re.search(r'^\s+(?:-\s+)?(?:if|continue-on-error|ref):',block,re.M)


def active_run_line(block, command):
    """Find a command on an uncommented shell line in a YAML run block."""
    runs = re.findall(r'^        run: \|\n((?: {10}[^\n]*(?:\n|$))*)', block, re.M)
    lines = (line.split('#', 1)[0].strip() for run in runs for line in run.splitlines())
    return any(re.match(r'^\.venv(?:-search)?/bin/python\s+(?:-m\s+|tools/automation/sourced-archive\.py\s+)', line)
               and command in line for line in lines)


def validate_retained_periodic_route(current):
    """Require current research tests plus pinned original-source thermal replay."""
    header = '      - name: Material-distribution experiments and disjoint cost accounting\n'
    current_header = '      - name: Current civil, material, lifecycle and numerical-kernel mathematics\n'
    current_methods = current_header in current
    if current_methods:
        header = current_header
    assert current.count(header) == 1
    step = current.split(header, 1)[1].split('      - ', 1)[0]
    assert not re.search(r'^        (?:if|continue-on-error|shell|working-directory):', step, re.M)
    match = re.fullmatch(r'        run: \|\n((?: {10}[^\n]*\n)+)', step)
    assert match, 'Retained periodic checks must remain in the mandatory fail-fast run step'
    lines = [line[10:] for line in match.group(1).splitlines()]
    assert not any(re.search(r'(^|[;\s])(?:set\s+\+e|exit\s+0)(?:[;\s]|$)', line)
                   for line in lines), 'Do not bypass the mandatory retained checks'
    required = [
        '.venv/bin/python -m pytest -q --import-mode=importlib engineering/design_search/tests/test_retained_source_epoch.py',
        '.venv/bin/python -m pytest -q --import-mode=importlib engineering/design_search/tests/test_periodic_thermal_research.py',
        'git fetch --no-tags --depth=1 origin ' + EXTRA_COMMIT,
        'OSR_TEST_RETAINED_PERIODIC=1 .venv/bin/python -m pytest -q --import-mode=importlib engineering/design_search/tests/test_retained_periodic_thermal.py',
        '.venv/bin/python -m engineering.design_search.retained_periodic_thermal verify',
        'retained_periodic_parent=$(mktemp -d "$RUNNER_TEMP/osr-periodic-thermal.XXXXXX")',
        '.venv/bin/python -m engineering.design_search.retained_periodic_thermal replay --output "$retained_periodic_parent/context"',
    ]
    if current_methods:
        required[:2] = ['.venv/bin/python -m pytest -q --import-mode=importlib engineering/design_search/tests/test_retained_source_epoch.py engineering/design_search/tests/test_periodic_thermal_research.py']
    assert lines[-len(required):] == required, 'Pinned thermal tests and replay must execute in order'
    job_conditions = re.findall(r'^    if: (.+)$', current, re.M)
    if current_methods:
        assert job_conditions == []
    else:
        assert job_conditions == ["(github.event_name == 'workflow_dispatch' && inputs.retired_methods) || github.event_name == 'schedule'"]


def validate_retired_reference_job(block):
    """All 36 original commands must execute on the exact original checkout."""
    commit = '3bf38a501d09fa3a3c2dd6f4731be11828d04f55'
    assert block.count('uses: actions/checkout@v4') == 1
    assert re.findall(r'^          ref: (.+)$', block, re.M) == [commit]
    checkout = block.split('uses: actions/checkout@v4', 1)[1].split('      - ', 1)[0]
    assert not re.search(r'^\s+path:', checkout, re.M)
    assert not re.search(r'^\s+(?:- )?(?:working-directory|continue-on-error):', block, re.M)
    assert re.findall(r'^    if: (.+)$', block, re.M) == [
        "(github.event_name == 'workflow_dispatch' && inputs.retired_methods) || github.event_name == 'schedule'"]
    assert re.findall(r'^        if: (.+)$', block, re.M) == ['always()']
    commands = []
    for step in re.split(r'(?=^      - )', block, flags=re.M):
        match = re.search(r'^(?:      - |        )run: (.*)$', step, re.M)
        if match:
            commands.append('\n'.join(line[10:] for line in step[match.end()+1:].splitlines()
                if line.startswith('          ')) if match[1] == '|' else match[1])
    assert len(commands) == 37
    assert commands[0] == 'test "$(git rev-parse HEAD)" = ' + commit
    # Canonical ordered command list extracted from the 3bf workflow, excluding
    # only the added checkout-proof command. No stored numerical hashes change.
    assert sha256(json.dumps(commands[1:], separators=(',', ':')).encode()).hexdigest() == \
        'c1d8bedcf7cbb4ed46ba3dcdec9c31413d799e56b053521de4bbe8ceab54505b'


def validate_retained_periodic_test_contract(text):
    """The isolated replay must execute both original test modules and verifier."""
    tree = ast.parse(text)
    assignments = {target.id: node.value for node in tree.body if isinstance(node, ast.Assign)
                   for target in node.targets if isinstance(target, ast.Name)}
    tests = ('engineering/design_search/tests/test_periodic_thermal_research.py',
             'engineering/design_search/tests/test_periodic_thermal_publication.py')
    assert ast.literal_eval(assignments['TESTS']) == tests
    bootstrap = ast.literal_eval(assignments['BOOTSTRAP'])
    child = ast.parse(bootstrap)
    pytest_calls = [node for node in ast.walk(child) if isinstance(node, ast.Call)
                    and isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Name)
                    and node.func.value.id == 'pytest' and node.func.attr == 'main']
    assert len(pytest_calls) == 1
    assert len(pytest_calls[0].args) == 1 and not pytest_calls[0].keywords
    assert ast.literal_eval(pytest_calls[0].args[0]) == ['-q', '-p', 'no:cacheprovider',
        '--import-mode=importlib', *tests]
    guard = ast.dump(ast.parse('if code: raise SystemExit(code)').body[0], include_attributes=False)
    assert any(ast.dump(node, include_attributes=False) == guard for node in child.body)
    verifies = [node for node in ast.walk(child) if isinstance(node, ast.Call)
                and isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Name)
                and node.func.value.id == 'publication' and node.func.attr == 'verify']
    assert len(verifies) == 1 and not verifies[0].args
    expected = {'expected_manifest_id': 'original_manifest_id', 'expected_handoff_id': 'worker_handoff_id',
                'expected_request_id': 'request_id', 'expected_evaluation_id': 'evaluation_id'}
    assert {arg.arg for arg in verifies[0].keywords} == expected.keys()
    for arg in verifies[0].keywords:
        assert isinstance(arg.value, ast.Subscript) and isinstance(arg.value.value, ast.Name)
        assert arg.value.value.id == 'pins' and ast.literal_eval(arg.value.slice) == expected[arg.arg]


def checked_historical_route(block, *, parent, prefix, commit, materialize, verify, expected_script):
    """Require one active shell block to materialize before its exact verifier."""
    assert not re.search(r'^\s+(shell|defaults):', block, re.M), 'Use the runner default fail-fast shell'
    runs = re.findall(r'^        run: \|\n((?: {10}[^\n]*(?:\n|$))*)', block, re.M)
    scripts = [[line.split('#', 1)[0].strip() for line in run.splitlines()] for run in runs]
    matches = [lines for lines in scripts if materialize in lines or verify in lines]
    assert len(matches) == 1
    lines = matches[0]
    assert lines == expected_script, 'Historical verifier shell block must match the complete guarded sequence'
    init = parent + '=$(mktemp -d "$RUNNER_TEMP/' + prefix + '.XXXXXX")'
    fetch = 'git fetch --no-tags --depth=1 origin ' + commit
    for command in (init, fetch, materialize, verify):assert lines.count(command) == 1, command
    assert lines.index(fetch) < lines.index(init) < lines.index(materialize) < lines.index(verify)
    assert sum(line.startswith(parent+'=') for line in lines) == 1
    assert not any(line == 'set +e' or line.startswith('set +e ') for line in lines)
    return lines


def validate_current_sourced_archive_consumers(sourced_text, geometry_text):
    """Current sourced consumers retain authenticated archive preparation."""
    sourced=job_blocks(sourced_text);geometry=job_blocks(geometry_text)
    for block, step_name, consumer in (
        (sourced['semantic-replay'], 'Reassemble the original authenticated payload',
         'Rebuild all five registries and actually replay every coupled case'),
        (sourced['geometry-and-recorded-methods'], 'Reassemble the original authenticated sourced-cell payload',
         'Reopen all five full-train occurrence inventories'),
        (geometry['regenerate'], 'Reassemble the original authenticated sourced-cell payload',
         'Export and reopen all five source-bound vehicle IFCs'),
    ):
        header='      - name: '+step_name+'\n'
        body=('        run: >-\n'
              '          "$GITHUB_WORKSPACE/.venv/bin/python" tools/automation/sourced-archive.py ensure docs/design-engine/sourced-case\n')
        assert block.count(header)==1
        tail=block.split(header,1)[1]
        next_step=re.search(r'^      - ',tail,re.M)
        assert next_step and tail[:next_step.start()]==body, 'Sourced preparation must be an unconditional fail-fast step'
        assert block.index(header)<block.index('      - name: '+consumer+'\n')


def validate(historical_text, shared_text, current_text, archive, sourced_text, geometry_text):
    validate_current_sourced_archive_consumers(sourced_text, geometry_text)
    unsigned = {k: v for k, v in archive.items() if k != 'archive_id'}
    raw = (json.dumps(unsigned, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n').encode()
    assert archive['schema'] == 'osr-v05-git-archive/1'
    assert archive['archive_id'] == sha256(raw).hexdigest()
    assert archive['physical_accepted'] is False
    assert re.fullmatch('[0-9a-f]{40}', archive['revision'])
    historical_jobs = job_blocks(historical_text)
    jobs = job_blocks(shared_text)
    assert set(historical_jobs) == {'primary-study'}
    assert set(jobs) == {'current-shared-software', 'bounded-axial-search-method', 'native-canonical-parity', 'control-formal'}
    validate_native_canonical_job(shared_text)
    axial=jobs['bounded-axial-search-method']
    for required in ('timeout-minutes: 15', 'OSR_TEST_NATIVE_AXIAL: "1"', 'OSR_TEST_NATIVE_FRAME: "1"',
                     'OPENBLAS_NUM_THREADS: "1"', 'OMP_NUM_THREADS: "1"', 'MKL_NUM_THREADS: "1"',
                     'calculix-ccx', 'numpy==2.3.5', 'test -x /usr/bin/ccx',
                     'engineering/design_search/tests/test_native_refinement.py -k native_axial_run_and_read_only_replay',
                     'engineering/design_search/tests/test_frame_native.py -k optional_native_bending_control_and_readonly_replay'):
        assert required in axial, 'Current bounded axial method control missing: '+required
    assert not re.search(r'^\s+ref:',axial,re.M), 'The current axial control must use current source'
    assert historical_text.startswith('name: Historical v0.5 ')
    assert shared_text.startswith('name: Shared software ')
    assert '  workflow_dispatch:' in historical_text and '  schedule:' in historical_text
    assert 'tags: ["v0.5.*"]' in historical_text
    triggers = historical_text.split('permissions:', 1)[0]
    path_filters = re.findall(r'^      - "([^"\n]+)"$', triggers, re.M)
    assert set(path_filters) == {'.github/workflows/historical-v05.yml', 'docs/archives/v0.5-maglev/**', 'tools/automation/historical-native-preflight.py', 'tools/automation/install-historical-freecad.py', 'tools/automation/download-pinned-tool.py', 'tools/automation/configure-historical-apt.py', 'tools/automation/prepare-historical-replay.py'}
    assert len(path_filters) == 14  # Same narrow push and PR filters.
    assert re.search(r'^    - cron: "[0-9]+ [0-9]+ \* \* [0-6]"$', triggers, re.M)
    shared_triggers = shared_text.split('permissions:', 1)[0]
    assert '  push:\n    branches: [main]\n    paths:\n' in shared_triggers
    push_block = shared_triggers.split('  push:\n', 1)[1].split('  pull_request:\n', 1)[0]
    pull_block = shared_triggers.split('  pull_request:\n', 1)[1].split('  workflow_dispatch:\n', 1)[0]
    push_paths = re.findall(r'^      - "([^"\n]+)"$', push_block, re.M)
    pull_paths = re.findall(r'^      - "([^"\n]+)"$', pull_block, re.M)
    assert push_paths and push_paths == pull_paths
    for required in ('.github/workflows/shared-software.yml', '.github/local-processing.json',
                     'engineering/**', 'tests/**', 'tools/**', 'services/**', 'crates/**',
                     'campaigns/**', 'cities/catalogue/**', 'docs/archives/**',
                     'docs/assets/chair-installation-r4-v06/**',
                     'docs/assets/terminal-frame-v06/**', 'docs/workbench/current/**',
                     'docs/design-engine/**', '!docs/design-engine/*.md', 'osr', 'osr-*'):
        assert required in push_paths, required
    assert path_filters_include('docs/design-engine/v06-design-closure/status.json', push_paths)
    assert not path_filters_include('docs/design-engine/native-design-search.md', push_paths), \
        'Unrelated root-level design narrative should not launch the shared suite'
    assert not path_filters_include('docs/open-source-rail-overview.md', push_paths)
    assert 'docs/**' not in push_paths
    assert not re.search(r'^\s+tags:', shared_triggers, re.M)
    historical = historical_jobs['primary-study']
    assert 'working-directory: historical' in historical
    assert re.findall(r'^          ref: (.+)$', historical, re.M) == [archive['revision']]
    assert 'path: current' in historical and 'path: historical' in historical
    assert "../current/docs/archives/v0.5-maglev/manifest.json" in historical
    assert "== manifest['revision']" in historical
    assert "Path('VERSION').read_text().strip() == '0.5'" in historical
    assert historical.count('uses: actions/checkout@v4') == 2
    assert 'runs-on: ubuntu-24.04' in historical
    assert 'QT_QPA_PLATFORM: offscreen' in historical
    assert 'install -y freecad' not in historical
    assert 'download-pinned-tool.py freecad --output build/native-download/freecad.AppImage' in historical
    assert historical.index('install-historical-freecad.py --archive') < historical.index('historical-native-preflight.py --output')
    dependency_step=historical.split('      - name: Install the direct native tools required by the pinned cycle\n',1)[1].split('      - name:',1)[0]
    assert '        shell: bash\n' in dependency_step, 'Dependency tee pipelines require explicit bash -eo pipefail'
    assert '        timeout-minutes: 20\n' in dependency_step
    dependency_commands = re.findall(r'^          (sudo .*apt-get .+)$', dependency_step, re.M)
    assert len(dependency_commands) == 2
    for command in dependency_commands:
        for option in ('Acquire::Retries=3', 'Acquire::http::Timeout=30',
                       'Acquire::https::Timeout=30', 'Acquire::http::Dl-Limit=0',
                       'Acquire::https::Dl-Limit=0'):
            assert '-o ' + option in command
    assert 'install --no-install-recommends -y gmsh getdp calculix-ccx libglu1-mesa libegl1 libopengl0 ffmpeg fonts-dejavu-core' in dependency_step
    route = 'configure-historical-apt.py --apt-root /etc/apt --output'
    route_step = historical.split('      - name: Record and route the disposable runner Ubuntu sources\n', 1)[1].split('      - name:', 1)[0]
    assert '        shell: bash\n' in route_step
    assert '/tools/automation/configure-historical-apt.py\n' in historical
    assert historical.index(route) < historical.index('sudo apt-get')
    for artifact in ('historical-apt-sources/', 'historical-apt-source-route.log',
                     'historical-apt-inherited-download.conf', 'historical-apt-effective-download.conf'):
        assert 'historical/build/' + artifact in historical
    assert 'python tools/automation/tests/test_historical_apt.py' in shared_text
    retention = 'prepare-historical-replay.py --repository . --archive-contract'
    assert '/tools/automation/prepare-historical-replay.py\n' in historical
    assert historical.index('verify-maglev-sources.py') < historical.index(retention)
    assert historical.index(retention) < historical.index('ferrite-maglev-study.py cycle')
    assert 'python tools/automation/tests/test_historical_replay.py' in shared_text
    browser_step = historical.split('      - name: Install locked browser dependencies before any publication can need them\n', 1)[1].split('      - name:', 1)[0]
    assert '        shell: bash\n' in browser_step
    assert '        timeout-minutes: 15\n' in browser_step
    assert historical.count('uses: actions/setup-node@v4') == 1
    assert historical.count('npm ci') == 1
    assert historical.count('npx playwright install --with-deps chromium') == 1
    assert (historical.index('uses: actions/setup-node@v4') < historical.index('npm ci')
            < historical.index('npx playwright install --with-deps chromium')
            < historical.index('ferrite-maglev-study.py cycle'))
    assert 'historical/build/historical-browser-install.log' in historical
    final_browser_step = historical.split('      - name: Browser report, images and mobile layout\n', 1)[1].split('      - name:', 1)[0]
    assert historical.index('ferrite-maglev-study.py cycle') < historical.index('      - name: Browser report, images and mobile layout\n')
    for command in ('ferrite-maglev-study.py run', 'verify-maglev-v05.mjs build/maglev-browser',
                    'verify-maglev-workbench.mjs build/maglev-workbench-browser'):
        assert command in final_browser_step
    for artifact in ('historical-replay-retained/', 'historical-replay-preparation.json',
                     'historical-replay-preparation.log'):
        assert 'historical/build/' + artifact in historical
    assert historical.index('historical-native-preflight.py --output') < historical.index('ferrite-maglev-study.py cycle')
    assert 'ferrite-maglev-study.py cycle' in historical and 'capabilities.py --check' in historical
    assert historical.index('ferrite-maglev-study.py cycle') < historical.index('capabilities.py --check')
    assert 'historical/build/maglev-historical-cycle.log' in historical
    assert re.findall(r'^\s+(?:- )?if: (.+)$', historical, re.M) == ['always()']
    # Keep the full historical coverage: source, configuration, numerical,
    # assurance, native receipts, replay, release refusal, books and browsers.
    for command in (
        'verify-maglev-sources.py', 'validate-host-manifests.py', 'capabilities.py --check',
        'catalogue.py index --check', 'generate-design-index.py --check',
        'generate-doc-index.py --check', 'check-readmes.py',
        'cargo test --locked --workspace --all-targets',
        'cargo test --locked -p osr-maglev-control --all-targets',
        'cargo check --locked -p osr-maglev-control --no-default-features',
        'cargo fmt --package osr-maglev-control -- --check',
        'cargo clippy -p osr-maglev-control --all-targets -- -D warnings',
        'observer-prototype/tests/differential.py',
        'ferrite-maglev-study.py cycle', 'test_ferrite_maglev*.py',
        'pilot_assurance verify --require-executed', 'geometry.verify_native',
        'evacuation.verify_native', 'system_development.verify()',
        'coupled --output', 'coupled --verify build/maglev-ci-coupled',
        'coupled --verify docs/design-engine/ferrite-maglev/coupled',
        'ferrite-maglev-study.py run', 'ferrite-maglev-study.py check',
        '--example multimodule_replay', 'ferrite-maglev-study.py release-check',
        'test "$code" = 3', 'generate-public-overview.py --check',
        'build-doc-book.py --check', 'verify-maglev-v05.mjs',
        'verify-maglev-workbench.mjs',
    ):
        assert command in historical, command
    for name in ('current-shared-software', 'bounded-axial-search-method', 'control-formal'):
        current = jobs[name]
        assert current.count('uses: actions/checkout@v4') == 1
        assert not re.search(r'^\s+(ref|working-directory|needs|continue-on-error):', current, re.M), name
        checkout = current.split('uses: actions/checkout@v4', 1)[1].split('      -', 1)[0]
        assert not re.search(r'^\s+path:', checkout, re.M), name
        assert re.findall(r'^\s+(?:- )?if: (.+)$', current, re.M) == (['always()'] if name == 'control-formal' else []), name
    shared = jobs['current-shared-software']
    for command in ('test_ci_architecture.py', 'verify-maglev-sources.py',
                    'test_doc_index.py',
                    'cargo test --locked --workspace --all-targets',
                    'cargo check --locked -p osr-maglev-control --no-default-features',
                    'observer-prototype/tests/differential.py',
                    'test_fe_point_load_and_modal_frequencies_have_independent_controls',
                    'test_invalid_beam_assumptions_fail_before_numerics'):
        assert command in shared, command
    assert 'pilot_assurance run control-formal' in jobs['control-formal']
    formal=jobs['control-formal']
    pinned_commands=('cargo install kani-verifier --version 0.67.0 --locked',
        'python tools/automation/download-pinned-tool.py kani --output build/native-download/kani-0.67.0-x86_64-unknown-linux-gnu.tar.gz',
        'cargo kani setup --use-local-bundle "$PWD/build/native-download/kani-0.67.0-x86_64-unknown-linux-gnu.tar.gz"',
        'python -m engineering.ferrite_maglev.pilot_assurance run control-formal')
    assert all(command in formal for command in pinned_commands)
    assert [formal.index(command) for command in pinned_commands]==sorted(formal.index(command) for command in pinned_commands)
    assert 'git fetch --no-tags --depth=1 origin 92e1385e03dcd5c6f76a5b0a9dd5ba348f50d164' in shared
    assert 'git fetch --no-tags --depth=1 origin 3bf38a501d09fa3a3c2dd6f4731be11828d04f55:refs/osr/retired-station-reference' in shared
    assert 'test_research_context.py' in shared and 'test_research_portability.py' in shared
    # Artifact upload may use always(), but checks cannot be conditional or ignored.
    assert not re.search(r'^\s+continue-on-error:', historical_text + shared_text, re.M)
    assert not re.search(r'^    (if|needs):', historical, re.M)
    # Current v0.6 contracts retain their independent required gate and neutral dependencies.
    current_jobs = job_blocks(current_text)
    assert not re.search(r'^defaults:', current_text, re.M), 'Do not replace the fail-fast runner shell'
    required_jobs = {'current-contracts', 'retired-reference-methods', 'independent-search', 'retained-packet-reconstruction',
                     'retained-service-energy-extra', 'vehicle-runtime-reproducibility'}
    assert required_jobs | {'required-engineering'} <= current_jobs.keys()
    dispatch = current_text.split('  workflow_dispatch:\n', 1)[1].split('  schedule:\n', 1)[0]
    assert re.search(r'^      retired_methods:\n        description: Run the 45-minute pinned fixed-service research regression\n        type: boolean\n        default: false$', dispatch, re.M)
    gate = current_jobs['required-engineering']
    needs = re.search(r'^    needs: \[([^\]\n]+)\]$', gate, re.M)
    assert needs, 'The current engineering gate must declare its required jobs'
    listed = [name.strip() for name in needs[1].split(',')]
    assert len(listed) == len(set(listed)) and set(listed) == required_jobs
    assert re.search(r'^    if: always\(\)$', gate, re.M)
    for name in required_jobs - {'retired-reference-methods'}:
        check = "test '${{ needs." + name + ".result }}' = success"
        assert re.search(r'^ {10}' + re.escape(check) + r' *$', gate, re.M), name
    for check in ('test "$RETIRED_REFERENCE_RESULT" = success', 'test "$RETIRED_REFERENCE_RESULT" = skipped'):
        assert re.search(r'^ {12}' + re.escape(check) + r' *$', gate, re.M), check
    assert "REQUIRE_RETIRED_REFERENCE: ${{ (github.event_name == 'workflow_dispatch' && inputs.retired_methods) || github.event_name == 'schedule' }}" in gate
    assert 'RETIRED_REFERENCE_RESULT: ${{ needs.retired-reference-methods.result }}' in gate
    for name in required_jobs - {'retired-reference-methods'}:
        assert not re.search(r'^    (if|continue-on-error):', current_jobs[name], re.M), name
    validate_retired_reference_job(current_jobs['retired-reference-methods'])
    validate_retained_periodic_route(current_jobs['retired-reference-methods'])
    validate_retained_periodic_route(current_jobs['current-contracts'])
    assert re.findall(r'^\s+(?:- )?if: (.+)$', current_jobs['current-contracts'], re.M) == ['always()']
    assert not re.search(r'^\s+(?:- )?continue-on-error:', current_jobs['current-contracts'], re.M)
    validate_retained_periodic_test_contract(RETAINED_PERIODIC_HELPER.read_text())
    assert re.search(r'^          \./osr design space verify$', current_jobs['current-contracts'], re.M)
    assert 'tests/test_propulsion_layout_quantities.py' in current_jobs['current-contracts']
    assert 'tests/test_candidate_specific_baseline.py' in current_jobs['current-contracts']
    assert ('git fetch --no-tags --depth=1 origin '
            '3bf38a501d09fa3a3c2dd6f4731be11828d04f55:refs/osr/retired-station-reference') in current_jobs['current-contracts']
    for name in ('independent-search', 'retained-packet-reconstruction', 'retained-service-energy-extra'):
        assert not re.search(r'^\s+continue-on-error:', current_jobs[name], re.M), name
        conditions = re.findall(r'^\s+(?:- )?if: (.+)$', current_jobs[name], re.M)
        assert conditions == (['always()'] if name == 'independent-search' else []), name
    for name, commands in {
            'independent-search': ('test_search_backends.py', 'civil_shape_portfolio verify',
                                   'civil_shape_portfolio audit-optimizers'),
            'retained-packet-reconstruction': ('test_retained_packet_materialize.py',
                                                'retained_packet_materialize',
                                                'retained_source_epoch verify'),
            'retained-service-energy-extra': ('test_retained_service_energy_epoch.py',
                                               'test_retained_service_energy_handoff.py',
                                               'test_retained_service_energy_materialize.py',
                                               'test_retained_service_energy_materialize_handoff.py',
                                               'test_service_energy_migration_inventory.py',
                                               'retained_service_energy_epoch verify',
                                               'retained_service_energy_materialize materialize'),
    }.items():
        for command in commands: assert active_run_line(current_jobs[name], command), (name, command)
    assert 'uses: actions/upload-artifact@v4' in current_jobs['independent-search']
    assert re.search(r'^          name: civil-portfolio-search-audit$', current_jobs['independent-search'], re.M)
    extra = current_jobs['retained-service-energy-extra']
    assert re.search(r'^        env:\n          OSR_MIGRATION_REQUIRE_REAL: "1"\n        run: \|$', extra, re.M)
    checked_historical_route(current_jobs['retained-packet-reconstruction'],
        parent='retained_packet_parent', prefix='osr-retained-packets', commit=OLD_COMMIT,
        materialize=OLD_MATERIALIZE, verify=OLD_VERIFY, expected_script=OLD_SCRIPT)
    checked_historical_route(extra, parent='retained_extra_parent', prefix='osr-service-energy',
        commit=EXTRA_COMMIT, materialize=EXTRA_MATERIALIZE, verify=EXTRA_VERIFY, expected_script=EXTRA_SCRIPT)
    assert 'sourced-archive.py ensure docs/design-engine/sourced-case' not in extra
    assert active_run_line(current_jobs['current-contracts'], 'test_retained_source_epoch.py')
    assert not active_run_line(current_jobs['current-contracts'], 'retained_source_epoch verify')
    runtime_job = current_jobs['vehicle-runtime-reproducibility']
    assert re.findall(r'python-version: "([^"]+)"', runtime_job) == ['3.11', '3.12', '3.13']
    for runtime in ('311', '312', '313'):
        assert 'steps.python' + runtime + '.outputs.python-path' in runtime_job
    assert 'test_vehicle_runtime_reproducibility.py' in runtime_job
    assert 'engineering/requirements.txt' in current_text and 'engineering/requirements.txt' in shared
    assert 'engineering/ferrite_maglev/requirements.txt' not in current_text + shared_text
    publication_inputs = (
        'engineering/readme_context.py', 'engineering/maglev_research/readme_context.py',
        'install.sh', '.github/repository-metadata.yml', 'engineering/requirements.txt',
        'engineering/research_context.py', 'engineering/research_test_support.py', 'engineering/research_ancestry.py',
        'engineering/development_baseline/tests/test_install_contract.py',
        'engineering/development_baseline/tests/test_readme_context.py',
        'docs/design-engine/v06-design-closure/status.json',
    )
    # Both PRs and main pushes must exercise the selected publication/installer contracts.
    for event in ('pull_request', 'push'):
        event_text = current_text.split('  ' + event + ':\n', 1)[1]
        event_text = re.split(r'^  [a-z_]+:', event_text, maxsplit=1, flags=re.M)[0]
        patterns = re.findall(r'^      - "([^"\n]+)"$', event_text, re.M)
        for path in publication_inputs:
            assert any(fnmatchcase(path, pattern) for pattern in patterns), (event, path)
    for name in re.findall(r'^      - name: (.+)$', shared_text, re.M):
        if 'maglev' in name.lower():
            assert 'retained' in name.lower(), name


PUBLICATION_ORIGINS = {
    'comfort-options': ('f0946b699376699b408df6e9a1f04a657f74022b', 'python -m engineering.comfort_options verify'),
    'comfort-design': ('578ee3950b872bf30fbf9e4207b2bda85951bdd7', 'python -m engineering.comfort_design verify'),
    'vehicle-optimisation': ('afff13ebdb775a024b3b3f2f3331473297e853ef', "publication.verify('docs/design-engine/vehicle-optimisation')"),
    'passive-suspension': ('aa31cec3307f82b0a5de65b76f8938081f7801a8', "publication.verify('docs/design-engine/passive-suspension')"),
}


def validate_publication(name, text):
    revision, verifier = PUBLICATION_ORIGINS[name]
    jobs = job_blocks(text)
    historical = jobs.pop('historical-publication')
    assert len(jobs) == 1
    current = next(iter(jobs.values()))
    assert not re.search(r'^\s+(ref|working-directory|needs|if|continue-on-error):', current, re.M)
    assert 'python -m pytest' in current
    fetch = 'git fetch --no-tags --depth=1 origin 92e1385e03dcd5c6f76a5b0a9dd5ba348f50d164'
    assert fetch in current
    assert current.index(fetch) < current.index('python -m pytest')
    assert verifier not in current
    assert historical.count('uses: actions/checkout@v4') == 2
    assert re.findall(r'^          ref: (.+)$', historical, re.M) == [revision]
    assert 'working-directory: historical' in historical
    guard = 'verify-research-snapshot.py --packet ' + name
    assert guard in historical and verifier in historical
    assert historical.index(guard) < historical.index(verifier)
    assert re.findall(r'^\s+(?:- )?if: (.+)$', historical, re.M) == ['always()']
    assert 'continue-on-error:' not in text and 'needs:' not in text
    if name.startswith('comfort-'):
        assert 'verify-' + name + '.mjs' in historical


CONTEXT_INPUTS = ('engineering/research_context.py', 'engineering/research_test_support.py',
                  'engineering/research_ancestry.py')


def validate_context_triggers(text):
    for event in ('pull_request', 'push'):
        block = text.split('  ' + event + ':\n', 1)[1]
        block = re.split(r'^  [a-z_]+:', block, maxsplit=1, flags=re.M)[0]
        inline = re.search(r'paths: (\[[^\n]+\])', block)
        patterns = (ast.literal_eval(inline[1]) if inline else
                    re.findall(r"^      - ['\"]([^'\"\n]+)['\"]$", block, re.M))
        for name in CONTEXT_INPUTS:
            assert any(fnmatchcase(name, pattern) for pattern in patterns), (event, name)


def validate_trip_routes(text):
    jobs=job_blocks(text)
    assert {'trip-workbench-contract','contracts-and-retained-evidence','p0-bounds',
            'native-chrono-and-fem','historical-trip-publication','historical-round-contracts'}==jobs.keys()
    for name in ('contracts-and-retained-evidence','p0-bounds'):
        current=jobs[name]
        assert not re.search(r'^\s+(ref|working-directory|needs|if|continue-on-error):',current,re.M)
        fetch='git fetch --no-tags --depth=1 origin 92e1385e03dcd5c6f76a5b0a9dd5ba348f50d164'
        assert current.index(fetch)<current.index('python -m pytest')
    for name in ('trip-workbench-contract','native-chrono-and-fem','historical-round-contracts'):
        assert re.findall(r'^          ref: (.+)$',jobs[name],re.M)==['92e1385e03dcd5c6f76a5b0a9dd5ba348f50d164']
    assert 'verify-trip-workbench.mjs' in jobs['trip-workbench-contract']
    for suite in ('engineering/trip_dynamics/tests','engineering/trip_dynamics/fixtures/magnetics/test_numerics.py',
                  'engineering/electropermanent/tests','engineering/magnetic_confirmation/tests'):
        assert suite in jobs['contracts-and-retained-evidence']
    for suite in ('test_whole_system.py','test_guideway_tradeoff.py','test_operating_point.py',
                  'test_comfort_fixes.py'):
        assert suite in jobs['p0-bounds']
    assert 'test_physical_round_publication.py' in jobs['historical-round-contracts']
    historical=jobs['historical-trip-publication']
    assert re.findall(r'^          ref: (.+)$',historical,re.M)==['d7c8f40e13d9a5f4889921557311542b84bcbfb1']
    guard='verify-research-snapshot.py --packet trip-dynamics'
    verifier='python -m engineering.trip_dynamics verify --output docs/design-engine/trip-dynamics'
    assert guard in historical and verifier in historical
    assert historical.index(guard)<historical.index(verifier)
    assert 'working-directory: historical' in historical
    assert 'continue-on-error:' not in text


class ArchitectureRoutingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.historical = HISTORICAL_WORKFLOW.read_text()
        cls.shared = SHARED_WORKFLOW.read_text()
        cls.current = CURRENT_WORKFLOW.read_text()
        cls.archive = json.loads(ARCHIVE.read_text())
        cls.sourced = SOURCED_WORKFLOW.read_text()
        cls.geometry = SOURCED_GEOMETRY_WORKFLOW.read_text()

    def check(self, *, historical=None, shared=None, current=None, archive=None, sourced=None, geometry=None):
        validate(self.historical if historical is None else historical,
                 self.shared if shared is None else shared,
                 self.current if current is None else current,
                 self.archive if archive is None else archive,
                 self.sourced if sourced is None else sourced,
                 self.geometry if geometry is None else geometry)

    def test_control_verifier_requires_the_verified_local_bundle(self):
        self.check()
        command='cargo kani setup --use-local-bundle "$PWD/build/native-download/kani-0.67.0-x86_64-unknown-linux-gnu.tar.gz"'
        with self.assertRaises(AssertionError):self.check(shared=self.shared.replace(command,'cargo kani setup'))

    def test_digital_twin_storage_guards_and_pinned_cad_order(self):
        text = DIGITAL_TWIN_WORKFLOW.read_text()
        cleanup, install = twin_storage_steps(text)
        self.assertEqual(len(twin_python_blocks(cleanup)), 2)
        self.assertEqual(len(twin_python_blocks(install)), 3)
        for original, replacement in (
                ('test "${RUNNER_ENVIRONMENT:-}" = github-hosted', '# disabled host guard'),
                ("'/usr/local/lib/android', '/opt/ghc', '/usr/share/dotnet'", "'/home/runner'"),
                ('16 * 1024**3', '0'),
                ('required = 8 * 1024**3', 'required = 0'),
                ('required = 6 * 1024**3', 'required = 0'),
                ('archive.unlink()', '# archive retained'),
                ('run: ./osr-twin verify-publication', 'run: true')):
            with self.subTest(removed=original), self.assertRaises(AssertionError):
                twin_storage_steps(text.replace(original, replacement, 1))

    def test_native_control_toolchain_is_isolated_pinned_and_mandatory(self):
        validate_native_control_toolchain(self.current)
        for old,new in (
                ('"$RUNNER_TEMP/osr-native-rustup"', '"/home/runner/.rustup"'),
                ('"$RUNNER_TEMP/osr-native-cargo"', '"/home/runner/.cargo"'),
                ('      RUSTUP_TOOLCHAIN: "1.92.0"', '      RUSTUP_HOME: ${{ runner.temp }}/rustup\n      RUSTUP_TOOLCHAIN: "1.92.0"'),
                ('      - name: Initialize isolated Rust paths', '      - if: false\n        name: Initialize isolated Rust paths'),
                ('      RUSTUP_TOOLCHAIN: "1.92.0"', '      RUSTUP_TOOLCHAIN: stable'),
                ('      - uses: dtolnay/rust-toolchain@1.92.0', '      - uses: dtolnay/rust-toolchain@stable'),
                ('      - name: Verify isolated Rust toolchain', '      - if: false\n        name: Verify isolated Rust toolchain'),
                ('test "$(cargo --version | awk \'{print $2}\')" = 1.92.0', 'true'),
                ('      - run: cargo test --locked -p osr-atp', '      - run: echo cargo test --locked -p osr-atp'),
                (' -p osr-station-scada\n      - uses: actions/upload-artifact@v4',
                 ' -p osr-station-scada\n        continue-on-error: true\n      - uses: actions/upload-artifact@v4')):
            with self.subTest(changed=old), self.assertRaises(AssertionError):
                validate_native_control_toolchain(self.current.replace(old,new,1))

    def test_canonical_abi_matrix_build_and_parity_cannot_be_skipped(self):
        validate_native_canonical_job(self.shared)
        block=job_blocks(self.shared)['native-canonical-parity']
        for old,new in (('python: ["3.12", "3.13"]','python: ["3.13"]'),
                ('      RUSTUP_TOOLCHAIN: "1.92.0"','      CARGO_HOME: ${{ runner.temp }}/cargo\n      RUSTUP_TOOLCHAIN: "1.92.0"'),
                ('"$RUNNER_TEMP/osr-canonical-rustup"','"/home/runner/.rustup"'),
                ('          components: clippy','          components: rustfmt'),
                ('      - name: Initialize isolated Rust paths','      - if: false\n        name: Initialize isolated Rust paths'),
                ('OSR_TEST_NATIVE_CANONICAL: "1"','OSR_TEST_NATIVE_CANONICAL: "0"'),
                ('uses: dtolnay/rust-toolchain@1.92.0','uses: dtolnay/rust-toolchain@stable'),
                ('python -m engineering.design_search.native_canonical build','echo extension-not-built'),
                ('engineering/design_search/tests/test_native_canonical.py','nonexistent-parity-test.py'),
                ('engineering/design_search/tests/test_native_sealing.py','nonexistent-sealing-test.py'),
                ('engineering/design_search/tests/test_interface_validation_performance.py','nonexistent-interface-test.py'),
                ('      - name: Require exact canonical parity','      - if: false\n        name: Require exact canonical parity'),
                ('      - name: Check the optional Rust extension','      - continue-on-error: true\n        name: Check the optional Rust extension')):
            with self.subTest(changed=old),self.assertRaises(AssertionError):
                validate_native_canonical_job(self.shared.replace(block,block.replace(old,new,1)))

    def test_rust_path_initializers_write_runner_temp_before_install(self):
        jobs = ((job_blocks(self.current)['native-methods'], 'native', True),
                (job_blocks(self.shared)['native-canonical-parity'], 'canonical', False))
        with tempfile.TemporaryDirectory(prefix='osr rust env ') as directory:
            for block, prefix, target in jobs:
                script = isolated_rust_path_script(block, prefix, target=target)
                env_path = Path(directory) / (prefix + '.env')
                env = dict(os.environ, RUNNER_TEMP=directory, GITHUB_ENV=str(env_path))
                subprocess.run(['bash', '-e', '-c', script], env=env, check=True)
                expected = [f'RUSTUP_HOME={directory}/osr-{prefix}-rustup',
                            f'CARGO_HOME={directory}/osr-{prefix}-cargo']
                if target: expected.append(f'CARGO_TARGET_DIR={directory}/osr-{prefix}-target')
                self.assertEqual(env_path.read_text().splitlines(), expected)
                for missing in ('RUNNER_TEMP', 'GITHUB_ENV'):
                    incomplete = dict(env); incomplete.pop(missing)
                    result = subprocess.run(['bash', '-e', '-c', script], env=incomplete, capture_output=True)
                    self.assertNotEqual(result.returncode, 0, missing)

    def test_digital_twin_disk_thresholds_fail_before_download(self):
        _, install = twin_storage_steps(DIGITAL_TWIN_WORKFLOW.read_text())
        blocks = twin_python_blocks(install)
        with tempfile.TemporaryDirectory(prefix='osr-twin-space-') as directory:
            for script, gib in zip(blocks[:2], (8, 6)):
                for free, success in ((gib*1024**3-1, False), (gib*1024**3, True)):
                    program = ('import shutil, types\n'
                               f'shutil.disk_usage=lambda path: types.SimpleNamespace(free={free})\n'
                               f'exec({script!r})\n')
                    result = subprocess.run([sys.executable, '-c', program],
                        env=dict(os.environ, GITHUB_WORKSPACE=directory), capture_output=True, text=True)
                    with self.subTest(gib=gib, free=free):
                        self.assertEqual(result.returncode == 0, success, result.stderr)

    def test_digital_twin_space_check_requires_both_runner_filesystems(self):
        cleanup, _ = twin_storage_steps(DIGITAL_TWIN_WORKFLOW.read_text())
        script = twin_python_blocks(cleanup)[1]
        with tempfile.TemporaryDirectory(prefix='osr-twin-space-') as directory:
            root=Path(directory); workspace=root/'workspace'; workspace.mkdir(); temp=root/'temp'; temp.mkdir()
            for workspace_free, temp_free, success in ((16*1024**3-1,2*1024**3,False),
                    (16*1024**3,2*1024**3-1,False), (16*1024**3,2*1024**3,True)):
                program = ('import shutil, types\n'
                           f'shutil.disk_usage=lambda path: types.SimpleNamespace(free={workspace_free} if str(path)=={str(workspace)!r} else {temp_free})\n'
                           f'exec({script!r})\n')
                result=subprocess.run([sys.executable,'-c',program],
                    env=dict(os.environ,GITHUB_WORKSPACE=str(workspace),RUNNER_TEMP=str(temp)),capture_output=True,text=True)
                with self.subTest(workspace=workspace_free,temp=temp_free):
                    self.assertEqual(result.returncode == 0, success, result.stderr)

    def test_runner_sdk_cleanup_refuses_symlinks_and_preserves_unlisted_data(self):
        cleanup, _ = twin_storage_steps(DIGITAL_TWIN_WORKFLOW.read_text())
        script = twin_python_blocks(cleanup)[0]
        original = "('/usr/local/lib/android', '/opt/ghc', '/usr/share/dotnet')"
        with tempfile.TemporaryDirectory(prefix='osr-runner-sdk-') as directory:
            root = Path(directory); names = [root/name for name in ('android', 'ghc', 'dotnet')]
            preserve = root/'workspace'; preserve.mkdir(); (preserve/'evidence').write_text('keep')
            for path in names:path.mkdir(); (path/'disposable').write_text('remove')
            local_script = script.replace(original, repr(tuple(map(str, names))), 1)
            self.assertNotEqual(local_script, script)
            result = subprocess.run([sys.executable, '-c', local_script], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue(all(not path.exists() for path in names))
            self.assertEqual((preserve/'evidence').read_text(), 'keep')
            names[0].symlink_to(preserve, target_is_directory=True)
            refused = subprocess.run([sys.executable, '-c', local_script], capture_output=True, text=True)
            self.assertNotEqual(refused.returncode, 0)
            self.assertIn('Refusing symlinked runner SDK path', refused.stderr)
            self.assertEqual((preserve/'evidence').read_text(), 'keep')

    def test_archived_and_current_sources_are_separate(self):
        self.check()
        self.assertFalse((ROOT / '.github/workflows/maglev-v05.yml').exists())

    def test_wrong_historical_pin_is_rejected(self):
        with self.assertRaises(AssertionError):
            self.check(historical=self.historical.replace(self.archive['revision'], '0'*40))

    def test_missing_shared_regression_is_rejected(self):
        with self.assertRaises(AssertionError):
            self.check(shared=self.shared.replace('cargo test --locked --workspace --all-targets',
                                                  'cargo check --workspace'))

    def test_current_axial_method_cannot_disable_its_native_control(self):
        with self.assertRaises(AssertionError):
            self.check(shared=self.shared.replace('OSR_TEST_NATIVE_AXIAL: "1"','OSR_TEST_NATIVE_AXIAL: "0"'))
        with self.assertRaises(AssertionError):
            self.check(shared=self.shared.replace('-k native_axial_run_and_read_only_replay','-k absent_control'))

    def test_current_axial_method_requires_bounded_threads(self):
        with self.assertRaises(AssertionError):
            self.check(shared=self.shared.replace('OPENBLAS_NUM_THREADS: "1"','OPENBLAS_NUM_THREADS: "8"'))

    def test_current_frame_method_cannot_disable_its_native_control(self):
        with self.assertRaises(AssertionError):
            self.check(shared=self.shared.replace('OSR_TEST_NATIVE_FRAME: "1"','OSR_TEST_NATIVE_FRAME: "0"'))
        with self.assertRaises(AssertionError):
            self.check(shared=self.shared.replace('-k optional_native_bending_control_and_readonly_replay','-k absent_frame_control'))

    def test_current_source_cannot_be_pinned(self):
        shared = self.shared.replace('      - uses: actions/checkout@v4',
            '      - uses: actions/checkout@v4\n        with:\n          ref: ' + self.archive['revision'], 1)
        with self.assertRaises(AssertionError):
            self.check(shared=shared)

    def test_retired_reference_cannot_change_source_commands_or_skip_checks(self):
        block = job_blocks(self.current)['retired-reference-methods']
        validate_retired_reference_job(block)
        for before, after in (
                ('ref: 3bf38a501d09fa3a3c2dd6f4731be11828d04f55', 'ref: main'),
                ('run: ./osr verify', 'run: echo skipped'),
                ('      - run: ./osr verify', '      - run: ./osr verify\n        if: false'),
                ('      - run: ./osr verify', '      - continue-on-error: true\n        run: ./osr verify'),
                ('          ref: 3bf38a501d09fa3a3c2dd6f4731be11828d04f55',
                 '          ref: 3bf38a501d09fa3a3c2dd6f4731be11828d04f55\n          path: other-source')):
            with self.subTest(changed=before), self.assertRaises(AssertionError):
                validate_retired_reference_job(block.replace(before, after, 1))

    def test_retired_reference_regression_is_opt_in_and_required_when_selected(self):
        condition="if: (github.event_name == 'workflow_dispatch' && inputs.retired_methods) || github.event_name == 'schedule'"
        gate_success='test "$RETIRED_REFERENCE_RESULT" = success'
        gate_skipped='test "$RETIRED_REFERENCE_RESULT" = skipped'
        for before,after in ((condition,'if: always()'),(gate_success,'true'),(gate_skipped,'true'),
                ('default: false\n  schedule:','default: true\n  schedule:')):
            with self.subTest(changed=before), self.assertRaises(AssertionError):
                self.check(current=self.current.replace(before,after,1))

    def test_retained_periodic_route_cannot_be_removed_skipped_or_reordered(self):
        block = job_blocks(self.current)['retired-reference-methods']
        validate_retained_periodic_route(block)
        for before, after in (
                ('test_periodic_thermal_research.py', 'not-the-current-test.py'),
                ('git fetch --no-tags --depth=1 origin ' + EXTRA_COMMIT,
                 'echo git fetch --no-tags --depth=1 origin ' + EXTRA_COMMIT),
                ('OSR_TEST_RETAINED_PERIODIC=1', 'OSR_TEST_RETAINED_PERIODIC=0'),
                ('test_retained_periodic_thermal.py', 'not-the-archived-test.py'),
                ('.venv/bin/python -m engineering.design_search.retained_periodic_thermal verify',
                 'echo .venv/bin/python -m engineering.design_search.retained_periodic_thermal verify'),
                ('.venv/bin/python -m engineering.design_search.retained_periodic_thermal replay',
                 '# .venv/bin/python -m engineering.design_search.retained_periodic_thermal replay'),
                ('retained_periodic_parent=$(mktemp -d "$RUNNER_TEMP/osr-periodic-thermal.XXXXXX")',
                 'retained_periodic_parent=/tmp/unbounded'),
                ('      - name: Material-distribution experiments and disjoint cost accounting',
                 '      - if: false\n        name: Material-distribution experiments and disjoint cost accounting'),
                ('      - name: Material-distribution experiments and disjoint cost accounting\n        run: |',
                 '      - name: Material-distribution experiments and disjoint cost accounting\n        continue-on-error: true\n        run: |'),
                ('      - name: Material-distribution experiments and disjoint cost accounting\n        run: |',
                 '      - name: Material-distribution experiments and disjoint cost accounting\n        run: |\n          set +e'),
                ('      - name: Material-distribution experiments and disjoint cost accounting\n        run: |',
                 '      - name: Material-distribution experiments and disjoint cost accounting\n        run: |\n          exit 0'),
        ):
            with self.subTest(changed=before), self.assertRaises(AssertionError):
                validate_retained_periodic_route(block.replace(before, after, 1))
        fetch = '          git fetch --no-tags --depth=1 origin ' + EXTRA_COMMIT + '\n'
        verify = '          .venv/bin/python -m engineering.design_search.retained_periodic_thermal verify\n'
        with self.assertRaises(AssertionError):
            validate_retained_periodic_route(block.replace(fetch, '', 1).replace(verify, verify + fetch, 1))

    def test_archived_periodic_replay_cannot_drop_original_tests_or_verifier(self):
        text = RETAINED_PERIODIC_HELPER.read_text()
        validate_retained_periodic_test_contract(text)
        for before, after in (
                ("'engineering/design_search/tests/test_periodic_thermal_research.py'", "'missing-research.py'"),
                ("'engineering/design_search/tests/test_periodic_thermal_publication.py'", "'missing-publication.py'"),
                ("'--import-mode=importlib'", "'-k nonexistent-test'"),
                ('if code:raise SystemExit(code)', 'if code:pass'),
                ('result=publication.verify(', 'result=publication.ignore('),
                ("expected_evaluation_id=pins['evaluation_id']", "expected_evaluation_id=pins['request_id']"),
        ):
            with self.subTest(changed=before), self.assertRaises(AssertionError):
                validate_retained_periodic_test_contract(text.replace(before, after, 1))

    def test_runtime_comparison_cannot_be_removed_from_the_required_gate(self):
        for before, after in (
                ("test '${{ needs.vehicle-runtime-reproducibility.result }}' = success", 'true'),
                ('python-version: "3.11"', 'python-version: "3.13"'),
                ('steps.python312.outputs.python-path', 'steps.python313.outputs.python-path')):
            with self.subTest(before=before), self.assertRaises(AssertionError):
                self.check(current=self.current.replace(before, after))

    def test_each_required_current_job_and_its_checks_cannot_be_removed(self):
        required = ('current-contracts', 'retired-reference-methods', 'independent-search', 'retained-packet-reconstruction',
                    'retained-service-energy-extra', 'vehicle-runtime-reproducibility')
        match = re.search(r'^    needs: \[([^\]\n]+)\]$', job_blocks(self.current)['required-engineering'], re.M)
        self.assertIsNotNone(match)
        line = 'needs: [' + match[1] + ']'
        for name in required:
            reduced = 'needs: [' + ', '.join(x.strip() for x in match[1].split(',') if x.strip()!=name) + ']'
            if name == 'retired-reference-methods':
                checks = ('test "$RETIRED_REFERENCE_RESULT" = success',
                          'test "$RETIRED_REFERENCE_RESULT" = skipped')
            else:
                checks = ("test '${{ needs." + name + ".result }}' = success",)
            mutations = [self.current.replace(line, reduced, 1)]
            mutations.extend(self.current.replace(check, 'true', 1) for check in checks)
            for mutated in mutations:
                with self.subTest(name=name, mutated=mutated != self.current), self.assertRaises(AssertionError):
                    self.check(current=mutated)
        for name, command in (
                ('independent-search', 'civil_shape_portfolio audit-optimizers'),
                ('retained-packet-reconstruction', 'test_retained_packet_materialize.py'),
                ('retained-service-energy-extra', 'retained_service_energy_epoch verify'),
                ('retained-service-energy-extra', 'test_service_energy_migration_inventory.py'),
                ('retained-service-energy-extra', 'retained_service_energy_materialize materialize')):
            with self.subTest(job=name), self.assertRaises(AssertionError):
                self.check(current=self.current.replace(command, 'removed-check', 1))
            with self.subTest(job=name, disabled='comment'), self.assertRaises(AssertionError):
                self.check(current=self.current.replace(command, '# ' + command, 1))
        check = "test '${{ needs.independent-search.result }}' = success"
        with self.assertRaises(AssertionError):
            self.check(current=self.current.replace('OSR_MIGRATION_REQUIRE_REAL: "1"', 'OSR_MIGRATION_REQUIRE_REAL: "0"', 1))
        with self.assertRaises(AssertionError):
            self.check(current=self.current.replace(check, '# ' + check, 1))
        audit = '.venv-search/bin/python -m engineering.design_search.civil_shape_portfolio audit-optimizers'
        with self.assertRaises(AssertionError):
            self.check(current=self.current.replace(audit, 'echo ' + audit, 1))
        with self.assertRaises(AssertionError):
            self.check(current=self.current.replace('      - name: Breadth-first civil geometry and independent search libraries',
                '      - if: false\n        name: Breadth-first civil geometry and independent search libraries', 1))

    def test_historical_verification_requires_exact_materialized_roots_and_pins(self):
        for command, root, archive_id in (
                (OLD_VERIFY, '$retained_packet_parent/packets/root', OLD_ARCHIVE_ID),
                (EXTRA_VERIFY, '$retained_extra_parent/packets/root', EXTRA_ARCHIVE_ID)):
            replacements = ('# '+command, 'echo '+command,
                            command.replace(root, '.'), command.replace(archive_id, '0'*64),
                            command+' || true')
            for changed in replacements:
                with self.subTest(command=command, changed=changed), self.assertRaises(AssertionError):
                    self.check(current=self.current.replace(command, changed, 1))
        with self.assertRaises(AssertionError):
            self.check(current=self.current.replace(EXTRA_VERIFY, EXTRA_VERIFY.replace(EXTRA_PINS_ID, '0'*64), 1))

    def test_historical_verification_must_follow_pinned_materialization(self):
        for materialize, verify, commit in ((OLD_MATERIALIZE, OLD_VERIFY, OLD_COMMIT),
                                             (EXTRA_MATERIALIZE, EXTRA_VERIFY, EXTRA_COMMIT)):
            adjacent = materialize+'\n          '+verify
            self.assertIn(adjacent, self.current)
            mutations = (self.current.replace(adjacent, verify+'\n          '+materialize, 1),
                         self.current.replace(materialize, '# '+materialize, 1),
                         self.current.replace(materialize, materialize.replace(commit, '0'*40), 1),
                         self.current.replace('git fetch --no-tags --depth=1 origin '+commit,
                                              'git fetch --no-tags --depth=1 origin '+'0'*40, 1),
                         *(self.current.replace(target, bypass+'\n          '+target, 1)
                           for target in (materialize,verify)
                           for bypass in ('set +e','set +o errexit','exit 0')),
                         self.current.replace('          '+materialize,
                            '        shell: bash {0}\n          '+materialize, 1))
            for altered in mutations:
                with self.subTest(materialize=materialize, altered=altered!=self.current), self.assertRaises(AssertionError):
                    self.check(current=altered)
            wrong_job=self.current.replace('          '+verify+'\n', '', 1).replace(
                '          .venv/bin/python -m pytest -q --import-mode=importlib engineering/design_search/tests/test_retained_source_epoch.py\n',
                '          .venv/bin/python -m pytest -q --import-mode=importlib engineering/design_search/tests/test_retained_source_epoch.py\n          '+verify+'\n', 1)
            with self.subTest(materialize=materialize, wrong_job=True), self.assertRaises(AssertionError):
                self.check(current=wrong_job)
        with self.assertRaises(AssertionError):
            self.check(current=self.current.replace('\njobs:\n','\ndefaults:\n  run:\n    shell: bash {0}\njobs:\n',1))

    def test_current_sourced_consumers_keep_independent_archive_preparation(self):
        ensure='"$GITHUB_WORKSPACE/.venv/bin/python" tools/automation/sourced-archive.py ensure docs/design-engine/sourced-case'
        self.assertEqual(self.sourced.count(ensure),2)
        self.assertEqual(self.geometry.count(ensure),1)
        first=self.sourced.replace(ensure, '# '+ensure, 1)
        last=self.sourced[::-1].replace(ensure[::-1], ('# '+ensure)[::-1], 1)[::-1]
        for changed in (first,last):
            with self.subTest(changed=changed), self.assertRaises(AssertionError):self.check(sourced=changed)
        with self.assertRaises(AssertionError):
            self.check(geometry=self.geometry.replace(ensure, '# '+ensure, 1))
        for extra in ('if: false','continue-on-error: true'):
            injected=ensure+'\n        '+extra
            first=self.sourced.replace(ensure,injected,1)
            last=self.sourced[::-1].replace(ensure[::-1],injected[::-1],1)[::-1]
            for changed in (first,last):
                with self.subTest(extra=extra), self.assertRaises(AssertionError):self.check(sourced=changed)
            with self.subTest(extra=extra, geometry=True), self.assertRaises(AssertionError):
                self.check(geometry=self.geometry.replace(ensure,injected,1))
        injected='          .venv/bin/python tools/automation/sourced-archive.py ensure docs/design-engine/sourced-case\n'
        with self.assertRaises(AssertionError):
            self.check(current=self.current.replace('          '+EXTRA_MATERIALIZE, injected+'          '+EXTRA_MATERIALIZE, 1))

    def test_historical_coverage_cannot_be_removed(self):
        with self.assertRaises(AssertionError):
            self.check(historical=self.historical.replace(
                'python tools/automation/capabilities.py --check', 'true'))

    def test_design_space_replay_cannot_be_removed(self):
        with self.assertRaises(AssertionError):
            self.check(current=self.current.replace('./osr design space verify', 'true', 1))
        for option in ('if: false', 'continue-on-error: true'):
            disabled = './osr design space verify\n        ' + option
            with self.subTest(option=option), self.assertRaises(AssertionError):
                self.check(current=self.current.replace('./osr design space verify', disabled, 1))

    def test_changed_archive_identity_is_rejected(self):
        archive = deepcopy(self.archive)
        archive['revision'] = '0'*40
        with self.assertRaises(AssertionError):
            self.check(archive=archive)

    def test_current_changes_do_not_trigger_the_historical_campaign(self):
        with self.assertRaises(AssertionError):
            self.check(historical=self.historical.replace(
                '      - "docs/archives/v0.5-maglev/**"', '      - "README.md"'))

    def test_historical_checks_cannot_be_silently_skipped(self):
        with self.assertRaises(AssertionError):
            self.check(historical=self.historical.replace(
                '      - name: Prepare runtime-bound publication and reader',
                '      - if: false\n        name: Prepare runtime-bound publication and reader'))

    def test_current_release_cannot_install_through_the_historical_package(self):
        with self.assertRaises(AssertionError):
            self.check(current=self.current.replace('engineering/requirements.txt',
                                                   'engineering/ferrite_maglev/requirements.txt'))

    def test_current_input_trigger_removal_is_rejected(self):
        for path in ('engineering/readme_context.py', 'engineering/maglev_research/readme_context.py',
                     'install.sh', '.github/repository-metadata.yml', 'engineering/requirements.txt',
        'engineering/research_context.py', 'engineering/research_test_support.py', 'engineering/research_ancestry.py',
                     'engineering/development_baseline/**',
                    'docs/design-engine/v06-design-closure/**'):
            with self.subTest(path=path):
                with self.assertRaises(AssertionError):
                    # Removing only the PR entry must fail even when main pushes still cover it.
                    self.check(current=self.current.replace('      - "' + path + '"\n', '', 1))

    def test_publication_origins_keep_current_and_historical_checks_independent(self):
        for name in PUBLICATION_ORIGINS:
            with self.subTest(packet=name):
                validate_publication(name, (ROOT / '.github/workflows' / (name + '.yml')).read_text())

    def test_wrong_publication_pin_is_rejected(self):
        for name, (revision, _) in PUBLICATION_ORIGINS.items():
            with self.subTest(packet=name):
                text = (ROOT / '.github/workflows' / (name + '.yml')).read_text()
                with self.assertRaises(AssertionError):
                    validate_publication(name, text.replace(revision, '0'*40))

    def test_context_helpers_trigger_their_current_compatibility_consumers(self):
        for name in ('comfort-options', 'comfort-design', 'vehicle-optimisation',
                     'passive-suspension', 'engineering-native', 'halbach-scaling', 'development-baseline'):
            with self.subTest(workflow=name):
                validate_context_triggers((ROOT / '.github/workflows' / (name + '.yml')).read_text())

    def test_missing_context_helper_trigger_is_rejected(self):
        text=(ROOT / '.github/workflows/comfort-options.yml').read_text()
        for name in CONTEXT_INPUTS:
            with self.subTest(source=name):
                with self.assertRaises(AssertionError):
                    validate_context_triggers(text.replace(repr(name)+', ', '', 1))

    def test_trip_unit_compatibility_and_original_publication_use_their_own_sources(self):
        text=(ROOT/'.github/workflows/trip-dynamics.yml').read_text()
        validate_trip_routes(text)
        validate_context_triggers(text)

    def test_trip_publication_cannot_be_moved_to_a_later_selector_revision(self):
        text=(ROOT/'.github/workflows/trip-dynamics.yml').read_text()
        with self.assertRaises(AssertionError):
            validate_trip_routes(text.replace('d7c8f40e13d9a5f4889921557311542b84bcbfb1',
                                             '92e1385e03dcd5c6f76a5b0a9dd5ba348f50d164'))

    def test_historical_dependency_failure_survives_log_capture(self):
        step=self.historical.split('      - name: Install the direct native tools required by the pinned cycle\n',1)[1].split('      - name:',1)[0]
        self.assertIn('        shell: bash\n',step)
        lines=step.split('        run: |\n',1)[1].splitlines()
        command='\n'.join(line[10:] for line in lines if line.startswith('          '))
        with tempfile.TemporaryDirectory(prefix='osr-apt-pipeline-test-') as directory:
            root=Path(directory);binary=root/'bin';binary.mkdir()
            sudo=binary/'sudo';sudo.write_text('#!/bin/sh\nexec "$@"\n');sudo.chmod(0o755)
            apt=binary/'apt-get'
            apt.write_text('#!/bin/sh\ncase " $* " in\n *" update "*) if [ "$CONTROLLED_APT_FAILURE" = update ]; then echo controlled-apt-update-failure; exit 73; fi;;\n *" install "*) touch install-was-run; if [ "$CONTROLLED_APT_FAILURE" = install ]; then echo controlled-apt-install-failure; exit 74; fi;;\nesac\necho controlled-apt-success\n')
            apt.chmod(0o755)
            environment=dict(os.environ,PATH=str(binary)+os.pathsep+os.environ['PATH'],
                             CONTROLLED_APT_FAILURE='update')
            failed=root/'strict';failed.mkdir()
            # This is GitHub's explicit `shell: bash` invocation. Only local
            # sudo/apt stubs execute; the actual published tee pipelines are used.
            result=subprocess.run(['/bin/bash','--noprofile','--norc','-e','-o','pipefail','-c',command],
                cwd=failed,env=environment,capture_output=True,text=True)
            self.assertEqual(result.returncode,73)
            self.assertFalse((failed/'install-was-run').exists())
            self.assertIn('controlled-apt-update-failure',(failed/'build/historical-native-install.log').read_text())
            # Negative control reproduces the defect in the former default
            # `bash -e` shell: tee hides the update failure and install continues.
            masked=root/'masked';masked.mkdir()
            control=subprocess.run(['/bin/bash','--noprofile','--norc','-e','-c',command],
                cwd=masked,env=environment,capture_output=True,text=True)
            self.assertEqual(control.returncode,0)
            self.assertTrue((masked/'install-was-run').exists())
            environment['CONTROLLED_APT_FAILURE']='install'
            install=root/'install-failed';install.mkdir()
            result=subprocess.run(['/bin/bash','--noprofile','--norc','-e','-o','pipefail','-c',command],
                cwd=install,env=environment,capture_output=True,text=True)
            self.assertEqual(result.returncode,74)
            self.assertTrue((install/'install-was-run').exists())
            self.assertIn('controlled-apt-install-failure',(install/'build/historical-native-install.log').read_text())

    def test_native_dependency_routing_and_packages_cannot_disappear(self):
        for before, after in (
            ('/tools/automation/configure-historical-apt.py\n', ''),
            ('install --no-install-recommends -y gmsh getdp calculix-ccx', 'install -y gmsh'),
            ('timeout-minutes: 20', 'timeout-minutes: 120'),
            ('shell: bash\n        run: |\n          mkdir -p build\n          sudo apt-get',
             'run: |\n          mkdir -p build\n          sudo apt-get'),
        ):
            with self.subTest(removed=before):
                with self.assertRaises(AssertionError):
                    self.check(historical=self.historical.replace(before, after))

    def test_browser_dependencies_cannot_be_delayed_until_after_the_cycle(self):
        start = self.historical.index('      - uses: actions/setup-node@v4\n')
        end = self.historical.index('      - name: Verify every published source and packet file is tracked\n')
        bootstrap = self.historical[start:end]
        late = self.historical[:start] + self.historical[end:]
        late = late.replace('      - name: Browser report, images and mobile layout\n',
                            bootstrap + '      - name: Browser report, images and mobile layout\n')
        # All original install and browser commands remain present in this
        # negative control; only the former broken dependency ordering returns.
        with self.assertRaises(AssertionError):
            self.check(historical=late)

    def test_browser_dependency_failures_survive_actual_workflow_log_pipelines(self):
        step = self.historical.split('      - name: Install locked browser dependencies before any publication can need them\n', 1)[1].split('      - name:', 1)[0]
        command = '\n'.join(line[10:] for line in step.split('        run: |\n', 1)[1].splitlines()
                            if line.startswith('          '))
        with tempfile.TemporaryDirectory(prefix='osr-browser-dependency-test-') as directory:
            root = Path(directory)
            binary = root / 'bin'
            binary.mkdir()
            for tool, code in (('npm', 81), ('npx', 82)):
                stub = binary / tool
                stub.write_text('#!/bin/sh\necho ' + tool + ' >> dependency-order.txt\n'
                    'if [ "$CONTROLLED_DEPENDENCY_FAILURE" = ' + tool + ' ]; then\n'
                    ' echo controlled-' + tool + '-failure; exit ' + str(code) + '\nfi\n'
                    'echo controlled-' + tool + '-success\n')
                stub.chmod(0o755)
            for failure, code, calls in (('npm', 81, ['npm']), ('npx', 82, ['npm', 'npx']),
                                         ('none', 0, ['npm', 'npx'])):
                with self.subTest(failure=failure):
                    run = root / failure
                    run.mkdir()
                    environment = dict(os.environ, PATH=str(binary) + os.pathsep + os.environ['PATH'],
                                       CONTROLLED_DEPENDENCY_FAILURE=failure)
                    # Execute the actual workflow block with local stubs only.
                    result = subprocess.run(['/bin/bash', '--noprofile', '--norc', '-e', '-o',
                                             'pipefail', '-c', command], cwd=run, env=environment,
                                            capture_output=True, text=True)
                    self.assertEqual(result.returncode, code)
                    self.assertEqual((run / 'dependency-order.txt').read_text().splitlines(), calls)
                    log = (run / 'build/historical-browser-install.log').read_text()
                    if failure != 'none':
                        self.assertIn('controlled-' + failure + '-failure', log)

    def test_required_current_release_gate_cannot_be_removed(self):
        mutated = re.sub(r'^    needs: \[[^\]\n]+\]$', '    needs: []', self.current, count=1, flags=re.M)
        self.assertNotEqual(mutated, self.current)
        with self.assertRaises(AssertionError):
            self.check(current=mutated)


if __name__ == '__main__':
    unittest.main()
