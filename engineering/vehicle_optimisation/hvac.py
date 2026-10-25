"""Occupied-car HVAC load/stock sensitivities, never a qualified equipment choice.

The 800 kg HVAC-and-duct allowance is replaced once inside the canonical
unlocated residual. It is not weighed hardware, and 40/60 kW total services are
not HVAC-only powers. Thermal load is independent of vehicle structural mass.
"""
from copy import deepcopy
from hashlib import sha256
import json
import math
from pathlib import Path
import tomllib

ROOT = Path(__file__).resolve().parents[2]
FLAGS = dict(physical_accepted=False, configuration_adopted=False, comfort_qualified=False)
CONTEXT = dict(cars=6, body_length_m=17., normal_passengers_per_car=120,
               maximum_passengers_per_car=160, comparison_pphpd=14400, headway_s=180,
               door_cycle_inferred_from_headway=False)
REFERENCES = {
    'tk-lrc': dict(url='https://thermokingzapp.com/tk-lrc-en/',
        manufacturer_page='https://europe.thermoking.com/rail-hvac/lrc', document='Thermo King LRC 08-2022 EN2',
        applicability='Current manufacturer-page download; family ranges are not one correlated order specification. Reduced output at 50 C is unquantified.'),
    'tk-msu': dict(url='https://thermokingzapp.com/tk-msu-en/',
        manufacturer_page='https://europe.thermoking.com/rail-hvac/msu', document='Thermo King MSU 08-2022 EN2',
        applicability='Short-module tram equipment; reduced output only to 49 C. No published electrical-input curve.'),
    'konvekta': dict(url='https://www.konvekta.de/en/products/hvac-thermal-management-systems-for-buses/electric-hybrid-bus/ultralight-500-700-em-3-gen.html',
        datasheet='https://www.konvekta.de/fileadmin/user_upload/docs/datenblaetter/busse/UltraLight_500-700_EM_Gen.3_dt_engl_1021.pdf',
        applicability='Electric-compressor bus roof package, not an engine-driven evaporator-only comparison. 50 C performance limit does not establish nominal output there or railway qualification.'),
    'river': dict(url='https://riverengg.com/key-products/railways-and-metro/roof-mounted-ac-package-unit-rmpu/',
        applicability='Stesalit-associated passenger-coach package: 24.6 kW thermal at 50 C; 16.5 kVA is apparent power, package mass and fresh-air rating are unspecified.'),
    'cpa': dict(url='https://www.cpaelettronica.it/en/impianti-hvac-co2/',
        applicability='COM1 roof monobloc, 730 kg/36 kW; published exterior envelope ends at 45 C. No electrical-input curve or Baghdad acceptance.'),
    'coolaer': dict(url='https://coolaer.com/wpcoolaer/wp-content/uploads/2024/10/CoolAer-Railway-Metro-Air-Conditioning-20241010.pdf',
        applicability='CRW035: 550 kg, 36.96 kW gross/20.9 kW net sensible and 15.272 kWe at 35 C outdoor/28 C return. Hotter output and complete interface scope remain unknown.'),
    'underfloor': dict(url='https://www.mitsubishielectric-railway.eu/products-solutions/air-conditioning/hvac/',
        applicability='Manufacturer supports roof, underfloor and split architectures. No order-specific mass, capacity or 50 C map is supplied; no numerical mass saving is credited.'),
    'glazing': dict(url='https://www.saint-gobain-sekurit-transport.com/sites/hps-mac3-sekurit-transport/files/2021-12/Saint-Gobain%20Sekurit%20Transport%20-%20Thermocontrol%20Reflecting.pdf',
        applicability='Stationary plot supports rounded g=.82/.55 clear/IR-reflecting hypotheses. Windshield construction transferred to side/door glazing is unqualified; U=5.7 is a separate assumption.'),
    'insulation': dict(url='https://diab-media.azureedge.net/eyajkrhd/diab-divinycell-h-sep-2025-rev25-si.pdf',
        manufacturer_page='https://diabgroup.com/certificates-datasheets/',
        applicability='H80 typical conductivity .031 W/m/K at 20 C; hot, bridged, joined railway panels require measurement. Core temperature and fire/structural limits are separate.'),
    'co2': dict(url='https://doi.org/10.1111/ina.12383',
        primary_copy='https://tsapps.nist.gov/publication/get_pdf.cfm?pub_id=920870',
        applicability='Metabolic CO2 varies with age/activity and reference temperature/pressure. Here generation is an explicit cabin-volume scenario, not a railway legal limit or comfort approval.'),
}


