"""Matched design interfaces and necessary bounds for the comfort train.

This dossier derives requirements from the supplied vehicle and service. It
does not silently import the old body, old L-return rails or a guaranteed
braking model. Component field samples remain exact samples: they are neither
confidence bounds nor a new installed force map.
"""
from copy import deepcopy
from functools import lru_cache
from hashlib import sha256
import json
import math
from pathlib import Path
import re
import tarfile
import tomllib

from engineering.comfort_options import systems
from engineering.vehicle_optimisation import hvac
from . import ROOT, FLAGS

SCHEMA='osr-comfort-design-interfaces/1'
THERMAL='docs/design-engine/ferrite-maglev/engineering-readiness/thermal-artifacts.tar.gz'
THERMAL_SHA='3ab5bc0f22d36e73417070d4814d0c4f828dae6add89c5fbd73bf957b85bcabd'
BRIEF='engineering/comfort_design/brief.json'
GRAVITY=9.80665
MODULES=24
CARS=6


def encoded(value):
    return (json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False)+'\n').encode()


def identity(value):return sha256(encoded(value)).hexdigest()


def _number(value,name,minimum=0.):
    if type(value) not in (int,float) or not math.isfinite(value) or value<minimum:
        raise ValueError('finite '+name+' >= '+str(minimum)+' required')
    return float(value)


def _check_sources(root,bindings):
    for name,digest in bindings.items():
        p=Path(name)
        if p.is_absolute() or '..' in p.parts or not re.fullmatch('[a-f0-9]{64}',digest):
            raise ValueError('ordinary source mapping required')
        path=Path(root)/p
        if path.is_symlink() or not path.is_file() or sha256(path.read_bytes()).hexdigest()!=digest:
            raise ValueError('interface input source differs: '+name)


@lru_cache(maxsize=4)
def _thermal(root_name):
    root=Path(root_name);path=root/THERMAL
    raw=path.read_bytes()
    if sha256(raw).hexdigest()!=THERMAL_SHA:raise ValueError('immutable winding/HVAC package differs')
    with tarfile.open(path,'r:gz') as archive:
        data={}
        for name in ('result.json','manifest.json'):
            member=archive.getmember('thermal/'+name)
            if not member.isfile() or member.size>8_000_000:raise ValueError('bounded ordinary thermal member required')
            data[name]=archive.extractfile(member).read()
    value=json.loads(data['result.json']);receipt=json.loads(data['manifest.json'])
    if receipt['files_sha256']['result.json']!=sha256(data['result.json']).hexdigest():raise ValueError('thermal member differs')
    _check_sources(root,value['source_sha256'])
    return value


def thermal_evidence(root=ROOT):
    root=Path(root).resolve();value=_thermal(str(root))
    if sha256((root/THERMAL).read_bytes()).hexdigest()!=THERMAL_SHA:raise ValueError('thermal package changed')
    _check_sources(root,value['source_sha256'])
    return deepcopy(value)


def _subject(vehicle,service,root):
    if not isinstance(vehicle,dict):raise ValueError('explicit generated vehicle record required')
    for key in ('candidate_id','body_candidate_id','magnet_component_id'):
        if not re.fullmatch('[a-f0-9]{64}',vehicle.get(key,'')):raise ValueError('explicit '+key+' required')
    if vehicle.get('evaluation_id')!=identity({k:v for k,v in vehicle.items() if k!='evaluation_id'}):
        raise ValueError('vehicle evaluation identity differs')
    physical=vehicle['physical_definition']
    if identity(physical)!=vehicle['candidate_id'] or identity(physical['body'])!=vehicle['body_candidate_id']:
        raise ValueError('vehicle physical/body identity differs')
    if physical['magnet_component_id']!=vehicle['magnet_component_id'] or physical['body_candidate_id']!=vehicle['body_candidate_id']:
        raise ValueError('vehicle physical component identities differ')
    if (physical['cars'],physical['fixed_seats_per_car'],physical['wheelchair_places_per_car'],physical['planned_standing_per_car'])!=(6,44,2,0):
        raise ValueError('explicit six-car comfort configuration differs')
    mounts=physical['module_mounts']
    if len(mounts)!=24 or sorted(set(round(m['translation_m'][1],8) for m in mounts))!=[-.88,.88] or any(m['translation_m'][2]!=-1.16 or m['facing_normal']!=[0.,0.,1.] for m in mounts):
        raise ValueError('guideway interface needs new mounting geometry')
    if vehicle['magnet_component_id']!=systems.MAGNET_ID:raise ValueError('current interface evidence belongs to another magnetic component')
    if vehicle.get('installed_mass_complete') is not False:raise ValueError('complete installed mass is not established by this dossier')
    tare=_number(vehicle['mass']['accounted_tare_kg_per_car'],'accounted tare',1.)
    loaded=_number(vehicle['mass']['accounted_cap_loaded_kg_per_car'],'accounted cap mass',1.)
    if not math.isclose(tare,math.fsum(r['mass_kg'] for r in vehicle['inventory']),abs_tol=1e-6):
        raise ValueError('vehicle inventory and accounted mass differ')
    if not math.isclose(loaded,tare+46*75.,abs_tol=1e-8):raise ValueError('46-person cap and passenger mass do not match vehicle')
    if vehicle['mass'].get('installed_tare_kg_per_car') is not None:raise ValueError('unqualified installed-mass substitution')
    _check_sources(root,vehicle['source_sha256'])
    if service is not None:
        if any(service.get(k)!=vehicle[k] for k in ('candidate_id','body_candidate_id','magnet_component_id')):raise ValueError('service belongs to another physical vehicle')
        _check_sources(root,service['source_sha256'])
    return tare,loaded


def _sources(root,vehicle,service,parent,thermal):
    result={}
    for record in (vehicle,parent,thermal,service or {}):
        for name,digest in record.get('source_sha256',{}).items():
            if name in result and result[name]!=digest:raise ValueError('mixed interface sources: '+name)
            result[name]=digest
    for name in (BRIEF,'engineering/vehicle_optimisation/hvac.py',
                 'engineering/comfort_options/systems.py',
                 'engineering/ferrite_maglev/candidate-structures.toml',
                 'engineering/ferrite_maglev/data/candidate-protection-equipment.json',
                 'engineering/ferrite_maglev/booster-kit.toml',
                 'engineering/ferrite_maglev/booster_kit.py',
                 'engineering/ferrite_maglev/stopped_recovery.py',
                 'ferrite-maglev-study.toml'):
        result[name]=sha256((root/name).read_bytes()).hexdigest()
    result[THERMAL]=THERMAL_SHA
    result['engineering/comfort_design/interfaces.py']=sha256(Path(__file__).read_bytes()).hexdigest()
    return dict(sorted(result.items()))


def winding_requirements(winding):
    if winding['candidate_id']!=systems.MAGNET_ID:raise ValueError('winding component mismatch')
    R=winding['R80_known_copper_ohm_per_module']
    rows=[]
    for current in (5.,10.,15.):
        heat=current**2*R
        rows.append(dict(RMS_current_A_hypothesis=current,known_copper_loss_W_per_module=heat,
            known_copper_loss_kW_per_car=MODULES*heat/1000.,known_copper_loss_kW_six_cars=CARS*MODULES*heat/1000.,
            minimum_copper_to_50C_ambient_conductance_W_K_per_module=heat/30.,
            copper_temperature_comparison_C=80.,actual_heat_rejection_W=None,
            RMS_operating_duty_demonstrated=False,whole_assembly_thermal_equilibrium_C=None))
    return dict(component_id=winding['candidate_id'],physical_circuit_scope=winding['generalized_port_scope'],
        copper_material_mass_kg_per_module=winding['copper_material_mass_kg_per_module'],
        R20_known_copper_ohm_per_module=winding['R20_known_copper_ohm_per_module'],
        R80_known_copper_ohm_per_module=R,declared_current_density_limit_A_per_mm2=3.75,
        maximum_sampled_common_current_A=15.,source_common_port_samples=deepcopy(winding['samples']),
        repeated_duty_sensitivities=rows,lead_converter_and_bus_losses_known=False,
        actual_driver_voltage_V=None,driver_rating_and_nonlinear_current_map_known=False,
        scope='Copper arithmetic from the same two physical circuits; no new 3D current source or stabilizing control law.',
        required_interfaces=['Two separately identified current-regulated winding channels per module',
            'Independent isolated gap sensing, synchronized current telemetry and local temperature sensing',
            'Protected onboard supply and positive-retention leads with fault isolation',
            'Measured 3D force/moment/current/gap maps, mutual inductance and verified control reserve',
            'A measured thermal path including contacts, backing, carrier, convection and stationary 50C air'],
        actual_stable_hover_established=False,**FLAGS)


