"""A strong local result or a method demonstration cannot pass a whole train."""
from copy import deepcopy
import pytest
from engineering.engineering_status import contracts as c


def composition():
    return dict(candidate_id='1'*64,body_candidate_id='2'*64,magnet_component_id='3'*64,name='fixture')


def unknowns():return [c.gate(k,'unknown','Missing same-configuration evidence') for k in c.GATES]


def test_same_component_does_not_identify_the_equipped_vehicle():
    value=composition()
    assert c.require_subject({'magnet_component_id':value['magnet_component_id']},value,'magnet')
    with pytest.raises(ValueError,match='different physical'):c.require_subject({'candidate_id':'4'*64},value,'composition')
    with pytest.raises(ValueError,match='different physical'):c.require_subject({'candidate_id':value['magnet_component_id']},value,'composition')


def test_method_pass_cannot_become_suspension_acceptance():
    rows=unknowns();rows[1]=c.gate('suspension','pass','Manufactured method succeeded',maturity='verified-simulation',
        evidence=[dict(scope='method',evaluation_id='4'*64)])
    with pytest.raises(ValueError,match='method evidence'):c.candidate(composition(),rows)


def test_resealed_outer_record_cannot_admit_a_wrong_body():
    rows=unknowns();rows[0]=c.gate('mass','pass','Equipped inventory',maturity='verified-simulation',
        evidence=[dict(scope='body',body_candidate_id='9'*64,evaluation_id='4'*64)])
    with pytest.raises(ValueError,match='different physical'):c.candidate(composition(),rows)


def test_unknown_mass_and_force_refuse_all_real_journeys_without_fake_trajectories():
    value=c.candidate(composition(),unknowns());rows=c.preflights(value)
    assert len(rows)==8 and {'receiving-power-loss','support-power-loss'}=={r['scenario']['fault']['id'] for r in rows if r['scenario']['fault']}
    assert all(r['vehicle_id']==value['candidate_id'] and r['dynamic_execution']=='not-run' and r['trajectory'] is None and r['distance_travelled_m']==0 for r in rows)
    assert all(r['scenario']['candidate_id']==value['candidate_id'] for r in rows)
    assert value['physical_acceptance']=='unknown' and value['physical_accepted'] is False


def test_journey_and_economics_are_outputs_not_circular_physics_prerequisites():
    rows=unknowns()
    for i,g in enumerate(rows):
        if g['id'] not in {'operations','economics'}:
            rows[i]=c.gate(g['id'],'pass','Complete hypothetical fixture inputs',maturity='verified-simulation',
                evidence=[dict(scope='composition',candidate_id='1'*64,evaluation_id='4'*64)],values={'criterion_complete':True})
    value=c.candidate(composition(),rows)
    assert value['engineering_readiness']=='unknown'
    assert all(r['dynamic_execution']=='ready-not-run' and r['trajectory'] is None for r in c.preflights(value))
    assert all(r['launch_authorised'] is False for r in c.preflights(value))


def test_analytical_component_screen_cannot_pass_full_equipped_criterion():
    rows=unknowns();rows[1]=c.gate('suspension','pass','Local capacity only',maturity='analytical-estimate',
        evidence=[dict(scope='magnet',magnet_component_id='3'*64,evaluation_id='4'*64)])
    with pytest.raises(ValueError,match='complete-criterion'):c.candidate(composition(),rows)


def test_definition_and_missing_gates_cannot_claim_pass():
    with pytest.raises(ValueError):c.gate('mass','pass','Definition',evidence=[{}])
    with pytest.raises(ValueError,match='every'):c.candidate(composition(),unknowns()[:-1])
