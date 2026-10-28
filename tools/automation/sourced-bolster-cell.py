#!/usr/bin/env python3
"""Propagate an independently recorded bolster revision, without changing baseline.

Only a declared primary-body/bogie-interface physical change is permitted. Old
product and numerical records remain ancestry, never recursively rebound receipts.
The controller uses cooperative checks, not an OS read-only sandbox.
"""
from pathlib import Path
from copy import deepcopy
from contextlib import redirect_stdout,redirect_stderr
import argparse,gzip,hashlib,importlib,json,shutil,sys,tarfile,traceback
ROOT=Path(__file__).resolve().parents[2]
PRODUCER='tools/automation/sourced-bolster-cell.py'
FLAGS=dict(physical_accepted=False,engineering_accepted=False,manufacturing_release=False,operating_release=False,selected_reference_changed=False)
REQUEST=dict(distance_m=2000.,variant='parker400-dpw-h300',distributed=False,ambient_C=55.)
LIMIT=256*1024**2


def encoded(v):return (json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False)+'\n').encode()
def identity(v):return hashlib.sha256(encoded(v)).hexdigest()
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,v):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);raw=encoded(v);p.write_bytes(gzip.compress(raw,mtime=0) if p.suffix=='.gz' else raw)
def read(p):
    p=Path(p)
    if p.is_symlink() or not p.is_file() or p.stat().st_size>LIMIT:raise ValueError('Ordinary bounded input required')
    if p.suffix=='.gz':
        with gzip.open(p,'rb') as f:raw=f.read(LIMIT+1)
    else:raw=p.read_bytes()
    if len(raw)>LIMIT:raise ValueError('Decompression budget exceeded')
    return json.loads(raw)
def unreleased(v):
    if isinstance(v,dict):
        for k,x in v.items():
            if k in FLAGS and x is not False:raise ValueError('Research input cannot grant release')
            unreleased(x)
    elif isinstance(v,list):
        for x in v:unreleased(x)
def sealed(v,key='evaluation_id'):
    if v.get(key)!=identity({k:x for k,x in v.items() if k!=key}):raise ValueError('Recorded identity differs')
    unreleased(v)
def modules(root):
    root=Path(root).resolve();sys.path.insert(0,str(root));c=importlib.import_module('engineering.sourced_case.coordinator')
    if Path(c.__file__).resolve()!=root/'engineering/sourced_case/coordinator.py':raise ValueError('Imported source root differs')
    return c


def boundary(old,new):
    """Only the registry candidate binding is excluded from physical comparison."""
    sealed(old);sealed(new)
    from engineering.component_registry import validate_registry
    for v in (old,new):
        validate_registry(v['registry'])
        if v['candidate_id']!=v['registry']['candidate_id'] or v['vehicle_id']!='V4':raise ValueError('Exact V4 registry required')
    revision=new.get('bolster_revision',{})
    if old['candidate_id']==new['candidate_id'] or revision.get('parent_candidate_id')!=old['candidate_id'] or revision.get('parent_vehicle_evaluation_id')!=old['evaluation_id']:
        raise ValueError('New bolster physical ancestry differs')
    for key in ('requirements','functional_requirements','interfaces','architecture'):
        if encoded(old[key])!=encoded(new[key]):raise ValueError('Bolster changed fixed vehicle interface '+key)
    A={o['occurrence_id']:o for o in old['registry']['occurrences']};B={o['occurrence_id']:o for o in new['registry']['occurrences']}
    ap={p['physical_definition_id']:p for p in old['registry']['parts']};bp={p['physical_definition_id']:p for p in new['registry']['parts']}
    def physical(o):return {k:v for k,v in o.items() if k!='candidate_id'}
    for key in set(A)&set(B):
        if encoded(physical(A[key]))!=encoded(physical(B[key])) or encoded(ap[A[key]['part_definition_id']])!=encoded(bp[B[key]['part_definition_id']]):
            raise ValueError('Retained occurrence/part/pose changed: '+key)
    removed=set(A)-set(B);added=set(B)-set(A);allowed={'primary-body','bogie-interfaces'}
    if not removed or not added:raise ValueError('Actual primary load-path revision required')
    for ids,O,P in ((removed,A,ap),(added,B,bp)):
        for key in ids:
            if not set(P[O[key]['part_definition_id']]['functions'])<=allowed:raise ValueError('Non-body hardware changed: '+key)
    declared=set(revision.get('removed_local_names',[]))
    if removed!={f'car-{car}/'+local for car in range(1,7) for local in declared}:raise ValueError('Removed structural stock differs from declared revision')
    if any(not key.split('/',1)[1].startswith('bolster-') for key in added):raise ValueError('Unexpected added physical stock')
    unchanged=sorted(set(A)&set(B));protected=[key for key in unchanged if not set(ap[A[key]['part_definition_id']]['functions'])<=allowed]
    payload=[dict(occurrence=physical(A[k]),part=ap[A[k]['part_definition_id']]) for k in protected]
    return dict(schema='osr-bolster-physical-boundary/1',parent_candidate_id=old['candidate_id'],candidate_id=new['candidate_id'],
        parent_vehicle_evaluation_id=old['evaluation_id'],native_vehicle_evaluation_id=new['evaluation_id'],
        retained_occurrences=len(unchanged),protected_nonbody_occurrences=len(protected),protected_physical_payload_id=identity(payload),
        protected_occurrence_ids=protected,removed_occurrence_ids=sorted(removed),added_occurrence_ids=sorted(added),
        all_shared_part_definitions_byte_identical=True,all_retained_physical_occurrences_and_poses_byte_identical=True,
        excluded_occurrence_field='candidate_id only; registry binding, not hardware',purchased_service_power_brake_hardware_unchanged=True,**FLAGS)