def _heat_case(passengers,humid,solar,door_cycle_s,construction):
    """Adapt the retained thermal equations to the explicitly changed panels.

    Roof/floor skins use a declared aluminium conductivity; core conductivities
    are room-temperature producer values. New rails/fasteners remain a separate
    thermal-bridge uncertainty rather than an invented zero penalty.
    """
    s=hvac.default_scenario(name='comfort-50C-'+('humid' if humid else 'dry'),
        passengers=passengers,outdoor_RH=.30 if humid else .15,
        glazing_m2=26.,solar_factor=solar,glazing_U_W_m2K=5.7,
        door_open_s=60. if humid else 30.,door_cycle_s=door_cycle_s,doors_open=2)
    load=hvac.heat_load(s);delta=s['outdoor_C']-s['indoor_C']
    area=17.*2.65;alpha_Al=160. # W/m/K comparison hypothesis, not a batch measurement.
    old_roof_U=load['upper_panel_U_W_m2K']
    rt,rc=construction['roof_skin_m'],construction['roof_core_m']
    ft,fc=construction['floor_skin_m'],construction['floor_core_m']
    new_roof_U=1/(.17+2*rt/alpha_Al+rc/.029)
    old_floor_U=1/(.17+.0045/.3+.06/.033)
    new_floor_U=1/(.17+2*ft/alpha_Al+fc/.031)
    correction=(2*1.4*2.1)*(old_roof_U-2.5)*delta
    floor_correction=area*(new_floor_U-old_floor_U)*delta
    load['sensible_components_W']['opaque_shell']+=correction+floor_correction
    load['sensible_components_W']['roof']=area*new_roof_U*(load['roof_solair_temperature_C']-s['indoor_C'])
    roof_q=load['sensible_components_W']['roof']/area
    core_hot=load['roof_solair_temperature_C']-roof_q*(1/s['outside_film_W_m2K']+rt/alpha_Al)
    roof_beta=(1/s['outside_film_W_m2K']+rt/alpha_Al)*new_roof_U
    maximum_solair=(70.-s['indoor_C']*roof_beta)/(1-roof_beta)
    maximum_absorptivity=(maximum_solair-s['outdoor_C'])*s['outside_film_W_m2K']/s['roof_solar_W_m2']
    sensible=max(0.,sum(load['sensible_components_W'].values()))
    latent=max(0.,sum(load['latent_components_W'].values()))
    load.update(sensible_kWthermal=sensible/1000.,total_kWthermal=(sensible+latent)/1000.,
        complete_HVAC_electric_kWe=None,actual_hot_condition_electrical_input_kWe=None,
        thermal_construction=dict(roof_faces_m=rt,roof_H60_core_m=rc,roof_core_lambda_W_mK=.029,
            floor_faces_m=ft,floor_H80_core_m=fc,floor_core_lambda_W_mK=.031,
            aluminium_lambda_W_mK_hypothesis=alpha_Al,new_roof_U_W_m2K=new_roof_U,
            new_floor_U_W_m2K=new_floor_U,removed_door_infill_opaque_correction_W=correction,
            floor_conduction_correction_W=floor_correction,new_rail_and_frame_bridge_UA_W_K=None,
            panel_point_bridges_and_actual_hot_properties_qualified=False,
            roof_outer_core_temperature_C_hypothesis=core_hot,core_continuous_temperature_limit_C=70.,
            necessary_hot_core_screen='pass' if core_hot<=70 else 'fail',
            maximum_roof_solar_absorptivity_for70C_core_hypothesis=maximum_absorptivity,
            reflective_finish_design_target_solar_absorptivity_max=.30,
            actual_aged_finish_absorptivity_and_coating_mass_known=False),
        door_recurrence_equals_line_headway=False,glazing_optical_values_are_sensitivities=True)
    return load


def thermal_requirements(thermal,vehicle,service=None):
    package=next(p for p in thermal['hvac']['packages'] if p['units_per_car']==5)
    roof=vehicle['components']['roof_revision']['selected']['physical_definition']
    floor=vehicle['components']['floor']['physical_definition']
    construction=dict(roof_skin_m=roof['skin_each_m'],roof_core_m=roof['core_m'],floor_skin_m=floor['skin_m'],floor_core_m=floor['core_m'])
    cycles=sorted({180.,240.}|{c['profile']['runtime_s']+c['inputs']['dwell_s'] for c,_ in _selected_cases(service)})
    cases=[]
    for passengers in (46,160):
        for humid in (False,True):
            for g in (.35,.55,.75):
                for cycle in cycles:
                    load=_heat_case(passengers,humid,g,cycle,construction)
                    needed=load['total_kWthermal']
                    cases.append(dict(passengers_total=passengers,humid=humid,door_cycle_s=cycle,
                        door_open_s=60. if humid else 30.,solar_factor_g_hypothesis=g,load=load,
                        installed_units=5,normal_required_50C_kWthermal_each=needed/5.,
                        N_minus_1_required_50C_kWthermal_each=needed/4.,
                        nominal_5unit_screen='pass' if needed<=165. else 'fail',
                        nominal_N_minus_1_screen='pass' if needed<=132. else 'fail',
                        actual_50C_normal_and_N_minus_1_screen='unknown',actual_COP_and_real_power_known=False))
    hvac_electrical=[]
    for phases,factor in (('single-phase hypothetical',1.),('balanced three-phase hypothetical',math.sqrt(3))):
        hvac_electrical.append(dict(supply_interpretation=phases,supplier_phase_count_known=False,
            five_compressor_maximum_apparent_kVA=5*400*24*factor/1000.,
            five_compressor_simultaneous_start_apparent_kVA=5*400*120*factor/1000.,
            one_start_four_running_apparent_kVA=(120+4*24)*400*factor/1000.,
            power_factor=None,actual_50C_compressor_kWe=None,
            phase_interpretation_selected=False))
    return dict(package_reference=deepcopy(package),cases=cases,
        electrical_supply_bounds=hvac_electrical,
        LV_regular_26V_kWe_per_car=2.6,LV_maximum_26V_kWe_per_car=11.7,
        fresh_air_cabin_requirement_m3_h_46persons=46*6*3.6,
        fresh_air_cabin_requirement_m3_h_160control=160*6*3.6,
        fresh_air_delivery_and_50C_capacity_known=False,
        compressor_start_requirement='Coordinate starts and preserve essential supply; sequences and bus ratings require actual phase/current/drive data.',
        nominal_roof_length_layout=dict(units=5,unit_length_m=2.655,unit_width_m=2.083,
            declared_between_unit_gap_m=.30,length_plus_four_gaps_m=5*2.655+4*.30,
            car_roof_length_m=17.,roof_width_m=2.65,declared_lateral_margin_each_m=.25,
            package_width_plus_margins_m=2.083+2*.25,actual_maintenance_clearance_and_recirculation_known=False),
        core_continuous_temperature_limit_C=70.,actual_solar_loaded_core_temperature_C=None,
        roof_coating_and_HVAC_heat_rejection_interaction_known=False,**FLAGS)


def _selected_cases(service):
    if service is None:return []
    selection=service['selection'];pairs=list(selection.get('shortlist',[]))
    if selection.get('selected_scenario_id') is None and selection.get('selected_station_id') is None:return []
    chosen=dict(scenario_id=selection['selected_scenario_id'],station_id=selection['selected_station_id'])
    pairs=[chosen]+[p for p in pairs if p!=chosen]
    seen=set();result=[]
    for pair in pairs:
        key=(pair['scenario_id'],pair['station_id'])
        if key in seen:continue
        seen.add(key)
        case=next((r for r in service['scenarios'] if r['scenario_id']==key[0]),None)
        if case is None:raise ValueError('selected service scenario missing')
        station=next((r for r in case['motor_zone_options'] if r['station_id']==key[1]),None)
        if station is None:raise ValueError('selected station geometry missing')
        result.append((case,station))
    return result


