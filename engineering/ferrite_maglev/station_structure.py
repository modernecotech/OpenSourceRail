"""Quantity-derived station-powered body/civil candidates; no engineering release.

Point-dipole calculations benchmark orientation methods in air. They do not
predict ferrite/iron railway lift, propulsion, demagnetisation or control power.
Civil properties are gross elastic screens, not prestress/ground design.
"""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import json
import math
import os
import tomllib

ROOT = Path(__file__).resolve().parents[2]
INPUT = Path(__file__).with_name('station-structure.toml')
OUTPUT = ROOT / 'docs/design-engine/ferrite-maglev/station-structure'
FLAGS = dict(design_complete=False, physical_validation=False,
             manufacturing_release=False, physical_release=False)
FILES = {'result.json', 'comparison.svg', 'README.md'}
MAX_BYTES = 8 * 1024 * 1024
BODY_HOLDS = [
    'orthotropic-laminate-and-core-property-cards', 'members-hardpoints-and-local-joint-sizing',
    'static-buckling-fatigue-creep-and-coupler-crash-loads', 'fire-smoke-heat-and-repair-qualification',
    'doors-dwell-evacuation-and-platform-interface', 'weighed-equipped-mass-cg-and-inertia',
]
CIVIL_HOLDS = [
    'prestress-rebar-cover-end-block-and-connection-detail', 'shear-torsion-fatigue-and-time-effects',
    'moving-six-car-and-cartridge-loads-relative-magnetic-gap', 'wind-seismic-braking-and-capture-loads',
    'ground-groundwater-utilities-settlement-and-foundation-selection',
    'lifting-transport-temporary-stability-and-strength-release',
    'rail-joints-anchors-bearings-survey-and-evacuation',
]
PRODUCTION_HOLDS = [
    'qualified-transfer-and-demould-strength', 'connection-grout-strength-before-loading',
    'surveyed-support-and-bearing-release', 'crane-capacity-at-radius-and-ground-support',
    'accepted-delivery-route-and-handling', 'final-rail-joint-and-instance-qa-acceptance',
    'measured-mould-and-crew-cycles',
]


def _positive(value, name, *, zero=False):
    if type(value) not in (int, float) or not math.isfinite(value) or (value < 0 if zero else value <= 0):
        raise ValueError('finite ' + ('nonnegative ' if zero else 'positive ') + name + ' required')
    return value


def _count(value, name, *, zero=False):
    if type(value) is not int or value < (0 if zero else 1):
        raise ValueError('integer ' + name + ' required')
    return value


def load():
    a = tomllib.loads(INPUT.read_text())
    if a.get('schema') != 'osr-station-structure-study/1':
        raise ValueError('station structure schema required')
    for section in ('body', 'vehicle', 'magnetic', 'civil', 'cost', 'production'):
        for name, value in a[section].items():
            if type(value) in (int, float):
                _positive(value, section + '.' + name)
    for case in a['body']['cases'].values():
        for name, value in case.items():
            _positive(value, name)
    for values in (a['body']['core_substitution_density_kg_m3'],
                   a['magnetic']['support_gap_study_m'], a['civil']['bearing_pressure_screens_kpa']):
        if not 1 <= len(values) <= 16:
            raise ValueError('bounded sensitivity list required')
        for value in values:
            _positive(value, 'sensitivity')
    if a['magnetic']['force_map_validated'] is not False or a['magnetic']['automatic_paper_gain_credit'] is not False:
        raise ValueError('no qualified force or paper-gain adapter supplied')
    if set(a['body']['cases']) != {'central', 'stretch', 'conservative'}:
        raise ValueError('three identified body cases required')
    _count(a['body']['doors_per_side'], 'doors per side')
    for name in ('cars', 'normal_passengers', 'maximum_passengers'):
        _count(a['vehicle'][name], name)
    if a['vehicle']['maximum_passengers'] < a['vehicle']['normal_passengers']:
        raise ValueError('maximum passengers below normal loading')
    for name in ('shifts_per_available_day', 'mould_positions', 'foundation_crews',
                 'accepted_beam_buffer', 'cranes_per_front'):
        _count(a['production'][name], name)
    cv = a['civil']
    if cv['column_inner_diameter_m'] >= cv['column_outer_diameter_m'] or cv['column_solid_end_total_m'] > cv['column_height_m']:
        raise ValueError('positive hollow column and valid solid end zones required')
    _count(a['magnetic']['cartridges'], 'cartridges')
    p = a['production']
    if not 0 < p['availability'] <= 1 or not 0 < p['factory_utilisation_yield'] <= 1:
        raise ValueError('availability and yield must be within (0,1]')
    if p['shifts_per_available_day'] * p['hours_per_shift'] > 24 or p['workdays_per_week'] > 7:
        raise ValueError('invalid working calendar')
    return a


def _vehicle(c, a):
    """Only explicitly shared formation/loading inputs override study defaults."""
    v = deepcopy(a['vehicle']); b = deepcopy(a['body'])
    if c is not None:
        supplied = c.get('vehicle', {})
        for source, target in [('nominal_car_length_m', 'length_m'), ('nominal_car_width_m', 'width_m')]:
            if source in supplied:
                b[target] = _positive(supplied[source], source)
        for source, target in [('cars_per_train', 'cars'), ('aw2_passengers_per_car', 'normal_passengers'),
                               ('aw3_passengers_per_car', 'maximum_passengers'), ('passenger_mass_screen_kg', 'passenger_mass_kg')]:
            if source in supplied:
                v[target] = _positive(supplied[source], source)
        for name in ('cars', 'normal_passengers', 'maximum_passengers'):
            _count(v[name], name)
        if v['maximum_passengers'] < v['normal_passengers']:
            raise ValueError('maximum passengers below normal loading')
    return v, b


