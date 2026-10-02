#!/usr/bin/env python3
"""Build a subsystem test dossier, quantitative screens and scoped decision readiness."""
from __future__ import annotations

import argparse
import copy
import csv
from datetime import date, datetime, timedelta, timezone
import itertools
import json
from pathlib import Path
import subprocess
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from engineering.analysis import rams
from tools.automation import connected_assurance as thread

PLAN = "lib/templates/subsystem-qualification.json"
OUTPUT = "engineering/assurance/battery-cooling/qualification-report"
STAGES = ("requirements", "design_verification", "physical_qualification", "integration", "independent_review", "operating_conditions")
COLUMNS = ("time_s", "temperature_c", "ambient_c", "flow_l_min", "pressure_kpa", "fault_active", "detected", "isolation", "derate")


def require(row: dict, *fields: str) -> None:
    if any(row.get(field) in (None, "", [], {}) for field in fields):
        raise ValueError(f"{row.get('id', 'record')} missing {', '.join(fields)}")


def response_trace(rows: list[dict], onset: float | None, test: dict | None) -> dict:
    """Establish normal operation, fault and ordered rising responses from samples."""
    gaps, transitions = [], {}
    if onset is None:
        if (test or {}).get("fault_required") or any(row["fault_active"] for row in rows):
            gaps.append("Fault onset is missing or inconsistent with a normal-operation test.")
        if test is not None and any(row[key] for row in rows for key in ("detected","isolation","derate")):
            gaps.append("Normal-operation diagnostic/protection preconditions are not demonstrated.")
        return {"state": "invalid" if gaps else "normal-operation", "blockers": gaps, "transitions_s": transitions}
    if test is not None and not test.get("fault_required"):
        gaps.append("Normal-operation test contains an injected fault.")
    baseline = [row for row in rows if row["time_s"] < onset]
    initial = (test or {}).get("preconditions", {})
    expected = {"fault_active": 0, "detected": 0, "isolation": 0, "derate": 0}
    expected.update(initial.get("digital_state", {}))
    if not set(expected) <= {"fault_active", "detected", "isolation", "derate"} or any(type(value) is not int or value not in (0, 1) for value in expected.values()):
        raise ValueError("unsupported response precondition channels or values")
    if not baseline:
        gaps.append("No normal-operation samples precede fault injection.")
    elif any(row[key] != value for row in baseline for key, value in expected.items()):
        gaps.append("Pre-fault diagnostic/protection state differs from scenario preconditions.")
    if test is not None:
        duration, flow = initial.get("minimum_duration_s"), initial.get("min_flow_l_min")
        if duration is None or flow is None:
            gaps.append("Scenario normal-operation duration/flow preconditions are unresolved.")
        else:
            rams.number(duration, "precondition duration", minimum=1e-12)
            rams.number(flow, "precondition flow", minimum=1e-12)
            if not baseline or baseline[-1]["time_s"]-baseline[0]["time_s"] < duration or any(row["flow_l_min"] < flow for row in baseline):
                gaps.append("Normal-operation duration or flow precondition is not demonstrated.")
    sequence = (test or {}).get("response_sequence", ["detected", "isolation"])
    if not sequence or len(sequence)!=len(set(sequence)) or not set(sequence)<={"detected", "isolation", "derate"}:
        raise ValueError("invalid scenario response sequence")
    required = {"fault_active", *sequence}
    for channel in required:
        transitions[channel] = next((b["time_s"] for a,b in zip(rows, rows[1:])
                                     if a[channel]==0 and b[channel]==1 and b["time_s"]>=onset), None)
        if channel != "fault_active" and any(row[channel] for row in baseline):
            gaps.append(f"{channel}: response was already asserted before the fault.")
        if transitions[channel] is None:
            gaps.append(f"{channel}: post-onset rising transition is not demonstrated.")
    ordered = [transitions.get(channel) for channel in ["fault_active", *sequence]]
    # Equal sample times cannot establish the claimed causal order.
    if all(value is not None for value in ordered) and any(a>=b for a,b in zip(ordered,ordered[1:])):
        gaps.append("Fault, diagnostic and protection transitions are not observed in the required order.")
    if test is not None:
        sample_limit = test.get("limits", {}).get("maximum_sample_gap_s")
        timing = [value for key,value in test.get("limits", {}).items() if key.endswith("_delay_s") and value is not None]
        sample_gap = max(b["time_s"]-a["time_s"] for a,b in zip(rows,rows[1:]))
        if sample_limit is None:
            gaps.append("Reviewed sampling resolution is unresolved.")
        else:
            rams.number(sample_limit,"sampling resolution",minimum=1e-12)
            if sample_gap > sample_limit or (timing and sample_limit > min(timing)):
                gaps.append("Sampling resolution cannot establish the fault-response timing criteria.")
    return {"state": "invalid" if gaps else "transitions-observed", "blockers": sorted(set(gaps)), "transitions_s": transitions}


def measurements(root: Path, run: dict, test: dict | None = None) -> tuple[list[dict], dict]:
    require(run, "id", "test_id", "raw_path", "raw_sha256", "configuration_fingerprint", "rig_serial",
            "specimen_serials", "performed_by", "performed_at", "procedure_revision", "channel_instruments", "origin")
    performed = datetime.fromisoformat(run["performed_at"].replace("Z", "+00:00"))
    if performed.tzinfo is None:
        raise ValueError("measurement timestamp requires a timezone")
    path = thread.source(root, run["raw_path"])
    actual_hash = thread.digest(root, run["raw_path"])
    if actual_hash != run["raw_sha256"]:
        raise ValueError(f"{run['id']}: raw measurement hash changed")
    with path.open(newline="") as stream:
        reader = csv.DictReader(stream)
        if not reader.fieldnames or len(reader.fieldnames) != len(set(reader.fieldnames)) or not set(COLUMNS) <= set(reader.fieldnames):
            raise ValueError("measurement CSV lacks required channels")
        rows = [{key:rams.number(float(row[key]), key, minimum=-273.15 if key.endswith("_c") else 0)
                 for key in COLUMNS} for row in reader]
    if len(rows) < 2 or any(a["time_s"] >= b["time_s"] for a,b in zip(rows, rows[1:])):
        raise ValueError("measurements require at least two strictly increasing sample times")
    if any(row[key] not in (0, 1) for row in rows for key in ("fault_active", "detected", "isolation", "derate")):
        raise ValueError("digital measurement channels must be zero or one")
    onset = run.get("fault_onset_s")
    if onset is not None:
        onset = rams.number(onset, "fault onset")
        if not rows[0]["time_s"] <= onset <= rows[-1]["time_s"]:
            raise ValueError("fault onset outside measured interval")
        if not any(row["fault_active"] for row in rows) or any(row["fault_active"] and row["time_s"] < onset for row in rows):
            raise ValueError("fault record disagrees with commanded onset")
    trace = response_trace(rows, onset, test)
    def delay(channel):
        observed = trace["transitions_s"].get(channel) if not trace["blockers"] else None
        return observed - onset if observed is not None else None
    fault_rows = [row for row in rows if row["fault_active"]]
    return rows, {"max_temperature_c":max(row["temperature_c"] for row in rows),
                  "min_flow_l_min":min(row["flow_l_min"] for row in rows),
                  "max_fault_flow_l_min":max((row["flow_l_min"] for row in fault_rows), default=None),
                  "max_detection_delay_s":delay("detected"), "max_isolation_delay_s":delay("isolation"),
                  "duration_s":rows[-1]["time_s"]-rows[0]["time_s"],
                  "maximum_sample_gap_s":max(b["time_s"]-a["time_s"] for a,b in zip(rows,rows[1:])),
                  "response_validation": trace}


