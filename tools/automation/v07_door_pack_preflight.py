#!/usr/bin/env python3
"""Check same-child door pack inputs before controlled review or native ERP work."""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path

from engineering.station_rail.common import encoded, identity


ROOT = Path(__file__).resolve().parents[2]
HANDOFF = ROOT / 'docs/design-engine/v07-execution/door-interface-handoff.json'
ROUTE = ROOT / 'docs/design-engine/v07-execution/door-route-request.json'
OUTPUT = ROOT / 'docs/design-engine/v07-execution/door-pack-preflight.json'
HANDOFF_SHA = 'd9879607cbd6d55d35deaf013f3ad76551fa0d2f853147b30fb1d2d3ca362314'
ROUTE_SHA = '577b11af4a7ff8785d274ecec0bc020b2f4bc11740bf02c81bfa83396f1fc922'
PHYSICAL_CHILD = '907da3680bcbd01ffe1223652443e4e34a9f581e201385917a99edf4150bd90a'
INSTALLED_CHILD = '17ce7a724fcd661e5c4f195cde19b68377c0968e4e7d7dbb5d6ac7c8d4074ad4'
DOCUMENT_TYPES = ('drawing', 'inspection', 'routing')
ASSEMBLIES = ('body/door-opening', 'services/door-electrical', 'door-operator')
IDENTITIES = {'candidate_id', 'bundle_evaluation_id', 'study_id', 'engineering_revision',
              'body_candidate_id', 'source_body_bundle_id', 'installed_component_candidate_id',
              'installed_mass_evaluation_id', 'civil_candidate_id', 'civil_evaluation_id',
              'service_evaluation_id', 'cost_evaluation_id', 'lifecycle_evaluation_id'}
STAGES = ('same-child closure study', 'installed/civil canonical bundle',
          'nominal service and fleet', 'core and full-scope cost',
          'sealed delivery proposal')
FORBIDDEN_AUTHORITY = {'operating_release', 'movement_authority',
                       'ready_for_native_assembly', 'automatic_order_release',
                       'selected_reference_changed', 'installation_accepted',
                       'transactions_performed', 'construction_release',
                       'engineering_accepted', 'physical_accepted',
                       'manufacturing_release', 'installed_geometry_verified',
                       'native_erp_admitted', 'pack_ready'}


def _input(path: Path, expected: str) -> dict:
    raw = path.read_bytes()
    if sha256(raw).hexdigest() != expected:
        raise ValueError(f'Selected input bytes differ: {path.name}')
    return json.loads(raw)


def _sealed(value: dict, key: str) -> None:
    if not isinstance(value, dict) or value.get(key) != identity({k: v for k, v in value.items() if k != key}):
        raise ValueError(f'Sealed {key} required')


def _no_authority(value) -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            if (key in FORBIDDEN_AUTHORITY or key.endswith('_approved')) and item is not None and item is not False:
                raise ValueError('Preflight proposal cannot grant release or movement authority')
            _no_authority(item)
    elif isinstance(value, list):
        for item in value:
            _no_authority(item)


def _maps(documents: dict | None, expected: set[str]) -> tuple[list[str], list[str]]:
    if documents is None:
        return sorted(expected), []
    if documents.get('schema') != 'osr-controlled-research-documents/1':
        raise ValueError('Controlled research document index required')
    rows = documents.get('components')
    if not isinstance(rows, list):
        raise ValueError('Component document mappings required')
    found = {}
    for row in rows:
        if not isinstance(row, dict) or set(row) != {'part_id', *DOCUMENT_TYPES}:
            raise ValueError('Each mapped part needs drawing, inspection and routing')
        name = row['part_id']
        if name in found or name not in expected:
            raise ValueError('Duplicate or foreign door part document mapping')
        if any(not isinstance(row[k], str) or not row[k] for k in DOCUMENT_TYPES):
            raise ValueError('Named controlled sidecar paths required')
        found[name] = row
    return sorted(expected - found.keys()), sorted(found)