def body(c=None, case='central'):
    a = load(); v, b = _vehicle(c, a)
    if case not in b['cases']:
        raise ValueError('unknown equipped-body case')
    s = b['cases'][case]; length, width, height = (b[k] for k in ('length_m', 'width_m', 'height_m'))
    door_count = 2*b['doors_per_side']
    upper_area = 2*length*height + 2*width*height + length*width - door_count*b['door_width_m']*b['door_height_m'] - b['fixed_side_glazing_area_m2'] - b['combined_end_opening_area_m2']
    floor_area = length*width
    _positive(upper_area, 'net upper-shell area')
    panel_rows = []
    for name, area, faces, core, density, bond in [
            ('upper-shell', upper_area, 2*s['upper_face_each_m'], s['upper_core_m'], s['upper_core_density_kg_m3'], s['upper_bond_finish_kg_m2']),
            ('floor', floor_area, s['floor_faces_total_m'], s['floor_core_m'], s['floor_core_density_kg_m3'], s['floor_bond_finish_kg_m2'])]:
        row = dict(id=name, net_area_m2=area, face_thickness_total_m=faces, core_thickness_m=core,
                   face_density_kg_m3=b['face_density_kg_m3'], core_density_kg_m3=density,
                   face_laminate_kg=area*faces*b['face_density_kg_m3'], core_kg=area*core*density,
                   bonding_finish_kg=area*bond)
        row['calculated_mass_kg'] = row['face_laminate_kg'] + row['core_kg'] + row['bonding_finish_kg']
        row['mass_per_area_kg_m2'] = row['calculated_mass_kg']/area
        panel_rows.append(row)
    # Ownership is exclusive. These are target allowances until sized parts exist.
    allocations = [dict(id=name, owner='equipped-body', mass_kg=s[name], basis='unsized allowance') for name in
                   ('primary_load_paths_kg', 'opening_joints_inserts_kg', 'doors_kg', 'fixed_glazing_kg', 'interior_kg', 'extra_treatments_kg')]
    panel_mass = sum(r['calculated_mass_kg'] for r in panel_rows)
    equipped = panel_mass + sum(r['mass_kg'] for r in allocations)
    other = [('ferrite', v['ferrite_kg']), ('support-guidance-carriers-coils-drives-sensors', v['support_guidance_equipment_kg']),
             ('capture-landing-emergency-braking', v['capture_landing_braking_kg']),
             ('services-battery', v['services_battery_kwh']*1000/v['pack_specific_energy_wh_kg']),
             ('hvac', v['hvac_kg']), ('auxiliary-controls-wiring', v['auxiliary_controls_wiring_kg']),
             ('couplers-gangways-solar', v['couplers_gangways_solar_kg']), ('growth-reserve', v['growth_reserve_kg'])]
    tare = s['rounded_equipped_target_kg'] + sum(value for _, value in other)
    nominal = [dict(id='equipped-body-target', owner='equipped-body', mass_kg=s['rounded_equipped_target_kg'])]
    nominal += [dict(id=name, owner='magnetics' if name.startswith(('ferrite', 'support-guidance')) else 'vehicle-equipment', mass_kg=value) for name, value in other]
    core_changes = [dict(substitution_density_kg_m3=density,
                        added_mass_kg=sum(r['net_area_m2']*r['core_thickness_m']*(density-r['core_density_kg_m3']) for r in panel_rows),
                        qualification_transferred=False) for density in b['core_substitution_density_kg_m3']]
    faces = sum(r['face_laminate_kg'] for r in panel_rows)
    # An illustrative constituent-density mixture, not a process fibre fraction.
    glass_volume_fraction = (b['face_density_kg_m3']-1200)/(2550-1200)
    return dict(schema='osr-gfrp-body-takeoff/1', case=case,
        envelope_m=dict(length=length, width=width, height=height), passenger_doors_per_car=door_count,
        door_configuration=dict(per_side=b['doors_per_side'], opening_width_m=b['door_width_m'], opening_height_m=b['door_height_m']),
        openings=dict(fixed_side_glazing_area_m2=b['fixed_side_glazing_area_m2'], combined_end_opening_area_m2=b['combined_end_opening_area_m2']),
        panels=panel_rows, unsized_body_allocations=allocations, calculated_equipped_mass_kg=equipped,
        rounded_equipped_target_kg=s['rounded_equipped_target_kg'], target_rounding_difference_kg=s['rounded_equipped_target_kg']-equipped,
        structural_shell_calculated_kg=panel_mass+s['primary_load_paths_kg']+s['opening_joints_inserts_kg'],
        vehicle_mass_ledger=nominal, tare_target_kg=tare, calculated_tare_with_unrounded_panels_kg=tare+equipped-s['rounded_equipped_target_kg'],
        aw2_target_kg=tare+v['normal_passengers']*v['passenger_mass_kg'], aw3_target_kg=tare+v['maximum_passengers']*v['passenger_mass_kg'],
        cars=v['cars'], train_tare_target_kg=tare*v['cars'], train_aw3_target_kg=(tare+v['maximum_passengers']*v['passenger_mass_kg'])*v['cars'],
        payload_floor_average_kpa=v['maximum_passengers']*v['passenger_mass_kg']*9.81/floor_area/1000,
        interface_ownership=[dict(id='body-hardpoint', included_in='primary_load_paths_kg', excludes='magnetic carrier and cartridge'),
                             dict(id='opening-local-inserts', included_in='opening_joints_inserts_kg', excludes='complete door mechanisms'),
                             dict(id='magnetic-carrier', included_in='support-guidance-carriers-coils-drives-sensors', excludes='body-side hardpoint'),
                             dict(id='door-glazing', included_in='doors_kg', excludes='fixed_glazing_kg')],
        purchasing_quantities=dict(face_laminate_kg=faces, core_kg=sum(r['core_kg'] for r in panel_rows),
            bonding_surface_kg=sum(r['bonding_finish_kg'] for r in panel_rows), illustrative_glass_kg=faces/b['face_density_kg_m3']*glass_volume_fraction*2550,
            illustrative_resin_kg=faces/b['face_density_kg_m3']*(1-glass_volume_fraction)*1200, cutting_waste_fraction=None,
            actual_fibre_fraction=None, tooling_and_consumables=None),
        core_density_substitutions=core_changes, cg_m=None, inertia_kg_m2=None, holds=BODY_HOLDS,
        material_selected=False, mass_measured=False, complete_part_bom=False, **FLAGS)


