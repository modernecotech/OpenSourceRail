"""Reviewable alignment hypotheses; original source maps remain immutable.

Shorter polylines do not establish road ownership, constructability, safe curves,
accessibility or quieter operation. All changed corridors carry explicit risk.
"""
from bisect import bisect_right
from copy import deepcopy
from math import asin, atan2, cos, hypot, isclose, isfinite, pi, sin, sqrt
from pathlib import Path

from engineering.station_rail import ROOT
from engineering.station_rail.common import digest, identity

PRODUCER='engineering/outline/city_alignment.py'
R=6371008.8
FLAGS=dict(physical_accepted=False,engineering_accepted=False,manufacturing_release=False,
    operating_release=False,movement_authority=False,selected_reference_changed=False)
DEFAULTS=dict(version='CITY-ALIGNMENT-1',maximum_chord_deviation_m=25.,minimum_saving_m=1.,
    minimum_relative_saving=.005,maximum_added_walk_m=500.,walk_detour_factor=1.4,
    row_width_m=20.,square_scale=.75,corner_radius_m=200.,lateral_acceleration_m_s2=.5,
    corner_samples=12,unverified_square_crossing_fraction=.05)


def distance(a,b):
    lat1,lat2=a[1]*pi/180,b[1]*pi/180;dl=(b[0]-a[0])*pi/180;dp=lat2-lat1
    return 2*R*asin(min(1.,sqrt(sin(dp/2)**2+cos(lat1)*cos(lat2)*sin(dl/2)**2)))


def chainages(points):
    result=[0.]
    for a,b in zip(points,points[1:]):result.append(result[-1]+distance(a,b))
    return result


def _frame(points):
    lon=sum(x[0] for x in points)/len(points);lat=sum(x[1] for x in points)/len(points);scale=cos(lat*pi/180)
    if scale<.01:raise ValueError('Polar alignment needs its own projection')
    def xy(p):return ((p[0]-lon)*pi/180*R*scale,(p[1]-lat)*pi/180*R)
    def ll(p):return [lon+p[0]/(R*scale)*180/pi,lat+p[1]/R*180/pi]
    return xy,ll


def _projection(point,a,b):
    dx=b[0]-a[0];dy=b[1]-a[1];den=dx*dx+dy*dy
    t=max(0.,min(1.,((point[0]-a[0])*dx+(point[1]-a[1])*dy)/den)) if den else 0.
    z=(a[0]+t*dx,a[1]+t*dy)
    return hypot(point[0]-z[0],point[1]-z[1]),t,z


def _at(points,chain,s):
    if s<=0:return list(points[0])
    if s>=chain[-1]:return list(points[-1])
    i=bisect_right(chain,s)-1;t=(s-chain[i])/(chain[i+1]-chain[i])
    return [points[i][k]+t*(points[i+1][k]-points[i][k]) for k in (0,1)]


def _runs(city,line):
    rows=sorted((deepcopy(z) for z in city.get('civil_segments',[]) if z['line_id']==line['line_id']),key=lambda z:z['from_m'])
    if not rows:return [dict(line_id=line['line_id'],**{'class':'elevated'},from_m=0.,to_m=line['route_m'],source_chainage_basis='explicit missing-class elevated assumption')]
    merged=[]
    for row in rows:
        if merged and merged[-1]['class']==row['class'] and isclose(merged[-1]['to_m'],row['from_m'],abs_tol=.02):merged[-1]['to_m']=row['to_m']
        else:merged.append(row)
    return merged


def _legs(line):
    stops=line['stops'];result=[]
    for a,b in zip(stops,stops[1:]):result.append(dict(from_stop=a['id'],to_stop=b['id'],distance_m=b['chainage_m']-a['chainage_m'],closing_leg=False))
    if line['shape']=='ring':result.append(dict(from_stop=stops[-1]['id'],to_stop=stops[0]['id'],distance_m=line['route_m']-stops[-1]['chainage_m']+stops[0]['chainage_m'],closing_leg=True))
    line['legs']=result;line['operational_route_m']=line['route_m'] if line['shape']=='ring' else stops[-1]['chainage_m']-stops[0]['chainage_m']


