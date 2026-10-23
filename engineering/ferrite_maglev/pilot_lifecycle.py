"""Controlled maglev business lifecycle; simulated business handback is not release.

The same identity/transition contract is imported by the ERP adapter. Native
execution is an explicit separate command; packet readers never start services.
"""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import gzip
import json
import sys
import tempfile
import tomllib

from . import model, pilot_product

ROOT=model.ROOT
INPUT=Path(__file__).with_name('pilot-lifecycle.toml')
OUTPUT=ROOT/'docs/design-engine/ferrite-maglev/pilot-lifecycle'
RAW=ROOT/'engineering/assurance/v052-pilot-lifecycle-native'
ERP=ROOT/'deployment/erpnext/apps/osr_erpnext'
INTEGRATION=ROOT/'services/integration'
for path in (ERP,INTEGRATION):
    if str(path) not in sys.path:sys.path.insert(0,str(path))
from osr_erpnext import maglev_lifecycle_contract as contract, planning, engineering_identity
from osr_integration import config as supervisory, fuxa

SCHEMA=contract.SCHEMA
FLAGS={**model.FLAGS,**contract.FLAGS,'automatic_handback':False,'movement_authority':False}
FILES={'study.json.gz','lifecycle-package.json','planning-bundle.json','supervisory-package.json','fuxa-project.json','serial-history.json','qa-travellers.json','unit-procedures.json','dimension-schedules.json','README.md'}
NATIVE_FILES={'native-workbench.png','native-fuxa.png'}

def encoded(v):return (json.dumps(v,sort_keys=True,indent=2,allow_nan=False)+'\n').encode()
def digest(p):return sha256(Path(p).read_bytes()).hexdigest()
def source_paths():
    own=[Path(__file__),INPUT,ROOT/'engineering/analysis/tests/test_ferrite_maglev_pilot_lifecycle.py',
         ROOT/'tools/automation/pilot-lifecycle-native.py',ERP/'osr_erpnext/maglev_pilot.py',
         ERP/'osr_erpnext/www/maglev-pilot.html',ERP/'osr_erpnext/www/maglev_pilot.py',
         *[Path(x.__file__) for x in (contract,planning,engineering_identity,supervisory,fuxa)]]
    own += [ERP/'osr_erpnext'/n for n in ('api.py','components.py','integration.py','procurement.py','disposition.py','disposition_contract.py','disposition_execution.py','lifecycle_governance.py')]
    own += [INTEGRATION/'osr_integration'/n for n in ('store.py','server.py')]
    own += [Path(__file__).parent/'data/qualification-plan.json']
    own += [ROOT/n for n in ('deployment/erpnext/compose.yaml','deployment/erpnext/Dockerfile','deployment/erpnext/configure-nginx.py','deployment/supervision/Dockerfile','package.json','package-lock.json')]
    own += [q for base in (ERP/'osr_erpnext',INTEGRATION/'osr_integration') for q in base.rglob('*')
            if q.is_file() and q.suffix in {'.py','.json','.js','.html'} and '__pycache__' not in q.parts]
    return sorted(set(own)|set(pilot_product.source_paths()))
def sources():return {p.relative_to(ROOT).as_posix():digest(p) for p in source_paths()}

def load():
    a=tomllib.loads(INPUT.read_text())
    if a['schema']!='osr-maglev-pilot-lifecycle-input/1' or a['environment']!='simulation' or a['city']!='baghdad' or len(a['positions'])!=3:raise ValueError('bounded current Baghdad software pilot required')
    return a

def lifecycle_package():
    a=load();cfg=pilot_product.configuration_profile(a['configuration_id'])
    wanted={p['product_id'] for p in a['positions']};rows=[]
    for p in pilot_product.products(cfg):
        if p['id'] not in wanted:continue
        bom=[]
        for line in p['bom']:
            # Preserve the complete engineering row and bind its bytes. Native
            # stock quantities are business fixtures, not a qualified process.
            state=line['definition_state'].lower()
            if state not in {'defined','allocated','missing'}:raise ValueError('unknown engineering BOM definition state')
            bom.append(dict(id=line['id'],state=state,source=deepcopy(line),source_sha256=contract.digest(line)))
        rows.append(dict(product_id=p['id'],product_revision_sha256=p['product_revision_sha256'],geometry_sha256=p['geometry_sha256'],
            geometry_source_ids=p['geometry_source_ids'],bom=bom,release='draft-unqualified',cost_state='unquoted-engineering-estimate'))
    package=dict(schema=SCHEMA,revision=a['revision'],environment=a['environment'],city=a['city'],railway_family=a['railway_family'],
        configuration_id=cfg['id'],configuration_sha256=cfg['configuration_sha256'],products=rows,positions=a['positions'],**contract.FLAGS)
    package['sha256']=contract.digest(package)
    return contract.validate_package(package)

