"""Independent staged-motion, storage, load and scoped-cost controls."""
from copy import deepcopy
import json
import math
import os

import pytest

from engineering.station_rail import ROOT
from engineering.station_rail.common import digest, encoded, identity
from engineering.station_energy import arrestor as model, arrestor_costs as costs
from engineering.station_energy import arrestor_examples as examples


@pytest.fixture
def kernel():
    if not (ROOT/'build/station-energy-target/release/osr-arrestor.receipt.json').exists():
        if os.environ.get('OSR_TEST_STATION_ARRESTOR') == '1':
            pytest.fail('Explicit arrestor-build is required')
        pytest.skip('Run python -m engineering.station_energy arrestor-build')


def evaluate(case):
    return model.calculate(dict(schema=model.SCHEMA, cases=[case]))[0]['cases'][0]


def test_generation_is_bounded_diverse_and_has_no_fixed_cruise_selection():
    request = examples.request()
    assert len(request['cases']) == 880
    assert len({c['id'] for c in request['cases']}) == 880
    assert {round(c['booster']['target_speed_m_s']*3.6) for c in request['cases']} == {40, 50, 60, 72}
    assert {c['storage']['design']['kind'] for c in request['cases']} == {'elastic','hydraulic','flywheel'}
    assert {c['handover'] for c in request['cases']} == {'continuous-total-force','independent-stage-pulses'}
    assert sum(c['capture_entry_speed_m_s'] == 0 for c in request['cases']) == 4


def test_stage_count_does_not_create_energy_and_handover_changes_geometry(kernel):
    case = examples.reference_case()
    continuous = evaluate(case)
    case['handover'] = 'independent-stage-pulses'
    pulses = evaluate(case)
    assert continuous['capture']['total_time_s'] == pytest.approx(14.1)
    assert continuous['capture']['total_distance_m'] == pytest.approx(70.5)
    assert pulses['capture']['total_time_s'] == pytest.approx(20.5)
    assert pulses['capture']['total_distance_m'] == pytest.approx(102.5)
    for r in (continuous, pulses):
        assert sum(s['kinetic_drop_j'] for s in r['capture']['stages']) == pytest.approx(8e6)
        assert r['storage']['delivered_j'] == pytest.approx(5.6e6)
        assert r['launch']['exit_speed_m_s'] == pytest.approx(math.sqrt(70.))
        assert r['launch']['distance_m'] == pytest.approx(43.36660026534076)
        assert r['launch']['required_peak_force_n'] == pytest.approx(160000.)
        assert abs(r['energy_residual_j']) < 1e-6
        assert r['necessary_bounds'] == 'unknown'
        assert all(r[k] is False for k in model.FLAGS)
        assert r['booster']['coupler_tension_n'] == []


def test_force_travel_ratio_conserves_work_and_does_not_reduce_store_mass(kernel):
    case = examples.reference_case()
    a = evaluate(case)
    for stage in case['stages']:
        stage['displacement_ratio'] *= 2
    b = evaluate(case)
    assert b['sizing']['active_mass_kg'] == a['sizing']['active_mass_kg']
    assert b['storage']['delivered_j'] == a['storage']['delivered_j']
    for old, new in zip(a['capture']['stages'], b['capture']['stages'], strict=True):
        assert new['store_travel_m'] == pytest.approx(old['store_travel_m']/2)
        assert new['store_force_upper_bound_n'] == pytest.approx(old['store_force_upper_bound_n']*2)


def test_rear_front_and_distributed_load_signs(kernel):
    case = examples.reference_case()
    rear = evaluate(case)
    assert rear['launch']['coupler_tension_n'] == pytest.approx([-160000*i/6 for i in range(1,6)])
    case['launch']['force_fractions'] = [1.,0.,0.,0.,0.,0.]
    front = evaluate(case)
    assert front['launch']['coupler_tension_n'] == pytest.approx([160000*(6-i)/6 for i in range(1,6)])
    case['launch']['force_fractions'] = list(case['launch']['mass_fractions'])
    distributed = evaluate(case)
    assert distributed['launch']['coupler_tension_n'] == pytest.approx([0.]*5, abs=1e-8)
    assert distributed['launch']['required_peak_force_n'] == pytest.approx(160000.)


