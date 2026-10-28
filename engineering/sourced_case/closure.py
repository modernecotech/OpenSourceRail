"""Read-only closure accounting over retained source-cell and native packages.

Execution, arithmetic, engineering screens, source maturity and physical
qualification are independent. This dashboard issues no acceptance authority.
"""
from pathlib import Path,PurePosixPath
from math import fsum,isfinite
from collections import Counter,defaultdict
import gzip,json,tarfile,hashlib
from copy import deepcopy
from . import ROOT,FLAGS,identity,digest
from engineering.component_registry import validate_registry
CODE='engineering/sourced_case/closure.py'

PHASES=[
 ('P0','Reference integrity','WP6',['Immutable source snapshot, candidate bindings and repeatable software execution']),
 ('P1','Material and component master','WP1',['Grade/lot, laminate schedule, directional/hot-wet/fire/fatigue allowables and reviewed component interfaces']),
 ('P2','Equipped vehicle families','WP2',['Installed component drawings, joints/fasteners, measured mass/CG/inertia and full-body correlation']),
 ('P3','Station drive and receiving','WP4',['Moving contact force/current/voltage/slip, speed handoff,120s thermal duty, cooling and receiving/DC absorption tests']),
 ('P4','Coupled protected journeys','WP4',['Correlated drive/brake dynamics, timestep refinement, empty/normal/crowd/adverse and protected recovery tests']),
 ('P5','Civil and station assemblies','WP3',['Survey/geotechnics, lateral/seismic/wind loads, bearings, reinforcement/prestress, stations and erection acceptance']),
 ('P6','Manufacturing and whole-life cost','WP5',['Qualified moulds/tooling/routings/yields, complete installation scope, dated quotations, labour and lifecycle records']),
 ('P7','GoA4 and delivery integration','WP6',['Candidate-linked sensing/localisation, brake/WSP HIL, timing/fault injection and controlled ERPNext/FUXA transactions']),
 ('P8','Prototype and independent qualification','WP2',['As-built serial/lot identity, calibrated measurements, approved limits and independent engineering review']),
 ('P9','Pilot and city deployment','WP3',['Commissioned pilot, independent safety approval, surveyed route/demand/service and verified operating economics'])]
TEST_INPUTS={
 'materials-joints':['As-built coupon and joint identity/lot/cure','Laminate ply angles/thickness, hot/wet/age conditioning','Calibrated tension/compression/shear/peel/fatigue/fire measurements','Approved limits and independent reviewer'],
 'vehicle':['Installed part occurrence/serial/position and fastener torque','Weighed empty/loaded mass, axle reactions, CG/inertia','Static/dynamic body load cases and measured strains/deflections','Doors/glazing/bogie/hardpoint clearances and fatigue/collision/fire assessment'],
 'drive':['Motor/inverter/gear/roller/clamp/reaction-strip revisions','Time-synchronised force, slip, position, speed, phase/DC currents and voltages','Wet/contaminated contact, handoff/spinup, bank failure and receiving/DC absorption','120s repeated duty, rotor/winding/drive/gear/coolant/ambient temperatures and flow/pressure'],
 'brake-control':['Caliper/pad/disc/actuator revisions and release/application supply','Speed/position/adhesion, pressure/clamp force, brake torque and stopping distribution','Hot/wet/fade/WSP/failed channels/power loss, standing hold and rescue','Localisation/timing hardware-in-loop fault logs and independent stopping/protection approval'],
 'civil-site':['Surveyed alignment/grade/utilities and ground investigation','Foundation soil/water parameters, bearings, reinforcement/prestress drawings','Concentrated motor/train/wind/lateral/seismic reactions','Lifting/transport/erection temporary works and inspection records'],
 'commercial-production':['Occurrence-linked quote, scope, quantity, currency, date, location and expiry','Gross/net yields, cycle/cure/labour/tool-life/shop measurements','Tool/mould/QA/work-instruction revisions and qualified release authority','Fleet, energy tariff, renewal/maintenance/reliability and same-service lifecycle assumptions']}


