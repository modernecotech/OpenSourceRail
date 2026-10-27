"""Portable recorded-output verification for the independent static subset.

Never invokes GetDP or requires the original executable path. The native
producer and its receipts remain unchanged; current verification is separate.
"""
from pathlib import Path,PurePosixPath
from hashlib import sha256
from math import isclose,isfinite,fsum
import argparse,gzip,io,json,tarfile,tempfile
import numpy as np
from engineering.station_rail import ROOT,FLAGS
from engineering.station_rail.common import encoded,identity,digest
from . import lim_static_benchmark as static,moving_lim

CODE='engineering/design_search/lim_static_publication.py'
OUTPUT='docs/design-engine/lim-static-field'
PRODUCER_SHA='cfaec43dc265d6b85a53296fbda8fe9ffceb7433a04d0f6e32bcb95b5f17303f'


def _id(value,key):
    if value.get(key)!=identity({k:v for k,v in value.items() if k!=key}):raise ValueError('Static identity differs: '+key)


def _unaccepted(value):
    if isinstance(value,dict):
        if any(k in (*FLAGS,'configuration_adopted','operating_map_admitted') and v is not False for k,v in value.items()):
            raise ValueError('Static qualification/release claim forbidden')
        for v in value.values():_unaccepted(v)
    elif isinstance(value,list):
        for v in value:_unaccepted(v)


def _same(a,b):
    if type(a) is bool or type(b) is bool:return a is b
    if isinstance(a,(int,float)) and isinstance(b,(int,float)):
        return isfinite(a) and isfinite(b) and isclose(a,b,rel_tol=1e-7,abs_tol=1e-14)
    if isinstance(a,dict) and isinstance(b,dict):return set(a)==set(b) and all(_same(a[k],b[k]) for k in a)
    if isinstance(a,list) and isinstance(b,list):return len(a)==len(b) and all(_same(x,y) for x,y in zip(a,b))
    return a==b


def sources(root=ROOT):return {**static.sources(root),CODE:digest(Path(root)/CODE)}


def _diagnostics_same(actual,recorded):
    # Closed positive/negative source cancellation uses a BLAS dot reduction;
    # the recorded/default thread contexts differ by about5e-14A here.
    key='global_imposed_source_current_A'
    return (set(actual)==set(recorded) and isclose(actual[key],recorded[key],rel_tol=0.,abs_tol=1e-10)
        and _same({k:v for k,v in actual.items() if k!=key},{k:v for k,v in recorded.items() if k!=key}))


