"""Typed offline evidence validation; independent inspection/handback stays separate."""
import base64
import hashlib
import time
from datetime import datetime
from ..config import finite, identifier
from .contracts import records


class Conflict(ValueError):
    """The caller must refresh controlled records, not silently overwrite them."""


def validate_work(work):
    if not isinstance(work, dict): raise ValueError('Work pack must be an object')
    if set(work) & {'sha256','baseline_sha256','engineering_revision','physical_serial','issued_by','operational_release','state'}:
        raise ValueError('Work pack contains server-owned fields')
    if not isinstance(work.get('instructions', ''), str) or len(work.get('instructions', '')) > 50000: raise ValueError('Invalid work instructions')
    for key in ('id', 'city', 'environment', 'asset_id', 'assigned_to', 'method_revision', 'erp_task', 'erp_asset'):
        identifier(work.get(key))
    if work['environment'] not in ('simulation', 'physical'): raise ValueError('Invalid field environment')
    if not isinstance(work.get('native_modified'), str) or not work['native_modified']:
        raise ValueError('Current native Task modification identity required')
    if type(work.get('requires_photo')) is not bool: raise ValueError('Photo policy required')
    for reading in records(work.get('readings'), 'work readings', 100).values():
        if reading.get('kind') not in ('number', 'text', 'boolean') or type(reading.get('required')) is not bool:
            raise ValueError('Reading kind and requirement flag required')
        if reading['kind'] == 'number':
            if not isinstance(reading.get('unit'), str) or not reading['unit']: raise ValueError('Reading unit required')
            finite(reading.get('min'), -1e12, 1e12); finite(reading.get('max'), reading['min'], 1e12)
    return work


def validate_completion(work, event):
    if not isinstance(event, dict) or set(event) - {'id','device_id','work_id','status','readings','photos','notes','performed_at'}:
        raise ValueError('Unknown field completion fields')
    for key in ('id', 'device_id', 'work_id'): identifier(event.get(key))
    if event['work_id'] != work['id'] or event.get('status') != 'performed-awaiting-inspection':
        raise ValueError('Field execution must await independent inspection')
    if event.get('performed_at') is not None:
        when = datetime.fromisoformat(event['performed_at'].replace('Z', '+00:00'))
        if when.tzinfo is None or when.timestamp() > time.time() + 300: raise ValueError('Field performance time requires timezone and cannot be in the future')
    defs = records(work['readings'], 'readings'); values = event.get('readings')
    if not isinstance(values, dict) or not values.keys() <= defs.keys(): raise ValueError('Unknown typed reading')
    for key, definition in defs.items():
        value = values.get(key)
        if key not in values:
            if definition['required']: raise ValueError('Required reading missing: ' + key)
            continue
        kind = definition['kind']
        if kind == 'number':
            if not isinstance(value, dict) or set(value) != {'value', 'unit'} or value['unit'] != definition['unit']:
                raise ValueError('Reading unit mismatch: ' + key)
            finite(value['value'], definition['min'], definition['max'])
        elif kind == 'boolean' and type(value) is not bool: raise ValueError('Boolean reading required')
        elif kind == 'text' and (not isinstance(value, str) or not value.strip() or len(value) > 10000): raise ValueError('Text reading required')
    photos = event.get('photos', [])
    if not isinstance(photos, list) or len(photos) > 8 or work['requires_photo'] and not photos:
        raise ValueError('Photo evidence policy not met')
    for photo in photos:
        identifier(photo.get('id'))
        if photo.get('mime') not in ('image/png', 'image/jpeg'): raise ValueError('Unsupported photo type')
        try: content = base64.b64decode(photo['base64'], validate=True)
        except (ValueError, KeyError, TypeError) as exc: raise ValueError('Invalid photo encoding') from exc
        if not 8 <= len(content) <= 2_000_000 or hashlib.sha256(content).hexdigest() != photo.get('sha256'):
            raise ValueError('Photo content hash/size mismatch')
        magic = b'\x89PNG\r\n\x1a\n' if photo['mime'] == 'image/png' else b'\xff\xd8\xff'
        if not content.startswith(magic): raise ValueError('Photo MIME/content mismatch')
    if len({photo['id'] for photo in photos}) != len(photos): raise ValueError('Duplicate photo identity')
    if not isinstance(event.get('notes', ''), str) or len(event.get('notes', '')) > 10000: raise ValueError('Invalid field notes')
    return event
