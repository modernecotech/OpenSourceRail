"""WP05/06/08 provisional electrical architecture and coupled duty adapter.

Uses the existing battery solver. Synthetic maps are explicitly *not* offered
LFP performance. This model checks conservation and causality, not train
comfort, railway protection, traction maps or physical controller timing.
"""
from copy import deepcopy
import math
import tomllib

import numpy as np
from scipy.integrate import solve_ivp

from engineering.twin_workflow import core
from engineering.integration_programme.battery import Battery, power_ledger
from . import contracts, evaluate


def profile():
    return tomllib.loads((core.ROOT/'lib/templates/rolling-stock.toml').read_text())['profiles']['metro-6car']


def electrical_architecture(equipment=None):
    """Named per-car circuits, isolation and returns; no implicit chassis return."""
    from . import installed_equipment
    p=profile();nodes=[];nets=[];interfaces=[];counts=installed_equipment.counts()
    functions=('charger','battery','bms','service-disconnect','main-fuse','precharge',
               'main-contactor','dc-link','inverter','motor','brake-chopper',
               'isolated-dcdc','lv-fuse','lv-cassette','hvac','battery-cooler','bond-bar','controller')
    for car in range(1,p['cars']+1):
        stem=f'car-{car:02d}/'
        for function in functions:
            nodes.append(dict(id=stem+function,function=function,ownership='purchased-boundary',
                physical_quantity=counts['cassettes_per_car'] if function=='lv-cassette' else counts['cooling_modules_per_car'] if function=='hvac' else None,
                physical_instance_ids=[i['id'] for i in equipment['instances']+equipment['purchased_boundaries'] if i['electrical_node_id']==stem+function] if equipment else [],
                supplier_part=None,mass_kg=None,configuration_revision=None,
                qualification='hold-exact-offered-configuration',nominal_voltage_v=(24. if function in {'lv-fuse','lv-cassette','controller'} else None)))
        routes=[('charger','battery','charge-hv'),('battery','service-disconnect','pack-hv'),
                ('service-disconnect','main-fuse','isolated-hv'),('main-fuse','main-contactor','protected-hv'),
                ('main-fuse','precharge','precharge-in'),('precharge','dc-link','precharge-out'),
                ('main-contactor','dc-link','traction-hv'),('dc-link','inverter','inverter-hv'),
                ('inverter','motor','motor-3phase'),('dc-link','brake-chopper','dump-hv'),
                ('dc-link','isolated-dcdc','aux-converter-hv'),('isolated-dcdc','lv-fuse','24V-unprotected'),
                ('lv-fuse','lv-cassette','24V-protected'),('lv-cassette','controller','control-lv'),
                ('dc-link','hvac','hvac-hv'),('dc-link','battery-cooler','battery-cooling-hv')]
        for a,b,label in routes:
            low=label.startswith(('24V','control-lv'))
            nets.append(dict(id=stem+label,endpoints=[stem+a,stem+b],
                conductors=['positive','dedicated-return'] if label!='motor-3phase' else ['U','V','W'],
                nominal_voltage_v=24. if low else p['battery_nominal_voltage_v'] if label!='motor-3phase' else None,
                limiting_voltage_v=None if low or label=='motor-3phase' else p['battery_normal_max_voltage_v'],
                cable_length_m=None,cable_part=None,wire_gauge=None,routing_revision=None,
                ampacity_and_protection=None,insulation_and_emc=None))
        for component in ('charger','battery','inverter','motor','isolated-dcdc','lv-cassette','hvac','battery-cooler'):
            interfaces.append(dict(id=stem+component+'/protective-bond',endpoints=[stem+component,stem+'bond-bar'],
                type='protective-bond',fault_current_a=None,clearing_time_s=None,bond_resistance_limit_ohm=None,
                separate_from_signal_return=True))
        for signal,source,target in [('hv-interlock','service-disconnect','bms'),('battery-permission','bms','main-contactor'),
                                      ('charge-permission','bms','charger'),('traction-permission','controller','inverter'),
                                      ('thermal-request','hvac','controller')]:
            interfaces.append(dict(id=stem+signal,endpoints=[stem+source,stem+target],type='software-signal',
                safe_state='deenergise-request',sample_time_s=None,timeout_s=None,target_timing_verified=False))
    value=dict(schema='osr-six-car-electrical-architecture/1',prototype_revision=contracts.prototype_configuration()['revision'],
        equipment_definition_revision=equipment['revision'] if equipment else None,
        nodes=nodes,nets=nets,interfaces=interfaces,
        isolation_boundaries=['per-car service disconnect','precharge versus main contactor','isolated HV/LV converter',
                              'protective bond separate from traction and signal returns'],
        installed_equipment_mass_kg=None,traction_brake_maps=None,protection_selectivity=None,
        scope='Hierarchical single-line definition and interface schedule; not an issued circuit or selected equipment',**core.FLAGS)
    validate_architecture(value,require_revision=False);value['revision']=core.digest(value);return value


