#!/usr/bin/env python3
"""Screen existing civil geometry; model conditional retained rental cash.

Unknown site eligibility remains unknown. Tenant security deposits are locked
cash matched by liabilities, never income or construction finance.
"""
from __future__ import annotations
import argparse
import bisect
from copy import deepcopy
import csv
import gzip
import hashlib
import html
import json
import math
from pathlib import Path
import statistics
import tomllib

ROOT=Path(__file__).resolve().parents[2]
CITY=ROOT/'cities/catalogue/west-asia/Iraq/Baghdad'
OUT=CITY/'engineering/viaduct-rentals'

def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def npv(rows,rate):return sum(value/(1+rate)**(month/12) for month,value in rows)
def write_csv(path,rows):
    if not rows:return
    with path.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)

def validate(config):
    m,g=config['model'],config['geometry']
    if any(m[k]!=0 for k in ('additional_government_cash_usd','additional_chinese_credit_usd','terminal_sale_usd')):
        raise ValueError('Uncommitted public/foreign cash or terminal sale unsupported')
    if any(not 0<=m[k]<=1 for k in ('arrears_fraction','arrears_recovery_fraction','annual_tenant_turnover_fraction','occupied_landlord_cost_fraction','corporate_tax_fraction')):
        raise ValueError('Invalid rental fraction')
    if any(m[k]<=0 for k in ('fitout_months','ramp_months','holding_years','asset_life_years','refurbishment_interval_months')):
        raise ValueError('Invalid rental duration')
    shell_width=g['unit_internal_depth_m']+2*g['wall_thickness_m']
    shell_length=g['unit_internal_frontage_m']+2*g['wall_thickness_m']
    if shell_width+g['independent_access_width_m']>g['reference_deck_width_m'] or shell_length*g['units_per_planning_bay']+2*g['inspection_zone_each_bay_end_m']>g['planning_span_m']:
        raise ValueError('Reference unit blocks access/inspection envelope')
    for c in config['cases'].values():
        if c['target_lettable_m2']<=0 or c['reference_monthly_rent_usd_per_m2']<0 or not 0<=c['target_occupancy']<=1:
            raise ValueError('Invalid portfolio area/rent/occupancy')

def route_points(geo):
    result={}
    for feature in geo['features']:
        if feature['properties'].get('kind')!='line':continue
        coordinates=feature['geometry']['coordinates'];chain=[0.]
        for a,b in zip(coordinates,coordinates[1:]):
            lon1,lat1,lon2,lat2=map(math.radians,(*a[:2],*b[:2]))
            h=math.sin((lat2-lat1)/2)**2+math.cos(lat1)*math.cos(lat2)*math.sin((lon2-lon1)/2)**2
            chain.append(chain[-1]+6371000*2*math.asin(min(1,math.sqrt(h))))
        result[feature['properties']['name']]=(coordinates,chain)
    return result

def point_at(route,station_m,design_length):
    coordinates,chain=route
    # Coordinates are an interpolation of the planning corridor, not a survey.
    distance=max(0,min(chain[-1],station_m/design_length*chain[-1]))
    i=min(len(chain)-2,max(0,bisect.bisect_right(chain,distance)-1))
    f=(distance-chain[i])/(chain[i+1]-chain[i]) if chain[i+1]>chain[i] else 0
    return [coordinates[i][k]+f*(coordinates[i+1][k]-coordinates[i][k]) for k in range(2)]

def register(design,geo,payload,config):
    validate(config);g=config['geometry'];routes=route_points(geo);lengths={r['name']:r['length_m'] for r in design['lines']}
    unit_area=g['unit_internal_frontage_m']*g['unit_internal_depth_m'];rows=[]
    for index,s in enumerate(design['civil_segments']):
        if s['class']!='elevated':continue
        start,end=s['from_station_m'],s['to_station_m'];length=end-start;mid=(start+end)/2
        bays=math.floor(max(0,length-2*g['approach_exclusion_each_end_m'])/g['planning_span_m']) if length>=g['minimum_candidate_segment_m'] else 0
        tracks=[a['asset_id'] for a in payload['assets'] if a['asset_type']=='track-section' and a['line']==s['line'] and float(a['km_start'])*1000<end and float(a['km_end'])*1000>start]
        stations=[r for r in design['stations'] if r['line']==s['line']];nearest=min(stations,key=lambda r:abs(r['s_m']-mid))
        xy=point_at(routes[s['line']],mid,lengths[s['line']])
        rows.append(dict(segment_id=f"{s['line']}:elevated:{start:.1f}:{end:.1f}",design_segment_index=index,line=s['line'],
            chainage_start_m=start,chainage_end_m=end,length_m=length,planning_longitude=xy[0],planning_latitude=xy[1],
            coordinate_basis='Interpolated planning corridor; no surveyed footprint',parent_track_asset_ids=tracks,
            native_parent_link_status='linked-to-existing-track-asset' if tracks else 'unmaterialised-parent-track-link',
            viaduct_product=s.get('viaduct_product'),nearest_station_id=nearest['id'],station_chainage_distance_m=abs(nearest['s_m']-mid),
            screening_bays=bays,screening_units=bays*g['units_per_planning_bay'],screening_net_area_m2=bays*g['units_per_planning_bay']*unit_area,
            screening_status='survey-candidate-not-commercially-eligible' if bays else 'short-segment-excluded-by-reference-kit',
            surveyed_footprint_m2=None,measured_clear_height_m=None,street_frontage_m=None,legal_owner=None,parcel_id=None,
            permitted_use=None,utility_capacity=None,inspection_access_accepted=False,fire_assessment_accepted=False,
            land_overlap_station_sale_checked=False,railway_access_plan_accepted=False,confirmed_eligible_area_m2=0,
            eligibility_accepted=False,lease_signed=False))
    return rows

