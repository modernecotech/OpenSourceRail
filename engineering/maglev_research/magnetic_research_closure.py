"""Audit retained magnetic research and run isolated, bounded winding searches.

The search uses the retained reluctance model. It cannot validate its flux
allocation or authorise a configuration, manufacturing, or physical release.
"""
from hashlib import sha256
import argparse
import itertools
import json
import math
from pathlib import Path
import subprocess
import sys
import tempfile
import tomllib
import types


ROOT = Path(__file__).resolve().parents[2]
ARCHIVE = Path('engineering/assurance/v053-pole-return-research/archive')
WORKER = Path(__file__).with_name('_magnetic_research_sweep.py')
G = 9.80665
SOURCE_NAMES = (str(ARCHIVE / 'manifest.json'),
                'engineering/maglev_research/magnetic_research_closure.py',
                'engineering/maglev_research/_magnetic_research_sweep.py')


def _encoded(value):
    return (json.dumps(value, sort_keys=True, indent=2, allow_nan=False) + '\n').encode()


def _plans():
    return itertools.product((.020, .0225, .025, .0275, .030, .035),
                             (1.5, 1.75, 2., 2.2, 2.4), (140., 200.), (False, True), (False, True))


def _hypothesis(plan):
    width, scale, turns, large, sensitive = plan
    outer = [.72 if large else .62, .188]
    inner = [.16 * scale + .02, .10]
    pack_volume = (math.prod(outer) - math.prod(inner)) * .073
    mean_length = sum(inner) + sum(outer)
    area = .549 * pack_volume / (turns * mean_length) * 1e6
    return dict(width_m=width, core_scale=scale, guide_turns=turns,
                guide_conductor_area_mm2=area, wide_pack=large,
                topology='useful-only-poles-sensitivity' if sensitive else 'original-branch-flux',
                guide_copper_fill_target=.549)


def _same(actual, expected, label):
    if (type(actual) not in (int, float) or not math.isfinite(actual)
            or not math.isclose(actual, expected, rel_tol=1e-9, abs_tol=1e-8)):
        raise ValueError(label + ' differs from raw research')


def _equal(actual, expected, label):
    if actual != expected or type(actual) is not type(expected):
        raise ValueError(label + ' differs from raw research')


def _load(root):
    archive = Path(root) / ARCHIVE
    # Loading bytecode through importlib would add __pycache__ inside the
    # sealed archive and invalidate its complete inventory.
    verifier = types.ModuleType('osr_retained_magnetic_verifier')
    verifier.__file__ = str(archive / 'verify.py')
    exec(compile((archive / 'verify.py').read_bytes(), verifier.__file__, 'exec'), verifier.__dict__)
    members, read = verifier.verify_archive(archive)
    records = {name: read(name) for name in verifier.RECORDS}
    inputs = tomllib.loads((archive / 'inputs/engineering/ferrite_maglev/candidate-magnetics.toml').read_text())
    summary = json.loads((archive / 'summary.json').read_text())
    return archive, members, records, inputs, summary


def _joint_point(row):
    target = row['target_n_per_module']
    points = [point for point in row['simultaneous_points']
              if math.isclose(point['target_n'][0], target, rel_tol=1e-10)
              and math.isclose(point['target_n'][1], .1 * target, rel_tol=1e-10)]
    if len(points) != 1:
        raise ValueError('one exact simultaneous AW3/0.1 AW3 point required')
    return points[0]


