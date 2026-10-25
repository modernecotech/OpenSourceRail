"""Map-bound suspension diagnostics; no passive stability or physical release credit.

Coordinates are gap increasing downwards, lateral displacement rightwards, upward
F_z and rightward F_y. Every result concerns the supplied physical map unit; this
module never multiplies force or power by an assumed train/module count.
"""
from hashlib import sha256
from copy import deepcopy
from itertools import product
import cmath
import json
import math


AXES = ('gap_m', 'lateral_m', 'current_A', 'temperature_C')
QUANTITIES = ('F_z_N', 'F_y_N', 'dF_z_dgap_N_per_m', 'dF_z_dcurrent_N_per_A',
              'dF_y_dlateral_N_per_m', 'dF_y_dgap_N_per_m', 'dF_z_dlateral_N_per_m',
              'dF_y_dcurrent_N_per_A', 'dflux_dgap_Wb_turn_per_m',
              'dflux_dlateral_Wb_turn_per_m', 'L_H', 'R_ohm')
FLAGS = dict(physical_accepted=False, configuration_adopted=False,
             cooling_eliminated=False, passive_levitation_established=False)
SERVICE_CONTEXT = dict(cars=6, body_length_m=17, normal_passengers_per_car=120,
                       comparison_pphpd=14400, reference_headway_s=180,
                       changed_speed_or_route_adopted=False)
REFERENCES = [
    dict(url='https://www.jstage.jst.go.jp/article/ieejias1987/120/4/120_4_509/_article/-char/en',
         doi='10.1541/ieejias.120.509',
         applicability='PM weight balance at a load-dependent gap still requires active control; multi-support modal constraints matter. No railway validation transfers.'),
    dict(url='https://www.precisionmechatronicslab.com/wp-content/publications/J05b.pdf',
         doi='10.1109/TMECH.2004.835341',
         applicability='Small-motion reciprocal transducer and shunt model. Its tuned RC/synthetic-impedance experiment does not establish simple-resistor railway damping or static stability.'),
]


class MapUnavailable(ValueError):
    """The supplied numerical map cannot support the requested calculation."""


def number(value, name, *, positive=False, nonnegative=False):
    if type(value) not in (int, float) or not math.isfinite(value):
        raise ValueError('finite '+name+' required')
    if positive and value <= 0 or nonnegative and value < 0:
        raise ValueError('positive/nonnegative '+name+' required')
    return float(value)


def _identity(value):
    return sha256((json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False)+'\n').encode()).hexdigest()


def _blend(values):
    """Interpolate scalar/circuit dictionaries; missing quantities stay unknown."""
    if any(value is None for _, value in values):
        return None
    first = values[0][1]
    if isinstance(first, dict):
        keys = set(first)
        if any(not isinstance(value, dict) or set(value) != keys for _, value in values):
            raise MapUnavailable('inconsistent circuit quantity inventory')
        return {key: _blend([(weight, value[key]) for weight, value in values]) for key in sorted(keys)}
    return sum(weight*number(value, 'map quantity') for weight, value in values)


