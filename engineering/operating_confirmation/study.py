"""Two finite NdFeB operating poses and a retained-field quadrature diagnostic.

The scalar-potential kernel models permanent magnets and passive steel only.
It contains no winding-current source. Every solve is fixed at80 C and0 A.
"""
from copy import deepcopy
from hashlib import sha256
import argparse
import importlib.metadata
import json
import math
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import time

from engineering.halbach_scaling import finite
from engineering.suspension_closure import study as parent
from engineering.magnetic_confirmation import analysis

ROOT=Path(__file__).resolve().parents[2]
SCHEMA='osr-finite-operating-confirmation/1'
FLAGS=parent.FLAGS
SETTINGS=dict(margin_m=.15,near_mesh_size_m=.032,gap_mesh_size_m=.010)
GAPS=(parent.GAP,.028)
COUNTS=(128,48,24)
QUAD_COUNTS=(256,96,48)


def identity(v):return parent.identity(v)
def write(p,v):return parent.write(p,v)
def read(p):return parent.read(p)
def digest(p):return parent.digest(p)


def environment():
    return dict(python=sys.version,**{name:importlib.metadata.version(name) for name in ('numpy','scipy','gmsh')})


def sources(root):
    values=parent.sources(root)
    for path in sorted(Path(__file__).parent.rglob('*.py')):
        if path.is_symlink():raise ValueError('ordinary numerical implementation required')
        values[path.relative_to(ROOT).as_posix()]=digest(path)
    return dict(sorted(values.items()))


def candidate(root):
    value=parent.candidates(root)[0]
    if value['component_id']!='397ddf033ab98afaea053acaa3047249a3329f542f1f5e52a6eb1b466b9662e0':raise ValueError('exact12L differential physical component required')
    return value


def state(gap_m,*,temperature_C=80.,currents_A=None):
    if type(gap_m) not in (int,float) or not math.isfinite(gap_m) or gap_m not in GAPS:
        raise ValueError('one of two explicitly declared operating gaps required')
    if temperature_C!=80. or type(temperature_C) not in (float,int) or currents_A not in (None,{}):
        raise ValueError('PM-only kernel supports exactly80 C and zero coil-current source')
    return dict(gap_m=float(gap_m),temperature_C=80.,currents_A={},lateral_m=0.,rotation_rad=[0.,0.,0.])


def specs():
    return [dict(case='medium-same-gap',state=state(GAPS[0]),settings=deepcopy(SETTINGS),face_counts=list(COUNTS)),
            dict(case='medium-28mm',state=state(GAPS[1]),settings=deepcopy(SETTINGS),face_counts=list(COUNTS))]


def _request_contract(request):
    if request['state']!=state(request['state']['gap_m']):raise ValueError('finite state differs')
    if request['candidate']!=candidate(request['root']):raise ValueError('finite candidate differs')
    if request['source_sha256']!=sources(request['root']) or request['getdp']!=finite.previous._tool(request['getdp']['path']):raise ValueError('finite sources/solver differ')
    if request['environment']!=environment():raise ValueError('finite numerical environment differs')
    if request['kind']=='solve':
        if request['settings']!=SETTINGS or request['face_counts']!=list(COUNTS):raise ValueError('declared medium mesh/contour grid required')
    elif request['kind']=='postprocess':
        if request['state']!=state(parent.GAP) or request['settings']!=parent.FINITE_SETTINGS or request['face_counts']!=list(QUAD_COUNTS):raise ValueError('declared coarse parent and denser face grid required')
    else:raise ValueError('unknown finite experiment kind')


