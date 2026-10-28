"""Dimension-derived blanks, machining waste and conditional production slots.

Rates are explicit Class C planning hypotheses, distinct from shop measurements.
Purchased equipment has no invented raw-material yield or manufacturing cycle.
"""
from math import pi,fsum,ceil,isfinite
from collections import Counter
from copy import deepcopy
from . import identity,FLAGS


def assumptions():
    a=dict(source_class='C',source_date='2026-10-28',location='unsurveyed-reference-cell',currency='USD',
        source='explicit-research-process-hypotheses',blank_allowance_m=.005,kerf_m=.003,
        cutting_m_per_h=[5.,30.],mould_contact_m2_per_h=[.3,2.],machine_removal_m3_per_h=[.0005,.005],
        labour_usd_per_h=[8.,40.],material_usd_per_kg=[2.,30.],receiving_h_per_unit=[.02,.10],
        assembly_h_per_unit=[.01,.15],inspection_h_per_unit=[.005,.05],shift_hours=8.,workstations=4,
        composite_cure_h=[12.,48.],tooling_setup_h=[2.,20.],mould_service_life_cycles=[50,500])
    a['source_id']=identity(a);return a


def blank(geometry,*,allowance_m=.005,kerf_m=.003):
    """Owned net primitive -> dimensional blank, never envelope fill volume."""
    kind=geometry['kind'];d=geometry['dimensions_m'];net=geometry.get('net_volume_m3')
    if kind=='envelope':return dict(blank_dimensions_m=None,blank_volume_m3=None,net_volume_m3=None,yield_fraction=None,
        cut_length_m=None,removed_volume_m3=None,reason='Purchased envelope is not net stock or raw material')
    if net is None or net<=0:raise ValueError('Positive net primitive volume required')
    if kind=='box':
        dims=[x+2*allowance_m for x in d];volume=dims[0]*dims[1]*dims[2];cut=2*(dims[0]+dims[1]);area=2*(d[0]*d[1]+d[0]*d[2]+d[1]*d[2])
    elif kind in ('tube','cylinder'):
        length=d['length']+2*allowance_m+kerf_m;outer=d.get('outer_radius',d.get('radius'))+allowance_m
        inner=max(0.,d.get('inner_radius',0.)-allowance_m)
        volume=pi*(outer**2-inner**2)*length;dims=dict(length=length,outer_radius=outer,inner_radius=inner)
        cut=2*pi*outer;area=2*pi*outer*d['length']
    else:raise ValueError('No owned blank evaluator for '+kind)
    if volume<net-1e-12:raise ValueError('Gross dimensional blank cannot be smaller than net part')
    return dict(blank_dimensions_m=dims,blank_volume_m3=volume,net_volume_m3=net,yield_fraction=net/volume,
        cut_length_m=cut,removed_volume_m3=volume-net,exposed_mould_area_m2=area,
        blank_form_is_manufacturing_hypothesis=True,approved_work_instruction=None)



