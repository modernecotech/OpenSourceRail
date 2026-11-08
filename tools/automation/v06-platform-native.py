#!/usr/bin/env python3
"""Explicit disposable ERPNext/HRMS/gateway/FUXA v0.6 business acceptance.

preflight and verify never start services. run uses only fresh owned resources.
Private credentials/databases stay in ignored build/. This is no physical test.
"""
from datetime import datetime, timezone, timedelta
from hashlib import sha256
from pathlib import Path
from urllib.error import HTTPError
from urllib.parse import quote
from urllib.request import Request, urlopen
import argparse
import importlib.util
import json
import os
import re
import secrets
import shutil
import signal
import socket
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[2]
FIXTURES=ROOT/'tools/automation/native-v06'
sys.path.insert(0,str(FIXTURES))
from contracts import load_input, validate_input, verify_result, FLAGS, REQUIRED
import candidate_contracts
IMAGES={'erp':'osr/erpnext:15.121.2-hr15.64.0-osr14','gateway':'osr/integration:0.1.3',
        'fuxa':'frangoteam/fuxa:1.3.4@sha256:3778da3377e7685842495497d13157d1548ccad8708c434dc5d4b99fb5cb25bf',
        'db':'mariadb:10.6.25','redis':'redis:7.2.13-alpine'}
LABEL='osr.native.owner'
BROWSERS=Path.home()/'.local/share/opensource-rail/toolchains/playwright'
if BROWSERS.is_dir():os.environ.setdefault('PLAYWRIGHT_BROWSERS_PATH',str(BROWSERS))


def encoded(value):
    return (json.dumps(value,sort_keys=True,indent=2,allow_nan=False)+'\n').encode()


def sources():
    paths=[Path(__file__),*FIXTURES.glob('*'),ROOT/'tools/automation/tests/browser-launch.mjs',ROOT/'deployment/erpnext/compose.yaml',ROOT/'deployment/erpnext/Dockerfile',ROOT/'deployment/erpnext/configure-nginx.py',
           ROOT/'deployment/supervision/Dockerfile',ROOT/'package.json',ROOT/'package-lock.json']
    paths += [p for p in (ROOT/'engineering/pilot_delivery').glob('*') if p.is_file() and p.suffix in {'.py','.json'}]
    paths += [p for folder in ('deployment/erpnext/apps/osr_erpnext','services/integration/osr_integration')
              for p in (ROOT/folder).rglob('*') if p.is_file() and p.suffix in {'.py','.json','.js','.html','.toml','.txt'} and '__pycache__' not in p.parts]
    return {p.relative_to(ROOT).as_posix():sha256(p.read_bytes()).hexdigest() for p in sorted(set(paths)) if p.is_file()}


