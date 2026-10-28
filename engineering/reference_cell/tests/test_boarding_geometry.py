from engineering.reference_cell import civil


def test_two_platforms_follow_negative_door_side_and_actual_floor_top_without_claiming_accessibility():
    r=civil.generate('a'*64,platform_height_above_rail_m=1.0257,door_side=-1)
    platforms=[p for p in r['stock'] if p['id'].endswith('/platform')]
    assert len(platforms)==2
    for p in platforms:
        assert abs(p['at_m'][2]+p['size_m'][2]-(r['rail_top_global_z_m']+1.0257))<1e-10
        assert p['at_m'][1]+p['size_m'][1]<-1.4
    assert r['boarding_accessibility_qualified'] is False


def test_positive_door_side_is_mirrored_without_changing_floor_or_counted_concrete():
    left=civil.generate('a'*64,door_side=-1);right=civil.generate('a'*64,door_side=1)
    assert left['concrete_volume_m3']==right['concrete_volume_m3']
    assert all(p['at_m'][1]>1.4 for p in right['stock'] if p['id'].endswith('/platform'))
