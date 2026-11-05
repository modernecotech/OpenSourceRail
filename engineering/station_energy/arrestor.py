"""Bounded staged-arrestor studies with separate physics and pricing identities."""
from copy import deepcopy
from collections import Counter
import json
from math import ceil, isclose, isfinite
from pathlib import Path
import time

from engineering.station_rail import ROOT
from engineering.station_rail.common import digest, encoded, identity
from engineering.design_search import native_search as io
from . import runner, arrestor_costs

PRODUCER = 'engineering/station_energy/arrestor.py'
SCHEMA = 'osr-multistage-arrestor-request/1'
RESULT_SCHEMA = 'osr-multistage-arrestor-result/1'
FLAGS = dict(physical_accepted=False, engineering_accepted=False,
    manufacturing_release=False, operating_release=False,
    selected_reference_changed=False, movement_authority=False)
FILES = {'request.json', 'physics.json', 'study.json', 'build-receipt.json'}
MAX_BYTES = 128*1024**2
MAX_CYCLES = 8
MAX_CONDITIONING_EVENTS = 10000


def sources(root=ROOT):
    return {**runner.sources(root), PRODUCER:digest(Path(root)/PRODUCER)}


def _seal(value, key):
    value[key] = identity(value)
    return value


def _reject_promotion(value):
    if isinstance(value, dict):
        for key, item in value.items():
            if key in FLAGS and item is not False:
                raise ValueError('Arrestor research cannot grant '+key)
            _reject_promotion(item)
    elif isinstance(value, list):
        for item in value:
            _reject_promotion(item)


def build(root=ROOT):
    before = sources(root)
    core = runner.build(root)
    binary = Path(root)/runner.TARGET/'release/osr-arrestor'
    if sources(root) != before:
        raise ValueError('Arrestor sources changed while building')
    receipt = _seal(dict(schema='osr-arrestor-build/1', source_sha256=before,
        build_command=runner.BUILD_COMMAND, tool_versions=core['tool_versions'],
        binary_sha256=digest(io._regular(binary))), 'receipt_id')
    runner._write(binary.with_suffix('.receipt.json'), receipt)
    return receipt


def _kernel(root):
    binary = Path(root)/runner.TARGET/'release/osr-arrestor'
    receipt = io._parse(io._read(binary.with_suffix('.receipt.json')))
    if (receipt.get('schema') != 'osr-arrestor-build/1'
        or receipt.get('receipt_id') != identity({k:v for k,v in receipt.items() if k != 'receipt_id'})
        or receipt.get('source_sha256') != sources(root)
        or receipt.get('tool_versions') != io._tools()
        or receipt.get('build_command') != runner.BUILD_COMMAND
        or receipt.get('binary_sha256') != digest(io._regular(binary))):
        raise ValueError('Arrestor kernel source/tool/binary context differs; rebuild explicitly')
    return binary, receipt


def calculate(request, root=ROOT):
    raw = encoded(request)
    if (not isinstance(request, dict) or set(request) != {'schema', 'cases'}
        or request.get('schema') != SCHEMA or not isinstance(request['cases'], list)
        or not 1 <= len(request['cases']) <= 1000 or len(raw) > runner.MAX_REQUEST_BYTES):
        raise ValueError('Explicit arrestor batch within 1000 cases / 8 MiB required')
    ids = [c.get('id') if isinstance(c, dict) else None for c in request['cases']]
    if any(not isinstance(i, str) or not i.strip() for i in ids) or len(set(ids)) != len(ids):
        raise ValueError('Unique arrestor case IDs required')
    binary, receipt = _kernel(root)
    result = io._parse(io._run([str(binary)], raw, cwd=root, timeout=30,
        maximum_output=MAX_BYTES))
    if (result.get('schema') != RESULT_SCHEMA
        or [r.get('id') for r in result.get('cases', [])] != ids
        or any(r.get(k) is not False for r in result['cases'] for k in FLAGS)
        or any(r.get('execution') != 'complete' for r in result['cases'])):
        raise ValueError('Arrestor result inventory or non-promoting disposition differs')
    if _kernel(root)[1] != receipt:
        raise ValueError('Arrestor evaluator changed during execution')
    return result, receipt