def quantitative(inputs: dict) -> dict:
    if inputs.get("schema") != "osr-rams-study/1":
        raise ValueError("unsupported RAMS study schema")
    thermal = rams.thermal_screen(inputs["thermal"], inputs["sample_times_s"])
    tree = rams.fault_tree_screen(inputs["fault_tree"], inputs["events"], inputs["mission_h"],
                                  independence=inputs["primitive_independence"] == "assumed-for-screening")
    inspection = inputs["inspection"]
    rate = rams.interval(inspection["rate_per_h"], "inspection rate",unit="1/h")
    interval = rams.interval(inspection["interval_h"], "inspection interval",unit="h")
    target = rams.interval(inspection["maximum_average_exposure"], "latent exposure budget",unit="probability")
    latent = {"state":"input-evidence-open"}
    if rate and interval and target:
        latent = {"state":"screening-unvalidated", "average_latent_exposure":[rams.latent_exposure(rate[i],interval[i]) for i in (0,1)],
                  "maximum_interval_h_at_upper_rate":rams.inspection_interval(rate[1],target[0]),
                  "limitations":"Perfect periodic proof-test detection and restoration, constant hardware rate, uniform demand timing; actual diagnostic coverage and repair exposure remain open."}
    maintenance = inputs["maintenance"]
    ranges = [rams.interval(maintenance[key], key,unit="1/h" if key=="rate_per_h" else "h") for key in ("rate_per_h", "repair_h", "turnaround_h")]
    logistics = {"state":"input-evidence-open"}
    if all(ranges):
        corners = [rams.maintenance_screen(maintenance["fleet"], *values,
                   maintenance["maximum_mean_wait_h"],maintenance["maximum_stockout_probability"])
                   for values in itertools.product(*ranges)]
        logistics = {"state":"planning-screen", "repair_crews":[min(row["repair_crews"] for row in corners),max(row["repair_crews"] for row in corners)],
                     "minimum_spares":[min(row["minimum_spares"] for row in corners),max(row["minimum_spares"] for row in corners)],
                     "limitations":corners[0]["limitations"]}
    brake = inputs["braking"]
    reaction = rams.interval(brake["reaction_s"], "brake delay",unit="s")
    deceleration = rams.interval(brake["one_channel_deceleration_m_s2"], "brake deceleration",unit="m/s2")
    braking = {"state":"input-evidence-open"}
    if reaction and deceleration:
        cases = [rams.braking_screen(brake["available_distance_m"], delay, decel) for delay,decel in itertools.product(reaction,deceleration)]
        braking = {"state":"illustrative-restriction-screen", "maximum_speed_km_h":[min(row["maximum_speed_km_h"] for row in cases),max(row["maximum_speed_km_h"] for row in cases)],
                   "limitations":cases[0]["limitations"]}
    options = []
    for option in inputs["design_options"]:
        changed = copy.deepcopy(inputs["events"])
        factor = rams.number(option["rate_multiplier"], "option failure-rate multiplier")
        for event in changed:
            if event["id"] == "EV-PUMP" and event["failure_rate_per_h"]["low"] is not None:
                for key in ("low", "high"):
                    event["failure_rate_per_h"][key] *= factor
        analysis = rams.fault_tree_screen(inputs["fault_tree"],changed,inputs["mission_h"],independence=inputs["primitive_independence"] == "assumed-for-screening")
        changed_thermal = copy.deepcopy(inputs["thermal"])
        factor = rams.number(option["residual_conductance_multiplier"], "option conductance multiplier")
        if changed_thermal["conductance_w_k"]["low"] is not None:
            for key in ("low", "high"):
                changed_thermal["conductance_w_k"][key] *= factor
        options.append({"id":option["id"], "title":option["title"], "illustrative_cost":rams.number(option["cost"],"option cost"),
                        "top_event_probability":analysis["mission_top_event_probability"],
                        "time_to_limit_s":rams.thermal_screen(changed_thermal,inputs["sample_times_s"])["time_to_limit_s"],
                        "decision":"comparison-only; uncertain supplier performance and cost require evidence"})
    return {"evidence_basis":inputs["evidence_basis"], "thermal":thermal,
            "physical_thermal":rams.thermal_screen(inputs["physical_thermal"],inputs["sample_times_s"]), "fault_tree":tree,
            "top_event":inputs["top_event"], "inspection":latent, "maintenance":logistics,
            "degraded_braking":braking, "design_options":options, "release_authority":False}


