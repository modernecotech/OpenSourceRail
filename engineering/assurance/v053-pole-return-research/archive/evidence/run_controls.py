"""Exact baseline invariance and simultaneous two-force stationarity controls."""
from hashlib import sha256
from pathlib import Path
import importlib.util,json,math,sys,time
import numpy as np
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT));OUT=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('pole_research',OUT/'run.py');r=importlib.util.module_from_spec(spec);spec.loader.exec_module(r);cm=r.cm
spec=importlib.util.spec_from_file_location('pole_topology',OUT/'run_topology.py');top=importlib.util.module_from_spec(spec);spec.loader.exec_module(top)


def asymmetric(context,up,left,T=40.):
    a,v,m,*_=context;Al=m['lift_pole_area_m2'];Ag=m['guide_pole_area_m2']
    squared=cm.MU0*np.array([Al*up+Ag*left,Al*up-Ag*left])
    if min(squared)<0:return dict(target_n=[up,left],geometric_two_force_solution=False,reason='Two useful branch squared fluxes cannot be nonnegative')
    q=np.sqrt(squared);hr=cm._steel(q[None,:],m['core_paths']['stationary_return'],context)[0][0]
    rg=(.008/Al+.008/Ag)/cm.MU0;rl=m['leakage']['path_length_m']/(cm.MU0*m['leakage']['path_area_m2']);leak=(rg*q+hr)/rl;psi=q+leak
    hs=float(cm._steel(np.array([sum(psi)]),m['core_paths']['common'],context)[0][0]);hb=cm._steel(psi[None,:],m['core_paths']['branch'],context)[0][0]
    pm=m['permanent_magnet'];f=a['materials']['ferrite'];Br=f['br_20c_t']*(1+f['br_temperature_coefficient_per_k']*(T-20))
    rm=pm['length_m']/(cm.MU0*f['recoil_relative_permeability']*pm['area_m2']);fpm=Br*pm['length_m']/(cm.MU0*f['recoil_relative_permeability'])
    drive=hs+hb+rm*psi-fpm+rg*q+hr;current=[float(sum(drive)/(2*v['turns_lift'])),float((drive[0]-drive[1])/(2*v['turns_guide']))]
    flux=np.r_[q,leak]
    raw=cm.evaluate_batch([[.008]*4],[current],T,initial_flux_wb=[flux]);actual=[float(raw['upward_n'][0]),float(raw['leftward_n'][0])]
    cu=a['materials']['copper'];coils=m['coils'];r20=np.array([coils[0]['conductor_length_m']/(v['copper_lift_mm2']*1e-6),sum(c['conductor_length_m'] for c in coils[1:])/(v['copper_guide_mm2']*1e-6)])*cu['resistivity_20c_ohm_m']
    G=np.asarray(v['cooling_w_k']);i=np.asarray(current);alpha=cu['resistance_temperature_coefficient_per_k'];gain=i*i*r20*alpha
    equilibrium=[]
    for n in (0,1):equilibrium.append(None if gain[n]>=G[n] else float(a['ambient_c']+i[n]*i[n]*r20[n]*(1+alpha*(a['ambient_c']-20))/(G[n]-gain[n])))
    result=dict(target_n=[up,left],actual_force_n=actual,force_error_n=[actual[0]-up,actual[1]-left],geometric_two_force_solution=True,
        required_current_a=current,map_valid=bool(raw['valid'][0]),domain_valid=bool(raw['domain_valid'][0]),canonical_converged=bool(raw['converged'][0]),
        stationarity_residual_at=r.residual(context,raw['flux_state_wb'][0],current,T),max_core_b_t=float(raw['peak_core_b_t'][0]),minimum_demag_margin_a_m=float(raw['demag_margin_a_m'].min()),
        current_density_a_mm2=(abs(i)/[v['copper_lift_mm2'],v['copper_guide_mm2']]).tolist(),
        continuous_current_density_screen=bool(np.all(abs(i)/[v['copper_lift_mm2'],v['copper_guide_mm2']]<=a['continuous_current_density_a_mm2'])),
        constant_current_thermal_equilibrium_c=equilibrium,constant_current_thermal_screen=bool(all(t is not None and t<=a['maximum_copper_c'] for t in equilibrium)),
        thermal_scope='Conditional source cooling and constantrequiredcurrents; guidecurrent is unchanged by common PMtemperature in thisnetwork. LiftPMfeedback/core/PWMlosses are omitted, no thermalrating.',
        no_current_clamp=True)
    return result


