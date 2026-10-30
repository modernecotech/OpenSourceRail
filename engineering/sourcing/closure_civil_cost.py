"""Candidate-bound partial Iraqi civil-material fabrication cost screens.

The screen prices only the declared concrete ingredient recipe and the separate
reinforcement allowance.  It deliberately leaves prestress, anchors, rails,
fasteners, foundations, moulds, QA, transport, erection and installed cost open.
"""
from decimal import Decimal, InvalidOperation
from hashlib import sha256
import gzip
import json
from pathlib import Path

from engineering.station_rail import ROOT as REPOSITORY_ROOT
from engineering.station_rail.common import digest, encoded, identity
from engineering.sourcing.model import identity as sourcing_identity


REFERENCE_DIR = Path(
    "docs/design-engine/sourcing/domestic-fabrication/"
    "regional-estimates-2026-september-v6"
)
REFERENCE_FILE = "iraq-domestic-cost-reference-2026-09.json"
MANIFEST_FILE = "manifest.json"
OUTPUT_DIR = REFERENCE_DIR / "candidate-span-cost-screen-2026-10"
CLOSURE_DIR = Path("docs/design-engine/railway-closure")
REGIONS = ("Baghdad", "Al-Muthanna")
CONCRETE_HOURS = ("2", "4", "8")
REBAR_HOURS = ("4", "8", "16")
UPLIFT = Decimal("0.20")


def _decimal(value, field):
    try:
        result = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError) as exc:
        raise ValueError(f"Invalid {field}: {value!r}") from exc
    if not result.is_finite() or result < 0:
        raise ValueError(f"Invalid nonnegative {field}: {value!r}")
    return result


def _engineering_quantity(value, field):
    """Discard insignificant binary-float tails while preserving 12 digits."""
    parsed = _decimal(value, field)
    return Decimal(format(float(parsed), ".12g"))


def _text(value):
    return format(value, "f")


def load_reference(root):
    """Load the published rate recipe only after checking its manifest hashes."""
    directory = Path(root) / REFERENCE_DIR
    manifest = json.loads((directory / MANIFEST_FILE).read_bytes())
    for relative, expected_hash in manifest.get("file_sha256", {}).items():
        evidence_path = directory / relative
        if (not evidence_path.is_file()
                or sha256(evidence_path.read_bytes()).hexdigest() != expected_hash):
            raise ValueError("Regional civil-cost source packet fails manifest SHA-256: " + relative)
    packet_path = directory / REFERENCE_FILE
    if manifest.get("manifest_id") != sourcing_identity(
            {key: val for key, val in manifest.items() if key != "manifest_id"}):
        raise ValueError("Regional civil-cost manifest identity differs")
    packet = json.loads(packet_path.read_bytes())
    if (packet.get("schema") != "osr-iraq-domestic-cost-reference/2"
            or packet.get("packet_id") != manifest.get("packet_id")
            or packet.get("packet_id") != sourcing_identity(
                {key: val for key, val in packet.items() if key != "packet_id"})
            or packet.get("unknown_is_zero") is not False
            or packet.get("complete_installed_cost") is not None
            or manifest.get("source_is_supplier_quote") is not False
            or packet.get("candidate_takeoff_mapped_for_unit_rate_estimates") is not False):
        raise ValueError("Regional civil-cost source is not the expected research reference")
    return packet


