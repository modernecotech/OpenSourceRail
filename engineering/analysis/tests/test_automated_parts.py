"""Physical change propagation and independent reference-parts balances."""
from copy import deepcopy
import hashlib
import json
import math
from pathlib import Path
import subprocess
import sys
import numpy as np
import pytest
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT),str(ROOT/'design/component-catalogue/src')]
from osr_mech.automated_geometry import aggregate,from_source,primitive_volume,primitive_inertia,source
from osr_mech.common import ConsistFamily
from osr_mech.engineering_definition import fingerprint,load_definition,validate,verification_register
from engineering.civil_exploration.automated_battery import compile_pack,duty_cycle,box
from engineering.civil_exploration.variant_compiler import compile_variant,validate_interfaces,BASIS_PATH,CHOICES_PATH
from engineering.civil_exploration.spatial_vehicle import SpatialVehicle,loaded_model
from engineering.analysis.shared_service import passage_configuration


@pytest.fixture(scope='module')
def compiled():return compile_variant()


def test_full_train_counts_positions_and_weight_equilibrium(compiled):
    model=compiled['model'];cfg=compiled['spatial_configuration'];v=SpatialVehicle(model,cfg['joint_laws'])
    assert len([g for g in v.groups.values() if g['kind']=='carbody'])==6
    assert len([g for g in v.groups.values() if g['kind']=='bogie'])==12
    assert len([g for g in v.groups.values() if g['wheel']])==24
    expected=sorted(x for b in model['family_definition']['bogies'] for x in b['axle_x_m'])
    assert sorted(g['cg'][0] for g in v.groups.values() if g['wheel'])==pytest.approx(expected)
    assert sum(c['static_n'] for c in v.contacts)==pytest.approx(v.total_mass*9.81)
    assert len(v.contacts)==48 and min(c['static_n'] for c in v.contacts)>0
    assert compiled['review']['mass_balance_residual_kg']==pytest.approx(0.)
    _,plan=passage_configuration(model,cfg,speed_m_s=15.)
    assert plan['full_family_represented'] and len(plan['trains'][0]['wheelsets'])==24
    # Independent passage distance between outer axles + both approaches/margins.
    assert plan['duration_s']==pytest.approx((75+12+max(expected)-min(expected))/15.)


@pytest.mark.parametrize('family',list(ConsistFamily))
def test_every_authoritative_family_can_be_generated_with_a_fitting_pack(family):
    choices=load_definition(CHOICES_PATH);choices['family']=family.value;choices['battery']['series_modules']=20
    r=compile_variant(choices)
    count=r['model']['family_definition']['car_count']
    assert r['review']['car_count']==count and r['review']['wheelset_count']==4*count
    assert r['review']['joint_count']==len(r['model']['instances'])-1


def test_battery_capacity_change_updates_geometry_mass_inertia_energy_heat_and_current(compiled):
    choices=load_definition(CHOICES_PATH);choices['battery']['parallel_strings']=2
    small=compile_variant(choices);large=compiled['battery'];pack=small['battery']
    assert pack['module_count']==large['module_count']/2
    assert pack['usable_energy_kwh']==pytest.approx(large['usable_energy_kwh']/2)
    assert pack['resistance_ohm']==pytest.approx(2*large['resistance_ohm'])
    assert pack['charge_current_limit_a']==large['charge_current_limit_a']/2
    assert pack['dimensions_m'][1]<large['dimensions_m'][1]
    assert pack['properties']['mass_kg']<large['properties']['mass_kg']
    assert np.trace(pack['properties']['inertia_tensor_kg_m2'])<np.trace(large['properties']['inertia_tensor_kg_m2'])
    segment=[dict(duration_s=60.,terminal_power_w=200000.)]
    a=duty_cycle(large,segment)['history'][0];b=duty_cycle(pack,segment)['history'][0]
    assert b['string_current_a']>a['string_current_a'] and b['heat_generation_w']>a['heat_generation_w']
    assert not b['constraints']['current'] and a['constraints']['current']
    assert b['soc']<a['soc'] and b['temperature_c']>a['temperature_c']
    budget=small['review']['conditional_operating_budget'];baseline=compiled['review']['conditional_operating_budget']
    assert budget['range_km']<baseline['range_km']/2
    assert budget['maximum_recharge_interval_km']<baseline['maximum_recharge_interval_km']
    assert not budget['current_constraints_passed'] and baseline['current_constraints_passed']
    delta=large['properties']['mass_kg']-pack['properties']['mass_kg']
    assert compiled['review']['total_mass_kg']-small['review']['total_mass_kg']==pytest.approx(6*delta)
    assert fingerprint(compiled['model'])!=fingerprint(small['model'])
    invalid=verification_register(small['model'],compiled['verification'],implementation_hashes=small['review']['sources_sha256'])
    assert {'mass-properties','vehicle-model','vehicle-dynamics','bridge-demand','cost'}<=set(invalid['invalidated'])


