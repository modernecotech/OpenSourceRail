"""Whole-cell physical correspondence, support scenarios and adverse controls."""
from copy import deepcopy
import json
import math
import pytest

from engineering.assembly_design import baseline,civil_assembly as civil
from engineering.twin_workflow import core
from engineering.design_consistency import contracts


@pytest.fixture(scope='module')
def policy():return core.read(baseline.DATA)


@pytest.fixture(scope='module')
def candidate(policy):return civil.build(policy)


def test_domain_explores_equal_function_architectures_and_actual_wall_mass(policy,candidate):
    assert len(civil.candidates(policy))==9
    assert candidate==civil.build(policy)
    assert len(candidate['contract']['parts'])==328
    assert all(candidate[k] is False for k in core.FLAGS)
    thin=civil.build(policy,dict(architecture='segmental',bracket_wall_m=.004))
    assert thin['revision']!=candidate['revision']
    assert thin['metadata']['mass_ledger']['defined_mass_kg']<candidate['metadata']['mass_ledger']['defined_mass_kg']
    assert all(not row['accepted'] and row['serial'] is None and row['records']==[] for row in candidate['qa_plan'])


def test_equal_volume_plinth_seats_respect_inner_head_gauge_and_source_mass(policy,candidate):
    kit=civil.source_kit(candidate['variables']);original={p['id']:p for p in kit['physical_contract']['parts']}
    parts={p['id']:p for p in candidate['contract']['parts']};gauge=candidate['metadata']['gauge_m']
    for identity,old in original.items():
        if identity.startswith('track-'):
            seats=[p for p in parts.values() if p.get('source_part_id')==identity]
            assert len(seats)==2 and len({p['manufacturing_unit_id'] for p in seats})==2
            assert all(len(p['manufacturing']['primitives'])==1 for p in seats)
            assert sum(p['properties']['mass_kg'] for p in seats)==pytest.approx(old['properties']['mass_kg'],abs=1e-9)
        else:
            assert parts[identity]['manufacturing']==old['manufacturing']
            assert parts[identity]['properties']==old['properties']
    for track in (1,2):
        low=parts[f'rail-T{track}--1']['manufacturing']['primitives'][2]
        high=parts[f'rail-T{track}-1']['manufacturing']['primitives'][2]
        assert high['centre_m'][1]-high['dimensions_m'][1]/2-(low['centre_m'][1]+low['dimensions_m'][1]/2)==pytest.approx(gauge)
    ledger=candidate['metadata']['mass_ledger']
    assert ledger['retained_allowance_study_mass_kg']==pytest.approx(kit['mass_ledger']['installed_study_mass_kg']+ledger['gross_added_represented_mass_kg'])
    assert ledger['gross_added_represented_mass_kg']>0 and ledger['complete_installed_mass_kg'] is None
    assert ledger['removal_credit_kg']==0


def test_every_stage_and_joint_references_exact_parts_and_dag(policy,candidate):
    contracts.validate(candidate['contract']);ids={p['id'] for p in candidate['contract']['parts']};done=set();covered=[]
    for stage in candidate['metadata']['assembly_sequence']:
        assert set(stage['requires'])<=done
        assert set(stage['part_ids'])<=ids
        done.add(stage['id']);covered+=stage['part_ids']
    assert len(covered)==len(set(covered)) and set(covered)==ids
    for joint in candidate['contract']['assembly_joints']:
        assert set(joint['endpoints'])<=ids
        assert not joint['qualified'] and joint['capacity_evidence'] is None
    assert len(candidate['metadata']['support_frames'])==24
    # Direct surface contacts: arm top at-.34, post bottom at-.34,
    # post top/bearer bottom at-.10, bearer top/walkway floor at0.
    from engineering.design_engine.manufacturing_rules import part_bounds
    parts={p['id']:p for p in candidate['contract']['parts']}
    for frame in candidate['metadata']['support_frames']:
        arm=part_bounds(parts[frame['id']+'/arm'])
        for edge in (0,1):
            post=part_bounds(parts[frame['id']+'/post-'+str(edge)])
            assert arm[1][2]==pytest.approx(post[0][2],abs=1e-12)
            assert post[1][2]==pytest.approx(candidate['metadata']['deck_top_m']-.1,abs=1e-12)
        seats=part_bounds(parts[frame['id']+'/service-seats'])
        assert arm[1][2]==pytest.approx(seats[0][2],abs=1e-12)
        assert seats[1][2]==pytest.approx(candidate['metadata']['deck_top_m']-.301,abs=1e-12)