def _rate_recipes(reference):
    selected = {}
    for row in reference.get("unit_rate_estimates", []):
        if row.get("region") not in REGIONS or row.get("family") not in (
                "concrete batching", "rebar cut/bend"):
            continue
        process = row.get("process", {})
        if (process.get("candidate_takeoff_mapped") is not False
                or process.get("uplift_fraction") != "0.2"
                or process.get("currency") != "IQD"):
            raise ValueError("Expected generic, non-takeoff-mapped unit-rate recipes")
        if row["family"] == "concrete batching":
            concrete_recipe = [
                (line.get("material_key"), line.get("quantity"), line.get("quantity_unit"))
                for line in process.get("material_lines", [])
            ]
            if concrete_recipe != [
                    ("Ordinary Iraqi-origin cement", "0.35", "t"),
                    ("Iraqi-origin red sand", "0.5", "m3"),
                    ("Iraqi-origin crushed gravel", "0.8", "m3")]:
                raise ValueError("Concrete material recipe differs from the declared cost-screen scope")
        elif row["family"] == "rebar cut/bend":
            rebar_recipe = process.get("material_lines", [])
            if (len(rebar_recipe) != 1
                    or rebar_recipe[0].get("material_key") !=
                    "Iraqi-origin 2026-09 CSO reinforcing-bar statistic; grade/diameter unresolved"
                    or rebar_recipe[0].get("quantity") != "1"
                    or rebar_recipe[0].get("quantity_unit") != "t"):
                raise ValueError("Reinforcement recipe differs from the declared cost-screen scope")
        key = (row["region"], row["family"], str(row["labour_hours_per_output"]))
        if key in selected:
            raise ValueError("Duplicate regional cost recipe: " + repr(key))
        selected[key] = (row, process)
    expected = {
        *((region, "concrete batching", hours) for region in REGIONS for hours in CONCRETE_HOURS),
        *((region, "rebar cut/bend", hours) for region in REGIONS for hours in REBAR_HOURS),
    }
    if set(selected) != expected:
        raise ValueError("Regional source packet does not cover the exact costing scenarios")
    return selected


def _material_lines(process, quantity, *, field):
    output = []
    for line in process.get("material_lines", []):
        per_output = _decimal(line.get("quantity"), field + " recipe quantity")
        rate = _decimal(line.get("unit_rate"), field + " source rate")
        source_unit = line.get("quantity_unit")
        if not line.get("benchmark_id") or line.get("currency") != "IQD":
            raise ValueError("Material recipe lacks IQD source evidence")
        extended_quantity = quantity * per_output
        extended_cost = extended_quantity * rate
        output.append({
            "material_key": line.get("material_key"),
            "quantity_per_output": _text(per_output),
            "quantity_unit": source_unit,
            "extended_quantity": _text(extended_quantity),
            "unit_rate_iqd": _text(rate),
            "extended_material_cost_iqd": _text(extended_cost),
            "benchmark_id": line["benchmark_id"],
            "source_ids": process.get("source_ids", []),
            "evidence_scope": line.get("evidence_scope"),
        })
    return output


def _labour_case(process, hours, output_quantity, expected_unit):
    lines = process.get("labour_lines", [])
    if len(lines) != 1:
        raise ValueError("Cost recipe must contain one explicit base-wage line")
    line = lines[0]
    rate = _decimal(line.get("unit_rate"), "wage benchmark")
    if (line.get("quantity_unit") != "h" or line.get("currency") != "IQD"
            or not line.get("benchmark_id")):
        raise ValueError("Labour recipe lacks an hourly IQD benchmark")
    person_hours = output_quantity * hours
    direct_labor = person_hours * rate
    return {
        "assumed_labour_hours_per_output": _text(hours),
        "output_unit": expected_unit,
        "labour_hours": _text(person_hours),
        "wage_rate_iqd_per_person_hour": _text(rate),
        "direct_labour_cost_iqd": _text(direct_labor),
        "wage_benchmark_id": line["benchmark_id"],
        "wage_basis": line.get("wage_basis"),
        "evidence_scope": line.get("evidence_scope"),
    }