def planning_bundle(package=None):
    p=package or lifecycle_package();manufacture=[];maintenance=[]
    for pos in p['positions']:
        product=next(x for x in p['products'] if x['product_id']==pos['product_id'])
        common=dict(asset_id=pos['asset_id'],product_id=pos['product_id'],configuration_sha256=p['configuration_sha256'],
            product_revision_sha256=product['product_revision_sha256'],bom=product['bom'],release='draft-unqualified',environment='simulation',schedule_reference=pos['schedule_reference'])
        manufacture.append(dict(manufacturing_uid=pos['asset_id']+'-manufacture',title='Draft '+pos['product_id']+' manufacture and inspection',**common))
        maintenance.append(dict(task_uid=pos['asset_id']+'-maintenance',title='Inspect, replace and independently review current maglev serial',**common))
    bundle=dict(project_twin=dict(city=p['city'],revision_id=p['revision']+'-'+p['configuration_sha256'][:12]),manufacturing_tasks=manufacture,maintenance_tasks=maintenance)
    # Executing this retained adapter is a compatibility check, not a parallel
    # schema that merely resembles its input.
    planning.validate_plan(planning.make_plan(bundle))
    return bundle

def supervisory_package(package=None,*,project='',bindings=None):
    p=package or lifecycle_package();templates={}
    for pos in p['positions']:
        templates[pos['supervisory_kind']]=dict(label=pos['product_id'],asset_types=[pos['site_type']],component_type_id=pos['product_id'],
            measurements={'condition_code':dict(min=0,max=1,unit='simulation-code',stale_seconds=30)},
            alarms=[dict(id='software-fixture-fault',measurement='condition_code',high=1,clear_below=.5,delay_seconds=0,repeat_seconds=60,
                         maintenance=True,response='Inspect simulated condition; no physical threshold or release.')],commands={})
    generic=dict(template_revision=p['revision'],rolling_stock_family=p['railway_family'],historian=dict(owner='osr-integration',retention_days=30,sampling_seconds=2),templates=templates)
    assets=[dict(asset_id=x['asset_id'],asset_type=x['site_type'],name=x['asset_id']) for x in p['positions']]
    return supervisory.build_package(generic,dict(city=p['city'],company=load()['company'],erp_project=project,bindings=bindings or {}),assets,p['configuration_sha256'],environment='simulation')

def fuxa_project(supervision):
    project=fuxa.project([supervision],workbench_url='http://127.0.0.1:18088')
    project['name']='OpenSourceRail current-maglev software pilot'
    for view in project['hmi']['views']:
        view['svgcontent']=view['svgcontent'].replace('href="http://127.0.0.1:18088/?','href="http://127.0.0.1:18088/maglev-pilot?')
    return project


def command(package,position,serial,kind,index,data,*,actor=None):
    product=next(x for x in package['products'] if x['product_id']==position['product_id'])
    evidence=encoded(dict(label='explicit synthetic business fixture',asset_id=position['asset_id'],serial=serial,kind=kind,index=index,data=data))
    return dict(id=f'{position["asset_id"]}:{serial}:{index}:{kind}',kind=kind,asset_id=position['asset_id'],serial=serial,batch='SIM-BATCH-'+position['asset_id'],
        configuration_sha256=package['configuration_sha256'],product_revision_sha256=product['product_revision_sha256'],actor=actor or 'sim-'+contract.ROLES[kind],
        role=contract.ROLES[kind],evidence=[sha256(evidence).hexdigest()],data=data)

