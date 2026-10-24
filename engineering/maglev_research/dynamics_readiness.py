"""Audit pre-motion failures and bound curve-layout alternatives without launching.

This analysis consumes retained current-based six-car evidence. Its geometric
optimisation is only a necessary clearance screen; it cannot validate magnetic
maps, add articulated mounts, or turn an unexecuted trip into a completed one.
"""
from __future__ import annotations

import argparse
from collections import Counter
from hashlib import sha256
import gzip
import json
import math
from pathlib import Path
import re
import tomllib

ROOT = Path(__file__).resolve().parents[2]
PACKET = Path('docs/design-engine/ferrite-maglev/full-dynamics')
SCHEMA = 'osr-dynamics-readiness/1'
FLAGS = dict(design_complete=False, physical_validation=False,
             manufacturing_release=False, physical_release=False,
             eligible_for_adoption=False)
MAX_RAW = 128 * 1024 * 1024
SHA256 = re.compile(r'[0-9a-f]{64}')
PAYLOAD_FILES = {'study.json.gz', 'overview.svg', 'interface-spec.json', 'README.md',
                 *('authority/'+name for name in ('init.json', 'producer.json', 'decisions.jsonl.gz', 'receipt.json'))}


def _number(value, name, *, positive=False):
    if type(value) not in (int, float) or not math.isfinite(value) or (positive and value <= 0):
        raise ValueError('finite ' + ('positive ' if positive else '') + name + ' required')
    return float(value)


def _hash(path):
    return sha256(path.read_bytes()).hexdigest()


def _owned(root, relative):
    if not isinstance(relative, str) or Path(relative).is_absolute() or '..' in Path(relative).parts:
        raise ValueError('repository-relative evidence path required')
    path = root / relative
    if any(p.is_symlink() for p in (path, *path.parents)) or not path.is_file():
        raise ValueError('ordinary evidence file required: ' + relative)
    if path.stat().st_size > MAX_RAW:
        raise ValueError('bounded evidence file required')
    return path


def retained(root=ROOT):
    """Check payload bytes and every original source, without executing a plant.

    This checks the original publication binding, not independent validation of
    the original solver. It rejects stale/mixed/modified retained evidence.
    """
    root = Path(root).resolve()
    manifest_path = _owned(root, str(PACKET / 'manifest.json'))
    manifest = json.loads(manifest_path.read_bytes())
    if manifest.get('schema') != 'osr-continued-full-dynamics/1':
        raise ValueError('current-based full-dynamics packet required')
    if any(manifest.get(key) is not False for key in FLAGS if key != 'eligible_for_adoption'):
        raise ValueError('unaccepted retained evidence required')
    hashes = manifest.get('files_sha256', {})
    if 'study.json.gz' not in hashes or not isinstance(manifest.get('source_sha256'), dict):
        raise ValueError('retained payload and original source bindings required')
    for name, expected in hashes.items():
        path = _owned(root, str(PACKET / name))
        if _hash(path) != expected:
            raise ValueError('retained dynamics payload differs: ' + name)
    for name, expected in manifest['source_sha256'].items():
        if _hash(_owned(root, name)) != expected:
            raise ValueError('retained dynamics source differs: ' + name)
    # A self-declared subset of correct hashes must not erase a source or a
    # payload from the original publication's dependency inventory.
    from engineering.ferrite_maglev import full_dynamics
    expected_sources = {p.relative_to(full_dynamics.ROOT).as_posix() for p in full_dynamics.source_paths()}
    if set(manifest['source_sha256']) != expected_sources:
        raise ValueError('complete original dynamics source inventory required')
    if set(hashes) != PAYLOAD_FILES:
        raise ValueError('complete original dynamics payload inventory required')
    count = manifest.get('raw_bytes')
    if type(count) is not int or not 0 < count <= MAX_RAW:
        raise ValueError('bounded dynamics expansion required')
    with gzip.open(root / PACKET / 'study.json.gz', 'rb') as stream:
        raw = stream.read(count + 1)
    if len(raw) != count:
        raise ValueError('retained dynamics expansion differs')
    value = json.loads(raw)
    if value.get('source_sha256') != manifest['source_sha256']:
        raise ValueError('retained study source identity differs')
    if value.get('source_unchanged_after_execution') is not True:
        raise ValueError('unchanged execution source receipt required')
    return value, {'manifest_sha256': _hash(manifest_path),
                   'study_sha256': hashes['study.json.gz'],
                   'original_source_files_verified': len(manifest['source_sha256']),
                   'solver_rerun': False}


