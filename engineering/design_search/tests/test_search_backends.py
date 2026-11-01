"""Real-library cross-checks for finite-pool diversity preservation."""
from copy import deepcopy
import json

import pytest

from engineering.design_search import quality_diversity, search_backends
from engineering.station_rail.common import identity


def pool():
    # The globally dominant family must not displace another family's front.
    return [dict(candidate_id=letter * 64, descriptor=dict(family=family),
        metrics=dict(mass=mass, cost=cost, hours=hours))
        for letter, family, mass, cost, hours in (
            ("a", "box", 10., 20., 5.),
            ("b", "box", 12., 15., 6.),
            ("c", "box", 10., 20., 5.),  # exact-vector tie
            ("d", "box", 15., 25., 9.),  # dominated
            ("e", "shell", 8., 8., 3.),
            ("f", "shell", 9., 7., 4.))]


def require_backends():
    pytest.importorskip("pymoo")
    pytest.importorskip("ribs")


def test_actual_libraries_preserve_cell_fronts_and_separate_champion_projections():
    require_backends()
    rows = pool()
    original = deepcopy(rows)
    objectives = ("mass", "cost", "hours")
    actual = search_backends.audit(rows, objectives, ("family",), seed=42)
    expected = quality_diversity.archive(rows, objectives, ("family",))
    assert rows == original
    assert actual["reference_archive_id"] == expected["archive_id"]
    assert actual["pymoo"]["matches_reference_archive"]
    assert actual["pymoo"]["cross_cell_partial_quantity_pareto_candidate_ids"] == ["e" * 64, "f" * 64]
    assert {key for cell in actual["pymoo"]["cells"] for key in cell["retained_pareto_candidate_ids"]} == {letter * 64 for letter in "abef"}
    assert len(actual["excluded_from_cell_front"]) == 2
    projections = {row["objective"]: row for row in actual["pyribs"]["projections"]}
    assert {row["candidate_id"] for row in projections["mass"]["champions"]} == {"a" * 64, "e" * 64}
    assert {row["candidate_id"] for row in projections["cost"]["champions"]} == {"b" * 64, "f" * 64}
    assert all(row["occupied_observed_cells"] == 2 for row in projections.values())
    assert actual["pyribs"]["multiobjective_archive_replaced"] is False
    assert actual["evolved_candidate_count"] == actual["numerical_solver_dispatch_count"] == 0
    assert all(actual[key] is False for key in search_backends.FLAGS)
    assert actual["integrated_selection"] is None
    assert actual["audit_id"] == identity({key: value for key, value in actual.items() if key != "audit_id"})
    assert json.loads(json.dumps(actual)) == actual
    assert search_backends.audit(list(reversed(rows)), objectives, ("family",), seed=42) == actual


@pytest.mark.parametrize("bad_value", [None, True, -1., float("nan"), float("inf"), 2**53 + 1, 10**500])
def test_unknown_or_nonfinite_metrics_never_become_zero_or_omit_a_candidate(bad_value):
    rows = pool()
    rows[0]["metrics"]["mass"] = bad_value
    with pytest.raises(ValueError, match="objective"):
        search_backends.audit(rows, ("mass",), ("family",))


def test_incomplete_descriptors_duplicate_identities_and_implicit_seed_are_rejected():
    rows = pool()
    rows[0]["descriptor"] = {}
    with pytest.raises(ValueError, match="descriptors"):
        search_backends.audit(rows, ("mass",), ("family",))
    rows = pool()
    rows.append(deepcopy(rows[0]))
    with pytest.raises(ValueError, match="identities"):
        search_backends.audit(rows, ("mass",), ("family",))
    with pytest.raises(ValueError, match="seed"):
        search_backends.audit(pool(), ("mass",), ("family",), seed=None)
    with pytest.raises(ValueError, match="nonempty"):
        search_backends.audit([], ("mass",), ("family",))
    with pytest.raises(ValueError, match="objectives"):
        search_backends.audit(pool(), ("mass", "mass"), ("family",))


def test_eighteen_candidate_three_objective_audit_has_full_family_coverage():
    require_backends()
    rows = [dict(candidate_id=identity(dict(family=family, profile=profile)),
        descriptor=dict(family=family), metrics=dict(mass=10. + profile,
            cost=20. - profile, hours=5. + 2 * profile))
        for family in ("box", "u", "variable", "folded", "hybrid", "ribbed")
        for profile in range(3)]
    result = search_backends.audit(rows, ("mass", "cost", "hours"), ("family",))
    assert result["candidate_count"] == 18
    assert result["reference_cell_count"] == 6
    assert all(row["occupied_observed_cells"] == 6 for row in result["pyribs"]["projections"])
