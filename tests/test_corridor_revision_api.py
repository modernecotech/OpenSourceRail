"""Comparison reuse consumes verified artifacts, not retained status hints."""
import json
from pathlib import Path
from threading import RLock

from engineering.outline import city_jobs, corridor_revision


def test_comparison_cache_cannot_be_retargeted_by_status_hints(monkeypatch):
    service = city_jobs.CityStudyService.__new__(city_jobs.CityStudyService)
    service.root = Path('/unused-test-source')
    service.lock = RLock()
    service._poll = lambda job: dict(state='completed', manifest_id='forged-status-hint')
    calls = []

    def artifact(job, name):
        value = {'manifest_id': 'verified-' + job} if name == 'manifest.json' else {'job': job}
        return json.dumps(value).encode()

    def compare(proposal, before, after, bm, am, **kwargs):
        calls.append((before['job'], after['job']))
        return dict(before=bm['manifest_id'], after=am['manifest_id'])

    service.artifact = artifact
    monkeypatch.setattr(corridor_revision, 'proposal', lambda root: {'proposal_id': 'fixed'})
    monkeypatch.setattr(corridor_revision, 'compare', compare)
    first = service.corridor_comparison('a'*32, 'b'*32)
    second = service.corridor_comparison('c'*32, 'd'*32)
    assert first['report'] != second['report']
    assert second['jobs']['before']['manifest_id'] == 'verified-' + 'c'*32
    assert second['jobs']['before']['job_id'] == 'c'*32
    assert len(calls) == 2
    again = service.corridor_comparison('c'*32, 'd'*32)
    assert again['report'] == second['report'] and again['cache_hit'] is True
    assert len(calls) == 2


def test_equivalent_artifacts_keep_their_own_job_download_links(monkeypatch):
    service = city_jobs.CityStudyService.__new__(city_jobs.CityStudyService)
    service.root = Path('/unused-test-source'); service.lock = RLock()
    service._poll = lambda job: dict(state='completed', manifest_id='same')
    service.artifact = lambda job, name: json.dumps({'manifest_id': 'same'}).encode()
    monkeypatch.setattr(corridor_revision, 'proposal', lambda root: {'proposal_id': 'fixed'})
    monkeypatch.setattr(corridor_revision, 'compare', lambda *args, **kwargs: {'comparison_id': 'same'})
    service.corridor_comparison('a'*32, 'b'*32)
    other = service.corridor_comparison('c'*32, 'd'*32)
    assert other['jobs']['before']['job_id'] == 'c'*32
    assert other['jobs']['after']['job_id'] == 'd'*32
