"""Resource-constrained provisional precast delivery, procurement and pooled factory.

Elapsed cure and simulated QA milestones never constitute measured strength or
release. Prices, foundation units, lifting chart and production rates are inputs.
"""
from functools import lru_cache
from hashlib import sha256
from pathlib import Path
import argparse
import gzip
import io
import json
import math
import tomllib

from . import configuration, geometry, model

ROOT=model.ROOT
INPUT=Path(__file__).with_name('delivery-schedule.toml')
TEST=ROOT/'engineering/analysis/tests/test_ferrite_maglev_delivery_schedule.py'
OUTPUT=ROOT/'docs/design-engine/ferrite-maglev/delivery-schedule'
SCHEMA='osr-resource-delivery/1'
FLAGS={**model.FLAGS,'engineering_accepted':False,'site_accepted':False,'procurement_released':False}
FILES={'study.json.gz','overview.svg','README.md'}
MAX_RAW=32*1024*1024

def encoded(v):return (json.dumps(v,sort_keys=True,indent=2,allow_nan=False)+'\n').encode()
def digest(p):return sha256(Path(p).read_bytes()).hexdigest()
def source_paths():return sorted({Path(__file__),INPUT,TEST,Path(geometry.__file__),Path(configuration.__file__),Path(model.__file__),*configuration.source_paths()})
def sources():return {p.relative_to(ROOT).as_posix():digest(p) for p in source_paths()}

def load():
    a=tomllib.loads(INPUT.read_text())
    if a['schema']!='osr-resource-delivery-input/1':raise ValueError('delivery input identity differs')
    for k,v in a.items():
        if type(v) in (int,float) and (not math.isfinite(v) or v<=0):raise ValueError('positive finite delivery input required: '+k)
    if a['span_m']!=configuration.selected().civil.span_m or not 1<=a['shift_hours']<=12 or a['curing_hours']<24:raise ValueError('bounded exact span/shift/cure assumptions required')
    if any(type(v) is not int or not 1<=v<=32 for v in a['resources'].values()):raise ValueError('bounded integer resource capacities required')
    if not math.isclose(a['factory_imported_finished_usd']+a['factory_imported_inputs_usd']+a['factory_local_process_usd'],a['shared_factory_capital_usd']):raise ValueError('factory origin/process ledger does not reconcile')
    if len({p['id'] for p in a['procurement']})!=len(a['procurement']):raise ValueError('duplicate procurement identity')
    if any(type(v) not in (int,float) or not math.isfinite(v) or v<=0 for v in a['rates'].values()):raise ValueError('positive finite delivery rates required')
    if any(not math.isfinite(p['lead_days']) or p['lead_days']<=0 or not math.isfinite(p['planning_usd']) or p['planning_usd']<0 for p in a['procurement']):raise ValueError('bounded procurement lead/cost required')
    return a

def work_window(start,hours,*,shift=8.,continuous=False):
    if continuous:return start,start+hours
    day=math.floor(start/24);within=start-day*24
    if within>=shift-1e-10:start=(day+1)*24
    actual=start;remaining=hours
    while remaining>1e-10:
        available=shift-start%24
        if remaining<=available+1e-10:return actual,start+remaining
        remaining-=available;start=(math.floor(start/24)+1)*24
    return actual,start

