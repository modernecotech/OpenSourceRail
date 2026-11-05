"""Compact, non-promoting handoff from existing 20 m civil research packets.

This consumer checks current quantity and retired-reference mechanics integrity;
it does not independently replay the 189 mechanical calculations or authenticate
physical measurements. Outputs are immutable and belong outside tracked docs.
"""
import argparse
from copy import deepcopy
import gzip
import json
from math import isfinite
from pathlib import Path
import shutil
import stat
import tempfile

from engineering.station_rail import ROOT, retired_station_reference
from engineering.development_baseline import selection
from engineering.station_rail.common import digest, encoded, identity
from . import civil_shape_mechanics as mechanics
from . import civil_shape_portfolio as portfolio
from . import quality_diversity

PRODUCER = "engineering/design_search/civil_demonstrator.py"
LOADED_PRODUCER_SHA256 = digest(Path(__file__))
OUTPUT = "build/civil-demonstrator"
FLAGS = dict(portfolio.FLAGS)
OBJECTIVES = mechanics.OBJECTIVES
OPEN_DOMAINS = (
    "installed-mass-and-resistance-layout", "moving-load-shear-torsion-and-unequal-rails",
    "cracking-fatigue-creep-shrinkage-and-composite-transfer", "connections-bearings-and-prestress-anchorage",
    "lifting-points-temporary-stability-and-crane-capacity-at-radius",
    "transport-route-clearances-supports-and-axle-limits", "site-ground-and-foundation-design",
    "machine-crew-curing-precedence-and-inspection-schedule",
    "relative-rail-vehicle-stator-displacement-and-tolerance-chain",
)
LIMITATIONS = (
    "Representative pose maximises midspan live moment only, not local stress, shear or torsion.",
    "Deflection and stress envelopes apply to declared gross linear-elastic hypotheses, not cracked or slipping physical structures.",
    "Prestress and reinforcement reserves add mass and cost, never structural resistance or stiffness.",
    "Steel-only and perfect-bond hybrid models are alternative hypotheses, not proven physical bounds.",
    "The 60 t hook and 25% rigging assumptions do not establish actual crane capacity at radius, ground bearing or lifting stability.",
    "Foundation, bearing and service reserves are not designed installed quantities.",
    "Two-shift worker-equivalent durations are not executable machine, crew, curing or erection schedules.",
    "Global beam deflection is not the relative LIM air-gap movement; the complete interface displacement chain remains open.",
)


def _sealed(value, key, label):
    if not isinstance(value, dict) or value.get(key) != identity({k: v for k, v in value.items() if k != key}):
        raise ValueError(label + " identity differs")


def _flags(value):
    if any(value.get(k) is not v for k, v in FLAGS.items()):
        raise ValueError("Research evidence cannot promote acceptance or change the reference")


def _index(rows, key, label):
    if not isinstance(rows, list) or not rows:
        raise ValueError(label + " coverage is missing")
    result = {}
    for row in rows:
        ident = row.get(key)
        if not isinstance(ident, str) or len(ident) != 64 or ident in result:
            raise ValueError(label + " identities must be unique")
        result[ident] = row
    return result


def _sources(root, mapping):
    if not isinstance(mapping, dict) or not mapping:
        raise ValueError("Explicit current source bindings required")
    for name, expected in mapping.items():
        path = Path(name)
        if path.is_absolute() or ".." in path.parts or not path.parts or digest(Path(root)/path) != expected:
            raise ValueError("Civil demonstrator source epoch differs: " + str(name))


def _pairs(pairs):
    value = {}
    for key, item in pairs:
        if key in value:
            raise ValueError("Duplicate JSON key")
        value[key] = item
    return value


def _json(data):
    def bad_constant(_):
        raise ValueError("Non-finite JSON value")
    return json.loads(data, object_pairs_hook=_pairs, parse_constant=bad_constant)


def _regular(path):
    mode = Path(path).lstat().st_mode
    if not stat.S_ISREG(mode):
        raise ValueError("Regular non-symlink packet file required")


