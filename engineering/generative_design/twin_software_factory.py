"""Executable offline software/factory twin lane; no installed twin is asserted.

Public catalogue fields remain separate from study assumptions and offered-unit
acceptance. Candidate safety policies are exercised against the same immutable
fault suite; a proposal cannot suppress its adverse results.
"""
from __future__ import annotations

from copy import deepcopy
import hashlib
import json
import math
from pathlib import Path

from engineering.twin_design.physics import closure_decision, precharge, thermal_study

ROOT = Path(__file__).resolve().parents[2]
INPUTS = 'engineering/twin_design/data/design-inputs.json'
EQUIPMENT = 'engineering/factory_examples/data/equipment.json'
FACTORY = 'engineering/generative_design/data/factory-systems.json'
PRODUCTION = 'engineering/factory_examples/data/production.json'
GUARDS = ('train_stopped', 'hvil_closed', 'insulation_ok', 'main_feedback_open',
          'return_feedback_closed', 'precharge_feedback_closed')


def _read(name):
    return json.loads((ROOT / name).read_text())


def _hash(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, allow_nan=False).encode()).hexdigest()


def _number(value, name, minimum=0):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value < minimum:
        raise ValueError(f'{name} must be a finite number >= {minimum}')
    return float(value)


def check(identifier, passed, value, limit, unit, basis):
    return dict(id=identifier, state='unknown' if passed is None else ('pass' if passed else 'fail'),
                value=value, limit=limit, unit=unit, basis=basis)


def _part(identifier, parent, title, specifications, *, material=None, manufacturing=None, inspection=None):
    return dict(id=identifier, parent_id=parent, title=title, specifications=specifications,
                material=material, manufacturing=manufacturing or {'release_state': 'not-released'},
                inspection=inspection or {'state': 'procedure-and-acceptance-evidence-required'})


def _variant(identifier, concept, parameters, parts, checks, objectives):
    states = {c['state'] for c in checks}
    selection = 'rejected' if 'fail' in states else ('conditional' if 'unknown' in states else 'study-admissible')
    return dict(id=identifier, concept=concept, parameters=parameters, parts=parts,
                checks=checks, objectives=objectives, selection_state=selection,
                configuration_id=_hash({'parameters': parameters, 'parts': parts}),
                production_released=False)


def replay_precharge(frames, policy='guarded', *, timeout_s=5., close_ratio=.95, maximum_age_s=.1,
                     cycle_start_s=0., elapsed_consistency_tolerance_s=1e-6):
    """Replay requests only. Positive and deliberately adverse policies share input.

    One invocation is one precharge cycle. The controller supplies a frozen
    cycle_start_s on the same monotonic clock as observed_s and received_s; a
    message cannot redefine that epoch. Its elapsed_s must equal observed_s
    minus this epoch within declared numerical tolerance. Faults latch; reset
    and physical switching are outside this simulator. Missing data fails closed.
    """
    if policy not in ('ratio-only', 'interlocks-only', 'guarded'):
        raise ValueError('unknown policy')
    _number(timeout_s, 'timeout', 1e-12)
    _number(maximum_age_s, 'maximum age', 1e-12)
    _number(close_ratio, 'closure ratio', 1e-12)
    _number(cycle_start_s, 'cycle start')
    _number(elapsed_consistency_tolerance_s, 'elapsed clock tolerance')
    if close_ratio >= 1:
        raise ValueError('closure ratio must be below one')
    state, previous_sequence, previous_time, previous_received = 'ISOLATED', -1, -1., -1.
    rows = []
    for frame in frames:
        faults = []
        try:
            seq = frame['sequence']
            if type(seq) is not int or seq < 0:
                raise ValueError('sequence must be a nonnegative integer')
            observed = _number(frame['observed_s'], 'observation time')
            received = _number(frame['received_s'], 'receipt time')
            signals = deepcopy(frame['signals'])
            # The analytical policy validates complete, strictly typed signals.
            decision = closure_decision({'timeout_s': timeout_s, 'close_ratio': close_ratio}, signals)
            stale = received - observed > maximum_age_s or received < observed
            reordered = seq <= previous_sequence or observed < previous_time
            received_backwards = received < previous_received
            elapsed_inconsistent = (observed < cycle_start_s or
                abs(signals['elapsed_s'] - (observed - cycle_start_s)) > elapsed_consistency_tolerance_s)
            faults = list(decision['faults'])
            if stale:
                faults.append('stale-or-future-observation')
            if reordered:
                faults.append('reordered-or-duplicate')
            if received_backwards:
                faults.append('receipt-clock-backwards')
            if elapsed_inconsistent:
                faults.append('elapsed-clock-inconsistency')
            if policy == 'ratio-only':
                request = signals['link_voltage_ratio'] >= close_ratio
            elif policy == 'interlocks-only':
                request = decision['can_request_main_close']
            else:
                request = decision['can_request_main_close'] and not faults
            previous_sequence, previous_time, previous_received = seq, observed, received
        except (ValueError, KeyError, TypeError):
            faults, request = ['invalid-observation'], False
        if state == 'LOCKOUT':
            request = False
        elif policy == 'guarded' and faults:
            state, request = 'LOCKOUT', False
        else:
            state = 'READY_REQUEST' if request else 'PRECHARGING'
        rows.append(dict(state=state, request_main_close=bool(request), faults=faults))
    return dict(policy=policy, rows=rows, final_state=state, physical_control_implemented=False)