def _number(value, name, *, minimum=None):
    if type(value) not in (int, float) or not math.isfinite(value) or minimum is not None and value < minimum:
        raise ValueError('finite bounded '+name+' required')
    return float(value)


def _identity(value):
    return sha256((json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False)+'\n').encode()).hexdigest()


def source_inputs(root=ROOT):
    root = Path(root)
    names = ['ferrite-maglev-study.toml', 'engineering/ferrite_maglev/station-structure.toml',
             'engineering/ferrite_maglev/pilot_product.py', 'engineering/ferrite_maglev/candidate_magnetics.py',
             'engineering/ferrite_maglev/data/candidate-parent-94ad.json',
             'engineering/ferrite_maglev/data/candidate-replaced-cartridges.json',
             'engineering/ferrite_maglev/data/candidate-retained-body-stock.json']
    values = {name: sha256((root/name).read_bytes()).hexdigest() for name in names}
    values['engineering/vehicle_optimisation/hvac.py'] = sha256(Path(__file__).read_bytes()).hexdigest()
    return dict(local_sha256=values, primary_references=deepcopy(REFERENCES), reviewed_date='2026-10-25')


def allocation_trace(root=ROOT):
    """Source accounting inference; no claim that 800 kg of HVAC was weighed."""
    root = Path(root)
    base = tomllib.loads((root/'ferrite-maglev-study.toml').read_text())
    body = tomllib.loads((root/'engineering/ferrite_maglev/station-structure.toml').read_text())
    parent = json.loads((root/'engineering/ferrite_maglev/data/candidate-parent-94ad.json').read_bytes())['configuration']
    removed = json.loads((root/'engineering/ferrite_maglev/data/candidate-replaced-cartridges.json').read_bytes())
    retained = json.loads((root/'engineering/ferrite_maglev/data/candidate-retained-body-stock.json').read_bytes())
    allowance = base['mass']['cabin_hvac_ducting']
    if allowance != body['vehicle']['hvac_kg'] or allowance != 800.:
        raise ValueError('Ancestor HVAC allocation changed; replacement must be reassessed')
    removed_copper = parent['magnetic']['winding_copper_kg_per_car']
    residual = parent['controlled_tare_kg']-removed['mass_kg_per_car']-removed_copper-retained['mass_kg_per_car']
    if residual < allowance or any('hvac' in row['id'].lower() for row in removed['parts']+retained['parts']):
        raise ValueError('HVAC overlap or insufficient residual prevents allowance replacement')
    power = base['power']
    split = [power['normal_suspension_allocation_kw'], power['normal_hvac_allocation_kw'], power['normal_auxiliary_allocation_kw']]
    if not math.isclose(sum(split), power['normal_hotel_kw_per_car']):
        raise ValueError('Normal total services no longer close')
    return dict(component_id='hvac', container_id='retained/unlocated-equipment-allocation',
        mass_kg=allowance, mass_state='ancestor allocation, not weighed equipment',
        origin='ferrite-maglev-study.toml:mass.cabin_hvac_ducting; station-structure.toml:vehicle.hvac_kg; pilot_product.mass_ledger row hvac',
        retained_residual_before_kg=residual, retained_residual_after_single_removal_kg=residual-allowance,
        removed_old_scopes=['exact cartridge stock', 'old three-coil copper'],
        scope_inference='Ancestor HVAC is not in the removed magnetic scopes or retained structural stock and remains within the unlocated residual. No individual installed HVAC geometry was recovered.',
        known_stock_removed_kg=0., normal_total_services_kWe=power['normal_hotel_kw_per_car'],
        normal_hvac_allocation_kWe=split[1], normal_other_services_allocation_kWe=split[0]+split[2],
        hot_total_services_kWe=power['hot_hotel_kw_per_car'], hot_hvac_split_kWe=None, **FLAGS)