def _guidance(row, inputs, parent_mass, parent_module_mass):
    """Recompute mass, fill, density, and constant-current heat balance."""
    module = row['hypothesis']['module_geometry']
    coils = module['coils']
    count = inputs['module_count_per_car']
    _same(module['mass_kg'], sum(part['mass_kg'] for part in module['parts']), 'module stock mass')
    _same(row['module_mass_kg'], module['mass_kg'], 'recorded module mass')
    _same(row['controlled_aw3_kg'], parent_mass + count * (module['mass_kg'] - parent_module_mass), 'AW3 mass feedback')
    _same(row['target_n_per_module'], row['controlled_aw3_kg'] * G / count, 'module force allocation')
    fills = []
    for coil in coils:
        fill = coil['conductor_length_m'] * coil['conductor_area_mm2'] * 1e-6 / (
            (math.prod(coil['outer_m']) - math.prod(coil['inner_m'])) * coil['height_m'])
        _same(coil['fill_fraction'], fill, 'copper fill')
        fills.append(fill)
    fill_pass = max(fills) <= inputs['coil_fill_limit']
    _equal(row['coil_fill_pass'], fill_pass, 'fill screen')
    point = _joint_point(row)
    current = point['required_current_a']
    areas = [coils[0]['conductor_area_mm2'], coils[1]['conductor_area_mm2']]
    density = [abs(i) / area for i, area in zip(current, areas)]
    for actual, expected in zip(point['current_density_a_mm2'], density):
        _same(actual, expected, 'current density')
    density_pass = max(density) <= inputs['continuous_current_density_a_mm2']
    _equal(point['continuous_current_density_screen'], density_pass, 'density screen')
    copper = inputs['materials']['copper']
    variant = next(v for v in inputs['variants'] if v['id'] == inputs['selected_variant'])
    conductance = variant['cooling_w_k']
    r20 = [coils[0]['conductor_length_m'] / (areas[0] * 1e-6) * copper['resistivity_20c_ohm_m'],
           sum(c['conductor_length_m'] for c in coils[1:]) / (areas[1] * 1e-6) * copper['resistivity_20c_ohm_m']]
    ambient = inputs['ambient_c']
    limit = inputs['maximum_copper_c']
    alpha = copper['resistance_temperature_coefficient_per_k']
    equilibrium = []
    required_cooling = []
    for circuit in range(2):
        heat20 = current[circuit] ** 2 * r20[circuit]
        feedback = heat20 * alpha
        temperature = None if conductance[circuit] <= feedback else (
            ambient + heat20 * (1 + alpha * (ambient - 20)) / (conductance[circuit] - feedback))
        equilibrium.append(temperature)
        actual = point['constant_current_thermal_equilibrium_c'][circuit]
        if temperature is None:
            _equal(actual, None, 'thermal equilibrium')
        else:
            _same(actual, temperature, 'thermal equilibrium')
        required_cooling.append(heat20 * (1 + alpha * (limit - 20)) / (limit - ambient))
    thermal_pass = all(t is not None and t <= limit for t in equilibrium)
    _equal(point['constant_current_thermal_screen'], thermal_pass, 'thermal screen')
    map_pass = (point['domain_valid'] and point['canonical_converged']
                and max(abs(i) for i in current) <= inputs['current_limit_a']
                and point['minimum_demag_margin_a_m'] > 0 and point['max_core_b_t'] < 2.2)
    _equal(point['map_valid'], bool(map_pass), 'field/current screen')
    for actual, target in zip(point['actual_force_n'], point['target_n']):
        _same(actual, target, 'achieved joint force')
    fit = row['hypothesis']['fit']['nominal_aabb_clear']
    passed = bool(fit and fill_pass and map_pass and density_pass and thermal_pass)
    _equal(row['conditional_nominal_aw3_lateral_screen'], passed, 'combined joint screen')
    area_required = [abs(i) / inputs['continuous_current_density_a_mm2'] for i in current]
    return dict(id=row['hypothesis']['id'], module_mass_kg=row['module_mass_kg'],
                controlled_aw3_kg=row['controlled_aw3_kg'], nominal_fit=fit,
                copper_fill_pass=fill_pass, map_pass=bool(map_pass),
                current_density_pass=density_pass, thermal_pass=thermal_pass,
                combined_screen_pass=passed, current_a=current, current_density_a_mm2=density,
                equilibrium_c=equilibrium,
                fixed_load_required_conductor_area_mm2=area_required,
                fixed_load_required_cooling_at120c_w_k=required_cooling,
                fixed_load_required_guide_fill=fills[1] * area_required[1] / areas[1],
                required_guide_cooling_ratio=required_cooling[1] / conductance[1],
                scope='Sizing lower bounds at archived force, mass and current only; winding/cooling redesign must recount mass and resolve both forces.')


