"""Opt-in stage profiling over unchanged mapped-city evaluators.

Exclusive self-time buckets partition instrumented time; cumulative function
measurements overlap. No source/evaluator monkeypatches or native solves.
"""
import argparse
import cProfile
import hashlib
import json
from pathlib import Path
import pstats
import subprocess
import sys
import time

GIB = 1024**3
STAGES = ('source_verification', 'decoding', 'geometry', 'service', 'civil',
          'cost', 'delivery', 'serialization_hashing', 'publication', 'unclassified')


def stage_for(filename, function):
    name = filename.replace('\\', '/')
    if function in ('digest', '_sources', 'verify_base', '_verify_sources'):
        return 'source_verification'
    if '/json/decoder.py' in name or '/gzip.py' in name and function in ('read', 'decompress'):
        return 'decoding'
    if name.endswith('/station_rail/common.py') and function in ('identity', 'encoded'):
        return 'serialization_hashing'
    if '/json/encoder.py' in name or 'hashlib' in name:
        return 'serialization_hashing'
    groups = dict(geometry=('planning_geometry', 'city_alignment', 'city_inputs'),
        service=('city_service', 'revision_service', 'operations', 'vehicle', 'braking', 'propulsion_layout', 'station_motor'),
        civil=('city_civil',), cost=('city_project_cost', 'city_cost_inputs', 'vehicle_supply', 'supply_economics', 'model_cost', 'make_buy'),
        delivery=('delivery_plan',))
    for stage, modules in groups.items():
        if any(name.endswith('/'+m+'.py') for m in modules):
            return stage
    if name.endswith('/station_rail/civil.py'): return 'civil'
    if '/services/integration/osr_integration/city_outline.py' in name: return 'delivery'
    if name.endswith('/city_workflow.py') and function == 'run': return 'publication'
    return 'unclassified'


def aggregate_stats(stats, elapsed):
    stages = {name: 0.0 for name in STAGES}; functions = []
    for (filename, line, function), (primitive, calls, own, cumulative, callers) in stats.items():
        stages[stage_for(filename, function)] += own
        functions.append(dict(file=filename, line=line, function=function, calls=calls,
            primitive_calls=primitive, self_seconds=own, cumulative_seconds=cumulative))
    accounted = sum(stages.values())
    return dict(exclusive_self_seconds=stages, accounted_self_seconds=accounted,
        elapsed_seconds=elapsed, overhead_or_uncaptured_seconds=max(0., elapsed-accounted),
        top_functions=sorted(functions,key=lambda r:r['cumulative_seconds'],reverse=True)[:30],
        timing_scope='Instrumented wall time, exclusive self-time stages. Cumulative function timings overlap.',
        unclassified_scope='Generic copying, I/O, builtin/extension work and orchestration without reliable attribution.')


def profile_call(call, stats_path):
    profiler=cProfile.Profile(); start=time.perf_counter()
    try: result=profiler.runcall(call)
    finally:
        elapsed=time.perf_counter()-start
        profiler.dump_stats(str(stats_path))
    return result, aggregate_stats(pstats.Stats(profiler).stats,elapsed)


def _git(root, *args):
    return subprocess.check_output(['git','-C',str(root),*args],text=True).strip()


def run(root, output, *, trials=1, maximum_wall_seconds=600):
    root,output=Path(root).resolve(),Path(output).resolve()
    if output==root or root in output.parents: raise ValueError('External immutable profile output required')
    if type(trials) is not int or not 1<=trials<=4: raise ValueError('One to four bounded trials required')
    if type(maximum_wall_seconds) not in (int,float) or not 1<=maximum_wall_seconds<=600:
        raise ValueError('Finite bounded wall budget required')
    if output.exists(): raise ValueError('Fresh profile output required; preserve prior runs')
    if _git(root,'status','--porcelain','--untracked-files=all'): raise ValueError('Clean runtime source required')
    commit,tree=_git(root,'rev-parse','HEAD'),_git(root,'rev-parse','HEAD^{tree}')
    sys.path.insert(0,str(root))
    from engineering.performance import disk_admission
    output.parent.mkdir(parents=True,exist_ok=True)
    admission=disk_admission(output.parent,minimum_free_gib=21)
    if not admission['admitted']: raise ValueError('20 GiB reserve plus 1 GiB scratch reservation unavailable')
    output.mkdir(); started=time.perf_counter()
    report=dict(schema='osr-corridor-stage-profile/1',runtime_root=str(root),
        runtime_source_commit=commit,runtime_source_tree=tree,
        profiler_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        profiler_source_commit=_git(Path(__file__).parent,'rev-parse','HEAD'),
        admission=admission,trials=[],complete=False,native_solver_jobs=0,CAD_jobs=0,
        maximum_output_bytes=GIB,
        trial_semantics='First call and same-process repeated recomputation into fresh stores, not retained-job cache hits. No OS/filesystem cache flushing.',
        resource_enforcement='Admission and between-case allocation/time checks; no aggregate quota or hard process-tree containment.')
    def save():
        report['total_wall_seconds']=time.perf_counter()-started
        (output/'profile.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
    def check_budget():
        size=sum(p.stat().st_size for p in output.rglob('*') if p.is_file())
        if time.perf_counter()-started>=maximum_wall_seconds or size>=GIB or not disk_admission(output,minimum_free_gib=20)['admitted']:
            raise ValueError('Profile invocation budget exhausted; completed cases retained')
    try:
        def prepare():
            from engineering.outline import corridor_revision,city_workflow
            return corridor_revision.proposal(root),city_workflow
        (proposal,workflow),report['proposal_profile']=profile_call(prepare,output/'proposal.pstats')
        report['proposal_id']=proposal['proposal_id']
        for trial in range(trials):
            row=dict(index=trial,cases={});report['trials'].append(row)
            for side,key in [('before','baseline_request'),('after','revised_request')]:
                check_budget();folder=output/f'trial-{trial}-{side}'
                manifest,timing=profile_call(lambda:workflow.run(proposal[key],folder,root=root),output/f'trial-{trial}-{side}.pstats')
                timing.update(manifest_id=manifest['manifest_id'],evaluation_id=manifest['evaluation_id'],
                    worker_performance=json.loads((folder/'performance.json').read_bytes()),
                    summary=json.loads((folder/'summary.json').read_bytes()))
                row['cases'][side]=timing;save()
        check_budget()
        if _git(root,'rev-parse','HEAD')!=commit or _git(root,'status','--porcelain','--untracked-files=all'):
            raise ValueError('Runtime source changed during profiling')
        report['complete']=True
    except BaseException as error:
        report['failure']=dict(type=type(error).__name__,message=str(error));save();raise
    save();return report


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',type=Path,required=True);parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--trials',type=int,default=1);args=parser.parse_args()
    result=run(args.root,args.output,trials=args.trials)
    print(json.dumps(dict(complete=result['complete'],output=str(args.output),trials=len(result['trials']),total_wall_seconds=result['total_wall_seconds'])))


if __name__=='__main__':main()