def _packet(root, folder, expected_schema, expected_sources, *, retired_reference=None):
    folder = Path(root)/folder
    if folder.is_symlink() or not folder.is_dir():
        raise ValueError("Regular packet directory required")
    for path in folder.iterdir():
        _regular(path)
    manifest = _json((folder/"manifest.json").read_bytes())
    _sealed(manifest, "manifest_id", "Publication manifest")
    _flags(manifest)
    actual = {p.name: digest(p) for p in folder.iterdir() if p.name != "manifest.json"}
    historical = retired_reference is not None
    if historical and manifest['manifest_id'] != retired_reference['retired_manifest_ids'].get(Path(folder).name):
        raise ValueError("Retired civil publication does not match its fixed source pin")
    if (manifest.get("schema") != expected_schema or actual != manifest.get("files_sha256")
            or (not historical and manifest.get("source_sha256") != expected_sources)):
        raise ValueError("Current civil publication payload or source bindings differ")
    if not historical:
        _sources(root, manifest["source_sha256"])
    return manifest


def _checked_inputs(root=ROOT):
    """Authenticate unchanged retired mechanics; no current evaluator admission."""
    root = Path(root)
    reference = retired_station_reference.verify(root)
    selected = selection.load(root)
    if any(reference['reference_candidate_ids'][key] != selected['vehicle'][key] for key in
           ('candidate_id', 'body_candidate_id', 'support_component_id', 'propulsion_component_id')):
        raise ValueError("Retired civil load physical reference differs from the current vehicle")
    pmanifest = _packet(root, portfolio.OUTPUT, "osr-civil-shape-publication/1", portfolio.sources(root))
    mmanifest = _packet(root, mechanics.OUTPUT, "osr-civil-mechanics-publication/1", None, retired_reference=reference)
    p = _json((root/portfolio.OUTPUT/"result.json").read_bytes())
    definitions = _json(gzip.decompress((root/portfolio.OUTPUT/"candidates.json.gz").read_bytes()))
    m = _json(gzip.decompress((root/mechanics.OUTPUT/"result.json.gz").read_bytes()))
    if pmanifest.get("portfolio_id") != p.get("portfolio_id") or mmanifest.get("study_id") != m.get("study_id"):
        raise ValueError("Manifest and civil study identities differ")
    return (p, definitions, m), reference, selected


def load_inputs(root=ROOT):
    return _checked_inputs(root)[0]