class FieldMap:
    """Complete regular grid with closed-domain multilinear interpolation only.

    Required metadata: axes, rows, map_id, unit_scope, interpolation_usable=True
    and numerical_status='converged'. A usable numerical map is still conditional
    on its material/2D/3D domain and independent physical correlation.
    """
    def __init__(self, data):
        if not isinstance(data, dict) or data.get('interpolation_usable') is not True or data.get('numerical_status') != 'converged':
            raise MapUnavailable('converged numerically usable field map required')
        if not data.get('map_id') or not data.get('unit_scope'):
            raise MapUnavailable('explicit map identity and physical unit scope required')
        self.data = {key: deepcopy(data[key]) for key in ('map_id', 'unit_scope', 'control_circuit_id',
                     'geometry_id', 'domain_id', 'source_sha256', 'series_circuits', 'length_x_m') if key in data}
        self.axes = {}
        for key in AXES:
            values = data.get('axes', {}).get(key)
            if not isinstance(values, list) or not 1 <= len(values) <= 100:
                raise MapUnavailable('bounded regular map axis required: '+key)
            axis = [number(value, key) for value in values]
            if axis != sorted(set(axis)) or key == 'gap_m' and axis[0] <= 0:
                raise MapUnavailable('strictly increasing positive-gap map axes required')
            self.axes[key] = axis
        if len(self.axes['gap_m']) < 2 or len(self.axes['current_A']) < 2:
            raise MapUnavailable('gap/current map requires at least two samples each')
        expected = math.prod(len(axis) for axis in self.axes.values())
        if expected > 100000 or len(data.get('rows', [])) != expected:
            raise MapUnavailable('complete bounded Cartesian field map required')
        self.rows = {}
        for row in data['rows']:
            row = deepcopy(row)
            key = tuple(number(row.get(name), name) for name in AXES)
            if key in self.rows or any(value not in self.axes[name] for name, value in zip(AXES, key)):
                raise MapUnavailable('duplicate or off-grid map row')
            if row.get('numerical_status', 'converged') != 'converged':
                raise MapUnavailable('nonconverged field/derivative row')
            if row.get('interpolation_usable', True) is not True:
                raise MapUnavailable('numerically unusable field/derivative row')
            number(row.get('F_z_N'), 'F_z_N')
            self.rows[key] = row
        self.quantity_digest = _identity(self.data | dict(axes=self.axes, rows=list(self.rows.values())))

    def sample(self, *, gap_m, lateral_m, current_A, temperature_C):
        coordinates = dict(gap_m=gap_m, lateral_m=lateral_m, current_A=current_A, temperature_C=temperature_C)
        brackets = []
        for name in AXES:
            value = number(coordinates[name], name)
            axis = self.axes[name]
            if value < axis[0] or value > axis[-1]:
                raise MapUnavailable('out-of-map '+name)
            if value in axis:
                brackets.append([(value, 1.)])
            else:
                upper = next(i for i, x in enumerate(axis) if x > value)
                low, high = axis[upper-1:upper+1]
                fraction = (value-low)/(high-low)
                brackets.append([(low, 1-fraction), (high, fraction)])
        rows = [(math.prod(weight for _, weight in corner), self.rows[tuple(value for value, _ in corner)])
                for corner in product(*brackets)]
        return coordinates | {quantity: _blend([(weight, row.get(quantity)) for weight, row in rows])
                              for quantity in QUANTITIES}


def _map(value):
    return value if isinstance(value, FieldMap) else FieldMap(value)


def _scalar(point, name, field):
    value = point.get(name)
    if isinstance(value, dict):
        circuit = field.data.get('control_circuit_id')
        if circuit is None and len(value) == 1:
            circuit = next(iter(value))
        value = value.get(circuit)
    if value is None:
        raise MapUnavailable('unknown '+name+' for the selected control circuit')
    return number(value, name)


def _roots(axis, evaluate, target):
    values = [evaluate(x)-target for x in axis]
    roots = [x for x, value in zip(axis, values) if abs(value) <= max(1e-9, abs(target)*1e-12)]
    for x0, x1, f0, f1 in zip(axis, axis[1:], values, values[1:]):
        if f0*f1 < 0:
            roots.append(x0-f0*(x1-x0)/(f1-f0))
    return sorted(set(roots))