def _finite_contract(directory,request,record,*,seed_directory=None):
    d=Path(directory);component=request['candidate'];posed=finite.pose(component['value'],request['state']['gap_m'])
    _request_contract(request)
    if read(d/'source.json')!=component or read(d/'pose.json')!=posed:raise ValueError('finite stock/pose input differs')
    if (record['schema']!=SCHEMA+'/point' or record['request_id']!=identity(request)
        or record['candidate_id']!=component['component_id'] or record['state_id']!=posed['evaluation_state_id']
        or record['state']!=request['state'] or record['settings']!=request['settings'] or record['face_counts']!=request['face_counts']):raise ValueError('finite evaluation identity differs')
    if request['kind']=='solve':
        if request['settings']!=SETTINGS or request['face_counts']!=list(COUNTS):raise ValueError('declared medium mesh/contour grid required')
    elif request['kind']=='postprocess':
        seed=request['seed'];seed_path=Path(seed_directory or request['seed_directory'])
        if request['settings']!=parent.FINITE_SETTINGS or request['face_counts']!=list(QUAD_COUNTS):raise ValueError('declared coarse parent and denser face grid required')
        if request['state']!=state(parent.GAP) or seed['request_id']!=identity(read(seed_path/'input.json')):raise ValueError('quadrature parent state differs')
        if set(request['seed_sha256'])!={'coupon.msh','coupon.pre','coupon.res'}:raise ValueError('complete retained field seed required')
        for name,expected in request['seed_sha256'].items():
            if name not in ('coupon.msh','coupon.pre','coupon.res') or digest(seed_path/name)!=expected or digest(d/name)!=expected:
                raise ValueError('retained solution/mesh changed during postprocess')
    else:raise ValueError('unknown finite experiment kind')
    command=[request['getdp']['path'],'coupon.pro','-msh','coupon.msh']
    if request['kind']=='solve':command+=['-solve','Solve']
    command+=['-pos','Results']
    if record['solver_command']!=command:raise ValueError('finite solve/postprocess command differs')
    mesh_check=finite.validate_mesh(d/'coupon.msh',record['mesh'],posed,request['settings'])
    boxes=finite.contours(posed)
    if (record['mesh_verification']!=mesh_check or record['contours_m']!=boxes
        or (d/'coupon.pro').read_text()!=finite.formulation(posed,record['mesh'],boxes,tuple(request['face_counts']))):raise ValueError('finite domain/material/formulation differs')
    if request['kind']=='solve':parsed=analysis.parse_stages((d/'getdp.stdout.log').read_text())
    else:parsed=request['seed']['continuation']
    full=record['solver_returncode']==0 and parsed['full_source_converged']
    if record['continuation']!=parsed or record['force_credit']!=full:raise ValueError('partial source cannot supply force')
    if full:
        expected=finite.analyze(d,posed,record['mesh'],boxes,tuple(request['face_counts']))
        if record.get('analysis')!=expected:raise ValueError('finite force/peak diagnostics differ')
    elif 'analysis' in record:raise ValueError('incomplete source cannot supply field values')
    if record['PDE_solves']!=(1 if request['kind']=='solve' else 0) or record.get('coil_current_source_modelled') is not False:
        raise ValueError('zero-current/postprocess numerical scope differs')
    for k in FLAGS:
        if record.get(k) is not False:raise ValueError('finite research cannot claim acceptance')
    return record


def _worker(request,directory):
    _request_contract(request)
    d=Path(directory);component=request['candidate'];posed=finite.pose(component['value'],request['state']['gap_m'])
    if request['kind']=='solve':
        mesh=finite.mesh_case(posed,d,request['settings'])
    else:
        seed=Path(request['seed_directory']);mesh=request['seed']['mesh']
        for name,expected in request['seed_sha256'].items():
            if digest(seed/name)!=expected:raise ValueError('postprocess seed identity differs')
            shutil.copyfile(seed/name,d/name)
    write(d/'source.json',component);write(d/'pose.json',posed)
    checked=finite.validate_mesh(d/'coupon.msh',mesh,posed,request['settings']);boxes=finite.contours(posed)
    (d/'coupon.pro').write_text(finite.formulation(posed,mesh,boxes,tuple(request['face_counts'])))
    command=[request['getdp']['path'],'coupon.pro','-msh','coupon.msh']
    if request['kind']=='solve':command+=['-solve','Solve']
    command+=['-pos','Results']
    with (d/'getdp.stdout.log').open('wb') as stdout,(d/'getdp.stderr.log').open('wb') as stderr:
        code=subprocess.run(command,cwd=d,stdout=stdout,stderr=stderr).returncode
    parsed=analysis.parse_stages((d/'getdp.stdout.log').read_text()) if request['kind']=='solve' else request['seed']['continuation']
    row=dict(schema=SCHEMA+'/point',request_id=identity(request),candidate_id=component['component_id'],
        state_id=posed['evaluation_state_id'],state=request['state'],settings=request['settings'],
        face_counts=request['face_counts'],mesh=mesh,mesh_verification=checked,contours_m=boxes,
        solver_returncode=code,solver_command=command,continuation=parsed,
        force_credit=code==0 and parsed['full_source_converged'],PDE_solves=1 if request['kind']=='solve' else 0,
        coil_current_source_modelled=False,**FLAGS)
    if row['force_credit']:row['analysis']=finite.analyze(d,posed,mesh,boxes,tuple(request['face_counts']))
    _finite_contract(d,request,row);write(d/'point.json',row)