def schedule(tasks,capacities,*,shift=8.):
    """Deterministic earliest-start list schedule with explicit non-overlap slots."""
    by_id={t['id']:t for t in tasks}
    if len(by_id)!=len(tasks) or any(p not in by_id for t in tasks for p in t['depends']):raise ValueError('task identity/dependency differs')
    # Global earliest-start selection makes scheduled starts monotone. A later
    # ready task cannot fill a time before the last global start; per-slot end
    # times therefore suffice without rescanning every historical interval.
    pools={key:[0.]*value for key,value in capacities.items()};done={};pending=set(by_id)
    def place(task):
        ready=max((done[p]['end_h'] for p in task['depends']),default=0.)
        key=task.get('resource');continuous=task.get('continuous',False)
        if key is None:return (*work_window(ready,task['hours'],shift=shift,continuous=True),None)
        if key not in pools:raise ValueError('missing task resource')
        options=[]
        for unit,free_at in enumerate(pools[key]):
            begin,end=work_window(max(ready,free_at),task['hours'],shift=shift,continuous=continuous);options.append((begin,end,unit))
        return min(options)
    while pending:
        ready=[by_id[k] for k in pending if all(p in done for p in by_id[k]['depends'])]
        if not ready:raise ValueError('cyclic task graph')
        candidates=[(place(t),t) for t in ready];(start,end,unit),task=min(candidates,key=lambda x:(x[0][0],x[1]['id']))
        row=dict(task,start_h=start,end_h=end,resource_unit=unit)
        done[task['id']]=row;pending.remove(task['id'])
        if task.get('resource'):pools[task['resource']][unit]=end
    rows=sorted(done.values(),key=lambda t:(t['start_h'],t['id']));verify_schedule(rows,capacities)
    return rows

def verify_schedule(rows,capacities):
    by_id={r['id']:r for r in rows};calendars={}
    if len(by_id)!=len(rows):raise ValueError('duplicate scheduled task')
    for row in rows:
        if row['end_h']<=row['start_h'] or any(by_id[p]['end_h']>row['start_h']+1e-9 for p in row['depends']):raise ValueError('schedule precedence/time differs')
        if row.get('resource'):
            key=row['resource'];unit=row['resource_unit']
            if type(unit) is not int or not 0<=unit<capacities[key]:raise ValueError('resource capacity exceeded')
            calendars.setdefault((key,unit),[]).append((row['start_h'],row['end_h']))
    for intervals in calendars.values():
        ordered=sorted(intervals)
        if any(a[1]>b[0]+1e-9 for a,b in zip(ordered,ordered[1:])):raise ValueError('overlapping constrained resource')
    return True

def factory_allocation(length_km,a=None):
    a=load() if a is None else a
    if not 0<length_km<=a['programme_factory_length_km']:raise ValueError('factory allocation exceeds programme capacity')
    fraction=length_km/a['programme_factory_length_km'];training=a['training_trainees']*a['training_hours_each']*a['training_local_usd_per_hour']+a['trainer_hours']*a['trainer_usd_per_hour']
    return dict(factory_id='BAGHDAD-SHARED-FACTORY-1',programme_route_km=a['programme_factory_length_km'],pilot_share=fraction,
        one_time_programme_factory_usd=a['shared_factory_capital_usd'],allocated_factory_usd=a['shared_factory_capital_usd']*fraction,
        unallocated_factory_usd=a['shared_factory_capital_usd']*(1-fraction),training_programme_usd=training,allocated_training_usd=training*fraction,
        imported_finished_usd=a['factory_imported_finished_usd']*fraction,imported_inputs_usd=a['factory_imported_inputs_usd']*fraction,local_process_usd=a['factory_local_process_usd']*fraction,
        local_process_spend_fraction=a['factory_local_process_usd']/a['shared_factory_capital_usd'],verified_domestic_value_added_fraction=None,
        origin_certificates_received=False,training_executed=False,allocation_basis='route-km share of a stated100km programme; pool capital is counted once, not once per city')