def _validate(p, definitions, m, root, reference_mechanics):
    _sealed(p, "portfolio_id", "Quantity portfolio")
    _sealed(m, "study_id", "Mechanical study")
    _flags(p); _flags(m)
    if (p.get("specification") != portfolio.specification(root)
            or m.get("specification") != mechanics.specification(root)
            or p.get("source_sha256") != portfolio.sources(root)
            or m.get("source_sha256") != reference_mechanics["source_sha256"]
            or m.get("parent_portfolio_id") != p["portfolio_id"]
            or p.get("integrated_selection") is not None or m.get("integrated_selection") is not None
            or m.get("stage_1_complete") is not False or m.get("native_jobs_dispatched") != 0):
        raise ValueError("Civil scope, parent, source or non-promoting disposition differs")
    context = m["load_context"]
    if context != reference_mechanics["load_context"]:
        raise ValueError("Selected vehicle, evaluation, selection or load context differs")
    candidates = _index(definitions, "candidate_id", "Physical candidate")
    quantities = _index(p["evaluations"], "candidate_id", "Quantity evaluation")
    summaries = _index(m["evaluations"], "candidate_id", "Mechanics summary")
    models = _index(m["section_models"], "evaluation_id", "Section model")
    cases = _index(m["cases"], "evaluation_id", "Mechanical case")
    if (set(candidates) != set(quantities) or set(candidates) != set(summaries)
            or len(candidates) != 18 or p.get("candidate_count") != 18 or m.get("candidate_count") != 18
            or p.get("family_count") != 6 or len(cases) != 189 or m.get("calculated_case_count") != 189):
        raise ValueError("Complete 18-candidate/189-case coverage required")
    expected_grid = {(f, profile) for f in portfolio.geometry.FAMILIES for profile in portfolio.geometry.PROFILES}
    if {(c["family"], c["profile"]) for c in definitions} != expected_grid:
        raise ValueError("Civil family/profile coverage differs")
    cost_assumptions = portfolio.model_cost.assumptions(root)
    consumed_cases = set(); consumed_models = set()
    for cid, c in candidates.items():
        q = quantities[cid]; summary = summaries[cid]
        if c != portfolio.geometry.generate(c["family"], c["profile"]):
            raise ValueError("Physical geometry differs from the declared family/profile")
        mechanics._parent_binding(c, q)
        _flags(q); _sealed(summary, "evaluation_id", "Mechanics summary"); _flags(summary)
        if (q.get("cost_estimate") != portfolio.estimate(c, q["quantities"], p["specification"], cost_assumptions)
                or q.get("metrics") != dict(nominal_stock_mass_kg=q["quantities"]["total_nominal_stock_mass_kg"],
                    scoped_installed_base_iqd=q["cost_estimate"]["cases"][1]["scoped_installed_iqd"],
                    factory_hours_base=q["cost_estimate"]["factory_person_hours"]["base"])
                or q.get("descriptor") != {"family": c["family"]} or q.get("profile") != c["profile"]
                or summary.get("descriptor") != q["descriptor"] or summary.get("profile") != c["profile"]
                or summary.get("load_context_id") != context["context_id"]
                or summary.get("stage_1_complete") is not False or summary.get("stage_2_admission") is not False
                or summary.get("first_stage_1_calculations_completed") is not True
                or summary.get("lifting") != mechanics.lifting(c, q, m["specification"])):
            raise ValueError("Same-candidate cost, load, lifting or partial-stage disposition differs")
        section_models = mechanics.sections.models(c, m["specification"]["elastic_moduli_Pa"])
        for model in section_models:
            mid = model["evaluation_id"]
            if models.get(mid) != model:
                raise ValueError("Section model, quantity or material hypothesis differs")
            consumed_models.add(mid)
        local = [case for case in m["cases"] if case["candidate_id"] == cid]
        ids = [case["evaluation_id"] for case in local]
        expected = {(model["evaluation_id"], load["name"], mass["case"])
            for model in section_models for load in context["cases"] for mass in q["cost_estimate"]["cases"]}
        actual = {(case["section_model_id"], case["load_case"], case["dead_mass_case"]) for case in local}
        if summary.get("case_evaluation_ids") != ids or actual != expected or len(local) != len(expected):
            raise ValueError("Mechanical model/load/mass case coverage differs")
        for case in local:
            _sealed(case, "evaluation_id", "Mechanical case"); _flags(case)
            mass = next(x for x in q["cost_estimate"]["cases"] if x["case"] == case["dead_mass_case"])
            model = models[case["section_model_id"]]
            extra = mass["accounted_delivery_mass_kg"]-q["quantities"]["total_nominal_stock_mass_kg"]
            expected_cells = [dict(x_start_m=cell["x_start_m"], x_end_m=cell["x_end_m"],
                EI_Nm2=cell["EI_Nm2"], distributed_load_N_m=(cell["mass_per_length_kg_m"]+extra/20)*mechanics.civil.G)
                for cell in model["cells"]]
            if (case.get("cells") != expected_cells or case.get("quantity_evaluation_id") != q["evaluation_id"]
                    or case.get("load_context_id") != context["context_id"]
                    or case.get("elastic_hypothesis") != model["name"]
                    or case.get("accounted_span_mass_kg") != mass["accounted_delivery_mass_kg"]
                    or case.get("producer_sha256") != {name: m["source_sha256"][name] for name in (
                        mechanics.PRODUCER, mechanics.CAMPAIGN, "engineering/design_search/civil_beam.py")}
                    or case.get("execution") != "completed"
                    or case.get("installed_dead_load_complete") is not False
                    or case.get("physical_deflection_upper_bound_available") is not False
                    or case.get("physical_strength_or_deflection_acceptance_limit") is not None
                    or case.get("stress_upper", {}).get("strength_allowables_available") is not False
                    or case.get("stress_upper", {}).get("resistance_credited") is not False):
                raise ValueError("Mechanical case candidate, source, mass, load or evidence disposition differs")
            for key in ("all_pose_all_observation_model_deflection_upper_m",
                    "representative_sampled_deflection_m", "force_equilibrium_residual_N", "moment_equilibrium_residual_Nm"):
                value = case.get(key)
                if type(value) not in (int, float) or not isfinite(value) or value < 0:
                    raise ValueError("Finite nonnegative mechanical diagnostic required")
            if (case["representative_sampled_deflection_m"] > case["all_pose_all_observation_model_deflection_upper_m"]+1e-10
                    or case["force_equilibrium_residual_N"] > 1e-6
                    or case["moment_equilibrium_residual_Nm"] > 1e-5):
                raise ValueError("Mechanical numerical-validity diagnostics differ from producer checks")
            consumed_cases.add(case["evaluation_id"])
        primary = "steel-only-longitudinal" if c["family"] == "hybrid_steel_concrete" else "full-section-uncracked"
        control = next(x for x in local if x["elastic_hypothesis"] == primary
            and x["load_case"] == "crowd_control" and x["dead_mass_case"] == "high")
        metrics = dict(crowd_high_mass_model_deflection_upper_m=control["all_pose_all_observation_model_deflection_upper_m"],
            lift_adjusted_scoped_installed_base_iqd=summary["lifting"]["cases"][1]["lift_adjusted_scoped_installed_iqd"],
            nominal_stock_mass_kg=q["quantities"]["total_nominal_stock_mass_kg"])
        if summary.get("primary_elastic_hypothesis") != primary or summary.get("metrics") != metrics:
            raise ValueError("Summary objectives do not derive from the same-candidate evidence")
    if consumed_cases != set(cases) or consumed_models != set(models):
        raise ValueError("Orphan mechanical cases or section models")
    if (p.get("archive") != quality_diversity.archive(p["evaluations"], portfolio.OBJECTIVES, ("family",))
            or m.get("archive") != quality_diversity.archive(m["evaluations"], OBJECTIVES, ("family",))):
        raise ValueError("Civil Pareto archive differs from its evaluated pool")
    return candidates, quantities, summaries, cases


