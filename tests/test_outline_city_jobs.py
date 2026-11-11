"""Controller tests use owned fake workers; engineering runs have separate tests."""
from copy import deepcopy
import json
from pathlib import Path

import pytest

from engineering.outline import city_jobs as jobs, city_workflow as workflow
from engineering.station_rail.common import encoded, digest


class Process:
    pid=987654321
    returncode=None
    def poll(self):return self.returncode
    def wait(self,timeout=None):self.returncode=-9;return self.returncode


@pytest.fixture
def service(tmp_path,monkeypatch):
    processes=[]
    def launch(*args,**kw):
        p=Process();processes.append((p,args,kw));return p
    monkeypatch.setattr(jobs.subprocess,'Popen',launch)
    monkeypatch.setattr(jobs.os,'killpg',lambda *a:None)
    monkeypatch.setattr(jobs.publication_cache,'json_member',lambda *a,**kw:
        dict(evaluation_id='a'*64,planning_seed=dict(seed_id='b'*64)))
    monkeypatch.setattr(jobs,'disk_admission',lambda root,**kw:dict(
        schema='osr-performance-disk-admission/1',admitted=True,
        minimum_free_reserve_gib=kw.get('minimum_free_gib')))
    monkeypatch.setattr(workflow,'_sources',lambda root:{'worker.py':'c'*64})
    s=jobs.CityStudyService(tmp_path)
    try:yield s,processes
    finally:s.close()


def test_one_worker_at_a_time_and_bounded_environment(service):
    s,ps=service;a=s.submit(dict(city_slug='samawah'));b=s.submit(dict(city_slug='baghdad'))
    assert a['state']=='running' and b['busy'] and a['job_id']==b['job_id']
    assert len(ps)==1
    _,args,kw=ps[0]
    assert kw['env']['OPENBLAS_NUM_THREADS']=='1' and kw['start_new_session']
    assert isinstance(args[0],list) and 'shell' not in kw
    assert a['resource_budget']['maximum_output_bytes']==jobs.MAX_JOB_BYTES
    assert a['resource_budget']['minimum_free_reserve_gib']==jobs.MINIMUM_FREE_GIB
    assert a['resource_admission']['admitted'] is True
    assert all(a[k] is False for k in jobs.FLAGS)


def test_city_job_store_can_be_placed_in_an_explicit_workspace(tmp_path,monkeypatch):
    root=tmp_path/'source';root.mkdir()
    store=tmp_path/'separate-output'/'city-studies'
    checked=[]
    monkeypatch.setattr(jobs,'disk_admission',lambda root,**kw:(checked.append(root) or dict(admitted=True)))
    class Process:
        pid=987654321
        returncode=None
        def poll(self):return None if self.returncode is None else self.returncode
        def wait(self,timeout=None):self.returncode=0;return 0
    monkeypatch.setattr(jobs.subprocess,'Popen',lambda *a,**kw:Process())
    monkeypatch.setattr(jobs.os,'killpg',lambda *a:None)
    service=jobs.CityStudyService(root,store=store)
    try:
        assert service.store==store.resolve()
        assert service.store.is_dir()
        assert not service.store.is_relative_to(service.root)
        monkeypatch.setattr(jobs.publication_cache,'json_member',lambda *a,**kw:
            dict(evaluation_id='a'*64,planning_seed=dict(seed_id='b'*64)))
        monkeypatch.setattr(workflow,'_sources',lambda root:{'worker.py':'c'*64})
        status=service.submit(dict(city_slug='samawah'))
        assert status['resource_admission']['admitted'] is True
        assert checked==[service.store], 'admission must inspect the job-output filesystem'
    finally:service.close()


def test_city_job_store_rejects_symlinked_destination(tmp_path,monkeypatch):
    root=tmp_path/'source';root.mkdir()
    outside=tmp_path/'outside';outside.mkdir()
    link=root/'linked';link.symlink_to(outside,target_is_directory=True)
    with pytest.raises(ValueError,match='Linked completion artifacts'):
        jobs.CityStudyService(root,store=link/'city-studies')


def test_explicit_city_job_store_cannot_write_into_source_checkout(tmp_path):
    root=tmp_path/'source';root.mkdir()
    with pytest.raises(ValueError,match='outside the source checkout'):
        jobs.CityStudyService(root,store=root/'build/city-studies')


def test_low_disk_holds_before_city_worker_without_deleting_or_creating_a_run(service,monkeypatch):
    s,ps=service
    denial=dict(schema='osr-performance-disk-admission/1',admitted=False,
        reason='Free space is below the configured reserve',filesystem_free_bytes=1,
        minimum_free_reserve_gib=jobs.MINIMUM_FREE_GIB)
    monkeypatch.setattr(jobs,'disk_admission',lambda root,**kw:denial)
    status=s.submit(dict(city_slug='samawah'))
    assert status['state']=='held' and status['resource_admission']==denial
    assert status['physical_accepted'] is False
    assert ps==[]
    assert list(s.store.glob('*/request.json'))==[]