def validate_architecture(value,*,require_revision=True):
    contracts.finite(value);ids=[n['id'] for n in value['nodes']]
    if any(value.get(k) is not False for k in core.FLAGS):raise ValueError('unqualified electrical architecture cannot assert release')
    if require_revision and value.get('revision')!=core.digest({k:v for k,v in value.items() if k!='revision'}):
        raise ValueError('electrical architecture revision differs')
    if len(ids)!=len(set(ids)) or not ids:raise ValueError('unique equipment identities required')
    if value.get('equipment_definition_revision'):
        physical_ids=[]
        for node in value['nodes']:
            if node['physical_quantity'] is not None and len(node['physical_instance_ids'])!=node['physical_quantity']:
                raise ValueError('electrical group/physical instance count differs')
            physical_ids+=node['physical_instance_ids']
        if len(set(physical_ids))!=len(physical_ids):raise ValueError('physical equipment instance mapped twice')
    routes=[n['id'] for n in value['nets']+value['interfaces']]
    if len(routes)!=len(set(routes)):raise ValueError('unique circuit and interface identities required')
    connected=set()
    for net in value['nets']+value['interfaces']:
        if len(net['endpoints'])!=2 or len(set(net['endpoints']))!=2 or not set(net['endpoints'])<=set(ids):
            raise ValueError('circuit endpoints missing or invalid')
        connected.update(net['endpoints'])
    if connected!=set(ids):raise ValueError('unconnected equipment boundary')
    if any(n.get('separate_from_signal_return') is not True for n in value['interfaces'] if n['type']=='protective-bond'):
        raise ValueError('protective-bond/signal-return segregation required')
    return True


def defaults(equipment=None):
    """All non-template quantities are explicit planning sensitivities."""
    from . import installed_equipment,cassette_duty,cassette_system
    p=profile();counts=installed_equipment.counts()
    performance=cassette_duty.cooling_map(p['hvac_design_ambient_c'])
    duct_area=equipment['duct_clear_area_m2'] if equipment else .01
    duct=cassette_system.duct_case(duct_area)
    fan_w=counts['cassettes_per_car']*duct['fan_input_w']
    lv_w=equipment['schedule']['model_lv_source_w']/p['cars'] if equipment else counts['cassettes_per_car']*cassette_system.electrical_case()['power_w']['source']
    return dict(architecture='baghdad-six-car',car_count=p['cars'],car_length_m=p['length_m']/p['cars'],
        passengers_per_car=p['passenger_capacity']/p['cars'],ambient_c=p['hvac_design_ambient_c'],
        target_c=26.,initial_c=35.,ambient_humidity_kg_kg=.015,initial_humidity_kg_kg=.010,
        dry_air_mass_kg=150.,thermal_capacity_j_k=1.2e6,envelope_ua_w_k=250.,
        passenger_sensible_w=75.,passenger_latent_w=55.,solar_w=7000.,equipment_w=3000.,
        fresh_air_kg_s=1.1*min(cassette_system.whole_car_duty()['assumptions']['fresh_air_m3_s'],counts['cassettes_per_car']*duct['useful_flow_m3_s']),door_air_kg_s=.88,cp_j_kg_k=1005.,latent_j_kg=2.45e6,
        cooling_capacity_w=counts['cooling_modules_per_car']*performance['per_module_capacity_w'],sensible_cooling_fraction=.75,cop=performance['cop'],fan_power_w=fan_w,
        base_auxiliary_w=3000.+lv_w,converter_efficiency=.95,battery_soc=.8,battery_soh=1.,
        equipment_definition_revision=equipment['revision'] if equipment else None,
        equipment_layout_sha256=core.sha(installed_equipment.DATA),equipment_counts=counts,
        battery_voltage_v=p['battery_nominal_voltage_v'],battery_capacity_ah=p['onboard_battery_nameplate_kwh']*1000/p['cars']/p['battery_nominal_voltage_v'],
        battery_resistance_ohm=.03,battery_thermal_capacity_j_k=2.e6,battery_ua_w_k=120.,
        battery_initial_c=35.,battery_cooling_w=2000.,battery_cooling_cop=2.5,traction_per_car_w=p['traction_peak_kw']*1000/p['cars']*.5,
        regenerative_per_car_w=100000.,duration_s=1200.,station_cycle_s=150.,door_open_s=30.,
        conditioning_basis='Ideal constant capacity/COP sensitivity, not manufacturer ambient/supply maps',
        battery_basis='Synthetic constant OCV/resistance map for numerical controls only; not chemistry parameterisation',
        missing_inputs=['measured LFP OCV/resistance/age/thermal maps','supplier HVAC and fan maps',
                        'adopted door/glazing/solar/occupancy duty','motor/inverter/brake efficiency maps',
                        'HV/LV cable routes, protection/selectivity/EMC','actual route gradients and station charging trace',
                        'calibrated comfort, air-quality, noise and emergency criteria'])