def plan_followup(rows, retained_ids, maximum_tasks=6):
    """Choose balanced within-family research representatives, never admission."""
    if type(maximum_tasks) is not int or not 0 <= maximum_tasks <= 6:
        raise ValueError("Explicit zero-to-six candidate work-package budget required")
    indexed = _index(rows, "candidate_id", "Follow-up candidate")
    if not isinstance(retained_ids, list) or len(set(retained_ids)) != len(retained_ids) or set(retained_ids)-set(indexed):
        raise ValueError("Explicit unique Pareto candidate identities required")
    families = {}
    for row in rows:
        if row.get("stage_1_complete") is not False or row.get("stage_2_admission") is not False:
            raise ValueError("Follow-up consumes partial stage-one evidence only")
        _flags(row)
        for metric in OBJECTIVES:
            value = row.get("metrics", {}).get(metric)
            if type(value) not in (int, float) or not isfinite(value) or value < 0:
                raise ValueError("Finite nonnegative known ranking metric required: " + metric)
        families.setdefault(row["descriptor"]["family"], []).append(row)
    if len(families) != 6:
        raise ValueError("Six distinct civil families required")
    representatives = []; rank_records = {}
    for family, members in sorted(families.items()):
        eligible = [r for r in members if r["candidate_id"] in retained_ids]
        if not eligible:
            raise ValueError("Every family needs a retained Pareto alternative")
        for row in eligible:
            ranks = {key: sum(other["metrics"][key] < row["metrics"][key] for other in eligible)
                for key in OBJECTIVES}
            rank_records[row["candidate_id"]] = ranks
        winner = min(eligible, key=lambda row: (
            max(rank_records[row["candidate_id"]].values()),
            sum(rank_records[row["candidate_id"]].values()), row["candidate_id"]))
        representatives.append(winner["candidate_id"])
    queued = representatives[:maximum_tasks]
    decisions = []
    for cid, row in sorted(indexed.items()):
        reason = ("balanced-family-representative" if cid in queued else
            "family-representative-deferred-by-budget" if cid in representatives else
            "retained-pareto-alternative" if cid in retained_ids else "dominated-alternative-retained-for-traceability")
        decisions.append(dict(candidate_id=cid, family=row["descriptor"]["family"],
            state="queued" if cid in queued else "deferred", reason=reason,
            within_family_objective_ranks=rank_records.get(cid)))
    return dict(schema="osr-civil-demonstrator-followup/1", purpose="next-experiment", maximum_tasks=maximum_tasks,
        policy="One Pareto representative per family: minimise worst ascending objective rank, then rank sum, then physical identity; lexical family order applies only to budget deferral.",
        objectives=list(OBJECTIVES), representative_candidate_ids=representatives, queued_candidate_ids=queued,
        deferred_candidate_ids=sorted(set(indexed)-set(queued)), decisions=decisions,
        requests=[dict(candidate_id=cid, stage=1, state="queued-not-executed",
            admission="unresolved-stage-one-domain-and-definition-work", required_domains=list(OPEN_DOMAINS),
            source_mechanics_evaluation_id=indexed[cid]["evaluation_id"],
            resources=dict(maximum_runtime_s=150, maximum_memory_bytes=512*1024**2,
                operating_system_enforcement=False),
            required_artifacts=["same-candidate domain/load/interface definitions",
                "complete mass/resistance proposal and unresolved evidence", "next evaluator admission decision"],
            completion="Resolve or explicitly retain every required domain; no automatic stage-two admission",
            stage_2_admission=False, native_jobs=0, **FLAGS) for cid in queued],
        integrated_selection=None, global_optimum_proven=False, native_jobs_dispatched=0, **FLAGS)


