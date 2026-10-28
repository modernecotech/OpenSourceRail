"""Located2s auxiliary-power revision; no installed fitment/ratings acceptance."""
from copy import deepcopy
from pathlib import Path
from math import pi
from engineering.component_registry import make_part,make_occurrence,make_registry,summary,affected_dependencies
from . import ROOT,FLAGS,identity,digest
from . import equipment,commerce

PRODUCER='engineering/sourced_case/power_revision.py'
CURRENT_EPC_SOURCE=dict(url='https://epicpower.es/product/epc-5k5-648i/',sha256='0f8e5ce690c0aa10f3a39d7d32e1cd7acbde54d98d4dbfbd82f38416da74f2de',bytes=167391,retrieved_date='2026-10-28',published_mass_kg=12.95,source_class='B',actual_quote=False)


def _vehicle(v,reg,root):
    r=deepcopy(v);r.pop('evaluation_id',None);r.update(candidate_id=reg['candidate_id'],registry=reg,summary=summary(reg),
      per_car_mass_properties=equipment._mass_properties(reg,'car-1'),train_mass_properties=equipment._mass_properties(reg),
      per_car_occurrences=sum(o['occurrence_id'].startswith('car-1/') for o in reg['occurrences']),per_car_part_definitions=len(reg['parts']),
      mass_complete=False,complete_installed_vehicle_mass_kg=None)
    r['source_sha256']={**v.get('source_sha256',{}),PRODUCER:digest(Path(root)/PRODUCER),**commerce.catalogue(root)['source_sha256']}
    parts={p['physical_definition_id']:p for p in reg['parts']}
    r['per_car_functional_occurrences']={f:sum(f in parts[o['part_definition_id']]['functions'] for o in reg['occurrences'] if o['occurrence_id'].startswith('car-1/')) for f in r['functional_requirements']}
    r['manufacturing_plan']=[dict(part_id=p['part_id'],part_definition_id=p['physical_definition_id'],part_revision_id=p['revision_id'],process=p['manufacturing'],required_inspections=['dimensions','mass-boundary','retention','electrical-protection'],approved_work_instruction=None,qualified_tooling=None) for p in reg['parts']]
    envelope_ids={p['physical_definition_id'] for p in reg['parts'] if p['geometry']['kind']=='envelope'}
    r['assembly_access']=equipment._access(dict(parts=reg['parts'],occurrences=[o for o in reg['occurrences'] if o['part_definition_id'] in envelope_ids]))
    r['unresolved']=list(v['unresolved'])+['Revised2s multi-string underfloor battery/auxiliary enclosure routing, cooling, stock load paths and all continuous installation/removal clearances']
    r['evaluation_id']=identity(r);return r


def _equipment(e,v,parallel_strings):
    r=deepcopy(e);r.pop('evaluation_id',None);r.update(candidate_id=v['candidate_id'],vehicle=v,summary=v['summary'])
    r['architecture'].update(battery_series_modules=2,battery_parallel_strings=parallel_strings,battery_original_bay_envelope_fit=False,battery_new_cradle_required=True)
    r['counts']['auxiliary-battery-with-BMS']=2*parallel_strings*v['requirements']['cars']
    r['counts']['auxiliary-DC-converter']=sum('Orion-' in o['occurrence_id'] for o in v['registry']['occurrences']) or v['requirements']['cars']
    r['power_revision_ancestry']=dict(parent_candidate_id=e['candidate_id'],parent_evaluation_id=e['evaluation_id'])
    r['evaluation_id']=identity(r);return r


