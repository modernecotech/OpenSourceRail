#!/usr/bin/env python3
"""A separate closed-frame next-experiment packet; never the selected baseline.

Current tracked code alone verifies and replays this package. Archived sources are
inert evidence. Integrity checks are cooperative, without an OS read-only sandbox.
"""
from pathlib import Path,PurePosixPath
from copy import deepcopy
from contextlib import redirect_stdout,redirect_stderr
import argparse,gzip,hashlib,importlib,importlib.util,io,json,shutil,sys,tarfile,tempfile,traceback
ROOT=Path(__file__).resolve().parents[2]
PRODUCER='tools/automation/frame-cell.py'
COMMON='tools/automation/sourced-bolster-cell.py'
COMMON_SHA='13ce074ed1934977f0875092c4e11e6b0d5bd96dbe5da1103a5968ce7d1b70b2'
MODEL='engineering/frame_refinement/model.py'
MODEL_SHA='e8c69db8edf093ea4a9549ecd2591930a68e277aad013e2818f9b4e329e8ac7d'
MAX_FILES=64;MAX_RAW=768*1024**2;MAX_COMPRESSED=128*1024**2
FLAGS=dict(physical_accepted=False,engineering_accepted=False,manufacturing_release=False,operating_release=False,selected_reference_changed=False)
REQUEST=dict(distance_m=2000.,variant='parker400-dpw-h300',distributed=False,ambient_C=55.)


def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def common(root=ROOT):
    root=Path(root).resolve()
    if sha(root/COMMON)!=COMMON_SHA or sha(root/MODEL)!=MODEL_SHA or sha(root/PRODUCER)!=sha(__file__):raise ValueError('Current tracked helper/model source differs')
    spec=importlib.util.spec_from_file_location('osr_frozen_bolster_common',root/COMMON);h=importlib.util.module_from_spec(spec);spec.loader.exec_module(h)
    c=h.modules(root);frame=importlib.import_module('engineering.frame_refinement.model')
    if Path(frame.__file__).resolve()!=root/MODEL:raise ValueError('Frame producer imported from another root')
    return h,c,frame


def source_map(root,h,c):
    out=c.sources(root)
    for name in (COMMON,PRODUCER,MODEL,'engineering/frame_refinement/__init__.py'):out[name]=h.sha(Path(root)/name)
    return dict(sorted(out.items()))