def consolidate(p, definitions, m, *, root=ROOT, maximum_tasks=6):
    """Join checked current packets into a compact, explicitly conditional record."""
    if (digest(Path(__file__)) != LOADED_PRODUCER_SHA256
            or digest(Path(root)/PRODUCER) != LOADED_PRODUCER_SHA256):
        raise ValueError("Loaded civil demonstrator producer differs from the declared source root")
    common_sources = set(p["source_sha256"]) & set(m["source_sha256"])
    if any(p["source_sha256"][name] != m["source_sha256"][name] for name in common_sources):
        raise ValueError("Civil parent/mechanics source epochs conflict")
    checked, reference, selected = _checked_inputs(root)
    source = {**p["source_sha256"], **selected['source_sha256'],
        **reference['dependency_sha256'], PRODUCER: LOADED_PRODUCER_SHA256}
    for folder in (portfolio.OUTPUT, mechanics.OUTPUT):
        source[folder+"/manifest.json"] = digest(Path(root)/folder/"manifest.json")
    _sources(root, source)
    candidates, quantities, summaries, cases = _validate(p, definitions, m, root, checked[2])
    if (p, definitions, m) != checked:
        raise ValueError("Supplied civil evidence differs from the checked publication payloads")
    followup = plan_followup(m["evaluations"], m["archive"]["retained_candidate_ids"], maximum_tasks)
    evidence = []
    for cid, c in sorted(candidates.items()):
        q = quantities[cid]; summary = summaries[cid]
        local = [cases[eid] for eid in summary["case_evaluation_ids"]]
        evidence.append(dict(candidate_id=cid, family=c["family"], profile=c["profile"], span_m=c["span_m"],
            quantity_evaluation_id=q["evaluation_id"], nominal_quantity_evaluation_id=q["quantities"]["evaluation_id"],
            mechanics_evaluation_id=summary["evaluation_id"], case_evaluation_ids=summary["case_evaluation_ids"],
            section_model_ids=sorted({case["section_model_id"] for case in local}),
            material_quantities=q["quantities"]["by_material"], nominal_centroid_m=q["quantities"]["centroid_m"],
            metrics=summary["metrics"], cost_estimate=q["cost_estimate"], lifting=summary["lifting"],
            force_equilibrium_residual_N=max(case["force_equilibrium_residual_N"] for case in local),
            moment_equilibrium_residual_Nm=max(case["moment_equilibrium_residual_Nm"] for case in local),
            evidence_status=dict(geometry="declared-nominal-prism-stock", quantity="calculated-nominal-stock",
                production="provisional-process-and-two-shift-labour-capacity", cost="bounded-Class-C-scenarios",
                mechanics="conditional-gross-linear-elastic-cases", installed_mass="unknown",
                strength="unknown", physical_acceptance="pending"),
            installed_mass_kg=None, strength_allowable_Pa=None, physical_deflection_limit_m=None,
            stage_1_complete=False, stage_2_admission=False, unresolved_domains=list(OPEN_DOMAINS), **FLAGS))
    _sources(root, source)
    value = dict(schema="osr-civil-demonstrator/1", purpose="next-experiment", span_m=20.,
        portfolio_id=p["portfolio_id"], mechanics_study_id=m["study_id"],
        load_context_id=m["load_context"]["context_id"],
        vehicle_candidate_id=m["load_context"]["vehicle_candidate_id"],
        vehicle_evaluation_id=m["load_context"]["vehicle_evaluation_id"], selection_id=m["load_context"]["selection_id"],
        reference_comparison=dict(selection_role='retired-reference-control-comparison',
            reference_commit=reference['reference_commit'], retention_id=reference['retention_id'],
            reference_selection_id=reference['reference_selection_id'],
            reference_dossier_evaluation_id=reference['reference_evaluation_id'],
            reference_vehicle_evaluation_id=m['load_context']['vehicle_evaluation_id'],
            active_selection_id=selected['selection_id'],
            active_vehicle_evaluation_id=selected['vehicle']['evaluation_id'],
            active_policy_id=selected['active_propulsion_policy']['policy_id'],
            reference_source_sha256=deepcopy(m['source_sha256']),
            current_evaluator_admission=False, numerical_reexecuted=False,
            active_installed_propulsion_selected=False),
        current_evaluator_admission=False, numerical_reexecuted=False,
        source_sha256=source, candidate_count=len(evidence), linked_mechanics_cases=len(cases), evidence=evidence,
        followup=followup, limitations=list(LIMITATIONS), integrated_selection=None,
        stage_1_complete=False, stage_2_admission=False, native_jobs_dispatched=0,
        verification_scope="Packet/source/identity/crosslink consistency with cheap geometry, quantity, cost, section and load reconstruction; no independent mechanical replay, physical authentication or OS sandbox.", **FLAGS)
    value["handoff_id"] = identity(value)
    return deepcopy(value)


