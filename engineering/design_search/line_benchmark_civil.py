"""Quantity/process-cost civil adapter for a terminal-line planning benchmark.

Statistical rebar and wage inputs calibrate explicitly hypothetical rail and
fastener fabrication routes. They establish neither material grade nor railway
acceptance. This adapter changes no selected geometry or published receipt.
"""
from copy import deepcopy
from math import ceil, isfinite
from pathlib import Path
import json

from engineering.station_rail import ROOT, civil
from engineering.station_rail.common import digest, identity

PRODUCER = 'engineering/design_search/line_benchmark_civil.py'
RATE_DATA = 'engineering/sourcing/data/iraq-domestic-2026-july.json'
FLAGS = dict(engineering_accepted=False, physical_accepted=False,
    manufacturing_release=False, operating_release=False, selected_reference_changed=False)
CASES = ('low', 'base', 'high')
PARAMETERS = dict(
    rail_grade_proxy_factor=[1.25, 1.5, 2.], rail_purchase_yield=[.95, .9, .85],
    rail_process_h_per_kg=[.015, .04, .1], rail_machine_quality_iqd_per_kg=[200., 500., 1500.],
    fastener_grade_proxy_factor=[1.5, 2., 3.], fastener_purchase_yield=[.95, .9, .82],
    fastener_process_h_per_set=[.25, .75, 2.], fastener_pad_iqd_per_set=[2000., 6000., 20000.],
    fastener_machine_quality_iqd_per_set=[3000., 9000., 30000.],
    employer_burden=[1.25, 1.5, 2.], second_shift_premium=[0., .1, .2],
    factory_overhead=[.1, .2, .3], concrete_cement_t_per_m3=[.3, .36, .45],
    concrete_aggregate_m3_per_m3=[.55, .68, .85], concrete_sand_m3_per_m3=[.28, .4, .55],
    concrete_waste=[.02, .05, .1], admixture_iqd_per_m3=[5000., 20000., 80000.],
    prestress_iqd_per_kg=[2500., 4000., 7500.], anchorage_iqd_per_kg=[4000., 7000., 14000.],
    beam_factory_h_per_span=[24., 64., 180.], beam_machine_iqd_per_span=[250000., 1200000., 5000000.],
    beam_quality_iqd_per_span=[150000., 700000., 3000000.],
    bearing_complete_iqd_per_pad=[250000., 750000., 2500000.],
    end_joint_drains_lifting_hardware_iqd_per_span=[500000., 1500000., 5000000.],
    protected_walkway_iqd_per_track_m=[150000., 350000., 900000.],
    transport_iqd_per_tonne_km=[100., 400., 1500.], crane_iqd_per_shift=[2000000., 10000000., 50000000.],
    spans_per_crane_shift=[4., 2., 1.], erection_h_per_span=[20., 64., 180.],
    rail_install_crew=[4, 6, 12], rail_install_machine_iqd_per_8h_shift=[750000., 2000000., 8000000.],
    rail_geometry_quality_iqd_per_shift=[100000., 500000., 2000000.],
    rail_track_m_per_shift=[300., 150., 60.], butt_weld_complete_iqd_each=[75000., 200000., 700000.],
    support_field_h_each=[8., 24., 64.],
    substructure_formwork_excavation_other_plant_iqd_per_support=[2000000., 6000000., 20000000.])


def _number(value, name, *, zero=False):
    if type(value) not in (int, float) or not isfinite(value) or (value < 0 if zero else value <= 0):
        raise ValueError('Finite '+('nonnegative ' if zero else 'positive ')+name+' required')
    return float(value)


def _rates(root):
    data = json.loads((Path(root)/RATE_DATA).read_bytes())
    rows = {row['benchmark_key']: row for row in data['benchmarks']}
    keys = dict(cement='iq-cso-2026-07:iraq-origin:material:cement-ordinary',
        aggregate='iq-cso-2026-07:iraq-origin:material:gravel-crushed',
        sand='iq-cso-2026-07:iraq-origin:material:sand-red',
        rebar='iq-cso-2026-07:iraq-origin:material:rebar',
        wage='iq-cso-2026-07:al-muthanna:wage:skilled:hour-8h-day')
    units = dict(cement='t', aggregate='m3', sand='m3', rebar='t', wage='h')
    result = {}
    for name, key in keys.items():
        row = rows[key]
        if row['currency'] != 'IQD' or row['quantity_unit'] != units[name] or row['supplier_quote'] is not False:
            raise ValueError('Statistical rate unit/currency/provenance differs: '+name)
        result[name] = _number(float(row['unit_price']), name)/(1000 if name == 'rebar' else 1)
    return result, keys


