"""Couple counted thermal features, hot-load scenarios and retained coil samples.

Package capacity at 50 C and actual nonlinear circuit/thermal parameters remain
unknown. Numerical fixtures verify arithmetic, not a functioning suspension or
rail-qualified climate system. No previous result or source receipt is changed.
"""
from copy import deepcopy
from hashlib import sha256
import itertools
import json
import math
from pathlib import Path
import platform
import sys
import tarfile
import time

from engineering.design_search.storage import atomic_immutable
from engineering.vehicle_optimisation import hvac
from engineering.halbach_scaling import candidates, screen

from . import ROOT, FLAGS

SCHEMA = 'osr-thermal-closure/1'
SELECTED_RECIPE = 'HS-V012-W40-H8-P1-Y00-D'
PARENT = 'docs/design-engine/halbach-scaling'
MAX_SECONDS = 120.
REFERENCES = dict(
    konvekta=dict(url=hvac.REFERENCES['konvekta']['url'],
        document_url=hvac.REFERENCES['konvekta']['datasheet'],
        document_sha256='43556f4d5324ccf32a924c19c5f4f19f8cdc2d81687f4867a07fd8717b46c484',
        reviewed_date='2026-10-26', document='UltraLight 500/600/700 EM Gen3, 10/2021, page 2',
        scope='Bus electric-compressor package. 50 C performance limit is not a cooling, COP or fresh-air rating there.'),
    diab=dict(url='https://diab-media.azureedge.net/eyajkrhd/diab-divinycell-h-may-2026-rev26-si.pdf',
        manufacturer_page='https://www.diabgroup.com/certificates-datasheets/',
        document_sha256='d4a108dd3be35da9fef378037ddbe92133a7e24b991f5098a3ed0a2882c6e4a4',
        reviewed_date='2026-10-26', document='Divinycell H rev26 SI May 2026, pages 1-2',
        scope='H80 nominal density 80, supplied range 67-87 kg/m3; conductivity .031 W/m/K at20 C; continuous upper temperature70 C. Railway fire/joints/hot loaded panel not qualified.'),
    glazing=deepcopy(hvac.REFERENCES['glazing']))


def encoded(value):
    return (json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False)+'\n').encode()


def identity(value):return sha256(encoded(value)).hexdigest()


def _num(value,name,minimum=None):
    if type(value) not in (int,float) or not math.isfinite(value) or minimum is not None and value<minimum:
        raise ValueError('finite bounded '+name+' required')
    return float(value)


def _source_name(path):
    parts=Path(path).resolve().parts
    return '/'.join(parts[parts.index('engineering'):])


def sources(root=ROOT):
    root=Path(root).resolve();result=hvac.source_inputs(root)['local_sha256']
    paths=set(Path(__file__).parent.rglob('*.py'))|set(candidates.source_paths())
    paths.add(Path(screen.__file__))
    from engineering.design_search import storage
    paths.add(Path(storage.__file__))
    for path in sorted(paths):
        if path.is_symlink():raise ValueError('ordinary implementation sources required')
        name=_source_name(path);digest=sha256(path.read_bytes()).hexdigest()
        if name in result and result[name]!=digest:raise ValueError('executing and retained sources disagree: '+name)
        result[name]=digest
    for name in ('manifest.json','comparison.json','operating.json','transverse-artifacts.tar.gz'):
        path=root/PARENT/name
        if not path.is_file() or path.is_symlink():raise ValueError('ordinary retained parent evidence required')
        result[path.relative_to(root).as_posix()]=sha256(path.read_bytes()).hexdigest()
    return dict(sorted(result.items()))