def _validate(config,dt_s,fault):
    contracts.finite(config)
    positive=('car_count','car_length_m','dry_air_mass_kg','thermal_capacity_j_k','cp_j_kg_k','latent_j_kg',
              'cop','battery_cooling_cop','battery_capacity_ah','battery_voltage_v','battery_thermal_capacity_j_k','battery_ua_w_k',
              'duration_s','station_cycle_s')
    nonnegative=('passengers_per_car','envelope_ua_w_k','passenger_sensible_w','passenger_latent_w','solar_w',
                 'equipment_w','fresh_air_kg_s','door_air_kg_s','cooling_capacity_w','fan_power_w','base_auxiliary_w',
                 'battery_resistance_ohm','battery_cooling_w','traction_per_car_w','regenerative_per_car_w',
                 'ambient_humidity_kg_kg','initial_humidity_kg_kg','door_open_s')
    for key in positive+nonnegative:
        x=config[key]
        if type(x) not in (int,float) or not math.isfinite(x) or x<0 or (key in positive and x==0):
            raise ValueError('invalid duty quantity: '+key)
    if type(dt_s) not in (int,float) or not math.isfinite(dt_s) or not 0<dt_s<=5:raise ValueError('duty step outside (0,5] seconds')
    if config['duration_s']>3600 or config['duration_s']/dt_s>20000:raise ValueError('bounded duty budget exceeded')
    if config['architecture']!='baghdad-six-car' or config['car_count']!=6:raise ValueError('six-car architecture required')
    if not .5<=config['battery_soh']<=1 or not .1<=config['battery_soc']<=.95:raise ValueError('battery state domain')
    if not 0<config['converter_efficiency']<=1 or not 0<=config['sensible_cooling_fraction']<=1:raise ValueError('efficiency/fraction domain')
    if config['door_open_s']>config['station_cycle_s']:raise ValueError('door cycle domain')
    if max(config['ambient_humidity_kg_kg'],config['initial_humidity_kg_kg'])>.05:raise ValueError('humidity outside dilute-air research domain')
    if fault not in {'nominal','cooling-loss','battery-cooling-loss','combined-cooling-loss','fan-failure','blocked-filter','communication-loss','open-bond','unlock','hot-start','sensor-bias','aged-battery'}:
        raise ValueError('unknown coupled fault')


