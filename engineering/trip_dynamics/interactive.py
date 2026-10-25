"""Bounded loopback Workbench jobs; calculation completion is not qualification.

Integration: attach ``TripService(repository_root)`` to ``server.trip_service``;
call ``handle_api(self)`` first in GET/POST handlers, and ``service.close()`` on
shutdown. False means the request belongs to the existing static server.
"""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from datetime import datetime, timezone
import fcntl
from hashlib import sha256
import ipaddress
import json
import math
import mimetypes
import os
from pathlib import Path, PurePosixPath
import re
import signal
import subprocess
import sys
import threading
import time
from urllib.parse import parse_qs, quote, unquote, urlsplit
import uuid

from engineering.design_search.contracts import encoded, identity
from engineering.design_search.storage import atomic_immutable


SCHEMA = 'osr-trip-interactive-request/1'
CODE_ROOT = Path(__file__).resolve().parents[2]
ACTIONS = frozenset({'experiment', 'campaign', 'fixture', 'verify', 'probe',
                     'setup-tools', 'validate-map', 'validate-modal'})
TERMINAL = frozenset({'completed', 'failed', 'cancelled', 'interrupted'})
ACCEPTANCE = frozenset({'physical_accepted', 'engineering_accepted', 'configuration_adopted',
                       'physical_release', 'physical_validation', 'manufacturing_release',
                       'design_complete'})
MAX_BODY = 4 * 1024**2
MAX_RESULT = 32 * 1024**2
MAX_LOG = 8 * 1024**2
MAX_LOG_RETURN = 128 * 1024
MAX_FILE = 64 * 1024**2
MAX_OUTPUT = 256 * 1024**2
JOB_RE = re.compile(r'[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}')


class RequestError(ValueError):
    pass


def _now():
    return datetime.now(timezone.utc).isoformat()


def _json(raw):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise RequestError('duplicate JSON key: ' + key)
            result[key] = value
        return result
    return json.loads(raw, object_pairs_hook=pairs,
                      parse_constant=lambda value: (_ for _ in ()).throw(RequestError('nonfinite JSON')))


def _ordinary(path, parent):
    path, parent = Path(path), Path(parent).resolve()
    if not path.is_absolute():
        path = parent / path
    if path.resolve() != path or not path.is_relative_to(parent):
        raise RequestError('ordinary contained output path required')
    return path


def _read(path, parent, limit=MAX_RESULT):
    path = _ordinary(path, parent)
    if not path.is_file() or path.stat().st_size > limit:
        raise RequestError('bounded ordinary JSON file required')
    return _json(path.read_bytes())


def _write(path, value):
    """Atomic replace for mutable lifecycle records; immutable inputs use storage."""
    if path.is_symlink():
        raise RequestError('symlink lifecycle record refused')
    temporary = path.with_name('.' + path.name + '-' + uuid.uuid4().hex)
    try:
        with temporary.open('xb') as stream:
            stream.write(encoded(value)); stream.flush(); os.fsync(stream.fileno())
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)


def _no_acceptance(value):
    if isinstance(value, dict):
        for key, child in value.items():
            if key in ACCEPTANCE and child is not False:
                raise RequestError('interactive result cannot assert qualification: ' + key)
            _no_acceptance(child)
    elif isinstance(value, list):
        for child in value:
            _no_acceptance(child)


def _code_snapshot():
    code = {}
    paths = list((CODE_ROOT / 'engineering/trip_dynamics').rglob('*'))
    paths += [CODE_ROOT / 'engineering/design_search' / name
              for name in ('contracts.py', 'storage.py', 'registry.py')]
    suffixes = {'.py', '.json', '.toml', '.geo', '.pro', '.comm', '.mail', '.export',
                '.lock', '.explicit', '.md', '.txt', '.sh'}
    for path in paths:
        if '__pycache__' not in path.parts and path.is_file() and path.suffix in suffixes:
            _ordinary(path, CODE_ROOT)
            code[path.relative_to(CODE_ROOT).as_posix()] = sha256(path.read_bytes()).hexdigest()
    return dict(sorted(code.items()))


