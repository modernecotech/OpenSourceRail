from copy import deepcopy
from functools import lru_cache
import math
import os
from pathlib import Path
import pytest
from engineering.suspension_closure import study as s
from engineering.halbach_scaling import candidates as old
from engineering.passive_suspension import fields

ROOT=Path(os.environ.get('OSR_SUSPENSION_EVIDENCE_ROOT',s.ROOT))


@lru_cache(None)
def catalogue():return s.candidates(ROOT)


def test_retained_components_have_exact_old_physical_ids_and_unchanged_stock():
    a,b,h=catalogue();prior=old.candidates(ROOT)
    assert a['value']==next(v for v in prior if v['physical_id']==a['component_id'])
    assert b['value']==next(v for v in prior if v['physical_id']==old.PARENT_ID)
    assert len({c['component_id'] for c in (a,b,h)})==3


def test_hybrid_replaces_actual_stock_density_and_preserves_magnetic_volume():
    a,b,h=catalogue();by=h['stock_by_material']
    assert by['Arnold-N35UH']['volume_m3']==pytest.approx(.006)
    assert by['TDK-FB9B-recoil-proxy']['volume_m3']==pytest.approx(.006)
    assert by['TDK-FB9B-recoil-proxy']['mass_kg']==pytest.approx(30.)
    assert a['known_stock_kg_per_module']-h['known_stock_kg_per_module']==pytest.approx(15.6)
    assert h['value']['stock']['train_known_mass_kg_per_module']==pytest.approx(h['known_stock_kg_per_module'])
    assert h['comparison_aw3_kg_per_car']==pytest.approx(a['comparison_aw3_kg_per_car']-24*15.6)
    assert h['installed_mass_kg_per_module'] is None and h['cost_per_module'] is None
    for p in h['value']['stock_parts']:
        assert p['mass_kg']==pytest.approx(p['volume_m3']*p['density_kg_m3'])
    # All actual PMs remain onboard; no source is assigned to passive steel.
    geo=s.geometry(h);rows,_,_=fields._prepare(geo,s.GAP,0.,0.,{},80.)
    assert all(not r['br'].any() and r['J']==0 for r in rows if r['group']=='guideway')


def test_rehashed_hybrid_stock_or_material_mutation_is_rejected():
    h=deepcopy(catalogue()[2]);h['value']['stock_parts'][0]['mass_kg']*=.1
    h['definition_id']=s.identity({k:v for k,v in h.items() if k!='definition_id'})
    with pytest.raises(ValueError,match='stock/material'):s.validate_candidate(h,ROOT)


def test_hybrid_demagnetisation_uses_each_regions_own_grade_not_aggregate_flag():
    h=catalogue()[2];state=s.scenario(h)
    region={r['id']:{'H_parallel_min_A_per_m':-400000.} for r in h['value']['regions'] if 'Br_y_T' in r and r['material'] not in ('copper','aluminium','steel')}
    raw=dict(numerical_status='converged',region_diagnostics=region,steel_B_peak_T=1.,
        material_model_domain_pass=True,diagnostics={'contour_forces':[dict(F_z_N=10000.,F_y_N=0.,M_x_Nm=0.)]*2})
    c=s.comparisons(h,raw,state)
    nd=[r for r in c['per_region_demag'] if r['material_id']=='Arnold-N35UH']
    ferrite=[r for r in c['per_region_demag'] if r['material_id']=='TDK-FB9B-recoil-proxy']
    assert all(r['demag_proxy_pass'] for r in nd)
    assert not any(r['demag_proxy_pass'] for r in ferrite)
    assert c['per_region_material_screen_pass'] is False
    assert c['legacy_aggregate_material_screen_used'] is False


@pytest.mark.parametrize('kw',[dict(gap_m=.007),dict(temperature_C=0.),dict(current_A=16.),dict(lateral_m=.01),dict(current_A=float('nan'))])
def test_unsupported_states_fail_before_solver(kw):
    with pytest.raises(ValueError):s.scenario(catalogue()[0],**kw)


def test_opposed_connection_requires_two_actual_circuits():
    with pytest.raises(ValueError,match='connection'):s.scenario(catalogue()[1],mode='opposed')
    p=s.scenario(catalogue()[0],mode='opposed',current_A=15.)
    assert sorted(p['currents_A'].values())==[-15.,15.]


def test_plan_resolves_relevant_gap_current_temperature_and_half_step_questions():
    rows=s.plan(catalogue())
    assert len(rows)==32
    assert max(abs(v) for r in rows for v in r['state']['currents_A'].values())==15
    assert {r['state']['temperature_C'] for r in rows}=={20.,80.}
    assert all(r['state']['gap_m']>=.008 for r in rows)
    a=[r for r in rows if r['candidate_id']==catalogue()[0]['component_id']]
    assert any(r['tag']=='80C/half-gap-plus' for r in a)


def test_central_force_difference_recovers_independent_quadratic_derivative():
    # F(g)=a*g²+b*g+c at x±h must give2*a*x+b for either contour.
    x=.035;h=.001;a=2e7;b=-1e6;c=25000.
    F=lambda g:a*g*g+b*g+c
    result=s.central_difference([F(x+h),2*F(x+h)],[F(x-h),2*F(x-h)],2*h)
    assert result==pytest.approx([2*a*x+b,2*(2*a*x+b)])
    with pytest.raises(ValueError):s.central_difference([1.],[0.],0.)


def test_interrupted_campaign_retains_unknowns_and_cannot_supply_force(tmp_path):
    out=tmp_path/'interrupted';r=s.run(out,ROOT,seconds_total=.01,seconds_per_trial=.01)
    assert len(r['rows'])==32 and all('point' not in row for row in r['rows'])
    assert all('nominal' not in t for c in r['comparisons'] for t in c['temperatures'])
    assert s.verify(out,ROOT)['completed']==0
    row=deepcopy(r['rows'][0]);row['execution_status']='completed'
    with pytest.raises(ValueError,match='successful worker'):s._usable(row)


def test_point_replay_rejects_rehashed_current_and_material_change():
    item=catalogue()[0];state=s.scenario(item)
    point=s.evaluate(item,state,ROOT)
    s.point_contract(point,item,state,ROOT)
    bad=deepcopy(point);bad['raw_result']['operating_point']['currents_A']={c['id']:1. for c in item['value']['circuits']}
    bad['raw_result']['result_id']=fields._digest({k:v for k,v in bad['raw_result'].items() if k!='result_id'})
    with pytest.raises(ValueError,match='field/material/state'):s.point_contract(bad,item,state,ROOT)
