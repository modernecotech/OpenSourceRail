"""Operating-inlet method tests; no fixture is an actual available motor map.

Authenticated assessments and replay callbacks below are supplied by this test
process only. They do not install project trust, qualify hardware or demonstrate
a physically supported journey.
"""
from copy import deepcopy
from itertools import product
from math import exp

import pytest

from engineering.railway_completion import operating as op
from engineering.railway_twin import model
from engineering.design_search import system_motion
from engineering.design_search import railway_bundle
from engineering.station_rail.common import identity


@pytest.fixture(scope='module')
def actual_bundle():
    return model.materialize()['bundle']


@pytest.fixture(scope='module')
def bundle(actual_bundle):
    """A separately identified, test-only thermal installation hypothesis."""
    b=deepcopy(actual_bundle)
    case=b['architecture_case'];physical=case['physical_definition']
    names=[row['id'] for row in duty_fixture()['nodes']]
    physical['wayside']['converter_and_feeder_definition']=dict(
        thermal_node_ids=names,converter_node_ids=[name for name in names if name.startswith('converter/')],
        test_fixture_only=True)
    candidate=identity(physical)
    case['candidate_id']=candidate
    case['capability_composition']['candidate_id']=candidate
    case['case_id']=identity({k:v for k,v in case.items() if k!='case_id'})
    b.update(candidate_id=candidate,bundle_id=candidate)
    b['brake_definition']['candidate_id']=candidate
    b['brake_definition']['brake_definition_id']=identity({k:v for k,v in b['brake_definition'].items() if k!='brake_definition_id'})
    b['definition_id']=identity({k:v for k,v in b.items() if k!='definition_id'})
    return railway_bundle.validate(b)


def seal(value):
    value=deepcopy(value)
    value['evaluation_id']=identity({k:v for k,v in value.items() if k!='evaluation_id'})
    return value


def map_fixture(bundle,*,scenario=None):
    """Algebraic data for inlet tests only, not finite-element motor output."""
    case=scenario or system_motion.scenario(bundle)
    positions=sorted({0.,250.,case['distance_m'],*[edge for pair in case['powered_windows'] for edge in pair]})
    axes=dict(position_m=positions,speed_m_s=[0.,20.],
              current_A=[0.,10.],temperature_C=[20.,80.])
    samples=[]
    for x,v,current,temp in product(*(axes[name] for name in system_motion.AXES)):
        active=any(a<=x<b for a,b in case['powered_windows'])
        force=6000.*current if active else 0.
        loss=current*current if active else 0.
        samples.append(dict(zip(system_motion.AXES,(x,v,current,temp)),
            thrust_N_train=force,electrical_input_W_train=force*v+loss,loss_W_train=loss,
            voltage_V=100. if active and current else 0.,vertical_force_N_train=0.))
    value=dict(schema='osr-station-available-force-map/1',candidate_id=bundle['candidate_id'],
        motor_component_id=bundle['propulsion_component_id'],scenario_id=case['scenario_id'],
        evidence_kind='verified-numerical-operating-map',model_family='nonlinear-moving-LIM',
        execution='completed',numerical_validity='converged',model_domain='supported',
        source_sha256=deepcopy(bundle['source_sha256']),powered_windows=case['powered_windows'],axes=axes,samples=samples,
        electrical_limits=dict(maximum_voltage_V=750.,maximum_current_A=20.,current_slew_A_s=1000.),
        thermal_model=dict(capacity_J_K=1e6,ambient_C=20.,initial_C=20.,maximum_C=80.,heat_rejection_W_K=10.),
        operating_envelope=dict(interface_state=op.interface(bundle),
            history_model='validated-zero-flux-start-and-isolation-envelope',
            frequency_control_law='UNIT-TEST-FIXTURE-NOT-AN-OPERATING-CONTROLLER',
            phase_registration='UNIT-TEST-FIXTURE-NOT-A-WINDING-APPROVAL',
            gap_each_side_m=bundle['motor_parameters']['physical']['gap_each_side_m']),
        interface_state_id=identity(op.interface(bundle)),supporting_record_ids={},review_record_id=None,
        validation={name:'supported' for name in op.REQUIRED})
    return case,seal(value)