def private(path,value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(value if isinstance(value,bytes) else value.encode());path.chmod(0o600)


def invoke(argv,*,log=None,timeout=180,data=None,check=True):
    try:
        r=subprocess.run(argv,cwd=ROOT,input=data,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=timeout)
    except subprocess.TimeoutExpired as exc:
        if log and exc.output:
            with Path(log).open('ab') as stream:stream.write(exc.output)
        raise
    if log:
        with Path(log).open('ab') as stream:stream.write(r.stdout)
    if check and r.returncode:raise RuntimeError('Native subprocess failed; inspect private diagnostics')
    return r


def http(url,data=None,headers=None,method=None):
    req=Request(url,data=None if data is None else json.dumps(data).encode(),
                headers={'Content-Type':'application/json',**(headers or {})},method=method)
    with urlopen(req,timeout=20) as response:
        raw=response.read();return json.loads(raw) if raw else {}


def http_ok(url):
    with urlopen(url,timeout=5) as response:return response.status==200


def poll(callback,timeout=120):
    deadline=time.monotonic()+timeout
    while time.monotonic()<deadline:
        try:
            result=callback()
            if result:return result
        except (OSError,ValueError,KeyError):pass
        time.sleep(1)
    raise RuntimeError('Native condition did not become ready within its bounded timeout')


def refused(callback,statuses=(401,403)):
    try:callback()
    except HTTPError as exc:
        if exc.code in statuses:return
        raise
    raise AssertionError('Unauthorised native request accepted')


def campaign_input(review_pack=None,proposal=None,component_id=None):
    supplied=(review_pack is not None,proposal is not None,component_id is not None)
    if any(supplied) and not all(supplied):raise ValueError('review-pack, proposal and component-id must be supplied together')
    return candidate_contracts.load_input(ROOT,review_pack,proposal,component_id) if all(supplied) else validate_input(load_input(ROOT))


def preflight(review_pack=None,proposal=None,component_id=None):
    value=campaign_input(review_pack,proposal,component_id);docker=shutil.which('docker')
    report=dict(schema='osr-v06-platform-preflight/1',input_id=value['input_id'],identities=value['identities'],
        disk_free_bytes=shutil.disk_usage(ROOT).free,cpu_count=os.cpu_count(),docker=bool(docker),images={},**FLAGS)
    if docker:
        info=invoke([docker,'info','--format','{{json .}}'],check=False)
        report['docker_ready']=info.returncode==0
        info=json.loads(info.stdout) if info.returncode==0 else {}
        report['cpu_quota_supported']=bool(info.get('CPUCfsQuota'))
        report['cpu_isolation']='one-CPU quota per container' if report['cpu_quota_supported'] else 'no enforced CPU quota; host Docker reports CFS unavailable'
        for key,name in IMAGES.items():
            report['images'][key]=invoke([docker,'image','inspect',name],check=False).returncode==0
    report['node']=bool(shutil.which('node'))
    browser=invoke(['node','--input-type=module','-e',
        'import {chromium} from "@playwright/test";import fs from "node:fs";process.exit(fs.existsSync(chromium.executablePath())?0:1)'],check=False) if report['node'] else None
    report['playwright_chromium']=bool(browser is not None and browser.returncode==0)
    report['ready']=bool(report['playwright_chromium'] and report.get('docker_ready') and all(report['images'].values()) and report['disk_free_bytes']>=8*1024**3)
    return report


def free_port():
    with socket.socket() as sock:
        sock.bind(('127.0.0.1',0));return sock.getsockname()[1]


def owned_namespace(value):
    if not re.fullmatch(r'osr-v06-[a-f0-9]{12}',value):raise ValueError('Fresh owned namespace required')
    return value


def verify(folder,review_pack=None,proposal=None,component_id=None):
    folder=Path(folder);m=json.loads((folder/'manifest.json').read_bytes())
    for name,expected in m['files_sha256'].items():
        path=folder/name
        if path.is_symlink() or not path.resolve().is_relative_to(folder.resolve()) or sha256(path.read_bytes()).hexdigest()!=expected:
            raise ValueError('Native evidence file changed')
    result=json.loads((folder/'result.json').read_bytes())
    value=campaign_input(review_pack,proposal,component_id)
    verifier=candidate_contracts.verify_result if value['schema'].endswith('/2') else verify_result
    return verifier(result,value,sources())


def run(output=None,review_pack=None,proposal=None,component_id=None):
    pre=preflight(review_pack,proposal,component_id)
    if not pre['ready']:raise RuntimeError('Native preflight hold: require Docker, all pinned images and >=8 GiB free; run preflight for details')
    source=sources();value=campaign_input(review_pack,proposal,component_id);start=time.monotonic()
    wheel=value['schema'].endswith('/2');required=candidate_contracts.REQUIRED if wheel else REQUIRED
    fixture_file='candidate_fixture.py' if wheel else 'fixture.py'
    namespace=owned_namespace('osr-v06-'+secrets.token_hex(6));run_id=namespace.removeprefix('osr-v06-')
    folder=Path(output or ROOT/'build/v06-platform-native'/namespace).absolute()
    if not folder.resolve().is_relative_to((ROOT/'build').resolve()) or folder.exists():
        raise ValueError('Fresh private directory inside this checkout build/ required')
    folder.mkdir(parents=True,mode=0o700);folder.chmod(0o700)
    log=folder/'native-log.txt';private(log,'Explicit native v06 software acceptance; physical gates remain open.\n')
    private(folder/'input.json',encoded(value));private(folder/'preflight.json',encoded(pre))
    ports={key:free_port() for key in ('erp','gateway','fuxa')}
    if len(set(ports.values()))!=3:raise RuntimeError('Loopback port collision; rerun with a fresh allocation')
    site=namespace+'.localhost';erp_url='http://127.0.0.1:'+str(ports['erp']);gw_url='http://127.0.0.1:'+str(ports['gateway']);fx_url='http://127.0.0.1:'+str(ports['fuxa'])
    private(folder/'private.env','DB_PASSWORD='+secrets.token_hex(24)+'\nADMIN_PASSWORD='+secrets.token_hex(24)+'\nSITE_NAME='+site+'\nERP_PORT='+str(ports['erp'])+'\n')
    service_names=('configurator','backend','frontend','websocket','queue-short','queue-long','scheduler','create-site')
    override='services:\n'
    for name in (*service_names,'db','redis-cache','redis-queue'):
        override+='  '+name+':\n    labels:\n      '+LABEL+': '+namespace+'\n'
        if pre['cpu_quota_supported']:override+='    cpus: 1.0\n'
        if name in service_names:override+='    environment:\n      OPENBLAS_NUM_THREADS: \"1\"\n      OMP_NUM_THREADS: \"1\"\n      MKL_NUM_THREADS: \"1\"\n    volumes:\n      - '+str(ROOT/'deployment/erpnext/apps/osr_erpnext')+':/home/frappe/frappe-bench/apps/osr_erpnext:ro\n'
    override+='volumes:\n'+''.join('  '+name+':\n    labels:\n      '+LABEL+': '+namespace+'\n' for name in ('sites','logs','db-data','redis-data'))
    private(folder/'compose.override.yaml',override)
    base=['docker','compose','--env-file',str(folder/'private.env'),'-f',str(ROOT/'deployment/erpnext/compose.yaml'),'-f',str(folder/'compose.override.yaml'),'-p',namespace]
    def compose(*args,check=True):return invoke([*base,*args],log=log,timeout=600,check=check)
    def container(service):
        return compose('ps','-q',service).stdout.decode().strip()
    backend=None;created=False;extra=[];volumes=[];result=None
    def fixture(phase,event=None):
        if event is not None:
            private(folder/'event.json',encoded(event));invoke(['docker','cp',str(folder/'event.json'),backend+':/tmp/osr-native-v06/event.json'],log=log)
            invoke(['docker','exec','--user','root',backend,'chown','frappe:frappe','/tmp/osr-native-v06/event.json'],log=log)
        invoke(['docker','exec','-e','OSR_TEST_SITE='+site,'-e','OSR_TEST_RUN='+run_id,backend,
                '/home/frappe/frappe-bench/env/bin/python','/tmp/osr-native-v06/'+fixture_file,phase],log=log,timeout=240)
        name='readback.json' if phase=='readback' else 'state.json'
        invoke(['docker','cp',backend+':/tmp/osr-native-v06/'+name,str(folder/name)],log=log)
        (folder/name).chmod(0o600);return json.loads((folder/name).read_bytes())
    try:
        if invoke(['docker','ps','-aq','--filter','label=com.docker.compose.project='+namespace]).stdout.strip():
            raise RuntimeError('Refusing namespace collision')
        created=True
        compose('up','-d','db','redis-cache','redis-queue','configurator','backend','websocket','frontend','queue-short','queue-long','scheduler')
        compose('run','--rm','create-site');poll(lambda:http(erp_url+'/api/method/ping').get('message')=='pong',180)
        backend=container('backend');invoke(['docker','exec',backend,'mkdir','-p','/tmp/osr-native-v06'],log=log)
        for p in [*FIXTURES.glob('*.py'),folder/'input.json']:
            invoke(['docker','cp',str(p),backend+':/tmp/osr-native-v06/'+p.name],log=log)
        invoke(['docker','exec','--user','root',backend,'chown','-R','frappe:frappe','/tmp/osr-native-v06'],log=log)
        if wheel:
            from engineering.pilot_delivery import review as source_review
            source_review.verify_artifacts(value['review_pack'],review_pack)
            artifact_folder=folder/'artifacts';artifact_folder.mkdir()
            for row in value['artifact_inventory']:
                src=source_review.ordinary(review_pack,row['path']);dst=artifact_folder/row['path'];dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dst)
            invoke(['docker','cp',str(artifact_folder),backend+':/tmp/osr-native-v06/artifacts'],log=log)
            invoke(['docker','exec','--user','root',backend,'chown','-R','frappe:frappe','/tmp/osr-native-v06/artifacts'],log=log)
        state=fixture('bootstrap')
        sys.path.insert(0,str(ROOT/'services/integration'))
        from osr_integration import config,fuxa
        generic=dict(template_revision='v06-native-1',rolling_stock_family='wheel-candidate-research' if wheel else 'v06-passive-wheel',historian=dict(owner='osr-integration',retention_days=1,sampling_seconds=2),
            templates=dict(condition=dict(label='SIM controlled research component' if wheel else 'SIM HVAC record',asset_types=['fixture'],component_type_id=value['source_occurrence']['id'],
                measurements=dict(condition_code=dict(min=0,max=1,unit='simulation-code',stale_seconds=180)),
                alarms=[dict(id='synthetic-fault',measurement='condition_code',high=1,clear_below=.5,delay_seconds=0,repeat_seconds=600,
                    maintenance=True,response='SIM software fault; no physical condition inferred')],commands={})))
        package=config.build_package(generic,dict(city=value['city'],company=state['company'],erp_project=state['project']),
            [dict(asset_id=state['asset_id'] if wheel else 'SIM-V06-HVAC',asset_type='fixture',name='SIM source-bound research component' if wheel else 'SIM source-bound HVAC fixture')],value['identities']['engineering_revision'] if wheel else value['identities']['candidate_id'])
        asset=package['equipment'][0];asset.update(asset_id=state['asset_id'],erp_asset_id=state['asset'],erp_item_code=state['finished_item'])
        if wheel:asset['physical_serial_id']=state['old']['serial']
        package['sha256']=config.digest({k:v for k,v in package.items() if k!='sha256'});config.validate_package(package)
        tokens={r:secrets.token_hex(24) for r in ('engineer','operator','controller')}
        observer=state['users']['observer'];cfg=dict(principals=[dict(subject='simulator' if r=='controller' else 'v06-'+r,role=r,token=t,cities=[value['city']],environments=['simulation']) for r,t in tokens.items()],
            erp=dict(url='http://frontend:8080',key=observer['key'],secret=observer['secret']))
        private(folder/'integration.json',encoded(cfg))
        for kind in ('integration','fuxa'):
            vol=namespace+'-'+kind;invoke(['docker','volume','create','--label',LABEL+'='+namespace,vol],log=log);volumes.append(vol)
        gateway=namespace+'-integration';extra.append(gateway)
        invoke(['docker','run','-d','--name',gateway,'--label',LABEL+'='+namespace,*(['--cpus','1'] if pre['cpu_quota_supported'] else []),'--network',namespace+'_default','--network-alias','integration',
            '-p','127.0.0.1:'+str(ports['gateway'])+':8092','-v',str(ROOT/'services/integration/osr_integration')+':/app/osr_integration:ro',
            '-v',str(folder/'integration.json')+':/run/secrets/integration.json:ro','-v',volumes[0]+':/data',IMAGES['gateway']],log=log)
        poll(lambda:http(gw_url+'/health'));headers={'Authorization':'Bearer '+tokens['engineer']}
        http(gw_url+'/packages',dict(package=package),headers)
        refused(lambda:http(gw_url+'/packages',dict(package=package),{'Authorization':'Bearer '+tokens['controller']}))
        refused(lambda:http(erp_url+'/api/method/osr_erpnext.integration.execution_feedback?project='+quote(state['project'])))
        auth=lambda role:{'Authorization':'token '+state['users'][role]['key']+':'+state['users'][role]['secret']}
        refused(lambda:http(erp_url+'/api/resource/BOM',dict(item=state['finished_item'],quantity=1),auth('observer')))
        now=datetime.now(timezone.utc)
        cmd=dict(request_id='SIM-NO-MOVEMENT',city=value['city'],environment='simulation',asset_id=state['asset_id'],command='movement_authority',parameters={},
                 created_at=now.isoformat(),expires_at=(now+timedelta(seconds=20)).isoformat(),required_conditions=[])
        denied=http(gw_url+'/commands',cmd,{'Authorization':'Bearer '+tokens['operator']});assert denied['state']=='rejected'
        assert http(gw_url+'/controller/commands',headers={'Authorization':'Bearer '+tokens['controller']})==[]
        # Cause a real ERP delivery outage, retain pending durable work, restart
        # the gateway, then recover exactly the same native condition event.
        compose('stop','frontend')
        reading=dict(city=value['city'],environment='simulation',asset_id=state['asset_id'],source_id='simulator',measurement='condition_code',sequence=1,
            source_timestamp=now.isoformat(),value=1,unit='simulation-code',quality='valid')
        http(gw_url+'/telemetry',reading,{'Authorization':'Bearer '+tokens['controller']})
        query='/outbox?city='+value['city']+'&environment=simulation'
        def pending():
            rows=http(gw_url+query,headers=headers)['items'];return rows if rows and rows[0]['attempts']>0 else None
        before=poll(pending,45);invoke(['docker','restart',gateway],log=log);compose('start','frontend')
        poll(lambda:http(erp_url+'/api/method/ping'));poll(lambda:http(gw_url+'/health'))
        def delivered():
            rows=http(gw_url+query,headers=headers)['items'];return rows if rows and all(r['state']=='delivered' for r in rows) else None
        after=poll(delivered,120);assert {r['id'] for r in before}=={r['id'] for r in after}
        eventrow=after[0]
        body=json.loads(invoke(['docker','exec',gateway,'python','-c',
            'import sqlite3,sys;db=sqlite3.connect("file:/data/integration.sqlite?mode=ro",uri=True);print(db.execute("SELECT body FROM outbox WHERE id=?",(sys.argv[1],)).fetchone()[0])',eventrow['id']]).stdout)
        response=eventrow['response'];response=json.loads(response) if isinstance(response,str) else response
        state=fixture('repair',dict(issue=response['issue'],event_id=body['event_id'],body=body))
        if not wheel:http(erp_url+'/api/resource/Task/'+quote(state['review_task'],safe=''),dict(status='Completed'),auth('reviewer'),method='PUT')
        readback=fixture('readback')
        # Native FUXA, fresh appdata and changed default credentials.
        passwords={r:secrets.token_hex(20) for r in ('admin','operator')}
        settings=dict(version=1.4,uiPort=1881,secureEnabled=True,secretCode=secrets.token_hex(32),tokenExpiresIn='1h',daqEnabled=False,nodeRedEnabled=False,allowedOrigins=[fx_url],broadcastAll=True)
        private(folder/'fuxa-settings.js','module.exports={...require("../settings.default.js"),...'+json.dumps(settings)+'};\n')
        fx=namespace+'-fuxa';extra.append(fx)
        invoke(['docker','run','-d','--name',fx,'--label',LABEL+'='+namespace,*(['--cpus','1'] if pre['cpu_quota_supported'] else []),'--network',namespace+'_default',
            '-p','127.0.0.1:'+str(ports['fuxa'])+':1881','-v',volumes[1]+':/usr/src/app/FUXA/server/_appdata',
            '-v',str(folder/'fuxa-settings.js')+':/usr/src/app/FUXA/server/_appdata/settings.js:ro',IMAGES['fuxa']],log=log)
        poll(lambda:http_ok(fx_url),120)
        token=http(fx_url+'/api/signin',dict(username='admin',password='123456'))['data']['token'];fh={'x-access-token':token}
        for user,groups in [('operator',0),('admin',-1)]:
            http(fx_url+'/api/users',dict(params=dict(username=user,fullname='SIM v06 '+user,password=passwords[user],groups=groups,info=json.dumps(dict(roles=[])))),fh)
        project=fuxa.project([package],workbench_url=erp_url);http(fx_url+'/api/project',project,fh)
        items=project['hmi']['views'][0]['items']
        def widget(name):return next(key for key,row in items.items() if row['name']==name)
        widgets=dict(connection=widget('Gateway status'),value=widget(asset['fuxa_device_id']+'__condition_code'),
            quality=widget(asset['fuxa_device_id']+'__condition_code_quality'),timestamp=widget(asset['fuxa_device_id']+'__condition_code_timestamp'))
        private(folder/'browser.json',encoded(dict(url=fx_url,password=passwords['operator'],widgets=widgets,screenshot=str(folder/'fuxa.png'))))
        # Refresh actual current observation after all ERP work so FUXA displays
        # current valid quality instead of a cached outage value.
        reading.update(sequence=2,source_timestamp=datetime.now(timezone.utc).isoformat(),value=0)
        http(gw_url+'/telemetry',reading,{'Authorization':'Bearer '+tokens['controller']})
        invoke(['node',str(FIXTURES/'browser.mjs'),str(folder/'browser.json')],log=log,timeout=120)
        image_ids={key:invoke(['docker','image','inspect','--format','{{.Id}}',name]).stdout.decode().strip() for key,name in IMAGES.items()}
        if source!=sources():raise ValueError('Source changed during native execution')
        result=dict(schema='osr-v06-native-platform-result/2' if wheel else 'osr-v06-native-platform-result/1',execution='executed',input_id=value['input_id'],identities=value['identities'],
            source_sha256=source,namespace=namespace,elapsed_seconds=round(time.monotonic()-start,3),images=image_ids,resource_preflight=pre,
            native_records=readback['records'],business_review=readback['review'],qa_binding=readback['binding'],review_context=readback['review_context'],
            outage=dict(before=before,after=after),checks={key:True for key in sorted(required)},uncovered=[],
            scope=value['scope'] if wheel else 'One synthetic HVAC kit conversion; native software/business transactions, no physical manufacturing or railway release',**FLAGS)
        if wheel:result.update(candidate_mapping=readback['candidate_mapping'],candidate_lifecycle=readback['candidate_lifecycle'],document_coverage=value['review_pack']['coverage'])
        # Deliberately exclude private configuration, user/API credentials,
        # databases, raw state and logs from the reviewable public evidence.
        print('Native covered lifecycle completed; checking teardown before publishing evidence')
    except BaseException as exc:
        private(folder/'failure.json',encoded(dict(execution='failed',error_type=type(exc).__name__,elapsed_seconds=round(time.monotonic()-start,3),
            input_id=value['input_id'],source_sha256=source,uncovered=sorted(required),**FLAGS)))
        print('Native execution failed; retained private diagnostics: '+str(folder),file=sys.stderr)
        raise
    finally:
        if created:
            errors=[]
            def cleanup_call(argv):
                try:
                    r=invoke(argv,log=log,check=False,timeout=45)
                    if r.returncode:errors.append('cleanup command returned '+str(r.returncode))
                    return r.stdout.decode().strip() if not r.returncode else ''
                except BaseException as exc:
                    errors.append(type(exc).__name__)
                    return ''
            cleanup_call([*base,'logs','--no-color'])
            for name in extra:
                label=cleanup_call(['docker','inspect','--format','{{ index .Config.Labels "'+LABEL+'" }}',name])
                if label==namespace:cleanup_call(['docker','rm','-f',name])
            cleanup_call([*base,'down','--volumes','--remove-orphans'])
            for name in volumes:
                label=cleanup_call(['docker','volume','inspect','--format','{{ index .Labels "'+LABEL+'" }}',name])
                if label==namespace:cleanup_call(['docker','volume','rm',name])
            remaining_c=cleanup_call(['docker','ps','-aq','--filter','label='+LABEL+'='+namespace]).split()
            remaining_v=cleanup_call(['docker','volume','ls','-q','--filter','label='+LABEL+'='+namespace]).split()
            remaining_n=cleanup_call(['docker','network','ls','-q','--filter','label=com.docker.compose.project='+namespace]).split()
            cleanup=dict(namespace=namespace,remaining_containers=remaining_c,remaining_volumes=remaining_v,remaining_networks=remaining_n,errors=errors,
                         verified=not errors and not remaining_c and not remaining_v and not remaining_n)
            private(folder/'cleanup.json',encoded(cleanup))
    if result is not None:
        if not cleanup['verified']:
            private(folder/'failure.json',encoded(dict(execution='cleanup-failed',input_id=value['input_id'],uncovered=['owned-resource-cleanup'],**FLAGS)))
            raise RuntimeError('Owned native cleanup was not fully verified; no success receipt published')
        result['cleanup']=cleanup
        evidence=folder/'evidence';evidence.mkdir();private(evidence/'result.json',encoded(result))
        shutil.copyfile(folder/'fuxa.png',evidence/'fuxa.png')
        private(evidence/'manifest.json',encoded(dict(schema='osr-v06-platform-evidence/1',files_sha256={p.name:sha256(p.read_bytes()).hexdigest() for p in evidence.iterdir()})))
        verify(evidence,review_pack,proposal,component_id);print('PASS native v06 software/business acceptance: '+str(evidence))
    return result


def main():
    signal.signal(signal.SIGTERM,lambda *_: (_ for _ in ()).throw(SystemExit('Native runner terminated')))
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('action',choices=['preflight','run','verify']);parser.add_argument('--output',type=Path)
    parser.add_argument('--review-pack',type=Path);parser.add_argument('--proposal',type=Path);parser.add_argument('--component-id')
    args=parser.parse_args();options=(args.review_pack,args.proposal,args.component_id)
    if args.action=='preflight':print(json.dumps(preflight(*options),indent=2))
    elif args.action=='run':run(args.output,*options)
    else:
        if args.output is None:parser.error('verify requires --output <evidence directory>')
        verify(args.output,*options);print('PASS retained source-bound native evidence; physical gates remain open')

if __name__=='__main__':main()
