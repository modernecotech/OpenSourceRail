"""Screen Baghdad's mapped rail centrelines for sustained duplication."""

from itertools import combinations
from math import cos, isfinite, radians

import numpy as np
from scipy.spatial import cKDTree

from .holistic_network import Track


class _Alignment:
    def __init__(self, line, sample_m):
        track = Track(line["geometry"])
        self.total = float(track.chainage[-1])
        self.loop = line.get("loop", False)
        self.points = track.points
        self.bounds = (self.points.min(axis=0), self.points.max(axis=0))
        self.edges = np.r_[np.arange(0.0, self.total, sample_m), self.total]
        self.mid = (self.edges[:-1] + self.edges[1:]) / 2

        def at(chainage):
            return np.column_stack([np.interp(chainage, track.chainage, axis)
                                    for axis in self.points.T])

        def tangent(chainage):
            chord = at(chainage + sample_m) - at(chainage - sample_m)
            norm = np.linalg.norm(chord, axis=1)
            index = np.searchsorted(track.chainage[1:], chainage)
            return np.divide(chord, norm[:, None],
                             out=track.delta[index] / track.lengths[index, None],
                             where=norm[:, None] > 1e-9)

        self.samples = at(self.mid)
        self.directions = tangent(self.mid)
        # Split long target segments to bound midpoint search without removing
        # any turns from the original alignment.
        nodes = np.unique(np.r_[track.chainage, self.edges])
        lengths = np.diff(nodes)
        keep = lengths > 1e-6
        self.starts = at(nodes[:-1][keep])
        self.delta = at(nodes[1:][keep]) - self.starts
        self.lengths = lengths[keep]
        self.chainage = nodes[:-1][keep]
        self.target_directions = tangent(self.chainage + self.lengths / 2)
        self.tree = cKDTree(self.starts + self.delta / 2)

    def nearest_aligned(self, source, nearby_m, sample_m, angle_cos):
        close = self.tree.query_ball_point(source.samples, nearby_m + sample_m / 2)
        observations = np.full((len(source.mid), 4), np.nan)
        counts = np.fromiter(map(len, close), dtype=int, count=len(close))
        if not counts.any():
            return observations

        source_i = np.repeat(np.arange(len(source.mid)), counts)
        target_i = np.concatenate(close[counts > 0]).astype(int)
        delta = self.delta[target_i]
        offset = source.samples[source_i] - self.starts[target_i]
        unbounded = (np.einsum("ij,ij->i", offset, delta)
                     / np.einsum("ij,ij->i", delta, delta))
        fraction = np.clip(unbounded, 0, 1)
        separation = offset - fraction[:, None] * delta
        distance = np.linalg.norm(separation, axis=1)
        directions = source.directions[source_i]
        dot = np.einsum("ij,ij->i", directions, self.target_directions[target_i])
        outside_end = (((target_i == 0) & (unbounded < 0))
                       | ((target_i == len(self.lengths) - 1) & (unbounded > 1)))
        eligible = (distance <= nearby_m) & (np.abs(dot) >= angle_cos)
        source_i, target_i = source_i[eligible], target_i[eligible]
        fraction, distance = fraction[eligible], distance[eligible]
        orientation = np.sign(dot[eligible])
        outside_end = outside_end[eligible]
        separation, directions = separation[eligible], directions[eligible]
        # Break equal-distance ties at vertices by original chainage.
        order = np.lexsort((target_i, distance, source_i))
        _, first = np.unique(source_i[order], return_index=True)
        best = order[first]
        # A tangent extension past a physical end has no matching track.
        best = best[~outside_end[best]]
        destination = target_i[best]
        signed_distance = (directions[:, 0] * separation[:, 1]
                           - directions[:, 1] * separation[:, 0])
        observations[source_i[best]] = np.column_stack((
            self.chainage[destination] + fraction[best] * self.lengths[destination],
            distance[best],
            signed_distance[best],
            orientation[best],
        ))
        return observations


def _continuous_runs(source, observations):
    match = np.isfinite(observations[:, 0])
    step = np.diff(source.mid)
    advance = np.diff(observations[:, 0])
    orientation = observations[:, 3]
    # The counterpart must progress along the other alignment. Allow pauses at
    # a corner, but bound jumps to another part of the target.
    connected = (match[:-1] & match[1:] & (orientation[:-1] == orientation[1:])
                 & (orientation[:-1] * advance >= -1e-6) & (np.abs(advance) <= 3 * step))
    cuts = np.r_[0, np.flatnonzero(~connected) + 1, len(match)]
    for start, end in zip(cuts[:-1], cuts[1:]):
        if end - start >= 2:
            yield start, end


