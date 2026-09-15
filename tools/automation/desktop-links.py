#!/usr/bin/env python3
"""Bind existing station library objects and city GIS features to OSR positions."""
import argparse
import gzip
import json
from pathlib import Path
import re
import sys
import zipfile
from xml.etree import ElementTree

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'services/integration'))
from osr_integration.config import digest
from osr_integration.engineering import ifc_overlay


def build(package, engineering, bundle, cad, ifc, gis):
    with zipfile.ZipFile(cad) as archive:
        document = ElementTree.fromstring(archive.read('Document.xml'))
        object_names = [o.get('name') for o in document.findall('.//ObjectData/Object')]
    text = ifc.read_text()
    # Existing catalogue tag; preserve the owning IFC object's GlobalId.
    match = re.search(r"=IFCELECTRICDISTRIBUTIONBOARD\('([^']+)'[^\n]*'STN-CHG-P010'", text)
    if not match:
        raise ValueError('Existing station IFC lacks charger catalogue tag STN-CHG-P010')
    feature_ids = {f['properties']['id'] for f in json.loads(gis.read_text())['features']}
    bindings = []
    for a in package['equipment']:
        if a['equipment_type'] != 'charger': continue
        station = next(r for r in bundle['assets'] if r['asset_id'] == a['site_id'])
        if station['source_id'] not in feature_ids:
            raise ValueError('OSR station identity missing in GIS')
        bindings.append(dict(asset_id=a['asset_id'], component_type_id=a['component_type_id'],
            ifc=[match[1]], ifc_global_id=match[1],
            freecad=[n for n in object_names if n.startswith('STN_CHG_P010_') or n=='Installed_STN_CHG_P010'],
            gis=[station['source_id']],
            scope='reference-library object mapped to city position; site placement remains reviewed engineering work'))
    # A reference model reused at several stations needs a selected site; avoid ambiguity.
    return dict(schema='osr-desktop-links/1', city=package['city'], environment=package['environment'],
                engineering_sha256=engineering['sha256'], supervisory_sha256=package['sha256'],
                ifc_overlay=ifc_overlay(engineering, bindings), bindings=bindings)


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('city');a=p.parse_args()
    import importlib.util
    spec=importlib.util.spec_from_file_location('supervision',ROOT/'tools/automation/supervision.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    path,_=module.cities.catalogue()[a.city];base=ROOT/'build/supervision'/a.city
    package=json.loads((base/'simulation/package.json').read_text());engineering=json.loads((base/'engineering.json').read_text())
    bundle=json.loads(gzip.decompress((path.parent/'operations'/f'{a.city}-operations.json.gz').read_bytes()))
    result=build(package,engineering,bundle,ROOT/'design/component-catalogue/models/cad/stations/station-terminal.FCStd',ROOT/'engineering/models/bim/reference/stations/station-terminal.ifc',path.parent/'engineering/gis/layers/stations.geojson')
    (base/'desktop-links.json').write_text(json.dumps(result,indent=2)+'\n')
    print(base/'desktop-links.json')

if __name__=='__main__':main()