INSTALLATION_ALLOWANCES = [
    dict(id='hvac/ducts-distribution', quantity=1, mass_range_kg=[30., 75.]),
    dict(id='hvac/mounts-local-reinforcement', quantity=1, mass_range_kg=[20., 55.]),
    dict(id='hvac/external-converter-cabling', quantity=1, mass_range_kg=[15., 45.]),
    dict(id='hvac/external-intake-filter-drain-interfaces', quantity=1, mass_range_kg=[15., 40.]),
    dict(id='hvac/external-piping-charge-connections', quantity=1, mass_range_kg=[5., 25.]),
]


def candidates():
    """Catalogue hardware plus explicit provisional installation bands per car."""
    definitions = [
        ('rail-lrc-one', 'tk-lrc', 'rail roof family', 1, [415., 480.], [26., 35.], 45., 50., [900., 1150.]),
        ('rail-lrc-two', 'tk-lrc', 'rail roof family', 2, [415., 480.], [26., 35.], 45., 50., [900., 1150.]),
        ('rail-msu-two', 'tk-msu', 'rail short-module roof', 2, [320., 330.], [15., 18.], 40., 49., [440., 600.]),
        ('bus-ul700-electric-two', 'konvekta', 'unqualified bus electric-compressor roof architecture', 2, [192., 192.], [33., 33.], None, 50., None),
        ('bus-ul500-electric-two', 'konvekta', 'unqualified bus electric-compressor roof architecture', 2, [162., 162.], [24., 24.], None, 50., None),
        ('bus-ul500-electric-three', 'konvekta', 'unqualified bus electric-compressor roof architecture', 3, [162., 162.], [24., 24.], None, 50., None),
        ('bus-ul700-electric-three', 'konvekta', 'unqualified bus electric-compressor roof architecture', 3, [192., 192.], [33., 33.], None, 50., None),
        ('rail-river-two', 'river', 'rail roof package', 2, None, [24.6, 24.6], None, None, None),
        ('rail-cpa-com1', 'cpa', 'rail roof monobloc', 1, [730., 730.], [36., 36.], None, 45., None),
        ('rail-coolaer-crw035', 'coolaer', 'rail roof package', 1, [550., 550.], [36.96, 36.96], None, None, None),
        ('rail-underfloor-custom', 'underfloor', 'custom split/underfloor architecture', 1, None, None, None, None, None),
    ]
    output = []
    additions = [sum(row['mass_range_kg'][i]*row['quantity'] for row in INSTALLATION_ALLOWANCES) for i in (0, 1)]
    for key, source, architecture, quantity, mass, capacity, full, maximum, fresh in definitions:
        unit_mass = None if mass is None else [quantity*x for x in mass]
        row = dict(id=key, source_id=source, architecture=architecture, units_per_car=quantity,
            package_unit_mass_range_kg=mass, package_hardware_mass_range_kg_per_car=unit_mass,
            package_capacity_kWthermal=None if capacity is None else [quantity*x for x in capacity],
            full_cooling_ambient_limit_C=full, published_operating_or_reduced_limit_C=maximum,
            rated_fresh_air_m3_h=None if fresh is None else [quantity*x for x in fresh],
            external_installation_allowances=deepcopy(INSTALLATION_ALLOWANCES),
            allowance_basis='Explicit design bands beyond package; not supplier measurements. External converter/cabling must be reconciled with retained auxiliaries; internal filters/refrigerant/fans are not counted again.',
            provisional_installed_mass_scenario_kg=None if unit_mass is None else [unit_mass[i]+additions[i] for i in (0, 1)],
            complete_installed_mass_kg=None,
            break_even_all_additional_hardware_mass_kg=None if unit_mass is None else [800.-unit_mass[1], 800.-unit_mass[0]],
            unknown_items=['order-specific package/charge scope', 'installed duct pressure and air balance', 'additional fresh-air treatment and filtration',
                           'enthalpy recovery equipment and fans', 'rail attachment/fire/EMC/shock adaptation', 'redundancy and failed-unit comfort'],
            package_electrical_input_kWe=None, **FLAGS)
        if source == 'konvekta':
            small = 'ul500' in key
            row.update(bus_only_not_rail_qualified=True, nominal_capacity_ambient_C=None,
                fresh_air_claim='100 percent fresh-air capability is advertised, but delivered flow/capacity/pressure at Baghdad conditions is unqualified',
                nominal_evaporator_air_m3_h=quantity*(4720. if small else 7080.),
                package_unit_envelope_m=[2.135 if small else 2.655, 2.083, .357],
                roof_projected_package_area_m2=quantity*(2.135 if small else 2.655)*2.083,
                installed_roof_access_CG_clearance_and_condenser_recirculation_verified=False,
                compressor_supply='400 V AC; 26 V DC auxiliary draw is not compressor/full-system input')
        if source == 'river':row.update(exact_rating_ambient_C=50., package_apparent_power_kVA=quantity*16.5)
        if source == 'coolaer':row.update(exact_rating_ambient_C=35., rating_return_air_C=28.,
            net_sensible_capacity_kWthermal=20.9, package_electrical_input_kWe=15.272)
        output.append(row)
    return output


