"""Extract a source-authenticated mapped corridor, without importing old prices.

Coordinates, stops and their geographic ancestry are retained. The old city's
vehicle, capacities, schedule and economics are not the selected detailed train.
"""
from copy import deepcopy
from math import isfinite
from pathlib import Path

from engineering.station_rail import ROOT
from engineering.station_rail.common import identity, digest
from engineering.outline import city_inputs, planning_geometry

FLAGS=dict(physical_accepted=False,engineering_accepted=False,manufacturing_release=False,
           operating_release=False,selected_reference_changed=False,movement_authority=False)
SOURCES=('engineering/railway_project/route.py','engineering/outline/city_inputs.py',
         'engineering/outline/planning_geometry.py','engineering/development_baseline/planning.py')


def from_catalogue(city_slug,line_id,first_stop_id,last_stop_id,*,wrap_ring=False,root=ROOT):
    """Public entry loads the authoritative city; no client-resealed input used."""
    city=city_inputs.load(city_slug,root=Path(root))
    return _slice(city,line_id,first_stop_id,last_stop_id,wrap_ring=wrap_ring,root=root)


def _slice(city,line_id,first_stop_id,last_stop_id,*,wrap_ring=False,root=ROOT):
    if city.get('schema')!='osr-city-outline-input/1' or city.get('input_id')!=identity({k:v for k,v in city.items() if k!='input_id'}):
        raise ValueError('Sealed authoritative mapped city required')
    if type(wrap_ring) is not bool:raise ValueError('Explicit ring direction required')
    lines=[r for r in city['lines'] if r['line_id']==line_id]
    if len(lines)!=1:raise ValueError('Known unique line required')
    line=lines[0];stops=line['stops'];by_id={r['id']:r for r in stops}
    if len(by_id)!=len(stops) or first_stop_id not in by_id or last_stop_id not in by_id:
        raise ValueError('Known unique corridor stop identities required')
    if first_stop_id==last_stop_id:raise ValueError('Use distinct corridor endpoints')
    chain=planning_geometry.route(line['coordinates'],line['shape']);length=chain[-1]
    if abs(length-line['route_m'])>1e-6:raise ValueError('Source route chainage differs')
    start=by_id[first_stop_id]['chainage_m'];end=by_id[last_stop_id]['chainage_m']
    if not all(type(v) in (int,float) and isfinite(v) and 0<=v<=length for v in (start,end)):
        raise ValueError('Finite source stop chainages required')
    if wrap_ring:
        if line['shape']!='ring' or end>=start:raise ValueError('Explicit wrap is only for a closing ring arc')
        end+=length
    elif end<=start:raise ValueError('Corridor endpoints must follow route order')
    # Slicing interpolates only endpoint positions on the existing polyline.
    # Internal points and all in-scope stops remain exactly source-defined.
    shifted=[(s,deepcopy(p)) for s,p in zip(chain,line['coordinates'])]
    if wrap_ring:shifted+=[(s+length,deepcopy(p)) for s,p in zip(chain[1:],line['coordinates'][1:])]
    def point(at):return planning_geometry.point(line['coordinates'],chain,at-length if at>length else at)
    coordinates=[point(start)]+[p for s,p in shifted if start<s<end]+[point(end)]
    # Repeated zero-length source vertices add no route, remove only exact repeats.
    coordinates=[p for i,p in enumerate(coordinates) if i==0 or p!=coordinates[i-1]]
    local_chain=planning_geometry.route(coordinates,'radial')
    selected=[]
    for stop in stops:
        at=stop['chainage_m']
        if wrap_ring and at<start:at+=length
        if start<=at<=end:
            item=deepcopy(stop);item['source_chainage_m']=stop['chainage_m'];item['chainage_m']=at-start
            selected.append(item)
    selected.sort(key=lambda s:s['chainage_m'])
    if len(selected)<2 or selected[0]['id']!=first_stop_id or selected[-1]['id']!=last_stop_id:
        raise ValueError('Corridor must retain ordered endpoint stops')
    # Geographic projection and source station chainage share the same metric.
    residual=abs(local_chain[-1]-(end-start))
    if residual>1e-3:raise ValueError('Corridor metric changed during clipping')
    definition=dict(schema='osr-mapped-corridor-geometry/1',city_slug=city['city']['slug'],
        line_id=line_id,coordinates=coordinates,coordinate_reference='WGS84 longitude/latitude degrees',
        shape='radial',source_shape=line['shape'],wrap_ring=wrap_ring,
        stations=[dict(id=s['id'],longitude=s['lon'],latitude=s['lat'],chainage_m=s['chainage_m']) for s in selected])
    sources=deepcopy(city['source_sha256'])
    for n in SOURCES:
        h=digest(Path(root)/n)
        if n in sources and sources[n]!=h:raise ValueError('Mixed source epochs')
        sources[n]=h
    cid=identity(definition)
    value=dict(schema='osr-mapped-corridor-input/1',corridor_geometry_id=cid,definition=definition,city=deepcopy(city['city']),
        source_city_input_id=city['input_id'],source_planning_revision=city['planning_revision_sha256'],
        geometry_reference=deepcopy(line['geometry_reference']),source_stops=selected,
        route_m=local_chain[-1],station_count=len(selected),
        legs=[dict(from_stop=a['id'],to_stop=b['id'],distance_m=b['chainage_m']-a['chainage_m']) for a,b in zip(selected,selected[1:])],
        metric_residual_m=residual,source_reference_candidate_ids=deepcopy(city['reference_candidate_ids']),
        detailed_vehicle_selected=False,legacy_capacity_schedule_and_price_imported=False,
        site_evidence=dict(demand='unverified; set explicit project requirement',ground='unknown; explicit design cases required',
            grade='unknown; explicit grade envelope or authenticated profile required',utilities='unknown; scoped quantities and allowances required',
            access='source stop markers retained; corridor access and transfers require re-evaluation'),
        source_sha256=sources,**FLAGS)
    value['evaluation_id']=identity(value)
    return value