def authenticated_reviews(root: Path, records: list[dict], policy_path: Path | None,
                          evidence_fingerprint: str, configuration_fingerprint: str, authors: set[str], today: date) -> tuple[list[dict], list[str]]:
    if not policy_path:
        return [], ["Independent review policy and signed decisions are not supplied."]
    policy = json.loads(policy_path.read_text())
    accepted, gaps = [], []
    for record in records:
        require(record,"envelope_path","signature_path")
        envelope_path = thread.source(root, record["envelope_path"])
        signature_path = thread.source(root, record["signature_path"])
        envelope = json.loads(envelope_path.read_text())
        identity = policy.get("reviewers", {}).get(envelope.get("reviewer"), {})
        if envelope.get("schema") != "osr-subsystem-review/1" or not identity.get("enabled"):
            gaps.append("Unknown review schema or unauthorized reviewer.")
            continue
        if envelope.get("reviewer") in authors or envelope.get("role") not in identity.get("roles", []):
            gaps.append("Review independence or reviewer role is invalid.")
            continue
        if envelope.get("evidence_fingerprint") != evidence_fingerprint or envelope.get("configuration_fingerprint") != configuration_fingerprint:
            gaps.append("Signed review binds an earlier evidence/configuration baseline.")
            continue
        if envelope.get("disposition") != "accepted" or not envelope.get("reference") or not envelope.get("valid_until"):
            gaps.append("Review does not record acceptance with a reference.")
            continue
        if today > date.fromisoformat(envelope["valid_until"]):
            gaps.append("Signed review validity has expired.")
            continue
        key = (policy_path.parent / identity["public_key"]).resolve()
        import hashlib
        if hashlib.sha256(key.read_bytes()).hexdigest() != identity.get("public_key_sha256"):
            gaps.append("Reviewer public key differs from the trusted policy.")
            continue
        verified = subprocess.run(["openssl","pkeyutl","-verify","-pubin","-inkey",str(key),"-rawin",
                                   "-in",str(envelope_path),"-sigfile",str(signature_path)],capture_output=True,timeout=10)
        if verified.returncode:
            gaps.append("Review signature is invalid.")
            continue
        accepted.append(envelope)
    return accepted, gaps


def instant(value: str, *, end_of_day: bool = False) -> datetime:
    """Date-only certificate bounds cover UTC days; acquisition times need offsets."""
    if len(value)==10:
        result=datetime.combine(date.fromisoformat(value), datetime.min.time(), timezone.utc)
        return result+timedelta(days=1,microseconds=-1) if end_of_day else result
    result=datetime.fromisoformat(value.replace("Z", "+00:00"))
    if result.tzinfo is None:
        raise ValueError("calibration timestamps require a timezone")
    return result.astimezone(timezone.utc)


def calibration_period(record: dict) -> tuple[datetime, datetime] | None:
    if not record.get("valid_from") or not record.get("valid_until"):
        return None
    start, end=instant(record["valid_from"]),instant(record["valid_until"],end_of_day=True)
    if start>end:
        raise ValueError("calibration start exceeds end")
    return start,end


def allocation_metrics(inputs: dict, analysis: dict, *, model_validated: bool, valid_evidence_ids: set[str]) -> dict:
    """Allowlisted result links retain units, conditions and parameter provenance."""
    events={row["id"]:row for row in inputs["events"]}
    pump=events.get("EV-PUMP", {})
    conditions=inputs.get("operating_conditions")
    def supported(parameters):
        return bool(parameters) and all(row.get("basis") in {"measured","supplier-data"} and row.get("evidence_ids")
                                        and set(row["evidence_ids"])<=valid_evidence_ids for row in parameters)
    def result(path,unit,bounds,parameters,*,context=conditions,qualified=True):
        return {"result_path":path,"unit":unit,"bounds":bounds,"operating_conditions":context,
                "evidence_qualified":bool(qualified and supported(parameters))}
    metrics={}
    for metric,field,unit in (("pump_failure_rate","failure_rate_per_h","1/h"),("pump_mean_repair_time","repair_h","h")):
        parameter=pump.get(field)
        if parameter:
            bounds=rams.interval(parameter,metric,unit=unit)
            metrics[metric]=result(f"events.EV-PUMP.{field}",unit,list(bounds) if bounds else None,[parameter])
    tree=analysis["fault_tree"]
    used=rams.tree_events(inputs["fault_tree"])
    parameters=[events[identifier][field] for identifier in sorted(used) for field in ("failure_rate_per_h","repair_h")]
    for metric,path,mission in (("function_availability","steady_state_availability",False),("mission_failure_probability","mission_top_event_probability",True)):
        context={**conditions,"mission_h":inputs["mission_h"]} if conditions and mission else conditions
        metrics[metric]=result("fault_tree."+path,"probability",tree.get(path),parameters,context=context,
                               qualified=not tree.get("unknown_events") and tree["state"]!="dependency-evidence-open")
    physical=analysis["physical_thermal"]
    metrics["thermal_time_to_limit"]=result("physical_thermal.time_to_limit_s","s",physical.get("time_to_limit_s"),
                                          list(inputs["physical_thermal"].values()),qualified=model_validated and not physical.get("some_cases_do_not_reach_limit"))
    return metrics


def assess_allocation(row: dict, metrics: dict) -> dict:
    """Meet a target only when the complete supported uncertainty envelope meets it."""
    result={"allocation_id":row["id"],"metric":row.get("metric"),"target":row.get("target"),
            "unit":row.get("unit"),"comparison":row.get("comparison"),"state":"undetermined",
            "numerical_state":"undetermined","uncertainty_treatment":"all-bounds","reasons":[]}
    if row.get("target") is not None:
        rams.number(row["target"],"RAMS target")
    metric=metrics.get(row.get("metric"))
    if metric is None:
        result["reasons"].append("Defined metric and linked quantitative result are unresolved.")
        return result
    result.update(result_path=metric["result_path"],bounds=metric["bounds"],result_operating_conditions=metric["operating_conditions"])
    if row.get("unit") != metric["unit"] or row.get("result_path") != metric["result_path"]:
        result["reasons"].append("Metric units or result link do not match the allocation.")
    if not row.get("operating_conditions") or row["operating_conditions"] != metric["operating_conditions"]:
        result["reasons"].append("Allocated operating conditions do not match the analysed conditions.")
    if row.get("uncertainty_treatment") != "all-bounds":
        result["reasons"].append("Conservative all-bounds uncertainty treatment is required.")
    if row.get("comparison") not in {">=","<="} or row.get("target") is None or row.get("review_state") != "reviewed":
        result["reasons"].append("RAMS target, comparison or allocation review remains open.")
    bounds=metric["bounds"]
    if bounds is None:
        result["reasons"].append("Quantitative result is unresolved.")
    elif not result["reasons"]:
        low,high=bounds
        target=row["target"]
        if metric["unit"]=="probability" and target>1:
            raise ValueError("RAMS probability target exceeds one")
        if row["comparison"]=="<=":
            result["numerical_state"]="met" if high<=target else "not-met" if low>target else "undetermined"
        else:
            result["numerical_state"]="met" if low>=target else "not-met" if high<target else "undetermined"
        if result["numerical_state"]=="undetermined":
            result["reasons"].append("Uncertainty envelope overlaps the acceptance target.")
    if not metric["evidence_qualified"]:
        result["reasons"].append("Result uses assumptions, unknown events or an unvalidated model.")
    if not result["reasons"]:
        result["state"]=result["numerical_state"]
    return result


