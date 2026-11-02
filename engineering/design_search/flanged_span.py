"""A separate, unqualified flanged-girder research adapter; no campaign runner.

The longitudinal solver sees real steel flange/web polygons, not an equivalent
thickness in the web-only topology FE model. Prices and process rates below are
editable planning hypotheses, not Iraqi supplier quotations or measured times.
"""
from copy import deepcopy
from math import ceil, fsum, isclose, isfinite
from pathlib import Path

from engineering.station_rail import ROOT, civil
from engineering.station_rail.common import digest, identity
from . import civil_beam as beam, civil_section_model as section_model
from . import civil_shape_geometry as geometry

PRODUCER = 'engineering/design_search/flanged_span.py'
FLAGS = dict(physical_accepted=False, engineering_accepted=False,
    manufacturing_release=False, operating_release=False, configuration_adopted=False,
    selected_reference_changed=False, current_evaluator_admission=False)
VEHICLE_ID = '756a68870162f7559b052b05c9b201728c9f448e3bb61114f287848c02f2d3a3'
SELECTION_ID = '8e5905bc7c81d6177bbaafde81ab3a5f8cc54947c4923eb4493949566ac85cdc'
GAUGES = {'baseline': (.012, .025), 'thick-web': (.016, .025),
    'thick-flange': (.012, .035)}
CASES = ('low', 'base', 'high')
POSES = ('quarter-span-moment', 'midspan-moment', 'left-support-reaction')
HOLDS = ['installed mass and reserve CG/inertia unknown',
    'deck reinforcement and transverse rail-load distribution unresolved',
    'unequal rail loading, torsion and actual bearing distribution unresolved',
    'shear deformation, local/lateral buckling and fatigue unresolved',
    'welds, full-moment splices, bracing and material grade unqualified',
    'lifting, construction stages, piers, foundations and site/geotechnics unresolved',
    'supplier/process evidence, schedule precedence and cost uncertainty unresolved']


def _finite(value):
    if isinstance(value, dict):
        for v in value.values(): _finite(v)
    elif isinstance(value, (list, tuple)):
        for v in value: _finite(v)
    elif isinstance(value, float) and not isfinite(value):
        raise ValueError('Finite derived flanged-span arithmetic required')


def _seal(value, key):
    _finite(value)
    value[key] = identity(value)
    return value


def _sealed(value, key):
    if value.get(key) != identity({k: v for k, v in value.items() if k != key}):
        raise ValueError('Sealed flanged-span identity required: ' + key)


def _sources():
    names = (PRODUCER, 'engineering/design_search/civil_shape_geometry.py',
        'engineering/design_search/civil_section_model.py',
        'engineering/design_search/civil_beam.py', 'engineering/station_rail/civil.py',
        'engineering/station_rail/common.py')
    root = Path(__file__).resolve().parents[2]
    return {name: digest(root/name) for name in names}


def default_spec():
    """Versioned bounded engineering assumptions; no claim of market accuracy."""
    return dict(schema='osr-flanged-span-assumptions/1',
        provenance='Declared Class C planning hypotheses; not measured process times or quotations',
        steel_density_kg_m3=7850., concrete_density_kg_m3=2500., steel_E_Pa=200e9,
        concrete_E_Pa=35e9, module_length_m=5.,
        production_shifts_per_day=2, civil_shifts_per_day=2, hours_per_shift=8,
        productive_utilisation=.75, production_crew_per_shift=4, civil_crew_per_shift=4,
        reserve_mass_kg=dict(deck_rebar=[500.,1000.,2000.], connectors=[100.,250.,600.],
            bearings=[100.,200.,400.], bracing=[200.,500.,1000.],
            protection_hardware=[50.,150.,400.], splice_and_weld_metal=[50.,100.,250.]),
        rates=dict(steel_iqd_kg=[1200.,1800.,2600.], concrete_iqd_m3=[100000.,160000.,250000.],
            finished_reserve_iqd_kg=[1500.,2500.,5000.], rail_iqd_kg=[1500.,2500.,4000.],
            fastener_set_iqd=[50000.,100000.,200000.], labour_iqd_h=[5000.,8000.,14000.],
            machine_iqd_h=[15000.,30000.,60000.], cut_h_m=[.015,.03,.06],
            fillet_weld_h_m=[.15,.3,.6], butt_weld_h_m=[1.,2.,4.],
            plate_prep_h_each=[.15,.3,.6], qa_h_plate=[.2,.4,.8],
            splice_qa_h_each=[1.,2.,4.], coating_iqd_m2=[6000.,12000.,24000.],
            concrete_labour_h_m3=[2.,4.,8.], brace_install_h_station=[1.,2.,4.],
            bearing_install_h_each=[1.,2.,4.], delivery_iqd_t_km=[200.,400.,800.],
            crane_iqd_h=[150000.,300000.,600000.], crane_hours=[8.,16.,32.],
            civil_labour_hours=[40.,80.,160.], rail_install_h_set=[.1,.2,.4]),
        material_yield=[.96,.9,.82], overhead_fraction=[.1,.2,.3], delivery_km=50.)