def scenario(package=None,directory=None):
    """Execute all three current products, durable restart and adversarial controls."""
    p=package or lifecycle_package();temporary=tempfile.TemporaryDirectory() if directory is None else None
    directory=Path(temporary.name if temporary else directory);directory.mkdir(parents=True,exist_ok=True)
    ledger=contract.Ledger(directory/'lifecycle.sqlite',p);controls=[];raw=[]
    def append(pos,serial,kind,data,actor=None):
        index=len(ledger.snapshot()['events'])+1;c=command(p,pos,serial,kind,index,data,actor=actor)
        r=ledger.append(c);raw.append(dict(command=c,source='synthetic-software-fixture',native_record=False))
        if ledger.append(c)['created']:raise AssertionError('duplicate appended')
        return c
    def rejected(name,c):
        before=ledger.snapshot()
        try:ledger.append(c)
        except (ValueError,PermissionError):
            if ledger.snapshot()!=before:raise AssertionError('rejected transaction changed history')
            controls.append(dict(id=name,result='rejected-without-history-change'));return
        raise AssertionError(name+' accepted')
    for pos in p['positions']:
        old='SIM-'+pos['asset_id']+'-OLD';new='SIM-'+pos['asset_id']+'-NEW'
        for serial in (old,new):
            append(pos,serial,'purchase',dict(draft_material_request='SIM-MR-'+serial,draft_purchase_order='SIM-PO-'+serial,bom_sha256=contract.digest(next(x for x in p['products'] if x['product_id']==pos['product_id'])['bom'])))
            append(pos,serial,'receive',dict(receipt='SIM-PR-'+serial))
            if serial==old:
                append(pos,serial,'inspect',dict(result='pass',inspection='SIM-QI-EARLY'))
                append(pos,serial,'inspect',dict(result='fail',inspection='SIM-QI-NCR'))
                rejected(pos['asset_id']+'/later-inspection-failure',command(p,pos,serial,'assemble',900,dict(work_order='SIM-WO',manufacture_entry='SIM-SE')))
                append(pos,serial,'rework',dict(nonconformance='SIM-NCR-'+serial,rework_order='SIM-REWORK-'+serial))
            append(pos,serial,'inspect',dict(result='pass',inspection='SIM-QI-PASS-'+serial))
            append(pos,serial,'assemble',dict(work_order='SIM-WO-'+serial,manufacture_entry='SIM-SE-'+serial))
            append(pos,serial,'install',dict(installation_record='SIM-INSTALL-'+serial,**(dict(replaces_serial=old) if serial==new else {})))
            passed=append(pos,serial,'test',dict(result='pass',test_record='SIM-TEST-'+serial))
            if serial==new:
                append(pos,serial,'test',dict(result='fail',test_record='SIM-TEST-LATE-FAIL'))
                rejected(pos['asset_id']+'/later-test-failure',command(p,pos,serial,'handback',901,dict(test_id=passed['id'],review_record='SIM-REVIEW')))
                passed=append(pos,serial,'test',dict(result='pass',test_record='SIM-RETEST-'+serial))
                rejected(pos['asset_id']+'/self-review',command(p,pos,serial,'handback',902,dict(test_id=passed['id'],review_record='SIM-SELF'),actor=passed['actor']))
            append(pos,serial,'handback',dict(test_id=passed['id'],review_record='SIM-INDEPENDENT-REVIEW-'+serial))
            if serial==old:
                append(pos,serial,'alarm',dict(incident_id='SIM-INCIDENT-'+serial))
                append(pos,serial,'maintain',dict(maintenance_case='SIM-REPAIR-'+serial))
                append(pos,serial,'remove',dict(removal_record='SIM-REMOVE-'+serial))
                # Open a new connection/object after committing the removal.
                before=ledger.snapshot();ledger=contract.Ledger(directory/'lifecycle.sqlite',p)
                if before!=ledger.snapshot():raise AssertionError('restart lost history')
                controls.append(dict(id=pos['asset_id']+'/restart',result='committed-history-replayed'))
        stale=command(p,pos,new,'test',903,dict(result='pass',test_record='SIM-STALE'));stale['configuration_sha256']='f'*64
        rejected(pos['asset_id']+'/stale-revision',stale)
        denied=command(p,pos,new,'alarm',904,dict(incident_id='SIM-DENIED'));denied['role']='reviewer'
        rejected(pos['asset_id']+'/wrong-role',denied)
        append(pos,new,'revision-proposal',dict(proposed_product_revision_sha256=contract.digest(dict(candidate='unadopted-revision',old=p['configuration_sha256']))))
        rejected(pos['asset_id']+'/changed-revision-handback',command(p,pos,new,'handback',905,dict(test_id=passed['id'],review_record='SIM-STALE-REVISION')))
    snapshot=ledger.snapshot()
    # Source evidence bodies are retained alongside their byte hashes. They are
    # deliberately synthetic and cannot count as measured engineering evidence.
    if temporary:temporary.cleanup()
    return dict(snapshot=snapshot,controls=controls,raw=raw,physical_evidence=False)

