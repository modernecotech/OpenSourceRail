"""Research design-for-manufacture/assembly from actual stock and join graphs.

Geometry prisms are not automatically purchased parts: explicit manufacturing
occurrence IDs group, for example, four wall prisms into one hollow extrusion.
Missing occurrence grouping, installed hardware, labor, tooling or access remain
unknown. Function integration does not by itself establish a net cost/mass win.
"""
from copy import deepcopy
from pathlib import Path
from math import isfinite
import json,re
from . import material_database as materials
from engineering.station_rail import ROOT
from engineering.station_rail.common import identity,digest

PRODUCER='engineering/design_search/dfma.py'
FLAGS=materials.FLAGS
ALIASES={'roof_structure':'roof-structure','roof structure':'roof-structure','roof':'roof-structure',
    'pv_mount':'solar-mount','PV mounting':'solar-mount','solar_mount':'solar-mount','solar-mounting':'solar-mount',
    'cable_route':'cable-route','wiring-channel':'cable-route','drain':'drainage',
    'hvac_duct':'hvac-duct','HVAC duct':'hvac-duct'}


def _sha(value):return isinstance(value,str) and re.fullmatch('[0-9a-f]{64}',value) is not None
def _finite(value):return type(value) in (float,int) and isfinite(value)


def _tags(row,key):
    value=row.get(key,[])
    if isinstance(value,str):value=[value]
    if not isinstance(value,list) or any(not isinstance(x,str) or not x for x in value):raise ValueError('Explicit string function/load-role tags required')
    return sorted({ALIASES.get(x,x) for x in value})


def _hours(operation,candidate_id,supplied,root):
    evidence=supplied.get('evidence') if supplied else None
    result=dict(labor_h=None,elapsed_h=None,tooling_cost_USD=None,evidence=None,
        supplied_unverified_labor_h=supplied.get('labor_h') if supplied else None,
        basis='No source-bound operation time or tooling evidence')
    if evidence is None:return result
    if not isinstance(evidence,dict) or not isinstance(evidence.get('path'),str) or not _sha(evidence.get('sha256')):raise ValueError('Exact ordinary operation-evidence path and digest required')
    rel=Path(evidence['path']);base=Path(root).resolve();p=base/rel
    if rel.is_absolute() or '..' in rel.parts or not rel.parts or not p.resolve().is_relative_to(base):raise ValueError('Operation evidence must stay inside the declared root')
    for q in (p,*p.parents):
        if q==base:break
        if q.is_symlink():raise ValueError('Ordinary operation evidence files required')
    if not p.is_file() or digest(p)!=evidence['sha256']:raise ValueError('Operation evidence bytes differ')
    record=json.loads(p.read_bytes())
    if record.get('schema')!='osr-dfma-operation-evidence/1' or record.get('candidate_id')!=candidate_id or record.get('operation_id')!=operation['id'] or sorted(record.get('part_ids',[]))!=sorted(operation['part_ids']):raise ValueError('Operation evidence uses different candidate/operation/parts')
    if record.get('basis') not in ('measured','supplier-quote','process-estimate'):raise ValueError('Declared operation evidence basis required')
    for key in ('labor_h','elapsed_h','tooling_cost_USD'):
        value=record.get(key)
        if value is not None and (not _finite(value) or value<0):raise ValueError('Finite nonnegative evidenced operation quantity required')
        result[key]=value
    result.update(evidence=deepcopy(evidence),basis=record['basis'],evidence_verification='Local bytes and exact context match; authenticity and independent review are not established by this adapter')
    return result


