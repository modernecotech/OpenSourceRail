"""Archived code verification must not silently qualify current implementations."""
from pathlib import Path
import runpy
import pytest

ROOT=Path(__file__).resolve().parents[3]
API=runpy.run_path(str(ROOT/'tools/automation/verify-shared-review-history.py'))


def test_archived_publication_matches_its_producing_commit_without_current_qualification():
    r=API['verify'](ROOT/'engineering/civil_exploration/examples/shared-spatial-engineering-review.json','bcb21593fb')
    assert r['published_sources_verified'] and r['source_count']>0
    assert not r['current_solver_qualified'] and not r['bulk_campaign_outputs_verified']
    assert not r['physical_validation'] and not r['engineering_released']


def test_repository_escape_and_external_review_are_rejected(tmp_path):
    with pytest.raises(ValueError,match='repository-relative'):API['git_file']('bcb21593fb','../outside.py')
    with pytest.raises(ValueError,match='inside'):API['verify'](tmp_path/'review.json','bcb21593fb')
