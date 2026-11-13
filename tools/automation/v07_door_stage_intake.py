#!/usr/bin/env python3
"""Read-only intake for the selected v0.7 door delivery stages.

An intake result is a review aid, never a controlled document review, native
ERP admission, manufacturing release or physical qualification.
"""
from __future__ import annotations

import argparse
import gzip
from hashlib import sha256
import io
import json
from pathlib import Path
import re

from engineering.pilot_delivery import model
from engineering.railway_closure.bundle import combine
from engineering.station_rail.common import identity
from tools.automation import v07_door_pack_preflight as door

MAX_INPUT_BYTES = 128 * 1024**2
STAGES = door.STAGES
HEX_ID = re.compile(r'[0-9a-f]{64}\Z')


def _sha(path: Path) -> str:
    h = sha256()
    with path.open('rb') as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def _packet(path: Path) -> tuple[dict, str]:
    if (any(p.is_symlink() for p in (path,*path.parents))
            or not path.is_file() or path.stat().st_size > MAX_INPUT_BYTES):
        raise ValueError('Ordinary bounded packet file required')
    raw = path.read_bytes()
    if path.suffix == '.gz':
        with gzip.GzipFile(fileobj=io.BytesIO(raw)) as stream:
            raw = stream.read(MAX_INPUT_BYTES + 1)
    if len(raw) > MAX_INPUT_BYTES:
        raise ValueError('Decompressed packet exceeds intake budget')
    value = json.loads(raw)
    if not isinstance(value, dict):
        raise ValueError('Object packet required')
    return value, _sha(path)


def _sources(packet: dict, root: Path) -> None:
    sources = packet.get('source_sha256')
    if not isinstance(sources, dict) or not sources:
        raise ValueError('Nonempty source hash map required')
    for name, expected in sources.items():
        if (not isinstance(name, str) or not isinstance(expected, str)
                or len(expected) != 64 or any(c not in '0123456789abcdef' for c in expected)):
            raise ValueError('Source path and SHA-256 required')
        rel = Path(name)
        if rel.is_absolute() or '..' in rel.parts or not rel.parts:
            raise ValueError('Source path escapes repository')
        path = root / rel
        if (any(p.is_symlink() for p in [path, *[p for p in path.parents if p != root and root in p.parents]])
                or not path.is_file() or _sha(path) != expected):
            raise ValueError('Source bytes differ: ' + name)


def _seal(packet: dict, key='evaluation_id') -> None:
    if packet.get(key) != identity({k: v for k, v in packet.items() if k != key}):
        raise ValueError('Unsealed '+key)


def _study(path: Path, root: Path, packet_hashes: dict | None = None) -> tuple[dict, str]:
    value, digest = _packet(path)
    if packet_hashes is not None:
        packet_hashes['study'] = digest
    if value.get('schema') != 'osr-railway-closure-study/1':
        raise ValueError('Railway closure study schema required')
    _seal(value, 'study_id'); _sources(value, root)
    if value.get('body_candidate_id') != door.INSTALLED_CHILD:
        raise ValueError('Closure study belongs to another installed child')
    door._no_authority(value)
    return value, digest


def _body(path: Path, study: dict, root: Path, packet_hashes: dict | None = None) -> tuple[dict, str]:
    body, digest = _packet(path)
    if packet_hashes is not None:
        packet_hashes['body'] = digest
    if body.get('schema') != 'osr-vehicle-installation/1':
        raise ValueError('Installed body schema required')
    _seal(body); _sources(body, root)
    if (body.get('candidate_id') != door.INSTALLED_CHILD
            or body.get('candidate_id') != study.get('body_candidate_id')
            or body.get('evaluation_id') != study.get('body_evaluation_id')
            or identity(body['physical_definition']) != body['candidate_id']):
        raise ValueError('Installed body candidate or evaluation differs')
    installed, civil, bundle = (study[name] for name in ('installed','civil','bundle'))
    for packet in (installed, civil, bundle): _seal(packet)
    for packet in (installed, civil): _sources(packet, root)
    if bundle != combine(installed, civil):
        raise ValueError('Mixed installed/civil canonical bundle')
    if (installed['vehicle_candidate_id'] != body['candidate_id']
            or installed['body_evaluation_id'] != body['evaluation_id']
            or bundle['body_evaluation_id'] != body['evaluation_id']):
        raise ValueError('Installed/civil bundle belongs to another body')
    door._no_authority(body)
    return body, digest


