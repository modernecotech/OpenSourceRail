"""Canonical-bundle installed-inventory and manufacturing research adapter.

Located nominal body stock, retained unlocated accounts and unknown joints are
kept in separate rows. Source accounts do not acquire invented coordinates or
inertias. Manufacturing cuts are gross nominal blanks, not fabricated/net joint
geometry. Commercial evidence is byte/context checked, never an installed quote
or authorization to procure or operate.
"""
from copy import deepcopy
from pathlib import Path
from math import sqrt,isfinite
import json,re
from . import design_grammar as grammar,grammar_geometry as geometry,dfma,material_database
from .system_selection import pareto
from engineering.station_rail import ROOT
from engineering.station_rail.common import identity,digest

PRODUCER='engineering/design_search/system_inventory.py'
FLAGS=dict(physical_accepted=False,engineering_accepted=False,configuration_adopted=False,
           manufacturing_release=False,operating_release=False)


def _sha(value):return isinstance(value,str) and re.fullmatch('[0-9a-f]{64}',value) is not None
def _finite(value):return type(value) in (float,int) and isfinite(value)


def _quantity(value,unit,scope,basis):
    return dict(value=value,interval=None if value is None else [value,value],unit=unit,scope=scope,basis=basis,
        uncertainty_scope='Nominal definition/account arithmetic only; manufactured and complete installed uncertainty is not established')


def _supply(rows,references,bundle_id,root):
    out={};root=Path(root).resolve()
    for reference in references:
        if not isinstance(reference,dict) or not isinstance(reference.get('path'),str) or not _sha(reference.get('sha256')):raise ValueError('Explicit local supply-evidence path and digest required')
        rel=Path(reference['path']);p=root/rel
        if rel.is_absolute() or '..' in rel.parts or not rel.parts or not p.resolve().is_relative_to(root):raise ValueError('Supply evidence must be an ordinary path inside source_root')
        for q in (p,*p.parents):
            if q==root:break
            if q.is_symlink():raise ValueError('Ordinary supply evidence files required')
        if not p.is_file() or digest(p)!=reference['sha256']:raise ValueError('Supply evidence bytes differ')
        r=json.loads(p.read_bytes());name=r.get('component_occurrence_id')
        if r.get('schema')!='osr-system-supply-evidence/1' or r.get('bundle_id')!=bundle_id or name not in rows or r.get('component_definition_id')!=rows[name]['component_definition_id']:raise ValueError('Supply evidence uses a different bundle/component definition')
        if not _sha(rows[name]['component_definition_id']):raise ValueError('Unresolved equipment requires a physical component definition before source pricing')
        if name in out:raise ValueError('Explicitly select one supply record per component before comparison')
        if r.get('evidence_kind') not in ('supplier-quote','supplier-catalogue','measured-prototype') or not isinstance(r.get('supplier'),str) or not r['supplier'] or not isinstance(r.get('source_locator'),str) or not r['source_locator']:raise ValueError('Typed supplier/source provenance required')
        price=r.get('unit_price_USD');lead=r.get('lead_time_days')
        if price is not None and (not _finite(price) or price<0 or r.get('currency')!='USD'):raise ValueError('Explicit USD source price or unknown required; no exchange rate inferred')
        if lead is not None and (not _finite(lead) or lead<0):raise ValueError('Finite nonnegative source lead time or unknown required')
        unit=r.get('quantity_unit');needed=rows[name]['accounted_mass_kg'] if unit=='kg' else float(rows[name]['quantity']) if unit==rows[name]['unit'] else None
        quote=r.get('quoted_quantity')
        if price is not None and (needed is None or not _finite(quote) or quote<needed):raise ValueError('Quote quantity/unit must cover this explicit component stock/account')
        out[name]=dict(record=deepcopy(r),evidence=deepcopy(reference),known_quoted_subtotal_USD=None if price is None else needed*price,
            commercial_validity_assessed=False,installed_cost_coverage=False,
            verification_scope='Local byte and bundle/component/unit/quantity matching only; current availability, authenticity and commercial acceptance require review')
    return out