def qa_travellers(package=None):
    p=package or lifecycle_package();rows=[]
    for pos in p['positions']:
        product=next(x for x in p['products'] if x['product_id']==pos['product_id']);serial='SIM-'+pos['asset_id']+'-NEW';batch='SIM-BATCH-'+pos['asset_id']
        char=dict(inspection_id=pos['asset_id']+'/simulation-record-code',instance_id=pos['asset_id'],part_id=pos['product_id'],part_revision=product['product_revision_sha256'],
            serial=serial,batch=batch,characteristic='Software record fixture, not a material/property test',unit='simulation-code',minimum=None,maximum=None,joint_ids=[])
        identity=dict(schema='osr-engineering-qa-map/1',configuration_sha256=p['configuration_sha256'],design_revision=product['product_revision_sha256'],state='as-maintained',asset_id=pos['asset_id'],characteristics=[char])
        identity['sha256']=engineering_identity.digest(identity)
        binding=engineering_identity.bind_quality_result(identity,dict(project='SIM-PROJECT',company=load()['company'],work_order='SIM-WO-'+serial,quality_inspection='SIM-QI-'+serial,material_batch=batch,nonconformance=None,calibration_record='SIM-SOFTWARE-NO-PHYSICAL-CALIBRATION'),
            dict(inspection_id=char['inspection_id'],configuration_sha256=p['configuration_sha256'],part_revision=product['product_revision_sha256'],serial=serial,batch=batch,unit='simulation-code',value=1))
        protocol_ids={'OSR-PILOT-MAGNETIC-CARTRIDGE':['magnetic-module','restrained-support','industrial-first-article'],'OSR-PILOT-GUIDEBEAM-25M':['civil-prestress-handling','baghdad-site','moving-guideway'],'OSR-PILOT-LAUNCH-CASSETTE-2P5M':['station-stator','target-io-timing','industrial-first-article']}
        rows.append(dict(identity=identity,binding=binding,physical_test_executed=False,qualified_limits=None,required_physical_protocols=protocol_ids[pos['product_id']],protocol_source='engineering/ferrite_maglev/data/qualification-plan.json',authenticated_independent_acceptance=False))
    return rows

