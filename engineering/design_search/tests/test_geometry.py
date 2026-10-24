"""Independent rigid, finite-material and intersample collision controls."""
import math
import numpy as np
import pytest
from engineering.design_search import geometry as g


def rz(angle):
    c,s=math.cos(angle),math.sin(angle)
    return [[c,-s,0],[s,c,0],[0,0,1]]


def box(uid='part',at=(-.5,-.5,-.5),size=(1,1,1),**kw):
    return dict(id=uid,kind='box',at_m=list(at),size_m=list(size),**kw)


def test_exact_rotated_bounds_and_nested_translation_composition():
    first=g.rigid_transform(rz(math.pi/2),[10,20,30])
    second=g.rigid_transform(translation_m=[2,0,0])
    pose=g.compose_transform(first,second)
    assert pose['translation_m']==pytest.approx([10,22,30])
    lo,hi=g.transformed_bounds(box(at=(0,0,0),size=(2,1,3)),pose)
    assert lo==pytest.approx([9,22,30]);assert hi==pytest.approx([10,24,33])
    local=box(at=(0,0,0),size=(2,1,3),rigid_transform=second)
    assert g.transformed_bounds(local,first)[0]==pytest.approx(lo)


@pytest.mark.parametrize('rotation', [np.diag([-1,1,1]),np.diag([2,1,1]),[[1,0,0],[1,1,0],[0,0,1]],np.full((3,3),float('nan'))])
def test_nonproper_or_nonfinite_rotations_are_refused(rotation):
    with pytest.raises(ValueError,match='proper orthonormal'):g.rigid_transform(rotation)


def test_parallel_rotated_stock_has_separating_axis_despite_aabb_overlap():
    a=box(at=(-2,-.05,-.05),size=(4,.1,.1))
    p=g.rigid_transform(rz(math.pi/4));q=g.rigid_transform(rz(math.pi/4),[-.3/math.sqrt(2),.3/math.sqrt(2),0])
    alo,ahi=g.transformed_bounds(a,p);blo,bhi=g.transformed_bounds(a,q)
    assert np.all(np.minimum(ahi,bhi)>np.maximum(alo,blo))
    assert not g.obb_overlap(a,a,p,q)
    assert g.collision_witness(a,a,p,q) is None


def test_crossed_thin_rotated_boxes_produce_an_actual_interior_witness():
    a=box(at=(-2,-.02,-.02),size=(4,.04,.04))
    p=g.rigid_transform(rz(.6));q=g.rigid_transform(rz(-.6))
    witness=g.collision_witness(a,a,p,q)
    assert witness is not None
    assert g.inside_material(witness['point_m'],a,p)
    assert g.inside_material(witness['point_m'],a,q)


def test_drilled_void_is_transformed_with_its_stock():
    plate=box(at=(-1,-1,-1),size=(2,2,2),holes=[dict(axis='z',x_m=1.,y_m=1.,diameter_m=.4,length_m=2.)])
    pin=box(at=(-.05,-.05,-.9),size=(.1,.1,1.8))
    pose=g.rigid_transform(rz(.7),[1,2,3])
    assert g.obb_overlap(plate,pin,pose,pose)
    assert g.collision_witness(plate,pin,pose,pose) is None
    material=box(at=(.5,.5,-.9),size=(.1,.1,1.8))
    assert g.collision_witness(plate,material,pose,pose) is not None


def test_tangent_cylinders_do_not_earn_positive_volume_material_witness():
    first=dict(id='a',kind='cylinder',at_m=[-1,-1,-1],size_m=[2,2,2])
    second=dict(id='b',kind='cylinder',at_m=[1,-1,-1],size_m=[2,2,2])
    assert g.collision_witness(first,second) is None


def test_translation_between_clear_endpoint_samples_remains_blocked():
    moving=[box('moving',(-.025,-.025,-.025),(.05,.05,.05))]
    fixed=[box('fixed',(-.025,-.025,-.025),(.05,.05,.05))]
    poses=[g.rigid_transform(translation_m=[x,0,0]) for x in (-.2,.2)]
    result=g.swept_clearance(moving,fixed,poses,max_translation_step_m=.4)
    assert result['sampled_envelopes_clear']
    assert not result['continuous_envelopes_separated']
    assert result['unresolved_segment_enclosures']
    with pytest.raises(ValueError,match='resolution'):g.swept_clearance(moving,fixed,poses)
    poses.insert(1,g.rigid_transform())
    assert g.swept_clearance(moving,fixed,poses,max_translation_step_m=.4)['material_interference_count']==1


def test_rotational_arc_enclosure_catches_motion_outside_endpoint_aabbs():
    moving=[box('moving',(.95,.95,-.05),(.1,.1,.1))]
    fixed=[box('fixed',(-.025,math.sqrt(2)-.025,-.025),(.05,.05,.05))]
    poses=[g.rigid_transform(rz(angle)) for angle in (0,math.pi/2)]
    result=g.swept_clearance(moving,fixed,poses,max_rotation_step_rad=math.pi/2)
    assert result['sampled_envelopes_clear']
    assert not result['continuous_envelopes_separated']
    assert result['unresolved_segment_enclosures'][0]['rotation_sagitta_bound_m']>0
    poses.insert(1,g.rigid_transform(rz(math.pi/4)))
    assert g.swept_clearance(moving,fixed,poses,max_rotation_step_rad=math.pi/2)['material_interference_count']==1


def test_conservative_separation_is_available_only_under_declared_path_model():
    result=g.swept_clearance([box('moving')],[box('fixed',(0,5,0))],
        [g.rigid_transform(),g.rigid_transform(translation_m=[.02,0,0])],clearance_m=.01)
    assert result['continuous_envelopes_separated']
    assert result['path_clearance_screen_pass']
    assert not result['clearance_qualified']
    assert result['interpolation']=='linear-translation-shortest-geodesic-rotation'


def test_empty_unsynchronised_and_unbounded_paths_refuse():
    with pytest.raises(ValueError):g.swept_clearance([box('a')],[box('b')],[])
    poses=[dict(**g.rigid_transform(),time_s=t) for t in (1.,1.)]
    with pytest.raises(ValueError,match='increasing'):g.swept_clearance([box('a')],[box('b')],poses)
    with pytest.raises(ValueError):g.obb_overlap(box(),box(),clearance_m=-1)
