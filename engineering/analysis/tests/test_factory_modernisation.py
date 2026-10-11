"""Design-to-production identity, datum, energy, quality and interlock checks."""
from copy import deepcopy
import hashlib
import csv
import json
import math
from pathlib import Path
import subprocess
import sys
import numpy as np
import pytest
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT),str(ROOT/'design/component-catalogue/src')]
from engineering.civil_exploration.variant_compiler import compile_variant
from engineering.industrialisation.expansion import build_package
from engineering.industrialisation.assembly import fixture_constraints,tolerance_stack,schedule
from engineering.industrialisation.materials import panel_screen,thermal_layers,train_energy
from engineering.industrialisation.quality import measurement_decision,assess_measurement,torque_trace,process_statistics,material_lot
from engineering.industrialisation.production import process_window,traveler_template,assess_traveler
from engineering.industrialisation.commissioning import CommissioningContract,reference_signals,HEALTH,fault_campaign


@pytest.fixture(scope='module')
def package():
    variant=compile_variant();return build_package(variant['model'],variant['battery'])


def evidence(tmp_path,kind='measurement',name=None):
    path=tmp_path/(name or kind+'.json');path.write_text(json.dumps(dict(kind=kind,basis='synthetic unit-test fixture; no production authority')))
    return dict(path=path.name,sha256=hashlib.sha256(path.read_bytes()).hexdigest(),kind=kind,revision='TEST-1',approved_by='fixture-reviewer')


def calibrated(tmp_path,unit='mm'):
    return dict(tool_id='fixture-tool',unit=unit,valid_from='2026-10-01T00:00:00Z',valid_until='2026-10-31T23:59:59Z',
                minimum=0.,maximum=100.,artifact=evidence(tmp_path,'calibration'))


def test_programme_covers_existing_parts_factory_controls_and_all_six_work_packages(package):
    r=package['review']
    assert {w['id'] for w in r['work_packages']}=={f'IM-0{i}' for i in range(1,7)}
    assert all(w['deliverable'] in package for w in r['work_packages'])
    assert r['material_passport_count']==r['process_route_count']==117
    assert r['assembly_operation_count']==756 and r['existing_first_article_characteristic_count']==416
    assert r['factory_package_count']==16 and r['existing_manufacturing_control_count']==10
    assert package['production_package']['family_transfer_review_required']
    assert package['production_package']['topology_validated'] and not r['blank_traveler_ready_for_review']
    assert all(p['released_grade'] is None and not p['material_accepted'] for p in package['material_passports'])
    assert not r['production_released'] and not r['physical_validation']


def test_fixture_has_six_independent_restraints_and_bad_locator_layout_is_rejected(package):
    f=package['assembly_package'];r=fixture_constraints(f['locator_points_m'],f['locator_normals'])
    assert r['constraint_rank']==6 and not r['fixture_released']
    normals=[[0.,0.,1.]]*6
    assert fixture_constraints(f['locator_points_m'],normals)['constraint_rank']<6
    with pytest.raises(ValueError):fixture_constraints(f['locator_points_m'],[[0.,0.,2.]]*6)
    with pytest.raises(ValueError):fixture_constraints([[True,0,0]]*6,normals)


def test_signed_tolerance_stack_uses_bounds_and_separate_declared_uncertainty():
    terms=[dict(id='opening',nominal_m=.010,tolerance_m=.001,coefficient=1.,standard_uncertainty_m=.0001,thermal_offset_m=.0002),
           dict(id='insert',nominal_m=.008,tolerance_m=.0005,coefficient=-1.,standard_uncertainty_m=.0002,thermal_offset_m=0.)]
    r=tolerance_stack(terms,.001,.004,independent_uncertainties=True)
    assert r['nominal_m']==pytest.approx(.0022) and r['worst_case_interval_m']==pytest.approx([.0007,.0037])
    assert not r['within_declared_clearance'] and r['rss_standard_uncertainty_m']==pytest.approx(math.sqrt(5e-8))
    assert tolerance_stack(terms,None,None)['within_declared_clearance'] is None
    assert tolerance_stack(terms,.001,.004)['rss_standard_uncertainty_m'] is None


