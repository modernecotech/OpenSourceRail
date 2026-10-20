"""Exact six-car interfaces, changed-part propagation and open passage acceptance."""
from copy import deepcopy

import pytest

from engineering.assembly_design import baseline,models,evaluate,reactions,integration,installed_equipment
from engineering.continuous_design import civil_kit
from engineering.twin_workflow import core


@pytest.fixture
def case(monkeypatch):
    sources={'fixture.py':'f'*64};monkeypatch.setattr(baseline,'sources',lambda:dict(sources))
    policy=baseline.validate(core.read(baseline.DATA))
    def make(wall=.002):
        def candidate(kind):
            variables={k:v[0] for k,v in policy['pilots'][kind]['domains'].items()}
            if kind=='bearing-seat':variables['bearing_family']='uk-spherical-candidate'
            else:variables['rail_wall_m']=wall
            return models.build(policy,kind,variables)
        cassette=candidate('service-cassette');bearing=candidate('bearing-seat');kit=civil_kit.build(civil_kit.defaults())
        vehicle=reactions.revisioned(dict(architecture='baghdad-six-car',context_id='test-context',cars=['car-'+str(i) for i in range(1,7)]))
        allocations=[dict(id=body+'/cassette-'+str(j),body_id=body,candidate_revision=cassette['revision'],architecture=vehicle['architecture'],context_id=vehicle['context_id'],
            translation_m=[i*18.5+point[0],point[1],point[2]],rotation=[[1.,0.,0.],[0.,1.,0.],[0.,0.,1.]],power_w=120.,heat_w=60.,mechanical_output_w=60.,storage_rate_w=0.) for i,body in enumerate(vehicle['cars']) for j,point in enumerate(installed_equipment.layout()['cassette_local_positions_m'])]
        revisions={'cassette':cassette['revision'],'bearing':bearing['revision'],'civil-kit':core.digest(kit),'software':core.digest(evaluate.control_source('branch'))}
        children={}
        for name,revision in revisions.items():
            # Typed synthetic admission fixtures exercise the interface; they
            # are not engineering/physical evidence for the real candidates.
            result=dict(candidate_revision=revision,state='passed')
            children[name]=dict(candidate_revision=revision,architecture=vehicle['architecture'],context_id=vehicle['context_id'],source_revision=core.digest(sources),
                result=result,result_sha256=core.digest(result),mandatory_evidence=[dict(candidate_revision=revision,state='passed')])
        return dict(policy=policy,cassette=cassette,bearing=bearing,kit=kit,vehicle=vehicle,allocations=allocations,children=children,expected_sources=sources)
    return make


def build(case):
    return integration.build(**case)


def test_mass_cg_and_rotated_inertia_reuse_existing_parallel_axis_adapter():
    parts=[dict(id=str(i),properties=dict(mass_kg=1.,cg_m=[x,0.,0.],inertia_tensor_kg_m2=[[0.,0.,0.],[0.,0.,0.],[0.,0.,0.]])) for i,x in enumerate((-1.,1.))]
    result=integration.mass_properties(parts,[dict(id='pair',translation_m=[3.,4.,0.],rotation=[[0.,-1.,0.],[1.,0.,0.],[0.,0.,1.]])])
    assert result['mass_kg']==2. and result['cg_m']==[3.,4.,0.]
    assert result['inertia_tensor_kg_m2']==[[2.,0.,0.],[0.,0.,0.],[0.,0.,2.]]
    assert result['inertia_interval_kg_m2'] is None


def test_exact_revision_mass_power_heat_force_ledgers_and_passage_holds(case):
    inputs=case();result=build(inputs);f=baseline.facts(inputs['policy'])
    mass=sum(p['properties']['mass_kg'] for p in inputs['cassette']['contract']['parts'])
    assert result['gross_added_properties']['mass_kg']==pytest.approx(48*mass)
    assert result['local_cassette_properties']['mass_kg']==pytest.approx(mass)
    assert result['electrical_ledger']['total_terminal_power_w']==5760.
    assert result['thermal_ledger']['reconciled'] is True
    assert all(r['residual_w']==0. for r in result['thermal_ledger']['entries'])
    planning=[c for c in result['force_ledger']['combinations'] if c['id'].startswith('planning-characteristic')]
    assert [c['train_mass_kg'] for c in planning]==pytest.approx([m+48*mass for m in f['train.mass_cases']])
    assert all(result['force_ledger']['checks'].values())
    assert result['candidate_revisions']['civil-kit']==core.digest(inputs['kit'])
    assert not result['children_eligible'] and result['interface_consistent']
    assert result['child_states']['cassette']=='failed' and 'cassette' in result['disqualified_children']
    assert result['state']=='failed' and result['full_train_passage_executed'] is False
    assert result['admitted_for_system_simulation'] is False
    assert {'time-step-convergence','deck-spatial-convergence','rail-mesh-convergence','carbody-modal-convergence'}<=result['full_passage_acceptance'].keys()
    assert all(gate['state']=='hold' and gate['evidence'] is None for gate in result['full_passage_acceptance'].values())
    assert result['removal_credit_mass_kg']==0. and result['net_vehicle_cg_m'] is None and result['net_vehicle_inertia_kg_m2'] is None
    assert all(not result[k] for k in core.FLAGS)


