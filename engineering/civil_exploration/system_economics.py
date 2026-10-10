"""Complete method-specific bill, synthetic scenarios and unknown actual costs."""
from __future__ import annotations
from copy import deepcopy
import math
from osr_mech.civil.exploration import foundation_geometry

from . import commercial
from .contracts import ROOT,HERE,sha,load
from .model import takeoff


def bill(candidate,study,construction):
    rows=commercial.bill(candidate,study)
    rows['beam_transport']['quantity']=construction['total_lifts']
    rows['crane_and_erection']['quantity']=construction['total_lifts']
    rows['crane_mobilisation']=dict(quantity=1.,unit='package')
    rows['site_overhead']=dict(quantity=1.,unit='package')
    q=takeoff(candidate,study);f=candidate['foundation'];fg=foundation_geometry(f)
    site_concrete=fg['cap_concrete_m3']*q['supports']
    if f['installation_method']!='driven':site_concrete+=fg['pile_concrete_m3']*q['supports']
    if construction['pier_method'] in ('cast-in-place','shell-infill'):site_concrete+=q['pier_concrete_m3']
    if construction['cap_method']=='cast-in-place':site_concrete+=q['cap_concrete_m3']
    if construction['beam_method'] in ('in-situ','shell-infill'):site_concrete+=q['deck_concrete_m3']
    rows['site_concrete_delivery']=dict(quantity=site_concrete,unit='m3')
    rows['precast_pile_transport']=dict(quantity=construction['pile_delivery_units'],unit='unit')
    rows['pile_splice_connections']=dict(quantity=max(0,construction['pile_delivery_units']-q['pile_count']),unit='ea')
    if candidate['foundation'].get('type')=='spread':
        f=candidate['foundation'];q=takeoff(candidate,study)
        rows['spread_excavation']=dict(quantity=f['cap_length_m']*f['cap_width_m']*(f['cap_depth_m']+.75)*q['supports'],unit='m3')
    return rows


def validate_scenario(scenario):
    # The shipped scenarios are controlled assumptions, not a quote importer.
    required={'id','basis','classification','price_date','location','deck_material_usd_m3','support_material_usd_m3','foundation_concrete_usd_m3',
              'uhpc_usd_m3','frp_usd_m3','structural_steel_usd_m3','reinforcement_usd_kg','prestress_usd_kg','inserts_usd_kg','bearings_joints_usd_each',
              'pile_plant_usd_m','spread_excavation_usd_m3','transport_distance_km','transport_dispatch_usd','transport_usd_t_km','crane_tiers',
              'track_interfaces_usd_track_m','temporary_works_usd','site_formwork_usd_m3','segmental_temporary_usd','shell_temporary_usd',
              'crew_usd_working_day','production_bed_usd_day','curing_yard_usd_day','qa_usd_day','tooling_usd','reinstatement_usd','site_overhead_usd_day',
              'maintenance_fraction_per_year','life_years','discount_rate','productivity','bearing_joint_replacement_years','cfrp_rate_multiplier','site_concrete_delivery_usd_m3','pile_splice_usd_each'}
    if set(scenario)!=required or scenario.get('classification')!='assumption' or not scenario.get('basis') or not scenario.get('id'):
        raise ValueError('comparative scenario must declare its assumption basis')
    for key,value in scenario.items():
        if type(value) is bool or (type(value) in (int,float) and (not math.isfinite(value) or value<0)):
            raise ValueError('negative/nonfinite scenario input: '+key)
    for mapping in ('deck_material_usd_m3','support_material_usd_m3','pile_plant_usd_m'):
        for value in scenario[mapping].values():commercial.number(value)
    tiers=scenario['crane_tiers']
    if not tiers or [r['max_mass_kg'] for r in tiers]!=sorted(set(r['max_mass_kg'] for r in tiers)):
        raise ValueError('crane scenario tiers must increase')
    for tier in tiers:
        if set(tier)!={'max_mass_kg','usd_lift','mobilisation_usd'}:raise ValueError('synthetic equipment tier scope invalid')
        for value in tier.values():commercial.number(value)


