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


def test_conductor_and_supports_change_dead_load_and_civil_identity(train,portfolio):
    linked=deepcopy(train)
    linked['line_equipment']=dict(cross_section_m2=.004,density_kg_m3_hypothesis=2700.,
        insulators_brackets_guards_mass_kg_track_m_hypothesis=6.,lateral_offset_from_track_centre_m=.9)
    linked.pop('evaluation_id');d.seal(linked)
    r=d.evaluate(linked)
    old=portfolio['reference_box','source']
    assert r['quantities']['line_equipment_dead_mass_kg']==pytest.approx(336.)
    assert r['quantities']['accounted_superstructure_kg']>=old['quantities']['accounted_superstructure_kg']+336.-1e-8
    assert r['policy']['line_equipment_dead_torque_Nm_m']==pytest.approx(16.8*9.80665*.9)
    assert r['civil_candidate_id']!=old['civil_candidate_id']
    assert any('conductor' in e['id'] for e in a.scene(r)['entities'])
    assert next(p for p in r['parts']['items'] if p['id']=='track/wayside-conductor')['cost_owner']=='wayside-propulsion in whole-system ledger'


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


def test_located_patterns_stay_inside_stock(portfolio):
    r=portfolio['folded_plate','thick-web'];scene=a.scene(r)
    plates=[e for e in scene['entities'] if '/fastener-' in e['id']]
    assert len(plates)==136
    assert all(0<=e['geometry']['at_m'][0] and e['geometry']['at_m'][0]+e['geometry']['size_m'][0]<=20+1e-12 for e in plates)
    hoops=[v for v in scene['definition_paths'] if v['kind']=='bending-centreline']
    assert min(v['x_m'] for v in hoops)>=.06-1e-12
    assert max(v['x_m'] for v in hoops)<=19.94+1e-12
    assert r['prestress']['service_maximum_bottom_compression_Pa']>=r['prestress']['service_midspan_bottom_compression_Pa']
    assert r['prestress']['transfer_minimum_compression_Pa']>0


def test_no_authority_and_explicit_lateral_magnitude(train):
    bad=deepcopy(train);bad['movement_authority']=True;bad.pop('evaluation_id');d.seal(bad)
    with pytest.raises(ValueError,match='acceptance'):d.validate_train(bad)
    bad=deepcopy(train);bad['load_cases'][0]['lateral_acceleration_m_s2']=-.5;bad.pop('evaluation_id');d.seal(bad)
    with pytest.raises(ValueError,match='Nonnegative'):d.validate_train(bad)


def test_cut_stock_and_nonadditive_manufacturing(portfolio):
    r=portfolio['folded_plate','thick-web'];rebar=r['reinforcement'];scene=a.scene(r)
    bars=[p for p in scene['definition_paths'] if p['kind']=='straight-bar-centreline']
    assert len(bars)==2*rebar['longitudinal_cut_pieces']
    assert sum(p['cut_length_m'] for p in bars)/2==pytest.approx(rebar['longitudinal_total_m'])
    assert all(p['path_xyz_m'][0][0]>10 or p['path_xyz_m'][1][0]<10 for p in bars)
    assert r['quantities']['prestress_procurement_kg']>r['quantities']['prestress_active_kg']
    assert not r['parts']['additive_mass_or_cost_ledger']
    assert r['shear_detail']['concrete_shear_strength_credit_N']==0
    assert not r['shear_detail']['strength_and_strut_anchorage_verified']


def test_support_wrench_distinguishes_patch_clamp_from_pin():
    from engineering.pilot_civil.native_trial import support_audit
    # A finite patch with equal/opposite nodal forces can carry a couple even
    # when the resultant lies outside its geometric footprint.
    model=dict(nodes={'1':[.2,0,-1.4],'2':[.5,0,-1.4],'3':[19.5,0,-1.4],'4':[19.8,0,-1.4]},support_nodes=[[1,2],[3,4]])
    readback=dict(reaction_distribution={'1':[0,0,-100],'2':[0,0,200],'3':[0,0,200],'4':[0,0,-100]})
    audit=support_audit(model,readback,{})
    assert audit['rows'][0]['equivalent_vertical_resultant_x_m']==pytest.approx(.8)
    assert not audit['rotation_free_line_definition_resolved']
    # Collapsing only the longitudinal constraint width permits bending
    # rotation, while keeping transverse bearing support geometry explicit.
    for n in ('1','2'):model['nodes'][n][0]=.35
    for n in ('3','4'):model['nodes'][n][0]=19.65
    audit=support_audit(model,readback,dict(lines_x_m=[.35,19.65]))
    assert audit['rotation_free_line_definition_resolved']
    assert all(abs(row['vertical_reaction_bending_couple_Nm'])<1e-12 for row in audit['rows'])


def test_same_pose_shear_reference_and_worker_definition(portfolio):
    from engineering.pilot_civil.native_trial import analytical_reference,mesh_worker
    r=portfolio['reference_box','source']
    ref=analytical_reference(r,dict(live_pose=dict(points=[dict(x_m=10.,force_N=1000.)])))
    assert ref['shear_correction_m']<0
    assert ref['declared_Timoshenko_displacement_m']<ref['Euler_Bernoulli_displacement_m']
    spec=dict(resource_request=dict(max_cells=50000),support_hypothesis=dict(mode='rotation-free-line'))
    text=mesh_worker(spec)
    assert '50000' in text and 'bearing_lines_x_m' in text
    assert 'mesh.embed(1,[edge]' in text
