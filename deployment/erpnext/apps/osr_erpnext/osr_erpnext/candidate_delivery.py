"""Authenticated, immutable wheel-candidate research delivery in native ERP.

The adapter creates reviewed drafts only. It never submits purchasing,
manufacturing, installation or movement authority. Native campaign transactions
are separate explicit actions in a disposable simulation site.
"""
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import re

import frappe
from . import candidate_delivery_contract as contract


def _role(name):
    if name not in frappe.get_roles():frappe.throw(name+' required',frappe.PermissionError)


def _json(value):
    return frappe.parse_json(value) if isinstance(value,str) else value


def _write(path,value):
    with path.open('x') as stream:json.dump(value,stream,sort_keys=True,separators=(',',':'),allow_nan=False)


def _context(project, *, write=False):
    if frappe.session.user=='Guest':frappe.throw('Authenticated project access required',frappe.PermissionError)
    doc=frappe.get_doc('Project',project);doc.check_permission('write' if write else 'read')
    folder=Path(frappe.get_site_path('private','files','osr-wheel-delivery',contract.digest(project)))
    context=contract.validate_context(json.loads((folder/'context.json').read_text()))
    if context['project']!=doc.name or context['company']!=doc.company or context['city']!=doc.custom_osr_city:
        frappe.throw('Controlled project/city/company binding changed')
    if frappe.session.user!='Administrator':
        policy=(frappe.conf.get('osr_integration_users') or {}).get(frappe.session.user,{})
        if (context['city'] not in policy.get('cities',[]) or context['environment'] not in policy.get('environments',[]) or
                project not in policy.get('projects',[])):
            frappe.throw('City, project and simulation environment access required',frappe.PermissionError)
    if write:
        # Serialise mutable software indexes and draft creation through the
        # authoritative native project transaction, not a browser revision.
        frappe.db.sql('SELECT name FROM `tabProject` WHERE name=%s FOR UPDATE',(project,))
    return doc,context,folder


def provision_project(project,context):
    """Explicit administrator provisioning, not a public candidate-selection API.

    The caller obtains this context from the verified source proposal compiler.
    A different candidate/revision requires a separate reviewed project; no
    existing orders or mappings are migrated by changing a current pointer.
    """
    if frappe.session.user!='Administrator':frappe.throw('Explicit administrator provisioning required',frappe.PermissionError)
    context=contract.validate_context(_json(context));doc=frappe.get_doc('Project',project);doc.check_permission('write')
    if (context['project']!=project or context['company']!=doc.company or context['city']!=doc.custom_osr_city):
        frappe.throw('Provisioned source must match native project/company/city')
    folder=Path(frappe.get_site_path('private','files','osr-wheel-delivery',contract.digest(project)))
    folder.mkdir(parents=True,exist_ok=True);target=folder/'context.json'
    if target.exists():
        if json.loads(target.read_text())!=context:frappe.throw('Project source binding is immutable; create a separately reviewed revision project')
    else:_write(target,context)
    return dict(context_sha256=context['sha256'],**contract.FLAGS)


def _files(project, pack, file_map):
    """Read actual native private File content, never client hash assertions."""
    wanted={r['path']:r for r in pack['artifacts']}
    if not isinstance(file_map,dict) or set(file_map)!=set(wanted):frappe.throw('Exact controlled artifact File mapping required')
    records=[];document_sets=[c['documents'] for c in pack['components']]+list(pack.get('assembly_documents',{}).values())
    definitions={e['path']:e['definition'] for docs in document_sets for e in docs.values()}
    for name in sorted(wanted):
        entry=wanted[name];doc=frappe.get_doc('File',file_map[name]);doc.check_permission('read')
        if doc.attached_to_doctype!='Project' or doc.attached_to_name!=project or not doc.is_private:
            frappe.throw('Controlled artifacts must be private Files attached to this exact project')
        raw=doc.get_content();raw=raw.encode() if isinstance(raw,str) else raw
        if len(raw)!=entry['bytes'] or sha256(raw).hexdigest()!=entry['sha256']:
            frappe.throw('Controlled native artifact bytes differ: '+name)
        if name in definitions and json.loads(raw)!=definitions[name]:frappe.throw('Controlled sidecar differs from review pack')
        records.append(dict(path=name,name=doc.name,sha256=entry['sha256'],bytes=len(raw),modified=str(doc.modified)))
    return records


@frappe.whitelist(methods=['POST'])
def register_pack(project,pack,files):
    """Propose an exact source/file set; independent review remains required."""
    _role('Manufacturing Manager');doc,context,folder=_context(project,write=True)
    pack=contract.validate_pack(_json(pack));contract.bind_pack(pack,context);files=_json(files)
    observations=_files(project,pack,files)
    record=contract.seal(dict(schema='osr-wheel-native-review-registration/1',project=project,
        context_sha256=context['sha256'],pack=pack,files=files,file_snapshot=observations,
        proposed_by=frappe.session.user,**contract.FLAGS))
    target=folder/('pack-'+pack['sha256']+'.json')
    if target.exists():
        old=json.loads(target.read_text());contract.sealed(old)
        if any(old[k]!=record[k] for k in ('pack','files','file_snapshot','context_sha256')):
            frappe.throw('Registered candidate/artifact set cannot be overwritten')
        return dict(registered=False,pack_sha256=pack['sha256'],proposed_by=old['proposed_by'],**contract.FLAGS)
    _write(target,record)
    return dict(registered=True,pack_sha256=pack['sha256'],proposed_by=record['proposed_by'],**contract.FLAGS)


def _pack(project,pack_sha256,write=False):
    contract.hash_id(pack_sha256);doc,context,folder=_context(project,write=write)
    record=contract.sealed(json.loads((folder/('pack-'+pack_sha256+'.json')).read_text()))
    if record['context_sha256']!=context['sha256']:frappe.throw('Registered project revision differs')
    contract.bind_pack(record['pack'],context)
    current=_files(project,record['pack'],record['files'])
    if current!=record['file_snapshot']:frappe.throw('Controlled artifact changed after registration; propose a new reviewed revision')
    return doc,context,folder,record