def _sha(v):return isinstance(v,str) and len(v)==64 and all(c in '0123456789abcdef' for c in v)


def _read(path):
    p=Path(path)
    if p.is_symlink() or not p.is_file() or p.stat().st_size>128*1024**2:raise ValueError('Bounded ordinary closure input required')
    if p.suffix=='.gz':
        with gzip.open(p,'rb') as f:raw=f.read(128*1024**2+1)
    else:raw=p.read_bytes()
    if len(raw)>128*1024**2:raise ValueError('Closure input decompression budget exceeded')
    return json.loads(raw)


def _path(folder,name):
    if not isinstance(name,str) or '\\' in name or not name or PurePosixPath(name).as_posix()!=name or PurePosixPath(name).is_absolute() or '..' in PurePosixPath(name).parts:raise ValueError('Canonical owned closure path required')
    p=Path(folder)
    for part in PurePosixPath(name).parts:
        p=p/part
        if p.is_symlink():raise ValueError('Linked closure path is not an owned artifact')
    return p


def _sealed(value,key='evaluation_id'):
    if value.get(key)!=identity({k:v for k,v in value.items() if k!=key}):raise ValueError('Closure input identity differs')
    from engineering.railway_progress.coordinator import _unreleased
    _unreleased(value)


def _native(descriptor,root):
    if not isinstance(descriptor,dict) or set(descriptor)!={'kind','path'} or descriptor['kind'] not in ('local-panels','whole-body','distributed-contact-whole'):raise ValueError('Explicit native package kind and path required, never an input approval boolean')
    folder=Path(descriptor['path'])
    if folder.is_symlink():raise ValueError('Ordinary retained native package required')
    from . import structure,whole_structure
    probe=_read(folder/'manifest.json');kind=descriptor['kind']
    if 'engineering/sourced_case/whole_contact.py' in probe.get('source_sha256',{}):kind='distributed-contact-whole'
    if kind=='distributed-contact-whole':
        from . import whole_contact
        verify=whole_contact.verify
    else:verify=structure.verify if kind=='local-panels' else whole_structure.verify
    check=verify(folder,root=root,require_current_source=False)
    request=_read(folder/'input.json');result=_read(folder/'result.json');manifest=_read(folder/'manifest.json')
    epoch=manifest['source_sha256'];current=all((Path(root)/p).is_file() and digest(Path(root)/p)==sha for p,sha in epoch.items())
    return dict(kind=kind,requested_kind=descriptor['kind'],package_id=check['package_id'],request_id=request['request_id'],candidate_id=request['candidate_id'],
        vehicle_evaluation_id=request['vehicle_evaluation_id'],evaluation_id=result.get('evaluation_id'),execution=result['execution'],
        source_epoch_current=current,recorded_source_payload_verified=True,numerical_recomputed=False,
        benchmark_pass=result.get('method_benchmark',{}).get('benchmark_pass'),refinement=deepcopy(result.get('refinement')),
        numerical_validity='recorded-algebraic-execution; known-contact-integration-model-defect' if kind=='whole-body' else 'recorded-method; convergence-and-physical-correlation-separate',
        model_defects=['Earlier whole_structure interface samples four springs across16.8m; contact-energy integration is unsuitable for vehicle stiffness predictions'] if kind=='whole-body' else [],
        engineering_screen='held-known-contact-integration-model-defect' if kind=='whole-body' else result.get('engineering_screen'),physical_allowables=result.get('physical_strength_allowables',result.get('approved_strength_allowables')),
        failure_reason=result.get('reason'),continuous_contact_benchmark=deepcopy(result.get('continuous_I_section_benchmark')),
        files_sha256={name:digest(folder/name) for name in ('manifest.json','input.json','result.json')},source_sha256=epoch,physical_qualified=False)


