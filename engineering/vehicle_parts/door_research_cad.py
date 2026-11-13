"""One-process SolidCraft visual control for the held 30 mm door research child.

Only gross header/guide/pulley envelopes are solids. The proposed belt route is
retained as data; pitch, teeth, tension, mounts, fits and motion remain unknown.
"""
import argparse
import json
from math import isfinite, pi, prod
from pathlib import Path
import shutil
import subprocess

from engineering.performance import disk_admission
from engineering.station_rail.common import digest, identity
from engineering.vehicle_parts import ROOT, FLAGS, door_research_child
from engineering.design_search.craft_backends import native, solidcraft

PRODUCER='engineering/vehicle_parts/door_research_cad.py'
_LOADED_SHA=digest(__file__)
CHILD='87d25968e8a3ca413221e72bf2bc9bce367060738da7e6c90d5f4eded391e865'
RADIUS_M=.03
MAX_OUTPUT_BYTES=1024**3
REQUIRED_FREE_GIB=21


def _git(root,*args):
    return subprocess.check_output(['git','-C',str(root),*args],text=True,timeout=10).strip()


def scene_case(child):
    if (child.get('physical_candidate_id')!=CHILD or
            child.get('necessary_bounds',{}).get('pulley_pitch_radius_m')!=RADIUS_M or
            child.get('disposition')!='held-research-geometry' or
            child.get('evaluation_id')!=identity({k:v for k,v in child.items() if k!='evaluation_id'}) or
            child.get('candidate_adopted') is not False):
        raise ValueError('Exact unselected 30 mm research child required')
    physical=child['physical_definition'];frame=physical['proposed_car_local_header_frame']
    x,y,z=frame['translation_m'];header=child['necessary_bounds']['header_stock_length_m']
    guide=physical['guide'];belt=physical['belt']
    if (header!=3. or guide['stock_cut_length_m']!=2.9 or belt['stock_cut_length_m']!=5.8
            or frame['rotation_matrix']!=[[1.,0.,0.],[0.,1.,0.],[0.,0.,1.]]):
        raise ValueError('Proposed stock or frame changed')
    # Rectangular stock bounds and nominal pulley envelope are diagnostic
    # solids, not their unknown finished sections or material volumes.
    entities=[
        dict(id='header-backplate/gross-stock',shape='box',at_m=[x-header/2,y-.004,z-.11],
             size_m=[header,.008,.22]),
        dict(id='guide-rail/nominal-bounding-box',shape='box',at_m=[x-1.45,y-.025,z-.0175],
             size_m=[2.9,.05,.035]),
    ]
    for name,centre in (('drive',belt['drive_axis_origin_car_m']),
                        ('idler',belt['idler_axis_origin_car_m'])):
        entities.append(dict(id=name+'-pulley/gross-envelope',shape='cylinder',
            at_m=[centre[0],centre[1]-.0175,centre[2]],axis=[0.,1.,0.],
            radius_m=.0375,length_m=.035))
    case=dict(case_id='held-door-header-visual-envelope-30mm/1',
        candidate_id=CHILD,component_geometry_id=identity(dict(candidate_id=CHILD,entities=entities,
            visual_scope='gross envelopes, no belt solid or mated assembly')),
        source_evaluation_id=child['evaluation_id'],source_selection_id=None,
        entities=entities,materials={},belt_route_polyline_m=child['parent_route_proposal']['belt']['closed_pitch_path_m'],
        visual_scope='Four gross envelope solids; belt remains an unverified non-solid proposed path',
        **FLAGS)
    solidcraft.script_for(case)  # Cheap interface/domain check before native admission.
    return case


def _size(folder):
    return sum(p.stat().st_size for p in folder.rglob('*') if p.is_file())


def _measure(case,raw):
    actual=solidcraft.parse_measurements(raw)
    by_id={b['id']:b for b in actual['bodies']}
    if len(by_id)!=4 or set(by_id)!={e['id'] for e in case['entities']}:
        raise ValueError('Four exact named native envelope bodies required')
    if any(b['closed'] is not True or type(b['volume_m3']) not in (int,float)
           or not isfinite(b['volume_m3']) or b['volume_m3']<=0 for b in by_id.values()):
        raise ValueError('Finite closed native envelope bodies required')
    comparisons={}
    for entity in case['entities']:
        if entity['shape']=='box':nominal=prod(entity['size_m'])
        else:nominal=pi*entity['radius_m']**2*entity['length_m']
        observed=by_id[entity['id']]['volume_m3']
        comparisons[entity['id']]=dict(nominal_envelope_volume_m3=nominal,
            native_tessellated_volume_m3=observed,relative_difference=abs(observed-nominal)/nominal,
            exact_material_volume_verified=False)
    return actual,comparisons


