"""Held, source-bound Samawah research overlay for a different physical candidate.

This adapter carries a station edit and packet identities into a research task.
It deliberately does not transfer reference service, fleet, quantity or price
results to the new candidate. The caller supplies trusted byte hashes for all
three retained input packets; a hash is not inferred from the file itself.
"""

import gzip
import hashlib
import io
import json
from pathlib import Path

from engineering.station_rail.common import identity
from engineering.v07_project import affected

MAX_COMPRESSED = 32 * 1024 * 1024
MAX_JSON = 96 * 1024 * 1024
CASES = ('before', 'after', 'delta')


def _sha(value):
    if not isinstance(value, str) or len(value) != 64 or any(c not in '0123456789abcdef' for c in value):
        raise ValueError('Exact SHA-256 required')
    return value


def _read(path, expected_sha256, *, compressed=False):
    path = Path(path)
    if path.is_symlink() or not path.is_file() or path.stat().st_size > MAX_COMPRESSED:
        raise ValueError('Regular bounded packet file required')
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != _sha(expected_sha256):
        raise ValueError('Packet byte hash differs')
    if compressed:
        with gzip.GzipFile(fileobj=io.BytesIO(raw)) as stream:
            data = stream.read(MAX_JSON + 1)
    else:
        data = raw
    if len(data) > MAX_JSON:
        raise ValueError('Decoded packet exceeds limit')
    return json.loads(data)


def _sealed(value, key):
    if not isinstance(value, dict) or value.get(key) != identity({k: v for k, v in value.items() if k != key}):
        raise ValueError('Unsealed ' + key)


def _sources(value):
    sources = value.get('source_sha256')
    if not isinstance(sources, dict) or not sources:
        raise ValueError('Named source bindings required')
    for name, digest in sources.items():
        if not isinstance(name, str) or not name or Path(name).is_absolute() or '..' in Path(name).parts:
            raise ValueError('Relative source name required')
        _sha(digest)
    return sources


def _verify_sources(source_root, source_maps):
    if source_root is None:
        return False
    root = Path(source_root).resolve(strict=True)
    for sources in source_maps:
        for name, expected in sources.items():
            path = root / name
            if path.is_symlink() or not path.is_file() or not path.resolve().is_relative_to(root):
                raise ValueError('Missing or unsafe source: ' + name)
            digest = hashlib.sha256()
            with path.open('rb') as stream:
                for chunk in iter(lambda: stream.read(1024 * 1024), b''):
                    digest.update(chunk)
            if digest.hexdigest() != expected:
                raise ValueError('Changed source: ' + name)
    return True


