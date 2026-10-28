"""Version-specific wayside PM drive configurations and bounded research caps.

Published ratings condition the calculations; they are not railway force maps.
Stationary motors remain wayside, and the vehicle carries only passive stock.
"""
from copy import deepcopy
from pathlib import Path
from math import pi,sqrt,exp,fsum,isfinite
import json,hashlib
from . import ROOT,FLAGS,identity,digest
from engineering.railway_progress import alternatives as legacy
CODE='engineering/sourced_case/drive.py'
DATA='engineering/sourced_case/data/drive-sources.json'
PAIRS={'emrax348-lv43-h300':('emrax348-lv43',450.),'emrax268-mv-h300':('emrax268-mv',400.),'parker400-dpw-h300':('parker400-dpw',400.)}


def sources(root=ROOT):return {p:digest(Path(root)/p) for p in (CODE,DATA,legacy.CODE,legacy.DATA)}


def catalogue(root=ROOT):
    r=json.loads((Path(root)/DATA).read_bytes())
    if r['schema']!='osr-sourced-station-drive-facts/1' or r['physical_accepted'] is not False:raise ValueError('Published unqualified drive facts required')
    for parsed in r['parsed_primary_sources'].values():
        raw=json.dumps(parsed['facts'],sort_keys=True,separators=(',',':')).encode()
        if hashlib.sha256(raw).hexdigest()!=parsed['parsed_facts_sha256']:raise ValueError('Parsed primary specification facts differ')
    return r


def _positive(value,name,zero=False):
    if type(value) not in (int,float) or not isfinite(value) or (value<0 if zero else value<=0):raise ValueError('Finite physical '+name+' required')
    return float(value)


def configure(variant='emrax348-lv43-h300',*,gear_ratio=5,roller_radius_m=.32,shared_motor=False,ambient_C=55.,motor_air_C=None,
              motor_coolant_C=None,inverter_coolant_C=55.,dc_voltage_V=None,root=ROOT):
    if variant not in PAIRS or type(shared_motor) is not bool:raise ValueError('Registered exact motor/inverter and physical sharing choice required')
    facts=catalogue(root);mid,voltage=PAIRS[variant];m=deepcopy(facts['motors'][mid]);i=deepcopy(facts['inverters']['h300']);g=deepcopy(facts['gearbox'])
    if type(gear_ratio) is not int or str(gear_ratio) not in g['ratios']:raise ValueError('Published one-stage AB180 ratio required')
    R=_positive(roller_radius_m,'roller radius');site=_positive(ambient_C+100,'ambient offset')-100
    air=site if motor_air_C is None else _positive(motor_air_C+100,'motor air offset')-100
    coolant=m['coolant_in_max_C'] if motor_coolant_C is None else float(motor_coolant_C)
    invcool=float(inverter_coolant_C);V=voltage if dc_voltage_V is None else _positive(dc_voltage_V,'DC link')
    if not all(isfinite(x) for x in (coolant,invcool)):raise ValueError('Finite coolant conditions required')
    ratio_current=m['torque_constant_Nm_per_Arms'] or m['nominal_point_torque_current_ratio_Nm_per_Arms']
    I=min(m['continuous_current_Arms'],i['continuous_current_Arms'])
    torque=min(m['continuous_torque_Nm'],ratio_current*I,g['ratios'][str(gear_ratio)]/(gear_ratio*g['efficiency_min']))
    current=torque/ratio_current
    rpm20=20/R*60/(2*pi)*gear_ratio
    voltage_rpm=m['loaded_rpm_per_Vdc']*V if m['loaded_rpm_per_Vdc'] is not None else m['rated_rpm'] if V==m['rated_voltage_Vdc'] else 0.
    rpm_cap=min(m['limiting_rpm'],voltage_rpm,g['nominal_input_rpm'])
    power=min(m['continuous_power_W'],i['continuous_apparent_power_VA'],torque*rpm_cap*2*pi/60)
    checks=dict(dc_bus=i['dc_voltage_min_V']<=V<=i['dc_voltage_max_V'],motor_air=air<=m['motor_air_max_C'],
        motor_coolant=coolant<=m['coolant_in_max_C'],inverter_coolant=invcool<i['coolant_derate_C'],inverter_ambient=site<=i['ambient_max_C'],
        gearbox_speed=rpm20<=g['nominal_input_rpm'],motor_voltage_speed=rpm20<=voltage_rpm,motor_mechanical_speed=rpm20<=m['limiting_rpm'])
    p=dict(variant=variant,motor_model=m['model'],motor_version=m['version'],inverter_model=i['model'],inverter_version=i['version'],
        gearbox_model=g['model'],gear_ratio=gear_ratio,roller_radius_m=R,shared_motor_per_opposed_pair=shared_motor,dc_voltage_V=V,
        conditioned_motor_plenum_required=air<site,motor_resolver_required=True,wayside_PM_only=True)
    r=dict(schema='osr-source-conditioned-drive/1',physical_definition=p,component_configuration_id=identity(p),motor=m,inverter=i,gearbox=g,
        context=dict(site_ambient_C=site,motor_air_C=air,motor_coolant_in_C=coolant,inverter_coolant_in_C=invcool),
        continuous_motor_torque_cap_Nm=torque,continuous_current_cap_Arms=current,continuous_shaft_power_cap_W=power,
        motor_rpm_at20m_s=rpm20,motor_rpm_cap=rpm_cap,source_domain_checks=checks,source_domain_supported=all(checks.values()),
        motor_airflow_m3_min_at_shaft_cap=None if m['rotor_air_m3_min_per_shaft_kW'] is None else m['rotor_air_m3_min_per_shaft_kW']*power/1000,
        full_loss_map_available=False,installed_cooling_verified=False,paired_commissioning_verified=False,available_operating_map=None,
        source_sha256=sources(root),**FLAGS)
    r['evaluation_id']=identity(r);return r


