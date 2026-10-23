"""A connected publication must retain unresolved engineering and execution."""
from copy import deepcopy
import pytest
from engineering.ferrite_maglev import pilot_release as p


def test_failed_mass_and_missing_execution_stay_visible(monkeypatch):
    components=[dict(id='controlled-product',summary=dict(mass_targets_closed=0,configurations=2)),
        dict(id='assurance-profiles',summary=dict(all_profiles_executed=False)),
        dict(id='capability-migration',summary=dict(capabilities=[dict(id='editor',state='missing')]))]
    monkeypatch.setattr(p,'read_components',lambda:deepcopy(components))
    value=p.study()
    assert not value['mass_targets_closed'] and not value['digital_profiles_executed']
    assert value['missing_legacy_capabilities']==['editor']
    assert value['development_deliverables'][1]['state']=='delivered-with-mass-hold'
    assert value['development_deliverables'][-1]['state']=='execution-hold'
    assert all(value[k] is False for k in p.model.FLAGS)


def test_profile_pass_does_not_become_physical_release(monkeypatch):
    components=[dict(id='controlled-product',summary=dict(mass_targets_closed=2,configurations=2)),
        dict(id='assurance-profiles',summary=dict(all_profiles_executed=True)),
        dict(id='capability-migration',summary=dict(capabilities=[]))]
    monkeypatch.setattr(p,'read_components',lambda:components)
    value=p.study()
    assert value['digital_profiles_executed'] and value['mass_targets_closed']
    assert value['physical_gate_state']=='open' and not value['physical_release']


def test_exact_child_configuration_and_derived_actuator_ancestry_required():
    good='a'*64
    components=[dict(id='controlled-product',summary=dict(configuration_sha256=good)),
        dict(id='pilot-corridor',summary=dict(configuration_sha256=good)),
        dict(id='native-lifecycle',summary=dict(configuration_sha256=good)),
        dict(id='coupled-actuators',summary=dict(base_configuration_sha256=good,configuration_sha256='b'*64)),
        dict(id='launch-options',summary=dict(research_recommendation=dict(configuration_sha256=good)))]
    p.check_configurations(components)
    components[2]['summary']['configuration_sha256']='c'*64
    with pytest.raises(ValueError,match='different exact'):
        p.check_configurations(components)
    components[2]['summary']['configuration_sha256']=good
    components[3]['summary']['base_configuration_sha256']='d'*64
    with pytest.raises(ValueError,match='ancestry'):
        p.check_configurations(components)


def test_scoped_digital_completion_never_closes_qualification_parent():
    values=[dict(id='resource-delivery',digital_packet_verified=True,scope='A resource-constrained1km schedule',
                 manifest_sha256='a'*64,summary={})]
    progress=p.digital_progress(values)
    assert progress['completed_scoped_digital_subtasks']==1
    assert progress['full_qualification_tasks_completed']==progress['physical_tasks_accepted']==0
    parent=next(t for t in progress['tasks'] if t['id']=='group/civil-strength-stages/design')
    assert parent['digital_subtasks']==['pilot/resource-delivery']
    assert parent['physical_state']=='unexecuted' and not parent['accepted']


@pytest.mark.parametrize('held,control_hash',[(False,'a'*64),(True,'b'*64)])
def test_failed_or_different_configuration_fault_controls_disqualify_model(monkeypatch,held,control_hash):
    components=[dict(id='controlled-product',summary=dict(mass_targets_closed=0,configurations=2)),
        dict(id='assurance-profiles',summary=dict(all_profiles_executed=True)),
        dict(id='capability-migration',summary=dict(capabilities=[])),
        dict(id='coupled-actuators',summary=dict(any_full_candidate_feasible=True,
            all_negative_controls_held=held,configuration_sha256='c'*64,
            qualified_configuration_sha256='a'*64,control_configuration_sha256=control_hash))]
    monkeypatch.setattr(p,'read_components',lambda:components)
    value=p.study()
    assert not value['coupled_model_feasible']
    assert value['development_deliverables'][3]['state']=='model-infeasible'


