#!/usr/bin/env python3
"""Publish source-bound city/country route additions and actual coverage gaps."""
import argparse
import csv
import hashlib
import io
import json
from pathlib import Path
import statistics
import tomllib

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'engineering/network-planning/catalogue'


def build():
    rows=[];sources={};countries={}
    for path in sorted((ROOT/'cities/catalogue').glob('*/*/*/design.toml')):
        design=tomllib.loads(path.read_text());city=path.parent
        report_path=city/'engineering/alignment/residential-expansion-evaluation.json'
        planning_path=city/'engineering/alignment/residential-line-expansion.json'
        report=json.loads(report_path.read_text());planning=json.loads(planning_path.read_text())
        for source,digest in report['sources_sha256'].items():
            if hashlib.sha256((ROOT/source).read_bytes()).hexdigest()!=digest:
                raise ValueError('Stale actual residential coverage input: '+source)
        for p in [path,report_path,planning_path]:sources[p.relative_to(ROOT).as_posix()]=hashlib.sha256(p.read_bytes()).hexdigest()
        row=dict(city=design['city']['slug'],recorded_country=design['city']['country'],
                 original_lines=planning['original_line_count'],current_lines=len(design['lines']),
                 added_lines=planning['added_line_count'],route_km=round(sum(l['length_m'] for l in design['lines'])/1000,4),
                 added_route_km=round(planning.get('added_route_m',0)/1000,4),stations=len(design['stations']),
                 original_station_radial_fraction=report['original_station_radial_fraction'],
                 actual_station_radial_fraction=report['actual_emitted_station_radial_fraction'],
                 target_radial_fraction=report['target_radial_fraction'],target_met=report['target_met'],
                 population_evidence='available' if report['actual_emitted_station_radial_fraction'] is not None else 'unavailable',
                 new_lines_are_planning_inventory=True,physical_release=False,operating_release=False)
        rows.append(row);countries.setdefault(row['recorded_country'],[]).append(row)
    native_counts=sum(r['population_evidence']=='available' for r in rows)
    summary=dict(schema='osr-residential-network-catalogue/1',as_of='2026-10-09',cities=len(rows),
                 countries=len(countries),cities_with_additional_lines=sum(r['added_lines']>0 for r in rows),
                 additional_lines=sum(r['added_lines'] for r in rows),native_population_available=native_counts,
                 native_population_unavailable=len(rows)-native_counts,actual_target_met=sum(r['target_met'] is True for r in rows),
                 physical_release=False,operating_release=False,
                 populations_are_not_summed_across_overlapping_city_bboxes=True,
                 country_codes_are_recorded_catalogue_jurisdictions_not_legal_boundary_acceptance=True,
                 sources_sha256=sources,city_results=rows)
    country_rows=[]
    for country,city_rows in sorted(countries.items()):
        fractions=[r['actual_station_radial_fraction'] for r in city_rows if r['actual_station_radial_fraction'] is not None]
        country_rows.append(dict(country=country,cities=len(city_rows),added_lines=sum(r['added_lines'] for r in city_rows),
            added_route_km=round(sum(r['added_route_km'] for r in city_rows),4),
            target_met_cities=sum(r['target_met'] is True for r in city_rows),
            population_unavailable_cities=sum(r['population_evidence']=='unavailable' for r in city_rows),
            city_coverage_median=round(statistics.median(fractions),8) if fractions else None))
    def encoded(value):return (json.dumps(value,indent=2,sort_keys=True)+'\n').encode()
    def table(data):
        buffer=io.StringIO();writer=csv.DictWriter(buffer,fieldnames=list(data[0]));writer.writeheader();writer.writerows(data)
        return buffer.getvalue().encode()
    text=['# Residential network additions across the catalogue','',
          'Controlled planning inventories and actual emitted-station population accounting; field and operating release remain open.','',
          f"All {len(rows)} city designs have a source-bound expansion/evaluation package. {summary['cities_with_additional_lines']} inventories contain added lines. Native population evidence is available for {native_counts} and unavailable for {len(rows)-native_counts}.",'',
          f"{summary['actual_target_met']} city inventories reach their 80% working station-circle target; every remaining gap is reported. The target is not declared met from proposed sites or a demand score.",'',
          'The [city register](cities.csv) records original/current line counts, added route quantities and actual station-circle fractions. The [country register](countries.csv) counts city programmes and reports the median city fraction; it is not national resident coverage. Population is never summed across potentially overlapping city bboxes. Recorded jurisdiction/source conflicts retain their explicit review gates.','',
          'Use each city alignment directory for immutable original design bytes, priority cells, common corridor connections, controlled terminal changes, native site/geometry reviews and actual emitted coverage. Country wages, fleet, depot, production, energy and finance models remain local. No Baghdad financing mix is transferred to another country.','',
          'Construction quantities, finite machine queues and line-opening dependencies follow the changed inventory. Public money, land, utilities, ground design, profiles, accessible walking routes, suppliers, prices, qualified workers and independent acceptance remain separate releases. These retained 2020 circles are not current census, observed passengers, funded feeder service or safe walking catchments.','',
          '[Regeneration method](../../../docs/civil/population-led-network-regeneration.md) · [Sources and complete city results](summary.json)','']
    return {OUT/'summary.json':encoded(summary),OUT/'cities.csv':table(rows),OUT/'countries.csv':table(country_rows),OUT/'README.md':'\n'.join(text).encode()}


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--check',action='store_true');args=parser.parse_args()
    for path,raw in build().items():
        if args.check:
            if not path.exists() or path.read_bytes()!=raw:raise ValueError('Stale residential network catalogue: '+str(path))
        else:path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(raw)
    print('Residential network catalogue: source-bound emitted coverage and remaining gaps current')