def _configuration(c,root=ROOT):
    if c.get('evaluation_id')!=identity({k:v for k,v in c.items() if k!='evaluation_id'}) or any(c.get(k) is not False for k in FLAGS):raise ValueError('Exact unqualified drive configuration required')
    p=c['physical_definition'];x=c['context']
    expected=configure(p['variant'],gear_ratio=p['gear_ratio'],roller_radius_m=p['roller_radius_m'],shared_motor=p['shared_motor_per_opposed_pair'],
        ambient_C=x['site_ambient_C'],motor_air_C=x['motor_air_C'],motor_coolant_C=x['motor_coolant_in_C'],inverter_coolant_C=x['inverter_coolant_in_C'],dc_voltage_V=p['dc_voltage_V'],root=root)
    if c!=expected:raise ValueError('Drive ratings/source epoch do not reconstruct from exact published variants')
    return c


def materialize(vehicle,base_bundle=None,*,distance_m=2000.,variant='emrax348-lv43-h300',parameters=None,ambient_C=55.,configuration=None,root=ROOT):
    """Return a new legacy-shaped alternative; old ABB inventories never survive.

    A shared motor has two contact channels. Legacy active_motor_count therefore
    counts channels; physical motor counts are reported separately and half power
    is allocated to each opposing face, preventing free duplication of power.
    """
    c=_configuration(deepcopy(configuration),root) if configuration is not None else configure(variant,ambient_C=ambient_C,root=root)
    p=dict(roller_diameter_m=2*c['physical_definition']['roller_radius_m'],roller_pairs_per_bank=6,motor_count=12)
    if parameters:p.update(deepcopy(parameters))
    requested_motors=None if parameters is None else parameters.get('motor_count')
    expected_motors=p['roller_pairs_per_bank']*(1 if c['physical_definition']['shared_motor_per_opposed_pair'] else 2)
    if requested_motors is not None and requested_motors!=expected_motors:raise ValueError('Physical motor count must match actual opposed-pair sharing')
    if 'roller_pairs_per_bank' in p:p['motor_count']=2*p['roller_pairs_per_bank']
    a=legacy.evaluate(vehicle,base_bundle,kind='station-pinch-rollers',distance_m=distance_m,parameters=p,root=root)
    old_id=a['candidate_id'];banks=len(a['parameters']['bank_starts_m']);pairs=a['parameters']['roller_pairs_per_bank'];shared=c['physical_definition']['shared_motor_per_opposed_pair']
    n=banks*pairs*(1 if shared else 2);inventory=[]
    a['parameters']['motor_count']=pairs*(1 if shared else 2)
    removed=('ABB-M3BP355MLB6-K','geared-transmission','VFD-protection-cooling-cabling')
    for row in a['inventory']:
        if row['part_id'] not in removed:inventory.append(deepcopy(row))
    centers=[s+(j+.5)*a['parameters']['bank_length_m']/pairs for s in a['parameters']['bank_starts_m'] for j in range(pairs) for _ in range(1 if shared else 2)]
    def purchased(name,count,mass,source,positions=None):
        row=dict(part_id=name,installation='wayside',shape='purchased-assembly-envelope',dimensions_m=None,net_volume_m3=None,
            calculated_mass_kg=None,catalogue_mass_kg=mass,mass_bounds_kg=None,count=count,at_m=None,source=source,
            longitudinal_instance_centres_m=deepcopy(centers if positions is None else positions),manufacturing='Qualified supplier, flange/shaft adaptation, containment and inspection pending')
        row['physical_definition_id']=identity({k:row[k] for k in ('part_id','installation','shape','dimensions_m','net_volume_m3','source')});inventory.append(row)
    purchased(c['motor']['model'],n,c['motor']['mass_kg'],c['motor']['source'])
    purchased(c['inverter']['model'],n,c['inverter']['mass_kg'],c['inverter']['source'])
    purchased('APEX-AB180-ratio-'+str(c['physical_definition']['gear_ratio']),n,c['gearbox']['mass_kg'],c['gearbox']['source'])
    for name,count,pos in [('encoder-temperature-and-phase-shielded-cable-kit',n,None),('motor-flange-shaft-coupling-guard-kit',n,None),
        ('DC-fuse-contactor-precharge-isolation-discharge-kit',n,None),('bank-rectifier-DC-bus-feeder-transformer-earthing-protection',banks,a['parameters']['bank_starts_m']),
        ('motor-cooling-pump-filter-manifold-hose-heat-exchanger',banks,a['parameters']['bank_starts_m']),('inverter-separate-cooling-loop',banks,a['parameters']['bank_starts_m']),('receiving-brake-chopper-resistor-DC-absorption-kit',banks,a['parameters']['bank_starts_m'])]:purchased(name,count,None,'unresolved-installed-equipment',pos)
    if shared:purchased('opposed-roller-two-output-reversing-drive-and-load-sharing',n,None,'unqualified-physical-transmission')
    if c['physical_definition']['conditioned_motor_plenum_required']:
        purchased('conditioned-rotor-air-plenum-chiller-fan-filter-condensate',banks,None,'unqualified-hot-climate-plant',a['parameters']['bank_starts_m'])
    physical=deepcopy(a['physical_definition']);physical['geometry']['motor_count']=a['parameters']['motor_count'];physical.update(source_conditioned_drive=c['physical_definition'],parent_prototype_candidate_id=old_id,
        inventory_definitions=[{k:r.get(k) for k in ('part_id','physical_definition_id','installation','count','at_m','longitudinal_instance_centres_m')} for r in inventory])
    cid=identity(physical)
    for row in inventory:row['candidate_id']=cid
    channels_per_motor=2 if shared else 1;model=deepcopy(a['conditional_force_model'])
    model.update(torque_per_motor_Nm=c['continuous_motor_torque_cap_Nm']/channels_per_motor,
        power_per_motor_W=c['continuous_shaft_power_cap_W']/channels_per_motor,gear_ratio=c['physical_definition']['gear_ratio'],
        transmission_efficiency=c['gearbox']['efficiency_min'],shaft_rotor_inertia_per_motor_kg_m2=c['motor']['rotor_inertia_kg_m2'],
        physical_motors_per_contact_pair=1 if shared else 2,legacy_active_motor_count_is_contact_channels=True,
        source_class='B-exact-variant-ratings;C-contact/clamp/installation; no railway operating map',
        source_domain_supported=c['source_domain_supported'],drive_configuration_id=c['evaluation_id'])
    a.update(candidate_id=cid,physical_definition=physical,inventory=inventory,drive_configuration=c,
        conditional_force_model=model,installed_physical_motor_count=n,installed_contact_channel_count=2*banks*pairs,
        published_catalogue_mass_subtotal_kg=fsum(r['count']*r['catalogue_mass_kg'] for r in inventory if r.get('catalogue_mass_kg') is not None),
        unknown_installed_mass_items=[r['part_id'] for r in inventory if r.get('calculated_mass_kg') is None and r.get('catalogue_mass_kg') is None],
        source_sha256={**a['source_sha256'],**sources(root)},parent_prototype_candidate_id=old_id,
        parent_source_fact_ids=deepcopy(a['source_fact_ids']),source_fact_ids=[c['motor']['source'],c['inverter']['source'],c['gearbox']['source']],
        installed_minimum_motor_flow_l_min=None if c['motor']['minimum_flow_l_min'] is None else n*c['motor']['minimum_flow_l_min'],
        motor_catalogue_mass_subtotal_kg=n*c['motor']['mass_kg'],inverter_catalogue_mass_subtotal_kg=n*c['inverter']['mass_kg'],gear_catalogue_mass_subtotal_kg=n*c['gearbox']['mass_kg'],
        ancestry=dict(parent_candidate_id=old_id,reason='Actual motor/inverter/gear/roller and plant revision; no inherited ABB rating or cost'),
        open_tasks=a['open_tasks']+['Validate source rating conditions, current/voltage response, cooling, repeated120s duty, gearbox adaptation, shared outputs and independent receiving/braking protection'])
    a['mechanism']=dict(a['mechanism'],gear_ratio_motor_to_roller=c['physical_definition']['gear_ratio'],active_motor_lower_count=None,conditional_nameplate_shaft_power_W=None,source_conditioned_motor_count=n,actual_converter_limits=None,available_force_map=None)
    # Old load-case power-pass rows were computed for ABB hardware. Retain only
    # same-mass demand quantities, explicitly replacing hardware-dependent claims.
    for row in a['load_cases']:
        for key in list(row):
            if any(token in key for token in ('mechanical_power_screen_passed','nameplate','available')):row.pop(key)
        row['mechanical_power_screen_passed']=None
    a['evaluation_id']=identity({k:v for k,v in a.items() if k!='evaluation_id'});return a


