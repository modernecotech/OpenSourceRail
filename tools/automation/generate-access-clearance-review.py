#!/usr/bin/env python3
"""Publish a source-bound catalogue review of access and obstacle assumptions."""
from collections import Counter
import argparse
import hashlib
import json
from pathlib import Path
import tomllib

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'engineering/assurance/access-clearance'


def generate(check=False):
    rows=[];sources={Path(__file__).relative_to(ROOT).as_posix():hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    for design_path in sorted((ROOT/'cities/catalogue').glob('*/*/*/design.toml')):
        city=design_path.parent;design=tomllib.loads(design_path.read_text())
        reports={key:city/f'engineering/{key}/summary.json' for key in ('access','clearance')}
        values={key:json.loads(path.read_text()) for key,path in reports.items()}
        for path in reports.values():sources[path.relative_to(ROOT).as_posix()]=hashlib.sha256(path.read_bytes()).hexdigest()
        for value in values.values():
            for relative,digest in value['sources_sha256'].items():
                path=ROOT/relative
                if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest()!=digest:raise ValueError('Stale review source: '+relative)
        access=values['access'];clearance=values['clearance']
        rows.append(dict(city=design['city']['slug'],name=design['city'].get('name',city.name),
            directory=city.relative_to(ROOT).as_posix(),legacy_routing_demand=access['legacy_routing_score']['high_demand_cell_fraction'],
            population_status=access['population']['status'],population_catchments=access['population']['catchments'],
            input_findings=access.get('input_findings',[]),
            transfers=access['transfers'],beam_status=clearance['beam_building_status'],
            support_status=clearance['reference_support_status'],terrain_status=clearance['terrain_status'],
            terrain_available=clearance['terrain_available'],mapped_footprints=clearance['mapped_footprints'],
            known_height_footprints=clearance['known_height_footprints'],physical_release=False))
    statuses=Counter(row['population_status'] for row in rows)
    summary=dict(schema='osr-access-clearance-review/1',city_count=len(rows),population_status=dict(statuses),
        fully_connected_networks=sum(row['transfers']['reachable_line_pair_fraction']==1 for row in rows),
        terrain_available_cities=sum(row['terrain_available'] for row in rows),physical_release_count=0,
        sources_sha256=sources,cities=rows)
    links=lambda row,part:'../../../'+row['directory']+'/engineering/'+part+'/README.md'
    fmt=lambda value:f'{value:.1%}' if value is not None else 'unavailable'
    text='\n'.join(['# Population access, transfers and viaduct obstacle review','',
        f"All **{len(rows)} cities** retain separate population/transfer and beam/support/terrain reports. **{statuses['available']}** have usable native WorldPop 2020 count evidence; **{len(rows)-statuses['available']}** have explicit missing or zero-count evidence. No routing score is multiplied by city population.",'',
        f"**{summary['fully_connected_networks']}** line networks are fully connected through declared interchanges; **{len(rows)-summary['fully_connected_networks']}** retain disconnected components. Direct line-pair transfers are reported separately. Geometry crossing alone creates no passenger transfer.",'',
        'The historical demand score counts high-demand cells near tracks, including areas between stations; it is not population access. Native station catchment unions can be higher or lower. Radial distance ignores walking barriers; wider radii require feeder/walking evidence and do not create extra fare revenue. Source year, bounding-box denominator, native pixel resolution and nodata remain explicit.','',
        *[f"**Input finding — {row['name']}:** {finding['finding']} [Evidence]({finding['evidence']}).\n" for row in rows for finding in row['input_findings']],
        f"Terrain is retained for **{summary['terrain_available_cities']}** cities; gaps remain visible elsewhere. **Zero cities are physically obstacle-released.** Beam overflight, foundations and terrain are checked separately. Known provisional clashes and unknown heights require survey and design changes; no accepted route clearance or unpriced height increase is invented.",'',
        '| City | Routing-demand cells (legacy) | Population access | Direct transfers | Reachable line pairs | Clearance |',
        '|---|---:|---|---:|---:|---|',
        *[f"| {row['name']} | {fmt(row['legacy_routing_demand'])} | [{row['population_status']}; radius sensitivities](<{links(row,'access')}>) | {fmt(row['transfers']['direct_transfer_fraction'])} | {fmt(row['transfers']['reachable_line_pair_fraction'])} | [physical release blocked](<{links(row,'clearance')}>) |" for row in rows],'',
        '[Machine-readable aggregate and source hashes](summary.json) · [Common clearance policy](../../../docs/civil/viaduct-obstacle-clearance.md).',''])
    outputs={OUT/'summary.json':(json.dumps(summary,indent=2,sort_keys=True)+'\n').encode(),OUT/'README.md':text.encode()}
    if not check:OUT.mkdir(parents=True,exist_ok=True)
    for path,raw in outputs.items():
        if check:
            if not path.is_file() or path.read_bytes()!=raw:raise ValueError('Stale catalogue access/clearance review: '+str(path))
        else:path.write_bytes(raw)
    print(len(rows),'cities;',dict(statuses),'population;',summary['fully_connected_networks'],'fully connected networks')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--check',action='store_true')
    generate(parser.parse_args().check)
