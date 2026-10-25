"""Bounded selected experiments shared by the CLI and local job service.

Requests contain JSON values, never client-selected commands or filesystem
paths. The caller owns ``root`` and ``output``. Evidence refuses before motion;
benchmarks use the genuine private Chrono backend with explicit ideal support.
"""
from copy import deepcopy
from hashlib import sha256
import json
import math
import os
from pathlib import Path
import subprocess

from engineering.design_search.contracts import encoded, identity
from engineering.design_search.storage import atomic_immutable

ROOT = Path(__file__).resolve().parents[2]
FLAGS = dict(configuration_adopted=False, engineering_accepted=False,
             physical_accepted=False, journey_accepted=False,
             complete_equipped_vehicle=False, physical_release=False)
ACTIONS = {'experiment', 'campaign', 'fixture', 'verify', 'probe', 'setup-tools',
           'validate-map', 'validate-modal'}
CHOICES = dict(mode=['evidence', 'benchmark'], distance_m=[1500, 2000],
               load_case=['empty', 'AW3'], temperature_C=[20, 50],
               mechanical_step_s=[.001, .0005])


def _write(path, value):
    atomic_immutable(Path(path), encoded(value))


def _json(path):
    path = Path(path)
    if path.is_symlink() or not path.is_file() or path.stat().st_size > 32*1024*1024:
        raise ValueError('bounded ordinary retained JSON required')
    return json.loads(path.read_bytes())


def _definitions(root):
    from .vehicle import current_vehicle_definitions
    return current_vehicle_definitions(Path(root))


def _vehicle(definitions, identifier=None):
    rows = [definitions['canonical'], *definitions['alternatives']]
    identifier = definitions['canonical']['candidate_id'] if identifier is None else identifier
    matches = [x for x in rows if x['candidate_id'] == identifier]
    if len(matches) != 1:
        raise ValueError('vehicle_id must select exactly one source-bound catalogue vehicle')
    return deepcopy(matches[0])


def comparison(vehicle):
    """Use each variant's own upper installation scenario, never canonical tare."""
    band = vehicle.get('comparison_aw3_mass_band_kg')
    aw3 = max(band) if band else vehicle['comparison_aw3_kg_per_car']
    empty = aw3 - vehicle['payload_aw3_kg_per_car'] if band else vehicle['comparison_empty_kg_per_car']
    return dict(empty_kg_per_car=empty, AW3_kg_per_car=aw3,
        AW3_band_kg_per_car=band,
        basis='upper published provisional-installation comparison band' if band else 'canonical retained allocation comparison',
        installed_mass_complete=False, installed_empty_kg_per_car=None,
        cg_m=None, inertia_kg_m2=None)