def derive(e,ancestor,new,*,helper_sha256):
    """Return compatible, newly sealed equipment wrapper; native vehicle untouched."""
    sealed(e)
    if encoded(e['vehicle'])!=encoded(ancestor):raise ValueError('Canonical vehicle is not exact native ancestor')
    proof=boundary(ancestor,new)
    if e['candidate_id']!=ancestor['candidate_id'] or encoded(e['summary'])!=encoded(ancestor['summary']):raise ValueError('Parent wrapper differs from vehicle')
    oldpower=e['complete_source_power_case'];sealed(oldpower)
    if oldpower['candidate_id']!=ancestor['candidate_id'] or oldpower['actual_registry_id']!=ancestor['registry']['registry_id']:raise ValueError('Power hardware binding differs')
    r=deepcopy(e);r.pop('evaluation_id');r.update(schema='osr-derived-sourced-equipment/1',candidate_id=new['candidate_id'],
        parent_candidate_id=ancestor['candidate_id'],vehicle=deepcopy(new),summary=deepcopy(new['summary']))
    invalidated=['fitment','installed-clearance','support-strength','joint-strength','fatigue','structural-response','service-access','installed-thermal-duty']
    r['fitment_screens']=dict(status='invalidated-by-primary-body-revision',previous_evaluation_id=e['evaluation_id'],
        current_candidate_id=new['candidate_id'],accepted=False,reason='Unchanged purchased poses do not establish fitment against revised body')
    r['dependency_invalidation']=dict(schema='osr-bolster-downstream-invalidation/1',parent_candidate_id=ancestor['candidate_id'],candidate_id=new['candidate_id'],
        invalidated_outcomes=invalidated,inherited_vehicle_diagnostics_are_ancestry_only=True,
        inherited_assembly_access_and_body_joint_outcomes_current=False,all_installed_clearances_proved=False)
    power=deepcopy(oldpower);power.pop('evaluation_id');power.update(schema='osr-derived-bound-auxiliary-power/1',
        candidate_id=new['candidate_id'],body_candidate_id=new['candidate_id'],actual_registry_id=new['registry']['registry_id'],
        parent_power_case_evaluation_id=oldpower['evaluation_id'],physical_hardware_boundary_id=identity(proof),
        binding_derivation='Unchanged exact parts and physical occurrence transforms; installed fitment/thermal evidence invalidated',
        all_final_position_clearances_proved=False,installed_thermal_acceptance=False)
    # source_derivation, its IDs, public sources and actual counts are kept verbatim.
    power['evaluation_id']=identity(power);r['complete_source_power_case']=power
    record=dict(schema='osr-bolster-equipment-derivation/1',producer=PRODUCER,producer_sha256=helper_sha256,
        parent_wrapper_candidate_id=e['candidate_id'],parent_wrapper_evaluation_id=e['evaluation_id'],
        parent_vehicle_evaluation_id=ancestor['evaluation_id'],native_vehicle_evaluation_id=new['evaluation_id'],
        candidate_id=new['candidate_id'],boundary=proof,previous_product_and_evidence_identities_retained_as_ancestry=True,
        inherited_native_vehicle_diagnostics_are_not_current_fitment_acceptance=True,
        parent_power_case_evaluation_id=oldpower['evaluation_id'],source_derivation_evaluation_id=oldpower['source_derivation_evaluation_id'],
        source_derivation_body_candidate_id=oldpower['source_derivation_body_candidate_id'],invalidated_outcomes=invalidated,**FLAGS)
    record['derivation_id']=identity(record);r['body_revision_derivation']=record
    r['known_installation_scope']=dict(status='pending-revised-body-installation-review',full_installed_mass_kg=None,
        preserved_parent_scope_is_ancestry=e.get('known_installation_scope'),current_clearance_qualified=False)
    r['evaluation_id']=identity(r);sealed(r)
    return r,record


