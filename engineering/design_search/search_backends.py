"""Optional, independent pymoo/pyribs audits of finite research portfolios.

This adapter does not generate shapes, execute an evolutionary search, or rank
an integrated railway. It checks already calculated partial objective values.
The multiobjective descriptor-cell archive remains authoritative; the pyribs
archives are separate single-objective projections, never its replacement.
"""
from importlib.metadata import version
from math import isfinite

from engineering.station_rail.common import identity
from . import quality_diversity

PRODUCER = "engineering/design_search/search_backends.py"
PINNED_VERSIONS = {"pymoo": "0.6.2", "ribs": "0.12.0"}
API_REFERENCES = {
    "pymoo": "https://github.com/anyoptimization/pymoo/blob/0.6.2/pymoo/util/nds/non_dominated_sorting.py",
    "pyribs": "https://docs.pyribs.org/en/stable/api/ribs.archives.CategoricalArchive.html",
}
FLAGS = dict(physical_accepted=False, engineering_accepted=False,
    configuration_adopted=False, manufacturing_release=False,
    operating_release=False, selected_reference_changed=False)


def _keys(values, label):
    values = tuple(values)
    if (not values or any(not isinstance(key, str) or not key for key in values)
            or len(set(values)) != len(values)):
        raise ValueError("Unique explicit " + label + " required")
    return values


def _pool(rows, objectives, descriptor_keys):
    """Reject unknown objectives rather than using zero or silently omitting rows."""
    objectives = _keys(objectives, "objectives")
    descriptor_keys = _keys(descriptor_keys, "descriptor keys")
    normalized = []
    seen = set()
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError("Explicit candidate records required")
        candidate_id = row.get("candidate_id")
        if (not isinstance(candidate_id, str) or len(candidate_id) != 64
                or any(ch not in "0123456789abcdef" for ch in candidate_id)
                or candidate_id in seen):
            raise ValueError("Unique SHA-256 physical candidate identities required")
        seen.add(candidate_id)
        descriptor = row.get("descriptor")
        if (not isinstance(descriptor, dict) or any(
                not isinstance(descriptor.get(key), str) or not descriptor[key]
                for key in descriptor_keys)):
            raise ValueError("Complete nonempty categorical descriptors required")
        metrics = row.get("metrics")
        if not isinstance(metrics, dict):
            raise ValueError("Explicit finite objective metrics required")
        for key in objectives:
            value = metrics.get(key)
            try:
                valid = (type(value) in (int, float) and isfinite(value) and value >= 0
                    and (type(value) is not int or int(float(value)) == value))
            except (OverflowError, ValueError):
                valid = False
            if not valid:
                raise ValueError("Unknown, negative or inexact objective cannot enter the audit: " + key)
        normalized.append(dict(candidate_id=candidate_id,
            descriptor={key: descriptor[key] for key in descriptor_keys},
            metrics={key: metrics[key] for key in objectives}))
    if not normalized:
        raise ValueError("A nonempty finite evaluated candidate pool is required")
    return sorted(normalized, key=lambda row: row["candidate_id"]), objectives, descriptor_keys


