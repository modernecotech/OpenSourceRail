"""Source-bound electrical interface screen for the held v0.7 door child.

Counted hardware and stock allowances are recorded. This does not infer a
power supply, wiring design, safety circuit, or accepted operating duty.
"""

from hashlib import sha256
import json
from pathlib import Path

from engineering.station_rail.common import digest, encoded, identity
from engineering.vehicle_parts import ROOT
from tools.automation import v07_door_route as route


PRODUCER = 'engineering/vehicle_parts/door_electrical.py'
_LOADED_SHA = digest(__file__)
REQUIRED_COUNTS = {
    'services/door-body-loom': 1,
    'services/door-bond': 2,
    'services/door-closed-switch': 2,
    'services/door-controller': 1,
    'services/door-drag-chain': 2,
    'services/door-encoder': 1,
    'services/door-light-curtain': 1,
    'services/door-lock-switch': 2,
    'services/door-motor': 1,
    'services/door-release-monitor': 2,
    'services/door-request': 2,
    'services/door-sensitive-edge': 2,
    'services/door-sounder': 1,
    'services/door-trailing-loom': 2,
    'body/door-emergency-cable': 2,
    'body/door-emergency-handle': 2,
    'body/door-manual-isolator': 1,
    'body/door-release-shaft': 1,
}


def _inputs(root: Path):
    root = root.resolve()
    if digest(root / PRODUCER) != _LOADED_SHA:
        raise ValueError('Loaded door electrical screen changed; restart caller')
    handoff_path = root / route.HANDOFF.relative_to(route.ROOT)
    raw = handoff_path.read_bytes()
    handoff = json.loads(raw)
    request = route.compile_request(handoff, raw)
    request_path = root / route.OUTPUT.relative_to(route.ROOT)
    request_raw = request_path.read_bytes()
    if request_raw != encoded(request):
        raise ValueError('Committed one-opening route request differs from handoff')
    for name, expected in handoff['source_sha256'].items():
        relative = Path(name)
        source = root / relative
        if (relative.is_absolute() or '..' in relative.parts or source.is_symlink()
                or digest(source) != expected):
            raise ValueError('One-opening child source changed: ' + name)
    return handoff, request, raw, request_raw


def evaluate():
    """Assess one selected opening without promoting it to installation evidence."""
    handoff, request, raw, request_raw = _inputs(ROOT)
    parts = {row['part_id']: row for row in handoff['parts']}
    electrical = {name: row['quantity_per_opening'] for name, row in parts.items()
                  if row['assembly_id'] == 'services/door-electrical'}
    if (len(electrical) != 23 or sum(electrical.values()) != 249
            or any(parts[name]['quantity_per_opening'] != count
                   for name, count in REQUIRED_COUNTS.items())):
        raise ValueError('Selected door electrical or release hardware counts changed')
    stock = {}
    for name in ('services/door-body-loom', 'services/door-trailing-loom',
                 'services/door-bond', 'services/door-sensitive-edge'):
        row = parts[name]
        if row['stock']['kind'] != 'cut-length':
            raise ValueError('Selected door electrical stock form changed: ' + name)
        stock[name] = dict(quantity_per_opening=row['quantity_per_opening'],
                           stock_length_each_m=row['stock']['length_m'],
                           installed_route_length_m=None)
    if parts['body/door-manual-isolator']['stock']['description'] != (
            'Key-operated mechanical latch; electrical state switch excluded'):
        raise ValueError('Manual release boundary differs')
    value = dict(
        schema='osr-v07-door-electrical-interface-screen/1',
        physical_candidate_id=request['physical_candidate_id'],
        installed_candidate_id=request['installed_candidate_id'],
        installed_evaluation_id=request['installed_evaluation_id'],
        opening=request['opening'], route_request_id=request['request_id'],
        source_sha256={**handoff['source_sha256'],
            route.HANDOFF.relative_to(route.ROOT).as_posix(): sha256(raw).hexdigest(),
            route.OUTPUT.relative_to(route.ROOT).as_posix(): sha256(request_raw).hexdigest(),
            'tools/automation/v07_door_route.py': digest(route.__file__),
            PRODUCER: _LOADED_SHA},
        electrical_parts_per_opening=dict(sorted(electrical.items())),
        electrical_part_types_per_opening=len(electrical),
        electrical_pieces_per_opening=sum(electrical.values()),
        electrical_pieces_per_six_car_train=12 * sum(electrical.values()),
        mechanical_release_parts_per_opening={
            name: parts[name]['quantity_per_opening']
            for name in sorted(REQUIRED_COUNTS) if name.startswith('body/')},
        stock_allowances=stock,
        known_functional_hardware={
            'motor_and_controller': ['services/door-motor', 'services/door-controller'],
            'closed_and_locked_detection': ['services/door-closed-switch', 'services/door-lock-switch'],
            'obstruction_detection': ['services/door-sensitive-edge', 'services/door-light-curtain'],
            'release_monitoring': ['services/door-release-monitor'],
            'manual_mechanical_release': ['body/door-manual-isolator',
                                          'body/door-emergency-cable',
                                          'body/door-emergency-handle'],
        },
        electrical_isolator_count=None,
        circuit_protection_device_count=None,
        electrical_state_switch_for_manual_release_count=None,
        supply_voltage_v=None, peak_motor_current_a=None,
        steady_motor_current_a=None, peak_motor_torque_nm=None,
        repeated_duty_loss_w=None, emergency_energy_wh=None,
        conductor_cross_sections_mm2=None, installed_wire_routes_m=None,
        interlock_logic_verified=False, obstruction_function_verified=False,
        emergency_release_verified=False, degraded_operation_verified=False,
        holds=[
            'Define door electrical supply, independent service battery and rescue energy under repeated duty',
            'Define and count electrical isolation, overcurrent protection, earthing and manual-release state sensing',
            'Specify motor/reducer torque-speed, current, voltage, losses and cooling for the selected mechanism',
            'Define loom conductor sizes, segregated circuits, connectors, bond lugs, flex bend and installed routes',
            'Prove closed/locked, obstruction, release and train interlock logic with fault and degraded cases',
            'Measure manual release force, emergency operation and access on an installed opening',
        ],
        ready_for_native_electrical=False, installed_geometry_verified=False,
        manufacturing_release=False, engineering_accepted=False,
        physical_accepted=False,
    )
    value['assessment_id'] = identity(value)
    return value
