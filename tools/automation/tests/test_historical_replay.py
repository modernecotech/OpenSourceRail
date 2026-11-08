#!/usr/bin/env python3
"""Bounded output-ownership tests; no native program or network is executed."""
import ast
from hashlib import sha256
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[3]
HELPER = ROOT / 'tools/automation/prepare-historical-replay.py'
SPEC = importlib.util.spec_from_file_location('historical_replay', HELPER)
REPLAY = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(REPLAY)
WORKFLOW = ROOT / '.github/workflows/historical-v05.yml'


def city_publication_views(text):
    """Both unchanged archived validators must run in their own publication view."""
    steps = re.split(r'(?=^      - (?:name|uses|run):)', text, flags=re.M)
    def step(name):
        found = [s for s in steps if s.startswith('      - name: '+name+'\n')]
        assert len(found) == 1, name
        value = found[0]
        assert not re.search(r'^        (?:if|continue-on-error):', value, re.M)
        assert '        shell: bash\n' in value
        assert 'set +e' not in value and '|| true' not in value
        return value
    before = step('Validate pristine pinned comfort navigation before replay')
    after = step('Verify regenerated historical maglev city publication')
    check = 'python tools/automation/check-readmes.py'
    assert text.count(check) == 1
    assert check+' 2>&1 | tee build/historical-pinned-comfort-readmes.log' in before
    assert 'test "$(git rev-parse HEAD)" = '+REPLAY.PIN in before
    assert before.count('git diff --exit-code HEAD -- .') == 2
    assert before.index('git diff --exit-code HEAD -- .') < before.index(check) < before.rindex('git diff --exit-code HEAD -- .')
    preparation = text.index('python ../current/tools/automation/prepare-historical-replay.py --repository')
    cycle = text.index('python tools/automation/ferrite-maglev-study.py cycle')
    assert text.index(before) < preparation < cycle < text.index(after)
    assert text.index(after) < text.index('python tools/automation/capabilities.py --check')
    assert "python - <<'PYTHON' 2>&1 | tee build/historical-regenerated-maglev-cities.log" in after
    assert 'value = cities.verify_index()' in after
    assert "assert value['current'], value['errors']" in after
    assert "assert value['city_count'] == value['expected_city_count'] == 266" in after
    assert "view='regenerated historical maglev publication'" in after
    for name in ('historical-pinned-comfort-readmes.log', 'historical-regenerated-maglev-cities.log'):
        assert 'historical/build/'+name in text
    assert '      - name: Preserve historical replay logs and reports\n' in text
    assert '        if: always()\n' in text
    return before, after


