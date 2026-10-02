#!/usr/bin/env python3
"""Compile the civil demonstration package; keep site release explicitly pending."""
from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from engineering.analysis.civil_evidence import sha
from osr_mech.civil.decked_pi import section_area_m2
from osr_mech.civil.foundation import foundation_candidates
from osr_mech.civil.reference import lifting_budget, compare_foundations

SOURCE = "engineering/assurance/civil-reference/reference-system.json"
DESTINATION = "engineering/assurance/civil-reference"


def load_thread():
    spec = importlib.util.spec_from_file_location("osr_connected_thread", ROOT/"tools/automation/connected_assurance.py")
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    return module


def compile_package(root: Path = ROOT) -> dict:
    source = json.loads((root/SOURCE).read_text())
    if source["schema"] != "osr-civil-reference/1": raise ValueError("unknown civil reference schema")
    thread = load_thread()
    budgets = {f"Pi{span}": lifting_budget(span, source["lifting"]["masses_kg"], source["lifting"]["configuration"]) for span in (20,25)}
    candidates = foundation_candidates(source["foundation_ground_class"], vibration_restricted=True)
    selection = compare_foundations(candidates["candidate_ids"], source.get("foundation_comparisons", []), source["foundation_site_inputs"])
    paths = [SOURCE, "tools/automation/civil_reference.py", "tools/automation/connected_assurance.py",
             "design/component-catalogue/src/osr_mech/civil/reference.py",
             "design/component-catalogue/src/osr_mech/civil/foundation.py",
             "design/component-catalogue/src/osr_mech/civil/decked_pi.py",
             "engineering/analysis/civil_evidence.py", "engineering/analysis/structural_release.py",
             "engineering/analysis/drainage_ground_design.py", "engineering/analysis/benchmarks/civil_reference.py",
             "lib/templates/structural-release-processing.toml", "lib/templates/drainage-ground-design-processing.toml"]
    paths += [p.relative_to(root).as_posix() for p in sorted((root/DESTINATION/"drainage").glob("*.inp"))]
    source_hashes = {p:sha(root/p) for p in paths}
    demonstrations = {}
    result_dir = root/DESTINATION/"calculations"
    for name in ("beam-sanity", "drainage-sanity"):
        path = result_dir/f"{name}.json"
        if not path.exists():
            demonstrations[name] = {"status":"not-executed", "project_design_accepted":False}
            continue
        value = json.loads(path.read_text())
        if value.get("project_design_accepted") is not False: raise ValueError("sanity exercise cannot claim project acceptance")
        if value.get("generator_sha256") != sha(root/"engineering/analysis/benchmarks/civil_reference.py"):
            raise ValueError("stale solver demonstration generator; rerun --run-solvers")
        for p,digest in value.get("dependency_hashes", {}).items():
            if sha(root/p) != digest: raise ValueError("stale solver dependency; rerun --run-solvers")
        for p,digest in value.get("output_hashes", {}).items():
            if Path(p).name != p or sha(result_dir/p) != digest: raise ValueError("solver demonstration native output mismatch")
        if name == "drainage-sanity":
            for scenario,row in value["scenarios"].items():
                if row["input_sha256"] != sha(root/DESTINATION/"drainage"/f"{scenario}.inp"):
                    raise ValueError("stale drainage demonstration input; rerun --run-solvers")
        demonstrations[name] = value
        source_hashes[path.relative_to(root).as_posix()] = sha(path)
    nodes = []; edges = []
    def node(identifier, kind, **fields): nodes.append(dict(id=identifier, kind=kind, **fields))
    def edge(a,b,relation): edges.append({"from":a,"to":b,"relation":relation})
    node(source["id"],"configurations",revision=source["revision"],source=SOURCE,release_ready=False)
    node("CIVIL-GATE","decisions",status="blocked",blockers=source["site_inputs_required"])
    for asset in [*source["asset_register"]["assets"], *source["connections"], *source["drainage_objects"], *source["asset_register"]["supports"]]:
        identifier = asset.get("asset_id",asset.get("support_id",asset.get("id")))
        existing = next((n for n in nodes if n["id"] == identifier), None)
        if existing:
            existing["interface_definition"] = asset
            continue
        node(identifier,"design_items",definition=asset,source=SOURCE)
        edge(source["id"],identifier,"contains")
    for row in source["failure_modes"]:
        identifier = row["id"]
        node(identifier,"failure_modes",definition=row)
        edge(row["asset_id"],identifier,"exposed-to")
        previous = identifier
        for i,stage in enumerate(row["causal_chain"]):
            chain_id = f"{identifier}-CHAIN-{i+1}"
            node(chain_id,"hazards",title=stage,stage=row["stage"])
            edge(previous,chain_id,"can-cause"); previous=chain_id
        req,ev = identifier+"-REQ",identifier+"-EVIDENCE"
        node(req,"requirements",controls=row["controls"],proof_required=row["required_evidence"])
        node(ev,"evidence",status="missing",evidence_class="physical-qualification-and-independent-review",satisfies=False)
        edge(previous,req,"requires-control");edge(req,ev,"requires-evidence");edge(ev,"CIVIL-GATE","blocks-release")
    identifiers = [r["id"] for r in nodes]
    if len(set(identifiers)) != len(identifiers) or any(e[k] not in identifiers for e in edges for k in ("from","to")):
        raise ValueError("civil graph duplicate ID or dangling relationship")
    graph = {"nodes":nodes,"edges":edges,"node_hashes":{r["id"]:thread.fingerprint(r) for r in nodes},"source_hashes":source_hashes}
    graph["drain_change_impact"] = thread.change_impact(graph,graph,["DRAIN-01"])
    return {"schema":"osr-civil-reference-report/1","id":source["id"],"status":source["status"],"release_ready":False,
            "authority_accepted":False,"independently_checked_design":False,"source_hashes":source_hashes,
            "layout":source["asset_register"],"lifting_budgets":budgets,"foundation_candidates":candidates,"foundation_comparison":selection,
            "quantities":{"basis":"bare envelope only; net local details and supplier take-off unresolved", "beam_count":4,
                "bare_beam_concrete_m3":2*section_area_m2()*(20+25),"deck_envelope_area_m2":2*2.9*(20+25),
                "elevated_support_lines":3,"bearing_seats_candidate":source["bearings"]["seat_count"],"at_grade_double_track_length_m":20,
                "foundation_concrete_m3":None,"reinforcement_kg":None,"prestress_kg":None,"installed_cost_usd":None},
            "connections":source["connections"],"bearings":source["bearings"],"construction_sequence":source["construction_sequence"],
            "comparator":source["comparator"],"trackform_options":source["trackform_options"],"drainage_objects":source["drainage_objects"],
            "failure_modes":source["failure_modes"],"site_inputs_required":source["site_inputs_required"],"references":source["references"],
            "demonstrations":demonstrations,"graph":graph}


