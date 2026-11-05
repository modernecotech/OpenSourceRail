"""Source-bound mapped city inputs for conditional outline calculations."""
from copy import deepcopy
from pathlib import Path
import gzip
import json
import math

from engineering.station_rail import ROOT
from engineering.station_rail.common import digest,identity
from engineering.development_baseline import planning

PRODUCER='engineering/outline/city_inputs.py'
BASE='docs/design-engine/current/planning'
FLAGS=dict(physical_accepted=False,engineering_accepted=False,manufacturing_release=False,
    operating_release=False,selected_reference_changed=False,movement_authority=False)
_LOADED={PRODUCER:digest(__file__),'engineering/development_baseline/planning.py':digest(planning.__file__)}


def prepare(root=ROOT):
    root=Path(root);index=json.loads((root/BASE/'index.json').read_bytes())
    manifest=json.loads((root/BASE/'manifest.json').read_bytes())
    catalogue=json.loads((root/'docs/design-engine/current/cities.json').read_bytes())
    if (index['selection_id']!=catalogue['selection_id'] or index['city_count']!=len(index['cities'])
            or index['city_count']!=catalogue['city_count']):
        raise ValueError('Current source-bound city planning catalogue required')
    if manifest['files_sha256']['index.json']!=digest(root/BASE/'index.json'):
        raise ValueError('Planning index differs from its manifest')
    geo={r['slug']:r for r in catalogue['cities']};rows=[]
    for row in index['cities']:
        g=geo[row['city']]
        rows.append(dict(slug=row['city'],name=row['label'],country=row['country'],
            plan_path=BASE+'/'+row['plan'],plan_sha256=manifest['files_sha256'][row['plan']],
            geography_path=g['geography_path'],route_geography_path=g['route_geography_path'],
            revision_sha256=row['revision_sha256']))
    sources={**_LOADED,**{n:digest(root/n) for n in
        (BASE+'/index.json',BASE+'/manifest.json','docs/design-engine/current/cities.json')}}
    return dict(rows=rows,by_slug={r['slug']:r for r in rows},selection_id=index['selection_id'],
        reference_candidate_ids=index['selected_candidate'],source_sha256=sources)


def catalogue(root=ROOT):return prepare(root)['rows']


def load(value,root=ROOT,*,context=None):
    root=Path(root);context=prepare(root) if context is None else context
    row=value if isinstance(value,dict) else context['by_slug'].get(value)
    if row is None or row.get('slug') not in context['by_slug'] or row!=context['by_slug'][row['slug']]:
        raise ValueError('City must be a current catalogue row or slug')
    sources=dict(context['source_sha256'])
    for name,sha in sources.items():
        if digest(root/name)!=sha:raise ValueError('City planning context source changed: '+name)
    raw=(root/row['plan_path']).read_bytes()
    if digest(root/row['plan_path'])!=row['plan_sha256']:raise ValueError('City planning payload differs')
    plan=json.loads(gzip.decompress(raw));g=json.loads((root/row['geography_path']).read_bytes())
    if plan['revision_sha256']!=planning.digest_json({k:v for k,v in plan.items() if k!='revision_sha256'}):
        raise ValueError('City planning revision differs')
    if plan['selection_id']!=context['selection_id']:raise ValueError('Mixed planning selection')
    for name,sha in plan['source_sha256'].items():
        if digest(root/name)!=sha:raise ValueError('City geographic source changed: '+name)
        if name in sources and sources[name]!=sha:raise ValueError('Mixed city source epochs')
        sources[name]=sha
    sources[row['plan_path']]=row['plan_sha256']
    old={r['name']:r for r in g['lines']};lines=[];scales={}
    for line in plan['lines']:
        base=old[line['id']];shape=base.get('shape')
        if shape not in ('radial','ring'):raise ValueError('Explicit radial/ring topology required')
        stops=deepcopy(line['stops']);legs=[]
        if len(stops)<2:raise ValueError('At least two stops required')
        for a,b in zip(stops,stops[1:]):
            gap=b['chainage_m']-a['chainage_m']
            if not math.isfinite(gap) or gap<=0:raise ValueError('Positive ordered stop gaps required')
            legs.append(dict(from_stop=a['id'],to_stop=b['id'],distance_m=gap,closing_leg=False))
        if shape=='ring':
            if line['coordinates'][0]!=line['coordinates'][-1]:raise ValueError('Ring geometry is not closed')
            gap=line['length_m']-stops[-1]['chainage_m']+stops[0]['chainage_m']
            if gap<=0:raise ValueError('Positive ring closing leg required')
            legs.append(dict(from_stop=stops[-1]['id'],to_stop=stops[0]['id'],distance_m=gap,closing_leg=True))
        scales[line['id']]=line['length_m']/base['length_m']
        coordinates=[point[:2] for point in line['coordinates']]
        lines.append(dict(line_id=line['id'],shape=shape,route_m=line['length_m'],
            coordinates=coordinates,coordinate_chainages_m=planning._chainages(coordinates),
            operational_route_m=math.fsum(r['distance_m'] for r in legs),stops=stops,legs=legs,
            source_schedule=deepcopy(base.get('service',{}).get('schedule',[])),
            retained_capacity_targets=deepcopy(base.get('capacity')),
            retained_service_and_capacity_are_current_demand=False,
            geometry_reference=dict(path=row['route_geography_path'],line=line['id']),
            unserved_radial_tail_m=line['length_m']-math.fsum(r['distance_m'] for r in legs) if shape=='radial' else 0.))
    civil=[]
    for segment in g.get('civil_segments',[]):
        scale=scales[segment['line']]
        civil.append(dict(line_id=segment['line'],**{'class':segment['class']},
            from_m=segment['from_station_m']*scale,to_m=segment['to_station_m']*scale,
            source_from_m=segment['from_station_m'],source_to_m=segment['to_station_m'],chainage_scale=scale))
    result=dict(schema='osr-city-outline-input/1',city=dict(slug=row['slug'],name=g['name'],country=row['country'],
        population_retained_unaccepted=g['city'].get('population')),selection_id=context['selection_id'],
        reference_candidate_ids=deepcopy(context['reference_candidate_ids']),planning_revision_sha256=plan['revision_sha256'],
        lines=lines,interchanges=deepcopy(g.get('interchanges',[])),civil_segments=civil,od=deepcopy(plan.get('od',[])),
        demand_scope='Empty OD means no surveyed demand. Retained capacity/schedule/population are unaccepted context, not forecasts.',
        source_sha256=dict(sorted(sources.items())),**FLAGS)
    result['input_id']=identity(result);return result
