"""Bounded final-load comparison with rotation-free bearing-line supports.

This is an additional source-bound experiment. Historical finite-patch packets
and their failures remain unchanged and independently replayable.
"""
import argparse,json,resource,time,sys
from pathlib import Path
from engineering.station_rail.common import identity,encoded,digest
from engineering.design_search.craft_backends import freecad_reference,native
from . import FLAGS,ROOT
from .design import evaluate,validate_train,seal
from .native_trial import source_context,generate,prepare,trial,support_audit,analytical_reference


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--axle-input',required=True,type=Path)
    parser.add_argument('--upstream-root',required=True,type=Path)
    parser.add_argument('--output',required=True,type=Path)
    parser.add_argument('--prior-case',action='append',default=[],type=Path)
    args=parser.parse_args();out=args.output.resolve();out.mkdir(parents=True,exist_ok=False)
    start=time.monotonic();before=source_context();train=json.loads(args.axle_input.read_bytes());validate_train(train,args.upstream_root)
    def write(name,value):
        path=out/name
        if path.exists():raise ValueError('Fresh immutable record required')
        path.write_bytes(encoded(value))
    write('axle-input.json',train);write('source-before.json',before)
    budget=dict(max_cells=50000,cpu_s_each_process=75,wall_s_each_process=73,memory_mib_each_process=3072)
    write('request.json',seal(dict(schema='osr-pilot-civil-final-request/1',system_candidate_id=train['candidate_id'],input_load_evaluation_id=train['evaluation_id'],source_sha256=before,
        purpose='Numerical model comparison only',command_argv=[sys.executable,'-m','engineering.pilot_civil.final_trial',*sys.argv[1:]],resources=budget,max_fem_cases=3,max_solidcraft_jobs=1,max_freecad_checks=1,private_disk_limit_bytes=int(1.5*1024**3),
        mesh_sizes_m=[.30,.25,.20],support_mode='rotation-free-line',load_case='normal-base',
        budget_revision_reason='Coordinator explicitly approved final-load verification with up to50k cells/3GiB/75CPU/100s wall; actual wall73s keeps existing wrappers CPU hard limit75s. Engineering5% refinement target unchanged.',
        rolling_checkpoints='Eight private scratch slots, overwritten under recorded command log; final retained files hashed. No immutable inputs/results overwritten.',**FLAGS)))
    audits=[]
    for path in args.prior_case:
        model=json.loads((path/'mesh.json').read_bytes());result=json.loads((path/'result.json').read_bytes())
        audits.append(dict(path=str(path),mesh_id=model['mesh_id'],evaluation_id=result['evaluation_id'],findings=support_audit(model,result['calculix'],{})))
    write('prior-support-audit.json',seal(dict(cases=audits,interpretation='Finite longitudinal fixed-U3 patches transmit a bending couple, making pin-based beam comparisons inconsistent. New transverse lines remove that numerical clamp; finite bearing contact/compliance still requires its own model.',**FLAGS)))
    civil=evaluate(train,family='folded_plate',revision='thick-web',soil_case='base',upstream_root=args.upstream_root)
    write('civil.json',civil)
    cad=generate(civil,out/'gross-beam-cad',gross_beam_only=True)
    records=[];ref=None;spec=None;reference=None
    if cad.get('gross_volume_screen_passed'):
        reference=freecad_reference.run(cad['step_path'],out/'independent-freecad',timeout_s=73,memory_mb=3072)
        write('independent-cad-summary.json',reference)
        spec=prepare(civil,train,cad,'normal-base',support_mode='rotation-free-line',resources=budget)
        write('native-input.json',spec);ref=analytical_reference(civil,spec);write('analytical-reference.json',ref)
        for i,size in enumerate((.30,.25,.20),1):
            record=trial(spec,out/('case-'+str(i)),size_m=size);records.append(record)
            if record.get('failure_reason') or any(k not in record for k in ('fieldcraft','calculix')):break
            if sum(p.stat().st_size for p in out.rglob('*') if p.is_file())>1.5*1024**3:break
    refinements=[]
    for a,b in zip(records,records[1:]):
        if all(k in a and k in b for k in ('fieldcraft','calculix')):
            u=a['fieldcraft']['displacement_m'][2];v=b['fieldcraft']['displacement_m'][2]
            refinements.append(dict(coarse_evaluation_id=a['evaluation_id'],fine_evaluation_id=b['evaluation_id'],relative_change=abs(u-v)/abs(v),target=.05,screen_passed=abs(u-v)/abs(v)<=.05))
    after=source_context();upstream_after={n:digest(args.upstream_root/n) for n in train['source_sha256']}
    write('source-after.json',after);write('upstream-source-after.json',upstream_after)
    summary=[]
    for r in records:
        row={k:r.get(k) for k in ('evaluation_id','size_m','cells','nodes','mesh_id','failure_reason','fieldcraft_failure','calculix_failure','cross_solver_relative_difference','cross_solver_screen_passed','support_audit')}
        for tool in ('fieldcraft','calculix'):
            if tool in r:row[tool]={k:v for k,v in r[tool].items() if k not in ('reaction_distribution','raw_external_RF_N')}
        if ref and 'fieldcraft' in r:
            u=r['fieldcraft']['displacement_m'][2];eb=ref['Euler_Bernoulli_displacement_m'];ts=ref['declared_Timoshenko_displacement_m']
            row.update(relative_difference_from_Euler_Bernoulli=abs(u-eb)/abs(eb),relative_difference_from_declared_Timoshenko=abs(u-ts)/abs(ts))
        summary.append(row)
    report=seal(dict(schema='osr-pilot-civil-final-report/1',system_candidate_id=train['candidate_id'],input_load_evaluation_id=train['evaluation_id'],civil_candidate_id=civil['civil_candidate_id'],civil_evaluation_id=civil['evaluation_id'],native_input_id=spec['input_id'] if spec else None,
        source_unchanged=before==after,upstream_source_unchanged=upstream_after==train['source_sha256'],analytical_reference=ref,results=summary,refinements=refinements,
        refinement_screen_passed=bool(refinements) and all(r['screen_passed'] for r in refinements),
        execution_wall_s=time.monotonic()-start,coordinator_peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        limitations=['Rotation-free line supports deliberately exclude actual finite elastomer/contact stiffness, unilateral lift-off and local support-stress interpretation.',
        'Gross bonded elastic concrete; no segment joint, reinforcement/prestress, cracking, fatigue, local anchorage or construction qualification.',
        'Train lateral inertia, full torsion/handling and soil/settlement remain independent analytical/physical gates.',
        'Same-pose Euler and Timoshenko comparisons test model consistency; neither becomes measured evidence.',
        'Single normal-base native load case; low/high and crowd controls remain analytical scenarios, not newly solved3D cases.'],**FLAGS))
    write('report.json',report)
    files={str(p.relative_to(out)):dict(sha256=digest(p),bytes=p.stat().st_size) for p in out.rglob('*') if p.is_file()}
    write('manifest.json',seal(dict(schema='osr-pilot-civil-final-manifest/1',files=files,total_bytes=sum(v['bytes'] for v in files.values()),**FLAGS)))
    print(json.dumps(dict(output=str(out),report_id=report['evaluation_id'],native_cases=len(records),refinement_screen_passed=report['refinement_screen_passed'],source_unchanged=report['source_unchanged'],upstream_source_unchanged=report['upstream_source_unchanged'])))
    if before!=after or upstream_after!=train['source_sha256']:raise SystemExit('Source drift retained; numerical evidence held')

if __name__=='__main__':main()
