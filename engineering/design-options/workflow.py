"""Bounded city design experiments; no automatic canonical or operating promotion."""
import copy
import hashlib
import json
import math
from pathlib import Path
import re
import subprocess
import sys
import tomllib

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'design/city-generation/src'))
from osr_scenario.generator import generate_scenario

GENERIC = Path(__file__).parent / 'config/generic.json'
PARAMETERS = {'charging_dwell_seconds', 'additional_trainsets',
              'additional_storage_modules', 'additional_pv_kw'}
REMAINING = [
    'Observed peak headways, directional service and calibrated passenger demand',
    'Updated capital and operating costs, site footprint and grid/solar feasibility',
    'Vehicle, charger, station, stabling and maintenance engineering review',
    'Independent operator acceptance and physical verification',
]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text())


def write(path, value):
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + '\n')


def toml_snapshot(doc):
    """Generated snapshot; edit the small JSON profile, not this inline TOML."""
    def value(item):
        if isinstance(item, dict):
            return '{' + ', '.join(json.dumps(k) + ' = ' + value(v) for k, v in item.items()) + '}'
        if isinstance(item, list):
            return '[' + ', '.join(value(v) for v in item) + ']'
        return json.dumps(item, ensure_ascii=False, allow_nan=False)
    text = '\n'.join(json.dumps(k) + ' = ' + value(v) for k, v in doc.items()) + '\n'
    if tomllib.loads(text) != doc:
        raise ValueError('Design snapshot failed TOML round trip')
    return text


