"""Resource-leveled, disabled city delivery hypotheses at already priced capacity.

Relative workdays are a planning calendar, not promised dates. Process-hour and
supplier-capacity assumptions do not establish engineering or manufacturing release.
"""
from copy import deepcopy
from bisect import insort
from hashlib import sha256
from heapq import heappop, heappush
from math import ceil, fsum, isfinite
from pathlib import Path
import json

ROOT=Path(__file__).resolve().parents[2]
PRODUCER='engineering/outline/delivery_plan.py'
CASES=('low','base','high')
FLAGS=dict(physical_accepted=False,engineering_accepted=False,manufacturing_release=False,
    operating_release=False,movement_authority=False,procurement_approved=False,
    submission_allowed=False,external_transactions_performed=False,named_workers_assigned=False)
DEFAULTS=dict(overrun_factory_annual_fraction=[.03,.06,.12],overrun_site_annual_fraction=[.002,.005,.01],version='CITY-DELIVERY-PLAN-1',production_years=3,days_per_year=250,
    shifts_per_day=2,hours_per_shift=8.,utilisation=.75,maximum_batches=128,maximum_tasks=5000,
    imported_lead_workdays=[30.,60.,120.],local_lead_workdays=[5.,15.,45.],
    engineering_workdays=[30.,60.,120.],plant_setup_workdays=[30.,60.,120.],
    final_test_workdays=[10.,20.,40.],supplier_delivery_target_workdays=[500.,750.,1000.],
    support_labour_h_each=[8.,24.,64.],erection_labour_h_span=[20.,64.,180.],
    spans_per_crane_shift=[4.,2.,1.],mould_cycle_workdays=[2.,5.,10.],
    mould_availability=.75,assembly_crew=6,precast_crew=8,field_crew=8,
    support_concrete_wait_workdays=[5.,10.,20.],precast_storage_workdays=[5.,10.,21.],
    ancillary_labour_budget_fraction=[.10,.20,.30],local_loaded_paid_wage_usd_h=[9375/1510,11812.5/1510,16500/1510])


def encoded(v):return (json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False)+'\n').encode()
def identity(v):return sha256(encoded(v)).hexdigest()
def digest(p):return sha256(Path(p).read_bytes()).hexdigest()
def seal(v,key):v[key]=identity(v);return v


def _number(v,name,zero=False):
    if type(v) not in (int,float) or not isfinite(v) or (v<0 if zero else v<=0):raise ValueError('Finite '+('nonnegative ' if zero else 'positive ')+name+' required')
    return float(v)


def _sealed(v,key):
    if not isinstance(v,dict) or v.get(key)!=identity({k:x for k,x in v.items() if k!=key}):raise ValueError('Stale delivery input identity: '+key)


def _policy(policy):
    p=deepcopy(DEFAULTS);over=(policy or {}).get('delivery',policy or {})
    if set(over)-set(p):raise ValueError('Unknown delivery policy key')
    p.update(over)
    for k,v in p.items():
        if isinstance(v,list):
            if len(v)!=3:raise ValueError('Three delivery cases required')
            for x in v:_number(x,k)
        elif type(v) in (int,float):_number(v,k)
    if (p['production_years'],p['days_per_year'],p['shifts_per_day'],p['hours_per_shift'],p['utilisation'])!=(3,250,2,8.,.75):
        raise ValueError('Delivery must match the priced three-year, two eight-hour shift, 250-day, 75% production calendar')
    if type(p['maximum_tasks']) is not int or not 100<=p['maximum_tasks']<=5000:raise ValueError('Delivery task budget must be100to5000')
    if type(p['maximum_batches']) is not int or not 1<=p['maximum_batches']<=128:raise ValueError('One to128 delivery batches required')
    return p


