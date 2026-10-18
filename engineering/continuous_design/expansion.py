"""Fixed-function shape/material/process searches over existing OSR compilers.

These are three bounded research demonstrations, not a general topology/circuit
inventor. Explicit material records are inseparable property bundles.
"""
from copy import deepcopy
import itertools
import math
from pathlib import Path

from engineering.twin_workflow import core
from . import processes,operation_graph,zone_thermal

ITEM='process-aware-multidiscipline-search'
CONTEXTS={
    'mechanical-roof-study':'roof-cassette-0.994x2.35m-85C',
    'mechanical-equipment-study':'six-car-equipment-and-reference-mount',
    'civil-architecture-study':'fixed-100m-five20m-twotrack',
}
LAYUPS={
    'quasi-isotropic':[0,45,-45,90,90,-45,45,0],
    'cross-ply':[0,90,0,90,90,0,90,0],
    'axial-biased':[0,0,45,-45,-45,45,0,0],
}


def domains(kind):
    if kind=='mechanical-roof-study':
        return dict(layup=list(LAYUPS),skin_m=[.0015,.002],core_m=[.02,.0246,.03],core_density=[60,80,100],
            crown_m=[.05,.1],support_span_m=[.5,.33],material_system=['development-gfrp'],process_profile=['vacuum-laminate'])
    if kind=='mechanical-equipment-study':
        return dict(topology=['rhs-ladder','folded-pan'],centre_rib=[False,True],cover_joint=['welded','bolted'],
            wall_m=[.004,.006,.008],series_modules=[24,28,32],parallel_strings=[2,3,4],hvac_modules=[3,4,5],
            duct_area_m2=[.01,.02,.04],flow_m3_s=[.08,.12,.16],duct_layout=['balanced','single-end'])
    if kind=='civil-architecture-study':
        from engineering.design_engine.design_alternatives import civil_variables
        result={key:spec['choices'] for key,spec in civil_variables().items()}
        result.update(geometry_fraction=[0.,.5,1.],mould_route=['split-reusable','rigid-one-piece'])
        return result
    raise ValueError('unregistered multidisciplinary study')


def sources():
    paths=[]
    for package in ('engineering/design_engine','engineering/design_consistency','engineering/civil_exploration','engineering/twin_design','design/component-catalogue/src/osr_mech'):
        paths.extend((core.ROOT/package).rglob('*.py'))
    for folder in ('engineering/composite_panels/config','engineering/twin_design/data','engineering/civil_exploration/config','lib/templates'):
        paths.extend(p for p in (core.ROOT/folder).rglob('*') if p.is_file() and p.suffix in {'.json','.toml','.csv'})
    paths.extend(p for p in (core.ROOT/'design/component-catalogue/src/osr_mech').rglob('*') if p.is_file() and p.suffix in {'.json','.toml','.csv'})
    return {str(path.relative_to(core.ROOT)):core.sha(path) for path in paths}


def validate(kind,parameters):
    domain=domains(kind)
    if set(parameters)!={'context_id','variables'} or parameters['context_id']!=CONTEXTS[kind]:
        raise ValueError('fixed functional context required')
    values=parameters['variables']
    if not isinstance(values,dict) or set(values)!=set(domain) or any(not any(type(v) is type(choice) and v==choice for choice in domain[k]) for k,v in values.items()):
        raise ValueError('shape/material/process choice outside registered domain')
    if kind=='civil-architecture-study':
        options=core.read(core.ROOT/'engineering/civil_exploration/config/system-options.json')
        family=next(f for f in options['beams'] if f['id']==values['deck_family'])
        if values['material'] not in family['materials']:
            raise ValueError('incompatible civil material/family pair')


