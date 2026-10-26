"""Typed component-interface/assembly checks, never product acceptance.

Ports describe declared interfaces in named coordinate/reference frames. No
implicit unit conversion, frame transform, electrical control, load sharing or
part geometry is invented. Evidence/source references still need authentication
by the existing qualification workflow. A matching catalogue label is not proof
that an installed interface can carry its actual duty.
"""
from copy import deepcopy
from hashlib import sha256
from math import isfinite
from pathlib import Path
import json,re
from typing import Literal,TypedDict,Required

Kind=Literal['mechanical','electrical','thermal','spatial','operational','manufacturing','assembly']
KINDS=('mechanical','electrical','thermal','spatial','operational','manufacturing','assembly')
SCHEMA='osr-interface-graph/1'
PRODUCER='engineering/design_search/interface_graph.py'
FLAGS=dict(physical_accepted=False,engineering_accepted=False,configuration_adopted=False,
    manufacturing_release=False,operating_release=False,selected_development_default_changed=False)


class Port(TypedDict,total=False):
    id:Required[str]
    kind:Required[Kind]
    unit:str
    units:dict[str,str]
    frame_id:str
    direction:str
    connector:str
    dofs:list[str]
    demand:dict
    capacity:dict
    ranges:dict
    data_validity:dict


class Component(TypedDict,total=False):
    occurrence_id:Required[str]
    part_id:Required[str]
    component_definition_id:Required[str]
    functions:list[str]
    ports:list[Port]
    stock:dict
    function_evidence:dict


Connection=TypedDict('Connection',{'id':str,'from':list[str],'to':list[str]})


class AssemblyOperation(TypedDict,total=False):
    id:Required[str]
    occurrences:list[str]
    requires:list[str]
    hours:float|None
    data_validity:dict


def identity(value):return sha256((json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False)+'\n').encode()).hexdigest()

def _sha(value):return isinstance(value,str) and re.fullmatch('[0-9a-f]{64}',value) is not None

def _number(value):return type(value) in (int,float) and isfinite(value)

def _names(values):
    result=[v if isinstance(v,str) else v['id'] for v in values]
    if any(not isinstance(n,str) or not n for n in result) or len(result)!=len(set(result)):raise ValueError('Unique explicit function identities required')
    return result


def physical_identity(graph):
    """Interface graph identity is separate from the full physical candidate ID.

    Model capacities, evidence, requirements and assembly order do not change
    physical stock identity. A changed occurrence/component or its connections
    does; the full geometry generator remains authoritative for candidate IDs.
    """
    return identity(dict(components=sorted([dict(occurrence_id=c['occurrence_id'],part_id=c['part_id'],component_definition_id=c['component_definition_id']) for c in graph['components']],key=lambda c:c['occurrence_id']),
        connections=sorted([dict(id=q['id'],source=q['from'],target=q['to']) for q in graph.get('connections',[])],key=lambda c:c['id'])))


def validate_identity(graph):
    if not isinstance(graph,dict) or graph.get('schema')!=SCHEMA or not _sha(graph.get('candidate_id')) or not isinstance(graph.get('requirement_revision'),str) or not graph['requirement_revision']:raise ValueError('Explicit graph schema, physical candidate and requirement revision required')
    value=deepcopy(graph);components=value.get('components')
    if not isinstance(components,list) or not components:raise ValueError('Explicit component occurrences required')
    ids=set();ports={}
    for c in components:
        uid=c.get('occurrence_id')
        if not isinstance(uid,str) or not uid or uid in ids or not c.get('part_id') or not _sha(c.get('component_definition_id')):raise ValueError('Unique occurrence, part and component definition identities required')
        if c.get('candidate_id',value['candidate_id'])!=value['candidate_id']:raise ValueError('Mixed candidate occurrence identities')
        ids.add(uid);_names(c.get('functions',[]));seen=set()
        for p in c.get('ports',[]):
            if not p.get('id') or p['id'] in seen or p.get('kind') not in KINDS:raise ValueError('Unique typed port identity required')
            if p.get('direction') not in ('source','sink','bidirectional',None):raise ValueError('Typed source/sink/bidirectional direction required')
            seen.add(p['id']);ports[uid,p['id']]=p
    seen=set()
    for q in value.get('connections',[]):
        if not q.get('id') or q['id'] in seen:raise ValueError('Unique connection identity required')
        seen.add(q['id'])
        for endpoint in (q.get('from'),q.get('to')):
            if not isinstance(endpoint,(list,tuple)) or len(endpoint)!=2 or tuple(endpoint) not in ports:raise ValueError('Connection references an absent occurrence/port')
    _names(value.get('required_functions',[]))
    if value.get('physical_graph_id',physical_identity(value))!=physical_identity(value):raise ValueError('Physical interface graph identity differs')
    json.dumps(value,allow_nan=False);return value


