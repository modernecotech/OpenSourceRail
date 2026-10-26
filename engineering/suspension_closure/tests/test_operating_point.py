"""Force crossings and current/temperature domains cannot grant hover evidence."""
from copy import deepcopy
import os
from pathlib import Path

import pytest

from engineering.suspension_closure import operating_point as op

EVIDENCE=Path(os.environ.get('OSR_EVIDENCE_ROOT',str(op.ROOT)))


@pytest.fixture(scope='module')
def ctx():return op.context(EVIDENCE)


def test_nonmonotonic_curve_preserves_every_crossing_and_flat_interval():
    roots=op.crossings([(0.01,10.),(.02,30.),(.03,10.),(.04,30.)],20.)
    assert [r['linear_estimate_gap_m'] for r in roots['crossings']]==pytest.approx([.015,.025,.035])
    assert roots['equilibrium_solved'] is False
    assert roots['sampled_force_is_a_confidence_bound'] is False
    flat=op.crossings([(.01,20.),(.02,20.)],20.)['crossings'][0]
    assert flat['continuum'] is True and flat['linear_estimate_gap_m'] is None


def test_curve_never_extrapolates_and_exact_node_is_not_duplicated():
    assert op.crossings([(.01,10.),(.02,20.)],30.)['crossings']==[]
    exact=op.crossings([(.01,10.),(.02,20.),(.03,30.)],20.)
    assert len(exact['crossings'])==1
    assert op.crossings([],10.)['status']=='insufficient-samples'
    with pytest.raises(ValueError):op.crossings([(.01,10.),(.01,20.)],15.)
    with pytest.raises(ValueError):op.crossings([(.01,float('nan')),(.02,10.)],15.)


@pytest.mark.parametrize('kwargs',[dict(gap_m=.007),dict(gap_m=.061),dict(gap_m=.04,temperature_C=19.),
    dict(gap_m=.04,temperature_C=81.),dict(gap_m=.04,currents_A={'array-left-control':15.}),
    dict(gap_m=.04,temperature_C=float('nan')),dict(gap_m=.04,facing_thickness_m=.01)])
def test_unsupported_native_states_are_refused(kwargs):
    with pytest.raises(ValueError):op.state(**kwargs)


def test_same_selected_equipped_mass_drives_normal_and_crowd_requirements(ctx):
    rows=op.loads(ctx)
    assert [r['passengers_per_car'] for r in rows]==[0,46,160]
    assert [r['six_car_passenger_mass_kg'] for r in rows]==[0.,20700.,72000.]
    assert rows[1]['mean_weight_N_per_module']==pytest.approx(20806.683728076856*op.G/24)
    assert all(r['actual_module_load_distribution_known'] is False for r in rows)


def test_temperature_rebase_changes_material_state_not_physical_stock(ctx):
    source=ctx['component'];original=deepcopy(source);grade=source['materials'][source['grade_id']]
    for T in (20.,50.,80.):
        effective=op.effective_value(source,op.state(.04,T))
        g=effective['materials'][source['grade_id']]
        assert g['br_20c_t']*(1+60*g['br_temperature_coefficient_per_k'])==pytest.approx(grade['br_20c_t']*(1+(T-20)*grade['br_temperature_coefficient_per_k']))
        assert g['hcj_20c_a_m']*(1+60*g['hcj_temperature_coefficient_per_k'])==pytest.approx((grade['hcj_20c_a_m']-grade.get('hcj_tolerance_a_m',0.))*(1+(T-20)*grade['hcj_temperature_coefficient_per_k']))
        assert effective['physical_id']==source['physical_id']
    assert source==original


def test_thin_facing_is_distinct_interface_and_train_stock_is_unchanged(ctx):
    old=ctx['component'];new=op.physical_interface(old,.020)
    assert new['physical_id']!=old['physical_id']
    assert [p for p in new['stock_parts'] if p['group']=='train']==[p for p in old['stock_parts'] if p['group']=='train']
    facing=next(p for p in new['stock_parts'] if p['group']=='guideway')
    assert facing['size_m']==[1.,.5,.020]
    assert new['stock']['facing_mass_kg_per_m_per_bank']==facing['mass_kg']
    assert facing['mass_kg']==pytest.approx(.010*next(p for p in old['stock_parts'] if p['group']=='guideway')['density_kg_m3'])
    bad=deepcopy(old);bad['physical_id']='0'*64
    with pytest.raises(ValueError,match='selected'):op.physical_interface(bad,.020)


def test_current_diagnostic_rejects_mixed_component_and_does_not_credit_3D(ctx):
    result=op.current_diagnostics(ctx)
    normal=next(r for r in result['common'] if r['gap_m']==.044 and r['load']['case']=='normal-46')
    assert normal['diagnostic']['status']=='sampled-crossing'
    assert normal['native_3D_current_authority_N'] is None
    assert normal['actual_current_selected'] is False
    assert result['redesigned_coil_contract']['required_3D_solver'].startswith('Vector potential')
    assert all(r['scope'].startswith('Retained2D35.338mm') for r in result['retained_35_338mm_transverse_diagnostics'])
    bad=deepcopy(ctx);bad['magnet_component_id']='0'*64
    with pytest.raises(ValueError,match='another'):op.current_diagnostics(bad)


def test_no_native_temperature_or_missing_axis_is_invented(ctx):
    curves=op.curve_diagnostics(ctx)
    assert len(curves)==6
    assert all(c['status']=='insufficient-samples' for r in curves if r['temperature_C']==20. for c in r['contours'])
    assert op.curve_diagnostics(ctx,[dict(execution_status='completed',point=dict(force_credit=False))])==curves
    assert all(r['operating_gap_selected'] is False and r['stable_hover_established'] is False for r in curves)
