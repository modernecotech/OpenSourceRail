"""FUXA 1.3.4 project export adapter, imported through its project API/UI."""
from html import escape
from urllib.parse import urlencode, urlsplit
from .config import digest, validate_package


VERSION = '1.3.4'
DEFAULT_WORKBENCH_URL = 'http://127.0.0.1:8090'


def _project_payload(value):
    """Accept FUXA's direct export and its API response wrapper."""
    if isinstance(value, dict) and isinstance(value.get('data'), dict):
        candidate = value['data']
        if 'devices' in candidate or 'hmi' in candidate:
            return candidate
    return value if isinstance(value, dict) else {}


def _views(value):
    return {row['id']: row for row in _project_payload(value).get('hmi', {}).get('views', [])
            if isinstance(row, dict) and row.get('id')}


def _devices(value):
    return _project_payload(value).get('devices', {}) or {}


def _settings(value):
    payload = _project_payload(value)
    hmi = payload.get('hmi', {})
    return {**{key: row for key, row in payload.items() if key not in {'devices', 'hmi'}},
        'hmi': {key: row for key, row in hmi.items() if key != 'views'}}


def _changes(current, desired):
    old, new = set(current), set(desired)
    return dict(added=sorted(new - old), removed=sorted(old - new),
        changed=sorted(key for key in old & new if digest(current[key]) != digest(desired[key])),
        unchanged=sorted(key for key in old & new if digest(current[key]) == digest(desired[key])))


def deployment_manifest(packages, desired=None, *, workbench_url=DEFAULT_WORKBENCH_URL):
    """Declare exactly which generated city packages and displays an import contains."""
    scopes, rows = set(), []
    for package in packages:
        validate_package(package)
        scope = (package['city'], package['environment'])
        if scope in scopes:
            raise ValueError('Only one FUXA package per city/environment may be imported')
        scopes.add(scope)
        sites = sorted({row['site_id'] for row in package['equipment']})
        rows.append(dict(city=package['city'], environment=package['environment'],
            engineering_revision=package['engineering_revision'], package_sha256=package['sha256'],
            sites=sites, equipment=len(package['equipment']),
            devices=sorted(row['fuxa_device_id'] for row in package['equipment']),
            views=['v_' + digest([package['city'], package['environment'], site])[:16] for site in sites]))
    desired = project(packages, workbench_url=workbench_url) if desired is None else desired
    payload = _project_payload(desired)
    manifest = dict(schema='osr-fuxa-deployment/1', fuxa_version=VERSION,
        packages=sorted(rows, key=lambda row: (row['city'], row['environment'])),
        reviewed_display_customisations=[],
        customisation_policy='Generated displays only; live-only or changed views are explicit removals/replacements in the import review',
        device_ids=sorted(_devices(payload)), view_ids=sorted(_views(payload)),
        desired_project_sha256=digest(payload))
    manifest['sha256'] = digest(manifest)
    return manifest


def deployment_review(current, packages, *, workbench_url=DEFAULT_WORKBENCH_URL):
    """Bind an add/change/remove preview to the live and desired FUXA projects."""
    desired = project(packages, workbench_url=workbench_url)
    old = _project_payload(current)
    review = dict(schema='osr-fuxa-import-review/1', current_project_sha256=digest(old),
        desired_project_sha256=digest(desired), manifest=deployment_manifest(packages, desired),
        devices=_changes(_devices(old), _devices(desired)),
        views=_changes(_views(old), _views(desired)),
        project_settings=dict(changed=digest(_settings(old)) != digest(_settings(desired)),
            current_sha256=digest(_settings(old)), desired_sha256=digest(_settings(desired))),
        replacement='FUXA project import replaces the complete live project')
    review['destructive_changes'] = bool(review['devices']['removed'] or review['devices']['changed'] or
        review['views']['removed'] or review['views']['changed'] or
        (review['project_settings']['changed'] and (_devices(old) or _views(old))))
    review['sha256'] = digest(review)
    return review


def validate_deployment_review(current, packages, supplied, *, workbench_url=DEFAULT_WORKBENCH_URL):
    expected = deployment_review(current, packages, workbench_url=workbench_url)
    if supplied != expected:
        raise ValueError('FUXA project or desired packages changed after review; preview again')
    return expected