def calculate(root=ROOT, maximum_tasks=6):
    return consolidate(*load_inputs(root), root=root, maximum_tasks=maximum_tasks)


def _readme(value):
    lines = ["# Civil demonstrator handoff", "",
        "A 20 m research comparison connects 18 physical candidates to 189 existing conditional mechanics cases. This handoff queues unresolved stage-one work; it neither runs a solver nor selects a railway structure.", "",
        "| Family / profile | Stock (t) | Adjusted scoped base cost (IQD million) | Conditional deflection (mm) | Follow-up |",
        "|---|---:|---:|---:|---|"]
    decisions = {row["candidate_id"]: row for row in value["followup"]["decisions"]}
    for row in value["evidence"]:
        metric = row["metrics"]
        lines.append(f"| {row['family']} / {row['profile']} | {metric['nominal_stock_mass_kg']/1000:.2f} | {metric['lift_adjusted_scoped_installed_base_iqd']/1e6:.2f} | {metric['crowd_high_mass_model_deflection_upper_m']*1000:.2f} | {decisions[row['candidate_id']]['state']} |")
    lines += ["", "All installed masses, strength allowables and physical acceptance limits remain unknown. Factory and civil scenarios each use two eight-hour shifts. The low/base/high cost lines and provisional routes are preserved in result.json.", "", *["- "+item for item in value["limitations"]], "", value["verification_scope"], "", "Handoff: `"+value["handoff_id"]+"`", ""]
    return "\n".join(lines)


