"""Executable closure worklist and strict ingestion of unaccepted test records.

Preparation and numerical checks never confer a physical or manufacturing release.
An external authenticator must verify identities/signatures using its own trust
store; a checksum, reviewer string or a locally supplied `passed` is insufficient.
"""
from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime
from hashlib import sha256
import gzip
import io
import json
import math
from pathlib import Path, PurePosixPath

from . import configuration, requirements, specification, transition

ROOT = Path(__file__).resolve().parents[2]
INPUT = Path(__file__).with_name('data') / 'qualification-plan.json'
OBLIGATIONS = Path(__file__).with_name('closure-obligations.json')
OUTPUT = ROOT / 'docs/design-engine/ferrite-maglev/qualification'
TEST = ROOT / 'engineering/analysis/tests/test_ferrite_maglev_qualification.py'
FLAGS = {**transition.FLAGS, 'engineering_accepted': False}
FILES = {'study.json.gz', 'README.md', 'evidence-template.json', 'raw-template.json'}
SCHEMA = 'osr-design-qualification/1'
MAX_RAW = 16 * 1024 * 1024


def encoded(value):
    return json.dumps(value, sort_keys=True, allow_nan=False, separators=(',', ':')).encode()


def content_hash(value):
    return sha256(encoded(value)).hexdigest()


def file_hash(path):
    return sha256(Path(path).read_bytes()).hexdigest()


def _json(raw):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError('duplicate JSON key in evidence')
            result[key] = value
        return result
    def constant(value):
        raise ValueError('non-finite JSON number in evidence: ' + value)
    return json.loads(raw, object_pairs_hook=pairs, parse_constant=constant)


def source_paths():
    from . import evacuation, geometry, model
    authored = json.loads(specification.INPUT.read_text())['source']
    return sorted({Path(__file__), INPUT, OBLIGATIONS, TEST,
        Path(requirements.__file__), Path(transition.__file__), transition.REQUIREMENTS,
        transition.DATA, Path(specification.__file__), specification.INPUT, ROOT / authored,
        *configuration.source_paths(), Path(evacuation.__file__), evacuation.INPUT,
        Path(geometry.__file__), Path(model.__file__), model.POLICY})


def source_snapshot():
    return {path.relative_to(ROOT).as_posix(): file_hash(path) for path in source_paths()}


def _unique(rows, label):
    ids = [row['id'] for row in rows]
    if not ids or len(ids) != len(set(ids)):
        raise ValueError('empty or duplicate ' + label)
    return set(ids)


def load():
    plan = json.loads(INPUT.read_text())
    register = requirements.register()
    ids = _unique(register['requirements'], 'applicable requirements')
    if plan['schema'] != 'osr-qualification-plan/1' or plan['status'] != 'prepared-unexecuted':
        raise ValueError('unexecuted qualification plan required')
    if plan['planning_targets_are_qualified_limits'] is not False:
        raise ValueError('planning targets cannot become qualified limits')
    if set(plan['requirement_group_map']) != ids:
        raise ValueError('applicable requirement coverage differs')
    expected_groups = json.loads(OBLIGATIONS.read_text())['groups']
    groups = _unique(plan['groups'], 'obligation groups')
    if groups != {g['id'] for g in expected_groups}:
        raise ValueError('obligation group coverage differs')
    protocols = _unique(plan['protocols'], 'protocols')
    refs = _unique(plan['reference_sources'], 'reference sources')
    if {p['gate'] for p in plan['protocols']} != {f'G{i}' for i in range(6)}:
        raise ValueError('all six physical programme gates required')
    for expected in expected_groups:
        actual = next(g for g in plan['groups'] if g['id'] == expected['id'])
        if any(actual.get(k) != v for k, v in expected.items()):
            raise ValueError('controlled obligation contents differ')
        wanted = {p['id'] for p in plan['protocols'] if expected['id'] in p['group_ids']}
        if set(actual['required_protocol_ids']) != wanted or not wanted:
            raise ValueError('group protocol coverage differs')
        for n in expected['sp_numbers']:
            if expected['id'] not in plan['requirement_group_map'][f'SP-{n:03d}']:
                raise ValueError('supplied specification obligation assignment differs')
    for assignment in plan['requirement_group_map'].values():
        if not assignment or len(assignment) != len(set(assignment)) or not set(assignment) <= groups:
            raise ValueError('invalid requirement group assignment')
    for p in plan['protocols']:
        if (p['evidence_class'] not in plan['evidence_policy']['allowed_classes']
                or not p['group_ids'] or not set(p['group_ids']) <= groups
                or not set(p['reference_ids']) <= refs
                or any(p[k] is not False for k in ('limits_approved', 'executed', 'accepted'))):
            raise ValueError('invalid or pre-accepted protocol')
        channels = [c['name'] for c in p['channels']]
        if len(channels) != len(set(channels)) or channels.count('time_s') != 1:
            raise ValueError('unique synchronised channels required')
        if any(not c['unit'] for c in p['channels']):
            raise ValueError('explicit channel units required')
        if not p['procedure'] or not p['specimen'] or not p['required_cases']:
            raise ValueError('actionable procedure, specimen and cases required')
        if len(p['required_cases']) != len(set(p['required_cases'])):
            raise ValueError('duplicate protocol cases')
        _unique(p['criteria'], 'criteria')
        for c in p['criteria']:
            channel = next((r for r in p['channels'] if r['name'] == c['channel']), None)
            if (channel is None or c['unit'] != channel['unit'] or c['limit'] is not None
                    or c['statistic'] not in {'min', 'max', 'absmax', 'mean', 'last'}
                    or c['comparison'] not in {'ge', 'le'} or not c['derivation']):
                raise ValueError('unqualified or inconsistent criterion')
    policy = plan['evidence_policy']
    if (type(policy['max_raw_bytes']) is not int or not 1 <= policy['max_raw_bytes'] <= MAX_RAW
            or type(policy['max_samples']) is not int or not 1 <= policy['max_samples'] <= 100000
            or policy['all_release_flags_remain_false'] is not True):
        raise ValueError('bounded unreleased evidence policy required')
    return plan


