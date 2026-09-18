#!/usr/bin/env python3
"""Isolated, repeatable Samawah city acceptance against real installed applications."""
import argparse
import importlib.util
import json
import os
from pathlib import Path
import secrets
import signal
import shutil
import subprocess
import sys
import time
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[2]
PRIVATE = ROOT / 'var/city-example'
OUTPUT = ROOT / 'build/city-example'
SITE = 'osr-example.localhost'
PORTS = dict(erp=8180, workbench=8190, city=8191, gateway=8192, fuxa=1981)
DOCKER = shutil.which('docker') or str(Path.home() / 'bin/docker')
sys.path.insert(0, str(ROOT / 'services/integration'))
sys.path.insert(0, str(ROOT / 'deployment/erpnext/apps/osr_erpnext'))
from osr_integration.server import request_json


def module(name, filename):
    spec = importlib.util.spec_from_file_location(name, ROOT / filename)
    result = importlib.util.module_from_spec(spec); spec.loader.exec_module(result)
    return result


def write(path, value, private=False):
    path.parent.mkdir(parents=True, exist_ok=True)
    if not isinstance(value, str): value = json.dumps(value, indent=2) + '\n'
    with open(path, 'w', opener=lambda p, flags: os.open(p, flags, 0o600 if private else 0o644)) as f: f.write(value)
    if private: path.chmod(0o600)


def command(args, log, stdin=None):
    with (OUTPUT / (log + '.log')).open('a') as stream:
        result = subprocess.run(args, input=stdin, text=True, cwd=ROOT, stdout=stream, stderr=subprocess.STDOUT)
    if result.returncode: raise RuntimeError(f'{log} failed; see build/city-example/{log}.log')


def compose(which, *args):
    assert which in {'erp', 'supervision'}
    return [DOCKER, 'compose', '-p', 'osr-example-' + which, '-f', str(PRIVATE / (which + '.json')), *args]


def backend(phase, data=None):
    script = (ROOT / 'deployment/example-city/erp-scenario.py').read_text()
    prefix = 'INPUT = ' + repr(dict(site=SITE, phase=phase, **(data or {}))) + '\n'
    result = subprocess.run(compose('erp', 'exec', '-T', 'backend', 'env/bin/python'), input=prefix+script,
                            text=True, capture_output=True, cwd=ROOT)
    write(OUTPUT / ('erp-' + phase + '.log'), result.stdout + result.stderr)
    if result.returncode: raise RuntimeError('ERP phase failed: ' + phase)
    return json.loads(next(line.removeprefix('OSR_RESULT:') for line in reversed(result.stdout.splitlines()) if line.startswith('OSR_RESULT:')))


def copy_in(path, remote):
    command(compose('erp', 'cp', str(path), 'backend:'+remote), 'transfer')
    command(compose('erp', 'exec', '-T', '--user', 'root', 'backend', 'chown', 'frappe:frappe', remote), 'transfer')
    command(compose('erp', 'exec', '-T', '--user', 'root', 'backend', 'chmod', '600', remote), 'transfer')


def wait_http(url, timeout=180):
    end = time.monotonic() + timeout
    while time.monotonic() < end:
        try:
            with urlopen(url, timeout=3) as response:
                if response.status == 200: return
        except OSError: pass
        time.sleep(2)
    raise RuntimeError('Service did not become ready: ' + url)


def here_erp():
    return ROOT/'deployment/erpnext/compose.yaml'