def station_requirements(loaded_kg,service,winding):
    train=CARS*_number(loaded_kg,'loaded per-car mass',1.)
    rows=[]
    for case,station in _selected_cases(service):
        s,p=case['inputs'],case['profile'];v=p['peak_speed_m_s'];arrival=p['arrival_speed_before_braking_m_s']
        a=s['acceleration_m_s2'];b=s['deceleration_m_s2'];C=s['constant_drag_N_per_car'];Q=s['quadratic_drag_N_per_car_per_m_s_squared']
        E=.5*train*v*v;arrival_E=.5*train*arrival*arrival
        runtime=p['runtime_s'];dwell=s['dwell_s'];headway=s['headway_s']
        drive_force=train*a+CARS*(C+Q*v*v)
        brake_force=max(0.,train*b-CARS*(C+Q*arrival*arrival))
        launch_work=p['launch_mechanical_kWh_per_train']*3.6e6
        coast_work=p['coast_drag_work_kWh_per_train']*3.6e6
        brake_drag=p['brake_drag_work_kWh_per_train']*3.6e6
        receive_work=p['theoretically_recoverable_mechanical_kWh_per_train']*3.6e6
        row=dict(scenario_id=case['scenario_id'],station_id=station['station_id'],
            inputs=deepcopy(s),peak_speed_m_s=v,receiving_entry_speed_m_s=arrival,runtime_s=runtime,headway_s=headway,
            shared_station_winding_length_m=station['length_m'],winding_start_m=station['start_m'],winding_end_m=station['end_m'],
            full_engagement_geometry=station['geometry_full_engagement'],
            two_direction_station_winding_subtotal_m=station['installed_direction_metres'],
            two_direction_motor_face_subtotal_m=station['installed_motor_face_metres'],
            sections_per_direction=station['sections_per_direction'],electrical_section_m=station['electrical_section_m'],
            minimum_independent_train_current_phase_branches_per_direction=station['minimum_concurrent_train_phase_current_branches_per_direction'],
            minimum_independent_train_current_phase_branch_sets_both_directions=2*station['minimum_concurrent_train_phase_current_branches_per_direction'],
            independently_addressed_sections_both_directions=2*station['sections_per_direction'],
            logical_3phase_to_two_bank_routing_paths_both_directions=2*station['sections_per_direction']*3*2,
            section_router_device_count_current_voltage_mass_and_cost=None,
            power_routing_requirement='Mutually exclusive isolated section ownership; synchronized phase/current banks for two trains, positive identified full-tail clearance, fail-open isolation and independently protected essential controls.',
            independently_sized_launch_plus_receiving_lengths_assumed=False,
            accounted_train_mass_kg=train,launch_peak_kinetic_energy_J=E,arrival_kinetic_energy_J=arrival_E,
            launch_mechanical_energy_kWh=p['launch_mechanical_kWh_per_train'],
            coast_drag_energy_kWh=p['coast_drag_work_kWh_per_train'],
            receiving_mechanical_energy_kWh=p['theoretically_recoverable_mechanical_kWh_per_train'],
            required_launch_train_force_N_at_peak_speed=drive_force,
            required_receiving_train_force_N_at_entry=brake_force,
            required_peak_train_mechanical_kW_from_overlap_model=station['required_peak_train_mechanical_kW'],
            required_force_density_N_per_active_band_m=station['force_density_requirement_N_m'],
            required_peak_force_per_equivalent_fully_engaged_car_N=station['required_peak_force_per_fully_engaged_car_N'],
            launch_endpoint_mechanical_kW=drive_force*v/1000.,
            receiving_entry_mechanical_kW=brake_force*arrival/1000.,
            simultaneous_two_train_absolute_endpoint_power_kW_per_direction=(drive_force*v+brake_force*arrival)/1000.,
            mechanical_launch_average_kW_direction=(3600/headway)*p['launch_mechanical_kWh_per_train'],
            normal_receiving_resistor_average_kW_direction=receive_work/headway/1000.,
            launch_to_receiving_energy_residual_J=launch_work-receive_work-(launch_work-E)-coast_work-brake_drag,
            coast_kinetic_balance_residual_J=E-arrival_E-coast_work,
            force_at_actual_position_speed_phase_current_temperature=None,
            dynamic_installed_motor_force_credit_N=None,guaranteed_power_loss_braking_force_N=None,
            bus_voltage_current_grouping_copper_temperature_and_installed_cost=None,
            normal_receiving_dump_requirement=dict(absorbed_mechanical_energy_J=receive_work,
                initial_endpoint_peak_mechanical_kW=brake_force*arrival/1000.,
                active_section_endpoint_concentration_known=False),
            independent_full_speed_fault_stop_requirement=dict(initial_kinetic_energy_J=E,
                source_of_force='Independent onboard brake/capture proposal; actual grade/drag/contact and guaranteed deployment remain unknown',
                receiving_stator_power_available_assumed=False),
            regenerative_energy_credit_kWh=0.,regeneration_credit_scope='No accepted common-DC link, accepting load or backup converter; no saving is credited.',
            direct_grid_power_at_launch_known=False,hotel_charging=[])
        for hvac_kW in (20.,40.,60.):
            copper=winding['repeated_duty_sensitivities'][-1]['known_copper_loss_kW_per_car']
            hotel_per_car=hvac_kW+copper+2.+2.6
            energy_train=hotel_per_car*CARS*(runtime+dwell)/3600.
            for charge in (20.,30.,45.):
                row['hotel_charging'].append(dict(HVAC_real_kWe_per_car_hypothesis=hvac_kW,
                    support_RMS_current_A_hypothesis=15.,other_essential_kWe_per_car_hypothesis=2.,
                    LV_HVAC_regular_kWe_per_car_hypothesis=2.6,
                    actual_complete_hotel_kWe_per_car=None,hotel_kWe_per_car_hypothesis=hotel_per_car,
                    same_car_door_to_door_cycle_s=runtime+dwell,hotel_energy_kWh_train=energy_train,
                    charge_window_s_hypothesis=charge,charge_window_fits_declared_dwell=charge<=dwell,
                    charger_efficiency_hypothesis=.9,input_charge_peak_kW=energy_train*3600/(charge*.9),
                    input_station_average_kW_direction=energy_train*3600/(headway*.9),
                    battery_usable_fraction_hypothesis=.8,
                    minimum_nominal_pack_kWh_car_for_one_leg=energy_train/CARS/.8,
                    phase_power_and_support_duty_demonstrated=False,charge_hardware_installed=False))
        rows.append(row)
    return dict(cases=rows,service_evaluation_id=None if service is None else service['evaluation_id'],
        source_force_reference_transferred_to_other_speed_or_geometry=False,
        coupled_grid_converter_storage_and_protection_design_complete=False,
        scope='Required mechanical force/energy from the selected drag-and-coast trajectory and explicit hotel-load scenarios; no executed moving electromagnetic plant or actual supplier bus rating.',**FLAGS)