def binding():
    register = requirements.register()
    return dict(configuration_revision=register['configuration_revision'],
        configuration_sha256=content_hash(configuration.selected().record()),
        requirements_revision=register['revision'],
        requirements_sha256=content_hash(register), source_sha256=source_snapshot())


def _task(identity, evidence_class, deliverable, prerequisites, **values):
    return dict(id=identity, evidence_class=evidence_class, deliverable=deliverable,
        prerequisites=sorted(set(prerequisites)), state='hold', accepted=False,
        digital_state='planned', digital_evidence=[], physical_state='unexecuted',
        pass_rule='Exact-revision deliverable and required authenticated records, approved limits and closed deviations',
        hold_rule='Missing/unverified evidence, unresolved limit, prerequisite, approval or configuration mismatch',
        fail_rule='Authenticated applicable measurement fails its pre-approved guard-banded criterion or a mandatory prerequisite is revoked',
        **values)


def _dag(tasks):
    ids = _unique(tasks, 'closure tasks')
    pending = {t['id']: set(t['prerequisites']) for t in tasks}
    if any(not deps <= ids for deps in pending.values()):
        raise ValueError('unknown task prerequisite')
    ordered = []
    while pending:
        ready = sorted(k for k, deps in pending.items() if not deps)
        if not ready:
            raise ValueError('cyclic closure task dependencies')
        ordered.extend(ready)
        pending = {k: deps - set(ready) for k, deps in pending.items() if k not in ready}
    return ordered


