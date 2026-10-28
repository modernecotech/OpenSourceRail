"""Source-bound auxiliary bus hardware and partial public-price calculations."""
from copy import deepcopy
from math import isfinite,ceil
from pathlib import Path
import json
from engineering.component_registry import make_part,make_occurrence,validate_registry
from . import ROOT,FLAGS,identity,digest
from .equipment import constraints

PRODUCER='engineering/sourced_case/commerce.py'
DATA='engineering/sourced_case/data/commerce-sources.json'


def _seal(v):v['evaluation_id']=identity(v);return v


def _number(x,name,positive=False):
    if type(x) not in (int,float) or not isfinite(x) or x<0 or positive and x<=0:raise ValueError('Finite '+name+' required')
    return float(x)


def catalogue(root=ROOT):
    root=Path(root)
    if digest(root/PRODUCER)!=digest(__file__):raise ValueError('Executing commerce source differs')
    v=json.loads((root/DATA).read_text())
    for p in v['products']:
        p['physical_product_id']=identity({k:p[k] for k in ('key','manufacturer','model','dimensions_m')})
        p['source_record_id']=identity(v['sources'][p['source']]);p['product_evaluation_id']=identity(p)
    return _seal(dict(v,source_sha256={PRODUCER:digest(root/PRODUCER),DATA:digest(root/DATA)},**FLAGS))


def _check_equipment(v):
    if v.get('evaluation_id')!=identity({k:x for k,x in v.items() if k!='evaluation_id'}):raise ValueError('Equipment identity differs')
    validate_registry(v['vehicle']['registry'])
    if v['candidate_id']!=v['vehicle']['candidate_id']:raise ValueError('Mixed equipment body')


def _module(p):
    return make_part('OSR-SOURCED-'+p['key'].upper(),'R1',['auxiliary-power'],
        dict(kind='envelope',dimensions_m=p['dimensions_m'],net_volume_m3=None),None,
        dict(calculated_kg=None,lower_bound_kg=.9*p['mass_kg'],upper_bound_kg=1.1*p['mass_kg'],
             evidence_state='bounded-estimate',catalogue_mass_kg=p['mass_kg'],bounds_source_class='C',bounds_basis='Explicit10% research allowance, not supplier tolerance'),
        dict(method='purchase-inspect-mount-configured-converter',cycle_hours=None,scrap_fraction=None),
        assembly=dict(product_configuration_id=p['physical_product_id'],mounting_fasteners=4,
            fastener_grade_and_torque_approved=False,air_cooling_clearances_verified=False),
        electrical_thermal=dict(physical_product_id=p['physical_product_id'],converter_bus='48V-to600Vauxiliary'),
        evidence=dict(source_record_id=p['source_record_id'],product_evaluation_id=p['product_evaluation_id'],source_class='B',installed_geometry_qualified=False))


