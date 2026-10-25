#!/usr/bin/env python3
"""Offline map/context integrity, projection, source and catalogue coverage."""
from hashlib import sha256
import json
from pathlib import Path
import sys
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from engineering.city_maps import basemap,render


def main():
    paths=sorted((ROOT/'cities/catalogue').glob('*/*/*/city.json'))
    if not paths:raise ValueError('city catalogue required')
    totals={};labels=0;tiles=0
    for path in paths:
        context_path=path.with_name('map-context.json.gz')
        context=basemap.load(context_path)
        report=json.loads((path.parent/'engineering/maglev/summary.json').read_bytes())
        design=json.loads(path.read_bytes())
        design['stations']=[s for line in report['lines'] for s in line['stations']]
        geo=path.with_name(design['city']['slug']+'.corridor.geojson')
        bounds,zoom=render.viewport(design,geo)
        if bounds!=context['bounds_wsen'] or zoom!=context['zoom']:raise ValueError('stale city viewport: '+str(path))
        relative=context_path.relative_to(ROOT).as_posix()
        if report['source_sha256'].get(relative)!=sha256(context_path.read_bytes()).hexdigest():raise ValueError('unbound basemap: '+str(path))
        svg=ET.parse(path.parent/'engineering/maglev/network.svg');ns={'s':'http://www.w3.org/2000/svg'}
        metadata=json.loads(svg.find('s:metadata',ns).text)
        if metadata['context_sha256']!=report['source_sha256'][relative]:raise ValueError('map context differs: '+str(path))
        if metadata['corridor_sha256']!=sha256(geo.read_bytes()).hexdigest():raise ValueError('map route differs: '+str(path))
        if metadata['current_stations_sha256']!=sha256(json.dumps(design['stations'],sort_keys=True).encode()).hexdigest():raise ValueError('map stops differ: '+str(path))
        if svg.findall('.//s:image',ns):raise ValueError('external/raster image dependency in city map')
        for layer in ('roads','water','buildings','labels'):
            if svg.find(f'.//s:g[@id="basemap-{layer}"]',ns) is None:raise ValueError('missing city layer: '+layer)
        if not context['layers'].get('roads') or not context['layers'].get('places'):raise ValueError('missing roads/place context')
        label_nodes=svg.findall('.//s:g[@id="basemap-labels"]/s:text',ns)
        if not label_nodes:raise ValueError('map has no rendered place labels')
        labels+=len(label_nodes)//2;tiles+=len(context['receipt']['tiles'])
        for name,count in context['receipt']['feature_counts'].items():totals[name]=totals.get(name,0)+count
    print(json.dumps(dict(city_maps=len(paths),offline=True,projection='EPSG:3857',
        tiles=tiles,rendered_labels=labels,features=totals,physical_clearance_accepted=False),sort_keys=True))


if __name__=='__main__':main()