def collect(execution,root=ROOT):
    execution=Path(execution);plan=static.read(execution/'plan.json');campaign=static.read(execution/'campaign.json');receipt=static.read(execution/'manifest.json')
    for value,key in ((plan,'plan_id'),(campaign,'campaign_id'),(receipt,'manifest_id')):_id(value,key)
    for value in (plan,campaign,receipt):_unaccepted(value)
    files={p.relative_to(execution).as_posix():digest(p) for p in execution.rglob('*') if p.is_file() and p.name!='manifest.json'}
    # Only the root manifest is excluded; nested parent receipts remain owned.
    for p in execution.rglob('manifest.json'):
        if p!=execution/'manifest.json':files[p.relative_to(execution).as_posix()]=digest(p)
    if files!=receipt['files_sha256'] or receipt['plan_id']!=plan['plan_id'] or receipt['campaign_id']!=campaign['campaign_id']:
        raise ValueError('Static raw inventory or receipt binding differs')
    if (plan['source_sha256']!=static.sources(root) or plan['source_sha256'].get(static.CODE)!=PRODUCER_SHA
        or {p.relative_to(execution/'source').as_posix():digest(p) for p in (execution/'source').rglob('*') if p.is_file()}!=plan['source_sha256']):
        raise ValueError('Exact static producer/source epoch differs')
    if (plan['maximum_component_jobs'],plan['maximum_campaign_seconds'],plan['maximum_nodes'])!=(4,240,75000):raise ValueError('Static numerical budget differs')
    parent=plan['parent_request'];moving_lim.validate(parent)
    if parent['bundle_id']!=static.BUNDLE or parent['motor_component_id']!=static.MOTOR:raise ValueError('Static physical parent differs')
    parent_input=static.read(execution/'parent'/'input.json');parent_result=static.read(execution/'parent'/'result.json')
    _id(parent_result,'evaluation_id')
    parent_receipt=static.read(execution/'parent'/'manifest.json');_id(parent_receipt,'manifest_id')
    for value in (parent_input,parent_result,parent_receipt):_unaccepted(value)
    if (parent_receipt['evaluation_id']!=parent_result['evaluation_id']
        or parent_receipt['source_sha256']!=moving_lim.sources(root)
        or parent_input['source_sha256']!=parent_receipt['source_sha256'] or parent_result['source_sha256']!=parent_receipt['source_sha256']
        or {p.name:digest(p) for p in (execution/'parent').iterdir() if p.is_file() and p.name!='manifest.json'}!=parent_receipt['files_sha256']):
        raise ValueError('Static parent source/receipt differs')
    if parent_input['request']!=parent or digest(execution/'parent'/'result.json')!=plan['parent_result_sha256'] or parent_result['evaluation_id']!=plan['parent_evaluation_id']:
        raise ValueError('Static parent identity differs')
    if (parent_result['request_id'],parent_result['bundle_id'],parent_result['motor_component_id'])!=(parent['request_id'],parent['bundle_id'],parent['motor_component_id']):
        raise ValueError('Static parent result context differs')
    if plan['cases']!=static.case_requests(parent,parent_result['trace'][-1]['path_currents_A']):raise ValueError('Static imposed-source cases differ')
    if (plan['tool']['version']!='3.5.0' or len(plan['tool']['sha256'])!=64 or campaign['plan_id']!=plan['plan_id']
        or campaign['source_sha256']!=plan['source_sha256'] or campaign['attempted_jobs']!=4 or campaign['completed_jobs']!=4
        or len(campaign['rows'])!=4 or campaign['elapsed_s']>240):raise ValueError('Completed static campaign contract differs')
    data=static.mesh_data(parent);points,tri,regions,boundary,branch,sign,area,grad,tags,outer=data
    if (moving_lim.mesh_fingerprint(*data[:6])!=plan['actual_mesh'] or len(points)>75000
        or (plan['nodes'],plan['elements'],plan['free_nodes'],plan['signed_source_regions'])!=(len(points),len(tri),len(points)-len(boundary),60)):
        raise ValueError('Static actual mesh differs')
    mesh=static.msh_text(points,tri,tags,outer);arrays={};rows=[]
    for case,row in zip(plan['cases'],campaign['rows']):
        _id(case,'request_id');_id(row,'evaluation_id');folder=execution/case['name']
        if (row!=static.read(folder/'result.json') or static.read(folder/'input.json')!=dict(plan=plan,case=case)
            or row['request_id']!=case['request_id'] or row['plan_id']!=plan['plan_id'] or row['name']!=case['name']
            or row['execution']!='completed' or row['elapsed_outer_s']>90 or row['elapsed_s']>85
            or row.get('physical_accepted') is not False or row.get('operating_map_admitted') is not False):
            raise ValueError('Static executed case binding differs')
        worker=static.read(folder/'worker-result.json')
        for value in (case,row,worker):_unaccepted(value)
        if set(worker)!= {'execution','analysis','elapsed_s'} or any(row[k]!=v for k,v in worker.items()):raise ValueError('Static worker/result binding differs')
        command=[plan['tool']['path'],'model.pro','-msh','model.msh','-solve','Solve','-pos','Result','-v','4','-skip_petscrc','-ksp_type','cg','-pc_type','icc','-ksp_rtol','1e-12','-ksp_atol','1e-14','-ksp_max_it','20000','-ksp_error_if_not_converged']
        if static.read(folder/'command.json')!=dict(command=command,threads=1):raise ValueError('Static recorded native command differs')
        if (folder/'model.msh').read_text()!=mesh or (folder/'model.pro').read_text()!=static.formulation(parent,case['path_currents_A']):
            raise ValueError('Executed static mesh/formulation differs')
        actual=static.analyze(folder,parent,case['path_currents_A'],data)
        if not _diagnostics_same(actual,row['analysis']):raise ValueError('Static analysis differs from recorded tables')
        a=row['analysis'];energy=abs(a['getdp_energy_J']);tol=1e-10*max(energy,1e-6)+1e-14
        if (not a['numerical_subset_agreement'] or a['reference_operator_residual']>1e-8
            or a['boundary_A_maximum_absolute_Wb_m']>1e-10
            or abs(a['global_imposed_source_current_A'])>1e-10
            or abs(a['getdp_source_work_minus_twice_energy_J'])>tol
            or abs(a['reference_source_work_minus_twice_energy_J'])>tol):raise ValueError('Static work/boundary/operator numerical screen failed')
        arrays[case['name']]=(static.node_table(folder/'a.txt',len(points)),static.element_table(folder/'b.txt',len(tri)))
        rows.append(row)
    zero,forward,reverse,unit=[arrays[n] for n in static.NAMES]
    if any(np.any(v!=0.) for v in zero) or any(rows[0]['analysis'][k]!=0. for k in ('getdp_energy_J','getdp_source_work_J')):raise ValueError('Static zero-source control failed')
    polarity_A=float(max(abs(forward[0]+reverse[0])));polarity_B=float(max(abs(forward[1]+reverse[1]).ravel()))
    if polarity_A>1e-10 or polarity_B>1e-10 or not isclose(rows[1]['analysis']['getdp_energy_J'],rows[2]['analysis']['getdp_energy_J'],rel_tol=1e-8,abs_tol=1e-14):raise ValueError('Static polarity control failed')
    density=parent['physical_geometry']['turns_per_coil']/(parent['physical_geometry']['slot_width_m']*parent['physical_geometry']['slot_depth_m'])
    def cross(currents,A):
        J=np.zeros(len(tri));mask=branch>=0;J[mask]=sign[mask]*density*np.asarray(currents)[branch[mask]]
        return parent['physical_geometry']['active_height_m']*fsum((area*J*A[tri].mean(axis=1)).tolist())
    left=cross(plan['cases'][1]['path_currents_A'],unit[0]);right=cross(plan['cases'][3]['path_currents_A'],forward[0])
    reciprocity=abs(left-right)
    if reciprocity>1e-8*max(abs(left),abs(right),1e-6)+1e-14:raise ValueError('Static reciprocity numerical screen failed')
    for v in (plan,campaign,receipt):
        if v.get('physical_accepted') is not False or v.get('operating_map_admitted',False) is not False:raise ValueError('Static acceptance forbidden')
    return dict(plan_id=plan['plan_id'],campaign_id=campaign['campaign_id'],tool_record=plan['tool'],
        physical_bundle_id=parent['bundle_id'],motor_component_id=parent['motor_component_id'],execution_wall_s=campaign['elapsed_s'],
        resource_budget=dict(maximum_jobs=4,maximum_nodes=75000,address_space_bytes_per_job=2*1024**3,external_seconds_per_job=90,total_seconds=240,actual_peak_RAM_bytes=None),
        recorded_runtime=plan['runtime'],original_executable_available_or_rechecked=False,
        mesh_discretization_id=plan['actual_mesh']['mesh_discretization_id'],nodes=len(points),rows=rows,
        comparisons=dict(zero_exact=True,polarity_A_maximum_absolute_Wb_m=polarity_A,polarity_B_maximum_absolute_T=polarity_B,
            reciprocity_source_work_left_J=left,reciprocity_source_work_right_J=right,reciprocity_residual_J=reciprocity,
            verification_diagnostic_relative_tolerance=1e-7,verification_diagnostic_absolute_tolerance=1e-14,
            verification_closed_source_current_absolute_tolerance_A=1e-10),
        scope=static.SCOPE,configuration_adopted=False,operating_map_admitted=False,**FLAGS)