def passive_options():
    """Count thermal-envelope additions, retaining unweighed interfaces."""
    roof=17.*2.65;wall=2*17.*2.8+2*2.65*2.8-4*1.4*2.1-24.
    rows=[]
    for glazing,absorptivity,core,recovery in itertools.product((.82,.55),(.5,.2),(.04,.06),(False,True)):
        delta=core-.04;volume=(wall+roof)*delta
        stock=[]
        if delta:
            stock.append(dict(id='added-upper-H80-core',role='thermal-core-increment',
                roof_area_m2=roof,net_opaque_wall_end_area_m2=wall,thickness_m=delta,
                volume_m3=volume,density_nominal_kg_m3=80.,density_range_kg_m3=[67.,87.],
                nominal_material_mass_kg=volume*80.,material_mass_range_kg=[volume*67.,volume*87.],
                source_id='diab',geometry_scope='Planar thermal-envelope increment; not a native installed structural panel',
                bonds_edges_fire_layers_cut_waste_and_interfaces_mass_kg=None))
        if absorptivity==.2:
            stock.append(dict(id='reflective-roof-finish',area_m2=roof,absorptivity_hypothesis=.2,
                thickness_m=None,mass_kg=None,removed_original_finish_mass_kg=None,
                basis='Target optical property; weathering, coating, substrate and installed mass unidentified'))
        if glazing==.55:
            stock.append(dict(id='solar-control-glazing-change',area_m2=28.,solar_factor_hypothesis=.55,
                mass_change_kg=None,basis='Retained rounded optical hypothesis; side/door construction and interfaces not a correlated rated product'))
        if recovery:
            stock.append(dict(id='enthalpy-recovery-device-and-ducts',mass_kg=None,
                sensible_effectiveness_hypothesis=.6,latent_effectiveness_hypothesis=.4,
                total_extra_air_pressure_Pa=200.,fan_efficiency_hypothesis=.5,
                basis='Declared total air-path pressure and effectiveness, not a sourced heat exchanger or free mass'))
        row=dict(glazing_solar_factor=glazing,roof_absorptivity=absorptivity,upper_core_m=core,
            upper_core_lambda_W_mK=.031,recovery=recovery,stock_additions=stock,
            additional_core_nominal_kg=volume*80.,additional_core_density_range_kg=[volume*67.,volume*87.],
            complete_additional_installed_mass_kg=None if stock else 0.,
            structural_properties_and_hot_conductivity_qualified=False,**FLAGS)
        row['thermal_feature_id']=identity(row);rows.append(row)
    return rows


def packages():
    """Exact unit quantities; external installation is not a transferred band."""
    parent=next(c for c in hvac.candidates() if c['id']=='bus-ul700-electric-two')
    rows=[]
    for count in (2,3,5):
        row=dict(family='Konvekta UL700 EM Gen3 quantity proposal',units_per_car=count,
            source_id='konvekta',catalogue_nominal_unit_kWthermal=33.,
            catalogue_nominal_total_kWthermal=33.*count,
            catalogue_hardware_kg=count*192.,unit_envelope_m=[2.655,2.083,.357],
            projected_roof_area_m2=count*2.655*2.083,
            low_voltage_V=26.,low_voltage_regular_current_A_each=20.,low_voltage_maximum_current_A_each=90.,
            catalogue_regular_low_voltage_kWe=.52*count,catalogue_maximum_low_voltage_kWe=2.34*count,
            compressor_supply='400 V AC',compressor_maximum_current_A_each=24.,compressor_start_current_A_each=120.,
            compressor_phase_count=None,power_factor=None,compressor_real_kWe=None,
            available_50C_kWthermal=None,actual_50C_COP=None,actual_50C_electric_kWe=None,
            catalogue_evaporator_flow_m3_h=count*7080.,rated_fresh_air_at_50C_m3_h=None,
            catalogue_ambient_performance_limit_C=50.,nominal_capacity_rating_conditions=None,
            external_mounts_ducts_supply_wiring_adaptation_mass_kg=None,
            installed_HVAC_mass_kg=None,roof_fit_access_CG_and_condenser_recirculation_qualified=False,
            electrical_scope='26 V draw excludes 400 V compressor. Current and voltage do not establish real compressor power or starting demand.',
            source_parent_candidate_id=parent['id'],**FLAGS)
        row['package_candidate_id']=identity(row);rows.append(row)
    return rows


