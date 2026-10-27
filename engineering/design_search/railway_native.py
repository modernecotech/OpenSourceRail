"""Bounded native work shared with the coupled railway dependency graph."""
from pathlib import Path
import json,time,shutil,tomllib
from math import ceil,prod
from bisect import bisect_left
from engineering.station_rail import ROOT
from engineering.station_rail.common import encoded,identity,digest
from . import grammar_shell,grammar_geometry,railway_bundle

PRODUCER='engineering/design_search/railway_native.py'


def cell_estimate(body,mesh_m):
    """Exact Cartesian cell count for disjoint boxes, before allocating a mesh."""
    ids=set(body.get('shell_model',{}).get('structural_part_ids',[]));parts=[p for p in body['parts'] if p['id'] in ids]
    if not parts:return None
    axes=[]
    for d in range(3):
        cuts={round(p['at_m'][d]+s*p['size_m'][d],10) for p in parts for s in (0,1)};lo=min(cuts);hi=max(cuts);n=ceil((hi-lo)/mesh_m)
        cuts.update(round(lo+(hi-lo)*i/n,10) for i in range(n+1));axes.append(sorted(cuts))
    count=sum(prod(bisect_left(axes[d],round(p['at_m'][d]+p['size_m'][d],10))-bisect_left(axes[d],round(p['at_m'][d],10)) for d in range(3)) for p in parts)
    return dict(solid_cells=count,coordinate_planes=[len(a) for a in axes],scope='Exact count for this disjoint-box conformal construction; memory/factorization cost is not a physical engineering limit')


def _packet(folder):
    m=json.loads((folder/'manifest.json').read_bytes());r=json.loads((folder/'result.json').read_bytes())
    if m['manifest_id']!=identity({k:v for k,v in m.items() if k!='manifest_id'}):raise ValueError('Native receipt differs')
    if r['evaluation_id']!=identity({k:v for k,v in r.items() if k!='evaluation_id'}):raise ValueError('Native result differs')
    if r['source_sha256']!=m['source_sha256'] or r['tool']!=m['tool']:raise ValueError('Native receipt and result context differ')
    actual={p.relative_to(folder).as_posix():digest(p) for p in folder.rglob('*') if p.is_file() and p.name!='manifest.json'}
    if actual!=m['files_sha256']:raise ValueError('Native files differ')
    if any(digest(ROOT/name)!=h for name,h in m['source_sha256'].items()):raise ValueError('Native physics producer changed')
    if digest(r['tool']['ccx_path'])!=r['tool']['ccx_sha256']:raise ValueError('Native executable differs')
    return r


def _requested(raw,result,request):
    if any(result['tool'].get(k)!=request[v] for k,v in (('requested_memory_mb','memory_mb'),('timeout_s','timeout_s'))):raise ValueError('Native resource request differs')
    definition=json.loads((raw/'definition.json').read_bytes())
    if request['kind']=='independent-solid-method':
        case=dict(id=result.get('benchmark_id'),raw=(raw/'model.inp').read_text(),definition=definition)
        if case['id']!=request['case_id'] or identity(case)!=request['input_id']:raise ValueError('Native fixture input does not match request')
    else:
        if result.get('candidate_id')!=request['body_candidate_id'] or result.get('definition_id')!=request['definition_id']:raise ValueError('Native body/definition differs from request')
        for key in ('load_case','mesh_m','load_mass_kg','load_basis','element_kind'):
            if definition.get(key)!=request[key] or result['mesh_summary'].get(key)!=request[key]:raise ValueError('Native body case/mesh/load differs: '+key)
    return result