def evaluate_alternative(alternative, context, reference):
    """Apply common source rates to one exact current railway civil alternative."""
    required_context = (
        "candidate_id", "bundle_id", "body_candidate_id", "architecture_family",
        "route_distance_m", "requirement_revision",
    )
    if any(not context.get(key) for key in required_context):
        raise ValueError("Candidate civil estimate requires complete physical/evaluation identity")
    for key in ("alternative_id", "physical_civil_component_id", "concrete_m3", "reinforcement_kg"):
        if alternative.get(key) is None:
            raise ValueError("Civil alternative missing cost-scope input: " + key)
    rates = _rate_recipes(reference)
    concrete_quantity = _engineering_quantity(alternative["concrete_m3"], "concrete m3")
    reinforcement_kg = _engineering_quantity(alternative["reinforcement_kg"], "reinforcement kg")
    if concrete_quantity <= 0 or reinforcement_kg <= 0:
        raise ValueError("Civil screen requires positive concrete and reinforcement quantities")
    reinforcement_t = reinforcement_kg / Decimal(1000)
    region_cases = []
    used_source_ids = sorted({
        source_id
        for (region, family, _), (_, process) in rates.items()
        if region in REGIONS and family in ("concrete batching", "rebar cut/bend")
        for source_id in process.get("source_ids", [])
    })
    for region in REGIONS:
        concrete_inputs = []
        rebar_inputs = []
        concrete_labor_cases = {}
        rebar_labor_cases = {}
        for hours in CONCRETE_HOURS:
            row, process = rates[(region, "concrete batching", hours)]
            if (process.get("output_quantity") != "1" or process.get("output_unit") != "m3"
                    or [line.get("quantity_unit") for line in process.get("material_lines", [])]
                    != ["t", "m3", "m3"]):
                raise ValueError("Concrete recipe output or ingredient scope changed")
            lines = _material_lines(process, concrete_quantity, field="concrete")
            if concrete_inputs and lines != concrete_inputs:
                raise ValueError("Concrete recipe material quantities/rates vary by labour case")
            concrete_inputs = lines
            concrete_labor_cases[hours] = _labour_case(process, Decimal(hours), concrete_quantity, "m3")
        for hours in REBAR_HOURS:
            row, process = rates[(region, "rebar cut/bend", hours)]
            if (process.get("output_quantity") != "1" or process.get("output_unit") != "t"
                    or [line.get("quantity_unit") for line in process.get("material_lines", [])]
                    != ["t"]):
                raise ValueError("Reinforcing-bar recipe output or material scope changed")
            lines = _material_lines(process, reinforcement_t, field="reinforcement")
            if rebar_inputs and lines != rebar_inputs:
                raise ValueError("Rebar material rate varies by labour case")
            rebar_inputs = lines
            rebar_labor_cases[hours] = _labour_case(process, Decimal(hours), reinforcement_t, "t")

        concrete_material = sum(
            (_decimal(line["extended_material_cost_iqd"], "concrete material extension")
             for line in concrete_inputs), Decimal(0))
        rebar_material = sum(
            (_decimal(line["extended_material_cost_iqd"], "rebar material extension")
             for line in rebar_inputs), Decimal(0))
        paired_scenarios = []
        for concrete_hours in CONCRETE_HOURS:
            for rebar_hours in REBAR_HOURS:
                concrete_labour = _decimal(
                    concrete_labor_cases[concrete_hours]["direct_labour_cost_iqd"], "concrete labour")
                rebar_labour = _decimal(
                    rebar_labor_cases[rebar_hours]["direct_labour_cost_iqd"], "rebar labour")
                direct_material = concrete_material + rebar_material
                direct_labor = concrete_labour + rebar_labour
                direct = direct_material + direct_labor
                uplift = direct * UPLIFT
                paired_scenarios.append({
                    "concrete_labour_hours_per_m3": concrete_hours,
                    "reinforcement_cut_bend_hours_per_t": rebar_hours,
                    "direct_material_cost_iqd": _text(direct_material),
                    "direct_labour_cost_iqd": _text(direct_labor),
                    "uplift_fraction": _text(UPLIFT),
                    "unallocated_uplift_iqd": _text(uplift),
                    "partial_material_labour_plus_20pct_iqd": _text(direct + uplift),
                    "complete_process_cost_iqd": None,
                    "installed_cost_iqd": None,
                    "whole_life_cost_iqd": None,
                })
        region_cases.append({
            "region": region,
            "currency": "IQD",
            "concrete_quantity_m3": _text(concrete_quantity),
            "concrete_material_takeoff": concrete_inputs,
            "concrete_direct_material_cost_iqd": _text(concrete_material),
            "concrete_labour_scenarios": [concrete_labor_cases[h] for h in CONCRETE_HOURS],
            "reinforcement_modeled_mass_kg": _text(reinforcement_kg),
            "reinforcement_mass_proxy_t": _text(reinforcement_t),
            "reinforcement_purchase_order_quantity_t": None,
            "reinforcement_quantity_basis": alternative.get("reinforcement_basis"),
            "reinforcement_material_takeoff": rebar_inputs,
            "reinforcement_direct_material_cost_iqd": _text(rebar_material),
            "reinforcement_labour_scenarios": [rebar_labor_cases[h] for h in REBAR_HOURS],
            "combined_assumed_labour_scenarios": paired_scenarios,
        })

    result = {
        "schema": "osr-candidate-civil-material-labour-screen/1",
        **{key: context[key] for key in required_context},
        "physical_civil_component_id": alternative["physical_civil_component_id"],
        "alternative_id": alternative["alternative_id"],
        "source_reference_packet_id": reference["packet_id"],
        "source_reference_file": (REFERENCE_DIR / REFERENCE_FILE).as_posix(),
        "source_rate_types": ["official statistical material rates", "official statistical base-wage rates"],
        "rate_source_ids": used_source_ids,
        "source_rate_scope": "Only generic, non-candidate-takeoff-mapped unit-rate recipes were reused; source candidate-specific cost results were not transferred. Current candidate civil quantities are recalculated below.",
        "source_candidate_result_reused": False,
        "regional_comparison_basis": "Material observations are national CSO market rates; Baghdad and Al-Muthanna vary the governorate base-wage input only. Neither region is selected as route or factory location.",
        "cost_scope": ["nominal concrete recipe ingredients", "declared reinforcement mass allowance"],
        "concrete_material_recipe_basis": "0.35 t cement + 0.50 m3 red sand + 0.80 m3 crushed gravel per nominal m3; illustrative unqualified recipe",
        "concrete_quantity_m3": _text(concrete_quantity),
        "reinforcement_modeled_mass_kg": _text(reinforcement_kg),
        "reinforcement_purchase_order_quantity_t": None,
        "reinforcement_basis": alternative.get("reinforcement_basis"),
        "unpriced_civil_quantities": {
            "prestress_kg": alternative.get("prestress_kg"),
            "prestress_anchorage_kg": alternative.get("prestress_anchorage_kg"),
            "running_rail_kg": alternative.get("running_rail_kg"),
            "direct_fastener_kg": alternative.get("direct_fastener_kg"),
            "foundation_actual_quantity": None,
        },
        "regions": region_cases,
        "exclusions": [
            "reinforcement grade, detailed bar schedule, wastage, yield and purchase order quantity",
            "prestressing strand, tensioning, anchorage and installation labour",
            "rails, fasteners, ducts, inserts and embedded steel",
            "concrete mix design, admixtures, curing, moulds, formwork and reusable tooling",
            "factory equipment, utilities, depreciation, QA, inspection, packaging and rework",
            "transport, lifting, foundations, erection, field installation and site works",
            "taxes, duties, employer labour burden, overhead validation, warranty and maintenance",
        ],
        "formula": "(candidate quantity x source material rates + assumed person-hours x source base wage) x 1.20",
        "uplift_fraction": _text(UPLIFT),
        "uplift_scope": "Unallocated planning uplift applied once to this screen's direct concrete/reinforcement materials plus assumed base-wage labour; not a validated shop rate, overhead, profit, tax or contingency.",
        "candidate_quantities_mapped": True,
        "supplier_quote": False,
        "complete_process_cost_iqd": None,
        "installed_cost_iqd": None,
        "whole_life_cost_iqd": None,
        "engineering_accepted": False,
        "procurement_approved": False,
        "physical_accepted": False,
        "unknown_is_zero": False,
    }
    result["estimate_id"] = identity(result)
    return result


