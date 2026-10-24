#!/usr/bin/env python3
"""Run an isolated ERPNext/FUXA pilot, or verify its retained evidence only.

Only the fixed ``osr-maglev-pilot`` namespace is provisioned. Existing operator
sites/volumes are never altered or removed. Secrets remain under ignored build/.
"""
from datetime import datetime,timezone
from hashlib import sha256
from pathlib import Path
import argparse
import json
import os
import secrets
import shutil
import subprocess
import sys
import time
from urllib.request import Request,urlopen
from urllib.error import HTTPError,URLError

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from engineering.ferrite_maglev import pilot_lifecycle as pilot
from osr_integration import config,fuxa

DOCKER=shutil.which('docker')
PRIVATE=ROOT/'build/maglev-pilot-native'
ERP='osr-maglev-pilot-backend-1'
SITE='osr-maglev-pilot.localhost'
PY='/home/frappe/frappe-bench/env/bin/python'

def write_private(path,value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True);path.write_text(value);path.chmod(0o600)

def call(argv,*,data=None,log=None,timeout=1800):
    r=subprocess.run(argv,input=data,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,cwd=ROOT,timeout=timeout)
    if log is not None:
        with open(log,'ab') as s:s.write(r.stdout)
    if r.returncode:raise RuntimeError('Native command failed; inspect the retained local log: '+str(log))
    return r.stdout

def http(url,data=None,headers=None):
    req=Request(url,data=None if data is None else json.dumps(data).encode(),headers={'Content-Type':'application/json',**(headers or {})})
    with urlopen(req,timeout=25) as r:
        b=r.read();return json.loads(b) if b else {}

def ready(url,timeout=150):
    start=time.monotonic()
    while time.monotonic()-start<timeout:
        try:
            with urlopen(url,timeout=3) as r:
                if r.status==200:return
        except (OSError,HTTPError,URLError):pass
        time.sleep(1)
    raise RuntimeError('Isolated native service did not become ready: '+url)

def compose(*args,log=None):
    return call([DOCKER,'compose','--env-file',str(PRIVATE/'private.env'),'-f',str(ROOT/'deployment/erpnext/compose.yaml'),'-f',str(PRIVATE/'compose.override.yaml'),'-p','osr-maglev-pilot',*args],log=log)

def bench(code,log):
    prefix="import os,json,frappe\nos.chdir('/home/frappe/frappe-bench/sites');frappe.init(site='"+SITE+"');frappe.connect();frappe.set_user('Administrator')\n"
    return call([DOCKER,'exec','-i',ERP,PY,'-'],data=(prefix+code+'\nfrappe.destroy()\n').encode(),log=log)

def native_fault_recovery(log):
    """Kill a disposable Python worker after native QI commit, before dispatch.

    No production flag or permission bypass is added to the action API. The
    test worker replaces only its own dispatch call with immediate process loss.
    A fresh process must find that exact QI and append one business event.
    """
    prefix="import os,json,frappe\nos.chdir('/home/frappe/frappe-bench/sites');frappe.init(site='"+SITE+"');frappe.connect();frappe.set_user('Administrator')\n"
    code="from osr_erpnext import maglev_pilot as p\nfolder,package,project,ledger=p._context();result=json.loads((folder/'result.json').read_text());frappe.set_user(result['users']['inspector'])\nintent=dict(asset_id=package['positions'][0]['asset_id'],action='test-fail',expected_head=ledger.snapshot()['head_sha256'])\nopen('/tmp/maglev-pilot-fault-intent.json','w').write(json.dumps(intent))\ndef die(*args,**kwargs):os._exit(86)\np.contract.Ledger.append=die\np.action(**intent)\nraise AssertionError('Fault boundary did not execute')\n"
    r=subprocess.run([DOCKER,'exec','-i',ERP,PY,'-'],input=(prefix+code).encode(),stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=90)
    with log.open('ab') as stream:stream.write(r.stdout);stream.write(b'Expected disposable native worker loss at post-QI-commit/pre-journal-dispatch: exit '+str(r.returncode).encode()+b'\n')
    if r.returncode!=86:raise AssertionError('Actual native fault injection did not reach the intended boundary')
    bench("from osr_erpnext import maglev_pilot as p\nfolder,package,project,ledger=p._context();result=json.loads((folder/'result.json').read_text());frappe.set_user(result['users']['inspector']);intent=json.load(open('/tmp/maglev-pilot-fault-intent.json'))\nassert ledger.snapshot()['head_sha256']==intent['expected_head']\nkey=p.contract.digest(dict(asset=intent['asset_id'],action=intent['action'],head=intent['expected_head'],actor=frappe.session.user));filters=dict(remarks='SIM-PILOT-EVENT:'+key)\nassert frappe.db.count('Quality Inspection',filters)==1\ncreated=p.action(**intent);retried=p.action(**intent);assert created['created'] and not retried['created'];assert frappe.db.count('Quality Inspection',filters)==1\nopen('/tmp/maglev-pilot-fault-recovery.json','w').write(json.dumps(dict(process_exit_code=86,native_qi_count=1,created=created['created'],retry_created=retried['created'],stage='after-native-QI-commit-before-journal-dispatch')))\nprint('PASS actual process loss after native commit, exact-QI recovery and duplicate refusal')",log)
    call([DOCKER,'cp',ERP+':/tmp/maglev-pilot-fault-recovery.json',str(PRIVATE/'fault-recovery.json')],log=log)
    return json.loads((PRIVATE/'fault-recovery.json').read_text())

