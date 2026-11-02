"""Typed fixture controls only: no selected-ledger campaign or native worker."""
from copy import deepcopy
import pytest

from engineering.design_search import flanged_span as span
from engineering.station_rail.common import identity


@pytest.fixture
def context(monkeypatch):
    rows=[]
    # Explicit test fixture, not a newly authenticated selected-ledger receipt.
    for mass,tare in [('low',17203.958),('base',19221.998),('high',21240.038)]:
        for name,people in [('empty',0),('normal',46),('crowd_control',160)]:
            loaded=tare+people*75.
            rows.append(dict(name=name,vehicle_mass_case=mass,passengers_per_car=people,
                tare_kg_per_car=tare,loaded_kg_per_car=loaded,
                full_axle_force_N=loaded*span.civil.G/4*1.3,offsets_m=span._offsets()))
    value=span._seal(dict(schema='osr-flanged-span-load-context/1',
        vehicle_candidate_id=span.VEHICLE_ID,selection_id=span.SELECTION_ID,
        vehicle_evaluation_id='1'*64,body_candidate_id='2'*64,support_component_id='3'*64,
        propulsion_component_id='4'*64,selected_context_id='5'*64,mass_reserve_result_id='6'*64,
        dynamic_factor_applied_once=1.3,cases=rows,source_sha256=span._sources(),**span.FLAGS),'context_id')
    frozen=deepcopy(value)
    monkeypatch.setattr(span,'load_context',lambda root=span.ROOT:deepcopy(frozen))
    return value


def reseal(value,key):
    value.pop(key,None)
    return span._seal(value,key)


def test_actual_polygons_mass_cg_and_steel_inertia():
    c=span.generate();q=span.quantities(c);g=q['source_quantities']
    assert len(c['physical_definition']['cells'][0]['sections'])==7
    rail=c['physical_definition']['rail_interface']
    assert rail['track_gauge_m']==1.435
    assert rail['rail_centre_spacing_m']==pytest.approx(1.507)
    assert rail['rail_centre_spacing_m']==rail['track_gauge_m']+rail['rail_head_width_m_hypothesis']
    assert rail['rail_centres_y_m']==pytest.approx([-.7535,.7535])
    assert g['by_material']['research_concrete']['volume_m3']==pytest.approx(7.2)
    steel=2*(2*.3*.025+.012*1.15)*20*7850
    assert steel==pytest.approx(9043.2)
    assert g['by_material']['structural_steel']['mass_kg']==pytest.approx(steel)
    assert g['total_nominal_stock_mass_kg']==pytest.approx(steel+18000)
    assert g['centroid_m']==pytest.approx([10,0,(-steel*.78-18000*.09)/(steel+18000)])
    assert g['by_material']['structural_steel']['I_y_m4']==pytest.approx(.013398)
    assert q['rail_mass_kg']==pytest.approx(2408.4)
    assert q['fastener_set_count']==70
    assert q['fastener_mass_kg']==560
    for i,case in enumerate(span.CASES):
        assert q['accounted_mass_kg_cases'][case]==pytest.approx(
            steel+18000+2408.4+560+sum(v[i] for v in q['reserve_mass_kg'].values()))
    assert q['complete_installed_mass_kg'] is None
    assert q['reserve_CG_and_inertia'] is None
    assert q['unknown_is_zero'] is False


@pytest.mark.parametrize('gauge',span.GAUGES)
def test_exact_prism_adapter_and_physical_flags(gauge):
    c=span.generate(gauge);s=span.default_spec();a=span._section_candidate(c,s)
    assert span.geometry.validate(a)
    assert c['candidate_id']==identity(c['physical_definition'])
    assert a['candidate_id']!=c['candidate_id']
    assert all(c[k] is False for k in span.FLAGS)
    assert a['provenance']['external_physical_candidate_id']==c['candidate_id']
    for row in a['cells'][0]['sections']:
        assert max(p[1] for p in row['polygon_yz_m'])<=0


