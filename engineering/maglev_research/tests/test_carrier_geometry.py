"""Finite stock, independent pivots and explicit slide travel govern curve fit."""
from copy import deepcopy
from hashlib import sha256
import math

import pytest

from engineering.maglev_research import carrier_geometry as g


def layout(n=12,length=.92,pitch=1.):
    return dict(id='fixture',module_count=2*n,
        module_centres_x_m=[(i-(n-1)/2)*pitch for i in range(n)],
        row_centres_y_m=[-.88,.88],body_length_m=17.,body_end_clearance_m=.5,
        current_body_width_m=2.65,proposed_underbody_clearance_width_m=3.,
        stock_bounds=dict(minimum_m=[-length/2,-.4,-.44],maximum_m=[length/2,.5,.516],size_m=[length,.9,.956]))


def test_full_finite_stock_can_fail_when_point_module_centres_fit():
    finite=layout(n=3,length=.96)
    points=layout(n=3,length=.000001)
    a=g.evaluate(finite,[finite['module_centres_x_m']],100.,.002,'yaw-and-lateral-slide')
    b=g.evaluate(points,[points['module_centres_x_m']],100.,.002,'yaw-and-lateral-slide')
    assert not a['finite_gap_screen_pass']
    assert b['finite_gap_screen_pass']
    assert a['maximum_finite_stock_radial_mismatch_m']>b['maximum_finite_stock_radial_mismatch_m']


def test_multiple_fixed_yaw_pivots_cannot_inherit_free_lateral_slides():
    a=layout()
    groups=next(g.partitions(a['module_centres_x_m'],3))
    fixed=g.evaluate(a,groups,300.,.002,'yaw-only-fixed-pivots')
    sliding=g.evaluate(a,groups,300.,.002,'yaw-and-lateral-slide')
    assert not fixed['finite_gap_screen_pass']
    assert fixed['lateral_slides_per_car']==0
    assert all(carrier['pivot_body_y_m']==0 for carrier in fixed['carrier_poses'])
    assert sliding['finite_gap_screen_pass']
    assert sliding['conditional_stock_geometry_screen_pass']
    assert sliding['lateral_slides_per_car']==sliding['yaw_joints_per_car']==3
    assert sliding['required_one_sided_lateral_slide_travel_m']>0
    assert sliding['joint_added_mass_kg'] is None
    assert not sliding['joint_installed_fit_verified']


def test_recentered_exact_radial_extremes_bound_dense_finite_box_samples():
    a=layout(n=3,length=.96)
    group=a['module_centres_x_m']
    bounds=a['stock_bounds']
    shift=g.recenter(group,bounds,a['row_centres_y_m'],150.)
    low,high=g.extremes(group,bounds,a['row_centres_y_m'],150.,shift)
    assert low==pytest.approx(-high,abs=1e-10)
    samples=[]
    for centre in group:
        for i in range(21):
            u=centre+bounds['minimum_m'][0]+i*bounds['size_m'][0]/20
            for v in (-1.28,0.,1.38):
                independent=math.hypot(u,150-v-shift)-(150-v)
                assert g.radial_error(u,v,shift,150.)==pytest.approx(independent,abs=1e-13)
                samples.append(independent)
    assert min(samples)>=low-1e-12
    assert max(samples)<=high+1e-12
    assert max(samples)==pytest.approx(high,abs=1e-12)


def test_body_translation_and_counted_slides_reproduce_actual_circle_pose():
    a=layout(n=15,length=.96,pitch=1.01)
    groups=next(g.partitions(a['module_centres_x_m'],5))
    result=g.evaluate(a,groups,150.,.002,'yaw-and-lateral-slide')
    assert result['conditional_stock_geometry_screen_pass']
    assert result['minimum_slide_pose_required_underbody_width_m']>3.
    assert result['additional_body_translation_for_package_m']>0
    assert result['required_centred_underbody_width_m']<=3.
    assert result['required_one_sided_lateral_slide_travel_m']>0.0613
    for carrier in result['carrier_poses']:
        x=carrier['pivot_body_x_m']
        world_y=result['body_lateral_offset_m']+carrier['pivot_body_y_m']
        assert math.hypot(x,150-world_y)==pytest.approx(150-carrier['normal_recentring_m'],abs=1e-12)
    assert not result['current_body_width_screen_pass']
    assert not result['cooler_and_separate_guidance_installed_fit_verified']


