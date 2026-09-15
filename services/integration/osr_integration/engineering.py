"""Versioned links to existing CAD, IFC, GIS and analysis artifacts."""
from contextlib import closing
import hashlib
import json
import re
import zipfile
from pathlib import Path
from xml.etree import ElementTree
from .config import digest

TOOLS = {'freecad', 'bonsai', 'qgis', 'osr', 'sumo', 'opensees', 'energyplus', 'fds', 'swmm', 'jupedsim', 'cloudcompare', 'blender', 'verification'}


def artifact(root, relative, tool, version):
    root = Path(root).resolve(); path = (root / relative).resolve()
    if not path.is_relative_to(root) or not path.is_file():
        raise ValueError('Artifact must exist within workspace')
    if tool not in TOOLS or not version:
        raise ValueError('Known owning tool and explicit version required')
    raw = path.read_bytes()
    result = dict(path=path.relative_to(root).as_posix(), tool=tool, tool_version=version,
                  sha256=hashlib.sha256(raw).hexdigest(), bytes=len(raw))
    if path.suffix.lower() == '.ifc':
        text = raw.decode('utf-8', errors='replace')
        result['ifc_objects'] = [{'entity': m[0], 'global_id': m[1]} for m in re.findall(r"=\s*(IFC[A-Z0-9]+)\s*\(\s*'([0-3][0-9A-Za-z_$]{21})'", text)]
    elif path.suffix.lower() in ('.fcstd', '.qgz', '.bcfzip', '.bcf'):
        with zipfile.ZipFile(path) as archive:
            # Metadata only, no extraction or execution of embedded code.
            result['members'] = archive.namelist()
            if path.suffix.lower() == '.fcstd':
                doc = ElementTree.fromstring(archive.read('Document.xml'))
                result['tool_version'] = doc.get('ProgramVersion', version)
                result['objects'] = [e.attrib for e in doc.findall('.//Objects/Object')]
            if path.suffix.lower() == '.qgz':
                name = next(n for n in archive.namelist() if n.endswith('.qgs'))
                doc = ElementTree.fromstring(archive.read(name))
                result['layers'] = [e.findtext('layername') for e in doc.findall('.//projectlayers/maplayer')]
                result['crs'] = doc.findtext('.//projectCrs/spatialrefsys/authid')
    elif path.suffix.lower() == '.gpkg':
        import sqlite3
        with closing(sqlite3.connect(path.as_uri() + '?mode=ro', uri=True)) as db:
            result['layers'] = [dict(table=r[0], data_type=r[1], srs_id=r[2]) for r in db.execute('SELECT table_name,data_type,srs_id FROM gpkg_contents')]
    elif path.suffix.lower() in ('.geojson', '.json'):
        value = json.loads(raw)
        if isinstance(value, dict) and isinstance(value.get('tool'), dict):
            result['tool_version'] = value['tool'].get('version_output', value['tool'].get('version', version))
        if isinstance(value, dict) and value.get('type') == 'FeatureCollection':
            result['features'] = len(value['features'])
            result['crs'] = value.get('crs', {'name': 'EPSG:4326 (GeoJSON)'})
    return result


def package(root, manifest):
    """Engineering evidence is an immutable proposal, never a production release."""
    required = ['city', 'asset_id', 'engineering_revision', 'assumptions', 'artifacts']
    if any(k not in manifest for k in required):
        raise ValueError('Incomplete engineering manifest')
    result = dict(schema='osr-engineering-evidence/1', **manifest, review_status='unreviewed')
    result['artifacts'] = [artifact(root, r['path'], r['tool'], r['tool_version']) for r in manifest['artifacts']]
    result['sha256'] = digest(result)
    return result


def execution_proposal(engineering, mapping):
    """Explicit eBOM/quantity -> production mapping, including units/allowances."""
    if engineering.get('sha256') != digest({k: v for k, v in engineering.items() if k != 'sha256'}):
        raise ValueError('Engineering package was changed')
    if not mapping.get('review_reference') or mapping.get('engineering_sha256') != engineering['sha256']:
        raise ValueError('Reviewed conversion must reference exact engineering package')
    if not mapping.get('items'):
        raise ValueError('Explicit native ERP Item mappings required')
    for item in mapping['items']:
        for key in ['component_type_id', 'erp_item_code', 'uom', 'inspection_reference', 'drawing_reference']:
            if not item.get(key):
                raise ValueError('Incomplete item mapping: ' + key)
        if item.get('production_bom') and not item.get('conversion_rule'):
            raise ValueError('Production BOM requires reviewed conversion rule, including process allowances')
    result = dict(schema='osr-execution-proposal/1', engineering_sha256=engineering['sha256'],
                  city=engineering['city'], asset_id=engineering['asset_id'], engineering_revision=engineering['engineering_revision'],
                  mapping=mapping, status='review-required', automatic_order_release=False)
    result['sha256'] = digest(result)
    return result


def ifc_overlay(package, bindings):
    """Sidecar consumed by viewers/Bonsai; existing IFC GlobalIds are preserved."""
    objects = {o['global_id'] for a in package['artifacts'] for o in a.get('ifc_objects', [])}
    for binding in bindings:
        if binding['ifc_global_id'] not in objects:
            raise ValueError('IFC binding does not exist in the versioned model')
    return dict(schema='osr-ifc-overlay/1', engineering_sha256=package['sha256'], bindings=bindings)