def _spec(value):
    s = default_spec() if value is None else deepcopy(value)
    template = default_spec()
    if set(s) != set(template) or s['schema'] != template['schema']:
        raise ValueError('Complete versioned flanged-span assumptions required')
    for k in ('steel_density_kg_m3','concrete_density_kg_m3'):
        if type(s[k]) not in (int,float) or not isfinite(s[k]) or not 1 <= s[k] <= 1e6:
            raise ValueError('Bounded positive material density required')
    for k in ('steel_E_Pa','concrete_E_Pa'):
        if type(s[k]) not in (int,float) or not isfinite(s[k]) or not 1e6 <= s[k] <= 1e12:
            raise ValueError('Bounded positive elastic hypothesis required')
    if (s['module_length_m'] != 5. or s['production_shifts_per_day'] != 2
            or s['civil_shifts_per_day'] != 2 or s['hours_per_shift'] != 8
            or not 0 < s['productive_utilisation'] <= 1
            or any(type(s[k]) is not int or not 1 <= s[k] <= 100 for k in
                ('production_crew_per_shift','civil_crew_per_shift'))
            or type(s['delivery_km']) not in (int,float)
            or not isfinite(s['delivery_km']) or not 0 < s['delivery_km'] <= 10000):
        raise ValueError('Explicit two-shift bounded production/delivery assumptions required')
    if set(s['rates']) != set(template['rates']) or set(s['reserve_mass_kg']) != set(template['reserve_mass_kg']):
        raise ValueError('All process rates and positive named reserves required')
    for rows in (s['rates'], s['reserve_mass_kg']):
        for values in rows.values():
            if (not isinstance(values,list) or len(values) != 3
                    or any(type(v) not in (int,float) or not isfinite(v) or not 0 < v <= 1e12 for v in values)
                    or values != sorted(values)):
                raise ValueError('Positive ordered low/base/high values required')
    for key, lower, upper in [('material_yield',.1,1.),('overhead_fraction',0.,1.)]:
        v=s[key]
        if not isinstance(v,list) or len(v)!=3 or any(type(x) not in (int,float)
                or not isfinite(x) or not lower < x <= upper for x in v):
            raise ValueError('Bounded three-case yield/overhead required')
    _finite(s)
    return s


def _rect(y0,y1,z0,z1):
    return [[y0,z0],[y1,z0],[y1,z1],[y0,z1]]


def _physical(gauge):
    if gauge not in GAUGES: raise ValueError('One of three explicit physical gauges required')
    tw,tf=GAUGES[gauge]
    sections=[dict(id='deck',material='research_concrete',polygon_yz_m=_rect(-1.,1.,-.18,0.))]
    for side,y in [('left',-.65),('right',.65)]:
        for name,p in [('top-flange',_rect(y-.15,y+.15,-.18-tf,-.18)),
                ('web',_rect(y-tw/2,y+tw/2,-1.38+tf,-.18-tf)),
                ('bottom-flange',_rect(y-.15,y+.15,-1.38,-1.38+tf))]:
            sections.append(dict(id=side+'-'+name,material='structural_steel',polygon_yz_m=p))
    return dict(schema='osr-flanged-span-physical/1',span_m=20.,deck_width_m=2.,
        coordinate_frame=dict(x='longitudinal',y='transverse',z='up',deck_top_z_m=0.),
        cells=[dict(id='cell-000',x_start_m=0.,x_end_m=20.,sections=sections)],
        rail_interface=dict(track_gauge_m=1.435,rail_head_width_m_hypothesis=.072,
            rail_centre_spacing_m=1.435+.072,
            rail_centres_y_m=[-(1.435+.072)/2,(1.435+.072)/2],
            centre_spacing_derivation='1.435m gauge +0.072m symmetric rail-head width =1.507m; centres at +/-0.7535m',
            gauge_geometry_scope='Assumed72mm head width at the gauge measurement height; exact running-face/contact geometry remains unqualified',
            deck_top_z_m=0.,rail_profile='60E1 quantity hypothesis; attachments unresolved'),
        nominal_stock_only=True)


