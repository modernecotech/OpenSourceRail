from copy import deepcopy
import json
import math
from pathlib import Path
import subprocess
import sys
import time

import pytest

from engineering.halbach_scaling import candidates as c, screen as s
from engineering.passive_suspension import fields


def fake_solve(geometry,*,gap_m,temperature_C,currents_A,settings):
    """Explicit unit fixture: prescribed forces, not magnetic design evidence."""
    force=20000+10*sum(currents_A.values())
    contours=[dict(F_z_N=force,F_y_N=0.,M_x_Nm=0.),dict(F_z_N=.99*force,F_y_N=0.,M_x_Nm=0.)]
    raw=dict(schema=fields.SCHEMA,geometry_id=fields._digest(geometry),source_sha256=fields.sources(),
        operating_point=dict(gap_m=float(gap_m),temperature_C=float(temperature_C),lateral_m=0.,roll_rad=0.,currents_A=currents_A),
        settings=fields._settings(settings),declared_material_definitions=geometry['materials'],
        F_z_N=force,F_y_N=0.,M_x_Nm=0.,steel_B_peak_T=1.2,PM_H_parallel_min_A_per_m=-500000.,
        numerical_status='converged',steel_model='nonlinear_repo_proxy',material_model_domain_pass=True,
        interpolation_usable=False,physical_accepted=False,material_correlated=False,unit_fixture=True,
        diagnostics=dict(contour_forces=contours,contour_relative_difference=.01,contour_check_pass=True,
                         validation_solves=1,mesh_check='not_assessed',boundary_check='not_assessed'))
    raw['result_id']=fields._digest(raw);return raw


def test_current_response_heat_and_mass_ceiling_are_recomputed(monkeypatch):
    monkeypatch.setattr(fields,'solve',fake_solve)
    value=next(q for q in c.candidates() if q['winding_definition']['layout']=='differential')
    currents={coil['id']:15. for coil in value['circuits']}
    point=s.evaluate_point(value,gap_m=.044,temperature_C=80.,currents_A=currents)
    assert s.validate_point(point,value) is point
    p=point['comparison']
    assert p['conservative_contour_Fz_N']==.99*20300
    assert p['conditional_1_3_aw3_ceiling_kg_per_car']==pytest.approx(24*.99*20300/(1.3*9.80665))
    assert p['conditional_aw3_ceiling_after_counted_support_kg']==pytest.approx(p['conditional_1_3_aw3_ceiling_kg_per_car']-value['stock']['train_known_mass_kg_per_car'])
    expected=sum(225*coil['resistance_20c_ohm'] for coil in value['circuits'])
    assert p['copper_I2R_20C_W_per_module']==pytest.approx(expected)
    assert p['copper_I2R_80C_W_per_module']==pytest.approx(expected*(1+60*.00393))
    assert all(q==3.75 for q in p['current_density_A_per_mm2'].values())
    assert p['thermal_equilibrium_C'] is None and p['complete_installed_car_mass_kg'] is None
    assert p['force_control_authority_qualified'] is False and p['mesh_domain_convergence_assessed'] is False


def test_negative_demag_margin_is_retained_as_a_failed_necessary_sample(monkeypatch):
    def failed_demag(*args,**kwargs):
        raw=fake_solve(*args,**kwargs);raw['PM_H_parallel_min_A_per_m']=-2e6
        raw.pop('result_id');raw['result_id']=fields._digest(raw)
        return raw
    monkeypatch.setattr(fields,'solve',failed_demag)
    value=next(q for q in c.candidates() if not q['winding_definition']['baseline_control'])
    point=s.evaluate_point(value)
    assert point['execution_status']=='completed' and point['numerical_status']=='converged'
    assert point['comparison']['demag_proxy_margin_A_per_m']<0
    assert point['comparison']['demag_proxy_screen_pass'] is False
    assert point['comparison']['next_experiment_sample_screen_pass'] is False


@pytest.mark.parametrize('mutation',['candidate','geometry','source','settings','force','material','release','raw-release','fake-map'])
def test_strict_single_point_validator_refuses_even_rehashed_incompatible_data(monkeypatch,mutation):
    monkeypatch.setattr(fields,'solve',fake_solve);value=c.candidates()[0]
    point=s.evaluate_point(value)
    if mutation=='candidate':point['candidate_id']='0'*64
    elif mutation=='geometry':point['raw_result']['geometry_id']='0'*64
    elif mutation=='source':point['request']['source_sha256']={}
    elif mutation=='settings':point['request']['settings']['steel_model']='linear_bound'
    elif mutation=='force':point['comparison']['conditional_1_3_aw3_ceiling_kg_per_car']+=1000
    elif mutation=='material':point['raw_result']['declared_material_definitions']['steel']['j_t'][1]+=1
    elif mutation=='release':point['physical_accepted']=True
    elif mutation=='raw-release':point['raw_result']['physical_accepted']=True
    else:point['raw_result']['interpolation_usable']=True
    raw=point['raw_result'];raw.pop('result_id');raw['result_id']=fields._digest(raw)
    point['evaluation_id']=c.identity(point['request'])
    with pytest.raises(ValueError):s.validate_point(point,value)


