"""One continuous-platform docking hypothesis, never a native admission.

The original producer Case is replay-checked without changing it.  A different
boarding arrangement can justify a different *requirement*; it does not improve
localisation, supply brake force, extend authority, or finish a train envelope.
All results here precede same-body propagation and motion evaluation.
"""
from copy import deepcopy
from math import isfinite, sqrt
from pathlib import Path

from engineering.station_rail import ROOT
from engineering.station_rail.common import digest, identity
from . import frame, motion
from .route import FLAGS

PRODUCER = 'engineering/railway_project/docking_policy.py'
G = 9.80665


def _positive(value, name, zero=False):
    if type(value) not in (int, float) or not isfinite(value) or (value < 0 if zero else value <= 0):
        raise ValueError('Finite explicit physical value required: ' + name)
    return value


def hypothesis():
    """Fixed research revision; none of these dimensions is measured hardware.

    Four metres bounds *true* station offset. Position error is consequently
    not added to that offset again. The separate 0.5 m is an unverified budget
    for setout/thermal/deflection/end movement NOT already in a swept envelope.
    Its adequacy remains unknown. Five metres is a retained project end target,
    not an authenticated universal safety clearance.
    """
    return dict(schema='osr-continuous-platform-docking-hypothesis/1',
        family='continuous-platform-train-carried-bridgeplates',
        platform_length_m=130., platform_floor_module_length_m=5.,
        platform_modules_per_face=26, transition_length_m=150., reserved_straight_m=430.,
        true_offset_allowance_m=4., independent_end_budget_m=.5, retained_end_target_m=5.,
        physical_target='unchanged station reference D', physical_authority='unchanged D',
        accepted_actual_arrival_interval_relative_to_station_m=[-4., 0.],
        door_registration='Train-carried plates move with all12one-sided doors; no fixed PSD aperture assumed',
        platform_edge_protection='No fixed aperture PSD selected; independent platform-edge, intercar-gap and egress protection assessment required',
        sensing='Original source policy, biases, ideal standstill assumption and all delays unchanged',
        brake_floor='Explicit grade/mass hold force; heat and full-brake/preload retention remain required',
        finished_swept_envelope_m=None, bridgeplate_load_or_accessibility_qualification=None,
        vendor_selected=False, measured_performance_added=False)


