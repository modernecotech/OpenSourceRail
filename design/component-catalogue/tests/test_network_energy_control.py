import json
from pathlib import Path
from osr_mech.network_energy_duty import network_duty
from osr_mech.network_energy_control import controlled_network_energy

ROOT=Path(__file__).resolve().parents[3]


def fixture(soc=.21):
    stations=[dict(id=k,line='line',s_m=i*1000) for i,k in enumerate('abc')]
    design=dict(lines=[dict(name='line',shape='linear',length_m=2000)],stations=stations)
    scenario=dict(consist=dict(car_count=1,energy_kwh_per_car_km=1,mass_kg=34000),
        stations=[dict(id=k,dwell_seconds=0) for k in 'abc'],sites=[],
        lines=[dict(id='line',stations=[dict(id=k,distance_from_prev_m=0 if i==0 else 1000) for i,k in enumerate('abc')])],
        fleets=[dict(line='line',trainset_count=2,service_start='00:00',dispatch_points=[dict(station='a',heading='forward'),dict(station='c',heading='reverse')],
            schedule=[{'from':'00:00','to':'01:00','headway_min':10}])])
    movement=dict(basis='native-model-test-fixture',sections=[dict(line='line',heading=heading,from_station=a,to_station=b,distance_m=1000,travel_seconds=60)
        for heading,a,b in [('forward','a','b'),('forward','b','c'),('reverse','c','b'),('reverse','b','a')]])
    duty=network_duty(design,scenario,average_speed_kmh=60,initial_soc=soc,auxiliary_kw_per_car=0,regen_fraction=0,minutes=60,movement_profiles=movement)
    packs=json.loads((ROOT/'lib/templates/battery-profiles.json').read_text())['profiles']
    return design,scenario,movement,packs['lfp-onboard-study'],packs['lfp-stationary-study'],duty['trains'],{},60


def test_energy_holds_preserve_station_identity_and_remove_stock_from_later_dispatches():
    result=controlled_network_energy(*fixture(),ambient_c=25,regen_fraction=0)
    assert result['dispatched_journeys']==2 and result['completed_journeys']==0
    assert result['distinct_energy_held_journeys']==2
    assert result['energy_hold_train_minutes']>2
    assert all(a['station']=='b' and not a['moving'] for a in result['final_train_locations'].values())
    assert len(result['missed_dispatches'])==10
    assert all(d['reason']=='stock-not-ready' for d in result['missed_dispatches'])


def test_healthy_stock_can_complete_both_directions_without_an_energy_hold():
    result=controlled_network_energy(*fixture(.8),ambient_c=25,regen_fraction=0)
    assert result['completed_journeys']==result['dispatch_opportunities']==12
    assert result['distinct_energy_held_journeys']==0 and not result['missed_dispatches']


def test_grid_recovery_releases_held_trains_and_restores_future_availability():
    values=list(fixture())
    values[6]={k:dict(initial_soc=.2,modules=1,pv_kw=0,grid_kw=60,charger_kw=60,contact_count=2,
        allow_grid_storage_recharge=True,storage_recharge_target_soc=.8) for k in 'abc'}
    result=controlled_network_energy(*values,ambient_c=25,regen_fraction=0,outages=set(range(10)))
    assert result['distinct_energy_held_journeys']==2
    assert result['completed_journeys']>2
    assert all(j['finish_minute'] is None or j['finish_minute']>=10 for j in result['journeys'])


def test_full_idle_packs_release_shared_charging_contacts():
    values=list(fixture(.01))
    values[5]['line-train-001']['initial_soc']=1
    values[0]['lines'][0].update(shape='ring',length_m=3000,ring_wrap_length_m=1000)
    values[1]['lines'][0]['ring_wrap_length_m']=1000
    values[1]['fleets'][0]['dispatch_points'][1]['station']='a'
    values[2]['sections'] += [dict(line='line',heading=h,from_station=a,to_station=b,distance_m=1000,travel_seconds=60)
        for h,a,b in [('forward','c','a'),('reverse','a','c')]]
    # Both headings share one contact before dispatch; a full pack must yield it.
    values[1]['fleets'][0]['schedule'][0]['from']='00:10'
    values[6]={'a':dict(initial_soc=.2,modules=1,pv_kw=0,grid_kw=600,charger_kw=600,contact_count=1)}
    result=controlled_network_energy(*values,ambient_c=25,regen_fraction=0)
    assert any(j['heading']=='reverse' and j['start_minute']==10 for j in result['journeys'])
