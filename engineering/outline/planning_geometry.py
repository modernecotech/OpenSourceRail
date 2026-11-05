"""Bounded explicit geometry edits for unaccepted priced planning revisions."""
from bisect import bisect_right
from copy import deepcopy
from math import isfinite

from engineering.development_baseline import planning

PRODUCER='engineering/outline/planning_geometry.py'


def number(value,name,low=0.,high=1_000_000.):
    if type(value) not in (int,float) or not isfinite(value) or not low<=value<=high:
        raise planning.PlanningError('Bounded finite '+name+' required')
    return float(value)


def route(coordinates,shape):
    if shape not in ('radial','ring') or not isinstance(coordinates,list) or not 2<=len(coordinates)<=100_000:
        raise planning.PlanningError('Explicit bounded radial/ring route required')
    for point in coordinates:
        if not isinstance(point,list) or len(point)!=2:
            raise planning.PlanningError('Two-coordinate longitude/latitude points required')
        number(point[0],'longitude',-180,180);number(point[1],'latitude',-90,90)
    chain=planning._chainages(coordinates)
    number(chain[-1],'route length',1,1_000_000)
    if shape=='ring' and coordinates[0]!=coordinates[-1]:
        raise planning.PlanningError('Ring route must remain explicitly closed')
    return chain


def point(coordinates,chain,at):
    at=number(at,'stop chainage',0,chain[-1]);i=min(len(chain)-2,max(0,bisect_right(chain,at)-1))
    fraction=(at-chain[i])/(chain[i+1]-chain[i]) if chain[i+1]>chain[i] else 0.
    return [coordinates[i][k]+fraction*(coordinates[i+1][k]-coordinates[i][k]) for k in (0,1)]


def replace_line(line,edit):
    required={'kind','line','coordinates','stops','shape','design_speed_cap_m_s','reason'}
    if set(edit)!=required or edit['kind']!='replace-line-geometry' or edit['line']!=line['id']:
        raise planning.PlanningError('Typed explicit route replacement fields required')
    if not isinstance(edit['reason'],str) or not edit['reason'].strip() or len(edit['reason'])>1000:
        raise planning.PlanningError('Bounded named route-revision reason required')
    chain=route(edit['coordinates'],edit['shape'])
    cap=number(edit['design_speed_cap_m_s'],'declared route speed cap',.1,80.)
    if not isinstance(edit['stops'],list) or not 2<=len(edit['stops'])<=10_000:
        raise planning.PlanningError('Explicit replacement stop positions required')
    seen=set();stops=[];previous=-1
    for stop in edit['stops']:
        if not isinstance(stop,dict) or set(stop)!={'id','chainage_m','dwell_s'}:
            raise planning.PlanningError('Replacement stops need identity, explicit chainage and dwell')
        name=stop['id']
        if not isinstance(name,str) or not name or len(name)>150 or name in seen:
            raise planning.PlanningError('Unique bounded replacement stop identities required')
        seen.add(name);at=number(stop['chainage_m'],'replacement stop chainage',0,chain[-1])
        if at<=previous:raise planning.PlanningError('Replacement stops must be in route order')
        previous=at;lon,lat=point(edit['coordinates'],chain,at)
        stops.append(dict(id=name,chainage_m=at,dwell_s=number(stop['dwell_s'],'dwell',10,3600),
            lon=lon,lat=lat,access_and_transfer_reassessment_required=True))
    result=deepcopy(line)
    result.update(coordinates=deepcopy(edit['coordinates']),length_m=chain[-1],shape=edit['shape'],
        stops=stops,design_speed_cap_m_s=cap,route_replacement_reason=edit['reason'].strip(),
        civil_crossings_access_and_curvature_reassessment_required=True)
    return result


def apply_edits(base,edits,actor):
    if not isinstance(actor,str) or not actor.strip() or len(actor)>150:
        raise planning.PlanningError('Named planning author required')
    if not isinstance(edits,list) or len(edits)>1000:raise planning.PlanningError('Bounded edit list required')
    value=deepcopy(base)
    for edit in edits:
        if not isinstance(edit,dict):raise planning.PlanningError('Typed planning edit required')
        if edit.get('kind')=='replace-line-geometry':
            index=next((i for i,x in enumerate(value['lines']) if x['id']==edit.get('line')),None)
            if index is None:raise planning.PlanningError('Unknown replacement line')
            value['lines'][index]=replace_line(value['lines'][index],edit)
            value['revision_sha256']=planning.digest_json({k:v for k,v in value.items() if k!='revision_sha256'})
            planning._validate_plan(value,base['city'])
        else:
            selected=next((x for x in value['lines'] if x['id']==edit.get('line')),None)
            if edit.get('kind')=='straighten-line' and selected and selected.get('shape')=='ring':
                raise planning.PlanningError('A ring needs an explicit closed geometry replacement')
            value=planning._apply_edits(value,[edit],actor)
    value.update(revision=base['revision']+1,parent_revision_sha256=base['revision_sha256'],
        actor=actor.strip(),changes=deepcopy(edits))
    value['revision_sha256']=planning.digest_json({k:v for k,v in value.items() if k!='revision_sha256'})
    return planning._validate_plan(value,base['city'])