def civil_design(accounted_tare_kg):
    """Dimension and count new passive faces, risers and brake/capture surfaces.

    Reuses the existing beam-top datum -1.60m. A solid cantilever placed below
    the working magnetic face would intersect the PM envelope, so the proposal
    keeps crossmembers below the modules and risers outside their swept width.
    The old L-return rail geometry/cost is not inherited.
    """
    span=25.;rho=7850.;E=200e9;pitch=.5;count=math.ceil(span/pitch)+1
    width=.5;thick=.035;face_y=.88;face_bottom=-1.16;beam_top=-1.60
    main_A=.15*.20-.13*.18;main_I=(.15*.20**3-.13*.18**3)/12;main_Z=main_I/.1
    cap_A=.15**2-.13**2;cap_I=(.15**4-.13**4)/12
    # Four narrow risers per crossmember stay outside the 400mm PM width.
    post_A=.08*.02-.074*.014;post_I=(.08*.02**3-.074*.014**3)/12
    baseplate_top=beam_top+.020
    base_top=baseplate_top+.20;cap_top=face_bottom+thick+.15
    post_length=cap_top-base_top
    brake_post_top=-.9435;brake_post_length=brake_post_top-base_top
    brake_A=.12**2-.10**2;brake_I=(.12**4-.10**4)/12;brake_Z=brake_I/.06
    rows=[
        dict(id='facing/35mm-working-plates',quantity=2,volume_m3=span*width*thick),
        dict(id='support/200x150x10-crossmember',quantity=count,volume_m3=main_A*2.40),
        dict(id='support/150x150x10-top-cap',quantity=2*count,volume_m3=cap_A*.50),
        dict(id='support/80x20x3-outside-PM-riser',quantity=4*count,volume_m3=post_A*post_length),
        dict(id='support/concrete-top-baseplate',quantity=2*count,volume_m3=.30*.40*.020),
        dict(id='support/triangular-gusset',quantity=4*count,volume_m3=.5*.20*.20*.010),
        dict(id='support/M24-anchor-shank-stock',quantity=8*count,volume_m3=math.pi*.024**2/4*.30),
        dict(id='support/M24-head-nut-stock',quantity=8*count,volume_m3=math.pi*.040**2/4*.04),
        dict(id='support/M24-washer-stock',quantity=16*count,volume_m3=math.pi*(.060**2-.026**2)/4*.005),
        dict(id='protection/120x120x10-brake-surface-post',quantity=2*count,volume_m3=brake_A*brake_post_length),
        dict(id='protection/12x200-vertical-wear-strip',quantity=2,volume_m3=span*.012*.20),
        dict(id='protection/60x16.5-capture-cap',quantity=2,volume_m3=span*.06*.0165),
        dict(id='protection/wear-strip-M12-shank',quantity=4*count,volume_m3=math.pi*.012**2/4*.08),
        dict(id='protection/wear-strip-M12-head-nut-stock',quantity=4*count,volume_m3=math.pi*.022**2/4*.025)]
    for r in rows:
        r['density_kg_m3']=rho;r['counted_mass_kg']=r['quantity']*r['volume_m3']*rho
    steel=math.fsum(r['counted_mass_kg'] for r in rows)
    plate_mass=rows[0]['counted_mass_kg'];fixtures=[]
    for force in (40000.,70000.):
        plate_I=.4*thick**3/12;plate_Z=.4*thick**2/6
        plate_M=force*pitch/4;plate_delta=force*pitch**3/(48*E*plate_I)
        arm=.88-.30;moment=force*arm
        cross_delta=force*arm**3/(3*E*main_I)
        cap_delta=force*.48**3/(48*E*cap_I)
        post_force=force/2;post_comp=post_force*post_length/(E*post_A)
        post_buckling=math.pi**2*E*post_I/post_length**2
        total=plate_delta+cross_delta+cap_delta+post_comp
        stress=max(plate_M/plate_Z,moment/main_Z,post_force/post_A)
        fixtures.append(dict(local_module_force_hypothesis_N=force,plate_pitch_m=pitch,
            plate_effective_width_hypothesis_m=.4,plate_stress_Pa=plate_M/plate_Z,
            plate_deflection_m=plate_delta,crossmember_overhang_m=arm,
            crossmember_stress_Pa=moment/main_Z,crossmember_deflection_m=cross_delta,
            cap_deflection_m=cap_delta,riser_compression_m=post_comp,
            riser_force_N=post_force,riser_pin_ended_weak_axis_buckling_N=post_buckling,
            combined_elastic_component_deflection_m=total,component_gap_deflection_target_m=.001,
            mechanical_stress_hypothesis_Pa=237e6,
            necessary_member_screen='pass' if stress<=237e6 and total<=.001 and post_force<=post_buckling/2 else 'fail',
            actual_joint_weld_baseplate_anchor_capacity_N=None,simultaneous_load_distribution_qualified=False,
            force_bound_qualified=False))
    normal=50000.;arm=-1.0435-base_top;brake_M=normal*arm
    brake_fixture=dict(clamp_normal_N=normal,contact_z_m=-1.0435,brake_post_root_z_m=base_top,
        moment_Nm=brake_M,post_bending_stress_Pa=brake_M/brake_Z,
        post_tip_elastic_deflection_m=normal*arm**3/(3*E*brake_I),
        post_necessary_member_screen='pass' if brake_M/brake_Z<=237e6 else 'fail',
        post_to_crossmember_and_unequal_clamp_anchor_cases='unknown')
    load_cases=[]
    for name,pax,extra in (('comfort',46,0.),('comfort-plus2t',46,2000.),('retained160crowd',160,0.),('retained160crowd-plus2t',160,2000.)):
        mass=accounted_tare_kg+75*pax+extra
        load_cases.append(dict(name=name,accounted_kg_per_car=mass,
            static_weight_N_per_car=mass*GRAVITY,uniform_module_weight_N=mass*GRAVITY/24,
            dynamic_1_3_N_per_car=1.3*mass*GRAVITY,dynamic_1_3_N_per_module=1.3*mass*GRAVITY/24,
            six_car_dynamic_1_3_N=6*1.3*mass*GRAVITY,
            module_distribution_is_a_uniform_hypothesis=True,asymmetric_and_fault_reactions_known=False))
    concrete_area=.8*2.5-(.8-2*.1)*(2.5-2*.15)
    concrete_volume=span*concrete_area;concrete_mass=2500*concrete_volume
    proposal=dict(span_m=span,reference_concrete_top_z_m=beam_top,
        reference_concrete_outer_width_m=.8,reference_concrete_depth_m=2.5,
        rail_centres_y_m=[-.88,.88],facing_width_m=width,facing_thickness_m=thick,
        overall_facing_envelope_width_m=2*face_y+width,rail_bottom_z_m=face_bottom,
        rails_are_downward_facing=True,module_nominal_drawing_gap_m=.012,
        drawing_gap_is_an_accepted_operating_gap=False,plain_guideway_has_powered_equipment=False,
        concrete_top_baseplate_bottom_z_m=beam_top,concrete_top_baseplate_top_z_m=baseplate_top,
        crossmember_bottom_z_m=baseplate_top,crossmember_top_z_m=base_top,
        crossmember_section_m=[.15,.20,.010],crossmember_length_m=2.4,
        top_cap_bottom_z_m=face_bottom+thick,top_cap_top_z_m=cap_top,
        riser_centres_abs_y_m=[.64,1.12],riser_y_thickness_m=.020,riser_height_m=post_length,
        clear_PM_width_at_risers_m=.46,PM_array_nominal_width_m=.40,
        minimum_nominal_riser_to_PM_edge_m=.03,actual_swept_and_wiring_clearance_qualified=False,
        brake_wear_surfaces=dict(centres_y_m=[-.4415,.4415],inner_contact_abs_y_m=.4355,
            width_y_m=.012,height_z_m=.20,centre_z_m=-1.0435,
            moving_pad_initial_abs_y_m=.4315,nominal_closing_gap_m=.004,
            actual_tolerance_and_hot_worn_contact_geometry_qualified=False),
        capture_caps=dict(centres_y_m=[-.4595,.4595],width_m=.06,thickness_m=.0165,
            top_z_m=-.927,nominal_shoe_underside_z_m=-.922,nominal_drop_gap_m=.005,
            actual_shoe_contact_and_upper_gap_capture_qualified=False),
        support_pitch_m=pitch,crossmembers_per_span=count,anchors_per_span=8*count,
        stock=rows,facing_only_kg_per_span=plate_mass,complete_counted_steel_stock_kg_per_span=steel,
        steel_stock_tonnes_per_direction_km=steel/span,
        reference_prismatic_concrete_volume_m3=concrete_volume,reference_prismatic_concrete_mass_kg=concrete_mass,
        concrete_plus_counted_steel_subtotal_kg=concrete_mass+steel,
        rebar_prestress_endblocks_bearings_sealants_and_embeds_kg=None,installed_span_mass_kg=None,
        installed_cost_per_direction_km=None,old_61_9tonne_span_or_L_return_rail_cost_transferred=False,
        local_member_fixtures=fixtures,brake_surface_post_fixture=brake_fixture,vehicle_load_cases=load_cases,
        anchor_positions_and_rebar_clashes_qualified=False,
        magnetic_effect_of_steel_spreaders_risers_protection_strips_and_joints_included_in_field_maps=False,
        full_guidebeam_prestress_torsion_movingload_foundation_and_erection_acceptance=False,
        steel_face_attachment_target='Factory jig; working face unobstructed; actual weld/bolt heads, thermal joints and installed magnetic shadow geometry need new analysis.',
        thermal_joint_requirements=dict(steel_alpha_per_K_hypothesis=12e-6,concrete_alpha_per_K_hypothesis=10e-6,
            declared_temperature_range_K=60.,five_metre_steel_vs_concrete_differential_m=(12e-6-10e-6)*60*5,
            full25m_free_steel_expansion_m=12e-6*60*25,joint_gap_fringe_drag_and_retention_known=False),
        conceptual_alternatives=[dict(id='wider-integral-concrete-ledges',scope='Reshape the concrete to carry the two faces and brake/capture surfaces with fewer steel risers',
            exact_geometry_rebar_volume_and_added_mass=None,installed_cost=None),
            dict(id='nonmagnetic-spreader-proposal',scope='Replace selected spreaders with nonmagnetic material to reduce field perturbation',
            exact_section_strength_stiffness_thermal_and_cost=None)],
        qualification_scope='New counted facing/support/protection-surface proposal and local fixtures; not an accepted guidebeam, force map or route.',**FLAGS)
    proposal['civil_interface_id']=identity(proposal)
    return proposal


def linear_capture_target(mass_kg,shoe_count,stroke_m):
    """New linear-force-law specification; never old8kg hardware capacity."""
    weight=mass_kg*GRAVITY;force_max=50000.;gap=.005
    per_shoe_k=force_max/stroke_m;K=shoe_count*per_shoe_k
    delta=(weight+math.sqrt(weight**2+2*K*weight*gap))/K
    force=per_shoe_k*delta
    return dict(shoes_proposed=shoe_count,maximum_stroke_m_proposed=stroke_m,
        maximum_force_N_per_shoe_proposed=force_max,linear_stiffness_N_m_proposed=per_shoe_k,
        nominal_drop_gap_m=gap,required_compression_m=delta,required_peak_force_N_each=force,
        necessary_energy_force_stroke_screen='pass' if delta<=stroke_m and force<=force_max else 'fail',
        energy_residual_J=.5*K*delta**2-weight*(gap+delta),
        new_hardware_mass_kg=None,new_hanger_reinforcement_mass_kg=None,
        source8kg_shoe_mass_transferred=False,new_geometry_applied_to_vehicle=False,
        force_law_materials_damping_contact_and_attachment_qualified=False)


