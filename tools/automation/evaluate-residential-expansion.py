#!/usr/bin/env python3
"""Audit emitted stations after population-led route adoption, without forecasts."""
import argparse
import hashlib
import json
from pathlib import Path
import tomllib

from city_access import population_audit
from residential_route_expansion import CONFIG, encoded, population_inputs

ROOT=Path(__file__).resolve().parents[2]


def evaluate(path,check=False):
    design=tomllib.loads(path.read_text());city=path.parent
    planning_path=city/'engineering/alignment/residential-line-expansion.json'
    if not planning_path.exists():return
    planning=json.loads(planning_path.read_text());cfg=json.loads(CONFIG.read_text())
    data,inputs,reason=population_inputs(city,design)
    actual=None;population=None
    if data is not None:
        import numpy as np
        population=population_audit(data['lat'],data['lon'],data['counts'],np.ones(len(data['counts']),dtype=bool),design,radii=[cfg['station_radius_m']])
        actual=population['catchments'][0]['fraction_of_raster_population']
    sources=[path,planning_path,CONFIG,Path(__file__),ROOT/'tools/automation/city_access.py',ROOT/'tools/automation/residential_route_expansion.py',*inputs]
    report=dict(schema='osr-residential-expansion-evaluation/1',city=design['city']['slug'],
                as_of=cfg['as_of'],line_count=len(design['lines']),station_count=len(design['stations']),
                added_line_count=planning['added_line_count'],target_radial_fraction=cfg['target_station_radial_fraction'],
                original_station_radial_fraction=planning.get('baseline_actual_station_radial_fraction'),
                actual_emitted_station_radial_fraction=actual,target_met=actual>=cfg['target_station_radial_fraction'] if actual is not None else None,
                population=population,unavailable_reason=reason,
                native_service_and_finance_regeneration_are_prerequisites=True,
                current_census_or_walkshed_claim=False,additional_paid_journeys=None,
                physical_release=False,operating_release=False,
                sources_sha256={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in sources})
    out=city/'engineering/alignment/residential-expansion-evaluation.json';raw=encoded(report)
    if check:
        if not out.exists() or out.read_bytes()!=raw:raise ValueError('Stale emitted-station expansion evaluation: '+str(out))
    else:out.write_bytes(raw)
    print(design['city']['slug']+': '+(f'{actual:.1%} retained population near emitted stations' if actual is not None else 'population evidence unavailable'))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--design',type=Path,required=True);parser.add_argument('--check',action='store_true')
    args=parser.parse_args();evaluate(args.design.resolve(),args.check)
