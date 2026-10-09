"""Equal-scope commercial and equipment comparisons with unknowns preserved."""
from __future__ import annotations
import datetime as dt
import math
from .model import takeoff
from .contracts import ROOT,sha


def source_binding(source,digest):
    from pathlib import Path
    p=Path(source)
    path=(ROOT/p).resolve()
    if p.is_absolute() or '..' in p.parts or not path.is_relative_to(ROOT) or not path.is_file() or sha(path)!=digest:
        raise ValueError('quotation/chart source missing, stale or uncontrolled')


def bill(candidate,study):
    q=takeoff(candidate,study)
    rows={
        'deck_concrete':dict(quantity=q['deck_concrete_m3'],unit='m3'),
        'pier_cap_concrete':dict(quantity=q['pier_concrete_m3']+q['cap_concrete_m3'],unit='m3'),
        'foundation_concrete':dict(quantity=q['foundation_concrete_m3'],unit='m3'),
        'reinforcement':dict(quantity=q['reinforcement_allowance_kg'],unit='kg'),
        'prestressing':dict(quantity=q['prestress_allowance_kg'],unit='kg'),
        'inserts':dict(quantity=q['embedded_allowance_kg'],unit='kg'),
        'bearings_and_joints':dict(quantity=q['bearing_count'],unit='ea'),
        'pile_installation':dict(quantity=q['pile_length_m'],unit='m'),
        'beam_transport':dict(quantity=q['beam_lifts'],unit='lift'),
        'crane_and_erection':dict(quantity=q['beam_lifts'],unit='lift'),
        'track_walkways_drainage_utilities':dict(quantity=study['route_length_m']*2,unit='track-m'),
        'temporary_works':dict(quantity=1.,unit='package'),
        'labour':dict(quantity=1.,unit='package'),
        'production_beds_curing':dict(quantity=1.,unit='package'),
        'tooling_qa_testing':dict(quantity=1.,unit='package'),
        'site_reinstatement':dict(quantity=1.,unit='package'),
    }
    volumes=q['deck_material_volumes_m3']
    if volumes.get('frp'):
        rows['frp_material_and_fabrication']=dict(quantity=volumes['frp'],unit='m3')
    if volumes.get('uhpc'):
        # UHPC receives its own rate rather than an ordinary-concrete rate.
        rows['deck_concrete']['quantity']-=volumes['uhpc']
        rows['uhpc_material_and_curing']=dict(quantity=volumes['uhpc'],unit='m3')
    return rows


def number(v,lo=0.):
    if type(v) not in (int,float) or not math.isfinite(v) or v<lo:
        raise ValueError('commercial value must be finite and nonnegative')
    return v


def equipment(candidate,study,proposal):
    q=takeoff(candidate,study)
    required={'radius_m','boom_length_m','dynamic_factor','transport_payload_kg','transport_length_m','charts','basis'}
    if set(proposal)!=required or not proposal['basis']:raise ValueError('equipment proposal coverage/basis incomplete')
    radius=number(proposal['radius_m']);boom=number(proposal['boom_length_m']);factor=number(proposal['dynamic_factor'],1.)
    demand=q['suspended_mass_kg']*factor
    candidates=[]
    for chart in proposal['charts']:
        if set(chart)!={'id','source','source_sha256','available','rows'} or not chart['source'] or len(chart['source_sha256'])!=64:
            raise ValueError('crane chart source binding incomplete')
        source_binding(chart['source'],chart['source_sha256'])
        if type(chart['available']) is not bool:raise ValueError('availability must be a boolean')
        for row in chart['rows']:
            if set(row)!={'boom_length_m','radius_m','capacity_kg'}:raise ValueError('crane chart row units/coverage invalid')
            for value in row.values():number(value)
        if not chart['available']:continue
        eligible=[r for r in chart['rows'] if r['boom_length_m']==boom and r['radius_m']>=radius]
        if not eligible:continue
        row=min(eligible,key=lambda r:r['radius_m'])
        capacity=number(row['capacity_kg'])
        if capacity>=demand:candidates.append(dict(id=chart['id'],capacity_kg=capacity,demand_kg=demand,source=chart['source']))
    selected=min(candidates,key=lambda r:r['capacity_kg']) if candidates else None
    payload=proposal['transport_payload_kg'];length=proposal['transport_length_m']
    transport=None if payload is None or length is None else (number(payload)>=q['transported_beam_mass_kg'] and number(length)>=candidate['definition']['deck']['span_m'])
    return dict(lift_demand_kg=demand,configured_crane=selected,transport_envelope_passed=transport,
                lift_screen='unresolved' if not proposal['charts'] else ('passed' if selected else 'failed'),
                construction_release=False,gaps=['outrigger/launcher ground bearing','route axle loads/clearances','rigging and lateral stability','supplier availability confirmation'])


