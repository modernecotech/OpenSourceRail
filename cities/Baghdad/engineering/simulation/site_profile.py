"""Size a desk-study rail profile from a source-bound terrain sample."""

from bisect import bisect_right
from hashlib import sha256
from itertools import accumulate, pairwise
from math import atan2, cos, degrees, hypot, isfinite, radians, sin
from pathlib import Path

from . import airport_alignment, corridor


def _interpolate(chainage, chainages, values):
    index = max(0, min(bisect_right(chainages, chainage) - 1, len(chainages) - 2))
    fraction = (chainage - chainages[index]) / (chainages[index + 1] - chainages[index])
    return values[index] + fraction * (values[index + 1] - values[index])


def _coordinate_at(chainage, vertices, points):
    index = min(bisect_right(vertices, chainage) - 1, len(vertices) - 2)
    a, b = points[index:index + 2]
    if chainage == vertices[index]:
        return a
    if chainage == vertices[index + 1]:
        return b
    fraction = (chainage - vertices[index]) / (vertices[index + 1] - vertices[index])
    angle = 1000 * corridor.distance_km(a, b) / 6_371_000
    weights = (sin((1 - fraction) * angle) / sin(angle), sin(fraction * angle) / sin(angle))
    vectors = [(cos(radians(lat)) * cos(radians(lon)), cos(radians(lat)) * sin(radians(lon)),
                sin(radians(lat))) for lon, lat in (a, b)]
    x, y, z = (sum(weight * component for weight, component in zip(weights, axis, strict=True))
               for axis in zip(*vectors, strict=True))
    return [degrees(atan2(y, x)), degrees(atan2(z, hypot(x, y)))]


def _grade_envelope(chainages, floors, max_slope):
    levels = floors.copy()
    for i in range(1, len(levels)):
        levels[i] = max(levels[i], levels[i - 1] - max_slope * (chainages[i] - chainages[i - 1]))
    for i in range(len(levels) - 2, -1, -1):
        levels[i] = max(levels[i], levels[i + 1] - max_slope * (chainages[i + 1] - chainages[i]))
    return levels


def derive_site_profile(layers, alignment, *, soffit_clearance_m=6.0,
                        rail_to_soffit_m=2.0, max_grade_pct=0.6, platform_length_m=140.0):
    """Raise a rail profile above the DSM and flatten a length at each stop."""
    if layers["alignment_id"] != alignment["alignment_id"]:
        raise ValueError("Terrain samples belong to a different horizontal alignment")
    terrain = layers["sources"]["terrain"]
    if terrain.get("units") != "m" or not terrain.get("vertical_datum"):
        raise ValueError("The terrain layer needs heights in metres and an explicit vertical datum")
    settings = dict(soffit_clearance_m=soffit_clearance_m, rail_to_soffit_m=rail_to_soffit_m,
                    max_grade_pct=max_grade_pct, platform_length_m=platform_length_m)
    if not all(isfinite(value) and value > 0 for value in settings.values()) or max_grade_pct > 2:
        raise ValueError("Use positive planning dimensions and a grade within the motion model's 2% domain")
    rows = layers["samples"]
    source_chainages = [row["chainage_m"] for row in rows]
    source_ground = [row["ground_elevation_m"] for row in rows]
    points = airport_alignment.physical_record(alignment)["horizontal_trace"]
    vertices = list(accumulate((1000 * corridor.distance_km(a, b) for a, b in pairwise(points)), initial=0.0))
    route_m = vertices[-1]
    if (len(rows) < 2 or abs(source_chainages[0]) > 1e-4 or abs(source_chainages[-1] - route_m) > 1e-4
            or any(not 0 < b - a <= 100 for a, b in pairwise(source_chainages))
            or any(type(v) not in (int, float) or not isfinite(v) for v in source_ground)):
        raise ValueError("Terrain samples need finite elevations at both ends and gaps no greater than 100 m")
    source_chainages[0], source_chainages[-1] = 0.0, route_m
    stations = [1000 * distance for distance in alignment["chainages_km"]]
    stations[-1] = route_m
    if platform_length_m > route_m:
        raise ValueError("Platform trial length exceeds the corridor")
    platform_starts = [max(0.0, min(s - platform_length_m / 2, route_m - platform_length_m))
                       for s in stations]
    flats = [(start, start + platform_length_m) for start in platform_starts]
    if any(b[0] <= a[1] for a, b in pairwise(flats)):
        raise ValueError("Adjacent platform grade limits overlap")

    # Retain all original corners. Merge nearly identical inserted vertices, using
    # precise stop and plateau boundaries for the operating input.
    chainages = sorted(set(vertices + stations + [x for flat in flats for x in flat]))
    for sample in source_chainages:
        insert = bisect_right(chainages, sample)
        if min(abs(chainages[j] - sample) for j in (insert - 1, insert) if 0 <= j < len(chainages)) > 1e-4:
            chainages.insert(insert, sample)
    distances = [s - sum(max(0.0, min(s, b) - a) for a, b in flats) for s in chainages]
    ground = [_interpolate(s, source_chainages, source_ground) for s in chainages]
    floors = [elevation + soffit_clearance_m + rail_to_soffit_m for elevation in ground]
    rail = _grade_envelope(distances, floors, max_grade_pct / 100)
    coordinates = [_coordinate_at(s, vertices, points) for s in chainages]
    stops = [dict(id=stop["id"], vertex=chainages.index(s), coordinates=coordinates[chainages.index(s)])
             for s, stop in zip(stations, alignment["stops"], strict=True)]
    samples = []
    for row, s, ground_m in zip(rows, source_chainages, source_ground, strict=True):
        elevation = _interpolate(s, chainages, rail)
        height = elevation - ground_m
        samples.append({**row, "chainage_m": s, "rail_elevation_m": elevation, "deck_height_m": height,
                        "soffit_height_m": height - rail_to_soffit_m})
    datum = terrain["vertical_datum"]
    grade = airport_alignment.rail_level_profile(coordinates, datum, rail)
    maximum_absolute_grade = max(map(abs, grade["grades_pct"]))
    if (abs(grade["chainages_m"][-1] - route_m) > 0.001 or maximum_absolute_grade > max_grade_pct + 1e-6
            or min(row["soffit_height_m"] for row in samples) < soffit_clearance_m - 0.001):
        raise ValueError("Desk-study profile differs from its route, grade or clearance bounds")
    profile = dict(schema="osr-baghdad-airport-site-profile/1", alignment_id=alignment["alignment_id"],
                   layers_sha256=airport_alignment.identity(layers), route_m=route_m, settings=settings,
                   samples=samples, platform_grade_limits_m=flats,
                   maximum_absolute_grade_pct=maximum_absolute_grade,
                   source_sha256={Path(__file__).name: sha256(Path(__file__).read_bytes()).hexdigest()})
    profile["site_profile_id"] = airport_alignment.identity(profile)
    geometry = {"type": "LineString", "coordinates": coordinates}
    geometry_sha = airport_alignment.identity({"geometry": geometry, "stops": stops})
    profile["alignment_input"] = {
        "schema": airport_alignment.SURVEY_SCHEMA, "parent_candidate_id": alignment["parent_candidate_id"],
        "crs": "EPSG:4326", "document": "Airport GIS desk-study profile from sampled elevation data",
        "revision": profile["site_profile_id"],
        "verification_reference": "DEM and assumed rail envelope. Study geometry and platform sites.",
        "geometry": geometry, "geometry_sha256": geometry_sha, "stops": stops,
        "vertical_profile": {"geometry_sha256": geometry_sha, "datum": datum, "elevations_m": rail},
    }
    return profile