def seeds():
    from .tasks import task
    roof=dict(layup='quasi-isotropic',skin_m=.0015,core_m=.0246,core_density=80,crown_m=.05,
        support_span_m=.33,material_system='development-gfrp',process_profile='vacuum-laminate')
    equipment=dict(topology='rhs-ladder',centre_rib=True,cover_joint='bolted',wall_m=.006,
        series_modules=28,parallel_strings=4,hvac_modules=4,duct_area_m2=.02,flow_m3_s=.08,duct_layout='balanced')
    values=[('mechanical-roof-study',roof),('mechanical-roof-study',dict(roof,layup='axial-biased',core_density=100)),
        ('mechanical-equipment-study',equipment),('mechanical-equipment-study',dict(equipment,topology='folded-pan')),
        ('mechanical-equipment-study',dict(equipment,cover_joint='welded')),
        ('mechanical-equipment-study',dict(equipment,hvac_modules=5))]
    from engineering.design_engine.design_alternatives import civil_defaults
    for family in domains('civil-architecture-study')['deck_family']:
        options=core.read(core.ROOT/'engineering/civil_exploration/config/system-options.json')
        deck=next(d for d in options['beams'] if d['id']==family)
        material='normal' if 'normal' in deck['materials'] else deck['materials'][0]
        values.append(('civil-architecture-study',dict(civil_defaults(),deck_family=family,material=material,
            geometry_fraction=.5,mould_route='split-reusable')))
    return [task(kind,dict(context_id=CONTEXTS[kind],variables=v),'Compare a fixed-function physical/material/process alternative; all release gates open') for kind,v in values]


def roof(values):
    from engineering.design_consistency import demonstrators as d
    from engineering.design_consistency.contracts import summary
    from osr_mech.rolling_stock import composite_panels as panel
    config=core.read(core.ROOT/'engineering/composite_panels/config/development.json')
    model=d.panel_bay(config,span=values['support_span_m'],grade_density=values['core_density'],
        crown=values['crown_m'],aperture=False,skin=values['skin_m'],core=values['core_m'],ply_angles=LAYUPS[values['layup']])
    plies=[panel.Ply(p['thickness_m'],p['angle_deg']) for p in model['ply_schedule']]
    abd=panel.laminate_abd(plies,values['core_m'],config['bond']['thickness_m_each'],config['glass'])
    hot=panel.strip_response(abd,3500.,values['support_span_m'],values['core_m'],model['core_grade']['shear_pa'],
        stiffness_factor=config['screen']['hot_wet_modulus_factor'],shear_factor=config['screen']['hot_wet_shear_factor'])
    checks=dict(nominal_strip_deflection=model['response']['total_deflection_m']<=.005,
        hot_wet_pressure_holdout=hot['total_deflection_m']<=.005)
    inventory=processes.physical_parts(model)
    graph=operation_graph.simple(inventory,process='bond')
    # The model contains material regions; this is not a laminate cure/flow model.
    process=dict(profile_id='vacuum-laminate',parts=inventory,graph=graph,
        observations=dict(ply_thicknesses_m=[p.thickness_m for p in plies],ply_placement_count=len([p for p in model['parts'] if 'laminate_ply' in p]),
            core_temperature_c=config['screen']['hot_roof_temperature_c'],core_temperature_limit_c=model['core_grade']['continuous_max_temperature_c']))
    return dict(contract=model,checks=checks,physics=dict(abd=abd,hot_wet=hot,glass=deepcopy(config['glass']),
        plies=model['ply_schedule'],core_m=values['core_m'],bond_m=config['bond']['thickness_m_each'],
        material_status='one coupled development GFRP card; fibre/resin/strength/temperature acceptance open',
        scope='Developed strip model only; curved roof shell and actual curved attachment contact remain unevaluated'),
        process=process,mass_kg=summary(model)['mass_kg'],unknown=model['unresolved_part_allocations']+['roof shell/attachments','measured resin/fibre system and cure','full-stack fire/hot-wet qualification'])