def generate(gauge='baseline'):
    physical=_physical(gauge)
    return _seal(dict(schema='osr-flanged-span-candidate/1',gauge=gauge,
        candidate_id=identity(physical),physical_definition=physical,
        source_sha256=_sources(),installed_mass_complete=False,**FLAGS),'geometry_id')


def _candidate(candidate):
    _sealed(candidate,'geometry_id')
    if (candidate.get('schema')!='osr-flanged-span-candidate/1'
            or candidate.get('physical_definition')!=_physical(candidate.get('gauge'))
            or candidate.get('candidate_id')!=identity(candidate['physical_definition'])
            or candidate.get('source_sha256')!=_sources()
            or any(candidate.get(k) is not False for k in FLAGS)):
        raise ValueError('Current exact nonpromoting flanged-span geometry required')


def _section_candidate(candidate,s):
    _candidate(candidate)
    p=candidate['physical_definition']
    value=dict(schema='osr-civil-shape-physical/1',family='hybrid_steel_concrete',
        profile='flanged-'+candidate['gauge'],span_m=20.,deck_width_m=2.,
        coordinate_frame=deepcopy(p['coordinate_frame']),cells=deepcopy(p['cells']),
        materials=dict(research_concrete=dict(density_kg_m3=s['concrete_density_kg_m3']),
            structural_steel=dict(density_kg_m3=s['steel_density_kg_m3'])),
        provenance=dict(representation='exact convex-prism steel flange/web and concrete deck polygons',
            external_physical_candidate_id=candidate['candidate_id'],
            density_is_evaluation_assumption=True),unresolved_installed_items=list(HOLDS),
        physical_accepted=False,engineering_accepted=False,manufacturing_release=False,operating_release=False)
    _seal(value,'candidate_id');geometry.validate(value)
    return value


def quantities(candidate,spec=None):
    s=_spec(spec);adapted=_section_candidate(candidate,s);q=geometry.quantities(adapted)
    rail_mass=2*20*civil.RAIL_KG_M;sets=2*(ceil(20/.6)+1)
    reserve=s['reserve_mass_kg']
    values=[q['total_nominal_stock_mass_kg']+rail_mass+8.*sets+fsum(v[i] for v in reserve.values()) for i in range(3)]
    return _seal(dict(schema='osr-flanged-span-quantities/1',candidate_id=candidate['candidate_id'],
        geometry_id=candidate['geometry_id'],section_adapter_candidate_id=adapted['candidate_id'],
        source_quantities=q,source_sha256=_sources(),density_assumptions=dict(steel=s['steel_density_kg_m3'],concrete=s['concrete_density_kg_m3']),
        rail_mass_kg=rail_mass,fastener_set_count=sets,fastener_mass_kg=8.*sets,
        reserve_mass_kg=deepcopy(reserve),accounted_mass_kg_cases=dict(zip(CASES,values)),
        reserve_CG_and_inertia=None,complete_installed_mass_kg=None,installed_mass_complete=False,
        unknown_is_zero=False,**FLAGS),'evaluation_id')


def _offsets():
    return [car*17.5+8.5+c+dx for car in range(6) for c in (-6.4,6.4) for dx in (-1.05,1.05)]