def manufacturing_status(case):
    """File exports remain review-only drafts, never transaction permission."""
    p=case['manufacturing'];_sealed(p)
    if p['candidate_id']!=case['candidate_id']:raise ValueError('Manufacturing belongs to another cell')
    rows=p['routings'];draft=p.get('ERPNext_drafts',{})
    safe=draft.get('submission_allowed') is False and draft.get('docstatus')==0 and draft.get('items_disabled') is True and draft.get('active_BOMs') is False and all(r.get('production_release') is False for r in rows)
    if 'export_id' in draft:
        safe=safe and draft['export_id']==identity({k:v for k,v in draft.items() if k!='export_id'}) and draft.get('candidate_id')==case['candidate_id']
        safe=safe and draft.get('external_transactions_performed') is False and draft.get('production_orders')==[] and draft.get('active_assets')==[]
        def disabled(value):
            if isinstance(value,dict):
                for k,v in value.items():
                    if k in ('submission_allowed','approved') and v is not False:return False
                    if k=='docstatus' and (type(v) is not int or v!=0):return False
                    if k in ('is_active','is_default') and v!=0:return False
                    if k=='disabled' and v!=1:return False
                    if k=='candidate_id' and v!=case['candidate_id']:return False
                    if not disabled(v):return False
            elif isinstance(value,list):return all(disabled(v) for v in value)
            return True
        safe=safe and disabled(draft)
    return dict(candidate_id=case['candidate_id'],manufacturing_evaluation_id=p['evaluation_id'],routing_groups=len(rows),
        routed_quantity=sum(r['quantity'] for r in rows),provided_cycle_values=sum(r.get('qualified_manufacturing_cycle_h') is not None for r in rows),qualified_cycles=None,
        referenced_work_instructions=sum(op.get('work_instruction_id') is not None for r in rows for op in r['operations']),approved_work_instructions=None,
        unknown_purchased_processes=p['purchased_occurrences'],tooling_cost_USD=p.get('tooling_cost_usd'),
        complete_installed_cost_USD=p.get('complete_installed_cost_usd'),research_draft_export_allowed=safe,
        export_status='disabled-review-drafts-only' if safe else 'held-unsafe-draft-state',
        ERPNext_submission_allowed=False,production_release=False,manufacturing_release=False)


