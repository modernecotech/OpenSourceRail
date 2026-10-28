"""Actual catalogue substitutions and conditional equipment constraints.

Product evidence is Class B; the ±10% mass bands and new mounting packages are
Class C hypotheses. No catalogue fact authenticates an installed railway part.
Every returned record is source/evaluation sealed; none grants a release.
"""
from collections import Counter
from copy import deepcopy
from math import isfinite,fsum,exp
from pathlib import Path
import json
from engineering.component_registry import (make_part,make_occurrence,make_registry,
    validate_registry,summary,affected_dependencies,geometry_properties)
from . import ROOT,FLAGS,identity,digest

PRODUCER='engineering/sourced_case/equipment.py'
DATA='engineering/sourced_case/data/equipment-sources.json'
DEFAULT_SELECTIONS={'independent-brake-caliper':'svendborg-bsfi208',
 'HVAC-roof-unit':'spheros-revoe-tropical','auxiliary-battery-with-BMS':'victron-ng256-200',
 'auxiliary-DC-converter':'victron-orion482416'}
ALLOWED={'independent-brake-caliper':{'svendborg-bsfi208','knorr-hsc1p10n'},
 'HVAC-roof-unit':{'spheros-revoe-tropical'},'auxiliary-battery-with-BMS':{'victron-ng256-200'},
 'auxiliary-DC-converter':{'victron-orion482416'}}


def _seal(value):
    value['evaluation_id']=identity(value);return value


def _checked(value):
    if value.get('evaluation_id')!=identity({k:v for k,v in value.items() if k!='evaluation_id'}):
        raise ValueError('Equipment evaluation identity differs')
    if any(value.get(k) is not False for k in FLAGS):raise ValueError('Equipment is unqualified research only')


def catalogue(root=ROOT):
    root=Path(root)
    if digest(root/PRODUCER)!=digest(__file__):raise ValueError('Executing equipment source differs')
    data=json.loads((root/DATA).read_text())
    for p in data['products']:
        p['physical_product_id']=identity({k:p[k] for k in ('key','manufacturer','model','dimensions_m')})
        p['source_record_id']=identity(data['sources'][p['source']])
        p['product_evaluation_id']=identity(p)
    return _seal(dict(data,source_sha256={PRODUCER:digest(root/PRODUCER),DATA:digest(root/DATA)},**FLAGS))


def _validate_catalogue(cat):
    _checked(cat)
    seen=set()
    for p in cat['products']:
        if p['key'] in seen:raise ValueError('Duplicate sourced product')
        seen.add(p['key'])
        expected=identity({k:p[k] for k in ('key','manufacturer','model','dimensions_m')})
        if p['physical_product_id']!=expected:raise ValueError('Product physical identity differs')
        if p['product_evaluation_id']!=identity({k:v for k,v in p.items() if k!='product_evaluation_id'}):raise ValueError('Product property identity differs')
        source=cat['sources'][p['source']]
        if source['source_class']!='B' or source['actual_supplier_quote'] is not False:raise ValueError('Published facts cannot become quoteA')
        if p['source_record_id']!=identity(source):raise ValueError('Product source identity differs')
        if type(p['mass_typical_kg']) not in (int,float) or not isfinite(p['mass_typical_kg']) or p['mass_typical_kg']<=0:raise ValueError('Positive catalogue mass required')


def _part(old,product,cat):
    dims=product['dimensions_m'] or old['geometry']['dimensions_m']
    name='OSR-SOURCED-'+product['key'].upper()
    typical=product['mass_typical_kg']
    return make_part(name,'R1',old['functions'],dict(kind='envelope',dimensions_m=dims,net_volume_m3=None),None,
        dict(calculated_kg=None,lower_bound_kg=.9*typical,upper_bound_kg=1.1*typical,
             evidence_state='bounded-estimate',nominal_catalogue_kg=typical,
             bounds_source_class='C',bounds_basis='Explicit ±10% exploration allowance, not delivered tolerance'),
        dict(method='purchase-configured-module-and-inspect',cycle_hours=None,scrap_fraction=None,
             gross_blank_volume_m3=None,manufacturing_qualified=False),
        assembly=dict(product_configuration_id=product['physical_product_id'],
             mounting_and_supplier_interface='unqualified-sized-hypothesis',
             retained_envelope_is_supplier_drawing=product['dimensions_m'] is not None,
             fasteners_are_separate_counted_parts=True,tolerance_m=None),
        # Do not hash evaluated power/current facts into physical definition.
        electrical_thermal=dict(product_configuration_id=product['physical_product_id'],
             electrical_interface_approval=None,cooling_interface_approval=None),
        evidence=dict(source_id=product['source_record_id'],product_evaluation_id=product['product_evaluation_id'],
             source_class='B',source=cat['sources'][product['source']]['url'],
             installed_geometry_qualified=False,physical_test_ids=[],scope=product['scope']),
        lifecycle=dict(inspection_interval_hours=None,replacement_procedure=None,repairability_review='pending'))


