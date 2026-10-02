import copy
import csv
from datetime import date
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import zipfile

import pytest

from tools.automation import connected_assurance as thread
from tools.automation import subsystem_qualification as qualification


@pytest.fixture
def dossier(tmp_path):
    plan=json.loads((thread.ROOT/qualification.PLAN).read_text())
    paths=set(thread.compile_thread()['source_hashes']) | {qualification.PLAN,plan['rams_input_path'],
                   'engineering/analysis/rams.py','tools/automation/subsystem_qualification.py'}
    for value in paths:
        path=tmp_path/value;path.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(thread.ROOT/value,path)
    return tmp_path,plan


def prepare_run(root,plan, *, origin='synthetic'):
    cfg=next(row for row in thread.compile_thread(root)['nodes'] if row['id']==plan['configuration_id'])
    fingerprint=thread.fingerprint(cfg)
    plan['rig'].update(serial_number='TEST-RIG-001',as_built_configuration_fingerprint=fingerprint)
    plan['rig']['selected_components']={key:'TEST-selected-'+key for key in plan['rig']['selected_components']}
    calibration=root/'test-calibration.json';calibration.write_text('{"test_fixture":true}')
    plan['rig']['calibration_records']=[dict(id='TEST-INSTRUMENT',path='test-calibration.json',sha256=thread.digest(root,'test-calibration.json'),valid_until='2027-01-01',uncertainty_c=.1)]
    path=root/'test-measurements.csv'
    with path.open('w',newline='') as stream:
        writer=csv.DictWriter(stream,fieldnames=qualification.COLUMNS);writer.writeheader()
        for t,temperature,detected,isolation in [(0,30,0,0),(1,30.1,1,0),(2,30.2,1,1),(3,30.3,1,1)]:
            writer.writerow(dict(time_s=t,temperature_c=temperature,ambient_c=50,flow_l_min=0,pressure_kpa=10,fault_active=1,detected=detected,isolation=isolation,derate=isolation))
    test=next(row for row in plan['tests'] if row['id']=='RIG-PUMP')
    test.update(limits=dict(max_temperature_c=40,max_detection_delay_s=1,max_isolation_delay_s=2,max_fault_flow_l_min=0),minimum_duration_s=3,model_error_limit_c=.2,repeat_count=1)
    units=dict(initial_c='degC',ambient_c='degC',heat_w='W',capacity_j_k='J/K',conductance_w_k='W/K',limit_c='degC')
    test['thermal_inputs']={key:dict(low=value,high=value,basis='illustrative-assumption',unit=units[key])
                           for key,value in dict(initial_c=30,ambient_c=50,heat_w=1000,capacity_j_k=10000,conductance_w_k=0,limit_c=40).items()}
    run=dict(id='TEST-RUN-001',test_id='RIG-PUMP',raw_path='test-measurements.csv',raw_sha256=thread.digest(root,'test-measurements.csv'),
             configuration_fingerprint=fingerprint,rig_serial='TEST-RIG-001',specimen_serials={key:'TEST-SERIAL-'+key for key in plan['rig']['selected_components']},
             performed_by='test-operator',performed_at='2026-10-02T10:00:00Z',procedure_revision='draft-A',origin=origin,fault_onset_s=0,
             channel_instruments={key:'TEST-INSTRUMENT' for key in plan['rig']['instrument_channels']})
    run['channel_semantics']={'isolation':'physical-energy-isolated'}
    plan['rig']['specimen_serials']=dict(run['specimen_serials'])
    plan['measurement_runs']=[run]
    return run


def test_repository_package_does_not_claim_real_qualification():
    report=qualification.compile_package()
    assert report['qualification_state']=='qualification-open'
    assert report['accepted_use'] is None and report['release_ready'] is False
    assert set(report['stages'])==set(qualification.STAGES)
    assert all(row['state']=='blocked' for row in report['stages'].values())
    assert report['measurement_results']==[]
    assert report['quantitative_analysis']['fault_tree']['unknown_events']==['EV-CONFIG']


