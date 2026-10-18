"""Adverse review probes for real resource lifetimes and immutable QA history."""
from copy import deepcopy
import itertools

import pytest

from engineering.continuous_design import civil_kit,construction_stage as stages,delivery_simulation as delivery,qa_traveller as qa


@pytest.fixture(scope='module')
def scenario():
    kit=civil_kit.build(civil_kit.defaults('segmental'));rows=stages.tasks(kit)
    scheduled=delivery.schedule(rows,kit['basis']['capacities'])
    assert scheduled['passed']
    return kit,rows,scheduled


def test_concrete_has_batch_travel_wait_discharge_and_return_with_reserved_plant(scenario):
    kit,rows,s=scenario;timed={r['id']:r for r in s['tasks']};by={r['id']:r for r in rows}
    result=stages.verify_schedule(kit,rows,s);assert all(result['checks'].values())
    assert len(result['concrete_deliveries'])==16
    for record in result['concrete_deliveries']:
        prefix=record['delivery'];uid=prefix.split('/mixer-')[0]
        assert timed[uid+'/pour-reserve']['end_h']<=record['batch_start_h']
        assert record['arrival_h']<=record['discharge_start_h']<record['discharge_end_h']
        assert record['age_at_discharge_end_h']<=kit['basis']['site']['concrete_mix']['maximum_batch_to_discharge_end_h']
        assert by[prefix+'/batch']['acquire']=={'mixer':1}
        assert by[prefix+'/return']['release']=={'mixer':1}
    occupied=sum(timed[r['id'].removesuffix('/batch')+'/return']['end_h']-timed[r['id']]['start_h'] for r in rows if r['id'].endswith('/batch'))
    assert s['resources']['mixer']['busy_resource_hours']==pytest.approx(occupied)
    labour=sum((timed[r['id'].removesuffix('/pour-reserve')+'/site-cast']['end_h']-timed[r['id']]['start_h'])*kit['basis']['site']['people_per_operation'] for r in rows if r['id'].endswith('/pour-reserve'))
    assert s['reserved_person_hours_by_location']['site']==pytest.approx(labour)


def test_seven_hour_wait_before_casting_fails_even_with_tightly_grouped_arrivals(scenario):
    kit,rows,s=scenario;changed=deepcopy(rows)
    first=next(r for r in changed if r['id'].endswith('/mixer-0/discharge'))
    parent=first['id'].removesuffix('/discharge')+'/travel'
    first['ready_after']={parent:7.}
    delayed=delivery.schedule(changed,kit['basis']['capacities']);assert delayed['passed']
    check=stages.verify_schedule(kit,changed,delayed)
    assert not check['checks'][first['id'].removesuffix('/discharge')+'/concrete-age-at-placement']
    assert max(r['waiting_h'] for r in check['concrete_deliveries'])>=7.


def test_one_mixer_cannot_hide_an_interrupted_continuous_pour(scenario):
    kit,_,_=scenario;kit=deepcopy(kit);kit['basis']['capacities']['mixer']=1
    rows=stages.tasks(kit);s=delivery.schedule(rows,kit['basis']['capacities']);assert s['passed']
    checks=stages.verify_schedule(kit,rows,s)['checks']
    assert any(not value for key,value in checks.items() if key.endswith('/placement-continuity'))


def test_mix_specific_age_limit_is_not_inferred_from_arrival_spread(scenario):
    kit,rows,s=scenario;kit=deepcopy(kit);kit['basis']['site']['concrete_mix']['maximum_batch_to_discharge_end_h']=1.
    assert any(not value for key,value in stages.verify_schedule(kit,rows,s)['checks'].items() if key.endswith('/concrete-age-at-placement'))


def test_missing_mix_bound_holds_instead_of_implying_unlimited_placement(scenario,tmp_path):
    from engineering.continuous_design import civil_kit_evaluation
    kit,_,_=scenario;basis=deepcopy(kit['basis']);basis['site']['concrete_mix']['maximum_batch_to_discharge_end_h']=None
    result=civil_kit_evaluation.evaluate(dict(context_id=civil_kit.CONTEXT,variables=civil_kit.defaults('segmental')),tmp_path,basis)
    assert not result['study_pass'] and not result['failed_checks']
    assert any('maximum_batch_to_discharge_end_h' in hold for hold in result['held_checks'])


