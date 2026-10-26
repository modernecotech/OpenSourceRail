from engineering.station_rail import civil,vehicle


def test_per_section_critical_pose_not_global_peak_reused():
    rows=civil.moving_envelope(20.,[0.,2.1,12.8,14.9],60000.)
    assert len({round(r['critical_train_translation_m'],6) for r in rows[1:-1]})>2
    for a,b in zip(rows,reversed(rows)):
        assert abs(a['max_live_moment_Nm']-b['max_live_moment_Nm'])<1e-6
    assert rows[0]['max_live_moment_Nm']==0
    assert rows[-1]['max_live_moment_Nm']<1e-6


def test_three_families_and_complete_quantity_boundaries():
    v=vehicle.build();c=civil.evaluate(v)
    assert len(c['alternatives'])==12
    assert {r['family'] for r in c['alternatives']}=={'twin-beam','box-beam','u-beam'}
    assert c['candidate_id']==v['candidate_id']
    r=c['selected_reference']
    assert r['running_rail_kg']==2*civil.RAIL_KG_M*r['span_m']
    assert r['direct_fastener_anchors']==r['direct_fastener_sets']*2
    assert r['prestress_kg']>0
    assert r['actual_installed_cost_USD'] is None
    assert not c['magnetic_suspension_facings']
    assert not r['physical_accepted']


def test_interior_pier_checks_entire_formation_on_both_spans():
    v=vehicle.build();offsets,axle_N=civil.axle_train(v)
    reaction=civil.interior_pier_train_reaction(30.,offsets,axle_N)
    arbitrary_head_pose=axle_N*len([a for a in offsets if a<=30.])
    assert reaction['maximum_live_reaction_N']>arbitrary_head_pose
    c=civil.evaluate(v)
    assert c['executed_case_count']==39
    assert c['control_alternatives']['crowd_control'][0]['load_case']=='crowd_control'


def test_crowd_checks_fixed_normal_beam_not_resized_tendons():
    c=civil.evaluate(vehicle.build())
    for base,control in zip(c['alternatives'],c['control_alternatives']['crowd_control']):
        assert control['prestress_strands']==base['prestress_strands']
        assert control['physical_civil_component_id']==base['physical_civil_component_id']
        assert control['prestress_design_policy']=='fixed-normal-design-stock'
        assert control['max_service_tension_Pa']>=base['max_service_tension_Pa']


def test_selected_reference_is_same_crowd_sized_beam_at_all_loads():
    c=civil.evaluate(vehicle.build());ref=c['selected_reference']
    assert ref['load_case']=='crowd_control'
    assert c['civil_component_id']==ref['physical_civil_component_id']
    for case in c['selected_physical_load_checks'].values():
        assert case['prestress_strands']==ref['prestress_strands']
        assert case['physical_civil_component_id']==c['civil_component_id']
    assert ref['span_m']==20.
    assert ref['necessary_longitudinal_screen']=='pass'