def _load_closure(root):
    directory = Path(root) / CLOSURE_DIR
    manifest = json.loads((directory / "manifest.json").read_bytes())
    if manifest.get("publication_id") != identity(
            {key: value for key, value in manifest.items() if key != "publication_id"}):
        raise ValueError("Current railway-closure publication identity differs")
    expected_files = {
        "README.md", "summary.json", "comparison.json", "source-epochs.json",
        "cases.json.gz", "equipped.json.gz", "required-tests.json.gz",
    }
    if (set(manifest.get("files", {})) != expected_files
            or manifest.get("physical_accepted") is not False
            or manifest.get("engineering_accepted") is not False):
        raise ValueError("Current railway-closure publication scope or file inventory differs")
    for name, expected_hash in manifest.get("files", {}).items():
        path = directory / name
        if not path.is_file() or digest(path) != expected_hash:
            raise ValueError("Current railway-closure source payload differs: " + name)
    cases = json.loads(gzip.decompress((directory / "cases.json.gz").read_bytes()))
    comparison = json.loads((directory / "comparison.json").read_bytes())
    if (cases.get("evaluation_id") != manifest.get("evaluation_id")
            or cases.get("evaluation_id") != identity({
                key: value for key, value in cases.items()
                if key not in ("evaluation_id", "new_bundles", "reused_bundles")})
            or comparison.get("closure_evaluation_id") != cases.get("evaluation_id")
            or comparison.get("schema") != "osr-candidate-journey-comparison/1"
            or comparison.get("evaluated_bundle_count") != 12
            or comparison.get("pending_bundle_count") != 0
            or comparison.get("comparison_id") != identity({
                key: value for key, value in comparison.items() if key != "comparison_id"})):
        raise ValueError("Current closure evaluation and comparison do not reconcile")
    for row in comparison.get("rows", []):
        if row.get("comparison_row_id") != identity({
                key: value for key, value in row.items() if key != "comparison_row_id"}):
            raise ValueError("Current closure comparison row identity differs")
    return manifest, cases, comparison