def _execute(d,request,root,seconds):
    d.mkdir();write(d/'input.json',request)
    if seconds<=0:return dict(execution_status='not-run',request_id=identity(request),**FLAGS)
    command=[sys.executable,'-m','engineering.operating_confirmation','worker','--input',str(d/'input.json'),'--output',str(d)]
    ex=parent._execute(command,d,seconds)
    result=dict(execution_status='interrupted' if ex['timed_out'] else 'tool-error',execution=ex,request_id=identity(request),**FLAGS)
    if ex['returncode']==0 and not ex['timed_out'] and (d/'point.json').is_file():
        result.update(execution_status='completed',point=read(d/'point.json'));_finite_contract(d,request,result['point'])
    return result


def _values(row):
    if row.get('execution_status')!='completed':return None
    ex=row.get('execution',{})
    if ex.get('returncode')!=0 or ex.get('timed_out') is not False:raise ValueError('successful complete worker required')
    p=row['point']
    if not p['force_credit']:return None
    return p['analysis']['air_contour_results']


def comparisons(item,parent_point,rows,quadrature):
    aw3=item['comparison_aw3_kg_per_car'];mean=aw3*9.80665/24;demand=(aw3+2000)*9.80665*1.3/24
    output=[]
    for row in rows:
        values=_values(row);point=row.get('point',{})
        if values:
            z=[r['force_N'][2] for r in values];a=point['analysis']
            observed=dict(contour_Fz_N=z,finite_minus_mean_weight_N=[f-mean for f in z],
                finite_minus_1_3_plus_2t_required_N=[f-demand for f in z],
                lower_contour_supports_mean_weight=min(z)>=mean,
                lower_contour_supports_1_3_plus_2t=min(z)>=demand,
                vertical_contour_relative_difference=abs(z[1]-z[0])/max(abs(z[0]),abs(z[1]),1e-12),
                vector_contour_difference=a['contour_force_change'],demag_proxy_margin_A_per_m=a['demag_proxy_margin_A_per_m'],
                steel_B_peak_T=a['steel_B_peak_T'])
        else:observed=None
        output.append(dict(case=row['case'],candidate_id=item['component_id'],
            state=None if 'point' not in row else point['state'],observed=observed,
            mean_AW3_weight_N_per_module=mean,plus_2t_1_3_required_N_per_module=demand,
            equilibrium_solved=False,all_six_dof_current_map=None,numerical_force_convergence_established=False,**FLAGS))
    diagnostic={}
    fine=_values(rows[0]) if rows else None
    if fine:
        diagnostic['mesh_change_same_state']=[dict(force=analysis.change(a['force_N'],b['force_N']),
            moment=analysis.change(a['moment_Nm'],b['moment_Nm'])) for a,b in zip(parent_point['analysis']['air_contour_results'],fine)]
    dense=_values(quadrature)
    if dense:
        diagnostic['quadrature_change_same_field']=[dict(force=analysis.change(a['force_N'],b['force_N']),
            moment=analysis.change(a['moment_Nm'],b['moment_Nm'])) for a,b in zip(parent_point['analysis']['air_contour_results'],dense)]
    diagnostic['force_map_qualified']=False;diagnostic['scope']='One field-mesh refinement and one face quadrature refinement are separate diagnostics; neither establishes local-peak, field-domain, force/moment or control convergence.'
    return dict(operating_states=output,diagnostics=diagnostic,
        parent_coarse=dict(candidate_id=item['component_id'],state=state(parent.GAP),settings=parent.FINITE_SETTINGS,
            request_id=parent_point['request_id'],state_id=parent_point['state_id'],
            air_contour_results=parent_point['analysis']['air_contour_results']),
        bracketed_stable_hover=False,**FLAGS)