def catalogue(root=ROOT):
    from .magnetic_maps import current_magnetic_evidence
    from .vehicle import _checked
    definitions = _definitions(root)
    magnetic = current_magnetic_evidence(Path(root))
    bindings=dict(definitions['source_bindings'])
    for name,digest in magnetic['source_sha256'].items():
        if name in bindings and bindings[name]!=digest:
            raise ValueError('catalogue source bindings disagree: '+name)
        bindings[name]=digest
    publication='docs/design-engine/vehicle-optimisation/'
    manifest=json.loads(_checked(root,publication+'manifest.json',bindings[publication+'manifest.json']))
    products={}
    for name in ('equipment.json','HVAC.json'):
        digest=manifest['files_sha256'][name]
        products[name]=json.loads(_checked(root,publication+name,digest))
        bindings[publication+name]=digest
    rows = []
    for v in [definitions['canonical'], *definitions['alternatives']]:
        records = [x for x in magnetic['records'] if x['candidate_id'] == v['candidate_id']]
        rows.append(dict(vehicle_id=v['candidate_id'], candidate_id=v['candidate_id'],
            label=v['label'], body_family=v['body_family'], magnetic_family=v['magnetic_family'],
            geometry_id=v['geometry_id'], material_id=v['material_id'],
            comparison_mass_context=comparison(v),
            comparison_aw3_mass_band_kg=v.get('comparison_aw3_mass_band_kg'),
            comparison_empty_kg_per_car=comparison(v)['empty_kg_per_car'],
            comparison_aw3_kg_per_car=comparison(v)['AW3_kg_per_car'],
            installed_empty_kg_per_car=None, cg_m=None, inertia_kg_m2=None,
            modules_per_car=v['modules_per_car'], cars=v['cars'], car_length_m=v['car_length_m'],
            unknown_installed_inventory=v['unknown_installed_inventory'],
            magnetic_record_available=len(records)==1,
            magnetic_map_available=bool(records and records[0].get('force_map')),
            **FLAGS))
    return dict(schema='osr-trip-interactive-catalogue/1', vehicles=rows,
        canonical_vehicle_id=definitions['canonical']['candidate_id'], choices=deepcopy(CHOICES),
        fixed_targets=dict(max_speed_m_s=20., acceleration_m_s2=.8, powered_zone_m=350.,
                           target_is_candidate_performance=False),
        fixtures=['current', 'laminate', 'nonlinear-magnetics'],
        magnets=magnetic['records'], equipment=products['equipment.json'], HVAC=products['HVAC.json'],
        source_sha256=bindings,
        model_upload_scope='Inline numerical/schema checks only; uploaded source paths are never read',
        requested_gfrp_optimisation=definitions['requested_gfrp_optimisation'], **FLAGS)


def status(root=ROOT):
    root = Path(root)
    cat = catalogue(root)
    folder = root/'docs/design-engine/trip-dynamics'
    publication = dict(present=False, integrity='not-verified')
    if (folder/'manifest.json').is_file():
        manifest, summary = _json(folder/'manifest.json'), _json(folder/'summary.json')
        if sha256((folder/'summary.json').read_bytes()).hexdigest() != manifest['files_sha256'].get('summary.json'):
            raise ValueError('published summary digest differs')
        publication = dict(present=True, integrity='summary-hash-checked; run verify for complete source/output verification',
                           campaign_id=summary['campaign_id'], summary=summary)
        publication['summary'].pop('source_sha256', None)
    return dict(schema='osr-trip-interactive-status/1', publication=publication,
        canonical_vehicle_id=cat['canonical_vehicle_id'], known_vehicle_count=len(cat['vehicles']),
        available_actions=sorted(ACTIONS), evidence_behavior='Completed preflight; motion refused when required evidence is missing',
        benchmark_behavior='Real private Chrono numerical method with ideal support and prescribed force; never candidate travel',
        tools=dict(chrono=dict(environment_present=(root/'build/trip-dynamics/environment/chrono/bin/python').is_file(),probed=False),
                   getdp=dict(executable_present=(root/'build/trip-dynamics/tools/getdp-3.5.0-Linux64/bin/getdp').is_file(),probed=False)), **FLAGS)


def cases():
    from .scenario import campaign_cases
    return dict(schema='osr-trip-case-catalogue/1', cases=campaign_cases(), choices=deepcopy(CHOICES), **FLAGS)


def _validate_request(request):
    if not isinstance(request, dict) or set(request) != {'action', 'parameters'}:
        raise ValueError('exact action/parameters request required')
    # This also rejects NaN/Infinity and non-JSON objects before any side effect.
    if len(encoded(request)) > 4*1024*1024:
        raise ValueError('request exceeds four MiB')
    action, params = request['action'], request['parameters']
    if not isinstance(action, str) or action not in ACTIONS or not isinstance(params, dict):
        raise ValueError('known action and parameters object required')
    allowed = {'experiment': set(CHOICES)|{'vehicle_id'}, 'fixture': {'fixture'},
               'validate-map': {'model_data','vehicle_id','load_case','temperature_C'},
               'validate-modal': {'model_data','vehicle_id','load_case','temperature_C'}}.get(action, set())
    if set(params)-allowed:
        raise ValueError('unsupported parameters: '+', '.join(sorted(set(params)-allowed)))
    for key, values in CHOICES.items():
        if key in params and (type(params[key]) not in ((str,) if isinstance(values[0], str) else (int, float)) or params[key] not in values):
            raise ValueError('unsupported '+key)
    if 'vehicle_id' in params and not isinstance(params['vehicle_id'], str):
        raise ValueError('vehicle_id must be a catalogue identity')
    if action in ('validate-map','validate-modal') and (not isinstance(params.get('model_data'), dict) or not params.get('vehicle_id')):
        raise ValueError('inline model_data and selected vehicle_id required')
    if action=='fixture' and params.get('fixture','nonlinear-magnetics') not in ('current','laminate','nonlinear-magnetics'):
        raise ValueError('unknown fixture')
    return action, deepcopy(params)


