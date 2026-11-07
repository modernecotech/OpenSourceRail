"""Explicit research hardware additions; mass is never a free energy allowance."""
from copy import deepcopy
from math import expm1, log, isfinite
from pathlib import Path
import json
from engineering.station_pair import coordinator
from engineering.station_rail.common import identity,digest
from . import ROOT

POLICY='engineering/station_cycle/policy.json'
SIZING_REFERENCE='crates/osr-station-energy/src/arrestor.rs'
CASES=('low','base','high')


def policy(root=ROOT):
    p=json.loads((Path(root)/POLICY).read_bytes())
    if p.get('schema')!='osr-station-cycle-policy/1':raise ValueError('Explicit cycle policy required')
    def check(v):
        if isinstance(v,dict):
            for x in v.values():check(x)
        elif isinstance(v,list):
            for x in v:check(x)
        elif type(v) in (int,float) and (not isfinite(v) or v<0):raise ValueError('Finite nonnegative cycle hypothesis required')
    check(p)
    if p['station_spacing_m']!=1500 or p['capture_stages']!=5 or p['leg_departure_interval_s']<=0:
        raise ValueError('This experiment declares the 1.5 km five-stage pilot')
    for tech in ('steel','hydraulic'):
        for k in ('capture_efficiency','release_efficiency','packing_fraction'):
            if not 0<p[tech][k]<=1:raise ValueError('Fraction outside physical range')
    return p


def size_store(technology,capacity,p):
    """Same analytical sizing hypotheses as the retained arrestor; no flow proof."""
    if not isfinite(capacity) or capacity<=0:raise ValueError('Positive finite storage capacity required')
    t=p[technology]
    if technology=='steel':
        specific=t['allowable_stress_pa']**2/(2*t['density_kg_m3']*t['modulus_pa'])*t['utilisation']
        active=capacity/specific;volume=active/t['density_kg_m3']
        return dict(active_mass_kg=active,fluid_mass_kg=0.,internal_volume_m3=volume,
            reserve_envelope_m3=volume/t['packing_fraction'],specific_energy_j_kg=specific,
            basis='Shear elastic material bound with declared stress/utilisation; spring geometry, fatigue and containment unverified')
    if technology!='hydraulic':raise ValueError('No implicit storage technology')
    p0,pmin,pmax,pret,n=(t[k] for k in ('precharge_pressure_pa','min_pressure_pa','max_pressure_pa','return_pressure_pa','polytropic_exponent'))
    if not 0<p0<=pmin<pmax or pret>=pmin or n<=0:raise ValueError('Invalid absolute accumulator pressures')
    lr=log(pmax/pmin);vmin=(p0/pmin)**(1/n);vmax=vmin*(pmin/pmax)**(1/n)
    work=p0*lr if n==1 else pmin*vmin*expm1((n-1)/n*lr)/(n-1)
    work-=pret*(vmin-vmax)
    if work<=0:raise ValueError('Positive hydraulic work required')
    volume=capacity/work
    fluid=volume*(1-(p0/pmax)**(1/n))*t['fluid_density_kg_m3']
    return dict(active_mass_kg=volume*t['vessel_mass_kg_per_m3'],fluid_mass_kg=fluid,
        internal_volume_m3=volume,reserve_envelope_m3=volume/t['packing_fraction'],specific_work_j_m3=work,
        basis='Polytropic gas work less return work; vessel kg/m3, fluid and packing are declared reserves, not pressure-vessel design')


def variants(root=ROOT):
    brief,bundle,mass,parents=coordinator.variants(root)
    p=policy(root);out=[]
    cable=next(v for v in parents if v['family']=='cable' and v['geometry']['motors']==6
        and v['geometry']['powered_front_window_m'][1]==350 and v['physical_definition']['station_spacing_m']==1500)
    wheel=next(v for v in parents if v['family']=='powered-wheel' and v['geometry']['driven_axles']==12
        and v['physical_definition']['station_spacing_m']==1500)
    for parent in (cable,wheel):
        out.append(dict(variant=parent,technology=None,capacity_j=0.,sizing=None,
            speed_cap_km_h=50. if parent['family']=='cable' else 60.,recovery_hardware=False))
    for parent in (cable,wheel):
        for technology in ('steel','hydraulic'):
            for capacity in p['capacities_j']:
                v=deepcopy(parent);sizing=size_store(technology,capacity,p)
                module=dict(technology=technology,nominal_capacity_j=capacity,stations=2,
                    active_stock_kg_per_station=sizing['active_mass_kg'],fluid_stock_kg_per_station=sizing['fluid_mass_kg'],
                    envelope_reserve_m3_per_station=sizing['reserve_envelope_m3'],
                    capture_stage_windows_m=[[1500-p['capture_length_m']+i*p['capture_length_m']/5,
                        1500-p['capture_length_m']+(i+1)*p['capture_length_m']/5] for i in range(5)],
                    release_window_m=p['release_window_m'],
                    transfer_class_hypotheses=dict(capture_force_n=p['stage_force_n'],capture_power_w=p['stage_power_w'],release_force_n=p['release_force_n'],release_power_w=p['release_power_w']),
                    installed_interface_mass_reserve_kg=p['interface_reserve_kg_per_train'],
                    cooling_wiring_installed_mass_reserve_kg_per_station=p['cooling_wiring_installed_mass_reserve_kg_per_station'],
                    material='spring-steel' if technology=='steel' else 'pressure-vessel-steel and hydraulic fluid',
                    station_load_path='Additional supported store, guards, cable transfer and access envelope; detailed foundations open',
                    onboard_interface='Reinforced capture/release load-transfer fittings; bounded installation reserve, not completed CAD')
                v['parent_candidate_id']=parent['candidate_id']
                v['physical_definition']['station_energy_module']=module
                v['name']=('Cable 350 m' if parent['family']=='cable' else 'Powered wheel 12 axles')+f' + {technology} {capacity/1e6:g} MJ'
                for c in CASES:v['onboard_added_mass_kg'][c]+=p['interface_reserve_kg_per_train'][c]
                v['inventory'].append(dict(id='capture-release-interface-reserve',quantity=1,location='train distributed attachment reserve',
                    mass_hypothesis_kg=p['interface_reserve_kg_per_train'],complete_installed_mass=False))
                v['limitations']+=['Generic transfer force/power envelopes do not model actual spring force–stroke or hydraulic pressure–flow',
                    'Capture/release interface reserve adds mass; a completed installed assembly and load-path verification remain required']
                v['candidate_id']=identity(v['physical_definition'])
                out.append(dict(variant=v,technology=technology,capacity_j=capacity,sizing=sizing,
                    speed_cap_km_h=50. if parent['family']=='cable' else 60.,recovery_hardware=True))
    return brief,bundle,mass,out


