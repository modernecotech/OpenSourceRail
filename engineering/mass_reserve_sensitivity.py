"""Bounded design-stage sensitivity for the selected vehicle's mass reserves.

Positive accounting residuals already sit inside the accounted tare. Each case
replaces those residual balances with a declared sensitivity value; it never
adds a second allowance on top of them. The report does not close installed
mass, component locations, centre of gravity, inertia, or axle reactions.
"""
from __future__ import annotations

import argparse
import gzip
import json
import math
import tomllib
from pathlib import Path

from engineering.station_rail import ROOT, FLAGS
from engineering.station_rail.common import digest, encoded, identity
from . import mass_ledger_audit

PRODUCER = "engineering/mass_reserve_sensitivity.py"
CONFIG = "campaigns/mass-reserve-sensitivity.toml"
INPUT = "docs/design-engine/mass-reconciliation/current"
OUTPUT = "docs/design-engine/mass-reserve-sensitivity/current"


def _specification(root):
    root = Path(root)
    value = tomllib.loads((root / CONFIG).read_text())
    cases = value.get("cases", {})
    names, factors = cases.get("names", []), cases.get("reserve_factors", [])
    if (value.get("schema") != "osr-current-mass-reserve-sensitivity/1"
            or names != ["low", "base", "high"] or len(factors) != 3
            or any(not math.isfinite(float(f)) or float(f) <= 0 for f in factors)
            or factors[1] != 1.0):
        raise ValueError("Mass sensitivity requires positive low/base/high factors with an exact base factor")
    value["config_sha256"] = digest(root / CONFIG)
    value["assumption_id"] = identity(value)
    return value


