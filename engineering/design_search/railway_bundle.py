"""One physical railway composition shared by all current design adapters.

An architecture is incomplete when its new drive, secondary or energy store is
unlocated/unweighed. Its common-stock demand calculation remains explicitly
conditional; this module never fills the missing equipment with zero mass.
"""
from copy import deepcopy
from pathlib import Path
from engineering.station_rail import ROOT,vehicle,braking,civil
from engineering.station_rail.common import digest,identity
from . import design_grammar as grammar,railway_architecture as architecture,wheel_motor

PRODUCER='engineering/design_search/railway_bundle.py'
FLAGS=grammar.FLAGS


def motor_options():
    first=wheel_motor.default_parameters();second=deepcopy(first)
    # Both keep exactly the retained onboard fin and its installation envelope.
    # This is an independent physical experiment, not an extrapolated force map.
    second['physical'].update(name='return-path-experiment',backiron_m=.05,slot_width_m=.035)
    return [first,second]


def _knobs(family):
    return {'P1':dict(launch_m=500.),'P2':dict(launch_m=250.),
        'P3':dict(launch_m=300.,booster_m=150.),'P4':dict(launch_m=500.,powered_axles=2),
        'P5':dict(fraction=.5),'P6':dict(supply='conductor-supply',powered_axles_per_car=2),
        'P7':dict(launch_m=500.)}[family]


def materialize(body,*,family='P1',motor_parameters=None,root=ROOT):
    grammar.validate(body);root=Path(root);reference=vehicle.build(root);p=body['parameters']
    if p['cars']!=6 or p['length_m']!=17. or p['width_m']!=2.65:raise ValueError('Current coupled experiment requires the explicit six-car 17m comfort context; materialize other fitout/support interfaces first')
    motor_parameters=deepcopy(motor_options()[0] if motor_parameters is None else motor_parameters)
    motor=wheel_motor.definition(motor_parameters)
    fin=motor_parameters['physical']
    if (fin['secondary_length_m'],fin['secondary_thickness_m'],fin['active_height_m'],fin['secondary_bottom_TOR_m'])!=(9.,.015,.16,.02):raise ValueError('A changed onboard secondary requires counted replacement stock, retention and interface materialization')
    spec=architecture.load_spec(root);spec['scenario']['car_length_m']=p['length_m']
    proxy=deepcopy(reference);proxy['body_candidate_id']=body['candidate_id'];proxy['propulsion_component_id']=motor['motor_component_id']
    speed=16. if family=='P2' else 20.
    case=architecture._configuration(family,p['cars'],2000.,speed,_knobs(family),spec,proxy)
    physical=case['physical_definition'];substitutions=[];unknown=[]
    if family in ('P6','P7'):
        substitutions.append(dict(remove_account_id='passive-secondary',replacement='wheel-traction' if family=='P6' else 'new-passive-secondary',replacement_installed_mass_kg=None))
        unknown.append('Located, counted replacement drive/secondary and its mountings')
    if family in ('P4','P6'):unknown += ['Drive, gear/axle interfaces, power electronics, cables and recovery/traction supply']
    if family in ('P6','P7'):
        motor=dict(schema='osr-incomplete-propulsion-definition/1',family=physical['wayside']['motor_family'] if family=='P7' else 'onboard-wheel-traction',
            physical_geometry=None,available_force_map=None,installed_mass_kg=None,
            motor_component_id=identity(dict(family=family,onboard=physical['onboard'],wayside=physical['wayside'])))
        motor_parameters=None
    physical['propulsion_definition_id']=motor['motor_component_id']
    physical['component_substitutions']=substitutions
    case['candidate_id']=identity(physical)
    case['capability_composition']=architecture.capabilities.composition(family,case['candidate_id'],case['requirement_revision'])
    case['case_id']=identity({k:v for k,v in case.items() if k!='case_id'})
    removed={q['remove_account_id'] for q in substitutions}
    equipment=[q for q in body['retained_equipment_accounts'] if q['id'] not in removed]
    tare=body['known_structure_stock_kg']+sum(q['mass_kg'] for q in equipment)
    v=deepcopy(reference);v.update(candidate_id=case['candidate_id'],body_candidate_id=body['candidate_id'],propulsion_component_id=motor['motor_component_id'])
    v['mass'].update(accounted_tare_kg_per_car=tare,accounted_cap_loaded_kg_per_car=tare+46*75.,accounted_160_control_kg_per_car=tare+160*75.,accounted_tare_kg_six_cars=6*tare)
    vehicle_geometry=deepcopy(reference['physical_definition']['vehicle']);vehicle_geometry.update(cars=6,body_length_m=p['length_m'],body_width_m=p['width_m'])
    support_geometry=deepcopy(reference['physical_definition']['support']);support_geometry['bogie_centres_x_m']=[-6.4,6.4]
    v['physical_definition']=dict(vehicle=vehicle_geometry,support=support_geometry,
        source_body_candidate_id=body['candidate_id'],geometry_definition_id=identity(body['physical']['geometry']),
        body_stock=dict(definition_id=body['definition_id'],known_structure_stock_kg=body['known_structure_stock_kg'],complete_installed_mass_kg=None),
        body_material_ids=sorted({q['material_id'] for q in body['parts']}),
        roof=dict(located_stock_ids=[q['id'] for q in body['parts'] if q['id'].startswith('roof/')],hot_strength_qualified=False),
        equipment_inventory=[dict(id=q['id'],component_definition_id=q['component_definition_id'],accounted_mass_kg=q['mass_kg'],installed_geometry=None) for q in equipment],
        propulsion=dict(component_id=motor['motor_component_id'],physical_geometry=motor.get('physical_configuration'),
            removed_reference_secondary=family in ('P6','P7'),available_force_map=None),
        component_substitutions=substitutions,unweighed_architecture_equipment=unknown,complete_installed_geometry=False)
    v['axle_loads'].update(empty_kg_per_axle=tare/4,normal_kg_per_axle=(tare+3450)/4,crowd_control_kg_per_axle=(tare+12000)/4)
    rotor=braking.rotating_stock(reference)
    # Only unchanged running-gear solids enter the independent brake definition.
    # No source vehicle body geometry masquerades as the newly generated body.
    v['geometry_parts']=[q for q in reference['geometry_parts'] if q['id'].startswith('bogie/')]
    brake=braking.definition(v)
    value=dict(schema='osr-coupled-railway-bundle/1',candidate_id=case['candidate_id'],bundle_id=case['candidate_id'],
        body_candidate_id=body['candidate_id'],body_definition_id=body['definition_id'],support_component_id=reference['support_component_id'],
        propulsion_component_id=motor['motor_component_id'],family_id=family,cars=6,car_length_m=17.,coupling_gap_m=.5,
        architecture_case=case,architecture_specification=spec,motor_parameters=motor_parameters,motor_definition=motor,
        brake_definition=brake,mass={k:v['mass'][k] for k in ('accounted_tare_kg_per_car','accounted_cap_loaded_kg_per_car','accounted_160_control_kg_per_car')},
        mass_scope='Known gross body stock plus explicit retained equipment accounts; new architecture equipment and installed completeness remain unknown',
        retained_equipment_accounts=equipment,component_substitutions=substitutions,unweighed_architecture_equipment=unknown,
        rotating_equivalent_kg_per_car=rotor['equivalent_inertial_mass_kg_per_car'],rotor_definition_id=identity(rotor),
        physical_definition=v['physical_definition'],axle_loads=v['axle_loads'],requirements=case['requirements'],requirement_revision=case['requirement_revision'],
        known_body_stock_kg=body['known_structure_stock_kg'],normal_sprung_mass_hypothesis_kg=tare+3450.-6730.,
        crowd_sprung_mass_hypothesis_kg=tare+12000.-6730.,complete_installed_mass_kg=None,complete_installed_CG_m=None,complete_installed_inertia_kg_m2=None,
        source_sha256={**reference['source_sha256'],**body['sources'],PRODUCER:digest(root/PRODUCER)},
        reference_changed=False,physical_journey_completed=False,**FLAGS)
    value['definition_id']=identity(value);validate(value);return value