@pytest.mark.parametrize('kwargs',[dict(gap_m=.007),dict(gap_m=.061),dict(temperature_C=81),dict(currents_A={'no-circuit':1.}),dict(currents_A={'array-control':15.001}),dict(settings={'steel_model':'linear_bound'})])
def test_out_of_domain_states_are_refused_before_a_solve(monkeypatch,kwargs):
    monkeypatch.setattr(fields,'solve',lambda *a,**k:pytest.fail('invalid request reached numerical solver'))
    with pytest.raises(ValueError):s.evaluate_point(c.candidates()[0],**kwargs)


def fake_execute(directory,request,root,seconds):
    directory.mkdir();s._write(directory/'input.json',request)
    scenario=request['scenario']
    point=s.evaluate_point(request['candidate'],gap_m=scenario['gap_m'],temperature_C=scenario['temperature_C'],currents_A=scenario['currents_A'],root=root)
    s._write(directory/'point.json',point)
    execution=dict(command=['explicit-unit-fixture'],returncode=0,timed_out=False,elapsed_s=.001,deadline_s=seconds)
    s._write(directory/'execution.json',execution)
    return dict(point,execution=execution)


def reseal(output):
    result=json.loads((output/'result.json').read_bytes());result.pop('screen_id');result['screen_id']=c.identity(result)
    (output/'result.json').write_bytes(c.encoded(result));manifest=json.loads((output/'manifest.json').read_bytes());manifest['files_sha256']=s._inventory(output)
    (output/'manifest.json').write_bytes(c.encoded(manifest))


def test_budget_inventory_zero_reuse_and_coherent_counts_tamper(tmp_path,monkeypatch):
    monkeypatch.setattr(fields,'solve',fake_solve);monkeypatch.setattr(s,'_execute',fake_execute)
    values=[q for q in c.candidates() if q['winding_definition']['layout']=='differential' and q['parameters']['magnet_volume_m3'] in (.012,.024)]
    output=tmp_path/'run';result=s.run(output,candidates=values)
    assert s.verify(output)['current']
    assert result['counts']==dict(physical_geometries=2,nominal_records=2,authority_records=6,reused_zero_current_records=2,field_solves_started=6,numerical_nominal_converged=2)
    assert len({q['evaluation_id'] for q in result['authority_rows']})==6
    assert all(not q['comparison']['force_control_authority_qualified'] for q in result['authority_rows'])
    with pytest.raises(FileExistsError):s.run(output,candidates=values)
    value=json.loads((output/'result.json').read_bytes());value['counts']['field_solves_started']=999
    (output/'result.json').write_bytes(c.encoded(value));reseal(output)
    with pytest.raises(ValueError,match='counts'):s.verify(output)


def test_interrupted_cases_keep_unknowns_and_no_force_credit(tmp_path,monkeypatch):
    def interrupted(directory,request,root,seconds):
        directory.mkdir();s._write(directory/'input.json',request)
        execution=dict(command=['explicit-unit-interruption'],returncode=-9,timed_out=True,elapsed_s=seconds,deadline_s=seconds)
        s._write(directory/'execution.json',execution)
        return dict(candidate_id=request['candidate']['physical_id'],execution_status='interrupted',numerical_status='unknown',execution=execution,error='fixture deadline',**s.FLAGS)
    monkeypatch.setattr(s,'_execute',interrupted)
    output=tmp_path/'interrupted';result=s.run(output,candidates=[c.candidates()[0]])
    assert s.verify(output)['current']
    assert result['rows'][0]['execution_status']=='interrupted'
    assert 'comparison' not in result['rows'][0]
    assert result['counts']['numerical_nominal_converged']==0


def test_worker_group_has_a_hard_deadline():
    process=subprocess.Popen([sys.executable,'-c','import time;time.sleep(30)'],start_new_session=True)
    started=time.monotonic();s._terminate(process)
    assert process.returncode!=0 and time.monotonic()-started<5


def test_free_air_field_fixture_matches_independent_charge_integral():
    geometry=dict(length_x_m=1.,materials={'ferrite':dict(relative_permeability=1.,br_temperature_coefficient_per_k=0.)},
        regions=[dict(id='air-pm',material='ferrite',group='train',bounds_yz_m=[-.1,.1,-.05,0.],Br_z_T=.45)])
    actual=fields.sample_field(geometry,[[0.,.05],[0.,.1]],settings=dict(mesh_size_m=.01,outer_margin_m=1.))
    for sample,d in zip(actual,(.05,.1)):
        expected=.45/math.pi*(math.atan(.1/d)-math.atan(.1/(d+.05)))
        assert sample[1]==pytest.approx(expected,rel=.035)