def quantities(length_m,a=None,*,beam_count=None,support_count=None):
    a=load() if a is None else a
    if not 25<=length_m<=100000:raise ValueError('bounded route length required')
    bays=math.ceil(length_m/a['span_m']);beams=2*bays if beam_count is None else beam_count;supports=bays+1 if support_count is None else support_count
    if any(type(v) is not int or v<=0 for v in (beams,supports)):raise ValueError('positive integer physical beam/support counts required')
    q=geometry.guideway_quantities(a['span_m']);beam_concrete=q['beam_concrete_mass_kg']/2500.;steel=q['magnetic_rail_mass_kg']
    suspended=(beam_concrete*2500+steel)/1000+a['rigging_t'];design=suspended*a['dynamic_lift_factor'];capacity=a['assumed_chart_capacity_t_at_radius']
    rates=a['rates'];rows=[]
    def add(uid,amount,rate,unit,scope):rows.append(dict(id=uid,quantity=amount,unit=unit,unit_rate_usd=rate,cost_usd=amount*rate,scope=scope,quote=False))
    add('beam-concrete',beams*beam_concrete,rates['concrete_usd_m3'],'m3','exact current hollow/end-infill stock; supports additional')
    add('beam-reinforcement',beams*beam_concrete*rates['reinforcement_kg_m3'],rates['steel_usd_kg'],'kg','assumed reinforcement ratio, detailed cage not released')
    add('reaction-faces',beams*steel,rates['reaction_steel_usd_kg'],'kg','actual current segmented steel face quantities')
    add('foundations',supports,rates['foundation_each_usd'],'support','uninvestigated all-in support allowance, not pile design')
    add('columns-caps',supports,rates['column_cap_each_usd'],'support','unqualified repeat support envelope')
    for label,key in [('transport','beam_transport_each_usd'),('erection','beam_erection_each_usd'),('qa','beam_qa_each_usd')]:add(label,beams,rates[key],'beam','unquoted handling/QA planning')
    add('stator',length_m,rates['stator_route_m_usd'],'route-m','mount and site installation only; copper/converters separately priced in pilot')
    add('test',length_m,rates['site_test_route_m_usd'],'route-m','offline/commissioning preparation, independent acceptance additional')
    return dict(requested_route_m=length_m,quantised_route_m=bays*a['span_m'],bays=bays,beams=beams,supports=supports,beam_concrete_m3=beam_concrete,
        maximum_lift_t=design,crane_radius_m=a['crane_radius_m'],assumed_capacity_t_at_radius=capacity,nominal_crane_screen_pass=design<=capacity,
        transport_payload_t=a['transport_payload_t'],nominal_transport_screen_pass=suspended-a['rigging_t']<=a['transport_payload_t'],
        crane_chart_verified=False,ground_mat_accepted=False,rows=rows,priced_scope_usd=sum(r['cost_usd'] for r in rows))

