"""Independent stock/provenance checks, explicitly below domain-physics confirmation."""
from hashlib import sha256
import math
from pathlib import Path

from . import contracts

ROOT = Path(__file__).resolve().parents[2]


def request_for(candidate, primary):
    contracts.validate_result(primary)
    sources = dict(primary['request']['evaluator_sources'])
    sources[Path(__file__).relative_to(ROOT).as_posix()] = sha256(Path(__file__).read_bytes()).hexdigest()
    return contracts.make_evaluation_request(candidate, evaluator_id=primary['request']['evaluator_id'],
        evaluator_sources=sources, purpose='confirmation', hypothesis=primary['request']['hypothesis'],
        settings=dict(confirmation_of=primary['evaluation_id'], primary_result_sha256=primary['result_sha256'], verification_scope='arithmetic-source-only'),
        scenario=dict(independent_check='stock-integrals-and-source-integrity'),
        environment=primary['request']['environment'])


def confirm(candidate, request, primary):
    contracts.validate_candidate(candidate); contracts.validate_result(primary); contracts.validate_request(request)
    if request != request_for(candidate, primary): raise ValueError('independent verifier context differs')
    if primary['candidate_id'] != candidate['candidate_id'] or primary['requirement_revision'] != candidate['requirement_revision']:
        raise ValueError('verifier input mixes candidate contexts')
    sources_match = all((ROOT/name).is_file() and sha256((ROOT/name).read_bytes()).hexdigest() == expected
                        for name, expected in request['evaluator_sources'].items())
    materials = {row['id']:row for row in candidate['materials']}
    geometry = {row['id']:row for row in candidate['geometry']}
    checks = []; unknown = []
    for item in candidate['installed_inventory']:
        if item['status'] == 'unknown':
            unknown.append(item['id']); continue
        part = geometry.get(item.get('geometry_id'))
        if not part or part['kind'] != 'box': continue
        density = materials[part['material_id']].get('density_kg_m3')
        if density is None: continue
        mass = math.prod(part['size_m']) * density
        cg = [part['at_m'][index]+part['size_m'][index]/2 for index in range(3)]
        checks.append(dict(id=item['id'], mass_matches=math.isclose(item['unit_mass_kg'], mass, rel_tol=1e-9),
            cg_matches=all(math.isclose(a,b,rel_tol=1e-9,abs_tol=1e-9) for a,b in zip(item['cg_m'],cg))))
    passed = sources_match and all(row['mass_matches'] and row['cg_matches'] for row in checks)
    return contracts.make_result(request, execution_status='executed', numerical_status='converged',
        screen_status='pass' if passed else 'fail', maturity='definition',
        metrics=dict(source_bindings_match=sources_match, independently_checked_boxes=len(checks),
                     unknown_stock_count=len(unknown), original_screen_status=primary['screen_status']),
        constraints=checks, diagnostics=['Arithmetic/source consistency only; no independent magnetic, thermal, structural or route qualification.'])