def setup():
    PRIVATE.mkdir(parents=True, exist_ok=True, mode=0o700); PRIVATE.chmod(0o700)
    OUTPUT.mkdir(parents=True, exist_ok=True)
    envpath = PRIVATE / 'local.env'
    if not envpath.exists():
        write(envpath, f'DB_PASSWORD={secrets.token_hex(24)}\nADMIN_PASSWORD={secrets.token_hex(24)}\nSITE_NAME={SITE}\nERP_PORT={PORTS["erp"]}\n', True)
    # Resolve the pinned production composition into its own project and volumes.
    # Resolve configuration upgrades while retaining isolated volume identities.
    resolved = subprocess.check_output([DOCKER,'compose','--env-file',str(envpath),'--profile','setup','-f',str(ROOT/'deployment/erpnext/compose.yaml'),'config','--format','json'],text=True)
    config = json.loads(resolved); config.pop('name', None)
    command([DOCKER,'compose','--env-file',str(envpath),'-f',str(here_erp()) ,'build','backend'],'build-erp')
    for volume in config.get('volumes', {}).values(): volume.pop('name', None)
    for network in config.get('networks', {}).values(): network.pop('name', None)
    image = config['services']['backend']['image']
    headers = subprocess.check_output([DOCKER,'run','--rm','--entrypoint','cat',image,'/etc/nginx/snippets/security_headers.conf'],text=True)
    headers = headers.replace('http://127.0.0.1:8090 http://localhost:8090 http://127.0.0.1:4177', 'http://127.0.0.1:8190 http://localhost:8190')
    write(PRIVATE/'security_headers.conf',headers)
    config['services']['frontend']['volumes'].append(dict(type='bind',source=str(PRIVATE/'security_headers.conf'),target='/etc/nginx/snippets/security_headers.conf',read_only=True))
    write(PRIVATE/'erp.json',config,True)
    print('Starting isolated ERP site on :8180',flush=True)
    command(compose('erp','up','-d'), 'setup')
    command(compose('erp','run','--rm','create-site'), 'setup')
    wait_http('http://127.0.0.1:8180/api/method/ping')
    company = backend('company')['company']
    cities = module('example_city_config', 'tools/automation/erpnext-city.py')
    projects = {}
    for city in ['samawah','mosul']:
        folder=OUTPUT/'erp'/city
        cities.prepare(city,folder,company=company,start_date='2026-10-05',release='example-1')
        print('Importing '+city+' planning baseline',flush=True)
        copy_in(folder/'plan.json','/tmp/example-plan.json')
        imported=backend('import',dict(path='/tmp/example-plan.json',company=company))
        projects[city]=imported['project']
        print(f"{city}: {imported['created']} tasks created, {imported['skipped']} retained",flush=True)
    write(OUTPUT/'setup.json',dict(company=company,projects=projects,ports=PORTS,site=SITE))
    scope=PRIVATE/'scope.json';write(scope,[dict(city=c,project=p) for c,p in projects.items()],True)
    copy_in(scope,'/tmp/example-scope.json')
    backend('provision')
    command(compose('erp','cp','backend:/tmp/example-credentials.json',str(PRIVATE/'erp-credentials.json')), 'transfer')
    (PRIVATE/'erp-credentials.json').chmod(0o600)
    if not (PRIVATE/'integration.json').exists():
        roles=['controller','operator','engineer','reviewer','inspector','maintainer','viewer']
        principals=[dict(subject='simulator' if r=='controller' else 'example-'+r,role=r,token=secrets.token_urlsafe(32),cities=['samawah','mosul'],environments=['simulation']) for r in roles]
        # One deliberately restricted identity for cross-city negative tests.
        principals.append(dict(subject='samawah-only',role='viewer',token=secrets.token_urlsafe(32),cities=['samawah'],environments=['simulation']))
        write(PRIVATE/'integration.json',dict(principals=principals,erp=json.loads((PRIVATE/'erp-credentials.json').read_text())),True)
    if not (PRIVATE/'fuxa.json').exists():
        write(PRIVATE/'fuxa.json',dict(secret=secrets.token_hex(32),admin_password=secrets.token_urlsafe(24),operator_password=secrets.token_urlsafe(24)),True)
    cfg=json.loads((PRIVATE/'fuxa.json').read_text())
    settings=dict(version=1.4,uiPort=1881,secureEnabled=True,secretCode=cfg['secret'],tokenExpiresIn='1h',daqEnabled=False,nodeRedEnabled=False,allowedOrigins=['http://127.0.0.1:1981','http://localhost:1981'],broadcastAll=True)
    write(PRIVATE/'fuxa-settings.js','module.exports = {...require("../settings.default.js"), ...'+json.dumps(settings)+'};\n',True)
    if not (PRIVATE/'supervision.json').exists():
        resolved=subprocess.check_output([DOCKER,'compose','-f',str(ROOT/'deployment/supervision/compose.yaml'),'config','--format','json'],text=True)
        config=json.loads(resolved);config.pop('name',None)
        for volume in config.get('volumes',{}).values():volume.pop('name',None)
        config['networks']['erp']['name']='osr-example-erp_default'
        config['networks']['supervision'].pop('name',None)
        for name,port in [('integration',8192),('fuxa',1981)]:
            service=config['services'][name];service['ports'][0]['published']=str(port)
            for volume in service['volumes']:
                if volume['type']=='bind':volume['source']=str(PRIVATE/Path(volume['source']).name)
        write(PRIVATE/'supervision.json',config,True)
    command(compose('supervision','up','-d','--build'),'setup-supervision')
    wait_http('http://127.0.0.1:8192/health');wait_http('http://127.0.0.1:1981/')
    supervisor=module('example_supervision','tools/automation/supervision.py')
    supervisor.PRIVATE=PRIVATE
    def fuxa(path,body=None,token=None):
        if token is None:token=request_json('http://127.0.0.1:1981/api/signin',{'username':'admin','password':cfg['admin_password']})['data']['token']
        return request_json('http://127.0.0.1:1981'+path,body,{'x-access-token':token})
    supervisor.fuxa_api=fuxa;supervisor.setup_fuxa()
    print('Isolated ERP, FUXA and gateway ready',flush=True)


def owned_host(pid):
    try:cmdline=Path(f'/proc/{pid}/cmdline').read_text().replace('\0',' ')
    except (FileNotFoundError,ProcessLookupError):return False
    return ('workbench-server.py' in cmdline and '--port 8190' in cmdline) or ('supervision-simulator.py' in cmdline and str(PRIVATE/'integration.json') in cmdline)