def topology_quantities(line,a=None):
    """Count each mainline leg and each one-direction loop independently.

    Common mainline stop caps and both bearings at each terminal cap are an
    explicit structural hypothesis. Internal loop supports are never paired
    with another loop or another direction to halve their count.
    """
    a=load() if a is None else a;stops=line['operating_plan']['stations'];loops=line['operating_plan']['terminal_loops'];events=[e for e in line['duty']['arrival_events_per_circuit'] if not e['terminal_loop_allowance']][:len(stops)-1]
    if len(events)!=len(stops)-1 or len(loops)!=2 or len({s['id'] for s in stops})!=len(stops) or len({l['id'] for l in loops})!=2:raise ValueError('complete unique open line and both terminal loops required')
    supports={s['id']:dict(id='support/'+s['id'],source_station=s['id'],coordinate=[s['lon'],s['lat']],shared_mainline_cap_hypothesis=True,engineering_accepted=False) for s in stops};beams=[];components=[]
    def segment(uid,length,ends,*,directions,curved=False,loop=None):
        count=math.ceil(length/a['span_m']);ids=[ends[0]]
        for i in range(1,count):
            key=f'{uid}/support-{i:04d}';supports[key]=dict(id='support/'+key,component=uid,chainage_m=i*a['span_m'],curved=curved,engineering_accepted=False);ids.append(key)
        ids.append(ends[1]);first=len(beams)
        for i in range(count):
            span=min(a['span_m'],length-i*a['span_m'])
            for direction in range(directions):
                beams.append(dict(id=f'beam-{len(beams):04d}',component=uid,direction=direction,span_index=i,installed_span_arclength_m=span,priced_stock_length_m=a['span_m'],
                    support_ids=[supports[ids[i]]['id'],supports[ids[i+1]]['id']],curved=curved,closing_unit=span<a['span_m']-1e-9,manufacturing_geometry_qualified=False))
        components.append(dict(id=uid,length_m=length,directions=directions,spans=count,beams=len(beams)-first,unique_internal_supports=count-1,endpoint_support_ids=[supports[e]['id'] for e in ends],curved=curved))
        if loop is not None:
            supports[ends[0]].setdefault('terminal_loop_endpoint_bearings',[]).extend([dict(loop=uid,end=end,coordinate=coord,shared_cap_accepted=False) for end,coord in [('start',loop['geometry']['coordinates'][0]),('end',loop['geometry']['coordinates'][-1])]])
    for i,(first,last,event) in enumerate(zip(stops,stops[1:],events)):segment(f'main-leg-{i:02d}',event['distance_m'],[first['id'],last['id']],directions=2)
    for index,loop in enumerate(loops):
        stop=stops[0 if index==0 else -1];segment(loop['id'],loop['geometry']['length_m'],[stop['id'],stop['id']],directions=1,curved=True,loop=loop)
    physical_length=sum(b['installed_span_arclength_m'] for b in beams);equivalent=physical_length/2
    if not math.isclose(physical_length,2*line['operational_route_length_m']+line['topology']['added_single_direction_loop_beam_m'],abs_tol=.01):raise ValueError('separate route/loop lengths do not reconcile')
    q=quantities(equivalent,a,beam_count=len(beams),support_count=len(supports));q.update(topology_specific=True,bays=None,equivalent_bays=len(beams)/2,quantised_route_m=len(beams)*a['span_m']/2,components=components,beam_units=beams,support_units=list(supports.values()),
        installed_beam_length_m=physical_length,priced_stock_length_m=len(beams)*a['span_m'],closing_stock_surplus_m=len(beams)*a['span_m']-physical_length,
        shared_terminal_cap_count=2,shared_support_acceptance=False,curved_beam_count=sum(b['curved'] for b in beams),closing_beam_count=sum(b['closing_unit'] for b in beams),
        bay_count_role='Equivalent material workload only; physical beams/supports use the explicit graph',
        quantity_scope='Separate legs and one-way loops; shared stop/terminal caps explicitly assumed. All closing/curved units priced as full25m stock; no cutting permission, curved mould/joint qualification, alignment fit or surveyed foundation acceptance is inherited.')
    return q