def _archive(execution,context):
    stream=io.BytesIO()
    with tarfile.open(fileobj=stream,mode='w') as tar:
        for prefix,root in (('execution',Path(execution)),('context',Path(context))):
            for p in sorted(root.rglob('*')):
                if p.is_symlink():raise ValueError('Static archive symlink refused')
                if not p.is_file():continue
                data=p.read_bytes();entry=tarfile.TarInfo(prefix+'/'+p.relative_to(root).as_posix());entry.size=len(data);entry.mode=0o644;entry.mtime=0
                tar.addfile(entry,io.BytesIO(data))
    return gzip.compress(stream.getvalue(),mtime=0)


def _readme(report):
    table='\n'.join('| '+row['name']+f" | {row['analysis']['getdp_energy_J']:.8g} | {row['analysis']['cell_B_relative_area_L2']:.3g} | {row['analysis']['energy_relative_error']:.3g} |" for row in report['rows'])
    return ('# Independent linear static LIM field benchmark\n\n'
        'Four bounded GetDP 3.5.0 comparisons use the exact 44,643-node motor mesh, 60 signed winding groups and imposed zero, archived-current, reversed-current and single-path basis sources. '
        'The linear steel permeability of 1000 is an unverified numerical hypothesis. Geometry is shared; GetDP independently assembles the field operator and source.\n\n'
        f"Research parent: `{report['physical_bundle_id']}`; exact motor geometry: `{report['motor_component_id']}`. Execution took {report['execution_wall_s']:.2f} seconds.\n\n"
        '| Mathematical source | Static energy, J | Field comparison error | Energy comparison error |\n|---|---:|---:|---:|\n'+table+'\n\n'
        '**This is a static field subset, with no moving secondary, eddy-current, circuit, controller, thermal, force-map, journey or physical qualification.** '
        'The single-path mathematical source is not a permissible floating-neutral drive point. Moving-entry thrust remains negative and time convergence remains open in the [separate moving experiment](../moving-lim-method/README.md).\n\n'
        'Potential, cell field, energy, source-work balance, boundary conditions, zero response, polarity and reciprocity are checked against the archived tables. '
        'Small comparison errors verify this shared-mesh numerical subset; they do not establish whole-domain convergence or actual material properties.\n\n'
        'Portable verification reads recorded outputs without invoking GetDP or requiring the original executable path. The recorded tool checksum/version and producer epoch remain bound to the original receipts; executable availability is not rechecked. '
        'Derived diagnostics permit explicit floating-point verification tolerances of relative 1e-7 and absolute 1e-14, with absolute 1e-10 A for closed-source cancellation across reduction contexts; these are numerical checks, not physical acceptance limits.\n\n'
        '[Assessment](assessment.json) · [Original inputs, outputs, logs and frozen sources](native-runs.tar.gz) · [Receipt](manifest.json)\n\n'
        'Run `python -m engineering.design_search.lim_static_publication verify`.\n')


