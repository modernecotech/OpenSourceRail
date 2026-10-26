"""Independent admission controls; synthetic receipts below are test data only."""
from copy import deepcopy

import pytest

from engineering.design_search import capabilities as c

CID='1'*64
BODY='2'*64
SOURCE='3'*64


def seal(row):
    row=deepcopy(row);row.pop('evidence_id',None)
    row['evidence_id']=c.identity(row)
    return row


def body_receipts():
    """A synthetic reviewed-model package, not existing engineering evidence."""
    cap=c.catalogue()['capabilities']['body.v06-frame']
    sources={p:SOURCE for p in cap['required_source_paths']}
    rows=[]
    for benchmark in cap['independent_benchmarks']:
        rows.append(seal(dict(candidate_id=CID,component_definition_id=BODY,
            capability_id=cap['id'],interface_revision=cap['interface_revision'],
            physical_family_id=cap['physical_family_id'],evaluator_id='wheel-body',
            evidence_kind='numerical-benchmark',benchmark_id=benchmark['id'],
            independence=benchmark['required_independence'],execution='completed',
            numerical_validity='converged',screen_status='pass',
            review_disposition='accepted-for-declared-model-domain',
            review_record_id='4'*64,artifact_id='5'*64,
            validation_domain=dict(physical_family_id=cap['physical_family_id'],
                limits={'load_case':'test fixture only','max_displacement_m':.001}),
            source_sha256=sources,**c.FLAGS)))
    return rows,sources


def fixture_composition():
    return c.composition('P1',CID,'REQUIREMENTS-A',component_definition_ids={'body':BODY})


def test_catalogue_separates_families_interfaces_and_unknown_quantities():
    cat=c.catalogue()
    assert set(cat['families'])=={'P1','P2','P3','P4','P5','P6','P7'}
    assert set(cat['domains'])=={'body','runninggear','propulsion','secondary','guideway','station','HVAC','manufacturing'}
    for family,record in cat['families'].items():
        value=c.composition(family,CID,'REQUIREMENTS-A')
        assert value['capabilities']==record['capabilities']
        assert set(value['capabilities'])==set(cat['domains'])
        assert not record['default_changed']
    assert cat['families']['P6']['energy_variants']==['battery','conductor-supply']
    assert cat['selected_development_default']=='engineering/development-baseline.toml'
    assert not cat['selected_development_default_changed'] and not cat['unknown_is_zero']
    for record in cat['capabilities'].values():
        assert record['complete_installed_mass_kg'] is None
        assert record['complete_installed_price_USD'] is None
        assert record['evidence_ids']==[]
        assert record['maturity']=='concept'
        assert record['native_evaluator'] is None or not record['native_evaluator']['validated']


def test_new_topology_cannot_reuse_old_motor_or_false_interface():
    with pytest.raises(ValueError,match='architecture mismatch'):
        c.composition('P7',CID,'REQ',capabilities={'propulsion':'propulsion.P1'})
    with pytest.raises(ValueError,match='architecture mismatch'):
        c.composition('P1',CID,'REQ',capabilities={'secondary':'secondary.alternative'})
    bad=fixture_composition();bad['interface_revisions']['body']='invented/9'
    with pytest.raises(ValueError,match='Interface revision'):
        c.validate_composition(bad)
    bad=fixture_composition();bad['capabilities'].pop('HVAC')
    with pytest.raises(ValueError,match='Every required'):
        c.validate_composition(bad)


def test_physical_identity_does_not_become_requirement_or_evaluation_identity():
    a=c.composition('P1',CID,'REQ-A');b=c.composition('P1',CID,'REQ-B')
    assert a['candidate_id']==b['candidate_id'] and c.identity(a)!=c.identity(b)
    for extra in ('evaluation_id','selection_id','solver_settings'):
        bad=deepcopy(a);bad[extra]='unrelated'
        with pytest.raises(ValueError,match='outside physical'):
            c.validate_composition(bad)
    with pytest.raises(ValueError,match='Physical candidate'):
        c.composition('P1','not-a-physical-id','REQ')
    with pytest.raises(ValueError,match='cannot assert release'):
        c.validate_composition({**a,'physical_accepted':True})