def test_pack_material_and_manufacturing_quantities_are_conservative(compiled):
    pack=compiled['battery'];cut=pack['cutlist']
    assert sum(r['mass_kg'] for r in cut)==pytest.approx(pack['properties']['mass_kg'])
    assert len([r for r in cut if r['feature'].startswith('module-')])==112
    assert len([r for r in cut if r['feature'].startswith('mount-')])==40
    assert len(pack['hole_pattern_m'])==8
    records=compiled['manufacturing']['battery_cutlist']
    assert sum(r['mass_kg'] for r in records)==pytest.approx(6*pack['properties']['mass_kg'])
    assert all(q['acceptance_limits'] is None and q['status'].startswith('unexecuted') for q in compiled['manufacturing']['qa_requirements'])


def test_residual_coverage_is_reported_for_every_required_slot(compiled):
    c=compiled['coverage'];rows=c['rows']
    assert len(rows)==c['required_allocation_count'] and len({r['allocation_id'] for r in rows})==len(rows)
    assert c['explicit_reference_allocation_count']+c['unresolved_allocation_count']==len(rows)
    assert c['unresolved_allocation_count']>0 and not c['full_production_component_coverage']
    for row in rows:
        if row['instances']:assert row['joints'] and row['interfaces']
        else:assert row['representation']=='unresolved-residual-allocation' and row['limits']
    assert not compiled['review']['physical_validation'] and compiled['review']['engineering_constraints_passed'] is None


def test_interfaces_reject_stale_identity_bad_units_endpoint_and_joint_mapping(compiled):
    for error in ('identity','units','endpoint','joint','limits','missing'):
        register=deepcopy(compiled['interfaces'])
        if error=='identity':register['configuration_sha256']='stale'
        elif error=='units':register['interfaces'][0]['units']['force']='kN'
        elif error=='endpoint':register['interfaces'][0]['endpoints'][0]['datum']='missing'
        elif error=='joint':register['interfaces'][0]['joint']='missing'
        elif error=='limits':register['interfaces'][0]['limits']['force_n']=[1.,0.]
        else:register['interfaces'].pop(0)
        with pytest.raises(ValueError):validate_interfaces(register,compiled['model'])


@pytest.mark.parametrize('field,value',[('parallel_strings',True),('series_modules',0),('series_modules',64),
    ('module_gap_m',0.),('enclosure_thickness_m',-.01),('soc_max',.05),('state_of_health',1.1)])
def test_invalid_choices_and_collisions_rejected(field,value):
    choices=load_definition(CHOICES_PATH);choices['battery'][field]=value
    with pytest.raises(ValueError):compile_variant(choices)


def test_dc_energy_charge_and_discharge_and_thermal_balance(compiled):
    pack=compiled['battery'];r=duty_cycle(pack,[dict(duration_s=30.,terminal_power_w=150000.),dict(duration_s=20.,terminal_power_w=-75000.)])
    assert abs(r['electrical_balance_residual_j'])<1e-7 and abs(r['thermal_balance_residual_j'])<1e-7
    assert r['history'][0]['pack_current_a']>0 and r['history'][1]['pack_current_a']<0
    for row in r['history']:
        I=row['pack_current_a'];V=row['terminal_voltage_v'];dt=row['duration_s']
        assert V*I==pytest.approx(row['terminal_power_w'])
        assert row['heat_generation_w']==pytest.approx(I*I*pack['resistance_ohm'])
        assert abs(row['energy_balance_residual_j'])<1e-7
    # At zero terminal power, cooling has the exact analytic exponential decay.
    cool=duty_cycle(pack,[dict(duration_s=100.,terminal_power_w=0.)],initial_temperature_c=40.)
    expected=25+15*math.exp(-pack['cooling_conductance_w_k']*100/pack['thermal_capacity_j_k'])
    assert cool['history'][0]['temperature_c']==pytest.approx(expected)
    with pytest.raises(ValueError,match='domain'):duty_cycle(pack,[dict(duration_s=1.,terminal_power_w=1e9)])