def necessary_bounds(case, *, berth_tolerance_m, brake_floor_n, creep_speed_m_s):
    """Cheap sufficient checks of EXISTING v2 algebra, not a motion solve.

    No sampling, trajectory, actual plant look-ahead, rolling-brake credit or
    signed-gravity improvement to the Rust method is introduced. A positive
    result is only a subset of its domain tests, never a protected journey.
    """
    for k, v in dict(berth_tolerance_m=berth_tolerance_m, brake_floor_n=brake_floor_n,
                     creep_speed_m_s=creep_speed_m_s).items():
        _positive(v, k, zero=(k == 'brake_floor_n'))
    if creep_speed_m_s > .25:
        raise ValueError('Retained v2 creep request must be <=0.25m/s')
    p = case['control']; lo = p['mass_lower_kg']; hi = p['mass_upper_kg']
    numeric = ('mass_lower_kg', 'mass_upper_kg', 'brake_force_lower_bound_n',
               'positive_acceleration_bound_m_s2', 'end_of_authority_m')
    for key in numeric: _positive(p[key], key)
    nonnegative = ('rotating_mass_upper_kg', 'external_mass_upper_kg', 'grade_error_bound',
        'position_error_bound_m', 'speed_error_bound_m_s', 'reaction_time_bound_s',
        'brake_rise_time_bound_s', 'stopping_margin_m', 'start_traction_lower_bound_n',
        'rolling_resistance_upper_n', 'external_resistance_upper_n')
    for key in nonnegative: _positive(p[key], key, zero=True)
    grade = p['grade_estimate_fraction']; error = p['grade_error_bound']
    if type(grade) not in (int, float) or not isfinite(grade) or abs(grade)+error > .1 or lo > hi:
        raise ValueError('Unchanged ordered mass and bounded grade required')
    full = p['brake_force_lower_bound_n']
    if brake_floor_n > full:
        raise ValueError('Floor cannot exceed the declared guaranteed braking')
    slope = min(abs(grade)+error, .1)
    hold = hi*G*slope/sqrt(1+slope*slope)
    up = max(grade+error, 0.)
    down = min(grade-error, 0.)
    uphill = hi*G*up/sqrt(1+up*up)
    downhill = -hi*G*down/sqrt(1+down*down)
    preload = brake_floor_n+uphill+p['rolling_resistance_upper_n']+p['external_resistance_upper_n']+.02*lo
    inertia = hi+p['rotating_mass_upper_kg']+p['external_mass_upper_kg']
    decel = (full-downhill)/inertia
    dt = _positive(case['dt_s'], 'dt_s')
    # stopping_distance_bound(speed_error, infinity, dt, downhill/lo), plus
    # position_error, exactly the static v2 expression. Infinity means no jerk
    # slew term ONLY for this independent brake bound, not an infinite actuator.
    zero = None
    if decel > 1e-9:
        delay = p['reaction_time_bound_s']+p['brake_rise_time_bound_s']
        v = p['speed_error_bound_m_s']; run = p['positive_acceleration_bound_m_s2']
        after_sample = v+run*dt; acceleration = downhill/lo
        after_delay = after_sample+acceleration*delay
        zero = (v*dt+.5*run*dt*dt+after_sample*delay+.5*acceleration*delay*delay+
                after_delay*after_delay/(2*decel)+p['stopping_margin_m']+p['position_error_bound_m'])
    available = berth_tolerance_m-p['position_error_bound_m']
    rate = .5*lo*_positive(case['comfort_jerk_m_s3'], 'comfort jerk')
    governor_delay = p['reaction_time_bound_s']+p['brake_rise_time_bound_s']+full/rate
    headroom = (p['speed_error_bound_m_s']+p['positive_acceleration_bound_m_s2']*dt+
                downhill/lo*governor_delay+preload*preload/(2*rate*lo))
    checks = dict(positive_braking=decel > 1e-9, retained_floor=brake_floor_n >= hold,
        traction_preload=preload <= p['start_traction_lower_bound_n'],
        full_brake_preload_retention=preload+downhill <= full,
        zero_speed_room=zero is not None and zero < available,
        creep_observation=creep_speed_m_s+p['speed_error_bound_m_s'] < .5,
        wind_supported=case['headwind_m_s'] == 0.,
        governor_speed_room=case['speed_cap_m_s'] > headroom)
    return dict(grade_interval=[grade-error, grade+error], floor_infimum_n=hold,
        chosen_floor_n=brake_floor_n, traction_preload_n=preload,
        available_traction_lower_n=p['start_traction_lower_bound_n'],
        required_full_brake_retention_n=preload+downhill, available_brake_lower_n=full,
        braking_deceleration_lower_m_s2=decel, zero_speed_bound_plus_position_m=zero,
        available_docking_clearance_m=available,
        zero_speed_residual_m=None if zero is None else available-zero,
        governor_headroom_at_preload_m_s=headroom,
        retained_floor_heat_j_per_m=brake_floor_n,
        retained_floor_heat_w_at_requested_creep=brake_floor_n*creep_speed_m_s,
        checks=checks, failed_checks=[k for k,v in checks.items() if not v],
        complete_v2_domain_checked=False, conditional_model_journey_admitted=False)