def _supplement(name,function,dims,bounds,role):
    return make_part('OSR-SOURCED-'+name,'H1',[function],dict(kind='envelope',dimensions_m=dims,net_volume_m3=None),None,
        dict(calculated_kg=None,lower_bound_kg=bounds[0],upper_bound_kg=bounds[1],evidence_state='bounded-estimate',
             bounds_source_class='C',bounds_basis='Explicit design allowance, no supplier weight'),
        dict(method='design-purchase-fit-and-inspect',cycle_hours=None,scrap_fraction=None),
        assembly=dict(role=role,interface_status='pending',fasteners_are_separate_counted_parts=True),
        evidence=dict(source_class='C',status='unqualified-installation-allowance',physical_test_ids=[]))


def _mass_properties(registry,car=None):
    parts={p['physical_definition_id']:p for p in registry['parts']};lo=hi=0.;qlo=[0.]*3;qhi=[0.]*3;known=0.
    for o in registry['occurrences']:
        if car and not o['occurrence_id'].startswith(car+'/'):continue
        p=parts[o['part_definition_id']];m=p['mass'];a=m['lower_bound_kg'];b=m['upper_bound_kg']
        if a is None or b is None:return dict(mass_lower_bound_kg=None,mass_upper_bound_kg=None,all_item_CG_bounds_m=None,installed_CG_m=None)
        lo+=a;hi+=b;known+=m['calculated_kg'] or 0.
        d=geometry_properties(p['geometry'])['envelope_dimensions_m'];R=o['transform']
        extent=[sum(abs(R[i][j])*d[j] for j in range(3))/2 for i in range(3)]
        for i in range(3):
            x=R[i][3];choices=[a*(x-extent[i]),a*(x+extent[i]),b*(x-extent[i]),b*(x+extent[i])]
            qlo[i]+=min(choices);qhi[i]+=max(choices)
    return dict(calculated_net_stock_mass_kg=known,mass_lower_bound_kg=lo,mass_upper_bound_kg=hi,
       all_item_CG_bounds_m=[[min(qlo[i]/lo,qlo[i]/hi,qhi[i]/lo,qhi[i]/hi),max(qlo[i]/lo,qlo[i]/hi,qhi[i]/lo,qhi[i]/hi)] for i in range(3)],
       installed_CG_m=None,installed_inertia_about_CG_kg_m2=None,
       scope='Conservative finite-envelope mass/CG hypothesis; not supplier tolerances or weighed installed properties')


