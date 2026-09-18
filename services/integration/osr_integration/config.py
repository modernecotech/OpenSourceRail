"""Deterministic, application-independent city supervisory packages."""
import copy
import hashlib
import json
import math
import re
import uuid

from .manufacturing import validate_method_metadata


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
    asset_types = {kind for template in templates.values() for kind in template.get('asset_types', ['station', 'depot'])}
    stations = [a for a in assets if a['asset_type'] in asset_types]
    energy_assets_by_parent = {}
    for asset in assets:
        if asset.get('asset_type') == 'energy':
            energy_assets_by_parent.setdefault(asset.get('parent_asset'), []).append(asset['asset_id'])
    if cfg.get('sites'):
        requested = cfg['sites']
        selected = set(requested)
        if len(selected) != len(requested) or not selected.issubset({a['asset_id'] for a in stations}):
            raise ValueError('Unknown or repeated supervised asset identity')
        # A bounded station pilot still needs real child assets such as its point
        # machines. Walk the existing parent links instead of inventing or copying
        # those identities into a city-specific supervision profile.
        while True:
            children = {a['asset_id'] for a in stations if a.get('parent_asset') in selected}
            expanded = selected | children
            if expanded == selected:
                break
            selected = expanded
        stations = [a for a in stations if a['asset_id'] in selected]
    equipment = []
    for station in stations:
        site = identifier(station['asset_id'])
        for kind, template in sorted(templates.items()):
            if station['asset_type'] not in template.get('asset_types', ['station', 'depot']):
                continue
            method = template.get('manufacturing_method')
            if method:
                validate_method_metadata(method)
                if method['rolling_stock_family'] != cfg.get('rolling_stock_family'):
                    continue
            identifier(kind)
            planned = f'{site}:{kind}'
            binding = cfg.get('bindings', {}).get(planned, {})
            item = dict(asset_id=planned, planned_asset_id=planned, parent_asset_id=site,
                site_id=site, source_asset_ids=[site] + (energy_assets_by_parent.get(site, []) if kind in ('charger', 'battery', 'pv') else []), city=slug, company_id=cfg.get('company', ''), environment=environment,
                name=f"{station['name']} · {template['label']}", equipment_type=kind,
                component_type_id=template['component_type_id'], engineering_revision=revision,
                source_crates=template.get('source_crates', []),
                ifc_global_id=binding.get('ifc_global_id', ''), physical_serial_id=binding.get('physical_serial_id', ''),
                erp_asset_id=binding.get('erp_asset_id', ''), erp_item_code=binding.get('erp_item_code', ''),
                erp_project=cfg.get('erp_project', ''), fuxa_device_id='osr-' + digest([environment, slug, planned])[:20],
                telemetry_namespace=f'osr/{environment}/{slug}/{site}/{kind}',
                source_id='simulator' if environment == 'simulation' else binding.get('source_id', ''),
                binding_status='simulation' if environment == 'simulation' else 'commissioning-required',
                supplier_binding=binding.get('supplier_binding', {}), measurements=template['measurements'],
                alarms=template.get('alarms', []), commands=template.get('commands', {}))
            if 'manufacturing_method' in template:
                item['manufacturing_method'] = copy.deepcopy(template['manufacturing_method'])
            equipment.append(item)
    if not equipment:
        raise ValueError('No applicable equipment selected; check sites and rolling-stock family')
    package = dict(schema='osr-supervisory/1', city=slug, environment=environment,
        engineering_revision=revision, rolling_stock_family=cfg.get('rolling_stock_family'), template_revision=cfg['template_revision'],
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
    finite(package['historian'].get('sampling_seconds', 2), 1, 3600)
    ids = set()
    for a in package['equipment']:
        aid = identifier(a['asset_id'])
        if aid in ids or a['city'] != package['city'] or a['environment'] != package['environment']:
            raise ValueError('Duplicate identity or wrong city/environment')
        ids.add(aid)
        if 'manufacturing_method' in a:
            validate_method_metadata(a['manufacturing_method'])
            if a['manufacturing_method']['rolling_stock_family'] != package.get('rolling_stock_family'):
                raise ValueError('Factory method does not apply to package rolling-stock family')
            if a['component_type_id'] != a['manufacturing_method']['method_id']:
                raise ValueError('Factory component and manufacturing method identities differ')
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
            if rule.get('measurement') not in a['measurements']:
                raise ValueError('Alarm references an unknown measurement')
            m = a['measurements'][rule['measurement']]
            finite(rule['high'], m['min'], m['max'])
            finite(rule['clear_below'], m['min'], rule['high'])
            finite(rule['delay_seconds'], 0, 3600)
            finite(rule['repeat_seconds'], 1, 86400)
            if not isinstance(rule.get('priority', 'medium'), str) or rule.get('priority', 'medium') not in {'low', 'medium', 'high'}:
                raise ValueError('Alarm priority must be low, medium or high')
            if type(rule.get('maintenance')) is not bool or not isinstance(rule.get('response'), str) or not rule['response'].strip():
                raise ValueError('Alarm maintenance flag and response are required')
        commands = a.get('commands', {})
        if not isinstance(commands, dict):
            raise ValueError('Commands must be an identity-keyed object')
        for name, command in commands.items():
            identifier(name)
            if not isinstance(command, dict):
                raise ValueError('Command contract must be an object')
            parameter = identifier(command.get('parameter'))
            low = finite(command.get('min'), -1e12, 1e12)
            finite(command.get('max'), low, 1e12)
            finite(command.get('max_ttl_seconds'), 1, 300)
            conditions = command.get('required_conditions')
            if not isinstance(conditions, list) or not conditions or any(
                    not isinstance(value, str) or identifier(value) != value for value in conditions):
                raise ValueError('Command required conditions must be non-empty identities')
            if len(conditions) != len(set(conditions)) or parameter in conditions:
                raise ValueError('Command conditions must be unique and distinct from its parameter')
    return package


def ifc_guid(planned_asset_id):
    """22-character IFC GUID from stable planned identity, independent of revision."""
    value = uuid.uuid5(uuid.NAMESPACE_URL, 'https://opensourcerail.org/assets/' + planned_asset_id).int
    alphabet = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz_$'
    return ''.join(alphabet[(value >> (6 * i)) & 63] for i in reversed(range(22)))