def zero_current_equilibria(field_map, load_N, *, temperature_C, lateral_m=0., tolerance_m=0.):
    """Find zero-current force balance, never infer passive stability from it."""
    load = number(load_N, 'load_N', positive=True)
    reserve = number(tolerance_m, 'tolerance_m', nonnegative=True)
    try:
        field = _map(field_map)
        def point(gap, lateral=lateral_m, current=0.):
            return field.sample(gap_m=gap, lateral_m=lateral, current_A=current, temperature_C=temperature_C)
        roots = _roots(field.axes['gap_m'], lambda gap: point(gap)['F_z_N'], load)
        equilibria = []
        for gap in roots:
            p = point(gap)
            slope = p.get('dF_z_dgap_N_per_m')
            unstable = None if slope is None else slope < 0
            corners = []
            for actual_gap, lateral in product(sorted({gap-reserve, gap+reserve}), sorted({lateral_m-reserve, lateral_m+reserve})):
                try:
                    edge = point(actual_gap, lateral)
                    corrections = _roots(field.axes['current_A'], lambda current: point(actual_gap, lateral, current)['F_z_N'], load)
                    corners.append(dict(gap_m=actual_gap, lateral_m=lateral, force_error_N=edge['F_z_N']-load,
                                        current_balance_roots_A=corrections, within_map=True))
                except MapUnavailable as exc:
                    corners.append(dict(gap_m=actual_gap, lateral_m=lateral, within_map=False, reason=str(exc), current_balance_roots_A=[]))
            equilibria.append(dict(gap_m=gap, zero_current_A=0., F_z_N=p['F_z_N'],
                dF_z_dgap_N_per_m=slope, attractive_gap_mode_unstable=unstable,
                open_loop_gap_growth_rate_per_s=(math.sqrt(-slope/(load/9.80665)) if slope is not None and slope < 0 else None),
                growth_rate_mass_assumption='supported inertial mass = load_N / standard gravity; other inertial mass requires local_gap_model',
                passive_lateral_stiffness_N_per_m=(None if p['dF_y_dlateral_N_per_m'] is None else -p['dF_y_dlateral_N_per_m']),
                open_loop_coupled_modes=local_force_modes(p, mass_kg=load/9.80665),
                tolerance_corners=corners,
                tolerance_current_balance_available=all(row['within_map'] and row['current_balance_roots_A'] for row in corners),
                active_stabilisation_required=True, coupled_multisupport_stability_established=False))
        return dict(status='equilibria-found' if roots else 'no-zero-current-equilibrium', map_id=field.data['map_id'],
                    map_quantity_sha256=field.quantity_digest, unit_scope=field.data['unit_scope'], load_N=load,
                    temperature_C=temperature_C, lateral_m=lateral_m, tolerance_m=reserve, equilibria=equilibria,
                    local_interpolation_only=True, **FLAGS)
    except MapUnavailable as exc:
        return dict(status='held-field-map', reason=str(exc), equilibria=[], **FLAGS)


def local_force_modes(point, *, mass_kg):
    """Undamped gap/lateral modes of one lump; roll and whole-car modes excluded."""
    mass = number(mass_kg, 'mass_kg', positive=True)
    names = ('dF_z_dgap_N_per_m', 'dF_z_dlateral_N_per_m',
             'dF_y_dgap_N_per_m', 'dF_y_dlateral_N_per_m')
    if any(point.get(name) is None for name in names):
        return dict(status='unknown-cross-coupled-derivatives', asymptotically_stable=False, **FLAGS)
    fg, fzy, fyg, fyy = [number(point[name], name) for name in names]
    jacobian = [[-fg, -fzy], [fyg, fyy]]
    a, b, c, d = -fg/mass, -fzy/mass, fyg/mass, fyy/mass
    discriminant = cmath.sqrt((a+d)**2-4*(a*d-b*c))
    squared_rates = [((a+d)+discriminant)/2, ((a+d)-discriminant)/2]
    modes = [sign*cmath.sqrt(value) for value in squared_rates for sign in (1, -1)]
    return dict(status='conditional-local-two-coordinate-modes', force_jacobian_N_per_m=jacobian,
                modes_per_s=[dict(real=value.real, imaginary=value.imag) for value in modes],
                exponentially_unstable=any(value.real > 1e-9 for value in modes),
                asymptotically_stable=False,
                domain='One inertial lump with equal gap/lateral mass; no damping, roll, multiple supports, joints or flexible structure.', **FLAGS)


