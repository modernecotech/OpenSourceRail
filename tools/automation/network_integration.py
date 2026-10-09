"""Concept geometry and bounded interchange integration, separate from acceptance."""
from __future__ import annotations

from collections import defaultdict
import hashlib
import itertools
import math

from shapely.geometry import LineString, Point
from shapely.ops import linemerge, unary_union
from shapely.strtree import STRtree


def stable_id(kind, lines, xy):
    seed = '|'.join([kind, *sorted(lines), *(f'{v:.3f}' for v in xy)])
    return kind + '-' + hashlib.sha256(seed.encode()).hexdigest()[:12]


def parts(geometry):
    if geometry.is_empty:
        return []
    if hasattr(geometry, 'geoms'):
        return [piece for item in geometry.geoms for piece in parts(item)]
    return [geometry]


def complete_link_groups(stations, maximum_diameter_m):
    """No transitive or same-line amalgamation can exceed the full diameter."""
    if maximum_diameter_m <= 0:
        raise ValueError('positive interchange diameter required')
    ordered = sorted(stations, key=lambda s: s['id'])
    distances = {}
    edges = []
    for i, left in enumerate(ordered):
        for j in range(i + 1, len(ordered)):
            right = ordered[j]
            distance = round(math.dist(left['xy'], right['xy']), 3)
            distances[(i, j)] = distance
            if left['line'] != right['line'] and distance <= maximum_diameter_m:
                edges.append((distance, left['id'], right['id'], i, j))
    groups = {i: {i} for i in range(len(ordered))}
    owner = list(range(len(ordered)))
    for _, _, _, i, j in sorted(edges):
        a, b = owner[i], owner[j]
        if a == b:
            continue
        combined = groups[a] | groups[b]
        if any(distances[tuple(sorted((u, v)))] > maximum_diameter_m for u, v in itertools.combinations(combined, 2)):
            continue
        keep, remove = min(a, b), max(a, b)
        groups[keep] = combined
        del groups[remove]
        for member in combined:
            owner[member] = keep
    result = []
    for members in sorted(groups.values(), key=lambda g: sorted(ordered[i]['id'] for i in g)):
        rows = [ordered[i] for i in sorted(members)]
        lines = sorted({row['line'] for row in rows})
        if len(lines) < 2:
            continue
        maximum = max((distances[tuple(sorted(pair))] for pair in itertools.combinations(members, 2)), default=0)
        centre = [round(math.fsum(s['xy'][axis] for s in rows) / len(rows), 3) for axis in (0, 1)]
        result.append(dict(id=stable_id('complex', lines, centre), lines=lines,
                           platform_ids=[s['id'] for s in rows], maximum_platform_separation_m=maximum,
                           centre_xy=centre, actual_walking_distance_m=None, accessible_path_accepted=False,
                           physical_acceptance=False))
    return result


def geometry_interfaces(lines):
    """Identify crossings and continuous shared corridors without joining rail paths."""
    findings = []
    for (left, a), (right, b) in itertools.combinations(sorted(lines.items()), 2):
        intersection = parts(a.intersection(b))
        linear = [piece for piece in intersection if piece.geom_type == 'LineString' and piece.length > .001]
        if linear:
            joined = unary_union(linear)
            joined = linemerge(joined) if joined.geom_type != 'LineString' else joined
            for piece in parts(joined):
                centre = piece.interpolate(.5, normalized=True)
                coords = [[round(x, 3), round(y, 3)] for x, y in piece.coords]
                coords = min(coords, list(reversed(coords)))
                findings.append(dict(id=stable_id('shared-corridor', [left, right], [centre.x, centre.y]),
                                     kind='shared-corridor', lines=[left, right], xy=[round(centre.x, 3), round(centre.y, 3)],
                                     geometry_xy=coords, shared_length_m=round(piece.length, 3),
                                     required_treatment='coordinate four-track civil footprint or separate deck levels; do not duplicate coincident guideways',
                                     rail_connection_created=False, vertical_profile_accepted=False))
        for piece in intersection:
            if piece.geom_type != 'Point' or any(piece.distance(linear_piece) <= .001 for linear_piece in linear):
                continue
            findings.append(dict(id=stable_id('crossing', [left, right], [piece.x, piece.y]), kind='crossing',
                                 lines=[left, right], xy=[round(piece.x, 3), round(piece.y, 3)],
                                 required_treatment='grade-separated structure and separately reviewed passenger access; no implicit switch',
                                 rail_connection_created=False, vertical_profile_accepted=False))
    for name, line in sorted(lines.items()):
        if line.is_simple:
            continue
        coords = list(line.coords)
        segments = [LineString([a, b]) for a, b in zip(coords, coords[1:]) if a != b]
        tree = STRtree(segments)
        seen = set()
        for i, segment in enumerate(segments):
            for j in tree.query(segment, predicate='intersects'):
                j = int(j)
                if j <= i + 1 or (i == 0 and j == len(segments) - 1 and coords[0] == coords[-1]):
                    continue
                for piece in parts(segment.intersection(segments[j])):
                    centre = piece if piece.geom_type == 'Point' else piece.centroid
                    xy = [round(centre.x, 3), round(centre.y, 3)]
                    key = tuple(xy)
                    if key in seen:
                        continue
                    seen.add(key)
                    findings.append(dict(id=stable_id('self-crossing', [name], xy), kind='self-crossing', lines=[name], xy=xy,
                                         route_legs=[i, j], required_treatment='same-line flyover or reviewed reroute preserving residential access',
                                         rail_connection_created=False, vertical_profile_accepted=False))
    unique = {row['id']: row for row in findings}
    return [unique[key] for key in sorted(unique)]


def line_at_chainage(route, chainage_m, declared_length_m):
    if not 0 <= chainage_m <= declared_length_m + .002:
        raise ValueError('support chainage outside its line')
    point = route.interpolate(min(chainage_m, declared_length_m) * route.length / declared_length_m)
    return [round(point.x, 3), round(point.y, 3)]


def legs_at_interface(route, xy, declared_length_m, tolerance_m=.05):
    """Keep distinct visits to a self-crossing; a global projection loses one leg."""
    target = Point(xy)
    distance = 0.
    hits = []
    for a, b in zip(route.coords, list(route.coords)[1:]):
        segment = LineString([a, b])
        if segment.length and segment.distance(target) <= tolerance_m:
            chainage = (distance + segment.project(target)) * declared_length_m / route.length
            if not hits or abs(hits[-1] - chainage) > .05:
                hits.append(round(chainage, 3))
        distance += segment.length
    return hits