def _blank(part):
    if part['kind']=='box':
        return dict(kind='rectangular-blank',at_m=part['at_m'],dimensions_m=part['size_m'],nominal_gross_volume_m3=part['volume_m3'],
            nesting_yield=None,kerf_m=None,stock_sheet_size_m=None,net_cut_geometry=None)
    if part['kind']=='oriented-RHS':
        L=sqrt(sum((b-a)**2 for a,b in zip(part['start_m'],part['end_m'])))
        return dict(kind='hollow-section-cut',start_m=part['start_m'],end_m=part['end_m'],length_m=L,
            width_m=part['width_m'],height_m=part['height_m'],wall_m=part['wall_m'],nominal_gross_volume_m3=part['volume_m3'],
            end_mitre_or_clevis_geometry=None,kerf_m=None,purchased_bar_length_m=None,cutting_yield=None)
    raise ValueError('Unsupported actual manufacturing stock primitive')


def _task(bundle_id,body_id,occurrence,kind,question,required):
    r=dict(bundle_id=bundle_id,body_candidate_id=body_id,component_occurrence_id=occurrence,kind=kind,question=question,
        required_artifacts=required,execution='planned',state='unknown',maximum_runtime_s=600,maximum_native_jobs=2,**FLAGS)
    r['task_id']=identity(r);return r


def _composition(candidate,substitutions,extra):
    accounts={r['id']:r for r in candidate['retained_equipment_accounts']};components={c['occurrence_id']:c for c in candidate['components']}
    if not isinstance(substitutions,(list,tuple)) or not isinstance(extra,(list,tuple)):raise ValueError('Explicit architecture substitution and unweighed-equipment sequences required')
    normalized=[];removed=set();obligations=[]
    for row in substitutions:
        allowed={'remove_account_id','replacement','replacement_installed_mass_kg','original_component_definition_id','remove_component_definition_id'}
        if not isinstance(row,dict) or set(row)-allowed:raise ValueError('Explicit supported account substitution fields required')
        name=row.get('remove_account_id');replacement=row.get('replacement')
        if name not in accounts or name in removed:raise ValueError('Remove an existing unique retained account, not body stock or an absent item')
        account=accounts[name];definition=account['component_definition_id']
        if components.get(name,{}).get('component_definition_id')!=definition:raise ValueError('Removed account does not match the body component definition')
        for key in ('original_component_definition_id','remove_component_definition_id'):
            if key in row and row[key]!=definition:raise ValueError('Original substituted component definition differs')
        if not isinstance(replacement,str) or not replacement:raise ValueError('Named replacement equipment/function requirement required')
        if row.get('replacement_installed_mass_kg') is not None:raise ValueError('Replacement mass requires counted/evidenced geometry; this unresolved substitution must remain unknown')
        removed.add(name);normalized.append(dict(remove_account_id=name,original_component_definition_id=definition,
            removed_accounted_mass_kg=account.get('mass_kg'),replacement=replacement,replacement_installed_mass_kg=None,
            replacement_occurrence_id='architecture/replacement/'+name))
    for i,row in enumerate(extra):
        if isinstance(row,str):description=row;name='architecture/unweighed/'+str(i)
        elif isinstance(row,dict) and not set(row)-{'id','description'}:description=row.get('description');name=row.get('id','architecture/unweighed/'+str(i))
        else:raise ValueError('Named unweighed equipment task or explicit id/description required')
        if not isinstance(name,str) or not name or not isinstance(description,str) or not description:raise ValueError('Explicit unweighed equipment task description required')
        if name in accounts or name in components or name in {r['replacement_occurrence_id'] for r in normalized} or name in {r['id'] for r in obligations}:raise ValueError('Architecture requirement occurrence collides with an existing component')
        obligations.append(dict(id=name,description=description,installed_mass_kg=None,physical_occurrence_count=None,
            may_overlap_other_equipment_obligations=True))
    return normalized,removed,obligations