def braking_and_capture_requirements(vehicle,root=ROOT):
    """Retain actual allocated protection stock; size its unproved interfaces."""
    data=json.loads((Path(root)/'engineering/ferrite_maglev/data/candidate-protection-equipment.json').read_bytes())
    wanted=('protection/independent-guideway-brake','protection/brake-hanger-kit','protection/brake-cross-tie',
            'protection/capture-shoe','protection/capture-hanger-kit')
    retained=[r for r in data['rows'] if r['id'] in wanted]
    source_ids={r.get('source_part_id') for r in vehicle['inventory']}
    if not set(wanted)<=source_ids:raise ValueError('retained protection hardware absent from matched vehicle inventory')
    tare=vehicle['mass']['accounted_tare_kg_per_car'];brake=[];capture=[]
    for passengers in (46,160):
        for extra in (0.,2000.):
            mass=tare+75*passengers+extra;weight=mass*GRAVITY
            for speed in (10.,12.,15.,20.):
                E=.5*mass*speed**2
                for active in (4,3):
                    for mu in (.05,.10,.20):
                        normal=50000.;force=active*mu*normal
                        for grade in (0.,.01,.05):
                            required=mass*(.4+GRAVITY*grade)
                            net=force/mass-GRAVITY*grade
                            delay=.05;distance=None if net<=0 else speed*delay+speed**2/(2*net)
                            heat=E*.3/active;rise=heat/(15*500.)
                            brake.append(dict(passengers_total=passengers,unclosed_extra_mass_kg=extra,
                                accounted_kg_per_car=mass,speed_m_s=speed,active_pad_units=active,
                                friction_coefficient_hypothesis=mu,normal_force_hypothesis_N_per_pad=normal,
                                downgrade_fraction_hypothesis=grade,required_net_deceleration_m_s2=.4,
                                required_braking_force_N=required,available_Coulomb_force_N_hypothesis=force,
                                net_deceleration_m_s2_hypothesis=net,
                                necessary_force_screen='pass' if force>=required else 'fail',
                                source_engagement_delay_s_hypothesis=delay,ideal_stopping_distance_m=distance,
                                vehicle_heat_fraction_hypothesis=.3,source_effective_thermal_mass_kg_per_pad=15.,
                                source_heat_capacity_J_kgK=500.,single_stop_delta_C_per_pad=rise,
                                initial_pad_C_hypothesis=80.,source_temperature_screen_C=180.,
                                one_stop_temperature_screen='pass' if 80+rise<=180 else 'fail',
                                repeated_stops_without_cooling_max_whole=math.floor(100/rise),
                                guideway_fraction_heat_J=.7*E,actual_partition_mu_deployment_and_cooling_qualified=False))
            gap=.005;k_shoe=10e6;count=8;K=count*k_shoe
            delta=(weight+math.sqrt(weight**2+2*K*weight*gap))/K
            peak=k_shoe*delta
            ideal_stroke8=(weight*gap)/(8*50000-weight) if 8*50000>weight else None
            ideal_stroke12=(weight*gap)/(12*50000-weight) if 12*50000>weight else None
            capture.append(dict(passengers_total=passengers,unclosed_extra_mass_kg=extra,
                accounted_kg_per_car=mass,retained_shoes=8,nominal_drop_gap_m=gap,
                source_stiffness_N_m_each=k_shoe,source_maximum_compression_m=.008,source_maximum_normal_N_each=50000.,
                undamped_linear_energy_compression_m=delta,undamped_linear_peak_force_N_each=peak,
                linear_source_shoe_screen='pass' if delta<=.008 and peak<=50000 else 'fail',
                linear_energy_residual_J=.5*K*delta**2-weight*(gap+delta),
                ideal_constant50kN_plateau_stroke_8shoes_m=ideal_stroke8,
                ideal_constant50kN_plateau_stroke_12shoes_m=ideal_stroke12,
                hypothetical_12shoe_8mm_plateau_bound='pass' if ideal_stroke12 is not None and ideal_stroke12<=.008 else 'fail',
                hypothetical_12shoe_extra_vehicle_stock_kg=4*(8.+10.22),
                extra_shoe_geometry_or_mass_applied_to_vehicle=False,
                actual_force_displacement_damping_retention_and_contact_qualified=False,
                redesign_targets=[linear_capture_target(mass,n,stroke) for n in (12,16) for stroke in (.020,.025)]))
    return dict(retained_vehicle_stock=[dict(id=r['id'],quantity_per_car=r['quantity_per_car'],
            unit_mass_kg=r['unit_mass_kg'],counted_or_allocated_kg_per_car=r['quantity_per_car']*r['unit_mass_kg'],
            source_evidence='Counted/allocated prototype stock; supplier/measured capacity and native fit unknown') for r in retained],
        retained_protection_subset_kg_per_car=sum(r['quantity_per_car']*r['unit_mass_kg'] for r in retained),
        inherited_vehicle_mass_removed_or_credited_again=False,
        guideway_surfaces_are_new_and_counted_in_civil=True,
        legacy_L_return_web_contact_transferred_without_redesign=False,
        release_actuation_requirement=dict(stroke_m_hypothesis=.004,working_normal_force_N_per_unit=50000.,
            minimum_constant_force_release_work_J_per_unit=200.,
            nominal_engagement_time_s_hypothesis=.05,mean_gap_closing_speed_m_s=.08,
            force_stroke_curve_spring_energy_release_latch_and_independent_trigger_qualified=False,
            power_loss_applies_brake_by_verified_hardware=False),
        brake_force_heat_sensitivities=brake,capture_energy_controls=capture,
        actual_guaranteed_onboard_deceleration_m_s2=None,
        actual_braking_distance_m=None,guaranteed_receiving_power_loss_protection=False,
        upper_gap_collapse_retention_design_complete=False,
        scope='Necessary contact, force, heat and capture-energy requirements using retained stock references. Dry/wet/hot friction, actuation, guideway load path and hardware are unqualified.',**FLAGS)

def restart_permission(*,stationary,protected_path,brake_control_ready,support_healthy,
                       at_powered_zone,power_confirmed,rescue_asset_ready=False,
                       coupling_inspected=False,tow_route_proved=False,contact_support_qualified=False):
    """Abstract prerequisite check; no train may restart by merely advancing time."""
    values=locals().copy()
    if any(type(v) is not bool for v in values.values()):raise ValueError('explicit observed/proved booleans required')
    missing=[name for name in ('stationary','protected_path','brake_control_ready') if not values[name]]
    if missing:return dict(action='hold',missing=missing,physical_movement_authorized=False)
    if support_healthy and at_powered_zone and power_confirmed:
        return dict(action='conditional-powered-restart-procedure',missing=[],physical_movement_authorized=False)
    tow_missing=[name for name in ('rescue_asset_ready','coupling_inspected','tow_route_proved') if not values[name]]
    if not support_healthy and not contact_support_qualified:tow_missing.append('qualified-contact-support-and-low-friction-retrieval')
    if tow_missing:return dict(action='hold',missing=tow_missing,physical_movement_authorized=False)
    return dict(action='conditional-protected-tow-to-powered-berth',missing=[],physical_movement_authorized=False)


def recovery_requirements(vehicle,service,winding,root=ROOT):
    root=Path(root);r=tomllib.loads((root/'engineering/ferrite_maglev/booster-kit.toml').read_text())['recovery']
    power=tomllib.loads((root/'ferrite-maglev-study.toml').read_text())['power']
    mass=vehicle['mass']['accounted_cap_loaded_kg_per_car']*6
    selected=_selected_cases(service)
    distance=max((case['inputs']['distance_m'] for case,_ in selected),default=2000.)
    reach=distance/2;length=reach+r['rope_tail_m'];rope_mass=length*r['selected_rope_mass_kg_m']
    capacity=r['selected_rope_minimum_breaking_force_n']*r['termination_efficiency_assumption']/r['rope_design_factor']
    force_cases=[]
    for mode,mu in (('support-healthy-levitated',None),('contact-slide-mu0.1',.1),('contact-slide-mu0.2',.2)):
        grade=.05;grade_force=mass*GRAVITY*grade/math.sqrt(1+grade*grade)
        drag=6*1000. if mu is None else mass*GRAVITY*mu
        cable_drag=rope_mass*GRAVITY*r['cable_drag_fraction']
        pull=(grade_force+drag+cable_drag)*r['working_pull_factor']
        force_cases.append(dict(mode=mode,sliding_friction_hypothesis=mu,
            maximum_downgrade_fraction_hypothesis=grade,grade_force_N=grade_force,
            vehicle_drag_N_hypothesis=drag,cable_drag_N_hypothesis=cable_drag,
            working_pull_N=pull,source_rope_capacity_after_factors_N=capacity,
            necessary_rope_screen='pass' if pull<=capacity else 'fail',
            winch_input_kW_at1m_s=pull/r['winch_efficiency']/1000.,
            actual_coupler_tow_eye_anchors_winch_and_support_mode_qualified=False))
    energy=[]
    cycles=[case['profile']['runtime_s']+case['inputs']['dwell_s'] for case,_ in selected] or [240.]
    for speed in (.5,1.):
        seconds=r['deployment_s']+reach/speed
        rescue_energy=15*seconds/3600.
        for pack in (30.,50.,60.):
            usable=pack*power['eol_capacity_fraction']*(power['normal_soc_high']-power['normal_soc_low'])
            for HVAC_kW in (20.,40.,60.):
                hotel=HVAC_kW+winding['repeated_duty_sensitivities'][-1]['known_copper_loss_kW_per_car']+2.+2.6
                incoming=hotel*max(cycles)/3600.
                energy.append(dict(tow_speed_m_s_hypothesis=speed,maximum_tow_reach_m=reach,
                    deployment_s_hypothesis=r['deployment_s'],deployment_plus_retrieval_s=seconds,
                    critical_services_kW_per_car_hypothesis=15.,critical_services_during_retrieval_kWh_car=rescue_energy,
                    HVAC_real_kWe_incoming_hypothesis=HVAC_kW,incoming_hotel_kWh_car=incoming,
                    incoming_leg_plus_dwell_s=max(cycles),pack_kWh_per_car_proposal=pack,
                    EOL_fraction=power['eol_capacity_fraction'],SOC_low=power['normal_soc_low'],SOC_high=power['normal_soc_high'],
                    EOL_SOC_usable_kWh_car=usable,required_incoming_plus_retrieval_kWh_car=incoming+rescue_energy,
                    margin_kWh_car=usable-incoming-rescue_energy,
                    necessary_energy_screen='pass' if usable>=incoming+rescue_energy else 'fail',
                    installed_pack_capacity_and_extra_pack_mass_known=False,
                    full_hot_weather_cooling_preserved_during_15kW_critical_mode=False))
    return dict(maximum_station_spacing_case_m=distance,station_winch_retrieval_reach_m=reach,
        old_nearest_node_half_spacing_reach_m=r['maximum_node_spacing_m']/2,
        old_nearest_node_reach_proves_tow_to_powered_station=False,
        rope_length_including_tail_m=length,rope_mass_kg=rope_mass,
        rope_diameter_m=r['selected_rope_diameter_m'],rope_source_url=r['rope_source_url'],
        rope_minimum_break_force_N=r['selected_rope_minimum_breaking_force_n'],
        termination_efficiency_hypothesis=r['termination_efficiency_assumption'],design_factor_hypothesis=r['rope_design_factor'],
        rope_drum_portal_foundation_and_access_need_resizing_for_this_reach=True,
        actual_located_recovery_nodes_and_quote=None,force_cases=force_cases,essential_energy_cases=energy,
        off_powered_zone_failure_action='Retain authority, stop following launches, secure the consist and require a located proved rescue/powered asset; time shift alone never supplies restart thrust.',
        support_failed_recovery_requirement='Qualified contact support plus low-friction recovery dollies/jacking or a separately sized heavy towing system; the levitated constant-drag rope calculation does not cover sliding capture pads.',
        independent_reconciliation_requirement='Fenced controller restart, fresh actual train integrity/readiness, retained forward locks and a proved new authority; stopped software reconciliation is not physical winch/coupling qualification.',
        normal120s_capacity_retained_during_recovery=False,
        baseline_off_zone_restart=restart_permission(stationary=True,protected_path=True,brake_control_ready=True,
            support_healthy=True,at_powered_zone=False,power_confirmed=False),
        actual_complete_recovery_demonstrated=False,**FLAGS)


