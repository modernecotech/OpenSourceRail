"""Occurrence-linked routings, conditional A/B/C cost bounds and disabled ERP drafts."""
from collections import Counter
from math import fsum,isfinite
from copy import deepcopy
from datetime import date
from engineering.component_registry import validate_registry
from . import identity,FLAGS

SCOPES=('rolling-stock','guideway','stations-power','factory-tooling','construction','land-utilities-depot',
        'fleet','energy','maintenance','renewals','recovery','reliability')


def scenario():
    """Explicit C inputs for sensitivity; no numbers are claimed as market prices."""
    value=dict(schema='osr-reference-cell-cost-scenario/1',source_class='C',currency='USD',
        source_date='2026-10-28',location='unsurveyed-reference-cell',quantity_basis='kg-and-process-hour',
        confidence='Unverified illustrative engineering assumptions; replace with dated local quotes and measured process rates',
        source='engineering/reference_cell/manufacturing.py::scenario',
        stock_usd_per_kg=[2.,30.],purchased_assembly_usd_per_kg=[10.,100.],labour_usd_per_h=[8.,40.],
        manufactured_kg_per_labour_h=[1.,30.],assembly_h_per_occurrence=[.01,.15],
        inspection_h_per_occurrence=[.005,.05],transport_usd_per_kg=[.01,.30],installation_h_per_occurrence=[.005,.1],
        default_yield_interval=[.8,.98],tooling_allocation_usd_per_part=None)
    value['source_id']=identity(value);return value


def _range(v,label):
    if not isinstance(v,list) or len(v)!=2 or any(type(x) not in (float,int) or not isfinite(x) or x<0 for x in v) or v[0]>v[1]:
        raise ValueError('Finite ordered '+label+' bounds required')
    return v


def _scenario(s):
    if s.get('schema')!='osr-reference-cell-cost-scenario/1' or s.get('source_class') not in ('B','C') or s.get('currency')!='USD':
        raise ValueError('Explicit non-procurement engineering estimate scenario required')
    if s.get('source_id')!=identity({k:v for k,v in s.items() if k!='source_id'}):raise ValueError('Scenario source identity differs')
    for k in ('source_date','location','quantity_basis','confidence','source'):
        if not isinstance(s.get(k),str) or not s[k]:raise ValueError('Cost '+k+' required')
    date.fromisoformat(s['source_date'])
    for k in ('stock_usd_per_kg','purchased_assembly_usd_per_kg','labour_usd_per_h','manufactured_kg_per_labour_h',
              'assembly_h_per_occurrence','inspection_h_per_occurrence','transport_usd_per_kg','installation_h_per_occurrence','default_yield_interval'):_range(s[k],k)
    if s['manufactured_kg_per_labour_h'][0]<=0 or not 0<s['default_yield_interval'][0]<=s['default_yield_interval'][1]<=1:
        raise ValueError('Positive production rate and bounded physical yield required')
    return s


