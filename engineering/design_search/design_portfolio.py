"""Reproducible breadth-first shape portfolio with provisional stock costing."""
from copy import deepcopy
import gzip
import json
from pathlib import Path
import shutil
import tomllib

from engineering.station_rail import ROOT
from engineering.station_rail.common import encoded, identity, digest
from . import design_grammar, grammar_geometry, interface_graph, dfma, model_cost
from . import shape_families, quality_diversity

OUTPUT = "docs/design-engine/breadth-first-shape-portfolio"
PRODUCER = "engineering/design_search/design_portfolio.py"
OBJECTIVES = (
    "known_gross_structure_stock_kg",
    "factory_gate_body_stock_base_iqd_per_car",
    "factory_process_hours_base_per_car",
    "manufacturing_occurrences",
)
FLAGS = dict(physical_accepted=False, engineering_accepted=False,
    configuration_adopted=False, manufacturing_release=False, operating_release=False)


def specification(root=ROOT):
    root = Path(root)
    spec = shape_families.load(root)
    assumptions = model_cost.assumptions(root)
    configured = spec["production_basis"]
    civil = spec["civil_basis"]
    operations = spec["operations_scenarios"]
    if (configured["shifts_per_day"] != assumptions["production_shifts_per_day"]
            or configured["hours_per_shift"] != assumptions["production_hours_per_shift"]
            or configured["days_per_year"] != assumptions["production_days_per_year"]
            or configured["productive_utilisation"] != assumptions["productive_utilisation"]
            or civil["shifts_per_day"] != assumptions["civil_shifts_per_day"]
            or civil["hours_per_shift"] != assumptions["civil_hours_per_shift"]
            or operations["shifts_per_day"] != assumptions["operations_shifts_per_day_cases"]
            or operations["hours_per_shift"] != assumptions["operations_hours_per_shift_cases"]):
        raise ValueError("Portfolio shift assumptions must match the canonical cost scenario")
    return dict(schema="osr-breadth-first-shape-portfolio-specification/1",
        purpose=spec["purpose"], candidate_budget=spec["maximum_candidates"],
        descriptor_axes=["frame", "shell", "ribs"], objectives=list(OBJECTIVES),
        fidelity="stage-0 geometry, gross-stock, interface and Class C factory-gate screen",
        production_basis=deepcopy(configured), civil_basis=deepcopy(civil),
        operations_scenarios=deepcopy(operations), profiles=deepcopy(spec["profiles"]),
        architecture_axes=deepcopy(spec["design_axes"]),
        reference_changes_allowed=False, native_dispatch=False, integrated_selection=None,
        scope="One 17 m car body envelope per candidate; same six-car formation context. No whole-car installation, vehicle/system cost or structural qualification.",
        unsupported_families=["curved or variable-thickness shells", "cellular/lattice internals",
            "implicit/organic topology", "topology-optimised load paths", "hybrid materials beyond existing frame/shell compositions",
            "multifunctional joints and new propulsion/suspension/civil architectures"], **FLAGS)


def sources(root=ROOT):
    root = Path(root)
    value = shape_families.sources(root)
    value[PRODUCER] = digest(root / PRODUCER)
    return value