def test_evaluation_assumptions_never_change_physical_identity():
    c=span.generate();first=span.quantities(c)
    s=span.default_spec();s['steel_density_kg_m3']=8000;s['steel_E_Pa']=190e9
    second=span.quantities(c,s)
    assert first['candidate_id']==second['candidate_id']==c['candidate_id']
    assert first['evaluation_id']!=second['evaluation_id']
    assert first['section_adapter_candidate_id']!=second['section_adapter_candidate_id']
    cost1=span.estimate(c);s['rates']['steel_iqd_kg']=[2000.,3000.,5000.]
    cost2=span.estimate(c,spec=s)
    assert cost1['candidate_id']==cost2['candidate_id']
    assert cost1['evaluation_id']!=cost2['evaluation_id']


def test_all_gauges_are_real_and_cost_more_for_more_steel():
    candidates=[span.generate(g) for g in span.GAUGES]
    assert len({c['candidate_id'] for c in candidates})==3
    q=[span.quantities(c) for c in candidates]
    costs=[span.estimate(c,quantity=v) for c,v in zip(candidates,q)]
    for i in (1,2):
        assert q[i]['source_quantities']['by_material']['structural_steel']['mass_kg']>q[0]['source_quantities']['by_material']['structural_steel']['mass_kg']
        for case in span.CASES:
            assert costs[i]['cases'][case]['scoped_installed_iqd']>costs[0]['cases'][case]['scoped_installed_iqd']


@pytest.mark.parametrize('change',['unsealed','resealed-stock','gauge-alias','promoted','source'])
def test_geometry_identity_tampering_rejected(change):
    c=span.generate()
    if change in ('unsealed','resealed-stock'):
        c['physical_definition']['cells'][0]['sections'][0]['polygon_yz_m'][0][0]=-.9
    elif change=='gauge-alias':c['gauge']='thick-web'
    elif change=='promoted':c['physical_accepted']=True
    else:c['source_sha256'][span.PRODUCER]='0'*64
    if change!='unsealed':reseal(c,'geometry_id')
    with pytest.raises(ValueError):span.quantities(c)


def test_textbook_bending_actual_gravity_and_complete_case_matrix(context):
    c=span.generate();r=span.evaluate(c,context)
    assert r['EI_Nm2']==pytest.approx(2.6796e9)
    assert r['steel_only_model']['name']=='steel-only-longitudinal'
    assert len(r['responses'])==81 and len(r['all_position_model_bounds'])==27
    labels={(x['load_case'],x['vehicle_mass_case'],x['span_mass_case'],x['pose']['name']) for x in r['responses']}
    assert len(labels)==81
    q=span.quantities(c)
    for row in r['responses']:
        response=row['response'];total=q['accounted_mass_kg_cases'][row['span_mass_case']]*span.civil.G+sum(p['force_N'] for p in row['points'])
        assert response['reaction_left_N']+response['reaction_right_N']==pytest.approx(total)
        assert row['total_downward_force_N']==pytest.approx(total)
        assert all(p['force_N']==row['full_axle_force_N'] for p in row['points'])
        assert row['full_axle_force_N'] in {x['full_axle_force_N'] for x in context['cases']}
        assert abs(response['force_residual_N'])<1e-6
        assert abs(response['moment_residual_Nm'])<1e-5
    for row in r['all_position_model_bounds']:
        assert row['maximum_simultaneous_axles']==6
        assert row['dead_load_midspan_m']==pytest.approx(row['dead_load_textbook_m'],rel=1e-12)
        for x in r['responses']:
            if (x['load_case'],x['vehicle_mass_case'],x['span_mass_case'])==(row['load_case'],row['vehicle_mass_case'],row['span_mass_case']):
                assert max(x['response']['deflection_at_observation_m'])<=row['all_position_model_deflection_upper_m']
    assert r['physical_strength_allowable_Pa'] is None
    assert r['physical_deflection_limit_m'] is None
    assert r['integrated_selection'] is None
    assert all(r[k] is False for k in span.FLAGS)


def test_concrete_E_has_no_longitudinal_stiffness_credit(context):
    c=span.generate();s=span.default_spec();s['concrete_E_Pa']=100e9
    a=span.evaluate(c,context);b=span.evaluate(c,context,s)
    assert a['EI_Nm2']==b['EI_Nm2']
    assert a['responses']==b['responses']
    assert a['evaluation_id']!=b['evaluation_id']


def test_independent_midpoint_point_load_formula():
    ei=2.6796e9;force=100000.
    cell=dict(x_start_m=0.,x_end_m=20.,EI_Nm2=ei,distributed_load_N_m=0.)
    answer=span.beam.analyse([cell],[dict(x_m=10.,force_N=force)],10.)
    assert answer['deflection_at_observation_m']==pytest.approx(force*20**3/(48*ei),rel=1e-12)