def fault_suite():
    signals = {k: True for k in GUARDS}
    signals.update(elapsed_s=3.5, link_voltage_ratio=.96)
    base = dict(sequence=1, observed_s=3.5, received_s=3.52, signals=signals)
    cases = [dict(id='healthy', frames=[deepcopy(base)], expected_request=True)]
    for guard in GUARDS:
        frame = deepcopy(base); frame['signals'][guard] = False
        cases.append(dict(id=guard, frames=[frame], expected_request=False))
    for identifier, key, value in [('timeout', 'elapsed_s', 6.), ('undervoltage', 'link_voltage_ratio', .5),
                                   ('untyped-guard', 'hvil_closed', 1), ('nonfinite-voltage', 'link_voltage_ratio', float('nan'))]:
        frame = deepcopy(base); frame['signals'][key] = value
        cases.append(dict(id=identifier, frames=[frame], expected_request=False))
    for identifier, key, value in [('stale', 'received_s', 4.), ('future', 'received_s', 3.),
                                   ('invalid-sequence', 'sequence', True)]:
        frame = deepcopy(base); frame[key] = value
        cases.append(dict(id=identifier, frames=[frame], expected_request=False))
    frame = deepcopy(base); del frame['signals']['insulation_ok']
    cases.append(dict(id='missing-observation', frames=[frame], expected_request=False))
    frame = deepcopy(base); frame['signals']['hvil_closed'] = False
    healthy = deepcopy(base); healthy.update(sequence=2, observed_s=3.6, received_s=3.62)
    cases.append(dict(id='latched-fault', frames=[frame, healthy], expected_request=False))
    cases.append(dict(id='duplicate', frames=[deepcopy(base), deepcopy(base)], expected_request=False))
    frozen = deepcopy(base); frozen.update(sequence=2, observed_s=10000., received_s=10000.02)
    cases.append(dict(id='fresh-envelope-frozen-elapsed', frames=[deepcopy(base), frozen], expected_request=False))
    first = deepcopy(base); first['received_s'] = 3.58
    backwards = deepcopy(base); backwards.update(sequence=2, observed_s=3.52, received_s=3.55)
    backwards['signals']['elapsed_s'] = 3.52
    cases.append(dict(id='receipt-clock-backwards', frames=[first, backwards], expected_request=False))
    return cases