def _factory_gate_stock_estimate(candidate, assumptions_record, root):
    """Apply the existing low/base/high Class C body-stock cost equations."""
    a = model_cost._validate_assumptions(assumptions_record, root)
    wage = assumptions_record["benchmark_rates_iqd"]["wage_skilled_iqd_per_h"]
    burden = a["wage_burden_multipliers"]
    second_premium = a["second_shift_wage_premium"]
    shifts = assumptions_record["production_shifts_per_day"]
    production_wage = [model_cost._shift_adjusted_wage(wage * burden[i], shifts,
        second_premium[i], a["third_shift_wage_premium"][i]) for i in range(3)]
    totals = {name: [0.0, 0.0, 0.0] for name in
        ("material", "labour", "equipment", "quality", "factory_overhead")}
    process_hours = [0.0, 0.0, 0.0]
    for part in candidate["parts"]:
        mass = float(part["mass_kg"])
        rates, _ = model_cost._material_rate(a, part.get("material_id"))
        purchased = [mass / a["body_purchase_yield"][i] for i in range(3)]
        material = [purchased[i] * rates[i] for i in range(3)]
        hours = [mass * a["body_process_hours_per_kg"][i]
            + a["body_process_setup_hours_per_stock"][i] for i in range(3)]
        labour = [hours[i] * production_wage[i] for i in range(3)]
        machine_hours = [mass * a["body_machine_hours_per_kg"][i] for i in range(3)]
        equipment = [machine_hours[i] * a["machine_rate_iqd_per_h"][i] for i in range(3)]
        quality = [material[i] * a["body_qa_fraction"][i] for i in range(3)]
        direct = [material[i] + labour[i] + equipment[i] + quality[i] for i in range(3)]
        overhead = [direct[i] * a["factory_overhead_fraction"][i] for i in range(3)]
        for name, values in (("material", material), ("labour", labour),
                ("equipment", equipment), ("quality", quality),
                ("factory_overhead", overhead)):
            totals[name] = [totals[name][i] + values[i] for i in range(3)]
        process_hours = [process_hours[i] + hours[i] for i in range(3)]
    total = [sum(totals[name][i] for name in totals) for i in range(3)]
    return dict(schema="osr-class-c-body-stock-gate-estimate/1",
        candidate_id=candidate["candidate_id"], estimate_class="C",
        rate_evidence_class="C", currency="IQD", unit="one-car nominal body stock",
        scenarios_iqd=dict(zip(model_cost.CASES, [round(x, 2) for x in total])),
        components_iqd={name: dict(zip(model_cost.CASES, [round(x, 2) for x in values]))
            for name, values in totals.items()},
        process_hours=dict(zip(model_cost.CASES, [round(x, 4) for x in process_hours])),
        six_car_body_stock_scenarios_iqd=dict(zip(model_cost.CASES,
            [round(x * candidate["parameters"]["cars"], 2) for x in total])),
        production_shifts_per_day=shifts,
        production_hours_per_shift=assumptions_record["production_hours_per_shift"],
        production_days_per_year=assumptions_record["production_days_per_year"],
        productive_utilisation=assumptions_record["productive_utilisation"],
        second_shift_wage_premium=deepcopy(second_premium),
        assumption_id=assumptions_record["assumption_id"],
        scope="Located nominal body stock factory gate only; excludes joints/fasteners, unlocated equipment, passenger fitout, final vehicle assembly, delivery, installation, tooling investment, civil works, propulsion, maintenance and lifecycle cost.",
        basis="Existing cost-engine equations: gross nominal part mass, bounded purchase yield, material-family rates, process-hours/kg plus setup-hours/stock, loaded skilled wage, machine-hours, QA fraction and factory overhead. These are planning proxies, not supplier prices or measured routings.",
        physical_accepted=False, engineering_accepted=False, manufacturing_release=False)


