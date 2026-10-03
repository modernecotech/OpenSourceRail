"""Build Baghdad industrial RFQs, executable evidence and gated finance studies.

All reference packages are drafts. Measurements, quotations and signed lender
commitments are external evidence; generating a package never accepts it.
"""
from __future__ import annotations
import argparse
from copy import deepcopy
import csv
from datetime import date, datetime, timezone
import gzip
import hashlib
import json
import math
from pathlib import Path
import subprocess
import tomllib

from baghdad_delivery_stress import ROOT, CITY, schedule, finance, write_csv
from osr_scenario.iraq_finance import city_funding_config
from subsystem_qualification import authenticated_reviews

OUT = CITY / 'engineering/qualification'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fingerprint(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def save(name, value):
    (OUT / name).write_text(json.dumps(value, indent=2, sort_keys=True) + '\n')


def temporary_facility(factory, options, risk):
    stages = factory['stages'][:-1]
    cells = [dict(id='TFA-C%02d' % (i + 1), package=s['package'],
                  floor_m2=s['process_floor_m2'] / s['cells'],
                  tooling_usd=s['tooling_allowance_usd_per_cell'],
                  transfer_destination=s['work_center'],
                  readiness='unqualified', quotation_received=False)
             for i, s in enumerate(stages)]
    production = sum(c['floor_m2'] for c in cells)
    floor = production * (1 + options['support_floor_fraction'])
    site = floor * options['site_to_floor_factor']
    lines = [('shell_fitout', floor, 'm2', options['building_usd_per_m2']),
             ('serviced_site', site, 'm2', options['site_services_usd_per_m2'])]
    lines += [(c['id'], 1, 'cell', c['tooling_usd']) for c in cells]
    lines += [(key, 1, 'lot', options[key]) for key in ('utilities_usd', 'handling_transport_usd',
              'qualification_training_usd', 'transfer_reinstall_usd', 'vendor_interface_usd')]
    rfqs = [dict(id='BAG-TFA-RFQ-%02d' % (i + 1), package=label, quantity=q, unit=unit,
                 reference_unit_usd=rate, reference_total_usd=q * rate, quotation_received=False,
                 required_return='Price date, tax, origin, import content, lead time, interface drawings, commissioning, warranty and exclusions')
            for i, (label, q, unit, rate) in enumerate(lines)]
    subtotal = sum(r['reference_total_usd'] for r in rfqs)
    contingent = subtotal * options['contingency_fraction']
    allocated = subtotal + contingent
    allowance = risk['recovery']['temporary_first_article_direct_usd']
    if allocated > allowance:
        raise ValueError('Temporary facility reference exceeds the existing recovery allowance')
    return dict(status='reference-concept-unquoted', process_floor_m2=production, support_floor_m2=floor-production,
                total_floor_m2=floor, site_m2=site, cells=cells, rfqs=rfqs, priced_subtotal_usd=subtotal,
                contingency_usd=contingent, allocated_direct_usd=allocated,
                unallocated_allowance_usd=allowance-allocated, existing_direct_allowance_usd=allowance,
                epc_usd=allowance*risk['costs']['epc_fraction'], additional_capex_beyond_recovery_case_usd=0,
                temporary_ready_working_day=260, permanent_acceptance_ready_working_day=390,
                first_article_additional_qualification_days=60, site_selected=False, accepted=False)


def facility_layout(facility):
    # Metric blocks, not a surveyed plot: all zones fit a 180 m x 93 m envelope.
    blocks = [(5, 5, 25, 10, 'Kitting'), (35, 5, 135, 6.5, 'Structural six-car bay'),
              (5, 25, 40, 30, 'Composite / cure'), (35, 15, 135, 6.5, 'Body install'),
              (35, 60, 135, 6.5, 'Electrical / HV'), (35, 70, 135, 6.5, 'Fitout / static'),
              (50, 25, 30, 15, 'Battery quarantine'), (85, 25, 25, 15, 'HV / utilities'),
              (115, 25, 50, 15, 'Quality / stores'), (50, 45, 115, 10, 'Dispatch / access')]
    parts = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 525">',
             '<rect width="900" height="525" fill="white"/>',
             '<text x="25" y="22" font-family="sans-serif" font-size="16">Temporary first article: reference 180 x 93 m envelope; survey and fire/access design pending</text>',
             '<g transform="translate(0 40) scale(5)"><rect x="0" y="0" width="180" height="93" fill="#f4f7fb" stroke="#234" stroke-width="0.3"/>']
    for x, y, w, h, label in blocks:
        parts += [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#b8d7ed" stroke="#234" stroke-width="0.2"/>',
                  f'<text x="{x+1}" y="{y+min(4,h/2)}" font-family="sans-serif" font-size="2.5">{label}</text>']
    parts += ['<text x="5" y="88" font-family="sans-serif" font-size="2.7">Unallocated lanes / fire separation / welfare / transfer access require vendor and authority review.</text>', '</g></svg>']
    return '\n'.join(parts)