def validate(bundle):
    if bundle.get('definition_id')!=identity({k:v for k,v in bundle.items() if k!='definition_id'}):raise ValueError('Modified coupled bundle')
    c=bundle['architecture_case'];p=c['physical_definition']
    if bundle['candidate_id']!=bundle['bundle_id'] or bundle['candidate_id']!=c['candidate_id'] or c['candidate_id']!=identity(p):raise ValueError('Mixed physical railway composition')
    if p['retained_body_definition_id']!=bundle['body_candidate_id'] or bundle['motor_definition']['motor_component_id']!=bundle['propulsion_component_id']:raise ValueError('Mixed body/motor identities')
    if any(bundle['brake_definition'][k]!=bundle[k] for k in ('candidate_id','body_candidate_id','support_component_id','propulsion_component_id')):raise ValueError('Mixed brake definition identity')
    m=bundle['mass']
    if abs(m['accounted_cap_loaded_kg_per_car']-m['accounted_tare_kg_per_car']-3450)>1e-7 or abs(m['accounted_160_control_kg_per_car']-m['accounted_tare_kg_per_car']-12000)>1e-7:raise ValueError('Load policy and mass differ')
    if any(bundle.get(k) is not False for k in FLAGS) or bundle.get('complete_installed_mass_kg') is not None:raise ValueError('Research bundle cannot supply installed completeness or release')
    return bundle


def civil_proxy(bundle):
    validate(bundle)
    return dict(candidate_id=bundle['candidate_id'],body_candidate_id=bundle['body_candidate_id'],mass=deepcopy(bundle['mass']),
        physical_definition=deepcopy(bundle['physical_definition']),axle_loads=deepcopy(bundle['axle_loads']))


def assess_architecture(bundle):
    validate(bundle)
    return architecture.compact_result(architecture.screen(bundle['architecture_case'],bundle['mass']['accounted_cap_loaded_kg_per_car'],
        bundle['rotating_equivalent_kg_per_car'],bundle['architecture_specification']))


def assess_civil(bundle):
    v=civil_proxy(bundle)
    return dict(candidate_id=bundle['candidate_id'],body_candidate_id=bundle['body_candidate_id'],load_scope=bundle['mass_scope'],
        alternatives=[civil.alternative(v,20.,f,'crowd_control') for f in ('box-beam','twin-beam','u-beam')],
        complete_substructure_or_installation=False,**FLAGS)
