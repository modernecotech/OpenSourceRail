#!/usr/bin/env python3
"""Compile a source-bound door interface and custody handoff without accepting fit."""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
from collections import Counter
from pathlib import Path

from engineering.station_rail.common import digest, encoded, identity
from engineering.vehicle_installation import model
from engineering.vehicle_installation.export import validate_declared_sources
from engineering.vehicle_parts import door_module

ROOT = Path(__file__).resolve().parents[2]
SOURCE = 'tools/automation/door_interface_handoff.py'
OPENING = 'car-0/door-0'
PURCHASED = {'buy-standard', 'buy-qualified'}
SELECTED_INSTALLED_CANDIDATE = '17ce7a724fcd661e5c4f195cde19b68377c0968e4e7d7dbb5d6ac7c8d4074ad4'
SELECTED_INSTALLED_EVALUATION = '123896d4014fd00bc11fc755f132aa8769ebfd217f06d6f34b2fe8342d62c4f1'
SELECTED_INSTALLATION_SHA256 = 'c199da74a00e7c42a2d10fb57f3c9765ac953df8038acf7b55d8d687a213c015'
SELECTED_ATTACHMENT_SHA256 = 'a6e8d1f7d5f59290bf45f8e31a570e4cbe27b846ed04cd8ade3d2e8c4dd9e2b0'


def compile_handoff(module: dict, attachment: dict, installation: dict, policy: dict) -> dict:
    validate_declared_sources(module.get('source_sha256'),ROOT)
    validate_declared_sources(installation.get('source_sha256'),ROOT)
    if (installation.get('schema') != 'osr-vehicle-installation/1'
            or installation.get('candidate_id') != identity(installation['physical_definition'])
            or installation.get('evaluation_id') != identity({k: v for k, v in installation.items() if k != 'evaluation_id'})
            or installation.get('parent_candidate_id') != module.get('candidate_id')
            or not installation.get('source_sha256')):
        raise ValueError('Exact sealed installed child required')
    if attachment.get('schema') != 'osr-door-opening-proposed-layout-attachment/1':
        raise ValueError('Sealed one-opening attachment required')
    if attachment.get('attachment_id') != identity({k: v for k, v in attachment.items() if k != 'attachment_id'}):
        raise ValueError('Door attachment seal differs')
    if (attachment.get('opening') != OPENING or attachment.get('parent_candidate_id') != module.get('candidate_id')
            or attachment.get('candidate_id') != installation['candidate_id']
            or attachment.get('evaluation_id') != installation['evaluation_id']
            or attachment.get('source_sha256') != installation['source_sha256']
            or attachment.get('source_bundle_id') != module.get('source_bundle_id')
            or attachment.get('source_bundle_evaluation_id') != module.get('source_evaluation_id')
            or attachment.get('source_door_module_sha256') != module['source_sha256'][door_module.PRODUCER]):
        raise ValueError('Door attachment and manufacturing candidate differ')
    if (module.get('module_id') != identity({k: v for k, v in module.items() if k != 'module_id'})
            or attachment.get('accepted_installed_transform_m') is not None
            or any(part.get('installed_transform_m') is not None for part in module['parts'])):
        raise ValueError('Unaccepted, sealed door module required')
    layout = policy['layout']
    if layout['door_centres_local_x_m'][0] != -4.5 or layout['door_clear_width_m'] != 1.4:
        raise ValueError('Named one-opening layout assumption changed')
    audited = {row['part_id']: row for row in attachment['component_audit']}
    if len(audited) != len(module['parts']) or set(audited) != {row['id'] for row in module['parts']}:
        raise ValueError('Attachment part audit is incomplete')
    rows=[]
    for part in sorted(module['parts'], key=lambda row: row['id']):
        if audited[part['id']]['component_definition_matches'] is not True or audited[part['id']]['expanded_count'] != part['quantity_per_train']:
            raise ValueError('Door part definition or count differs')
        rows.append(dict(part_id=part['id'],component_definition_id=part['component_definition_id'],
            assembly_id=part['assembly_id'],quantity_per_opening=part['quantity_per_opening'],
            make_buy=part['make_buy'],stock=part['stock'],source_ids=part['source_ids'],
            installed_transform_m=None,controlled_mating_datums=None,
            approved_inspection_limits=None))
    counts=Counter(row['make_buy'] for row in rows)
    pieces=Counter()
    for row in rows: pieces[row['make_buy']]+=row['quantity_per_opening']
    if (len(rows),sum(pieces.values()),sum(pieces[k] for k in PURCHASED)) != (74,694,597):
        raise ValueError('Source door custody counts changed; review scope again')
    result=dict(schema='osr-v07-door-interface-handoff/1',physical_candidate_id=module['candidate_id'],
        installed_candidate_id=installation['candidate_id'],installed_evaluation_id=installation['evaluation_id'],
        module_id=module['module_id'],attachment_id=attachment['attachment_id'],opening=OPENING,
        opening_frame=dict(car_local_x_m=layout['door_centres_local_x_m'][0],
            clear_width_m=layout['door_clear_width_m'],proposed_slide_m=layout['door_slide_m'],
            proposed_tool_radius_m=layout['door_tool_clearance_m'],accepted_installation_datum=None),
        type_counts=dict(sorted(counts.items())),piece_counts=dict(sorted(pieces.items())),
        purchased_piece_count=597,parts=rows,
        required_interfaces=[
            'Header-to-body datums, holes, joint, load path and access hatch',
            'Guide section, carriage/bearing fits, holes, retention and 2.9 m routed extent',
            'Pulley centres, belt pitch/path/tension and 5.8 m loop sweep',
            'Motor/reducer shaft and bolt pattern, torque/thermal duty and removal clearance',
            'Finished leaf/seal/end-stop shapes, motion and tool/removal sweeps',
            'Sensor datums, wiring/protection and controlled inspection limits',
            'Purchased receipt and lot/serial custody with latest accepted incoming QA'],
        source_sha256={**module['source_sha256'],**installation['source_sha256'],
            'engineering/vehicle_installation/policy.json': digest(ROOT / model.POLICY),
            SOURCE: digest(ROOT / SOURCE)},
        installed_geometry_verified=False,manufacturing_release=False,
        engineering_accepted=False,physical_accepted=False)
    result['handoff_id']=identity(result)
    return result


