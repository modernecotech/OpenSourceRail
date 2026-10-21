"""Station launch/coast/arrival numerical study and unquoted equipment budgets.

The plant prescribes jerk-limited net acceleration at station motors and exact
free coast under a provisional resistance law. It does not solve a motor, prove
protection, or authorize outputs. Every sampled overlap result is conditional on
an assumed force density, not evidence of electromagnetic performance.
"""
from copy import deepcopy
from functools import lru_cache
from hashlib import sha256
import gzip
import json
import math
from pathlib import Path
import platform
import tomllib

ROOT = Path(__file__).resolve().parents[2]
INPUT = Path(__file__).with_suffix('.toml')
OUTPUT = ROOT/'docs/design-engine/ferrite-maglev/station-powered'
SCHEMA = 'osr-station-powered-study/1'
FLAGS = dict(design_complete=False, physical_validation=False,
             manufacturing_release=False, physical_release=False)
FILES = {'result.json.gz', 'overview.svg', 'power.svg', 'README.md'}
MAX_RAW = 64*1024*1024
G = 9.81


def _finite(value, name, low, high):
    if type(value) not in (int, float) or not math.isfinite(value) or not low <= value <= high:
        raise ValueError(f'finite bounded {name} required ({low}..{high})')
    return float(value)


def _integer(value, name, low, high):
    if type(value) is not int or not low <= value <= high:
        raise ValueError(f'bounded integer {name} required')
    return value


def load():
    """Read bounded project assumptions; none is an accepted hardware rating."""
    a = tomllib.loads(INPUT.read_text())
    if a.get('schema') != SCHEMA:
        raise ValueError('station-powered study schema required')
    v, m, s, c = (a[k] for k in ('vehicle', 'motion', 'station', 'cost'))
    _integer(v['cars'], 'cars', 1, 12)
    for key, lo, hi in [('car_mass_kg', 5000, 100000), ('body_length_m', 8, 30),
                        ('coupling_gap_m', 0, 2), ('magnetic_band_m_per_car', 1, 30),
                        ('pole_pitch_m', .05, 1), ('combined_motor_face_width_m', .1, 3)]:
        _finite(v[key], key, lo, hi)
    if v['magnetic_band_m_per_car'] > v['body_length_m']:
        raise ValueError('magnetic band must fit the assumed body')
    for key, lo, hi in [('distance_m', 100, 10000), ('runtime_s', 20, 600),
                        ('acceleration_m_s2', .1, 2), ('deceleration_m_s2', .1, 2),
                        ('jerk_m_s3', .1, 2), ('speed_limit_kmh', 10, 160),
                        ('resistance_constant_n_per_car', 1, 10000),
                        ('resistance_quadratic_n_per_car', .01, 100),
                        ('motoring_efficiency', .1, 1), ('generating_efficiency', .1, 1),
                        ('overlap_sample_interval_s', .002, .01),
                        ('published_trace_interval_s', .05, .5)]:
        _finite(m[key], key, lo, hi)
    for key, lo, hi in [('winding_start_m', -1000, -1), ('winding_end_m', 1, 1000),
                        ('electrical_section_m', .5, 50), ('mechanical_cassette_m', .1, 10),
                        ('equivalent_envelope_force_n_m', 100, 20000), ('dwell_s', 10, 180),
                        ('connected_charging_s', 1, 180), ('scheduled_headway_s', 30, 1200),
                        ('release_allowance_s', 0, 60), ('hot_services_kw_per_car', 1, 200),
                        ('services_battery_kwh_per_car', 5, 100), ('battery_eol_fraction', .1, 1),
                        ('soc_low', 0, 1), ('soc_high', 0, 1),
                        ('protected_services_reserve_minutes', 0, 60)]:
        _finite(s[key], key, lo, hi)
    if s['connected_charging_s'] > s['dwell_s'] or s['soc_low'] >= s['soc_high']:
        raise ValueError('charging/SOC windows inconsistent')
    if type(s['independent_shore_supply_during_disconnected_dwell']) is not bool:
        raise ValueError('explicit disconnected-dwell supply assumption required')
    for name, value in a['validation'].items():
        if value is not False:
            raise ValueError('unqualified study cannot claim '+name)
    _finite(c['estimating_reserve_fraction'], 'estimating reserve', 0, 1)
    for key in ('stator_usd_per_direction_m', 'supply_rectifier_dc_usd',
                'brake_chopper_resistor_usd', 'charging_interfaces_usd',
                'motion_sensing_safety_usd', 'thermal_installation_acceptance_usd',
                'bridge_usd_per_kw_equivalent', 'routing_assemblies_usd'):
        if len(c[key]) != 3:
            raise ValueError('three target-rate sensitivities required')
        for value in c[key]:
            _finite(value, key, 1, 1e8)
    _integer(c['fixed_group_bridges'], 'fixed bridge count', 2, 32)
    for count in c['routed_bank_counts']:
        _integer(count, 'routed bank count', 2, 32)
    for key in ('fixed_group_kw_equivalent_per_bridge', 'routed_kw_equivalent_per_bank',
                'independent_kw_equivalent_per_section'):
        _finite(c[key], key, 1, 10000)
    return a


def _encoded(value):
    return (json.dumps(value, sort_keys=True, indent=2, allow_nan=False)+'\n').encode()


def _digest(path):
    return sha256(Path(path).read_bytes()).hexdigest()


def sources():
    """Calculation inputs only; generated packets never feed their own identity."""
    names = ['engineering/ferrite_maglev/station.py', 'engineering/ferrite_maglev/station.toml',
             'ferrite-maglev-study.toml', 'engineering/ferrite_maglev/model.py',
             'engineering/ferrite_maglev/manufacturing.py',
             'engineering/ferrite_maglev/configuration.py',
             'engineering/ferrite_maglev/reference-configuration.toml',
             'engineering/ferrite_maglev/data/cost-rates.json', 'requirements.in', 'requirements.txt']
    return {name: _digest(ROOT/name) for name in names if (ROOT/name).is_file()}