def assess(records, inputs, summary):
    """Derive the magnetic feedback checks from verified raw case records."""
    initial = records['results.json']
    topology = records['topology-results.json']
    controls = records['controls-results.json']
    guidance = records['guidance-results.json']
    groups = dict(original_geometry_winding_cases=len(initial['cases']),
                  refinement_topology_cases=len(topology['cases']),
                  exact_baseline_asymmetric_controls=len(controls['cases']),
                  guidance_winding_cases=len(guidance['cases']))
    for name, count in groups.items():
        _equal(summary['executed'][name], count, 'executed ' + name)
    for record in records.values():
        if 'executed_cases' in record:
            _equal(record['executed_cases'], len(record['cases']), 'executed case inventory')
        for flag in ('configuration_adopted', 'complete_system_feasible', 'physical_validation', 'engineering_accepted'):
            _equal(record[flag], False, flag)
    original_static = sum(row['conditional_static_screen'] for row in initial['cases'])
    original_peak = sum(row['adverse_peak_current_and_flux_screen'] for row in initial['cases'])
    original_peak += sum(row['adverse_peak_current_and_flux_screen'] for row in topology['cases'] if not row['topology_sensitivity'])
    conditional_peak = sum(row['adverse_peak_current_and_flux_screen'] for row in topology['cases'] if row['topology_sensitivity'])
    _equal(summary['original_cases_with_static_screen'], original_static, 'original static count')
    _equal(summary['original_cases_with1_3screen'], original_peak, 'original 1.3 AW3 count')
    _equal(summary['topological_sensitivities_with1_3screen'], conditional_peak, 'sensitive 1.3 AW3 count')
    baseline_rows = [row for row in controls['cases'] if row['hypothesis']['id'].startswith('exact-baseline-')]
    baseline_invariant = len(baseline_rows) == 4 and all(
        row['necessary_25mm_return_only_2_2t_force_bound_n'] < row['module_own_weight_n'] < row['target_n']
        for row in baseline_rows)
    _equal(summary['baseline_failure_invariant'], baseline_invariant, 'baseline invariant')
    baseline = next(row for row in baseline_rows if row['hypothesis']['id'] == 'exact-baseline-original')
    _same(summary['parent']['force_at120a_n'], baseline['source_gap8mm_current120_force_n'], 'canonical lift')
    _same(summary['parent']['aw3_kg'], initial['parent_aw3_kg'], 'canonical AW3 mass')
    _equal(summary['parent']['configuration_sha256'], initial['parent_configuration_sha256'], 'canonical identity')
    rows = [_guidance(row, inputs, initial['parent_aw3_kg'], initial['parent_module_mass_kg']) for row in guidance['cases']]
    _equal(summary['fitting_guidance_cases'], sum(row['nominal_fit'] for row in rows), 'nominal fit count')
    _equal(summary['guidance_copper_fill_passes'], sum(row['copper_fill_pass'] for row in rows), 'fill pass count')
    _equal(summary['guidance_combined_screen_passes'], sum(row['combined_screen_pass'] for row in rows), 'guidance combined count')
    fitting = [row for row in rows if row['nominal_fit'] and row['copper_fill_pass']]
    best = min(fitting, key=lambda row: (max(row['current_density_a_mm2']), row['controlled_aw3_kg']))
    _equal(summary['best_fitting_guidance']['id'], best['id'], 'best fitting identity')
    _same(summary['best_fitting_guidance']['controlled_aw3_kg'], best['controlled_aw3_kg'], 'best fitting AW3 mass')
    return dict(schema='osr-magnetic-research-closure/1', canonical_configuration_sha256=initial['parent_configuration_sha256'],
                archive_semantic_checks_passed=True, executed=groups,
                executed_case_records=sum(groups.values()), original_static_passes=original_static,
                original_1_3_aw3_passes=original_peak, conditional_topology_1_3_aw3_passes=conditional_peak,
                baseline_failure_invariant=baseline_invariant, guidance_combined_passes=sum(row['combined_screen_pass'] for row in rows),
                best_fitting_guidance=best, guidance_cases=rows,
                closure_gates=[
                    dict(id='MAG-TOPOLOGY', state='open', evidence='Independent finite geometry nonlinear spatial maps and rig correlation; same-network energy checks cannot close this gate.'),
                    dict(id='MAG-JOINT-DUTY', state='failed', evidence='One exact counted candidate must meet simultaneous AW3 lift and lateral force, current density, fill, field and repeated thermal duty.'),
                    dict(id='MAG-MASS-FEEDBACK', state='open', evidence='Recount copper, insulation, manifolds, coldplates, cooling power and protection, then rerun joint support demand.'),
                    dict(id='MAG-DYNAMIC-MAPS', state='open', evidence='Gap, current, temperature and fault maps need calibrated force/linkage/loss/demagnetisation data before dynamics adoption.')],
                configuration_adopted=False, engineering_accepted=False, physical_validation=False,
                complete_system_feasible=False)


