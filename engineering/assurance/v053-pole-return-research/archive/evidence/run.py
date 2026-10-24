"""Isolated pole-face/return-path research, no canonical edits or adoption."""
from contextlib import contextmanager
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import itertools,json,math,platform,sys,time
import numpy as np
import scipy
from scipy.optimize import brentq
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from engineering.ferrite_maglev import candidate_magnetics as cm
OUT=Path(__file__).resolve().parent;G=9.80665;START=time.monotonic()


def save(name,value):
    path=OUT/name
    if path.exists():raise ValueError('retain prior research bytes: '+str(path))
    path.write_bytes(cm.encoded(value))


def context_for(width,scale=1.,turns=140.,copper=20.):
    original=cm._runtime('shared-stem-140');a=deepcopy(original[0]);v=deepcopy(original[1]);v.update(core_scale=scale,turns_lift=turns,copper_lift_mm2=copper)
    m=cm._module(a,v);x=.16*scale;rho=a['materials']['steel']['density_kg_m3']*a['stack_fill'];new=[]
    for p in m['parts']:
        if p['id'].startswith('core/lift-pole-'):
            side=int(p['id'].rsplit('-',1)[-1]) if not p['id'].endswith('--1') else -1
            size=list(p['size_m']);at=list(p['at_m']);size[1]=width;at[1]=side*.15-width/2
            p=cm._box(p['id'],size,at,p['material'],rho,p['component_scope'],lamination_plane='yz',stack_axis='x')
        new.append(p)
    m['parts']=new;m['mass_kg']=sum(p['mass_kg'] for p in new);m['lift_pole_area_m2']=x*width
    for p in m['core_paths']['branch']:
        if p['id']=='core/lift-pole':p['area_m2']=x*width
    for p in m['core_paths']['stationary_return']:
        if p['id']=='stationary/flange-entry':p['area_m2']=x*width
    assert all(p['volume_m3']>0 and p['mass_kg']>0 for p in m['parts'])
    assert all(min(p['size_m'])>0 for p in m['parts'])
    m['stationary_return_rail']['lift_face_width_m']=width
    return (a,v,m,*original[3:])


@contextmanager
def installed(context):
    old=cm._runtime;cm._runtime=lambda _:context
    try:yield
    finally:cm._runtime=old


def required(context,target,temperature=40.):
    a,v,m,*_=context;mu=cm.MU0;q=math.sqrt(target*mu*m['lift_pole_area_m2'])
    hr=float(cm._steel(np.array([[q,q]]),m['core_paths']['stationary_return'],context)[0][0,0])
    rg=(.008/m['lift_pole_area_m2']+.008/m['guide_pole_area_m2'])/mu
    rleak=m['leakage']['path_length_m']/(mu*m['leakage']['path_area_m2']);leak=(rg*q+hr)/rleak;psi=q+leak
    hs=float(cm._steel(np.array([2*psi]),m['core_paths']['common'],context)[0][0]);hb=float(cm._steel(np.array([[psi,psi]]),m['core_paths']['branch'],context)[0][0,0])
    pm=m['permanent_magnet'];f=a['materials']['ferrite'];br=f['br_20c_t']*(1+f['br_temperature_coefficient_per_k']*(temperature-20))
    rm=pm['length_m']/(mu*f['recoil_relative_permeability']*pm['area_m2']);fpm=br*pm['length_m']/(mu*f['recoil_relative_permeability'])
    current=(hs+hb+rm*psi-fpm+rg*q+hr)/v['turns_lift']
    return dict(current_a=current,q_wb=q,leakage_wb=leak,flux=[q,q,leak,leak],useful_fraction=q/psi,
        mmf_at=dict(gaps=rg*q,stationary_rail=hr,shared_core=hs,branch_core=hb,pm_recoil=rm*psi,pm_bias=fpm))


