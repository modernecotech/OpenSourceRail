"""Complete civil retained-mass transfer, independent equilibrium and fail-closed inputs."""
from copy import deepcopy

import pytest

from engineering.assembly_design import baseline, evaluate, models, reactions
from engineering.continuous_design import civil_kit
from engineering.twin_workflow import core


@pytest.fixture(scope='module')
def inputs():
    policy=baseline.validate(core.read(baseline.DATA))
    variables={k:choices[0] for k,choices in policy['pilots']['bearing-seat']['domains'].items()}
    variables['bearing_family']='uk-spherical-candidate'
    candidate=models.build(policy,'bearing-seat',variables)
    a=policy['pilots']['bearing-seat']['assumptions'];f=baseline.facts(policy)
    train=reactions.revisioned(dict(architecture=policy['architecture'],mass_cases_kg=f['train.mass_cases'],cars=a['train_cars'],
        car_length_m=f['train.car_length'],tracks=a['tracks'],span_m=a['span_m'],gravity_m_s2=a['gravity_m_s2'],
        permanent_factor=a['vertical_factor'],variable_factor=a['vertical_factor']))
    seat=reactions.revisioned(dict(candidate_revision=candidate['revision'],mass_kg=sum(p['properties']['mass_kg'] for p in candidate['contract']['parts'])))
    return civil_kit.build(civil_kit.defaults()),train,seat,policy,candidate


def run(inputs):
    kit,train,seat,_,_=inputs
    return reactions.envelope(kit,train,seat,expected_kit_revision=core.digest(kit),expected_train_revision=train['revision'])


def test_known_60000_kg_track_omission_cannot_recur(inputs):
    envelope=run(inputs);g=inputs[1]['gravity_m_s2']
    permanent=envelope['combinations'][0]
    ledger={r['id']:r for r in envelope['permanent_load_ledger']}
    tracks=[r for r in permanent['loads'] if r['load_id'].startswith('G/track-')]
    assert envelope['track_support_mass_kg']==pytest.approx(60000.)
    assert sum(r['force_down_n'] for r in tracks)==pytest.approx(60000*g)
    # Independent equal-division benchmark applies to this symmetric track
    # allocation only, not as a substitute for the full eccentric load path.
    for uid in envelope['bearing_demands']:
        contribution=sum(r['bearing_contributions_n'].get(uid,0.) for r in tracks)
        assert contribution==pytest.approx(60000*g/8.)
        assert contribution==pytest.approx(73575.)
    assert {r['load_id'][2:] for r in tracks}=={uid for uid,row in ledger.items() if row['category']=='track-support'}


def test_every_permanent_unit_and_replacement_is_accounted_once(inputs):
    kit,train,seat,_,_=inputs;envelope=run(inputs)
    rows=envelope['permanent_load_ledger'];original_bearings=[u for u in kit['units'] if u['category']=='bearing']
    assert len(rows)==len(kit['units']) and {r['id'] for r in rows}=={u['id'] for u in kit['units']}
    expected=kit['mass_ledger']['installed_study_mass_kg']-sum(u['mass_kg'] for u in original_bearings)+8*seat['mass_kg']
    assert envelope['permanent_applied_mass_kg']==pytest.approx(expected)
    assert all(r['replacement_candidate_revision']==seat['candidate_revision'] for r in rows if r['category']=='bearing')
    for case in envelope['combinations']:
        toe=[r for r in case['section_resultants'] if r['section']=='pile-toes']
        # Independent whole-system vertical force check, including buried
        # foundations/piles and cage allowances, not merely the deck ledger.
        live=2*case['train_mass_kg']*20/(6*train['car_length_m'])*train['gravity_m_s2']*case['Q']
        assert -sum(r['downstream_demand_wrench'][2] for r in toe)==pytest.approx(expected*train['gravity_m_s2']*case['G']+live)
        included=[uid for r in toe for uid in r['included_self_mass_ids']]
        assert len(included)==len(set(included))
        assert set(included)=={r['id'] for r in rows if r['category'] in {'pier-cap','pier','foundation-cap','pile','pile-cage'}}
        # Reconcile global first moments as well as vertical force across both
        # pile-toe cuts, including the eccentric bearing-to-column transfer.
        for axis,moment_index,sign in ((0,4,1.),(1,3,-1.)):
            expected_first_moment=sum(r['position_m'][axis]*r['applied_mass_kg']*train['gravity_m_s2']*case['G'] for r in rows)
            expected_first_moment+=live*(10. if axis==0 else 0.)
            actual_first_moment=sum(sign*r['downstream_demand_wrench'][moment_index]+r['origin_m'][axis]*(-r['downstream_demand_wrench'][2]) for r in toe)
            # Demand Fz is negative: Mx=-yP, My=+xP.
            assert actual_first_moment==pytest.approx(expected_first_moment)


def test_signed_equilibrium_recomputed_independently_from_raw_coordinates(inputs):
    envelope=run(inputs)
    for case in envelope['combinations']:
        loads=case['loads'];support=case['bearing_reactions']
        down=sum(r['force_down_n'] for r in loads)
        assert sum(r['force_n'][2] for r in support)==pytest.approx(down)
        # These direct first moments are independent of the production wrench
        # cross-product implementation and reaction residual summary.
        for axis in (0,1):
            assert sum(r['force_n'][2]*r['position_m'][axis] for r in support)==pytest.approx(sum(r['force_down_n']*r['point_m'][axis] for r in loads))
        assert case['equilibrium_pass']
        assert max(abs(x) for x in case['equilibrium_residual'])<1e-6