def _conditioning(case, result):
    """Sum identical nominal arrivals to saturation, without gifting charge.

    For a fully supplied, authorized flat-track event the usable-state map is
    E' = min(capacity, E + captured_after_conversion) - standing - withdrawn.
    Only its positive-gain branch is accelerated. The next Rust invocation must
    independently confirm the resulting periodic state and actual force bounds.
    """
    s, inputs = result['storage'], case['storage']
    if (result['failures'] or s['departure_state'] != 'nominal-transfer-only'
        or result['capture']['stages'] is None or s['request_shortfall_j'] > .0001
        or s['unresolved_capture_j'] != 0 or s['unrecovered_braking_j'] != 0
        or not isclose(s['standing_loss_j'], inputs['standing_loss_w']*inputs['dwell_s'],
                       rel_tol=0., abs_tol=.0001)):
        return None
    captured = s['accepted_j'] + s['overflow_j']
    gain = captured - s['standing_loss_j'] - s['withdrawn_j']
    end = inputs['capacity_j'] - s['standing_loss_j'] - s['withdrawn_j']
    start = s['end_j']
    if gain <= .0001 or end < inputs['reserve_j'] or end-start <= .0001:
        return None
    count = ceil((end-start)/gain)
    if not 1 <= count <= MAX_CONDITIONING_EVENTS:
        return None
    overflow = count*gain - (end-start)
    if overflow < -.0001:
        return None
    credited = sum(stage['credited_capture_j'] for stage in result['capture']['stages'])
    ledger = dict(id=case['id'], method='analytical-identical-nominal-event-sum/1',
        nominal_events=count, numerical_solver_events=0,
        initial_j=start, end_j=end, credited_capture_j=count*credited,
        capture_conversion_loss_j=count*s['capture_conversion_loss_j'],
        store_conversion_loss_j=count*s['store_conversion_loss_j'],
        overflow_j=max(0., overflow), standing_loss_j=count*s['standing_loss_j'],
        withdrawn_j=count*s['withdrawn_j'], delivered_j=count*s['delivered_j'],
        release_loss_j=count*s['release_loss_j'], requires_next_rust_cycle_check=True)
    residual = (start + ledger['credited_capture_j']
        - ledger['capture_conversion_loss_j'] - ledger['store_conversion_loss_j']
        - ledger['overflow_j'] - ledger['standing_loss_j'] - ledger['withdrawn_j'] - end)
    if not all(isfinite(v) for v in ledger.values() if type(v) in (int, float)):
        return None
    if abs(residual) > max(.0001, 1e-12*ledger['credited_capture_j']):
        return None
    ledger['balance_residual_j'] = residual
    return ledger


def physics(request, root=ROOT):
    """Carry one store state per event stream; retain every nominal cycle.

    Each case is an independent station-side store, not another claimant to a
    shared energy balance. At most eight solver batches and 10,000 analytically
    accounted conditioning arrivals per transition bound this invocation.
    Unclosed states receive no recurring annual saving.
    """
    current = deepcopy(request)
    cycles = []
    for _ in range(MAX_CYCLES):
        result, receipt = calculate(current, root)
        cycles.append(dict(request=current, result=result))
        closed = [isclose(r['storage']['end_j'], c['storage']['initial_j'],
            rel_tol=0.0, abs_tol=.0001) for c,r in zip(current['cases'], result['cases'], strict=True)]
        if all(closed):
            break
        conditioning = []
        current = deepcopy(current)
        for c, r, is_closed in zip(current['cases'], result['cases'], closed, strict=True):
            c['storage']['initial_j'] = r['storage']['end_j']
            entry = None if is_closed else _conditioning(c, r)
            if entry is not None:
                conditioning.append(entry)
                c['storage']['initial_j'] = entry['end_j']
        if conditioning:
            cycles[-1]['conditioning_after'] = conditioning
    return _seal(dict(schema='osr-arrestor-cyclic-physics/1',
        request_id=identity(request), build_receipt_id=receipt['receipt_id'],
        source_sha256=sources(root), cycles=cycles, cyclic_storage_closed=closed,
        maximum_cycles=MAX_CYCLES,
        maximum_conditioning_events=MAX_CONDITIONING_EVENTS,
        model_scope='Flat-track nominal point-mass motion, usable storage and quasistatic force distribution',
        **FLAGS), 'physics_evaluation_id'), receipt