def test_resource_schedule_respects_capacity_predecessors_and_dry_wait():
    ops=[dict(id='a',predecessors=[],resource='cell',duration_minutes=10.,minimum_wait_minutes=0.),
         dict(id='b',predecessors=[],resource='cell',duration_minutes=10.,minimum_wait_minutes=0.),
         dict(id='inspect',predecessors=['a','b'],resource='quality',duration_minutes=2.,minimum_wait_minutes=30.)]
    r=schedule(ops,dict(cell=1,quality=1));rows={o['id']:o for o in r['operations']}
    assert rows['b']['start_minutes']>=rows['a']['finish_minutes'] and rows['inspect']['start_minutes']==50.
    assert schedule(ops,dict(cell=2,quality=1))['makespan_minutes']==42.
    assert not r['production_forecast_qualified']
    ops[0]['predecessors']=['inspect']
    with pytest.raises(ValueError,match='cyclic'):schedule(ops,dict(cell=1,quality=1))


@pytest.mark.parametrize('value,uncertainty,status',[(10.,.1,'within-guarded-limits'),(10.95,.1,'uncertainty-overlaps-limit'),(11.3,.1,'outside-limits')])
def test_uncertainty_decision_does_not_pass_a_nominal_value_overlapping_a_limit(value,uncertainty,status):
    assert measurement_decision(value,uncertainty,9.,11.)['status']==status
    assert measurement_decision(value,uncertainty,None,None)['status']=='open-limits'


def measurement_fixture(tmp_path):
    characteristic=dict(characteristic_id='C1',configuration_sha256='a'*64,instance_id='I1',part_revision='R1',serial='S1',batch='B1',unit='mm',
        minimum=9.,maximum=11.,procedure=evidence(tmp_path,'procedure'),environment_limits=dict(temperature_c=[18.,24.]))
    record={k:characteristic[k] for k in ('characteristic_id','configuration_sha256','instance_id','part_revision','serial','batch','unit')}
    record.update(value=10.,expanded_uncertainty=.1,performed_at='2026-10-11T10:00:00Z',operator='operator',inspector='inspector',
        calibration=calibrated(tmp_path),environment=dict(temperature_c=20.),evidence=evidence(tmp_path))
    return characteristic,record


def test_measurement_binds_revision_tool_environment_and_uncertainty(tmp_path):
    c,r=measurement_fixture(tmp_path);assessment=assess_measurement(c,r,tmp_path)
    assert assessment['ready_for_independent_quality_review'] and not assessment['production_released']
    for defect in ('revision','expired','self-review','environment','tampered','synthetic'):
        changed=deepcopy(r)
        if defect=='revision':changed['part_revision']='R2'
        elif defect=='expired':changed['calibration']['valid_until']='2026-10-10T00:00:00Z'
        elif defect=='self-review':changed['inspector']=changed['operator']
        elif defect=='environment':changed['environment']['temperature_c']=30.
        elif defect=='tampered':changed['evidence']['sha256']='0'*64
        else:changed['evidence']['kind']='synthetic'
        with pytest.raises(ValueError):assess_measurement(c,changed,tmp_path)


def test_torque_trace_rejects_unapproved_retorque_and_does_not_claim_preload(tmp_path):
    limits=dict(joint_id='J1',configuration_sha256='a'*64,part_revision='R1',procedure=evidence(tmp_path,'procedure'),minimum_nm=19.,maximum_nm=21.,final_angle_deg=[20.,60.])
    trace=dict(joint_id='J1',configuration_sha256='a'*64,part_revision='R1',fastener_id='F1',tool=calibrated(tmp_path,'N m'),
        performed_at='2026-10-11T10:00:00Z',operator='operator',inspector='inspector',attempt=1,rework_authority=None,
        samples=[[0.,0.,0.],[1.,10.,20.],[2.,20.,40.]],expanded_uncertainty=.2,evidence=evidence(tmp_path))
    r=torque_trace(trace,limits,root=tmp_path)
    assert r['ready_for_independent_quality_review'] and not r['preload_verified']
    trace['attempt']=2
    with pytest.raises(ValueError):torque_trace(trace,limits,root=tmp_path)
    trace['attempt']=1;trace['samples'][2][2]=10.
    with pytest.raises(ValueError):torque_trace(trace,limits,root=tmp_path)