def allocation_replacement(candidate, *, root=ROOT, already_removed_ids=()):
    """Only the exclusive hvac allocation can be removed, at most once."""
    if (any(not isinstance(key, str) or not key for key in already_removed_ids)
            or len(already_removed_ids) != len(set(already_removed_ids))
            or any('hvac' in key.lower() for key in already_removed_ids)):
        raise ValueError('HVAC allowance already removed or duplicate removal IDs')
    trace = allocation_trace(root)
    mass = candidate['provisional_installed_mass_scenario_kg']
    if mass is not None and (len(mass) != 2 or any(_number(x, 'replacement mass', minimum=0.) < 0 for x in mass) or mass[1] < mass[0]):
        raise ValueError('ordered nonnegative replacement mass interval required')
    return dict(remove_component_id='hvac', remove_mass_kg=trace['mass_kg'],
        remove_from_container_id=trace['container_id'], known_geometry_mass_removed_kg=0.,
        replacement_id=candidate['id'], replacement_mass_scenario_kg=mass,
        mass_replacement_numerically_applicable=mass is not None,
        mass_change_scenario_kg=None if mass is None else [x-trace['mass_kg'] for x in mass],
        remaining_residual_allocation_kg=trace['retained_residual_after_single_removal_kg'],
        combined_residual_and_replacement_scenario_kg=None if mass is None else
            [trace['retained_residual_after_single_removal_kg']+x for x in mass],
        other_services_battery_body_glazing_door_allocations_removed=False,
        complete_installed_mass_kg=None, scope='Unweighed allocation-replacement scenario, separate from known-stock optimisation', **FLAGS)


def moist_air(temperature_C, relative_humidity, pressure_Pa=101325.):
    """Simple moist-air enthalpy, valid only for this declared -20..60 C screen."""
    t = _number(temperature_C, 'air temperature')
    rh = _number(relative_humidity, 'relative humidity', minimum=0.)
    pressure = _number(pressure_Pa, 'pressure', minimum=1000.)
    if not -20 <= t <= 60 or rh > 1:raise ValueError('psychrometric screening domain exceeded')
    vapour = rh*610.94*math.exp(17.625*t/(t+243.04))
    if vapour >= pressure:raise ValueError('vapour pressure exceeds total pressure')
    w = .62198*vapour/(pressure-vapour)
    return dict(humidity_ratio_kg_per_kg_dry=w, enthalpy_J_per_kg_dry=1006*t+w*(2501000+1860*t),
                dry_air_density_kg_m3=(pressure-vapour)/(287.055*(t+273.15)))


