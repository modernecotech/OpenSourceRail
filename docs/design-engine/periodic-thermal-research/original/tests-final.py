import gzip
import json
import math
from pathlib import Path

import pytest
from engineering.design_search import periodic_thermal_research as p


def test_loss_reconstruction_uses_midpoint_power_and_checks_temperature():
    thermal=dict(capacity_J_K=1000.,heat_rejection_W_K=100.,ambient_C=30.,initial_C=30.)
    trace=[dict(time_s=1.,temperature_C=30.2,speed_m_s=10.,
                electrical_input_W_train=300.,thrust_N_train=20.)]
    result=p.recover(trace,thermal,200.)
    assert result['intervals'][0]['loss_W']==pytest.approx(200.)
    assert result['signed_loss_J']==pytest.approx(200.)
    assert result['thermal_inversion_loss_J']==pytest.approx(200.)
    assert result['absolute_per_step_method_difference_J']<result['energy_budget_J']
    assert result['clipped_negative_energy_J']==0.


def test_small_signed_power_roundoff_is_recorded_but_real_negative_loss_rejected():
    thermal=dict(capacity_J_K=1000.,heat_rejection_W_K=100.,ambient_C=30.,initial_C=30.)
    row=dict(time_s=1.,temperature_C=30.,speed_m_s=10.,
        electrical_input_W_train=100.-1e-14,thrust_N_train=20.)
    result=p.recover([row],thermal,0.)
    assert result['clipped_negative_energy_J']>0.
    assert result['negative_step_count']==1
    assert result['intervals'][0]['loss_W']==0.
    row['electrical_input_W_train']=99.
    with pytest.raises(ValueError,match='negative reconstructed loss'):
        p.recover([row],thermal,0.)


def test_inconsistent_thermal_reconstruction_and_nonmonotonic_time_rejected():
    thermal=dict(capacity_J_K=1000.,heat_rejection_W_K=100.,ambient_C=30.,initial_C=30.)
    row=dict(time_s=1.,temperature_C=31.,speed_m_s=0.,electrical_input_W_train=100.,thrust_N_train=0.)
    with pytest.raises(ValueError,match='thermal check'):
        p.recover([row],thermal,100.)
    row['time_s']=0.
    with pytest.raises(ValueError,match='increasing'):
        p.recover([row],thermal,100.)


def test_exact_periodic_recurrence_conserves_energy_and_counts_prelaunch_once():
    pulse=[dict(start_s=0.,end_s=1.,loss_W=100.)]
    result=p.periodic(pulse,10.,1000.,100.,30.,4.,.1,prelaunch_s=1.)
    a=math.exp(-.1);a3=math.exp(-.3)
    expected=(.01*a+(1.-a))*a3/(1.-a**4)
    steady=result['steady_cycle']
    assert result['status']=='conditional-periodic-solution'
    assert steady['initial_C']==pytest.approx(30.+expected,abs=1e-10)
    assert steady['energy_in_J']==pytest.approx(110.)
    assert steady['cooling_rejected_J']==pytest.approx(110.,abs=1e-7)
    assert abs(steady['energy_residual_J'])<steady['energy_budget_J']
    assert abs(steady['closure_residual_C'])<1e-8
    assert abs(result['exact_cooling_subdivision_difference_C'])<1e-9


def test_rejection_is_the_independent_analytic_heat_transfer_integral():
    result=p.cycle([(0.,1.,100.)],0.,1000.,100.,30.,50.,1.)
    a=math.exp(-.1)
    expected=100.*(20.*(1-a)/.1 + 1.-(1-a)/.1)
    assert result['cooling_rejected_J']==pytest.approx(expected,abs=1e-10)
    assert abs(result['energy_residual_J'])<1e-9
    tiny=p.cycle([(0.,.001,10.)],0.,1000.,1e-12,30.,31.,1.)
    assert tiny['cooling_rejected_J']==pytest.approx(1e-15,rel=1e-6)
    assert math.isfinite(tiny['final_C'])


def test_tiny_positive_cooling_uses_stable_relative_affine_solution():
    pulse=[dict(start_s=0.,end_s=120.,loss_W=10.)]
    value=p.periodic(pulse,0.,1e8,1e-4,30.,120.,.05)
    assert value['status']=='conditional-periodic-solution'
    assert value['affine_one_minus_A']==pytest.approx(-math.expm1(-1.2e-10),rel=1e-14)
    assert value['steady_cycle']['peak_C']==pytest.approx(100030.,abs=1e-6)
    assert abs(value['steady_cycle']['closure_residual_C'])<1e-7


