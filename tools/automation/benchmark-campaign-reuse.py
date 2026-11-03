#!/usr/bin/env python3
"""Compare bounded analytical reuse against independent recomputation.

Run with the project's Python environment and OPENBLAS/OMP/MKL_NUM_THREADS=1.
Artifacts stay in a new private directory. No native engineering job is allowed.
Timings describe this machine/workload and do not establish railway feasibility.
"""
import argparse
from hashlib import sha256
import json
import os
from pathlib import Path
import resource
import statistics
import sys
import time

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from engineering.design_search import axial_analysis, design_grammar, grammar_structure, native_campaign
from engineering.station_rail.common import digest, encoded, identity


def timed(call):
    start=time.perf_counter()
    result=call()
    return time.perf_counter()-start,result


def comparison(result,state):
    """Compare full numerical/economic payloads and exact native requests."""
    packets=[json.loads((state/"generated"/(g["generation_id"]+".json")).read_bytes()) for g in result["generations"]]
    return dict(evaluations=result["evaluations"],
        requests=[p["request"] for p in packets],proposals=[p["generated"]["proposals"] for p in packets],
        feedback=[g["parent_feedback_snapshot_id"] for g in result["generations"]],
        attempts=[{k:v for k,v in a.items() if k!="proposal_id"} for a in result["attempts"]],
        assessments=result["refinement"]["assessments"],plan=result["refinement"]["parent_feedback_plan"],
        frame_assessments=[row["assessment"] for row in result["refinement"]["frame_assessments"]],
        deferred=[{k:v for k,v in a.items() if k!="proposal_id"} for a in result["deferred"]])


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output",type=Path,required=True)
    parser.add_argument("--samples",type=int,default=2)
    args=parser.parse_args()
    if not 1<=args.samples<=3:parser.error("Use one to three bounded samples per policy")
    for name in ("OPENBLAS_NUM_THREADS","OMP_NUM_THREADS","MKL_NUM_THREADS"):
        if os.environ.get(name)!="1":parser.error(name+"=1 must be set before Python starts")
    args.output.mkdir(parents=True,exist_ok=False)
    source={**native_campaign._sources(ROOT),str(Path(__file__).relative_to(ROOT)):digest(__file__)}
    body=design_grammar.parameters();body["braced"]=True
    graph=design_grammar.build(body)["structure"]
    def original():
        diagnostic=grammar_structure.diagnose_rigidity(graph)
        reference=grammar_structure.linear_reference(graph)
        stock=grammar_structure._validated(graph)[3]
        return diagnostic,reference,stock
    def prepared():
        system=axial_analysis.prepare(graph)
        return system.diagnose(),system.linear_reference(),system.stock
    expected=original()
    if prepared()!=expected:raise ValueError("Prepared axial method differs from independent oracle")
    methods={name:[] for name in ("original","prepared")}
    for _ in range(3):
        for name,call in (("original",original),("prepared",prepared)):
            seconds,value=timed(call)
            if value!=expected:raise ValueError("Axial method changed during timing")
            methods[name].append(seconds)
    samples=[];reference=None
    for repetition in range(args.samples):
        # Alternate order to reduce systematic warm-cache/order bias.
        for enabled in ((False,True) if repetition%2==0 else (True,False)):
            state=args.output/(str(repetition)+("-reuse" if enabled else "-recompute"))
            seconds,summary=timed(lambda:native_campaign.run(state=state,native_jobs=0,invocation_reuse=enabled))
            value=json.loads(Path(summary["output"]).read_bytes())
            if (summary["numerical_solver_dispatch_count"]!=0 or summary["native_evidence_reused"]!=0
                    or any(summary[k] is not False for k in native_campaign.FLAGS)):
                raise ValueError("Benchmark dispatched a solver or granted acceptance")
            payload=comparison(value,state)
            if reference is None:reference=payload
            if payload!=reference:raise ValueError("Reuse changes candidate, numerical, cost or generation payloads")
            samples.append(dict(reuse=enabled,repetition=repetition,full_call_wall_s=seconds,
                reported_campaign_s=summary["elapsed_s"],run_id=summary["run_id"],
                run_file_sha256=digest(summary["output"]),output=summary["output"],
                candidate_count=summary["candidate_count"],generated_programs=summary["generated_programs"],
                evaluations=len(value["evaluations"]),analytical_assessments=summary["analytical_assessments"],
                cache=summary["invocation_cache"]))
    if any(digest(ROOT/name)!=sha for name,sha in source.items()):
        raise ValueError("Benchmark sources changed during execution")
    report=dict(schema="osr-campaign-reuse-benchmark/1",source_sha256=source,runtime=native_campaign._runtime(),
        methods=methods,method_medians_s={k:statistics.median(v) for k,v in methods.items()},samples=samples,
        full_call_medians_s={str(enabled):statistics.median(s["full_call_wall_s"] for s in samples if s["reuse"]==enabled) for enabled in (False,True)},
        comparison_payload_sha256=identity(reference),exact_payload_parity=True,native_solver_dispatches=0,
        cumulative_process_maxrss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        measurement_scope="perf_counter wall time; alternating order; no campaign warmup; RSS is cumulative process high-water, not per-case peak",
        physical_accepted=False,engineering_accepted=False,integrated_selection=None)
    report["benchmark_id"]=identity(report)
    raw=encoded(report);(args.output/"report.json").write_bytes(raw)
    print(json.dumps(dict(benchmark_id=report["benchmark_id"],report_sha256=sha256(raw).hexdigest(),
        method_medians_s=report["method_medians_s"],full_call_medians_s=report["full_call_medians_s"],exact_payload_parity=True),indent=2))


if __name__=="__main__":main()
