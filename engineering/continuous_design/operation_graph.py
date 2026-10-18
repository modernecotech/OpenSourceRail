"""Bounded assembly/removal simulation; conservative envelopes, no process qualification."""
from copy import deepcopy
import math


def box(value):
    if not isinstance(value,list) or len(value)!=2 or any(not isinstance(row,list) or len(row)!=3 for row in value):
        raise ValueError('lower/upper operation bounds required')
    if any(type(v) not in (int,float) or not math.isfinite(v) for row in value for v in row) or any(a>=b for a,b in zip(*value)):
        raise ValueError('finite positive operation envelope required')
    return value


def intersects(a,b):
    return all(max(a[0][i],b[0][i])<min(a[1][i],b[1][i])-1e-10 for i in range(3))


def swept(bounds,translation):
    box(bounds)
    if not isinstance(translation,list) or len(translation)!=3 or any(type(v) not in (int,float) or not math.isfinite(v) for v in translation):
        raise ValueError('finite operation translation required')
    return [[bounds[0][i]+min(0,translation[i]) for i in range(3)],
            [bounds[1][i]+max(0,translation[i]) for i in range(3)]]


def evaluate(plan):
    if plan.get('schema') not in {'osr-operation-graph/1','osr-operation-graph/2'}:
        raise ValueError('versioned operation graph required')
    parts={p['id']:p for p in plan['parts']}
    fixtures={f['id']:f for f in plan['fixtures']}
    operations={o['id']:o for o in plan['operations']}
    joints={j['id']:j for j in plan.get('joints',[])}
    if len(joints)!=len(plan.get('joints',[])):
        raise ValueError('unique declared joints required')
    required_joints={p['id']:set(p.get('required_joints',[])) for p in parts.values()}
    required_tests={p['id']:set(p.get('required_inspections',[])) for p in parts.values()}
    for joint in joints.values():
        endpoints=joint['endpoints']
        if len(endpoints)!=2 or len(set(endpoints))!=2 or not set(endpoints)<=parts.keys()|{'world'}:
            raise ValueError('joint requires two distinct declared endpoints')
        if joint['process'] not in {'fasten','weld','bond','form'}:
            raise ValueError('registered retention process required')
    if any(not refs<=joints.keys() for refs in required_joints.values()):
        raise ValueError('required joint definition absent')
    if len(parts)!=len(plan['parts']) or len(fixtures)!=len(plan['fixtures']) or len(operations)!=len(plan['operations']) or len(operations)>4096:
        raise ValueError('bounded unique physical parts and operations required')
    for part in parts.values():
        box(part['bounds_m'])
        if type(part['mass_kg']) not in (int,float) or not math.isfinite(part['mass_kg']) or part['mass_kg']<=0:
            raise ValueError('positive represented part mass required')
        if 'reversible' in part and type(part['reversible']) is not bool:
            raise ValueError('explicit Boolean joint reversibility required')
    for fixture in fixtures.values():
        if type(fixture['capacity_kg']) not in (int,float) or not math.isfinite(fixture['capacity_kg']) or fixture['capacity_kg']<=0:
            raise ValueError('positive fixture capacity hypothesis required')
    for op in operations.values():
        if not set(op['parts'])<=parts.keys() or not op['parts'] or not set(op['after'])<=operations.keys() or op['id'] in op['after']:
            raise ValueError('operation references absent parts/dependencies')
    installed=set();done=set();trace=[];checks={};unknown=[];held=set();retained=set();tested=set()
    def secured(targets):
        return all(required_joints[p] and required_joints[p]<=retained for p in targets)
    def inspected(targets):
        return all(required_tests[p] and all((p,test) in tested for test in required_tests[p]) for p in targets)
    def connected(targets):
        reached=set(plan.get('reference_roots',['world']))
        for _ in range(len(parts)+1):
            prior=set(reached)
            for identity in retained:
                endpoints=set(joints[identity]['endpoints'])
                if endpoints&reached:reached|=endpoints
            if reached==prior:break
        return set(targets)<=reached
    while len(done)<len(operations):
        ready=sorted(o for o in operations if o not in done and set(operations[o]['after'])<=done)
        if not ready:
            raise ValueError('assembly operation graph is cyclic')
        for identifier in ready:
            op=operations[identifier];kind=op['kind'];targets=set(op['parts']);passed=True;reason=[]
            if kind=='install':
                if targets&installed:
                    raise ValueError('part installed twice')
                fixture=fixtures.get(op.get('fixture'))
                if fixture is None:
                    passed=False;reason.append('temporary support/fixture missing')
                elif sum(parts[p]['mass_kg'] for p in (targets if fixture.get('load_scope')=='current_operation' else installed|targets))>fixture['capacity_kg']:
                    passed=False;reason.append('fixture capacity hypothesis exceeded')
                if fixture and fixture.get('load_scope')=='current_operation':
                    unknown.append(identifier+'/installed-assembly-temporary-stability')
                installed|=targets
            elif kind in {'fasten','weld','bond','cure','form','inspect','release'}:
                if not targets<=installed:
                    passed=False;reason.append('parts unavailable at operation')
                if kind=='cure' and not any(operations[d]['kind']=='bond' for d in done if set(operations[d]['parts'])&targets):
                    passed=False;reason.append('cure before bond')
                if kind=='inspect':
                    if not secured(targets) or not connected(targets):
                        passed=False;reason.append('inspection before required retention is complete')
                    elif op.get('inspection_id'):
                        held|=targets
                        tested.update((p,op['inspection_id']) for p in targets)
                if kind=='release' and (not secured(targets) or not inspected(targets) or not connected(targets)):
                    passed=False;reason.append('release before declared retention and required inspection coverage')
                if kind=='form':unknown.append(identifier+'/forming-tool-and-springback')
            else:
                raise ValueError('unsupported manufacturing operation')
            tool=op.get('tool_bounds_m')
            if tool is not None:
                box(tool)
                blocked=[p for p in installed-targets if intersects(tool,parts[p]['bounds_m'])]
                if blocked:
                    passed=False;reason.append('tool envelope blocked by '+','.join(sorted(blocked)))
            elif kind in {'fasten','weld','bond'}:
                unknown.append(identifier+'/actual-tool-access')
            linked=op.get('joints',[op['joint']] if op.get('joint') else [])
            if not set(linked)<=joints.keys():raise ValueError('operation references absent joint')
            for joint_id in linked:
                joint=joints[joint_id]
                endpoints=set(joint['endpoints'])-{'world'}
                if kind!=joint['process'] or not endpoints<=installed or joint['operation']!=identifier:
                    passed=False;reason.append('joint endpoints/process/retention operation mismatch')
                if passed:
                    retained.add(joint['id'])
                    unknown.append(joint['id']+'/engineered-capacity-and-physical-lock-verification')
            checks[identifier]=passed
            trace.append(dict(operation=identifier,kind=kind,passed=passed,reasons=reason,installed_parts=sorted(installed),
                inspection_status='simulated hold point only' if kind=='inspect' else None))
            done.add(identifier)
    checks['all_parts_installed']=installed==set(parts)
    checks['all_required_joints_retained']=secured(set(parts))
    checks['declared_connection_graph']=connected(set(parts))
    checks['required_inspection_coverage']=inspected(set(parts))
    removals=[]
    for request in plan.get('maintenance',[]):
        target=request['part'];detached=request.get('remove_first',[])
        if target not in parts or len(set(detached))!=len(detached) or not set(detached)<=parts.keys() or target in detached:
            raise ValueError('invalid maintenance part sequence')
        remaining=set(parts);blocked=[];steps=[]
        for name in [*detached,target]:
            definition=parts[name]
            if not definition.get('reversible',True):
                blocked.append(name+'/destructive-joint')
            travel=request.get('translation_m',[0.,0.,1.])
            envelope=swept(definition['bounds_m'],travel)
            obstacles=[p for p in remaining-{name} if intersects(envelope,parts[p]['bounds_m'])]
            blocked.extend(obstacles)
            steps.append(dict(part=name,blocked_by=sorted(obstacles),swept_bounds_m=envelope))
            remaining.remove(name)
        checks['maintenance/'+target]=not blocked
        removals.append(dict(part=target,passed=not blocked,steps=steps,blocked_by=sorted(set(blocked))))
    return dict(schema='osr-operation-replay/1',checks=checks,trace=trace,removal_sequences=removals,
        unknown=unknown,metrics=dict(operation_count=len(operations),setup_count=len({o.get('setup','unspecified') for o in operations.values()}),
            fixture_count=len(fixtures),inspection_count=sum(o['kind']=='inspect' for o in operations.values()),
            destructive_joint_count=sum(o['kind'] in {'weld','bond'} for o in operations.values()),
            blocked_replacement_count=sum(not r['passed'] for r in removals),
            required_joint_count=len(joints),retained_joint_count=len(retained),
            required_inspection_count=sum(len(v) for v in required_tests.values()),
            covered_inspection_count=sum((p,t) in tested for p,tests in required_tests.items() for t in tests)),
        scope='AABB envelopes and prerequisite replay, not weld distortion, cure/flow, clamping strength, human inspection or physical process simulation',
        measured_assembly_time_s=None,manufacturing_release=False)