def residual(context,flux,current,temperature=40.):
    a,v,m,*_=context;q=np.asarray(flux);psi=np.array([q[0]+q[2],q[1]+q[3]])
    hs=float(cm._steel(np.array([sum(psi)]),m['core_paths']['common'],context)[0][0]);hb=cm._steel(psi[None,:],m['core_paths']['branch'],context)[0][0]
    hr=cm._steel(q[None,:2],m['core_paths']['stationary_return'],context)[0][0]
    pm=m['permanent_magnet'];f=a['materials']['ferrite'];br=f['br_20c_t']*(1+f['br_temperature_coefficient_per_k']*(temperature-20))
    rm=pm['length_m']/(cm.MU0*f['recoil_relative_permeability']*pm['area_m2']);fpm=br*pm['length_m']/(cm.MU0*f['recoil_relative_permeability'])
    C=np.array([[v['turns_lift']]*4,[v['turns_guide'],-v['turns_guide'],v['turns_guide'],-v['turns_guide']]])
    grad=hs+np.tile(hb+rm*psi-fpm,2)-np.asarray(current)@C
    rg=(.008/m['lift_pole_area_m2']+.008/m['guide_pole_area_m2'])/cm.MU0
    grad[:2]+=rg*q[:2]+hr;grad[2:]+=m['leakage']['path_length_m']/(cm.MU0*m['leakage']['path_area_m2'])*q[2:]
    return float(max(abs(grad)))


def point(context,target,temperature=40.,*,cold_check=False):
    ideal=required(context,target,temperature)
    r=cm.evaluate_batch([[.008]*4],[[ideal['current_a'],0.]],temperature,initial_flux_wb=[ideal['flux']])
    result=dict(**ideal,actual_force_n=float(r['upward_n'][0]),relative_force_error=float(abs(r['upward_n'][0]/target-1)),
        canonical_converged=bool(r['converged'][0]),map_valid=bool(r['valid'][0]),domain_valid=bool(r['domain_valid'][0]),
        stationarity_residual_at=residual(context,r['flux_state_wb'][0],[ideal['current_a'],0.],temperature),
        max_core_b_t=float(r['peak_core_b_t'][0]),max_vehicle_core_b_t=float(r['peak_vehicle_core_b_t'][0]),
        return_rail_b_t=r['peak_return_rail_b_t'][0].tolist(),minimum_demag_margin_a_m=float(r['demag_margin_a_m'].min()),
        incremental_inductance_h=r['incremental_inductance_h'][0].tolist(),linkage_wb=r['flux_linkage_wb'][0].tolist())
    if cold_check:
        starts=[]
        for name,initial in [('canonical-default',None),('zero',[0.]*4),('half-analytic',[.5*v for v in ideal['flux']]),('one-and-half-analytic',[1.5*v for v in ideal['flux']])]:
            raw=cm.evaluate_batch([[.008]*4],[[ideal['current_a'],0.]],temperature,initial_flux_wb=None if initial is None else [initial])
            starts.append(dict(start=name,converged=bool(raw['converged'][0]),map_valid=bool(raw['valid'][0]),force_n=float(raw['upward_n'][0]),
                stationarity_residual_at=residual(context,raw['flux_state_wb'][0],[ideal['current_a'],0.],temperature),
                flux_max_difference_wb=float(max(abs(raw['flux_state_wb'][0]-np.asarray(ideal['flux']))))))
        result['independent_initializations']=starts
        result['all_starts_converged_to_same_point']=all(s['converged'] and s['stationarity_residual_at']<1e-3 and s['flux_max_difference_wb']<1e-8 for s in starts)
    return result


def thermal(context,target,uniform_hot=False):
    a,v,m,*_=context;coil=m['coils'][0];cu=a['materials']['copper'];r20=coil['conductor_length_m']/(v['copper_lift_mm2']*1e-6)*cu['resistivity_20c_ohm_m'];ambient=a['ambient_c'];conductance=v['cooling_w_k'][0]
    def current(T):return required(context,target,T if uniform_hot else (T+ambient)/2)['current_a']
    def heat_balance(T):return conductance*(T-ambient)-current(T)**2*r20*(1+cu['resistance_temperature_coefficient_per_k']*(T-20))
    grid=np.linspace(ambient,a['maximum_copper_c'],161);roots=[]
    for lo,hi in zip(grid[:-1],grid[1:]):
        if heat_balance(lo)<=0<=heat_balance(hi):roots.append(float(brentq(heat_balance,lo,hi)));break
    T=None if not roots else roots[0];I=None if T is None else current(T)
    r=None if T is None else cm.evaluate_batch([[.008]*4],[[I,0.]],[[T,T] if uniform_hot else [T,ambient]])
    density=None if I is None else abs(I)/v['copper_lift_mm2']
    eq_stable=None if T is None else (heat_balance(T+1e-3)-heat_balance(T-1e-3))/(2e-3)>0
    return dict(temperature_assumption='Uniform hot copper/core proxy' if uniform_hot else 'Canonical two-coil temperature mean with inactive guidecoil at40C',
        equilibrium_c=T,equilibrium_current_a=I,current_density_a_mm2=density,stable_conditional_equilibrium=eq_stable,
        resistance20_ohm=r20,source_lift_cooling_w_k=conductance,source_maximum_copper_c=a['maximum_copper_c'],
        source_continuous_density_limit=a['continuous_current_density_a_mm2'],source_peak_current_limit_a=a['current_limit_a'],
        map_valid_at_equilibrium=False if r is None else bool(r['valid'][0]),
        map_converged_at_equilibrium=False if r is None else bool(r['converged'][0]),
        equilibrium_lift_force_n=None if r is None else float(r['upward_n'][0]),
        static_continuous_symmetric_screen=bool(T is not None and eq_stable and abs(I)<=a['current_limit_a'] and density<=a['continuous_current_density_a_mm2'] and r['valid'][0]),
        scope='Conditional steady DC copper/Br heat balance; same unqualified24W/K heat path, no core/PWM/guide/dynamic duty qualification')


