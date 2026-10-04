"""Adversarial evidence, fixed holds, funding stops and section cash identities."""
import csv
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

import pytest

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'tools/automation'))
from baghdad_delivery_stress import production_duration
from baghdad_qualification import verify_result, fingerprint

CITY=ROOT/'cities/catalogue/west-asia/Iraq/Baghdad'
OUT=CITY/'engineering/qualification'


def data(name):return json.loads((OUT/name).read_text())


def test_shift_does_not_compress_fixed_holds_or_qualification():
    stage=dict(cycle_working_days=10)
    assert production_duration(stage,.85,1,6)==12
    assert production_duration(stage,.75,1,6)==14
    assert production_duration(stage,.75,1.5,6)==12
    assert production_duration(stage,.75,100,6)==7
    with pytest.raises(ValueError):production_duration(stage,.75,1.5,11)
    with pytest.raises(ValueError):production_duration(stage,.75,0,6)
    report=json.loads((CITY/'engineering/delivery-risk/summary.json').read_text())
    ledger=list(csv.DictReader((CITY/'engineering/delivery-risk/calendar_baseline-monthly-finance.csv').open()))
    expected=sum(((float(row['revenue_iqd'])-float(row['opex_iqd']))/1300-float(row['capex_usd']))/1.134**(int(row['month'])/12) for row in ledger)
    assert report['cases']['calendar_baseline']['metrics']['unlevered_project_npv_usd']==pytest.approx(expected,abs=.02)
    rows=list(csv.DictReader((CITY/'engineering/delivery-risk/availability_75pct_all_stage_shifts-schedule.csv').open()))
    prototype=min((r for r in rows if r['asset_type']=='rolling-stock'),key=lambda r:int(r['start_hour']))['asset_id']
    acceptance=next(r for r in rows if r['asset_id']==prototype and r['manufacturing_uid'].endswith('rs-50-dynamic-commissioning'))
    assert int(acceptance['end_hour'])-int(acceptance['start_hour']) >= 60*8


def test_facility_quantities_and_costs_fit_existing_allowance():
    f=data('temporary-facility.json')
    assert len(f['cells'])==6
    assert f['process_floor_m2']==4960
    assert f['total_floor_m2']==6696
    assert f['site_m2']==16740
    assert sum(r['reference_total_usd'] for r in f['rfqs'])==pytest.approx(f['priced_subtotal_usd'])
    assert f['allocated_direct_usd']+f['unallocated_allowance_usd']==35e6
    assert f['existing_direct_allowance_usd']+f['epc_usd']==37.45e6
    assert not f['accepted'] and not any(r['quotation_received'] for r in f['rfqs'])


def test_funding_stop_moves_invoices_and_does_not_create_refusal_replacement():
    gates=data('funding-gates.json')['cases']
    assert all(g['refused_native']>0 for g in gates)
    for g in gates:
        rows=list(csv.DictReader((OUT/(g['case']+'-placement-monthly.csv')).open()))
        assert sum(float(r['refused_source_native']) for r in rows)==pytest.approx(g['refused_native'])
        if g['permanent_refusal_blocks_programme']:
            assert g['first_opening_month'] is None
            assert not any(float(r['replacement_placement_required_native']) for r in rows)
        else:
            assert sum(float(r['replacement_placement_required_native']) for r in rows)==pytest.approx(g['refused_native'])
    risk=json.loads((CITY/'engineering/delivery-risk/summary.json').read_text())
    for name,left,right in [('domestic_placement_interrupted_recovered',29,35),('export_credit_delayed_recovered',0,6)]:
        case=risk['cases'][name];s=case['settings']
        assert case['metrics']['funding_restart_capital_usd']==10.7e6
        assert case['metrics']['government_capital_share']==pytest.approx(.25)
        six=list(csv.DictReader((CITY/'engineering/delivery-risk'/(name+'-six-month-finance.csv')).open()))
        assert sum(float(r['capex_usd']) for r in six)==pytest.approx(case['metrics']['total_capital_usd'])
        # Independent invoice projection: all withheld-month uses deferred.
        from baghdad_delivery_stress import finance, schedule
        # Published monthly files cover these cases for direct audit.
        cash=list(csv.DictReader((CITY/'engineering/delivery-risk'/(name+'-monthly-finance.csv')).open()))
        assert all(float(r['capex_usd'])==0 for r in cash if left<=int(r['month'])<right)
        assert all(float(r['chinese_export_credit_draw_native'])==0 and float(r['domestic_bonds_draw_native'])==0 for r in cash if left<=int(r['month'])<right)


