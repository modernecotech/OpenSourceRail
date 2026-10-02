#!/usr/bin/env python3
"""Compile the civil demonstration package; keep site release explicitly pending."""
from __future__ import annotations

import argparse
import csv
import math
import tempfile
import importlib.util
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from engineering.analysis.civil_evidence import sha, finite, controlled_path, design_context, inspect_register
from osr_mech.civil.decked_pi import section_area_m2, DECK_WIDTH_MM
from osr_mech.civil.foundation import foundation_candidates
from osr_mech.civil.reference import lifting_budget, compare_foundations

SOURCE = "engineering/assurance/civil-reference/reference-system.json"
DESTINATION = "engineering/assurance/civil-reference"


def load_thread():
    spec = importlib.util.spec_from_file_location("osr_connected_thread", ROOT/"tools/automation/connected_assurance.py")
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    return module


def layout_quantities(source: dict, root: Path) -> tuple[dict, dict, dict]:
    register = source["asset_register"]
    basis_path = root/source["route_basis_path"]
    station_lines, extents = design_context(basis_path)
    line_ids = {r["line_id"] for r in extents}
    findings = inspect_register(register, sha(basis_path), line_ids, set(station_lines), station_lines, extents, require_review=False)
    if findings: raise ValueError("invalid civil layout: " + "; ".join(findings))
    route_basis = json.loads(basis_path.read_text())
    if {r["id"] for r in source["drainage_objects"] if r["kind"] != "transition"} != set(route_basis["drainage_asset_ids"]):
        raise ValueError("drainage objects differ from authoritative route basis")
    spans = [a for a in register["assets"] if a["asset_type"] == "span"]
    grade = [a for a in register["assets"] if a["asset_type"] == "at-grade-structure"]
    lengths = {a["asset_id"]: finite(a["to_station_m"])-finite(a["from_station_m"]) for a in spans}
    for a in spans:
        if a["variant_id"] != f"Pi{lengths[a['asset_id']]:g}": raise ValueError("Pi variant and layout span length disagree")
    budgets = {f"Pi{span:g}":lifting_budget(span, source["lifting"]["masses_kg"], source["lifting"]["configuration"],
               product_deviation=source["lifting"].get("product_deviations", {}).get(f"Pi{span:g}")) for span in sorted(set(lengths.values()))}
    seats = source["bearings"]["seats_per_beam_end"]
    if type(seats) is not int or seats < 1: raise ValueError("candidate bearing seats per end must be positive integer")
    grade_length = 0.
    for line in line_ids:
        ranges = sorted((finite(a["from_station_m"]),finite(a["to_station_m"])) for a in grade if a["line_id"] == line)
        end = -1.
        for start,finish in ranges:
            grade_length += max(0.,finish-max(start,end));end=max(end,finish)
    quantities = {"basis":"layout-derived bare envelope only; local details, supplier take-off and installed cost unresolved", "beam_count":len(spans),
        "span_lengths_m":sorted(set(lengths.values())), "bare_beam_concrete_m3":sum(lengths.values())*section_area_m2(),
        "deck_envelope_area_m2":sum(lengths.values())*DECK_WIDTH_MM/1000,
        "elevated_support_lines":len({i for a in spans for i in a["support_ids"]}),
        "bearing_seats_candidate":2*len(spans)*seats, "at_grade_route_length_m":grade_length,
        "at_grade_track_length_m":sum(finite(a["to_station_m"])-finite(a["from_station_m"]) for a in grade),
        "route_track_counts":{r.get("id",r.get("name")):r["civil_track_count"] for r in route_basis["lines"]},
        "bare_mass_by_asset_kg":{a["asset_id"]:budgets[a["variant_id"]]["bare_mass_kg"] for a in spans},
        "foundation_concrete_m3":None,"reinforcement_kg":None,"prestress_kg":None,"installed_cost_usd":None,
        "cost_state":"no comparable validated installed/whole-life price"}
    return quantities,budgets,{a["asset_id"]:a for a in register["assets"]}


