from copy import deepcopy
import json

import pytest

from engineering.outline import city_atlas as atlas
from engineering.station_rail.common import encoded, identity
from engineering.design_search.model_cost import SCOPES


def seal(value, key='evaluation_id'):
    value.pop(key, None)
    value[key] = identity(value)
    return value


@pytest.fixture
def study():
    stops = [dict(id='a', lon=0., lat=0., chainage_m=0., dwell_s=35.),
             dict(id='b', lon=.01, lat=0., chainage_m=1000., dwell_s=35.)]
    line = dict(line_id='L', shape='radial', coordinates=[[0., 0.], [.01, 0.]],
        coordinate_chainages_m=[0., 1000.], route_m=1000., operational_route_m=1000., stops=stops)
    city = seal(dict(city=dict(slug='fixture', name='Fixture', country='IQ'),
        lines=[line], selection_id='selection', reference_candidate_ids=dict(candidate_id='candidate'),
        interchanges=[], source_sha256={}), 'input_id')
    req = dict(headway_s=200., peak_demand_pphpd=4000., operating_days_per_year=365, operating_hours_per_day=18.)
    design = dict(aux_kw_per_car=8., charge_efficiency=.9)
    s = seal(dict(active_trainsets=2, total_trainsets=3, train_km_per_day=648.,
        mechanical_work_kwh_per_direction_trip=4., requirements=req, design=design))
    complexes = [dict(operational_stop_id=stop['id'], original_stop_ids=[stop['id']],
        original_marker_walks=[dict(original_stop_id=stop['id'], along_route_connector_m=0.)],
        boarding_platform_intervals_m=[[stop['chainage_m']-60., stop['chainage_m']+60.]]) for stop in stops]
    duty = seal(dict(line_id='L', requirements=req, design=design, service=s,
        propulsion_hypothesis=seal(dict(kind='station-launch-reference'), 'research_configuration_id'),
        operational_stops=stops, station_repair=dict(complexes=complexes), legs=[dict(distance_m=1000.)]))
    services = seal(dict(city_input_id=city['input_id'], line_services=[duty], source_sha256={}, assumptions={}))
    amount = dict(low=10., base=20., high=30.)
    ledgers = [dict(line_id=str(i), scope=scope, costs_usd=amount) for i, scope in enumerate(SCOPES)]
    totals = {c: v*len(SCOPES) for c, v in amount.items()}
    cost = seal(dict(city_input_id=city['input_id'], input_line_services_id=identity(services['line_services']),
        installed_capital_usd=totals, whole_life_npv_usd=totals,
        scope_totals_usd={s:amount for s in SCOPES}, capital_lines=ledgers, lifecycle_lines=[],
        civil=dict(quantities=dict(route_m=1000.)), resources={}, source_sha256={}))
    detail = dict(city=city['city'], evaluation_id='outline', reference_candidate_ids=city['reference_candidate_ids'],
        research_configuration_id='configuration', outline_completion='accepted-calculated-outline',
        full_result_sha256='result', selected_alignment_id='alignment', selected_alignment_kind='original',
        qualification_requirements=['survey demand'], **atlas.FLAGS)
    geometry = dict(type='FeatureCollection', features=[dict(type='Feature',
        properties=dict(alignment_id='alignment'), geometry=dict(type='LineString', coordinates=line['coordinates']))])
    return detail, geometry, city, services, cost


def test_packet_preserves_same_candidate_geometry_ledgers_and_open_evidence(study):
    original = deepcopy(study)
    packet = atlas.build_record(*study)
    assert study == original
    assert packet['geometry'] == study[1]
    assert packet['identity']['service_evaluation_id'] == study[3]['evaluation_id']
    assert packet['costs']['capital_lines'] == study[4]['capital_lines']
    assert set(packet['costs']['scope_totals_usd']) == set(SCOPES)
    assert packet['lines'][0]['metrics']['annual_train_km'] == 648*365
    assert packet['lines'][0]['metrics']['electrical_traction_kwh_per_day'] is None
    complex_ = packet['lines'][0]['station_complexes'][0]
    assert complex_['boarding_platform_intervals_m'] == [[-60., 60.]]
    assert complex_['platform_coordinates'][0][0] == [0., 0.]
    assert complex_['access_connectors'][0]['from_coordinates'] == [0., 0.]
    assert packet['evidence']['surveyed_demand_available'] is False
    assert all(packet[k] is False for k in atlas.FLAGS)
    assert packet['packet_id'] == identity({k:v for k,v in packet.items() if k!='packet_id'})


