#!/usr/bin/env python3
"""Complete one bounded campaign with lightweight inclusive phase timings.

Set OPENBLAS/OMP/MKL_NUM_THREADS=1 before starting Python. The timers preserve
function results and count nested work inclusively; phase times must not be
added. No native engineering jobs are permitted by this profiling command.
"""
import argparse
from functools import wraps
import json
import os
from pathlib import Path
import resource
import sys
import time

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from engineering.design_search import native_campaign as c,frame_analysis,grammar_structure,native_search
from engineering.station_rail import common


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output",type=Path,required=True)
    args=parser.parse_args()
    for name in ("OPENBLAS_NUM_THREADS","OMP_NUM_THREADS","MKL_NUM_THREADS"):
        if os.environ.get(name)!="1":parser.error(name+"=1 required before Python imports")
    args.output.mkdir(parents=True,exist_ok=False)
    sources={**c._sources(ROOT),str(Path(__file__).relative_to(ROOT)):common.digest(__file__)}
    measurements={};originals=[]
    def instrument(owner,name,label):
        original=getattr(owner,name)
        row=measurements.setdefault(label,dict(calls=0,failed=0,inclusive_wall_s=0.))
        @wraps(original)
        def timed(*args,**kwargs):
            start=time.perf_counter();row["calls"]+=1
            try:return original(*args,**kwargs)
            except BaseException:
                row["failed"]+=1
                raise
            finally:row["inclusive_wall_s"]+=time.perf_counter()-start
        setattr(owner,name,timed);originals.append((owner,name,original))
    for owner,name,label in (
        (c,"_materialise","geometry_materialisation"),(c,"_evaluate","nominal_stock_cost"),
        (c,"_check_epoch","campaign_source_checks"),(c,"_runtime","runtime_identity_checks"),
        (c,"_verify_frontier","frontier_reconstruction"),(c,"_read_cache","record_readback"),
        (c,"_checkpoint","checkpoint_write"),(grammar_structure,"_system","axial_matrix_assembly"),
        (frame_analysis,"_assemble","frame_matrix_assembly"),(native_search,"_run","rust_process_and_tool_communication"),
        (c.np.linalg,"svd","compiled_svd"),(c.np.linalg,"solve","compiled_linear_solve"),
        (c.np.linalg,"eigvalsh","compiled_frame_eigenvalue_check")):
        instrument(owner,name,label)
    # Modules import these helpers by name. Wrap all currently loaded engineering
    # aliases so this measures actual campaign hashing/encoding rather than only
    # calls made through the common module object.
    for helper,label in (("identity","canonical_identity"),("encoded","canonical_json_encoding")):
        original=getattr(common,helper)
        aliases=[(module,helper) for name,module in list(sys.modules.items())
                 if name.startswith("engineering.") and getattr(module,helper,None) is original]
        instrument(common,helper,label)
        wrapped=getattr(common,helper)
        for owner,name in aliases:
            if owner is common:continue
            originals.append((owner,name,getattr(owner,name)));setattr(owner,name,wrapped)
    start=time.perf_counter()
    try:summary=c.run(state=args.output/"state",native_jobs=0,frame_native_jobs=0)
    finally:
        for owner,name,original in reversed(originals):setattr(owner,name,original)
    elapsed=time.perf_counter()-start
    if summary["numerical_solver_dispatch_count"]!=0:raise ValueError("Profiling dispatched an engineering solver")
    if any(common.digest(ROOT/name)!=sha for name,sha in sources.items()):raise ValueError("Profile source epoch changed")
    run=json.loads(Path(summary["output"]).read_bytes())
    if run["seed_pending"] or run["pending"] or summary["generated_programs"]!=2000:
        raise ValueError("Profile did not complete the declared default campaign")
    report=dict(schema="osr-completed-campaign-phase-profile/1",completed=True,source_sha256=sources,
        runtime=c._runtime(),full_call_wall_s=elapsed,measurements=measurements,summary=summary,
        run_file_sha256=common.digest(summary["output"]),
        process_maxrss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        method="Lightweight perf_counter wrappers, inclusive and nested; not additive or uninstrumented benchmark timings",
        physical_accepted=False,engineering_accepted=False,integrated_selection=None)
    report["profile_id"]=common.identity(report)
    (args.output/"report.json").write_bytes(common.encoded(report))
    print(json.dumps(dict(profile_id=report["profile_id"],full_call_wall_s=elapsed,
        run_id=summary["run_id"],completed=True,measurements=measurements),indent=2))


if __name__=="__main__":main()
