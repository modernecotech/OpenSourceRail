#!/usr/bin/env python3
"""Tamper and source-routing controls for historical publication replay."""
from hashlib import sha256
import importlib.util
import json
import os
from pathlib import Path
import tempfile
import subprocess
import sys
import unittest
from unittest.mock import patch

TOOLS = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('research_snapshot', TOOLS / 'verify-research-snapshot.py')
snapshot = importlib.util.module_from_spec(spec)
spec.loader.exec_module(snapshot)


class SnapshotTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix='osr-source-guard-test-')
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.repo, self.current = self.root/'historical', self.root/'current'
        self.repo.mkdir(); self.current.mkdir()
        (self.repo/'source.py').write_text('recorded evaluator\n')
        (self.repo/'packet/nested').mkdir(parents=True)
        (self.repo/'packet/data.json').write_text('{}\n')
        (self.repo/'packet/nested/manifest.json').write_text('{"nested":true}\n')
        self.manifest = dict(source_sha256={'source.py':sha256((self.repo/'source.py').read_bytes()).hexdigest()},
            files_sha256={n:sha256((self.repo/'packet'/n).read_bytes()).hexdigest()
                          for n in ('data.json','nested/manifest.json')},
            physical_accepted=False, engineering_accepted=False, configuration_adopted=False)
        self.write_manifest()
        self.addCleanup(patch.stopall)
        patch.object(snapshot, 'PACKETS', {'fixture':('packet','a'*40)}).start()
        self.revision = patch.object(snapshot, 'revision', return_value='a'*40).start()
        self.blob = patch.object(snapshot, 'committed_receipt', return_value=(self.repo/'packet/manifest.json').read_bytes()).start()

    def write_manifest(self):
        self.manifest.pop('publication_id', None)
        self.manifest['publication_id'] = sha256((json.dumps(self.manifest,sort_keys=True,separators=(',',':'))+'\n').encode()).hexdigest()
        for root in (self.repo,self.current):
            (root/'packet').mkdir(exist_ok=True)
            (root/'packet/manifest.json').write_text(json.dumps(self.manifest,sort_keys=True)+'\n')

    def check(self):
        return snapshot.verify('fixture',self.repo,self.current)

    def test_exact_sources_and_nested_payloads_pass_without_writing(self):
        before={p: p.read_bytes() for root in (self.repo,self.current) for p in root.rglob('*') if p.is_file()}
        result=self.check()
        self.assertEqual(result['source_files'],1)
        self.assertEqual(result['payload_files'],2)
        self.assertFalse(result['physical_accepted'])
        self.assertEqual(before,{p:p.read_bytes() for p in before})

    def test_resealing_both_receipts_cannot_change_the_git_archive(self):
        self.manifest['extra']='rehashed claim';self.write_manifest()
        with self.assertRaisesRegex(ValueError,'immutable historical source'):self.check()

    def test_original_trip_schema_uses_committed_receipt_and_campaign_identity(self):
        self.manifest.update(schema='osr-trip-publication/1',campaign_id='c'*64)
        self.write_manifest();self.blob.return_value=(self.repo/'packet/manifest.json').read_bytes()
        with patch.dict(snapshot.PACKETS,{'trip-dynamics':('packet','a'*40)}):
            result=snapshot.verify('trip-dynamics',self.repo,self.current)
            self.assertEqual(result['source_files'],1)
            self.assertTrue(result['original_semantic_verifier_required'])
            self.assertFalse(result['physical_accepted'])

    def test_original_trip_schema_requires_a_full_campaign_identity(self):
        self.manifest.update(schema='osr-trip-publication/1',campaign_id='invalid')
        self.write_manifest();self.blob.return_value=(self.repo/'packet/manifest.json').read_bytes()
        with patch.dict(snapshot.PACKETS,{'trip-dynamics':('packet','a'*40)}):
            with self.assertRaisesRegex(ValueError,'schema/campaign identity required'):
                snapshot.verify('trip-dynamics',self.repo,self.current)

    def test_wrong_revision_is_rejected(self):
        self.revision.return_value='b'*40
        with self.assertRaisesRegex(ValueError,'originating revision'):self.check()

    def test_changed_source_is_rejected(self):
        (self.repo/'source.py').write_text('changed evaluator\n')
        with self.assertRaisesRegex(ValueError,'source bytes differ'):self.check()

    def test_changed_payload_is_rejected(self):
        (self.repo/'packet/data.json').write_text('{"changed":true}')
        with self.assertRaisesRegex(ValueError,'payload bytes differ'):self.check()

    def test_extra_payload_is_rejected(self):
        (self.repo/'packet/extra.json').write_text('{}')
        with self.assertRaisesRegex(ValueError,'inventory differs'):self.check()

    def test_changed_current_receipt_is_rejected(self):
        (self.current/'packet/manifest.json').write_text('{}')
        with self.assertRaisesRegex(ValueError,'receipt differs'):self.check()

    def test_unsafe_source_path_is_rejected(self):
        self.manifest['source_sha256']={'../escape.py':'a'*64};self.write_manifest()
        self.blob.return_value=(self.repo/'packet/manifest.json').read_bytes()
        with self.assertRaisesRegex(ValueError,'relative evidence path'):self.check()

    def test_symlinked_source_is_rejected(self):
        (self.root/'outside.py').write_text('recorded evaluator\n')
        (self.repo/'source.py').unlink();(self.repo/'source.py').symlink_to(self.root/'outside.py')
        with self.assertRaisesRegex(ValueError,'Linked evidence'):self.check()

    def test_rehashed_physical_acceptance_is_rejected(self):
        self.manifest['physical_accepted']=True;self.write_manifest()
        self.blob.return_value=(self.repo/'packet/manifest.json').read_bytes()
        with self.assertRaisesRegex(ValueError,'cannot assert'):self.check()

    def test_missing_source_inventory_is_rejected(self):
        self.manifest['source_sha256']={};self.write_manifest()
        self.blob.return_value=(self.repo/'packet/manifest.json').read_bytes()
        with self.assertRaisesRegex(ValueError,'inventories required'):self.check()