def test_timeout_and_output_budget_preserve_requests(service,monkeypatch):
    s,ps=service;a=s.submit(dict(city_slug='samawah'));folder=s._job(a['job_id'])
    s.jobs[a['job_id']]['started']-=jobs.WALL_SECONDS+1
    assert s.status(a['job_id'])['state']=='timed-out'
    assert (folder/'request.json').exists() and (folder/'worker.log').exists()
    b=s.submit(dict(city_slug='baghdad'));monkeypatch.setattr(jobs,'MAX_JOB_BYTES',1)
    assert s.status(b['job_id'])['state']=='failed-output-budget'


def test_restarted_coordinator_marks_orphan_interrupted(service):
    s,_=service;job='d'*32;folder=s._job(job);folder.mkdir(parents=True)
    (folder/'status.json').write_bytes(encoded(dict(job_id=job,state='running')))
    s.close()
    replacement=jobs.CityStudyService(s.root)
    try:assert replacement.status(job)['state']=='interrupted'
    finally:replacement.close()
    with pytest.raises(ValueError):s.status('../outside')


def test_complete_cache_hit_requires_verified_artifacts(service,monkeypatch):
    s,ps=service;request=dict(city_slug='samawah');a=s.submit(request)
    folder=s._job(a['job_id'])/'artifacts';folder.mkdir()
    (folder/'summary.json').write_bytes(encoded(dict(calculation_complete=True)))
    monkeypatch.setattr(s,'_verify',lambda p:dict(manifest_id='f'*64))
    ps[0][0].returncode=0
    assert s.status(a['job_id'])['state']=='completed'
    monkeypatch.setattr(jobs,'disk_admission',lambda root,**kw:dict(admitted=False))
    assert s.submit(request)['cache_hit'] is True and len(ps)==1
    def stale(p):raise ValueError('source changed')
    monkeypatch.setattr(s,'_verify',stale)
    assert s.status(a['job_id'])['state']=='stale'
    monkeypatch.setattr(jobs,'disk_admission',lambda root,**kw:dict(admitted=True))
    assert s.submit(request)['job_id']!=a['job_id'] and len(ps)==2


def test_restarted_completed_index_is_only_a_hint_and_skips_store_scans(service,monkeypatch):
    s,ps=service;request=dict(city_slug='samawah');started=s.submit(request)
    folder=s._job(started['job_id'])/'artifacts';folder.mkdir()
    (folder/'summary.json').write_bytes(encoded(dict(calculation_complete=True)))
    monkeypatch.setattr(s,'_verify',lambda p:dict(manifest_id='f'*64))
    ps[0][0].returncode=0
    assert s.status(started['job_id'])['state']=='completed'
    s.close()
    replacement=jobs.CityStudyService(s.root)
    monkeypatch.setattr(replacement,'_verify',lambda p:dict(manifest_id='f'*64))
    monkeypatch.setattr(replacement,'_usage',lambda:pytest.fail('cache hit must not scan store usage'))
    original_glob=jobs.Path.glob
    def no_status_scan(path,pattern):
        if path==replacement.store and pattern=='*/status.json':
            raise AssertionError('cache hit must use the rebuilt request-key index')
        return original_glob(path,pattern)
    monkeypatch.setattr(jobs.Path,'glob',no_status_scan)
    try:
        hit=replacement.submit(request)
        assert hit['job_id']==started['job_id'] and hit['cache_hit'] is True
        assert len(ps)==1
    finally:replacement.close()


def test_restarted_completed_index_rechecks_tampered_artifacts(service,monkeypatch):
    s,ps=service;request=dict(city_slug='samawah');started=s.submit(request)
    folder=s._job(started['job_id'])/'artifacts';folder.mkdir()
    (folder/'summary.json').write_bytes(encoded(dict(calculation_complete=True)))
    monkeypatch.setattr(s,'_verify',lambda p:dict(manifest_id='f'*64))
    ps[0][0].returncode=0
    assert s.status(started['job_id'])['state']=='completed'
    s.close()
    replacement=jobs.CityStudyService(s.root)
    monkeypatch.setattr(replacement,'_verify',lambda p:(_ for _ in ()).throw(ValueError('artifact changed')))
    monkeypatch.setattr(replacement,'_usage',lambda:0)
    try:
        next_job=replacement.submit(request)
        assert next_job['state']=='running' and next_job['job_id']!=started['job_id']
        retained=json.loads((s._job(started['job_id'])/'status.json').read_bytes())
        assert retained['state']=='stale'
        assert len(ps)==2
    finally:replacement.close()


def test_store_full_refuses_new_worker_without_deleting_runs(service,monkeypatch):
    s,ps=service;monkeypatch.setattr(s,'_usage',lambda:jobs.MAX_STORE_BYTES)
    with pytest.raises(ValueError,match='storage budget'):s.submit(dict(city_slug='samawah'))
    assert not ps