def simulate(config=None,*,dt_s=1.,fault='nominal'):
    """Explicit one-car sample-and-hold plant; report six-car energy by symmetry.

    Air and sensible energy ODEs use exact frozen-input exponential integration.
    Heat/moisture ledgers integrate the same boundary fluxes. The battery adapter
    independently balances chemical/terminal/Joule energy. Traces retain one
    representative car; identical-car scaling is not a full-train dynamics model.
    """
    c=deepcopy(config or defaults());_validate(c,dt_s,fault)
    if fault=='hot-start':c['initial_c']=55.
    if fault=='aged-battery':c['battery_soh']=.8
    pack=dict(soc_min=.1,soc_max=.95,capacity_ah=c['battery_capacity_ah'],
        discharge_current_limit_a=1200.,charge_current_limit_a=500.,
        thermal_capacity_j_k=c['battery_thermal_capacity_j_k'],cooling_conductance_w_k=c['battery_ua_w_k'])
    maps=dict(soc=[.1,.95],temperature_c=[-20.,90.],capacity_reference_soh=1.,
        ocv_v=[[c['battery_voltage_v']]*2]*2,resistance_ohm=[[max(c['battery_resistance_ohm'],1e-12)]*2]*2,basis=c['battery_basis'])
    battery=Battery(pack,maps,soc=c['battery_soc'],temperature_c=c['battery_initial_c'],soh=c['battery_soh'])
    T=c['initial_c'];w=c['initial_humidity_kg_kg'];initial_T=T;initial_w=w;tripped=False;rows=[]
    latent=c['latent_j_kg'];control={};exec(evaluate.control_source('branch'),control)
    totals={key:0. for key in ('terminal_j','chemical_j','joule_j','cooling_j','hvac_electric_j','battery_cooling_electric_j','converter_heat_j',
                               'cabin_net_sensible_j','water_net_kg','condensate_kg')}
    maxres={key:0. for key in ('battery_electrical_j','battery_thermal_j','cabin_sensible_j','water_kg','electrical_w')}
    time_s=0.;domain_error=None
    while time_s<c['duration_s']-1e-9:
        dt=min(dt_s,c['duration_s']-time_s);phase=time_s%c['station_cycle_s'];doors=phase<c['door_open_s']
        # Inputs sampled at left edge; reset never injected automatically.
        inputs=dict(locked=fault!='unlock',earth_ok=fault!='open-bond',fresh=not(fault=='communication-loss' and time_s>=300),
                    supply_ok=True,reset=False,stopped=doors,request=True)
        permission=control['step'](tripped,inputs);tripped=permission['tripped'];enabled=permission['enabled']
        fan=0. if fault=='fan-failure' or not enabled else c['fan_power_w']
        fresh=c['fresh_air_kg_s']*(.4 if fault=='blocked-filter' else 1.) if fan else 0.
        air=fresh+(c['door_air_kg_s'] if doors else 0.)
        sensed=T+(-5. if fault=='sensor-bias' else 0.)
        cooling=c['cooling_capacity_w'] if enabled and fan and sensed>c['target_c'] and fault not in {'cooling-loss','combined-cooling-loss'} else 0.
        qs=cooling*c['sensible_cooling_fraction'];ql=cooling-qs
        # Limit condensation by incoming + stored moisture; never negative humidity.
        generated=c['passengers_per_car']*c['passenger_latent_w']/latent
        stored_release=w*air/math.expm1(air*dt/c['dry_air_mass_kg']) if air else w*c['dry_air_mass_kg']/dt
        condensate=min(ql/latent,generated+air*c['ambient_humidity_kg_kg']+stored_release)
        H=c['envelope_ua_w_k']+air*c['cp_j_kg_k']
        Q=c['passengers_per_car']*c['passenger_sensible_w']+c['solar_w']+c['equipment_w']+fan-qs
        oldT=T;oldw=w
        if H:
            eq=c['ambient_c']+Q/H;T=eq+(T-eq)*math.exp(-H*dt/c['thermal_capacity_j_k'])
            sensible_integral=c['thermal_capacity_j_k']*(T-oldT)
        else:T+=Q*dt/c['thermal_capacity_j_k'];sensible_integral=Q*dt
        water_source=generated-condensate
        if air:
            eqw=c['ambient_humidity_kg_kg']+water_source/air
            w=eqw+(w-eqw)*math.exp(-air*dt/c['dry_air_mass_kg'])
        else:w+=water_source*dt/c['dry_air_mass_kg']
        if w < -1e-14:raise ValueError('moisture state outside nonnegative domain')
        w=max(w,0.)
        # Independently recover integrals of the exact ODE solutions.
        meanT=(c['ambient_c']+Q/H)+(oldT-c['ambient_c']-Q/H)*(-math.expm1(-H*dt/c['thermal_capacity_j_k']))/(H*dt/c['thermal_capacity_j_k']) if H else (oldT+T)/2
        cabin_flux=(H*(c['ambient_c']-meanT)+Q)*dt
        meanw=eqw+(oldw-eqw)*(-math.expm1(-air*dt/c['dry_air_mass_kg']))/(air*dt/c['dry_air_mass_kg']) if air else (oldw+w)/2
        water_flux=(generated-condensate+air*(c['ambient_humidity_kg_kg']-meanw))*dt
        actual_cooling=qs+condensate*latent
        hvac=actual_cooling/c['cop']+fan
        lv=c['base_auxiliary_w'];converter=lv/c['converter_efficiency'];converter_heat=converter-lv
        battery_cooling=0. if fault in {'battery-cooling-loss','combined-cooling-loss'} else c['battery_cooling_w']
        battery_cooling_electric=battery_cooling/c['battery_cooling_cop']
        traction=0. if doors or not enabled else c['traction_per_car_w'] if phase<70 else -c['regenerative_per_car_w'] if phase>=120 else c['traction_per_car_w']*.12
        ledger=power_ledger([dict(id='traction-net',power_w=traction),dict(id='HVAC',power_w=hvac),
                             dict(id='battery-cooling',power_w=battery_cooling_electric),
                             dict(id='LV-load',power_w=lv),dict(id='converter-loss',power_w=converter_heat)])
        battery_T0=battery.temperature
        try:b=battery.step(ledger['total_terminal_power_w'],dt,cooling_w=battery_cooling,ambient_c=c['ambient_c'])
        except ValueError as exc:
            # A rejected coupling step commits neither plant state.
            T=oldT;w=oldw;domain_error=str(exc);break
        residual=ledger['total_terminal_power_w']-traction-hvac-lv-converter_heat-battery_cooling_electric
        maxres['electrical_w']=max(maxres['electrical_w'],abs(residual))
        maxres['battery_electrical_j']=max(maxres['battery_electrical_j'],abs(b['electrical_residual_j']))
        battery_heat_residual=independent_battery_heat_residual(b,battery_T0,dt,
            thermal_capacity_j_k=c['battery_thermal_capacity_j_k'],conductance_w_k=c['battery_ua_w_k'],ambient_c=c['ambient_c'])
        maxres['battery_thermal_j']=max(maxres['battery_thermal_j'],abs(battery_heat_residual))
        maxres['cabin_sensible_j']=max(maxres['cabin_sensible_j'],abs(sensible_integral-cabin_flux))
        maxres['water_kg']=max(maxres['water_kg'],abs(c['dry_air_mass_kg']*(w-oldw)-water_flux))
        for key,value in dict(terminal_j=b['terminal_energy_j'],chemical_j=b['chemical_energy_j'],joule_j=b['joule_heat_j'],
            cooling_j=actual_cooling*dt,hvac_electric_j=hvac*dt,battery_cooling_electric_j=battery_cooling_electric*dt,
            converter_heat_j=converter_heat*dt,cabin_net_sensible_j=cabin_flux,
            water_net_kg=water_flux,condensate_kg=condensate*dt).items():totals[key]+=value
        if int(time_s)%10==0 or time_s+dt>=c['duration_s']:
            rows.append(dict(time_s=time_s+dt,cabin_c=T,humidity_kg_kg=w,battery_c=b['temperature_c'],soc=b['soc'],
                enabled=enabled,doors_open=doors,terminal_power_w=ledger['total_terminal_power_w'],traction_w=traction,
                hvac_w=hvac,battery_cooling_w=battery_cooling,battery_cooling_electric_w=battery_cooling_electric,
                cooling_w=actual_cooling,requested_cooling_w=cooling,condensate_kg_s=condensate))
        time_s+=dt
    checks=dict(completed_horizon=domain_error is None and abs(time_s-c['duration_s'])<1e-8,
        electrical_conservation=maxres['electrical_w']<1e-6 and maxres['battery_electrical_j']<1e-5,
        battery_heat_conservation=maxres['battery_thermal_j']<1e-5,cabin_heat_conservation=maxres['cabin_sensible_j']<1e-5,
        water_conservation=maxres['water_kg']<1e-10,
        fault_permission=all(not r['enabled'] and r['traction_w']==0 for r in rows if (fault in {'unlock','open-bond'} or fault=='communication-loss' and r['time_s']>300)),
        supplier_performance=None,comfort_and_air_quality=None,route_specific_duty=None,target_hardware_timing=None)
    result=dict(schema='osr-coupled-cabin-battery-duty/1',input=c,fault=fault,dt_s=dt_s,elapsed_s=time_s,domain_error=domain_error,
        initial=dict(cabin_c=initial_T,humidity_kg_kg=initial_w),final=dict(cabin_c=T,humidity_kg_kg=w,soc=battery.soc,battery_c=battery.temperature),
        representative_car_totals=totals,six_identical_car_totals={k:v*c['car_count'] for k,v in totals.items()},
        maximum_residuals=maxres,trace=rows,checks=checks,failed_checks=[k for k,v in checks.items() if v is False],
        held_checks=[k for k,v in checks.items() if v is None],battery_map_sha256=core.digest(maps),
        causality='Left-edge sampled permissions and cooling; electrical load -> battery; heat/moisture -> next controller sample. Sensor-bias case is -5 C. Cooling-loss affects cabin; separate cases remove battery or both cooling plants. No iterative algebraic loop.',
        scope='Twenty-minute synthetic repeated-station sensitivity, one-car lumped air/thermal state and identical-car energy scaling. No full train passage, refrigeration circuit, CFD or LFP validation.',**core.FLAGS)
    result['revision']=core.digest(result);return result


