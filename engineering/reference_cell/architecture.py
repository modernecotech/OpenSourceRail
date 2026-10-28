"""Typed architecture registration and dependency-aware revision requests."""
from copy import deepcopy
from math import isfinite
from . import identity, FLAGS

KINDS=('body','running-gear','propulsion','guideway','station','manufacturing')
PORTS={'body':{'support':'mechanical','services':'electrical','passengers':'accessibility'},
       'running-gear':{'support':'mechanical','rail':'wheel-rail','brakes':'brake'},
       'propulsion':{'secondary':'mechanical','supply':'electrical','controls':'control'},
       'guideway':{'rail':'wheel-rail','supports':'mechanical','erection':'construction'},
       'station':{'passengers':'accessibility','supply':'electrical','rescue':'recovery'},
       'manufacturing':{'parts':'product','resources':'process','inspection':'evidence'}}
EDGES={'materials':('geometry','structure','manufacturing','cost'),
       'geometry':('mass','structure','interfaces','manufacturing'),
       'mass':('propulsion','brakes','civil','service','cost'),
       'propulsion':('journey','thermal','civil','controls','cost'),
       'brakes':('journey','controls','service'), 'journey':('civil','controls','service','energy'),
       'civil':('construction','cost'), 'manufacturing':('construction','cost'),
       'service':('fleet','cost'), 'energy':('cost',), 'construction':('cost',),
       'cost':('selection',),'structure':('selection',),'controls':('selection',)}


class Registry:
    """Trusted code registers definitions, never executable code from input files."""
    def __init__(self):self.records={}
    def register(self,kind,name,parameters,ports,*,evaluator=None,origin='research-hypothesis'):
        if kind not in KINDS or not isinstance(name,str) or not name or (kind,name) in self.records:
            raise ValueError('Unique named typed architecture required')
        if ports!=PORTS[kind]:raise ValueError('Architecture interface types differ')
        if evaluator is not None and (not isinstance(evaluator,str) or not evaluator.strip()):
            raise ValueError('Named owning evaluator or explicit absence required')
        value=dict(kind=kind,name=name,parameters=deepcopy(parameters),ports=deepcopy(ports),
                   evaluator=evaluator,origin=origin,**FLAGS)
        # Canonical encoding rejects NaN and non-serializable imported objects.
        value['definition_id']=identity(dict(kind=kind,parameters=parameters,ports=ports))
        value['evaluation_id']=identity(value);self.records[kind,name]=value
        return deepcopy(value)
    def get(self,kind,name):return deepcopy(self.records[kind,name])
    def bundle(self,choices,requirements):
        if set(choices)!=set(KINDS):raise ValueError('Complete architecture composition required')
        parts={k:self.get(k,choices[k]) for k in KINDS}
        if requirements.get('cars')!=6 or requirements.get('normal_places_per_car')!=46:
            raise ValueError('This comparison retains the six-car comfort service')
        physical=dict(components={k:v['definition_id'] for k,v in parts.items()},requirements=deepcopy(requirements))
        return dict(schema='osr-extensible-architecture/1',candidate_id=identity(physical),physical_definition=physical,
                    components=parts,unsupported_evaluators=[k for k,v in parts.items() if v['evaluator'] is None],**FLAGS)


def defaults():
    r=Registry()
    for i in range(1,6):r.register('body',f'V{i}',dict(vehicle=f'V{i}'),PORTS['body'],evaluator='reference_cell.vehicles')
    r.register('running-gear','passive',dict(bogies_per_car=2,axles_per_bogie=2,wheels_per_axle=2),PORTS['running-gear'],evaluator='reference_cell.vehicles')
    for name,starts,length,method in (
        ('five-20m',[-13.,87.375,187.75,288.125,388.5],20.,'LIM'),
        ('six-20m',[-13.,67.,147.,227.,307.,387.],20.,'LIM'),
        ('ten-20m',[float(x)-13. for x in range(0,500,50)],20.,'LIM'),
        ('longer-distributed',[0.,170.,340.],100.,'LIM'),
        ('continuous-500m',[0.],500.,'LIM'),
        ('auxiliary-rescue',[0.,100.,200.,300.,400.],20.,'LIM-with-onboard-rescue'),
        ('station-cable',[0.],500.,'mechanical-cable')):
        r.register('propulsion',name,dict(bank_starts_m=starts,bank_length_m=length,method=method,
            onboard_traction=method=='LIM-with-onboard-rescue',installed_primary_m=len(starts)*length,
            recovery_required=True),PORTS['propulsion'],evaluator='reference_cell.physics' if method=='LIM' and length==20. else None)
    for name in ('box','twin','u'):r.register('guideway',name,dict(span_m=20.,section=name),PORTS['guideway'],evaluator='reference_cell.civil')
    r.register('station','accessible-two-station',dict(count=2,platform_m=110.,lift_per_station=2,evacuation_required=True),PORTS['station'],evaluator='reference_cell.civil')
    r.register('manufacturing','local-modular',dict(mode='local-manufacture-or-qualified-procurement',trace_domestic_value_added=True),PORTS['manufacturing'],evaluator='reference_cell.manufacturing')
    return r


def invalidated(changes):
    if not changes or any(x not in EDGES for x in changes):raise ValueError('Explicit dependency changes required')
    found=set(changes);pending=list(changes)
    while pending:
        for name in EDGES.get(pending.pop(),()):
            if name not in found:found.add(name);pending.append(name)
    return sorted(found)


def revision(candidate_id,failure_class,observations):
    if not isinstance(candidate_id,str) or len(candidate_id)!=64 or any(c not in '0123456789abcdef' for c in candidate_id):raise ValueError('Exact parent candidate hash required')
    if failure_class not in ('physical','numerical','missing-evidence','cost'):
        raise ValueError('Failure class must distinguish physics, method, evidence and economics')
    if not observations:raise ValueError('A revision needs retained observations')
    actions={'physical':['bank-count','bank-length','winding','secondary','supply','alternative-architecture'],
             'numerical':['time-refinement','spatial-refinement','solver-resource','independent-method'],
             'missing-evidence':['supplier-record','component-test','survey','independent-review'],
             'cost':['process-yield','part-integration','local-route','formation-and-service-comparison']}[failure_class]
    value=dict(parent_candidate_id=candidate_id,failure_class=failure_class,observations=deepcopy(observations),
        permitted_actions=actions,selection_purpose='next-experiment-only',integrated_winner=None,
        invalidated_stages=invalidated(['propulsion' if failure_class in ('physical','numerical') else 'cost' if failure_class=='cost' else 'materials']),**FLAGS)
    value['task_id']=identity(value);return value
