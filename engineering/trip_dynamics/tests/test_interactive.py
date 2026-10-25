"""Owned subprocesses, durable refusals and bounded local HTTP transport."""
from copy import deepcopy
from email.message import Message
from hashlib import sha256
from http import HTTPStatus
import importlib.util
from io import BytesIO
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import time
from types import SimpleNamespace

import pytest

from engineering.trip_dynamics import interactive as api
from engineering.design_search.contracts import encoded, identity


FAKE_EXPERIMENTS = '''from pathlib import Path
from hashlib import sha256
import json,subprocess,sys,time
from engineering.design_search.contracts import encoded
def catalogue(root):
    root=Path(root)
    return {'vehicles':[{'candidate_id':'a'*64}], 'source_sha256':{'data.json':sha256((root/'data.json').read_bytes()).hexdigest()},'physical_accepted':False}
def status(root):
    return {'publication':{'present':False},'tools':{},'physical_accepted':False}
def execute(request,output,root):
    output=Path(output);output.mkdir()
    (output/'partial.json').write_text('{"physical_accepted":false}')
    print('real subprocess entered action',request['action'],flush=True)
    if request['action']=='fixture':
        child=subprocess.Popen([sys.executable,'-c','import time;time.sleep(60)'])
        (output/'child.json').write_text(json.dumps({'pid':child.pid}))
        time.sleep(60)
    if request['action']=='verify':
        (Path(root)/'data.json').write_text('{"changed":true}')
    if request['action']=='setup-tools':
        tool=Path(root)/'build/trip-dynamics/environment/chrono/bin/python'
        tool.parent.mkdir(parents=True,exist_ok=True);tool.write_bytes(b'new-private-tool')
    if request['action']=='validate-map':
        tool=Path(root)/'build/trip-dynamics/tools/getdp-3.5.0-Linux64/bin/getdp'
        tool.parent.mkdir(parents=True,exist_ok=True);tool.write_bytes(b'unexpected-tool-change')
    if request['action']=='validate-modal':
        return {'execution_status':'failed','physical_accepted':False}
    (output/'trace.png').write_bytes(b'original fixture image bytes')
    result={'execution_status':'refused','result':{'gates':[{'state':'unknown'}]},'physical_accepted':False,'engineering_accepted':False}
    result['outputs']=[{'path':p.name,'bytes':p.stat().st_size,'sha256':sha256(p.read_bytes()).hexdigest()} for p in sorted(output.iterdir()) if p.is_file()]
    (output/'execution.json').write_bytes(encoded(result))
    return result
'''


@pytest.fixture
def repository(tmp_path, monkeypatch):
    root = tmp_path / 'repository'
    root.mkdir()
    (root / 'data.json').write_text('{"original":true}')
    module = root / 'engineering/trip_dynamics'
    module.mkdir(parents=True)
    for name in ('interactive.py', 'interactive_worker.py'):
        shutil.copyfile(Path(api.__file__).with_name(name), module / name)
    design = root / 'engineering/design_search'
    design.mkdir()
    for name in ('contracts.py', 'storage.py', 'registry.py'):
        shutil.copyfile(api.CODE_ROOT / 'engineering/design_search' / name, design / name)
    (module / 'experiments.py').write_text(FAKE_EXPERIMENTS)
    spec = importlib.util.spec_from_file_location('engineering.trip_dynamics.experiments', module / 'experiments.py')
    fake = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(fake)
    import engineering.trip_dynamics as package
    monkeypatch.setitem(sys.modules, 'engineering.trip_dynamics.experiments', fake)
    monkeypatch.setattr(package, 'experiments', fake, raising=False)
    monkeypatch.setattr(api, 'CODE_ROOT', root)
    return root


def wait_for(service, job_id, predicate=lambda row: row['state'] in api.TERMINAL, timeout=8):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        value = service.job(job_id)
        if predicate(value):
            return value
        time.sleep(.03)
    raise AssertionError('job did not reach expected state: ' + repr(service.job(job_id)))


def submit(service, action='probe', parameters=None):
    return service.submit(dict(action=action, parameters=parameters or {}))


def alive(pid):
    try:
        data = Path(f'/proc/{pid}/stat').read_text()
        return data[data.rfind(')') + 2:].split()[0] != 'Z'
    except OSError:
        return False