def assembly_plan(vehicle):
    tasks=[
        ('body-jig',[],['Survey floor/body datums and magnetic mounting frames','Inspect exact frame members, galvanic isolation and bond preparation'],['Fixture calibration','Material/lot identity']),
        ('floor',['body-jig'],['Bond/fasten selected tiled floor panels with counted edge closures and inserts','Keep seat, wheelchair and battery hardpoint interfaces accessible'],['Core/skin bond witness coupons','Concentrated floor and insert loads']),
        ('roof',['body-jig'],['Fit revised thicker-skin/45mm-core roof on retained ribs and counted bearing shims','Inspect rejected crossrail clashes and new panel/lap/roof datums before HVAC ducts'],['Panel/bearing and retained-rib joint inspection','Roof/duct/passenger headroom clash review']),
        ('door-window',['body-jig'],['Install 61mm door leaf proposal and retained glass references','Resolve exterior slide/plug parking, seal lines, track recession and emergency release'],['Open/close swept clearance','Entrapment/interlock and egress test']),
        ('seat-restraints',['floor','door-window'],['Fit the exact paired and single-seat fixtures from the selected vehicle to qualified floor hardpoints','Fit two wheelchair restraint bays and preserve access paths'],['Vertical/backrest/restraint and fatigue tests','Occupied accessibility and evacuation trials']),
        ('HVAC-services',['roof'],['Fit five package references, drains, ducts, wiring and fresh-air paths','Separate essential support power from shed-able comfort loads and coordinate compressor starts'],['50C capacity/COP/airflow and N-1 test','Electrical isolation, heat rejection and EMC']),
        ('magnets',['floor','HVAC-services'],['Use restrained magnetic tooling to fit24 exact modules at surveyed transforms','Install independent retained capture and support isolation paths'],['Polarity and retention inspection','Matched gap/current/force map and controller test']),
        ('civil-factory',[],['Cast reference beam only after new facing-anchor/rebar design','Fit steel facings and spreaders in datum jig with working face unobstructed'],['Concrete release strength','Anchor/fatigue and magnetic shadow evidence']),
        ('erection',['civil-factory'],['Approve crane/transport configuration, foundation and temporary stability','Install, survey and lock facing adjustment with thermal joints'],['Signed lifting plan','Loaded alignment/deflection survey']),
        ('station',['erection'],['Install the actual selected shared winding length and protected electrical groups','Configure receiving path, battery charging, dump resistor and independent protection'],['Same-candidate force/voltage/heat duty','120s dwell, tail-clearance and fault cases']),
        ('acceptance',['seat-restraints','magnets','station'],['Weigh equipped car and measure CG/inertia','Confirm hover before any physical journey; test full train and faults'],['Authenticated physical evidence','Independent acceptance'])]
    return [dict(id=key,predecessors=before,operations=operations,release_evidence=evidence,
                 labour_hours=None,tooling_cost=None,procurement_lead_days=None,state='design-proposal',
                 actual_qualified_completion=False) for key,before,operations,evidence in tasks]


def evaluate(vehicle,service=None,*,root=ROOT):
    root=Path(root).resolve();tare,loaded=_subject(vehicle,service,root)
    parent=systems.parent_evidence(root);thermal=thermal_evidence(root)
    winding=winding_requirements(thermal['support_winding'])
    support=systems.support_comparison(tare,46,parent['samples'])
    civil=civil_design(tare);climate=thermal_requirements(thermal,vehicle,service);station=station_requirements(loaded,service,winding)
    protection=braking_and_capture_requirements(vehicle,root)
    recovery=recovery_requirements(vehicle,service,winding,root)
    gates=[dict(gate='mass',state='unknown',reason='Equipped mass, CG and inertia retain unlocated allocations/references and unresolved installation stock.'),
        dict(gate='suspension',state='unknown',reason='Zero-current component samples have unresolved contour disagreement; no installed3D multiaxis current map, equilibrium or damping proof.'),
        dict(gate='control',state='unknown',reason='Actual current authority, supply bandwidth, gap/tolerance envelope and essential-power fault response are unqualified.'),
        dict(gate='HVAC-electrical',state='unknown',reason='Actual50C capacity/COP/fresh air, compressor phases and complete bus/charging duty remain unqualified.'),
        dict(gate='roof-hot-core',state='fail',reason='The retained0.5solar-absorptivity/900Wm2/50C unshaded hypothesis exceeds the H60 continuous70C limit; measured finish/shading or material revision is required.'),
        dict(gate='body-clearance',state='unknown',reason='Revised roof on retained ribs,61mm doors, floor inserts, seat restraints and magnetic attachments need native swept fit and joined-body analysis.'),
        dict(gate='civil',state='unknown',reason='New2.26m steel-facing envelope and spreaders need anchors, concrete/rebar, prestress, moving loads, magnetic shadow and site evidence.'),
        dict(gate='capture-energy',state='fail',reason='The retained eight-shoe undamped linear source model exceeds the source force/compression bounds in the required drop cases; alternatives need counted geometry and measured force/stroke.'),
        dict(gate='onboard-braking',state='unknown',reason='Retained clamp stock has declared force/friction/thermal sensitivities, but actual wet/hot friction, independent deployment and guideway load paths are unqualified.'),
        dict(gate='recovery',state='unknown',reason='A stopped off-zone train needs located powered or winch recovery and essential energy. Contact-supported towing can exceed the retained rope bound; time shift is not restart thrust.'),
        dict(gate='operations',state='unknown',reason='A nominal120s resource screen cannot establish support, guaranteed braking, receiving-power-loss protection or actual dwell distribution.'),
        dict(gate='economics',state='unknown',reason='Trainset unit price, priced BOM coverage, labour, tooling, station power, fleet and whole-life costs are incomplete.')]
    for g in gates:
        g.update(name=g['gate'],scope='Stated necessary criterion; physical acceptance separate',**FLAGS)
    value=dict(schema=SCHEMA,candidate_id=vehicle['candidate_id'],body_candidate_id=vehicle['body_candidate_id'],
        magnet_component_id=vehicle['magnet_component_id'],service_evaluation_id=None if service is None else service['evaluation_id'],
        same_candidate_inputs=dict(vehicle_candidate_id=vehicle['candidate_id'],accounted_tare_kg_per_car=tare,
            accounted_cap_loaded_kg_per_car=loaded,cars=6,normal_passengers_per_car=46,
            retained_overcrowding_control_per_car=160,local_magnetic_frame_reaction_hypothesis_N=40000.),
        support=support,winding=winding,thermal=climate,station=station,civil=civil,protection=protection,recovery=recovery,
        coordinate_contract=dict(x='forward/longitudinal',y='left',z='up',body_floor_top_z_m=0.,
            PM_mounts_proposed_bank_y_m=[-.88,.88],PM_mounts_translation_z_m=-1.16,
            component_field_maps_are_not_a_full_installed_interface=True),
        design_interfaces=[dict(id='magnetic-module/body',count_per_car=24,
            nominal_retained_local_force_N=40000.,force_direction='Vertical upward on train; equal downward reaction at steel facing',
            lateral_force_and_roll_pitch_yaw_moment_envelopes=None,inspection='Polarity/retention, surveyed gap and independent isolated sensors',
            actual_mount_or_fault_load_limit_qualified=False),
            dict(id='floor/seats',pairs=sum(u['places']==2 for u in vehicle['physical_definition']['body']['seat_units']),
                singles=sum(u['places']==1 for u in vehicle['physical_definition']['body']['seat_units']),wheelchair_places=2,declared_seat_vertical_fixture_N_per_place=1500.,
                whole_floor_pointloads_restraints_and_accessibility_qualified=False),
            dict(id='door/body/platform',openings=2,leaf_depth_proposal_m=.061,
                original_sidewall_depth_m=.0447,additional_depth_over_wall_m=.0163,
                actual_opening_parking_track_and_platform_sweep=None,normal_active_openings_retained=2),
            dict(id='roof/HVAC',units=5,new_roof_assembly_depth_hypothesis_m=vehicle['interfaces']['roof_top_z_m']-vehicle['interfaces']['roof_bottom_skin_z_m'],
                actual_duct_routing_headroom_and_maintenance_access_qualified=False),
            dict(id='station/ordinary-guideway',PMs_and_support_coils='On train only',ordinary_structure='Concrete with passive steel facings',
                shared_station_winding_lengths_m=[r['shared_station_winding_length_m'] for r in station['cases']],
                actual_motor_conductor_turns_grouping_and_protection=None)],
        assembly_and_construction_plan=assembly_plan(vehicle),
        procurement_and_economics=dict(priced_complete_installed_BOM=False,priced_component_count=None,
            actual_trainset_unit_cost=None,complete_station_and_guideway_unit_cost=None,
            local_content_percent=None,origin_evidence_complete=False,
            decision_rule='Compare whole-life installed cost at declared service. Low unit train cost is a hypothesis until priced quantities, tooling, labour, fleet and renewal scope agree.',
            supplier_evidence_required=['Installed door/operator package and track depth','50C HVAC capacity/COP/phases/fresh air',
                'Magnet material/temperature/demagnetization and retention','Aluminium/core/adhesive fire and hot-load properties',
                'Facing steel magnetic BH and mechanical grade from the same batch','Anchor/prestress/foundation and route survey evidence',
                'Actual converter, charging, receiving dump and essential supply ratings']),
        gates=gates,execution='completed',numerical_validity='valid-necessary-bounds-with-explicit-unknowns',
        evidence_maturity='matched-analytical-design-dossier-and-retained-component-samples',
        complete_design_qualified=False,complete_operating_train_established=False,
        engineering_screen='fail-required-capture-fixture',integrated_baseline_eligible=False,
        source_sha256=_sources(root,vehicle,service,parent,thermal),**FLAGS)
    value['evaluation_id']=identity(value)
    return value