def roof_core_screen(load):
    """Split the retained steady1D envelope resistances to screen hot core.

    The .17 m2K/W total film resistance is inherited. Outside film1/h and
    2mm/.3 W/m/K outer skin are explicit; core hot strength remains unknown.
    """
    s=load['scenario'];area=17.*2.65;q=load['sensible_components_W']['roof']/area
    outer_film=1/s['outside_film_W_m2K'];outer_skin=.002/.3
    if outer_film>=.17:raise ValueError('outside film exceeds the retained total film resistance')
    temperature=load['roof_solair_temperature_C']-q*(outer_film+outer_skin)
    return dict(roof_heat_flux_W_m2=q,outer_core_face_C=temperature,
        continuous_material_temperature_limit_C=70.,source_id='diab',
        necessary_temperature_screen='pass' if -200<=temperature<=70 else 'fail',
        model='Steady1D planar resistance split; .17 total films, 2mm outer GFRP at.3 W/m/K',
        heat_distortion_temperature_used_as_continuous_allowable=False,
        actual_panel_hot_strength_fire_bridges_weathering_and_temperature_validated=False,**FLAGS)


def capacity_screen(package,load,*,failed_cooling_units=0):
    count=package['units_per_car']
    if type(failed_cooling_units) is not int or not 0<=failed_cooling_units<count:raise ValueError('valid unavailable cooling-unit count required')
    available=count-failed_cooling_units;nominal=33.*available;demand=load['total_kWthermal']
    row=dict(package_candidate_id=package['package_candidate_id'],load_id=load['load_id'],
        installed_units=count,unavailable_cooling_units=failed_cooling_units,available_cooling_units=available,
        required_kWthermal=demand,available_nameplate_sum_kWthermal=nominal,
        required_capacity_fraction_of_nominal=demand/nominal,
        required_50C_capacity_kWthermal_each=demand/available,
        nominal_capacity_margin_kWthermal=nominal-demand,
        nominal_capacity_comparison='pass' if nominal>=demand else 'fail',
        actual_50C_capacity_screen='unknown',actual_50C_capacity_kWthermal=None,
        required_fresh_air_cabin_m3_h=load['fresh_air_cabin_m3_h'],delivered_fresh_air_at_50C_m3_h=None,
        complete_HVAC_electric_kWe=None,compressor_input_kWe=None,
        specified_low_voltage_scenario_kWe=load['specified_low_voltage_scenario_kWe'],
        recovery_fan_scenario_kWe=load['recovery_fan_extra_kWe'],
        nominal_sensible_latent_split_and_return_air_correlation_known=False,
        failed_unit_air_path_and_ventilation_qualified=False,
        failure_scope='Cooling path unavailable; all installed low-voltage auxiliary draws are retained as a heat/power scenario. This is not full failed-unit operation.',
        **FLAGS)
    row['evaluation_id']=identity(row);return row


