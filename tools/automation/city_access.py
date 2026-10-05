"""Population and transfer accounting, separate from routing-demand scores.

Population inputs are retained native WorldPop count pixels, never smoothed
demand, averaged/resampled counts or a fraction of an unrelated city total.
"""
from __future__ import annotations

from collections import deque
import math

import numpy as np

EARTH_RADIUS_M = 6_371_000.0


def xyz(lat, lon):
    lat = np.radians(lat)
    lon = np.radians(lon)
    return np.column_stack((np.cos(lat) * np.cos(lon),
                            np.cos(lat) * np.sin(lon), np.sin(lat)))


def transfer_audit(design):
    """Shortest number of transfers through declared passenger interchanges.

    A geometric crossing alone does not create a passenger transfer. Explicit
    interchange membership, station junction groups and shared platform IDs
    are unioned; partial explicit records must not hide other valid groups.
    """
    names = [str(line.get('id') or line['name']) for line in design.get('lines', [])]
    if len(set(names)) != len(names):
        raise ValueError('Duplicate line IDs')
    graph = {name: set() for name in names}
    groups = [set(map(str, item.get('lines', []))) for item in design.get('interchanges', [])]
    junctions = {}
    station_lines = {}
    for station in design.get('stations', []):
        line = str(station.get('line', ''))
        if station.get('junction_group') is not None:
            junctions.setdefault(station['junction_group'], set()).add(line)
        station_lines.setdefault(str(station['id']), set()).add(line)
    for line in design.get('lines', []):
        name = str(line.get('id') or line['name'])
        for station in line.get('station_ids', []):
            station_lines.setdefault(str(station), set()).add(name)
    groups += list(junctions.values()) + list(station_lines.values())
    for group in groups:
        members = group & graph.keys()
        for name in members:
            graph[name].update(members - {name})
    distances = {}
    components = []
    seen = set()
    pairs = []
    for index, name in enumerate(names):
        distance = {name: 0}
        queue = deque([name])
        while queue:
            node = queue.popleft()
            for neighbour in sorted(graph[node]):
                if neighbour not in distance:
                    distance[neighbour] = distance[node] + 1
                    queue.append(neighbour)
        distances[name] = distance
        if name not in seen:
            component = sorted(distance)
            components.append(component)
            seen.update(component)
        for other in names[index + 1:]:
            pairs.append(dict(lines=[name, other], minimum_transfers=distance.get(other)))
    total = len(pairs)
    fraction = lambda predicate: sum(predicate(row) for row in pairs) / total if total else (1.0 if names else None)
    return dict(line_count=len(names), line_pair_count=total, components=components,
                direct_transfer_fraction=fraction(lambda row: row['minimum_transfers'] == 1),
                reachable_line_pair_fraction=fraction(lambda row: row['minimum_transfers'] is not None),
                reachable_with_at_most_two_transfers_fraction=fraction(
                    lambda row: row['minimum_transfers'] is not None and row['minimum_transfers'] <= 2),
                maximum_required_transfers=max((row['minimum_transfers'] for row in pairs
                                               if row['minimum_transfers'] is not None), default=0),
                pairs=pairs,
                basis='Declared passenger-transfer topology; no pedestrian accessibility, timetable or travel-time acceptance implied.')


