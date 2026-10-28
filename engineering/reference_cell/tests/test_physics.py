"""Synthetic method controls do not furnish operating or physical evidence."""
from copy import deepcopy
from math import sqrt
import pytest
from engineering.reference_cell import physics as p
from engineering.railway_twin import model
from engineering.railway_completion import FLAGS
from engineering.design_search import system_motion
from engineering.design_search.tests.test_system_motion import bundle as old_bundle,case as old_case,force_map,seal
from engineering.station_rail.common import identity


def bundle():
    b=old_bundle();b.update(car_length_m=17.,coupling_gap_m=.5)
    b['brake_definition']['brake_definition_id']=identity(b['brake_definition'])
    return b


def case(b,**changes):
    s=old_case(b);s.update(changes);s.pop('scenario_id');return system_motion.scenario(b,s)

def models(b):
    node=dict(capacity_J_K=1e6,heat_rejection_W_K=0.,initial_C=20.,ambient_C=20.,maximum_C=500.)
    x=dict(schema='osr-reference-cell-coupling-models/1',candidate_id=b['candidate_id'],bundle_definition_id=b.get('definition_id'),
        brake_definition_id=b['brake_definition']['brake_definition_id'],brake_thermal=node,
        pad_fade=[dict(temperature_C=20.,pad_mu=.35),dict(temperature_C=500.,pad_mu=.15)],
        auxiliary=dict(service_load_W=100.,HVAC_W=200.,usable_energy_J=1e7,initial_energy_J=1e7,minimum_essential_energy_J=1000.,heat_fraction=.1,thermal=deepcopy(node)),
        reactions=dict(bogie_centres_from_rear_m=[3.,14.],CG_from_rear_m=8.5,CG_height_m=1.,axles_per_bogie=2),
        protection=dict(response_s=1.,guaranteed_deceleration_m_s2=.5,position_uncertainty_m=1.,blocks_m=[[0.,50.],[50.,100.]],minimum_separation_m=10.),
        launch_hold=dict(declared=False,maximum_s=10.,maximum_restraint_N_train=10000.),supporting_record_ids={})
    x['model_id']=p.model_payload_id(x);return x


def reseal(x):
    x['model_id']=p.model_payload_id(x);return x


def test_production_holds_missing_maps_and_coupled_models():
    b=model.materialize()['bundle'];result=p.evaluate(b)
    assert result['execution']=='not-run'
    assert 'Missing available force map' in result['reasons']
    assert any('coupled' in r for r in result['reasons'])
    assert not result['numerical_arrival_predicted']
    assert all(result[k] is False for k in FLAGS)


def test_all_loads_faults_and_temperature_cases_keep_exact_candidate():
    b=model.materialize()['bundle'];rows=p.scenarios(b)
    assert len(rows)==27 and len({r['scenario']['scenario_id'] for r in rows})==27
    assert {r['candidate_id'] for r in rows}=={b['candidate_id']}
    assert {r['scenario']['load'] for r in rows}=={'empty','normal','crowd'}
    assert {r['scenario'].get('ambient_C') for r in rows}>={5.,45.}
    assert {r['scenario']['fault']['kind'] for r in rows}>={'bank-failure','power-interruption','emergency-braking','disabled-rescue'}
    assert {r['scenario']['distance_m'] for r in rows}=={2000.}


def test_constant_force_auxiliary_energy_reactions_and_independent_motion_arithmetic():
    b=bundle();s=case(b);m=force_map(b,s);m0=models(b)
    result=p.method_test(b,m,m0,scenario_overrides=s)
    assert result['state']=='destination-boundary'
    assert result['final_position_m']==pytest.approx(100.,abs=1e-8)
    assert result['final_speed_m_s']==pytest.approx(sqrt(20.),abs=1e-8)
    assert result['elapsed_s']==pytest.approx(sqrt(2000.),abs=1e-8)
    assert result['auxiliary_energy_used_J']==pytest.approx(300/.9*result['elapsed_s'])
    assert abs(result['auxiliary_energy_residual_J'])<1e-5
    assert abs(result['auxiliary_delivery_residual_J'])<1e-5
    assert result['auxiliary_internal_heat_J']==pytest.approx(result['auxiliary_energy_used_J']*.1)
    assert abs(result['mechanical_energy_residual_J'])<1e-5
    assert abs(result['electrical_work_residual_J'])<1e-5
    assert sum(result['trace'][-1]['axle_normal_reactions_N'])==pytest.approx(1000*9.80665)
    assert result['trace'][-1]['auxiliary_temperature_C']>20.
    assert result['available_operating_map_id'] is None and result['test_only']
    assert not result['numerical_arrival_predicted'] and result['qualified_headway_s'] is None
    assert all(result[k] is False for k in FLAGS)


