"""Reproducible refused evidence attempts and separately identified solver benchmarks."""
from copy import deepcopy
from hashlib import sha256
import gzip
import json
import math
import os
from pathlib import Path
import platform
import shutil
import subprocess

from engineering.design_search.contracts import FLAGS, encoded, identity
from engineering.design_search.storage import atomic_immutable
from .scenario import bind_vehicle, campaign_cases, kinematic_target, scenario, validate
from .validation import gate, preflight_result
from .programme import tasks

ROOT = Path(__file__).resolve().parents[2]
SCHEMA = 'osr-trip-campaign/1'
RELEASE_FLAGS = dict(FLAGS, physical_release=False, physical_validation=False,
                     manufacturing_release=False, design_complete=False)


def digest(path):
    return sha256(Path(path).read_bytes()).hexdigest()


def source_snapshot(root, vehicle=None, magnetics=None):
    code = Path(__file__).parent
    packages = [code, code.parent/'electropermanent', code.parent/'magnetic_confirmation']
    mapping = {p.relative_to(code.parents[1]).as_posix(): digest(p) for package in packages for p in package.rglob('*')
               if p.is_file() and '__pycache__' not in p.parts and p.suffix in
               {'.py', '.json', '.toml', '.pro', '.geo', '.comm', '.mail', '.export', '.md', '.txt', '.lock', '.explicit', '.sh', '.yml'}}
    root = Path(root).resolve()
    for value in (vehicle, magnetics):
        for name, expected in ((value or {}).get('source_sha256') or (value or {}).get('source_bindings', {})).items():
            p = root/name
            if p.is_symlink() or not p.is_file() or not p.resolve().is_relative_to(root) or digest(p) != expected:
                raise ValueError('trip evidence source changed: '+name)
            if name in mapping and mapping[name] != expected:
                raise ValueError('source workspaces disagree: '+name)
            mapping[name] = expected
    for name in ('engineering/design_search/contracts.py', 'engineering/design_search/registry.py',
                 'engineering/design_search/storage.py'):
        mapping[name] = digest(root/name)
    return dict(sorted(mapping.items()))


def _masses(vehicle, loading):
    key = 'comparison_empty_kg_per_car' if loading == 'empty' else 'comparison_aw3_kg_per_car'
    value = vehicle.get(key)
    if value is None:
        raise ValueError('explicit comparison mass required; unknown equipped mass cannot become zero')
    return [float(value)]*6


def evidence_attempt(case, vehicle, magnetic):
    from .magnetic_maps import assess_magnetic_readiness
    from .vehicle import structural_readiness
    case = bind_vehicle(validate(case), vehicle['candidate_id'])
    vehicle = deepcopy(vehicle)
    mass_context = dict(basis='canonical retained allocation comparison',
                        empty_kg_per_car=vehicle['comparison_empty_kg_per_car'],
                        AW3_kg_per_car=vehicle['comparison_aw3_kg_per_car'], installed_mass_complete=False)
    if vehicle.get('comparison_aw3_mass_band_kg'):
        upper = max(vehicle['comparison_aw3_mass_band_kg'])
        vehicle['comparison_aw3_kg_per_car'] = upper
        vehicle['comparison_empty_kg_per_car'] = upper-vehicle['payload_aw3_kg_per_car']
        mass_context.update(basis='upper published provisional-installation comparison band; not a complete installed mass',
                            empty_kg_per_car=vehicle['comparison_empty_kg_per_car'], AW3_kg_per_car=upper,
                            AW3_band_kg_per_car=vehicle['comparison_aw3_mass_band_kg'])
    case['comparison_mass_context'] = mass_context
    case['scenario_id'] = identity({k:v for k,v in case.items() if k != 'scenario_id'})
    gates = []
    for prefix, rows in (('magnetic', assess_magnetic_readiness(magnetic, vehicle, case)),
                         ('structure', structural_readiness(vehicle, case))):
        for row in rows:
            row = deepcopy(row); row['id'] = prefix+'/'+row['id']; gates.append(row)
    gates += [gate('station/moving-electromechanical-map', 'unknown',
                   'No matched position/speed/phase/current/voltage and repeated-duty station map is admitted.'),
              gate('controls/closed-loop-coupling', 'unknown',
                   'The scalar Rust fixture does not establish mapped suspension or station-drive integration.'),
              gate('thermal/complete-duty', 'unknown',
                   'Suspension, drive, battery and HVAC repeated-duty parameters are not complete for this equipped candidate.'),
              gate('capture/fault-qualification', 'unknown',
                   'Capture, emergency braking and parking have separate unresolved geometry, load and qualification interfaces.')]
    if case['load_case'] == 'asymmetric':
        gates.append(gate('passengers/spatial-load', 'unknown',
                          'A passenger count alone does not specify the roll/yaw load distribution.'))
    result = preflight_result(case, vehicle['candidate_id'], gates)
    result.update(scenario=case, kinematic_target=kinematic_target(case, _masses(vehicle, case['load_case'])),
                  comparison_mass_context=mass_context,
                  target_is_candidate_performance=False,
                  requested_outputs={name: dict(value=None, status='unevaluated',
                                               reason='Dynamic execution refused before launch; no fabricated trajectory.')
                                     for name in ('speed_position_acceleration_jerk', 'six_component_module_wrenches',
                                                  'module_gaps', 'body_deflection_modes_stresses',
                                                  'drive_current_voltage_energy', 'support_current_heat',
                                                  'battery_HVAC_auxiliaries', 'receiving_recovery_dissipation',
                                                  'passenger_comfort', 'fault_capture_response')})
    return result


