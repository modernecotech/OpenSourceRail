"""Rank parts of Baghdad where residents face a long walk to the proposed railway."""

from collections import defaultdict
from math import floor, isfinite

import numpy as np

from .holistic_network import LOCAL_METRES, Track


def _candidate_connections(point, network, tracks):
    stations = network["stations"]
    projected = np.asarray(point) * LOCAL_METRES
    # Rank the corridors by their closest point to the gap centre. Separately
    # give the nearest station on each corridor, which could be much farther away.
    distances = sorted((track.locate(point)[1], code) for code, track in tracks.items())
    nearby = []
    for distance, code in distances[:2]:
        line = network["lines"][code]
        ids = line["station_ids"]
        coordinates = np.asarray([stations[key]["coordinates"] for key in ids]) * LOCAL_METRES
        station_distances = np.linalg.norm(coordinates - projected, axis=1)
        index = int(station_distances.argmin())
        station_id = ids[index]
        station = stations[station_id]
        nearby.append({
            "line_id": code,
            "line_name": line.get("name", code),
            "alignment_distance_m": round(distance),
            "station_id": station_id,
            "station_name": station["name"] or station_id,
            "station_lines": sorted(station["lines"]),
            "station_distance_m": round(float(station_distances[index])),
        })
    return nearby


def prioritize(coverage_cells, network, *, tile_m=4000):
    """Rank disjoint planning areas by residents beyond the 1,200 m walk.

    Input points represent inhabited 1 km grid cells. Align the larger grid
    to the same local metre projection so a precinct has a stable ID even
    when line or station locations change. Use a weighted centre to describe
    each gap. Nearby distances are straight-line screening distances.
    """
    if type(tile_m) is not int or tile_m < 1000 or tile_m % 1000:
        raise ValueError("Planning areas must combine complete 1 km cells")
    groups = defaultdict(list)
    for row in coverage_cells:
        lon, lat = row["coordinates"]
        people, unmet = row["people"], row["beyond_1200_m"]
        if (not all(isfinite(value) for value in (lon, lat, people, unmet))
                or not (-180 <= lon <= 180 and -90 <= lat <= 90)
                or not 0 <= unmet <= people):
            raise ValueError("Invalid coverage cell coordinates or population")
        easting, northing = (floor(value * scale / tile_m)
                             for value, scale in zip((lon, lat), LOCAL_METRES, strict=True))
        groups[easting, northing].append((lon, lat, people, unmet))

    tracks = {code: Track(line["geometry"]) for code, line in network["lines"].items()}
    gaps = []
    for (east, north), cells in sorted(groups.items()):
        # Sorting the cells also fixes rounding order when the caller supplies
        # the same coverage file in a different order.
        cells.sort()
        population = sum(row[2] for row in cells)
        unmet = sum(row[3] for row in cells)
        if not unmet:
            continue
        coordinates = [round(sum(row[axis] * row[3] for row in cells) / unmet, 6) for axis in (0, 1)]
        bounds = [
            round(index * tile_m / float(LOCAL_METRES[axis]), 6)
            for index, axis in ((east, 0), (north, 1), (east + 1, 0), (north + 1, 1))
        ]
        gaps.append({
            "id": f"G-{east}-{north}",
            "coordinates": coordinates,
            "bounds_wsen": bounds,
            "people": population,
            "beyond_1200_m": unmet,
            "cell_count": len(cells),
            "nearby_rail": _candidate_connections(coordinates, network, tracks),
        })
    gaps.sort(key=lambda row: (-row["beyond_1200_m"], row["id"]))
    for rank, gap in enumerate(gaps, 1):
        gap["rank"] = rank
    return gaps
