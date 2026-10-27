"""Conditional independent-brake response after ideal propulsion isolation.

These are candidate-bound initial-state experiments, not full fault journeys or
approved protection curves. Actual isolation transients, brake supplies, WSP,
installed mass and safe limits remain unqualified. Static holding is resolved
separately: kinetic brake torque never accelerates a stationary car backwards.
"""
from math import copysign, isfinite, sqrt
from pathlib import Path
from engineering.station_rail import ROOT, braking
from engineering.station_rail.common import digest, identity
from . import railway_bundle

PRODUCER = 'engineering/design_search/fault_response.py'
REFERENCE = 'https://www.era.europa.eu/system/files/2022-11/Introduction%20to%20ETCS%20braking%20curves.pdf'
FLAGS = dict(physical_accepted=False, engineering_accepted=False, configuration_adopted=False,
             manufacturing_release=False, operating_release=False, physical_journey_completed=False)


def _number(x, name, minimum=0., maximum=None):
    if type(x) not in (int, float) or not isfinite(x) or x < minimum or (maximum is not None and x > maximum):
        raise ValueError('Finite bounded ' + name + ' required')
    return float(x)


def _plant(bundle):
    railway_bundle.validate(bundle)
    spec = bundle['brake_definition']
    if spec['brake_definition_id'] != identity({k: v for k, v in spec.items() if k != 'brake_definition_id'}):
        raise ValueError('Independent brake definition identity differs')
    if abs(spec['rotors']['equivalent_inertial_mass_kg_per_car'] - bundle['rotating_equivalent_kg_per_car']) > 1e-8:
        raise ValueError('Rotor and vehicle inertial mass scopes differ')
    return spec


def request(bundle, *, name, load='normal', initial_position_m=500., initial_speed_m_s=20.,
            grade_up_fraction=0., adhesion=.05, working_discs=8, pressure_available_fraction=1.,
            detection_command_latency_s=1., horizon_s=60., dt_s=.05):
    spec = _plant(bundle)
    if not isinstance(name, str) or not name or load not in ('empty', 'normal', 'crowd'):
        raise ValueError('Named initial-state experiment and explicit loading required')
    distance = bundle['architecture_case']['physical_definition']['route']['station_spacing_m']
    initial_position_m = _number(initial_position_m, 'initial position', maximum=distance)
    initial_speed_m_s = _number(initial_speed_m_s, 'signed initial speed', minimum=-20., maximum=20.)
    grade_up_fraction = _number(grade_up_fraction, 'uphill grade', minimum=-.1, maximum=.1)
    adhesion = _number(adhesion, 'adhesion hypothesis', maximum=1.)
    pressure_available_fraction = _number(pressure_available_fraction, 'pressure availability', maximum=1.)
    detection_command_latency_s = _number(detection_command_latency_s, 'command latency', maximum=10.)
    horizon_s = _number(horizon_s, 'observation horizon', minimum=.1, maximum=120.)
    dt_s = _number(dt_s, 'timestep', minimum=.005, maximum=.1)
    if type(working_discs) is not int or not 0 <= working_discs <= 8:
        raise ValueError('Zero to eight counted working brake discs per car required')
    value = dict(schema='osr-independent-fault-response-request/1', name=name,
        bundle_id=bundle['bundle_id'], bundle_definition_id=bundle['definition_id'],
        body_candidate_id=bundle['body_candidate_id'], brake_definition_id=spec['brake_definition_id'],
        requirement_revision=bundle['requirement_revision'], load=load, distance_m=distance,
        initial_position_m=initial_position_m, initial_speed_m_s=initial_speed_m_s,
        grade_up_fraction=grade_up_fraction, adhesion=adhesion, working_discs=working_discs,
        pressure_available_fraction=pressure_available_fraction,
        detection_command_latency_s=detection_command_latency_s, horizon_s=horizon_s, dt_s=dt_s,
        initial_state_origin='Explicit sensitivity hypothesis; not the output of a completed powered journey',
        grade_profile_origin='Constant-grade sensitivity throughout the response region, including any station-position crossing; no surveyed route profile',
        post_isolation_motor_force_N_per_car_hypothesis=0., actual_isolation_transient_verified=False,
        actual_brake_supply_independence_verified=False, hardware_WSP_verified=False,
        maximum_steps=24000, maximum_abs_speed_m_s=40.,
        approved_stopping_or_rollback_limit_m=None, safety_braking_floor_m_s2=None,
        reference=dict(url=REFERENCE, version='ERA_ERTMS_040026 v1.5',
            scope='Background separation of nominal prediction, build-up time and guaranteed braking; no ETCS implementation or compliance claim'), **FLAGS)
    value['request_id'] = identity(value)
    return value


