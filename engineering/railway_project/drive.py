"""Continuous-only, conditional drive sizing for a counted compact research body.

The catalogue is not an installed force/duty map.  This adapter retains that
distinction even when explicit sizing hypotheses allow a point-train simulation.
It does not change the physical body, certify adhesion, or qualify current control.
"""
from copy import deepcopy
from math import fsum, isfinite, pi, sqrt
from pathlib import Path

from engineering.station_rail import ROOT
from engineering.station_rail.common import digest, identity
from engineering.compact_drive.common import validate as validate_body

SCHEMA = 'osr-compact-drive-duty-evaluation/1'
CONDITIONAL_DOMAIN = 'continuous-catalogue-sizing-hypotheses-only'
FLAGS = dict(physical_evidence=False, physical_accepted=False,
             engineering_accepted=False, manufacturing_release=False,
             operating_release=False, admitted_operating_map=False,
             selected_reference_changed=False, movement_authority=False)
DATASHEET = dict(
    url='https://emrax.com/wp-content/uploads/2026/08/EMRAX_268_datasheet_v1.7_version-C.pdf',
    sha256='a3c527667ddcaafd3f49be6f06599cf2316fca12d60e8fe5b7f789e9f6f532ab',
    table='page2; standard MV, LC, 1UVW; not CC/HV/2UVW/older1.6',
    motor_continuous_torque_nm=205., motor_continuous_power_w=91000.,
    motor_maximum_rpm=4500., motor_continuous_current_arms=220.,
    peak_torque_nm=500., peak_s2_duration_s=30., peak_not_used=True,
    kt_nm_per_arms=1.20, phase_resistance_25c_ohm=.00967,
    phase_ld_h=.000129, phase_lq_h=.000138, flux_vs=.080,
    pole_pairs=10, nominal_kv_rpm_per_vdc=7.59,
    coolant_max_c=50., coolant_min_l_min_each=6.,
    rotor_airflow_m3_min_per_kw=.4,
    winding_sensor_limit_c=100., rotor_surface_limit_c=80.,
    rotor_inertia_kg_m2=.0949,
    constants_are_catalogue_not_identified_installed_parameters=True)

# Every capacity is either explicitly supplied or stays unknown.  A declaration
# here is an evaluation hypothesis, not proof of the bounded item in the BOM.
INPUT_UNITS = {
    'wheel_radius_m': 'm; declared worn/new case in [0.34,0.38]',
    'motor_torque_limit_nm': 'Nm per motor; continuous <=205',
    'motor_power_limit_w': 'W shaft per motor; continuous <=91000',
    'inverter_current_limit_arms': 'Arms per motor; continuous <=220',
    'inverter_input_power_limit_w_each': 'W DC per inverter',
    'dc_bus_min_v': 'V DC under load; <=830',
    'gear_input_torque_limit_nm': 'Nm per gearbox input',
    'gear_output_torque_limit_nm': 'Nm per gearbox output',
    'gear_output_power_limit_w': 'W per gearbox output',
    'gear_efficiency': 'fraction (0,1]',
    'motor_efficiency_floor': 'declared fraction (0,0.96]; not a proven map',
    'inverter_efficiency_floor': 'declared fraction (0,1]',
    'grid_input_power_limit_w': 'W train total, exclusive of base auxiliaries',
    'contact_force_limit_n': 'N train total, separately assumed adhesion cap',
    'coolant_inlet_c': 'C, must meet <=50 catalogue condition',
    'coolant_flow_l_min_each': 'L/min per motor, >=6',
    'rotor_airflow_m3_min_each': 'm3/min per motor, >=0.4 per declared kW',
    'cooling_parasitic_power_w': 'positive W train total; chiller/pump/fan sizing',
    'copper_resistance_hot_multiplier': 'declared positive multiplier >=1',
    'voltage_model': "must explicitly be 'catalogue-nominal-kv-sizing-hypothesis'",
    'assumption_reference': 'nonempty design/evaluation assumption reference',
}


def _sealed(value):
    value['evaluation_id'] = identity(value)
    return value


def _positive(value, name):
    if type(value) not in (int, float) or not isfinite(value) or value <= 0:
        raise ValueError('Positive finite declared ' + name + ' required')
    return float(value)


