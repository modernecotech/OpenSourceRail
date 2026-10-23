"""Current-maglev software-pilot journal. Business review never releases hardware."""
from copy import deepcopy
from contextlib import contextmanager
from hashlib import sha256
import json
import re
import sqlite3
from pathlib import Path

SCHEMA='osr-maglev-pilot-lifecycle/1'
ROLES={'purchase':'planner','receive':'stock','inspect':'inspector','rework':'technician',
       'assemble':'assembler','install':'engineer','alarm':'observer','maintain':'maintainer',
       'remove':'maintainer','test':'inspector','handback':'reviewer','revision-proposal':'engineer'}
FLAGS={'design_complete':False,'physical_validation':False,'manufacturing_release':False,
       'physical_release':False,'engineering_accepted':False}


def digest(value):return sha256(json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
def valid_hash(v):return isinstance(v,str) and re.fullmatch('[0-9a-f]{64}',v) is not None

def validate_package(package):
    if package.get('schema')!=SCHEMA or package.get('environment')!='simulation':raise ValueError('simulation-only maglev lifecycle package required')
    if package.get('sha256')!=digest({k:v for k,v in package.items() if k!='sha256'}):raise ValueError('lifecycle package checksum differs')
    if any(package.get(k) is not False for k in FLAGS):raise ValueError('software pilot cannot release hardware')
    if not valid_hash(package.get('configuration_sha256')) or not package.get('configuration_id'):raise ValueError('exact controlled configuration required')
    if package.get('city')!='baghdad' or package.get('railway_family')!='fixed-zone-ferrite-maglev':raise ValueError('current Baghdad maglev scope required')
    products=package.get('products',[])
    if not products or len(products)!=len({p['product_id'] for p in products}):raise ValueError('unique current products required')
    for p in products:
        if not p['product_id'].startswith('OSR-PILOT-') or not valid_hash(p['product_revision_sha256']):raise ValueError('current product and revision required')
        if p.get('release')!='draft-unqualified' or not p.get('bom'):raise ValueError('draft current manufacturing BOM required')
        for line in p['bom']:
            if not line.get('id') or line.get('state') not in {'defined','allocated','missing'}:raise ValueError('typed BOM identity/state required')
    positions=package.get('positions',[])
    if len(positions)!=3 or len({p['asset_id'] for p in positions})!=3:raise ValueError('three distinct pilot positions required')
    for p in positions:
        if p['product_id'] not in {x['product_id'] for x in products} or not p['asset_id'].startswith('SIM-BAG-'):raise ValueError('simulation position/current product binding required')
    return package


def initial_state(package):
    validate_package(package)
    return dict(articles={},positions={p['asset_id']:dict(product_id=p['product_id'],serial=None,removed=[],
        condition='uninstalled',maintenance=False,replacement_required=False,last_test=None,handback='hold',revision_hold=False) for p in package['positions']},
        revision_requests=[],physical_release=False,engineering_accepted=False)


def validate_command(command,package):
    fields={'id','kind','asset_id','serial','batch','configuration_sha256','product_revision_sha256','actor','role','evidence','data'}
    if not isinstance(command,dict) or set(command)!=fields:raise ValueError('exact typed lifecycle command required')
    if not isinstance(command['id'],str) or not re.fullmatch(r'[A-Za-z0-9_.:-]{1,150}',command['id']):raise ValueError('bounded event identity required')
    if command['kind'] not in ROLES or command['role']!=ROLES[command['kind']]:raise PermissionError('lifecycle role does not permit action')
    if not command['actor'] or command['actor']=='Guest':raise PermissionError('named authenticated or explicit simulator actor required')
    position=next((p for p in package['positions'] if p['asset_id']==command['asset_id']),None)
    if not position:raise ValueError('asset outside controlled pilot')
    product=next(p for p in package['products'] if p['product_id']==position['product_id'])
    if command['configuration_sha256']!=package['configuration_sha256'] or command['product_revision_sha256']!=product['product_revision_sha256']:
        raise ValueError('stale or incompatible configuration/product revision')
    if not re.fullmatch(r'SIM-[A-Za-z0-9_.:-]{1,100}',command['serial']) or not command['batch'].startswith('SIM-'):raise ValueError('simulated serial/batch required')
    if not isinstance(command['evidence'],list) or not 1<=len(command['evidence'])<=30 or any(not valid_hash(x) for x in command['evidence']):raise ValueError('versioned evidence byte digests required')
    if not isinstance(command['data'],dict) or any(k in command['data'] for k in ('physical_release','manufacturing_release','engineering_accepted','movement_authority')):raise ValueError('no physical authority in business commands')
    digest(command)
    return position,product


def transition(before,command,package):
    validate_command(command,package);state=deepcopy(before);kind=command['kind'];serial=command['serial'];asset=command['asset_id'];pos=state['positions'][asset];data=command['data']
    article=state['articles'].get(serial)
    if kind=='purchase':
        if article:raise ValueError('serial already has purchasing history')
        if set(data)!={'draft_material_request','draft_purchase_order','bom_sha256'} or not valid_hash(data['bom_sha256']):raise ValueError('draft purchasing/BOM references required')
        state['articles'][serial]=dict(asset_id=asset,batch=command['batch'],revision=command['product_revision_sha256'],stage='purchase-draft',
            inspections=[],rework=[],installed_at=None,removed=False,native_records=deepcopy(data))
        return state
    if not article or article['asset_id']!=asset or article['batch']!=command['batch'] or article['revision']!=command['product_revision_sha256']:raise ValueError('serial/batch/revision history mismatch')
    if kind=='receive':
        if article['stage']!='purchase-draft' or not data.get('receipt'):raise ValueError('draft purchase required before simulated receipt')
        article['stage']='received-quarantine';article['native_records']['receipt']=data['receipt']
    elif kind=='inspect':
        if article['stage'] not in {'received-quarantine','reworked','inspection-passed','inspection-failed'} or set(data)!={'result','inspection'} or data['result'] not in {'pass','fail'}:raise ValueError('receipt/rework and typed inspection required')
        # A later failure invalidates every earlier pass.
        article['inspections'].append(dict(result=data['result'],record=data['inspection'],actor=command['actor'],event_id=command['id']))
        article['stage']='inspection-passed' if data['result']=='pass' else 'inspection-failed'
    elif kind=='rework':
        if article['stage']!='inspection-failed' or not data.get('nonconformance') or not data.get('rework_order'):raise ValueError('failed inspection and NCR/rework order required')
        article['rework'].append(deepcopy(data));article['stage']='reworked'
    elif kind=='assemble':
        if article['stage']!='inspection-passed' or not data.get('work_order') or not data.get('manufacture_entry'):raise ValueError('latest passing inspection required before assembly')
        article['stage']='assembled';article['native_records'].update(deepcopy(data))
    elif kind=='install':
        if article['stage']!='assembled' or pos['serial'] or pos['revision_hold']:raise ValueError('assembled unit and vacant compatible position required')
        if pos['removed'] and data.get('replaces_serial')!=pos['removed'][-1]:raise ValueError('replacement must identify exact removed serial')
        if not data.get('installation_record'):raise ValueError('installation record required')
        pos.update(serial=serial,condition='installed-unreviewed',replacement_required=False,handback='hold',last_test=None);article['stage']='installed';article['installed_at']=asset
    elif kind=='alarm':
        if pos['serial']!=serial or not data.get('incident_id'):raise ValueError('alarm requires current installed serial')
        pos.update(condition='alarm-active',replacement_required=True,handback='hold',last_test=None)
    elif kind=='maintain':
        if pos['serial']!=serial or pos['condition']!='alarm-active' or not data.get('maintenance_case'):raise ValueError('current alarm and maintenance case required')
        pos.update(maintenance=True,condition='maintenance',handback='hold',last_test=None)
    elif kind=='remove':
        if pos['serial']!=serial or not pos['maintenance'] or not data.get('removal_record'):raise ValueError('maintenance/removal evidence required')
        pos['removed'].append(serial);pos.update(serial=None,handback='hold',last_test=None);article.update(stage='removed',removed=True)
    elif kind=='test':
        if pos['serial']!=serial or data.get('result') not in {'pass','fail'} or not data.get('test_record'):raise ValueError('current installed serial and exact test required')
        pos['last_test']=dict(result=data['result'],actor=command['actor'],id=command['id'],serial=serial,evidence=deepcopy(command['evidence']))
        pos['handback']='hold';pos['condition']='tested' if data['result']=='pass' else 'test-failed'
    elif kind=='handback':
        test=pos['last_test']
        if pos['serial']!=serial or not test or test['result']!='pass' or data.get('test_id')!=test['id'] or command['actor']==test['actor'] or pos['revision_hold'] or pos['replacement_required']:
            raise ValueError('independent reviewer and latest passing exact-serial test required')
        if not data.get('review_record'):raise ValueError('independent business review reference required')
        pos.update(handback='simulation-business-reviewed',condition='software-pilot-reviewed',maintenance=False)
    elif kind=='revision-proposal':
        if not valid_hash(data.get('proposed_product_revision_sha256')) or data['proposed_product_revision_sha256']==article['revision']:raise ValueError('distinct proposed revision required')
        pos.update(revision_hold=True,handback='hold');state['revision_requests'].append(dict(asset_id=asset,installed_serial=pos['serial'],old_revision=article['revision'],new_revision=data['proposed_product_revision_sha256'],actor=command['actor'],state='independent-review-and-retest-required'))
    return state


class Ledger:
    """Transactional append-only journal with replay, idempotency and restart checks."""
    def __init__(self,path,package):
        self.path=Path(path);self.package=deepcopy(validate_package(package));self.path.parent.mkdir(parents=True,exist_ok=True)
        with self.connect() as db:
            db.executescript('CREATE TABLE IF NOT EXISTS meta (key TEXT PRIMARY KEY,value TEXT NOT NULL); CREATE TABLE IF NOT EXISTS events (seq INTEGER PRIMARY KEY,id TEXT UNIQUE NOT NULL,body TEXT NOT NULL,previous_sha256 TEXT NOT NULL,sha256 TEXT NOT NULL); CREATE TRIGGER IF NOT EXISTS immutable_events_update BEFORE UPDATE ON events BEGIN SELECT RAISE(ABORT,"immutable lifecycle history"); END; CREATE TRIGGER IF NOT EXISTS immutable_events_delete BEFORE DELETE ON events BEGIN SELECT RAISE(ABORT,"immutable lifecycle history"); END;')
            old=db.execute('SELECT value FROM meta WHERE key="package"').fetchone()
            if old and old[0]!=digest(package):raise ValueError('changed configuration cannot overwrite existing serial history')
            db.execute('INSERT OR IGNORE INTO meta VALUES("package",?)',(digest(package),))
        self.snapshot()
    @contextmanager
    def connect(self):
        db=sqlite3.connect(self.path,timeout=10);db.row_factory=sqlite3.Row
        try:
            with db:yield db
        finally:db.close()
    def _read(self,db):
        state=initial_state(self.package);previous='0'*64;events=[]
        for row in db.execute('SELECT * FROM events ORDER BY seq'):
            command=json.loads(row['body'])
            if row['seq']!=len(events)+1 or row['previous_sha256']!=previous or row['sha256']!=digest(dict(seq=row['seq'],command=command,previous_sha256=previous)) or row['id']!=command['id']:raise ValueError('lifecycle history or hash chain altered')
            state=transition(state,command,self.package);previous=row['sha256'];events.append(dict(seq=row['seq'],command=command,previous_sha256=row['previous_sha256'],sha256=row['sha256']))
        return dict(state=state,events=events,head_sha256=previous,environment='simulation',**FLAGS)
    def snapshot(self):
        with self.connect() as db:return self._read(db)
    def append(self,command,*,expected_head=None):
        with self.connect() as db:
            db.execute('BEGIN IMMEDIATE');snapshot=self._read(db);old=db.execute('SELECT body FROM events WHERE id=?',(command.get('id'),)).fetchone()
            if old:
                if json.loads(old[0])!=command:raise ValueError('event identity reused with changed data or actor')
                return dict(created=False,head_sha256=snapshot['head_sha256'])
            if expected_head is not None and expected_head!=snapshot['head_sha256']:raise ValueError('stale lifecycle preview')
            transition(snapshot['state'],command,self.package);seq=len(snapshot['events'])+1;fingerprint=digest(dict(seq=seq,command=command,previous_sha256=snapshot['head_sha256']))
            db.execute('INSERT INTO events VALUES(?,?,?,?,?)',(seq,command['id'],json.dumps(command,sort_keys=True,allow_nan=False),snapshot['head_sha256'],fingerprint))
            return dict(created=True,head_sha256=fingerprint)