def assurance_findings(graph: dict, plan: dict, reviews: list[dict] | None = None) -> dict:
    """Scope children/dependencies and their propagated assurance obligations."""
    nodes={row["id"]:row for row in graph["nodes"]}
    scope=plan.get("assurance_scope", {})
    roots={plan["subject_id"], *scope.get("additional_record_ids", [])}
    if roots-set(nodes):
        raise ValueError("unknown qualification assurance scope record")
    pending=list(roots)
    while pending:
        subject=pending.pop()
        for edge in graph["edges"]:
            if edge["to"]==subject and edge["relation"] in {"part_of","depends_on"} and edge["from"] not in roots:
                roots.add(edge["from"]);pending.append(edge["from"])
    records=set(thread.change_impact(graph,graph,sorted(roots))["trace_paths"])
    exclusions={row["id"]:row for row in scope.get("exclusions", [])}
    if len(exclusions)!=len(scope.get("exclusions", [])):
        raise ValueError("duplicate assurance exclusion")
    findings=[]
    for identifier in sorted(records):
        for message in sorted(set(graph["gaps"].get(identifier, []))):
            finding_id=thread.fingerprint({"record_id":identifier,"blocker":message})
            stage={"requirements":"requirements","obligations":"requirements","occurrences":"physical_qualification",
                   "incidents":"operating_conditions","configurations":"design_verification"}.get(nodes[identifier]["kind"],"design_verification")
            if nodes[identifier]["kind"]=="decisions":
                stage={"G1":"requirements","G2":"design_verification","G3":"physical_qualification","G4":"integration"}[nodes[identifier]["gate"]]
            if nodes[identifier]["kind"]=="evidence":
                stage="physical_qualification" if nodes[identifier]["verification_class"] in {"physical-qualification","process-evidence"} else "design_verification"
            disposition="open"
            exclusion=exclusions.get(finding_id)
            if exclusion:
                require(exclusion,"id","record_id","rationale","accountable_owner","author","reviewer","review_reference","graph_fingerprint")
                if exclusion["record_id"]!=identifier or exclusion["graph_fingerprint"]!=graph["fingerprint"] or exclusion["author"]==exclusion["reviewer"]:
                    disposition="invalid-exclusion"
                else:
                    disposition="exclusion-proposed"
                    approved=[row for row in reviews or [] if finding_id in row.get("approved_exclusion_ids", [])]
                    assessor=any(row["role"]=="assessor" and row["reviewer"]==exclusion["reviewer"] and row["reference"]==exclusion["review_reference"] for row in approved)
                    authority=any(row["role"]=="design-authority" for row in approved)
                    if assessor and authority:
                        disposition="excluded-by-authenticated-review"
            findings.append({"id":finding_id,"record_id":identifier,"kind":nodes[identifier]["kind"],"message":message,
                             "stage":stage,"disposition":disposition})
    if set(exclusions)-{row["id"] for row in findings}:
        raise ValueError("assurance exclusion does not identify a current scoped blocker")
    return {"graph_fingerprint":graph["fingerprint"],"roots":sorted(roots),"record_ids":sorted(records),"findings":findings}


