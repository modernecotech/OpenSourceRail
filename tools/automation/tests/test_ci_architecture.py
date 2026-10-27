#!/usr/bin/env python3
"""Guard CI source routing: frozen v0.5 replay and current shared regressions."""
from copy import deepcopy
import ast
from hashlib import sha256
from fnmatch import fnmatchcase
import json
import os
import subprocess
import tempfile
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[3]
HISTORICAL_WORKFLOW = ROOT / '.github/workflows/historical-v05.yml'
SHARED_WORKFLOW = ROOT / '.github/workflows/shared-software.yml'
CURRENT_WORKFLOW = ROOT / '.github/workflows/development-baseline.yml'
ARCHIVE = ROOT / 'docs/archives/v0.5-maglev/manifest.json'


def job_blocks(text):
    # Read only top-level job blocks, retaining nested step text unchanged.
    jobs = text.split('\njobs:\n', 1)[1]
    matches = list(re.finditer(r'^  ([a-z][a-z0-9-]*):\n', jobs, re.M))
    return {m[1]: jobs[m.end():matches[i+1].start() if i+1 < len(matches) else len(jobs)]
            for i, m in enumerate(matches)}


def validate(historical_text, shared_text, current_text, archive):
    unsigned = {k: v for k, v in archive.items() if k != 'archive_id'}
    raw = (json.dumps(unsigned, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n').encode()
    assert archive['schema'] == 'osr-v05-git-archive/1'
    assert archive['archive_id'] == sha256(raw).hexdigest()
    assert archive['physical_accepted'] is False
    assert re.fullmatch('[0-9a-f]{40}', archive['revision'])
    historical_jobs = job_blocks(historical_text)
    jobs = job_blocks(shared_text)
    assert set(historical_jobs) == {'primary-study'}
    assert set(jobs) == {'current-shared-software', 'control-formal'}
    assert historical_text.startswith('name: Historical v0.5 ')
    assert shared_text.startswith('name: Shared software ')
    assert '  workflow_dispatch:' in historical_text and '  schedule:' in historical_text
    assert 'tags: ["v0.5.*"]' in historical_text
    triggers = historical_text.split('permissions:', 1)[0]
    path_filters = re.findall(r'^      - "([^"\n]+)"$', triggers, re.M)
    assert set(path_filters) == {'.github/workflows/historical-v05.yml', 'docs/archives/v0.5-maglev/**', 'tools/automation/historical-native-preflight.py', 'tools/automation/install-historical-freecad.py', 'tools/automation/configure-historical-apt.py', 'tools/automation/prepare-historical-replay.py'}
    assert len(path_filters) == 12  # Same narrow push and PR filters.
    assert re.search(r'^    - cron: "[0-9]+ [0-9]+ \* \* [0-6]"$', triggers, re.M)
    shared_triggers = shared_text.split('permissions:', 1)[0]
    assert '  push:\n    branches: [main]\n  pull_request:' in shared_triggers
    assert not re.search(r'^\s+(paths|tags):', shared_triggers, re.M)
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
    assert 'FreeCAD_1.1.4-Linux-x86_64-py311.AppImage' in historical
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
    for name in ('current-shared-software', 'control-formal'):
        current = jobs[name]
        assert current.count('uses: actions/checkout@v4') == 1
        assert not re.search(r'^\s+(ref|working-directory|needs|continue-on-error):', current, re.M), name
        checkout = current.split('uses: actions/checkout@v4', 1)[1].split('      -', 1)[0]
        assert not re.search(r'^\s+path:', checkout, re.M), name
        assert re.findall(r'^\s+(?:- )?if: (.+)$', current, re.M) == (['always()'] if name == 'control-formal' else []), name
    shared = jobs['current-shared-software']
    for command in ('test_ci_architecture.py', 'verify-maglev-sources.py',
                    'cargo test --locked --workspace --all-targets',
                    'cargo check --locked -p osr-maglev-control --no-default-features',
                    'observer-prototype/tests/differential.py',
                    'test_fe_point_load_and_modal_frequencies_have_independent_controls',
                    'test_invalid_beam_assumptions_fail_before_numerics'):
        assert command in shared, command
    assert 'pilot_assurance run control-formal' in jobs['control-formal']
    assert 'git fetch --no-tags --depth=1 origin 92e1385e03dcd5c6f76a5b0a9dd5ba348f50d164' in shared
    assert 'test_research_context.py' in shared and 'test_research_portability.py' in shared
    # Artifact upload may use always(), but checks cannot be conditional or ignored.
    assert not re.search(r'^\s+continue-on-error:', historical_text + shared_text, re.M)
    assert not re.search(r'^    (if|needs):', historical, re.M)
    # Current v0.6 contracts retain their independent required gate and neutral dependencies.
    current_jobs = job_blocks(current_text)
    assert {'current-contracts', 'required-engineering'} <= current_jobs.keys()
    assert 'needs: [current-contracts]' in current_jobs['required-engineering']
    assert "needs.current-contracts.result" in current_jobs['required-engineering']
    assert 'engineering/requirements.txt' in current_text and 'engineering/requirements.txt' in shared
    assert 'engineering/ferrite_maglev/requirements.txt' not in current_text + shared_text
    publication_inputs = (
        'engineering/readme_context.py', 'engineering/maglev_research/readme_context.py',
        'install.sh', '.github/repository-metadata.yml', 'engineering/requirements.txt',
        'engineering/research_context.py', 'engineering/research_test_support.py', 'engineering/research_ancestry.py',
        'engineering/development_baseline/tests/test_install_contract.py',
        'engineering/development_baseline/tests/test_readme_context.py',
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

    def check(self, *, historical=None, shared=None, current=None, archive=None):
        validate(self.historical if historical is None else historical,
                 self.shared if shared is None else shared,
                 self.current if current is None else current,
                 self.archive if archive is None else archive)

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

    def test_current_source_cannot_be_pinned(self):
        shared = self.shared.replace('      - uses: actions/checkout@v4',
            '      - uses: actions/checkout@v4\n        with:\n          ref: ' + self.archive['revision'], 1)
        with self.assertRaises(AssertionError):
            self.check(shared=shared)

    def test_historical_coverage_cannot_be_removed(self):
        with self.assertRaises(AssertionError):
            self.check(historical=self.historical.replace(
                'python tools/automation/capabilities.py --check', 'true'))

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
                     'engineering/development_baseline/**'):
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
        with self.assertRaises(AssertionError):
            self.check(current=self.current.replace('needs: [current-contracts]', 'needs: []'))


if __name__ == '__main__':
    unittest.main()