@pytest.mark.parametrize('change',['candidate','selection','duplicate','force-double','half-axle','formation','stale-source','negative-mass'])
def test_mixed_or_fabricated_load_accounting_rejected(context,change):
    if change=='candidate':context['vehicle_candidate_id']='0'*64
    elif change=='selection':context['selection_id']='0'*64
    elif change=='duplicate':context['cases'][0]=deepcopy(context['cases'][1])
    elif change=='force-double':context['cases'][0]['full_axle_force_N']*=1.3
    elif change=='half-axle':context['cases'][0]['full_axle_force_N']/=2
    elif change=='formation':context['cases'][0]['offsets_m'][0]+=.1
    elif change=='negative-mass':context['cases'][0]['tare_kg_per_car']=-1
    else:context['source_sha256'][span.PRODUCER]='0'*64
    reseal(context,'context_id')
    with pytest.raises(ValueError):span.evaluate(span.generate(),context)


def test_cost_units_and_labour_are_counted_once():
    c=span.generate();s=span.default_spec();cost=span.estimate(c,spec=s);stock=cost['manufacturing_stock']
    assert stock['flange_plates']==16 and stock['web_plates']==8
    assert stock['girder_splices']==6 and stock['bracing_stations']==9
    assert stock['bearing_assemblies']==4 and stock['double_fillet_weld_m']==160
    assert stock['module_splice_x_m']==[5.,10.,15.]
    assert stock['splice_continuity_qualified'] is False
    for i,case in enumerate(span.CASES):
        row=cost['cases'][case];hours=sum(row['factory_labour_hours'].values())
        assert row['fabrication_iqd']['labour']==pytest.approx(hours*s['rates']['labour_iqd_h'][i])
        assert row['factory_gate_iqd']==pytest.approx(sum(row['material_iqd'].values())+sum(row['fabrication_iqd'].values())+row['overhead_iqd'])
        assert row['delivered_iqd']==row['factory_gate_iqd']+row['delivery_iqd']
        assert row['scoped_installed_iqd']==pytest.approx(row['delivered_iqd']+sum(row['installation_iqd'].values()))
        assert row['production_days_capacity_lower_bound']>=hours/(2*8*.75*4)
    assert cost['complete_installed_cost_iqd'] is None
    assert cost['dedicated_plant_capital_iqd'] is None
    assert cost['lifecycle_cost_iqd'] is None
    assert cost['whole_system_ranking_allowed'] is False
    assert cost['schedule_is_precedence_resolved'] is False


@pytest.mark.parametrize('bad',[0.,-1.,float('nan'),float('inf')])
def test_unknown_reserves_cannot_disappear_or_be_nonfinite(bad):
    spec=span.default_spec();spec['reserve_mass_kg']['bearings']=[bad,bad,bad]
    with pytest.raises(ValueError):span.quantities(span.generate(),spec)


def test_changed_quantities_cannot_be_costed_as_same_record():
    c=span.generate();q=span.quantities(c);q['rail_mass_kg']*=2
    reseal(q,'evaluation_id')
    with pytest.raises(ValueError):span.estimate(c,q)


def test_validly_resealed_alternative_tare_cannot_replace_selected_ledger(context):
    for row in context['cases']:
        row['tare_kg_per_car']+=1000
        row['loaded_kg_per_car']+=1000
        row['full_axle_force_N']=row['loaded_kg_per_car']*span.civil.G/4*1.3
    reseal(context,'context_id')
    with pytest.raises(ValueError,match='freshly generated'):
        span.evaluate(span.generate(),context)


def test_resealed_component_evaluation_identity_mismatch_rejected(context):
    context['support_component_id']='0'*64
    reseal(context,'context_id')
    with pytest.raises(ValueError,match='freshly generated'):
        span.evaluate(span.generate(),context)


@pytest.mark.parametrize('key,value',[('production_shifts_per_day',1),('civil_shifts_per_day',3),
    ('hours_per_shift',12),('steel_E_Pa',float('inf')),('steel_density_kg_m3',-1)])
def test_explicit_model_and_shift_domains(key,value):
    s=span.default_spec();s[key]=value
    with pytest.raises(ValueError):span.quantities(span.generate(),s)
