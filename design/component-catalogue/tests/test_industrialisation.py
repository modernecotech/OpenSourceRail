from copy import deepcopy
import pytest

from osr_mech.industrialisation import (vehicle_support_graph,moving_axle_screen,production_balance,
    installed_cost_comparison,support_packet_check,disruption_metrics,service_finance_gate,elevation_reference)
from osr_mech.station.layout import station_layout


def test_shared_support_graph_conserves_weight_without_assuming_a_bogie_reduction():
    bogies=[dict(id=str(i),x_m=i*10.,mass_kg=1000.,axles=2,axle_offsets_m=[-1.,1.]) for i in range(3)]
    bodies=[dict(id=str(i),cg_x_m=i*10.+5.,supported_mass_kg=10000.,support_bogies=[str(i),str(i+1)]) for i in range(2)]
    graph=vehicle_support_graph(bodies,bogies)
    assert graph['bogie_count']==3 and graph['axle_count']==6 and graph['total_mass_kg']==23000
    assert graph['bogie_reactions_kn']['1']==pytest.approx(11000*9.81/1000)
    assert graph['load_balance_passed'] and not graph['engineering_accepted']
    bodies[0]['supported_mass_kg']=None
    unknown=vehicle_support_graph(bodies,bogies)
    assert unknown['total_mass_kg'] is None and all(p['static_load_kn'] is None for p in unknown['axle_pattern'])
    assert not unknown['articulation_changes_bogie_count_automatically']


def test_axle_load_pattern_drives_civil_demand_without_granting_capacity():
    row=moving_axle_screen([dict(x_m=0.,static_load_kn=100.)],20.)
    assert row['maximum_support_reaction_kn']==100
    assert row['maximum_live_moment_knm']==pytest.approx(500)
    assert not row['capacity_accepted'] and row['dynamic_augmentation'] is None


def production():
    return dict(launchers=18,shifts_day=2,mould_occupation_hours=48.,casting_position_availability=1.,
        first_pass_yield=1.,buffer_working_days=5,accepted_capacities_per_working_day={
            k:None for k in ('released_foundations','accepted_piers','accepted_beams','transported_beams','erected_bays','accepted_completed_bays')})


def test_accepted_bay_chain_controls_casting_positions_buffer_and_spares():
    config=production();row=production_balance(config,1.5,independent_fronts=18)
    assert (row['illustrative_bays_per_working_day'],row['illustrative_beams_per_working_day'],row['casting_positions'],row['buffer_beams'])==(27.,54.,108,270)
    assert row['accepted_chain_bays_per_working_day'] is None
    config['accepted_capacities_per_working_day']={k:100. for k in config['accepted_capacities_per_working_day']}
    config['accepted_capacities_per_working_day']['accepted_completed_bays']=12.
    assert production_balance(config,1.5,independent_fronts=18)['accepted_chain_bays_per_working_day']==12.
    row=production_balance(config,1.5,independent_fronts=6)
    assert row['active_launchers']==6 and row['spare_launchers']==12


def test_unknown_cost_and_support_evidence_cannot_release_work_or_claim_savings():
    row=installed_cost_comparison(['a','b'],[dict(id='example',scope_costs_usd={'a':100})])[0]
    assert row['known_scoped_cash_usd']==100 and row['complete_installed_cost_usd'] is None
    packet=support_packet_check(dict(support_id='support',revision='r',evidence={}), 'r')
    assert packet['missing_evidence'] and not packet['launcher_support_released']


def test_overlapping_closures_count_lane_hours_once_and_bind_to_accepted_bays():
    events=[dict(id=str(i),bay_id='bay',kind='lane',resource_id='lane-1',start_at=a,finish_at=b) for i,(a,b) in enumerate([
        ('2027-01-01T08:00:00+03:00','2027-01-01T10:00:00+03:00'),
        ('2027-01-01T09:00:00+03:00','2027-01-01T11:00:00+03:00')])]
    measured=disruption_metrics(events,['bay','other-completed-bay'])
    assert measured['lane_hours_closed']==3
    assert measured['lane_hours_closed_per_accepted_bay']==1.5
    with pytest.raises(ValueError,match='accepted completed bay'):disruption_metrics(events,[])
    assert disruption_metrics([],[])['lane_hours_closed'] is None


def test_delivered_trains_do_not_create_paid_journeys_or_a_financing_approval():
    row=dict(line='line',month='2027-01',required_trainsets=10,commissioned_trainsets=5,scheduled_train_km=100,served_train_km=40)
    result=service_finance_gate([row])['line_months'][0]
    assert result['fleet_readiness_fraction']==.5 and result['delivered_service_fraction']==.4
    assert result['finance_receipts_iqd'] is None and not result['finance_adoption_authorised']


def test_additional_elevation_keeps_reference_delta_separate_from_installed_cost():
    result=elevation_reference(10000.,2_584_000.,9_748_000.)
    assert result['marginal_reference_civil_allowance_usd']==71_640_000
    assert result['complete_incremental_installed_cost_usd'] is None
    assert result['discounted_net_benefit_usd'] is None and not result['economic_selection_accepted']


def test_default_equipment_is_contained_in_platforms_and_sized_concourse_decks():
    layout=station_layout(dict(platform_layout='stacked',elevation='elevated',platform_count=2,platform_length_m=59.5,platform_width_m=8))
    for equipment in layout.equipment:
        assert abs(equipment.x_mm)+equipment.length_mm/2<=59500/2
        for deck in layout.concourse_decks:
            if deck['level'] in equipment.served_levels:
                assert abs(equipment.x_mm-deck['x_mm'])+equipment.length_mm/2<=deck['length_mm']/2
    assert layout.payload()['equipment_geometry_contained'] and not layout.payload()['street_access_accepted']


def test_custom_equipment_cannot_be_clipped_to_hide_an_overhang_or_small_concourse():
    parameters=dict(platform_layout='island',elevation='elevated',platform_count=1,platform_length_m=60,platform_width_m=8)
    original=station_layout(parameters)
    rows=[dict(id=e.id,kind=e.kind,served_levels=e.served_levels,x_mm=e.x_mm,y_mm=e.y_mm,width_mm=e.width_mm,length_mm=e.length_mm) for e in original.equipment]
    broken=deepcopy(rows);broken[0]['x_mm']=30000
    with pytest.raises(ValueError,match='support envelope'):station_layout({**parameters,'access_equipment':broken})
    with pytest.raises(ValueError,match='support envelope'):
        station_layout({**parameters,'concourse_decks':[dict(id='concourse',level='concourse',z_mm=4500,length_mm=24000,width_mm=10000)]})
