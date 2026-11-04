#!/usr/bin/env python3
"""Compare retained bounded full-call measurements; never dispatch a solver.

Measurements use two source epochs, so source/evaluation/ancestry receipt IDs
are reported separately. Exact canonical bytes are checked for physical graph
records; complete numerical/DFMA/frame payloads are compared where unchanged.
"""
import argparse
import gzip
import hashlib
import json
from pathlib import Path


def encoded(value):
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)+"\n").encode()


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def numeric(value):
    if isinstance(value, dict):
        return {k:numeric(v) for k,v in value.items() if isinstance(v,(dict,list,int,float))}
    if isinstance(value,list):
        return [numeric(v) for v in value]
    return value


def geometry_cohort(directory, retained_runs):
    """Select exact run definitions/runtime, not every later cache occupant.

    A shared state may legitimately contain additional Python/NumPy/source
    contexts. Those are outside these retained measurements. Selected records
    still require canonical bytes, their own seals, request-derived filenames,
    exact source membership and complete unambiguous definition coverage.
    """
    expected={}
    for run in retained_runs:
        runtime=encoded(run["contract"]["runtime"])
        for row in [*run["evaluations"],*run["attempts"]]:
            if row.get("candidate_id") and row.get("definition_id"):
                key=(row["candidate_id"],row["definition_id"],runtime)
                expected.setdefault(key,[]).append(run["sources"])
    if not expected:
        raise ValueError("Retained measurements contain no physical geometry definitions")
    selected={};covered={};storage=0;ignored=0
    for path in sorted(Path(directory).glob("*.gz")):
        raw=gzip.decompress(path.read_bytes())
        value=json.loads(raw)
        request=value["request"]
        candidate=value["candidate"]
        key=(candidate["candidate_id"],candidate["definition_id"],encoded(request["runtime"]))
        if key not in expected:
            ignored+=1
            continue
        dependencies={**request["source_sha256"],**request["retained_equipment_sources"]}
        if not any(all(sources.get(name)==sha for name,sha in dependencies.items()) for sources in expected[key]):
            ignored+=1
            continue
        unsealed={k:v for k,v in value.items() if k!="record_id"}
        if (raw!=encoded(value) or value.get("record_id")!=hashlib.sha256(encoded(unsealed)).hexdigest()
                or path.name!=hashlib.sha256(encoded(request)).hexdigest()+".json.gz"):
            raise ValueError("Selected geometry canonical/request/record identity differs: "+str(path))
        if key in covered:
            raise ValueError("Ambiguous geometry records for a retained definition/runtime")
        covered[key]=path.name
        selected[path.name]=raw
        storage+=path.stat().st_size
    if set(covered)!=set(expected):
        raise ValueError("Retained geometry cohort coverage incomplete: missing "+str(len(set(expected)-set(covered))))
    metadata=dict(selected_records=len(selected),expected_definition_runtime_pairs=len(expected),
        ignored_other_context_records=ignored,compressed_bytes=storage,
        runtime_context_ids=sorted({hashlib.sha256(k[2]).hexdigest() for k in expected}))
    return selected,metadata


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--directory", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args=parser.parse_args()
    if args.output.exists():
        raise SystemExit("Refusing to replace a retained benchmark report")
    root=Path(__file__).resolve().parents[2]
    directory=args.directory.resolve()
    measurements={}
    runs={}
    for epoch in ("baseline","optimized"):
        measurements[epoch]={}
        runs[epoch]={}
        for mode in ("fresh","resume"):
            timing=directory/(epoch+"-"+mode+"-timing.json")
            summary=directory/(epoch+"-"+mode+".json")
            value=json.loads(summary.read_bytes())
            run=Path(value["output"])
            measurements[epoch][mode]=dict(json.loads(timing.read_bytes()),
                summary_sha256=digest(summary),run_sha256=digest(run),run_path=str(run),
                candidate_count=value["candidate_count"],generated_programs=value["generated_programs"],
                section_jobs_new=value["section_jobs_new"],section_evidence_reused=value["section_evidence_reused"])
            runs[epoch][mode]=json.loads(run.read_bytes())
    cohorts={epoch:geometry_cohort(directory/(epoch+"-state")/"geometry",list(runs[epoch].values())) for epoch in measurements}
    geometries={epoch:cohort[0] for epoch,cohort in cohorts.items()}
    checks={"exact_canonical_geometry_records":geometries["baseline"]==geometries["optimized"]}
    for mode in ("fresh","resume"):
        before,after=(runs[e][mode] for e in ("baseline","optimized"))
        checks[mode+"_complete_detailed_finalists"]=before["detailed_finalists"]==after["detailed_finalists"]
        checks[mode+"_complete_analytical_assessments"]=before["refinement"]["assessments"]==after["refinement"]["assessments"]
        checks[mode+"_complete_coarse_frame_assessments"]=[r["assessment"] for r in before["refinement"]["frame_assessments"]]==[
            r["assessment"] for r in after["refinement"]["frame_assessments"]]
        evaluation=lambda run:sorted([{k:v for k,v in row.items() if k not in ("request","evaluation_id")}
            for row in run["evaluations"]],key=lambda row:(row["candidate_id"],row["definition_id"]))
        checks[mode+"_complete_cost_and_quantity_payloads"]=evaluation(before)==evaluation(after)
        ancestry=lambda run:[{k:row.get(k) for k in ("genes","operator","parent_candidate_ids","candidate_id","definition_id","state","reason")}
            for row in run["attempts"]]
        checks[mode+"_physical_ancestry_and_attempt_dispositions"]=ancestry(before)==ancestry(after)
        archive=lambda run:{k:run["archive"][k] for k in ("cells","global_front","dominated","retained_candidate_ids","statistics")}
        checks[mode+"_archive_decisions"]=archive(before)==archive(after)
        sections=lambda run:[dict(candidate_id=r["assessment"]["candidate_id"],state=r["assessment"]["state"],
            execution=r["assessment"]["execution"],domain_holds=r["assessment"]["domain_holds"],
            numeric_frame_payload=numeric(r["assessment"]["frame_result"])) for r in run["refinement"]["section_frame_assessments"]]
        checks[mode+"_section_frame_numeric_payload_and_holds"]=sections(before)==sections(after)
        checks[mode+"_qualification_flags"]=all(before[k] is after[k] is False for k in (
            "physical_accepted","engineering_accepted","manufacturing_release","operating_release","configuration_adopted"))
    if not all(checks.values()):
        raise SystemExit("Parity failure: "+str([k for k,v in checks.items() if not v]))
    storage={epoch:cohort[1]["compressed_bytes"] for epoch,cohort in cohorts.items()}
    report=dict(schema="osr-campaign-serialization-benchmark/1",method="Uninstrumented perf_counter around complete imported native_campaign.run; one fresh and one exact resume per source epoch",
        budgets=dict(memory_MiB=1024,timeout_s_per_call=90,threads=1,ccx_jobs=0,section_jobs=1),
        measurements=measurements,parity_checks=checks,geometry_record_count=len(geometries["baseline"]),geometry_compressed_bytes=storage,
        geometry_cohorts={epoch:cohort[1] for epoch,cohort in cohorts.items()},
        full_call_speedup_percent={mode:100*(1-measurements["optimized"][mode]["wall_s"]/measurements["baseline"][mode]["wall_s"]) for mode in ("fresh","resume")},
        sources_before=runs["baseline"]["fresh"]["sources"],sources_after=runs["optimized"]["fresh"]["sources"],
        baseline_snapshot_sha256=digest(directory/"producer-before/manifest.json"),tool_sha256=digest(Path(__file__)),
        current_producer_sha256=digest(root/"engineering/design_search/native_campaign.py"),
        caveats=["One sample per case; no statistical confidence or isolated CPU claim; ordinary test activity may overlap",
            "RSS is process cumulative peak including imports; fresh and resume share a process within each epoch",
            "Source-bound receipt and evaluation IDs intentionally differ across epochs; physical/cost/response/decision comparisons are explicit above",
            "Level1 geometry gzip trades modest disk bytes for CPU; decompressed canonical records are exactly equal",
            "No high-fidelity native solver speed or physical railway qualification is established"])
    args.output.parent.mkdir(parents=True,exist_ok=True)
    with args.output.open("xb") as handle:
        handle.write(encoded(report))
    print(json.dumps(dict(report=str(args.output),sha256=digest(args.output),speedup_percent=report["full_call_speedup_percent"],all_checks=True)))


if __name__=="__main__":
    main()