def main():
    start=time.monotonic();before=cm.sources();drivers={Path(p).relative_to(ROOT).as_posix():cm.digest(p) for p in (__file__,r.__file__,top.__file__)};parent=cm.definition();rows=[]
    cases=[('exact-baseline-original',.1,1.,140.,20.,None),*[(f'exact-baseline-sensitive-g{int(f*100):03d}',.1,1.,140.,20.,f) for f in (0.,.5,1.)],
        ('narrow-original-w025-s2',.025,2.,140.,20.,None),('narrow-original-w0225-s22',.0225,2.2,140.,23.5,None),
        ('narrow-sensitive-g000-w0225-s22',.0225,2.2,140.,23.5,0.),('narrow-sensitive-g100-w0225-s22',.0225,2.2,140.,23.5,1.),
        ('narrow-sensitive-g100-w025-s24',.025,2.4,140.,23.5,1.)]
    for identity,width,scale,turns,copper,gf in cases:
        context=r.context_for(width,scale,turns,copper)
        if gf is not None:context=top.topology(context,gf)
        m=context[2];aw3=parent['controlled_aw3_kg']+24*(m['mass_kg']-parent['module']['mass_kg']);target=aw3*r.G/24
        with r.installed(context):
            control=cm.evaluate_batch([[.008]*4],[[120.,0.]],40.)
            points=[asymmetric(context,mult*target,lat*target) for mult,lat in ((1.,0.),(1.3,0.),(1.,.1),(1.3,.1))]
            matrix=context[2]['core_paths']
            hypothesis=dict(id=identity,width_m=width,core_scale=scale,turns_lift=turns,copper_lift_mm2=copper,
                guide_useful_fraction=gf,core_paths=matrix,module_mass_kg=m['mass_kg'],parent_configuration_sha256=parent['configuration_sha256'])
            row=dict(research_hypothesis_sha256=sha256(cm.encoded(hypothesis)).hexdigest(),hypothesis=hypothesis,aw3_kg=aw3,target_n=target,
                source_gap8mm_current120_force_n=float(control['upward_n'][0]),source_gap8mm_current120_map_valid=bool(control['valid'][0]),
                module_own_weight_n=m['mass_kg']*r.G,necessary_25mm_return_only_2_2t_force_bound_n=(2.2*.16*scale*.025*context[0]['stack_fill'])**2/(cm.MU0*m['lift_pole_area_m2']),
                simultaneous_asymmetric_stationarity_points=points,complete_system_feasible=False,configuration_adopted=False,**cm.FLAGS)
            rows.append(row);print(json.dumps(dict(id=identity,mass=m['mass_kg'],aw3=aw3,points=[dict(up=p['target_n'][0],left=p['target_n'][1],I=p.get('required_current_a'),valid=p.get('map_valid'),B=p.get('max_core_b_t'),residual=p.get('stationarity_residual_at')) for p in points])),flush=True)
    baseline=rows[0];assert math.isclose(baseline['hypothesis']['module_mass_kg'],parent['module']['mass_kg'],abs_tol=1e-8)
    assert math.isclose(baseline['source_gap8mm_current120_force_n'],3064.00098821,rel_tol=1e-9)
    baseline_invariant=all(row['necessary_25mm_return_only_2_2t_force_bound_n']<row['module_own_weight_n']<row['target_n'] for row in rows[:4])
    assert baseline_invariant
    assert before==cm.sources() and all(cm.digest(ROOT/p)==h for p,h in drivers.items())
    result=dict(schema='osr-pole-return-independent-controls/1',source_sha256={**before,**drivers},source_unchanged=True,cases=rows,baseline_failure_invariant=baseline_invariant,
        symmetric_and_asymmetric_force_targets_not_clamped=True,elapsed_s=time.monotonic()-start,configuration_adopted=False,complete_system_feasible=False,
        interpretation='Positive useful branch fluxes are algebraicallyfixed by simultaneous total lift and lateral force. Each leakage branch follows subtraction of its useful/leakage stationarity equations. Sum/difference of exactbranchMMFs gives bothrequiredcircuitcurrents, which are tested by the unchanged4flux evaluator. This avoids treating an inverse-iteration stopping point as an achieved design load; it is not an independent3D/physicalvalidation.',**cm.FLAGS)
    r.save('controls-results.json',result);r.save('controls-source-manifest.json',dict(source_sha256=result['source_sha256'],files_sha256={name:cm.digest(OUT/name) for name in ('run.py','run_topology.py','run_controls.py','controls-results.json')},**cm.FLAGS));print('FINAL '+json.dumps(dict(cases=len(rows),baseline_failure_invariant=baseline_invariant,elapsed_s=result['elapsed_s'])),flush=True)

if __name__=='__main__':main()