def substitute(vehicle,selections=None,root=ROOT,*,catalogue_override=None,hvac_units_per_car=1,battery_parallel_strings=2):
    """Return an actual newly sealed registry, retaining explicit old ancestry.

    Battery substitution counts four upright25.6V modules per car (2s2p),
    with separate BMS/enclosure allowance. Catalogue caliper mass is treated as
    the complete pad-containing assembly for this hypothesis; the old pad-pair
    account is removed one-for-one and the weight boundary remains a test hold.
    """
    if vehicle.get('evaluation_id')!=identity({k:v for k,v in vehicle.items() if k!='evaluation_id'}):raise ValueError('Vehicle identity differs')
    if hvac_units_per_car not in (1,2) or type(hvac_units_per_car) is not int:raise ValueError('One or two HVAC units per car required')
    if battery_parallel_strings not in (2,3,4) or type(battery_parallel_strings) is not int:raise ValueError('Explicit2/3/4 battery parallel strings required')
    old=vehicle['registry'];validate_registry(old)
    if vehicle['candidate_id']!=old['candidate_id']:raise ValueError('Mixed vehicle candidate')
    selections=deepcopy(DEFAULT_SELECTIONS if selections is None else selections)
    if not selections or set(selections)-set(ALLOWED):raise ValueError('Explicit supported equipment substitutions required')
    cat=deepcopy(catalogue_override if catalogue_override is not None else catalogue(root));_validate_catalogue(cat)
    products={p['key']:p for p in cat['products']}
    for target,key in selections.items():
        if key not in ALLOWED[target]:raise ValueError('Product cannot supply requested function')
    target_parts={};lookup={p['physical_definition_id']:p for p in old['parts']}
    for target in selections:
        found=[p for p in old['parts'] if '-'+target.upper()+'-' in p['part_id']]
        if len(found)!=1:raise ValueError('One exact target definition required: '+target)
        target_parts[found[0]['physical_definition_id']]=(target,found[0],_part(found[0],products[selections[target]],cat))
    remove_pads='independent-brake-caliper' in selections
    removed_pad_ids={p['physical_definition_id'] for p in old['parts'] if '-BRAKE-PAD-PAIR-' in p['part_id']} if remove_pads else set()
    # Extra parts are bounded installation research packages, not unweighed zero.
    extras={}
    if remove_pads:extras['bracket']=_supplement('CALIPER-BRACKET-RETENTION','running-gear',[.25,.12,.06],[3.,8.],'caliper bracket/retention allowance; actual holes/loadpath pending')
    if 'auxiliary-battery-with-BMS' in selections:extras['BMS']=_supplement('BMS-ENCLOSURE-BUSBARS','auxiliary-power',[.60,.22,.22],[15.,40.],'external required BMS, contactor, fuse, enclosure, busbar assembly allowance')
    kept=[deepcopy(p) for p in old['parts'] if p['physical_definition_id'] not in target_parts and p['physical_definition_id'] not in removed_pad_ids]
    kept.extend(p[2] for p in target_parts.values());kept.extend(extras.values());occ=[];replacements=[];counts=Counter();seen_hvac=Counter()
    for o in old['occurrences']:
        if o['part_definition_id'] in removed_pad_ids:continue
        target=target_parts.get(o['part_definition_id']);p=lookup[o['part_definition_id']]
        if target is None:
            occ.append(make_occurrence(o['occurrence_id'],p,o['parent_id'],o['transform'],o['scope']));continue
        name,source,p=target
        if name=='HVAC-roof-unit':
            car=o['occurrence_id'].split('/')[0];seen_hvac[car]+=1
            if seen_hvac[car]>hvac_units_per_car:continue
        copies=2*battery_parallel_strings if name=='auxiliary-battery-with-BMS' else 1
        for k in range(copies):
            pose=deepcopy(o['transform'])
            if name=='HVAC-roof-unit' and hvac_units_per_car==1:
                pose[0][3]=17.5*int(o['occurrence_id'].split('/')[0].split('-')[1].split('/')[0])-17.5+8.5
            # Four upright modules occupy .648×.708×.235m with .02m gaps;
            # original serviced bay is1.1×.75×.38m. Terminal/tool access unresolved.
            if copies>1:
                # Upright modules in two longitudinal rows; width grows for3/4p
                # and intentionally triggers original-bay fitment hold.
                columns=4 if battery_parallel_strings==2 else battery_parallel_strings
                row=k//columns;column=k%columns
                if battery_parallel_strings>2:pose[0][3]+=(row-.5)*.668
                pose[1][3]+=(column-(columns-1)/2)*.182
            oid=o['occurrence_id']+'/sourced-'+str(k+1)
            occ.append(make_occurrence(oid,p,o['parent_id'],pose,o['scope']));counts[name]+=1
        replacements.append(dict(old_occurrence_id=o['occurrence_id'],old_part_definition_id=source['physical_definition_id'],
           old_part_revision_id=source['revision_id'],new_part_definition_id=p['physical_definition_id'],new_quantity=copies,
           product_configuration_id=products[selections[name]]['physical_product_id']))
        extra=extras.get('bracket' if name=='independent-brake-caliper' else 'BMS' if copies>1 else '')
        if extra:
            pose=deepcopy(o['transform']);pose[2][3]-=.12
            if copies>1:pose[0][3]-=1.15
            occ.append(make_occurrence(o['occurrence_id']+'/installation-package',extra,o['parent_id'],pose,o['scope']))
    reg=make_registry(old['label']+' primary-catalogue research revision',kept,occ,old['required_functions'],
        parent_candidate_id=old['candidate_id'],assemblies=old['assemblies'],materials=old['materials'])
    revised=deepcopy(vehicle);revised.pop('evaluation_id');revised.update(candidate_id=reg['candidate_id'],registry=reg,summary=summary(reg),
       per_car_mass_properties=_mass_properties(reg,'car-1'),train_mass_properties=_mass_properties(reg),
       per_car_occurrences=len([o for o in occ if o['occurrence_id'].startswith('car-1/')]),
       per_car_part_definitions=len(kept),mass_complete=False,complete_installed_vehicle_mass_kg=None,
       manufacturing_plan=[dict(part_definition_id=p['physical_definition_id'],part_revision_id=p['revision_id'],part_id=p['part_id'],
             process=p['manufacturing'],required_inspections=['source-configuration','dimensional','mass-boundary','retention'],approved_work_instruction=None,qualified_tooling=None) for p in kept])
    revised['source_sha256']={**vehicle.get('source_sha256',{}),**cat['source_sha256']}
    revised['assembly_access']=_access(reg) # Recompute finite paths; all are conditional/unchecked.
    revised['unresolved']=list(vehicle['unresolved'])+[
       'Revised equipment installation/removal swept envelopes, actual bolt/joint patterns and hose/cable service loops',
       'Caliper catalogue weight boundary versus delivered pads, brackets, disc compatibility and emergency release',
       '600V HVAC supply, external BMS/protection/cooling, auxiliary energy and hot-ambient derating']
    revised['sourced_equipment_ancestry']=dict(parent_candidate_id=old['candidate_id'],parent_evaluation_id=vehicle['evaluation_id'],
         catalogue_evaluation_id=cat['evaluation_id'],selections=selections,hvac_units_per_car=hvac_units_per_car,battery_parallel_strings=battery_parallel_strings)
    revised['evaluation_id']=identity(revised)
    value=dict(schema='osr-sourced-equipment-substitution/1',candidate_id=reg['candidate_id'],parent_candidate_id=old['candidate_id'],
      vehicle=revised,catalogue=cat,selections=selections,replacements=replacements,counts=dict(counts),
      architecture=dict(hvac_units_per_car=hvac_units_per_car,battery_series_modules=2,battery_parallel_strings=battery_parallel_strings,
        battery_original_bay_envelope_fit=battery_parallel_strings==2,battery_new_cradle_required=battery_parallel_strings>2,HVAC600V_supply_and_charger_defined=False),
      summary=summary(reg),mass_change_bounds_kg=[summary(reg)['mass_lower_bound_kg']-vehicle['summary']['mass_upper_bound_kg'],
          summary(reg)['mass_upper_bound_kg']-vehicle['summary']['mass_lower_bound_kg']],
      dependency_invalidation=affected_dependencies(old,reg),
      pad_accounting=dict(removed_old_pad_occurrences=sum(o['part_definition_id'] in removed_pad_ids for o in old['occurrences']),
        treatment='Included in replacement caliper assembly hypothesis; delivered supplier bill/mass boundary pending'),
      known_installation_scope=dict(bracket_allowances=sum('/installation-package' in o['occurrence_id'] and 'caliper' in o['occurrence_id'] for o in occ),
        installation_accepted=False,fastener_joint_loads_qualified=False,service_sweeps_qualified=False,
        cooling_and_wiring_flexibility_qualified=False),**FLAGS)
    value['fitment_screens']=_fitment(reg)
    return _seal(value)