def test_synthetic_measurements_cannot_close_physical_or_model_qualification(dossier):
    root,plan=dossier;prepare_run(root,plan)
    report=qualification.compile_package(root,plan)
    row=report['measurement_results'][0]
    assert row['metrics']['max_detection_delay_s']==1
    assert row['metrics']['max_isolation_delay_s']==2
    assert all(row['criteria'].values())
    assert row['model_maximum_error_c']==pytest.approx(.1)
    assert not row['model_correlation_passed']
    assert any('Synthetic' in value for value in row['blockers'])
    assert report['accepted_use'] is None


def test_current_physical_measurements_are_still_unreviewed(dossier):
    root,plan=dossier;prepare_run(root,plan,origin='physical')
    report=qualification.compile_package(root,plan)
    assert report['measurement_results'][0]['state']=='measured-unreviewed'
    assert report['measurement_results'][0]['model_correlation_passed']
    assert report['stages']['independent_review']['state']=='blocked'
    assert report['qualification_state']=='qualification-open'


@pytest.mark.parametrize('mutation,match',[
    (lambda root,plan,run:(root/'test-measurements.csv').write_text('changed'),'raw measurement hash changed'),
    (lambda root,plan,run:plan['model_validation'].update(calibration_run_ids=[run['id']],validation_run_ids=[run['id']]),'must be separate'),
    (lambda root,plan,run:run.update(raw_path='../outside'),'repository-relative'),
    (lambda root,plan,run:run.update(performed_at='2026-10-02T10:00:00'),'timezone'),
    (lambda root,plan,run:plan['tests'][1].update(repeat_count=True),'positive integer'),
])
def test_invalid_measurement_and_validation_provenance_fails_closed(dossier,mutation,match):
    root,plan=dossier;run=prepare_run(root,plan)
    mutation(root,plan,run)
    with pytest.raises(ValueError,match=match):qualification.compile_package(root,plan)


def test_changed_config_calibration_and_unobserved_response_stay_blocked(dossier):
    root,plan=dossier;run=prepare_run(root,plan,origin='physical')
    run['configuration_fingerprint']='0'*64
    plan['rig']['calibration_records'][0]['valid_until']='2025-01-01'
    rows=list(csv.DictReader((root/'test-measurements.csv').open()))
    for row in rows:row['isolation']='0'
    with (root/'test-measurements.csv').open('w',newline='') as stream:
        writer=csv.DictWriter(stream,fieldnames=qualification.COLUMNS);writer.writeheader();writer.writerows(rows)
    run['raw_sha256']=thread.digest(root,run['raw_path'])
    report=qualification.compile_package(root,plan)
    row=report['measurement_results'][0]
    assert row['metrics']['max_isolation_delay_s'] is None
    assert row['criteria']['max_isolation_delay_s'] is None
    assert any('configuration' in value for value in row['blockers'])
    assert any('expired' in value for value in row['blockers'])
    assert not row['model_correlation_passed']


def test_corrupted_or_nonfinite_csv_cannot_be_measurement_evidence(dossier):
    root,plan=dossier;run=prepare_run(root,plan)
    path=root/'test-measurements.csv'
    path.write_text(path.read_text().replace('30.1','nan'))
    run['raw_sha256']=thread.digest(root,run['raw_path'])
    with pytest.raises(ValueError,match='finite'):qualification.compile_package(root,plan)


def test_changed_specimen_and_partial_integration_remain_blocked(dossier):
    root,plan=dossier;run=prepare_run(root,plan,origin='physical')
    run['specimen_serials']['OSR-COOL-PUMP']='REPLACED-PUMP'
    plan['integration_evidence']=[dict(id='TEST-HIL',path=run['raw_path'],sha256=run['raw_sha256'],
         configuration_fingerprint=run['configuration_fingerprint'],review_reference='TEST-review',kind='hil')]
    report=qualification.compile_package(root,plan)
    assert any('specimen serials differ' in gap for gap in report['measurement_results'][0]['blockers'])
    assert not report['measurement_results'][0]['model_correlation_passed']
    assert report['stages']['integration']['blockers']==[
        'infrastructure: integration evidence absent.', 'operations: integration evidence absent.', 'vehicle: integration evidence absent.']