def evaluate(requirements, design, vehicle, root=ROOT):
    """Return planning quantities and cost lines without native solver execution.

    ``vehicle`` is the unmodified reference vehicle; ``added_vehicle_mass_kg_per_car``
    is applied once here as an evaluation hypothesis. Independent foundations
    are mandatory. Soil cases are sensitivities; base pricing uses 200 kPa.
    """
    root = Path(root); r = deepcopy(requirements); d = deepcopy(design)
    if digest(root/PRODUCER) != digest(__file__) or digest(root/civil.PRODUCER) != digest(civil.__file__):
        raise ValueError('Executing civil producer differs from declared source root')
    route_m = 1000*_number(r['route_km'], 'route kilometres')
    if type(r.get('trackways')) is not int or r['trackways'] != 2:
        raise ValueError('Explicit two-track benchmark required')
    if type(r.get('stations')) is not int or r['stations'] < 2:
        raise ValueError('At least two integer stations required')
    span = _number(d.get('span_m', 20.), 'span')
    if span != 20. or d.get('beam_family', 'box-beam') != 'box-beam':
        raise ValueError('This cost route requires the selected 20 m box-beam family')
    if d.get('shared_crossheads', False) is not False:
        raise ValueError('Shared crossheads need their own geometry/load/cost adapter')
    pier_height = _number(d.get('pier_height_m', 8.), 'pier height')
    platform_length = _number(d.get('platform_length_m', 120.), 'platform length')
    platform_width = _number(d.get('platform_width_m', 4.), 'platform width')
    soils = d.get('soil_cases_kpa', [300., 200., 100.])
    if not isinstance(soils, (tuple, list)) or len(soils) != 3 or sorted(soils) != [100., 200., 300.]:
        raise ValueError('Explicit 300/200/100 kPa soil sensitivities required')
    added = _number(d.get('added_vehicle_mass_kg_per_car', 0.), 'added per-car mass', zero=True)
    reserve = _number(d.get('load_detail_reserve_fraction', 0.), 'load-detail reserve', zero=True)
    if reserve > 1.: raise ValueError('Load-detail reserve must not exceed one')
    include_walkway_gravity = d.get('include_walkway_gravity', False)
    if type(include_walkway_gravity) is not bool:
        raise ValueError('Walkway gravity inclusion must be explicit boolean')
    footprint_credit = d.get('platform_continuity_cost_assumption', True)
    if type(footprint_credit) is not bool: raise ValueError('Platform continuity cost assumption must be boolean')
    count = ceil(route_m/span)*2; supports = (ceil(route_m/span)+1)*2
    walkway_m = route_m*2-(r['stations']*2*platform_length if footprint_credit else 0.)
    if walkway_m < 0.: raise ValueError('Platform lengths exceed the priced route')
    v = deepcopy(vehicle)
    for field in ('accounted_tare_kg_per_car', 'accounted_cap_loaded_kg_per_car', 'accounted_160_control_kg_per_car'):
        v['mass'][field] += added
    beam = civil.alternative(v, span, 'box-beam', 'crowd_control')
    names = [PRODUCER, civil.PRODUCER, RATE_DATA, 'engineering/station_rail/common.py']
    source = {**vehicle.get('source_sha256', {}), **{p:digest(root/p) for p in names}}
    rates, benchmark_keys = _rates(root); p = deepcopy(PARAMETERS)
    pier_area = _number(d.get('pier_area_m2', .8), 'pier area')
    footing_t = _number(d.get('footing_thickness_m', 1.2), 'footing thickness')
    haul = _number(d.get('haul_km', 50.), 'haul distance')
    walkway_mass = _number(d.get('walkway_mass_kg_per_track_m', 47.), 'walkway mass')
    concrete_rho = 2500.; gravity = civil.G; pier_volume = pier_area*pier_height
    reaction = next(x['dead_plus_train_support_reaction_N'] for x in beam['foundation_scenarios'] if x['allowable_bearing_kPa_hypothesis'] == 200.)
    additional_walkway_reaction = walkway_mass*span*gravity if include_walkway_gravity else 0.
    soil_bounds = []
    for pressure in soils:
        denominator = pressure*1000-concrete_rho*gravity*footing_t
        if denominator <= 0: raise ValueError('No positive gravity-closed shallow footing area at this pressure/thickness')
        area = (reaction+additional_walkway_reaction+pier_volume*concrete_rho*gravity)/denominator
        soil_bounds.append(dict(soil_kPa=pressure, gravity_closed_area_m2=area,
            footing_concrete_m3=area*footing_t, pier_concrete_m3=pier_volume,
            bare_beam_train_area_m2=reaction/(pressure*1000), minimum_only=True, qualified=False))
    foundation = next(x for x in soil_bounds if x['soil_kPa'] == 200.)
    quantities = dict(route_m=route_m, track_m=route_m*2, rail_m=route_m*4,
        span_count=count, independent_supports=supports, supports=supports,
        concrete_m3=beam['concrete_m3']*count, rebar_kg=beam['reinforcement_kg']*count,
        tendon_kg=beam['prestress_kg']*count, anchorage_kg=beam['prestress_anchorage_kg']*count,
        rail_kg=beam['running_rail_kg']*count, fastener_sets=beam['direct_fastener_sets']*count,
        fastener_hardware_kg=beam['direct_fastener_kg']*count, bearing_pad_units=count*4,
        platform_area_m2=r['stations']*2*platform_length*platform_width,
        protected_walkway_m=walkway_m, walkway_mass_kg=walkway_mass*walkway_m,
        foundation_pier_concrete_m3=(foundation['footing_concrete_m3']+pier_volume)*supports,
        field_butt_welds=4*(ceil(route_m/20)-1), rail_supply_piece_m_hypothesis=20.,
        added_mass_kg_per_car=added, field_haul_km=haul,
        source_max_bare_piece_kg=beam['construction']['reference_max_piece_kg'],
        minimum_hook_kg=beam['construction']['minimum_crane_hook_capacity_kg_hypothesis'])
    quantities['foundation_pier_rebar_kg'] = quantities['foundation_pier_concrete_m3']*160.
    lines = []; unit_rates = {}; case_values = {}
    for i, case in enumerate(CASES):
        wage = rates['wage']*p['employer_burden'][i]*(1+p['second_shift_premium'][i]/2)
        oh = 1+p['factory_overhead'][i]
        rail_unit = (rates['rebar']*p['rail_grade_proxy_factor'][i]/p['rail_purchase_yield'][i]+p['rail_process_h_per_kg'][i]*wage+p['rail_machine_quality_iqd_per_kg'][i])*oh
        fastener_unit = (8*rates['rebar']*p['fastener_grade_proxy_factor'][i]/p['fastener_purchase_yield'][i]+p['fastener_process_h_per_set'][i]*wage+p['fastener_pad_iqd_per_set'][i]+p['fastener_machine_quality_iqd_per_set'][i])*oh
        concrete_unit = (rates['cement']*p['concrete_cement_t_per_m3'][i]+rates['aggregate']*p['concrete_aggregate_m3_per_m3'][i]+rates['sand']*p['concrete_sand_m3_per_m3'][i])*(1+p['concrete_waste'][i])+p['admixture_iqd_per_m3'][i]
        beam_inputs = (beam['concrete_m3']*concrete_unit+beam['reinforcement_kg']*rates['rebar']+
            beam['prestress_kg']*p['prestress_iqd_per_kg'][i]+beam['prestress_anchorage_kg']*p['anchorage_iqd_per_kg'][i]+
            p['beam_factory_h_per_span'][i]*wage+p['beam_machine_iqd_per_span'][i]+p['beam_quality_iqd_per_span'][i])
        factory = beam_inputs*oh+beam['running_rail_kg']*rail_unit+beam['direct_fastener_sets']*fastener_unit
        install_unit = (p['rail_install_crew'][i]*8*wage+p['rail_install_machine_iqd_per_8h_shift'][i]+p['rail_geometry_quality_iqd_per_shift'][i])/p['rail_track_m_per_shift'][i]
        unit_rates[case] = dict(loaded_two_shift_wage_iqd_h=wage, rail_factory_iqd_kg=rail_unit,
            complete_8kg_fastener_factory_iqd_set=fastener_unit, concrete_ingredient_iqd_m3=concrete_unit,
            beam_factory_iqd_span=factory, rail_field_install_iqd_track_m=install_unit)
        case_values[case] = dict(
            beam_factory=factory*count, bearing_pads=quantities['bearing_pad_units']*p['bearing_complete_iqd_per_pad'][i],
            end_joint_drains_lifting_hardware=count*p['end_joint_drains_lifting_hardware_iqd_per_span'][i],
            substructure_concrete=quantities['foundation_pier_concrete_m3']*concrete_unit,
            substructure_rebar=quantities['foundation_pier_rebar_kg']*rates['rebar'],
            substructure_field_labour=supports*p['support_field_h_each'][i]*wage,
            substructure_formwork_excavation_other_plant=supports*p['substructure_formwork_excavation_other_plant_iqd_per_support'][i],
            all_span_stock_haul=beam['total_counted_span_mass_kg']/1000*count*haul*p['transport_iqd_per_tonne_km'][i],
            crane_shifts=ceil(count/p['spans_per_crane_shift'][i])*p['crane_iqd_per_shift'][i],
            erection_labour=count*p['erection_h_per_span'][i]*wage,
            field_two_rail_track_install=quantities['track_m']*install_unit,
            field_butt_welding=quantities['field_butt_welds']*p['butt_weld_complete_iqd_each'][i],
            protected_nonstation_walkway=walkway_m*p['protected_walkway_iqd_per_track_m'][i],
            civil_load_detail_reserve=factory*count*reserve)
    basis = dict(beam_factory='Actual beam concrete/rebar/tendons/anchorages, plus explicit fabrication labour, machine/QA and one overhead; rail and complete 8 kg fastener assemblies have own overhead, not a second beam uplift.',
        bearing_pads='Four complete Class C bearing pad/plate/anchor/QA packages per span; no bearing design acceptance.',
        end_joint_drains_lifting_hardware='Separate nonzero Class C package for unresolved end joints, drainage and lifting interfaces.',
        substructure_concrete='Gravity-closed 200 kPa footing/pier volume times ingredient recipe; does not establish footing structural or geotechnical acceptance.',
        substructure_rebar='160 kg/m3 preliminary pad/pier detailing times dated CSO rebar; laps and bar schedule remain unresolved.',
        substructure_field_labour='Declared support crew-hours times loaded two-shift hourly wage.',
        substructure_formwork_excavation_other_plant='Nonzero formwork, excavation and construction-plant allowance per independent support.',
        all_span_stock_haul='All counted span stock tonne-km at declared haul; field rails shipped separately from bare concrete lifting piece.',
        crane_shifts='Spans per active crane shift; hook rating at actual radius, ground support and temporary stability remain unverified.',
        erection_labour='Declared crew-hours per span at loaded two-shift wage.',
        field_two_rail_track_install='One installation charge per two-rail TRACK metre; avoids charging the same track operation per rail metre.',
        field_butt_welding='Explicit 20 m supply-length rail butt joints, with separate weld/test process allowance.',
        protected_nonstation_walkway='Protected access/evacuation route budget, with platform overlap removed only as explicit cost continuity hypothesis; physical continuity unverified.',
        civil_load_detail_reserve='Declared extra cost reserve for unresolved additions; not extra measured stock or a structural pass.')
    for key in case_values['base']:
        lines.append(dict(key=key, scope='guideway' if key in ('beam_factory', 'bearing_pads', 'end_joint_drains_lifting_hardware', 'civil_load_detail_reserve') else 'construction',
            quantity=dict(basis_quantity_record_id=identity(quantities), spans=count, supports=supports),
            costs_iqd={case:case_values[case][key] for case in CASES}, basis=basis[key], source_class='C'))
    compact = {k:beam[k] for k in ('alternative_id','physical_civil_component_id','family','span_m','load_case','concrete_m3','reinforcement_kg','running_rail_kg','direct_fastener_sets','direct_fastener_kg','prestress_kg','prestress_strands','prestress_anchorage_kg','total_counted_span_mass_kg','deflection_upper_bound_m','maximum_live_moment_Nm')}
    result = dict(schema='osr-line-benchmark-civil/1', reference_vehicle_candidate_id=vehicle.get('candidate_id'),
        requirements=r, design=d, reference_vehicle_input_id=identity(vehicle), evaluation_vehicle_mass_hypothesis=v['mass'],
        capital_lines=lines, quantities=quantities, unit_rates=unit_rates, beam=compact,
        source_sha256=source, statistical_rates_iqd=rates, statistical_benchmark_keys=benchmark_keys,
        process_assumptions=p, soil_gravity_necessary_bounds=soil_bounds,
        production_shifts_per_day=2, civil_shifts_per_day=2, native_solver_jobs=0,
        structural_evidence=dict(beam_model_includes_added_vehicle_mass=True, walkway_gravity_in_foundations=include_walkway_gravity,
            walkway_uniform_beam_response_and_eccentric_torsion_qualified=False,
            extra_walkway_dead_load_kg_per_track_m=walkway_mass, platform_continuity_qualified=False,
            bearing_and_temporary_stability_qualified=False, soil_and_shallow_footing_qualified=False,
            complete_installed_civil_mass=False),
        limitations=['Class C rail fabrication price uses rebar only as a cost scale, not a qualified rail material or process.',
            'Four pads per beam, joints, walkway, excavation/formwork and machine prices are bounded package assumptions.',
            'Two independent support lines are priced; shared-crosshead savings need a separately designed and costed adapter.',
            'Crane capacity at radius, prestress transfer, fatigue, torsion, bearings, foundations and vehicle/stator clearance remain unqualified.',
            'Factory buildings/tooling, stations, depot, land, utilities, launch equipment, fees, contingency and rolling stock are priced by the parent benchmark, not this adapter.'], **FLAGS)
    if any(digest(root/name)!=sha for name,sha in source.items()): raise ValueError('Civil cost source epoch changed during evaluation')
    result['evaluation_id'] = identity(result)
    return result
