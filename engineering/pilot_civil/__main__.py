"""Reproduce a bounded immutable civil research packet."""
import argparse,json,platform,resource,time
from pathlib import Path
from engineering.station_rail.common import digest,identity,encoded
from . import FLAGS,ROOT
from .design import baseline_train,evaluate_portfolio,seal
from .assembly import scene
from .native_trial import source_context,generate,prepare,trial


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',required=True,type=Path)
    parser.add_argument('--axle-input',type=Path)
    parser.add_argument('--upstream-root',type=Path,default=ROOT)
    parser.add_argument('--native',action='store_true',help='Exactly two SolidCraft jobs and at most two dual-solver FEM cases')
    args=parser.parse_args();out=args.output.resolve();out.mkdir(parents=True,exist_ok=False)
    started=time.monotonic();before=source_context();train=json.loads(args.axle_input.read_bytes()) if args.axle_input else baseline_train()
    def write(name,value):
        path=out/name
        if path.exists():raise ValueError('Immutable packet file already exists')
        path.write_bytes(encoded(value))
    write('axle-input.json',train);write('source-before.json',before)
    request=seal(dict(schema='osr-pilot-civil-request/1',input_evaluation_id=train['evaluation_id'],system_candidate_id=train['candidate_id'],source_sha256=before,
        native_requested=args.native,resources=dict(moving_positions_each=501,max_cells=20000,max_cad_jobs=2,max_fem_cases=2,native_cpu_s_each_process=60,native_wall_s_each_process=58,native_memory_mib_each_process=2048),**FLAGS))
    write('request.json',request)
    results=evaluate_portfolio(train,upstream_root=args.upstream_root);write('portfolio.json',results)
    eligible=[r for r in results if r['advisory_screen_passed'] and r['foundation']['soil_case']=='base']
    selected=min(eligible,key=lambda r:r['cost']['scoped_installed_usd']['base']) if eligible else None
    selection=seal(dict(schema='osr-pilot-civil-selection/1',system_candidate_id=train['candidate_id'],purpose='Next experiment only; not integrated baseline adoption',eligible_civil_ids=[r['civil_candidate_id'] for r in eligible],
        proposed_civil_id=selected['civil_candidate_id'] if selected else None,rationale='Lowest scoped central civil cost among successful declared gross-model screens in base soil hypothesis',**FLAGS),'selection_id')
    write('selection.json',selection)
    trials=[]
    if selected:
        write('assembly.json',scene(selected));write('selected-evaluation.json',selected)
        if args.native:
            cad=generate(selected,out/'gross-beam-cad',gross_beam_only=True)
            generate(selected,out/'located-assembly-cad')
            if cad.get('gross_volume_screen_passed'):
                from engineering.design_search.craft_backends import freecad_reference
                reference=freecad_reference.run(cad['step_path'],out/'independent-freecad',timeout_s=58,memory_mb=2048)
                write('independent-cad-summary.json',reference)
                names=[l['name'] for l in train['load_cases']]
                load_name='normal-high' if 'normal-high' in names else names[-1]
                spec=prepare(selected,train,cad,load_name);write('native-input.json',spec)
                for i,size in enumerate((.3,.2)):
                    result=trial(spec,out/('native-'+str(i+1)),size_m=size);trials.append(result)
                    if result.get('failure_reason') or 'calculix' not in result or 'fieldcraft' not in result:break
    after=source_context();write('source-after.json',after)
    report=seal(dict(schema='osr-pilot-civil-run/1',request_id=request['evaluation_id'],system_candidate_id=train['candidate_id'],source_unchanged=before==after,
        executions_completed=True,numerical_sampling_converged=False,physical_acceptance=False,selected_for_next_experiment=selection['proposed_civil_id'],
        candidates=len(results),advisory_passes=sum(r['advisory_screen_passed'] for r in results),native_trials=len(trials),
        elapsed_s=time.monotonic()-started,coordinator_peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        verifier_isolation='Coordinator source snapshots and before/after hashes; not an OS read-only source sandbox. Native logs report actual requested isolation and process outcomes.',
        scope='Civil-only provisional replacement accounts; no complete railway or city repricing claim.',python=platform.python_version(),**FLAGS))
    write('report.json',report)
    files={str(path.relative_to(out)):dict(sha256=digest(path),bytes=path.stat().st_size) for path in out.rglob('*') if path.is_file()}
    write('manifest.json',seal(dict(schema='osr-pilot-civil-manifest/1',files=files,total_bytes=sum(v['bytes'] for v in files.values()),**FLAGS)))
    print(json.dumps(dict(output=str(out),run_id=report['evaluation_id'],candidates=len(results),advisory_passes=report['advisory_passes'],source_unchanged=report['source_unchanged'],native_trials=len(trials))))
    if before!=after:raise SystemExit('Source drift: retained packet held')

if __name__=='__main__':main()