def dependency_graph(cases,vehicles,native=()):
    """Actual component/revision bindings connect to every dependent case stage."""
    nodes={};edges=set()
    def node(n,kind,revision,scope=None):
        if n not in nodes:nodes[n]=dict(node_id=n,kind=kind,revision_id=revision,scopes=[])
        if scope is not None and scope not in nodes[n]['scopes']:nodes[n]['scopes'].append(scope)
        return n
    def edge(a,b):edges.add((a,b))
    for vid,e in vehicles.items():
        v=e['vehicle'];reg=v['registry'];body=v['candidate_id'];prefix='vehicle/'+body+'/'
        stages={k:node(prefix+k,k,None,body) for k in ('requirements','geometry','mass-CG-inertia','structure','BOM','manufacturing')}
        nodes[stages['requirements']]['revision_id']=identity(v['requirements'])
        nodes[stages['geometry']]['revision_id']=identity(dict(parts=[(p['physical_definition_id'],p['geometry']) for p in reg['parts']],occurrences=reg['occurrences']))
        nodes[stages['mass-CG-inertia']]['revision_id']=identity(v['summary']);nodes[stages['BOM']]['revision_id']=reg['registry_id']
        material_ids={}
        for material in reg['materials']:
            mid=material['material_id'];revision=material.get('material_evaluation_id',identity(material));material_ids[mid]='material/'+mid+'/'+revision
            node(material_ids[mid],'material-process',revision,body)
        for p in reg['parts']:
            part=node('component/'+p['physical_definition_id']+'/'+p['revision_id'],'component',p['revision_id'],body)
            for k in ('geometry','BOM','manufacturing'):edge(part,stages[k])
            if p.get('material_id') in material_ids:edge(material_ids[p['material_id']],part)
        for a,b in (('requirements','geometry'),('requirements','structure'),('geometry','mass-CG-inertia'),('geometry','structure'),('BOM','manufacturing')):edge(stages[a],stages[b])
        exact=[n for n in native if n['candidate_id']==body and n['vehicle_evaluation_id']==v['evaluation_id'] and n['source_epoch_current']]
        nodes[stages['structure']]['revision_id']=identity([n['evaluation_id'] for n in exact]) if exact else None
    for case in cases:
        cid=case['candidate_id'];body=case['body_candidate_id'];prefix='cell/'+cid+'/'
        stages={k:node(prefix+k,k,None,cid) for k in ('drive-electrothermal','journey','civil-loads','civil-geometry','procurement','cost','control','service','city','publication')}
        nodes[stages['drive-electrothermal']]['revision_id']=case['drive']['evaluation_id']
        nodes[stages['journey']]['revision_id']=identity([r['result']['evaluation_id'] for r in case['journeys']])
        nodes[stages['civil-geometry']]['revision_id']=case['civil'].get('evaluation_id')
        nodes[stages['civil-loads']]['revision_id']=case['civil_load_transfer'].get('evaluation_id')
        nodes[stages['cost']]['revision_id']=case['partial_public_price']['evaluation_id']
        nodes[stages['publication']]['revision_id']=case['evaluation_id']
        b='vehicle/'+body+'/'
        for src,dst in ((b+'geometry',stages['drive-electrothermal']),(b+'mass-CG-inertia',stages['drive-electrothermal']),
            (b+'mass-CG-inertia',stages['journey']),(b+'structure',stages['civil-loads']),(b+'structure',stages['drive-electrothermal']),
            (b+'BOM',stages['procurement']),(b+'manufacturing',stages['cost'])):edge(src,dst)
        for a,z in (('drive-electrothermal','journey'),('journey','civil-loads'),('civil-loads','civil-geometry'),
            ('civil-geometry','cost'),('civil-geometry','control'),('procurement','cost'),('journey','control'),('control','service'),('cost','service'),('service','city'),('city','publication')):edge(stages[a],stages[z])
    value=dict(schema='osr-candidate-dependency-invalidation-graph/1',nodes=sorted(nodes.values(),key=lambda x:x['node_id']),
        edges=[dict(upstream=a,downstream=b) for a,b in sorted(edges)],automatic_redesign_or_release_allowed=False)
    value['graph_id']=identity(value);return value


def invalidate(graph,changes):
    if graph.get('graph_id')!=identity({k:v for k,v in graph.items() if k!='graph_id'}):raise ValueError('Exact dependency graph required')
    lookup={n['node_id']:n for n in graph['nodes']};adj=defaultdict(list)
    for e in graph['edges']:
        if e['upstream'] not in lookup or e['downstream'] not in lookup:raise ValueError('Graph has missing dependencies')
        adj[e['upstream']].append(e['downstream'])
    if not isinstance(changes,list) or not changes:raise ValueError('Explicit revision changes required')
    changed=[];physical=False
    for change in changes:
        if set(change)!={'node_id','old_revision_id','new_revision_id','change_kind'} or change['node_id'] not in lookup:raise ValueError('Exact known node revision required')
        if change['old_revision_id']!=lookup[change['node_id']]['revision_id'] or change['new_revision_id'] is not None and not _sha(change['new_revision_id']):raise ValueError('Old binding or new immutable revision differs')
        if change['change_kind'] not in ('physical','evaluator','supplier-evidence','requirement'):raise ValueError('Declared physical/evaluator/evidence/requirement change required')
        if change['new_revision_id']==change['old_revision_id']:continue
        changed.append(change['node_id']);physical=physical or change['change_kind']=='physical'
    invalid=set(changed);todo=list(changed)
    while todo:
        for n in adj[todo.pop()]:
            if n not in invalid:invalid.add(n);todo.append(n)
    r=dict(schema='osr-bound-dependency-invalidation/1',parent_graph_id=graph['graph_id'],changes=deepcopy(changes),
        changed_nodes=sorted(changed),invalidated_nodes=sorted(invalid),invalidated_kinds=sorted({lookup[n]['kind'] for n in invalid}),
        affected_scopes=sorted({s for n in invalid for s in lookup[n]['scopes']}),physical_candidate_revision_required=physical,
        evaluations_must_be_recomputed=bool(invalid),cached_outputs_reusable=not invalid,automatic_selection_allowed=False,**FLAGS)
    r['evaluation_id']=identity(r);return r