def revise(equipment_result,*,parallel_strings=8,converter_units=3,lv_parallel_units=9,root=ROOT):
    """Generate actual battery/cradle/cable/BMS/converter placements and masses.

    Catalogue bill quantities and ClassC installation hypotheses remain distinct.
    Returns the existing equipment-result shape with a newly sealed vehicle.
    """
    root=Path(root)
    if digest(root/PRODUCER)!=digest(__file__):raise ValueError('Executing power-revision source differs')
    commerce._check_equipment(equipment_result)
    if type(parallel_strings) is not int or not 2<=parallel_strings<=25:raise ValueError('NG requires2s and at most25parallel strings')
    v=equipment_result['vehicle'];old=v['registry'];cars=v['requirements']['cars'];sourceparts={p['physical_definition_id']:p for p in old['parts']}
    batteries=[p for p in old['parts'] if p['part_id']=='OSR-SOURCED-VICTRON-NG256-200']
    if len(batteries)!=1:raise ValueError('Exact sourced NG25.6V200Ah module required')
    battery=batteries[0]
    remove={p['physical_definition_id'] for p in old['parts'] if p is battery or p['part_id']=='OSR-SOURCED-BMS-ENCLOSURE-BUSBARS' or any(x in p['part_id'] for x in ('-BATTERY-SLIDE-RAIL-','-BATTERY-STOP-LOCK-AND-RESTRAINT-','-BATTERY-CRADLE-ANCHOR-'))}
    retained=[p for p in old['parts'] if p['physical_definition_id'] not in remove];parts=deepcopy(retained);parts.append(deepcopy(battery))
    occurrences=[deepcopy(o) for o in old['occurrences'] if o['part_definition_id'] not in remove]
    materials={m['grade_id']:m for m in old['materials']}
    def purchased(name,dims,bounds,role):
        p=make_part('OSR-SOURCED-POWER-'+name,'H1',['auxiliary-power'],dict(kind='envelope',dimensions_m=dims,net_volume_m3=None),None,
          dict(calculated_kg=None,lower_bound_kg=bounds[0],upper_bound_kg=bounds[1],evidence_state='bounded-estimate',bounds_source_class='C',bounds_basis=role),
          dict(method='configure-fabricate-procure-inspect-install',cycle_hours=None,scrap_fraction=None),
          assembly=dict(role=role,installation_accepted=False,fasteners_are_separate_counted_parts=True),
          evidence=dict(source_class='C',physical_test_ids=[],status='bounded-installation-hypothesis'))
        parts.append(p);return p
    def stock(name,grade,kind,dims):
        m=materials[grade];vol=(dims[0]*dims[1]*dims[2] if kind=='box' else pi*dims['radius']**2*dims['length'])
        p=make_part('OSR-SOURCED-POWER-'+name,'H1',['auxiliary-power'],dict(kind=kind,dimensions_m=dims,net_volume_m3=vol),m['material_id'],
          dict(calculated_kg=vol*m['density_kg_m3']['nominal'],lower_bound_kg=vol*m['density_kg_m3']['lower'],upper_bound_kg=vol*m['density_kg_m3']['upper'],evidence_state='calculated'),
          dict(method='cut-machine-form-inspect',scrap_fraction=.15,cycle_hours=None),
          assembly=dict(retention_load_and_torque_approved=False,thread_or_cut_detail='pending'),material_evaluation_id=m['material_evaluation_id'])
        parts.append(p);return p
    # BMS exact configuration from primary2026Q2 manufacturer price/specification.
    cat=commerce.catalogue(root);BMSprice=next(x for x in cat['prices'] if x['SKU']=='LYN034170310')
    BMS=make_part('OSR-SOURCED-LYNX1000-NG-LYN034170310','R1',['auxiliary-power'],dict(kind='envelope',dimensions_m=[.186,.080,.170],net_volume_m3=None),None,
       dict(calculated_kg=None,lower_bound_kg=2.25,upper_bound_kg=2.75,evidence_state='bounded-estimate',catalogue_mass_kg=2.5,bounds_source_class='C'),
       dict(method='purchase-configured-BMS-and-inspect',cycle_hours=None,scrap_fraction=None),
       assembly=dict(product_model='LynxSmartBMS1000NG M10',rating_A=1000,installation_accepted=False),
       evidence=dict(source_class='B',source_record_id=identity(cat['sources']['usd-pricelist']),price_record_id=identity(BMSprice),physical_test_ids=[]))
    parts.append(BMS)
    housing=purchased('CONDITIONED-HOUSING',[1.0,.28,.65],[10.,30.],'Conditioned EPC enclosure/duct/support hypothesis; delivered heat transfer/weight pending')
    protection=purchased('BRANCH-PROTECTION-CONTACTORS',[.65,.20,.20],[12.,25.],'String fuses/disconnect/contactors/control distribution allowance, no rated hardware selection')
    insulation=purchased('INSULATION-TERMINATIONS-FLEX',[1.,.20,.12],[5.,15.],'Insulation/strain relief/connectors/flexible cooling/wiring loops; actual routing pending')
    rail=stock('BATTERY-CRADLE-RAIL','AL-6082-T6-EXTRUSION','box',[.75,.03,.04])
    stop=stock('BATTERY-CRADLE-STOP','AL-6082-T6-EXTRUSION','box',[.03,.22,.06])
    bolt=stock('BATTERY-CRADLE-FASTENER','STEEL-FASTENER-HYPOTHESIS','cylinder',dict(radius=.006,length=.04))
    cable=stock('BATTERY-BRANCH-COPPER','COPPER-CU-ETP-HYPOTHESIS','cylinder',dict(radius=(95e-6/pi)**.5,length=.8))
    trunk=stock('BATTERY-TRUNK-COPPER','COPPER-CU-ETP-HYPOTHESIS','cylinder',dict(radius=(200e-6/pi)**.5,length=2.))
    def put(car,name,p,x,y,z,axis='z'):
        from engineering.reference_cell.vehicles import pose
        o=make_occurrence(f'car-{car+1}/auxiliary-power/power-revision-{name}',p,f'car-{car+1}/auxiliary-power',pose(x+17.5*car,y,z,axis),'vehicle/auxiliary-power')
        occurrences.append(o)
    for car in range(cars):
        for n in range(2*parallel_strings):
            column=n%parallel_strings;side=-1 if n<parallel_strings else 1
            x=4.5+8.1*column/(parallel_strings-1);y=.8*side
            put(car,'battery-'+str(n),battery,x,y,.55)
            for k,dy in enumerate((-.10,.10)):put(car,f'rail-{n}-{k}',rail,x,y+dy,.3975)
            for k,dx in enumerate((-.36,.36)):put(car,f'stop-{n}-{k}',stop,x+dx,y,.44)
            for k in range(12):put(car,f'bolt-{n}-{k}',bolt,x-.29+.193333*(k%4),y-.10+.10*(k//4),.42)
            for k in range(2):put(car,f'branch-{n}-{k}',cable,x,y+(-.19 if k==0 else .19),.73,axis='x')
        put(car,'BMS',BMS,8.55,.30,.78)
        put(car,'housing',housing,7.37,-1.05,.62)
        put(car,'protection',protection,5.9,.30,.78)
        put(car,'flex-insulation',insulation,10.0,.35,.78)
        for k in range(2):put(car,'trunk-'+str(k),trunk,8.5,.30+.06*k,.76,axis='x')
    # Closely packed25p cannot fit this finite17m layout; preserve failure rather
    # than silently overlapping battery modules under the permissive source limit.
    pitch=8.1/(parallel_strings-1)
    fit=pitch>=.648+.02
    used={o['part_definition_id'] for o in occurrences};parts=[p for p in parts if p['physical_definition_id'] in used]
    intermediate=make_registry(old['label']+f'2s{parallel_strings}p auxiliary research revision',parts,occurrences,old['required_functions'],old['candidate_id'],old['assemblies'],old['materials'])
    iv=_vehicle(v,intermediate,root);intake=_equipment(equipment_result,iv,parallel_strings)
    power=commerce.power_case(intake,converter_units,lv_parallel_units,root=root)
    removal=set(power['removed_occurrence_ids']);occurrences=[o for o in intermediate['occurrences'] if o['occurrence_id'] not in removal]
    byid={p['physical_definition_id']:p for p in parts}
    for part in power['parts']:
        p=deepcopy(part)
        if p['part_id']=='OSR-SOURCED-EPC5K5648I':
            mass=dict(p['mass'],lower_bound_kg=.9*8.95,upper_bound_kg=1.1*12.95,
                catalogue_mass_kg=None,published_mass_versions_kg=[8.95,12.95],
                bounds_basis='Historical2024PDF8.95kg versus2026currentESweb12.95kg; delivered variant uncertain, expanded10% exploration band')
            p=make_part(p['part_id'],p['revision'],p['functions'],p['geometry'],None,mass,p['manufacturing'],
                assembly=p['assembly'],electrical_thermal=p['electrical_thermal'],cost=p['cost'],procurement=p['procurement'],
                evidence=dict(p['evidence'],current_source_record_id=identity(CURRENT_EPC_SOURCE),current_source_record=CURRENT_EPC_SOURCE,variant_availability_confirmed=False),lifecycle=p['lifecycle'])
        byid[p['physical_definition_id']]=p
    for o in power['occurrences']:
        occurrences.append(make_occurrence(o['occurrence_id'],byid[o['part_definition_id']],o['parent_id'],o['transform'],o['scope']))
    used={o['part_definition_id'] for o in occurrences}
    final=make_registry(old['label']+f'2s{parallel_strings}p complete auxiliary inventory',
       [p for key,p in byid.items() if key in used],occurrences,old['required_functions'],old['candidate_id'],old['assemblies'],old['materials'])
    fv=_vehicle(v,final,root);result=_equipment(equipment_result,fv,parallel_strings)
    result.pop('evaluation_id')
    result['architecture'].update(battery_parallel_strings=parallel_strings,auxiliary_nominal_voltage_V=51.2,
       BMS_model='LYN034170310',BMS_nominal_current_A=1000,converter_units_per_car=converter_units,LV_parallel_units_per_car=lv_parallel_units)
    result['dependency_invalidation']=affected_dependencies(old,final)
    result['complete_source_power_case']=dict(schema='osr-bound-auxiliary-power-revision/1',candidate_id=final['candidate_id'],
      body_candidate_id=final['candidate_id'],source_derivation_body_candidate_id=intermediate['candidate_id'],
      source_derivation_evaluation_id=power['evaluation_id'],source_derivation=power,
      actual_registry_id=final['registry_id'],battery_series_modules=2,battery_parallel_strings=parallel_strings,
      BMS_nominal_limit_A=1000,source_max_charge_A=parallel_strings*200,manufacturer_recommended_charge_A=parallel_strings*100,
      battery_pitch_m=pitch,battery_longitudinal_spacing_screen='conditional-envelope-fit' if fit else 'fail-module-overlap',
      hardware_counts_per_car=dict(battery_modules=2*parallel_strings,BMS=1,EPC=converter_units,Orion=lv_parallel_units,
       cradle_rails=4*parallel_strings,stops=4*parallel_strings,cradle_fasteners=24*parallel_strings,
       branch_copper_lengths=.8*4*parallel_strings,trunk_copper_length_m=4.),
      housing_protection_flex_source_class='C-explicit-bounds',installed_thermal_acceptance=False,complete_installed_mass_kg=None,
      EPC_mass_source_discrepancy=CURRENT_EPC_SOURCE,
      EPC_selected_mass_bounds_per_module_kg=[.9*8.95,1.1*12.95],
      public_price_links={'battery':'BAT524120620','BMS':'LYN034170310','Orion':'ORI482441110','EPC':None},
      all_final_position_clearances_proved=False,**FLAGS)
    result['complete_source_power_case']['evaluation_id']=identity(result['complete_source_power_case'])
    result['evaluation_id']=identity(result);return result