@pytest.mark.parametrize('capacity,mass', ((2e6,14285.714285714286),(8e6,57142.857142857145),(32e6,228571.42857142858)))
def test_literature_density_is_a_capacity_control_not_installed_mass(kernel, capacity, mass):
    case = examples.reference_case()
    case['storage']['capacity_j'] = capacity
    r = evaluate(case)
    assert r['sizing']['active_mass_kg'] == pytest.approx(mass)
    assert r['sizing']['complete_installed_mass'] is False


@pytest.mark.parametrize('exponent,work', ((1.,1376294.3611198906),
    (1.0000000001,1376294.360935024),(1.4,891916.5128415835)))
def test_polytropic_work_with_return_pressure_and_log_limit(kernel, exponent, work):
    case = examples.reference_case()
    case['storage']['design'] = dict(kind='hydraulic',precharge_pressure_pa=10e6,
        min_pressure_pa=10e6,max_pressure_pa=20e6,return_pressure_pa=.1e6,
        polytropic_exponent=exponent,vessel_mass_kg_per_m3=3500.,packing_fraction=.5)
    r = evaluate(case)
    precharge_volume = .1*2**(1/exponent)
    assert r['sizing']['specific_work_j_m3'] == pytest.approx(work/precharge_volume, rel=1e-9)


def test_unsupported_grade_is_retained_unknown_without_level_track_recovery(kernel):
    case = examples.reference_case()
    case['grade_fraction'] = .02
    r = evaluate(case)
    assert r['capture']['stages'] is None
    assert r['storage']['unresolved_capture_j'] == pytest.approx(8e6)
    assert r['storage']['accepted_j'] == 0.
    assert r['physical_accepted'] is False


def test_no_departure_authorisation_does_not_release_energy(kernel):
    case = examples.reference_case()
    case['storage']['departure_authorized'] = False
    r = evaluate(case)
    assert r['storage']['delivered_j'] == 0.
    assert r['storage']['end_j'] == pytest.approx(5.6e6)
    assert r['launch'] is None and r['movement_authority'] is False


def test_repeated_store_closes_and_does_not_reset_initial_charge(kernel):
    rules = examples.policy()
    case = examples.case(rules['stores'][0],20.,60.,10.,'continuous-total-force','rear',rules)
    value, _ = model.physics(dict(schema=model.SCHEMA,cases=[case]))
    assert len(value['cycles']) == 2
    assert value['cyclic_storage_closed'] == [True]
    for previous, current in zip(value['cycles'], value['cycles'][1:]):
        transition = previous['conditioning_after'][0]
        assert transition['initial_j'] == previous['result']['cases'][0]['storage']['end_j']
        assert current['request']['cases'][0]['storage']['initial_j'] == transition['end_j']
        assert abs(transition['balance_residual_j']) < .0001
    r = value['cycles'][-1]['result']['cases'][0]
    assert r['storage']['overflow_j'] > 0
    assert r['storage']['delivered_j'] == pytest.approx(8e6)
    assert abs(r['energy_residual_j']) < 1e-6


def test_slow_positive_storage_gain_has_an_accounted_warmup_and_native_terminal_check(kernel):
    case = next(c for c in examples.request()['cases'] if c['id']=='G3-flywheel-full-release-c20-v60')
    value, _ = model.physics(dict(schema=model.SCHEMA,cases=[case]))
    assert len(value['cycles']) == 2
    first, final = value['cycles']
    ledger = first['conditioning_after'][0]
    # Independent scalar recurrence, not the closed-form implementation.
    r = first['result']['cases'][0]['storage']
    state = r['end_j']; overflow = 0.
    captured = .5*160000*20**2*.7
    withdrawn = .5*160000*(60/3.6)**2
    for _ in range(ledger['nominal_events']):
        overflow += max(0., state+captured-case['storage']['capacity_j'])
        state = min(case['storage']['capacity_j'],state+captured)-3000.-withdrawn
    assert ledger['nominal_events'] > model.MAX_CYCLES
    assert ledger['numerical_solver_events'] == 0
    assert state == pytest.approx(ledger['end_j'], abs=1e-6)
    assert overflow == pytest.approx(ledger['overflow_j'], abs=1e-6)
    assert ledger['credited_capture_j'] == pytest.approx(ledger['nominal_events']*32e6)
    assert ledger['delivered_j'] == pytest.approx(ledger['nominal_events']*withdrawn)
    assert ledger['initial_j']+ledger['credited_capture_j'] == pytest.approx(sum(ledger[k] for k in
        ('capture_conversion_loss_j','store_conversion_loss_j','overflow_j','standing_loss_j','withdrawn_j','end_j')))
    native = final['result']['cases'][0]['storage']
    assert native['initial_j'] == ledger['end_j']
    assert native['end_j'] == pytest.approx(native['initial_j'], abs=.0001)
    assert value['cyclic_storage_closed'] == [True]
    assert all(final['result']['cases'][0][k] is False for k in model.FLAGS)