def stop_hosts():
    process_file=PRIVATE/'processes.json'
    if not process_file.exists():return
    stopped=[]
    for row in json.loads(process_file.read_text()):
        try:
            if owned_host(row['pid']):
                os.killpg(row['pid'],signal.SIGTERM);stopped.append(row['pid'])
        except ProcessLookupError:pass
    deadline=time.monotonic()+10
    while time.monotonic()<deadline and any(owned_host(pid) for pid in stopped):time.sleep(0.1)
    for pid in stopped:
        try:
            if owned_host(pid):os.killpg(pid,signal.SIGKILL)
        except ProcessLookupError:pass
    process_file.unlink()


def stop(reset=False):
    stop_hosts()
    for which in ['supervision','erp']:
        if (PRIVATE/(which+'.json')).exists():
            command(compose(which,*(['down','--volumes','--remove-orphans'] if reset else ['stop'])),'stop')
    if reset:
        # These exact directories and Compose project names belong solely to this fixture.
        shutil.rmtree(PRIVATE,ignore_errors=True)
        shutil.rmtree(OUTPUT,ignore_errors=True)
    print('Example services and records removed' if reset else 'Example services stopped; example volumes retained')


def host_commands(fresh=False):
    env={**os.environ,'OSR_ERP_URL':'http://127.0.0.1:8180','OSR_FUXA_URL':'http://127.0.0.1:1981',
        'OSR_INTEGRATION_URL':'http://127.0.0.1:8192','OSR_SUPERVISION_ROOT':str(OUTPUT/'supervision'),
        'OSR_SUPERVISION_CONFIG':str(PRIVATE/'integration.json'),'OSR_ERP_SNAPSHOT':str(PRIVATE/'operating-twins.json'),
        'OSR_SUPERVISION_PROFILES':str(OUTPUT/'profiles')}
    project=PRIVATE/'city-project'
    if fresh:
        shutil.copytree(ROOT/'cities/workspaces/samawah',project)
        for relative in ['project.osr.toml','sources.lock.json']:
            path=project/relative
            path.write_text(path.read_text().replace('../../catalogue',str((ROOT/'cities/catalogue').resolve())))
    if not project.exists():raise RuntimeError('No retained example workspace; complete setup and run first')
    return [
        ('simulator',[sys.executable,str(ROOT/'tools/automation/supervision-simulator.py'),'--config',str(PRIVATE/'integration.json'),
            '--controls',str(PRIVATE/'controls.json'),'--url','http://127.0.0.1:8192'],None),
        ('workbench',[sys.executable,str(ROOT/'tools/automation/workbench-server.py'),'--port','8190','--city-port','8191',
            '--db',str(PRIVATE/'ops.sqlite3'),'--project',str(project)],env)]


def start():
    report=OUTPUT/'report.json'
    if not report.exists() or json.loads(report.read_text()).get('passed') is not True:
        raise RuntimeError('Complete the example run before reopening its retained deployment')
    stop_hosts()
    for which in ['erp','supervision']:command(compose(which,'up','-d'),'start')
    wait_http('http://127.0.0.1:8180/api/method/ping');wait_http('http://127.0.0.1:8192/health');wait_http('http://127.0.0.1:1981/')
    processes=[]
    try:
        for name,args,env in host_commands():
            with (OUTPUT/(name+'.log')).open('a') as log:
                proc=subprocess.Popen(args,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
            processes.append(dict(name=name,pid=proc.pid))
        write(PRIVATE/'processes.json',processes,True)
        wait_http('http://127.0.0.1:8190/api/workbench/services')
    except BaseException:
        write(PRIVATE/'processes.json',processes,True);stop_hosts();raise
    print('Retained example available at http://127.0.0.1:8190')


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('action',choices=['setup','run','start','stop','reset','restart-check','expand-check','business-check','coverage','disposition-check','release-evidence']);args=parser.parse_args()
    OUTPUT.mkdir(parents=True,exist_ok=True)
    if args.action=='setup':setup()
    elif args.action=='start':start()
    elif args.action=='release-evidence':module('example_evidence','deployment/example-city/evidence.py').record(sys.modules[__name__])
    elif args.action=='disposition-check':module('example_disposition','deployment/example-city/disposition.py').verify(sys.modules[__name__])
    elif args.action=='business-check':module('example_business','deployment/example-city/business.py').verify(sys.modules[__name__])
    elif args.action=='expand-check':module('example_expansion','deployment/example-city/expansion.py').run(sys.modules[__name__])
    elif args.action=='coverage':module('example_coverage','deployment/example-city/coverage.py').generate(sys.modules[__name__])
    elif args.action=='restart-check':module('example_restart','deployment/example-city/restart.py').verify(sys.modules[__name__])
    elif args.action=='run':
        scenario=module('example_scenario','deployment/example-city/scenario.py');scenario.run(sys.modules[__name__])
    else:stop(reset=args.action=='reset')


if __name__=='__main__':main()