def main() -> int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--attachment',required=True,type=Path)
    parser.add_argument('--installation',required=True,type=Path)
    parser.add_argument('--output',required=True,type=Path)
    args=parser.parse_args()
    if args.output.exists():parser.error('output must be a new file')
    attachment_raw=args.attachment.read_bytes()
    if hashlib.sha256(attachment_raw).hexdigest() != SELECTED_ATTACHMENT_SHA256:
        parser.error('one-opening attachment bytes differ from selected immutable packet')
    attachment=json.loads(attachment_raw)
    validate_declared_sources(attachment['source_sha256'],ROOT)
    if args.installation.stat().st_size > 32 * 1024 * 1024:
        parser.error('installation archive exceeds 32 MiB')
    if hashlib.sha256(args.installation.read_bytes()).hexdigest() != SELECTED_INSTALLATION_SHA256:
        parser.error('installed packet bytes differ from selected immutable packet')
    with gzip.open(args.installation,'rb') as stream:
        raw=stream.read(64 * 1024 * 1024 + 1)
    if len(raw) > 64 * 1024 * 1024:
        parser.error('installation record exceeds 64 MiB')
    installation=json.loads(raw)
    if (installation.get('candidate_id') != SELECTED_INSTALLED_CANDIDATE
            or installation.get('evaluation_id') != SELECTED_INSTALLED_EVALUATION):
        parser.error('selected installed identity differs')
    validate_declared_sources(installation['source_sha256'],ROOT)
    result=compile_handoff(door_module.build(ROOT),attachment,installation,model.policy(ROOT))
    validate_declared_sources(result['source_sha256'],ROOT)
    args.output.write_bytes(encoded(result))
    print(result['handoff_id'])
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
