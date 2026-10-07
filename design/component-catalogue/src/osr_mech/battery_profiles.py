"""Explicit pack-level profiles and chronological shared-charger study.

This deterministic minute-step simulator reports missed energy/reserve duties.
It is a study, never a commissioning calibration or timetable release.
"""
from __future__ import annotations
from dataclasses import dataclass
import math


class _ShortfallLedger:
    """Keep exact counters while optionally bounding retained diagnostics."""
    def __init__(self, retain_all):
        self.retain_all=retain_all
        self.rows=[]
        self.count=0
        self.reserve_minutes=0
        self.journeys=set()

    def append(self,row):
        self.count+=1
        self.reserve_minutes+=row['reason']=='reserve-SOC'
        if row.get('journey'):
            self.journeys.add(row['journey'])
        if self.retain_all or len(self.rows)<20:
            self.rows.append(row)


def validate_profile(p: dict) -> None:
    positive = ('nameplate_kwh','usable_kwh','pack_mass_kg','pack_volume_m3','voltage_min_v','voltage_max_v',
                'nominal_voltage_v','series_cells','parallel_strings','charge_max_kw','discharge_max_kw',
                'cycle_life_efc','calendar_life_years','installed_cost_usd','replacement_cost_usd')
    if any(not math.isfinite(p[k]) or p[k] <= 0 for k in positive):
        raise ValueError('battery profile requires positive finite pack parameters')
    if not 0 < p['usable_kwh'] <= p['nameplate_kwh'] or not 0 < p['efficiency'] <= 1:
        raise ValueError('invalid capacity/efficiency')
    if not p['voltage_min_v'] < p['nominal_voltage_v'] < p['voltage_max_v']:
        raise ValueError('invalid voltage range')
    if not p['temperature_min_c'] < p['temperature_cold_derate_c'] < p['temperature_derate_c'] < p['temperature_max_c'] or not 0 < p['soc_taper_start'] < 1 or not 0 < p['replace_at_soh'] < 1:
        raise ValueError('invalid charge envelope or replacement threshold')
    if not p.get('evidence_revision') or not p.get('supplier_cell_identity'):
        raise ValueError('missing battery identity/evidence revision')


def resolve_profile(configuration: dict, catalogue: dict, application: str) -> dict:
    """Explicit identities; a changed chemistry label cannot reuse LFP data."""
    profile_id=configuration.get('battery_profile')
    if not profile_id or profile_id not in catalogue['profiles']:
        raise ValueError('explicit known battery_profile required')
    profile=catalogue['profiles'][profile_id]
    if profile['application'] != application or profile['chemistry'] != configuration.get('battery_chemistry',profile['chemistry']):
        raise ValueError('battery profile chemistry/application mismatch')
    validate_profile(profile)
    return profile


def charge_limit_kw(profile: dict, soc: float, temperature_c: float, soh: float) -> float:
    if temperature_c <= profile['temperature_min_c'] or temperature_c >= profile['temperature_max_c']:
        return 0.0
    thermal = min(1,(profile['temperature_max_c']-temperature_c)/(profile['temperature_max_c']-profile['temperature_derate_c']),
                  (temperature_c-profile['temperature_min_c'])/(profile['temperature_cold_derate_c']-profile['temperature_min_c']))
    taper = min(1,max(0,(1-soc)/(1-profile['soc_taper_start'])))
    return profile['charge_max_kw']*thermal*taper*soh


def discharge_limit_kw(profile: dict, soc: float, temperature_c: float, soh: float) -> float:
    if temperature_c <= profile['temperature_min_c'] or temperature_c >= profile['temperature_max_c']:
        return 0.0
    thermal = min(1,(profile['temperature_max_c']-temperature_c)/(profile['temperature_max_c']-profile['temperature_derate_c']),
                  (temperature_c-profile['temperature_min_c'])/(profile['temperature_cold_derate_c']-profile['temperature_min_c']))
    low_soc = min(1,max(0,soc/0.1))
    return profile['discharge_max_kw']*thermal*low_soc*soh


def vehicle_profile(reference_mass_kg: float, cars: int, reference: dict, selected: dict) -> dict:
    validate_profile(selected)
    if reference['application'] != 'onboard' or selected['application'] != 'onboard':
        raise ValueError('vehicle requires onboard profile')
    if reference['usable_kwh'] != selected['usable_kwh']:
        raise ValueError('matched case requires equal usable capacity')
    mass = reference_mass_kg+cars*(selected['pack_mass_kg']-reference['pack_mass_kg'])
    return dict(vehicle_mass_kg=mass,usable_kwh=selected['usable_kwh']*cars,
                nameplate_kwh=selected['nameplate_kwh']*cars,pack_volume_m3=selected['pack_volume_m3']*cars,
                energy_mass_factor=mass/reference_mass_kg,installed_cost_usd=selected['installed_cost_usd']*cars,
                replacement_cost_usd=selected['replacement_cost_usd']*cars)