def compile_package(root: Path = ROOT, plan: dict | None = None, *, today: date | None = None,
                    review_policy: Path | None = None) -> dict:
    plan = copy.deepcopy(plan if plan is not None else json.loads(thread.source(root,PLAN).read_text()))
    today = today or date.today()
    if plan.get("schema") != "osr-subsystem-qualification/1":
        raise ValueError("unsupported subsystem qualification schema")
    if plan["scope"].get("kind") not in {"reference","deployment"}:
        raise ValueError("qualification scope must be reference or deployment")
    graph = thread.compile_thread(root,today=today)
    nodes = {row["id"]:row for row in graph["nodes"]}
    def ref(identifier, kinds):
        if identifier not in nodes or nodes[identifier]["kind"] not in kinds:
            raise ValueError(f"uncontrolled qualification reference: {identifier}")
        return nodes[identifier]
    ref(plan["subject_id"], {"design_items"})
    cfg = ref(plan["configuration_id"], {"configurations"})
    configuration_fingerprint = thread.fingerprint(cfg)
    inputs = json.loads(thread.source(root,plan["rams_input_path"]).read_text())
    hashes = {**graph["source_hashes"], PLAN:thread.digest(root,PLAN), plan["rams_input_path"]:thread.digest(root,plan["rams_input_path"]),
              "engineering/analysis/rams.py":thread.digest(root,"engineering/analysis/rams.py"),
              "tools/automation/subsystem_qualification.py":thread.digest(root,"tools/automation/subsystem_qualification.py")}
    blockers = {stage:[] for stage in STAGES}
    input_evidence = {row["id"]:row for row in plan.get("input_evidence",[])}
    if len(input_evidence) != len(plan.get("input_evidence",[])):
        raise ValueError("duplicate parameter evidence IDs")
    valid_evidence_ids = set()
    for row in input_evidence.values():
        require(row,"id","path","sha256","review_reference","valid_until")
        hashes[row["path"]] = thread.digest(root,row["path"])
        if hashes[row["path"]] != row["sha256"] or today > date.fromisoformat(row["valid_until"]):
            blockers["design_verification"].append(f"{row['id']}: parameter evidence changed or expired")
        else:
            valid_evidence_ids.add(row["id"])
    if (inputs.get("operating_conditions") or {}).get("configuration_id") != cfg["id"]:
        blockers["design_verification"].append("RAMS result operating conditions are not bound to the qualification configuration.")
    def parameter_evidence(value):
        if isinstance(value,dict):
            if value.get("basis") in {"measured","supplier-data"}:
                for identifier in value.get("evidence_ids",[]):
                    if identifier not in input_evidence:
                        raise ValueError(f"uncontrolled quantitative input evidence: {identifier}")
            for child in value.values():
                parameter_evidence(child)
        elif isinstance(value,list):
            for child in value:
                parameter_evidence(child)
    parameter_evidence(inputs)
    parameter_evidence(plan["tests"])
    for row in plan["allocations"]:
        ref(row["system_item_id"], {"design_items"})
        for identifier in row["allocated_to"]:
            ref(identifier,{"design_items","interfaces","functions"})
        for identifier in row["requirement_ids"]:
            ref(identifier,{"requirements"})
            if graph["gaps"].get(identifier):
                blockers["requirements"].append(f"{identifier}: requirement review remains open")
        for identifier in row["hazard_ids"]:
            ref(identifier,{"hazards"})
        if row["target"] is None or row["review_state"] != "reviewed":
            blockers["requirements"].append(f"{row['id']}: RAMS allocation/target review open")
    for event in inputs["events"]:
        ref(event["failure_mode_id"], {"failure_modes"})
    for row in plan["common_causes"]:
        for identifier in row["item_ids"]:
            ref(identifier,{"design_items"})
        if row["event_id"] not in {event["id"] for event in inputs["events"]}:
            raise ValueError("common cause references an unknown event")
        if row["review_state"] != "reviewed":
            blockers["design_verification"].append(f"{row['id']}: common-cause assessment open")
    if graph["gaps"].get(cfg["id"]):
        for stage in STAGES:
            blockers[stage].append("Frozen engineering configuration is stale.")
    rig = plan["rig"]
    if not rig["serial_number"] or any(not value for value in rig["selected_components"].values()):
        blockers["physical_qualification"].append("Selected components and real rig serial are missing.")
    expected_serials = rig.get("specimen_serials", {})
    if set(expected_serials) != set(rig["selected_components"]) or any(not value for value in expected_serials.values()):
        blockers["physical_qualification"].append("Controlled rig specimen serials are missing.")
    if rig["as_built_configuration_fingerprint"] != configuration_fingerprint:
        blockers["physical_qualification"].append("Rig as-built configuration is not bound to the frozen design.")
    if any(not value for value in plan["rig_safety_review"].values()):
        blockers["physical_qualification"].append("Fault injection, independent shutdown and rig protection review remain open.")
    instruments = {row["id"]:row for row in rig["calibration_records"]}
    if len(instruments) != len(rig["calibration_records"]):
        raise ValueError("duplicate calibration instrument IDs")
    for row in instruments.values():
        hashes[row["path"]] = thread.digest(root,row["path"])
        if hashes[row["path"]] != row["sha256"]:
            blockers["physical_qualification"].append(f"{row['id']}: calibration certificate changed")
        if calibration_period(row) is None:
            blockers["physical_qualification"].append(f"{row['id']}: calibration start/end interval is unresolved")
    invalid_instruments = {row["id"] for row in instruments.values() if hashes[row["path"]]!=row["sha256"]}
    calibration_events = plan.get("calibration_events", [])
    if len({row["id"] for row in calibration_events}) != len(calibration_events):
        raise ValueError("duplicate retrospective calibration event")
    calibration_impact = []
    for event in calibration_events:
        require(event,"id","instrument_id","discovered_at","affected_from","affected_until","reference")
        if instant(event["affected_from"]) > instant(event["affected_until"],end_of_day=True):
            raise ValueError("retrospective calibration interval is reversed")
        instant(event["discovered_at"])
        calibration_impact.append({"event_id":event["id"], "instrument_id":event["instrument_id"], "affected_run_ids":[]})
    if any(value is None for value in rig["operating_envelope"].values()):
        blockers["physical_qualification"].append("Representative rig duty and environmental envelope unresolved.")
    tests = {row["id"]:row for row in plan["tests"]}
    if len(tests) != len(plan["tests"]):
        raise ValueError("duplicate test IDs")
    for test in tests.values():
        if test.get("scenario_id"):
            ref(test["scenario_id"],{"scenarios"})
        for identifier in test["requirement_ids"]:
            ref(identifier,{"requirements"})
        if any(value is None for value in test["limits"].values()) or test["minimum_duration_s"] is None or test["repeat_count"] is None:
            blockers["physical_qualification"].append(f"{test['id']}: acceptance limits, duration or repeat count unresolved")
        if test["model_error_limit_c"] is None:
            blockers["design_verification"].append(f"{test['id']}: model correlation tolerance unresolved")
        else:
            rams.number(test["model_error_limit_c"],"model error criterion")
        for limit in test["limits"].values():
            if limit is not None:
                rams.number(limit,"rig acceptance limit")
        if test["minimum_duration_s"] is not None:
            rams.number(test["minimum_duration_s"],"rig test duration",minimum=1e-12)
        if test["repeat_count"] is not None and (type(test["repeat_count"]) is not int or test["repeat_count"] < 1):
            raise ValueError("rig repeat count must be a positive integer")
    run_ids = [row["id"] for row in plan["measurement_runs"]]
    if len(run_ids) != len(set(run_ids)):
        raise ValueError("duplicate measurement run IDs")
    results, authors = [], {plan["owner"]}
    authors.update(row.get("author") for row in plan.get("assurance_scope", {}).get("exclusions", []))
    for run in plan["measurement_runs"]:
        if run["test_id"] not in tests:
            raise ValueError("measurement run references unknown test")
        test = tests[run["test_id"]]
        rows, metrics = measurements(root,run,test)
        hashes[run["raw_path"]] = thread.digest(root,run["raw_path"])
        authors.add(run["performed_by"])
        run_blockers = list(metrics["response_validation"]["blockers"])
        if run["origin"] != "physical" or str(run["rig_serial"]).startswith("DEMO"):
            run_blockers.append("Synthetic measurements cannot qualify a physical assembly.")
        if run["configuration_fingerprint"] != configuration_fingerprint or run["rig_serial"] != rig["serial_number"]:
            run_blockers.append("Measurement configuration or rig serial differs.")
        if run["procedure_revision"] != test["procedure_revision"]:
            run_blockers.append("Test procedure revision differs.")
        if test["fault_required"] and run.get("fault_onset_s") is None:
            run_blockers.append("Fault timing is not recorded.")
        if set(rig["instrument_channels"]) - set(run["channel_instruments"]) or any(value not in instruments for value in run["channel_instruments"].values()):
            run_blockers.append("Measurement channels lack controlled instrument provenance.")
        if set(run["channel_instruments"].values()) & invalid_instruments:
            run_blockers.append("Measurement calibration certificate changed.")
        acquisition = instant(run["performed_at"])
        measurement_start = acquisition+timedelta(seconds=rows[0]["time_s"])
        measurement_end = acquisition+timedelta(seconds=rows[-1]["time_s"])
        calibration_checks = []
        for identifier in sorted(set(run["channel_instruments"].values()) & set(instruments)):
            instrument = instruments[identifier]
            period = calibration_period(instrument)
            valid = bool(period and period[0]<=measurement_start<=measurement_end<=period[1] and identifier not in invalid_instruments)
            calibration_checks.append({"calibration_id":identifier,"valid_at_measurement":valid})
            if not valid:
                run_blockers.append(f"{identifier}: calibration was expired, not yet valid, changed or unresolved at measurement time.")
            for event, impact in zip(calibration_events,calibration_impact):
                if (event["instrument_id"] == instrument.get("instrument_id",identifier) and
                    instant(event["affected_from"])<=measurement_end and instant(event["affected_until"],end_of_day=True)>=measurement_start):
                    impact["affected_run_ids"].append(run["id"])
                    run_blockers.append(f"{event['id']}: retrospective instrument validity finding affects this measurement.")
        if run.get("channel_semantics",{}).get("isolation") != "physical-energy-isolated":
            run_blockers.append("Isolation channel has not been identified as a physical energy-isolation observation.")
        for identifier, serial in run["specimen_serials"].items():
            if identifier not in rig["selected_components"] or not serial or str(serial).startswith("DEMO"):
                run_blockers.append("Specimen serials are missing, synthetic or out of scope.")
        if set(rig["selected_components"]) - set(run["specimen_serials"]):
            run_blockers.append("Not every selected rig component has an observed serial.")
        if run["specimen_serials"] != expected_serials:
            run_blockers.append("Observed specimen serials differ from the controlled rig record.")
        criteria = {}
        for key, limit in test["limits"].items():
            if key not in metrics:
                raise ValueError("unsupported rig acceptance quantity: " + key)
            criteria[key] = None if limit is None or metrics[key] is None else metrics[key] >= limit if key.startswith("min_") else metrics[key] <= limit
        if test["minimum_duration_s"] is None or metrics["duration_s"] < test["minimum_duration_s"]:
            run_blockers.append("Required test duration unresolved or not achieved.")
        if not all(value is True for value in criteria.values()):
            run_blockers.append("Measurement criteria failed or remain unresolved.")
        prediction = rams.thermal_screen(test.get("thermal_inputs") or inputs["physical_thermal"],[row["time_s"]-rows[0]["time_s"] for row in rows])
        model_error = None
        if prediction["predictions"]:
            model_error = max(max(abs(row["temperature_c"]-value) for value in point["temperature_c"])
                              for row,point in zip(rows,prediction["predictions"]))
            temperature_instrument = instruments.get(run["channel_instruments"].get("temperature_c"),{})
            if temperature_instrument.get("uncertainty_c") is None:
                model_error = None
            else:
                model_error += rams.number(temperature_instrument["uncertainty_c"],"measurement temperature uncertainty")
        correlation_passed = not run_blockers and model_error is not None and test["model_error_limit_c"] is not None and model_error <= test["model_error_limit_c"]
        results.append({"run_id":run["id"],"test_id":run["test_id"],"raw_path":run["raw_path"],"metrics":metrics,
                        "calibration_checks":calibration_checks,
                        "criteria":criteria,"blockers":run_blockers,"model_maximum_error_c":model_error,
                        "model_correlation_passed":correlation_passed,"state":"measured-unreviewed" if run["origin"] == "physical" else "synthetic-unreviewed"})
        blockers["physical_qualification"].extend(f"{run['id']}: {value}" for value in run_blockers)
    for identifier,test in tests.items():
        passing = [row for row in results if row["test_id"] == identifier and not row["blockers"]]
        if not passing or len(passing) < (test["repeat_count"] or 1):
            blockers["physical_qualification"].append(f"{identifier}: representative physical repetitions missing")
    validation = plan["model_validation"]
    calibration_ids, validation_ids = set(validation["calibration_run_ids"]),set(validation["validation_run_ids"])
    if calibration_ids & validation_ids:
        raise ValueError("calibration and held-out validation runs must be separate")
    if (calibration_ids | validation_ids) - set(run_ids):
        raise ValueError("model validation references an unknown run")
    if not validation_ids or validation["state"] != "reviewed" or not validation["review_reference"]:
        blockers["design_verification"].append("Calibrated model and held-out validation review remain open.")
    if any(not row["model_correlation_passed"] for row in results if row["run_id"] in validation_ids):
        blockers["design_verification"].append("Held-out model/measurement discrepancy exceeds criterion or is unresolved.")
    if validation_ids and {row["test_id"] for row in results if row["run_id"] in validation_ids} != set(tests):
        blockers["design_verification"].append("Declared model envelope lacks held-out normal/fault-case coverage.")
    manufacturing = []
    for characteristic in plan["critical_characteristics"]:
        ref(characteristic["item_id"],{"design_items"})
        if characteristic["lower"] is None or characteristic["upper"] is None:
            manufacturing.append(f"{characteristic['id']}: production limits and inspection release open")
    if not plan["production_batches"]:
        manufacturing.append("No controlled production-equivalence records for serialised assemblies.")
    for batch in plan["production_batches"]:
        require(batch,"id","serials","supplier_batches","operation_revision","raw_path","raw_sha256","configuration_fingerprint")
        if not isinstance(batch.get("characteristic_results"),dict):
            raise ValueError("production characteristic results require a per-serial mapping")
        hashes[batch["raw_path"]] = thread.digest(root,batch["raw_path"])
        if hashes[batch["raw_path"]] != batch["raw_sha256"]:
            manufacturing.append(f"{batch['id']}: production record changed")
        if batch.get("origin") != "physical" or any(str(serial).startswith("DEMO") for serial in batch["serials"]):
            manufacturing.append(f"{batch['id']}: synthetic/unidentified production cannot demonstrate equivalence")
        if batch["configuration_fingerprint"] != configuration_fingerprint or batch["operation_revision"] != plan["production_process_revision"]:
            manufacturing.append(f"{batch['id']}: design/process change requires requalification")
        for characteristic in plan["critical_characteristics"]:
            values = batch["characteristic_results"].get(characteristic["id"],{})
            for serial in batch["serials"]:
                value = values.get(serial)
                if value is not None:
                    rams.number(value,"production measurement")
                if value is None or characteristic["lower"] is None or characteristic["upper"] is None or not characteristic["lower"] <= value <= characteristic["upper"]:
                    manufacturing.append(f"{batch['id']}/{serial}/{characteristic['id']}: equivalence not demonstrated")
    for ncr in plan["nonconformances"]:
        require(ncr,"id","affected_serials","disposition","requalification")
        if ncr["disposition"] != "independently-approved" or not ncr.get("review_reference") or ncr["requalification"] != "closed-with-evidence":
            manufacturing.append(f"{ncr['id']}: disposition or requalification open")
    for rule in plan["replacement_rules"]:
        ref(rule["item_id"],{"design_items"})
        if not rule["supplier_compatibility_evidence"] or not rule["maintenance_instruction"]:
            manufacturing.append(f"{rule['item_id']}: replacement compatibility or instructions open")
        if nodes[rule["item_id"]]["revision"] not in rule["compatible_design_revisions"]:
            manufacturing.append(f"{rule['item_id']}: changed replacement revision requires compatibility review")
    blockers["physical_qualification"].extend(manufacturing)
    integration_kinds = {"hil", "vehicle", "infrastructure", "operations"}
    supplied_kinds = {row.get("kind") for row in plan["integration_evidence"]}
    for kind in sorted(integration_kinds - supplied_kinds):
        blockers["integration"].append(f"{kind}: integration evidence absent.")
    for evidence in plan["integration_evidence"]:
        require(evidence,"id","path","sha256","configuration_fingerprint","review_reference","kind")
        hashes[evidence["path"]] = thread.digest(root,evidence["path"])
        if evidence["sha256"] != hashes[evidence["path"]] or evidence["configuration_fingerprint"] != configuration_fingerprint:
            blockers["integration"].append(f"{evidence['id']}: integration evidence changed or out of scope")
    assessment = plan["assessment_approach"]
    if not assessment["agreed_reference"] or not assessment["operator"] or not assessment["independent_assessor"]:
        blockers["independent_review"].append("Operator/assessor assessment approach is not agreed.")
    if not plan["operating_conditions"]:
        blockers["operating_conditions"].append("Operating envelope, restrictions and handback conditions are unresolved.")
    if plan["scope"]["kind"] == "reference":
        blockers["operating_conditions"].append("Reference configuration has no deployment-specific accepted use.")
    analysis = quantitative(inputs)
    metrics = allocation_metrics(inputs,analysis,model_validated=not blockers["design_verification"],valid_evidence_ids=valid_evidence_ids)
    allocation_results = [assess_allocation(row,metrics) for row in plan["allocations"]]
    for result in allocation_results:
        if result["state"] != "met":
            blockers["requirements"].append(f"{result['allocation_id']}: RAMS target {result['state']}; "+"; ".join(result["reasons"]))
    semantic_plan = {key:value for key,value in plan.items() if key not in {"review_records","accepted_baseline_fingerprint"}}
    scope_hashes = {key:value for key,value in hashes.items() if key != PLAN}
    scoped_findings = assurance_findings(graph,plan)
    evidence_fingerprint = thread.fingerprint({"definition":semantic_plan,"sources":scope_hashes,"results":results,
                                              "allocation_results":allocation_results,"assurance_scope":scoped_findings,
                                              "calibration_impact":calibration_impact})
    reviews,review_gaps = authenticated_reviews(root,plan["review_records"],review_policy,evidence_fingerprint,configuration_fingerprint,authors,today)
    scoped_findings = assurance_findings(graph,plan,reviews)
    for finding in scoped_findings["findings"]:
        if finding["disposition"] != "excluded-by-authenticated-review":
            blockers[finding["stage"]].append(f"Assurance graph {finding['record_id']}: {finding['message']} ({finding['disposition']})")
    for record in plan["review_records"]:
        for key in ("envelope_path","signature_path"):
            hashes[record[key]] = thread.digest(root,record[key])
    blockers["independent_review"].extend(review_gaps)
    roles = {row["role"] for row in reviews}
    assessors={row["reviewer"] for row in reviews if row["role"]=="assessor"}
    design_authorities={row["reviewer"] for row in reviews if row["role"]=="design-authority"}
    if assessors & design_authorities:
        blockers["independent_review"].append("Assessor and design authority require separate reviewer identities.")
    for role in ("assessor","design-authority"):
        if role not in roles:
            blockers["independent_review"].append(f"Authenticated {role} decision missing.")
    for record in plan["operational_records"]:
        require(record,"id","asset_serial","failure_mode_id","corrective_action","effectiveness_check","engineering_handback")
        ref(record["failure_mode_id"],{"failure_modes"})
        if record["engineering_handback"] != "independently-accepted" or record["effectiveness_check"] == "open":
            blockers["operating_conditions"].append(f"{record['id']}: engineering handback/effectiveness review open")
    stages = {stage:{"state":"blocked" if blockers[stage] else "evidence-current-for-review",
                     "blockers":sorted(set(blockers[stage]))} for stage in STAGES}
    accepted_use = next((row.get("accepted_use") for row in reviews if row["role"] == "design-authority"),None)
    accepted = bool(accepted_use) and all(not row["blockers"] for row in stages.values())
    return {"schema":plan["schema"],"package_id":plan["id"],"title":plan["title"],"subject_id":plan["subject_id"],
            "configuration_id":cfg["id"],"configuration_fingerprint":configuration_fingerprint,"scope":plan["scope"],
            "evidence_fingerprint":evidence_fingerprint,"source_hashes":dict(sorted(hashes.items())),
            "stages":stages,"quantitative_analysis":analysis,"measurement_results":results,
            "allocation_results":allocation_results,
            "assurance_scope":scoped_findings,
            "calibration_impact":calibration_impact,
            "manufacturing_blockers":manufacturing,"authenticated_reviews":reviews,
            "accepted_use":accepted_use if accepted else None,"qualification_state":"recorded-subsystem-acceptance" if accepted else "qualification-open",
            "changes_since_decision":"no-authenticated-acceptance-baseline" if not plan["accepted_baseline_fingerprint"] else
                                      "baseline-reference-unverified-reassessment-required" if not reviews else
                                      "evidence-changed-reassessment-required" if plan["accepted_baseline_fingerprint"] != evidence_fingerprint else "baseline-current",
            "test_plan":plan["tests"],"critical_characteristics":plan["critical_characteristics"],
            "qualification_definition":plan,
            "release_ready":False,"interpretation":"Subsystem dossier readiness; vehicle, railway integration and deployment authorization remain separately controlled."}