def study():
    plan = load(); register = requirements.register(); frozen = binding(); tasks = []
    tasks.append(_task('baseline/freeze', 'executed-study',
        'Controlled requirement texts, selected configuration, hazard/source/uncertainty inventory and agreed operator demand; signed baseline disposition', []))
    group_rows = {g['id']: g for g in plan['groups']}
    for g in plan['groups']:
        tasks.append(_task('group/' + g['id'] + '/design', 'executed-study',
            g['deliverable'], ['baseline/freeze'], group_ids=[g['id']],
            system_ids=g['system_ids'], missing_evaluators=g['missing_evaluators_or_external_tests']))
    for p in plan['protocols']:
        previous = [] if p['gate'] == 'G0' else ['gate/G' + str(int(p['gate'][1:]) - 1)]
        deps = ['group/' + g + '/design' for g in p['group_ids']]
        tasks.append(_task('protocol/' + p['id'], p['evidence_class'],
            p['specimen'] + '; raw calibrated measurements, complete case matrix, uncertainty and independently authenticated disposition',
            previous + deps, protocol_id=p['id'], gate=p['gate'], group_ids=p['group_ids']))
    for i in range(6):
        gate = f'G{i}'
        deps = ['protocol/' + p['id'] for p in plan['protocols'] if p['gate'] == gate]
        tasks.append(_task('gate/' + gate, 'independent-review',
            gate + ' independently witnessed exact-article decision with prior gate/NCR closure', deps,
            gate=gate, decision=None))
    trace = []
    for r in register['requirements']:
        rid = r['id']; groups = plan['requirement_group_map'][rid]
        pids = sorted({pid for g in groups for pid in group_rows[g]['required_protocol_ids']})
        definition = 'requirement/' + rid + '/definition'
        verification = 'requirement/' + rid + '/verification'
        acceptance = 'requirement/' + rid + '/independent-review'
        tasks.append(_task(definition, 'executed-study',
            r['requirement'] + '; dimensioned/configured deliverable and explicit uncertainty/acceptance allocation',
            ['group/' + g + '/design' for g in groups], requirement_id=rid))
        tasks.append(_task(verification, 'physical-rig',
            rid + ' case-specific verification report, raw records and traceable applicable procedure/limit dispositions',
            [definition] + ['protocol/' + pid for pid in pids], requirement_id=rid,
            protocol_ids=pids, evidence_classes=sorted({p['evidence_class'] for p in plan['protocols'] if p['id'] in pids})))
        tasks.append(_task(acceptance, 'independent-review',
            rid + ' authenticated independent acceptance or explicit rejected/held decision; supplier/site/rig scope must match requirement',
            [verification], requirement_id=rid))
        trace.append(dict(requirement_id=rid, requirement_sha256=content_hash(r),
            requirement_text=r['requirement'], group_ids=groups, protocol_ids=pids,
            task_ids=[definition, verification, acceptance], accepted=False))
    for g in plan['groups']:
        deps = ['requirement/' + r['requirement_id'] + '/independent-review' for r in trace if g['id'] in r['group_ids']]
        tasks.append(_task('group/' + g['id'] + '/closure', 'independent-review',
            'Complete independent acceptance dossier for all listed systems and applicable requirements', deps,
            group_ids=[g['id']], system_ids=g['system_ids']))
    tasks.append(_task('system/independent-closure', 'independent-review',
        'All requirement, system, route/operator/manufacturing and G0–G5 independent dispositions; no local automatic release',
        ['gate/G5'] + ['group/' + g['id'] + '/closure' for g in plan['groups']]))
    order = _dag(tasks)
    current = dict(schema=SCHEMA, revision=plan['revision'], binding=frozen,
        binding_sha256=content_hash(frozen), requirements=trace, groups=plan['groups'],
        protocols=plan['protocols'], tasks=tasks, topological_task_order=order,
        raw_data_schemas={p['id']: raw_schema(p) for p in plan['protocols']},
        common_prerequisites=plan['common_prerequisites'], references=plan['reference_sources'],
        coverage=dict(applicable_requirements=len(trace), supplied_specification_requirements=sum(r['requirement_id'].startswith('SP-') for r in trace),
            obligation_groups=len(plan['groups']), system_ids=len({s for g in plan['groups'] for s in g['system_ids']}),
            gates=6, protocols=len(plan['protocols']), tasks=len(tasks), accepted_requirements=0,
            accepted_physical_gates=0, uncovered_requirements=[], uncovered_groups=[]),
        status='prepared-unexecuted; supplier/site/rig/independent records and approved limits required',
        **FLAGS)
    current['content_sha256'] = content_hash(current)
    return current


def _number(value, label):
    try:
        valid = type(value) in (int, float) and math.isfinite(value)
    except OverflowError:
        valid = False
    if not valid:
        raise ValueError('finite numeric ' + label + ' required')
    return value


def _digest(value):
    return isinstance(value, str) and len(value) == 64 and all(c in '0123456789abcdef' for c in value)


def _time(value):
    if not isinstance(value, str) or not value.endswith('Z'):
        raise ValueError('UTC timestamp with Z required')
    try:
        parsed = datetime.fromisoformat(value[:-1] + '+00:00')
        if parsed.tzinfo is None:
            raise ValueError('timezone-aware UTC timestamp required')
        return parsed
    except ValueError as exc:
        raise ValueError('invalid UTC timestamp') from exc


def _attested(attestation, payload, role, authenticator):
    if not isinstance(attestation, dict):
        return False
    if (attestation.get('role') != role or not attestation.get('identity')
            or not attestation.get('signature') or attestation.get('payload_sha256') != content_hash(payload)):
        return False
    # Authentication is deliberately external; recording a claimed name/hash is not authentication.
    return authenticator is not None and authenticator(deepcopy(attestation), role) is True