def scenario_price(candidate,study,choice,construction,schedule,scenario,source):
    validate_scenario(scenario);rows=bill(candidate,study,construction)
    q=takeoff(candidate,study);occ=schedule['resource_working_days'];c=construction
    masses=[u['transport_mass_kg']*q['beam_lifts'] for u in c['per_beam_units']]
    masses += [u['transport_mass_kg']*q['supports'] for u in c['per_pier_units']]
    masses += [c['cap_transport_mass_kg']*c['cap_units']]
    average=sum(masses)/max(1,c['total_lifts'])
    tier=next((r for r in scenario['crane_tiers'] if r['max_mass_kg']>=c['maximum_lift_mass_kg']),None)
    if tier is None:raise ValueError('lift exceeds bounded hypothetical equipment tiers')
    temporary=scenario['temporary_works_usd']
    if c['beam_method']=='in-situ':temporary+=q['deck_concrete_m3']*scenario['site_formwork_usd_m3']
    if c['beam_method']=='segmental':temporary+=scenario['segmental_temporary_usd']
    if c['beam_method']=='shell-infill' or c['pier_method']=='shell-infill':temporary+=scenario['shell_temporary_usd']
    values=dict(deck_concrete=scenario['deck_material_usd_m3'][choice['material']],
                pier_cap_concrete=scenario['support_material_usd_m3'][choice['support_material']],
                foundation_concrete=scenario['foundation_concrete_usd_m3'],reinforcement=scenario['reinforcement_usd_kg'],
                prestressing=scenario['prestress_usd_kg'],inserts=scenario['inserts_usd_kg'],bearings_and_joints=scenario['bearings_joints_usd_each'],
                pile_installation=scenario['pile_plant_usd_m'][candidate['foundation']['installation_method']],
                beam_transport=scenario['transport_dispatch_usd']+average/1000*scenario['transport_distance_km']*scenario['transport_usd_t_km'],
                crane_and_erection=tier['usd_lift'],crane_mobilisation=tier['mobilisation_usd'] if c['total_lifts'] else 0.,
                track_walkways_drainage_utilities=scenario['track_interfaces_usd_track_m'],temporary_works=temporary,
                labour=(sum(v for k,v in occ.items() if k not in ('curing-yard','procurement-wait'))+schedule['programme_working_days']*.25)*scenario['crew_usd_working_day'],
                production_beds_curing=(occ['precast-bed']+occ['cap-bed']+occ['pile-bed'])*scenario['production_bed_usd_day']+occ['curing-yard']*scenario['curing_yard_usd_day'],
                tooling_qa_testing=scenario['tooling_usd']+occ['qa']*scenario['qa_usd_day'],site_reinstatement=scenario['reinstatement_usd'],
                site_overhead=schedule['programme_working_days']*scenario['site_overhead_usd_day'],
                frp_material_and_fabrication=scenario['frp_usd_m3']*(scenario['cfrp_rate_multiplier'] if choice.get('fibre_material')=='cfrp' else 1.),uhpc_material_and_curing=scenario['uhpc_usd_m3'],
                structural_steel_material_and_fabrication=scenario['structural_steel_usd_m3'],spread_excavation=scenario['spread_excavation_usd_m3'],
                site_concrete_delivery=scenario['site_concrete_delivery_usd_m3'],
                pile_splice_connections=scenario['pile_splice_usd_each'],
                precast_pile_transport=scenario['transport_dispatch_usd']+sum(u['transport_mass_kg'] for u in c['per_support_pile_units'])/max(1,len(c['per_support_pile_units']))/1000*scenario['transport_distance_km']*scenario['transport_usd_t_km'])
    inputs=dict(schema='osr-civil-commercial/1',price_date=scenario['price_date'],location=scenario['location'],
                fx_to_usd={'USD':1.},fx_basis='USD identity; synthetic comparative rates',rates={},
                life_years=scenario['life_years'],real_discount_rate=scenario['discount_rate'],maintenance_annual=0.,replacement_events=[],
                equipment=deepcopy(load(HERE/'config/commercial.json')['equipment']))
    for key,quantity in rows.items():
        inputs['rates'][key]=dict(unit=quantity['unit'],rate=values[key],currency='USD',source=source.relative_to(ROOT).as_posix(),
                                  source_sha256=sha(source),classification='assumption',expiry_date=None)
    result=commercial.price(candidate,study,inputs,quantities=rows)
    inputs['maintenance_annual']=result['installed_cost_usd']*scenario['maintenance_fraction_per_year']
    replacement=next(r['cost_usd'] for r in result['rows'] if r['item']=='bearings_and_joints')
    inputs['replacement_events']=[dict(year=year,cost_usd=replacement,basis='Synthetic bearing/joint replacement interval, no supplier life adopted') for year in scenario['bearing_joint_replacement_years']]
    result=commercial.price(candidate,study,inputs,quantities=rows)
    result.update(scenario_id=scenario['id'],scenario_basis=scenario['basis'],actual_baghdad_price=False,
                  maximum_actual_lift_mass_kg=c['maximum_lift_mass_kg'],
                  hypothetical_crane_tier=tier,hypothetical_tier_is_not_a_crane_chart=True,
                  scope_notes=['material lines include material/fabrication only; bed/curing occupancy separately costed',
                               'pile installation rate is plant only; materials, precast production/delivery/splices and crew wages are separate',
                               'crane rate is plant; crew wages and mobilisation separate','track interfaces include materials; labour separately scheduled',
                               'reinforcement/tendons are quantity allowances, not released detailing'],
                  maintenance_basis='unmeasured annual fraction plus declared bearing/joint replacement years; no service-life evidence adopted')
    return result


def actual_price(candidate,study,construction,inputs):
    inputs=deepcopy(inputs);rows=bill(candidate,study,construction)
    if set(inputs['rates'])-(set(rows)|{'frp_material_and_fabrication','uhpc_material_and_curing','structural_steel_material_and_fabrication','spread_excavation'}):
        raise ValueError('unknown actual-price scope')
    inputs['rates']={k:v for k,v in inputs['rates'].items() if k in rows}
    result=commercial.price(candidate,study,inputs,quantities=rows)
    result['actual_baghdad_price']='baghdad' in inputs['location'].lower() and not result['unpriced_scope'] and all(r['rate_record'] and r['rate_record']['classification']=='supplier-quote' for r in result['rows'] if r['quantity'])
    return result
