"""Same-quantity civil supply alternatives for an outline railway budget.

Commercial scenarios do not substitute the advertised GB43 profile for the
selected 60E1 rail, change installed geometry, or provide physical acceptance.
"""
from copy import deepcopy
from math import ceil, fsum, isclose, isfinite
from pathlib import Path
import json

from engineering.station_rail import ROOT
from engineering.station_rail.common import digest, identity
from engineering.outline import make_buy

PRODUCER = 'engineering/outline/civil_supply.py'
DATA = 'engineering/outline/data/china-supply-20261104.json'
CASES = ('low', 'base', 'high')
FLAGS = dict(engineering_accepted=False, physical_accepted=False,
    manufacturing_release=False, operating_release=False,
    procurement_approved=False, selected_reference_changed=False)
_LOADED = {PRODUCER: digest(__file__), make_buy.PRODUCER: digest(make_buy.__file__),
    'engineering/station_rail/common.py': digest(Path(ROOT)/'engineering/station_rail/common.py')}


def _number(value, name, positive=True):
    if type(value) not in (int, float) or not isfinite(value) or (value <= 0 if positive else value < 0):
        raise ValueError('Finite '+('positive ' if positive else 'nonnegative ')+name+' required')
    return float(value)


def _triple(values):
    return dict(zip(CASES, values))


def _operations(**overrides):
    result = dict(cell_hours_per_unit=1., labour_hours_per_unit=0., machine_hours_per_unit=0.,
        setup_cell_hours_per_batch=0., setup_labour_hours_per_batch=0., setup_machine_hours_per_batch=0.,
        batch_quantity=1., labour_rate_per_hour=0., machine_rate_per_hour=0.,
        energy_kwh_per_unit=0., setup_energy_kwh_per_batch=0., energy_rate_per_kwh=0.,
        consumables_per_unit=0., qa_per_unit=0., labour_rate_basis='paid-hour',
        paid_hours_per_productive_hour=1/.75,
        machine_rate_basis='cash-operating-excluding-capital-recovery')
    result.update(overrides)
    return result


def _purchase(unit, price, source, freight, qa, delivery=0.):
    return dict(unit=unit, currency='USD', tiers=[dict(minimum_quantity=1., unit_price=price,
        already_bulk=True, source_class='C', source=source)], landed=dict(
        freight_per_unit=freight, insurance_fraction=_triple([.002,.005,.01]),
        duty_fraction=_triple([.02,.05,.1]), qa_per_unit=qa, local_delivery_per_unit=delivery))


def _compare(item, quantity, unit, years, purchase, manufacture, root):
    return make_buy.evaluate(dict(item_id=item, quantity=quantity, committed_volume=quantity,
        unit=unit, currency='USD', project_years=years, purchase=purchase, make=manufacture), root=root)