def hvac_campaign():
    features=passive_options();options=packages();loads=[];comparisons=[];physical=[]
    duties=[dict(id='AW2-dry-door30',passengers=120,outdoor_RH=.15,door_open_s=30.),
        dict(id='AW3-humid-stationary-closed',passengers=160,outdoor_RH=.30,doors_open=0,door_open_s=0.),
        dict(id='AW3-humid-door30',passengers=160,outdoor_RH=.30,door_open_s=30.),
        dict(id='AW3-humid-door60',passengers=160,outdoor_RH=.30,door_open_s=60.)]
    for feature,package in itertools.product(features,options):
        physical_id=identity(dict(feature_id=feature['thermal_feature_id'],package_id=package['package_candidate_id'],context=hvac.CONTEXT))
        physical.append(dict(component_candidate_id=physical_id,thermal_feature_id=feature['thermal_feature_id'],
            package_candidate_id=package['package_candidate_id'],complete_vehicle_candidate_id=None,**FLAGS))
        for duty,mode,fraction in itertools.product(duties,('catalogue-regular','catalogue-maximum'),(0.,1.)):
            aux=package['catalogue_regular_low_voltage_kWe'] if mode=='catalogue-regular' else package['catalogue_maximum_low_voltage_kWe']
            scenario=hvac.default_scenario(name=duty['id'],outdoor_C=50.,solar_factor=feature['glazing_solar_factor'],
                roof_absorptivity=feature['roof_absorptivity'],upper_core_m=feature['upper_core_m'],
                unit_blower_heat_W=aux*1000*fraction,
                sensible_recovery_effectiveness=.6 if feature['recovery'] else 0.,
                latent_recovery_effectiveness=.4 if feature['recovery'] else 0.,
                recovery_total_pressure_Pa=200. if feature['recovery'] else 0.,
                **{k:v for k,v in duty.items() if k!='id'})
            result=hvac.heat_load(scenario)
            result.update(component_candidate_id=physical_id,thermal_feature_id=feature['thermal_feature_id'],
                package_candidate_id=package['package_candidate_id'],low_voltage_draw_mode=mode,
                low_voltage_heat_fraction_into_cabin=fraction,specified_low_voltage_scenario_kWe=aux,
                actual_HVAC_electric_kWe=None,blower_heat_fraction_identified=False,
                declared_COP_scenario_is_not_manufacturer_input=True)
            result['core_material_temperature']=roof_core_screen(result)
            result['load_id']=identity(result);loads.append(result)
            comparisons.extend(capacity_screen(package,result,failed_cooling_units=n) for n in (0,1))
    return dict(thermal_features=features,packages=options,component_candidates=physical,loads=loads,comparisons=comparisons,
        runtime_budget_s=MAX_SECONDS,actual_50C_rating_known=False,
        actual_fresh_air_rating_known=False,vehicle_structural_mass_is_an_HVAC_load_input=False,
        uncertainty_scope='Effective door exchange, weather, humid air, optical properties, films, hot core conductivity, fan heat and recovery are declared scenarios; not calibrated worst-case confidence bounds.',**FLAGS)


def _read_member(archive,name):
    with tarfile.open(archive,'r:gz') as stream:
        all_members=stream.getmembers()
        if len(all_members)>5000:raise ValueError('bounded parent archive inventory required')
        members=[m for m in all_members if m.name==name]
        if len(members)!=1 or not members[0].isfile() or not 0<members[0].size<32*1024**2:
            raise ValueError('one ordinary bounded retained record required')
        return stream.extractfile(members[0]).read()


