"""Pure wheel-candidate business contracts; no Frappe imports or authority.

Engineering records use their original newline-terminated canonical identity.
This business protocol uses the existing integration SHA convention (no newline).
"""
from copy import deepcopy
from decimal import Decimal, ROUND_CEILING, ROUND_HALF_UP
from hashlib import sha256
import json
import math
from pathlib import PurePosixPath
import re

FLAGS = dict(physical_accepted=False, engineering_accepted=False,
             manufacturing_release=False, operating_release=False,
             movement_authority=False, physical_evidence=False)
IDENTITIES = {'candidate_id', 'bundle_evaluation_id', 'study_id', 'engineering_revision',
    'body_candidate_id', 'source_body_bundle_id', 'installed_component_candidate_id',
    'installed_mass_evaluation_id', 'civil_candidate_id', 'civil_evaluation_id',
    'service_evaluation_id', 'cost_evaluation_id', 'lifecycle_evaluation_id'}
DOCUMENT_TYPES = {'drawing', 'inspection', 'routing'}
MAX_COMPONENTS = 4000
MAX_ARTIFACT_BYTES = 32 * 1024**2
MAX_PACK_BYTES = 16 * 1024**2
UOMS = {'Nos', 'Kg', 'Meter', 'Square Meter', 'Cubic Meter'}
UNIT_MAP = {'each':'Nos', 'kg':'Kg', 'm':'Meter', 'm2':'Square Meter', 'm3':'Cubic Meter'}