def evaluate(candidate,*,bundle_id,source_root=ROOT,geometry_record=None,dfma_record=None,supply_evidence=(),comparison_context=None,
             component_substitutions=(),extra_equipment_tasks=()):
    """Compile same-body records under the coordinator's canonical bundle ID.

    ``bundle_id`` is supplied, not inferred from a body or selected by this
    adapter. Optional projections must reproduce the exact generated body.
    Retained equipment accounts come from the candidate's pinned reference.
    ``comparison_context`` adds the coordinator's common route/service context;
    changing it prevents cross-context Pareto dominance.
    Explicit substitutions remove only identified retained accounts; unknown
    replacements and additions become unlocated requirements, never zero mass.
    """
    candidate=deepcopy(grammar.validate(candidate))
    if not _sha(bundle_id):raise ValueError('Explicit canonical bundle ID required')
    if 'bundle_id' in candidate and candidate['bundle_id']!=bundle_id:raise ValueError('Mixed canonical bundle and body candidate')
    substitutions,removed,architecture_obligations=_composition(candidate,component_substitutions,extra_equipment_tasks)
    body_id=candidate['candidate_id'];actual_geometry=geometry.mass_properties(candidate)
    if geometry_record is not None and geometry_record!=actual_geometry:raise ValueError('Mass/CG/inertia projection uses different body geometry')
    if dfma_record is None:dfma_record=dfma.evaluate(candidate,root=source_root)
    else:
        dfma_record=deepcopy(dfma_record)
        if dfma_record.get('candidate_id')!=body_id or dfma_record.get('input_graph_id')!=identity(candidate) or dfma_record.get('evaluation_id')!=identity({n:v for n,v in dfma_record.items() if n!='evaluation_id'}):raise ValueError('Manufacturing projection uses different body/source graph')
        if dfma_record!=dfma.evaluate(candidate,dfma_record.get('material_assignments'),root=source_root):raise ValueError('Manufacturing projection cannot be reproduced from this body')
    components={r['occurrence_id']:r for r in candidate['components']};rows={};tasks=[];groups={};materials=candidate['materials']
    database=material_database.catalogue();database_rows={r['id']:r for r in database['records']}
    aliases={'pet_core_reference':'core.pet_t92_80','aluminium_core_reference':'core.al_5052_criii_31','aluminium_reference':'joining.welded-al-extrusion-node'}
    for part in candidate['parts']:
        name=part['id'];component=components.get(name)
        if component is None or not _sha(component.get('component_definition_id')):raise ValueError('Located stock lacks its component definition identity')
        lo,hi=geometry.bounds(part);mat=materials[part['material_id']];source_record=database_rows.get(aliases.get(part['material_id']))
        row=dict(id=name,bundle_id=bundle_id,body_candidate_id=body_id,component_definition_id=component['component_definition_id'],
            scope='located-nominal-gross-body-stock',quantity=1,unit='piece',accounted_mass_kg=part['mass_kg'],
            material_id=part['material_id'],material_basis=mat['source_basis'],material_form=part['form'],
            geometry=dict(kind=part['kind'],frame_id='vehicle',unit='m',definition=deepcopy(part),bounds_min_m=lo,bounds_max_m=hi),
            material_supply=dict(source_record_id=None if source_record is None else source_record['record_id'],
                database_record=None if source_record is None else source_record['id'],supplier_selected=False,lot_id=None,
                actual_stock_availability=None,grade_allowables=None,source_density_not_complete_material_law=True),
            functions=part.get('functions',[]),load_roles=part.get('load_roles',[]),installed_geometry_qualified=False,
            source_reference=candidate['sources'],price_USD=None,lead_time_days=None)
        rows[name]=row;group=part.get('manufacturing_occurrence_id') or 'unresolved/'+name;groups.setdefault(group,[]).append(part)
    for material in sorted({p['material_id'] for p in candidate['parts']}):
        ids=[p['id'] for p in candidate['parts'] if p['material_id']==material]
        task=_task(bundle_id,body_id,ids[0],'material-and-supply-characterization',
            'Resolve the declared '+material+' material/form assumption for these actual stock occurrences',
            ['Selected supplier/grade/form or laminate schedule with lot and source identities','Direction-dependent, temperature and moisture properties appropriate to the actual material',
             'Strength, fatigue, joint/HAZ and environmental design allowables','Fire/smoke, repair and manufacturing-process compatibility','Density and price/availability evidence for the actual purchased stock'])
        task['affected_stock_ids']=ids;task.pop('task_id');task['task_id']=identity(task);tasks.append(task)
    retained=[]
    for account in candidate['retained_equipment_accounts']:
        name=account['id'];component=components.get(name)
        if name in removed:continue
        if name in rows or component is None or component.get('component_definition_id')!=account['component_definition_id']:raise ValueError('Retained source account overlaps or has a mismatched component definition')
        m=account.get('mass_kg')
        if m is not None and (not _finite(m) or m<0):raise ValueError('Finite retained account or explicit unknown required')
        row=dict(id=name,bundle_id=bundle_id,body_candidate_id=body_id,component_definition_id=account['component_definition_id'],
            scope='retained-unlocated-reference-account',quantity=1,unit='account',accounted_mass_kg=m,system=account['system'],
            geometry=None,frame_id=None,installed_CG_m=None,installed_inertia_kg_m2=None,
            functions=component.get('functions',[]),account_basis=account['basis'],
            retained_reference_candidate_id=candidate['retained_reference_candidate_id'],source_reference=candidate['sources'],
            price_USD=None,lead_time_days=None)
        rows[name]=row;retained.append(row)
        tasks.append(_task(bundle_id,body_id,name,'installed-equipment-design',
            'Resolve this retained '+account['system']+' account into actual installed occurrences and interfaces for this body',
            ['Selected component drawings and complete hardware/BOM','Measured or supplier mass, local CG and inertia','Body-frame positions and swept/service/removal envelope',
             'Mount/load/electrical/cooling/drainage interfaces as applicable','Assembly sequence, inspection, source price and procurement lead time']))
    for join in candidate['joins']:
        name=join['id'];component=components.get(name)
        if name in rows or component is None:raise ValueError('Joint occurrence graph is inconsistent')
        rows[name]=dict(id=name,bundle_id=bundle_id,body_candidate_id=body_id,component_definition_id=component['component_definition_id'],
            scope='unknown-installed-joint',quantity=1,unit='joint-assembly',accounted_mass_kg=None,geometry=None,
            joining_hypothesis=join['method'],connected_stock_ids=join['part_ids'],price_USD=None,lead_time_days=None,
            stiffness_strength_fatigue='unknown',frame_id=None,actual_hardware_and_joint_end_cuts=None)
        tasks.append(_task(bundle_id,body_id,name,'joint-realization',
            'Replace the '+join['method']+' idealization with counted and validated joining hardware/end geometry at these exact member interfaces',
            ['Pin/clevis/bolt/bond/insert geometry and net stock cuts','Actual six-axis stiffness, strength, fatigue and degraded load path',
             'Fasteners, preload/retention, corrosion isolation and inspection','Installed joint mass, assembly/removal clearance and repair method']))
    architecture_ids=[]
    for row in substitutions:
        name=row['replacement_occurrence_id']
        if name in rows:raise ValueError('Replacement requirement collides with selected physical stock')
        requirement_id=identity(dict(bundle_id=bundle_id,body_candidate_id=body_id,substitution=row))
        rows[name]=dict(id=name,bundle_id=bundle_id,body_candidate_id=body_id,component_definition_id=None,
            requirement_id=requirement_id,scope='unlocated-architecture-replacement-requirement',quantity=None,unit='equipment-requirement',
            accounted_mass_kg=None,geometry=None,installed_CG_m=None,installed_inertia_kg_m2=None,
            replaces_account_id=row['remove_account_id'],source_component_definition_id=row['original_component_definition_id'],
            replacement_function=row['replacement'],price_USD=None,lead_time_days=None)
        architecture_ids.append(name)
        tasks.append(_task(bundle_id,body_id,name,'architecture-replacement-design',
            'Generate and count the actual '+row['replacement']+' assembly, replacing only the recorded '+row['remove_account_id']+' account',
            ['Physical component/occurrence definitions and actual hardware inventory','Geometry, installed locations, mount/axle/electrical/cooling interfaces and clearance',
             'Derived or measured installed mass, CG and inertia','Protection, thermal/braking/recovery duty and failure cases','Manufacturing, supplier, assembly/repair access and source price/lead time']))
    for obligation in architecture_obligations:
        name=obligation['id'];requirement_id=identity(dict(bundle_id=bundle_id,body_candidate_id=body_id,obligation=obligation))
        rows[name]=dict(id=name,bundle_id=bundle_id,body_candidate_id=body_id,component_definition_id=None,
            requirement_id=requirement_id,scope='unlocated-architecture-equipment-obligation',quantity=None,unit='equipment-requirement',
            description=obligation['description'],accounted_mass_kg=None,geometry=None,installed_CG_m=None,installed_inertia_kg_m2=None,
            physical_occurrence_count=None,may_overlap_other_equipment_obligations=True,price_USD=None,lead_time_days=None)
        architecture_ids.append(name)
        tasks.append(_task(bundle_id,body_id,name,'architecture-equipment-design',obligation['description'],
            ['Resolve this obligation into non-overlapping physical component/occurrence definitions','Count actual stock, fasteners, cables, converters, energy supply and protection as applicable',
             'Locate and weigh installed assemblies with CG/inertia and maintenance clearance','Validate interfaces and fault duty; provide supplier/process/QA/price/lead-time evidence']))
    supply=_supply(rows,supply_evidence,bundle_id,source_root)
    for name,row in rows.items():row['supply_evidence']=supply.get(name)
    mbom=[]
    for group,parts in sorted(groups.items()):
        ids=[p['id'] for p in parts];processes=sorted({p['process'] for p in parts});occurrences=[o for o in dfma_record['operations'] if o['kind']=='fabrication' and o['manufacturing_occurrence_id']==group]
        mbom.append(dict(id=group,bundle_id=bundle_id,body_candidate_id=body_id,engineering_stock_ids=ids,
            material_ids=sorted({p['material_id'] for p in parts}),nominal_cuts_and_blanks=[dict(stock_id=p['id'],**_blank(p)) for p in parts],
            known_gross_stock_mass_kg=sum(p['mass_kg'] for p in parts),process_candidates=processes,
            operation_ids=[o['id'] for o in occurrences],labor_h=None if len(occurrences)!=1 else occurrences[0]['labor_h'],
            tooling=None,supplier_selected=False,process_qualification=None,QA_plan=None,assembly_access=None,repair_removal_path=None,
            net_joint_cut_mass_kg=None,purchased_quantity_and_yield=None,complete_fabricated_mass_kg=None))
        tasks.append(_task(bundle_id,body_id,group,'manufacturing-definition',
            'Complete the '+', '.join(processes)+' route for these actual gross stock occurrences',
            ['Purchased stock/form/grade and cut/nesting yield','End mitres, inserts, bonds, cure and process tolerances as applicable',
             'Tooling/jigs, fabrication and assembly access','Source-bound cycle/labor time, inspection and replaceability','Supplier quote, stock availability, lead time and local capability']))
    gross=actual_geometry['known_gross_stock_mass_kg'];retained_mass=sum(r['accounted_mass_kg'] for r in retained if r['accounted_mass_kg'] is not None)
    accounted=gross+retained_mass;unknown_accounts=[r['id'] for r in retained if r['accounted_mass_kg'] is None]
    unknown_empty_mass=bool(unknown_accounts or architecture_ids)
    # This quantity is not a certified lower bound: nominal stock includes
    # unresolved cuts/overlaps while other installed mass is still missing.
    quantities={
      'known_gross_structure_stock_kg':_quantity(gross,'kg','nominal-body-cut-stock/1','Exact generated gross-stock aggregate at declared research densities'),
      'retained_accounted_equipment_kg':_quantity(retained_mass,'kg','retained-unlocated-account-subtotal/1','Pinned source allocations; actual hardware/placement unqualified'),
      'known_accounted_mass_subtotal_kg':_quantity(accounted,'kg','gross-stock-plus-kept-known-accounts/1','Known arithmetic subtotal; unknown replacement/additional equipment is not zero or a certified lower bound'),
      'accounted_empty_mass_kg':_quantity(None if unknown_empty_mass else accounted,'kg','gross-stock-plus-retained-accounts/1','Arithmetic sensitivity account only; unresolved replacement/additional equipment prevents even this account from closing'),
      'manufacturing_occurrences':_quantity(dfma_record['resolved_manufactured_component_count'],'count','declared-body-manufacturing-occurrences/1','Explicit manufacturing group count, excluding unlocated equipment and unknown joints'),
      'assembly_interfaces':_quantity(dfma_record['assembly_interfaces'],'count','declared-body-join-interfaces/1','Declared join graph only, not complete installed fasteners/operations'),
      'installed_CAPEX_USD':_quantity(None,'USD','complete-same-service-installed-CAPEX/1','Quotes and installed economic coverage incomplete')}
    scope=dict(requirement_revision=candidate['requirement_revision'],formation_and_envelope=candidate['physical']['architecture'],
        retained_account_definitions=[{k:r[k] for k in ('id','component_definition_id','accounted_mass_kg')} for r in retained],
        component_substitutions=deepcopy(substitutions),unweighed_architecture_obligations=deepcopy(architecture_obligations),
        supplied_common_context=deepcopy(comparison_context),quantity_purpose='partial-research-quantity-comparison')
    result=dict(schema='osr-canonical-system-inventory/1',candidate_id=bundle_id,bundle_id=bundle_id,body_candidate_id=body_id,
        body_definition_id=candidate['definition_id'],requirement_revision=candidate['requirement_revision'],comparison_scope=scope,comparison_scope_id=identity(scope),
        engineering_BOM=list(rows.values()),manufacturing_BOM=mbom,known_gross_stock_mass_properties=actual_geometry,
        material_reference_catalogue=dict(database_id=database['database_id'],
            records=[deepcopy(database_rows[name]) for name in sorted({r['material_supply']['database_record'] for r in rows.values() if r.get('material_supply',{}).get('database_record')})],
            sources=deepcopy(database['sources']),scope='Reference lookup only; these records are not automatically selected grades, complete material laws or installed sourcing'),
        known_accounted_mass_subtotal_kg=accounted,accounted_empty_mass_kg=None if unknown_empty_mass else accounted,
        component_substitutions=substitutions,unweighed_architecture_equipment=architecture_obligations,
        account_ledger=dict(original_retained_known_mass_kg=sum(r['mass_kg'] for r in candidate['retained_equipment_accounts'] if r.get('mass_kg') is not None),
            removed_reference_accounts=[deepcopy(r) for r in candidate['retained_equipment_accounts'] if r['id'] in removed],
            removed_known_mass_kg=sum(r['mass_kg'] for r in candidate['retained_equipment_accounts'] if r['id'] in removed and r.get('mass_kg') is not None),
            remaining_retained_known_mass_kg=retained_mass,known_gross_body_stock_kg=gross,known_accounted_mass_subtotal_kg=accounted,
            unresolved_architecture_requirement_ids=architecture_ids,complete_installed_mass_kg=None),
        complete_installed_mass_kg=None,complete_installed_CG_m=None,complete_installed_inertia_kg_m2=None,
        geometry_coverage=dict(located_stock_occurrences=len(candidate['parts']),unlocated_retained_account_ids=[r['id'] for r in retained],
            unknown_joint_ids=[j['id'] for j in candidate['joins']],unresolved_mass_account_ids=unknown_accounts,
            unlocated_architecture_requirement_ids=architecture_ids,unweighed_architecture_excluded_from_accounted_fraction=bool(architecture_ids),
            located_fraction_of_accounted_mass=None if unknown_accounts or accounted<=0 else gross/accounted,
            scope='Coverage of current nominal stock+known retained accounts only; omitted installed equipment is not included in this denominator'),
        supply_coverage=dict(quoted_component_count=sum(r['known_quoted_subtotal_USD'] is not None for r in supply.values()),
            components_without_price=[n for n in rows if n not in supply or supply[n]['known_quoted_subtotal_USD'] is None],
            known_quoted_stock_cost_subtotal_USD=sum(r['known_quoted_subtotal_USD'] for r in supply.values() if r['known_quoted_subtotal_USD'] is not None),
            lead_time_known_count=sum(r['record'].get('lead_time_days') is not None for r in supply.values()),
            complete_installed_CAPEX_USD=None,commercial_validity_assessed=False),
        assembly_operation_graph=dfma_record,component_tasks=tasks,quantities=quantities,integrated_suitability='unknown',
        economic_winner=None,qualified_winner=None,selected_reference_changed=False,
        source_sha256={**candidate['sources'],**dfma_record['source_sha256'],
            'engineering/design_search/grammar_geometry.py':digest(geometry.__file__),PRODUCER:digest(__file__),
            'engineering/design_search/system_selection.py':digest(Path(__file__).with_name('system_selection.py'))},**FLAGS)
    result['evaluation_id']=identity(result);return result