def hardware_requirements(body):
    """Positive gross stock/process allowances, not installed purchase prices.

    The old body's door hardware is NOT automatically credited or removed. A
    later BOM delta must identify replacements before costing or mass summing.
    Local fabrication is a hypothesis; no vendor or sensing accuracy is selected.
    """
    layout = body['policy']['layout']
    if layout['cars'] != 6 or len(layout['door_centres_local_x_m']) != 2 or layout['door_clear_width_m'] != 1.4:
        raise ValueError('This research hypothesis is bound to twelve1.4m doors on six cars')
    panel_mass = 1.4*.35*.012*2700.
    rows = [
        dict(id='docking/bridgeplate-deck', quantity=12, material='aluminium plate research stock',
            stock_size_m=[1.4,.35,.012], mass_kg_each=[panel_mass]*3,
            process='cut, mill non-slip surface, deburr, fixture and inspect; strength/deflection not established',
            direct_cost_usd_each=[120.,220.,400.], peak_power_w_each=[0.,0.,0.], power_basis='passive stock'),
        dict(id='docking/slide-hinge-and-fixings', quantity=12, material='steel guide/hinge/bolts research assembly',
            mass_kg_each=[5.,9.,15.], direct_cost_usd_each=[180.,360.,750.], peak_power_w_each=[0.,0.,0.],
            process='machine guide, weld/bolt mounting, alignment and retention inspection', power_basis='passive stock'),
        dict(id='docking/bridgeplate-actuator-and-lock', quantity=12, material='bounded electromechanical equipment',
            mass_kg_each=[6.,10.,16.], direct_cost_usd_each=[300.,650.,1500.], peak_power_w_each=[150.,250.,500.],
            process='mount, wire, prove load retention and emergency retract; no verified capability', power_basis='declared sizing allowance'),
        dict(id='docking/position-interlock-and-harness', quantity=12, material='sensor/connector/harness/protection allowance',
            mass_kg_each=[1.,2.,4.], direct_cost_usd_each=[100.,220.,500.], peak_power_w_each=[5.,10.,20.],
            process='route protected wiring, test isolated position channels and door/brake interlocks', power_basis='declared sizing allowance'),
        dict(id='docking/standstill-brake-interface', quantity=2, material='independent detector/controller/mount/protection allowance',
            mass_kg_each=[3.,6.,12.], direct_cost_usd_each=[500.,1500.,4000.], peak_power_w_each=[10.,25.,60.],
            process='locate, wire, fault-test retained brake and departure inhibit; original accuracy not improved', power_basis='declared sizing allowance')]
    positions = [layout['car_length_m']/2+i*(layout['car_length_m']+layout['intercar_gap_m'])+x
                 for i in range(6) for x in layout['door_centres_local_x_m']]
    return dict(rows=rows, bridgeplate_x_about_body_x0_m=positions,
        mounting_side='+bodyY in both travel directions', deployment='0.35m stock depth; stroke/load/slope/contact geometry unresolved',
        proposed_gross_mass_kg=[sum(r['quantity']*r['mass_kg_each'][i] for r in rows) for i in range(3)],
        direct_component_cost_usd=[sum(r['quantity']*r['direct_cost_usd_each'][i] for r in rows) for i in range(3)],
        simultaneously_active_peak_power_w=[sum(r['quantity']*r['peak_power_w_each'][i] for r in rows) for i in range(3)],
        installed_mass_or_cost_complete=False, installed_BOM_counted=False, vendor_selected=False,
        exclusions=['Final mounting stresses, fixtures, structural reinforcement and existing-equipment replacement credits.',
            'Shared tooling, final assembly, QA/proof tests, commissioning, delivery, maintenance and replacement.',
            'Platform edge protection, accessible load/slope/gap proof and independent safety assessment.'])


def end_budget(*, finished_swept_half_extent_m=None, independent_end_budget_m=None,
               proxy_half_extent_m=None):
    """Do not turn gross stock or a CG box into a finished/swept envelope."""
    h = hypothesis()
    for key,value in dict(finished_swept_half_extent_m=finished_swept_half_extent_m,
            independent_end_budget_m=independent_end_budget_m,proxy_half_extent_m=proxy_half_extent_m).items():
        if value is not None: _positive(value,key,zero=(key=='independent_end_budget_m'))
    remaining = None
    if finished_swept_half_extent_m is not None and independent_end_budget_m is not None:
        remaining = (h['platform_length_m']/2-finished_swept_half_extent_m-
            h['true_offset_allowance_m']-independent_end_budget_m-h['retained_end_target_m'])
    proxy = None if proxy_half_extent_m is None else (h['platform_length_m']/2-proxy_half_extent_m-
        h['true_offset_allowance_m']-h['independent_end_budget_m']-h['retained_end_target_m'])
    return dict(finished_swept_end_residual_m=remaining,proxy_only_end_residual_m=proxy,
        finished_geometry_budget_known=remaining is not None,
        provisional_geometric_inequality_met=None if remaining is None else remaining >= 0,
        physical_clearance_verified=False,independent_end_budget_adequacy_verified=False)