@dataclass(frozen=True)
class EvidenceIdentity:
    protocol_id: str
    procedure_revision: str
    binding_sha256: str
    configuration_revision: str
    article_configuration_sha256: str

    @classmethod
    def parse(cls, value, protocol, current):
        if not isinstance(value, dict) or set(value) != set(cls.__annotations__):
            raise ValueError('exact typed evidence identity required')
        result = cls(**value)
        if (result.protocol_id != protocol['id'] or result.procedure_revision != protocol['revision']
                or result.binding_sha256 != current['binding_sha256']
                or result.configuration_revision != current['binding']['configuration_revision']
                or not _digest(result.article_configuration_sha256)):
            raise ValueError('stale or invalid procedure/configuration/source binding')
        return result


def _read_owned(root, record, maximum):
    if not isinstance(record, dict) or set(record) != {'name', 'sha256', 'bytes'}:
        raise ValueError('typed raw file receipt required')
    name = record['name']
    p = PurePosixPath(name) if isinstance(name, str) else None
    if (not name or p is None or p.is_absolute() or '..' in p.parts or p.as_posix() != name
            or not _digest(record['sha256']) or type(record['bytes']) is not int
            or not 1 <= record['bytes'] <= maximum):
        raise ValueError('unsafe path, digest or raw size')
    root = Path(root).resolve(); path = root / name
    if any((root / Path(*p.parts[:i])).is_symlink() for i in range(1, len(p.parts) + 1)):
        raise ValueError('raw evidence may not traverse links')
    if not path.is_file() or not path.resolve().is_relative_to(root):
        raise ValueError('raw evidence outside owned root')
    with path.open('rb') as stream:
        raw = stream.read(maximum + 1)
    if len(raw) != record['bytes'] or len(raw) > maximum or sha256(raw).hexdigest() != record['sha256']:
        raise ValueError('raw evidence bytes/checksum differ')
    return _json(raw)


def raw_schema(protocol):
    """Per-protocol JSON Schema; temporal/authenticity rules are checked in code."""
    channels = {c['name']: dict(type='number', description=c['role'] + '; unit=' + c['unit']) for c in protocol['channels']}
    return {'$schema': 'https://json-schema.org/draft/2020-12/schema',
        'title': protocol['id'] + ' unaccepted measurement records', 'type': 'object',
        'required': ['schema', 'identity', 'provenance', 'units', 'samples', 'accepted'],
        'properties': {
            'schema': {'const': 'osr-qualification-raw/1'}, 'identity': {'type': 'object'},
            'provenance': {'type': 'object', 'required': ['kind', 'synthetic', 'simulated', 'operator', 'producer'],
                'properties': {'kind': {'const': protocol['evidence_class']}, 'synthetic': {'const': False}, 'simulated': {'const': False}}},
            'units': {'const': {c['name']: c['unit'] for c in protocol['channels']}},
            'accepted': {'const': False},
            'samples': {'type': 'array', 'minItems': 1, 'maxItems': 100000, 'items': {
                'type': 'object', 'additionalProperties': False,
                'required': ['case_id', *channels],
                'properties': {'case_id': {'enum': protocol['required_cases']}, **channels}}}}}


def template(protocol_id='magnetic-module'):
    """Unexecuted import template. Every null is an explicit hold, not evidence."""
    current = study(); p = next(p for p in current['protocols'] if p['id'] == protocol_id)
    identity = dict(protocol_id=p['id'], procedure_revision=p['revision'],
        binding_sha256=current['binding_sha256'], configuration_revision=current['binding']['configuration_revision'],
        article_configuration_sha256=None)
    raw = dict(schema='osr-qualification-raw/1', identity=identity,
        provenance=dict(kind='unexecuted-template', operator=None, producer=None, synthetic=False, simulated=False),
        units={c['name']: c['unit'] for c in p['channels']}, samples=[],
        required_case_ids=p['required_cases'], accepted=False)
    bundle = dict(schema='osr-qualification-evidence/1', identity=identity,
        article_serials=[], material_batches=[], started_at=None, ended_at=None,
        raw_file=dict(name='measurements.json', sha256=None, bytes=None),
        calibrations=[], limits=[], prerequisite_dispositions=[], deviations=[],
        operator=None, witness_attestation=None, raw_attestation=None,
        independent_decision=None, accepted=False,
        instructions='Templates and synthetic fixtures cannot close physical gates. Use authenticated lab/site/supplier records; null limits block evaluation.')
    return bundle, raw