def test_real_subprocess_refusal_is_completed_calculation_and_durable(repository):
    service = api.TripService(repository)
    try:
        job = submit(service, 'experiment', dict(mode='evidence', vehicle_id='a'*64, distance_m=1500))
        job = wait_for(service, job['job_id'])
        assert job['state'] == 'completed'
        assert job['calculation_completed'] is True
        assert job['result']['execution_status'] == 'refused'
        assert job['engineering_accepted'] is False and job['physical_accepted'] is False
        assert 'real subprocess entered action' in service.logs(job['job_id'])['text']
        assert (service._directory(job['job_id']) / 'request.json').is_file()
        assert service.output_path(job['job_id'], 'outputs/partial.json').is_file()
    finally:
        service.close()
    reopened = api.TripService(repository)
    try:
        assert reopened.job(job['job_id'])['state'] == 'completed'
        assert reopened.job(job['job_id'])['result'] == job['result']
    finally:
        reopened.close()


def test_live_service_owns_job_root_until_its_workers_close(repository):
    first = api.TripService(repository)
    try:
        job = submit(first, 'fixture')
        wait_for(first, job['job_id'], lambda row: row['state'] == 'running')
        with pytest.raises(ValueError, match='Another live Workbench'):
            api.TripService(repository)
        # A second constructor must not enter recovery and cancel live jobs.
        assert first.job(job['job_id'])['state'] == 'running'
        first.cancel(job['job_id'])
        wait_for(first, job['job_id'])
    finally:
        first.close()
    second = api.TripService(repository)
    try:
        assert second.job(job['job_id'])['state'] == 'cancelled'
        assert (second.output_root/'.service.lock').is_file()
    finally:
        second.close()


@pytest.mark.parametrize('value', [
    {'action': 'shell', 'parameters': {}},
    {'action': 'probe', 'parameters': {'command': 'touch forbidden'}},
    {'action': 'experiment', 'parameters': {'output': '/tmp/foreign'}},
    {'action': 'experiment', 'parameters': {'mode': 'exploration'}},
    {'action': 'experiment', 'parameters': {'distance_m': True}},
    {'action': 'experiment', 'parameters': {'temperature_C': 80}},
    {'action': 'experiment', 'parameters': {'vehicle_id': 'f'*64}},
    {'action': 'validate-map', 'parameters': {'model_data': '/tmp/map.json', 'vehicle_id': 'a'*64}},
    {'action': 'validate-modal', 'parameters': {'model_data': {}, 'vehicle_id': 'a'*64, 'source_path': '/etc/passwd'}},
])
def test_invalid_client_requests_never_create_job_or_process(repository, value):
    service = api.TripService(repository)
    try:
        with pytest.raises((ValueError, TypeError)):
            service.submit(value)
        assert service.jobs() == []
        assert {path.name for path in service.output_root.iterdir()} == {'.service.lock'}
    finally:
        service.close()


def test_cancel_owned_group_including_descendant_retains_partial_output(repository):
    service = api.TripService(repository)
    try:
        job = submit(service, 'fixture')
        job = wait_for(service, job['job_id'], lambda row: any(x['path'] == 'outputs/child.json' for x in row['outputs']))
        child = json.loads(service.output_path(job['job_id'], 'outputs/child.json').read_bytes())['pid']
        assert alive(child)
        service.cancel(job['job_id'])
        cancelled = wait_for(service, job['job_id'])
        assert cancelled['state'] == 'cancelled'
        assert not cancelled['calculation_completed']
        assert not alive(child)
        assert any(x['path'] == 'interrupted-result.json' for x in cancelled['outputs'])
        assert service.output_path(job['job_id'], 'outputs/partial.json').is_file()
    finally:
        service.close()


def test_timeout_is_interrupted_and_not_engineering_pass(repository):
    service = api.TripService(repository, deadlines={'fixture': .3})
    try:
        job = wait_for(service, submit(service, 'fixture')['job_id'])
        assert job['state'] == 'interrupted'
        assert 'deadline' in job['progress']['message']
        assert not job['physical_accepted'] and not job['calculation_completed']
    finally:
        service.close()