def run(output,root,getdp,parent_run,*,seconds_total=600.,seconds_per_case=300.,quadrature=True):
    if type(seconds_total) not in (int,float) or type(seconds_per_case) not in (int,float) or not 0<seconds_total<=600 or not 0<seconds_per_case<=300:
        raise ValueError('bounded600s campaign/300s cases required')
    if type(quadrature) is not bool:raise ValueError('explicit quadrature request required')
    start=time.monotonic();before=sources(root);root=Path(root).resolve();output=Path(output).resolve()
    if output.is_symlink() or any(p.is_symlink() for p in output.parents):raise ValueError('ordinary fresh output required')
    output.mkdir(parents=True,exist_ok=False)
    parent.verify(parent_run,root);shutil.copytree(parent_run,output/'parent')
    parent_result=read(output/'parent/result.json');seed=parent_result['finite']
    if not seed.get('point',{}).get('force_credit') or _values(seed) is None:raise ValueError('full-source coarse operating parent required')
    item=candidate(root);tool=finite.previous._tool(getdp)
    request=dict(schema=SCHEMA,root=str(root),candidate=item,source_sha256=before,getdp=tool,specs=specs(),environment=environment(),
        parent_request_id=parent_result['request_id'],parent_result_id=parent_result['result_id'],
        parent_files_sha256=finite.inventory(output/'parent'),quadrature_requested=quadrature,
        budget=dict(seconds_total=seconds_total,seconds_per_case=seconds_per_case,quadrature_seconds=60.,numerical_workers=1),**FLAGS)
    write(output/'request.json',request);rows=[]
    for spec in request['specs']:
        child=dict(root=str(root),candidate=item,kind='solve',source_sha256=before,getdp=tool,environment=request['environment'],
            state=spec['state'],settings=spec['settings'],face_counts=spec['face_counts'])
        row=_execute(output/spec['case'],child,root,min(seconds_per_case,max(0.,seconds_total-(time.monotonic()-start))))
        row['case']=spec['case'];rows.append(row)
    quad=dict(execution_status='not-requested',**FLAGS)
    if quadrature:
        directory=output/'parent/finite';record=seed['point']
        child=dict(root=str(root),candidate=item,kind='postprocess',source_sha256=before,getdp=tool,environment=request['environment'],
            state=state(parent.GAP),settings=parent.FINITE_SETTINGS,face_counts=list(QUAD_COUNTS),seed=record,
            seed_directory=str(directory),seed_sha256={p:digest(directory/p) for p in ('coupon.msh','coupon.pre','coupon.res')})
        quad=_execute(output/'parent-quadrature',child,root,min(60.,max(0.,seconds_total-(time.monotonic()-start))))
    if sources(root)!=before:raise ValueError('confirmation sources changed')
    result=dict(schema=SCHEMA,request_id=identity(request),rows=rows,quadrature=quad,
        comparisons=comparisons(item,record if quadrature else seed['point'],rows,quad),
        elapsed_s=time.monotonic()-start,source_sha256=before,**FLAGS)
    result['evaluation_id']=identity(result);write(output/'result.json',result)
    write(output/'manifest.json',dict(source_sha256=before,request_id=identity(request),evaluation_id=result['evaluation_id'],
        files_sha256=finite.inventory(output,('manifest.json',)),**FLAGS))
    return result