def _units(port):
    value=port.get('units')
    return value if isinstance(value,dict) else {'quantity':port['unit']} if port.get('unit') else {}


def _datum(value,unit=None):
    return deepcopy(value) if isinstance(value,dict) else dict(value=value,unit=unit,validity='unknown')


def _supported(data,graph,*,numeric=False):
    if not isinstance(data,dict) or data.get('validity',data.get('status'))!='supported':return False
    source=graph.get('sources',{}).get(data.get('source_id'),{})
    if not _sha(source.get('sha256')) or not source.get('locator'):return False
    if source.get('candidate_id',graph['candidate_id'])!=graph['candidate_id']:return False
    allowed=('approved-interface','verified-simulation','correlated-measurement') if numeric else ('geometry-definition','approved-interface','verified-simulation','correlated-measurement')
    if source.get('kind') not in allowed:return False
    if source['kind']=='verified-simulation' and (source.get('numerical_validity') not in ('valid','converged') or source.get('model_domain')!='supported'):return False
    return True


def _box(value):
    if not isinstance(value,dict) or not value.get('frame_id') or value.get('unit','m')!='m':return None
    lo=value.get('min_m');hi=value.get('max_m')
    if not isinstance(lo,list) or not isinstance(hi,list) or len(lo)!=3 or len(hi)!=3 or any(not _number(n) for n in lo+hi) or any(b<a for a,b in zip(lo,hi)):raise ValueError('Finite ordered SI envelope coordinates required')
    return lo,hi


def _stock_totals(graph):
    mass=hours=0.;unknown_mass=[];unknown_hours=[]
    for c in graph['components']:
        value=c.get('stock',{}).get('mass_kg')
        if _number(value) and value>=0:mass+=value
        else:unknown_mass.append(c['occurrence_id'])
    for op in graph.get('assembly',[]):
        value=op.get('hours')
        if _number(value) and value>=0:hours+=value
        else:unknown_hours.append(op['id'])
    if not graph.get('assembly'):unknown_hours.append('<assembly-plan-unassigned>')
    return dict(known_stock_mass_kg=mass,unknown_mass_occurrences=unknown_mass,
        known_declared_assembly_hours=hours,unknown_assembly_hours_operations=unknown_hours,
        complete_installed_mass_kg=None,complete_assembly_hours=None,complete_installed_cost_USD=None)