def validate(bundle, value):
    keys=('name','load','initial_position_m','initial_speed_m_s','grade_up_fraction','adhesion',
          'working_discs','pressure_available_fraction','detection_command_latency_s','horizon_s','dt_s')
    if not isinstance(value, dict) or any(k not in value for k in keys):
        raise ValueError('Complete explicit fault-response request required')
    if value != request(bundle, **{k: value[k] for k in keys}):
        raise ValueError('Fault response differs from exact bundle, model domain or experiment contract')
    return value


def _command(spec, mass, elapsed, discs, pressure):
    # Extract the existing actuator's unmodified command at zero external force.
    # Its kinetic acceleration is deliberately not used for static holding.
    force = braking.force_state(spec, mass, 0., max(0., elapsed), rail_adhesion=1.,
                                pressure_Pa=pressure, available_discs=discs)
    return force['commanded_brake_torque_Nm_per_car'] / spec['rotors']['radius_m']


def _static(spec, mass, elapsed, case):
    pressure = spec['maximum_pressure_Pa_hypothesis'] * case['pressure_available_fraction']
    command = _command(spec, mass, elapsed, case['working_discs'], pressure)
    normal = mass * braking.G / sqrt(1 + case['grade_up_fraction'] ** 2)
    return min(command, case['adhesion'] * normal)


