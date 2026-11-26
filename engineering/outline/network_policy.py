"""Default planning screen for direct city approaches and mapped transfers."""

from bisect import bisect_left, bisect_right
from collections import defaultdict
from math import fsum, isfinite
from pathlib import Path

from shapely.geometry import LineString, Point, Polygon, shape

from engineering.city_maps import basemap
from engineering.station_rail.common import digest
from . import city_alignment

PRODUCER = 'engineering/outline/network_policy.py'
SOURCE_SHA256 = {
    PRODUCER: digest(Path(__file__)),
    'engineering/city_maps/basemap.py': digest(Path(basemap.__file__)),
}
METHOD = 'direct-approaches/1'
MAXIMUM_DETOUR_RATIO = 1.10
MINIMUM_TRANSFER_SEPARATION_M = 650.
MAXIMUM_PLATFORM_SEPARATION_M = 25.
TRANSFER_CROSSING_CHECK_M = 50.


def crossing_failures(*, detour_ratio, maximum_detour_ratio, water_required, water_crossings,
                      required_ring_ids, ring_interchanges):
    """Check each approach against the mapped interfaces declared applicable."""
    failures = []
    if (not isfinite(detour_ratio) or detour_ratio < 1 - 1e-8
            or detour_ratio > maximum_detour_ratio + 1e-8):
        failures.append('Approach exceeds the directness bound')
    if water_required and water_crossings < 1:
        failures.append('Approach lacks a corroborated crossing of the applicable river')
    for ring_id in sorted(set(required_ring_ids)):
        if not ring_interchanges.get(ring_id):
            failures.append('Approach lacks a shared interchange with ' + ring_id)
    return failures


def _river_axes(city, root):
    paths = [(name, sha) for name, sha in city.get('source_sha256', {}).items()
             if name.endswith('/map-context.json.gz')]
    if not paths:
        return None
    if len(paths) != 1:
        raise ValueError('One retained map context is required for a city approach screen')
    name, sha = paths[0]
    root = Path(root).resolve()
    path = (root / name).resolve()
    if not path.is_relative_to(root) or digest(path) != sha:
        raise ValueError('Retained city map context differs')
    context = basemap.load(path)
    rivers = defaultdict(list)
    for feature in context['layers'].get('water', []):
        properties = feature['properties']
        geometry = feature['geometry']
        if properties.get('kind') == 'river' and properties.get('name') and geometry['type'] in (
                'LineString', 'MultiLineString'):
            rivers[properties['name']].append(shape(geometry))
    return rivers


def _bridge_axes(city, line):
    coordinates = line['coordinates']
    chainages = line['coordinate_chainages_m']
    first, last = line['stops'][0]['chainage_m'], line['stops'][-1]['chainage_m']
    for segment in city_alignment._runs(city, line):
        if segment['class'] != 'bridge' or segment.get('assumed'):
            continue
        low, high = max(first, segment['from_m']), min(last, segment['to_m'])
        if low >= high:
            continue
        yield LineString([
            city_alignment._at(coordinates, chainages, low),
            *coordinates[bisect_right(chainages, low):bisect_left(chainages, high)],
            city_alignment._at(coordinates, chainages, high),
        ])


def _crosses(bridges, river):
    return any(bridge.crosses(axis) for bridge in bridges for axis in river)


def _transfer_sites(city):
    """Record only declared interchanges with a live platform on both lines."""
    platforms = {line['line_id']: {stop['id']: stop for stop in line['stops']}
                 for line in city['lines']}
    transfers = defaultdict(list)
    for interchange in city.get('interchanges', []):
        stops = set(interchange.get('platforms', []))
        members = {}
        for line_id in interchange.get('lines', []):
            own = platforms.get(line_id, {})
            if len(matches := stops & own.keys()) == 1:
                members[line_id] = own[next(iter(matches))]
        for first, first_stop in members.items():
            for second, second_stop in members.items():
                if first == second:
                    continue
                if city_alignment.distance(
                        [first_stop['lon'], first_stop['lat']],
                        [second_stop['lon'], second_stop['lat']]) > MAXIMUM_PLATFORM_SEPARATION_M:
                    continue
                transfers[first, second].append((interchange['id'], first_stop['chainage_m']))
    return transfers