def price(value, root=ROOT):
    last = value['cycles'][-1]
    context = arrestor_costs.prepare(root)
    rows = []
    for inputs, result, closed in zip(last['request']['cases'], last['result']['cases'],
                                      value['cyclic_storage_closed'], strict=True):
        cost = arrestor_costs.estimate(inputs, result,
            cyclic_storage_closed=closed, root=root, context=context)
        rows.append(dict(id=result['id'], input=inputs, physics=result, estimate=cost))
    if arrestor_costs.sources(root) != context[1]:
        raise ValueError('Pricing source context changed during the batch')
    return _seal(dict(schema='osr-arrestor-study/1',
        physics_evaluation_id=value['physics_evaluation_id'],
        cost_source_sha256=context[1], cases=rows,
        execution_complete=True, preferred_architecture=None, preferred_speed_kmh=None,
        whole_railway_optimised=False, fleet_or_corridor_price=None,
        counts=dict(cases=len(rows), necessary_bounds=dict(Counter(r['physics']['necessary_bounds'] for r in rows)),
            costed_station_modules=sum(r['estimate']['estimate_complete'] for r in rows),
            cyclic_stores_closed=sum(value['cyclic_storage_closed']), solver_batches=len(value['cycles']),
            numerical_case_events=sum(len(cycle['result']['cases']) for cycle in value['cycles']),
            nominal_case_events_analytically_accounted=sum(e['nominal_events'] for cycle in value['cycles']
                for e in cycle.get('conditioning_after', []))),
        costs_are_scoped_estimates=True, **FLAGS), 'evaluation_id')


def _write(output, request, value, receipt, study, *, invocations):
    output = Path(output)
    if output.exists():
        raise ValueError('A fresh immutable arrestor output directory is required')
    output.mkdir(parents=True)
    for name, record in (('request.json', request), ('physics.json', value),
                         ('study.json', study), ('build-receipt.json', receipt)):
        runner._write(output/name, record)
    manifest = _seal(dict(schema='osr-arrestor-study-manifest/1',
        evaluation_id=study['evaluation_id'], physics_evaluation_id=value['physics_evaluation_id'],
        physics_source_sha256=value['source_sha256'],
        cost_source_sha256=study['cost_source_sha256'],
        files_sha256={n:digest(output/n) for n in sorted(FILES)}, **FLAGS), 'manifest_id')
    runner._write(output/'manifest.json', manifest)
    runner._write(output/'performance.json', dict(rust_invocations=invocations,
        physics_cache_reused=invocations == 0, cases=len(request['cases']),
        replay_is_independent_recalculation=False))
    return manifest


def run(output, request, root=ROOT):
    if Path(output).exists():
        raise ValueError('A fresh immutable arrestor output directory is required')
    started = time.monotonic()
    value, receipt = physics(request, root)
    result = _write(output, request, value, receipt, price(value, root),
        invocations=len(value['cycles']))
    timing = io._parse(io._read(Path(output)/'performance.json'))
    timing['wall_seconds'] = time.monotonic()-started
    runner._write(Path(output)/'performance.json', timing)
    return result


def _read(output, root):
    output = Path(output)
    m = io._parse(io._read(output/'manifest.json'))
    if (m.get('schema') != 'osr-arrestor-study-manifest/1'
        or m.get('manifest_id') != identity({k:v for k,v in m.items() if k != 'manifest_id'})
        or set(m.get('files_sha256', {})) != FILES
        or any(m.get(k) is not False for k in FLAGS)
        or m.get('physics_source_sha256') != sources(root)):
        raise ValueError('Arrestor manifest/source context differs')
    for name, expected in m['files_sha256'].items():
        if digest(io._regular(output/name)) != expected:
            raise ValueError('Arrestor artifact differs: '+name)
    records = {n:io._parse(io._read(output/n, MAX_BYTES)) for n in FILES}
    _reject_promotion(records['physics.json'])
    value = records['physics.json']
    if (value.get('physics_evaluation_id') != identity({k:v for k,v in value.items() if k != 'physics_evaluation_id'})
        or value['physics_evaluation_id'] != m['physics_evaluation_id']
        or value['source_sha256'] != sources(root)
        or value['request_id'] != identity(records['request.json'])
        or any(value.get(k) is not False for k in FLAGS)
        or records['build-receipt.json'] != _kernel(root)[1]
        or value['build_receipt_id'] != records['build-receipt.json']['receipt_id']):
        raise ValueError('Stored arrestor physics identity or build context differs')
    return m, records


