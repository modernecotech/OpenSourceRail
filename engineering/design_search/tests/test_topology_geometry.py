from copy import deepcopy
import pytest
from engineering.station_rail.common import identity
from engineering.design_search import topology_geometry as g


def refined(mask):return [[v for v in row for _ in (0,1)] for row in mask for _ in (0,1)]
def ring():return [[1,1,1,1],[1,0,0,1],[1,0,0,1],[1,1,1,1]]


@pytest.mark.parametrize('mask',[[[1]],ring(),[[1,1,0],[1,0,0],[1,1,1]],[[1,0],[0,1]],[[0]]])
def test_same_actual_union_has_grid_independent_physical_identity(mask):
    a=g.realize(mask);b=g.realize(refined(mask));assert a==b
    assert a['candidate_id']==identity(a['physical_definition'])
    assert g.quantities(a)==g.quantities(b)


def test_ring_actual_hole_boundaries_volume_and_splice_intersections():
    c=g.realize(ring());p=c['web_geometry'];q=g.quantities(c)
    assert p['area_m2']==18 and p['hole_pierces']==1 and p['finite_edge_components']==1
    assert p['cut_perimeter_m']==pytest.approx(63.6)
    assert len(p['boundary_segments_xz_m'])==8
    assert q['quantities']['steel_net_mass_kg']==pytest.approx(5652)
    assert q['quantities']['deck_concrete_mass_kg']==18000
    assert q['quantities']['steel_total_surface_area_m2']==pytest.approx(74.544)
    assert q['quantities']['steel_exposed_area_m2']==pytest.approx(73.744)
    assert q['handling']['actual_cut_pieces']==12
    assert q['handling']['two_web_module_hole_pierces']==0
    assert q['handling']['two_web_module_contour_starts_hypothesis']==12
    assert [p['mass_kg'] for p in q['quantities']['nominal_part_quantities']]==pytest.approx([18000,2826,2826])
    assert q['handling']['two_web_splice_ligament_m']==pytest.approx(3.6)
    assert q['handling']['two_web_module_cut_perimeter_m']==pytest.approx(134.4)
    assert q['quantities']['nominal_CG_m'][0:2]==pytest.approx([10,0])
    assert q['quantities']['nominal_CG_m'][2]==pytest.approx((18000*-.09+5652*-.78)/23652)


def test_no_splice_is_invented_where_material_starts_at_module_boundary():
    q=g.quantities(g.realize([[0,1,1,1]]))
    assert q['handling']['splices'][0]['two_web_weld_seam_m']==0
    assert q['handling']['two_web_splice_ligament_m']==pytest.approx(4.8)


def test_corner_contact_and_disconnected_stock_remain_actual_failed_geometry():
    c=g.realize([[1,0],[0,1]]);p=c['web_geometry']
    assert p['finite_edge_components']==2 and p['corner_only_contacts']==1
    assert not p['one_finite_edge_component'] and p['area_m2']==12
    assert p['topology_screen']=='disconnected-or-corner-contact'
    assert g.quantities(c)['quantities']['steel_net_mass_kg']>0


def test_density_is_an_evaluation_and_unknown_reserve_cg_is_not_fabricated():
    c=g.realize([[1]]);a=g.quantities(c);b=g.quantities(c,dict(steel=8000.,concrete=2400.))
    assert a['candidate_id']==b['candidate_id']==c['candidate_id'] and a['evaluation_id']!=b['evaluation_id']
    assert a['reserve_CG_and_inertia_unknown'] and a['complete_installed_mass_kg'] is None
    assert all(v[0]>0 for v in a['reserve_mass_kg'].values())
    assert all(c[k] is False and a[k] is False for k in g.FLAGS)


def test_deck_only_inertia_is_exact_prism_and_empty_web_is_not_pruned_into_success():
    c=g.realize([[0]]);q=g.quantities(c);I=q['quantities']['nominal_inertia_tensor_kg_m2']
    assert c['web_geometry']['topology_screen']=='empty'
    assert I[0][0]==pytest.approx(18000*(2**2+.18**2)/12)
    assert I[1][1]==pytest.approx(18000*(20**2+.18**2)/12)
    assert I[0][1]==I[0][2]==I[1][2]==0


@pytest.mark.parametrize('mask',[[],[[1],[1,0]],[[.5]],[[2]],[[float('nan')]]])
def test_invalid_masks_rejected(mask):
    with pytest.raises(ValueError):g.realize(mask)


def test_resealed_geometry_tampering_cannot_supply_false_quantities():
    c=g.realize([[1]]);c['web_geometry']['area_m2']=1;c.pop('geometry_id');c['geometry_id']=identity(c)
    with pytest.raises(ValueError,match='union differs'):g.quantities(c)


def test_module_and_density_computational_domains_reject_unbounded_or_underflow_inputs():
    c=g.realize([[1]])
    with pytest.raises(ValueError):g.quantities(c,module_length_m=1e-100)
    with pytest.raises(ValueError):g.quantities(c,dict(steel=1e300,concrete=2500.))
    with pytest.raises(ValueError):g.quantities(c,dict(steel=7850.,concrete=1e-300))
