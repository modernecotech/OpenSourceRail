"""Independent energy, reciprocity, mass and known-failure controls."""
import json
import math
from pathlib import Path

import numpy as np
import pytest

from engineering.ferrite_maglev import candidate_magnetics as m


def test_current_candidate_has_exact_historical_parent_and_no_free_mass():
    d=m.definition();p=json.loads(m.PARENT.read_text())['configuration'];ledger=d['mass_accounting']
    removed=sum(r['mass_kg_per_car'] for r in ledger['removed_defined_components'])
    added=sum(r['mass_kg_per_car'] for r in ledger['added_defined_components'])
    assert d['parent_configuration_sha256']==p['configuration_sha256']=='94ad256eb52204d3f14664aa18ad9e09a7b4478bd6347a6f6f7c00b39174cedc'
    assert math.isclose(p['controlled_tare_kg']-removed+added,d['controlled_tare_kg'],abs_tol=1e-7)
    assert d['controlled_tare_kg']+12000==d['controlled_aw3_kg']
    assert ledger['residual_ferrite_allocation_kg']==pytest.approx(174)
    assert ledger['retained_unlocated_allocation_kg']>7000
    assert all(d[k] is False for k in m.FLAGS)
    assert d['configuration_sha256']!=d['parent_configuration_sha256']


def test_actual_pole_and_coil_window_are_explicit_and_fit():
    d=m.definition();module=d['module'];v=next(v for v in m.load()['variants'] if v['id']==d['variant_id'])
    assert module['lift_pole_area_m2']==pytest.approx(.16*v['core_scale']*.1)
    stem=next(p for p in module['parts'] if p['id']=='core/shared-stem')
    coil=module['coils'][0]
    assert np.array(coil['inner_m']).min()>0
    assert coil['inner_m'][0]-stem['size_m'][0]==pytest.approx(.02)
    assert coil['inner_m'][1]-stem['size_m'][1]==pytest.approx(.02)
    assert max(c['fill_fraction'] for c in module['coils'])<=m.load()['coil_fill_limit']
    assert len(d['module_placements_m'])==24
    assert d['module_placements_m'][0][2]==-1.16


def test_zero_excitation_and_pm_zero_current_are_different():
    z=m.evaluate_batch([[.008]*4],[[0,0]],pm_enabled=False)
    p=m.evaluate_batch([[.008]*4],[[0,0]])
    assert z['upward_n'][0]<1e-10
    assert z['stored_energy_j'][0]<1e-10
    assert p['upward_n'][0]>1000
    assert p['stored_energy_j'][0]>0
    assert p['leftward_n'][0]==pytest.approx(0,abs=1e-8)


def test_asymmetric_network_spd_and_linkage_current_derivative():
    g=np.array([[.006,.011,.009,.014]]);i=np.array([[35.,12.]])
    r=m.evaluate_batch(g,i)
    assert r['valid'][0]
    L=r['incremental_inductance_h'][0]
    assert np.allclose(L,L.T,atol=1e-12)
    assert np.linalg.eigvalsh(L).min()>0
    eps=1e-2
    for k in range(2):
        delta=np.zeros((1,2));delta[0,k]=eps
        numeric=(m.evaluate_batch(g,i+delta,initial_flux_wb=r['flux_state_wb'])['flux_linkage_wb']-m.evaluate_batch(g,i-delta,initial_flux_wb=r['flux_state_wb'])['flux_linkage_wb'])/(2*eps)
        assert np.allclose(numeric[0],L[:,k],rtol=2e-5,atol=1e-8)


def test_maxwell_force_matches_coenergy_and_reciprocity():
    g=np.array([[.008,.009,.010,.011]]);i=np.array([[30.,8.]])
    r=m.evaluate_batch(g,i);eps=1e-7
    for k in range(4):
        delta=np.zeros((1,4));delta[0,k]=eps
        numerical=-(m.evaluate_batch(g+delta,i)['coenergy_j']-m.evaluate_batch(g-delta,i)['coenergy_j'])/(2*eps)
        branch=k%2;expected=r['branch_lift_force_n'][0,branch] if k<2 else r['branch_guidance_force_n'][0,branch]
        assert numerical[0]==pytest.approx(expected,rel=3e-5)
    eps=1e-2
    for k in range(2):
        delta=np.zeros((1,2));delta[0,k]=eps
        a=m.evaluate_batch(g,i+delta);b=m.evaluate_batch(g,i-delta)
        df=(a['upward_n']-b['upward_n'])/(2*eps)
        expected=-r['dflux_dgap_wb_m'][0,k,:2].sum()
        assert df[0]==pytest.approx(expected,rel=3e-5)