def preflight(*, proposal: dict | None = None, documents: dict | None = None,
              conversions: dict | None = None) -> dict:
    """Inventory inputs. The final review compiler still authenticates all files."""
    handoff = _input(HANDOFF, HANDOFF_SHA)
    route = _input(ROUTE, ROUTE_SHA)
    _sealed(handoff, 'handoff_id')
    _sealed(route, 'request_id')
    if (handoff.get('schema') != 'osr-v07-door-interface-handoff/1'
            or route.get('schema') != 'osr-v07-one-opening-route-request/1'
            or handoff.get('physical_candidate_id') != PHYSICAL_CHILD
            or handoff.get('installed_candidate_id') != INSTALLED_CHILD
            or route.get('physical_candidate_id') != PHYSICAL_CHILD
            or route.get('installed_candidate_id') != INSTALLED_CHILD
            or route.get('installed_evaluation_id') != handoff.get('installed_evaluation_id')
            or route.get('source_handoff_sha256') != HANDOFF_SHA
            or route.get('source_handoff_id') != handoff['handoff_id']):
        raise ValueError('Door route and handoff candidates differ')
    parts = {p['part_id']: p for p in handoff['parts']}
    route_parts = {p['part_id']: p for p in route['component_definitions']}
    if (len(parts) != 74 or len(route_parts) != 74 or set(parts) != set(route_parts)
            or sum(p['quantity_per_opening'] for p in parts.values()) != 694
            or any(p['component_definition_id'] != route_parts[name]['component_definition_id']
                   or p['quantity_per_opening'] != route_parts[name]['quantity_per_opening']
                   for name, p in parts.items())):
        raise ValueError('Counted one-opening component definitions differ')
    purchased = {name for name, p in parts.items()
                 if p['make_buy'] in ('buy-qualified', 'buy-standard')}
    if len(purchased) != 35 or sum(parts[name]['quantity_per_opening'] for name in purchased) != 597:
        raise ValueError('Purchased child count or make/buy route differs')
    if any(handoff.get(k) is not False or route.get(k) is not False for k in
           ('engineering_accepted', 'physical_accepted', 'manufacturing_release')):
        raise ValueError('Research inputs cannot grant acceptance')

    if proposal is not None:
        _sealed(proposal, 'proposal_id')
        _no_authority(proposal)
        identities = proposal.get('identities')
        if (proposal.get('schema') != 'osr-pilot-delivery-proposal/1'
                or proposal.get('status') != 'DRAFT'
                or not isinstance(identities, dict) or set(identities) != IDENTITIES
                or identities['body_candidate_id'] != INSTALLED_CHILD
                or identities['engineering_revision'] != handoff['installed_evaluation_id']
                or any(proposal.get(k) is not False for k in
                       ('engineering_accepted', 'physical_accepted', 'manufacturing_release'))):
            raise ValueError('Same-child unapproved delivery proposal required')
        rows = proposal.get('items')
        if not isinstance(rows, list) or len({p['id'] for p in rows}) != len(rows):
            raise ValueError('Unique source proposal parts required')
        by_id = {p['id']: p for p in rows}
        if not set(parts) <= set(by_id):
            raise ValueError('Door proposal omits selected component definitions')
        for name, part in parts.items():
            row = by_id[name]
            if (row.get('source_component_candidate_id') != PHYSICAL_CHILD
                    or row.get('component_definition_id') != part['component_definition_id']
                    or row.get('quantity_per_train') != 12 * part['quantity_per_opening']
                    or row.get('make_buy') != part['make_buy']):
                raise ValueError('Mixed door candidate, part, count or make/buy route')
    if documents is not None and proposal is None:
        raise ValueError('Document index needs a same-child delivery proposal')
    if conversions is not None and proposal is None:
        raise ValueError('Conversions need a same-child delivery proposal')
    if proposal is not None and documents is not None and documents.get('identities') != proposal['identities']:
        raise ValueError('Document identities differ from delivery proposal')
    missing_docs, supplied_docs = _maps(documents, set(parts))
    assembly_rows = [] if documents is None else documents.get('assemblies', [])
    if not isinstance(assembly_rows, list) or any(not isinstance(row, dict) for row in assembly_rows):
        raise ValueError('Assembly document mappings must be a list')
    assembly_docs = {r.get('assembly_id'): r for r in assembly_rows}
    if documents is not None and (len(assembly_docs) != len(assembly_rows)
                                  or set(assembly_docs) - set(ASSEMBLIES)):
        raise ValueError('Duplicate or foreign door assembly document mapping')
    missing_assemblies = sorted(set(ASSEMBLIES) - set(assembly_docs))
    for row in assembly_docs.values():
        if set(row) != {'assembly_id', *DOCUMENT_TYPES} or any(not isinstance(row[k], str) or not row[k] for k in DOCUMENT_TYPES):
            raise ValueError('Parent and child assemblies need three controlled sidecars')
    if conversions is not None and not isinstance(conversions, dict):
        raise ValueError('Reviewed part conversion map required')
    if conversions is not None and set(conversions) - set(parts):
        raise ValueError('Foreign door conversion supplied')
    missing_conversions = sorted(set(parts) - set(conversions or {}))
    result = dict(schema='osr-v07-door-pack-preflight/1',
                  generator_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
                  source_handoff_sha256=HANDOFF_SHA, source_route_sha256=ROUTE_SHA,
                  physical_component_candidate_id=PHYSICAL_CHILD,
                  installed_body_candidate_id=INSTALLED_CHILD,
                  installed_body_evaluation_id=handoff['installed_evaluation_id'],
                  opening=handoff['opening'], part_types=74, pieces_per_opening=694,
                  purchased_types=35, purchased_pieces_per_opening=597,
                  proposal_shape_supplied=proposal is not None,
                  unverified_stage_inputs=list(STAGES),
                  unnamed_part_document_ids=missing_docs,
                  named_part_document_ids=supplied_docs,
                  unnamed_assembly_document_ids=missing_assemblies,
                  unnamed_conversion_ids=missing_conversions,
                  stage_source_authentication_required=True,
                  controlled_payloads_verified=False,
                  conversion_values_verified=False,
                  review_compiler_still_required=True,
                  pack_ready=False,
                  native_erp_admitted=False, installed_geometry_verified=False,
                  engineering_accepted=False, physical_accepted=False,
                  manufacturing_release=False)
    result['preflight_id'] = identity(result)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    parser.add_argument('--proposal', type=Path)
    parser.add_argument('--documents', type=Path)
    parser.add_argument('--conversions', type=Path)
    args = parser.parse_args()
    if args.check and any((args.proposal, args.documents, args.conversions)):
        parser.error('--check inspects the committed no-input inventory only')
    def load(path):
        if path is None:
            return None
        if path.stat().st_size > 32 * 1024 * 1024:
            parser.error('preflight input exceeds 32 MiB')
        return json.loads(path.read_bytes())
    report = preflight(proposal=load(args.proposal), documents=load(args.documents),
                       conversions=load(args.conversions))
    data = encoded(report)
    if args.check:
        if not OUTPUT.is_file() or OUTPUT.read_bytes() != data:
            parser.error('committed door pack preflight differs')
        print('current: door pack preflight')
    elif any((args.proposal, args.documents, args.conversions)):
        print(json.dumps(dict(preflight_id=report['preflight_id'],
                              unverified_stage_inputs=report['unverified_stage_inputs'],
                              unnamed_part_documents=len(report['unnamed_part_document_ids']),
                              unnamed_assembly_documents=report['unnamed_assembly_document_ids'],
                              unnamed_conversions=len(report['unnamed_conversion_ids']),
                              pack_ready=False,
                              native_erp_admitted=False), sort_keys=True))
    else:
        OUTPUT.write_bytes(data)
        print('wrote door pack preflight')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