def equipment(values):
    from engineering.design_engine.design_alternatives import compile_vehicle
    from engineering.design_engine.electrical_installation import auxiliary_power_screen,cooling_loss_duty
    from engineering.design_consistency import demonstrators as d
    from engineering.design_consistency.contracts import box,part,member,summary
    design=compile_vehicle(dict(series_modules=values['series_modules'],parallel_strings=values['parallel_strings'],
        hvac_modules=values['hvac_modules']))
    payload=design['battery']['properties']['mass_kg']+values['hvac_modules']*125.
    mats=d.materials();mats['payload-envelope']=dict(density_kg_m3=payload/(.9*.6*.35),young_pa=1e9,poisson=.3,
        basis='Homogeneous mass envelope of existing battery/HVAC allocation; no stiffness or internal geometry credit')
    thickness=values['wall_m'];parts=[];bearing_ids=[]
    def plate(identifier,size,centre):
        p=part(identifier,'steel',dict(role='provisional carrier fabrication',primitives=[box(identifier,*size,centre)]),mats)
        parts.append(p);return p
    floor=plate('floor',[1.2,.9,thickness],[0.,0.,thickness/2]);bearing_ids.append('floor')
    if values['topology']=='rhs-ladder':
        for index,y in enumerate([-.3,.3]+([0.] if values['centre_rib'] else [])):
            name=f'rail-{index}';parts.append(member(name,1.2,.08,.18,thickness,'steel',mats,(0.,y,-.09)));bearing_ids.append(name)
        profile_id='profile-cut-weld'
    else:
        for index,y in enumerate([-.45+thickness/2,.45-thickness/2]+([0.] if values['centre_rib'] else [])):
            name=f'web-{index}';plate(name,[1.2,thickness,.18],[0.,y,-.09]);bearing_ids.append(name)
        profile_id='folded-bolted'
    for i,(x,y) in enumerate(itertools.product([-.55,.55],[-.4,.4])):
        plate(f'post-{i}',[.02,.04,.43-thickness],[x,y,(.43+thickness)/2])
    parts.append(part('equipment-payload','payload-envelope',dict(role='equipment mass envelope',primitives=[box('payload',.9,.6,.35,[0.,0.,thickness+.195])]),mats))
    plate('cover',[1.2,.9,thickness],[0.,0.,.43+thickness/2])
    duct_outer=math.sqrt(values['duct_area_m2'])+.0014
    duct_length=4. if values['duct_layout']=='balanced' else 6.
    for index,side in enumerate([-1.,1.]):
        parts.append(member(f'duct-{index}',duct_length,duct_outer,duct_outer,.0007,'steel',mats,
            (side*(duct_length/2+.7),.8,.6)))
    model=d.contract('Reference mounting cassette with existing six-car equipment allocation',parts,mats)
    model['unresolved_part_allocations']=['full bolt/locking and weld geometry','bend radii and allowances','actual equipment mounting interfaces','harness/duct connections and sealing']
    inventory=processes.physical_parts(model)
    next(p for p in inventory if p['id']=='cover')['reversible']=values['cover_joint']=='bolted'
    graph=operation_graph.simple(inventory,process='weld' if values['topology']=='rhs-ladder' else 'fasten',
        maintenance=[dict(part='equipment-payload',remove_first=['cover'],translation_m=[0.,0.,1.])])
    # Derive gross prismatic section from the very same generated solids.
    sections=[]
    for p in parts:
        if p['id'] not in bearing_ids:continue
        area=p['properties']['mass_kg']/mats['steel']['density_kg_m3']/1.2
        centre=p['properties']['cg_m'][2]
        if p['id'].startswith('rail-'):
            inertia=(.08*.18**3-(.08-2*thickness)*(.18-2*thickness)**3)/12
        else:
            height=thickness if p['id']=='floor' else .18
            inertia=area*height**2/12
        sections.append((area,centre,inertia))
    area=sum(a for a,z,i in sections);centroid=sum(a*z for a,z,i in sections)/area
    inertia=sum(i+a*(z-centroid)**2 for a,z,i in sections)
    represented_mass=summary(model)['mass_kg']
    bend_allowance=2*(math.pi/2*(2*thickness+.4*thickness)) if values['topology']=='folded-pan' else 0.
    # Conservative excess blank material is carried as an unresolved mass
    # allowance, with no stiffness credit, until finished bends are modeled.
    bend_allowance_mass=1.2*bend_allowance*thickness*mats['steel']['density_kg_m3']
    model_mass=represented_mass+bend_allowance_mass;force=model_mass*3*9.81
    ei=210e9*inertia;deflection=5*(force/1.2)*1.2**4/(384*ei)
    stress=(force*1.2/8)*max(abs(-.18-centroid),abs(thickness-centroid))/inertia
    hvac=deepcopy(design['inputs']['hvac'])
    normal=zone_thermal.solve(hvac,module_count=values['hvac_modules'],flow_m3_s=values['flow_m3_s'],duct_area_m2=values['duct_area_m2'],layout=values['duct_layout'])
    failed=zone_thermal.solve(hvac,module_count=values['hvac_modules'],failed_modules=1,flow_m3_s=values['flow_m3_s'],duct_area_m2=values['duct_area_m2'],layout=values['duct_layout'])
    auxiliary=auxiliary_power_screen(design['battery'],values['hvac_modules'])
    reference=compile_vehicle({})
    auxiliary['fan_augmented_input_lower_bound_w']=auxiliary['ac_component_input_lower_bound_w']+normal['fan_power_w']
    duty=cooling_loss_duty(design['battery'],[dict(duration_s=60.,terminal_power_w=200000.),
        dict(duration_s=60.,terminal_power_w=30000.),dict(duration_s=20.,terminal_power_w=-75000.)],
        auxiliary_power_w=auxiliary['fan_augmented_input_lower_bound_w'])
    checks=dict(reference_carrier_deflection=deflection<=.005,reference_carrier_stress=stress<=235e6,
        nominal_two_zone_temperature=normal['maximum_temperature_c']<=hvac['thermal_assumptions']['study_limit_c'],
        failed_module_two_zone_temperature=failed['maximum_temperature_c']<=hvac['thermal_assumptions']['study_limit_c'],
        humidity_hypothesis=failed['maximum_humidity_ratio']<=.020,
        duct_velocity=normal['duct_velocity_m_s']<=8.,minimum_ventilation_hypothesis=values['flow_m3_s']>=.08,
        auxiliary_capacity=auxiliary['fan_augmented_input_lower_bound_w']<=auxiliary['candidate_nameplate_apparent_power_va'],
        nominal_converter_voltage=auxiliary['checks']['nominal_converter_input_voltage']!='failed',
        fixed_reference_usable_energy=design['battery']['usable_energy_kwh']>=reference['battery']['usable_energy_kwh'],
        battery_cooling_loss_duty=duty['research_constraints_passed'])
    rectangles=[dict(id=p['id'],size_m=sorted(p['manufacturing']['primitives'][0]['dimensions_m'],reverse=True)) for p in parts if p['id'] not in {'equipment-payload'} and p['id'].startswith(('floor','cover','web','post'))]
    if values['topology']=='folded-pan':
        rectangles=[r for r in rectangles if r['id'] not in {'floor','web-0','web-1'}]
        rectangles.append(dict(id='developed-pan-blank',size_m=[1.2,.9+2*.18+bend_allowance,thickness]))
    return dict(contract=model,mass_kg=model_mass,checks=checks,
        physics=dict(beam=dict(length_m=1.2,ei_nm2=ei,force_n=force,deflection_m=deflection,section_area_m2=area,centroid_z_m=centroid,inertia_m4=inertia,bearing_part_ids=bearing_ids),
            hvac_normal=normal,hvac_failed=failed,hvac_inputs=hvac,auxiliary=auxiliary,battery_cooling_loss=duty,
            represented_material_mass_kg=represented_mass,unrepresented_bend_allowance_kg=bend_allowance_mass,
            reference_train_mass_kg=design['review']['total_train_mass_kg'],
            gross_addition_hypothesis_train_mass_kg=design['review']['total_train_mass_kg']+6*model_mass,
            unresolved_converter_mass_lower_bound_kg_per_car=auxiliary['additional_equipment_mass_lower_bound_kg_per_car'],
            replacement_mass_credit_kg=0.,payload_mass_kg=payload),
        process=dict(profile_id=profile_id,parts=inventory,rectangles=rectangles,graph=graph,
            observations=dict(wall_m=thickness,inside_bend_radius_m=2*thickness,bend_count=2)),
        unknown=model['unresolved_part_allocations']+['complete installed mount mass and interfaces','supplier cooling/refrigeration/duct map','target protection and converter compatibility','SIL/HIL and physical test'])


