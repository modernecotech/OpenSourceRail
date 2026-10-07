#!/usr/bin/env python3
"""Publish current scope studies and label earlier catalogue appraisals.

Presentation is separate from the unchanged catalogue finance model. Receipt
refreshes are restricted to the documents this publisher changes and their
dependent hash records; unrelated drift is never cleared.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
from copy import deepcopy
import csv
import hashlib
import json
import os
from pathlib import Path
import re
import sys
import tomllib

ROOT = Path(__file__).resolve().parents[2]
CONFIG = ROOT/'lib/templates/city-publication.toml'
sys.path.insert(0, str(ROOT/'design/city-generation/src'))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from osr_scenario.network_readme import render_readme
from city_access import transfer_audit

BEGIN = '<!-- OSR CURRENT SCOPE CONTEXT -->'
END = '<!-- END OSR CURRENT SCOPE CONTEXT -->'


def sha(raw):return hashlib.sha256(raw).hexdigest()
def read(path):return json.loads(path.read_text())
def encoded(data):return (json.dumps(data,indent=2,sort_keys=True)+'\n').encode()
def link(path, directory):return Path(os.path.relpath(path,directory)).as_posix()
def table(headers,rows):
    return '\n'.join(['| '+' | '.join(headers)+' |','| '+' | '.join(['---']*len(headers))+' |',
        *['| '+' | '.join(str(x) for x in row)+' |' for row in rows]])


def without_context(text):
    return re.sub(re.escape(BEGIN)+r'.*?'+re.escape(END)+r'\n\n?', '', text, flags=re.S)


def reference_context(path, study):
    if path.parent.name=='Iraq' and path.name in ('NATIONAL-BRIEF.md','IRAQ-FUNDING-PROGRAMME.md'):
        from iraq_current_basis import current_basis, current_header, funding_document
        if path.name=='IRAQ-FUNDING-PROGRAMME.md':
            return funding_document(path.read_text()).encode()
        # National generator owns its complete current-scope table.
        return without_context(path.read_text()).encode()
    body=without_context(path.read_text())
    notice=(f'{BEGIN}\n> **Original catalogue or earlier scope reference.** '
        f'The figures and policies below retain their original assumptions; '
        f'they are not the latest Baghdad staffing, depot, procurement or funding basis. '
        f'See the [current Baghdad recalculation]({link(study/"README.md",path.parent)}) '
        f'and [current city summary]({link(study.parents[1]/"README.md",path.parent)}). '
        'National/portfolio totals have not been repriced with that conditional Baghdad option.\n'
        f'{END}\n\n')
    first,separator,rest=body.partition('\n\n')
    return (first+'\n\n'+notice+rest if separator else notice+body).encode()


def verify_study(study, root=ROOT):
    summary=read(study/'summary.json')
    for base,group in ((root,'sources_sha256'),(study,'outputs_sha256')):
        for relative,digest in summary[group].items():
            path=base/relative
            if not path.is_file() or sha(path.read_bytes())!=digest:
                raise ValueError('Current scope study is stale; reconcile its dependencies and regenerate it: '+str(path))
    return summary


def refresh_receipts(root, paths, planned):
    """Plan only hash substitutions justified by changed publication bytes.

    The recorded old hash must match the pre-publication bytes, or already
    match the planned new bytes. Model values and release flags are untouched.
    All planning completes before files are written; cycles fail closed.
    """
    original={p:p.read_bytes() for p in paths}
    old_hash={p:sha(raw) for p,raw in original.items()}
    old_hash.update({p:sha(p.read_bytes()) for p in planned})
    templates={p:json.loads(raw) for p,raw in original.items()}
    for _ in range(len(paths)+2):
        changed=False
        digests={p:sha(raw) for p,raw in planned.items()}
        for path,template in templates.items():
            data=deepcopy(template);updated=False
            def replace(mapping,key,target):
                nonlocal updated
                if target not in digests or mapping[key]==digests[target]:return
                if mapping[key]!=old_hash[target]:
                    raise ValueError('Unrelated/pre-existing receipt drift: '+str(path)+' -> '+str(target))
                mapping[key]=digests[target];updated=True
            def visit(value):
                if isinstance(value,list):
                    for child in value:visit(child)
                elif isinstance(value,dict):
                    for group in ('sources_sha256','outputs_sha256','external_outputs_sha256'):
                        hashes=value.get(group)
                        if isinstance(hashes,dict):
                            base=path.parent if group=='outputs_sha256' else root
                            for relative in hashes:
                                if isinstance(hashes[relative],str):replace(hashes,relative,(base/relative).resolve())
                    source_paths=value.get('source_paths');hashes=value.get('source_sha256')
                    if isinstance(source_paths,dict) and isinstance(hashes,dict):
                        for key,relative in source_paths.items():
                            if key in hashes and isinstance(relative,str):replace(hashes,key,(root/relative).resolve())
                    if isinstance(value.get('path'),str) and isinstance(value.get('sha256'),str):
                        replace(value,'sha256',(root/value['path']).resolve())
                    for key,relative in list(value.items()):
                        if isinstance(relative,str) and isinstance(value.get(key+'_sha256'),str):
                            replace(value,key+'_sha256',(root/relative).resolve())
                    for child in value.values():visit(child)
            visit(data)
            if updated:
                raw=encoded(data)
                if planned.get(path)!=raw:planned[path]=raw;changed=True
        if not changed:return planned
    raise ValueError('Publication receipt dependency cycle')


def current_readme(city, study, selected, baseline):
    summary=read(study/'summary.json');case=read(study/(selected+'.json'));metrics=case['metrics']
    people=read(study/'workforce.json');depots=read(study/'depots.json');industry=read(study/'industry.json')
    alignment=read(study/'alignment.json');core=read(city/'engineering/alignment/core-realignment.json');buy=summary['finance_cases']['revised_scope_buy']
    design=tomllib.loads((city/'design.toml').read_text());fx=tomllib.loads((ROOT/'lib/templates/baghdad-programme-recalculation.toml').read_text())['model']['iqd_per_usd']
    sections={}
    for match in re.finditer(r'^## ([^\n]+)\n(.*?)(?=^## |\Z)',baseline,re.M|re.S):sections[match[1]]=match[0].strip()
    buckets=defaultdict(float)
    with (study/case['contract_schedule_file']).open() as handle:
        for row in csv.DictReader(handle):buckets[row['bucket']]+=float(row['budget_usd'])
    if abs(sum(buckets.values())-metrics['total_capital_usd'])>.02:raise ValueError('Published capital does not reconcile')
    capital_groups=[('Civil and bearing allowance',('civil','bearing_index_delta')),
        ('Stations and core elevated access',('stations','core_elevated_station_upgrade')),
        ('Rolling stock',('rolling_stock',)),('Final assembly and component plants',('production_plant','component_factory')),
        ('Line-local depots',('revised_depot',)),('Solar and charging',('solar_plant','charging_microgrid'))]
    grouped=[[label,sum(buckets[key] for key in keys)] for label,keys in capital_groups]
    covered={key for _,keys in capital_groups for key in keys}
    grouped.append(['Signalling and programme overhead',sum(value for key,value in buckets.items() if key not in covered)])
    rows=case['monthly']
    sources=[(label,currency,sum(r[key] for r in rows)) for label,currency,key in (
        ('Government import cash','USD','government_usd_cash'),('Government local cash','IQD','government_iqd_cash'),
        ('Chinese capital credit','USD','chinese_export_credit_draw_native'),('Ordinary capital bonds','IQD','domestic_bonds_draw_native'),
        ('Green capital bonds','IQD','green_bonds_draw_native'),('Senior bank capital credit','IQD','bank_credit_draw_native'),
        ('Conditional climate grant','IQD','climate_grant_iqd'))]
    if abs(sum(amount/(1 if currency=='USD' else fx) for _,currency,amount in sources)-metrics['total_capital_usd'])>.02:
        raise ValueError('Published native sources do not reconcile')
    selected_products=[p for p in industry['products'] if p['id'] in case['selected_component_factories']]
    funding_statement=(f"The model requires **IQD {metrics['unfunded_support_iqd']/1e12:.3f}tn unsourced support** in addition to assumed facilities" if metrics['unfunded_support_iqd']>.02*fx else "Assumed facilities cover the modelled cash deficits; their placement is uncommitted")
    first=min(p['opening_month'] for p in case['opening_phases']);last=max(p['opening_month'] for p in case['opening_phases'])
    prefix=link(study,city)
    text=f'''# Baghdad — Urban Rail Network

**Country:** IQ · **Population:** {design['city']['population']:,} · [Current Iraq planning basis](../NATIONAL-BRIEF.md)

**Current planning basis: {summary['as_of']} [programme recalculation]({prefix}/README.md), `{selected}` conditional local-production case.** The main route is the reworked city-centre elevated planning alignment; service remains a capacity-led assumption. Revised scope is unquoted and uncommitted; this is not a construction design or an operating release.

[Connected construction and battery study, 2026-10-06](engineering/connected-build/README.md) now reconciles island topology, 18 launchers/two shifts, supplier/logistics constraints, equipment cash and sodium alternatives. Its full-network energy duties report service shortfalls; supplier contracts, installed-rate credits and accessible-entrance coverage remain unqualified. The financial figures below are retained comparators and do not include an accepted accelerated-build saving.

Base programme planning allowance is **USD {metrics['total_capital_usd']/1e9:.3f}bn**, including line-local depots, final assembly and selected upstream component plants. {funding_statement}, and the case retains **IQD {metrics['terminal_all_debt_iqd']/1e12:.3f}tn terminal debt**. Local special/segmental structures, installed grid/charging upgrades, actual foundations, land and utilities remain unpriced. Removing search penalties establishes no realised saving. Older catalogue financial passes establish arithmetic for their own assumptions, not viability of this revised scope.

{sections['Network']}

Population access uses retained native count pixels where available; radial catchments require pedestrian/feeder validation. The former demand-score resident proxy is retired. [Access and transfers](engineering/access/README.md) · [Building, support and terrain clearance](engineering/clearance/README.md).

{sections['Energy']}
These energy quantities describe the current regenerated scenario. Zero annual residual grid import is an accounting balance, not accepted hourly autonomy. Depot charging/grid upgrades, duty and launch conflicts remain open.

## Current capital and operating people

{table(['Revised capital scope','USD equivalent million'],[[label,f'{value/1e6:,.3f}'] for label,value in grouped]+[['**Total programme**',f"**{metrics['total_capital_usd']/1e6:,.3f}**"]])}

There are **{depots['number_of_depots']} depots**, one per line, with **{depots['full_fleet_storage_slots']} storage slots** for all 111 m six-car trains plus clearance. Depot reference capital is **USD {depots['gross_reference_cost_usd']/1e6:.3f}m**, replacing the old USD 8m once. Workshop bays are sized separately by workload. The current case gives no capacity credit to station stabling. Actual land, foundations, connected access, installed charging and morning launch acceptance remain open. [Depot quantities]({prefix}/depots.json) · [Items]({prefix}/depot-items.csv).

The operating establishment is **{people['reference_required_fte']:,} FTE**, including **{people['station_cover']['station_cover_fte']:,} station-cover FTE**. Two staff per station and two normal eight-hour shifts give {people['station_cover']['normal_daily_shift_assignments']} daily shift assignments; retained 20.5-hour service also funds late cover and weekly/leave/training/sickness relief. Loaded annual payroll is **IQD {people['reference_annual_loaded_payroll_iqd']/1e9:.3f}bn**, with subsequent OPEX inflation. General pay starts at **IQD {people['wage_basis']['general_monthly_floor_iqd']:,.0f}/month**, 50% above the historical employee median indexed to 2026. Technical/supervisor/senior/director grades are separate; this is not a newly measured median. [Roles and wages]({prefix}/workforce.csv).
Final assembly has {industry['main_factory_production_fte']} production and {industry['main_factory_support_fte']} support FTE; selected upstream plants add {sum(p['production_fte'] for p in selected_products)} production and {sum(p['support_fte'] for p in selected_products)} support FTE. Their {industry['production_months']} paid production months are separate from permanent railway jobs. [Construction crew screen]({prefix}/construction-workforce.json) is incomplete; contractor labour is already inside contract rates.

## Iraqi manufacture and USD capital exposure

{table(['Product','Network quantity','Current case'],[[p['id'],p['network_quantity'],'Local process option' if p in selected_products else 'Bought component'] for p in industry['products']])}

Imported process machinery supports the selected Iraqi fabrication and assembly options shown above. Cells/BMS, wheels/axles/bearings, inverters and other critical inputs retain imports. Products with negative Baghdad-only whole-order margins remain bought in this case. Plant readiness/qualification within 18 months is assumed, not demonstrated. [Make/buy appraisal]({prefix}/component-make-buy.csv).

Compared with the matched bought-component case, capital changes from USD {buy['total_capital_usd']/1e9:.3f}bn to USD {metrics['total_capital_usd']/1e9:.3f}bn; imported invoice exposure changes from USD {buy['imported_invoices_usd']/1e9:.3f}bn ({buy['usd_capital_intensity']:.2%}) to USD {metrics['imported_invoices_usd']/1e9:.3f}bn (**{metrics['usd_capital_intensity']:.2%}**). The historical 148 km / USD 18bn proposal has a different scope and assumed all-USD funding; it is not a matched tender saving.

## Current funding and cashflows

Government capital is exactly **25%**. Imports use **50% government USD cash / 50% proposed Chinese USD credit**. Only Chinese debt is USD; the rest of government cash, bonds, bank/gap credit and mezzanine is IQD. Government invoice downpayments are scheduled within the total 25% contribution. FX is the historical planning anchor of IQD {fx:,.0f}/USD.

{table(['Capital-only source','Currency','Native amount'],[[label,currency,f'{amount:,.0f}'] for label,currency,amount in sources])}

Interest/fees, reserve cash, OPEX and gap facilities are additional cashflows, not capital added twice. Fares, kiosks, advertising, additional receipts and fare/OPEX indexation are included. Green/grant/rights terms and concessional gap credit remain uncommitted. Conditional first/full line revenue is month **{first} / {last}**; physical and financing gates are open.

The tested IQD mezzanine leaves {summary['finance_cases']['local_positive_mezzanine']['junior_defaulted_vintages']} defaulted draw vintages and increases terminal debt to IQD {summary['finance_cases']['local_positive_mezzanine']['terminal_all_debt_iqd']/1e12:.3f}tn. It does not establish sustainable repayment. [Monthly cashflow]({prefix}/{selected}-monthly.csv) · [Six-month bond/loan placements]({prefix}/{selected}-semiannual.csv) · [All {len(summary['finance_cases'])} cases]({prefix}/README.md) · [Cost and demand review]({link(ROOT/'docs/baghdad-cost-and-demand-review-2026-10-05.md',city)}).

## City-centre elevated alignment

The main design uses straight core radial tangents and broad curved ring connections where the retained water evidence permits them, inside the explicit {core['core']['south']}–{core['core']['north']}°N / {core['core']['west']}–{core['core']['east']}°E study area. Shoreline detours retain their separate curve and structure review gates. Land sections there are elevated; water crossings remain bridges. The final water-constrained core routes change from **{core['core_original_length_m']/1000:.3f} km to {core['core_final_route_length_m']/1000:.3f} km**. The main network is **{sum(l['length_m'] for l in design['lines'])/1000:.3f} route km**, with **{alignment['current_elevated_fraction']:.2%} elevated** across the whole system. Maps, station placement, fleet, civil quantities, staff and finance use that reworked design. [Analytical controls and limitations](engineering/alignment/core-realignment.json).

![Earlier corridors and current central alignment](engineering/alignment/core-alignment-comparison.png)

Property/air rights, obstacles, protected sites, surveyed heights, utilities, piers, foundations, transition curves and vertical alignment remain open. Existing outer approaches retain street/raster bends; exceptional geometry still requires realignment or special products. Additional outer grade-separation sensitivities add {alignment['candidate_extra_elevated_m']/1000:.3f} km and retain current dates; they are not the adopted core geometry or an achieved routing-penalty saving.

## Evidence, original references and regeneration

[Complete proposal PDF](Baghdad-Proposal.pdf) · [Editable proposal](BAGHDAD-PROPOSAL.md) · [Supporting data](Baghdad-Proposal-Supporting-Data.zip) · [Planning-only ERP drafts]({prefix}/erp-planning-drafts.json) · [Original catalogue finance](engineering/finance/FUNDING-MODEL.md) · [Original depot/stabling screen](engineering/depot-scope/README.md). Simulation, energy and asset evidence uses the current reworked geometry; the new staffing/depot/factory plans do not create accepted sites, appointed employees or operational assets.

Auto-planned by the OpenSourceRail design pipeline. Shared assumptions are in the [deployment planning reference]({link(ROOT/'docs/deployment-planning-reference.md',city)}). Inputs: [design](design.toml), [scenario](baghdad.toml), [map](baghdad-network-map.png), [package evidence](package-manifest.json). City-local [simulation](engineering/simulation/validation-summary.json), [energy](engineering/energy/summary.json), [GIS](engineering/gis/summary.json), [operations](operations/acceptance-evidence-report.md) and [delivery](engineering/delivery/README.md) retain their recorded planning/release gates.

For presentation-only updates, run `.venv/bin/python tools/automation/publish-city-summary.py`; add `--check` to detect drift. The city regeneration pipeline uses this publisher. A stale scope study stops publication rather than silently restoring the original cost headline. Publication provenance is in [publication-manifest.json](publication-manifest.json).
'''
    return text.encode()


def current_catalogue_context(design_path, baseline):
    city=design_path.parent
    if not (city/'alignment-policy.toml').is_file():return baseline
    d=tomllib.loads(design_path.read_text());core=read(city/'engineering/alignment/core-realignment.json')
    for relative,digest in core['sources_sha256'].items():
        if sha((ROOT/relative).read_bytes())!=digest:raise ValueError('Stale alignment input: '+relative)
    depot=read(city/'engineering/line-depots/summary.json');factory=read(city/'engineering/factory/summary.json')
    water=read(city/'engineering/alignment/station-water-screen.json')
    if not water['passed']:raise ValueError('Platform over mapped water in current city')
    for report in (depot,factory,water):
        for relative,digest in report['sources_sha256'].items():
            if sha((ROOT/relative).read_bytes())!=digest:raise ValueError('Stale current scope input: '+relative)
    retained=sum(run.get('geometry_basis')=='retained-raster-requires-geometry-review' for line in core['lines'] for run in line['core_runs'])
    context=f'''**Current alignment, depot and production basis.** Core corridors change from **{core['core_original_length_m']/1000:.3f} km to {core['core_final_route_length_m']/1000:.3f} km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. {retained} core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **{water['platforms_checked']} platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**{depot['number_of_depots']} line-local depots** provide **{depot['full_fleet_storage_slots']} full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **{factory['total_trainsets']} {factory['family']} trainsets / {factory['vehicle_modules']} cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

'''
    marker='Auto-planned by'
    i=baseline.find(marker)
    return baseline[:i]+context+baseline[i:] if i>=0 else baseline+context


def access_context(design_path, baseline):
    """Correct public accounting without changing certified operating inputs."""
    design=tomllib.loads(design_path.read_text())
    city=design_path.parent
    path=city/'engineering/access/summary.json'
    report=read(path) if path.is_file() else None
    graph=transfer_audit(design)
    if report:
        for relative,digest in report['sources_sha256'].items():
            source=ROOT/relative
            if not source.is_file() or sha(source.read_bytes())!=digest:
                raise ValueError('Stale access accounting: '+relative)
        if report['transfers']!=graph:raise ValueError('Changed transfer topology')
    population=report['population'] if report else {'status':'unavailable','catchments':[]}
    selected=next((row for row in population['catchments'] if row['radius_m']==800),None)
    population_text=(f"{selected['covered_population_2020']:,.0f} (2020 raster; {selected['fraction_of_raster_population']:.1%} of bbox)"
                     if selected and selected['fraction_of_raster_population'] is not None else 'unavailable — native population evidence required')
    fmt=lambda value:f'{value:.1%}' if value is not None else 'unavailable'
    baseline=re.sub(r'^\| Coverage / transfer reachability \|.*$',
        '| Direct transfers / reachable line pairs | '+fmt(graph['direct_transfer_fraction'])+' / '+fmt(graph['reachable_line_pair_fraction'])+' |',baseline,flags=re.M)
    baseline=re.sub(r'^\| Estimated station catchment \|.*$',
        '| Residents within 800 m radial station catchments | '+population_text+' |',baseline,flags=re.M)
    if report and report.get('input_findings'):
        for finding in report['input_findings']:
            baseline=baseline.replace('## Network\n',f"**Input discrepancy:** {finding['finding']} [Evidence]({finding['evidence']}).\n\n## Network\n",1)
        baseline=baseline.replace('**Country:** SD','**Recorded country:** SD (jurisdiction mismatch; see below)')
    details=('Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. '
             '[Population radii, denominator and transfer paths](engineering/access/README.md) · '
             '[Viaduct beam, foundation and terrain checks](engineering/clearance/README.md). '
             'Capital figures are base planning allowances: route-search scores are excluded from money, while special structures and installed-price gaps remain open. '
             '[Cost boundary](../../../../../docs/finance/civil-allowance-boundary.md).')
    return re.sub(r'^(Auto-planned.*)$',lambda match:match[0]+' '+details,baseline,count=1,flags=re.M)


def publish(design, scenario, output, *, check=False, allow_stale_evidence=False):
    registry=tomllib.loads(CONFIG.read_text())['city']
    entry=next((e for e in registry if (ROOT/e['directory']/'design.toml').resolve()==design.resolve()),None)
    baseline=access_context(design,render_readme(design,scenario,allow_stale_evidence=allow_stale_evidence and entry is None))
    if not entry:
        expected=current_catalogue_context(design,baseline).encode()
        if check:
            if not output.is_file() or output.read_bytes()!=expected:raise ValueError('Stale catalogue README: '+str(output))
        else:output.write_bytes(expected)
        return
    city=design.parent;study=city/entry['study'];verify_study(study)
    controls=read(city/'engineering/alignment/core-realignment.json')
    for relative,digest in controls['sources_sha256'].items():
        if sha((ROOT/relative).read_bytes())!=digest:raise ValueError('Stale alignment control source: '+relative)
    references=[city/p for p in entry['references']]+[ROOT/p for p in entry['portfolio_references']]
    planned={p:reference_context(p,study) for p in references}
    # Only hash-bearing reports can participate; financial row data remains unchanged.
    paths=[]
    for path in [*city.rglob('*.json'),*(city.parent/'finance').glob('*.json')]:
        if path.parent==city and path.name in ('manifest.json','archive-manifest.json','publication-manifest.json','package-manifest.json','appendix-sources.json','national-context.json'):continue
        data=read(path)
        if isinstance(data,dict) and any(key in data for key in ('sources_sha256','outputs_sha256','external_outputs_sha256','sources','source_sha256')):paths.append(path)
    planned=refresh_receipts(ROOT,paths,planned)
    # The text uses numerical data, which receipt refresh cannot change.
    planned[output]=current_readme(city,study,entry['case'],baseline)
    manifest=city/'publication-manifest.json'
    sources={p.relative_to(ROOT).as_posix():sha(p.read_bytes()) for p in (Path(__file__),CONFIG,design,scenario,
        ROOT/'design/city-generation/src/osr_scenario/network_readme.py')}
    for path in (city/'engineering/access/summary.json',city/'engineering/clearance/summary.json',ROOT/'tools/automation/city_access.py'):
        if path.is_file():sources[path.relative_to(ROOT).as_posix()]=sha(path.read_bytes())
    study_summary=study/'summary.json'
    sources[study_summary.relative_to(ROOT).as_posix()]=sha(planned.get(study_summary,study_summary.read_bytes()))
    receipt=dict(schema=1,case=entry['case'],scope='Baghdad current study; original reference math and release gates retained',
        sources_sha256=sources,reference_bodies_sha256={p.relative_to(ROOT).as_posix():sha(without_context(p.read_text()).encode()) for p in references},
        outputs_sha256={p.relative_to(ROOT).as_posix():sha(planned.get(p,p.read_bytes())) for p in [*references,*paths,output]})
    planned[manifest]=encoded(receipt)
    if check:
        for path,raw in planned.items():
            if not path.is_file() or path.read_bytes()!=raw:raise ValueError('Stale published city/context: '+str(path))
        stored=read(manifest)
        for relative,digest in stored['outputs_sha256'].items():
            if sha((ROOT/relative).read_bytes())!=digest:raise ValueError('Changed publication output: '+relative)
        print('Current city summary, reference contexts and publication hashes pass')
    else:
        for path,raw in planned.items():path.write_bytes(raw)
        verify_study(study)
        print(f'Published {city.name} current scope and {len(references)} original-reference contexts')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--design',type=Path,default=ROOT/'cities/catalogue/west-asia/Iraq/Baghdad/design.toml')
    parser.add_argument('--scenario',type=Path);parser.add_argument('--out',type=Path);parser.add_argument('--check',action='store_true')
    parser.add_argument('--allow-stale-evidence',action='store_true',help='audit view for catalogue-only cities; current scope studies still require valid evidence')
    args=parser.parse_args();slug=tomllib.loads(args.design.read_text())['city']['slug']
    publish(args.design.resolve(),(args.scenario or args.design.parent/(slug+'.toml')).resolve(),
        (args.out or args.design.parent/'README.md').resolve(),check=args.check,allow_stale_evidence=args.allow_stale_evidence)


if __name__=='__main__':main()
