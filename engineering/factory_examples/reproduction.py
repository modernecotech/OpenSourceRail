"""Exact retained evidence integrity and tolerant, independent recomputation.

The seal never rewrites an original report, drawing or CAD file. Its producer
identity and the current verifier identity are deliberately separate.
"""

from __future__ import annotations

import csv
import io
import json
import math
from pathlib import Path
from xml.etree import ElementTree as ET

from .native import digest

SCHEMA = "osr-factory-reproduction/1"
RELATIVE = 1e-9
# SI absolute floors for cancellation near zero; not engineering allowables.
ABSOLUTE = {
    "_n": 1e-5,
    "_nm": 1e-5,
    "_pa": 1e-4,
    "_kg": 1e-7,
    "_m": 1e-10,
    "_m2": 1e-12,
    "_m3": 1e-12,
    "_m4": 1e-14,
}
FIGURES = {"development.svg", "connections.svg"}
METADATA = {
    "report.json": {("source_sha256",)},
    "development.json": {("numerical_toolchain",)},
}


def load(text):
    def invalid(value):
        raise ValueError("nonfinite reproduction value: " + value)

    def pairs(items):
        value = {}
        for key, child in items:
            if key in value:
                raise ValueError("duplicate reproduction field: " + key)
            value[key] = child
        return value

    return json.loads(text, parse_constant=invalid, object_pairs_hook=pairs)


def differences(retained, recomputed, *, path=(), ignored=frozenset(), numeric=True):
    """States, unknowns, counts, keys and array lengths always compare exactly."""
    if path in ignored:
        return []
    label = "/".join(map(str, path)) or "root"
    if isinstance(retained, dict) and isinstance(recomputed, dict):
        if retained.keys() != recomputed.keys():
            return [label + ": fields differ"]
        return [
            error
            for key in retained
            for error in differences(
                retained[key],
                recomputed[key],
                path=(*path, key),
                ignored=ignored,
                numeric=numeric,
            )
        ]
    if isinstance(retained, list) and isinstance(recomputed, list):
        if len(retained) != len(recomputed):
            return [label + ": array length differs"]
        return [
            error
            for index, (a, b) in enumerate(zip(retained, recomputed))
            for error in differences(
                a, b, path=(*path, index), ignored=ignored, numeric=numeric
            )
        ]
    if numeric and type(retained) is float and type(recomputed) in (int, float):
        field = next((key for key in reversed(path) if isinstance(key, str)), "")
        floor = next(
            (value for suffix, value in ABSOLUTE.items() if field.endswith(suffix)),
            1e-12,
        )
        if (
            math.isfinite(retained)
            and math.isfinite(recomputed)
            and math.isclose(retained, recomputed, rel_tol=RELATIVE, abs_tol=floor)
        ):
            return []
    elif type(retained) is type(recomputed) and retained == recomputed:
        return []
    return [f"{label}: {retained!r} != {recomputed!r}"]


def csv_values(text):
    rows = list(csv.DictReader(io.StringIO(text)))
    for row in rows:
        for key, value in row.items():
            try:
                row[key] = load(value)
            except (ValueError, TypeError):
                pass
    return rows


def compare_outputs(folder, outputs):
    errors, presentation = [], []
    for name, generated in outputs.items():
        path = Path(folder) / name
        if not path.is_file():
            errors.append(name + ": missing")
            continue
        original = path.read_text()
        if name in FIGURES:
            # Backend/font/version details are not portable numerical evidence.
            # Exact retained bytes are checked by the seal; data are checked in
            # their JSON reports. No pixel or SVG path equivalence is claimed.
            for text in (original, generated):
                root = ET.fromstring(text)
                if root.tag != "{http://www.w3.org/2000/svg}svg" or not root.get(
                    "viewBox"
                ):
                    errors.append(name + ": invalid standalone figure")
            if original != generated:
                presentation.append(name)
        elif name.endswith(".json"):
            errors.extend(
                name + ": " + error
                for error in differences(
                    load(original),
                    load(generated),
                    ignored=METADATA.get(name, set()),
                    numeric=not name.endswith("/model.json"),
                )
            )
        elif name.endswith(".csv"):
            if original.splitlines()[0] != generated.splitlines()[0]:
                errors.append(name + ": CSV columns differ")
            errors.extend(
                name + ": " + e
                for e in differences(csv_values(original), csv_values(generated))
            )
        elif original != generated:
            errors.append(name + ": rounded presentation or controlled text differs")
    return errors, presentation