def scoped_readiness(report: dict, city: str, environment: str, subject: str = "") -> dict:
    if environment not in {"simulation","physical"} or not city or len(city)>64 or len(subject)>160 or any(c not in "abcdefghijklmnopqrstuvwxyz0123456789-" for c in city):
        raise ValueError("invalid readiness context")
    scope = report["scope"]
    matches = scope["kind"] == "deployment" and scope["city"] == city and scope["environment"] == environment and (not subject or subject == report["subject_id"])
    return {"requested_context":{"city":city,"environment":environment,"subject":subject},
            "deployment_state":"package-in-scope" if matches else "no-deployment-qualification-package",
            "deployment_accepted_use":report["accepted_use"] if matches else None,
            "reference_package":report if matches or scope["kind"] == "reference" else None,
            "release_ready":False}


def export_dossier(root: Path, report: dict, output: Path) -> None:
    """Export exact original inputs plus readable results; never creates acceptance."""
    output.parent.mkdir(parents=True,exist_ok=True)
    originals = {value:thread.source(root,value).read_bytes() for value in report["source_hashes"]}
    import hashlib
    if any(hashlib.sha256(data).hexdigest()!=report["source_hashes"][value] for value,data in originals.items()):
        raise ValueError("Dossier inputs changed during export")
    manifest = {"schema":"osr-qualification-dossier/1","package_id":report["package_id"],
                "evidence_fingerprint":report["evidence_fingerprint"],"configuration_fingerprint":report["configuration_fingerprint"],
                "source_hashes":report["source_hashes"],"qualification_state":report["qualification_state"],"release_ready":False}
    temporary = output.with_suffix(output.suffix+".tmp")
    try:
        with zipfile.ZipFile(temporary,"w",compression=zipfile.ZIP_DEFLATED) as archive:
            archive.writestr("manifest.json",json.dumps(manifest,indent=2,sort_keys=True)+"\n")
            archive.writestr("report.json",json.dumps(report,indent=2,sort_keys=True)+"\n")
            archive.writestr("report.md",render_markdown(report))
            archive.writestr("definition.json",json.dumps(report["qualification_definition"],indent=2,sort_keys=True)+"\n")
            for value,data in sorted(originals.items()):
                archive.writestr("inputs/"+value,data)
        temporary.replace(output)
    finally:
        temporary.unlink(missing_ok=True)


