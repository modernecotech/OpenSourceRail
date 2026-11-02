#!/usr/bin/env python3
"""Keep generated navigation stable when a checkout omits tracked Markdown."""

import importlib.util
import os
from pathlib import Path
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[3]
SCRIPT = ROOT / 'tools/automation/generate-doc-index.py'


class DocumentIndexTests(unittest.TestCase):
    def test_dependency_markdown_is_excluded_while_project_drafts_are_discoverable(self):
        with tempfile.TemporaryDirectory(prefix='osr-doc-index-') as directory:
            root=Path(directory)
            subprocess.run(['git','init','-q'],cwd=root,check=True)
            dependency=root/'.venv-search/lib/python3.12/site-packages/package/LICENSE.md'
            dependency.parent.mkdir(parents=True)
            dependency.write_text('# Third-party dependency license\n')
            draft=root/'docs/draft.md';draft.parent.mkdir();draft.write_text('# Project draft\n')
            spec=importlib.util.spec_from_file_location('osr_doc_index_environment',SCRIPT)
            indexer=importlib.util.module_from_spec(spec);spec.loader.exec_module(indexer)
            indexer.REPO_ROOT=root
            result=indexer.generate()
            self.assertIn('Project draft',result)
            self.assertNotIn('Third-party dependency',result)
            self.assertNotIn('.venv-search',result)
            # Exercise Git's ignored-file boundary as well as the shared policy.
            (root/'.gitignore').write_text((ROOT/'.gitignore').read_text())
            self.assertEqual(subprocess.run(['git','check-ignore','-q',str(dependency.relative_to(root))],cwd=root).returncode,0)
            self.assertIn('Project draft',indexer.generate())

    def test_sparse_checkout_indexes_tracked_source_title(self):
        with tempfile.TemporaryDirectory(prefix='osr-doc-index-') as directory:
            root = Path(directory)
            subprocess.run(['git', 'init', '-q'], cwd=root, check=True)
            source = root / 'CHANGELOG.md'
            source.write_text('# Sparse checkout changelog\n')
            subprocess.run(['git', 'add', 'CHANGELOG.md'], cwd=root, check=True)
            environment = dict(os.environ, GIT_AUTHOR_NAME='OpenSourceRail test',
                               GIT_AUTHOR_EMAIL='test@example.invalid',
                               GIT_COMMITTER_NAME='OpenSourceRail test',
                               GIT_COMMITTER_EMAIL='test@example.invalid')
            subprocess.run(['git', 'commit', '-qm', 'Add changelog'], cwd=root,
                           env=environment, check=True)
            source.unlink()

            spec = importlib.util.spec_from_file_location('osr_doc_index', SCRIPT)
            indexer = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(indexer)
            indexer.REPO_ROOT = root

            tracked = Path('CHANGELOG.md')
            self.assertTrue(indexer._indexed(tracked))
            self.assertEqual(indexer._title(tracked), 'Sparse checkout changelog')
            self.assertIn('CHANGELOG.md', indexer.generate())


if __name__ == '__main__':
    unittest.main()