def unit_procedures(package=None):
    """Issued provisional digital work instructions, with physical holds intact.

    No unknown prestress, cure time, torque, weld or acceptance tolerance is
    invented. Every such operation identifies the evidence needed to release it.
    """
    from . import geometry, drive_design
    p=package or lifecycle_package();bay=pilot_product.bay_definition();coil=drive_design.winding(zone=350.)
    definitions={
      'OSR-PILOT-MAGNETIC-CARTRIDGE':dict(parts=[*bay['retained_parts'],*bay['equipment']],drawing='pilot-product/bay-views.svg',
        steps=['Freeze exact product/BOM/geometry revision; purchase ferrite, carrier stock and winding/sensor/drive kits against draft specification.',
          'Machine carrier and inspect actual bore positions/edge clearances; retain material and serial/batch records.',
          'Fixture and positively retain ferrite; protect magnetic handling and prevent uncontrolled attraction.',
          'Install separately identified lift/guidance winding packs, sensors, current circuits, cooling and connector provisions; detailed missing parts remain holds.',
          'Inspect dimensions, insulation, continuity, sensor mapping and retention; magnetic force/loss/thermal rig tests require qualified limits.',
          'Support/isolate the installed assembly before removal; retained downward extraction has an identified obstruction. Evaluate the separate segmented-collector lateral candidate, not an unauthorised cut.',
          'Capture old/new serial and connector identity, repeat gap/current/sensor tests and independent physical acceptance before any deployment.'],
        holds=['Qualified magnetic force/loss/temperature maps','Resolved complete cartridge replacement path and segmented-collector joints','Qualified retention/torque and electrical/cooling connector drawings']),
      'OSR-PILOT-GUIDEBEAM-25M':dict(parts=geometry.beam_parts('pilot-guidebeam-25m',25.),drawing='dimension-schedules.json#OSR-PILOT-GUIDEBEAM-25M',
        steps=['Freeze section, support and exact reinforcement/prestress drawing; require site/ground, load and handling basis.',
          'Inspect mould/reinforcement/ducts/embedded passive-rail interfaces before casting; record batch and curing instruments.',
          'Cast and cure under approved process; specimen strength and release force/time are unqualified until supplier/engineer approval.',
          'Check as-cast dimensions and material evidence before demoulding; handling/lifting/transport stages require independent calculations.',
          'Survey supports, temporary stability and crane radius/ground support; lift and lock using an approved erection method.',
          'Record installed beam serial, passive-rail alignment, connections, survey and damage checks; preserve rejected/reworked records.',
          'During replacement, isolate service, independently support neighbouring units and verify staged load paths; repeat survey/structure acceptance.'],
        holds=['Detailed reinforcement/tendons/anchorage and prestress process','Lifting inserts, temporary support and crane/site qualification','Concrete strength/curing, survey tolerances and independent structure/site acceptance']),
      'OSR-PILOT-LAUNCH-CASSETTE-2P5M':dict(parts=deepcopy(coil['schedule']),drawing='dimension-schedules.json#OSR-PILOT-LAUNCH-CASSETTE-2P5M',
        steps=['Freeze winding schedule, copper bar geometry, insulation class, section identity and protected-zone interface.',
          'Form and inspect winding against source conductor length/turn schedule; record conductor batch, continuity and insulation.',
          'Mount against an issued support/fastener/thermal expansion design; support and interfaces remain allocations until detailed.',
          'Connect current sensing, drive isolation and independently protected enable; prove wrong-zone/stale/replay refusal offline.',
          'Execute current, thrust/loss/thermal and target timing tests on a bounded rig; simulation does not supply physical calibration.',
          'Install serial within exact guideway zone and align relative to train reaction surface; record surveyed location and power/protection interfaces.',
          'For replacement prove dead and support assembly, record removed serial, inspect electrical/mechanical joints, retest independent zone protection and physical acceptance.'],
        holds=['Complete support, fastener, insulation and service-interface drawings','Measured thrust/loss/temperature and continuous thermal limits','Protected power zone, target hardware timing/EMI and independently witnessed acceptance'])}
    rows=[];dimensions=[]
    for pos in p['positions']:
        product=next(x for x in p['products'] if x['product_id']==pos['product_id']);definition=definitions[pos['product_id']]
        row=dict(product_id=pos['product_id'],position_id=pos['asset_id'],configuration_sha256=p['configuration_sha256'],product_revision_sha256=product['product_revision_sha256'],
            geometry_sha256=product['geometry_sha256'],digital_instruction_state='provisional-issued-for-study',physical_instruction_state='unapproved-unexecuted',
            drawing_reference=definition['drawing'],drawing_scope='Source-bound provisional dimensions, not a supplier fabrication drawing',
            procurement=[dict(source_line_id=x['id'],source_sha256=x['source_sha256'],quantity=x['source']['quantity'],unit=x['source']['unit'],definition_state=x['state'],
                supplier=None,supplier_quote=None,material_certificate=None,approved_specification=None,purchase_release=False) for x in product['bom']],
            assembly_steps=[dict(sequence=i+1,instruction=s,physical_executed=False) for i,s in enumerate(definition['steps'])],
            qualification_protocol_ids=next(x['required_physical_protocols'] for x in qa_travellers(p) if x['identity']['asset_id']==pos['asset_id']),
            inspection_plan=[dict(id=pos['product_id']+'/'+name,stage=stage,serial=None,measured_results=None,evidence_sha256=None,qualified_limits=None,qualified_reviewer=None,state='unexecuted-hold')
                for name,stage in [('revision-and-material-trace','incoming'),('dimensions-and-interfaces','factory'),('functional-rig','factory'),('handling-and-damage','transport'),('survey-and-connection','installed'),('replacement-independent-review','maintained')]],
            open_approval_holds=definition['holds'],manufacturing_release=False,physical_release=False)
        rows.append(row);dimensions.append(dict(product_id=pos['product_id'],product_revision_sha256=product['product_revision_sha256'],configuration_sha256=p['configuration_sha256'],
            source_geometry_sha256=product['geometry_sha256'],parts=definition['parts'],units='m unless a named field declares another unit',tolerance_values=None,approved=False))
    return rows,dimensions

def native_sources():return sources()