def _step(v, acc, jerk, duration):
    return (v+acc*duration+.5*jerk*duration**2, acc+jerk*duration,
            v*duration+.5*acc*duration**2+jerk*duration**3/6)


def _launch(v, mass, acceleration, jerk, constant, quadratic):
    ac = -(constant+quadratic*v*v)/mass
    peak = min(acceleration, math.sqrt(jerk*v+.5*ac*ac))
    if ac > peak or ac < -acceleration:
        raise ValueError('free-coast acceleration exceeds the launch envelope')
    first, last = peak/jerk, (peak-ac)/jerk
    v1, _, _ = _step(0, 0, jerk, first)
    hold = (v-v1-(peak+ac)*last/2)/peak
    if hold < -1e-8:
        raise ValueError('launch ramp has no forward solution')
    return [(jerk, first), (0., max(0., hold)), (-jerk, last)]


def _brake(v, mass, deceleration, jerk, constant, quadratic):
    ac = -(constant+quadratic*v*v)/mass
    peak = min(deceleration, math.sqrt(jerk*v+.5*ac*ac))
    if ac < -peak or ac > deceleration:
        raise ValueError('free-coast acceleration exceeds the receiving envelope')
    first, last = (peak+ac)/jerk, peak/jerk
    v1, _, _ = _step(v, ac, -jerk, first)
    hold = (v1-peak*last/2)/peak
    if hold < -1e-8:
        raise ValueError('braking ramp has no forward solution')
    return [(-jerk, first), (0., max(0., hold)), (jerk, last)]


def _segments(v, acc, phases):
    out, x, t = [], 0., 0.
    for jerk, duration in phases:
        out.append(dict(start_time_s=t, start_position_m=x, start_speed_m_s=v,
                        start_acceleration_m_s2=acc, jerk_m_s3=jerk, duration_s=duration))
        v, acc, dx = _step(v, acc, jerk, duration)
        x += dx
        t += duration
    return out, t, x


def _coast(v, duration, mass, constant, quadratic):
    """Exact positive-speed Riccati solution, capped when an uphill train stops."""
    k, q = constant/mass, quadratic/mass
    if k > 1e-12:
        rate = math.sqrt(k*q)
        theta = math.atan(v*math.sqrt(q/k))
        stop = theta/rate
        used = min(duration, stop)
        final = theta-rate*used
        speed = max(0., math.sqrt(k/q)*math.tan(final))
        distance = (math.log(math.cos(final))-math.log(math.cos(theta)))/q
        return speed, distance, max(0., duration-stop)
    if k < -1e-12:
        rate, terminal = math.sqrt(-k*q), math.sqrt(-k/q)
        z, ratio = rate*duration, v/terminal
        speed = terminal*(ratio+math.tanh(z))/(1+ratio*math.tanh(z))
        distance = math.log(math.cosh(z)+ratio*math.sinh(z))/q
        return speed, distance, 0.
    return v/(1+q*v*duration), math.log1p(q*v*duration)/q, 0.


def _phase_samples(segments, interval):
    import numpy as np
    rows = []
    for segment in segments:
        duration = segment['duration_s']
        ts = np.linspace(0., duration, max(2, int(math.ceil(duration/interval))+1))
        v, acc, jerk = (segment[k] for k in ('start_speed_m_s', 'start_acceleration_m_s2', 'jerk_m_s3'))
        rows.append((segment['start_time_s']+ts,
                     segment['start_position_m']+v*ts+.5*acc*ts**2+jerk*ts**3/6,
                     v+acc*ts+.5*jerk*ts**2, acc+jerk*ts))
    return tuple(np.concatenate([r[i] for r in rows]) for i in range(4))


def _hold(inputs, reason, **details):
    return dict(schema=SCHEMA, status='hold', study_pass=False,
                numerically_feasible=False, inputs=inputs, reason=reason,
                physical_output_authorised=False, **FLAGS, **details)


