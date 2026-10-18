"""Finite-resource, dependency/event simulation of conditional delivery scenarios.

Times are explicit scenario inputs, never measured productivity. Storage tokens
are held from dispatch until placement; trucks can only dispatch into capacity.
"""
from copy import deepcopy
import math


def schedule(tasks,capacities):
    if not capacities or any(type(v) is not int or v<1 for v in capacities.values()):
        raise ValueError('positive integer resource capacities required')
    by_id={r['id']:deepcopy(r) for r in tasks}
    if len(by_id)!=len(tasks) or len(tasks)>4096:
        raise ValueError('bounded unique delivery tasks required')
    for task in by_id.values():
        if type(task['hours']) not in (int,float) or not math.isfinite(task['hours']) or task['hours']<=0:
            raise ValueError('finite positive scenario duration required')
        if not set(task['after'])<=by_id.keys() or task['id'] in task['after']:
            raise ValueError('unknown/self delivery dependency')
        for parent,delay in task.get('ready_after',{}).items():
            if parent not in task['after'] or type(delay) not in (int,float) or not math.isfinite(delay) or delay<0:
                raise ValueError('finite nonnegative lag on a declared predecessor required')
        for resource,people in task.get('held_people',{}).items():
            if resource not in task.get('acquire',{}) or type(people) is not int or people<1:
                raise ValueError('held labour must belong to an acquired resource')
        for field in ('resources','acquire','release'):
            for resource,amount in task.get(field,{}).items():
                if resource not in capacities or type(amount) is not int or not 1<=amount<=capacities[resource]:
                    raise ValueError('invalid resource demand')
    used={name:0 for name in capacities};peak=dict(used);busy={name:0. for name in capacities}
    held={};labour={};reserved={'site':0.,'factory':0.,'transport':0.};running={};finished={};started=set();trace=[];clock=0.
    while len(finished)<len(tasks):
        for key in sorted(k for k,v in running.items() if v[0]<=clock+1e-9):
            end,begin=running.pop(key);task=by_id[key];owner=task.get('owner',key)
            for name,n in task.get('resources',{}).items():used[name]-=n
            for name,n in task.get('release',{}).items():
                if held.get((owner,name),0)<n:raise ValueError('release of unowned storage/temporary resource')
                held[owner,name]-=n;used[name]-=n
                if not held[owner,name]:labour.pop((owner,name),None)
            finished[key]=end
            trace.append(dict(id=key,owner=owner,start_h=begin,end_h=end,resources=task.get('resources',{}),
                acquire=task.get('acquire',{}),release=task.get('release',{}),
                site=task.get('site',False),location=task.get('location','site' if task.get('site') else 'factory'),person_hours=task.get('people',0)*task['hours'],
                working_at_height_person_hours=task.get('people',0)*task['hours'] if task.get('at_height') else 0.))
        if len(finished)==len(tasks):break
        future=[]
        for key,task in sorted(by_id.items()):
            if key in started or not set(task['after'])<=finished.keys():continue
            ready=max([finished[p]+delay for p,delay in task.get('ready_after',{}).items()]+[0.])
            if ready>clock+1e-9:future.append(ready);continue
            demands=dict(task.get('resources',{}))
            for name,n in task.get('acquire',{}).items():demands[name]=demands.get(name,0)+n
            if any(used[name]+n>capacities[name] for name,n in demands.items()):continue
            owner=task.get('owner',key)
            if any(held.get((owner,name),0)<n for name,n in task.get('release',{}).items()):continue
            for name,n in demands.items():used[name]+=n;peak[name]=max(peak[name],used[name])
            for name,n in task.get('acquire',{}).items():held[owner,name]=held.get((owner,name),0)+n
            for name,n in task.get('held_people',{}).items():labour[owner,name]=(n,task.get('location','site' if task.get('site') else 'factory'))
            for name,n in task.get('resources',{}).items():busy[name]+=n*task['hours']
            running[key]=(clock+task['hours'],clock);started.add(key)
        if not running and not future:
            return dict(passed=False,reason='dependency/resource deadlock',blocked=sorted(set(by_id)-finished.keys()),tasks=trace)
        next_time=min([end for end,begin in running.values()]+future)
        for name in capacities:busy[name]+=sum(n for (owner,resource),n in held.items() if resource==name)*(next_time-clock)
        for people,location in labour.values():reserved[location]+=people*(next_time-clock)
        clock=next_time
    if any(held.values()):return dict(passed=False,reason='unreleased storage/temporary resource',tasks=trace)
    makespan=max(finished.values(),default=0.)
    resources={name:dict(capacity=capacity,peak_occupied=peak[name],busy_resource_hours=busy[name],
        utilisation=busy[name]/(capacity*makespan) if makespan else 0.) for name,capacity in capacities.items()}
    return dict(passed=True,makespan_h=makespan,tasks=sorted(trace,key=lambda r:(r['start_h'],r['id'])),resources=resources,
        onsite_person_hours=sum(r['person_hours'] for r in trace if r['site'])+reserved['site'],
        factory_person_hours=sum(r['person_hours'] for r in trace if r['location']=='factory')+reserved['factory'],
        reserved_person_hours_by_location=reserved,
        working_at_height_person_hours=sum(r['working_at_height_person_hours'] for r in trace),
        scope='Conditional deterministic resource scenario; durations, calendars and access are uncalibrated hypotheses',physical_release=False)