def _straighten(city,line,p):
    points=line['coordinates'];old=chainages(points)
    if not isclose(old[-1],line['route_m'],rel_tol=1e-8,abs_tol=.05):raise ValueError('Mapped coordinate length and chainages disagree')
    runs=_runs(city,line);anchors=sorted(set([0.,old[-1]]+[s['chainage_m'] for s in line['stops']]+[z[k] for z in runs for k in ('from_m','to_m')]))
    xy,_=_frame(points);new_points=[];new_anchor=[0.];changed=0.;removed=0
    for lo,hi in zip(anchors,anchors[1:]):
        part=[_at(points,old,lo)]+[list(points[i]) for i in range(bisect_right(old,lo),bisect_right(old,hi)) if old[i]<hi]+[_at(points,old,hi)]
        shape=next(z['class'] for z in runs if z['from_m']-.01<=(lo+hi)/2<=z['to_m']+.01)
        a,b=xy(part[0]),xy(part[-1]);deviation=max(_projection(xy(z),a,b)[0] for z in part)
        straight=distance(part[0],part[-1]);saving=hi-lo-straight
        use=(shape not in ('bridge','tunnel') and deviation<=p['maximum_chord_deviation_m'] and saving>=p['minimum_saving_m'] and saving/(hi-lo)>=p['minimum_relative_saving'])
        selected=[part[0],part[-1]] if use else part
        if use:changed+=straight;removed+=len(part)-2
        if new_points:new_points.extend(selected[1:])
        else:new_points.extend(selected)
        new_anchor.append(chainages(selected)[-1]+new_anchor[-1])
    new_chain=chainages(new_points)
    def mapped(s):
        if s>=anchors[-1]:return new_anchor[-1]
        i=max(0,bisect_right(anchors,s)-1);t=(s-anchors[i])/(anchors[i+1]-anchors[i])
        return new_anchor[i]+t*(new_anchor[i+1]-new_anchor[i])
    output=deepcopy(line);output.update(coordinates=new_points,coordinate_chainages_m=new_chain,route_m=new_chain[-1])
    for stop in output['stops']:stop['chainage_m']=mapped(stop['chainage_m'])
    _legs(output)
    revised_runs=[{**z,'from_m':mapped(z['from_m']),'to_m':mapped(z['to_m']),'source_chainage_basis':'anchor-preserving alignment revision; exact class-boundary coordinates retained'} for z in runs]
    return output,revised_runs,dict(changed_route_m=changed,removed_nonanchor_vertices=removed,length_saved_m=line['route_m']-output['route_m'],maximum_added_walk_m=0.,additional_access_walkway_m=0.,original_stop_coordinates_retained=True)


