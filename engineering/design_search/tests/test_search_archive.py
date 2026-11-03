"""Crossover dispatch, shared semantics and compact archive regression tests."""
from copy import deepcopy
import gzip
import json
import random

import pytest

from engineering.design_search import native_search, quality_diversity, search_archive as a


class NoNative:
    """Any attempt to call a process/binary path is a regression for small pools."""
    def archive(self, *args, **kwargs):
        raise AssertionError("Python dispatch must not execute the native archive")


class Spy:
    def __init__(self):
        self.calls = []

    def archive(self, rows, objectives, descriptors, **kwargs):
        self.calls.append((deepcopy(rows), objectives, descriptors, kwargs))
        # The explicit Python reference provides a protocol-shaped native spy
        # without installing a binary or relying on a receipt in dispatch tests.
        value = a.archive(NoNative(), rows, objectives, descriptors, backend="python")
        for key in ("backend", "backend_policy", "source_sha256", "runtime_python", "archive_id"):
            value.pop(key)
        return value


def pool(size, dimensions=3):
    rng = random.Random(3)
    return [dict(candidate_id=f"{i:064x}", descriptor=dict(family=str(i % 3)),
                 metrics={f"m{j}": rng.randrange(10) for j in range(dimensions)}) for i in range(size)]


@pytest.fixture(scope="module")
def engine():
    path = native_search.ROOT / native_search.TARGET / "release/osr-design-search"
    if not path.is_file() or not native_search._receipt_path(path).is_file():
        pytest.skip("Explicitly build Rust kernel for native crossover integration tests")
    return native_search.NativeSearch()


@pytest.mark.parametrize("size,threshold,expected", [(0, 64, "python"), (54, 64, "python"),
    (64, 64, "python"), (65, 64, "rust"), (1, 0, "rust"), (4, 3, "rust")])
def test_configurable_dispatch_avoids_process_overhead_for_small_pools(size, threshold, expected):
    spy = Spy()
    value = a.archive(spy, pool(size), ["m0", "m1", "m2"], ["family"], python_threshold=threshold)
    assert value["backend"] == expected
    assert len(spy.calls) == (expected == "rust")
    assert value["statistics"]["point_count"] == size


def test_explicit_python_requires_neither_binary_nor_receipt_and_preserves_all_fronts():
    rows = pool(40)
    value = a.archive(NoNative(), rows, ["m0", "m1", "m2"], ["family"], backend="python")
    reference = quality_diversity.archive(rows, ["m0", "m1", "m2"], ["family"])
    assert value["global_front"] == reference["cross_cell_partial_quantity_pareto_candidate_ids"]
    assert value["retained_candidate_ids"] == reference["retained_candidate_ids"]
    for row in value["dominated"]:
        cell = next(c for c in reference["cells"] if c["cell_id"] == row["cell_id"])
        excluded = next(r for r in cell["excluded"] if r["candidate_id"] == row["candidate_id"])
        assert row["dominated_by"] == excluded["dominated_by"][0]
    assert all(value[k] == v for k, v in native_search.FLAGS.items())
    assert value["source_sha256"][a.PRODUCER]
    assert value["source_sha256"]["engineering/design_search/quality_diversity.py"]
    assert value["runtime_python"]