def build_packet(root=REPOSITORY_ROOT):
    """Map source rates to the latest exact closure cases and retain identities."""
    root = Path(root)
    source_reference = load_reference(root)
    closure_manifest, closure, comparison = _load_closure(root)
    comparison_by_bundle = {row["bundle_id"]: row for row in comparison.get("rows", [])}
    if len(comparison_by_bundle) != len(comparison.get("rows", [])):
        raise ValueError("Closure comparison contains duplicate bundle identities")
    entries = []
    seen = set()
    for case in closure.get("rows", []):
        if case.get("record_id") != identity({key: value for key, value in case.items()
                                               if key != "record_id"}):
            raise ValueError("Closure case record identity differs")
        bundle, output = case["bundle"], case["output"]
        if (bundle.get("candidate_id") != output.get("candidate_id")
                or bundle.get("bundle_id") != comparison_by_bundle.get(bundle.get("bundle_id"), {}).get("bundle_id")
                or output.get("candidate_id") != comparison_by_bundle.get(bundle.get("bundle_id"), {}).get("candidate_id")
                or output.get("body_candidate_id") != bundle.get("body_candidate_id")):
            raise ValueError("Civil-cost screen cannot bind mixed closure candidate identities")
        comparison_options = {
            row.get("alternative_id"): (row.get("physical_civil_component_id"), row.get("concrete_m3"))
            for row in comparison_by_bundle[bundle["bundle_id"]].get("civil_alternatives", [])
        }
        case_options = {
            row.get("alternative_id"): (row.get("physical_civil_component_id"), row.get("concrete_m3"))
            for row in output.get("civil", {}).get("alternatives", [])
        }
        if not case_options or case_options != comparison_options:
            raise ValueError("Civil quantities do not reconcile to the published candidate comparison")
        context = {
            "candidate_id": bundle["candidate_id"],
            "bundle_id": bundle["bundle_id"],
            "body_candidate_id": bundle["body_candidate_id"],
            "architecture_family": bundle.get("family_id") or bundle.get("architecture_case", {}).get("family_id"),
            "route_distance_m": output.get("distance_m"),
            "requirement_revision": bundle.get("requirement_revision"),
        }
        for alternative in output.get("civil", {}).get("alternatives", []):
            key = (bundle["bundle_id"], alternative.get("alternative_id"))
            if key in seen:
                raise ValueError("Duplicate civil alternative under one physical bundle")
            seen.add(key)
            screen = evaluate_alternative(alternative, context, source_reference)
            row = {
                **context,
                "body_family": comparison_by_bundle[bundle["bundle_id"]]["body_family"],
                "closure_evaluation_id": closure["evaluation_id"],
                "closure_case_record_id": case["record_id"],
                "civil_alternative": {
                    "physical_civil_component_id": alternative["physical_civil_component_id"],
                    "alternative_id": alternative["alternative_id"],
                    "family": alternative.get("family"),
                    "span_m": alternative.get("span_m"),
                    "concrete_m3": alternative.get("concrete_m3"),
                    "reinforcement_kg": alternative.get("reinforcement_kg"),
                    "reinforcement_basis": alternative.get("reinforcement_basis"),
                    "prestress_kg": alternative.get("prestress_kg"),
                    "prestress_anchorage_kg": alternative.get("prestress_anchorage_kg"),
                    "running_rail_kg": alternative.get("running_rail_kg"),
                    "direct_fastener_kg": alternative.get("direct_fastener_kg"),
                    "engineering_screen": alternative.get("engineering_screen"),
                    "torsion_and_unequal_rail_loading_qualified": alternative.get(
                        "torsion_and_unequal_rail_loading_qualified"),
                    "installed_mass_complete": alternative.get("installed_mass_complete"),
                },
                "cost_screen": screen,
            }
            row["row_id"] = identity(row)
            entries.append(row)
    if len(closure.get("rows", [])) != 12 or len(entries) != 36:
        raise ValueError("Expected the full 12-bundle, 36-alternative closure cost matrix")
    entries.sort(key=lambda row: (row["body_family"], row["architecture_family"],
                                  row["route_distance_m"], row["candidate_id"],
                                  row["civil_alternative"]["family"]))
    packet = {
        "schema": "osr-candidate-bound-domestic-civil-cost-screen/1",
        "closure_evaluation_id": closure["evaluation_id"],
        "closure_publication_id": closure_manifest["publication_id"],
        "comparison_id": comparison["comparison_id"],
        "regional_cost_reference_packet_id": source_reference["packet_id"],
        "bundle_count": len(closure["rows"]),
        "civil_alternative_count": len(entries),
        "rows": entries,
        "cost_scope": "per-span partial raw-material and assumed direct base-wage labour sensitivity",
        "unknown_is_zero": False,
        "complete_precaster_cost_iqd": None,
        "installed_civil_cost_iqd": None,
        "whole_life_cost_iqd": None,
        "engineering_accepted": False,
        "procurement_approved": False,
        "physical_accepted": False,
    }
    packet["packet_id"] = identity(packet)
    return packet