def check_case(r,e,epoch):
    sealed(r)
    if r['source_sha256']!=epoch or r['body_candidate_id']!=e['candidate_id'] or any(r.get(k)!=v for k,v in REQUEST.items()):raise ValueError('Wrong downstream case/source/request')
    b=r['bundle'];sealed(b,'definition_id');sealed(r['drive'])
    cid=r['candidate_id']
    if b['candidate_id']!=cid or b['body_candidate_id']!=e['candidate_id'] or r['drive']['body_candidate_id']!=e['candidate_id']:raise ValueError('Mixed downstream identities')
    if identity(b['architecture_case']['physical_definition']['composition'])!=cid or b['propulsion_component_id']!=r['drive']['candidate_id']:raise ValueError('Physical composition differs')
    if any(r[name]['candidate_id']!=cid for name in ('civil','manufacturing','partial_public_price')):raise ValueError('Downstream cell binding differs')
    expected={'empty','normal','crowd-control','uphill','downhill','low-adhesion','one-bank-failed','power-interruption','emergency'}
    if len(r['journeys'])!=9 or {x['name'] for x in r['journeys']}!=expected:raise ValueError('Nine required contexts missing')
    for row in r['journeys']:
        q=row['result'];sealed(q)
        if q['candidate_id']!=cid or q['bundle_definition_id']!=b['definition_id'] or q['alternative_candidate_id']!=r['drive']['candidate_id']:raise ValueError('Mixed journey inputs')
    if r['conditional_arrivals']!=sum(x['result'].get('conditional_numerical_arrival',False) for x in r['journeys']) or r['conditional_motion_screens']!=sum(x['result'].get('requested_service_screen_passed',False) for x in r['journeys']):raise ValueError('Journey summary differs')
    if r['qualified_journeys']!=0 or r['operating_map_admitted'] is not False or r['integrated_winner'] is not None:raise ValueError('Unsupported engineering qualification')


def expected_payload(ifc):
    names={'parent-equipment.json.gz','equipment.json.gz','derivation.json','equipment-constraints.json','helper-source.py','input-sources.tar.gz','request.json','stdout.log','stderr.log','result.json.gz'}
    native={'manifest.json','input.json','result.json','sources.tar','stdout.log','stderr.log'}
    names.update(prefix+'/'+n for prefix in ('ancestor-native','bolster-native') for n in native)
    if ifc:names.update({'ifc/V4.ifc','ifc/V4.ifc.receipt.json','ifc-verification.json'})
    return names