def test_segment_update_does_not_divide_power_by_tiny_conductance():
    value=p.cycle([(0.,1.,1e10)],0.,1000.,1e-320,30.,30.,1.)
    assert value['final_C']==pytest.approx(10_000_030.)
    assert math.isfinite(value['energy_residual_J'])
    with pytest.raises(ValueError,match='finite'):
        p.periodic([dict(start_s=0.,end_s=1.,loss_W=1e10)],0.,1000.,1e-320,30.,2.,1.)


def test_overlapping_pulses_are_folded_with_multiplicity():
    result=p.periodic([dict(start_s=0.,end_s=3.,loss_W=100.)],0.,1000.,100.,30.,2.,.25)
    # At steady phase [0,1) has two 100 W pulses; [1,2) has one.
    a=math.exp(-.1);start=(2*a+1)/(1+a)
    assert result['phase_max_simultaneous_nonzero_pulses']==2
    assert result['first_cycle']['energy_in_J']==pytest.approx(200.)
    assert result['steady_cycle']['energy_in_J']==pytest.approx(300.)
    assert result['steady_cycle']['initial_C']==pytest.approx(30.+start,abs=1e-10)
    assert result['steady_cycle']['cooling_rejected_J']==pytest.approx(300.,abs=1e-7)


def test_pulse_extending_across_multiple_headways_is_not_truncated():
    result=p.periodic([dict(start_s=0.,end_s=5.,loss_W=100.)],0.,1000.,100.,30.,2.,.1)
    assert result['phase_max_simultaneous_nonzero_pulses']==3
    assert result['first_cycle']['energy_in_J']==pytest.approx(200.)
    assert result['steady_cycle']['energy_in_J']==pytest.approx(500.)
    assert result['steady_cycle']['cooling_rejected_J']==pytest.approx(500.,abs=1e-7)


def test_cooling_suppressed_for_one_second_does_not_extend_period():
    pulse=[dict(start_s=0.,end_s=1.,loss_W=100.)]
    continuous=p.periodic(pulse,10.,1000.,100.,30.,4.,.1,prelaunch_s=1.)
    suppressed=p.periodic(pulse,10.,1000.,100.,30.,4.,.1,
        prelaunch_s=1.,suppress_cooling_during_prelaunch=True)
    assert continuous['headway_s']==suppressed['headway_s']==4.
    assert suppressed['steady_cycle']['peak_C']>continuous['steady_cycle']['peak_C']
    assert suppressed['steady_cycle']['energy_in_J']==pytest.approx(110.)
    assert suppressed['steady_cycle']['cooling_rejected_J']==pytest.approx(110.,abs=1e-7)


@pytest.mark.parametrize('pre,pulse,status', [
    (0.,[], 'no-unique-steady-state'),
    (1.,[], 'no-steady-state-positive-heat'),
    (0.,[dict(start_s=0.,end_s=3.,loss_W=5.)], 'no-steady-state-positive-heat'),
])
def test_zero_cooling_never_invents_a_unique_steady_temperature(pre,pulse,status):
    value=p.periodic(pulse,pre,1000.,0.,30.,2.,.1)
    assert value['status']==status
    assert value['steady_cycle'] is None


@pytest.mark.parametrize('energy,status', [
    (0.,'no-unique-steady-state'),(1.,'no-steady-state-positive-heat')])
def test_full_headway_prelaunch_suppression_has_no_effective_cooling(energy,status):
    value=p.periodic([],energy,1000.,100.,30.,2.,.1,
        prelaunch_s=2.,suppress_cooling_during_prelaunch=True)
    assert value['status']==status
    assert value['steady_cycle'] is None


def _seal(value,key):
    value[key]=p._id(value)
    return value