def parent_inputs(root=ROOT):
    root=Path(root);directory=root/PARENT
    manifest=json.loads((directory/'manifest.json').read_bytes())
    if manifest.get('manifest_id')!=identity({k:v for k,v in manifest.items() if k!='manifest_id'}):raise ValueError('parent manifest identity differs')
    if any(manifest.get(k) is not False for k in ('configuration_adopted','engineering_accepted','physical_accepted')):
        raise ValueError('unaccepted source-bound parent study required')
    for name in ('comparison.json','operating.json','transverse-artifacts.tar.gz'):
        if sha256((directory/name).read_bytes()).hexdigest()!=manifest['files_sha256'][name]:raise ValueError('parent evidence payload differs')
    comparison=json.loads((directory/'comparison.json').read_bytes())
    if comparison['study_id']!=manifest['study_id'] or comparison['study_id']!=identity({k:v for k,v in comparison.items() if k!='study_id'}):
        raise ValueError('parent comparison identity differs')
    raw_bytes=_read_member(directory/'transverse-artifacts.tar.gz','transverse/result.json')
    raw=json.loads(raw_bytes)
    receipt=json.loads(_read_member(directory/'transverse-artifacts.tar.gz','transverse/manifest.json'))
    if sha256(raw_bytes).hexdigest()!=receipt['files_sha256']['result.json']:raise ValueError('retained transverse record differs')
    op=json.loads((directory/'operating.json').read_bytes())
    bundle=next(b for b in candidates.candidates(root) if b['recipe_id']==SELECTED_RECIPE)
    selected=next(s for s in comparison['selection']['selected'] if s['purpose']=='controlled')
    if selected['magnet_component_id']!=bundle['physical_id']:raise ValueError('controlled parent candidate changed')
    composed=next(r for r in comparison['comparisons'] if r['comparison_id']==selected['comparison_id'])
    body=next(b for b in comparison['vehicle_candidates'] if b['candidate_id']==selected['body_candidate_id'])
    if body['candidate_id']!=identity(body['physical_definition']) or body['bundle_sha256']!=identity({k:v for k,v in body.items() if k!='bundle_sha256'}):
        raise ValueError('parent body definition identity differs')
    if composed['body_candidate_id']!=body['candidate_id']:raise ValueError('parent composition/body identity differs')
    points={}
    for point in [*raw['authority_rows'],*[r['result'] for r in op['rows']]]:
        if point['candidate_id']!=bundle['physical_id'] or point.get('execution_status')!='completed':continue
        execution=point.get('execution',{});p=point['raw_result']['operating_point']
        currents=list(p['currents_A'].values());current=0. if not currents else currents[0]
        if p['temperature_C']!=80. or p['gap_m'] not in (.012,.044) or current not in (-15.,0.,15.):continue
        screen.validate_point(point,bundle,root)
        if execution.get('returncode')!=0 or execution.get('timed_out') is not False or point['raw_result']['numerical_status']!='converged':continue
        if currents and (set(p['currents_A'])!={c['id'] for c in bundle['circuits']} or len(set(currents))!=1):raise ValueError('common-current sample required')
        key=(p['gap_m'],current)
        if key in points and points[key]['raw_result']['result_id']!=point['raw_result']['result_id']:raise ValueError('inconsistent duplicate field state')
        points[key]=point
    if set(points)!={(g,i) for g in (.012,.044) for i in (-15.,0.,15.)}:raise ValueError('six exact retained signed-current samples required')
    return bundle,composed,body,points,comparison['study_id']


def matches_parent_package(package,parent):
    """Match only published package topology; never a complete equipped body."""
    return (parent is not None and package['units_per_car']==parent['units_per_car']
        and package['source_id']==parent['source_id']
        and package['unit_envelope_m']==parent['package_unit_envelope_m']
        and parent['package_unit_mass_range_kg']==[192.,192.]
        and parent['package_hardware_mass_range_kg_per_car']==[package['catalogue_hardware_kg']]*2
        and parent['package_capacity_kWthermal']==[package['catalogue_nominal_total_kWthermal']]*2)


def linear_rl_step(*,initial_A,voltage_V,resistance_ohm,inductance_H,duration_s):
    """Exact fixed-gap linear RL diagnostic with signed energy exchange."""
    initial=_num(initial_A,'initial current');voltage=_num(voltage_V,'voltage')
    R=_num(resistance_ohm,'resistance',1e-12);L=_num(inductance_H,'inductance',1e-12);dt=_num(duration_s,'duration',1e-12)
    tau=L/R;x=dt/tau;increment=voltage/R-initial
    # Integrate i=i0+increment*(1-exp(-t/tau)). Series retain the O(t^3)
    # heat of an initially empty inductor instead of subtracting large terms.
    if x<1e-3:
        first=tau*math.fsum((-1.)**n*x**n/math.factorial(n) for n in range(2,11))
        second=tau*math.fsum((-1.)**n*(2.-2.**(n-1))*x**n/math.factorial(n) for n in range(3,12))
    else:
        first=tau*(x+math.expm1(-x))
        second=tau*(x+2*math.expm1(-x)-.5*math.expm1(-2*x))
    end=initial+increment*(-math.expm1(-x))
    charge=initial*dt+increment*first
    integral_i2=initial**2*dt+2*initial*increment*first+increment**2*second
    heat=R*integral_i2;energy=voltage*charge;stored=.5*L*(end-initial)*(end+initial)
    return dict(initial_A=initial,voltage_V=voltage,resistance_ohm=R,inductance_H=L,duration_s=dt,
        final_A=end,copper_heat_J=heat,net_electrical_input_J=energy,inductor_energy_change_J=stored,
        energy_residual_J=energy-heat-stored,model='Constant R/L fixed-gap generalized common-current port; PM-linked flux and motion fixed',
        actual_current_control_or_voltage_qualified=False,**FLAGS)