def record(identity,width,scale,turns,copper,parent):
    context=context_for(width,scale,turns,copper);a,v,m,*_=context
    aw3=parent['controlled_aw3_kg']+24*(m['mass_kg']-parent['module']['mass_kg']);target=aw3*G/24
    with installed(context):
        static=point(context,target);adverse=point(context,1.3*target)
        temps=thermal(context,target);uniform=thermal(context,target,True)
        i=np.linspace(-120.,120.,49);sweep=cm.evaluate_batch(np.full((len(i),4),.008),np.column_stack([i,np.zeros(len(i))]),40.)
        valid=np.flatnonzero(sweep['valid']);best=None if not len(valid) else int(valid[np.argmax(sweep['upward_n'][valid])])
        area=x=.16*scale;area=x*.025*a['stack_fill'];pole_eff=x*width*a['stack_fill'];qbound=2.2*min(area,pole_eff)
        hypothesis=dict(id=identity,pole_face_width_m=width,core_scale=scale,turns_lift=turns,copper_lift_mm2=copper,return_wall_m=.025,
            gap_faces_fixed=True,stationary_section_changed=False,module_geometry=m,source_variant='shared-stem-140')
        result=dict(hypothesis=hypothesis,research_hypothesis_sha256=sha256(cm.encoded(hypothesis)).hexdigest(),
            module_mass_kg=m['mass_kg'],module_mass_delta_kg=m['mass_kg']-parent['module']['mass_kg'],controlled_aw3_kg=aw3,target_n_per_module=target,
            parent_retained_equipment_and_propulsion_unchanged=True,necessary_2_2t_pole_and_return_force_bound_n=qbound*qbound/(cm.MU0*m['lift_pole_area_m2']),
            coil_fill_fractions=[float(c['fill_fraction']) for c in m['coils']],coil_fill_pass=max(c['fill_fraction'] for c in m['coils'])<=a['coil_fill_limit'],
            aw3_required=static,one_point_three_aw3_required=adverse,thermal=temps,uniform_hot_thermal=uniform,
            peak120=dict(force_n=float(sweep['upward_n'][-1]),converged=bool(sweep['converged'][-1]),valid=bool(sweep['valid'][-1]),peak_b_t=float(sweep['peak_core_b_t'][-1])),
            current_sweep=dict(current_a=i.tolist(),force_n=sweep['upward_n'].tolist(),converged=sweep['converged'].tolist(),map_valid=sweep['valid'].tolist(),peak_b_t=sweep['peak_core_b_t'].tolist()),
            largest_valid_5a_sample=None if best is None else dict(current_a=float(i[best]),force_n=float(sweep['upward_n'][best])),
            conditional_static_screen=bool(temps['static_continuous_symmetric_screen'] and max(c['fill_fraction'] for c in m['coils'])<=a['coil_fill_limit']),
            adverse_peak_current_and_flux_screen=bool(adverse['map_valid'] and abs(adverse['current_a'])<=120.),
            complete_system_feasible=False,configuration_adopted=False,**cm.FLAGS)
    return result,context


