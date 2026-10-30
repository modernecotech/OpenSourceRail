"""Reproducible comparison of exact railway bundles and partial civil costs.

The report joins the current candidate-to-journey closure to the Iraqi civil
materials/labour screen. It preserves source row identities and keeps physical
acceptance, selected status, complete installed cost and whole-life cost open.
"""
from decimal import Decimal
from hashlib import sha256
import json
from pathlib import Path

from engineering.station_rail.common import ROOT as REPOSITORY_ROOT
from engineering.station_rail.common import digest, encoded, identity
from engineering.sourcing.closure_civil_cost import (
    _load_closure,
    verify_packet as verify_civil_packet,
)


OUTPUT_DIR = Path("docs/design-engine/railway-comparison-2026-10")
CIVIL_OUTPUT_DIR = Path(
    "docs/design-engine/sourcing/domestic-fabrication/"
    "candidate-span-cost-screen-2026-10")
REPORT_FILE = "candidate-comparison.json"
MANIFEST_FILE = "manifest.json"
README_FILE = "README.md"


def _decimal(value):
    parsed = Decimal(str(value))
    if not parsed.is_finite():
        raise ValueError("Comparative report contains a non-finite cost")
    return parsed


def _selected_2026_scenario(cost_screen, region_name):
    region = next((row for row in cost_screen["regions"]
                   if row.get("region") == region_name), None)
    if region is None:
        raise ValueError("Civil cost row lacks declared 2026 region " + region_name)
    matches = [row for row in region["combined_assumed_labour_scenarios"]
               if row.get("concrete_labour_hours_per_m3") == "4"
               and row.get("reinforcement_cut_bend_hours_per_t") == "8"]
    if len(matches) != 1:
        raise ValueError("Civil cost row lacks one 4h/m3 + 8h/t 2026 scenario")
    return matches[0]


def _selected_2025_scenario(annual_region, wage_category="skilled"):
    sensitivities = annual_region.get("worker_category_rate_sensitivities", {})
    category = sensitivities.get(wage_category)
    if not isinstance(category, dict):
        raise ValueError("Annual CSO comparison lacks wage category " + wage_category)
    matches = [row for row in category.get("scenarios", [])
               if row.get("concrete_labour_hours_per_m3") == "4"
               and row.get("reinforcement_cut_bend_hours_per_t") == "8"]
    if len(matches) != 1:
        raise ValueError("Annual CSO comparison lacks one 4h/m3 + 8h/t scenario")
    return matches[0]


def _cost_summary(cost_screen):
    current = {}
    for region_name in ("Baghdad", "Al-Muthanna"):
        current[region_name] = _selected_2026_scenario(cost_screen, region_name)

    annual_by_region = {}
    annual = cost_screen["annual_2025_regional_crosscheck"]
    for region in annual.get("regional_material_and_wage_scenarios", []):
        annual_by_region[region["region"]] = _selected_2025_scenario(region)
    if set(annual_by_region) != {"Baghdad", "Al-Muthanna"}:
        raise ValueError("Annual CSO cost crosscheck region inventory differs")
    return {
        "scope": cost_screen["cost_scope"],
        "formula": cost_screen["formula"],
        "uplift_fraction": cost_screen["uplift_fraction"],
        "scenario_assumptions": {
            "concrete_person_hours_per_m3": "4",
            "reinforcement_cut_bend_person_hours_per_t": "8",
            "annual_2025_wage_category": "skilled",
            "annual_2025_wage_interpretation": (
                "Single-category rate sensitivity applied to all assumed hours; "
                "not a crew mix or factory charge-out rate."),
        },
        "september_2026_by_region": current,
        "annual_2025_cso_by_region": annual_by_region,
        "complete_precaster_cost_iqd": None,
        "installed_civil_cost_iqd": None,
        "whole_life_cost_iqd": None,
    }