def compile_civil_graph(root: Path, source: dict, thread) -> dict:
    config_path = source["assurance_path"]
    config = json.loads((root/config_path).read_text())
    definitions = {}
    for rows in (source["asset_register"]["assets"], source["asset_register"]["supports"], source["connections"], source["drainage_objects"]):
        for row in rows:
            identifier = row.get("asset_id",row.get("support_id",row.get("id")))
            definitions.setdefault(identifier, []).append(row)
    ids = {r["id"] for r in config["design_items"]}
    if not set(definitions) <= ids: raise ValueError("civil assurance needs every layout/connection/drainage item")
    for row in config["design_items"]:
        definition = definitions.get(row["id"], {"title":row["title"],"part_of":row.get("part_of",[])})
        row["definition"] = definition
        row["revision"] = "sha256:" + thread.fingerprint({"definition":definition,"lifting":source["lifting"],"bearing_seats_per_end":source["bearings"]["seats_per_beam_end"],"route_basis_sha256":sha(root/source["route_basis_path"]),
            "geometry_sha256":sha(root/"design/component-catalogue/src/osr_mech/civil/decked_pi.py"),
            "mass_model_sha256":sha(root/"design/component-catalogue/src/osr_mech/civil/reference.py")})
    return thread.compile_thread(root,config,config_source=config_path,import_catalog=False,include_controller_execution=False)