def inventory(folder):
    return {p.relative_to(folder).as_posix():dict(bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(folder.rglob('*')) if p.is_file() and p!=folder/'manifest.json'}


def run(equipment_path,ancestor_native,bolster_native,output,*,root=ROOT,ifc=False):
    if type(ifc) is not bool:raise ValueError('Explicit IFC execution flag required')
    c=modules(root);root=Path(root);out=Path(output)
    if out.exists() or out.is_symlink():raise ValueError('Fresh immutable output directory required')
    for ancestor in (Path(ancestor_native).resolve(),Path(bolster_native).resolve(),Path(equipment_path).resolve().parent):
        if out.resolve()==ancestor or ancestor in out.resolve().parents:raise ValueError('Output must not mutate retained input directories')
    if sha(root/PRODUCER)!=sha(__file__):raise ValueError('Executing helper source differs')
    epoch=c.sources(root);out.mkdir(parents=True);helper=sha(__file__)
    try:
        from engineering.sourced_case import whole_contact,equipment
        e=read(equipment_path);write(out/'parent-equipment.json.gz',e)
        native=[]
        for name,source in (('ancestor-native',ancestor_native),('bolster-native',bolster_native)):
            source=Path(source)
            if source.is_symlink() or any(p.is_symlink() or not p.is_file() for p in source.iterdir()):raise ValueError('Ordinary closed native package required')
            check=whole_contact.verify(source,root=root)
            if check['execution']!='completed':raise ValueError('Completed native revision required')
            shutil.copytree(source,out/name);native.append(dict(path=name,verification=check))
        old=read(out/'ancestor-native/input.json')['vehicle'];new=read(out/'bolster-native/input.json')['vehicle']
        derived,record=derive(e,old,new,helper_sha256=helper)
        # Exact catalogue/thermal/brake typed interface; this is not acceptance.
        limits=equipment.constraints(derived,ambient_C=55.,disc_specific_heat_J_kgK=500.)
        write(out/'equipment.json.gz',derived);write(out/'derivation.json',record);write(out/'equipment-constraints.json',limits)
        (out/'helper-source.py').write_bytes(Path(__file__).read_bytes())
        (out/'input-sources.tar.gz').write_bytes(c.pipeline._input_archive(root,epoch))
        write(out/'request.json',dict(schema='osr-bolster-cell-request/1',request=REQUEST,source_sha256=epoch,helper_sha256=helper,
            parent_equipment_evaluation_id=e['evaluation_id'],derived_equipment_evaluation_id=derived['evaluation_id'],native_packages=native,**FLAGS))
        if ifc:
            from engineering.reference_cell import geometry
            exported=geometry.export_ifc(derived['vehicle'],out/'ifc')
            reopened=geometry.verify_ifc(derived['vehicle'],out/'ifc')
            write(out/'ifc-verification.json',dict(export_receipt=exported,fresh_reopen=reopened))
        with (out/'stdout.log').open('w') as stdout,(out/'stderr.log').open('w') as stderr,redirect_stdout(stdout),redirect_stderr(stderr):
            result=c.evaluate(derived,root=root,**REQUEST)
        check_case(result,derived,epoch);write(out/'result.json.gz',result)
        if c.sources(root)!=epoch or sha(__file__)!=helper:raise ValueError('Sources changed during numerical evaluation')
        manifest=dict(schema='osr-bolster-cell-package/1',execution='completed',selection_purpose='next-experiment-only',
            candidate_id=result['candidate_id'],body_candidate_id=derived['candidate_id'],evaluation_id=result['evaluation_id'],
            derivation_id=record['derivation_id'],source_sha256=epoch,helper_sha256=helper,
            conditional_arrivals=result['conditional_arrivals'],conditional_motion_screens=result['conditional_motion_screens'],
            semantic_replay_executed=False,native_current_numerical_recomputed=False,
            revised_body_ifc_exported_and_reopened=ifc,
            inherited_installation_outcomes_invalidated=True,operating_map_admitted=False,integrated_winner=None,
            verifier_isolation='Cooperative integrity checks; no OS read-only sandbox',limitations=[
                'Native numerical result remains separately source-bound, not structural qualification',
                'Conditional quasi-static drive; current dynamics, repeated cooling, protection and receiving duty remain open',
                'Unchanged purchased equipment does not prove revised fitment, sweep or thermal installation',
                'Disabled manufacturing drafts and bounded process costs are not production release or whole-life cost'],**FLAGS)
    except BaseException as err:
        (out/'failure.log').write_text(traceback.format_exc())
        manifest=dict(schema='osr-bolster-cell-package/1',execution='failed',reason=type(err).__name__+': '+str(err),
            source_sha256=epoch,helper_sha256=helper,selection_purpose='next-experiment-only',**FLAGS)
        manifest['files']=inventory(out);manifest['package_id']=identity(manifest);write(out/'manifest.json',manifest)
        raise
    manifest['files']=inventory(out)
    if set(manifest['files'])!=expected_payload(ifc):raise ValueError('Unexpected completed package inventory')
    manifest['package_id']=identity(manifest);write(out/'manifest.json',manifest)
    return manifest


def verify(output,*,root=ROOT,replay=False):
    c=modules(root);out=Path(output);m=read(out/'manifest.json');sealed(m,'package_id')
    if out.is_symlink() or any(p.is_symlink() for p in out.rglob('*')):raise ValueError('Ordinary immutable package required')
    if m['files']!=inventory(out):raise ValueError('Closed payload inventory differs')
    if m['execution']!='completed':raise ValueError('Failed execution has no completed downstream result')
    if type(m.get('revised_body_ifc_exported_and_reopened')) is not bool or set(m['files'])!=expected_payload(m['revised_body_ifc_exported_and_reopened']):raise ValueError('Unexpected completed package inventory')
    if m.get('selection_purpose')!='next-experiment-only' or m.get('semantic_replay_executed') is not False or m.get('native_current_numerical_recomputed') is not False or m.get('inherited_installation_outcomes_invalidated') is not True or m.get('operating_map_admitted') is not False or m.get('integrated_winner') is not None:raise ValueError('Unsupported package completion claim')
    if m['source_sha256']!=c.sources(root) or m['helper_sha256']!=sha(__file__) or sha(out/'helper-source.py')!=m['helper_sha256']:raise ValueError('Package source epoch differs')
    if (out/'input-sources.tar.gz').read_bytes()!=c.pipeline._input_archive(root,m['source_sha256']):raise ValueError('Source archive differs')
    from engineering.sourced_case import whole_contact,equipment
    request=read(out/'request.json')
    if request['source_sha256']!=m['source_sha256'] or request['request']!=REQUEST or request['helper_sha256']!=m['helper_sha256']:raise ValueError('Request differs')
    if len(request['native_packages'])!=2 or {n['path'] for n in request['native_packages']}!={'ancestor-native','bolster-native'}:raise ValueError('Exact pair of native packages required')
    for n in request['native_packages']:
        if n['path'] not in ('ancestor-native','bolster-native') or whole_contact.verify(out/n['path'],root=root)!=n['verification']:raise ValueError('Native linkage differs')
    old=read(out/'ancestor-native/input.json')['vehicle'];new=read(out/'bolster-native/input.json')['vehicle']
    parent=read(out/'parent-equipment.json.gz')
    derived,record=derive(parent,old,new,helper_sha256=m['helper_sha256'])
    if request['parent_equipment_evaluation_id']!=parent['evaluation_id'] or request['derived_equipment_evaluation_id']!=derived['evaluation_id']:raise ValueError('Request wrapper binding differs')
    if encoded(derived)!=encoded(read(out/'equipment.json.gz')) or encoded(record)!=encoded(read(out/'derivation.json')):raise ValueError('Derived equipment replay differs')
    if m['revised_body_ifc_exported_and_reopened']:
        from engineering.reference_cell import geometry
        recorded=read(out/'ifc-verification.json')
        actual=geometry.verify_ifc(derived['vehicle'],out/'ifc')
        if encoded(actual)!=encoded(recorded['fresh_reopen']):raise ValueError('Fresh revised IFC reopening differs')
    limits=equipment.constraints(derived,ambient_C=55.,disc_specific_heat_J_kgK=500.)
    if encoded(limits)!=encoded(read(out/'equipment-constraints.json')):raise ValueError('Typed constraints differ')
    r=read(out/'result.json.gz');check_case(r,derived,m['source_sha256'])
    if any(m[k]!=r[k] for k in ('candidate_id','body_candidate_id','evaluation_id','conditional_arrivals','conditional_motion_screens')) or m['derivation_id']!=record['derivation_id']:raise ValueError('Package summary differs')
    if replay and encoded(r)!=encoded(c.evaluate(derived,root=root,**REQUEST)):raise ValueError('Fresh downstream numerical replay differs')
    return dict(verified=True,package_id=m['package_id'],execution='completed',semantic_replay_executed=replay,
        cases=1,journeys=9,selection_purpose='next-experiment-only',**FLAGS)


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',type=Path,default=ROOT);s=p.add_subparsers(dest='command',required=True)
    runp=s.add_parser('run')
    for name in ('equipment','ancestor-native','bolster-native','output'):runp.add_argument('--'+name,type=Path,required=True)
    runp.add_argument('--ifc',action='store_true')
    v=s.add_parser('verify');v.add_argument('output',type=Path);v.add_argument('--replay',action='store_true')
    a=p.parse_args()
    if a.command=='run':value=run(a.equipment,a.ancestor_native,a.bolster_native,a.output,root=a.root,ifc=a.ifc)
    else:value=verify(a.output,root=a.root,replay=a.replay)
    print(json.dumps(value,sort_keys=True,indent=2))
if __name__=='__main__':main()