def compile(vehicle,civil,*,estimate=None,quotes=(),authenticator=None,bundle=None):
    r=vehicle['registry'];validate_registry(r);candidate=r['candidate_id']
    if vehicle['candidate_id']!=candidate:raise ValueError('Vehicle registry identity differs')
    if bundle is not None:
        from engineering.design_search.railway_bundle import validate
        validate(bundle)
        if bundle['body_candidate_id']!=candidate:raise ValueError('Manufacturing bundle uses another vehicle registry')
        candidate=bundle['candidate_id']
    if civil['candidate_id']!=candidate:raise ValueError('Manufacturing requires same physical candidate')
    s=_scenario(deepcopy(estimate) if estimate is not None else scenario());parts={p['physical_definition_id']:p for p in r['parts']}
    counts=Counter(o['part_definition_id'] for o in r['occurrences']);quotes_by={}
    for q in quotes:
        if q.get('candidate_id')!=candidate or q.get('part_definition_id') not in parts or q.get('source_class')!='A':
            raise ValueError('Actual quote must bind candidate and part, class A')
        if authenticator is None or authenticator(q,'supplier-quote') is not True:raise ValueError('External actual-quote authentication required')
        if q.get('quote_id')!=identity({k:v for k,v in q.items() if k!='quote_id'}):raise ValueError('Quote content identity differs')
        for name in ('supplier','source_date','valid_until','currency','location','quantity_basis','source_document_sha256'):
            if not isinstance(q.get(name),str) or not q[name]:raise ValueError('Actual quote '+name+' required')
        if q['currency']!='USD' or q['quantity_basis']!='one-part':raise ValueError('Same-unit USD quote required; retain conversion source upstream')
        if q.get('quote_scope') not in ('finished-part','material-blank'):raise ValueError('Explicit quote scope required')
        if len(q['source_document_sha256'])!=64 or any(c not in '0123456789abcdef' for c in q['source_document_sha256']):raise ValueError('Actual quote document digest required')
        if date.fromisoformat(q['source_date'])>date.fromisoformat(s['source_date']):raise ValueError('Quote postdates estimate')
        if date.fromisoformat(q['valid_until'])<date.fromisoformat(s['source_date']):raise ValueError('Quote expires before estimate date')
        _range(q['unit_usd'],'quote');key=q['part_definition_id']
        if key in quotes_by:raise ValueError('Select one valid quotation per part explicitly')
        quotes_by[key]=q
    routes=[];rfqs=[];items=[];part_costs=[];complete_known=True
    for key,p in sorted(parts.items()):
        n=counts[key];mass=p['mass'];lo=mass.get('lower_bound_kg');hi=mass.get('upper_bound_kg');purchased=p['geometry']['kind']=='envelope'
        if lo is None and mass.get('calculated_kg') is not None:lo=hi=mass['calculated_kg']
        y=p['manufacturing'].get('gross_to_net_yield_hypothesis')
        if y is not None and (type(y) not in (int,float) or not isfinite(y) or not 0<y<=1):raise ValueError('Physical per-part yield required')
        yield_bounds=[y,y] if y is not None else s['default_yield_interval']
        gross=None if lo is None else [lo/yield_bounds[1],hi/yield_bounds[0]]
        hours=None if gross is None or purchased else [gross[0]/s['manufactured_kg_per_labour_h'][1],gross[1]/s['manufactured_kg_per_labour_h'][0]]
        raw_rate=s['purchased_assembly_usd_per_kg'] if purchased else s['stock_usd_per_kg']
        material=None if lo is None else [lo*raw_rate[0],hi*raw_rate[1]] if purchased else [gross[0]*raw_rate[0],gross[1]*raw_rate[1]]
        processing=None if hours is None else [hours[0]*s['labour_usd_per_h'][0],hours[1]*s['labour_usd_per_h'][1]]
        known_components={'material_or_purchased':material,'processing':None if purchased else processing,
            'assembly':[s['assembly_h_per_occurrence'][i]*s['labour_usd_per_h'][i] for i in range(2)],
            'inspection':[s['inspection_h_per_occurrence'][i]*s['labour_usd_per_h'][i] for i in range(2)],
            'transport':None if lo is None else [lo*s['transport_usd_per_kg'][0],hi*s['transport_usd_per_kg'][1]],
            'installation':[s['installation_h_per_occurrence'][i]*s['labour_usd_per_h'][i] for i in range(2)],
            'allocated_tooling':s.get('tooling_allocation_usd_per_part')}
        # No processing charge is added to a purchased-unit price. Unknown tooling
        # stays outside the known conditional subtotal and blocks full cost.
        known_subtotal=None if material is None else [fsum(v[i] for k,v in known_components.items() if v is not None) for i in range(2)]
        actual_quote=quotes_by.get(key)
        if actual_quote:
            known_components['material_or_purchased']=actual_quote['unit_usd']
            if actual_quote['quote_scope']=='finished-part':known_components['processing']=None
            known_subtotal=[fsum(v[i] for v in known_components.values() if v is not None) for i in range(2)]
        complete_known &= known_subtotal is not None
        part_costs.append(dict(part_definition_id=key,part_revision_id=p['revision_id'],candidate_id=candidate,count=n,
            cost_source_class=s['source_class'],material_or_purchased_source_class='A' if actual_quote else s['source_class'],
            component_source_ids=[s['source_id']]+([] if actual_quote is None else [actual_quote['quote_id']]),source_id=s['source_id'],
            currency='USD',source_date=actual_quote['source_date'] if actual_quote else s['source_date'],location=s['location'],quantity_basis='one-part',
            components_usd=known_components,known_scope_subtotal_usd=known_subtotal,complete_installed_unit_cost_usd=None,
            quoted_price_is_full_installed_scope=False,tooling_and_full_operations_qualified=False))
        operations=['receive-inspect'] if purchased else ['prepare-blank','form-machine-or-mould','join-cure-or-finish','inspect']
        operations+=['assemble-with-counted-mating-parts','test-and-release-by-human','transport','install-and-inspect']
        route=dict(candidate_id=candidate,part_definition_id=key,part_revision_id=p['revision_id'],quantity=n,
            net_mass_interval_kg=None if lo is None else [lo,hi],gross_mass_interval_kg=gross,
            gross_to_net_yield_hypothesis=yield_bounds,manufacturing_method=p['manufacturing']['method'],
            process_labour_h_per_unit=hours,operations=[dict(sequence=i+1,name=op,workstation=None,cycle_hours=None,approved_work_instruction=None) for i,op in enumerate(operations)],
            tooling=p['manufacturing'].get('tooling_id'),batch_size=None,local_value_added_fraction=None,
            production_throughput_per_day=None,manufacturing_release=False)
        route['routing_id']=identity(route);routes.append(route)
        items.append(dict(doctype='Item',item_code=p['part_id']+'-'+p['revision_id'][:12],candidate_id=candidate,
            engineering_part_definition_id=key,engineering_revision_id=p['revision_id'],disabled=1,is_stock_item=1))
        rfqs.append(dict(doctype='Request for Quotation',candidate_id=candidate,part_definition_id=key,quantity=n,
            disabled=True,docstatus=0,workflow_state='Engineering draft - human review required',
            supplier=None,transaction_submission_allowed=False))
    known=[c for c in part_costs if c['known_scope_subtotal_usd'] is not None]
    total=[fsum(c['known_scope_subtotal_usd'][i]*c['count'] for c in known) for i in range(2)]
    civil_mass=civil['known_material_mass_kg'];civil_budget=[civil_mass*s['stock_usd_per_kg'][i] for i in range(2)]
    assembly_code='OSR-'+vehicle.get('vehicle_id',candidate[:12])
    cars=vehicle.get('requirements',{}).get('cars')
    car_bom=(cars==6 and all(n%cars==0 for n in counts.values()))
    package_bom=dict(doctype='BOM',candidate_id=candidate,item=assembly_code+'-TRAIN',quantity=1,docstatus=0,is_active=0,is_default=0,
        items=[dict(item_code=assembly_code+'-CAR',qty=cars)] if car_bom else [dict(item_code=parts[k]['part_id']+'-'+parts[k]['revision_id'][:12],qty=n) for k,n in sorted(counts.items())],
        source_registry_id=r['registry_id'],field_mapping_and_import_validation='pending')
    boms=[package_bom]
    if car_bom:boms.append(dict(package_bom,item=assembly_code+'-CAR',items=[dict(item_code=parts[k]['part_id']+'-'+parts[k]['revision_id'][:12],qty=n/cars) for k,n in sorted(counts.items())]))
    value=dict(schema='osr-reference-cell-manufacturing-cost/1',candidate_id=candidate,estimate_scenario=s,
        EBOM=[dict(candidate_id=candidate,part_definition_id=k,revision_id=parts[k]['revision_id'],quantity=n) for k,n in sorted(counts.items())],
        MBOM=routes,part_costs=part_costs,known_vehicle_scope_conditional_usd=total,
        all_known_vehicle_occurrences_have_conditional_budget=complete_known,
        actual_quote_part_count=len(quotes_by),actual_quoted_occurrence_count=sum(counts[k] for k in quotes_by),
        actual_quote_occurrence_coverage=sum(counts[k] for k in quotes_by)/len(r['occurrences']),
        counted_civil_material_only_C_sensitivity_usd=civil_budget,
        complete_installed_vehicle_cost_usd=None,complete_CAPEX_usd=None,whole_life_cost_usd=None,
        missing_whole_life_scopes=list(SCOPES),economic_winner=None,
        ERPNext=dict(items=items,rfq_drafts=rfqs,
            BOM_drafts=boms,assembly_item_drafts=[dict(doctype='Item',item_code=x['item'],disabled=1,candidate_id=candidate) for x in boms],
            routing_drafts=[dict(target_doctype='Routing',candidate_id=candidate,routing_id=x['routing_id'],operations=x['operations'],approved=False) for x in routes],
            workstation_requirements=[dict(target_doctype='Workstation',process=x['manufacturing_method'],qualified_capacity=None,approved=False) for x in routes],
            production_orders=[],active_asset_records=[],
            external_transactions_performed=False,automatic_redesign_changes_active_orders=False,
            required_mappings={'assembly':'BOM','operations':'Routing/Operation','resources':'Workstation','released_batch':'Work Order',
                'external_need':'Material Request/Request for Quotation','price':'Supplier Quotation','accepted_component':'Quality Inspection/Stock Entry','installed_equipment':'Asset/Maintenance Schedule'}),
        construction_sequence_id=identity(civil['construction_sequence']),
        uncertainty_priority=['Complete installed equipment and approved geometry','Actual supplier quotes, source dates, currency/location/validity',
            'Measured process yield/cycle/tooling and crew/transport/site access','Protected service, energy, maintenance, reliability and renewals'],**FLAGS)
    value['evaluation_id']=identity(value);return value