def assess_evidence(protocol_id, bundle, raw_root, *, authenticator=None):
    """Validate raw records and guard-band approved limits; never issue release.

    `authenticator(attestation, required_role)` must independently verify a
    signature and the signer's authorised scope. Without it all measurements
    remain held even when a self-declared reviewer reports success.
    """
    current = study(); plan = load()
    protocol = next((p for p in plan['protocols'] if p['id'] == protocol_id), None)
    if protocol is None:
        raise ValueError('unknown qualification protocol')
    if not isinstance(bundle, dict) or bundle.get('schema') != 'osr-qualification-evidence/1':
        raise ValueError('typed qualification evidence required')
    if bundle.get('accepted') is not False:
        raise ValueError('imported self-acceptance is forbidden')
    identity = EvidenceIdentity.parse(bundle.get('identity'), protocol, current)
    raw = _read_owned(raw_root, bundle['raw_file'], plan['evidence_policy']['max_raw_bytes'])
    if raw.get('schema') != 'osr-qualification-raw/1' or raw.get('identity') != bundle['identity']:
        raise ValueError('raw schema or exact identity differs')
    provenance = raw.get('provenance', {})
    if (not isinstance(provenance, dict) or provenance.get('kind') != protocol['evidence_class']
            or provenance.get('synthetic') is not False or provenance.get('simulated') is not False):
        raise ValueError('simulation, synthetic, supplier or template evidence cannot impersonate another evidence class')
    if raw.get('accepted') is not False:
        raise ValueError('raw self-acceptance is forbidden')
    if raw.get('units') != {c['name']: c['unit'] for c in protocol['channels']}:
        raise ValueError('exact required channel units differ')
    serials = bundle.get('article_serials')
    batches = bundle.get('material_batches')
    if (not isinstance(serials, list) or not serials or any(not isinstance(s, str) or not s for s in serials)
            or len(serials) != len(set(serials)) or not isinstance(batches, list)
            or not batches or any(not isinstance(s, str) or not s for s in batches)):
        raise ValueError('serial and batch identities required')
    started = _time(bundle['started_at']); ended = _time(bundle['ended_at'])
    if ended < started:
        raise ValueError('negative evidence run duration')
    samples = raw.get('samples')
    if not isinstance(samples, list) or not 1 <= len(samples) <= plan['evidence_policy']['max_samples']:
        raise ValueError('bounded nonempty raw samples required')
    channels = {c['name'] for c in protocol['channels']}; cases = {}
    duration = (ended - started).total_seconds()
    for row in samples:
        if not isinstance(row, dict) or set(row) != channels | {'case_id'} or row['case_id'] not in protocol['required_cases']:
            raise ValueError('required case/channel sample schema differs')
        for name in channels:
            _number(row[name], name)
        case = cases.setdefault(row['case_id'], [])
        if row['time_s'] < 0 or row['time_s'] > duration or (case and row['time_s'] <= case[-1]['time_s']):
            raise ValueError('strict case timebase within run duration required')
        case.append(row)
    holds = []
    if any(len(cases.get(case, [])) < protocol['minimum_samples_per_case'] for case in protocol['required_cases']):
        holds.append('missing or undersampled required physical cases')
    if not bundle.get('operator') or provenance.get('operator') != bundle['operator']:
        raise ValueError('operator identity differs')
    raw_claim = dict(identity=bundle['identity'], raw_file=bundle['raw_file'],
        article_serials=serials, material_batches=batches,
        started_at=bundle['started_at'], ended_at=bundle['ended_at'], operator=bundle['operator'])
    if not _attested(bundle.get('raw_attestation'), raw_claim, 'record-producer', authenticator):
        holds.append('raw provenance/signature not authenticated')
    witness = bundle.get('witness_attestation')
    if (not _attested(witness, raw_claim, 'independent-witness', authenticator)
            or witness.get('identity') == bundle['operator']):
        holds.append('independent witness not authenticated or not independent')
    calibrations = bundle.get('calibrations', [])
    if not isinstance(calibrations, list):
        raise ValueError('typed calibration list required')
    names = [c.get('channel') for c in calibrations if isinstance(c, dict)]
    if len(names) != len(calibrations) or len(names) != len(set(names)) or not set(names) <= channels:
        raise ValueError('unknown or duplicate calibration channel')
    uncertainties = {}
    for c in calibrations:
        payload = {k: v for k, v in c.items() if k != 'attestation'}
        unit = raw['units'][c['channel']]
        u = _number(c.get('expanded_uncertainty'), 'expanded uncertainty')
        lower = _number(c.get('range_min'), 'calibrated range minimum')
        upper = _number(c.get('range_max'), 'calibrated range maximum')
        if (u < 0 or lower >= upper or c.get('unit') != unit or not _digest(c.get('certificate_sha256'))
                or not c.get('instrument_serial') or _number(c.get('coverage_factor'), 'coverage factor') <= 0):
            raise ValueError('valid calibration unit/certificate/instrument/uncertainty required')
        if any(not lower <= row[c['channel']] <= upper for row in samples):
            holds.append('samples outside calibrated measurement range: ' + c['channel'])
        elif (_time(c['calibrated_at']) > started or _time(c['valid_until']) < ended
                or not _attested(c.get('attestation'), payload, 'calibration-authority', authenticator)):
            holds.append('unverified or out-of-validity calibration: ' + c['channel'])
        else:
            uncertainties[c['channel']] = u
    if set(uncertainties) != channels:
        holds.append('authenticated calibration and uncertainty missing for required channels')
    limits = bundle.get('limits', [])
    if not isinstance(limits, list):
        raise ValueError('typed limit approvals required')
    cids = [c.get('criterion_id') for c in limits if isinstance(c, dict)]
    wanted = {c['id'] for c in protocol['criteria']}
    if len(cids) != len(limits) or len(cids) != len(set(cids)) or not set(cids) <= wanted:
        raise ValueError('unknown or duplicate approved criterion')
    metrics = []; failure = False
    for criterion in protocol['criteria']:
        limit = next((c for c in limits if c['criterion_id'] == criterion['id']), None)
        if limit is None:
            holds.append('missing pre-approved limit: ' + criterion['id']); continue
        payload = {k: v for k, v in limit.items() if k != 'attestation'}
        value = _number(limit.get('value'), 'approved limit')
        selected = limit.get('case_ids')
        if (limit.get('protocol_id') != protocol_id or limit.get('statistic') != criterion['statistic']
                or limit.get('unit') != criterion['unit'] or limit.get('comparison') != criterion['comparison']
                or limit.get('binding_sha256') != current['binding_sha256']
                or limit.get('article_configuration_sha256') != identity.article_configuration_sha256
                or limit.get('procedure_revision') != protocol['revision']
                or limit.get('uncertainty_policy') != 'guard-band'
                or not isinstance(selected, list) or not selected or len(selected) != len(set(selected))
                or not set(selected) <= set(protocol['required_cases']) or not limit.get('derivation_record_sha256')
                or not _digest(limit['derivation_record_sha256'])):
            raise ValueError('case-specific exact-revision qualified limit schema differs')
        if (_time(limit['approved_at']) > started
                or not _attested(limit.get('attestation'), payload, 'limit-approver', authenticator)):
            holds.append('limit not authenticated before execution: ' + criterion['id']); continue
        rows = [r for case in selected for r in cases.get(case, [])]
        if any(len(cases.get(case, [])) < protocol['minimum_samples_per_case'] for case in selected) or criterion['channel'] not in uncertainties:
            holds.append('limit case data/calibration incomplete: ' + criterion['id']); continue
        statistic = criterion['statistic']
        uncertainty = uncertainties[criterion['channel']]
        case_results = []
        for case in selected:
            values = [r[criterion['channel']] for r in cases[case]]
            observed = (min(values) if statistic == 'min' else max(values) if statistic == 'max'
                else max(map(abs, values)) if statistic == 'absmax'
                else math.fsum(values) / len(values) if statistic == 'mean' else values[-1])
            guarded = observed + uncertainty if criterion['comparison'] == 'le' else observed - uncertainty
            passed = guarded <= value if criterion['comparison'] == 'le' else guarded >= value
            case_results.append(dict(case_id=case, observed=observed,
                guard_banded_value=guarded, passed=passed))
        passed = all(c['passed'] for c in case_results)
        failure |= not passed
        metrics.append(dict(criterion_id=criterion['id'], case_ids=selected, cases=case_results,
            expanded_uncertainty=uncertainty,
            unit=criterion['unit'], limit=value, comparison=criterion['comparison'], passed=passed))
    prerequisites = bundle.get('prerequisite_dispositions', [])
    required_prereqs = {'procedure-and-hazards', 'article-and-material-revisions', 'earlier-gates-and-ncrs', 'safe-restraint-and-rescue'}
    if not isinstance(prerequisites, list):
        raise ValueError('typed prerequisite dispositions required')
    pids = [p.get('id') for p in prerequisites if isinstance(p, dict)]
    if len(pids) != len(prerequisites) or len(pids) != len(set(pids)) or not set(pids) <= required_prereqs:
        raise ValueError('unknown or duplicate prerequisite disposition')
    checked = set()
    for prerequisite in prerequisites:
        payload = {k: v for k, v in prerequisite.items() if k != 'attestation'}
        if (prerequisite.get('protocol_id') != protocol_id or prerequisite.get('binding_sha256') != current['binding_sha256']
                or prerequisite.get('article_configuration_sha256') != identity.article_configuration_sha256
                or not _digest(prerequisite.get('record_sha256'))):
            raise ValueError('prerequisite exact revision/hash differs')
        if _attested(prerequisite.get('attestation'), payload, 'independent-assessor', authenticator):
            if prerequisite.get('state') == 'failed':
                failure = True
            elif prerequisite.get('state') == 'passed':
                checked.add(prerequisite['id'])
    if checked != required_prereqs:
        holds.append('authenticated approved prerequisites and previous gate/NCR closure missing')
    deviations = bundle.get('deviations')
    if not isinstance(deviations, list):
        raise ValueError('explicit deviation list required')
    # Deviations require a separate independently approved retest/procedure revision.
    if deviations:
        holds.append('deviations require authenticated disposition and compatible retest revision')
    ready = not holds and not failure and len(metrics) == len(protocol['criteria'])
    return dict(schema='osr-qualification-assessment/1', protocol_id=protocol_id,
        binding_sha256=current['binding_sha256'], article_configuration_sha256=identity.article_configuration_sha256,
        state='failed' if failure else 'passed-records' if ready else 'hold',
        evidence_ready_for_independent_decision=ready, holds=sorted(set(holds)), metrics=metrics,
        raw_file=deepcopy(bundle['raw_file']), accepted=False,
        scope='Authenticated record consistency and guard-banded measurement screening only; an independent gate disposition and system acceptance remain required', **FLAGS)


