"""Scoped ClassC plate/deck production; no whole-railway or installed closure.

No precast-beam labour recipe is borrowed for steel. Plant/tooling is separate
from per-piece costs. Rails, piers/foundations and all other14-scope records must
be supplied by a same-candidate adapter; this record cannot silently replace them.
"""
from copy import deepcopy
from math import fsum,isfinite
from pathlib import Path
from engineering.station_rail.common import identity,digest
from . import topology_geometry as geometry

PRODUCER='engineering/design_search/topology_cost.py'
CASES=('low','base','high')


def default_spec():
    return dict(schema='osr-topology-scoped-cost-spec/1',provenance='Version1 explicit topology-only ClassC engineering hypotheses; no supplier quote or accepted process',
        module_length_m=5.,reserve_mass_kg=deepcopy(geometry.DEFAULT_RESERVES),steel_purchase_yield=[.96,.90,.82],
        cut_hours_per_m=[.03,.08,.20],pierce_hours_each=[.02,.05,.15],handling_hours_per_module=[.25,.75,2.],splice_weld_hours_per_m=[.5,1.5,4.],
        machine_hours_per_cut_m=[.02,.06,.15],QA_hours_per_m2=[.02,.06,.18],coating_hours_per_m2=[.02,.06,.20],coating_iqd_per_m2=[5000.,15000.,50000.],
        deck_process_hours_per_m3=[2.,5.,12.],install_hours_per_tonne=[1.,3.,8.],civil_crew_people=[4.,6.,10.],production_crew_people=[2.,4.,6.],
        transport_iqd_per_tonne_km=[1000.,3000.,10000.],transport_distance_km=50.,crane_iqd_per_piece=[500000.,2000000.,10000000.],
        dedicated_plant_capital_iqd=[100000000.,500000000.,2500000000.],tooling_iqd=[10000000.,50000000.,250000000.],
        maintenance_fraction_per_year=[.005,.01,.025],coating_renewal_years=[15.,10.,7.],coating_renewal_fraction=[.02,.05,.12],bearing_renewal_years=[30.,20.,15.])


def _validate_spec(spec):
    expected=default_spec()
    if set(spec)!=set(expected) or spec['schema']!=expected['schema'] or not isinstance(spec['provenance'],str) or not spec['provenance']:raise ValueError('Explicit complete topology-only rate spec required')
    for key,value in spec.items():
        if key in ('schema','provenance','reserve_mass_kg'):continue
        values=value if isinstance(value,list) else [value]
        if isinstance(value,list) and len(value)!=3:raise ValueError('Low/base/high rate triple required: '+key)
        if any(type(v) not in (int,float) or not isfinite(v) or v<=0 for v in values):raise ValueError('Positive finite topology rate required: '+key)
    # Construction domain: at most120 quarterly events per asset over30years;
    # these bounds limit execution, not certified asset lives.
    for key in ('coating_renewal_years','bearing_renewal_years'):
        if any(not .25<=x<=1000 for x in spec[key]):raise ValueError('Renewal interval construction domain is0.25..1000years: '+key)
    if any(x>1 for x in spec['steel_purchase_yield']) or any(x>=1 for x in spec['maintenance_fraction_per_year']):raise ValueError('Yield/maintenance fraction outside domain')
    return spec


def _finite_cost(value):
    """Reject arithmetic overflow throughout a record before identity sealing."""
    if isinstance(value,dict):
        for item in value.values():_finite_cost(item)
    elif isinstance(value,(list,tuple)):
        for item in value:_finite_cost(item)
    elif type(value) in (int,float):
        try:finite=isfinite(value)
        except OverflowError:finite=False
        if not finite:raise ValueError('Topology cost arithmetic produced a nonfinite value')