def audit_runs(value, assumptions):
    """Derive earned motion credit from raw counters and initial inverse attempts."""
    if value.get('schema') != 'osr-continued-full-dynamics/1':
        raise ValueError('legacy/ideal-force dynamics cannot supply current-based readiness')
    identity = value.get('configuration_sha256', '')
    if not isinstance(identity, str) or SHA256.fullmatch(identity) is None:
        raise ValueError('exact candidate identity required')
    if any(value.get(key) is not False for key in FLAGS if key != 'eligible_for_adoption'):
        raise ValueError('unaccepted dynamics evidence required')
    runs = value.get('runs')
    if not isinstance(runs, list) or not runs or value.get('simulated_cases') != len(runs):
        raise ValueError('complete executed case inventory required')
    if [run.get('case') for run in runs] != assumptions['cases']:
        raise ValueError('all exact configured six-car cases required')
    current_limit = _number(assumptions['current_limit_a'], 'drive current limit', positive=True)
    dt = _number(assumptions['mechanical_step_s'], 'mechanical step', positive=True)
    micro_dt = _number(assumptions['current_step_s'], 'current step', positive=True)
    microsteps = round(dt / micro_dt)
    if microsteps < 1 or not math.isclose(microsteps * micro_dt, dt, rel_tol=0., abs_tol=1e-12):
        raise ValueError('integer current microsteps required')
    rows = []
    for run in runs:
        if run.get('configuration_sha256') != identity:
            raise ValueError('mixed dynamics configuration')
        if any(run.get(key) is not False for key in FLAGS if key != 'eligible_for_adoption'):
            raise ValueError('run cannot confer physical acceptance')
        keys = ('executed_steps', 'executed_current_frames', 'executed_current_microsteps',
                'post_fault_steps', 'post_fault_current_frames')
        if any(type(run.get(key)) is not int or run[key] < 0 for key in keys):
            raise ValueError('nonnegative executed frame counts required')
        steps, frames, micros, post, post_current = (run[key] for key in keys)
        if not steps <= frames <= steps + 1 or micros != microsteps * frames:
            raise ValueError('mechanical/current execution counts differ')
        if post > steps or post_current > frames or post > post_current:
            raise ValueError('continued fault frames differ')
        if _number(run['executed_s'], 'mechanical execution duration') != steps * dt:
            raise ValueError('mechanical execution duration differs')
        if type(run.get('fault_injected')) is not bool:
            raise ValueError('actual fault injection state required')
        if (post or post_current or run.get('fault_tick') is not None) and (not run['fault_injected'] or run['case']['fault'] == 'none'):
            raise ValueError('unexecuted fault cannot earn post-fault motion credit')
        if any(type(passed) is not bool for passed in run['screens'].values()):
            raise ValueError('boolean dynamics screens required')
        if type(run.get('study_pass')) is not bool or run['study_pass'] != all(run['screens'].values()):
            raise ValueError('dynamics outcome and executed screens differ')
        if run['terminal_state'].startswith('hold-initial-') and any((steps, frames, micros, post, post_current)):
            raise ValueError('initial hold cannot earn mechanical/current execution credit')
        if run.get('study_pass') is True and (steps == 0 or run['terminal_state'] not in {'supported-stop', 'captured-stop'}):
            raise ValueError('initial refusal cannot become completed dynamics')
        inverse = run.get('initial_inverse')
        attempted = None
        if inverse is not None:
            currents, residuals, valid = (inverse.get(key) for key in ('current_a', 'force_residual_n', 'valid'))
            if (not isinstance(currents, list) or len(currents) != 144 or
                    not isinstance(residuals, list) or len(residuals) != 144 or
                    not isinstance(valid, list) or len(valid) != 144 or
                    any(type(v) is not bool for v in valid)):
                raise ValueError('actual six-car 144-module inverse evidence required')
            if any(not isinstance(row, list) or len(row) != 2 for row in currents + residuals):
                raise ValueError('two-axis current/force arrays required')
            peak = max(abs(_number(x, 'attempted current')) for row in currents for x in row)
            residual = max(abs(_number(x, 'attempted force residual')) for row in residuals for x in row)
            attempted = dict(peak_current_a=peak, drive_limit_a=current_limit,
                             current_limit_ratio=peak / current_limit,
                             invalid_modules=len(valid) - sum(valid),
                             peak_force_residual_n=residual,
                             admissible=all(valid) and peak <= current_limit and residual <= 50.)
            if run['screens']['initial_equilibrium'] and not attempted['admissible']:
                raise ValueError('out-of-limit inverse cannot supply valid initial equilibrium')
        elif run['screens']['initial_equilibrium']:
            raise ValueError('initial equilibrium requires current inverse evidence')
        rows.append(dict(id=run['case']['id'], terminal_state=run['terminal_state'],
                         executed_steps=steps, post_fault_steps=post,
                         executed_peak_current_a=run['maximum']['current_a'],
                         attempted_initial_inverse=attempted,
                         minimum_gap_m=run['minimum_gap_m'], maximum_gap_m=run['maximum_gap_m'],
                         unexecuted_screens=[key for key, passed in run['screens'].items() if not passed]))
    attempt = value.get('full_line_attempt', {})
    if attempt.get('configuration_sha256') != identity:
        raise ValueError('full-line attempt candidate differs')
    # A true full-trip claim needs a future verifier for actual poses, all stops,
    # dwell, charge, electrical duty and repeated service. This audit cannot issue it.
    if attempt.get('full_trip_executed') is not False or attempt.get('study_pass') is not False:
        raise ValueError('completed journey requires separate trajectory/electrical verification')
    if attempt.get('actual_rust_authority') is not True or attempt.get('actual_rust_current_plant') is not True:
        raise ValueError('real authority/current-kernel refusal evidence required')
    return dict(configuration_sha256=identity, cases=len(rows),
                terminal_counts=dict(sorted(Counter(row['terminal_state'] for row in rows).items())),
                meaningful_motion_cases=sum(row['executed_steps'] > 0 for row in rows),
                continued_post_fault_cases=sum(row['post_fault_steps'] > 0 for row in rows),
                rows=rows, full_trip_executed=False,
                full_line_terminal_state=attempt['terminal_state'],
                full_line_static_support_valid=attempt['static_support']['valid'],
                full_line_propulsion_map_accepted=attempt['map_adoption_permitted'])