def safe_file(folder, name):
    path = folder / name
    if (
        path.is_symlink()
        or not path.resolve().is_relative_to(folder.resolve())
        or not path.is_file()
    ):
        raise ValueError("missing or unsafe retained file: " + name)
    return path


def retained_hashes(folder, outputs, models):
    names = set(outputs)
    names.update(
        f"{key}/{name}" for key in models for name in ("native-cad.json", "model.FCStd")
    )
    return {name: digest(safe_file(folder, name)) for name in sorted(names)}


def seal(folder, outputs, models, sources):
    """Explicit re-verification of retained evidence, never a regeneration."""
    folder = Path(folder)
    existing = folder / "reproduction.json"
    if existing.is_file():
        previous = load(existing.read_text())
        if previous["retained_files_sha256"] != retained_hashes(
            folder, outputs, models
        ):
            raise ValueError(
                "cannot reseal changed original evidence; generate a separate evidence directory"
            )
    errors, presentation = compare_outputs(folder, outputs)
    if errors:
        raise ValueError("Cannot seal failed reproduction: " + "; ".join(errors[:12]))
    report = load((folder / "report.json").read_text())
    producer = load((folder / "development.json").read_text())["numerical_toolchain"]
    return dict(
        schema=SCHEMA,
        retained_files_sha256=retained_hashes(folder, outputs, models),
        original_producer_sources_sha256=report["source_sha256"],
        original_producer_toolchain=producer,
        verification_sources_sha256=sources,
        numerical_policy=dict(
            relative=RELATIVE,
            absolute_by_si_suffix=ABSOLUTE,
            default_absolute=1e-12,
            counts_states_unknowns_and_geometry="exact",
        ),
        presentation_policy="Retained bytes exact; rounded prose exact; Matplotlib SVG paths are platform-dependent views of separately checked JSON data",
        original_artifacts_rewritten=False,
        physical_release=False,
    )


def verify(folder, outputs, models, sources):
    folder = Path(folder)
    record = load(safe_file(folder, "reproduction.json").read_text())
    if record.get("schema") != SCHEMA:
        raise ValueError("controlled factory reproduction seal required")
    expected_policy = dict(
        relative=RELATIVE,
        absolute_by_si_suffix=ABSOLUTE,
        default_absolute=1e-12,
        counts_states_unknowns_and_geometry="exact",
    )
    if record.get("numerical_policy") != expected_policy:
        raise ValueError("reproduction tolerance policy differs")
    if record["verification_sources_sha256"] != sources:
        raise ValueError(
            "factory verifier source/input mismatch; explicitly re-verify retained evidence"
        )
    if record["retained_files_sha256"] != retained_hashes(folder, outputs, models):
        raise ValueError("retained factory artifact integrity mismatch")
    report = load((folder / "report.json").read_text())
    development = load((folder / "development.json").read_text())
    if (
        report["source_sha256"] != record["original_producer_sources_sha256"]
        or development["numerical_toolchain"] != record["original_producer_toolchain"]
    ):
        raise ValueError("original factory producer identity differs")
    errors, changed_figures = compare_outputs(folder, outputs)
    if errors:
        raise ValueError(
            "factory numerical reproduction mismatch: " + "; ".join(errors[:12])
        )
    return dict(
        schema="osr-factory-recomputation/1",
        passed=True,
        verifier_toolchain=load(outputs["development.json"])["numerical_toolchain"],
        original_producer_toolchain=record["original_producer_toolchain"],
        platform_dependent_figures=changed_figures,
        numerical_policy=record["numerical_policy"],
        exact_retained_integrity=True,
        original_artifacts_rewritten=False,
        physical_release=False,
    )
