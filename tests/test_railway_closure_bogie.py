"""Detailed running-gear revision must propagate without overlapping allowances."""
from copy import deepcopy
from math import fsum
import pytest
from engineering.powered_bogie.design import parent,build
from engineering.railway_closure.installed import integrate,axle_packet
from engineering.railway_closure import ROOT
from engineering.station_rail.common import identity

@pytest.fixture(scope='module')
def bodies():
    old=parent();return old,build(old)

def test_revised_drive_mass_and_first_moment_replace_one_allowance(bodies):
    old,child=bodies;before=integrate(old);after=integrate(child)
    p=child['BOP_partition'];by={r['name']:r for r in before['load_cases']}
    for r in after['load_cases']:
        case=r['name'].split('-')[-1]
        expected=child['change_set']['mass_delta_kg'][case]-p['explicit_parts_already_in_body_kg'][case]
        assert r['train_mass_kg']-by[r['name']]['train_mass_kg']==pytest.approx(expected)
        assert abs(r['force_residual_N'])<1e-7
        assert abs(r['moment_residual_Nm'])<1e-6
        assert r['added_known_drive_kg']==9552.
        assert r['added_drive_reserve_kg']==pytest.approx(p['remaining_unknown_external_reserve_kg'][case])
        assert all(r['inertia_about_CG_kg_m2'][a][a]>0 for a in range(3))
    assert after['vehicle_candidate_id']==child['candidate_id']
    assert axle_packet(after)['mass_evaluation_id']==after['evaluation_id']
    assert after['packaging_screen'].startswith('hold:')
    assert after['physical_accepted'] is False

def test_resealed_wrong_partition_and_drive_ownership_are_rejected(bodies):
    for mutate in (lambda b:b['BOP_partition']['remaining_unknown_external_reserve_kg'].__setitem__('base',4000.),
                   lambda b:b['external_drive_placements'][0].__setitem__('body_BOM_contains_mass',True)):
        bad=deepcopy(bodies[1]);mutate(bad)
        bad.pop('evaluation_id');bad['evaluation_id']=identity(bad)
        with pytest.raises(ValueError):integrate(bad)

def test_conventional_child_is_a_new_candidate_and_no_store_is_separate(bodies):
    child=bodies[1];yes=integrate(child);no=integrate(child,with_recovery=False)
    assert yes['candidate_id']!=no['candidate_id']
    for y,n in zip(yes['load_cases'],no['load_cases']):
        assert y['train_mass_kg']-n['train_mass_kg']==pytest.approx(y['added_capture_interface_kg'])
