from copy import deepcopy

from shapely.geometry import LineString

from engineering.outline import city_alignment, network_policy


def _line(line_id, shape, coordinates, platforms):
    chainages = city_alignment.chainages(coordinates)
    return dict(line_id=line_id, shape=shape, coordinates=coordinates,
                coordinate_chainages_m=chainages, route_m=chainages[-1], stops=[
                    dict(id=stop_id, lon=coordinates[index][0], lat=coordinates[index][1],
                         chainage_m=chainages[index]) for index, stop_id in platforms])


def _network():
    approach = _line('approach', 'radial',
        [[-.04, 0], [-.03, 0], [-.02, 0], [.02, 0], [.03, 0], [.04, 0]],
        [(0, 'west'), (1, 'aw'), (2, 'bw'), (3, 'be'), (4, 'ae'), (5, 'east')])
    outer = _line('outer', 'ring',
        [[-.03, 0], [-.03, .03], [.03, .03], [.03, 0], [.03, -.03], [-.03, -.03], [-.03, 0]],
        [(0, 'ow'), (3, 'oe')])
    inner = _line('inner', 'ring',
        [[-.02, 0], [-.02, .02], [.02, .02], [.02, 0], [.02, -.02], [-.02, -.02], [-.02, 0]],
        [(0, 'iw'), (3, 'ie')])
    interchanges = [
        dict(id=ring + bank, lines=['approach', ring], platforms=[approach_stop, ring_stop])
        for ring, bank, approach_stop, ring_stop in [
            ('outer', 'west', 'aw', 'ow'), ('outer', 'east', 'ae', 'oe'),
            ('inner', 'west', 'bw', 'iw'), ('inner', 'east', 'be', 'ie')]]
    length = approach['route_m']
    return dict(lines=[approach, outer, inner], interchanges=interchanges,
                civil_segments=[dict(line_id='approach', **{'class': 'bridge'},
                                     from_m=.45 * length, to_m=.55 * length)])


def test_named_river_and_both_nested_rings_need_actual_crossing_and_shared_platforms(monkeypatch):
    city = _network()
    monkeypatch.setattr(network_policy, '_river_axes',
                        lambda *_: {'River': [LineString([[0, -.05], [0, .05]])]})
    context = network_policy.prepare(city, None)
    original = network_policy.screen(city, city, context)
    assert original['applicability']['ring_ids'] == ['outer', 'inner']
    assert original['applicability']['river_name'] == 'River'
    assert original['well_spaced_ring_transfer_pairs'] == 2
    assert original['full_method_pass']

    modified = deepcopy(city)
    modified['civil_segments'][0]['assumed'] = True
    for interchange in modified['interchanges']:
        if interchange['id'].startswith('inner'):
            interchange['platforms'][1] = 'missing'
    screen = network_policy.screen(city, modified, context)
    assert not screen['full_method_pass']
    assert screen['geographic_interface_failures'] == 2
    assert screen['approaches'][0]['ring_interchanges']['inner'] == []
    assert len(screen['approaches'][0]['failures']) == 2


def test_bridge_label_without_an_actual_river_crossing_cannot_trigger_water_requirement(monkeypatch):
    city = _network()
    monkeypatch.setattr(network_policy, '_river_axes',
                        lambda *_: {'River': [LineString([[.025, -.05], [.025, .05]])]})
    context = network_policy.prepare(city, None)
    assert context['applicability']['water_status'] == 'no-corroborated-river-crossing'


def test_terminal_touch_or_tangent_does_not_certify_ring_crossing():
    city = _network()
    ring = network_policy._ring_polygons(city)['inner']
    terminal = _line('terminal', 'radial', [[-.04, 0], [-.02, 0]],
                     [(0, 'a'), (1, 'b')])
    tangent = _line('tangent', 'radial', [[-.04, .03], [0., .02], [.04, .03]],
                    [(0, 'a'), (1, 'b'), (2, 'c')])
    for line in (terminal, tangent):
        assert not network_policy._ring_crossing_at_transfer(line, line['stops'][1]['chainage_m'], ring)


def _case(key, screen, cost):
    return dict(alignment_id=key, network_planning=screen,
                record=dict(cost=dict(whole_life_npv_usd=dict(base=cost))))


def test_no_map_or_ring_fallback_keeps_access_and_rejects_cheapest_unusable_option():
    city = _network()
    city['lines'] = city['lines'][:1]
    city['interchanges'] = []
    context = network_policy.prepare(city, None)
    original = network_policy.screen(city, city, context)
    assert original['applicability']['water_status'] == 'map-context-unavailable'
    assert original['applicability']['ring_status'] == 'no-linked-ring'

    revised = deepcopy(city)
    revised['lines'][0]['stops'][1]['lat'] = .000001
    moved = network_policy.screen(city, revised, context)
    assert not moved['retained_station_access']
    cases = [_case('moved', moved, 1), _case('original', original, 5)]
    assert network_policy.choose(cases, [0, 1], automatic=True) == (
        1, 'direct-approaches-with-local-applicability')
    assert network_policy.choose(cases, [0], automatic=True)[1] == 'requires-revision'
    assert network_policy.choose(cases, [0, 1], automatic=False) == (0, 'explicit-scenario')


def test_applicable_full_method_beats_cheaper_missing_crossing_and_is_deterministic(monkeypatch):
    city = _network()
    monkeypatch.setattr(network_policy, '_river_axes',
                        lambda *_: {'River': [LineString([[0, -.05], [0, .05]])]})
    context = network_policy.prepare(city, None)
    original = network_policy.screen(city, city, context)
    revised = deepcopy(city)
    revised['civil_segments'] = []
    missed = network_policy.screen(city, revised, context)
    cases = [_case('missed', missed, 1), _case('z', original, 5), _case('a', original, 5)]
    assert network_policy.choose(cases, [0, 1, 2], automatic=True) == (
        2, 'direct-river-and-two-ring-approaches')
    assert network_policy.choose(cases, [0], automatic=True) == (0, 'bounded-retained-corridor-fallback')
