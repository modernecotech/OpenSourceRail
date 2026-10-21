"""Geometry/material and independent PDE controls; no physical release assertions."""
import math
from pathlib import Path
import sys
import numpy as np
import pytest
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT))
from engineering.ferrite_maglev import geometry,field


def test_native_seed_matches_array_stations_and_explicit_full_pm_budget():
    r=geometry.interface()
    assert len(r['modules'])==24 and len(r['ferrite_block_inventory'])==4560
    assert sum(m['ferrite_mass_kg'] for m in r['modules'])==2826
    assert sum(r['magnet_budget'][k] for k in ['lift_modelled_kg','guidance_propulsion_reserved_unmodelled_kg'])==3000
    assert r['whole_vehicle_mass_kg'] is None
    assert r['clearances']['bolt_head_to_face_m']==pytest.approx(.008)
    assert geometry.interface('flat-retainer')['clearances']['bolt_head_to_face_m']==pytest.approx(.002)
    assert r['clearances']['full_error_budget_accepted'] is False
    assert len(set(p['id'] for p in r['parts']))==len(r['parts'])


def test_box_beam_material_regions_do_not_count_void_as_concrete():
    p=geometry.beam_parts('x',25)
    concrete=sum(geometry.volume(v) for v in p if v['material']=='concrete')
    assert concrete==pytest.approx((.8*1.8-.6*1.5)*25+2*.4*.6*1.5)
    rail=sum(geometry.volume(v) for v in p if v['role']=='magnetic-rail')
    assert rail==pytest.approx(2*10*2.49*.96*.02)
    assert geometry.civil_bay()['foundation_selected'] is False


def test_pde_grid_refinement_is_second_order_against_analytic_sine():
    r=field.manufactured_controls()
    assert r['second_order_control']
    assert all(3.8<v<4.2 for v in r['error_reduction_ratios'])
    assert all(v['linear_residual']<1e-10 for v in r['refinements'])


def test_coupon_force_is_on_iron_and_has_no_vehicle_capacity_credit():
    r=field.coupon(count=61)
    assert r['net_free_current_a']==pytest.approx(0,abs=1e-12)
    assert all(v[1]<0 for v in r['iron_force_contours_n_per_m'])
    assert all(abs(v[0])<1e-8 for v in r['iron_force_contours_n_per_m'])
    assert r['force_contour_relative_difference']<.1
    assert r['vehicle_lift_capacity_n'] is None and r['magnetic_force_map_validated'] is False


def test_hot_magnet_and_larger_gap_do_not_gain_free_force():
    cold=field.coupon(count=61);hot=field.coupon(count=61,temperature_c=80)
    far=field.coupon(count=61,gap_m=.014)
    force=lambda r:abs(r['iron_force_contours_n_per_m'][0][1])
    assert force(hot)<force(cold) and force(far)<force(cold)


@pytest.mark.parametrize('count,gap',[(20,.008),(81,0),(81,float('nan'))])
def test_invalid_grid_or_gap_is_rejected(count,gap):
    with pytest.raises(ValueError):field.coupon(count=count,gap_m=gap)


def test_retained_native_geometry_reopens_exact_revision_and_mass_ledger():
    import gzip,json
    folder=ROOT/'docs/design-engine/ferrite-maglev/native'
    manifest=geometry.verify_native(folder)
    assert len(manifest['files_sha256'])==17
    for name,definition in [('interface',geometry.interface()),('civil-bay',geometry.civil_bay())]:
        receipt=json.loads((folder/name/'native-cad.json').read_text())
        mesh=json.loads(gzip.decompress((folder/name/'native-mesh.json.gz').read_bytes()))
        assert receipt['fcstd_reopened'] and receipt['step_reopened']
        assert {p['id'] for p in mesh['parts']}=={p['id'] for p in definition['parts']}
        actual={p['id']:p for p in mesh['parts']}
        mass=sum(actual[p['id']]['volume_m3']*geometry.MATERIALS[p['material']] for p in definition['parts'])
        assert mass==pytest.approx(definition['modelled_material_mass_kg'],rel=1e-8)
        assert not definition['design_complete'] and not definition['manufacturing_release']


def test_native_packet_rejects_changed_geometry_and_unlisted_payload(tmp_path):
    import shutil
    source=ROOT/'docs/design-engine/ferrite-maglev/native';folder=tmp_path/'native'
    shutil.copytree(source,folder)
    (folder/'interface/definition.json').write_text('{}')
    with pytest.raises(ValueError,match='differs'):geometry.verify_native(folder)
    shutil.copy2(source/'interface/definition.json',folder/'interface/definition.json')
    (folder/'unexpected.txt').write_text('unlisted')
    with pytest.raises(ValueError,match='inventory'):geometry.verify_native(folder)