def validate(record,vehicle,service=None,*,root=ROOT):
    if record!=evaluate(vehicle,service,root=root):raise ValueError('matched interface result or candidate differs')
    return True


def summary(record):
    from collections import Counter
    cap=next(c for c in record['support']['cases'] if c['passengers_total']==46 and c['unclosed_additional_mass_kg']==0.)
    sample=next(s for s in cap['samples'] if s['gap_m']==.028)
    crowd=next(c for c in record['protection']['capture_energy_controls'] if c['passengers_total']==160 and c['unclosed_extra_mass_kg']==2000.)
    normal=next(c for c in record['protection']['capture_energy_controls'] if c['passengers_total']==46 and c['unclosed_extra_mass_kg']==0.)
    climate=[c['load']['total_kWthermal'] for c in record['thermal']['cases'] if c['passengers_total']==46]
    copper=record['winding']['repeated_duty_sensitivities'][-1]
    stations=[]
    for r in record['station']['cases']:
        valid=[c for c in r['hotel_charging'] if c['charge_window_fits_declared_dwell']]
        stations.append({k:r[k] for k in ('scenario_id','station_id','shared_station_winding_length_m',
            'two_direction_station_winding_subtotal_m','two_direction_motor_face_subtotal_m',
            'sections_per_direction','minimum_independent_train_current_phase_branch_sets_both_directions',
            'peak_speed_m_s','receiving_entry_speed_m_s','runtime_s','headway_s',
            'launch_mechanical_energy_kWh','receiving_mechanical_energy_kWh',
            'required_force_density_N_per_active_band_m','required_peak_force_per_equivalent_fully_engaged_car_N')}
            |dict(hotel_charge_input_peak_kW_range=[min(x['input_charge_peak_kW'] for x in valid),max(x['input_charge_peak_kW'] for x in valid)]))
    return dict(schema=SCHEMA,candidate_id=record['candidate_id'],body_candidate_id=record['body_candidate_id'],
        magnet_component_id=record['magnet_component_id'],evaluation_id=record['evaluation_id'],gates=record['gates'],
        gate_states=dict(Counter(g['state'] for g in record['gates'])),
        accounted_tare_kg_per_car=record['same_candidate_inputs']['accounted_tare_kg_per_car'],
        accounted_cap_loaded_kg_per_car=record['same_candidate_inputs']['accounted_cap_loaded_kg_per_car'],
        reserve_28mm_80C_min_sample_margin_N=sample['smaller_sampled_contour_1_3_margin_N'],
        force_contour_spread_N=sample['vertical_contour_spread_N'],
        retained15A_copper_loss_kW_per_car=copper['known_copper_loss_kW_per_car'],
        necessary80C_copper_to50C_air_conductance_W_K_per_module=copper['minimum_copper_to_50C_ambient_conductance_W_K_per_module'],
        thermal46person_sensitivity_kW_range=[min(climate),max(climate)],
        actual50C_cooling_and_real_power_known=False,station_cases=stations,
        roof_core_temperature_C_hypothesis=record['thermal']['cases'][0]['load']['thermal_construction']['roof_outer_core_temperature_C_hypothesis'],
        maximum_roof_solar_absorptivity_for70C_core_hypothesis=record['thermal']['cases'][0]['load']['thermal_construction']['maximum_roof_solar_absorptivity_for70C_core_hypothesis'],
        civil_interface_id=record['civil']['civil_interface_id'],
        civil_facing_envelope_width_m=record['civil']['overall_facing_envelope_width_m'],
        civil_facing_only_kg_per25m=record['civil']['facing_only_kg_per_span'],
        civil_counted_steel_kg_per25m=record['civil']['complete_counted_steel_stock_kg_per_span'],
        civil_concrete_and_counted_steel_kg_per25m=record['civil']['concrete_plus_counted_steel_subtotal_kg'],
        civil_local_fixtures=record['civil']['local_member_fixtures'],
        retained_capture8shoe_comfort_peak_N_each=normal['undamped_linear_peak_force_N_each'],
        retained_capture8shoe_comfort_stroke_m=normal['undamped_linear_energy_compression_m'],
        retained_capture8shoe_crowd_plus2t_peak_N_each=crowd['undamped_linear_peak_force_N_each'],
        retained_capture8shoe_crowd_plus2t_stroke_m=crowd['undamped_linear_energy_compression_m'],
        capture_redesign_targets_crowd_plus2t=crowd['redesign_targets'],
        actual_guaranteed_onboard_deceleration_m_s2=None,recovery=record['recovery'],complete_design_qualified=False,**FLAGS)