def _snapshot(path,epoch):
    with tarfile.open(path,'r:gz') as archive:
        members=archive.getmembers();names=[m.name for m in members]
        if len(names)!=len(set(names)) or set(names)!=set(epoch):raise ValueError('Saved source archive inventory differs')
        total=0
        for member in members:
            n=PurePosixPath(member.name);total+=member.size
            if not member.isfile() or n.is_absolute() or '..' in n.parts or '\\' in member.name or member.size>64*1024**2 or total>512*1024**2:raise ValueError('Unsafe or oversized saved source archive')
            if hashlib.sha256(archive.extractfile(member).read()).hexdigest()!=epoch[member.name]:raise ValueError('Saved source bytes differ from recorded epoch')


def build(state,*,native=(),root=ROOT,require_current_source=True):
    """Inspect actual saved inputs/results without running any model generator."""
    from . import coordinator
    from engineering.railway_twin import pipeline
    folder=Path(state)
    if digest(Path(root)/CODE)!=digest(__file__):raise ValueError('Executing closure producer differs from declared source root')
    if folder.is_symlink():raise ValueError('Ordinary saved state required')
    run=_read(_path(folder,'latest.json'));_sealed(run,'run_id');epoch=run['source_sha256'];current=coordinator.sources(root)==epoch
    if require_current_source and not current:raise ValueError('Closure state source epoch differs from current producers')
    # Archive verification uses recorded bytes, not an invented verification flag.
    _snapshot(_path(folder,'input-sources.tar.gz'),epoch)
    requests=[r['request'] for r in run['cases']]+run['pending'];request_ids=list(map(identity,requests))
    if len(request_ids)!=len(set(request_ids)):raise ValueError('Saved executed/pending requests overlap')
    if current and sorted(request_ids)!=sorted(map(identity,coordinator.plan())):raise ValueError('Saved case/pending coverage differs')
    cases=[];vehicles={};inputs={'latest.json':digest(folder/'latest.json'),'input-sources.tar.gz':digest(_path(folder,'input-sources.tar.gz'))}
    for row in run['cases']:
        req=row['request'];expected='cases/'+identity(dict(request=req,source=epoch))+'.json.gz'
        if row['path']!=expected:raise ValueError('Noncanonical saved case path')
        path=_path(folder,expected);case=_read(path);_sealed(case)
        if case['source_sha256']!=epoch or any(row[k]!=case[v] for k,v in (('candidate_id','candidate_id'),('evaluation_id','evaluation_id'),('arrivals','conditional_arrivals'),('motion_screens','conditional_motion_screens'))):raise ValueError('Saved case/source/summary differs')
        if case['qualified_journeys']!=0 or case['operating_map_admitted'] is not False:raise ValueError('Unsupported physical qualification claim')
        cid=case['candidate_id'];_sealed(case['bundle'],'definition_id')
        if case['bundle']['candidate_id']!=cid or any(case[k]['candidate_id']!=cid for k in ('civil','manufacturing','partial_public_price')):raise ValueError('Mixed downstream candidate')
        name='vehicles/'+req['vehicle_id']+'.json.gz'
        if req['vehicle_id'] not in vehicles:
            e=_read(_path(folder,name));_sealed(e);v=e['vehicle'];_sealed(v);validate_registry(v['registry'])
            if e['candidate_id']!=v['candidate_id'] or v['candidate_id']!=v['registry']['candidate_id']:raise ValueError('Mixed vehicle registry')
            vehicles[req['vehicle_id']]=e;inputs[name]=digest(folder/name)
        if case['body_candidate_id']!=vehicles[req['vehicle_id']]['vehicle']['candidate_id']:raise ValueError('Case uses another saved vehicle')
        for r in case['journeys']:
            result=r['result'];_sealed(result)
            if result['candidate_id']!=cid or result['bundle_definition_id']!=case['bundle']['definition_id'] or result['alternative_candidate_id']!=case['drive']['candidate_id']:raise ValueError('Mixed journey inputs')
            if result['qualified_numerical_arrival'] is not False or result['admitted_operating_map'] is not False:raise ValueError('Conditional trajectory cannot qualify hardware')
        cases.append(case);inputs[expected]=digest(path)
    actual={p.relative_to(folder).as_posix() for p in folder.rglob('*') if p.is_file() and p.name!='.coordinator.lock'}
    if actual!=set(inputs) or any(p.is_symlink() for p in folder.rglob('*')):raise ValueError('Unexpected or linked saved closure input')
    native_rows=[_native(d,root) for d in native]
    return _assemble(run,cases,vehicles,native_rows,inputs,current,root)