def build(root=ROOT, output=None, maximum_tasks=6):
    """Create an immutable local package; never overwrite a previous handoff."""
    root = Path(root); out = root/OUTPUT if output is None else Path(output)
    if out.exists() or out.is_symlink():
        raise ValueError("Handoff output already exists; verify it or choose a fresh directory")
    value = calculate(root, maximum_tasks)
    out.parent.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix=".civil-demonstrator-", dir=out.parent))
    try:
        (stage/"result.json").write_bytes(encoded(value)); (stage/"README.md").write_text(_readme(value))
        manifest = dict(schema="osr-civil-demonstrator-publication/1", handoff_id=value["handoff_id"],
            source_sha256=value["source_sha256"], files_sha256={p.name: digest(p) for p in stage.iterdir()}, **FLAGS)
        manifest["manifest_id"] = identity(manifest)
        (stage/"manifest.json").write_bytes(encoded(manifest))
        verify(root, stage)
        stage.rename(out)
    finally:
        if stage.exists():
            shutil.rmtree(stage)
    return verify(root, out)


def verify(root=ROOT, output=None):
    """Verify recorded sources and reconstruct the handoff; do not refresh it."""
    root = Path(root); out = root/OUTPUT if output is None else Path(output)
    if out.is_symlink() or not out.is_dir():
        raise ValueError("Regular handoff directory required")
    for path in out.iterdir():
        _regular(path)
    manifest = _json((out/"manifest.json").read_bytes())
    _sealed(manifest, "manifest_id", "Handoff manifest"); _flags(manifest)
    if (manifest.get("schema") != "osr-civil-demonstrator-publication/1"
            or set(manifest.get("files_sha256", {})) != {"README.md", "result.json"}
            or {p.name: digest(p) for p in out.iterdir() if p.name != "manifest.json"} != manifest["files_sha256"]):
        raise ValueError("Civil handoff payload differs")
    _sources(root, manifest["source_sha256"])
    value = _json((out/"result.json").read_bytes()); _sealed(value, "handoff_id", "Handoff")
    expected = calculate(root, value.get("followup", {}).get("maximum_tasks"))
    if (value != expected or manifest.get("handoff_id") != value["handoff_id"]
            or manifest.get("source_sha256") != value["source_sha256"]
            or (out/"README.md").read_text() != _readme(value)):
        raise ValueError("Civil handoff does not reproduce from current checked inputs")
    return dict(verified=True, handoff_id=value["handoff_id"], manifest_id=manifest["manifest_id"],
        candidate_count=value["candidate_count"], linked_mechanics_cases=value["linked_mechanics_cases"],
        queued=len(value["followup"]["queued_candidate_ids"]), deferred=len(value["followup"]["deferred_candidate_ids"]),
        stage_1_complete=False, stage_2_admission=False, native_jobs_dispatched=0, **FLAGS)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("build", "verify"))
    parser.add_argument("--output", type=Path)
    parser.add_argument("--maximum-tasks", type=int, default=6)
    args = parser.parse_args()
    result = build(output=args.output, maximum_tasks=args.maximum_tasks) if args.action == "build" else verify(output=args.output)
    print(json.dumps(result, indent=2))