def test_independent_beam_and_signed_whole_bay_gravity_do_not_close_acceptance(policy,candidate):
    result=civil.evaluate(policy,json.loads(json.dumps(candidate)))
    assert result['failed_checks']==[] and len(result['held_checks'])==10
    beam=result['metrics']['bracket'];assert beam['independent']['force_balance_relative_error']<1e-7
    assert beam['tip_deflection_m']==pytest.approx(beam['independent']['maximum_nodal_deflection_m'],rel=1e-7)
    assert beam['adverse_2x']['maximum_nodal_deflection_m']==pytest.approx(2*beam['tip_deflection_m'],rel=1e-7)
    context=result['metrics']['gravity_context']
    assert context['train']['mass_cases_kg']==[384000.,460800.]
    assert context['train']['cars']==6 and context['train']['tracks']==2
    assert all(case['equilibrium_pass'] for case in context['combinations'])
    assert len(context['combinations'])==5
    assert sum(row['mass_kg'] for row in context['added_part_mass_ledger'])==pytest.approx(candidate['metadata']['mass_ledger']['gross_added_represented_mass_kg'])
    assert not candidate['metadata']['full_pilot_scope'] and not candidate['metadata']['complete_installed_system']
    assert all(result[k] is False for k in core.FLAGS)


def test_full_span_lift_failures_are_preserved_and_larger_radius_cannot_be_extrapolated(policy,candidate):
    full=civil.build(policy,dict(architecture='large-span',bracket_wall_m=.006))
    result=civil.evaluate(policy,full)
    assert set(result['failed_checks'])=={'deck-T1-U0/crane-at-radius-scenario','deck-T2-U0/crane-at-radius-scenario'}
    radius=civil.evaluate(policy,candidate,crane_radius_m=21.)
    assert radius['failed_checks'] and all(row['chart_capacity_kg'] is None and not row['scenario_pass'] for row in radius['metrics']['lifts'])
    # No interpolation through an unknown part of a manufacturer chart.
    assert civil._capacity([[8,125000],[14,80000],[20,40000]],15)==40000


def test_adverse_walkway_loads_fail_same_fixed_acceptance_screens(policy,candidate):
    normal=civil.evaluate(policy,candidate);bad=civil.evaluate(policy,candidate,walkway_load_factor=100.)
    assert normal['checks']['bracket_tip_L250_scenario']
    assert not bad['checks']['bracket_tip_L250_scenario']
    assert not bad['checks']['bracket_gross_elastic_355MPa_screen']
    assert not bad['checks']['walkway_floor_L250_scenario']
    assert not bad['checks']['longitudinal_bearer_L250_scenario']


@pytest.mark.parametrize('mutation',('geometry','mass','stage','source','rail-source'))
def test_resealed_stale_geometry_or_source_cannot_reuse_assessment(policy,candidate,mutation):
    broken=deepcopy(candidate)
    if mutation=='geometry':broken['contract']['parts'][0]['manufacturing']['primitives'][0]['length_m']=1.
    elif mutation=='mass':broken['contract']['parts'][0]['properties']['mass_kg']+=1.
    elif mutation=='stage':broken['metadata']['assembly_sequence'][0]['part_ids']=[]
    elif mutation=='source':broken['source_kit_revision']='0'*64
    else:broken['metadata']['rail_source']['published']['mass_kg_m']=1.
    broken['definition_sha256']=core.digest({k:v for k,v in broken.items() if k!='definition_sha256'})
    with pytest.raises(ValueError,match='exact controlled reconstruction'):civil.evaluate(policy,broken)


@pytest.mark.parametrize('factor',(float('nan'),float('inf'),0.,-1.,True))
def test_nonfinite_or_nonsensical_adverse_inputs_rejected(policy,candidate,factor):
    with pytest.raises(ValueError):civil.evaluate(policy,candidate,walkway_load_factor=factor)


def test_real_native_whole_cell_has_no_solid_collisions_and_roundtrips(tmp_path,candidate):
    from engineering.continuous_design import study_confirmation
    path=tmp_path/'definition.json';core.write(path,candidate['contract'])
    proof,state,error=study_confirmation.native(path,tmp_path/'native')
    assert state=='passed',error
    assert proof['physical_ids_preserved'] and proof['native_reopened']
    assert proof['step_volume_reconciled'] and proof['manufacturing_unit_ids_preserved']
    assert len(proof['checks'])==len(candidate['contract']['parts'])
