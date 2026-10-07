"""Bidirectional ring stock, dispatch identity and controlled edge distances."""
import pytest
from osr_mech.network_energy_duty import network_duty


def ring_case():
    stations=[dict(id='a',line='ring',s_m=0),dict(id='b',line='ring',s_m=1000),dict(id='c',line='ring',s_m=3000)]
    design=dict(lines=[dict(name='ring',shape='ring',length_m=4000,ring_wrap_length_m=1000)],stations=stations)
    scenario=dict(consist=dict(car_count=1,energy_kwh_per_car_km=2.4,mass_kg=34000),
        stations=[dict(id=s['id'],dwell_seconds=60) for s in stations],sites=[],
        lines=[dict(id='ring',ring_wrap_length_m=1000,stations=[dict(id='a',distance_from_prev_m=0),dict(id='b',distance_from_prev_m=1000),dict(id='c',distance_from_prev_m=2000)])],
        fleets=[dict(line='ring',trainset_count=2,service_start='00:00',service_end='01:00',
                     dispatch_points=[dict(station='b',heading='forward'),dict(station='c',heading='reverse')],
                     schedule=[{'from':'00:00','to':'01:00','headway_min':10}])])
    return design,scenario


def duty(design,scenario):
    return network_duty(design,scenario,average_speed_kmh=60,initial_soc=.8,
                        auxiliary_kw_per_car=10,regen_fraction=.15,minutes=60)


def test_ring_serves_both_directions_and_the_declared_dispatch_stations():
    d,s=ring_case();result=duty(d,s)
    assert not result['missed_dispatches']
    assert {j['heading'] for j in result['journeys']}=={'forward','reverse'}
    for j in result['journeys']:
        assert j['dispatch_station']==('b' if j['heading']=='forward' else 'c')
        assert j['arrival_station']==j['dispatch_station']
        assert j['distance_km']==4
        legs=[leg for leg in result['departures'] if leg['journey']==j['id']]
        assert legs[0]['from_station']==j['dispatch_station']
        assert all(leg['distance_km']>0 for leg in legs)
    assert not result['distance_findings']


def test_reverse_wrap_uses_the_same_controlled_distance_as_forward_wrap():
    d,s=ring_case();result=duty(d,s)
    wraps=[leg for leg in result['departures'] if {leg['from_station'],leg['to_station']}=={'a','c'}]
    assert {leg['heading'] for leg in wraps}=={'forward','reverse'}
    assert {leg['distance_km'] for leg in wraps}=={1}


def test_dispatch_station_cannot_be_silently_substituted():
    d,s=ring_case();s['fleets'][0]['dispatch_points'][0]['station']='not-on-line'
    with pytest.raises(ValueError,match='dispatch points'):
        duty(d,s)


def test_alignment_and_operating_distance_difference_is_reported():
    d,s=ring_case();d['lines'][0]['length_m']=5000
    result=duty(d,s)
    assert result['distance_findings'][0]['controlled_operating_m']==4000
    assert result['distance_findings'][0]['declared_geometry_m']==5000


def test_repeated_days_reuse_the_same_stock_without_state_reset():
    d,s=ring_case()
    result=network_duty(d,s,average_speed_kmh=60,initial_soc=.8,auxiliary_kw_per_car=10,regen_fraction=.15,minutes=1500)
    assert len(result['trains'])==2
    assert len(result['journeys'])==24
    assert not result['missed_dispatches']
    assert all(len(t['service_journeys'])==12 for t in result['trains'].values())