def reprice(output, previous, root=ROOT):
    """Reuse exact-source cached physics; price changes do not rerun motion.

    This cooperative cache check is not an independent physical calculation.
    The normal verify action replays all events before accepting a publication.
    """
    _, records = _read(previous, root)
    value = records['physics.json']
    return _write(output, records['request.json'], value, records['build-receipt.json'],
        price(value, root), invocations=0)


def verify(output, root=ROOT):
    manifest, records = _read(output, root)
    if manifest['cost_source_sha256'] != arrestor_costs.sources(root):
        raise ValueError('Arrestor price context differs; reprice into a fresh output')
    actual, receipt = physics(records['request.json'], root)
    study = price(actual, root)
    if (actual != records['physics.json'] or receipt != records['build-receipt.json']
        or study != records['study.json'] or study['evaluation_id'] != manifest['evaluation_id']):
        raise ValueError('Arrestor independent calculation replay differs')
    return manifest


def _reference_content(request, study):
    rows, selected = [], []
    for row in study['cases']:
        c, r, cost = row['input'], row['physics'], row['estimate']
        record = dict(id=row['id'], necessary_bounds=r['necessary_bounds'],
            cyclic_storage_closed=cost.get('cyclic_storage_closed', False),
            costed=cost['estimate_complete'], active_store_kg=r['sizing']['active_mass_kg'],
            capture_path_m=r['capture']['total_distance_m'],
            launch_path_m=r['launch']['distance_m'] if r['launch'] else None,
            remaining_booster_path_m=r['booster']['distance_m'] if r['booster'] else None,
            module_installed_usd={k:v['installed_usd'] for k,v in cost['costs'].items()} if cost['estimate_complete'] else None,
            module_npv_usd={k:v['thirty_year_npv_usd'] for k,v in cost['costs'].items()} if cost['estimate_complete'] else None)
        rows.append(record)
        sample = (row['id'] == 'no-capture-v60' or
            (c['capture_entry_speed_m_s'] == 10.0
             and c['booster']['target_speed_m_s'] == 60/3.6
             and c['handover'] == 'continuous-total-force'
             and c['stages'][0]['displacement_ratio'] == 10.0
             and c['launch']['force_fractions'][-1] == 1.0))
        if sample:
            selected.append(dict(**record, input=c, physics=r,
                estimate={k:v for k,v in cost.items() if k != 'cost_evaluation_id'}))
    return dict(input_request_id=identity(request), counts=study['counts'],
        comparison_scope='Illustrative station-module budgets and required nominal motion; not whole-railway optimisation',
        sample_purpose='10 m/s capture, 60 km/h target, ratio 10, continuous total force and rear launch; not a preferred selection',
        cases=rows, selected_samples=selected, **FLAGS)


def publish_reference(state, root=ROOT):
    """Publish compact scalars and five samples; full cycle records stay private."""
    verify(state, root)
    _, records = _read(state, root)
    from . import arrestor_examples
    if records['request.json'] != arrestor_examples.request(root):
        raise ValueError('Canonical arrestor research request differs; keep custom studies separate')
    names = ('engineering/station_energy/arrestor_examples.py', arrestor_examples.POLICY)
    value = _seal(dict(schema='osr-arrestor-reference/1',
        source_sha256={**sources(root), **arrestor_costs.sources(root),
            **{n:digest(Path(root)/n) for n in names}},
        producer_evaluation_id=records['study.json']['evaluation_id'],
        producer_physics_evaluation_id=records['physics.json']['physics_evaluation_id'],
        content=_reference_content(records['request.json'], records['study.json']), **FLAGS), 'publication_id')
    path = Path(root)/'docs/design-engine/station-regenerative-launch/reference.json'
    runner._write(path, value)
    return value


def _close(expected, actual):
    if type(expected) in (int, float) and type(actual) in (int, float):
        if not isclose(expected, actual, rel_tol=1e-9, abs_tol=1e-6):
            raise ValueError('Arrestor reference numerical result differs')
    elif isinstance(expected, dict) and isinstance(actual, dict) and set(expected) == set(actual):
        for key in expected:
            _close(expected[key], actual[key])
    elif isinstance(expected, list) and isinstance(actual, list) and len(expected) == len(actual):
        for a, b in zip(expected, actual, strict=True):
            _close(a, b)
    elif expected != actual or type(expected) is not type(actual):
        raise ValueError('Arrestor reference scope or result differs')


