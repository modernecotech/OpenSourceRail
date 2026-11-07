"""One explicit numerical-resource revision of frozen exact-CAD FEM evidence.

Only the previously held fine FieldCraft solve is fresh. Geometry meshing,
coarse FieldCraft and both CalculiX calculations retain their original roles,
identities and 2GiB resource requests. A larger numerical budget grants no new
physical evidence or approval.
"""
from pathlib import Path
import json
from . import native,identity,FLAGS
from . import viaduct_fem as fem
from .fieldcraft import batch_results

SOURCE='engineering/design_search/craft_backends/viaduct_fem_resource.py'


def sources():
    return {**fem.sources(),SOURCE:native.digest(__file__)}


def physics_commands(commands):
    """Scope paths/checkpoint storage may change; physical command data may not."""
    result=[]
    for row in commands:
        if row['command'] in ('file.save','file.open'):continue
        row=json.loads(json.dumps(row))
        if row['command']=='deck.read':row['params']['path']='<exact-imported-mesh>'
        result.append(row)
    return result


def comparisons(field,coarse,ccx):
    u=field['displacement_m'][2];reference=ccx['displacement_m'][2]
    if not u or not reference:raise ValueError('Nonzero bending observation required')
    cross=abs(u-reference)/abs(reference);refine=abs(coarse['displacement_m'][2]-u)/abs(u)
    return dict(cross_solver_displacement_relative_difference=cross,
        cross_solver_screen_passed=cross<=fem.SCREENS['cross_solver_displacement_relative'],
        displacement_refinement_relative_change=refine,
        displacement_refinement_screen_passed=refine<=fem.SCREENS['displacement_refinement_relative'],
        mesh_independence_established=False)


def parse(replies,model):
    rows=[]
    for reply in replies:
        if reply.get('id',0)<=1:continue
        if reply.get('result',{}).get('isError'):
            try:
                failed=json.loads(reply['result']['content'][0]['text']).get('failed')
                if failed:raise ValueError('FieldCraft numerical hold: '+str(failed))
            except (KeyError,IndexError,json.JSONDecodeError):pass
        rows.extend(batch_results(native.payload(reply)))
    return fem.parse_field(rows,model)


def revisionrun(spec,original_case_run,output,*,memory_mb=3072):
    if memory_mb!=3072:raise ValueError('Only the explicitly budgeted 3072MiB/120s revision is admitted')
    original=Path(original_case_run).resolve();receipt=fem.verify(original,spec)
    prior=json.loads((original/'result.json').read_text());old_request=json.loads((original/'request.json').read_text())
    coarse=prior['levels']['coarse']['results'];fine=prior['levels']['fine']['results']
    if 'fieldcraft' not in coarse or 'calculix' not in fine or 'fieldcraft' in fine:raise ValueError('Requires original matched coarse and held fine FieldCraft evidence')
    model=json.loads((original/'mesh-fine/mesh.json').read_text())
    if model['mesh_id']!=prior['levels']['fine']['mesh_id'] or model['input_id']!=spec['input_id']:raise ValueError('Original fine mesh/input differs')
    if model['candidate_id']!=spec['candidate_id'] or model['component_geometry_id']!=spec['component_geometry_id']:raise ValueError('Original physical identities differ')
    folder=Path(output).resolve();folder.mkdir(parents=True,exist_ok=False)
    native.write(folder/'input.json',spec);native.write(folder/'original-verification.json',receipt)
    (folder/'resource-evaluator-source.py').write_bytes(Path(__file__).read_bytes())
    deck=folder/'import-mesh.inp';deck.write_bytes((original/'solve-fine/import-mesh.inp').read_bytes())
    if deck.read_text()!=fem.deck(spec,model).split('*BOUNDARY')[0]:raise ValueError('Exact imported mesh deck differs')
    cmds=fem.commands(spec,model,deck);old=fem.commands(spec,model,original/'solve-fine/import-mesh.inp')
    if physics_commands(cmds)!=physics_commands(old):raise ValueError('Resource revision changes physical command data')
    epoch=sources();request=dict(schema='osr-viaduct-fem-resource-request/1',candidate_id=spec['candidate_id'],component_geometry_id=spec['component_geometry_id'],input_id=spec['input_id'],
        original_case_run=str(original),original_result_id=prior['result_id'],original_evaluation_id=prior['evaluation_id'],original_request_sha256=native.digest(original/'request.json'),
        original_source_sha256=old_request['source_sha256'],source_sha256=epoch,fine_mesh_id=model['mesh_id'],
        original_mesh_sha256=native.digest(original/'mesh-fine/mesh.json'),imported_mesh_deck_sha256=native.digest(deck),
        source_fine_calculix_record_id=identity(fine['calculix']),source_coarse_fieldcraft_record_id=identity(coarse['fieldcraft']),
        tool=native.pin('fieldcraft'),executable_sha256=native.digest(native.executable('fieldcraft')),
        resources=dict(memory_mb=memory_mb,timeout_s=120,thread_environment_requested_one=True,hard_cpu_affinity_enforced=False,aggregate_cgroup_memory=False),
        unchanged_physics_command_id=identity(physics_commands(cmds)),screens=fem.SCREENS,
        reuse_scope='Exact imported CAD mesh, coarse FieldCraft and fine CalculiX from authenticated original run; only fine FieldCraft is fresh under revised address-space limit',**FLAGS)
    request['evaluation_id']=identity(request);native.write(folder/'request.json',request)
    calls=[('batch',dict(commands=cmds[i:i+4000])) for i in range(0,len(cmds),4000)]
    execution,replies=native.mcp('fieldcraft',calls,folder/'fieldcraft',read_root=folder,memory_mb=memory_mb,timeout_s=120)
    result=dict(schema='osr-viaduct-fem-resource-result/1',candidate_id=spec['candidate_id'],component_geometry_id=spec['component_geometry_id'],input_id=spec['input_id'],
        evaluation_id=request['evaluation_id'],original_result_id=prior['result_id'],execution=execution,**FLAGS)
    try:
        if execution['execution']!='executed':raise ValueError('Revised numerical worker did not complete')
        result['fieldcraft']=parse(replies,model);result['comparisons']=comparisons(result['fieldcraft'],coarse['fieldcraft'],fine['calculix']);result['state']='numerical-comparison-completed'
    except (ValueError,KeyError,IndexError) as e:result.update(state='held',reason=str(e))
    if epoch!=sources():raise ValueError('Resource evaluator source changed; preserve without publication')
    result['artifact_sha256']={p.relative_to(folder).as_posix():native.digest(p) for p in folder.rglob('*') if p.is_file()}
    result['result_id']=identity(result);native.write(folder/'result.json',result);return result