def force_model(alternative):
    if alternative.get('evaluation_id')!=identity({k:v for k,v in alternative.items() if k!='evaluation_id'}):raise ValueError('Exact sourced alternative required')
    a=deepcopy(alternative);c=_configuration(a['drive_configuration']);owned=legacy.force_model(a)
    def force(front_m,speed_m_s,*,condition='nominal',power_enabled=True,failed_banks=()):
        # Always call the geometry validator, even in held domain states.
        row=owned(front_m,speed_m_s,condition=condition,power_enabled=power_enabled,failed_banks=failed_banks)
        if not c['source_domain_supported']:
            return dict(row,force_N=None,state='held-outside-published-drive-conditions',source_domain_checks=c['source_domain_checks'],physical_motor_count=0,
                electrical_thermal_ratings=c,available_operating_map=None)
        channels=row.get('active_motor_count',0);shared=c['physical_definition']['shared_motor_per_opposed_pair']
        return dict(row,physical_motor_count=channels/(2 if shared else 1),electrical_thermal_ratings=c,
            motor_continuous_current_cap_Arms=c['continuous_current_cap_Arms'],motor_rpm=float(speed_m_s)/c['physical_definition']['roller_radius_m']*c['physical_definition']['gear_ratio']*60/(2*pi),
            dc_voltage_V=c['physical_definition']['dc_voltage_V'],repeated_thermal_duty_verified=False,receiving_regeneration_qualified=False)
    return force