def estimate(candidate,quantities,spec,canonical_assumptions):
    from . import model_cost
    root=Path(__file__).resolve().parents[2];a=model_cost._validate_assumptions(canonical_assumptions,root);spec=_validate_spec(deepcopy(spec))
    if canonical_assumptions['design_life_years']!=30 or any(canonical_assumptions[k]!=v for k,v in [('production_shifts_per_day',2),('production_hours_per_shift',8),('civil_shifts_per_day',2),('civil_hours_per_shift',8)]):raise ValueError('Thirty-year two8h-shift production/civil reference required')
    if quantities.get('evaluation_id')!=identity({k:v for k,v in quantities.items() if k!='evaluation_id'}):raise ValueError('Sealed topology quantities required')
    actual=geometry.quantities(candidate,quantities['densities_kg_m3'],reserves_kg=spec['reserve_mass_kg'],module_length_m=spec['module_length_m'])
    if actual!=quantities:raise ValueError('Candidate, module or reserve quantities differ')
    q=quantities['quantities'];handling=quantities['handling'];bench=canonical_assumptions['benchmark_rates_iqd'];rows=[]
    for i,name in enumerate(CASES):
        loaded=bench['wage_skilled_iqd_per_h']*a['wage_burden_multipliers'][i]
        wage=loaded*(1+a['second_shift_wage_premium'][i]/2)
        # Actual full blanks remain purchased. No uncontracted offcut reuse credit.
        gross=max(q['steel_full_stock_envelope_kg'],q['steel_net_mass_kg']/spec['steel_purchase_yield'][i]);steel_rate=a['steel_iqd_per_kg'][i]
        recipe=(a['concrete_cement_t_per_m3'][i]*bench['cement_iqd_per_t']+a['concrete_aggregate_m3_per_m3'][i]*bench['aggregate_iqd_per_m3']+a['concrete_sand_m3_per_m3'][i]*bench['sand_iqd_per_m3']+a['concrete_admixture_iqd_per_m3'][i])
        reserve={key:values[i] for key,values in spec['reserve_mass_kg'].items()}
        reserve_cost={key:mass*(bench['rebar_iqd_per_kg']*a['material_rate_sensitivity'][i] if key=='deck_rebar' else steel_rate if key=='bracing' else a['finished_equipment_iqd_per_kg'][i]) for key,mass in reserve.items()}
        hours=dict(cutting=handling['two_web_module_cut_perimeter_m']*spec['cut_hours_per_m'][i]+handling['two_web_module_contour_starts_hypothesis']*spec['pierce_hours_each'][i],
            handling=max(handling['plate_handling_modules'],handling['actual_cut_pieces'])*spec['handling_hours_per_module'][i],splice_welding=handling['two_web_splice_ligament_m']*spec['splice_weld_hours_per_m'][i],
            quality=handling['steel_surface_before_joining_m2']*spec['QA_hours_per_m2'][i],coating=handling['steel_surface_before_joining_m2']*spec['coating_hours_per_m2'][i],deck=q['deck_concrete_m3']*spec['deck_process_hours_per_m3'][i])
        labour=fsum(hours.values());machine=handling['two_web_module_cut_perimeter_m']*spec['machine_hours_per_cut_m'][i]
        factory_items=dict(steel_blank_material=gross*steel_rate,concrete_ingredients=q['deck_concrete_m3']*(1+a['concrete_waste_fraction'][i])*recipe,
            **{'reserve_'+key:value for key,value in reserve_cost.items()},factory_labour=labour*wage,cutting_machine=machine*a['machine_rate_iqd_per_h'][i],coating_consumables=handling['steel_surface_before_joining_m2']*spec['coating_iqd_per_m2'][i])
        factory_direct=fsum(factory_items.values());overhead=factory_direct*a['factory_overhead_fraction'][i];factory=factory_direct+overhead
        mass=quantities['accounted_mass_kg_cases'][i];transport=mass/1000*spec['transport_distance_km']*spec['transport_iqd_per_tonne_km'][i];delivered=factory+transport
        civil_hours=mass/1000*spec['install_hours_per_tonne'][i];install=civil_hours*wage+spec['crane_iqd_per_piece'][i];installed=delivered+install
        rate=canonical_assumptions['real_discount_rate'];life=30
        maintenance=fsum(installed*spec['maintenance_fraction_per_year'][i]/(1+rate)**year for year in range(1,life+1))
        renewals=[]
        for asset,interval,basis in [('coating',spec['coating_renewal_years'][i],installed*spec['coating_renewal_fraction'][i]),('bearings',spec['bearing_renewal_years'][i],reserve_cost['bearings']+civil_hours*wage*.25)]:
            year=interval
            while year<life:
                renewals.append(dict(asset=asset,year=year,undiscounted_iqd=basis,present_value_iqd=basis/(1+rate)**year));year+=interval
        renewal=fsum(x['present_value_iqd'] for x in renewals);disposal=installed*a['decommissioning_fraction_of_installed_CAPEX'][i]/(1+rate)**life
        plant=spec['dedicated_plant_capital_iqd'][i];tooling=spec['tooling_iqd'][i]
        rows.append(dict(case=name,source_class='C',mass_accounted_kg=mass,steel_purchased_kg=gross,steel_scrap_or_offcut_kg=gross-q['steel_net_mass_kg'],actual_net_to_purchased_yield=q['steel_net_mass_kg']/gross,
            offcut_credit_iqd=0.,reserve_mass_kg=reserve,reserve_cost_iqd=reserve_cost,process_person_hours=hours,total_factory_person_hours=labour,cutting_machine_hours=machine,
            factory_line_items_iqd=factory_items,factory_overhead_iqd=overhead,factory_gate_iqd=factory,transport_iqd=transport,delivered_iqd=delivered,
            installation_person_hours=civil_hours,installation_labour_iqd=civil_hours*wage,installation_crane_iqd=spec['crane_iqd_per_piece'][i],scoped_installed_iqd=installed,
            dedicated_plant_capital_iqd=plant,tooling_capital_iqd=tooling,plant_and_tooling_in_per_piece_iqd=False,
            lifecycle=dict(horizon_years=life,real_discount_rate=rate,maintenance_npv_iqd=maintenance,renewals=renewals,renewal_npv_iqd=renewal,disposal_npv_iqd=disposal,total_scoped_npv_iqd=installed+maintenance+renewal+disposal,certified_asset_life=False),
            schedule=dict(production_shifts_per_day=2,civil_shifts_per_day=2,hours_per_shift=8,productive_utilisation=canonical_assumptions['productive_utilisation'],
                production_minimum_crew_days=labour/(16*canonical_assumptions['productive_utilisation']*spec['production_crew_people'][i]),civil_minimum_crew_days=civil_hours/(16*canonical_assumptions['productive_utilisation']*spec['civil_crew_people'][i]),precedence_and_tool_capacity_verified=False)))
    value=dict(schema='osr-topology-scoped-cost/1',candidate_id=candidate['candidate_id'],geometry_id=candidate['geometry_id'],quantity_evaluation_id=quantities['evaluation_id'],
        cost_basis=dict(machine_hour_rate='Canonical generic hourly rate used as an explicit ClassC operating/energy/consumables proxy, excluding operator labour and dedicated plant/tooling capital in this model',steel_stock='Full5m-module rectangular blank envelope or net/yield, whichever is larger; no offcut reuse credit',surface_process='All module steel surfaces before joining, including provisional splice faces; installed exposed area remains separate',mass_reserves='Positive bounded material/hardware accounts; locations, grades, interfaces and structural capacity unknown'),
        topology_spec_id=identity(spec),topology_spec=spec,canonical_assumption_id=canonical_assumptions['assumption_id'],currency='IQD',source_class='C',cases=rows,
        scope=dict(per_piece='Two cut steel webs and retained concrete deck; named provisional hardware/rebar/bracing/protection reserves',
            rails_included=False,foundations_and_piers_included=False,plant_and_tooling_separate=True,complete_installed_cost=False,complete_whole_system_lifecycle_cost=False,
            physical_topology_screen=candidate['web_geometry']['topology_screen'],unqualified_or_disconnected_geometry_may_still_be_costed=True),
        source_sha256={**candidate['source_sha256'],**model_cost.sources(root),PRODUCER:digest(__file__)},
        limitations=['ClassC coupled scenarios, not supplier quotations or probabilistic intervals','Module cutting/splicing, finite bracing/bearings and reserves have no accepted strength, fatigue, buckling or lifting proof','Cutting/nesting and time estimates do not prove minimum features, tooling or manufacturability','Maintenance and renewal intervals are planning assumptions, not certified service lives','No foundations, piers, rail procurement, utilities or complete railway operations cost; adapters must add those exactly once'],**geometry.FLAGS)
    _finite_cost(value)
    value['evaluation_id']=identity(value);return value