def build_report(root=REPOSITORY_ROOT):
    """Build one report row per exact candidate bundle with matched span costs."""
    root = Path(root).resolve()
    closure_manifest, closure, comparison = _load_closure(root)
    civil_dir = root / CIVIL_OUTPUT_DIR
    civil_verification = verify_civil_packet(civil_dir, root=root)
    civil_manifest = json.loads((civil_dir / "manifest.json").read_bytes())
    civil_packet = json.loads((civil_dir / "candidate-span-cost-screen.json").read_bytes())

    if (comparison.get("physical_accepted") is not False
            or comparison.get("engineering_accepted") is not False
            or closure_manifest.get("physical_accepted") is not False
            or civil_packet.get("physical_accepted") is not False
            or civil_packet.get("engineering_accepted") is not False
            or civil_packet.get("unknown_is_zero") is not False):
        raise ValueError("Comparative inputs contain an inconsistent acceptance or unknown policy")
    if (civil_packet.get("comparison_id") != comparison.get("comparison_id")
            or civil_packet.get("closure_evaluation_id") != closure.get("evaluation_id")
            or civil_packet.get("closure_publication_id") != closure_manifest.get("publication_id")):
        raise ValueError("Civil cost packet does not bind the exact current closure comparison")

    civil_by_key = {}
    for row in civil_packet.get("rows", []):
        key = (row.get("candidate_id"), row.get("bundle_id"),
               row.get("civil_alternative", {}).get("alternative_id"))
        if None in key or key in civil_by_key:
            raise ValueError("Civil cost packet has missing or duplicate candidate/alternative identities")
        screen = row.get("cost_screen", {})
        if (screen.get("candidate_id") != row["candidate_id"]
                or screen.get("bundle_id") != row["bundle_id"]
                or screen.get("alternative_id") != key[2]
                or screen.get("physical_civil_component_id") !=
                   row["civil_alternative"].get("physical_civil_component_id")
                or screen.get("candidate_quantities_mapped") is not True
                or screen.get("complete_process_cost_iqd") is not None
                or screen.get("installed_cost_iqd") is not None
                or screen.get("whole_life_cost_iqd") is not None):
            raise ValueError("Civil cost row identity, quantity mapping or open-cost state differs")
        civil_by_key[key] = row

    candidates = []
    seen_bundles = set()
    for row in comparison.get("rows", []):
        candidate_id = row["candidate_id"]
        bundle_id = row["bundle_id"]
        if candidate_id != bundle_id or bundle_id in seen_bundles:
            raise ValueError("Current comparison has inconsistent or duplicate physical bundle identities")
        seen_bundles.add(bundle_id)
        if row.get("comparison_row_id") != identity({
                key: value for key, value in row.items() if key != "comparison_row_id"}):
            raise ValueError("Candidate comparison row identity differs")
        if row.get("acceptance", {}).get("physical_accepted") is not False:
            raise ValueError("Candidate comparison row has an unexpected physical acceptance state")

        span_rows = []
        for alternative in row.get("civil_alternatives", []):
            key = (candidate_id, bundle_id, alternative.get("alternative_id"))
            matched = civil_by_key.get(key)
            if matched is None:
                raise ValueError("No exact domestic cost row for candidate/span " + repr(key))
            if (matched.get("body_candidate_id") != row.get("body_candidate_id")
                    or matched.get("body_family") != row.get("body_family")
                    or matched.get("architecture_family") != row.get("architecture_family")
                    or matched.get("route_distance_m") != row.get("route_distance_m")
                    or matched.get("requirement_revision") != row.get("requirement_revision")
                    or matched["civil_alternative"].get("physical_civil_component_id") !=
                       alternative.get("physical_civil_component_id")
                    or matched["civil_alternative"].get("concrete_m3") != alternative.get("concrete_m3")):
                raise ValueError("Candidate and civil-cost row do not share exact bundle/component quantities")
            cost_screen = matched["cost_screen"]
            span_rows.append({
                "civil_alternative": alternative,
                "cost_screen_id": cost_screen["estimate_id"],
                "cost_scope": cost_screen["cost_scope"],
                "cost_summary": _cost_summary(cost_screen),
                "complete_process_cost_iqd": None,
                "installed_cost_iqd": None,
                "whole_life_cost_iqd": None,
                "source_cost_screen": cost_screen,
            })
        if len(span_rows) != 3:
            raise ValueError("Expected the same three civil alternatives for each candidate bundle")

        identity_fields = {
            "physical_candidate_id": candidate_id,
            "bundle_id": bundle_id,
            "body_candidate_id": row["body_candidate_id"],
            "bundle_definition_id": row.get("bundle_definition_id"),
            "comparison_row_id": row["comparison_row_id"],
            "closure_evaluation_id": closure["evaluation_id"],
            "architecture_evaluation_id": row.get("architecture", {}).get("evaluation_id"),
            "inventory_evaluation_id": row.get("inventory_and_manufacturing", {}).get("inventory_evaluation_id"),
            "economics_evaluation_id": row.get("economics", {}).get("evaluation_id"),
            "requirement_revision": row.get("requirement_revision"),
            "selection_id": None,
            "selected_for_development": False,
        }
        candidate = {
            "identity": identity_fields,
            "architecture_family": row.get("architecture_family"),
            "body_family": row.get("body_family"),
            "route_distance_m": row.get("route_distance_m"),
            "comparison_row": row,
            "journey_scenarios": row.get("journey_scenarios", []),
            "civil_alternatives_with_cost_screens": span_rows,
            "unresolved_installed_and_whole_life_cost": {
                "vehicle_installed_cost_USD": row.get("economics", {}).get("vehicle_installed_cost_USD"),
                "wayside_installed_cost_USD": row.get("economics", {}).get("wayside_installed_cost_USD"),
                "civil_installed_cost_USD": row.get("economics", {}).get("civil_installed_cost_USD"),
                "whole_life_cost_USD": row.get("economics", {}).get("whole_life_cost_USD"),
                "complete_installed_mass_kg": row.get("mass", {}).get("complete_installed_mass_kg"),
                "available_force_map_id": row.get("propulsion", {}).get("available_force_map_id"),
            },
            "engineering_risks_and_next_work": row.get("engineering_risks_and_next_work", []),
            "physical_accepted": False,
            "engineering_accepted": False,
        }
        candidate["candidate_report_row_id"] = identity(candidate)
        candidates.append(candidate)

    if len(candidates) != 12 or len(civil_by_key) != 36:
        raise ValueError("Expected 12 candidates and 36 exact candidate/span cost bindings")
    candidates.sort(key=lambda item: (
        item["body_family"], item["architecture_family"], item["route_distance_m"],
        item["identity"]["physical_candidate_id"]))

    report = {
        "schema": "osr-candidate-comparative-closure-report/1",
        "report_scope": "same-service candidate comparison with domestic civil materials/base-wage screens",
        "closure_evaluation_id": closure["evaluation_id"],
        "closure_publication_id": closure_manifest["publication_id"],
        "comparison_id": comparison["comparison_id"],
        "civil_cost_publication_id": civil_manifest["publication_id"],
        "civil_cost_packet_id": civil_packet["packet_id"],
        "service_specification": comparison["same_service_specification"],
        "candidate_count": len(candidates),
        "civil_alternative_count": len(civil_by_key),
        "candidates": candidates,
        "source_files": {
            "closure_comparison": "docs/design-engine/railway-closure/comparison.json",
            "closure_cases": "docs/design-engine/railway-closure/cases.json.gz",
            "closure_manifest": "docs/design-engine/railway-closure/manifest.json",
            "civil_cost_packet": (CIVIL_OUTPUT_DIR / "candidate-span-cost-screen.json").as_posix(),
            "civil_cost_manifest": (CIVIL_OUTPUT_DIR / "manifest.json").as_posix(),
        },
        "unknown_is_zero": False,
        "selection": None,
        "selected_reference_changed": False,
        "complete_installed_cost_USD": None,
        "complete_installed_cost_IQD": None,
        "whole_life_cost": None,
        "physical_accepted": False,
        "engineering_accepted": False,
    }
    report["report_id"] = identity(report)
    return report