def _specs(project,pack,item_group):
    company=frappe.get_doc('Company',project.company);company.check_permission('read')
    if company.default_currency!='USD':frappe.throw('Reviewed USD source requires a USD company; explicit reviewed FX conversion is unavailable')
    group=frappe.get_doc('Item Group',item_group);group.check_permission('read')
    if group.is_group:frappe.throw('Select a leaf Item Group')
    prefix='SIM-WD-'+contract.digest([project.name,pack['sha256']])[:12].upper()
    items=[];boms=[];stations=[];operations=[];routes=[];components=[]
    for component in pack['components']:
        source=component['source_part'];short=contract.digest(source['id'])[:10].upper();base=prefix+'-'+short
        provenance=json.dumps(dict(schema='osr-wheel-native-source/1',pack_sha256=pack['sha256'],
            component_id=source['id'],component_definition_id=source['component_definition_id'],
            source_part_sha256=component['source_part_sha256'],identities=pack['identities'],
            cost_basis=source['cost_basis'],valuation_mode=component['conversion']['valuation_mode'],
            maturity='controlled-research-draft',research_holds=sorted({hold for entry in component['documents'].values()
                for hold in entry['definition']['research_holds']}),
            native_routing_cost='non-additive source-account allocation; no zero-labour claim',**contract.FLAGS),sort_keys=True)
        raw=[]
        for i,line in enumerate(component['stock_lines']):
            code=base+'-R'+str(i+1)
            items.append(dict(doctype='Item',item_code=code,item_name=('SIM stock '+source['name'])[:140],
                item_group=item_group,stock_uom=line['uom'],is_stock_item=1,is_purchase_item=1,
                inspection_required_before_purchase=1,valuation_rate=contract.native_valuation_rate(line['rate']),description=provenance))
            raw.append(dict(item_code=code,qty=line['quantity'],rate=line['rate'],uom=line['uom']))
        fg=base+'-FG';items.append(dict(doctype='Item',item_code=fg,item_name=('SIM '+source['name'])[:140],
            item_group=item_group,stock_uom=contract.UNIT_MAP[source['unit']],is_stock_item=1,
            has_serial_no=1,has_batch_no=1,valuation_rate=contract.native_valuation_rate(source['counted_direct_parts_process_usd_per_train']['base']/source['quantity_per_train']),description=provenance))
        route_rows=[];steps=component['documents']['routing']['definition']['operations']
        process_allowance=(component['conversion']['direct_process_allowance_usd']
            if component['conversion']['valuation_mode']=='quantified-source-stock' else 0.)
        total_minutes=sum(s['setup_minutes']+s['run_minutes_per_unit'] for s in steps)
        process_hour_rate=process_allowance*60/total_minutes
        for i,step in enumerate(steps):
            station=base+'-WS'+str(i+1);operation=base+'-OP'+str(i+1)
            stations.append(dict(doctype='Workstation',workstation_name=station,description=step['workstation'],
                production_capacity=1,hour_rate_labour=process_hour_rate))
            operations.append(dict(doctype='Operation',name=operation,description=step['operation'],workstation=station))
            # Cost already resides in source-priced inputs or a separately
            # declared process allowance. Time is resource information; no
            # extra price is added to the existing project ledger here.
            route_rows.append(dict(operation=operation,workstation=station,
                time_in_mins=step['setup_minutes']+step['run_minutes_per_unit'],hour_rate=process_hour_rate,description=step['operation']))
        routing=base+'-ROUTE';routes.append(dict(doctype='Routing',routing_name=routing,operations=route_rows))
        boms.append(dict(doctype='BOM',item=fg,company=project.company,quantity=1,currency='USD',
            with_operations=1,routing=routing,items=raw,operations=route_rows))
        components.append(dict(part_id=source['id'],finished_item=fg,raw_items=[r['item_code'] for r in raw],
            routing=routing,quantity_per_train=source['quantity_per_train'],quantity_project=source['quantity_project'],
            source_unit=source['unit'],source_direct_usd_per_unit=source['counted_direct_parts_process_usd_per_train']['base']/source['quantity_per_train'],
            native_stock_usd_per_unit=sum(r['qty']*r['rate'] for r in raw),
            native_fg_valuation_rate_usd=contract.native_valuation_rate(source['counted_direct_parts_process_usd_per_train']['base']/source['quantity_per_train']),
            native_direct_process_allowance_usd_per_unit=process_allowance,
            documents=component['documents']))
    extra={}
    if pack.get('assemblies'):
        source_parts={r['source_part']['id']:r['source_part'] for r in pack['components']}
        ordered=contract.validate_assemblies(pack['assemblies'],source_parts,pack['identities'],pack['proposal_id'])
        mapped={('part',r['part_id']):(r['finished_item'],r['native_fg_valuation_rate_usd']) for r in components}
        engineering_rates={('part',r['part_id']):r['source_direct_usd_per_unit'] for r in components}
        assemblies=[];links={}
        fleets={p['quantity_project']/p['quantity_per_train'] for p in source_parts.values()}
        if len(fleets)!=1 or not next(iter(fleets)).is_integer():frappe.throw('Exact shared project fleet required')
        fleet=int(next(iter(fleets)))
        for node in ordered:
            code=prefix+'-A'+contract.digest(node['id'])[:10].upper()
            provenance=json.dumps(dict(schema='osr-wheel-native-assembly-source/1',identities=pack['identities'],
                assembly_definition=node,maturity='controlled-research-draft',
                costing='Counted child direct subtotal only; assembly process cost remains unknown, not zero',**contract.FLAGS),sort_keys=True)
            native_subtotal=sum(edge['quantity']*mapped[(edge['kind'],edge['id'])][1] for edge in node['children'])
            exact_subtotal=sum(edge['quantity']*engineering_rates[(edge['kind'],edge['id'])] for edge in node['children'])
            native_valuation=contract.native_valuation_rate(native_subtotal)
            items.append(dict(doctype='Item',item_code=code,item_name=('SIM assembly '+node['id'])[:140],item_group=item_group,
                stock_uom='Nos',is_stock_item=1,has_serial_no=1,has_batch_no=1,valuation_rate=native_valuation,description=provenance))
            children=[dict(item_code=mapped[(edge['kind'],edge['id'])][0],qty=edge['quantity'],
                rate=mapped[(edge['kind'],edge['id'])][1],uom='Nos',do_not_explode=1) for edge in node['children']]
            boms.append(dict(doctype='BOM',item=code,company=project.company,quantity=1,currency='USD',with_operations=0,items=children))
            links[code]=[r['item_code'] for r in children]
            documents=pack.get('assembly_documents',{}).get(node['id'])
            if documents:
                route_rows=[]
                for i,step in enumerate(documents['routing']['definition']['operations']):
                    station=code+'-WS'+str(i+1);operation=code+'-OP'+str(i+1)
                    stations.append(dict(doctype='Workstation',workstation_name=station,description=step['workstation'],production_capacity=1,hour_rate_labour=0.))
                    operations.append(dict(doctype='Operation',name=operation,description=step['operation'],workstation=station))
                    route_rows.append(dict(operation=operation,workstation=station,time_in_mins=step['setup_minutes']+step['run_minutes_per_unit'],hour_rate=0.,description=step['operation']))
                routing=code+'-ROUTE';routes.append(dict(doctype='Routing',routing_name=routing,operations=route_rows))
                boms[-1].update(with_operations=1,routing=routing,operations=route_rows)
            subtotal=sum(r['qty']*r['rate'] for r in children)
            mapped['assembly',node['id']]=(code,native_valuation)
            engineering_rates['assembly',node['id']]=exact_subtotal
            assemblies.append(dict(assembly_id=node['id'],definition_id=node['definition_id'],finished_item=code,
                children=deepcopy(node['children']),child_items=[r['item_code'] for r in children],
                source_occurrence_ids=node['occurrence_ids'],quantity_per_train=node['quantity_per_train'],
                quantity_project=node['quantity_per_train']*fleet,counted_child_direct_subtotal_usd=exact_subtotal,
                native_child_direct_subtotal_usd=subtotal,native_valuation_rate_usd=native_valuation,
                assembly_process_cost_usd=None,complete_assembly_cost=False,physical_placement_verified=False,
                costing_scope='Hierarchical non-additive child subtotal; do not sum parent and descendant prices'))
            if documents:assemblies[-1]['documents']=documents
        owned={e['id'] for node in ordered for e in node['children'] if e['kind']=='assembly'}
        extra=dict(assemblies=assemblies,assembly_bom_links=links,assembly_roots=[node['id'] for node in ordered if node['id'] not in owned])
    return dict(items=items,workstations=stations,operations=operations,routings=routes,boms=boms,components=components,**extra)


