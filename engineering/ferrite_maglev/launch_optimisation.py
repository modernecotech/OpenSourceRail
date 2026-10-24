"""Finite independently energized LSM groups: equal-service loss/lifetime sweep.

This is a computational winding/converter hypothesis, not an accepted motor map.
All installed converters, inactive control power, maintenance and renewal count.
"""
from hashlib import sha256
from pathlib import Path
import gzip
import json
import math
import tomllib
import numpy as np
from . import corridor, drive_design, model, pilot_product as product, station

ROOT=model.ROOT
INPUT=Path(__file__).with_name('launch-optimisation.toml')
OUTPUT=ROOT/'docs/design-engine/ferrite-maglev/launch-optimisation'
TEST=ROOT/'engineering/analysis/tests/test_ferrite_maglev_launch_optimisation.py'
SCHEMA='osr-launch-optimisation/1'
FLAGS=product.FLAGS
def encoded(v):return product.encoded(v)
def digest(b):return sha256(b).hexdigest()
def source_paths():return sorted({Path(__file__),INPUT,TEST,*product.source_paths(),Path(corridor.__file__),corridor.INPUT})
def sources():return {p.relative_to(ROOT).as_posix():digest(p.read_bytes()) for p in source_paths()}
def load():
    a=tomllib.loads(INPUT.read_text())
    if a['schema']!='osr-launch-optimisation-input/1' or a['groups_per_direction']!=[2,4,7,14,28,70] or a['conductor_areas_mm2']!=[250.,350.,500.] or a['turns']!=[1,2] or a['dc_buses_v']!=[1800.,2400.,3300.]:raise ValueError('explicit bounded launch alternatives required')
    for k,v in a.items():
        if type(v) in (int,float) and (not math.isfinite(v) or v<=0):raise ValueError('finite positive launch assumption '+k)
    if a['regeneration_reuse_fraction']>1 or a['discount_fraction']>=1:raise ValueError('bounded lifecycle fractions required')
    return a

def reference_profile(profile_id='urban',configuration_id='baghdad-30kwh-aw3'):
    if profile_id not in {'urban','suburban'}:raise ValueError('named urban or suburban profile required')
    cfg=product.configuration_profile(configuration_id);a=corridor.load()
    return corridor.profile(distance_m=a[profile_id+'_reference_distance_m'],runtime_s=a[profile_id+'_reference_runtime_s'],cars=6,car_mass_kg=cfg['controlled_aw3_kg'],mode=profile_id)

def idle_control_energy(*,physical_station_groups,annual_mainline_legs,runtime_s,stations=1,trip_groups=None):
    """Annual base load less exactly the idle energy already inside trip DC.

    Two terminal events in each trip represent one two-direction station. This
    explicit reconciliation avoids counting the same idle watts twice.
    """
    if type(physical_station_groups) is not int or type(stations) is not int or min(physical_station_groups,stations)<1:raise ValueError('positive installed counts required')
    trip_groups=physical_station_groups if trip_groups is None else trip_groups
    if type(trip_groups) is not int or trip_groups<0:raise ValueError('nonnegative trip group count required')
    if any(type(x) not in (int,float) or not math.isfinite(x) or x<0 for x in (annual_mainline_legs,runtime_s)):raise ValueError('finite nonnegative actual duty required')
    watts=load()['idle_group_control_w'];full=stations*physical_station_groups*watts*8760/1000.
    included=annual_mainline_legs*runtime_s*trip_groups*watts/3600000.
    return dict(full_year_station_idle_kwh=full,idle_already_inside_trip_dc_kwh=included,additional_idle_kwh=max(0.,full-included),
        duplicated_trip_idle_credit_kwh=max(0.,included-full),annual_idle_reconciliation_kwh=full-included,
        installed_groups=stations*physical_station_groups,groups_inside_each_trip=trip_groups,
        included_idle_exceeds_calendar_budget=included>full,
        scope='Replace trip-allocated constant35W/group with one actual installed calendar base load. A signed accounting correction removes overlapping trip allocations only; copper, mechanical and active incremental losses receive no credit.')

