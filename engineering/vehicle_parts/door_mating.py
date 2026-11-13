"""Held one-opening door mating screen from the counted v0.7 child.

This records the dimensions and transforms needed for a real assembly. Stock
lengths and a proposed opening centre are never substituted for installed datums.
"""
from hashlib import sha256
import json
from math import dist, fsum, isfinite, sqrt
from pathlib import Path

from engineering.station_rail.common import digest, encoded, identity
from engineering.vehicle_parts import ROOT
from tools.automation import v07_door_route as route

PRODUCER = 'engineering/vehicle_parts/door_mating.py'
_LOADED_SHA = digest(__file__)
HARDWARE = {
    'body/door-guide-rail': 1,
    'body/door-belt': 1,
    'body/door-drive-pulley': 1,
    'body/door-idler-pulley': 1,
    'body/door-pulley-bearing': 2,
    'body/door-belt-tensioner': 1,
    'body/door-leaf-belt-clamp': 2,
    'body/door-carriage': 4,
    'body/door-carriage-roller': 8,
    'body/door-roller-axle': 8,
    'body/door-roller-bearing': 8,
    'body/door-roller-circlip': 16,
    'body/door-stop': 4,
    'body/door-bottom-guide': 4,
    'body/door-guide-bolt': 24,
    'body/door-guide-nut': 24,
    'body/door-guide-washer': 48,
    'services/door-body-loom': 1,
    'services/door-trailing-loom': 2,
    'services/door-drag-chain': 2,
    'services/door-bond': 2,
    'services/door-motor': 1,
    'services/door-controller': 1,
    'services/door-motor-fixing-bolt': 4,
    'services/door-motor-fixing-nut': 4,
    'services/door-motor-fixing-washer': 8,
}


def _current_inputs(root):
    root = Path(root).resolve()
    if digest(root/PRODUCER) != _LOADED_SHA:
        raise ValueError('Loaded door mating screen changed; restart caller')
    handoff_raw = (root/route.HANDOFF.relative_to(route.ROOT)).read_bytes()
    handoff = json.loads(handoff_raw)
    request = route.compile_request(handoff, handoff_raw)
    request_raw = (root/route.OUTPUT.relative_to(route.ROOT)).read_bytes()
    if request_raw != encoded(request):
        raise ValueError('Committed one-opening route request differs from handoff')
    for name, expected in handoff['source_sha256'].items():
        path = Path(name)
        if (path.is_absolute() or '..' in path.parts or (root/path).is_symlink()
                or digest(root/path) != expected):
            raise ValueError('One-opening child source changed: '+name)
    parts = {p['part_id']: p for p in handoff['parts']}
    if any(parts[name]['quantity_per_opening'] != count for name, count in HARDWARE.items()):
        raise ValueError('Door joint, bearing, fixing or stop count changed')
    return handoff, request, handoff_raw, request_raw


def _polyline_length(path):
    if path is None:
        return None
    segments = [dist(a, b) for a, b in zip(path, path[1:])]
    if any(not isfinite(length) or length <= 0 for length in segments):
        raise ValueError('Closed belt path has a degenerate segment')
    if len({tuple(p) for p in path[:-1]}) < 3:
        raise ValueError('Closed belt path needs three distinct route stations')
    return fsum(segments)


def _pulley_axes(value, path, parts):
    if value is None:
        return None
    if (not isinstance(value, list) or len(value) != 2
            or any(not isinstance(x, dict) or not isinstance(x.get('part_id'), str) for x in value)
            or {x['part_id'] for x in value}
            != {'body/door-drive-pulley', 'body/door-idler-pulley'}):
        raise ValueError('Exactly one drive and one idler pulley axis required')
    def vector(v):
        return (isinstance(v, list) and len(v) == 3 and
                all(type(x) in (int, float) and isfinite(x) for x in v))
    for row in value:
        if (not vector(row.get('origin_car_m')) or not vector(row.get('axis_unit_car'))
                or type(row.get('pitch_radius_m')) not in (int, float)
                or not isfinite(row['pitch_radius_m']) or row['pitch_radius_m'] <= 0):
            raise ValueError('Finite pulley centre, unit axis and positive pitch radius required')
        axis = row['axis_unit_car']
        if abs(sqrt(fsum(x*x for x in axis))-1.) > 1e-6:
            raise ValueError('Pulley axis must be unit length')
        envelope = parts[row['part_id']]['stock']['size_m']
        if row['pitch_radius_m'] > min(envelope[:2])/2:
            raise ValueError('Pulley pitch radius exceeds counted stock envelope')
    a,b=value;axis=a['axis_unit_car'];other=b['axis_unit_car']
    dot=lambda x,y:fsum(u*v for u,v in zip(x,y))
    delta=[y-x for x,y in zip(a['origin_car_m'],b['origin_car_m'])]
    if abs(abs(dot(axis,other))-1.) > 1e-6 or abs(dot(delta,axis)) > 1e-6:
        raise ValueError('Pulley axes must be parallel and share the belt plane')
    if dist(a['origin_car_m'],b['origin_car_m']) <= a['pitch_radius_m']+b['pitch_radius_m']:
        raise ValueError('Counted pulley pitch circles overlap')
    if path is not None:
        for point in path:
            offset=[x-y for x,y in zip(point,a['origin_car_m'])]
            if abs(dot(offset,axis)) > 1e-6:
                raise ValueError('Closed belt path must lie in the pulley pitch plane')
        drop=max(range(3),key=lambda i:abs(axis[i]))
        keep=[i for i in range(3) if i!=drop]
        projected=[(point[keep[0]],point[keep[1]]) for point in path]
        for pulley in value:
            x,y=(pulley['origin_car_m'][i] for i in keep)
            inside=False
            for (ax,ay),(bx,by) in zip(projected,projected[1:]):
                if (ay>y)!=(by>y) and x < ax+(bx-ax)*(y-ay)/(by-ay):
                    inside=not inside
            if not inside:
                raise ValueError('Both pulley axes must lie inside the proposed closed belt route')
    return value


