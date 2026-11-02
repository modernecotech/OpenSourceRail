from copy import deepcopy
import pytest
from engineering.design_search import matched_renewal_research as m


def sample():
    assumptions={'production_shifts_per_day':2,'production_hours_per_shift':8,'civil_shifts_per_day':2,'civil_hours_per_shift':8,
        'design_life_years':30,'real_discount_rate':.04,'operating_hours_per_day_cases':[16,18,24],
        'maintenance_reference_operating_hours_per_day':18,'benchmark_rates_iqd':{'wage_skilled_iqd_per_h':7500},
        'assumptions':{'wage_burden_multipliers':[1.25,1.5,2.], 'second_shift_wage_premium':[0.,.1,.2],
            'finished_equipment_iqd_per_kg':[20000.,80000.,300000.], 'factory_overhead_fraction':[.1,.2,.3],
            'maintenance_fraction_per_year':[.015,.04,.09], 'construction_contingency_fraction':[.1,.2,.3],
            'decommissioning_fraction_of_installed_CAPEX':[.01,.03,.08]}}
    scopes={s:[1000.,2000.,3000.] for s in m.cost.model.SCOPES}
    groups=[{'asset_group':'guideway','cases':[{'events':[]} for _ in range(3)]}]
    def line(key,quantity,scenario=None):return {'line_key':key,'quantity':quantity,'scenario_iqd':scenario or {'low':0.,'base':0.,'high':0.}}
    lines=[line('precast-beam-concrete-recipe',{'net_concrete_m3':13368.96}),
        line('erection-rail-installation-and-temporary-works',{'field_hours':[12000.,38400.,108000.]}),
        line('beam-heavy-haul-to-site',{'counted_span_mass_t':62.151672}),
        line('bounded-asset-replacements',{'renewal_plan':{'asset_groups':groups}})]
    case={'civil_design_basis':{'family':'box-beam','span_m':20.},'cost':{'corridor_basis':{'span_count':600},
        'cost_line_items':lines,'scope_totals_iqd':scopes,'model_based_installed_CAPEX_iqd':[1e9,2e9,3e9]},
        'renewal_line':{'scenario_iqd':{'low':5.,'base':6.,'high':7.}}}
    context={'cases':[{'name':'normal','vehicle_mass_case':'base','offsets_m':[0.], 'full_axle_force_N':1e5}]}
    return case,{'assumptions':assumptions},context


def test_concrete_reserve_arithmetic_and_erection_partition():
    case,baseline,context=sample();r=m._reference(case,baseline,context,m.assumptions(),False,sealer=False)
    rows=r['rows'];supply=[600*(r['finished_iqd']+r['qa_iqd']+r['overhead_iqd']+r['transport_iqd']) for r in rows]
    assert supply == pytest.approx([1_323_618_750.,11_544_804_000.,93_781_776_000.])
    assert [x['installation_hours_partitioned'] for x in rows]==[4,8,16]
    assert r['scope_totals_iqd']['construction'][1] == pytest.approx(2000+600*rows[1]['transport_iqd'])
    assert rows[1]['incremental_installation_if_not_included_iqd'] == pytest.approx(600*8*11812.5*1.2)
    assert r['concrete_m3_per_span']==pytest.approx(22.2816)
    assert r['coating_outer_longitudinal_area_m2_per_span']==136
    assert r['support']['base']['normal'][1]['interior_vertical_N']>r['support']['base']['normal'][0]['interior_vertical_N']


def test_concrete_sealer_is_separate_addition_and_does_not_include_cavity():
    case,base,context=sample();s=m.assumptions()
    a=m._reference(case,base,context,s,False,sealer=False);b=m._reference(case,base,context,s,True,sealer=True)
    assert a['rows'][1]['sealer_factory_iqd']==0
    assert b['rows'][1]['sealer_factory_iqd']>0
    assert b['scope_totals_iqd']['guideway'][1]-a['scope_totals_iqd']['guideway'][1]==pytest.approx(600*b['rows'][1]['sealer_factory_iqd'])
    assert 'interior' in b['coating_scope']
    assert all(x['sealer_events'] is None for x in a['rows'])
    assert b['rows'][1]['sealer_events']['present_value_iqd']>0


def test_parent_replacement_resets_component_ages_and_avoids_duplicate_event():
    r=m._events(30,10,[10,25],100.,600,.04)
    assert [(e['year'],e['covered_by_parent_replacement']) for e in r['events']]==[(10.,True),(20.,False)]
    assert r['present_value_iqd']==pytest.approx(600*100/(1.04**20))