def assess(candidate_graph):
    g=validate_identity(candidate_graph);issues=[];checks=[]
    def issue(status,code,context,detail):issues.append(dict(status=status,code=code,context=context,detail=detail))
    def supported(data,context,numeric=False):
        ok=_supported(data,g,numeric=numeric)
        if not ok:issue('unknown','evidence-unknown',context,'Declared interface data lacks supported, scoped source evidence')
        return ok
    components={c['occurrence_id']:c for c in g['components']};ports={(c['occurrence_id'],p['id']):p for c in g['components'] for p in c.get('ports',[])}
    connected={tuple(p) for q in g.get('connections',[]) for p in (q['from'],q['to'])};combined={}
    for endpoint,p in ports.items():
        if endpoint not in connected and p.get('connection_required') is not False:issue('fail' if p.get('connection_required') is True else 'unknown','unconnected-required-port','/'.join(endpoint),'Declare and connect required interfaces, or explicitly mark an unused optional port')
    for c in g['components']:
        if c.get('inventory_status','unknown')!='located':issue('unknown','location-unknown',c['occurrence_id'],'Unlocated/unknown stock is not installed geometry')
    for connection in g.get('connections',[]):
        key=connection['id'];a=ports[tuple(connection['from'])];b=ports[tuple(connection['to'])];start=len(issues)
        if a['kind']!=b['kind']:issue('fail','kind-mismatch',key,'Different interface domains require an explicit adapter')
        ua,ub=_units(a),_units(b)
        if not ua or not ub:issue('unknown','unit-unknown',key,'Quantity units are unassigned')
        elif set(ua)!=set(ub) or any(ua[n]!=ub[n] for n in ua):issue('fail','unit-mismatch',key,'No implicit conversion or missing quantity mapping')
        for field in ('frame_id','connector'):
            if not a.get(field) or not b.get(field):issue('unknown',field+'-unknown',key,'Explicit interface reference required')
            elif a[field]!=b[field]:issue('fail',field+'-mismatch',key,'No implicit frame transform or connector adaptation')
        if a.get('frame_id') and a['frame_id'] not in g.get('frames',{}):issue('unknown','frame-definition-unknown',key,'Named frame/reference has no definition')
        if a.get('direction') not in ('source','bidirectional') or b.get('direction') not in ('sink','bidirectional'):
            issue('unknown' if not a.get('direction') or not b.get('direction') else 'fail','direction-mismatch',key,'Connection must follow a declared source/sink convention')
        roles=(a.get('connector_role'),b.get('connector_role'))
        if all(roles) and roles not in (('plug','socket'),('socket','plug'),('symmetric','symmetric')):issue('fail','connector-role-mismatch',key,'Mating roles do not complement')
        if a['kind']=='mechanical':
            required=a.get('required_dofs',a.get('dofs'));available=b.get('supported_dofs',b.get('dofs'))
            if required is None or available is None:issue('unknown','load-dof-unknown',key,'Load/kinematic transfer DOFs need explicit definition')
            elif not set(required)<=set(available):issue('fail','load-dof-mismatch',key,'Receiver does not transfer every required DOF')
        if a.get('phase_order') and b.get('phase_order') and a['phase_order']!=b['phase_order']:issue('fail','phase-order-mismatch',key,'Electrical phase convention differs')
        supported(a.get('data_validity'),key);supported(b.get('data_validity'),key)
        if a['kind'] in ('mechanical','electrical','thermal') and not (a.get('demand') or b.get('demand')):issue('unknown','duty-unassigned',key,'Actual demand and capacity are required in addition to a matching connector')
        # A source operating envelope must fit receiver limits. A selectable
        # supply may instead name an actual controlled operating point.
        for name in set(a.get('ranges',{}))|set(b.get('ranges',{})):
            if name not in ua or name not in ub:issue('unknown','range-unit-unassigned',key+'/'+name,'Operating/acceptance range lacks quantity units')
            x=a.get('ranges',{}).get(name);y=b.get('ranges',{}).get(name)
            if x is None or y is None:issue('unknown','range-unknown',key+'/'+name,'Both operating and acceptance ranges are required');continue
            if len(x)!=2 or len(y)!=2 or any(not _number(v) for v in list(x)+list(y)) or x[0]>x[1] or y[0]>y[1]:raise ValueError('Finite ordered interface ranges required')
            selected=a.get('selected_values',{}).get(name)
            range_supported=_supported(a.get('data_validity'),g,numeric=True) and _supported(b.get('data_validity'),g,numeric=True)
            if not range_supported:issue('unknown','range-evidence-unknown',key+'/'+name,'Unverified range data cannot establish operating compatibility')
            if selected is not None:
                if not _number(selected) or not x[0]<=selected<=x[1] or not y[0]<=selected<=y[1]:issue('fail' if range_supported else 'unknown','selected-value-outside-range',key+'/'+name,'Controlled value lies outside a declared operating/acceptance range')
            elif x[0]<y[0] or x[1]>y[1]:issue('fail' if range_supported else 'unknown','range-mismatch',key+'/'+name,'Source operating range exceeds receiver acceptance; intersection alone is insufficient')
        for source,receiver,endpoint in ((a,b,tuple(connection['to'])),(b,a,tuple(connection['from']))):
            for name,value in source.get('demand',{}).items():
                d=_datum(value,_units(source).get(name));cap=_datum(receiver.get('capacity',{}).get(name),_units(receiver).get(name))
                combined.setdefault((endpoint,name),[]).append(d)
                if d.get('unit')!=cap.get('unit') or not d.get('unit'):issue('fail' if d.get('unit') and cap.get('unit') else 'unknown','capacity-unit-mismatch',key+'/'+name,'Demand/capacity units must match')
                if not _number(d.get('value')) or not _number(cap.get('value')):issue('unknown','capacity-unknown',key+'/'+name,'Unknown demand/capacity is not zero');continue
                if cap['value']<0:raise ValueError('Maximum-magnitude capacities must be nonnegative')
                if abs(d['value'])>cap['value']:issue('fail' if _supported(d,g,numeric=True) and _supported(cap,g,numeric=True) else 'unknown','capacity-exceeded',key+'/'+name,'Declared demand exceeds capacity; unsupported values are a hold, not a proven physical failure')
                supported(d,key+'/'+name,True);supported(cap,key+'/'+name,True)
        ea,eb=a.get('envelope'),b.get('envelope')
        if ea is not None or eb is not None:
            x,y=_box(ea),_box(eb)
            if x is None or y is None:issue('unknown','mating-envelope-unknown',key,'Both required/available envelopes are needed')
            elif ea['frame_id']!=eb['frame_id']:issue('fail','mating-envelope-frame-mismatch',key,'Explicit transformed envelope required')
            else:
                required,available=(x,y) if ea.get('role')=='required' and eb.get('role')=='available' else (y,x) if eb.get('role')=='required' and ea.get('role')=='available' else (None,None)
                if required is None:issue('unknown','mating-envelope-role-unknown',key,'Name required and available spaces')
                elif any(a<b or c>d for a,b,c,d in zip(required[0],available[0],required[1],available[1])):issue('fail','mating-envelope-does-not-fit',key,'Required space exceeds available envelope')
                supported(ea.get('data_validity'),key);supported(eb.get('data_validity'),key)
        local=issues[start:];checks.append(dict(connection_id=key,status='fail' if any(i['status']=='fail' for i in local) else 'unknown' if local else 'pass'))
    for (endpoint,name),demands in combined.items():
        if len(demands)<2:continue
        cap=_datum(ports[endpoint].get('capacity',{}).get(name),_units(ports[endpoint]).get(name));key='/'.join(endpoint)+'/'+name
        if g.get('simultaneous_demands') is not True:issue('unknown','load-sharing-unknown',key,'Explicit simultaneous load-case or scheduling evidence is required before combining demand envelopes')
        elif not _number(cap.get('value')) or any(not _number(d.get('value')) for d in demands):issue('unknown','combined-capacity-unknown',key,'Shared capacity or one simultaneous demand is unknown')
        elif sum(abs(d['value']) for d in demands)>cap['value']:issue('fail' if _supported(cap,g,numeric=True) and all(_supported(d,g,numeric=True) for d in demands) else 'unknown','combined-capacity-exceeded',key,'Sum of declared simultaneous demands exceeds shared capacity; unsupported bounds remain a hold')
    required=_names(g.get('required_functions',[]));provided={n:[c for c in g['components'] if n in _names(c.get('functions',[]))] for n in required}
    for function,providers in provided.items():
        if not providers:issue('fail','required-function-missing',function,'Part elimination removed a required function')
        elif not any(_supported(c.get('function_evidence',{}).get(function),g,numeric=True) for c in providers):issue('unknown','function-evidence-unknown',function,'A declared provider is not demonstrated function performance')
    if not required:issue('unknown','required-functions-unassigned','functions','Broad function obligations must be explicit')
    keepouts=g.get('keepouts',[])+g.get('openings',[])
    for keepout in keepouts:
        bounds=_box(keepout)
        if bounds is None:issue('unknown','keepout-unknown',keepout.get('id'),'Opening/keepout geometry unassigned');continue
        for c in g['components']:
            if c['occurrence_id'] in keepout.get('exempt_occurrences',[]):continue
            envelopes=c.get('envelopes',([c['envelope']] if c.get('envelope') else []))
            if not envelopes:issue('unknown','occupied-envelope-unknown',c['occurrence_id'],'Cannot clear an opening without occupied geometry')
            for envelope in envelopes:
                box=_box(envelope)
                if box is None or envelope.get('kind') not in ('occupied','swept'):issue('unknown','occupied-envelope-unknown',c['occurrence_id'],'An allocation box is not occupied/swept geometry');continue
                if envelope['frame_id']!=keepout['frame_id']:issue('unknown','spatial-frame-unresolved',c['occurrence_id'],'A frame transform is required before clearance evaluation');continue
                if all(min(b,d)-max(a,c)>1e-10 for a,b,c,d in zip(bounds[0],bounds[1],box[0],box[1])):issue('fail','opening-keepout-intersection',c['occurrence_id'],'Declared occupied/swept material obstructs a required empty space')
                supported(envelope.get('data_validity'),c['occurrence_id']);supported(keepout.get('data_validity'),keepout['id'])
    operations={};covered=set()
    for op in g.get('assembly',[]):
        if not op.get('id') or op['id'] in operations:raise ValueError('Unique assembly operation identities required')
        operations[op['id']]=op;covered.update(op.get('occurrences',[]))
        if set(op.get('occurrences',[]))-set(components):issue('fail','assembly-occurrence-missing',op['id'],'Operation references an eliminated/absent part')
        if 'requires' not in op:issue('unknown','assembly-dependencies-unknown',op['id'],'Prerequisites are unassigned')
        supported(op.get('data_validity'),op['id'])
    for uid,op in operations.items():
        if set(op.get('requires',[]))-set(operations):issue('fail','assembly-dependency-missing',uid,'Prerequisite operation is absent')
    seen=set();active=set()
    def visit(uid):
        if uid in active:issue('fail','assembly-cycle',uid,'Assembly prerequisites are cyclic');return
        if uid in seen:return
        active.add(uid)
        for parent in operations[uid].get('requires',[]):
            if parent in operations:visit(parent)
        active.remove(uid);seen.add(uid)
    for uid in operations:visit(uid)
    for uid in set(components)-covered:issue('unknown','assembly-plan-missing',uid,'Installed/removal process is unassigned')
    result=dict(schema='osr-interface-graph-assessment/1',candidate_id=g['candidate_id'],requirement_revision=g['requirement_revision'],
        physical_graph_id=physical_identity(g),compatibility_status='fail' if any(i['status']=='fail' for i in issues) else 'unknown' if issues else 'pass',
        connection_checks=checks,issues=issues,required_functions=required,declared_functions_preserved=all(provided.values()),
        function_scope='Declared coverage is separate from supported performance',stock=_stock_totals(g),
        integrated_suitability='unknown',evidence_authentication='Source references require external authentication and independent qualification',
        capacity_sharing_scope='Shared sums require simultaneous_demands=true; no assumed coincidence, cancellation, diversity or timing credit',
        source_sha256={PRODUCER:sha256(Path(__file__).read_bytes()).hexdigest()},**FLAGS)
    result['evaluation_id']=identity(result);return result