def group_geometry(profile,groups_per_direction):
    """Whole2.5m cassettes; booster is a separately counted physical asset."""
    a=corridor.load();rows=[];cassette=drive_design.load()['launch']['cassette_m']
    for zone in corridor._zones(profile,a):
        count=round(zone['length_m']/cassette)
        if not math.isclose(count*cassette,zone['length_m']):raise ValueError('whole mechanical cassettes required')
        # Match segmentation density and partition integer cassette populations.
        groups=min(count,max(1,round(groups_per_direction*zone['length_m']/350.)))
        for j,indices in enumerate(np.array_split(np.arange(count),groups)):
            start=zone['start_m']+int(indices[0])*cassette;end=start+len(indices)*cassette
            rows.append(dict(id=f'{zone["id"]}/group-{j:02d}',zone_id=zone['id'],start_m=start,end_m=end,length_m=end-start,cassettes_per_face=len(indices)))
    return rows

def loss_model(profile,*,groups_per_direction=2,conductor_area_mm2=350.,turns=1,dc_bus_v=2400.,configuration_id='baghdad-30kwh-aw3',record_trace=False,_context=None):
    a,d,cfg= (load(),drive_design.load(),product.configuration_profile(configuration_id)) if _context is None else _context
    l=d['launch'];m=d['material']
    if not profile.get('study_pass') or profile['inputs']['cars']!=6:raise ValueError('feasible explicit six-car motion profile required')
    if groups_per_direction not in a['groups_per_direction'] or conductor_area_mm2 not in a['conductor_areas_mm2'] or turns not in a['turns'] or dc_bus_v not in a['dc_buses_v']:raise ValueError('bounded loss-model candidate required')
    s=drive_design.sampled(profile);time=s['times'];x=s['position'];speed=s['speed'];force=s['force'];groups=group_geometry(profile,groups_per_direction)
    v=station.load()['vehicle'];band=v['magnetic_band_m_per_car'];pitch=v['body_length_m']+v['coupling_gap_m'];bands=np.array([[-(v['body_length_m']-band)/2-band-j*pitch,-(v['body_length_m']-band)/2-j*pitch] for j in range(6)])
    flux=l['useful_fundamental_flux_t']*2*l['pole_pitch_m']/math.pi*l['face_width_m'];k=math.pi/l['pole_pitch_m'];omega=k*speed
    psi=[];resistance=[];inductance=[];copper=[]
    wire=drive_design.copper(d,turns,2*(l['face_width_m']+l['pole_pitch_m']),conductor_area_mm2,l['hot_copper_temperature_c'])
    for g in groups:
        ov=station._overlap(x,bands,g['start_m'],g['end_m']);mask=s['zone']==g['zone_id']
        psi.append(np.where(mask,ov*l['faces']/l['cassette_m']*5*turns*flux,0.))
        coils_phase=g['cassettes_per_face']*l['faces']*5
        resistance.append(wire['resistance_hot_ohm']*coils_phase)
        inductance.append(a['inductance_one_turn_175m_h']*turns**2*g['length_m']/175.)
        copper.append(wire['copper_kg']*g['cassettes_per_face']*l['faces']*15)
    psi=np.array(psi);R=np.array(resistance);L=np.array(inductance);K=1.5*k*psi
    # Analytic constrained sharing before current/voltage limits: this minimizes
    # sum(1.5*R*Iq²) while reproducing the demanded force. A limit is a rejection,
    # never an undocumented post-hoc clipping that retains the ideal trajectory.
    denominator=np.sum(K*K/R[:,None],axis=0)
    current=np.divide(force[None,:]*K/R[:,None],denominator[None,:],out=np.zeros_like(K),where=denominator[None,:]>1e-12)
    active=psi>1e-9;uncovered=(np.abs(force)>1e-6)&(denominator<=1e-12)
    di=np.gradient(current,time,axis=1);dpsi=np.gradient(psi,time,axis=1)
    vd=dpsi-omega[None,:]*L[:,None]*current;vq=R[:,None]*current+L[:,None]*di+omega[None,:]*psi
    voltage=np.where(active,np.hypot(vd,vq),0.)
    # Current must decay at an enable edge. Keep the full derivative requirement;
    # group transitions are neither loss-free nor assumed instantaneous.
    copper_w=1.5*R[:,None]*current**2
    conduction=3*a['switch_drop_v']*np.abs(current)+1.5*a['switch_resistance_ohm']*current**2
    switching=6*a['switching_energy_j_per_amp']*np.abs(current)*a['pwm_hz']*(dc_bus_v/2400.)
    control=np.where(active,a['active_group_control_w'],a['idle_group_control_w'])
    converter_w=conduction+switching+control
    copper_j=np.trapezoid(copper_w,time,axis=1);converter_j=np.trapezoid(converter_w,time,axis=1)
    mechanical_w=force*speed;loss_w=np.sum(copper_w+converter_w,axis=0);dc_w=mechanical_w+loss_w
    # A local receiving resistor remains required. Reuse is a finance sensitivity
    # on available DC energy, not a claimed reversible grid connection.
    imported=float(np.trapezoid(np.maximum(dc_w,0.),time));returned=float(np.trapezoid(np.maximum(-dc_w,0.),time))
    realised_force=np.sum(K*current,axis=0);residual=float(np.max(np.abs(realised_force-force)))
    phase_limit=.95*dc_bus_v/math.sqrt(3);peak_current=float(np.max(np.abs(current)));peak_voltage=float(voltage.max())
    rise=np.array(copper_j)/(np.array(copper)*m['copper_specific_heat_j_kg_k'])
    limits=dict(overlap=not bool(uncovered.any()),current=peak_current<=a['maximum_phase_current_a'],voltage=peak_voltage<=phase_limit,
        adiabatic_temperature=float(rise.max())<=a['maximum_adiabatic_event_rise_c'],force_balance=residual<1e-6)
    # The station has both directions; the trip consumes one departure and one
    # arrival at different stations. Their combined winding stock equals one
    # two-direction station. Booster stock is counted separately below.
    terminal=[i for i,g in enumerate(groups) if g['zone_id']!='booster'];booster=[i for i,g in enumerate(groups) if g['zone_id']=='booster']
    converter_cost=[a['converter_base_usd']+a['converter_usd_per_amp']*float(np.abs(current[i]).max())+a['converter_usd_per_peak_kw']*float((1.5*voltage[i]*np.abs(current[i])).max())/1000. for i in range(len(groups))]
    noncopper_length=sum(g['length_m'] for g in groups)
    converter_capex=sum(converter_cost);copper_capex=sum(copper)*a['copper_finished_usd_per_kg'];fixed_capex=noncopper_length*a['stator_non_copper_usd_per_direction_m']+len(groups)*a['group_sensor_protection_usd']
    cooling=float(np.max(np.sum(copper_w+converter_w,axis=0)))/1000.*a['cooling_usd_per_peak_kw']
    capex=converter_capex+copper_capex+fixed_capex+cooling
    annual=2*a['reference_departures_per_direction_per_year'];net_kwh=(imported-a['regeneration_reuse_fraction']*returned)/3600000.
    # Every trip contains departure and arrival groups; annual stock contains
    # their equivalent two-direction station plus both booster directions.
    # Reconcile the constant idle baseline once even when trip windows overlap.
    standby=idle_control_energy(physical_station_groups=len(terminal)+2*len(booster),
        trip_groups=len(groups),annual_mainline_legs=annual,runtime_s=profile['inputs']['runtime_s'])
    idle_kwh=standby['annual_idle_reconciliation_kwh']
    annual_maint=converter_capex*a['annual_converter_maintenance_fraction']+(capex-converter_capex)*a['annual_other_maintenance_fraction']
    disc=a['discount_fraction'];annuity=sum((1+disc)**-year for year in range(1,a['life_years']+1))
    energy_cost=(annual*net_kwh+idle_kwh)*a['electricity_usd_per_kwh'];renewal=converter_capex/(1+disc)**a['converter_renewal_year']
    result=dict(schema='osr-launch-loss-model/1',configuration_sha256=cfg['configuration_sha256'],profile_sha256=digest(encoded(profile)),configuration_id=configuration_id,
        assessed_car_mass_kg=profile['inputs']['car_mass_kg'],controlled_mass_matches=math.isclose(profile['inputs']['car_mass_kg'],cfg['controlled_aw3_kg'],abs_tol=1e-6),
        candidate=dict(groups_per_direction=groups_per_direction,conductor_area_mm2=conductor_area_mm2,turns=turns,dc_bus_v=dc_bus_v),
        powered_groups=len(groups),station_converter_count=2*groups_per_direction,booster_converter_count=len(booster),
        winding_copper_kg=sum(copper),station_winding_copper_kg=sum(copper[i] for i in terminal),booster_copper_kg=sum(copper[i] for i in booster),
        copper_heat_kwh_per_trip=float(sum(copper_j))/3600000.,terminal_copper_heat_kwh_per_trip=float(sum(copper_j[i] for i in terminal))/3600000.,
        converter_heat_kwh_per_trip=float(sum(converter_j))/3600000.,dc_import_kwh=imported/3600000.,recoverable_to_dc_kwh=returned/3600000.,
        net_grid_kwh_at_assumed_reuse=net_kwh,regeneration_reuse_fraction=a['regeneration_reuse_fraction'],
        peak_current_a=peak_current,peak_phase_voltage_v=peak_voltage,phase_voltage_limit_v=phase_limit,
        peak_copper_w=float(np.sum(copper_w,axis=0).max()),peak_converter_loss_w=float(np.sum(converter_w,axis=0).max()),
        maximum_adiabatic_event_rise_c=float(rise.max()),force_balance_residual_n=residual,limits=limits,feasible=all(limits.values()),
        station_installed_allowance_usd=capex if not booster else None,all_profile_assets_allowance_usd=capex,converter_allowance_usd=converter_capex,
        lifecycle=dict(years=a['life_years'],discount_fraction=disc,reference_annual_train_passages=annual,annual_maintenance_allowance_usd=annual_maint,
            annual_energy_allowance_usd=energy_cost,additional_idle_control_kwh_per_year=standby['additional_idle_kwh'],idle_accounting=standby,converter_renewal_present_usd=renewal,
            installed_lifetime_cost_usd=capex+annuity*(annual_maint+energy_cost)+renewal),
        cost_is_quote=False,selected_for_city_defaults=False,qualified=False,**FLAGS)
    if record_trace:result['trace']=dict(time_s=time.tolist(),motor_force_n=force.tolist(),speed_m_s=speed.tolist(),groups=[dict(**g,R_ohm=R[i],L_h=L[i],psi_wb=psi[i].tolist(),q_a=current[i].tolist(),phase_voltage_v=voltage[i].tolist(),copper_w=copper_w[i].tolist()) for i,g in enumerate(groups)])
    return result