def _required_permissions(*,create):
    for dt in ('Item','BOM','Workstation','Operation','Routing'):
        frappe.has_permission(dt,'read',throw=True)
        if create:frappe.has_permission(dt,'create',throw=True)


def _named(spec):
    return spec.get('item_code',spec.get('workstation_name',spec.get('routing_name',spec.get('name'))))


def _fields(value,template):
    """Retain selected native fields without mutable child-row bookkeeping."""
    if isinstance(template,list):
        if len(value)!=len(template):frappe.throw('Native child-row count differs')
        return [_fields(row,mask) for row,mask in zip(value,template)]
    if isinstance(template,dict):return {k:_fields(value.get(k),mask) for k,mask in template.items()}
    return deepcopy(value)


def _snapshot(specs):
    result=[]
    for key in ('items','workstations','operations','routings'):
        for spec in specs[key]:
            name=_named(spec);dt=spec['doctype']
            if frappe.db.exists(dt,name):
                doc=frappe.get_doc(dt,name);doc.check_permission('read')
                result.append(dict(doctype=dt,name=name,modified=str(doc.modified),docstatus=doc.docstatus,
                    fields={k:_fields(doc.get(k),v) for k,v in spec.items() if k not in ('doctype','name')}))
            else:result.append(dict(doctype=dt,name=name,missing=True))
    return result


def _prepare(project,pack_sha256,item_group,*,create=True):
    doc,context,folder,record=_pack(project,pack_sha256,write=True);_required_permissions(create=create)
    specs=_specs(doc,record['pack'],item_group)
    for key in ('items','workstations','operations','routings','boms'):
        for spec in specs[key]:
            meta=frappe.get_meta(spec['doctype'])
            if any(not meta.has_field(k) for k in spec if k not in ('doctype','name')):
                frappe.throw('Pinned native schema does not support the declared '+spec['doctype']+' fields')
    native=_snapshot(specs)
    if any(not row.get('missing') for row in native):frappe.throw('Fresh controlled Item/routing namespace required; existing records cannot be relabelled')
    value=dict(project=project,context_sha256=context['sha256'],registration_sha256=record['sha256'],
        item_group=item_group,specifications=specs,native_snapshot=native)
    return doc,context,folder,record,value


@frappe.whitelist(methods=['POST'])
def preview(project,pack_sha256,item_group):
    _role('Manufacturing Manager')
    _,_,_,_,value=_prepare(project,pack_sha256,item_group)
    return dict(**value,fingerprint=contract.digest(value),state='independent-review-required',**contract.FLAGS)


@frappe.whitelist(methods=['POST'])
def review(project,pack_sha256,item_group,fingerprint):
    _role('Projects Manager')
    doc,context,folder,record,value=_prepare(project,pack_sha256,item_group,create=False)
    if record['proposed_by']==frappe.session.user:frappe.throw('The proposer cannot independently review their own candidate conversion',frappe.PermissionError)
    if contract.digest(value)!=fingerprint:frappe.throw('Native prerequisites or controlled documents changed after preview')
    review_id=contract.digest([context['sha256'],pack_sha256,fingerprint,frappe.session.user]);target=folder/('review-'+review_id+'.json')
    if target.exists():
        old=contract.sealed(json.loads(target.read_text()));_review_record(old,doc)
        return dict(review_id=review_id,task=old['task'],created=False,**contract.FLAGS)
    body=dict(schema='osr-wheel-authenticated-business-review/1',project=project,pack_sha256=pack_sha256,
        context_sha256=context['sha256'],fingerprint=fingerprint,item_group=item_group,
        proposed_by=record['proposed_by'],reviewed_by=frappe.session.user,
        scope='Simulation business conversion only; physical manufacture and railway handback remain held',**contract.FLAGS)
    task=frappe.get_doc(dict(doctype='Task',project=project,subject='SIM independent wheel delivery review '+review_id[:12],
        description=json.dumps(body,sort_keys=True),status='Completed')).insert()
    result=contract.seal(dict(**body,task=task.name,task_description_sha256=sha256(task.description.encode()).hexdigest(),review_id=review_id))
    _write(target,result)
    return dict(review_id=review_id,task=task.name,created=True,**contract.FLAGS)