def _evaluate(candidate, descriptor, profile_id, assumptions_record, root):
    design_grammar.validate(candidate)
    mass = grammar_geometry.mass_properties(candidate)
    dfma_result = dfma.evaluate(candidate, root=root)
    interfaces = interface_graph.assess(grammar_geometry.interface_projection(candidate))
    cost = _factory_gate_stock_estimate(candidate, assumptions_record, root)
    if mass["candidate_id"] != candidate["candidate_id"] or dfma_result["candidate_id"] != candidate["candidate_id"]:
        raise ValueError("Candidate identity differs across shape evaluation")
    if interfaces["candidate_id"] != candidate["candidate_id"]:
        raise ValueError("Candidate identity differs across interface evaluation")
    metrics = dict(known_gross_structure_stock_kg=mass["known_gross_stock_mass_kg"],
        factory_gate_body_stock_base_iqd_per_car=cost["scenarios_iqd"]["base"],
        factory_process_hours_base_per_car=cost["process_hours"]["base"],
        manufacturing_occurrences=dfma_result["declared_manufacturing_occurrences"])
    if metrics["manufacturing_occurrences"] is None:
        raise ValueError("A declared manufacturing-occurrence count is required for the partial archive")
    return dict(candidate_id=candidate["candidate_id"], definition_id=candidate["definition_id"],
        descriptor=deepcopy(descriptor), profile_id=profile_id, metrics=metrics,
        mass_properties=mass, cost_estimate=cost,
        DFMA=dict(evaluation_id=dfma_result["evaluation_id"],
            declared_manufacturing_occurrences=dfma_result["declared_manufacturing_occurrences"],
            assembly_interfaces=dfma_result["assembly_interfaces"],
            known_stock_mass_subtotal_kg=dfma_result["known_stock_mass_subtotal_kg"],
            unknown_fastener_join_count=len(dfma_result["unknown_fastener_join_ids"]),
            complete_installed_mass_kg=dfma_result["complete_installed_mass_kg"],
            complete_installed_cost_USD=dfma_result["complete_installed_cost_USD"],
            labor_scope=deepcopy(dfma_result["labor"])),
        interface_screen=dict(status=interfaces["compatibility_status"],
            declared_functions_preserved=interfaces["declared_functions_preserved"],
            issues=[dict(code=row.get("code"), status=row.get("status")) for row in interfaces["issues"]]),
        fidelity="stage-0 actual nominal geometry, stock mass properties, interface checks and provisional Class C body-stock cost",
        structural_analysis="not-run", curved_or_cellular_geometry="not-generated",
        full_body_evaluator="unavailable-for-these-topologies",
        complete_installed_mass_kg=None, complete_installed_cost_iqd=None,
        integrated_selection=None, **FLAGS)


def _calculate(root=ROOT):
    root = Path(root)
    spec = specification(root)
    source_epoch = sources(root)
    assumptions_record = model_cost.assumptions(root)
    generated = shape_families.generate(root)
    candidates = [row["candidate"] for row in generated]
    evaluations = [_evaluate(row["candidate"], row["descriptor"], row["profile_id"],
        assumptions_record, root) for row in generated]
    archive_rows = [dict(candidate_id=row["candidate_id"], descriptor=row["descriptor"],
        metrics=row["metrics"]) for row in evaluations]
    archive = quality_diversity.archive(archive_rows, OBJECTIVES,
        ("frame", "shell", "ribs"))
    profiles_by_id = {row["id"]: row for row in spec["profiles"]}
    cells = []
    for cell in archive["cells"]:
        members = [row for row in evaluations
            if all(row["descriptor"][key] == cell["descriptor"][key]
                for key in ("frame", "shell", "ribs"))]
        cells.append(dict(cell_id=cell["cell_id"], descriptor=cell["descriptor"],
            candidate_count=len(cell["candidate_ids"]),
            retained_pareto_candidate_ids=cell["retained_pareto_candidate_ids"],
            profiles=[dict(profile_id=row["profile_id"], candidate_id=row["candidate_id"],
                metrics=row["metrics"], retained=row["candidate_id"] in cell["retained_pareto_candidate_ids"])
                for row in sorted(members, key=lambda item: item["profile_id"])],
            excluded=cell["excluded"]))
    result = dict(schema="osr-breadth-first-shape-portfolio/1",
        specification=spec, source_sha256=source_epoch,
        candidate_count=len(candidates), composition_cell_count=len(cells),
        profile_count=len(profiles_by_id), candidate_ids=sorted(c["candidate_id"] for c in candidates),
        evaluations=evaluations, archive=archive, cells=cells,
        assumptions=dict(assumption_id=assumptions_record["assumption_id"],
            source_sha256=model_cost.sources(root), estimate_class="C",
            cost_scope="Nominal body stock factory gate only"),
        integrated_selection=None, selected_candidate_id=None,
        selected_reference_changed=False,
        physical_accepted=False, engineering_accepted=False,
        configuration_adopted=False, manufacturing_release=False, operating_release=False,
        closure=dict(all_candidates_have_geometry=True, all_candidates_have_mass_properties=True,
            all_candidates_have_provisional_body_stock_cost=True,
            installed_mass_complete=False, structural_qualification_complete=False,
            whole_vehicle_cost_complete=False, city_cost_complete=False,
            physical_acceptance_complete=False),
        future_adapters=dict(curved_shells=False, variable_thickness_shells=False,
            cellular_or_lattice_geometry=False, topology_optimisation=False,
            implicit_geometry=False, coupled_vehicle_guideway_shape_search=False))
    if source_epoch != sources(root):
        raise ValueError("Portfolio sources changed during the bounded calculation")
    result["portfolio_id"] = identity(result)
    compressed = gzip.compress(encoded(candidates), mtime=0)
    return result, compressed