def audit(rows, objectives, descriptor_keys, seed=0):
    """Audit per-cell/global Pareto fronts and per-objective cell champions.

    All objectives are minimized. Exact equal objective vectors use the
    lexicographically first physical candidate ID, matching the in-repository
    archive. Input order, library archive order and nondominated-sort order do
    not affect the canonical result. Optional pinned packages are imported only
    after input validation; absence is an explicit dependency hold.
    """
    rows, objectives, descriptor_keys = _pool(rows, objectives, descriptor_keys)
    if type(seed) is not int or not 0 <= seed < 2**32:
        raise ValueError("An explicit unsigned 32-bit seed is required")
    try:
        import numpy as np
        from pymoo.util.nds.non_dominated_sorting import NonDominatedSorting
        from ribs.archives import CategoricalArchive
    except ImportError as exc:
        raise RuntimeError("Optional search packages are unavailable; install engineering/design_search/requirements-search.txt") from exc
    versions = {name: version(name) for name in PINNED_VERSIONS}
    if versions != PINNED_VERSIONS:
        raise RuntimeError("Search audit requires its pinned package versions: " + str(PINNED_VERSIONS))
    reference = quality_diversity.archive(rows, objectives, descriptor_keys)
    by_id = {row["candidate_id"]: row for row in rows}

    def front(members):
        values = np.asarray([[row["metrics"][key] for key in objectives]
            for row in members], dtype=np.float64)
        indices = NonDominatedSorting().do(values, only_non_dominated_front=True)
        unique = {}
        for index in sorted(int(value) for value in indices):
            row = members[index]
            vector = tuple(row["metrics"][key] for key in objectives)
            unique.setdefault(vector, row["candidate_id"])
        return sorted(unique.values())

    cells = []
    for cell in reference["cells"]:
        members = [by_id[candidate_id] for candidate_id in cell["candidate_ids"]]
        actual = front(members)
        if actual != cell["retained_pareto_candidate_ids"]:
            raise ValueError("pymoo descriptor-cell Pareto front differs: " + cell["cell_id"])
        cells.append(dict(cell_id=cell["cell_id"], descriptor=cell["descriptor"],
            retained_pareto_candidate_ids=actual))
    global_front = front(rows)
    if global_front != reference["cross_cell_partial_quantity_pareto_candidate_ids"]:
        raise ValueError("pymoo cross-cell partial-quantity Pareto front differs")

    categories = [sorted({row["descriptor"][key] for row in rows})
        for key in descriptor_keys]
    projections = []
    for objective in objectives:
        archive = CategoricalArchive(solution_dim=1, categories=categories,
            solution_dtype=np.int64, seed=seed)
        for index, row in enumerate(rows):
            # Negative values convert minimization to pyribs maximization.
            # Ordered single insertion makes lexical tie handling explicit.
            archive.add_single(solution=[index], objective=-float(row["metrics"][objective]),
                measures=[row["descriptor"][key] for key in descriptor_keys])
        champions = []
        for elite in archive:
            row = rows[int(elite["solution"][0])]
            descriptor = row["descriptor"]
            champions.append(dict(cell_id=identity(descriptor), descriptor=descriptor,
                candidate_id=row["candidate_id"], value=row["metrics"][objective]))
        champions.sort(key=lambda row: row["cell_id"])
        expected = []
        for cell in reference["cells"]:
            champion = min((by_id[key] for key in cell["candidate_ids"]),
                key=lambda row: (row["metrics"][objective], row["candidate_id"]))
            expected.append(dict(cell_id=cell["cell_id"], descriptor=cell["descriptor"],
                candidate_id=champion["candidate_id"], value=champion["metrics"][objective]))
        if champions != expected:
            raise ValueError("pyribs single-objective descriptor coverage or champion differs: " + objective)
        projections.append(dict(objective=objective, direction="minimize",
            occupied_observed_cells=len(champions), champions=champions,
            archive_kind="ribs.archives.CategoricalArchive",
            scope="Separate single-objective projection; not a multiobjective Pareto archive"))

    result = dict(schema="osr-finite-search-backend-audit/1", purpose="next-experiment",
        input_pool_id=identity(rows), candidate_count=len(rows),
        candidate_ids=[row["candidate_id"] for row in rows],
        objectives=list(objectives), descriptor_keys=list(descriptor_keys),
        descriptor_categories=categories, seed=seed,
        library_versions={**versions, "numpy": np.__version__},
        api_references=API_REFERENCES,
        reference_archive_id=reference["archive_id"],
        reference_cell_count=reference["cell_count"],
        pymoo=dict(method="pymoo.util.nds.non_dominated_sorting.NonDominatedSorting",
            cells=cells, cross_cell_partial_quantity_pareto_candidate_ids=global_front,
            matches_reference_archive=True),
        pyribs=dict(projections=projections, all_observed_descriptor_cells_covered=True,
            multiobjective_archive_replaced=False),
        excluded_from_cell_front=[dict(cell_id=cell["cell_id"], **row)
            for cell in reference["cells"] for row in cell["excluded"]],
        evidence_scope="Independent library checks of already calculated partial objectives; unknown metrics are rejected. No new physical candidates or engineering evidence are generated.",
        evolved_candidate_count=0, numerical_solver_dispatch_count=0,
        integrated_selection=None, global_optimum_proven=False, **FLAGS)
    result["audit_id"] = identity(result)
    return result