def test_implemented_module_and_software_tests_are_not_native_evidence():
    value=fixture_composition();rows,sources=body_receipts()
    assert c.eligible_evaluators(value)==[]
    software=[seal({**r,'evidence_kind':'software-test'}) for r in rows]
    assert c.eligible_evaluators(value,software,current_source_sha256=sources)==[]
    assert c.admission_check(value,purpose='native-research')['readiness']=='held-no-validated-native-capability'


def test_exact_reviewed_benchmarks_bind_candidate_stock_interface_and_current_source():
    value=fixture_composition();rows,sources=body_receipts()
    eligible=c.eligible_evaluators(value,rows,current_source_sha256=sources)
    assert len(eligible)==1 and eligible[0]['domain']=='body'
    assert not eligible[0]['automatic_dispatch_eligible']
    assert eligible[0]['request_domain_check_required']
    assert eligible[0]['validated_domains'][0]['validation_domain']['limits']['load_case']=='test fixture only'
    assert c.eligible_evaluators(value,rows[:1],current_source_sha256=sources)==[]
    for key,wrong in [('candidate_id','a'*64),('component_definition_id','b'*64),
        ('interface_revision','wrong/1'),('physical_family_id','a-new-topology/1'),
        ('numerical_validity','nonconverged'),('screen_status','unknown'),
        ('review_disposition','not-reviewed'),('review_record_id',None)]:
        bad=[seal({**r,key:wrong}) for r in rows]
        assert c.eligible_evaluators(value,bad,current_source_sha256=sources)==[],key
    stale={**sources,next(iter(sources)):'f'*64}
    assert c.eligible_evaluators(value,rows,current_source_sha256=stale)==[]
    assert c.eligible_evaluators(value,rows,current_source_sha256={})==[]


def test_hash_tampering_source_omission_and_unknown_component_identity_fail_closed():
    value=fixture_composition();rows,sources=body_receipts()
    tampered=deepcopy(rows);tampered[0]['artifact_id']='a'*64
    assert c.eligible_evaluators(value,tampered,current_source_sha256=sources)==[]
    missing_source=[]
    for row in rows:
        row=deepcopy(row);row['source_sha256'].pop(next(iter(row['source_sha256'])))
        missing_source.append(seal(row))
    assert c.eligible_evaluators(value,missing_source,current_source_sha256=sources)==[]
    unknown=c.composition('P1',CID,'REQ')
    assert c.eligible_evaluators(unknown,rows,current_source_sha256=sources)==[]
    alternative=c.composition('P1',CID,'REQ',capabilities={'body':'body.new-topology'},component_definition_ids={'body':BODY})
    assert c.eligible_evaluators(alternative,rows,current_source_sha256=sources)==[]


def test_plans_are_not_measurements_and_preferences_cannot_override_safety():
    value=fixture_composition();cat=c.catalogue()
    constraint_states={name:'pass' for category in ('mandatory_safety','mandatory_accessibility','mandatory_functional') for name in cat['constraints'][category]}
    plans={name:{**plan,'plan_id':f'PLAN-{name}'} for name,plan in cat['measurement_plans'].items()}
    complete={name:'complete' for name in cat['assembly_requirements']}
    result=c.admission_check(value,purpose='integrated-review',constraint_states=constraint_states,assembly_states=complete,measurement_plans=plans)
    assert result['readiness']=='held-for-evidence'
    assert {r['id'] for r in result['holds'] if r['kind']=='physical-measurement-evidence'}=={'M1','M2','M3'}
    assert result['complete_installed_mass_kg'] is None and result['complete_installed_price_USD'] is None
    assert not result['measurement_plan_is_measurement'] and not result['measurement_evidence_accepted']
    assert all(result[name] is False for name in c.FLAGS)
    constraint_states['boarding-gap-and-step']='unknown'
    constraint_states['independent-braking-and-parking']='fail'
    constraint_states.update({name:'pass' for name in cat['constraints']['preferences']})
    result=c.admission_check(value,constraint_states=constraint_states)
    assert {'kind':'mandatory-constraint','id':'independent-braking-and-parking','state':'fail'} in result['holds']
    assert {'kind':'mandatory-constraint','id':'boarding-gap-and-step','state':'unknown'} in result['holds']
    assert cat['measurement_plans']['M1']['scope']=='Measured component, joint and brake correlation'
    assert cat['measurement_plans']['M2']['scope']=='Repeated one passive carriage launch/coast/safe stop/faults'
    assert cat['measurement_plans']['M3']['scope']=='Full-sized station-to-station pilot and recovery'