def _environment():
    return dict(os.environ, PYTHONPATH=str(ROOT), OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1',
                MPLBACKEND='Agg', PYTHONDONTWRITEBYTECODE='1')


def _chrono_python(root):
    python = Path(root)/'build/trip-dynamics/environment/chrono/bin/python'
    if not python.is_file() or not os.access(python, os.X_OK):
        raise RuntimeError('private PyChrono environment unavailable; no benchmark fallback')
    return python


def _probe_chrono(root):
    try:
        python = _chrono_python(root)
        result = subprocess.run([str(python), '-c',
            'import json; from engineering.trip_dynamics.chrono_runner import solver_info; print(json.dumps(solver_info()))'],
            cwd=ROOT, env=_environment(), capture_output=True, text=True, timeout=30)
        if result.returncode:
            return dict(available=False, fallback=False, reason=result.stderr[-2000:])
        value = json.loads(result.stdout)
        if value.get('available') is not True or value.get('fallback') is not False or not value.get('solver_id'):
            return dict(available=False, fallback=False, reason=value.get('reason','native solver identity absent'))
        return value
    except (RuntimeError, OSError, ValueError, subprocess.TimeoutExpired) as error:
        return dict(available=False, fallback=False, reason=str(error))


def probe(root=ROOT):
    root = Path(root)
    getdp = root/'build/trip-dynamics/tools/getdp-3.5.0-Linux64/bin/getdp'
    native = dict(available=getdp.is_file(), executed=False)
    if native['available']:
        run = subprocess.run([str(getdp), '-version'], capture_output=True, text=True, timeout=10)
        native.update(available=run.returncode==0, version=(run.stdout+run.stderr).strip(),
                      sha256=sha256(getdp.read_bytes()).hexdigest(), executed=True)
    return dict(schema='osr-trip-interactive-tools/1', chrono=_probe_chrono(root), getdp=native,
                code_aster=dict(executed=False, installed_by_this_action=False),
                global_environment_modified=False, **FLAGS)


def _selected(params, definitions):
    vehicle = _vehicle(definitions, params.get('vehicle_id'))
    from .scenario import scenario
    mode = params.get('mode','evidence')
    case = scenario('selected-'+identity(params)[:16], params.get('distance_m',2000),
        params.get('load_case','AW3'), temperature_C=params.get('temperature_C',20), mode=mode,
        mechanical_step_s=params.get('mechanical_step_s',.001),
        vehicle_id=vehicle['candidate_id'] if mode=='benchmark' else None)
    return vehicle, case