def compile_package(root: Path = ROOT, source_data: dict | None = None) -> dict:
    source = source_data if source_data is not None else json.loads((root/SOURCE).read_text())
    if source["schema"] != "osr-civil-reference/1": raise ValueError("unknown civil reference schema")
    thread = load_thread()
    quantities, budgets, assets = layout_quantities(source,root)
    candidates = foundation_candidates(source["foundation_ground_class"], vibration_restricted=True)
    selection = compare_foundations(candidates["candidate_ids"], source.get("foundation_comparisons", []), source["foundation_site_inputs"])
    paths = [SOURCE, source["route_basis_path"], source["assurance_path"], "engineering/analysis/solver_results.py", "tools/automation/civil_reference.py", "tools/automation/connected_assurance.py",
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
        if name == "beam-sanity":
            from engineering.analysis.solver_results import extract_results
            exchanges = value["native_exchanges"]
            if len(exchanges) != 2*len(value["results"]): raise ValueError("native exchange coverage missing")
            for entry in exchanges:
                if entry["csv_path"] != entry["report"]["numerical_results_path"]: raise ValueError("native exchange path mismatch")
                for p,digest in entry["report"]["output_hashes"].items():
                    if value["output_hashes"].get(p) != digest: raise ValueError("native exchange output hash mismatch")
                extracted = extract_results(entry["report"],result_dir,entry["register"],entry["solver"])
                with controlled_path(result_dir,entry["csv_path"]).open(newline="") as handle:
                    recorded = list(csv.DictReader(handle))
                if len(recorded) != len(extracted): raise ValueError("native exchange row coverage mismatch")
                for actual, expected in zip(recorded,extracted):
                    if (any(actual[k] != expected[k] for k in ("asset_id","load_case_id","metric","unit"))
                        or not math.isclose(finite(actual["value"]),expected["value"],rel_tol=1e-9,abs_tol=1e-12)):
                        raise ValueError("recorded CSV/native solver output disagreement")
        if name == "drainage-sanity":
            for scenario,row in value["scenarios"].items():
                if row["input_sha256"] != sha(root/DESTINATION/"drainage"/f"{scenario}.inp"):
                    raise ValueError("stale drainage demonstration input; rerun --run-solvers")
        demonstrations[name] = value
        source_hashes[path.relative_to(root).as_posix()] = sha(path)
    graph = compile_civil_graph(root,source,thread)
    source_hashes.update(graph["source_hashes"])
    graph["drain_change_impact"] = thread.change_impact(graph,graph,["DRAIN-01"])
    return {"schema":"osr-civil-reference-report/1","id":source["id"],"status":source["status"],"release_ready":False,
            "authority_accepted":False,"independently_checked_design":False,"source_hashes":source_hashes,
            "layout":source["asset_register"],"lifting_budgets":budgets,"foundation_candidates":candidates,"foundation_comparison":selection,
            "quantities":quantities,
            "connections":source["connections"],"bearings":{**source["bearings"],"seat_count":quantities["bearing_seats_candidate"]},"construction_sequence":source["construction_sequence"],
            "comparator":{**source["comparator"],"span_options_m":quantities["span_lengths_m"]},"trackform_options":source["trackform_options"],"drainage_objects":source["drainage_objects"],
            "failure_modes":source["failure_modes"],"shared_failure_modes":[n for n in graph["nodes"] if n["kind"] == "failure_modes"],"site_inputs_required":source["site_inputs_required"],"references":source["references"],
            "demonstrations":demonstrations,"graph":graph}


def markdown(r: dict) -> str:
    q = r["quantities"]
    span_text = "/".join(f"{v:g}" for v in q["span_lengths_m"])
    lines = ["# Civil reference demonstration A", "", "**Status: awaiting site design, physical evidence and independent review. Release is blocked.**", "",
        f"The reference contains {q['beam_count']} beam assets with {span_text} m spans and {q['at_grade_route_length_m']:g} m of adjoining at-grade transition. It provides quantities, connection briefs, construction hold points, option comparisons and a connected civil FMEA. It is a review package for engineers and suppliers; it has no accepted construction drawings.", "",
        "## Layout and quantities", "", "| Asset | Family | Chainage (m) | Supports |", "|---|---|---:|---|"]
    for a in r["layout"]["assets"]: lines.append(f"| {a['asset_id']} | {a['variant_id']} | {a['from_station_m']}–{a['to_station_m']} | {', '.join(a['support_ids'])} |")
    lines += ["",f"{q['beam_count']} bare beams contain **{r['quantities']['bare_beam_concrete_m3']:.2f} m³** of envelope concrete over **{r['quantities']['deck_envelope_area_m2']:.1f} m²** of deck. Foundation, reinforcement, prestress and installed cost quantities remain unresolved. {q['elevated_support_lines']} elevated support lines are identified. The candidate arrangement has {q['bearing_seats_candidate']} bearing seats; capacities and fixity are unresolved.","", "## Mass and lifting", "", "| Family | Bare mass (kg) | Margin under 75 t (kg) | Complete lift |", "|---|---:|---:|---|"]
    for name,b in r["lifting_budgets"].items(): lines.append(f"| {name} | {b['bare_mass_kg']:,.1f} | {b['bare_margin_kg']:,.1f} | {b['status']} |")
    lines += ["", "Net diaphragms, bulk-density reinforcement adjustment, prestress steel, anchorages, embedded lifting hardware, attachments, retained temporary works, slings, spreader and hook/block masses must be measured or substantiated. The overlapping CAD diaphragm zones cannot be summed as additional fabrication concrete. The actual crane/launcher chart, configuration, radius, dynamic allowance, utilisation, centre of gravity, ground support and lateral stability must be reviewed.", "", "## Foundation and trackform comparison", "",f"Candidate foundations: {', '.join(r['foundation_candidates']['candidate_ids'])}. None is selected. A measured comparison must cover axial/lateral resistance, total and differential settlement, groundwater, chemistry, liquefaction/scour where relevant, utilities and installation constraints. Calcium-based treatment needs reviewed chemistry compatibility. Reinforced-soil approaches need railway deformation, stability and scour justification.","", "Ballasted track, slipformed slab and precast panels remain explicit alternatives. Compare settlement, drainage, local material and maintenance capability, repair possessions and whole-life cost for the layout-defined transition before selection.","", "## Conventional girder comparator", "", r["comparator"]["system"]+f" is retained for the {span_text} m span families. Supplier section, girder count, deck quantities and price are pending; no system is declared cheapest.",""]
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
    lines += ["", "The shared schema allocates the coupled drainage chain to these planned assets and responsibilities:", "",
        "| Failure / asset | Owner | Calculation or observation | Required response |", "|---|---|---|---|"]
    lines += [f"| {f['id']} / {f['item_id']} | {f['ownership']['responsible_role']} | {f['calculation_or_observation_reference']} | {f['required_response']} |" for f in r["shared_failure_modes"] if f["id"].startswith("CF-01")]
    lines += ["", "The physical hierarchy connects parts to subassemblies, the reference bay and the civil system. Foundation–bearing–track interfaces and the saturation common cause are explicit. Planned member occurrences link concrete mix revision, constituent batches, curing, transfer/lifting strength, test records and nonconformances to the member. The planned drainage inspection links its work order, model reassessment, effectiveness check and engineering handback to the same failure chain. These templates contain no manufactured members, measured strengths or completed maintenance."]
    lines += ["", "[Machine-readable report](report.json) contains the typed graph and drain-change trace. It uses the existing connected-assurance traversal, including both old and new relationships. The civil assembly is validated through the same configuration, ownership, effect, mitigation, evidence and decision schema as the component example. A drain change reaches formation, foundation, bearing and track failures, required operator response and blocked civil gates. All physical and independent evidence remains missing.", "", "## Unresolved site inputs", ""]
    lines += [f"- {s}." for s in r["site_inputs_required"]]
    lines += ["", "## Public references and reuse rights", "", "No external drawing or code was copied into this package. Record drawing-specific rights before incorporation; software licences do not grant rights to unrelated drawings.", "", "| Reference | Intended use | Rights/access status |", "|---|---|---|"]
    lines += [f"| [{s['id']}]({s['url']}) | {s['use']} | {s['reuse_rights']}; {s['retrieval_status']} |" for s in r["references"]]
    lines += ["", "## Reproduction", "", "From the repository root:", "", "```bash", ".venv/bin/python tools/automation/civil_reference.py --run-solvers", ".venv/bin/python tools/automation/civil_reference.py --check", ".venv/bin/python tools/automation/civil_reference.py --verify-native-replay", "```", "", "OpenSeesPy, PySWMM and native `ccx` are needed for replay. The default compiler and `--check` validate recorded files and provenance without running native solvers. The release gates require a separately reviewed, design-hash-bound asset register, per-asset numerical outputs and accepted limits. This concept register is deliberately pending and cannot satisfy them.", ""]
    return "\n".join(lines)


def transport_summary(r: dict) -> str:
    lines = ["# Transport and erection mass summary", "", "**Equipment selection and lifting release are pending.**", "",
        "This summary is generated from the layout and complete mass-budget fields. The 75 t product envelope and equipment capacity are separate requirements. A larger crane cannot waive the member envelope; an independently reviewed, mass-basis-bound deviation is required.", "",
        "| Family | Bare member (kg) | Complete member (kg) | Missing fields | Equipment check | Overall |", "|---|---:|---:|---|---|---|"]
    for name,b in r["lifting_budgets"].items():
        complete = f"{b['complete_member_mass_kg']:,.1f}" if b['complete_member_mass_kg'] is not None else "Unresolved"
        equipment = "Unresolved" if b['missing_inputs'] else "Passed" if b['equipment_capacity_met'] else "Failed"
        lines.append(f"| {name} | {b['bare_mass_kg']:,.1f} | {complete} | {', '.join(b['missing_inputs']) or 'None'} | {equipment} | {b['status']} |")
    lines += ["", "Confirm net detail masses, centre of gravity, transport axle loads/clearances, storage and transport support positions, lifting anchors/strength, lateral stability, temporary bracing, actual chart radius/configuration and ground support before release. Benchmark beam calculations do not qualify these stages. Earlier approximate handling guidance cannot establish feasibility of a complete member.", "", "[Complete controlled package](README.md) · [Machine-readable budgets and provenance](report.json)", ""]
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--run-solvers", action="store_true")
    parser.add_argument("--verify-native-replay", action="store_true")
    args = parser.parse_args()
    if sum((args.check,args.run_solvers,args.verify_native_replay)) > 1: parser.error("choose one of --check, --run-solvers or --verify-native-replay")
    if args.run_solvers:
        from engineering.analysis.benchmarks.civil_reference import run_beams, run_drainage
        output = ROOT/DESTINATION/"calculations"
        run_beams(output); run_drainage(output)
    report = compile_package()
    if args.verify_native_replay:
        from engineering.analysis.benchmarks.civil_reference import run_beams, run_drainage
        with tempfile.TemporaryDirectory(prefix="osr-civil-replay-") as folder:
            output = Path(folder)
            run_beams(output); run_drainage(output)
            for name in ("beam-sanity", "drainage-sanity"):
                actual = json.loads((output/f"{name}.json").read_text())
                expected = report["demonstrations"][name]
                if name == "beam-sanity":
                    for a,e in zip(actual["results"],expected["results"]):
                        for key in ("analytical_deflection_m","opensees_deflection_m","calculix_deflection_m"):
                            if not math.isclose(a[key],e[key],rel_tol=1e-6,abs_tol=1e-10): raise ValueError("native beam replay changed")
                else:
                    if actual["scenarios"] != expected["scenarios"]: raise ValueError("native drainage replay changed")
        print("Native beam and hydraulic outputs reproduced; no project qualification claimed.")
        return
    generated = {"report.json":json.dumps(report,indent=2,sort_keys=True)+"\n", "README.md":markdown(report), "transport-and-erection.md":transport_summary(report)}
    for name,contents in generated.items():
        path = ROOT/DESTINATION/name
        if args.check:
            if not path.is_file() or path.read_text() != contents: raise SystemExit(f"stale civil reference: {path}")
        else: path.write_text(contents)
    print("Civil reference package current; site design, physical qualification and independent acceptance pending.")


if __name__ == "__main__": main()