def evaluate(*, proposal=None):
    """Return a source-bound held assessment; no inferred installed acceptance."""
    handoff, request, handoff_raw, request_raw = _current_inputs(ROOT)
    route_holds = route.assess_proposal(request, proposal) if proposal is not None else []
    guide_path = None if proposal is None else proposal.get('guide', {})
    belt_path = None if proposal is None else proposal.get('belt', {})
    guide = None
    if guide_path is not None and guide_path.get('installed_start_m') is not None:
        start, end = guide_path['installed_start_m'], guide_path['installed_end_m']
        if abs(end[0]-start[0]) < 2.9-1e-6 or abs(end[1]-start[1]) > 1e-6 or abs(end[2]-start[2]) > 1e-6:
            raise ValueError('Guide must span the full 2.9 m along car-local longitudinal x')
        guide = dict(start_car_m=start, end_car_m=end, straight_extent_m=dist(start, end),
                     status='proposed-uncontrolled')
    path = None if belt_path is None else belt_path.get('closed_pitch_path_m')
    belt_length = _polyline_length(path)
    parts = {p['part_id']:p for p in handoff['parts']}
    pulley_axes = _pulley_axes(None if belt_path is None else belt_path.get('pulley_axis_datums'),path,parts)
    frames = {name:dict(parent='car-local',transform_from_parent=None,
                        controlled_source=None,status='unlocated') for name in
              ('body-aperture','header','guide','drive-pulley-axis','idler-pulley-axis',
               'left-leaf','right-leaf','motor-reducer','sensor-carrier')}
    frames['car-local'] = dict(parent=None,
        transform_from_parent=dict(translation_m=[0.,0.,0.],rotation_matrix=[[1.,0.,0.],[0.,1.,0.],[0.,0.,1.]]),
        units='m',axes='x longitudinal, y lateral, z vertical',status='declared-reference-frame')
    controls = request['nominal_motion_control']
    required = [
        'Controlled header-to-body transform, mount holes, joint and load path',
        'Full guide profile, carriage fits, fixing locations and 2.9 m placement',
        'Drive/idler shaft axes, pulley pitch radii, centres, belt pitch and tension range',
        'Closed belt wrap and clamp positions for two moving leaves',
        'Four stops, four carriages, eight roller/bearing/axle sets and retention fits',
        'Finite leaf, seal, end-stop, cable and tool/removal swept clearances',
        'Motor/reducer torque, electrical protection, interlocks and manual release',
        'Motor thermal duty and any needed cooling hardware, routing and service flexibility',
        'Controlled drawings, inspection limits and physical measurements',
    ]
    value = dict(schema='osr-v07-door-mating-screen/1',
        physical_candidate_id=request['physical_candidate_id'],
        installed_candidate_id=request['installed_candidate_id'],
        installed_evaluation_id=request['installed_evaluation_id'],
        opening=request['opening'],route_request_id=request['request_id'],
        proposal_id=None if proposal is None else identity(proposal),
        source_sha256={**handoff['source_sha256'],
            route.HANDOFF.relative_to(route.ROOT).as_posix():sha256(handoff_raw).hexdigest(),
            route.OUTPUT.relative_to(route.ROOT).as_posix():sha256(request_raw).hexdigest(),
            'tools/automation/v07_door_route.py':digest(route.__file__),
            PRODUCER:_LOADED_SHA},
        frames=frames,proposed_opening_centre_car_x_m=request['frame']['proposed_centre_x_m'],
        accepted_header_to_body_transform=None,
        all_parts_per_opening={name:parts[name]['quantity_per_opening'] for name in sorted(parts)},
        pieces_per_opening=sum(parts[name]['quantity_per_opening'] for name in parts),
        checked_hardware_per_opening=dict(HARDWARE),motor_cooling_hardware_count=None,
        stock=dict(header_backplate_length_m=parts['body/door-header-backplate']['stock']['size_m'][0],
                   guide_cut_length_m=request['guide']['stock_cut_length_m'],
                   belt_cut_length_m=request['belt']['stock_cut_length_m'],
                   belt_pitch_length_m=None),
        nominal_control=dict(clear_opening_m=controls['clear_width_m'],
            slide_per_leaf_m=controls['leaf_slide_each_side_m'],
            opening_plus_slides_m=controls['opening_plus_two_slides_m'],
            guide_stock_minus_nominal_span_m=controls['guide_stock_minus_nominal_span_m'],
            scope='Arithmetic envelope only; actual stops, carriages, clamp travel and fit unverified'),
        proposed_guide=guide,proposed_pulley_axes=pulley_axes,
        proposed_belt_pitch_polyline_m=belt_length,
        belt_stock_minus_polyline_m=None if belt_length is None else
            request['belt']['stock_cut_length_m']-belt_length,
        belt_stock_to_pitch_fit='unknown: pulley pitch, tooth count, tension, stretch and allowable splice are unverified',
        required_datums_and_checks=required,route_intake_holds=route_holds,
        proposed_geometry_installed_in_child=False,
        new_physical_child_required_before_adopting_proposal=proposal is not None,
        selected_reference_changed=False,
        installed_geometry_verified=False,ready_for_native_assembly=False,
        engineering_accepted=False,physical_accepted=False,manufacturing_release=False)
    value['assessment_id'] = identity(value)
    return value