def local_gap_model(point, *, mass_kg, proportional_A_per_m, derivative_A_s_per_m,
                    current_loop_gain_ohm=0., control_circuit_id=None):
    """Three-state local model with finite current-loop bandwidth and ideal sensing.

    v=R*i_command + lambda_gap*gap_velocity + Kc*(i_command-i).
    Frozen R/L, exact model back-emf feedforward, no sensing delay or flexibility.
    The cubic Hurwitz test is a local mathematical test, not hardware validation.
    """
    mass = number(mass_kg, 'mass_kg', positive=True)
    kp = number(proportional_A_per_m, 'proportional gain')
    kd = number(derivative_A_s_per_m, 'derivative gain')
    gain = number(current_loop_gain_ohm, 'current-loop gain', nonnegative=True)
    class Scope:
        data = dict(control_circuit_id=control_circuit_id)
    if point.get('dF_z_dgap_N_per_m') is None or point.get('dF_z_dcurrent_N_per_A') is None:
        raise MapUnavailable('unknown field force derivative')
    fg = number(point['dF_z_dgap_N_per_m'], 'field gap derivative')
    fi = number(point['dF_z_dcurrent_N_per_A'], 'field current derivative')
    resistance = _scalar(point, 'R_ohm', Scope)
    inductance = _scalar(point, 'L_H', Scope)
    number(resistance, 'R_ohm', positive=True); number(inductance, 'L_H', positive=True)
    rate = (resistance+gain)/inductance
    a1, a2, a3 = rate, (fg+fi*rate*kd)/mass, rate*(fg+fi*kp)/mass
    stable = a1 > 0 and a2 > 0 and a3 > 0 and a1*a2 > a3
    return dict(state_order=['gap displacement_m', 'gap velocity_m_s', 'current deviation_A'],
                A_per_s=[[0., 1., 0.], [-fg/mass, 0., -fi/mass], [rate*kp, rate*kd, -rate]],
                characteristic_polynomial=[1., a1, a2, a3], hurwitz_strict=stable,
                open_loop_attractive_gap_unstable=fg < 0,
                ideal_current_closed_stiffness_N_per_m=fg+fi*kp,
                ideal_current_closed_damping_N_s_per_m=fi*kd, current_loop_rate_per_s=rate,
                domain='Frozen local derivatives at one supplied map point; ideal sensors/back-emf feedforward; no delay, joints or multisupport modes.', **FLAGS)


def _rk4(state, dt, derivative):
    k1 = derivative(state)
    k2 = derivative([x+dt*k/2 for x, k in zip(state, k1)])
    k3 = derivative([x+dt*k/2 for x, k in zip(state, k2)])
    k4 = derivative([x+dt*k for x, k in zip(state, k3)])
    return [x+dt*(a+2*b+2*c+d)/6 for x, a, b, c, d in zip(state, k1, k2, k3, k4)]


def _steps(duration_s, dt_s):
    duration = number(duration_s, 'duration_s', positive=True)
    dt = number(dt_s, 'dt_s', positive=True)
    ratio = duration/dt
    if not math.isfinite(ratio) or not 1 <= ratio <= 200000:
        raise ValueError('bounded finite duration/time-step ratio required')
    count = round(ratio)
    if not 1 <= count <= 200000 or duration > 60 or not math.isclose(count*dt, duration, rel_tol=1e-10, abs_tol=1e-12):
        raise ValueError('integral 1..200000 steps and duration <=60 s required')
    return count, dt


