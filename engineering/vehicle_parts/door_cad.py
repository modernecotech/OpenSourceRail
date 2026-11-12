"""Two-process SolidCraft proof of one door header's declared gross stock blank.

This checks primitive geometry, not installed operator fit, holes, tolerances,
material properties or independent exact B-rep agreement.
"""
import argparse
from math import isfinite,prod
from pathlib import Path
import json
import subprocess
from engineering.performance import disk_admission
from engineering.station_rail.common import digest,identity
from engineering.vehicle_parts import door_module,FLAGS
from engineering.design_search.craft_backends import native,solidcraft

PRODUCER='engineering/vehicle_parts/door_cad.py'
_LOADED_SHA=digest(__file__)
MAX_OUTPUT=256*1024**2
RELATIVE_VOLUME_TOLERANCE=1e-6
POSITION_TOLERANCE_M=1e-6


def compare(expected,measured,*,allow_import_label=False):
    rows=measured.get('bodies',[])
    if len(rows)!=1:raise ValueError('One measured stock solid required')
    body=rows[0];label=body['id'];name=expected['id'];size=expected['size_m'];origin=expected['at_m']
    if label!=name and not allow_import_label:raise ValueError('Generated source body identity differs')
    volume=body.get('volume_m3');center=body.get('center_of_mass_m');bbox=body.get('bbox_m')
    if body.get('closed') is not True or type(volume) not in (int,float) or not isfinite(volume) or volume<=0:
        raise ValueError('Positive closed stock solid required')
    if not isinstance(center,list) or not isinstance(bbox,dict):raise ValueError('Explicit centroid and bounds required')
    points=[*center,*bbox.get('min',[]),*bbox.get('max',[])]
    if len(points)!=9 or any(type(x) not in (int,float) or not isfinite(x) for x in points):
        raise ValueError('Finite three-dimensional centroid and bounds required')
    expected_volume=prod(size)
    expected_points=[*[x+s/2 for x,s in zip(origin,size)],*origin,*[x+s for x,s in zip(origin,size)]]
    volume_error=abs(volume-expected_volume)/expected_volume
    position_error=max(abs(x-y) for x,y in zip(points,expected_points))
    return dict(comparison_passed=volume_error<=RELATIVE_VOLUME_TOLERANCE and position_error<=POSITION_TOLERANCE_M,
        source_part_id=name,native_label=label,native_names_preserved=label==name,
        source_identity_basis='Exact generated name' if label==name else 'Single solid with analytic volume/centroid/bounds correspondence; imported label preserved',
        expected_volume_m3=expected_volume,measured_volume_m3=volume,
        expected_centroid_m=expected_points[:3],measured_centroid_m=center,
        measured_bounds_m=bbox,relative_volume_error=volume_error,maximum_position_error_m=position_error,
        tolerances=dict(relative_volume=RELATIVE_VOLUME_TOLERANCE,position_m=POSITION_TOLERANCE_M),
        tolerance_scope='Numerical primitive comparison only; no approved manufacturing tolerance',**FLAGS)


def reopen_measurements(replies):
    ids=[r.get('id') for r in replies if r.get('id') is not None]
    if len(ids)!=5 or set(ids)!=set(range(1,6)):raise ValueError('Complete unique reopen replies required')
    payloads={i:native.payload(next(r for r in replies if r.get('id')==i)) for i in range(2,6)}
    return {name:solidcraft.parse_measurements(payloads[i]) for name,i in [('native',3),('step',5)]}


def _git(root,*args):return subprocess.check_output(['git','-C',str(root),*args],text=True).strip()