def solve(bundle, case):
    validate(bundle, case); spec = _plant(bundle)
    mass = bundle['mass'][dict(empty='accounted_tare_kg_per_car', normal='accounted_cap_loaded_kg_per_car',
                               crowd='accounted_160_control_kg_per_car')[case['load']]]
    effective = mass + bundle['rotating_equivalent_kg_per_car']
    cars = bundle['cars']; grade = case['grade_up_fraction']
    gravity = -mass * braking.G * grade / sqrt(1 + grade * grade)
    pressure = spec['maximum_pressure_Pa_hypothesis'] * case['pressure_available_fraction']
    latency = case['detection_command_latency_s']
    x = case['initial_position_m']; v = case['initial_speed_m_s']; t = 0.
    initial = .5 * effective * v * v
    heat = gravity_work = path = reverse_path = rollback_from_peak = 0.; trace = []; stops = []
    minimum_x = maximum_x = x; max_speed = abs(v); state = 'observation-horizon'; reason = None

    def kinetic(h, direction):
        f = braking.force_state(spec, mass, abs(v), max(0., t + h / 2 - latency),
            grade_down_fraction=-direction * grade, rail_adhesion=case['adhesion'],
            available_discs=case['working_discs'], pressure_Pa=pressure)
        if not f['valid']: raise ValueError(f['reason'])
        return direction * f['acceleration_m_s2'], f['torque_equivalent_brake_force_N_per_car']

    for step in range(case['maximum_steps']):
        if t >= case['horizon_s'] - 1e-10: break
        h = min(case['dt_s'], case['horizon_s'] - t)
        # Resolve the command and pressure-delay boundaries before quadrature.
        boundaries = [latency, latency + spec['pressure_response_delay_s_hypothesis']]
        future = [z for z in boundaries if t + 1e-10 < z < t + h]
        if future: h = min(future) - t
        capacity = _static(spec, mass, t - latency, case)
        held = abs(v) <= 1e-10 and abs(gravity) <= capacity + 1e-9
        try:
            if held:
                newv = 0.; dx = 0.; brake_force = abs(gravity); acceleration = 0.
            else:
                direction = copysign(1., v if abs(v) > 1e-10 else gravity)
                acceleration, brake_force = kinetic(h, direction)
                if abs(v) <= 1e-10 and direction * acceleration < 0:
                    # Pressure became sufficient within this short step. Refine
                    # rather than create reverse propulsion from a brake command.
                    for _ in range(40):
                        h /= 2; acceleration, brake_force = kinetic(h, direction)
                        if direction * acceleration >= 0: break
                    else: raise ValueError('Static-to-rolling transition unresolved')
                newv = v + acceleration * h
                if abs(v) > 1e-10 and v * newv < 0:
                    lo = 0.; hi = h
                    for _ in range(45):
                        mid = (lo + hi) / 2; a, _ = kinetic(mid, direction)
                        if direction * (v + a * mid) > 0: lo = mid
                        else: hi = mid
                    h = (lo + hi) / 2; acceleration, brake_force = kinetic(h, direction); newv = 0.
                    stops.append(dict(time_s=t + h, position_m=x + v * h / 2))
                dx = (v + newv) * h / 2
            heat += brake_force * abs(dx); gravity_work += gravity * dx
            x += dx; t += h; v = newv; path += abs(dx); reverse_path += max(0., -dx)
            minimum_x = min(minimum_x, x); maximum_x = max(maximum_x, x); max_speed = max(max_speed, abs(v))
            rollback_from_peak = max(rollback_from_peak, maximum_x - x)
            trace.append(dict(time_s=t, position_m=x, signed_speed_m_s=v, static_hold=held,
                static_rail_reaction_N_per_car=-gravity if held else None,
                commanded_brake_force_N_per_car=_command(spec, mass, t - latency, case['working_discs'], pressure),
                applied_brake_force_N_per_car=brake_force, acceleration_m_s2=acceleration,
                energy_residual_J_per_car=initial + gravity_work - heat - .5 * effective * v * v))
            if max_speed > case['maximum_abs_speed_m_s']:
                state='outside-speed-domain'; reason='40 m/s calculation domain exceeded'; break
        except ValueError as error:
            state='outside-model-domain'; reason=str(error); break
    else:
        if t < case['horizon_s'] - 1e-10:
            state='step-budget'; reason='24000-step numerical budget exhausted'
    stationary = abs(v) <= 1e-8
    final_capacity = _static(spec, mass, t - latency, case)
    active_disc_capacity = spec['counted_disc_stock_kg_per_car'] * case['working_discs'] / 8 * spec['steel_specific_heat_J_kg_K_hypothesis']
    value = dict(schema='osr-independent-fault-response/1', request_id=case['request_id'],
        candidate_id=bundle['candidate_id'], body_candidate_id=bundle['body_candidate_id'],
        brake_definition_id=spec['brake_definition_id'],
        execution='interrupted' if state=='step-budget' else 'held-outside-model-domain' if state.startswith('outside-') else 'completed-conditional-method',
        state=state, reason=reason, elapsed_s=t, final_position_m=x, final_signed_speed_m_s=v,
        minimum_position_m=minimum_x, maximum_position_m=maximum_x, travelled_path_m=path,
        maximum_reverse_displacement_m=max(0., case['initial_position_m'] - minimum_x),
        maximum_reverse_displacement_origin='Initial fault position; reverse travel from a later forward peak is reported separately',
        cumulative_reverse_travel_m=reverse_path, maximum_rollback_from_reached_position_m=rollback_from_peak,
        downstream_station_position_crossed=maximum_x > case['distance_m'],
        maximum_downstream_station_overshoot_m=max(0., maximum_x - case['distance_m']),
        forward_travel_from_fault_m=max(0., maximum_x - case['initial_position_m']),
        maximum_abs_speed_m_s=max_speed, stationary_at_horizon=stationary,
        static_holding_necessary_margin_N_per_car=final_capacity - abs(gravity),
        stationary_holding_hypothesis=stationary and final_capacity >= abs(gravity) - 1e-9,
        stopping_events=stops, initial_kinetic_energy_J_train=cars * initial,
        final_kinetic_energy_J_train=cars * .5 * effective * v * v,
        gravity_work_J_train=cars * gravity_work, disc_heat_J_train=cars * heat,
        energy_residual_J_train=cars * (initial + gravity_work - heat - .5 * effective * v * v),
        lumped_active_disc_temperature_C_hypothesis=None if active_disc_capacity == 0 else spec['ambient_C_hypothesis'] + heat / active_disc_capacity,
        complete_installed_mass_kg=None, mass_scope=bundle['mass_scope'], trace=trace,
        actual_protected_stop=False, precise_station_stopping_demonstrated=False,
        safety_braking_floor_m_s2=None, approved_stopping_or_rollback_limit_m=None,
        engineering_screen='unknown', numerical_validity='incomplete-budget' if state=='step-budget' else 'outside-declared-domain' if state.startswith('outside-') else 'midpoint-work-identity-evaluated-refinement-required',
        scope='Uniform six-car pure rolling and ideal adhesion limiter; no drag credit, coupler dynamics, real WSP, fade, pressure-store failure model or validated initial powered journey', **FLAGS)
    value['evaluation_id'] = identity(value)
    return value