def _software(inputs):
    interfaces = [dict(id='precharge-observation-v1', direction='input',
        fields={'signals': {**{k: 'strict boolean' for k in GUARDS}, 'elapsed_s': 'finite float seconds >=0',
                'link_voltage_ratio': 'finite float [0,1.05]'}, 'sequence': 'uint monotonic',
                'observed_s': 'monotonic timestamp seconds', 'received_s': 'same-clock receipt seconds'},
        transport='not-selected',
        clock={'basis': 'common monotonic study clock; installed synchronization unqualified',
               'cycle_start_s': 'frozen controller-owned epoch for this replay invocation; messages cannot reset it',
               'elapsed_s_rule': 'observed_s minus cycle_start_s',
               'elapsed_consistency_tolerance_s': 1e-6, 'maximum_age_s': .1,
               'observed_and_received_monotonic': True}),
        dict(id='precharge-request-v1', direction='output', fields={'request_main_close': 'boolean request only',
             'state': ['ISOLATED', 'PRECHARGING', 'READY_REQUEST', 'LOCKOUT'], 'faults': 'list of identifiers'},
             physical_actuation=False)]
    variants, experiments = [], []
    for policy in ('ratio-only', 'interlocks-only', 'guarded'):
        results = []
        for case in fault_suite():
            result = replay_precharge(case['frames'], policy)
            actual = result['rows'][-1]['request_main_close']
            results.append(dict(id=case['id'], expected_request=case['expected_request'],
                                actual_request=actual, passed=actual == case['expected_request'], replay=result))
        failed = sum(not row['passed'] for row in results)
        checks = [check('independent-adverse-suite', failed == 0, failed, 0, 'failed cases',
                        'Same fault suite for each policy, including latch, timing and malformed input'),
                  check('installed-safety-validation', None, None, 'accepted hazard and assurance case', None,
                        'Offline requests; no target hardware, qualified transport or safety integrity allocation')]
        variants.append(_variant('control-' + policy, policy, {'policy': policy, 'maximum_age_s': .1, 'cycle_start_s': 0., 'elapsed_consistency_tolerance_s': 1e-6},
            [_part('controller', None, 'Offline precharge controller', {'language': 'Python', 'physical_output': False},
                   manufacturing={'process': 'versioned source and deterministic replay', 'firmware_target': None},
                   inspection={'procedure': 'independent fault suite', 'case_count': len(results)})], checks,
            {'failed_fault_cases': failed, 'verified_fault_case_count': len(results)}))
        experiments.append(dict(id='fault-replay-' + policy, domain='software', results=results,
                                execution='actual offline deterministic replay'))
    system = dict(id='software-precharge-control', title='Precharge state, transport freshness and fault latch',
        configuration_id=_hash(interfaces), requirements=['Every critical fault inhibits closure request',
            'Malformed, stale or reordered observations fail closed', 'A latched fault requires separately specified reset procedure'],
        interfaces=interfaces, variants=variants)
    return system, experiments