@lru_cache(maxsize=8192)
def _trajectory_cached(distance, runtime, car_mass, cars, acceleration, deceleration,
                       jerk, grade, speed_limit, trace, constant_per_car,
                       quadratic_per_car, motoring_eta, generating_eta, trace_interval):
    import numpy as np
    from scipy.integrate import quad
    from scipy.optimize import least_squares
    mass = car_mass*cars
    drag_constant, quadratic = constant_per_car*cars, quadratic_per_car*cars
    constant = drag_constant+mass*G*grade
    inputs = dict(distance_m=distance, runtime_s=runtime, car_mass_kg=car_mass, cars=cars,
                  train_mass_kg=mass, acceleration_m_s2=acceleration,
                  deceleration_m_s2=deceleration, jerk_m_s3=jerk,
                  grade=grade, speed_limit_kmh=speed_limit)
    vmax = speed_limit/3.6

    def parts(speed, coast_time):
        launch = _segments(0., 0., _launch(speed, mass, acceleration, jerk, constant, quadratic))
        receiving_speed, coast_distance, stopped = _coast(speed, coast_time, mass, constant, quadratic)
        braking = _segments(receiving_speed, -(constant+quadratic*receiving_speed**2)/mass,
                            _brake(receiving_speed, mass, deceleration, jerk, constant, quadratic))
        return launch, receiving_speed, coast_distance, stopped, braking

    def residual(values):
        speed, coast_time = values
        try:
            launch, _, coast_distance, stopped, braking = parts(speed, coast_time)
        except ValueError:
            return [100., 100.]
        return [(launch[1]+coast_time+braking[1]-runtime+stopped)/runtime,
                (launch[2]+coast_distance+braking[2]-distance)/distance]

    starts = [min(vmax*.95, max(1., distance/runtime*1.35)), min(vmax*.99, distance/runtime*1.8)]
    solutions = []
    for initial in starts:
        initial_coast = min(runtime*.9, max(.01, runtime-initial/acceleration-initial/deceleration))
        solution = least_squares(residual, [initial, initial_coast],
                                 bounds=([.01, 0.], [vmax, runtime]),
                                 xtol=1e-10, ftol=1e-10, gtol=1e-10, max_nfev=100)
        solutions.append(solution)
        if max(abs(v) for v in residual(solution.x)) < 1e-8:
            break
    solution = min(solutions, key=lambda value: sum(v*v for v in residual(value.x)))
    if max(abs(v) for v in residual(solution.x)) > 1e-7:
        return _hold(inputs, 'No launch/coast/arrival solution within the speed, jerk and acceleration bounds',
                     normalised_distance_time_residual=list(map(float, residual(solution.x))))
    speed, coast_time = map(float, solution.x)
    launch, receiving_speed, coast_distance, stopped, braking = parts(speed, coast_time)
    if stopped > 1e-8 or coast_time <= 0:
        return _hold(inputs, 'Unpowered span stops before the receiving motor or has no coasting interval')
    launch_segments, launch_time, launch_distance = launch
    brake_segments, brake_time, brake_distance = braking

    def work(segments):
        values = []
        for segment in segments:
            v, a, jj, duration = (segment[k] for k in ('start_speed_m_s', 'start_acceleration_m_s2', 'jerk_m_s3', 'duration_s'))
            velocity = lambda t: v+a*t+.5*jj*t*t
            force = lambda t: mass*(a+jj*t)+constant+quadratic*velocity(t)**2
            motor = quad(lambda t: force(t)*velocity(t), 0, duration, epsabs=1e-5)[0]
            drag = quad(lambda t: (drag_constant+quadratic*velocity(t)**2)*velocity(t), 0, duration, epsabs=1e-5)[0]
            positive = quad(lambda t: max(0., force(t)*velocity(t)), 0, duration, epsabs=1e-4)[0]
            negative = quad(lambda t: max(0., -force(t)*velocity(t)), 0, duration, epsabs=1e-4)[0]
            values.append((motor, drag, positive, negative))
        return tuple(sum(v[i] for v in values) for i in range(4))

    launch_work, launch_drag, launch_positive, launch_negative = work(launch_segments)
    braking_signed_work, braking_drag, brake_positive, brake_negative = work(brake_segments)
    coast_drag = .5*mass*(speed**2-receiving_speed**2)-mass*G*grade*coast_distance
    drag_work = launch_drag+coast_drag+braking_drag
    gradient_work = mass*G*grade*distance
    closure = launch_work+braking_signed_work-drag_work-gradient_work
    interval = .01
    lt, lx, lv, la = _phase_samples(launch_segments, interval)
    bt, bx, bv, ba = _phase_samples(brake_segments, interval)
    lf = mass*la+constant+quadratic*lv*lv
    bf = mass*ba+constant+quadratic*bv*bv
    lp, bp = lf*lv, bf*bv
    peak_speed = max(float(lv.max()), float(bv.max()), speed, receiving_speed)
    if peak_speed > vmax+1e-7 or min(float(lv.min()), float(bv.min())) < -1e-7:
        return _hold(inputs, 'Trajectory overspeed or reversal during a jerk ramp')
    mechanical_input = max(float(lp.max()), float(bp.max()))
    mechanical_brake = max(float((-lp).max()), float((-bp).max()))
    result = dict(schema=SCHEMA, status='study-pass', study_pass=True, numerically_feasible=True,
        inputs=inputs, phases=dict(launch=dict(duration_s=launch_time, distance_m=launch_distance),
            coast=dict(duration_s=coast_time, distance_m=coast_distance),
            braking=dict(duration_s=brake_time, distance_m=brake_distance)),
        peak_speed_kmh=peak_speed*3.6, launch_speed_kmh=speed*3.6,
        brake_entry_speed_kmh=receiving_speed*3.6,
        peak_traction_force_n=max(float(lf.max()), float(bf.max())),
        peak_braking_force_n=max(float((-lf).max()), float((-bf).max())),
        peak_mechanical_propulsion_kw=mechanical_input/1000,
        peak_traction_input_kw=mechanical_input/motoring_eta/1000,
        peak_mechanical_braking_kw=mechanical_brake/1000,
        peak_regenerated_dc_kw=mechanical_brake*generating_eta/1000,
        launch_mechanical_work_kwh=launch_work/3.6e6,
        launch_input_kwh=launch_positive/motoring_eta/3.6e6,
        receiving_brake_mechanical_work_kwh=-braking_signed_work/3.6e6,
        station_positive_input_kwh=(launch_positive+brake_positive)/motoring_eta/3.6e6,
        station_generated_dc_kwh=(launch_negative+brake_negative)*generating_eta/3.6e6,
        receiving_brake_dc_kwh=brake_negative*generating_eta/3.6e6,
        energy_balance=dict(motor_launch_j=launch_work, motor_braking_signed_j=braking_signed_work,
            passive_drag_j=drag_work, gravity_j=gradient_work, final_minus_initial_kinetic_j=0.,
            residual_j=closure, passed=abs(closure)<max(1.,abs(launch_work)*1e-7)),
        resistance=dict(constant_n_per_car=constant_per_car, quadratic_n_per_car_per_m_s_squared=quadratic_per_car),
        efficiencies=dict(motoring=motoring_eta, generating=generating_eta, measured=False),
        segments=dict(launch=launch_segments, braking=brake_segments),
        trace=[], physical_output_authorised=False, **FLAGS,
        scope='Prescribed-force longitudinal plant; stationary motors only. No electromagnetic, electrical, thermal or protection validation.',
        assumptions=['Constant grade uses g times slope as a small-angle screen',
            'Per-car drag summed over the consist; whole-consist aerodynamics unmeasured',
            'Constant efficiencies; no phase-current, voltage, copper-loss or reactive-power solution',
            'Station controller can realize the prescribed force and jerk; this is not demonstrated',
            'Zero-speed continuation of the drag law is not a parking model'])
    result.update(moving_seconds=runtime, runtime_s=runtime,
        launch_input_kwh_train=result['launch_input_kwh'],
        brake_recovered_kwh_train=result['receiving_brake_dc_kwh'],
        launch_duration_s=launch_time, brake_duration_s=brake_time)
    if trace:
        def records(t, x, v, acc, phase):
            force = mass*acc+constant+quadratic*v*v
            mechanical = force*v
            return dict(time_s=float(t), position_m=float(x), speed_m_s=float(v),
                        acceleration_m_s2=float(acc), motor_force_n=float(force),
                        mechanical_kw=float(mechanical/1000),
                        input_kw=float(max(0.,mechanical)/motoring_eta/1000),
                        regenerated_dc_kw=float(max(0.,-mechanical)*generating_eta/1000), phase=phase)
        ltrace = _phase_samples(launch_segments, trace_interval)
        for row in zip(*ltrace):
            result['trace'].append(records(*row, 'launch'))
        for t in np.linspace(0.,coast_time,max(2,int(math.ceil(coast_time/trace_interval))+1)):
            vv,xx,_ = _coast(speed,float(t),mass,constant,quadratic)
            result['trace'].append(dict(time_s=launch_time+float(t),position_m=launch_distance+xx,
                speed_m_s=vv,acceleration_m_s2=-(constant+quadratic*vv*vv)/mass,
                motor_force_n=0.,mechanical_kw=0.,input_kw=0.,regenerated_dc_kw=0.,phase='coast'))
        btrace = _phase_samples(brake_segments, trace_interval)
        for t,x,v,acc in zip(*btrace):
            result['trace'].append(records(t+launch_time+coast_time,x+launch_distance+coast_distance,v,acc,'braking'))
    result['study_pass'] = bool(result['energy_balance']['passed'])
    return result


