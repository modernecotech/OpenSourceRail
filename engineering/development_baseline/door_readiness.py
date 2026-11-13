"""Source-checked, read-only status for the v0.7 door research child."""
from hashlib import sha256
import json
from pathlib import Path

from engineering.station_rail.common import identity
from tools.automation import v07_door_pack_preflight as contract


PACKET = 'docs/design-engine/v07-execution/door-pack-preflight.json'
PACKET_SHA = '154b32468a77a1d12b7d85ed6c53bfe3a120a64356bd61e7db2e4958284f97fa'


def summary(root: Path) -> dict:
    """Refuse stale or mixed inputs before showing the module's open gates."""
    root = Path(root)

    def checked(relative: str, expected: str) -> bytes:
        raw = (root / relative).read_bytes()
        if sha256(raw).hexdigest() != expected:
            raise ValueError('Door readiness source changed: ' + relative)
        return raw

    raw = checked(PACKET, PACKET_SHA)
    packet = json.loads(raw)
    checked('docs/design-engine/v07-execution/door-interface-handoff.json', packet['source_handoff_sha256'])
    route = json.loads(checked('docs/design-engine/v07-execution/door-route-request.json', packet['source_route_sha256']))
    checked('tools/automation/v07_door_pack_preflight.py', packet['generator_sha256'])
    if (packet.get('schema') != 'osr-v07-door-pack-preflight/1'
            or packet.get('preflight_id') != identity({k: v for k, v in packet.items() if k != 'preflight_id'})
            or packet.get('source_handoff_sha256') != contract.HANDOFF_SHA
            or packet.get('source_route_sha256') != contract.ROUTE_SHA
            or packet.get('physical_component_candidate_id') != contract.PHYSICAL_CHILD
            or packet.get('installed_body_candidate_id') != contract.INSTALLED_CHILD
            or packet.get('part_types') != 74
            or packet.get('pieces_per_opening') != 694
            or route.get('physical_candidate_id') != contract.PHYSICAL_CHILD
            or route.get('installed_candidate_id') != packet.get('installed_body_candidate_id')
            or route.get('installed_evaluation_id') != packet.get('installed_body_evaluation_id')
            or route.get('ready_for_native_assembly') is not False
            or any(packet.get(key) is not False for key in
                   ('pack_ready', 'native_erp_admitted', 'installed_geometry_verified',
                    'engineering_accepted', 'physical_accepted', 'manufacturing_release'))):
        raise ValueError('Door readiness candidate or authority differs')
    return {
        'schema': 'osr-v07-door-readiness-view/1',
        'physical_component_candidate_id': packet['physical_component_candidate_id'],
        'installed_body_candidate_id': packet['installed_body_candidate_id'],
        'preflight_id': packet['preflight_id'],
        'route_request_id': route['request_id'],
        'opening': packet['opening'],
        'guide_stock_cut_length_m': route['guide']['stock_cut_length_m'],
        'belt_stock_cut_length_m': route['belt']['stock_cut_length_m'],
        'route_datums_missing': route['guide']['mounting_datums'] is None or route['belt']['pulley_axis_datums'] is None,
        'unverified_stage_inputs': packet['unverified_stage_inputs'],
        'unnamed_part_document_count': len(packet['unnamed_part_document_ids']),
        'unnamed_assembly_document_count': len(packet['unnamed_assembly_document_ids']),
        'unnamed_conversion_count': len(packet['unnamed_conversion_ids']),
        'purchased_types': packet['purchased_types'],
        'purchased_pieces_per_opening': packet['purchased_pieces_per_opening'],
        'controlled_payloads_verified': packet['controlled_payloads_verified'],
        'conversion_values_verified': packet['conversion_values_verified'],
        'review_compiler_still_required': packet['review_compiler_still_required'],
        'pack_ready': False,
        'native_erp_admitted': False,
        'physical_accepted': False,
    }
