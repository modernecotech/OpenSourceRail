"""Counted capture and hot-roof proposals for the selected comfort car.

This bounded experiment changes component proposals, not the selected vehicle.
Typical coupon properties and declared curves are engineering screens. They do
not qualify a landing system, a roof, or the whole train.
"""
from collections import Counter
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import argparse
import gzip
import json
import math
import platform
import time

import numpy as np
from scipy.integrate import solve_ivp
from scipy.optimize import brentq, root as nonlinear_root

ROOT = Path(__file__).resolve().parents[2]
CODE = 'engineering/thermal_closure/comfort_fixes.py'
SCHEMA = 'osr-comfort-capture-roof-experiment/1'
G = 9.80665
SIGMA = 5.670374419e-8
PSI = 6894.757293168
PCF = 16.01846337396
ROOF_AREA = 17.*2.65
FLAGS = dict(configuration_adopted=False,engineering_accepted=False,
    physical_accepted=False,installed_mass_complete=False,manufacturing_release=False,
    operating_release=False)
REFERENCES = dict(
    hexcel=dict(url='https://www.hexcel.com/wp-content/uploads/2025/12/HexWeb_CRIII_DataSheet.pdf',
        document_sha256='0467f718f7d9d3a175635718573f94f58baea1d753e83db4be8edcba9f374034',
        document='HexWeb CR III product data, copyright2017, pp3-4, 5052 1/4inch 4.3pcf row',
        reviewed='2026-10-26', density_pcf=4.3, density_tolerance_fraction=.10,
        typical_crush_psi=230.,typical_bare_compressive_psi=500.,test_thickness_m=.015875,
        scope='Typical coupon stresses, not allowable stress, a transient force curve, a strain limit, or an assembled landing rating.'),
    karnak=dict(url='https://www.karnakcorp.com/product/529-renu-white',
        document_url='https://cdn.prod.website-files.com/5fdb6a6c2e47643f50c6794c/691f88e3d7d055c1556674c1_529_PDS_070124.pdf',
        document_sha256='81e06c6c4b6e0eb65177eddf1a3f79accfed4d6cbe32aad037f0327b0f472e17',
        reviewed='2026-10-26',reflectance_initial=.85,reflectance_3yr=.73,
        emissivity_initial=.90,emissivity_3yr=.88,wet_weight_lb_per_USgal=11.5,
        nominal_solids_mass_fraction=.63,nominal_solids_volume_fraction=.50,
        coats=2,total_USgal_per100ft2=3.,cured_film_service_max_C=(180.-32.)*5/9,
        scope='Building-roof finish data. Railway adhesion, flexing, fire, Iraq dust/weathering and fastener/repair interfaces unqualified.'),
    diab_hp=dict(url='https://www.diabgroup.com/media/enygao3k/diab-divinycell-hp-april-2022-rev26-si.pdf',
        alternate_document_url='https://www.diabgroup.com/media/juzhmx0h/diab-divinycell-hp-april-2022-rev26-imp.pdf',
        reviewed='2026-10-26', document='Divinycell HP rev26 April2022; manufacturer-indexed data',
        nominal_density_kg_m3=60.,density_variation=[-.10,.15],
        conductivity_W_mK=.243*.144227909,continuous_temperature_limit_C=80.,
        scope='Manufacturer-indexed HP60, conductivity at10C. NativePDF endpoint unavailable at review; provenance not source-byte-confirmed.125C distortion/150C processing are not continuous limits.'),
    ace=dict(url='https://www.acecontrols.com/media/acedownloads/ACE_Main-Catalogue_EN_2016_20170705.pdf',
        product_url='https://www.acecontrols.com/us/products/automation-control/profile-dampers/tubus-ta/ta/ta50-22.html',
        reviewed='2026-10-26',dynamic_curve_minimum_impact_speed_m_s=.5,
        TA50_22_stroke_m=.022,TA50_22_catalogue_mass_kg=.085,
        TA50_22_catalogue_continuous_energy_J=170.,TA50_22_emergency_energy_J=223.,
        scope='Published dynamic characteristic is above0.5m/s; static/low-speed curves and preloaded hot use require manufacturer input. Energy ratings do not establish a landing curve.'))


def encoded(value):
    return (json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False)+'\n').encode()


def identity(value):return sha256(encoded(value)).hexdigest()


def number(value,name,minimum=0.):
    if type(value) not in (int,float) or not math.isfinite(value) or value<minimum:
        raise ValueError('finite '+name+' >= '+str(minimum)+' required')
    return float(value)