def test_production_entry_rejects_synthetic_instead_of_allowing_self_approval():
    b=bundle();s=case(b);m=force_map(b,s)
    with pytest.raises(ValueError,match='Synthetic'):p.evaluate(b,m,models=models(b),scenario_overrides=s)


@pytest.mark.parametrize('change',[
    lambda x:x.update(candidate_id='f'*64),
    lambda x:x['auxiliary'].update(usable_energy_J=-1),
    lambda x:x['brake_thermal'].update(capacity_J_K=0),
    lambda x:x['reactions'].update(CG_from_rear_m=16.),
    lambda x:x['protection'].update(guaranteed_deceleration_m_s2=0.),
    lambda x:x['pad_fade'].reverse(),
    lambda x:x['launch_hold'].update(maximum_s=31.),
])
def test_invalid_or_mixed_coupled_models_rejected(change):
    b=bundle();x=models(b);change(x);reseal(x)
    with pytest.raises(ValueError):p.validate_models(b,x)


def test_no_nominal_force_scaling_for_failed_bank():
    b=bundle();s=case(b,fault=dict(kind='bank-failure',at_s=2.,bank_index=1));m=force_map(b,s)
    with pytest.raises(ValueError,match='Separate exact'):p.method_test(b,m,models(b),scenario_overrides=s)


def test_power_interruption_uses_separate_map_and_no_hidden_coast_force():
    b=bundle();fault=dict(kind='power-interruption',at_s=2.);s=case(b,fault=fault)
    nominal=force_map(b,s);failed=force_map(b,s,force=0.);failed['fault_state']=fault;failed=seal(failed)
    result=p.method_test(b,nominal,models(b),scenario_overrides=s,fault_maps={'power-interruption':failed})
    active=[r for r in result['trace'] if r['fault_active']]
    assert active and all(r['thrust_N_train']==0. for r in active)
    assert all(r['electrical_input_W_train']==0. for r in active)
    assert abs(result['mechanical_energy_residual_J'])<1e-5


def test_emergency_braking_couples_brake_heat_and_fade():
    b=bundle();s=case(b,fault=dict(kind='emergency-braking',at_s=5.));m=force_map(b,s)
    result=p.method_test(b,m,models(b),scenario_overrides=s)
    assert result['state']=='stopped'
    assert result['final_position_m']<100.
    assert result['friction_brake_heat_J']>0.
    assert result['trace'][-1]['brake_temperature_C']>20.
    assert abs(result['mechanical_energy_residual_J'])<1e-4


def test_disabled_train_never_receives_invented_rescue_drive():
    b=bundle();s=case(b,fault=dict(kind='disabled-rescue',at_s=5.));m=force_map(b,s)
    result=p.method_test(b,m,models(b),scenario_overrides=s)
    assert result['rescue_required'] and result['rescue_execution']=='not-run-no-tow-model'
    assert not result['numerical_arrival_predicted']


def test_exhausted_auxiliary_service_energy_is_an_actual_failure():
    b=bundle();s=case(b);x=models(b)
    x['auxiliary'].update(usable_energy_J=1.,initial_energy_J=1.,minimum_essential_energy_J=0.);reseal(x)
    result=p.method_test(b,force_map(b,s),x,scenario_overrides=s)
    assert result['state']=='outside-model-domain' and 'battery' in result['reason']


