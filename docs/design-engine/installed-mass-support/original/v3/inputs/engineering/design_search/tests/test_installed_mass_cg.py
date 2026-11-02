"""Selected-candidate static sensitivity: accounting and physical limits."""
from copy import deepcopy
import json
import math

import pytest

from engineering.design_search import installed_mass_cg as m


@pytest.fixture(scope='module')
def inputs():
    return m.load_inputs()


def test_published_reference_with_independent_base_calculation(inputs):
    result=m.evaluate()
    assert result['candidate_id']==m.CANDIDATE_ID
    assert result['worksheet_id']==m.WORKSHEET_ID
    assert result['complete_installed_mass_kg'] is None
    assert result['installed_cg_m'] is None and result['axle_reactions_N'] is None
    assert result['account_overlap_resolved'] is False
    assert all(result[k] is False for k in m.FLAGS)
    low,base,high=result['cases']
    assert [case['scenario_accounted_mass_kg'] for case in (low,base,high)] == pytest.approx(
        [17203.958216173272,19221.998134341986,21240.038052510696])
    assert base['x_cg_interval_m'] == pytest.approx([-4.462709109915217,4.461097449917876])
    assert base['right_bogie_force_interval_N'] == pytest.approx([28530.151177841002,159949.5221855192])
    assert base['left_bogie_force_interval_N'] == pytest.approx([28553.859818625744,159973.2308263032])
    assert base['residual_replacement_mass_kg'] == pytest.approx(10090.199590843558)
    assert not base['possible_negative_reaction']
    assert m.evaluate()['evaluation_id']==result['evaluation_id']


def test_force_and_moment_equilibrium_at_correlated_endpoints(inputs):
    for case in m._evaluate_data(inputs)['cases']:
        assert sum(case['account_residual_mass_kg'].values())==pytest.approx(case['residual_replacement_mass_kg'])
        assert case['located_geometry_mass_kg']+case['residual_replacement_mass_kg']==pytest.approx(case['scenario_accounted_mass_kg'])
        for key in ('lower_cg_endpoint','upper_cg_endpoint'):
            p=case[key]
            assert p['left_bogie_force_N']+p['right_bogie_force_N']==pytest.approx(case['gravity_weight_N'])
            assert p['right_bogie_force_N']*12.8 == pytest.approx(case['gravity_weight_N']*(p['x_cg_m']+6.4))
            assert p['located_geometry_first_moment_kg_m']+p['residual_first_moment_kg_m']==pytest.approx(p['scenario_first_moment_kg_m'])
            assert p['scenario_first_moment_kg_m']==pytest.approx(case['scenario_accounted_mass_kg']*p['x_cg_m'])
            assert abs(p['force_residual_N'])<1e-9
            assert abs(p['moment_residual_N_m'])<1e-9


def test_partial_caller_intervals_tighten_only_matching_account(inputs):
    default=m.evaluate()
    narrowed=m.evaluate({'services':[-2.,1.]})
    assert narrowed['account_centroid_intervals']['services']['basis']=='caller supplied synthetic hypothesis'
    assert narrowed['account_centroid_intervals']['retained-comfort/body']['x_min_m']==-8.5
    for a,b in zip(default['cases'],narrowed['cases']):
        assert b['x_cg_interval_m'][0]>a['x_cg_interval_m'][0]
        assert b['x_cg_interval_m'][1]<a['x_cg_interval_m'][1]
        assert b['scenario_accounted_mass_kg']==a['scenario_accounted_mass_kg']
    assert narrowed['evaluation_id']!=default['evaluation_id']


def test_negative_support_is_reported_not_clipped(inputs):
    case=m._evaluate_data(inputs,{'services':[100,100]})['cases'][1]
    assert case['possible_negative_reaction']
    assert case['left_bogie_force_interval_N'][0]<0
    assert case['upper_cg_endpoint']['left_bogie_force_N']<0


@pytest.mark.parametrize('intervals',[{'typo':[0,1]},{'services':[0]},
    {'services':[2,1]},{'services':[float('nan'),1]},{'services':[0,float('inf')]},
    {'services':[False,1]}, {'services':[0, 1e300]}, {'services':[0, 10**1000]},
    [],{'services':'0,1'}])
def test_invalid_interval_is_rejected(inputs,intervals):
    with pytest.raises(ValueError):m._evaluate_data(inputs,intervals)


