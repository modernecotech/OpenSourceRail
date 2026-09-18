#!/usr/bin/env python3
"""Coordinated cold checkpoints and isolated fresh-volume recovery rehearsals.

Private checkpoint directories contain deployment credentials and encryption keys.
Source writers are stopped briefly and resumed in finally; restored controllers,
workers and schedulers stay stopped. No existing volume is a restore destination.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import signal
import socketserver
import threading
import stat
import subprocess
import sys
import time
import uuid
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[2]
DOCKER = shutil.which('docker') or str(Path.home() / 'bin/docker')


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''): h.update(block)
    return h.hexdigest()


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + '\n'); path.chmod(0o600)


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    result = importlib.util.module_from_spec(spec); spec.loader.exec_module(result)
    return result


def run(args, log, stdin=None, timeout=300):
    result = subprocess.run(args, input=stdin, text=True, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, timeout=timeout)
    log.write(result.stdout + result.stderr); log.flush()
    if result.returncode: raise RuntimeError('Recovery subprocess failed; inspect private recovery log')
    return result.stdout


def safe_relative(name):
    p = Path(name)
    if not name or p.is_absolute() or p.as_posix() != name or '..' in p.parts or '\\' in name:
        raise ValueError('Unsafe checkpoint member')
    return p


def unique_object(pairs):
    value={}
    for key,item in pairs:
        if key in value: raise ValueError('Duplicate JSON member')
        value[key]=item
    return value


def verify(directory):
    directory = directory.resolve()
    manifest = json.loads((directory / 'manifest.json').read_text(), object_pairs_hook=unique_object)
    if manifest.get('schema') != 'osr-platform-checkpoint/1' or manifest.get('complete') is not True:
        raise ValueError('Incomplete or unsupported checkpoint')
    if any(p.is_symlink() for p in directory.rglob('*')):
        raise ValueError('Checkpoint must not contain filesystem symlinks')
    if not isinstance(manifest.get('files'), dict) or not manifest['files']:
        raise ValueError('Checkpoint requires checksummed members')
    expected = set(manifest['files'])
    actual = {p.relative_to(directory).as_posix() for p in directory.rglob('*') if p.is_file()}
    if actual != expected | {'manifest.json'}: raise ValueError('Checkpoint membership differs')
    for name, record in manifest['files'].items():
        path = directory / safe_relative(name)
        if (not isinstance(record,dict) or set(record)!={'bytes','sha256'}
                or type(record['bytes']) is not int or record['bytes']<0
                or not isinstance(record['sha256'],str) or not re.fullmatch('[0-9a-f]{64}',record['sha256'])):
            raise ValueError('Invalid checksum member')
        if path.stat().st_size != record['bytes'] or sha(path) != record['sha256']:
            raise ValueError('Checkpoint file changed: ' + name)
    if not {'state.json', 'ops.zip', 'ops.signing-key'} <= expected:
        raise ValueError('Checkpoint lacks application state or signing identity')
    state = json.loads((directory / 'state.json').read_text(), object_pairs_hook=unique_object)
    if state.get('images_archive') and state['images_archive'] not in expected:
        raise ValueError('Missing captured image archive')
    for row in state['volumes'].values():
        if row['archive'] not in expected: raise ValueError('Missing volume archive')
    for service in state['services'].values():
        if not re.fullmatch(r'sha256:[0-9a-f]{64}', service['image']):
            raise ValueError('Restores require captured immutable image IDs')
        for mount in service['volumes']:
            if mount['type'] == 'volume' and mount['source'] not in state['volumes']:
                raise ValueError('Unknown checkpoint volume')
            if mount['type'] == 'bind' and mount['source'] not in expected:
                raise ValueError('Unknown checkpoint binding')
    return manifest, state


# Run inside an isolated helper container. Hash names, bytes, link targets and
# ownership/modes without following symlinks into another filesystem.
INVENTORY = '''import hashlib,json,os,stat
from pathlib import Path
root=Path('/volume');h=hashlib.sha256();count=0
for base,dirs,files in os.walk(root,followlinks=False):
 dirs.sort();files.sort()
 for p in sorted([Path(base)] + [Path(base)/n for n in dirs+files if (Path(base)/n).is_symlink() or n in files]):
  s=p.lstat();r={'path':p.relative_to(root).as_posix(),'mode':stat.S_IMODE(s.st_mode),'uid':s.st_uid,'gid':s.st_gid}
  if p.is_symlink():r['link']=os.readlink(p)
  elif p.is_file():
   f=hashlib.sha256()
   with p.open('rb') as stream:
    for block in iter(lambda:stream.read(1024*1024),b''):f.update(block)
   r['sha256']=f.hexdigest();r['bytes']=s.st_size
  elif not p.is_dir():raise ValueError('Unsupported special volume member')
  h.update(json.dumps(r,sort_keys=True).encode()+b'\\n');count+=1
print(json.dumps({'sha256':h.hexdigest(),'entries':count}))
'''


def helper(image, volume, folder, args, log, readonly=True):
    return run([DOCKER, 'run', '--rm', '--network', 'none', '--read-only', '--user', '0',
        '--mount', f'type=volume,source={volume},target=/volume' + (',readonly' if readonly else ''),
        '--mount', f'type=bind,source={folder},target=/archive' + ('' if readonly else ',readonly'),
        '--entrypoint', args[0], image, *args[1:]], log, timeout=600)


def host_processes(profile):
    found = []
    identifiers = [str((ROOT / profile[k]).resolve()).encode() for k in ('private_root', 'ops_db')]
    for proc in Path('/proc').iterdir():
        if not proc.name.isdigit(): continue
        try:
            args = [x for x in (proc / 'cmdline').read_bytes().split(b'\0') if x]
            if not any(x.endswith((b'/workbench-server.py', b'/supervision-simulator.py')) for x in args): continue
            if not any(any(x.startswith(identity) for identity in identifiers) for x in args): continue
            env = dict(x.decode().split('=', 1) for x in (proc / 'environ').read_bytes().split(b'\0') if b'=' in x)
            found.append(dict(pid=int(proc.name), argv=[x.decode() for x in args], env=env))
        except (FileNotFoundError, ProcessLookupError): continue
    if len(found) != 2: raise ValueError('Expected exactly one source Workbench and simulator')
    return found


def host_alive(pid):
    try:
        return Path("/proc", str(pid), "stat").read_text().rsplit(")", 1)[1].split()[0] != "Z"
    except FileNotFoundError:
        return False


def stop_host(row):
    pid = row['pid']
    children = subprocess.run(['pgrep', '-P', str(pid)], capture_output=True, text=True).stdout.split()
    for child in children:
        try: os.kill(int(child), signal.SIGTERM)
        except ProcessLookupError: pass
    os.kill(pid, signal.SIGTERM)
    deadline = time.monotonic() + 10
    while host_alive(pid) and time.monotonic() < deadline: time.sleep(.1)
    if host_alive(pid): raise RuntimeError('Source host writer did not stop')


def checkpoint(profile_path, output, report_path):
    profile = json.loads(profile_path.read_text())
    if profile.get('schema') != 'osr-recovery-profile/1': raise ValueError('Unknown profile')
    output = output.resolve()
    if not output.is_relative_to((ROOT / 'var').resolve()):
        raise ValueError('Credential-bearing checkpoints must be under the private var directory')
    output.mkdir(parents=True, exist_ok=False, mode=0o700)
    report = dict(schema='osr-platform-checkpoint-result/1', passed=False, source_resumed=False)
    state = dict(profile=profile, services={}, volumes={})
    capture_started = time.monotonic()
    runner_hash = sha(Path(__file__))
    hosts = host_processes(profile); stopped_hosts = []; containers = []; stopped = []
    logpath = output.parent / (output.name + '-capture.log')
    with logpath.open('w') as log:
        logpath.chmod(0o600)
        try:
            for project in profile['projects']:
                if not re.fullmatch('[a-z0-9][a-z0-9-]+', project): raise ValueError('Invalid project')
                ids = run([DOCKER, 'ps', '-q', '--filter', 'label=com.docker.compose.project=' + project], log).split()
                if not ids: raise ValueError('Source project is not running')
                containers += json.loads(run([DOCKER, 'inspect', *ids], log))
            if len({c['Config']['Labels']['com.docker.compose.service'] for c in containers}) != len(containers):
                raise ValueError('Duplicate service names across source projects')
            # Archive immutable image IDs before stopping writers. Saving by ID
            # avoids restoring mutable repository tags over a newer deployment.
            state['images_archive'] = 'images.tar'
            run([DOCKER, 'image', 'save', '--output', str(output / state['images_archive']),
                *sorted({c['Image'] for c in containers})], log, timeout=900)
            for row in hosts:
                stopped_hosts.append(row); stop_host(row)
            # Stop ingestion before ERP, so in-flight condition deliveries finish or
            # remain in the durable outbox for idempotent reconciliation.
            ordered = sorted(containers, key=lambda c: (c['Config']['Labels']['com.docker.compose.service'] != 'integration',
                c['Config']['Labels']['com.docker.compose.service'] in ('db', 'redis-cache', 'redis-queue')))
            for c in ordered:
                stopped.append(c['Id']); run([DOCKER, 'stop', '--time', '10', c['Id']], log)
            frozen = datetime.now(timezone.utc).isoformat()
            for c in containers:
                name = c['Config']['Labels']['com.docker.compose.service']; cfg = c['Config']
                service = dict(image=c['Image'], entrypoint=cfg['Entrypoint'], command=cfg['Cmd'],
                    environment=cfg['Env'], working_dir=cfg['WorkingDir'], user=cfg['User'], volumes=[])
                for m in c['Mounts']:
                    if m['Type'] == 'volume':
                        key = 'v' + str(list(state['volumes']).index(m['Name'])) if m['Name'] in state['volumes'] else 'v' + str(len(state['volumes']))
                        if m['Name'] not in state['volumes']:
                            state['volumes'][m['Name']] = dict(key=key, archive='volumes/' + key + '.tar')
                        source = m['Name']
                    elif m['Type'] == 'bind':
                        src = Path(m['Source'])
                        if not src.is_file() or src.is_symlink(): raise ValueError('Only regular-file bindings supported')
                        source = 'bindings/' + sha(src) + '-' + src.name
                        dest = output / source; dest.parent.mkdir(exist_ok=True); shutil.copyfile(src, dest); dest.chmod(0o600)
                    else: raise ValueError('Unsupported persistent mount')
                    mount = dict(type=m['Type'], source=source, target=m['Destination'], read_only=not m['RW'])
                    if m['Type'] == 'bind': mount['mode'] = stat.S_IMODE(src.stat().st_mode)
                    service['volumes'].append(mount)
                state['services'][name] = service
            required = {'backend', 'frontend', 'db', 'integration', 'fuxa'}
            if not required <= state['services'].keys(): raise ValueError('Missing required platform service')
            image = state['services']['backend']['image']; (output / 'volumes').mkdir()
            for name, row in state['volumes'].items():
                row['inventory'] = json.loads(helper(image, name, output, ['python', '-c', INVENTORY], log))
                helper(image, name, output, ['tar', '-C', '/volume', '-cpf', '/archive/' + row['archive'], '.'], log)
            ops = module('recovery_ops', 'tools/automation/ops-core-backup.py')
            db = ROOT / profile['ops_db']
            ops.create_backup(db, db.parent / 'ops-evidence', output / 'ops.zip')
            shutil.copyfile(db.with_suffix('.signing-key'), output / 'ops.signing-key')
            for name, source in profile['auxiliary'].items():
                dest = output / 'auxiliary' / safe_relative(name); src = ROOT / source
                if src.is_dir(): shutil.copytree(src, dest)
                else: dest.parent.mkdir(parents=True, exist_ok=True); shutil.copyfile(src, dest)
            write(output / 'state.json', state)
            files = {p.relative_to(output).as_posix(): dict(bytes=p.stat().st_size, sha256=sha(p))
                     for p in output.rglob('*') if p.is_file()}
            write(output / 'manifest.json', dict(schema='osr-platform-checkpoint/1', complete=True,
                frozen_at=frozen, runner_sha256=runner_hash, commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(), files=files))
            verify(output); report.update(passed=True, volumes=len(state['volumes']), services=len(state['services']),
                frozen_at=frozen, manifest_sha256=sha(output / 'manifest.json'))
        finally:
            # Restore only the source containers/processes that this invocation stopped.
            errors = []
            for identity in reversed(stopped):
                try: run([DOCKER, 'start', identity], log)
                except Exception as exc: errors.append(type(exc).__name__)
            for i, row in enumerate(stopped_hosts):
                if host_alive(row['pid']):
                    row['restarted_pid'] = row['pid']
                    errors.append('SourceHostDidNotStop')
                    continue
                hostlog = output.parent / (output.name + f'-source-{i}.log')
                with hostlog.open('ab') as stream:
                    child = subprocess.Popen(row['argv'], env=row['env'], cwd=ROOT,
                        stdout=stream, stderr=subprocess.STDOUT, start_new_session=True)
                hostlog.chmod(0o600); row['restarted_pid'] = child.pid
            registry = [dict(name='workbench' if any(a.endswith('workbench-server.py') for a in row['argv']) else 'simulator', pid=row['restarted_pid']) for row in stopped_hosts]
            if registry: write(ROOT / profile['private_root'] / 'processes.json', registry)
            for url in profile.get('source_health_urls', []):
                try: wait_http(url)
                except Exception as exc: errors.append(type(exc).__name__)
            report['source_resumed'] = not errors
            report['restart_errors'] = errors
            report['capture_and_resume_seconds'] = round(time.monotonic()-capture_started,3)
            write(report_path, report)
    if not report['passed'] or not report['source_resumed']: raise RuntimeError('Checkpoint or source resume failed')
    print(json.dumps(report))


def clone_config(state, checkpoint_dir, private, project, port):
    services = {}; volumes = {r['key']: {} for r in state['volumes'].values()}
    for name, original in state['services'].items():
        service = {k:v for k,v in original.items() if k != 'volumes' and v is not None}
        service['pull_policy'] = 'never'
        service['restart'] = 'no'; service['networks'] = ['default']; service['volumes'] = []
        for mount in original['volumes']:
            m = dict(mount)
            mode = m.pop('mode', 0o644 if m['target'].endswith('/security_headers.conf') else 0o600)
            if m['type'] == 'volume': m['source'] = state['volumes'][m['source']]['key']
            else:
                source = checkpoint_dir / safe_relative(m['source']); dest = private / m['source']
                dest.parent.mkdir(parents=True, exist_ok=True); shutil.copyfile(source, dest)
                if name == 'integration' and m['target'].endswith('integration.json'):
                    cfg = json.loads(dest.read_text()); cfg.pop('erp', None)  # Reconcile explicitly after integrity checks.
                    write(dest, cfg)
                dest.chmod(mode)
                m['source'] = str(dest)
            service['volumes'].append(m)
        services[name] = service
    return dict(name=project, services=services, volumes=volumes, networks={'default': {'internal': True}})


def wait_http(url, headers=None):
    end = time.monotonic() + 120
    while time.monotonic() < end:
        try:
            with urlopen(Request(url, headers=headers or {}), timeout=3) as response:
                if response.status == 200: return response.read()
        except OSError: pass
        time.sleep(1)
    raise RuntimeError('Restored HTTP service did not become ready')


# Full-duplex byte forwarding over Docker's local exec channel. This keeps the
# recovered services on an internal-only network even on engines that suppress
# published ports for internal networks. Destinations are fixed by the runner.
RELAY = """import os,select,socket,sys
sock=socket.create_connection((sys.argv[1],int(sys.argv[2])),timeout=15);sock.settimeout(None)
inputs=[0,sock]
while True:
 ready,_,_=select.select(inputs,[],[],60)
 if not ready:break
 for source in ready:
  if source==0:
   data=os.read(0,65536)
   if data:sock.sendall(data)
   else:inputs.remove(0);sock.shutdown(socket.SHUT_WR)
  else:
   data=sock.recv(65536)
   if not data:sys.exit(0)
   sys.stdout.buffer.write(data);sys.stdout.buffer.flush()