def added_accounts(design,cost,p):
    """Material/process rows plus positive equipment/site reserves, once only."""
    if not design['recovery_hardware']:return []
    v=design['variant'];s=design['sizing'];rates=p['cost'];tech=design['technology'];rows=[]
    def add(owner,scope,quantity,unit,values,basis,renewal_class):
        row=dict(candidate_id=v['candidate_id'],owner='regenerative-'+owner,scope=scope,quantity=quantity,unit=unit,
            cost_usd={c:quantity*values[i] for i,c in enumerate(CASES)},basis=basis,renewal_class=renewal_class)
        row['account_id']=identity(row);rows.append(row)
    def fabricated(mass,material):
        return [(mass/rates['purchase_yield'][i]*rates['material_usd_kg'][material][i]
            +mass*rates['process_h_kg'][material][i]*rates['loaded_labour_usd_h'][i]
            +mass*rates['machine_QA_consumables_usd_kg'][i])*(1+rates['overhead_fraction'][i]) for i in range(3)]
    add('active-store','stations-power',2,'banks',fabricated(s['active_mass_kg'],tech),
        'Active material/yield + process hours×loaded labour + machinery/QA + declared overhead; unqualified material/design', 'station-storage')
    housing=[s['active_mass_kg']*rates['housing_support_mass_to_active'][i] for i in range(3)]
    add('housing-and-support','stations-power',2,'bank support packages',
        [fabricated(housing[i],tech)[i] for i in range(3)],'Positive containment, lock/support fabrication reserve; no containment proof','station-mechanical')
    if tech=='hydraulic':
        add('hydraulic-fluid','stations-power',2*s['fluid_mass_kg'],'kg',rates['fluid_usd_kg'],
            'Calculated vessel fluid subtotal; balance-of-plant fluid included in package reserve','station-storage')
        add('hydraulic-flow-package','stations-power',2,'pump-valve-return packages',rates['hydraulic_flow_valves_reservoir_package_usd'],
            'Positive pump/valve/piping/reservoir reserve; actual flow and repeated duty unverified','station-mechanical')
    for name,q,k,basis,rc in (
        ('capture',10,'capture_stage_package_usd','Five stages at each station, including cables/clutches/fixings; calculated package allowances','station-mechanical'),
        ('release',2,'release_transmission_guard_package_usd','Controlled forward transfer, return trolley, guards and interfaces; original grid launch retained','station-mechanical'),
        ('control-lock',2,'control_lock_monitoring_per_station_usd','Positive lock, sensing and control reserve; independent brakes retained','station-electrical'),
        ('cooling-wiring',2,'module_cooling_wiring_per_station_usd','Positive heat-rejection, pumps/fans, wiring, piping and support reserve; temperatures/duty and detailed routing unverified','station-electrical'),
        ('electrical-protection',2,'module_electrical_protection_per_station_usd','Module reset supply/protection separate from existing grid and traction panels','station-electrical')):
        add(name,'stations-power',q,'packages',rates[k],basis,rc)
    support_mass=[s['active_mass_kg']+s['fluid_mass_kg']+x+p['cooling_wiring_installed_mass_reserve_kg_per_station'][i] for i,x in enumerate(housing)]
    add('site-support','construction',2,'store foundation packages',
        [support_mass[i]*rates['module_foundation_support_usd_kg'][i] for i in range(3)],
        'Additional bank support/site reserve, not duplicated viaduct supports; actual site design open','site')
    fleet=cost['service']['total_trainsets']
    add('vehicle-interface','rolling-stock',fleet,'six-car installation kits',
        [p['interface_reserve_kg_per_train'][c]*rates['onboard_interface_installed_usd_kg'][i] for i,c in enumerate(CASES)],
        'New interface installed provision; body parent costs are unchanged and not re-added','station-mechanical')
    return rows


def sources(root=ROOT):
    return {n:digest(Path(root)/n) for n in (POLICY,SIZING_REFERENCE,'engineering/station_cycle/design.py')}