def section_study(design, scenario, payload, factory, context, options, risk):
    stations = sorted((r for r in design['stations'] if r['line'] == options['line']), key=lambda r:r['s_m'])[:options['station_count']]
    length = (stations[-1]['s_m']-stations[0]['s_m'])/1000
    consist = scenario['consist']
    running_minutes = 120 * length / options['average_running_kmh']
    intermediate_minutes = 2 * (len(stations)-2) * options['intermediate_dwell_seconds']/60
    terminal_minutes = 2 * options['terminal_charging_seconds']/60
    cycle = running_minutes + intermediate_minutes + terminal_minutes
    peak = math.ceil(cycle/options['headway_minutes'])
    spares = math.ceil(peak*options['spare_fraction'])
    fleet = peak+spares+1
    aux_kw = consist['car_count']*(consist['systems']['hvac_thermal_kw_per_car']+consist['systems']['lighting_power_w_per_car']/1000)+consist['roof_pv']['air_cleaner']['compressor_power_kw']
    traction_kwh = 2*length*consist['car_count']*consist['energy_kwh_per_car_km']
    duty_kwh = traction_kwh + aux_kw*cycle/60
    charging_kw = next(r for r in scenario['stations'] if r['id']==stations[0]['id'])['charging_power_kw']
    delivered = 2*charging_kw*options['charger_efficiency']*options['terminal_charging_seconds']/3600
    berths = math.ceil((options['terminal_charging_seconds']+options['terminal_clearance_seconds'])/(options['headway_minutes']*60))
    profile_name = 'metro-6car'
    profile = tomllib.loads((ROOT/'lib/templates/rolling-stock.toml').read_text())['profiles'][profile_name]
    nameplate = float(profile['onboard_battery_nameplate_kwh'])
    usable = float(profile['onboard_battery_kwh'])
    if consist['battery_capacity_kwh'] != nameplate or not 0 < usable <= nameplate:
        raise ValueError('Section battery differs from controlled six-car gross/usable profile')
    battery_window = usable*(1-options['minimum_soc'])
    charge_margin = delivered/duty_kwh-1
    if delivered < duty_kwh or duty_kwh/2 > battery_window:
        raise ValueError('Section duty fails reference charging or usable SOC envelope')
    station_ids = {r['id'] for r in stations}
    assets = [r for r in payload['assets'] if r['line']==options['line'] and r['asset_type']!='rolling-stock'
              and (r['station'] in station_ids or r['km_end'] and float(r['km_end']) <= length+.001)]
    asset_ids = {r['asset_id'] for r in assets}
    settings = dict(fixed_process_holds=risk['fixed_process_holds'], early_civil_assets=sorted(asset_ids))
    delivery = schedule(payload['manufacturing_tasks'], factory, settings)
    accepts = sorted((r for r in delivery['tasks'] if r['line']==options['line'] and r['manufacturing_uid'].endswith('rs-50-dynamic-commissioning')), key=lambda r:r['end_hour'])[:fleet]
    fleet_day = math.ceil(max(r['end_hour'] for r in accepts)/8)-1
    civil_day = math.ceil(max(r['end_hour'] for r in delivery['tasks'] if r['asset_id'] in asset_ids)/8)-1
    support_day = options['civil_and_support_ready_day']
    day = max(fleet_day, civil_day, support_day)
    opening = math.floor((day+30)*12/260)+1+3
    full_line = next(p for p in delivery['phases'] if p['line']==options['line'])
    if opening >= full_line['opening_month']:
        raise ValueError('First section does not create an earlier operating phase')
    capacity_weight = min(fleet/831, full_line['weight']*length/(next(l['length_m'] for l in design['lines'] if l['name']==options['line'])/1000))
    weight = capacity_weight*options['demand_fraction_of_capacity_proxy']
    full_line_month = full_line['opening_month']
    full_line['weight'] -= weight
    delivery['phases'].insert(0,dict(line=options['line']+'-first-section', opening_month=opening, weight=weight,
                                   fleet_completion_day=fleet_day, infrastructure_completion_day=max(civil_day,support_day)))
    direct = sum(options[k] for k in ('turnback_terminal_direct_usd','charging_grid_direct_usd','maintenance_access_direct_usd','controls_acceptance_direct_usd'))
    programme,city_finance=context[2],context[3]
    components=city_finance['annual_opex_usd']['components']
    length_share=length/(sum(l['length_m'] for l in design['lines'])/1000)
    salary=programme['comparison']['operating_labour_annual_iqd']/programme['comparison']['operating_fte']/1300
    annual_legs=2*options['service_hours_per_day']*60/options['headway_minutes']*options['service_days_per_year']
    annual_grid_kwh=annual_legs*duty_kwh/2/options['charger_efficiency']
    section_opex=dict(labour=options['operating_fte']*salary,
        civil_station_maintenance=components['civil_station_depot_maintenance']*length_share,
        rolling_stock_and_battery_reserve=components['rolling_stock_maintenance_including_battery_renewal_reserve']*fleet/831,
        solar_maintenance=components['solar_plant_maintenance']*length_share,
        signalling_maintenance=components['signalling_maintenance']*length_share,
        conservative_grid_energy=annual_grid_kwh*options['reference_grid_usd_per_kwh'],
        incremental_support_asset_maintenance=direct*1.07*options['additional_support_asset_annual_maintenance_fraction'])
    stabling_roads=math.ceil(fleet/2)
    rfqs=[dict(id='BAG-SEC-RFQ-01',package='Terminal adaptations and new turnback',quantity=2,unit='terminal',
               reference_direct_usd=options['turnback_terminal_direct_usd'],
               required_scope='Two 121 m berths per end; new line-1 fifth-station turnback and crossover; existing start-terminal turnback reused/adapted; swept path, braking, evacuation and works isolation'),
          dict(id='BAG-SEC-RFQ-02',package='Additional charging and feeder upgrades',quantity=2*(berths-1),unit='additional-2MW-charger',
               reference_direct_usd=options['charging_grid_direct_usd'],
               required_scope='Reuse one already-budgeted 2 MW charger at each end subject to qualification; add remaining berth chargers; upgrade each terminal to 4 MW simultaneous supply; protection, utility/grid agreement, degraded duty and BMS interface'),
          dict(id='BAG-SEC-RFQ-03',package='Independent maintenance, stabling and access',quantity=1,unit='site',
               reference_direct_usd=options['maintenance_access_direct_usd'],
               required_scope=f'{stabling_roads} stabling roads with two trains each; minimum 250 m usable road; two 135 x 6.5 m maintenance bays, welfare/stores, battery quarantine, certified lifting, rescue/towing access and 3.5 ha provisional site envelope; land rights not demonstrated'),
          dict(id='BAG-SEC-RFQ-04',package='Section control integration and acceptance',quantity=1,unit='section-dossier',
               reference_direct_usd=options['controls_acceptance_direct_usd'],
               required_scope='Isolated OCC and train/wayside configuration, telecom coverage, interlocking/turnback/charging interfaces, ERP serial maintenance and passenger/ticketing configuration, emergency exercises and independently signed opening dossier')]
    for row in rfqs:
        row.update(quotation_received=False,origin_verified=False,
                   excluded_existing_scope='Existing route/stations/wayside and all allocated trains remain in the original city budget; quote only adaptations/additional assets, identify reused equipment and remove overlap')
    settings.update(first_section_direct_usd=direct, first_section_ready_day=support_day,
                    first_section_support_fte=options['section_support_fte'], first_section_support_until_month=full_line_month,
                    first_section_annual_opex_usd=sum(section_opex.values()), first_section_opening_month=opening)
    result = finance(delivery, settings, context)
    return dict(status='separate-unqualified-first-section-option', line=options['line'], station_ids=[r['id'] for r in stations],
                route_km=length, headway_minutes=options['headway_minutes'], running_minutes=running_minutes,
                round_trip_minutes=cycle, peak_trains=peak, spare_trains=spares, cold_reserve=1, total_trainsets=fleet,
                allocated_existing_trainsets=[r['asset_id'] for r in accepts], ultimate_city_trainsets=831,
                terminal_berths_per_end=berths, charger_kw_per_berth=charging_kw,
                terminal_grid_kw_per_end=berths*charging_kw, terminal_charge_seconds=options['terminal_charging_seconds'],
                auxiliary_proxy_kw=aux_kw, round_trip_energy_kwh=duty_kwh, round_trip_charge_delivered_kwh=delivered,
                nameplate_battery_kwh=nameplate, usable_battery_kwh=usable,
                usable_soc_window_kwh=battery_window, minimum_soc=options['minimum_soc'],
                soc_basis='Section conservative 40% floor applied to the controlled 1080 kWh usable energy; nameplate is not dispatchable energy',
                round_trip_charging_margin_fraction=charge_margin, normal_duty_energy_margin_kwh=battery_window-duty_kwh/2,
                degraded_charge_margin_fraction=.9*delivered/duty_kwh-1,
                degraded_charge_qualified=False,
                energy_qualification='Conservative HVAC thermal-kW proxy as electric load; roof PV and intermediate charging excluded; supplier duty/heat/gradient tests pending',
                accelerated_existing_assets=sorted(asset_ids), civil_completion_day=civil_day,
                independent_support_ready_day=support_day, fleet_completion_day=fleet_day,
                conditional_opening_month=opening, full_line_opening_month=full_line_month,
                revenue_weight=weight, measured_catchment=False, accepted=False,
                extra_direct_capital_usd=direct, extra_capital_with_epc_usd=direct*1.07,
                rfqs=rfqs, independent_stabling_roads=stabling_roads,
                stabling_usable_road_m=250, maintenance_bays=2, provisional_maintenance_site_m2=35000,
                reference_annual_opex_usd=section_opex, operating_fte=options['operating_fte'],
                reference_mature_annual_revenue_usd=programme['operating_receipts']['total_annual_usd']*weight,
                reference_mature_annual_operating_balance_usd=programme['operating_receipts']['total_annual_usd']*weight-sum(section_opex.values()),
                reference_annual_grid_kwh=annual_grid_kwh,
                reference_support='Own fenced stabling for all section trains, rescue/towing access, two maintenance bays, lifting and battery quarantine, isolatable OCC/wayside/ERP interfaces; no dependency on line-6 depot',
                operations='Two terminal berths per end; 121 m clear platform for 111 m train; segregated service roads; No.9 crossover/points and 185 m safeguarded terminal envelope pending swept-path/braking survey',
                metrics=result['metrics']), result, delivery