def test_production_process_change_and_open_ncr_require_requalification(dossier):
    root,plan=dossier
    path=root/'test-production.json';path.write_text('{"synthetic":true}')
    plan['production_batches']=[dict(id='TEST-BATCH',serials=['TEST-002','TEST-020','TEST-200'],supplier_batches=['TEST-SUPPLIER'],
          operation_revision='changed-process',configuration_fingerprint='old',characteristic_results={},raw_path='test-production.json',raw_sha256=thread.digest(root,'test-production.json'))]
    plan['nonconformances']=[dict(id='TEST-NCR',affected_serials=['TEST-020'],disposition='open',requalification='open')]
    report=qualification.compile_package(root,plan)
    assert any('design/process change' in value for value in report['manufacturing_blockers'])
    assert any('TEST-NCR' in value for value in report['manufacturing_blockers'])
    assert any('TEST-200' in value for value in report['manufacturing_blockers'])


def test_readiness_does_not_bind_reference_or_other_city_acceptance():
    report=qualification.compile_package()
    result=qualification.scoped_readiness(report,'mosul','physical','MOS-TRAIN-001')
    assert result['deployment_state']=='no-deployment-qualification-package'
    assert result['deployment_accepted_use'] is None
    other=copy.deepcopy(report);other['scope']=dict(kind='deployment',city='samawah',environment='physical')
    other['accepted_use']='TEST acceptance for another city'
    assert qualification.scoped_readiness(other,'mosul','physical')['reference_package'] is None
    with pytest.raises(ValueError,match='context'):qualification.scoped_readiness(report,'../other','physical')


def test_dossier_contains_original_hash_bound_inputs_and_no_release(dossier):
    root,plan=dossier;report=qualification.compile_package(root,plan)
    output=root/'package.zip';qualification.export_dossier(root,report,output)
    with zipfile.ZipFile(output) as archive:
        manifest=json.loads(archive.read('manifest.json'))
        assert manifest['release_ready'] is False
        for path,digest in manifest['source_hashes'].items():
            assert hashlib.sha256(archive.read('inputs/'+path)).hexdigest()==digest
    (root/plan['rams_input_path']).write_text('changed')
    with pytest.raises(ValueError,match='changed during export'):qualification.export_dossier(root,report,output)


def test_signed_reviews_require_trusted_role_independence_and_exact_baseline(tmp_path):
    private=tmp_path/'private.pem';public=tmp_path/'public.pem'
    subprocess.run(['openssl','genpkey','-algorithm','ED25519','-out',str(private)],check=True,capture_output=True)
    subprocess.run(['openssl','pkey','-in',str(private),'-pubout','-out',str(public)],check=True,capture_output=True)
    policy=tmp_path/'policy.json';policy.write_text(json.dumps({'reviewers':{'test-reviewer':dict(enabled=True,roles=['assessor'],public_key='public.pem',public_key_sha256=hashlib.sha256(public.read_bytes()).hexdigest())}}))
    envelope=dict(schema='osr-subsystem-review/1',reviewer='test-reviewer',role='assessor',disposition='accepted',reference='TEST-review',
                  valid_until='2027-01-01',evidence_fingerprint='evidence-A',configuration_fingerprint='configuration-A')
    file=tmp_path/'envelope.json';file.write_text(json.dumps(envelope));signature=tmp_path/'signature.bin'
    subprocess.run(['openssl','pkeyutl','-sign','-inkey',str(private),'-rawin','-in',str(file),'-out',str(signature)],check=True,capture_output=True)
    records=[dict(envelope_path='envelope.json',signature_path='signature.bin')]
    verify=lambda ev,authors=set():qualification.authenticated_reviews(tmp_path,records,policy,ev,'configuration-A',authors,date(2026,10,2))
    assert len(verify('evidence-A')[0])==1
    assert not verify('changed')[0]
    assert not verify('evidence-A',{'test-reviewer'})[0]
    envelope['reference']='changed after signing';file.write_text(json.dumps(envelope))
    assert not verify('evidence-A')[0]


def test_generated_readiness_is_deterministic():
    assert qualification.compile_package()==qualification.compile_package()