def test_two_worker_bound_and_queued_cancellation(repository):
    service = api.TripService(repository, max_workers=2)
    try:
        jobs = [submit(service, 'fixture') for _ in range(3)]
        wait_for(service, jobs[0]['job_id'], lambda row: row['state'] == 'running')
        wait_for(service, jobs[1]['job_id'], lambda row: row['state'] == 'running')
        assert service.job(jobs[2]['job_id'])['state'] == 'queued'
        assert sum(row['state'] == 'running' for row in service.jobs()) == 2
        service.cancel(jobs[2]['job_id'])
        service.cancel(jobs[0]['job_id'])
        wait_for(service, jobs[0]['job_id'])
        queued = wait_for(service, jobs[2]['job_id'])
        assert queued['state'] == 'cancelled'
        assert queued['started_at'] is None
    finally:
        service.close()


def test_source_change_during_execution_prevents_success(repository):
    service = api.TripService(repository)
    try:
        job = wait_for(service, submit(service, 'verify')['job_id'])
        assert job['state'] == 'interrupted'
        assert 'source changed' in job['progress']['message'].lower()
        assert not job['calculation_completed']
        assert service.output_path(job['job_id'], 'outputs/partial.json').is_file()
    finally:
        service.close()


def test_source_inventory_addition_is_detected(repository):
    snapshot, _ = api.source_snapshot(repository)
    (repository / 'engineering/trip_dynamics/late.py').write_text('x=1\n')
    with pytest.raises(ValueError, match='inventory changed'):
        api.verify_snapshot(snapshot, repository)


def test_service_epoch_refuses_new_work_but_keeps_existing_jobs_readable(repository):
    service = api.TripService(repository)
    try:
        job = wait_for(service, submit(service)['job_id'])
        assert service.status()['restart_required'] is False
        (repository/'engineering/trip_dynamics/experiments.py').write_text(FAKE_EXPERIMENTS+'\n# new implementation epoch\n')
        assert service.status()['restart_required'] is True
        assert service.status()['status'] == 'held'
        before = set(service.output_root.iterdir())
        with pytest.raises(ValueError, match='restart the server'):
            submit(service)
        assert set(service.output_root.iterdir()) == before
        assert service.job(job['job_id'])['state'] == 'completed'
        assert service.logs(job['job_id'])['text']
        assert service.cancel(job['job_id'])['state'] == 'completed'
    finally:
        service.close()


def test_queued_request_tamper_is_refused_before_launch(repository):
    service = api.TripService(repository, max_workers=1)
    try:
        first = submit(service, 'fixture')
        wait_for(service, first['job_id'], lambda row: row['state'] == 'running')
        queued = submit(service)
        path = service._directory(queued['job_id']) / 'request.json'
        request = json.loads(path.read_bytes()); request['parameters'] = {'command':'ignored'}
        path.write_bytes(encoded(request))
        service.cancel(first['job_id'])
        held = wait_for(service, queued['job_id'])
        assert held['state'] == 'failed' and held['started_at'] is None
        assert 'digest differs' in held['progress']['message']
        assert not (service._directory(queued['job_id'])/'launch.json').exists()
    finally:
        service.close()


def test_setup_tracks_authorised_new_private_tool_identity(repository):
    service = api.TripService(repository)
    try:
        assert service.deadlines['setup-tools'] == 1200
        job = wait_for(service, submit(service, 'setup-tools')['job_id'])
        assert job['state'] == 'completed'
        wrapped = json.loads((service._directory(job['job_id'])/'result.json').read_bytes())
        assert wrapped['tool_setup_authorised'] is True
        assert wrapped['tools_before']['chrono_python']['available'] is False
        assert wrapped['tools_after']['chrono_python']['available'] is True
        assert wrapped['tools_after']['chrono_python']['sha256'] == sha256(b'new-private-tool').hexdigest()
    finally:
        service.close()


def test_setup_cannot_replace_existing_private_tool(repository):
    path = repository/'build/trip-dynamics/environment/chrono/bin/python'
    path.parent.mkdir(parents=True);path.write_bytes(b'original-tool')
    service = api.TripService(repository)
    try:
        job = wait_for(service, submit(service, 'setup-tools')['job_id'])
        assert job['state'] == 'interrupted'
        assert 'tool bytes changed' in job['progress']['message']
    finally:
        service.close()


