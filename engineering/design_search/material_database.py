"""Component material/form/process search over retained primary-source leads.

Compatibility here means a catalogue filter matches the requested facts. It is
not a design allowable, a qualified material substitution or native-model
admission. Typical coupon numbers, continuous-temperature claims and rail fire
acceptance remain different fields. Missing data is never filled by isotropy,
an unrelated grade, room-temperature extrapolation or a generic price.
"""
from copy import deepcopy
from pathlib import Path
from math import isfinite
from . import structural_families as structural,joining_catalogue as joining
from engineering.station_rail.common import identity,digest

PRODUCER='engineering/design_search/material_database.py'
FLAGS=dict(physical_accepted=False,engineering_accepted=False,configuration_adopted=False,
           manufacturing_release=False,operating_release=False)


def _fact(value,unit,sources,*,direction='scalar',temperature=None,temperature_range=None,basis='supplier-typical',scope='Published material/coupon fact only; not a design allowable'):
    return dict(value=value,unit=unit,direction=direction,test_temperature_C=temperature,
        measured_temperature_range_C=temperature_range,basis=basis if value is not None else 'unknown',source_ids=list(sources),
        design_allowable=False,scope=scope)


def source_map():
    return {PRODUCER:digest(__file__),'engineering/design_search/structural_families.py':digest(structural.__file__),
        'engineering/design_search/joining_catalogue.py':digest(joining.__file__)}


def _record(name,kind,functions,forms,sources,properties,original,*,routes=(),mandatory_processes=(),temperature=None,processing_max=None):
    r=dict(id=name,kind=kind,source_designation=original.get('grade',original.get('proposed_stock_alloy',original.get('id'))),
        candidate_functions=list(functions),function_roles_are_exhaustive=False,
        forms=list(forms),source_ids=list(sources),properties=properties,
        process=dict(candidate_routes=[list(x) for x in routes],mandatory=list(mandatory_processes),
            routes_are_exhaustive=False,process_qualified=False,route_provenance='Proposed research manufacturing routes; supplier endorsement is not inferred',
            mandatory_process_basis='Pinned supplier cure requirement where explicitly present; otherwise no mandatory route inferred'),
        operating_temperature_claim_C=temperature,maximum_processing_temperature_claim_C=processing_max,
        complete_orthotropic_matrix=None,strength_design_allowables=None,hot_wet_design_allowables=None,
        fatigue_model=None,rail_fire_acceptance=None,thermal_expansion_design_data=None,
        stock_dimensions_and_availability=None,purchased_lot_properties=None,
        installed_price_USD=None,unit_price_USD_per_kg=None,price_coverage='unknown; no generic price supplied',
        upstream_facts=deepcopy(original),automatic_substitution_eligible=False,native_material_law_available=False,
        scope='Research sourcing/filter record; actual function, interfaces, manufacturing and qualification need separate evidence',**FLAGS)
    r['record_id']=identity(r);return r