def _verify_sources(source, root):
    root=Path(root).resolve()
    if not isinstance(source,dict) or not source:
        raise ValueError('Exact duty/body source epoch required')
    for name,want in source.items():
        path=Path(name)
        if (path.is_absolute() or '..' in path.parts or path.as_posix()!=name
                or not (root/path).resolve().is_relative_to(root)):
            raise ValueError('Ordinary in-root duty source path required')
        if digest(root/path)!=want:
            raise ValueError('Exact duty/body source epoch required')


def _verify(value, root=ROOT):
    if value.get('schema') != SCHEMA or value.get('evaluation_id') != identity(
            {k: v for k, v in value.items() if k != 'evaluation_id'}):
        raise ValueError('Sealed compact-drive duty evaluation required')
    if any(value.get(k) is not False for k in FLAGS):
        raise ValueError('Conditional sizing cannot grant physical admission')
    source=value.get('source_sha256', {})
    _verify_sources(source,root)
    return value


def evaluate(body, requirements, *, root=ROOT):
    """Bind the exact body to declared continuous drive limits and explicit holds.

    Missing sizing capacities produce ``None`` and a held simulation definition;
    they are never interpreted as zero or filled from another railway candidate.
    """
    root = Path(root)
    validate_body(body)
    if body.get('schema') != 'osr-vehicle-installation/1':
        raise ValueError('Counted installed research body required')
    contract = body.get('compact_drive_contract', {})
    if contract.get('candidate_id') != body['candidate_id'] or contract.get('contract_id') != identity(
            {k: v for k, v in contract.items() if k != 'contract_id'}):
        raise ValueError('Body and compact-drive contract identity differ')
    source = deepcopy(body.get('source_sha256', {}))
    _verify_sources(source,root)
    before = {**source, 'engineering/railway_project/drive.py': digest(root / 'engineering/railway_project/drive.py')}
    parts = {r['id']: r for r in body['parts']}
    if len(parts) != len(body['parts']):
        raise ValueError('Duplicate counted component definition')
    ownership = contract.get('mass_ownership', {})
    if (ownership.get('all_new_drive_components_in_body_BOM') is not True
            or ownership.get('additional_external_drive_mass_kg') != 0.
            or ownership.get('zero_is_exact_no_external_addition_not_unknown_equipment') is not True
            or ownership.get('remaining_unknown_mass_positive') is not True):
        raise ValueError('Counted compact drive mass ownership required; no legacy append')
    motor = parts.get('compact-drive/vendor-motor')
    inverter = parts.get('compact-drive/inverter')
    reserve = parts.get('compact-drive/integration-reserve')
    for row, count in ((motor, 24), (inverter, 24), (reserve, 6)):
        if row is None or row['quantity_per_train'] != count:
            raise ValueError('Exact 24 motor/inverter and six positive reserve ownership required')
        if sum(q['count'] for q in body['patterns'] if q['part_id'] == row['id']) != count:
            raise ValueError('Drive component occurrence count differs')
        if any(_positive(row['mass_each_kg'][c], 'installed component mass') <= 0 for c in ('low', 'base', 'high')):
            raise ValueError('Unknown installed drive mass cannot be zero')
    gear = contract['geartrain']
    ratio = _positive(gear['ratio'], 'gear ratio')
    gears = gear.get('gears', [])
    if (len(gears) != 4 or any(type(g.get('teeth')) is not int or g['teeth'] <= 0 for g in gears)
            or abs(ratio - gears[1]['teeth'] / gears[0]['teeth'] * gears[3]['teeth'] / gears[2]['teeth']) > 1e-12):
        raise ValueError('Declared two-stage ratio differs from counted gear definition')
    for g in gears:
        row = parts.get('compact-drive/' + g['id'])
        if (row is None or row['quantity_per_train'] != 24
                or sum(q['count'] for q in body['patterns'] if q['part_id'] == row['id']) != 24):
            raise ValueError('24 complete counted gear trains required')
    hardware = body['physical_definition'].get('hardware', {}).get('motor')
    if hardware is not None and any(hardware.get(k) != v for k, v in {
            'manufacturer': 'EMRAX', 'model': '268', 'winding': 'MV',
            'phase_system': '1UVW', 'cooling': 'LC'}.items()):
        raise ValueError('This source/evaluator covers only EMRAX268 MV1UVW LC')
    if not isinstance(requirements, dict) or set(requirements) - set(INPUT_UNITS):
        raise ValueError('Known explicit compact drive sizing input fields required')
    declared = {k: deepcopy(requirements.get(k)) for k in INPUT_UNITS}
    holds = [dict(kind='unknown-sizing-input', field=k) for k, v in declared.items() if v is None]
    if hardware is None:
        holds.append(dict(kind='missing-physical-hardware-projection', field='physical_definition.hardware.motor'))
    for k, v in declared.items():
        if v is None or k in ('voltage_model', 'assumption_reference'):
            continue
        if k == 'coolant_inlet_c':
            if type(v) not in (int, float) or not isfinite(v):
                raise ValueError('Finite coolant inlet temperature required')
        else:
            _positive(v, k)
    for name in ('gear_efficiency', 'motor_efficiency_floor', 'inverter_efficiency_floor'):
        if declared[name] is not None and declared[name] > (0.96 if name == 'motor_efficiency_floor' else 1.):
            raise ValueError('Declared efficiency exceeds permitted source/model range')
    for name, lo, hi in (
            ('wheel_radius_m', .34, .38), ('motor_torque_limit_nm', 0., 205.),
            ('motor_power_limit_w', 0., 91000.), ('inverter_current_limit_arms', 0., 220.),
            ('dc_bus_min_v', 0., 830.)):
        if declared[name] is not None and not lo <= declared[name] <= hi:
            raise ValueError('Outside continuous catalogue/model domain: ' + name)
    if declared['copper_resistance_hot_multiplier'] is not None and declared['copper_resistance_hot_multiplier'] < 1.:
        raise ValueError('Copper loss cannot use resistance below the pinned25C value')
    if declared['voltage_model'] is not None and declared['voltage_model'] != 'catalogue-nominal-kv-sizing-hypothesis':
        raise ValueError('Explicit nominal KV hypothesis required; no invented voltage map')
    if declared['assumption_reference'] is not None and (not isinstance(declared['assumption_reference'], str) or not declared['assumption_reference'].strip()):
        raise ValueError('Explicit assumption reference required')
    condition_failures = []
    if declared['coolant_inlet_c'] is not None and declared['coolant_inlet_c'] > 50.:
        condition_failures.append('coolant inlet exceeds source50C')
    if declared['coolant_flow_l_min_each'] is not None and declared['coolant_flow_l_min_each'] < 6.:
        condition_failures.append('coolant flow below source6L/min per motor')
    if declared['rotor_airflow_m3_min_each'] is not None and declared['motor_power_limit_w'] is not None and declared['rotor_airflow_m3_min_each'] < .4 * declared['motor_power_limit_w'] / 1000.:
        condition_failures.append('rotor airflow below catalogue guidance for declared output')
    holds += [dict(kind='source-condition-not-met', reason=reason) for reason in condition_failures]
    model = None
    if not holds:
        r = declared['wheel_radius_m']; eg = declared['gear_efficiency']
        em = declared['motor_efficiency_floor']; ei = declared['inverter_efficiency_floor']
        current_limit = min(220., declared['inverter_current_limit_arms'])
        torque = min(205., declared['motor_torque_limit_nm'], current_limit * 1.2,
                     declared['gear_input_torque_limit_nm'],
                     declared['gear_output_torque_limit_nm'] / (ratio * eg))
        amps = torque / 1.2
        # Fixed loss reservation is an explicitly conservative budgeting device
        # for the point-train kernel. It must be added to Case auxiliaries, not
        # silently removed from system electricity/heat. It is not a dq solve.
        copper_each = 3. * amps ** 2 * .00967 * declared['copper_resistance_hot_multiplier']
        reserved = 24. * copper_each / ei + declared['cooling_parasitic_power_w']
        available_grid = declared['grid_input_power_limit_w'] - reserved
        inverter_available = declared['inverter_input_power_limit_w_each'] - copper_each / ei
        if available_grid <= 0 or inverter_available <= 0:
            holds.append(dict(kind='power-reservation-exceeds-supply', required_fixed_power_w=reserved))
        else:
            efficiency = eg * em * ei
            output_each = min(declared['motor_power_limit_w'] * eg,
                              declared['gear_output_power_limit_w'],
                              inverter_available * efficiency,
                              available_grid * efficiency / 24.)
            rpm = min(4500., declared['dc_bus_min_v'] * 7.59)
            vmax = rpm * 2. * pi / 60. / ratio * r
            force = min(24. * torque * ratio * eg / r, declared['contact_force_limit_n'])
            power = 24. * output_each
            # Native kernel independently caps F*v by mechanical_power_w.
            # The samples themselves are NOT advertised as a free interpolation
            # of a validated nonlinear motor map.
            points = [dict(speed_m_s=vmax*i/32., force_n=min(force, power/(vmax*i/32.)) if i else force) for i in range(33)]
            model = dict(points=points, maximum_speed_m_s=vmax,
                         mechanical_power_w=power, electrical_efficiency=efficiency,
                         grid_power_w=available_grid, contact_force_cap_n=declared['contact_force_limit_n'],
                         external_mass_kg=0., external_resistance_n=0.,
                         motor_count=24, driven_axle_count=24, gear_ratio=ratio,
                         motor_torque_cap_nm=torque, motor_rms_current_cap_a=amps,
                         motor_rpm_cap=rpm, copper_loss_reservation_w_each=copper_each,
                         mandatory_auxiliary_addition_w=reserved,
                         fixed_loss_reservation_is_not_measured_loss=True,
                         copper_reservation_adds_to_efficiency_loss_allowance=True,
                         base_speed_m_s=min(vmax, power/force),
                         rotor_reflected_equivalent_mass_kg=24.*DATASHEET['rotor_inertia_kg_m2']*ratio**2/r**2,
                         other_rotating_inertia_unknown=True,
                         torque_output_cap_nm_each=torque*ratio*eg,
                         shaft_output_power_cap_w_each=output_each)
    findings = [
        'Catalogue continuous ratings are conditional on actual coolant, airflow, controller and installation.',
        'No selected inverter, collector/contact system, protection, DC supply sag or installation-tested current regulator.',
        'Nominal KV is a sizing hypothesis; phase/line RMS and dq flux/current conventions are not independently identified.',
        'No installed winding/rotor thermal network, coolant heat rejection or hot50C repeated-duty validation.',
        'Point-train constant-efficiency kernel omits stall copper loss; mandatory explicit auxiliary reservation budgets it conservatively.',
        'Gear/shaft/bearing/contact fatigue and torque capacity are declared sizing limits, not demonstrated hardware performance.',
        'Motor/shaft/cooling source revision compatibility and mechanical mount/rotating interface remain independently held.',
        'Friction/WSP braking, emergency independence, degraded adhesion, rescue and route acceptance remain separate.',
        '24 motor/inverter masses and positive integration reserves are in this bodyBOM; no9552kg legacy external append.',
        'No regeneration or storage energy credit is applied by this continuous traction adapter.',
    ]
    counts = dict(motors=24, inverters=24, driven_axles=24,
                  motor_mass_kg={c:24.*motor['mass_each_kg'][c] for c in ('low','base','high')},
                  integration_reserve_mass_kg={c:6.*reserve['mass_each_kg'][c] for c in ('low','base','high')},
                  external_drive_mass_kg=0., exact_no_external_addition=True)
    value = dict(schema=SCHEMA, candidate_id=body['candidate_id'], body_evaluation_id=body['evaluation_id'],
                 body_contract_id=contract['contract_id'], physical_definition_unchanged=True,
                 purpose='unselected continuous-only research simulation sizing', domain=CONDITIONAL_DOMAIN,
                 hardware=deepcopy(hardware), source_catalogue=deepcopy(DATASHEET),
                 declared=declared, required_inputs=deepcopy(INPUT_UNITS), mass_ownership=counts,
                 simulation_definition='ready-under-explicit-hypotheses' if model is not None else 'held',
                 definition_holds=holds, installed_operating_map_admission='held',
                 installed_evidence_holds=findings, model=model,
                 current_dynamics=dict(status='unsupported; no closed-loop dq simulation',
                    phase_ld_h=.000129, phase_lq_h=.000138, phase_r25_ohm=.00967,
                    l_over_r25_s=[.000129/.00967, .000138/.00967],
                    kt_torque_current_relation_is_catalogue_sizing_hypothesis=True,
                    thermal_rc=None, thermal_rc_unknown_not_zero=True),
                 source_sha256=before, **FLAGS)
    if any(digest(root/n) != h for n,h in before.items()):
        raise ValueError('Drive or body sources changed during evaluation')
    return _sealed(value)