def compare_integration(before,after):
    """Compare known stock/operations only after checking both revised graphs."""
    a=validate_identity(before);b=validate_identity(after)
    if a['candidate_id']==b['candidate_id'] and physical_identity(a)!=physical_identity(b):raise ValueError('Changed physical occurrences/connections require a new candidate identity')
    aa=assess(a);bb=assess(b);old=set(_names(a.get('required_functions',[])));new=set(_names(b.get('required_functions',[])))
    supplied={f for c in b['components'] for f in _names(c.get('functions',[]))};missing=sorted(old-supplied)
    ma,mb=aa['stock'],bb['stock'];mass_delta=None if ma['unknown_mass_occurrences'] or mb['unknown_mass_occurrences'] else mb['known_stock_mass_kg']-ma['known_stock_mass_kg']
    hours_delta=None if ma['unknown_assembly_hours_operations'] or mb['unknown_assembly_hours_operations'] else mb['known_declared_assembly_hours']-ma['known_declared_assembly_hours']
    result=dict(schema='osr-function-integration-comparison/1',before_candidate_id=a['candidate_id'],after_candidate_id=b['candidate_id'],
        before_evaluation_id=aa['evaluation_id'],after_evaluation_id=bb['evaluation_id'],occurrence_count_delta=len(b['components'])-len(a['components']),
        declared_function_coverage='fail' if missing or old-new else 'pass',missing_functions=missing,dropped_function_obligations=sorted(old-new),
        known_stock_mass_delta_kg=mass_delta,known_declared_assembly_hours_delta=hours_delta,
        after_compatibility_status=bb['compatibility_status'],integrated_suitability='unknown',complete_installed_mass_delta_kg=None,
        complete_installed_cost_USD=None,comparison_scope='Known declared stock and operations; no performance, labour-rate or complete installed saving is invented',**FLAGS)
    result['comparison_id']=identity(result);return result