def compile_civil_shape(values):
    from engineering.design_engine.design_alternatives import compile_civil
    from engineering.design_engine.design_alternatives import _civil_contract
    from engineering.civil_exploration.workflow import candidate
    from engineering.civil_exploration.model import takeoff
    from osr_mech.civil.exploration import geometry
    selected={k:values[k] for k in ('deck_family','pier_family','material','foundation_family')}
    design=compile_civil(selected)
    if values['geometry_fraction']==.5:
        return design
    options=core.read(core.ROOT/'engineering/civil_exploration/config/system-options.json')
    definition=deepcopy(design['civil_candidate']['definition'])
    for name,group in (('deck','beams'),('pier','piers')):
        choice=next(r for r in options[group] if r['id']==definition[name]['family'])
        definition[name]['parameters']={key:(int(round(a+(b-a)*values['geometry_fraction'])) if key=='rib_count' else a+(b-a)*values['geometry_fraction']) for key,(a,b) in choice['bounds'].items()}
    study=deepcopy(design['study'])
    study['candidates'][0].update(definition)
    compiled=candidate(definition,study)
    contract,correspondence=_civil_contract(compiled,study)
    quantities=takeoff(compiled,study)
    allowance=sum(quantities[k] for k in ('reinforcement_allowance_kg','prestress_allowance_kg','embedded_allowance_kg','superimposed_dead_allowance_kg'))
    review=deepcopy(design['alternatives_review'])
    review.update(defined_material_mass_kg=correspondence['mass_kg'],unresolved_allowance_mass_kg=allowance,
        mass_balance_residual_kg=quantities['installed_study_mass_kg']-correspondence['mass_kg']-allowance)
    design.update(study=study,civil_candidate=compiled,geometry=geometry(compiled['definition']),contract=contract,
        correspondence=correspondence,quantities=quantities,alternatives_review=review)
    return design