def _review_record(record,project):
    contract.sealed(record)
    task=frappe.get_doc('Task',record['task']);task.check_permission('read')
    if (task.project!=project.name or task.status!='Completed' or task.owner!=record['reviewed_by'] or
            task.modified_by!=record['reviewed_by'] or record['reviewed_by']==record['proposed_by'] or
            sha256(task.description.encode()).hexdigest()!=record['task_description_sha256']):
        frappe.throw('Authenticated independent native review record changed')
    return task


@frappe.whitelist(methods=['POST'])
def apply(project,pack_sha256,review_id):
    """Create native drafts after current independent review; never submit."""
    _role('Manufacturing Manager');contract.hash_id(review_id)
    doc,context,folder,registration=_pack(project,pack_sha256,write=True);_required_permissions(create=True)
    reviewed=contract.sealed(json.loads((folder/('review-'+review_id+'.json')).read_text()));_review_record(reviewed,doc)
    if reviewed['context_sha256']!=context['sha256'] or reviewed['pack_sha256']!=pack_sha256:frappe.throw('Review belongs to another project or pack')
    applied=folder/('applied-'+pack_sha256+'.json')
    if applied.exists():
        result=contract.sealed(json.loads(applied.read_text()))
        if result['review_id']!=review_id:frappe.throw('Applied conversion cannot be replaced by another review')
        _read_created(result,doc)
        return dict(applied=result,created=False,**contract.FLAGS)
    _,_,_,_,value=_prepare(project,pack_sha256,reviewed['item_group'])
    if contract.digest(value)!=reviewed['fingerprint']:frappe.throw('Native prerequisites changed after independent review')
    specs=value['specifications'];records=[];component_boms={}
    for key in ('items','workstations','operations','routings','boms'):
        for spec in specs[key]:
            payload=deepcopy(spec)
            if key=='boms' and payload['item'] in specs.get('assembly_bom_links',{}):
                for row in payload['items']:
                    if row['item_code'] not in component_boms:frappe.throw('Reviewed child BOM must be created before parent assembly')
                    # ERPNext refuses bom_no links to draft children. Keep
                    # exact links in controlled metadata without submitting or
                    # implicitly exploding any child BOM.
                    if row.get('do_not_explode')!=1:frappe.throw('Draft assembly child must not be exploded')
            native=frappe.get_doc(payload).insert()
            if native.docstatus!=0:frappe.throw('New business records must remain drafts')
            fields={k:_fields(native.get(k),v) for k,v in payload.items() if k not in ('doctype','name')}
            expected={k:deepcopy(v) for k,v in payload.items() if k not in ('doctype','name')}
            if fields!=expected:frappe.throw('Native defaults changed reviewed source quantity, price or route fields; review a supported conversion')
            records.append(dict(doctype=native.doctype,name=native.name,expected_fields=fields))
            if key=='boms':component_boms[native.item]=native.name
    components=[]
    for row in specs['components']:
        components.append(dict(row,bom=component_boms[row['finished_item']]))
    extra={}
    if 'assemblies' in specs:
        extra['assemblies']=[dict(row,bom=component_boms[row['finished_item']],
            child_bom_links=[dict(item_code=code,bom=component_boms[code]) for code in row['child_items']],
            native_bom_no_links_created=False) for row in specs['assemblies']]
        extra['assembly_roots']=specs['assembly_roots']
    result=contract.seal(dict(schema='osr-wheel-native-applied-drafts/1',project=project,company=doc.company,
        context_sha256=context['sha256'],pack_sha256=pack_sha256,review_id=review_id,
        authenticated_actor=frappe.session.user,records=records,components=components,
        automatic_order_release=False,created=True,**extra,**contract.FLAGS))
    _write(applied,result)
    return dict(applied=result,created=True,**contract.FLAGS)


def _read_created(result,project):
    for assembly in result.get('assemblies',[]):
        if assembly.get('native_bom_no_links_created') is not False:frappe.throw('Draft assembly cannot claim native child BOM links')
        for link in assembly['child_bom_links']:
            child=frappe.get_doc('BOM',link['bom']);child.check_permission('read')
            if child.item!=link['item_code'] or child.docstatus==2:frappe.throw('Draft assembly child BOM provenance changed')
    observed=[]
    for row in result['records']:
        doc=frappe.get_doc(row['doctype'],row['name']);doc.check_permission('read')
        if doc.docstatus==2 or (doc.get('company') and doc.company!=project.company):frappe.throw('Applied native document cancelled or moved company')
        for field,expected in row['expected_fields'].items():
            actual=_fields(doc.get(field),expected)
            if actual!=expected:frappe.throw('Applied native source/quantity/routing fields changed: '+row['name']+'/'+field)
        observed.append(dict(doctype=doc.doctype,name=doc.name,docstatus=doc.docstatus,modified=str(doc.modified)))
    return observed


@frappe.whitelist(methods=['GET'])
def status(project,pack_sha256):
    doc,context,folder,record=_pack(project,pack_sha256)
    path=folder/('applied-'+pack_sha256+'.json')
    result=contract.sealed(json.loads(path.read_text())) if path.exists() else None
    native=_read_created(result,doc) if result else []
    return dict(project=project,context_sha256=context['sha256'],pack_sha256=pack_sha256,
        coverage=record['pack']['coverage'],proposed_by=record['proposed_by'],
        state='reviewed-native-business-mapping' if result else 'independent-review-required',applied=result,native_records=native,**contract.FLAGS)


def _native(doctype,name,project,*,submitted=False):
    doc=frappe.get_doc(doctype,name);doc.check_permission('read')
    if doc.get('company') and doc.company!=project.company:frappe.throw('Native '+doctype+' belongs to another company')
    if doc.get('project') and doc.project!=project.name:frappe.throw('Native '+doctype+' belongs to another project')
    if submitted and doc.docstatus!=1:frappe.throw('Submitted native '+doctype+' required')
    return doc


def _serial_row(stock,item,project,direction):
    rows=[r for r in stock.items if r.item_code==item and r.project==project.name]
    if len(rows)!=1:frappe.throw('Exactly one project-bound finished row required')
    row=rows[0]
    if row.qty!=1 or not row.serial_and_batch_bundle:frappe.throw('One individually serialised native stock row required')
    bundle=_native('Serial and Batch Bundle',row.serial_and_batch_bundle,project)
    serials=[r.serial_no for r in bundle.entries if r.serial_no]
    if (bundle.item_code!=item or bundle.company!=project.company or bundle.is_cancelled or
            bundle.type_of_transaction!=direction or len(serials)!=1):
        frappe.throw('Native serial/batch bundle differs from source Item or custody direction')
    serial=_native('Serial No',serials[0],project)
    if serial.item_code!=item:frappe.throw('Native serial belongs to another source Item')
    return row,bundle,serial.name