def verify(output,spec):
    folder=Path(output);r=json.loads((folder/'result.json').read_text());q=json.loads((folder/'request.json').read_text())
    if r['result_id']!=identity({k:v for k,v in r.items() if k!='result_id'}) or q['evaluation_id']!=identity({k:v for k,v in q.items() if k!='evaluation_id'}):raise ValueError('Resource result/request seal differs')
    if q['source_sha256']!=sources() or json.loads((folder/'input.json').read_text())!=spec:raise ValueError('Resource input or source differs')
    original=Path(q['original_case_run']);fem.verify(original,spec);prior=json.loads((original/'result.json').read_text());model=json.loads((original/'mesh-fine/mesh.json').read_text())
    for key in ('candidate_id','component_geometry_id','input_id'):
        if r[key]!=spec[key] or q[key]!=spec[key]:raise ValueError('Resource physical/load identity differs')
    if r['evaluation_id']!=q['evaluation_id'] or prior['result_id']!=q['original_result_id'] or r['original_result_id']!=q['original_result_id']:raise ValueError('Resource ancestry differs')
    if q['original_request_sha256']!=native.digest(original/'request.json') or q['fine_mesh_id']!=model['mesh_id'] or q['original_mesh_sha256']!=native.digest(original/'mesh-fine/mesh.json'):raise ValueError('Original immutable request/mesh differs')
    if q['source_fine_calculix_record_id']!=identity(prior['levels']['fine']['results']['calculix']) or q['source_coarse_fieldcraft_record_id']!=identity(prior['levels']['coarse']['results']['fieldcraft']):raise ValueError('Reused solver record differs')
    files={p.relative_to(folder).as_posix():p for p in folder.rglob('*') if p.is_file() and p!=folder/'result.json'}
    if set(files)!=set(r['artifact_sha256']) or any(p.is_symlink() or native.digest(p)!=r['artifact_sha256'][n] for n,p in files.items()):raise ValueError('Resource immutable artifact differs')
    cmds=fem.commands(spec,model,folder/'import-mesh.inp');inv=json.loads((folder/'fieldcraft/invocation.json').read_text())
    submitted=[c for line in inv['stdin'].splitlines() for msg in [json.loads(line)] if msg.get('method')=='tools/call' for c in msg['params']['arguments']['commands']]
    if submitted!=cmds or identity(physics_commands(cmds))!=q['unchanged_physics_command_id']:raise ValueError('Fresh resource commands differ')
    if inv['resources']['memory_mb']!=3072 or inv['resources']['timeout_s']!=120:raise ValueError('Native resource request differs')
    if q['tool']!=native.pin('fieldcraft') or q['executable_sha256']!=native.digest(native.executable('fieldcraft')):raise ValueError('Fresh FieldCraft pin differs')
    if r['state']=='numerical-comparison-completed':
        replies=[json.loads(l) for l in (folder/'fieldcraft/stdout.jsonl').read_text().splitlines()];field=parse(replies,model)
        if field!=r['fieldcraft'] or comparisons(field,prior['levels']['coarse']['results']['fieldcraft'],prior['levels']['fine']['results']['calculix'])!=r['comparisons']:raise ValueError('Resource numerical readback differs')
    if any(r.get(k) is not False for k in FLAGS):raise ValueError('A numerical resource revision cannot grant release')
    return dict(integrity_verified=True,fresh_native_solve=False,result_id=r['result_id'],original_result_id=prior['result_id'],**FLAGS)