def readme(result):
    c = result['coverage']
    lines = ['# Qualification and design closure worklist', '',
        f"{c['applicable_requirements']} applicable requirements, {c['supplied_specification_requirements']} supplied specification items, {c['obligation_groups']} obligation groups, {c['system_ids']} system IDs and six gates have explicit task/protocol coverage. {c['protocols']} protocols and {c['tasks']} dependency-ordered tasks are prepared. Accepted requirements and physical gates remain zero.", '',
        'Every requirement retains its exact text/digest, dimensioned design deliverable, applicable measurement procedures and separate independent-review task. This register makes the remaining work actionable; it does not complete a train or qualify a physical test.', '',
        '| Protocol | Gate | Evidence | Required cases |', '|---|---|---|---:|']
    for p in result['protocols']:
        lines.append(f"| {p['title']} | {p['gate']} | {p['evidence_class']} | {len(p['required_cases'])} |")
    lines += ['', 'Approved limits remain null until the responsible designer/operator/assessor derives and authenticates them before a run. Numerical study targets, manufacturer claims and open-map site estimates cannot be imported as qualified limits. Each protocol includes specimen definitions, real test steps, required channels/units, case coverage, criterion derivations and raw-data schema.', '',
        'The importer checks serial/batch identity; source/configuration/procedure revisions; exact raw bytes and digest; finite, synchronised channels; calibration validity and uncertainty; case coverage; pre-approved guarded limits; independent witness and prerequisite dispositions. A trusted external signature verifier is required. Reviewer names, local hashes and self-reported success confer no acceptance. Simulated or synthetic data cannot impersonate physical rig records.', '',
        '`passed-records` means an authenticated, internally consistent measurement screen is ready for an independent decision. All release flags remain false, and this package has no authority to issue physical or manufacturing release.', '',
        '[Complete task graph and procedures](study.json.gz) · [Unexecuted evidence template](evidence-template.json) · [Unexecuted raw template](raw-template.json) · [Source and payload receipt](manifest.json)', '', 'References:', '']
    lines += [f"- [{r['id']}]({r['url']}): {r['scope']}" for r in result['references']]
    return '\n'.join(lines) + '\n'