def run(output,*,root=ROOT):
    root=Path(root).resolve();output=Path(output).absolute()
    if (output==root or root in output.parents or output.exists() or output.is_symlink()
            or any(p.is_symlink() for p in output.parents)):
        raise ValueError('Fresh ordinary external CAD output required')
    output.parent.mkdir(parents=True,exist_ok=True)
    output.mkdir()
    commit=None;candidate=None;phase='source'
    try:
        if root!=ROOT or digest(root/PRODUCER)!=_LOADED_SHA:
            raise ValueError('Loaded CAD source/worktree changed')
        if _git(root,'status','--porcelain','--untracked-files=all'):
            raise ValueError('Clean committed source required for native CAD')
        commit=_git(root,'rev-parse','HEAD')
        candidate=door_research_child.evaluate_radius(RADIUS_M)
        case=scene_case(candidate)
        phase='admission'
        admission=disk_admission(output,minimum_free_gib=REQUIRED_FREE_GIB)
        if not admission['admitted']:
            raise ValueError('20 GiB host reserve plus 1 GiB CAD scratch unavailable')
        phase='tool'
        executable=native.executable('solidcraft')
        names=[PRODUCER,'engineering/design_search/craft_backends/native.py',
            'engineering/design_search/craft_backends/solidcraft.py',
            'engineering/design_search/craft_backends/tools.json']
        sources={**candidate['source_sha256'],**{n:digest(root/n) for n in names}}
        commands=solidcraft.script_for(case)
        request=dict(schema='osr-v07-door-research-cad-request/1',source_commit=commit,
            source_tree=_git(root,'rev-parse','HEAD^{tree}'),
            physical_candidate_id=CHILD,parent_physical_candidate_id=candidate['parent_physical_candidate_id'],
            parent_installed_candidate_id=candidate['parent_installed_candidate_id'],
            source_evaluation_id=candidate['evaluation_id'],case=case,
            source_sha256=sources,tool=native.pin('solidcraft'),
            tool_binary_sha256=digest(executable),resource_admission=admission,
            maximum_native_processes=1,timeout_s=120,address_space_mib=2048,
            maximum_output_bytes=MAX_OUTPUT_BYTES,
            scope='Unselected visual stock envelopes only; no installed fit, belt solid or physical qualification',**FLAGS)
        request['request_id']=identity(request)
        native.write(output/'request.json',request)
        native.write(output/'commands.json',commands)
        free_before=shutil.disk_usage(output).free
        phase='native'
        execution=native.run('solidcraft',[
            'run',output/'commands.json','--save',output/'native/scene.sc',
            '--out',output/'native/scene.step','--results','--json-out',output/'native/results.json'],
            output/'native',read_roots=(output,),timeout_s=120,memory_mb=2048)
        if execution['execution']!='executed':
            raise ValueError('Native envelope generation failed; logs retained')
        phase='verification'
        if _git(root,'rev-parse','HEAD')!=commit or _git(root,'status','--porcelain','--untracked-files=all'):
            raise ValueError('CAD source changed during execution')
        if any(digest(root/n)!=sha for n,sha in sources.items()):
            raise ValueError('CAD source bytes changed during execution')
        if _size(output)>MAX_OUTPUT_BYTES or not disk_admission(output,minimum_free_gib=20)['admitted']:
            raise ValueError('CAD output budget or host reserve exhausted')
        for path in (output/'native/scene.sc',output/'native/scene.step',output/'native/results.json'):
            if not path.is_file() or path.stat().st_size==0:raise ValueError('Native scene, STEP and results required')
        measured,comparisons=_measure(case,json.loads((output/'native/results.json').read_bytes()))
        native.write(output/'measurements.json',measured)
        result=dict(schema='osr-v07-door-research-cad-result/1',request_id=request['request_id'],
            physical_candidate_id=CHILD,source_evaluation_id=candidate['evaluation_id'],
            component_geometry_id=case['component_geometry_id'],source_sha256=sources,
            native_execution=execution,native_processes=1,comparisons=comparisons,
            wall_seconds=execution['elapsed_s'],
            peak_rss_kib=None if execution['usage'] is None else execution['usage'].get('peak_rss_kib'),
            disk_observation=dict(free_bytes_before=free_before,
                free_bytes_after=shutil.disk_usage(output).free,
                output_logical_bytes=_size(output),
                aggregate_quota_enforced=False,peak_temporary_disk_bytes=None),
            belt_route_is_non_solid=True,scene_reopened=False,step_reopened=False,
            independent_exact_brep_verified=False,installed_mated_assembly_verified=False,
            required_mount_motion_tension_and_supplier_inputs=candidate['unresolved_inputs'],
            candidate_adopted=False,**FLAGS)
        result['evaluation_id']=identity(result)
        native.write(output/'result.json',result)
        if _size(output)>MAX_OUTPUT_BYTES:
            raise ValueError('CAD output budget exceeded after sealing results')
        manifest=dict(schema='osr-v07-door-research-cad-packet/1',status='held-visual-control',
            result_evaluation_id=result['evaluation_id'],physical_candidate_id=CHILD,
            files_sha256={p.relative_to(output).as_posix():digest(p) for p in sorted(output.rglob('*')) if p.is_file()},
            **FLAGS)
        manifest['manifest_id']=identity(manifest);native.write(output/'manifest.json',manifest)
        return result
    except BaseException as error:
        native.write(output/'failure.json',dict(schema='osr-v07-door-research-cad-failure/1',
            type=type(error).__name__,message=str(error),phase=phase,source_commit=commit,
            physical_candidate_id=CHILD,source_evaluation_id=None if candidate is None else candidate['evaluation_id'],
            **FLAGS))
        manifest=dict(schema='osr-v07-door-research-cad-packet/1',
            status=('held-'+phase if phase in ('source','admission','tool') else 'failed-'+phase),
            physical_candidate_id=CHILD,
            files_sha256={p.relative_to(output).as_posix():digest(p) for p in sorted(output.rglob('*')) if p.is_file()},
            **FLAGS)
        manifest['manifest_id']=identity(manifest);native.write(output/'manifest.json',manifest)
        raise


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',required=True,type=Path)
    args=parser.parse_args()
    value=run(args.output)
    print(json.dumps(dict(evaluation_id=value['evaluation_id'],physical_candidate_id=CHILD,
        native_processes=value['native_processes'],installed_mated_assembly_verified=False),sort_keys=True))


if __name__=='__main__':main()