def _base_case(region):
    return next(row for row in region["combined_assumed_labour_scenarios"]
                if row["concrete_labour_hours_per_m3"] == "4"
                and row["reinforcement_cut_bend_hours_per_t"] == "8")


def render_readme(packet):
    lines = [
        "# Candidate-bound Iraqi civil material + labour screen — October 2026",
        "",
        f"This packet applies the September 2026 regional cost-reference recipes to {packet['civil_alternative_count']} exact span alternatives in {packet['bundle_count']} candidate bundles. Every row retains physical candidate, body, bundle, evaluation and civil-alternative identities. The cost estimate is partial and is not a supplier quote, approved procurement price, complete precast price or installed cost.",
        "",
        "## Scope and estimate method",
        "",
        "The screen prices the nominal concrete ingredient recipe (0.35 t cement, 0.50 m³ red sand and 0.80 m³ crushed gravel per nominal m³) and the separate preliminary reinforcement mass allowance. For each exact civil alternative, the formula is `(source-priced material quantities + assumed person-hours × regional CSO skilled base wage) × 1.20`. The 20% is unallocated and applied once to combined direct materials plus base-wage labour.",
        "",
        "Material observations are national Iraqi-origin CSO statistics. Baghdad and Al-Muthanna change the governorate wage input only; neither location is a selected factory or route site. Labour hours are planning assumptions (2/4/8 h per nominal m³ concrete and 4/8/16 h per tonne rebar), not timed manufacturing routes or employer-loaded shop rates. The displayed middle-hour row uses 4 h/m³ and 8 h/t; the data packet retains all nine paired hour cases for both wage regions.",
        "",
        "| Body | Drive | Route | Candidate | Civil option | Span m | Concrete m³ | Reinforcement allowance kg | Baghdad IQD million/span | Al-Muthanna IQD million/span |",
        "|---|---|---:|---|---|---:|---:|---:|---:|---:|",
    ]
    for row in packet["rows"]:
        region_costs = {region["region"]: float(_base_case(region)[
            "partial_material_labour_plus_20pct_iqd"]) / 1_000_000
                        for region in row["cost_screen"]["regions"]}
        alternative = row["civil_alternative"]
        lines.append(
            "| {body} | {drive} | {route:g} km | `{candidate}` | {option} (`{alternative}`) | {span:g} | {concrete:.4f} | {rebar:.1f} | {baghdad:.3f} | {muthanna:.3f} |".format(
                body=row["body_family"], drive=row["architecture_family"],
                route=row["route_distance_m"] / 1000, candidate=row["candidate_id"][:12],
                option=alternative["family"], alternative=alternative["alternative_id"][:10],
                span=alternative["span_m"], concrete=alternative["concrete_m3"],
                rebar=alternative["reinforcement_kg"], baghdad=region_costs["Baghdad"],
                muthanna=region_costs["Al-Muthanna"]))
    lines += [
        "",
        "The scenario values are raw material plus assumed direct base-wage labour with an unallocated 20% uplift. The CSO source prices do not establish exact grade, seller, availability, delivery or an order quantity. Reinforcement mass uses the preliminary civil model’s declared 120 kg/m³ allowance; detailed bar schedules, cutting yield and purchase quantities are unknown.",
        "",
        "Prestressing strand and installation, anchorage, rail, fasteners, concrete mix validation, formwork, moulds, factory plant/utilities, QA, scrap/yield, transport, crane/lifting, foundations, erection, employer burden, taxes, maintenance and warranty are excluded. These unknowns are not zero. No total network CAPEX is inferred from per-span quantities.",
        "",
        "The rate basis and source hashes are retained in the [September 2026 regional reference](../regional-estimates-2026-september-v6/README.md). Candidate identities and civil quantities come from the [current 1.5/2 km closure packet](../../../railway-closure/README.md). Full IDs, line-item calculations, source benchmark IDs and paired sensitivities are in [candidate-span-cost-screen.json](candidate-span-cost-screen.json).",
        "",
        "Complete process, installed civil and whole-life costs remain unknown. Engineering, procurement and physical acceptance remain false.",
        "",
    ]
    return "\n".join(lines)