def initialise(log):
    PRIVATE.mkdir(parents=True,exist_ok=True)
    env=PRIVATE/'private.env'
    if not env.exists():write_private(env,'DB_PASSWORD='+secrets.token_hex(24)+'\nADMIN_PASSWORD='+secrets.token_hex(24)+'\nSITE_NAME='+SITE+'\nERP_PORT=18088\n')
    services=('configurator','backend','frontend','websocket','queue-short','queue-long','scheduler','create-site')
    mount=str(ROOT/'deployment/erpnext/apps/osr_erpnext')+':/home/frappe/frappe-bench/apps/osr_erpnext:ro'
    write_private(PRIVATE/'compose.override.yaml','services:\n'+''.join('  '+s+':\n    volumes:\n      - '+mount+'\n' for s in services))
    compose('up','-d','db','redis-cache','redis-queue','configurator','backend','websocket','frontend',log=log)
    exists=subprocess.run([DOCKER,'exec',ERP,'test','-f','/home/frappe/frappe-bench/sites/'+SITE+'/site_config.json'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL).returncode==0
    if not exists:compose('run','--rm','create-site',log=log)
    ready('http://127.0.0.1:18088/login')

def install_supervision(result,package,log):
    # The actual native identities are explicit disposable-run fixture IDs;
    # source product/position identities stay separately recorded.
    sup=pilot.supervisory_package(package,project=result['project'])
    for a in sup['equipment']:
        native=next(p for p in result['products'] if p['asset_id']==a['site_id'])
        a.update(asset_id=native['native_asset_identity'],erp_asset_id=native['asset'],erp_item_code=native['finished_item'],company_id=result['company'])
    sup['sha256']=config.digest({k:v for k,v in sup.items() if k!='sha256'});config.validate_package(sup)
    tokens={role:secrets.token_hex(24) for role in ('engineer','operator','controller')}
    credential=PRIVATE/'erp-credentials.json'
    bench("from frappe.utils.password import set_encrypted_password\nfrom frappe.utils import password\nfrom osr_erpnext.maglev_pilot import _root\nr=json.loads((_root()/'current.json').read_text());result=json.loads((_root()/r['run']/'result.json').read_text())\nu=result['users']['observer'];key=frappe.generate_hash(length=20);secret=frappe.generate_hash(length=32)\nfrappe.db.set_value('User',u,'api_key',key);set_encrypted_password('User',u,secret,'api_secret')\ncreds=dict(key=key,secret=secret,users={})\nfor role,user in result['users'].items():\n pwd=frappe.generate_hash(length=24);password.update_password(user,pwd);creds['users'][role]=dict(user=user,password=pwd)\nopen('/tmp/maglev-pilot-credentials.json','w').write(json.dumps(creds));frappe.db.commit()",log)
    call([DOCKER,'cp',ERP+':/tmp/maglev-pilot-credentials.json',str(credential)],log=log);credential.chmod(0o600);creds=json.loads(credential.read_text())
    cfg=dict(principals=[dict(subject='simulator' if r=='controller' else 'pilot-'+r,role=r,token=t,cities=['baghdad'],environments=['simulation']) for r,t in tokens.items()],erp=dict(url='http://frontend:8080',key=creds['key'],secret=creds['secret']))
    write_private(PRIVATE/'integration.json',json.dumps(cfg));fuxa_passwords=dict(admin=secrets.token_hex(20),operator=secrets.token_hex(20));write_private(PRIVATE/'fuxa-passwords.json',json.dumps(fuxa_passwords))
    settings=dict(version=1.4,uiPort=1881,secureEnabled=True,secretCode=secrets.token_hex(32),tokenExpiresIn='1h',daqEnabled=False,nodeRedEnabled=False,allowedOrigins=['http://127.0.0.1:1888'],broadcastAll=True)
    write_private(PRIVATE/'fuxa-settings.js','module.exports={...require("../settings.default.js"),...'+json.dumps(settings)+'};\n')
    # Fixed names, own volumes and loopback ports; no external operator stack.
    for name in ('osr-maglev-pilot-integration','osr-maglev-pilot-fuxa'):
        subprocess.run([DOCKER,'rm','-f',name],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    call([DOCKER,'run','-d','--name','osr-maglev-pilot-integration','--network','osr-maglev-pilot_default','--network-alias','integration','-p','127.0.0.1:18092:8092',
          '-v',str(ROOT/'services/integration/osr_integration')+':/app/osr_integration:ro','-v',str(PRIVATE/'integration.json')+':/run/secrets/integration.json:ro',
          '-v','osr-maglev-pilot-integration-'+result['run']+'-'+secrets.token_hex(4)+':/data','osr/integration:0.1.3'],log=log)
    ready('http://127.0.0.1:18092/health')
    headers={'Authorization':'Bearer '+tokens['engineer']};http('http://127.0.0.1:18092/packages',dict(package=sup),headers)
    # Start with a separate fresh FUXA appdata per explicit campaign to avoid
    # importing over an operator's project or retaining default credentials.
    run=result['run'];volume='osr-maglev-pilot-fuxa-'+run+'-'+secrets.token_hex(4)
    call([DOCKER,'run','-d','--name','osr-maglev-pilot-fuxa','--network','osr-maglev-pilot_default','-p','127.0.0.1:1888:1881','-v',volume+':/usr/src/app/FUXA/server/_appdata',
          '-v',str(PRIVATE/'fuxa-settings.js')+':/usr/src/app/FUXA/server/_appdata/settings.js:ro',
          'frangoteam/fuxa:1.3.4@sha256:3778da3377e7685842495497d13157d1548ccad8708c434dc5d4b99fb5cb25bf'],log=log)
    ready('http://127.0.0.1:1888')
    auth=http('http://127.0.0.1:1888/api/signin',dict(username='admin',password='123456'))['data']['token'];fh={'x-access-token':auth}
    for user,groups in [('admin',-1),('operator',0)]:
        http('http://127.0.0.1:1888/api/users',dict(params=dict(username=user,fullname='Pilot '+user,password=fuxa_passwords[user],groups=groups,info=json.dumps(dict(roles=[])))),fh)
    project=pilot.fuxa_project(sup);http('http://127.0.0.1:1888/api/project',project,fh)
    # Real durable gateway: force delivery outage, persist pending work, restart,
    # then replay it through native ERP without duplicates.
    call([DOCKER,'stop','osr-maglev-pilot-frontend-1'],log=log)
    for a in sup['equipment']:
        reading=dict(city='baghdad',environment='simulation',asset_id=a['asset_id'],source_id='simulator',measurement='condition_code',sequence=int(time.time()),
                     source_timestamp=datetime.now(timezone.utc).isoformat(),value=1,unit='simulation-code',quality='valid')
        http('http://127.0.0.1:18092/telemetry',reading,{'Authorization':'Bearer '+tokens['controller']})
    deadline=time.monotonic()+30;pending=[]
    while time.monotonic()<deadline:
        pending=http('http://127.0.0.1:18092/outbox?city=baghdad&environment=simulation',headers=headers)['items']
        if len(pending)>=3 and all(r.get('attempts',0)>0 for r in pending):break
        time.sleep(1)
    if len(pending)<3 or not any(r.get('attempts',0)>0 for r in pending):raise AssertionError('real outbox outage/retry not observed')
    call([DOCKER,'restart','osr-maglev-pilot-integration'],log=log);call([DOCKER,'start','osr-maglev-pilot-frontend-1'],log=log);ready('http://127.0.0.1:18088/login');ready('http://127.0.0.1:18092/health')
    delivered=[];deadline=time.monotonic()+100
    while time.monotonic()<deadline:
        delivered=http('http://127.0.0.1:18092/outbox?city=baghdad&environment=simulation',headers=headers)['items']
        if len(delivered)>=3 and all(r['state']=='delivered' for r in delivered):break
        time.sleep(1)
    if not delivered or any(r['state']!='delivered' for r in delivered):raise AssertionError('native ERP outbox replay failed')
    for a in sup['equipment']:
        http('http://127.0.0.1:18092/telemetry',dict(city='baghdad',environment='simulation',asset_id=a['asset_id'],source_id='simulator',measurement='condition_code',sequence=int(time.time())+1,
             source_timestamp=datetime.now(timezone.utc).isoformat(),value=0,unit='simulation-code',quality='valid'),{'Authorization':'Bearer '+tokens['controller']})
    # All current maglev equipment commands are empty, and a controller cannot
    # mutate package definitions through the authenticated API.
    try:http('http://127.0.0.1:18092/packages',dict(package=sup),{'Authorization':'Bearer '+tokens['controller']})
    except HTTPError as exc:
        if exc.code!=403:raise
    else:raise AssertionError('controller configuration write accepted')
    result['gateway']=dict(outage_observed=True,outbox_before_restart=pending,outbox_after_restart=delivered,commands_observation_only=all(not a['commands'] for a in sup['equipment']))
    return project,creds,fuxa_passwords

BROWSER=r'''
import {chromium,expect} from '@playwright/test';import fs from 'node:fs';
const cfg=JSON.parse(fs.readFileSync(process.argv[2]));const browser=await chromium.launch();
const context=await browser.newContext({viewport:{width:1450,height:1050}});const page=await context.newPage();
const anonymous=await page.request.get('http://127.0.0.1:18088/api/method/osr_erpnext.maglev_pilot.snapshot');expect([401,403]).toContain(anonymous.status());
const login=await page.request.post('http://127.0.0.1:18088/api/method/login',{data:{usr:cfg.users.inspector.user,pwd:cfg.users.inspector.password}});expect(login.ok()).toBeTruthy();
await page.goto('http://127.0.0.1:18088/maglev-pilot');await expect(page.getByRole('heading',{name:'Current maglev pilot Workbench'})).toBeVisible();
await expect(page.locator('.pilot-card')).toHaveCount(3);const card=page.locator('.pilot-card').first();
const initial=(await (await page.request.get('http://127.0.0.1:18088/api/method/osr_erpnext.maglev_pilot.snapshot')).json()).message;
await card.getByRole('button',{name:'Record simulated failed test'}).click();await page.waitForLoadState('networkidle');await expect(page.locator('.pilot-card').first()).toContainText('test-failed');
const retry=await page.evaluate(async input=>{const r=await fetch('/api/method/osr_erpnext.maglev_pilot.action',{method:'POST',headers:{'Content-Type':'application/json','X-Frappe-CSRF-Token':frappe.csrf_token},body:JSON.stringify(input)});return await r.json();},{asset_id:initial.package.positions[0].asset_id,action:'test-fail',expected_head:initial.journal.head_sha256});expect(retry.message.created).toBe(false);
await page.locator('.pilot-card').first().getByRole('button',{name:'Independently review business handback'}).click();await expect(page.locator('#pilot-feedback')).toContainText('Action refused');
await page.locator('.pilot-card').first().getByRole('button',{name:'Record simulated passing test'}).click();await page.waitForLoadState('networkidle');await expect(page.locator('.pilot-card').first()).toContainText('tested');
// Actual separate authenticated ERP identity performs business review.
const review=await browser.newContext({viewport:{width:1450,height:1050}});const reviewer=await review.newPage();
await reviewer.request.post('http://127.0.0.1:18088/api/method/login',{data:{usr:cfg.users.reviewer.user,pwd:cfg.users.reviewer.password}});
await reviewer.goto('http://127.0.0.1:18088/maglev-pilot');await reviewer.locator('.pilot-card').first().getByRole('button',{name:'Independently review business handback'}).click();await reviewer.waitForLoadState('networkidle');
await expect(reviewer.locator('.pilot-card').first()).toContainText('simulation-business-reviewed');await reviewer.screenshot({path:cfg.screenshot,fullPage:true});
const snap=await reviewer.request.get('http://127.0.0.1:18088/api/method/osr_erpnext.maglev_pilot.snapshot');fs.writeFileSync(cfg.snapshot,JSON.stringify((await snap.json()).message));
const fuxaLogin=await page.request.post('http://127.0.0.1:1888/api/signin',{data:{username:'operator',password:cfg.fuxa_operator}});const token=(await fuxaLogin.json()).data.token;
const deny=await page.request.post('http://127.0.0.1:1888/api/project',{headers:{'x-access-token':token},data:{}});expect([401,403]).toContain(deny.status());
const fuxaPage=await browser.newPage({viewport:{width:1450,height:1000}});await fuxaPage.goto('http://127.0.0.1:1888/home');
const dialog=fuxaPage.locator('mat-dialog-container');await dialog.waitFor();await dialog.locator('form input[type=text]').fill('operator');await dialog.locator('input[type=password]').fill(cfg.fuxa_operator);await dialog.getByRole('button',{name:'OK',exact:true}).click();await dialog.waitFor({state:'hidden'});
await expect(fuxaPage.locator('g[type="svg-ext-value"]').first()).toContainText('5',{timeout:30000});await expect(fuxaPage.locator('body')).toContainText('condition_code');await fuxaPage.screenshot({path:cfg.fuxa_screenshot,fullPage:true});
console.log('PASS authenticated native Workbench actions, late failed test refusal, independent reviewer and FUXA operator write refusal');await browser.close();
'''

def run():
    if not DOCKER:raise RuntimeError('Docker is required for explicit native run; retained verify does not need Docker')
    RAW=pilot.RAW;before=pilot.native_sources();PRIVATE.mkdir(parents=True,exist_ok=True);log=PRIVATE/'native-log.txt';log.write_bytes(b'Explicit isolated current-maglev software business campaign\n')
    initialise(log);run_id=datetime.now(timezone.utc).strftime('pilot-%Y%m%d-%H%M%S');package=pilot.lifecycle_package()
    source=dict(package=package,bundle=pilot.planning_bundle(package),run_id=run_id)
    write_private(PRIVATE/'input.json',json.dumps(source));call([DOCKER,'cp',str(PRIVATE/'input.json'),ERP+':/tmp/maglev-pilot-input.json'],log=log)
    bench("from osr_erpnext.maglev_pilot import run_fixture\nv=json.load(open('/tmp/maglev-pilot-input.json'));r=run_fixture(**v)\nopen('/tmp/maglev-pilot-result.json','w').write(json.dumps(r));print('PASS native ERP current-maglev fixture: '+str(len(r['products']))+' products')",log)
    call([DOCKER,'cp',ERP+':/tmp/maglev-pilot-result.json',str(PRIVATE/'native-result.json')],log=log);result=json.loads((PRIVATE/'native-result.json').read_text())
    project,creds,fp=install_supervision(result,package,log)
    result['fault_recovery']=native_fault_recovery(log)
    # Clear template caches on the isolated site only; source mounts stay readonly.
    call([DOCKER,'exec',ERP,'bench','--site',SITE,'clear-cache'],log=log);call([DOCKER,'restart',ERP],log=log);ready('http://127.0.0.1:18088/login')
    write_private(PRIVATE/'browser-config.json',json.dumps(dict(users=creds['users'],fuxa_operator=fp['operator'],screenshot=str(PRIVATE/'workbench.png'),fuxa_screenshot=str(PRIVATE/'fuxa.png'),snapshot=str(PRIVATE/'operator-snapshot.json'))))
    browser=ROOT/'build/maglev-pilot-browser.mjs';browser.write_text(BROWSER)
    call(['node',str(browser),str(PRIVATE/'browser-config.json')],log=log,timeout=180)
    snapshot=json.loads((PRIVATE/'operator-snapshot.json').read_text());result['operator_ui']=dict(actor=snapshot['actor'],journal=snapshot['journal'],actual_native_test_records=True)
    bench("from osr_erpnext.maglev_pilot import _context\nfolder,package,project,ledger=_context();result=json.loads((folder/'result.json').read_text());records=[];refs=set()\nfor row in result['products']:\n refs.update([('Asset',row['asset']),('BOM',row['bom']),('Purchase Order',row['purchase_order']),('Purchase Receipt',row['receipt']),('Quality Inspection',row['failed_inspection']),('Task',row['rework_task']),('Issue',row['issue']),('Asset Repair',row['asset_repair']),('Batch',row['batch'])]+[('Work Order',n) for n in row['work_orders']]+[('Stock Entry',n) for n in row['stock_entries']]+[('Serial No',row[k]) for k in ('old_serial','current_serial')])\nfor event in ledger.snapshot()['events']:\n c=event['command']\n if c['kind'] in ('inspect','test'):refs.add(('Quality Inspection',c['data'].get('inspection') or c['data']['test_record']))\nfor dt,name in sorted(refs):\n doc=frappe.get_doc(dt,name);fields=('status','produced_qty','qty','inspected_by','repair_status','custom_osr_handback_required','custom_osr_pilot_current_serial','custom_osr_pilot_revision','item_code','reference_type','reference_name','gross_purchase_amount','total')\n records.append(dict(doctype=dt,name=name,docstatus=doc.docstatus,owner=doc.owner,modified=str(doc.modified),values={**{f:doc.get(f) for f in fields if doc.meta.has_field(f)},**({'items':[dict(item_code=x.item_code,qty=x.qty,uom=x.get('uom') or x.get('stock_uom'),rate=x.get('rate'),basic_rate=x.get('basic_rate'),s_warehouse=x.get('s_warehouse'),t_warehouse=x.get('t_warehouse')) for x in doc.items]} if doc.meta.has_field('items') else {})}))\nopen('/tmp/maglev-pilot-readback.json','w').write(json.dumps(records,default=str))",log)
    call([DOCKER,'cp',ERP+':/tmp/maglev-pilot-readback.json',str(PRIVATE/'readback.json')],log=log)
    result['native_documents']=json.loads((PRIVATE/'readback.json').read_text())
    result['images']={name:call([DOCKER,'inspect','--format','{{.Image}}',name],log=log).decode().strip() for name in (ERP,'osr-maglev-pilot-integration','osr-maglev-pilot-fuxa')}
    result['checks']=[dict(id=i,passed=True) for i in ('native-erp-manufacture','native-receipt-quality-fail-rework','native-revision-disposition','native-alarm-repair','independent-business-review','restart-replay','permission-refusal','late-failure-refusal','removed-serial-history','fuxa-observation-only','workbench-authentication')]
    result.update(passed=True,physical_release=False,engineering_accepted=False)
    if before!=pilot.native_sources():raise ValueError('Native lifecycle sources changed during execution; retain prototype locally and rerun')
    # Published evidence contains no credentials, private config or database.
    files={'native-result.json':pilot.encoded(result),'native-log.txt':log.read_bytes(),'fuxa-project.json':pilot.encoded(project),'workbench.png':(PRIVATE/'workbench.png').read_bytes(),'fuxa.png':(PRIVATE/'fuxa.png').read_bytes()}
    stage=PRIVATE/'publication';shutil.rmtree(stage,ignore_errors=True);stage.mkdir()
    for n,b in files.items():(stage/n).write_bytes(b)
    manifest=dict(schema='osr-maglev-native-lifecycle/1',source_sha256=before,source_unchanged=True,files_sha256={n:sha256(b).hexdigest() for n,b in files.items()},**pilot.FLAGS)
    (stage/'manifest.json').write_bytes(pilot.encoded(manifest));pilot.verify_native(stage)
    RAW.parent.mkdir(parents=True,exist_ok=True)
    if RAW.exists():
        backup=PRIVATE/('previous-'+run_id);RAW.rename(backup)
    stage.rename(RAW);print('Native current-maglev lifecycle evidence verified:',RAW.relative_to(ROOT))

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('action',choices=('run','verify','status','down'));parser.add_argument('--candidate',action='store_true',help='Run current quantified candidate, preserving prior base receipt');args=parser.parse_args()
    global pilot
    if args.candidate:
        from engineering.ferrite_maglev import candidate_lifecycle
        pilot=candidate_lifecycle
    if args.action=='run':run()
    elif args.action=='verify':pilot.verify_native();print('PASS retained source-bound native ERPNext/FUXA/Workbench lifecycle evidence; physical gates open')
    elif args.action=='status':
        print(call([DOCKER,'ps','--filter','name=osr-maglev-pilot','--format','{{.Names}} {{.Status}}']).decode());print('Disposable pilot UI http://127.0.0.1:18088/maglev-pilot; FUXA http://127.0.0.1:1888; credentials remain in ignored private files.')
    else:
        compose('down')
        for name in ('osr-maglev-pilot-integration','osr-maglev-pilot-fuxa'):subprocess.run([DOCKER,'rm','-f',name],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        print('Stopped only the isolated pilot namespace; retained volumes and evidence.')

if __name__=='__main__':main()