def followup(row,context):
    target=row['target_n_per_module'];a,v,m,*_=context;T=row['thermal']['equilibrium_c']
    report=dict(id=row['hypothesis']['id'],aw3_multiple_starts=None,one_point_three_multiple_starts=None,guidance=[],linkage_checks=[])
    with installed(context):
        report['aw3_multiple_starts']=point(context,target,cold_check=True)
        report['one_point_three_multiple_starts']=point(context,1.3*target,cold_check=True)
        sym=required(context,target);base=cm.evaluate_batch([[.008]*4],[[sym['current_a'],0]],40.,initial_flux_wb=[sym['flux']]);eps=.01
        for k in (0,1):
            di=np.zeros((1,2));di[0,k]=eps;curr=np.array([[sym['current_a'],0.]])
            p=cm.evaluate_batch([[.008]*4],curr+di,40.,initial_flux_wb=base['flux_state_wb']);n=cm.evaluate_batch([[.008]*4],curr-di,40.,initial_flux_wb=base['flux_state_wb'])
            numeric=(p['flux_linkage_wb'][0]-n['flux_linkage_wb'][0])/(2*eps);analytic=base['incremental_inductance_h'][0,:,k]
            report['linkage_checks'].append(dict(axis=k,analytic_h=analytic.tolist(),numeric_h=numeric.tolist(),agreement=bool(np.allclose(numeric,analytic,rtol=3e-4,atol=1e-8)),both_sides_converged=bool(p['converged'][0] and n['converged'][0])))
        report['incremental_inductance_symmetric']=bool(np.allclose(base['incremental_inductance_h'][0],base['incremental_inductance_h'][0].T,atol=1e-10))
        report['incremental_inductance_eigenvalues_h']=np.linalg.eigvalsh(base['incremental_inductance_h'][0]).tolist()
        report['geometric_lateral_force_upper_bound_at_fixed_up_n']=target*m['lift_pole_area_m2']/m['guide_pole_area_m2']
        for mult,lat,gaps in [(1.,.1,[.008]*4),(1.3,.1,[.008]*4),(1.,0.,[.008,.008,.007,.009])]:
            solved=cm.inverse_current([mult*target],[lat*target],[gaps],40.,initial_a=[[required(context,mult*target)['current_a'],0.]],initial_flux_wb=[required(context,mult*target)['flux']])
            raw=cm.evaluate_batch([gaps],solved['current_a'],40.,initial_flux_wb=solved['flux_state_wb'])
            densities=abs(solved['current_a'][0])/[v['copper_lift_mm2'],v['copper_guide_mm2']]
            report['guidance'].append(dict(upward_multiple=mult,lateral_multiple=lat,gaps_m=gaps,target_force_n=[mult*target,lat*target],
                current_a=solved['current_a'][0].tolist(),inverse_converged=bool(solved['converged'][0]),map_valid=bool(raw['valid'][0]),force_residual_n=solved['force_residual_n'][0].tolist(),
                current_density_a_mm2=densities.tolist(),continuous_density_screen=bool(np.max(densities)<=a['continuous_current_density_a_mm2']),
                max_core_b_t=float(raw['peak_core_b_t'][0]),minimum_demag_margin_a_m=float(raw['demag_margin_a_m'].min())))
        # Same-network finite-gap coenergy force controls, no spatial validation.
        gap_checks=[];delta=1e-7;curr=[[sym['current_a'],0.]]
        for k in (0,2):
            gp=np.full((1,4),.008);gn=gp.copy();gp[0,k]+=delta;gn[0,k]-=delta
            p=cm.evaluate_batch(gp,curr,40.,initial_flux_wb=base['flux_state_wb']);n=cm.evaluate_batch(gn,curr,40.,initial_flux_wb=base['flux_state_wb'])
            derivative=-(p['coenergy_j'][0]-n['coenergy_j'][0])/(2*delta)
            expected=base['branch_lift_force_n'][0,0] if k==0 else base['branch_guidance_force_n'][0,0]
            gap_checks.append(dict(gap_index=k,numerical_force_n=float(derivative),maxwell_force_n=float(expected),relative_error=float(abs(derivative/expected-1)),both_sides_converged=bool(p['converged'][0] and n['converged'][0])))
        report['gap_coenergy_checks']=gap_checks
        if T is not None:
            report['one_point_three_at_hot_mean']=point(context,1.3*target,(T+40)/2)
            report['one_point_three_at_uniform_hot']=point(context,1.3*target,T)
    return report


