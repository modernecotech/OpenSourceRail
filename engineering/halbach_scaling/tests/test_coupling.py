from copy import deepcopy
from io import BytesIO
from pathlib import Path
import math
import os
import tarfile
import pytest
from engineering.halbach_scaling import coupling as c, candidates, vehicles, publication

ROOT=Path(os.environ.get('OSR_HALBACH_EVIDENCE_ROOT',candidates.ROOT))


def _point(force,margin=100.):
    return dict(candidate_id='m',execution_status='completed',execution=dict(returncode=0,timed_out=False),evaluation_id='request',
                raw_result=dict(numerical_status='converged',result_id='result',environment={'solver':'fixture'},operating_point={'gap_m':.012}),
                comparison=dict(conservative_contour_Fz_N=force,demag_proxy_margin_A_per_m=margin,
                                reported_contour_Fz_N=[force,force*1.1],next_experiment_sample_screen_pass=margin>=0,air_contour_relative_difference=0.))


def test_unexecuted_and_unsuccessful_worker_cannot_supply_force():
    assert c.force_point({'execution_status':'interrupted'}) is None
    for mutate in (lambda p:p.pop('execution'),lambda p:p['execution'].__setitem__('returncode',2),lambda p:p['execution'].__setitem__('timed_out',True)):
        p=_point(100.);mutate(p)
        with pytest.raises(ValueError,match='successful worker'):c.force_point(p)


def test_full_comparison_rejects_missing_duplicate_and_wrong_geometry():
    m=candidates.candidates(ROOT)[0]
    for rows in ([],[{'candidate_id':m['physical_id']},{'candidate_id':m['physical_id']}],
                 [dict(candidate_id=m['physical_id'],execution_status='completed',raw_result={})]):
        with pytest.raises(ValueError):c.comparison_rows([m],[],rows,root=ROOT)


def test_hot_cooling_and_plus_two_tonne_member_failures_cannot_win_selection():
    magnets=[dict(physical_id='D',parameters={'winding_layout':'differential','periods':1},stock={'magnet_volume_m3_per_module':.012},stock_parts=[])]
    bodies=[dict(candidate_id='v',thermal={'comparisons':[{}]})]
    row=dict(comparison_id='x',magnet_component_id='D',body_candidate_id='v',comparison_aw3_kg_per_car=30000,
        recipe_id='r',force_point=_point(30000),known_member_failure=False,next_capacity_experiment_eligible=True,
        sampled_peak_structure={'member_level_necessary_pass':True},
        support_sensitivities=[{}, {},dict(observed_2D_headroom_N=1000,member_necessary_pass=True)])
    selected=c.select_experiments(magnets,bodies,[row])['selected'][0]
    assert selected['failed_or_unknown_necessary_screen'] is False
    row['support_sensitivities'][2]['member_necessary_pass']=False
    assert c.select_experiments(magnets,bodies,[row])['selected']==[]
    row['support_sensitivities'][2]['member_necessary_pass']=True
    row['sampled_peak_structure']['member_level_necessary_pass']=None
    assert c.select_experiments(magnets,bodies,[row])['selected']==[]


def test_attachment_load_uses_larger_absolute_contour_not_smaller_capacity_force():
    point=_point(30000);point['comparison']['reported_contour_Fz_N']=[30000,-42000]
    observed=c.peak_force_points([point])['m']
    assert c.force_point(point)['force_N']==30000
    assert observed['observed_absolute_Fz_N_per_module']==42000
    assert observed['certified_fault_load_bound'] is False
    point['raw_result']['numerical_status']='nonconverged'
    assert c.peak_force_points([point])=={}


def test_gap_crossings_are_not_reserve_or_stable_hover_and_invalid_recoil_is_excluded():
    mass=dict(comparison_id='x',comparison_empty_kg_per_car=10000.,comparison_aw3_kg_per_car=22000.)
    selection={'selected':[dict(comparison_id='x',magnet_component_id='m',body_candidate_id='v')]}
    op={'rows':[dict(point=dict(candidate_id='m',temperature_C=80.,gap_m=g,current_A=0.),
                    result=_point(15000*math.exp(-40*(g-.012)))) for g in (.012,.028,.044,.060)]}
    p=c.gap_profiles(op,selection,[mass]);hot=next(q for q in p if q['temperature_C']==80)
    assert hot['loads'][1]['sampled_zero_current_crossing_brackets_m']==[[.012,.028]]
    assert hot['loads'][0]['sampled_zero_current_crossing_brackets_m']==[[.044,.060]]
    assert not hot['loads'][0]['stable_equilibrium_established']
    op['rows'][1]['result']=_point(op['rows'][1]['result']['comparison']['conservative_contour_Fz_N'],-1)
    hot=next(q for q in c.gap_profiles(op,selection,[mass]) if q['temperature_C']==80)
    assert hot['loads'][1]['sampled_zero_current_crossing_brackets_m']==[]