def funding_placement(baseline, name, source, start, end, fraction, recovered):
    """Measure refused placement against requested baseline tranches, not a loan.

    Work/invoices are stopped separately in the recovered schedule. Available capital below is an undrawn placement-capacity scenario, not
    received cash, an operating ledger or a substitute USD credit line.
    """
    rows=[]; cumulative=0.; escrow=0.
    for r in baseline:
        month=int(r['month'])
        requested = float(r[source])
        blocked = start <= month <= end
        withheld = requested*(1-fraction) if blocked else 0.
        cumulative += withheld
        capital=float(r['capex_usd'])
        # Domestic funding is IQD; the export-credit requested column is USD.
        fx=1300. if source!='chinese_export_credit_draw_native' else 1.
        if blocked:
            available = capital-withheld/fx
            escrow += available
        release = cumulative if recovered and month==end+1 else 0.
        if release:escrow=0.
        rows.append(dict(month=month, requested_source_native=requested, placed_source_native=requested-withheld,
                         refused_source_native=withheld, replacement_placement_required_native=release,
                         deferred_original_invoice_usd=capital if blocked else 0.,
                         available_undrawn_capital_for_deferred_invoices_usd=escrow,
                         status='replacement-uncommitted' if release else ('procurement-and-construction-hold' if blocked else 'outside-stress-window')))
    return dict(case=name, currency='USD' if source=='chinese_export_credit_draw_native' else 'IQD',
                refused_native=cumulative, later_placement_assumed=recovered, placed_fraction_in_window=fraction,
                first_opening_month=None if not recovered else 'see-costed-recovery-case',
                permanent_refusal_blocks_programme=not recovered, debt_clearance_month_without_new_placement=None,
                existing_debt_not_forgiven=True, no_automatic_bridge_or_government_replacement=True), rows