def default_scenario(**updates):
    return dict(name='AW2-hot-dry-clear', passengers=120, outdoor_C=50., outdoor_RH=.15,
        indoor_C=26., indoor_RH=.50, pressure_Pa=101325., cabin_air_volume_m3=90.,
        glazing_m2=28., solar_factor=.82, glazing_U_W_m2K=5.7,
        incident_glazing_solar_W_m2=600., roof_solar_W_m2=900., roof_absorptivity=.5,
        outside_film_W_m2K=15., upper_core_m=.04, upper_core_lambda_W_mK=.031,
        thermal_bridge_UA_W_K=15., passengers_sensible_W_each=75., passengers_latent_W_each=55.,
        fresh_air_L_s_per_person=6., co2_generation_L_s_per_person_at_cabin=.005,
        outdoor_co2_ppm=420., initial_co2_ppm=420., stationary_duration_s=600.,
        doors_open=2, door_width_m=1.4, door_height_m=2.1, door_open_s=30., door_cycle_s=180.,
        door_effective_exchange_velocity_m_s=.20, closed_leak_m3_s=.03,
        sensible_recovery_effectiveness=0., latent_recovery_effectiveness=0.,
        recovery_total_pressure_Pa=0., recovery_fan_efficiency=.5,
        recovery_fan_heat_into_cabin_fraction=.5, unit_blower_heat_W=1000., internal_equipment_heat_W=1500.,
        system_COP_scenario=2.5) | updates