def test_nonsetup_tool_changes_and_runtime_errors_are_not_completed(repository):
    service = api.TripService(repository)
    try:
        job = wait_for(service, submit(service, 'validate-map', {'model_data':{},'vehicle_id':'a'*64})['job_id'])
        assert job['state'] == 'interrupted'
        assert 'tool availability changed' in job['progress']['message']
        job = wait_for(service, submit(service, 'validate-modal', {'model_data':{},'vehicle_id':'a'*64})['job_id'])
        assert job['state'] == 'failed' and job['calculation_completed'] is False
        assert 'runtime execution failed' in job['progress']['message']
    finally:
        service.close()


def test_result_tamper_hidden_and_paths_logs_and_symlinks_refused(repository):
    service = api.TripService(repository)
    try:
        job = wait_for(service, submit(service)['job_id'])
        directory = service._directory(job['job_id'])
        path = directory / 'result.json'
        value = json.loads(path.read_bytes())
        value['result']['execution_status'] = 'accepted'
        path.write_bytes(encoded(value))
        held = service.job(job['job_id'])
        assert held['result'] is None and 'digest' in held['result_integrity_error']
        for name in ('../request.json', '/etc/passwd', 'outputs/../../request.json', 'outputs\\partial.json', 'request.json'):
            with pytest.raises((ValueError, KeyError)):
                service.output_path(job['job_id'], name)
        (directory / 'outputs/evil.json').symlink_to(repository / 'data.json')
        with pytest.raises((ValueError, KeyError)):
            service.output_path(job['job_id'], 'outputs/evil.json')
        with pytest.raises(ValueError):
            service.logs(job['job_id'], '../../request')
        (directory / 'stdout.log').write_bytes(b'x' * (api.MAX_LOG_RETURN + 2))
        log = service.logs(job['job_id'])
        assert log['truncated'] is True and len(log['text']) == api.MAX_LOG_RETURN
    finally:
        service.close()


def test_completed_trace_and_execution_receipt_tamper_cannot_be_served(repository):
    service = api.TripService(repository)
    try:
        job = wait_for(service, submit(service)['job_id'])
        assert all(item['verified'] for item in job['outputs'])
        trace = service.output_path(job['job_id'], 'outputs/trace.png')
        receipt = service.output_path(job['job_id'], 'outputs/execution.json')
        trace.write_bytes(b'different image')
        receipt.write_bytes(b'{"execution_status":"accepted"}\n')
        for name in ('outputs/trace.png', 'outputs/execution.json'):
            with pytest.raises(ValueError, match='bytes/digest differ'):
                service.output_path(job['job_id'], name)
        changed = {item['path']: item for item in service.job(job['job_id'])['outputs']}
        assert changed['outputs/trace.png']['integrity'] == 'held'
        assert changed['outputs/trace.png']['url'] is None
        assert changed['outputs/execution.json']['verified'] is False
    finally:
        service.close()


def test_interrupted_forensic_outputs_are_available_but_not_verified(repository):
    service = api.TripService(repository)
    try:
        job = wait_for(service, submit(service, 'verify')['job_id'])
        assert job['state'] == 'interrupted'
        path = service.output_path(job['job_id'], 'outputs/partial.json')
        path.write_bytes(b'partial forensic bytes')
        assert service.output_path(job['job_id'], 'outputs/partial.json').read_bytes() == b'partial forensic bytes'
        outputs = service.job(job['job_id'])['outputs']
        assert all(item['integrity'] == 'unverified-forensic' and item['verified'] is False for item in outputs)
    finally:
        service.close()


def test_pid_start_token_and_nonce_refuse_unrelated_process(monkeypatch):
    child = subprocess.Popen([sys.executable, '-c', 'import time;time.sleep(10)'], start_new_session=True)
    try:
        launch = dict(pid=child.pid, start_token=api._process_token(child.pid),
                      command=[sys.executable, '-c', 'import time;time.sleep(10)'], owner_token='not-this-process')
        signals = []
        monkeypatch.setattr(os, 'killpg', lambda *args: signals.append(args))
        assert not api._signal_owned(launch, signal.SIGTERM)
        launch['start_token'] = 'reused-pid-token'
        assert not api._signal_owned(launch, signal.SIGKILL)
        assert signals == [] and child.poll() is None
    finally:
        child.terminate(); child.wait(timeout=2)