def rc_node(name,*,power=10.,maximum=100.):
    return dict(id=name,mass_kg=10.,specific_heat_J_kg_K=100.,resistance_K_W=2.,
        ambient_C=20.,maximum_C=maximum,phases=[dict(duration_s=60.,loss_W=power),dict(duration_s=60.,loss_W=0.)])


def duty_fixture():
    names=[f'bank/{i}/winding' for i in range(5)]
    names += [f'secondary/{i}' for i in range(6)]
    names += [f'converter/{i}' for i in range(5)]
    return dict(headway_s=120.,nodes=[rc_node(name) for name in names])


def support_fixture(bundle,case,force_map):
    """Test-only assessment registry and independent application callback."""
    value=deepcopy(force_map);dataset=op.payload_id(value);assessments=[]
    for scope,protocol in op.REQUIRED.items():
        data=dict(scope=scope,map_payload_id=dataset,interface_state_id=identity(op.interface(bundle)),
                  scenario_id=case['scenario_id'],test_fixture_only=True)
        source=deepcopy(bundle['source_sha256'])
        artifact_request=dict(scope=scope,candidate_id=bundle['candidate_id'],
            motor_component_id=bundle['propulsion_component_id'],map_payload_id=dataset,
            scenario_id=case['scenario_id'],source_sha256=source,
            tool_identity=dict(kind='UNIT-TEST-METHOD-ONLY',version='0'),
            numerical_request=dict(unit_test_fixture_only=True,scenario_id=case['scenario_id']))
        data.update(artifact_request=artifact_request,
            output_evaluation_id=identity(dict(test_only='NO-ACTUAL-SOLVER',scope=scope,dataset=dataset)))
        if scope=='thermal_duty':
            data.update(duty=duty_fixture(),required_node_ids=[n['id'] for n in duty_fixture()['nodes']])
        record=dict(schema='osr-wheel-operating-evidence/1',candidate_id=bundle['candidate_id'],
            bundle_definition_id=bundle['definition_id'],body_candidate_id=bundle['body_candidate_id'],
            requirement_revision=bundle['requirement_revision'],source_sha256=deepcopy(bundle['source_sha256']),
            data=data,**op.FLAGS)
        record['record_id']=identity(record)
        value['supporting_record_ids'][scope]=record['record_id']
        assessments.append(dict(record_id=record['record_id'],candidate_id=bundle['candidate_id'],protocol_id=protocol,
            authenticated=True,state='authenticated-for-declared-scope',record=record,
            physical_protocol_screen_passed=False,**op.FLAGS))
    value['review_record_id']=assessments[0]['record_id']
    value=seal(value)
    def method_test_backend(record,actual_bundle,actual_case,actual_map):
        assert record['data']['test_fixture_only'] is True
        assert actual_bundle['candidate_id']==bundle['candidate_id']
        assert actual_case['scenario_id']==case['scenario_id']
        assert op.payload_id(actual_map)==dataset
        return dict(verified=True,record_id=record['record_id'],scope=record['data']['scope'],
            map_payload_id=dataset,source_sha256=deepcopy(record['data']['artifact_request']['source_sha256']),
            tool_identity=deepcopy(record['data']['artifact_request']['tool_identity']),
            tool_request_id=identity(record['data']['artifact_request']),
            output_evaluation_id=record['data']['output_evaluation_id'])
    return value,assessments,method_test_backend


def test_missing_map_never_becomes_a_demand_driven_journey(bundle):
    case=system_motion.scenario(bundle)
    gate=op.admit(bundle,None,case)
    assert not gate['admitted'] and not gate['evidence_ready']
    result=op.evaluate(bundle)
    assert result['forward_motion']['execution']=='not-run'
    assert not result['numerical_arrival_predicted'] and not result['protected_service_qualified']
    assert all(result[key] is False for key in op.FLAGS)