def audit(root=ROOT):
    """Return a fresh semantic audit without writing or rerunning the model."""
    archive, _, records, inputs, summary = _load(root)
    result = assess(records, inputs, summary)
    result['source_sha256'] = {
        (ARCHIVE / 'manifest.json').as_posix(): sha256((archive / 'manifest.json').read_bytes()).hexdigest(),
        Path(__file__).relative_to(ROOT).as_posix(): sha256(Path(__file__).read_bytes()).hexdigest()}
    return result


def validate_optimisation(value, root=ROOT):
    """Check the complete fixed search and independently derive its screens."""
    if value.get('schema') != 'osr-bounded-magnetic-winding-optimisation/1':
        raise ValueError('bounded magnetic optimisation schema required')
    for flag in ('configuration_adopted', 'complete_system_feasible', 'engineering_accepted', 'physical_validation'):
        _equal(value.get(flag), False, 'optimisation ' + flag)
    sources = value.get('source_sha256')
    if not isinstance(sources, dict) or set(sources) != set(SOURCE_NAMES):
        raise ValueError('exact three optimisation source bindings required')
    for name, expected in sources.items():
        if sha256((Path(root) / name).read_bytes()).hexdigest() != expected:
            raise ValueError('stale optimisation source: ' + name)
    archive, _, records, inputs, _ = _load(root)
    manifest = json.loads((archive / 'manifest.json').read_text())
    source_model = {name: expected for name, expected in records['results.json']['source_sha256'].items()
                    if not name.startswith('build/')}
    _equal(value.get('source_model_sha256'), source_model, 'frozen source model inventory')
    for name, expected in source_model.items():
        _equal(manifest['files_sha256']['inputs/' + name], expected, 'frozen model source')
    parent = records['results.json']
    _equal(value.get('parent_configuration_sha256'), parent['parent_configuration_sha256'], 'optimisation parent')
    rows = value.get('cases')
    if not isinstance(rows, list) or len(rows) != 240:
        raise ValueError('complete fixed 240-case optimisation required')
    _equal(value.get('executed_cases'), 240, 'optimisation executed count')
    cu = inputs['materials']['copper']
    ambient, maximum = inputs['ambient_c'], inputs['maximum_copper_c']
    variant = next(v for v in inputs['variants'] if v['id'] == inputs['selected_variant'])
    conductance = variant['cooling_w_k']
    passes, fitting = 0, []
    for number, (row, plan) in enumerate(zip(rows, _plans())):
        hypothesis = _hypothesis(plan)
        _equal(row['id'], f'closure-{number:03d}', 'optimisation case identity')
        _equal(row['hypothesis'], hypothesis, 'optimisation hypothesis grid')
        _equal(row['hypothesis_sha256'], sha256(_encoded(hypothesis)).hexdigest(), 'optimisation hypothesis digest')
        _equal(row['hypothesis_sha256'], sha256(_encoded(row['hypothesis'])).hexdigest(), 'recorded hypothesis digest')
        _same(row['module_mass_kg'], row['counted_stock_mass_kg'], 'optimisation counted mass')
        if row['module_mass_kg'] <= 0:
            raise ValueError('positive optimisation module mass required')
        aw3 = parent['parent_aw3_kg'] + inputs['module_count_per_car'] * (row['module_mass_kg'] - parent['parent_module_mass_kg'])
        _same(row['controlled_aw3_kg'], aw3, 'optimisation AW3 mass feedback')
        target = aw3 * G / inputs['module_count_per_car']
        x = .16 * hypothesis['core_scale']
        lift_area = 23.5
        areas = [lift_area, hypothesis['guide_conductor_area_mm2']]
        lengths = [140 * (2 * x + .60),
                   2 * hypothesis['guide_turns'] * (x + .02 + .10 + (.72 if hypothesis['wide_pack'] else .62) + .188)]
        r20 = [length / (area * 1e-6) * cu['resistivity_20c_ohm_m'] for length, area in zip(lengths, areas)]
        lift_fill = lengths[0] * lift_area * 1e-6 / (((x + .12) * .28 - (x + .02) * .18) * .12)
        for actual, expected in zip(row['copper_fill_fractions'], [lift_fill, .549, .549]):
            _same(actual, expected, 'optimisation copper fill')
        if len(row['copper_fill_fractions']) != 3:
            raise ValueError('three physical optimisation coils required')
        if type(row['nominal_aabb_clear']) is not bool or type(row['collision_count']) is not int:
            raise ValueError('typed nominal clearance evidence required')
        _equal(row['nominal_aabb_clear'], row['collision_count'] == 0, 'optimisation nominal clearance')
        for key, up in (('nominal_joint', target), ('adverse_joint', 1.3 * target)):
            point = row[key]
            if any(not isinstance(point.get(name), list) or len(point[name]) != 2 for name in (
                    'target_n', 'actual_force_n', 'force_error_n', 'required_current_a',
                    'current_density_a_mm2', 'constant_current_thermal_equilibrium_c')):
                raise ValueError('complete two-circuit joint fields required')
            _equal(point['geometric_two_force_solution'], True, 'optimisation joint force solution')
            _equal(point['no_current_clamp'], True, 'optimisation unclamped current')
            for actual, expected in zip(point['target_n'], [up, .1 * target]):
                _same(actual, expected, 'optimisation force target')
            for actual, expected in zip(point['actual_force_n'], point['target_n']):
                _same(actual, expected, 'optimisation achieved force')
            for actual, force, demand in zip(point['force_error_n'], point['actual_force_n'], point['target_n']):
                _same(actual, force - demand, 'optimisation force residual')
            current = point['required_current_a']
            if len(current) != 2 or len(point['current_density_a_mm2']) != 2:
                raise ValueError('two optimisation circuits required')
            density = [abs(i) / area for i, area in zip(current, areas)]
            for actual, expected in zip(point['current_density_a_mm2'], density):
                _same(actual, expected, 'optimisation current density')
            _equal(point['continuous_current_density_screen'], max(density) <= inputs['continuous_current_density_a_mm2'], 'optimisation density screen')
            _equal(point['domain_valid'], max(abs(i) for i in current) <= inputs['current_limit_a'], 'optimisation current domain')
            if type(point['canonical_converged']) is not bool:
                raise ValueError('typed optimisation convergence required')
            _equal(point['map_valid'], bool(point['domain_valid'] and point['canonical_converged']
                   and point['minimum_demag_margin_a_m'] > 0 and point['max_core_b_t'] < 2.2), 'optimisation field screen')
            equilibrium = []
            for i, resistance, cooling in zip(current, r20, conductance):
                heat = i * i * resistance
                feedback = heat * cu['resistance_temperature_coefficient_per_k']
                equilibrium.append(None if cooling <= feedback else ambient + heat * (1 + cu['resistance_temperature_coefficient_per_k'] * (ambient - 20)) / (cooling - feedback))
            for actual, expected in zip(point['constant_current_thermal_equilibrium_c'], equilibrium):
                if expected is None:
                    _equal(actual, None, 'optimisation thermal equilibrium')
                else:
                    _same(actual, expected, 'optimisation thermal equilibrium')
            _equal(point['constant_current_thermal_screen'], all(t is not None and t <= maximum for t in equilibrium), 'optimisation thermal screen')
        nominal = row['nominal_joint']
        cooling_needed = [i * i * resistance * (1 + cu['resistance_temperature_coefficient_per_k'] * (maximum - 20)) / (maximum - ambient)
                          for i, resistance in zip(nominal['required_current_a'], r20)]
        if len(row['fixed_current_required_cooling_at120c_w_k']) != 2:
            raise ValueError('two optimisation cooling requirements required')
        for actual, expected in zip(row['fixed_current_required_cooling_at120c_w_k'], cooling_needed):
            _same(actual, expected, 'optimisation required cooling')
        ratios = dict(density=max(nominal['current_density_a_mm2']) / inputs['continuous_current_density_a_mm2'],
                      current=max(abs(i) for i in nominal['required_current_a']) / inputs['current_limit_a'],
                      field=nominal['max_core_b_t'] / 2.2,
                      thermal=max(required / available for required, available in zip(cooling_needed, conductance)))
        if set(row['normalised_constraint_ratios']) != set(ratios):
            raise ValueError('complete optimisation ranking constraints required')
        for name, expected in ratios.items():
            _same(row['normalised_constraint_ratios'][name], expected, 'optimisation ' + name + ' ratio')
        fit = row['nominal_aabb_clear'] and max(row['copper_fill_fractions']) <= inputs['coil_fill_limit']
        violation = max(*ratios.values(), 1. if fit else 1e30)
        _same(row['maximum_constraint_ratio'], violation, 'optimisation ranking score')
        passed = bool(fit and nominal['map_valid'] and nominal['continuous_current_density_screen'] and nominal['constant_current_thermal_screen'])
        _equal(row['joint_screen_pass'], passed, 'optimisation joint screen')
        _equal(row['topology_independently_validated'], False, 'optimisation topology validation')
        _equal(row['configuration_adopted'], False, 'optimisation case adoption')
        passes += passed
        if fit:
            fitting.append(row)
    _equal(value['nominal_fit_and_fill_cases'], len(fitting), 'optimisation fitting count')
    _equal(value['joint_screen_passes'], passes, 'optimisation survivor count')
    ranked = sorted(fitting, key=lambda row: (row['maximum_constraint_ratio'], row['controlled_aw3_kg'], row['id']))
    best = {name: next((row for row in ranked if row['hypothesis']['topology'] == name), None)
            for name in ('original-branch-flux', 'useful-only-poles-sensitivity')}
    _equal(value['best_by_topology'], best, 'optimisation best cases')
    return value


