"""Independent ERP validation of queued offline evidence, without gateway imports."""
import base64
import hashlib
import json
import math
import time
from datetime import datetime


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()).hexdigest()


def verify(packet):
    if packet.get('schema') != 'osr-field-completion/1' or packet.get('operational_release') is not False:
        raise ValueError('Field intake cannot grant operational release')
    work = packet['work']; event = packet['event']
    if set(event) - {'id','device_id','work_id','status','readings','photos','notes','performed_at'}: raise ValueError('Unknown field event fields')
    if work['sha256'] != digest({k: v for k, v in work.items() if k != 'sha256'}): raise ValueError('Work pack hash mismatch')
    if event.get('performed_at') is not None:
        when = datetime.fromisoformat(event['performed_at'].replace('Z', '+00:00'))
        if when.tzinfo is None or when.timestamp() > time.time() + 300: raise ValueError('Invalid offline performance timestamp')
    expected = digest(dict(event=event, actor=packet['actor'], scope=packet['city'] + '|' + packet['environment']))
    if expected != packet['idempotency_sha256']: raise ValueError('Field event hash mismatch')
    if event.get('work_id') != work['id'] or event.get('status') != 'performed-awaiting-inspection': raise ValueError('Invalid field execution state')
    if work['city'] != packet['city'] or work['environment'] != packet['environment'] or work['assigned_to'] != packet['actor']:
        raise ValueError('Field event scope/technician mismatch')
    definitions = {r['id']: r for r in work['readings']}; values = event['readings']
    if len(definitions) != len(work['readings']) or not values.keys() <= definitions.keys(): raise ValueError('Unknown/duplicate field reading')
    for key, spec in definitions.items():
        if key not in values:
            if spec['required']: raise ValueError('Missing required field reading')
            continue
        value = values[key]
        if spec['kind'] == 'number':
            if not isinstance(value, dict) or value.get('unit') != spec['unit']: raise ValueError('Field reading unit mismatch')
            number = value.get('value')
            if isinstance(number, bool) or not isinstance(number, (float, int)) or not math.isfinite(number) or not spec['min'] <= number <= spec['max']:
                raise ValueError('Invalid numeric field reading')
        elif spec['kind'] == 'boolean':
            if type(value) is not bool: raise ValueError('Invalid boolean field reading')
        elif spec['kind'] == 'text':
            if not isinstance(value, str) or not value.strip() or len(value) > 10000: raise ValueError('Invalid text field reading')
        else: raise ValueError('Unsupported field reading kind')
    photos = event.get('photos', [])
    if len(photos) > 8 or work['requires_photo'] and not photos: raise ValueError('Field photo requirement not met')
    photo_ids = set()
    for photo in photos:
        if photo['id'] in photo_ids: raise ValueError('Duplicate field photo')
        photo_ids.add(photo['id'])
        content = base64.b64decode(photo['base64'], validate=True)
        if not 8 <= len(content) <= 2_000_000 or hashlib.sha256(content).hexdigest() != photo['sha256']:
            raise ValueError('Field photo hash/size mismatch')
        magic = {'image/png': b'\x89PNG\r\n\x1a\n', 'image/jpeg': b'\xff\xd8\xff'}.get(photo['mime'])
        if not magic or not content.startswith(magic): raise ValueError('Field photo content mismatch')
    return packet