def evidence_packages(register, factory, programme, section, sources):
    def c(label, operator, value, unit):
        return dict(id=label, operator=operator, target=value, unit=unit)
    criteria=[
      [*[c(s['package']+'-occupation','le',s['planned_occupation_days']*8,'working-hour') for s in factory['stages']],c('availability','ge',.85,'fraction'),c('first-article-qualification','ge',60,'working-day'),c('fixed-hold-shift-compression','eq',0,'working-hour')],
      [c('complete-qualified-kits','eq',831,'six-car-kit'),c('origin-and-invoice-coverage','eq',1,'fraction')],
      [c('competent-baseline-cell-staff','ge',1044,'FTE'),c('qualified-fatigue-roster','eq',1,'fraction')],
      [c('segregated-paths','ge',2,'path'),c('exclusive-running-test','ge',16,'hour/train'),c('qualified-throughput','ge',factory['minimum_steady_output_trainsets_per_year'],'train/year')],
      [c('survey-and-permit-coverage','eq',1,'fraction'),c('accepted-quantity-and-rate-coverage','eq',1,'fraction')],
      [c('temporary-ready','le',260,'working-day'),c('permanent-acceptance-ready','le',390,'working-day'),c('transfer-and-quote-coverage','eq',1,'fraction')],
      [c('phase-demand-calibration','eq',1,'fraction'),c('concession-net-receipts-evidence','eq',1,'fraction')],
      [c('all-six-month-financing-gates-covered','eq',1,'fraction'),c('signed-native-currency-term-coverage','eq',1,'fraction'),c('government-capital-share','eq',.25,'fraction')],
      [c('open-release-hazards','eq',0,'hazard'),c('allocated-full-fleet-acceptance','eq',831,'train'),c('line-infrastructure-acceptance','eq',1,'fraction')],
    ]
    rows=[]
    for i,(entry,checks) in enumerate(zip(register,criteria),1):
        uid='BAG-EVID-%03d'%i
        rows.append(dict(id=uid, erpnext_doctype='Task', erpnext_subject=uid+' — '+entry['assumption'],
                         accountable_owner_role=entry['accountable_role'], accountable_owner_identity=None,
                         owner_assignment_status='named-person-required', required_measurement=entry['required_evidence'],
                         acceptance_rule=entry['acceptance_rule'], criteria=checks, required_reviewer_role='assessor',
                         source_revision=source_revision(sources), sources_sha256=sources,
                         result=None, status='not-demonstrated', operational_release=False,
                         evidence_result_template=uid+'-result-template.json'))
    uid='BAG-EVID-010'
    rows.append(dict(id=uid,erpnext_doctype='Task',erpnext_subject=uid+' — Independently operable first section',
        accountable_owner_role='Section design authority / operator / independent assessor',accountable_owner_identity=None,
        owner_assignment_status='named-person-required',required_measurement='Surveyed turnbacks/platforms; feeder/charger and thermal duty tests; section fleet acceptance; isolated software/wayside configuration; own maintenance/rescue access; OD calibration and signed opening dossier',
        acceptance_rule='All section infrastructure and allocated trains accepted; no unresolved release hazard; operator and statutory authority release remain separate',
        criteria=[c('accepted-section-fleet','eq',section['total_trainsets'],'train'),c('clear-platform-length','ge',121,'m'),
                  c('terminal-berths-per-end','ge',section['terminal_berths_per_end'],'berth'),
                  c('feeder-power-per-end','ge',section['terminal_grid_kw_per_end'],'kW'),
                  c('round-trip-delivered-charge','ge',section['round_trip_energy_kwh'],'kWh'),
                  c('independent-maintenance-rescue-acceptance','eq',1,'fraction'),c('surveyed-section-demand','eq',1,'fraction'),
                  c('accepted-stabling-spaces','ge',section['total_trainsets'],'train-space'),
                  c('open-section-release-hazards','eq',0,'hazard')],required_reviewer_role='assessor',
        source_revision=source_revision(sources),sources_sha256=sources,result=None,status='not-demonstrated',operational_release=False,
        evidence_result_template=uid+'-result-template.json'))
    for row in rows:
        row['acceptance_criteria_sha256']=fingerprint(row['criteria'])
    return rows


def source_revision(sources):
    # A content revision is reproducible before/after git commits; no generation
    # cycle or false claim that uncommitted inputs belong to HEAD.
    return 'sha256:'+fingerprint(sources)


