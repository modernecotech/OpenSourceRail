"""Actual journal transactions and failures, not assertions of physical approval."""
from copy import deepcopy
import gzip
import json
import sqlite3
from pathlib import Path
import pytest
from engineering.ferrite_maglev import pilot_lifecycle as p


@pytest.fixture(scope='module')
def package():return p.lifecycle_package()

@pytest.fixture(scope='module')
def scenario(package):return p.scenario(package)

def test_current_three_products_and_retained_erp_adapter(package):
    assert {r['product_id'] for r in package['products']}=={'OSR-PILOT-MAGNETIC-CARTRIDGE','OSR-PILOT-GUIDEBEAM-25M','OSR-PILOT-LAUNCH-CASSETTE-2P5M'}
    assert len(package['positions'])==3
    bundle=p.planning_bundle(package);plan=p.planning.make_plan(bundle);p.planning.validate_plan(plan)
    assert len(plan['records'])==6
    assert all(x['configuration_sha256']==package['configuration_sha256'] for x in bundle['manufacturing_tasks'])
    assert all(x['release']=='draft-unqualified' for x in package['products'])

def test_history_replacement_and_no_physical_credit(scenario):
    s=scenario['snapshot'];assert len(s['events'])==69
    assert all(s[k] is False for k in p.contract.FLAGS)
    for pos in s['state']['positions'].values():
        assert pos['serial'].endswith('-NEW') and len(pos['removed'])==1 and pos['removed'][0].endswith('-OLD')
        assert pos['revision_hold'] and pos['handback']=='hold'
        assert s['state']['articles'][pos['removed'][0]]['stage']=='removed'
    assert len(scenario['controls'])==21
    assert all(c['result'] in {'rejected-without-history-change','committed-history-replayed'} for c in scenario['controls'])

def test_latest_inspection_and_test_failures_have_real_negative_controls(scenario):
    ids={c['id'] for c in scenario['controls']}
    for pos in p.load()['positions']:
        assert all(pos['asset_id']+'/'+suffix in ids for suffix in ('later-inspection-failure','later-test-failure','self-review','stale-revision','wrong-role','changed-revision-handback','restart'))

def test_durable_retry_and_changed_duplicate_refusal(package,tmp_path):
    ledger=p.contract.Ledger(tmp_path/'journal.sqlite',package);pos=package['positions'][0]
    c=p.command(package,pos,'SIM-ONE','purchase',1,dict(draft_material_request='SIM-MR',draft_purchase_order='SIM-PO',bom_sha256='a'*64))
    assert ledger.append(c,expected_head='0'*64)['created']
    restarted=p.contract.Ledger(tmp_path/'journal.sqlite',package)
    assert not restarted.append(c)['created']
    changed=deepcopy(c);changed['actor']='different-actor'
    with pytest.raises(ValueError,match='identity reused'):restarted.append(changed)
    assert len(restarted.snapshot()['events'])==1
    next_command=p.command(package,pos,'SIM-ONE','receive',2,dict(receipt='SIM-PR'))
    with pytest.raises(ValueError,match='stale lifecycle'):restarted.append(next_command,expected_head='0'*64)
    assert len(restarted.snapshot()['events'])==1

def test_rejected_write_rolls_back_and_history_is_immutable(package,tmp_path):
    ledger=p.contract.Ledger(tmp_path/'j.sqlite',package);pos=package['positions'][0]
    c=p.command(package,pos,'SIM-UNIT','purchase',1,dict(draft_material_request='SIM-MR',draft_purchase_order='SIM-PO',bom_sha256='a'*64));ledger.append(c)
    before=ledger.snapshot();bad=p.command(package,pos,'SIM-UNIT','assemble',2,dict(work_order='SIM-WO',manufacture_entry='SIM-SE'))
    with pytest.raises(ValueError):ledger.append(bad)
    assert ledger.snapshot()==before
    with ledger.connect() as db:
        with pytest.raises(sqlite3.IntegrityError,match='immutable'):db.execute('DELETE FROM events')
        with pytest.raises(sqlite3.IntegrityError,match='immutable'):db.execute('UPDATE events SET body="{}"')

def test_changed_configuration_cannot_overwrite_old_serial_ledger(package,tmp_path):
    p.contract.Ledger(tmp_path/'j.sqlite',package);changed=deepcopy(package);changed['configuration_sha256']='f'*64
    changed['sha256']=p.contract.digest({k:v for k,v in changed.items() if k!='sha256'})
    with pytest.raises(ValueError,match='cannot overwrite'):p.contract.Ledger(tmp_path/'j.sqlite',changed)

def test_alarm_cannot_be_bypassed_with_a_new_pass_and_review(package,scenario):
    state=p.contract.initial_state(package);events=scenario['snapshot']['events'];alarm=None
    for event in events:
        state=p.contract.transition(state,event['command'],package)
        if event['command']['kind']=='alarm':alarm=event['command'];break
    pos=next(x for x in package['positions'] if x['asset_id']==alarm['asset_id'])
    test=p.command(package,pos,alarm['serial'],'test',901,dict(result='pass',test_record='SIM-BYPASS'))
    state=p.contract.transition(state,test,package)
    review=p.command(package,pos,alarm['serial'],'handback',902,dict(test_id=test['id'],review_record='SIM-NO-REPAIR'))
    with pytest.raises(ValueError,match='latest passing'):p.contract.transition(state,review,package)
    assert state['positions'][alarm['asset_id']]['replacement_required']