class GuardFailureArtifactTests(unittest.TestCase):
    def test_failed_cli_guard_retains_a_held_report(self):
        with tempfile.TemporaryDirectory() as directory:
            output=Path(directory)/'guard.json'
            result=subprocess.run([sys.executable,str(TOOLS/'verify-research-snapshot.py'),
                '--packet','vehicle-optimisation','--repository',directory,'--receipt-root',directory,
                '--output',str(output)],capture_output=True,text=True)
            self.assertNotEqual(result.returncode,0)
            record=json.loads(output.read_text())
            self.assertEqual(record['execution'],'held')
            self.assertFalse(record['source_and_payload_bytes_verified'])
            self.assertFalse(record['physical_accepted'])


class OfficialBundleTests(unittest.TestCase):
    def test_wrong_bundle_hash_is_refused_before_any_execution_or_install(self):
        spec=importlib.util.spec_from_file_location('historical_install', TOOLS/'install-historical-freecad.py')
        installer=importlib.util.module_from_spec(spec);spec.loader.exec_module(installer)
        self.assertEqual(installer.SHA256,'f6dc6ba676e5ac96a565ebc8d657232f94c6158e85b4352141bd1a46f6b43434')
        with tempfile.TemporaryDirectory() as directory:
            archive=Path(directory)/'unverified.AppImage';archive.write_bytes(b'not an official bundle')
            destination=Path(directory)/'install'
            with patch.object(installer.subprocess,'run') as execute:
                with self.assertRaisesRegex(ValueError,'SHA256 differs'):
                    installer.install(archive,destination)
                execute.assert_not_called()
                self.assertFalse(destination.exists())


class NativeDependencyTests(unittest.TestCase):
    def test_absent_direct_freecad_is_refused_before_flatpak_fallback(self):
        spec = importlib.util.spec_from_file_location('historical_preflight', TOOLS / 'historical-native-preflight.py')
        preflight = importlib.util.module_from_spec(spec);spec.loader.exec_module(preflight)
        with tempfile.TemporaryDirectory() as directory:
            with patch.object(preflight.shutil, 'which', return_value=None):
                with self.assertRaisesRegex(ValueError, 'Direct FreeCADCmd/freecadcmd required'):
                    preflight.run(Path(directory) / 'preflight.json')
            record=json.loads((Path(directory)/'preflight.json').read_text())
            self.assertEqual(record['execution'],'held')
            self.assertFalse(record['physical_accepted'])


    def test_missing_freecad_cli_exits_nonzero_with_a_held_report(self):
        with tempfile.TemporaryDirectory() as directory:
            output=Path(directory)/'preflight.json'
            result=subprocess.run([sys.executable,str(TOOLS/'historical-native-preflight.py'),
                '--output',str(output)],env=dict(os.environ,PATH=directory),capture_output=True,text=True)
            self.assertNotEqual(result.returncode,0)
            report=json.loads(output.read_text())
            self.assertEqual(report['execution'],'held')
            self.assertFalse(report['physical_accepted'])


if __name__ == '__main__':unittest.main()
