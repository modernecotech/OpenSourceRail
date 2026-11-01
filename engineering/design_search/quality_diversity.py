"""Deterministic descriptor-cell Pareto archive for breadth-first exploration."""
from math import isfinite

from engineering.station_rail.common import identity


def archive(rows, objectives, descriptor_keys):
    """Retain each descriptor cell's nondominated candidates and all exclusions.

    This is an in-repository MAP-Elites-style archive, not the pyribs package.
    It keeps per-cell fronts and a separate cross-cell partial-quantity front;
    neither produces an integrated selection.
    """
    if not objectives or not descriptor_keys:
        raise ValueError("Explicit objectives and descriptor keys required")
    seen = set()
    cells = {}
    for row in rows:
        candidate_id = row.get("candidate_id")
        if not isinstance(candidate_id, str) or len(candidate_id) != 64 or candidate_id in seen:
            raise ValueError("Unique physical candidate identities required")
        seen.add(candidate_id)
        descriptor = row.get("descriptor")
        if not isinstance(descriptor, dict) or set(descriptor_keys) - set(descriptor):
            raise ValueError("Candidate descriptor is incomplete")
        metrics = row.get("metrics")
        if not isinstance(metrics, dict):
            raise ValueError("Explicit measured/calculated objective metrics required")
        for name in objectives:
            value = metrics.get(name)
            if type(value) not in (int, float) or not isfinite(value) or value < 0:
                raise ValueError("Finite nonnegative objective required: " + name)
        cell_id = identity({key: descriptor[key] for key in descriptor_keys})
        cells.setdefault(cell_id, []).append(row)

    def dominates(left, right):
        a = [left["metrics"][key] for key in objectives]
        b = [right["metrics"][key] for key in objectives]
        strict = any(x < y for x, y in zip(a, b))
        equal_tiebreak = a == b and left["candidate_id"] < right["candidate_id"]
        return all(x <= y for x, y in zip(a, b)) and (strict or equal_tiebreak)

    cell_rows = []
    retained_ids = []
    for cell_id, members in sorted(cells.items()):
        front = sorted(row["candidate_id"] for row in members
            if not any(dominates(other, row) for other in members))
        retained_ids.extend(front)
        by_id = {row["candidate_id"]: row for row in members}
        exemplar = by_id[front[0]]
        cell_rows.append(dict(cell_id=cell_id,
            descriptor={key: exemplar["descriptor"][key] for key in descriptor_keys},
            candidate_ids=sorted(by_id), retained_pareto_candidate_ids=front,
            excluded=[dict(candidate_id=row["candidate_id"],
                dominated_by=sorted(other["candidate_id"] for other in members
                    if dominates(other, row)))
                for row in sorted(members, key=lambda item: item["candidate_id"])
                if row["candidate_id"] not in front]))
    global_front = sorted(row["candidate_id"] for row in rows
        if not any(dominates(other, row) for other in rows))
    result = dict(schema="osr-quality-diversity-archive/1", objectives=list(objectives),
        descriptor_keys=list(descriptor_keys), cell_count=len(cells), cells=cell_rows,
        retained_candidate_ids=sorted(retained_ids),
        cross_cell_partial_quantity_pareto_candidate_ids=global_front,
        integrated_selection=None, global_optimum_proven=False,
        method="Deterministic descriptor-cell Pareto archive with a separate cross-cell partial-quantity front; no scalar score or external optimizer")
    result["archive_id"] = identity(result)
    return result