def _asset_position(folder,asset):
    index=contract.sealed(json.loads((folder/('asset-'+contract.digest(asset)+'.json')).read_text()))
    value=contract.sealed(json.loads((folder/('position-'+index['position_id']+'.json')).read_text()))
    if value['asset']!=asset or index['context_sha256']!=value['context_sha256']:
        frappe.throw('Current Asset/position index differs')
    return value


def _index_asset(folder,record):
    path=folder/('asset-'+contract.digest(record['asset'])+'.json')
    index=contract.seal(dict(asset=record['asset'],position_id=record['position_id'],context_sha256=record['context_sha256']))
    if path.exists():
        if json.loads(path.read_text())!=index:frappe.throw('Asset cannot move to another source position implicitly')
    else:_write(path,index)


def _source_mapping(pack, context, applied, kind, source_id):
    if kind=='part':
        mapped=next((r for r in applied['components'] if r['part_id']==source_id),None)
        source=next((r for r in pack['components'] if r['source_part']['id']==source_id),None)
        if mapped is None or source is None:frappe.throw('Exact reviewed part mapping required')
        return mapped,source['source_part']['component_definition_id']
    if kind!='assembly':frappe.throw('Typed part or assembly source required')
    node=context.get('source_assemblies',{}).get(source_id)
    mapped=next((r for r in applied.get('assemblies',[]) if r['assembly_id']==source_id),None)
    docs=pack.get('assembly_documents',{}).get(source_id)
    if (node is None or mapped is None or mapped['definition_id']!=node['definition_id'] or not docs
            or context.get('assembly_document_hashes',{}).get(source_id)!=contract.engineering_digest(docs)
            or mapped.get('documents')!=docs):
        frappe.throw('Own authoritative assembly drawing, inspection, routing and exact definition required')
    return mapped,node['definition_id']


def _current_mapping(current, pack, context, applied):
    kind=current.get('source_kind','part')
    mapped,definition=_source_mapping(pack,context,applied,kind,current.get('source_id',current.get('part_id')))
    if kind=='assembly' and (current.get('assembly_id')!=current['source_id'] or current.get('assembly_definition_id')!=definition):
        frappe.throw('Installed typed assembly definition differs')
    return mapped


def _latest_qa(made, item, row, project):
    latest=frappe.get_all('Quality Inspection',filters=dict(reference_type='Stock Entry',reference_name=made.name,
        item_code=item,child_row_reference=row.name),pluck='name',order_by='creation desc, name desc',limit_page_length=1)
    if len(latest)!=1:frappe.throw('Latest native inspection required')
    return _native('Quality Inspection',latest[0],project)


def _bundle_voucher(bundle, stock, row):
    if (bundle.get('voucher_type')!='Stock Entry' or bundle.get('voucher_no')!=stock.name
            or bundle.get('voucher_detail_no')!=row.name):
        frappe.throw('Assembly serial bundle belongs to another native voucher row')


def _assembly_custody(project, pack, context, applied, assembly_id, made, provenance):
    """Read exact consumed child serials recursively; never infer child custody."""
    if len(contract.encoded(provenance))>contract.MAX_PACK_BYTES:frappe.throw('Assembly provenance byte budget exceeded')
    work=[0];uses=[];observations=[]
    def visit(name, parent_stock, rows, depth):
        if depth>contract.MAX_ASSEMBLY_DEPTH:frappe.throw('Assembly custody depth exceeded')
        node=context['source_assemblies'][name]
        if any(r.project!=project.name for r in parent_stock.items):frappe.throw('Assembly stock contains another project row')
        if not isinstance(rows,list) or len(rows)!=len(node['children']):frappe.throw('Exact typed child provenance required')
        expected={(edge['kind'],edge['id']):edge['quantity'] for edge in node['children']}
        seen=set();items=set()
        for edge in rows:
            if not isinstance(edge,dict) or set(edge)!={'kind','id','units'}:frappe.throw('Typed child provenance fields required')
            key=(edge['kind'],edge['id'])
            if key not in expected or key in seen:frappe.throw('Typed source child identity differs')
            seen.add(key);units=edge['units']
            if not isinstance(units,list) or len(units)!=expected[key]:frappe.throw('Exact child quantities required')
            work[0]+=len(units)
            if work[0]>4096:frappe.throw('Assembly serial custody budget exceeded')
            mapped,_=_source_mapping(pack,context,applied,*key);item=mapped['finished_item'];items.add(item)
            if key[0]=='part':
                source=next(c['source_part'] for c in pack['components'] if c['source_part']['id']==key[1])
                if source.get('make_buy') not in ('local-fabricate','make'):
                    frappe.throw('Assembly custody currently supports manufactured individually serialized children only; purchased or lot custody remains held')
            consumed=[r for r in parent_stock.items if r.item_code==item and r.project==project.name]
            if len(consumed)!=1 or consumed[0].qty!=len(units) or not consumed[0].serial_and_batch_bundle:
                frappe.throw('Parent manufacture must consume exact counted child row')
            bundle=_native('Serial and Batch Bundle',consumed[0].serial_and_batch_bundle,project)
            _bundle_voucher(bundle,parent_stock,consumed[0])
            serials=[r.serial_no for r in bundle.entries if r.serial_no]
            if (bundle.item_code!=item or bundle.company!=project.company or bundle.is_cancelled or
                    bundle.type_of_transaction!='Outward' or len(serials)!=len(units) or len(set(serials))!=len(serials)):
                frappe.throw('Child consumption serial bundle differs')
            supplied=[]
            for unit in units:
                if not isinstance(unit,dict) or set(unit)!={'serial','work_order','manufacture_stock','children'}:
                    frappe.throw('Exact child manufacturing provenance required')
                wo=_native('Work Order',unit['work_order'],project,submitted=True)
                child=_native('Stock Entry',unit['manufacture_stock'],project,submitted=True)
                bom=_native('BOM',mapped['bom'],project,submitted=True)
                if (bom.item!=item or wo.production_item!=item or wo.bom_no!=bom.name or wo.produced_qty<1
                        or child.work_order!=wo.name or child.stock_entry_type!='Manufacture'):
                    frappe.throw('Child manufacture differs from exact reviewed submitted BOM')
                row,child_bundle,serial=_serial_row(child,item,project,'Inward')
                _bundle_voucher(child_bundle,child,row)
                if serial!=unit['serial']:frappe.throw('Child manufactured serial differs')
                qa=_latest_qa(child,item,row,project)
                if qa.docstatus!=1 or qa.status!='Accepted':frappe.throw('Latest child native QA must be accepted')
                supplied.append(serial);uses.append(dict(serial=serial,item=item,parent_stock=parent_stock.name))
                observations.append(dict(kind=key[0],source_id=key[1],serial=serial,item=item,
                    parent_stock=parent_stock.name,work_order=wo.name,bom=bom.name,manufacture_stock=child.name,
                    latest_qa=dict(name=qa.name,status=qa.status,docstatus=qa.docstatus,modified=str(qa.modified),inspector=qa.inspected_by),
                    native_modifications=dict(work_order=str(wo.modified),bom=str(bom.modified),manufacture=str(child.modified),
                        consumption_bundle=str(bundle.modified),manufacture_bundle=str(child_bundle.modified))))
                if key[0]=='assembly':visit(key[1],child,unit['children'],depth+1)
                elif unit['children']:frappe.throw('Part cannot claim assembly child provenance')
            if set(supplied)!=set(serials) or len(set(supplied))!=len(supplied):frappe.throw('Consumed and manufactured child serials differ')
        outgoing={r.item_code for r in parent_stock.items if r.project==project.name and not getattr(r,'is_finished_item',False)}
        if outgoing!=items:frappe.throw('Parent manufacture has unaccounted source children')
    visit(assembly_id,made,provenance,1)
    if len({u['serial'] for u in uses})!=len(uses):frappe.throw('Child serial has duplicate hierarchy ownership')
    return dict(uses=uses,observations=observations)