def test_corrupt_retained_status_is_preserved_without_blocking_new_work(service):
    s,ps=service;a=s.submit(dict(city_slug='samawah'));folder=s._job(a['job_id'])
    (folder/'status.json').write_bytes(b'{invalid')
    assert s.status(a['job_id'])['state']=='failed-integrity'
    assert list(folder.glob('status.invalid-*.json'))[0].read_bytes()==b'{invalid'
    assert s.jobs[a['job_id']]['finished'] and s.jobs[a['job_id']]['log'].closed
    assert s.submit(dict(city_slug='baghdad'))['job_id']!=a['job_id']


def test_another_coordinator_cannot_share_the_same_store(service):
    s,_=service
    with pytest.raises(ValueError,match='Another completion coordinator'):
        jobs.CityStudyService(s.root)


def test_shutdown_with_corrupt_status_still_closes_logs_and_releases_coordinator(service):
    s,_=service;a=s.submit(dict(city_slug='samawah'));folder=s._job(a['job_id'])
    (folder/'status.json').write_bytes(b'{invalid')
    s.close()
    assert s.jobs[a['job_id']]['log'].closed
    assert json.loads((folder/'status.json').read_bytes())['state']=='failed-integrity'
    replacement=jobs.CityStudyService(s.root)
    replacement.close()


def test_workbench_constructor_releases_other_service_when_store_is_owned(service,monkeypatch):
    from engineering.development_baseline.server import WorkbenchHTTPServer,Handler
    from engineering.trip_dynamics import interactive
    s,_=service;closed=[]
    class Trip:
        def __init__(self,root):pass
        def close(self):closed.append(True)
    monkeypatch.setattr(interactive,'TripService',Trip)
    with pytest.raises(ValueError,match='Another completion coordinator'):
        WorkbenchHTTPServer(('127.0.0.1',0),Handler,root=s.root)
    assert closed==[True]


def test_artifact_whitelist_and_payload_hash(service,monkeypatch):
    s,_=service;job='e'*32;folder=s._job(job)/'artifacts';folder.mkdir(parents=True)
    (folder/'summary.json').write_bytes(b'{"result":1}\n')
    manifest=dict(artifact_paths={'summary.json':'summary.json'},files_sha256={'summary.json':digest(folder/'summary.json')})
    monkeypatch.setattr(s,'_poll',lambda j:dict(state='completed'))
    monkeypatch.setattr(s,'_verify',lambda p:deepcopy(manifest))
    assert json.loads(s.artifact(job,'summary.json'))=={'result':1}
    with pytest.raises(ValueError,match='Known'):s.artifact(job,'../../outside')
    (folder/'summary.json').write_bytes(b'{"result":2}\n')
    with pytest.raises(ValueError,match='differs'):s.artifact(job,'summary.json')


@pytest.mark.parametrize('raw',[b'{"city_slug":"a","city_slug":"b"}',b'{"x":NaN}',b'{"x":Infinity}'])
def test_ambiguous_or_nonfinite_json_refused(raw):
    with pytest.raises(ValueError):jobs._json(raw)


def test_iterative_edits_inherit_verified_policy_without_resetting_demand_or_prices():
    previous=dict(operating_hours_per_day=24,operating_days_per_year=330,peak_demand_pphpd=5000,
        pricing_basis='china-bulk-buy',project=dict(pricing_scenario='china-bulk-buy',station_launch_mode='roller'),
        alignment=dict(maximum_added_walk_m=350,corner_radius_m=200))
    result=workflow._rules(previous,workflow.normalize(dict(city_slug='samawah')))
    assert result['operating_days_per_year']==330 and result['peak_demand_pphpd']==5000
    assert result['project']==previous['project'] and result['operations_shifts_per_day']==3
    result=workflow._rules(previous,workflow.normalize(dict(city_slug='samawah',alignment=dict(maximum_added_walk_m=250))))
    assert result['alignment']==dict(maximum_added_walk_m=250,corner_radius_m=200)


@pytest.mark.parametrize('proposal',[
    {'city_slug':'../outside'}, {'city_slug':'samawah','command':'rm'},
    {'city_slug':'samawah','service':{'maximum_headway_s':True}},
    {'city_slug':'samawah','service':{'planning_occupancy':float('nan')}},
    {'city_slug':'samawah','alignment':{'corner_samples':4.5}},
    {'city_slug':'samawah','base_study_id':'x'*32,'edit_bundle':{}},
    {'city_slug':'samawah','project':{'foreign_local_rate_transfer':[2,1,3]}},
])
def test_request_contract_has_no_arbitrary_commands_paths_or_unbounded_values(proposal):
    with pytest.raises((ValueError,TypeError)):workflow.normalize(proposal)