def trajectory(*, distance_m=1000., runtime_s=90., car_mass_kg=26200., cars=6,
               acceleration=.8, deceleration=.8, jerk=.6, grade=0.,
               speed_limit_kmh=80., record_trace=True, motoring_efficiency=None,
               generating_efficiency=None, resistance_constant_n_per_car=None,
               resistance_quadratic_n_per_car=None):
    """Return a bounded longitudinal solution, or an explicit hold if infeasible.

    Invalid/malformed inputs raise ValueError. A physically impossible route under
    the declared numerical plant returns study_pass=False; it never adds traction
    during the nominally unpowered coast. Cached results are copied for callers.
    """
    a = load()['motion']
    values = [_finite(distance_m,'distance',100,10000), _finite(runtime_s,'runtime',20,600),
        _finite(car_mass_kg,'car mass',5000,100000), _integer(cars,'cars',1,12),
        _finite(acceleration,'acceleration',.1,2), _finite(deceleration,'deceleration',.1,2),
        _finite(jerk,'jerk',.1,2), _finite(grade,'grade',-.1,.1),
        _finite(speed_limit_kmh,'speed limit',10,160)]
    if type(record_trace) is not bool:
        raise ValueError('explicit trace flag required')
    constant=a['resistance_constant_n_per_car'] if resistance_constant_n_per_car is None else _finite(
        resistance_constant_n_per_car,'constant resistance',1,10000)
    quadratic=a['resistance_quadratic_n_per_car'] if resistance_quadratic_n_per_car is None else _finite(
        resistance_quadratic_n_per_car,'quadratic resistance',.01,100)
    eta=a['motoring_efficiency'] if motoring_efficiency is None else _finite(motoring_efficiency,'motoring efficiency',.1,1)
    regen=a['generating_efficiency'] if generating_efficiency is None else _finite(generating_efficiency,'generating efficiency',.1,1)
    result = _trajectory_cached(*values, record_trace, constant, quadratic, eta, regen,
        a['published_trace_interval_s'])
    return deepcopy(result)


def _overlap(positions, bands, start, end):
    import numpy as np
    x = np.asarray(positions)[:,None]
    return np.maximum(0.,np.minimum(x+bands[:,1],end)-np.maximum(x+bands[:,0],start)).sum(axis=1)


