#!/usr/bin/env python3
"""Publish the actual city-sized industrial requirement from its operations twin."""
from __future__ import annotations
import argparse
import csv
import gzip
import hashlib
import io
import json
import math
from pathlib import Path
import tomllib

ROOT=Path(__file__).resolve().parents[2]
CITY=ROOT/'cities/catalogue/west-asia/Iraq/Baghdad'
OUT=CITY/'engineering/factory'


def csv_text(rows):
    out=io.StringIO(newline='');w=csv.DictWriter(out,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows);return out.getvalue()


def build():
    manifest=CITY/'operations/baghdad-operations-manifest.json'
    m=json.loads(manifest.read_text());payload=CITY/'operations'/m['file']
    if hashlib.sha256(payload.read_bytes()).hexdigest()!=m['compressed_sha256']:
        raise ValueError('current operations payload required')
    b=json.loads(gzip.decompress(payload.read_bytes()));r=b['factory_sizing'];t=b['manufacturing_tasks']
    for source in b['project_twin']['sources'].values():
        path=ROOT/source['path']
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest()!=source['sha256']:
            raise ValueError('stale operations input: '+source['path'])
    config=tomllib.loads((ROOT/'lib/templates/baghdad-factory.toml').read_text())
    funding_path=ROOT/'lib/templates/iraq-funding.toml'
    calendar=tomllib.loads(funding_path.read_text())['model']
    if config['factory']['working_days_per_year']!=calendar['working_days_per_year']:
        raise ValueError('factory and finance planning calendars must agree')
    capex=tomllib.loads((ROOT/'lib/templates/capex-costs.toml').read_text())
    # A quoted physical expansion may replace this planning budget later; the
    # current city-sized envelope must not be disguised as free added capacity.
    existing=r['vehicle_modules']*capex['production_plant']['per_vehicle_usd']
    r['legacy_module_plant_allowance_usd']=existing
    r['budgeted_plant_direct_usd']=max(existing,r['plant_cost_envelope_usd'])
    r['budgeted_plant_epc_usd']=r['budgeted_plant_direct_usd']*capex['overhead']['epc_fraction']
    r['incremental_plant_capex_with_epc_usd']=(r['budgeted_plant_direct_usd']-existing)*(1+capex['overhead']['epc_fraction'])
    actual={line:max(x['planned_finish_day'] for x in t if x['asset_type']=='rolling-stock' and x['line']==line) for line in r['line_priority']}
    if actual!=r['line_stock_finish_working_day'] or max(actual.values())>r['infrastructure_target_working_day']:
        raise ValueError('factory sizing disagrees with the integrated task schedule')
    deliveries=[]
    for x in t:
        if x['package_id']=='rs-50-dynamic-commissioning':
            deliveries.append(dict(trainset=x['asset_id'],line=x['line'],working_day=x['planned_finish_day'],
                month_after_financial_close=math.floor((x['planned_finish_day']+calendar['pre_ntp_working_days'])*12/calendar['working_days_per_year']),cars=6,
                status='conditional-planned-acceptance-not-delivered'))
    deliveries.sort(key=lambda x:(x['working_day'],x['trainset']))
    if len(deliveries)!=r['total_trainsets'] or len({x['trainset'] for x in deliveries})!=len(deliveries):
        raise ValueError('fleet delivery identities/quantity do not reconcile')
    sources=[manifest,CITY/'design.toml',ROOT/'lib/templates/baghdad-factory.toml',ROOT/'lib/templates/capex-costs.toml',funding_path,
             ROOT/'tools/automation/factory_sizing.py',ROOT/'tools/automation/project_twin.py',
             ROOT/'tools/automation/generate-qa-maintenance-data.py',Path(__file__)]
    sources.extend(ROOT/s['path'] for s in b['project_twin']['sources'].values())
    r['sources_sha256']={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in sources}
    r['operations_payload_sha256']=m['compressed_sha256']
    r['schema']='org.opensourcerail.city-factory.v1'
    rows=[]
    for line in r['line_priority']:
        civil=r['infrastructure_deadlines'][line];stock=actual[line];finish=max(civil,stock)
        rows.append(dict(line=line,trainsets=sum(x['line']==line for x in deliveries),infrastructure_finish_day=civil,
            full_fleet_finish_day=stock,integrated_completion_day=finish,
            conditional_opening_month=math.floor((finish+calendar['pre_ntp_working_days'])*12/calendar['working_days_per_year'])+1+tomllib.loads(funding_path.read_text())['city_overrides']['baghdad']['model']['phased_commissioning_months'],
            fleet_delay_after_infrastructure_days=max(0,stock-civil)))
    def table(headers,values):return '\n'.join(['| '+' | '.join(headers)+' |','| '+' | '.join(['---']*len(headers))+' |',*['| '+' | '.join(map(str,v))+' |' for v in values]])
    line_one=next(x for x in r['civil_rephasing']['line_completions'] if x['line']=='line-1')
    text=f'''# Baghdad factory sized to the city programme

One factory is sized for **{r['total_trainsets']:,} complete six-car trainsets / {r['vehicle_modules']:,} cars**, with physical cells, crews and test paths. Facility readiness is **18 months from notice to proceed (working day {r['factory_ready_working_day']})**, replacing the old 24-month assumption. Financial close precedes NTP by 30 working days; these are conditional offsets, not dated construction commitments.

The unchanged infrastructure resource model finishes on working day **{r['infrastructure_target_working_day']}**. The sized flow accepts the final train on day **{r['stock_finish_working_day']}**, {r['infrastructure_target_working_day']-r['stock_finish_working_day']} working days earlier. Full-network commissioning therefore follows infrastructure completion, rather than waiting decades for four generic train-production slots. All **{r['total_trainsets']}** trains remain in the planned scope; there is no smaller opening-fleet substitution.

## Flow and physical capacity

Cycles explicitly represent a **whole six-car trainset**, with structural, electrical and fit-out allowances doubled from the old generic cycle. One eight-hour shift and 85% productive availability are assumed. Occupation is ceil(productive cycle / availability); availability is not deducted again from that output. The first complete train belongs to the {r['total_trainsets']} and carries an additional 60-working-day qualification allowance. Every remaining material-kit task depends on that first-article acceptance; no series release is assumed before day {r['serial_release_working_day']}.

{table(['Stage','Productive days','Occupied days','Cells/bays','Direct crew'],[(s['work_center'],s['cycle_working_days'],s['planned_occupation_days'],s['cells'],s['direct_crew_fte']) for s in r['stages']])}

The limiting steady capacity is **{r['minimum_steady_output_trainsets_per_year']:.1f} trainsets / {r['minimum_steady_output_trainsets_per_year']*6:.0f} cars per working year**. The resource scheduler simulates each train's linked stages, finite lanes and first-article gate. Cells are calculated from the city's fleet and the remaining infrastructure window, then increased to the first feasible balanced allocation; this is a reproducible capacity design, not a proof of minimum land or minimum cost.

Production bays use a 135 m by 6.5 m envelope for the 111 m consist, not a released building module. Composite and kitting cells have separate floor assumptions. Process and support space totals **{r['process_and_support_floor_m2']:,.0f} m²**. The site screen is **{r['planning_site_m2']/10000:.1f} hectares**, including circulation/storage and **{r['test_tracks']} independently segregated {r['test_track_length_m']/1000:.1f} km test paths**. These are site-reservation assumptions pending geometry, braking, fire, access, geotechnical and safe-operation design. Dynamic acceptance bays are not independent running tracks: the separate path calculation permits only **{r['exclusive_test_path_capacity_trainsets_per_year']:.1f} trainsets/year**, based on {r['exclusive_track_hours_per_trainset']:.0f} exclusive track-hours/train and 85% path availability. A shared route cannot be counted twice. The test-path margin above limiting production is only {r['exclusive_test_path_capacity_trainsets_per_year']/r['minimum_steady_output_trainsets_per_year']-1:.2%}; the final fleet has only {r['infrastructure_target_working_day']-r['stock_finish_working_day']} working days of schedule margin. See the [frozen-resource disruption, costed second-shift recovery and civil acceleration study](../delivery-risk/README.md). Those stresses preserve the selected cells rather than resizing them to hide delay.

Direct cell staffing totals **{r['direct_production_crew_fte']:,} positions per staffed shift** before management, stores, maintenance, relief and shift coverage. It is a proposed resource requirement, not measured job creation. Manufacturing labour and materials are already in train procurement CAPEX; they are not added again to plant CAPEX or railway OPEX.

## Line handover and the early-line constraint

{table(['Line','Full fleet','Infrastructure day','Fleet day','Opening month'],[(x['line'],x['trainsets'],x['infrastructure_finish_day'],x['full_fleet_finish_day'],x['conditional_opening_month']) for x in rows])}

The factory completes alongside the **overall city civil programme**. Full-fleet openings are retained. Noncritical infrastructure now moves within its existing crew lanes and dependency graph towards fleet handover, with a 90-working-day target buffer; critical infrastructure retains its original completion dates. Line 1's infrastructure completion moves from day {line_one['original_infrastructure_day']} to day {line_one['rephased_infrastructure_day']}, reducing the idle interval before its fleet from {line_one['original_idle_working_days']} to {line_one['rephased_idle_working_days']} working days. No rolling-stock date, task duration, resource count or opening date changes. This is a conditional investment-timing proposal: surveys, land, utilities, permits and contract dates require approval before deferring site work. [Original and rephased line reconciliation](civil-rephasing.csv) preserves both sets of dates. Line priority follows the original infrastructure requirements, with actual asset identifiers preserved.

The opening calculation retains the separate three-month integrated commissioning allowance after line infrastructure, the full fleet and shared depot/control work. The 60-day first-article allowance and three-month line allowance cover different activities. Required approvals, surveys, physical tests and independent acceptance remain open; neither allowance constitutes accepted safety evidence or an approved construction calendar.

## Eighteen-month facility construction sequence

{table(['Activity','Working days','Accountable role'],[(p['name'],p['days'],p['owner']) for p in r['construction_phases']])}

These six sequential planning packages total 390 working days. Long-lead tooling, cranes, battery handling equipment and imported systems must be ordered early enough to install and prove within that window. Land/access and financing availability are required at NTP. A delay to those gates changes the programme; the schedule is not a contractor-backed promise.

## Factory capital and cashflow

{table(['Physical budget allocation','USD million'],[(k.replace('_',' '),f'{v/1e6:,.3f}') for k,v in r['cost_allowances_usd'].items()])}

The physical envelope is **USD {r['plant_cost_envelope_usd']/1e6:,.3f} million direct**, compared with the old module allowance of USD {existing/1e6:,.3f} million. The programme budgets the larger amount, **USD {r['budgeted_plant_direct_usd']/1e6:,.3f} million plus USD {r['budgeted_plant_epc_usd']/1e6:,.3f} million EPC**, counted once. The resulting capital increase is **USD {r['incremental_plant_capex_with_epc_usd']/1e6:,.3f} million**; added bays are not treated as free capacity. Rates and quantities are engineering allocations requiring Iraqi contractor/vendor quotations, not market-verified prices. Actual equipment origin must also reconcile to the programme's imported/local allowances.

Factory payments are re-timed to the 390-day facility programme and city train payments follow the new production tasks. Baghdad's monthly debt, interest, 5% fare/OPEX indexing, liquidity gaps, surplus repayments and six-month bond/loan requirements are recalculated from those dates. Government remains 25% of capital; import cash and Chinese credit retain the 50:50 USD split, with remaining funding in IQD. The existing aggregate plant import allowance remains 20% of direct plant capital, allocated within tooling/test equipment rather than buildings; supplier origin and the actual equipment mix require RFQs and eligibility checks. EPC retains its separate procurement-origin allowance. Future national cities do not enter this plant's production load or Baghdad cashflow.

## Procurement and qualification requirements

Before release, obtain measured six-car labour routes and prototype cycle times; trainset-level supplier delivery schedules; released mould/fixture drawings and duplication plans; lifting/handling and HV/battery fire segregation; stores, quarantine and rework capacity; inspection/calibration capacity; crew recruitment and training; both independent test-path designs; utility availability; and a land/industrial permit package. Composite cells cannot be mistaken for the number of panel moulds: the final panel design and cure/release conditions determine mould duplication. The hypothetical whole-kit cycle must be validated against that tooling count. Existing civil precast/slab yards retain their own production resources and are not assigned to train bays.

The 85% factor is a deterministic allowance for non-productive time, not a quantified programme contingency. Supplier disruption, multi-month qualification, redesign and civil delays need risk scenarios before investment decisions. Expansion beyond Baghdad needs a new demand and capacity assessment; a national module budget is not a promise of parallel national production.

[Cell and tooling register](cells.csv) · [{r['total_trainsets']} planned trainset acceptances](deliveries.csv) · [Line handover reconciliation](line-completion.csv) · [Machine-readable calculation](summary.json) · [Factory capacity inputs](../../../../../../../lib/templates/baghdad-factory.toml)

Regenerate after operations with `.venv/bin/python tools/automation/generate-factory-plan.py`; validate the same command with `--check`. Status: reference planning engineering, no construction or manufacturing release.
'''
    return {'summary.json':json.dumps(r,indent=2,sort_keys=True)+'\n','README.md':text,'cells.csv':csv_text(r['stages']),
            'deliveries.csv':csv_text(deliveries),'line-completion.csv':csv_text(rows),'civil-rephasing.csv':csv_text(r['civil_rephasing']['line_completions'])}


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--check',action='store_true');args=parser.parse_args()
    outputs=build();OUT.mkdir(parents=True,exist_ok=True)
    for name,text in outputs.items():
        path=OUT/name
        if args.check:
            if not path.is_file() or path.read_text()!=text:raise ValueError('stale factory output: '+name)
        else:path.write_text(text)
    print('Baghdad factory plan '+('current' if args.check else 'generated'))

if __name__=='__main__':main()