def test_conditioning_does_not_repair_failed_or_held_physics(kernel):
    case = next(c for c in examples.request()['cases'] if c['id']=='G3-flywheel-full-release-c20-v60')
    for change in ({'departure_authorized':False}, {'isolated_during_dwell':False}):
        altered = deepcopy(case); altered['storage'].update(change)
        result = evaluate(altered)
        assert model._conditioning(altered,result) is None
    failed = deepcopy(case); failed['stages'][0]['available_stroke_m'] = 0.
    assert model._conditioning(failed,evaluate(failed)) is None


def test_cost_scope_accounting_depth_and_paid_shift_time(kernel):
    case = examples.reference_case(); result = evaluate(case)
    p, sources = costs.prepare()
    a = costs.estimate(case,result,cyclic_storage_closed=True,context=(p,sources))
    p2 = deepcopy(p); p2['geometry']['foundation_allowance_depth_m'] *= 2
    b = costs.estimate(case,result,cyclic_storage_closed=True,context=(p2,sources))
    minimum = p['geometry']['minimum_foundation_m3']
    assert b['foundation_allowance_m3']-minimum == pytest.approx(2*(a['foundation_allowance_m3']-minimum))
    assert a['foundation_reference_area_m2']*p['geometry']['foundation_allowance_depth_m']+minimum == pytest.approx(a['foundation_allowance_m3'])
    for scenario in costs.CASES:
        row = a['costs'][scenario]
        assert sum(c['factory_cost_usd'][scenario] for c in a['components']) == pytest.approx(row['factory_usd'])
        assert a['production_days_at_one_position'][scenario] == pytest.approx(a['production_labour_h'][scenario]/16)
        assert row['installed_usd'] == pytest.approx(sum(row[k] for k in ('factory_usd','tooling_allocation_usd','delivery_usd','erection_usd','civil_reserve_usd','installation_labour_usd')))
    assert a['costs']['base']['renewal_pv_usd'] > 0
    assert a['fleet_and_corridor_total_usd'] is None
    assert a['complete_installed_mass'] is False


def test_stress_mode_does_not_silently_choose_material_prices(kernel):
    case = examples.reference_case()
    case['storage']['design'] = dict(kind='elastic',stress_mode='axial',density_kg_m3=7850.,
        modulus_pa=200e9,allowable_stress_pa=500e6,utilisation=.4,packing_fraction=.2)
    r = evaluate(case)
    unknown = costs.estimate(case,r,cyclic_storage_closed=True)
    assert unknown['estimate_complete'] is False and unknown['cost'] is None
    p, sources = costs.prepare()
    p['material_routes'][costs.design_id(case['storage']['design'])] = dict(
        storage_design=case['storage']['design'],material_family='spring-steel')
    explicit = costs.estimate(case,r,cyclic_storage_closed=True,context=(p,sources))
    assert explicit['estimate_complete'] is True
    assert any(row['component']=='active-steel-spring-material' for row in explicit['components'])


def test_no_capture_does_not_buy_or_replace_an_active_store(kernel):
    case = next(c for c in examples.request()['cases'] if c['id']=='no-capture-v60')
    result = evaluate(case)
    estimate = costs.estimate(case,result,cyclic_storage_closed=True)
    assert estimate['active_storage_element_mass_kg'] == 0.
    assert estimate['costs']['base']['renewal_pv_usd'] == 0.
    assert not any(row['component'].startswith('active-') for row in estimate['components'])


