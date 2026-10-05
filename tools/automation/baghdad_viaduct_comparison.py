#!/usr/bin/env python3
"""Compare complete viaduct packages without manufacturing quotes or savings."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import re
from pathlib import Path
import sys
import tomllib

ROOT = Path(__file__).resolve().parents[2]
CITY = ROOT / 'cities/catalogue/west-asia/Iraq/Baghdad'
OUT = CITY / 'engineering/viaduct-comparison'
CONFIG = ROOT / 'lib/templates/baghdad-viaduct-comparison.toml'
sys.path.insert(0, str(ROOT / 'design/component-catalogue/src'))
from osr_mech.civil.decked_pi import approx_mass_kg, section_area_m2
from osr_mech.civil.continuity import semi_continuous_unit_plan
from osr_mech.civil.ugirder import EXTERNAL_WIDTH_MM as US_WIDTH_MM, section_area_m2 as us_area
from osr_mech.civil.viaduct import ViaductEnvelopeCheck, straight_span_chord_offset_m

BUCKETS = (
    ('beam-concrete', 'm3'), ('reinforcement', 'kg'), ('prestressing', 'kg'),
    ('connections-and-grout', 'assembly'), ('columns-and-caps', 'support'),
    ('foundations-by-ground-zone', 'support'), ('bearings', 'each'),
    ('trackform', 'track-m'), ('drainage-walkways-barriers', 'route-m'),
    ('yard-beds-moulds', 'package'), ('transport', 'delivery'),
    ('erection-plant-and-mobilisation', 'package'), ('temporary-works', 'package'),
    ('traffic-management', 'package'), ('labour-rework-and-QA', 'package'),
    ('design-independent-check-testing', 'package'), ('maintenance-access', 'package'),
)
SEPARATE_COSTS = ('land-and-rights', 'utility-relocation', 'tax-and-duties',
                  'escalation', 'risk-contingency', 'financing')
STAGES = ('foundation', 'column-cap-connection', 'casting-and-strength-release',
          'transport', 'erection', 'structural-or-link-connection', 'track-egress',
          'survey-correction-and-acceptance')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def positive(value, label, *, zero=False):
    if type(value) not in (int, float) or not math.isfinite(value) or value < 0 or (not zero and value == 0):
        raise ValueError(f'{label} must be finite and {"nonnegative" if zero else "positive"}')
    return value


def support_layout(length_m, span_m, scheme, *, tracks=2, unit_spans=4):
    """Count finite assets, including both end supports; never omit end bearings."""
    positive(length_m, 'length'); positive(span_m, 'span')
    if span_m not in (20., 25.) or type(tracks) is not int or tracks != 2 or unit_spans != 4:
        raise ValueError('Comparison requires 20/25 m spans, two tracks and four-span units')
    if scheme not in ('simple-span-link-slab', 'structural-continuity'):
        raise ValueError('Unknown bearing scheme')
    spans = round(length_m/span_m)
    if spans < 1 or abs(spans*span_m-length_m) > 1e-6:
        raise ValueError('A closure-span design is required for a nondivisible length')
    units = math.ceil(spans/unit_spans)
    supports = []
    for index in range(spans+1):
        end = index in (0, spans)
        boundary = not end and index % unit_spans == 0
        count = 4 if end or (scheme == 'structural-continuity' and not boundary) else 8
        supports.append(dict(support_id=f'S-{index:03}',candidate_chainage_m=index*span_m,
            role='end' if end else 'expansion' if boundary else 'internal',bearings=count,
            ground_zone=None,foundation_product=None,actual_deep_element_length_m=None,
            deep_element_count=None,utilities_survey=None,structural_calculation=None,
            installed_foundation_cost=None,currency=None,quotation=None,accepted=False))
    total_bearings=sum(r['bearings'] for r in supports)
    shared=semi_continuous_unit_plan(length_m,span_m=span_m,connection_scheme=scheme)
    if total_bearings!=shared.bearings:raise ValueError('Finite support register differs from catalogue bearings')
    return dict(spans=spans,support_locations=len(supports),single_track_beams=tracks*spans,
        movement_units=units,internal_connections=spans-units,deck_expansion_gaps=units-1,
        bearings=total_bearings,supports=supports,
        structural_continuity_accepted=False,finite_end_supports_included=True)


def installed_estimate(rows, route_m, fx):
    """Partial costs stay partial; unpriced scope cannot produce a total."""
    positive(route_m, 'route'); positive(fx, 'FX')
    missing=[];subtotal=0.;seen=set()
    for row in rows:
        key=row['id']
        if key in seen: raise ValueError('Duplicate cost item: '+key)
        seen.add(key)
        quantity, rate = row.get('quantity'), row.get('rate')
        if quantity is not None: positive(quantity, key+' quantity', zero=True)
        if rate is not None: positive(rate, key+' rate', zero=True)
        if quantity is None or rate is None or row.get('currency') is None:
            missing.append(key); continue
        if row['currency'] not in ('IQD','USD'): raise ValueError('Unsupported quote currency')
        value = quantity*rate/(fx if row['currency']=='IQD' else 1.)
        positive(value, key+' amount', zero=True);subtotal+=value
    required={key for key,_ in BUCKETS}|set(SEPARATE_COSTS)
    missing+=sorted(required-seen)
    if not math.isfinite(subtotal): raise ValueError('Estimate overflow')
    return dict(known_subtotal_usd=subtotal,unpriced_items=missing,
        installed_total_usd=None if missing else subtotal,
        installed_usd_per_completed_double_track_m=None if missing else subtotal/route_m,
        quoted_and_independently_checked=False,construction_release=False)


def production_capacity(stages):
    """Use accepted complete bays per week, with all fronts measured on that basis."""
    unknown=[];rates={}
    for stage in STAGES:
        row=stages.get(stage,{})
        crews,hours,cycle=row.get('crews'),row.get('productive_hours_per_crew_week'),row.get('crew_hours_per_complete_bay')
        if any(v is None for v in (crews,hours,cycle)):
            unknown.append(stage);continue
        if type(crews) is not int: raise ValueError('Crew count must be integer')
        for value in (crews,hours,cycle):positive(value,stage)
        rates[stage]=crews*hours/cycle
    return dict(stage_capacity_bays_per_week=rates,missing_stage_inputs=unknown,
        complete_double_track_bays_per_week=None if unknown else min(rates.values()),
        cycle_measured=False,resource_loaded_programme_accepted=False,
        note='Steady-state bottleneck only; precedence, curing, stock buffers, closures and shifts need an accepted programme')


def bearing_index_delta_contracts(contracts, task_lines, design, cost):
    """Price only existing Pi25 length; inherit civil invoice timing/origin as a sensitivity."""
    driver=next(r for r in cost['classes']['elevated']['drivers'] if r['quantity']=='bearings_per_km')
    delta=cost['classes']['elevated']['benchmark_usd_per_km']*driver['cost_share']*(320-driver['current_quantity'])/driver['benchmark_quantity']
    positive(delta,'bearing index delta',zero=True)
    lengths={}
    for segment in design['civil_segments']:
        if segment['class']=='elevated' and segment.get('viaduct_product')=='OSR-Pi25':
            lengths[segment['line']]=lengths.get(segment['line'],0)+positive(segment['to_station_m']-segment['from_station_m'],'Pi25 length')
    result=[]
    for line,length in lengths.items():
        invoices=[r for r in contracts if r['bucket']=='civil' and task_lines.get(r['manufacturing_uid'])==line]
        for invoice in invoices:
            positive(invoice['budget_usd'],'civil invoice budget',zero=True)
            share=positive(invoice['imported_share'],'civil import share',zero=True)
            if share>1:raise ValueError('Civil import share exceeds one')
            start,finish=invoice['planned_start_day'],invoice['planned_finish_day']
            if type(start) is not int or type(finish) is not int or start<0 or finish<start:
                raise ValueError('Invalid civil invoice dates')
        budget=sum(r['budget_usd'] for r in invoices)
        positive(budget,'civil invoice profile')
        for invoice in invoices:
            result.append(dict(bucket='bearing_index_delta',line=line,
                budget_usd=length/1000*delta*invoice['budget_usd']/budget,
                imported_share=invoice['imported_share'],planned_start_day=invoice['planned_start_day'],
                planned_finish_day=invoice['planned_finish_day'],source_invoice=invoice['manufacturing_uid'],
                rate_quality='unquoted-Pi25-only-index-sensitivity',actual_bearing_origin_and_dates_accepted=False))
    return result


def alignment_register(design,rate):
    source=(ROOT/'crates/osr-routing/src/civil.rs').read_text()
    preferred=float(re.search(r'ELEVATED_PREFERRED_RADIUS_M:\s*f64\s*=\s*([\d_.]+)',source).group(1).replace('_',''))
    chord_limit=ViaductEnvelopeCheck().maximum_chord_adjustment_mm/1000
    rows=[]
    for index,segment in enumerate(design['civil_segments']):
        if segment['class']!='elevated':continue
        length=positive(segment['to_station_m']-segment['from_station_m'],'segment length')
        multiplier=positive(segment.get('elevated_cost_multiplier',1.),'routing factor')
        if multiplier < 1:raise ValueError('Routing factor cannot imply a priced saving')
        base=length/1000*rate
        proxy_radius=segment.get('minimum_curve_radius_m')
        offsets={span:straight_span_chord_offset_m(span,proxy_radius) if proxy_radius and proxy_radius>span/2 else None for span in (20,25)}
        stations=[s for s in design.get('stations',[]) if s['line']==segment['line']]
        nearest=sorted(stations,key=lambda s:min(abs(s['s_m']-segment['from_station_m']),abs(s['s_m']-segment['to_station_m'])))[:2]
        rows.append(dict(id=f"{segment['line']}:civil-{index:04}",line=segment['line'],
            from_station_m=segment['from_station_m'],to_station_m=segment['to_station_m'],length_m=length,
            product=segment.get('viaduct_product'),minimum_radius_m=segment.get('minimum_curve_radius_m'),
            routing_multiplier=multiplier,standard_rate_allowance_usd=base,
            radius_proxy_from_routing_multiplier_m=proxy_radius,
            radius_proxy_is_surveyed=False,nearest_station_ids=';'.join(s['id'] for s in nearest),
            pi20_chord_offset_proxy_m=offsets[20],pi25_chord_offset_proxy_m=offsets[25],
            chord_planning_limit_m=chord_limit,
            pi20_chord_screen_passed=None if offsets[20] is None else offsets[20]<=chord_limit,
            special_priority_rank=None,
            routing_penalty_usd=0.,original_modelled_cost_usd=base,
            search_penalty_equivalent_m=length*(multiplier-1),search_penalty_is_money=False,
            special_structure_increment_usd=None if segment.get('viaduct_product') not in ('OSR-Pi25','OSR-Pi20') else 0.,
            installed_total_usd=None,
            quantity_basis='Local method length; supplier geometry/support layout and installed unit rates unresolved',
            bare_pi_concrete_m3=section_area_m2()*length*2 if segment.get('viaduct_product') in ('OSR-Pi25','OSR-Pi20') else None,
            priced_structural_design=False,review_priority='individual-special-review' if segment.get('viaduct_product')=='REALIGN-OR-SPECIAL' else 'corridor-review',
            wider_curve_candidate=None,station_move_candidate=None,alternative_right_of_way=None,
            realignment_installed_cost_usd=None,segmental_installed_cost_usd=None,
            utility_and_land_cost_usd=None,traffic_cost_usd=None,whole_life_cost_usd=None,
            selected_alternative=None,actual_od_count=None,accepted=False))
    special=sorted((r for r in rows if r['product']=='REALIGN-OR-SPECIAL'),key=lambda r:(-r['search_penalty_equivalent_m'],r['id']))
    for rank,row in enumerate(special,1):row['special_priority_rank']=rank
    return rows


def build():
    cfg=tomllib.loads(CONFIG.read_text());design=tomllib.loads((CITY/'design.toml').read_text())
    if any(value not in (0,False) for value in cfg['evidence'].values()):
        raise ValueError('Physical evidence requires controlled records; configuration cannot assert acceptance')
    cost=tomllib.loads((ROOT/'lib/templates/civil-cost-model.toml').read_text())
    train=tomllib.loads((ROOT/'lib/templates/rolling-stock.toml').read_text())['profiles']['metro-6car']
    load=tomllib.loads((ROOT/'docs/civil/viaduct-load-model.toml').read_text())['deployment_trains']['metro-6car']
    if load['axles']!=train['cars']*4 or load['cars']!=train['cars'] or load['length_m']!=train['length_m'] or load['tare_mass_t']!=train['tare_mass_t']:
        raise ValueError('Six-car infrastructure seed differs from the controlled train')
    for key,capacity in [('aw2_mass_t','passenger_capacity'),('aw3_mass_t','crush_capacity')]:
        if load[key]!=train['tare_mass_t']+train[capacity]*load['passenger_mass_kg']/1000:
            raise ValueError('Loaded train mass differs from the controlled profile')
    length=positive(cfg['comparison_route_m'],'comparison route')
    if cfg['tracks']!=2 or cfg['movement_unit_spans']!=4:raise ValueError('Unsupported comparison layout')
    fx=positive(cfg['iqd_per_usd_reference'],'FX')
    if fx!=tomllib.loads((ROOT/'lib/templates/iraq-funding.toml').read_text())['model']['iqd_per_usd']:
        raise ValueError('Reconcile funding/comparison FX')
    packages=[]
    for span in (20.,25.):
        for scheme in ('simple-span-link-slab','structural-continuity'):
            layout=support_layout(length,span,scheme)
            packages.append(dict(id=f'Pi{span:g}-{scheme}',product=f'OSR-Pi{span:g}',span_m=span,
                scheme=scheme,geometry=layout,bare_member_mass_kg=approx_mass_kg(span),
                bare_member_target_margin_kg=(60000 if span==20 else 75000)-approx_mass_kg(span),
                complete_member_mass_kg=None,hook_demand_kg=None,actual_equipment_offer=None,
                transport_width_m=2.9,beam_lifts=layout['single_track_beams'],
                bare_beam_concrete_m3=section_area_m2()*length*2,
                erection_options=['configured ground crane or lifting portal','qualified self-launching frame'],
                construction_release=False))
    segment_length=positive(cfg['segment_length_m'],'segment length')
    if not 2.5<=segment_length<=3 or abs(25/segment_length-round(25/segment_length))>1e-6:
        raise ValueError('Match-cast length must divide a 25 m span and remain 2.5–3 m')
    segment_layout=support_layout(length,25.,'simple-span-link-slab')
    # OSR-US geometry, tendon and support design cannot inherit Pi quantities.
    for support in segment_layout['supports']:support['bearings']=None
    segment_layout['bearings']=None;segment_layout['internal_connections']=None
    segment_count=int(length/segment_length)*2
    packages.append(dict(id='US25-segmental',product='OSR-US',span_m=25.,scheme='supplier-segmental-design',
        geometry=segment_layout,segment_length_m=segment_length,segment_lifts=segment_count,
        match_cast_internal_joints=segment_count-segment_layout['single_track_beams'],
        bare_member_mass_kg=None,complete_member_mass_kg=None,hook_demand_kg=None,
        coordination_segment_bare_mass_upper_bound_kg=us_area()*segment_length*2500,
        coordination_mass_basis='Straight-length envelope at catalogue bulk 2500 kg/m3; excludes net details and rigging',
        transport_width_m=US_WIDTH_MM/1000,primary_shipping_target_m=3.0,
        primary_shipping_target_met=US_WIDTH_MM<=3000,
        bare_beam_concrete_m3=None,actual_equipment_offer=None,
        erection_options=['qualified overhead segment launcher'],construction_release=False))
    for package in packages:
        quantities={'beam-concrete':package['bare_beam_concrete_m3'],
            'columns-and-caps':package['geometry']['support_locations'],
            'foundations-by-ground-zone':package['geometry']['support_locations'],
            'bearings':package['geometry']['bearings'],'trackform':length*2,
            'drainage-walkways-barriers':length,'transport':package.get('beam_lifts',package.get('segment_lifts'))}
        package['cost_items']=[dict(id=key,unit=unit,quantity=quantities.get(key),rate=None,currency=None,
            quotation=None,price_date=None,inclusions=None,exclusions=None,
            invoice_origin=None,chinese_credit_eligibility=None,independently_checked=False) for key,unit in BUCKETS]
        package['cost_items'] += [dict(id=key,unit='package',quantity=None,rate=None,currency=None,
            quotation=None,price_date=None,inclusions=None,exclusions=None) for key in SEPARATE_COSTS]
        package['estimate']=installed_estimate(package['cost_items'],length,fx)
        package['production_stages']={s:dict(crews=None,productive_hours_per_crew_week=None,
            crew_hours_per_complete_bay=None,measured_trial=None,strength_release=None,
            survey_tolerance_and_correction=None,accepted=False) for s in STAGES}
        package['capacity']=production_capacity(package['production_stages'])
    rate=cost['civil_usd_per_km']['elevated'];rows=alignment_register(design,rate)
    candidate=max((r for r in rows if r['product']=='OSR-Pi25'),key=lambda r:r['length_m'])
    benchmark=cost['classes']['elevated']['benchmark_usd_per_km']
    bearing_driver=next(r for r in cost['classes']['elevated']['drivers'] if r['quantity']=='bearings_per_km')
    # This is only the existing index's bearing term, without reapplying curve penalties.
    delta=benchmark*bearing_driver['cost_share']*(320-bearing_driver['current_quantity'])/bearing_driver['benchmark_quantity']
    concrete_driver=next(r for r in cost['classes']['elevated']['drivers'] if r['quantity']=='bare_beam_concrete_m3_per_km')
    total_length=sum(r['length_m'] for r in rows)
    effects=[dict(reduction_fraction=p,elevated_rate_usd_per_km=rate*(1-p),
        same_budget_length_multiplier=1/(1-p),achievable_saving=False) for p in (.1,.2,.3)]
    finance_context=json.loads((CITY/'engineering/delivery-closure/finance-reconciled_full_fleet.json').read_text())['metrics']
    bearing_finance=json.loads((CITY/'engineering/delivery-closure/finance-simple_span_bearing_index.json').read_text())
    pi25_length=sum(r['length_m'] for r in rows if r['product']=='OSR-Pi25')
    return dict(schema='baghdad-viaduct-comparison/1',status=cfg['status'],comparison_route_m=length,
        existing_integrated_finance_metrics=finance_context,
        bearing_sensitivity_finance_metrics=bearing_finance['metrics'],
        actual_corridor_candidate=candidate,actual_corridor_selected=False,
        candidate_basis='Longest existing Pi25 run, for investigation only; the 1 km comparison is separate',
        complete_train=load,packages=packages,alignment_segments=rows,
        elevated_length_m=total_length,standard_rate_allowance_usd=sum(r['standard_rate_allowance_usd'] for r in rows),
        routing_penalty_usd=sum(r['routing_penalty_usd'] for r in rows),
        original_modelled_elevated_cost_usd=sum(r['original_modelled_cost_usd'] for r in rows),
        special_segment_count=sum(r['product']=='REALIGN-OR-SPECIAL' for r in rows),
        bearing_index_sensitivity=dict(current_conditional_rate_usd_per_km=rate,
            simple_span_link_slab_rate_usd_per_km=rate+delta,delta_usd_per_km=delta,
            direct_network_delta_usd=total_length/1000*delta,adopted=False,
            uniform_network_delta_is_not_a_priced_scope=True,
            financed_pi25_only_length_m=pi25_length,
            financed_pi25_only_direct_delta_usd=sum(r['budget_usd'] for r in bearing_finance['capital_components'] if r['bucket']=='bearing_index_delta'),
            connection_and_consequential_costs_usd=None,rate_quality='unquoted-index-sensitivity'),
        beam_concrete_20pct_reduction_index_delta_usd_per_km=benchmark*concrete_driver['cost_share']*concrete_driver['quantity_ratio']*.2,
        elevated_budget_sensitivities=effects,
        quote_scope=['Checked complete train loading and structural scheme','Per-support ground zone and actual foundations',
            'Complete mass budget and configured transport/erection proposal','Precast cap/column/cages/inserts and connection release',
            'Resource-loaded programme and measured accepted double-track bay cycle','Complete installed and maintenance costs'],
        equipment_release_fields=['equipment_id','configured_capacity_chart','complete_member_and_rigging_mass',
            'lift_radius','wind_limit','ground_pressure','launcher_reactions','deck_delivery_loads',
            'route_swept_path','bridge_culvert_capacity','overhead_clearance','axle_configuration',
            'temporary_bracing','synchronisation','landing_and_recovery_plan'],
        first_article_hold_points=['Checked scheme and independent design','First mould/bed and prestress transfer',
            'First complete beam weighed and transport trial','Representative pier/cap/connection assembly',
            'Trial erection including temporary reactions','Track/egress/drainage and final survey acceptance',
            'Measured cycles, rework, labour, equipment and installed costs'],
        foundation_buffer_bays=cfg['foundation_buffer_bays'],buffer_validated=False,
        finance_recalculated=True,baseline_finance_replaced=False,complete_delivery_budget=False,actual_quotes=0,
        first_article_accepted=False,construction_release=False,references=cfg['references'])


def markdown(r):
    sensitivity=r['bearing_index_sensitivity'];candidate=r['actual_corridor_candidate']
    lines=['# Baghdad manufactured-viaduct comparison','',
        '**Status: controlled planning package; no construction design, quotations or selected corridor.**','',
        'Compare Pi20, Pi25 and constrained-access OSR-US for the same complete double-track scope. '
        'Supplier bids must include fabrication, transport, erection, temporary works, foundations, '
        'traffic management, connections, track/egress, checking and maintenance. No 30 m product is introduced.','',
        f"The investigation candidate is {candidate['line']} chainage {candidate['from_station_m']:.1f}–{candidate['to_station_m']:.1f} m "
        f"({candidate['length_m']:.1f} m), the longest current Pi25 run. It is not a surveyed or selected alignment. "
        'The separate 1,000 m comparison below includes both end supports; support ground zones and deep-element lengths are unknown.','',
        '| Package | Bays | Supports | Bearings | Beam/segment lifts | Bare member kg | Installed USD/double-track m |',
        '|---|---:|---:|---:|---:|---:|---|']
    for p in r['packages']:
        g=p['geometry'];lines.append(f"| {p['id']} | {g['spans']} | {g['support_locations']} | {g['bearings']} | "
            f"{p.get('beam_lifts',p.get('segment_lifts'))} | {p['bare_member_mass_kg']} | Unpriced |")
    lines+=['','Pi25 has only 62.5 kg bare margin beneath 75 t; Pi20 has 50 kg beneath its 60 t product target. '
        'Complete member and hook masses remain unknown. Segmental concrete and support/bearing geometry '
        'require their own supplier design; Pi quantities are not transferred. '
        f"The current OSR-US coordination envelope is {r['packages'][-1]['transport_width_m']:.2f} m wide, exceeding the primary 3 m shipping target. "
        'Shorter/lighter segments do not solve a width restriction without redesign or a reviewed oversize route.','',
        '## Connections and quantities','',
        'A link slab can remove an expansion joint while simply supported girders retain their bearings. '
        'The shared-bearing scheme needs a structural connection and checked staged load path. '
        'A finite 40-span Pi25 corridor has 320 simple-span bearings versus 200 in the structural alternative. '
        'The periodic planning index also uses 320 versus 200, but its ten expansion gaps differ from the nine gaps between finite units. Both schemes need '
        'CWR/thermal/braking/seismic/foundation interaction, fatigue, replacement access and connection prices.','',
        f"Under the existing index only, restoring simple-span bearings changes USD {sensitivity['current_conditional_rate_usd_per_km']/1e6:.3f}m/km "
        f"to USD {sensitivity['simple_span_link_slab_rate_usd_per_km']/1e6:.3f}m/km: "
        f"USD {sensitivity['direct_network_delta_usd']/1e6:.3f}m as a uniform-rate illustration over all current elevation. "
        'This is an unadopted counterfactual before connection/end-effect/EPC costs, not a priced scope or a transfer of Pi bearings to segmental/special designs.','',
        f"The [financed bearing sensitivity](../delivery-closure/finance-simple_span_bearing_index.json) applies only to {sensitivity['financed_pi25_only_length_m']/1000:.3f} km of existing standard Pi25: "
        f"USD {sensitivity['financed_pi25_only_direct_delta_usd']/1e6:.3f}m direct plus the existing incremental EPC rate once. "
        f"Its capital is USD {r['bearing_sensitivity_finance_metrics']['total_capital_usd']/1e9:.3f}bn and terminal gap debt IQD {r['bearing_sensitivity_finance_metrics']['terminal_supplemental_balance_iqd']/1e12:.3f}tn. "
        'Monthly/six-month cash, debt/reserves/early repayment are recalculated under unchanged government and currency rules. '
        'Original civil invoice timing and origin shares are inherited assumptions, not supplier evidence; all consequential costs remain open.','',
        '## Alignment and budget boundary','',
        f"The register covers all {len(r['alignment_segments'])} elevated segments, including {r['special_segment_count']} individual special reviews. "
        f"It separates USD {r['standard_rate_allowance_usd']/1e9:.3f}bn standard-rate allowance from "
        f"USD {r['routing_penalty_usd']/1e9:.3f}bn monetary routing penalty. "
        'Search deterrents are excluded from monetary allowances. This base allowance is not a complete installed price or an achieved saving; special/segmental increments remain unknown. Each special segment has '
        'wider-curve, station-move, right-of-way, segmental, land/utility, traffic and whole-life comparison fields. '
        'No alternative is accepted and original capital/debt figures are preserved.','',
        'The individual special reviews are ranked by existing penalty exposure to direct investigation effort, '
        'not by achieved savings. Approximate radius is recovered from the rounded routing multiplier; '
        'it is not a fitted/surveyed radius. The Pi20 chord screen shows where shortening alone still fails '
        'the existing catalogue allowance. Nearby station IDs support bounded station/right-of-way studies.','',
        '| Special priority | Line/chainage m | Length m | Routing penalty USD m | Radius proxy m | Pi20 chord screen |',
        '|---|---|---:|---:|---:|---|',
        *[f"| {row['special_priority_rank']} | {row['line']} {row['from_station_m']:.1f}–{row['to_station_m']:.1f} | {row['length_m']:.1f} | {row['routing_penalty_usd']/1e6:.3f} | {row['radius_proxy_from_routing_multiplier_m']:.1f} | {row['pi20_chord_screen_passed']} |"
          for row in sorted((row for row in r['alignment_segments'] if row['special_priority_rank']),key=lambda row:row['special_priority_rank'])[:10]],'',
        f"A further 20% reduction in beam concrete changes the existing index by only USD {r['beam_concrete_20pct_reduction_index_delta_usd_per_km']/1e6:.3f}m/km "
        'before any offsetting prestress, reinforcement or fabrication changes. No literature percentage is applied again.','',
        '## Production, procurement and first article','',
        '[comparison.json](comparison.json) contains per-support foundation records, five complete-package quantity/rate forms, '
        'equipment-release fields, all eight production fronts and first-article hold points. '
        '[installed-cost-rfq.csv](installed-cost-rfq.csv) retains invoice currency, origin, quote date and exclusions. '
        'Unknown costs remain null, not zero; partial totals cannot produce an installed price. IQD quotes stay IQD, '
        'with historical FX used only for reporting. Loan eligibility requires actual invoices and lender terms.','',
        'Measure casting, strength release, column/cap connections, transport, erection, closure curing, '
        'survey/tolerance correction, track/egress and acceptance in crew-hours per complete double-track bay. '
        'The rate is the slowest front, not the beam lift count. Parallel moulds and fronts, shifts, closures, '
        '10–15-bay foundation/accepted-stock buffers and deck-supply loads require a resource-loaded programme and trials. '
        'The existing 48-hour casting planning cycle remains until the 24-hour target is physically qualified.','',
        'Issue competing ground-crane/portal and overhead-launcher bids for the same route. Include configured '
        'charts, pads/ground improvement, mobilisation, closures, launch/deck reactions and recovery. '
        'Use conventional prestressed concrete first; compare UHPC connections and special steel/composite '
        'crossings where measured whole-life resources justify them. Carbon percentages are not cost savings.','',
        'Build and measure the first beam and representative pier/cap/connection only after design release. '
        'Record accepted complete bays/week, labour, rejected/reworked pieces and installed cost. '
        'Supplier bids, boreholes, utilities, demand counts, actual production trials, signed checks and funding remain external work.','',
        '## Review scope and evidence','',
        f"The older review of `135e249e` predates the integrated USD {r['existing_integrated_finance_metrics']['total_capital_usd']/1e9:.3f}bn full-fleet sensitivity and its "
        f"IQD {r['existing_integrated_finance_metrics']['terminal_supplemental_balance_iqd']/1e12:.3f}tn terminal gap debt. Depot/workforce/site-energy reconciliation, supplier RFQ forms, "
        'opening-fleet replay, rental alternatives and clean-checkout bootstrap already exist in '
        '[delivery closure](../delivery-closure/README.md). This package closes repository comparison gaps; '
        'it does not replace supplier offers, measured demand or a complete delivery budget.','']
    for reference in r['references']:lines.append(f"- [{reference['title']}]({reference['url']}): {reference['use']} (checked {reference['checked']}).")
    return '\n'.join(lines)+'\n'


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--check',action='store_true');args=parser.parse_args()
    if args.check:
        summary=json.loads((OUT/'summary.json').read_text())
        for base,key in ((ROOT,'sources_sha256'),(OUT,'outputs_sha256')):
            for path,digest in summary[key].items():
                if sha(base/path)!=digest:raise ValueError('Stale viaduct comparison: '+path)
        print('Viaduct comparison source/output hashes pass');return
    result=build();OUT.mkdir(parents=True,exist_ok=True)
    (OUT/'comparison.json').write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+'\n')
    (OUT/'README.md').write_text(markdown(result))
    rows=[dict(package=p['id'],**r) for p in result['packages'] for r in p['cost_items']]
    fields=list(dict.fromkeys(k for row in rows for k in row))
    with (OUT/'installed-cost-rfq.csv').open('w',newline='') as stream:
        writer=csv.DictWriter(stream,fieldnames=fields,lineterminator='\n');writer.writeheader();writer.writerows(rows)
    with (OUT/'alignment-review.csv').open('w',newline='') as stream:
        writer=csv.DictWriter(stream,fieldnames=list(result['alignment_segments'][0]),lineterminator='\n')
        writer.writeheader();writer.writerows(result['alignment_segments'])
    sources=[Path(__file__),CONFIG,CITY/'design.toml',ROOT/'lib/templates/rolling-stock.toml',
        ROOT/'lib/templates/iraq-funding.toml',ROOT/'lib/templates/civil-cost-model.toml',
        ROOT/'docs/civil/viaduct-load-model.toml',ROOT/'design/component-catalogue/src/osr_mech/civil/decked_pi.py',
        ROOT/'design/component-catalogue/src/osr_mech/civil/continuity.py',
        ROOT/'design/component-catalogue/src/osr_mech/civil/ugirder.py',
        ROOT/'design/component-catalogue/src/osr_mech/civil/viaduct.py',ROOT/'crates/osr-routing/src/civil.rs',
        CITY/'engineering/delivery-closure/finance-reconciled_full_fleet.json']
    sources.append(CITY/'engineering/delivery-closure/finance-simple_span_bearing_index.json')
    summary=dict(schema=result['schema'],sources_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in sources},
        outputs_sha256={name:sha(OUT/name) for name in ('comparison.json','README.md','installed-cost-rfq.csv','alignment-review.csv')},
        complete_delivery_budget=False,construction_release=False,actual_quotes=0)
    (OUT/'summary.json').write_text(json.dumps(summary,indent=2,sort_keys=True)+'\n')
    print('Prepared five viaduct packages, finite supports, installed-cost forms and all elevated alignment reviews')


if __name__=='__main__':main()