def test_clearance_uses_rotated_boxes_and_tolerance_inflation():
    bounds=dict(minimum_m=[-.5,-.2,0.],maximum_m=[.5,.2,1.],size_m=[1.,.4,1.])
    first=g.corners(0,0,.2,bounds)
    # Translate along the same rotated carrier tangent, leaving1mm nominalgap.
    second=g.corners(1.001*math.cos(.2),1.001*math.sin(.2),.2,bounds)
    distance,collisions=g.clearance([first,second])
    assert collisions==0
    assert distance==pytest.approx(.001,abs=1e-12)
    inflated=[g.corners(0,0,.2,bounds,.001),
        g.corners(1.001*math.cos(.2),1.001*math.sin(.2),.2,bounds,.001)]
    assert g.clearance(inflated)[1]==1


def test_balanced_partitions_preserve_every_module_and_at_most_two_lengths():
    positions=list(range(15))
    cases=list(g.partitions(positions,4))
    assert len(cases)==4
    for groups in cases:
        assert [x for group in groups for x in group]==positions
        assert max(map(len,groups))-min(map(len,groups))==1
    with pytest.raises(ValueError):list(g.partitions(positions,16))


def test_invalid_tolerance_does_not_expand_physical_gap_limits():
    a=layout()
    groups=next(g.partitions(a['module_centres_x_m'],4))
    with pytest.raises(ValueError,match='positive physical gap allowance'):
        g.evaluate(a,groups,150.,.006,'yaw-and-lateral-slide')


@pytest.mark.parametrize('mutation', ['omitted-module','duplicate-module','wrong-total'])
def test_a_carrier_fit_cannot_drop_counted_modules(mutation):
    a=layout()
    groups=next(g.partitions(a['module_centres_x_m'],4))
    if mutation=='omitted-module':groups[0].pop()
    elif mutation=='duplicate-module':groups[0].append(groups[0][0])
    else:a['module_count']=30
    with pytest.raises(ValueError,match='every declared finite module exactly once'):
        g.evaluate(a,groups,150.,.002,'yaw-and-lateral-slide')


def test_stock_bounds_include_every_material_envelope():
    parts=[dict(at_m=[-.4,-.2,-.5],size_m=[.8,.4,1.]),
           dict(at_m=[-.48,-.4,.4],size_m=[.96,.9,.116])]
    bounds=g.stock_bounds(parts)
    assert bounds['minimum_m']==[-.48,-.4,-.5]
    assert bounds['maximum_m']==pytest.approx([.48,.5,.516])
    assert bounds['size_m']==pytest.approx([.96,.9,1.016])


def test_source_bound_sweep_preserves_unknown_installed_parts_and_failure_cases():
    value=g.study()
    assert value['executed_geometry_cases']==160
    assert value['yaw_only_geometry_survivors']==0
    assert value['slide_geometry_survivors']>0
    assert not value['complete_installed_carrier_fit']
    assert not value['dynamics_rerun_ready']
    for name,expected in value['source_sha256'].items():
        assert sha256((g.ROOT/name).read_bytes()).hexdigest()==expected
    assert all(not row['system_eligible'] for row in value['cases'])
    recommended={(row['layout'],row['radius_m'],row['tolerance_reserve_m']):row for row in value['recommendations']}
    assert recommended[('canonical24-stock',150.,.002)]['least_carrier_count']==4
    assert recommended[('proposed30-wide-stock',150.,.002)]['least_carrier_count']==5
    assert recommended[('canonical24-stock',300.,.002)]['least_carrier_count']==3
    assert recommended[('proposed30-wide-stock',300.,.002)]['least_carrier_count']==4
    assert not any(row['stock_geometry_candidate'] for row in value['recommendations'] if row['radius_m']<=100.)