def heat_load(scenario):
    """Sensible/latent, average door cycle and stationary case, all per car.

    Ventilation is specified at cabin conditions. Door exchange is a declared
    effective outside-air flow, additional to ventilation, not measured CFD.
    Recovery acts only on the mechanically exhausted fresh-air stream.
    """
    base = default_scenario()
    if set(scenario)-set(base):raise ValueError('unsupported thermal scenario keys: '+str(sorted(set(scenario)-set(base))))
    s = base | scenario
    for key, value in s.items():
        if key != 'name':_number(value, key)
    if type(s['passengers']) is not int or not 0 <= s['passengers'] <= 160:
        raise ValueError('integer passenger case 0..160 required')
    if type(s['doors_open']) is not int or not 0 <= s['doors_open'] <= 4:
        raise ValueError('integer active door count 0..4 required')
    for key in ('glazing_m2', 'incident_glazing_solar_W_m2', 'roof_solar_W_m2', 'roof_absorptivity',
                'thermal_bridge_UA_W_K', 'passengers_sensible_W_each', 'passengers_latent_W_each',
                'fresh_air_L_s_per_person', 'door_open_s', 'door_effective_exchange_velocity_m_s',
                'closed_leak_m3_s', 'unit_blower_heat_W', 'internal_equipment_heat_W', 'recovery_total_pressure_Pa',
                'co2_generation_L_s_per_person_at_cabin', 'outdoor_co2_ppm', 'initial_co2_ppm', 'stationary_duration_s'):
        _number(s[key], key, minimum=0.)
    for key in ('door_cycle_s', 'outside_film_W_m2K', 'upper_core_m', 'upper_core_lambda_W_mK',
                'glazing_U_W_m2K', 'cabin_air_volume_m3', 'system_COP_scenario', 'recovery_fan_efficiency'):
        if s[key] <= 0:raise ValueError('positive '+key+' required')
    if s['door_width_m'] <= 0 or s['door_height_m'] <= 0:raise ValueError('positive door dimensions required')
    if (s['sensible_recovery_effectiveness'] > 0 or s['latent_recovery_effectiveness'] > 0) and s['recovery_total_pressure_Pa'] <= 0:
        raise ValueError('Recovery needs an explicit positive fan pressure-loss scenario')
    if s['door_open_s'] > s['door_cycle_s']:raise ValueError('door open time exceeds independent recurrence period')
    for key in ('solar_factor', 'sensible_recovery_effectiveness', 'latent_recovery_effectiveness',
                'recovery_fan_heat_into_cabin_fraction', 'recovery_fan_efficiency', 'roof_absorptivity'):
        if not 0 <= s[key] <= 1:raise ValueError('fraction outside 0..1: '+key)
    inside = moist_air(s['indoor_C'], s['indoor_RH'], s['pressure_Pa'])
    outside = moist_air(s['outdoor_C'], s['outdoor_RH'], s['pressure_Pa'])
    delta = s['outdoor_C']-s['indoor_C']
    fresh_cabin = s['passengers']*s['fresh_air_L_s_per_person']/1000.
    fresh_mass = fresh_cabin*inside['dry_air_density_kg_m3']
    fresh_outside = fresh_mass/outside['dry_air_density_kg_m3']
    door_duty = s['door_open_s']/s['door_cycle_s']
    door_outside = s['doors_open']*s['door_width_m']*s['door_height_m']*s['door_effective_exchange_velocity_m_s']*door_duty
    leak_mass = (door_outside+s['closed_leak_m3_s'])*outside['dry_air_density_kg_m3']
    def exchange(mass):
        sensible = mass*(1006+1860*outside['humidity_ratio_kg_per_kg_dry'])*delta
        latent = mass*(2501000+1860*s['indoor_C'])*(outside['humidity_ratio_kg_per_kg_dry']-inside['humidity_ratio_kg_per_kg_dry'])
        return sensible, latent
    ventilation_s, ventilation_l = exchange(fresh_mass)
    infiltration_s, infiltration_l = exchange(leak_mass)
    recovery_fan = s['recovery_total_pressure_Pa']*fresh_outside/s['recovery_fan_efficiency']
    # Gross wall/end shell minus four door apertures and 24 m² fixed glass;
    # door vision glass is already in the 28 m² glazing total.
    roof = floor = 17.*2.65
    wall = 2*17.*2.8+2*2.65*2.8-4*1.4*2.1-24.
    opaque_door = 4*1.4*2.1-(s['glazing_m2']-24.)
    if not 24 <= s['glazing_m2'] <= 24+4*1.4*2.1:raise ValueError('glazing and retained door apertures overlap')
    upper_U = 1/(.17+.004/.3+s['upper_core_m']/s['upper_core_lambda_W_mK'])
    floor_U = 1/(.17+.0045/.3+.06/.033)
    roof_skin = s['outdoor_C']+s['roof_absorptivity']*s['roof_solar_W_m2']/s['outside_film_W_m2K']
    sensible = dict(occupants=s['passengers']*s['passengers_sensible_W_each'],
        opaque_shell=(wall*upper_U+floor*floor_U+opaque_door*2.5+s['thermal_bridge_UA_W_K'])*delta,
        roof=roof*upper_U*(roof_skin-s['indoor_C']),
        glass_conduction=s['glazing_m2']*s['glazing_U_W_m2K']*delta,
        glass_solar=s['glazing_m2']*s['solar_factor']*s['incident_glazing_solar_W_m2'],
        mechanical_fresh_air=ventilation_s*(1-s['sensible_recovery_effectiveness']),
        doors_and_leakage=infiltration_s, unit_blower=s['unit_blower_heat_W'],
        internal_equipment=s['internal_equipment_heat_W'], recovery_fan=recovery_fan*s['recovery_fan_heat_into_cabin_fraction'])
    latent = dict(occupants=s['passengers']*s['passengers_latent_W_each'],
        mechanical_fresh_air=ventilation_l*(1-s['latent_recovery_effectiveness']), doors_and_leakage=infiltration_l)
    raw_s, raw_l = sum(sensible.values()), sum(latent.values())
    total = (max(raw_s, 0.)+max(raw_l, 0.))/1000.
    generation = s['passengers']*s['co2_generation_L_s_per_person_at_cabin']/1000.
    if fresh_cabin:
        co2_steady = s['outdoor_co2_ppm']+generation/fresh_cabin*1e6
        co2_time = co2_steady+(s['initial_co2_ppm']-co2_steady)*math.exp(-fresh_cabin*s['stationary_duration_s']/s['cabin_air_volume_m3'])
    else:
        co2_steady = None if generation else s['outdoor_co2_ppm']
        co2_time = s['initial_co2_ppm']+generation*s['stationary_duration_s']/s['cabin_air_volume_m3']*1e6
    return dict(name=s['name'], scenario=s, sensible_components_W=sensible, latent_components_W=latent,
        sensible_kWthermal=max(raw_s, 0.)/1000., latent_kWthermal=max(raw_l, 0.)/1000., total_kWthermal=total,
        signed_net_heat_W=raw_s+raw_l, heating_required_W=max(-raw_s, 0.), humidification_required_W=max(-raw_l, 0.),
        fresh_air_cabin_m3_s=fresh_cabin, fresh_air_cabin_m3_h=fresh_cabin*3600., fresh_air_outside_m3_s=fresh_outside,
        dry_fresh_air_kg_s=fresh_mass, door_average_outside_air_m3_s=door_outside, door_open_fraction=door_duty,
        unrecovered_ventilation_sensible_W=ventilation_s, unrecovered_ventilation_latent_W=ventilation_l,
        recovery_fan_extra_kWe=recovery_fan/1000., recovery_hardware_mass_kg=None,
        co2_steady_mechanical_only_ppm=co2_steady, co2_after_stationary_period_ppm=co2_time,
        co2_legal_limit_ppm=None, ventilation_compliance_established=False,
        demand_control_ventilation_controller_validated=False,
        roof_solair_temperature_C=roof_skin, upper_panel_U_W_m2K=upper_U,
        additional_upper_core_mass_scenario_kg=max(0., s['upper_core_m']-.04)*(wall+roof)*80.,
        additional_insulation_interfaces_mass_kg=None if s['upper_core_m'] != .04 else 0.,
        HVAC_electric_scenario_kWe=total/s['system_COP_scenario']+recovery_fan/1000.,
        electrical_basis='Declared whole-unit thermal/electrical ratio; not a manufacturer hot-condition power map. Recovery fan is additional.',
        complete_services_kWe=None, scope='Occupied one-car steady-period screen; no comfort, transient pull-down, fouling or failed-unit validation', **FLAGS)