def test_payload_identity_excludes_review_links_but_retains_dataset_and_interface(bundle):
    case,value=map_fixture(bundle)
    linked,records,backend=support_fixture(bundle,case,value)
    assert op.payload_id(linked)==op.payload_id(value)
    for key in ('review_record_id','supporting_record_ids','validation','evaluation_id'):
        changed=deepcopy(linked);changed[key]='changed-review-metadata'
        assert op.payload_id(changed)==op.payload_id(value)
    changed=deepcopy(value);changed['samples'][0]['voltage_V']=1.
    assert op.payload_id(changed)!=op.payload_id(value)


def test_supported_strings_and_hash_shaped_reviews_do_not_replace_resolved_records(bundle):
    case,value=map_fixture(bundle)
    value.update(review_record_id='a'*64,supporting_record_ids={scope:'b'*64 for scope in op.REQUIRED})
    result=op.admit(bundle,seal(value),case)
    assert not result['admitted']
    assert any('record' in reason for reason in result['reasons'])


@pytest.mark.parametrize('voltage',[-1.,-1e6,751.])
def test_negative_or_over_bus_voltage_magnitude_rejected_before_evidence_lookup(bundle,voltage):
    case,value=map_fixture(bundle)
    value['samples'][0]['voltage_V']=voltage
    with pytest.raises(ValueError,match='voltage'):
        op.admit(bundle,seal(value),case)


def test_samples_must_fit_current_magnitude_limits(bundle):
    case,value=map_fixture(bundle)
    value['electrical_limits']['maximum_current_A']=5.
    with pytest.raises(ValueError,match='current'):
        op.admit(bundle,seal(value),case)


@pytest.mark.parametrize('kind',['force','input','loss'])
def test_off_window_force_electrical_input_or_heat_is_not_silently_discarded(bundle,kind):
    case,value=map_fixture(bundle)
    row=next(r for r in value['samples'] if r['position_m']==case['distance_m'] and r['current_A']==10. and r['speed_m_s']==0.)
    if kind=='force':row['thrust_N_train']=1.
    else:row['electrical_input_W_train']=row['loss_W_train']=1.
    with pytest.raises(ValueError,match='off-window'):
        op.admit(bundle,seal(value),case)


def test_zero_current_force_and_unbalanced_power_are_rejected(bundle):
    case,value=map_fixture(bundle)
    row=value['samples'][0];row['thrust_N_train']=1.
    with pytest.raises(ValueError,match='zero current'):
        op.admit(bundle,seal(value),case)
    case,value=map_fixture(bundle);value['samples'][0]['electrical_input_W_train']=100.
    with pytest.raises(ValueError,match='identity'):
        op.admit(bundle,seal(value),case)


@pytest.mark.parametrize('kind',['incomplete','duplicate','synthetic','wrong-schema'])
def test_incomplete_duplicate_or_unsupported_maps_are_rejected(bundle,kind):
    case,value=map_fixture(bundle)
    if kind=='incomplete':value['samples'].pop()
    elif kind=='duplicate':value['samples'][-1]=deepcopy(value['samples'][0])
    elif kind=='synthetic':value['evidence_kind']='synthetic-method-test'
    else:value['schema']='osr-generic-DC-method/1'
    with pytest.raises(ValueError):op.admit(bundle,seal(value),case)


def test_resolved_assessments_still_need_an_independent_application_backend(bundle):
    case,value=map_fixture(bundle);value,records,backend=support_fixture(bundle,case,value)
    gate=op.admit(bundle,value,case,assessments=records)
    assert not gate['admitted']
    assert any('backend' in reason for reason in gate['reasons'])


def test_method_fixture_can_exercise_admission_without_physical_or_operating_release(bundle):
    case,value=map_fixture(bundle);value,records,backend=support_fixture(bundle,case,value)
    gate=op.admit(bundle,value,case,assessments=records,artifact_verifier=backend)
    assert gate['admitted'] and gate['evidence_ready']
    assert len(gate['replayed_evidence'])==len(op.REQUIRED)
    assert all(gate[key] is False for key in op.FLAGS)


