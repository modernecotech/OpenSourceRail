#!/usr/bin/env python3
"""Generate and operate reproducible OSR equipment supervision and lifecycle links."""
import argparse
import base64
import gzip
import hashlib
import hmac
import importlib.util
import json
import os
from pathlib import Path
import secrets
import shutil
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'services/integration'))
from osr_integration.config import build_package, merge
from osr_integration.fuxa import project
from osr_integration.server import request_json
from osr_integration.engineering import package as engineering_package, execution_proposal

PRIVATE = ROOT / 'var/supervision'
GENERIC = ROOT / 'deployment/supervision/config/generic.json'
spec = importlib.util.spec_from_file_location('erp_city', ROOT / 'tools/automation/erpnext-city.py')
cities = importlib.util.module_from_spec(spec); spec.loader.exec_module(cities)


def write_private(path, value):
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, 'w') as f:
        f.write(value)
    path.chmod(0o600)


def configuration():
    return json.loads((PRIVATE / 'integration.json').read_text())


def api(path, data=None, role='engineer', query=''):
    principal = next(p for p in configuration()['principals'] if p['role'] == role)
    return request_json('http://127.0.0.1:8092' + path + query, data, {'Authorization': 'Bearer ' + principal['token']})


def prepare(slug, environment='simulation', first_site=False, first_vehicle=False):
    path, _ = cities.catalogue()[slug]
    override_path = path.parent / 'operations/supervision.json'
    override = json.loads(override_path.read_text()) if override_path.exists() else {'city': slug}
    if override['city'] != slug:
        raise ValueError('City profile identity mismatch')
    source = path.parent / 'operations' / f'{slug}-operations.json.gz'
    if not source.exists():
        raise ValueError(f'Generate city first: ./osr city {slug}')
    bundle = json.loads(gzip.decompress(source.read_bytes()))
    if first_site:
        override['sites'] = [next(a['asset_id'] for a in bundle['assets'] if a['asset_type'] == 'station')]
    if first_vehicle:
        override['sites'] = list(override.get('sites', [])) + [next(a['asset_id'] for a in bundle['assets'] if a['asset_type'] == 'rolling-stock')]
    p = build_package(json.loads(GENERIC.read_text()), override, bundle['assets'], bundle['project_twin']['revision_id'], environment)
    folder = ROOT / 'build/supervision' / slug / environment; folder.mkdir(parents=True, exist_ok=True)
    for name, data in [('package.json', p), ('fuxa-project.json', project([p]))]:
        (folder / name).write_text(json.dumps(data, indent=2) + '\n')
    return folder


def compose(args, **kwargs):
    docker = shutil.which('docker') or str(Path.home() / 'bin/docker')
    env = {**os.environ, 'PATH': str(Path(docker).parent) + ':' + os.environ['PATH']}
    return subprocess.run([docker, 'compose', '-f', str(ROOT / 'deployment/supervision/compose.yaml')] + args, check=True, env=env, **kwargs)


def init():
    PRIVATE.mkdir(parents=True, exist_ok=True, mode=0o700)
    if not (PRIVATE / 'integration.json').exists():
        names = {'controller': 'simulator', 'operator': 'pilot-operator', 'engineer': 'pilot-engineer', 'reviewer': 'pilot-reviewer', 'inspector': 'pilot-inspector', 'maintainer': 'pilot-maintainer', 'viewer': 'workbench'}
        cfg = {'principals': [dict(subject=name, role=role, token=secrets.token_urlsafe(32), cities=['samawah', 'mosul'], environments=['simulation']) for role, name in names.items()]}
        write_private(PRIVATE / 'integration.json', json.dumps(cfg, indent=2))
    if not (PRIVATE / 'fuxa.json').exists():
        cfg = {'secret': secrets.token_hex(32), 'admin_password': secrets.token_urlsafe(24), 'operator_password': secrets.token_urlsafe(24)}
        write_private(PRIVATE / 'fuxa.json', json.dumps(cfg, indent=2))
    f = json.loads((PRIVATE / 'fuxa.json').read_text())
    settings = {'version': 1.4, 'uiPort': 1881, 'secureEnabled': True, 'secretCode': f['secret'], 'tokenExpiresIn': '1h', 'daqEnabled': False, 'nodeRedEnabled': False, 'allowedOrigins': ['http://127.0.0.1:1881', 'http://localhost:1881'], 'broadcastAll': True}
    write_private(PRIVATE / 'fuxa-settings.js', 'module.exports = {...require("../settings.default.js"), ...' + json.dumps(settings) + '};\n')
    print('Private service credentials:', PRIVATE)