def ring_benchmark(count=16, heights=(0., .4, .8)):
    """Unit dipoles in air; maximize one target Bx component at each height."""
    _count(count, 'ring dipoles')
    if not 4 <= count <= 128 or not 1 <= len(heights) <= 16:
        raise ValueError('bounded ring benchmark required')
    rows = []
    for h in heights:
        _positive(h, 'dimensionless target height', zero=True)
        classical = best = 0.
        for i in range(count):
            theta = 2*math.pi*i/count; distance = math.sqrt(1+h*h)
            unit = [-math.cos(theta)/distance, -math.sin(theta)/distance, h/distance]
            response = [3*unit[0]*unit[j]-(1 if j == 0 else 0) for j in range(3)]
            classical += (response[0]*math.cos(2*theta)+response[1]*math.sin(2*theta))/distance**3
            best += math.sqrt(sum(x*x for x in response))/distance**3
        if classical <= 0:
            raise ValueError('comparison field is not positive')
        rows.append(dict(target_height_over_radius=h, optimized_to_classical_field=best/classical,
                         target_field_gain_percent=100*(best/classical-1)))
    return dict(scope='Air-core point-dipole ring Bx reference; no iron, ferrite grade, finite cuboid force, rail lift or mass saving',
                dipoles=count, cases=rows, railway_force_gain=None, automatic_gain_credit=False, **FLAGS)


def linear_candidates():
    """Finite block inventories and orientation seeds; no rail field solution."""
    a = load(); m = a['magnetic']; v = a['vehicle']; count = 20
    length = 1.; block_length = length/count
    volume = v['ferrite_kg']/m['cartridges']/m['ferrite_density_kg_m3']
    width = .5; thickness = volume/(length*width); gap = .008
    wavelength = 2*m['pole_pitch_study_m']
    centres = [(i+.5)*block_length-length/2 for i in range(count)]
    patterns = []
    for name in ('stock-four-orientation-halbach', 'segmented-linear-halbach', 'finite-block-point-dipole-seed', 'alternating-pole-iron-backed'):
        blocks = []
        for i, x in enumerate(centres):
            phase = 2*math.pi*x/wavelength
            if name == 'stock-four-orientation-halbach':
                angle = round(phase/(math.pi/2))*(math.pi/2); direction = [math.sin(angle), 0., math.cos(angle)]
            elif name == 'segmented-linear-halbach':
                direction = [math.sin(phase), 0., math.cos(phase)]
            elif name == 'alternating-pole-iron-backed':
                direction = [0., 0., 1. if math.cos(phase) >= 0 else -1.]
            else:
                gradient = [0., 0., 0.]
                # Target alternating Bz over the cartridge, in air. Each source
                # moment aligns with its linear objective gradient. It remains
                # an initial seed for finite-cuboid/steel/coil optimisation.
                for target in centres:
                    delta = [target-x, 0., thickness/2+gap]
                    distance = math.sqrt(sum(z*z for z in delta)); unit = [z/distance for z in delta]
                    weight = math.cos(2*math.pi*target/wavelength)
                    for axis in range(3):
                        gradient[axis] += weight*(3*unit[2]*unit[axis]-(1 if axis == 2 else 0))/distance**3
                norm = math.sqrt(sum(z*z for z in gradient))
                direction = [z/norm for z in gradient]
            blocks.append(dict(id=f'{name}/block-{i:02d}', size_m=[block_length, width, thickness],
                               centre_m=[x, 0., 0.], magnetisation_unit_vector=direction))
        patterns.append(dict(id=name, blocks=blocks, ferrite_volume_m3=volume,
            ferrite_mass_kg=volume*m['ferrite_density_kg_m3'], total_car_allocation_if_repeated_kg=volume*m['ferrite_density_kg_m3']*m['cartridges'],
            distinct_orientation_count=len({tuple(round(z, 8) for z in b['magnetisation_unit_vector']) for b in blocks}),
            needs_return_steel=name == 'alternating-pole-iron-backed', return_steel_geometry=None,
            support_force_n=None, propulsion_force_n=None, loss_w=None, rail_force_validated=False))
    return dict(scope='One 1 m cartridge seed, repeated 24 times only as a volume budget; finite block locations and dipole orientation initial estimates, no nonlinear magnetic solution',
                pole_pitch_study_m=m['pole_pitch_study_m'], effective_support_area_m2=None,
                shared_support_propulsion_demonstrated=False, candidates=patterns, **FLAGS)


def section(width, depth, web, flange):
    for name, value in [('width', width), ('depth', depth), ('web', web), ('flange', flange)]:
        _positive(value, name)
    if width <= 2*web or depth <= 2*flange:
        raise ValueError('positive box void required')
    area = width*depth-(width-2*web)*(depth-2*flange)
    ix = (width*depth**3-(width-2*web)*(depth-2*flange)**3)/12
    iy = (depth*width**3-(depth-2*flange)*(width-2*web)**3)/12
    mid_area = (width-web)*(depth-flange)
    torsion = 4*mid_area**2/(2*(width-web)/flange+2*(depth-flange)/web)
    return dict(width_m=width, depth_m=depth, web_m=web, flange_m=flange,
                area_m2=area, vertical_inertia_m4=ix, lateral_inertia_m4=iy, thin_wall_torsion_j_m4=torsion)