def run(root,output):
    root,output=Path(root).resolve(),Path(output).resolve()
    if output==root or root in output.parents:raise ValueError('External immutable CAD output required')
    if output.exists():raise ValueError('Fresh CAD output required; preserve previous runs')
    if digest(root/PRODUCER)!=_LOADED_SHA:raise ValueError('Loaded CAD runner changed; restart its caller')
    if _git(root,'status','--porcelain','--untracked-files=all'):raise ValueError('Clean source required')
    output.parent.mkdir(parents=True,exist_ok=True)
    admission=disk_admission(output.parent,minimum_free_gib=20.25)
    if not admission['admitted']:raise ValueError('20 GiB reserve plus 256 MiB output reservation required')
    native.executable('solidcraft')  # Verify availability, never install/download.
    module=door_module.build(root);stock=module['representative_stock'];case=stock['geometry_request']
    if (stock['stock_only'] is not True or stock['native_executed'] is not False
        or len(case['entities'])!=1 or case['entities'][0]['shape']!='box'):
        raise ValueError('One explicitly unexecuted gross stock box required')
    names=[PRODUCER,'engineering/design_search/craft_backends/native.py',
           'engineering/design_search/craft_backends/solidcraft.py','engineering/design_search/craft_backends/tools.json']
    sources={**module['source_sha256'],**{n:digest(root/n) for n in names}}
    commit=_git(root,'rev-parse','HEAD');output.mkdir()
    request=dict(schema='osr-door-stock-cad-request/1',source_commit=commit,source_tree=_git(root,'rev-parse','HEAD^{tree}'),
        module_id=module['module_id'],candidate_id=module['candidate_id'],parent_candidate_id=module['parent_candidate_id'],
        case=case,source_sha256=sources,tool=native.pin('solidcraft'),admission=admission,
        maximum_native_processes=2,timeout_s_per_process=120,memory_mib_per_process=2048,
        maximum_output_bytes=MAX_OUTPUT,numerical_tolerances=dict(volume_relative=RELATIVE_VOLUME_TOLERANCE,position_m=POSITION_TOLERANCE_M),
        scope='One gross stock blank in its local frame; no installed assembly, holes or qualification',
        protocol_reference='https://github.com/tangency-labs/solidcraft/blob/8e2b0cd60d14b4152b12b8f1fdb2bcfdcd8c52f4/crates/mcp/src/tools.rs',**FLAGS)
    request['request_id']=identity(request);native.write(output/'request.json',request)
    native.write(output/'commands.json',stock['solidcraft_commands'])
    executions=[]
    def check():
        if not disk_admission(output,minimum_free_gib=20)['admitted']:raise ValueError('Host reserve exhausted')
        if sum(p.stat().st_size for p in output.rglob('*') if p.is_file())>MAX_OUTPUT:
            raise ValueError('Observed aggregate CAD output budget exceeded')
        if any(digest(root/n)!=sha for n,sha in sources.items()) or _git(root,'rev-parse','HEAD')!=commit:
            raise ValueError('CAD source changed during execution')
    try:
        check();gen=output/'generate'
        executions.append(native.run('solidcraft',['run',output/'commands.json','--save',gen/'blank.sc',
            '--out',gen/'blank.step','--results','--json-out',gen/'results.json'],gen,
            read_roots=(output,),timeout_s=120,memory_mb=2048))
        if executions[-1]['execution']!='executed':raise ValueError('Stock generation failed; native logs retained')
        generated=solidcraft.parse_measurements(json.loads((gen/'results.json').read_bytes()))
        check()
        execution,replies=native.mcp('solidcraft',[('open',dict(path=str(gen/'blank.sc'))),('measure',{}),
            ('open',dict(path=str(gen/'blank.step'))),('measure',{})],output/'reopen',
            read_root=output,timeout_s=120,memory_mb=2048)
        executions.append(execution);native.write(output/'reopen-replies.json',replies)
        if execution['execution']!='executed':raise ValueError('Stock reopening failed; native logs retained')
        measurements={'generated':generated,**reopen_measurements(replies)}
        comparisons={stage:compare(case['entities'][0],value,allow_import_label=stage=='step') for stage,value in measurements.items()}
        native.write(output/'measurements.json',measurements);check()
        result=dict(schema='osr-door-stock-cad-result/1',request_id=request['request_id'],
            module_id=module['module_id'],candidate_id=module['candidate_id'],source_sha256=sources,
            stock_geometry_comparison_passed=all(x['comparison_passed'] for x in comparisons.values()),
            comparisons=comparisons,executions=executions,native_processes=len(executions),
            independent_exact_brep_verified=False,installed_operator_verified=False,
            output_budget_enforcement='Admission and between-process observed directory size, not an aggregate filesystem quota',
            artifact_sha256={str(p.relative_to(output)):digest(p) for p in sorted(output.rglob('*')) if p.is_file()},**FLAGS)
        result['evaluation_id']=identity(result);native.write(output/'result.json',result);return result
    except BaseException as error:
        native.write(output/'failure.json',dict(type=type(error).__name__,message=str(error),request_id=request['request_id'],executions=executions,**FLAGS))
        raise


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',type=Path,required=True);parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();result=run(args.root,args.output)
    print(json.dumps(dict(evaluation_id=result['evaluation_id'],stock_geometry_comparison_passed=result['stock_geometry_comparison_passed'])))


if __name__=='__main__':main()