def _access(registry):
    parts={p['physical_definition_id']:p for p in registry['parts']};rows=[]
    for o in registry['occurrences']:
        p=parts[o['part_definition_id']]
        if not p['part_id'].startswith('OSR-SOURCED-') or not o['occurrence_id'].startswith('car-1/'):continue
        d=p['geometry']['dimensions_m'];start=deepcopy(o['transform']);end=deepcopy(start)
        roof='SPHEROS' in p['part_id'];end[2 if roof else 1][3]+=1.5 if roof else 2.
        rows.append(dict(moving_occurrence_id=o['occurrence_id'],part_revision_id=p['revision_id'],
          envelope_dimensions_m=[x+.10 for x in d],start_transform=start,end_transform=end,
          frame='registry-metres-centred-local',motion=dict(kind='translation',sample_count=17),
          removal_sequence=['isolate-and-prove-dead-or-restrain-stored-energy','disconnect-labelled-services','support-with-rated-crane-or-module-trolley','remove-retainers','withdraw-along-proposed-path'],
          tool_access_radius_m_hypothesis=.15,minimum_flexible_service_slack_m_hypothesis=.6,
          lifting_capacity_required_kg_lower=p['mass']['upper_bound_kg'],
          supplier_lifting_points_approved=False,continuous_clearance_proved=False,
          retaining_fastener_pattern=None,installation_accepted=False))
    return rows