def construction(length_m=1000.,*,scenario='nominal',a=None,quantity_plan=None):
    a=load() if a is None else a;q=quantities(length_m,a) if quantity_plan is None else quantity_plan;tasks=[]
    if scenario not in {'nominal','rework','import-delay','crane-outage','slow-cure'}:raise ValueError('declared construction scenario required')
    def add(uid,hours,depends=(),resource=None,continuous=False,cost=0.,**extra):tasks.append(dict(id=uid,hours=hours,depends=list(depends),resource=resource,continuous=continuous,cost_usd=cost,**extra))
    add('DESIGN-SITE-PLANNING',24*a['design_and_site_planning_days'],continuous=True,external_acceptance_required=True)
    for p in a['procurement']:
        if p['id'] in {'PROC-VEHICLES','PROC-LIFTS'}:continue
        delay=45 if scenario=='import-delay' and p['id']=='PROC-BATCH' else 0
        add(p['id'],24*(p['lead_days']+delay),continuous=True,quoted=False)
    support_units=q.get('support_units',[dict(id=f'bay-{i:04d}') for i in range(q['supports'])])
    for support in support_units:add(support['id']+'/foundation',a['foundation_hours'],['DESIGN-SITE-PLANNING'],'foundation',cost=a['rates']['foundation_each_usd']+a['rates']['column_cap_each_usd'])
    for unit in range(q['beams']):
        uid=f'beam-{unit:04d}';bay=unit//2;serial=f'PILOT-BEAM-{unit:04d}'
        add(uid+'/batch',a['batch_hours'],['PROC-BATCH'],'batch',serial=serial)
        add(uid+'/cast',a['mould_occupation_hours'],[uid+'/batch','PROC-MOULDS'],'mould',True,serial=serial)
        add(uid+'/cure',a['curing_hours']*(2 if scenario=='slow-cure' else 1),[uid+'/cast'],'curing',True,serial=serial,measured_strength_received=False)
        add(uid+'/qa',a['qa_hours'],[uid+'/cure'],'qa',cost=a['rates']['beam_qa_each_usd'],serial=serial,inspection_executed=False)
        previous=uid+'/qa'
        if scenario=='rework' and unit%10==0:
            add(uid+'/rework',8.,[previous],'mould',cost=1500.,serial=serial)
            add(uid+'/retest',a['qa_hours'],[uid+'/rework'],'qa',cost=250.,serial=serial);previous=uid+'/retest'
        add(uid+'/transport',a['transport_hours'],[previous],'transport',cost=a['rates']['beam_transport_each_usd'],serial=serial)
        ends=q['beam_units'][unit]['support_ids'] if 'beam_units' in q else [f'bay-{bay:04d}',f'bay-{bay+1:04d}']
        deps=[uid+'/transport',*(end+'/foundation' for end in dict.fromkeys(ends)),'PROC-CRANE']
        if scenario=='crane-outage':
            if unit==0:add('CRANE-REPAIR',24*10.,['PROC-CRANE'],continuous=True,cost=15000.)
            deps.append('CRANE-REPAIR')
        add(uid+'/erect',a['erection_hours'],deps,'crane',cost=a['rates']['beam_erection_each_usd'],serial=serial,actual_lift_permit=False)
        add(uid+'/stator',a['stator_hours'],[uid+'/erect','PROC-STATOR'],'stator',serial=serial)
        add(uid+'/test',a['test_hours'],[uid+'/stator'],'test',serial=serial,handback_accepted=False)
    rows=schedule(tasks,a['resources'],shift=a['shift_hours']);end=max(r['end_h'] for r in rows)/24
    months=[]
    for month in range(math.ceil(end/30)):
        finished=[r for r in rows if month*720<=r['end_h']<(month+1)*720]
        months.append(dict(month=month+1,task_cost_usd=sum(r['cost_usd'] for r in finished),completed_beams=sum(r['id'].endswith('/test') for r in finished)))
    return dict(scenario=scenario,quantities=q,resources=a['resources'],tasks=rows,completion_calendar_day=end,monthly_task_cash=months,
        completed_test_plans=q['beams'],actual_qa_or_construction_executed=False,
        planning_readiness=bool(q['nominal_crane_screen_pass'] and q['nominal_transport_screen_pass']),
        release=False,limits=['continuous elapsed curing capacity and mould occupancy; onsite crews operate8h percalendar day','no road closure windows, hot-weather strength-development data, foundation/transport route or vendor chart approval','plans schedule unexecuted holdpoints; elapsed age alone cannot release concrete'])

@lru_cache(maxsize=2)
def _study(source):
    a=load();cases=[construction(a['reference_length_m'],scenario=k,a=a) for k in ('nominal','rework','import-delay','crane-outage','slow-cure')]
    return encoded(dict(schema=SCHEMA,source_sha256=json.loads(source),assumptions=a,cases=cases,shared_factory=factory_allocation(1.,a),**FLAGS))
def study():return json.loads(_study(json.dumps(sources(),sort_keys=True)))