def _assembly_readback(current, pack, context, applied, made, project):
    if current.get('source_kind')=='assembly':
        mapped=_current_mapping(current,pack,context,applied)
        wo=_native('Work Order',current['work_order'],project,submitted=True)
        bom=_native('BOM',mapped['bom'],project,submitted=True)
        if (wo.production_item!=mapped['finished_item'] or wo.bom_no!=bom.name or wo.produced_qty<1
                or made.work_order!=wo.name or made.stock_entry_type!='Manufacture'):
            frappe.throw('Assembly manufacturing custody changed')
        return _assembly_custody(project,pack,context,applied,current['source_id'],made,current['child_provenance'])
    return []


@frappe.whitelist(methods=['POST'])
def register_assembly_installation(project,pack_sha256,assembly_id,asset,source_pattern_id,ordinal,train_index,
                                  work_order,manufacture_stock,installation_stock,child_provenance,repair=None,removal_stock=None):
    """Research software custody for made, individually serialized children only.

    Purchased/lot-managed children remain outside this admitted domain.
    """
    return register_installation(project,pack_sha256,assembly_id,asset,source_pattern_id,ordinal,train_index,
        work_order,manufacture_stock,installation_stock,repair,removal_stock,
        source_kind='assembly',child_provenance=_json(child_provenance))