def bottlenecks(tasks,capacities,reference=None):
    reference=reference or schedule(tasks,capacities)
    if not reference['passed']:return []
    rows=[]
    for name in capacities:
        changed=dict(capacities);changed[name]+=1
        alternative=schedule(tasks,changed)
        rows.append(dict(resource=name,additional_capacity=1,scenario_hours_saved=reference['makespan_h']-alternative['makespan_h'] if alternative['passed'] else None))
    return sorted(rows,key=lambda r:(-(r['scenario_hours_saved'] or 0.),r['resource']))


def audit(tasks,scheduled,capacities):
    """Independently integrate resource/owner events over the recorded timeline."""
    timed={r['id']:r for r in scheduled.get('tasks',[])};checks={};events={name:[] for name in capacities};owners={}
    checks['unique_timed_tasks']=len(timed)==len(scheduled.get('tasks',[]))
    checks['exact_task_coverage']=timed.keys()=={r['id'] for r in tasks}
    if not checks['exact_task_coverage']:return checks
    for row in tasks:
        t=timed[row['id']];start,end=t['start_h'],t['end_h'];owner=row.get('owner',row['id'])
        checks[row['id']+'/finite-duration']=all(type(x) in (int,float) and math.isfinite(x) for x in (start,end)) and 0<=start<end
        if not checks[row['id']+'/finite-duration']:return checks
        for name,n in row.get('resources',{}).items():events[name]+=[(start,n),(end,-n)]
        for name,n in row.get('acquire',{}).items():
            events[name].append((start,n));owners.setdefault((owner,name),[]).append((start,n))
        for name,n in row.get('release',{}).items():
            events[name].append((end,-n));owners.setdefault((owner,name),[]).append((end,-n))
    for (owner,name),values in owners.items():
        held=0;valid=True
        for when,delta in sorted(values):held+=delta;valid &= held>=0
        checks[owner+'/'+name+'/ownership']=valid and held==0
    for name,values in events.items():
        held=peak=0;busy=0.;previous=0.;valid=True
        grouped={}
        for when,delta in values:grouped[when]=grouped.get(when,0)+delta
        for when,delta in sorted(grouped.items()):
            busy+=held*(when-previous);held+=delta;peak=max(peak,held);valid &= 0<=held<=capacities[name];previous=when
        recorded=scheduled.get('resources',{}).get(name,{})
        checks[name+'/capacity-and-occupancy']=valid and held==0 and recorded.get('capacity')==capacities[name] and recorded.get('peak_occupied')==peak and abs(recorded.get('busy_resource_hours',float('inf'))-busy)<1e-6
    return checks
