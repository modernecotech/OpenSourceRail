import importlib.util
from pathlib import Path

import pytest

from engineering.outline import planning_geometry


RUNNER = (Path(__file__).resolve().parents[1] /
    'docs/design-engine/v06-design-closure/samawah-current-source-cost-recalculation-01/run.py')
SPEC = importlib.util.spec_from_file_location('samawah_cost_recalculation', RUNNER)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def _lon(metres):
    return metres / 111_195.0


def test_current_source_simplification_keeps_station_anchors_and_deviation_bound():
    coordinates = [[_lon(0), 0.0], [_lon(250), 0.00004], [_lon(500), 0.00009],
                   [_lon(750), 0.00004], [_lon(1000), 0.0]]
    chain = planning_geometry.route(coordinates, 'radial')
    stops = []
    for stop_id, at in (('A', 0.0), ('B', chain[2]), ('C', chain[-1])):
        point = planning_geometry.point(coordinates, chain, at)
        stops.append(dict(id=stop_id, chainage_m=at, dwell_s=30.0, lon=point[0], lat=point[1]))
    line = dict(id='line-1', shape='radial', coordinates=coordinates, stops=stops,
                design_speed_cap_m_s=20.0)

    simplified, revised_stops, detail = MODULE._simplify_canonical_line(
        line, 20.0, planning_geometry)

    assert detail['maximum_sampled_deviation_m'] <= 20.05
    assert detail['station_coordinates_moved'] is False
    assert [row['id'] for row in revised_stops] == ['A', 'B', 'C']
    new_chain = planning_geometry.route(simplified, 'radial')
    for stop, revised in zip(stops, revised_stops):
        assert stop['id'] == revised['id']
        point = planning_geometry.point(simplified, new_chain, revised['chainage_m'])
        assert MODULE._haversine_m(point, [stop['lon'], stop['lat']]) <= 0.001


def test_current_source_simplification_rejects_station_off_route():
    coordinates = [[_lon(0), 0.0], [_lon(500), 0.0], [_lon(1000), 0.0]]
    chain = planning_geometry.route(coordinates, 'radial')
    line = dict(id='line-1', shape='radial', coordinates=coordinates,
        stops=[dict(id='A', chainage_m=0.0, dwell_s=30.0, lon=coordinates[0][0], lat=0.0),
               dict(id='B', chainage_m=chain[-1], dwell_s=30.0,
                    lon=coordinates[-1][0], lat=0.00001)],
        design_speed_cap_m_s=20.0)

    with pytest.raises(ValueError, match='canonical stop is not on current route'):
        MODULE._simplify_canonical_line(line, 25.0, planning_geometry)


def test_request_uses_screen_only_as_geometry_tolerance_context():
    request_path = RUNNER.parent / 'request.json'
    import json
    request = json.loads(request_path.read_text(encoding='utf-8'))
    assert request['geometry_proposal']['maximum_deviation_m'] == 20.0
    assert 'tolerance context only' in request['geometry_proposal']['use_as']


def test_city_verifier_success_is_bound_to_returned_manifest_identity():
    assert MODULE._replay_verified({'evaluation_id': 'a'}, {'evaluation_id': 'a'}, True)
    assert MODULE._replay_verified({'evaluation_id': 'a'}, {'evaluation_id': 'b'}, False) is False
    with pytest.raises(ValueError, match='returned manifest'):
        MODULE._replay_verified({'evaluation_id': 'a'}, {'evaluation_id': 'b'}, True)


def test_baseline_plan_binds_published_seed_and_new_study_evaluation():
    candidate_ids = {'candidate_id': 'candidate', 'body_candidate_id': 'body'}
    seed = {'seed_id': 'seed', 'reference_candidate_ids': candidate_ids}
    plan = dict(official_seed_id='seed', source_outline_evaluation_id='study-eval',
        outline_context={'seed': {'reference_candidate_ids': candidate_ids}})
    summary = {'outline_evaluation_id': 'study-eval'}
    assert MODULE._validate_base_plan(plan, seed, summary)
    with pytest.raises(ValueError, match='published vehicle or seed'):
        MODULE._validate_base_plan(plan, seed, {'outline_evaluation_id': 'wrong'})


def test_china_cost_label_does_not_claim_unmodeled_volume_discounts():
    description = MODULE.PRICING_DESCRIPTIONS['china-bulk-buy'].lower()
    assert 'no negotiated or blanket volume discount is applied' in description
    assert 'local-contractor proxies' in description