def chronological_energy(onboard: dict, stationary: dict, trains: dict[str,dict], sites: dict[str,dict],
                         visits: list[dict], departures: list[dict], minutes: int,
                         *, ambient_c: float = 45.0, seasonal_solar_factor: float = 1.0,
                         cleaning_factor: float = 0.9, outages: set[int] | None = None,
                         reserve_soc: float = 0.2, setup_seconds: float = 20.0,
                         retain_shortfalls: bool = True, initial_state: dict | None = None,
                         minute_offset: int = 0) -> dict:
    validate_profile(onboard); validate_profile(stationary)
    if onboard['application'] != 'onboard' or stationary['application'] != 'stationary':
        raise ValueError('profiles do not match battery applications')
    if minutes <= 0 or not 0 <= reserve_soc < 1 or not 0 <= cleaning_factor <= 1 or not 0 <= seasonal_solar_factor <= 1 or setup_seconds < 0:
        raise ValueError('invalid duty-cycle assumptions')
    states = {tid:dict(energy=t['initial_soc']*onboard['usable_kwh']*t['cars'],soh=1.0,min_soc=t['initial_soc'],throughput=0.0,replacements=0) for tid,t in trains.items()}
    storage = {sid:s['initial_soc']*stationary['usable_kwh']*s['modules'] for sid,s in sites.items()}
    storage_soh=dict.fromkeys(sites,1.0)
    storage_replacements=dict.fromkeys(sites,0)
    if initial_state is not None:
        if set(initial_state['trains'])!=set(trains) or set(initial_state['storage_kwh'])!=set(sites):
            raise ValueError('continuous energy state identities differ from the duty')
        states=initial_state['trains'];storage=initial_state['storage_kwh']
        storage_soh=initial_state['storage_soh'];storage_replacements=initial_state['storage_replacements']
    compatibility={sid:onboard['voltage_min_v'] <= site.get('charger_bus_voltage_v',onboard['nominal_voltage_v']) <= onboard['voltage_max_v'] for sid,site in sites.items()}
    totals=dict(grid_kwh=0.0,grid_storage_replenishment_kwh=0.0,solar_kwh=0.0,charger_kwh=0.0,regeneration_accepted_kwh=0.0,regeneration_rejected_kwh=0.0,unserved_traction_kwh=0.0,auxiliary_kwh=0.0)
    shortfalls=_ShortfallLedger(retain_shortfalls)
    service_events={};journey_events={}
    for tid,train in trains.items():
        for a,b in train.get('service_intervals',[(0,minutes)]):
            if b<=0:
                continue
            service_events.setdefault(max(0,math.ceil(a)),[]).append((tid,1))
            service_events.setdefault(math.ceil(b),[]).append((tid,-1))
        for a,b,identity in train.get('service_journeys',[]):
            if b<=0:
                continue
            journey_events.setdefault(max(0,math.ceil(a)),[]).append((tid,identity))
            journey_events.setdefault(math.ceil(b),[]).append((tid,None))
    in_service_counts=dict.fromkeys(trains,0)
    active_journeys={}
    missed=[]
    received=dict.fromkeys(range(len(visits)),0.0)
    by_train={}
    for v in visits:
        if v['train'] not in trains or v['site'] not in sites or v['departure_min']<=v['arrival_min']:
            raise ValueError('invalid train charging visit')
        by_train.setdefault(v['train'],[]).append(v)
    for rows in by_train.values():
        ordered=sorted(rows,key=lambda v:v['arrival_min'])
        if any(a['departure_min']>b['arrival_min']+1e-9 for a,b in zip(ordered,ordered[1:])):
            raise ValueError('train has overlapping visits')
    departures_at={}
    for d in departures:
        departures_at.setdefault(d['minute'],[]).append(d)
    active_at={}
    for i,v in enumerate(visits):
        if v.get('missed',False):
            continue
        for m in range(max(0,math.floor(v['arrival_min'])),min(minutes,math.ceil(v['departure_min']))):
            start=max(m,v['arrival_min']+setup_seconds/60)
            stop=min(m+1,v['departure_min'])
            if stop>start:
                active_at.setdefault((m,v['site']),[]).append((i,v,(stop-start)/60))
    regen_at={}
    for d in departures:
        if d.get('regenerative_kwh',0):
            regen_at.setdefault(d.get('arrival_minute', d['minute']+math.ceil(d.get('travel_minutes',1))),[]).append(d)
    for minute in range(minutes):
        clock_minute=minute+minute_offset
        for tid,change in service_events.get(minute,[]):
            in_service_counts[tid]+=change
        # End old journeys before starting any journey at the same minute.
        for tid,identity in sorted(journey_events.get(minute,[]),key=lambda row:row[1] is not None):
            active_journeys[tid]=identity
        before_throughput={tid:s['throughput'] for tid,s in states.items()}
        for d in departures_at.get(minute,[]):
            if d['minute'] != minute:
                continue
            tid=d['train']; state=states[tid]; t=trains[tid]
            demand=d['distance_km']*t['energy_kwh_km']*t['mass_factor']
            capacity=onboard['usable_kwh']*t['cars']*state['soh']
            power_energy=discharge_limit_kw(onboard,state['energy']/capacity,ambient_c,state['soh'])*t['cars']*d.get('travel_minutes',1)/60
            usable=min(state['energy'],power_energy)
            delivered=min(demand,usable)
            state['energy']-=delivered; state['throughput']+=delivered
            if delivered < demand:
                totals['unserved_traction_kwh']+=demand-delivered
                shortfalls.append(dict(minute=minute,train=tid,journey=d.get('journey'),reason='traction-energy-or-discharge-power',unserved_kwh=demand-delivered))
        for d in regen_at.get(minute,[]):
            tid=d['train']; state=states[tid]; t=trains[tid]
            regen=d['regenerative_kwh']
            capacity=onboard['usable_kwh']*t['cars']*state['soh']
            soc=state['energy']/capacity
            accepted=min(regen,charge_limit_kw(onboard,soc,ambient_c,state['soh'])*t['cars']*d.get('regen_seconds',60)/3600,max(0,capacity-state['energy'])/onboard['efficiency'])
            state['energy']+=accepted*onboard['efficiency']; state['throughput']+=accepted*onboard['efficiency']
            totals['regeneration_accepted_kwh']+=accepted; totals['regeneration_rejected_kwh']+=regen-accepted
        for tid,state in states.items():
            t=trains[tid]
            in_service=in_service_counts[tid]>0
            journey=active_journeys.get(tid)
            aux=(t.get('auxiliary_kw',0)*max(1,ambient_c/30)+onboard['cooling_kw']*t['cars'])/60 if in_service else 0.0
            consumed=min(state['energy'],aux)
            state['energy']-=consumed;state['throughput']+=consumed
            totals['auxiliary_kwh']+=consumed
            if consumed<aux:
                shortfalls.append(dict(minute=minute,train=tid,journey=journey,reason='auxiliary-energy',unserved_kwh=aux-consumed))
            capacity=onboard['usable_kwh']*t['cars']*state['soh']
            state['min_soc']=min(state['min_soc'],state['energy']/capacity)
            if state['energy'] < reserve_soc*capacity:
                shortfalls.append(dict(minute=minute,train=tid,journey=journey,reason='reserve-SOC',unserved_kwh=0))
        for sid,site in sites.items():
            all_active=active_at.get((minute,sid),[])
            active=all_active[:site.get('contact_count',len(all_active))]
            if len(active)<len(all_active):
                shortfalls.append(dict(minute=minute,site=sid,reason='charger-contact-capacity',unserved_kwh=0.0))
            solar=site['pv_kw']*seasonal_solar_factor*cleaning_factor*max(0,math.sin(math.pi*((clock_minute%1440)/60-6)/12)) if 360 <= clock_minute%1440 <= 1080 else 0
            grid=0 if clock_minute in (outages or set()) else site['grid_kw']
            cap=stationary['usable_kwh']*site['modules']*storage_soh[sid]
            available=min(discharge_limit_kw(stationary,storage[sid]/cap,ambient_c,storage_soh[sid])*site['modules'],max(0,storage[sid]-cap*reserve_soc)*60*stationary['efficiency'])
            storage_aux=stationary['cooling_kw']*site['modules']
            power=max(0,solar+grid+available-storage_aux)
            allocated=[]
            for i,v,dt in active:
                state=states[v['train']];t=trains[v['train']]
                capacity=onboard['usable_kwh']*t['cars']*state['soh']
                charger_kw=min(site['charger_kw'],site.get('charger_max_current_a',float('inf'))*site.get('charger_bus_voltage_v',onboard['nominal_voltage_v'])/1000)
                charger=min(charger_kw/len(active),power/len(active),charge_limit_kw(onboard,state['energy']/capacity,ambient_c,state['soh'])*t['cars']) if compatibility[sid] else 0.0
                if not compatibility[sid]:
                    shortfalls.append(dict(minute=minute,site=sid,reason='battery-charger-voltage-incompatibility',unserved_kwh=0.0))
                efficiency=onboard['efficiency']*site.get('charger_efficiency',1.0)
                energy=min(charger*dt,max(0,capacity-state['energy'])/efficiency)
                state['energy']+=energy*efficiency;state['throughput']+=energy*efficiency
                received[i]+=energy*efficiency;allocated.append(energy)
            consumed=sum(allocated)+storage_aux/60
            if consumed > (solar+grid+available)/60+1e-9:
                shortfalls.append(dict(minute=minute,site=sid,reason='stationary-cooling-energy',unserved_kwh=consumed-(solar+grid+available)/60))
                consumed=(solar+grid+available)/60
            solar_energy=solar/60
            grid_energy=min(grid/60,max(0,consumed-solar_energy))
            discharge=max(0,consumed-solar_energy-grid_energy)/stationary['efficiency']
            discharge=min(storage[sid],discharge)
            storage[sid]-=discharge
            surplus=max(0,solar_energy-consumed)
            grid_surplus=max(0,grid/60-grid_energy) if site.get('allow_grid_storage_recharge',False) else 0.0
            soc=storage[sid]/cap
            target=site.get('storage_recharge_target_soc',1.0)
            if not 0<=target<=1:
                raise ValueError('stationary recharge target SOC must be in [0,1]')
            charge=min(surplus+grid_surplus,charge_limit_kw(stationary,soc,ambient_c,storage_soh[sid])*site['modules']/60,max(0,cap*target-storage[sid])/stationary['efficiency'])
            solar_charge=min(charge,surplus);grid_charge=charge-solar_charge
            storage[sid]+=charge*stationary['efficiency']
            loss=(discharge+charge*stationary['efficiency'])/(2*stationary['nameplate_kwh']*site['modules'])*(1-stationary['replace_at_soh'])/stationary['cycle_life_efc']
            storage_soh[sid]-=loss+(1-stationary['replace_at_soh'])/(stationary['calendar_life_years']*365.25*1440)
            if storage_soh[sid]<=stationary['replace_at_soh']:
                storage_replacements[sid]+=1;storage_soh[sid]=1.0
            storage[sid]=min(storage[sid],stationary['usable_kwh']*site['modules']*storage_soh[sid])
            totals['grid_kwh']+=grid_energy+grid_charge;totals['grid_storage_replenishment_kwh']+=grid_charge
            totals['solar_kwh']+=min(solar_energy,consumed)+solar_charge;totals['charger_kwh']+=sum(allocated)
        for tid,state in states.items():
            t=trains[tid]
            throughput=state['throughput']-before_throughput[tid]
            fade=throughput/(2*onboard['nameplate_kwh']*t['cars'])*(1-onboard['replace_at_soh'])/onboard['cycle_life_efc']
            state['soh']-=fade+(1-onboard['replace_at_soh'])/(onboard['calendar_life_years']*365.25*1440)
            if state['soh']<=onboard['replace_at_soh']:
                state['replacements']+=1;state['throughput']=0;state['soh']=1.0
            state['energy']=min(state['energy'],onboard['usable_kwh']*t['cars']*state['soh'])
    for i,v in enumerate(visits):
        if v.get('missed',False) or received[i] < v.get('required_charge_kwh',0):
            missed.append(dict(visit=i,train=v['train'],reason='missed-opportunity' if v.get('missed',False) else 'insufficient-charge',
                               unmet_charge_kwh=max(0,v.get('required_charge_kwh',0)-received[i])))
    return dict(stationary_pack_quantities={sid:dict(pack_mass_kg=site['modules']*stationary['pack_mass_kg'],
                pack_volume_m3=site['modules']*stationary['pack_volume_m3'],nameplate_kwh=site['modules']*stationary['nameplate_kwh'],
                usable_kwh=site['modules']*stationary['usable_kwh']) for sid,site in sites.items()},
                charging_voltage_compatible=compatibility,totals=totals,trains=states,storage_kwh=storage,storage_soh=storage_soh,storage_replacements=storage_replacements,
                shortfalls=shortfalls.rows,shortfall_events=shortfalls.count,
                shortfall_records_complete=retain_shortfalls,
                missed_charges=missed,minimum_soc=min((s['min_soc'] for s in states.values()),default=1),
                reserve_violation_train_minutes=shortfalls.reserve_minutes,
                distinct_energy_affected_journeys=len(shortfalls.journeys),
                service_disruption_feedback_modelled=False,
                installed_battery_cost_usd=sum(t['cars'] for t in trains.values())*onboard['installed_cost_usd']+sum(s['modules'] for s in sites.values())*stationary['installed_cost_usd'],
                replacement_cost_usd=sum(states[k]['replacements']*t['cars'] for k,t in trains.items())*onboard['replacement_cost_usd']+sum(storage_replacements[k]*s['modules'] for k,s in sites.items())*stationary['replacement_cost_usd'],
                service_qualified=False,time_step_seconds=60)