def study():
    p=reference_profile();rows=[];context=(load(),drive_design.load(),product.configuration_profile())
    for n in load()['groups_per_direction']:
        for area in load()['conductor_areas_mm2']:
            for turns in load()['turns']:
                for bus in load()['dc_buses_v']:rows.append(loss_model(p,groups_per_direction=n,conductor_area_mm2=area,turns=turns,dc_bus_v=bus,_context=context))
    passing=[r for r in rows if r['feasible']];best=min(passing,key=lambda r:r['lifecycle']['installed_lifetime_cost_usd']) if passing else None
    baseline=next(r for r in rows if r['candidate']==dict(groups_per_direction=2,conductor_area_mm2=350.,turns=1,dc_bus_v=2400.))
    return dict(schema=SCHEMA,revision=load()['revision'],configuration=product.configuration_profile(),profile=p,candidates=rows,candidate_count=len(rows),feasible_count=len(passing),
        research_recommendation=best,retained_long_group_comparison=baseline,
        holds=['No measured force/flux/inductance/saturation map or hardware-current qualification','Optimal instantaneous sharing requires physical enable/ramp and protected handover execution','Adiabatic winding temperature is not cooling/ambient duty acceptance','Cost inputs are unquoted assumptions; converter/device/cabinet/current capability and switching loss curves unselected','Grid absorption/recovery, protection/braking redundancy, service duty and financing remain separately qualified'],**FLAGS)