def boundary(old,new,h):
    """Check declared changed stock and unchanged complete service occurrences."""
    h.sealed(old);h.sealed(new)
    from engineering.component_registry import validate_registry
    for v in (old,new):
        validate_registry(v['registry'])
        if v['candidate_id']!=v['registry']['candidate_id'] or v['vehicle_id']!='V4':raise ValueError('Exact V4 registry required')
    revision=new.get('frame_refinement',{})
    if old['candidate_id']==new['candidate_id'] or revision.get('parent_candidate_id')!=old['candidate_id'] or revision.get('parent_vehicle_evaluation_id')!=old['evaluation_id']:raise ValueError('Frame ancestry differs')
    for key in ('requirements','functional_requirements','interfaces','architecture'):
        if h.encoded(old[key])!=h.encoded(new[key]):raise ValueError('Fixed interface changed: '+key)
    A={o['occurrence_id']:o for o in old['registry']['occurrences']};B={o['occurrence_id']:o for o in new['registry']['occurrences']}
    ap={p['physical_definition_id']:p for p in old['registry']['parts']};bp={p['physical_definition_id']:p for p in new['registry']['parts']}
    changes=revision['changed_stock'];local={r['occurrence_local_name']:r for r in changes}
    if len(local)!=len(changes):raise ValueError('Duplicate stock change declaration')
    declared={f'car-{car}/'+name for car in range(1,7) for name in local}
    def physical(o):return {k:v for k,v in o.items() if k!='candidate_id'}
    changed=set();protected=[];unchanged=[];allowed={'primary-body','bogie-interfaces'}
    if set(A)-set(B):raise ValueError('Frame record declares no removed occurrence IDs')
    for key in sorted(set(A)&set(B)):
        before,after=A[key],B[key];p,q=ap[before['part_definition_id']],bp[after['part_definition_id']]
        equal=h.encoded(physical(before))==h.encoded(physical(after)) and h.encoded(p)==h.encoded(q)
        if equal:
            unchanged.append(key)
            if not set(p['functions'])<=allowed:protected.append(dict(occurrence=physical(before),part=p))
            continue
        changed.add(key)
        if key not in declared or not set(p['functions'])<=allowed or not set(q['functions'])<=allowed:raise ValueError('Undeclared or non-body hardware change: '+key)
        row=local[key.split('/',1)[1]]
        if before['part_definition_id']!=row['parent_part_definition_id'] or after['part_definition_id']!=row['new_part_definition_id']:raise ValueError('Changed stock definition differs')
        if q['geometry']['dimensions_m']!=row['after_dimensions_m'] or p['geometry']['dimensions_m']!=row['before_dimensions_m']:raise ValueError('Changed stock dimensions differ')
        car=int(key.split('/')[0].split('-')[1]);position=list(row['new_position_m']);position[0]+=17.5*(car-1)
        if [r[3] for r in after['transform'][:3]]!=position:raise ValueError('Changed stock pose differs')
    if changed!=declared:raise ValueError('Declared changed-stock occurrence coverage differs')
    added=sorted(set(B)-set(A))
    if len(added)!=6*revision['new_occurrences_per_car'] or not added:raise ValueError('New counted stock coverage differs')
    if any(not set(bp[B[k]['part_definition_id']]['functions'])<={'primary-body'} for k in added):raise ValueError('New service hardware undeclared')
    return dict(schema='osr-frame-physical-boundary/1',parent_candidate_id=old['candidate_id'],candidate_id=new['candidate_id'],
        changed_occurrence_ids=sorted(changed),added_occurrence_ids=added,removed_occurrence_ids=[],unchanged_occurrences=len(unchanged),
        protected_nonbody_occurrences=len(protected),protected_physical_payload_id=h.identity(protected),
        exact_protected_parts_and_poses=True,candidate_binding_only_excluded=True,**FLAGS)


def derive(e,old,new,h,*,helper_sha256):
    h.sealed(e)
    if h.encoded(e['vehicle'])!=h.encoded(old) or e['candidate_id']!=old['candidate_id'] or h.encoded(e['summary'])!=h.encoded(old['summary']):raise ValueError('Parent equipment is not exact native ancestor')
    proof=boundary(old,new,h);power=e['complete_source_power_case'];h.sealed(power)
    if power['candidate_id']!=old['candidate_id'] or power['actual_registry_id']!=old['registry']['registry_id']:raise ValueError('Parent power binding differs')
    r=deepcopy(e);r.pop('evaluation_id');r.update(schema='osr-frame-derived-sourced-equipment/1',candidate_id=new['candidate_id'],parent_candidate_id=old['candidate_id'],vehicle=deepcopy(new),summary=deepcopy(new['summary']))
    invalidated=['structural-response','fitment','installed-clearance','service-access','installed-thermal-duty','fatigue','joint-strength']
    previous=r.pop('body_revision_derivation',None)
    r['frame_equipment_ancestry']=dict(parent_equipment_evaluation_id=e['evaluation_id'],parent_body_revision_derivation=previous)
    record=dict(schema='osr-frame-equipment-derivation/1',producer=PRODUCER,producer_sha256=helper_sha256,parent_wrapper_candidate_id=e['candidate_id'],parent_wrapper_evaluation_id=e['evaluation_id'],
        candidate_id=new['candidate_id'],native_vehicle_evaluation_id=new['evaluation_id'],boundary=proof,invalidated_outcomes=invalidated,
        historical_product_and_source_derivation_receipts_preserved=True,inherited_native_vehicle_diagnostics_are_ancestry_only=True,**FLAGS)
    record['derivation_id']=h.identity(record);r['body_revision_derivation']=record
    r['fitment_screens']=dict(status='invalidated-by-frame-revision',candidate_id=new['candidate_id'],accepted=False)
    r['dependency_invalidation']=dict(parent_candidate_id=old['candidate_id'],candidate_id=new['candidate_id'],invalidated_outcomes=invalidated,inherited_assembly_access_and_body_joint_outcomes_current=False)
    r['known_installation_scope']=dict(status='pending-revised-frame-installation-review',full_installed_mass_kg=None,all_installed_clearances_proved=False)
    p=deepcopy(power);p.pop('evaluation_id');p.update(schema='osr-frame-derived-power-binding/1',candidate_id=new['candidate_id'],body_candidate_id=new['candidate_id'],actual_registry_id=new['registry']['registry_id'],
        parent_power_case_evaluation_id=power['evaluation_id'],physical_hardware_boundary_id=h.identity(proof),installed_thermal_acceptance=False,all_final_position_clearances_proved=False)
    p['evaluation_id']=h.identity(p);r['complete_source_power_case']=p;r['evaluation_id']=h.identity(r);h.sealed(r)
    return r,record