def markdown(record):
    v=summary(record)
    lines=['# Matched electrical, protection and civil design interfaces','',
        'This dossier uses the exact comfort vehicle and selected shared station-winding geometry. It specifies counted parts and numerical requirements while preserving physical acceptance gates.','',
        f"Vehicle `{v['candidate_id']}`; body `{v['body_candidate_id']}`; PM component `{v['magnet_component_id']}`.",'',
        '| Gate | Necessary result | Remaining evidence |','|---|---|---|']
    for g in v['gates']:lines.append(f"| {g['name']} | {g['state']} | {g['reason']} |")
    lines += ['', '## Support and hot-weather services','',
        f"The smaller retained zero-current 28 mm/80°C force sample exceeds 1.3× accounted comfort load by {v['reserve_28mm_80C_min_sample_margin_N']:.0f} N/module. The two contours differ by {v['force_contour_spread_N']:.0f} N/module. This is not a converged force-map bound or stable hover.",'',
        f"At 15 A RMS, known copper loss is {v['retained15A_copper_loss_kW_per_car']:.3f} kW/car. Maintaining 80°C copper against 50°C air requires at least {v['necessary80C_copper_to50C_air_conductance_W_K_per_module']:.3f} W/K per module before other losses. Actual heat rejection and RMS duty are unknown.",'',
        f"The matched aluminium-skin/45 mm H60 roof and floor thermal sensitivities give {min(v['thermal46person_sensitivity_kW_range']):.1f}–{max(v['thermal46person_sensitivity_kW_range']):.1f} kW thermal/car at 46 people. Glazing solar values and bridge losses are hypotheses; actual 50°C HVAC capacity, phase count, COP, input power and N−1 ventilation remain unknown. Same-car door recurrence is journey plus dwell, not the line headway.",'',
        f"The unshaded retained solar-absorptivity0.5 scenario puts the outer H60 core at {v['roof_core_temperature_C_hypothesis']:.1f}°C, above its70°C continuous reference. Under the declared1D films/conduction, aged roof absorptivity must be at most {v['maximum_roof_solar_absorptivity_for70C_core_hypothesis']:.3f}; ≤0.30 is a design target. Actual finish/coating mass, shading by HVAC and condenser recirculation are unknown, so no thermal or mass credit is applied.", '',
        '## Receiving, charging and protected two-minute service','',
        'The selected coast model arrives slower than launch speed. Normal receiving energy uses the actual arrival state; the independent fault brake must still stop from peak speed at any coast position. The retained 20 m/s force coupon is not transferred to new speeds/current states.','',
        '| Shared winding per direction | Sections/direction | Independent train branch sets, both directions | Peak/arrival speed | Required launch mechanical energy | Required receiving mechanical energy |','|---|---:|---:|---:|---:|---:|']
    for r in v['station_cases']:
        lines.append(f"| {r['shared_station_winding_length_m']:.0f} m | {r['sections_per_direction']} | {r['minimum_independent_train_current_phase_branch_sets_both_directions']} | {r['peak_speed_m_s']:.2f}/{r['receiving_entry_speed_m_s']:.2f} m/s | {r['launch_mechanical_energy_kWh']:.3f} kWh | {r['receiving_mechanical_energy_kWh']:.3f} kWh |")
    lines += ['', 'Section-addressed operation requires independently protected phase/current banks, interlocked routing and identified full-tail clearance. Four branch sets across two directions are a minimum functional count, not a proven converter BOM. Their current/voltage, switching, cooling and price remain unknown. Hotel charging uses explicit 20/40/60 kWe HVAC and 20/30/45-second charger scenarios; actual input power and battery/charger mass remain unknown. No regenerative saving is credited.','',
        '## Independent brakes and capture','',
        'Four retained clamp allocations, their hangers and two cross-ties remain counted in the vehicle. New wear/capture surfaces are counted in the civil proposal. Coulomb force/heat scenarios preserve three/four active units, wet/hot friction hypotheses, grades and the 160-person +2t control. They are requirements, not measured guaranteed braking.','',
        f"The retained eight-shoe linear model fails: at comfort load a 5 mm drop produces {v['retained_capture8shoe_comfort_stroke_m']*1000:.2f} mm compression and {v['retained_capture8shoe_comfort_peak_N_each']/1000:.1f} kN/shoe, against source 8 mm/50 kN bounds. At 160 people +2t, it produces {v['retained_capture8shoe_crowd_plus2t_stroke_m']*1000:.2f} mm and {v['retained_capture8shoe_crowd_plus2t_peak_N_each']/1000:.1f} kN/shoe.",'',
        '| New capture design target at 160 people +2t | Required stroke | Required force/shoe | Energy/force/stroke screen |','|---|---:|---:|---|']
    for r in v['capture_redesign_targets_crowd_plus2t']:
        lines.append(f"| {r['shoes_proposed']} shoes; {r['maximum_stroke_m_proposed']*1000:.0f} mm maximum; 50 kN maximum | {r['required_compression_m']*1000:.2f} mm | {r['required_peak_force_N_each']/1000:.1f} kN | {r['necessary_energy_force_stroke_screen']} |")
    lines += ['', 'Those are new force-law specifications. The old 8 kg shoe mass is not transferred; actual long-stroke hardware, upper-gap retention, hangers, reinforcement and contact/damping evidence remain required before updating the vehicle.','',
        '## New steel-faced concrete beam proposal','',
        f"Two 0.50 m-wide, 35 mm-thick facings at y=±0.88 m span {v['civil_facing_envelope_width_m']:.2f} m across. The plates alone count {v['civil_facing_only_kg_per25m']/1000:.3f} t per 25 m. New crossmembers, risers, baseplates, anchor stock and brake/capture surfaces bring counted steel to {v['civil_counted_steel_kg_per25m']/1000:.3f} t; adding the reference prismatic concrete gives {v['civil_concrete_and_counted_steel_kg_per25m']/1000:.3f} t before reinforcement, prestress, end blocks, bearings and other unresolved work.",'',
        'The existing −1.60 m beam-top datum is retained. Lower crossmembers, outside-PM risers and top caps support the working faces; new inner vertical wear strips and capture caps match the retained protection coordinates. Extra magnetic steel and joints invalidate any assumption that the isolated-coupon field map is the complete installed interface.','',
        'The 40 kN local member fixture passes the declared 1 mm elastic-component target; the 70 kN escalation fails it. Neither value is a qualified magnetic-collapse force bound. Welds, anchors, concrete breakout/rebar, global prestress/torsion, pier/foundation loads, erection and site quantities still need the matched design. Old L-return rail prices and the former 61.9 t beam are not transferred.','',
        '## Build and qualification sequence','']
    for r in record['assembly_and_construction_plan']:
        lines.append(f"- **{r['id']}**, after {', '.join(r['predecessors']) or 'design release'}: {'; '.join(r['operations'])}. Release evidence: {'; '.join(r['release_evidence'])}.")
    recovery=record['recovery']
    lines += ['', '## Off-zone stop and retrieval', '',
        f"A stopped coasting train has no arbitrary restart thrust. For the {recovery['maximum_station_spacing_case_m']:.0f} m leg, reaching a powered station can require {recovery['station_winch_retrieval_reach_m']:.0f} m of retrieval and {recovery['rope_length_including_tail_m']:.0f} m of cable including tail: {recovery['rope_mass_kg']/1000:.3f} t of the retained38mm rope reference. The old500m nearest-node reach does not by itself prove a complete handoff to a powered berth.", '',
        'Levitated towing and contact-supported sliding are separate cases. Wet/hot contact drag can exceed the retained rope design bound; source drum, portal, anchors, foundations and access require resizing. The rescue plan needs a powered receiving location, proved tow/coupling path and controller reconciliation, not an animation time shift.', '',
        'Essential energy preserves incoming hotel duty, deployment and actual retrieval time under30/50/60kWh pack hypotheses. Installed pack mass/capacity, full cooling during a15kW critical mode and physical recovery are unqualified. Normal120-second service is not promised during retrieval.', '']
    lines += ['', 'Labour hours, tooling, supplier lead times, actual unit trainset price and whole-life installed cost remain unknown. Lower-cost vehicles cannot justify extra service frequency without the station, fleet, energy, renewal and financing comparison.','',
        f"Interface evaluation `{record['evaluation_id']}`. Physical, manufacturing and operating release flags remain false.",'']
    return '\n'.join(lines)


def render_section_svg(record):
    """Dimensioned proposal section; no rendering is a clearance acceptance."""
    from html import escape
    v=record['civil'];scale=100.;cx=610.;floor=130.
    def rect(x,z,w,h,colour):return f'<rect x="{cx+x*scale:g}" y="{floor-z*scale:g}" width="{w*scale:g}" height="{h*scale:g}" fill="{colour}" stroke="#263746"/>'
    out=['<svg xmlns="http://www.w3.org/2000/svg" width="840" height="770" viewBox="0 0 840 770">',
        '<rect width="840" height="770" fill="white"/>',
        '<style>text{font:14px sans-serif;fill:#213544}.title{font-size:20px;font-weight:bold}</style>',
        '<text class="title" x="25" y="32">Comfort train / passive steel-faced beam interface</text>',
        '<text x="25" y="58">Proposed section: floor-top datum z=0; actual fit and operating gap remain unqualified</text>',
        rect(-1.325,0.,2.65,.08,'#b7d3e9'),rect(-.4,-1.60,.8,2.5,'#d3d3cc'),
        rect(-1.20,v['crossmember_top_z_m'],2.4,.20,'#a9bac5')]
    for y in (-.88,.88):
        out.append(rect(y-.25,-1.125,.5,.035,'#6f7f88'))
        out.append(rect(y-.25,-.975,.5,.15,'#a9bac5'))
        out.append(rect(y-.20,-1.172,.4,.041,'#7eacb7'))
        for shift in (-.24,.24):out.append(rect(y+shift-.01,v['top_cap_top_z_m'],.02,v['riser_height_m'],'#a9bac5'))
    for sign in (-1,1):
        out.append(rect(sign*.4415-.006,-.9435,.012,.20,'#875e55'))
        out.append(rect(sign*.4595-.03,-.927,.06,.0165,'#875e55'))
    out += ['<text x="31" y="114">Body width 2.65 m</text>',
        '<text x="25" y="350">Two facing centres: y=±0.88 m</text>',
        '<text x="25" y="373">Facing width 0.50 m; thickness 35 mm; total width 2.26 m</text>',
        '<text x="25" y="396">Crossmembers below PMs; risers outside 400 mm array width</text>',
        '<text x="25" y="419">Nominal longitudinal support pitch 500 mm</text>',
        '<text x="25" y="442">PM reference gap 12 mm is not a qualified operating gap</text>',
        '<text x="25" y="610">Concrete top z=−1.60 m; 0.8×2.5 m box is a section comparator</text>',
        '<text x="25" y="636">Welds, anchors, prestress, field shadow and global loads remain open</text>',
        '<text x="25" y="662">Brown: new brake wear strips and capture caps at retained protection coordinates</text>',
        '<text x="25" y="688">Added steel and beam joints require a matching installed 3D field model</text>',
        f'<text x="25" y="725">Civil proposal {escape(v["civil_interface_id"][:24])}; no physical release</text>','</svg>']
    return '\n'.join(out)+'\n'
