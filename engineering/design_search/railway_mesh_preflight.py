"""Exact nested anisotropic cell-count preflight for the held current mesh.

This computes the axis planes and disjoint-box solid-cell totals only. It does
not build a native deck, estimate solver memory, run CalculiX, or qualify the
unchanged vehicle candidate.
"""
from __future__ import annotations

import json
import math
import tomllib
from bisect import bisect_left
from math import ceil, prod
from pathlib import Path

from engineering.station_rail import ROOT, FLAGS
from engineering.station_rail.common import digest, encoded, identity
from . import railway_native, railway_publication, grammar_shell

PRODUCER = "engineering/design_search/railway_mesh_preflight.py"
CONFIG = "campaigns/current-mesh-preflight.toml"
OUTPUT = "docs/design-engine/current-mesh-preflight"


def specification(root=ROOT):
    root = Path(root)
    config = tomllib.loads((root / CONFIG).read_text())
    if config.get("schema") != "osr-current-mesh-preflight/1":
        raise ValueError("Unexpected mesh preflight schema")
    profiles = config.get("profiles", [])
    if len(profiles) != 8 or len({p.get("name") for p in profiles}) != len(profiles):
        raise ValueError("Eight uniquely named axis refinement profiles are required")
    if any(len(p.get("axis_steps_m", [])) != 3
           or any(not math.isfinite(float(s)) or not 0.01 <= float(s) <= 2.0
                  for s in p["axis_steps_m"]) for p in profiles):
        raise ValueError("Every profile needs three finite mesh steps within the declared builder domain")
    if (config.get("load_case") != "normal" or config.get("element_kind") != "C3D8I"
            or config.get("previous_mesh_m") != 0.10625
            or config.get("next_uniform_mesh_m") != 0.053125):
        raise ValueError("The profile comparison must retain its exact current mesh and load context")
    config["config_sha256"] = digest(root / CONFIG)
    config["assumption_id"] = identity(config)
    return config


def _axes(parts, steps):
    axes = []
    for d, step in enumerate(steps):
        cuts = {round(p["at_m"][d] + side * p["size_m"][d], 10)
                for p in parts for side in (0, 1)}
        low, high = min(cuts), max(cuts)
        count = ceil((high - low) / step)
        cuts.update(round(low + (high - low) * i / count, 10)
                    for i in range(count + 1))
        axes.append(sorted(cuts))
    return axes


def _estimate(parts, steps, reference_axes=None):
    axes = _axes(parts, steps)
    cells = 0
    for part in parts:
        cells += prod(
            bisect_left(axes[d], round(part["at_m"][d] + part["size_m"][d], 10))
            - bisect_left(axes[d], round(part["at_m"][d], 10))
            for d in range(3))
    nested = None if reference_axes is None else [
        all(x in set(axes[d]) for x in reference_axes[d]) for d in range(3)]
    return dict(solid_cells=cells, coordinate_planes=[len(a) for a in axes],
                nested_with_reference_axes=nested)