def power_case(equipment,converter_units=3,lv_parallel_units=7,converter_air_C=40.,
               efficiency_bounds=(.90,.98),root=ROOT):
    """Return actual component placements for canonical parent integration.

    Existing one-per-car Orion occurrences are explicitly removed and replaced
    by lv_parallel_units per car. New EPC occurrences are additional hardware.
    Poses use vehicle registry coordinates; mounting/slack/enclosure are held.
    """
    _check_equipment(equipment);cat=catalogue(root);c=constraints(equipment)
    for x in (converter_units,lv_parallel_units):
        if type(x) is not int or not 1<=x<=32:raise ValueError('Bounded integer converter inventory required')
    if type(converter_air_C) not in (float,int) or not isfinite(converter_air_C):raise ValueError('Finite conditioned air temperature required')
    if not isinstance(efficiency_bounds,(list,tuple)) or len(efficiency_bounds)!=2:raise ValueError('Explicit efficiency interval required')
    eta_lo,eta_hi=efficiency_bounds
    if any(type(x) not in (int,float) or not isfinite(x) for x in efficiency_bounds) or not 0<eta_lo<=eta_hi<=.98:raise ValueError('Efficiency cannot exceed source maximum')
    vehicle=equipment['vehicle'];reg=vehicle['registry'];ep=next(p for p in cat['products'] if p['key']=='epc5k5648i');f=ep['facts']
    module=_module(ep);old={p['physical_definition_id']:p for p in reg['parts']}
    orion_parts=[p for p in reg['parts'] if p['part_id']=='OSR-SOURCED-VICTRON-ORION482416']
    if len(orion_parts)!=1 or not c['HVAC'] or not c['electrical']:raise ValueError('SourcedHVAC/battery/Orion equipment required')
    orion=orion_parts[0];removed=[o for o in reg['occurrences'] if o['part_definition_id']==orion['physical_definition_id']]
    cars=vehicle['requirements']['cars']
    if len(removed)!=cars:raise ValueError('Exactly one existing Orion per car required before replacement')
    occ=[]
    for car in range(cars):
        for n in range(converter_units):
            pose=[[1.,0.,0.,17.5*car+7.1+.27*n],[0.,1.,0.,-1.05],[0.,0.,1.,.62],[0.,0.,0.,1.]]
            occ.append(make_occurrence(f'car-{car+1}/auxiliary-power/EPC-{n+1}',module,f'car-{car+1}/auxiliary-power',pose,'vehicle/auxiliary-power'))
        for n in range(lv_parallel_units):
            pose=[[1.,0.,0.,17.5*car+9.2+.22*(n%8)],[0.,1.,0.,-1.05],[0.,0.,1.,.62+.2*(n//8)],[0.,0.,0.,1.]]
            occ.append(make_occurrence(f'car-{car+1}/auxiliary-power/Orion-{n+1}',orion,f'car-{car+1}/auxiliary-power',pose,'vehicle/auxiliary-power'))
    lowV=c['electrical']['end_pack_voltage_V'];highV=600.
    nominal_each=min(f['nominal_power_W'],highV*f['HV_continuous_A'])
    each=[min(nominal_each,lowV*f['LV_continuous_A']*eta) for eta in (eta_lo,eta_hi)]
    temp_ok=f['ambient_range_C'][0]<=converter_air_C<=f['ambient_range_C'][1]
    voltage_ok=f['LV_range_V'][0]<=lowV<=f['LV_range_V'][1] and f['HV_range_V'][0]<=highV<=f['HV_range_V'][1]
    hv_need=c['HVAC']['units_per_car']*600*18;lv_need=c['HVAC']['units_per_car']*26*70
    lv_each=c['electrical']['LV_converter_per_car_capacity_W'];lv_cap=None if lv_each is None else lv_parallel_units*lv_each
    demand=[hv_need/eta+lv_need/.89 for eta in (eta_hi,eta_lo)]
    capacity=c['electrical']['continuous_at_end_voltage_W']
    available=[converter_units*x for x in each] if temp_ok and voltage_ok else [None,None]
    physical=dict(parent_body_candidate_id=equipment['candidate_id'],EPC_physical_product_id=ep['physical_product_id'],
       EPC_units_per_car=converter_units,LV_parallel_units_per_car=lv_parallel_units,
       part_definition_ids=[module['physical_definition_id'],orion['physical_definition_id']],
       removed_occurrence_ids=[o['occurrence_id'] for o in removed],
       occurrences=[{k:o[k] for k in ('occurrence_id','part_definition_id','parent_id','transform','scope','pose_frame')} for o in occ],
       conditioned_aux_cabinet_required=True)
    return _seal(dict(schema='osr-sourced-auxiliary-bus-case/1',body_candidate_id=equipment['candidate_id'],
       equipment_evaluation_id=equipment['evaluation_id'],physical_definition_id=identity(physical),physical_definition=physical,
       parts=[module,deepcopy(orion)],occurrences=occ,removed_occurrence_ids=[o['occurrence_id'] for o in removed],
       source_sha256=cat['source_sha256'],source_record_id=ep['source_record_id'],
       converter_air_C=converter_air_C,air_temperature_within_published_domain=temp_ok,voltage_within_published_domain=voltage_ok,
       efficiency_bounds_hypothesis=list(efficiency_bounds),efficiency_lower_is_source_guaranteed=False,
       HV_required_per_car_W=hv_need,HV_available_bounds_per_car_W=available,
       LV_HVAC_fans_required_per_car_W=lv_need,LV_available_per_car_W=lv_cap,
       battery_demand_bounds_per_car_W=demand,battery_continuous_per_car_W=capacity,
       battery_peak_headroom_bounds_W=[capacity-demand[1],capacity-demand[0]],
       known_converter_heat_per_car_bounds_W=[hv_need*(1/eta_hi-1)+lv_need*(1/.89-1),hv_need*(1/eta_lo-1)+lv_need*(1/.89-1)],
       conditioned_enclosure_conduction_heat_W=None,conditioned_enclosure_mass_kg=None,
       EPC_catalogue_mass_per_car_kg=converter_units*ep['mass_kg'],
       converter_electrical_necessary_screen='conditional-pass' if temp_ok and voltage_ok and available[0]>=hv_need and lv_cap is not None and lv_cap>=lv_need and capacity>=demand[1] else 'fail-or-held',
       installation_requirements=dict(EPC_mount_fasteners_per_car=4*converter_units,
         converter_earthing_connections_per_car=2*converter_units,HV_fuse_disconnect_branches=converter_units,
         LV_fuse_disconnect_branches=converter_units+lv_parallel_units,
         conditioned_cooling_ducts_required=True,cable_lengths_and_bend_radii=None,
         terminals_torque_and_vibration_retention_approved=False,service_clearance_verified=False,
         external_fans_cooling_and_enclosure_included=False),
       complete_installed_mass_kg=None,operating_map_admitted=False,**FLAGS))


def citysphere_case(required_cooling_W,ambient_C=50.,root=ROOT):
    """Mild-climate alternative with actual published condition and inventories."""
    required_cooling_W=_number(required_cooling_W,'cooling requirement',True)
    if type(ambient_C) not in (int,float) or not isfinite(ambient_C):raise ValueError('Finite ambient required')
    p=next(p for p in catalogue(root)['products'] if p['key']=='citysphere24');f=p['facts'];count=ceil(required_cooling_W/f['rated_cooling_W'])
    return _seal(dict(schema='osr-sourced-directLV-HVAC-case/1',product_evaluation_id=p['product_evaluation_id'],units_per_car=count,
       rated_cooling_subtotal_W=count*f['rated_cooling_W'],rated_inside_C=25.,rated_outside_C=29.,
       selected_ambient_C=ambient_C,available_at_selected_ambient_W=count*f['rated_cooling_W'] if ambient_C==29. else None,
       input_voltage_V=24.,peak_current_A=count*72.,catalogue_mass_kg=count*45.,roof_net_envelope_area_m2=count*1.2*.86,
       converter_and_mounting_mass_kg=None,whole_life_cost=None,hot_climate_screen='held-no-rated-hot-capacity' if ambient_C!=29 else 'conditional-rated-point-only',**FLAGS))


def price_subtotal(candidate_id,records,root=ROOT):
    """Price exact occurrence scope once; unknown remaining scope stays unknown."""
    if not isinstance(candidate_id,str) or len(candidate_id)!=64 or any(c not in '0123456789abcdef' for c in candidate_id):raise ValueError('Candidate identity required')
    if not isinstance(records,list) or not records:raise ValueError('Explicit priced scope required')
    cat=catalogue(root);prices={p['SKU']:p for p in cat['prices']};seen=set();rows=[];total=0.
    for r in records:
        if r['candidate_id']!=candidate_id:raise ValueError('Mixed commercial candidate')
        ids=r['occurrence_ids']
        if not isinstance(ids,list) or not ids or any(not isinstance(x,str) or not x for x in ids) or len(set(ids))!=len(ids) or set(ids)&seen:raise ValueError('Duplicate or malformed priced occurrences')
        seen.update(ids);p=prices.get(r['SKU']);cost=None if p is None else len(ids)*p['unit_price'];total+=cost or 0.
        rows.append(dict(SKU=r['SKU'],occurrence_ids=ids,quantity=len(ids),unit_price_USD=None if p is None else p['unit_price'],
           subtotal_USD=cost,price_source=None if p is None else p,source_record_id=None if p is None else identity(cat['sources'][p['source']])))
    return _seal(dict(schema='osr-public-price-subtotal/1',candidate_id=candidate_id,rows=rows,
       known_list_price_subtotal_USD=total,listed_scope_total_USD=total if all(r['subtotal_USD'] is not None for r in rows) else None,
       complete_installed_total_USD=None,price_class='B-public-regional-list',actual_quotation_coverage=0.,
       shipping_taxes_installation_USD=None,unknown_is_zero=False,**FLAGS))


def charge_budget(equipment,auxiliary_power_W,journey_s,dwell_s=35.,solar_power_W=0.,charging_efficiency=.90,bms_current_A=None):
    """Necessary per-car station charging energy; taper/hardware remain open."""
    _check_equipment(equipment)
    for v,n in ((auxiliary_power_W,'auxiliary power'),(journey_s,'journey'),(dwell_s,'dwell'),(solar_power_W,'solar')):_number(v,n)
    if dwell_s<=0 or not 0<charging_efficiency<=1:raise ValueError('Positive dwell and efficiency required')
    if bms_current_A is not None:_number(bms_current_A,'BMScurrent',True)
    e=constraints(equipment)['electrical'];parallel=e['parallel_strings'];Vcharge=2*28.4
    current_upper=parallel*200 if bms_current_A is None else min(parallel*200,bms_current_A)
    maxcharge=Vcharge*current_upper
    energy=max(0.,auxiliary_power_W-solar_power_W)*(journey_s+dwell_s)
    needed=energy/dwell_s
    return _seal(dict(schema='osr-auxiliary-station-charge-bound/1',candidate_id=equipment['candidate_id'],
       equipment_evaluation_id=equipment['evaluation_id'],journey_s=journey_s,dwell_s=dwell_s,
       auxiliary_power_W=auxiliary_power_W,solar_power_W=solar_power_W,
       required_battery_replenishment_Wh=energy/3600,required_mean_battery_charge_W=needed,
       required_station_input_per_car_W=needed/charging_efficiency,
       source_max_charge_current_A=parallel*200,manufacturer_recommended_charge_current_A=parallel*100,
       BMS_current_hypothesis_A=bms_current_A,installed_BMS_current_validated=False,
       current_limit_after_BMS_hypothesis_A=current_upper,
       battery_manual_source_record_id=identity(equipment['catalogue']['sources']['battery']),
       source_upper_charge_voltage_V=Vcharge,
       nominal_upper_battery_charge_power_W=maxcharge,
       necessary_charge_screen='fail-power-bound' if needed>maxcharge else 'conditional-only',
       charger_installed_mass_kg=None,charger_price=None,actual_SOC_taper_temperature_limits_validated=False,
       cycle_energy_is_measured=False,**FLAGS))