def test_launch_hold_requires_explicit_supported_force_and_time_bounds():
    b=bundle();s=case(b,initial_current_A=0.,rolling_coefficient=.0025,bearing_N_per_car=5.)
    x=models(b);x['launch_hold']['declared']=True;reseal(x)
    m=force_map(b,s);m['electrical_limits']['current_slew_A_s']=1.;m=seal(m)
    result=p.method_test(b,m,x,scenario_overrides=s)
    assert result['trace'][0]['launch_hold_active']
    assert any(not r['launch_hold_active'] for r in result['trace'])
    assert result['trace'][0]['position_m']==0.
    assert result['trace'][0]['launch_hold_restraint_N_train']>0.
    assert not result['physical_journey_completed']


def test_fmi_types_units_and_sources_are_interfaces_not_executed_models():
    b=bundle();m=dict(schema='osr-reference-cell-FMI-exchange/1',candidate_id=b['candidate_id'],
        ports=[dict(name=k,type=v[0],unit=v[1],causality=v[2]) for k,v in p.FMI_PORTS.items()],
        models=[dict(sha256='a'*64,source_identity='b'*64,model_identifier='test-only-fmu')])
    m['manifest_id']=identity(m)
    result=p.fmi_manifest(b,m)
    assert result['interface_valid'] and result['execution']=='not-run' and not result['models_verified']
    m['ports'][0]['unit']='km';m['manifest_id']=identity({k:v for k,v in m.items() if k!='manifest_id'})
    with pytest.raises(ValueError,match='port'):p.fmi_manifest(b,m)


def coupled_record_fixture():
    """Trusted in-process replay fixtures; never physical or project trust records."""
    b=model.materialize()['bundle'];s=system_motion.scenario(b);x=models(b);records=[]
    current=p.sources();source={p.PRODUCER:current[p.PRODUCER]}
    for scope,protocol in p.MODEL_SCOPES.items():
        request=dict(candidate_id=b['candidate_id'],scope=scope,model_id=x['model_id'],scenario_id=s['scenario_id'],
            source_sha256=source,tool_identity={'test-only':'fixture'},numerical_request={'method_test_only':True})
        data=dict(scope=scope,model_id=x['model_id'],scenario_id=s['scenario_id'],artifact_request=request,output_evaluation_id=identity(['fixture',scope]))
        record=dict(schema='osr-wheel-operating-evidence/1',**p.evidence.binding(b),data=data)
        record['record_id']=identity(record)
        records.append(dict(authenticated=True,protocol_id=protocol,candidate_id=b['candidate_id'],record_id=record['record_id'],record=record))
        x['supporting_record_ids'][scope]=record['record_id']
    assert p.model_payload_id(x)==x['model_id']
    def replay(r,*args):
        d=r['data'];request=d['artifact_request']
        return dict(verified=True,record_id=r['record_id'],scope=d['scope'],tool_request_id=identity(request),
            source_sha256=request['source_sha256'],tool_identity=request['tool_identity'],output_evaluation_id=d['output_evaluation_id'])
    return b,s,x,records,current,replay


def test_coupled_support_identity_avoids_cycles_and_replay_binds_actual_model():
    b,s,x,records,current,replay=coupled_record_fixture()
    assert p._model_admission(b,x,s,None,records,replay,current)==[]
    x['auxiliary']['HVAC_W']+=100.;reseal(x)
    assert len(p._model_admission(b,x,s,None,records,replay,current))==4


def test_coupled_supported_strings_do_not_replace_external_replay():
    b,s,x,records,current,replay=coupled_record_fixture()
    reasons=p._model_admission(b,x,s,None,records,None,current)
    assert len(reasons)==4 and all('replay backend missing' in r for r in reasons)


@pytest.mark.parametrize('mutation',[
    lambda a:a.update(authenticated=False),
    lambda a:a.update(protocol_id='T10'),
    lambda a:a.update(candidate_id='f'*64),
    lambda a:a['record']['data'].update(output_evaluation_id=None),
])
def test_resealed_coupled_evidence_cannot_inherit_wrong_scope_or_provenance(mutation):
    b,s,x,records,current,replay=coupled_record_fixture();a=records[0];scope=a['record']['data']['scope']
    mutation(a)
    a['record']['record_id']=identity({k:v for k,v in a['record'].items() if k!='record_id'})
    a['record_id']=a['record']['record_id'];x['supporting_record_ids'][scope]=a['record_id']
    assert p._model_admission(b,x,s,None,records,replay,current)
