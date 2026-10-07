import pytest
from osr_mech.station.passenger_demand import station_passenger_demand


def fixture():
    design=dict(city=dict(slug='test'),lines=[dict(name='line',shape='linear')],stations=[dict(id=k,line='line',s_m=i*1000) for i,k in enumerate('abc')])
    scenario=dict(fleets=[dict(line='line',service_start='06:00',schedule=[dict(**{'from':'06:00','to':'09:00'},headway_min=3),dict(**{'from':'09:00','to':'12:00'},headway_min=6)])])
    register=dict(cities=dict(test=dict(survey_source='test-only',survey_date='2026-10-06',peak_window_start='08:00',peak_window_end='10:00',coverage_complete=False,
        assignments=[dict(id='cohort',passengers_hour=120,legs=[dict(from_station='a',to_station='c',heading='forward')])])))
    return design,scenario,register


def test_station_loads_follow_od_legs_and_the_actual_service_window():
    result=station_passenger_demand(*fixture())
    assert result['stations']['a']['recorded_boardings_hour']==120
    assert result['stations']['c']['recorded_alightings_hour']==120
    assert result['stations']['a']['peak_waiting_accumulation_pax']==12
    assert len(result['section_peak_loads'])==2
    assert not result['forecast_accepted']


def test_empty_assignment_is_unknown_and_wrong_direction_is_rejected():
    design,scenario,register=fixture()
    empty=station_passenger_demand(design,scenario,{'cities':{}})
    assert all(row['recorded_boardings_hour'] is None for row in empty['stations'].values())
    register['cities']['test']['assignments'][0]['legs'][0]['heading']='reverse'
    with pytest.raises(ValueError,match='direction'):station_passenger_demand(design,scenario,register)
