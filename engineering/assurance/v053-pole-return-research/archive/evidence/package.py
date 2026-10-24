"""Create a source/driver-bound portable appendix without canonical mutations."""
from pathlib import Path
from hashlib import sha256
import gzip,json,shutil
OUT=Path(__file__).resolve().parent;ARCHIVE=OUT/'archive'


def sha(path):return sha256(Path(path).read_bytes()).hexdigest()
def read(name):return json.loads((OUT/name).read_bytes())
def dump(path,value):path.write_text(json.dumps(value,sort_keys=True,indent=2,allow_nan=False)+'\n')


def chart(summary):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    initial=read('results.json');top=read('topology-results.json');guide=read('guidance-results.json')
    fig,axs=plt.subplots(2,2,figsize=(12,8),layout='constrained')
    for scale in (1.,1.5,2.):
        rows=sorted([c for c in initial['cases'] if c['hypothesis']['core_scale']==scale and c['hypothesis']['turns_lift']==140 and c['hypothesis']['copper_lift_mm2']==20],key=lambda c:c['hypothesis']['pole_face_width_m'])
        axs[0,0].plot([c['hypothesis']['pole_face_width_m']*1000 for c in rows],[c['peak120']['force_n']/c['target_n_per_module'] for c in rows],marker='x',label=f'{scale:g}x stack; includes invalid points')
    axs[0,0].axhline(1.,color='black',ls='--',lw=1);axs[0,0].set(xlabel='Lift-pole face width /mm',ylabel='120A lift / actual AW3 demand',title='Original flux allocation; field limits still apply');axs[0,0].legend(fontsize=7)
    for sensitive,label in [(False,'Original total-branch pole flux'),(True,'Useful-only sensitivity; unqualified')]:
        rows=sorted([c for c in top['cases'] if c.get('topology_sensitivity')==sensitive and c['hypothesis']['core_scale']==2.2 and (not sensitive or c['guide_pole_useful_length_fraction']==1.)],key=lambda c:c['hypothesis']['pole_face_width_m'])
        axs[0,1].plot([c['hypothesis']['pole_face_width_m']*1000 for c in rows],[c['one_point_three_aw3_required']['max_core_b_t'] for c in rows],marker='o',label=label)
    axs[0,1].axhline(2.2,color='black',ls='--',lw=1);axs[0,1].set(xlabel='Lift-pole face width /mm',ylabel='Peak steel B at1.3AW3 /T',title='Topology sensitivity changes conclusions');axs[0,1].legend(fontsize=7)
    labels=['Parent\nfailed','Narrow pole\nsource topology','Narrow pole\nflux sensitivity','Larger guidecoil\nfailed combined screen']
    vals=[summary['parent']['aw3_kg']/1000,summary['representative_original']['controlled_aw3_kg']/1000,summary['representative_sensitivity']['controlled_aw3_kg']/1000,summary['best_fitting_guidance']['controlled_aw3_kg']/1000]
    axs[1,0].bar(range(4),vals,color=['#6a7d88','#d78a3d','#5f9ab2','#ba5a59']);axs[1,0].set_xticks(range(4),labels,fontsize=8);axs[1,0].set(ylabel='Recounted AW3 /tonnes per car',title='Moving mass is counted, with no adoption')
    for i,c in enumerate(guide['cases']):axs[1,1].scatter(i+1,c['simultaneous_points'][2]['current_density_a_mm2'][1],color='#b8594f' if not c['coil_fill_pass'] else '#46839f',marker='x' if not c['coil_fill_pass'] else 'o')
    axs[1,1].axhline(3.75,color='black',ls='--',lw=1);axs[1,1].set(xlabel='Executed guide-winding case',ylabel='Guidance copper current density /A/mm2',title='AW3 lift +0.1AW3 lateral; every combined screen fails')
    for ax in axs.flat:ax.grid(alpha=.2)
    fig.suptitle('Pole/return research: same-network numerical studies, no physical or engineering acceptance',fontsize=12)
    fig.savefig(OUT/'research-comparison.png',dpi=130);plt.close(fig)


