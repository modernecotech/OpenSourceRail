#!/usr/bin/env python3
"""Bind delivered sections, OD capacity, costs, line openings and retained finance."""
import argparse
from collections import Counter,defaultdict
from copy import deepcopy
import csv
import gzip
import hashlib
import io
import json
from pathlib import Path
import sys
import tomllib

ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'design/component-catalogue/src'),str(ROOT/'tools/automation')]
from osr_mech.coupled_scenario import allocate_od,line_opening,OPENING_PACKAGES
from osr_mech.workload_staffing import workload_staffing,recruitment_backplan
from osr_mech.vehicle_mass_properties import mass_properties
from osr_mech.station_capacity import passenger_pulses
from osr_mech.pack_thermal import thermal_duty
from osr_mech.depot_dispatch import yard_dispatch
from osr_mech.service_trace import decode_sections
from osr_mech.provenance import stable_sum as sum,input_revision
from baghdad_delivery_closure import reconstruct_inputs
from baghdad_funding_analysis import capital_projection
from baghdad_recalculation_finance import simulate

CITY=ROOT/'cities/catalogue/west-asia/Iraq/Baghdad'
SOURCE=ROOT/'design/programme/coupled-case.json'
OUT=CITY/'engineering/coupled-programme'


def read(path):return json.loads(path.read_text())
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def precision(value,key=''):
    if isinstance(value,dict):return {k:precision(v,k) for k,v in value.items()}
    if isinstance(value,list):return [precision(v,key) for v in value]
    if isinstance(value,float):
        result=round(value,2 if key.endswith(('_usd','_iqd','_native')) else 8)
        return 0. if result==0 else result
    return value
def encoded(value):return (json.dumps(precision(value),indent=2,sort_keys=True,allow_nan=False)+'\n').encode()