def catalogue():
    sc=structural.material_catalogue();jc=joining.catalogue();records=[];sources={}
    for key,row in sc['sources'].items():
        sources['structural.'+key]=dict(url=row['url'],revision=row.get('revision'),pages_one_based=row.get('pages',[]),
            raw_document_sha256=row.get('sha256'),source_kind='retained-primary-supplier-reference',
            adapter_retrieved_document=False,raw_bytes_independently_reverified=False)
    for key,row in jc['sources'].items():
        sources['joining.'+key]=dict(**deepcopy(row),source_kind='retained-primary-supplier-reference',
            adapter_retrieved_document=False,raw_bytes_independently_reverified=False)
    for key,row in sc['cores'].items():
        ss=['structural.'+n for n in row['source_ids']];t=row.get('source_test_temperature_C');props={}
        for name,unit,direction in [('density_kg_m3','kg/m3','scalar'),('compression_modulus_T_Pa','Pa','T'),
            ('shear_modulus_LT_Pa','Pa','LT'),('shear_modulus_WT_Pa','Pa','WT'),
            ('compression_strength_bare_Pa','Pa','T'),('shear_strength_LT_Pa','Pa','LT'),('shear_strength_WT_Pa','Pa','WT')]:
            props[name]=_fact(row.get(name),unit,ss,direction=direction,temperature=t)
        for name,value in row.get('minimum_properties_Pa',{}).items():
            direction='LT' if name.endswith('_LT') else 'WT' if name.endswith('_WT') else 'T'
            props['minimum_'+name+'_Pa']=_fact(value,'Pa',ss,direction=direction,temperature=t,basis='supplier-minimum-test-checkpoint',
                scope='Published minimum coupon/test checkpoint, not a structural design allowable')
        props['thermal_expansion_per_K']=_fact(None,'1/K',ss,basis='unknown')
        chem=row.get('chemistry','');form='honeycomb-core' if 'honeycomb' in chem else 'foam-core'
        r=_record('core.'+key,'material',['sandwich-core','floor-core','roof-core','sidewall-core'],[form,'core-sheet'],ss,props,row,
            routes=[['core-cutting','bonded-sandwich'],['core-cutting','infusion']],
            temperature=dict(minimum=None,maximum=row.get('continuous_temperature_claim_C'),basis='supplier-continuous-temperature-claim',qualifies_hot_strength=False),
            processing_max=row.get('processing_temperature_claim_C'))
        r['direction_axes']=deepcopy(sc['axes']);r['record_id']=identity({n:v for n,v in r.items() if n!='record_id'});records.append(r)
    kinds={
      'bonded-flange':(['structural-joint','adhesive'],['mixed-adhesive','bondline'],[['surface-preparation','controlled-mixing','bonding']]),
      'bond-plus-bolts':(['structural-joint','positive-retention'],['bondline','fastener-assembly'],[['bonding','drilling','bolted-assembly']]),
      'potted-insert':(['sandwich-insert','structural-joint'],['potting-compound','insert-assembly'],[['potting','controlled-heat-cure']]),
      'sandwich-core':(['sandwich-core','roof-core','floor-core'],['foam-core','core-sheet'],[['core-cutting','bonded-sandwich']]),
      'welded-node':(['body-member','structural-joint'],['aluminium-extrusion','welded-node'],[['GTAW/TIG'],['GMAW/MIG']]),
      'clip-plus-positive-retention':(['removable-service-panel','positive-retention'],['matched-clip-pair','captive-fastener'],[['drilling','retained-panel-assembly']]),
      'glazing':(['window-pane'],['flat-sheet'],[['sheet-cutting','retained-glazing']]),
      'HVAC':(['HVAC-module'],['packaged-module'],[['module-mounting','ducting','electrical-assembly']]),
    }
    for row in jc['entries']:
        functions,forms,routes=kinds[row['family']];ss=['joining.'+n for n in row['sources']];props={}
        for name,unit,direction in [('density_kg_m3','kg/m3','scalar'),('typical_density_kg_m3','kg/m3','scalar'),
            ('typical_tensile_modulus_Pa','Pa','in-plane-unspecified'),('thermal_expansion_per_K','1/K','in-plane-unspecified'),
            ('minimum_compressive_Pa','Pa','T'),('minimum_shear_Pa','Pa','unspecified'),('nominal_shear_modulus_Pa','Pa','unspecified'),
            ('supplier_module_mass_kg','kg','scalar'),('cooling_capacity_at_50C_W','W','scalar')]:
            if name in row:
                props[name]=_fact(row[name],unit,ss,direction=direction,temperature=row.get('properties_temperature_C'),
                    temperature_range=row.get('expansion_measurement_range_C') if name=='thermal_expansion_per_K' else None,
                    basis='supplier-minimum-test-checkpoint' if name.startswith('minimum_') else 'supplier-typical')
        if 'typical_density_kg_m3' in props and 'density_kg_m3' not in props:props['density_kg_m3']=deepcopy(props['typical_density_kg_m3'])
        if 'coupon' in row:
            coupon=row['coupon'];value=coupon.get('typical_stress_Pa',coupon.get('typical_compressive_Pa'))
            props['coupon_strength_Pa']=_fact(value,'Pa',ss,direction='coupon-specific',temperature=coupon.get('test_temperature_C'),
                scope='Only the stated substrate, coupon, preparation, cure and failure mode; never a joint allowable')
        if 'hot_coupon' in row:
            props['hot_coupon_strength_Pa']=_fact(row['hot_coupon'].get('typical_stress_Pa'),'Pa',ss,direction='coupon-specific',temperature=row['hot_coupon'].get('test_temperature_C'))
        continuous=row.get('continuous_temperature_C');temp=None if continuous is None else dict(minimum=continuous[0],maximum=continuous[1],basis='supplier-continuous-temperature-claim',qualifies_hot_strength=False)
        records.append(_record('joining.'+row['id'],'component-or-joining-lead',functions,forms,ss,props,row,routes=routes,
            mandatory_processes=['controlled-heat-cure'] if row['family']=='potted-insert' else [],temperature=temp,
            processing_max=row.get('maximum_processing_temperature_C')))
    result=dict(schema='osr-component-material-database/1',records=records,sources=sources,source_sha256=source_map(),
        search_scope='Compatibility of requested catalogue facts and declared available processes only; no physical qualification or evaluator admission',
        unknown_is_zero=False,**FLAGS)
    result['database_id']=identity(result);return result