def adiabatic_copper(*,initial_C,current_A,R20_ohm,alpha_per_K,capacity_J_K,duration_s):
    """Exact nominal copper R(T) heat-up with zero heat rejection.

    This is a deliberately hypothetical thermal boundary, not a measured bound
    on installed temperatures, gradients or heat arriving from other equipment.
    """
    initial=_num(initial_C,'initial temperature');I=_num(current_A,'current');R=_num(R20_ohm,'R20',1e-12)
    alpha=_num(alpha_per_K,'resistance coefficient',1e-12);C=_num(capacity_J_K,'capacity',1e-12);dt=_num(duration_s,'duration',0.)
    theta=1+alpha*(initial-20.)
    if theta<=0:raise ValueError('positive temperature-dependent resistance required')
    end=20.+(theta*math.exp(alpha*I**2*R*dt/C)-1)/alpha
    return dict(initial_C=initial,current_A=I,duration_s=dt,final_C=end,
        copper_capacity_J_K=C,copper_heat_and_stored_J=C*(end-initial),rejected_heat_J=0.,
        thermal_boundary='No heat rejection, uniform copper only, constant current, nominal linear copper resistance',
        force_credit_beyond_retained_80C_state=False,installed_temperature_prediction=False,**FLAGS)


def winding_study(root=ROOT):
    bundle,composed,body,points,parent_id=parent_inputs(root)
    copper=bundle['materials']['copper'];circuits=bundle['circuits']
    R20=sum(c['resistance_20c_ohm'] for c in circuits);alpha=copper['resistance_temperature_coefficient_per_k']
    mass=sum(c['copper_mass_kg'] for c in circuits);capacity=mass*copper['specific_heat_j_kg_k']
    for c in circuits:
        expected=copper['resistivity_20c_ohm_m']*c['conductor_length_m']/c['conductor_area_m2']
        if not math.isclose(c['resistance_20c_ohm'],expected,rel_tol=1e-12):raise ValueError('coil stock/resistance mismatch')
    R80=R20*(1+alpha*60.);heat=15**2*R80
    cases=[]
    for gap in (.012,.044):
        values=[points[(gap,i)] for i in (-15.,0.,15.)]
        flux=[sum(p['raw_result']['flux_linkage_Wb_turn'][c['id']] for c in circuits) for p in values]
        L=(flux[2]-flux[0])/30.
        if not L>0:raise ValueError('positive secant inductance required for the declared linear RL diagnostic')
        force=[p['comparison']['conservative_contour_Fz_N'] for p in values]
        rows=[]
        for name,kg in [('empty',composed['comparison_empty_kg_per_car']),('AW3',composed['comparison_aw3_kg_per_car'])]:
            mean=kg*9.80665/24
            rows.append(dict(load_case=name,comparison_mass_kg_per_car=kg,mean_weight_N_per_module=mean,
                sampled_force_brackets_weight=min(force)<=mean<=max(force),
                scope='Only three discrete 2D current samples; no interpolation, stable equilibrium or control reserve qualification'))
        cases.append(dict(gap_m=gap,temperature_C=80.,candidate_id=bundle['physical_id'],
            physical_current_circuits=[c['id'] for c in circuits],common_currents_A=[-15.,0.,15.],
            flux_linkage_common_port_Wb_turn=flux,conservative_Fz_N=force,
            force_current_secant_N_per_A=(force[2]-force[0])/30.,common_port_secant_L_H=L,
            sample_evaluation_ids=[p['evaluation_id'] for p in values],
            sample_result_ids=[p['raw_result']['result_id'] for p in values],
            differential_inductance_convergence_and_3D_correlation_known=False,
            parent_body_comparison_id=composed['comparison_id'],load_comparisons=rows,
            linear_RL_voltage_sensitivities=[linear_rl_step(initial_A=-15.,voltage_V=v,resistance_ohm=R80,inductance_H=L,duration_s=.010) for v in (24.,48.,96.)],
            declared_10ms_target_is_not_stability_requirement=True,**FLAGS))
    return dict(candidate_id=bundle['physical_id'],parent_study_id=parent_id,
        parent_composition_id=composed['composition_id'],parent_body_candidate_id=body['candidate_id'],
        parent_body_name=body['name'],parent_HVAC=deepcopy(body['HVAC']),
        copper_material_mass_kg_per_module=mass,
        copper_capacity_nominal_J_K_per_module=capacity,R20_known_copper_ohm_per_module=R20,
        R80_known_copper_ohm_per_module=R80,copper_DC_loss_15A_80C_W_per_module=heat,
        copper_DC_loss_15A_80C_kW_per_car=24*heat/1000.,
        copper_DC_loss_15A_80C_kW_per_train=6*24*heat/1000.,
        per_coil_DC_voltage_15A_80C_V=[15*c['resistance_20c_ohm']*(1+alpha*60) for c in circuits],
        generalized_common_port_DC_voltage_15A_80C_V=15*R80,
        necessary_conductance_for_80C_copper_50C_ambient_W_K_per_module=heat/30.,
        actual_thermal_conductance_W_K=None,thermal_equilibrium_C=None,
        electrical_lead_converter_bus_losses_and_motion_emf=None,actual_drive_bus_voltage_V=None,
        declared_current_density_limit_A_per_mm2=3.75,sampled_15A_conductor_current_density_A_per_mm2=3.75,
        dc_density_screen_pass=True,continuous_thermal_screen='unknown',fast_stabilization_screen='unknown',
        generalized_port_scope='Both physical circuits carry the same numerical I; summed R and flux describe an energy-equivalent coordinate, not a selected wired series topology.',
        samples=cases,adiabatic_copper_diagnostics=[adiabatic_copper(initial_C=t,current_A=15.,R20_ohm=R20,
            alpha_per_K=alpha,capacity_J_K=capacity,duration_s=d) for t,d in itertools.product((50.,80.),(60.,180.,300.))],
        missing=['Measured nonlinear inductance matrix and mutual coupling','3D force/current/gap/temperature derivatives and damping',
            'Actual driver voltage/current/bandwidth and protection','Winding insulation limits and hot-spot gradients',
            'Measured heat rejection and repeated operating duty','Leadouts, converters, cooling and protection installed stock'],**FLAGS)