def friction_case(v_disc,T,convention,*,apply_prose_c=False,root=ROOT):
    """Evaluate the paper's fitted Eq2, never an admitted OSR pad map.

    Available text gives two plotted slices (v_disc9.6m/s and surface50C),
    not an authenticated raw dataset or complete fitted validity domain.
    Numerical evaluation away from these conditions is explicitly extrapolative.
    """
    if convention not in ('paper-Td-temperature-rise','figure-surface-temperature'):
        raise ValueError('Explicit temperature convention required; paper ambiguity is unresolved')
    if type(apply_prose_c) is not bool:raise ValueError('Explicit prose correction choice required')
    for x in (v_disc,T):
        if type(x) not in (float,int) or not isfinite(x) or x<0:raise ValueError('Finite nonnegative formula inputs required')
    cat=catalogue(root)
    mu=.38*(1+.184*exp(-.1*v_disc))*(1+.105*exp(-.014*T))
    return _seal(dict(schema='osr-brake-friction-method-case/1',
       source_record_id=identity(cat['sources']['brake-paper']),
       source_url=cat['sources']['brake-paper']['url'],equation='Eq2',
       disc_tangential_speed_m_s=v_disc,disc_temperature_variable_C=T,temperature_convention=convention,
       fitted_equation_mu=mu,prose_correction_c=.98,prose_correction_applied=apply_prose_c,
       evaluated_mu=mu*(.98 if apply_prose_c else 1.),
       experimental_scope='Korean150km/h wheel-disc HILS; different organic pad/steel disc, wheelD.86m discD.55m',
       published_measurement_slices=dict(friction_speed_m_s=9.6,figure_surface_temperature_C=50.),
       actual_complete_empirical_domain=None,raw_dynamometer_points_available=False,
       extrapolation_beyond_documented_slice=not(v_disc==9.6 or T==50.),
       temperature_ambiguity='Eq2 variable called temperature increase; Fig2 prose surface temperature; unresolved',
       independently_reproduced_raw_measurement_error=None,
       fitted_point_is_raw_test_data=False,can_supply_OSR_operating_brake_map=False,**FLAGS))


def friction_method_probe(root=ROOT):
    value=friction_case(9.6,50.,'paper-Td-temperature-rise',root=root)
    value.pop('evaluation_id');value['explicit_prose_corrected_mu']=.98*value['fitted_equation_mu']
    return _seal(value)


def _fitment(registry):
    parts={p['physical_definition_id']:p for p in registry['parts']};hvac=[];solar=[]
    for o in registry['occurrences']:
        p=parts[o['part_definition_id']]
        if 'SPHEROS-REVOE' in p['part_id']:hvac.append((o,p))
        if '-FLUSH-SOLAR-MODULE-' in p['part_id']:solar.append((o,p))
    hits=[]
    for o,p in hvac:
        for other,q in solar:
            d=p['geometry']['dimensions_m'];e=q['geometry']['dimensions_m']
            if all(abs(o['transform'][i][3]-other['transform'][i][3])<(d[i]+e[i])/2 for i in range(3)):
                hits.append(dict(equipment_occurrence=o['occurrence_id'],obstacle_occurrence=other['occurrence_id']))
    return dict(roof_equipment_solar_AABB_intersections=hits,continuous_sweeps_qualified=False,
         final_position_geometry_is_acceptance=False,supplier_attachment_and_fastener_pattern=None)