def _source_paths(root):
    root = Path(root)
    return (
        Path(__file__).resolve().relative_to(root.resolve()),
        Path("engineering/sourcing/cli.py"),
        Path("engineering/sourcing/model.py"),
        Path("engineering/station_rail/common.py"),
        CLOSURE_DIR / "manifest.json",
        CLOSURE_DIR / "cases.json.gz",
        CLOSURE_DIR / "comparison.json",
        REFERENCE_DIR / REFERENCE_FILE,
        REFERENCE_DIR / MANIFEST_FILE,
    )


def _write(path, payload):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".pending")
    temporary.write_bytes(payload)
    temporary.replace(path)


def publish_packet(root=REPOSITORY_ROOT, output=None):
    root = Path(root).resolve()
    target = (root / OUTPUT_DIR if output is None else Path(output).expanduser().resolve())
    if target.is_symlink():
        raise ValueError("Civil cost report output must not be a symlink")
    if target.exists() and any(target.iterdir()):
        old_manifest_path = target / "manifest.json"
        if not old_manifest_path.is_file():
            raise ValueError("Existing cost-screen output is not an owned publication")
        old_manifest = json.loads(old_manifest_path.read_bytes())
        if (old_manifest.get("schema") != "osr-candidate-bound-domestic-civil-cost-publication/1"
                or old_manifest.get("publication_id") != identity({
                    key: value for key, value in old_manifest.items() if key != "publication_id"})):
            raise ValueError("Existing cost-screen output has an invalid publication identity")
    packet = build_packet(root)
    readme = render_readme(packet)
    packet_payload = encoded(packet)
    report = {
        "schema": "osr-candidate-bound-domestic-civil-cost-publication/1",
        "packet_id": packet["packet_id"],
        "sources": {path.as_posix(): digest(root / path) for path in _source_paths(root)},
        "files": {
            "README.md": sha256(readme.encode("utf-8")).hexdigest(),
            "candidate-span-cost-screen.json": sha256(packet_payload).hexdigest(),
        },
        "unknown_is_zero": False,
        "complete_precaster_cost_iqd": None,
        "installed_civil_cost_iqd": None,
        "whole_life_cost_iqd": None,
        "engineering_accepted": False,
        "procurement_approved": False,
        "physical_accepted": False,
    }
    report["publication_id"] = identity(report)
    _write(target / "README.md", readme.encode("utf-8"))
    _write(target / "candidate-span-cost-screen.json", packet_payload)
    _write(target / "manifest.json", encoded(report))
    return verify_packet(target, root=root)