@pytest.mark.parametrize('change', ['candidate','selection','worksheet','duplicated_account','missing_account','added_residual','redistribution','negative_mass'])
def test_identity_and_account_mutations_are_rejected(inputs,monkeypatch,change):
    data=deepcopy(inputs)
    # Check the semantic guard independently of the pinned payload-hash guard.
    monkeypatch.setattr(m,'_identity',lambda *args: None)
    if change=='candidate': data['reserve']['candidate_id']='wrong'
    elif change=='selection': data['summary']['selection_id']='wrong'
    elif change=='worksheet': data['reserve']['worksheet_id']='wrong'
    elif change=='duplicated_account': data['reserve']['reserve_accounts'].append(deepcopy(data['reserve']['reserve_accounts'][0]))
    elif change=='missing_account': data['reserve']['reserve_accounts'].pop()
    elif change=='added_residual': data['reserve']['reserve_accounts'][0]['added_instead_of_replaced']=True
    elif change=='redistribution':
        rows=data['reserve']['reserve_accounts']
        rows[0]['scenario_reserve_kg']['base']+=1
        rows[1]['scenario_reserve_kg']['base']-=1
    else: data['reserve']['reserve_accounts'][0]['scenario_reserve_kg']['base']=-1
    with pytest.raises(ValueError):m._evaluate_data(data)


def test_mixed_source_pinning_and_payload_tamper_are_rejected(inputs,tmp_path):
    for name in m.INPUT_SHA256:
        target=tmp_path/name;target.parent.mkdir(parents=True,exist_ok=True)
        target.write_bytes((m.ROOT/name).read_bytes())
    (tmp_path/m.PRODUCER).parent.mkdir(parents=True,exist_ok=True)
    (tmp_path/m.PRODUCER).write_bytes((m.ROOT/m.PRODUCER).read_bytes())
    assert m.evaluate(root=tmp_path)['evaluation_id']==m.evaluate()['evaluation_id']
    (tmp_path/m.PRODUCER).write_text('tampered')
    with pytest.raises(ValueError,match='Executing producer differs'):m.evaluate(root=tmp_path)
    (tmp_path/m.PRODUCER).write_bytes((m.ROOT/m.PRODUCER).read_bytes())
    (tmp_path/m.BRIEF).write_text('tampered')
    with pytest.raises(ValueError,match='Pinned source differs'):m.evaluate(root=tmp_path)
    modified=deepcopy(inputs);modified['worksheet']['rows'][0]['account_id']='tampered'
    with pytest.raises(ValueError,match='payload does not reproduce'):m._evaluate_data(modified)


def test_occurrence_allocation_reconciles_per_account_not_only_globally(inputs,monkeypatch):
    data=deepcopy(inputs)
    rows=[r for r in data['worksheet']['rows'] if r['record_kind']=='candidate-geometry-occurrence']
    first=rows[0]
    second=next(r for r in rows if r['account_id']!=first['account_id']
                and r['candidate_geometry_mass_kg']!=first['candidate_geometry_mass_kg'])
    total=sum(r['candidate_geometry_mass_kg'] for r in rows)
    moment=sum(r['candidate_geometry_mass_kg']*r['candidate_geometry_centroid_m'][0] for r in rows)
    first['account_id'],second['account_id']=second['account_id'],first['account_id']
    assert sum(r['candidate_geometry_mass_kg'] for r in rows)==total
    assert sum(r['candidate_geometry_mass_kg']*r['candidate_geometry_centroid_m'][0] for r in rows)==moment
    # Isolate the per-account check from the earlier pinned source hash guard.
    monkeypatch.setattr(m,'_identity',lambda *args: None)
    with pytest.raises(ValueError,match='their own account'):m._evaluate_data(data)


def test_no_source_manifest_is_changed_by_running(inputs):
    result=m.evaluate()
    assert result['source_sha256']==m.INPUT_SHA256
    assert result['release_or_selection_effect'] is False
    assert 'not physical mass bounds' in result['scenario_assumptions'][-1]
    assert len(json.dumps(result,allow_nan=False))>0


def test_private_arithmetic_never_claims_source_byte_authentication(inputs):
    result=m._evaluate_data(inputs)
    assert 'source_sha256' not in result and 'producer_sha256' not in result
    assert 'input_authentication' not in result and 'evaluation_id' not in result
    for name in ('summary','brief'):
        modified=deepcopy(inputs)
        modified[name]['injected_unpinned_value']=True
        with pytest.raises(ValueError,match='Summary or parsed brief differs'):
            m._evaluate_data(modified)