def magnetic_overlap(t, a=None):
    """Exact rectangular band intersections sampled at <=10 ms, not a motor map."""
    import numpy as np
    from scipy.optimize import minimize
    a = a or load()
    v, s = a['vehicle'], a['station']
    cars=t['inputs']['cars'];length=cars*v['body_length_m']+(cars-1)*v['coupling_gap_m']
    band=v['magnetic_band_m_per_car'];offset=(v['body_length_m']-band)/2
    pitch=v['body_length_m']+v['coupling_gap_m']
    bands=np.array([[-offset-band-i*pitch,-offset-i*pitch] for i in range(cars)])
    density=s['equivalent_envelope_force_n_m']*length/(band*cars)
    base=dict(status='hold',conditional_force_density_n_per_envelope_m=s['equivalent_envelope_force_n_m'],
        actual_active_band_force_density_n_m=density,magnetic_bands_relative_to_front_m=bands.tolist(),
        train_length_assumption_m=length,magnetic_fill_fraction=band*cars/length,
        winding_start_m=s['winding_start_m'],winding_end_m=s['winding_end_m'],
        force_map_validated=False,phase_registration_validated=False,
        current_voltage_thermal_duty_validated=False,engineering_force_reserve_accepted=False,**FLAGS)
    if not t['study_pass']:
        return dict(base,reason='No feasible longitudinal demand to size',study_pass=False)
    mass=t['inputs']['train_mass_kg'];motion=a['motion'];grade=t['inputs']['grade']
    drag=t['resistance']['constant_n_per_car']*cars+mass*G*grade
    quadratic=t['resistance']['quadratic_n_per_car_per_m_s_squared']*cars
    lt,lx,lv,la=_phase_samples(t['segments']['launch'],motion['overlap_sample_interval_s'])
    bt,bx,bv,ba=_phase_samples(t['segments']['braking'],motion['overlap_sample_interval_s'])
    bx-=t['phases']['braking']['distance_m']
    lf=np.abs(mass*la+drag+quadratic*lv*lv);bf=np.abs(mass*ba+drag+quadratic*bv*bv)
    total_capacity=band*cars*density
    if max(float(lf.max()),float(bf.max()))>total_capacity:
        return dict(base,reason='Assumed force density cannot deliver peak force even at full overlap',study_pass=False)
    def good(x,f,left,right):
        return float(np.min(_overlap(x,bands,left,right)*density-f))>=-1e-5
    # At arrival x<=0 and departure x>=0. Requiring A<=-L and B>=0 makes
    # their limiting ends independent and admits monotone bracketed searches.
    left_lo,left_hi=-length-t['phases']['braking']['distance_m'],-length
    right_lo,right_hi=0.,t['phases']['launch']['distance_m']
    for _ in range(55):
        mid=(left_lo+left_hi)/2
        if good(bx,bf,mid,0.):left_lo=mid
        else:left_hi=mid
        mid=(right_lo+right_hi)/2
        if good(lx,lf,-length,mid):right_hi=mid
        else:right_lo=mid
    # Allow partial engagement already at the berth. This matters for the
    # economy case: forcing the winding to contain the complete parked train
    # would overstate its minimum. Retain all band gaps in both constraints.
    def margins_at(ends):
        left,right=ends
        return np.concatenate((_overlap(lx,bands,left,right)*density-lf,
                               _overlap(bx,bands,left,right)*density-bf))/max(1.,total_capacity)
    search=minimize(lambda ends:ends[1]-ends[0],[left_lo,right_hi],method='SLSQP',
        bounds=[(-length-t['phases']['braking']['distance_m'],0.),(0.,t['phases']['launch']['distance_m'])],
        constraints=[dict(type='ineq',fun=margins_at)],
        options=dict(ftol=1e-9,maxiter=200))
    converged=bool(search.success and float(np.min(margins_at(search.x)))>=-1e-7)
    if converged:left_lo,right_hi=map(float,search.x)
    start,end=s['winding_start_m'],s['winding_end_m']
    margins={}
    for name,x,f in [('launch',lx,lf),('braking',bx,bf)]:
        active=f>1.
        margins[name]=float(np.min(_overlap(x,bands,start,end)[active]*density/f[active])-1.)
    passed=all(value>=-1e-7 for value in margins.values())
    return dict(base,status='conditional-study-pass' if passed else 'hold',study_pass=passed,
        reason=None if passed else 'Rounded winding cannot deliver the sampled force demand at assumed force density',
        minimum_winding_start_m=left_lo if converged else None,
        minimum_winding_end_m=right_hi if converged else None,
        minimum_winding_length_m=right_hi-left_lo if converged else None,
        winding_search_feasible_upper_bound_m=right_hi-left_lo,
        winding_search_converged=converged,
        winding_minimum_scope='Sampled piecewise-linear overlap numerical optimum; no electrical, thermal or fault reserve',
        full_engagement_winding_length_m=length+t['phases']['launch']['distance_m']+t['phases']['braking']['distance_m'],
        rounded_winding_length_m=end-start,minimum_force_reserve_fraction=margins,
        sample_interval_max_s=motion['overlap_sample_interval_s'],
        samples_evaluated=len(lx)+len(bx),
        motor_faces_per_direction=2,
        installed_direction_m_per_two_direction_station=2*(end-start),
        installed_face_m_per_two_direction_station=4*(end-start),
        addressable_sections_per_two_direction_station=2*math.ceil((end-start)/s['electrical_section_m']),
        individual_face_cassettes_per_two_direction_station=4*math.ceil((end-start)/s['mechanical_cassette_m']))


def _time_at_position(t, position):
    """Front clearance from the same trajectory, never an occupancy proof."""
    from scipy.optimize import brentq
    p=t['phases'];mass=t['inputs']['train_mass_kg'];cars=t['inputs']['cars']
    constant=t['resistance']['constant_n_per_car']*cars+mass*G*t['inputs']['grade']
    quadratic=t['resistance']['quadratic_n_per_car_per_m_s_squared']*cars
    if position>t['inputs']['distance_m'] or position<0:return None
    if position<=p['launch']['distance_m']:
        for seg in t['segments']['launch']:
            v,acc,jj,duration=(seg[k] for k in ('start_speed_m_s','start_acceleration_m_s2','jerk_m_s3','duration_s'))
            dx=_step(v,acc,jj,duration)[2]
            if seg['start_position_m']+dx>=position-1e-8:
                target=max(0.,position-seg['start_position_m'])
                if target<=1e-10:return seg['start_time_s']
                return seg['start_time_s']+brentq(lambda tt:_step(v,acc,jj,tt)[2]-target,0.,duration)
    target=position-p['launch']['distance_m']
    if target<=p['coast']['distance_m']:
        return p['launch']['duration_s']+brentq(lambda tt:_coast(t['launch_speed_kmh']/3.6,tt,mass,constant,quadratic)[1]-target,0.,p['coast']['duration_s'])
    target-=p['coast']['distance_m']
    for seg in t['segments']['braking']:
        v,acc,jj,duration=(seg[k] for k in ('start_speed_m_s','start_acceleration_m_s2','jerk_m_s3','duration_s'))
        if seg['start_position_m']+_step(v,acc,jj,duration)[2]>=target-1e-8:
            return (p['launch']['duration_s']+p['coast']['duration_s']+seg['start_time_s']+
                    brentq(lambda tt:_step(v,acc,jj,tt)[2]-(target-seg['start_position_m']),0.,duration))
    return None