def names():
    files={'parent-equipment.json.gz','equipment.json.gz','derivation.json','equipment-constraints.json','helper-source.py','input-sources.tar.gz','request.json','stdout.log','stderr.log','result.json.gz','ifc/V4.ifc','ifc/V4.ifc.receipt.json','ifc-verification.json'}
    files.update(a+'/'+n for a in ('ancestor-native','frame-native') for n in ('manifest.json','input.json','result.json','sources.tar','stdout.log','stderr.log'))
    return files


def ordinary(folder):
    folder=Path(folder)
    if folder.is_symlink() or any(p.is_symlink() or not(p.is_dir() or p.is_file()) for p in folder.rglob('*')):raise ValueError('Regular unlinked payload required')


def run(equipment_path,ancestor_native,frame_native,output,*,root=ROOT):
    h,c,f=common(root);root=Path(root);out=Path(output)
    if out.exists() or out.is_symlink():raise ValueError('Fresh immutable output required')
    for source in (Path(equipment_path).resolve().parent,Path(ancestor_native).resolve(),Path(frame_native).resolve()):
        if out.resolve()==source or source in out.resolve().parents:raise ValueError('Output cannot mutate retained inputs')
    epoch=c.sources(root);sources=source_map(root,h,c);out.mkdir(parents=True)
    try:
        from engineering.sourced_case import whole_contact,equipment
        from engineering.reference_cell import geometry
        e=h.read(equipment_path);h.write(out/'parent-equipment.json.gz',e);native=[]
        for name,source in (('ancestor-native',ancestor_native),('frame-native',frame_native)):
            source=Path(source);ordinary(source);check=whole_contact.verify(source,root=root)
            if check['execution']!='completed':raise ValueError('Completed source-bound native experiment required')
            shutil.copytree(source,out/name);native.append(dict(path=name,verification=check))
        old=h.read(out/'ancestor-native/input.json')['vehicle'];new=h.read(out/'frame-native/input.json')['vehicle']
        if h.encoded(f.revision(old,root=root))!=h.encoded(new):raise ValueError('Native vehicle differs from actual tracked physical generator')
        revised,record=derive(e,old,new,h,helper_sha256=sha(__file__))
        limits=equipment.constraints(revised,ambient_C=55.,disc_specific_heat_J_kgK=500.)
        h.write(out/'equipment.json.gz',revised);h.write(out/'derivation.json',record);h.write(out/'equipment-constraints.json',limits)
        (out/'helper-source.py').write_bytes(Path(__file__).read_bytes());(out/'input-sources.tar.gz').write_bytes(c.pipeline._input_archive(root,sources))
        h.write(out/'request.json',dict(schema='osr-frame-cell-request/1',request=REQUEST,source_sha256=sources,core_source_sha256=epoch,
            parent_equipment_evaluation_id=e['evaluation_id'],derived_equipment_evaluation_id=revised['evaluation_id'],native_packages=native,**FLAGS))
        with (out/'stdout.log').open('w') as stdout,(out/'stderr.log').open('w') as stderr,redirect_stdout(stdout),redirect_stderr(stderr):
            receipt=geometry.export_ifc(revised['vehicle'],out/'ifc');reopened=geometry.verify_ifc(revised['vehicle'],out/'ifc')
            h.write(out/'ifc-verification.json',dict(export_receipt=receipt,fresh_reopen=reopened))
            result=c.evaluate(revised,root=root,**REQUEST)
        h.check_case(result,revised,epoch);h.write(out/'result.json.gz',result)
        if source_map(root,h,c)!=sources:raise ValueError('Sources changed during execution')
        m=dict(schema='osr-frame-cell-package/1',execution='completed',selection_purpose='next-experiment-only',candidate_id=result['candidate_id'],body_candidate_id=new['candidate_id'],evaluation_id=result['evaluation_id'],
            source_sha256=sources,core_source_sha256=epoch,derivation_id=record['derivation_id'],conditional_arrivals=result['conditional_arrivals'],conditional_motion_screens=result['conditional_motion_screens'],
            numerical_native_recomputed=False,physical_qualification=None,operating_map_admitted=False,whole_life_cost=None,integrated_winner=None,
            inherited_installation_outcomes_invalidated=True,IFC_exported_and_reopened=True,
            limitations=['Conditional linear-domain experiment, not structural/material/joint qualification','Quasi-static drive; actual current dynamics, repeated cooling/protection and receiving braking remain open','Geometry includes nominal stock and purchased bounding envelopes, not accepted installed fitment','Disabled manufacturing drafts and partial B/C costs do not establish full installed/whole-life costs'],**FLAGS)
        m['files']=h.inventory(out)
        if set(m['files'])!=names():raise ValueError('Unexpected completed frame-cell inventory')
    except BaseException as err:
        (out/'failure.log').write_text(traceback.format_exc());m=dict(schema='osr-frame-cell-package/1',execution='failed',reason=type(err).__name__+': '+str(err),source_sha256=sources,core_source_sha256=epoch,**FLAGS)
        m['files']=h.inventory(out);m['package_id']=h.identity(m);h.write(out/'manifest.json',m);raise
    m['package_id']=h.identity(m);h.write(out/'manifest.json',m);return m