def review_options(vehicles, magnetic):
    rows = []
    for vehicle in [vehicles['canonical'], *vehicles['alternatives']]:
        for temperature in (20., 40., 50., 80.):
            for loading in ('empty', 'AW3'):
                case = scenario(f"explore-{vehicle['candidate_id'][:12]}-{loading}-{temperature:g}C",
                                2000, loading, temperature_C=temperature, mode='exploration')
                rows.append(evidence_attempt(case, vehicle, magnetic))
    return dict(schema='osr-trip-source-option-review/1', comparisons=rows,
                purpose='Source-bound necessary/readiness review; no hypothetical forces or integrated optimisation pass',
                integrated_candidate_selected=None, installed_cost=None, complete_installed_mass=None,
                source_next_experiment_ids=[v['candidate_id'] for v in vehicles['alternatives'] if v.get('next_experiment_only')],
                selection_policy_changed=False, physical_accepted=False)


def _write(path, value):
    atomic_immutable(path, encoded(value))


def _benchmark_specifications(canonical):
    rows = []
    for distance in (1500, 2000):
        for loading in ('empty', 'AW3'):
            rows.append(('', scenario(f'benchmark-{distance}-{loading}', distance, loading,
                                       mode='benchmark', vehicle_id=canonical['candidate_id'])))
    rows.append(('refinement', scenario('benchmark-2000-AW3', 2000, 'AW3', mode='benchmark',
                                        mechanical_step_s=.0005, vehicle_id=canonical['candidate_id'])))
    return rows