def station_costs(a=None):
    """Separate installed-channel targets; no MW-to-price claim or quotation."""
    a=a or load();c,s=a['cost'],a['station'];length=s['winding_end_m']-s['winding_start_m']
    sections=2*math.ceil(length/s['electrical_section_m']);rates=[]
    for i,label in enumerate(('aggressive-target','middle-target','stress-target')):
        common=dict(active_stators=2*length*c['stator_usd_per_direction_m'][i],
            supply_rectifier_dc=c['supply_rectifier_dc_usd'][i],
            braking=c['brake_chopper_resistor_usd'][i],
            charging=c['charging_interfaces_usd'][i],
            motion_sensing_safety=c['motion_sensing_safety_usd'][i],
            thermal_installation_acceptance=c['thermal_installation_acceptance_usd'][i])
        topologies={}
        choices=[('B-two-fixed-groups',c['fixed_group_bridges'],c['fixed_group_kw_equivalent_per_bridge'],False),
            *[(f'C-routed-{n}-banks',n,c['routed_kw_equivalent_per_bank'],True) for n in c['routed_bank_counts']],
            ('D-independent-sections',sections,c['independent_kw_equivalent_per_section'],False)]
        for name,count,rating,routed in choices:
            rows=dict(common,bridges=count*rating*c['bridge_usd_per_kw_equivalent'][i],
                      output_routing=c['routing_assemblies_usd'][i] if routed else 0.)
            subtotal=sum(rows.values())
            topologies[name]=dict(rows_usd=rows,direct_subtotal_usd=subtotal,
                subtotal_with_reserve_usd=subtotal*(1+c['estimating_reserve_fraction']),
                installed_bridges=count,assumed_kw_equivalent_per_bridge=rating,
                phase_current_kva_rating_qualified=False,**FLAGS)
        rates.append(dict(sensitivity=label,topologies=topologies))
    return dict(currency=c['currency'],basis=c['basis'],supplier_quote=False,
        estimating_reserve_fraction=c['estimating_reserve_fraction'],sensitivity_cases=rates,
        charging_rate_basis=c['charging_rate_basis'],complete_railway_price=False,
        unpriced_topologies=['A-whole-zone winding: installed current/kVA and winding losses not established'],
        exclusions=['development and qualification','factory capital and tooling','utility reinforcement',
            'station buildings/platforms/access','land and air rights','depot/recovery/fleet',
            'taxes/duties/finance/programme costs','actual winding electrical/thermal and 45-second charging rating'],**FLAGS)


