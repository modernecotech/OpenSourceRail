"""Separately identified flux-allocation sensitivities; not corrected3D models."""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import importlib.util,itertools,json,math,sys,time
import numpy as np
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT));OUT=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('pole_research',OUT/'run.py');r=importlib.util.module_from_spec(spec);spec.loader.exec_module(r);cm=r.cm


def topology(context,guide_useful_fraction):
    a,v,m,*tail=deepcopy(context);branch=[];moved=[]
    for path in m['core_paths']['branch']:
        if path['id']=='core/lift-pole':moved.append(dict(path,id='useful-only/lift-pole'))
        elif path['id']=='core/guide-pole':
            if guide_useful_fraction<1:branch.append(dict(path,length_m=path['length_m']*(1-guide_useful_fraction)))
            if guide_useful_fraction>0:moved.append(dict(path,id='useful-only/guide-pole',length_m=path['length_m']*guide_useful_fraction))
        else:branch.append(path)
    m['core_paths']['branch']=branch;m['core_paths']['stationary_return']+=moved
    m['flux_allocation_sensitivity']=dict(lift_pole_flux='useful q only',guide_pole_useful_length_fraction=guide_useful_fraction,
        guide_pole_remaining_flux='total branch psi=q+leak',material_geometry_and_mass_unchanged=True,
        physical_interpretation='Bounded allocation sensitivity only: observed fork-to-guide leak bypasses liftpole; exact guidepole merging/leak-only portions need3D solution')
    return (a,v,m,*tail)


def physical_peaks(context,target):
    p=r.required(context,target);q=p['q_wb'];psi=q+p['leakage_wb'];m=context[2]
    def peak(phi,paths):return 0. if not paths else float(cm._steel(np.array([[phi,phi]]),paths,context)[3].max())
    return dict(stationary_return_steel_b_t=peak(q,[p for p in m['core_paths']['stationary_return'] if p['id'].startswith('stationary/')]),
        useful_only_vehicle_poles_b_t=peak(q,[p for p in m['core_paths']['stationary_return'] if p['id'].startswith('useful-only/')]),
        total_branch_vehicle_core_b_t=peak(psi,m['core_paths']['branch']),
        shared_stem_b_t=float(cm._steel(np.array([2*psi]),m['core_paths']['common'],context)[3].max()),
        note='Canonical peak_return_rail_b_t includes the whole useful-only reluctance group in this sensitivity; these separately recovered physical categories avoid mislabelling moved vehicle poles as rail.')