def constraints(substitution,speed_m_s=20.,ambient_C=50.,adhesion=.08,disc_specific_heat_J_kgK=None):
    """Necessary conditional constraints, never admitted brake/operating maps."""
    _checked(substitution);v=substitution['vehicle'];validate_registry(v['registry'])
    if v['candidate_id']!=substitution['candidate_id']:raise ValueError('Mixed equipment candidate')
    if v['evaluation_id']!=identity({k:x for k,x in v.items() if k!='evaluation_id'}):raise ValueError('Equipment vehicle evaluation differs')
    for x in (speed_m_s,ambient_C,adhesion):
        if type(x) not in (int,float) or not isfinite(x):raise ValueError('Finite equipment conditions required')
    if speed_m_s<0 or not 0<=adhesion<=1:raise ValueError('Speed/adhesion outside physical domain')
    products={p['key']:p for p in substitution['catalogue']['products']};sels=substitution['selections'];cars=v['requirements']['cars']
    n=substitution['counts'];brake={};electric={};hvac={};holds=[]
    if 'independent-brake-caliper' in sels:
        key=sels['independent-brake-caliper'];p=products[key];f=p['facts'];count=n['independent-brake-caliper']
        # Existing source geometry, not a guessed disc diameter/count.
        discs=[part for part in v['registry']['parts'] if '-FRICTION-BRAKE-DISC-' in part['part_id']]
        disc=discs[0] if len(discs)==1 else None
        diameter=2*disc['geometry']['dimensions_m']['outer_radius'] if disc else None
        torque=(f['clamp_min_N']*2*f['nominal_mu']*(diameter-.07)/2) if key=='svendborg-bsfi208' and diameter and diameter>.07 else None
        # wheel0.32m is explicit source geometry, validated here.
        wheels=[p for p in v['registry']['parts'] if '-WHEEL-RIM-' in p['part_id']]
        radius=wheels[0]['geometry']['dimensions_m']['outer_radius'] if len(wheels)==1 else None
        raw=None if torque is None or radius is None else torque*count/radius
        normal_mass=v['train_mass_properties']['mass_upper_bound_kg']+cars*46*75
        adhesive=normal_mass*9.80665*adhesion
        kinetic=.5*normal_mass*speed_m_s**2
        disc_mass=None if disc is None else disc['mass']['calculated_kg']*count
        delta=None
        if disc_specific_heat_J_kgK is not None:
            if type(disc_specific_heat_J_kgK) not in (float,int) or not isfinite(disc_specific_heat_J_kgK) or disc_specific_heat_J_kgK<=0:raise ValueError('Positive sourced/explicit heat capacity required')
            delta=kinetic/(disc_mass*disc_specific_heat_J_kgK) if disc_mass else None
        brake=dict(calipers=count,disc_diameter_m=diameter,nominal_mu=f.get('nominal_mu'),nominal_torque_per_disc_Nm=torque,
          nominal_train_force_before_adhesion_N=raw,assumed_wheel_rail_adhesion=adhesion,
          adhesion_upper_N=adhesive,conditional_force_upper_N=None if raw is None else min(raw,adhesive),
          normal_load_upper_mass_kg=normal_mass,normal_load_stop_kinetic_energy_J=kinetic,
          counted_disc_mass_kg=disc_mass,adiabatic_all_energy_to_disc_rise_K=delta,
          brake_heat_capacity_J_kgK=disc_specific_heat_J_kgK,heat_partition_unknown=True,
          aggregate_arrival_stream_brake_heat_W_at120s_headway=kinetic/120.,
          each_train_brake_repetition_period_s=None,rotational_and_gradient_energy_J=None,hot_wet_mu_map=None,
          response_s_guide=f.get('guide_response_s'),operating_map_admitted=False)
        holds+=['Disc/pad grade-specific μ(T,v,pressure,wear,wet), fade and repeated120s dynamometer tests',
           'Exact caliper force interpretation, disc clearance/strength, hydraulic delay/release and wheel-slide tests']
    if 'HVAC-roof-unit' in sels:
        f=products[sels['HVAC-roof-unit']]['facts'];per=n['HVAC-roof-unit']/cars
        peak=per*(f['hv_voltage_V']*f['hv_max_current_A']+f['lv_voltage_V']*f['lv_nominal_current_A'])
        hvac=dict(units_per_car=per,per_car_peak_electrical_W=peak,
           per_car_regulated_electrical_W=per*(f['hv_voltage_V']*f['hv_regulated_current_A']+f['lv_voltage_V']*f['lv_nominal_current_A']),
           application_ambient_in_published_range=ambient_C<=f['application_max_ambient_C'],
           cooling_available_at_selected_ambient_W=None,cooling_capacity_unit_conflict=True,
           requires_HV_supply_V=f['hv_voltage_V'],capacity_at55C_proven=False)
        holds+=['Resolve USA cooling table unit conflict with manufacturer drawing; measure cooling/cabin load at50/55C',
           '600V compressor supply/converter absent; new roof envelopes conflict-check with solar/structure and removal crane']
    if 'auxiliary-battery-with-BMS' in sels:
        f=products[sels['auxiliary-battery-with-BMS']]['facts'];series=2;parallel=substitution['architecture']['battery_parallel_strings']
        available=series*f['end_voltage_V']*parallel*f['continuous_discharge_A']
        electric=dict(series_modules=series,parallel_strings=parallel,modules_per_car=series*parallel,
          nominal_per_car_energy_Wh=series*parallel*f['nominal_energy_Wh'],nominal_pack_voltage_V=series*f['nominal_voltage_V'],
          end_pack_voltage_V=series*f['end_voltage_V'],continuous_current_A=parallel*f['continuous_discharge_A'],
          continuous_at_end_voltage_W=available,continuous_at_nominal_voltage_W=series*f['nominal_voltage_V']*parallel*f['continuous_discharge_A'],
          energy_condition_C=f['capacity_condition_C'],pack_power_rating_at_selected_ambient_W=None,
          discharge_temperature_in_range=f['discharge_range_C'][0]<=ambient_C<=f['discharge_range_C'][1],
          charging_temperature_in_range=f['charge_range_C'][0]<=ambient_C<=f['charge_range_C'][1],
          external_BMS_and_protection_qualified=False,
          peak_HVAC_only_deficit_W=max(0.,hvac['per_car_peak_electrical_W']-available) if hvac else None)
        holds+=['Pack<BMS/fuses/contactors> fault energy, hot climate cooling/charge, isolation and emergency-service autonomy tests']
    if 'auxiliary-DC-converter' in sels:
        f=products[sels['auxiliary-DC-converter']]['facts'];derate=max(0.,1-f['derate_fraction_per_C_above40']*max(0.,ambient_C-40))
        capacity=f['continuous_power_at40C_W']*derate if f['ambient_range_C'][0]<=ambient_C<=f['ambient_range_C'][1] else None
        electric['LV_converter_per_car_capacity_W']=capacity
        electric['LV_converter_output_V']=f['output_voltage_V'];electric['HVAC600V_converter_available']=False
        electric['nominal26V_HVAC_fan_power_per_car_W']=None if not hvac else hvac['units_per_car']*26*70
        electric['LV_fan_only_deficit_W']=None if not hvac or capacity is None else max(0.,hvac['units_per_car']*26*70-capacity)
        electric['fan_voltage_compatibility_qualified']=False
        electric['converter_output_loss_W']=None if capacity is None else capacity*(1/f['efficiency']-1)
        holds+=['Essential24V load/current/routing/protection and converter derating; additional600V converter thermal/electrical design']
    return _seal(dict(schema='osr-sourced-equipment-constraints/1',candidate_id=substitution['candidate_id'],
       substitution_evaluation_id=substitution['evaluation_id'],conditions=dict(speed_m_s=speed_m_s,ambient_C=ambient_C,adhesion=adhesion),
       brake=brake,HVAC=hvac,electrical=electric,required_tests=holds,
       complete_installed_mass_kg=None,complete_installed_price=None,source_class='B/C-conditional',**FLAGS))
