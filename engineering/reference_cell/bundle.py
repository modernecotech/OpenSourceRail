"""Bind a located equipped vehicle registry to one new physical railway cell.

Only the unchanged 20 m primary stock template is reused. Segmented secondaries,
wheel/axle/disc solids, body/support interfaces and bounded installed accounts
come from this vehicle registry. Old GFRP body/mass/brake identities are absent.
"""
from copy import deepcopy
from math import fsum, pi
from pathlib import Path
from engineering.station_rail import ROOT
from engineering.station_rail.common import identity,digest
from engineering.component_registry import validate_registry,summary
from engineering.design_search import railway_bundle,system_motion,capabilities,railway_architecture
from engineering.railway_twin import propulsion as primary_template
from . import architecture

PRODUCER='engineering/reference_cell/bundle.py'
FLAGS=dict(railway_bundle.FLAGS,selected_reference_changed=False)


def _part_rows(registry,first_car=True):
    definitions={p['physical_definition_id']:p for p in registry['parts']}
    return [(o,definitions[o['part_definition_id']]) for o in registry['occurrences']
        if not first_car or o['occurrence_id'].startswith('car-1/')]


def _physical_rows(rows):
    return [dict(occurrence_id=o['occurrence_id'].split('/',1)[-1],part_definition_id=p['physical_definition_id'],
        geometry=deepcopy(p['geometry']),transform=deepcopy(o['transform'])) for o,p in rows]


def _rotors(rows):
    counted=[];unknown=[];discs=[]
    for o,p in rows:
        name=p['part_id'].lower()
        if 'axle-bearing' in name:
            unknown.append(dict(occurrence_id=o['occurrence_id'],part_revision_id=p['revision_id'],rotating_fraction=None,I_axial_kg_m2=None))
            continue
        rotating=next((k for k in ('wheel-rim','wheel-web','friction-brake-disc','-axle-') if k in name),None)
        if rotating is None:
            if 'axle-bearing' in name:unknown.append(dict(occurrence_id=o['occurrence_id'],part_revision_id=p['revision_id'],rotating_fraction=None,I_axial_kg_m2=None))
            continue
        g=p['geometry'];d=g['dimensions_m'];rotation=[r[:3] for r in o['transform'][:3]]
        if g['kind'] not in ('cylinder','tube') or [rotation[i][2] for i in range(3)]!=[0.,1.,0.]:
            raise ValueError('Actual rotating stock must have a transverse cylindrical axis')
        mass=p['mass'];nominal=mass['calculated_kg']
        if nominal is None:raise ValueError('Counted rotating material needs calculated stock mass')
        outer=d.get('outer_radius',d.get('radius'));inner=d.get('inner_radius',0.);factor=.5*(outer*outer+inner*inner)
        row=dict(occurrence_id=o['occurrence_id'],part_definition_id=p['physical_definition_id'],part_revision_id=p['revision_id'],
            role=rotating,mass_kg=nominal,mass_lower_kg=mass['lower_bound_kg'],mass_upper_kg=mass['upper_bound_kg'],
            I_axial_kg_m2=nominal*factor,I_axial_bounds_kg_m2=[mass['lower_bound_kg']*factor,mass['upper_bound_kg']*factor])
        counted.append(row)
        if rotating=='friction-brake-disc':discs.append((o,p))
    counts={k:sum(r['role']==k for r in counted) for k in ('wheel-rim','wheel-web','friction-brake-disc','-axle-')}
    if counts!={'wheel-rim':8,'wheel-web':8,'friction-brake-disc':8,'-axle-':4} or len(unknown)!=8:
        raise ValueError('Eight counted wheel rims/webs/discs, four axles and eight unresolved bearings required per car')
    for o,p in discs:
        if p['geometry']['dimensions_m']!=dict(length=.018,outer_radius=.210,inner_radius=.080):
            raise ValueError('This new brake plant requires its actual .42m diameter/.018m disc geometry')
    radius=.320;I=fsum(r['I_axial_kg_m2'] for r in counted)
    result=dict(schema='osr-counted-wheel-inertia/1',radius_m=radius,parts=counted,I_kg_m2_per_car=I,
        equivalent_inertial_mass_kg_per_car=I/radius**2,counted_rotating_mass_kg_per_car=fsum(r['mass_kg'] for r in counted),
        I_bounds_kg_m2=[fsum(r['I_axial_bounds_kg_m2'][i] for r in counted) for i in range(2)],
        unresolved_rotating_equipment=unknown,complete_installed_rotational_inertia_kg_m2=None,
        static_axle_load_uses_equivalent_inertial_mass=False,
        scope='Actual nominal wheel/axle/disc solids only; rotating bearing/seal fractions and delivered inertias remain unknown')
    return result,discs


