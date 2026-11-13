"""Authenticate an explicit installed body for a closure research run.

The closure coordinator's downstream system is a powered-wheel research
configuration. Supplying a body does not select that system, admit its door
installation, or transfer physical approval from the body.
"""
from __future__ import annotations

import gzip
from hashlib import sha256
import io
import json
from pathlib import Path
import re
import stat

from engineering.station_rail.common import identity
from engineering.vehicle_installation.export import validate_declared_sources

MAX_COMPRESSED_BYTES = 32 * 1024**2
MAX_JSON_BYTES = 128 * 1024**2
HEXDIGEST = re.compile(r'[0-9a-f]{64}\Z')
RESEARCH_FLAGS = ('engineering_accepted', 'physical_accepted', 'manufacturing_release',
                  'operating_release', 'movement_authority', 'selected_reference_changed')
CASES = ('low', 'base', 'high')


def file_sha256(path: Path) -> str:
    h = sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def _required_shape(body: dict) -> None:
    """Reject incomplete input before exporting or launching native workers."""
    physical = body['physical_definition']
    if (not isinstance(physical, dict)
            or not isinstance(physical.get('track_interface'), dict)
            or not isinstance(body.get('parent_bundle_id'), str)
            or HEXDIGEST.fullmatch(body['parent_bundle_id']) is None):
        raise ValueError('Installed body track interface and source bundle required')
    for name in ('parts', 'patterns', 'materials', 'mass_scenarios'):
        if not isinstance(body.get(name), list) or not body[name]:
            raise ValueError('Nonempty installed body ' + name + ' required')
    for name in ('source_component_types', 'proposed_component_types', 'total_occurrences'):
        if type(body.get(name)) is not int or body[name] < 1:
            raise ValueError('Positive installed body ' + name + ' required')
    for name in ('nominal_part_mass_kg', 'direct_parts_process_usd'):
        values = body.get(name)
        if not isinstance(values, dict) or any(case not in values for case in CASES):
            raise ValueError('Installed body low/base/high ' + name + ' required')
    if (not isinstance(body.get('interface_screens'), dict)
            or not isinstance(body.get('policy'), dict)
            or not isinstance(body['policy'].get('evaluation'), dict)
            or not isinstance(body['policy']['evaluation'].get('unlocated_installation_reserve_kg'), dict)
            or any(case not in body['policy']['evaluation']['unlocated_installation_reserve_kg'] for case in CASES)):
        raise ValueError('Installed body interface and mass-reserve policy required')
    for scenario in body['mass_scenarios']:
        if (not isinstance(scenario, dict)
                or scenario.get('case') not in CASES
                or any(name not in scenario for name in ('name', 'train_mass_kg', 'CG_m',
                    'inertia_about_CG_kg_m2', 'lateral_acceleration_m_s2'))
                or not isinstance(scenario.get('axles'), list)
                or len(scenario['axles']) != 24
                or any(not isinstance(a, dict) or 'x_m' not in a or 'vertical_force_N' not in a
                       for a in scenario['axles'])):
            raise ValueError('Complete 24-axle installed body load cases required')


def load(path: Path, *, expected_candidate_id: str, root: Path) -> tuple[dict, dict]:
    """Read a bounded, sealed, current-source body with an explicit identity."""
    path = Path(path).absolute()
    if (not isinstance(expected_candidate_id, str)
            or HEXDIGEST.fullmatch(expected_candidate_id) is None):
        raise ValueError('Exact expected body candidate SHA-256 required')
    if any(p.is_symlink() for p in (path, *path.parents)):
        raise ValueError('Body input must not traverse a symlink')
    try:
        size = path.stat().st_size
        if not stat.S_ISREG(path.stat().st_mode) or size > MAX_COMPRESSED_BYTES:
            raise ValueError('Bounded ordinary compressed body input required')
    except OSError as exc:
        raise ValueError('Body input unavailable') from exc
    before = file_sha256(path)
    try:
        with gzip.GzipFile(fileobj=io.BytesIO(path.read_bytes())) as stream:
            raw = stream.read(MAX_JSON_BYTES + 1)
        if len(raw) > MAX_JSON_BYTES:
            raise ValueError('Decompressed body input exceeds budget')
        body = json.loads(raw)
    except (OSError, EOFError, json.JSONDecodeError) as exc:
        raise ValueError('Invalid compressed body input') from exc
    if not isinstance(body, dict) or body.get('schema') != 'osr-vehicle-installation/1':
        raise ValueError('Installed body schema required')
    if (body.get('candidate_id') != expected_candidate_id
            or identity(body.get('physical_definition')) != expected_candidate_id
            or body.get('evaluation_id') != identity({k: v for k, v in body.items() if k != 'evaluation_id'})):
        raise ValueError('Body physical or evaluation identity differs')
    if any(body.get(flag) is not False for flag in RESEARCH_FLAGS):
        raise ValueError('Body input must retain explicit research-only flags')
    _required_shape(body)
    validate_declared_sources(body.get('source_sha256'), root)
    if file_sha256(path) != before:
        raise ValueError('Body input changed during authentication')
    receipt = dict(schema='osr-railway-closure-body-input/1',
                   input_sha256=before, input_bytes=size,
                   body_candidate_id=body['candidate_id'],
                   body_evaluation_id=body['evaluation_id'],
                   body_physical_schema=body['physical_definition'].get('schema'),
                   source_count=len(body['source_sha256']),
                   closure_system_architecture='powered-wheel-research',
                   selected_reference_changed=False,
                   engineering_accepted=False, physical_accepted=False)
    receipt['receipt_id'] = identity(receipt)
    return body, receipt


def recheck(path: Path, receipt: dict) -> None:
    if file_sha256(Path(path)) != receipt['input_sha256']:
        raise ValueError('Body input changed during closure run')
