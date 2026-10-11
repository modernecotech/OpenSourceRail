"""Interacting capacity/route queues with mobility classes and timed outages.

Capacity and traversal time are declared scenario inputs. This is a flow model,
without crowd interaction, smoke, heat, or authority-approved evacuation limits.
"""
from collections import defaultdict
import heapq
import math
from engineering.industrialisation.common import finite, fingerprint


def simulate(nodes,edges,cohorts,*,duration_s=600.,dt_s=1.,outages=(),clearance_limit_s=None):
    dt=finite(dt_s,'station step',.001);duration=finite(duration_s,'station duration',dt)
    if duration/dt>100000:raise ValueError('station step budget exceeded')
    ids={n['id'] for n in nodes};exits={n['id'] for n in nodes if n.get('exit')}
    if len(ids)!=len(nodes) or not exits:raise ValueError('unique station nodes and safe destination required')
    edge_ids={e['id'] for e in edges}
    if len(edge_ids)!=len(edges):raise ValueError('duplicate station edge')
    for e in edges:
        if e['from'] not in ids or e['to'] not in ids or e['from']==e['to']:raise ValueError('invalid station edge')
        finite(e['capacity_people_s'],'edge capacity',0.);finite(e['travel_s'],'edge traversal',dt)
    if any(o['edge'] not in edge_ids or not 0<=o['start_s']<o['end_s'] for o in outages):raise ValueError('invalid outage')
    groups={c['id']:c for c in cohorts};queues=defaultdict(float);completed=defaultdict(float);transit=[];history=[];total=0.
    if len(groups)!=len(cohorts):raise ValueError('duplicate cohort')
    for c in cohorts:
        if c['node'] not in ids:raise ValueError('cohort outside station')
        count=finite(c['people'],'cohort count',0.);queues[c['node'],c['id']]+=count;total+=count
    def route(node,cohort,active):
        heap=[(0.,node,None)];seen=set()
        while heap:
            cost,n,first=heapq.heappop(heap)
            if n in seen:continue
            seen.add(n)
            if n in exits:return first
            for e in active:
                if e['from']==n and cohort['mobility'] in e['mobility'] and e['capacity_people_s']>0:
                    heapq.heappush(heap,(cost+e['travel_s'],e['to'],first or e['id']))
        return None
    finish=None;max_unroutable=0.
    for step in range(math.ceil(duration/dt)+1):
        t=step*dt;pending=[]
        for arrival,node,group,count in transit:
            if arrival<=t+1e-9:queues[node,group]+=count
            else:pending.append((arrival,node,group,count))
        transit=pending
        for (node,group),count in list(queues.items()):
            if node in exits:completed[group]+=count;queues[node,group]=0.
        remaining=sum(queues.values())+sum(r[3] for r in transit)
        residual=total-remaining-sum(completed.values())
        if abs(residual)>1e-7*max(1.,total):raise ValueError('station passenger conservation failed')
        active=[e for e in edges if not any(o['edge']==e['id'] and o['start_s']<=t<o['end_s'] for o in outages)]
        requests=defaultdict(list);unroutable=0.
        for (node,group),count in queues.items():
            if count<=1e-9:continue
            choice=route(node,groups[group],active)
            if choice is None:unroutable+=count
            else:requests[choice].append((node,group,count))
        max_unroutable=max(max_unroutable,unroutable)
        history.append(dict(time_s=t,queued_people=sum(queues.values()),in_transit_people=sum(r[3] for r in transit),completed_people=sum(completed.values()),unroutable_people=unroutable,conservation_residual_people=residual))
        if remaining<=1e-7:
            finish=t;break
        if step==math.ceil(duration/dt):break
        for e in active:
            req=requests[e['id']];demand=sum(r[2] for r in req);factor=min(1.,e['capacity_people_s']*dt/demand) if demand else 0.
            for node,group,count in req:
                flow=count*factor;queues[node,group]-=flow;transit.append((t+math.ceil(e['travel_s']/dt)*dt,e['to'],group,flow))
    return dict(schema='osr-station-interacting-flow/1',scenario_sha256=fingerprint(dict(nodes=nodes,edges=edges,cohorts=cohorts,outages=list(outages))),
        history=history,clearance_time_s=finish,max_unroutable_people=max_unroutable,completed_by_cohort=dict(completed),
        numerical_clearance_completed=finish is not None,within_declared_clearance_limit=None if clearance_limit_s is None else finish is not None and finish<=finite(clearance_limit_s,'clearance limit',0.),
        fire_tenability_accepted=False,physical_validation=False,engineering_released=False,
        open_domains=['measured inflow and boarding dwell','crowd interaction','smoke/heat/visibility','lift rescue and assisted egress','emergency lighting and responder counterflow','authority limits'])
