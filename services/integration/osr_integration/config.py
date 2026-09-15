"""Deterministic, application-independent city supervisory packages."""
import copy
import hashlib
import json
import math
import re
import uuid


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()).hexdigest()


def identifier(value):
    if not isinstance(value, str) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.:-]{0,159}', value):
        raise ValueError('Invalid identity')
    return value


def finite(value, low, high):
    if isinstance(value, bool) or not isinstance(value, (float, int)) or not math.isfinite(value) or not low <= value <= high:
        raise ValueError(f'Expected finite number between {low} and {high}')
    return value


def merge(base, override):
    result = copy.deepcopy(base)
    for key, value in override.items():
        result[key] = merge(result[key], value) if isinstance(value, dict) and isinstance(result.get(key), dict) else copy.deepcopy(value)
    return result


def build_package(generic, city, assets, revision, environment='simulation'):
    if environment not in ('simulation', 'physical'):
        raise ValueError('Unknown environment')
    slug = identifier(city['city'])
    cfg = merge(generic, city)
    templates = cfg['templates']
    stations = [a for a in assets if a['asset_type'] in ('station', 'depot')]
    if cfg.get('sites'):
        stations = [a for a in stations if a['asset_id'] in cfg['sites']]
        if len(stations) != len(set(cfg['sites'])):
            raise ValueError('Unknown or repeated station/depot identity')
    equipment = []
    for station in stations:
        site = identifier(station['asset_id'])
        for kind, template in sorted(templates.items()):
            identifier(kind)
            planned = f'{site}:{kind}'
            binding = cfg.get('bindings', {}).get(planned, {})
            equipment.append(dict(asset_id=planned, planned_asset_id=planned, parent_asset_id=site,
                site_id=site, source_asset_ids=[site] + [r['asset_id'] for r in assets if r.get('asset_type') == 'energy' and r.get('parent_asset') == site and kind in ('charger', 'battery', 'pv')], city=slug, company_id=cfg.get('company', ''), environment=environment,
                name=f"{station['name']} · {template['label']}", equipment_type=kind,
                component_type_id=template['component_type_id'], engineering_revision=revision,
                ifc_global_id=binding.get('ifc_global_id', ''), physical_serial_id=binding.get('physical_serial_id', ''),
                erp_asset_id=binding.get('erp_asset_id', ''), erp_item_code=binding.get('erp_item_code', ''),
                erp_project=cfg.get('erp_project', ''), fuxa_device_id='osr-' + digest([environment, slug, planned])[:20],
                telemetry_namespace=f'osr/{environment}/{slug}/{site}/{kind}',
                source_id='simulator' if environment == 'simulation' else binding.get('source_id', ''),
                binding_status='simulation' if environment == 'simulation' else 'commissioning-required',
                supplier_binding=binding.get('supplier_binding', {}), measurements=template['measurements'],
                alarms=template.get('alarms', []), commands=template.get('commands', {})))
    if not equipment:
        raise ValueError('No station or depot equipment selected')
    package = dict(schema='osr-supervisory/1', city=slug, environment=environment,
        engineering_revision=revision, template_revision=cfg['template_revision'],
        historian=cfg['historian'], equipment=equipment,
        lifecycle=['plan', 'design', 'procure', 'manufacture', 'construct', 'commission', 'operate', 'maintain', 'renew'])
    package['sha256'] = digest(package)
    validate_package(package)
    return package


def validate_package(package):
    body = {k: v for k, v in package.items() if k != 'sha256'}
    if package.get('schema') != 'osr-supervisory/1' or digest(body) != package.get('sha256'):
        raise ValueError('Package schema/checksum mismatch')
    identifier(package['city'])
    if package['environment'] not in ('simulation', 'physical'):
        raise ValueError('Invalid environment')
    if package['historian']['owner'] != 'osr-integration':
        raise ValueError('This adapter requires one OSR historian; FUXA DAQ stays disabled')
    finite(package['historian']['retention_days'], 1, 365)
    ids = set()
    for a in package['equipment']:
        aid = identifier(a['asset_id'])
        if aid in ids or a['city'] != package['city'] or a['environment'] != package['environment']:
            raise ValueError('Duplicate identity or wrong city/environment')
        ids.add(aid)
        for name, m in a['measurements'].items():
            identifier(name)
            finite(m['min'], -1e12, 1e12); finite(m['max'], m['min'], 1e12)
            finite(m['stale_seconds'], 1, 3600)
            finite(m.get('scale', 1), 1e-12, 1e12); finite(m.get('offset', 0), -1e12, 1e12)
            if not isinstance(m['unit'], str):
                raise ValueError('Measurement unit required')
        rule_ids = set()
        for rule in a['alarms']:
            identifier(rule['id'])
            if rule['id'] in rule_ids:
                raise ValueError('Duplicate alarm identity')
            rule_ids.add(rule['id'])
            m = a['measurements'][rule['measurement']]
            finite(rule['high'], m['min'], m['max'])
            finite(rule['clear_below'], m['min'], rule['high'])
            finite(rule['delay_seconds'], 0, 3600)
            finite(rule['repeat_seconds'], 1, 86400)
    return package


def ifc_guid(planned_asset_id):
    """22-character IFC GUID from stable planned identity, independent of revision."""
    value = uuid.uuid5(uuid.NAMESPACE_URL, 'https://opensourcerail.org/assets/' + planned_asset_id).int
    alphabet = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz_$'
    return ''.join(alphabet[(value >> (6 * i)) & 63] for i in reversed(range(22)))