def independent_battery_heat_residual(step,initial_c,dt_s,*,thermal_capacity_j_k,conductance_w_k,ambient_c):
    """Integrate the ambient flux independently of Battery's inferred residual."""
    C=thermal_capacity_j_k;H=conductance_w_k
    heat_rate=step['joule_heat_j']/dt_s;removed_rate=step['active_heat_removed_j']/dt_s
    equilibrium=ambient_c+(heat_rate-removed_rate)/H
    ambient_heat=H*((equilibrium-ambient_c)*dt_s+(initial_c-equilibrium)*C/H*(-math.expm1(-H*dt_s/C)))
    return step['joule_heat_j']-step['active_heat_removed_j']-ambient_heat-C*(step['temperature_c']-initial_c)


def circuit_benchmark():
    """Independent IVP against exact RC control; not an ngspice execution."""
    V,R,C=24.,10.,.0047;times=np.linspace(0,.25,101)
    solution=solve_ivp(lambda t,y:[(V-y[0])/(R*C)],(0,.25),[0.],t_eval=times,rtol=1e-10,atol=1e-11)
    exact=V*(1-np.exp(-times/(R*C)));error=float(np.max(np.abs(solution.y[0]-exact)))
    return dict(method='scipy.solve_ivp RK45 versus analytic RC',maximum_voltage_error_v=error,
        passed=bool(solution.success and error<1e-7),ngspice_executed=False,
        open=['selected converter input model','electrothermal contact/arc model','protective device I2t and selectivity'],**core.FLAGS)