alternative=materialize


def electrical_step(configuration,current_Arms,voltage_q_rms_V,rpm,dt_s,*,winding_C=80.):
    """Source-parameter RL method control; not a commissioned vector controller.

    Line-RMS back EMF is converted to phase RMS. Cross-axis Lq voltage is retained
    as a necessary bus requirement. Actual vector-control/flux conventions and
    force correlation remain unvalidated; missing R/L never becomes zero.
    """
    return _electrical_step_owned(_configuration(configuration),current_Arms,voltage_q_rms_V,rpm,dt_s,winding_C=winding_C)


def electrical_model(configuration):
    c=deepcopy(_configuration(configuration))
    def step(current_Arms,voltage_q_rms_V,rpm,dt_s,*,winding_C=80.):
        return _electrical_step_owned(c,current_Arms,voltage_q_rms_V,rpm,dt_s,winding_C=winding_C)
    return step


def _electrical_step_owned(c,current_Arms,voltage_q_rms_V,rpm,dt_s,*,winding_C=80.):
    m=c['motor'];I=_positive(current_Arms,'current',True);V=_positive(voltage_q_rms_V,'phase command',True)
    rpm=_positive(rpm,'rpm',True);dt=_positive(dt_s,'time step');T=float(winding_C)
    if not isfinite(T) or T<=-273.15 or dt>1:raise ValueError('Finite bounded winding/time context required')
    if any(m[k] is None for k in ('phase_R25_ohm','Lq_H','Ke_line_RMS_V_per_rpm','pole_pairs')):
        return dict(execution='held-missing-source-R-L-flux-current-model',current_Arms=None,copper_loss_W=None,**FLAGS)
    R=m['phase_R25_ohm']*(1+.00393*(T-25))
    if R<=0:raise ValueError('Copper resistance extrapolation outside method domain')
    L=m['Lq_H'];E=m['Ke_line_RMS_V_per_rpm']*rpm/sqrt(3);phase_limit=c['physical_definition']['dc_voltage_V']/sqrt(6)
    V=min(V,phase_limit);steady=max(0.,(V-E)/R);nextI=min(c['continuous_current_cap_Arms'],steady+(I-steady)*exp(-R*dt/L))
    nextI=max(0.,nextI);cross=2*pi*rpm/60*m['pole_pairs']*L*nextI
    required=sqrt((R*nextI+E)**2+cross**2)
    return dict(execution='conditional-RL-method',current_Arms=nextI,torque_cap_Nm=min(c['continuous_motor_torque_cap_Nm'],m['torque_constant_Nm_per_Arms']*nextI),
        phase_voltage_required_rms_V=required,phase_bus_limit_rms_V=phase_limit,voltage_necessary_screen_passed=required<=phase_limit,
        copper_loss_W=3*R*nextI**2,phase_R_ohm=R,current_dynamics_validated=False,voltage_convention_verified=False,Ke_line_to_line_RMS_interpretation_is_hypothesis=True,copper_alpha_per_K_hypothesis=.00393,**FLAGS)