def main():
    canonical=cm.sources();own=cm.digest(__file__);snapshot={**canonical,Path(__file__).relative_to(ROOT).as_posix():own}
    for name,h in canonical.items():
        path=OUT/'inputs'/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes((ROOT/name).read_bytes());path.chmod(0o444)
        assert cm.digest(path)==h
    parent=cm.definition();cases=[];contexts={}
    recipes=[(f'w{round(w*1000):03d}-s{s:.2f}-n140-a{area:.1f}',w,s,140.,area) for s,w,area in itertools.product((1.,1.25,1.5,1.75,2.),(.02,.025,.03,.04,.05,.075,.1),(20.,23.5))]
    recipes += [(f'w025-s{s:.2f}-n{int(turn)}-a{area:.1f}',.025,s,turn,area) for s in (1.25,1.5,1.75,2.) for turn,area in ((100.,32.5),(180.,18.3))]
    for args in recipes:
        if time.monotonic()-START>1200:break
        try:
            row,context=record(*args,parent);cases.append(row);contexts[args[0]]=context
            print(json.dumps(dict(id=args[0],mass=row['module_mass_kg'],aw3=row['controlled_aw3_kg'],I=row['aw3_required']['current_a'],I1_3=row['one_point_three_aw3_required']['current_a'],B=row['aw3_required']['max_core_b_t'],static=row['conditional_static_screen'],dynamic=row['adverse_peak_current_and_flux_screen'])),flush=True)
        except Exception as e:
            cases.append(dict(hypothesis=dict(id=args[0],pole_face_width_m=args[1],core_scale=args[2],turns_lift=args[3],copper_lift_mm2=args[4]),execution_error=repr(e),conditional_static_screen=False,complete_system_feasible=False,configuration_adopted=False,**cm.FLAGS));print(json.dumps(dict(id=args[0],error=repr(e))),flush=True)
    promising=[c for c in cases if c.get('conditional_static_screen')]
    promising.sort(key=lambda c:(not c['adverse_peak_current_and_flux_screen'],c['controlled_aw3_kg'],c['one_point_three_aw3_required']['current_a']))
    followups=[]
    for row in promising[:4]:
        try:followups.append(followup(row,contexts[row['hypothesis']['id']]))
        except Exception as e:followups.append(dict(id=row['hypothesis']['id'],execution_error=repr(e)))
    assert canonical==cm.sources() and own==cm.digest(__file__)
    result=dict(schema='osr-pole-return-isolated-research/1',parent_configuration_sha256=parent['configuration_sha256'],parent_module_mass_kg=parent['module']['mass_kg'],
        parent_aw3_kg=parent['controlled_aw3_kg'],source_sha256=snapshot,source_unchanged=True,planned_cases=len(recipes),executed_cases=len(cases),cases=cases,followups=followups,
        elapsed_s=time.monotonic()-START,environment=dict(python=platform.python_version(),numpy=np.__version__,scipy=scipy.__version__),
        unchanged_return_linear_mass_kg_m=cm.guideway_definition(1.)['mass_kg'],configuration_adopted=False,canonical_outputs_edited=False,complete_system_feasible=False,
        limitations=['Exact existing convex four-flux evaluator with isolated physically recounted pole/stack/coil hypotheses only; no3D field, native clearance or measured validation.',
            'Laminated25mmreturn path remains unchanged; wider stack uses a larger patch of existing continuous rail, with longitudinal leakage/coupling unverified.',
            'Only actual lift-pole blocks and consistent liftgap/lift-pole/flange-entry areas narrow; guidanceface/leakage/PM/core paths stay fully counted.',
            'Narrow poles change lift/guidance force ratio, saturation locality, flux spreading, corner/fringe and mechanical loads; no inherited map/control/RL or system feasibility adoption.',
            '1.3AW3 and0.1AW3lateral are explicit research sensitivities, not adopted railway combinations; peak120A and continuous3.75A/mm2 are separate screens.',
            'Cooling remains unqualified24W/K; this study has no actualchannels, PWM/core losses, fault reserve, connectors, attachment, civil or manufacturing acceptance.'],**cm.FLAGS)
    save('results.json',result)
    save('source-manifest.json',dict(source_sha256=snapshot,source_unchanged=True,parent_configuration_sha256=parent['configuration_sha256'],files_sha256={'run.py':cm.digest(__file__),'results.json':cm.digest(OUT/'results.json')},**cm.FLAGS))
    print('FINAL '+json.dumps(dict(executed=len(cases),errors=sum('execution_error'in c for c in cases),static=len(promising),dynamic=sum(c.get('adverse_peak_current_and_flux_screen',False) for c in cases),followups=len(followups),elapsed_s=result['elapsed_s'])),flush=True)

if __name__=='__main__':main()