def evaluate(c=None, *, distance_m=1000., cars=None, runtime_s=None, grade=0.,
             headway_s=190., car_mass_kg=None,winding_length_m=None,acceleration=None):
    """Coordinate trajectory, band overlap, occupancy planning and station scope."""
    a=deepcopy(load());v,m,s=a['vehicle'],a['motion'],a['station']
    if c is not None:
        cv,cp=c['vehicle'],c['power']
        v['cars']=cv['cars_per_train'];v['body_length_m']=cv['nominal_car_length_m']
        m.update(acceleration_m_s2=cv['maximum_initial_acceleration_m_s2'],
                 deceleration_m_s2=cv['service_deceleration_study_m_s2'],
                 jerk_m_s3=cv.get('jerk_study_m_s3',m['jerk_m_s3']),
                 speed_limit_kmh=cv['service_speed_study_kmh'])
        s.update(hot_services_kw_per_car=cp['hot_hotel_kw_per_car'],
            services_battery_kwh_per_car=cp.get('services_battery_kwh_per_car',s['services_battery_kwh_per_car']),
            battery_eol_fraction=cp['eol_capacity_fraction'],soc_low=cp['normal_soc_low'],soc_high=cp['normal_soc_high'],
            dwell_s=cp['station_dwell_seconds'],connected_charging_s=cp['charger_effective_seconds'])
        m.update(motoring_efficiency=cp.get('station_drive_efficiency',m['motoring_efficiency']),
            generating_efficiency=cp.get('station_generating_efficiency',m['generating_efficiency']),
            resistance_constant_n_per_car=cp.get('passive_rail_drag_study_n_per_car',m['resistance_constant_n_per_car']),
            resistance_quadratic_n_per_car=.5*cp.get('air_density_study_kg_m3',1.2)*cp.get('drag_area_study_m2_per_car',3.))
        if car_mass_kg is None:
            from . import model
            car_mass_kg=model.mass(c,c['mass']['ferrite_base'],s['services_battery_kwh_per_car'])['aw3_kg']
        if runtime_s is None:runtime_s=cv.get('runtime_reference_seconds',m['runtime_s'])
    if winding_length_m is not None:
        length=_finite(winding_length_m,'winding length',100,600)
        s['winding_start_m']=-125.-(length-200.)/2;s['winding_end_m']=75.+(length-200.)/2
    if acceleration is not None:m['acceleration_m_s2']=_finite(acceleration,'acceleration',.1,2)
    cars=v['cars'] if cars is None else cars
    runtime_s=m['runtime_s'] if runtime_s is None else runtime_s
    car_mass_kg=v['car_mass_kg'] if car_mass_kg is None else car_mass_kg
    _finite(headway_s,'headway',30,1200)
    if s['connected_charging_s']>s['dwell_s']:
        raise ValueError('charging window longer than dwell')
    t=trajectory(distance_m=distance_m,runtime_s=runtime_s,car_mass_kg=car_mass_kg,cars=cars,
        acceleration=m['acceleration_m_s2'],deceleration=m['deceleration_m_s2'],jerk=m['jerk_m_s3'],
        grade=grade,speed_limit_kmh=m['speed_limit_kmh'],motoring_efficiency=m['motoring_efficiency'],
        generating_efficiency=m['generating_efficiency'],resistance_constant_n_per_car=m['resistance_constant_n_per_car'],
        resistance_quadratic_n_per_car=m['resistance_quadratic_n_per_car'])
    overlap=magnetic_overlap(t,a)
    length=cars*v['body_length_m']+(cars-1)*v['coupling_gap_m']
    clearance=_time_at_position(t,length+s['winding_end_m']) if t['study_pass'] else None
    headway_min=runtime_s+s['dwell_s']+clearance+s['release_allowance_s'] if clearance is not None else None
    services=cars*s['hot_services_kw_per_car'];disconnected=s['dwell_s']-s['connected_charging_s']
    battery_time=runtime_s+(0. if s['independent_shore_supply_during_disconnected_dwell'] else disconnected)
    replacement=services*battery_time/3600
    battery_charging=replacement*3600/s['connected_charging_s']
    interface=battery_charging+services
    usable=s['services_battery_kwh_per_car']*s['battery_eol_fraction']*(s['soc_high']-s['soc_low'])
    consumed_per_car=replacement/cars;remaining=usable-consumed_per_car
    reserve=s['hot_services_kw_per_car']*s['protected_services_reserve_minutes']/60
    battery_ok=remaining>=reserve
    charging=dict(services_kw_per_train=services,moving_services_kwh=services*runtime_s/3600,
        disconnected_dwell_s=disconnected,battery_supplied_seconds_per_cycle=battery_time,
        replacement_kwh_per_train=replacement,battery_charging_kw_per_train=battery_charging,
        direct_services_kw_per_train=services,connected_interface_kw_per_train=interface,
        battery_charge_c_rate=battery_charging/(cars*s['services_battery_kwh_per_car']),
        charger_losses_included=False,charge_taper_and_repeated_duty_validated=False,
        independent_disconnected_dwell_shore_supply=s['independent_shore_supply_during_disconnected_dwell'])
    battery=dict(gross_kwh_per_car=s['services_battery_kwh_per_car'],eol_usable_soc_window_kwh_per_car=usable,
        cycle_consumption_kwh_per_car=consumed_per_car,remaining_before_recharge_kwh_per_car=remaining,
        protected_services_reserve_minutes=s['protected_services_reserve_minutes'],
        protected_services_reserve_kwh_per_car=reserve,screen_pass=battery_ok,
        reserve_basis='Explicit project ten-minute hot-services sensitivity; rescue mission and required emergency reserve unaccepted',
        accepted=False)
    traffic=dict(scheduled_headway_s=headway_s,clearance_front_distance_m=length+s['winding_end_m'],
        time_until_tail_clears_winding_s=clearance,planning_minimum_headway_s=headway_min,
        planning_headway_margin_s=headway_s-headway_min if headway_min is not None else None,
        screen_pass=headway_min is not None and headway_s>=headway_min,
        normal_passengers_per_train=cars*(c['vehicle']['aw2_passengers_per_car'] if c else 120),
        trains_per_hour=3600/headway_s,release_requires_positive_full_consist_evidence=True,
        timer_is_clearance_proof=False,physical_resource_controller_accepted=False)
    traffic['normal_passengers_per_hour_direction']=traffic['normal_passengers_per_train']*traffic['trains_per_hour']
    power=None
    if t['study_pass']:
        average=(t['station_positive_input_kwh']+services*(runtime_s+s['dwell_s'])/3600)*2*3600/headway_s
        power=dict(peak_traction_input_kw=t['peak_traction_input_kw'],
            one_launch_plus_opposite_connected_services_kw=t['peak_traction_input_kw']+interface,
            two_coincident_launches_kw=2*t['peak_traction_input_kw'],
            two_coincident_connected_services_kw=2*interface,
            average_two_direction_input_kw_before_station_loads_and_losses=average,
            brake_resistor_peak_dc_kw=t['peak_regenerated_dc_kw'],
            brake_resistor_energy_per_arrival_mj=t['receiving_brake_dc_kwh']*3.6,
            brake_reuse_credited=False,braking_independent_of_another_load_required=True,
            power_kva_and_repeated_thermal_rating_validated=False,
            station_loads_additional=True)
    passed=t['study_pass'] and overlap['study_pass'] and traffic['screen_pass'] and battery_ok
    return dict(schema=SCHEMA,status='conditional-study-pass' if passed else 'hold',study_pass=passed,
        trajectory=t,magnetic_overlap=overlap,traffic=traffic,charging=charging,battery=battery,
        station_power=power,costs=station_costs(a),physical_output_authorised=False,**FLAGS,
        missing_evidence=['measured ferrite force/flux/R/L/loss maps','motor current/voltage/kVA/thermal/fault ratings',
            'force and phase registration across coupler motion','actual route grade/wind/drag/tolerance envelopes',
            'receiving braking and grid-fault response','restart/rescue of a stopped unpowered-span train',
            'full-consist occupancy detection and committed launch interlocking',
            'qualified services battery, charging interface and reserve mission','supplier quotes and full-system cost'])


def study():
    """Small fixed benchmark, retaining infeasible cases and provisional targets."""
    cases=[]
    for name,options in [('reference-90s',{}),('economy-100s',dict(runtime_s=100.)),
        ('uphill-2-percent',dict(grade=.02)),('uphill-5-percent',dict(grade=.05)),
        ('downhill-5-percent',dict(grade=-.05))]:
        cases.append(dict(name=name,result=evaluate(**options)))
    return dict(schema=SCHEMA,source_sha256=sources(),assumptions=load(),cases=cases,
        runtime=dict(python=platform.python_version(),scipy=__import__('scipy').__version__),
        candidate_count=len(cases),conditional_pass_count=sum(row['result']['study_pass'] for row in cases),
        engineering_accepted_count=0,**FLAGS,
        scope='Reproducible station-powered longitudinal, overlap, charging and cost screens; not a qualified train or railway')


def _svg(t, quantity, title):
    """Standalone plots from executed trajectory, without illustrative geometry."""
    from html import escape
    trace=t.get('trace',[])
    if not trace:return '<svg xmlns="http://www.w3.org/2000/svg" width="900" height="180"><text x="20" y="50">No feasible trajectory</text></svg>\n'
    values=[row[quantity] for row in trace];lo=min(0.,min(values));hi=max(values)
    if hi-lo<1e-9:hi=lo+1
    points=' '.join(f'{65+800*row["time_s"]/t["inputs"]["runtime_s"]:.2f},{340-260*(row[quantity]-lo)/(hi-lo):.2f}' for row in trace)
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="920" height="420" viewBox="0 0 920 420" role="img" aria-label="{escape(title)}"><rect width="920" height="420" fill="#f6f9fc"/><text x="40" y="35" font-size="21">{escape(title)}</text><path d="M65 70V340H870" fill="none" stroke="#34485e"/><polyline points="{points}" fill="none" stroke="#087e8b" stroke-width="2"/><text x="65" y="365">0 s</text><text x="810" y="365">{t["inputs"]["runtime_s"]:g} s</text><text x="15" y="85">{hi:.1f}</text><text x="15" y="340">{lo:.1f}</text><text x="40" y="400" font-size="13">Prescribed-force numerical plant. Magnetic, electrical, thermal and physical acceptance open.</text></svg>\n'