def verify(output,*,root=ROOT,replay=True):
    h,c,f=common(root);out=Path(output);ordinary(out);m=h.read(out/'manifest.json');h.sealed(m,'package_id')
    if m['execution']!='completed' or m['files']!=h.inventory(out) or set(m['files'])!=names():raise ValueError('Closed completed frame-cell payload required')
    if m['source_sha256']!=source_map(root,h,c) or m['core_source_sha256']!=c.sources(root) or sha(out/'helper-source.py')!=sha(__file__):raise ValueError('Current frame-cell sources differ')
    if m['selection_purpose']!='next-experiment-only' or m['physical_qualification'] is not None or m['operating_map_admitted'] is not False or m['whole_life_cost'] is not None or m['integrated_winner'] is not None or m['inherited_installation_outcomes_invalidated'] is not True or m['IFC_exported_and_reopened'] is not True or m['numerical_native_recomputed'] is not False:raise ValueError('Unsupported acceptance/closure claim')
    if (out/'input-sources.tar.gz').read_bytes()!=c.pipeline._input_archive(root,m['source_sha256']):raise ValueError('Source archive differs')
    from engineering.sourced_case import whole_contact,equipment
    from engineering.reference_cell import geometry
    req=h.read(out/'request.json');h.unreleased(req)
    if req['request']!=REQUEST or req['source_sha256']!=m['source_sha256'] or req['core_source_sha256']!=m['core_source_sha256']:raise ValueError('Exact request differs')
    if len(req['native_packages'])!=2 or {n['path'] for n in req['native_packages']}!={'ancestor-native','frame-native'}:raise ValueError('Exact native package pair required')
    for n in req['native_packages']:
        if whole_contact.verify(out/n['path'],root=root)!=n['verification']:raise ValueError('Native package linkage differs')
    old=h.read(out/'ancestor-native/input.json')['vehicle'];new=h.read(out/'frame-native/input.json')['vehicle']
    if h.encoded(f.revision(old,root=root))!=h.encoded(new):raise ValueError('Actual frame generator replay differs')
    parent=h.read(out/'parent-equipment.json.gz');revised,record=derive(parent,old,new,h,helper_sha256=sha(__file__))
    if req['parent_equipment_evaluation_id']!=parent['evaluation_id'] or req['derived_equipment_evaluation_id']!=revised['evaluation_id']:raise ValueError('Wrapper request binding differs')
    if h.encoded(revised)!=h.encoded(h.read(out/'equipment.json.gz')) or h.encoded(record)!=h.encoded(h.read(out/'derivation.json')):raise ValueError('Equipment derivation differs')
    limits=equipment.constraints(revised,ambient_C=55.,disc_specific_heat_J_kgK=500.)
    if h.encoded(limits)!=h.encoded(h.read(out/'equipment-constraints.json')):raise ValueError('Typed constraints differ')
    saved=h.read(out/'ifc-verification.json');actual=geometry.verify_ifc(revised['vehicle'],out/'ifc')
    if h.encoded(actual)!=h.encoded(saved['fresh_reopen']):raise ValueError('Fresh IFC geometry reopening differs')
    r=h.read(out/'result.json.gz');h.check_case(r,revised,m['core_source_sha256'])
    if any(m[k]!=r[k] for k in ('candidate_id','body_candidate_id','evaluation_id','conditional_arrivals','conditional_motion_screens')) or m['derivation_id']!=record['derivation_id']:raise ValueError('Frame-cell summary differs')
    if replay and h.encoded(r)!=h.encoded(c.evaluate(revised,root=root,**REQUEST)):raise ValueError('Actual nine-context downstream replay differs')
    return dict(verified=True,package_id=m['package_id'],actual_IFC_reopened=True,semantic_replay_executed=replay,numerical_native_recomputed=False,cases=1,journeys=9,physical_qualification=None,**FLAGS)