@pytest.mark.parametrize('part,key', [(2,'input_id'), (3,'city_input_id'), (4,'input_line_services_id')])
def test_mixed_identity_and_resealed_cross_candidate_inputs_are_rejected(study, part, key):
    values = deepcopy(study)
    values[part][key] = 'different'
    if key != 'input_id':
        seal(values[part])
    with pytest.raises(ValueError, match='identity|Mixed'):
        atlas.build_record(*values)


def test_reusable_completed_workflow_record_and_deterministic_compression(study, tmp_path):
    detail, geometry, city, services, cost = deepcopy(study)
    detail.update(geometry_and_service=city, service_evaluation=services, cost=cost, alignment_geometry=geometry)
    packet = atlas.build_record(detail)
    a, b = tmp_path/'a.gz', tmp_path/'b.gz'
    atlas._write_gzip(a, packet); atlas._write_gzip(b, packet)
    assert a.read_bytes() == b.read_bytes()
    assert atlas._read(a) == packet
    detail['physical_accepted'] = True
    with pytest.raises(ValueError, match='release'):
        atlas.build_record(detail)


def test_resumable_compile_reuses_packet_and_verifier_rejects_tampering(study, tmp_path, monkeypatch):
    from engineering.outline import city_inputs, coordinator, city_project_cost
    detail, geometry, city, services, cost = study
    root = tmp_path/'source'; output = tmp_path/'atlas'
    detail['planning_seed'] = seal(dict(selected_city_input_id=city['input_id'],
        selected_service_evaluation_id=services['evaluation_id'], source_cost_evaluation_id=cost['evaluation_id'],
        source_outline_evaluation_id=detail['evaluation_id'], selected_alignment_id=detail['selected_alignment_id'],
        research_configuration_id=detail['research_configuration_id'], reference_candidate_ids=city['reference_candidate_ids'],
        source_sha256={}, rules={}), 'seed_id')
    base = root/atlas.completion_publication.PUBLICATION
    atlas._write_gzip(base/'cities/fixture.json.gz', detail)
    atlas._write_gzip(base/'maps/fixture.geojson.gz', geometry)
    published = dict(manifest_id='publication', source_sha256={})
    catalogue = dict(catalogue_id='catalogue', cities=[dict(city=city['city'])])
    monkeypatch.setattr(atlas.completion_publication, 'verify', lambda **kw:(published,catalogue))
    calls = []
    monkeypatch.setattr(coordinator, 'prepare', lambda root: {})
    monkeypatch.setattr(city_inputs, 'prepare', lambda root: {})
    def reconstruct(*args, **kw):
        calls.append(kw['verify_cost'])
        return city, services
    monkeypatch.setattr(atlas.planning_adapter, '_reconstruct', reconstruct)
    monkeypatch.setattr(city_project_cost, 'evaluate_city_cost', lambda *a, **kw:cost)
    manifest, summary = atlas.compile(output, root)
    assert calls == [True]
    assert summary['completed_cities'] == 1 and summary['pending_cities'] == []
    assert atlas.verify(output, root) == (manifest, summary)
    assert atlas.compile(output, root) == (manifest, summary)
    assert calls == [True]
    path = output/'cities/fixture.json.gz'
    packet = atlas._read(path); packet['costs']['installed_capital_usd']['base'] = 1.
    atlas._write_gzip(path, packet)
    with pytest.raises(ValueError, match='artifact differs'):
        atlas.verify(output, root)


def test_verified_workflow_adapter_keeps_edited_calculation_without_replay(study, monkeypatch):
    detail, geometry, city, services, cost = deepcopy(study)
    detail.update(geometry_and_service=city, service_evaluation=services, cost=cost,
        planning_revision_id='edited-revision')
    seal(detail)
    workflow = seal(dict(schema='osr-mapped-city-workflow/1', calculation_complete=True,
        city=city['city'], city_outline=detail, cases=[dict(kind='edited', alignment_id='alignment', record=detail)],
        source_sha256={}, **atlas.FLAGS))
    def forbidden(*args, **kwargs):
        raise AssertionError('Completed studies must not replay/reprice')
    monkeypatch.setattr(atlas.planning_adapter, '_reconstruct', forbidden)
    packet = atlas.from_study(workflow)
    assert packet['identity']['workflow_evaluation_id'] == workflow['evaluation_id']
    assert packet['identity']['planning_revision_id'] == 'edited-revision'
    assert packet['lines'][0]['coordinates'] == city['lines'][0]['coordinates']
    assert packet['costs']['capital_lines'] == cost['capital_lines']
    assert packet['geometry']['features'][0]['properties']['variant'] == 'edited'
    assert all(packet[k] is False for k in atlas.FLAGS)