def load_context(root=ROOT):
    """Execute current selection/ledger guards; never accept old vehicle masses."""
    from . import civil_shape_mechanics
    from engineering import mass_reserve_sensitivity
    from engineering.development_baseline import selection
    base=civil_shape_mechanics.load_context(root);reserve=mass_reserve_sensitivity.plan(root)
    vehicle=selection.load(root)['vehicle']
    if (base['vehicle_candidate_id']!=reserve['candidate_id'] or base['selection_id']!=reserve['selection_id']
            or vehicle['candidate_id']!=base['vehicle_candidate_id']
            or vehicle['evaluation_id']!=base['vehicle_evaluation_id']):
        raise ValueError('Selected vehicle/mass-reserve context differs')
    cases=[]
    for mass in reserve['sensitivity_cases']:
        for name,passengers in [('empty',0),('normal',46),('crowd_control',160)]:
            loaded=mass['scenario_tare_mass_kg_per_car']+75.*passengers
            cases.append(dict(name=name,vehicle_mass_case=mass['name'],passengers_per_car=passengers,
                tare_kg_per_car=mass['scenario_tare_mass_kg_per_car'],loaded_kg_per_car=loaded,
                full_axle_force_N=loaded*civil.G/4*1.3,offsets_m=deepcopy(base['cases'][0]['offsets_m'])))
    result=_seal(dict(schema='osr-flanged-span-load-context/1',vehicle_candidate_id=base['vehicle_candidate_id'],
        vehicle_evaluation_id=base['vehicle_evaluation_id'],selection_id=base['selection_id'],
        **{k:vehicle[k] for k in ('body_candidate_id','support_component_id','propulsion_component_id')},
        selected_context_id=base['context_id'],mass_reserve_result_id=reserve['result_id'],
        dynamic_factor_applied_once=1.3,cases=cases,
        source_sha256={**base['source_sha256'],**reserve['source_sha256'],**_sources()},**FLAGS),'context_id')
    _context(result,root)
    return result


def _context(context,root=ROOT):
    _sealed(context,'context_id')
    if (context.get('schema')!='osr-flanged-span-load-context/1'
            or context.get('vehicle_candidate_id')!=VEHICLE_ID or context.get('selection_id')!=SELECTION_ID
            or context.get('dynamic_factor_applied_once')!=1.3
            or any(context.get(k) is not False for k in FLAGS)):
        raise ValueError('Exact selected six-car nonpromoting context required')
    rows=context['cases'];expected={(name,mass) for name in ('empty','normal','crowd_control') for mass in CASES}
    if len(rows)!=9 or {(r['name'],r['vehicle_mass_case']) for r in rows}!=expected:
        raise ValueError('Complete disjoint nine vehicle scenarios required')
    for mass in CASES:
        if len({r['tare_kg_per_car'] for r in rows if r['vehicle_mass_case']==mass})!=1:
            raise ValueError('Mixed vehicle tare scenarios')
    for row in rows:
        people=dict(empty=0,normal=46,crowd_control=160)[row['name']]
        if (row.get('passengers_per_car')!=people or row['offsets_m']!=_offsets()
                or type(row['tare_kg_per_car']) not in (int,float) or not isfinite(row['tare_kg_per_car'])
                or row['tare_kg_per_car']<=0 or row['loaded_kg_per_car']!=row['tare_kg_per_car']+75.*people
                or row['full_axle_force_N']!=row['loaded_kg_per_car']*civil.G/4*1.3):
            raise ValueError('Full axle force, passenger mass or formation differs')
    if not context.get('source_sha256'): raise ValueError('Source-bound selected context required')
    root=Path(root).resolve()
    for name,h in context['source_sha256'].items():
        path=Path(name)
        if path.is_absolute() or '..' in path.parts or digest(root/path)!=h:
            raise ValueError('Selected context source bytes differ')


def _pose(offsets,name):
    section=5. if name=='quarter-span-moment' else 10.
    breaks=(0.,20.) if name=='left-support-reaction' else (0.,section,20.)
    candidates=sorted({x-a for a in offsets for x in breaks})
    def score(t):
        return fsum((20-x)/20 if name=='left-support-reaction' else
            ((20-section)*x/20 if x<=section else section*(20-x)/20)
            for a in offsets if 0 <= (x:=a+t) <= 20.)
    t=min(candidates,key=lambda t:(-round(score(t),12),t))
    return dict(name=name,translation_m=t,scope='Representative ideal-beam influence pose; not a stress/deflection envelope')