def test_reject_partition_exceeding_original_hours_and_invalid_bounds():
    case,base,context=sample();spec=m.assumptions();spec['bearing_install_hours_per_span']=[21,22,23]
    with pytest.raises(ValueError,match='exceeds'):
        m._reference(case,base,context,spec,False,sealer=False)
    for key,value in [('bearing_mass_kg_per_span',[0,200,400]),('bearing_count_per_span',0),('maintenance_overlap_fraction',[0,1.1])]:
        spec=m.assumptions();spec[key]=value
        with pytest.raises(ValueError):m._assumptions(spec)


def test_overlap_is_a_bounded_sensitivity_not_an_added_charge():
    item={'scope_totals_iqd':{s:[10.,20.,30.] for s in m.cost.model.SCOPES},'rows':[{'explicit_component_renewal_npv_iqd':8.} for _ in range(3)]}
    result=m._scenario_totals(item,m.assumptions())
    assert result[1]['base_npv_iqd']==280
    assert result[1]['overlap_removed_iqd']==2
    assert result[1]['overlap_sensitivity_npv_iqd']==278


def test_component_event_and_hypothesis_inputs_do_not_mutate():
    original=m.assumptions();keep=deepcopy(original);out=m._assumptions(original);out['bearing_mass_kg_per_span'][0]=999
    assert original==keep
    with pytest.raises(ValueError,match='source epoch'):
        m.compare('/missing',root='/tmp',expected_publication_manifest_id='x',expected_topology_manifest_id='y',expected_flanged_manifest_id='z')


def test_flanged_coating_uses_candidate_route_and_replaces_old_event():
    case,base,context=sample();rows=[]
    for name in m.CASES:
        rows.append({'case':name,'shared_loaded_wage_iqd_per_h':10000.,'added_coating_person_hours':10.,
            'factory_items_iqd':{'coating_consumables':100000.},'reserve_cost_iqd':{'bearings':200000.},
            'transport_distance_km':50.,'transport_iqd_per_tonne_km':3000.,'coating_renewal_years':10.,'bearing_renewal_years':20.})
    scopes={s:[10000.,20000.,30000.] for s in m.cost.model.SCOPES};groups=[{'asset_group':'guideway','cases':[{'events':[]} for _ in range(3)]}]
    groups[0]['cases'][1]['events']=[{'year':25.}]
    flanged_case={'scope_totals_iqd':scopes,'corridor_basis':{'span_count':600},'cost_line_items':[{'line_key':'flanged-coating-and-bearing-renewals','scenario_iqd':{'low':1.,'base':2.,'high':3.}}],
        'model_based_installed_CAPEX_iqd':[1.,2.,3.],'renewal_plan':{'asset_groups':groups}}
    record={'cases':{'base':flanged_case},'normalized_span_cost':{'cases':rows},'support_demands':{'cases':{'base':{}}}}
    detail={'cost':{'assumptions':{'reserve_mass_kg':{'bearings':[100.,200.,400.]}},'manufacturing_stock':{'steel_coating_m2':100.}}}
    out=m._flanged(record,detail,base,m.assumptions(),'base');r=out['rows'][1]
    assert r['coating_material_iqd']==100000
    assert r['coating_actual_route_labour_iqd']==100000
    assert out['scope_totals_iqd']['renewals'][1] == pytest.approx(20000-2+r['explicit_component_renewal_npv_iqd']+r['parent_coating_qa_npv_iqd'])
    assert r['bearing_mass_kg_per_span']==200
    assert len(out['scope_totals_iqd'])==14
    initial=600*100*.01*10000*1.2
    assert r['initial_coating_qa_corridor_iqd']==pytest.approx(initial)
    assert out['scope_totals_iqd']['guideway'][1]==pytest.approx(20000+initial)
    assert r['installed_capex_iqd']==pytest.approx(2+initial)
    assert r['parent_coating_qa_npv_iqd']==pytest.approx(initial/(1.04**25))
    assert out['scope_totals_iqd']['maintenance'][1]>20000
    assert out['scope_totals_iqd']['disposal'][1]>20000


def test_reference_physical_identity_uses_each_civil_geometry_not_evaluation_or_price():
    case={'physical_civil_component_id':'a'*64,'source_civil_evaluation_id':'d'*64,'prestress_strands':25}
    first=m._reference_composition(case,'b'*64,'unsealed')
    altered=dict(case,source_civil_evaluation_id='e'*64,prestress_strands=99)
    assert m._reference_composition(altered,'b'*64,'unsealed')['candidate_id']==first['candidate_id']
    assert m._reference_composition(dict(case,physical_civil_component_id='c'*64),'b'*64,'unsealed')['candidate_id']!=first['candidate_id']
    assert m._reference_composition(case,'b'*64,'outer_sealer')['candidate_id']!=first['candidate_id']
    assert 'baseline_id' not in first['physical_definition']
    assert 'mass_kg_per_span' not in first['physical_definition']['bearing_concept']
