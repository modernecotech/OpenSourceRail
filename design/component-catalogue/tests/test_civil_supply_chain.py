"""Production/acceptance/transport conservation and release timing regressions."""
from dataclasses import replace

import pytest

from osr_mech.civil.supply import DeliveryRoute, Evidence, ErectionFront, SupplierCapacity
from osr_mech.civil.supply_chain import ComponentDemand, ConstructionSupplyChain
from osr_mech.civil.shift_schedule import ShiftCycle, simulate_erection


COMPONENT = ComponentDemand('pi-beam25', 85.5, 25, 2.9)


def supplier(**overrides):
    values = dict(id='fixture-production', location='test fixture', delivery_catchment=('test',),
                  relevant_products=('pi-beam25',), prestressing_qualified=True, beds=4, moulds=4,
                  handling_limit_t=100, maximum_length_m=25, maximum_width_m=3,
                  demonstrated_cycle_days=1, total_plant_units_day=4,
                  contracted_units_day={'pi-beam25': 2}, storage_units=4, dispatch_units_day=2,
                  existing_commitments='test-only allocation', qualification='qualified',
                  required_upgrades=(), delivered_prices_usd={}, commercial_terms='test fixture',
                  evidence=Evidence('components/day, t, m', 'synthetic regression fixture',
                                    '2026-10-06', 'test-only', 'test-only', 'engineering-calculation'))
    return SupplierCapacity(**{**values, **overrides})


def route(front='a', **overrides):
    values = dict(id='route-'+front, supplier='fixture-production', front=front, journey_hours=4,
                  trailers=2, payload_t=100, trips_per_trailer_day=2, delivery_window_hours=12,
                  loading_hours=1, unloading_hours=1, maximum_length_m=25, bridge_limit_t=140,
                  buffer_beams=4, access_released=True, turning_space_released=True,
                  loading_equipment_released=True, unloading_equipment_released=True,
                  vehicle_tare_t=20, maximum_width_m=3)
    return DeliveryRoute(**{**values, **overrides})


def front(fid='a', start=0, end=50, **overrides):
    return ErectionFront(fid, 'line', start, end, 1, 'launcher-'+fid,
                         'access-'+fid, 'path-'+fid, int((end-start)/25)+1, **overrides)


def chain(s=None, routes=None, order=4, **allocation):
    s = s or supplier()
    return ConstructionSupplyChain([s], [dict(supplier=s.id, product='pi-beam25',
        units_day=2, **allocation)], routes or [route()], COMPONENT, order)


def run(c, fronts=None, days=30, buffer=4):
    fronts = fronts or [front()]
    return simulate_erection(fronts, ShiftCycle(), accepted_beams_day={}, delivered_beams_day={},
        supports_released_day={}, buffer_capacity={f.id:buffer for f in fronts},
        maximum_days=days, supply_chain=c)


def test_acceptance_hold_and_transit_cannot_credit_future_components():
    result = run(chain(acceptance_delay_days=2))
    assert result['complete']
    assert result['daily'][0]['fronts'][0]['limiting_resource']=='acceptance'
    assert result['daily'][2]['fronts'][0]['limiting_resource']=='transport'
    assert result['daily'][2]['cumulative_erected_beams']==0
    assert result['daily'][3]['cumulative_erected_beams']==2
    assert result['days']==5
    assert result['supply_chain']['cumulative']['delivered']==4


def test_factory_dispatch_and_storage_pause_production_without_banking_capacity():
    c = chain(supplier(storage_units=4, dispatch_units_day=1), order=12)
    f = front(end=150, interruptions_days=tuple(range(3,9)))
    result = run(c, [f], days=60, buffer=2)
    assert result['complete']
    assert c.peak_storage['fixture-production']<=4
    previous_cast=0
    paused=False
    for row in result['daily']:
        cast=row['supply_chain']['cumulative']['cast']
        assert cast-previous_cast<=2
        paused |= cast==previous_cast and cast<12 and row['day']>=3
        previous_cast=cast
        assert row['fronts'][0]['buffer_beams']<=2 if row['fronts'] else True
        for factory in row['supply_chain']['factories'].values():
            assert factory['awaiting_acceptance']+factory['accepted_stock']<=factory['storage_limit']
    assert paused


def test_manufacturing_and_transport_rejections_require_replacements():
    c=chain(supplier(storage_units=8), [route(rejection_fraction=0.5)],
            manufacturing_rejection_fraction=0.25)
    result=run(c, days=40)
    assert result['complete']
    summary=result['supply_chain']['cumulative']
    assert summary['manufacturing_rejected']>0
    assert summary['transport_rejected']>0
    assert summary['cast']>summary['accepted']>summary['delivered']==4
    assert summary['cast']==summary['accepted']+summary['manufacturing_rejected']
    assert summary['dispatched']==summary['delivered']+summary['transport_rejected']
    assert result['daily'][-1]['cumulative_erected_beams']==4


def test_shared_fleet_and_supplier_dispatch_are_not_multiplied_by_routes():
    s=supplier(contracted_units_day={'pi-beam25':4}, total_plant_units_day=4,
               storage_units=8, dispatch_units_day=4)
    routes=[route(fid,fleet_id='shared-fleet',fleet_daily_trips=2) for fid in ('a','b')]
    c=ConstructionSupplyChain([s], [dict(supplier=s.id,product='pi-beam25',units_day=4)], routes, COMPONENT, 8)
    result=run(c,[front(),front('b',50,100)],days=20)
    assert result['complete']
    assert all(sum(f['dispatched_today'] for f in row['supply_chain']['factories'].values())<=2
               for row in result['daily'])


def test_blocked_primary_route_uses_alternative_with_gross_vehicle_clearance():
    c=chain(routes=[route(bridge_limit_t=100), route(id='alternative',bridge_limit_t=140)])
    result=run(c)
    assert result['complete']
    # No load is credited to the first route: 85.5 t beam + 20 t vehicle exceeds 100 t.
    assert c.transport_rejection_credit['route-a']==0
    assert result['supply_chain']['cumulative']['dispatched']==4


def test_unknown_handling_or_storage_cannot_become_available_contract_supply():
    for s in (supplier(handling_limit_t=None),supplier(storage_units=None)):
        result=run(chain(s),days=3)
        assert not result['complete']
        assert result['supply_chain']['cumulative']['cast']==0


def test_aggregate_contract_and_study_opt_in_are_enforced():
    s=supplier()
    with pytest.raises(ValueError,match='contracted capacity'):
        ConstructionSupplyChain([s],[dict(supplier=s.id,product='pi-beam25',units_day=2)]*2,
                                [route()], COMPONENT,4)
    study=replace(s,qualification='study-assumed')
    with pytest.raises(ValueError,match='not qualified'):
        chain(study)
    c=ConstructionSupplyChain([study],[dict(supplier=s.id,product='pi-beam25',units_day=2)],
                             [route()], COMPONENT,4,allow_study_assumptions=True)
    assert run(c)['complete']
    assert not c.summary()['supplier_inputs_qualified']


def test_in_transit_reservations_and_chronology_are_checked():
    c=chain(routes=[route(journey_hours=30,delivery_window_hours=72)],order=4)
    result=run(c,buffer=2,days=20)
    assert result['complete']
    assert all(row['supply_chain']['in_transit_beams']<=2 for row in result['daily'])
    with pytest.raises(ValueError,match='chronological'):
        c.step(1,front_inventory={'a':0},front_buffer_capacity={'a':2},
               remaining_beams={'a':0},delivery_access={'a':'access'})