def overview(v):
    rows=['<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="450"><rect width="1200" height="450" fill="#f5f7fa"/><g font-family="sans-serif" fill="#152c45"><text x="30" y="38" font-size="24">1 km resource-constrained delivery: provisional calendar days</text>']
    for i,c in enumerate(v['cases']):
        y=95+i*55;days=c['completion_calendar_day'];rows.append(f'<text x="30" y="{y}" font-size="17">{c["scenario"]}</text><rect x="225" y="{y-20}" width="{days*3:.2f}" height="28" fill="#28877b"/><text x="{240+days*3:.2f}" y="{y}" font-size="16">{days:.1f} days</text>')
    rows.append('<text x="30" y="420" font-size="16">QA, strength, site, crane chart and manufacturing acceptance remain open. Dates are planning outputs.</text></g></svg>');return '\n'.join(rows)+'\n'
def readme(v):
    return '# Resource-loaded Baghdad delivery study\n\nA complete finite 1 km task graph counts 80 directional beams, 41 support positions, finite mould/curing/QA/haul/crane/stator/test resources and procurement lead times. All inspections and strength certificates remain unexecuted.\n\n[Schedule and quantities](study.json.gz) · [Scenario chart](overview.svg) · [Receipt](manifest.json)\n\n'+ '\n'.join(f'- {c["scenario"]}: {c["completion_calendar_day"]:.2f} calendar days; {len(c["tasks"])} tasks.' for c in v['cases'])+'\n\nFactory capital is a single100km programme pool with a route-km allocation, not a separate whole factory charged to every city. Imported finished equipment, imported inputs, local process expenditure and training are separated; local spend is not verified domestic value added. UK suppliers are research candidates; no ordered model, origin certificate or quote is claimed. See dated primary-source links in assumptions.\n'
def publish(output=OUTPUT):
    v=study();p=Path(output);p.mkdir(parents=True,exist_ok=True)
    if p.is_symlink() or any(x.is_symlink() or x.name not in FILES|{'manifest.json'} for x in p.iterdir()):raise ValueError('owned delivery output required')
    raw=encoded(v)
    if len(raw)>MAX_RAW:raise ValueError('bounded delivery result required')
    payload={'study.json.gz':gzip.compress(raw,mtime=0),'overview.svg':overview(v).encode(),'README.md':readme(v).encode()}
    for name,data in payload.items():(p/name).write_bytes(data)
    m=dict(schema=SCHEMA,source_sha256=v['source_sha256'],files_sha256={name:digest(p/name) for name in FILES},**FLAGS);(p/'manifest.json').write_bytes(encoded(m));return verify(p)
def _verified_payload(output):
    p=Path(output)
    if p.is_symlink() or not p.is_dir() or {x.name for x in p.iterdir()}!=FILES|{'manifest.json'} or any(x.is_symlink() for x in p.iterdir()):raise ValueError('exact delivery packet required')
    m=json.loads((p/'manifest.json').read_bytes())
    if m.get('source_sha256')!=sources() or any(m.get(k) is not False for k in FLAGS):raise ValueError('delivery source/authority differs')
    for name in FILES:
        if (p/name).stat().st_size>MAX_RAW or digest(p/name)!=m['files_sha256'][name]:raise ValueError('delivery checksum/size differs')
    with gzip.GzipFile(fileobj=io.BytesIO((p/'study.json.gz').read_bytes())) as stream:raw=stream.read(MAX_RAW+1)
    v=study()
    if raw!=encoded(v) or (p/'overview.svg').read_text()!=overview(v) or (p/'README.md').read_text()!=readme(v):raise ValueError('delivery recalculation/presentation differs')
    return m,v
def verify(output=OUTPUT):return _verified_payload(output)[0]
def read_summary(output=OUTPUT):
    _,v=_verified_payload(output);return dict(schema=SCHEMA,scenarios=[dict(scenario=c['scenario'],calendar_days=c['completion_calendar_day'],tasks=len(c['tasks'])) for c in v['cases']],shared_factory=v['shared_factory'],**FLAGS)
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('action',choices=('publish','verify'),nargs='?',default='publish');args=parser.parse_args();print(json.dumps(globals()[args.action](),indent=2))