def test_capability_remains_diagnostic_without_stability_normality_and_msa(tmp_path):
    values=[10+(i%5-2)*.01 for i in range(50)]
    r=process_statistics(values,9.,11.)
    assert r['diagnostic_pp']>0 and r['conditional_cpk'] is None and not r['capability_accepted']
    ref=evidence(tmp_path,'record')
    qualified=process_statistics(values,9.,11.,stability_evidence=ref,normality_evidence=ref,measurement_system_evidence=ref,root=tmp_path)
    assert qualified['conditional_cpk']==pytest.approx(qualified['diagnostic_ppk']) and not qualified['capability_accepted']
    assert process_statistics([10.,10.],9.,11.)['diagnostic_pp'] is None


def test_material_grade_expiry_and_cure_sampling_gates(tmp_path):
    p=dict(material_id='MAT1',unit='kg',released_grade=None)
    lot=dict(lot_id='L1',material_id='MAT1',unit='kg',quantity=2.,grade='G1',expiry='2026-10-12T00:00:00Z',supplier='supplier',certificate=evidence(tmp_path,'material'))
    assert material_lot(p,lot,'2026-10-11T10:00:00Z',tmp_path)['status']=='open-grade'
    p['released_grade']='G2';assert material_lot(p,lot,'2026-10-11T10:00:00Z',tmp_path)['status']=='grade-mismatch'
    with pytest.raises(ValueError):material_lot(p,lot,'2026-10-13T00:00:00Z',tmp_path)
    assert process_window([[0.,90.],[10.,91.],[20.,90.]],80.,100.,20.,10.)['record_checks_passed']
    assert not process_window([[0.,90.],[20.,91.]],80.,100.,20.,10.)['record_checks_passed']
    assert process_window([],None,None,None,None)['status']=='open-process-window'


def test_traveler_cannot_accept_planning_records_or_stale_hashes(package):
    p=package['production_package'];r=traveler_template(p);a=assess_traveler(p,r)
    assert not a['ready_for_independent_quality_review'] and not a['native_erp_records_changed']
    assert 'identified physical configuration required' in a['blockers']
    changed=deepcopy(r);changed['configuration_sha256']='b'*64
    with pytest.raises(ValueError):assess_traveler(p,changed)
    changed=deepcopy(r);changed['operations'].append(changed['operations'][0])
    with pytest.raises(ValueError):assess_traveler(p,changed)


def test_work_order_holds_ncrs_predecessors_and_missing_acceptance_criteria(package,tmp_path):
    p=deepcopy(package['production_package']);p['operations']=p['operations'][:2]
    r=traveler_template(p);r['work_order']='TEST-WO';r['record_id']='TEST-RECORD'
    for i,row in enumerate(r['operations']):
        row.update(disposition='performed',operator='operator',inspector='inspector',performed_at=f'2026-10-11T10:0{i}:00Z',
            evidence=[evidence(tmp_path,kind,name=f'{i}-{kind}.json') for kind in p['operations'][i]['required_evidence_kinds']])
    r['operations'][0]['open_ncr_ids']=['TEST-NCR']
    result=assess_traveler(p,r,tmp_path)
    assert any('unresolved nonconformance' in b for b in result['blockers'])
    assert any('released acceptance criteria missing' in b for b in result['blockers'])
    r['operations'][1]['performed_at']='2026-10-11T09:00:00Z'
    assert any('predecessor hold point' in b for b in assess_traveler(p,r,tmp_path)['blockers'])


def test_withdrawing_qualification_while_moving_requires_lockout():
    m=CommissioningContract();s=reference_signals()
    for event in ('wake','self-test','depot-exit','mainline'):m.command(event,s)
    s['speed_m_s']=10.;s['service_envelope_verified']=False
    result=m.command('tick',s)
    assert result['state']=='locked-out' and not result['movement_permitted']