def test_no_booster_is_an_explicit_local_station_alternative(kernel):
    case = next(c for c in examples.request()['cases'] if c['id']=='G3-flywheel-full-release-c20-v60')
    r = evaluate(case)
    assert r['launch']['exit_speed_m_s'] == pytest.approx(60/3.6)
    assert r['booster']['distance_m'] == 0.
    assert r['booster']['source_energy_j'] == 0.
    assert r['physical_accepted'] is False
    estimate = costs.estimate(case,r,cyclic_storage_closed=True)
    assert not any(row['component'].startswith('remaining-booster-') for row in estimate['components'])


def test_distributed_launch_counts_all_mechanisms_and_launch_ropes(kernel):
    case = examples.reference_case()
    rear = evaluate(case)
    rear_cost = costs.estimate(case,rear,cyclic_storage_closed=True)
    case['launch']['force_fractions'] = list(case['launch']['mass_fractions'])
    distributed = evaluate(case)
    distributed_cost = costs.estimate(case,distributed,cyclic_storage_closed=True)
    assert rear_cost['launcher_force_points'] == 1
    assert distributed_cost['launcher_force_points'] == 6
    key = 'overrunning-clutches-release-locks-and-return-drives'
    unit_count = lambda c: next(x['quantity'] for x in c['components'] if x['component']==key)
    assert unit_count(distributed_cost)-unit_count(rear_cost) == 5
    extended = deepcopy(rear); extended['launch']['distance_m'] *= 2
    extended_cost = costs.estimate(examples.reference_case(),extended,cyclic_storage_closed=True)
    ropes = lambda c: next(x['quantity'] for x in c['components'] if x['component']=='train-and-store-side-rope-stock')
    assert ropes(extended_cost) > ropes(rear_cost)


def test_pricing_reuses_physics_and_strict_verification_replays(kernel, tmp_path, monkeypatch):
    request = dict(schema=model.SCHEMA,cases=[examples.reference_case()])
    original = tmp_path/'original'; repriced = tmp_path/'repriced'
    first = model.run(original, request)
    assert model.verify(original) == first
    original_calculate = model.calculate
    monkeypatch.setattr(model,'calculate',lambda *args,**kwargs: pytest.fail('Repricing must not run the motion evaluator'))
    second = model.reprice(repriced, original)
    assert second['physics_evaluation_id'] == first['physics_evaluation_id']
    assert json.loads((repriced/'performance.json').read_bytes())['rust_invocations'] == 0
    monkeypatch.setattr(model,'calculate',original_calculate)
    assert model.verify(repriced) == second
    value = json.loads((repriced/'physics.json').read_bytes())
    value['cycles'][-1]['result']['cases'][0]['launch']['distance_m'] = 1.
    value['physics_evaluation_id'] = identity({k:v for k,v in value.items() if k!='physics_evaluation_id'})
    (repriced/'physics.json').write_bytes(encoded(value))
    second['physics_evaluation_id'] = value['physics_evaluation_id']
    second['files_sha256']['physics.json'] = digest(repriced/'physics.json')
    second['manifest_id'] = identity({k:v for k,v in second.items() if k!='manifest_id'})
    (repriced/'manifest.json').write_bytes(encoded(second))
    with pytest.raises(ValueError,match='replay differs'):
        model.verify(repriced)


def test_cache_cannot_promote_a_physical_design(kernel, tmp_path):
    request = dict(schema=model.SCHEMA,cases=[examples.reference_case()])
    original = tmp_path/'original'
    manifest = model.run(original,request)
    value = json.loads((original/'physics.json').read_bytes())
    value['cycles'][0]['result']['cases'][0]['physical_accepted'] = True
    value['physics_evaluation_id'] = identity({k:v for k,v in value.items() if k!='physics_evaluation_id'})
    (original/'physics.json').write_bytes(encoded(value))
    manifest['physics_evaluation_id'] = value['physics_evaluation_id']
    manifest['files_sha256']['physics.json'] = digest(original/'physics.json')
    manifest['manifest_id'] = identity({k:v for k,v in manifest.items() if k!='manifest_id'})
    (original/'manifest.json').write_bytes(encoded(manifest))
    with pytest.raises(ValueError,match='cannot grant'):
        model.reprice(tmp_path/'new',original)


@pytest.mark.parametrize('change', ({'grade_fraction': True},{'reset_s': -1.}, {'made_up_force': 1.}))
def test_invalid_schema_and_domain_rejected(kernel, change):
    case = examples.reference_case(); case.update(change)
    with pytest.raises((RuntimeError,ValueError)):
        evaluate(case)