def publish(output=OUTPUT):
    """Publish one bounded owned packet; writes manifest after payloads."""
    output=Path(output)
    if output.is_symlink():raise ValueError('station packet cannot be a symlink')
    output.mkdir(parents=True,exist_ok=True)
    if any(p.is_symlink() or not p.is_file() for p in output.iterdir()):
        raise ValueError('station packet must contain ordinary files only')
    if {p.name for p in output.iterdir()}-(FILES|{'manifest.json'}):
        raise ValueError('unexpected station packet inventory')
    before=sources();result=study();reference=result['cases'][0]['result'];t=reference['trajectory']
    text=(f'# Station-powered maglev study\n\n'
        f'The six-car flat 1 km reference takes {t["inputs"]["runtime_s"]:g} s and demands '
        f'{t["peak_traction_input_kw"]/1000:.3f} MW peak traction input at assumed 85% efficiency. '
        f'The train coasts {t["phases"]["coast"]["distance_m"]:.1f} m without commanded propulsion.\n\n'
        f'At 45 s connected charging in 60 s dwell, the services battery supplies 105 s per cycle. '
        f'Replacement is {reference["charging"]["replacement_kwh_per_train"]:.2f} kWh/train; '
        f'the connected interface needs {reference["charging"]["connected_interface_kw_per_train"]/1000:.2f} MW before losses. '
        f'The present 190 s schedule yields {reference["traffic"]["normal_passengers_per_hour_direction"]:,.0f} '
        f'normal passengers/hour/direction.\n\n'
        '![Executed speed history](overview.svg)\n\n![Executed motor power history](power.svg)\n\n'
        'The winding screen uses six actual rectangular magnetic bands and provisional force per overlap metre. '
        'The 200 m winding is a conditional layout, with no accepted magnetic force reserve or drive rating. '
        'Gradient failures remain recorded holds. Cost topologies are additional station scopes and unquoted targets.\n\n'
        'The result retains analytical segments, energy balance, traces, exact assumptions and source hashes. '
        'No hardware I/O is present. Design completion, physical validation, manufacturing release and physical release are false.\n')
    payloads={'result.json.gz':gzip.compress(_encoded(result),mtime=0),
        'overview.svg':_svg(t,'speed_m_s','Executed flat-reference speed (m/s)').encode(),
        'power.svg':_svg(t,'mechanical_kw','Executed signed station motor power (kW)').encode(),
        'README.md':text.encode()}
    if before!=sources():raise ValueError('station sources changed during calculation')
    manifest=dict(schema=SCHEMA,sources_sha256=before,
        files_sha256={name:sha256(data).hexdigest() for name,data in payloads.items()},
        engineering_accepted_count=0,**FLAGS)
    for name,data in payloads.items():
        (output/name).write_bytes(data)
    (output/'manifest.json').write_bytes(_encoded(manifest))
    verify(output)
    return manifest


def verify(output=OUTPUT):
    output=Path(output)
    if output.is_symlink() or not output.is_dir():raise ValueError('station packet directory required')
    if {p.name for p in output.iterdir()}!=FILES|{'manifest.json'}:
        raise ValueError('station packet inventory differs')
    if any(p.is_symlink() or not p.is_file() or p.stat().st_size>MAX_RAW for p in output.iterdir()):
        raise ValueError('bounded ordinary station packet files required')
    manifest=json.loads((output/'manifest.json').read_text())
    if manifest.get('schema')!=SCHEMA or manifest.get('sources_sha256')!=sources():
        raise ValueError('station packet source identity differs')
    if set(manifest.get('files_sha256',{}))!=FILES:
        raise ValueError('station payload receipt differs')
    for name,digest in manifest['files_sha256'].items():
        if _digest(output/name)!=digest:raise ValueError('station payload checksum differs')
    with gzip.open(output/'result.json.gz','rb') as handle:
        raw=handle.read(MAX_RAW+1)
    if len(raw)>MAX_RAW:raise ValueError('station result exceeds bound')
    result=json.loads(raw)
    if result.get('source_sha256')!=manifest['sources_sha256'] or result.get('assumptions')!=load():
        raise ValueError('station result input identity differs')
    if any(result.get(key) is not False or manifest.get(key) is not False for key in FLAGS):
        raise ValueError('station study asserts an engineering release')
    cases=result.get('cases',[])
    if len(cases)!=5 or [r.get('name') for r in cases]!=['reference-90s','economy-100s','uphill-2-percent','uphill-5-percent','downhill-5-percent']:
        raise ValueError('station benchmark inventory differs')
    if result.get('engineering_accepted_count')!=0 or manifest.get('engineering_accepted_count')!=0:
        raise ValueError('station acceptance must remain open')
    for row in cases:
        r=row['result'];t=r['trajectory']
        if any(r.get(key) is not False or t.get(key) is not False for key in FLAGS):
            raise ValueError('station candidate asserts release')
        if t['study_pass'] and (not t['energy_balance']['passed'] or abs(t['energy_balance']['residual_j'])>1):
            raise ValueError('station energy balance failed')
        if t.get('physical_output_authorised') is not False:
            raise ValueError('station packet authorizes physical output')
    if not cases[0]['result']['study_pass'] or cases[3]['result']['study_pass'] or cases[4]['result']['study_pass']:
        raise ValueError('reference/control benchmark classification differs')
    return manifest