def _ring_polygons(city):
    loops = {}
    for line in city['lines']:
        if line['shape'] == 'ring' and line['coordinates'][0] == line['coordinates'][-1]:
            polygon = Polygon(line['coordinates'])
            if polygon.is_valid and polygon.area:
                loops[line['line_id']] = polygon
    return loops


def _rings(city, transfers):
    loops = _ring_polygons(city)
    approaches = [line['line_id'] for line in city['lines'] if line['shape'] == 'radial']
    ordered = sorted(loops, key=lambda ring_id: (-loops[ring_id].area, ring_id))
    for outer in ordered:
        for inner in ordered:
            if (inner != outer and loops[outer].contains_properly(loops[inner])
                    and any(transfers[line, outer] for line in approaches)
                    and any(transfers[line, inner] for line in approaches)):
                return [outer, inner], len(loops)
    linked = next((ring_id for ring_id in ordered if any(transfers[line, ring_id]
                                                        for line in approaches)), None)
    return ([linked] if linked else []), len(loops)


def prepare(original, root):
    """Derive applicability once from retained city inputs for the whole comparison."""
    axes = _river_axes(original, root)
    transfers = _transfer_sites(original)
    ring_ids, ring_count = _rings(original, transfers)
    river_name = None
    if axes:
        bridges = {line['line_id']: list(_bridge_axes(original, line))
                   for line in original['lines'] if line['shape'] == 'radial'}
        counts = {name: sum(_crosses(route, river) for route in bridges.values())
                  for name, river in axes.items()}
        river_name = next((name for name in sorted(counts, key=lambda name: (-counts[name], name))
                           if counts[name]), None)
    return dict(river_axes=axes.get(river_name, []) if axes else [],
                applicability=dict(
                    method=METHOD,
                    river_name=river_name,
                    water_status=('applicable-mapped-river' if river_name else
                                  'no-corroborated-river-crossing' if axes is not None else 'map-context-unavailable'),
                    ring_ids=ring_ids,
                    mapped_ring_count=ring_count,
                    ring_status={2: 'applicable-nested-pair', 1: 'applicable-single-ring',
                                 0: 'no-linked-ring'}[len(ring_ids)],
                    pedestrian_status='no-verified-pedestrian-network-in-outline-input',
                    maximum_detour_ratio=MAXIMUM_DETOUR_RATIO,
                    maximum_platform_separation_m=MAXIMUM_PLATFORM_SEPARATION_M,
                    transfer_crossing_check_m=TRANSFER_CROSSING_CHECK_M,
                    minimum_transfer_separation_m=MINIMUM_TRANSFER_SEPARATION_M))


def _access_points(city):
    return {(line['line_id'], stop['id']): (stop['lon'], stop['lat'])
            for line in city['lines'] for stop in line['stops']}


def _ring_crossing_at_transfer(line, chainage, polygon):
    if polygon is None:
        return False
    low = max(line['stops'][0]['chainage_m'], chainage - TRANSFER_CROSSING_CHECK_M)
    high = min(line['stops'][-1]['chainage_m'], chainage + TRANSFER_CROSSING_CHECK_M)
    if not low < chainage < high:
        return False
    first, second = (Point(city_alignment._at(line['coordinates'], line['coordinate_chainages_m'], dist))
                     for dist in (low, high))
    return ((polygon.contains(first) and polygon.disjoint(second))
            or (polygon.disjoint(first) and polygon.contains(second)))