def publish(output=OUTPUT):
    result = study(); output = Path(output)
    if output.is_symlink() or (output.exists() and any(p.is_symlink() or p.name not in FILES | {'manifest.json'} for p in output.iterdir())):
        raise ValueError('unowned or linked qualification packet')
    raw = encoded(result)
    if len(raw) > MAX_RAW:
        raise ValueError('bounded qualification packet required')
    bundle, measurements = template()
    if binding() != result['binding']:
        raise ValueError('qualification source changed before publication')
    output.mkdir(parents=True, exist_ok=True)
    (output / 'study.json.gz').write_bytes(gzip.compress(raw, mtime=0))
    (output / 'README.md').write_text(readme(result))
    for name, value in [('evidence-template.json', bundle), ('raw-template.json', measurements)]:
        (output / name).write_text(json.dumps(value, sort_keys=True, indent=2) + '\n')
    manifest = dict(schema=SCHEMA, source_sha256=result['binding']['source_sha256'],
        binding_sha256=result['binding_sha256'], content_sha256=result['content_sha256'],
        files_sha256={name: file_hash(output / name) for name in sorted(FILES)},
        raw_bytes=len(raw), **FLAGS)
    (output / 'manifest.json').write_text(json.dumps(manifest, sort_keys=True, indent=2) + '\n')
    verify(output)
    return manifest