def test_closed_plate_volume_and_inertia_match_independent_subtraction():
    p=box('plate',[1.,.5,.01],[0,0,0],'plate',holes_xy_m=[[-.2,0.],[.2,0.]],hole_radius_m=.01)
    density=2700.;mass=primitive_volume(p)*density
    assert mass==pytest.approx(density*(.005-2*math.pi*.01**2*.01))
    removed=density*math.pi*.01**2*.01;gross=13.5
    expected_izz=gross*(1+.25)/12-2*removed*(.01**2/2+.2**2)
    assert primitive_inertia(p,mass)[2,2]==pytest.approx(expected_izz)
    two=[box('a',[.1,.1,.1],[-1.,0,0]),box('b',[.1,.1,.1],[1.,0,0])]
    result=aggregate(two,[2.,2.])
    assert result['cg_m']==[0.,0.,0.] and result['inertia_tensor_kg_m2'][1][1]==pytest.approx(4+4*.02/12)


def test_geometry_is_embedded_in_model_identity_and_rejected_when_malformed(compiled):
    row=next(r for r in compiled['model']['instances'] if r['id']=='car-1/battery')
    assert from_source(row['geometry'])==compiled['battery']['geometry']
    model=deepcopy(compiled['model']);geometry=next(r for r in model['instances'] if r['id']==row['id'])['geometry']
    geometry['source']=['osr-parametric-reference/1:'+json.dumps(dict(role='bad',primitives=[]))]
    with pytest.raises(ValueError):validate(model)


def test_passenger_loading_does_not_double_count_expanded_battery(compiled):
    cfg=compiled['spatial_configuration'];base=SpatialVehicle(compiled['model'],cfg['joint_laws'])
    loaded=loaded_model(compiled['model'],dict(cfg['traffic'][0]['load_case'],id='nominal'))
    gross=SpatialVehicle(loaded,cfg['joint_laws'])
    assert gross.total_mass-base.total_mass==pytest.approx(75*compiled['model']['family_definition']['profile']['passenger_capacity'])


def test_generated_package_verifies_and_detects_modified_output(tmp_path):
    script=ROOT/'tools/automation/compile-reference-parts.py';output=tmp_path/'parts'
    cmd=[sys.executable,str(script)]
    subprocess.run(cmd+['generate','--output',str(output)],check=True,capture_output=True)
    subprocess.run(cmd+['verify','--output',str(output)],check=True,capture_output=True)
    (output/'battery.json').write_text('{}\n')
    failure=subprocess.run(cmd+['verify','--output',str(output)],capture_output=True,text=True)
    assert failure.returncode!=0 and 'changed generated part output' in failure.stderr


def test_retained_native_parts_match_the_current_variant_and_saved_geometry(compiled):
    folder=ROOT/'design/component-catalogue/models/cad'
    native=load_definition(folder/'reference-full-train.native.json');audit=load_definition(folder/'reference-full-train.audit.json')
    cad_hash=hashlib.sha256((folder/'reference-full-train.FCStd').read_bytes()).hexdigest()
    assert native['configuration_sha256']==audit['configuration_sha256']==fingerprint(compiled['model'])
    assert native['fcstd_sha256']==audit['fcstd_sha256']==cad_hash
    assert audit['reopened_native_instance_count']==192 and audit['restored_native_solver_result']==0
    assert audit['analytic_occ_primitive_checks']==164 and audit['maximum_relative_inertia_error']<1e-8
    assert all(count>0 for count in native['drawing_visible_edges'].values())
    assert not native['drawing_issued'] and not audit['production_released'] and not audit['physical_validation']


def test_retained_failed_service_case_is_kept_out_of_the_completed_passage_set(compiled):
    proof=load_definition(ROOT/'engineering/civil_exploration/examples/automated-parts-evidence.json')
    assert proof['configuration_sha256']==fingerprint(compiled['model'])
    service=proof['service']
    assert not service['complete_full_family_case_ids'] and not service['numerical_time_and_mesh_confirmation_performed']
    assert len(service['cases'])==1 and service['cases'][0]['status']=='failed'
    assert '9.775s' in service['cases'][0]['error'] and not service['cases'][0]['complete_passage']
    assert len(service['unexecuted_case_ids'])==21 and service['retained_history_sha256']
    assert proof['engineering_constraints_passed'] is None and not proof['production_released'] and not proof['physical_validation']