def civil(values):
    from engineering.civil_exploration.model import System
    from engineering.design_consistency.contracts import summary
    design=compile_civil_shape(values)
    response=System(design['civil_candidate'],design['study'],design['study']['ground_scenarios'][0],4).static_envelope()
    model=design['contract'];inventory=processes.physical_parts(model)
    graph=operation_graph.simple(inventory,process='inspect',capacity_kg=125000.)
    graph['fixtures'][0]['load_scope']='current_operation'
    withdrawal=4. if values['mould_route']=='split-reusable' else 20.
    checks=dict(finite_reference_response=all(math.isfinite(v) for v in response['envelope'].values() if type(v) in (int,float)),
        mass_allowance_reconciliation=abs(design['alternatives_review']['mass_balance_residual_kg'])<1e-6)
    limits=[]
    for metric,limit in design['study']['research_limits'].items():
        value=design['quantities'].get(metric,response['envelope'].get(metric))
        state='unresolved' if limit is None or value is None else 'passed' if value<=limit else 'failed'
        limits.append(dict(metric=metric,value=value,limit=limit,state=state,approved=False))
        if state!='unresolved':checks['source_research_limit/'+metric]=state=='passed'
    return dict(contract=model,mass_kg=design['quantities']['installed_study_mass_kg'],checks=checks,
        physics=dict(response=response,candidate=design['civil_candidate'],study=design['study'],
            research_limits=limits,
            defined_material_mass_kg=summary(model)['mass_kg'],unresolved_allowance_mass_kg=design['alternatives_review']['unresolved_allowance_mass_kg'],
            source_scope='100m reference, five 20m two-track spans; not adopted Baghdad loading/ground',
            section_physics='Existing synthetic material cards and any perfect-bond composite assumptions remain unqualified'),
        process=dict(profile_id='precast-reusable',parts=inventory,graph=graph,
            observations=dict(withdrawal_m=withdrawal,suspended_mass_kg=design['quantities']['suspended_mass_kg'])),
        unknown=model['unresolved_part_allocations']+['unresolved civil criterion/'+row['metric'] for row in limits if row['state']=='unresolved']+['reinforcement/cage and actual casting units','temporary works/erection load path','soil, settlement and supplier material qualification'])