def civil(c=None, *, width=None, depth=None, web=None, flange=None, span=None, pier_height=None):
    a = load(); cv = a['civil']; rho = cv['concrete_density_kg_m3']
    width, depth, web, flange, span, height = [default if value is None else value for value, default in
        [(width, cv['width_m']), (depth, cv['depth_m']), (web, cv['web_m']), (flange, cv['flange_m']),
         (span, cv['span_m']), (pier_height, cv['column_height_m'])]]
    s = section(width, depth, web, flange)
    for name, value in [('span', span), ('pier height', height)]:
        _positive(value, name)
    infill = cv['end_infill_each_m']
    if span <= 2*infill or height < cv['column_solid_end_total_m']:
        raise ValueError('end zones exceed member length')
    concrete = s['area_m2']*span+2*infill*(width-2*web)*(depth-2*flange)
    rail = cv['reaction_rail_kg_per_direction_m']*span
    loaded = body(c)['aw3_target_kg']
    length = body(c)['envelope_m']['length']
    line_live = loaded/length
    q = (s['area_m2']*rho+cv['reaction_rail_kg_per_direction_m']+line_live)*9.81
    deflection = 5*q*span**4/(384*cv['concrete_young_pa']*s['vertical_inertia_m4'])
    do = cv['column_outer_diameter_m']; di = cv['column_inner_diameter_m']; solid = cv['column_solid_end_total_m']
    column = math.pi/4*((do**2-di**2)*(height-solid)+do**2*solid)
    cap = cv['cap_volume_m3']
    # End infills affect volume/reactions. Deflection remains the stated gross
    # middle-section UDL screen; actual moving loads and variable EI are open.
    superstructure = 2*(concrete*rho+rail+line_live*span)*9.81/1000
    foundation_top = superstructure+(column+cap)*rho*9.81/1000
    footing_unit_pressure = rho*9.81/1000*cv['footing_thickness_m']
    footing_screens = []
    for pressure in cv['bearing_pressure_screens_kpa']:
        area = foundation_top/(pressure-footing_unit_pressure) if pressure > footing_unit_pressure else None
        footing_screens.append(dict(assumed_gross_allowable_kpa=pressure, axial_only_required_area_m2=area,
                                   axial_only_square_side_m=math.sqrt(area) if area else None, ground_evidence=False))
    footing_side = cv['footing_square_side_m']; moment = cv['base_moment_study_knm']
    max_pressure = foundation_top/footing_side**2+footing_unit_pressure+6*moment/footing_side**3
    min_pressure = foundation_top/footing_side**2+footing_unit_pressure-6*moment/footing_side**3
    return dict(schema='osr-station-civil-quantity-study/1', section=s, span_m=span,
        beam=dict(middle_concrete_area_m2=s['area_m2'], end_infill_each_m=infill, end_infill_total_m3=concrete-s['area_m2']*span,
                  concrete_m3=concrete, reaction_iron_kg=rail, concrete_plus_iron_kg=concrete*rho+rail,
                  complete_lift_mass_kg=None, attachment_reinforcement_prestress_mass_kg=None,
                  rigging_mass_kg=None, gross_udl_deflection_m=deflection,
                  live_udl_increment_m=5*line_live*9.81*span**4/(384*cv['concrete_young_pa']*s['vertical_inertia_m4']),
                  concrete_m3_continuous_dual_km=concrete*2000/span),
        supports=dict(beam_centres_m=cv['beam_centres_m'], column_height_m=height, hollow_column_m3=column,
                      column_kg=column*rho, cap_m3=cap, cap_kg=cap*rho,
                      superstructure_shared_gravity_kn=superstructure, foundation_top_gravity_kn=foundation_top,
                      continuous_supports_per_route_km=1000/span, beam_deliveries_per_route_km=2000/span,
                      isolated_integer_span_count=math.ceil(1000/span), isolated_supports_for_that_count=math.ceil(1000/span)+1),
        foundation_families=[dict(id='shallow', quantity_basis='bearing/settlement/overturning/socket study; no ground selected',
            illustrative_concrete_m3=footing_side**2*cv['footing_thickness_m']),
            dict(id='single-shaft', shaft_diameter_m=None, shaft_depth_m=None, quantity_m3=None),
            dict(id='pile-group', pile_count=None, pile_length_m=None, cap_m3=None)],
        qualified_foundation_selection=None, footing_sensitivity=dict(axial_only=footing_screens,
            square_side_m=footing_side, thickness_m=cv['footing_thickness_m'], assumed_base_moment_knm=moment,
            maximum_pressure_kpa=max_pressure, minimum_pressure_kpa=min_pressure,
            no_tension_screen_pass=min_pressure>=0, bearing_criterion_accepted=False),
        loading=dict(aw3_mass_kg_per_car=loaded, gross_concrete_modulus_pa=cv['concrete_young_pa'],
                     live_load_model='uniform body-length density, not a moving cartridge/full-consist load model'),
        relative_magnetic_gap_error_m=None, construction_stage_strength_verified=False, holds=CIVIL_HOLDS, **FLAGS)


