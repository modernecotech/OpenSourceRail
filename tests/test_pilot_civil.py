from copy import deepcopy
from math import isclose
import pytest
from engineering.pilot_civil import design as d
from engineering.pilot_civil import assembly as a
from engineering.station_rail.common import identity


@pytest.fixture(scope='module')
def train():
    return d.baseline_train()


@pytest.fixture(scope='module')
def portfolio(train):
    return {(f,r):d.evaluate(train,family=f,revision=r) for f,r in [('reference_box','source'),('folded_plate','source'),('folded_plate','thick-web')]}


def test_mass_and_source_binding(train):
    assert d.validate_train(train)
    bad=deepcopy(train);bad['load_cases'][0]['axles'][0]['vertical_force_N']*=2
    bad.pop('evaluation_id');d.seal(bad)
    with pytest.raises(ValueError,match='conserve'):d.validate_train(bad)
    bad=deepcopy(train);bad['candidate_id']='a'*64
    with pytest.raises(ValueError,match='Sealed'):d.validate_train(bad)
    bad=deepcopy(train);bad['source_sha256']['engineering/station_rail/common.py']='a'*64
    bad.pop('evaluation_id');d.seal(bad)
    with pytest.raises(ValueError,match='source'):d.validate_train(bad)


def test_exact_beam_supports_and_equilibrium():
    EI=1e9;R1,R2,y,M=d._response([(10.,1000.)],0.,.35,19.65,EI)
    assert R1==pytest.approx(500.) and R2==pytest.approx(500.)
    assert y(.35)==pytest.approx(0.,abs=1e-15) and y(19.65)==pytest.approx(0.,abs=1e-15)
    assert M(10.)==pytest.approx(1000.*19.3/4)
    assert abs(y(10.))==pytest.approx(1000.*19.3**3/(48*EI))
    assert M(20.)==pytest.approx(0.,abs=1e-9)


def test_real_revision_retains_failure(portfolio):
    old=portfolio['folded_plate','source'];new=portfolio['folded_plate','thick-web']
    assert not old['screens']['duct_cover'] and not old['screens']['gross_vertical_deflection_target']
    assert new['screens']['duct_cover'] and new['screens']['gross_vertical_deflection_target']
    assert old['civil_candidate_id']!=new['civil_candidate_id']
    assert new['quantities']['nominal_concrete_mass_kg']>old['quantities']['nominal_concrete_mass_kg']
    assert new['prestress']['strands']%6==0
    assert new['physical_definition']['segment_joint']['closure_width_m']==.002
    assert not new['prestress']['profile_and_joint_local_stresses_verified']


def test_crane_and_cost_scope(portfolio):
    r=portfolio['reference_box','source'];cost=r['cost']
    assert not r['lifting']['whole_fits_provisional_chart']
    assert r['lifting']['whole_required_hook_kg']>60000
    assert r['lifting']['segmented_fits_provisional_chart']
    assert not r['lifting']['verified_chart_available']
    assert cost['beams']==150 and cost['shared_bents']==76
    assert next(row for row in cost['accounts'] if row['owner']=='civil/bearings')['quantity']==600
    assert len({row['owner'] for row in cost['accounts']})==len(cost['accounts'])
    assert cost['scoped_installed_usd']['base']==pytest.approx(sum(row['cost_usd']['base'] for row in cost['accounts'])*1.25)


def test_soil_hypothesis_vs_physical_redesign(train,portfolio):
    r=portfolio['reference_box','source'];B=r['foundation']['width_m']
    other=d.evaluate(train,soil_case='weak',foundation_width_m=B)
    assert other['civil_candidate_id']==r['civil_candidate_id']
    assert other['evaluation_id']!=r['evaluation_id']
    revised=d.evaluate(train,soil_case='weak')
    assert revised['foundation']['width_m']>B
    assert revised['civil_candidate_id']!=r['civil_candidate_id']


def test_assembly_is_bound_and_reserves_not_mass(portfolio):
    r=portfolio['folded_plate','thick-web'];scene=a.scene(r)
    assert scene['civil_candidate_id']==r['civil_candidate_id']
    assert len({e['id'] for e in scene['entities']})==len(scene['entities'])
    assert len([e for e in scene['entities'] if '/bearing-' in e['id']])==8
    assert len([e for e in scene['entities'] if '/piece-' in e['id']])==16
    assert len([p for p in scene['definition_paths'] if p['kind']=='tendon-duct-centreline'])==12
    assert not scene['installed_mass_from_cad_permitted']
    assert not r['construction']['construction_release']
    for k in d.FLAGS:assert r[k] is False


def test_cache_is_exact_and_returns_independent_copy(train,portfolio):
    r=portfolio['reference_box','source'];s=r['section'];p=r['policy'];load=train['load_cases'][0]
    x=d.moving(s,load,p,r['quantities']['accounted_superstructure_kg']);x['moment_Nm']=-1
    again=d.moving(s,load,p,r['quantities']['accounted_superstructure_kg'])
    assert again['moment_Nm']>0
    assert again['dynamic_factor_applied_once']==1.3
    assert again['sampled_translations']==501