def allocate(rows,target):
    remaining=target;allocation=[]
    for r in sorted(rows,key=lambda r:(r['station_chainage_distance_m'],-r['screening_net_area_m2'],r['segment_id'])):
        amount=min(remaining,r['screening_net_area_m2'])
        if amount:
            allocation.append(dict(segment_id=r['segment_id'],line=r['line'],assumed_lettable_m2=amount,eligibility_accepted=False));remaining-=amount
        if remaining<=0:break
    return allocation,remaining

def portfolio(name,config,segments,phases,horizon=None):
    if horizon is None:
        horizon=max(p['opening_month'] for p in phases)+config['model']['rail_operating_years']*12-1
    """Cash collection and asset schedule; arithmetic assumptions, no real leases."""
    validate(config);m=deepcopy(config['model']);c=config['cases'][name];m.update({k:v for k,v in c.items() if k in m})
    g=config['geometry'];area=g['unit_internal_frontage_m']*g['unit_internal_depth_m'];unit_cost=sum(config['unit_allowances_usd'].values())
    allocation,shortfall=allocate(segments,c['target_lettable_m2']);by_line={}
    for a in allocation:by_line[a['line']]=by_line.get(a['line'],0)+a['assumed_lettable_m2']
    openings={p['line']:p for p in phases};cohorts=[]
    for line,target in sorted(by_line.items()):
        p=openings[line];start=math.ceil((p['infrastructure_completion_day']+30)*12/260)
        finish=start+m['fitout_months']-1;handover=max(p['opening_month'],finish+1)+c.get('lease_delay_months',0)
        cohorts.append(dict(line=line,lettable_m2=target,constructed_net_m2=math.ceil(target/area)*area,
            build_first_month=start,build_last_month=finish,handover_month=handover,
            first_billing_month=handover+m['rent_free_months'],lease_end_month=min(horizon-1,handover+m['holding_years']*12)))
    if shortfall:
        return dict(status='unmapped-area-blocked',name=name,allocation=allocation,unmapped_area_m2=shortfall,cohorts=cohorts,
            monthly=[],metrics=dict(target_lettable_m2=c['target_lettable_m2'],confirmed_eligible_area_m2=0,financing_committed=False))
    rows=[];arrears=deposit=ppe=tax_next=annual_profit=0.;recoveries={};writeoffs={}
    for month in range(horizon+1):
        rent_index=(1+m['rent_indexation'])**(month//12);opex_index=(1+m['opex_inflation'])**(month//12)
        capital=billed=occupied_cost=vacant_cost=refurb=desired_deposit=dep=active_area=occupied_area=0.
        for p in cohorts:
            ref_cost=p['constructed_net_m2']*unit_cost/area
            if p['build_first_month']<=month<=p['build_last_month']:
                capital+=ref_cost/m['fitout_months']*(1+m['construction_inflation'])**(month/12)
            active=p['handover_month']<=month<p['lease_end_month']
            if active:
                age=month-p['handover_month'];ramp=m['initial_occupancy_fraction_of_target']+(1-m['initial_occupancy_fraction_of_target'])*min(1,age/m['ramp_months'])
                occupancy=c['target_occupancy']*ramp*(1-m['annual_tenant_turnover_fraction']*m['reletting_vacancy_months']/12)
                occupied=p['lettable_m2']*occupancy;active_area+=p['lettable_m2'];occupied_area+=occupied
                # Service costs persist through free concessions and follow
                # their own cost index, including the 7% downside.
                occupied_cost+=occupied*c['reference_monthly_rent_usd_per_m2']*m['occupied_landlord_cost_fraction']*opex_index
                billed+=occupied*c['reference_monthly_rent_usd_per_m2']*rent_index*(1-m['annual_tenant_turnover_fraction']*m['reletting_rent_free_months']/12) if month>=p['first_billing_month'] else 0.
                vacant_cost+=(p['lettable_m2']-occupied)*(m['vacant_maintenance_usd_per_m2_year']+m['vacant_insurance_usd_per_m2_year'])/12*opex_index
                desired_deposit+=occupied*c['reference_monthly_rent_usd_per_m2']*rent_index*m['deposit_months']
                if age and age%m['refurbishment_interval_months']==0:refurb+=ref_cost*m['refurbishment_fraction_of_reference_fitout']*opex_index
                cohort_actual=sum(ref_cost/m['fitout_months']*(1+m['construction_inflation'])**(n/12) for n in range(p['build_first_month'],p['build_last_month']+1))
                if age<m['asset_life_years']*12:dep+=cohort_actual/(m['asset_life_years']*12)
        added=billed*m['arrears_fraction'];due=month+m['arrears_recovery_lag_months']
        recoveries[due]=recoveries.get(due,0)+added*m['arrears_recovery_fraction'];writeoffs[due]=writeoffs.get(due,0)+added*(1-m['arrears_recovery_fraction'])
        # Final month only settles the prior tax and refunds locked deposits.
        # No new taxable recovery can arrive after the final annual accrual;
        # any unresolved receivable is conservatively written off below.
        recovered=recoveries.get(month,0.) if month<horizon else 0.
        bad=writeoffs.get(month,0.);arrears+=added-recovered-bad
        if month==horizon:bad+=arrears;arrears=0.
        collected=billed-added+recovered;opex=occupied_cost+vacant_cost+refurb
        ppe+=capital-dep
        change=desired_deposit-deposit;deposit=desired_deposit
        tax_paid=tax_next;tax_next=0.;annual_profit+=collected-opex-dep
        accrual=0.
        if month%12==11 or month==horizon-1:
            accrual=m['corporate_tax_fraction']*max(0,annual_profit);annual_profit=0.;tax_next=accrual
        rows.append(dict(month=month,physical_fitout_capital_usd=capital,contract_rent_billed_usd=billed,rent_collected_usd=collected,
            arrears_added_usd=added,arrears_recovered_usd=recovered,bad_debt_writeoff_usd=bad,closing_arrears_usd=arrears,
            landlord_opex_usd=opex,occupied_landlord_opex_usd=occupied_cost,vacant_maintenance_and_insurance_usd=vacant_cost,refurbishment_usd=refurb,
            active_lettable_m2=active_area,occupied_m2=occupied_area,depreciation_usd=dep,closing_ppe_usd=ppe,
            tenant_deposit_received_iqd=max(0,change)*1300,tenant_deposit_refunded_iqd=max(0,-change)*1300,
            restricted_deposit_cash_iqd=deposit*1300,tenant_deposit_liability_iqd=deposit*1300,
            deposit_revenue_iqd=0.,standalone_tax_accrual_usd=accrual,standalone_cash_tax_usd=tax_paid,
            unlevered_cash_before_tax_usd=collected-opex-capital,unlevered_cash_after_tax_usd=collected-opex-capital-tax_paid))
    metrics=dict(target_lettable_m2=c['target_lettable_m2'],constructed_net_m2=sum(p['constructed_net_m2'] for p in cohorts),
        confirmed_eligible_area_m2=0,total_fitout_capital_usd=sum(r['physical_fitout_capital_usd'] for r in rows),
        first_conditional_receipt_month=next((r['month'] for r in rows if r['rent_collected_usd']>0),None),
        gross_contract_rent_usd=sum(r['contract_rent_billed_usd'] for r in rows),collected_rent_usd=sum(r['rent_collected_usd'] for r in rows),
        landlord_opex_usd=sum(r['landlord_opex_usd'] for r in rows),refurbishment_usd=sum(r['refurbishment_usd'] for r in rows),
        standalone_cash_tax_usd=sum(r['standalone_cash_tax_usd'] for r in rows),
        resource_npv_before_tax_usd=npv([(r['month'],r['unlevered_cash_before_tax_usd']) for r in rows],m['nominal_discount_rate']),
        standalone_resource_npv_after_tax_usd=npv([(r['month'],r['unlevered_cash_after_tax_usd']) for r in rows],m['nominal_discount_rate']),
        peak_security_deposits_iqd=max(r['tenant_deposit_liability_iqd'] for r in rows),additional_land_opportunity_cost_usd=None,
        actual_leases_signed=0,financing_committed=False)
    metrics['hypothetical_partner_fitout_equity_fraction']=m['private_partner_fitout_equity_fraction']
    return dict(status='conditional-unverified-retained-portfolio',name=name,metrics=metrics,allocation=allocation,unmapped_area_m2=0,
        cohorts=cohorts,monthly=rows,additional_public_cash_usd=0.,additional_chinese_credit_usd=0.,terminal_asset_sale_usd=0.)

def pilot(segments,config,design,geo,payload):
    g=config['geometry'];needed=math.ceil(g['pilot_units']/g['units_per_planning_bay'])
    choices=[s for s in segments if s['screening_bays']>=needed]
    chosen=min(choices,key=lambda s:(s['station_chainage_distance_m'],-s['screening_bays'],s['segment_id']))
    route=route_points(geo)[chosen['line']];length=next(r['length_m'] for r in design['lines'] if r['name']==chosen['line'])
    units=[]
    for i in range(g['pilot_units']):
        start=chosen['chainage_start_m']+g['approach_exclusion_each_end_m']+(i//g['units_per_planning_bay'])*g['planning_span_m']+g['inspection_zone_each_bay_end_m']+(i%g['units_per_planning_bay'])*(g['unit_internal_frontage_m']+2*g['wall_thickness_m'])
        end=start+g['unit_internal_frontage_m']+2*g['wall_thickness_m'];xy=point_at(route,(start+end)/2,length)
        units.append(dict(unit_id=f'BAG-VR-PILOT-{i+1:03d}',segment_id=chosen['segment_id'],line=chosen['line'],
        parent_track_asset_ids=[a['asset_id'] for a in payload['assets'] if a['asset_type']=='track-section' and a['line']==chosen['line'] and float(a['km_start'])*1000<end and float(a['km_end'])*1000>start],planning_longitude=xy[0],planning_latitude=xy[1],
        planning_chainage_start_m=start,planning_chainage_end_m=end,surveyed_footprint=None,
        planning_bay=i//g['units_per_planning_bay']+1,unit_in_bay=i%g['units_per_planning_bay']+1,
        internal_floor_m2=g['unit_internal_frontage_m']*g['unit_internal_depth_m'],unit_design='BAG-VR-KIT-01',
        erp_asset=None,native_lease_contract=None,tenant_customer=None,approved_use=None,lease_start=None,lease_end=None,
        electric_meter_serial=None,water_meter_serial=None,landlord_isolation_point=None,maintenance_access_evidence=None,
        inspection_record=None,approved_fire_plan=None,permit_accepted=False,status='survey-and-qualification-draft',
        hazard_ids=['BAG-VR-H01','BAG-VR-H02','BAG-VR-H03','BAG-VR-H04','BAG-VR-H05']))
    return units

def hazard_rows():
    data=[('H01','Tenant fire, smoke or incompatible storage','Enclosure heat/smoke → pier/cap/bearings → span strength and both tracks',
        'Independent fire/load/egress review; isolate tenant services; exclude unassessed hot work, fuels and battery repair; emergency railway response'),
        ('H02','Flooding or blocked drainage','Unit/drain leakage → foundations/scour/settlement → track geometry and operations',
        'Survey flood paths; independent drained slab; no viaduct drain connections without approval; rainfall inspections and isolation'),
        ('H03','Delivery-vehicle impact','Vehicle/enclosure debris → pier or utilities → shared span and railway operation',
        'Separate loading route; swept paths and engineered independent barriers; no storage/parking in protected pier zones'),
        ('H04','Blocked railway inspection or jacking access','Blocked panels/piers → undetected defect or inaccessible bearing replacement → railway restriction',
        'Enforce landlord/rail access easement; removable panels; prohibit storage in inspection zones; close units for lifting/jacking work'),
        ('H05','Tenant utility fault or unapproved structural fixing','Services/earthing/attachments → pier/deck equipment or live metal → public and railway hazard',
        'Independent foundations and supports; approved isolation/earthing and metering; no drilling, welding or anchors on railway assets')]
    return [dict(hazard_id='BAG-VR-'+key,initiating_event=event,physical_path=path,proposed_controls=controls,
        affected_systems='unit; utilities; pier/foundation; bearing; span; track; railway operation',
        severity='potential-common-physical-railway-hazard',likelihood=None,residual_risk_accepted=False,
        independent_evidence=None,named_risk_owner=None,linked_native_issue=None,
        response='Landlord and railway incident/safety processes; occupancy/operation restriction decided by authorised engineer',
        software_redundancy_mitigation=False) for key,event,path,controls in data]

def unit_svg(config):
    return '''<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="420" viewBox="0 0 1000 420">
<rect width="1000" height="420" fill="white"/><g font-family="sans-serif" fill="#17324d">
<text x="35" y="35" font-size="23">BAG-VR-KIT-01 — planning bay 25 m × reference deck width 7 m</text>
<text x="35" y="62" font-size="15">Independent enclosures; unverified clear height, soil, fire, utilities and land. Not a construction release.</text>
<rect x="50" y="110" width="850" height="238" fill="#f0f5f8" stroke="#46617a"/>
<rect x="50" y="110" width="68" height="238" fill="#fde7b5"/><rect x="832" y="110" width="68" height="238" fill="#fde7b5"/>
<rect x="118" y="110" width="217.6" height="183.6" fill="#c5e6df" stroke="#287969"/>
<rect x="335.6" y="110" width="217.6" height="183.6" fill="#c5e6df" stroke="#287969"/>
<rect x="553.2" y="110" width="217.6" height="183.6" fill="#c5e6df" stroke="#287969"/>
<text x="155" y="200">Unit 1: 30 m² net</text><text x="370" y="200">Unit 2: 30 m² net</text><text x="585" y="200">Unit 3: 30 m² net</text>
<text x="190" y="235">6 × 5 m internal; 6.4 × 5.4 m shell; 3.2 m clear height required</text>
<rect x="118" y="294" width="714" height="40.8" fill="#dce8fa"/><text x="270" y="321">Independent 1.2 m access/egress strip</text>
<text x="51" y="380">2 m protected inspection zones at each support end; pier footprints and jacking envelopes need survey.</text>
<text x="51" y="405">No attachment to pier/cap/deck. Enclosure roof and services remain independent of railway drainage and equipment.</text>
</g></svg>'''

def report_text(segments,cases,config):
    g=config['geometry'];capacity=sum(s['screening_net_area_m2'] for s in segments);rows=[]
    for name,c in config['cases'].items():
        if name=='medium_downside':continue
        annual=c['target_lettable_m2']*c['reference_monthly_rent_usd_per_m2']*12*c['target_occupancy']*.75
        rows.append(f"| {name} | {c['target_lettable_m2']:,.0f} | {c['reference_monthly_rent_usd_per_m2']:.0f} | {c['target_occupancy']:.0%} | {annual/1e6:.2f} |")
    annual=100000*15*12*.8*.75
    illustrative=npv([(48+12*i,annual*1.05**i) for i in range(30)],.134)
    financial=[]
    for name,c in cases.items():
        m=c['metrics']
        if c['status']=='unmapped-area-blocked':financial.append(f"| {name} | unmapped-area-blocked | Unmodelled | Blocked | Unmodelled | Unmodelled |")
        else:financial.append(f"| {name} | {c['status']} | {m['total_fitout_capital_usd']/1e6:.3f} | {m['first_conditional_receipt_month']} | {m['resource_npv_before_tax_usd']/1e6:.3f} | {m['standalone_resource_npv_after_tax_usd']/1e6:.3f} |")
    return f'''# Baghdad retained under-viaduct rental portfolio — {config['model']['as_of']}

Rental income is a conditional addition to the existing station-development **sale** case, with different assets and external tenants. No site is commercially accepted, surveyed, leased or funded. [Network Rail's arch portfolio](https://property.networkrail.co.uk/business-space-let/railway-arches/) provides a precedent for railway SME premises. [Places for London's guidance](https://www.placesforlondon.co.uk/blog/renting-railway-arch-london-what-small-businesses-need-know) emphasises access, services, insulation, fit-out responsibilities and permitted uses. These UK precedents do not establish Iraqi demand, prices or building permissions. Sources checked 4 October 2026.

## Geometry, eligibility and pilot

The controlled design has {len(segments):,} elevated civil segments totalling {sum(s['length_m'] for s in segments)/1000:.4f} km, with median length {statistics.median(s['length_m'] for s in segments):.0f} m. Each [register entry](commercial-space-register.json) carries its civil index, line/chainage, planning coordinates, existing parent track assets and nearest station. {sum(not s['parent_track_asset_ids'] for s in segments)} segments lack a materialised parent track link and need asset-register reconciliation; no ID is invented. Coordinates interpolate the corridor and **are not surveyed footprints**. Clear height, frontage, ownership, title, utilities, permitted use and street/rail access remain null or unaccepted.

The reference screen excludes segments shorter than {g['minimum_candidate_segment_m']} m, reserves {g['approach_exclusion_each_end_m']} m at each approach and counts complete {g['planning_span_m']} m planning bays. Each bay tests three independent 30 m² internal units, with 2 m protected support-end inspection zones and 1.2 m independent access. It suggests **{capacity:,.0f} m²**, before unknown road crossings, utility space, pier positions, access, ownership, flooding, station-sale overlap and fire exclusions. **Confirmed eligible area is zero.** Elevation alone never grants eligibility. Pier height is not usable clear height beneath a cap/deck.

The 200,000 m² illustration exceeds this screen by {max(0,200000-capacity):,.0f} m² and is **unmapped-area-blocked**, with no lease receipts in executable integrated cases. It requires a different surveyed footprint/reference layout; there is no automatic widening of a viaduct. Small/medium models allocate assumed area against identified civil segments and phase construction by their infrastructure dates. These are conditional surveys-to-test, not valuations. [Thirty draft pilot units](pilot-digital-twin.json) use one long candidate selected by station-chainage proximity and bay count, without a claim of commercial desirability. Market-test 20–50 units through comparable IQD rents, tenant interest, permissions and costed fit-outs before expansion. No external contact has been made.

## Open reference unit and costs

[Unit plan](unit-plan.svg) gives a 6 × 5 m internal module in a 6.4 × 5.4 m independent shell, requiring 3.2 m measured clear height. [Parts and allowances](unit-parts.csv) total USD 21,000 equivalent per 30 m² unit: USD 18,000 direct, USD 2,000 design/shared services and USD 1,000 contingency, contracted in IQD. These are planning allowances, not quotes. Walls/roof, thermal/acoustic insulation, drainage, slab, independent foundations, doors/windows, separate metered/isolation services, fire/egress equipment, vehicle protection and removable inspection panels are included. Actual soil, materials, fire protection and service capacity may change cost materially. No structure is dimensioned from rental value alone; compare net value against costs before modifying supports or spans. Open licences remain intact.

The shell is independent of railway piers/caps/deck: no drilling, welding or load attachment. Preserve bearing/jacking, drainage and electrical access, surveyed support clearances and maintenance easements. Independent utility meters are paid directly by tenants in the model; no utility reimbursement is booked as extra profit. Retail, services and studios are candidate uses only; workshops, cooking, hot works, fuel/solvent storage and battery activities require specific assessments. There is no generic permission for a use because it fits the floor area.

## Illustrations versus priced cash-flow scenarios

| Area illustration | Lettable m² | Monthly rent USD eq/m² | Occupancy | Annual landlord NOI USD m eq |
| --- | --- | --- | --- | --- |
{chr(10).join(rows)}

These illustrations deduct 25% of occupied receipts and exclude capital, financing and tax. For the medium illustration, 30 annual receipts, **first at month 48**, rising 5% each year, discounted at 13.4%, have PV **USD {illustrative/1e6:.3f}m**. Explicit payment dates matter: this is receipts-only PV, not project NPV or the phased portfolio forecast.

| Executable rental scenario | Status | Fit-out capital USD m eq | First conditional cash month | Resource NPV before tax USD m eq | Standalone after-tax NPV USD m eq |
| --- | --- | --- | --- | --- | --- |
{chr(10).join(financial)}

Monthly ledgers phase fit-outs after the corresponding infrastructure-completion month and delay tenant handover until railway opening or fit-out completion, whichever is later. Six-month enclosures, three initial rent-free months and an 18-month occupancy ramp precede steady receipts. The last fractional module is constructed in full; spare floor area receives no rent. Rent and OPEX escalate 5% from financial close, and unquoted capital escalates 5% to each invoice. The downside uses rent USD 9/m², 55% target occupancy, 12 extra months of vacancy, a 36-month ramp, 8% arrears and 7% OPEX inflation.

Market vacancy is separate from modeled tenant turnover (10%/year, three-month re-letting vacancy and one-month free concession). Three-percent arrears have 50% recovery after six months; unrecovered debt is written off, and final unresolved receivables have zero recoverable value. Revenue is cash collected in these pro-forma sensitivity accounts; statutory accrual/tax treatment needs advice. Occupied maintenance/insurance uses 25% of reference occupied face rent with its **own OPEX index**, including during rent-free concessions, plus USD 10/m²/year for vacant-unit maintenance/insurance. Costs persist through concessions or defaults. Major refurbishment is additional cash expense at 20% of reference fit-out every 12 years, with OPEX inflation; it is not also capitalised. Existing station kiosk receipts are unchanged.

Security deposits of two months' indexed face rent are assumed topped up/refunded with occupancy. They are separately restricted cash **and tenant liabilities**, with zero revenue, zero construction funding and no shareholder distribution. Ending leases refund all deposits. No upfront lease premium or sold rental parcel is booked. Parcel overlap with the existing 15 station sale candidates is unknown and must be accepted as disjoint before either case can become executable. Current site-right cash is explicitly assumed zero, with additional land opportunity cost unknown: full site economics cannot be concluded from the reported before-land NPV. No USD credit or additional government cash is assumed for fit-outs.

Assets depreciate over 20 years from each cohort handover. Standalone tax applies the illustrative 15% positive annual cash-profit-after-depreciation proxy, with no loss relief or interest deductions, paid the next month; it is not an Iraqi tax ruling. The holding model instead includes the same portfolio inside its separate-business tax stress, so **standalone tax is not deducted twice**. The project horizon caps late cohorts' rental years and leaves no unsupported terminal sale/rent beyond the railway forecast. These cases improve only to the extent that collected rent exceeds all additional resources and costs.

## Financing, dividends and terminal cash

[Financing redesign](../financing-redesign/README.md) adds a separately financed retained-property entity with 25% private partner fit-out equity and IQD construction bank debt. Its operating-gap capacity is zero; missing carry/fees/reserves are exposed rather than adding an uncommitted facility to the existing 13tn cap. Internal distributions are zero pending lender consent. External tenant cash adds group revenue; future property-to-rail transfers would cancel exactly. The [holding-equity study](../equity/README.md) uses the same resources with a 100%-owned business, replacing partner equity with the parent subscription case and borrowing the residual in IQD. These are alternative ownership/funding structures, not cumulative sources.

The holding study separately compares all-debt-repaid dividends with an unapproved coverage/reserve/profit-based policy, and reports a diagnostic of proportional final unrestricted cash net of liabilities. Cash at the horizon is not a guaranteed redemption, quoted share price or assumed sale of railway/property assets. Do not confuse that diagnostic with actual company distributions or count cash twice. Company accounts remain separately reconciled.

## Digital twin, common hazards and evidence

Every draft pilot unit links its civil segment/parent track, proposed enclosure design, unknown lease and tenant IDs, meters, isolation, inspection rights, permitted use and [hazard records](hazards.json). The [native ERP mapping](erp-record-map.json) uses existing Asset/Contract/Customer/Sales Invoice/Payment Entry/Asset Maintenance/Issue types when actual records and permissions exist; null IDs are not live leases, meters or safety records. No fake tenant, permit, contract or asset is created from an unverified footprint.

Tenant fire, flooding/drainage, delivery impact, blocked inspection access and utility/attachment faults propagate from enclosure to pier/foundation, bearings and shared spans and can affect railway operations. Redundant onboard controllers provide no mitigation for these common physical hazards. Proposed inspections include pre-lease engineering acceptance, monthly access/drain/isolation checks, post-incident checks, annual structure-linked inspection and controlled jacking/maintenance closures; durations and legal/fire requirements need actual assessment. Native maintenance/Issue records must trace the landlord obligation to the railway asset and escalation owner. Occupancy and any railway restriction require the authorised engineer's decision, not automatic evidence acceptance by this model.

[Six 90-day evidence packages](90-day-work-programme.json) require surveyed eligibility and rights/no-overlap, independent civil/fire/utility access acceptance, market-tested pilot leases, supplier fit-out/refurbishment quotes, native lease/meter/maintenance controls, and independent cash/tax/funding/distribution review. Named people, surveys, quotes and leases remain pending. Native ERP Task imports are open drafts; no evidence or operating release is granted.

Regenerate `.venv/bin/python tools/automation/baghdad_viaduct_rentals.py`, then financing redesign, equity and proposal; validate source/output hashes with `--check`.
'''

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--check',action='store_true');a=p.parse_args()
    if a.check:
        s=json.loads((OUT/'summary.json').read_text())
        for base,key in ((ROOT,'sources_sha256'),(OUT,'outputs_sha256')):
            for rel,sha in s[key].items():
                if digest(base/rel)!=sha:raise ValueError('Stale viaduct rentals '+rel)
        print('Viaduct rental source/output hashes pass');return
    paths=[Path(__file__),ROOT/'lib/templates/baghdad-viaduct-rentals.toml',CITY/'design.toml',CITY/'baghdad.corridor.geojson',
        CITY/'operations/baghdad-operations.json.gz',CITY/'engineering/delivery-risk/summary.json',ROOT/'docs/civil/viaduct-substructure-kit.md',ROOT/'lib/templates/iraq-funding.toml']
    config=tomllib.loads(paths[1].read_text())
    if config['model']['rail_operating_years']!=tomllib.loads(paths[-1].read_text())['model']['operating_years']:raise ValueError('Rental/rail operating horizons disagree')
    design=tomllib.loads(paths[2].read_text());geo=json.loads(paths[3].read_text())
    payload=json.loads(gzip.decompress(paths[4].read_bytes()));risk=json.loads(paths[5].read_text())
    sources={r.relative_to(ROOT).as_posix():digest(r) for r in paths};revision=hashlib.sha256(json.dumps(sources,sort_keys=True).encode()).hexdigest()
    segments=register(design,geo,payload,config);cases={name:portfolio(name,config,segments,risk['cases']['calendar_baseline']['phases']) for name in config['cases']}
    OUT.mkdir(parents=True,exist_ok=True);outputs=[]
    def save(name,value):
        r=OUT/name;r.write_text(json.dumps(value,indent=2,sort_keys=True,allow_nan=False)+'\n');outputs.append(r)
    def csvout(name,rows):
        if rows:write_csv(OUT/name,rows);outputs.append(OUT/name)
    save('commercial-space-register.json',segments);csvout('commercial-space-register.csv',segments)
    save('pilot-digital-twin.json',pilot(segments,config,design,geo,payload));save('hazards.json',hazard_rows());csvout('hazards.csv',hazard_rows())
    save('erp-record-map.json',dict(status='draft-no-native-unit-lease-records',native_ids=None,
        record_types=['Asset','Contract','Customer','Sales Invoice','Payment Entry','Asset Maintenance','Issue'],
        linked_existing_parent_assets=True,meters_are_physical_serials_not_invoice_revenue=True,
        lease_fields=['unit_id','civil_segment_id','tenant_customer','approved_use','dates','rent_iqd','index_clause','deposit_liability','landlord_rail_access_easement'],
        maintenance_fields=['parent_rail_asset','unit_asset','inspection_scope','cadence','isolation','hazard_id','independent_acceptance'],
        deposit_accounting='Restricted cash asset plus tenant liability; no rent revenue, capital funding or dividend'))
    quantities=[(67.12,'m2 wall envelope less door/window allowance'),(5.184,'m3 at 150 mm slab planning thickness'),(34.56,'m2 independent roof'),
        (1,'door/window set'),(1,'electrical/water meters and isolation set'),(1,'fire/egress equipment set'),(1,'independent drainage set'),
        (1,'foundation set; size/reinforcement unverified'),(1,'access/impact protection set'),(1,'removable inspection panel set'),(1,'design/shared-service allowance'),(1,'contingency allowance')]
    parts=[dict(part_id='BAG-VR-KIT-'+str(i+1).zfill(2),scope=key.replace('_',' '),planning_quantity=quantities[i][0],quantity_basis=quantities[i][1],reference_allowance_usd=value,allowance_iqd=value*1300,
        quote=None,engineering_accepted=False) for i,(key,value) in enumerate(config['unit_allowances_usd'].items())]
    csvout('unit-parts.csv',parts);save('unit-parts.json',parts)
    svg=OUT/'unit-plan.svg';svg.write_text(unit_svg(config));outputs.append(svg)
    for name,c in cases.items():
        save(name+'.json',c);csvout(name+'-monthly.csv',c['monthly'])
        semi=[]
        for first in range(0,len(c['monthly']),6):
            rows=c['monthly'][first:first+6];keys=['physical_fitout_capital_usd','rent_collected_usd','landlord_opex_usd','refurbishment_usd','standalone_cash_tax_usd','tenant_deposit_received_iqd','tenant_deposit_refunded_iqd']
            semi.append(dict(start_month=rows[0]['month'],end_month=rows[-1]['month'],**{k:sum(r[k] for r in rows) for k in keys},
                closing_deposit_cash_iqd=rows[-1]['restricted_deposit_cash_iqd'],closing_deposit_liability_iqd=rows[-1]['tenant_deposit_liability_iqd']))
        csvout(name+'-six-months.csv',semi)
    workstreams=[('SITE','Survey/title and independent valuer','Segment footprint, height, frontage, utilities, permissions, railway access, road/flood exclusions and no overlap with sold station parcels',15,60),
        ('CIVIL','Civil engineer and independent fire authority','Independent enclosure/soil/impact/fire/egress, pier/bearing/jacking access, utility isolation and common hazard acceptance',15,75),
        ('MARKET','Iraqi commercial leasing lead','20–50-unit pilot: comparable IQD rents, licensed permitted tenants, vacancy/arrears, obligations and signed lease evidence',30,75),
        ('COST','Local supplier procurement lead','Itemised shell/utility/insurance/maintenance/refurbishment and site-right quotes against the unit allowance',30,75),
        ('TWIN','Landlord asset manager and ERP lead','Actual native asset/lease/meter/customer/invoice/deposit/maintenance/Issue trace and independently accepted access obligations',30,90),
        ('FINANCE','Independent model reviewer and lender counsel','Funding placements, separate-business tax, no sold/rented overlap, deposit liabilities, group eliminations and distribution/exit covenants',60,90)]
    packages=[dict(id='BAG-EVID-VR90-'+key,accountable_owner_role=role,named_owner=None,start_day=start,due_day=due,
        day_basis='Days from approved rental-evidence start; no calendar date assigned',output=output,evidence=None,status='not-demonstrated',
        source_revision=revision,acceptance_rule='Independent signed site/engineering/market/legal evidence; model is not acceptance') for key,role,output,start,due in workstreams]
    save('90-day-work-programme.json',dict(work_packages=packages,status='draft-no-evidence',external_contacts_made=False))
    tasks=[dict(subject=r['id']+' — '+r['accountable_owner_role'],status='Open',priority='High',description='<pre>'+html.escape(json.dumps(r,indent=2))+'</pre>') for r in packages]
    save('erpnext-tasks.json',dict(doctype='Task',status='draft-import-package-not-live-records',tasks=tasks));csvout('erpnext-task-import.csv',tasks)
    report=OUT/'README.md';report.write_text(report_text(segments,cases,config));outputs.append(report)
    (OUT/'summary.json').write_text(json.dumps(dict(schema='baghdad-retained-viaduct-rentals/1',as_of=config['model']['as_of'],source_revision=revision,
        sources_sha256=sources,outputs_sha256={r.name:digest(r) for r in outputs},confirmed_eligible_area_m2=0,
        screening_area_m2=sum(r['screening_net_area_m2'] for r in segments),elevated_segment_count=len(segments),elevated_length_m=sum(r['length_m'] for r in segments),
        operational_release=False,financing_committed=False,commercial_eligibility_accepted=False,
        cases={n:dict(status=c['status'],metrics=c['metrics'],unmapped_area_m2=c['unmapped_area_m2']) for n,c in cases.items()}),indent=2,sort_keys=True)+'\n')
    print('Generated 1143 civil-linked candidate records, 30 pilot unit drafts, rental ledgers, hazards and six ERP evidence packages')

if __name__=='__main__':main()
