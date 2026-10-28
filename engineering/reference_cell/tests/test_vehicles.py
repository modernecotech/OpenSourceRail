"""Equipped geometry hypotheses stay distinct from installed acceptance."""
from copy import deepcopy
from collections import Counter

import pytest

from engineering.reference_cell import vehicles as v
from engineering.component_registry import validate_registry


@pytest.fixture(scope='module')
def candidates():
    return {name:v.evaluate(name) for name in v.variants()}


def part_occurrences(candidate, prefix):
    registry=candidate['registry']
    definitions={p['physical_definition_id']:p for p in registry['parts']}
    return [(r,definitions[r['part_definition_id']]) for r in registry['occurrences']
        if definitions[r['part_definition_id']]['part_id'].startswith('OSR-'+candidate['vehicle_id']+'-'+prefix.upper())]


def test_five_distinct_physical_constructions_with_one_service_requirement(candidates):
    assert set(candidates)=={'V1','V2','V3','V4','V5'}
    assert len({r['candidate_id'] for r in candidates.values()})==5
    assert len({r['architecture']['load_path_hypothesis'] for r in candidates.values()})==5
    assert all(r['requirements']==v.REQUIREMENTS for r in candidates.values())
    assert all(r['functional_requirements']==list(v.FUNCTIONS) for r in candidates.values())


@pytest.mark.parametrize('name',v.variants())
def test_all_functional_categories_are_located_and_bound_without_acceptance(candidates,name):
    result=candidates[name];registry=result['registry']
    validate_registry(registry)
    assert len(registry['occurrences'])==6*result['per_car_occurrences']
    assert all(result['per_car_functional_occurrences'][f]>0 for f in v.FUNCTIONS)
    assert result['installed_functional_categories_represented'] is True
    assert result['mass_complete'] is False
    assert result['complete_installed_vehicle_mass_kg'] is None
    assert result['summary']['complete_nominal_mass_kg'] is None
    assert result['summary']['mass_lower_bound_kg']>0
    assert result['summary']['mass_upper_bound_kg']>result['summary']['mass_lower_bound_kg']
    assert result['summary']['installed_CG_m'] is None
    assert result['summary']['installed_inertia_kg_m2'] is None
    assert all(result[key] is False for key in v.FLAGS)


def test_actual_seats_doors_wheels_brakes_and_services_are_counted(candidates):
    result=candidates['V1']
    # 40 individual seats+two double-place wall benches, repeated six times.
    assert len(part_occurrences(result,'seat-pan'))==240
    assert len(part_occurrences(result,'two-place-wall-bench'))==12
    assert len(part_occurrences(result,'door-drive-lock-emergency-set'))==12
    assert len(part_occurrences(result,'door-leaf-core'))==24
    assert len(part_occurrences(result,'wheel-rim'))==48
    assert len(part_occurrences(result,'axle-bearing'))==48
    assert len(part_occurrences(result,'independent-brake-caliper'))==48
    assert len(part_occurrences(result,'passive-aluminium-fin'))==18
    assert len(part_occurrences(result,'auxiliary-battery-with-BMS'))==6
    assert len(part_occurrences(result,'HVAC-roof-unit'))==12
    assert len(part_occurrences(result,'wheelchair-restraint-and-call'))==12
    assert result['requirements']['powered_bogies']==0
    assert result['requirements']['traction_batteries']==0


def test_shared_equipment_has_identical_geometry_and_mass_bounds_across_bodies(candidates):
    def equipment(result):
        return {name:[(p['geometry'],p['mass']) for _,p in part_occurrences(result,name)]
            for name in ('side-window-module','HVAC-roof-unit','auxiliary-battery-with-BMS',
                         'door-drive-lock-emergency-set','wheel-rim','passive-aluminium-fin')}
    common=equipment(candidates['V1'])
    assert all(equipment(r)==common for r in candidates.values())


def test_canonical_occurrence_frames_match_real_axle_and_hardpoint_offsets(candidates):
    result=candidates['V1']
    assert result['interfaces']['axle_longitudinal_positions_m']==[2.15,3.65,13.35,14.85]
    axles=part_occurrences(result,'axle-')
    axles=[(r,p) for r,p in axles if '-AXLE-' in p['part_id'] and 'BEARING' not in p['part_id']]
    assert len(axles)==24
    actual=sorted(r['transform'][0][3] for r,_ in axles)
    expected=sorted(17.5*car+x for car in range(6) for x in (2.15,3.65,13.35,14.85))
    assert actual==pytest.approx(expected)
    assert len(result['interfaces']['body_secondary_hardpoint_positions_m'])==4
    assert all(r['candidate_id']==result['candidate_id'] for r in result['registry']['occurrences'])


def test_purchased_envelopes_do_not_become_density_derived_filled_solids(candidates):
    result=candidates['V1']
    envelopes=[p for p in result['registry']['parts'] if p['geometry']['kind']=='envelope']
    assert envelopes
    assert all(p['geometry']['net_volume_m3'] is None for p in envelopes)
    assert all(p['mass']['calculated_kg'] is None for p in envelopes)
    assert all(p['material_id'] is None for p in envelopes)
    assert all(p['mass']['upper_bound_kg']>p['mass']['lower_bound_kg']>0 for p in envelopes)
    assert all(p['procurement']['supplier'] is None for p in envelopes)