def revalue(civil, spec, scenario, root=ROOT):
    """Reprice one immutable civil quantity record, retaining all fourteen scopes.

    Returned capital excludes precast buildings/yards: the caller prices the
    returned floor/yard areas once. Fastener workshop building cost, if selected,
    is already in its returned owned capital and is not part of those areas.
    Make/buy comparisons nevertheless include both building and yard cash costs.
    """
    if scenario not in ('china-bulk-buy', 'project-make-buy'):
        raise ValueError('Unknown civil supply scenario')
    root = Path(root)
    if any(digest(root/name) != sha for name,sha in _LOADED.items()):
        raise ValueError('Loaded civil supply source changed; restart evaluator')
    before = {**_LOADED, DATA:digest(root/DATA)}
    old = deepcopy(civil); result = deepcopy(civil); s = deepcopy(spec)
    if old.get('evaluation_id') != identity({k:v for k,v in old.items() if k!='evaluation_id'}):
        raise ValueError('Civil input evaluation identity differs')
    q,b,p = old['quantities'], old['beam'], old['process_assumptions']
    if b.get('family') != 'box-beam' or b.get('span_m') != 20.:
        raise ValueError('Explicit selected 20 m box-beam required')
    for key in ('span_count','rail_kg','fastener_sets','rebar_kg','foundation_pier_rebar_kg'):
        _number(q[key],key)
    count=q['span_count']; sets=q['fastener_sets']; rail_t=q['rail_kg']/1000
    if not isclose(q['rail_kg'],count*b['running_rail_kg']) or not isclose(sets,count*b['direct_fastener_sets']):
        raise ValueError('Civil aggregate and per-span quantities disagree')
    if (q['route_m'] != 1000*s['requirements']['route_km']
            or count != 2*ceil(q['route_m']/20.)
            or q['track_m'] != 2*q['route_m'] or q['rail_m'] != 4*q['route_m']
            or q['independent_supports'] != 2*(ceil(q['route_m']/20.)+1)):
        raise ValueError('Civil route, tracks, spans and independent supports disagree')
    fx=_number(s['currency']['iqd_per_usd'],'IQD/USD'); d=s['design']; c=s['capital']
    years=_number(d['production_years'],'production years')
    if d['production_shifts'] != 2 or d['hours_per_production_shift'] != 8 or d['production_days_per_year'] != 250 or d['productive_utilisation'] != .75:
        raise ValueError('Explicit two 8-hour shifts, 250 days and 75% utilisation required')
    capacity=dict(shifts_per_day=2,hours_per_shift=8.,days_per_year=250.,utilisation=.75)
    cap_h=years*3000.; workdays=years*250.
    data=json.loads((root/DATA).read_bytes()); observations={v['id']:v for v in data['observations']}
    cny=_number(data['fx_reference']['quote_per_base'],'CNY/USD')
    rebar_obs=observations['cn-nbs-20261021-31-hrb400e-rebar']
    plate_obs=observations['cn-nbs-20261021-31-q235-plate']
    for obs in (rebar_obs,plate_obs):
        if obs['advertised_price']['currency']!='CNY' or obs['advertised_price']['unit']!='metric_tonne':
            raise ValueError('Raw steel observation unit/currency differs')
    wage=_triple([old['unit_rates'][case]['loaded_two_shift_wage_iqd_h']/fx for case in CASES])
    # Domestic circulation benchmarks need explicit export preparation as well as landing.
    def raw_landed(obs):
        nominal=obs['advertised_price']['low']/cny/1000
        return [(nominal+[.03,.06,.12][i]+[.1,.18,.3][i])*(1+[.002,.005,.01][i])*(1+[.02,.05,.1][i])+[.01,.02,.05][i] for i in range(3)]
    cn_rebar=raw_landed(rebar_obs); plate=raw_landed(plate_obs)
    local_rebar=old['statistical_rates_iqd']['rebar']/fx
    # Source is a design-stage purchasing decision, not an independently
    # cherry-picked minimum in each sensitivity case. Retain its whole vector.
    rebar_source='China HRB400E compatible-grade pricing hypothesis' if cn_rebar[1]<local_rebar else 'Iraq CSO rebar benchmark'
    rebar=list(cn_rebar) if cn_rebar[1]<local_rebar else [local_rebar]*3
    # The advertised GB43 rail is a scope hold, never a quantity/profile substitution.
    rail=_compare('selected-60E1-finished-rail-buy',rail_t,'metric_tonne',years,
        _purchase('metric_tonne',_triple([600.,800.,1100.]),
            'Class C 60E1 equivalent finished-rail hypothesis; advertised GB43 is not equivalent',
            _triple([80.,150.,250.]),_triple([5.,15.,40.]),_triple([20.,30.,50.])),None,root)
    rail_unit={case:rail['cases'][case]['purchase']['per_unit']/1000 for case in CASES}
    fast_buy=_purchase('complete-8kg-assembly',_triple([16.,23.,40.]),
        'Class C complete baseplate/clip/bolt/insulator/pad assembly, not a clip-only listing',
        _triple([.8,1.44,2.4]),_triple([.25,.75,2.]),_triple([.15,.3,.75]))
    fast_op=_operations(cell_hours_per_unit=_triple([.07,.125,.25]),
        labour_hours_per_unit=_triple([.2,.35,.7]),machine_hours_per_unit=_triple([.04,.08,.2]),
        setup_cell_hours_per_batch=_triple([1.,2.,4.]),setup_labour_hours_per_batch=_triple([2.,4.,8.]),
        setup_machine_hours_per_batch=_triple([.5,1.,2.]),batch_quantity=500.,
        labour_rate_per_hour=wage,machine_rate_per_hour=_triple([3.,8.,20.]),
        energy_kwh_per_unit=_triple([.3,.6,1.5]),energy_rate_per_kwh=_triple([.1,.15,.3]),
        consumables_per_unit=_triple([6.4,11.,21.]),qa_per_unit=_triple([.5,1.,3.]))
    fast_cells=[ceil((sets*[.07,.125,.25][i]+ceil(sets/500)*[1.,2.,4.][i])/cap_h) for i in range(3)]
    fast_floor=[n*80. for n in fast_cells]
    fast_make=dict(unit='complete-8kg-assembly',material=dict(unit='local-baseplate-kg',net_quantity_per_unit=6.,
        unit_price=_triple(plate),yield_fraction=_triple([.95,.92,.85]),scrap_credit_per_unit=None),
        operations=fast_op,capacity=capacity,learning=None,
        fixed=dict(equipment_per_cell=_triple([40000.,80000.,200000.]),tooling_per_cell=_triple([15000.,30000.,80000.]),
            building_shared=_triple([fast_floor[i]*c['factory_building_iqd_per_m2'][i]/fx for i in range(3)]),
            commissioning_shared=_triple([30000.,80000.,250000.])))
    fast=_compare('complete-8kg-fastener-local-plate-purchased-specialist-parts',sets,'complete-8kg-assembly',years,fast_buy,fast_make,root)
    fast_choice='buy' if scenario=='china-bulk-buy' else fast['base_choice']
    if fast_choice not in ('make','buy','tie'): raise ValueError('Incomplete fastener comparison')
    if fast_choice=='tie': fast_choice='buy'
    fast_branch='make' if fast_choice=='make' else 'purchase'
    # One reusable mould includes both faces, removable core and structural ribs.
    face_area=2*(2.+1.4)*20.+2*(1.64+1.04)*20.
    moulds=[ceil(count*cycle/(workdays*.75)) for cycle in (2.,5.,10.)]
    mould_mass=[face_area*t*7850+rib for t,rib in zip((.005,.006,.008),(6000.,8500.,12000.))]
    mould_price=[]
    for i,case in enumerate(CASES):
        mould_price.append(mould_mass[i]/[.95,.9,.85][i]*plate[i]
            +[500.,1000.,2000.][i]*wage[case]/.75+[4000.,8000.,20000.][i]
            +[1500.,4000.,12000.][i]+[1000.,3000.,8000.][i])
    beam_h=p['beam_factory_h_per_span']; crew=c['precast_crew_per_cell']
    cells=[ceil((count*beam_h[i]/crew+count*.5)/cap_h) for i in range(3)]
    floor=[n*24.*5. for n in moulds]
    storage=ceil(count/workdays*c['precast_yard_hold_workdays'])*22.*c['precast_storage_width_m']/c['precast_storage_utilisation']
    yard=[a+storage for a in floor]
    building=[floor[i]*c['factory_building_iqd_per_m2'][i]/fx+yard[i]*c['precast_yard_iqd_per_m2'][i]/fx for i in range(3)]
    materials=[]; concrete=[]
    for i,case in enumerate(CASES):
        concrete.append(b['concrete_m3']*old['unit_rates'][case]['concrete_ingredient_iqd_m3']/fx)
        materials.append(concrete[i]+b['reinforcement_kg']*rebar[i]/[.98,.95,.9][i]
            +b['prestress_kg']*p['prestress_iqd_per_kg'][i]/fx/[.99,.98,.95][i]
            +b['prestress_anchorage_kg']*p['anchorage_iqd_per_kg'][i]/fx)
    # Material is a declared full structural kit: rail/fasteners are deliberately excluded.
    beam_op=_operations(cell_hours_per_unit=_triple([h/crew for h in beam_h]),
        labour_hours_per_unit=_triple(beam_h),machine_hours_per_unit=_triple([2.,4.,10.]),
        setup_cell_hours_per_batch=.5,setup_labour_hours_per_batch=_triple([2.,4.,8.]),
        setup_machine_hours_per_batch=_triple([.5,1.,2.]),batch_quantity=1.,
        labour_rate_per_hour=wage,machine_rate_per_hour=_triple([10.,25.,60.]),
        energy_kwh_per_unit=_triple([100.,300.,1000.]),energy_rate_per_kwh=_triple([.1,.15,.3]),
        consumables_per_unit=_triple([80.,250.,800.]),
        qa_per_unit=_triple([p['beam_quality_iqd_per_span'][i]/fx for i in range(3)]))
    equipment=[500000.+cells[0]*50000.,1200000.+cells[1]*100000.,3000000.+cells[2]*250000.]
    tooling=[moulds[i]*mould_price[i]+[150000.,400000.,1000000.][i] for i in range(3)]
    beam_make=dict(unit='20m-structural-box-beam',material=dict(unit='concrete-rebar-tendon-anchorage-kit',
        net_quantity_per_unit=1.,unit_price=_triple(materials),yield_fraction=1.,scrap_credit_per_unit=None),
        operations=beam_op,capacity=capacity,learning=None,
        fixed=dict(equipment_per_cell=_triple([equipment[i]/cells[i] for i in range(3)]),
            tooling_per_cell=_triple([tooling[i]/cells[i] for i in range(3)]),building_shared=_triple(building),
            commissioning_shared=_triple([100000.,250000.,750000.])))
    # First evaluate own variable costs independently of the contractor proxy.
    beam0=_compare('precast-variable-cost-control',count,'20m-structural-box-beam',years,None,beam_make,root)
    variable=[beam0['cases'][case]['make']['variable_total']/count for case in CASES]
    contractor=[variable[i]*(1+[.12,.25,.5][i])+[250.,750.,2500.][i] for i in range(3)]
    beam_buy=dict(unit='20m-structural-box-beam',currency='USD',tiers=[dict(minimum_quantity=1.,unit_price=_triple(contractor),
        already_bulk=True,source_class='C',source='Local contractor full factory-gate structural beam; variable route plus explicit overhead/profit and nonzero existing plant-capital allocation')],
        landed=dict(freight_per_unit=0.,insurance_fraction=0.,duty_fraction=0.,qa_per_unit=0.,local_delivery_per_unit=0.))
    beam=_compare('local-contracted-versus-owned-precast',count,'20m-structural-box-beam',years,beam_buy,beam_make,root)
    beam_choice='buy' if scenario=='china-bulk-buy' else beam['base_choice']
    if beam_choice not in ('make','buy','tie'): raise ValueError('Incomplete precast comparison')
    if beam_choice=='tie': beam_choice='buy'
    owned=[];chosen_beam=[];chosen_fast=[]
    for i,case in enumerate(CASES):
        br=beam['cases'][case];fr=fast['cases'][case]
        # Fixed factory costs are exported once, not amortised into beam/set unit rates again.
        chosen_beam.append(br['make']['variable_total']/count if beam_choice=='make' else br['purchase']['per_unit'])
        chosen_fast.append(fr['make']['variable_total']/sets if fast_choice=='make' else fr['purchase']['per_unit'])
        owned.append((br['make']['fixed_total']-br['make']['fixed_components']['building'] if beam_choice=='make' else 0.)
            +(fr['make']['fixed_total'] if fast_choice=='make' else 0.))
    rows={v['key']:v for v in result['capital_lines']}
    expected={'beam_factory','bearing_pads','end_joint_drains_lifting_hardware','substructure_concrete','substructure_rebar',
        'substructure_field_labour','substructure_formwork_excavation_other_plant','all_span_stock_haul','crane_shifts',
        'erection_labour','field_two_rail_track_install','field_butt_welding','protected_nonstation_walkway','civil_load_detail_reserve'}
    if set(rows)!=expected or len(result['capital_lines'])!=14:
        raise ValueError('All fourteen original civil scopes required exactly once')
    deltas={}
    for i,case in enumerate(CASES):
        prior=old['unit_rates'][case]
        stripped=prior['beam_factory_iqd_span']-b['running_rail_kg']*prior['rail_factory_iqd_kg']-b['direct_fastener_sets']*prior['complete_8kg_fastener_factory_iqd_set']
        if stripped<=0: raise ValueError('Original structural beam subtotal must be positive')
        new_struct=chosen_beam[i]*fx
        rail_new=rail_unit[case]*fx; fast_new=chosen_fast[i]*fx
        new_factory=new_struct+b['running_rail_kg']*rail_new+b['direct_fastener_sets']*fast_new
        rows['beam_factory']['costs_iqd'][case]=new_factory*count
        rows['substructure_rebar']['costs_iqd'][case]=q['foundation_pier_rebar_kg']*rebar[i]*fx/[.98,.95,.9][i]
        rows['civil_load_detail_reserve']['costs_iqd'][case]=new_factory*count*old['design'].get('load_detail_reserve_fraction',0.)
        # Civil work is also paid across declared utilisation; hired cranes/haul remain unchanged.
        for key in ('substructure_field_labour','erection_labour'):
            rows[key]['costs_iqd'][case]=old['capital_lines'][next(j for j,z in enumerate(old['capital_lines']) if z['key']==key)]['costs_iqd'][case]/.75
        crew_h=p['rail_install_crew'][i]*8
        install=(crew_h*prior['loaded_two_shift_wage_iqd_h']/.75+p['rail_install_machine_iqd_per_8h_shift'][i]+p['rail_geometry_quality_iqd_per_shift'][i])/p['rail_track_m_per_shift'][i]
        rows['field_two_rail_track_install']['costs_iqd'][case]=q['track_m']*install
        result['unit_rates'][case].update(rail_factory_iqd_kg=rail_new,complete_8kg_fastener_factory_iqd_set=fast_new,
            beam_factory_iqd_span=new_factory,rail_field_install_iqd_track_m=install,
            productive_two_shift_wage_iqd_h=prior['loaded_two_shift_wage_iqd_h']/.75)
        deltas[case]=dict(original_structural_beam_iqd=stripped,new_structural_beam_iqd=new_struct,
            original_rail_and_fasteners_removed_iqd=count*(b['running_rail_kg']*prior['rail_factory_iqd_kg']+b['direct_fastener_sets']*prior['complete_8kg_fastener_factory_iqd_set']),
            replacement_rail_and_fasteners_iqd=count*(b['running_rail_kg']*rail_new+b['direct_fastener_sets']*fast_new))
    for key in ('beam_factory','substructure_rebar','civil_load_detail_reserve','substructure_field_labour','erection_labour','field_two_rail_track_install'):
        rows[key]['basis']+=' Outline civil supply route '+scenario+'; paid idle, exact rail/fastener replacement and external owned fixed capital recorded separately.'
        rows[key]['source_class']='C'
    decisions=[dict(item='finished-60E1-rail',selected_route='buy-existing-mill',comparison=rail,
        reason='No project rail rolling mill; GB43 listing is not the selected profile'),
        dict(item='complete-fasteners',selected_route=fast_choice,comparison=fast),
        dict(item='structural-precast-beam',selected_route=beam_choice,comparison=beam)]
    assumptions=dict(source_class='C',scenario=scenario,quantity_geometry_mass_unchanged=True,
        raw_rebar_cn_landed_usd_kg=cn_rebar,rebar_selected_usd_kg=rebar,
        rebar_selected_base_source=rebar_source,rebar_source_by_case=[rebar_source]*3,
        rebar_counterfactual_usd_kg=dict(China=cn_rebar,Iraq=[local_rebar]*3),
        raw_material_grade_equivalence_is_planning_hypothesis=True,plate_landed_usd_kg=plate,
        rail_60E1_FOB_usd_t=[600.,800.,1100.],rail_scope_hold_observation_id='cn-yongyang-gb43-rail',
        fastener_make_material='6 kg local plate + 2 kg accounted specialist bought clip/bolt/insulator/pad package; complete 8 kg accounting retained',
        fastener_specialist_package_plus_consumables_usd_each=[6.4,11.,21.],fastener_floor_m2_charged_in_own_capital=fast_floor,
        paid_labour_hours_per_productive_hour=1/.75,owned_machine_rate_excludes_capital_recovery=True,
        old_full_beam_machine_hire_replaced=True,concrete_recipe_and_prestress_premium_retained=True,
        rebar_purchase_yield=[.98,.95,.9],tendon_purchase_yield=[.99,.98,.95],
        mould_face_area_m2=face_area,mould_face_thickness_m=[.005,.006,.008],mould_steel_mass_kg=mould_mass,
        mould_price_usd_each=mould_price,mould_cycle_workdays=[2.,5.,10.],mould_availability=.75,mould_counts=moulds,
        precast_cells=cells,precast_crew_per_cell_per_shift=crew,precast_storage_m2=storage,
        concrete_material_kit_usd_per_beam=concrete,structural_material_kit_usd_per_beam=materials,
        contractor_overhead_profit_fraction=[.12,.25,.5],contractor_existing_fixed_allocation_usd_per_beam=[250.,750.,2500.],
        precast_fixed_in_comparison_includes_building_and_yard=True,
        returned_precast_fixed_excludes_building_and_yard=True,
        parent_accounting='Replace original complete precast factory allocation; price returned floor/yard once at existing capital rates. Fastener fixed includes its workshop. Do not add a second factory or import-duty uplift to these landed prices.',
        imported_full_concrete_beams_not_selected=True,replacement_accounting=deltas,
        base_choice_retained_across_low_high=True,geometry_or_performance_acceptance=False,
        physical_holds=['prestress transfer','mould extraction and handling','crane at radius','temporary stability','torsion and moving loads','foundations','deformation feedback to magnetic gap','rail and fastener testing/grade/interface qualification'])
    result.pop('evaluation_id',None); result['source_sha256']={**old.get('source_sha256',{}),**before}
    result['supply_scenario']=scenario;result['supply_assumptions_id']=identity(assumptions);result.update(FLAGS)
    result['evaluation_id']=identity(result)
    if result['quantities']!=old['quantities'] or result['beam']!=old['beam']: raise ValueError('Supply repricing changed physical quantities')
    if any(digest(root/name)!=sha for name,sha in before.items()): raise ValueError('Supply sources changed during evaluation')
    output=dict(schema='osr-outline-civil-supply/1',civil=result,decisions=decisions,
        owned_factory_capital_usd=_triple(owned),precast_floor_m2=floor if beam_choice=='make' else [0.,0.,0.],
        precast_yard_m2=yard if beam_choice=='make' else [0.,0.,0.],source_sha256=before,assumptions=assumptions,
        input_civil_evaluation_id=old.get('evaluation_id'),input_civil_identity=identity(old),scenario=scenario,**FLAGS)
    output['evaluation_id']=identity(output)
    return output