def markdown(r: dict) -> str:
    lines = ["# Civil reference demonstration A", "", "**Status: awaiting site design, physical evidence and independent review. Release is blocked.**", "",
        "The reference contains adjoining 20 m and 25 m double-track bays and a 20 m at-grade transition. It provides quantities, connection briefs, construction hold points, option comparisons and a connected civil FMEA. It is a review package for engineers and suppliers; it has no accepted construction drawings.", "",
        "## Layout and quantities", "", "| Asset | Family | Chainage (m) | Supports |", "|---|---|---:|---|"]
    for a in r["layout"]["assets"]: lines.append(f"| {a['asset_id']} | {a['variant_id']} | {a['from_station_m']}–{a['to_station_m']} | {', '.join(a['support_ids'])} |")
    lines += ["",f"Four bare beams contain **{r['quantities']['bare_beam_concrete_m3']:.2f} m³** of envelope concrete over **{r['quantities']['deck_envelope_area_m2']:.1f} m²** of deck. Foundation, reinforcement, prestress and installed cost quantities remain unresolved. Three elevated support lines and a ground-zone check at 65 m are identified. The candidate arrangement has 16 bearing seats; capacities and fixity are unresolved.","", "## Mass and lifting", "", "| Family | Bare mass (kg) | Margin under 75 t (kg) | Complete lift |", "|---|---:|---:|---|"]
    for name,b in r["lifting_budgets"].items(): lines.append(f"| {name} | {b['bare_mass_kg']:,.1f} | {b['bare_margin_kg']:,.1f} | {b['status']} |")
    lines += ["", "Net diaphragms, bulk-density reinforcement adjustment, prestress steel, anchorages, embedded lifting hardware, attachments, retained temporary works, slings, spreader and hook/block masses must be measured or substantiated. The overlapping CAD diaphragm zones cannot be summed as additional fabrication concrete. The actual crane/launcher chart, configuration, radius, dynamic allowance, utilisation, centre of gravity, ground support and lateral stability must be reviewed.", "", "## Foundation and trackform comparison", "",f"Candidate foundations: {', '.join(r['foundation_candidates']['candidate_ids'])}. None is selected. A measured comparison must cover axial/lateral resistance, total and differential settlement, groundwater, chemistry, liquefaction/scour where relevant, utilities and installation constraints. Calcium-based treatment needs reviewed chemistry compatibility. Reinforced-soil approaches need railway deformation, stability and scour justification.","", "Ballasted track, slipformed slab and precast panels remain explicit alternatives. Compare settlement, drainage, local material and maintenance capability, repair possessions and whole-life cost for the 20 m transition before selection.","", "## Conventional girder comparator", "", r["comparator"]["system"]+" is retained for both spans. Supplier section, girder count, deck quantities and price are pending; no system is declared cheapest.",""]
    lines += [f"- {field}." for field in r["comparator"]["comparison_fields"]]
    lines += ["", "Use equivalent railway actions, geometry and service-life assumptions for both systems. Record initial capital, construction possessions, inspection, cleaning, bearing/track replacement, discount rate and uncertainty before calculating whole-life net present cost.", "", "## Controlled connection briefs", "", "Numerical loads, tolerances, resistance and movement limits are pending for every connection. Each requires an engineered drawing, first-article qualification and independent review.", ""]
    for c in r["connections"]:
        lines += [f"### {c['id']} — {c['title']}","",f"Loads: {c['applicable_loads']}.","",f"Install: {c['installation_sequence']}.","",f"Inspect: {c['inspection']}.","",f"Repair/replacement: {c['repair_method']}.",""]
    lines += ["## Construction sequence and hold points", "", "| Stage | Activity | Hold point |", "|---|---|---|"]
    lines += [f"| {s['id']} | {s['activity']} | {s['hold_point']} |" for s in r["construction_sequence"]]
    lines += ["", "## Calculations and drainage demonstration", "", "[Native model/result files](calculations/) preserve the reproducible elastic calculation and drainage replay. The beam comparison uses E = 30 GPa, bulk-envelope self-weight, an illustrative 20 kN/m additional service load and endpoint supports. OpenSees uses the Pi-section area/inertia; CalculiX uses an equal-area/inertia rectangular surrogate. Prestress, reinforcement, torsion, fatigue, derailment, seismic response, actual lift support positions and rail interaction are unresolved.","", "The elastic hand check is 5wL⁴/(384EI). This checks software and units; its deflections are not accepted railway limits.",""]
    beam = r["demonstrations"].get("beam-sanity", {})
    if beam.get("results"):
        lines += ["| Span / stage | Hand deflection (mm) | OpenSees (mm) | CalculiX (mm) |", "|---|---:|---:|---:|"]
        lines += [f"| {x['span_m']:g} m / {x['stage']} | {1000*x['analytical_deflection_m']:.3f} | {1000*x['opensees_deflection_m']:.3f} | {1000*x['calculix_deflection_m']:.3f} |" for x in beam["results"]]
    lines += ["", "The synthetic drainage system uses a 1 ha catchment, a 50 m conduit and a storm independent of any site. The blockage sensitivity reduces the 0.5 m conduit to 0.1 m; the backwater sensitivity fixes tailwater at 1.5 m. Reviewed project blockage/debris and flood boundaries may require different cases.",""]
    for name,entry in r["demonstrations"].get("drainage-sanity", {}).get("scenarios", {}).items():
        lines.append(f"- {name}: routing continuity error {entry['replay']['routing_error_percent']:.6g}%; {len(entry['illustrative_limit_findings'])} hydraulic limit exceedances in the illustrative screen.")
    lines += ["", "Adequate continuity does not establish adequate drainage. Flooding volume, surcharge duration, peak head, conduit depth and outfall flow are checked using engine statistics across every routing step. Culvert debris, outfall consent, erosion/scour, flood pathways and cleaning access need site design. Consider ANUGA when 2D surface overflow changes the risk.", "", "## Connected civil FMEA", "", "| ID / stage | Failure chain | Controls and evidence |", "|---|---|---|"]
    lines += [f"| {f['id']} / {f['stage']} | {' → '.join(f['causal_chain'])} | {f['controls']}. Evidence: {f['required_evidence']}. **Open**. |" for f in r["failure_modes"]]
    lines += ["", "[Machine-readable report](report.json) contains the typed graph and drain-change trace. It uses the existing connected-assurance traversal, including both old and new relationships. A drain change reaches saturation, settlement, geometry, operating risk, required evidence and the civil release gate. All physical and independent evidence remains missing.", "", "## Unresolved site inputs", ""]
    lines += [f"- {s}." for s in r["site_inputs_required"]]
    lines += ["", "## Public references and reuse rights", "", "No external drawing or code was copied into this package. Record drawing-specific rights before incorporation; software licences do not grant rights to unrelated drawings.", "", "| Reference | Intended use | Rights/access status |", "|---|---|---|"]
    lines += [f"| [{s['id']}]({s['url']}) | {s['use']} | {s['reuse_rights']}; {s['retrieval_status']} |" for s in r["references"]]
    lines += ["", "## Reproduction", "", "From the repository root:", "", "```bash", ".venv/bin/python tools/automation/civil_reference.py --run-solvers", ".venv/bin/python tools/automation/civil_reference.py --check", "```", "", "OpenSeesPy, PySWMM and native `ccx` are needed for replay. The default compiler and `--check` validate recorded files and provenance without running native solvers. The release gates require a separately reviewed, design-hash-bound asset register, per-asset numerical outputs and accepted limits. This concept register is deliberately pending and cannot satisfy them.", ""]
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--run-solvers", action="store_true")
    args = parser.parse_args()
    if args.check and args.run_solvers: parser.error("choose generation/replay or --check")
    if args.run_solvers:
        from engineering.analysis.benchmarks.civil_reference import run_beams, run_drainage
        output = ROOT/DESTINATION/"calculations"
        run_beams(output); run_drainage(output)
    report = compile_package()
    generated = {"report.json":json.dumps(report,indent=2,sort_keys=True)+"\n", "README.md":markdown(report)}
    for name,contents in generated.items():
        path = ROOT/DESTINATION/name
        if args.check:
            if not path.is_file() or path.read_text() != contents: raise SystemExit(f"stale civil reference: {path}")
        else: path.write_text(contents)
    print("Civil reference package current; site design, physical qualification and independent acceptance pending.")


if __name__ == "__main__": main()
