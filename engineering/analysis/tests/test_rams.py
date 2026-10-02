import math

import pytest

from engineering.analysis import rams


def test_adiabatic_energy_balance_and_time_limit():
    inputs=dict(initial_c=30,ambient_c=50,heat_w=1000,capacity_j_k=10000,conductance_w_k=0)
    assert rams.temperature(100,**inputs)==40
    assert rams.time_to_limit(**inputs,limit_c=50)==200
    assert rams.time_to_limit(**{**inputs,"heat_w":0},limit_c=50) is None
    almost_adiabatic={**inputs,'conductance_w_k':1e-300}
    assert rams.temperature(100,**almost_adiabatic)==pytest.approx(40)
    assert rams.time_to_limit(**almost_adiabatic,limit_c=50)==pytest.approx(200)


def test_heat_transfer_equilibrium_and_initial_limit():
    inputs=dict(initial_c=20,ambient_c=20,heat_w=100,capacity_j_k=1000,conductance_w_k=10)
    assert rams.temperature(100,**inputs)==pytest.approx(30-10/math.e)
    assert rams.time_to_limit(**inputs,limit_c=25)==pytest.approx(100*math.log(2))
    assert rams.time_to_limit(**inputs,limit_c=30) is None
    assert rams.time_to_limit(**inputs,limit_c=20)==0


def test_shared_and_repeated_events_are_not_independent_duplicates():
    a,b,c=({'event':i} for i in ('A','B','C'))
    tree={'or':[a,{'and':[b,c]},{'and':[a,b]}]}
    assert rams.minimal_cut_sets(tree)==[['A'],['B','C']]
    assert rams.exact_probability(tree,{'A':.1,'B':.2,'C':.3})==pytest.approx(.1+.9*.2*.3)
    duplicate={'and':[a,a]}
    assert rams.exact_probability(duplicate,{'A':.1})==pytest.approx(.1)


def bounds(a,b,unit='1/h'):
    return dict(low=a,high=b,basis='illustrative-assumption',unit=unit)


def test_repair_and_redundancy_change_availability():
    events=[dict(id=i,event_class='hardware-random',failure_rate_per_h=bounds(.01,.01),repair_h=bounds(10,10,'h')) for i in ('A','B')]
    out=rams.fault_tree_screen({'and':[{'event':'A'},{'event':'B'}]},events,1,independence=True)
    assert out['steady_state_availability']==pytest.approx([1-(.1/1.1)**2]*2)
    assert out['mission_top_event_probability']==pytest.approx([(1-math.exp(-.01))**2]*2)
    assert rams.fault_tree_screen({'event':'A'},events,1,independence=False)['mission_top_event_probability'] is None


def test_unknown_systematic_events_preserve_probability_uncertainty():
    unknown=dict(low=None,high=None,basis='unknown',unit='1/h')
    events=[dict(id='hardware',event_class='hardware-random',failure_rate_per_h=bounds(.01,.02),repair_h=bounds(1,2,'h')),
            dict(id='software',event_class='software-systematic',failure_rate_per_h=unknown,repair_h={**unknown,'unit':'h'})]
    out=rams.fault_tree_screen({'and':[{'event':'hardware'},{'event':'software'}]},events,1,independence=True)
    assert out['mission_top_event_probability'][0]==0
    assert out['mission_top_event_probability'][1]==pytest.approx(1-math.exp(-.02))
    assert out['unknown_events']==['software']
    events[1]['failure_rate_per_h']=bounds(.001,.002)
    with pytest.raises(ValueError,match='systematic'):
        rams.fault_tree_screen({'event':'software'},events,1,independence=True)


def test_latent_exposure_interval_and_small_rate_stability():
    assert rams.latent_exposure(0,100)==0
    assert rams.latent_exposure(1e-12,100)==pytest.approx(5e-11)
    period=rams.inspection_interval(1e-5,.001)
    assert rams.latent_exposure(1e-5,period)==pytest.approx(.001)
    assert rams.inspection_interval(0,.001) is None


def test_brake_restriction_satisfies_available_distance():
    out=rams.braking_screen(300,2,.5)
    speed=out['maximum_speed_m_s']
    assert speed*2+speed*speed/(2*.5)==pytest.approx(300)
    assert rams.braking_screen(300,3,.3)['maximum_speed_m_s']<speed


def test_queue_and_spares_account_for_repair_and_turnaround():
    low=rams.maintenance_screen(100,.001,4,24,1,.01)
    high=rams.maintenance_screen(100,.002,8,72,1,.01)
    assert high['repair_crews']>low['repair_crews']
    assert high['minimum_spares']>low['minimum_spares']
    assert high['mean_queue_wait_h']<=1
    assert high['pipeline_stockout_probability']<=.01
    assert rams.maintenance_screen(100,0,4,24,1,.01)['repair_crews']==0


@pytest.mark.parametrize('value',[float('nan'),float('inf'),-1,True])
def test_invalid_rates_are_rejected(value):
    with pytest.raises(ValueError):
        rams.latent_exposure(value,24)


def test_unbounded_thermal_cases_and_missing_evidence_are_not_finite_answers():
    units=dict(initial_c='degC',ambient_c='degC',heat_w='W',capacity_j_k='J/K',conductance_w_k='W/K',limit_c='degC')
    inputs={key:bounds(value,value,units[key]) for key,value in dict(initial_c=20,ambient_c=20,heat_w=10,capacity_j_k=1000,conductance_w_k=1,limit_c=40).items()}
    out=rams.thermal_screen(inputs,[0,100])
    assert out['time_to_limit_s'] is None
    assert out['some_cases_do_not_reach_limit'] is True
    inputs['capacity_j_k']=dict(low=None,high=None,basis='unknown',unit='J/K')
    assert rams.thermal_screen(inputs,[0,100])['state']=='input-evidence-open'
