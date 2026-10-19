"""Third physical pilot: actual parts, controlled variations and independent beam controls."""
from copy import deepcopy
import math
import pytest
from engineering.assembly_design import baseline,structural_bay as s
from engineering.twin_workflow import core
from engineering.design_consistency import contracts


@pytest.fixture
def policy():
    p=core.read(baseline.DATA);p['pilots']['structural-bay']=deepcopy(s.PILOT);return p


def candidate(policy,**changes):
    v=next(s.candidates(policy));v.update(changes);return s.build(policy,v)


def test_domain_has_twenty_four_repeatable_shape_and_assembly_variations(policy):
    recipes=list(s.candidates(policy));assert len(recipes)==24
    first=candidate(policy);second=s.build(policy,recipes[0])
    assert first==second
    assert first['requirement_ids']==['baghdad:ME-01']
    assert first['kind']=='structural-bay'
    assert all(first[k] is False for k in core.FLAGS)
    assert all(p['records']==[] and not p['accepted'] for p in first['qa_plan'])


def test_mass_cg_inertia_follow_every_represented_part(policy):
    c=candidate(policy);summary=contracts.summary(c['contract']);r=s.evaluate(policy,c)
    assert len(c['contract']['parts'])==30
    assert r['measurements']['mass_kg']==pytest.approx(sum(p['properties']['mass_kg'] for p in c['contract']['parts']))
    assert r['measurements']['cg_m']==pytest.approx(summary['cg_m'])
    assert r['measurements']['inertia_tensor_kg_m2']==summary['inertia_tensor_kg_m2']
    assert c['metadata']['steel_test_block_mass_kg']==pytest.approx(.4*.3*.04*7850)
    assert 'unrepresented' in ' '.join(r['open_requirements'])


def test_wall_change_changes_actual_mass_stiffness_stress_revision(policy):
    light=candidate(policy);thick=candidate(policy,rail_wall_m=.005)
    a=s.evaluate(policy,light);b=s.evaluate(policy,thick)
    assert thick['revision']!=light['revision']
    assert b['measurements']['mass_kg']>a['measurements']['mass_kg']
    assert b['measurements']['section_inertia_m4']>a['measurements']['section_inertia_m4']
    assert b['measurements']['beam_cases'][-1]['deflection_m']<a['measurements']['beam_cases'][-1]['deflection_m']
    assert b['measurements']['beam_cases'][-1]['stress_pa']<a['measurements']['beam_cases'][-1]['stress_pa']


def test_more_crossmembers_and_thicker_floor_add_geometry_and_mass(policy):
    base=candidate(policy);more=candidate(policy,crossmember_count=3);floor=candidate(policy,floor_thickness_m=.004)
    assert len(more['contract']['parts'])==len(base['contract']['parts'])+1
    assert more['metadata']['crossmember_positions_m']==[-.55,0.,.55]
    assert s.evaluate(policy,more)['measurements']['mass_kg']>s.evaluate(policy,base)['measurements']['mass_kg']
    assert s.evaluate(policy,floor)['measurements']['mass_kg']>s.evaluate(policy,base)['measurements']['mass_kg']
    assert len({base['revision'],more['revision'],floor['revision']})==3


def test_closed_form_refinement_equilibrium_and_adverse_scaling(policy):
    r=s.evaluate(policy,candidate(policy));a,b=r['measurements']['beam_cases']
    for case in (a,b):
        assert case['analytical_agreement_relative_error']<1e-7
        assert case['refinement_relative_change']<1e-7
        assert sum(v['force_z_n'] for v in case['support_reactions'])==pytest.approx(case['represented_mass_kg']*9.80665*case['acceleration_factor'])
        assert len(case['support_reactions'])==4
        assert case['boundary_sensitivity']['ratio']==pytest.approx(5.)
    assert b['deflection_m']==pytest.approx(3*a['deflection_m'])
    assert b['stress_pa']==pytest.approx(3*a['stress_pa'])
    assert not r['implemented_checks_pass'] and not r['screen_pass']
    assert 'detail/floor-strip/stress-provisional' in r['failed_checks']
    assert r['state']=='failed' and r['checks']['modal-acceptance'] is None
    assert r['checks']['shell-buckling'] is None and r['checks']['fatigue-spectrum'] is None
    assert not r['digital_specification_complete']


def test_every_non_external_part_is_connected_in_declared_loadpath(policy):
    c=candidate(policy);ids={p['id'] for p in c['contract']['parts']};connected=set()
    for joint in c['contract']['assembly_joints']:
        assert set(joint['endpoints'])<=ids
        assert joint['qualified'] is False
        connected|=set(joint['endpoints'])
    assert ids<=connected
    assert len([p for p in c['contract']['parts'] if p['geometric_role']=='hardware-envelope'])==16


@pytest.mark.parametrize('change',({'rail_wall_m':float('nan')},{'rail_wall_m':.001},{'crossmember_count':4}))
def test_unregistered_and_nonfinite_domains_rejected(policy,change):
    with pytest.raises(ValueError):candidate(policy,**change)


def test_stale_geometry_or_lm3_inputs_cannot_reuse_result(policy):
    c=candidate(policy);c['contract']['parts'][0]['properties']['mass_kg']+=1
    with pytest.raises(ValueError,match='controlled structural'):s.evaluate(policy,c)
    policy['architecture']='legacy-lm3'
    with pytest.raises(ValueError,match='architecture'):candidate(policy)


@pytest.mark.parametrize('floor',(.003,.016))
def test_structural_bay_native_mass_ids_static_contact_and_step(tmp_path,policy,floor):
    from engineering.continuous_design import study_confirmation
    c=candidate(policy,floor_thickness_m=floor);path=tmp_path/'definition.json';core.write(path,c['contract'])
    proof,state,error=study_confirmation.native(path,tmp_path/'cad')
    if state=='hold':pytest.skip('Native tool unavailable: '+str(error))
    assert state=='passed',error
    assert proof['physical_ids_preserved'] and proof['manufacturing_unit_ids_preserved']
    assert proof['native_reopened'] and proof['step_volume_reconciled']
    assert len(proof['checks'])==len(c['contract']['parts'])
    assert max(row['mass_relative_error'] for row in proof['checks'])<1e-9