def evaluate(candidate_graph,material_assignments=None,*,root=ROOT):
    """Build an operation graph and integration/repair comparison contract.

    Input: candidate_id; parts or geometry_parts with unique id and total-row
    mass_kg (optional quantity is an explicit count, never a second multiplier);
    optional manufacturing_occurrence_id/functions/load_roles/process/form/
    removable/removal_path/tooling/supplier/QA; joins[{id,part_ids,method?}].
    Optional operations attach source-bound time records and additional
    prerequisites by generated operation ID. Joins may declare after_join_ids;
    these require the prior join's inspection. Cycles are refused. Material
    assignments map actual part IDs to database record IDs.
    """
    graph=deepcopy(candidate_graph)
    if not isinstance(graph,dict) or not _sha(graph.get('candidate_id')):raise ValueError('Exact physical candidate ID required')
    if 'graph_id' in graph and graph['graph_id']!=identity({n:v for n,v in graph.items() if n!='graph_id'}):raise ValueError('Candidate graph identity differs')
    raw=graph.get('parts',graph.get('geometry_parts'))
    if not isinstance(raw,list) or not raw:raise ValueError('Actual physical stock rows required')
    parts={};groups={};unassigned=[];known_mass=0.;unknown_mass=[]
    db=materials.catalogue();catalogue={r['id']:r for r in db['records']};assign=deepcopy(material_assignments or {})
    if not isinstance(assign,dict):raise ValueError('Explicit part-to-material assignments required')
    for p in raw:
        name=p.get('id')
        if not isinstance(name,str) or not name or name in parts:raise ValueError('Unique actual stock IDs required')
        quantity=p.get('quantity',1)
        if type(quantity) is not int or quantity<1:raise ValueError('Positive explicit row quantity required')
        mass=p.get('mass_kg')
        if mass is not None and (not _finite(mass) or mass<=0):raise ValueError('Finite positive physical stock mass or unknown required; interfaces belong in joins')
        if mass is None:unknown_mass.append(name)
        else:known_mass+=mass
        part={**p,'functions':_tags(p,'functions'),'load_roles':_tags(p,'load_roles')}
        parts[name]=part;occurrence=p.get('manufacturing_occurrence_id')
        if occurrence is None:
            unassigned.append(name);group='unresolved-occurrence/'+name
        else:
            if not isinstance(occurrence,str) or not occurrence:raise ValueError('Explicit manufacturing occurrence IDs required')
            group=occurrence
        groups.setdefault(group,[]).append(name)
    if set(assign)-set(parts):raise ValueError('Material assignment references an absent physical part')
    for name,material in assign.items():
        if not isinstance(material,str) or material not in catalogue:raise ValueError('Registered component/material record ID required')
    joins=graph.get('joins',[])
    if not isinstance(joins,list):raise ValueError('Explicit actual join list required')
    declared_join_ids={j.get('id') for j in joins if isinstance(j,dict)}
    seen=set();ops=[];integration=[]
    for group,ids in sorted(groups.items()):
        functions=sorted({f for name in ids for f in parts[name]['functions']});roles=sorted({f for name in ids for f in parts[name]['load_roles']})
        process_values=sorted({parts[name]['process'] for name in ids if isinstance(parts[name].get('process'),str) and parts[name]['process']})
        process=process_values[0] if len(process_values)==1 else None
        common=dict(part_ids=ids,manufacturing_occurrence_id=None if group.startswith('unresolved-occurrence/') else group,
            functions=functions,load_roles=roles,material_records=sorted({assign[n] for n in ids if n in assign}),
            process=process,process_provenance=[parts[n].get('process_provenance') for n in ids],
            tooling=[parts[n].get('tooling') for n in ids],supplier=[parts[n].get('supplier') for n in ids],
            QA_requirements=[parts[n].get('QA') for n in ids],qualified=False)
        ops.append(dict(id='fabricate:'+group,kind='fabrication',prerequisites=[],**common))
        # Functions are explicitly claimed by this physical group. Geometry,
        # seals, loads, airflow and electrical segregation still need checks.
        if len(functions)>1:
            roof='roof-structure' in functions
            integration.append(dict(manufacturing_occurrence_id=common['manufacturing_occurrence_id'],part_ids=ids,
                functions=functions,load_roles=roles,roof_service_integration=roof and bool(set(functions)&{'solar-mount','cable-route','drainage','hvac-duct'}),
                known_group_stock_mass_kg=None if any(parts[n].get('mass_kg') is None for n in ids) else sum(parts[n]['mass_kg'] for n in ids),
                removal_path=[parts[n].get('removal_path') for n in ids],
                repair_coupling='Replacing the shared physical member can affect every listed function; removal and resealing need explicit design',
                required_checks=['Structural contribution and actual load path','Water/air sealing, condensate and cleaning access',
                    'Cable/drain/duct segregation and thermal/fire compatibility','PV retention and wiring interfaces' if roof else 'Function-specific retention and interfaces',
                    'Repair/removal path, replacement time and QA'],
                removed_interfaces_count=None,net_installed_mass_delta_kg=None,net_cost_delta_USD=None,functional_equivalence_verified=False))
        if any(parts[n].get('removable') is True for n in ids):
            ops.append(dict(id='remove:'+group,kind='maintenance-removal',prerequisites=[],**common,
                removal_path=[parts[n].get('removal_path') for n in ids],repair_hours=None))
    group_by_part={name:group for group,ids in groups.items() for name in ids};join_holds=[];known_fasteners=0;unknown_fasteners=[]
    for join in joins:
        if not isinstance(join,dict):raise ValueError('Actual join records required')
        name=join.get('id');ids=join.get('part_ids')
        if not isinstance(name,str) or not name or name in seen or not isinstance(ids,list) or len(set(ids))!=len(ids) or len(ids)<2 or set(ids)-set(parts):raise ValueError('Unique join ID and existing distinct physical part IDs required')
        seen.add(name);method=join.get('method');prerequisites=sorted({'fabricate:'+group_by_part[n] for n in ids})
        after=join.get('after_join_ids',[])
        if not isinstance(after,list) or any(not isinstance(n,str) or n==name or n not in declared_join_ids for n in after):raise ValueError('Explicit existing prior join IDs required')
        prerequisites+=['inspect:'+n for n in after]
        if method is not None and (not isinstance(method,str) or not method):raise ValueError('Explicit joining process or unknown required')
        roles=_tags(join,'load_roles');structural=any(x in ('primary','primary-structure','load-bearing','structural') for x in roles)
        if structural and method in ('clip','clip-only','snap-fit'):
            join_holds.append(dict(join_id=name,reason='Primary load transfer cannot inherit removable-panel clip evidence; validate a positively retained structural joint'))
        count=join.get('fastener_count')
        if count is None:unknown_fasteners.append(name)
        elif type(count) is not int or count<0:raise ValueError('Explicit nonnegative fastener count or unknown required')
        else:known_fasteners+=count
        hardware_mass=join.get('hardware_mass_kg')
        if hardware_mass is not None and (not _finite(hardware_mass) or hardware_mass<0):raise ValueError('Finite nonnegative declared join hardware mass or unknown required')
        common=dict(part_ids=ids,join_id=name,process=method,load_roles=roles,
            declared_hardware_mass_kg=hardware_mass,process_provenance=join.get('process_provenance'),
            QA_requirements=join.get('QA'),tooling=join.get('tooling'),supplier=join.get('supplier'),qualified=False)
        ops.append(dict(id='assemble:'+name,kind='assembly',prerequisites=prerequisites,**common))
        ops.append(dict(id='inspect:'+name,kind='inspection',prerequisites=['assemble:'+name],**common))
    supplied=graph.get('operations',[])
    if not isinstance(supplied,list):raise ValueError('Explicit operation evidence rows required')
    provided={}
    for row in supplied:
        if not isinstance(row,dict) or not isinstance(row.get('id'),str) or row['id'] in provided:raise ValueError('Unique operation evidence IDs required')
        provided[row['id']]=row
    if set(provided)-{o['id'] for o in ops}:raise ValueError('Operation evidence references an absent generated operation')
    for op in ops:
        row=provided.get(op['id'],{});extra=row.get('prerequisites',[])
        if not isinstance(extra,list) or any(not isinstance(n,str) for n in extra):raise ValueError('Explicit operation prerequisite IDs required')
        op['prerequisites']=sorted(set(op['prerequisites']+extra));op.update(_hours(op,graph['candidate_id'],row,root))
    remaining={o['id']:set(o['prerequisites']) for o in ops};all_ids=set(remaining);order=[]
    if any(v-all_ids for v in remaining.values()):raise ValueError('Operation prerequisite references an absent actual operation')
    while remaining:
        ready=sorted(n for n,v in remaining.items() if not v)
        if not ready:raise ValueError('Assembly/inspection/removal operation graph contains a cycle')
        order.extend(ready)
        for n in ready:remaining.pop(n)
        for v in remaining.values():v.difference_update(ready)
    totals={}
    for kind in ('fabrication','assembly','inspection','maintenance-removal'):
        subset=[o for o in ops if o['kind']==kind]
        totals[kind]=dict(operation_count=len(subset),source_claimed_labor_h_subtotal=sum(o['labor_h'] for o in subset if o['labor_h'] is not None),
            unknown_labor_operation_ids=[o['id'] for o in subset if o['labor_h'] is None],
            complete_labor_h=sum(o['labor_h'] for o in subset) if subset and all(o['labor_h'] is not None for o in subset) else None,
            scope='Counts and supplied time evidence for the declared partial graph only; not full production labor')
    result=dict(schema='osr-research-dfma-evaluation/1',candidate_id=graph['candidate_id'],input_graph_id=identity(graph),
        material_database_id=db['database_id'],material_assignments=assign,geometric_stock_rows=len(parts),
        declared_manufacturing_occurrences=len(groups)-len(unassigned),unknown_occurrence_stock_ids=unassigned,
        resolved_manufactured_component_count=None if unassigned else len(groups),complete_vehicle_component_count=None,
        known_stock_mass_subtotal_kg=known_mass,unknown_mass_stock_ids=unknown_mass,complete_installed_mass_kg=None,
        assembly_interfaces=len(joins) if 'joins' in graph else None,known_fastener_count_subtotal=known_fasteners,
        unknown_fastener_join_ids=unknown_fasteners,complete_fastener_count=None if unknown_fasteners or 'joins' not in graph else known_fasteners,
        operations=ops,operation_order=order,labor=totals,function_integration=integration,joint_holds=join_holds,
        material_assignment_compatibility='Not inferred from IDs; search the material database under explicit function/load/environment/process requirements',
        complete_tooling_cost_USD=None,complete_installed_cost_USD=None,net_installed_mass_delta_kg=None,
        functional_equivalence_verified=False,economic_winner=None,
        scope='Actual declared stock/occurrence/join research graph; missing fitout, hardware, access, process evidence and prototype validation remain open',
        source_sha256={**materials.source_map(),PRODUCER:digest(__file__)},**FLAGS)
    result['evaluation_id']=identity(result);return result