def test_eccentric_point_load_retains_negative_reactions_and_first_moments():
    supports=[dict(id=str(i),position_m=[x,y,0.]) for i,(x,y) in enumerate(((0.,-1.),(0.,1.),(10.,-1.),(10.,1.)))]
    for point in ([5.,0.,2.],[3.,.25,2.],[-1.,2.,2.]):
        forces=reactions.distribute_vertical(1000.,point,supports)
        assert sum(forces.values())==pytest.approx(1000.)
        assert sum(forces[b['id']]*b['position_m'][0] for b in supports)==pytest.approx(1000*point[0])
        assert sum(forces[b['id']]*b['position_m'][1] for b in supports)==pytest.approx(1000*point[1])
    assert min(forces.values())<0.  # A contact hold must not be hidden by clipping.
    assert reactions.distribute_vertical(1000.,[5.,0.,0.],supports)==dict.fromkeys(('0','1','2','3'),250.)
    with pytest.raises(ValueError):reactions.distribute_vertical(1000.,[0.,0.,0.],supports[:3])


@pytest.mark.parametrize('defect',('kit-revision','train-revision','seat-revision','missing-masses','wrong-architecture','unsupported-span','missing-track','missing-unit-revision','missing-support','negative-mass','unaccounted-category'))
def test_missing_or_stale_load_revision_and_configuration_are_rejected(inputs,defect):
    kit,train,seat,_,_=deepcopy(inputs);expected_kit=core.digest(kit);expected_train=train['revision']
    if defect=='kit-revision':expected_kit='0'*64
    elif defect=='train-revision':expected_train='0'*64
    elif defect=='seat-revision':seat['mass_kg']+=1
    elif defect=='missing-masses':train=reactions.revisioned({k:v for k,v in train.items() if k not in ('revision','mass_cases_kg')});expected_train=train['revision']
    elif defect=='wrong-architecture':train=reactions.revisioned(dict({k:v for k,v in train.items() if k!='revision'},architecture='legacy-lm3'));expected_train=train['revision']
    elif defect=='unsupported-span':train=reactions.revisioned(dict({k:v for k,v in train.items() if k!='revision'},span_m=25.));expected_train=train['revision']
    else:
        if defect=='missing-track':kit['units']=[u for u in kit['units'] if u['category']!='track-support']
        elif defect=='missing-unit-revision':kit['units'][0]['revision']='0'*64
        elif defect=='missing-support':kit['units'][0]['support_ids']=['not-a-unit']
        elif defect=='negative-mass':kit['units'][0]['mass_kg']=-1.
        elif defect=='unaccounted-category':kit['units'][0]['category']='new-unsupported-load'
        expected_kit=core.digest(kit)
    with pytest.raises(ValueError):
        reactions.envelope(kit,train,seat,expected_kit_revision=expected_kit,expected_train_revision=expected_train)


def test_non_gravity_actions_are_mandatory_holds_not_zero_or_passing(inputs):
    envelope=run(inputs)
    assert {'braking-traction','thermal-restraint','wind','seismic','uplift-contact','erection','ground-response'}<=envelope['mandatory_action_holds'].keys()
    assert all(envelope['mandatory_action_holds'].values())
    assert all(not envelope[k] for k in core.FLAGS)
    result=evaluate.evaluate(inputs[3],inputs[4]);assert result['state']=='hold'
    assert all(result['checks']['mandatory-action/'+name] is None for name in envelope['mandatory_action_holds'])
    for local in result['measurements']['seat_load_cases']:
        shared=next(c for c in result['measurements']['reaction_envelope']['combinations'] if c['id']==local['combination_id'])
        assert local['normal_force_n']==max(r['force_n'][2] for r in shared['bearing_reactions'])
        assert local['reaction_envelope_revision']==result['measurements']['reaction_envelope']['revision']


def test_adverse_train_mass_changes_reaction_revision_and_demands(inputs):
    before=run(inputs);kit,train,seat,policy,candidate=deepcopy(inputs)
    train=reactions.revisioned(dict({k:v for k,v in train.items() if k!='revision'},mass_cases_kg=[m*2 for m in train['mass_cases_kg']]))
    after=run((kit,train,seat,policy,candidate))
    assert before['revision']!=after['revision'] and before['train_revision']!=after['train_revision']
    assert all(after['bearing_demands'][uid]['maximum_compression_n']>row['maximum_compression_n'] for uid,row in before['bearing_demands'].items())


@pytest.mark.parametrize('architecture',('large-span','segmental','light-ribbed'))
def test_selected_civil_architecture_drives_its_own_reaction_revision(inputs,architecture):
    _,train,seat,policy,candidate=inputs
    kit=civil_kit.build(civil_kit.defaults(architecture))
    envelope=run((kit,train,seat,policy,candidate))
    assert envelope['kit_revision']==core.digest(kit)
    assert envelope['track_support_mass_kg']==60000.
    assert set(envelope['unit_revisions'])=={u['id'] for u in kit['units']}
    assert all(envelope['checks'].values())
