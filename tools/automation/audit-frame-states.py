#!/usr/bin/env python3
"""Independent saved-state assembly audit; never factorizes or solves a system.

Uses current source-bound element laws with a separate direct-scatter assembly,
checks registry/model geometry and retained hardware, and regenerates the physical
definition. This is an independent software consistency check, not a human
engineering review, independent physical model, test correlation or release.
"""
from pathlib import Path
import argparse,hashlib,json,os,resource,sys
import numpy as np
import scipy
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from engineering.station_rail.common import identity,encoded,digest
from engineering.sourced_case import whole_contact as w
from engineering.sourced_case import layered_structure as layer
from engineering.frame_refinement import model as definition
ROOT=Path(__file__).resolve().parents[2]
PRODUCER='tools/automation/audit-frame-states.py'
FLAGS=layer.FLAGS


def snapshot(folder):
    folder=Path(folder)
    if folder.is_symlink() or not folder.is_dir():raise ValueError('Ordinary native folder required')
    expected={'input.json','result.json','sources.tar','manifest.json','stdout.log','stderr.log'}
    if {p.name for p in folder.iterdir()}!=expected:raise ValueError('Closed native inventory differs')
    output={}
    for p in sorted(folder.iterdir()):
        if p.is_symlink() or not p.is_file():raise ValueError('Ordinary native files required')
        h=hashlib.sha256()
        with p.open('rb') as f:
            while block:=f.read(1024**2):h.update(block)
        output[p.name]=dict(bytes=p.stat().st_size,sha256=h.hexdigest())
    return output


def parent_check(old,new):
    if new['registry']['parent_candidate_id']!=old['candidate_id'] or new['frame_refinement']['parent_candidate_id']!=old['candidate_id'] or new['frame_refinement']['parent_vehicle_evaluation_id']!=old['evaluation_id']:raise ValueError('Exact physical/evaluation ancestry differs')
    if old['requirements']!=new['requirements'] or old['interfaces']!=new['interfaces']:raise ValueError('Fixed interfaces or requirements changed')
    A={o['occurrence_id']:o for o in old['registry']['occurrences']};B={o['occurrence_id']:o for o in new['registry']['occurrences']};P={p['physical_definition_id']:p for p in old['registry']['parts']};Q={p['physical_definition_id']:p for p in new['registry']['parts']}
    declared={c['occurrence_local_name']:c for c in new['frame_refinement']['changed_stock']};protected=unchanged=changed=0
    for key,o in A.items():
        if key not in B:raise ValueError('Unexpected removed parent occurrence')
        local=key.split('/',1)[1];p=P[o['part_definition_id']];q=Q[B[key]['part_definition_id']]
        if local in declared:
            c=declared[local]
            if p['physical_definition_id']!=c['parent_part_definition_id'] or q['physical_definition_id']!=c['new_part_definition_id'] or not set(p['functions'])<={'primary-body','bogie-interfaces'}:raise ValueError('Declared structural revision differs')
            changed+=1
        else:
            if {k:v for k,v in o.items() if k!='candidate_id'}!={k:v for k,v in B[key].items() if k!='candidate_id'} or p!=q:raise ValueError('Retained stock/hardware/pose changed')
            unchanged+=1
        if not set(p['functions'])<={'primary-body','bogie-interfaces'}:protected+=1
    return dict(parent_candidate_id=old['candidate_id'],candidate_id=new['candidate_id'],protected_nonbody_occurrences_byte_identical=protected,
        retained_occurrences_byte_identical_except_candidate_binding=unchanged,declared_structural_occurrences_changed=changed,
        new_occurrences=len(set(B)-set(A)),fixed_requirements_and_interfaces_unchanged=True)


