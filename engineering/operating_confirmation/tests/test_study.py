from copy import deepcopy
import os
from pathlib import Path
import pytest
from engineering.operating_confirmation import study as s

ROOT=Path(os.environ.get('OSR_SUSPENSION_EVIDENCE_ROOT',s.ROOT))


def test_physical_component_is_exact_retained_differential_stock():
    item=s.candidate(ROOT)
    assert item['component_id']=='397ddf033ab98afaea053acaa3047249a3329f542f1f5e52a6eb1b466b9662e0'
    assert item['value']['stock']['magnet_volume_m3_per_module']==pytest.approx(.012)
    assert s.specs()[0]['state']['gap_m']==.035338
    assert s.specs()[1]['state']['gap_m']==.028
    assert all(r['settings']==dict(margin_m=.15,near_mesh_size_m=.032,gap_mesh_size_m=.010) for r in s.specs())


@pytest.mark.parametrize('kw',[dict(temperature_C=20.),dict(temperature_C=True),dict(currents_A={'array-left-control':1.}),dict(currents_A={'array-left-control':0.})])
def test_scalar_potential_fixture_cannot_claim_coil_current_or_other_temperature(kw):
    with pytest.raises(ValueError,match='PM-only'):s.state(.028,**kw)


@pytest.mark.parametrize('gap',[.012,.031,float('nan'),True])
def test_unrequested_gap_is_not_substituted_or_interpolated(gap):
    with pytest.raises(ValueError):s.state(gap)


def test_unsupported_worker_state_is_rejected_before_native_mesher(monkeypatch,tmp_path):
    called=[]
    monkeypatch.setattr(s.finite,'mesh_case',lambda *a:called.append(True))
    with pytest.raises(ValueError,match='state differs'):
        s._worker({'state':dict(s.state(.028),currents_A={'coil':1.})},tmp_path)
    assert called==[]


def row(z,case):
    forces=[dict(force_N=[0.,0.,v],moment_Nm=[0.,0.,0.],moment_origin_m=[0.,0.,0.]) for v in z]
    p=dict(force_credit=True,state=s.state(.028 if case=='medium-28mm' else s.parent.GAP),
        analysis=dict(air_contour_results=forces,contour_force_change=s.analysis.change(forces[0]['force_N'],forces[1]['force_N']),
            demag_proxy_margin_A_per_m=100.,steel_B_peak_T=1.2))
    return dict(case=case,execution_status='completed',execution=dict(returncode=0,timed_out=False),point=p)


def test_load_screen_uses_lower_contour_and_preserves_mean_reserve_distinction():
    item=dict(component_id='physical',comparison_aw3_kg_per_car=30000.)
    base=row([9000.,10000.],'old')['point'];base.update(request_id='retained-request',state_id='retained-state')
    a=row([11000.,13000.],'medium-same-gap');b=row([14000.,15000.],'medium-28mm')
    report=s.comparisons(item,base,[a,b],{'execution_status':'not-requested'})
    p,q=report['operating_states']
    assert p['observed']['lower_contour_supports_mean_weight'] is False
    assert q['observed']['lower_contour_supports_mean_weight'] is True
    assert q['observed']['lower_contour_supports_1_3_plus_2t'] is False
    assert q['mean_AW3_weight_N_per_module']==pytest.approx(30000*9.80665/24)
    assert q['plus_2t_1_3_required_N_per_module']==pytest.approx(32000*9.80665*1.3/24)
    assert report['diagnostics']['force_map_qualified'] is False
    assert report['bracketed_stable_hover'] is False


def test_interrupted_or_partial_source_cannot_supply_force():
    assert s._values({'execution_status':'interrupted'}) is None
    partial=row([11000.,13000.],'medium-same-gap');partial['point']['force_credit']=False
    assert s._values(partial) is None
    failed=row([11000.,13000.],'medium-same-gap');failed['execution']['timed_out']=True
    with pytest.raises(ValueError,match='successful'):s._values(failed)


def test_postprocess_and_mesh_changes_have_separate_diagnostics():
    item=dict(component_id='physical',comparison_aw3_kg_per_car=30000.)
    base=row([9000.,10000.],'old')['point'];base.update(request_id='retained-request',state_id='retained-state')
    a=row([11000.,13000.],'medium-same-gap');b=row([14000.,15000.],'medium-28mm');quad=row([9500.,10500.],'quadrature')
    r=s.comparisons(item,base,[a,b],quad)['diagnostics']
    assert r['mesh_change_same_state'][0]['force']['delta'][2]==2000.
    assert r['quadrature_change_same_field'][0]['force']['delta'][2]==500.


@pytest.mark.parametrize('kw',[dict(seconds_total=601.),dict(seconds_per_case=301.),dict(seconds_total=0.),dict(seconds_total=True),dict(quadrature=1)])
def test_resource_contract_is_checked_before_launch(tmp_path,kw):
    with pytest.raises(ValueError):s.run(tmp_path/'run',ROOT,None,None,**kw)