def test_falsework_token_is_held_through_erection_and_removal(scenario):
    kit,rows,s=scenario;t={r['id']:r for r in s['tasks']}
    occupied=t['falsework/remove']['end_h']-t['falsework/reserve']['start_h']
    assert occupied>kit['basis']['site']['falsework_install_hours']+kit['basis']['site']['falsework_remove_hours']
    assert s['resources']['falsework']['busy_resource_hours']==pytest.approx(occupied)
    assert all(delivery.audit(rows,s,kit['basis']['capacities']).values())
    changed=deepcopy(rows);next(r for r in changed if r['id']=='falsework/reserve')['acquire']={}
    next(r for r in changed if r['id']=='falsework/remove')['release']={}
    bad=delivery.schedule(changed,kit['basis']['capacities']);assert bad['passed']
    assert not stages.verify_schedule(kit,changed,bad)['checks']['falsework/reserve/required-resource-contract']


def test_two_bays_compete_for_installed_falsework_not_just_installation_labour():
    rows=[]
    for bay in ('A','B'):
        rows += [dict(id=bay+'/install',hours=1.,after=[],resources={},acquire={'falsework':1},owner=bay),
                 dict(id=bay+'/erect',hours=10.,after=[bay+'/install'],resources={}),
                 dict(id=bay+'/remove',hours=1.,after=[bay+'/erect'],resources={},release={'falsework':1},owner=bay)]
    a=delivery.schedule(rows,{'falsework':1});b=delivery.schedule(rows,{'falsework':2})
    assert a['makespan_h']==24 and b['makespan_h']==12
    assert a['resources']['falsework']['busy_resource_hours']==24


def test_oversized_temporary_plant_fails_same_crane_and_transport_checks(scenario):
    kit,_,_=scenario;kit=deepcopy(kit);u=kit['temporary_units'][0];u['mass_kg']=85000.
    checked=stages.handling(kit)
    assert not checked['checks'][u['id']+'/crane-at-radius']
    assert checked['maximum_lift_mass_kg']==86000.
    u['transport_dimensions_m']=[30.,3.,2.];u['mass_kg']=100000.
    checked=stages.handling(kit)
    assert not checked['checks'][u['id']+'/transport-envelope'] and not checked['checks'][u['id']+'/transport-payload']
    kit['basis']['lifting']['ground_pressure_limit_pa']=1.
    assert not stages.handling(kit)['checks'][u['id']+'/ground-pressure-hypothesis']


def test_driven_piles_have_pitch_drive_records_acceptance_and_optional_splices():
    v=dict(civil_kit.defaults(),foundation_family='hollow-driven-six',foundation_route='precast-driven')
    kit=civil_kit.build(v);piles=[u for u in kit['units'] if u['category']=='pile'];assert len(piles)==12
    rows=stages.tasks(kit);by={r['id']:r for r in rows};s=delivery.schedule(rows,kit['basis']['capacities']);assert s['passed']
    assert all(stages.verify_schedule(kit,rows,s)['checks'].values())
    for u in piles:
        uid=u['id'];assert by[uid+'/place-and-temporary-lock']['acquire']=={'pile_rig':1}
        assert by[uid+'/drive-0']['held_plant']=='pile_rig'
        assert by[uid+'/installation-test']['release']=={'pile_rig':1}
        assert uid+'/installation-test' in by[uid+'/engineered-joint']['after']
        assert 'pile-driving-record' in qa.requirements(u)['installed']
    assert s['resources']['pile_rig']['busy_resource_hours']>sum(r['hours'] for r in rows if '/drive-' in r['id'])
    missing=[r for r in rows if not r['id'].endswith('/drive-0')]
    assert not stages.verify_schedule(kit,missing,s)['checks']['all_required_stage_ids']
    length=piles[0]['pile_installation']['segments_m'][0];piles[0]['pile_installation']['segments_m']=[length/2,length/2]
    by={r['id']:r for r in stages.tasks(kit)};uid=piles[0]['id']
    assert by[uid+'/splice-1']['after']==[uid+'/drive-0']
    assert by[uid+'/drive-1']['after']==[uid+'/splice-1']


def passing_traveller(unit):
    t=qa.template(unit);t['serial']='synthetic-serial'
    for stage,tests in qa.requirements(unit).items():
        for name in tests:
            t['records'].append(qa.event(dict(event_type='test',sequence=len(t['records'])+1,stage=stage,test=name,state='passed',
                serial=t['serial'],unit_revision=unit['revision'],interface_revision='IF-1',qualified_reviewer='test fixture; not approval',evidence_sha256='a'*64)))
    return t