def _benchmark(root, output, vehicle, case):
    backend = _probe_chrono(root)
    if backend.get('available') is not True:
        raise RuntimeError(backend.get('reason','native Chrono unavailable'))
    context = comparison(vehicle)
    mass = context['empty_kg_per_car'] if case['load_case']=='empty' else context['AW3_kg_per_car']
    job = dict(scenario=case, masses_kg=[mass]*6, mechanical_step_s=case['mechanical_step_s'], expected_solver_id=backend['solver_id'])
    job['job_id'] = identity(job)
    _write(output/'benchmark-input.json',job)
    command = [str(_chrono_python(root)), '-m', 'engineering.trip_dynamics', 'benchmark-worker',
               '--input', str(output/'benchmark-input.json'), '--output', str(output/'benchmark-result.json')]
    with (output/'benchmark-stdout.txt').open('xb') as stdout, (output/'benchmark-stderr.txt').open('xb') as stderr:
        process = subprocess.run(command, cwd=ROOT, env=_environment(), stdout=stdout, stderr=stderr, timeout=280)
    if process.returncode:
        raise RuntimeError('native Chrono worker failed; see retained stdout/stderr')
    result = _json(output/'benchmark-result.json')
    if result.get('input_job_id') != job['job_id'] or result.get('backend',{}).get('solver_id') != backend['solver_id']:
        raise ValueError('native result differs from exact selected job/solver')
    if result.get('physical_accepted') is not False or result.get('journey_accepted') is not False:
        raise ValueError('ideal numerical benchmark cannot confer acceptance')
    import matplotlib
    matplotlib.use('Agg')
    from matplotlib import pyplot as plt
    figure, axes = plt.subplots(2,1,sharex=True,figsize=(9,6),layout='constrained')
    rows=result['trace']
    axes[0].plot([r['time_s'] for r in rows],[r['cars'][0]['velocity_m_s'][0] for r in rows])
    axes[1].plot([r['time_s'] for r in rows],[r['cars'][0]['translation_m'] for r in rows])
    axes[0].set_ylabel('Lead-car speed (m/s)');axes[1].set_ylabel('Lead-car translation (m)')
    axes[1].set_xlabel('Simulated time (s)')
    figure.suptitle('Actual Chrono method trace; ideal support and prescribed force\nNot candidate journey performance')
    figure.savefig(output/'trace.png',dpi=140)
    plt.close(figure)
    return result


def _fixture(name, output, root):
    if name=='laminate':
        from .flexible_body import laminate_benchmark
        return laminate_benchmark()
    if name=='nonlinear-magnetics':
        from .fixtures.magnetics.run_fixture import run
        getdp = Path(root)/'build/trip-dynamics/tools/getdp-3.5.0-Linux64/bin/getdp'
        return run(output/'magnetic',getdp,timeout_s=120)
    from .onboard_control import current_fixture
    from .vehicle import _checked
    # Execute the retained exact ABI build; don't silently compile or install
    # into a shared/global path from a browser job.
    record = _json(Path(root)/'docs/design-engine/trip-dynamics/rust-current-fixture.json')
    binary = Path(root)/'build/trip-dynamics/rust/release/libosr_full_dynamics_kernel.so'
    build = record['build']
    if sha256(binary.read_bytes()).hexdigest() != build['binary_sha256']:
        raise ValueError('installed Rust ABI differs from retained build')
    for path, digest in build['source_sha256'].items():
        _checked(root,path,digest)
    return dict(scope='Executed existing source-bound Rust current-controller ABI; not a magnetic force or journey model',
                binary_sha256=build['binary_sha256'], result=current_fixture(binary), **FLAGS)


