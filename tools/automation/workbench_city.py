"""City deployment inventory and native tool routes; no credentials or authority grants."""
import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlencode, quote


def read_json(path):
    try:
        value = json.loads(path.read_text())
        return value if isinstance(value, dict) else None
    except (OSError, ValueError):
        return None


def city_summary(root, city, design_path, control_city, environment='simulation'):
    if environment not in {'simulation', 'physical'}:
        raise ValueError('Unknown asset environment')
    operations = Path(design_path).parent / 'operations'
    profile = read_json(operations / 'supervision.json') or {}
    feedback = read_json(root / 'var/erpnext/operating-twins.json') or {}
    candidates = [r for r in feedback.get('snapshots', []) if r.get('city') == city]
    if profile.get('erp_project'):
        candidates = [r for r in candidates if r.get('project') == profile['erp_project'] and
                      (not profile.get('company') or r.get('company') == profile['company'])]
    chosen = candidates[0] if len(candidates) == 1 else None
    routes = {'projects': '/app/project?' + urlencode({'custom_osr_city': city})}
    erp = {'state': 'ambiguous' if len(candidates) > 1 else 'unavailable', 'project': None,
           'observed_at': None, 'stale': True, 'routes': routes}
    if chosen:
        erp.update(state='linked', project=chosen['project'], company=chosen.get('company'),
                   observed_at=chosen.get('observed_at'))
        try:
            observed = datetime.fromisoformat(chosen['observed_at'].replace('Z', '+00:00'))
            age = (datetime.now(timezone.utc) - observed).total_seconds()
            erp['stale'] = age < -60 or age > 3600
        except (ValueError, TypeError, KeyError):
            pass
        project = chosen['project']
        routes['projects'] = '/app/project/' + quote(project, safe='')
        # These pinned ERPNext DocTypes have a native parent Project field. Child-only
        # project lines can also appear in city execution's permission-filtered actuals.
        for module, doctype in [('tasks','task'), ('procurement','purchase-order'),
                ('receipts','purchase-receipt'), ('manufacturing','work-order'),
                ('stock','stock-entry'), ('issues','issue'), ('finance','purchase-invoice')]:
            routes[module] = '/app/' + doctype + '?' + urlencode({'project': project})
    package = read_json(root / 'build/supervision' / city / environment / 'package.json')
    package_valid = bool(package and package.get('city') == city and package.get('environment') == environment)
    sites = sorted({a['site_id'] for a in package.get('equipment', [])}) if package_valid else []
    # A new factory/wayside view must not silently change the default display.
    vehicles = sorted({a['site_id'] for a in (package or {}).get('equipment', [])
                       if a.get('equipment_type', '').startswith('vehicle-')}) if package_valid else []
    preferred = profile.get('preferred_supervision_site') or (vehicles[0] if vehicles else next(iter(sites), None))
    if preferred not in sites:
        preferred = None
    engineering = read_json(root / 'build/supervision' / city / 'engineering.json')
    return {'city': city, 'environment': environment, 'control_workspace': control_city,
            'control_available': city == control_city, 'erp': erp,
            'engineering': {'state': 'prepared' if engineering and engineering.get('city') == city else 'unavailable',
                            'artifact_count': len(engineering.get('artifacts', [])) if engineering and engineering.get('city') == city else 0},
            'supervision': {'state': 'prepared' if package_valid else 'unavailable', 'sites': sites,
                           'preferred_site': preferred, 'equipment_count': len(package.get('equipment', [])) if package_valid else 0},
            'profiles': {name: (operations / filename).is_file() for name, filename in
                         [('erp', 'erpnext.toml'), ('components', 'erp-components.json'), ('supervision', 'supervision.json')]}}