"""


def tunnel(container, destination, target, port):
    class Tunnel(socketserver.ThreadingTCPServer):
        allow_reuse_address=True
        daemon_threads=True
    class Handler(socketserver.BaseRequestHandler):
        def handle(self):
            proc=subprocess.Popen([DOCKER,'exec','-i',container,'python','-u','-c',RELAY,destination,str(target)],
                stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.DEVNULL)
            with self.server.lock:self.server.children.add(proc)
            self.request.settimeout(60)
            def upload():
                try:
                    while data:=self.request.recv(65536):proc.stdin.write(data);proc.stdin.flush()
                except (OSError,ValueError):pass
                finally:
                    try:proc.stdin.close()
                    except OSError:pass
            thread=threading.Thread(target=upload,daemon=True);thread.start()
            try:
                while data:=proc.stdout.read1(65536):self.request.sendall(data)
            except OSError:pass
            finally:
                proc.kill();proc.wait();proc.stdout.close()
                with self.server.lock:self.server.children.discard(proc)
    server=Tunnel(('127.0.0.1',port),Handler);server.children=set();server.lock=threading.Lock()
    thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
    return server,thread


def close_tunnel(server,thread):
    server.shutdown();server.server_close();thread.join()
    with server.lock:
        for proc in list(server.children):
            try:proc.kill()
            except ProcessLookupError:pass


def rehearse(checkpoint_dir, report_path, port):
    checkpoint_dir = checkpoint_dir.resolve(); manifest, state = verify(checkpoint_dir)
    project = 'osr-recovery-' + uuid.uuid4().hex[:12]
    private = ROOT / 'var/recovery' / project; private.mkdir(parents=True, mode=0o700)
    report = dict(schema='osr-platform-recovery-result/1', passed=False, project=project,
        checkpoint_sha256=sha(checkpoint_dir / 'manifest.json'), fresh_volumes=True,
        external_network_access=False, controllers_started=False, independent_acceptance=False,
        commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        working_tree_dirty=bool(subprocess.check_output(['git','status','--porcelain'],cwd=ROOT,text=True).strip()),
        source_sha256={name:sha(ROOT / name) for name in ['tools/automation/platform-recovery.py',
            'deployment/recovery/audit-erp.py','deployment/recovery/reconcile-gateway.py']})
    cfg = clone_config(state, checkpoint_dir, private, project, port); write(private / 'compose.json', cfg)
    compose = [DOCKER, 'compose', '-p', project, '-f', str(private / 'compose.json')]
    created = []; tunnels = []; workbench = None; logpath = private / 'recovery.log'
    started = time.monotonic()
    with logpath.open('w') as log:
        logpath.chmod(0o600)
        try:
            if run([DOCKER, 'volume', 'ls', '-q', '--filter', 'label=com.docker.compose.project=' + project], log).strip():
                raise ValueError('Restore project already has volumes')
            if state.get('images_archive'):
                run([DOCKER,'image','load','--input',str(checkpoint_dir / state['images_archive'])],log,timeout=900)
                report['captured_images_loaded'] = True
            else:
                report['captured_images_loaded'] = False  # Legacy cache-only checkpoints.
            for image in {service['image'] for service in state['services'].values()}:
                run([DOCKER,'image','inspect',image],log)
            image = state['services']['backend']['image']
            for row in state['volumes'].values():
                name = project + '_' + row['key']
                if subprocess.run([DOCKER,'volume','inspect',name],capture_output=True).returncode == 0:
                    raise ValueError('Refusing existing restore volume')
                run([DOCKER,'volume','create','--label','com.docker.compose.project='+project,
                    '--label','com.docker.compose.volume='+row['key'],name],log);created.append(name)
                helper(image,name,checkpoint_dir,['tar','-C','/volume','-xpf','/archive/'+row['archive']],log,False)
                actual = json.loads(helper(image,name,private,['python','-c',INVENTORY],log))
                if actual != row['inventory']: raise ValueError('Restored volume inventory differs')
            report['volume_inventories_verified'] = len(created)
            ops = module('recovery_ops', 'tools/automation/ops-core-backup.py')
            ops.restore_backup(checkpoint_dir / 'ops.zip', private / 'ops')
            shutil.copyfile(checkpoint_dir / 'ops.signing-key', private / 'ops/data/ops-core.signing-key')
            report['ops_signing_key_preserved'] = sha(private / 'ops/data/ops-core.signing-key') == sha(checkpoint_dir / 'ops.signing-key')
            core=module('recovery_ops_core','tools/automation/ops-core-server.py')
            key=(private / 'ops/data/ops-core.signing-key').read_bytes(); signed=0
            with core.connect(private / 'ops/data/ops-core.sqlite3') as db:
                for city in state['profile']['cities']:
                    for records in core.load_state(db,city).values():
                        if not isinstance(records,list):continue
                        for record in records:
                            if record.get('signature'):
                                if not core._verify_attestation(record,key):raise ValueError('Restored Ops Core attestation failed')
                                signed+=1
            report['ops_attestations_verified']=signed
            run(compose + ['up','-d','db','redis-cache','redis-queue'],log)
            # Wait for native MariaDB readiness without injecting database secrets into commands.
            end=time.monotonic()+90
            while time.monotonic()<end:
                probe=subprocess.run(compose+['exec','-T','db','healthcheck.sh','--connect','--innodb_initialized'],capture_output=True)
                if probe.returncode==0:break
                time.sleep(1)
            else:raise RuntimeError('Restored database did not become ready')
            run(compose + ['up','-d','backend','websocket','integration'],log)
            run(compose + ['up','-d','frontend','fuxa'],log)
            relay=run(compose+['ps','-q','integration'],log).strip()
            addresses={}
            for offset,(name,target) in enumerate([('frontend',8080),('integration',8092),('fuxa',1881)]):
                tunnels.append(tunnel(relay,name,target,port+offset))
                addresses[name]=f'http://127.0.0.1:{port+offset}'
            for name,path in [('frontend','/api/method/ping'),('integration','/health'),('fuxa','/')]:
                wait_http(addresses[name]+path)
            audit = (ROOT / 'deployment/recovery/audit-erp.py').read_text()
            def erp_audit():
                return json.loads(run(compose + ['exec','-T','-e','OSR_RESTORE_SITE='+state['profile']['site'],
                    'backend','env/bin/python','-'],log,stdin=audit))
            before = erp_audit()
            binding = next(m for m in state['services']['integration']['volumes']
                if m['type']=='bind' and m['target'].endswith('integration.json'))
            credentials = json.loads((checkpoint_dir / binding['source']).read_text())
            script = 'CONFIG = ' + repr(credentials) + '\n' + (ROOT / 'deployment/recovery/reconcile-gateway.py').read_text()
            report['queue_reconciliation'] = json.loads(run(compose + ['exec','-T','integration','python','-'],log,stdin=script))
            after = erp_audit()
            if before != after: raise ValueError('Lost-reply replay changed native ERP records')
            report['erp_records'] = after
            # Restore the host-side twin/UI context and signing identity. The
            # evidence alias stays within this private recovery directory.
            shutil.copytree(checkpoint_dir / 'auxiliary', private / 'auxiliary')
            (private / 'ops/data/evidence').mkdir(exist_ok=True)
            (private / 'ops/data/ops-evidence').symlink_to('evidence', target_is_directory=True)
            env = {**os.environ,'OSR_ERP_URL':addresses['frontend'],
                'OSR_INTEGRATION_URL':addresses['integration'], 'OSR_FUXA_URL':addresses['fuxa'],
                'OSR_SUPERVISION_CONFIG':str(private / binding['source']),
                'OSR_SUPERVISION_ROOT':str(private / 'auxiliary/supervision'),
                'OSR_SUPERVISION_PROFILES':str(private / 'auxiliary/profiles'),
                'OSR_ERP_SNAPSHOT':str(private / 'auxiliary/operating-twins.json')}
            workbench = subprocess.Popen([sys.executable,str(ROOT / 'tools/automation/workbench-server.py'),
                '--port',str(port+3),'--city-port',str(port+4),'--db',str(private / 'ops/data/ops-core.sqlite3'),
                '--project',str(private / 'auxiliary/city-project')],cwd=ROOT,env=env,
                stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
            wait_http(f'http://127.0.0.1:{port+3}/api/workbench/services')
            for city in state['profile']['cities']:
                snapshot=json.loads(wait_http(f'http://127.0.0.1:{port+3}/api/lifecycle/snapshot?city={city}&environment=simulation'))
                if not snapshot.get('assets') or any(a['city']!=city for a in snapshot['assets']):
                    raise ValueError('Restored lifecycle city scope differs')
                operations=json.loads(wait_http(f'http://127.0.0.1:{port+3}/api/ops-core/{city}'))
                if operations.get('city_slug')!=city or 'state' not in operations:
                    raise ValueError('Restored Ops Core city scope differs')
            report.update(http_services_verified=['ERPNext','integration','FUXA','Workbench','Ops Core'],passed=True,
                recovery_seconds=round(time.monotonic()-started,3),
                scope='Cold volume/file/ownership integrity; native records and encryption; queue lost-reply reconciliation; restored Workbench city/lifecycle/Ops Core HTTP. Controllers, workers and schedulers remain stopped; production RTO/RPO and independent acceptance remain open.')
        finally:
            for server,thread in tunnels: close_tunnel(server,thread)
            if workbench is not None:
                workbench.terminate()
                try: workbench.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    os.killpg(workbench.pid,signal.SIGKILL);workbench.wait()
            try:
                run(compose+['down','--volumes','--remove-orphans'],log)
                for name in created:
                    if subprocess.run([DOCKER,'volume','inspect',name],capture_output=True).returncode==0:run([DOCKER,'volume','rm',name],log)
                report['isolated_resources_removed']=True
            except Exception as exc:report['cleanup_error']=type(exc).__name__
            write(report_path,report)
    print(json.dumps(report))
    if not report['passed'] or not report.get('isolated_resources_removed'):
        raise RuntimeError('Recovery verification or cleanup failed')


def main():
    os.umask(0o077)
    def interrupted(signum, frame):
        raise KeyboardInterrupt('Recovery interrupted; resuming source or cleaning isolated restore')
    signal.signal(signal.SIGTERM, interrupted)
    parser=argparse.ArgumentParser(description=__doc__);subs=parser.add_subparsers(dest='action',required=True)
    capture=subs.add_parser('checkpoint');capture.add_argument('--profile',type=Path,required=True);capture.add_argument('--output',type=Path,required=True);capture.add_argument('--report',type=Path,required=True)
    restore=subs.add_parser('rehearse');restore.add_argument('checkpoint',type=Path);restore.add_argument('--report',type=Path,required=True);restore.add_argument('--port',type=int,default=28880)
    check=subs.add_parser('verify');check.add_argument('checkpoint',type=Path)
    args=parser.parse_args()
    if args.action=='checkpoint':checkpoint(args.profile,args.output,args.report)
    elif args.action=='rehearse':rehearse(args.checkpoint,args.report,args.port)
    else:verify(args.checkpoint);print('Checkpoint integrity verified')


if __name__=='__main__':main()