def main():
    if ARCHIVE.exists():raise ValueError('new immutable archive required')
    initial=read('results.json');top=read('topology-results.json');controls=read('controls-results.json');guide=read('guidance-results.json')
    original=next(c for c in initial['cases'] if c['hypothesis']['id']=='w025-s2.00-n140-a20.0')
    sensitive=next(c for c in top['cases'] if c['hypothesis']['id']=='topology-g100-w22.5-s2.20')
    best=min([c for c in guide['cases'] if c['coil_fill_pass']],key=lambda c:max(c['simultaneous_points'][2]['current_density_a_mm2']))
    parent=controls['cases'][0]
    summary=dict(schema='osr-pole-return-research-summary/1',parent=dict(configuration_sha256=initial['parent_configuration_sha256'],module_mass_kg=initial['parent_module_mass_kg'],aw3_kg=initial['parent_aw3_kg'],
        force_at120a_n=parent['source_gap8mm_current120_force_n'],module_own_weight_n=parent['module_own_weight_n'],aw3_force_n=parent['target_n'],optimistic_return_2_2t_force_bound_n=parent['necessary_25mm_return_only_2_2t_force_bound_n']),
        executed=dict(original_geometry_winding_cases=len(initial['cases']),refinement_topology_cases=len(top['cases']),exact_baseline_asymmetric_controls=len(controls['cases']),guidance_winding_cases=len(guide['cases']),preliminary_driver_execution_errors_retained=1),
        baseline_failure_invariant=controls['baseline_failure_invariant'],original_cases_with_static_screen=sum(c['conditional_static_screen'] for c in initial['cases']),
        original_cases_with1_3screen=sum(c['adverse_peak_current_and_flux_screen'] for c in initial['cases']),
        topological_sensitivities_with1_3screen=sum(c.get('adverse_peak_current_and_flux_screen',False) for c in top['cases'] if c.get('topology_sensitivity')),
        fitting_guidance_cases=sum(c['hypothesis']['fit']['nominal_aabb_clear'] for c in guide['cases']),guidance_copper_fill_passes=sum(c['coil_fill_pass'] for c in guide['cases']),
        guidance_combined_screen_passes=sum(c['conditional_nominal_aw3_lateral_screen'] for c in guide['cases']),
        representative_original=dict(id=original['hypothesis']['id'],module_mass_kg=original['module_mass_kg'],controlled_aw3_kg=original['controlled_aw3_kg'],aw3_current40_a=original['aw3_required']['current_a'],
            conditional_copper_equilibrium_c=original['thermal']['equilibrium_c'],one_point_three_aw3_current40_a=original['one_point_three_aw3_required']['current_a'],one_point_three_peak_b_t=original['one_point_three_aw3_required']['max_core_b_t']),
        representative_sensitivity=dict(id=sensitive['hypothesis']['id'],module_mass_kg=sensitive['module_mass_kg'],controlled_aw3_kg=sensitive['controlled_aw3_kg'],aw3_current40_a=sensitive['aw3_required']['current_a'],
            one_point_three_aw3_current40_a=sensitive['one_point_three_aw3_required']['current_a'],one_point_three_peak_b_t=sensitive['one_point_three_aw3_required']['max_core_b_t']),
        best_fitting_guidance=dict(id=best['hypothesis']['id'],module_mass_kg=best['module_mass_kg'],controlled_aw3_kg=best['controlled_aw3_kg'],
            simultaneous_current_a=best['simultaneous_points'][2]['required_current_a'],guide_current_density_a_mm2=best['simultaneous_points'][2]['current_density_a_mm2'][1],
            no_equilibrium_within40_120c=not best['simultaneous_points'][2]['constant_current_thermal_screen'],continuous_guide_cooling_w_k=best['hypothesis']['fit']['source_guide_cooling_w_k']),
        unchanged_return_linear_mass_kg_m=initial['unchanged_return_linear_mass_kg_m'],configuration_adopted=False,complete_system_feasible=False,
        design_complete=False,physical_validation=False,manufacturing_release=False,physical_release=False,physical_output_authorised=False,engineering_accepted=False)
    dump(OUT/'summary.json',summary);chart(summary)
    text=f'''# Pole-face and25mm return-path research —24October2026

No canonical source, configuration or generated packet was changed. This is a separate, unqualified research appendix; no candidate is adopted or accepted.

The original candidate `{initial['parent_configuration_sha256']}` is still disqualified. At8mm gap/+120A its435.97kg module gives3064N, below4275N own weight and15371N full AW3 allocation. Its unchanged25mm return has an optimistic3476N ceiling at2.2T. This bound and failure remain invariant under all three alternative pole-flux allocations tested on the exact original geometry/mass.

Executed evidence contains78initial pole/stack/winding cases,118refinement/topology cases,9exactbaseline/asymmetric controls and20larger-guidewinding cases. Controls overlap designs; these are executed case records, not225unique completed designs. Every rejection and one preliminary driverTypeError are retained. All acceptance/release/adoption flags are false.

## Original flux allocation

Only four of the first78cases pass the conditional symmetric static screen. A25mm face with2x stack weighs772.26kg per module and raises AW3 to45.69t/car. It needs47.37A at40C; the conditional copper equilibrium is57.68C under the original unqualified24W/K heat path. At1.3AW3 it requires330.51A and2.711T: both120A and2.2T screens fail. Refined widths/stacks up to2.4x retain positive geometric stock; none passes the1.3 screen under the original allocation. More turns can reduce current but cannot remove the recorded excessive field.

## Topology sensitivity — not a corrected3D model

The real declared leakage clearance is from the fork edge toward the inner guidancepole; it bypasses the separate liftpole. The original network nevertheless assigns total branch flux `psi=q+leakage` to its liftpole path. The sensitivity moves the complete liftpole and0/50/100percent of the guidancepole path length into useful-only `q` reluctance. All stock/mass stays counted. Positive B-H energy terms, their gradients/Hessians and the original coil incidence/linkage remain consistent. Exact guidepole merging, leakage-only lengths, cross-field/fringing and3D behaviour remain unresolved.

This sensitivity changes narrow-pole conclusions. A22.5mm face/2.2x stack/23.5mm2 liftcopper example weighs846.14kg and raises AW3 to47.46t/car; it requires9.97A for symmetric AW3 and85.94A/2.105T for1.3AW3 at40C. The same geometry under the original allocation fails1.3. The numerical sensitivity is not a physical correction or accepted solution. Multiple initial flux states converge, and finite-difference linkage/coenergy checks agree with the same network. They are not independent spatial/physical validation.

## Guidance and physical winding envelopes

The same representative sensitivity fails the simultaneous1.0AW3 lift+0.1AW3 lateral research case: guidance needs about102.8A and exceeds2.2T. Different turns alone cannot remove the winding ampere-turn/current-density requirement.

Twenty new guidewinding cases count actual copper, squarewire enamel, flooded pack fluid,1mm bobbins and, where needed, cover/coldplate extensions plus relocated connectors. The existing globalfluid allocation is retained without credit. All20have nominal box clearance;16meet the unchanged55percent copper-fill limit and4overfill controls are retained. Additional mass feeds all24modules into AW3 before solving simultaneous forces. No demands or current/temperature/field limits were reduced.

Zero cases pass the combined1.0AW3+0.1AW3 lateral current-density/thermal screen. The best fitting/fill case by peak circuit currentdensity weighs961.93kg/module and gives50.24t/car AW3. Its200turn/13.4mm2 guide winding requires62.79A:4.686A/mm2 exceeds3.75A/mm2. With the retained18W/K guide cooling there is no equilibrium within40–120C. Algebraic temperatures above120C and enormous out-of-domain currents are failure indicators, not physical operating predictions or ratings. Individual-turn routing/bend radius, tolerances, pressure/cooling manifolds, RL/busvoltage, protection, native clearance, manufacturing and physical qualification remain open.

Reducing face width is worth studying, but this bounded work establishes neither a lighter self-consistent complete system nor a feasible train. Stationary return steel remains{initial['unchanged_return_linear_mass_kg_m']:.3f}kg/m, with no civil support/strength/cost acceptance. The larger moving mass, unqualified topology and guidance failures prevent adoption.

## Verify and replay

`python verify.py` checks every archived byte, compressed raw receipt and original source binding without the current repository. `python verify.py --replay` reconstructs the original tree in a temporary directory and runs all four successful drivers using only archived inputs. NumPy and SciPy are required; recorded versions are in the raw results. Each driver is bounded to300seconds by the verifier. Replay compares all raw results exactly apart from elapsed wall time. No network or canonical paths are used.

`summary.json` and `research-comparison.png` present the raw executed cases. All sources, successful/failed drivers, logs and complete results are retained under `inputs/` and `evidence/`; `manifest.json` gives checksums. Hash consistency and replay provide research reproducibility, not authenticated engineering acceptance.
'''
    (OUT/'README.md').write_text(text)
    ARCHIVE.mkdir();(ARCHIVE/'evidence').mkdir();shutil.copytree(OUT/'inputs',ARCHIVE/'inputs')
    raw={}
    for name in ('results.json','topology-results.json','controls-results.json','guidance-results.json'):
        target=ARCHIVE/'evidence'/(name+'.gz');target.write_bytes(gzip.compress((OUT/name).read_bytes(),mtime=0));raw[name]=dict(path=target.relative_to(ARCHIVE).as_posix(),raw_sha256=sha(OUT/name),raw_bytes=(OUT/name).stat().st_size)
    evidence=['run.py','run_topology.py','run_controls.py','run_guidance.py','run_guidance-failed.py','execution.log','topology-execution.log','controls-execution.log','guidance-execution.log','guidance-failed-execution.log',
        'source-manifest.json','topology-source-manifest.json','controls-source-manifest.json','guidance-source-manifest.json','package.py']
    for name in evidence:shutil.copy2(OUT/name,ARCHIVE/'evidence'/name)
    for name in ('summary.json','research-comparison.png','README.md','verify.py'):shutil.copy2(OUT/name,ARCHIVE/name)
    files={p.relative_to(ARCHIVE).as_posix():sha(p) for p in sorted(ARCHIVE.rglob('*')) if p.is_file()}
    manifest=dict(schema='osr-portable-pole-return-research/1',files_sha256=files,raw_records=raw,canonical_sources_edited=False,source_binding='Eight original model/config/data/test files and exact executed driver bytes',**{k:False for k in ('design_complete','physical_validation','manufacturing_release','physical_release','physical_output_authorised','engineering_accepted','configuration_adopted','complete_system_feasible')})
    dump(ARCHIVE/'manifest.json',manifest)
    print(json.dumps(dict(files=len(files),bytes=sum(p.stat().st_size for p in ARCHIVE.rglob('*') if p.is_file()),manifest_sha256=sha(ARCHIVE/'manifest.json'))))

if __name__=='__main__':main()