@pytest.mark.parametrize('flag',list(p.contract.FLAGS))
def test_no_self_asserted_release(package,flag):
    changed=deepcopy(package);changed[flag]=True;changed['sha256']=p.contract.digest({k:v for k,v in changed.items() if k!='sha256'})
    with pytest.raises(ValueError,match='cannot release'):p.contract.validate_package(changed)

def test_supervision_uses_current_components_and_no_commands(package):
    sup=p.supervisory_package(package);p.supervisory.validate_package(sup)
    assert sup['environment']=='simulation' and len(sup['equipment'])==3
    assert {e['component_type_id'] for e in sup['equipment']}=={r['product_id'] for r in package['products']}
    assert all(not e['commands'] for e in sup['equipment'])
    assert all(e['measurements']['condition_code']['unit']=='simulation-code' for e in sup['equipment'])
    project=p.fuxa.project([sup]);assert project['hmi']['views']

def test_serial_qa_is_bound_but_unqualified(package):
    rows=p.qa_travellers(package);assert len(rows)==3
    for row in rows:
        binding=row['binding'];assert binding['engineering_accepted'] is False and binding['within_defined_limits'] is None
        assert row['physical_test_executed'] is False
        identity=row['identity'];measurement=deepcopy(binding['measurement']);measurement['serial']='SIM-WRONG'
        native={k:binding[k] for k in ('project','company','work_order','quality_inspection','material_batch','nonconformance','calibration_record')}
        with pytest.raises(ValueError,match='serial/batch'):p.engineering_identity.bind_quality_result(identity,native,measurement)

def test_all_kits_have_actionable_unexecuted_procedures_and_exact_quantities(package):
    rows,dimensions=p.unit_procedures(package)
    assert len(rows)==len(dimensions)==3
    for row in rows:
        product=next(x for x in package['products'] if x['product_id']==row['product_id'])
        assert len(row['assembly_steps'])>=7 and len(row['inspection_plan'])==6 and row['open_approval_holds']
        assert row['manufacturing_release'] is row['physical_release'] is False
        assert all(x['qualified_limits'] is None and x['state']=='unexecuted-hold' for x in row['inspection_plan'])
        assert [(x['quantity'],x['unit'])for x in row['procurement']]==[(x['source']['quantity'],x['source']['unit'])for x in product['bom']]
        assert all(x['supplier_quote'] is None and x['purchase_release'] is False for x in row['procurement'])
    assert all(x['parts'] and x['tolerance_values'] is None for x in dimensions)

def test_portable_packet_rehash_tampering_cannot_close_release(tmp_path):
    out=tmp_path/'packet';p.publish(out);p.verify(out)
    value=json.loads(gzip.decompress((out/'study.json.gz').read_bytes()));value['physical_release']=True
    (out/'study.json.gz').write_bytes(gzip.compress(p.encoded(value),mtime=0))
    m=json.loads((out/'manifest.json').read_bytes());m['files_sha256']['study.json.gz']=p.digest(out/'study.json.gz');(out/'manifest.json').write_bytes(p.encoded(m))
    with pytest.raises(ValueError,match='derived evidence'):p.verify(out)

def test_source_set_includes_native_execution_and_ui_inputs():
    paths={x.relative_to(p.ROOT).as_posix() for x in p.source_paths()}
    assert {'tools/automation/pilot-lifecycle-native.py','deployment/erpnext/compose.yaml','deployment/supervision/Dockerfile',
        'deployment/erpnext/apps/osr_erpnext/osr_erpnext/maglev_pilot.py',
        'deployment/erpnext/apps/osr_erpnext/osr_erpnext/www/maglev-pilot.html'}<=paths

def test_native_retained_receipt_when_published():
    # The delivery-lifecycle profile first runs the mandatory native `verify`.
    # Host unit development remains possible before the explicit heavy campaign.
    if (p.RAW/'manifest.json').exists():p.verify_native()

@pytest.mark.parametrize('mutation',['product-position','batch','qa-configuration','serial-item'])
def test_resealed_native_identity_mismatch_refused(tmp_path,mutation):
    # These run against the actual current Docker campaign, never an invented
    # native-positive fixture. The mandatory profile runs native verify first.
    if not (p.RAW/'manifest.json').exists():pytest.skip('explicit native campaign has not yet been published')
    import shutil
    out=tmp_path/'native';shutil.copytree(p.RAW,out);r=json.loads((out/'native-result.json').read_bytes());row=r['products'][0]
    if mutation=='product-position':
        row['product_id']=r['products'][1]['product_id'];row['product_revision_sha256']=r['products'][1]['product_revision_sha256']
    elif mutation=='batch':row['batch']=r['products'][1]['batch']
    elif mutation=='qa-configuration':
        row['engineering_qa_identity']['configuration_sha256']='a'*64
        row['engineering_qa_identity']['sha256']=p.engineering_identity.digest({k:v for k,v in row['engineering_qa_identity'].items() if k!='sha256'})
    else:
        next(x for x in r['native_documents'] if x['doctype']=='Serial No' and x['name']==row['current_serial'])['values']['item_code']='SIM-OTHER-ITEM'
    (out/'native-result.json').write_bytes(p.encoded(r));m=json.loads((out/'manifest.json').read_bytes());m['files_sha256']['native-result.json']=p.digest(out/'native-result.json');(out/'manifest.json').write_bytes(p.encoded(m))
    with pytest.raises(ValueError):p.verify_native(out)