def main():
    start=time.monotonic();before=cm.sources();driver={Path(__file__).relative_to(ROOT).as_posix():cm.digest(__file__),r.Path(r.__file__).relative_to(ROOT).as_posix():cm.digest(r.__file__)};parent=cm.definition()
    plans=[(f'topology-g{int(gf*100):03d}-w{w*1000:04.1f}-s{s:.2f}',w,s,gf) for s,w,gf in itertools.product((1.,1.25,1.5,1.75,2.,2.2,2.4),(.020,.0225,.025,.0275,.030),(0.,.5,1.))]
    plans += [(f'topology-baseline-g{int(gf*100):03d}',.1,1.,gf) for gf in (0.,.5,1.)]
    plans += [(f'original-topology-w{w*1000:04.1f}-s{s:.2f}',w,s,None) for s,w in itertools.product((2.2,2.4),(.02,.0225,.025,.0275,.03))]
    rows=[];contexts={};factory=r.context_for
    for identity,width,scale,gf in plans:
        context=factory(width,scale,140.,23.5)
        if gf is not None:context=topology(context,gf)
        r.context_for=lambda *_:context
        try:
            row,_=r.record(identity,width,scale,140.,23.5,parent)
            row['topology_sensitivity']=gf is not None;row['geometry_and_mass_only_changes_from_original_context']=False if gf is not None else True
            row['guide_pole_useful_length_fraction']=gf
            row['actual_physical_peaks_aw3']=physical_peaks(context,row['target_n_per_module'])
            row['actual_physical_peaks_one_point_three']=physical_peaks(context,1.3*row['target_n_per_module'])
            rows.append(row);contexts[identity]=context
            print(json.dumps(dict(id=identity,mass=row['module_mass_kg'],aw3=row['controlled_aw3_kg'],I=row['aw3_required']['current_a'],I1_3=row['one_point_three_aw3_required']['current_a'],B=row['aw3_required']['max_core_b_t'],B1_3=row['one_point_three_aw3_required']['max_core_b_t'],static=row['conditional_static_screen'],dynamic=row['adverse_peak_current_and_flux_screen'])),flush=True)
        except Exception as e:
            rows.append(dict(hypothesis=dict(id=identity,pole_face_width_m=width,core_scale=scale),topology_sensitivity=gf is not None,guide_pole_useful_length_fraction=gf,execution_error=repr(e),conditional_static_screen=False,**cm.FLAGS));print(json.dumps(dict(id=identity,error=repr(e))),flush=True)
        finally:r.context_for=factory
        if time.monotonic()-start>1200:break
    positives=sorted([row for row in rows if row.get('conditional_static_screen')],key=lambda row:(not row['adverse_peak_current_and_flux_screen'],row['controlled_aw3_kg'],row['one_point_three_aw3_required']['current_a']))
    follow=[]
    # Include lightest topology-sensitive joint pass and the lightest actual
    # unchanged-flux-topology pass, keeping model dependence visible.
    chosen=positives[:3]
    originals=[row for row in positives if not row['topology_sensitivity']]
    if originals and originals[0] not in chosen:chosen.append(originals[0])
    for row in chosen:
        try:follow.append(r.followup(row,contexts[row['hypothesis']['id']]))
        except Exception as e:follow.append(dict(id=row['hypothesis']['id'],execution_error=repr(e)))
    assert before==cm.sources() and all(cm.digest(ROOT/p)==h for p,h in driver.items())
    result=dict(schema='osr-pole-return-topology-sensitivity/1',source_sha256={**before,**driver},source_unchanged=True,
        parent_configuration_sha256=parent['configuration_sha256'],planned_cases=len(plans),executed_cases=len(rows),cases=rows,followups=follow,
        elapsed_s=time.monotonic()-start,configuration_adopted=False,complete_system_feasible=False,
        energy_linkage_hessian_consistency='The exact canonical convex evaluator remains unchanged. Moved positive B-H path integrals enter the existing useful-flux energy ur(q), gradient Hr(q), and Hessian dHr/dq. Remaining paths enter ub(psi). The same coil incidence C, linkage=Cq and C H^-1 C^T are retained. No fitted force gain or current clamp is introduced.',
        topology_caveat='Actual side air leakage is from the fork edge toward the inner guidancepole, bypassing the physically separate liftpole. Canonical all-branch iron paths all carry psi=q+leak, including liftpole. This sensitivity relocates all liftpole and0/50/100percent of guidepole path length to useful-only q; it does not assert this is a correct flux map. Exact guidepole merging/leak-only lengths, cross-field/fringing and3D fields remain unknown.',
        scope='Research comparisons only; PM/steel proxies, cooling, nativegeometry, guidanceauthority, dynamicreserve, propulsion, manufacturing/civil/physical acceptance remain open',**cm.FLAGS)
    r.save('topology-results.json',result);r.save('topology-source-manifest.json',dict(source_sha256=result['source_sha256'],files_sha256={'run_topology.py':cm.digest(__file__),'run.py':cm.digest(r.__file__),'topology-results.json':cm.digest(OUT/'topology-results.json')},**cm.FLAGS))
    print('FINAL '+json.dumps(dict(executed=len(rows),errors=sum('execution_error'in row for row in rows),static=len(positives),dynamic=sum(row.get('adverse_peak_current_and_flux_screen',False) for row in rows),followups=len(follow),elapsed_s=result['elapsed_s'])),flush=True)

if __name__=='__main__':main()