def publish(execution,context,*,root=ROOT,output=None,replace=False):
    target=Path(output) if output else Path(root)/OUTPUT
    if target.exists():
        if not replace:raise ValueError('Fresh static publication required; use explicit replacement for owned generated files')
        previous=static.read(target/'manifest.json');_id(previous,'manifest_id')
        if (set(p.name for p in target.iterdir())!={'README.md','assessment.json','manifest.json','native-runs.tar.gz'}
            or any(p.is_symlink() for p in target.iterdir())
            or {p.name:digest(p) for p in target.iterdir() if p.name!='manifest.json'}!=previous['files_sha256']):raise ValueError('Static owned publication inventory differs')
    report=collect(execution,root);archive=_archive(execution,context);report.update(schema='osr-LIM-static-field-publication/1',archive_sha256=sha256(archive).hexdigest(),source_sha256=sources(root));report['publication_id']=identity(report)
    target.mkdir(parents=True,exist_ok=True);(target/'assessment.json').write_bytes(encoded(report));(target/'native-runs.tar.gz').write_bytes(archive);(target/'README.md').write_text(_readme(report))
    receipt=dict(publication_id=report['publication_id'],source_sha256=sources(root),files_sha256={p.name:digest(p) for p in target.iterdir() if p.name!='manifest.json'},configuration_adopted=False,**FLAGS);receipt['manifest_id']=identity(receipt);(target/'manifest.json').write_bytes(encoded(receipt));return verify(target,root=root)


def verify(output=None,*,root=ROOT):
    target=Path(output) if output else Path(root)/OUTPUT;m=static.read(target/'manifest.json');r=static.read(target/'assessment.json');_id(m,'manifest_id');_id(r,'publication_id')
    _unaccepted(m);_unaccepted(r)
    if m['source_sha256']!=sources(root) or r['source_sha256']!=sources(root) or m['publication_id']!=r['publication_id'] or {p.name:digest(p) for p in target.iterdir() if p.name!='manifest.json'}!=m['files_sha256']:raise ValueError('Static publication source/payload differs')
    if any(r.get(k) is not v or m.get(k) is not v for k,v in FLAGS.items()) or r['operating_map_admitted'] is not False:raise ValueError('Static publication cannot grant acceptance')
    archive=(target/'native-runs.tar.gz').read_bytes()
    if sha256(archive).hexdigest()!=r['archive_sha256'] or (target/'README.md').read_text()!=_readme(r):raise ValueError('Static archive/explanation differs')
    with tempfile.TemporaryDirectory(prefix='osr-static-packet-') as folder:
        path=Path(folder);seen=set();size=0
        with tarfile.open(fileobj=io.BytesIO(archive),mode='r:gz') as tar:
            for member in tar:
                p=PurePosixPath(member.name);size+=member.size
                if (not member.isfile() or p.is_absolute() or '..' in p.parts or p.as_posix()!=member.name or p.parts[0] not in ('execution','context')
                    or member.name in seen or member.size>20*1024**2 or size>100*1024**2):raise ValueError('Ordinary unique bounded static archive required')
                seen.add(member.name);dest=path/p;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(tar.extractfile(member).read())
        actual=collect(path/'execution',root)
        expected={k:v for k,v in r.items() if k not in ('schema','archive_sha256','source_sha256','publication_id')}
        if not _same(actual,expected):raise ValueError('Static assessment differs from archived executions')
    return dict(verified=True,publication_id=r['publication_id'],static_cases=4,operating_map_admitted=False,physical_accepted=False)


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('action',choices=('publish','verify'));p.add_argument('--execution',type=Path);p.add_argument('--context',type=Path);p.add_argument('--output',type=Path);p.add_argument('--replace',action='store_true');a=p.parse_args()
    if a.action=='publish' and (a.execution is None or a.context is None):p.error('Explicit sealed execution and separate context required')
    print(json.dumps(publish(a.execution,a.context,output=a.output,replace=a.replace) if a.action=='publish' else verify(a.output),sort_keys=True))


if __name__=='__main__':main()
