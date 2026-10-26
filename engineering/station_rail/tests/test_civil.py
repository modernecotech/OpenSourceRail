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
    assert r['running_rail_kg']==3010.5
    assert r['direct_fastener_anchors']==r['direct_fastener_sets']*2
    assert r['prestress_kg']>0
    assert r['actual_installed_cost_USD'] is None
    assert not c['magnetic_suspension_facings']
    assert not r['physical_accepted']