def encoded(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()


def digest(value):
    return sha256(encoded(value)).hexdigest()


def engineering_digest(value):
    return sha256(encoded(value) + b'\n').hexdigest()


def seal(value):
    result=deepcopy(value);result['sha256']=digest(result);return result


def sealed(value):
    if not isinstance(value,dict) or value.get('sha256') != digest({k:v for k,v in value.items() if k!='sha256'}):
        raise ValueError('Business contract checksum differs')
    return value


def hash_id(value, label='identity'):
    if not isinstance(value,str) or re.fullmatch('[0-9a-f]{64}',value) is None:
        raise ValueError('Exact SHA256 '+label+' required')
    return value


def text(value, label='text', maximum=1000):
    if not isinstance(value,str) or not value.strip() or len(value)>maximum or '\x00' in value:
        raise ValueError('Bounded nonempty '+label+' required')
    return value


def identities(value):
    if not isinstance(value,dict) or set(value)!=IDENTITIES:
        raise ValueError('Complete explicit railway candidate binding required')
    for name,item in value.items():hash_id(item,name)
    return value


def flags(value):
    if any(value.get(k) is not False for k in FLAGS):
        raise ValueError('Business research records cannot confer physical authority')


def safe_path(value):
    text(value,'artifact path',1024);p=PurePosixPath(value)
    if p.is_absolute() or '..' in p.parts or '\\' in value or str(p)!=value or value=='.':
        raise ValueError('Ordinary relative artifact path required')
    return value


def number(value, label, *, positive=False):
    if type(value) not in (int,float) or not math.isfinite(value) or (value<=0 if positive else value<0):
        raise ValueError('Finite '+('positive ' if positive else 'nonnegative ')+label+' required')
    return value


def validate_document(value, source_part, binding):
    required={'schema','document_type','identities','part_id','component_definition_id',
        'source_part_sha256','revision','maturity','payloads','research_holds',*FLAGS}
    kind=value.get('document_type')
    extra={'characteristics'} if kind=='inspection' else {'operations'} if kind=='routing' else set()
    if set(value)!=required|extra or value['schema']!='osr-controlled-research-document/1' or kind not in DOCUMENT_TYPES:
        raise ValueError('Controlled drawing/inspection/routing document contract required')
    flags(value);identities(value['identities'])
    if (value['identities']!=binding or value['part_id']!=source_part['id'] or
            value['component_definition_id']!=source_part['component_definition_id'] or
            value['source_part_sha256']!=engineering_digest(source_part)):
        raise ValueError('Controlled document belongs to another source part/candidate')
    if value['maturity']!='controlled-research-draft':raise ValueError('Explicit research document maturity required')
    text(value['revision'],'document revision',100)
    if not isinstance(value['research_holds'],list) or any(not isinstance(x,str) or not x.strip() for x in value['research_holds']):
        raise ValueError('Research holds must be explicit strings, including an empty list when none declared')
    payloads=value['payloads']
    if not isinstance(payloads,list) or not 1<=len(payloads)<=12:raise ValueError('Real controlled artifact payloads required')
    seen=set()
    for row in payloads:
        if set(row)!={'path','sha256','bytes','media_type'}:raise ValueError('Exact controlled artifact metadata required')
        safe_path(row['path']);hash_id(row['sha256']);text(row['media_type'],'media type',100)
        if row['path'] in seen or type(row['bytes']) is not int or not 0<row['bytes']<=MAX_ARTIFACT_BYTES:
            raise ValueError('Duplicate, empty or oversized controlled artifact')
        seen.add(row['path'])
    if kind=='inspection':
        rows=value['characteristics'];seen=set()
        if not isinstance(rows,list) or not 1<=len(rows)<=200:raise ValueError('Explicit inspection characteristics required')
        for row in rows:
            if set(row)!={'id','name','unit','minimum','maximum','method','evidence_maturity'}:
                raise ValueError('Inspection characteristic fields differ')
            for k in ('id','name','unit','method'):text(row[k],k,500)
            if row['id'] in seen:raise ValueError('Duplicate inspection characteristic')
            seen.add(row['id'])
            for k in ('minimum','maximum'):
                if row[k] is not None and (type(row[k]) not in (int,float) or not math.isfinite(row[k])):
                    raise ValueError('Finite or explicitly unknown inspection limit required')
            if row['minimum'] is None and row['maximum'] is None:raise ValueError('At least one declared research inspection limit required')
            if row['minimum'] is not None and row['maximum'] is not None and row['minimum']>row['maximum']:
                raise ValueError('Ordered inspection limits required')
            if row['evidence_maturity']!='calculated-research-limit':raise ValueError('No measured inspection limit inferred')
    if kind=='routing':
        rows=value['operations'];seen=set()
        if not isinstance(rows,list) or not 1<=len(rows)<=200:raise ValueError('Explicit routing operations required')
        for row in rows:
            if set(row)!={'sequence','operation','workstation','tools','setup_minutes','run_minutes_per_unit','time_basis','inspection_ids'}:
                raise ValueError('Routing operation fields differ')
            if type(row['sequence']) is not int or row['sequence']<=0 or row['sequence'] in seen:raise ValueError('Unique positive operation sequence required')
            seen.add(row['sequence'])
            for k in ('operation','workstation','time_basis'):text(row[k],k,1000)
            if not isinstance(row['tools'],list) or not row['tools'] or any(not isinstance(x,str) or not x.strip() for x in row['tools']):
                raise ValueError('Explicit tools/fixtures required')
            number(row['setup_minutes'],'setup time');number(row['run_minutes_per_unit'],'run time',positive=True)
            if not isinstance(row['inspection_ids'],list):raise ValueError('Inspection hold points must be explicit')
    return value


def stock_lines(mapping, source_part=None):
    """One source-priced workpiece or explicitly quantified cut-stock rows.

    Source-priced workpiece valuation already owns processing allowances; native
    routing time is non-additive resource information, never zero labour cost.
    """
    mode=mapping['valuation_mode'];rows=[]
    if mode not in {'source-priced-workpiece','quantified-source-stock'}:
        raise ValueError('Explicit valuation mode required')
    source=source_part if source_part is not None else mapping['source_part'];quantity=source['quantity_per_train']
    exact_rate=source['counted_direct_parts_process_usd_per_train']['base']/quantity
    if mode=='source-priced-workpiece':
        if mapping.get('stock_inputs') not in (None,[]):raise ValueError('Source-priced workpiece cannot add raw costs again')
        unit=UNIT_MAP.get(source['unit'])
        if unit is None:raise ValueError('Explicit reviewed source/native UOM conversion required')
        inputs=[dict(id=source['id'],uom=unit,net_quantity=1.,gross_quantity=1.,waste_fraction=0.,
            unit_rate_usd=exact_rate,source_sha256=engineering_digest(source),
            basis='One counted source-priced workpiece; existing direct part/process account retained once, not raw-material procurement or complete train price')]
    else:
        inputs=mapping.get('stock_inputs')
        if not isinstance(inputs,list) or not inputs or len(inputs)>100:raise ValueError('Reviewed quantified stock rows required')
    seen=set()
    for row in inputs:
        if set(row)!={'id','uom','net_quantity','gross_quantity','waste_fraction','unit_rate_usd','source_sha256','basis'}:
            raise ValueError('Explicit stock quantity/yield/rate/source fields required')
        text(row['id'],'stock ID');text(row['basis'],'stock basis');hash_id(row['source_sha256'])
        if row['id'] in seen or row['uom'] not in UOMS:raise ValueError('Duplicate stock or unknown UOM')
        seen.add(row['id'])
        net=number(row['net_quantity'],'net quantity',positive=True);gross=number(row['gross_quantity'],'gross quantity',positive=True)
        waste=number(row['waste_fraction'],'waste fraction');rate=number(row['unit_rate_usd'],'unit rate',positive=True)
        if waste>=1 or not math.isclose(net,gross*(1-waste),rel_tol=1e-10,abs_tol=1e-12):
            raise ValueError('Net/gross/yield balance differs')
        native_quantity=float(Decimal(str(gross)).quantize(Decimal('.001'),rounding=ROUND_CEILING))
        native_rate=float(Decimal(str(rate)).quantize(Decimal('.000001'),rounding=ROUND_HALF_UP))
        if native_rate<=0:raise ValueError('Native precision cannot turn a positive cost into zero')
        rows.append(dict(row,engineering_gross_quantity=gross,engineering_unit_rate_usd=rate,
            quantity=native_quantity,rate=native_rate,extended_usd=native_quantity*native_rate,
            quantity_resolution=.001,rate_resolution_usd=.000001,
            rounding_basis='Gross consumption up to0.001unit; unquoted source rate half-up toUSD0.000001; exact engineering quantities retained'))
    actual=sum(r['gross_quantity']*r['unit_rate_usd'] for r in rows)
    if mode=='quantified-source-stock':
        allowance=mapping.get('direct_process_allowance_usd')
        number(allowance,'explicit direct process allowance')
        if not math.isclose(actual+allowance,exact_rate,rel_tol=1e-9,abs_tol=1e-7):
            raise ValueError('Source direct cost and stock/process decomposition differ')
    elif mapping.get('direct_process_allowance_usd') is not None:
        raise ValueError('Source-priced workpiece processing is already included, not zero or an additional allowance')
    return rows


def validate_pack(value):
    sealed(value);flags(value);identities(value['identities'])
    if value.get('schema')!='osr-wheel-delivery-review-pack/1' or value.get('environment')!='simulation':
        raise ValueError('Explicit simulation-only wheel delivery review pack required')
    if len(encoded(value))>MAX_PACK_BYTES:raise ValueError('Review pack byte limit exceeded')
    hash_id(value['proposal_id']);hash_id(value['proposal_sha256']);text(value['city'],'city',100)
    components=value['components']
    if not isinstance(components,list) or not components or len(components)>MAX_COMPONENTS:raise ValueError('Bounded nonempty component scope required')
    seen=set();artifact_closure={}
    for row in components:
        source=row['source_part'];part=source['id']
        if part in seen or source['identities']!=value['identities'] or row['source_part_sha256']!=engineering_digest(source):
            raise ValueError('Mixed, changed or duplicate source component')
        seen.add(part);hash_id(source['component_definition_id'])
        if set(row['documents'])!=DOCUMENT_TYPES:raise ValueError('Drawing/inspection/routing documents required per covered component')
        for kind,entry in row['documents'].items():
            safe_path(entry['path']);hash_id(entry['sha256']);validate_document(entry['definition'],source,value['identities'])
            if entry['definition']['document_type']!=kind:raise ValueError('Document kind differs')
            if type(entry['bytes']) is not int or not 0<entry['bytes']<=2*1024**2:raise ValueError('Bounded sidecar bytes required')
            additions=[dict(path=entry['path'],sha256=entry['sha256'],bytes=entry['bytes'],media_type='application/json',role='controlled-'+kind+'-metadata')]
            additions += [dict(item,role=kind+'-payload') for item in entry['definition']['payloads']]
            for item in additions:
                if item['path'] in artifact_closure and artifact_closure[item['path']]!=item:raise ValueError('Conflicting artifact ownership')
                artifact_closure[item['path']]=item
        chars={r['id'] for r in row['documents']['inspection']['definition']['characteristics']}
        if any(not set(op['inspection_ids'])<=chars for op in row['documents']['routing']['definition']['operations']):
            raise ValueError('Routing references missing inspection characteristic')
        if row['stock_lines']!=stock_lines(row['conversion'],source):raise ValueError('Native stock conversion changed')
        if row['conversion']['source_part_sha256']!=engineering_digest(source):raise ValueError('Conversion belongs to another source part')
        for flag in ('native_orders_released','physical_manufacture_validated'):
            if row.get(flag) is not False:raise ValueError('Review pack cannot release production')
    if 'assemblies' in value:
        validate_assemblies(value['assemblies'],{r['source_part']['id']:r['source_part'] for r in components},value['identities'],value['proposal_id'])
    coverage=value['coverage']
    missing=sorted(set(coverage['source_part_ids'])-seen)
    if (coverage['covered_part_ids']!=sorted(seen) or coverage['uncovered_part_ids']!=missing or
            coverage['complete'] is not (not missing) or not seen<=set(coverage['source_part_ids'])):
        raise ValueError('Partial component coverage cannot become complete')
    if value['artifacts'] != [artifact_closure[k] for k in sorted(artifact_closure)]:raise ValueError('Controlled artifact dependency closure differs')
    return value


def validate_context(value):
    sealed(value);flags(value);identities(value['identities'])
    if value.get('schema')!='osr-wheel-delivery-project/1' or value['environment']!='simulation':raise ValueError('Simulation project context required')
    for key in ('project','company','city'):text(value[key],key,150)
    hash_id(value['proposal_id']);hash_id(value['proposal_sha256'])
    if type(value['project_trainsets']) is not int or value['project_trainsets']<1:raise ValueError('Explicit project fleet required')
    for name,row in value['source_patterns'].items():
        text(name,'source pattern')
        if row['part_id'] not in value['source_parts'] or type(row['count_per_train']) is not int or row['count_per_train']<1:
            raise ValueError('Counted source pattern required')
    if 'source_assemblies' in value:
        quantities={}
        for row in value['source_patterns'].values():quantities[row['part_id']]=quantities.get(row['part_id'],0)+row['count_per_train']
        validate_assemblies(list(value['source_assemblies'].values()),{k:{'quantity_per_train':v} for k,v in quantities.items()},value['identities'],value['proposal_id'])
        if any(k!=v['id'] for k,v in value['source_assemblies'].items()):raise ValueError('Source assembly dictionary identity differs')
        if value.get('assembly_patterns')!=assembly_patterns(value['source_assemblies']):raise ValueError('Counted assembly patterns differ')
    return value


def bind_pack(pack, context):
    validate_pack(pack);validate_context(context)
    if any(pack[k]!=context[k] for k in ('identities','proposal_id','proposal_sha256','environment','city')):
        raise ValueError('Pack differs from authoritative native project source')
    if pack['coverage']['source_part_ids']!=sorted(context['source_parts']):raise ValueError('Pack source coverage differs from authoritative project')
    for row in pack['components']:
        if context['source_parts'].get(row['source_part']['id'])!=row['source_part_sha256']:
            raise ValueError('Part differs from authoritative native project source')
    for node in pack.get('assemblies',[]):
        if context.get('source_assemblies',{}).get(node['id'])!=node:
            raise ValueError('Assembly differs from authoritative native project source')
    return True


def business_handback(context, observed, *, actor):
    """Validate authenticated native readback; never grant railway authority."""
    validate_context(context)
    if observed['project']!=context['project'] or observed['company']!=context['company'] or observed['identities']!=context['identities']:
        raise ValueError('Handback belongs to another project/candidate')
    if actor!=observed['reviewer'] or actor in {observed['inspector'],observed['proposer']}:
        raise ValueError('Authenticated independent business reviewer required')
    if (observed['latest_qa_docstatus']!=1 or observed['latest_qa_status']!='Accepted' or
            observed['repair_docstatus']!=1 or observed['repair_status']!='Completed' or
            observed['installation_docstatus']!=1 or observed['installed_serial']!=observed['manufactured_serial'] or
            not observed['physical_handback_required']):
        raise ValueError('Latest native QA, serial installation, repair and physical hold required')
    for key in ('latest_qa','installed_serial','installation_record','repair','review_task'):
        text(observed[key],key,150)
    return seal(dict(schema='osr-wheel-business-handback/1',context_sha256=context['sha256'],
        native_readback=deepcopy(observed),authenticated_actor=actor,
        business_state='simulation-business-reviewed',**FLAGS))


MAX_ASSEMBLIES=128
MAX_ASSEMBLY_EDGES=4000
MAX_ASSEMBLY_DEPTH=8


def validate_assemblies(nodes,parts,binding,proposal_id):
    """Validate a bounded, disjoint counted hierarchy; return child-first order.

    Parts are already source-verified review components (or counted context
    projections). Assembly definitions do not establish installed placement.
    """
    if not isinstance(nodes,list) or len(nodes)>MAX_ASSEMBLIES:raise ValueError('Bounded assembly hierarchy required')
    if len(encoded(nodes))>MAX_PACK_BYTES:raise ValueError('Assembly hierarchy byte budget exceeded')
    by_id={};owners={};edge_count=0
    for node in nodes:
        if set(node)!={'id','identities','quantity_per_train','occurrence_ids','children','source_reference','research_holds','definition_id'}:
            raise ValueError('Explicit source assembly definition required')
        name=text(node['id'],'assembly id',150)
        if name in by_id or name in parts:raise ValueError('Duplicate assembly/part ownership')
        if node['identities']!=binding or node['definition_id']!=engineering_digest({k:v for k,v in node.items() if k!='definition_id'}):
            raise ValueError('Mixed or changed assembly definition')
        ref=node['source_reference']
        if (not isinstance(ref,dict) or ref.get('proposal_id')!=proposal_id or
            ref.get('scope')!='source-authoritative-proposal-reference-only' or ref.get('physical_module_id') is not None):
            raise ValueError('Source proposal assembly reference required; no physical module identity inferred')
        q=node['quantity_per_train'];occ=node['occurrence_ids']
        if type(q) is not int or q<1 or not isinstance(occ,list) or len(occ)!=q or len(set(occ))!=len(occ):
            raise ValueError('Exact counted assembly occurrences required')
        for item in occ:text(item,'assembly occurrence',500)
        if not isinstance(node['research_holds'],list) or not node['research_holds'] or any(not isinstance(x,str) or not x.strip() for x in node['research_holds']):
            raise ValueError('Explicit research assembly holds required')
        if not isinstance(node['children'],list) or not node['children']:raise ValueError('Nonempty counted assembly children required')
        for edge in node['children']:
            if set(edge)!={'kind','id','quantity'} or edge['kind'] not in ('part','assembly') or type(edge['quantity']) is not int or edge['quantity']<1:
                raise ValueError('Typed positive integer assembly edge required')
            key=(edge['kind'],text(edge['id'],'child id',150));edge_count+=1
            if key in owners:raise ValueError('Duplicate assembly child ownership')
            owners[key]=name
        by_id[name]=node
    if edge_count>MAX_ASSEMBLY_EDGES:raise ValueError('Assembly edge work budget exceeded')
    order=[];active=set();done=set();height={}
    def visit(name,depth):
        if depth>MAX_ASSEMBLY_DEPTH:raise ValueError('Assembly depth budget exceeded')
        if name in active:raise ValueError('Cyclic assembly hierarchy')
        if name in done:
            if depth+height[name]-1>MAX_ASSEMBLY_DEPTH:raise ValueError('Assembly depth budget exceeded')
            return
        active.add(name);node=by_id[name]
        for edge in node['children']:
            if edge['kind']=='assembly':
                if edge['id'] not in by_id:raise ValueError('Missing child assembly')
                child=by_id[edge['id']]
                if child['quantity_per_train']!=node['quantity_per_train']*edge['quantity']:raise ValueError('Nested assembly source count differs')
                visit(edge['id'],depth+1)
            else:
                part=parts.get(edge['id'])
                if part is None:raise ValueError('Assembly child lacks reviewed source component')
                if part['quantity_per_train']!=node['quantity_per_train']*edge['quantity']:raise ValueError('Assembly source part count differs')
                if 'unit' in part and UNIT_MAP.get(part['unit'])!='Nos':raise ValueError('Counted assembly leaves require discrete workpieces')
        height[name]=1+max((height[e['id']] for e in node['children'] if e['kind']=='assembly'),default=0)
        if depth+height[name]-1>MAX_ASSEMBLY_DEPTH:raise ValueError('Assembly depth budget exceeded')
        active.remove(name);done.add(name);order.append(node)
    for name in by_id:visit(name,1)
    return order


def assembly_patterns(nodes):
    return {digest(dict(assembly_id=name,definition_id=node['definition_id'],occurrence_id=occ)):
        dict(assembly_id=name,definition_id=node['definition_id'],occurrence_id=occ,count_per_train=1)
        for name,node in nodes.items() for occ in node['occurrence_ids']}


def native_valuation_rate(value):
    """Reviewed source estimate rounded to existing USD six-decimal policy."""
    number(value,'source valuation rate',positive=True)
    try:rate=float(Decimal(str(value)).quantize(Decimal('.000001'),rounding=ROUND_HALF_UP))
    except (ArithmeticError,ValueError,OverflowError) as exc:raise ValueError('Representable source valuation rate required') from exc
    if not math.isfinite(rate) or rate<=0:raise ValueError('Positive source rate cannot round to zero or nonfinite valuation')
    return rate