def simulate_gap(field_map, scenario):
    """Bounded nonlinear vertical/RL model; any clamp or map exit is a failed hold."""
    count, dt = _steps(scenario['duration_s'], scenario['dt_s'])
    mass = number(scenario['mass_kg'], 'mass_kg', positive=True)
    load = number(scenario['load_N'], 'load_N', positive=True)
    kp = number(scenario['proportional_A_per_m'], 'proportional gain')
    kd = number(scenario['derivative_A_s_per_m'], 'derivative gain')
    current_limit = number(scenario['current_limit_A'], 'current_limit_A', positive=True)
    voltage_limit = number(scenario['voltage_limit_V'], 'voltage_limit_V', positive=True)
    gain = number(scenario.get('current_loop_gain_ohm', 0.), 'current-loop gain', nonnegative=True)
    gap0 = number(scenario['equilibrium_gap_m'], 'equilibrium_gap_m', positive=True)
    current0 = number(scenario.get('equilibrium_current_A', 0.), 'equilibrium_current_A')
    lateral, temperature = scenario['lateral_m'], scenario['temperature_C']
    status, reason, elapsed, model = 'completed-local-scenario', None, 0., None
    records = []
    state = [gap0+scenario.get('initial_displacement_m', 0.), scenario.get('initial_velocity_m_s', 0.),
             current0, 0., 0., 0., 0.]  # integrals: I, I², I²R, VI
    try:
        field = _map(field_map)
        def sample(gap, current):
            return field.sample(gap_m=gap, lateral_m=lateral, current_A=current, temperature_C=temperature)
        equilibrium = sample(gap0, current0)
        if abs(equilibrium['F_z_N']-load) > max(1e-6, load*1e-7):
            raise MapUnavailable('requested linearisation is not a force equilibrium')
        model = local_gap_model(equilibrium, mass_kg=mass, proportional_A_per_m=kp,
            derivative_A_s_per_m=kd, current_loop_gain_ohm=gain,
            control_circuit_id=field.data.get('control_circuit_id'))
        if not model['hurwitz_strict']:
            raise MapUnavailable('finite-bandwidth local model is unstable')
        if dt*model['current_loop_rate_per_s'] > .1:
            raise MapUnavailable('time step exceeds declared electrical resolution')

        def derivative(values):
            gap, velocity, current = values[:3]
            if abs(current) > current_limit:
                raise MapUnavailable('actual-current-limit-exceeded')
            p = sample(gap, current)
            resistance, inductance = _scalar(p, 'R_ohm', field), _scalar(p, 'L_H', field)
            number(resistance, 'R_ohm', positive=True);number(inductance, 'L_H', positive=True)
            if dt*(resistance+gain)/inductance > .1:
                raise MapUnavailable('time step exceeds local electrical resolution')
            gradient = _scalar(p, 'dflux_dgap_Wb_turn_per_m', field)
            command = current0+kp*(gap-gap0)+kd*velocity
            if abs(command) > current_limit:
                raise MapUnavailable('current-command-clamped')
            voltage = resistance*command+gradient*velocity+gain*(command-current)
            if abs(voltage) > voltage_limit:
                raise MapUnavailable('voltage-command-clamped')
            acceleration = (load+scenario.get('downward_disturbance_N', 0.)-p['F_z_N'])/mass
            return [velocity, acceleration, (voltage-resistance*current-gradient*velocity)/inductance,
                    current, current*current, current*current*resistance, voltage*current]

        derivative(state)
        records.append(dict(time_s=0., gap_m=state[0], velocity_m_s=state[1], current_A=state[2]))
        stride = max(1, count//200)
        for step in range(count):
            next_state = _rk4(state, dt, derivative)
            derivative(next_state)
            state = next_state
            elapsed = (step+1)*dt
            if (step+1) % stride == 0 or step+1 == count:
                records.append(dict(time_s=elapsed, gap_m=state[0], velocity_m_s=state[1], current_A=state[2]))
    except MapUnavailable as exc:
        status, reason = 'held-local-model', str(exc)
    losses = {name: scenario.get(name) for name in ('driver_loss_W', 'sensor_loss_W', 'other_loss_W')}
    for name, value in losses.items():
        if value is not None:number(value, name, nonnegative=True)
    coil_loss = state[5]/elapsed if elapsed else None
    known_loss = None if coil_loss is None else coil_loss+sum(value for value in losses.values() if value is not None)
    return dict(status=status, reason=reason, elapsed_s=elapsed, requested_duration_s=count*dt,
                map_id=(field.data['map_id'] if 'field' in locals() else None), unit_scope=(field.data['unit_scope'] if 'field' in locals() else None),
                map_quantity_sha256=(field.quantity_digest if 'field' in locals() else None),
                local_model=model, records=records, current_mean_A=state[3]/elapsed if elapsed else None,
                current_rms_A=math.sqrt(max(0., state[4]/elapsed)) if elapsed else None,
                winding_copper_loss_W=coil_loss, total_known_loss_W=known_loss,
                total_loss_W=known_loss if all(value is not None for value in losses.values()) else None,
                unknown_loss_terms=[name for name, value in losses.items() if value is None],
                loss_scope='Winding I²R plus explicitly supplied other loss terms; unmodelled core/eddy/switching and installed cooling need independent quantities.',
                supply_energy_J=state[6] if elapsed else None,
                clamp_or_domain_failure=status != 'completed-local-scenario',
                unmodelled=['sensor delay/noise', 'multisupport modes', 'flexible structure', 'core/eddy loss', 'switching/protection', 'thermal feedback'],
                service_context=SERVICE_CONTEXT, **FLAGS)


def current_loss_statistics(currents_A, resistances_ohm, *, weights_s=None):
    """Time-weighted RMS/copper heat; opposite signed currents do not cancel heat."""
    if not currents_A or len(currents_A) > 200000:
        raise ValueError('bounded nonempty current samples required')
    currents = [number(value, 'current sample') for value in currents_A]
    resistance = ([resistances_ohm]*len(currents) if type(resistances_ohm) in (int, float) else resistances_ohm)
    weights = [1.]*len(currents) if weights_s is None else weights_s
    if len(resistance) != len(currents) or len(weights) != len(currents):
        raise ValueError('sample/resistance/time inventory differs')
    resistance = [number(value, 'sample resistance', nonnegative=True) for value in resistance]
    weights = [number(value, 'sample duration', positive=True) for value in weights]
    duration = sum(weights)
    heat = sum(weight*current*current*r for weight, current, r in zip(weights, currents, resistance))
    return dict(current_mean_A=sum(weight*current for weight, current in zip(weights, currents))/duration,
                current_rms_A=math.sqrt(sum(weight*current*current for weight, current in zip(weights, currents))/duration),
                winding_copper_loss_W=heat/duration, winding_copper_energy_J=heat if weights_s is not None else None,
                time_weighted=weights_s is not None, total_installed_loss_W=None, **FLAGS)


def _rank(rows, tolerance=1e-10):
    if not rows:return 0
    values = [list(row) for row in rows]
    scale = max((abs(x) for row in values for x in row), default=0.)
    if scale == 0:return 0
    pivot = 0
    for column in range(len(values[0])):
        choice = max(range(pivot, len(values)), key=lambda i: abs(values[i][column]), default=pivot)
        if pivot == len(values) or abs(values[choice][column]) <= tolerance*scale:continue
        values[pivot], values[choice] = values[choice], values[pivot]
        divisor = values[pivot][column]
        values[pivot] = [x/divisor for x in values[pivot]]
        for i in range(pivot+1, len(values)):
            factor = values[i][column]
            values[i] = [x-factor*y for x, y in zip(values[i], values[pivot])]
        pivot += 1
    return pivot


def shunt_response(circuits, frequencies_Hz, *, velocity_rms_m_s=None):
    """Independent passive RL circuits, signed series gradients and MIMO rank.

    C(omega)=sum G.T*G*R_total/(R_total²+(omega*L)²). Static velocity
    and force are zero; a nonzero DC velocity still experiences induction drag.
    Gradients must belong to the actual installed circuit, not unsigned poles.
    """
    if not 1 <= len(circuits) <= 32 or not 1 <= len(frequencies_Hz) <= 100:
        raise ValueError('bounded shunt circuits/frequencies required')
    prepared = []
    try:
        for circuit in circuits:
            members = circuit.get('series_member_gradients_Wb_turn_per_m')
            gradient = circuit.get('flux_gradient_Wb_turn_per_m')
            if members is not None:
                if not members or not 1 <= len(members[0]) <= 6 or any(len(member) != len(members[0]) for member in members):
                    raise ValueError('consistent series gradient dimension required')
                summed = [sum(number(member[j], 'series gradient') for member in members) for j in range(len(members[0]))]
                if gradient is not None and gradient != summed:raise ValueError('signed series gradient does not match declared total')
                gradient = summed
            if gradient is None or circuit.get('L_H') is None or circuit.get('R_coil_ohm') is None or circuit.get('R_load_ohm') is None:
                raise MapUnavailable('unknown shunt gradient, inductance or resistance; no damping credit')
            gradient = [number(x, 'flux gradient') for x in gradient]
            if not 1 <= len(gradient) <= 6:raise ValueError('one to six displacement coordinates required')
            coil = number(circuit['R_coil_ohm'], 'coil resistance', nonnegative=True)
            resistor = number(circuit['R_load_ohm'], 'load resistance', nonnegative=True)
            total = number(coil+resistor, 'total resistance', positive=True)
            inductance = number(circuit['L_H'], 'inductance', positive=True)
            prepared.append(dict(id=circuit.get('id'), gradient=gradient, coil=coil, resistor=resistor, total=total, L=inductance))
    except MapUnavailable as exc:
        return dict(status='held-shunt-data', reason=str(exc), damping_credit=False, **FLAGS)
    dimension = len(prepared[0]['gradient'])
    if any(len(row['gradient']) != dimension for row in prepared):raise ValueError('consistent shunt coordinate dimension required')
    velocity = [number(x, 'prescribed RMS velocity') for x in (velocity_rms_m_s if velocity_rms_m_s is not None else [0.]*dimension)]
    if len(velocity) != dimension:raise ValueError('RMS velocity coordinate dimension differs')
    rows = []
    for frequency in frequencies_Hz:
        omega = 2*math.pi*number(frequency, 'frequency_Hz', nonnegative=True)
        matrix = [[0.]*dimension for _ in range(dimension)]
        coil_heat, resistor_heat, circuit_rows = 0., 0., []
        for circuit in prepared:
            g, total, inductance = circuit['gradient'], circuit['total'], circuit['L']
            denominator = total*total+(omega*inductance)**2
            factor = total/denominator
            for i, j in product(range(dimension), repeat=2):matrix[i][j] += g[i]*g[j]*factor
            emf = sum(a*b for a, b in zip(g, velocity))
            i2 = emf*emf/denominator
            coil_heat += i2*circuit['coil'];resistor_heat += i2*circuit['resistor']
            circuit_rows.append(dict(id=circuit['id'], current_rms_A=math.sqrt(i2), coil_heat_W=i2*circuit['coil'], resistor_heat_W=i2*circuit['resistor']))
        absorbed = sum(velocity[i]*matrix[i][j]*velocity[j] for i, j in product(range(dimension), repeat=2))
        rows.append(dict(frequency_Hz=frequency, damping_matrix_N_s_per_m=matrix, prescribed_velocity_rms_m_s=velocity,
                         absorbed_mechanical_power_W=absorbed, coil_heat_W=coil_heat, resistor_heat_W=resistor_heat,
                         energy_balance_residual_W=absorbed-coil_heat-resistor_heat, circuits=circuit_rows))
    return dict(status='conditional-RL-shunt-calculation', gradient_rank=_rank([row['gradient'] for row in prepared]),
                displacement_coordinates=dimension, signed_series_cancellation=[row['id'] for row in prepared if all(x == 0 for x in row['gradient'])],
                frequency_rows=rows, static_shunt_force_N=[0.]*dimension, static_stiffness_N_per_m=[[0.]*dimension for _ in range(dimension)],
                static_attractive_instability_removed=False, installed_winding_hardware_and_mass_known=False,
                inductance_model='Independent RL circuits; mutual inductance and active-control interaction remain unestablished.',
                same_winding_active_and_passive_damping_compatibility_established=False,
                translational_drag_and_total_eddy_loss_known=False, extra_winding_preferred_to_existing_control=False, **FLAGS)


def simulate_shunt_decay(*, mass_kg, stiffness_N_per_m, damping_N_s_per_m,
                         flux_gradient_Wb_turn_per_m, L_H, R_coil_ohm, R_load_ohm,
                         displacement_m, duration_s, dt_s):
    """Reciprocal scalar energy benchmark; a supplied stable spring is not maglev."""
    mass = number(mass_kg, 'mass', positive=True)
    stiffness = number(stiffness_N_per_m, 'stiffness', positive=True)
    damping = number(damping_N_s_per_m, 'damping', nonnegative=True)
    gradient = number(flux_gradient_Wb_turn_per_m, 'flux gradient')
    inductance = number(L_H, 'inductance', positive=True)
    coil = number(R_coil_ohm, 'coil resistance', nonnegative=True)
    resistor = number(R_load_ohm, 'load resistance', nonnegative=True)
    total = number(coil+resistor, 'total resistance', positive=True)
    count, dt = _steps(duration_s, dt_s)
    if dt*max(total/inductance, math.sqrt(stiffness/mass), abs(gradient)/math.sqrt(mass*inductance)) > .1:
        raise ValueError('time step exceeds declared benchmark resolution')
    values = [number(displacement_m, 'displacement'), 0., 0., 0., 0., 0.]
    def energy(state):return .5*(stiffness*state[0]**2+mass*state[1]**2+inductance*state[2]**2)
    def derivative(state):
        q, velocity, current = state[:3]
        return [velocity, (-stiffness*q-damping*velocity+gradient*current)/mass,
                (-total*current-gradient*velocity)/inductance,
                coil*current*current, resistor*current*current, damping*velocity*velocity]
    initial = energy(values);maximum_increase = 0.
    for _ in range(count):
        previous = energy(values);values = _rk4(values, dt, derivative)
        maximum_increase = max(maximum_increase, energy(values)-previous)
    final = energy(values);heat = sum(values[3:])
    return dict(initial_energy_J=initial, final_energy_J=final, coil_heat_J=values[3], resistor_heat_J=values[4],
                mechanical_damper_heat_J=values[5], energy_balance_residual_J=initial-final-heat,
                maximum_step_energy_increase_J=maximum_increase,
                benchmark_scope='Supplied positive-stiffness scalar oscillator; no railway passive-support claim.', **FLAGS)


def passive_cooling_scenario(loss_W, *, ambient_C, maximum_coil_C, area_m2,
                             convection_W_m2K, emissivity, coil_to_surface_K_per_W):
    """Necessary stationary heat capacity with declared convection/conduction only."""
    parameters = dict(loss_W=loss_W, ambient_C=ambient_C, maximum_coil_C=maximum_coil_C, area_m2=area_m2,
                      convection_W_m2K=convection_W_m2K, emissivity=emissivity, coil_to_surface_K_per_W=coil_to_surface_K_per_W)
    if any(value is None for value in parameters.values()):
        return dict(status='unknown-cooling-inputs', unknown=[key for key, value in parameters.items() if value is None], **FLAGS)
    loss = number(loss_W, 'loss', nonnegative=True)
    ambient = number(ambient_C, 'ambient');maximum = number(maximum_coil_C, 'maximum coil temperature')
    area = number(area_m2, 'area', positive=True);h = number(convection_W_m2K, 'convection', nonnegative=True)
    e = number(emissivity, 'emissivity', nonnegative=True);r = number(coil_to_surface_K_per_W, 'conduction resistance', nonnegative=True)
    if ambient <= -273.15 or maximum <= ambient or e > 1:raise ValueError('physical temperatures and emissivity required')
    def reject(surface):return h*area*(surface-ambient)+e*5.670374419e-8*area*((surface+273.15)**4-(ambient+273.15)**4)
    if r == 0:
        surface = maximum
    else:
        low, high = ambient, maximum
        for _ in range(80):
            surface = (low+high)/2
            if reject(surface) > (maximum-surface)/r:high = surface
            else:low = surface
        surface = (low+high)/2
    capacity = reject(surface)
    return dict(status='declared-stationary-cooling-scenario', scenario_inputs=parameters,
                maximum_rejection_W=capacity, required_loss_W=loss, necessary_heat_capacity_margin_W=capacity-loss,
                necessary_screen_pass=capacity >= loss, surface_temperature_at_coil_limit_C=surface,
                measured_or_qualified=False, whole_installed_thermal_equilibrium_established=False, **FLAGS)


def gravity_assistance_scenario(mass_kg, *, vertical_drop_m, distance_m, target_speed_m_s,
                                resistance_force_N=None, conversion_efficiency=1.):
    """One-way potential-energy scenario; return climb and stopping remain separate."""
    mass = number(mass_kg, 'mass', positive=True);drop = number(vertical_drop_m, 'drop', nonnegative=True)
    distance = number(distance_m, 'distance', positive=True);speed = number(target_speed_m_s, 'speed', nonnegative=True)
    efficiency = number(conversion_efficiency, 'efficiency', positive=True)
    if efficiency > 1 or drop > distance:raise ValueError('efficiency <=1 and geometric drop <= distance required')
    available = mass*9.80665*drop*efficiency;kinetic = .5*mass*speed*speed
    resistance = None if resistance_force_N is None else number(resistance_force_N, 'resistance', nonnegative=True)*distance
    return dict(status='declared-gravity-assistance-scenario', potential_energy_J=mass*9.80665*drop,
                useful_gravity_energy_J=available, ideal_no_resistance_speed_m_s=math.sqrt(2*9.80665*drop*efficiency),
                average_gravity_force_N=available/distance, target_kinetic_energy_J=kinetic, resistance_energy_J=resistance,
                energy_margin_J=None if resistance is None else available-kinetic-resistance,
                reverse_climb_energy_before_losses_J=mass*9.80665*drop,
                independent_support_energy_credit_J=0., route_adopted=False,
                station_power_plant_saving_established=False, measured_or_qualified=False,
                service_context=SERVICE_CONTEXT, **FLAGS)