def geometry_check(model,rows):
    lookup={r['occurrence']['occurrence_id']:r for r in rows};xyz=np.asarray(model['nodes']);frames=panels=0;maximum=0.
    for group in model['groups']:
        actual=lookup[group['source']];points=xyz[group['nodes']]
        if group['kind']=='frame':
            frames+=1;error=max(float(abs(np.asarray(group['lower'])-actual['lower']).max()),float(abs(np.asarray(group['upper'])-actual['upper']).max()))
            if np.any(points<actual['lower']-1e-10) or np.any(points>actual['upper']+1e-10):raise ValueError('Frame nodes leave registered stock')
            error=max(error,abs(float(np.linalg.norm(points[-1]-points[0]))-float(max(actual['dimensions']))))
        else:
            panels+=1;error=max(float(abs(np.ptp(points,axis=0)[:2]-actual['dimensions'][:2]).max()),float(abs((points.min(0)+points.max(0))[:2]/2-actual['position'][:2]).max()))
        maximum=max(maximum,error)
        if error>1e-10:raise ValueError('Registered geometry/model dimensions or pose differ')
    return dict(frames_checked=frames,cassettes_checked=panels,maximum_dimension_or_position_difference_m=maximum,
        source_occurrences_match=True,finite_joint_rank_six=all(j['rank']==6 for j in model['joint_mechanical_rank']))


def element_action(K,u):
    force=K@u
    return force,float(u@force/2)


def contact_action(B,stiffness,u):
    delta=B@u;traction=np.asarray(stiffness)*delta
    return B.T@traction,float(delta@traction/2)


def rigid_modes(xyz):
    out=np.zeros((len(xyz),6,6))
    for j in range(3):out[:,j,j]=1.;out[:,:3,3+j]=np.cross(np.eye(3)[j],xyz);out[:,3+j,3+j]=1.
    return out.reshape(len(xyz)*6,6)


def audit_model(vehicle,level,rows,panels):
    model=level['model'];xyz=np.asarray(model['nodes']);size=6*len(xyz);geometry=geometry_check(model,rows);cases,mass=w.loads(vehicle,model,rows,panels);load=dict(cases)
    supported=sum(r['part']['mass']['upper_bound_kg'] for r in rows if 'running-gear' not in r['part']['functions'])
    if abs(mass['supported_upper_mass_kg']-supported)>1e-7:raise ValueError('Independent supported mass differs')
    crowd=(supported+160*75)*w.G
    if abs(load['crowd160-upper'].reshape(-1,6)[:,2].sum()+crowd)>1e-6:raise ValueError('Crowd vertical force not conserved')
    modes=rigid_modes(xyz);elements=[];contacts=[];rigid_contact=rigid_element=0.
    for e in model['elements']:
        ids=np.asarray([6*e['a']+j for j in range(6)]+[6*e['b']+j for j in range(6)]);K,_,_=w._element_k(e,model['nodes']);elements.append((ids,K,e['source']))
        rigid_element=max(rigid_element,float(np.linalg.norm(K@modes[ids])/(max(1.,np.linalg.norm(K))*max(1.,np.linalg.norm(modes[ids])))))
    for link in model['links']:
        ids=np.asarray(link['dofs']);B=np.asarray(link['interpolation_B']);ks=np.asarray(link['stiffness_N_m']);contacts.append((ids,B,ks,tuple(link['source_pair'])));rigid_contact=max(rigid_contact,float(abs(B@modes[ids]).max()))
    if rigid_contact>1e-10 or rigid_element>1e-12:raise ValueError('Structural/contact rigid-body objectivity failed')
    free=np.setdiff1d(np.arange(size),model['fixed_dofs']);results=[]
    for saved in level['response']['cases']:
        u=np.asarray(saved['displacements_m_rad']).ravel();internal=np.zeros(size);member={};joint={};total=0.
        for ids,K,key in elements:
            f,E=element_action(K,u[ids]);np.add.at(internal,ids,f);member[key]=member.get(key,0.)+E;total+=E
        for ids,B,ks,key in contacts:
            f,E=contact_action(B,ks,u[ids]);np.add.at(internal,ids,f);joint[key]=joint.get(key,0.)+E;total+=E
        F=load[saved['name']];residual=float(np.linalg.norm((internal-F)[free])/max(1.,np.linalg.norm(F)));difference=abs(total-saved['strain_energy_J'])/max(1.,abs(total));work=float(u@F/2)
        if residual>=1e-6 or difference>=1e-6 or abs(total-work)/max(1.,abs(total))>=1e-6:raise ValueError('Independent saved-state equilibrium/energy failed')
        witness=max(saved['stress_witnesses'],key=lambda r:r['normal_stress_proxy_Pa']);jw=max(saved['joint_witnesses'],key=lambda r:r['traction_proxy_Pa'])
        R=internal-F;reactions=np.zeros_like(R);reactions[model['fixed_dofs']]=R[model['fixed_dofs']];global_load=(F+reactions).reshape(-1,6)
        results.append(dict(name=saved['name'],independent_free_relative_residual=residual,independent_strain_energy_J=total,
            saved_strain_energy_J=saved['strain_energy_J'],saved_energy_relative_difference=difference,external_work_J=work,
            member_energy_J=sum(member.values()),contact_energy_J=sum(joint.values()),closed_sill_plate_energy_J=sum(E for k,E in member.items() if '/frame-sill-' in k and any(t in k for t in ('-top','-bottom','-inner','-outer'))),
            force_balance_residual_N=global_load[:,:3].sum(0).tolist(),moment_balance_residual_Nm=(global_load[:,3:]+np.cross(xyz,global_load[:,:3])).sum(0).tolist(),
            maximum_translation_m=saved['maximum_translation_m'],maximum_rotation_rad=saved['maximum_rotation_rad'],
            saved_numerical_valid=saved['numerical_valid'],declared_linear_domain_suspect=saved['linear_kinematic_domain_suspect'],
            largest_member_energies=[dict(source=k,energy_J=E) for k,E in sorted(member.items(),key=lambda t:t[1],reverse=True)[:5]],
            largest_contact_energies=[dict(source_pair=list(k),energy_J=E) for k,E in sorted(joint.items(),key=lambda t:t[1],reverse=True)[:5]],
            maximum_member_normal_stress_proxy=witness,maximum_joint_traction_proxy=jw,approved_strength_margin=None,approved_functional_clearance_limit_m=None))
    return dict(mesh_m=model['mesh_m'],geometry=geometry,supported_upper_mass_kg=supported,crowd_force_N=crowd,
        nodes=len(xyz),elements=len(elements),finite_contact_points=len(contacts),maximum_contact_rigid_mode_error_m=rigid_contact,
        maximum_element_relative_rigid_mode_error=rigid_element,cases=results)


