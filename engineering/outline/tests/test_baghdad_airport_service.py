from collections import Counter, defaultdict
from itertools import pairwise
import json
from xml.etree import ElementTree

import pytest

from cities.Baghdad.airport_service import build_service, terminal_screen, time_distance_svg
from engineering.outline import baghdad_diagrams as diagrams, baghdad_system as system


@pytest.fixture(scope='module')
def opening():
    cfg = system.load()
    group = json.loads(diagrams.PUBLICATION.read_bytes())['networks']['first']['groups']['Airport']
    return cfg, build_service(cfg, group)


def test_all_day_workings_reach_every_departure_and_return_to_depot(opening):
    cfg, service = opening
    group, terminal = service['group'], service['terminal']
    assert group['scheduled_trips'] == 144
    assert group['diagrammed_sets'] == 3
    assert group['sets_starting_at_A_B'] == group['sets_finishing_at_A_B'] == [2, 1]
    assert Counter((side, dep // 3600) for _, side, dep, _ in service['trips']) == {
        (side, h): 4 for side in (0, 1) for h in range(6, 24)}
    by_set = defaultdict(list)
    for train, side, dep, arr in service['trips'] + service['positioning_trips']:
        by_set[train].append((dep, arr, side))
    for train, sequence in by_set.items():
        path = sorted(sequence)
        assert path[0][2] == 0 and path[-1][2] == 1
        assert all(dep - arr >= 180 and a != b for (_, arr, a), (dep, _, b) in pairwise(path))
        yard = [row for row in terminal['yard_moves'] if row['train'] == train]
        assert len(yard) == 2
        assert yard[0]['end_s'] < path[0][0] < path[-1][1] < yard[1]['start_s']
    assert len(service['positioning_trips']) == 2
    assert service['non_revenue_km_per_day'] == 25.5
    assert cfg['vehicle']['peak_headway_s'] == 150
    assert service['scheduled_places_per_hour_direction'] == 2800


def test_separation_uses_timed_resources_and_rejects_a_conflicting_empty_path(opening):
    cfg, service = opening
    terminal = service['terminal']
    assert terminal['open_platform_faces_each_end'] == [1, 1]
    assert terminal['directional_interstation_blocks'] == 10
    assert terminal['train_fits'] and terminal['schedule_screen_passed'] and not terminal['conflicts']
    assert min(terminal['minimum_margin_s_by_resource'].values()) == 150
    for intervals in terminal['resources'].values():
        assert all(a['end_s'] <= b['start_s'] for a, b in pairwise(intervals))
    trips = service['trips'] + service['positioning_trips']
    outbound, inbound = service['positioning_trips']
    # A rescue set following these same two empty paths produces actual resource conflicts.
    altered = trips + [('rescue', *outbound[1:]), ('rescue', *inbound[1:])]
    collision = terminal_screen(cfg, service['group'], altered, service['patterns'], service['leg_profiles'])
    assert not collision['schedule_screen_passed']
    assert any(row['resource'].startswith('block-') for row in collision['conflicts'])
    assert not service['physical_accepted']


def test_leg_profiles_close_distance_and_full_day_plot_is_standalone(opening):
    cfg, service = opening
    for side, legs in enumerate(service['leg_profiles']):
        assert len(legs) == 5
        for leg in legs:
            coast, up, down = (leg[k] for k in ('cruise_s', 'acceleration_s', 'braking_s'))
            speed = leg['cruise_m_s']
            assert 0 < speed <= cfg['vehicle']['speed_cap_kmh'] / 3.6
            assert up + coast + down == pytest.approx(leg['arrival_s'] - leg['departure_s'])
            assert speed * (coast + .5*(up + down)) == pytest.approx(1000 * abs(leg['end_km']-leg['start_km']))
            assert (leg['end_km'] < leg['start_km']) == bool(side)
    svg = ElementTree.fromstring(time_distance_svg(service))
    titles = [t.text for t in svg.iter('{http://www.w3.org/2000/svg}title')]
    assert 'Airport-001 · passenger' in titles
    assert sum(' · empty' in title for title in titles) >= 2
    assert any('platform to depot' in title for title in titles)
    assert '00:00+1' in ''.join(svg.itertext())