def build_overlay(*, comparison_path, comparison_sha256, milestone_path, milestone_sha256,
                  study_path, study_sha256,
                  proposal_path, proposal_sha256, reference_candidate_id,
                  research_candidate_id, body_candidate_id, study_id,
                  service_evaluation_id, source_root=None):
    """Return a sealed hold; no city evaluation or solver is run.

    ``source_root`` optionally checks every source binding against a full
    checkout. Without it, bindings are retained but current-source verification
    is explicitly false. Trusted expected packet hashes remain mandatory.
    """
    comparison = _read(comparison_path, comparison_sha256)
    milestone = _read(milestone_path, milestone_sha256)
    study = _read(study_path, study_sha256, compressed=True)
    proposal = _read(proposal_path, proposal_sha256, compressed=True)
    if comparison.get('schema') != 'osr-corridor-comparison-response/1':
        raise ValueError('Unexpected comparison wrapper')
    report = comparison.get('report')
    if report.get('schema') != 'osr-corridor-revision-comparison/1':
        raise ValueError('Current corridor comparison required')
    if milestone.get('schema') != 'osr-v07-samawah-milestone-record/1':
        raise ValueError('Current retained Samawah milestone required')
    if milestone['raw_evidence']['files']['run-03/comparison.json']['sha256'] != comparison_sha256:
        raise ValueError('Milestone does not bind comparison bytes')
    if (milestone['comparison_id'] != report['comparison_id']
            or milestone['edit'] != report['edit']
            or milestone['identities'] != report['identities']
            or milestone['reference_candidate_ids'] != report['reference_candidate_ids']):
        raise ValueError('Milestone and browser comparison differ')
    comparison_seal_verified = report['comparison_id'] == identity({k: v for k, v in report.items() if k != 'comparison_id'})
    _sealed(study, 'study_id')
    _sealed(proposal, 'proposal_id')
    if study.get('schema') != 'osr-railway-closure-study/1' or proposal.get('schema') != 'osr-pilot-delivery-proposal/1':
        raise ValueError('Current closure and delivery packets required')
    for value in (reference_candidate_id, research_candidate_id, body_candidate_id, study_id, service_evaluation_id):
        _sha(value)
    reference = report['reference_candidate_ids']
    if reference['candidate_id'] != reference_candidate_id or reference_candidate_id == research_candidate_id:
        raise ValueError('Distinct reference and research candidates required')
    for side in ('before', 'after'):
        if report['identities'][side]['reference_candidate_ids'] != reference:
            raise ValueError('Mixed reference candidate in corridor comparison')
    links = proposal['identities']
    bundle = study['bundle']
    if (study['study_id'] != study_id or study['body_candidate_id'] != body_candidate_id
            or bundle['candidate_id'] != research_candidate_id
            or bundle['physical_definition']['body_candidate_id'] != body_candidate_id
            or links['candidate_id'] != research_candidate_id
            or links['body_candidate_id'] != body_candidate_id
            or links['study_id'] != study_id
            or links['bundle_evaluation_id'] != bundle['evaluation_id']
            or links['service_evaluation_id'] != service_evaluation_id):
        raise ValueError('Closure, service and delivery identities disagree')
    services = [s for s in study['service_plans'] if s.get('evaluation_id') == service_evaluation_id]
    if len(services) != 1:
        raise ValueError('Explicit service evaluation missing or ambiguous')
    _sealed(services[0], 'evaluation_id')
    nominal_ids = [r['service']['evaluation_id'] for r in study['records']
                   if r.get('experiment') == 'nominal' and r.get('enabled') is True]
    if len(nominal_ids) != 6 or len(set(nominal_ids)) != 6 or service_evaluation_id not in nominal_ids:
        raise ValueError('Six retained nominal service alternatives required')
    if not set(nominal_ids) <= {s['evaluation_id'] for s in study['service_plans']}:
        raise ValueError('Nominal service alternative missing from study')
    if proposal.get('status') != 'DRAFT' or proposal['summary']['cost_scopes'] != 14:
        raise ValueError('Unreleased fourteen-scope planning draft required')
    for packet in (report, study, proposal):
        for field in ('engineering_accepted', 'physical_accepted', 'manufacturing_release',
                      'operating_release', 'selected_reference_changed'):
            if packet.get(field) not in (None, False):
                raise ValueError('Research packet cannot carry acceptance or selection')
    if study.get('integrated_selection') is not None or study.get('priced_cities_replaced') is not False:
        raise ValueError('Closure study changed selected or priced reference')
    if proposal.get('transactions_performed') or proposal.get('automatic_order_release'):
        raise ValueError('Delivery draft contains execution')
    scopes = report['cost_scopes']
    if not isinstance(scopes, dict) or len(scopes) != 14:
        raise ValueError('Fourteen reference cost scope names required')
    _sources(report)  # Historical reference bindings; not reinterpreted as current research sources.
    maps = [_sources(study), _sources(proposal)]
    current_sources_verified = _verify_sources(source_root, maps)
    result = dict(
        schema='osr-v07-candidate-corridor-overlay/1', status='HELD_RESEARCH',
        reference_candidate_id=reference_candidate_id,
        research_candidate_id=research_candidate_id, body_candidate_id=body_candidate_id,
        selected_candidate_id=None, city_recalculated=False,
        research_source_bindings_verified_against_current_checkout=current_sources_verified,
        historical_comparison_embedded_seal_verified=comparison_seal_verified,
        input_sha256=dict(comparison=_sha(comparison_sha256), study=_sha(study_sha256),
                          proposal=_sha(proposal_sha256), milestone=_sha(milestone_sha256)),
        input_ids=dict(comparison=report['comparison_id'], study=study_id,
                       proposal=proposal['proposal_id'], service=service_evaluation_id),
        input_source_map_ids=dict(historical_comparison=identity(report['source_sha256']),
                                  closure_study=identity(study['source_sha256']),
                                  delivery_proposal=identity(proposal['source_sha256'])),
        retained_nominal_service_evaluation_ids=nominal_ids,
        research_installed_mass_evaluation_id=bundle['installed_mass_evaluation_id'],
        retained_geography_context=dict(edit=milestone['edit'],
            before={k: milestone['identities']['before'][k] for k in ('source_outline_evaluation_id', 'planning_seed_id', 'city_input_id', 'manifest_id')},
            after={k: milestone['identities']['after'][k] for k in ('source_outline_evaluation_id', 'planning_seed_id', 'city_input_id', 'manifest_id')}),
        invalidated_stages=affected(['vehicle', 'geometry']),
        cost_scopes={name: {case: None for case in CASES} for name in sorted(scopes)},
        service=dict(normal_passenger_capacity=None, dwell_s=None, headway_s=None,
                     full_tail_clearance=None, grade=None, fleet=None,
                     platform_count=None, station_count=None,
                     powered_zones=None, grid_equipment=None, charging=None,
                     reserve=None, recovery=None),
        installed_mass=None, civil_quantities=None, operational_geometry=None,
        site_specific_prices_verified=False, affordability_established=False,
        required_inputs=[
            'Candidate-specific Samawah formation, platform, door and full-tail clearance geometry',
            'Normal passenger capacity, dwell, headway and grade on both station cases',
            'Installed mass, force and independent braking maps at relevant loads',
            'Powered-zone length, grid equipment, energy, charging, reserve and recovery duty',
            'Fleet, civil quantities, station and guideway interfaces, and all fourteen priced scopes',
            'Native GIS revision identity and source-bound before/after city evaluation',
        ],
        limitations=[
            'Reference corridor numbers belong to the passive-wheel candidate and are not transferred.',
            'The browser comparison embedded seal is not reproducible from its retained JSON; the milestone byte hash authenticates context only.',
            'The closure service is a separate short research pilot, not a Samawah timetable or fleet.',
            'No affordable whole-life service, engineering acceptance or physical qualification established.',
        ],
        engineering_accepted=False, physical_accepted=False,
        manufacturing_release=False, operating_release=False,
    )
    result['overlay_id'] = identity(result)
    return result
