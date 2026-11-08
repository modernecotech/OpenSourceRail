"""Mapped corridor ancestry and geometry; these are not surveyed site evidence."""
from copy import deepcopy
from pathlib import Path
import pytest
from engineering.outline import city_inputs
from engineering.station_rail.common import identity
from engineering.railway_project import route


@pytest.fixture(scope='module')
def baghdad():return city_inputs.load('baghdad',root=Path.cwd())


def test_mapped_city_corridor_retains_stations_and_excludes_old_vehicle_cost(baghdad):
    line=baghdad['lines'][0];a,b=line['stops'][6],line['stops'][9]
    result=route.from_catalogue('baghdad',line['line_id'],a['id'],b['id'])
    assert result['station_count']==4
    assert [s['id'] for s in result['source_stops']]==[s['id'] for s in line['stops'][6:10]]
    assert abs(result['route_m']-sum(x['distance_m'] for x in result['legs']))<1e-3
    assert result['source_city_input_id']==baghdad['input_id']
    assert result['legacy_capacity_schedule_and_price_imported'] is False
    assert result['detailed_vehicle_selected'] is False and result['site_evidence']['grade'].startswith('unknown')
    assert result['evaluation_id']==identity({k:v for k,v in result.items() if k!='evaluation_id'})


def test_direction_and_missing_stop_are_not_silently_repaired(baghdad):
    line=baghdad['lines'][0];a,b=line['stops'][0],line['stops'][2]
    with pytest.raises(ValueError):route.from_catalogue('baghdad',line['line_id'],b['id'],a['id'])
    with pytest.raises(ValueError):route.from_catalogue('baghdad',line['line_id'],a['id'],'invented-stop')
    with pytest.raises(ValueError):route.from_catalogue('baghdad',line['line_id'],a['id'],b['id'],wrap_ring=True)


def test_changed_city_cannot_reuse_its_original_seal(baghdad):
    city=deepcopy(baghdad);city['lines'][0]['route_m']+=10
    line=city['lines'][0]
    with pytest.raises(ValueError,match='Sealed'):
        route._slice(city,line['line_id'],line['stops'][0]['id'],line['stops'][1]['id'])


def test_population_evidence_changes_evaluation_not_physical_route(baghdad):
    line=baghdad['lines'][0];args=(line['line_id'],line['stops'][0]['id'],line['stops'][2]['id'])
    before=route._slice(baghdad,*args)
    city=deepcopy(baghdad);city['city']['population_retained_unaccepted']+=100
    city['input_id']=identity({k:v for k,v in city.items() if k!='input_id'})
    after=route._slice(city,*args)
    assert before['corridor_geometry_id']==after['corridor_geometry_id']
    assert before['evaluation_id']!=after['evaluation_id']
