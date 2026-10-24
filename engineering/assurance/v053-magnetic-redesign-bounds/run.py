"""Isolated magnetic redesign bounds; never alter/adopt production definitions."""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import json
import math
import platform
import sys
import time

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
import numpy as np
import scipy
from scipy.optimize import brentq
from engineering.ferrite_maglev import candidate_magnetics as cm

OUT=Path(__file__).resolve().parent
G=9.80665

def encoded(value):return cm.encoded(value)
def digest(path):return sha256(Path(path).read_bytes()).hexdigest()
def sources():return {**cm.sources(),Path(__file__).relative_to(ROOT).as_posix():digest(__file__)}

def context_for(variant_id,changes,rail_t):
    original=cm._runtime(variant_id)
    a=deepcopy(original[0]);v=deepcopy(original[1]);v.update(changes)
    m=cm._module(a,v)
    # Fixed gap faces; added stock extends outwards, not into the 8mm gaps.
    x=.16*v['core_scale']
    m['core_paths']['stationary_return']=[
        dict(id='scratch/flange-entry',length_m=rail_t/2,area_m2=x*.10),
        dict(id='scratch/flange-run',length_m=.258+rail_t/2,area_m2=x*rail_t),
        dict(id='scratch/web-run',length_m=.158+rail_t/2,area_m2=x*rail_t),
        dict(id='scratch/guide-exit',length_m=rail_t/2,area_m2=x*.10)]
    context=(a,v,m,*original[3:])
    return context

def required_point(context,target_n,temperature_c=40.):
    """Independent symmetric stationarity reduction of the same network.

    The useful and leakage branch equations subtract to rLeak*leak=rg*q+Hrail.
    Therefore required useful flux, leakage and current follow without inverse
    force iteration. This is an algebraic cross-check, not an independent FE map.
    """
    a,v,m,*_=context;mu=cm.MU0
    q=math.sqrt(target_n*mu*m['lift_pole_area_m2'])
    hr=float(cm._steel(np.array([[q,q]]),m['core_paths']['stationary_return'],context)[0][0,0])
    rg=(.008/m['lift_pole_area_m2']+.008/m['guide_pole_area_m2'])/mu
    rleak=m['leakage']['path_length_m']/(mu*m['leakage']['path_area_m2'])
    leak=(rg*q+hr)/rleak;psi=q+leak
    hs=float(cm._steel(np.array([2*psi]),m['core_paths']['common'],context)[0][0])
    hb=float(cm._steel(np.array([[psi,psi]]),m['core_paths']['branch'],context)[0][0,0])
    pm=m['permanent_magnet'];f=a['materials']['ferrite']
    br=f['br_20c_t']*(1+f['br_temperature_coefficient_per_k']*(temperature_c-20))
    rm=pm['length_m']/(mu*f['recoil_relative_permeability']*pm['area_m2'])
    fpm=br*pm['length_m']/(mu*f['recoil_relative_permeability'])
    current=(hs+hb+rm*psi-fpm+rg*q+hr)/v['turns_lift']
    result=cm.evaluate_batch([[.008]*4],[[current,0.]],temperature_c,
        initial_flux_wb=[[q,q,leak,leak]])
    assert result['converged'][0]
    assert math.isclose(float(result['upward_n'][0]),target_n,rel_tol=1e-9)
    return dict(required_current_a=current,branch_useful_flux_wb=q,branch_leakage_flux_wb=leak,
        useful_to_total_flux_fraction=q/psi,air_gap_mmf_at=rg*q,rail_mmf_at=hr,
        common_core_mmf_at=hs,branch_core_mmf_at=hb,pm_bias_mmf_at=fpm,
        maximum_core_b_t=float(result['peak_core_b_t'][0]),
        maximum_vehicle_core_b_t=float(result['peak_vehicle_core_b_t'][0]),
        return_rail_b_t=result['peak_return_rail_b_t'][0].tolist(),
        minimum_demag_margin_a_m=float(result['demag_margin_a_m'].min()),
        numerical_domain_valid=bool(result['domain_valid'][0]),map_valid=bool(result['valid'][0]),
        actual_force_n=float(result['upward_n'][0]),
        numerical_crosscheck='Closed symmetric stationarity vs original four-flux convex Newton evaluator; no independent spatial qualification')