def evaluate(root=ROOT):
    started=time.monotonic();before=sources(root)
    climate=hvac_campaign();winding=winding_study(root)
    climate['parent_package_binding']=dict(parent_body_candidate_id=winding['parent_body_candidate_id'],
        parent_composition_id=winding['parent_composition_id'],parent_HVAC_units_per_car=winding['parent_HVAC']['units_per_car'],
        matching_package_candidate_ids=[p['package_candidate_id'] for p in climate['packages'] if matches_parent_package(p,winding['parent_HVAC'])],
        scope='Matches unit count, source, envelope, hardware mass and nominal capacity only. Passive changes require a newly composed complete vehicle; installation remains unknown.',
        complete_revised_vehicle_candidate_id=None,full_revised_vehicle_composition_required=True,**FLAGS)
    if time.monotonic()-started>MAX_SECONDS:raise TimeoutError('bounded ordinary thermal study deadline exceeded')
    if sources(root)!=before:raise ValueError('sources changed during thermal evaluation')
    counts=dict(thermal_feature_options=len(climate['thermal_features']),package_quantities=len(climate['packages']),
        thermal_component_candidates=len(climate['component_candidates']),heat_load_scenarios=len(climate['loads']),
        nameplate_and_N_minus_one_comparisons=len(climate['comparisons']),
        nominal_capacity_comparison_failures=sum(c['nominal_capacity_comparison']=='fail' for c in climate['comparisons']),
        hot_core_temperature_scenario_failures=sum(l['core_material_temperature']['necessary_temperature_screen']=='fail' for l in climate['loads']),
        actual_50C_capacity_qualifications=0,retained_signed_current_samples=6,new_FEM_solves=0)
    report=dict(schema=SCHEMA,context=deepcopy(hvac.CONTEXT),source_sha256=before,primary_references=deepcopy(REFERENCES),
        execution='completed',evidence_maturity='Analytical engineering scenarios plus retained uncorrelated transverse FEM samples',
        counts=counts,hvac=climate,support_winding=winding,
        readiness=dict(HVAC_50C_capacity='unknown',HVAC_failed_unit_air_quality='unknown',
            electrical_services_total='unknown',support_thermal_duty='unknown',support_current_control='unknown',
            thermal_material_necessary_scenarios='fail' if counts['hot_core_temperature_scenario_failures'] else 'unknown',
            integrated_vehicle='unknown'),
        next_measurements=['Correlated UL700 capacity/sensible/latent/electrical maps at50C and actual fresh-air pressure',
            'Occupied-car door exchange and return-air conditions','Roof skin/core temperatures and weathered optical measurements',
            'Heat-recovery efficiency, pressure, hygiene and installed mass','Coil R/L matrix and voltage/current/heat-rejection duty'],
        numerical_environment=dict(python=sys.version,platform=platform.platform()),**FLAGS)
    report['evaluation_id']=identity(report);return report