def test_running_restart_is_interrupted_without_relaunch(repository):
    service = api.TripService(repository)
    job = wait_for(service, submit(service)['job_id'])
    service.close()
    path = service._directory(job['job_id']) / 'status.json'
    record = json.loads(path.read_bytes()); record.pop('status_id')
    record.update(state='running', finished_at=None, calculation_completed=False)
    record['status_id'] = identity(record); path.write_bytes(encoded(record))
    restarted = api.TripService(repository)
    try:
        value = restarted.job(job['job_id'])
        assert value['state'] == 'interrupted'
        assert value['progress']['phase'] == 'restart'
        assert 'restarted' in value['progress']['message']
    finally:
        restarted.close()


class Handler:
    def __init__(self, service, path, *, method='GET', body=None, origin=True, host='127.0.0.1:8090'):
        self.path, self.command = path, method
        self.server = SimpleNamespace(trip_service=service, server_port=8090, publication_integrity={'checked': True})
        self.client_address = ('127.0.0.1', 1234)
        self.headers = Message(); self.headers['Host'] = host
        if origin:
            self.headers['Origin'] = 'http://' + host
        self.headers['Content-Type'] = 'application/json'
        raw = encoded(body) if body is not None else b''
        self.headers['Content-Length'] = str(len(raw))
        self.rfile, self.wfile = BytesIO(raw), BytesIO()
        self.response_headers = {}
    def send_response(self, code): self.code = code
    def send_header(self, name, value): self.response_headers[name] = value
    def end_headers(self): pass
    def value(self): return json.loads(self.wfile.getvalue())


def test_http_contract_same_origin_size_limits_and_owned_files(repository):
    service = api.TripService(repository)
    try:
        bad = Handler(service, '/api/trip/jobs', method='POST', body={'action':'probe','parameters':{}}, origin=False)
        assert api.handle_api(bad) and bad.code == 403
        bad = Handler(service, '/api/trip/jobs', method='POST', body={}, host='evil.example:8090')
        api.handle_api(bad); assert bad.code == 403
        bad = Handler(service, '/api/trip/jobs', method='POST', body={})
        bad.headers.replace_header('Content-Length', str(api.MAX_BODY+1))
        api.handle_api(bad); assert bad.code == 413
        good = Handler(service, '/api/trip/jobs', method='POST', body={'action':'probe','parameters':{}})
        assert api.handle_api(good) and good.code == 202
        job = wait_for(service, good.value()['job_id'])
        for suffix in ('', '/logs?stream=stdout'):
            get = Handler(service, '/api/trip/jobs/'+job['job_id']+suffix)
            assert api.handle_api(get) and get.code == 200
        get = Handler(service, '/api/trip/jobs/'+job['job_id']+'/files/outputs/partial.json')
        assert api.handle_api(get) and get.code == 200
        assert get.value() == {'physical_accepted':False}
        assert 'sandbox' in get.response_headers['Content-Security-Policy']
        get = Handler(service, '/api/trip/jobs/'+job['job_id']+'/files/outputs/%2e%2e/request.json')
        api.handle_api(get); assert get.code in (400,404)
        status = Handler(service, '/api/trip/status')
        api.handle_api(status); assert status.value()['publication_integrity']['checked']
        assert api.handle_api(Handler(service, '/outside-trip-api')) is False
    finally:
        service.close()


EVIDENCE_ROOT = Path(os.environ.get('OSR_EVIDENCE_ROOT', '/home/hayder/Documents/OpenSourceRail'))


@pytest.mark.skipif(not (EVIDENCE_ROOT/'docs/design-engine/vehicle-optimisation/manifest.json').is_file(), reason='explicit retained evidence root required')
def test_actual_current_evidence_preflight_subprocess(tmp_path):
    """Real pinned vehicle/magnetic readers; no ideal mechanics or fake fields."""
    output = EVIDENCE_ROOT / 'build/workbench-trips' / ('test-' + tmp_path.name)
    service = api.TripService(EVIDENCE_ROOT, output_root=output)
    try:
        job = submit(service, 'experiment', dict(mode='evidence', distance_m=1500, load_case='AW3', temperature_C=20, mechanical_step_s=.001))
        job = wait_for(service, job['job_id'], timeout=20)
        assert job['state'] == 'completed'
        assert job['result']['execution_status'] == 'refused'
        assert job['result']['result']['dynamic_execution'] == 'not-run'
        assert job['result']['result']['launch_authorised'] is False
        assert job['physical_accepted'] is False
    finally:
        service.close()