@pytest.mark.parametrize('defect',('missing-allocation','duplicate-allocation','wrong-body','stale-allocation','architecture','context','child-revision','child-source','result-binding','missing-child','missing-evidence','source-stale','nonfinite-placement','rotation','power-heat-mismatch'))
def test_missing_stale_and_inconsistent_interface_inputs_rejected(case,defect):
    inputs=case()
    if defect=='missing-allocation':inputs['allocations'].pop()
    elif defect=='duplicate-allocation':inputs['allocations'][1]['id']=inputs['allocations'][0]['id']
    elif defect=='wrong-body':inputs['allocations'][0]['body_id']='missing-car'
    elif defect=='stale-allocation':inputs['allocations'][0]['candidate_revision']='0'*64
    elif defect=='architecture':inputs['allocations'][0]['architecture']='legacy-lm3'
    elif defect=='context':inputs['allocations'][0]['context_id']='other-context'
    elif defect=='child-revision':inputs['children']['cassette']['candidate_revision']='0'*64
    elif defect=='child-source':inputs['children']['bearing']['source_revision']='0'*64
    elif defect=='result-binding':inputs['children']['cassette']['result']['state']='failed'
    elif defect=='missing-child':del inputs['children']['civil-kit']
    elif defect=='missing-evidence':inputs['children']['bearing']['mandatory_evidence']=[]
    elif defect=='source-stale':inputs['expected_sources']={}
    elif defect=='nonfinite-placement':inputs['allocations'][0]['translation_m'][0]=float('nan')
    elif defect=='rotation':inputs['allocations'][0]['rotation'][0][0]=-1.
    elif defect=='power-heat-mismatch':inputs['allocations'][0]['heat_w']=0.
    with pytest.raises(ValueError):build(inputs)


@pytest.mark.parametrize('state',('failed','hold'))
def test_known_failed_or_held_confirmation_disqualifies_original_child(case,state,monkeypatch):
    # Isolate confirmation precedence after a synthetic passing current evaluator;
    # separate regression below exercises real known mandatory cassette failure.
    monkeypatch.setattr(evaluate,'evaluate',lambda policy,candidate:dict(candidate_revision=candidate['revision'],state='passed',failed_checks=[],held_checks=[]))
    inputs=case();child=inputs['children']['cassette']
    child['mandatory_evidence'].append(dict(candidate_revision=child['candidate_revision'],state=state))
    result=build(inputs)
    assert result['children_eligible'] is False and 'cassette' in result['disqualified_children']
    assert result['child_states']['cassette']==state
    assert result['state']==state
    assert result['admitted_for_system_simulation'] is False


def test_changed_part_invalidates_old_allocations_and_changes_mass_tensor_and_reactions(case):
    original=case(.002);modified=case(.004)
    stale=deepcopy(original);stale['cassette']=modified['cassette']
    with pytest.raises(ValueError,match='allocation revision'):build(stale)
    before=build(original);after=build(modified)
    assert before['revision']!=after['revision']
    assert before['gross_added_properties']['mass_kg']<after['gross_added_properties']['mass_kg']
    assert before['gross_added_properties']['inertia_tensor_kg_m2']!=after['gross_added_properties']['inertia_tensor_kg_m2']
    for uid,demand in before['force_ledger']['bearing_demands'].items():
        assert after['force_ledger']['bearing_demands'][uid]['maximum_compression_n']>demand['maximum_compression_n']


def test_unknown_heat_map_cannot_become_balanced_zero_heat(case):
    inputs=case();inputs['allocations'][0]['heat_w']=None
    result=build(inputs)
    assert result['thermal_ledger']['reconciled'] is None
    assert result['thermal_ledger']['entries'][0]['heat_w'] is None
    assert result['state']=='failed'


def test_failed_check_veto_survives_a_contradictory_passing_summary(case):
    inputs=case();child=inputs['children']['bearing'];child['result']['failed_checks']=['native geometry mismatch']
    child['result_sha256']=core.digest(child['result'])
    result=build(inputs)
    assert result['child_states']['bearing']=='failed' and result['children_eligible'] is False
    assert result['state']=='failed'


def test_live_snapshot_reuses_adapters_and_retains_missing_qualification(case):
    result=integration.snapshot()
    assert 'run_spatial' in result['existing_adapters']['spatial-passage']
    assert 'NativeSpatialLoop' in result['existing_adapters']['controller-battery-thermal']
    assert result['gross_added_properties']['mass_kg']>0
    assert result['thermal_ledger']['reconciled'] is None
    assert result['children_eligible'] is False and result['state'] in ('hold','failed')
    assert result['full_train_passage_executed'] is False


def test_real_mandatory_cassette_failure_overrides_synthetic_passing_child_result(case):
    inputs=case();assert inputs['children']['cassette']['result']['state']=='passed'
    result=build(inputs)
    actual=result['current_cassette_screen']
    assert actual['candidate_revision']==inputs['cassette']['revision']
    assert 'cassette-system/worst_case_guide_fit' in actual['failed_checks']
    assert 'cassette-system/connector_derating' in actual['held_checks']
    assert result['state']=='failed' and not result['children_eligible']
    assert result['child_states']['cassette']=='failed' and 'cassette' in result['disqualified_children']
    assert not result['admitted_for_system_simulation']
    assert inputs['children']['cassette']['result']['state']=='passed'  # original history preserved