def optimise(output, root=ROOT):
    """Execute the finite sweep using only reconstructed frozen model inputs."""
    output = Path(output)
    if output.exists():
        raise ValueError('retain prior optimisation evidence; output already exists')
    archive, members, _, _, _ = _load(root)
    snapshot = {name: (Path(root) / name).read_bytes() for name in SOURCE_NAMES}
    manifest = json.loads(snapshot[SOURCE_NAMES[0]])
    with tempfile.TemporaryDirectory(prefix='osr-magnetic-closure-') as temporary:
        tree = Path(temporary)
        for name in members:
            if name.startswith('inputs/'):
                target = tree / name.removeprefix('inputs/')
                target.parent.mkdir(parents=True, exist_ok=True)
                payload = (archive / name).read_bytes()
                if sha256(payload).hexdigest() != manifest['files_sha256'][name]:
                    raise ValueError('archived source changed before reconstruction: ' + name)
                target.write_bytes(payload)
        work = tree / 'build/pole-return-research'
        work.mkdir(parents=True)
        for name in ('run.py', 'run_topology.py', 'run_controls.py', 'run_guidance.py'):
            payload = (archive / 'evidence' / name).read_bytes()
            if sha256(payload).hexdigest() != manifest['files_sha256']['evidence/' + name]:
                raise ValueError('archived driver changed before reconstruction: ' + name)
            (work / name).write_bytes(payload)
        (work / 'closure_sweep.py').write_bytes(snapshot[SOURCE_NAMES[2]])
        subprocess.run([sys.executable, str(work / 'closure_sweep.py')], cwd=tree, check=True, timeout=180,
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        result = json.loads((work / 'closure-sweep.json').read_text())
    if any((Path(root) / name).read_bytes() != payload for name, payload in snapshot.items()):
        raise ValueError('optimisation sources changed during execution')
    result['source_sha256'] = {name: sha256(payload).hexdigest() for name, payload in snapshot.items()}
    validate_optimisation(result, root)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, sort_keys=True, indent=2, allow_nan=False) + '\n')
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--optimise', type=Path, help='run the fixed, bounded isolated search into a new JSON receipt')
    args = parser.parse_args()
    result = optimise(args.optimise) if args.optimise else audit()
    if args.optimise:
        print(json.dumps({k: result[k] for k in ('schema', 'executed_cases', 'joint_screen_passes', 'configuration_adopted')}))
    else:
        print(json.dumps(result, sort_keys=True, indent=2, allow_nan=False))


if __name__ == '__main__':
    main()
