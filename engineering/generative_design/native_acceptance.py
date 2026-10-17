"""Mandatory fresh architecture CAD acceptance, separate from design release.

Recompute current architecture cases and selections, export/reopen the two
required selected models, and retain every attempted campaign on failure.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import shutil

from . import architecture_campaign as architecture
from . import architecture_civil, architecture_mechanical
from .coverage import ROOT, sha
from engineering.design_engine import factory
from engineering.factory_examples import native
from engineering.factory_examples.models import volume, global_size

ARCHITECTURES = ("LM3", "metro-6car-planning")
SCHEMA = "osr-architecture-native-acceptance/1"
FLAGS = ("engineering_design_complete", "manufacturing_release", "physical_release")


def _write(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n")


def _file(folder, name):
    folder = Path(folder).resolve()
    relative = Path(name)
    if relative.is_absolute() or ".." in relative.parts:
        raise ValueError("safe relative architecture native artifact required")
    path = folder / relative
    if not path.resolve().is_relative_to(folder):
        raise ValueError("architecture native artifact outside retained campaign")
    for parent in [path, *path.parents]:
        if parent == folder:
            break
        if parent.is_symlink():
            raise ValueError("architecture native artifact links are not accepted")
    if not path.is_file():
        raise ValueError("missing architecture native artifact: " + relative.as_posix())
    return path


def _read(path):
    return json.loads(Path(path).read_text())


def current_targets():
    """Derive mandatory cases from current inputs, never observed native records."""
    mechanical = architecture_mechanical.run()
    cases = [architecture.canonical_case(c) for c in mechanical["cases"]]
    cases += architecture.six_car_cases(architecture.read(architecture.BASIS))
    targets = []
    for identity in ARCHITECTURES:
        choices = [c for c in cases if c["architecture_id"] == identity]
        if not choices:
            raise ValueError("required architecture input missing: " + identity)
        selected = max(choices, key=lambda c: (c["total_mass_kg"], c["id"]))
        architecture.validate_case(selected, current=True)
        targets.append(selected)
    if len({c["id"] for c in targets}) != len(ARCHITECTURES):
        raise ValueError("required architecture case identities are not distinct")
    return targets


def current_selection(case):
    basis = architecture.read(architecture.BASIS)
    report = architecture_civil.assess_pattern(
        architecture_civil.candidate_family(),
        case,
        sensitivity=basis["force_sensitivity_multiplier"],
    )
    if not report["selected_candidate_ids"]:
        raise ValueError(
            "required architecture has no selected local beam: " + case["id"]
        )
    identity = report["selected_candidate_ids"][0]
    candidate = next(c for c in report["candidates"] if c["id"] == identity)
    return identity, architecture_civil.model_definition(candidate)


def _retain_native_logs(output):
    """Exporter bootstrap/logs live outside the campaign seal; copy beside it."""
    folder = Path(output) / "campaign"
    if not folder.is_dir():
        return
    for model in folder.rglob("model.json"):
        work = ROOT / "build/factory-examples-native" / model.parent.name
        for name in ("generate.py", "freecad.log", "completed"):
            source = work / name
            if source.is_file() and not source.is_symlink():
                target = (
                    Path(output)
                    / "native-logs"
                    / model.parent.relative_to(folder)
                    / name
                )
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(source, target)


def validate_model(folder, record, expected_identity, expected_model):
    """Require an exact fresh model definition and complete native reopen proof."""
    if record.get("status") != "passed" or record.get("physical_release") is not False:
        raise ValueError(
            "required architecture native model did not pass: "
            + record.get("case_id", "missing")
        )
    if record.get("candidate_id") != expected_identity:
        raise ValueError("required architecture native selection differs")
    model_path = _file(folder, record["model"])
    proof_path = _file(folder, record["receipt"])
    if proof_path.parent != model_path.parent:
        raise ValueError("architecture native proof/model folders differ")
    model = _read(model_path)
    proof = _read(proof_path)
    if model != expected_model:
        raise ValueError(
            "architecture native model differs from current selected geometry"
        )
    parts = model["parts"]
    ids = [p["id"] for p in parts]
    proof_parts = proof.get("parts", [])
    if (
        proof.get("schema") != "osr-factory-native-cad/1"
        or proof.get("physical_release") is not False
        or proof.get("fcstd_reopened") is not True
        or proof.get("step_reopened") is not True
        or proof.get("input_sha256") != sha(model_path)
        or proof.get("exporter_sha256") != sha(native.__file__)
        or proof.get("geometry_helpers_sha256")
        != sha(Path(native.__file__).with_name("models.py"))
        or type(proof.get("part_count")) is not int
        or proof["part_count"] != len(parts)
        or record.get("part_count") != len(parts)
        or type(record.get("part_count")) is not int
        or len(ids) != len(set(ids))
        or len(proof_parts) != len(parts)
        or {p["id"] for p in proof_parts} != set(ids)
        or set(proof.get("files_sha256", {})) != {"model.FCStd", "model.step"}
    ):
        raise ValueError(
            "architecture native schema/input/exporter/reopen proof incomplete"
        )
    by_id = {p["id"]: p for p in proof_parts}
    for p in parts:
        row = by_id[p["id"]]
        expected_volume = volume(p)
        expected_bounds = p["at_m"] + [
            p["at_m"][j] + global_size(p)[j] for j in range(3)
        ]
        if (
            type(row.get("volume_m3")) not in (int, float)
            or not math.isfinite(row["volume_m3"])
            or not math.isclose(
                row["volume_m3"], expected_volume, rel_tol=1e-7, abs_tol=1e-12
            )
            or not isinstance(row.get("bounds_m"), list)
            or len(row["bounds_m"]) != 6
            or any(
                type(v) not in (int, float) or not math.isfinite(v) or abs(v - w) > 1e-8
                for v, w in zip(row["bounds_m"], expected_bounds)
            )
        ):
            raise ValueError(
                "architecture native primitive correspondence differs: " + p["id"]
            )
    if not math.isclose(
        proof.get("volume_sum_m3", float("nan")),
        sum(volume(p) for p in parts),
        rel_tol=1e-7,
        abs_tol=1e-12,
    ):
        raise ValueError("architecture native total occupied volume differs")
    cad = {}
    for name in ("model.FCStd", "model.step"):
        path = _file(folder, (model_path.parent / name).relative_to(folder))
        if sha(path) != proof["files_sha256"][name]:
            raise ValueError("architecture native CAD artifact changed: " + name)
        cad[name] = sha(path)
    return dict(
        case_id=record["case_id"],
        candidate_id=expected_identity,
        part_count=len(parts),
        model_sha256=sha(model_path),
        receipt_sha256=sha(proof_path),
        cad_sha256=cad,
        fcstd_reopened=True,
        step_reopened=True,
        physical_release=False,
    )


def acceptance(folder):
    folder = Path(folder).resolve()
    request = _read(_file(folder, "request.json"))
    if (
        request.get("schema") != "osr-architecture-native-request/1"
        or request.get("native") is not True
        or any(request.get(k) is not False for k in FLAGS)
    ):
        raise ValueError("controlled mandatory architecture native request required")
    if request.get("source_sha256") != architecture.sources():
        raise ValueError(
            "architecture native request belongs to another source revision"
        )
    tools = _read(_file(folder, "prerequisites.json"))
    if (
        tools.get("available") is not True
        or tools.get("missing")
        or tools != factory.toolchain()
    ):
        raise ValueError("required architecture native tools unavailable or changed")
    campaign_folder = folder / "campaign"
    verified = architecture.verify(campaign_folder, current=True)
    if not verified.get("integrity_verified") or not verified.get(
        "current_sources_checked"
    ):
        raise ValueError("fresh current architecture campaign verification required")
    campaign_request = _read(_file(campaign_folder, "request.json"))
    if campaign_request.get("native") is not True:
        raise ValueError("architecture acceptance requires fresh native execution")
    report = _read(_file(campaign_folder, "report.json"))
    if any(report.get(k) is not False for k in FLAGS):
        raise ValueError("architecture native evidence cannot grant design/release")
    targets = current_targets()
    required = {c["id"] for c in targets}
    records = report.get("native_geometry", [])
    if (
        request.get("required_case_ids") != [c["id"] for c in targets]
        or len(records) != len(ARCHITECTURES)
        or {r["case_id"] for r in records} != required
    ):
        raise ValueError("required architecture native model/case membership differs")
    by_case = {r["case_id"]: r for r in records}
    cases = {r["id"]: r for r in report["cases"]}
    results = []
    for target in targets:
        if target["id"] not in cases or cases[target["id"]]["case"] != target:
            raise ValueError(
                "required native architecture case differs from current inputs"
            )
        candidate, model = current_selection(target)
        if (
            not cases[target["id"]]["selected_local_beam_ids"]
            or cases[target["id"]]["selected_local_beam_ids"][0] != candidate
        ):
            raise ValueError("required architecture local beam selection differs")
        results.append(
            validate_model(campaign_folder, by_case[target["id"]], candidate, model)
        )
    return dict(
        schema=SCHEMA,
        passed=True,
        required_architectures=list(ARCHITECTURES),
        required_case_ids=[c["id"] for c in targets],
        required_model_count=len(ARCHITECTURES),
        native_models=results,
        current_sources_checked=True,
        numerical_selection_recomputed=True,
        fresh_native_execution_required=True,
        source_sha256=request["source_sha256"],
        engineering_design_complete=False,
        manufacturing_release=False,
        physical_release=False,
    )


def run(output):
    output = Path(output).resolve()
    if output.exists() or not output.is_relative_to(ROOT / "build"):
        raise ValueError("architecture native acceptance needs a fresh build directory")
    output.mkdir(parents=True)
    try:
        targets = current_targets()
        _write(
            output / "request.json",
            dict(
                schema="osr-architecture-native-request/1",
                native=True,
                required_case_ids=[c["id"] for c in targets],
                source_sha256=architecture.sources(),
                engineering_design_complete=False,
                manufacturing_release=False,
                physical_release=False,
            ),
        )
        tools = factory.toolchain()
        _write(output / "prerequisites.json", tools)
        if tools.get("available") is not True or tools.get("missing"):
            raise ValueError("required architecture native tools unavailable")
        architecture.run(output / "campaign", native=True)
        _retain_native_logs(output)
        result = acceptance(output)
        _write(output / "acceptance.json", result)
        return result
    except Exception as error:
        try:
            _retain_native_logs(output)
        except (OSError, ValueError):
            pass  # Preserve the original failure and all extant model files.
        failure = dict(
            schema=SCHEMA,
            passed=False,
            error=type(error).__name__,
            message=str(error),
            required_architectures=list(ARCHITECTURES),
            retained_campaign=(output / "campaign").is_dir(),
            engineering_design_complete=False,
            manufacturing_release=False,
            physical_release=False,
        )
        _write(output / "failure.json", failure)
        _write(output / "acceptance.json", failure)
        raise


def verify(folder):
    folder = Path(folder).resolve()
    retained = _read(_file(folder, "acceptance.json"))
    if retained != acceptance(folder):
        raise ValueError("architecture native acceptance record changed or failed")
    return retained


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("run", "verify"))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        result = run(args.output) if args.action == "run" else verify(args.output)
    except Exception as error:
        print(
            json.dumps(
                dict(
                    passed=False,
                    error=type(error).__name__,
                    message=str(error),
                    physical_release=False,
                ),
                sort_keys=True,
            )
        )
        return 1
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