@frappe.whitelist(methods=['POST'])
def register_installation(project,pack_sha256,part_id,asset,source_pattern_id,ordinal,train_index,
                          work_order,manufacture_stock,installation_stock,repair=None,removal_stock=None,
                          source_kind='part',child_provenance=None):
    """Record read-back stock custody for a proposed research occurrence.

    This does not mark a physical installation accepted. A replacement must
    have an actual same-serial native return/removal and condition repair.
    """
    _role('Asset Manager');doc,context,folder,registration=_pack(project,pack_sha256,write=True)
    applied=contract.sealed(json.loads((folder/('applied-'+pack_sha256+'.json')).read_text()));_read_created(applied,doc)
    component,definition_id=_source_mapping(registration['pack'],context,applied,source_kind,part_id)
    pattern=context['source_patterns' if source_kind=='part' else 'assembly_patterns'].get(source_pattern_id)
    if any(type(v) not in (int,str) or re.fullmatch('[0-9]{1,6}',str(v)) is None for v in (ordinal,train_index)):
        frappe.throw('Bounded nonnegative integer occurrence indices required')
    ordinal=int(ordinal);train_index=int(train_index)
    if (component is None or pattern is None or pattern.get('part_id' if source_kind=='part' else 'assembly_id')!=part_id or (source_kind=='assembly' and pattern['definition_id']!=definition_id) or ordinal<0 or ordinal>=pattern['count_per_train'] or
            train_index<0 or train_index>=context['project_trainsets']):frappe.throw('Exact counted source occurrence and train index required')
    position=contract.digest(dict(context_sha256=context['sha256'],source_pattern_id=source_pattern_id,ordinal=ordinal,train_index=train_index))
    if source_kind=='assembly':position=contract.digest(dict(context_sha256=context['sha256'],source_kind=source_kind,source_id=part_id,definition_id=definition_id,source_pattern_id=source_pattern_id,ordinal=ordinal,train_index=train_index))
    asset_doc=_native('Asset',asset,doc,submitted=True)
    if asset_doc.custom_osr_asset_id!='SIM-WD-'+position[:24]:frappe.throw('Native Asset differs from the counted source occurrence')
    wo=_native('Work Order',work_order,doc,submitted=True)
    if wo.production_item!=component['finished_item'] or wo.bom_no!=component['bom'] or wo.produced_qty<1:frappe.throw('Manufacture must use the exact reviewed source BOM')
    made=_native('Stock Entry',manufacture_stock,doc,submitted=True)
    installed=_native('Stock Entry',installation_stock,doc,submitted=True)
    if made.work_order!=wo.name or made.stock_entry_type!='Manufacture' or installed.stock_entry_type!='Material Issue':
        frappe.throw('Native manufacturing and outward installation custody required')
    finished,made_bundle,serial=_serial_row(made,component['finished_item'],doc,'Inward')
    installed_row,installed_bundle,installed_serial=_serial_row(installed,component['finished_item'],doc,'Outward')
    if serial!=installed_serial:frappe.throw('Installed serial differs from manufactured serial')
    if source_kind=='assembly':_native('BOM',component['bom'],doc,submitted=True)
    if source_kind=='assembly':
        _bundle_voucher(made_bundle,made,finished);_bundle_voucher(installed_bundle,installed,installed_row)
    custody=_assembly_custody(doc,registration['pack'],context,applied,part_id,made,child_provenance) if source_kind=='assembly' else {'uses':[],'observations':[]}
    child_uses=custody['uses']
    serial_index=folder/('serial-position-'+contract.digest(serial)+'.json')
    if (folder/('consumed-serial-'+contract.digest(serial)+'.json')).exists():frappe.throw('Consumed child serial cannot also be installed independently')
    serial_binding=contract.seal(dict(serial=serial,position_id=position,context_sha256=context['sha256']))
    if serial_index.exists() and contract.sealed(json.loads(serial_index.read_text()))!=serial_binding:frappe.throw('Serial already belongs to another counted position')
    for use in child_uses:
        if (folder/('serial-position-'+contract.digest(use['serial'])+'.json')).exists():frappe.throw('Installed serial cannot also be consumed as an assembly child')
        used=folder/('consumed-serial-'+contract.digest(use['serial'])+'.json')
        if used.exists() and contract.sealed(json.loads(used.read_text()))!=contract.seal(use):frappe.throw('Child serial is already consumed by another assembly')
    pointer=folder/('position-'+position+'.json');prior=contract.sealed(json.loads(pointer.read_text())) if pointer.exists() else None
    if prior is not None and prior['installed_serial']==serial:
        expected=dict(source_pattern_id=source_pattern_id,ordinal=ordinal,train_index=train_index,part_id=part_id,
            asset=asset,work_order=wo.name,manufacture_stock=made.name,installation_record=installed.name,repair=repair,removal_stock=removal_stock)
        if source_kind=='assembly':
            expected.pop('part_id');expected.update(source_kind='assembly',source_id=part_id,assembly_definition_id=definition_id,child_provenance=child_provenance)
        if any(prior.get(k)!=v for k,v in expected.items()):frappe.throw('A serial installation cannot be rebound to different native custody')
        _index_asset(folder,prior)
        return dict(installation=prior,created=False,**contract.FLAGS)
    if prior is not None and prior['installed_serial']!=serial:
        if not repair or not removal_stock:frappe.throw('Replacement requires native repair and exact old-serial removal')
        repair_doc=_native('Asset Repair',repair,doc,submitted=True)
        removal=_native('Stock Entry',removal_stock,doc,submitted=True)
        if (repair_doc.asset!=asset or repair_doc.custom_osr_environment!='simulation' or repair_doc.repair_status!='Completed' or
                not repair_doc.custom_osr_handback_required or removal.stock_entry_type!='Material Receipt'):
            frappe.throw('Completed condition repair and inward removed-serial custody required')
        removed_row,removed_bundle,removed=_serial_row(removal,component['finished_item'],doc,'Inward')
        if source_kind=='assembly':_bundle_voucher(removed_bundle,removal,removed_row)
        if removed!=prior['installed_serial']:frappe.throw('Removal does not identify the exact previously installed serial')
    record=contract.seal(dict(schema='osr-wheel-native-installation/1',project=project,company=doc.company,
        context_sha256=context['sha256'],pack_sha256=pack_sha256,identities=context['identities'],
        position_id=position,source_pattern_id=source_pattern_id,ordinal=ordinal,train_index=train_index,
        part_id=part_id,asset=asset,work_order=wo.name,manufacture_stock=made.name,finished_row=finished.name,
        installation_record=installed.name,installed_serial=serial,manufactured_serial=serial,
        manufacture_bundle=made_bundle.name,installation_bundle=installed_bundle.name,repair=repair,removal_stock=removal_stock,
        previous_installation_sha256=prior['sha256'] if prior and prior['installed_serial']!=serial else None,
        authenticated_actor=frappe.session.user,installation_accepted=False,**contract.FLAGS))
    if source_kind=='assembly':
        record.pop('sha256');record.pop('part_id');record.update(source_kind=source_kind,source_id=part_id,assembly_id=part_id,assembly_definition_id=definition_id,child_provenance=child_provenance)
        record=contract.seal(record)
    event=folder/('installation-'+record['sha256']+'.json')
    if event.exists():return dict(installation=record,created=False,**contract.FLAGS)
    if not serial_index.exists():_write(serial_index,serial_binding)
    for use in child_uses:
        used=folder/('consumed-serial-'+contract.digest(use['serial'])+'.json')
        if not used.exists():_write(used,contract.seal(use))
    _write(event,record)
    # The pointer is merely a current software index; immutable events retain
    # every source-bound predecessor and never confer physical acceptance.
    temporary=folder/('position-'+position+'.next');_write(temporary,record);temporary.replace(pointer)
    _index_asset(folder,record)
    return dict(installation=record,created=True,**contract.FLAGS)


def _handback_observation(project,context,folder,registration,asset):
    current=_asset_position(folder,asset)
    if current['context_sha256']!=context['sha256'] or current['pack_sha256']!=registration['pack']['sha256']:
        frappe.throw('Installed source revision differs')
    made=_native('Stock Entry',current['manufacture_stock'],project,submitted=True)
    installed_stock=_native('Stock Entry',current['installation_record'],project,submitted=True)
    applied=contract.sealed(json.loads((folder/('applied-'+current['pack_sha256']+'.json')).read_text()));_read_created(applied,project)
    component=_current_mapping(current,registration['pack'],context,applied)
    child_readback=_assembly_readback(current,registration['pack'],context,applied,made,project)
    row,manufacture_bundle,serial=_serial_row(made,component['finished_item'],project,'Inward')
    installed_row,installed_bundle,installed_serial=_serial_row(installed_stock,component['finished_item'],project,'Outward')
    if current.get('source_kind')=='assembly':
        _bundle_voucher(manufacture_bundle,made,row);_bundle_voucher(installed_bundle,installed_stock,installed_row)
    if serial!=current['installed_serial'] or installed_serial!=serial:frappe.throw('Native serial custody changed')
    if not current['repair']:frappe.throw('Repair lifecycle evidence required before repair handback')
    repair=_native('Asset Repair',current['repair'],project,submitted=True)
    issue=_native('Issue',repair.custom_osr_issue,project)
    if (repair.asset!=asset or issue.project!=project.name or issue.custom_osr_erp_asset!=asset or
            issue.custom_osr_environment!='simulation' or repair.custom_osr_environment!='simulation'):
        frappe.throw('Condition event, repair and installed source position differ')
    # Include pending and cancelled later inspections: neither can revive an
    # earlier pass merely because it was the latest submitted accepted row.
    qa=_latest_qa(made,component['finished_item'],row,project)
    observed=dict(project=project.name,company=project.company,identities=context['identities'],
        reviewer=frappe.session.user,inspector=qa.inspected_by,proposer=registration['proposed_by'],
        latest_qa=qa.name,latest_qa_docstatus=qa.docstatus,latest_qa_status=qa.status,
        repair=repair.name,repair_docstatus=repair.docstatus,repair_status=repair.repair_status,
        physical_handback_required=bool(repair.custom_osr_handback_required),
        installation_record=installed_stock.name,installation_docstatus=installed_stock.docstatus,
        installed_serial=installed_serial,manufactured_serial=serial,
        review_task='not-yet-created',installation_sha256=current['sha256'],
        native_modifications=dict(inspection=str(qa.modified),repair=str(repair.modified),
            manufacture=str(made.modified),installation=str(installed_stock.modified)))
    if current.get('source_kind')=='assembly':
        observed['child_observations']=child_readback['observations']
        observed['native_modifications']['child_observations']=contract.digest(child_readback['observations'])
    return observed,current