def _batches(total,n):
    return [total//n+(i<total%n) for i in range(n)]


def _schedule(tasks,resources,case):
    """Earliest-start serial scheduling with sorted availability (no time grid)."""
    by={x['task_id']:x for x in tasks}
    pools={r['resource_id']:[(0.,i) for i in range(r['capacity_by_case'][case])] for r in resources}
    if len(by)!=len(tasks):raise ValueError('Duplicate delivery task')
    successors={k:[] for k in by};counts={}
    for k,t in by.items():
        if len(t['predecessors'])!=len(set(t['predecessors'])) or any(x not in by for x in t['predecessors']):raise ValueError('Unknown or duplicate task predecessor')
        counts[k]=len(t['predecessors'])
        for x in t['predecessors']:successors[x].append(k)
    ready={k for k,n in counts.items() if n==0};done={};capacity_pass=True;reservations={}
    while ready:
        choices=[]
        for k in ready:
            t=by[k];start=max((done[x]['finish_workday'] for x in t['predecessors']),default=0.)
            requests=[(r['resource_id'],int(r.get('units_by_case',{}).get(case,r.get('units',1)))) for r in t['resource_requests']]
            valid=True
            for r,n in requests:
                if r not in pools or n<1 or n>len(pools[r]):valid=False;break
                start=max(start,pools[r][n-1][0])
            choices.append((start,t.get('ordinal',0),k,requests,valid))
        start,_,k,requests,valid=min(choices,key=lambda x:x[:3]);ready.remove(k);t=by[k]
        finish=start+_number(t['duration_workdays'][case],'task duration');allocations=[]
        if not valid:capacity_pass=False
        else:
            for r,n in requests:
                selected=pools[r][:n];del pools[r][:n]
                allocations.append(dict(resource_id=r,units=[i for _,i in selected]))
                for _,i in selected:
                    reservations.setdefault((r,i),[]).append((start,finish));insort(pools[r],(finish,i))
        done[k]=dict(task_id=k,start_workday=start,finish_workday=finish,resource_allocations=allocations,status='scheduled-conditional' if valid else 'unpriced-resource-hold')
        for x in successors[k]:
            counts[x]-=1
            if counts[x]==0:ready.add(x)
    if len(done)!=len(by):raise ValueError('Cyclic delivery task graph')
    for intervals in reservations.values():
        intervals.sort()
        if any(a[1]>b[0]+1e-9 for a,b in zip(intervals,intervals[1:])):raise ValueError('Overlapping constrained delivery resource')
    return dict(tasks=sorted(done.values(),key=lambda z:(z['start_workday'],z['task_id'])),finish_workday=max(z['finish_workday'] for z in done.values()),capacity_pass=capacity_pass,duration_is_conditional_bound=True,engineering_release=False)


def evaluate(city_record,policy=None,root=ROOT):
    """Create a complete provisional plan without changing the city price ledger."""
    root=Path(root);p=_policy(policy);_sealed(city_record,'evaluation_id')
    record=city_record;cost=record['cost'];_sealed(cost,'evaluation_id')
    geometry=record['geometry_and_service'];_sealed(geometry,'input_id')
    if (record['input_id']!=cost['city_input_id'] or record['input_id']!=geometry['input_id']):raise ValueError('Mixed city cost and geometry identities')
    service_evaluation=record['service_evaluation'];_sealed(service_evaluation,'evaluation_id')
    if service_evaluation.get('city_input_id')!=record['input_id'] or cost.get('input_line_services_id')!=identity(service_evaluation['line_services']):raise ValueError('Mixed delivery service/cost identities')
    configuration=record['research_configuration']
    if record['research_configuration_id']!=identity(configuration):raise ValueError('Research configuration identity differs')
    if configuration['city_input_id']!=record['input_id'] or configuration['reference_candidate_ids']!=record['reference_candidate_ids']:raise ValueError('Mixed delivery configuration')
    for k in ('physical_accepted','engineering_accepted','manufacturing_release','operating_release','movement_authority'):
        if record.get(k) is not False or cost.get(k) is not False:raise ValueError('Outline delivery cannot inherit physical release')
    sources={}
    for mapping in (record.get('source_sha256',{}),cost.get('source_sha256',{}),geometry.get('source_sha256',{})):
        for name,sha in mapping.items():
            if name in sources and sources[name]!=sha:raise ValueError('Mixed delivery source epochs')
            sources[name]=sha
    for name,sha in sources.items():
        if Path(name).is_absolute() or '..' in Path(name).parts:raise ValueError('Repository-relative delivery source required')
        if digest(root/name)!=sha:raise ValueError('Delivery source changed: '+name)
    sources[PRODUCER]=digest(__file__)
    vc=cost['production_supply']['vehicle_cost'];_sealed(vc,'cost_estimate_id')
    if vc['candidate_id']!=record['reference_candidate_ids']['candidate_id']:raise ValueError('Mixed vehicle cost candidate')
    capital=cost['capital_lines'];capital_by={r['key']:r for r in capital}
    if len(capital_by)!=len(capital):raise ValueError('Duplicate capital account')
    factory=capital_by['citywide-production-equipment-tools-buildings-yards']['quantity']
    fleet=cost['resources']['total_trainsets'];cars=cost['resources']['totalcars']
    if type(fleet) is not int or fleet<=0 or cars!=6*fleet or factory['committed_cars']!=cars:raise ValueError('Committed delivery quantity differs')
    fx=cost['production_supply']['assumptions']['iqd_per_usd'];hday=16*.75;horizon=750.
    items=[];boms=[];groups=[];tasks=[];resources=[];flows=[];next_tasks=[];labour_total={c:0. for c in CASES}
    scope=record['research_configuration_id'];prefix='OSR-'+scope[:12]+'-'
    def item(key,name,qty,uom,kind,lines,budget=None,**extra):
        value=dict(item_code=prefix+identity(key)[:16],name=name,quantity=qty,uom=uom,kind=kind,source_line_ids=list(lines),provisional=True,**extra)
        if budget is not None:
            value['budget_usd']=dict(budget)
            value['unit_cost_usd']={c:budget[c]/qty for c in CASES}
        seal(value,'item_id');items.append(value);return value['item_code']
    def resource(key,name,domain,capacity,unit,owned,priced,lines):
        r=dict(resource_id=identity([scope,key]),name=name,domain=domain,capacity_by_case=dict(zip(CASES,capacity)),capacity_unit=unit,owned=owned,priced=priced,calendar_id='two-shift-productive' if domain!='supplier' else 'supplier-planning',source_line_ids=list(lines))
        if any(type(n) is not int or n<0 for n in capacity):raise ValueError('Integer resource capacity required')
        resources.append(r);return r['resource_id']
    def task(key,name,domain,quantity,uom,predecessors,durations,requests,lines,**extra):
        t=dict(task_id=identity([scope,key]),ordinal=len(tasks),name=name,domain=domain,quantity=quantity,uom=uom,predecessors=list(dict.fromkeys(predecessors)),resource_requests=requests,duration_workdays=dict(zip(CASES,[max(1e-8,float(x)) for x in durations])),source_line_ids=list(lines),**extra)
        tasks.append(t);return t['task_id']
    def req(r,n=1):return dict(resource_id=r,units=n)
    labour=resource('factory-labour','Priced pooled local production positions','manufacturing',list(cost['resources']['production_positions_per_shift']),'operators',True,True,[capital_by['citywide-production-equipment-tools-buildings-yards']['line_id']])
    if any(n<=0 for n in cost['resources']['production_positions_per_shift']):raise ValueError('Positive priced production workforce required')
    development=task('development','Survey/design/prototypes/independent-review planning gates','engineering',1,'project',[],p['engineering_workdays'],[],[capital_by['design-prototypes-independent-review']['line_id']],planned_gate_only=True,gate_executed=False)
    plant=task('plant-setup','Priced production premises/equipment/tooling commissioning hypothesis','manufacturing',1,'project',[development],p['plant_setup_workdays'],[],[capital_by['citywide-production-equipment-tools-buildings-yards']['line_id']],gate_executed=False)
    component_count=sum(z['line_key'] not in ('six-car-final-vehicle-assembly','reference-factory-to-assembly-delivery') for z in vc['lines'])
    vehicle_batch_limit=max(1,(p['maximum_tasks']-128*9-component_count-10)//(2*component_count+1))
    train_batches=_batches(fleet,min(fleet,p['maximum_batches'],vehicle_batch_limit));car_batches=[n*6 for n in train_batches]
    decisions={r.get('line_key'):r for r in cost['production_supply']['decisions']}
    component_codes=[];finished_by_batch=[[] for _ in train_batches]
    for index,line in enumerate(vc['lines']):
        key=line['line_key'];q=line['quantity'];source=[line['line_id']]
        if key in ('six-car-final-vehicle-assembly','reference-factory-to-assembly-delivery'):continue
        factors=vc['mass_reserve_sensitivity']['case_factors'];hours=[];budgets={}
        for i,c in enumerate(CASES):
            norm=factors[c] if key.startswith('unlocated-account/') else 1.
            hours.append(fleet*(q.get('process_hours_per_train',[0,0,0])[i]/norm+6*q.get('process_hours_per_car',[0,0,0])[i]))
            budgets[c]=line['cost_iqd'][c]/norm*fleet/fx;labour_total[c]+=hours[-1]
        if any(x<=0 for x in hours):raise ValueError('Missing local manufacturing/receiving labour remains undefined: '+key)
        code=item('vehicle/'+key,key,cars,'account-kit','provisional-account-assembly',source,budgets,
            scope_note='One source-account kit per car, not an approved detailed physical BOM',occurrence_ids=line.get('occurrence_ids',[]))
        component_codes.append(code);decision=decisions.get(key,{});route=decision.get('selected_route','receive-fit')
        comparison=decision.get('comparison');cell=None;duration=[]
        if route=='make':
            cell=resource('cell/'+key,'Priced '+key+' processing-cell bundle','manufacturing',[comparison['cases'][c]['make']['cell_count'] for c in CASES],'processing-cell',True,True,source)
            for i,c in enumerate(CASES):
                m=comparison['cases'][c]['make'];crew=min(cost['resources']['production_positions_per_shift'][i],max(1,ceil(m['labour_hours']/m['required_cell_hours'])))
                duration.append(max(m['required_cell_hours'],m['machine_hours'],hours[i]/crew)/hday)
            material_qty={c:comparison['cases'][c]['make']['material']['purchased_quantity'] for c in CASES}
            raw=item('raw/'+key,'Declared material recipe for '+key,material_qty['base'],comparison['cases']['base']['make']['material']['unit'],'material-recipe',source,
                {c:comparison['cases'][c]['make']['variable_components']['material_gross'] for c in CASES},quantity_cases=material_qty)
            bom=dict(item_code=code,output_quantity=1,uom='account-kit',items=[dict(item_code=raw,qty=material_qty['base']/cars,uom=comparison['cases']['base']['make']['material']['unit'])],source_line_ids=source,physical_material_definition_resolved=False)
            seal(bom,'bom_id');boms.append(bom)
        else:
            route='buy' if route=='buy' else 'receive-fit';duration=[h/hday for h in hours]
            raw=item('purchased/'+key,'Purchased bounded '+key,cars,'account-kit','purchased',source,budgets)
            material_qty={c:float(cars) for c in CASES}
        supplier=resource('supplier/'+key,'Assumed contracted material/module delivery: '+key,'supplier',[1,1,1],'contracted-stream',False,True,source)
        availability=task('procurement/'+key,'Source/qualify/ship '+key,'procurement',material_qty['base'],'source-unit',[development],p['imported_lead_workdays'],[],source,supplier_confirmed=False)
        crews=[min(cost['resources']['production_positions_per_shift'][i],max(1,ceil(comparison['cases'][c]['make']['labour_hours']/comparison['cases'][c]['make']['required_cell_hours']))) if route=='make' else 1 for i,c in enumerate(CASES)]
        previous_delivery=availability
        for b,ncar in enumerate(car_batches):
            fraction=ncar/cars
            delivered=task('delivery/'+key+'/'+str(b),'Incoming material/module batch '+key,'supplier',ncar,'car-kit',[previous_delivery],
                [fraction*z for z in p['supplier_delivery_target_workdays']],[req(supplier)],source)
            previous_delivery=delivered
            made=task('process/'+key+'/'+str(b),'Make/receive/fit/inspect '+key,'manufacturing',ncar,'account-kit',[plant,delivered],
                [fraction*z for z in duration],[dict(resource_id=labour,units=crews[1],units_by_case=dict(zip(CASES,crews)))]+([req(cell)] if cell else []),source,
                productive_person_hours={c:hours[i]*fraction for i,c in enumerate(CASES)},unexecuted_inspection=True)
            finished_by_batch[b].append(made)
            flows.append(dict(item_code=raw,receipt_task=delivered,consume_task=made,quantity_cases={c:material_qty[c]*fraction for c in CASES},unit=next(x['uom'] for x in items if x['item_code']==raw)))
        operations=[dict(operation_id=identity([scope,key,'process']),name='Make/receive/fit and inspect declared account kit',sequence=1,source_line_ids=source,resource_id=cell or labour,hours_per_unit={c:duration[i]*hday/cars for i,c in enumerate(CASES)},person_hours_per_unit={c:hours[i]/cars for i,c in enumerate(CASES)},duration_basis='Productive workstation occupancy derived from priced cell/machine/labour requirement; person-hours retained separately; procurement elapsed time excluded')]
        groups.append(dict(group_id=identity([scope,key]),item_code=code,route=route,output_quantity=cars,uom='account-kit',operations=operations,source_cost_line_ids=source,resource_ids=[labour]+([cell] if cell else []),source_comparison_id=comparison.get('evaluation_id') if comparison else None))
    car=item('car','Provisional complete car account assembly',cars,'Nos','assembly',[capital_by['network-delivered-assembled-fleet']['line_id']],capital_by['network-delivered-assembled-fleet']['costs_usd'])
    train=item('train','Six-car train account assembly',fleet,'Nos','assembly',[capital_by['network-delivered-assembled-fleet']['line_id']],capital_by['network-delivered-assembled-fleet']['costs_usd'])
    boms.append(seal(dict(item_code=car,output_quantity=1,uom='Nos',items=[dict(item_code=x,qty=1,uom='account-kit') for x in component_codes],source_line_ids=[capital_by['network-delivered-assembled-fleet']['line_id']],account_overlap_unresolved=vc.get('accounting_overlap')),'bom_id'))
    boms.append(seal(dict(item_code=train,output_quantity=1,uom='Nos',items=[dict(item_code=car,qty=6,uom='Nos')],source_line_ids=[capital_by['network-delivered-assembled-fleet']['line_id']]),'bom_id'))
    assembly_line=next(z for z in vc['lines'] if z['line_key']=='six-car-final-vehicle-assembly');assembly_h=[fleet*6*z for z in assembly_line['quantity']['labour_hours_per_car']]
    assembly_resource=resource('assembly','Priced final assembly bays','manufacturing',list(factory['assembly_bays']),'bay',True,True,[assembly_line['line_id']])
    assembly_tasks=[]
    assembly_crews=[min(p['assembly_crew'],n) for n in cost['resources']['production_positions_per_shift']]
    for b,ntrain in enumerate(train_batches):
        assembly_tasks.append(task('assembly/'+str(b),'Final assembly, interfaces and test batch','manufacturing',ntrain,'train',finished_by_batch[b],
            [ntrain/fleet*h/(assembly_crews[i]*hday) for i,h in enumerate(assembly_h)],[req(assembly_resource),dict(resource_id=labour,units=assembly_crews[1],units_by_case=dict(zip(CASES,assembly_crews)))],[assembly_line['line_id']],unexecuted_inspection=True,productive_person_hours={c:assembly_h[i]*ntrain/fleet for i,c in enumerate(CASES)}))
    for i,c in enumerate(CASES):labour_total[c]+=assembly_h[i]
    groups.append(dict(group_id=identity([scope,'final-assembly']),item_code=train,route='make',output_quantity=fleet,uom='Nos',source_cost_line_ids=[assembly_line['line_id']],resource_ids=[assembly_resource,labour],operations=[dict(operation_id=identity([scope,'final-assembly-op']),name='Assemble six cars, inspect and integration-test',sequence=1,source_line_ids=[assembly_line['line_id']],resource_id=assembly_resource,hours_per_unit={c:assembly_h[i]/fleet/assembly_crews[i] for i,c in enumerate(CASES)},person_hours_per_unit={c:assembly_h[i]/fleet for i,c in enumerate(CASES)},duration_basis='Productive bay occupancy divides source person-hours by declared crew within priced positions; no additional labour cost')]))
    # Civil production and field work are distinct from the owned vehicle pool.
    cq=cost['civil']['quantities'];span_count=cq['span_count'];support_count=cq['independent_supports'];civil_dec=cost['civil']['factory_decision'];civil_end=[]
    civil_labour=[support_count*p['support_labour_h_each'][i]+span_count*p['erection_labour_h_span'][i] for i in range(3)]
    available_field_days=[max(1.,horizon-p['engineering_workdays'][i]-p['plant_setup_workdays'][i]-max(p['imported_lead_workdays'][i],p['support_concrete_wait_workdays'][i])-p['final_test_workdays'][i]) for i in range(3)]
    field_positions=[max(p['field_crew'],ceil(h/(available_field_days[i]*hday))) if h else 0 for i,h in enumerate(civil_labour)]
    field=resource('field-labour','Timeboxed civil crew positions within declared paid-hour provision','civil',field_positions,'operators',False,True,[capital_by['piers-and-foundations']['line_id'],capital_by['transport-crane-erection-track-install']['line_id']])
    crane_shifts=[ceil(span_count/z) for z in p['spans_per_crane_shift']]
    crane=resource('cranes','Hired crane active shifts already inside erection provision','civil',[max(1,ceil(h/(available_field_days[i]*2))) if h else 0 for i,h in enumerate(crane_shifts)],'hired-crane',False,True,[capital_by['transport-crane-erection-track-install']['line_id']])
    beam_code=None
    if span_count:
        beam_code=item('civil/span','Selected 20 m repeat box-beam structural kit',span_count,'Nos','provisional-civil-assembly',[capital_by['repeat-box-beams']['line_id']],capital_by['repeat-box-beams']['costs_usd'])
        raw_beam=item('civil/span-material-kit','Concrete/rebar/tendon/anchorage structural kit',span_count,'kit','material-recipe',[capital_by['repeat-box-beams']['line_id']],
            {c:civil_dec['comparison']['cases'][c]['make']['variable_components']['material_gross'] for c in CASES})
        boms.append(seal(dict(item_code=beam_code,output_quantity=1,uom='Nos',items=[dict(item_code=raw_beam,qty=1,uom='kit')],source_line_ids=[capital_by['repeat-box-beams']['line_id']],detailed_bar_and_prestress_schedule_qualified=False),'bom_id'))
        make=civil_dec['selected_route']=='make';comp=civil_dec['comparison'];cell=None;mould=None
        if make:
            cell=resource('precast-cells','Priced repeat-beam production cells','civil',[comp['cases'][c]['make']['cell_count'] for c in CASES],'processing-cell',True,True,[capital_by['repeat-box-beams']['line_id']])
            mould_counts=[int(round(z/120)) for z in factory['precast_floor_m2']]
            mould=resource('precast-moulds','Priced 24 by5m bed/mould footprints','civil',mould_counts,'mould',True,True,[capital_by['repeat-box-beams']['line_id']])
        supplier=resource('beam-contract','Contracted beam/material delivery stream','supplier',[1,1,1],'contracted-stream',False,True,[capital_by['repeat-box-beams']['line_id']])
        civil_limit=max(1,(p['maximum_tasks']-len(tasks)-3)//9)
        civil_batch_count=min(span_count,128,civil_limit,max(p['maximum_batches'],ceil(span_count/max(1,mould_counts[1])) if make else p['maximum_batches']))
        counts=_batches(span_count,civil_batch_count)
        support_batches=_batches(support_count,len(counts))
        previous_beam_delivery=development
        for b,n in enumerate(counts):
            sub=task('foundations/'+str(b),'Foundations/piers with unexecuted geotechnical and concrete QA gates','civil',support_batches[b],'support',[development],
                [support_batches[b]*z/(p['field_crew']*hday) for z in p['support_labour_h_each']],[req(field,p['field_crew'])],[capital_by['piers-and-foundations']['line_id']])
            cured=task('foundation-cure/'+str(b),'Foundation strength-development/inspection allowance','civil',support_batches[b],'support',[sub],p['support_concrete_wait_workdays'],[],[capital_by['piers-and-foundations']['line_id']],elapsed_age_is_not_release=True)
            delivered=task('beam-input/'+str(b),'Precast inputs or contracted finished-beam batch','supplier',n,'beam',[previous_beam_delivery],
                [n/span_count*z for z in p['supplier_delivery_target_workdays']],[req(supplier)],[capital_by['repeat-box-beams']['line_id']])
            previous_beam_delivery=delivered
            if make:
                # Complete mould cycle includes prep/cure/inspection; occupancy
                # availability is charged once, separately from crew effort.
                cast=task('precast-cast/'+str(b),'Precast preparation/casting productive crew work','civil',n,'beam',[plant,delivered],
                    [n*comp['cases'][c]['make']['labour_hours']/comp['cases'][c]['make']['quantity']/(p['precast_crew']*hday) for c in CASES],
                    [req(cell)],[capital_by['repeat-box-beams']['line_id']],crew_positions_per_cell=p['precast_crew'])
                used=[min(n,m) for m in mould_counts]
                cycle=[ceil(n/used[i])*p['mould_cycle_workdays'][i]/p['mould_availability'] for i in range(3)]
                made=task('precast/'+str(b),'Priced mould occupancy/curing/QA lot','civil',n,'beam',[cast],cycle,
                    [dict(resource_id=mould,units=used[1],units_by_case=dict(zip(CASES,used)))],
                    [capital_by['repeat-box-beams']['line_id']],elapsed_age_is_not_release=True,
                    mould_cycle_starts_after_casting_is_conservative_bound=True)
            else:made=delivered
            stored=task('beam-storage/'+str(b),'Cure certificate, storage and dispatch planning gate','civil',n,'beam',[made],p['precast_storage_workdays'],[],[capital_by['repeat-box-beams']['line_id']],gate_executed=False)
            prepared=task('erection-prepare/'+str(b),'Transport, setup and temporary-stability preparation','civil',n,'beam',[stored,cured],
                [n*z*.75/(p['field_crew']*hday) for z in p['erection_labour_h_span']],[req(field,p['field_crew'])],[capital_by['transport-crane-erection-track-install']['line_id']])
            lift=task('erection/'+str(b),'Crane-at-radius lift/secure/inspect active-shift allocation','civil',n,'beam',[prepared],
                [n/z/2+(crane_shifts[i]-span_count/z)/2*(b==len(counts)-1) for i,z in enumerate(p['spans_per_crane_shift'])],
                [req(crane),dict(resource_id=field,units=6,units_by_case={c:min(field_positions[i],max(1,ceil(p['erection_labour_h_span'][i]*.25*2*p['spans_per_crane_shift'][i]/hday))) for i,c in enumerate(CASES)})],[capital_by['transport-crane-erection-track-install']['line_id']],crane_chart_qualified=False)
            civil_end.append(lift);flows.append(dict(item_code=raw_beam,receipt_task=delivered,consume_task=made,quantity_cases={c:float(n) for c in CASES},unit='kit'))
        groups.append(dict(group_id=identity([scope,'precast']),item_code=beam_code,route='make' if make else 'buy',output_quantity=span_count,uom='Nos',source_cost_line_ids=[capital_by['repeat-box-beams']['line_id']],resource_ids=[cell] if cell else [supplier],operations=[dict(operation_id=identity([scope,'precast-op']),name='Produce or receive precast span, inspect and dispatch',sequence=1,source_line_ids=[capital_by['repeat-box-beams']['line_id']],resource_id=cell or supplier,hours_per_unit={c:comp['cases'][c]['make']['required_cell_hours']/comp['cases'][c]['make']['quantity'] if make else 1. for c in CASES},person_hours_per_unit={c:comp['cases'][c]['make']['labour_hours']/comp['cases'][c]['make']['quantity'] for c in CASES},duration_basis='Productive cell occupancy or bounded incoming inspection hour; separate person-hours and elapsed mould/cure intervals')]))
    # Remaining infrastructure has explicit bounded contractor effort rather
    # than missing/zero station, groundworks, tunnel or electrical installation.
    ancillary=[z for z in capital if z['scope'] in ('stations-power','construction','land-utilities-depot') and z['key'] not in ('piers-and-foundations','transport-crane-erection-track-install','city-project-risk-contingency','design-prototypes-independent-review','unallocated-package-tax-duty')]
    ancillary_h=[fsum(z['costs_usd'][c] for z in ancillary)*p['ancillary_labour_budget_fraction'][i]/p['local_loaded_paid_wage_usd_h'][i]*.75 for i,c in enumerate(CASES)]
    ancillary_positions=[max(1,ceil(h/(available_field_days[i]*hday))) for i,h in enumerate(ancillary_h)]
    installer=resource('installation-contract','Contracted power/access/track/surface/tunnel installation positions','civil',ancillary_positions,'contractor-operators',False,True,[z['line_id'] for z in ancillary])
    installation_tasks=[];fronts=max(1,min(len(geometry['lines']),len(civil_end) or 1))
    install_crew=[max(1,n//fronts) for n in ancillary_positions]
    endings=civil_end or [development]
    for b,precedent in enumerate(endings):
        installation_tasks.append(task('systems-install/'+str(b),'Streamed power/controls/access/surface/tunnel/depot installation lot','civil',1/len(endings),'network-lot',[precedent],
            [h/len(endings)/(n*hday) for h,n in zip(ancillary_h,install_crew)],
            [dict(resource_id=installer,units=install_crew[1],units_by_case=dict(zip(CASES,install_crew)))],[z['line_id'] for z in ancillary],labour_estimate_is_budget_share_not_measured=True))
    final=task('final-test','Integrated trials, accessibility/fire/protection and independent review planning gate','engineering',1,'network',installation_tasks+assembly_tasks,p['final_test_workdays'],[],[capital_by['design-prototypes-independent-review']['line_id']],gate_executed=False,movement_authority=False)
    if len(tasks)>p['maximum_tasks']:raise ValueError('Quantity-conserving lot coarsening did not meet task budget')
    schedules={c:_schedule(tasks,resources,c) for c in CASES}
    for c,case in schedules.items():
        case['target_workdays']=horizon;case['target_met']=case['finish_workday']<=horizon
        if not case['capacity_pass'] or not case['target_met']:next_tasks.append(dict(kind='provisional-resource-or-programme-redesign',case=c,computed_completion_workday=case['finish_workday'],priced_target_workday=horizon,priced_capacity_changed=False,additional_cost_added=False))
    # Allocate a bounded elapsed-time upkeep/site-services estimate to the
    # already counted project contingency; never buy premises/capex again.
    overrun={};allocated={};uncovered={};remaining={}
    reserve=capital_by.get('city-project-risk-contingency',{}).get('costs_usd',{c:0. for c in CASES})
    for i,c in enumerate(CASES):
        extra_years=max(0.,schedules[c]['finish_workday']-horizon)/250
        premises=cost['resources'].get('vehicle_factory_premises_usd',{}).get(c,0.)
        site=fsum(z['costs_usd'][c] for z in capital if z['scope'] in ('construction','stations-power','land-utilities-depot') and z['key']!='city-project-risk-contingency')
        overrun[c]=extra_years*(premises*p['overrun_factory_annual_fraction'][i]+site*p['overrun_site_annual_fraction'][i])
        allocated[c]=min(reserve[c],overrun[c]);uncovered[c]=max(0.,overrun[c]-reserve[c]);remaining[c]=max(0.,reserve[c]-overrun[c])
        if uncovered[c]>0:next_tasks.append(dict(kind='uncovered-programme-overrun-budget',case=c,uncovered_usd=uncovered[c],amount_added_to_original_ledger=False))
    # Independent material-precedence check; no consumption precedes receipt.
    material_checks=[]
    for c,sc in schedules.items():
        rows={z['task_id']:z for z in sc['tasks']}
        valid=all(rows[z['receipt_task']]['finish_workday']<=rows[z['consume_task']]['start_workday']+1e-9 or z['receipt_task']==z['consume_task'] for z in flows)
        if not valid:raise ValueError('Material consumption precedes delivery')
        material_checks.append(dict(case=c,nonnegative_stock_by_precedence=True,receipt_and_consumption_quantities_reconcile=True))
    workforces=[dict(shift_id='production',domain='manufacturing',shifts_per_day=2,hours_per_shift=8.,days_per_year=250,utilisation=.75,positions_by_case=dict(zip(CASES,cost['resources']['production_positions_per_shift'])),two_shift_distinct_people={c:2*cost['resources']['production_positions_per_shift'][i] for i,c in enumerate(CASES)}),
        dict(shift_id='civil',domain='civil',shifts_per_day=2,hours_per_shift=8.,days_per_year=250,utilisation=.75,positions_by_case={c:field_positions[i]+ancillary_positions[i]+(civil_dec['comparison']['cases'][c]['make']['cell_count']*p['precast_crew'] if span_count and civil_dec['selected_route']=='make' else 0) for i,c in enumerate(CASES)},employment_basis='Timeboxed contracted peak demand, not full-horizon permanent employment')]
    services=record['service_evaluation']['line_services'];op_hours=max(z['requirements']['operating_hours_per_day'] for z in services);op_shifts=2 if op_hours<=18 else 3
    workforces.append(dict(shift_id='operations',domain='operations',shifts_per_day=op_shifts,hours_per_shift=op_hours/op_shifts,days_per_year=365,utilisation=1.,positions_by_case={c:float([2,4,8][i]+cost['resources']['access_sites']*[1,2,4][i]) for i,c in enumerate(CASES)},staffing_basis='Same current city-cost controller[2,4,8] and staff-per-access-site[1,2,4] assumptions; additional relief/competence/site roster requires review'))
    value=dict(schema='osr-city-outline-delivery-plan/1',city=record['city'],city_record_evaluation_id=record['evaluation_id'],city_input_id=record['input_id'],cost_evaluation_id=cost['evaluation_id'],research_configuration_id=scope,
        reference_candidate_ids=record['reference_candidate_ids'],selection_id=record['selection_id'],planning_revision_id=record.get('planning_revision_id',record['input_id']),planning_revision_sha256=geometry.get('planning_revision_sha256',geometry.get('revision_sha256')),
        items=items,boms=boms,production_groups=groups,resources=resources,tasks=tasks,schedule=dict(cases=schedules,final_gate_task_id=final,calendar_dates_assigned=False),
        workforce=dict(shift_patterns=workforces,named_workers_assigned=False),material_flow=dict(events=flows,checks=material_checks,starting_inventory_zero_hypothesis=True),
        cost_reconciliation=dict(source_capital_usd=cost['installed_capital_usd'],source_whole_life_usd=cost['whole_life_npv_usd'],cost_ledger_identity=identity(cost['capital_lines']+cost['lifecycle_lines']),additional_cost_usd={c:0. for c in CASES},factory_capital_counted_again=False,priced_resources_changed=False,item_budgets_are_hierarchical_not_additive=True,capacity_hours_per_workplace=9000.,derived_local_productive_person_hours=labour_total,paid_factory_person_hours={c:h/.75 for c,h in labour_total.items()},civil_productive_person_hours=dict(zip(CASES,civil_labour)),civil_paid_person_hours={c:civil_labour[i]/.75 for i,c in enumerate(CASES)},priced_crane_active_shifts=dict(zip(CASES,crane_shifts)),ancillary_productive_person_hours=dict(zip(CASES,ancillary_h)),hired_crew_available_workdays=dict(zip(CASES,available_field_days)),overrun_overhead_estimate_usd=overrun,existing_contingency_usd=reserve,contingency_allocated_to_overrun_usd=allocated,remaining_contingency_usd=remaining,uncovered_overrun_usd=uncovered,overrun_basis='Elapsed security/supervision/site services and premises upkeep only; productive labour already costed; allocation within existing contingency is not a second capital charge'),
        calendars=[dict(calendar_id='two-shift-productive',shifts_per_day=2,hours_per_shift=8.,days_per_year=250,utilisation=.75,productive_hours_per_workday=12.,calendar_dates_assigned=False)],
        assumptions=dict(policy=p,personnel_are_independent_across_two_shifts=True,
            schedule_is_provisional_resource_feasible_bound=True,common_task_count=len(tasks),quantity_conserving_lot_coarsening=True,source_account_kits_are_not_complete_detailed_BOM=True,
            supplier_capacity_confirmed=False,owned_machine_models_qualified=False,
            mould_counts_from_priced_120m2_per_bed_footprints=True,
            ancillary_labour_is_declared_fraction_of_existing_contractor_budget=True,
            operation_lifecycles_or_cost_totals_changed=False,native_solver_jobs=0,
            limitations=['Relative workdays do not establish actual dates, holidays or road closure windows.',
                'Inspections, concrete strength, crane-at-radius and temporary-stability gates are scheduled but unexecuted.',
                'Source cost-account kits and material recipes preserve unresolved geometry/overlap; they are not approved drawings.',
                'Cell/machine/crew definitions and supplier throughput are explicit planning hypotheses, not measured factory performance.',
                'Worker positions are peak timeboxed demand; retaining a full fixed payroll through idle programme extensions needs additional review.',
                'A delayed programme requires revised resources, methods or dates; this plan does not add unpriced capacity or costs.']),
        next_tasks=next_tasks+[dict(kind='engineering-and-site-release-evidence',status='pending',automatically_satisfied=False)],source_sha256=sources,**FLAGS)
    return seal(value,'plan_id')