def thermal(context,target):
    a,v,m,*_=context;cu=a['materials']['copper'];coil=m['coils'][0]
    r20=coil['conductor_length_m']/(v['copper_lift_mm2']*1e-6)*cu['resistivity_20c_ohm_m']
    alpha=cu['resistance_temperature_coefficient_per_k'];conductance=v['cooling_w_k'][0];ambient=a['ambient_c']
    def point(T):return required_point(context,target,T)['required_current_a']
    # I(T) is affine here: only the declared reversible Br source varies.
    i40=point(40.);i120=point(120.)
    def current(T):return i40+(i120-i40)*(T-40.)/80.
    def residual(T):return conductance*(T-ambient)-current(T)**2*r20*(1+alpha*(T-20))
    grid=np.linspace(ambient,a['maximum_copper_c'],81);equilibrium=None
    for left,right in zip(grid[:-1],grid[1:]):
        if residual(left)<=0<=residual(right):equilibrium=float(brentq(residual,left,right));break
    eqcurrent=None if equilibrium is None else current(equilibrium)
    density=None if eqcurrent is None else abs(eqcurrent)/v['copper_lift_mm2']
    hotloss=None if eqcurrent is None else eqcurrent**2*r20*(1+alpha*(equilibrium-20))
    return dict(resistance20_ohm=r20,copper_mass_lift_kg=coil['copper_mass_kg'],
        current40_a=i40,current120_a=i120,conditional_equilibrium_c=equilibrium,
        conditional_equilibrium_current_a=eqcurrent,conditional_equilibrium_copper_loss_w=hotloss,
        current_density_a_mm2=density,cooling_conductance_w_k=conductance,
        declared_continuous_density_limit_a_mm2=a['continuous_current_density_a_mm2'],
        declared_drive_peak_limit_a=a['current_limit_a'],
        continuous_screen_pass=bool(equilibrium is not None and density<=a['continuous_current_density_a_mm2'] and abs(eqcurrent)<=a['current_limit_a']),
        scope='Symmetric lift only, zero guidance current. Conditional stable DC copper/Br heat balance in40..120C; unqualified cooling retained unchanged, no repeated dynamic/guidance reserve qualification')

def rail_mass(a,t):
    # Four continuous L sections, each disjoint .308m flange +(.208+t)m web.
    steel=4*t*(.516+t)*a['materials']['steel']['density_kg_m3']*a['stack_fill']
    return steel+37.68