def test_section_is_complete_on_its_own_and_does_not_buy_another_fleet():
    s=data('first-section.json')
    assert len(s['station_ids'])==5 and s['station_ids'][0].endswith('s000000')
    assert s['station_ids'][-1].endswith('s014034')
    assert s['total_trainsets']==s['peak_trains']+s['spare_trains']+s['cold_reserve']==16
    assert len(set(s['allocated_existing_trainsets']))==16
    assert s['ultimate_city_trainsets']==current_fleet()
    assert s['terminal_berths_per_end']==2
    assert s['terminal_grid_kw_per_end']==4000
    assert s['round_trip_charge_delivered_kwh']>s['round_trip_energy_kwh']
    assert s['nameplate_battery_kwh']==1350 and s['usable_battery_kwh']==1080
    assert s['usable_soc_window_kwh']==648
    assert s['round_trip_energy_kwh']/2 <= s['usable_soc_window_kwh']
    assert s['round_trip_charging_margin_fraction']<.025
    assert s['degraded_charge_margin_fraction']<0 and not s['degraded_charge_qualified']
    assert s['conditional_opening_month']<s['full_line_opening_month']==next(p['opening_month'] for p in json.loads((CITY/'engineering/delivery-risk/summary.json').read_text())['cases']['calendar_baseline']['phases'] if p['line']==s['line'])
    assert s['extra_capital_with_epc_usd']==29.96e6
    rows=list(csv.DictReader((OUT/'first-section-monthly-finance.csv').open()))
    assert all(float(r['fare_receipts_iqd'])==0 for r in rows if int(r['month'])<s['conditional_opening_month'])
    metrics=s['metrics']
    assert metrics['government_capital_share']==pytest.approx(.25)
    assert metrics['maximum_cash_residual_usd']<.02
    assert metrics['maximum_principal_balance_residual_usd']<.02
    assert sum(float(r['capex_usd']) for r in rows)==pytest.approx(metrics['total_capital_usd'])
    assert metrics['total_capital_usd']==pytest.approx(json.loads((CITY.parent/'finance/baghdad-programme.json').read_text())['total_capex_usd']+s['extra_capital_with_epc_usd'])
    # Allocated stock and advanced civil are still serialised in frozen lanes.
    from collections import defaultdict
    lanes=defaultdict(list)
    for r in csv.DictReader((OUT/'first-section-schedule.csv').open()):
        lanes[r['resource_pool'],r['resource_lane']].append((int(r['start_hour']),int(r['end_hour'])))
    for intervals in lanes.values():
        ordered=sorted(intervals)
        assert all(a[1]<=b[0] for a,b in zip(ordered,ordered[1:]))


def test_all_evidence_rows_have_erp_subjects_and_pending_actual_results():
    packages=data('evidence-work-packages.json')['work_packages']
    assert len(packages)==10
    register=list(csv.DictReader((CITY/'engineering/delivery-risk/qualification-register.csv').open()))
    assert {r['work_package_id'] for r in register}=={r['id'] for r in packages[:9]}
    tasks=data('erpnext-tasks.json')['tasks']
    assert {t['subject'] for t in tasks}=={p['erpnext_subject'] for p in packages}
    for p in packages:
        assert p['status']=='not-demonstrated' and p['result'] is None and p['accountable_owner_identity'] is None
        template=data(p['evidence_result_template'])
        assert template['status']=='not-executed'
        assert all(m['value'] is None for m in template['measurements'].values())
    report=data('summary.json')
    for rel,digest in report['sources_sha256'].items():assert hashlib.sha256((ROOT/rel).read_bytes()).hexdigest()==digest
    for rel,digest in report['outputs_sha256'].items():assert hashlib.sha256((OUT/rel).read_bytes()).hexdigest()==digest
    f=data('feasibility.json')
    assert f['additional_real_reference_annual_external_benefit_threshold_usd']*f['external_benefit_pv_factor']==pytest.approx(-f['unlevered_financial_npv_usd'])


