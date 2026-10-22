"""Ignored, reproducible rigid-car sensitivity; no accepted plant replacement."""
from concurrent.futures import ProcessPoolExecutor
from hashlib import sha256
from pathlib import Path
import gzip
import json
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from engineering.ferrite_maglev import assembled_body, moving_train, model, body_stiffness

OUTPUT = Path(__file__).resolve().parent


def encoded(value):
    return (json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + '\n').encode()


def digest(value):
    return sha256(value).hexdigest()


def source_snapshot():
    values = dict(moving_train.sources())
    values.update(assembled_body.sources())
    values.update(body_stiffness.sources())
    values[Path(__file__).relative_to(ROOT).as_posix()] = digest(Path(__file__).read_bytes())
    return values


def execute(args):
    name, executable, candidate = args
    started = time.monotonic()
    result = body_stiffness.run_with_witness(Path(executable), candidate)
    body_stiffness.validate_trace_and_energy(result, candidate)
    raw = gzip.compress(encoded(result), mtime=0)
    name = name + '.json.gz'
    (OUTPUT / name).write_bytes(raw)
    return dict(file=name, sha256=digest(raw), elapsed_wall_s=time.monotonic()-started,
                candidate_sha256=result['candidate_sha256'], assumptions=result['assumptions'],
                metrics={k: v for k, v in result.items() if k not in body_stiffness.METRIC_EXCLUDE},
                confirmation_eligible=moving_train.confirmation_eligible(result),
                retained_trace_rows=len(result['trace']))


def main():
    before = source_snapshot()
    retained_file = moving_train.OUTPUT / 'result.json.gz'
    retained_bytes = retained_file.read_bytes()
    retained = json.loads(gzip.decompress(retained_bytes))['moving_run']
    baseline = retained['assumptions']
    if baseline != moving_train.candidate_assumptions(moving_train.load())[0]:
        raise ValueError('retained candidate differs from current exact selected nominal')
    if retained['candidate_sha256'] != digest(moving_train.encoded(baseline)):
        raise ValueError('retained candidate identity is inconsistent')
    # The complete AW3 mass is retained. Partial CAD stock is never substituted.
    if baseline['car_mass_kg'] != 26200.0 or baseline['cars'] != 6:
        raise ValueError('expected exact current six-car 26200 kg AW3 benchmark')
    try:
        moving_train.read_selected()
        retained_publication_verified = True
        retained_publication_error = None
    except ValueError as exc:
        retained_publication_verified = False
        retained_publication_error = str(exc)
    axial = assembled_body.axial_screen()
    candidates = [('reference-100MN', baseline)]
    for name, field in (
        ('gross-series', 'body_and_coupler_series_stiffness_n_m'),
        ('drilled-series', 'drilled_body_and_coupler_series_stiffness_n_m'),
    ):
        candidate = dict(baseline, coupler_stiffness_n_m=axial[field])
        differences = {k for k in candidate if candidate[k] != baseline[k]}
        if differences != {'coupler_stiffness_n_m'}:
            raise ValueError('sensitivity changed an unrelated assumption')
        candidates.append((name, candidate))
    executable, build = moving_train.build_bridge()
    if digest(executable.read_bytes()) != build['binary_sha256']:
        raise ValueError('compiled bridge changed before execution')
    with ProcessPoolExecutor(max_workers=2) as pool:
        runs = list(pool.map(execute, [(name, str(executable), a) for name, a in candidates]))
    after = source_snapshot()
    if before != after or digest(executable.read_bytes()) != build['binary_sha256']:
        raise ValueError('sources/binary changed while sensitivity executed')
    reference = runs[0]['metrics']
    comparison_keys = ('minimum_gap_m', 'maximum_gap_m', 'peak_coupler_force_n',
        'peak_coupler_extension_m', 'maximum_magnetic_phase_spread_degrees',
        'maximum_longitudinal_relative_spread_m', 'peak_module_force_n',
        'peak_beam_displacement_m', 'completed_moving_steps', 'planned_moving_steps')
    summary = dict(schema='osr-rigid-car-body-axial-sensitivity/1', source_sha256=before,
        source_unchanged_after_execution=True, build=build, axial_screen=axial,
        full_aw3_car_mass_kg=baseline['car_mass_kg'], full_train_mass_kg=6*baseline['car_mass_kg'],
        retained_selected_candidate_sha256=retained['candidate_sha256'],
        retained_result_file=retained_file.relative_to(ROOT).as_posix(),
        retained_result_sha256=digest(retained_bytes),
        retained_publication_verified=retained_publication_verified,
        retained_publication_error=retained_publication_error,
        retained_candidate_exact_current=True,
        runs=runs,
        comparisons=[dict(name=run['file'], stiffness_n_m=run['assumptions']['coupler_stiffness_n_m'],
            metrics={key:run['metrics'][key] for key in comparison_keys},
            delta_from_fresh_reference={key:run['metrics'][key]-reference[key] for key in comparison_keys},
            original_nominal_screen_pass=run['metrics']['study_pass'],
            confirmation_screen_pass=run['confirmation_eligible']) for run in runs],
        fresh_reference_difference_from_retained={key:reference[key]-retained[key] for key in comparison_keys},
        only_changed_assumption='coupler_stiffness_n_m',
        accepted_body_or_plant=False, city_default_changed=False, physical_output_authorised=False,
        scope='Fresh 88s prescribed 1km station trajectory on six rigid cars and repeated linear pinned spans with actual Rust vertical controllers; only lumped longitudinal series stiffness is changed. Full retained AW3 26200kg/car is used. This is not a distributed flexible-body model, joined-body verification, shared-field thrust/phase confirmation, measured material test, hardware acceptance or city default.',
        **model.FLAGS)
    (OUTPUT/'summary.json').write_bytes(encoded(summary))
    files = [run['file'] for run in runs] + ['summary.json', 'run.py']
    receipt = dict(schema='osr-body-axial-sensitivity-receipt/1',source_sha256=before,
        files_sha256={name:digest((OUTPUT/name).read_bytes()) for name in files},
        command='OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 tools/automation/osr-python build/body-axial-sensitivity/run.py',
        accepted_body_or_plant=False, city_default_changed=False, **model.FLAGS)
    (OUTPUT/'receipt.json').write_bytes(encoded(receipt))
    print(json.dumps(dict(comparisons=summary['comparisons'], source_files=len(before),
        retained_publication_verified=retained_publication_verified,
        fresh_reference_difference_from_retained=summary['fresh_reference_difference_from_retained'],
        receipt=str(OUTPUT/'receipt.json')),sort_keys=True),flush=True)


if __name__ == '__main__':
    main()