def _unaccepted(value):
    if isinstance(value,dict):
        for name,child in value.items():
            if name in set(FLAGS)|{'physical_release','manufacturing_release','design_complete','stable_hover_established'} and child is not False:
                raise ValueError('research cannot assert acceptance: '+name)
            _unaccepted(child)
    elif isinstance(value,list):
        for child in value:_unaccepted(child)


def run(output,root=ROOT):
    value=evaluate(root);_unaccepted(value);output=Path(output)
    output.mkdir(parents=True,exist_ok=False)
    raw=encoded(value);atomic_immutable(output/'result.json',raw)
    manifest=dict(schema=SCHEMA+'/publication',evaluation_id=value['evaluation_id'],source_sha256=value['source_sha256'],
        files_sha256={'result.json':sha256(raw).hexdigest()},**FLAGS)
    manifest['manifest_id']=identity(manifest);atomic_immutable(output/'manifest.json',encoded(manifest))
    return dict(current=True,evaluation_id=value['evaluation_id'],counts=value['counts'],physical_accepted=False)


def verify(output,root=ROOT):
    output=Path(output)
    if output.is_symlink() or any(p.is_symlink() or not p.is_file() for p in output.iterdir()):raise ValueError('ordinary retained publication files required')
    if {p.name for p in output.iterdir()}!={'result.json','manifest.json'}:raise ValueError('exact publication file inventory required')
    value=json.loads((output/'result.json').read_bytes());manifest=json.loads((output/'manifest.json').read_bytes())
    _unaccepted(value);_unaccepted(manifest)
    if manifest.get('schema')!=SCHEMA+'/publication' or manifest.get('manifest_id')!=identity({k:v for k,v in manifest.items() if k!='manifest_id'}):raise ValueError('manifest identity differs')
    if manifest['files_sha256']!={'result.json':sha256((output/'result.json').read_bytes()).hexdigest()}:raise ValueError('publication payload differs')
    if value['evaluation_id']!=identity({k:v for k,v in value.items() if k!='evaluation_id'}) or manifest['evaluation_id']!=value['evaluation_id']:raise ValueError('evaluation identity differs')
    fresh=evaluate(root)
    if encoded(fresh)!=encoded(value) or manifest['source_sha256']!=fresh['source_sha256']:raise ValueError('derived result/current source differs')
    return dict(current=True,evaluation_id=value['evaluation_id'],counts=value['counts'],physical_accepted=False)