def _square(city,line,p,mandatory):
    xy,ll=_frame(line['coordinates']);oldxy=[xy(z) for z in line['coordinates']]
    xs=[z[0] for z in oldxy];ys=[z[1] for z in oldxy];cx=(min(xs)+max(xs))/2;cy=(min(ys)+max(ys))/2
    w=(max(xs)-min(xs))*p['square_scale'];h=(max(ys)-min(ys))*p['square_scale']
    if min(w,h)<20:raise ValueError('Ring envelope too small for rounded rectangular hypothesis')
    r=min(p['corner_radius_m'],w/4,h/4);xmin,xmax=cx-w/2,cx+w/2;ymin,ymax=cy-h/2,cy+h/2
    pts=[(cx,ymax),(xmax-r,ymax)]
    for center,start,end,nextpoint in [((xmax-r,ymax-r),90,0,(xmax,ymin+r)),((xmax-r,ymin+r),0,-90,(xmin+r,ymin)),((xmin+r,ymin+r),-90,-180,(xmin,ymax-r)),((xmin+r,ymax-r),180,90,(cx,ymax))]:
        for j in range(1,int(p['corner_samples'])+1):
            angle=(start+(end-start)*j/p['corner_samples'])*pi/180;pts.append((center[0]+r*cos(angle),center[1]+r*sin(angle)))
        pts.append(nextpoint)
    coords=[ll(z) for z in pts];chain=chainages(coords)
    def nearest(point):
        best=None
        for i,(a,b) in enumerate(zip(pts,pts[1:])):
            dist,t,z=_projection(point,a,b)
            if best is None or dist<best[0]:best=(dist,chain[i]+t*(chain[i+1]-chain[i]),ll(z))
        return best
    stops=[]
    for i,z in enumerate(((cx,ymax),(xmax,cy),(cx,ymin),(xmin,cy))):
        _,s,llz=nearest(z);stops.append(dict(id=line['line_id']+'-square-edge-'+str(i),chainage_m=s,lon=llz[0],lat=llz[1],dwell_s=max(t.get('dwell_s',35.) for t in line['stops'])))
    for old in line['stops']:
        if old['id'] in mandatory:
            _,s,llz=nearest(xy([old['lon'],old['lat']]))
            stops.append({**old,'chainage_m':s,'lon':llz[0],'lat':llz[1],'original_lon':old['lon'],'original_lat':old['lat']})
    stops.sort(key=lambda z:(z['chainage_m'],z['id']))
    coverage=[]
    for old in line['stops']:
        best=min(stops,key=lambda z:distance([old['lon'],old['lat']],[z['lon'],z['lat']]))
        walk=distance([old['lon'],old['lat']],[best['lon'],best['lat']])*p['walk_detour_factor']
        coverage.append(dict(original_stop_id=old['id'],proposed_stop_id=best['id'],added_walk_m=walk,walk_network_verified=False))
    output=deepcopy(line);output.update(coordinates=coords,coordinate_chainages_m=chain,route_m=chain[-1],stops=stops,
        design_speed_cap_m_s=sqrt(p['lateral_acceleration_m_s2']*r),
        curve_speed_basis='Conservative whole-line cap from explicit radius/lateral-acceleration hypothesis; no dynamics/noise qualification',minimum_turn_radius_m=r,lateral_acceleration_m_s2=p['lateral_acceleration_m_s2'])
    _legs(output)
    # A radically different path cannot inherit surveyed crossing/soil claims.
    runs=[dict(line_id=line['line_id'],**{'class':'elevated'},from_m=0.,to_m=chain[-1],source_chainage_basis='new alignment elevated planning assumption; crossing risk independently reserved')]
    return output,runs,dict(changed_route_m=chain[-1],length_saved_m=line['route_m']-chain[-1],maximum_added_walk_m=max(z['added_walk_m'] for z in coverage),
        additional_access_walkway_m=sum(z['added_walk_m'] for z in coverage),coverage=coverage,original_stop_coordinates_retained=False,
        unverified_bridge_route_m_hypothesis=max(sum(z['to_m']-z['from_m'] for z in _runs(city,line) if z['class']=='bridge'),p['unverified_square_crossing_fraction']*chain[-1]),
        minimum_radius_m=r,corner_speed_cap_m_s=output['design_speed_cap_m_s'],instant_right_angle_turns=False,quieter_operation_demonstrated=False)


def _geo(city):
    return dict(type='FeatureCollection',features=[dict(type='Feature',properties=dict(line_id=z['line_id'],shape=z['shape'],outline_hypothesis_only=True),geometry=dict(type='LineString',coordinates=z['coordinates'])) for z in city['lines']])