def change_support(value,records,scope,mutate):
    value=deepcopy(value);records=deepcopy(records)
    row=next(r for r in records if r['record_id']==value['supporting_record_ids'][scope])
    previous=row['record_id']
    mutate(row)
    record=row['record']
    record['record_id']=identity({k:v for k,v in record.items() if k!='record_id'})
    row['record_id']=record['record_id']
    value['supporting_record_ids'][scope]=record['record_id']
    if value['review_record_id']==previous:
        value['review_record_id']=record['record_id']
    return seal(value),records


@pytest.mark.parametrize('key,value',[('candidate_id','a'*64),('motor_component_id','b'*64),('scenario_id','c'*64)])
def test_cross_candidate_motor_or_scenario_map_is_rejected(bundle,key,value):
    case,data=map_fixture(bundle)
    data[key]=value
    data,records,backend=support_fixture(bundle,case,seal(data))
    gate=op.admit(bundle,data,case,assessments=records,artifact_verifier=backend)
    assert not gate['admitted']


@pytest.mark.parametrize('change',['record-candidate','record-source','assessment-candidate','wrong-protocol','quote-schema','wrong-map'])
def test_authenticated_records_must_still_match_exact_scope_and_candidate(bundle,change):
    case,value=map_fixture(bundle);value,records,backend=support_fixture(bundle,case,value)
    def mutate(assessment):
        record=assessment['record']
        if change=='record-candidate':record['candidate_id']='d'*64
        elif change=='record-source':record['source_sha256']={'unrelated.py':'e'*64}
        elif change=='assessment-candidate':assessment['candidate_id']='f'*64
        elif change=='wrong-protocol':assessment['protocol_id']='T10'
        elif change=='quote-schema':record['schema']='osr-completion-domain-record/1'
        else:record['data']['map_payload_id']='0'*64
    value,records=change_support(value,records,'independent_benchmarks',mutate)
    gate=op.admit(bundle,value,case,assessments=records,artifact_verifier=backend)
    assert not gate['admitted']


@pytest.mark.parametrize('field,wrong',[
    ('verified',False),('record_id','a'*64),('scope','unrelated-method'),
    ('map_payload_id','b'*64),('source_sha256',{'wrong.py':'c'*64}),
    ('tool_request_id','d'*64),('tool_identity',{'kind':'UNRELATED'}),('output_evaluation_id','e'*64),
])
def test_application_replay_output_must_match_the_entire_declared_request(bundle,field,wrong):
    case,value=map_fixture(bundle);value,records,backend=support_fixture(bundle,case,value)
    def altered(*args):
        result=backend(*args);result[field]=wrong;return result
    gate=op.admit(bundle,value,case,assessments=records,artifact_verifier=altered)
    assert not gate['admitted']
    assert any('replay' in reason for reason in gate['reasons'])


def test_stale_declared_solver_source_cannot_be_replayed_under_current_sources(bundle):
    case,value=map_fixture(bundle);value,records,backend=support_fixture(bundle,case,value)
    def mutate(assessment):
        request=assessment['record']['data']['artifact_request']
        name=next(iter(request['source_sha256']))
        request['source_sha256'][name]='0'*64
    value,records=change_support(value,records,'mesh_time_convergence',mutate)
    gate=op.admit(bundle,value,case,assessments=records,artifact_verifier=backend)
    assert not gate['admitted']
    assert any('source' in reason for reason in gate['reasons'])


def test_default_project_has_no_thermal_installation_to_inherit_from_method_fixture(actual_bundle):
    case,value=map_fixture(actual_bundle);value,records,backend=support_fixture(actual_bundle,case,value)
    gate=op.admit(actual_bundle,value,case,assessments=records,artifact_verifier=backend)
    assert not gate['admitted']
    assert any('thermal' in reason for reason in gate['reasons'])


@pytest.mark.parametrize('prefix',['bank/4','secondary/5','converter/'])
def test_missing_declared_thermal_nodes_cannot_be_hidden_by_rescoping_required_ids(bundle,prefix):
    case,value=map_fixture(bundle);value,records,backend=support_fixture(bundle,case,value)
    def mutate(assessment):
        data=assessment['record']['data']
        data['duty']['nodes']=[n for n in data['duty']['nodes'] if not n['id'].startswith(prefix)]
        data['required_node_ids']=[n['id'] for n in data['duty']['nodes']]
    value,records=change_support(value,records,'thermal_duty',mutate)
    gate=op.admit(bundle,value,case,assessments=records,artifact_verifier=backend)
    assert not gate['admitted']
    assert any('thermal' in reason for reason in gate['reasons'])


