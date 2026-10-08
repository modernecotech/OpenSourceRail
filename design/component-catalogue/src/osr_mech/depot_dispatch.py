"""Conflict-aware yard routes, berths, charging slots and repeated departures.

Route resources are explicit track/switch/isolation identities. A planning
storage rectangle cannot provide them or authorise a depot departure.
"""
from .industrialisation import nonnegative


def yard_dispatch(routes,trains,requests,*,horizon_minutes):
    nonnegative(horizon_minutes,'yard horizon')
    by_id={r['id']:r for r in routes}
    if len(by_id)!=len(routes):raise ValueError('distinct depot routes required')
    train_states={row['id']:dict(row) for row in trains}
    if len(train_states)!=len(trains):raise ValueError('distinct yard train identities required')
    occupancy={};rows=[];seen=set();berths={}
    for train in train_states.values():
        if train['berth'] in berths:raise ValueError('two trains cannot occupy one initial storage berth')
        berths[train['berth']]=[dict(train=train['id'],start=0,end=horizon_minutes)]
    for request in sorted(requests,key=lambda r:(r['requested_minute'],r['id'])):
        if request['id'] in seen:raise ValueError('duplicate yard request')
        seen.add(request['id']);route=by_id.get(request['route']);train=train_states.get(request['train'])
        if route is None or train is None:raise ValueError('yard request needs an identified train and surveyed/planning route')
        resources=route['resources'];duration=nonnegative(route['travel_minutes'],'yard travel')
        if duration<=0 or not resources or len(set(resources))!=len(resources):raise ValueError('positive yard travel and distinct route resources required')
        if train['berth']!=route['from_berth']:raise ValueError('train is not at the route origin; no teleportation')
        ready=max(request['requested_minute'],train['ready_minute'],train.get('charge_ready_minute',0))
        clearance=nonnegative(route.get('clearance_minutes',0),'route clearance')
        while True:
            end=ready+duration+clearance
            conflicts=[b for resource in resources for a,b in occupancy.get(resource,[]) if ready<b and a<end]
            if not conflicts:break
            ready=max(conflicts)
        arrival=ready+duration
        if arrival>horizon_minutes:
            rows.append(dict(id=request['id'],served=False,departure_minute=None,reason='yard horizon exceeded'));continue
        if not route.get('to_is_network',False) and any(r['train']!=train['id'] and r['end']>arrival
            for r in berths.get(route['to_berth'],[])):
            rows.append(dict(id=request['id'],served=False,departure_minute=None,reason='destination berth unavailable'));continue
        for interval in berths.get(train['berth'],[]):
            if interval['train']==train['id'] and interval['end']==horizon_minutes:interval['end']=ready
        for resource in resources:occupancy.setdefault(resource,[]).append((ready,arrival+clearance))
        train.update(berth=route['to_berth'],ready_minute=arrival)
        if not route.get('to_is_network',False):berths.setdefault(route['to_berth'],[]).append(dict(train=train['id'],start=arrival,end=horizon_minutes))
        rows.append(dict(id=request['id'],train=train['id'],route=route['id'],served=True,departure_minute=ready,
            arrival_minute=arrival,queue_minutes=ready-request['requested_minute'],resources=resources,
            movement_authority_granted=False))
    return dict(departures=rows,final_train_states=train_states,resource_reservations=occupancy,berth_occupancy=berths,
        geometry_and_interlocking_accepted=False,endpoint_dispatch_replaced=False,operational_release=False)
