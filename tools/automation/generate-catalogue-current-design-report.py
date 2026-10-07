#!/usr/bin/env python3
"""Audit regenerated comparison cities without exporting Baghdad's funding case."""
from __future__ import annotations
import argparse
import csv
import hashlib
import io
import json
import math
from pathlib import Path
import sys
import tomllib

ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'design/city-generation/src'),str(ROOT/'tools/automation')]
from osr_scenario.network_readme import _workforce_payroll_usd
from finance_evidence import stale_finance_sources
from planning_ci_evidence import current as planning_execution_current
import importlib.util
_water_spec=importlib.util.spec_from_file_location('catalogue_water',ROOT/'tools/automation/generate-station-water-screen.py')
water=importlib.util.module_from_spec(_water_spec);_water_spec.loader.exec_module(water)
OUT=ROOT/'engineering/assurance/catalogue-current-design'
DOC=ROOT/'docs/catalogue-current-design-review.md'


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def read(path):return json.loads(path.read_text())


def check_charging_requirement(design, policy, slug):
    """A regenerated default cannot replace a controlled city requirement."""
    required=policy.get('charging',{}).get('station_cabinet_count')
    actual=design['costs']['technology_basis']['station_charging_cabinet_count']
    if required is not None and actual!=required:
        raise ValueError('Controlled charging requirement mismatch: '+slug)