def failure_events(unit):
    t=passing_traveller(unit);old=t['records'][-1]
    failure=qa.event(dict({k:v for k,v in old.items() if k!='event_id'},state='failed',sequence=100,evidence_sha256='b'*64))
    return t,old,failure


def test_replayed_old_pass_never_hides_failure_and_order_is_irrelevant(scenario):
    unit=scenario[0]['units'][0];t,old,failure=failure_events(unit);base=t['records'][:-1]
    for suffix in itertools.permutations([old,failure,old]):
        t['records']=base+list(suffix);r=qa.assess(unit,t,interface_revision='IF-1')
        assert r['state']=='failed' and failure['event_id'] in r['unresolved_failure_event_ids']
    t=passing_traveller(unit);t['records']+=t['records']
    assert qa.assess(unit,t,interface_revision='IF-1')['state']=='passed-records'


def test_only_linked_retest_and_documented_disposition_clear_failure(scenario):
    unit=scenario[0]['units'][0];t,old,failure=failure_events(unit);t['records'].append(failure)
    retest=qa.event(dict({k:v for k,v in old.items() if k!='event_id'},sequence=101,retests=[failure['event_id']],evidence_sha256='c'*64))
    t['records'].append(retest);assert qa.assess(unit,t,interface_revision='IF-1')['state']=='failed'
    disposition=qa.event(dict({k:v for k,v in old.items() if k!='event_id'},event_type='disposition',state='closed',sequence=102,
        failure_event_ids=[failure['event_id']],retest_event_ids=[retest['event_id']],reason='Synthetic documented repair and retest fixture',evidence_sha256='d'*64))
    t['records'].append(disposition)
    for values in (t['records'],list(reversed(t['records'])),t['records']+[failure,old]):
        t['records']=values;r=qa.assess(unit,t,interface_revision='IF-1')
        assert r['state']=='passed-records' and not r['accepted'] and not r['unresolved_failure_event_ids']


@pytest.mark.parametrize('change',[{'unit_revision':'other'},{'serial':'other'},{'interface_revision':'other'},{'retests':[]},{'sequence':99}])
def test_inapplicable_or_older_retest_cannot_clear_failure(scenario,change):
    unit=scenario[0]['units'][0];t,old,failure=failure_events(unit)
    record=dict({k:v for k,v in old.items() if k!='event_id'},sequence=101,retests=[failure['event_id']]);record.update(change);retest=qa.event(record)
    disposition=qa.event(dict({k:v for k,v in old.items() if k!='event_id'},event_type='disposition',state='closed',sequence=102,
        failure_event_ids=[failure['event_id']],retest_event_ids=[retest['event_id']],reason='Test only'))
    t['records'] += [failure,retest,disposition]
    assert qa.assess(unit,t,interface_revision='IF-1')['state']=='failed'


def test_mutated_legacy_or_conflicting_identity_cannot_report_passed_records(scenario):
    unit=scenario[0]['units'][0];t=passing_traveller(unit)
    legacy=deepcopy(t['records'][-1]);legacy.pop('event_id');legacy['state']='failed';t['records'].append(legacy)
    assert qa.assess(unit,t,interface_revision='IF-1')['state']=='failed'
    t=passing_traveller(unit);mutated=deepcopy(t['records'][-1]);mutated['state']='failed';t['records'].append(mutated)
    assert qa.assess(unit,t,interface_revision='IF-1')['state']=='failed'
    t=passing_traveller(unit);same=deepcopy(t['records'][-1]);same.pop('event_id');same['evidence_sha256']='b'*64;t['records'].append(qa.event(same))
    assert qa.assess(unit,t,interface_revision='IF-1')['state']=='hold'


def test_timed_dispatch_can_advance_a_clock_with_only_held_resources():
    rows=[dict(id='reserve',hours=1.,after=[],resources={},owner='pour',acquire={'pump':1}),
          dict(id='delivery',hours=1.,after=['reserve'],resources={},ready_after={'reserve':5.}),
          dict(id='finish',hours=1.,after=['delivery'],resources={},owner='pour',release={'pump':1})]
    result=delivery.schedule(rows,{'pump':1})
    assert result['passed'] and result['makespan_h']==8 and result['resources']['pump']['busy_resource_hours']==8
    assert all(delivery.audit(rows,result,{'pump':1}).values())