def _finite(value):return type(value) in (float,int) and isfinite(value)


def _range(value):
    if _finite(value):return [float(value),float(value)]
    if isinstance(value,(list,tuple)) and len(value)==2 and all(_finite(x) for x in value) and value[0]<=value[1]:return list(value)
    raise ValueError('Finite operating-temperature value or ordered pair required')


def search(function_requirements,available_processes=None):
    """Return compatible/unknown/excluded sourcing records with exact reasons.

    Requirements: function or functions; optional forms; operating_temperature_C
    and processing_temperature_C; maximum_density_kg_m3; property_requirements
    [{name,unit,value,operator:>=|<=,direction?,basis?:typical|design-allowable}];
    require_rail_fire/require_hot_wet/require_fatigue/require_design_allowables/
    require_complete_orthotropic_matrix. Unrecognized requirements are refused.
    No condition silently drops out of the filter.
    """
    rq=deepcopy(function_requirements)
    allowed={'function','functions','forms','operating_temperature_C','processing_temperature_C','maximum_density_kg_m3',
        'property_requirements','require_rail_fire','require_hot_wet','require_fatigue','require_design_allowables','require_complete_orthotropic_matrix'}
    if not isinstance(rq,dict) or set(rq)-allowed:raise ValueError('Explicit supported functional material requirements required')
    if 'function' in rq and 'functions' in rq:raise ValueError('Use function or functions, not ambiguous duplicate requirement fields')
    functions=rq.get('functions',[rq['function']] if 'function' in rq else [])
    if not isinstance(functions,list) or not functions or any(not isinstance(f,str) or not f for f in functions):raise ValueError('Explicit candidate function roles required')
    forms=rq.get('forms',[])
    if not isinstance(forms,list) or any(not isinstance(f,str) or not f for f in forms):raise ValueError('Explicit form identifiers required')
    if available_processes is not None and (not isinstance(available_processes,(list,tuple,set)) or any(not isinstance(x,str) or not x for x in available_processes)):raise ValueError('Available process identifiers required')
    available=None if available_processes is None else set(available_processes)
    temperature=None if rq.get('operating_temperature_C') is None else _range(rq['operating_temperature_C'])
    processing=None if rq.get('processing_temperature_C') is None else _range(rq['processing_temperature_C'])
    for key in ('require_rail_fire','require_hot_wet','require_fatigue','require_design_allowables','require_complete_orthotropic_matrix'):
        if key in rq and type(rq[key]) is not bool:raise ValueError('Boolean evidence requirement required: '+key)
    density=rq.get('maximum_density_kg_m3')
    if density is not None and (not _finite(density) or density<=0):raise ValueError('Positive finite density bound required')
    property_requirements=rq.get('property_requirements',[])
    if not isinstance(property_requirements,list):raise ValueError('Explicit typed property requirements required')
    for p in property_requirements:
        if not isinstance(p,dict) or set(p)-{'name','unit','value','operator','direction','basis'} or not isinstance(p.get('name'),str) or not isinstance(p.get('unit'),str) or not _finite(p.get('value')) or p.get('operator','>=') not in ('>=','<=') or p.get('basis','typical') not in ('typical','design-allowable'):raise ValueError('Typed property name/unit/value/operator/basis required')
    db=catalogue();matches=[]
    for record in db['records']:
        excluded=[];unknown=[];matched=[]
        if not set(functions)<=set(record['candidate_functions']):unknown.append('function-route-not-established; novel use requires a new functional/material evaluation')
        if forms and not set(forms)&set(record['forms']):unknown.append('requested-stock-form-not-established; new sourcing/process route required')
        claim=record['operating_temperature_claim_C']
        if temperature is not None:
            if claim is None:unknown.append('continuous-operating-temperature-claim-unavailable')
            elif ((claim['maximum'] is not None and temperature[1]>claim['maximum']) or
                  (claim['minimum'] is not None and temperature[0]<claim['minimum'])):excluded.append('outside-published-continuous-temperature-claim')
            else:matched.append('within-published-temperature-claim; hot-load-allowable-not-inferred')
        if processing is not None:
            maximum=record['maximum_processing_temperature_claim_C']
            if maximum is None:unknown.append('processing-temperature-compatibility-unavailable')
            elif processing[1]>maximum:excluded.append('outside-published-processing-temperature-claim')
        if available is not None:
            missing=set(record['process']['mandatory'])-available
            if missing:excluded.append('declared-process-inventory-missing-mandatory:'+','.join(sorted(missing)))
            elif any(set(route)<=available for route in record['process']['candidate_routes']):matched.append('candidate-process-route-in-declared-inventory; process-not-qualified')
            else:unknown.append('no-listed-process-route-in-inventory; alternatives-not-exhausted')
        if density is not None:
            d=record['properties'].get('density_kg_m3',{}).get('value')
            if d is None:unknown.append('density-unavailable')
            elif d>density:excluded.append('published-density-above-requested-bound')
            else:matched.append('published-density-within-requested-bound')
        for request in property_requirements:
            prop=record['properties'].get(request['name']);label=request['name']
            if prop is None or prop['value'] is None:unknown.append('property-unavailable:'+label);continue
            if request['unit']!=prop['unit']:raise ValueError('Property unit mismatch; explicit conversion required: '+label)
            if request.get('direction') is not None and request['direction']!=prop['direction']:unknown.append('direction-not-supported:'+label);continue
            if request.get('basis','typical')=='design-allowable' and prop['design_allowable'] is not True:unknown.append('design-allowable-unavailable:'+label);continue
            if temperature is not None:
                domain=prop['measured_temperature_range_C']
                if domain is None and prop['test_temperature_C'] is not None:domain=[prop['test_temperature_C']]*2
                if domain is None or temperature[0]<domain[0] or temperature[1]>domain[1]:unknown.append('no-temperature-extrapolation:'+label);continue
            okay=prop['value']>=request['value'] if request.get('operator','>=')=='>=' else prop['value']<=request['value']
            (matched if okay else excluded).append(('published-property-matches:' if okay else 'published-property-outside-bound:')+label)
        for request,key in [('require_rail_fire','rail_fire_acceptance'),('require_hot_wet','hot_wet_design_allowables'),
            ('require_fatigue','fatigue_model'),('require_design_allowables','strength_design_allowables'),
            ('require_complete_orthotropic_matrix','complete_orthotropic_matrix')]:
            if rq.get(request) and record[key] is None:unknown.append('required-evidence-unavailable:'+key)
        matches.append(dict(record_id=record['record_id'],id=record['id'],status='excluded' if excluded else 'unknown' if unknown else 'compatible',
            matched=matched,unknown=unknown,excluded=excluded,source_ids=record['source_ids'],properties=record['properties'],
            installed_price_USD=None,automatic_substitution_eligible=False,**FLAGS))
    value=dict(schema='osr-component-material-search/1',database_id=db['database_id'],requirements=rq,
        available_processes=None if available is None else sorted(available),matches=matches,
        compatibility_means='Matches requested catalogue facts only; not a design/material/process qualification',
        source_sha256=db['source_sha256'],selected_record_id=None,**FLAGS)
    value['search_id']=identity(value);return value