def _mid_cost_iqd(candidate, *, year, region):
    values = []
    for span in candidate["civil_alternatives_with_cost_screens"]:
        cost = span["cost_summary"]
        source = (cost["september_2026_by_region"] if year == 2026
                  else cost["annual_2025_cso_by_region"])
        values.append(_decimal(source[region]["partial_material_labour_plus_20pct_iqd"]))
    return min(values), max(values)


def render_readme(report):
    lines = [
        "# Candidate comparison and domestic fabrication screen",
        "",
        "This generated report joins the exact candidate-to-journey comparison with the candidate-bound Iraqi civil material and base-wage screen. It covers 12 bundles (three body families × two drive families × two routes) and all 36 matched 20 m beam alternatives.",
        "",
        "**No candidate is selected or physically accepted.** Complete installed vehicle mass, available station-drive force maps, completed fault journeys, supplier-installed costs, complete civil installed costs and whole-life cost remain open. The domestic civil values below price only the declared concrete ingredients and reinforcement allowance plus assumed labour, with a 20% planning uplift.",
        "",
        f"Closure evaluation `{report['closure_evaluation_id']}` · comparison `{report['comparison_id']}` · civil cost packet `{report['civil_cost_packet_id']}` · report `{report['report_id']}`.",
        "",
        "## Candidate matrix",
        "",
        "Costs are per span, not per route. The 2026 range covers the three civil alternatives and the Baghdad/Al-Muthanna wage cases at 4 assumed person-hours per m³ concrete and 8 per tonne reinforcement. The 2025 column uses the same hours with the CSO skilled-wage sensitivity and annual governorate material rates. Those vintages differ in geographic aggregation and must not be read as a pure inflation comparison.",
        "",
        "| Body | Drive | Route | Physical candidate | Accounted tare kg/car | Max required force kN/train | Max required power MW/train | Adverse demand runtime s | Civil screen 2026 IQD m/span | CSO annual 2025 IQD m/span | Complete mass / force map / whole-life cost |",
        "|---|---|---:|---|---:|---:|---:|---:|---:|---:|---|",
    ]
    for candidate in report["candidates"]:
        row = candidate["comparison_row"]
        force = row["propulsion"].get("maximum_required_force_N_train_across_declared_loads")
        power = row["propulsion"].get("maximum_required_power_W_train_across_declared_loads")
        adverse = [scenario for scenario in candidate["journey_scenarios"]
                   if scenario.get("scenario_name") == "adverse-normal"]
        runtime = adverse[0].get("demand_path_runtime_s") if adverse else None
        costs_2026 = [_mid_cost_iqd(candidate, year=2026, region=region)
                      for region in ("Baghdad", "Al-Muthanna")]
        costs_2025 = [_mid_cost_iqd(candidate, year=2025, region=region)
                      for region in ("Baghdad", "Al-Muthanna")]
        min_2026 = min(value[0] for value in costs_2026) / Decimal(1_000_000)
        max_2026 = max(value[1] for value in costs_2026) / Decimal(1_000_000)
        min_2025 = min(value[0] for value in costs_2025) / Decimal(1_000_000)
        max_2025 = max(value[1] for value in costs_2025) / Decimal(1_000_000)
        lines.append(
            f"| {candidate['body_family']} | {candidate['architecture_family']} | "
            f"{candidate['route_distance_m'] / 1000:g} km | `"
            f"{candidate['identity']['physical_candidate_id'][:12]}` | "
            f"{row['mass']['accounted_tare_kg_per_car']:.1f} | "
            f"{force / 1000:.2f} | {power / 1_000_000:.3f} | "
            f"{runtime:.1f} | {min_2026:.2f}–{max_2026:.2f} | "
            f"{min_2025:.2f}–{max_2025:.2f} | unknown |")
    lines.extend([
        "",
        "The force and power columns are required demand, not available motor output. Adverse runtime is from the analytical demand path only. All body, brake, thermal, foundation and propulsion models retain their source limitations in the machine-readable row.",
        "",
        "## Scope and evidence",
        "",
        "Each machine-readable candidate row preserves the original closure comparison row, all four load cases, the candidate's BOM and manufacturing coverage, economics, risks, outstanding evidence, and three exact civil alternatives with their complete regional and labour-hour sensitivity details. Every civil row is bound to candidate, bundle, physical civil component and alternative IDs.",
        "",
        "The September 2026 model applies the generic Iraqi material rates and base-wage recipes. The 2025 cross-check uses the CSO's annual governorate material averages and six separate wage-category sensitivities. An 8-hour day converts published daily wages to assumed hourly base wages. Neither source provides validated factory charge-out rates, crew mix, production yield, tooling, QC, overhead, or a supplier quote. The 20% uplift is unallocated and applied once to the screen's direct material plus assumed labour.",
        "",
        "The displayed cost is not a precast beam price, an installed span price or a route CAPEX estimate. Prestress, anchorage, rails, fasteners, moulds, factory utilities, QA, scrap, transport, cranes, foundations, erection, taxes and maintenance remain outside this screen. The CSO annual series and September 2026 national rates use different periods and geographic aggregation.",
        "",
        "## Reproduction and verification",
        "",
        "```sh",
        "./osr source report candidate-comparison --output docs/design-engine/railway-comparison-2026-10",
        "./osr source report candidate-comparison --output docs/design-engine/railway-comparison-2026-10 --check",
        "```",
        "",
        "[Candidate comparison JSON](candidate-comparison.json) · [Publication manifest](manifest.json) · [source closure dossier](../railway-closure/README.md) · [Iraqi civil rate and fabrication dossier](../sourcing/README.md)",
        "",
    ])
    return "\n".join(lines)