def plan(root=ROOT):
    root = Path(root).resolve()
    verified = mass_ledger_audit.verify(root)
    folder = root / INPUT
    manifest = json.loads((folder / "manifest.json").read_bytes())
    worksheet = json.loads(gzip.decompress((folder / "mass-closure-worksheet.json.gz").read_bytes()))
    summary = json.loads((folder / "summary.json").read_bytes())
    config = _specification(root)
    if (verified.get("verified") is not True
            or worksheet.get("candidate_id") != config["source_candidate_id"]
            or worksheet.get("selection_id") != config["source_selection_id"]
            or worksheet.get("worksheet_id") != summary.get("closure_worksheet_id")
            or worksheet.get("unknown_is_zero") is not False
            or summary.get("installed_mass_complete") is not False):
        raise ValueError("Selected mass ledger/worksheet identity or open-evidence state differs")
    closures = [r for r in worksheet["rows"] if r.get("record_kind") == "account-closure"]
    if len(closures) != summary.get("account_row_count"):
        raise ValueError("Mass reserve requires every canonical account closure exactly once")
    residual_rows = []
    reconciled_geometry_accounts = []
    for row in closures:
        accounted = float(row["accounted_source_mass_kg"])
        geometry = float(row["candidate_geometry_mass_kg"])
        residual = float(row["accounting_residual_kg"])
        if (not all(math.isfinite(v) for v in (accounted, geometry, residual))
                or min(accounted, geometry, residual) < -1e-8
                or abs(accounted - geometry - residual) > 1e-6):
            raise ValueError("Accounted mass must reconcile once into geometry plus residual reserve")
        if residual > 1e-8:
            residual_rows.append(dict(account_id=row["account_id"],
                accounted_source_mass_kg=accounted,
                candidate_geometry_mass_kg=geometry,
                existing_residual_kg=residual,
                mass_evidence_class=row["mass_evidence_class"],
                scenario_reserve_kg={name: residual * factor for name, factor
                    in zip(config["cases"]["names"], config["cases"]["reserve_factors"])},
                added_instead_of_replaced=False,
                physically_installed_mass_kg=None, installed_position_m=None,
                component_identity_resolved=False))
        else:
            reconciled_geometry_accounts.append(dict(account_id=row["account_id"],
                accounted_source_mass_kg=accounted,
                candidate_geometry_mass_kg=geometry,
                accounting_residual_kg=0.0,
                note="Accounting subtotal matches represented geometry. This does not verify installation or exclude unmodelled joints, fasteners, or interfaces."))
    if len(residual_rows) != summary.get("closure_worksheet_account_residual_count"):
        raise ValueError("Positive residual account count differs from the exact closure worksheet")
    factors = config["cases"]["reserve_factors"]
    names = config["cases"]["names"]
    located = float(summary["located_geometry_mass_kg"])
    accounted_tare = float(summary["accounted_tare_kg_per_car"])
    residual_total = float(summary["residual_reference_or_unlocated_mass_kg"])
    if (abs(sum(r["existing_residual_kg"] for r in residual_rows) - residual_total) > 1e-6
            or abs(located + residual_total - accounted_tare) > 1e-6):
        raise ValueError("Per-account reserves do not close to the existing selected-candidate tare")
    cases = []
    for name, factor in zip(names, factors):
        reserve = sum(r["scenario_reserve_kg"][name] for r in residual_rows)
        tare = located + reserve
        cases.append(dict(name=name, reserve_factor=factor,
            existing_unlocated_reserve_kg=residual_total,
            sensitivity_reserve_kg=reserve,
            located_geometry_subtotal_kg=located,
            scenario_tare_mass_kg_per_car=tare,
            six_car_scenario_tare_mass_kg=6.0 * tare,
            change_from_accounted_tare_kg_per_car=tare - accounted_tare,
            scenario_basis="Located candidate geometry subtotal plus the re-scaled existing residual accounts; no duplicate reserve added."))
    source_files = {name: digest(root / name) for name in (
        "engineering/mass_ledger_audit.py", CONFIG,
        f"{INPUT}/manifest.json", f"{INPUT}/mass-closure-worksheet.json.gz",
        f"{INPUT}/summary.json")}
    result = dict(schema="osr-current-mass-reserve-sensitivity-result/1",
        assumption_id=config["assumption_id"], ledger_manifest_id=manifest["manifest_id"],
        worksheet_id=worksheet["worksheet_id"], candidate_id=worksheet["candidate_id"],
        body_candidate_id=worksheet["body_candidate_id"], selection_id=worksheet["selection_id"],
        evaluation_id=worksheet["evaluation_id"], vehicle_evaluation_id=worksheet["vehicle_evaluation_id"],
        accounted_tare_mass_kg_per_car=accounted_tare,
        located_geometry_mass_kg_per_car=located,
        existing_unlocated_residual_kg_per_car=residual_total,
        residual_account_count=len(residual_rows), reserve_accounts=residual_rows,
        geometry_reconciled_accounts=reconciled_geometry_accounts,
        sensitivity_cases=cases,
        complete_installed_mass_kg_per_car=None, installed_centre_of_gravity_m=None,
        installed_inertia_kg_m2=None, axle_reactions=None,
        mass_scenario_complete_for_declared_scope=True,
        physically_installed_mass_known=False,
        physical_acceptance=False, interpretation=(
            "This is a provisional sensitivity of the existing selected-candidate mass account. "
            "The low/base/high factors are declared scenarios, not probability bounds. Positive "
            "residuals are replaced within each scenario; they are not added twice. Equipment, "
            "joint, fastener, cooling, wiring, and installation identities/locations remain open "
            "where the source worksheet has no physical component evidence."),
        source_sha256=source_files, **FLAGS)
    result["result_id"] = identity(result)
    return result