@pytest.fixture
def bound_input(tmp_path):
    source='engineering/design_search/original.py';raw=b'original producer\n'
    target=tmp_path/source;target.parent.mkdir(parents=True);target.write_bytes(raw)
    source_map={source:p._sha(raw)}
    def case(name,state):
        pre=dict(duration_s=1.,motor_loss_energy_J=10.)
        thermal=dict(capacity_J_K=1000.,heat_rejection_W_K=100.,ambient_C=30.,initial_C=30.01,maximum_C=120.)
        scenario=_seal(dict(powered_windows=[[0.,500.]],distance_m=2000.,berth_tolerance_m=2.),'scenario_id')
        axes=dict(position_m=[0.],speed_m_s=[0.],current_A=[0.],temperature_C=[30.,120.])
        samples=[dict(position_m=0.,speed_m_s=0.,current_A=0.,temperature_C=t,
            thrust_N_train=0.,electrical_input_W_train=0.,loss_W_train=0.,voltage_V=1.,vertical_force_N_train=0.)
            for t in axes['temperature_C']]
        force=_seal(dict(candidate_id=p.BUNDLE,evidence_kind='synthetic-method-test',thermal_model=thermal,
            axes=axes,samples=samples),'evaluation_id')
        trace=[dict(time_s=1.,temperature_C=30.209,position_m=1999.,speed_m_s=0.,electrical_input_W_train=200.,thrust_N_train=0.)]
        forward=_seal(dict(state=state,reason=None,execution='completed-method-test',
            final_position_m=1999.,final_speed_m_s=0.,predicted_stop_within_berth=True,
            test_only=True,available_motor_map_id=None,physical_accepted=False,engineering_accepted=False,
            configuration_adopted=False,manufacturing_release=False,operating_release=False,
            physical_journey_completed=False,trace=trace,elapsed_s=1.,temperature_C=30.209,magnetic_loss_energy_J=200.),'method_result_id')
        return dict(case=name,scenario=scenario,force_map=force,map_id=force['evaluation_id'],prelaunch=pre,
            forward=forward,test_only=True,available_motor_map_id=None,physical_journey_completed=False,
            trajectory_summary=dict(total_conditional_motor_loss_energy_J=210.))
    output=_seal(dict(candidate_id=p.BUNDLE,bundle_id=p.BUNDLE,reference_candidate_id=p.REFERENCE,
        powered_windows_m=[[0.,500.]],physical_accepted=False,engineering_accepted=False,
        engineering_validated=False,approved_for_manufacture_or_operation=False,
        configuration_adopted=False,manufacturing_release=False,operating_release=False,
        physical_journey_completed=False,cases=[case('low','stopped'),case('base','stopped'),
            case('high','controller-speed-limit')]),'evaluation_id')
    record=_seal(dict(bundle_id=p.BUNDLE,output=output),'record_id')
    artifact=gzip.compress(p._encoded(record),mtime=0);target=tmp_path/p.ARTIFACT
    target.parent.mkdir(parents=True);target.write_bytes(artifact)
    manifest=_seal(dict(schema='osr-conditional-journey-publication/2',study_id='1'*64,
        source_sha256=source_map,files_sha256={'candidates/'+p.BUNDLE+'.json.gz':p._sha(artifact)},
        physical_accepted=False,engineering_accepted=False,manufacturing_release=False,
        operating_release=False,configuration_adopted=False,physical_journey_completed=False),'manifest_id')
    (tmp_path/p.MANIFEST).write_bytes(p._encoded(manifest))
    request=dict(schema='osr-periodic-thermal-request/1',reference_candidate_id=p.REFERENCE,bundle_id=p.BUNDLE,
        record_id=record['record_id'],output_evaluation_id=output['evaluation_id'],study_manifest_id=manifest['manifest_id'],
        study_id='1'*64,candidate_artifact_sha256=p._sha(artifact),source_epoch_id=p._id(source_map),
        headway_s=120.,maximum_step_s=.05)
    return tmp_path,request,p._id(request)


def test_bound_research_preserves_early_termination_and_false_qualification(bound_input):
    root,request,request_id=bound_input
    value=p.evaluate(root,request,expected_request_id=request_id)
    assert len(value['cases'])==3
    assert value['cases'][2]['periodic']==dict(status='held-incomplete-trajectory',
        reason='controller-speed-limit',first_cycle=None,steady_cycle=None)
    assert value['cases'][0]['periodic']['continuous_cooling']['status']=='conditional-periodic-solution'
    assert value['cases'][0]['temperature_grid']['temperature_independent_at_sampled_nodes'] is True
    assert value['cases'][0]['periodic']['continuous_cooling']['model_domain']['within_declared_temperature_domain'] is True
    assert all(value[k] is False for k in ('physical_accepted','engineering_accepted','configuration_adopted',
        'selected_reference_changed','manufacturing_release','operating_release','physical_journey_completed'))
    assert value['available_motor_map_id'] is None


def test_external_pins_reject_changed_request_source_and_candidate(bound_input):
    root,request,request_id=bound_input
    changed=dict(request,headway_s=100.)
    with pytest.raises(ValueError,match='request identity'):
        p.evaluate(root,changed,expected_request_id=request_id)
    source=root/'engineering/design_search/original.py';original=source.read_bytes();source.write_bytes(b'tampered')
    with pytest.raises(ValueError,match='producer source'):
        p.evaluate(root,request,expected_request_id=request_id)
    source.write_bytes(original)
    path=root/p.ARTIFACT;path.write_bytes(path.read_bytes()+b'tampered')
    with pytest.raises(ValueError,match='candidate payload'):
        p.evaluate(root,request,expected_request_id=request_id)


