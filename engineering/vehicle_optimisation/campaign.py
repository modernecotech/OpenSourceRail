"""Compose sourced magnetic and lightweight alternatives without accepting a train.

Numerical worker outputs retain their own exact field geometry/source identity.
Changing a vehicle mass scenario reuses that field primitive and re-executes the
load comparison, rather than claiming another field solve or another magnet.
"""
from __future__ import annotations
import argparse
from copy import deepcopy
from hashlib import sha256
import json
import math
from pathlib import Path
import tempfile

from engineering.design_search.contracts import (
    FLAGS, PHYSICAL_KEYS, encoded, identity, make_candidate, make_evaluation_request,
    make_result, validate_candidate,
)
from engineering.design_search.registry import ImmutableRegistry
from engineering.design_search.selection import select
from engineering.design_search.storage import atomic_immutable
from engineering.ferrite_maglev import candidate_magnetics as canonical
from engineering.passive_suspension import fields
from . import magnets,equipment,hvac,ledger

ROOT=Path(__file__).resolve().parents[2]
REQUIREMENTS='ndfeb-halbach-lightweight-six-car-2026-10-25'
FRAME=dict(id='car',parent_id=None,origin_m=[0.,0.,0.],rotation_matrix=[[1.,0.,0.],[0.,1.,0.],[0.,0.,1.]])


def sources():
    paths={p for p in Path(__file__).parent.glob('*.py') if p.name!='publication.py'}
    paths.update((Path(__file__).parent/'recipes').glob('*.py'))
    paths.update(ROOT/p for p in magnets.sources())
    paths.update(ROOT/p for p in equipment.sources())
    paths.update(ROOT/p for p in hvac.source_inputs()['local_sha256'])
    paths.update((ROOT/'engineering/design_search').glob('*.py'))
    return {p.relative_to(ROOT).as_posix():sha256(p.read_bytes()).hexdigest() for p in sorted(paths)}