def intake(*, study_path: Path | None = None, body_path: Path | None = None,
           service_id: str | None = None, proposal_path: Path | None = None,
           root: Path = door.ROOT) -> dict:
    return _intake(study_path=study_path, body_path=body_path,
                   service_id=service_id, proposal_path=proposal_path, root=root)


def _intake(*, study_path: Path | None = None, body_path: Path | None = None,
            service_id: str | None = None, proposal_path: Path | None = None,
            root: Path = door.ROOT, _batch_common: dict | None = None) -> dict:
    root = Path(root).resolve()
    rows = []; packet_hashes = {}; first = None; reason = None

    def stage(name, supplied, check):
        nonlocal first, reason
        if first is not None:
            rows.append(dict(stage=name, status='blocked-by-earlier-stage'))
            return None
        if not supplied:
            first = name; reason = 'Stage input missing'
            rows.append(dict(stage=name, status='missing', reason=reason))
            return None
        try:
            value = check()
        except (OSError, ValueError, KeyError, TypeError, IndexError, json.JSONDecodeError) as exc:
            first = name; reason = str(exc)
            rows.append(dict(stage=name, status='held', reason=reason))
            return None
        rows.append(dict(stage=name, status='source-verified'))
        return value

    def study_check():
        value, digest = (_batch_common['study'], _batch_common['study_sha256']) if _batch_common else _study(Path(study_path), root, packet_hashes)
        packet_hashes['study'] = digest
        return value

    study = stage(STAGES[0], study_path is not None, study_check)

    def body_check():
        body, digest = (_batch_common['body'], _batch_common['body_sha256']) if _batch_common else _body(Path(body_path), study, root, packet_hashes)
        packet_hashes['body'] = digest
        return body

    body = stage(STAGES[1], body_path is not None, body_check)

    def service_check():
        if not isinstance(service_id, str) or len(service_id) != 64:
            raise ValueError('Explicit nominal service evaluation ID required')
        records = [r for r in study['records'] if r.get('experiment') == 'nominal'
                   and r.get('service', {}).get('evaluation_id') == service_id]
        if len(records) != 1:
            raise ValueError('One matching nominal service/fleet record required')
        record = records[0]; service = record['service']; _seal(service)
        if (service.get('candidate_id') != study['bundle']['candidate_id']
                or record['request']['candidate_id'] != service['candidate_id']
                or record['result']['candidate_id'] != service['candidate_id']
                or type(service.get('total_trainsets')) is not int
                or service['total_trainsets'] != service['active_trainsets'] + service['spare_trainsets']):
            raise ValueError('Mixed service candidate or fleet')
        return record

    record = stage(STAGES[2], service_id is not None, service_check)

    def cost_check():
        checked, source_map = model._input_validation(study, body, service_id, root)
        if checked != record:
            raise ValueError('Cost record differs from selected nominal service')
        return model._binding(study, body, record), source_map

    cost_context = stage(STAGES[3], record is not None, cost_check)

    def proposal_check():
        proposal, digest = _packet(Path(proposal_path)); packet_hashes['proposal'] = digest
        door.preflight(proposal=proposal)
        model.validate_proposal(proposal)
        binding, source_map = cost_context
        if proposal.get('identities') != binding:
            raise ValueError('Delivery proposal belongs to another child or evaluation')
        if proposal.get('source_sha256') != source_map:
            raise ValueError('Delivery proposal source bytes differ')
        return proposal

    stage(STAGES[4], proposal_path is not None, proposal_check)
    report = dict(schema='osr-v07-door-stage-intake/1',
                  producer_sha256=_sha(Path(__file__)),
                  physical_component_candidate_id=door.PHYSICAL_CHILD,
                  installed_body_candidate_id=door.INSTALLED_CHILD,
                  packet_sha256=packet_hashes, stages=rows,
                  first_unverified_stage=first, first_unverified_reason=reason,
                  stage_source_authentication_complete=first is None,
                  controlled_document_review_complete=False,
                  pack_ready=False, native_erp_admitted=False,
                  engineering_accepted=False, physical_accepted=False,
                  manufacturing_release=False)
    report['intake_id'] = identity(report)
    return report