def project(packages, *, workbench_url=DEFAULT_WORKBENCH_URL):
    origin = urlsplit(workbench_url)
    if (origin.scheme not in {'http', 'https'} or not origin.hostname or
            origin.username is not None or origin.password is not None or
            origin.path not in {'', '/'} or origin.query or origin.fragment or
            any(character.isspace() for character in workbench_url)):
        raise ValueError('Workbench URL must be an HTTP(S) origin without credentials')
    # Accessing port also rejects invalid/out-of-range ports.
    origin.port
    workbench_url = workbench_url.rstrip('/')
    devices, views, navigation, system_tags = {}, [], [], {}
    for package in packages:
        validate_package(package)
        sites = sorted({a['site_id'] for a in package['equipment']})
        for site in sites:
            view_id = 'v_' + digest([package['city'], package['environment'], site])[:16]
            items, variables = {}, {}
            site_assets = [a for a in package['equipment'] if a['site_id'] == site]
            count = len(site_assets)
            alarm_y = 110 + max(len(a['measurements']) for a in site_assets) * 70
            link_y = alarm_y + max(len(a['alarms']) for a in site_assets) * 20 + 22
            card_height = link_y + 24
            height = 115 + ((count + 1) // 2) * (card_height + 20)
            svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="{height}"><g id="svgcontent">',
                   f'<text x="30" y="38" font-size="24" fill="#183642">{escape(package["city"])} · {site} · {package["environment"].upper()}</text>',
                   '<text x="30" y="68" font-size="14" fill="#183642">OSR equipment supervision · source timestamps and quality shown explicitly</text>']
            for index, a in enumerate(a for a in package['equipment'] if a['site_id'] == site):
                device = a['fuxa_device_id']; x, y = 30 + (index % 2) * 580, 95 + (index // 2) * (card_height + 20)
                tags = {}
                connection = device + '__connection'
                system_tags[connection] = dict(id=connection, name=connection, type='number', sysType=1, memaddress=device, init=0, daq={'enabled': False})
                connection_widget = 'VAL_' + digest(connection)[:20]
                items[connection_widget] = dict(id=connection_widget, type='svg-ext-value', name='Gateway status', label='Value', property=dict(variable=connection, variableId=connection, variableSrc='0', events=[], ranges=[]))
                variables[connection] = dict(id=connection, name=connection, source='0')
                visibility = [dict(type='hide', variableId=connection, range=dict(min=0,max=3)), dict(type='show', variableId=connection, range=dict(min=5,max=5))]
                svg += [f'<rect x="{x}" y="{y}" width="550" height="{card_height}" rx="12" fill="#eef5f7" stroke="#b5cbd0"/>',
                        f'<text x="{x+20}" y="{y+32}" font-size="20" fill="#183642">{escape(a["equipment_type"].title())} · {escape(a["asset_id"])}</text>']
                svg += [f'<text x="{x+20}" y="{y+57}" font-size="12" fill="#73561b">Gateway: 0 offline · 3 stale · 5 live</text>', f'<g id="{connection_widget}" type="svg-ext-value"><text id="text_{connection_widget}" x="{x+300}" y="{y+57}" fill="#73561b">0</text></g>']
                for row, (name, m) in enumerate(a['measurements'].items()):
                    yy = y + 92 + row * 70
                    svg.append(f'<text x="{x+20}" y="{yy}" font-size="14" fill="#183642">{escape(name)} ({escape(m["unit"])})</text>')
                    for suffix, dx, dy, dtype in [('', 270, 0, 'Double'), ('_quality', 390, 0, 'String'), ('_timestamp', 270, 23, 'String')]:
                        tid = device + '__' + name + suffix
                        tags[tid] = dict(id=tid, name=tid, type=dtype, address=tid, daq={'enabled': False})
                        wid = 'VAL_' + digest([device, tid])[:20]
                        variable = tid
                        items[wid] = dict(id=wid, type='svg-ext-value', name=tid, label='Value', property=dict(variable=tid, variableId=variable, variableSrc=device, events=[], ranges=[], actions=visibility))
                        variables[variable] = dict(id=tid, name=tid, source=device)
                        svg.append(f'<g id="{wid}" type="svg-ext-value" fill="none"><text id="text_{wid}" x="{x+dx}" y="{yy+dy}" font-size="14" fill="#183642">—</text></g>')
                for n, rule in enumerate(a['alarms']):
                    tid = device + '__alarm_' + rule['id']; wid = 'VAL_' + digest([device, tid])[:20]
                    tags[tid] = dict(id=tid, name=tid, type='Bool', address=tid, daq={'enabled': False})
                    variable = tid
                    items[wid] = dict(id=wid, type='svg-ext-value', name=tid, label='Value', property=dict(variable=tid, variableId=variable, variableSrc=device, events=[], ranges=[], actions=visibility))
                    variables[variable] = dict(id=tid, name=tid, source=device)
                    svg += [f'<text x="{x+20}" y="{y+alarm_y+n*20}" font-size="14" fill="#a43228">{escape(rule["id"])} alarm (1 active)</text>', f'<g id="{wid}" type="svg-ext-value"><text id="text_{wid}" x="{x+280}" y="{y+alarm_y+n*20}" fill="#a43228">0</text></g>']
                url = workbench_url + '/?' + urlencode({'module': 'lifecycle', 'city': a['city'], 'environment': a['environment'], 'selected_asset': a['asset_id']})
                svg.append(f'<a href="{escape(url, quote=True)}" target="_top"><text x="{x+20}" y="{y+link_y}" fill="#166a70" font-size="14">Open asset, maintenance, engineering and history</text></a>')
                devices[device] = dict(id=device, name=device, type='WebAPI', enabled=True, polling=2000,
                    property=dict(getTags=f'http://integration:8093/tags/{a["city"]}/{a["environment"]}/{a["asset_id"]}'), tags=tags)
            svg.append('</g></svg>')
            views.append(dict(id=view_id, name=f'{package["city"]} · {site} · {package["environment"]}', type='svg',
                              profile=dict(width=1200, height=height, bkcolor='#ffffff'), items=items, variables=variables, svgcontent=''.join(svg)))
            navigation.append(dict(icon='dashboard', view=view_id, link='', text=views[-1]['name']))
    return dict(version='1.02', name='OpenSourceRail station supervision', devices=devices,
                server=dict(id='0', name='FUXA Server', type='FuxaServer', property={}, tags=system_tags), charts=[],
                hmi=dict(views=views, layout=dict(start=views[0]['id'], navigation=dict(mode='fix', type='inline', items=navigation, bkcolor='#eef5f7', fgcolor='#183642'),
                         header=dict(bkcolor='#ffffff', fgcolor='#183642'), showdev=True, loginonstart=True, show_connection_error=True)))