@pytest.fixture
def signed_result(tmp_path):
    source=tmp_path/'source.txt';source.write_text('reviewed source')
    raw=tmp_path/'raw.csv';raw.write_text('measured\n4\n')
    package=dict(id='TEST-WP',source_revision='sha256:TEST-REV',sources_sha256={'source.txt':hashlib.sha256(source.read_bytes()).hexdigest()},required_reviewer_role='assessor',criteria=[dict(id='cycle',operator='le',target=5,unit='hour')])
    package['acceptance_criteria_sha256']=fingerprint(package['criteria'])
    result=dict(acceptance_criteria_sha256=package['acceptance_criteria_sha256'],work_package_id='TEST-WP',source_revision=package['source_revision'],status='passed',executed_by='test-measurer',accountable_owner_identity='test-owner',acquired_at='2026-01-01T12:00:00+00:00',raw_evidence_sha256={'raw.csv':hashlib.sha256(raw.read_bytes()).hexdigest()},measurements={'cycle':dict(value=4,unit='hour')})
    result_path=tmp_path/'result.json';result_path.write_text(json.dumps(result))
    private=tmp_path/'private.pem';public=tmp_path/'public.pem'
    subprocess.run(['openssl','genpkey','-algorithm','ED25519','-out',str(private)],check=True,capture_output=True)
    subprocess.run(['openssl','pkey','-in',str(private),'-pubout','-out',str(public)],check=True,capture_output=True)
    policy=tmp_path/'policy.json';policy.write_text(json.dumps({'reviewers':{'test-assessor':dict(enabled=True,roles=['assessor'],public_key='public.pem',public_key_sha256=hashlib.sha256(public.read_bytes()).hexdigest())}}))
    envelope=tmp_path/'envelope.json'
    review=dict(schema='osr-subsystem-review/1',reviewer='test-assessor',role='assessor',disposition='accepted',reference='TEST-ONLY',valid_until='2099-01-01',evidence_fingerprint=hashlib.sha256(result_path.read_bytes()).hexdigest(),configuration_fingerprint=package['source_revision'])
    envelope.write_text(json.dumps(review));signature=tmp_path/'signature.bin'
    subprocess.run(['openssl','pkeyutl','-sign','-inkey',str(private),'-rawin','-in',str(envelope),'-out',str(signature)],check=True,capture_output=True)
    return package,result,result_path,dict(envelope_path='envelope.json',signature_path='signature.bin'),policy,tmp_path


def test_only_authorized_source_bound_measured_signed_result_is_accepted(signed_result):
    p,r,path,review,policy,root=signed_result
    accepted=verify_result(p,path,review,policy,root)
    assert accepted['authenticated'] and not accepted['operational_release']
    (root/'source.txt').write_text('changed source')
    with pytest.raises(ValueError,match='Stale'):verify_result(p,path,review,policy,root)


@pytest.mark.parametrize('mutation',['unsigned','unauthorized','self_review','raw_changed','missing_measurement','bad_unit','over_limit','null_value','stale_revision','future_time','changed_criteria'])
def test_bad_measurement_or_review_fails_closed(signed_result,mutation):
    p,r,path,review,policy,root=signed_result
    if mutation=='unsigned':(root/'signature.bin').write_bytes(b'fake signature')
    elif mutation=='unauthorized':policy.write_text('{"reviewers":{}}')
    elif mutation=='self_review':r['executed_by']='test-assessor'
    elif mutation=='raw_changed':(root/'raw.csv').write_text('different')
    elif mutation=='missing_measurement':r['measurements']={}
    elif mutation=='bad_unit':r['measurements']['cycle']['unit']='day'
    elif mutation=='over_limit':r['measurements']['cycle']['value']=6
    elif mutation=='null_value':r['measurements']['cycle']['value']=None
    elif mutation=='stale_revision':r['source_revision']='old'
    elif mutation=='future_time':r['acquired_at']='2099-01-01T00:00:00+00:00'
    elif mutation=='changed_criteria':p['criteria'][0]['target']=100
    path.write_text(json.dumps(r))
    if mutation=='self_review':
        envelope=root/'envelope.json';decision=json.loads(envelope.read_text());decision['evidence_fingerprint']=hashlib.sha256(path.read_bytes()).hexdigest();envelope.write_text(json.dumps(decision))
        subprocess.run(['openssl','pkeyutl','-sign','-inkey',str(root/'private.pem'),'-rawin','-in',str(envelope),'-out',str(root/'signature.bin')],check=True,capture_output=True)
    with pytest.raises(ValueError):verify_result(p,path,review,policy,root)


def test_erp_refresh_preserves_owner_status_and_task_identity():
    spec=importlib.util.spec_from_file_location('qualification_import',ROOT/'deployment/erpnext/apps/osr_erpnext/osr_erpnext/qualification.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    class Doc:
        name='TASK-TEST';status='Completed';owner='actual-user';description='old'
        def save(self):self.saved=True
    doc=Doc()
    class Frappe:
        def get_all(self,*args,**kwargs):return ['TASK-TEST']
        def get_doc(self,*args,**kwargs):return doc
    payload=dict(doctype='Task',status='draft-import-package-not-live-records',tasks=[dict(subject='BAG-EVID-001 — Test',status='Open',priority='High',description='new')])
    preview=module.reconcile_tasks(Frappe(),payload)
    assert not preview['applied'] and doc.description=='old'
    applied=module.reconcile_tasks(Frappe(),payload,True)
    assert applied['tasks'][0]['task']=='TASK-TEST'
    assert doc.description=='new' and doc.status=='Completed' and doc.owner=='actual-user'


def current_design():
    import tomllib
    return tomllib.loads((ROOT/'cities/catalogue/west-asia/Iraq/Baghdad/design.toml').read_text())

def current_fleet():
    return sum(r['trainset_count'] for r in current_design()['fleets'])
