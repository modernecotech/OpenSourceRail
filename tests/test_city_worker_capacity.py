"""Owned fake analytic processes exercise shared admission and persistent queues."""
import json
import os
import pytest
from engineering.outline import city_jobs as jobs,city_resources as resources,city_workflow
from engineering.station_rail.common import encoded


class Process:
    pid=os.getpid()
    returncode=None
    def poll(self):return self.returncode
    def wait(self,timeout=None):self.returncode=-15;return self.returncode


@pytest.fixture
def pool(tmp_path,monkeypatch):
    made=[];services=[]
    def launch(*args,**kwargs):
        p=Process();made.append(p);return p
    monkeypatch.setattr(jobs.subprocess,'Popen',launch)
    monkeypatch.setattr(jobs.os,'killpg',lambda *args:None)
    monkeypatch.setattr(jobs.publication_cache,'json_member',lambda *args,**kw:dict(evaluation_id='a'*64,planning_seed=dict(seed_id='b'*64)))
    monkeypatch.setattr(city_workflow,'_sources',lambda root:{'worker':'c'*64})
    monkeypatch.setattr(resources,'available_memory',lambda:20*1024**3)
    monkeypatch.setattr(resources,'cpu_slots',lambda:2)
    monkeypatch.setattr(resources,'disk_admission',lambda *a,**kw:dict(admitted=True))
    ledger=tmp_path/'shared.json'
    def make(name):
        root=tmp_path/(name+'-source');root.mkdir(exist_ok=True)
        s=jobs.CityStudyService(root,store=tmp_path/(name+'-jobs'),max_workers=2,resource_ledger=ledger,minimum_free_gib=20)
        s.stop.set();services.append(s);return s
    yield make,made
    for s in reversed(services):s.close()


def complete(s,job):
    folder=s._job(job['job_id'])/'artifacts';folder.mkdir()
    (folder/'summary.json').write_bytes(encoded(dict(calculation_complete=True)))
    s._verify=lambda path:dict(manifest_id='f'*64)
    s.jobs[job['job_id']]['process'].returncode=0
    return s.status(job['job_id'])


def test_two_workers_fifo_and_queue_limit(pool):
    make,processes=pool;s=make('a')
    a=s.submit(dict(city_slug='samawah'));b=s.submit(dict(city_slug='baghdad'))
    assert a['state']==b['state']=='running' and len(processes)==2
    queued=[s.submit(dict(city_slug='city-'+str(i))) for i in range(4)]
    assert all(x['state']=='queued' for x in queued)
    refused=s.submit(dict(city_slug='queue-full'))
    assert refused['state']=='held' and refused['busy'] is True
    job=queued[0]['job_id'];before=(s._job(job)/'request.json').read_bytes()
    complete(s,a)
    assert s.status(job)['state']=='running' and len(processes)==3
    assert s.status(queued[1]['job_id'])['state']=='queued'
    assert (s._job(job)/'request.json').read_bytes()==before


def test_shared_stores_and_memory_refusal_resume_without_failed_run(pool,monkeypatch):
    make,processes=pool;a=make('a');b=make('b')
    one=a.submit(dict(city_slug='samawah'));a.submit(dict(city_slug='baghdad'))
    held=b.submit(dict(city_slug='basra'))
    assert held['state']=='queued' and len(processes)==2
    complete(a,one)
    monkeypatch.setattr(resources,'available_memory',lambda:2*1024**3)
    status=b.status(held['job_id'])
    assert status['state']=='queued' and 'memory' in status['resource_admission']['reason']
    monkeypatch.setattr(resources,'available_memory',lambda:20*1024**3)
    assert b.status(held['job_id'])['state']=='running' and len(processes)==3


def test_disk_reservation_refusal_keeps_queued_request(pool,monkeypatch):
    make,processes=pool
    monkeypatch.setattr(resources,'disk_admission',lambda *a,**kw:dict(admitted=False))
    s=make('a');job=s.submit(dict(city_slug='samawah'))
    assert job['state']=='queued' and not processes
    assert (s._job(job['job_id'])/'request.json').exists()
    assert not (s._job(job['job_id'])/'worker.log').exists()


def test_close_preserves_pending_and_restart_resumes_fifo(pool):
    make,processes=pool;s=make('a')
    running=[s.submit(dict(city_slug=x)) for x in ('samawah','baghdad')]
    queued=[s.submit(dict(city_slug=x)) for x in ('basra','mosul')]
    contents={x['job_id']:(s._job(x['job_id'])/'request.json').read_bytes() for x in queued}
    s.close()
    for x in running:assert json.loads((s._job(x['job_id'])/'status.json').read_bytes())['state']=='interrupted'
    for x in queued:assert json.loads((s._job(x['job_id'])/'status.json').read_bytes())['state']=='queued'
    resumed=make('a');assert resumed.pending==[x['job_id'] for x in queued]
    assert resumed.status(queued[0]['job_id'])['state']=='running'
    assert len(processes)==4
    for job,raw in contents.items():assert (resumed._job(job)/'request.json').read_bytes()==raw


def test_queued_request_tamper_preserved_and_never_launched(pool,monkeypatch):
    make,processes=pool;monkeypatch.setattr(resources,'available_memory',lambda:0)
    s=make('a');job=s.submit(dict(city_slug='samawah'));folder=s._job(job['job_id'])
    (folder/'request.json').write_bytes(encoded(dict(city_slug='baghdad')))
    assert s.status(job['job_id'])['state']=='failed-integrity'
    assert not processes and (folder/'request.json').exists()


def test_single_cpu_defers_second_worker(pool,monkeypatch):
    make,processes=pool;monkeypatch.setattr(resources,'cpu_slots',lambda:1)
    s=make('a');a=s.submit(dict(city_slug='samawah'));b=s.submit(dict(city_slug='baghdad'))
    assert a['state']=='running' and b['state']=='queued' and len(processes)==1


def test_malformed_shared_ledger_defers_without_launch(pool):
    make,processes=pool;s=make('a')
    s.reservations.path.write_text(json.dumps(dict(schema='osr-analytic-worker-reservations/1',reservations=[])))
    job=s.submit(dict(city_slug='samawah'))
    assert job['state']=='queued' and not processes
    assert 'ledger unavailable' in job['resource_admission']['reason']


def test_unknown_crashed_launch_is_reserved_until_reconciled(pool,monkeypatch,tmp_path):
    make,processes=pool;s=make('a')
    r=s.reservations
    with r.transaction() as rows:
        rows['orphan-launch']=dict(owner_pid=987654321,owner_token='1',worker_pid=None,worker_token=None,
            device=s.store.stat().st_dev,disk_bytes=resources.DISK_BYTES)
    status=s.submit(dict(city_slug='samawah'))
    assert status['state']=='queued' and not processes
    assert status['resource_admission']['unreconciled_launches']==['orphan-launch']
