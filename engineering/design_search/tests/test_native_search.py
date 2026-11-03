"""Native search parity, source provenance and bounded-process regressions."""
from copy import deepcopy
import gzip
import json
from pathlib import Path
import random
import shutil
import sys

import pytest

from engineering.design_search import native_search as n, quality_diversity


@pytest.fixture(scope="module")
def kernel():
    path = n.ROOT / n.TARGET / "release/osr-design-search"
    if not path.is_file() or not n._receipt_path(path).is_file():
        pytest.skip("Explicitly build the Rust search release kernel before native integration checks")
    return n.NativeSearch()


def rows(count=30, dimensions=4):
    rng = random.Random(20261103)
    return [dict(candidate_id=f"{i:064x}", descriptor=dict(family=str(i % 3)),
                 metrics={f"m{j}": rng.randrange(8) for j in range(dimensions)}) for i in range(count)]


def compare(kernel, pool, objectives, descriptors):
    actual = kernel.archive(pool, objectives, descriptors)
    expected = quality_diversity.archive(pool, objectives, descriptors)
    assert actual["global_front"] == expected["cross_cell_partial_quantity_pareto_candidate_ids"]
    assert actual["retained_candidate_ids"] == expected["retained_candidate_ids"]
    assert {c["cell_id"]: c["retained_candidate_ids"] for c in actual["cells"]} == {
        c["cell_id"]: c["retained_pareto_candidate_ids"] for c in expected["cells"]}
    assert all(actual[k] == v for k, v in n.FLAGS.items())
    assert actual["provenance"]["binary_sha256"] == kernel.receipt["binary_sha256"]
    return actual


@pytest.mark.parametrize("dimensions", [1, 2, 3, 4, 8])
def test_native_fronts_match_small_independent_oracle_with_ties_and_reordering(kernel, dimensions):
    pool = rows(dimensions=dimensions)
    a = compare(kernel, pool, [f"m{j}" for j in range(dimensions)], ["family"])
    random.Random(4).shuffle(pool)
    b = kernel.archive(pool, [f"m{j}" for j in range(dimensions)], ["family"])
    assert a == b


@pytest.mark.parametrize("folder,objectives,descriptors", [
    ("civil-shape-portfolio", ["nominal_stock_mass_kg", "scoped_installed_base_iqd", "factory_hours_base"], ["family"]),
    ("breadth-first-shape-portfolio", ["known_gross_structure_stock_kg", "factory_gate_body_stock_base_iqd_per_car",
                                      "factory_process_hours_base_per_car", "manufacturing_occurrences"], ["frame", "shell", "ribs"]),
])
def test_actual_civil_and_body_portfolio_fronts_match(kernel, folder, objectives, descriptors):
    path = n.ROOT / "docs/design-engine" / folder / "result.json"
    if path.exists():
        value = json.loads(path.read_bytes())
    else:
        value = json.loads(gzip.decompress(path.with_suffix(".json.gz").read_bytes()))
    compare(kernel, value["evaluations"], objectives, descriptors)


@pytest.mark.parametrize("bad", [None, True, -1, float("nan"), float("inf"), 2**53 + 1, 10**400])
def test_unknown_or_inexact_objectives_cannot_become_zero(kernel, bad):
    pool = rows(1)
    pool[0]["metrics"]["m0"] = bad
    with pytest.raises(ValueError, match="objective"):
        kernel.archive(pool, ["m0"], ["family"])


def test_equal_vector_tie_uses_physical_identity_and_does_not_reidentify(kernel):
    pool = rows(2, 1)
    for row in pool:
        row["descriptor"] = dict(family="same")
        row["metrics"] = dict(m0=1.0)
    actual = kernel.archive(list(reversed(pool)), ["m0"], ["family"])
    assert actual["retained_candidate_ids"] == [pool[0]["candidate_id"]]
    assert actual["dominated"][0]["dominated_by"] == pool[0]["candidate_id"]
    assert [r["candidate_id"] for r in pool] == [f"{i:064x}" for i in range(2)]


def test_negative_zero_and_exact_large_float_have_python_comparison_semantics(kernel):
    pool = rows(3, 2)
    for row in pool:
        row["descriptor"] = dict(family="same")
    pool[0]["metrics"] = dict(m0=-0.0, m1=2**54)
    pool[1]["metrics"] = dict(m0=0.0, m1=float(2**54))
    pool[2]["metrics"] = dict(m0=1e300, m1=0.0)
    compare(kernel, pool, ["m0", "m1"], ["family"])