def boarding_requirements(body, station):
    """Typed unresolved boarding/protection interfaces with positive ownership.

    A common nominal floor datum does not bound relative boarding height. None
    below is zero travel, perfect levelling, a tested interlock or a PSD waiver.
    """
    sites=station['physical_definition']['stations']
    faces=[f for s in sites for f in s['boarding_faces']]
    layout=body['policy']['layout']
    return dict(schema='osr-docking-boarding-protection-requirements/1',
        body_candidate_id=body['candidate_id'],body_evaluation_id=body['evaluation_id'],
        station_candidate_id=station['candidate_id'],station_evaluation_id=station['evaluation_id'],
        nominal_car_floor_above_rail_m=layout['floor_top_m'],
        nominal_platform_tops_above_rail_m=[f['nominal_platform_top_above_rail_m'] for f in faces],
        vertical_variation_m=dict(wheel_radius_wear=None,primary_suspension_travel=None,
            secondary_suspension_travel=None,car_roll_at_door=None,body_deflection_at_door=None,
            platform_deflection_setout_and_settlement=None,total_relative_floor_platform_interval=None),
        bridgeplate_capability=dict(qualified_horizontal_reach_m=None,qualified_vertical_reach_m=None,
            permissible_slope=None,design_and_proof_load_n=None,landing_overlap_m=None,
            landing_contact_detection=None,slip_resistance=None,ride_height_detection_and_interlock=None,
            nominal_stock_depth_m=.35,stock_depth_is_not_guaranteed_reach=True),
        door_enable_requires=['independent movement authority held against departure',
            'independently confirmed zero speed and retained braking',
            'measured ride-height/gap within independently approved bridgeplate envelope',
            'plate deployed, positively locked and supported on qualified landing',
            'platform/intercar passenger-edge protection in approved boarding state'],
        departure_enable_requires=['doors independently confirmed closed and locked',
            'all12plates independently confirmed stowed and locked',
            'platform passenger-edge protection in approved departure state',
            'new departure authority and retained-brake/traction-preload conditions met'],
        fault_response='Inhibit normal boarding/departure; independent braking and separately designed accessible evacuation remain available',
        platform_edge_protection=dict(selected_PSD_or_equivalent_architecture=None,
            no_PSD_absence_waiver=True,interfaces_with_door_authority_and_plate_control=True,
            control_assemblies=len(faces),protected_edge_length_m=130.*len(faces),
            ownership='NEW station scope; not a train-hardware or existing platform credit',
            reserve_mass_kg_each=[150.,300.,600.],reserve_peak_power_w_each=[100.,250.,500.],
            reserve_installed_cost_usd_each=[10000.,25000.,60000.],
            reserve_basis='Positive provisional scope allowance only; architecture, parts, foundations and achieved capability remain unknown',
            total_reserve_mass_kg=[len(faces)*v for v in (150.,300.,600.)],
            total_reserve_peak_power_w=[len(faces)*v for v in (100.,250.,500.)],
            total_reserve_installed_cost_usd=[len(faces)*v for v in (10000.,25000.,60000.)]),
        ride_height_or_door_alignment_verified=False,boarding_accessibility_verified=False,
        passenger_edge_protection_verified=False,conditional_boarding_admitted=False,
        conditional_native_service_admitted=False)


