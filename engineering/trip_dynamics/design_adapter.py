"""Trip preflights use the existing immutable candidate/evaluation registry."""
from hashlib import sha256
from pathlib import Path
import platform

from engineering.design_search.contracts import (make_evaluation_request, make_result,
    mass_properties, validate_candidate)
from engineering.design_search.registry import ImmutableRegistry
from .scenario import bind_vehicle, validate
from .validation import gate


def evaluate_preflight(candidate, scenario, *, registry=None, force_map=None, modal_model=None):
    """Store a real completed gate evaluation, never a synthetic journey pass."""
    candidate = validate_candidate(candidate)
    scenario = validate(scenario)
    if scenario['mode'] != 'evidence':
        raise ValueError('candidate preflight requires evidence mode')
    scenario = bind_vehicle(scenario, candidate['candidate_id'])
    paths = [Path(__file__), Path(__file__).with_name('scenario.py'),
             Path(__file__).with_name('validation.py')]
    from engineering.design_search import contracts, registry as registry_module
    paths += [Path(contracts.__file__), Path(registry_module.__file__)]
    code_root = Path(__file__).resolve().parents[2]
    sources = {p.relative_to(code_root).as_posix(): sha256(p.read_bytes()).hexdigest() for p in paths}
    # Imported evidence belongs to this exact physical candidate. Its full
    # content participates in the request, so changing a map creates a new job.
    if force_map is not None:
        from .magnetic_maps import validate_force_map
        admitted = validate_force_map(force_map, expected_identity={'candidate_id': candidate['candidate_id']})
        if admitted['evidence_kind'] != 'candidate-nonlinear3d':
            raise ValueError('synthetic/manufactured maps cannot become candidate evidence')
    if modal_model is not None and modal_model.get('candidate_id') != candidate['candidate_id']:
        raise ValueError('modal body belongs to a different physical candidate')
    request = make_evaluation_request(candidate, evaluator_id='trip-dynamics/preflight-v1',
        evaluator_sources=sources, hypothesis={'no_extrapolation': True},
        settings={'force_map': force_map, 'modal_model': modal_model}, scenario=scenario,
        environment={'python': platform.python_version()}, purpose='diagnostic')
    inventory = mass_properties(candidate)
    gates = [gate('equipped-mass-properties', 'pass' if inventory['complete_installed_distribution'] else 'unknown',
                  'Use installed stock, CG and inertia from the same physical candidate.', **inventory),
             gate('nonlinear-3d-magnetic-map', 'unknown',
                  'A matched map still needs its source execution, envelope and operational ports checked; no scalar lift substitution.'),
             gate('qualified-flexible-body', 'unknown',
                  'Modal validation, equipped loads, joints, prestress and attachment transfer remain required.'),
             gate('station-force-electrical-thermal-map', 'unknown',
                  'A prescribed force benchmark is not a moving inverter/current/thermal plant.'),
             gate('closed-loop-integration-confirmation', 'unknown',
                  'A new candidate needs independently confirmed current, modal, gap and energy coupling.')]
    result = make_result(request, execution_status='executed', numerical_status='not-assessed',
        screen_status='unknown', maturity='definition', constraints=gates,
        metrics={'dynamic_execution': 'not-run', 'distance_travelled_m': 0.,
                 'installed_mass_properties': inventory},
        diagnostics=['Completed definition/readiness evaluation. No dynamic or engineering feasibility credit.'])
    if registry is not None:
        store = ImmutableRegistry(registry)
        store.store('candidate', candidate)
        store.store('evaluation-request', request)
        store.store('evaluation', result)
    return result
