#!/usr/bin/env python3
"""Publish compact integrity-checked numerical review evidence with source scope."""
from pathlib import Path
import argparse,hashlib,json,sys,tomllib
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from engineering.civil_exploration.constraints import convergence
PUBLIC=ROOT/'engineering/integration_programme/evidence'


def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda:stream.read(1024*1024),b''):h.update(chunk)
    return h.hexdigest()


def write(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,indent=2,sort_keys=True,allow_nan=False)+'\n')


def retained(folder):
    receipt_path=folder/'receipt.json';receipt=json.loads(receipt_path.read_text())
    if receipt.get('physical_validation') is not False:raise ValueError('numerical review requires explicit nonphysical scope')
    hashes=receipt.get('outputs_sha256',receipt.get('output_sha256'))
    if not isinstance(hashes,dict) or not hashes:raise ValueError('retained execution has no output integrity map')
    for name,digest in hashes.items():
        path=(folder/name).resolve()
        if not path.is_relative_to(folder) or not path.is_file() or sha(path)!=digest:raise ValueError('retained output changed: '+name)
    sources=receipt.get('sources_sha256',receipt.get('source_sha256'))
    if not isinstance(sources,dict) or not sources:raise ValueError('retained execution has no source scope')
    changed=[]
    for name,digest in sources.items():
        path=(ROOT/name).resolve()
        if not path.is_relative_to(ROOT):raise ValueError('source escapes repository')
        if not path.is_file() or sha(path)!=digest:changed.append(name)
    return dict(receipt_sha256=sha(receipt_path),retained_receipt=receipt,
        current_recorded_sources_match=not changed,changed_recorded_sources=changed,
        evidence_status='current-recorded-source-scope' if not changed else 'historical-source-scope',
        large_histories_published=False,physical_validation=False,production_released=False)


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--service',type=Path,action='append',default=[])
    p.add_argument('--coupling',type=Path,action='append',default=[]);p.add_argument('--integration',type=Path)
    p.add_argument('--recovery',type=Path);p.add_argument('--checkpoint',type=Path);p.add_argument('--proofs',type=Path)
    p.add_argument('--reference-refinement',type=Path,action='append',default=[]);a=p.parse_args()
    outputs=[]
    def save(name,row):write(PUBLIC/name,row);outputs.append(name)
    for folder in a.service:
        folder=folder.resolve();row=retained(folder);row['report']=json.loads((folder/'summary.json').read_text())
        save(folder.name+'.json',row)
    for folder in a.coupling:
        folder=folder.resolve();row=retained(folder);row['report']=json.loads((folder/'review.json').read_text())
        dynamics=json.loads((folder/'dynamics.json').read_text())
        row['numerical_metrics']={k:dynamics[k] for k in ('maximum_wheel_contact_n','minimum_wheel_contact_n','maximum_wheel_unloading','peak_structure_displacement_m','peak_ride_acceleration_m_s2')}
        save(folder.name+'.json',row)
    if a.integration:
        folder=a.integration.resolve();row=retained(folder)
        names=['civil-cad-analysis-audit.json','shell-execution.json','flexible-vehicle-operators.json','battery-mount-pilot.json','station-cases.json','civil-lifecycle-review.json','osrd-twin-comparison.json']
        row['reports']={name:json.loads((folder/name).read_text()) for name in names if (folder/name).is_file()}
        save('integration-pilot.json',row)
    # Recovery public reports contain counts/results, never the private checkpoint
    # state, environment, keys, bindings or archives.
    if bool(a.recovery)!=bool(a.checkpoint):raise ValueError('recovery requires both public execution reports')
    if a.recovery:
        recovery=json.loads(a.recovery.read_text());checkpoint=json.loads(a.checkpoint.read_text())
        if not recovery.get('passed') or not checkpoint.get('passed') or not checkpoint.get('source_resumed') or not recovery.get('isolated_resources_removed'):
            raise ValueError('incomplete recovery execution')
        if recovery['checkpoint_sha256']!=checkpoint['manifest_sha256']:raise ValueError('recovery targets another checkpoint')
        save('isolated-recovery.json',dict(recovery=recovery,checkpoint=checkpoint,source_reports_sha256={a.recovery.name:sha(a.recovery),a.checkpoint.name:sha(a.checkpoint)},
            independent_host_acceptance=False,operational_cutover_accepted=False,physical_validation=False))
    if a.proofs:
        execution_path=a.proofs/'execution.json';results_path=a.proofs/'results.toml'
        execution=json.loads(execution_path.read_text())
        if sha(results_path)!=execution['results_sha256']:raise ValueError('formal results changed')
        rows=[]
        for result in tomllib.loads(results_path.read_text())['result']:
            log=(ROOT/result['report']).resolve()
            if not log.is_relative_to(ROOT) or sha(log)!=result['report_sha256']:raise ValueError('formal log changed')
            rows.append({key:value for key,value in result.items() if key!='inputs'})
        changed=[name for name,digest in execution['inputs'].items() if not (ROOT/name).is_file() or sha(ROOT/name)!=digest]
        save('open-formal-obligations.json',dict(execution=execution,results=rows,execution_sha256=sha(execution_path),
            current_recorded_sources_match=not changed,changed_recorded_sources=changed,
            obligations_discharged=False,scope='retained resource-bound attempts; timeouts/tool/resource failures establish no proof',physical_validation=False))
    metrics=['maximum_wheel_contact_n','peak_structure_displacement_m','peak_ride_acceleration_m_s2','maximum_wheel_unloading']
    if a.reference_refinement:
        levels=[];identities=set();environments=set()
        for folder in a.reference_refinement:
            folder=folder.resolve();evidence=retained(folder);summary=json.loads((folder/'summary.json').read_text())
            if len(summary['cases'])!=1 or summary['cases'][0]['status']!='completed':raise ValueError('refinement needs one completed case per folder')
            case=summary['cases'][0]['case'];result=json.loads((folder/case/'dynamics.json').read_text())
            identities.add((result['hardware_definition_sha256'],sha(folder/case/'configuration.json')))
            environments.add(json.dumps(evidence['retained_receipt']['solver_environment'],sort_keys=True))
            levels.append(dict(name=folder.name,budgets=summary['budgets'],evidence=evidence,metrics={k:result[k] for k in metrics}))
        if len(identities)!=1 or len(environments)!=1:raise ValueError('refinement configuration/environment differs')
        temporal=[];spatial=[]
        for prior,current in zip(levels,levels[1:]):
            a1,a2=prior['budgets'],current['budgets']
            check=convergence([prior['metrics'],current['metrics']],metrics)
            row=dict(coarse=prior['name'],fine=current['name'],comparison=check)
            if a1['deck_mesh']==a2['deck_mesh'] and a1['rail_step_m']==a2['rail_step_m'] and a2['time_step_s']<a1['time_step_s']:temporal.append(row)
            elif a1['time_step_s']==a2['time_step_s'] and a2['deck_mesh']>a1['deck_mesh'] and a2['rail_step_m']<a1['rail_step_m']:spatial.append(row)
            else:raise ValueError('time and spatial refinement must be separate')
        save('reference-refinement.json',dict(levels=levels,temporal=temporal,spatial=spatial,
            final_temporal_passed=bool(temporal) and temporal[-1]['comparison']['passed'],final_spatial_passed=bool(spatial) and spatial[-1]['comparison']['passed'],
            scope='one reference passage, independent step and mesh screens; no complete operating envelope or physical acceptance',physical_validation=False))
    if len(a.coupling)>1:
        levels=[]
        for folder in a.coupling:
            report=json.loads((folder/'review.json').read_text());result=json.loads((folder/'dynamics.json').read_text())
            levels.append(dict(name=folder.name,dt_s=report['dt_s'],configuration_sha256=report['analysis_configuration_sha256'],metrics={k:result[k] for k in metrics}))
        if len({r['configuration_sha256'] for r in levels})!=1 or any(b['dt_s']>=a['dt_s'] for a,b in zip(levels,levels[1:])):
            raise ValueError('coupling refinement requires identical configuration and decreasing timesteps')
        save('native-coupling-refinement.json',dict(levels=levels,comparisons=[dict(coarse=a['name'],fine=b['name'],comparison=convergence([a['metrics'],b['metrics']],metrics)) for a,b in zip(levels,levels[1:])],
            scope='one-second prescribed-transport perturbation; temporal screening only; spatial/operating/physical qualification remains open',physical_validation=False))
    write(PUBLIC/'manifest.json',dict(schema='osr-published-integration-review/1',producer_sha256=sha(Path(__file__)),producer_dependencies_sha256={'engineering/civil_exploration/constraints.py':sha(ROOT/'engineering/civil_exploration/constraints.py')},
        artifact_sha256={name:sha(PUBLIC/name) for name in outputs},scope='numerical and isolated software review; open task register remains authoritative',
        physical_validation=False,production_released=False))
    print(json.dumps(dict(published_files=outputs,physical_validation=False)))


if __name__=='__main__':main()