def _source_paths(root):
    return (
        Path("engineering/sourcing/comparative_report.py"),
        Path("engineering/sourcing/closure_civil_cost.py"),
        Path("engineering/sourcing/cli.py"),
        Path("engineering/sourcing/model.py"),
        Path("engineering/station_rail/common.py"),
        Path("docs/design-engine/railway-closure/manifest.json"),
        Path("docs/design-engine/railway-closure/cases.json.gz"),
        Path("docs/design-engine/railway-closure/comparison.json"),
        CIVIL_OUTPUT_DIR / "manifest.json",
        CIVIL_OUTPUT_DIR / "candidate-span-cost-screen.json",
    )


def _write(path, content):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".pending")
    temporary.write_bytes(content)
    temporary.replace(path)


def publish_packet(root=REPOSITORY_ROOT, output=None):
    root = Path(root).resolve()
    target = root / OUTPUT_DIR if output is None else Path(output).expanduser().resolve()
    if target.is_symlink():
        raise ValueError("Comparative report output must not be a symlink")
    if target.exists() and any(target.iterdir()):
        prior = target / MANIFEST_FILE
        if not prior.is_file():
            raise ValueError("Existing comparative report output is not an owned publication")
        old = json.loads(prior.read_bytes())
        if (old.get("schema") != "osr-candidate-comparative-closure-publication/1"
                or old.get("publication_id") != identity({
                    key: value for key, value in old.items() if key != "publication_id"})):
            raise ValueError("Existing comparative report publication identity differs")
    report = build_report(root)
    report_bytes = encoded(report)
    readme = render_readme(report).encode("utf-8")
    manifest = {
        "schema": "osr-candidate-comparative-closure-publication/1",
        "report_id": report["report_id"],
        "sources": {path.as_posix(): digest(root / path) for path in _source_paths(root)},
        "files": {
            README_FILE: sha256(readme).hexdigest(),
            REPORT_FILE: sha256(report_bytes).hexdigest(),
        },
        "unknown_is_zero": False,
        "complete_installed_cost_USD": None,
        "complete_installed_cost_IQD": None,
        "whole_life_cost": None,
        "selection": None,
        "engineering_accepted": False,
        "physical_accepted": False,
    }
    manifest["publication_id"] = identity(manifest)
    _write(target / README_FILE, readme)
    _write(target / REPORT_FILE, report_bytes)
    _write(target / MANIFEST_FILE, encoded(manifest))
    return verify_packet(target, root=root)