def verify_result(package, result_path, review, policy, root=ROOT):
    """Require measured criteria + raw bytes + source-bound independent signature."""
    result=json.loads(result_path.read_text())
    if result.get('work_package_id')!=package['id'] or result.get('source_revision')!=package['source_revision']:
        raise ValueError('Result belongs to a different package or source revision')
    if package.get('acceptance_criteria_sha256')!=fingerprint(package['criteria']) or result.get('acceptance_criteria_sha256')!=package['acceptance_criteria_sha256']:
        raise ValueError('Changed or unbound acceptance criteria')
    if result.get('status')!='passed' or not result.get('executed_by') or not result.get('accountable_owner_identity') or not result.get('acquired_at'):
        raise ValueError('Incomplete or unexecuted measurement result')
    acquired=datetime.fromisoformat(result['acquired_at'])
    if acquired.tzinfo is None or acquired > datetime.now(timezone.utc):
        raise ValueError('Acquisition time must include a timezone and not be in the future')
    for rel,digest in package['sources_sha256'].items():
        path=(root/rel).resolve()
        if not path.is_relative_to(root.resolve()) or sha(path)!=digest:
            raise ValueError('Stale work-package inputs')
    raw=result.get('raw_evidence_sha256',{})
    if not raw:
        raise ValueError('Raw measurement/quotation files required')
    for rel,digest in raw.items():
        path=(root/rel).resolve()
        if not path.is_relative_to(root.resolve()) or not path.is_file() or sha(path)!=digest:
            raise ValueError('Missing or changed raw evidence')
    values=result.get('measurements',{})
    if set(values)!={c['id'] for c in package['criteria']}:
        raise ValueError('Missing or unexpected acceptance measurement')
    for c in package['criteria']:
        m=values[c['id']];value=m.get('value')
        if m.get('unit')!=c['unit'] or isinstance(value,bool) or not isinstance(value,(int,float)) or not math.isfinite(value):
            raise ValueError('Measurement has invalid value or units')
        passed={'le':value<=c['target'],'ge':value>=c['target'],'eq':value==c['target']}[c['operator']]
        if not passed:
            raise ValueError('Acceptance criterion failed: '+c['id'])
    fingerprint_result=sha(result_path)
    accepted,gaps=authenticated_reviews(root,[review],policy,fingerprint_result,package['source_revision'],
                {result['executed_by'],result['accountable_owner_identity']},date.today())
    if not accepted or not any(r.get('role')==package['required_reviewer_role'] for r in accepted):
        raise ValueError('No authorized independent acceptance: '+'; '.join(gaps))
    return dict(work_package_id=package['id'],status='evidence-accepted',authenticated=True,
                signed_result_sha256=fingerprint_result, reviews=accepted, operational_release=False)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check',action='store_true')
    parser.add_argument('--verify-result',type=Path)
    parser.add_argument('--envelope',type=Path)
    parser.add_argument('--signature',type=Path)
    parser.add_argument('--policy',type=Path)
    args=parser.parse_args()
    if args.check:
        report=json.loads((OUT/'summary.json').read_text())
        for rel,digest in report['sources_sha256'].items():
            if sha(ROOT/rel)!=digest:raise ValueError('Stale qualification input: '+rel)
        for rel,digest in report['outputs_sha256'].items():
            if sha(OUT/rel)!=digest:raise ValueError('Changed qualification output: '+rel)
        print('Qualification package source and output hashes pass');return
    if args.verify_result:
        if not all((args.envelope,args.signature,args.policy)):parser.error('Verification requires envelope, signature and trusted policy')
        manifest=json.loads((OUT/'summary.json').read_text())
        if sha(OUT/'evidence-work-packages.json')!=manifest['outputs_sha256']['evidence-work-packages.json']:
            raise ValueError('Changed generated work-package register')
        result=json.loads(args.verify_result.read_text())
        package=next(p for p in json.loads((OUT/'evidence-work-packages.json').read_text())['work_packages'] if p['id']==result['work_package_id'])
        print(json.dumps(verify_result(package,args.verify_result,dict(envelope_path=str(args.envelope.resolve().relative_to(ROOT)),signature_path=str(args.signature.resolve().relative_to(ROOT))),args.policy)));return
    paths=[Path(__file__),Path(__file__).with_name('baghdad_delivery_stress.py'),Path(__file__).with_name('subsystem_qualification.py'),
           Path(__file__).with_name('baghdad_funding_analysis.py'),ROOT/'design/city-generation/src/osr_scenario/iraq_finance.py',
           ROOT/'lib/templates/baghdad-qualification.toml',ROOT/'lib/templates/baghdad-delivery-risk.toml',
           ROOT/'lib/templates/iraq-funding.toml',ROOT/'lib/templates/baghdad-finance-options.toml',
           CITY/'design.toml',CITY/'baghdad.toml',CITY/'operations/baghdad-operations.json.gz',
           CITY/'engineering/factory/summary.json',CITY/'engineering/finance/summary.json',
           CITY.parent/'finance/baghdad-programme.json',CITY/'engineering/delivery-risk/summary.json',
           CITY/'engineering/delivery-risk/qualification-register.csv',
           CITY/'engineering/delivery-risk/calendar_baseline-monthly-finance.csv']
    paths.extend([ROOT/'lib/templates/rolling-stock.toml', ROOT/'deployment/erpnext/apps/osr_erpnext/osr_erpnext/qualification.py',
                  ROOT/'tools/automation/connected_assurance.py'])
    sources={p.relative_to(ROOT).as_posix():sha(p) for p in paths}
    opts=tomllib.loads(paths[5].read_text());risk=tomllib.loads(paths[6].read_text())
    config=city_funding_config(tomllib.loads(paths[7].read_text()),'baghdad');finance_opts=tomllib.loads(paths[8].read_text())
    design=tomllib.loads(paths[9].read_text());scenario=tomllib.loads(paths[10].read_text())
    payload=json.loads(gzip.decompress(paths[11].read_bytes()));factory=json.loads(paths[12].read_text());city_finance=json.loads(paths[13].read_text());programme=json.loads(paths[14].read_text())
    city_finance['_contracts']=payload['project_twin']['budget_contracts']
    context=(config,finance_opts,programme,city_finance,factory,risk)
    OUT.mkdir(parents=True,exist_ok=True)
    facility=temporary_facility(factory,opts['temporary_facility'],risk)
    save('temporary-facility.json',facility);write_csv(OUT/'temporary-facility-rfqs.csv',facility['rfqs'])
    (OUT/'temporary-facility-layout.svg').write_text(facility_layout(facility))
    section,result,delivery=section_study(design,scenario,payload,factory,context,opts['first_section'],risk)
    save('first-section.json',section);write_csv(OUT/'first-section-monthly-finance.csv',result['monthly']);write_csv(OUT/'first-section-six-month-finance.csv',result['semiannual']);write_csv(OUT/'first-section-schedule.csv',delivery['tasks']);write_csv(OUT/'first-section-incremental-costs.csv',result['incremental_costs'])
    write_csv(OUT/'first-section-rfqs.csv',section['rfqs'])
    risk_report=json.loads(paths[15].read_text())
    comparison=[]
    for name in ('calendar_baseline','temporary_first_article','availability_75pct_costed','availability_75pct_all_stage_shifts',
                 'domestic_placement_interrupted_recovered','export_credit_delayed_recovered'):
        case=risk_report['cases'][name];m=case['metrics']
        comparison.append(dict(case=name,first_month=min(p['opening_month'] for p in case['phases']),
            full_month=max(p['opening_month'] for p in case['phases']),total_capital_usd=m['total_capital_usd'],
            unlevered_npv_usd=m['unlevered_project_npv_usd'],peak_gap_iqd=m['peak_supplemental_balance_iqd'],
            debt_clearance_month=m['debt_clearance_month_without_unfunded_support']))
    m=section['metrics']
    comparison.append(dict(case='independent_first_section',first_month=section['conditional_opening_month'],
        full_month=comparison[0]['full_month'],total_capital_usd=m['total_capital_usd'],unlevered_npv_usd=m['unlevered_project_npv_usd'],
        peak_gap_iqd=m['peak_supplemental_balance_iqd'],debt_clearance_month=m['debt_clearance_month_without_unfunded_support']))
    write_csv(OUT/'financial-comparison.csv',comparison)
    baseline=list(csv.DictReader(paths[17].open()))
    gates=[]
    for name,source,start,end,fraction,recovered in (
       ('domestic_half_placement_recovered','domestic_bonds_draw_native',29,34,risk['funding_gates']['domestic_placement_fraction'],True),
       ('domestic_half_placement_permanent','domestic_bonds_draw_native',29,len(baseline)-1,risk['funding_gates']['domestic_placement_fraction'],False),
       ('export_unavailable_recovered','chinese_export_credit_draw_native',0,5,0.,True),
       ('export_denied_permanent','chinese_export_credit_draw_native',0,len(baseline)-1,0.,False)):
        gate,rows=funding_placement(baseline,name,source,start,end,fraction,recovered)
        gates.append(gate);write_csv(OUT/(name+'-placement-monthly.csv'),rows)
        semi=[]
        for startmonth in range(0,len(rows),6):
            rr=rows[startmonth:startmonth+6]
            semi.append(dict(start_month=startmonth,end_month=rr[-1]['month'],
                             **{k:sum(r[k] for r in rr) for k in ('requested_source_native','placed_source_native','refused_source_native','replacement_placement_required_native','deferred_original_invoice_usd')},
                             available_undrawn_capital_for_deferred_invoices_usd=rr[-1]['available_undrawn_capital_for_deferred_invoices_usd']))
        write_csv(OUT/(name+'-placement-six-month.csv'),semi)
    save('funding-gates.json',dict(status='uncommitted-procurement-gate-study',cases=gates,government_capital_share=.25))
    register=list(csv.DictReader(paths[16].open()))
    packages=evidence_packages(register,factory,programme,section,sources)
    save('evidence-work-packages.json',dict(schema='baghdad-evidence-work-packages/1',work_packages=packages,erpnext_imported=None,erpnext_state_basis='Deployment-specific native Task IDs and assignments are recorded in private var/erpnext import receipts'))
    tasks=[]
    for p in packages:
        desc=json.dumps({k:p[k] for k in ('id','accountable_owner_role','owner_assignment_status','required_measurement','acceptance_rule','criteria','source_revision','evidence_result_template')},indent=2)
        tasks.append(dict(subject=p['erpnext_subject'],status='Open',priority='High',description='<pre>'+desc.replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')+'</pre>'))
        save(p['evidence_result_template'],dict(work_package_id=p['id'],source_revision=p['source_revision'],acceptance_criteria_sha256=p['acceptance_criteria_sha256'],status='not-executed',executed_by=None,accountable_owner_identity=None,acquired_at=None,raw_evidence_sha256={},measurements={c['id']:dict(value=None,unit=c['unit']) for c in p['criteria']}))
    save('erpnext-tasks.json',dict(doctype='Task',tasks=tasks,status='draft-import-package-not-live-records'))
    write_csv(OUT/'erpnext-task-import.csv',tasks)
    npv=programme['independent_recalculation']['cases']['fare_5pct_opex_5pct']['pricing_project_npv_usd_equivalent']
    pricing=programme['independent_recalculation']['cases']['fare_5pct_opex_5pct']
    discount=pricing['pricing_nominal_discount_rate']
    phases=programme['phased_opening']['phases']
    annuity=sum(sum(p['weight'] for p in phases if m>=p['opening_month']) * 1.05**(m//12)/12/(1+discount)**(m/12) for m in range(len(baseline)))
    threshold=max(0,-npv)/annuity
    save('feasibility.json',dict(status='conditional-financeability-not-established-bankability',unlevered_financial_npv_usd=npv,
         nominal_discount_rate=discount, additional_real_reference_annual_external_benefit_threshold_usd=threshold,
         external_benefit_pv_factor=annuity,benefit_threshold_basis='Illustrative benefits start with each baseline opening weight, index 5% from close and discount at 13.4%; threshold only, not an economic CBA. Fares/transfers are not economic benefits; wages and loans are not additional benefits.',
         assessed_external_benefits_usd=None,lender_commitments_received=False))
    write_readme(facility,section,gates,threshold,npv,comparison)
    outputs={p.relative_to(OUT).as_posix():sha(p) for p in sorted(OUT.glob('*')) if p.is_file() and p.name!='summary.json'}
    save('summary.json',dict(schema='baghdad-qualification-package/1',source_revision=source_revision(sources),
         sources_sha256=sources,outputs_sha256=outputs,operational_release=False,financing_committed=False,erpnext_imported=None))
    print('Built temporary facility, ten evidence tasks, four funding gates and first-section finance; conditional section opening month',section['conditional_opening_month'])


def write_readme(facility,section,gates,threshold,npv,comparison):
    text=f'''# Baghdad qualification, funding gates and first operating section

This package turns the review findings into executable draft work. It supplies no physical acceptance, supplier quotation, named owner assignment or financing commitment. The full 831-train Baghdad baseline and its month 41/83 openings remain unchanged.

## Temporary first-article industrial package

[Site block layout](temporary-facility-layout.svg), [quantities and reconciliation](temporary-facility.json), and [RFQ schedule](temporary-facility-rfqs.csv) specify six prototype cells, {facility['process_floor_m2']:,.1f} m² process floor, {facility['total_floor_m2']:,.1f} m² total covered floor and {facility['site_m2']:,.1f} m² fenced-site allowance. The metric 180 x 93 m envelope is a reference arrangement, not a selected or surveyed site. Access/fire widths, hazardous materials, drainage, foundations, heavy-haul route, crane coverage and utilities require detailed vendor/civil drawings. No production acceptance paths are counted at this temporary site.

The quantity-based direct subtotal is USD {facility['priced_subtotal_usd']/1e6:.3f}m; contingency USD {facility['contingency_usd']/1e6:.3f}m; allocated total USD {facility['allocated_direct_usd']/1e6:.3f}m. USD {facility['unallocated_allowance_usd']/1e6:.3f}m remains unallocated within the existing USD 35m allowance. EPC remains USD 2.45m. **Nothing in this package is added a second time to the USD 37.45m recovery case.** Rates are editable assumptions, not received quotations or realised savings.

Vendor interfaces: bogie/body datum and lifting reactions; composite mould temperature/cure traceability and ventilation; door/window fit and tolerance stack; battery transport SOC/fire segregation and HV isolation; electrical test connectors and calibrated instruments; ERP lot/serial traveller and revision interfaces. RFQ returns must identify imported tooling versus Iraqi buildings/labour, actual origin, tax, delivery slots and financed invoice eligibility; the recovery model's 20% tooling/import fraction remains unqualified until these are reconciled.

Transfer sequence: permanently identify TFA-C01 through C06 tooling in the asset register; release the prototype traveller and first-article configuration; move the complete six-car train on certified frames/haulage with clearance and escort approval to permanent acceptance at day 390; retain all temporary tools until prototype acceptance and production continuity are secured; lock out, pack, transfer, reinstall and recalibrate each cell into its named permanent work centre; validate first-off dimensions/HV tests before release. Permanent plant tooling is already fully budgeted: temporary equipment is incremental and any reuse credit needs an approved asset/cost change, never an automatic reduction.

Readiness gates: survey/land and supplier interfaces before procurement; civil/fire/utility/lifting acceptance and calibrated equipment before day-260 assembly; permanent segregated test paths and bays before day-390 dynamic tests; the **additional 60 working-day first-article qualification** remains fixed; no series release before signed acceptance. Day 260/390 and month-36 first service are conditional dates, with independent ERP evidence tasks below.

## Executable evidence work and ERPNext

[Ten source-bound work packages](evidence-work-packages.json) map every delivery qualification row to an accountable role, measurement fields, units, numeric criteria, source content revision, ERPNext Task subject and result template. A named accountable person is deliberately pending rather than fabricated. [Task import JSON](erpnext-tasks.json) and [CSV](erpnext-task-import.csv) are drafts; they are not live ERP records or accepted evidence. Reconcile them with the ERP app's `qualification.import_tasks` method; preview is the default. Assign actual users/owners through ERP and preserve assignment when refreshing descriptions.

Populate each BAG-EVID result template using real measurements and raw evidence file checksums. Use `.venv/bin/python tools/automation/baghdad_qualification.py --verify-result RESULT --envelope ENVELOPE --signature SIGNATURE --policy TRUSTED_POLICY`. The verifier rejects null/wrong-unit/out-of-threshold measurements, missing raw files, source changes, absent or unauthorized review and self-review. It reuses the subsystem qualification's externally controlled Ed25519 reviewer policy and envelope (`osr-subsystem-review/1`), with evidence fingerprint = SHA256 of the exact result bytes, configuration fingerprint = package source revision, required role = assessor, acceptance reference and expiry. Trusted reviewer identities/keys must be supplied independently; the generator provides no signing key and no acceptance. An accepted evidence package still does not authorize public operation.

Coverage ratios require item/lot/phase-level underlying files and independent scope review, not an unsupported declaration of 1. Production records must separate elapsed cure clocks and inspection holds from staffed hours. Baseline throughput and the shifted recoveries remain unmeasured. Funding evidence needs the appropriation, actual native-currency term sheets, investor/underwriter placement mandates, collateral/guarantees, maturity/fees, and every six-month sources-and-uses gate, including reserves and interest. Demand work must include a surveyed OD matrix, affordable fare/elasticity tests and **net** kiosk/advertising concessions after vacancy, collection and management costs.

## Denied and interrupted funding

[Funding gate cases](funding-gates.json) and each placement-monthly/six-month CSV distinguish requested source face, available fraction, refused amount, invoices held and undrawn capital capacity reserved for deferred invoices. Recovered domestic placement assumes half the ordinary IQD bond placement fails for months 29–34; all unfinished procurement, civil work, production and running tests pause at working day 600 for 130 working days. Recovered export credit pauses the programme at NTP for 130 working days and requires the refused initial USD credit to be placed before imported procurement restarts. The costed schedules and financing are in the delivery-risk cases `domestic_placement_interrupted_recovered` and `export_credit_delayed_recovered`. A USD 10m equivalent **IQD local remobilisation** assumption plus 7% EPC is added once, with staff/site carrying costs charged in the six suspension months for the already-mobilised domestic case. An export refusal at proposed NTP shifts the entire unstarted programme without buying another construction/production staffed span; only the quoted-later remobilisation/reservation allowance is added. Cure/inspection restart requirements could cost more and need vendor evidence. Longer delay, storage damage, cancellation penalties, FX changes and lender acceleration/default are outside these recovery prices.

The placement files diagnose the **original** invoice request. Recovered cashflow files retime actual invoice milestones using the held schedule; they must not be added together. The available-capital column is an undrawn capacity requirement, not received or free operating cash. Recovered cases retain uncommitted liquidity for interest and hold costs; it never replaces the refused core capital. Investor commitment/carry fees on undrawn domestic placement are unquoted and excluded. Partial grants/green placements already in the baseline remain assumed; refusing ordinary bonds does not prove green placements will succeed. Bank refusal can be run with the same gate mechanism. Recovered dates and repayment require renewed placement and restart appropriations, which remain uncommitted. **Permanent domestic/export refusal has no operating opening or debt-clearance date.** Existing debt is not forgiven; cancellation, default/workout, liquidation proceeds and prior-creditor claims require a separate resolution model and are not represented by zero balances. Government is not automatically increased beyond 25%; the original import split stays 50% government USD / 50% Chinese USD loan; only actual import invoices can qualify. Domestic cash, bonds, bank/green/gap credit remain IQD, while foreign donor receipts would have separately identified FX conversion requirements.

| Gate | Currency | Refused amount | Recovery assumed |
|---|---|---:|---|
'''
    for g in gates:
        text+=f"| {g['case']} | {g['currency']} | {g['refused_native']:,.2f} | {g['later_placement_assumed']} |\n"
    text+=f'''
## Separate independently operable first-section option

[First-section duty, assets and finance](first-section.json) takes the actual first five line-1 stations, from the Mahmudiya terminal to {section['station_ids'][-1]}, spanning **{section['route_km']:.3f} km**. This outer corridor is a demonstrator candidate, not a proven best catchment. It needs its own OD/accessibility study and comparison against better central corridors. Existing station/track/wayside tasks alone are pulled forward within the frozen lane/predecessor graph; their already-budgeted capital is retimed, not purchased again. Other route quantities and the 831-city fleet remain unchanged.

At the reference six-minute headway and 40 km/h average running speed, the round trip is {section['round_trip_minutes']:.2f} minutes including intermediate dwells and ten-minute charging/turnaround at each end. It requires **{section['peak_trains']} peak + {section['spare_trains']} spare + 1 cold reserve = {section['total_trainsets']} existing six-car trains**. Allocated train IDs are in the data file and must all pass acceptance before section operation. A six-minute section service is an explicit early-phase option rather than the ultimate line's three-minute design demand.

Each end needs {section['terminal_berths_per_end']} independent 121 m clear berths for the 111 m train, No.9 crossover/points, a safeguarded 185 m terminal arrangement, {section['terminal_berths_per_end']} x {section['charger_kw_per_berth']:,.0f} kW chargers and {section['terminal_grid_kw_per_end']:,.0f} kW feeder capacity. Dwell plus clearance occupies each berth for 11 minutes against a 12-minute two-berth arrival cycle. These are geometry/utility requirements pending surveyed access, swept path, braking, interlocking and electrical studies; a generic standard station cannot silently serve as the new terminal.

Round-trip traction plus the conservative auxiliary proxy is {section['round_trip_energy_kwh']:.1f} kWh, compared with {section['round_trip_charge_delivered_kwh']:.1f} kWh delivered terminal charge at 90% efficiency. Battery definitions are **{section['nameplate_battery_kwh']:,.0f} kWh nameplate / {section['usable_battery_kwh']:,.0f} kWh usable** from the controlled six-car profile. The conservative section-specific 40% floor is applied to usable energy, leaving {section['usable_soc_window_kwh']:,.0f} kWh; one-leg duty fits that window. Normal charging margin is only **{section['round_trip_charging_margin_fraction']:.2%}**. A 10% reduction in delivered charging gives **{section['degraded_charge_margin_fraction']:.2%}** balance and is not qualified. Roof PV and intermediate charging are excluded. The battery acceptance power, HVAC electrical demand, gradients, ambient heat, degraded charging and rescue case require measured qualification; the small energy margin is not operational robustness.

The [section RFQs](first-section-rfqs.csv) provide four incremental packages excluding already-budgeted route, station and fleet equipment. Reuse one original charger per end and add two berth chargers in total, upgrading each end to 4 MW. Independent maintenance/stabling, battery quarantine, lifting, rescue and road access avoid reliance on the distant line-6 depot. The provisional 3.5 ha maintenance site has eight stabling roads of 250 m usable length (two 111 m trains per road plus 28 m clearance) and two 135 x 6.5 m maintenance bays; site rights, turnout ladders, fire/access geometry and measured depot duty remain open. Turnback/platform adaptation USD 5m, charging/grid USD 8m, maintenance/access USD 12m and controls/acceptance USD 3m give **USD {section['extra_capital_with_epc_usd']/1e6:.2f}m including EPC**, assuming 20% imported direct scope pending RFQs. The section has its own reference {section['operating_fte']} operating FTE and USD {sum(section['reference_annual_opex_usd'].values())/1e6:.3f}m/year OPEX before indexation, replacing the whole-network fixed OPEX before month 41. It covers 16 hours/day over 330 days/year, USD 0.10/kWh grid electricity with no PV generation credit, Iraqi wage proxies, proportional existing civil/solar/signalling maintenance and train maintenance including the existing battery reserve, plus 2% maintenance on additional support assets. These cost/demand/utility assumptions need quotations and surveys. Separately, sixty temporary construction/qualification support FTE are indexed and charged from support readiness until the full line opens, then integrated into the baseline allowance; they are not counted as section operating staff. Civil/support acceptance at day 560 is an additional unqualified support-package assumption, not an existing accepted site.

The first {section['total_trainsets']} accepted trains finish at day {section['fleet_completion_day']}; selected civil at day {section['civil_completion_day']}; independent support at day {section['independent_support_ready_day']}. The resulting **conditional section opening is month {section['conditional_opening_month']}**, including the same three-month commissioning allowance; complete line opening stays month {section['full_line_opening_month']}. No passengers or fares occur before that opening. Section paid demand is only half the smaller of fleet-capacity and route-length allocation proxies, weight {section['revenue_weight']:.6f}, deducted from later full-line demand to avoid double counting. This is a scenario, not population coverage evidence. Opening acceptance must cover section-specific turnbacks/chargers/depot, full allocated section fleet, isolation from works, evacuation/rescue, software configuration, hazards and independently signed operator/authority release; the full-line BAG-EVID-009 remains separate.

[Monthly finance](first-section-monthly-finance.csv), [six-month tranches](first-section-six-month-finance.csv) and [incremental cost ledger](first-section-incremental-costs.csv) include early baseline invoice timing, new support capital, indexed support payroll, fares/nonfare ramp, fixed/variable OPEX, reserves, native debt and prepayments. Peak gap debt is IQD {section['metrics']['peak_supplemental_balance_iqd']/1e12:.3f}tn; clearance month {section['metrics']['debt_clearance_month_without_unfunded_support']}. Its unlevered NPV is USD {section['metrics']['unlevered_project_npv_usd']/1e9:.3f}bn. Compare against the baseline IQD 4.461tn peak / month 303 clearance / USD -3.299bn NPV. At the conservative demand proxy, mature section receipts are only USD {section['reference_mature_annual_revenue_usd']/1e6:.3f}m/year versus its USD {sum(section['reference_annual_opex_usd'].values())/1e6:.3f}m OPEX before indexing/ramp: it is not independently self-financing. Earlier service requires an explicit operating bridge; the extra facilities and advanced invoices must be justified by measured access benefits, demand or lower costs.

## Financial feasibility and funding evidence

The baseline remains conditionally financeable under uncommitted cheap IQD gap credit and green/rights/receipt assumptions. Its unlevered financial NPV is **USD {npv/1e9:.3f}bn** at 13.4% nominal (8% real plus 5% inflation), before additional grant/rights/receipt targets. Clearing debt through later nominal fare growth is not the same as positive discounted investment value. [Feasibility data](feasibility.json) supplies an illustrative annual external-benefit threshold of USD {threshold/1e6:.1f}m in reference prices, phased with baseline openings and indexed 5%, whose discounted value would offset that financial deficit. This is **not** a completed economic appraisal: economic CBA must remove fares/taxes/financing transfers, use shadow resource costs, count time/safety/emissions benefits without double counting, and assess displacement/opportunity cost of labour rather than call every wage a net benefit.

Additional funding routes to investigate are competitively leased station land/development rights, employer travel contracts, advertising/kiosk concessions, utility/telecom corridor leases, climate grant/guarantee applications, and Iraqi institutional or retail IQD placements. Their net contract proceeds, authority, collection costs, timing and senior-creditor covenants are required before cash enters the ledger; a loan/guarantee is financing, not new operating revenue. The existing USD 300m net rights and USD 25m/year additional net receipts are targets, not a valuation or signed concession, and must not be added again as these same mechanisms. Replicable land value capture depends on land rights, planning powers and market demand ([World Bank financing guidance](https://www.worldbank.org/en/topic/urbandevelopment/publication/financing-transit-oriented-development-with-land-values)). Iraq's [GCF country programme](https://www.greenclimate.fund/document/iraq-country-programme) establishes a project-development framework, not a Baghdad rail award or a 2% IQD facility. No fund application, lender term sheet or placement was obtained in this work.

## Compare liquidity, repayment and discounted value separately

[Financial comparison data](financial-comparison.csv) uses each case's actual capital and indexed operating ledger, excluding debt and new grant/rights/receipt targets from unlevered NPV. All dates require physical acceptance and financing availability.

| Case | First/full month | Capital USD bn | NPV USD bn | Peak IQD gap tn | Debt cleared month |
|---|---:|---:|---:|---:|---:|
'''
    for r in comparison:
        text+=f"| {r['case']} | {r['first_month']}/{r['full_month']} | {r['total_capital_usd']/1e9:.3f} | {r['unlevered_npv_usd']/1e9:.3f} | {r['peak_gap_iqd']/1e12:.3f} | {r['debt_clearance_month']} |\n"
    text+='''
Temporary first-article production opens the complete first line earlier and lowers peak gap/repayment time, yet worsens discounted reference investment value after its additional capital/early operating costs. The independent shorter section also adds capital and runs a conservative standalone operating deficit. Neither is adopted merely because fares arrive sooner. Coordinated shifts should be compared with the matching 75% availability case, not assumed to save money against the stronger baseline. Funding-delay NPV can look less negative because nominal un-escalated purchases are deferred; this discounting effect is not a benefit of denied credit. Real delay appraisal needs contract escalation, FX, cancellation/default costs and lost passenger benefits. Existing escalation/downside scenarios demonstrate their materiality.

Rebuild after delivery stresses with `.venv/bin/python tools/automation/baghdad_qualification.py`; validate with `--check`. Physical evidence and finance gates remain open.
'''
    (OUT/'README.md').write_text(text)


if __name__=='__main__':main()