def test_admitted_method_fixture_remains_an_unqualified_force_driven_calculation(bundle):
    overrides=dict(maximum_time_s=.1,rolling_coefficient=0.,bearing_N_per_car=0.,aero_N_s2_m2_per_car=0.)
    case=system_motion.scenario(bundle,overrides)
    case,value=map_fixture(bundle,scenario=case);value,records,backend=support_fixture(bundle,case,value)
    result=op.evaluate(bundle,value,scenario_overrides=overrides,assessments=records,artifact_verifier=backend)
    assert result['map_admission']['admitted']
    assert result['forward_motion']['execution']=='completed-reduced-model'
    assert result['forward_motion']['state']=='stalled'
    assert not result['numerical_arrival_predicted'] and not result['protected_service_qualified']
    assert all(result[key] is False for key in op.FLAGS)


def test_position_grid_cannot_hide_nonzero_interpolation_outside_a_powered_window(bundle):
    case,value=map_fixture(bundle)
    value['axes']['position_m'].remove(500.)
    value['samples']=[row for row in value['samples'] if row['position_m']!=500.]
    value,records,backend=support_fixture(bundle,case,seal(value))
    interpolated=system_motion.sample_map(value,position_m=600.,speed_m_s=0.,current_A=10.,temperature_C=20.)
    assert interpolated['thrust_N_train']>0
    with pytest.raises(ValueError,match='window|position|boundar'):
        op.admit(bundle,value,case,assessments=records,artifact_verifier=backend)


def test_power_window_right_boundary_is_zero_before_the_next_interpolation_cell(bundle):
    case,value=map_fixture(bundle)
    row=next(r for r in value['samples'] if r['position_m']==500. and r['current_A']==10. and r['speed_m_s']==0.)
    row['thrust_N_train']=1.
    with pytest.raises(ValueError,match='window|position|boundar'):
        op.admit(bundle,seal(value),case)


def test_periodic_rc_solution_matches_independent_closed_form():
    node=rc_node('bank/0',power=10.)
    result=op.periodic_duty(dict(headway_s=120.,nodes=[node]))['nodes'][0]
    a=exp(-60./2000.)
    initial=20.*a/(1+a)
    peak=20./(1+a)
    assert result['periodic_initial_C']==pytest.approx(20.+initial)
    assert result['periodic_peak_C']==pytest.approx(20.+peak)
    assert result['cycle_residual_K']==pytest.approx(0.,abs=1e-12)
    assert result['passes'] is True


def test_constant_heat_reaches_thermal_equilibrium_and_overtemperature_remains_failure():
    node=rc_node('converter/0',power=10.,maximum=39.)
    node['phases']=[dict(duration_s=120.,loss_W=10.)]
    result=op.periodic_duty(dict(headway_s=120.,nodes=[node]))
    assert result['nodes'][0]['periodic_peak_C']==pytest.approx(40.)
    assert result['passes'] is False
    assert all(result[key] is False for key in op.FLAGS)


@pytest.mark.parametrize('change',['negative-heat','missing-nodes','duplicate-node','wrong-headway','incomplete-cycle'])
def test_invalid_thermal_duty_cannot_become_a_supported_cooling_system(change):
    value=dict(headway_s=120.,nodes=[rc_node('bank/0')])
    if change=='negative-heat':value['nodes'][0]['phases'][0]['loss_W']=-1.
    elif change=='missing-nodes':value['nodes']=[]
    elif change=='duplicate-node':value['nodes'].append(deepcopy(value['nodes'][0]))
    elif change=='wrong-headway':value['headway_s']=60.
    else:value['nodes'][0]['phases'][0]['duration_s']=59.
    with pytest.raises(ValueError):op.periodic_duty(value)