def tool_record():
    import numpy._core._multiarray_umath as numpy_kernel
    import scipy.sparse.linalg._dsolve._superlu as superlu
    def limits(which):return ['unlimited' if n==resource.RLIM_INFINITY else n for n in resource.getrlimit(which)]
    return dict(python_version=sys.version,python_executable=sys.executable,python_executable_sha256=digest(sys.executable),numpy_version=np.__version__,scipy_version=scipy.__version__,
        numpy_kernel_sha256=digest(numpy_kernel.__file__),superlu_sha256=digest(superlu.__file__),thread_environment={k:os.environ.get(k) for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS')},
        audit_RLIMIT_AS=limits(resource.RLIMIT_AS),audit_RLIMIT_CPU=limits(resource.RLIMIT_CPU),
        audit_isolation='Ordinary Python process; code reads native inputs and checks hashes before/after; no enforced read-only filesystem/network sandbox',
        fresh_factorization_executed=False,fresh_native_solve_executed=False)


def audit(native,*,parent_native,root=ROOT):
    if Path(w.__file__).resolve()!=Path(root).resolve()/'engineering/sourced_case/whole_contact.py' or Path(definition.__file__).resolve()!=Path(root).resolve()/'engineering/frame_refinement/model.py':raise ValueError('Imported evaluator/definition source root differs')
    native=Path(native).resolve();parent=Path(parent_native).resolve();before=snapshot(native);parent_before=snapshot(parent)
    checks=w.verify(native,root=root);parent_checks=w.verify(parent,root=root)
    if checks['execution']!='completed' or parent_checks['execution']!='completed':raise ValueError('Completed recorded frame and parent packages required')
    req=json.loads((native/'input.json').read_text());response=json.loads((native/'result.json').read_text());manifest=json.loads((native/'manifest.json').read_text());vehicle=req['vehicle'];ancestor=json.loads((parent/'input.json').read_text())['vehicle']
    lineage=parent_check(ancestor,vehicle);regenerated=definition.revision(ancestor,root=root)
    if encoded(regenerated)!=encoded(vehicle):raise ValueError('Current physical definition does not reproduce exact native vehicle')
    del regenerated
    rows,panels=layer.inventory(vehicle);levels=[audit_model(vehicle,level,rows,panels) for level in response['results']]
    if len(levels)!=2 or any(len(level['cases'])!=9 for level in levels):raise ValueError('Two meshes and nine contexts required')
    refinement=[]
    for a,b in zip(levels[0]['cases'],levels[1]['cases']):
        if a['name']!=b['name']:raise ValueError('Refinement contexts differ')
        refinement.append(dict(case=a['name'],maximum_translation_relative_change=abs(a['maximum_translation_m']-b['maximum_translation_m'])/max(1e-30,b['maximum_translation_m']),
            energy_increase_relative_to_coarse=(b['independent_strain_energy_J']-a['independent_strain_energy_J'])/max(1e-30,a['independent_strain_energy_J']),
            member_stress_proxy_relative_change=abs(a['maximum_member_normal_stress_proxy']['normal_stress_proxy_Pa']-b['maximum_member_normal_stress_proxy']['normal_stress_proxy_Pa'])/max(1.,b['maximum_member_normal_stress_proxy']['normal_stress_proxy_Pa'])))
    if snapshot(native)!=before or snapshot(parent)!=parent_before:raise ValueError('Native input bytes changed during audit')
    source=dict(req['source_sha256']);source[PRODUCER]=digest(Path(root)/PRODUCER)
    if source[PRODUCER]!=digest(__file__):raise ValueError('Current executing audit source differs')
    allcases=[c for level in levels for c in level['cases']]
    report=dict(schema='osr-independent-frame-saved-state-audit/1',audit_kind='independent-software-consistency-check',candidate_id=vehicle['candidate_id'],vehicle_evaluation_id=vehicle['evaluation_id'],
        native_package_id=manifest['package_id'],native_evaluation_id=response['evaluation_id'],source_sha256=dict(sorted(source.items())),
        input_native=str(native),parent_native=str(parent),input_files_before_and_after=before,parent_files_before_and_after=parent_before,
        recorded_current_source_verifications=[checks,parent_checks],current_physical_definition_regenerated_identically=True,ancestry_and_hardware=lineage,
        added_upper_mass_per_car_kg=vehicle['frame_refinement']['added_upper_mass_per_car_kg'],tool_record=tool_record(),
        native_recorded_isolation=manifest['isolation'],native_recorded_resource_limits=manifest['resource_limits'],
        results=levels,refinement=refinement,independent_saved_state_cases_checked=len(allcases),
        recorded_numerically_valid_cases=sum(c['saved_numerical_valid'] for c in allcases),recorded_linear_domain_cases=sum(not c['declared_linear_domain_suspect'] for c in allcases),
        equilibrium_and_energy_checks_passed=True,energy_and_stress_refinement_complete=False,independent_fresh_solver_validation=False,
        human_engineering_review=False,physical_test_correlation=False,approved_material_joint_HAZ_fatigue_buckling_allowables=None,
        limitations=['Current source element laws reused; assembly/action accumulation independently implemented without factorization',
            'Two meshes and successful residuals do not establish complete stress/energy convergence',
            'Stress/traction proxies are not approved combined-stress, local plate buckling, weld/HAZ, fatigue or crash margins',
            'Linear domain is the unchanged evaluator domain, not approved door/glazing/gauge/maintenance tolerances',
            'Bounded equipment/weld masses and static primitive gaps do not establish installed mass or dynamic clearance',
            'Native recorded integrity and saved-state checks do not constitute a fresh independent solve or physical approval'],**FLAGS)
    report['audit_id']=identity(report);return report


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('input_native',type=Path);parser.add_argument('--parent-native',type=Path);parser.add_argument('--root',type=Path,default=ROOT);parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
    parent=args.parent_native or args.input_native.parent/'ancestor-native'
    if not parent.is_dir():parser.error('Provide --parent-native (or sibling ancestor-native) for exact ancestry/COTS/definition checks')
    target=args.output.resolve()
    for source in (args.input_native.resolve(),parent.resolve()):
        if target==source or source in target.parents:parser.error('Audit output must be outside immutable native inputs')
    result=audit(args.input_native,parent_native=parent,root=args.root);target.parent.mkdir(parents=True,exist_ok=True)
    with target.open('xb') as out:out.write(encoded(result))
    print(json.dumps(dict(audit_id=result['audit_id'],output=str(target),source_sha256=result['source_sha256'][PRODUCER],cases=result['independent_saved_state_cases_checked'],numerically_valid=result['recorded_numerically_valid_cases'],linear_domain_cases=result['recorded_linear_domain_cases'],**FLAGS),sort_keys=True))
if __name__=='__main__':main()
