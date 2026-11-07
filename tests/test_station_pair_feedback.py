"""Controller/plant separation and retained evidence; no native jobs here."""
from copy import deepcopy
from math import sqrt
import json,shutil
from pathlib import Path
import pytest
from engineering.station_pair import coordinator,control_policy,history
from engineering.station_rail.common import identity


@pytest.fixture(scope='module')
def data():return coordinator.variants()


def request(data,**kw):
    brief,bundle,mass,variants=data
    v=next(v for v in variants if v['family']=='powered-wheel')
    return coordinator.case_for(v,bundle,mass,brief,speed_km_h=50,control_mode='feedback',**kw)


def test_same_controller_bounds_across_mass_force_and_grade_observations(data):
    base=request(data)
    for kw in (dict(mass_case='low'),dict(mass_case='high'),dict(force_case='low'),
               dict(grade=-.02),dict(wind=15),dict(drive_fault_observed=True),
               dict(sensor_biases=dict(position_bias_m=-.25,speed_bias_m_s=-.1))):
        changed=request(data,**kw)
        assert control_policy.same_policy(base['control'],changed['control'])
        assert changed['candidate_id']==base['candidate_id']
        assert changed['id']!=base['id']


def test_controller_inputs_do_not_follow_actual_plant_values(data):
    high=request(data,mass_case='high',force_case='low')
    low=request(data,mass_case='low')
    assert high['mass_kg']!=low['mass_kg']
    assert high['drive']['mechanical_power_w']!=low['drive']['mechanical_power_w']
    assert high['control']==low['control']
    assert high['control']['mass_upper_kg']>=high['mass_kg']
    assert high['control']['mass_lower_kg']<=low['mass_kg']


def test_motor_failure_does_not_twice_derate_contact_floor(data):
    brief,bundle,mass,variants=data
    v=next(v for v in variants if v['family']=='powered-wheel')
    c=request(data);p=c['control']
    floor=brief['degraded_adhesion_hypothesis']*p['mass_lower_kg']*9.80665*v['geometry']['driven_axles']/24
    limit=json.loads((coordinator.ROOT/control_policy.POLICY).read_bytes())['numerical_grade_magnitude_limit']
    assert p['start_traction_lower_bound_n']==pytest.approx(floor/sqrt(1+limit**2))
    assert p['start_traction_lower_bound_n']>floor*.9


def test_berth_tolerance_never_expands_model_travel_boundary(data):
    c=request(data)
    assert c['control']['end_of_authority_m']==c['distance_m']
    assert c['control']['end_of_authority_m']<c['distance_m']+c['berth_tolerance_m']
    revised=deepcopy(c['control']);revised['end_of_authority_m']+=2
    assert not control_policy.same_policy(c['control'],revised)


def test_unknown_architecture_does_not_invent_controller_mass_bounds(data):
    brief,bundle,mass,variants=data
    for v in variants:
        if v['family'] in ('compact-LIM','hybrid'):
            c=coordinator.case_for(v,bundle,mass,brief,speed_km_h=50,control_mode='feedback')
            assert c['control'] is None and c['drive'] is None


def test_bias_outside_contract_is_explicit_not_hidden_in_new_policy(data):
    nominal=request(data);bad=request(data,sensor_biases=dict(position_bias_m=-2.))
    assert bad['control']['position_error_bound_m']==nominal['control']['position_error_bound_m']
    assert bad['control']['position_bias_m']==-2.
    assert bad['control']['policy_id']==nominal['control']['policy_id']
    assert bad['id']!=nominal['id']
    with pytest.raises(ValueError):request(data,sensor_biases=dict(hidden_mass_kg=1.))
    with pytest.raises(ValueError):request(data,drive_fault_observed='false')


def test_comparison_uses_same_fault_plant_and_different_explicit_control(data):
    brief,bundle,mass,variants=data
    v=next(v for v in variants if v['family']=='powered-wheel')
    fixed=coordinator.case_for(v,bundle,mass,brief,speed_km_h=50)
    fixed['brake_start_m']=600;fixed['id']=identity({k:v for k,v in fixed.items() if k!='id'})
    f=coordinator.followup_requests(v,bundle,mass,brief,fixed)
    a=coordinator.followup_requests(v,bundle,mass,brief,request(data))
    assert [n for n,_ in f]==[n for n,_ in a]
    for (name,x),(_,y) in zip(f,a):
        assert {k:w for k,w in x.items() if k not in ('id','control','brake_start_m')}=={
            k:w for k,w in y.items() if k not in ('id','control','brake_start_m')}
        assert x['brake_start_m']==600
    byname=dict(a)
    assert byname['half-drive']['control']['drive_fault_observed'] is True
    assert byname['half-drive-unobserved']['control']['drive_fault_observed'] is False
    assert byname['compound-downhill-boundary']['grade_fraction']==pytest.approx(-.021)
    assert len({c['control']['policy_id'] for _,c in a})==1


def test_uphill_cable_necessary_energy_failure_is_not_hidden(data):
    brief,bundle,mass,variants=data
    for v in variants:
        if v['family']=='cable':
            c=coordinator.case_for(v,bundle,mass,brief,speed_km_h=60,grade=.02,control_mode='feedback')
            assert coordinator.coast_bound(v,c)['fails_even_without_aerodynamic_loss'] is True
            c['headwind_m_s']=-15
            assert coordinator.coast_bound(v,c)['fails_even_without_aerodynamic_loss'] is None


def test_fixed_control_archive_is_immutable_source_bound_history(tmp_path):
    proof=history.verify()
    assert proof['git_source_commit']==history.BASE
    assert proof['physical_accepted'] is False and proof['selected_reference_changed'] is False
    folder=tmp_path/history.OUTPUT;shutil.copytree(history.ROOT/history.OUTPUT,folder)
    archive=folder/'packet-and-declared-sources.tar.gz'
    archive.write_bytes(archive.read_bytes()+b'changed')
    with pytest.raises(ValueError,match='archive changed'):history.verify(tmp_path)