def _benchmark(python, case, masses, output, code_root, solver_id):
    job = dict(scenario=case, masses_kg=masses, mechanical_step_s=case['mechanical_step_s'], expected_solver_id=solver_id)
    job['job_id'] = identity(job)
    input_path = output/(case['case_id']+'-input.json')
    result_path = output/(case['case_id']+'-result.json')
    _write(input_path, job)
    command = [str(python), '-m', 'engineering.trip_dynamics', 'benchmark-worker',
               '--input', str(input_path), '--output', str(result_path)]
    env = dict(os.environ, PYTHONPATH=str(code_root), OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1')
    completed = subprocess.run(command, cwd=code_root, env=env, capture_output=True, timeout=300)
    atomic_immutable(output/(case['case_id']+'-stdout.txt'), completed.stdout)
    atomic_immutable(output/(case['case_id']+'-stderr.txt'), completed.stderr)
    if completed.returncode:
        raise ValueError('Chrono benchmark failed: '+case['case_id']+' '+completed.stderr.decode(errors='replace')[-2000:])
    value = json.loads(result_path.read_bytes())
    if value.get('input_job_id') != job['job_id']:
        raise ValueError('Chrono worker returned a different input identity')
    return value


def run(output, *, root=ROOT, chrono_python=None, run_rust=True, getdp=None, finite_coupon_archive=None):
    from .vehicle import current_vehicle_definitions
    from .magnetic_maps import current_magnetic_evidence
    root, output = Path(root).resolve(), Path(output).resolve()
    if output.exists():
        raise ValueError('a fresh campaign directory is required; retained executions are immutable')
    vehicles, magnetic = current_vehicle_definitions(root), current_magnetic_evidence(root)
    before = source_snapshot(root, vehicles, magnetic)
    backend = None
    if chrono_python is not None:
        probe = subprocess.run([str(chrono_python), '-m', 'engineering.trip_dynamics', 'probe'], cwd=ROOT,
                               env=dict(os.environ, PYTHONPATH=str(ROOT), OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1'),
                               capture_output=True, text=True, timeout=30)
        if probe.returncode:
            raise ValueError('Chrono environment probe failed: '+probe.stderr[-2000:])
        backend = json.loads(probe.stdout)
        if backend.get('available') is not True or backend.get('fallback') is not False:
            raise ValueError('a real isolated Chrono backend is required')
    archive_record = None
    if finite_coupon_archive is not None:
        from .archive import verify_magnetic_archive
        archive_record = verify_magnetic_archive(finite_coupon_archive, root=root)
    canonical = vehicles['canonical']
    cases = [bind_vehicle(c, canonical['candidate_id']) for c in campaign_cases()]
    attempts = [evidence_attempt(case, canonical, magnetic) for case in cases]
    cases = [a['scenario'] for a in attempts]
    import numpy, scipy, matplotlib
    specification = dict(schema=SCHEMA, scenarios=cases, vehicle_id=canonical['candidate_id'],
                         source_sha256=before, runtime={'python': platform.python_version()},
                         numerical_versions=dict(numpy=numpy.__version__, scipy=scipy.__version__, matplotlib=matplotlib.__version__),
                         chrono_backend=backend,
                         chrono_requested=chrono_python is not None, magnetic_method_fixture_requested=getdp is not None,
                         finite_coupon_archive_sha256=None if archive_record is None else archive_record['archive_sha256'],
                         **RELEASE_FLAGS)
    specification['campaign_id'] = identity(specification)
    output.mkdir(parents=True)
    _write(output/'input.json', specification)
    _write(output/'vehicles.json', vehicles); _write(output/'magnetic-evidence.json', magnetic)
    _write(output/'evidence-attempts.json', attempts)
    options = review_options(vehicles, magnetic)
    _write(output/'option-review.json', options)
    _write(output/'digital-programme.json', tasks())
    if archive_record is not None:
        atomic_immutable(output/'finite-coupon-artifacts.tar.gz', Path(finite_coupon_archive).read_bytes())
        _write(output/'finite-coupon-verification.json', archive_record)
    from .flexible_body import laminate_benchmark
    _write(output/'laminate-method-fixture.json', laminate_benchmark())
    if getdp is not None:
        from .fixtures.magnetics.run_fixture import run as magnetic_fixture
        magnetic_fixture(output/'magnetic-method-fixture', getdp)
    controls = dict(execution='not-run', reason='explicitly disabled; no current-control claim')
    if run_rust:
        from .onboard_control import build_current_kernel, current_fixture
        binary, build = build_current_kernel(root)
        controls = dict(build=build, result=current_fixture(binary))
    _write(output/'rust-current-fixture.json', controls)
    benchmarks = []
    if chrono_python is not None:
        directory = output/'chrono'; directory.mkdir()
        refinement = directory/'refinement'; refinement.mkdir()
        for subfolder, case in _benchmark_specifications(canonical):
            benchmarks.append(_benchmark(chrono_python, case, _masses(canonical, case['load_case']), directory/subfolder, ROOT, backend['solver_id']))
        from .chrono_runner import compare_timesteps
        _write(output/'timestep-comparison.json', compare_timesteps(benchmarks[-2], benchmarks[-1]))
        plot_benchmarks(output/'benchmark-traces.png', benchmarks)
    if source_snapshot(root, vehicles, magnetic) != before:
        raise ValueError('trip sources changed during campaign; keep interrupted directory and start a new execution')
    summary = dict(schema=SCHEMA, campaign_id=specification['campaign_id'], source_sha256=before,
                   canonical_candidate_id=canonical['candidate_id'], evidence_attempts=len(attempts),
                   completed_evidence_preflights=len(attempts),
                   integrated_journeys_executed=0, integrated_journeys_passed=0,
                   evidence_states={s: sum(a['engineering_screen'] == s for a in attempts) for s in ('pass', 'fail', 'unknown')},
                   chrono_benchmarks_executed=len(benchmarks),
                   chrono_benchmark_terminal_screens_passed=sum(b['summary']['terminal_screen_pass'] for b in benchmarks),
                   benchmark_is_design_evidence=False,
                   complete_equipped_vehicle=False, full_route_qualification=False,
                   all_requested_criteria_evaluated=False, **RELEASE_FLAGS)
    summary['source_option_preflights'] = len(options['comparisons'])
    summary['finite_nonlinear_coupon_attempts'] = 0 if archive_record is None else len(archive_record['finite_candidate']['attempts'])
    summary['finite_nonlinear_coupon_force_credit'] = False
    _write(output/'summary.json', summary)
    atomic_immutable(output/'README.md', readme(summary, attempts, benchmarks).encode())
    files = {p.relative_to(output).as_posix(): digest(p) for p in output.rglob('*') if p.is_file()}
    _write(output/'manifest.json', dict(schema='osr-trip-publication/1', campaign_id=summary['campaign_id'],
                                      source_sha256=before, files_sha256=files, **RELEASE_FLAGS))
    return summary


def verify(output, *, root=ROOT):
    from .vehicle import current_vehicle_definitions
    from .magnetic_maps import current_magnetic_evidence
    output = Path(output).resolve(); root = Path(root).resolve()
    if output.is_symlink() or any(p.is_symlink() for p in output.rglob('*')):
        raise ValueError('ordinary retained trip publication required')
    manifest = json.loads((output/'manifest.json').read_bytes())
    if manifest.get('schema') != 'osr-trip-publication/1' or any(manifest.get(k) is not False for k in RELEASE_FLAGS):
        raise ValueError('research trip receipt cannot assert acceptance')
    actual = {p.relative_to(output).as_posix() for p in output.rglob('*') if p.is_file()}
    if actual != set(manifest['files_sha256']) | {'manifest.json'}:
        raise ValueError('trip output inventory differs')
    for name, expected in manifest['files_sha256'].items():
        path = output/name
        if not path.resolve().is_relative_to(output) or digest(path) != expected:
            raise ValueError('trip output differs: '+name)
    vehicles, magnetic = current_vehicle_definitions(root), current_magnetic_evidence(root)
    if manifest['source_sha256'] != source_snapshot(root, vehicles, magnetic):
        raise ValueError('trip implementation or retained input changed')
    attempts = json.loads((output/'evidence-attempts.json').read_bytes())
    if attempts != [evidence_attempt(c, vehicles['canonical'], magnetic) for c in campaign_cases()]:
        raise ValueError('trip preflight no longer agrees with source-bound evidence')
    specification = json.loads((output/'input.json').read_bytes())
    if specification.get('campaign_id') != identity({k:v for k,v in specification.items() if k != 'campaign_id'}):
        raise ValueError('trip input identity differs')
    if (specification.get('campaign_id') != manifest['campaign_id']
            or specification.get('source_sha256') != manifest['source_sha256']
            or specification.get('vehicle_id') != vehicles['canonical']['candidate_id']
            or specification.get('scenarios') != [a['scenario'] for a in attempts]):
        raise ValueError('trip input and evidence contexts differ')
    if json.loads((output/'vehicles.json').read_bytes()) != vehicles or json.loads((output/'magnetic-evidence.json').read_bytes()) != magnetic:
        raise ValueError('trip retained component reports differ from their sources')
    if json.loads((output/'digital-programme.json').read_bytes()) != tasks():
        raise ValueError('trip digital task contracts differ')
    if json.loads((output/'option-review.json').read_bytes()) != review_options(vehicles, magnetic):
        raise ValueError('trip option review differs from matched source candidates')
    benchmarks = []
    if specification['chrono_requested']:
        for subfolder, case in _benchmark_specifications(vehicles['canonical']):
            folder = output/'chrono'/subfolder
            job = json.loads((folder/(case['case_id']+'-input.json')).read_bytes())
            expected = dict(scenario=case, masses_kg=_masses(vehicles['canonical'], case['load_case']), mechanical_step_s=case['mechanical_step_s'], expected_solver_id=specification['chrono_backend']['solver_id'])
            expected['job_id'] = identity(expected)
            if job != expected:
                raise ValueError('benchmark input differs from the declared comparison')
            value = json.loads((folder/(case['case_id']+'-result.json')).read_bytes())
            verify_benchmark(value, job)
            if value['backend'] != specification['chrono_backend']:
                raise ValueError('Chrono backend changed within the campaign')
            benchmarks.append(value)
        from .chrono_runner import compare_timesteps
        if json.loads((output/'timestep-comparison.json').read_bytes()) != compare_timesteps(benchmarks[-2], benchmarks[-1]):
            raise ValueError('benchmark timestep comparison differs')
    summary = json.loads((output/'summary.json').read_bytes())
    if (output/'finite-coupon-artifacts.tar.gz').is_file():
        from .archive import verify_magnetic_archive
        if json.loads((output/'finite-coupon-verification.json').read_bytes()) != verify_magnetic_archive(output/'finite-coupon-artifacts.tar.gz', root=root):
            raise ValueError('finite coupon archive verification changed')
    if summary['campaign_id'] != manifest['campaign_id'] or summary['integrated_journeys_executed'] != 0:
        raise ValueError('trip summary changed its execution scope')
    counts = dict(evidence_attempts=len(attempts), completed_evidence_preflights=len(attempts),
                  integrated_journeys_executed=0, integrated_journeys_passed=0,
                  evidence_states={s:sum(a['engineering_screen']==s for a in attempts) for s in ('pass','fail','unknown')},
                  chrono_benchmarks_executed=len(benchmarks),
                  chrono_benchmark_terminal_screens_passed=sum(b['summary']['terminal_screen_pass'] for b in benchmarks),
                  source_option_preflights=len(review_options(vehicles, magnetic)['comparisons']),
                  benchmark_is_design_evidence=False, complete_equipped_vehicle=False,
                  full_route_qualification=False, all_requested_criteria_evaluated=False,
                  finite_nonlinear_coupon_force_credit=False)
    if any(summary.get(k) != v for k,v in counts.items()) or any(summary.get(k) is not False for k in RELEASE_FLAGS):
        raise ValueError('trip summary contradicts actual execution dispositions')
    if (output/'README.md').read_text() != readme(summary, attempts, benchmarks):
        raise ValueError('trip introduction no longer agrees with the retained results')
    return manifest


def verify_benchmark(value, job):
    """Check scope, input identity and terminal/energy summaries without a solver."""
    from . import chrono_runner, formation
    if value.get('schema') != 'osr-chrono-trip-benchmark/1' or value.get('input_job_id') != job['job_id']:
        raise ValueError('benchmark result belongs to another request')
    if any(value.get(k) is not False for k in ('physical_accepted','journey_accepted','engineering_qualified')):
        raise ValueError('ideal mechanics cannot become engineering acceptance')
    case = job['scenario']; dt = job['mechanical_step_s']
    scenario_input = chrono_runner._scenario(case, dt)
    definition = formation.definition(job['masses_kg'])
    inputs = value['inputs']
    if (inputs['scenario'] != scenario_input or inputs['scenario_id'] != case['scenario_id']
            or inputs['source_vehicle_id'] != case['vehicle_id'] or inputs['vehicle'] != definition
            or inputs['vehicle_id'] != definition['vehicle_id'] or value['dt_s'] != dt):
        raise ValueError('benchmark scenario, mass or formation binding differs')
    backend = value['backend']
    if backend.get('available') is not True or backend.get('fallback') is not False or backend['solver_id'] != identity({k:v for k,v in backend.items() if k!='solver_id'}):
        raise ValueError('benchmark lacks a coherent real solver identity')
    if inputs['solver_id'] != backend['solver_id'] or backend['solver_id'] != job['expected_solver_id']:
        raise ValueError('benchmark backend and input identities disagree')
    for name, expected in inputs['source_sha256'].items():
        if Path(name).name != name or digest(Path(__file__).parent/name) != expected:
            raise ValueError('benchmark component source differs')
    if value['evaluation_id'] != identity(dict(inputs=inputs, dt_s=dt, zones=value['zones'])):
        raise ValueError('benchmark evaluation identity differs')
    states = value['final_state']; trace = value['trace']; reported = value['summary']
    if len(states) != 6 or not trace or len(trace[-1]['cars']) != 6:
        raise ValueError('six-car terminal record required')
    if trace[-1]['time_s'] != reported['elapsed_simulation_s']:
        raise ValueError('benchmark terminal time differs')
    initial = [-i*(definition['body_length_m']+definition['coupling_gap_m']) for i in range(6)]
    position_error = max(abs(s['position_m'][0]-x-case['distance_m']) for s,x in zip(states,initial))
    speed_error = max(abs(s['velocity_m_s'][0]) for s in states)
    kinetic = sum(.5*m*sum(v*v for v in s['velocity_m_s']) for m,s in zip(job['masses_kg'],states))
    spring = sum(.5*definition['coupler_stiffness_N_per_m']*q['extension_m']**2 for q in trace[-1]['couplers'])
    for key, actual in [('terminal_max_distance_error_m',position_error), ('terminal_max_speed_m_s',speed_error),
                        ('final_kinetic_energy_J',kinetic), ('final_coupler_spring_energy_J',spring)]:
        if not math.isclose(reported[key], actual, rel_tol=1e-8, abs_tol=1e-9):
            raise ValueError('benchmark summary differs from terminal states: '+key)
    residual = kinetic+spring-reported['external_work_J']+reported['damper_heat_J']
    if not math.isclose(reported['work_energy_residual_J'], residual, rel_tol=1e-8, abs_tol=1e-8):
        raise ValueError('benchmark work/energy residual differs')
    terminal = value['state']=='completed' and position_error<=.2 and speed_error<=.05
    if reported['terminal_screen_pass'] != terminal or reported['terminal_distance_tolerance_m'] != .2 or reported['terminal_speed_tolerance_m_s'] != .05:
        raise ValueError('benchmark terminal disposition differs')
    return value


def plot_benchmarks(path, benchmarks):
    """Plot actual downsampled Chrono records, never an invented failed journey."""
    import matplotlib
    matplotlib.use('Agg')
    from matplotlib import pyplot as plt
    fig, axes = plt.subplots(2, 1, figsize=(10, 7), sharex=True, constrained_layout=True)
    for value in benchmarks:
        if value['dt_s'] < .001:
            continue
        rows = value['trace']; label = value['inputs']['scenario']['case_id'].removeprefix('benchmark-')
        axes[0].plot([r['time_s'] for r in rows], [r['cars'][0]['velocity_m_s'][0] for r in rows], label=label)
        axes[1].plot([r['time_s'] for r in rows], [r['cars'][0]['translation_m'] for r in rows], label=label)
    axes[0].set_ylabel('Lead-car speed (m/s)'); axes[1].set_ylabel('Lead-car translation (m)')
    axes[1].set_xlabel('Simulated time (s)')
    for axis in axes:
        axis.grid(alpha=.25); axis.legend(fontsize=8)
    fig.suptitle('Executed Chrono method benchmarks\nIdeal support and prescribed force; not current train performance', fontsize=12)
    fig.savefig(path, dpi=150)
    plt.close(fig)


def readme(summary, attempts, benchmarks):
    rows = '\n'.join('| '+a['case_id']+' | '+a['engineering_screen']+' | '+a['dynamic_execution']+' |'
                     for a in attempts)
    numerical = '\n'.join('| '+b['inputs']['scenario']['case_id']+' | '+str(b['dt_s']*1000)+' | '+
                          f"{b['summary']['terminal_max_distance_error_m']:.6g}"+' | '+
                          f"{b['summary']['relative_work_energy_residual']:.3g}"+' |'
                          for b in benchmarks)
    benchmark_display = 'Chrono benchmarks were not requested in this execution; no benchmark trajectory is supplied.'
    if benchmarks:
        benchmark_display = f'''| Numerical case | Step, ms | Maximum terminal position error, m | Work residual / absolute external work |
|---|---:|---:|---:|
{numerical}

![Actual sampled benchmark traces, with ideal support and prescribed force](benchmark-traces.png)

The trace is sampled at 10 Hz; native integration, work/impulse accounting and extrema run at every mechanical step. The [smaller-step comparison](timestep-comparison.json) checks the full sampled path and coupler peaks as well as arrival. Two step sizes do not prove continuum convergence.'''
    finite_display = ''
    if summary['finite_nonlinear_coupon_attempts']:
        finite_display = '''
## Actual nonlinear 3D neodymium coupon

Three bounded attempts used the source-bound finite N35UH Halbach coupon at 80°C, 12 mm and zero coil current. Newton diverged, a fine-mesh run timed out, and a Picard repair stalled. **No force or usable map credit is given.** The independent manufactured 3D method fixture passed its analytical air-Maxwell check; that success does not validate the candidate coupon.

[Verified artifact inventory and dispositions](finite-coupon-verification.json) · [Exact input/mesh/log archive](finite-coupon-artifacts.tar.gz). Historical limitations include uncaptured stdout for the timed-out attempt and an unrecovered Python recipe for an earlier pre-solve syntax failure; their exact solver inputs remain identified. The later replay recipe does not relabel those executions.
'''
    return f'''# Six-car journey simulation programme

OpenSourceRail aims for simple construction, low whole-life cost and high passenger throughput. All permanent magnets and support/guidance coils remain onboard; ordinary concrete beams carry passive steel facings. Stations provide launch and receiving propulsion. GFRP and aluminium-extrusion body alternatives remain separate identified designs.

**Result: {len(attempts)} completed evidence preflights; no integrated journey admitted.** The equipped mass distribution, flexible body and nonlinear 3D force/current/loss maps are not complete for one common candidate. These attempts therefore produce no fabricated travel, stable hover or post-fault capture trajectory.

{len(benchmarks)} separately identified Chrono benchmarks exercise six bodies and finite station zones with ideal straight support and prescribed forces. They are numerical method demonstrations; the actual train has not acquired their force, power or stability capability.

[Summary](summary.json) · [All case gates and unevaluated outputs](evidence-attempts.json) · [Source-bound option review](option-review.json) · [Vehicle inventories](vehicles.json) · [Magnetic evidence](magnetic-evidence.json) · [Digital task contracts](digital-programme.json) · [Integrity receipt](manifest.json) · [Method and commands](../../../engineering/trip_dynamics/README.md)

| Case | Engineering preflight | Dynamic execution |
|---|---|---|
{rows}

## Separately executed Chrono benchmarks

{benchmark_display}

{finite_display}

The source option review executes {summary['source_option_preflights']} additional preflights across the canonical, retained-GFRP/neodymium and aluminium variants at 20/40/50/80°C, with empty and AW3 comparison loads. Their own mass ledgers and operating points stay distinct. It selects no integrated candidate and does not turn unknown installed mass or cost into zero.

The independent ideal target at 20 m/s and 0.8 m/s² is 100 s for 1.5 km and 125 s for 2 km, with 250 m acceleration and braking distances. It excludes drag, grades, jerk, auxiliaries and electrical limits. A 350 m zone length alone does not prove full-formation magnetic overlap. Comparison masses are retained allocations/material ledgers, not newly completed equipped vehicle masses.

The Rust current fixture executes the existing 50 µs controller/plant ABI and sensor-loss refusal; it is not a magnetic force model. The composite coupon is an analytical/finite-element method check, not an accepted body. Code_Aster and complete nonlinear candidate maps have their own explicit execution and applicability dispositions.

Every unexecuted field in the report is marked unevaluated. The task graph adds digital execution contracts while leaving physical qualification unchanged. Campaign `{summary['campaign_id']}`; engineering acceptance, configuration adoption and physical release remain false.
'''