def _electrothermal(inputs):
    electrical, thermal, experiments = [], [], []
    for resistance in (75., 150., 600.):
        p = deepcopy(inputs['electrical']['precharge']); p['resistance_ohm'] = resistance
        result = precharge(p, 800.)
        residual = max(abs(s['energy_residual_j']) for s in result['samples'])
        electrical.append(_variant(f'precharge-{resistance:g}-ohm', 'Passive resistor precharge', p,
            [_part('precharge-network', None, 'Precharge electrical study circuit', {'topology': 'source/return-contactor/resistor/precharge-contactor/capacitor'}),
             _part('resistor', 'precharge-network', 'Pulse resistor', {'resistance_ohm': resistance,
                 'required_pulse_j': result['required_resistor_pulse_energy_j'], 'worst_initial_power_w': result['worst_initial_resistor_power_w'],
                 'qualified_model': None}, material={'resistor_element': None, 'certificate': None}),
             _part('dc-link', 'precharge-network', 'DC-link capacitance', {'capacitance_f': p['capacitance_f'],
                    'voltage_limit_v': p['maximum_voltage_v'], 'esr_ohm': None}),
             _part('contactors', 'precharge-network', 'Return, precharge and main contactors',
                   {'quantity': 3, 'rated_breaking_capacity': None, 'auxiliary_contact_timing_s': None})],
            [check('worst-tolerance-timeout', result['within_declared_timeout'], result['worst_tolerance_ready_time_s'], p['timeout_s'], 's', 'Closed-form RC tolerance corner'),
             check('energy-balance', residual < 1e-7, residual, 1e-7, 'J', 'Source work minus resistor dissipation and stored capacitor energy'),
             check('qualified-pulse-and-switching', None, None, 'supplier pulse, contactor and transient evidence', None, 'No installed rating inferred')],
            {'worst_ready_time_s': result['worst_tolerance_ready_time_s'], 'worst_initial_current_a': result['worst_initial_current_a']}))
        experiments.append(dict(id=f'rc-{resistance:g}', domain='electrical', result=result))
    hvac = inputs['hvac']
    for modules in (3, 4, 5):
        result = thermal_study(hvac['thermal_assumptions'], modules - 1, hvac['module_cooling_w'])
        mass = modules * hvac['module_mass_kg']
        thermal.append(_variant(f'hvac-{modules}-modules', 'Replaceable modular HVAC with one unit unavailable',
            {'installed_modules': modules, 'failed_modules': 1, 'thermal_assumptions': hvac['thermal_assumptions'], 'module_cooling_w': hvac['module_cooling_w']},
            [_part('hvac-array', None, 'Per-car HVAC array', {'installed_modules': modules, 'nominal_total_mass_kg': mass}),
             _part('replaceable-module', 'hvac-array', 'Repeated cooling module candidate',
                   {'quantity': modules, 'envelope_m': hvac['module_dimensions_m'], 'nominal_cooling_w': hvac['module_cooling_w'],
                    'nominal_mass_kg': hvac['module_mass_kg'], 'ambient_derated_capacity_w': None},
                   inspection={'procedure': 'ambient chamber and installed airflow test', 'measured': None})],
            [check('one-unit-out-temperature', result['within_declared_study_limit'], result['maximum_temperature_c'], hvac['thermal_assumptions']['study_limit_c'], 'degC', 'One-node exact integration; excludes humidity/fresh air and ambient capacity derating'),
             check('thermal-energy-balance', result['maximum_energy_residual_j'] < 1e-6, result['maximum_energy_residual_j'], 1e-6, 'J', 'Independent first-law residual'),
             check('installed-ambient-performance', None, None, 'accepted vehicle thermal and airflow measurements', None, 'Nominal public capacity is not measured Baghdad performance')],
            {'nominal_module_mass_kg': mass, 'electrical_energy_kwh': result['electrical_energy_kwh'], 'maximum_temperature_c': result['maximum_temperature_c']}))
        experiments.append(dict(id=f'one-unit-out-{modules}', domain='thermal', result=result))
    systems = [dict(id='electrical-precharge', title='DC precharge component specification and energy study',
        configuration_id=_hash(inputs['electrical']['precharge']), requirements=['Reach 95% within provisional 5 s timeout at tolerance corners', 'Conserve electrical energy'],
        interfaces=[{'id': 'hv-bus', 'voltage_v': [0, 900], 'rated_fault_current_a': None}], variants=electrical),
        dict(id='thermal-control', title='Per-car HVAC availability and thermal balance', configuration_id=_hash(hvac),
             requirements=['One module unavailable: remain <=27 degC for declared 1800 s case'],
             interfaces=[{'id': 'saloon-thermal', 'unit': 'W', 'source': 'declared internal, solar and conductive gains'},
                         {'id': 'hvac-electrical', 'unit': 'kWh', 'basis': 'assumed COP 2.5; supply voltage and transients open'}], variants=thermal)]
    return systems, experiments


def origin_screen(equipment):
    """Preference evidence is not an offered-unit origin certificate."""
    origin = equipment.get('origin', equipment.get('origin_detail', ''))
    text = origin.lower()
    if 'imported alternative' in text or 'czech' in text:
        preference = 'imported-uk-supply-only'
    elif 'integration' in text or 'assembly' in text or 'assembled' in text:
        preference = 'uk-integration-or-assembly-origin-open'
    elif equipment.get('origin_state') == 'manufacturer-stated-UK-manufacture' or any(word in text for word in ('british', 'britain', 'uk manufacture', 'uk hoist', 'united kingdom', 'england', 'manufactured in york')):
        preference = 'published-uk-manufacture-priority-offer-unconfirmed'
    else:
        preference = 'origin-unresolved'
    return dict(preference=preference, published_statement=origin, exact_offered_origin=None,
                origin_acceptance='unknown', supplier_contacted=False)


