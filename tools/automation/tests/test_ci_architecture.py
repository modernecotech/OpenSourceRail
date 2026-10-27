#!/usr/bin/env python3
"""Guard CI source routing: frozen v0.5 replay and current shared regressions."""
from copy import deepcopy
from hashlib import sha256
from fnmatch import fnmatchcase
import json
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
    assert set(path_filters) == {'.github/workflows/historical-v05.yml', 'docs/archives/v0.5-maglev/**'}
    assert len(path_filters) == 4  # Same narrow push and PR filters.
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
                     'engineering/development_baseline/**'):
            with self.subTest(path=path):
                with self.assertRaises(AssertionError):
                    # Removing only the PR entry must fail even when main pushes still cover it.
                    self.check(current=self.current.replace('      - "' + path + '"\n', '', 1))

    def test_required_current_release_gate_cannot_be_removed(self):
        with self.assertRaises(AssertionError):
            self.check(current=self.current.replace('needs: [current-contracts]', 'needs: []'))


if __name__ == '__main__':
    unittest.main()