def source_snapshot(root):
    """Bind executing code separately from explicitly rooted retained evidence."""
    from . import experiments
    catalogue = experiments.catalogue(Path(root))
    data = catalogue.get('source_sha256', catalogue.get('source_bindings', {}))
    if not isinstance(data, dict) or not data:
        raise RequestError('catalogue lacks source bindings')
    result = dict(code_sha256=_code_snapshot(), evidence_sha256=dict(sorted(data.items())))
    verify_snapshot(result, root)
    return result, catalogue


def verify_snapshot(value, root):
    if value.get('code_sha256') != _code_snapshot():
        raise RequestError('executing source bytes or inventory changed')
    for key, folder in (('code_sha256', CODE_ROOT), ('evidence_sha256', Path(root).resolve())):
        mapping = value.get(key)
        if not isinstance(mapping, dict) or (key == 'code_sha256' and not mapping):
            raise RequestError('explicit source snapshot required')
        for name, expected in mapping.items():
            rel = PurePosixPath(name)
            if rel.is_absolute() or '..' in rel.parts or rel.as_posix() != name:
                raise RequestError('ordinary relative source required')
            path = _ordinary(folder / name, folder)
            if not path.is_file() or sha256(path.read_bytes()).hexdigest() != expected:
                raise RequestError('source changed: ' + name)


def tool_snapshot(root, python):
    """Actual local executable/native-package bytes, not a claim of validation."""
    root = Path(root).resolve()
    paths = {'worker_python': Path(python),
             'chrono_python': root / 'build/trip-dynamics/environment/chrono/bin/python',
             'getdp': root / 'build/trip-dynamics/tools/getdp-3.5.0-Linux64/bin/getdp',
             'micromamba': root / 'build/trip-dynamics/tools/micromamba/bin/micromamba'}
    env = root / 'build/trip-dynamics/environment/chrono'
    paths['chrono_core_library'] = env / 'lib/libChrono_core.so'
    config = Path(python).parent.parent / 'pyvenv.cfg'
    if config.is_file():
        paths['worker_venv_config'] = config
    for path in sorted(env.glob('lib/python*/site-packages/pychrono/_core*.so')):
        paths['chrono_native/' + path.name] = path
    for path in sorted((env / 'conda-meta').glob('pychrono-*.json')):
        paths['chrono_package/' + path.name] = path
    result = {}
    for name, path in paths.items():
        invocation = str(path.absolute())
        path = path.resolve()
        result[name] = dict(path=str(path), invocation_path=invocation, available=path.is_file(),
                            sha256=sha256(path.read_bytes()).hexdigest() if path.is_file() else None)
    return result


def verify_tools(value, *, allow_setup=False):
    for name, record in value.items():
        path = Path(record['path'])
        if allow_setup and name in {'chrono_python', 'chrono_core_library', 'getdp', 'micromamba'} and not record['available'] and Path(record.get('invocation_path', record['path'])).is_file():
            continue  # only the source-bound pinned installer is allowed this transition
        if Path(record.get('invocation_path', record['path'])).resolve() != path:
            raise RequestError('tool invocation target changed: ' + name)
        if path.is_file() != record['available']:
            raise RequestError('tool availability changed: ' + name)
        if record['available'] and sha256(path.read_bytes()).hexdigest() != record['sha256']:
            raise RequestError('tool bytes changed: ' + name)