def _readme(result):
    lines = ["# Selected vehicle mass reserve sensitivity", "",
        f"Candidate `{result['candidate_id']}` and selection `{result['selection_id']}` retain the source ledger's accounted tare of **{result['accounted_tare_mass_kg_per_car']:,.3f} kg/car**. Candidate geometry represents **{result['located_geometry_mass_kg_per_car']:,.3f} kg/car**. The existing positive accounting residual is **{result['existing_unlocated_residual_kg_per_car']:,.3f} kg/car** across {result['residual_account_count']} accounts.", "",
        "Each low/base/high case replaces that existing residual reserve with a declared 0.8×/1.0×/1.2× sensitivity. The reserve is not added again on top of the accounted tare.", "",
        "| Case | Reserve sensitivity (kg/car) | Scenario tare (kg/car) | Six-car scenario tare (kg) | Change from existing tare (kg/car) |",
        "|---|---:|---:|---:|---:|"]
    for row in result["sensitivity_cases"]:
        lines.append(f"| {row['name']} ({row['reserve_factor']:.1f}×) | {row['sensitivity_reserve_kg']:,.3f} | {row['scenario_tare_mass_kg_per_car']:,.3f} | {row['six_car_scenario_tare_mass_kg']:,.3f} | {row['change_from_accounted_tare_kg_per_car']:+,.3f} |")
    lines += ["", "## Account-level reserves", "",
        "| Account | Existing residual (kg/car) | Low (kg/car) | Base (kg/car) | High (kg/car) |",
        "|---|---:|---:|---:|---:|"]
    for row in result["reserve_accounts"]:
        s = row["scenario_reserve_kg"]
        lines.append(f"| {row['account_id']} | {row['existing_residual_kg']:,.3f} | {s['low']:,.3f} | {s['base']:,.3f} | {s['high']:,.3f} |")
    lines += ["", "## Scope and evidence", "",
        result["interpretation"], "",
        "The two accounts with no accounting residual reconcile to represented geometry mass; this still does not prove installation or exclude additional physical joints, fasteners, and interfaces. No reserve has been declared for those unknowns, so installed mass is not complete.", "",
        "The 0.8×/1.0×/1.2× factors are sensitivity assumptions only. They are not statistical confidence limits or supplier-confirmed ranges. Replace them with component-specific calculated mass or measured procurement/installation evidence when available.", "",
        "The selected reference, CAD, and release states are unchanged. Centre of gravity, inertia, axle reactions, and complete installed mass remain unknown.", "",
        "Reproduce with `python3 -m engineering.mass_reserve_sensitivity build` and `python3 -m engineering.mass_reserve_sensitivity verify`.", "",
        "[Exact result](result.json) · [Manifest](manifest.json)", ""]
    return "\n".join(lines)


def publish(root=ROOT, output=None):
    root = Path(root).resolve()
    out = root / OUTPUT if output is None else Path(output)
    result = plan(root)
    out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_bytes(encoded(result))
    (out / "README.md").write_text(_readme(result))
    sources = dict(result["source_sha256"], **{PRODUCER: digest(root / PRODUCER)})
    manifest = dict(schema="osr-current-mass-reserve-sensitivity-manifest/1",
        result_id=result["result_id"], source_sha256=sources,
        files_sha256={p.relative_to(out).as_posix(): digest(p) for p in out.rglob("*")
                      if p.is_file() and p.name != "manifest.json"},
        physical_acceptance=False, **FLAGS)
    manifest["manifest_id"] = identity(manifest)
    (out / "manifest.json").write_bytes(encoded(manifest))
    return verify(root, out)


def verify(root=ROOT, output=None):
    root = Path(root).resolve()
    out = root / OUTPUT if output is None else Path(output)
    manifest = json.loads((out / "manifest.json").read_bytes())
    actual = {p.relative_to(out).as_posix(): digest(p) for p in out.rglob("*")
              if p.is_file() and p.name != "manifest.json"}
    if (manifest.get("manifest_id") != identity({k: v for k, v in manifest.items()
                                                   if k != "manifest_id"})
            or manifest.get("files_sha256") != actual
            or any(digest(root / name) != value for name, value in manifest.get("source_sha256", {}).items())):
        raise ValueError("Mass reserve sensitivity manifest, payload or source epoch differs")
    result = json.loads((out / "result.json").read_bytes())
    expected = plan(root)
    if result != expected or manifest.get("result_id") != expected.get("result_id"):
        raise ValueError("Mass reserve sensitivity does not replay from the selected exact worksheet")
    if (result.get("installed_mass_complete") is not False
            or result.get("complete_installed_mass_kg_per_car") is not None
            or result.get("physical_acceptance") is not False):
        raise ValueError("Mass sensitivity cannot grant installed-mass or physical acceptance")
    return dict(verified=True, result_id=result["result_id"],
        candidate_id=result["candidate_id"], selection_id=result["selection_id"],
        residual_account_count=result["residual_account_count"],
        low_tare_kg_per_car=result["sensitivity_cases"][0]["scenario_tare_mass_kg_per_car"],
        base_tare_kg_per_car=result["sensitivity_cases"][1]["scenario_tare_mass_kg_per_car"],
        high_tare_kg_per_car=result["sensitivity_cases"][2]["scenario_tare_mass_kg_per_car"],
        complete_installed_mass_kg_per_car=None, **FLAGS)


def main(argv=None):
    parser = argparse.ArgumentParser(prog="python3 -m engineering.mass_reserve_sensitivity")
    parser.add_argument("action", choices=("build", "verify"))
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    result = publish(args.root, args.output) if args.action == "build" else verify(args.root, args.output)
    print(json.dumps(result, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