def civil_costs():
    """Reconcile the supplied target-rate exercise; no automatic weight savings."""
    a = load(); cv = a['civil']; r = a['cost']; rail = 2000*cv['reaction_rail_kg_per_direction_m']
    counts = dict(supports=1000/cv['span_m'], beams=2000/cv['span_m'])
    rows = []
    def add(identity, qty0, qty1, rate0, rate1, unit):
        rows.append(dict(id=identity, unit=unit, baseline_quantity=qty0, target_quantity=qty1,
                         baseline_rate_usd=rate0, target_rate_usd=rate1,
                         baseline_usd=qty0*rate0, target_usd=qty1*rate1, supplier_quote=False, accepted=False))
    baseline_concrete = section(.8, 1.6, .15, .18)['area_m2']*2000
    target_concrete = cv['budget_effective_area_m2']*2000
    add('beam-concrete', baseline_concrete, target_concrete, r['concrete_cast_cure_usd_m3'], r['concrete_cast_cure_usd_m3'], 'm3')
    add('reinforcement-allowance', baseline_concrete*r['reinforcement_intensity_kg_m3'], target_concrete*r['reinforcement_intensity_kg_m3'], r['reinforcement_fabricated_usd_kg'], r['reinforcement_fabricated_usd_kg'], 'kg')
    add('passive-rail', rail, rail, r['passive_rail_usd_kg'], r['passive_rail_usd_kg'], 'kg')
    for identity, count, key, unit in [('supports', counts['supports'], 'support', 'shared support'),
            ('delivery', counts['beams'], 'delivery', 'beam'), ('erection', counts['beams'], 'erection', 'beam'),
            ('temporary', counts['supports'], 'temporary', 'support'), ('alignment', 2000, 'alignment', 'direction-m')]:
        suffix = dict(support='_usd', delivery='_usd_beam', erection='_usd_beam', temporary='_usd_support', alignment='_usd_direction_m')[key]
        add(identity, count, count, r['baseline_'+key+suffix], r['target_'+key+suffix], unit)
    for identity, key in [('access', 'access'), ('traffic', 'traffic')]:
        add(identity, 1, 1, r['baseline_'+key+'_usd_km'], r['target_'+key+'_usd_km'], 'route-km')
    for identity, key in [('qa', 'route_qa_usd_km'), ('ordinary-utilities', 'ordinary_utilities_usd_km')]:
        add(identity, 1, 1, r[key], r[key], 'route-km')
    baseline = sum(x['baseline_usd'] for x in rows); target = sum(x['target_usd'] for x in rows)
    nonrail0 = baseline-rail*r['passive_rail_usd_kg']; nonrail1 = target-rail*r['passive_rail_usd_kg']
    exact = civil()['beam']['concrete_m3_continuous_dual_km']
    exact_target = target+(exact-target_concrete)*(r['concrete_cast_cure_usd_m3']+r['reinforcement_intensity_kg_m3']*r['reinforcement_fabricated_usd_kg'])
    return dict(schema='osr-station-civil-target-cost/1', unit='USD_per_two_direction_route_km', rows=rows,
        baseline_listed_scope_usd=baseline, target_listed_scope_usd=target,
        target_from_exact_end_infill_geometry_usd=exact_target, exact_concrete_m3=exact, rounded_budget_concrete_m3=target_concrete,
        saving_usd=baseline-target, saving_fraction=1-target/baseline,
        non_rail_saving_fraction=1-nonrail1/nonrail0,
        support_rate_change_share_of_saving=(r['baseline_support_usd']-r['target_support_usd'])*counts['supports']/(baseline-target),
        estimating_reserve_fraction=r['estimating_reserve_fraction'],
        target_plus_reserve_usd=target*(1+r['estimating_reserve_fraction']),
        historical_comparator='v0.5.1 ordinary no-walkway quantity/rate allowance; existing narrow beams, no end infills',
        conditional_rail_cases=[dict(reduction_fraction=x, target_listed_scope_usd=target-rail*r['passive_rail_usd_kg']*x,
                                     demonstrated=False, credited_to_primary=False) for x in (0., .2, .3)],
        support_price_cases=[dict(average_support_usd=x, target_listed_scope_usd=target+(x-r['target_support_usd'])*counts['supports']) for x in (22000., 28000., 35000.)],
        exclusions=['stations-and-station-LSM-converters-grid-and-charging', 'complete-evacuation-and-access',
                    'land-air-rights-major-crossings-and-diversions', 'depot-terminal-recovery-and-train-fleet',
                    'development-qualification-factory-capital', 'unpriced-overhead-profit-tax-duty-finance-and-risk'],
        complete_installed_price_usd=None, costs_are_supplier_quotes=False, weight_proportional_support_saving=False, **FLAGS)


def production(*, mould_positions=None, mould_cycle_elapsed_hours=None, availability=None,
               beam_deliveries_per_planned_day=None, accepted_beam_buffer=None,
               measured_release_evidence=None, route_length_m=10000.):
    """Balanced planned-working-day capacities; unexecuted gates block release."""
    a = load(); p = deepcopy(a['production']); span = a['civil']['span_m']
    for key, value in [('mould_positions', mould_positions), ('mould_cycle_elapsed_hours', mould_cycle_elapsed_hours),
                       ('availability', availability), ('beam_deliveries_per_planned_day', beam_deliveries_per_planned_day),
                       ('accepted_beam_buffer', accepted_beam_buffer)]:
        if value is not None:
            p[key] = value
    _count(p['mould_positions'], 'mould positions'); _count(p['accepted_beam_buffer'], 'buffer', zero=True)
    for key in ('mould_cycle_elapsed_hours', 'availability'):
        _positive(p[key], key)
    _positive(p['beam_deliveries_per_planned_day'], 'deliveries', zero=True)
    _positive(route_length_m, 'route length', zero=True)
    if p['availability'] > 1:
        raise ValueError('availability exceeds one')
    # Curing cycle is elapsed clock hours across nights; assembly uses scheduled
    # shifts. The six-day calendar and lost-window allowance are applied once.
    beams_factory = p['mould_positions']*24/p['mould_cycle_elapsed_hours']*p['factory_utilisation_yield']
    foundations = p['foundation_crews']/p['productive_crew_days_per_foundation']*p['availability']
    piers = p['pier_caps_per_available_day']*p['availability']
    erection = p['beam_placements_per_available_day']*p['availability']
    routes = dict(factory=beams_factory*span/2, foundations=foundations*span,
                  piers=piers*span, delivery=p['beam_deliveries_per_planned_day']*span/2,
                  erection=erection*span/2, final_rail_survey=p['rail_completion_route_m_per_available_day']*p['availability'])
    minimum = min(routes.values()); beams_consumed = 2*minimum/span
    # Claims of a reviewer/hash are not authenticated acceptance. This API
    # intentionally has no external evidence authority adapter.
    if measured_release_evidence is not None and not isinstance(measured_release_evidence, dict):
        raise ValueError('evidence observations must be a mapping')
    gates = [dict(id=k, state='unexecuted', accepted=False) for k in PRODUCTION_HOLDS]
    return dict(schema='osr-station-production-study/1', resources=p,
        capacity_route_m_per_planned_workday=routes,
        bottlenecks=[k for k, value in routes.items() if math.isclose(value, minimum, abs_tol=1e-9)],
        conditional_route_m_per_planned_workday=minimum,
        conditional_beams_per_planned_day=beams_consumed,
        accepted_output_demonstrated_m_per_day=None, production_release_allowed=False,
        beam_buffer_planned_workdays=p['accepted_beam_buffer']/beams_consumed if beams_consumed else None,
        beam_buffer_full_available_erection_windows=p['accepted_beam_buffer']/p['beam_placements_per_available_day'],
        route_length_m=route_length_m,
        steady_workdays=route_length_m/minimum if minimum else None,
        elapsed_calendar_days_with_declared_lags=(route_length_m/minimum+p['programme_initial_and_trailing_workdays'])*7/p['workdays_per_week'] if minimum else None,
        factory_cycle_basis='elapsed clock hours, including overnight curing; parallel moulds; six-day dispatch calendar, qualified turnaround unproved',
        availability_basis='lost/partial erection and site windows applied once; factory has separate utilization/yield',
        strength_and_handover_gates=gates,
        supplied_evidence_claims_authenticated=False,
        scope='Conditional bottleneck capacity model, not a discrete-event construction replay or evidence of achieved output', **FLAGS)


