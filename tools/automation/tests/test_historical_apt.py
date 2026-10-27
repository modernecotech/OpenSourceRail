#!/usr/bin/env python3
"""Exercise runner source routing using temporary fixtures, without APT/network."""
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import stat
import subprocess
import sys
import tempfile
import unittest

HELPER = Path(__file__).resolve().parents[1] / 'configure-historical-apt.py'
SPEC = importlib.util.spec_from_file_location('historical_apt', HELPER)
APT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(APT)
AZURE = 'http://azure.archive.ubuntu.com/ubuntu/'
OFFICIAL = 'https://archive.ubuntu.com/ubuntu/'


class HistoricalAptSourceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='osr-apt-source-fixture-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.apt = self.root / 'apt'
        self.apt.mkdir()
        self.audit = self.root / 'audit'

    def write(self, name, text):
        path = self.apt / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(text.encode())
        return path

    def test_deb822_changes_only_uri_tokens_and_preserves_security_and_signing(self):
        source = (
            '# ' + AZURE + ' is an explanatory comment\n'
            'Types: deb deb-src\nURIs: ' + AZURE + '\n'
            ' https://azure.archive.ubuntu.com/ubuntu https://security.ubuntu.com/ubuntu/\n'
            'Suites: noble noble-updates noble-backports\nComponents: main restricted universe multiverse\n'
            'Architectures: amd64\nSigned-By: /usr/share/keyrings/ubuntu-archive-keyring.gpg\n'
            'Enabled: yes\n\nTypes: deb\nURIs: https://security.ubuntu.com/ubuntu/\n'
            'Suites: noble-security\nComponents: main universe\n'
            'Signed-By:\n -----BEGIN PGP PUBLIC KEY BLOCK-----\n .\n ' + AZURE + '\n'
            ' -----END PGP PUBLIC KEY BLOCK-----\n')
        path = self.write('sources.list.d/ubuntu.sources', source)
        path.chmod(0o640)
        expected = source.replace('URIs: ' + AZURE, 'URIs: ' + OFFICIAL).replace(
            ' https://azure.archive.ubuntu.com/ubuntu https://security',
            ' https://archive.ubuntu.com/ubuntu https://security')
        result = APT.configure(self.apt, self.audit)
        self.assertEqual(path.read_text(), expected)
        self.assertEqual(stat.S_IMODE(path.stat().st_mode), 0o640)
        self.assertEqual(result['changed_sources'], ['sources.list.d/ubuntu.sources'])
        self.assertFalse(result['inherited_rate_cap_established'])
        self.assertFalse(result['physical_accepted'])
        record = result['sources']['sources.list.d/ubuntu.sources']
        self.assertEqual(record['original_sha256'], sha256(source.encode()).hexdigest())
        self.assertEqual(record['effective_sha256'], sha256(expected.encode()).hexdigest())
        self.assertEqual((self.audit / 'original/sources.list.d/ubuntu.sources').read_text(), source)
        self.assertEqual((self.audit / 'effective/sources.list.d/ubuntu.sources').read_text(), expected)
        self.assertEqual(json.loads((self.audit / 'manifest.json').read_text()), result)

    def test_noble_mirror_indirection_keeps_all_priorities_and_security_lines(self):
        source = 'Types: deb\nURIs: mirror+file:/etc/apt/apt-mirrors.txt\nSuites: noble noble-updates\nComponents: main universe\nSigned-By: /usr/share/keyrings/ubuntu-archive-keyring.gpg\n'
        mirrors = AZURE + '\tpriority:1\n' + OFFICIAL + '\tpriority:2\nhttps://security.ubuntu.com/ubuntu/\tpriority:3\n'
        self.write('sources.list.d/ubuntu.sources', source)
        self.write('apt-mirrors.txt', mirrors)
        result = APT.configure(self.apt, self.audit)
        self.assertEqual((self.apt / 'sources.list.d/ubuntu.sources').read_text(), source)
        self.assertEqual((self.apt / 'apt-mirrors.txt').read_text(), mirrors.replace(AZURE, OFFICIAL))
        self.assertEqual(result['changed_sources'], ['apt-mirrors.txt'])

    def test_legacy_options_comments_and_third_party_sources_remain_exact(self):
        source = '# deb ' + AZURE + ' noble main\n' + 'deb [arch=amd64 signed-by=/keyring] ' + AZURE + ' noble main universe # ' + AZURE + '\n' + 'deb-src https://azure.archive.ubuntu.com/ubuntu noble main\ndeb https://security.ubuntu.com/ubuntu/ noble-security main\n'
        unrelated = 'deb ' + AZURE + ' research main\n'
        self.write('sources.list', source)
        self.write('sources.list.d/vendor.list', unrelated)
        result = APT.configure(self.apt, self.audit)
        expected = source.replace('signed-by=/keyring] ' + AZURE, 'signed-by=/keyring] ' + OFFICIAL).replace(
            'deb-src https://azure.archive.ubuntu.com/ubuntu ', 'deb-src https://archive.ubuntu.com/ubuntu ')
        self.assertEqual((self.apt / 'sources.list').read_text(), expected)
        self.assertEqual((self.apt / 'sources.list.d/vendor.list').read_text(), unrelated)
        self.assertFalse(result['sources']['sources.list.d/vendor.list']['changed'])
        self.assertEqual((self.audit / 'original/sources.list.d/vendor.list').read_text(), unrelated)

    def test_lookalikes_are_not_rewritten_and_repeat_is_audited_noop(self):
        source = 'deb https://azure.archive.ubuntu.com.evil.test/ubuntu/ noble main\ndeb http://azure.archive.ubuntu.com/ubuntu/other noble main\n'
        self.write('sources.list', source)
        result = APT.configure(self.apt, self.audit)
        self.assertEqual(result['changed_sources'], [])
        self.assertEqual((self.apt / 'sources.list').read_text(), source)
        APT.configure(self.apt, self.root / 'audit-2')
        with self.assertRaises(ValueError):
            APT.configure(self.apt, self.audit)

    def test_linked_source_is_rejected_before_any_source_mutation(self):
        path = self.write('sources.list', 'deb ' + AZURE + ' noble main\n')
        external = self.root / 'external'
        external.write_text('deb ' + AZURE + ' noble main\n')
        (self.apt / 'apt-mirrors.txt').symlink_to(external)
        before = path.read_bytes()
        with self.assertRaisesRegex(ValueError, 'Linked APT'):
            APT.configure(self.apt, self.audit)
        self.assertEqual(path.read_bytes(), before)
        self.assertEqual(external.read_text(), 'deb ' + AZURE + ' noble main\n')
        self.assertFalse(self.audit.exists())

    def test_linked_source_directory_and_nested_audit_are_rejected(self):
        external = self.root / 'external'
        external.mkdir()
        (self.apt / 'sources.list.d').symlink_to(external, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, 'Linked APT source directory'):
            APT.configure(self.apt, self.audit)
        (self.apt / 'sources.list.d').unlink()
        self.write('sources.list', 'deb ' + AZURE + ' noble main\n')
        with self.assertRaisesRegex(ValueError, 'outside APT root'):
            APT.configure(self.apt, self.apt / 'audit')

    def test_cli_requires_explicit_apt_root_and_has_no_host_default(self):
        result = subprocess.run([sys.executable, str(HELPER), '--output', str(self.audit)],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)
        self.assertIn('--apt-root', result.stderr)
        self.assertFalse(self.audit.exists())

    def test_cli_routes_only_its_explicit_fixture_and_writes_audit(self):
        source = 'deb ' + AZURE + ' noble main\n'
        self.write('sources.list', source)
        result = subprocess.run([sys.executable, str(HELPER), '--apt-root', str(self.apt),
                                 '--output', str(self.audit)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)['changed_sources'], ['sources.list'])
        self.assertEqual((self.apt / 'sources.list').read_text(), source.replace(AZURE, OFFICIAL))
        self.assertEqual((self.audit / 'original/sources.list').read_text(), source)


if __name__ == '__main__':
    unittest.main()
