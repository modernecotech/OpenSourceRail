"""Size a city's physical production flow to its infrastructure programme.

Cells are calculated from actual fleet demand and a simulated finite-resource
flow, not an arbitrary multiplier on a generic resource pool. Physical inputs
and costs remain explicit engineering allowances requiring qualification/RFQs.
"""
from __future__ import annotations

from collections import defaultdict
from copy import deepcopy
import math

from project_twin import apply_resource_cpm


def _positive(value, name):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value <= 0:
        raise ValueError('invalid positive factory input: '+name)
    return value


def size_factory(tasks: list[dict], capacities: dict, config: dict) -> dict:
    """Modify rolling-stock tasks and return a physical, auditable sizing plan."""
    f = config['factory']; stages = config['stage']
    for key, value in f.items():
        if key not in ('city', 'family'):
            _positive(value, key)
    if f['productive_availability'] > 1:
        raise ValueError('productive availability cannot exceed one')
    for key in ('ready_months_from_ntp', 'working_days_per_year', 'shift_hours', 'shifts_per_day',
                'first_article_additional_working_days', 'test_tracks'):
        if int(f[key]) != f[key]:
            raise ValueError('factory count/day must be a whole number: '+key)
    if sum(p['days'] for p in config['construction_phase']) != f['ready_months_from_ntp']*f['working_days_per_year']/12:
        raise ValueError('factory construction phases do not reconcile to readiness')
    for phase in config['construction_phase']:
        if type(phase['days']) is not int or phase['days'] <= 0:
            raise ValueError('invalid factory construction phase')
    stage_by_id = {s['package']:s for s in stages}
    if len(stage_by_id) != len(stages) or len({s['work_center'] for s in stages}) != len(stages):
        raise ValueError('duplicate factory stage or work centre')
    for s in stages:
        for key in ('cycle_working_days', 'crew_per_cell', 'tooling_allowance_usd_per_cell'):
            _positive(s[key], key)
        if any(type(s[k]) is not int for k in ('cycle_working_days', 'crew_per_cell')):
            raise ValueError('stage cycles and crews must be whole counts')
        _positive(s.get('floor_m2_per_cell', f['trainset_bay_length_m']*f['trainset_bay_width_m']), 'stage floor')
    rs = [r for r in tasks if r['asset_type']=='rolling-stock']
    for row in tasks:
        row['dispatch_priority']=0
    if not rs or {r['package_id'] for r in rs} != set(stage_by_id):
        raise ValueError('factory stages must cover the complete trainset flow')
    if any(r.get('product_family') != f['family'] for r in rs):
        raise ValueError('factory cycle assumptions cannot serve a different train family')
    # Remove stock only; infrastructure resources, quantities and dependencies
    # are retained exactly. Missing stock predecessors on infrastructure fail.
    infra = deepcopy([r for r in tasks if r['asset_type']!='rolling-stock'])
    infra_ids = {r['manufacturing_uid'] for r in infra}
    if any(p.strip() not in infra_ids for r in infra for p in r.get('predecessor_uids','').split(';') if p.strip()):
        raise ValueError('infrastructure has a stock dependency; separate deadline invalid')
    apply_resource_cpm(infra, capacities)
    deadlines = defaultdict(int)
    shared = max((r['planned_finish_day'] for r in infra if not r.get('line') or r['asset_type']=='depot'),default=0)
    for r in infra:
        if r.get('line'):
            deadlines[r['line']] = max(deadlines[r['line']],r['planned_finish_day'],shared)
    target = max(deadlines.values())
    ready = int(f['ready_months_from_ntp']*f['working_days_per_year']/12)
    cycles = {s['package']:math.ceil(s['cycle_working_days']/f['productive_availability']) for s in stages}
    lead = sum(cycles.values())
    serial_ready = ready+lead+f['first_article_additional_working_days']
    fleets = defaultdict(set)
    for r in rs:
        fleets[r['line']].add(r['asset_id'])
    if set(fleets) != set(deadlines):
        raise ValueError('factory and infrastructure line scopes differ')
    count = sum(len(v) for v in fleets.values())
    window = target+1-serial_ready-lead
    if window <= 0:
        raise ValueError('18-month factory cannot precede infrastructure target with qualification and production lead time')
    order = sorted(deadlines,key=lambda line:(deadlines[line],line))
    first_asset = sorted(fleets[order[0]])[0]
    prototype_uid = next(r['manufacturing_uid'] for r in rs if r['asset_id']==first_asset and r['package_id']==stages[-1]['package'])
    for r in rs:
        s=stage_by_id[r['package_id']]
        r['work_center']=s['work_center']; r['duration_days']=cycles[r['package_id']]
        r['duration_model']='whole-six-car-cell-cycle-with-availability'
        r['quantity_basis']=f"{s['cycle_working_days']} productive working days / {f['productive_availability']:.0%} availability, rounded up; one complete six-car trainset"
        r['work_order_title']=s['work_center']+' work package'
        r['work_order_detail']='Whole six-car planning occupation; family-specific drawings, mould count, labour routing and measured first-article times required before manufacturing release.'
        r['deliverables']='One six-car trainset stage accepted against the released family-specific ITP'
        r['materials_or_inputs']='Released six-car family kit and traveller; LM3 module counts are not applied'
        if r['manufacturing_uid']==prototype_uid:
            r['duration_days']+=f['first_article_additional_working_days']
            r['quantity_basis']+='; plus 60-working-day first-article qualification allowance'
            r['evidence_required']+='; first-article type/integration/charging/braking/fire/environmental evidence and independent series-release signoff'
        if r['package_id']==stages[0]['package'] and r['asset_id']!=first_asset:
            r['predecessor_uids']='; '.join(filter(None,[r.get('predecessor_uids',''),prototype_uid]))
        r['dispatch_priority']=order.index(r['line'])
    # Equal-delay cells maintain genuine concurrency; bays are not test tracks.
    resource_ready={s['work_center']:ready for s in stages}
    rate=(count-1)/window
    result=None
    for _ in range(500):
        cells={s['work_center']:max(1,math.ceil(rate*cycles[s['package']])) for s in stages}
        trial=deepcopy(rs)
        # Physical asset IDs and UIDs stay unchanged. Baseline-freeze is an
        # external, completed prerequisite by the 18-month factory readiness.
        apply_resource_cpm(trial,{**capacities,**cells},resource_ready)
        finish=max(r['planned_finish_day'] for r in trial)
        if finish <= target:
            result=trial;break
        rate+=f['capacity_search_step_trainsets_per_day']
    if result is None:
        raise ValueError('no factory sizing solution within search limit')
    bottleneck=min(cells[s['work_center']]/cycles[s['package']] for s in stages)
    track_capacity=f['test_tracks']*f['shift_hours']*f['shifts_per_day']*f['productive_availability']/f['exclusive_track_hours_per_trainset']
    if track_capacity < bottleneck:
        raise ValueError('acceptance bays exceed independently segregated test-track path capacity')
    # Tell the common scheduler the approved planning priority explicitly.
    physical=[]
    for s in stages:
        n=cells[s['work_center']]
        physical.append(dict(**s,planned_occupation_days=cycles[s['package']],cells=n,
            trainsets_per_year=n/cycles[s['package']]*f['working_days_per_year'],
            direct_crew_fte=n*s['crew_per_cell']*f['shifts_per_day'],
            process_floor_m2=n*s.get('floor_m2_per_cell',f['trainset_bay_length_m']*f['trainset_bay_width_m']),
            tooling_allowance_usd=n*s['tooling_allowance_usd_per_cell']))
    floor=sum(s['process_floor_m2'] for s in physical)*(1+f['support_floor_fraction'])
    track_land=f['test_tracks']*f['test_track_length_m']*f['test_track_land_width_m']
    land=floor*f['site_floor_multiplier']+track_land
    c=config['cost_envelope']
    for k,v in c.items(): _positive(v,k)
    costs=dict(buildings=floor*c['building_allowance_usd_m2'],
               serviced_site=land*c['serviced_site_allowance_usd_m2'],
               stage_tooling=sum(s['tooling_allowance_usd'] for s in physical),
               test_tracks=f['test_tracks']*f['test_track_length_m']/1000*c['test_track_allowance_usd_km'],
               shared_utilities_stores_labs_logistics=c['shared_utilities_stores_labs_logistics_usd'],
               design_training_qualification=c['design_training_qualification_usd'])
    costs['contingency']=sum(costs.values())*c['contingency_fraction']
    finishes={line:max(r['planned_finish_day'] for r in result if r['line']==line) for line in order}
    return dict(city=f['city'],family=f['family'],engineering_release=False,
        factory_ready_working_day=ready,readiness_months_from_ntp=f['ready_months_from_ntp'],
        total_trainsets=count,vehicle_modules=count*6,
        infrastructure_deadlines=dict(deadlines),infrastructure_target_working_day=target,
        serial_release_working_day=serial_ready,stock_finish_working_day=max(finishes.values()),
        line_stock_finish_working_day=finishes,line_priority=order,
        lines_civil_complete_before_factory_ready=[line for line in order if deadlines[line]<ready],
        resource_capacity=cells,resource_ready_days=resource_ready,stages=physical,
        minimum_steady_output_trainsets_per_year=bottleneck*f['working_days_per_year'],
        exclusive_test_path_capacity_trainsets_per_year=track_capacity*f['working_days_per_year'],
        process_and_support_floor_m2=floor,planning_site_m2=land,
        direct_production_crew_fte=sum(s['direct_crew_fte'] for s in physical),
        cost_allowances_usd=costs,plant_cost_envelope_usd=sum(costs.values()),
        cost_basis='Unquoted engineering allowance; production labour/materials already within train CAPEX. Plant EPC compared separately. Not a supplier offer or a released factory design.',
        construction_phases=config['construction_phase'],
        limitations=['Overall full-fleet delivery matches infrastructure target, not every early line civil date.',
          'First-article, production cycles, availability, test-track duty and cell layout require measured qualification.',
          'Infra dates retain the existing conditional resource model; civil buildability, risk and calendar approval remain open.',
          'Supplier qualification, order lead times, imports/customs and funding must support the derived manufacturing rate.',
          'No future national city consumes Baghdad capacity; expansion requires a new factory loading assessment.'])