@pytest.mark.parametrize("folder,objectives,descriptors,size", [
    ("civil-shape-portfolio", ["nominal_stock_mass_kg", "scoped_installed_base_iqd", "factory_hours_base"], ["family"], 18),
    ("breadth-first-shape-portfolio", ["known_gross_structure_stock_kg", "factory_gate_body_stock_base_iqd_per_car",
        "factory_process_hours_base_per_car", "manufacturing_occurrences"], ["frame", "shell", "ribs"], 54),
])
def test_actual_portfolios_have_identical_fronts_valid_witnesses_and_distinct_evaluation_ids(engine, folder, objectives, descriptors, size):
    path = native_search.ROOT / "docs/design-engine" / folder / "result.json"
    raw = path.read_bytes() if path.exists() else gzip.decompress(path.with_suffix(".json.gz").read_bytes())
    rows = json.loads(raw)["evaluations"]
    assert len(rows) == size
    python = a.archive(NoNative(), rows, objectives, descriptors, backend="python")
    rust = a.archive(engine, rows, objectives, descriptors, backend="rust")
    assert python["global_front"] == rust["global_front"]
    assert python["retained_candidate_ids"] == rust["retained_candidate_ids"]
    assert python["archive_id"] != rust["archive_id"]
    assert [c["descriptor"] for c in python["cells"]] == [c["descriptor"] for c in rust["cells"]]
    by_id = {row["candidate_id"]: row for row in rows}
    for result in (python, rust):
        for exclusion in result["dominated"]:
            left, right = [by_id[exclusion[key]] for key in ("dominated_by", "candidate_id")]
            assert left["descriptor"] == right["descriptor"]
            assert all(left["metrics"][key] <= right["metrics"][key] for key in objectives)
            assert any(left["metrics"][key] < right["metrics"][key] for key in objectives) or left["candidate_id"] < right["candidate_id"]


@pytest.mark.parametrize("backend", ["auto", "python", "rust"])
@pytest.mark.parametrize("bad", [None, True, -1, float("nan"), float("inf"), 2**53 + 1, 10**400])
def test_unknown_and_inexact_metrics_are_rejected_before_backend_dispatch(backend, bad):
    rows = pool(2)
    rows[0]["metrics"]["m0"] = bad
    with pytest.raises(ValueError, match="objective"):
        a.archive(NoNative(), rows, ["m0"], ["family"], backend=backend)


@pytest.mark.parametrize("threshold", [-1, 513, True, 1.5, None])
def test_invalid_crossover_rejected(threshold):
    with pytest.raises(ValueError, match="crossover"):
        a.archive(NoNative(), pool(1), ["m0"], ["family"], python_threshold=threshold)


def test_explicit_python_cannot_start_unbounded_quadratic_work():
    with pytest.raises(ValueError, match="512-row"):
        a.archive(NoNative(), pool(513), ["m0"], ["family"], backend="python")


def test_backend_selection_changes_evaluation_not_physical_candidates_and_is_order_independent():
    rows = pool(20)
    original_ids = [r["candidate_id"] for r in rows]
    x = a.archive(NoNative(), rows, ["m0", "m1"], ["family"])
    random.Random(8).shuffle(rows)
    y = a.archive(NoNative(), rows, ["m0", "m1"], ["family"])
    assert x == y
    assert sorted(r["candidate_id"] for r in rows) == original_ids
    z = a.archive(NoNative(), rows, ["m0", "m1"], ["family"], backend="python")
    assert z["retained_candidate_ids"] == x["retained_candidate_ids"]
    assert z["archive_id"] != x["archive_id"]


def test_relocated_or_changed_wrapper_source_cannot_be_attributed_to_current_execution(tmp_path, monkeypatch):
    different = tmp_path / "different.py"
    different.write_text("# other implementation\n")
    monkeypatch.setattr(a, "__file__", str(different))
    with pytest.raises(ValueError, match="Loaded archive dispatcher"):
        a.archive(NoNative(), pool(1), ["m0"], ["family"])


def test_invalid_identity_descriptor_and_objective_names_share_the_native_domain():
    rows = pool(2)
    rows[0]["candidate_id"] = "x" * 64
    with pytest.raises(ValueError, match="identities"):
        a.archive(NoNative(), rows, ["m0"], ["family"])
    rows = pool(2)
    with pytest.raises(ValueError, match="descriptor"):
        a.archive(NoNative(), rows, ["m0"], ["missing"])
    with pytest.raises(ValueError, match="names"):
        a.archive(NoNative(), rows, ["m0", "m0"], ["family"])
