"""Independent longitudinal-load, moving-envelope and release-boundary checks."""
from math import fsum
import pytest
from engineering.reference_cell import civil as c


def test_uniform_solid_load_is_integrated_at_actual_span_overlap_not_smeared():
    left,right=c.rectangular_load(15.,25.,100.,0.,20.)
    assert (left,right)==pytest.approx((6.25,43.75))
    other=c.rectangular_load(15.,25.,100.,20.,40.)
    assert other==pytest.approx((43.75,6.25))
    assert sum((left,right,*other))==pytest.approx(100.)
    assert c.rectangular_load(50.,60.,100.,0.,20.)==(0.,0.)


def test_point_response_and_piecewise_moving_envelope_include_off_midspan_extremum():
    assert c.point_response([(10.,100.)],0.,20.)==pytest.approx({'left_N':50.,'right_N':50.,'maximum_bending_Nm':500.})
    env=c.moving_envelope([(0.,1.),(4.,1.)])
    assert env['maximum_bending_Nm']==pytest.approx(8.1)
    assert env['method']=='piecewise-quadratic moving-point-load extrema'
    # Placing each axle exactly at midspan misses the actual 11m leading-axle extremum.
    sampled=max(c.point_response([(front,1.),(front-4.,1.)],0.,20.)['maximum_bending_Nm'] for front in (0.,4.,10.,14.,20.,24.))
    assert sampled==pytest.approx(8.) and env['maximum_bending_Nm']>sampled


def test_moving_envelope_bounds_dense_quasi_static_reference_for_unequal_axles():
    axles=[(0.,3.),(1.8,2.),(12.,4.),(13.8,1.)]
    exact=c.moving_envelope(axles)
    dense=[c.point_response([(front-o,F) for o,F in axles],0.,20.) for front in [i*.01 for i in range(3381)]]
    assert exact['maximum_bending_Nm']>=max(x['maximum_bending_Nm'] for x in dense)-1e-9
    assert exact['maximum_end_reaction_N']>=max(max(x['left_N'],x['right_N']) for x in dense)-1e-9


@pytest.fixture(scope='module')
def base():return c.generate('a'*64,distance_m=1500.,car_mass_upper_kg=[18000.]*6)


def test_complete_declared_span_stock_and_actual_primary_deadweight_conserve_support_force(base):
    assert base['stations']==2 and base['span_count']*20.==base['counted_interval_m'][1]-base['counted_interval_m'][0]
    assert len(base['primary_loads'])==5*486
    expected=fsum(p['mass_kg']*c.G for p in base['stock'] if p['assembly'].startswith('span/'))+base['known_primary_weight_N']
    assert fsum(base['support_known_superstructure_reactions_N'])==pytest.approx(expected,abs=2e-6)
    assert abs(base['support_force_residual_N'])<1e-5
    assert base['known_primary_weight_N']/c.G==pytest.approx(52407.552)
    assert all(row['qualified_bending_capacity_Nm'] is None for row in base['beam_loads'])
    assert base['complete_installed_mass_kg'] is None and not base['physical_accepted']


def test_relocating_banks_changes_actual_supports_but_preserves_total_plant_mass(base):
    shifted=c.generate('a'*64,distance_m=1500.,bank_starts_m=(-3.,97.375,197.75,298.125,398.5))
    assert shifted['known_primary_weight_N']==pytest.approx(base['known_primary_weight_N'])
    assert shifted['support_known_superstructure_reactions_N']!=base['support_known_superstructure_reactions_N']
    assert fsum(shifted['support_known_superstructure_reactions_N'])==pytest.approx(fsum(base['support_known_superstructure_reactions_N']))
    # Stationside equipment is not averaged over the distant ordinary guideway.
    assert shifted['support_known_superstructure_reactions_N'][40:]==base['support_known_superstructure_reactions_N'][40:]


def test_new_bank_length_has_no_inherited_stock_load_qualification():
    v=c.generate('a'*64,distance_m=1500.,bank_length_m=100.,bank_starts_m=(0.,170.,340.))
    assert not v['primary_loads']
    assert any('New motor length' in x for x in v['open_items'])
    assert v['complete_installed_mass_kg'] is None


def test_civil_uses_current_car_axle_offsets_and_keeps_moving_load_model_conditional():
    a=c.generate('a'*64,distance_m=1500.,car_mass_upper_kg=[18000.]*6,axle_positions_m=(1.,2.,15.,16.))
    b=c.generate('a'*64,distance_m=1500.,car_mass_upper_kg=[18000.]*6,axle_positions_m=(3.,4.,13.,14.))
    assert a['moving_load_screen']['maximum_bending_Nm']!=b['moving_load_screen']['maximum_bending_Nm']
    assert not a['moving_load_screen']['actual_wheel_rail_dynamics_validated']


@pytest.mark.parametrize('bad',['wrong','g'*64])
def test_malformed_candidate_id_is_rejected(bad):
    with pytest.raises(ValueError):c.generate(bad,distance_m=1500.)


@pytest.mark.parametrize('bad',[float('nan'),float('inf')])
def test_nonfinite_bank_location_is_rejected_before_weight_disappears(bad):
    with pytest.raises(ValueError):c.generate('a'*64,distance_m=1500.,bank_starts_m=(bad,))


def test_site_boolean_alone_never_becomes_authenticated_geotechnical_evidence():
    with pytest.raises(ValueError):c.generate('a'*64,distance_m=1500.,site={'candidate_id':'a'*64,'site_record_authenticated':False})
    v=c.generate('a'*64,distance_m=1500.,site={'candidate_id':'a'*64,'site_record_authenticated':True})
    assert v['site']['state']=='requires-completion-evidence-adapter'
    assert v['site']['allowable_bearing_Pa'] is None and v['site']['settlement_m'] is None


def test_construction_hook_load_excludes_unknown_rigging_and_does_not_approve_crane(base):
    for row in base['construction_sequence']:
        assert row['known_hook_mass_kg']>0 and row['rigging_mass_kg'] is None and row['required_crane_capacity_kg'] is None
        assert row['QA_record'] is None and row['production_slot'] is None