def verify_packet(output=None, *, root=REPOSITORY_ROOT):
    root = Path(root).resolve()
    target = root / OUTPUT_DIR if output is None else Path(output).expanduser().resolve()
    manifest = json.loads((target / MANIFEST_FILE).read_bytes())
    if (manifest.get("schema") != "osr-candidate-comparative-closure-publication/1"
            or manifest.get("publication_id") != identity({
                key: value for key, value in manifest.items() if key != "publication_id"})):
        raise ValueError("Comparative report publication identity differs")
    expected_sources = {path.as_posix(): digest(root / path) for path in _source_paths(root)}
    if manifest.get("sources") != expected_sources:
        raise ValueError("Comparative report source epoch differs")
    expected_report = build_report(root)
    if json.loads((target / REPORT_FILE).read_bytes()) != expected_report:
        raise ValueError("Candidate comparison report does not reproduce")
    if (target / README_FILE).read_text() != render_readme(expected_report):
        raise ValueError("Candidate comparison README does not reproduce")
    if manifest.get("files") != {
            name: digest(target / name) for name in (README_FILE, REPORT_FILE)}:
        raise ValueError("Comparative report output hashes differ")
    if (manifest.get("unknown_is_zero") is not False
            or manifest.get("selection") is not None
            or manifest.get("physical_accepted") is not False
            or manifest.get("engineering_accepted") is not False
            or any(manifest.get(key) is not None for key in
                   ("complete_installed_cost_USD", "complete_installed_cost_IQD", "whole_life_cost"))):
        raise ValueError("Comparative packet cannot select or physically accept a design")
    return {
        "verified": True,
        "publication_id": manifest["publication_id"],
        "report_id": expected_report["report_id"],
        "candidate_count": expected_report["candidate_count"],
        "civil_alternative_count": expected_report["civil_alternative_count"],
        "selection": None,
        "complete_installed_cost_USD": None,
        "complete_installed_cost_IQD": None,
        "whole_life_cost": None,
        "physical_accepted": False,
    }