def record(identity,variant_id,changes,t,parent):
    context=context_for(variant_id,changes,t);a,v,m,*_=context
    runtime=cm._runtime;cm._runtime=lambda _:context
    try:
        aw3=parent['controlled_aw3_kg']+24*(m['mass_kg']-parent['module']['mass_kg'])
        target=aw3*G/24;own=m['mass_kg']*G
        grid=np.arange(-120.,120.0001,5.)
        curve=cm.evaluate_batch(np.full((len(grid),4),.008),np.column_stack([grid,np.zeros(len(grid))]),40.)
        feasible=np.flatnonzero(curve['valid']);validmax=None if not len(feasible) else int(feasible[np.argmax(curve['upward_n'][feasible])])
        point=required_point(context,target);selfpoint=required_point(context,own)
        dynamicpoint=required_point(context,1.3*target)
        thermal_result=thermal(context,target)
        continuous=thermal_result['conditional_equilibrium_c'];hotpoint=None if continuous is None else required_point(context,target,continuous)
        field_screen=bool(point['map_valid'] and hotpoint is not None and hotpoint['map_valid'])
        rho=a['materials']['steel']['density_kg_m3']*a['stack_fill'];x=.16*v['core_scale']
        area=x*t*a['stack_fill'];upper=2.2**2*area**2/(cm.MU0*m['lift_pole_area_m2'])
        bound=[]
        for b in (2.2,1.8,1.6):
            required_t=point['branch_useful_flux_wb']/(x*a['stack_fill']*b)
            dynamic_t=required_t*math.sqrt(1.3)
            bound.append(dict(return_b_ceiling_t=b,required_wall_m=required_t,
                rail_kg_m_at_wall=rail_mass(a,required_t),wall_m_for1_3load=dynamic_t,
                rail_kg_m_for1_3load=rail_mass(a,dynamic_t)))
        hypothesis=dict(id=identity,parent_configuration_sha256=parent['configuration_sha256'],base_variant=variant_id,
            changed_variant_inputs=changes,rail_wall_m=t,gap_faces_fixed=True,
            module_geometry=m,rail_geometry=dict(count_per_track=4,web_height_m=.208+t,web_width_m=t,flange_width_m=.308,flange_height_m=t))
        research_id=sha256(encoded(hypothesis)).hexdigest()
        maxsample=dict(upward_n=float(curve['upward_n'][-1]),map_valid=bool(curve['valid'][-1]),peak_core_b_t=float(curve['peak_core_b_t'][-1]))
        maxvalid=None if validmax is None else dict(current_a=float(grid[validmax]),upward_n=float(curve['upward_n'][validmax]),peak_core_b_t=float(curve['peak_core_b_t'][validmax]))
        return dict(research_hypothesis_sha256=research_id,hypothesis=hypothesis,
            controlled_aw3_kg=aw3,module_mass_kg=m['mass_kg'],module_own_weight_n=own,required_full_car_lift_n_per_module=target,
            module_mass_delta_kg=m['mass_kg']-parent['module']['mass_kg'],vehicle_mass_delta_kg=aw3-parent['controlled_aw3_kg'],
            copper_fill_fractions=[c['fill_fraction'] for c in m['coils']],coil_pack_screen=bool(max(c['fill_fraction'] for c in m['coils'])<=a['coil_fill_limit']),
            rail_linear_mass_kg_m=rail_mass(a,t),rail_mass_25m_t=25*rail_mass(a,t)/1000,
            additional_rail_kg_m=rail_mass(a,t)-rail_mass(a,.025),
            necessary_rail_upper_lift_bound_n=upper,rail_bound_proves_cannot_lift_own_module=upper<own,
            peak120a_sample=maxsample,largest_valid_lift_in5a_sweep=maxvalid,
            required_aw3_point=point,required_self_only_point=selfpoint,
            required1_3_aw3_point=dynamicpoint,
            necessary_rail_area_bounds=bound,conditional_lift_thermal=thermal_result,
            conditional_static_lift_screen_pass=bool(field_screen and thermal_result['continuous_screen_pass'] and max(c['fill_fraction'] for c in m['coils'])<=a['coil_fill_limit']),
            complete_system_feasible=False,manufacturing_accepted=False,physical_release=False,
            holds=['Only same-network symmetric static lift. No guidance authority, fault reserve, movingRL control, independent field/demag qualification, native clearance, winding insulation, connectors, cooling, structural/rail/civil or propulsion acceptance.',
                'Rail thickness extends stock outwards at fixed inner faces; interfaces, attachments, corner flux, module/cradle/body interference and civil mass response have not been redesigned.',
                'Changed module variants use actual existing parametric stock/copper mass; no mass credit for hypothetical topology simplification. Parent retained equipment, dedicated propulsion band and405.124kg protection remain counted.'])
    finally:cm._runtime=runtime

