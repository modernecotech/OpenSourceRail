"""Publish the separate assumption-bound conditional P1 journey study."""
from pathlib import Path
from hashlib import sha256
import gzip
import json
import shutil

from engineering.station_rail import ROOT
from engineering.station_rail.common import digest, encoded, identity
from . import conditional_journey_study as study, railway_publication

PRODUCER="engineering/design_search/conditional_journey_publication.py"
OUTPUT="docs/design-engine/conditional-journey-study"


def _case_row(case):
    return dict(name=case["case"],map_id=case["map_id"],
        force_map_evidence_kind=case["force_map"]["evidence_kind"],
        assumed_peak_force_N_per_car=case["assumption"]["peak_force_N_per_car"],
        assumed_peak_current_A_train=case["assumption"]["peak_current_A_train"],
        current_command_A=case["assumption"]["current_command_A"],
        rated_efficiency=case["assumption"]["rated_efficiency"],
        trajectory=case["trajectory_summary"],brake_fit_state=case["brake_fit_state"],
        physical_journey_completed=False,available_motor_map_id=None,test_only=True)


def _summary(records,index):
    cases_by_name={name:[] for name in ("low","base","high")}
    rows=[]
    for record in records:
        output=record["output"]
        cases=[_case_row(case) for case in output["cases"]]
        for case in cases:cases_by_name[case["name"]].append(case)
        rows.append(dict(candidate_id=output["candidate_id"],body_candidate_id=output["body_candidate_id"],
            bundle_definition_id=output["bundle_definition_id"],normal_accounted_mass_kg_per_car=output["normal_accounted_mass_kg_per_car"],
            rotating_equivalent_kg_per_car=output["rotating_equivalent_kg_per_car"],
            commanded_power_windows_m=output["powered_windows_m"],
            initial_force_for_target_acceleration_N_per_car=output["initial_force_for_target_acceleration_N_per_car"],
            assumed_current_fraction_of_base_limit=output["assumed_current_fraction_of_base_limit"],
            service_capacity_arithmetic=output["service_capacity_arithmetic"],cases=cases,
            evaluation_id=output["evaluation_id"],record_id=record["record_id"]))
    case_summary={}
    for name,rows_for_case in cases_by_name.items():
        trajectories=[r["trajectory"] for r in rows_for_case]
        case_summary[name]=dict(case_count=len(rows_for_case),
            journey_states={state:sum(t["state"]==state for t in trajectories)
                for state in sorted({t["state"] for t in trajectories})},
            berth_stops=sum(t["berth_stop"] is True for t in trajectories),
            maximum_positive_acceleration_m_s2=dict(
                minimum=min(t["maximum_positive_acceleration_m_s2"] for t in trajectories),
                maximum=max(t["maximum_positive_acceleration_m_s2"] for t in trajectories)),
            movement_time_s=dict(minimum=min(t["elapsed_s"] for t in trajectories),
                maximum=max(t["elapsed_s"] for t in trajectories)),
            maximum_abs_energy_residual_J=max(abs(t["energy_residual_J"] or 0.0) for t in trajectories),
            maximum_abs_electrical_work_residual_J=max(abs(t["electrical_work_residual_J"] or 0.0) for t in trajectories),
            all_test_only=all(r["test_only"] and r["available_motor_map_id"] is None
                and r["physical_journey_completed"] is False for r in rows_for_case))
    shifts=index["service_shift_context"]
    service=rows[0]["service_capacity_arithmetic"]
    return dict(schema="osr-conditional-journey-study-summary/1",study_id=index["study_id"],
        parent_campaign_id=index["contract"]["parent_campaign_id"],
        parent_contract_id=index["contract"]["parent_contract_id"],parent_run_id=index["contract"]["parent_run_id"],
        candidate_bundle_count=len(rows),conditional_case_count=sum(x["case_count"] for x in case_summary.values()),
        candidate_rows=rows,case_summary=case_summary,
        service_capacity_arithmetic=service,
        service_shift_context=shifts,
        physical_journey_count=0,engineering_validated_count=0,approved_for_manufacture_or_operation_count=0,
        integrated_selection=None,selected_reference_changed=False,
        completion_scope="All canonical current P1 bundles have low/base/high assumption-bound point-train design-study results; the repository physical-journey and acceptance states remain open.",
        limitations=list(index["open_limitations"]),physical_accepted=False,engineering_accepted=False,
        configuration_adopted=False,manufacturing_release=False,operating_release=False,
        physical_journey_completed=False)