def verify_native(raw=RAW):
    raw=Path(raw);m=json.loads((raw/'manifest.json').read_bytes())
    required={'native-result.json','native-log.txt','fuxa-project.json','workbench.png','fuxa.png'}
    if m.get('schema')!='osr-maglev-native-lifecycle/1' or m.get('source_sha256')!=native_sources() or m.get('source_unchanged') is not True:raise ValueError('native lifecycle receipt missing/stale')
    if set(m.get('files_sha256',{}))!=required or set(x.name for x in raw.iterdir())!=required|{'manifest.json'}:raise ValueError('native lifecycle payload coverage differs')
    if any(m.get(k) is not False for k in FLAGS):raise ValueError('native business receipt cannot release railway')
    for n,h in m['files_sha256'].items():
        if (raw/n).is_symlink() or not (raw/n).is_file() or digest(raw/n)!=h:raise ValueError('native lifecycle evidence altered')
    r=json.loads((raw/'native-result.json').read_bytes())
    if r.get('configuration_sha256')!=lifecycle_package()['configuration_sha256'] or r.get('environment')!='simulation' or r.get('passed') is not True:raise ValueError('native lifecycle identity/result differs')
    expected={'native-erp-manufacture','native-receipt-quality-fail-rework','native-revision-disposition','native-alarm-repair','independent-business-review','restart-replay','permission-refusal','late-failure-refusal','removed-serial-history','fuxa-observation-only','workbench-authentication'}
    if {x['id'] for x in r.get('checks',[]) if x.get('passed') is True}!=expected:raise ValueError('native lifecycle check coverage differs')
    if len(r.get('products',[]))!=3 or any(x.get('physical_release') is not False for x in r['products']):raise ValueError('all three exact products and physical holds required')
    for row in r['products']:
        if not all(row.get(k) for k in ('product_revision_sha256','asset','purchase_order','receipt','failed_inspection','rework_task','work_orders','stock_entries','issue','asset_repair','old_serial','current_serial','serial_history')):raise ValueError('native document/serial chain incomplete')
    package=lifecycle_package();expected_products={x['product_id']:x for x in package['products']};positions={x['asset_id']:x for x in package['positions']}
    if len({x['asset_id'] for x in r['products']})!=3 or {x['asset_id'] for x in r['products']}!=set(positions):raise ValueError('native controlled position coverage differs')
    records={(x['doctype'],x['name']):x for x in r.get('native_documents',[])}
    if len(records)!=len(r.get('native_documents',[])):raise ValueError('duplicate native document readback')
    for row in r['products']:
        product=expected_products.get(row['product_id'])
        if not product or product['product_revision_sha256']!=row['product_revision_sha256'] or positions[row['asset_id']]['product_id']!=row['product_id']:raise ValueError('native product revision/position differs')
        failed=records.get(('Quality Inspection',row['failed_inspection']),{})
        if failed.get('docstatus')!=1 or failed.get('values',{}).get('status')!='Rejected':raise ValueError('native rejected quality record absent')
        for name in row['work_orders']:
            doc=records.get(('Work Order',name),{})
            if doc.get('docstatus')!=1 or doc.get('values',{}).get('produced_qty')!=1:raise ValueError('native manufacture not completed')
        if len(row['work_orders'])!=2 or len(row['stock_entries'])!=2:raise ValueError('original and replacement manufacture required')
        for dt,key in [('Purchase Order','purchase_order'),('Purchase Receipt','receipt'),('Asset','asset'),('Asset Repair','asset_repair')]:
            if records.get((dt,row[key]),{}).get('docstatus')!=1:raise ValueError('submitted native business record absent')
        repair=records[('Asset Repair',row['asset_repair'])]['values']
        if repair.get('repair_status')!='Completed' or repair.get('custom_osr_handback_required')!=1:raise ValueError('repair must preserve independent handback hold')
        if row['old_serial'] not in row['serial_history']['removed'] or row['serial_history']['serial']!=row['current_serial']:raise ValueError('removed/current serial chain differs')
        if records[('Asset',row['asset'])]['values'].get('custom_osr_pilot_current_serial')!=row['current_serial']:raise ValueError('native current serial differs')
        if ('Batch',row.get('batch')) not in records or any(('Serial No',row[k]) not in records for k in ('old_serial','current_serial')):raise ValueError('native serial/batch readback absent')
        identity=row.get('engineering_qa_identity',{});binding=row.get('engineering_qa_binding',{})
        if identity.get('asset_id')!=row['asset_id'] or identity.get('configuration_sha256')!=package['configuration_sha256'] or identity.get('design_revision')!=row['product_revision_sha256']:raise ValueError('native QA must bind the controlled position/revision')
        if len(identity.get('characteristics',[]))!=1 or any(c['part_id']!=row['product_id'] or c['part_revision']!=row['product_revision_sha256'] for c in identity['characteristics']):raise ValueError('native QA product identity differs')
        fields=('project','company','work_order','quality_inspection','material_batch','nonconformance','calibration_record')
        expected=engineering_identity.bind_quality_result(identity,{k:binding.get(k) for k in fields},binding.get('measurement',{}))
        if expected!=binding or binding['engineering_accepted'] is not False or binding['within_defined_limits'] is not None or binding['measurement']['serial']!=row['current_serial'] or binding['material_batch']!=row['batch']:raise ValueError('native QA identity must remain exact and unqualified')
        if any(records[('Serial No',row[k])]['values'].get('item_code')!=row['finished_item'] for k in ('old_serial','current_serial')):raise ValueError('native serial belongs to another finished item')
    # Independently replay the retained immutable business events, including the
    # actual operator UI test/refusal/review sequence, without contacting ERP.
    journal=r.get('operator_ui',{}).get('journal',{});state=contract.initial_state(package);previous='0'*64
    bodies={x['sha256']:x['body'] for x in r.get('evidence_bodies',[])}
    if any(contract.digest(body)!=h for h,body in bodies.items()):raise ValueError('native evidence body digest differs')
    for i,event in enumerate(journal.get('events',[]),1):
        cmd=event['command'];expected=contract.digest(dict(seq=i,command=cmd,previous_sha256=previous))
        if event['seq']!=i or event['previous_sha256']!=previous or event['sha256']!=expected:raise ValueError('native event hash chain changed')
        if cmd['kind'] in {'inspect','test'}:
            name=cmd['data'].get('inspection') or cmd['data'].get('test_record');qa=records.get(('Quality Inspection',name),{})
            status='Accepted' if cmd['data']['result']=='pass' else 'Rejected'
            if qa.get('docstatus')!=1 or qa.get('values',{}).get('status')!=status or qa.get('values',{}).get('inspected_by')!=cmd['actor']:raise ValueError('native QA result/inspector differs from serial journal')
            native=next(x for x in r['products'] if x['asset_id']==cmd['asset_id'])
            reference=native['receipt'] if cmd['kind']=='inspect' else state['articles'][cmd['serial']]['native_records']['manufacture_entry']
            if qa['values'].get('reference_name')!=reference or (cmd['kind']=='test' and qa['values'].get('item_code')!=native['finished_item']):raise ValueError('native QA reference differs from exact article history')
        for h in cmd['evidence']:
            if h in bodies:continue
            if cmd['id'].startswith('ui-') and cmd['kind']=='test':
                body=dict(doctype='Quality Inspection',name=cmd['data']['test_record'],status=records[('Quality Inspection',cmd['data']['test_record'])]['values']['status'])
            elif cmd['id'].startswith('ui-') and cmd['kind']=='handback':
                body=dict(user=cmd['actor'],latest_test=deepcopy(state['positions'][cmd['asset_id']]['last_test']),scope='Software-business review only')
            else:raise ValueError('native journal evidence body absent')
            if contract.digest(body)!=h:raise ValueError('native operator evidence binding differs')
        state=contract.transition(state,cmd,package);previous=expected
    if state!=journal.get('state') or previous!=journal.get('head_sha256') or len(journal.get('events',[]))<60:raise ValueError('native business journal does not replay')
    for row in r['products']:
        pos=state['positions'][row['asset_id']];article=state['articles'][row['current_serial']]
        if pos['serial']!=row['current_serial'] or row['old_serial'] not in pos['removed'] or article['batch']!=row['batch'] or article['revision']!=row['product_revision_sha256']:raise ValueError('native unit identity differs from replayed exact serial history')
    if any(journal.get(k) is not False for k in contract.FLAGS):raise ValueError('native journal authority differs')
    gateway=r.get('gateway',{});pending=gateway.get('outbox_before_restart',[]);delivered=gateway.get('outbox_after_restart',[])
    if gateway.get('outage_observed') is not True or gateway.get('commands_observation_only') is not True or len(pending)<3 or not any(x.get('attempts',0)>0 for x in pending) or len(delivered)<3 or any(x.get('state')!='delivered' for x in delivered):raise ValueError('native persisted outage/restart delivery not demonstrated')
    fault=r.get('fault_recovery',{})
    if fault!={'process_exit_code':86,'native_qi_count':1,'created':True,'retry_created':False,'stage':'after-native-QI-commit-before-journal-dispatch'}:raise ValueError('native commit-to-dispatch process recovery not demonstrated')
    fp=json.loads((raw/'fuxa-project.json').read_bytes())
    if len(fp.get('devices',{}))!=3 or any(t.get('daq',{}).get('enabled') is not False for d in fp['devices'].values() for t in d['tags'].values()):raise ValueError('FUXA must observe current pilot without owning historian')
    for n in ('workbench.png','fuxa.png'):
        if not (raw/n).read_bytes().startswith(b'\x89PNG\r\n\x1a\n'):raise ValueError('native UI screenshot missing')
    return m