def screen(original, revised, context):
    """Compare an outline candidate with unchanged station access and declared geography."""
    applicability = context['applicability']
    current_access = _access_points(revised)
    retained_access = all(current_access.get(key) == position
                          for key, position in _access_points(original).items())
    transfers = _transfer_sites(revised)
    rings = _ring_polygons(revised)
    approaches = []
    for line in revised['lines']:
        if line['shape'] != 'radial':
            continue
        line_id = line['line_id']
        start, end = line['stops'][0], line['stops'][-1]
        length = end['chainage_m'] - start['chainage_m']
        chord = city_alignment.distance([start['lon'], start['lat']], [end['lon'], end['lat']])
        ratio = length / chord if chord and length > 0 else None
        crossings = {ring_id: [(site_id, chainage) for site_id, chainage in transfers[line_id, ring_id]
                               if _ring_crossing_at_transfer(line, chainage, rings.get(ring_id))]
                     for ring_id in applicability['ring_ids']}
        ring_interchanges = {ring_id: sorted({site_id for site_id, _ in sites})
                             for ring_id, sites in crossings.items()}
        well_spaced = 0
        for ring_id, sites in ring_interchanges.items():
            if len(sites) >= 2:
                chainages = [chainage for _, chainage in crossings[ring_id]]
                well_spaced += max(chainages) - min(chainages) >= MINIMUM_TRANSFER_SEPARATION_M
        river_crossing = bool(context['river_axes'] and _crosses(_bridge_axes(revised, line),
                                                                  context['river_axes']))
        failures = crossing_failures(
            detour_ratio=ratio if ratio is not None else float('inf'),
            maximum_detour_ratio=MAXIMUM_DETOUR_RATIO,
            water_required=bool(applicability['river_name']), water_crossings=int(river_crossing),
            required_ring_ids=applicability['ring_ids'], ring_interchanges=ring_interchanges)
        approaches.append(dict(line_id=line_id, length_m=length, chord_m=chord, detour_ratio=ratio,
                               river_crossing=river_crossing, ring_interchanges=ring_interchanges,
                               well_spaced_ring_transfer_pairs=well_spaced, failures=failures))
    required_failures = sum((bool(applicability['river_name']) and not row['river_crossing'])
                            + sum(not sites for sites in row['ring_interchanges'].values())
                            for row in approaches)
    return dict(applicability=applicability, approaches=approaches,
                retained_station_access=retained_access,
                geographic_interface_failures=required_failures,
                well_spaced_ring_transfer_pairs=sum(row['well_spaced_ring_transfer_pairs'] for row in approaches),
                chord_excess_m=fsum(max(0., row['length_m'] - row['chord_m']) for row in approaches),
                full_method_pass=bool(approaches) and retained_access
                and all(not row['failures'] for row in approaches))


def choose(cases, passing, *, automatic):
    """Rank functional comparable proposals, keeping failures inspectable."""
    def cost(index):
        case = cases[index]
        return case['record']['cost']['whole_life_npv_usd']['base'], case['alignment_id']

    if not automatic:
        return min(passing or range(len(cases)), key=cost), 'explicit-scenario'
    comparable = [i for i in passing if cases[i]['network_planning']['retained_station_access']]
    if not comparable:
        return min(range(len(cases)), key=cost), 'requires-revision'
    full = [i for i in comparable if cases[i]['network_planning']['full_method_pass']]

    def ranked(index):
        result = cases[index]['network_planning']
        return (result['geographic_interface_failures'], -result['well_spaced_ring_transfer_pairs'],
                result['chord_excess_m'], *cost(index))

    chosen = min(full or comparable, key=ranked)
    application = cases[chosen]['network_planning']['applicability']
    if not full:
        status = 'bounded-retained-corridor-fallback'
    elif application['river_name'] and len(application['ring_ids']) == 2:
        status = 'direct-river-and-two-ring-approaches'
    else:
        status = 'direct-approaches-with-local-applicability'
    return chosen, status