def test_missing_descriptor_duplicate_identity_and_malformed_metrics_are_rejected(kernel):
    pool = rows(2, 1)
    with pytest.raises(ValueError, match="identities"):
        kernel.archive([pool[0], pool[0]], ["m0"], ["family"])
    with pytest.raises(ValueError, match="descriptor"):
        kernel.archive(pool, ["m0"], ["absent"])
    with pytest.raises(ValueError, match="records"):
        kernel.archive([None], ["m0"], ["family"])
    pool[0]["metrics"] = None
    with pytest.raises(ValueError, match="metrics"):
        kernel.archive(pool, ["m0"], ["family"])


def test_kernel_generates_bounded_deterministic_new_genes_with_ancestry(kernel):
    fields = dict(seed=11, generation=2, limit=12, max_attempts=300,
        axes=[dict(name="family", choices=3), dict(name="depth", choices=5), dict(name="ribs", choices=3)],
        family_axis=0, parents=[dict(candidate_id=f"{1:064x}", genes=[0, 0, 0])],
        seen=[[0, 0, 0]], weights=[50, 30, 20])
    a = kernel.propose(**fields)
    assert a == kernel.propose(**fields)
    genes = [tuple(p["genes"]) for p in a["proposals"]]
    assert len(genes) == len(set(genes)) == 12
    assert (0, 0, 0) not in genes
    assert all(p["parent_candidate_ids"] == [f"{1:064x}"] for p in a["proposals"])
    assert set(p["operator"] for p in a["proposals"]) <= {"exploit", "alternative-family", "unconventional"}


def test_native_work_budget_failure_never_returns_a_partial_front(kernel):
    with pytest.raises(RuntimeError, match="[Bb]udget|[Ww]ork"):
        kernel.archive(rows(60, 4), ["m0", "m1", "m2", "m3"], ["family"], max_work=1)


def test_source_and_binary_receipts_are_required_and_not_refreshed_implicitly(kernel, tmp_path):
    target = tmp_path / "kernel"
    shutil.copy2(kernel.binary, target)
    with pytest.raises(ValueError):
        n.NativeSearch(binary=target)
    receipt = n._receipt_path(target)
    shutil.copy2(n._receipt_path(kernel.binary), receipt)
    assert n.NativeSearch(binary=target).receipt == kernel.receipt
    value = json.loads(receipt.read_bytes())
    value["source_sha256"]["Cargo.toml"] = "0" * 64
    value.pop("receipt_id")
    value["receipt_id"] = n.identity(value)
    receipt.write_bytes(n.encoded(value))
    with pytest.raises(ValueError, match="source, binary or receipt changed"):
        n.NativeSearch(binary=target)


def test_changed_binary_is_rejected_even_with_an_unchanged_receipt(kernel, tmp_path):
    target = tmp_path / "kernel"
    shutil.copy2(kernel.binary, target)
    shutil.copy2(n._receipt_path(kernel.binary), n._receipt_path(target))
    copied = n.NativeSearch(binary=target)
    with target.open("ab") as handle:
        handle.write(b"modified")
    with pytest.raises(ValueError, match="source, binary or receipt changed"):
        copied.archive(rows(1), ["m0"], ["family"])


def test_symlinked_binary_is_rejected(kernel, tmp_path):
    target = tmp_path / "kernel"
    target.symlink_to(kernel.binary)
    shutil.copy2(n._receipt_path(kernel.binary), n._receipt_path(target))
    with pytest.raises(ValueError, match="non-symlink"):
        n.NativeSearch(binary=target)


def test_bridge_bounds_output_and_kills_timed_out_processes():
    with pytest.raises(ValueError, match="output size budget"):
        n._run([sys.executable, "-c", "import sys;sys.stdout.buffer.write(b'x'*100000)"], maximum_output=20)
    with pytest.raises(TimeoutError, match="runtime budget"):
        n._run([sys.executable, "-c", "import time;time.sleep(2)"], timeout=0.05)


def test_reader_rejects_fifo_symlink_and_duplicate_json(tmp_path):
    import os
    fifo = tmp_path / "fifo"
    os.mkfifo(fifo)
    with pytest.raises(ValueError, match="Regular Rust record"):
        n._read(fifo)
    file = tmp_path / "source"
    file.write_bytes(b"{}")
    link = tmp_path / "link"
    link.symlink_to(file)
    with pytest.raises(ValueError, match="non-symlink"):
        n._read(link)
    with pytest.raises(ValueError, match="Duplicate JSON"):
        n._parse(b'{"schema":1,"schema":2}')