def evaluate(candidate,context,spec=None,*,root=ROOT):
    """81 cheap representative responses plus27 all-position beam-model bounds."""
    s=_spec(spec);_context(context,root)
    # A valid self-seal is not evidence of current selection/ledger provenance.
    # Regenerate through their strict guards before admitting an external context.
    if context != load_context(root):
        raise ValueError('Context differs from freshly generated selected vehicle/ledger inputs')
    q=quantities(candidate,s);adapted=_section_candidate(candidate,s)
    models=section_model.models(adapted,dict(structural_steel=s['steel_E_Pa'],research_concrete=s['concrete_E_Pa']))
    model=next(m for m in models if m['name']=='steel-only-longitudinal');ei=model['cells'][0]['EI_Nm2']
    tw,tf=GAUGES[candidate['gauge']];h=1.2-2*tf
    textbook_iy=2*(tw*h**3/12+2*(.3*tf**3/12+.3*tf*(.6-tf/2)**2))
    if not isclose(ei,s['steel_E_Pa']*textbook_iy,rel_tol=1e-11):
        raise ValueError('Polygon stiffness differs from independent I-girder formula')
    responses=[];bounds=[]
    for load in context['cases']:
        offsets=load['offsets_m'];force=load['full_axle_force_N']
        max_axles=max(sum(a <= x <= a+20. for x in offsets) for a in offsets)
        for mass_case,mass in q['accounted_mass_kg_cases'].items():
            w=mass*civil.G/20.;cells=[dict(x_start_m=0.,x_end_m=20.,EI_Nm2=ei,distributed_load_N_m=w)]
            dead=beam.analyse(cells,[],10.)['deflection_at_observation_m']
            dead_formula=5*w*20.**4/(384*ei)
            if not isclose(dead,dead_formula,rel_tol=1e-12):raise ValueError('Dead-load textbook control differs')
            upper_cells=[dict(cells[0],distributed_load_N_m=w+2*max_axles*force/20.)]
            upper=beam.deflection_upper_bound(upper_cells,[])
            bounds.append(dict(load_case=load['name'],vehicle_mass_case=load['vehicle_mass_case'],
                span_mass_case=mass_case,maximum_simultaneous_axles=max_axles,
                all_position_model_deflection_upper_m=upper,dead_load_midspan_m=dead,
                dead_load_textbook_m=dead_formula,physical_deflection_upper_bound_available=False))
            for name in POSES:
                pose=_pose(offsets,name);points=[dict(x_m=a+pose['translation_m'],force_N=force)
                    for a in offsets if 0<=a+pose['translation_m']<=20.]
                result=beam.analyse(cells,points,[0.,5.,10.,15.,20.])
                if (max(abs(result[k]) for k in ('force_residual_N','moment_residual_Nm',
                        'right_support_internal_moment_residual_Nm'))>1e-5
                        or max(result['deflection_at_observation_m'])>upper+1e-10):
                    raise ValueError('Beam equilibrium or all-position model bound differs')
                responses.append(dict(load_case=load['name'],vehicle_mass_case=load['vehicle_mass_case'],
                    span_mass_case=mass_case,pose=pose,points=points,full_axle_force_N=force,
                    accounted_span_mass_kg=mass,total_downward_force_N=w*20.+len(points)*force,
                    response=result,gross_steel_extreme_fibre_stress_demand_Pa=result['maximum_sagging_moment_Nm']*.6/textbook_iy))
    return _seal(dict(schema='osr-flanged-span-beam-evaluation/1',candidate_id=candidate['candidate_id'],
        quantity_evaluation_id=q['evaluation_id'],load_context_id=context['context_id'],
        section_adapter_candidate_id=adapted['candidate_id'],steel_only_model=model,
        evaluation_assumptions=s,source_sha256={**context['source_sha256'],**_sources()},
        textbook_steel_I_y_m4=textbook_iy,EI_Nm2=ei,responses=responses,all_position_model_bounds=bounds,
        execution='completed',numerical_validity='gross-beam-equilibrium-and-textbook-controls-checked',
        scope='Simply supported paired girders with common curvature and symmetric load-sharing hypothesis; no composite concrete stiffness',
        physical_deflection_limit_m=None,physical_strength_allowable_Pa=None,engineering_screen='unresolved',
        installed_mass_complete=False,holds=list(HOLDS),integrated_selection=None,**FLAGS),'evaluation_id')