def report(equipment=None):
    config=defaults(equipment);cases=[simulate(config,fault=fault) for fault in ('nominal','cooling-loss','battery-cooling-loss','combined-cooling-loss','fan-failure','blocked-filter',
        'communication-loss','open-bond','unlock','hot-start','sensor-bias','aged-battery')]
    refined=simulate(config,dt_s=.5);nominal=cases[0]
    differences={k:abs(nominal['final'][k]-refined['final'][k]) for k in nominal['final']}
    value=dict(schema='osr-provisional-system-design/1',equipment_definition_revision=config['equipment_definition_revision'],equipment_counts=config['equipment_counts'],electrical=electrical_architecture(equipment),duty_cases=cases,
        refinement=dict(dt_s=[1.,.5],absolute_final_differences=differences,
            same_final_state_within_screen=all(v<.02 for v in differences.values()),
            scope='Time discretisation check in the synthetic duty; not spatial/modal convergence or comfort acceptance'),
        circuit=circuit_benchmark(),assumption_status='Planning sensitivity; no parameters adopted as approved requirements',
        sources=[dict(path='lib/templates/rolling-stock.toml',sha256=core.sha(core.ROOT/'lib/templates/rolling-stock.toml'),
                      locator='profiles.metro-6car; nameplate, voltage, passengers, traction allocation, climate'),
                 dict(url='https://ngspice.sourceforge.io/ngspice-electrothermal-tutorial.html',
                      applicability='Implementation reference only; external simulator not executed'),
                 dict(url='https://coolprop.org/fluid_properties/HumidAir.html',
                      applicability='Higher fidelity property adapter still required; present Level 1 uses declared constant cp/latent assumptions')],
        scope='Hierarchical electrical interface definition plus conserving temporal research model; exact purchased configurations, physical calibration and full train integration remain open',**core.FLAGS)
    value['revision']=core.digest(value);return value
