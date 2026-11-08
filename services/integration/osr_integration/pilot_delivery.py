"""Fixed native wheel-delivery API requests; caller authentication stays native.

This module neither executes ERP requests nor forwards browser-supplied roles,
reviewers, physical approval or controller commands.
"""
from copy import deepcopy
import json
import re

METHODS = {
    'register': ('register_pack', {'project','pack','files'}),
    'preview': ('preview', {'project','pack_sha256','item_group'}),
    'review': ('review', {'project','pack_sha256','item_group','fingerprint'}),
    'apply': ('apply', {'project','pack_sha256','review_id'}),
    'status': ('status', {'project','pack_sha256'}),
    'install': ('register_installation', {'project','pack_sha256','part_id','asset','source_pattern_id','ordinal','train_index',
        'work_order','manufacture_stock','installation_stock','repair','removal_stock'}),
    'handback': ('review_handback', {'project','pack_sha256','asset'}),
    'lifecycle-status': ('lifecycle_status', {'project','pack_sha256','asset'}),
}


def request(action, values):
    if action not in METHODS:raise ValueError('Supported wheel-delivery business action required')
    method,fields=METHODS[action]
    if not isinstance(values,dict) or set(values)!=fields:raise ValueError('Exact native business arguments required; client roles/approval/commands are forbidden')
    if not isinstance(values.get('project'),str) or not values['project'].strip() or len(values['project'])>140:
        raise ValueError('Explicit native project required')
    for name in ('pack_sha256','fingerprint','review_id'):
        if name in values and re.fullmatch('[0-9a-f]{64}',str(values[name])) is None:raise ValueError('Exact '+name+' required')
    raw=json.dumps(values,sort_keys=True,separators=(',',':'),allow_nan=False)
    if len(raw.encode())>18*1024**2:raise ValueError('Bounded delivery request required')
    return dict(method='osr_erpnext.candidate_delivery.'+method,
        http_method='GET' if action in ('status','lifecycle-status') else 'POST',
        arguments=deepcopy(values),scope='Authenticated native simulation-business review; no physical or railway authority',
        physical_accepted=False,engineering_accepted=False,physical_evidence=False,manufacturing_release=False,operating_release=False,movement_authority=False)
