import pytest
from osr_mech.coupled_scenario import allocate_od,line_opening,OPENING_PACKAGES,operating_cost
from osr_mech.station.circulation import continuous_path
from osr_mech.station_capacity import footprint_screen


def event(journey,train,line,a,b,depart,arrive):
    return dict(journey=journey,train=train,line=line,heading='forward',from_station=a,to_station=b,
        depart_minute=depart,arrival_minute=arrive,distance_m=1000)


def leg(line,a,b,walk=0):
    return dict(line=line,heading='forward',from_station=a,to_station=b,transfer_walk_minutes=walk)


def test_shared_section_capacity_limits_od_cohorts_and_transfers_charge_once():
    events=[event('one','t1','L1','a','b',5,10),event('one','t1','L1','b','c',11,16),
        event('two','t2','L2','x','y',15,20)]
    requests=[dict(id='first',arrival_minute=0,passengers=8,fare_iqd=100,legs=[leg('L1','a','b'),leg('L2','x','y',4)]),
        dict(id='second',arrival_minute=0,passengers=6,fare_iqd=100,legs=[leg('L1','a','c')])]
    result=allocate_od(events,requests,{'t1':10,'t2':10},[('b','x')])
    assert result['totals']['completed_paid_journeys']==10
    assert result['totals']['train_boardings']==18
    assert result['totals']['recognised_fare_iqd']==1000
    assert result['cohorts'][1]['unserved_passengers']==4
    assert result['actual_collected_receipts_iqd'] is None
    requests[0]['legs'][1]['transfer_walk_minutes']=6
    assert allocate_od(events,requests,{'t1':10,'t2':10},[('b','x')])['cohorts'][0]['completed_paid_journeys']==0


def test_a_partial_train_journey_can_deliver_a_short_od_but_not_an_unserved_destination():
    events=[event('partial','t1','line','a','b',5,10)]
    r=dict(id='short',arrival_minute=0,passengers=5,fare_iqd=100,legs=[leg('line','a','b')])
    assert allocate_od(events,[r],{'t1':10})['totals']['completed_paid_journeys']==5
    r['legs']=[leg('line','a','c')]
    assert allocate_od(events,[r],{'t1':10})['totals']['completed_paid_journeys']==0


def test_line_opening_waits_for_all_packages_and_keeps_unknown_cash_open():
    packages={k:dict(completion_date='2028-01-01',installed_cash_usd=1,accepted=True,acceptance_record=k) for k in OPENING_PACKAGES}
    packages['approvals']['completion_date']='2028-02-01'
    row=line_opening('line',packages)
    assert row['full_line_opening_date']=='2028-02-01' and row['known_bottleneck_packages']==['approvals']
    packages['stations']['completion_date']=None;packages['stations']['installed_cash_usd']=None
    row=line_opening('line',packages)
    assert row['full_line_opening_date'] is None and row['complete_scope_cash_usd'] is None
    assert not row['opening_accepted'] and not row['revenue_opening_adopted']


def test_energy_and_distance_are_costed_once_in_the_same_operating_scope():
    cost=operating_cost(100,20,.1,2,50)
    assert cost['total_modelled_opex_usd']==100


def test_alternating_cross_section_lanes_do_not_establish_a_connected_path():
    bounds=(-20,20,-4,4)
    obstacles=[(-15,0,-4,1),(0,15,-1,4)]
    assert not continuous_path(bounds,obstacles,1.5)
    assert continuous_path(bounds,[(-10,10,-1,1)],1.5)


def test_capacity_screen_does_not_clip_a_protruding_lift_to_hide_its_envelope():
    platform=dict(level='platform',y_mm=0,width_mm=8000)
    lift=dict(served_levels=['platform'],x_mm=0,y_mm=3000,width_mm=3500,length_mm=3500)
    with pytest.raises(ValueError,match='outside platform'):footprint_screen(platform,60,[lift])