def compare(left,right,*,left_material_assignments=None,right_material_assignments=None,root=ROOT):
    """Compare explicit integration/replaceable graphs without inventing savings."""
    a=evaluate(left,left_material_assignments,root=root);b=evaluate(right,right_material_assignments,root=root)
    functions=lambda r:sorted({f for o in r['operations'] if o['kind']=='fabrication' for f in o['functions']})
    result=dict(schema='osr-dfma-integration-comparison/1',left_evaluation_id=a['evaluation_id'],right_evaluation_id=b['evaluation_id'],
        left_candidate_id=a['candidate_id'],right_candidate_id=b['candidate_id'],left_functions=functions(a),right_functions=functions(b),
        same_declared_function_tags=functions(a)==functions(b),functional_equivalence_verified=False,
        known_stock_subtotal_difference_kg=b['known_stock_mass_subtotal_kg']-a['known_stock_mass_subtotal_kg'],
        declared_assembly_interface_difference=None if a['assembly_interfaces'] is None or b['assembly_interfaces'] is None else b['assembly_interfaces']-a['assembly_interfaces'],
        left=a,right=b,net_installed_mass_delta_kg=None,net_installed_cost_delta_USD=None,whole_life_cost_delta_USD=None,
        winner=None,scope='Counted partial-graph differences only; common functional performance, installed completeness, tooling, repair and economics are not established',**FLAGS)
    result['comparison_id']=identity(result);return result