def test_finite_plan_proposes_new_force_evaluation_at_interpolated_gap():
    selection={'selected':[dict(purpose='controlled',comparison_id='x',magnet_component_id='m',body_candidate_id='v')]}
    mass=dict(comparison_id='x',comparison_aw3_kg_per_car=22000.)
    points=[dict(gap_m=g,force_N=15000*math.exp(-40*(g-.012)),necessary_point_screen_pass=True) for g in (.012,.028)]
    plan=c.finite_plan([dict(physical_id='m')],selection,[mass],[dict(candidate_id='m',temperature_C=80.,points=points)])
    target=.012+math.log(15000/(22000*c.G/24))/40
    assert plan[0]['gap_m']==.012 and plan[1]['gap_m']==pytest.approx(target,abs=1e-6)


def test_gap_proposal_cannot_interpolate_across_invalid_interior_sample():
    selection={'selected':[dict(purpose='controlled',comparison_id='x',magnet_component_id='m',body_candidate_id='v')]}
    points=[dict(gap_m=g,force_N=f,necessary_point_screen_pass=valid) for g,f,valid in
            [(.012,20000,True),(.028,None,False),(.044,5000,True)]]
    plan=c.finite_plan([dict(physical_id='m')],selection,[dict(comparison_id='x',comparison_aw3_kg_per_car=24000)],
                       [dict(candidate_id='m',temperature_C=80.,points=points)])
    assert plan[1]['proposal_method']=='nearest-valid-sample-no-accepted-crossing'
    assert plan[1]['gap_m'] in (.012,.044)


def test_reinforcement_changes_mass_comparison_without_relabelling_solved_component_pose():
    selection={'selected':[dict(purpose='controlled',comparison_id='x',magnet_component_id='m',body_candidate_id='reinforced')]}
    comparison=dict(comparison_id='x',support_sensitivities=[{}, {},dict(required_force_N_per_module=18000)])
    bundle={'physical_id':'m'};proposals=[dict(candidate=bundle,gap_m=.012),dict(candidate=bundle,gap_m=.035)]
    request=dict(candidates=[bundle,bundle],gaps_m=[.012,.036],request_id='field-request',temperature_C=80.,currents_A={})
    profiles=[dict(candidate_id='m',temperature_C=80.,points=[dict(gap_m=.012),dict(gap_m=.06)],
        loads=[dict(load_case='AW3',mean_weight_N_per_module=12000,sampled_zero_current_crossing_brackets_m=[[.028,.044]])])]
    result={'rows':[dict(case='capacity',evaluation_id='e0',state_id='pose0',force_credit=True,analysis={'air_contour_results':[{'force_N':[0,0,30000]},{'force_N':[0,0,32000]}]}),
                    dict(case='operating',evaluation_id='e1',state_id='pose1',force_credit=False)]}
    states=c.evaluated_finite_states(request,result,proposals,selection,[comparison],profiles)
    assert states[1]['gap_m']==.036 and states[1]['current_proposed_gap_m']==.035
    assert states[1]['differs_from_current_proposal'] is True
    assert states[0]['finite_minus_mean_weight_N']==[18000,20000]
    assert states[1]['finite_minus_mean_weight_N'] is None
    assert states[1]['current_body_candidate_id']=='reinforced'
    request['candidates'][1]={'physical_id':'other'}
    with pytest.raises(ValueError,match='physical candidates'):c.evaluated_finite_states(request,result,proposals,selection,[comparison],profiles)


@pytest.mark.parametrize('kind',['traversal','symlink','duplicate'])
def test_archive_reader_rejects_path_and_member_tricks(tmp_path,kind):
    archive=tmp_path/'bad.tar.gz'
    with tarfile.open(archive,'w:gz') as stream:
        item=tarfile.TarInfo('../escape' if kind=='traversal' else 'finite/data.json');item.size=2
        if kind=='symlink':item.type=tarfile.SYMTYPE;item.linkname='/etc/passwd';item.size=0
        stream.addfile(item,BytesIO(b'{}'))
        if kind=='duplicate':stream.addfile(item,BytesIO(b'{}'))
    target=tmp_path/'read';target.mkdir()
    with pytest.raises(ValueError):publication._extract(archive,target,'finite')