def main():
    before=sources();start=time.monotonic();d=cm.definition()
    cases=[('baseline','shared-stem-140',{},.025),('compact','compact-100',{},.025),
        ('high-bias','high-bias-180',{},.025),('light-yoke','light-yoke-160',{},.025),
        *[(f'rail-{int(t*1000):03d}','shared-stem-140',{},t) for t in (.04,.055,.065,.08)],
        ('longer-stack-125-rail55','shared-stem-140',dict(core_scale=1.25),.055),
        ('longer-stack-150-rail55','shared-stem-140',dict(core_scale=1.5),.055),
        ('pm80-rail55','shared-stem-140',dict(pm_length_m=.08),.055),
        ('copper32-rail55','shared-stem-140',dict(copper_lift_mm2=32.),.055)]
    results=[]
    for args in cases:
        r=record(*args,d);results.append(r)
        print(json.dumps(dict(id=args[0],mass_kg=r['module_mass_kg'],aw3_kg=r['controlled_aw3_kg'],required_a=r['required_aw3_point']['required_current_a'],core_b_t=r['required_aw3_point']['maximum_core_b_t'],thermal=r['conditional_lift_thermal']['conditional_equilibrium_c'],screen=r['conditional_static_lift_screen_pass'])),flush=True)
    assert before==sources()
    result=dict(schema='osr-isolated-magnetic-redesign-bounds/1',source_sha256=before,source_unchanged=True,
        parent_configuration_sha256=d['configuration_sha256'],parent_aw3_kg=d['controlled_aw3_kg'],parent_module_mass_kg=d['module']['mass_kg'],cases=results,
        environment=dict(python=platform.python_version(),numpy=np.__version__,scipy=scipy.__version__),elapsed_s=time.monotonic()-start,
        interpretation='Necessary area bounds are optimistic and independent of available MMF. Explicit changed hypotheses receive new research identities and do not rebind the parent design. Any static-screen pass is same-network/conditional only; no system/physical/manufacturing qualification.',
        production_sources_edited=False,canonical_outputs_edited=False,configuration_adopted=False,**cm.FLAGS)
    (OUT/'results.json').write_bytes(encoded(result))
    baseline=results[0]
    lines=['# Isolated magnetic redesign bounds','',
        'This ignored scratch study changes no production source, configuration or canonical packet. Every hypothesis has its own research SHA and retains the failed parent as its provenance. No hypothesis is adopted or physically accepted.','',
        f"At 8 mm and +120 A the baseline produces {baseline['peak120a_sample']['upward_n']:.1f} N versus its own {baseline['module_own_weight_n']:.1f} N weight and {baseline['required_full_car_lift_n_per_module']:.1f} N full AW3 allocation.",
        f"An optimistic 2.2 T rail-only ceiling is {baseline['necessary_rail_upper_lift_bound_n']:.1f} N: current or PM changes cannot make the current 25 mm return section lift its own module while retaining that limit.",
        '','For symmetric lift q=sqrt(F*mu0*A_pole), and rail wall t>=q/(stack_fill*x*B_limit). These are necessary, not sufficient bounds. The magnetomotive-force/thermal screens retain the actual nonlinear steel proxy, PM recoil/demag checks, coil fill, 120 A drive limit and 3.75 A/mm2 continuous limit.','',
        '| Hypothesis | Module kg | Full AW3 kg/car | Return+wear kg/m | Required A at 40 C | Equilibrium C | Static lift screen | 1.3 AW3 map valid |',
        '|---|---:|---:|---:|---:|---:|---|---|']
    for r in results:
        eq=r['conditional_lift_thermal']['conditional_equilibrium_c']
        lines.append(f"|{r['hypothesis']['id']}|{r['module_mass_kg']:.2f}|{r['controlled_aw3_kg']:.2f}|{r['rail_linear_mass_kg_m']:.2f}|{r['required_aw3_point']['required_current_a']:.2f}|{'none within40..120C' if eq is None else format(eq,'.2f')}|{r['conditional_static_lift_screen_pass']}|{r['required1_3_aw3_point']['map_valid']}|")
    lines+=['','A static pass covers symmetric lift and conditional unchanged cooling only. The 1.3 AW3 point is a separate current/BH/demag/domain check, with no reserve-guide circuit, RL/transient/fault or spatial-field qualification.','',
        'The return rail wall grows outward at fixed gap faces. The continuous steel mass is counted before brackets; new joints, clearances, rail/civil strength, foundations and erection costs remain unresolved. Larger module stock and actual copper increase vehicle mass before recalculating its lift demand.','',
        'The direct symmetric stationarity reduction is checked by the original four-flux Newton evaluator. This is an independent algebraic cross-check of the same network, not an independent FE/spatial validation. Extreme saturated points are inadmissible extrapolations explaining failure, not proposed rated operating points.','',
        'Reproduce: OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 tools/automation/osr-python build/magnetic-redesign-bounds/run.py','']
    (OUT/'README.md').write_text('\n'.join(lines))
    (OUT/'source-manifest.json').write_bytes(encoded(dict(schema='osr-isolated-redesign-receipt/1',source_sha256=before,
        source_unchanged_after_execution=True,files_sha256={name:digest(OUT/name) for name in ('run.py','results.json','README.md','execution.log')},
        command='OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 tools/automation/osr-python build/magnetic-redesign-bounds/run.py',
        configuration_adopted=False,**cm.FLAGS)))

if __name__=='__main__':main()