def study():
    families = [('repository-geometry-comparator', .8, 1.6, .15, .18, 25.),
                ('balanced-25m', .8, 1.8, .10, .15, 25.), ('narrow-25m', .65, 1.9, .10, .14, 25.),
                ('short-20m', .70, 1.6, .12, .15, 20.), ('long-30m', .65, 2.3, .10, .14, 30.)]
    b = body(); a = load(); v = a['vehicle']; m = a['magnetic']; weight = b['aw3_target_kg']*9.81
    return dict(schema='osr-station-structure-study/1', configuration=a,
        body_cases=[body(case=case) for case in ('stretch', 'central', 'conservative')],
        magnetic_screens=dict(equal_static_cartridge_force_n=weight/m['cartridges'],
            ferrite_volume_m3=v['ferrite_kg']/m['ferrite_density_kg_m3'],
            ferrite_kg_per_cartridge=v['ferrite_kg']/m['cartridges'],
            required_ideal_gap_field_t=math.sqrt(2*4*math.pi*1e-7*weight/m['pole_area_study_m2']),
            required_ideal_gap_field_with_force_multiplier_t=math.sqrt(2*4*math.pi*1e-7*weight*m['force_multiplier_study']/m['pole_area_study_m2']),
            force_multiplier_is_regulatory=False, actual_effective_pole_area_m2=None,
            tare_to_aw3_force_ratio=b['aw3_target_kg']/b['tare_target_kg'],
            full_payload_force_swing_n=(b['aw3_target_kg']-b['tare_target_kg'])*9.81,
            ring_reference=ring_benchmark(), linear_orientation_candidates=linear_candidates(),
            useful_rail_force_gain=None, field_map_validated=False),
        civil_families=[dict(id=name, **civil(width=w, depth=h, web=tw, flange=tf, span=length)) for name, w, h, tw, tf, length in families],
        civil_cost_comparison=civil_costs(), production=production(),
        prior_cases=[dict(id='v0.5.1-onboard-traction-225kwh', equipped_body_kg=6400., tare_kg=18750., aw3_kg=30750.),
                     dict(id='preceding-station-powered-target', equipped_body_kg=6400., tare_kg=15400., aw3_kg=27400.)],
        global_optimum_proven=False, complete_manufactured_system=False,
        scope='Quantity/geometry, analytical reference and target-rate/process study; no solved railway magnetic circuit, structural design or production acceptance', **FLAGS)


def source_paths():
    return [Path(__file__), INPUT,ROOT/'ferrite-maglev-study.toml',ROOT/'OpenSourceRail_Station_Powered_Maglev_Design_Specification.docx']


def _sources():
    return {p.relative_to(ROOT).as_posix(): sha256(p.read_bytes()).hexdigest() for p in source_paths()}


def _encoded(value):
    return (json.dumps(value, sort_keys=True, indent=2, allow_nan=False)+'\n').encode()


def _chart(result):
    data = result['civil_families']; width = 660; height = 270
    lines = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="Unqualified guidebeam concrete and iron mass comparison">',
             '<rect width="100%" height="100%" fill="#111d31"/>',
             '<text x="20" y="26" fill="white" font-size="17">Study beams: concrete + unchanged passive iron</text>',
             '<text x="20" y="49" fill="#c7d4e6" font-size="12">Includes equal end infills. Reinforcement and attachment mass remain open.</text>']
    maximum = max(row['beam']['concrete_plus_iron_kg'] for row in data)
    for i, row in enumerate(data):
        y = 68+34*i; mass = row['beam']['concrete_plus_iron_kg']; bar = 270*mass/maximum
        lines += [f'<text x="20" y="{y+16}" fill="white" font-size="12">{row["id"]}</text>',
                  f'<rect x="240" y="{y}" width="{bar:.2f}" height="23" fill="#5dcbd0"/>',
                  f'<text x="{250+bar:.2f}" y="{y+16}" fill="white" font-size="12">{mass/1000:.2f} t</text>']
    lines.append('<text x="20" y="257" fill="#f3cc82" font-size="12">Geometry and cost targets: no structural, magnetic or manufacturing release.</text></svg>')
    return '\n'.join(lines).encode()


def _readme():
    return ('# Station-powered body and civil candidates\n\n'
        'Source-bound quantity and target-rate study. The central equipped-body allocation is 5.2 t/car and total tare target is 14.2 t/car. '
        'Panel stock is calculated; members, joints, complete magnetic circuits and manufacturing qualification remain open.\n\n'
        '[Full calculated results](result.json) · [Beam mass comparison](comparison.svg) · [Source and payload checksums](manifest.json)\n\n'
        'The civil target prices an incomplete ordinary guideway scope. Station propulsion, complete evacuation, factory capital and other programme scope are additional. '
        'Production figures are conditional bottleneck capacities; strength and final survey hold points are unexecuted. '
        'Ring benchmarks and block orientation seeds do not demonstrate railway force or magnet-mass gains.\n\n'
        'Regenerate with the station-structure workflow stage. No design, physical validation, manufacturing or physical release is claimed.\n').encode()