def _assemble(run,cases,vehicles,native,inputs,current,root):
    body={e['vehicle']['candidate_id']:e['vehicle'] for e in vehicles.values()};vehicle_rows=[]
    for cid,v in sorted(body.items()):
        reg=v['registry'];parts={p['physical_definition_id']:p for p in reg['parts']};occ=reg['occurrences'];counts=Counter(o['part_definition_id'] for o in occ)
        listed={o for c in cases if c['body_candidate_id']==cid for row in c['partial_public_price']['rows'] if row['unit_price_USD'] is not None for o in row['occurrence_ids']}
        ids={o['occurrence_id'] for o in occ}
        if not listed<=ids:raise ValueError('Priced occurrence belongs to another registry')
        known=fsum(p['mass']['calculated_kg']*counts[pid] for pid,p in parts.items() if p['mass']['calculated_kg'] is not None)
        exact=[n['package_id'] for n in native if n['candidate_id']==cid and n['vehicle_evaluation_id']==v['evaluation_id'] and n['source_epoch_current']]
        vehicle_rows.append(dict(body_candidate_id=cid,vehicle_evaluation_id=v['evaluation_id'],registry_id=reg['registry_id'],part_definitions=len(parts),occurrences=len(occ),
            located_occurrences=sum('transform' in o for o in occ),net_geometry_occurrences=sum(parts[o['part_definition_id']]['geometry']['kind']!='envelope' for o in occ),
            bounded_purchased_occurrences=sum(parts[o['part_definition_id']]['geometry']['kind']=='envelope' for o in occ),known_calculated_stock_kg=known,
            installed_mass_kg=None,installed_CG_m=None,installed_inertia_kg_m2=None,public_list_priced_occurrences=len(listed),
            public_price_occurrence_coverage=len(listed)/len(occ) if occ else None,authenticated_quotation_occurrences=0,
            current_exact_native_packages=exact,qualification='held-external-physical-evidence'))
    journey_rows=[]
    for case in cases:
        for row in case['journeys']:
            r=row['result'];arithmetic=None;residual=None
            if 'energy_J' in r:
                w=r['energy_J'];residual=w['traction']-fsum(w[k] for k in ('aerodynamic','rolling','gravity','brake'))-r['kinetic_energy_J']
                arithmetic=isfinite(residual) and abs(residual-r['discrete_work_kinetic_residual_J'])<=1e-8*max(1.,abs(w['traction']))
                if not arithmetic:raise ValueError('Retained work/kinetic residual does not reproduce')
            journey_rows.append(dict(candidate_id=case['candidate_id'],scenario=row['name'],evaluation_id=r['evaluation_id'],execution=r['execution'],
                numerical_validity='arithmetic-checked; timestep/model convergence unresolved' if arithmetic else 'not-evaluated',work_kinetic_residual_J=residual,
                engineering_screen=r.get('requested_service_screen_passed'),conditional_arrival=r['conditional_numerical_arrival'],
                source_maturity='B-published-component facts plus C-model/contact/control hypotheses',physical_qualification=False))
    m=[manufacturing_status(c) for c in cases]
    counts=dict(saved_cases=len(cases),pending_cases=len(run['pending']),saved_vehicle_candidates=len(vehicles),
        conditional_journeys=len(journey_rows),conditional_arrivals=sum(r['conditional_arrival'] for r in journey_rows),
        conditional_motion_screens=sum(r['engineering_screen'] is True for r in journey_rows),
        native_packages=len(native),native_completed=sum(n['execution'].startswith('completed') for n in native),
        current_exact_vehicle_native_matches=sum(len(v['current_exact_native_packages']) for v in vehicle_rows),
        provided_authenticated_physical_records=0,accepted_operating_maps=0,qualified_journeys=0,
        external_physical_record_availability=None,complete_installed_cost_USD=None,complete_whole_life_cost_USD=None)
    phases=[]
    for pid,title,wp,required in PHASES:
        selected={'P0':counts['saved_cases'],'P1':sum(v['part_definitions'] for v in vehicle_rows),'P2':len(vehicle_rows),
            'P3':len({c['drive']['candidate_id'] for c in cases}),'P4':len(journey_rows),'P5':len(cases),'P6':sum(x['routing_groups'] for x in m)}.get(pid)
        phases.append(dict(phase_id=pid,title=title,work_package=wp,provided_output_count=selected,
            execution='retained-calculations' if selected else 'no-execution-record-supplied',numerical_validity=None,
            engineering_screen='open-requirements-and-physical-correlation',source_maturity='mixed-published-and-hypothesis' if selected else 'not-demonstrated-in-supplied-records',
            physical_qualification=False,required_inputs=required,completion=None))
    wps=[dict(work_package='WP'+str(i),phase_ids=[p['phase_id'] for p in phases if p['work_package']=='WP'+str(i)],
        software_outputs='source-bound supplied records and dependency graph',physical_completion=None,physical_qualified=False) for i in range(1,7)]
    result=dict(schema='osr-sourced-engineering-closure-dashboard/1',run_id=run['run_id'],source_epoch_current=current,current_plan_coverage_verified=current,
        input_files_sha256=inputs,counts=counts,vehicles=vehicle_rows,journeys=journey_rows,native_results=native,
        phases=phases,work_packages=wps,manufacturing_exports=m,required_test_inputs=deepcopy(TEST_INPUTS),
        dependency_graph=dependency_graph(cases,vehicles,native),design_complete_percentage=None,
        unintegrated_research_proposals=[dict(integrated_case_candidate_id=c['candidate_id'],included_in_integrated_candidate=False,
            proposal=deepcopy(c['charging_proposal']),pending='Vehicle converter/charger mass, wiring, civil supply, hot derating, costs and interlocks require a separate physical integration revision') for c in cases if c.get('charging_proposal') is not None],
        source_sha256={CODE:digest(Path(root)/CODE)},limitations=['Read-only recorded evidence accounting; no fresh numerical/native or physical execution',
            'Verified archive bytes and benchmark arithmetic do not approve material, manufactured hardware or railway operation',
            'Listed native packages only cover current inputs when candidate, vehicle evaluation and evaluator source all match',
            'Provided physical/quote/HIL/site evidence counts apply to this packet; external availability remains unknown'],**FLAGS)
    result['evaluation_id']=identity(result);return result