def verify(output,root):
    d=Path(output);request=read(d/'request.json');result=read(d/'result.json');manifest=read(d/'manifest.json')
    if manifest['files_sha256']!=finite.inventory(d,('manifest.json',)) or request['source_sha256']!=sources(root):raise ValueError('confirmation source/payload differs')
    parent.verify(d/'parent',root);pr=read(d/'parent/result.json');seed=pr['finite'];item=candidate(root)
    if (request['schema']!=SCHEMA or request['candidate']!=item or request['getdp']!=finite.previous._tool(request['getdp']['path'])
        or request['specs']!=specs() or request['environment']!=environment() or request['parent_result_id']!=pr['result_id'] or request['parent_request_id']!=pr['request_id']
        or request['parent_files_sha256']!=finite.inventory(d/'parent')):raise ValueError('confirmation parent/candidate/plan differs')
    b=request['budget']
    if b!=dict(seconds_total=b['seconds_total'],seconds_per_case=b['seconds_per_case'],quadrature_seconds=60.,numerical_workers=1) or not 0<b['seconds_total']<=600 or not 0<b['seconds_per_case']<=300:raise ValueError('confirmation budget differs')
    if len(result['rows'])!=2:raise ValueError('two explicit native execution records required')
    def check(row,directory,child,seed_directory=None):
        if read(directory/'input.json')!=child or row['request_id']!=identity(child):raise ValueError('native request differs')
        if row.get('execution_status') not in ('completed','not-run','interrupted','tool-error'):raise ValueError('unknown native execution state')
        if row['execution_status']=='completed':
            _values(row)
            if row['point']!=read(directory/'point.json'):raise ValueError('native record differs')
            _finite_contract(directory,child,row['point'],seed_directory=seed_directory)
        elif 'point' in row:raise ValueError('interrupted native worker cannot supply force')
        if row['execution_status']=='not-run' and 'execution' in row:raise ValueError('unrun native case has execution metadata')
        if row['execution_status'] in ('interrupted','tool-error'):
            ex=row.get('execution',{})
            if not isinstance(ex.get('returncode'),int) or ex.get('timed_out') is not (row['execution_status']=='interrupted'):raise ValueError('unsuccessful native execution metadata differs')
    for spec,row in zip(specs(),result['rows']):
        if row.get('case')!=spec['case']:raise ValueError('native case order differs')
        child=dict(root=request['root'],candidate=item,kind='solve',source_sha256=sources(root),getdp=request['getdp'],environment=request['environment'],
            state=spec['state'],settings=spec['settings'],face_counts=spec['face_counts'])
        check(row,d/spec['case'],child)
    q=result['quadrature']
    if request['quadrature_requested']:
        directory=d/'parent/finite';record=seed['point']
        # The recorded seed path is provenance. A replay reads retained files
        # from the extracted packet instead of requiring its original run path.
        child=read(d/'parent-quadrature/input.json');expected=dict(root=request['root'],candidate=item,
            kind='postprocess',source_sha256=sources(root),getdp=request['getdp'],environment=request['environment'],state=state(parent.GAP),
            settings=parent.FINITE_SETTINGS,face_counts=list(QUAD_COUNTS),seed=record,
            seed_directory=child['seed_directory'],seed_sha256={p:digest(directory/p) for p in ('coupon.msh','coupon.pre','coupon.res')})
        if child!=expected:raise ValueError('retained quadrature request differs')
        check(q,d/'parent-quadrature',child,seed_directory=directory)
    elif q['execution_status']!='not-requested':raise ValueError('unrequested quadrature supplied numerical credit')
    expected=comparisons(item,seed['point'],result['rows'],q)
    if result['comparisons']!=expected:raise ValueError('native comparison does not reproduce')
    eid=identity({k:v for k,v in result.items() if k!='evaluation_id'})
    if (result['evaluation_id']!=eid or manifest['evaluation_id']!=eid or result['request_id']!=identity(request)
        or manifest['request_id']!=identity(request) or manifest['source_sha256']!=sources(root) or result['source_sha256']!=sources(root)):
        raise ValueError('confirmation identities differ')
    def reject(value):
        if isinstance(value,dict):
            for k,v in value.items():
                if k in FLAGS and v is not False:raise ValueError('confirmation cannot assert acceptance')
                reject(v)
        elif isinstance(value,list):
            for v in value:reject(v)
    reject(request);reject(result);reject(manifest)
    return dict(current=True,native_cases=2,full_source_cases=sum(_values(r) is not None for r in result['rows']),
        quadrature_completed=_values(q) is not None,PDE_case_budget=2,**FLAGS)


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('action',choices=('run','verify','worker'))
    p.add_argument('--root',type=Path,default=ROOT);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--getdp',type=Path);p.add_argument('--parent-run',type=Path);p.add_argument('--input',type=Path)
    args=p.parse_args()
    if args.action=='run':value=run(args.output,args.root,args.getdp,args.parent_run)
    elif args.action=='verify':value=verify(args.output,args.root)
    else:_worker(read(args.input),args.output);return
    print(json.dumps(value,sort_keys=True,allow_nan=False))