def render_markdown(report: dict) -> str:
    lines=["# Battery-cooling qualification readiness","","> Generated by `tools/automation/subsystem_qualification.py`.","",
           f"Package `{report['package_id']}` / configuration `{report['configuration_id']}`. **{report['qualification_state'].upper()}.**","",
           "Quantitative screens retain their stated input evidence basis. Physical qualification and accepted use require the separately listed measurements and authenticated decisions.","",
           "| Decision area | State | Open findings |","|---|---|---|"]
    for stage,row in report["stages"].items():
        lines.append(f"| {stage.replace('_',' ')} | {row['state']} | {'; '.join(row['blockers']) or 'Evidence current for review'} |")
    lines += ["","## RAMS allocation outcomes","","| Allocation / metric | Target | Result bounds | Outcome |","|---|---|---|---|"]
    for row in report["allocation_results"]:
        lines.append(f"| {row['allocation_id']} / {row['metric']} | {row['comparison']} {row['target']} {row['unit']} | {row.get('bounds')} | {row['state']} — {'; '.join(row['reasons'])} |")
    scope=report["assurance_scope"]
    lines += ["","## Scoped graph findings","",
              f"Graph `{scope['graph_fingerprint']}`; {len(scope['record_ids'])} scoped records. Every scoped blocker requires closure or an authenticated, baseline-bound exclusion.","",
              "| Record | Finding | Disposition |","|---|---|---|"]
    for finding in scope["findings"]:
        lines.append(f"| {finding['record_id']} | {finding['message']} | {finding['disposition']} |")
    lines += ["","## Quantitative screening","","```json",json.dumps(report["quantitative_analysis"],indent=2,sort_keys=True),"```","",
              "## Controlled rig tests","","| Test | Procedure | Acceptance inputs |","|---|---|---|"]
    for row in report["test_plan"]:
        lines.append(f"| {row['id']} — {row['title']} | {row['procedure_revision']} | {', '.join(row['limits'])}; duration, repetitions and model tolerance require review |")
    return "\n".join(lines)+"\n"