def materialize(vehicle,distance_m=2000.,propulsion='five-20m',guideway='box',root=ROOT):
    """Return a direct canonical bundle; do not mutate the vehicle/body registry."""
    root=Path(root)
    if digest(root/PRODUCER)!=digest(__file__):raise ValueError('Executing bundle adapter differs from declared source root')
    if any(digest(root/name)!=sha for name,sha in vehicle.get('source_sha256',{}).items()):raise ValueError('Equipped vehicle source epoch is stale')
    if distance_m not in (1500.,2000.):raise ValueError('Explicit1.5/2km physical route required')
    if vehicle.get('schema')!='osr-equipped-reference-cell-vehicle/1' or vehicle.get('evaluation_id')!=identity({k:v for k,v in vehicle.items() if k!='evaluation_id'}):
        raise ValueError('Exact current equipped-vehicle result required')
    registry=vehicle['registry'];validate_registry(registry)
    if vehicle['candidate_id']!=registry['candidate_id']:raise ValueError('Mixed equipped body/registry identity')
    req=vehicle['requirements']
    if any(req.get(k)!=v for k,v in dict(cars=6,car_length_m=17.,fixed_seats_per_car=44,wheelchair_places_per_car=2,axle_count_per_car=4,wheel_count_per_car=8,powered_bogies=0,traction_batteries=0).items()):
        raise ValueError('Explicit six-car passive 17m comfort equipment required')
    catalogue=architecture.defaults();drive=catalogue.get('propulsion',propulsion);civil=catalogue.get('guideway',guideway)
    if drive['parameters']['method']!='LIM' or drive['parameters']['bank_length_m']!=20.:
        raise ValueError('Registered architecture has no owned complete motor adapter yet: retain the unsupported architecture/evidence task rather than reuse20m LIM hardware')
    choices=dict(body=vehicle['vehicle_id'],running_gear='passive')
    rows=_part_rows(registry);support_rows=[(o,p) for o,p in rows if o['scope'] in ('vehicle/running-gear','vehicle/bogie-interfaces')]
    support_geometry=dict(schema='osr-located-passive-bogie-assembly/1',parts=_physical_rows(support_rows),
        interfaces=deepcopy(vehicle['interfaces']),wheel_new_diameter_m=.64,bogies_per_car=2,axles_per_bogie=2,drive_motors=0)
    support_id=identity(support_geometry)
    rotor,disc_rows=_rotors(rows)
    fins=[(o,p) for o,p in rows if 'passive-aluminium-fin' in p['part_id'].lower()]
    if len(fins)!=3 or any(p['geometry']['kind']!='box' or p['geometry']['dimensions_m']!=[2.98,.012,.30] for o,p in fins):
        raise ValueError('Actual three2.98m segmented aluminium secondaries required')
    bottom=min(o['transform'][2][3]-.15 for o,p in fins)
    template=primary_template.materialize();parameters=deepcopy(template['parameters']);original=template['parameters']['physical'];new=parameters['physical']
    # Slot/winding/backiron dimensions stay unchanged; fin replacement/alignment
    # is a new geometry outside the retained single-fin field evaluator domain.
    new.update(name='segmented-secondary-reference-cell',secondary_length_m=2.98,secondary_thickness_m=.012,
        secondary_bottom_TOR_m=bottom,secondary_height_m=.30,secondary_segment_count=3,
        secondary_segment_geometry=_physical_rows(fins))
    physical_motor=dict(primary_parameters={k:v for k,v in original.items() if not k.startswith('secondary_') and k!='name'},
        secondary_coordinate_frame='one-car-local:rearx0,frontx17,positive-directionx;occurrences positioned by vehicle train-local registry',
        primary_coordinate_frame='one-bank-local:x0..20 transformed by route bank start;globalz=rail-top',
        primary_bottom_TOR_m=bottom,primary_gap_each_side_m=.015,secondary_segments=_physical_rows(fins),
        primary_activation_layout=deepcopy(drive['parameters']))
    motor_id=identity(physical_motor)
    primary=[]
    for old in template['wayside_stock']:
        p=deepcopy(old);side=1 if p['at_m'][1]>=0 else -1
        p['at_m'][1]+=side*(.012-original['secondary_thickness_m'])/2
        p['at_m'][2]+=bottom-original['secondary_bottom_TOR_m']
        p['cg_m']=[a+s/2 for a,s in zip(p['at_m'],p['size_m'])]
        p['motor_component_id']=motor_id;primary.append(p)
    definition=dict(schema='osr-segmented-passive-secondary-definition/1',motor_component_id=motor_id,
        physical_configuration=new,physical_composition=physical_motor,available_force_map=None,
        primary_template_geometry_id=template['motor_definition']['motor_component_id'],
        bare_primary_stock_kg_per_bank=fsum(p['mass_kg'] for p in primary),bare_primary_stock_kg_per_m=fsum(p['mass_kg'] for p in primary)/20.,
        source_winding_geometry_unchanged=True,segmented_secondary_field_model_supported=False,
        operating_evidence_inherited=False,actual_converter_or_cooling_defined=False,
        limitations=['Segmented full-height plates and their entry/exit/gaps/return paths need a new moving 3D/validated reduced evaluator',
            'Retained field samples and winding electrical headroom cannot be transferred to these new secondaries',
            'Primary relocation, fin supports and civil clearances require interference/load verification'],**FLAGS)
    bank=drive['parameters'];starts=[float(x) for x in bank['bank_starts_m']];L=float(bank['bank_length_m'])
    length=104.5;requirements=dict(base_revision='REFERENCE-CELL-EQUIPPED-1',cars=6,passengers_per_car=46,crowd_control_per_car=160,
        capacity_pphpd=8280.,speed_cap_m_s=20.,acceleration_m_s2=.4,service_deceleration_m_s2=.6,dwell_s=35.,target_headway_s=120.,
        mandatory=['passenger-protection','independent-braking','accessibility','protected-recovery'])
    revision=identity(requirements)
    physical=dict(schema='osr-railway-architecture-physical/1',retained_body_definition_id=registry['candidate_id'],
        retained_support_reference_id=support_id,propulsion_definition_id=motor_id,
        formation=dict(cars=6,car_length_m=17.,coupling_gap_m=.5,train_length_m=length,seats_per_car=44,wheelchair_places_per_car=2),
        route=dict(station_spacing_m=float(distance_m),tracks=1,stations=2,geometry_scope='New two-station directional reference cell; site/survey remains absent'),
        guideway=dict(family=guideway,parameters=deepcopy(civil['parameters'])),
        wayside=dict(motor_family=bank['method'],reference_motor_definition_id=motor_id,
            primary_layout_name=propulsion,bank_starts_from_initial_nose_m=starts,bank_length_m=L,
            installed_linear_track_intervals_per_leg_m=[[x,x+L] for x in starts],
            primary_geometry_definition=physical_motor,receiving_zone_geometry=None,converter_and_feeder_definition=None,
            scope='Launch primary geometry only; receiving apparatus and complete supply/protection remain unresolved'),
        onboard=dict(drive='unmaterialized-recovery-drive' if bank['onboard_traction'] else 'none',driven_axle_count=None if bank['onboard_traction'] else 0,
            supply='auxiliary-only',recovery_traction_equipment=None,passive_secondary_segments=_physical_rows(fins)),
        complete_installed_geometry=False)
    physical['formation'].update(train_registry_frame=dict(origin='trailing end of car1',leading_nose_train_local_x_m=104.5,leading_car_index=5,positive_travel_axis='x'),
        train_local_to_route_at_front_zero=[[1.,0.,0.,-104.5],[0.,1.,0.,0.],[0.,0.,1.,0.],[0.,0.,0.,1.]])
    candidate=identity(physical)
    # Commands are explicit controller requests; installed lengths/overlaps are
    # separate geometry and never imply any available train force.
    command_windows=[[0.,min(500.,float(distance_m))]] if bank['method'].startswith('LIM') else []
    case=dict(schema='osr-railway-architecture-case/1',candidate_id=candidate,physical_definition=physical,family_id='P1',
        requirement_revision=revision,requirements=requirements,capability_composition=capabilities.composition('P1',candidate,revision),
        commanded_power_windows_m=command_windows,generation=0,parent_case_ids=[],reference_candidate_id=None,
        complete_mass_kg=None,complete_CG_m=None,complete_inertia_kg_m2=None,**FLAGS)
    case['case_id']=identity(case)
    totals=summary(registry);upper=totals['mass_upper_bound_kg'] if 'mass_upper_bound_kg' in totals else vehicle['train_mass_properties']['mass_upper_bound_kg']
    # Registry summary is authoritative; derived per-car properties are checked
    # against it, never borrowed from an unrelated reference body.
    lower=totals['mass_lower_bound_kg'] if 'mass_lower_bound_kg' in totals else vehicle['train_mass_properties']['mass_lower_bound_kg']
    if lower is None or upper is None or lower<=0 or upper<lower:raise ValueError('Every proposed item needs an explicit finite mass interval before a conservative vehicle load can be formed')
    tare=upper/6.;mass=dict(accounted_tare_kg_per_car=tare,accounted_cap_loaded_kg_per_car=tare+3450.,accounted_160_control_kg_per_car=tare+12000.)
    brake_geometry_id=identity(_physical_rows([(o,p) for o,p in rows if 'brake' in p['part_id'].lower()]))
    brake=dict(schema='osr-wheel-brake-research-definition/1',candidate_id=candidate,body_candidate_id=registry['candidate_id'],support_component_id=support_id,propulsion_component_id=motor_id,
        physical_brake_geometry_id=brake_geometry_id,rotors=rotor,discs_per_car=8,counted_disc_stock_kg_per_car=fsum(p['mass']['calculated_kg'] for o,p in disc_rows),
        pad_outer_radius_m=.210,pad_inner_radius_m=.080,effective_friction_radius_m=2/3*(.210**3-.080**3)/(.210**2-.080**2),
        opposed_pistons_per_caliper_hypothesis=2,piston_diameter_m_hypothesis=.10,maximum_pressure_Pa_hypothesis=.6e6,pad_friction_coefficient_hypothesis=.35,
        pressure_response_delay_s_hypothesis=1.,pressure_rise_time_s_hypothesis=.4,steel_specific_heat_J_kg_K_hypothesis=500.,ambient_C_hypothesis=50.,
        parameter_provenance='New explicit unvalidated actuator/pad/response engineering hypotheses; not inherited force/fade/test evidence',
        supplier_friction_or_fade_curve=None,actual_caliper_force_pressure_curve=None,actual_WSP_qualified=False,
        installed_hardware_qualified=False,brake_safety_floor_m_s2=None,**FLAGS)
    brake['brake_definition_id']=identity(brake)
    source={**vehicle['source_sha256'],PRODUCER:digest(root/PRODUCER),primary_template.PRODUCER:digest(root/primary_template.PRODUCER),
        railway_bundle.PRODUCER:digest(root/railway_bundle.PRODUCER),'engineering/reference_cell/architecture.py':digest(root/'engineering/reference_cell/architecture.py')}
    all_rows=_part_rows(registry,first_car=False)
    route_axles=[dict(occurrence_id=o['occurrence_id'],offset_behind_leading_nose_m=104.5-o['transform'][0][3],
        train_local_transform=deepcopy(o['transform'])) for o,p in all_rows if '-axle-' in p['part_id'].lower() and 'axle-bearing' not in p['part_id'].lower()]
    route_fins=[]
    for o,p in all_rows:
        if 'passive-aluminium-fin' not in p['part_id'].lower():continue
        pose=deepcopy(o['transform']);pose[0][3]-=104.5
        route_fins.append(dict(occurrence_id=o['occurrence_id'],part_definition_id=p['physical_definition_id'],geometry=deepcopy(p['geometry']),
            transform_at_leading_front_zero=pose,dynamic_translation_m='[front_displacement_m,0,0]'))
    if len(route_axles)!=24 or len(route_fins)!=18:raise ValueError('Exact24axle/18segment route-frame mapping required')
    result=dict(schema='osr-coupled-railway-bundle/1',candidate_id=candidate,bundle_id=candidate,body_candidate_id=registry['candidate_id'],
        body_definition_id=registry['registry_id'],body_evaluation_id=vehicle['evaluation_id'],support_component_id=support_id,
        propulsion_component_id=motor_id,family_id='P1',cars=6,car_length_m=17.,coupling_gap_m=.5,architecture_case=case,
        architecture_specification=dict(scenario=dict(car_length_m=17.,coupling_gap_m=.5)),motor_parameters=parameters,motor_definition=definition,wayside_primary_stock=primary,
        brake_definition=brake,mass=mass,mass_interval_kg_per_car=[lower/6.,upper/6.],
        mass_scope='Conservative registry upper bound for declared purchased envelopes and calculated solids; not a weighed or fully installed vehicle',
        retained_equipment_accounts=[],component_substitutions=[],unweighed_architecture_equipment=['Undelivered equipment, actual routings/tolerances/attachments and undefined receiving/supply/cooling equipment'],
        rotating_equivalent_kg_per_car=rotor['equivalent_inertial_mass_kg_per_car'],rotor_definition_id=identity(rotor),
        physical_definition=dict(vehicle=dict(cars=6,body_length_m=17.,body_width_m=req['car_width_m'],
                train_local_to_route_at_front_zero=deepcopy(physical['formation']['train_local_to_route_at_front_zero']),leading_car_index=5),support=support_geometry,
            body_registry_candidate_id=registry['candidate_id'],body_registry_revision_id=registry['registry_id'],
            propulsion=dict(component_id=motor_id,physical_geometry=new,available_force_map=None),complete_installed_geometry=False),
        axle_loads=dict(empty_kg_per_axle=tare/4,normal_kg_per_axle=(tare+3450)/4,crowd_control_kg_per_axle=(tare+12000)/4),
        requirements=requirements,requirement_revision=revision,complete_installed_mass_kg=None,complete_installed_CG_m=None,complete_installed_inertia_kg_m2=None,
        route_axle_offsets_from_leading_nose_m=route_axles,route_secondary_segments_at_front_zero_m=route_fins,
        mass_registry_revision_id=registry['registry_id'],available_force_map=None,source_sha256=source,reference_changed=False,physical_journey_completed=False,**FLAGS)
    result['definition_id']=identity(result)
    railway_bundle.validate(result);system_motion._bundle(result)
    return result