def price(candidate,study,inputs):
    required={'schema','price_date','location','fx_to_usd','fx_basis','rates','life_years','real_discount_rate','maintenance_annual','replacement_events','equipment'}
    if set(inputs)!=required or inputs['schema']!='osr-civil-commercial/1' or not inputs['location']:
        raise ValueError('commercial contract scope incomplete')
    dt.date.fromisoformat(inputs['price_date'])
    quantities=bill(candidate,study)
    if set(inputs['rates'])-quantities.keys():raise ValueError('unknown cost scope item')
    rows=[];missing=[]
    for item,quantity in quantities.items():
        rate=inputs['rates'].get(item)
        cost=None
        if rate is not None:
            if set(rate)!={'unit','rate','currency','source','source_sha256','classification','expiry_date'} or rate['unit']!=quantity['unit']:
                raise ValueError('rate quantity/unit/source contract mismatch: '+item)
            if rate['classification'] not in ('supplier-quote','assumption'):raise ValueError('unknown price classification')
            if rate['rate'] is not None:
                number(rate['rate']);fx=inputs['fx_to_usd'].get(rate['currency'])
                if fx is not None:
                    number(fx)
                    if fx<=0:raise ValueError('currency rate must be positive')
                    if not inputs['fx_basis']:raise ValueError('currency conversion basis missing')
                    if rate['classification']=='supplier-quote' and (not rate['source'] or len(rate['source_sha256'])!=64):
                        raise ValueError('supplier quotation must identify its controlled source')
                    if rate['classification']=='supplier-quote':source_binding(rate['source'],rate['source_sha256'])
                    if rate['expiry_date'] and dt.date.fromisoformat(rate['expiry_date'])<dt.date.fromisoformat(inputs['price_date']):
                        raise ValueError('expired supplier rate')
                    cost=quantity['quantity']*rate['rate']*fx
        if cost is None:missing.append(item)
        rows.append(dict(item=item,**quantity,rate_record=rate,cost_usd=cost))
    installed=None if missing else math.fsum(r['cost_usd'] for r in rows)
    life=inputs['life_years'];discount=number(inputs['real_discount_rate'])
    if type(life) is not int or not 1<=life<=200 or discount>1:raise ValueError('invalid lifecycle scenario')
    maintenance=inputs['maintenance_annual'];whole=None
    if installed is not None and maintenance is not None:
        number(maintenance)
        whole=installed+sum(maintenance/(1+discount)**year for year in range(1,life+1))
        for event in inputs['replacement_events']:
            if set(event)!={'year','cost_usd','basis'} or not 1<=event['year']<=life or not event['basis']:
                raise ValueError('replacement event requires traceable timing and cost')
            whole+=number(event['cost_usd'])/(1+discount)**event['year']
    return dict(schema='osr-civil-commercial-result/1',candidate_id=candidate['id'],scope='complete double-track package',
                price_date=inputs['price_date'],location=inputs['location'],rows=rows,unpriced_scope=missing,
                installed_cost_usd=installed,whole_life_cost_usd=whole,
                classification='unpriced' if installed is None else 'conditional-priced-scenario',
                equipment=equipment(candidate,study,inputs['equipment']),physical_release=False,
                lifecycle_gaps=[] if whole is not None else ['maintenance/replacement/possession quotations or complete initial costs'])