def validate_command(value, catalogue=None):
    if not isinstance(value, dict) or set(value) != {'action', 'parameters'}:
        raise RequestError('request requires exactly action and parameters')
    action, params = value['action'], value['parameters']
    if not isinstance(action, str) or action not in ACTIONS or not isinstance(params, dict):
        raise RequestError('known action and parameter object required')
    params = deepcopy(params)
    allowed = set()
    if action == 'experiment':
        allowed = {'mode', 'vehicle_id', 'distance_m', 'load_case', 'temperature_C', 'mechanical_step_s'}
    elif action == 'fixture':
        allowed = {'fixture'}
        if params.get('fixture', 'nonlinear-magnetics') not in {'current', 'laminate', 'nonlinear-magnetics'}:
            raise RequestError('unknown bounded fixture')
    elif action in {'validate-map', 'validate-modal'}:
        allowed = {'model_data', 'vehicle_id', 'load_case', 'temperature_C'}
        if not isinstance(params.get('model_data'), dict) or not isinstance(params.get('vehicle_id'), str):
            raise RequestError('inline model_data object and vehicle_id required')
    if set(params) - allowed:
        raise RequestError('unknown parameters; client paths, commands and overrides are refused')
    if action == 'experiment':
        if params.get('mode', 'evidence') not in {'evidence', 'benchmark'}:
            raise RequestError('evidence or explicitly ideal benchmark mode required')
        if type(params.get('distance_m', 2000)) not in (int, float) or params.get('distance_m', 2000) not in (1500, 2000):
            raise RequestError('distance must be 1500 or 2000m')
        if type(params.get('mechanical_step_s', .001)) not in (int, float) or params.get('mechanical_step_s', .001) not in (.001, .0005):
            raise RequestError('mechanical step must be .001 or .0005s')
    if action in {'experiment', 'validate-map', 'validate-modal'}:
        if params.get('load_case', 'AW3') not in {'empty', 'AW3'}:
            raise RequestError('empty or AW3 load case required')
        if type(params.get('temperature_C', 20)) not in (int, float) or params.get('temperature_C', 20) not in (20, 50):
            raise RequestError('temperature must be 20 or 50 degrees Celsius')
        vehicle_id = params.get('vehicle_id')
        if vehicle_id is not None and (not isinstance(vehicle_id, str) or not re.fullmatch('[0-9a-f]{64}', vehicle_id)):
            raise RequestError('catalogue physical vehicle identity required')
        if catalogue is not None and vehicle_id is not None:
            vehicles = catalogue.get('vehicles', [])
            if isinstance(vehicles, dict):
                vehicles = list(vehicles.values())
            if vehicle_id not in {v.get('candidate_id', v.get('vehicle_id')) for v in vehicles if isinstance(v, dict)}:
                raise RequestError('vehicle is absent from the source-bound catalogue')
    # Catch nonfinite values and overlarge objects before any directory/process.
    if len(encoded(params)) > MAX_BODY:
        raise RequestError('request exceeds JSON budget')
    return dict(action=action, parameters=params)


def _process_token(pid):
    try:
        text = Path(f'/proc/{pid}/stat').read_text()
        return text[text.rfind(')') + 2:].split()[19]
    except (OSError, IndexError):
        return None


def _owned_alive(launch):
    """Never signal a reused PID, another group, or a non-worker process."""
    try:
        pid = launch['pid']
        if type(pid) is not int or pid <= 1 or not launch.get('start_token'):
            return False
        if _process_token(pid) != launch['start_token'] or os.getpgid(pid) != pid:
            return False
        command = Path(f'/proc/{pid}/cmdline').read_bytes().rstrip(b'\0').split(b'\0')
        if command != [part.encode() for part in launch['command']]:
            return False
        token = ('OSR_TRIP_JOB_TOKEN=' + launch['owner_token']).encode()
        return token in Path(f'/proc/{pid}/environ').read_bytes().split(b'\0')
    except (OSError, KeyError, TypeError):
        return False


def _orphaned_group_owned(launch):
    """After a verified TERM, identify surviving descendants by group + nonce.

    A reused leader PID or any unverifiable group member prevents signalling.
    Environment bytes are inspected only for the job nonce and never returned.
    """
    if Path(f'/proc/{launch["pid"]}').exists():
        return _owned_alive(launch)
    found = False
    try:
        token = ('OSR_TRIP_JOB_TOKEN=' + launch['owner_token']).encode()
        for path in Path('/proc').iterdir():
            if not path.name.isdecimal():
                continue
            try:
                if os.getpgid(int(path.name)) != launch['pid']:
                    continue
                stat = (path / 'stat').read_text()
                if stat[stat.rfind(')') + 2:].split()[0] == 'Z':
                    continue
                found = True
                if token not in (path / 'environ').read_bytes().split(b'\0'):
                    return False
            except ProcessLookupError:
                continue
        return found
    except (OSError, KeyError, TypeError):
        return False


def _signal_owned(launch, sig, *, orphaned=False):
    if not (_orphaned_group_owned(launch) if orphaned else _owned_alive(launch)):
        return False
    try:
        os.killpg(launch['pid'], sig)
        return True
    except ProcessLookupError:
        return False