def test_panel_geometry_changes_mass_and_stiffness_without_free_material_benefits():
    m=dict(id='test',density_kg_m3=1000.,longitudinal_modulus_pa=1e9,allowable_stress_pa=None)
    g=dict(length_m=.2,width_m=.4,thickness_m=.01);d=dict(tip_force_n=10.,deflection_limit_m=None)
    a=panel_screen(m,g,d);b=panel_screen(m,dict(g,thickness_m=.02),d)
    assert b['mass_kg']==2*a['mass_kg'] and b['EI_nm2']==8*a['EI_nm2'] and b['tip_deflection_m']==pytest.approx(a['tip_deflection_m']/8)
    assert a['conditional_stress_passed'] is None and a['embodied_carbon_kgco2e'] is None and not a['engineering_accepted']
    assert thermal_layers([dict(thickness_m=.01,conductivity_w_m_k=.1)],2.,10.)['heat_flow_w']==pytest.approx(200.)


def test_energy_balance_efficiency_and_mass_effects_are_explicit():
    duty=[dict(duration_s=10.,speed_start_m_s=0.,speed_end_m_s=10.,grade_ratio=0.,aerodynamic_force_n=0.),
          dict(duration_s=10.,speed_start_m_s=10.,speed_end_m_s=0.,grade_ratio=0.,aerodynamic_force_n=0.)]
    a=train_energy(duty,1000.,.8,.5,100.,0.);b=train_energy(duty,1000.,.9,.5,100.,0.)
    assert a['mechanical_work_j']==pytest.approx(0.) and a['battery_energy_j']==pytest.approx(39500.)
    assert abs(a['energy_balance_residual_j'])<1e-7 and b['battery_energy_j']<a['battery_energy_j']
    assert train_energy(duty,500.,.8,.5,100.,0.)['battery_energy_j']<a['battery_energy_j']
    assert not a['service_delivery_qualified']


@pytest.mark.parametrize('fault',sorted(HEALTH))
def test_critical_faults_lock_out_without_automatic_recovery(fault):
    m=CommissioningContract();s=reference_signals()
    for event in ('wake','self-test','depot-exit','mainline'):m.command(event,s)
    s[fault]=False;r=m.command('reset-noncritical',s)
    assert r['state']=='locked-out' and not r['movement_permitted']
    s[fault]=True;s['reset_authority']=False;assert m.command('clear-lockout',s)['state']=='locked-out'
    s['reset_authority']=True;assert m.command('clear-lockout',s)['state']=='self-test'


@pytest.mark.parametrize('signal',['doors_locked','obstacle_clear','configuration_released','service_envelope_verified'])
def test_missing_movement_gate_inhibits_start_and_withdrawn_authority_holds_train(signal):
    m=CommissioningContract();s=reference_signals();m.command('wake',s);m.command('self-test',s)
    s[signal]=False;assert not m.command('depot-exit',s)['movement_permitted']


def test_lifecycle_and_bounded_noncritical_reset_are_only_offline_contract_checks():
    r=fault_campaign();assert r['contract_checks_passed'] and not r['goa4_qualified'] and not r['actual_train_configuration_released']
    m=CommissioningContract();s=reference_signals();m.command('wake',s);m.command('self-test',s)
    assert m.command('reset-noncritical',s)['command_allowed'] and not m.command('reset-noncritical',s)['command_allowed']
    s['speed_m_s']=1.;assert m.command('tick',s)['state']=='locked-out'


def test_generated_factory_package_verifies_and_changed_records_are_detected(tmp_path):
    output=tmp_path/'factory';script=ROOT/'tools/automation/factory-modernisation.py'
    base=[sys.executable,str(script)]
    subprocess.run(base+['generate','--output',str(output)],check=True,capture_output=True)
    subprocess.run(base+['verify','--output',str(output)],check=True,capture_output=True)
    with (output/'assembly-operations.csv').open() as stream:operations=list(csv.DictReader(stream))
    with (output/'material-passports.csv').open() as stream:passports=list(csv.DictReader(stream))
    assert len(operations)==756 and len({row['id'] for row in operations})==756 and len(passports)==117
    assert 'unissued' in (output/'work-instructions.md').read_text().lower()
    (output/'material_passports.json').write_text('[]\n')
    result=subprocess.run(base+['verify','--output',str(output)],capture_output=True,text=True)
    assert result.returncode!=0 and 'factory output changed' in result.stderr