def propose(city_input,root=ROOT,policy=None):
    """Return original, anchored detour revision, and rounded-ring alternatives."""
    root=Path(root);p=deepcopy(DEFAULTS);over=(policy or {}).get('alignment',{})
    if set(over)-set(p):raise ValueError('Unknown alignment policy key')
    p.update(over)
    for k,v in p.items():
        if type(v) in (int,float) and (not isfinite(v) or v<=0):raise ValueError('Positive finite alignment assumptions required')
    if not 0<p['square_scale']<=1 or p['walk_detour_factor']<1 or int(p['corner_samples'])!=p['corner_samples'] or p['corner_samples']<4:raise ValueError('Invalid rounded geometry/access assumptions')
    original=deepcopy(city_input)
    if original.get('input_id')!=identity({k:v for k,v in original.items() if k!='input_id'}):raise ValueError('Original city input identity differs')
    source={**original.get('source_sha256',{}),PRODUCER:digest(root/PRODUCER)}
    for line in original['lines']:
        if len(line.get('coordinates',[]))<2:raise ValueError('Exact mapped route coordinates required')
    variants=[dict(kind='original',city_input=deepcopy(original),alignment_id=identity(dict(kind='original',city_input_id=original['input_id'])),geometry_geojson=_geo(original),selection_eligibility=dict(status='retained-original',access_screen='unchanged'),risk_quantities=dict(changed_route_m=0.,additional_row_area_m2=0.),**FLAGS)]
    mandatory={x for z in original.get('interchanges',[]) for x in z.get('platforms',[])}
    kinds=['anchor-preserving-chord-research']+(['rounded-four-edge-ring-research'] if any(z['shape']=='ring' for z in original['lines']) else [])
    for kind in kinds:
        candidate=deepcopy(original);newlines=[];segments=[];details=[]
        for line in original['lines']:
            if kind=='rounded-four-edge-ring-research' and line['shape']=='ring':out,runs,detail=_square(original,line,p,mandatory)
            elif kind=='anchor-preserving-chord-research':out,runs,detail=_straighten(original,line,p)
            else:out,runs,detail=deepcopy(line),_runs(original,line),dict(changed_route_m=0.,length_saved_m=0.,maximum_added_walk_m=0.,additional_access_walkway_m=0.,original_stop_coordinates_retained=True)
            newlines.append(out);segments.extend(runs);details.append(dict(line_id=line['line_id'],**detail))
        changed=sum(z['changed_route_m'] for z in details);walk=max(z['maximum_added_walk_m'] for z in details);coverage=[z for d in details for z in d.get('coverage',[])]
        fail=[z['original_stop_id'] for z in coverage if z['added_walk_m']>p['maximum_added_walk_m']]
        risk=dict(changed_route_m=changed,additional_row_area_m2=changed*p['row_width_m'],
            additional_access_walkway_m=sum(z['additional_access_walkway_m'] for z in details),
            unverified_bridge_route_m_hypothesis=sum(z.get('unverified_bridge_route_m_hypothesis',0.) for z in details),
            route_clearance_unknown=True,crossing_reassessment_required=changed>0)
        eligibility=dict(status='hold' if fail else 'eligible-outline-hypothesis',access_screen='fail' if fail else 'pass',
            maximum_added_walk_m=walk,maximum_allowed_walk_m=p['maximum_added_walk_m'],unserved_original_stop_ids=fail,
            mandatory_transfer_access_preserved=not any(z['original_stop_id'] in mandatory for z in coverage if z['added_walk_m']>p['maximum_added_walk_m']),
            actual_walk_network_verified=False,physical_clearance_approval=False)
        hypothesis=dict(kind=kind,parent_input_id=original['input_id'],policy=p,lines=details,risk_quantities=risk,selection_eligibility=eligibility,
            length_saved_m=sum(z['length_saved_m'] for z in details),strict_cost_advantage_established=False,site_and_row_verified=False)
        candidate.pop('input_id');candidate.update(lines=newlines,civil_segments=segments,source_sha256=source,alignment_hypothesis=hypothesis,ancestry=dict(parent_input_id=original['input_id'],revision_operator=kind),**FLAGS)
        candidate['input_id']=identity(candidate)
        variants.append(dict(kind=kind,city_input=candidate,alignment_id=identity(dict(city_input_id=candidate['input_id'],hypothesis=hypothesis)),
            ancestry=candidate['ancestry'],geometry_geojson=_geo(candidate),risk_quantities=risk,selection_eligibility=eligibility,**FLAGS))
    result=dict(schema='osr-city-alignment-portfolio/1',original_city_input_id=original['input_id'],variants=variants,source_sha256=source,policy=p,original_maps_modified=False,native_solvers=0,**FLAGS)
    result['evaluation_id']=identity(result);return result