def safe_unpack(archive,output):
    archive=Path(archive);target=Path(output)
    if archive.is_symlink() or not archive.is_file() or archive.stat().st_size>MAX_COMPRESSED:raise ValueError('Bounded regular compressed publication required')
    with tarfile.open(archive,'r:gz') as tar:
        seen=set();total=0
        for member in tar:
            path=PurePosixPath(member.name)
            if not member.isfile() or path.is_absolute() or '..' in path.parts or '\\' in member.name or member.name in seen or member.size<0:raise ValueError('Unsafe/duplicate archive member')
            seen.add(member.name);total+=member.size
            if len(seen)>MAX_FILES or total>MAX_RAW:raise ValueError('Publication extraction budget exceeded')
            dest=target/member.name;dest.parent.mkdir(parents=True,exist_ok=True)
            with tar.extractfile(member) as src,dest.open('xb') as out:shutil.copyfileobj(src,out)


def snapshot(folder,h):
    ordinary(folder);folder=Path(folder)
    return {p.relative_to(folder).as_posix():dict(bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(folder.rglob('*')) if p.is_file()}


def publish(state,output,*,root=ROOT):
    h,c,f=common(root);check=verify(state,root=root,replay=True);folder=Path(state);target=Path(output)
    if target.resolve()==folder.resolve() or folder.resolve() in target.resolve().parents:raise ValueError('Publication must remain outside closed experiment')
    if target.exists():raise ValueError('Fresh immutable publication required')
    pinned=snapshot(folder,h);m=h.read(folder/'manifest.json')
    if m['package_id']!=check['package_id']:raise ValueError('Experiment changed after verification')
    files=sorted(p for p in folder.rglob('*') if p.is_file())
    if len(files)>MAX_FILES or sum(p.stat().st_size for p in files)>MAX_RAW:raise ValueError('Publication inventory exceeds budget')
    stream=io.BytesIO()
    with tarfile.open(fileobj=stream,mode='w') as tar:
        for path in files:
            raw=path.read_bytes();name=path.relative_to(folder).as_posix()
            if pinned.get(name)!=dict(bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest()):raise ValueError('Experiment bytes changed during publication')
            info=tarfile.TarInfo(name);info.size=len(raw);info.mode=0o644;info.mtime=0;tar.addfile(info,io.BytesIO(raw))
    raw=gzip.compress(stream.getvalue(),mtime=0)
    if len(raw)>MAX_COMPRESSED:raise ValueError('Compressed publication exceeds budget')
    if snapshot(folder,h)!=pinned or source_map(root,h,c)!=m['source_sha256']:raise ValueError('Experiment inventory/source changed during publication')
    target.mkdir(parents=True);(target/'frame-cell.tar.gz').write_bytes(raw)
    summary={k:m[k] for k in ('package_id','candidate_id','body_candidate_id','evaluation_id','conditional_arrivals','conditional_motion_screens','physical_qualification','selection_purpose')};summary.update(FLAGS);h.write(target/'summary.json',summary)
    pub=dict(schema='osr-frame-cell-publication/1',source_sha256=source_map(root,h,c),validation=check,files={n:dict(sha256=sha(target/n),bytes=(target/n).stat().st_size) for n in ('frame-cell.tar.gz','summary.json')},**FLAGS)
    pub['publication_id']=h.identity(pub);h.write(target/'manifest.json',pub);return pub


def verify_publication(output,*,root=ROOT):
    h,c,f=common(root);folder=Path(output);ordinary(folder)
    if {p.name for p in folder.iterdir()}!={'manifest.json','frame-cell.tar.gz','summary.json'}:raise ValueError('Closed publication inventory required')
    pub=h.read(folder/'manifest.json');h.sealed(pub,'publication_id')
    if pub['source_sha256']!=source_map(root,h,c) or set(pub['files'])!={'frame-cell.tar.gz','summary.json'}:raise ValueError('Publication source or inventory differs')
    for name,item in pub['files'].items():
        p=folder/name
        if p.stat().st_size!=item['bytes'] or sha(p)!=item['sha256']:raise ValueError('Publication payload differs')
    with tempfile.TemporaryDirectory(prefix='osr-frame-current-replay-') as temp:
        safe_unpack(folder/'frame-cell.tar.gz',temp);check=verify(temp,root=root,replay=True)
        if check!=pub['validation']:raise ValueError('Publication actual replay differs')
        m=h.read(Path(temp)/'manifest.json');summary={k:m[k] for k in ('package_id','candidate_id','body_candidate_id','evaluation_id','conditional_arrivals','conditional_motion_screens','physical_qualification','selection_purpose')};summary.update(FLAGS)
        if h.encoded(summary)!=h.encoded(h.read(folder/'summary.json')):raise ValueError('Publication summary differs')
    return dict(check,publication_id=pub['publication_id'])


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',type=Path,default=ROOT);sub=p.add_subparsers(dest='command',required=True)
    r=sub.add_parser('run')
    for k in ('equipment','ancestor-native','frame-native','output'):r.add_argument('--'+k,type=Path,required=True)
    v=sub.add_parser('verify');v.add_argument('output',type=Path);v.add_argument('--integrity-only',action='store_true')
    v=sub.add_parser('publish');v.add_argument('state',type=Path);v.add_argument('--output',type=Path,required=True)
    v=sub.add_parser('verify-publication');v.add_argument('output',type=Path)
    a=p.parse_args()
    if a.command=='run':value=run(a.equipment,a.ancestor_native,a.frame_native,a.output,root=a.root)
    elif a.command=='verify':value=verify(a.output,root=a.root,replay=not a.integrity_only)
    elif a.command=='publish':value=publish(a.state,a.output,root=a.root)
    else:value=verify_publication(a.output,root=a.root)
    print(json.dumps(value,sort_keys=True,indent=2))
if __name__=='__main__':main()