def verify(output=OUTPUT):
    output = Path(output)
    if output.is_symlink() or set(p.name for p in output.iterdir()) != FILES | {'manifest.json'} or any(p.is_symlink() for p in output.iterdir()):
        raise ValueError('qualification packet inventory differs')
    manifest = json.loads((output / 'manifest.json').read_bytes())
    if manifest['schema'] != SCHEMA or any(manifest.get(k) is not False for k in FLAGS):
        raise ValueError('qualification release claim forbidden')
    if set(manifest['files_sha256']) != FILES or any(file_hash(output / name) != digest for name, digest in manifest['files_sha256'].items()):
        raise ValueError('qualification payload checksum differs')
    if manifest['source_sha256'] != source_snapshot():
        raise ValueError('qualification sources are stale')
    compressed = (output / 'study.json.gz').read_bytes()
    if len(compressed) > MAX_RAW:
        raise ValueError('compressed qualification budget exceeded')
    with gzip.GzipFile(fileobj=io.BytesIO(compressed)) as stream:
        raw = stream.read(MAX_RAW + 1)
    expected = study()
    if (len(raw) > MAX_RAW or len(raw) != manifest['raw_bytes'] or raw != encoded(expected)
            or manifest['binding_sha256'] != expected['binding_sha256']
            or manifest['content_sha256'] != expected['content_sha256']):
        raise ValueError('qualification recalculation differs')
    if (output / 'README.md').read_text() != readme(expected):
        raise ValueError('qualification presentation differs')
    bundle, measurements = template()
    if any(json.loads((output / name).read_text()) != value for name, value in [('evidence-template.json', bundle), ('raw-template.json', measurements)]):
        raise ValueError('qualification unexecuted templates differ')
    return manifest


def read_summary(output=OUTPUT):
    verify(output); result = study()
    return dict(schema=SCHEMA, binding_sha256=result['binding_sha256'],
        **result['coverage'], status=result['status'], **FLAGS)


def main(argv=None):
    """Standalone importer. The CLI has no trust anchor and cannot accept evidence."""
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='action', required=True)
    for action in ('publish', 'verify', 'summary'):
        command = sub.add_parser(action); command.add_argument('--output', type=Path, default=OUTPUT)
    command = sub.add_parser('assess')
    command.add_argument('--protocol', required=True)
    command.add_argument('--bundle', required=True, type=Path)
    command.add_argument('--raw-root', required=True, type=Path)
    command.add_argument('--output', type=Path)
    args = parser.parse_args(argv)
    if args.action == 'assess':
        if args.bundle.is_symlink() or args.bundle.stat().st_size > MAX_RAW:
            parser.error('bounded regular evidence bundle required')
        result = assess_evidence(args.protocol, _json(args.bundle.read_bytes()), args.raw_root)
        # The command deliberately has no local self-approval or simulated-physical option.
        text = json.dumps(result, sort_keys=True, indent=2) + '\n'
        if args.output:
            if args.output.resolve() in {args.bundle.resolve(), (args.raw_root / result['raw_file']['name']).resolve()}:
                parser.error('assessment may not overwrite imported evidence')
            args.output.write_text(text)
        print(text, end='')
        return 1 if result['state'] == 'failed' else 2 if result['state'] == 'hold' else 0
    function = {'publish': publish, 'verify': verify, 'summary': read_summary}[args.action]
    print(json.dumps(function(args.output), sort_keys=True, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
