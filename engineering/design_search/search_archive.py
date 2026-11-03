"""Choose a bounded Python reference archive or the Rust archive by pool size.

The default crossover is provisional: small real portfolios avoid process and
receipt overhead, while large pools use the native search kernel. The Python
all-pairs implementation remains the independent reference; both backends retain
the same physical identities and never select or qualify an installed railway.
"""
from __future__ import annotations

from copy import deepcopy
from math import isfinite
from pathlib import Path
import sys

from engineering.station_rail import ROOT, common
from engineering.station_rail.common import digest, identity
from . import native_search, quality_diversity

PRODUCER = "engineering/design_search/search_archive.py"
MAX_PYTHON_ROWS = 512
MAX_ROWS = 100_000
DEFAULT_PYTHON_THRESHOLD = 64
MODULES = ((quality_diversity, "engineering/design_search/quality_diversity.py"),
           (common, "engineering/station_rail/common.py"),
           (native_search, native_search.PRODUCER))
LOADED_SOURCE_SHA256 = {name: digest(module.__file__) for module, name in MODULES}
LOADED_SOURCE_SHA256[PRODUCER] = digest(__file__)
LOADED_SOURCE_SHA256[native_search.PRODUCER] = digest(native_search.__file__)


def _source_record(engine, backend):
    root = Path(getattr(engine, "root", ROOT))
    modules = list(MODULES)
    result = {PRODUCER: LOADED_SOURCE_SHA256[PRODUCER]}
    if digest(__file__) != result[PRODUCER] or digest(root / PRODUCER) != result[PRODUCER]:
        raise ValueError("Loaded archive dispatcher differs from declared source root")
    for module, name in modules:
        expected = LOADED_SOURCE_SHA256[name]
        if digest(module.__file__) != expected or digest(root / name) != expected:
            raise ValueError("Loaded archive dependency differs from declared source root: " + name)
        result[name] = expected
    return result


def _pool(rows, objectives, descriptor_keys):
    if isinstance(objectives, str) or isinstance(descriptor_keys, str):
        raise ValueError("Explicit objective and descriptor name sequences required")
    objectives, descriptor_keys = tuple(objectives), tuple(descriptor_keys)
    for keys in (objectives, descriptor_keys):
        if not keys or any(not isinstance(k, str) or not k for k in keys) or len(set(keys)) != len(keys):
            raise ValueError("Unique explicit objective and descriptor names required")
    if len(objectives) > 8:
        raise ValueError("The shared native/reference domain supports one to eight objectives")
    normalized, seen = [], set()
    for row in rows:
        if len(normalized) >= MAX_ROWS:
            raise ValueError("Archive candidate pool exceeds the shared resource domain")
        if not isinstance(row, dict):
            raise ValueError("Explicit archive candidate records required")
        cid = row.get("candidate_id")
        if not native_search._hex(cid) or cid in seen:
            raise ValueError("Unique SHA-256 physical candidate identities required")
        seen.add(cid)
        descriptor, metrics = row.get("descriptor"), row.get("metrics")
        if not isinstance(descriptor, dict) or set(descriptor_keys) - set(descriptor):
            raise ValueError("Complete explicit descriptor required")
        if not isinstance(metrics, dict):
            raise ValueError("Explicit objective metrics required")
        selected_metrics = {}
        for name in objectives:
            value = metrics.get(name)
            try:
                valid = (type(value) in (int, float) and isfinite(value) and value >= 0
                         and (type(value) is not int or int(float(value)) == value))
            except (OverflowError, ValueError):
                valid = False
            if not valid:
                raise ValueError("Unknown, negative or inexact objective cannot enter search: " + name)
            selected_metrics[name] = value
        selected_descriptor = {key: deepcopy(descriptor[key]) for key in descriptor_keys}
        identity(selected_descriptor)  # Require finite canonical-JSON descriptor values.
        normalized.append(dict(candidate_id=cid, descriptor=selected_descriptor, metrics=selected_metrics))
    return sorted(normalized, key=lambda row: row["candidate_id"]), objectives, descriptor_keys


def archive(engine, rows, objectives, descriptor_keys, *, backend="auto",
            python_threshold=DEFAULT_PYTHON_THRESHOLD, max_work=100_000_000):
    """Return the shared compact archive; unknown objectives never become zero.

    ``engine`` is used only by the Rust branch. Python execution does not inspect
    a binary or build receipt. Explicit Python execution is limited to 512 rows;
    this limits its quadratic reference work and complete dominator lists.
    ``max_work`` retains the Rust kernel's algorithmic-work meaning, not an OS
    runtime/memory limit or a physical engineering constraint.
    """
    if backend not in ("auto", "python", "rust"):
        raise ValueError("Archive backend must be auto, python or rust")
    if type(python_threshold) is not int or not 0 <= python_threshold <= MAX_PYTHON_ROWS:
        raise ValueError("Python crossover must be an explicit zero-to-512 row resource bound")
    if type(max_work) is not int or not 1 <= max_work <= 1_000_000_000:
        raise ValueError("Explicit positive archive work budget required")
    rows, objectives, descriptor_keys = _pool(rows, objectives, descriptor_keys)
    selected = "python" if backend == "auto" and len(rows) <= python_threshold else backend
    if selected == "auto":
        selected = "rust"
    if selected == "python" and len(rows) > MAX_PYTHON_ROWS:
        raise ValueError("Explicit Python archive exceeds its 512-row quadratic reference budget")
    source = _source_record(engine, selected)
    if selected == "rust":
        result = deepcopy(engine.archive(rows, objectives, descriptor_keys, max_work=max_work))
        result.pop("archive_id", None)
    else:
        reference = quality_diversity.archive(rows, objectives, descriptor_keys)
        global_front = reference["cross_cell_partial_quantity_pareto_candidate_ids"]
        result = dict(schema=native_search.RESULT_SCHEMA, operation="pareto",
            cells=[dict(cell_id=cell["cell_id"], descriptor=deepcopy(cell["descriptor"]),
                        retained_candidate_ids=cell["retained_pareto_candidate_ids"])
                   for cell in reference["cells"]],
            retained_candidate_ids=reference["retained_candidate_ids"], global_front=global_front,
            dominated=sorted([dict(candidate_id=row["candidate_id"], cell_id=cell["cell_id"],
                                  dominated_by=row["dominated_by"][0])
                              for cell in reference["cells"] for row in cell["excluded"]],
                             key=lambda row: row["candidate_id"]),
            statistics=dict(point_count=len(rows), objective_count=len(objectives), work=None,
                max_work=max_work, method=reference["method"],
                work_scope="Bounded all-pairs reference; max_work is not counted or enforced by this backend"),
            objectives=list(objectives), descriptor_keys=list(descriptor_keys),
            cross_cell_partial_quantity_pareto_candidate_ids=global_front,
            scope="Compact known-objective research archive; no installed-system selection or physical qualification",
            provenance=dict(reference_archive_id=reference["archive_id"],
                            input_pool_id=identity(rows), method="Python independent reference"),
            **native_search.FLAGS)
    if _source_record(engine, selected) != source:
        raise ValueError("Archive sources changed during evaluation")
    result.update(backend=selected,
        backend_policy=dict(requested=backend, python_threshold=python_threshold,
            selection_basis="pool size; provisional configurable crossover, not a universal performance guarantee"),
        source_sha256=source, runtime_python=sys.version)
    result["archive_id"] = identity(result)
    return result