def run(bodies,folder,*,maximum_new_jobs=0,root=ROOT):
    root=Path(root);folder=Path(folder);folder.mkdir(parents=True,exist_ok=True);new=0;reused=0;pending=[];fixtures=[];body_results=[];CAD=[];paths=[];cache_rejections=[];refinements=[]
    if type(maximum_new_jobs) is not int or not 0<=maximum_new_jobs<=12:raise ValueError('Bounded zero-to-twelve native allowance required')
    epoch={PRODUCER:digest(root/PRODUCER),grammar_shell.PRODUCER:digest(root/grammar_shell.PRODUCER)}
    specification=tomllib.loads((root/'campaigns/coupled-railway-design.toml').read_text())
    cases=dict(zip(specification['body_cases'],specification['body_mesh_m']))
    if set(cases)!=set(('normal','normal-fine','crowd')):raise ValueError('Same-candidate normal/refinement/crowd case controls required')
    def job(kind,request,execute,known=None):
        nonlocal new,reused
        key=identity(dict(request=request,source_sha256=epoch));path=folder/'jobs'/key;raw=path/'raw'
        if not path.exists():
            for old in sorted((root/'build/coupled-railway').glob('*/native/jobs/*/request.json')):
                if json.loads(old.read_bytes())!=request:continue
                original=old.parent/'raw'
                try:r=_requested(original,_packet(original),request)
                except (ValueError,OSError,KeyError) as error:
                    cache_rejections.append(dict(original_request_sha256=digest(old),reason=str(error)));continue
                path.mkdir(parents=True);(path/'request.json').write_bytes(encoded(request));shutil.copytree(original,raw)
                (path/'reuse-context.json').write_bytes(encoded(dict(original_manifest_id=json.loads((original/'manifest.json').read_bytes())['manifest_id'],
                    original_evaluation_id=r['evaluation_id'],reason='Exact numerical input/candidate/load/mesh/tool/resources and physics source match across coordinator epochs')))
                break
        if not path.exists() and known is not None and (known/'manifest.json').is_file():
            old=_requested(known,_packet(known),request);path.mkdir(parents=True);(path/'request.json').write_bytes(encoded(request));shutil.copytree(known,raw)
            (path/'reuse-context.json').write_bytes(encoded(dict(original_native_manifest_id=json.loads((known/'manifest.json').read_bytes())['manifest_id'],
                original_evaluation_id=old['evaluation_id'],reason='Exact fixture input, source and executable match; immutable packet copied without a new solve')))
        if (raw/'manifest.json').is_file():
            if json.loads((path/'request.json').read_bytes())!=request:raise ValueError('Native request differs')
            r=_requested(raw,_packet(raw),request);reused+=1
        elif new>=maximum_new_jobs:
            pending.append(dict(kind=kind,request=request,job_id=key,state='ready'));return None
        else:
            if path.exists():
                archive=folder/'interrupted';archive.mkdir(exist_ok=True);path.rename(archive/(key+'-'+str(time.time_ns())))
            path.mkdir(parents=True);(path/'request.json').write_bytes(encoded(request));r=execute(raw);new+=1
            _requested(raw,_packet(raw),request)
        paths.append(dict(kind=kind,job_id=key,raw_path=raw.relative_to(folder).as_posix(),evaluation_id=r['evaluation_id']))
        return r
    plan=grammar_shell.benchmark_plan()
    for case in plan['cases']:
        request=dict(kind='independent-solid-method',case_id=case['id'],input_id=identity(json.loads(encoded(case))),memory_mb=3072,timeout_s=90)
        known=root/'build/coupled-railway/solid-method-r1'/case['id']
        if (known/'manifest.json').is_file() and ((known/'model.inp').read_text()!=case['raw'] or json.loads((known/'definition.json').read_bytes())!=json.loads(encoded(case['definition']))):known=None
        r=job('method',request,lambda raw,c=case:grammar_shell.run_benchmark(c,raw,root=root,memory_mb=3072,timeout_s=90),known=known)
        if r is not None:fixtures.append(r)
    admitted=len(fixtures)==len(plan['cases']) and all(r.get('method_screen')=='pass' for r in fixtures)
    admissions={}
    for b in bodies:
        value=grammar_shell.plan(b)
        estimates={name:cell_estimate(b,mesh) for name,mesh in cases.items()} if value['admitted'] else {}
        over=any(e['solid_cells']>specification['maximum_solid_cells_per_job'] for e in estimates.values())
        value.update(computational_mesh_estimates=estimates,dispatch_eligible=value['admitted'] and not over,
            computational_hold='Conformal grid exceeds this invocation cell budget after a retained 5GiB allocation failure; change discretization/profile layout or explicitly revise resources' if over else None)
        admissions[b['candidate_id']]=value
    for body in bodies:
        if not admissions[body['candidate_id']]['admitted']:continue
        bundle=railway_bundle.materialize(body,root=root)
        if not admissions[body['candidate_id']]['dispatch_eligible']:
            pending.append(dict(kind='computational-resource-or-profile-revision',body_candidate_id=body['candidate_id'],state='open',resource_hold=admissions[body['candidate_id']]['computational_hold']));continue
        for case,mesh in cases.items():
            mass=bundle['crowd_sprung_mass_hypothesis_kg'] if case=='crowd' else bundle['normal_sprung_mass_hypothesis_kg']
            request=dict(kind='three-dimensional-body',body_candidate_id=body['candidate_id'],definition_id=body['definition_id'],
                bundle_id=bundle['candidate_id'],load_case='normal' if case=='normal-fine' else case,case_label=case,mesh_m=mesh,
                load_mass_kg=mass,load_basis=dict(bundle_id=bundle['candidate_id'],bundle_definition_id=bundle['definition_id'],scope=bundle['mass_scope']),
                element_kind='C3D8I',memory_mb=specification['maximum_native_memory_mb'],timeout_s=specification['body_timeout_s'])
            if not admitted:
                pending.append(dict(kind='three-dimensional-body',request=request,state='blocked-by-independent-method-fixtures'));continue
            r=job('body',request,lambda raw,b=body,q=request:grammar_shell.run(b,raw,root=root,mesh_m=q['mesh_m'],load_case=q['load_case'],
                load_mass_kg=q['load_mass_kg'],load_basis=q['load_basis'],element_kind=q['element_kind'],memory_mb=q['memory_mb'],timeout_s=q['timeout_s']))
            if r is not None:
                body_results.append(dict(body_candidate_id=body['candidate_id'],bundle_id=bundle['candidate_id'],case=case,mesh_m=mesh,
                    evaluation_id=r['evaluation_id'],raw=r))
        current=[r for r in body_results if r['body_candidate_id']==body['candidate_id']]
        coarse=next((r for r in current if r['case']=='normal'),None);fine=next((r for r in current if r['case']=='normal-fine'),None)
        if coarse and fine and all(r['raw'].get('numerical_validity')=='equilibrium_energy_confirmed_only' for r in (coarse,fine)):
            a,b=coarse['raw']['maximum_displacements'],fine['raw']['maximum_displacements']
            changes={k:abs(a[k]-b[k])/max(abs(b[k]),1e-9) for k in a};control=specification['numerical_refinement']
            if max(changes.values())>control['trigger_relative_change']:
                mesh=fine['mesh_m']*control['factor'];estimate=cell_estimate(body,mesh)
                observation=dict(body_candidate_id=body['candidate_id'],parent_evaluation_ids=[coarse['evaluation_id'],fine['evaluation_id']],component_relative_changes=changes,
                    purpose=control['purpose'],proposed_mesh_m=mesh,computational_estimate=estimate)
                refinements.append(observation)
                if mesh<control['minimum_mesh_m'] or estimate['solid_cells']>specification['maximum_solid_cells_per_job']:
                    pending.append(dict(kind='refined-discretization-or-resource-development',body_candidate_id=body['candidate_id'],observation=observation,state='open'))
                else:
                    request=dict(kind='three-dimensional-body',body_candidate_id=body['candidate_id'],definition_id=body['definition_id'],
                        bundle_id=bundle['candidate_id'],load_case='normal',case_label='normal-refined',mesh_m=mesh,
                        load_mass_kg=bundle['normal_sprung_mass_hypothesis_kg'],load_basis=dict(bundle_id=bundle['candidate_id'],bundle_definition_id=bundle['definition_id'],scope=bundle['mass_scope']),
                        element_kind='C3D8I',memory_mb=specification['maximum_native_memory_mb'],timeout_s=specification['body_timeout_s'])
                    r=job('body-refinement',request,lambda raw,b=body,q=request:grammar_shell.run(b,raw,root=root,mesh_m=q['mesh_m'],load_case='normal',load_mass_kg=q['load_mass_kg'],
                        load_basis=q['load_basis'],element_kind=q['element_kind'],memory_mb=q['memory_mb'],timeout_s=q['timeout_s']))
                    if r is not None:body_results.append(dict(body_candidate_id=body['candidate_id'],bundle_id=bundle['candidate_id'],case='normal-refined',mesh_m=mesh,evaluation_id=r['evaluation_id'],raw=r))
        destination=folder/'CAD'/body['candidate_id']
        if not destination.exists():
            for old in sorted((root/'build/coupled-railway').glob('*/native/CAD/'+body['candidate_id']+'/manifest.json')):
                grammar_geometry.read_export(body,old.parent);destination.parent.mkdir(exist_ok=True);shutil.copytree(old.parent,destination);break
        if (destination/'manifest.json').is_file():CAD.append(grammar_geometry.read_export(body,destination))
        elif maximum_new_jobs>0 and admitted:
            CAD.append(grammar_geometry.export(body,destination))
    if epoch!={PRODUCER:digest(root/PRODUCER),grammar_shell.PRODUCER:digest(root/grammar_shell.PRODUCER)}:raise ValueError('Native coordinator sources changed')
    result=dict(schema='osr-coupled-native-evidence/1',source_sha256=epoch,
        method_status='benchmarked-solid-method-only' if admitted else 'method-not-admitted',method_evaluation_ids=[r['evaluation_id'] for r in fixtures],
        independent_fixtures=fixtures,body_admission=admissions,body_results=body_results,CAD_results=CAD,packet_index=paths,
        new_native_jobs=new,reused_native_jobs=reused,requested_native_jobs=maximum_new_jobs,pending=pending,cache_rejections=cache_rejections,refinement_diagnostics=refinements,
        full_body_physical_qualification=False,physical_accepted=False)
    return result