def test_repaired_candidate_uses_its_own_fault_controls(monkeypatch):
    components=[dict(id='controlled-product',summary=dict(mass_targets_closed=0,configurations=2)),
        dict(id='assurance-profiles',summary=dict(all_profiles_executed=True)),
        dict(id='capability-migration',summary=dict(capabilities=[])),
        dict(id='coupled-actuators',summary=dict(any_full_candidate_feasible=True,
            all_negative_controls_held=True,configuration_sha256='b'*64,
            qualified_configuration_sha256='a'*64,control_configuration_sha256='a'*64,
            repair_candidates=[dict(configuration_sha256='a'*64,extrema=dict(peak_module_force_n=19_000.))]))]
    monkeypatch.setattr(p,'read_components',lambda:components)
    assert p.study()['coupled_model_feasible']


@pytest.mark.parametrize('peak',[20_001.,float('nan'),None])
def test_actual_force_overshoot_or_missing_evidence_cannot_inherit_command_limit(monkeypatch,peak):
    components=[dict(id='controlled-product',summary=dict(mass_targets_closed=0,configurations=2)),
        dict(id='assurance-profiles',summary=dict(all_profiles_executed=True)),
        dict(id='capability-migration',summary=dict(capabilities=[])),
        dict(id='coupled-actuators',summary=dict(any_full_candidate_feasible=True,
            all_negative_controls_held=True,qualified_configuration_sha256='a'*64,
            control_configuration_sha256='a'*64,
            repair_candidates=[dict(configuration_sha256='a'*64,extrema=dict(peak_module_force_n=peak))]))]
    monkeypatch.setattr(p,'read_components',lambda:components)
    value=p.study()
    assert not value['coupled_model_feasible']
    assert not value['coupled_actual_module_force']['passed']


def test_candidate_finance_cannot_borrow_a_different_actuator_pass():
    base='a'*64;repair='b'*64
    components=[dict(id='controlled-product',summary=dict(configuration_sha256=base)),
        dict(id='pilot-corridor',summary=dict(configuration_sha256=base)),
        dict(id='native-lifecycle',summary=dict(configuration_sha256=base)),
        dict(id='coupled-actuators',summary=dict(base_configuration_sha256=base,
            configuration_sha256=base,qualified_configuration_sha256=repair)),
        dict(id='launch-options',summary=dict(research_recommendation=None)),
        dict(id='candidate-finance',summary=dict(base_configuration_sha256=base,
            configuration_sha256=repair))]
    p.check_configurations(components)
    components[-1]['summary']['configuration_sha256']='c'*64
    with pytest.raises(ValueError,match='exact executed'):
        p.check_configurations(components)


def test_publication_manifest_source_claim_is_checked(tmp_path,monkeypatch):
    import json
    from hashlib import sha256
    monkeypatch.setattr(p,'study',lambda:{})
    monkeypatch.setattr(p,'readme',lambda value,output:'Fixture')
    for name,data in [('study.json',b'{}'),('README.md',b'Fixture')]:
        (tmp_path/name).write_bytes(data)
    m=dict(schema=p.SCHEMA,source_sha256=p.sources(),files_sha256={
        n:sha256((tmp_path/n).read_bytes()).hexdigest() for n in ('study.json','README.md')},**p.model.FLAGS)
    (tmp_path/'manifest.json').write_bytes(p.encoded(m));p.verify(tmp_path)
    m['source_sha256']={'forged':'b'*64};(tmp_path/'manifest.json').write_bytes(p.encoded(m))
    with pytest.raises(ValueError,match='altered'):
        p.verify(tmp_path)


def test_rehashed_false_release_text_is_rejected(tmp_path,monkeypatch):
    import json
    from hashlib import sha256
    monkeypatch.setattr(p,'study',lambda:{'source_sha256':p.sources()})
    monkeypatch.setattr(p,'readme',lambda value,output:'Physical acceptance remains open.')
    p.publish(tmp_path);p.verify(tmp_path)
    (tmp_path/'README.md').write_text('Accepted for passenger service and manufacture.')
    receipt=json.loads((tmp_path/'manifest.json').read_bytes())
    receipt['files_sha256']['README.md']=sha256((tmp_path/'README.md').read_bytes()).hexdigest()
    (tmp_path/'manifest.json').write_bytes(p.encoded(receipt))
    with pytest.raises(ValueError,match='altered'):
        p.verify(tmp_path)