def _readme(result):
    retained = sum(len(cell["retained_pareto_candidate_ids"]) for cell in result["cells"])
    global_front = result["archive"]["cross_cell_partial_quantity_pareto_candidate_ids"]
    lines = ["# Breadth-first shape portfolio", "",
        f"This source-bound research portfolio generated **{result['candidate_count']} physical body candidates** across **{result['composition_cell_count']} frame/shell/rib cells** and three parameter profiles. It retains **{retained} per-cell Pareto alternatives**. The separate cross-cell partial-quantity front contains {len(global_front)} candidates.", "",
        "## Scope and evidence", "",
        "Each candidate holds the development baseline's 17 m car length and six-car formation context. The screen uses actual grammar-generated nominal stock, calculated stock mass properties, the current interface checks, declared DFMA operation counts and low/base/high Class C stock-only factory-gate cost. It does not run structural analysis, topology optimization or native CAD for all 54 alternatives. No global scalar winner or integrated selection is produced.", "",
        "The cost is per one car body, with a six-body subtotal also recorded. It includes the current material-family proxy, purchase yield, setup and process-hour estimates, loaded skilled labour, machine allowance, QA allowance and factory overhead. It excludes installed joints and fasteners, unlocated equipment, final vehicle assembly, delivery, tooling investment, civil works, propulsion, operating costs, maintenance and lifecycle cost. The estimate is not a supplier quote or a measured production route.", "",
        "The factory-gate production proxy uses the cost engine's two 8-hour shifts per day. The linked scenario defines civil work at two 8-hour shifts and operations at two 8-hour, two 9-hour and three 8-hour shifts per day; this body-shape study generates no civil estimate, operating cost or staffing plan.", "",
        "## Composition cells", "",
        "| Frame | Shell | Rib layout | Candidates | Per-cell Pareto IDs |", "|---|---|---|---:|---|"]
    for cell in result["cells"]:
        ids = ", ".join(f"`{value[:12]}`" for value in cell["retained_pareto_candidate_ids"])
        d = cell["descriptor"]
        lines.append(f"| {d['frame']} | {d['shell']} | {d['ribs']} | {cell['candidate_count']} | {ids} |")
    lines += ["", "## Interpretation limits", "",
        "The archive preserves alternatives within each material/shape production family. Its metrics are partial quantity estimates and cannot establish that a candidate carries required loads, meets fatigue/fire/accessibility requirements, fits all installed equipment, is cheaper as a railway, or can be manufactured at the estimated hours. Pin-graph and stock totals are not body qualification. Unknown values stay unknown.", "",
        "This first executable breadth step composes the existing aluminium/GFRP frames, skin/sandwich/honeycomb shells and full/sparse/modular rib rules. Curved or variable-thickness shells, cellular/lattice internals, organic implicit geometry, topology optimization, and coupled guideway/station shape families remain future geometry/evaluator adapters. They are not represented by cosmetic labels.", "",
        "The study does not alter the selected v0.6 body or railway, dispatch native solvers, or approve any candidate. Physical and engineering acceptance remain false.", "",
        "## Reproduce and verify", "", "```bash", "./osr design portfolio plan", "./osr design portfolio build", "./osr design portfolio verify", "```", "",
        "[Result](result.json) · [All generated physical candidates](candidates.json.gz) · [Manifest](manifest.json)", ""]
    return "\n".join(lines)


def _files(directory):
    return {path.relative_to(directory).as_posix(): digest(path)
        for path in sorted(Path(directory).rglob("*"))
        if path.is_file() and path.name != "manifest.json"}