def test_guidance_is_passively_destabilizing_and_differential_current_changes_force():
    displaced=m.evaluate_batch([[.008,.008,.007,.009]],[[40,0]])
    assert displaced['leftward_n'][0]>0
    plus=m.evaluate_batch([[.008]*4],[[40,8]])
    minus=m.evaluate_batch([[.008]*4],[[40,-8]])
    assert plus['leftward_n'][0]>0>minus['leftward_n'][0]
    assert plus['leftward_n'][0]==pytest.approx(-minus['leftward_n'][0],rel=1e-8)


def test_inverse_returns_current_not_force_and_warm_start_preserves_result():
    g=np.array([[.008,.008,.009,.007]])
    target=m.evaluate_batch(g,[[40.,5.]])
    up=target['upward_n'];left=target['leftward_n']
    a=m.inverse_current(up,left,g)
    b=m.inverse_current(up,left,g,initial_a=a['current_a'],initial_flux_wb=a['flux_state_wb'])
    assert a['valid'][0] and b['valid'][0]
    assert np.allclose(a['current_a'],b['current_a'],atol=1e-5)
    actual=m.evaluate_batch(g,b['current_a'])
    assert actual['upward_n'][0]==pytest.approx(up[0],abs=.1)
    assert actual['leftward_n'][0]==pytest.approx(left[0],abs=.1)


@pytest.mark.parametrize('g,i,T',[(.001,0,40),(.031,0,40),(.008,121,40),(.008,0,-21),(.008,0,121)])
def test_outside_domain_does_not_clip(g,i,T):
    r=m.evaluate_batch([[g]*4],[[i,0]],T)
    assert not r['valid'][0] and not r['domain_valid'][0]


def test_known_demagnetization_failure_is_visible():
    r=m.evaluate_batch([[.03]*4],[[-120,0]],-20)
    assert not r['valid'][0]
    assert r['demag_margin_a_m'].min()<0


def test_steel_curve_is_polarization_converted_to_b_and_static_loss_zero():
    a=m.load();context=m._runtime(None)
    idx=a['materials']['steel']['h_a_m'].index(10000.)
    assert context[4][idx]==pytest.approx(1.82+m.MU0*10000)
    r=m.evaluate_batch([[.008]*4],[[30,0]])
    assert r['steel_loss_w'][0]==0
    assert m.ripple_loss(1.,50.)['specific_loss_w_kg']==pytest.approx(1.61)
    assert m.ripple_loss(1.5,50.)['specific_loss_w_kg']==pytest.approx(3.65)


def test_bom_masses_purchase_and_scopes_close():
    d=m.definition();rows=d['manufacturing_bom']
    assert sum(r['mass_kg']*r['quantity_per_car'] for r in rows)==pytest.approx(24*d['module']['mass_kg']+d['propulsion_band']['mass_kg'])
    for r in rows:
        assert r['purchase_quantity']>=r['net_material_quantity']
        assert r['extended_cost_usd']==pytest.approx(r['purchase_quantity']*r['unit_rate_usd'])
        assert r['geometry_part_ids'] and r['origin_basis']


def test_reaction_rail_is_counted_and_below_old_spines():
    d=m.guideway_definition(25)
    assert d['mass_kg']==pytest.approx(25*d['linear_mass_kg_m'])
    assert d['mass_kg']>9000 and not d['brackets_counted_here']
    assert max(p['at_m'][2]+p['size_m'][2] for p in d['parts'])<-.904


def test_spatial_halbach_independent_field_force_and_refinement():
    a=m.spatial_band_coupon(64,16);b=m.spatial_band_coupon(128,32)
    assert a['field_relative_difference']<.003 and b['field_relative_difference']<.003
    for v in (a,b):
        assert v['force_x_n_per_m_height']==pytest.approx(v['force_x_coenergy_n_per_m_height'],rel=2e-5)
        assert v['force_x_n_per_m_height']==pytest.approx(v['force_x_cross_maxwell_n_per_m_height'],rel=.005)
        assert v['force_normal_n_per_m_height']==pytest.approx(v['force_normal_cross_maxwell_n_per_m_height'],rel=.005)
    assert b['conservative_demag_margin_a_m']<0