def _equipment_systems(register, cfg):
    systems = []
    cases = register['equipment'] + [dict(row, origin=row['origin_detail'], unknown=row['unresolved']) for row in cfg['supplier_cases']]
    for item in cases:
        origin = origin_screen(item)
        root_id = item['id']
        specs = {'supplier': item['supplier'], 'model': item['model'], 'published': item['published'],
                 'planning': item.get('planning', {}), 'source_urls': item['sources'],
                 'source_locator': item.get('source_locator', item.get('locator')), 'origin': origin,
                 'specification_status': 'catalogue-candidate-and-declared-study-allowances', 'installed_price': None}
        parts = [_part(root_id, None, item['model'], specs, material={'certificate': None},
            manufacturing={'route': item.get('process', 'supplier-configured installation'), 'offered_factory': None, 'release_state': 'not-released'},
            inspection={'factory_acceptance': 'supplier-approved configuration, functional and dimensional tests pending',
                        'site_acceptance': 'Baghdad utilities, ambient, duty, safeguarding and maintainability tests pending'})]
        for suffix, title in [('utility-interface', 'Power, air, coolant and extraction connections'),
                              ('tooling', 'Process workholding, tools and consumables'),
                              ('foundation-interface', 'Foundation, mounting and service-clearance interfaces'),
                              ('inspection-package', 'Calibration, commissioning and process qualification')]:
            parts.append(_part(root_id + '/' + suffix, root_id, title,
                {'state': 'exact-configuration-required', 'supplier_drawing': None, 'quantity': None,
                 'open_fields': item.get('unknown', [])}))
        checks = [check('offered-unit-origin', None, None, 'offered-unit factory and origin certificate', None,
                    'Published manufacture or UK supply does not establish exact offered unit origin'),
                  check('process-qualification', None, None, 'accepted installation and part process trial', None,
                    'Catalogue capacity is not manufacturing acceptance')]
        variant = _variant(root_id + '-catalogue', 'Source-qualified procurement candidate', specs, parts, checks,
            {'uk_manufacture_priority': origin['preference'], 'installed_cost': None, 'validated_throughput': None})
        systems.append(dict(id='factory/' + root_id, title=item['model'], configuration_id=_hash(specs),
            requirements=item.get('unknown', []), interfaces=[{'id': suffix, 'owner': root_id, 'accepted': False}
                for suffix in ('utility-interface', 'foundation-interface', 'inspection-package')], variants=[variant]))
    return systems


def _cmm_air(cfg, equipment):
    cmm = next(row for row in equipment['equipment'] if row['id'] == 'aberlink-axiom-900')
    bambi = next(row for row in cfg['supplier_cases'] if row['id'] == 'bambi-vts200d')
    published = bambi['published']; variants, experiments = [], []
    required = cmm['published']['air_l_min'] * (1 + cfg['air']['capacity_reserve_fraction']) / (1 - max(cfg['air']['leak_fraction']))
    for units in (1, 2, 3):
        capacity = units * published['fad_8bar_l_min'] * published['maximum_duty_fraction']
        parameters = {'duty_units': units, 'standby_units': 1, 'required_l_min': required,
            'published_fad_l_min_per_unit_at_8bar': published['fad_8bar_l_min'],
            'maximum_duty_fraction': published['maximum_duty_fraction'],
            'leak_fraction': max(cfg['air']['leak_fraction']), 'reserve_fraction': cfg['air']['capacity_reserve_fraction']}
        checks = [check('sustained-flow', capacity >= required, capacity, required, 'free-air L/min',
            'Published FAD times maximum duty fraction, worst configured leakage and planning reserve'),
            check('baghdad-air-quality-and-derating', None, None, 'pressure/dewpoint/oil/particle and hot-ambient trial', None,
                'Receiver cannot create sustained flow; this is time-average screening, not duty-cycle validation'),
            check('exact-offered-origin', None, None, 'exact-unit origin', None, bambi['origin_detail'])]
        variants.append(_variant(f'cmm-air-{units}-duty', 'Segregated CMM air supply', parameters,
            [_part('air-train', None, 'Duty/standby segregated metrology air train', parameters),
             _part('compressors', 'air-train', 'Bambi VTS200D candidates', {'quantity': units + 1, 'operational_roles': {'duty': units, 'standby': 1}, 'published': published}),
             _part('treatment', 'air-train', 'Dryer, filters, receiver and sequencer',
                   {'receiver_l': None, 'air_quality_class': None, 'continuous_pressure_bar': None, 'hot_ambient_rating': None})],
             checks, {'duty_unit_count': units, 'continuous_average_capacity_l_min': capacity}))
        experiments.append(dict(id=f'cmm-air-flow-{units}', domain='factory', parameters=parameters,
                                actual_capacity_l_min=capacity, passed_flow_screen=capacity >= required))
    return dict(id='factory/cmm-air-system', title='Continuous metrology air supply alternatives', configuration_id=_hash({'cmm': cmm, 'compressor': bambi}),
        requirements=['Serve 100 free-air L/min published demand with 25% planning reserve and 20% leakage hypothesis',
                      'Preserve standby unit; qualify duty cycle, pressure stability and air quality'],
        interfaces=[{'id': 'cmm-air-outlet', 'published_consumer_pressure_bar': 7, 'accepted_quality_class': None}], variants=variants), experiments