def fuxa_api(path, body=None, token=None):
    cfg = json.loads((PRIVATE / 'fuxa.json').read_text())
    if token is None:
        token = request_json('http://127.0.0.1:1881/api/signin', {'username': 'admin', 'password': cfg['admin_password']})['data']['token']
    return request_json('http://127.0.0.1:1881' + path, body, {'x-access-token': token})


def setup_fuxa():
    # Bootstrap using configured signing secret, through the supported users API.
    # No direct writes to FUXA's internal user database.
    cfg = json.loads((PRIVATE / 'fuxa.json').read_text())
    b64 = lambda x: base64.urlsafe_b64encode(json.dumps(x, separators=(',', ':')).encode()).rstrip(b'=')
    msg = b64({'alg': 'HS256', 'typ': 'JWT'}) + b'.' + b64({'id': 'admin', 'groups': -1, 'exp': int(time.time()) + 60})
    token = (msg + b'.' + base64.urlsafe_b64encode(hmac.new(cfg['secret'].encode(), msg, hashlib.sha256).digest()).rstrip(b'=')).decode()
    for name, fullname, groups, password in [('admin', 'OSR configuration editor', -1, cfg['admin_password']), ('operator', 'OSR station operator', 1, cfg['operator_password'])]:
        fuxa_api('/api/users', {'params': {'username': name, 'fullname': fullname, 'groups': groups, 'password': password, 'info': '{}'}}, token)
    print('FUXA editor and operator accounts configured; passwords remain in var/supervision/fuxa.json')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    for action in ['init', 'up', 'status', 'setup-fuxa', 'backup', 'init-configs', 'validate', 'simulate']:
        sub.add_parser(action)
    p = sub.add_parser('connect-erp'); p.add_argument('cities', nargs='+')
    p = sub.add_parser('prepare'); p.add_argument('city'); p.add_argument('--environment', choices=['simulation', 'physical'], default='simulation'); p.add_argument('--first-site', action='store_true'); p.add_argument('--first-vehicle', action='store_true')
    p = sub.add_parser('apply'); p.add_argument('package', type=Path); p.add_argument('--expected')
    p = sub.add_parser('import-fuxa'); p.add_argument('packages', nargs='+', type=Path)
    p = sub.add_parser('engineering'); p.add_argument('manifest', type=Path); p.add_argument('--output', required=True, type=Path)
    p = sub.add_parser('execution-proposal'); p.add_argument('engineering', type=Path); p.add_argument('mapping', type=Path); p.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    if args.command == 'init': init()
    elif args.command == 'up': compose(['up', '-d', '--build'])
    elif args.command == 'status': compose(['ps'])
    elif args.command == 'simulate':
        subprocess.run(['cargo', 'build', '-p', 'osr-sim', '--example', 'operating_bridge'], cwd=ROOT, check=True)
        directory = Path.home() / '.config/systemd/user'; directory.mkdir(parents=True, exist_ok=True)
        script = json.dumps(str(ROOT / 'tools/automation/supervision-simulator.py').replace('%', '%%'))
        (directory / 'osr-supervision-simulator.service').write_text('[Unit]\nDescription=OSR simulated station telemetry\n[Service]\nUMask=0077\nRestart=always\nRestartSec=5\nExecStart=/usr/bin/python3 ' + script + '\n[Install]\nWantedBy=default.target\n')
        subprocess.run(['systemctl', '--user', 'daemon-reload'], check=True)
        subprocess.run(['systemctl', '--user', 'enable', 'osr-supervision-simulator'], check=True)
        subprocess.run(['systemctl', '--user', 'restart', 'osr-supervision-simulator'], check=True)
    elif args.command == 'setup-fuxa': setup_fuxa()
    elif args.command == 'connect-erp':
        import uuid
        scope = []
        for slug in args.cities:
            path, _ = cities.catalogue()[slug]
            cfg = json.loads((path.parent / 'operations/supervision.json').read_text())
            scope.append(dict(city=slug, project=cfg['erp_project']))
        task = 'osr-supervision-' + uuid.uuid4().hex
        local = PRIVATE / (task + '.json'); write_private(local, json.dumps(scope))
        remote = '/tmp/' + task + '.json'; output = '/tmp/' + task + '-credentials.json'
        docker = shutil.which('docker') or str(Path.home() / 'bin/docker')
        erp = [docker, 'compose', '--env-file', str(ROOT / 'var/erpnext/local.env'), '-f', str(ROOT / 'deployment/erpnext/compose.yaml')]
        env = {**os.environ, 'PATH': str(Path(docker).parent) + ':' + os.environ['PATH']}
        try:
            subprocess.run(erp + ['cp', str(local), 'backend:' + remote], check=True, env=env)
            subprocess.run([str(ROOT / 'osr'), 'erp', 'bench', 'execute', 'osr_erpnext.integration.provision_service', '--kwargs', json.dumps(dict(path=remote,output=output))], check=True)
            subprocess.run(erp + ['cp', 'backend:' + output, str(local)], check=True, env=env)
            cfg = configuration(); cfg['erp'] = json.loads(local.read_text())
            for principal in cfg['principals']:
                principal['cities'] = sorted(set(principal['cities'] + args.cities))
            write_private(PRIVATE / 'integration.json', json.dumps(cfg, indent=2))
        finally:
            local.unlink(missing_ok=True)
            subprocess.run(erp + ['exec', '-T', 'backend', 'rm', '-f', remote, output], check=True, env=env)
        compose(['restart', 'integration'])
    elif args.command == 'init-configs':
        count = 0
        for slug, (path, _) in cities.catalogue().items():
            target = path.parent / 'operations/supervision.json'
            if not target.exists():
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(json.dumps({'schema': 'osr-supervision-profile/1', 'city': slug, 'bindings': {}}, indent=2) + '\n'); count += 1
        print('Created profiles:', count)
    elif args.command == 'validate':
        for slug, (path, _) in cities.catalogue().items():
            cfg = json.loads((path.parent / 'operations/supervision.json').read_text())
            if cfg['city'] != slug: raise ValueError('City identity mismatch')
            build_package(json.loads(GENERIC.read_text()), {**cfg, 'sites': []}, [{'asset_type': 'station', 'asset_id': 'validation', 'name': 'Validation station'}], 'validation')
        print('Validated profiles:', len(cities.catalogue()))
    elif args.command == 'prepare': print(prepare(args.city, args.environment, args.first_site, args.first_vehicle))
    elif args.command == 'apply': print(json.dumps(api('/packages', {'package': json.loads(args.package.read_text()), 'expected': args.expected}), indent=2))
    elif args.command == 'import-fuxa':
        old = fuxa_api('/api/project')
        folder = PRIVATE / 'backups'; folder.mkdir(exist_ok=True)
        write_private(folder / f'fuxa-before-{time.time_ns()}.json', json.dumps(old))
        fuxa_api('/api/project', project([json.loads(p.read_text()) for p in args.packages]))
        print('FUXA project imported; previous project backed up')
    elif args.command in ('engineering', 'execution-proposal'):
        result = engineering_package(ROOT, json.loads(args.manifest.read_text())) if args.command == 'engineering' else execution_proposal(json.loads(args.engineering.read_text()), json.loads(args.mapping.read_text()))
        args.output.parent.mkdir(parents=True, exist_ok=True); args.output.write_text(json.dumps(result, indent=2) + '\n'); print(args.output)
    elif args.command == 'backup':
        folder = PRIVATE / 'backups' / str(time.time_ns()); folder.mkdir(parents=True)
        compose(['exec', '-T', 'integration', 'python', '-c', 'from osr_integration.store import Store; Store("/data/integration.sqlite").backup("/data/backup.sqlite")'])
        compose(['cp', 'integration:/data/backup.sqlite', str(folder / 'integration.sqlite')])
        write_private(folder / 'fuxa-project.json', json.dumps(fuxa_api('/api/project')))
        for name in ['integration.json', 'fuxa.json', 'fuxa-settings.js']:
            write_private(folder / name, (PRIVATE / name).read_text())
        print('Consistent integration backup and FUXA project export:', folder)


if __name__ == '__main__':
    main()