def test_continuous_thermal_and_pack_failures_are_not_hidden():
    s=m.variant_study();by={v['id']:v for v in s['variants']}
    assert not by['compact-100']['screen_pass']
    assert not by['high-bias-180']['pack_fit']
    assert s['provisional_mass_first_screen_choice'] is None
    assert not any(v['screen_pass'] for v in s['variants'])
    assert all(v['thermal']['steady_duty_defined'] is False for v in s['variants'])
    assert all(v['thermal']['steady_duty_c'][0] is None for v in s['variants'])
    m.encoded(s)
    assert not by['light-yoke-160']['screen_pass']
    assert all(not v['complete_system_feasible'] for v in s['variants'])


def test_group_reciprocity_side_asymmetry_and_known_failure_are_preserved():
    groups=[dict(start_m=0.,end_m=5.)];x=np.array([2.131]);speed=[10.];gap=np.array([[.008,.011]]);current=[[80.,-30.]]
    r=m.propulsion_group_map(x,speed,gap,groups,current)
    assert not r['accepted_for_simulation']
    assert r['field_numerically_converged']
    assert np.any(abs(r['lambda_side_wb'][:,:,0]-r['lambda_side_wb'][:,:,1])>0)
    eps=1e-6
    for axis in (0,1):
        delta=np.zeros_like(gap);delta[0,axis]=eps
        p=m.propulsion_group_map(x,speed,gap+delta,groups,current)
        n=m.propulsion_group_map(x,speed,gap-delta,groups,current)
        numeric=(p['lambda_wb']-n['lambda_wb'])/(2*eps)
        assert np.allclose(numeric,r['dpsi_dgap_side_wb_m'][:,:,axis],rtol=1e-6,atol=1e-6)
        force=-(p['coenergy_j']-n['coenergy_j'])/(2*eps)
        assert np.allclose(force,r['normal_side_n'][:,:,axis],rtol=2e-6)
    p=m.propulsion_group_map(x+eps,speed,gap,groups,current);n=m.propulsion_group_map(x-eps,speed,gap,groups,current)
    assert np.allclose((p['coenergy_j']-n['coenergy_j'])/(2*eps),r['force_x_n'],rtol=2e-6)
    w=m.propulsion_group_definition()
    assert w['copper_mass_kg']==pytest.approx(w['total_conductor_length_m']*w['conductor_area_mm2']*1e-6*8960)
    assert w['phase_resistance_20c_ohm']==pytest.approx(w['conductor_length_m_per_phase']*1.724e-8/(w['conductor_area_mm2']*1e-6))
    assert w['slot_copper_fill']<=.55
    assert sum(v['mass_kg'] for v in w['manufacturing_bom'])==pytest.approx(w['total_mass_kg'])


@pytest.fixture(scope='module')
def packet(tmp_path_factory):
    out=tmp_path_factory.mktemp('magnetics-packet');assert m.publish(out)['verified'];return out


@pytest.mark.parametrize('target',['report-mass','purchasing'])
def test_rehashed_misleading_report_and_purchase_are_rejected(packet,tmp_path,target):
    from hashlib import sha256
    import gzip,shutil
    out=tmp_path/'forged';shutil.copytree(packet,out);manifest=json.loads((out/'manifest.json').read_text())
    if target=='report-mass':
        value=json.loads(gzip.decompress((out/'study.json.gz').read_bytes()));value['controlled_aw3_kg']-=5000
        (out/'study.json.gz').write_bytes(gzip.compress(m.encoded(value),mtime=0));name='study.json.gz'
    else:
        name='manufacturing-bom.csv';(out/name).write_bytes((out/name).read_bytes().replace(b'60,',b'1,',1))
    manifest['files_sha256'][name]=sha256((out/name).read_bytes()).hexdigest();(out/'manifest.json').write_bytes(m.encoded(manifest))
    with pytest.raises(ValueError):m.verify(out)


def test_actual_thin_return_cross_section_cannot_inherit_pole_area_or_aw3_pass():
    d=m.definition();paths=d['module']['core_paths']['stationary_return'];x=next(p for p in d['module']['parts'] if p['id']=='core/shared-stem')['size_m'][0]
    thin=[p for p in paths if p['id'] in {'stationary/flange-run','stationary/web-run'}]
    assert len(thin)==2 and all(p['area_m2']==pytest.approx(x*.025) for p in thin)
    r=m.evaluate_batch([[.008]*4],[[120.,0.]])
    assert r['peak_core_b_t'][0]==pytest.approx(max(r['peak_vehicle_core_b_t'][0],*r['peak_return_rail_b_t'][0]))
    assert r['peak_return_rail_b_t'].max()>2.
    required=d['controlled_aw3_kg']*9.80665/24
    assert r['upward_n'][0]<required/4
    inverse=m.inverse_current([required],[0.],[[.008]*4])
    assert not inverse['valid'][0]
    assert not inverse['converged'][0]