def requests_for_case(design,scenario,movement,control,capacity,load,fare):
    """Declared cohorts at dispatch nodes; ring destination is halfway around.

    This provides a reproducible sensitivity, not a substitute for surveyed OD.
    Each energy case sees the same planned demand, including missed departures.
    """
    opportunities={r['id']:(r['line'],r['station'],r['heading'],r['minute']) for r in control['missed_dispatches']}
    opportunities.update({r['id']:(r['line'],r['start_station'],r['heading'],r['start_minute']) for r in control['journeys']})
    requests=[];route_distances={};routes={}
    for line in design['lines']:
        ordered=sorted((s for s in design['stations'] if s['line']==line['name']),key=lambda s:s['s_m'])
        for heading in ('forward','reverse'):
            routes[(line['name'],heading)]=ordered if heading=='forward' else list(reversed(ordered))
            route_distances[(line['name'],heading)]=sum(e['distance_m'] for e in movement['sections'] if e['line']==line['name'] and e['heading']==heading)/1000
    planned_km=0.
    for uid,(line,station,heading,minute) in sorted(opportunities.items()):
        route=routes[(line,heading)];shape=next(l['shape'] for l in design['lines'] if l['name']==line)
        if shape=='ring':
            pos=next(i for i,s in enumerate(route) if s['id']==station);destination=route[(pos+max(1,len(route)//2))%len(route)]['id']
        else:destination=route[-1]['id']
        requests.append(dict(id=uid,arrival_minute=minute,passengers=int(capacity[line]*load),fare_iqd=fare,
            legs=[dict(line=line,heading=heading,from_station=station,to_station=destination)]))
        planned_km+=route_distances[(line,heading)]
    return requests,planned_km


def build(compare=None):
    cfg=read(SOURCE)
    if cfg['schema']!='osr-coupled-programme/1' or cfg['authority_acceptance']:
        raise ValueError('only the controlled unaccepted programme study is supported')
    design_path=CITY/'design.toml';scenario_path=CITY/'baghdad.toml'
    design=tomllib.loads(design_path.read_text());scenario=tomllib.loads(scenario_path.read_text())
    connected=CITY/'engineering/connected-build';control=read(connected/'energy-control.json')
    movement=read(connected/'movement-profiles.json');civil=read(connected/'civil.json')
    energy=read(connected/'energy.json');minutes=energy['duration_minutes'];factor=365*1440/minutes
    reference=CITY/'engineering/programme-recalculation/local_positive.json';retained=read(reference)
    phases=retained['opening_phases'];finance_path=CITY/'engineering/finance/summary.json';finance=read(finance_path)
    settings=tomllib.loads((ROOT/'lib/templates/baghdad-programme-recalculation.toml').read_text());fx=settings['model']['iqd_per_usd']
    paths={k:ROOT/v for k,v in dict(funding='lib/templates/iraq-funding.toml',options='lib/templates/baghdad-finance-options.toml',
        programme='cities/catalogue/west-asia/Iraq/finance/baghdad-programme.json',finance=str(finance_path.relative_to(ROOT)),
        factory='cities/catalogue/west-asia/Iraq/Baghdad/engineering/factory/summary.json',risk_config='lib/templates/baghdad-delivery-risk.toml',
        stress='cities/catalogue/west-asia/Iraq/Baghdad/engineering/delivery-risk/summary.json',operations='cities/catalogue/west-asia/Iraq/Baghdad/operations/baghdad-operations.json.gz',
        reference='cities/catalogue/west-asia/Iraq/Baghdad/engineering/financing-redesign/reference.json').items()}
    inputs,_,_,_=reconstruct_inputs(paths)
    contracts_path=CITY/'engineering/programme-recalculation/local_positive-contracts.csv'
    with contracts_path.open() as stream:contracts=list(csv.DictReader(stream))
    capital=capital_projection(contracts,inputs['config'],set(inputs['options']['green']['candidate_buckets']))
    baseline=[]
    for row in retained['monthly']:
        baseline.append(dict(month=row['month'],phases=phases,revenue_usd=row['revenue_iqd']/fx,opex_usd=row['opex_iqd']/fx,
            restricted_working_capital_usd=max(0,row['closing_buffer_iqd']/fx-row['opex_iqd']/fx*settings['financing']['operating_buffer_months'])))
    reproduced=simulate(capital,baseline,inputs['config'],inputs['options'],settings)
    for key in ('total_capital_usd','terminal_cash_iqd','unfunded_support_iqd','terminal_all_debt_iqd'):
        if abs(reproduced['metrics'][key]-retained['metrics'][key])>.1:raise ValueError('retained ledger reconstruction differs: '+key)
    capacities={l['name']:tomllib.loads((ROOT/'lib/templates/rolling-stock.toml').read_text())['profiles'][l['rolling_stock']]['passenger_capacity'] for l in design['lines']}
    train_caps={f"{f['line']}-train-{i+1:03d}":capacities[f['line']] for f in scenario['fleets'] for i in range(f['trainset_count'])}
    fare=finance['revenue_basis']['single_trip_fare_usd']*fx
    closure=CITY/'engineering/delivery-closure';power=read(closure/'site-energy.json')
    rate=tomllib.loads((ROOT/'lib/templates/baghdad-delivery-baseline.toml').read_text())['energy']['import_purchase_usd_per_kwh']
    old_grid=sum((r['grid_import_kwh']+r['firm_purchase_topup_kwh'])*rate for r in power['cases']['reference']['sites'])
    old_rolling=finance['annual_opex_usd']['components']['rolling_stock_maintenance_including_battery_renewal_reserve']
    reserve=read(closure/'maintenance.json')['reference_annual_battery_reserve_usd'];variable_rolling=old_rolling-reserve
    old_components=read(closure/'finance-simple_span_bearing_index.json')['opex_components']
    outputs={};cases={};sensitivity=[];trace_sources=[]
    planning_requests,planned_km=requests_for_case(design,scenario,movement,control['cases']['lfp-throughout'],capacities,cfg['demand']['primary_load_fraction'],fare)
    for case_name,case in control['cases'].items():
        descriptor=case['section_event_trace'];trace=connected/descriptor['path'];trace_sources.append(trace)
        if sha(trace)!=descriptor['sha256']:raise ValueError('completed section trace changed')
        events=decode_sections(trace.read_bytes())
        if len(events)!=descriptor['rows']:raise ValueError('section trace row count differs')
        totals_by_load={};primary=None;primary_requests=None
        for load in cfg['demand']['load_fractions']:
            if not 0<load<=1:raise ValueError('load sensitivity must be in (0,1]')
            requests,expected_km=requests_for_case(design,scenario,movement,control['cases']['lfp-throughout'],capacities,load,fare)
            if cfg['demand']['od_requests']:requests=cfg['demand']['od_requests']
            allocated=allocate_od(events,requests,train_caps,[(a,b) for t in design.get('interchanges',[]) for a in t['platforms'] for b in t['platforms'] if a!=b])
            totals_by_load[str(load)]=allocated['totals']
            sensitivity.append(dict(case=case_name,load_fraction=load,**allocated['totals'],annualisation_factor=factor))
            if load==cfg['demand']['primary_load_fraction']:primary=allocated;primary_requests=requests
        if primary is None:raise ValueError('primary load must be included in sensitivities')
        line_fares=defaultdict(float)
        cohort_lookup={r['id']:r for r in primary_requests}
        for row in primary['cohorts']:
            if row['id'] in cohort_lookup:line_fares[cohort_lookup[row['id']]['legs'][0]['line']]+=row['recognised_fare_iqd']*factor/fx
            else:raise ValueError('OD result does not match its controlled request')
        annual_grid=case['totals']['grid_kwh']*factor;annual_km=sum(r['completed_train_km'] for r in case['service_by_line'].values())*factor
        maintenance_ratio=annual_km/(planned_km*factor) if planned_km else 0
        op=deepcopy(baseline);diagnostics=[]
        first=min(p['opening_month'] for p in phases);last=max(p['opening_month'] for p in phases)
        for row,original,oldcomp in zip(op,inputs['operating'],old_components):
            month=row['month'];active=first<=month<last+inputs['config']['model']['operating_years']*12
            opened=sum(p['weight'] for p in phases if month>=p['opening_month']) if active else 0
            weight=inputs['config']['model']['phased_fixed_opex_share']+(1-inputs['config']['model']['phased_fixed_opex_share'])*opened if active else 0
            index=(1+inputs['options']['fares']['opex_inflation'])**(month//12)
            annual_fare_index=(1+inputs['options']['fares']['annual_increase'])**(month//12)
            fares=0.
            opening_months={p['line']:p['opening_month'] for p in phases}
            for cohort in primary['cohorts']:
                needed={leg['line'] for leg in cohort_lookup[cohort['id']]['legs']}
                ready=max(opening_months[line] for line in needed)
                if active and month>=ready:
                    age=(month-ready)//12;ramp=inputs['config']['model']['revenue_ramp'][min(age,len(inputs['config']['model']['revenue_ramp'])-1)]
                    fares+=cohort['recognised_fare_iqd']*factor/fx*ramp*annual_fare_index/12
            row['revenue_usd']=fares+original['nonfare_revenue_usd']
            energy_delta=(annual_grid*rate-old_grid)*weight*index/12
            maintenance_delta=variable_rolling*(maintenance_ratio-1)*weight*index/12
            row['opex_usd']+=energy_delta+maintenance_delta
            if row['opex_usd']<0:raise ValueError('replacement cost scopes exceed retained OPEX')
            diagnostics.append(dict(month=month,modelled_fares_iqd=fares*fx,retained_nonfare_iqd=original['nonfare_revenue_usd']*fx,
                grid_energy_cost_delta_iqd=energy_delta*fx,distance_maintenance_delta_iqd=maintenance_delta*fx,
                new_opex_iqd=row['opex_usd']*fx,restricted_factory_working_capital_iqd=row['restricted_working_capital_usd']*fx))
        result=simulate(capital,op,inputs['config'],inputs['options'],settings)
        fields=('month','revenue_iqd','opex_iqd','senior_service_iqd_equivalent','closing_gap_iqd','unfunded_support_iqd',
            'closing_cash_iqd','closing_chinese_export_credit_native','closing_domestic_bonds_native','closing_bank_credit_native')
        outputs[f'finance-{case_name}.json']=encoded(dict(metrics=result['metrics'],monthly=[{k:r[k] for k in fields} for r in result['monthly']],
            operating_scope=diagnostics,capital_invoice_scope='retained local_positive; additional installed scope unpriced',
            full_line_opening_adopted=False,finance_baseline_replaced=False))
        outputs[f'demand-{case_name}.json']=encoded(primary)
        outputs[f'station-pulses-{case_name}.json']=encoded(dict(stations=passenger_pulses(primary['boarding_events']),
            one_lift_out_capacity_source='../connected-build/station-capacity.json',
            measured_lift_and_egress_criteria_missing=True,evacuation_and_assisted_rescue_accepted=False))
        cases[case_name]=dict(service_by_line=case['service_by_line'],demand_totals=primary['totals'],
            modelled_annual_grid_kwh=annual_grid,modelled_annual_train_km=annual_km,finance_metrics=result['metrics'],
            raw_journey_dispatches_are_not_fare_receipts=True,additional_fleet_and_charger_investment_usd=None,
            supplier_calibrated_lifetime_cost_usd=None,scenario_accepted=False)
    opening_rows=[]
    for name,case in civil['conditional_scenarios'].items():
        for row in case['opening_stages']:
            packages=deepcopy(cfg['opening']['packages_by_line'].get(row['line'],{}))
            packages.setdefault('running_structures',dict(completion_date=row['conditional_opening_date'],accepted=False,
                source='connected civil conditional running-span plus fitout date',installed_cash_usd=None))
            opening_rows.append(dict(case=name,**line_opening(row['line'],packages),packages=packages,
                retained_financial_opening_month=next(p['opening_month'] for p in phases if p['line']==row['line'])))
    outputs['line-opening-milestones.json']=encoded(dict(rows=opening_rows,common_financial_close_date=cfg['opening']['common_financial_close_date'],
        incomplete_packages_never_become_zero_duration=True,construction_is_not_revenue_opening=True))
    workforce=workload_staffing(cfg['workforce']['operations'],cfg['workforce']['calendar'])
    workforce['recruitment']=[dict(role=r['role'],**recruitment_backplan(cfg['workforce']['readiness_targets'].get(r['role']),r['required_establishment_fte'],cfg['workforce']['training'])) for r in workforce['roles']]
    outputs['workload-and-recruitment.json']=encoded(workforce)
    profiles=read(ROOT/'lib/templates/battery-profiles.json')['profiles']
    thermal_rows=[dict(id=row['id'],**thermal_duty(profiles[row['profile']],row['parameters'],row['steps'],
        initial_soc=row['initial_soc'],initial_temperature_c=row['initial_temperature_c'],soh=row['soh'])) for row in cfg['thermal_calibrations']]
    outputs['thermal-calibration-handoff.json']=encoded(dict(duties=thermal_rows,calibration_accepted=False,
        current_network_pack_heat_feedback_calibrated=False,missing_inputs=['heat capacity','cell loss map','cooling heat rejection','sensor location/calibration','aged and hot recovery traces']))
    yards=[dict(id=row['id'],**yard_dispatch(row['routes'],row['trains'],row['requests'],horizon_minutes=row['horizon_minutes'])) for row in cfg['yard_routes']]
    outputs['depot-routing-handoff.json']=encoded(dict(yards=yards,storage_rectangles_are_not_surveyed_routes=True,
        actual_route_switch_berth_charging_data_missing=not yards,canonical_endpoint_dispatch_replaced=False))
    outputs['pilot-evidence-packets.json']=encoded(dict(
        packets=[dict(id=identity,scope=scope,selected_supplier_and_exact_product=None,
            required_evidence={key:None for key in ('released_drawing','material_and_component_specification','licensed_process',
                'tooling_and_metrology','inspection_and_NDT','scope_separated_cost_offer','first_article_measurements','independent_acceptance')},
            existing_source=source,first_article_accepted=False,commercial_and_manufacturing_release=False)
            for identity,scope,source in (
                ('bogie-first-article','One supplier-supported bogie, surrounding approved interfaces and transfer process','../../../../../../../engineering/industrialisation/work-packages-and-erp-handoffs.json'),
                ('paired-viaduct-bay','One identified Pi20/Pi25 double-track bay, shared pier, foundation and all-stage erection proof','../connected-build/span-layout.json'),
                ('onboard-COTS-pilot','One exact host, harness, enclosure, power/thermal budget, frozen image and bench/HIL faults','../detail/register.json'))],
        supplier_offer_records=cfg['supplier_offers'],physical_first_article_records=cfg['physical_first_articles'],
        missing_evidence_never_becomes_a_pass=True))
    mass_ledger=ROOT/'design/component-catalogue/catalog/buildable-trainset/mass-closure-ledger.json';ledger=read(mass_ledger)
    products=ledger['product_rows'];required=[r['product_id'] for r in products if r['active_in_reference_configuration']]
    supports=cfg.get('mass_supports',dict(bodies=[],bogies=[]))
    outputs['mass-evidence-handoff.json']=encoded(mass_properties(cfg['mass_records'],required,supports['bodies'],supports['bogies']))
    outputs['summary.json']=encoded(dict(schema=1,status=cfg['status'],cases=cases,load_sensitivities=sensitivity,
        forecast_accepted=False,complete_accelerated_capital_usd=None,financial_close_date=cfg['opening']['common_financial_close_date'],
        retained_opening_months_are_explicit_sensitivity_only=True,retained_model_reconstruction_passed=True,
        fixed_solar_grid_connection_payroll_and_battery_reserves_retained=True,
        remaining_cost_calibration=['distance/time maintenance split','chemistry-specific renewal','phased site energy and idle fleets',
            'actual OD queues and transfer/refund policy','nonfare footfall effects','additional installed fleet chargers stations special scopes'],
        actual_collected_receipts_iqd=None,financial_baseline_replaced=False,operational_release=False))
    outputs['README.md']=('''# Coupled Baghdad programme study

**Unaccepted conditional study.** Completed native-timed section events feed capacity-limited OD itineraries, one net reference fare per completed journey, grid purchases, distance-sensitive maintenance and the existing native-currency financing engine. Departures and whole train circuits are not paid passenger journeys. Short OD trips can complete on a train whose full duty is later held. Transfers consume seats on all legs and recognise one fare.

The controlled demand is a 25/50/75% capacity-reservation sensitivity at dispatch nodes; it is not surveyed OD demand. Ring destinations are halfway around the ring. The primary 50% case uses the same demand across all three unqualified energy profiles. Actual queues, refunds, income uptake, equipment calibration and representativeness over an operating year remain open. Money is reported to cents after full-precision calculation.

[Summary](summary.json) links service, demand and financing. Three demand reports retain cohort outcomes and station boarding pulses. Three finance reports retain monthly receipts, OPEX, senior debt and supplemental support. The old ledger is reconstructed before any scope replacement. Electricity is replaced once; existing fixed solar/connection services and the battery reserve stay in scope. The residual rolling maintenance is treated as distance-sensitive solely as an uncalibrated sensitivity. Payroll and nonfare receipts remain explicit retained comparators. Additional vehicle, charger, station, special, installation and chemistry-specific renewal prices remain unknown. No revised national budget or financial baseline is adopted.

[Complete line-opening milestones](line-opening-milestones.json) require running structures, stations, specials/transitions, track, energy, depots, fleet, testing and approvals. Missing dates and prices stay unknown; a running-span finish cannot become a complete railway opening. Known bottlenecks and cash subtotals are shown separately. A common financial-close anchor and actual handovers are missing, so the finance cases retain their older opening months as explicit conditional assumptions.

[Workload and recruitment](workload-and-recruitment.json) derives establishment from measured role-hours, concurrency and productive calendar hours, then works backwards through recruitment, training batches, supervised practice and assessment capacity. Empty measurement and readiness inputs do not become funded headcounts or appointments. Native Task guards check construction, manufacturing and maintenance authority, role quantities, live resource state, shifts, rest and future reservations. Maintenance on unavailable equipment requires current isolation evidence. Training attendance is not work authority.

[Mass handoff](mass-evidence-handoff.json) keeps physical rows open. The reusable component model checks nonoverlapping included scope, uncertainty, locations, CG and individual axle reactions; no guessed CAD-envelope mass or selected vehicle startup is inserted. Supplier offers, first articles, surveyed yards, thermal calibration and accountable acceptance remain external evidence gaps.

Run `.venv/bin/python tools/automation/coupled-programme-study.py`; `--check` rejects drift. `--compare <previous summary.json>` writes a separate reviewable comparison of input locks and conclusion changes. [Manifest](manifest.json) binds source and output bytes; its revision is independent of its containing commit.
''').encode()
    sources=[SOURCE,Path(__file__),design_path,scenario_path,reference,contracts_path,finance_path,
        connected/'manifest.json',connected/'energy-control.json',connected/'energy.json',connected/'civil.json',connected/'movement-profiles.json',
        closure/'site-energy.json',closure/'maintenance.json',closure/'finance-simple_span_bearing_index.json',mass_ledger,
        ROOT/'lib/templates/rolling-stock.toml',ROOT/'lib/templates/baghdad-programme-recalculation.toml',ROOT/'lib/templates/baghdad-delivery-baseline.toml',
        ROOT/'tools/automation/baghdad_funding_analysis.py',ROOT/'tools/automation/baghdad_recalculation_finance.py',
        ROOT/'design/component-catalogue/src/osr_mech/coupled_scenario.py',ROOT/'design/component-catalogue/src/osr_mech/workload_staffing.py',
        ROOT/'design/component-catalogue/src/osr_mech/vehicle_mass_properties.py',*paths.values(),*trace_sources]
    sources += [ROOT/'lib/templates/battery-profiles.json',ROOT/'design/component-catalogue/src/osr_mech/station_capacity.py',ROOT/'design/component-catalogue/src/osr_mech/service_trace.py',
        ROOT/'design/component-catalogue/src/osr_mech/pack_thermal.py',ROOT/'design/component-catalogue/src/osr_mech/depot_dispatch.py',
        ROOT/'design/component-catalogue/src/osr_mech/provenance.py']
    hashes={p.relative_to(ROOT).as_posix():sha(p) for p in sources}
    outputs['manifest.json']=encoded(dict(schema=1,sources_sha256=hashes,source_revision=input_revision(hashes),
        outputs_sha256={n:hashlib.sha256(v).hexdigest() for n,v in outputs.items()},engineering_and_financial_adoption=False))
    if compare:
        previous=read(compare);old_manifest=read(compare.with_name('manifest.json'))
        return outputs,dict(changed_inputs=[p for p,h in hashes.items() if old_manifest['sources_sha256'].get(p)!=h],
            previous_conclusions=previous.get('cases'),current_conclusions=cases,
            conclusion_bytes_changed=encoded(previous)!=outputs['summary.json'])
    return outputs,None


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--check',action='store_true');parser.add_argument('--compare',type=Path)
    args=parser.parse_args();outputs,difference=build(args.compare)
    if args.check:
        stale=[n for n,data in outputs.items() if not (OUT/n).is_file() or (OUT/n).read_bytes()!=data]
        if stale:raise SystemExit('stale coupled programme: '+', '.join(stale))
    else:
        OUT.mkdir(parents=True,exist_ok=True)
        for name,data in outputs.items():(OUT/name).write_bytes(data)
    if difference:(OUT/'comparison.json').write_bytes(encoded(difference))
    print('Coupled service/OD/cost/finance and full-line milestone contract current; physical adoption open')

if __name__=='__main__':main()