def assess(candidate, load):
    """Necessary catalogue comparisons; missing derating never becomes full output."""
    ambient = load['scenario']['outdoor_C']
    nominal = candidate['package_capacity_kWthermal']
    full, maximum = candidate['full_cooling_ambient_limit_C'], candidate['published_operating_or_reduced_limit_C']
    exact = candidate.get('exact_rating_ambient_C')
    band, domain = None, 'unknown-rating-domain'
    if maximum is not None and ambient > maximum:
        domain = 'outside-published-ambient-envelope'
    elif full is not None and ambient <= full:
        band, domain = nominal, 'catalogue-full-output-family-range'
    elif full is not None and maximum is not None and ambient <= maximum:
        band, domain = [0., nominal[1]], 'reduced-output-curve-unknown'
    elif exact is not None and math.isclose(ambient, exact):
        band, domain = nominal, 'published-rating-point-only'
    thermal = 'unknown'
    if domain == 'outside-published-ambient-envelope':thermal = 'fail-ambient-domain'
    elif band is not None and band[1] < load['total_kWthermal']:thermal = 'necessary-capacity-fail'
    elif band is not None and band[0] >= load['total_kWthermal']:thermal = 'conditional-nameplate-covers-load'
    fresh = candidate['rated_fresh_air_m3_h']
    missing_air = None if fresh is None else max(0., load['fresh_air_cabin_m3_h']-fresh[1])
    return dict(candidate_id=candidate['id'], scenario=load['name'], ambient_rating_disposition=domain,
        available_capacity_band_kWthermal=band, needed_kWthermal=load['total_kWthermal'], thermal_screen=thermal,
        required_kWthermal_per_unit=load['total_kWthermal']/candidate['units_per_car'],
        required_fraction_of_nominal_upper_capacity=None if nominal is None else load['total_kWthermal']/nominal[1],
        nominal_capacity_margin_kWthermal=None if nominal is None else nominal[1]-load['total_kWthermal'],
        additional_fresh_air_treatment_needed_m3_h=missing_air,
        sensible_rating_margin_kWthermal=None if candidate.get('net_sensible_capacity_kWthermal') is None else
            candidate['net_sensible_capacity_kWthermal']-(load['sensible_kWthermal']-load['scenario']['unit_blower_heat_W']/1000.),
        fresh_air_reference_conditions_and_pressure_confirmed=False,
        complete_mass_and_electric_input_known=False, matched_return_air_humidity_and_derating_validated=False, **FLAGS)