def publish(output=OUTPUT):
    output = Path(output)
    if output.is_symlink() or (output.exists() and not output.is_dir()):
        raise ValueError('ordinary owned packet directory required')
    if output.exists() and any(p.name not in FILES | {'manifest.json'} or p.is_symlink() or not p.is_file() for p in output.iterdir()):
        raise ValueError('unexpected station structure packet content')
    sources = _sources(); result = study(); epoch = sha256(_encoded(sources)).hexdigest()
    result['source_epoch_sha256'] = epoch
    readme = _readme()
    payload = {'result.json': _encoded(result), 'comparison.svg': _chart(result), 'README.md': readme}
    if _sources() != sources:
        raise ValueError('station structure sources changed during computation')
    manifest = dict(schema='osr-station-structure-packet/1', sources_sha256=sources,
                    source_epoch_sha256=epoch, files_sha256={name: sha256(data).hexdigest() for name, data in payload.items()}, **FLAGS)
    output.mkdir(parents=True, exist_ok=True)
    for name, data in {**payload, 'manifest.json': _encoded(manifest)}.items():
        if len(data) > MAX_BYTES:
            raise ValueError('bounded structure payload required')
        temporary = output/(name+'.pending')
        if temporary.is_symlink():
            raise ValueError('symlink temporary payload refused')
        with temporary.open('wb') as handle:
            handle.write(data); handle.flush(); os.fsync(handle.fileno())
        temporary.replace(output/name)
    return verify(output)


def verify(output=OUTPUT):
    output = Path(output)
    if output.is_symlink() or not output.is_dir() or {p.name for p in output.iterdir()} != FILES | {'manifest.json'}:
        raise ValueError('exact station structure packet inventory required')
    payload = {}
    for name in FILES | {'manifest.json'}:
        path = output/name
        if path.is_symlink() or not path.is_file() or path.stat().st_size > MAX_BYTES:
            raise ValueError('bounded ordinary structure payload required')
        payload[name] = path.read_bytes()
    manifest = json.loads(payload['manifest.json']); sources = _sources()
    epoch = sha256(_encoded(sources)).hexdigest()
    if manifest.get('schema') != 'osr-station-structure-packet/1' or manifest.get('sources_sha256') != sources or manifest.get('source_epoch_sha256') != epoch:
        raise ValueError('stale station structure source receipt')
    if manifest.get('files_sha256') != {name: sha256(payload[name]).hexdigest() for name in FILES}:
        raise ValueError('station structure payload checksum differs')
    result = json.loads(payload['result.json'])
    expected = study(); expected['source_epoch_sha256'] = epoch
    if result != expected or payload['comparison.svg'] != _chart(expected) or payload['README.md'] != _readme():
        raise ValueError('station structure result differs from reproducible calculations')
    if any(manifest.get(key) is not False or result.get(key) is not False for key in FLAGS):
        raise ValueError('unqualified structure release flag')
    return dict(state='verified-study-records', source_epoch_sha256=epoch,
                body_cases=len(result['body_cases']), civil_families=len(result['civil_families']), **FLAGS)


def _rectangles(width, height, holes=()):
    """Nonoverlapping material rectangles of a developed panel with openings."""
    _positive(width, 'panel width'); _positive(height, 'panel height')
    for x0, y0, x1, y1 in holes:
        if not (0 <= x0 < x1 <= width and 0 <= y0 < y1 <= height):
            raise ValueError('opening outside developed panel')
    xs = sorted({0., width, *(x for hole in holes for x in (hole[0], hole[2]))})
    ys = sorted({0., height, *(y for hole in holes for y in (hole[1], hole[3]))})
    return [(x0, y0, x1-x0, y1-y0) for x0, x1 in zip(xs, xs[1:]) for y0, y1 in zip(ys, ys[1:])
            if not any(h[0] < (x0+x1)/2 < h[2] and h[1] < (y0+y1)/2 < h[3] for h in holes)]