def propose(case, manifest, bundle, body, alignment, station, tracks, duty, envelope, feed, *,
            origin_route_m, allowed_initial_route_interval_m, brake_floor_n, creep_speed_m_s, root=ROOT):
    """Audit exact current ancestry, then return a NEW physical proposal only.

    Existing frame.compile_frame replays the original motion/drive producers and
    source policy. Resealing changed sensor bounds or a mixed body/station/feed
    cannot pass that check. This API intentionally exports NO Case or admission:
    new hardware and geometry first require a real body/station/track/feed and
    cost producer revision, with a new source-aware Case/policy/evaluation.
    """
    _, checked, entry, _ = frame.compile_frame(case, manifest, bundle, body, alignment, station,
        tracks, duty, envelope, feed, origin_route_m=origin_route_m,
        allowed_initial_route_interval_m=allowed_initial_route_interval_m, root=root)
    if 'research_v2' in case['control']:
        raise ValueError('Use the unchanged source producer Case; v2 is an explicit future projection')
    h = hypothesis(); hardware = hardware_requirements(body)
    boarding = boarding_requirements(body,station)
    p = station['physical_definition']; n = len(p['stations'])
    lengths = {f['platform_polygon_local_xy_m'][1][0]*2 for s in p['stations'] for f in s['boarding_faces']}
    if lengths != {125.} or alignment['physical_definition']['platform_straight_m'] != 425.:
        raise ValueError('This proposal retains exact125/425m station ancestry, not an already revised site')
    if tracks['physical_definition']['transition_length_m'] != h['transition_length_m']:
        raise ValueError('Retain the actual150m transitions; no implicit curvature change')
    if case['control']['end_of_authority_m'] != case['distance_m'] or case['berth_tolerance_m'] != 1.:
        raise ValueError('Original1m/physicalEOA=D control must remain the unchanged parent')
    physical = dict(schema='osr-continuous-docking-physical-proposal/1',
        parent_project_candidate_id=bundle['candidate_id'], parent_body_candidate_id=body['candidate_id'],
        parent_station_candidate_id=station['candidate_id'], parent_track_candidate_id=tracks['candidate_id'],
        design=h, train_carried_hardware=hardware,
        station_passenger_protection=dict(schema=boarding['schema'],
            control_assemblies=boarding['platform_edge_protection']['control_assemblies'],
            protected_edge_length_m=boarding['platform_edge_protection']['protected_edge_length_m'],
            architecture=None,positive_hardware_ownership_required=True),
        geometry_changes=dict(platform_length_delta_m=5., reserved_straight_delta_m=5.,
            platform_floor_delta_m2=2*n*5*p['platform_width_m'],
            terminal_track_delta_m=10., terminal_rail_delta_m=20.,
            terminal_feed_reference_length_delta_m=10.,
            feed_circuit_conductor_count_and_cross_section='Recount from actual selected feed; not a free10m electrical capacity',
            old_final_bay_overrun_credit='Reconcile once against terminal civil/rail ledger; not extra authority'))
    # Rates/capacity/analysis are evaluation context, not a manufactured geometry.
    physical['train_carried_hardware'] = {k:deepcopy(v) for k,v in hardware.items()
        if k not in ('proposed_gross_mass_kg','direct_component_cost_usd','simultaneously_active_peak_power_w','exclusions')}
    for row in physical['train_carried_hardware']['rows']:
        for key in ('mass_kg_each','direct_cost_usd_each','peak_power_w_each','power_basis'): row.pop(key)
    bounds = necessary_bounds(case, berth_tolerance_m=h['true_offset_allowance_m'],
        brake_floor_n=brake_floor_n, creep_speed_m_s=creep_speed_m_s)
    sources = deepcopy(checked['source_sha256']); sources[PRODUCER] = digest(Path(__file__))
    result = dict(schema='osr-continuous-docking-proposal-evaluation/1', candidate_id=identity(physical),
        physical_definition=physical, parent_body_evaluation_id=body['evaluation_id'],
        parent_project_evaluation_id=bundle['evaluation_id'], parent_input_evaluation_id=manifest['evaluation_id'],
        parent_case_id=case['id'], parent_policy_id=case['control']['policy_id'],
        ancestry_frame_context_id=entry['context_id'], source_sha256=sources,
        hardware_allowances=hardware,boarding_protection_contract=boarding,prepropagation_necessary_bounds=bounds,
        full_train_end_budget=end_budget(),
        numerical_scenario=deepcopy(manifest['scenario']), original_case_modified=False,
        physical_authority_extension_m=0., sensor_or_delay_improvement_assumed=False,
        native_export_supported=False, conditional_model_journey_admitted=False,
        operating_map_admitted=False, physical_evidence=False,
        holds=['Finished six-car swept envelope, couplers, end seals and positive reserves remain unverified; P1 proxy extents are not finished geometry.',
            '130m platforms and430m reserved straights are NEW geometry; actual mapped alignment, transitions, station supports, feed and costs must be regenerated.',
            'Train-carried bridgeplates and independent interlocks require real located/mated hardware, structural/accessibility/edge-protection design and same-body BOM propagation.',
            'Nominal car/platform floor datums do not resolve wheel wear, primary/secondary travel, roll/deflection, plate reach/slope/load/landing or ride-height interlocks; horizontal fit admits no boarding.',
            'Unchanged sensor/delay/brake/adhesion bounds and ideal standstill event are research assumptions; no precision or available hardware is measured.',
            'Prepropagation scalar bounds do not grant force/current/thermal duty, brake heat capacity, docking dynamics, protection, or service acceptance.',
            'Any future trajectory needs the separate journey assessor, positive stopping margin, speed/rollback/energy checks and explicit unresolved terminal jerk.',
            'Actual signed stop offsets and entire biased observation interval must propagate through exact future station/track/envelope/feed frame bindings.'], **FLAGS)
    result['evaluation_id'] = identity(result)
    return result