def verify_packet(output=None, *, root=REPOSITORY_ROOT):
    root = Path(root).resolve()
    target = (root / OUTPUT_DIR if output is None else Path(output).expanduser().resolve())
    manifest = json.loads((target / "manifest.json").read_bytes())
    if (manifest.get("schema") != "osr-candidate-bound-domestic-civil-cost-publication/1"
            or manifest.get("publication_id") != identity({
                key: value for key, value in manifest.items() if key != "publication_id"})):
        raise ValueError("Civil cost publication identity differs")
    if manifest.get("sources") != {path.as_posix(): digest(root / path) for path in _source_paths(root)}:
        raise ValueError("Civil cost source epoch differs")
    expected_packet = build_packet(root)
    if json.loads((target / "candidate-span-cost-screen.json").read_bytes()) != expected_packet:
        raise ValueError("Candidate civil-cost packet does not reproduce")
    if (target / "README.md").read_text() != render_readme(expected_packet):
        raise ValueError("Candidate civil-cost README does not reproduce")
    if manifest.get("files") != {
            name: digest(target / name) for name in ("README.md", "candidate-span-cost-screen.json")}:
        raise ValueError("Candidate civil-cost output hashes differ")
    if (manifest.get("unknown_is_zero") is not False
            or any(manifest.get(key) is not False for key in
                   ("engineering_accepted", "procurement_approved", "physical_accepted"))):
        raise ValueError("Civil screen cannot approve the railway")
    return {
        "verified": True,
        "publication_id": manifest["publication_id"],
        "packet_id": expected_packet["packet_id"],
        "bundle_count": expected_packet["bundle_count"],
        "civil_alternative_count": expected_packet["civil_alternative_count"],
        "complete_precaster_cost_iqd": None,
        "installed_civil_cost_iqd": None,
        "whole_life_cost_iqd": None,
        "physical_accepted": False,
    }