def study():
    package=lifecycle_package();simulation=scenario(package)
    try:native=verify_native();status='executed-current';receipt=digest(RAW/'manifest.json')
    except (OSError,ValueError,KeyError):native=None;status='hold';receipt=None
    return dict(schema=SCHEMA,configuration_sha256=package['configuration_sha256'],source_sha256=sources(),simulation=simulation,
        products=package['products'],positions=package['positions'],qa_travellers=qa_travellers(package),
        native=dict(state=status,receipt_sha256=receipt,receipt='engineering/assurance/v052-pilot-lifecycle-native/manifest.json' if native else None),
        digital_scope='Current-maglev draft procurement, native business execution when separately retained, serial inspection/rework, installation, alarm/repair, replacement and independent software-business review. No commissioning or operating authority.',
        unit_procedures=unit_procedures(package)[0],
        physical_gates=['Measured magnetic/thermal maps and qualified cartridge process','Guidebeam materials, prestress, handling and site acceptance','Target controls/timing and integrated protection','Fire/evacuation and independent engineering/authority acceptance'],**FLAGS)

def payloads(result):
    p=lifecycle_package();sup=supervisory_package(p)
    text=['# Current maglev pilot lifecycle','',result['digital_scope'],'',
          'The three pilot positions use the exact controlled product/BOM revisions. Costs remain unquoted; stock transactions are explicit software fixtures.',
          'The journal rejects a late failed inspection/test, stale configuration, wrong role and self review. Replacement keeps the removed serial and original records. A proposed revision reopens business review and test holds.',
          '',f"Native stack evidence: **{result['native']['state']}**. Use `tools/automation/pilot-lifecycle-native.py run` for an isolated disposable campaign and `verify` for retained evidence only.",
          'Native ERPNext owns purchasing, stock, quality, production and Asset Repair. FUXA observes simulated conditions only. The authenticated ERP Workbench exposes serial actions and business evidence.',
          'A business handback never changes physical/manufacturing release or movement authority. Independent physical acceptance remains open.','',
          'Physical gates: '+', '.join(result['physical_gates'])+'.','']
    files={'study.json.gz':gzip.compress(encoded(result),mtime=0),'lifecycle-package.json':encoded(p),'planning-bundle.json':encoded(planning_bundle(p)),
        'supervisory-package.json':encoded(sup),'fuxa-project.json':encoded(fuxa_project(sup)),
        'serial-history.json':encoded(result['simulation']),'qa-travellers.json':encoded(result['qa_travellers']),
        'unit-procedures.json':encoded(result['unit_procedures']),'dimension-schedules.json':encoded(unit_procedures(p)[1]),'README.md':'\n'.join(text).encode()}
    if result['native']['state']=='executed-current':
        verify_native();files.update({'native-workbench.png':(RAW/'workbench.png').read_bytes(),'native-fuxa.png':(RAW/'fuxa.png').read_bytes()})
    return files