def plan(root=ROOT):
    root = Path(root)
    config = specification(root)
    folder, campaign = railway_publication.current(root)
    bodies = {b["candidate_id"]: b for b in campaign["bodies"]}
    body = bodies.get(config["body_candidate_id"])
    bundles = {b["candidate_id"]: b for b in campaign["bundles"]}
    bundle = bundles.get(config["bundle_id"])
    if (body is None or bundle is None
            or body.get("definition_id") != config["body_definition_id"]
            or bundle.get("definition_id") != config["bundle_definition_id"]
            or bundle.get("body_candidate_id") != body["candidate_id"]):
        raise ValueError("Preflight candidate or bundle differs from the current canonical campaign")
    if bundle.get("family_id") != "P1":
        raise ValueError("Current mesh preflight is fixed to the canonical P1 bundle")
    structural_ids = set(body.get("shell_model", {}).get("structural_part_ids", []))
    parts = [p for p in body["parts"] if p["id"] in structural_ids]
    if not parts:
        raise ValueError("No canonical structural stock is available for mesh preflight")
    reference = next(p for p in config["profiles"]
                     if p["name"] == "reference-0.10625-isotropic")
    reference_estimate = _estimate(parts, reference["axis_steps_m"])
    if reference_estimate["solid_cells"] != 128_382:
        raise ValueError("Exact current 0.10625 m count differs from the preserved refinement")
    reference_axes = _axes(parts, reference["axis_steps_m"])
    rows = []
    for profile in config["profiles"]:
        estimate = _estimate(parts, profile["axis_steps_m"], reference_axes)
        rows.append(dict(name=profile["name"], axis_steps_m=profile["axis_steps_m"],
                         **estimate,
                         cells_over_reference=estimate["solid_cells"] - reference_estimate["solid_cells"],
                         percent_over_reference=100.0 * (estimate["solid_cells"]
                                                         / reference_estimate["solid_cells"] - 1.0),
                         exceeds_previous_cell_budget=(estimate["solid_cells"]
                                                        > config["previous_cell_budget"])))
    sources = {
        **campaign["source_sha256"],
        PRODUCER: digest(root / PRODUCER),
        CONFIG: digest(root / CONFIG),
        railway_publication.PRODUCER: digest(root / railway_publication.PRODUCER),
        railway_native.PRODUCER: digest(root / railway_native.PRODUCER),
        grammar_shell.PRODUCER: digest(root / grammar_shell.PRODUCER),
    }
    if any(digest(root / name) != value for name, value in sources.items()):
        raise ValueError("Current mesh preflight source epoch changed during evaluation")
    result = dict(schema="osr-current-mesh-preflight-result/1",
                  assumption_id=config["assumption_id"],
                  parent_campaign_id=campaign["campaign_id"],
                  parent_contract_id=campaign["contract_id"],
                  parent_run_id=campaign["run_id"],
                  body_candidate_id=body["candidate_id"],
                  body_definition_id=body["definition_id"],
                  bundle_id=bundle["candidate_id"],
                  bundle_definition_id=bundle["definition_id"],
                  load_case=config["load_case"],
                  load_mass_kg=bundle["normal_sprung_mass_hypothesis_kg"],
                  element_kind=config["element_kind"],
                  structural_part_count=len(parts), profiles=rows,
                  solver_invocations=0, native_deck_generated=False,
                  physical_candidate_changed=False,
                  computational_resource_hold=True,
                  configuration_adopted=False,
                  selected_reference_changed=False,
                  physical_journey_completed=False,
                  prior_resource_request=dict(cell_budget=config["previous_cell_budget"],
                                              memory_mb=8192, timeout_s=240),
                  resource_boundary_note=("Cell and coordinate-plane counts are exact for the retained "
                      "disjoint-box conformal construction. They do not estimate factorization memory "
                      "or runtime. No native deck or solver invocation was made. The uniform 0.053125 m "
                      "case remains held on this host; any finer run needs an explicitly reviewed "
                      "worker/process-tree resource boundary and observed peak memory."),
                  source_sha256=sources, **FLAGS)
    result["result_id"] = identity(result)
    return result