def evaluate(kind,parameters,output):
    validate(kind,parameters);values=parameters['variables']
    data={'mechanical-roof-study':roof,'mechanical-equipment-study':equipment,'civil-architecture-study':civil}[kind](values)
    core.write(output/'physical-contract.json',data['contract'],exclusive=True)
    core.write(output/'physics.json',data['physics'],exclusive=True)
    assignments={}
    for part in data['contract']['parts']:
        material=part['material'].lower()
        profile=data['process']['profile_id']
        if part['id']=='equipment-payload':profile='purchased-equipment'
        elif part['id'].startswith('duct-'):profile='sheet-duct'
        elif kind=='civil-architecture-study' and 'steel' in material:profile='profile-cut-weld'
        elif 'frp' in material:profile='vacuum-laminate' if kind=='mechanical-roof-study' else 'pultrusion-bond'
        elif kind=='mechanical-roof-study' and material in {'steel','fastener'}:profile='purchased-section-fastener'
        assignments[part['id']]=profile
    process=processes.evaluate(**data['process'],part_profiles=assignments,contract=data['contract'],output=output)
    checks=dict(data['checks'],**{'manufacturing/'+k:v for k,v in process['checks'].items()})
    failed=[k for k,v in checks.items() if not v]
    metrics=dict(mass_kg=data['mass_kg'],**process['metrics'])
    assessment=dict(context_id=CONTEXTS[kind],candidate_family=CONTEXTS[kind],variables=values,
        geometry=dict(parts=[dict(id=p['id']) for p in data['contract']['parts']]),objectives=metrics)
    blocked=kind=='mechanical-roof-study' and not process['checks']['core_service_temperature']
    needs=[dict(item_id='qualified-high-temperature-roof-material-system',required='Provide one compatible resin/fibre/core/bond/fire system for the fixed 85C roof context; current coupled core cards fail. Do not lower the temperature or independently select material constants.')] if blocked else []
    if kind=='mechanical-equipment-study':
        needs.append(dict(item_id='circuit-and-hvac-performance-adapters',required='Develop separately benchmarked circuit/electrothermal and detailed ventilation/refrigeration evaluators with supplier maps and target timing; two-zone and gross-beam screens do not qualify these systems.'))
    if kind=='civil-architecture-study':
        needs.append(dict(item_id='site-qualified-civil-construction-inputs',required='Bind adopted train loads, Baghdad ground, measured material laws, reinforcement/units, temporary works and erection sequences before civil design acceptance.'))
    return dict(study_pass=not failed,checks=checks,failed_checks=failed,metrics=metrics,assessment=assessment,
        manufacturing_process=process,needs=needs,search_blocked=dict(reason='all registered core cards exceed their service-temperature datum') if blocked else None,
        open_evidence=data['unknown']+process['unknown'],
        physical_contract_sha256=core.sha(output/'physical-contract.json'),physics_sha256=core.sha(output/'physics.json'),
        scope='Bounded fixed-function geometry/material/assembly demonstration; study pass covers implemented research screens only',**core.FLAGS)


def neighbors(kind,parameters,result):
    if result.get('search_blocked'):return []
    domain=domains(kind);values=parameters['variables'];proposals=[]
    # Architecture switches come first; every proposal is recompiled and screened.
    for key,choices in domain.items():
        index=choices.index(values[key])
        for j in (index-1,index+1):
            if 0<=j<len(choices):
                changed=dict(values);changed[key]=choices[j]
                params=dict(context_id=parameters['context_id'],variables=changed)
                try:validate(kind,params)
                except ValueError:continue
                proposals.append(params)
    return proposals


def repair_tasks(kind,parameters,result,envelope):
    from . import tasks
    import sqlite3
    values=[tasks.task(kind,p,'Recompile a different shape/material/process choice from actual measured screen feedback',parent=envelope['key'])
        for p in neighbors(kind,parameters,result)]
    workspace=envelope.get('evidence_workspace')
    if workspace:
        db=sqlite3.connect((Path(workspace)/'queue.sqlite').resolve().as_uri()+'?mode=ro',uri=True)
        try:
            values=[v for v in values if not db.execute('SELECT 1 FROM jobs WHERE key=?',(tasks.identity(v,envelope['baseline_sha256']),)).fetchone()]
        finally:db.close()
    return values[:4]