def build(root=ROOT, output=None):
    root = Path(root)
    out = root / OUTPUT if output is None else Path(output)
    result, compressed = _calculate(root)
    readme = _readme(result).encode()
    if out.exists():
        manifest_path = out / "manifest.json"
        if not manifest_path.is_file():
            raise ValueError("Existing portfolio output has no source-bound manifest")
        previous = json.loads(manifest_path.read_bytes())
        if previous.get("manifest_id") != identity({k: v for k, v in previous.items() if k != "manifest_id"}):
            raise ValueError("Existing portfolio manifest identity differs")
        if previous.get("files_sha256") != _files(out):
            raise ValueError("Existing portfolio payload changed; investigate before replacement")
        if previous.get("source_sha256") == sources(root):
            return verify(root, out)
        archive = root / "build/design-portfolio/replaced-publications" / previous["manifest_id"]
        archive.parent.mkdir(parents=True, exist_ok=True)
        if archive.exists():
            raise ValueError("Previous source-bound portfolio is already retained")
        shutil.move(out, archive)
    out.mkdir(parents=True)
    (out / "result.json").write_bytes(encoded(result))
    (out / "candidates.json.gz").write_bytes(compressed)
    (out / "README.md").write_bytes(readme)
    manifest = dict(schema="osr-breadth-first-shape-portfolio-publication/1",
        portfolio_id=result["portfolio_id"], source_sha256=result["source_sha256"],
        files_sha256=_files(out))
    manifest["manifest_id"] = identity(manifest)
    (out / "manifest.json").write_bytes(encoded(manifest))
    return verify(root, out)


def verify(root=ROOT, output=None):
    root = Path(root)
    out = root / OUTPUT if output is None else Path(output)
    manifest_path = out / "manifest.json"
    if not manifest_path.is_file():
        raise ValueError("Build the breadth-first portfolio first")
    manifest = json.loads(manifest_path.read_bytes())
    if manifest.get("manifest_id") != identity({k: v for k, v in manifest.items() if k != "manifest_id"}):
        raise ValueError("Portfolio manifest identity differs")
    if manifest.get("files_sha256") != _files(out):
        raise ValueError("Portfolio publication payload hash differs")
    if manifest.get("source_sha256") != sources(root):
        raise ValueError("Portfolio source epoch differs; regenerate from current source definitions")
    published = json.loads((out / "result.json").read_bytes())
    if published.get("portfolio_id") != identity({k: v for k, v in published.items() if k != "portfolio_id"}):
        raise ValueError("Portfolio result identity differs")
    candidates = json.loads(gzip.decompress((out / "candidates.json.gz").read_bytes()))
    if len(candidates) != published.get("candidate_count") or sorted(
            candidate.get("candidate_id") for candidate in candidates) != published.get("candidate_ids"):
        raise ValueError("Candidate archive coverage differs from portfolio result")
    for candidate in candidates:
        design_grammar.validate(candidate)
    replay, compressed = _calculate(root)
    if encoded(replay) != encoded(published):
        raise ValueError("Independent portfolio replay differs from the recorded result")
    if compressed != (out / "candidates.json.gz").read_bytes():
        raise ValueError("Generated physical candidate archive differs on replay")
    if _readme(published).encode() != (out / "README.md").read_bytes():
        raise ValueError("Portfolio reader differs from its source-bound result")
    if any(published.get(key) is not False for key in (
            "physical_accepted", "engineering_accepted", "configuration_adopted",
            "manufacturing_release", "operating_release", "selected_reference_changed")):
        raise ValueError("Research portfolio cannot promote its candidate or release the reference")
    if published.get("integrated_selection") is not None or published.get("selected_candidate_id") is not None:
        raise ValueError("Partial shape metrics cannot make an integrated selection")
    return dict(verified=True, portfolio_id=published["portfolio_id"],
        manifest_id=manifest["manifest_id"], candidate_count=published["candidate_count"],
        composition_cell_count=published["composition_cell_count"],
        retained_cell_pareto_count=sum(len(cell["retained_pareto_candidate_ids"])
            for cell in published["cells"]),
        cross_cell_partial_quantity_front_count=len(
            published["archive"]["cross_cell_partial_quantity_pareto_candidate_ids"]),
        integrated_selection=None, physical_accepted=False,
        engineering_accepted=False, manufacturing_release=False, operating_release=False)
