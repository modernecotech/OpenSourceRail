"""Finite placement controls; contact is never a force map or a journey."""
from itertools import repeat
from math import inf, nan

import pytest

from engineering.design_search.sparse_launch import geometry


SITES = [0., 104.5, 204.5, 304.5, 404.5, 504.5]


@pytest.mark.parametrize('count,length,last,covered,minimum,maximum,best', [
    (3, 10., 210.5, 210.5, 0., 9., 0.),
    (3, 12.5, 213., 213., 0., 9., 0.),
    (3, 20., 220.5, 220.5, 0., 16.5, 0.),
    (6, 10., 510.5, 500., 1.5, 9., .75),
    (6, 12.5, 513., 500., 4., 9., 2.),
    (6, 20., 520.5, 500., 9., 16.5, 5.75),
])
def test_berthed_three_and_six_site_controls(count, length, last, covered, minimum, maximum, best):
    result = geometry(SITES[:count], length)
    assert result['last_contact_advance_m'] == last
    assert result['geometric_covered_m'] == covered
    assert result['min_sum_overlap_m'] == minimum
    assert result['max_sum_overlap_m'] == maximum
    assert result['longest_single_fin_min_m'] == best
    assert result['continuous_contact_over_launch'] is (count == 6)
    assert result['min_active_fins'] == (1 if count == 6 else 0)
    assert result['min_active_sites'] == (1 if count == 6 else 0)
    assert result['max_active_fins'] == result['max_active_sites'] == 2
    assert result['fully_contained_fin_all_positions'] is False
    assert result['site_count'] == count
    assert result['summed_bank_length_m'] == count * length
    assert result['primary_face_count'] == 2 * count
    assert result['primary_face_length_sum_m'] == 2 * count * length


def test_exact_start_and_500m_contact_are_not_six_fully_engaged_cars():
    short, long = geometry(SITES, 10.), geometry(SITES, 20.)
    assert short['start_overlap']['overlap_pairs'] == [
        dict(site_index=0, car_index=5, overlap_m=6., full_fin_contained=False)]
    assert long['start_overlap']['overlap_pairs'] == [
        dict(site_index=0, car_index=5, overlap_m=9., full_fin_contained=True)]
    end = long['breakpoint_records'][-1]
    assert end['nose_advance_m'] == 500.
    assert end['active_sites'] == 1 and end['active_fins'] == 2
    assert end['sum_overlap_m'] == 11.5
    assert end['overlap_pairs'] == [
        dict(site_index=5, car_index=4, overlap_m=3., full_fin_contained=False),
        dict(site_index=5, car_index=5, overlap_m=8.5, full_fin_contained=False)]


@pytest.mark.parametrize('shift', [-1000.25, .1, 1000000.1])
def test_common_coordinate_translation_has_no_physical_or_evaluation_effect(shift):
    original = geometry(SITES, 20.)
    shifted = geometry([value + shift for value in SITES], 20., initial_nose_m=104.5 + shift)
    assert shifted == original


def test_state_and_requested_distance_are_not_new_physical_geometry():
    original = geometry(SITES, 20.)
    moved = geometry(SITES, 20., initial_nose_m=110.)
    shorter = geometry(SITES, 20., launch_distance_m=200.)
    changed = geometry(SITES, 10.)
    assert original['physical_geometry_id'] == moved['physical_geometry_id'] == shorter['physical_geometry_id']
    assert len({r['geometry_evaluation_id'] for r in (original, moved, shorter)}) == 3
    assert changed['physical_geometry_id'] != original['physical_geometry_id']
    assert geometry(reversed(SITES), 20.) == original


def test_missing_standstill_contact_cannot_claim_self_start_or_qualification():
    result = geometry(SITES[:3], 1.)
    assert result['initial_geometric_overlap'] is False
    assert result['start_overlap']['overlap_pairs'] == []
    assert result['future_contact_union_m'][0][0] == 4.
    for key in ('self_start_proven', 'force_map_available', 'force_scaling_per_overlap_available',
                'physical_evidence', 'physical_accepted', 'engineering_accepted',
                'native_dispatch_allowed', 'manufacturing_release', 'operating_release'):
        assert result[key] is False
    for key in ('installed_cost', 'receiving_extent_m', 'available_force_N', 'available_electrical_power_W'):
        assert result[key] is None