def study(root=ROOT):
    trace = allocation_trace(root)
    scenarios = [
        default_scenario(name='AW2-40C-clear', outdoor_C=40., outdoor_RH=.25),
        default_scenario(name='AW2-50C-clear'),
        default_scenario(name='AW2-50C-solar-control', solar_factor=.55),
        default_scenario(name='AW2-50C-solar-control-recovery', solar_factor=.55, sensible_recovery_effectiveness=.6,
                         latent_recovery_effectiveness=.4, recovery_total_pressure_Pa=200.),
        default_scenario(name='AW2-50C-DCV-3L-scenario', solar_factor=.55, fresh_air_L_s_per_person=3.),
        default_scenario(name='AW2-50C-extra20mm-core', solar_factor=.55, upper_core_m=.06),
        default_scenario(name='AW3-50C-humid-closed-stationary', passengers=160, outdoor_RH=.30, doors_open=0, solar_factor=.55),
        default_scenario(name='AW3-50C-humid-doors60s', passengers=160, outdoor_RH=.30, door_open_s=60., solar_factor=.55),
        default_scenario(name='AW3-50C-humid-closed-recovery', passengers=160, outdoor_RH=.30, doors_open=0, solar_factor=.55,
                         sensible_recovery_effectiveness=.6, latent_recovery_effectiveness=.4, recovery_total_pressure_Pa=200.),
        default_scenario(name='AW3-50C-humid-doors60s-recovery', passengers=160, outdoor_RH=.30, door_open_s=60., solar_factor=.55,
                         sensible_recovery_effectiveness=.6, latent_recovery_effectiveness=.4, recovery_total_pressure_Pa=200.),
        default_scenario(name='AW2-50C-door-recurrence120s', door_cycle_s=120., solar_factor=.55),
    ]
    loads = [heat_load(s) for s in scenarios]
    options = candidates()
    return dict(schema='osr-vehicle-hvac-optimisation/1', context=CONTEXT, source_inputs=source_inputs(root),
        allocation_trace=trace, candidates=options, loads=loads,
        comparisons=[assess(candidate, load) for candidate in options for load in loads],
        allocation_replacements=[allocation_replacement(candidate, root=root) for candidate in options],
        normal_services_comparators=[dict(scenario=load['name'], retained_non_HVAC_allocation_kWe=trace['normal_other_services_allocation_kWe'],
            modeled_HVAC_kWe=load['HVAC_electric_scenario_kWe'],
            total_scenario_kWe=trace['normal_other_services_allocation_kWe']+load['HVAC_electric_scenario_kWe'],
            scope='Retained normal 10 kW support + 5 kW auxiliaries only; new support/auxiliary duty must replace those allocations separately') for load in loads],
        custom_design_target=dict(required_50C_thermal_kW_by_case={load['name']:load['total_kWthermal'] for load in loads},
            complete_installed_HVAC_mass_for_allocation_saving_kg='strictly below 800, including all new equipment and rail adaptation',
            bus_UL700_two_unit_extra_mass_headroom_kg=416.,
            unknown=['50 C capacity/power maps', 'latent/sensible split', 'delivered fresh air/filter pressure', 'recovery mass and fouling',
                     'stationary solar test', 'rails fire/shock/EMC', 'complete measured installation and redundant comfort']),
        lighter_complete_HVAC_proven=False, **FLAGS)