def audit(city_slugs=None):
    rows=[];sources={};countries={};programme_rows=[]
    catalogue=ROOT/'lib/city-batches/world-sample.toml'
    sources[catalogue.relative_to(ROOT).as_posix()]=sha(catalogue)
    entries={c['slug']:c for c in tomllib.loads(catalogue.read_text())['cities']}
    geography_path=ROOT/'engineering/assurance/catalogue-geography/summary.json'
    geography=read(geography_path)
    if not geography['passed'] or geography['cities_checked']!=len(entries):raise ValueError('Incomplete catalogue geography audit')
    if geography['generator_sha256']!=sha(ROOT/'tools/automation/audit-city-geography.py') or geography['water_constraint_generator_sha256']!=sha(ROOT/'tools/automation/water-route-constraints.py'):
        raise ValueError('Stale catalogue geography generator')
    sources[geography_path.relative_to(ROOT).as_posix()]=sha(geography_path)
    geography_cities={row['city']:row for row in geography['cities']}
    for design in sorted((ROOT/'cities/catalogue').glob('*/*/*/design.toml')):
        d=tomllib.loads(design.read_text());slug=d['city']['slug'];city=design.parent
        if slug=='baghdad' or (city_slugs is not None and slug not in city_slugs):continue
        geographic=geography_cities[slug]
        if not geographic['passed'] or geographic['design_sha256']!=sha(design) or geographic['corridor_sha256']!=sha(city/(slug+'.corridor.geojson')):
            raise ValueError('Stale or failed city geography: '+slug)
        overrides=city/'design-overrides.toml'
        if overrides.exists():
            check_charging_requirement(d,tomllib.loads(overrides.read_text()),slug)
            sources[overrides.relative_to(ROOT).as_posix()]=sha(overrides)
        infill_policy=city/'station-infill-policy.toml'
        if infill_policy.exists():
            infill_report=city/'engineering/alignment/station-infill.json'
            for p in (infill_policy,infill_report):sources[p.relative_to(ROOT).as_posix()]=sha(p)
            for source,digest in read(infill_report)['sources_sha256'].items():
                if sha(ROOT/source)!=digest:raise ValueError('Stale station infill source: '+slug)
                sources[source]=digest
        entry=entries[slug];family={l['rolling_stock'] for l in d['lines']}
        if len(family)!=1:raise ValueError('Mixed family without a configured factory: '+slug)
        paths=[design,city/(slug+'.toml'),city/'README.md',city/'alignment-policy.toml',city/'package-manifest.json',
               *[city/'engineering'/p for p in ('alignment/core-realignment.json','line-depots/summary.json','factory/summary.json','finance/summary.json')]]
        for p in paths:
            if not p.is_file():raise ValueError('Incomplete regenerated city: '+str(p))
            sources[p.relative_to(ROOT).as_posix()]=sha(p)
        manifest=read(city/'package-manifest.json')
        if not manifest['planning_example_complete'] or manifest['stale_analysis_sources']:
            raise ValueError('City example incomplete or stale: '+slug)
        if manifest['operational_release']:raise ValueError('Concept must not claim operational release: '+slug)
        if manifest['generator_sha256']!=sha(ROOT/'tools/automation/generate-city-package-manifest.py'):
            raise ValueError('Stale package generator: '+slug)
        for relative,receipt in manifest['artifacts'].items():
            if sha(city/relative)!=receipt['sha256']:raise ValueError('Package artifact drift: '+slug+': '+relative)
        simulation_path=city/'engineering/simulation/validation-summary.json'
        if not planning_execution_current(design,simulation_path):
            raise ValueError('Stale or incomplete source-bound native planning execution: '+slug)
        execution_path=simulation_path.with_name('ci-execution.json')
        sources[execution_path.relative_to(ROOT).as_posix()]=sha(execution_path)
        sources.update(read(execution_path)['inputs'])
        simulation=read(simulation_path)
        for case in simulation['runs']+simulation['resilience_cases']:
            if case['execution_receipt']['inputs']['simulator_sha256']!=simulation['simulator_sha256']:
                raise ValueError('Operating cases used different simulator builds: '+slug)

        core=read(city/'engineering/alignment/core-realignment.json')
        water_screen=water.screen(design,check=True)
        if not water_screen['passed']:raise ValueError('Platform over mapped water: '+slug)
        depot=read(city/'engineering/line-depots/summary.json');factory=read(city/'engineering/factory/summary.json')
        fin=read(city/'engineering/finance/summary.json')
        for r in (core,water_screen,depot,factory):
            for source,digest in r['sources_sha256'].items():
                if sha(ROOT/source)!=digest:raise ValueError('Stale scope source for '+slug+': '+source)
        if stale_finance_sources(fin,ROOT):raise ValueError('Stale country finance: '+slug)
        fleet=sum(f['trainset_count'] for f in d['fleets'])
        if len(d['lines'])!=len(d['depots']) or fleet!=depot['full_fleet_storage_slots'] or fleet!=factory['total_trainsets']:
            raise ValueError('Line/fleet/depot/factory inventory mismatch: '+slug)
        if d['costs']['depots_usd']!=depot['gross_reference_cost_usd']:
            raise ValueError('Depot capital mismatch: '+slug)
        profiles=tomllib.loads((ROOT/'lib/templates/rolling-stock.toml').read_text())['profiles']
        if factory['vehicle_modules']!=fleet*profiles[next(iter(family))]['cars']:
            raise ValueError('Factory car count differs from controlled family: '+slug)
        planned={site['line']:site['storage_slots'] for site in depot['sites']}
        if planned!={f['line']:f['trainset_count'] for f in d['fleets']}:
            raise ValueError('Per-line depot stock mismatch: '+slug)
        if factory['family']!=next(iter(family)) or factory['readiness_months_from_ntp']!=18:
            raise ValueError('Wrong production family/readiness: '+slug)
        w=fin['workforce'];pay=_workforce_payroll_usd(w['groups_fte'],w['monthly_country_income_proxy_usd'])
        if not math.isclose(pay,w['annual_labour_usd'],abs_tol=.01) or not math.isclose(pay,fin['annual_opex_usd']['components']['labour'],abs_tol=.01):
            raise ValueError('Graded payroll mismatch: '+slug)
        if w['total_fte']!=sum(w['groups_fte'].values()):raise ValueError('Staff inventory mismatch: '+slug)
        expected=math.ceil(len(d['stations'])*2*w['service_hours_per_day']*365/w['productive_hours_per_fte_year'])
        if w['groups_fte']['station_platform']!=expected:raise ValueError('Station cover mismatch: '+slug)
        civil={k:math.fsum(s['to_station_m']-s['from_station_m'] for s in d['civil_segments'] if s['class']==k)/1000 for k in ('at-grade','elevated','bridge')}
        km=math.fsum(l['length_m'] for l in d['lines'])/1000
        if not math.isclose(math.fsum(civil.values()),km,abs_tol=.002):raise ValueError('Civil length mismatch: '+slug)
        row=dict(city=slug,country=d['city']['country'],family=next(iter(family)),lines=len(d['lines']),stations=len(d['stations']),
            planning_infill_stations=sum(s.get('anchor_kind')=='planning:infill' for s in d['stations']),route_km=round(km,4),elevated_km=round(civil['elevated'],4),bridge_km=round(civil['bridge'],4),trainsets=fleet,
            cars=factory['vehicle_modules'],depots=len(d['depots']),storage_slots=depot['full_fleet_storage_slots'],
            operating_fte=w['total_fte'],station_fte=w['groups_fte']['station_platform'],annual_payroll_usd=round(pay,2),
            city_capital_usd=round(fin['capex_usd']['reconciled_project_total'],2),shared_factory_envelope_usd=round(factory['plant_cost_envelope_usd'],2),
            retained_core_fragments=sum(run['geometry_basis']=='retained-raster-requires-geometry-review' for l in core['lines'] for run in l['core_runs']),
            planning_example_complete=True,operational_release=False)
        rows.append(row)
        if entry.get('programme_evidence',True) and slug!='lyon':
            programme_rows.append(row)
            country=countries.setdefault(str(d['city']['country']),dict(cities=0,largest_city_order_factory_envelope_usd=0))
            country['cities']+=1
            country['largest_city_order_factory_envelope_usd']=max(country['largest_city_order_factory_envelope_usd'],row['shared_factory_envelope_usd'])
    expected=len(entries)-1 if city_slugs is None else len(city_slugs)
    if len(rows)!=expected:raise ValueError('Catalogue inventory incomplete')
    sources[Path(__file__).relative_to(ROOT).as_posix()]=sha(Path(__file__))
    connected_pilots={}
    for name in ('Baghdad','Samawah','Amarah'):
        city=ROOT/'cities/catalogue/west-asia/Iraq'/name
        manifest_path=city/'engineering/connected-build/manifest.json'
        manifest=read(manifest_path)
        for base,key in ((ROOT,'source_sha256'),(manifest_path.parent,'output_sha256')):
            for relative,digest in manifest[key].items():
                if sha(base/relative)!=digest:raise ValueError('Stale connected pilot: '+name+': '+relative)
        sources[manifest_path.relative_to(ROOT).as_posix()]=sha(manifest_path)
        connected_pilots[name]=dict(manifest=manifest_path.relative_to(ROOT).as_posix(),
            engineering_qualified=False,operational_release=False)
    for helper in ('tools/automation/planning_ci_evidence.py','tools/automation/city-planning-ci.py'):
        sources[helper]=sha(ROOT/helper)
    report=dict(schema_version=1,status='complete-regenerated-planning-examples-not-construction-release',cities=rows,
        regenerated_other_city_count=len(rows),developing_world_other_city_count=len(programme_rows),
        excluded_baghdad_reason='Dedicated source-bound funding, make/buy and revised scope remain in the Baghdad publication; its funding terms are not exported.',
        countries=countries,connected_pilots=connected_pilots,sources_sha256=sources,passed=True,operational_release=False,
        limitations=['Core rectangles are design-centroid planning screens, not surveyed city-centre boundaries or property rights.',
                    'Unaccepted land, foundations, suppliers, installation, commissioning and independent-check gates remain open.',
                    'Country income proxies are retained estimates; graded wages are planning premiums, not observed payroll quotations.',
                    'Factory capital is a shared national allowance, not city capital; independent city-order envelopes do not demonstrate simultaneous national capacity.',
                    'Generic finance retains country terms and fixed-price steady-state sensitivities; Baghdad indexed monthly cashflows remain separate.',
                    'Native service screens retain station dispatch/staging; full-depot yard access, launch capacity and the transition to depot dispatch require separate validation.',
                    'Historical station-stabling studies retain their original geometry and source fingerprints; they cannot release these new layouts.'])
    return report