def curve_fit(positions_m, radius_m, nominal_gap_m, minimum_gap_m, maximum_gap_m):
    """Exact symmetric rigid-array Chebyshev lateral recentering on a circle.

    For a symmetric array, an odd yaw term cannot reduce the worst even chord
    error. The optimal translation is midway between min/max chord offsets.
    Each guide pair must stay within both lower and upper magnetic gap limits.
    """
    positions = sorted(set(_number(x, 'module longitudinal position') for x in positions_m))
    radius = _number(radius_m, 'curve radius', positive=True)
    nominal, minimum, maximum = (_number(x, 'gap', positive=True) for x in
                                 (nominal_gap_m, minimum_gap_m, maximum_gap_m))
    if not minimum < nominal < maximum or not positions or positions != sorted(-x for x in positions):
        raise ValueError('symmetric positions and ordered physical gap envelope required')
    if max(abs(x) for x in positions) >= radius:
        raise ValueError('rigid-array extent must be smaller than radius')
    # Rationalised form avoids cancellation for large radius in threshold search.
    offsets = [x*x / (radius + math.sqrt(radius*radius - x*x)) for x in positions]
    translate = (min(offsets) + max(offsets)) / 2
    raw_error = max(offsets)
    optimum_error = (max(offsets) - min(offsets)) / 2
    allowance = min(nominal - minimum, maximum - nominal)
    return dict(radius_m=radius, lateral_gap_allowance_m=allowance,
                continuous_recentered_rigid_span_limit_m=4*math.sqrt(radius*allowance-allowance**2) if radius > allowance else 0.,
                original_maximum_mismatch_m=raw_error,
                optimal_lateral_translation_m=translate,
                optimal_maximum_mismatch_m=optimum_error,
                original_geometry_screen_pass=raw_error <= allowance,
                recentered_geometry_screen_pass=optimum_error <= allowance,
                recentered_minimum_gap_m=nominal-optimum_error,
                recentered_maximum_gap_m=nominal+optimum_error,
                hardware_revision_required=True, adopted=False)


def minimum_radius(positions_m, nominal_gap_m, minimum_gap_m, maximum_gap_m, *, recentered):
    extent = max(abs(_number(x, 'position')) for x in positions_m)
    if extent <= 0:
        raise ValueError('nonzero rigid extent required')
    lo, hi = extent * (1+1e-12), max(100., extent*2)
    field = 'recentered_geometry_screen_pass' if recentered else 'original_geometry_screen_pass'
    while not curve_fit(positions_m, hi, nominal_gap_m, minimum_gap_m, maximum_gap_m)[field]:
        hi *= 2
        if hi > 1e9:
            raise ValueError('bounded radius search exceeded')
    for _ in range(80):
        middle = (lo+hi)/2
        if curve_fit(positions_m, middle, nominal_gap_m, minimum_gap_m, maximum_gap_m)[field]:
            hi = middle
        else:
            lo = middle
    return hi