def simple(parts,*,process='fasten',capacity_kg=25000.,maintenance=None):
    """Explicit lower-bound graph; missing swept access stays unknown."""
    parts=deepcopy(parts);operations=[];joints=[]
    previous=[]
    for index,part in enumerate(parts):
        install=dict(id=f'install-{index}',kind='install',parts=[part['id']],after=list(previous),fixture='assembly-fixture',setup='assembly')
        joining=part.get('joining_process',process)
        if joining in {'weld','bond'}:part['reversible']=False
        joint_id='retention/'+part['id']
        part['required_joints']=[joint_id];part['required_inspections']=['assembly-inspection']
        joint=dict(id=f'join-{index}',kind=joining,parts=[part['id']],after=[install['id']],setup=joining,joint=joint_id)
        joints.append(dict(id=joint_id,endpoints=[part['id'],'world' if index==0 else parts[0]['id']],
            process=joining,operation=joint['id'],capacity_evidence=None))
        operations.extend([install,joint]);previous=[joint['id']]
    all_parts=[p['id'] for p in parts]
    operations.extend([dict(id='inspect',kind='inspect',parts=all_parts,after=previous,setup='inspection',inspection_id='assembly-inspection'),
        dict(id='release',kind='release',parts=all_parts,after=['inspect'],setup='inspection')])
    return dict(schema='osr-operation-graph/2',parts=parts,joints=joints,fixtures=[dict(id='assembly-fixture',capacity_kg=capacity_kg,capacity_accepted=False)],
        operations=operations,maintenance=maintenance or [],retention_scope='Declared simulation only; world anchorage, actual manufactured-unit grouping and physical connection capacity remain open')