def _stop_owned(launch, process=None):
    signalled = _signal_owned(launch, signal.SIGTERM)
    if not signalled:
        return False
    deadline = time.monotonic() + 1.
    while time.monotonic() < deadline:
        if process is not None:
            process.poll()  # reap the owned group leader before descendant checks
        if not _orphaned_group_owned(launch):
            break
        time.sleep(.05)
    _signal_owned(launch, signal.SIGKILL, orphaned=True)
    if process is not None:
        try:
            process.wait(timeout=1.)
        except subprocess.TimeoutExpired:
            return False
    return True


class TripService:
    def __init__(self, root, *, output_root=None, max_workers=2, deadlines=None):
        self.root = Path(root).resolve()
        if type(max_workers) is not int or not 1 <= max_workers <= 2:
            raise ValueError('one or two local workers required')
        self.output_root = _ordinary(Path(output_root or self.root / 'build/workbench-trips').absolute(), self.root / 'build')
        self.output_root.mkdir(parents=True, exist_ok=True, mode=0o700)
        proposed = self.root / '.venv/bin/python'
        # Preserve venv invocation: resolving bin/python before launching would
        # silently discard pyvenv.cfg and its installed worker dependencies.
        self.python = str(proposed.absolute() if proposed.is_file() else Path(sys.executable).absolute())
        self.max_workers = max_workers
        self.deadlines = {a: 1200. if a in {'campaign', 'setup-tools'} else 300. for a in ACTIONS}
        for action, value in (deadlines or {}).items():
            if action not in ACTIONS or type(value) not in (int, float) or not math.isfinite(value) or not 0 < value <= self.deadlines[action]:
                raise ValueError('deadline override may only shorten a known action budget')
            self.deadlines[action] = float(value)
        self._lock = threading.RLock()
        self._jobs, self._events = {}, {}
        self._closed = False
        self._code_epoch = _code_snapshot()
        lock_path = _ordinary(self.output_root / '.service.lock', self.output_root)
        self._service_lock = lock_path.open('a+b')
        try:
            fcntl.flock(self._service_lock.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as error:
            self._service_lock.close()
            raise RequestError('Another live Workbench owns this job directory; reuse that server or choose a separate server-managed job root') from error
        try:
            self._recover()
            self._executor = ThreadPoolExecutor(max_workers=max_workers, thread_name_prefix='trip-job')
        except BaseException:
            self._service_lock.close()
            raise

    def _directory(self, job_id):
        if not isinstance(job_id, str) or not JOB_RE.fullmatch(job_id):
            raise KeyError('unknown job')
        return _ordinary(self.output_root / job_id, self.output_root)

    def _persist(self, value):
        record = deepcopy(value)
        record['status_id'] = identity(record)
        _write(self._directory(value['job_id']) / 'status.json', record)
        self._jobs[value['job_id']] = deepcopy(value)

    def _recover(self):
        for directory in sorted(self.output_root.iterdir()):
            if not JOB_RE.fullmatch(directory.name) or directory.is_symlink() or not directory.is_dir():
                continue
            try:
                record = _read(directory / 'status.json', self.output_root, MAX_BODY)
                digest = record.pop('status_id', None)
                if digest != identity(record) or record['job_id'] != directory.name:
                    raise RequestError('job status digest/identity differs')
                # Uploaded JSON is an untrusted input, not a qualification flag.
                # Preserve even malformed claims so rejected imports stay durable.
                _no_acceptance({key: record[key] for key in ACCEPTANCE if key in record})
                request = _read(directory / 'request.json', self.output_root, 2 * MAX_BODY)
                check_request(request)
                if record['request_id'] != request['request_id']:
                    raise RequestError('job request binding differs')
                if record['state'] not in TERMINAL:
                    signalled = False
                    if (directory / 'launch.json').is_file():
                        launch = _read(directory / 'launch.json', self.output_root)
                        if launch.get('request_id') == request['request_id']:
                            signalled = _stop_owned(launch)
                    record.update(state='interrupted', finished_at=_now(),
                                  progress=dict(phase='restart', message='Server restarted; retained attempt is not resumed', owned_group_signalled=signalled))
                self._persist(record)
            except (OSError, ValueError, KeyError, TypeError) as error:
                # Preserve corrupt records as evidence, without trusting their PID.
                self._jobs[directory.name] = dict(job_id=directory.name, state='interrupted',
                    action='unknown', parameters={}, created_at=None, request_id=None,
                    progress=dict(phase='recovery-held', message=str(error)), physical_accepted=False)

    def catalogue(self):
        if self.restart_required():
            raise RequestError('Workbench source changed; restart the server before requesting a current catalogue or submitting work')
        from . import experiments
        return experiments.catalogue(self.root)

    def restart_required(self):
        try:
            return _code_snapshot() != self._code_epoch
        except (OSError, ValueError):
            return True

    def status(self):
        restart = self.restart_required()
        if restart:
            result = dict(schema='osr-trip-interactive-status/1', status='held',
                          error='Workbench source changed; restart the server before submitting work',
                          physical_accepted=False)
        else:
            try:
                from . import experiments
                result = experiments.status(self.root)
            except (OSError, ValueError, RuntimeError) as error:
                result = dict(status='held', error=str(error), physical_accepted=False)
        result = deepcopy(result)
        result.update(jobs=self.jobs()[:12], limits=dict(max_workers=self.max_workers, max_jobs=32,
                      request_bytes=MAX_BODY, campaign_seconds=1200, setup_seconds=1200, small_job_seconds=300),
                      restart_required=restart, physical_accepted=False)
        return result

    def submit(self, value):
        if self.restart_required():
            raise RequestError('Workbench source changed; restart the server before submitting work')
        command = validate_command(value)
        snapshot, catalogue = source_snapshot(self.root)
        command = validate_command(command, catalogue)
        with self._lock:
            if self.restart_required():
                raise RequestError('Workbench source changed; restart the server before submitting work')
            if self._closed:
                raise RequestError('job service is closed')
            if sum(v['state'] not in TERMINAL for v in self._jobs.values()) >= 32:
                raise RequestError('local job queue is full')
            job_id = str(uuid.uuid4())
            directory = self._directory(job_id)
            directory.mkdir(mode=0o700)
            request = dict(schema=SCHEMA, job_id=job_id, **command, source_snapshot=snapshot,
                           tools=tool_snapshot(self.root, self.python), deadline_s=self.deadlines[command['action']],
                           physical_accepted=False)
            request['request_id'] = identity(request)
            atomic_immutable(directory / 'request.json', encoded(request))
            for name in ('stdout.log', 'stderr.log'):
                (directory / name).touch(exist_ok=False)
            record = dict(job_id=job_id, **command, request_id=request['request_id'], state='queued',
                          created_at=_now(), started_at=None, finished_at=None,
                          progress=dict(phase='queued', message='Waiting for a local worker'),
                          calculation_completed=False, engineering_accepted=False, physical_accepted=False)
            self._events[job_id] = threading.Event()
            self._persist(record)
            self._executor.submit(self._run, job_id)
        return self.job(job_id)

    def _run(self, job_id):
        directory = self._directory(job_id)
        event = self._events[job_id]
        process = None
        launch = None
        disposition = None
        started = time.monotonic()
        try:
            request = _read(directory / 'request.json', self.output_root, 2 * MAX_BODY)
            check_request(request)
            verify_snapshot(request['source_snapshot'], self.root)
            verify_tools(request['tools'])
            with self._lock:
                record = deepcopy(self._jobs[job_id])
                if event.is_set() or self._closed:
                    disposition = ('cancelled', 'Cancelled before worker launch')
                else:
                    command = [self.python, '-m', 'engineering.trip_dynamics.interactive_worker',
                               '--request', str(directory / 'request.json'), '--output', str(directory), '--root', str(self.root)]
                    token = uuid.uuid4().hex
                    env = dict(os.environ, PYTHONPATH=str(CODE_ROOT), PYTHONUNBUFFERED='1',
                               OMP_NUM_THREADS='1', OPENBLAS_NUM_THREADS='1', MKL_NUM_THREADS='1',
                               OSR_TRIP_JOB_TOKEN=token)
                    with (directory / 'stdout.log').open('ab') as stdout, (directory / 'stderr.log').open('ab') as stderr:
                        process = subprocess.Popen(command, cwd=CODE_ROOT, env=env, stdout=stdout,
                                                   stderr=stderr, start_new_session=True)
                    launch = dict(pid=process.pid, start_token=_process_token(process.pid),
                                  command=command, owner_token=token, request_id=request['request_id'])
                    atomic_immutable(directory / 'launch.json', encoded(launch))
                    record.update(state='running', started_at=_now(), progress=dict(phase='execution', message='Owned subprocess running; see logs'))
                    self._persist(record)
            last_check = 0.
            while process is not None and process.poll() is None:
                elapsed = time.monotonic() - started
                if event.is_set():
                    disposition = ('cancelled', 'Cancellation requested')
                elif elapsed > request['deadline_s']:
                    disposition = ('interrupted', 'Wall-clock deadline exceeded')
                elif any((directory / name).stat().st_size > MAX_LOG for name in ('stdout.log', 'stderr.log')):
                    disposition = ('interrupted', 'Log byte budget exceeded')
                if disposition:
                    if not _stop_owned(launch, process):
                        disposition = ('interrupted', 'Worker ownership could not be confirmed; no unrelated process was signalled')
                    break
                if elapsed - last_check > 1.:
                    outputs = self._outputs(job_id)
                    if len(outputs) > 256 or sum(v['bytes'] for v in outputs) > MAX_OUTPUT:
                        disposition = ('interrupted', 'Output byte/file budget exceeded')
                        continue
                    with self._lock:
                        record = deepcopy(self._jobs[job_id])
                        record['progress'].update(elapsed_s=round(elapsed, 2), output_files=len(outputs))
                        self._persist(record)
                    last_check = elapsed
                time.sleep(.1)
            if disposition is None:
                verify_snapshot(request['source_snapshot'], self.root)
                verify_tools(request['tools'], allow_setup=request['action'] == 'setup-tools')
                result = self._result(job_id)
                if process is None or process.returncode != 0 or result is None:
                    disposition = ('failed', 'Worker failed; inspect retained result and stderr')
                elif result['execution_status'] != 'completed':
                    disposition = ('failed', 'Worker execution error; scientific refusals remain completed calculations')
                elif result.get('result', {}).get('execution_status') == 'failed':
                    disposition = ('failed', 'Tool/runtime execution failed; retained calculation is not a successful execution')
                else:
                    disposition = ('completed', 'Calculation completed; engineering and physical acceptance remain false')
        except (OSError, ValueError, KeyError, TypeError, RuntimeError) as error:
            disposition = ('interrupted' if 'changed' in str(error) else 'failed', str(error))
            if process is not None and process.poll() is None and launch:
                _stop_owned(launch, process)
        finally:
            state, reason = disposition or ('failed', 'Worker controller ended without a result')
            with self._lock:
                record = deepcopy(self._jobs[job_id])
                record.update(state=state, finished_at=_now(), calculation_completed=state == 'completed',
                              progress=dict(phase=state, message=reason, elapsed_s=round(time.monotonic() - started, 2)))
                if state != 'completed':
                    _write(directory / 'interrupted-result.json', dict(schema='osr-trip-interrupted-job/1',
                        job_id=job_id, request_id=record['request_id'], state=state, reason=reason,
                        partial_output_paths=[v['path'] for v in self._outputs(job_id)],
                        engineering_accepted=False, physical_accepted=False))
                self._persist(record)

    def _result(self, job_id):
        directory = self._directory(job_id)
        if not (directory / 'result.json').is_file():
            return None
        value = _read(directory / 'result.json', self.output_root)
        expected = value.get('result_sha256')
        raw = {k: v for k, v in value.items() if k != 'result_sha256'}
        if expected != identity(raw) or value.get('request_id') != self._jobs[job_id]['request_id']:
            raise RequestError('result digest/request binding differs')
        _no_acceptance(value)
        return value

    def _outputs(self, job_id):
        directory = self._directory(job_id)
        paths = list((directory / 'outputs').rglob('*')) if (directory / 'outputs').is_dir() and not (directory / 'outputs').is_symlink() else []
        paths += [directory / name for name in ('result.json', 'interrupted-result.json')]
        result = []
        for path in sorted(paths):
            try:
                _ordinary(path, directory)
                if not path.is_file():
                    continue
                size = path.stat().st_size
                if size > MAX_FILE:
                    raise RequestError('output file exceeds size budget')
                name = path.relative_to(directory).as_posix()
                result.append(dict(path=name, bytes=size, url='/api/trip/jobs/' + job_id + '/files/' + quote(name, safe='/')))
            except (OSError, ValueError):
                continue
        return result

    def job(self, job_id):
        self._directory(job_id)
        with self._lock:
            if job_id not in self._jobs:
                raise KeyError('unknown job')
            value = deepcopy(self._jobs[job_id])
            try:
                wrapped = self._result(job_id)
                value['result'] = wrapped.get('result') if wrapped else None
                value['result_sha256'] = wrapped.get('result_sha256') if wrapped else None
            except (OSError, ValueError, KeyError) as error:
                value['result'] = None
                value['result_integrity_error'] = str(error)
            value['outputs'] = self._outputs(job_id)
            return value

    def jobs(self):
        with self._lock:
            rows = [deepcopy(v) for v in self._jobs.values()]
        return sorted(rows, key=lambda v: v.get('created_at') or '', reverse=True)

    def cancel(self, job_id):
        self._directory(job_id)
        with self._lock:
            if job_id not in self._jobs:
                raise KeyError('unknown job')
            if self._jobs[job_id]['state'] not in TERMINAL:
                self._events[job_id].set()
                value = deepcopy(self._jobs[job_id])
                value['progress'] = dict(phase='cancelling', message='Cancellation requested for this owned job only')
                self._persist(value)
        return self.job(job_id)

    def logs(self, job_id, stream='stdout'):
        if stream not in {'stdout', 'stderr'}:
            raise RequestError('stdout or stderr stream required')
        if job_id not in self._jobs:
            raise KeyError('unknown job')
        path = _ordinary(self._directory(job_id) / (stream + '.log'), self.output_root)
        size = path.stat().st_size
        with path.open('rb') as source:
            source.seek(max(0, size - MAX_LOG_RETURN))
            raw = source.read(MAX_LOG_RETURN)
        return dict(text=raw.decode('utf-8', errors='replace'), truncated=size > MAX_LOG_RETURN, bytes=size)

    def output_path(self, job_id, relative):
        if not isinstance(relative, str) or not relative or '\\' in relative or '\0' in relative:
            raise RequestError('ordinary relative artifact name required')
        rel = PurePosixPath(relative)
        if rel.is_absolute() or '..' in rel.parts or rel.as_posix() != relative:
            raise RequestError('ordinary relative artifact name required')
        if job_id not in self._jobs or relative not in {v['path'] for v in self._outputs(job_id)}:
            raise KeyError('unknown owned artifact')
        return _ordinary(self._directory(job_id) / relative, self.output_root)

    def close(self):
        with self._lock:
            self._closed = True
            for event in self._events.values():
                event.set()
        try:
            self._executor.shutdown(wait=True, cancel_futures=False)
        finally:
            # Keep the kernel owner lock until every owned worker/controller is
            # stopped. Never unlink it: another opener must lock the same inode.
            if not self._service_lock.closed:
                fcntl.flock(self._service_lock.fileno(), fcntl.LOCK_UN)
                self._service_lock.close()


def check_request(value):
    if not isinstance(value, dict) or value.get('schema') != SCHEMA or not JOB_RE.fullmatch(value.get('job_id', '')):
        raise RequestError('interactive request schema/job differs')
    if value.get('request_id') != identity({k: v for k, v in value.items() if k != 'request_id'}):
        raise RequestError('interactive request digest differs')
    validate_command({k: value[k] for k in ('action', 'parameters')})
    if value.get('physical_accepted') is not False:
        raise RequestError('interactive work cannot qualify physical design')
    cap = 1200 if value['action'] in {'campaign', 'setup-tools'} else 300
    if type(value.get('deadline_s')) not in (int, float) or not 0 < value['deadline_s'] <= cap:
        raise RequestError('bounded action deadline required')
    return value


def _loopback(handler, *, post):
    try:
        if not ipaddress.ip_address(handler.client_address[0]).is_loopback:
            return False
        host = handler.headers.get('Host', '')
        url = urlsplit('http://' + host)
        if url.username or url.password or url.path or url.query or url.fragment:
            return False
        if url.hostname not in {'127.0.0.1', 'localhost', '::1'} or (url.port or 80) != handler.server.server_port:
            return False
        if post:
            origin = urlsplit(handler.headers.get('Origin', ''))
            if origin.scheme != 'http' or origin.netloc.lower() != host.lower() or origin.path or origin.query or origin.fragment:
                return False
            if handler.headers.get('Sec-Fetch-Site', 'same-origin') != 'same-origin':
                return False
        return True
    except (ValueError, TypeError):
        return False


def _reply(handler, code, value):
    raw = encoded(value)
    handler.send_response(code)
    handler.send_header('Content-Type', 'application/json; charset=utf-8')
    handler.send_header('Content-Length', str(len(raw)))
    handler.send_header('Cache-Control', 'no-store')
    handler.send_header('X-Content-Type-Options', 'nosniff')
    handler.end_headers(); handler.wfile.write(raw)


def handle_api(handler):
    url = urlsplit(handler.path)
    if not (url.path == '/api/trip' or url.path.startswith('/api/trip/')):
        return False
    service = handler.server.trip_service
    try:
        post = handler.command == 'POST'
        if handler.command not in {'GET', 'POST'}:
            _reply(handler, 405, dict(error='GET or POST required')); return True
        if not _loopback(handler, post=post):
            _reply(handler, 403, dict(error='matching loopback Host/Origin required')); return True
        parts = url.path.strip('/').split('/')
        query = parse_qs(url.query, keep_blank_values=True)
        if post:
            if handler.headers.get('Transfer-Encoding') or handler.headers.get_content_type() != 'application/json':
                raise RequestError('bounded Content-Length application/json request required')
            length = handler.headers.get('Content-Length', '')
            if not length.isdecimal() or not 0 < int(length) <= MAX_BODY:
                _reply(handler, 413, dict(error='request body exceeds byte budget or lacks length')); return True
            if hasattr(handler, 'connection'):
                handler.connection.settimeout(10.)
            raw = handler.rfile.read(int(length))
            if len(raw) != int(length):
                raise RequestError('request body length differs')
            document = _json(raw)
            if parts == ['api', 'trip', 'jobs'] and not query:
                _reply(handler, 202, service.submit(document)); return True
            if len(parts) == 5 and parts[:3] == ['api', 'trip', 'jobs'] and parts[4] == 'cancel' and not query:
                if document != {}:
                    raise RequestError('cancel request body must be empty object')
                _reply(handler, 200, service.cancel(parts[3])); return True
        elif parts == ['api', 'trip', 'status'] and not query:
            value = service.status()
            value['publication_integrity'] = deepcopy(getattr(handler.server, 'publication_integrity', None))
            _reply(handler, 200, value); return True
        elif parts == ['api', 'trip', 'catalogue'] and not query:
            _reply(handler, 200, service.catalogue()); return True
        elif parts == ['api', 'trip', 'jobs'] and not query:
            _reply(handler, 200, dict(jobs=service.jobs())); return True
        elif len(parts) == 4 and parts[:3] == ['api', 'trip', 'jobs'] and not query:
            _reply(handler, 200, service.job(parts[3])); return True
        elif len(parts) == 5 and parts[:3] == ['api', 'trip', 'jobs'] and parts[4] == 'logs':
            if set(query) - {'stream'} or len(query.get('stream', ['stdout'])) != 1:
                raise RequestError('one stdout/stderr log stream required')
            _reply(handler, 200, service.logs(parts[3], query.get('stream', ['stdout'])[0])); return True
        elif len(parts) >= 6 and parts[:3] == ['api', 'trip', 'jobs'] and parts[4] == 'files' and not query:
            name = unquote('/'.join(parts[5:]))
            path = service.output_path(parts[3], name)
            handler.send_response(200)
            media = mimetypes.guess_type(path.name)[0] or 'application/octet-stream'
            handler.send_header('Content-Type', media)
            handler.send_header('Content-Length', str(path.stat().st_size))
            handler.send_header('X-Content-Type-Options', 'nosniff')
            handler.send_header('Content-Security-Policy', "sandbox; default-src 'none'; img-src 'self' data:; style-src 'unsafe-inline'")
            handler.send_header('Cache-Control', 'no-store')
            handler.end_headers()
            with path.open('rb') as source:
                while chunk := source.read(64 * 1024):
                    handler.wfile.write(chunk)
            return True
        _reply(handler, 404, dict(error='unknown trip API route'))
    except KeyError as error:
        _reply(handler, 404, dict(error=str(error)))
    except (ValueError, TypeError, OSError, RuntimeError) as error:
        _reply(handler, 400, dict(error=str(error), physical_accepted=False))
    return True