def _part(name,volume,density,quantity=1,**extra):
    return dict(id=name,volume_m3_each=volume,density_kg_m3=density,quantity=quantity,
        mass_kg=volume*density*quantity,**extra)


def _capture_positions(count):
    if count%2 or count<4:raise ValueError('paired capture units required')
    return [[float(x),y,-.862] for x in np.linspace(-7.5,7.5,count//2) for y in (-.4595,.4595)]


def capture_candidates():
    rows=[]
    for damping in (0.,20000.):
        physical=dict(component='retained-eight-shoe-reference',count=8,
            law='linear-Kelvin-Voigt' if damping else 'linear-undamped',
            stiffness_N_m_each=1e7,damping_N_s_m_each=damping,stroke_m=.008,force_limit_N_each=50000.,
            engagement_drop_m=.005,allocated_shoe_kg_each=8.,allocated_hanger_kg_each=10.22,
            retained_installed_mass_complete=False)
        rows.append(dict(physical_definition=physical,component_candidate_id=identity(physical),
            proposal='retained-reference-control',counted_or_allocated_stock_kg=8*(8+10.22),
            net_accounted_stock_change_kg=0.,stock=[],geometry=None,**FLAGS))
    for count,layers in ((12,3),(16,5),(24,5),(32,5)):
        length,width=.30,.014/.30
        core_h=layers*REFERENCES['hexcel']['test_thickness_m']
        stroke=.020 if layers==3 else .035
        shell=(.32,.06,.12);wall=.003
        stock=[_part('honeycomb/core-pieces',length*width*.015875,4.3*PCF,count*layers,
                    size_m=[length,width,.015875],cell_axis='vertical'),
            _part('cartridge/four-wall-steel-guide',shell[2]*(shell[0]*shell[1]-(shell[0]-2*wall)*(shell[1]-2*wall)),7850.,count,
                  outer_size_m=list(shell),wall_m=wall),
            _part('cartridge/top-and-bottom-load-plates',shell[0]*shell[1]*.006,7850.,2*count,size_m=[.32,.06,.006]),
            _part('cartridge/intermediate-load-spreaders',length*width*.0015,7850.,count*(layers-1),size_m=[length,width,.0015]),
            _part('cartridge/four-guiding-rods',math.pi*.010**2/4*.12,7850.,4*count,diameter_m=.010,length_m=.12),
            _part('cartridge/guide-rod-end-retaining-collars',math.pi*(.016**2-.010**2)/4*.008,7850.,8*count,role='Retains unloaded cartridge pieces; not a vehicle magnetic pull-in stop'),
            _part('cartridge/collar-crosspins',math.pi*.003**2/4*.020,7850.,4*count,role='Unloaded cartridge retention only; strength unknown'),
            _part('hanger/two-cheeks',.12*.008*.45,7850.,2*count,size_m=[.12,.008,.45]),
            _part('hanger/top-spreader',.35*.10*.012,7850.,count,size_m=[.35,.10,.012]),
            _part('hanger/lower-saddle',.35*.08*.012,7850.,count,size_m=[.35,.08,.012]),
            _part('hanger/four-M12-gross-shanks',math.pi*.012**2/4*.060,7850.,4*count,diameter_m=.012,length_m=.060),
            _part('hanger/washer-pairs',math.pi*(.024**2-.013**2)/4*.0025,7850.,8*count),
            _part('hanger/nut-blanks-minus-bore',(.019**2-math.pi*.012**2/4)*.010,7850.,4*count)]
        mass=math.fsum(p['mass_kg'] for p in stock)
        physical=dict(component='replaceable-honeycomb-crush-cartridge',count=count,core_layers=layers,
            core_grade='HexWeb-CRIII-5052-quarter-inch-4.3pcf-proposal',core_area_m2=.014,
            core_stack_height_m=core_h,usable_stroke_m=stroke,
            usable_crush_strain_hypothesis=stroke/core_h,
            force_limit_N_each_hypothesis=50000.,stock=stock,
            stock_exclusions=['Seals/liners, positive retention latch, body hardpoint reinforcement, corrosion system, service access and discarded crush stock handling'],
            positions_m=_capture_positions(count),cartridge_envelope_m=[.35,.06,.12],
            old_shoe_and_hanger_scope_replaced=True,old_same_scope_stock_kg=145.76,
            material_curve='Typical stress-scaled loading curve; precrush variant is a process/design hypothesis',
            unloading_recoverable_energy_fraction_hypothesis=.10,
            load_path=['Passive steel cap','Contact plate','Replaceable crush stack and guide','Lower saddle','Two hanger cheeks','Top spreader/bolts','Unqualified body hardpoint and beam attachment'])
        rows.append(dict(physical_definition=physical,component_candidate_id=identity(physical),
            proposal='counted-next-experiment',stock=stock,counted_or_allocated_stock_kg=mass,
            net_accounted_stock_change_kg=mass-145.76,
            geometry=dict(core_dimensions_m=[length,width,core_h],stack_with_spreaders_m=core_h+(layers-1)*.0015+.012,
                rail_top_z_m=-.927,free_moving_underside_z_m=-.922,initial_gap_m=.005,
                proposed_contact_width_m=.06,retained_contact_width_m=.04,
                installation_and_motion_clearance='unknown; same nominal datum but widened/new locations need native assembly and beam checks'),
            **FLAGS))
    return rows


def crush_curve(candidate,*,strength_factor=1.,precrushed=False):
    p=candidate['physical_definition']
    if p['component']!='replaceable-honeycomb-crush-cartridge':raise ValueError('explicit crush cartridge required')
    factor=number(strength_factor,'material strength factor',.01)
    F=REFERENCES['hexcel']['typical_crush_psi']*PSI*p['core_area_m2']*factor
    # These knots are declared shapes for a necessary bound, not digitised supplier data.
    # Typical bare compression stress exposes initial peak. Precrushing removes it
    # only as a separately labelled manufacturing/force-law target.
    peak=F if precrushed else REFERENCES['hexcel']['typical_bare_compressive_psi']*PSI*p['core_area_m2']*factor
    scale=p['core_layers']/5.
    x=np.array([0.,.00025*scale,.001*scale,p['usable_stroke_m']])
    f=np.array([0.,peak,F,F])
    return x,f


def capture_response(candidate,mass_kg,*,active_count=None,gap_m=.005,strength_factor=1.,precrushed=False,max_step_s=.0001):
    mass=number(mass_kg,'accounted mass',1.);gap=number(gap_m,'drop gap')
    p=candidate['physical_definition'];count=p['count']
    active=count if active_count is None else active_count
    if type(active) is not int or not 1<=active<=count:raise ValueError('active count must be within counted units')
    speed=math.sqrt(2*G*gap);crush=p['component']=='replaceable-honeycomb-crush-cartridge'
    stroke=p['usable_stroke_m'] if crush else p['stroke_m']
    if crush:
        knots,forces=crush_curve(candidate,strength_factor=strength_factor,precrushed=precrushed)
        def one_force(x,v):return float(np.interp(max(0.,x),knots,forces))
    else:
        def one_force(x,v):return max(0.,p['stiffness_N_m_each']*x+p['damping_N_s_m_each']*v)
    def rhs(t,y):
        force=active*one_force(y[0],y[1]);return [y[1],G-force/mass,force*y[1]]
    def arrested(t,y):return y[1]
    arrested.terminal=True;arrested.direction=-1
    def bottomed(t,y):return y[0]-stroke
    bottomed.terminal=True;bottomed.direction=1
    solution=solve_ivp(rhs,[0.,1.],[0.,speed,0.],rtol=1e-8,atol=[1e-11,1e-10,1e-7],
                       max_step=number(max_step_s,'time step',1e-7),events=(arrested,bottomed))
    if not solution.success:raise ValueError('capture integration failed: '+solution.message)
    xs,vs=solution.y[:2]
    observed=[one_force(float(x),float(v)) for x,v in zip(xs,vs)]
    peak=max(observed);delta=float(xs[-1]);velocity=float(vs[-1]);work=float(solution.y[2,-1])
    arrest=bool(len(solution.t_events[0]));force_limit=p.get('force_limit_N_each_hypothesis',p.get('force_limit_N_each'))
    # Include exact crossed curve peaks, so adaptive timesteps cannot miss a narrow spike.
    if crush:
        peak=max(peak,*[float(f) for x,f in zip(knots,forces) if x<=max(xs)+1e-12])
    residual=.5*mass*speed**2+mass*G*delta-.5*mass*velocity**2-work
    recovered_fraction=p.get('unloading_recoverable_energy_fraction_hypothesis',1.) if crush else None
    if crush and arrest:
        conditional_recovered=work*recovered_fraction
        recovered=work  # Strict energy-only bound: no damping/precrush dissipation is guaranteed.
        maximum_rebound_height_bound=recovered/(mass*G)
    else:recovered=None;conditional_recovered=None;maximum_rebound_height_bound=None
    gross_bolt_shear=peak/(4*math.pi*.012**2/4) if crush else None
    saddle_stress=peak*.08/4/(.35*.012**2/6) if crush else None
    verdict='pass' if arrest and peak<=force_limit and delta<=stroke+1e-9 else 'fail'
    return dict(component_candidate_id=candidate['component_candidate_id'],accounted_mass_kg=mass,
        active_contacts=active,counted_contacts=count,drop_m=gap,initial_impact_speed_m_s=speed,
        loading_curve='precrushed-plateau-target' if crush and precrushed else 'unprecrushed-peak-sensitivity' if crush else p['law'],
        strength_factor_hypothesis=strength_factor if crush else None,arrested_before_bottoming=arrest,
        integration_execution='completed',numerical_validity='within_declared_equations',
        required_compression_m=delta,maximum_usable_stroke_m=stroke,
        peak_force_N_each=peak,force_limit_N_each_hypothesis=force_limit,
        peak_total_contact_force_N=active*peak,
        peak_net_upward_acceleration_m_s2=max(0.,active*peak/mass-G),
        peak_supported_load_factor=active*peak/(mass*G),
        kinetic_energy_at_stroke_J=.5*mass*velocity**2,absorbed_loading_work_J=work,
        energy_balance_residual_J=residual,arrest_time_s=float(solution.t[-1]),
        rebound_recoverable_energy_fraction_hypothesis=recovered_fraction,
        rebound_energy_J_upper_bound=recovered,
        rebound_energy_J_conditional_on_fraction=conditional_recovered,
        rebound_bound_scope='Gravity-only total-loading-work bound; magnetic pull-in energy is additional and unknown',
        rebound_height_m_upper_bound=maximum_rebound_height_bound,
        secondary_latch_or_capture_needed=True,
        proposed_M12_gross_shank_shear_demand_Pa=gross_bolt_shear,
        proposed_12mm_saddle_simply_supported_bending_demand_Pa=saddle_stress,
        saddle_declared_S235_yield_div1p5_necessary_screen=None if not crush else ('pass' if saddle_stress<=235e6/1.5 else 'fail'),
        bolt_thread_bearing_eccentricity_fatigue_body_and_beam_strength='unknown',
        occupant_acceleration_pulse_acceptance='unknown',
        necessary_energy_force_stroke_screen=verdict,
        material_curve_and_hardware_qualified=False,**FLAGS)


def coating_stock(area_m2):
    area=number(area_m2,'coating area',.01);s=REFERENCES['karnak']
    gallons=area/(100*.09290304)*s['total_USgal_per100ft2']
    wet_mass=gallons*s['wet_weight_lb_per_USgal']*.45359237
    dry_mass=wet_mass*s['nominal_solids_mass_fraction']
    return dict(source_id='karnak',area_m2=area,coats=2,wet_USgal=gallons,
        wet_purchased_product_kg=wet_mass,nominal_dry_finish_kg=dry_mass,
        nominal_dry_thickness_m=gallons*.003785411784/area*s['nominal_solids_volume_fraction'],
        primer_and_repairs_mass_kg=None,removed_existing_finish_kg=0.,
        nominal_mass_is_not_measured_installed_mass=True)


def roof_candidates(vehicle):
    old_core=next(p for p in vehicle['components']['roof_revision']['selected']['stock_parts'] if p['id']=='core/trimmed-foam')
    core_volume=old_core['volume_m3_each']*old_core['quantity']
    boxes=vehicle['interfaces']['HVAC_packages'];canopy_area=ROOF_AREA-sum(b['size_m'][0]*b['size_m'][1] for b in boxes)
    variants=[('retained-H60',.5,.10,'H60',False),('white-initial-H60',.15,.90,'H60',False),
              ('white-aged-H60',.27,.88,'H60',False),('white-dust-H60',.40,.88,'H60',False),
              ('white-aged-HP60',.27,.88,'HP60',False),('vented-white-screen-H60',.27,.88,'H60',True)]
    rows=[]
    for name,alpha,epsilon,core,canopy in variants:
        stock=[];finish=None
        if name!='retained-H60':
            finish=coating_stock(ROOF_AREA+(2*canopy_area if canopy else 0.))
            stock.append(dict(id='finish/two-coat-white-acrylic',mass_kg=finish['nominal_dry_finish_kg'],**finish))
        if core=='HP60':
            stock.append(dict(id='core/HP60-replacement',volume_m3=core_volume,
                density_kg_m3=60.,mass_kg=core_volume*60.,removed_H60_kg=old_core['total_mass_kg'],
                net_nominal_mass_kg=core_volume*60.-old_core['total_mass_kg'],
                density_mass_range_kg=[core_volume*54.,core_volume*69.]))
        if canopy:
            stock += [_part('screen/aluminium-skin-minus-five-HVAC-openings',canopy_area*.0005,2710.,1,
                        area_m2=canopy_area,thickness_m=.0005),
                _part('screen/two-longitudinal-30x20x2-rails',17*(.03*.02-.026*.016),2710.,2),
                _part('screen/40-standoff-angles',.05*(.025*.002*2-.002**2),2710.,40),
                _part('screen/80-M6-gross-fasteners',math.pi*.006**2/4*.025,7850.,80),
                _part('screen/80-washers',math.pi*(.012**2-.0065**2)/4*.0015,7850.,80)]
        delta=math.fsum(p.get('net_nominal_mass_kg',p['mass_kg']) for p in stock)
        physical=dict(component='comfort-roof-thermal-proposal',name=name,
            parent_roof_id=vehicle['components']['roof_revision']['selected']['physical_definition_id'],
            total_roof_area_m2=ROOF_AREA,skin_each_m=.0012,skin_lambda_W_mK_hypothesis=160.,
            core_thickness_m=.045,core_grade=core,core_lambda_W_mK=.029 if core=='H60' else REFERENCES['diab_hp']['conductivity_W_mK'],
            core_continuous_limit_C=70. if core=='H60' else 80.,
            absorptivity=alpha,emissivity=epsilon,optical_basis='hypothesis for retainedfinish' if name=='retained-H60' else 'dust sensitivity, not rating' if 'dust' in name else 'KARNAK529 manufacturer initial/3yearoptics',
            stock=stock,net_counted_material_change_kg=delta,
            canopy=canopy,canopy_opening_HVAC_boxes=deepcopy(boxes) if canopy else [],
            canopy_area_m2=canopy_area if canopy else 0.,canopy_roof_clearance_m=.05 if canopy else None,
            coating_area_counts_both_canopy_sides=canopy,
            canopy_wind_pressure_Pa_hypothesis=1500. if canopy else None,
            canopy_net_wind_load_N_hypothesis=1500*canopy_area if canopy else None,
            actual_coating_thermal_resistance_m2K_W=None,
            coating_thermal_bound='Zero coating resistance used for a conservative core heat-ingress bound; coating surface temperature/adhesion need actual material data',
            canopy_air_h_W_m2K_hypothesis=3. if canopy else None,
            added_top_skin_within_vehicle_envelope_qualified=False,
            roof_HVAC_recirculation_access_wind_and_bridges_qualified=False)
        rows.append(dict(component_candidate_id=identity(physical),physical_definition=physical,
            source_materiality='primary-numeric-datasheet' if core=='H60' else 'manufacturer-indexed-HP-data-native-document-unavailable',
            net_counted_material_change_kg=delta,complete_added_installed_mass_kg=None,**FLAGS))
    return rows


def roof_equilibrium(candidate,*,outside_C=50.,inside_C=26.,solar_W_m2=900.,outside_h_W_m2K=15.,longwave_environment_C=50.,inner_h_W_m2K=1/(.17-1/15),canopy_air_h_W_m2K=None):
    p=candidate['physical_definition'];Ta=number(outside_C+273.15,'ambient Kelvin',1.)-273.15
    Ti=number(inside_C+273.15,'cabin Kelvin',1.)-273.15
    h=number(outside_h_W_m2K,'external convection',.01)
    hi=number(inner_h_W_m2K,'internal convection',.01);S=number(solar_W_m2,'solar irradiance')
    Te=number(longwave_environment_C+273.15,'longwave Kelvin',1.)
    if not 0<=p['absorptivity']<=1 or not 0<=p['emissivity']<=1:raise ValueError('bounded optical coefficients required')
    metalR=p['skin_each_m']/p['skin_lambda_W_mK_hypothesis']
    R=2*metalR+p['core_thickness_m']/p['core_lambda_W_mK']+1/hi
    a,e=p['absorptivity'],p['emissivity']
    def radiative(T,Cenv,epsilon):return epsilon*SIGMA*((T+273.15)**4-Cenv**4)
    if not p['canopy']:
        def balance(T):return a*S-h*(T-Ta)-radiative(T,Te,e)-(T-Ti)/R
        Ts=brentq(balance,min(Ti,Ta,longwave_environment_C)-100,max(Ta,longwave_environment_C)+200,xtol=1e-11)
        residual=balance(Ts);screen_temperature=None;Troof=Ts
    else:
        hv=number(p['canopy_air_h_W_m2K_hypothesis'] if canopy_air_h_W_m2K is None else canopy_air_h_W_m2K,'screen gap-air convection',0.)
        # Both surfaces have the same declared finish. Ambient-connected gap air
        # is a ventilation hypothesis; zero hv is the blocked-vent control.
        effective=1/(1/e+1/e-1)
        def eq(x):
            top,roof=x;exchange=effective*SIGMA*((top+273.15)**4-(roof+273.15)**4)
            return [a*S-h*(top-Ta)-radiative(top,Te,e)-hv*(top-Ta)-exchange,
                    exchange-hv*(roof-Ta)-(roof-Ti)/R]
        solution=nonlinear_root(eq,[Ta+15,Ta+8])
        if not solution.success or max(abs(v) for v in eq(solution.x))>1e-6:raise ValueError('screen heat-balance did not converge')
        screen_temperature,Troof=[float(v) for v in solution.x];residual=max(abs(v) for v in eq(solution.x))
    q=(Troof-Ti)/R;core_hot=Troof-q*metalR
    core_cold=core_hot-q*p['core_thickness_m']/p['core_lambda_W_mK']
    limit=p['core_continuous_limit_C']
    finish_limit=REFERENCES['karnak']['cured_film_service_max_C'] if p['name']!='retained-H60' else None
    surface_peak=max(Troof,screen_temperature or Troof)
    return dict(component_candidate_id=candidate['component_candidate_id'],outside_C=Ta,inside_C=Ti,
        solar_W_m2=S,outside_h_W_m2K=h,longwave_environment_C=longwave_environment_C,
        canopy_gap_h_W_m2K=None if not p['canopy'] else hv,
        outer_skin_temperature_C=Troof,canopy_temperature_C=screen_temperature,
        core_hot_C=core_hot,core_cold_C=core_cold,core_limit_C=limit,
        finish_service_limit_C=finish_limit,roof_heat_flux_to_cabin_W_m2=q,
        necessary_core_temperature_screen='pass' if core_hot<=limit else 'fail',
        necessary_finish_temperature_screen='unknown' if finish_limit is None else 'pass' if surface_peak<=finish_limit else 'fail',
        heat_balance_residual_W_m2=residual,
        whole_car_HVAC_demand_kW=None,
        hot_adhered_panel_strength_fire_optical_weathering_and_thermal_bridges='unknown',
        uncertainty='1D steady local field, declared film/longwave boundaries. Gap ventilation and optical transfer to moving rail vehicle are not established.',**FLAGS)


def _sources(root,selected):
    root=Path(root).resolve();result={**selected['source_sha256'],**selected['vehicle']['source_sha256']}
    for name in (CODE,'engineering/thermal_closure/__init__.py','engineering/ferrite_maglev/data/candidate-protection-equipment.json'):
        p=root/name
        if name==CODE and p.read_bytes()!=Path(__file__).read_bytes():raise ValueError('executed producer differs from declared source root')
        result[name]=sha256(p.read_bytes()).hexdigest()
    for name,digest in result.items():
        p=root/name
        if p.is_symlink() or sha256(p.read_bytes()).hexdigest()!=digest:raise ValueError('source input differs: '+name)
    return dict(sorted(result.items()))


def subject(root=ROOT):
    from engineering.development_baseline import selection
    selected=selection.load(root);car=selected['vehicle']
    if (selected['selection']['vehicle']['cars'],selected['selection']['vehicle']['normal_passengers_per_car'])!=(6,46):raise ValueError('selected comfort context required')
    if car['mass']['installed_tare_kg_per_car'] is not None:raise ValueError('study does not accept an invented installed tare')
    return selected


def evaluate(root=ROOT):
    root=Path(root).resolve();selected=subject(root);car=selected['vehicle'];sources=_sources(root,selected)
    captures=capture_candidates();roofs=roof_candidates(car);impact=[];thermal=[]
    loads=[(0,0.),(46,0.),(160,0.),(160,2000.)]
    for c in captures:
        p=c['physical_definition'];count=p['count'];crush='core_layers' in p
        for passengers,extra in loads:
            mass=car['mass']['accounted_tare_kg_per_car']+75.*passengers+extra+c['net_accounted_stock_change_kg']
            for active in (count,3*count//4):
                variants=[(scale,pre) for scale in (.75,1.,1.25) for pre in (False,True)] if crush else [(1.,False)]
                for scale,pre in variants:
                    row=capture_response(c,mass,active_count=active,strength_factor=scale,precrushed=pre)
                    row.update(passengers=passengers,unclosed_extra_mass_kg_hypothesis=extra,
                        source_tare_kg_per_car=car['mass']['accounted_tare_kg_per_car'],
                        net_counted_component_stock_change_kg=c['net_accounted_stock_change_kg'])
                    row['evaluation_id']=identity(row);impact.append(row)
    for c in roofs:
        for h in (5.,15.,35.):
            for environment in (30.,50.,60.):
                row=roof_equilibrium(c,outside_h_W_m2K=h,longwave_environment_C=environment)
                row['evaluation_id']=identity(row);thermal.append(row)
    # The canopy cannot quietly assume ambient-connected air if venting is lost.
    canopy=next(c for c in roofs if c['physical_definition']['canopy'])
    for environment in (50.,60.):
        row=roof_equilibrium(canopy,outside_h_W_m2K=5.,longwave_environment_C=environment,canopy_air_h_W_m2K=0.)
        row['evaluation_id']=identity(row);thermal.append(row)
    low_speed=math.sqrt(2*G*.005)
    old_R=.17+2*.0012/160.+.045/.029
    old_q=(80.-26.)/old_R
    retained_roof_control=dict(model='Original sol-air15W/m2K/.17totalfilms, no longwave term',
        roof_hot_core_C=80.-old_q*(1/15+.0012/160.),
        necessary_hot_core_screen='fail',original_default_gate_unchanged=True)
    record=dict(schema=SCHEMA,selection_id=selected['selection_id'],
        candidate_id=car['candidate_id'],body_candidate_id=car['body_candidate_id'],magnet_component_id=car['magnet_component_id'],
        source_sha256=sources,parent_mass=deepcopy(car['mass']),references=deepcopy(REFERENCES),
        capture_candidates=captures,roof_candidates=roofs,capture_cases=impact,roof_cases=thermal,
        retained_roof_equation_control=retained_roof_control,
        budget=dict(maximum_cases=300,executed_cases=len(impact)+len(thermal),capture_cases=len(impact),roof_cases=len(thermal),native_FEM_executions=0),
        method=dict(capture='SciPy solve_ivp, event-resolved first arrest or stroke exhaustion; absolute energy residual retained',
            thermal='Steady nonlinear surface radiation/convection and through-panel conduction; bracketed roots or coupled two-surface heat balance'),
        ace_low_speed_gate=dict(actual_free_drop_speed_m_s=low_speed,published_dynamic_curve_minimum_m_s=.5,
            actual_force_curve_valid=False,screen='outside-catalogue-characteristic-domain',
            static_support_rebound_hot_preload_and_mounting='unknown'),
        capture_direction_coverage=dict(downward_gravity='Analytical first-impact cases only',
            upward_magnetic_pull_in='unknown/out_of_domain',
            upward_energy_J=None,upward_stop_force_N=None,
            reason='No accepted installed force-gap-current-temperature map supports the magnetic work integral to a closest-approach stop. Attractive PMs remain active after power loss.',
            required='Separate positive vehicle retention, approach stops, rebound latch and complete body/beam force paths; counted unloaded cartridge retainers do not supply these functions'),
        maturity=dict(capture='analytical',roof='analytical',material='manufacturer-typical-coupon/product data',
            complete_installed_capture='concept',complete_vehicle='not evaluated'),
        complete_vehicle_candidate_generated=False,physically_qualified_alternatives=0,
        default_configuration_changed=False,**FLAGS)
    if record['budget']['executed_cases']>300:raise ValueError('case budget exceeded')
    record['evaluation_id']=identity(record);return record


def summary(record):
    impact=record['capture_cases'];thermal=record['roof_cases']
    selected=[]
    for c in record['capture_candidates']:
        if c['proposal']=='retained-reference-control':continue
        rows=[r for r in impact if r['component_candidate_id']==c['component_candidate_id'] and r['loading_curve']=='precrushed-plateau-target']
        nominal=next(r for r in rows if r['passengers']==46 and r['unclosed_extra_mass_kg_hypothesis']==0 and r['strength_factor_hypothesis']==1 and r['active_contacts']==r['counted_contacts'])
        selected.append(dict(component_candidate_id=c['component_candidate_id'],contacts=c['physical_definition']['count'],
            counted_new_stock_kg=c['counted_or_allocated_stock_kg'],net_accounted_stock_change_kg=c['net_accounted_stock_change_kg'],
            nominal_46_person_case=nominal,precrushed_target_cases=len(rows),
            precrushed_target_necessary_passes=sum(r['necessary_energy_force_stroke_screen']=='pass' for r in rows),
            precrush_force_curve_material_and_complete_load_path_qualified=False))
    roof_summary=[]
    for c in record['roof_candidates']:
        rows=[r for r in thermal if r['component_candidate_id']==c['component_candidate_id']]
        reference=next(r for r in rows if r['outside_h_W_m2K']==15 and r['longwave_environment_C']==50)
        roof_summary.append(dict(component_candidate_id=c['component_candidate_id'],name=c['physical_definition']['name'],
            counted_material_change_kg=c['net_counted_material_change_kg'],reference_hot_core_C=reference['core_hot_C'],
            maximum_studied_hot_core_C=max(r['core_hot_C'] for r in rows),
            cases=len(rows),necessary_core_passes=sum(r['necessary_core_temperature_screen']=='pass' for r in rows),
            installed_thermal_qualification=False))
    return dict(schema=SCHEMA,selection_id=record['selection_id'],candidate_id=record['candidate_id'],
        body_candidate_id=record['body_candidate_id'],magnet_component_id=record['magnet_component_id'],evaluation_id=record['evaluation_id'],
        cases=record['budget'],capture_screen_counts=dict(Counter(r['necessary_energy_force_stroke_screen'] for r in impact)),
        roof_core_screen_counts=dict(Counter(r['necessary_core_temperature_screen'] for r in thermal)),
        capture_options=selected,roof_options=roof_summary,ace_low_speed_gate=record['ace_low_speed_gate'],
        capture_direction_coverage=deepcopy(record['capture_direction_coverage']),
        physically_qualified_alternatives=0,default_configuration_changed=False,**FLAGS)


def verify(output,*,root=ROOT,replay=True):
    folder=Path(output);m=json.loads((folder/'manifest.json').read_bytes())
    for name,digest in m['source_sha256'].items():
        p=Path(root)/name
        if p.is_symlink() or sha256(p.read_bytes()).hexdigest()!=digest:raise ValueError('source differs: '+name)
    for name,digest in m['files_sha256'].items():
        if Path(name).is_absolute() or '..' in Path(name).parts or sha256((folder/name).read_bytes()).hexdigest()!=digest:raise ValueError('payload differs: '+name)
    record=json.loads(gzip.decompress((folder/'result.json.gz').read_bytes()))
    selected=subject(root)
    expected={**selected['vehicle'],'selection_id':selected['selection_id']}
    for key in ('selection_id','candidate_id','body_candidate_id','magnet_component_id'):
        if record.get(key)!=expected[key] or m.get(key)!=expected[key]:raise ValueError('selected physical identity differs: '+key)
    if record['source_sha256']!=m['source_sha256'] or m['source_sha256']!=_sources(root,selected):raise ValueError('producer/source set differs')
    if any(record.get(k) is not v or m.get(k) is not v for k,v in FLAGS.items()):raise ValueError('research cannot grant qualification')
    if record['evaluation_id']!=identity({k:v for k,v in record.items() if k!='evaluation_id'}):raise ValueError('evaluation identity differs')
    if m['evaluation_id']!=record['evaluation_id']:raise ValueError('manifest evaluation differs')
    if replay and evaluate(root)!=record:raise ValueError('replayed capture/roof equations differ')
    if json.loads((folder/'summary.json').read_bytes())!=summary(record):raise ValueError('summary differs')
    return dict(verified=True,replayed=replay,evaluation_id=record['evaluation_id'],cases=record['budget']['executed_cases'],**FLAGS)


def run(output,*,root=ROOT):
    folder=Path(output);folder.mkdir(parents=True,exist_ok=False);started=time.monotonic();record=evaluate(root)
    payloads={'result.json.gz':gzip.compress(encoded(record),mtime=0),'summary.json':encoded(summary(record))}
    for name,data in payloads.items():(folder/name).write_bytes(data)
    receipt=dict(schema=SCHEMA,evaluation_id=record['evaluation_id'],
        **{k:record[k] for k in ('selection_id','candidate_id','body_candidate_id','magnet_component_id')},source_sha256=record['source_sha256'],
        files_sha256={n:sha256(v).hexdigest() for n,v in payloads.items()},**FLAGS)
    (folder/'manifest.json').write_bytes(encoded(receipt));result=verify(folder,root=root,replay=True)
    (folder/'execution.json').write_bytes(encoded(dict(execution='completed',elapsed_s=time.monotonic()-started,
        verification=result,python=platform.python_version(),numerical_model='SciPy',**FLAGS)))
    return summary(record)


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('action',choices=('run','verify'))
    parser.add_argument('--root',type=Path,default=ROOT);parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args(argv);value=run(args.output,root=args.root) if args.action=='run' else verify(args.output,root=args.root)
    print(json.dumps(value,sort_keys=True,indent=2));return 0


if __name__=='__main__':raise SystemExit(main())
