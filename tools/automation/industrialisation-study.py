#!/usr/bin/env python3
"""Compile the linked vehicle/bogie/viaduct programme and possible vendor register."""
import argparse
import csv
import hashlib
import io
import json
from pathlib import Path
import sys
import tomllib

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'design/component-catalogue/src'))
from osr_mech.industrialisation import (vehicle_support_graph,moving_axle_screen,production_balance,
    support_packet_check,installed_cost_comparison,disruption_metrics,service_finance_gate,elevation_reference)
from osr_mech.rolling_stock.bogie.assembly import WHEELBASE_MM
from osr_mech.provenance import stable_sum as sum

SOURCE=ROOT/'design/industrialisation/programme.json'
VENDORS=SOURCE.with_name('vendor-candidates.json')
OUT=ROOT/'engineering/industrialisation'
CITY=ROOT/'cities/catalogue/west-asia/Iraq/Baghdad'


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def read(path):return json.loads(path.read_text())
def encoded(value):return (json.dumps(value,indent=2,sort_keys=True,ensure_ascii=False)+'\n').encode()


def build():
    config=read(SOURCE);vendors=read(VENDORS)
    if config['schema']!='osr-industrialisation-programme/1':raise ValueError('unknown programme schema')
    ids=[v['id'] for v in vendors['vendors']]
    if len(set(ids))!=len(ids):raise ValueError('vendor candidate IDs must be distinct')
    for vendor in vendors['vendors']:
        if not vendor['official_source_url'].startswith('https://') or vendor['status']!='potential-vendor-screening-only':
            raise ValueError('supplier listing requires a primary source and screening boundary')
        if any(vendor[k] for k in ('osr_compatibility_accepted','manufacturing_rights_confirmed','regional_supply_confirmed','contacted')):
            raise ValueError('public-source candidates cannot grant a commitment or acceptance')
    mass=read(ROOT/config['links']['mass_budget'])
    profiles=tomllib.loads((ROOT/'lib/templates/rolling-stock.toml').read_text())['profiles']
    vehicle=config['reference_vehicle'];profile=profiles[vehicle['family']]
    if vehicle['cars']!=profile['cars'] or mass['controlled_planning_tare_kg']!=profile['tare_mass_t']*1000:
        raise ValueError('industrialisation reference differs from controlled vehicle profile')
    selected=config['selected_configuration']
    if selected['accepted']:raise ValueError('supplier selection/freeze requires an external controlled acceptance workflow')
    count=profile['cars'];length=profile['length_m'];body_length=length/count
    reference_bogies=count*vehicle['bogies_per_car'];wheelbase=WHEELBASE_MM/1000
    bogie_mass=mass['modeled_categories_kg']['bogie frames, wheelsets, brakes, and suspension']/reference_bogies
    body_mass=(mass['controlled_planning_tare_kg']-bogie_mass*reference_bogies)/count
    bogies=[];bodies=[]
    for i in range(count):
        centre=(i+.5)*body_length;supports=[]
        for j,sign in enumerate((-1,1)):
            key=f'reference-car-{i+1}-bogie-{j+1}';supports.append(key)
            bogies.append(dict(id=key,x_m=centre+sign*(body_length/2-wheelbase),mass_kg=bogie_mass,
                axles=2,axle_offsets_m=[-wheelbase/2,wheelbase/2],powered=j==0))
        bodies.append(dict(id=f'reference-car-{i+1}',cg_x_m=centre,support_bogies=supports,
            supported_mass_kg=body_mass+profile['passenger_capacity']/count*vehicle['payload_kg_per_passenger']))
    baseline=vehicle_support_graph(bodies,bogies)
    baseline.update(loading='AW2 planning reference, equal mass and passengers per car',
        mass_source=config['links']['mass_budget'],source_release_status=mass['release_status'],
        bogie_allowance_is_average_unclosed_mass=True,remaining_mass_lumped_at_each_body_midpoint=True,
        baseline_unchanged=True,selected_supplier_configuration=False)
    # A shared-bogie arrangement is an explicit alternative graph, never a
    # consequence of buying an articulation. Redesign masses stay unknown.
    shared_bogies=[dict(id=f'shared-support-{i}',x_m=i*body_length,mass_kg=None,axles=2,
        axle_offsets_m=[-wheelbase/2,wheelbase/2]) for i in range(count+1)]
    shared_bodies=[dict(id=f'shared-body-{i+1}',cg_x_m=(i+.5)*body_length,supported_mass_kg=None,
        support_bogies=[shared_bogies[i]['id'],shared_bogies[i+1]['id']]) for i in range(count)]
    alternative=vehicle_support_graph(shared_bodies,shared_bogies)
    alternative.update(status='load-path-alternative-not-selected',carbody_and_joint_redesign_required=True,
        mass_saving_kg=None,energy_saving_kwh=None,cost_saving_usd=None)
    civil=[moving_axle_screen(baseline['axle_pattern'],span) for span in config['viaduct']['ordinary_spans_m']]
    connected=read(CITY/'engineering/connected-build/manifest.json')
    schedule=read(CITY/'engineering/connected-build/civil.json')
    design=tomllib.loads((CITY/'design.toml').read_text())
    retained_case=read(CITY/'engineering/programme-recalculation/local_positive.json')
    energy_control=read(CITY/'engineering/connected-build/energy-control.json')
    outputs={}
    outputs['vehicle-civil-load-trace.json']=encoded(dict(schema=1,reference=baseline,shared_bogie_alternative=alternative,
        selected_configuration=selected,civil_static_demand=civil,viaduct_configuration=config['viaduct'],
        quantities_source='../../cities/catalogue/west-asia/Iraq/Baghdad/engineering/connected-build/span-layout.json',
        span_layout_sha256=sha(CITY/'engineering/connected-build/span-layout.json'),
        moving_vehicle_and_launcher_loads_are_separate=True,adopted_civil_loading=False,
        frozen_vehicle_mass_kg=None,articulation_and_bogie_selected_independently=False))
    rows=[production_balance(config['supply_chain'],rate,independent_fronts=18)
        for rate in config['supply_chain']['illustrative_bays_launcher_working_day']]
    outputs['production-balance.json']=encoded(dict(rows=rows,unit='accepted double-track bay',
        ordinary_span_mix_source='span-layout.json',all_25m_is_illustrative=True,
        evidence_backed_capacity_adopted=False,mobilisation_requires=['sufficient continuous released run',
            'qualified accepted supply','executable delivery and access plan','assessed authorised crew','inspected compatible equipment'],
        measured_cycles=config['measured_cycles'],foundation_depth_and_capacity_site_specific=True,
        construction_chain=['survey-utilities','foundations','columns-caps','accepted-serialized-beams-and-transport',
            'erection-bearings-temporary-works','connections-walkways-drainage-track','structure-systems-handover']))
    cost_cases=[dict(id=case,scope_costs_usd=config['installed_costs_usd'].get(case,{})) for case in
        ('complete-bogie-import','repeat-local-assembly','local-frame-manufacture','precast-column-and-cap','in-situ-column-precast-cap')]
    finance=service_finance_gate(config['accepted_services'])
    finance.update(installed_cost_comparisons=installed_cost_comparison(config['procurement_scopes'],cost_cases),
        retained_baghdad_comparator=config['links']['finance'],retained_programme_sha256=sha(ROOT/config['links']['finance']),
        connected_construction_source_revision=connected['source_revision'],
        conditional_running_bay_milestones_source='../../cities/catalogue/west-asia/Iraq/Baghdad/engineering/connected-build/civil.json',
        elevation_comparison_rule='Compare complete priced foundation, station, special, grid, vehicle and installed scopes with accepted service/paid journeys, funding and measured disruption; no additional-elevation net benefit is adopted.',
        actual_received_finance_cases=len(config['accepted_services']))
    outputs['installed-cost-and-service-finance.json']=encoded(finance)
    retained_openings={row['line']:row for row in retained_case['opening_phases']}
    fleets={row['line']:row['trainset_count'] for row in design['fleets']}
    delivery_rows=[]
    for case_name,case in schedule['conditional_scenarios'].items():
        for row in case['opening_stages']:
            original=retained_openings[row['line']]
            delivery_rows.append(dict(case=case_name,line=row['line'],
                conditional_running_span_date=row['conditional_opening_date'],
                retained_financial_opening_month=original['opening_month'],
                retained_fleet_completion_day=original['fleet_completion_day'],
                required_controlled_trainsets=fleets[row['line']],
                selected_supplier_vehicle_delivery_date=None,station_special_structure_system_handover_date=None,
                actual_opening_date=None,qualified_delivered_service_fraction=None,finance_receipt_adjustment_iqd=None))
    outputs['baghdad-delivery-finance-bridge.json']=encoded(dict(rows=delivery_rows,
        retained_monthly_cashflow_source='../../cities/catalogue/west-asia/Iraq/Baghdad/engineering/programme-recalculation/local_positive.json',
        reference_energy_service_diagnostics={name:{key:case[key] for key in ('dispatch_opportunities','dispatched_journeys','completed_journeys','distinct_energy_held_journeys')}
            for name,case in energy_control['cases'].items()},
        operating_qualification=False,common_financial_close_date=None,
        date_to_finance_month_conversion_accepted=False,receipts_scale_automatically_with_dispatches=False,
        uptake_rule='Use the maximum of accepted civil/station/system handovers and commissioned vehicle delivery, then qualify delivered service and unique paid journeys before changing the monthly finance ledger.',
        service_finance_gate=finance['line_months'],baseline_monthly_finance_replaced=False))
    rates=tomllib.loads((ROOT/'lib/templates/civil-cost-model.toml').read_text())['civil_usd_per_km']
    available_at_grade=sum(s['to_station_m']-s['from_station_m'] for s in design['civil_segments'] if s['class']=='at-grade')
    outputs['further-elevation-comparison.json']=encoded(dict(
        basis='0/25/50/100% of current at-grade length as unaccepted scope sensitivities, not selected alignments or purchased quantities',
        controlled_at_grade_m=available_at_grade,
        cases=[elevation_reference(available_at_grade*fraction,rates['at_grade'],rates['elevated']) for fraction in (0.,.25,.5,1.)],
        adopted_additional_elevation_m=None,complete_economic_case_accepted=False))
    packets=[support_packet_check(p,config['revision']) for p in config['support_packets']]
    outputs['support-release-and-urban-access.json']=encoded(dict(packets=packets,
        required_support_packet=['survey_position','utility_clearance','ground_basis','foundation_design','access_plan',
            'traffic_arrangement','inspection_plan','connection_and_release_strength','launcher_stage_loading'],
        foundation_families=config['viaduct']['foundation_families'],pier_alternatives=config['viaduct']['pier_alternatives'],
        disruption=disruption_metrics(config['closure_events'],config.get('accepted_completed_bay_ids',[])),
        controls=['compact segregated worksite','maintained pedestrian shop emergency access','appointment-based spoil and concrete movements',
            'booked off-peak lifting exclusions','staging away from roadside','prompt pavement reinstatement',
            'dust noise vibration settlement monitoring','separate station and junction access plans'],
        installed_is_not_launcher_ready=True,site_traffic_and_structural_acceptance=False))
    tasks=[]
    for wp in config['work_packages']:
        if not wp['owner_role'] or not wp['evidence_required']:raise ValueError('work package requires owner role and exit evidence')
        tasks.append(dict(id=wp['id'],title=wp['title'],product=wp['product'],target_window_days=wp['target_window_days'],
            responsible_role=wp['owner_role'],appointed_person=None,accepted=False,
            existing_package_refs=wp['related_existing_packages'],required_outputs=wp['evidence_required'],
            native_records=['Department','Project','Task','Employee','Training Program','Shift Type','Shift Assignment','Asset','OSR Construction Release'],
            training_attendance_grants_equipment_authority=False,allocation_review_submitted=False))
    outputs['work-packages-and-erp-handoffs.json']=encoded(dict(tasks=tasks,stages=config['stages'],front_roles=config['front_roles'],
        responsibility_chain=['Department','production-unit/front','crew','shift','worker','task','accepted-component'],
        recruitment_backplan=['mobilisation','equipment-specific assessment','supervised practice','training','funded recruitment'],
        recruitment_dates=None,relief_and_inspection_independence_required=True,future_reservations_require_live_conflict_checks=True,
        legal_companies_and_live_authentication_configured=False))
    outputs['vendor-candidates.json']=encoded(vendors)
    stream=io.StringIO();writer=csv.writer(stream);writer.writerow(['vendor_id','name','corporate_group','category','family','source','status','price_usd','rights_confirmed','regional_supply_confirmed'])
    for v in vendors['vendors']:writer.writerow([v['id'],v['display_name'],v['corporate_group'],v['category'],v['product_family'],v['official_source_url'],v['status'],'','false','false'])
    outputs['vendor-candidates.csv']=stream.getvalue().encode()
    supplier_lines='\n'.join(f"| {v['display_name']} | {v['category']} | [{v['product_family']}]({v['official_source_url']}) |" for v in vendors['vendors'])
    outputs['README.md']=f'''# Coordinated industrialisation programme

**Status: proposed programme; products, rights, commercial terms and physical acceptance remain open.** Vehicle platform, bogie localisation and the viaduct system share one configuration and evidence chain. HÜBNER and CRRC are proposed discussion partners; no exact product or manufacturing-transfer agreement is selected. [Controlled programme](../../design/industrialisation/programme.json).

## Vehicle configuration and civil demand

[Vehicle-to-civil trace](vehicle-civil-load-trace.json) preserves the current three-car, six-bogie/twelve-axle reference. Its 78,750 kg tare is an unclosed planning control. Equal car loading, midpoint CG and equal bogie axle sharing are explicitly assumed. Bogie locations follow the existing CAD rule. The shared-bogie alternative has an explicit four-support graph with unknown redesign masses. Buying an articulation creates no bogie-count, mass, energy or cost reduction. Exact joint/bogie selection, low-floor clearances, yaw/pitch/roll, stiffness/damping, fatigue/crash and maintenance/recovery require a joint interface freeze.

The same axle pattern feeds sampled static Pi20/Pi25 live-load demand. Dynamic augmentation, permanent capacity, prestress, bearings and launcher loads need independent design. [Identified Baghdad spans](../../cities/catalogue/west-asia/Iraq/Baghdad/engineering/connected-build/span-layout.json) remain the quantity authority. No vehicle/civil loading baseline is overwritten.

## Bogie localisation and first articles

First article → repeat assembly with qualified bought-in subcomponents → released frame cutting/forming/welding/machining/NDT/coating → further component localisation where economics justify qualification. Initially buy precision articulation assemblies and make approved surrounding adapters locally. Assess existing Iraqi fabrication and machining processes. Prioritise fixtures, metrology, weld quality, inspection and test equipment. Transfer rights, fees, tooling, qualification, imported components, labour, rejects, warranty and repeat prices have separate scopes.

## Civil catalogue and urban delivery

Two single-track full-span beams share a pier: 25 m primary, 20 m secondary, and separately engineered exceptional crossings. Standardise column/cap connections, bearing/jacking/lifting seats, direct-fixation datums, removable walkway/service cassettes and island-station transitions. Ground zones, depth, capacity, utility clearances and working platforms remain site-specific.

[Support packets and urban controls](support-release-and-urban-access.json) keep foundation mobilisation and launcher support acceptance distinct. Compare precast columns/caps with reusable-form in-situ columns/precast caps by measured accepted supports/week and complete installed cost. Require inspectable connections, temporary stability, grout and verified release strength. Maintain shop/pedestrian/emergency access, appointment-based deliveries/spoil, booked lifting exclusions and prompt reinstatement. Lane-hours, access interruptions and occupation days are unioned by resource and bound to accepted completed bays; absent observations stay unknown.

## Production chain and 18-launcher scenario

[Production balance](production-balance.json) treats one accepted double-track bay as the planning unit. Eighteen active independent fronts at 1/1.5/2 bays per working day give 18/27/36 bays, 36/54/72 beams and 450/675/900 m under the illustrative all-25 m assumption. Actual 20/25 m mixes and special spans retain identified quantities. At 54 beams/day, 48-hour occupation needs 108 casting positions before availability/reject allowances; a long-line bed can hold several positions. A five-working-day buffer needs 270 beams. None is a production commitment.

Released foundations → accepted piers → accepted serialized beams → transport → erection → completed-bay acceptance limit output together. Casting alone cannot release a bay. Mobilise only against a sufficiently long released run, qualified supply, access, authorised crew and compatible inspected machinery. Coordinate existing Iraqi precast facilities and expertise; allocate qualified products/slots and add only demonstrated necessary tooling/capacity.

## Work, training, programme gates and finance

[Linked work packages and ERP handoffs](work-packages-and-erp-handoffs.json) connect the existing supplier, civil and execution structures. The first 30 and 30–90 day windows are proposed planning targets, followed by accepted pilot trials, controlled ramp-up and up-to-18-machine deployment. Responsible roles are named; appointments, funded recruitment and dated rosters remain open. Training attendance is separate from assessed equipment-specific work authority. Future reviewed reservations must undergo the same live machinery/worker exclusivity checks.

[Installed costs and delivered-service finance](installed-cost-and-service-finance.json) separates priced scopes and missing amounts. The [Baghdad delivery/finance bridge](baghdad-delivery-finance-bridge.json) joins each line's conditional running-span date, retained finance opening month/fleet deadline, controlled required fleet and energy/service diagnostics. A common financial-close anchor, supplier vehicle deliveries and accepted station/special/system handovers are still missing. Dispatch completion does not automatically scale paid journeys. Running-bay completion is not railway revenue opening. Unique paid journeys/collection and operating acceptance are required before revised receipts can be considered. Transfers do not multiply paid journeys. [Further elevation comparisons](further-elevation-comparison.json) expose marginal civil reference allowances for explicit scope sensitivities, with complete installed costs, disruption values, financing and net benefit unknown. No additional alignment, beam order, price or accelerated saving is adopted.

## Possible component and equipment vendors

{vendors['method']} Related group brands are not independent offers. Product-family listings establish neither OSR fit nor regional availability, rights, prices, capacity or acceptance. Gangways are not automatically structural joints; segmental gantries are not whole-beam launchers. [Machine-readable candidates](vendor-candidates.json) · [RFQ comparison CSV](vendor-candidates.csv).

| Possible vendor | Scope | Official product/reference source |
|---|---|---|
{supplier_lines}

## Regeneration

Run `.venv/bin/python tools/automation/industrialisation-study.py`; add `--check` for source/output drift. [Manifest](manifest.json) records exact inputs and output bytes. Missing supplier or engineering evidence never becomes acceptance.
'''.encode()
    sources=[SOURCE,VENDORS,Path(__file__),ROOT/'design/component-catalogue/src/osr_mech/industrialisation.py',
        ROOT/'design/component-catalogue/src/osr_mech/rolling_stock/bogie/assembly.py',ROOT/'design/component-catalogue/src/osr_mech/rolling_stock/trainset.py',
        ROOT/'lib/templates/rolling-stock.toml',*(ROOT/path for path in config['links'].values()),
        CITY/'engineering/connected-build/span-layout.json',CITY/'engineering/connected-build/civil.json']
    sources += [CITY/'design.toml',CITY/'engineering/connected-build/energy-control.json',
        CITY/'engineering/programme-recalculation/local_positive.json',ROOT/'lib/templates/civil-cost-model.toml']
    outputs['manifest.json']=encoded(dict(schema=1,status='source-bound-industrialisation-study-not-acceptance',
        sources_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in sources},
        outputs_sha256={name:hashlib.sha256(data).hexdigest() for name,data in outputs.items()},
        vendor_count=len(vendors['vendors']),independent_corporate_groups=len({v['corporate_group'] for v in vendors['vendors']}),
        engineering_release=False,commercial_commitments=False))
    return outputs


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--check',action='store_true');a=p.parse_args()
    outputs=build();OUT.mkdir(parents=True,exist_ok=True)
    for name,data in outputs.items():
        path=OUT/name
        if a.check:
            if not path.is_file() or path.read_bytes()!=data:raise ValueError('stale industrialisation output: '+name)
        else:path.write_bytes(data)
    print('Industrialisation programme current: vehicle/bogie/viaduct trace, '+str(len(read(VENDORS)['vendors']))+' possible vendors; acceptance open')
if __name__=='__main__':main()
