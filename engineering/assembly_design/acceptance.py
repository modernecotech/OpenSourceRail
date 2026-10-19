"""Authenticate externally signed measurements; never issue a railway release.

Trust is explicitly configured by an operator outside an evidence submission.
Ed25519 verifies authorship/integrity, not the truth of a measurement. A
separate authorised reviewer signs the exact measurement and disposition.
OpenSSL is used to avoid installing a second cryptographic implementation.
"""
import base64
from datetime import date
import json
import math
from pathlib import Path
import re
import subprocess
import tempfile

from engineering.twin_workflow import core


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False,
                      allow_nan=False).encode('utf-8')


def digest(value):
    from hashlib import sha256
    return sha256(canonical(value)).hexdigest()


def signed(envelope, trust, role, *, today=None):
    """Verify an Ed25519 envelope with a pre-pinned key and restricted role."""
    today = today or date.today().isoformat()
    date.fromisoformat(today)
    if envelope.get('algorithm') != 'Ed25519':
        raise ValueError('Ed25519 signature required')
    key = trust.get(envelope.get('key_id'))
    if not key or key.get('revoked') is not False or role not in key.get('roles', []):
        raise ValueError('untrusted, revoked or unauthorised signing key')
    if not date.fromisoformat(key['valid_from']) <= date.fromisoformat(today) <= date.fromisoformat(key['valid_until']):
        raise ValueError('signing key outside configured validity')
    try:
        signature = base64.b64decode(envelope['signature'], validate=True)
        if len(signature) != 64:
            raise ValueError('invalid signature length')
        message = canonical(envelope['payload'])
        if len(message) > 2_000_000:
            raise ValueError('signed record size limit')
        with tempfile.TemporaryDirectory(prefix='osr-verify-') as temp:
            folder = Path(temp)
            (folder/'public.pem').write_text(key['public_key_pem'])
            (folder/'signature').write_bytes(signature)
            (folder/'message').write_bytes(message)
            result = subprocess.run(['openssl', 'pkeyutl', '-verify', '-pubin', '-inkey',
                str(folder/'public.pem'), '-rawin', '-in', str(folder/'message'),
                '-sigfile', str(folder/'signature')], capture_output=True, timeout=10)
        if result.returncode:
            raise ValueError('signature verification failed')
    except (KeyError, TypeError, json.JSONDecodeError) as exc:
        raise ValueError('malformed signed record') from exc
    return envelope['payload']


def _artifact(root, descriptor):
    name = descriptor['path']
    path = Path(root)/name
    if not isinstance(name, str) or not name or Path(name).is_absolute() or '..' in Path(name).parts:
        raise ValueError('unsafe evidence path')
    if path.is_symlink() or not path.resolve().is_relative_to(Path(root).resolve()) or not path.is_file():
        raise ValueError('missing or escaping evidence file')
    if not re.fullmatch('[0-9a-f]{64}', descriptor['sha256']) or core.sha(path) != descriptor['sha256']:
        raise ValueError('raw evidence hash differs')


def ingest(record, calibration, review, trust, root, expected, *, today=None):
    """Validate identity, raw bytes, calibration and a separate signed review.

    expected comes from the controlled unit/traveller, not from the submission.
    No trust keys, method adoption or release authority are inferred from names.
    """
    measured = signed(record, trust, 'measurement', today=today)
    calibrated = signed(calibration, trust, 'calibration', today=today)
    disposition = signed(review, trust, 'review', today=today)
    if record['key_id'] == review['key_id']:
        raise ValueError('measurement author cannot be its independent reviewer')
    required = ('architecture', 'unit_id', 'unit_revision', 'serial', 'interface_revision', 'method', 'standard_edition')
    if any(not expected.get(k) or measured.get(k) != expected[k] for k in required):
        raise ValueError('measurement applicability differs from controlled traveller')
    if not measured.get('fixture_id') or not measured.get('fixture_revision') or not measured.get('conditions'):
        raise ValueError('fixture revision and operating conditions required')
    if not measured.get('raw_files') or not measured.get('measurements'):
        raise ValueError('raw data and measured quantities required')
    at = date.fromisoformat(measured['measured_date'])
    now = date.fromisoformat(today or date.today().isoformat())
    if at > now:
        raise ValueError('future measurement')
    if not date.fromisoformat(calibrated['valid_from']) <= at <= date.fromisoformat(calibrated['valid_until']):
        raise ValueError('calibration not valid at measurement')
    if calibrated.get('instrument_id') != measured.get('instrument_id') or not measured.get('instrument_id'):
        raise ValueError('calibration instrument differs')
    if calibrated.get('instrument_revision') != measured.get('instrument_revision') or not measured.get('instrument_revision'):
        raise ValueError('calibration instrument revision differs')
    if measured.get('calibration_sha256') != digest(calibrated):
        raise ValueError('measurement targets different calibration')
    for quantity in measured['measurements']:
        if not quantity.get('quantity') or not quantity.get('unit') or quantity.get('uncertainty_basis') != 'expanded-k2':
            raise ValueError('typed quantity and expanded uncertainty basis required')
        for field in ('value', 'uncertainty'):
            value = quantity[field]
            if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
                raise ValueError('finite measured value and uncertainty required')
        if quantity['uncertainty'] < 0:
            raise ValueError('negative measurement uncertainty')
        ranges = [r for r in calibrated['ranges'] if r['quantity'] == quantity['quantity'] and r['unit'] == quantity['unit']]
        if not ranges or not any(r['minimum'] <= quantity['value'] <= r['maximum'] and
                0 <= r['uncertainty_floor'] <= quantity['uncertainty'] for r in ranges):
            raise ValueError('quantity outside calibration range/uncertainty')
    for descriptor in [*measured['raw_files'], calibrated['certificate']]:
        _artifact(root, descriptor)
    if disposition.get('measurement_sha256') != digest(measured) or disposition.get('calibration_sha256') != digest(calibrated):
        raise ValueError('review targets different measurement/calibration')
    if disposition.get('applicability') != {k: expected[k] for k in required}:
        raise ValueError('review applicability differs')
    if disposition.get('decision') not in {'accepted-record', 'retest', 'rejected'} or not disposition.get('reasons'):
        raise ValueError('explicit applicable signed disposition required')
    return dict(schema='osr-authenticated-external-record/1', authenticated=True,
        state=disposition['decision'], measurement_sha256=digest(measured), calibration_sha256=digest(calibrated),
        review_sha256=digest(disposition), applicability={k: expected[k] for k in required},
        scope='Pinned-key signature, raw-data identity, calibration coverage and signed disposition only; engineering authority must assess fitness and release separately',
        **core.FLAGS)