def native_drive(evaluation, distance_m, *, acknowledge_domain=None, root=ROOT):
    """Return only the exact Rust ``Drive`` fields; physical admission stays held.

    Caller MUST add ``mandatory_auxiliary_power_w(evaluation)`` to its Case's
    explicitly priced/supplied auxiliary demand and retain this evaluation in the
    case manifest. This function never inserts undocumented native JSON fields.
    """
    _verify(evaluation, root)
    if acknowledge_domain != CONDITIONAL_DOMAIN:
        raise ValueError('Explicit continuous-only conditional research domain acknowledgement required')
    m = evaluation.get('model')
    if m is None or evaluation['definition_holds']:
        raise ValueError('Unknown/unmet source, current, power, cooling or gear requirements; drive held')
    distance = _positive(distance_m, 'route distance')
    names = ('points','maximum_speed_m_s','mechanical_power_w','electrical_efficiency',
             'grid_power_w','contact_force_cap_n','external_mass_kg','external_resistance_n')
    return {**{k:deepcopy(m[k]) for k in names}, 'windows_m':[[0., distance]]}


def mandatory_auxiliary_power_w(evaluation, *, root=ROOT):
    _verify(evaluation, root)
    if evaluation.get('model') is None:
        raise ValueError('No sized copper/cooling reservation for held drive')
    return evaluation['model']['mandatory_auxiliary_addition_w']