def test_external_request_rejects_physical_candidate_relabel(bound_input):
    root,request,request_id=bound_input
    changed=dict(request,bundle_id='f'*64)
    with pytest.raises(ValueError,match='Exact selected'):
        p.evaluate(root,changed,expected_request_id=p._id(changed))


def test_stopped_train_outside_berth_cannot_supply_periodic_pulse():
    scenario=dict(distance_m=2000.,berth_tolerance_m=2.)
    result=dict(state='stopped',reason=None,execution='completed-method-test',
        predicted_stop_within_berth=True,final_position_m=1800.,final_speed_m_s=0.)
    assert p._completion_reason(result,scenario)=='stopped-outside-declared-berth'
    result['final_position_m']=1999.
    assert p._completion_reason(result,scenario) is None
    result['predicted_stop_within_berth']=False
    assert p._completion_reason(result,scenario)=='stopped-outside-declared-berth'


def test_temperature_domain_exceedance_holds_extrapolation():
    pulse=[dict(start_s=0.,end_s=1.,loss_W=1000.)]
    value=p._domain(p.periodic(pulse,0.,1000.,1.,30.,2.,.1),30.,120.)
    assert value['status']=='held-model-domain-exceeded'
    assert value['equilibrium_status']=='conditional-periodic-solution'
    assert value['model_domain']['within_declared_temperature_domain'] is False
    assert value['steady_cycle']['peak_C']>120.


def test_temperature_dependent_grid_is_not_claimed_independent(bound_input):
    root,request,request_id=bound_input
    record,manifest=p._inputs(root,request)
    fmap=record['output']['cases'][0]['force_map']
    assert p._temperature_grid(fmap)['temperature_independent_at_sampled_nodes'] is True
    fmap['samples'][1]['loss_W_train']=1.
    assert p._temperature_grid(fmap)['temperature_independent_at_sampled_nodes'] is False


def test_short_headway_reports_suppressed_branch_hold_without_masking(bound_input):
    root,request,_=bound_input
    changed=dict(request,headway_s=1.)
    value=p.evaluate(root,changed,expected_request_id=p._id(changed))
    result=value['cases'][0]['periodic']
    assert result['status']=='held-one-or-more-thermal-hypotheses'
    assert result['branch_dispositions']==dict(continuous_cooling='conditional-periodic-solution',
        prelaunch_cooling_suppressed='no-steady-state-positive-heat')


@pytest.mark.parametrize('flag', ['physical_accepted','engineering_accepted','manufacturing_release',
    'operating_release','configuration_adopted','physical_journey_completed','selected_reference_changed'])
def test_resealed_promoting_source_manifest_is_rejected(bound_input,flag):
    root,request,request_id=bound_input
    path=root/p.MANIFEST;manifest=json.loads(path.read_bytes());manifest.pop('manifest_id')
    manifest[flag]=True;_seal(manifest,'manifest_id');path.write_bytes(p._encoded(manifest))
    changed=dict(request,study_manifest_id=manifest['manifest_id'])
    with pytest.raises(ValueError,match='cannot promote'):
        p.evaluate(root,changed,expected_request_id=p._id(changed))


def test_resealed_synthetic_case_cannot_claim_a_nested_available_motor_map(bound_input):
    root,request,request_id=bound_input
    artifact_path=root/p.ARTIFACT;record=json.loads(gzip.decompress(artifact_path.read_bytes()))
    output=record['output'];forward=output['cases'][0]['forward']
    forward['available_motor_map_id']='f'*64;forward.pop('method_result_id');_seal(forward,'method_result_id')
    output.pop('evaluation_id');_seal(output,'evaluation_id')
    record.pop('record_id');_seal(record,'record_id')
    artifact=gzip.compress(p._encoded(record),mtime=0);artifact_path.write_bytes(artifact)
    manifest_path=root/p.MANIFEST;manifest=json.loads(manifest_path.read_bytes())
    manifest['files_sha256']['candidates/'+p.BUNDLE+'.json.gz']=p._sha(artifact)
    manifest.pop('manifest_id');_seal(manifest,'manifest_id');manifest_path.write_bytes(p._encoded(manifest))
    changed=dict(request,record_id=record['record_id'],output_evaluation_id=output['evaluation_id'],
        candidate_artifact_sha256=p._sha(artifact),study_manifest_id=manifest['manifest_id'])
    with pytest.raises(ValueError,match='Synthetic, non-promoting'):
        p.evaluate(root,changed,expected_request_id=p._id(changed))
