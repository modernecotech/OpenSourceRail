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
        for field in ('resources','acquire','release'):
            for resource,amount in task.get(field,{}).items():
                if resource not in capacities or type(amount) is not int or not 1<=amount<=capacities[resource]:
                    raise ValueError('invalid resource demand')
    used={name:0 for name in capacities};peak=dict(used);busy={name:0. for name in capacities}
    held={};running={};finished={};started=set();trace=[];clock=0.
    while len(finished)<len(tasks):
        for key in sorted(k for k,v in running.items() if v[0]<=clock+1e-9):
            end,begin=running.pop(key);task=by_id[key];owner=task.get('owner',key)
            for name,n in task.get('resources',{}).items():used[name]-=n
            for name,n in task.get('release',{}).items():
                if held.get((owner,name),0)<n:raise ValueError('release of unowned storage/temporary resource')
                held[owner,name]-=n;used[name]-=n
            finished[key]=end
            trace.append(dict(id=key,owner=owner,start_h=begin,end_h=end,resources=task.get('resources',{}),
                site=task.get('site',False),location=task.get('location','site' if task.get('site') else 'factory'),person_hours=task.get('people',0)*task['hours'],
                working_at_height_person_hours=task.get('people',0)*task['hours'] if task.get('at_height') else 0.))
        if len(finished)==len(tasks):break
        for key,task in sorted(by_id.items()):
            if key in started or not set(task['after'])<=finished.keys():continue
            demands=dict(task.get('resources',{}))
            for name,n in task.get('acquire',{}).items():demands[name]=demands.get(name,0)+n
            if any(used[name]+n>capacities[name] for name,n in demands.items()):continue
            owner=task.get('owner',key)
            if any(held.get((owner,name),0)<n for name,n in task.get('release',{}).items()):continue
            for name,n in demands.items():used[name]+=n;peak[name]=max(peak[name],used[name])
            for name,n in task.get('acquire',{}).items():held[owner,name]=held.get((owner,name),0)+n
            for name,n in task.get('resources',{}).items():busy[name]+=n*task['hours']
            running[key]=(clock+task['hours'],clock);started.add(key)
        if not running:
            return dict(passed=False,reason='dependency/resource deadlock',blocked=sorted(set(by_id)-finished.keys()),tasks=trace)
        next_time=min(end for end,begin in running.values())
        for name in capacities:busy[name]+=sum(n for (owner,resource),n in held.items() if resource==name)*(next_time-clock)
        clock=next_time
    if any(held.values()):return dict(passed=False,reason='unreleased storage/temporary resource',tasks=trace)
    makespan=max(finished.values(),default=0.)
    resources={name:dict(capacity=capacity,peak_occupied=peak[name],busy_resource_hours=busy[name],
        utilisation=busy[name]/(capacity*makespan) if makespan else 0.) for name,capacity in capacities.items()}
    return dict(passed=True,makespan_h=makespan,tasks=sorted(trace,key=lambda r:(r['start_h'],r['id'])),resources=resources,
        onsite_person_hours=sum(r['person_hours'] for r in trace if r['site']),
        factory_person_hours=sum(r['person_hours'] for r in trace if r['location']=='factory'),
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
