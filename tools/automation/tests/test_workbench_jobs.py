"""Project-twin outcomes survive reload and interrupted work retains its original record."""
import importlib.util
import json
from pathlib import Path

MODULE=Path(__file__).resolve().parents[1]/'workbench_jobs.py'
spec=importlib.util.spec_from_file_location('durable_city_jobs',MODULE)
jobs=importlib.util.module_from_spec(spec);spec.loader.exec_module(jobs)


def test_city_job_reload_keeps_terminal_summary_and_interrupted_request(tmp_path,monkeypatch):
    design=tmp_path/'cities/catalogue/west-asia/Iraq/Samawah/design.toml'
    design.parent.mkdir(parents=True);design.write_text('[city]\nslug="samawah"\n')
    monkeypatch.setattr(jobs.threading.Thread,'start',lambda self:None)
    first=jobs.ProjectTwinManager(tmp_path);queued=first.start('samawah')
    first._update(queued['id'],owner_pid=99999999)
    restarted=jobs.ProjectTwinManager(tmp_path)
    record=restarted.job(queued['id'])
    assert record['status']=='interrupted' and record['design_sha256']==queued['design_sha256']
    restarted._update(queued['id'],status='completed',summary={'revision_id':'fixture-history'},physical_release=False)
    third=jobs.ProjectTwinManager(tmp_path)
    assert third.job(queued['id'])['summary']=={'revision_id':'fixture-history'}
    assert third.jobs('mosul')==[]
    assert third.jobs('samawah')[0]['physical_release']is False


def test_missing_proc_keeps_queued_city_owner_across_reload(tmp_path, monkeypatch):
    from engineering.design_engine import store
    design = tmp_path / 'cities/catalogue/west-asia/Iraq/Samawah/design.toml'
    design.parent.mkdir(parents=True)
    design.write_text('[city]\nslug="samawah"\n')
    monkeypatch.setattr(jobs.threading.Thread, 'start', lambda self: None)
    def missing(_pid):
        raise FileNotFoundError('procfs unavailable')
    monkeypatch.setattr(store, '_process_stat', missing)
    first = jobs.ProjectTwinManager(tmp_path)
    queued = first.start('samawah')
    assert queued['owner_process_start'].startswith('local:')
    second = jobs.ProjectTwinManager(tmp_path)
    assert second.job(queued['id'])['status'] == 'queued'
    assert second.start('samawah')['id'] == queued['id']


def test_unverifiable_city_owner_is_preserved(tmp_path, monkeypatch):
    design = tmp_path / 'cities/catalogue/west-asia/Iraq/Samawah/design.toml'
    design.parent.mkdir(parents=True)
    design.write_text('[city]\nslug="samawah"\n')
    monkeypatch.setattr(jobs.threading.Thread, 'start', lambda self: None)
    first = jobs.ProjectTwinManager(tmp_path)
    queued = first.start('samawah')
    monkeypatch.setattr(jobs, 'process_ownership', lambda pid, expected: None)
    assert jobs.ProjectTwinManager(tmp_path).job(queued['id'])['status'] == 'queued'