def selected_cost_energy(profile_id='urban',*,configuration_id='baghdad-30kwh-aw3',profile=None):
    # Cheap reusable numerical sweep; no Rust process or native geometry export.
    p=reference_profile(profile_id,configuration_id) if profile is None else profile;rows=[];context=(load(),drive_design.load(),product.configuration_profile(configuration_id))
    for n in load()['groups_per_direction']:
        for area in load()['conductor_areas_mm2']:
            for turns in load()['turns']:
                for bus in load()['dc_buses_v']:
                    r=loss_model(p,groups_per_direction=n,conductor_area_mm2=area,turns=turns,dc_bus_v=bus,configuration_id=configuration_id,_context=context)
                    if r['feasible']:rows.append(r)
    return min(rows,key=lambda r:r['lifecycle']['installed_lifetime_cost_usd']) if rows else None

def overview(r):
    best=r['research_recommendation'];label='No feasible candidate' if best is None else str(best['candidate'])
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="330"><rect width="1200" height="330" fill="#101c2b"/><g fill="white" font-family="sans-serif"><text x="30" y="48" font-size="26">Finite LSM group lifecycle optimisation</text><text x="30" y="105" font-size="20">{r["candidate_count"]} equal-service alternatives; {r["feasible_count"]} numerical screens pass</text><text x="30" y="165" font-size="17">{label}</text><text x="30" y="230" font-size="18">Converter stock, control idle power, cooling, maintenance and renewal included.</text><text x="30" y="285" font-size="16">Unquoted assumptions; no physical qualification or automatic city adoption.</text></g></svg>'