def _readme(value):
    rows = value["profiles"]
    lines = ["# Current mesh resource preflight", "",
             f"This exact preflight is bound to body `{value['body_candidate_id']}`, definition "
             f"`{value['body_definition_id']}`, P1 bundle `{value['bundle_id']}`, normal load "
             f"({value['load_mass_kg']:.3f} kg sprung-mass hypothesis), and `{value['element_kind']}`.", "",
             "It counts nested axis-plane refinements of the same disjoint-box stock. The operation "
             "does not generate a native deck or call CalculiX. It reports no memory or runtime estimate.", "",
             "| Profile | x / y / z step (m) | Solid cells | Coordinate planes x / y / z | Nested from reference | Over reference | Prior 140,000-cell budget |",
             "|---|---:|---:|---:|---|---:|---|"]
    for row in rows:
        steps = " / ".join(f"{v:.6f}" for v in row["axis_steps_m"])
        nested = "yes" if all(row["nested_with_reference_axes"]) else "no"
        planes = " / ".join(map(str, row["coordinate_planes"]))
        budget = "exceeds" if row["exceeds_previous_cell_budget"] else "within"
        lines.append(f"| {row['name']} | {steps} | {row['solid_cells']:,} | {planes} | {nested} | "
                     f"{row['percent_over_reference']:.1f}% | {budget} |")
    smallest = min((r for r in rows if r["name"] != "reference-0.10625-isotropic"),
                   key=lambda r: r["solid_cells"])
    lines += ["", f"The least-cell nested refinement is **{smallest['name']}** at "
              f"{smallest['solid_cells']:,} cells, {smallest['percent_over_reference']:.1f}% over the "
              f"reference mesh. It still exceeds the prior {value['prior_resource_request']['cell_budget']:,}-cell "
              "allowance. This is a mesh-count comparison, not a solver resource prediction or selection.", "",
              "## Resource hold", "",
              value["resource_boundary_note"], "",
              "The earlier 0.10625 m solve completed 128,382 cells with a requested 8 GiB solver-child "
              "address-space cap and 240 s timeout. A separate 5 GiB attempt failed during factorization. "
              "The saved tool receipt records the requested RLIMIT_AS, not observed peak RSS. The next "
              "full solve therefore needs a suitably provisioned worker, a process-tree memory boundary, "
              "and peak-RSS collection before resource settings are selected.", "",
              "All engineering, numerical, and physical qualification obligations remain unchanged. "
              "No result from these counts establishes structural adequacy.", "",
              "[Exact profile result](result.json) · [Manifest](manifest.json)", ""]
    return "\n".join(lines)


def publish(root=ROOT, output=None):
    root = Path(root)
    out = root / OUTPUT if output is None else Path(output)
    result = plan(root)
    out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_bytes(encoded(result))
    (out / "README.md").write_text(_readme(result))
    sources = result["source_sha256"]
    manifest = dict(schema="osr-current-mesh-preflight-manifest/1",
                    result_id=result["result_id"], source_sha256=sources,
                    files_sha256={p.relative_to(out).as_posix(): digest(p)
                                  for p in out.rglob("*")
                                  if p.is_file() and p.name != "manifest.json"},
                    solver_invocations=0, configuration_adopted=False,
                    selected_reference_changed=False, physical_journey_completed=False,
                    **FLAGS)
    manifest["manifest_id"] = identity(manifest)
    (out / "manifest.json").write_bytes(encoded(manifest))
    return verify(root, out)


def verify(root=ROOT, output=None):
    root = Path(root)
    out = root / OUTPUT if output is None else Path(output)
    manifest = json.loads((out / "manifest.json").read_bytes())
    actual = {p.relative_to(out).as_posix(): digest(p) for p in out.rglob("*")
              if p.is_file() and p.name != "manifest.json"}
    if (manifest.get("manifest_id") != identity({k: v for k, v in manifest.items()
                                                   if k != "manifest_id"})
            or manifest.get("files_sha256") != actual
            or any(digest(root / name) != value
                   for name, value in manifest.get("source_sha256", {}).items())):
        raise ValueError("Current mesh preflight manifest, payload, or source epoch differs")
    result = json.loads((out / "result.json").read_bytes())
    expected = plan(root)
    if result != expected or manifest.get("result_id") != expected.get("result_id"):
        raise ValueError("Published mesh preflight does not reproduce from current exact inputs")
    if result.get("solver_invocations") != 0 or result.get("native_deck_generated") is not False:
        raise ValueError("Mesh preflight cannot claim numerical solver evidence")
    next_cells = min(r["solid_cells"] for r in result["profiles"]
                     if r["name"] != "reference-0.10625-isotropic")
    return dict(verified=True, result_id=result["result_id"],
                profile_count=len(result["profiles"]), solver_invocations=0,
                least_refined_cell_count=next_cells,
                computational_resource_hold=True, configuration_adopted=False,
                selected_reference_changed=False, physical_journey_completed=False,
                **FLAGS)
