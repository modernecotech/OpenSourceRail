#!/usr/bin/env python3
"""Verify the maintained offline city maps and their source-bound context."""
from hashlib import sha256
import json
from pathlib import Path
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from engineering.city_maps import basemap, render

SVG = '{http://www.w3.org/2000/svg}'


def main():
    dossier = ROOT / 'docs/design-engine/city-dossiers'
    index_path = dossier / 'index.json'
    index = json.loads(index_path.read_bytes())
    index_manifest = json.loads((dossier / 'manifest.json').read_bytes())
    if index_manifest['files_sha256'].get('docs/design-engine/city-dossiers/index.json') != sha256(index_path.read_bytes()).hexdigest():
        raise ValueError('City catalogue index differs from its publication manifest')
    paths = sorted(ROOT / entry['path'] / 'city.json' for entry in index['cities'])
    actual = sorted((ROOT / 'cities/catalogue').glob('*/*/*/city.json'))
    if (len(paths) != index['city_count'] or len(paths) != index_manifest['city_count']
            or paths != actual):
        raise ValueError('City map inputs differ from the maintained dossier inventory')
    totals = {}
    places = tiles = 0
    for path in paths:
        city = path.parent
        design = json.loads(path.read_bytes())
        context_path = city / 'map-context.json.gz'
        context = basemap.load(context_path)
        corridor = city / (design['city']['slug'] + '.corridor.geojson')
        bounds, zoom = render.viewport(design, corridor)
        if not render.viewport_matches(bounds, zoom, context):
            raise ValueError('stale city viewport: ' + str(path))
        relative = context_path.relative_to(ROOT).as_posix()
        context_digest = sha256(context_path.read_bytes()).hexdigest()

        publication = city / 'engineering/outline'
        manifest = json.loads((publication / 'manifest.json').read_bytes())
        svg_path = publication / 'network.svg'
        if manifest['files_sha256'].get('network.svg') != sha256(svg_path.read_bytes()).hexdigest():
            raise ValueError('city map differs from its publication manifest: ' + str(svg_path))
        request = manifest['map_request']
        if (request['context']['path'] != relative or request['context']['sha256'] != context_digest
                or request['packet_id'] != manifest['atlas_packet_id']):
            raise ValueError('city map request differs from context or atlas packet: ' + str(svg_path))
        root = ET.parse(svg_path).getroot()
        metadata_node = root.find(SVG + 'metadata')
        if metadata_node is None or not metadata_node.text:
            raise ValueError('city map metadata missing: ' + str(svg_path))
        metadata = json.loads(metadata_node.text)
        if (metadata['context'] != request['context']
                or metadata['packet_id'] != request['packet_id']
                or metadata['rendering']['projection'] != 'local-equirectangular-111320'):
            raise ValueError('city map context, packet or projection differs: ' + str(svg_path))
        if root.findall('.//' + SVG + 'image'):
            raise ValueError('external/raster image dependency in city map: ' + str(svg_path))
        ids = {element.get('id'): element for element in root.iter() if element.get('id')}
        for layer in ('roads', 'water', 'landuse'):
            group = ids.get('context-' + layer)
            if context['layers'].get(layer) and (group is None or not any(
                    child.get('d') for child in group.iter() if child.tag == SVG + 'path')):
                raise ValueError('missing rendered city context geometry: ' + layer + ': ' + str(svg_path))
        for line in range(len(design['lines'])):
            route = ids.get(f'selected-route-{line}')
            if route is None or route.tag != SVG + 'path' or not route.get('d'):
                raise ValueError('missing selected route geometry: ' + str(svg_path))
        if not context['layers'].get('roads') or not context['layers'].get('places'):
            raise ValueError('missing roads/place context: ' + str(context_path))
        places += len(context['layers']['places'])
        tiles += len(context['receipt']['tiles'])
        for name, count in context['receipt']['feature_counts'].items():
            totals[name] = totals.get(name, 0) + count
    print(json.dumps(dict(city_maps=len(paths), offline=True,
                          projection='local-equirectangular-111320',
                          tiles=tiles, context_places=places, features=totals,
                          physical_clearance_accepted=False), sort_keys=True))


if __name__ == '__main__':
    main()