def test_banks_entirely_behind_train_have_no_future_contact():
    result = geometry([0.], 5., initial_nose_m=1000.)
    assert result['future_contact_union_m'] == result['required_launch_contact_union_m'] == []
    assert result['last_contact_advance_m'] is None
    assert result['geometric_covered_m'] == result['min_sum_overlap_m'] == 0.


def test_touching_banks_keep_equipment_counts_without_counting_a_fin_twice():
    result = geometry([0., 10.], 10., cars=1, initial_nose_m=13., launch_distance_m=3.)
    end = result['breakpoint_records'][-1]
    assert result['site_count'] == 2
    assert end['active_pairs'] == end['active_sites'] == 2
    assert end['active_fins'] == 1
    assert end['sum_overlap_m'] == 9.
    assert result['fully_contained_fin_all_positions'] is False


def test_complete_fin_containment_is_possible_but_not_a_qualification():
    result = geometry([0.], 100., cars=1, initial_nose_m=20., launch_distance_m=10.)
    assert result['fully_contained_fin_all_positions'] is True
    assert result['longest_single_fin_min_m'] == result['min_sum_overlap_m'] == 9.
    assert result['physical_accepted'] is False and result['force_map_available'] is False


@pytest.mark.parametrize('length', [10., 12.5, 20.])
def test_exact_event_and_envelope_extrema_against_independent_dense_center_formula(length):
    result = geometry(SITES, length)
    sampled = []
    # Independent center-distance overlap construction, including the quarter-
    # metre worst-single-fin handoffs missed by geometry edge events alone.
    for index in range(4001):
        nose = 104.5 + index / 8
        matches = []
        for site_id, site in enumerate(SITES):
            bank_center = site + length / 2
            for car in range(6):
                fin_center = nose - 17.5 * car - 8.5
                separation = abs(bank_center - fin_center)
                if separation >= (length + 9.) / 2:
                    overlap = 0.
                elif separation <= abs(length - 9.) / 2:
                    overlap = min(length, 9.)
                else:
                    overlap = (length + 9.) / 2 - separation
                if overlap > 0:
                    matches.append((site_id, car, overlap))
        sampled.append((sum(row[2] for row in matches),
                        max((row[2] for row in matches), default=0.),
                        len({row[0] for row in matches}), len({row[1] for row in matches})))
    assert min(row[0] for row in sampled) == result['min_sum_overlap_m']
    assert max(row[0] for row in sampled) == result['max_sum_overlap_m']
    assert min(row[1] for row in sampled) == result['longest_single_fin_min_m']
    assert min(row[2] for row in sampled) == result['min_active_sites']
    assert max(row[2] for row in sampled) == result['max_active_sites']
    assert min(row[3] for row in sampled) == result['min_active_fins']
    assert max(row[3] for row in sampled) == result['max_active_fins']


@pytest.mark.parametrize('sites,length,kwargs', [
    ([], 10., {}), ([0., 0.], 10., {}), ([0., 9.], 10., {}),
    ([nan], 10., {}), ([inf], 10., {}), ([0.], 0., {}),
    ([0.], -1., {}), ([0.], nan, {}), ([0.], inf, {}),
    ([0.], True, {}), ([0.], 10., {'cars': 0}),
    ([0.], 10., {'cars': 1.5}), ([0.], 10., {'cars': True}),
    ([0.], 10., {'car_length_m': 0.}), ([0.], 10., {'coupling_gap_m': -.5}),
    ([0.], 10., {'fin_length_m': 0.}), ([0.], 10., {'fin_length_m': 18.}),
    ([0.], 10., {'fin_setback_m': -1.}), ([0.], 10., {'fin_setback_m': 9.}),
    ([0.], 10., {'initial_nose_m': nan}), ([0.], 10., {'launch_distance_m': inf}),
    ([0.], 10., {'launch_distance_m': 0.}), ('123', 10., {}),
    (repeat(0.), 10., {}),
])
def test_invalid_or_unbounded_geometry_requests_fail_closed(sites, length, kwargs):
    with pytest.raises(ValueError):
        geometry(sites, length, **kwargs)