def outputs(report):
    rows=report['cities'];csv_io=io.StringIO();w=csv.DictWriter(csv_io,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    doc=['# Current design across the city catalogue','',
        f"**{report['regenerated_other_city_count']} other city examples regenerated**, including Lyon as a technical comparison; {report['developing_world_other_city_count']} are developing-world examples. Baghdad retains its dedicated funding and scope publication. All regenerated examples have complete source-bound planning packages. Construction and operational releases remain open.",'',
        'The adopted core concepts straighten radial routes where retained water evidence permits and use elevated land sections; short water crossings remain bridge candidates. Shoreline detours keep their actual lengths and geometry review gates. Rings remain in the controlled inventory and use analytical fillets where suitable. Retained unsuitable fragments keep their geometry and special-product review gates. Cell-centre conversion is inverted explicitly, including the last raster row and column. Immutable seeds retain the original controlled geometry and capture revision.', '',
        'The independent catalogue geography audit covers all 266 cities, including Baghdad: zero wet platforms, zero missed checked dry line junctions and zero unapproved water runs above the 1 km planning limit. Full-resolution centreline exports preserve shoreline detours, and map markers use actual platform coordinates. Historical WorldCover samples and retained OSM geometry remain planning evidence; footprints, bank access, transfer levels and crossing structures require separate releases. [Geography audit](../engineering/assurance/catalogue-geography/README.md).', '',
        'Each line has one full-fleet planning depot sized to its train count and consist length. Storage slots and maintenance bays are separate. Storage roads hold up to three sets; the last road can be shorter, while the land screen retains a rectangular envelope. Depot PV/storage equipment is included once in depot capital; land, utility and installation quotations remain open. Native station dispatch does not validate a full-depot launch.', '',
        'Every listed station/platform record has two posts and two normal eight-hour shifts, with additional cover for the actual service window. Interchange platform nodes are counted separately. FTE cover deducts leave, training, sickness and handover from paid hours. Wages start at 150% of the retained country income proxy; technical and management roles have higher premiums, plus employer/overtime allowances. Finance and role totals reconcile.', '',
        'Factories are sized to each city order and family. Facility readiness is 18 months; qualification and serial manufacture follow it. Integrated openings wait when an 18-month facility, qualification, production or the physical test-path limit is the critical path. Infrastructure deadlines remain distinct from integrated targets. The national brief counts shared factory capital once, using its module allowance or the larger physical city-order envelope. National sequencing and concurrent capacity remain uncommitted.', '',
        'Every city retains actual source-bound native outputs for the two-hour trace, full nominal service day and eight full-day degraded cases. Aggregate software planning screens pass the unchanged thresholds. Per-line service, depot launch, physical acceptance and operating qualification remain separate release gates.', '',
        'Connected span, station, construction, battery and delivery-evidence studies are also generated for [Baghdad](../cities/catalogue/west-asia/Iraq/Baghdad/engineering/connected-build/README.md), [Samawah](../cities/catalogue/west-asia/Iraq/Samawah/engineering/connected-build/README.md) and [Amarah](../cities/catalogue/west-asia/Iraq/Amarah/engineering/connected-build/README.md). These city-specific pilots use the declared hypothetical fleet and Iraqi supply assumptions. They establish no supplier commitment, engineering acceptance or adopted accelerated saving in country finance.', '',
        'Country finance assumptions stay local. Baghdad’s government share, Chinese credit, IQD bonds and indexed monthly programme are not copied into other cities. Generic finance remains a fixed-price steady-state screen, with fares and commercial income at its recorded country assumptions. Earlier operating studies remain historical diagnostics.', '',
        '[Full city quantities and costs](../engineering/assurance/catalogue-current-design/cities.csv) · [Source-bound audit](../engineering/assurance/catalogue-current-design/summary.json) · [Catalogue index](../cities/catalogue/README.md)', '',
        '| Region/country code | Other programme cities | Largest city-order factory reference USD million |','|---|---:|---:|']
    doc += [f"| {name} | {v['cities']} | {v['largest_city_order_factory_envelope_usd']/1e6:.3f} |" for name,v in sorted(report['countries'].items())]
    doc += ['',*['- '+v for v in report['limitations']],'']
    return {OUT/'summary.json':(json.dumps(report,indent=2,sort_keys=True)+'\n').encode(),OUT/'cities.csv':csv_io.getvalue().encode(),DOC:'\n'.join(doc).encode()}


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--check',action='store_true');a=p.parse_args()
    r=audit()
    for path,raw in outputs(r).items():
        if a.check:
            if not path.is_file() or path.read_bytes()!=raw:raise ValueError('Stale catalogue audit: '+str(path))
        else:path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(raw)
    print('Catalogue current design: '+str(r['regenerated_other_city_count'])+' complete planning examples; releases open')
if __name__=='__main__':main()