def duty(configuration,samples,*,headway_s=120.):
    """One physical motor's repeated-cycle RMS and source-conditioned loss bounds."""
    c=_configuration(configuration);period=_positive(headway_s,'headway')
    if period!=120. or not samples or len(samples)>10000:raise ValueError('Explicit bounded120s duty samples required')
    used=0.;I2=0.;shaft=0.;speed2=0.;copper=0.;unknown=False;peakI=peakP=peakrpm=0.
    for s in samples:
        if set(s)!={'dt_s','current_Arms','shaft_power_W','rpm','winding_C'}:raise ValueError('Per-motor currents/power/speed/temperature required')
        dt=_positive(s['dt_s'],'sample duration');I=_positive(s['current_Arms'],'sample RMS current',True);P=_positive(s['shaft_power_W'],'shaft power',True);rpm=_positive(s['rpm'],'speed',True)
        temperature=s['winding_C']
        if type(temperature) not in (int,float) or not isfinite(temperature) or temperature<=-273.15:raise ValueError('Finite physical winding temperature required')
        used+=dt;I2+=I*I*dt;shaft+=P*dt;speed2+=rpm*rpm*dt;peakI=max(peakI,I);peakP=max(peakP,P);peakrpm=max(peakrpm,rpm)
        R=c['motor']['phase_R25_ohm']
        if R is None:unknown=True
        else:copper+=3*I*I*R*(1+.00393*(s['winding_C']-25))*dt
    if used>period+1e-9:raise ValueError('Duty exceeds complete headway cycle')
    I=sqrt(I2/period);eff=c['motor']['peak_efficiency'];lower=0. if unknown else copper/period
    if eff is not None:lower=max(lower,shaft/period*(1/eff-1))
    r=dict(schema='osr-station-drive120s-duty/1',configuration_evaluation_id=c['evaluation_id'],headway_s=period,active_duration_s=used,
        RMS_current_Arms=I,maximum_current_Arms=peakI,maximum_shaft_power_W=peakP,maximum_rpm=peakrpm,RMS_speed_rpm=sqrt(speed2/period),mean_shaft_power_W=shaft/period,
        counted_copper_heat_W=None if unknown else copper/period,other_motor_heat_W=None,inverter_heat_W=None,
        motor_heat_lower_bound_W=None if unknown else lower,motor_heat_upper_bound_W=None,gear_heat_W=None,
        current_necessary_screen_passed=I<=c['continuous_current_cap_Arms'] and peakI<=c['continuous_current_cap_Arms'],
        instantaneous_continuous_current_screen_passed=peakI<=c['continuous_current_cap_Arms'],
        power_speed_necessary_screen_passed=peakP<=c['continuous_shaft_power_cap_W'] and peakrpm<=c['motor_rpm_cap'],
        full_thermal_or_cooling_screen_passed=False,assumption='Unlisted rest time has zero traction current only; fans/pumps/control and standby losses remain unknown',**FLAGS)
    r['evaluation_id']=identity(r);return r
