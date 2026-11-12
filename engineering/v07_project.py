"""Explicit candidate custody and dependency invalidation for v0.7 projects.

Stage records are references to separately verified evaluator artifacts. This
module checks their composition; it does not authenticate arbitrary payloads or
infer engineering acceptance from matching identities.
"""
from copy import deepcopy
import re
from engineering.station_rail.common import identity

DEPENDENCIES = {
    'vehicle': (), 'geometry': (),
    'service': ('vehicle', 'geometry'),
    'civil': ('vehicle', 'geometry', 'service'),
    'manufacturing': ('vehicle',),
    'cost': ('service', 'civil', 'manufacturing'),
    'delivery': ('manufacturing', 'cost'),
    'maintenance': ('vehicle', 'manufacturing'),
    'dossier': ('service', 'civil', 'cost', 'delivery', 'maintenance'),
}


def affected(changed):
    """Return edited stages and all transitive dependants, in graph order."""
    changed = set(changed)
    if not changed <= DEPENDENCIES.keys():
        raise ValueError('Known project stages required')
    result = set(changed)
    for stage, dependencies in DEPENDENCIES.items():
        if result.intersection(dependencies):
            result.add(stage)
    return [stage for stage in DEPENDENCIES if stage in result]


def _hash(value):
    if not isinstance(value, str) or not re.fullmatch('[0-9a-f]{64}', value):
        raise ValueError('Exact SHA-256 identity required')
    return value


def stage_record(stage, candidate_id, artifact_id, *, source_sha256, dependencies):
    """Bind an already verified artifact; dependency values are stage record IDs."""
    if stage not in DEPENDENCIES or set(dependencies) != set(DEPENDENCIES[stage]):
        raise ValueError('Exact stage dependency set required')
    if not isinstance(source_sha256, dict) or not source_sha256:
        raise ValueError('Nonempty verified source bindings required')
    if any(not isinstance(k, str) or not k for k in source_sha256):
        raise ValueError('Named source bindings required')
    for value in [candidate_id, artifact_id, *source_sha256.values(), *dependencies.values()]:
        _hash(value)
    record = dict(schema='osr-v07-project-stage/1', stage=stage,
                  physical_candidate_id=candidate_id, artifact_id=artifact_id,
                  source_sha256=deepcopy(source_sha256), dependencies=deepcopy(dependencies))
    record['stage_id'] = identity(record)
    return record


def compose(candidate_id, records):
    """Reject mixed or stale dependency bindings; expose missing stages as holds."""
    _hash(candidate_id)
    if not isinstance(records, dict) or set(records) - DEPENDENCIES.keys():
        raise ValueError('Named project stage records required')
    for stage, record in records.items():
        expected = stage_record(stage, record['physical_candidate_id'], record['artifact_id'],
                                source_sha256=record['source_sha256'], dependencies=record['dependencies'])
        if expected != record or record['stage'] != stage:
            raise ValueError('Project stage seal or stage identity differs')
        if record['physical_candidate_id'] != candidate_id:
            raise ValueError('Mixed physical candidates cannot form one project')
        for dependency, stage_id in record['dependencies'].items():
            if dependency not in records or records[dependency]['stage_id'] != stage_id:
                raise ValueError('Missing or stale upstream project stage')
    missing = [stage for stage in DEPENDENCIES if stage not in records]
    result = dict(schema='osr-v07-project/1', physical_candidate_id=candidate_id,
                  records=deepcopy(records), missing_stages=missing,
                  composition_complete=not missing, engineering_accepted=False,
                  physical_accepted=False, manufacturing_release=False)
    result['project_id'] = identity(result)
    return result


def from_comparison(comparison):
    """Expose verified corridor artifacts as an incomplete, same-candidate project.

    Caller authenticates the comparison at CityStudyService's artifact boundary.
    Manufacturing/lifecycle stages stay missing until actual matching packets
    exist; no catalogue child is attached under the reference candidate ID.
    """
    if comparison.get('comparison_id') != identity({k:v for k,v in comparison.items() if k != 'comparison_id'}):
        raise ValueError('Sealed corridor comparison required')
    if comparison.get('schema') != 'osr-corridor-revision-comparison/1':
        raise ValueError('Current corridor comparison schema required')
    candidate = comparison['reference_candidate_ids']['candidate_id']
    sources = comparison['source_sha256']
    cases = {}
    for side in ('before', 'after'):
        ids = comparison['identities'][side]
        if ids['reference_candidate_ids'] != comparison['reference_candidate_ids']:
            raise ValueError('Mixed reference candidate in project comparison')
        records = {}
        artifacts = {'vehicle': ids['reference_candidate_ids']['body_candidate_id'],
                     'geometry': ids['city_input_id'], 'service': ids['service_evaluation_id'],
                     'civil': ids['civil_quantity_id']}
        for stage, artifact in artifacts.items():
            records[stage] = stage_record(stage, candidate, artifact, source_sha256=sources,
                dependencies={key:records[key]['stage_id'] for key in DEPENDENCIES[stage]})
        cases[side] = compose(candidate, records)
    return dict(schema='osr-v07-corridor-projects/1', comparison_id=comparison['comparison_id'],
                cases=cases, station_edit_affected=affected(['geometry']),
                rate_edit_affected=affected(['cost']),
                hold='Matching manufacturing, costing, delivery and maintenance project stages still required; corridor cost results remain available in their existing verified dossier.')