def execute(request, output, root=ROOT):
    """Execute one validated local job. Server chooses output/root, never JSON.

    Runtime/model refusal is retained as a result. Invalid request syntax raises
    before creating output. Every output is under the caller's fresh directory.
    """
    action, params = _validate_request(request)
    root, output = Path(root).resolve(), Path(output)
    if output.is_symlink() or any(p.is_symlink() for p in [output,*output.parents]):
        raise ValueError('ordinary server-allocated output directory required')
    output = output.resolve()
    if output.exists() and (not output.is_dir() or any(output.iterdir())):
        raise ValueError('fresh or empty output directory required')
    definitions = _definitions(root)
    vehicle, case = _selected(params,definitions) if action in ('experiment','validate-map','validate-modal') else (None,None)
    from .campaign import source_snapshot
    from .magnetic_maps import current_magnetic_evidence
    magnetic = current_magnetic_evidence(root)
    before = source_snapshot(root,definitions,magnetic)
    output.mkdir(parents=True,exist_ok=True)
    _write(output/'request.json', request)
    execution = 'completed'
    try:
        if action=='experiment':
            if case['mode']=='evidence':
                from .campaign import evidence_attempt
                result = evidence_attempt(case,vehicle,magnetic)
                case = result['scenario']
                execution = 'refused'
            else:
                result = _benchmark(root,output,vehicle,case)
        elif action=='fixture':
            result = _fixture(params.get('fixture','nonlinear-magnetics'),output,root)
        elif action=='probe':
            result = probe(root)
        elif action=='setup-tools':
            from .setup_tools import install
            result = install(output/'tools')
            result['chrono_environment_installed']=False
            result['existing_private_chrono']=_probe_chrono(root)
            result['scope']='Pinned GetDP/micromamba tools installed under this job only; existing private Chrono state reported separately'
        elif action=='verify':
            from .campaign import verify
            result = verify(root/'docs/design-engine/trip-dynamics',root=root)
        elif action=='campaign':
            from .campaign import run
            native = _probe_chrono(root)
            if not native.get('available'):
                raise RuntimeError('private native Chrono required for requested full campaign')
            getdp = root/'build/trip-dynamics/tools/getdp-3.5.0-Linux64/bin/getdp'
            archive = root/'docs/design-engine/trip-dynamics/finite-coupon-artifacts.tar.gz'
            result = run(output/'campaign',root=root,chrono_python=_chrono_python(root),
                getdp=getdp,finite_coupon_archive=archive if archive.is_file() else None)
        elif action=='validate-map':
            from .magnetic_maps import validate_force_map
            valid = validate_force_map(params['model_data'],expected_identity={'candidate_id':vehicle['candidate_id']})
            if valid['evidence_kind'] != 'candidate-nonlinear3d':
                raise ValueError('synthetic/manufactured map cannot be candidate evidence')
            result = dict(valid=True,map_id=valid['map_id'],validation_scope='schema-and-candidate-identity-only',
                          source_verified=False, accepted_for_dynamics=False,
                          reason='Uploaded source declarations are not verified files; no source-file paths followed', **FLAGS)
        else:
            from .flexible_body import _equipped, validate_modal_model
            from .scenario import bind_vehicle
            case=bind_vehicle(case,vehicle['candidate_id'])
            _equipped(vehicle,case['load_case'])
            valid = validate_modal_model(params['model_data'],vehicle,case)
            result = dict(valid=True,receipt=valid.receipt(),source_verified=False,accepted_for_dynamics=False, **FLAGS)
    except (ValueError, RuntimeError, OSError, KeyError, TypeError, subprocess.TimeoutExpired) as error:
        execution='refused' if isinstance(error,(ValueError,KeyError,TypeError)) else 'failed'
        result=dict(valid=False,reason=str(error),accepted_for_dynamics=False, **FLAGS)
    if source_snapshot(root,definitions,magnetic) != before:
        execution='failed'
        result=dict(valid=False,reason='Sources changed during execution; retain outputs without reuse', **FLAGS)
    _write(output/'result.json',result)
    artifacts=[]
    for path in sorted(output.rglob('*')):
        if path.is_symlink():
            raise ValueError('job produced a symlink artifact')
        if path.is_file():
            artifacts.append(dict(path=path.relative_to(output).as_posix(),bytes=path.stat().st_size,
                                  sha256=sha256(path.read_bytes()).hexdigest()))
    answer=dict(schema='osr-trip-interactive-result/1', action=action,request_id=identity(request),
        execution_status=execution,mode=None if case is None else case['mode'],
        vehicle_id=None if vehicle is None else vehicle['candidate_id'],
        scenario_id=None if case is None else case['scenario_id'],scenario=case,
        comparison_mass_context=None if vehicle is None else comparison(vehicle),
        installed_mass_known=False,source_sha256=before,outputs=artifacts,result=result, **FLAGS)
    answer['evaluation_id']=identity(answer)
    _write(output/'execution.json',answer)
    return answer