@frappe.whitelist(methods=['POST'])
def review_handback(project,pack_sha256,asset):
    """Independent authenticated business review of actual latest native state."""
    _role('Projects Manager');doc,context,folder,registration=_pack(project,pack_sha256,write=True)
    observed,current=_handback_observation(doc,context,folder,registration,asset)
    contract.business_handback(context,observed,actor=frappe.session.user)
    key=contract.digest(observed);path=folder/('handback-'+key+'.json')
    if path.exists():
        record=contract.sealed(json.loads(path.read_text()))
        _handback_task(record,doc)
        return dict(handback=record,created=False,**contract.FLAGS)
    task=frappe.get_doc(dict(doctype='Task',project=project,status='Completed',subject='SIM independent business handback '+key[:12],
        description=json.dumps(dict(native_readback=observed,physical_handback='still-required',**contract.FLAGS),sort_keys=True))).insert()
    observed['review_task']=task.name
    guarded=contract.business_handback(context,observed,actor=frappe.session.user)
    result=contract.seal(dict({k:v for k,v in guarded.items() if k!='sha256'},
        native_review_task_sha256=sha256(task.description.encode()).hexdigest()))
    _write(path,result)
    return dict(handback=result,created=True,**contract.FLAGS)


def _handback_task(record,project):
    task=_native('Task',record['native_readback']['review_task'],project)
    if (task.status!='Completed' or task.owner!=record['authenticated_actor'] or task.modified_by!=record['authenticated_actor'] or
            task.project!=project.name or sha256(task.description.encode()).hexdigest()!=record['native_review_task_sha256']):
        frappe.throw('Independent business handback Task changed')
    return task


@frappe.whitelist(methods=['GET'])
def lifecycle_status(project,pack_sha256,asset):
    doc,context,folder,registration=_pack(project,pack_sha256)
    observed,current=_handback_observation(doc,context,folder,registration,asset)
    matches=[]
    for path in folder.glob('handback-*.json'):
        record=contract.sealed(json.loads(path.read_text()));prior=record['native_readback']
        if (prior['installation_sha256']==current['sha256'] and prior['latest_qa']==observed['latest_qa'] and
                prior['native_modifications']==observed['native_modifications']):
            _handback_task(record,doc);matches.append(record)
    ready=observed['latest_qa_docstatus']==1 and observed['latest_qa_status']=='Accepted' and bool(matches)
    return dict(project=project,pack_sha256=pack_sha256,installation=current,
        state='simulation-business-reviewed' if ready else 'business-handback-held',
        latest_native_inspection=dict(name=observed['latest_qa'],status=observed['latest_qa_status'],docstatus=observed['latest_qa_docstatus']),
        physical_handback_required=True,**contract.FLAGS)


def guard_condition_event(event):
    """Called by existing ingress only for an explicitly bound wheel project."""
    project=event['project']
    folder=Path(frappe.get_site_path('private','files','osr-wheel-delivery',contract.digest(project)))
    if not (folder/'context.json').is_file():return False  # Retained ingress contract unchanged.
    doc,context,folder=_context(project)
    if (event.get('engineering_revision')!=context['identities']['engineering_revision'] or
            event.get('environment')!=context['environment'] or event.get('city')!=context['city'] or event.get('company')!=context['company']):
        frappe.throw('Condition event differs from authoritative wheel project revision')
    asset=_native('Asset',event.get('erp_asset_id'),doc,submitted=True)
    current=_asset_position(folder,asset.name)
    if (asset.custom_osr_asset_id!=event.get('asset_id') or current['context_sha256']!=context['sha256'] or
            event.get('physical_serial_id')!=current['installed_serial']):
        frappe.throw('Condition event differs from current counted position/installed serial')
    # Recheck the exact component's registered drawing/inspection/routing and
    # native mapping before permitting a provisional defect/Issue side effect.
    _,_,_,registration=_pack(project,current['pack_sha256'])
    applied=contract.sealed(json.loads((folder/('applied-'+current['pack_sha256']+'.json')).read_text()));_read_created(applied,doc)
    mapped=_current_mapping(current,registration['pack'],context,applied)
    wo=_native('Work Order',current['work_order'],doc,submitted=True)
    made=_native('Stock Entry',current['manufacture_stock'],doc,submitted=True)
    installed=_native('Stock Entry',current['installation_record'],doc,submitted=True)
    _assembly_readback(current,registration['pack'],context,applied,made,doc)
    if (wo.production_item!=mapped['finished_item'] or wo.bom_no!=mapped['bom'] or wo.produced_qty<1 or
            made.work_order!=wo.name or made.stock_entry_type!='Manufacture' or installed.stock_entry_type!='Material Issue'):
        frappe.throw('Current native manufacturing or installation custody changed')
    made_row,made_bundle,made_serial=_serial_row(made,mapped['finished_item'],doc,'Inward')
    installed_row,installed_bundle,installed_serial=_serial_row(installed,mapped['finished_item'],doc,'Outward')
    if current.get('source_kind')=='assembly':
        _bundle_voucher(made_bundle,made,made_row);_bundle_voucher(installed_bundle,installed,installed_row)
    if made_serial!=current['installed_serial'] or installed_serial!=made_serial:
        frappe.throw('Current installed native serial custody differs')
    return True