def audit_trace(evaluation, trace, *, candidate_id, root=ROOT):
    """Diagnostic RMS/copper/work audit of one explicit trace, without admission.

    Current is inferred from force and catalogue KT, not solved by a current
    regulator. Sparse trace quadrature is labelled approximate. No trace can
    establish closed-loop voltage response, rotor temperature or brake capacity.
    """
    _verify(evaluation, root)
    if candidate_id != evaluation['candidate_id']:
        raise ValueError('Trace belongs to a different physical vehicle')
    m=evaluation.get('model')
    if m is None or not isinstance(trace,list) or len(trace)<2:
        raise ValueError('Sized drive and at least two time-ordered trace samples required')
    ratio=m['gear_ratio']; d=evaluation['declared']; rows=[]
    for row in trace:
        for name in ('time_s','speed_m_s','traction_n'):
            v=row.get(name)
            if type(v) not in (int,float) or not isfinite(v) or v<0:
                raise ValueError('Finite nonnegative drive trace fields required')
        if rows and row['time_s']<=rows[-1]['time_s']:
            raise ValueError('Strict trace time ordering required')
        torque=row['traction_n']*d['wheel_radius_m']/(24.*ratio*d['gear_efficiency'])
        amps=torque/1.2
        copper=24.*3.*amps**2*.00967*d['copper_resistance_hot_multiplier']
        rows.append(dict(time_s=row['time_s'],arms=amps,copper_w=copper,
                         wheel_power_w=row['traction_n']*row['speed_m_s'],
                         rpm=row['speed_m_s']/d['wheel_radius_m']*ratio*60./(2.*pi)))
    duration=rows[-1]['time_s']-rows[0]['time_s']
    if duration<=0:raise ValueError('Positive trace duration required')
    def integ(field):return fsum((b['time_s']-a['time_s'])*(a[field]+b[field])/2. for a,b in zip(rows,rows[1:]))
    rms=sqrt(fsum((b['time_s']-a['time_s'])*(a['arms']**2+b['arms']**2)/2. for a,b in zip(rows,rows[1:]))/duration)
    max_i=max(r['arms'] for r in rows);max_rpm=max(r['rpm'] for r in rows)
    result=dict(schema='osr-compact-drive-trace-diagnostic/1', candidate_id=candidate_id,
                duty_evaluation_id=evaluation['evaluation_id'],trace_id=identity(trace),
                quadrature='trapezoidal over provided output samples; no exact native energy replacement',
                duration_s=duration, motor_current_rms_a=rms, maximum_inferred_motor_arms=max_i,
                current_margin_a=m['motor_rms_current_cap_a']-max_i,
                maximum_motor_rpm=max_rpm, rpm_margin=m['motor_rpm_cap']-max_rpm,
                copper_loss_estimate_j=integ('copper_w'), wheel_work_estimate_j=integ('wheel_power_w'),
                fixed_reservation_grid_energy_j=m['mandatory_auxiliary_addition_w']*duration,
                torque_current_hypothesis_only=True,current_dynamics_resolved=False,
                repeated_duty_thermal_admission=False, **FLAGS)
    return _sealed(result)