def evaluate(bundle, *, root=ROOT):
    _plant(bundle)
    source_names=(PRODUCER,'engineering/station_rail/braking.py','engineering/design_search/railway_bundle.py')
    sources={**bundle['source_sha256'],**{n:digest(Path(root)/n) for n in source_names}}
    loaded={PRODUCER:digest(__file__),source_names[1]:digest(braking.__file__),source_names[2]:digest(railway_bundle.__file__)}
    if any(sources[name] != h for name,h in loaded.items()):
        raise ValueError('Executing fault-response producer differs from source root')
    definitions = [
        dict(name='failed-launch', initial_position_m=0., initial_speed_m_s=0., grade_up_fraction=.01),
        dict(name='wayside-power-loss', initial_position_m=500., initial_speed_m_s=20., grade_up_fraction=-.02),
        dict(name='one-brake-channel-lost', initial_position_m=500., initial_speed_m_s=20., grade_up_fraction=-.02, working_discs=4, load='crowd'),
        dict(name='brake-pressure-lost-control', initial_position_m=500., initial_speed_m_s=20., grade_up_fraction=-.02, pressure_available_fraction=0.),
        dict(name='insufficient-adhesion-control', initial_position_m=500., initial_speed_m_s=20., grade_up_fraction=-.04, adhesion=.03, load='crowd'),
        dict(name='stranded-train-holding', initial_position_m=1000., initial_speed_m_s=0., grade_up_fraction=.02),
    ]
    rows=[]
    for definition in definitions:
        case=request(bundle, **definition); result=solve(bundle, case)
        rows.append(dict(request=case, result=result))
    if any(digest(Path(root)/name)!=h for name,h in sources.items()):
        raise ValueError('Fault-response source epoch changed during calculation')
    value=dict(schema='osr-candidate-fault-response-matrix/1', candidate_id=bundle['candidate_id'],
        body_candidate_id=bundle['body_candidate_id'], bundle_definition_id=bundle['definition_id'],
        cases=rows, source_sha256=sources, integrated_fault_journey_demonstrated=False,
        recovery_drive_or_rescue_demonstrated=False, independent_qualification_required=True, **FLAGS)
    value['evaluation_id']=identity(value)
    return value