def write(path,value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    atomic_immutable(path,encoded(value))


FIELD_SETTINGS=dict(mesh_size_m=.005,outer_margin_m=.25,max_nodes=180000,check_convergence=True,steel_model='linear_bound')
REFINEMENT_RECIPES=[['N35-H8-half-no-yoke','planar-halbach','Arnold-N35UH',dict(segments=8,yoke_m=0.,magnet_volume_m3=.006)],
                    ['N35-H8-quarter-no-yoke','planar-halbach','Arnold-N35UH',dict(segments=8,yoke_m=0.,magnet_volume_m3=.003)]]


def check_field(raw,geometry,*,gap_m=None,temperature_C=None,currents_A=None,steel_model='linear_bound'):
    if raw['result_id']!=fields._digest({k:v for k,v in raw.items() if k!='result_id'}):
        raise ValueError('Field primitive content differs')
    if raw['source_sha256']!=fields.sources() or raw['geometry_id']!=fields._digest(geometry):
        raise ValueError('Field primitive source/actual geometry differs')
    if raw['physical_accepted'] is not False:raise ValueError('Field cannot confer physical acceptance')
    if gap_m is not None:
        expected=dict(gap_m=gap_m,temperature_C=temperature_C,lateral_m=0.,roll_rad=0.,currents_A=currents_A or {})
        if raw['operating_point']!=expected:raise ValueError('Field operating point differs from declared scenario')
        cfg=fields._settings(dict(FIELD_SETTINGS,steel_model=steel_model))
        if raw['diagnostics'].get('requested_settings')!=cfg:
            raise ValueError('Field primitive solver/refinement/material settings differ')
    return raw


def load_workers(study_path,refinement_path,nonlinear_path):
    study=json.loads(Path(study_path).read_bytes())
    if study['study_id']!=identity({k:v for k,v in study.items() if k!='study_id'}) or study['source_sha256']!=magnets.sources():
        raise ValueError('Magnetic worker source or study identity differs')
    values={v['sample_id']:v for v in magnets.candidates()}
    if study['candidates']!=list(values.values()):raise ValueError('Magnetic catalogue changed')
    inputs={name:magnets.field_geometry(v) for name,v in values.items()}
    rows=[]
    expected=magnets.reference_schedule(list(values.values()))
    observed=[(row['sample_id'],row['gap_m'],row['temperature_C']) for row in study['rows']]
    if observed!=expected or len(observed)!=32:raise ValueError('Exact unique32-point worker schedule required')
    for row in study['rows']:
        if row['execution_status']=='executed':check_field(row['raw_result'],inputs[row['sample_id']],
            gap_m=row['gap_m'],temperature_C=row['temperature_C'])
        else:
            raise ValueError('This fixed36-checked-point archive requires every declared worker point executed; preserve refused jobs separately')
        rows.append(row)
    refinements=json.loads(Path(refinement_path).read_bytes())
    if refinements['source_sha256']!=magnets.sources() or refinements['refinement_id']!=identity({k:v for k,v in refinements.items() if k!='refinement_id'}):
        raise ValueError('Derived experiment identity/source differs')
    recipe=Path(__file__).with_name('recipes')/'refinement_recipe.py'
    if sha256(recipe.read_bytes()).hexdigest()!=refinements['recipe_sha256']:
        raise ValueError('Retained experiment recipe source differs')
    if [item['recipe'] for item in refinements['candidates']]!=REFINEMENT_RECIPES:
        raise ValueError('Only the two declared derived physical recipes are admitted')
    for item in refinements['candidates']:
        value=magnets._build(tuple(item['recipe']))
        if value!=item['candidate']:raise ValueError('Derived physical recipe/stock differs')
        # Explicit admission by this campaign, not the frozen catalogue. The
        # generic recoil model and named grade are inherited unchanged.
        fg=deepcopy(inputs['N35-H8'])
        for key in ('length_x_m','reference_gap_m','origin_yz_m','regions','circuits'):
            fg[key]=deepcopy(value[key])
        if fg!=item['field_geometry']:raise ValueError('Derived recoil adapter or actual geometry differs')
        if item['lineage']['parent_physical_ids']!=[values['N35-H8']['physical_id']] or item['lineage']['operation']!='counted-PM-volume-reduction':
            raise ValueError('Derived experiment lineage differs')
        if value['materials']!=values['N35-H8']['materials']:raise ValueError('Derived grade/material laws differ')
        name=value['sample_id'];values[name]=value;inputs[name]=fg
        check_field(item['raw_result'],fg,gap_m=.012,temperature_C=80.)
        rows.append(dict(sample_id=name,gap_m=.012,temperature_C=80.,execution_status='executed',
                         raw_result=item['raw_result'],derived_recipe=item['recipe'],lineage=item['lineage']))
    authority=refinements['authority']
    if authority['sample_id']!='N35-H8-half-no-yoke' or authority['selected_physical_id']!=values[authority['sample_id']]['physical_id']:
        raise ValueError('Authority experiment must use declared half-volume candidate')
    check_field(authority['raw_result'],inputs[authority['sample_id']],gap_m=.012,temperature_C=80.,currents_A={'array-control':20.})
    nonlinear=json.loads(Path(nonlinear_path).read_bytes())
    raw=nonlinear.get('raw_result',nonlinear)
    check_field(raw,inputs['N35-H8'],gap_m=.012,temperature_C=80.,steel_model='nonlinear_repo_proxy')
    if nonlinear['source_sha256']!=magnets.sources() or len(values)!=14 or len(rows)+2!=36:
        raise ValueError('Exact14-proposal/36-point campaign required')
    return dict(study=study,refinements=refinements,nonlinear=nonlinear,
                values=values,field_inputs=inputs,rows=rows,checked_points=len(rows)+2)


def component_changes(value,chassis,fitout,climate,base,*,audit=None,climate_trace=None):
    changes=[dict(id='support',removal_kind='counted-stock',
        removed_part_ids=[f'a79/support-module/{i}' for i in range(24)],
        removed_kg_per_car=24*base['module']['mass_kg'],added_known_kg_per_car=value['stock']['train_known_mass_kg_per_car'],
        basis='Replace only 24 counted canonical support modules; retain propulsion band, all other equipment and allocations',
        source_bindings=base['source_sha256'],unknown_installed_inventory=value['unknown_installed_inventory'])]
    if chassis is not None:
        changes.append(dict(id='frame',removal_kind='counted-stock',removed_part_ids=chassis['removed_stock_ids'],
            removed_kg_per_car=chassis['removed_counted_frame_kg'],added_known_kg_per_car=chassis['counted_material_mass_kg'],
            basis='Exact retained frame IDs only; magnetic collectors, hardpoints, fasteners and panels remain',
            source_bindings=equipment.sources(),unknown_installed_inventory=chassis['unknown_installed_inventory']))
    if fitout is not None:
        audit=equipment.allocation_audit() if audit is None else audit
        changes.append(dict(id='doors-windows',removal_kind='inherited-allocation',
            removed_allocation_ids=[x['id'] for x in audit['eligible_removals']],
            removed_kg_per_car=sum(x['mass_kg'] for x in audit['eligible_removals']),
            added_known_kg_per_car=fitout['counted_material_mass_kg']+fitout['supplier_mechanism_reference_mass_kg'],
            basis='Door500 and fixed-glazing500 ancestor allowances; added material plus supplier mechanism reference, not complete certified doors',
            source_bindings=equipment.sources(),unknown_installed_inventory=fitout['unknown_installed_inventory']))
    if climate is not None:
        removed=hvac.allocation_replacement(climate)['remove_mass_kg'] if climate_trace is None else climate_trace['mass_kg']
        if climate['package_hardware_mass_range_kg_per_car'][0]!=climate['package_hardware_mass_range_kg_per_car'][1]:
            raise ValueError('This campaign requires one nominal package-weight point; other ranges stay in HVAC study')
        changes.append(dict(id='hvac',removal_kind='inherited-allocation',removed_allocation_ids=['hvac'],
            removed_kg_per_car=removed,added_known_kg_per_car=climate['package_hardware_mass_range_kg_per_car'][0],
            basis='Nominal electric-compressor package hardware; 800kg unweighed HVAC allowance removed once',
            source_bindings=hvac.source_inputs()['local_sha256'],unknown_installed_inventory=climate['unknown_items']))
    return changes


def systems_modes(body,climates):
    fitout=next(e for e in body['equipment'] if e['id']=='aluminium-sandwich-ES2-reference/solar-laminated-6.76mm')
    two=next(h for h in climates['candidates'] if h['id']=='bus-ul700-electric-two')
    three=next(h for h in climates['candidates'] if h['id']=='bus-ul700-electric-three')
    return [dict(id='retained-systems',chassis=None,fitout=None,climate=None),
            dict(id='lighter-doors-windows',chassis=None,fitout=fitout,climate=None),
            dict(id='lighter-services-two',chassis=None,fitout=fitout,climate=two),
            dict(id='larger-duty-three',chassis=None,fitout=fitout,climate=three),
            *[dict(id='lighter-services/'+c['id'],chassis=c,fitout=fitout,climate=two) for c in body['chassis']]]


def physical_descriptor(value,mode):
    c,e,h=(mode[key] for key in ('chassis','fitout','climate'))
    return dict(magnet=magnets.physical_definition(value),
        chassis='retained-frame' if c is None else dict(id=c['id'],material={k:c['material'][k] for k in ('alloy','temper','density_kg_m3')},
            members=[{k:deepcopy(m[k]) for k in ('id','width_m','depth_m','wall_m','length_m','section')} for m in c['members']],
            stock=c['stock_parts']),
        doors_windows='retained-allowances' if e is None else dict(id=e['id'],stock=e['stock_parts'],
            mechanism_id=e['door']['id'],mechanism_count=4,opening_m=[1.4,2.1],glazing=e['glazing']['id']),
        HVAC='retained-800kg-allowance' if h is None else dict(id=h['id'],units_per_car=h['units_per_car'],
            manufacturer_source_id=h['source_id'],package_envelope_m=h.get('package_unit_envelope_m'),
            supply=h.get('compressor_supply')))


def candidate_bundle(value,mode,mass,src):
    physical=physical_descriptor(value,mode)
    components=[];inventory=[]
    def stock(name,weight,kind='component-reference'):
        key={'support':'magnet','frame':'chassis','doors-windows':'doors_windows','hvac':'HVAC'}.get(name)
        components.append(dict(id=name,kind=kind,frame_id='car',material_id='assembly',
                               physical_component_ref=None if key is None else identity(physical[key]),resolved_in='source-bound component records'))
        inventory.append(dict(id=name,status='known',quantity=1,scope='vehicle-per-car',basis='Declared material/reference/retained allocation subtotal; no surveyed installation',
            unit_mass_kg=weight,geometry_id=name,frame_id='car',cg_m=None,inertia_kg_m2=None))
    stock('retained',mass['retained_other_components_and_allocations_kg'],'unlocated-mass-budget')
    for change in mass['changes']:
        stock(change['id'],change['added_known_kg_per_car'])
    for i,item in enumerate(mass['unknown_installed_inventory']):
        scope=item.get('scope') if isinstance(item,dict) else None
        inventory.append(dict(id=f'unknown/{i}',status='unknown',quantity=24 if scope=='per-module' else 1,
            scope='guideway-per-span' if scope=='per-beam-span' else 'vehicle-per-car',basis=str(item),
            unit_mass_kg=None,geometry_id=None,frame_id='car',cg_m=None,inertia_kg_m2=None))
    return make_candidate(requirement_revision=REQUIREMENTS,architecture=physical,
        frames=[FRAME],materials=[dict(id='assembly',density_kg_m3=None,basis='Material and supplier identities resolve in explicit component definitions; no fictitious homogeneous density')],
        geometry=components,interfaces=[dict(id='guideway',permanent_magnets='train-only',suspension_coils='train-only',
            ordinary_guideway='concrete with passive steel facings; matching concrete/attachments ungenerated'),
            dict(id='service',**ledger.SERVICE)],installed_inventory=inventory,
        label=value['sample_id']+' / '+mode['id'],source_bindings=src,
        lineage=dict(parent_candidate_ids=[],operation='explicit-component-substitution'))


def winding_screen(value):
    out=[]
    for coil in value['circuits']:
        copper=coil['turns']*coil['conductor_area_m2']
        window=coil['window_pack_width_m']*coil['window_height_m']
        out.append(dict(circuit_id=coil['id'],bare_copper_fill=copper/window,limit=.55,pass_screen=copper/window<=.55))
    return out


def field_quality(value,raw):
    grade=value['materials'][value['grade_id']];temp=raw['operating_point']['temperature_C']
    hcj=(grade['hcj_20c_a_m']-grade.get('hcj_tolerance_a_m',0))*(1+grade['hcj_temperature_coefficient_per_k']*(temp-20))
    margin=raw['PM_H_parallel_min_A_per_m']+hcj*grade['demag_hcj_fraction_limit']
    forces=[q['F_z_N'] for q in raw['diagnostics']['validation_quantities'].values()]
    forces.extend(q['F_z_N'] for q in raw['diagnostics']['contour_forces'])
    variation=max(abs(raw['F_z_N']-force) for force in forces)
    return dict(point_numerically_usable=raw['interpolation_usable'],recoil_margin_A_per_m=margin,
        steel_peak_T=raw['steel_B_peak_T'],steel_guard_T=2.2,
        observed_force_variation_N=variation,
        joint_point_usable=raw['interpolation_usable'] and margin>=0 and raw['steel_B_peak_T']<=2.2,
        scope='Checked2D material-proxy point, not an actuator/operating/physical pass')


def run(output,*,worker_study,refinements,nonlinear):
    output=Path(output);src=sources();workers=load_workers(worker_study,refinements,nonlinear)
    base=canonical.definition();body=equipment.study();climates=hvac.study()
    for name,value in (('magnetic-worker.json',workers['study']),('refinements.json',workers['refinements']),
                       ('nonlinear-confirmation.json',workers['nonlinear']),('equipment.json',body),('HVAC.json',climates)):
        write(output/name,value)
    registry=ImmutableRegistry(output/'registry');candidates=[];results=[];comparisons=[];eligible=[];excluded={}
    modes=systems_modes(body,climates)
    for name,value in workers['values'].items():
        write(output/'magnet-components'/(value['physical_id']+'.json'),value)
        write(output/'field-inputs'/(value['physical_id']+'.json'),workers['field_inputs'][name])
        hot=next((r['raw_result'] for r in workers['rows'] if r['execution_status']=='executed' and r['sample_id']==name and r['gap_m']==.012 and r['temperature_C']==80.),None)
        for mode in modes:
            changes=component_changes(value,mode['chassis'],mode['fitout'],mode['climate'],base,
                audit=body['allocation_audit'],climate_trace=climates['allocation_trace'])
            mass=ledger.compose(base['controlled_tare_kg'],changes)
            candidate=candidate_bundle(value,mode,mass,src);registry.store('candidate',candidate);candidates.append(candidate)
            write(output/'candidates'/(candidate['candidate_id']+'.json'),candidate)
            allowance=[0.,0.]
            if mode['climate'] is not None:
                h=mode['climate'];hardware=h['package_hardware_mass_range_kg_per_car'][0]
                allowance=[amount-hardware for amount in h['provisional_installed_mass_scenario_kg']]
            masses=[mass['comparison_aw3_kg_per_car']+x for x in allowance]
            bounds=[]
            for bound in masses:
                context=deepcopy(mass);context['comparison_aw3_kg_per_car']=bound
                bounds.append(None if hot is None else ledger.support_screen(hot['F_z_N'],context,
                    quality_usable=field_quality(value,hot)['joint_point_usable'],
                    numerical_variation_N=field_quality(value,hot)['observed_force_variation_N']))
            interface=None if mode['fitout'] is None else mode['fitout']['hvac_interface']
            scenario=hvac.default_scenario(name='matched-AW2-50C')
            if interface is not None:
                scenario.update(glazing_m2=interface['total_glazing_area_m2'],solar_factor=interface['solar_factor_g'],
                    glazing_U_W_m2K=interface['U_W_m2K'],doors_open=interface['platform_side_doors_open'])
                door=mode['fitout']['door'];scenario.update(door_width_m=door['door_width_m'],door_height_m=door['door_height_m'])
                if not math.isclose(scenario['doors_open']*scenario['door_width_m']*scenario['door_height_m'],interface['open_area_m2']):
                    raise ValueError('HVAC door area differs from actual fitout')
            load=hvac.heat_load(scenario)
            climate_check=None if mode['climate'] is None else hvac.assess(mode['climate'],load)
            structure=None
            if mode['chassis'] is not None:
                reference=mode['chassis']['screens'];ratio=masses[1]/reference['comparison_aw3_kg_per_car']
                structure=dict(reference=reference,mass_ratio=ratio,
                    roof_rail_stress_pa=reference['roof_rail_stress_pa']*ratio,
                    roof_rail_deflection_m=reference['roof_rail_deflection_m']*ratio,
                    spreader_stress_pa=reference['spreader_plate_stress_pa']*ratio,
                    method='Same frozen geometry, linear load-response rescaling only; global buckling/joints not solved')
                structure.update(roof_rail_elastic_necessary_pass=structure['roof_rail_stress_pa']<=reference['HAZ_allowable_pa']
                        and structure['roof_rail_deflection_m']<=.002,
                    spreader_elastic_necessary_pass=structure['spreader_stress_pa']<=reference['HAZ_allowable_pa'],
                    bracing_fatigue_and_global_body_qualified=False)
            report=dict(candidate_id=candidate['candidate_id'],magnet_id=value['physical_id'],sample_id=name,mode=mode['id'],
                mass_ledger=mass,provisional_installation_addition_kg=allowance,comparison_aw3_mass_band_kg=masses,
                hot_support_bounds=bounds,hot_field_quality=None if hot is None else field_quality(value,hot),
                winding=winding_screen(value),HVAC_load=load,HVAC_screen=climate_check,structure=structure,
                physical_accepted=False,integrated_eligible=False)
            comparisons.append(report)
            request=make_evaluation_request(candidate,evaluator_id='combined-support-envelope',evaluator_sources=src,
                purpose='next-experiment',hypothesis=dict(field='2D infinite travel with named recoil grade; source-bound primitive reused',
                    HVAC='catalogue hardware plus explicit unknown installation bands'),
                scenario=dict(temperature_C=80.,gap_m=.012,installation_mass_band_kg=allowance),
                settings=dict(magnet_component_id=value['physical_id'],field_result_id=None if hot is None else hot['result_id']))
            constraints=[dict(id='support-reserve-at-mass-band',state='unknown' if hot is None else bounds[-1]['state']),
                dict(id='winding-fill',state='pass' if all(r['pass_screen'] for r in report['winding']) else 'fail'),
                dict(id='actuation-thermal-civil-and-physical',state='unknown')]
            result=make_result(request,execution_status='executed',numerical_status='converged',
                screen_status='fail' if any(c['state']=='fail' for c in constraints) else 'unknown',maturity='numerical-screen',
                metrics=dict(known_support_kg=value['stock']['train_known_mass_kg_per_car'],
                    comparison_aw3_upper_kg=masses[1]),constraints=constraints,
                diagnostics=[dict(report_sha256=identity(report),scope='Derived mass/load screen; no additional FEM solves claimed')])
            registry.store('evaluation-request',request);registry.store('evaluation',result);results.append(result)
            if mode['id']=='lighter-services-two':
                if hot is None or not field_quality(value,hot)['joint_point_usable']:
                    excluded[candidate['candidate_id']]=['no-jointly-usable-hot-field-point']
                elif hot['F_z_N']-field_quality(value,hot)['observed_force_variation_N']<masses[1]*9.80665/24:
                    excluded[candidate['candidate_id']]=['below-unreserved-comparison-support']
                else:eligible.append(candidate['candidate_id'])
    if len(candidates)>112:raise ValueError('Composed alternative budget exceeded')
    policy=dict(policy_id='next-magnet-experiment-minimum-listed-stock/1',objectives={'known_support_kg':1.},
        eligibility='Named80Ccheckedpoint and unreserved conservative mass-band support; fixed lighter-services-two comparison context; winding/control remain holds')
    next_selection=select([c for c in candidates if c['candidate_id'] in eligible],
        [r for r in results if r['candidate_id'] in eligible],purpose='next-experiment',policy=policy)
    integrated=select(candidates,results,purpose='integrated-baseline',policy=dict(policy,
        critical_evaluators=['combined-support-envelope','coupled-qualified-system'],minimum_maturity='coupled-numerical'))
    registry.store('selection',next_selection);registry.store('selection',integrated)
    if sources()!=src:raise ValueError('Composition source changed; publication refused')
    summary=dict(schema='osr-ndfeb-lightweight-campaign/1',source_sha256=src,
        requirements=ledger.SERVICE,magnetic_geometry_count=len(workers['values']),checked_field_points=workers['checked_points'],
        composed_candidate_count=len(candidates),comparisons=comparisons,candidate_ids=[c['candidate_id'] for c in candidates],
        evaluation_ids=[r['evaluation_id'] for r in results],next_experiment=next_selection,next_experiment_exclusions=excluded,
        integrated_selection=integrated,full_route_executed=False,installed_mass_known=False,
        source_unchanged=True,**FLAGS)
    summary['campaign_id']=identity(summary)
    write(output/'summary.json',summary)
    return summary


def verify(output):
    output=Path(output);summary=json.loads((output/'summary.json').read_bytes())
    if summary['campaign_id']!=identity({k:v for k,v in summary.items() if k!='campaign_id'}) or summary['source_sha256']!=sources():
        raise ValueError('Composed campaign source/content differs')
    if any(summary.get(key) is not False for key in FLAGS) or summary['integrated_selection']['selected_candidate_id'] is not None:
        raise ValueError('Incomplete research cannot be adopted')
    registry=ImmutableRegistry(output/'registry')
    reports={r['candidate_id']:r for r in summary['comparisons']}
    for cid in summary['candidate_ids']:
        candidate=json.loads((output/'candidates'/(cid+'.json')).read_bytes());validate_candidate(candidate)
        if registry.read_context(identity(candidate))!=candidate:raise ValueError('Candidate context differs')
        physical=registry.read('candidate',cid)
        if any(physical[k]!=candidate[k] for k in PHYSICAL_KEYS):raise ValueError('Registered physical design differs')
    for eid in summary['evaluation_ids']:
        result=registry.read('evaluation',eid)
        if result['request']!=registry.read('evaluation-request',eid):raise ValueError('Evaluation binding differs')
        if result['diagnostics'][0]['report_sha256']!=identity(reports[result['candidate_id']]):raise ValueError('Mass/force comparison differs')
    for name in ('next_experiment','integrated_selection'):
        if registry.read('selection',summary[name]['selection_id'])!=summary[name]:raise ValueError('Selection differs')
    # Rebuild derived comparisons and identities from current deterministic
    # tools and unchanged raw field primitives. This redoes no FEM calculation.
    with tempfile.TemporaryDirectory(prefix='osr-vehicle-recompute-') as directory:
        expected=run(directory,worker_study=output/'magnetic-worker.json',refinements=output/'refinements.json',
                     nonlinear=output/'nonlinear-confirmation.json')
        if expected!=summary:raise ValueError('Retained vehicle/component/selection reports differ from source reconstruction')
        for relative in ('equipment.json','HVAC.json'):
            if (Path(directory)/relative).read_bytes()!=(output/relative).read_bytes():
                raise ValueError('Retained domain report differs: '+relative)
        rebuilt=ImmutableRegistry(Path(directory)/'registry')
        for key in summary['candidate_ids']:
            if rebuilt.read('candidate',key)!=registry.read('candidate',key):raise ValueError('Rebuilt candidate differs')
        for key in summary['evaluation_ids']:
            if rebuilt.read('evaluation',key)!=registry.read('evaluation',key):raise ValueError('Rebuilt evaluation differs')
    return dict(verified=True,campaign_id=summary['campaign_id'],physical_accepted=False)


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('action',choices=['run','verify'])
    parser.add_argument('--output',type=Path,default=ROOT/'build/vehicle-optimisation/campaign')
    parser.add_argument('--worker-study',type=Path);parser.add_argument('--refinements',type=Path);parser.add_argument('--nonlinear',type=Path)
    args=parser.parse_args()
    value=verify(args.output) if args.action=='verify' else run(args.output,worker_study=args.worker_study,refinements=args.refinements,nonlinear=args.nonlinear)
    print(json.dumps({k:value[k] for k in ('campaign_id','verified','composed_candidate_count') if k in value},indent=2))


if __name__=='__main__':main()