def _readme(summary,index):
    stats=summary["case_summary"]
    assumptions=index["assumptions"]
    cases=assumptions["lim_assumptions"]
    lines=["# Conditional P1 journey design study","",
        f"This source-bound study evaluated **{summary['candidate_bundle_count']} canonical P1 bundles** from the current coordinated railway campaign: two separate primary-iron definitions for each of 14 body candidates. It generated **{summary['conditional_case_count']} low/base/high assumption cases** using each bundle's own mass, propulsion identity, braking interface and commanded power windows.","",
        "Each generated force/current/thermal map is labelled `synthetic-method-test` inside the reduced longitudinal method and retained as an assumption-only design-study input. The nested result keeps `test_only=true`, `available_motor_map_id=null`, and all physical journey, engineering, acceptance and release flags false. The required campaign journey result remains `not-run`.","",
        "## Assumptions and outcomes","",
        "| Case | Assumed peak thrust per car | Train current limit | Rated efficiency | Journey outcome | Berth stops | Maximum initial acceleration |",
        "|---|---:|---:|---:|---|---:|---:|"]
    for i,name in enumerate(cases["case_names"]):
        outcome=stats[name]
        states=", ".join(f"{k}: {v}" for k,v in outcome["journey_states"].items())
        lines.append(f"| {name} | {cases['peak_force_N_per_car'][i]/1000:.1f} kN | {cases['peak_current_A_train'][i]:.0f} A | {cases['rated_efficiency'][i]:.0%} | {states} | {outcome['berth_stops']}/{outcome['case_count']} | {outcome['maximum_positive_acceleration_m_s2']['minimum']:.3f}–{outcome['maximum_positive_acceleration_m_s2']['maximum']:.3f} m/s² |")
    lines += ["",
        "The base force assumption is 11.1 kN/car, equivalent to 222 kW/car at 20 m/s if that force were available there. The maps use a one-second stationary pre-excitation assumption, a current fraction derived from the base-case initial 0.4 m/s² force balance, and lumped route-level thermal inventory/cooling hypotheses. These are explicit model inputs, not LIM measurements or validated operating maps.","",
        "The low cases remain below the 0.4 m/s² acceleration target and take longer than the base cases. The base cases reach the declared two-metre berth tolerance using the unqualified candidate brake model. The high cases exceed the assumed controller's speed limit during the launch segment. These outcomes identify useful control and evidence work for the next design cycle.","",
        "## Service and shift context","",
        f"The candidate carries {summary['service_capacity_arithmetic']['places_per_car']} places per car ({summary['service_capacity_arithmetic']['seats_per_car']} seats plus {summary['service_capacity_arithmetic']['wheelchair_places_per_car']} wheelchair places), or {summary['service_capacity_arithmetic']['places_per_train']} places per six-car train. At the declared {summary['service_capacity_arithmetic']['target_headway_s']:.0f} s target, arithmetic capacity is {summary['service_capacity_arithmetic']['arithmetic_places_per_hour_direction']:.0f} places/hour/direction. The {summary['service_capacity_arithmetic']['dwell_s']:.0f} s dwell is carried separately. This calculation does not establish tail clearance, station occupation, fleet size, dwell performance or a protected headway.","",
        f"The existing Class C cost model's schedule assumptions are carried forward: production uses {summary['service_shift_context']['production_shifts_per_day']} {summary['service_shift_context']['production_hours_per_shift']}-hour shifts/day; civil work uses {summary['service_shift_context']['civil_shifts_per_day']} {summary['service_shift_context']['civil_hours_per_shift']}-hour shifts/day; operations cost cases cover {summary['service_shift_context']['operating_hours_per_day_cases']} hours/day with {summary['service_shift_context']['operations_shifts_per_day_cases']} shifts/day. The three-shift high case remains a cost assumption; this trajectory calculation does not validate staffing or round-the-clock operating duty.","",
        "## Exact interfaces and open limits","",
        "The study propagates each bundle's declared command windows without filling unpowered gaps. For this reference P1 case the command window is `[[0, 500]] m`; the bundle's separately defined wayside installation intervals are not treated as proof that every installed interval is energized during this trip. The point-train model also omits train-tail clearance, electrical section interaction, current protection, repeated 120-second thermal duty, charging/reserve, adverse grade/headwind, crowd loading, faults, recovery, passenger protection, and actual site geometry.","",
        "Normal mass is the candidate's accounted loaded-mass hypothesis; complete installed mass remains unknown. Braking and adhesion are unqualified hypotheses. All physical journeys, engineering validations and approvals remain open.","",
        "## Reproduction","",
        "```bash","./osr design journey-study verify --replay","./osr design journey-study publish","```","",
        "[Summary](summary.json) · [Candidate index](candidate-index.json) · [Source-bound study index](study-index.json) · [Payload manifest](manifest.json)",""]
    return "\n".join(lines)