def verify_reference(root=ROOT, *, state=None):
    path = Path(root)/'docs/design-engine/station-regenerative-launch/reference.json'
    value = io._parse(io._read(path, MAX_BYTES))
    _reject_promotion(value)
    from . import arrestor_examples
    expected_sources = {**sources(root), **arrestor_costs.sources(root),
        **{n:digest(Path(root)/n) for n in ('engineering/station_energy/arrestor_examples.py', arrestor_examples.POLICY)}}
    if (value.get('schema') != 'osr-arrestor-reference/1'
        or value.get('publication_id') != identity({k:v for k,v in value.items() if k != 'publication_id'})
        or value.get('source_sha256') != expected_sources
        or value.get('content', {}).get('input_request_id') != identity(arrestor_examples.request(root))
        or any(value.get(k) is not False for k in FLAGS)):
        raise ValueError('Arrestor reference source or disposition differs')
    if state is not None:
        verify(state, root)
        _, records = _read(state, root)
        _close(value['content'], _reference_content(records['request.json'], records['study.json']))
    return value


def render_reference(root=ROOT):
    value = verify_reference(root)
    content = value['content']
    lines = ['<!-- arrestor-results:start -->', '### Calculated G station-module comparison', '',
        'This sample uses 160 t effective train mass, 10 m/s capture, a 60 km/h departure target, ratio 10, continuous aggregate handover and rear launch. Conversion efficiency, material properties, process times, cycle lives and rates are declared hypotheses. No storage technology or launcher arrangement is selected.', '',
        '| Sample | Active store material / vessel mass | Estimated module installed cost, low / base / high | Base 30-year module NPV |',
        '| --- | --- | --- | --- |']
    for row in content['selected_samples']:
        prices = row['module_installed_usd']
        if prices is None:
            continue
        name = 'No recovery' if row['id'].startswith('no-capture') else row['id'].split('-c10')[0]
        amounts = ' / '.join(f"${prices[k]/1000:,.0f}k" for k in ('low', 'base', 'high'))
        lines.append(f"| {name} | {row['active_store_kg']/1000:,.2f} t | {amounts} | ${row['module_npv_usd']['base']/1e6:,.2f}m |")
    n = content['counts']
    lines += ['', f"The bounded campaign completed {n['cases']} scenarios and priced {n['costed_station_modules']} station modules after repeating arrival/hold/release events to check storage-state closure. Its release conditions remain unknown or failed where stated, independently of calculation completion.", '',
        'These budgets include declared capture/transmission/store/launcher/remaining-booster hardware, protection, cooling, delivery, installation, support allowances, energy, inspection and renewal. Tooling is allocated once across an illustrative 22-site production batch; production and civil work use two shifts. Actual storage, controls, interfaces, contact, fatigue, foundations and safe stopping remain unqualified.', '',
        'The comparison excludes the rest of the railway. Per-train interface allowances are reported separately, and a candidate-specific fleet/corridor budget remains open. Required active acceleration distance is not installed winding length. Material/rim mass is not a complete installed store mass; hydraulic fluid and flywheel containment are additional lines. Low/base/high values are engineering sensitivities, not supplier quotes or confidence intervals.', '',
        f"Compact calculation and source records: [reference.json](reference.json), publication `{value['publication_id']}`. The originating execution has physics identity `{value['producer_physics_evaluation_id']}`; new compiler/binary contexts receive their own execution identities. CI independently checks the reference numbers with declared numerical tolerances.",
        '<!-- arrestor-results:end -->']
    path = Path(root)/'docs/design-engine/station-regenerative-launch/README.md'
    text = path.read_text()
    start, end = '<!-- arrestor-results:start -->', '<!-- arrestor-results:end -->'
    block = '\n'.join(lines)
    if start in text:
        a, b = text.index(start), text.index(end)+len(end)
        text = text[:a]+block+text[b:]
    else:
        text = text.rstrip()+'\n\n'+block+'\n'
    path.write_text(text)
    return value['publication_id']
