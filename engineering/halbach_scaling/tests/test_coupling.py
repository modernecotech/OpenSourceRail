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
    return dict(execution_status='completed',execution=dict(returncode=0,timed_out=False),evaluation_id='request',
                raw_result=dict(numerical_status='converged',result_id='result',environment={'solver':'fixture'}),
                comparison=dict(conservative_contour_Fz_N=force,demag_proxy_margin_A_per_m=margin,
                                next_experiment_sample_screen_pass=margin>=0,air_contour_relative_difference=0.))


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
        support_sensitivities=[{}, {},dict(observed_2D_headroom_N=1000,member_necessary_pass=True)])
    selected=c.select_experiments(magnets,bodies,[row])['selected'][0]
    assert selected['failed_or_unknown_necessary_screen'] is False
    row['support_sensitivities'][2]['member_necessary_pass']=False
    assert c.select_experiments(magnets,bodies,[row])['selected'][0]['failed_or_unknown_necessary_screen'] is True


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