def test_hardware_adhesive_support_and_manufacturing_scope_are_not_unweighed_allocations(candidates):
    result=candidates['V1']
    for prefix in ('cassette-joint-shaft','cassette-joint-head','cassette-joint-nut',
        'cassette-joint-washer','cassette-seam-adhesive','body-bogie-hardpoint',
        'secondary-hanger','battery-stop-lock-and-restraint','battery-slide-rail'):
        rows=part_occurrences(result,prefix)
        assert rows,prefix
        assert all(p['mass']['lower_bound_kg']>0 for _,p in rows)
    for part in result['registry']['parts']:
        m=part['manufacturing']
        assert m['method']
        if part['geometry']['kind']!='envelope':
            assert m['blank_volume_m3']>part['geometry']['net_volume_m3']>0
        assert part['cost']['supplier_quote_id'] is None


def test_wiring_is_located_as_finite_car_length_segments(candidates):
    result=candidates['V1']
    for prefix,length_per_car in (('LV-power-conductor-',30.),('door-HVAC-conductor-',120.),('control-data-conductor-',240.)):
        rows=part_occurrences(result,prefix)
        conductors=[(r,p) for r,p in rows if p['geometry']['kind']=='cylinder']
        assert sum(p['geometry']['dimensions_m']['length'] for _,p in conductors)==pytest.approx(6*length_per_car)
        assert all(p['geometry']['dimensions_m']['length']<=17. for _,p in conductors)


def test_finite_access_and_service_sweeps_report_obstructions_without_accepting_installation(candidates):
    result=candidates['V1'];records=result['assembly_access']
    assert records
    assert any(r['function']=='doors' and r['method']=='plug-slide-service-sweep' for r in records)
    assert any(r['function']=='HVAC' and r['lifting_device']=='crane-and-spreader' for r in records)
    assert any(r['sampled_broad_phase_intersections'] for r in records)
    for row in records:
        assert row['motion']['sample_count']==9
        assert row['clearance_and_lifting_verified'] is False
        assert row['continuous_clearance_proved'] is False
        assert all(row['swept_AABB_m']['min'][i]<row['swept_AABB_m']['max'][i] for i in range(3))


def test_resealed_occurrence_mixing_and_part_mass_mutation_are_rejected(candidates):
    registry=deepcopy(candidates['V1']['registry'])
    registry['occurrences'][0]['candidate_id']=candidates['V2']['candidate_id']
    with pytest.raises(ValueError):validate_registry(registry)
    registry=deepcopy(candidates['V1']['registry'])
    registry['parts'][0]['mass']['calculated_kg']*=.1
    with pytest.raises(ValueError):validate_registry(registry)


def test_unknown_vehicle_is_not_silently_substituted():
    with pytest.raises(ValueError):v.evaluate('V6')


def test_component_mass_bounds_and_calculated_subset_inertia_reconcile(candidates):
    for result in candidates.values():
        car=result['per_car_mass_properties'];train=result['train_mass_properties'];coverage=result['summary']
        assert 6*car['mass_lower_bound_kg']==pytest.approx(train['mass_lower_bound_kg'])
        assert 6*car['mass_upper_bound_kg']==pytest.approx(train['mass_upper_bound_kg'])
        assert train['mass_lower_bound_kg']==pytest.approx(coverage['mass_lower_bound_kg'])
        assert train['mass_upper_bound_kg']==pytest.approx(coverage['mass_upper_bound_kg'])
        assert train['calculated_net_stock_mass_kg']==pytest.approx(coverage['known_calculated_mass_kg'])
        assert train['calculated_subset_CG_m'][0]-car['calculated_subset_CG_m'][0]==pytest.approx(43.75)
        assert all(car['all_item_CG_bounds_m'][i][0]<car['all_item_CG_bounds_m'][i][1] for i in range(3))
        assert all(car['calculated_subset_uniform_inertia_about_its_CG_kg_m2'][i][i]>0 for i in range(3))
        assert car['installed_CG_m'] is None


def test_nominal_couplers_and_gangways_bridge_the_actual_intercar_gap(candidates):
    result=candidates['V1']
    for prefix in ('coupler-drawgear','gangway-bellows-and-retention'):
        rows=part_occurrences(result,prefix)
        first=[(r,p) for r,p in rows if r['occurrence_id'].startswith('car-1/')]
        second=[(r,p) for r,p in rows if r['occurrence_id'].startswith('car-2/')]
        rear=max(first,key=lambda item:item[0]['transform'][0][3])
        front=min(second,key=lambda item:item[0]['transform'][0][3])
        rear_face=rear[0]['transform'][0][3]+rear[1]['geometry']['dimensions_m'][0]/2
        front_face=front[0]['transform'][0][3]-front[1]['geometry']['dimensions_m'][0]/2
        assert rear_face==pytest.approx(17.25)
        assert front_face==pytest.approx(17.25)
    # Central 1.2m gangway aperture is not filled by the nominal end glazing.
    assert all(abs(r['transform'][1][3])-p['geometry']['dimensions_m'][1]/2>.60
        for r,p in part_occurrences(result,'end-escape-glazing'))