def publish(output=OUTPUT):
    output=Path(output);output.mkdir(parents=True,exist_ok=True);result=study();files=payloads(result)
    for n in NATIVE_FILES-set(files):
        if (output/n).exists():(output/n).unlink()
    for n,b in files.items():(output/n).write_bytes(b)
    m=dict(schema=SCHEMA,source_sha256=result['source_sha256'],files_sha256={n:sha256(b).hexdigest() for n,b in files.items()},**FLAGS)
    (output/'manifest.json').write_bytes(encoded(m));return m

def verify(output=OUTPUT):
    output=Path(output);m=json.loads((output/'manifest.json').read_bytes())
    if m.get('schema')!=SCHEMA or m.get('source_sha256')!=sources() or any(m.get(k) is not False for k in FLAGS):raise ValueError('lifecycle packet source/authority differs')
    declared=set(m['files_sha256'])
    if declared not in (FILES,FILES|NATIVE_FILES) or set(x.name for x in output.iterdir())!=declared|{'manifest.json'}:raise ValueError('lifecycle packet coverage differs')
    for n,h in m['files_sha256'].items():
        if (output/n).is_symlink() or digest(output/n)!=h:raise ValueError('lifecycle payload differs')
    r=json.loads(gzip.decompress((output/'study.json.gz').read_bytes()))
    if r!=study() or payloads(r)!={n:(output/n).read_bytes() for n in declared}:raise ValueError('lifecycle derived evidence differs')
    return m

def read_summary(output=OUTPUT):
    verify(output);r=json.loads(gzip.decompress((Path(output)/'study.json.gz').read_bytes()))
    return dict(schema=SCHEMA,configuration_sha256=r['configuration_sha256'],positions=len(r['positions']),products=len(r['products']),
        events=len(r['simulation']['snapshot']['events']),controls=len(r['simulation']['controls']),native=r['native'],physical_gates=r['physical_gates'],
        native_images=sorted(NATIVE_FILES) if r['native']['state']=='executed-current' else [],**FLAGS)