def build(root=ROOT,output=None):
    root=Path(root);out=root/OUTPUT if output is None else Path(output)
    verification=study.run(root);study_id=verification["study_id"]
    run_folder=root/study.OUTPUT/study_id
    result=json.loads((run_folder/"result.json").read_bytes())
    assumptions=study.specification(root)
    cases=[]
    candidate_records=[]
    source_rows=[]
    for row in result["rows"]:
        bundle_id=row["bundle_id"];source=run_folder/(bundle_id+".json.gz")
        relative="candidates/"+bundle_id+".json.gz"
        target=out/relative;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,target)
        h=digest(target);candidate_records.append(dict(bundle_id=bundle_id,body_candidate_id=row["output"]["body_candidate_id"],
            bundle_definition_id=row["bundle_definition_id"],record_id=row["record_id"],artifact=relative,sha256=h,
            output_evaluation_id=row["output"]["evaluation_id"]))
        source_rows.append(row)
    index=dict(schema="osr-conditional-journey-study-index/1",study_id=study_id,
        contract=result["contract"],result_sha256=result["result_sha256"],
        assumption_id=assumptions["assumption_id"],assumptions=assumptions,
        source_sha256=result["source_sha256"],service_shift_context=result["service_shift_context"],
        open_limitations=result["open_limitations"],candidate_records=candidate_records)
    index["index_id"]=identity(index)
    s=_summary(source_rows,index);s["summary_id"]=identity(s)
    out.mkdir(parents=True,exist_ok=True)
    (out/"study-index.json").write_bytes(encoded(index))
    (out/"candidate-index.json").write_bytes(encoded(candidate_records))
    (out/"summary.json").write_bytes(encoded(s))
    (out/"README.md").write_text(_readme(s,index))
    sources={**result["source_sha256"],PRODUCER:digest(root/PRODUCER)}
    if any(digest(root/name)!=h for name,h in sources.items()):
        raise ValueError("Conditional-study source epoch changed during publication")
    manifest=dict(schema="osr-conditional-journey-publication/1",study_id=study_id,
        source_sha256=sources,
        files_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob("*") if p.is_file()},
        physical_journey_completed=False,physical_accepted=False,engineering_accepted=False,
        configuration_adopted=False,manufacturing_release=False,operating_release=False)
    manifest["manifest_id"]=identity(manifest);(out/"manifest.json").write_bytes(encoded(manifest))
    return verify(root,out)