def _straight_crossing(chainage, signed, common_m, sample_m):
    """Recognise a near-linear approach through a shallow crossing."""
    if (len(signed) < 3 or min(abs(signed[0]), abs(signed[-1])) <= common_m
            or signed[0] * signed[-1] >= 0):
        return False
    x = chainage - chainage.mean()
    slope = np.dot(x, signed) / np.dot(x, x)
    residual = signed - signed.mean() - slope * x
    return np.max(np.abs(residual)) <= sample_m / 10


def _codeparture(source, target, source_m, target_m, terminal_m):
    if source.loop or target.loop:
        return False
    for a, b in zip(source_m, target_m):
        a_index = 0 if a <= source.total / 2 else -1
        b_index = 0 if b <= target.total / 2 else -1
        a_end = 0 if a_index == 0 else source.total
        b_end = 0 if b_index == 0 else target.total
        if (abs(a - a_end) <= terminal_m and abs(b - b_end) <= terminal_m
                and np.linalg.norm(source.points[a_index] - target.points[b_index]) <= terminal_m):
            return True
    return False


def _pair_runs(a_id, b_id, a, b, *, sample_m, nearby_m, common_m, min_run_m,
               max_angle_deg, terminal_m):
    if np.any(a.bounds[0] - b.bounds[1] > nearby_m) or np.any(b.bounds[0] - a.bounds[1] > nearby_m):
        return
    observations = b.nearest_aligned(a, nearby_m, sample_m, cos(radians(max_angle_deg)))
    for start, end in _continuous_runs(a, observations):
        if a.edges[end] - a.edges[start] < min_run_m:
            continue
        distance, signed = observations[start:end, 1:3].T
        if _straight_crossing(a.mid[start:end], signed, common_m, sample_m):
            continue
        common = distance <= common_m
        cuts = np.r_[start, np.flatnonzero(common[1:] != common[:-1]) + start + 1, end]
        for first, stop in zip(cuts[:-1], cuts[1:]):
            a_range = [a.edges[first], a.edges[stop]]
            b_first, b_last = observations[[first, stop - 1], 0]
            if abs(b_last - b_first) + sample_m < min_run_m:
                continue
            direction = np.sign(b_last - b_first)
            b_range = np.clip([b_first - direction * (a.mid[first] - a_range[0]),
                               b_last + direction * (a_range[1] - a.mid[stop - 1])], 0, b.total)
            length = min(a_range[1] - a_range[0], abs(b_range[1] - b_range[0]))
            if length + 1e-6 < min_run_m:
                continue
            distances = observations[first:stop, 1]
            yield {
                "lines": [a_id, b_id],
                "kind": "common_alignment" if common[first - start] else "nearby_parallel",
                "chainage_m": {a_id: [round(float(x), 1) for x in a_range],
                               b_id: [round(float(x), 1) for x in sorted(b_range)]},
                "length_m": round(float(length), 1),
                "median_distance_m": round(float(np.median(distances)), 1),
                "max_distance_m": round(float(distances.max()), 1),
                "terminal_codeparture": _codeparture(a, b, a_range, b_range, terminal_m),
            }


def screen(lines, *, sample_m=100, nearby_m=1000, common_m=10, min_run_m=2000,
           max_angle_deg=25, terminal_m=250, pair_filter=None):
    """Rank contiguous runs on WGS84 lines using Baghdad's local metric grid.

    The pair filter restricts comparison to nominated unordered pairs of IDs.
    Chainage starts at each geometry's first vertex. Sampled boundaries are
    approximate. The short-distance class identifies coincident mapped
    centrelines within tolerance. It cannot establish shared tracks, rights of
    way, accessible catchments or operational redundancy.
    """
    settings = dict(sample_m=sample_m, nearby_m=nearby_m, common_m=common_m,
                    min_run_m=min_run_m, max_angle_deg=max_angle_deg, terminal_m=terminal_m)
    if (not all(isfinite(value) and value > 0 for value in settings.values())
            or common_m >= nearby_m or 2 * sample_m > min_run_m or max_angle_deg >= 90):
        raise ValueError("Invalid rail duplication screen thresholds")
    pairs = (list(combinations(sorted(lines), 2)) if pair_filter is None
             else sorted({tuple(sorted(pair)) for pair in pair_filter}))
    if any(len(pair) != 2 or pair[0] == pair[1] or any(code not in lines for code in pair)
           for pair in pairs):
        raise ValueError("Pair filter must identify two distinct known lines per pair")

    active = sorted({code for pair in pairs for code in pair})
    tracks = {code: _Alignment(lines[code], sample_m) for code in active}
    runs = [run for a, b in pairs for run in _pair_runs(a, b, tracks[a], tracks[b], **settings)]
    runs.sort(key=lambda run: (-run["length_m"], run["lines"], run["chainage_m"][run["lines"][0]]))
    return {"settings": settings, "pairs_screened": len(pairs), "runs": runs}
