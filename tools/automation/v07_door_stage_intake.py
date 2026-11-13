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

from engineering.pilot_delivery import model
from engineering.railway_closure.bundle import combine
from engineering.station_rail.common import identity
from tools.automation import v07_door_pack_preflight as door

MAX_INPUT_BYTES = 128 * 1024**2
STAGES = door.STAGES


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


def intake(*, study_path: Path | None = None, body_path: Path | None = None,
           service_id: str | None = None, proposal_path: Path | None = None,
           root: Path = door.ROOT) -> dict:
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
        value, digest = _packet(Path(study_path)); packet_hashes['study'] = digest
        if value.get('schema') != 'osr-railway-closure-study/1':
            raise ValueError('Railway closure study schema required')
        _seal(value, 'study_id'); _sources(value, root)
        if value.get('body_candidate_id') != door.INSTALLED_CHILD:
            raise ValueError('Closure study belongs to another installed child')
        door._no_authority(value)
        return value

    study = stage(STAGES[0], study_path is not None, study_check)

    def body_check():
        body, digest = _packet(Path(body_path)); packet_hashes['body'] = digest
        if body.get('schema') != 'osr-vehicle-installation/1':
            raise ValueError('Installed body schema required')
        _seal(body); _sources(body, root)
        if (body.get('candidate_id') != door.INSTALLED_CHILD
                or body.get('candidate_id') != study.get('body_candidate_id')
                or body.get('evaluation_id') != study.get('body_evaluation_id')
                or identity(body['physical_definition']) != body['candidate_id']):
            raise ValueError('Installed body candidate or evaluation differs')
        installed, civil, bundle = (study[name] for name in ('installed','civil','bundle'))
        for packet in (installed, civil, bundle):_seal(packet)
        for packet in (installed, civil):_sources(packet, root)
        if bundle != combine(installed, civil):
            raise ValueError('Mixed installed/civil canonical bundle')
        if (installed['vehicle_candidate_id'] != body['candidate_id']
                or installed['body_evaluation_id'] != body['evaluation_id']
                or bundle['body_evaluation_id'] != body['evaluation_id']):
            raise ValueError('Installed/civil bundle belongs to another body')
        door._no_authority(body)
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


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--study',type=Path)
    parser.add_argument('--body',type=Path)
    parser.add_argument('--service-id')
    parser.add_argument('--proposal',type=Path)
    parser.add_argument('--root',type=Path,default=door.ROOT)
    args=parser.parse_args(argv)
    print(json.dumps(intake(study_path=args.study,body_path=args.body,
        service_id=args.service_id,proposal_path=args.proposal,root=args.root),sort_keys=True,indent=2))
    return 0


if __name__=='__main__':
    raise SystemExit(main())