class HistoricalCityViewOrderTests(unittest.TestCase):
    def setUp(self):
        self.text = WORKFLOW.read_text()

    def test_pinned_comfort_and_regenerated_maglev_validators_have_separate_ordered_views(self):
        city_publication_views(self.text)
        self.assertIn('Run 42470979160 exposed incompatible archived front-page owners', self.text)

    def test_comfort_check_cannot_move_after_publication_preparation(self):
        before, _ = city_publication_views(self.text)
        late = self.text.replace(before, '', 1)
        cycle_header = '      - name: Prepare runtime-bound publication and reader\n'
        late = late.replace(cycle_header, before+cycle_header, 1)
        with self.assertRaises(AssertionError):
            city_publication_views(late)

    def test_original_checker_cannot_be_removed_or_repeated_on_incompatible_postcycle_view(self):
        for changed in (self.text.replace('python tools/automation/check-readmes.py', 'true'),
                        self.text.replace('          python tools/automation/capabilities.py --check',
                            '          python tools/automation/check-readmes.py\n          python tools/automation/capabilities.py --check')):
            with self.subTest(changed=changed), self.assertRaises(AssertionError):
                city_publication_views(changed)

    def test_maglev_errors_counts_and_unconditional_steps_cannot_be_relaxed(self):
        for old,new in (("assert value['current'], value['errors']", 'pass'),
                        ("assert value['city_count'] == value['expected_city_count'] == 266", 'pass'),
                        ('      - name: Verify regenerated historical maglev city publication\n',
                         '      - name: Verify regenerated historical maglev city publication\n        continue-on-error: true\n'),
                        ('      - name: Validate pristine pinned comfort navigation before replay\n',
                         '      - name: Validate pristine pinned comfort navigation before replay\n        if: false\n')):
            with self.subTest(old=old), self.assertRaises(AssertionError):
                city_publication_views(self.text.replace(old,new,1))

    def test_both_view_logs_must_be_retained_on_failure(self):
        for name in ('historical-pinned-comfort-readmes.log', 'historical-regenerated-maglev-cities.log'):
            with self.subTest(name=name), self.assertRaises(AssertionError):
                city_publication_views(self.text.replace('            historical/build/'+name+'\n', '', 1))

    def test_view_verifier_failures_survive_tee_and_retain_actual_stdout(self):
        before,after = city_publication_views(self.text)
        for index,step in enumerate((before,after)):
            with self.subTest(view=index), tempfile.TemporaryDirectory(prefix='osr-city-view-shell-') as directory:
                root=Path(directory);(root/'bin').mkdir();(root/'build').mkdir()
                git=root/'bin/git';git.write_text('#!/bin/sh\nif [ "$1" = rev-parse ]; then printf "%s\\n" '+REPLAY.PIN+'; fi\n')
                python=root/'bin/python';python.write_text('#!/bin/sh\necho actual-view-verifier-failure\nexit 9\n')
                for executable in (git,python):executable.chmod(0o700)
                body=step.split('        run: |\n',1)[1]
                body='\n'.join(line[10:] if line.startswith('          ') else line for line in body.splitlines())
                result=subprocess.run(['bash','-eo','pipefail','-c',body],cwd=root,
                    env=dict(os.environ,PATH=str(root/'bin')+os.pathsep+os.environ['PATH']),
                    capture_output=True,text=True,timeout=5)
                self.assertEqual(result.returncode,9,result.stderr)
                name=('historical-pinned-comfort-readmes.log','historical-regenerated-maglev-cities.log')[index]
                self.assertEqual((root/'build'/name).read_text(),'actual-view-verifier-failure\n')


class HistoricalReplayTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='osr-historical-retention-test-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.packet = self.root / REPLAY.PACKET
        self.packet.mkdir(parents=True)
        subprocess.run(['git', 'init', '--quiet', str(self.root)], check=True)
        (self.root / 'VERSION').write_text('0.5\n')
        self.original = {n: ('historical fixture ' + n).encode()
                         for n in REPLAY.FILES if n != 'manifest.json'}
        manifest = dict(schema='osr-maglev-pilot-lifecycle/1',
                        files_sha256={n: sha256(b).hexdigest() for n, b in self.original.items()},
                        **{flag: False for flag in REPLAY.FLAGS})
        self.original['manifest.json'] = (json.dumps(manifest) + '\n').encode()
        for name, raw in self.original.items():
            (self.packet / name).write_bytes(raw)
        subprocess.run(['git', '-C', str(self.root), 'add', '.'], check=True)
        tree = subprocess.check_output(['git', '-C', str(self.root), 'write-tree']).decode().strip()
        revision = subprocess.check_output(['git', '-C', str(self.root), '-c', 'user.name=Fixture',
                    '-c', 'user.email=fixture@example.invalid', 'commit-tree', tree, '-m', 'isolated test fixture']).decode().strip()
        subprocess.run(['git', '-C', str(self.root), 'update-ref', 'HEAD', revision], check=True)
        self.pin = patch.object(REPLAY, 'PIN', revision)
        self.pin.start()
        self.addCleanup(self.pin.stop)
        contract = dict(schema='osr-v05-git-archive/1', revision=revision, physical_accepted=False)
        raw = (json.dumps(contract, sort_keys=True, separators=(',', ':')) + '\n').encode()
        contract['archive_id'] = sha256(raw).hexdigest()
        self.contract = self.root / 'archive-contract.json'
        self.contract.write_text(json.dumps(contract))
        self.output = self.root / 'build/retained'
        self.raw_native = self.root / 'engineering/assurance/v052-pilot-lifecycle-native/manifest.json'
        self.raw_native.parent.mkdir(parents=True)
        self.raw_native.write_text('independent immutable native receipt\n')

    def prepare(self):
        return REPLAY.prepare(self.root, self.contract, self.output)

    def assert_untouched(self):
        self.assertTrue(self.packet.is_dir())
        for name, raw in self.original.items():
            self.assertEqual((self.packet / name).read_bytes(), raw)
        self.assertFalse(self.output.exists())

    def test_exact_old_thirteen_files_are_retained_without_touching_raw_native_evidence(self):
        report = self.prepare()
        self.assertFalse(self.packet.exists())
        self.assertEqual(report['retained_files'], 13)
        self.assertFalse(report['native_receipts_modified'])
        self.assertFalse(report['physical_accepted'])
        self.assertTrue(report['original_staging_install_guard_unchanged'])
        for name, raw in self.original.items():
            self.assertEqual((self.output / 'pilot-lifecycle' / name).read_bytes(), raw)
        self.assertEqual(self.raw_native.read_text(), 'independent immutable native receipt\n')
        self.assertEqual(json.loads((self.output / 'retention.json').read_text()), report)

    def test_unowned_file_is_rejected_before_any_move(self):
        note = self.packet / 'personal-notes.txt'
        note.write_text('preserve')
        with self.assertRaisesRegex(ValueError, 'Unowned or missing'):
            self.prepare()
        self.assert_untouched()
        self.assertEqual(note.read_text(), 'preserve')

    def test_tampered_known_file_is_rejected_before_any_move(self):
        (self.packet / 'native-workbench.png').write_bytes(b'changed')
        with self.assertRaisesRegex(ValueError, 'bytes differ'):
            self.prepare()
        self.assertTrue(self.packet.is_dir())
        self.assertFalse(self.output.exists())
        self.assertEqual((self.packet / 'native-workbench.png').read_bytes(), b'changed')

    def test_existing_nonempty_destination_is_preserved(self):
        self.output.mkdir(parents=True)
        note = self.output / 'existing.txt'
        note.write_text('preserve')
        with self.assertRaisesRegex(ValueError, 'Fresh retained-output'):
            self.prepare()
        self.assertTrue(self.packet.is_dir())
        self.assertEqual(note.read_text(), 'preserve')

    def test_packet_link_is_rejected_without_changing_external_bytes(self):
        external = self.root / 'external'
        self.packet.rename(external)
        self.packet.symlink_to(external, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, 'Ordinary complete'):
            self.prepare()
        self.assertFalse(self.output.exists())
        for name, raw in self.original.items():
            self.assertEqual((external / name).read_bytes(), raw)

    def test_wrong_pin_or_contract_is_rejected(self):
        with patch.object(REPLAY, 'PIN', '0' * 40):
            with self.assertRaisesRegex(ValueError, 'Exact v0.5'):
                self.prepare()
        value = json.loads(self.contract.read_text())
        value['physical_accepted'] = True
        self.contract.write_text(json.dumps(value))
        with self.assertRaisesRegex(ValueError, 'archive contract'):
            self.prepare()
        self.assert_untouched()

    def test_original_pinned_install_guard_accepts_fresh_hold_and_rejects_unknown_files(self):
        # Execute only the unchanged install_packet function from the actual
        # immutable Git source, with fixture files. No engineering imports/solves.
        source = subprocess.check_output(['git', '-C', str(ROOT), 'show',
            '92e1385e03dcd5c6f76a5b0a9dd5ba348f50d164:engineering/ferrite_maglev/workflow.py'], text=True)
        definition = next(node for node in ast.parse(source).body
                          if isinstance(node, ast.FunctionDef) and node.name == 'install_packet')
        namespace = {}
        exec('from pathlib import Path\nimport os\n', namespace)
        exec(compile(ast.Module(body=[definition], type_ignores=[]), '<exact-v05-install_packet>', 'exec'), namespace)
        install = namespace['install_packet']
        staging = self.root / 'staging'
        staging.mkdir()
        for name in REPLAY.FILES - {'native-workbench.png', 'native-fuxa.png'}:
            (staging / name).write_bytes(b'fresh explicit hold fixture')
        with self.assertRaisesRegex(ValueError, 'unexpected files'):
            install(staging, self.packet)
        self.prepare()
        install(staging, self.packet)
        self.assertEqual({p.name for p in self.packet.iterdir()},
                         REPLAY.FILES - {'native-workbench.png', 'native-fuxa.png'})
        self.assertTrue((self.output / 'pilot-lifecycle/native-workbench.png').is_file())
        (self.packet / 'unowned.txt').write_text('preserve')
        with self.assertRaisesRegex(ValueError, 'unexpected files'):
            install(self.output / 'pilot-lifecycle', self.packet)
        self.assertEqual((self.packet / 'unowned.txt').read_text(), 'preserve')


if __name__ == '__main__':
    unittest.main()