def build():
    inputs, equipment, cfg, production = (_read(name) for name in (INPUTS, EQUIPMENT, FACTORY, PRODUCTION))
    software, experiments = _software(inputs)
    physics_systems, physics_experiments = _electrothermal(inputs)
    air, air_experiments = _cmm_air(cfg, equipment)
    systems = [software] + physics_systems + _equipment_systems(equipment, cfg) + [air]
    # Part identity is global across alternatives; parent links stay in their variant.
    for system in systems:
        for variant in system['variants']:
            prefix = system['id'] + '/' + variant['id'] + '/'
            for part in variant['parts']:
                part['id'] = prefix + part['id']
                if part['parent_id'] is not None:
                    part['parent_id'] = prefix + part['parent_id']
            variant['configuration_id'] = _hash({'parameters': variant['parameters'], 'parts': variant['parts']})
    names = [INPUTS, EQUIPMENT, FACTORY, PRODUCTION, 'engineering/twin_design/physics.py',
             'engineering/generative_design/twin_software_factory.py',
             'engineering/industrialisation/common.py',
             'engineering/twin_design/data/research-graph.json']
    requests = [dict(id='SF-calibration', owner='software-and-test', required_evidence=['Sensor asset IDs and calibrated accuracy/drift/latency',
        'Synchronized timestamp and sequence behavior, packet-loss bounds, telemetry transport and retention',
        'Measured voltage/current/temperature with SI units, source revision and calibration certificates',
        'Hold-out traces for independent validation; model parameters cannot be fitted against the same acceptance trace'],
        state='open', closure='paired measured/predicted residuals with approved uncertainty limits; no connected asset currently asserted'),
        dict(id='SF-control-release', owner='independent-assurance', state='open', required_evidence=[
            'Hazard analysis and safety allocation for every state and failure; physical interlocks and contactor feedback',
            'Target controller, executable build identity, secure update/rollback, watchdog and power-loss behavior',
            'Qualified transport timing, fault reset authorization, HIL and independently approved test evidence']),
        dict(id='SF-factory-production', owner='manufacturing', state='open', required_evidence=[
            'Exact offered machine origin, model/serial/GA, material/process and tooling configurations',
            'Commissioned process trials, measured scrap/yield/cycle time, labor, maintenance and cure-release data',
            'Iraqi utilities, ambient derating, foundations, guarding, lifting and environmental acceptance'],
             unmeasured_resource_basis=production, throughput_established=False),
        dict(id='SF-subcomponent-closure', owner='supplier-and-engineering', state='open', required_evidence=[
            'Equipment internal vendor BOM, bearings, drives, wiring, firmware, wear parts and repair documentation',
            'Qualified fasteners, connector pinouts, torque values, cable schedules and approved inspection limits'],
             closure='Every unknown leaf requires controlled drawing/data or explicit externally purchased boundary')]
    for system in systems:
        for variant in system['variants']:
            for item in variant['checks']:
                if item['state'] == 'unknown':
                    requests.append(dict(id='SF/' + system['id'] + '/' + variant['id'] + '/' + item['id'],
                        owner='domain-engineering', state='open', required_evidence=[item['limit']], affected_variant=variant['id']))
    result = dict(schema='osr-domain-design-twin/1', domain='software-factory',
        source_files={name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in names},
        systems=systems, experiments=experiments + physics_experiments + air_experiments,
        open_requests=requests, status='provisional-executable-design-twin; no installed/calibrated operational twin',
        telemetry_contract={'schema': 'osr-twin-observation/1',
            'required_fields': ['asset_id', 'configuration_id', 'signal_id', 'value', 'unit', 'observed_s', 'received_s',
                                'sequence', 'quality', 'calibration_id', 'source_revision'],
            'units': {'voltage': 'V', 'current': 'A', 'temperature': 'degC', 'energy': 'J', 'flow': 'free-air L/min'},
            'calibration_state': 'unmeasured', 'installed_asset_connection': False,
            'promotion': 'Independent hold-out replay, calibrated uncertainty and accepted parent checks required'})
    # Reject NaN/Infinity at the serialization boundary, including adverse fixtures.
    json.dumps(result, allow_nan=False)
    return result