def estimate(candidate,quantity=None,spec=None):
    """Per-span costs only; excludes piers/foundations, plant capital and lifecycle."""
    s=_spec(spec);q=quantities(candidate,s)
    if quantity is not None and quantity!=q:raise ValueError('Cost quantity/candidate/assumption identity differs')
    tw,tf=GAUGES[candidate['gauge']];h=1.2-2*tf;g=q['source_quantities']
    stock=dict(flange_plates=16,web_plates=8,plate_handling_modules=8,girder_splices=6,
        bracing_stations=9,bearing_assemblies=4,cut_perimeter_m=16*2*(5.+.3)+8*2*(5.+h),
        double_fillet_weld_m=160.,full_penetration_butt_weld_m=6*(h+2*.3),
        weld_thickness_time_factor=max(tw/.012,tf/.025),steel_coating_m2=g['steel_surface_m2'],
        module_splice_x_m=[5.,10.,15.],splice_continuity_qualified=False,
        bracing_geometry=None,bearing_geometry=None,plate_nesting_proved=False)
    cases={}
    for i,name in enumerate(CASES):
        r={k:v[i] for k,v in s['rates'].items()};reserve_mass=fsum(v[i] for v in s['reserve_mass_kg'].values())
        material=dict(main_steel=g['by_material']['structural_steel']['mass_kg']/s['material_yield'][i]*r['steel_iqd_kg'],
            concrete=g['by_material']['research_concrete']['volume_m3']*r['concrete_iqd_m3'],
            finished_named_reserves=reserve_mass*r['finished_reserve_iqd_kg'],
            running_rails=q['rail_mass_kg']*r['rail_iqd_kg'],fastener_sets=q['fastener_set_count']*r['fastener_set_iqd'])
        hours=dict(cut=stock['cut_perimeter_m']*r['cut_h_m'],
            flange_web_weld=stock['double_fillet_weld_m']*r['fillet_weld_h_m']*stock['weld_thickness_time_factor'],
            full_moment_splice_weld=stock['full_penetration_butt_weld_m']*r['butt_weld_h_m']*stock['weld_thickness_time_factor'],
            plate_preparation=24*r['plate_prep_h_each'],qa=24*r['qa_h_plate']+6*r['splice_qa_h_each'],
            deck_casting=g['by_material']['research_concrete']['volume_m3']*r['concrete_labour_h_m3'],
            brace_assembly=9*r['brace_install_h_station'],bearing_assembly=4*r['bearing_install_h_each'])
        labour_hours=fsum(hours.values());machine_hours=hours['cut']+hours['flange_web_weld']+hours['full_moment_splice_weld']
        fabrication=dict(labour=labour_hours*r['labour_iqd_h'],machine_operating=machine_hours*r['machine_iqd_h'],
            coating=stock['steel_coating_m2']*r['coating_iqd_m2'])
        subtotal=fsum(material.values())+fsum(fabrication.values());overhead=subtotal*s['overhead_fraction'][i]
        factory=subtotal+overhead
        delivery=q['accounted_mass_kg_cases'][name]/1000*s['delivery_km']*r['delivery_iqd_t_km']
        civil_hours=r['civil_labour_hours']+q['fastener_set_count']*r['rail_install_h_set']
        install=dict(civil_labour=civil_hours*r['labour_iqd_h'],crane=r['crane_hours']*r['crane_iqd_h'])
        productive=s['hours_per_shift']*2*s['productive_utilisation']
        cases[name]=dict(material_iqd=material,fabrication_iqd=fabrication,overhead_iqd=overhead,
            factory_gate_iqd=factory,delivery_iqd=delivery,delivered_iqd=factory+delivery,
            installation_iqd=install,scoped_installed_iqd=factory+delivery+fsum(install.values()),
            factory_labour_hours=hours,machine_operating_hours=machine_hours,
            civil_labour_hours=civil_hours,crane_hours=r['crane_hours'],
            production_days_capacity_lower_bound=max(labour_hours/(productive*s['production_crew_per_shift']),machine_hours/productive),
            civil_days_capacity_lower_bound=max(civil_hours/(productive*s['civil_crew_per_shift']),r['crane_hours']/productive))
    return _seal(dict(schema='osr-flanged-span-cost/1',candidate_id=candidate['candidate_id'],
        quantity_evaluation_id=q['evaluation_id'],source_sha256=_sources(),assumptions=s,
        estimate_class='C',currency='IQD',manufacturing_stock=stock,cases=cases,
        production_crews='Two separate 8-hour crews; worker count is per shift',
        machine_rate_scope='Operating-only rate excludes operator labour and dedicated plant capital',
        reserve_rate_scope='Finished reserve unit price includes reserve fabrication; only assembly labour added',
        scope='Per20mspan: named nominal stock/reserves, rails/fasteners once, fabrication, delivery and scoped erection',
        whole_system_ranking_allowed=False,complete_installed_cost_iqd=None,dedicated_plant_capital_iqd=None,
        lifecycle_cost_iqd=None,installed_mass_complete=False,manufacturing_qualified=False,
        schedule_is_precedence_resolved=False,holds=list(HOLDS),**FLAGS),'evaluation_id')
