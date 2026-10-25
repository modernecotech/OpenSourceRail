from copy import deepcopy
import math
from pathlib import Path

import numpy as np
import pytest

from engineering.halbach_scaling import candidates as c
from engineering.passive_suspension import fields

MAIN = c.ROOT


def test_counted_stock_and_fixed_facing_close_for_all_36_proposals():
    values = c.candidates(MAIN)
    assert len(values) == len({q['physical_id'] for q in values}) == 36
    assert values[0]['physical_id'] == c.PARENT_ID
    for q in values:
        c.validate(q, MAIN)
        train = [p for p in q['stock_parts'] if p['group'] == 'train']
        guideway = [p for p in q['stock_parts'] if p['group'] == 'guideway']
        assert len(guideway) == 1 and guideway[0]['material'] == 'steel'
        assert guideway[0]['size_m'] == [1., .5, .035]
        assert q['stock']['train_known_mass_kg_per_module'] == pytest.approx(math.fsum(p['volume_m3']*p['density_kg_m3'] for p in train))
        assert q['stock']['magnet_volume_m3_per_module'] == pytest.approx(q['parameters']['magnet_volume_m3'])
        assert q['packing']['modules_per_car'] == 24
        assert q['packing']['physical_module_envelope_x_m'] < 17/12
        assert q['installed_mass_kg_per_car'] is None and q['physical_accepted'] is False
        assert all(p['group'] == 'train' for p in q['stock_parts'] if p['material'] == q['grade_id'])
        # Exact independent AABB checks: all PM/copper/backing/yoke stock is
        # disjoint. Merely touching adjacent magnet blocks is allowed.
        low = np.array([p['at_m'] for p in train]); high = low+np.array([p['size_m'] for p in train])
        for start in range(0, len(train), 64):
            overlap = np.all(np.minimum(high[start:start+64,None,:],high[None,:,:])-np.maximum(low[start:start+64,None,:],low[None,:,:])>1e-10,axis=2)
            for j in range(len(overlap)):overlap[j,start+j] = False
            assert not overlap.any(),q['recipe_id']


def test_old_fill_failure_is_retained_and_new_coils_have_counted_lower_fill():
    values = c.candidates(MAIN)
    assert max(values[0]['winding_definition']['copper_fill_by_circuit'].values()) > .55
    for q in values[1:]:
        assert max(q['winding_definition']['copper_fill_by_circuit'].values()) <= .55
        assert q['parameters']['conductor_insulation_m'] == .0004
        assert q['winding_definition']['insulation_mass_kg'] is None
        for coil in q['circuits']:
            copper = [p for p in q['stock_parts'] if p['id'].startswith(coil['id']+'/')]
            assert len(copper) == 4*coil['turns']
            assert coil['copper_mass_kg'] == pytest.approx(math.fsum(p['mass_kg'] for p in copper))
            assert coil['resistance_20c_ohm'] == pytest.approx(1.724e-8*coil['conductor_length_m']/coil['conductor_area_m2'])


def test_differential_pm_phase_slot_and_winding_polarity_are_physical():
    for q in c.candidates(MAIN):
        if q['winding_definition']['layout'] != 'differential':continue
        pm = [r for r in q['regions'] if r['material'] == q['grade_id']]
        assert all(r['Br_z_T'] > 0 for r in pm[:4])
        assert all(r['Br_z_T'] < 0 for r in pm[4:])
        assert pm[3]['bounds_yz_m'][1] == pytest.approx(-.025)
        assert pm[4]['bounds_yz_m'][0] == pytest.approx(.025)
        assert [p['signed_window_turns'] for p in q['circuits']] == [[60,-60],[-60,60]]
        geometry = c.field_geometry(q, MAIN)
        rows,_,point = fields._prepare(geometry,.012,0.,0.,{k:15. for k in q['winding_definition']['common_current_connection']},80.)
        assert point['currents_A'] == {k:15. for k in q['winding_definition']['common_current_connection']}
        assert abs(sum(r['J']*r['area'] for r in rows)) < 1e-9
        assert q['free_air_seed_80C_T'] is None


@pytest.mark.parametrize('key',['mass','material','stock','interface','release'])
def test_even_rehashed_bundle_changes_are_refused(key):
    q=c.candidates(MAIN)[1]
    if key=='mass':q['stock']['train_known_mass_kg_per_module']=0.
    elif key=='material':q['materials'][q['grade_id']]['br_20c_t']=2.
    elif key=='stock':q['stock_parts'][0]['size_m'][0]=.5
    elif key=='interface':q['interface']['aw3_payload_kg_per_car']=0.
    else:q['physical_accepted']=True
    q.pop('bundle_sha256');q['bundle_sha256']=c.identity(q)
    with pytest.raises(ValueError,match='unsupported or modified'):c.validate(q,MAIN)


def test_rotations_and_free_air_seed_have_independent_limits():
    for segments in (4,8,16):
        directions=np.array(c.rotating_directions(segments,2))
        assert np.allclose(np.linalg.norm(directions,axis=1),1.)
        assert np.linalg.norm(directions.sum(axis=0)) < 1e-12
    args=dict(br_T=1.17,thickness_m=.05,width_m=.4,gap_m=.012,periods=1)
    assert c.free_air_seed_T(**args,segments=16)>c.free_air_seed_T(**args,segments=8)
    assert c.free_air_seed_T(**dict(args,gap_m=.024),segments=16)<c.free_air_seed_T(**args,segments=16)
    large=c.free_air_seed_T(**dict(args,thickness_m=100.,gap_m=0.),segments=16)
    assert large == pytest.approx(args['br_T']*math.sin(math.pi/16)/(math.pi/16))
