#!/usr/bin/env python3
"""Bound one door-opening route request to the retained counted handoff.

This is an input gate for later CAD work. It does not position or qualify a door.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from math import dist, isfinite
from pathlib import Path

from engineering.station_rail.common import encoded, identity


ROOT = Path(__file__).resolve().parents[2]
HANDOFF = ROOT / 'docs/design-engine/v07-execution/door-interface-handoff.json'
OUTPUT = ROOT / 'docs/design-engine/v07-execution/door-route-request.json'
HANDOFF_SHA256 = 'd9879607cbd6d55d35deaf013f3ad76551fa0d2f853147b30fb1d2d3ca362314'
PHYSICAL_CHILD = '907da3680bcbd01ffe1223652443e4e34a9f581e201385917a99edf4150bd90a'
INSTALLED_CHILD = '17ce7a724fcd661e5c4f195cde19b68377c0968e4e7d7dbb5d6ac7c8d4074ad4'
GUIDE = 'body/door-guide-rail'
BELT = 'body/door-belt'


def compile_request(handoff: dict, raw: bytes) -> dict:
    """Create an immutable request; unknown locations remain unknown."""
    if sha256(raw).hexdigest() != HANDOFF_SHA256:
        raise ValueError('Selected sealed one-opening handoff bytes differ')
    if handoff != json.loads(raw):
        raise ValueError('Handoff object differs from pinned bytes')
    if (handoff.get('schema') != 'osr-v07-door-interface-handoff/1'
            or handoff.get('handoff_id') != identity({k: v for k, v in handoff.items() if k != 'handoff_id'})
            or handoff.get('physical_candidate_id') != PHYSICAL_CHILD
            or handoff.get('installed_candidate_id') != INSTALLED_CHILD
            or handoff.get('opening') != 'car-0/door-0'
            or any(handoff.get(k) is not False for k in
                   ('installed_geometry_verified', 'manufacturing_release',
                    'engineering_accepted', 'physical_accepted'))):
        raise ValueError('Selected unaccepted child handoff required')
    parts = handoff['parts']
    if (len(parts) != 74 or len({p['part_id'] for p in parts}) != 74
            or sum(p['quantity_per_opening'] for p in parts) != 694
            or any(p['installed_transform_m'] is not None or p['controlled_mating_datums'] is not None
                   or p['approved_inspection_limits'] is not None for p in parts)):
        raise ValueError('Counted, unlocated opening differs')
    by_id = {p['part_id']: p for p in parts}
    guide, belt = by_id[GUIDE], by_id[BELT]
    if (guide['stock'].get('kind') != 'cut-length' or guide['stock'].get('length_m') != 2.9
            or belt['stock'].get('kind') != 'cut-length' or belt['stock'].get('length_m') != 5.8
            or guide['quantity_per_opening'] != 1 or belt['quantity_per_opening'] != 1):
        raise ValueError('Guide and belt stock definitions differ')
    frame = handoff['opening_frame']
    if (frame['accepted_installation_datum'] is not None
            or frame['car_local_x_m'] != -4.5 or frame['clear_width_m'] != 1.4
            or frame['proposed_slide_m'] != 0.72):
        raise ValueError('Opening frame proposal differs')
    motion_span = frame['clear_width_m'] + 2 * frame['proposed_slide_m']
    request = dict(
        schema='osr-v07-one-opening-route-request/1',
        generator_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
        source_handoff_id=handoff['handoff_id'], source_handoff_sha256=HANDOFF_SHA256,
        physical_candidate_id=PHYSICAL_CHILD, installed_candidate_id=INSTALLED_CHILD,
        installed_evaluation_id=handoff['installed_evaluation_id'], opening='car-0/door-0',
        part_count=74, piece_count=694,
        component_definitions=[dict(part_id=p['part_id'],
                                    component_definition_id=p['component_definition_id'],
                                    quantity_per_opening=p['quantity_per_opening'])
                               for p in sorted(parts, key=lambda p: p['part_id'])],
        frame=dict(name='car-local metres', proposed_centre_x_m=-4.5,
                   accepted_header_to_body_datum=None),
        nominal_motion_control=dict(clear_width_m=frame['clear_width_m'],
                                    leaf_slide_each_side_m=frame['proposed_slide_m'],
                                    opening_plus_two_slides_m=motion_span,
                                    guide_stock_minus_nominal_span_m=round(2.9 - motion_span, 9),
                                    meaning='Arithmetic proposal only; stops, end allowances and fit are unknown'),
        guide=dict(part_id=GUIDE, component_definition_id=guide['component_definition_id'],
                   stock_cut_length_m=2.9, display_proxy_m=2.0,
                   required_geometry='full straight guide in car-local frame',
                   installed_start_m=None, installed_end_m=None,
                   mounting_datums=None, end_stops=None, clearance_sweep=None,
                   removal_path=None),
        belt=dict(part_id=BELT, component_definition_id=belt['component_definition_id'],
                  stock_cut_length_m=5.8, display_proxy_m=2.0,
                  required_geometry='closed loop about identified pulleys in car-local frame',
                  pulley_axis_datums=None, closed_pitch_path_m=None,
                  tensioner_range_m=None, clearance_sweep=None,
                  removal_path=None),
        other_required_interfaces=['header-to-body mounting and load path',
                                   'carriage and bearing fits', 'drive and idler shaft datums',
                                   'leaf/stop motion and crush clearances',
                                   'sensor/wiring/protection and emergency release'],
        ready_for_native_assembly=False, installed_geometry_verified=False,
        manufacturing_release=False, engineering_accepted=False,
        physical_accepted=False)
    request['request_id'] = identity(request)
    return request


def assess_proposal(request: dict, proposal: dict) -> list[str]:
    """Reject false fit claims and return missing inputs for a proposed route.

    Passing this intake never grants installed or physical acceptance.
    """
    raw = HANDOFF.read_bytes()
    if request != compile_request(json.loads(raw), raw):
        raise ValueError('Route request differs from pinned child handoff')
    if not isinstance(proposal, dict):
        raise ValueError('Route proposal object required')
    for key in ('request_id', 'physical_candidate_id', 'installed_candidate_id',
                'installed_evaluation_id', 'opening'):
        if proposal.get(key) != request[key]:
            raise ValueError(f'Route proposal {key} differs')
    if proposal.get('schema') != 'osr-v07-one-opening-route-proposal/1':
        raise ValueError('Explicit route proposal schema required')
    if any(proposal.get(k) is not False for k in
           ('ready_for_native_assembly', 'installed_geometry_verified', 'manufacturing_release',
            'engineering_accepted', 'physical_accepted')):
        raise ValueError('Route intake cannot grant engineering or physical acceptance')
    guide = proposal.get('guide', {})
    belt = proposal.get('belt', {})
    if not isinstance(guide, dict) or not isinstance(belt, dict):
        raise ValueError('Guide and belt route objects required')
    if guide.get('geometry') not in (None, 'straight-full-guide'):
        raise ValueError('Guide requires its full straight extent')
    extent = guide.get('extent_m')
    if extent is not None and (type(extent) not in (int, float) or not isfinite(extent)
                               or extent != request['guide']['stock_cut_length_m']):
        raise ValueError('Guide extent must match selected 2.9 m stock; revise candidate for a trimmed guide')
    start, end = guide.get('installed_start_m'), guide.get('installed_end_m')
    if start is not None or end is not None:
        if (not all(isinstance(point, list) and len(point) == 3 and
                    all(type(x) in (int, float) and isfinite(x) for x in point)
                    for point in (start, end))
                or extent is None or abs(dist(start, end) - extent) > 1e-6):
            raise ValueError('Full guide endpoints must span the declared stock in car-local metres')
    if belt.get('geometry') not in (None, 'closed-loop'):
        raise ValueError('Belt cut length cannot be treated as a straight span')
    if belt.get('straight_extent_m') is not None:
        raise ValueError('Belt stock cut length is not an installed straight extent')
    path = belt.get('closed_pitch_path_m')
    if path is not None:
        if (not isinstance(path, list) or len(path) < 4
                or any(not isinstance(point, list) or len(point) != 3
                       or any(type(x) not in (int, float) or not isfinite(x) for x in point)
                       for point in path)
                or path[0] != path[-1]):
            raise ValueError('Belt requires a finite closed car-local pitch path')
    holds = []
    if guide.get('geometry') is None or extent is None or start is None or end is None:
        holds.append('full 2.9 m guide route and car-local placement')
    if guide.get('mounting_datums') is None or guide.get('removal_path') is None:
        holds.append('controlled guide mounts and removal clearance')
    if belt.get('geometry') is None or path is None:
        holds.append('closed belt pitch path and pulley axes')
    if belt.get('pulley_axis_datums') is None or belt.get('tensioner_range_m') is None:
        holds.append('pulley/tensioner datums and duty')
    holds.append('independent motion, clearance, electrical and physical review')
    return holds


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    operation = parser.add_mutually_exclusive_group()
    operation.add_argument('--check', action='store_true')
    operation.add_argument('--proposal', type=Path, help='Assess one proposed route without accepting it')
    args = parser.parse_args()
    raw = HANDOFF.read_bytes()
    request = compile_request(json.loads(raw), raw)
    value = encoded(request)
    if args.proposal:
        if args.proposal.stat().st_size > 1024 * 1024:
            parser.error('route proposal exceeds 1 MiB')
        holds = assess_proposal(request, json.loads(args.proposal.read_bytes()))
        print(json.dumps(dict(request_id=request['request_id'],
                              ready_for_native_assembly=False, holds=holds), sort_keys=True))
    elif args.check:
        if not OUTPUT.is_file() or OUTPUT.read_bytes() != value:
            parser.error('door route request differs from selected handoff')
        print('current: door route request')
    else:
        OUTPUT.write_bytes(value)
        print('wrote door route request')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