def _unchanged_input(path: Path, expected: str) -> None:
    if (any(p.is_symlink() for p in (path, *path.parents))
            or not path.is_file() or path.stat().st_size > MAX_INPUT_BYTES
            or _sha(path) != expected):
        raise ValueError('Batch input changed during intake: ' + str(path))


def intake_many(*, study_path: Path, body_path: Path,
                service_ids: list[str] | tuple[str, ...],
                root: Path = door.ROOT) -> dict:
    """Reuse common authentication across a bounded explicit service set.

    Each service still runs the existing full pilot-delivery cost validation.
    Shared packet/source bytes are checked again after the final report; any
    drift refuses the whole batch. No service is selected or promoted.
    """
    if (not isinstance(service_ids, (list, tuple)) or not 1 <= len(service_ids) <= 12
            or any(not isinstance(s, str) or HEX_ID.fullmatch(s) is None for s in service_ids)
            or len(set(service_ids)) != len(service_ids)):
        raise ValueError('One to twelve distinct explicit service evaluation IDs required')
    root = Path(root).resolve(); study_path = Path(study_path); body_path = Path(body_path)
    study, study_sha = _study(study_path, root)
    body, body_sha = _body(body_path, study, root)
    source_map = model._source_map(study, body, root)
    common = dict(study=study, body=body, study_sha256=study_sha,
                  body_sha256=body_sha)
    reports = [_intake(study_path=study_path, body_path=body_path,
                      service_id=s, root=root, _batch_common=common)
               for s in service_ids]
    _unchanged_input(study_path, study_sha)
    _unchanged_input(body_path, body_sha)
    if model._source_map(study, body, root) != source_map:
        raise ValueError('Batch sources changed during intake')
    # The original stage intake also refuses source-path symlinks. Recheck
    # those paths after processing, not just the content digests above.
    for packet in (study, body, study['installed'], study['civil']):
        _sources(packet, root)
    # Legacy intake IDs do not encode the requested service and can coincide
    # when reports have the same stage outcomes. Keep each legacy report intact
    # while binding its batch case ID to the explicit service evaluation.
    cases = []
    for service_id, report in zip(service_ids, reports, strict=True):
        case = dict(service_evaluation_id=service_id, intake_report=report)
        case['report_id'] = identity(case)
        cases.append(case)
    value = dict(schema='osr-v07-door-stage-batch/1',
                 producer_sha256=_sha(Path(__file__)),
                 packet_sha256=dict(study=study_sha, body=body_sha),
                 service_evaluation_ids=list(service_ids),
                 reports=cases, selected_service_id=None,
                 all_cost_stages_source_verified=all(
                     row['stages'][3]['status'] == 'source-verified' for row in reports),
                 controlled_document_review_complete=False,
                 pack_ready=False, native_erp_admitted=False,
                 engineering_accepted=False, physical_accepted=False,
                 manufacturing_release=False)
    value['batch_id'] = identity(value)
    return value


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--study',type=Path)
    parser.add_argument('--body',type=Path)
    service = parser.add_mutually_exclusive_group()
    service.add_argument('--service-id')
    service.add_argument('--service-ids', help='Comma-separated explicit nominal service IDs, at most twelve')
    parser.add_argument('--proposal',type=Path)
    parser.add_argument('--root',type=Path,default=door.ROOT)
    args=parser.parse_args(argv)
    if args.service_ids is not None:
        if args.study is None or args.body is None or args.proposal is not None:
            parser.error('Batch intake requires study and body, without a proposal')
        value = intake_many(study_path=args.study, body_path=args.body,
                            service_ids=args.service_ids.split(','), root=args.root)
    else:
        value = intake(study_path=args.study,body_path=args.body,
                       service_id=args.service_id,proposal_path=args.proposal,root=args.root)
    print(json.dumps(value,sort_keys=True,indent=2))
    return 0


if __name__=='__main__':
    raise SystemExit(main())