def readme(r):
    return '\n'.join(['# Provisional finite-group launch optimisation','',f'{r["candidate_count"]} equal-service winding/group/voltage candidates; {r["feasible_count"]} satisfy the implemented analytical current/voltage/heat screens.','',
        'Each result binds the exact component-accounted vehicle configuration and motion profile. Groups contain whole2.5m cassettes; the loss-minimizing finite-group current allocation is rejected when current or voltage limits cannot produce the requested trajectory. Booster stock and heat remain separately counted.','',
        'Installed lifetime cost includes finished copper, every converter and sensor/protection group, stator hardware, cooling, idle power, maintenance and converter renewal. Assumed train passages and regeneration reuse are explicit finance sensitivities, not route or grid acceptance.','',*r['holds'],'','No supplier quote, measured magnetic map, physical output, manufacturing release or default adoption.',''])

def publish(output=OUTPUT):
    src=sources();r=study();text=readme(r)
    if src!=sources():raise ValueError('launch sources changed during calculation')
    return product.publish_packet(output,SCHEMA,r,src,{'overview.svg':overview(r).encode(),'README.md':text.encode()})

def verify(output=OUTPUT):
    m,r=product.verify_packet(output,SCHEMA,sources());expected=study()
    if set(m['files_sha256'])!={'study.json.gz','overview.svg','README.md'} or r!=expected or (Path(output)/'overview.svg').read_text()!=overview(expected) or (Path(output)/'README.md').read_text()!=readme(expected):raise ValueError('launch derived sweep or presentation differs')
    return dict(schema='osr-launch-optimisation-verification/1',verified=True,candidates=r['candidate_count'],feasible=r['feasible_count'],research_recommendation=r['research_recommendation'],**FLAGS)

def read_summary(output=OUTPUT):return dict(**verify(output),manifest_sha256=digest((Path(output)/'manifest.json').read_bytes()))