def population_audit(latitudes, longitudes, counts, valid, design,
                     radii=(500, 800, 1000, 1500, 2000)):
    """Union station catchments on the sphere, counted once per native pixel.

    The denominator is valid population inside the retained raster window.
    Missing pixels are explicit; station circles are potential radial access,
    not verified walksheds. Feeder sensitivities require actual feeder plans.
    """
    from scipy.spatial import cKDTree
    lat = np.asarray(latitudes, dtype=float).reshape(-1)
    lon = np.asarray(longitudes, dtype=float).reshape(-1)
    pop = np.asarray(counts, dtype=float).reshape(-1)
    known = np.asarray(valid, dtype=bool).reshape(-1)
    if not (lat.size == lon.size == pop.size == known.size):
        raise ValueError('Population coordinate/count/mask dimensions differ')
    if np.any(known & (~np.isfinite(pop) | (pop < 0))) or not np.all(np.isfinite(lat) & np.isfinite(lon)):
        raise ValueError('Invalid population counts or coordinates')
    total = math.fsum(pop[known])
    stations = {(float(s['lat']), float(s['lon'])) for s in design.get('stations', [])}
    points = xyz(lat, lon)
    if stations:
        coordinates = np.asarray(sorted(stations))
        chord, _ = cKDTree(xyz(coordinates[:, 0], coordinates[:, 1])).query(points)
        distances = 2 * EARTH_RADIUS_M * np.arcsin(np.minimum(1.0, chord / 2))
    else:
        distances = np.full(lat.shape, np.inf)
    rows = []
    for radius in sorted(set(radii)):
        if radius <= 0:
            raise ValueError('Catchment radius must be positive')
        covered = math.fsum(pop[known & (distances <= radius + 1e-7)])
        rows.append(dict(radius_m=radius, covered_population_2020=covered,
                         fraction_of_raster_population=covered / total if total > 0 else None,
                         interpretation='Radial station-access sensitivity; barriers and entrance paths unverified.'
                         if radius <= 1000 else 'Extended radial/feeder sensitivity; no feeder service assumed or funded.'))
    return dict(status='available' if total > 0 else 'no-positive-population',
                population_year=2020, bbox_population_2020=total,
                valid_pixels=int(known.sum()), missing_pixels=int((~known).sum()),
                unique_station_coordinates=len(stations), catchments=rows,
                planning_city_population=design['city']['population'],
                denominator='Sum of valid native population-count pixels inside the city bounding box; no scaling to catalogue population.',
                basis='Great-circle distance from native population pixel centres to station coordinates; union without double counting.',
                limitations=['Population year/boundary differs from the catalogue; counts are not current census counts.',
                             'Radial access can overstate walking access across rivers, motorways, walls or steep terrain.',
                             'No fare demand, unique passengers, feeder revenue or funding improvement is inferred.'])


def transfer_recovery_candidates(design):
    """Shortest straight-distance component links for walking/connector survey.

    These are investigation candidates, never declared passenger transfers.
    Barriers, entrances, steps, timing, safety and property rights remain unknown.
    """
    components=transfer_audit(design)['components']
    if len(components)<=1:return []
    stations=design.get('stations',[])
    candidates=[]
    for i,left in enumerate(components):
        a=[s for s in stations if s['line'] in left]
        for j in range(i+1,len(components)):
            b=[s for s in stations if s['line'] in components[j]]
            if not a or not b:continue
            best=None
            for x in a:
                for y in b:
                    p,q=xyz([x['lat'],y['lat']],[x['lon'],y['lon']])
                    distance=float(2*EARTH_RADIUS_M*math.asin(min(1.,float(np.linalg.norm(p-q))/2)))
                    if best is None or distance<best[0]:best=(distance,x,y)
            distance,x,y=best
            candidates.append(dict(components=[i,j],stations=[x['id'],y['id']],lines=[x['line'],y['line']],
                straight_distance_m=distance,walk_time_minutes=None,accessible_path_accepted=False,
                barrier_and_height_clearance_accepted=False,transfer_created=False,
                required_evidence=['surveyed entrances and accessible pedestrian path','river/road/wall crossings',
                    'walking/vertical access and transfer time','property and operating approval']))
    # A minimum spanning candidate tree reduces duplicated survey effort while
    # leaving the actual transfer graph and its reachable pairs unchanged.
    roots=list(range(len(components)));selected=[]
    def root(i):
        while roots[i]!=i:i=roots[i]
        return i
    for candidate in sorted(candidates,key=lambda r:(r['straight_distance_m'],r['stations'])):
        i,j=(root(v) for v in candidate['components'])
        if i==j:continue
        roots[j]=i;selected.append(candidate)
    return selected