def main() -> int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check",action="store_true")
    parser.add_argument("--plan",type=Path)
    parser.add_argument("--review-policy",type=Path)
    parser.add_argument("--stdout",action="store_true")
    parser.add_argument("--export",type=Path,help="export original inputs and the readiness report as a review dossier")
    args=parser.parse_args()
    plan=json.loads(args.plan.read_text()) if args.plan else None
    report=compile_package(plan=plan,review_policy=args.review_policy)
    if args.export:
        export_dossier(ROOT,report,args.export)
        print(f"Qualification dossier: {args.export}; {report['qualification_state']}");return 0
    if args.stdout:
        print(json.dumps(report,indent=2,sort_keys=True));return 0
    if args.plan or args.review_policy:
        parser.error("Custom inputs use --stdout; tracked baseline reports retain repository scope")
    targets={ROOT/(OUTPUT+".json"):json.dumps(report,indent=2,sort_keys=True)+"\n",ROOT/(OUTPUT+".md"):render_markdown(report)}
    for path,value in targets.items():
        if args.check:
            if not path.is_file() or path.read_text()!=value:
                raise SystemExit(f"stale qualification report: {path}")
        else:
            path.write_text(value)
    print("Subsystem qualification: six separate readiness states; physical evidence and acceptance OPEN")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