def resolve(profile, policy):
    if set(profile) != {'schema', 'city', 'id', 'lines'} or profile['schema'] != 'osr-design-option/1':
        raise ValueError('Invalid profile schema or unknown profile fields')
    if any(not isinstance(profile[k], str) or not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', profile[k]) for k in ('city', 'id')):
        raise ValueError('City and option id must be lowercase slugs')
    if policy.get('schema') != 'osr-design-option-policy/1' or set(policy.get('parameters', {})) != PARAMETERS:
        raise ValueError('Invalid generic parameter policy')
    if not isinstance(profile['lines'], dict):
        raise ValueError('lines must map line ids to settings')
    result = copy.deepcopy(profile)
    for line, settings in profile['lines'].items():
        if not isinstance(settings, dict) or set(settings) - PARAMETERS:
            raise ValueError(f'Unknown settings for {line}')
        result['lines'][line] = {}
        for key, rule in policy['parameters'].items():
            v = settings.get(key, rule['default'])
            if v is None and key == 'charging_dwell_seconds' and key not in settings:
                result['lines'][line][key] = v
                continue
            types = (int,) if rule['type'] == 'integer' else (int, float)
            if type(v) not in types or not math.isfinite(v) or not rule['minimum'] <= v <= rule['maximum']:
                raise ValueError(f'{line}.{key} outside {rule["minimum"]}..{rule["maximum"]}')
            result['lines'][line][key] = v
    return result


def apply_option(design, baseline, resolved):
    candidate = copy.deepcopy(design)
    lines = {line['name']: line for line in candidate['lines']}
    if set(resolved['lines']) - set(lines):
        raise ValueError('Profile refers to an unknown city line')
    ledger = []
    def change(kind, key, obj, field, after):
        before = obj.get(field)
        if before != after:
            ledger.append(dict(kind=kind, id=key, field=field, before=before, after=after))
            obj[field] = after
    energy = any(p['additional_storage_modules'] or p['additional_pv_kw'] for p in resolved['lines'].values())
    if energy:
        # Explicit sites replace generator defaults; preserve every other site.
        candidate['sites'] = copy.deepcopy(baseline['sites'])
    impacts = dict(additional_trainsets=0, additional_storage_modules=0,
                   additional_storage_kwh=0, additional_pv_kw=0, affected_energy_sites=0)
    for line_id, params in resolved['lines'].items():
        dwell = params['charging_dwell_seconds']
        if dwell is not None:
            change('line', line_id, lines[line_id], 'charging_dwell_seconds', dwell)
        extra = params['additional_trainsets']
        if extra:
            fleets = [f for f in candidate['fleets'] if f['line'] == line_id]
            if len(fleets) != 1:
                raise ValueError('Additional trainsets require exactly one fleet per line')
            fleet = fleets[0]
            change('fleet', line_id, fleet, 'trainset_count', fleet['trainset_count'] + extra)
            change('fleet', line_id, fleet, 'service_rotation_count', fleet.get('service_rotation_count', 0) + extra)
            impacts['additional_trainsets'] += extra
        modules, pv = params['additional_storage_modules'], params['additional_pv_kw']
        if modules or pv:
            stations = {s['id'] for s in candidate['stations'] if s['line'] == line_id}
            sites = [s for s in candidate['sites'] if s['station'] in stations]
            if not sites:
                raise ValueError(f'No energy sites for {line_id}')
            for site in sites:
                capacity = modules * site['storage_module_kwh']
                change('site', site['station'], site, 'storage_capacity_kwh', site['storage_capacity_kwh'] + capacity)
                change('site', site['station'], site, 'pv_nameplate_kw', site['pv_nameplate_kw'] + pv)
                # Keep duplicate depot planning quantities consistent with sites.
                for depot in candidate.get('depots', []):
                    if depot.get('station') == site['station']:
                        for field, source in [('battery_kwh', 'storage_capacity_kwh'), ('pv_nominal_kwp', 'pv_nameplate_kw')]:
                            if field in depot:
                                change('depot', depot['station'], depot, field, site[source])
                impacts['additional_storage_modules'] += modules
                impacts['additional_storage_kwh'] += capacity
                impacts['additional_pv_kw'] += pv
                impacts['affected_energy_sites'] += 1
    return candidate, dict(changes=ledger, resource_delta=impacts,
                          costs_recomputed=False, remaining=REMAINING)


def check_effects(before, after, resolved, design):
    """Reject ignored settings and preserve the denominator of service gates."""
    if before['consist'] != after['consist']:
        raise ValueError('Option changed vehicle configuration')
    if before['scenario'] != after['scenario']:
        raise ValueError('Option changed operating policy')
    for old in before['fleets']:
        new = next(f for f in after['fleets'] if f['line'] == old['line'])
        params = resolved['lines'].get(old['line'], {})
        if old.get('schedule') != new.get('schedule'):
            raise ValueError('Option changed published timetable')
        if new['trainset_count'] != old['trainset_count'] + params.get('additional_trainsets', 0):
            raise ValueError('Fleet adjustment was not effective')
    station_lines = {s['id']: s['line'] for s in design['stations']}
    for old in before['stations']:
        new = next(s for s in after['stations'] if s['id'] == old['id'])
        params = resolved['lines'].get(station_lines[old['id']], {})
        dwell = params.get('charging_dwell_seconds')
        if dwell is not None and old.get('charging_power_kw', 0) > 0 and new['dwell_seconds'] != dwell:
            raise ValueError('Charging dwell adjustment was not effective')
    stations = station_lines
    for old in before['sites']:
        new = next(s for s in after['sites'] if s['station'] == old['station'])
        params = resolved['lines'].get(stations.get(old['station']), {})
        for field, delta in [('storage_capacity_kwh', params.get('additional_storage_modules', 0) * old['storage_module_kwh']),
                             ('pv_nameplate_kw', params.get('additional_pv_kw', 0))]:
            if not math.isclose(new[field], old[field] + delta, abs_tol=0.01):
                raise ValueError(f'Site adjustment was not effective: {old["station"]}.{field}')


def dependencies(extra):
    paths = {Path(__file__).resolve(), GENERIC, *extra}
    for folder, glob in [('crates', '*.rs'), ('lib/templates', '*.toml'),
                         ('design/city-generation/src', '*.py'),
                         ('design/component-catalogue/catalog/buildable-trainset', '*.json')]:
        paths.update((ROOT / folder).rglob(glob))
    paths.update((ROOT / 'crates').rglob('Cargo.toml'))
    paths.update(ROOT / p for p in ['Cargo.toml', 'Cargo.lock', 'rust-toolchain.toml',
                 'tools/automation/design-option.py', 'tools/automation/validate-city-service.py',
                 'tools/automation/validate-city-simulation.py'])
    return {str(p.relative_to(ROOT)): sha(p) for p in sorted(paths) if p.is_file()}


def prepare(profile_path, output):
    profile_path, output = profile_path.resolve(), output.resolve()
    if not profile_path.is_relative_to(ROOT) or not output.is_relative_to(ROOT / 'build'):
        raise ValueError('Use a repository profile and a fresh output directory inside build/')
    profile, policy = read(profile_path), read(GENERIC)
    resolved = resolve(profile, policy)
    city = resolved['city']
    choices = [p for p in (ROOT / 'cities/catalogue').rglob(city + '.toml') if (p.parent / 'design.toml').is_file()]
    if len(choices) != 1:
        raise ValueError('City must identify exactly one canonical package')
    canonical = choices[0]
    source = canonical.parent / 'design.toml'
    design = tomllib.loads(source.read_text())
    # Apply changes to the current generator baseline and record drift from the
    # checked-in scenario. This keeps generator changes visible, not hidden.
    baseline_text = generate_scenario(design, source, ROOT / 'lib/templates')
    baseline = tomllib.loads(baseline_text)
    candidate, ledger = apply_option(design, baseline, resolved)
    generated = generate_scenario(candidate, output / 'design.toml', ROOT / 'lib/templates')
    check_effects(baseline, tomllib.loads(generated), resolved, design)
    inputs = dependencies([source, canonical, profile_path])
    output.mkdir(parents=True, exist_ok=False)
    (output / 'design.toml').write_text(toml_snapshot(candidate))
    (output / f'{city}.toml').write_text(generated)
    (output / 'generator-baseline.toml').write_text(baseline_text)
    write(output / 'profile.json', profile)
    write(output / 'generic.json', policy)
    write(output / 'resolved.json', resolved)
    write(output / 'changes.json', ledger)
    manifest = dict(schema='osr-design-option-bundle/1', city=city, id=resolved['id'],
                    environment='simulation', operating_release=False,
                    canonical_scenario_matches_generator=tomllib.loads(canonical.read_text()) == baseline,
                    inputs=inputs, files={p.name: sha(p) for p in sorted(output.iterdir())})
    write(output / 'manifest.json', manifest)
    return manifest


def verify(folder, current=True):
    folder = folder.resolve()
    manifest = read(folder / 'manifest.json')
    if manifest['schema'] != 'osr-design-option-bundle/1':
        raise ValueError('Invalid option bundle')
    for name, digest in manifest['files'].items():
        if Path(name).name != name or sha(folder / name) != digest:
            raise ValueError(f'Changed bundle file: {name}')
    if current:
        for name, digest in manifest['inputs'].items():
            path = (ROOT / name).resolve()
            if not path.is_relative_to(ROOT) or sha(path) != digest:
                raise ValueError(f'Changed source dependency: {name}')
    if (folder / 'result.json').exists():
        result = read(folder / 'result.json')
        if result['manifest_sha256'] != sha(folder / 'manifest.json') or result['qualification_sha256'] != sha(folder / 'qualification.json'):
            raise ValueError('Result does not match the recorded bundle')
        report = read(folder / 'qualification.json')
        if report['scenario_sha256'] != manifest['files'][manifest['city'] + '.toml'] or report['design_sha256'] != manifest['files']['design.toml']:
            raise ValueError('Qualification tested a different design or scenario')
        if report.get('service_acceptance_schema') != 'osr-city-service-qualification/1':
            raise ValueError('Missing per-line qualification')
        if result['city'] != manifest['city'] or result['id'] != manifest['id'] or result['operating_release'] is not False:
            raise ValueError('Result scope mismatch')
        if result['passed'] != bool(report['passed'] and report['qualification_inputs_unchanged'] and report['resilience_required'] and report['full_window_passed']):
            raise ValueError('Result disagrees with full qualification')
    return manifest


def qualify(folder):
    folder = folder.resolve()
    manifest = verify(folder)
    if (folder / 'qualification.json').exists() or (folder / 'result.json').exists():
        raise ValueError('Qualification already exists; prepare a fresh option bundle')
    command = [sys.executable, str(ROOT / 'tools/automation/validate-city-service.py'),
               '--scenario', str(folder / (manifest['city'] + '.toml')), '--resilience',
               '--full-only', '--output', str(folder / 'qualification.json')]
    with (folder / 'execution.log').open('w') as log:
        process = subprocess.run(command, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT)
    verify(folder)
    report = read(folder / 'qualification.json')
    if process.returncode != (0 if report['passed'] else 1) or report['simulator_sha256'] != sha(ROOT / report['simulator_binary']):
        raise ValueError('Qualification did not finish with the recorded simulator')
    result = dict(schema='osr-design-option-result/1', city=manifest['city'], id=manifest['id'],
                  environment='simulation', passed=bool(report['passed']), operating_release=False,
                  manifest_sha256=sha(folder / 'manifest.json'), qualification_sha256=sha(folder / 'qualification.json'),
                  simulator_sha256=report['simulator_sha256'], remaining=REMAINING)
    write(folder / 'result.json', result)
    verify(folder)
    return result