def _drafts(vehicle,alternative,candidate_id,parts,counts,routes):
    """Candidate-bound neutral Frappe drafts; import/custom-field review required."""
    if len(parts)!=len(routes) or {x['part_definition_id'] for x in routes}!=set(parts):
        raise ValueError('Every physical definition needs exactly one routing')
    if len({x['part_definition_id'] for x in routes})!=len(routes):raise ValueError('Duplicate manufacturing routing')
    records={};onboard_counts=Counter();wayside_counts=Counter();source_to_code={};items=[];operations=[];routings=[];rfqs=[];workstations={}
    def seal(v):v['draft_id']=identity(v);return v
    def item(source_key,physical_id,revision_id,label,quantity,scope,purchased=False):
        if source_key in records or type(quantity) is not int or quantity<=0:raise ValueError('Unique positive individual item counts required')
        code='OSR-'+candidate_id[:12]+'-'+identity(source_key)[:12]+'-'+revision_id[:12]
        if code in source_to_code.values():raise ValueError('Draft item-code collision')
        source_to_code[source_key]=code
        r=seal(dict(doctype='Item',item_code=code,item_name=label,stock_uom='Nos',disabled=1,docstatus=0,
            is_stock_item=1,is_purchase_item=1 if purchased else 0,is_sales_item=0,
            candidate_id=candidate_id,part_definition_id=physical_id,part_revision_id=revision_id,
            source_scope=scope,source_key=source_key,source_registry_id=vehicle['registry']['registry_id'],
            source_alternative_candidate_id=alternative['candidate_id'] if scope.startswith('launch') else None,
            default_supplier=None,valuation_rate=None,standard_rate=None,
            import_validation_required=True,submission_allowed=False))
        items.append(r);records[source_key]=r
        return code
    for key,p in sorted(parts.items()):
        item('vehicle/'+key,key,p['revision_id'],p['part_id'],counts[key],'vehicle',p['geometry']['kind']=='envelope')
        onboard_counts['vehicle/'+key]=counts[key]
    for i,p in enumerate(alternative['inventory']):
        physical=p.get('physical_definition_id')
        if not isinstance(physical,str) or len(physical)!=64 or any(c not in '0123456789abcdef' for c in physical) or type(p.get('count')) is not int or p['count']<=0:
            raise ValueError('Owned physical plant definitions and positive integer counts required')
        key='launch/'+p['part_id']
        revision=identity(p)
        item(key,physical,revision,p['part_id'],p['count'],'launch-onboard' if p['installation']=='onboard' else 'launch-wayside',p.get('calculated_mass_kg') is None)
        (onboard_counts if p['installation']=='onboard' else wayside_counts)[key]=p['count']
    route_by={r['part_definition_id']:r for r in routes}
    operation_defs={}
    for source_key,record in records.items():
        parent=source_key.split('/',1)[1];route=route_by.get(parent) if source_key.startswith('vehicle/') else None
        route_steps=route['operations'] if route else [dict(sequence=1,name='qualify-launch-component-and-source',workstation=None,work_instruction_id=None),dict(sequence=2,name='install-inspect-test-launch-component',workstation=None,work_instruction_id=None)]
        steps=[]
        for step in route_steps:
            op_key=identity(dict(candidate_id=candidate_id,name=step['name']))
            if op_key not in operation_defs:
                op=seal(dict(doctype='Operation',name='OSR-OP-'+op_key[:20],operation=step['name'],candidate_id=candidate_id,
                    operation_definition_id=op_key,disabled=1,docstatus=0,default_workstation=None,approved_work_instruction=None,
                    time_in_mins=None,hour_rate=None,submission_allowed=False,import_validation_required=True))
                operation_defs[op_key]=op;operations.append(op)
            op=operation_defs[op_key]
            workstation=step.get('workstation')
            if workstation is not None and workstation not in workstations:
                workstations[workstation]=seal(dict(doctype='Workstation',name='OSR-WS-'+identity([candidate_id,workstation])[:20],
                    workstation_name=workstation,candidate_id=candidate_id,disabled=1,docstatus=0,
                    production_capacity=None,qualified_process_capacity=None,hour_rate=None,
                    submission_allowed=False,import_validation_required=True))
            steps.append(dict(doctype='Routing Operation',sequence_id=step['sequence'],operation=op['name'],
                workstation=None if workstation is None else workstations[workstation]['name'],time_in_mins=None,
                source_part_definition_id=record['part_definition_id'],source_part_revision_id=record['part_revision_id'],approved_work_instruction=None))
        routing=seal(dict(doctype='Routing',name='OSR-RT-'+identity([candidate_id,source_key,record['part_revision_id']])[:24],
            candidate_id=candidate_id,item_code=record['item_code'],part_definition_id=record['part_definition_id'],part_revision_id=record['part_revision_id'],
            operations=steps,disabled=1,docstatus=0,approved=False,submission_allowed=False,import_validation_required=True))
        routings.append(routing)
        quantity=(onboard_counts|wayside_counts)[source_key]
        rfqs.append(seal(dict(doctype='Request for Quotation',name='OSR-RFQ-'+identity([candidate_id,source_key])[:24],candidate_id=candidate_id,
            source_part_definition_id=record['part_definition_id'],source_part_revision_id=record['part_revision_id'],
            docstatus=0,status='Draft',workflow_state='Engineering review required',disabled=1,company=None,
            transaction_date=None,suppliers=[],message_for_supplier=None,send_supplier_emails=False,
            items=[dict(item_code=record['item_code'],qty=quantity,uom='Nos',rate=None,amount=None)],
            submission_allowed=False,import_validation_required=True)))
    # Decide from actual occurrence ownership, not divisibility of totals alone.
    car_count=vehicle.get('requirements',{}).get('cars');car_counts=[]
    if car_count==6:
        for car in range(6):
            car_counts.append(Counter('vehicle/'+o['part_definition_id'] for o in vehicle['registry']['occurrences'] if o['occurrence_id'].startswith('car-'+str(car+1)+'/')))
    repeated=(car_count==6 and len(car_counts)==6 and all(x==car_counts[0] for x in car_counts)
        and sum(sum(x.values()) for x in car_counts)==len(vehicle['registry']['occurrences'])
        and all(n%6==0 for k,n in onboard_counts.items() if k.startswith('launch/')))
    boms=[];assembly_items=[]
    def assembly(name,entries,scope):
        code='OSR-'+candidate_id[:16]+'-'+name
        assembly_items.append(seal(dict(doctype='Item',item_code=code,item_name=name,stock_uom='Nos',candidate_id=candidate_id,
            disabled=1,docstatus=0,is_stock_item=1,is_sales_item=0,submission_allowed=False,import_validation_required=True)))
        bom=seal(dict(doctype='BOM',name='OSR-BOM-'+candidate_id[:16]+'-'+name,item=code,quantity=1,uom='Nos',candidate_id=candidate_id,
            source_registry_id=vehicle['registry']['registry_id'],source_alternative_candidate_id=alternative['candidate_id'],
            source_assembly_scope=scope,docstatus=0,is_active=0,is_default=0,with_operations=0,items=entries,
            approved=False,submission_allowed=False,import_validation_required=True))
        boms.append(bom);return code,bom['name']
    if repeated:
        per={k:n//6 for k,n in onboard_counts.items()}
        car_code,car_bom=assembly('CAR',[dict(doctype='BOM Item',item_code=records[k]['item_code'],qty=n,uom='Nos',part_definition_id=records[k]['part_definition_id'],part_revision_id=records[k]['part_revision_id']) for k,n in sorted(per.items())], 'one-proposed-car-with-counted-launch-interface')
        assembly('TRAIN',[dict(doctype='BOM Item',item_code=car_code,bom_no=car_bom,qty=6,uom='Nos')], 'six-repeated-cars')
        exploded={k:n*6 for k,n in per.items()}
    else:
        assembly('VEHICLE-PACKAGE',[dict(doctype='BOM Item',item_code=records[k]['item_code'],qty=n,uom='Nos',part_definition_id=records[k]['part_definition_id'],part_revision_id=records[k]['part_revision_id']) for k,n in sorted(onboard_counts.items())], 'actual-nonrepeated-owned-occurrences')
        exploded=dict(onboard_counts)
    if wayside_counts:assembly('WAYSIDE-PLANT',[dict(doctype='BOM Item',item_code=records[k]['item_code'],qty=n,uom='Nos',part_definition_id=records[k]['part_definition_id'],part_revision_id=records[k]['part_revision_id']) for k,n in sorted(wayside_counts.items())], 'counted-launch-plant-only-civil-separate')
    if exploded!=dict(onboard_counts):raise ValueError('Multi-level BOM explosion differs from actual physical occurrences')
    value=dict(submission_allowed=False,docstatus=0,items_disabled=True,active_BOMs=False,
        schema='osr-disabled-production-drafts/1',candidate_id=candidate_id,
        item_drafts=items,assembly_item_drafts=assembly_items,BOM_drafts=boms,operation_drafts=operations,routing_drafts=routings,
        workstation_drafts=list(workstations.values()),rfq_drafts=rfqs,production_orders=[],active_assets=[],external_transactions_performed=False,
        quantity_reconciliation=dict(vehicle_occurrences=sum(counts.values()),added_onboard_launch_occurrences=sum(n for k,n in onboard_counts.items() if k.startswith('launch/')),
            wayside_launch_occurrences=sum(wayside_counts.values()),exploded_onboard_occurrences=sum(exploded.values()),all_counts_reconciled=True,
            identical_six_car_BOM=repeated,part_definition_count=len(records)),
        export_scope='Actual vehicle registry and counted launch-interface/wayside definitions; civil construction slots retained separately. Unknown vendor internals are not invented.',
        field_mapping_and_permissions_review='Required before any external import; these neutral drafts are not commissioned ERPNext records')
    value['export_id']=identity(value);return value


def compile(vehicle,civil,alternative,candidate_id,*,process=None):
    from engineering.component_registry import validate_registry
    if not isinstance(candidate_id,str) or len(candidate_id)!=64 or any(c not in '0123456789abcdef' for c in candidate_id):raise ValueError('Exact physical cell identity required')
    validate_registry(vehicle['registry'])
    if vehicle.get('evaluation_id')!=identity({k:v for k,v in vehicle.items() if k!='evaluation_id'}) or vehicle['candidate_id']!=vehicle['registry']['candidate_id']:
        raise ValueError('Exact equipped vehicle registry/evaluation required')
    if alternative.get('evaluation_id')!=identity({k:v for k,v in alternative.items() if k!='evaluation_id'}) or alternative['body_candidate_id']!=vehicle['candidate_id']:
        raise ValueError('Manufacturing launch alternative must bind this vehicle')
    if civil.get('candidate_id')!=candidate_id or civil.get('body_candidate_id')!=vehicle['candidate_id'] or civil.get('alternative_candidate_id')!=alternative['candidate_id'] or civil.get('evaluation_id')!=identity({k:v for k,v in civil.items() if k!='evaluation_id'}):
        raise ValueError('Manufacturing civil geometry must bind this complete cell and launch alternative')
    a=deepcopy(process or assumptions())
    if set(a)!=set(assumptions()) or a.get('source_class')!='C' or a.get('source_id')!=identity({k:v for k,v in a.items() if k!='source_id'}):raise ValueError('Exact explicit process-rate hypothesis required')
    for k in ('blank_allowance_m','kerf_m'):
        if type(a[k]) not in (int,float) or not isfinite(a[k]) or a[k]<0:raise ValueError('Nonnegative physical blank allowance required')
    for k in ('cutting_m_per_h','mould_contact_m2_per_h','machine_removal_m3_per_h','labour_usd_per_h','material_usd_per_kg',
        'receiving_h_per_unit','assembly_h_per_unit','inspection_h_per_unit','composite_cure_h','tooling_setup_h','mould_service_life_cycles'):
        if not isinstance(a[k],list) or len(a[k])!=2 or any(type(x) not in (int,float) or not isfinite(x) or x<=0 for x in a[k]) or a[k][0]>a[k][1]:raise ValueError('Positive ordered process-rate bounds required: '+k)
    if type(a['workstations']) is not int or not 1<=a['workstations']<=1000 or type(a['shift_hours']) not in (int,float) or not 0<a['shift_hours']<=24:
        raise ValueError('Positive explicit workstation/shift plan required')
    parts={p['physical_definition_id']:p for p in vehicle['registry']['parts']};counts=Counter(o['part_definition_id'] for o in vehicle['registry']['occurrences'])
    routes=[];known_cost=[0.,0.];known_hours=[0.,0.];gross_mass=0.;net_mass=0.;purchased=0;unpriced=[]
    for key,p in sorted(parts.items()):
        g=p['geometry'];b=blank(g,allowance_m=a['blank_allowance_m'],kerf_m=a['kerf_m']);n=counts[key]
        mass=p['mass'];nom=mass.get('calculated_kg');method=p['manufacturing']['method'];is_composite=any(x in method.lower() for x in ('infus','laminat','mould','sandwich'))
        if g['kind']=='envelope':
            purchased+=n;unit_hours=None;material=None;batch_cycle=None;tool=None;unpriced.append(p['part_id'])
            operations=['procure-qualified-module','receive-inspect','mount-removably','connect-test']
        else:
            density=nom/g['net_volume_m3'];gross=b['blank_volume_m3']*density;gross_mass+=gross*n;net_mass+=nom*n
            unit_hours=[b['cut_length_m']/a['cutting_m_per_h'][1-i]+b['removed_volume_m3']/a['machine_removal_m3_per_h'][1-i] for i in range(2)]
            if is_composite:unit_hours=[unit_hours[i]+b['exposed_mould_area_m2']/a['mould_contact_m2_per_h'][1-i] for i in range(2)]
            unit_hours=[unit_hours[i]+a['assembly_h_per_unit'][i]+a['inspection_h_per_unit'][i] for i in range(2)]
            material=[gross*a['material_usd_per_kg'][i] for i in range(2)]
            unit_cost=[material[i]+unit_hours[i]*a['labour_usd_per_h'][i] for i in range(2)]
            for i in range(2):known_cost[i]+=unit_cost[i]*n;known_hours[i]+=unit_hours[i]*n
            batch_cycle=a['composite_cure_h'] if is_composite else None
            tool=dict(tooling_id='prototype-tool/'+key,setup_h=a['tooling_setup_h'],service_life_cycles=a['mould_service_life_cycles'],
                mould_geometry_definition=g,qualified=False,tool_price_usd=None) if is_composite else None
            operations=['dimensioned-blank','cut-and-machine','surface-prepare-layup-and-cure' if is_composite else 'form-join-finish','inspect','assemble-inspect']
        routes.append(dict(candidate_id=candidate_id,part_definition_id=key,part_revision_id=p['revision_id'],quantity=n,
            material_id=p['material_id'],method=method,blank=b,labour_h_per_unit=unit_hours,
            unattended_cure_h_per_batch=batch_cycle,tooling=tool,material_scope_cost_usd=material,
            operations=[dict(sequence=i+1,name=op,workstation='prototype/'+op,work_instruction_id=None) for i,op in enumerate(operations)],
            qualified_manufacturing_cycle_h=None,source_id=a['source_id'],production_release=False))
    civil_slots=deepcopy(civil.get('construction_sequence',[]))
    value=dict(schema='osr-dimensional-production-plan/1',candidate_id=candidate_id,body_candidate_id=vehicle['candidate_id'],
        process_assumptions=a,routings=routes,net_counted_vehicle_stock_kg=net_mass,dimensioned_vehicle_blank_kg=gross_mass,
        removed_or_offcut_vehicle_stock_kg=gross_mass-net_mass,known_vehicle_stock_process_cost_usd=known_cost,
        known_vehicle_labour_h=known_hours,conditional_vehicle_labour_days=[h/(a['shift_hours']*a['workstations']) for h in known_hours],
        purchased_occurrences=purchased,purchased_module_processes_unknown=True,unpriced_part_ids=unpriced,
        civil_construction_slots=civil_slots,alternative_plant_inventory=deepcopy(alternative['inventory']),
        complete_installed_cost_usd=None,tooling_cost_usd=None,whole_life_cost_usd=None,
        unknown_whole_life_scopes=['Purchased equipment prices','Actual tooling, labour, cure yields and qualified processes','Stations, access, land/utilities/depot',
            'Complete electrical/cooling/supply/protection','Recovery, fleet availability, energy, maintenance and renewal'],
        ERPNext_drafts=_drafts(vehicle,alternative,candidate_id,parts,counts,routes),**FLAGS)
    value['evaluation_id']=identity(value);return value