def study(root=ROOT):
    root = Path(root).resolve()
    value, provenance = retained(root)
    assumptions = tomllib.loads((root/'engineering/ferrite_maglev/full-dynamics.toml').read_text())
    audited = audit_runs(value, assumptions)
    # Existing definition supplies exact counted placements; no map or motion run.
    from engineering.ferrite_maglev import candidate_magnetics
    candidate = candidate_magnetics.definition()
    if candidate['configuration_sha256'] != audited['configuration_sha256']:
        raise ValueError('current candidate differs from retained dynamics')
    positions = [position[0] for position in candidate['module_placements_m']]
    gap = [assumptions[key] for key in ('nominal_gap_m', 'minimum_gap_m', 'maximum_gap_m')]
    curves = [curve_fit(positions, case['curve_radius_m'], *gap) for case in assumptions['cases'] if case['curve_radius_m']]
    capacity = value['runs'][0]['preferred_support_vector']['capacity_screen']
    mass = value['mass_properties']['mass_kg']
    required = mass*assumptions['gravity_m_s2']/len(candidate['module_placements_m'])
    cap = capacity['maximum_n']
    dependencies = [
        dict(id='candidate-definition', requires=[], evidence='One revised configuration digest with complete installed mass/CG/inertia, tolerances and protection equipment counted once.'),
        dict(id='maps-and-initial-equilibrium', requires=['candidate-definition'], evidence='Same-revision finite-geometry support/guidance maps over actual gaps/current/temperature with converged flux topology and within-drive current/thermal/material limits; actual 144-module inverse and static guideway equilibrium.'),
        dict(id='curve-and-contact-fit', requires=['candidate-definition'], evidence='Same-revision rigid or articulated module, capture and brake geometry fits urban/terminal curves with tolerance and load paths; count added mechanisms/mass.'),
        dict(id='propulsion-and-electrical-transients', requires=['candidate-definition', 'maps-and-initial-equilibrium'], evidence='Same-revision converged useful-field map, located group phase/R/L/flux, voltage/current limits, thermal repeated duty, receiver braking and support/reserve independence.'),
        dict(id='continued-fault-motion', requires=['maps-and-initial-equilibrium', 'curve-and-contact-fit', 'propulsion-and-electrical-transients'], evidence='Current-based six-car motion and post-injection trajectories under all named faults with nonzero frames, energy balances and verified supported/captured stop outcomes.'),
        dict(id='four-stop-electromechanical', requires=['continued-fault-motion'], evidence='Actual front/tail authority and complete poses through four stops, receiving braking, dwell, services/charging, terminal return and repeated dispatch on the same revised installed mass/maps.'),
        dict(id='physical-qualification', requires=['four-stop-electromechanical'], evidence='Calibrated rigs, actual target timing/protection, serial-specific hardware and independent G0–G5 dispositions. Numerical screening gives no release authority.'),
    ]
    return dict(schema=SCHEMA, **audited, provenance=provenance,
                support_deficit=dict(aw3_mass_kg_per_car=mass, modules_per_car=len(positions),
                    required_average_module_support_n=required, sampled_nominal_capacity_n=cap,
                    sampled_current_a=capacity['current_a'], force_shortfall_n=required-cap,
                    required_to_sampled_force_ratio=required/cap,
                    sample_covers_fraction=cap/required,
                    caveat='Sample is from an invalid material/current map, not an available physical support rating. Ratios only size the next research target.'),
                curve_optimisation=dict(cases=curves,
                    original_minimum_radius_m=minimum_radius(positions,*gap,recentered=False),
                    recentered_minimum_radius_m=minimum_radius(positions,*gap,recentered=True),
                    scope='Exact rigid-array lateral chord screen on undeformed rail only. Recentring cannot close current support or physical fit; no altered geometry is adopted.'),
                admission_requirements=dependencies, full_line_rerun_ready=False,
                next_experiment='Revise magnetic/support geometry and counted installed mass; retain actual same-revision maps and prove static equilibrium before rerunning known pre-motion holds.',
                **FLAGS)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    value = study(args.root)
    payload = json.dumps(value, sort_keys=True, indent=2, allow_nan=False)+'\n'
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload)
    else:
        print(payload, end='')


if __name__ == '__main__':
    main()