def verify(root=ROOT,output=None,*,replay=False):
    root=Path(root);out=root/OUTPUT if output is None else Path(output)
    manifest=json.loads((out/"manifest.json").read_bytes())
    if manifest.get("manifest_id")!=identity({k:v for k,v in manifest.items() if k!="manifest_id"}):
        raise ValueError("Conditional journey publication manifest identity differs")
    if any(digest(root/name)!=h for name,h in manifest["source_sha256"].items()):
        raise ValueError("Conditional journey source epoch changed")
    actual={p.relative_to(out).as_posix():digest(p) for p in out.rglob("*") if p.is_file() and p!=out/"manifest.json"}
    if manifest.get("files_sha256")!=actual:raise ValueError("Conditional journey publication payload changed")
    index=json.loads((out/"study-index.json").read_bytes())
    if (index.get("index_id")!=identity({k:v for k,v in index.items() if k!="index_id"})
            or index.get("study_id")!=manifest.get("study_id")
            or any(manifest.get("source_sha256",{}).get(k)!=v
                   for k,v in index.get("source_sha256",{}).items())):
        raise ValueError("Conditional study index, source epoch or publication identity differs")
    coupled=Path(root)/railway_publication.OUTPUT
    railway_publication.verify(root,coupled)
    parent_manifest=json.loads((coupled/"manifest.json").read_bytes())
    parent_summary=json.loads((coupled/"summary.json").read_bytes())
    execution=json.loads((coupled/"execution.json").read_bytes())
    bundles=json.loads(gzip.decompress((coupled/"bundles.json.gz").read_bytes()))
    p1={b["candidate_id"]:b for b in bundles if b.get("family_id")=="P1"}
    if (index["contract"].get("parent_campaign_id")!=parent_summary.get("campaign_id")
            or index["contract"].get("parent_contract_id")!=parent_summary.get("contract_id")
            or index["contract"].get("parent_run_id")!=execution.get("run_id")
            or set(index["contract"].get("bundle_ids",[]))!=set(p1)
            or len(p1)!=28):
        raise ValueError("Conditional study does not bind to the current exact P1 campaign")
    rows=[];seen=set()
    for item in index["candidate_records"]:
        artifact=out/item["artifact"]
        if digest(artifact)!=item["sha256"]:raise ValueError("Conditional candidate archive changed")
        record=json.loads(gzip.decompress(artifact.read_bytes()))
        bundle=p1.get(item["bundle_id"])
        output=record.get("output",{})
        if (bundle is None or item["bundle_id"] in seen or record.get("record_id")!=item["record_id"]
                or record.get("record_id")!=identity({k:v for k,v in record.items() if k!="record_id"})
                or record.get("bundle_id")!=item["bundle_id"]
                or record.get("bundle_definition_id")!=bundle.get("definition_id")
                or output.get("evaluation_id")!=item["output_evaluation_id"]
                or output.get("evaluation_id")!=identity({k:v for k,v in output.items() if k!="evaluation_id"})
                or output.get("candidate_id")!=item["bundle_id"]
                or output.get("body_candidate_id")!=bundle.get("body_candidate_id")):
            raise ValueError("Conditional candidate result is mixed, changed or unbound")
        seen.add(item["bundle_id"]);rows.append(record)
        for case in output.get("cases",[]):
            force_map=case.get("force_map",{});scenario=case.get("scenario",{});forward=case.get("forward",{})
            if (force_map.get("evaluation_id")!=identity({k:v for k,v in force_map.items() if k!="evaluation_id"})
                    or force_map.get("candidate_id")!=item["bundle_id"]
                    or force_map.get("scenario_id")!=scenario.get("scenario_id")
                    or force_map.get("assumption_id")!=index.get("assumption_id")
                    or scenario.get("scenario_id")!=identity({k:v for k,v in scenario.items() if k!="scenario_id"})
                    or forward.get("method_result_id")!=identity({k:v for k,v in forward.items() if k!="method_result_id"})
                    or forward.get("test_only") is not True or forward.get("available_motor_map_id") is not None
                    or forward.get("physical_journey_completed") is not False):
                raise ValueError("Assumed force map or nested method result is changed or improperly admitted")
    summary=json.loads((out/"summary.json").read_bytes())
    expected=_summary(rows,index)
    if summary!={**expected,"summary_id":identity(expected)}:
        raise ValueError("Conditional journey summary differs from exact candidate receipts")
    if any(manifest.get(k) is not False for k in ("physical_journey_completed","physical_accepted","engineering_accepted","configuration_adopted","manufacturing_release","operating_release")):
        raise ValueError("Conditional journey publication cannot grant validation or release")
    if replay:
        for record in rows:
            if record["output"]!=study.evaluate_bundle(p1[record["bundle_id"]],study.specification(root)):
                raise ValueError("Conditional candidate does not reproduce from current source and declared assumptions")
    return dict(verified=True,manifest_id=manifest["manifest_id"],study_id=index["study_id"],
        candidate_count=len(rows),conditional_cases=sum(len(x["output"]["cases"]) for x in rows),
        physical_journeys=0,engineering_validated=0,approved_for_manufacture_or_operation=0,
        physical_journey_completed=False,physical_accepted=False,engineering_accepted=False,
        configuration_adopted=False,manufacturing_release=False,operating_release=False)