def definition(c=None, *, case='central'):
    """Partial material geometry for native export; unsized budgets stay absent.

    Panel regions are developed-stock quantities placed near the body envelope.
    Corner mitres, bonded joints, inserts, equipment and complete hardpoints are
    absent. This is not a watertight or collision-qualified assembled carbody.
    """
    a = load(); b = body(c, case); _, inputs = _vehicle(c, a); s = inputs['cases'][case]
    cv = a['civil']; cr = civil(c); beam = cr['section']; span = cr['span_m']
    length, width, height = (b['envelope_m'][key] for key in ('length', 'width', 'height'))
    if inputs['doors_per_side'] != 2 or inputs['fixed_side_glazing_area_m2'] != 24. or inputs['combined_end_opening_area_m2'] != 6.5:
        raise ValueError('native panel opening layout requires the explicit four-door reference')
    if length < 16 or width < 2.5 or height < 2.6:
        raise ValueError('regenerate native opening geometry for unsupported smaller envelope')
    parts = []; groups = {}
    materials = {'gfrp': inputs['face_density_kg_m3'], 'core-80': 80., 'core-100': 100.,
                 'bond-surface': 1000., 'concrete': cv['concrete_density_kg_m3'], 'steel': 7850.}
    def add(identity, size, at, material, group, **kw):
        if any(type(x) not in (int, float) or not math.isfinite(x) for x in [*size, *at]) or min(size) <= 0:
            raise ValueError('positive finite native dimensions required')
        part = dict(id=identity, size_m=list(size), at_m=list(at), material=material, kind='box',
                    role='panel-stock' if group == 'gfrp-panel-stock' else material,
                    basis='Unqualified station-powered material-region study', **kw)
        parts.append(part); groups.setdefault(group, []).append(identity)
    upper = [(s['upper_face_each_m'], 'gfrp'), (s['upper_core_m'], f"core-{s['upper_core_density_kg_m3']:g}"),
             (s['upper_face_each_m'], 'gfrp'), (s['upper_bond_finish_kg_m2']/1000, 'bond-surface')]
    floor = [(s['floor_faces_total_m']/2, 'gfrp'), (s['floor_core_m'], f"core-{s['floor_core_density_kg_m3']:g}"),
             (s['floor_faces_total_m']/2, 'gfrp'), (s['floor_bond_finish_kg_m2']/1000, 'bond-surface')]
    for layers in (upper, floor):
        if any(material not in materials for _, material in layers):
            raise ValueError('native core density needs its own explicit material identity')
    def panel(name, local_width, local_height, holes, axis, fixed, origin, layers):
        offset = 0.
        for layer, (thickness, material) in enumerate(layers):
            for index, (x, y, dx, dy) in enumerate(_rectangles(local_width, local_height, holes)):
                if axis == 'z':
                    size = [dx, dy, thickness]; at = [origin[0]+x, origin[1]+y, fixed+offset]
                elif axis == 'y':
                    size = [dx, thickness, dy]; at = [origin[0]+x, fixed+offset, origin[1]+y]
                else:
                    size = [thickness, dx, dy]; at = [fixed+offset, origin[0]+x, origin[1]+y]
                add(f'body/{name}/layer-{layer}/region-{index}', size, at, material, 'gfrp-panel-stock')
            offset += thickness
    panel('floor', length, width, [], 'z', .3-sum(t for t, _ in floor), [-length/2, -width/2], floor)
    panel('roof', length, width, [], 'z', .3+height-sum(t for t, _ in upper), [-length/2, -width/2], upper)
    side_holes = []
    for centre in (-4.5, 4.5):
        x = centre+length/2; side_holes.append((x-.7, 0., x+.7, 2.1))
    for centre in (-6.5, -1.5, 1.5, 6.5):
        x = centre+length/2; side_holes.append((x-1., .9, x+1., 2.4))
    for side in (-1, 1):
        fixed = -width/2 if side < 0 else width/2-sum(t for t, _ in upper)
        panel(f'side-{side}', length, height, side_holes, 'y', fixed, [-length/2, .3], upper)
    end_holes = [(width/2-.65, 0., width/2+.65, 2.5)]
    for side in (-1, 1):
        fixed = -length/2 if side < 0 else length/2-sum(t for t, _ in upper)
        panel(f'end-{side}', width, height, end_holes, 'x', fixed, [-width/2, .3], upper)
    # Actual box-member shell and void infills; rail faces retain the comparison
    # quantity, not an optimised magnetic circuit or structural anchor design.
    w, d, tw, tf = (beam[k] for k in ('width_m', 'depth_m', 'web_m', 'flange_m'))
    for side in (-1, 1):
        y = side*cv['beam_centres_m']/2; prefix = f'civil/beam-{side}'
        add(prefix+'/top', [span, w, tf], [-span/2, y-w/2, -tf], 'concrete', 'beams-and-iron')
        add(prefix+'/bottom', [span, w, tf], [-span/2, y-w/2, -d], 'concrete', 'beams-and-iron')
        for edge in (-1, 1):
            add(prefix+f'/web-{edge}', [span, tw, d-2*tf], [-span/2, y-w/2 if edge < 0 else y+w/2-tw, -d+tf], 'concrete', 'beams-and-iron')
            for i in range(math.ceil(span/2.5)):
                x = -span/2+i*2.5; run = min(2.49, span-(x+span/2))
                add(prefix+f'/rail-{edge}-{i}', [run, .96, .02], [x, y-w/2-.96 if edge < 0 else y+w/2, -.3], 'steel', 'beams-and-iron', role_override='unqualified-reaction-iron')
        for end in (-1, 1):
            x = -span/2 if end < 0 else span/2-cv['end_infill_each_m']
            add(prefix+f'/end-infill-{end}', [cv['end_infill_each_m'], w-2*tw, d-2*tf], [x, y-w/2+tw, -d+tf], 'concrete', 'beams-and-iron')
    do = cv['column_outer_diameter_m']; di = cv['column_inner_diameter_m']; ph = cr['supports']['column_height_m']
    solid = cv['column_solid_end_total_m']; cap_depth = .9
    for end in (-1, 1):
        x = end*span/2; top_column = -d-cap_depth; foot_top = top_column-ph; prefix = f'civil/support-{end}'
        add(prefix+'/cap-main', [1., 5., cap_depth], [x-.5, -2.5, -d-cap_depth], 'concrete', 'illustrative-supports')
        for side in (-1, 1):
            add(prefix+f'/cap-widening-{side}', [.3125, 1.6, cap_depth], [x-.8125 if side < 0 else x+.5, -.8, -d-cap_depth], 'concrete', 'illustrative-supports')
        add(prefix+'/column-hollow', [do, do, ph-solid], [x-do/2, -do/2, foot_top+solid/2], 'concrete', 'illustrative-supports',
            kind_override='cylinder', holes=[dict(axis='z', x_m=do/2, y_m=do/2, diameter_m=di, length_m=ph-solid)])
        for side in (-1, 1):
            add(prefix+f'/column-end-{side}', [do, do, solid/2], [x-do/2, -do/2, foot_top if side < 0 else top_column-solid/2], 'concrete', 'illustrative-supports', kind_override='cylinder')
        foot = cv['footing_square_side_m']; ft = cv['footing_thickness_m']
        add(prefix+'/shallow-footing-study', [foot, foot, ft], [x-foot/2, -foot/2, foot_top-ft], 'concrete', 'unselected-foundation-envelope')
    for part in parts:
        if 'kind_override' in part:
            part['kind'] = part.pop('kind_override')
        if 'role_override' in part:
            part['role'] = part.pop('role_override')
    return dict(schema='osr-maglev-development-solids/1', id='OSR-STATION-POWERED-PANEL-CIVIL-STOCK', parts=parts,
        construction_stages=[dict(id=key, parts=values) for key, values in groups.items()],
        material_density_assumptions_kg_m3=materials, retain_native_tessellation=True,
        scope='One car of developed sandwich-panel stock beside a two-direction ordinary bay; two illustrative end supports, no complete train or accepted foundation. Corner mitres and joint fit-up are unresolved.',
        body_stock_mass_kg=sum(row['calculated_mass_kg'] for row in b['panels']),
        unmodelled_body_budget_kg=sum(row['mass_kg'] for row in b['unsized_body_allocations']),
        complete_body_mass_modelled=False, qualified_foundation_selection=None,
        holds=BODY_HOLDS+CIVIL_HOLDS+['panel-corner-mitres-bonded-joints-and-hardware-not-modelled'], **FLAGS)
