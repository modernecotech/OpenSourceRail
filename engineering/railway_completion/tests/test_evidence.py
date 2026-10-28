"""Adversarial current evidence tests; fixtures are never real qualification.

Positive authentication below is an opaque HMAC callback owned by this test
process. No production trust store, identity, physical record or approval is
provided or installed by these fixtures.
"""
from copy import deepcopy
from hashlib import sha256
import hmac
import json
from pathlib import Path

import pytest

from engineering.railway_twin import model
from engineering.railway_completion import evidence as e, domains
from engineering.station_rail.common import encoded, identity
from engineering.design_search import test_readiness


TEST_KEY = b'UNIT-TEST-ONLY-NOT-A-PRODUCTION-TRUST-ANCHOR'
ROLES = {'record-producer','independent-reviewer','procedure-approver',
         'independent-assessor','calibration-authority','limit-approver'}
PREREQUISITES = ('procedure-and-hazards','article-and-material-revisions',
                 'earlier-gates-and-ncrs','safe-restraint-and-rescue')


def sign(claim, role, subject=None):
    value = dict(role=role,subject_id=subject or 'unit-test-'+role,
                 payload_sha256=identity(claim))
    value['signature'] = hmac.new(TEST_KEY,encoded(value),sha256).hexdigest()
    return value


def test_only_authenticator(attestation, role):
    if role not in ROLES or attestation.get('role') != role:
        return False
    claim = {k:v for k,v in attestation.items() if k != 'signature'}
    signature = hmac.new(TEST_KEY,encoded(claim),sha256).hexdigest()
    return hmac.compare_digest(attestation.get('signature',''),signature)


test_only_authenticator.__test__ = False


@pytest.fixture(scope='module')
def bundle():
    return model.materialize()['bundle']


def write_file(folder, name, value):
    path = Path(folder)/name
    path.parent.mkdir(parents=True,exist_ok=True)
    raw = value if isinstance(value,bytes) else encoded(value)
    path.write_bytes(raw)
    return dict(path=name,sha256=sha256(raw).hexdigest())


def reseal_record(record):
    record = deepcopy(record)
    record['record_id'] = identity({k:v for k,v in record.items() if k != 'record_id'})
    return record


def resign_envelope(envelope):
    claim = {k:v for k,v in envelope.items() if k not in ('attestations','attestation')}
    envelope.setdefault('attestations',{})
    envelope['attestations']['producer'] = sign(claim,'record-producer')
    envelope['attestations']['reviewer'] = sign(claim,'independent-reviewer')
    return envelope


@pytest.mark.parametrize('raw',[
    b'{"x":1,"x":2}', b'{"x":NaN}', b'{"x":Infinity}', b'{"x":-Infinity}',
])
def test_duplicate_or_nonfinite_json_cannot_hide_evidence(raw):
    with pytest.raises(ValueError):
        e.parse(raw)


@pytest.mark.parametrize('path',[
    '../outside.json','/absolute.json','a/../raw.json','a\\raw.json','./raw.json','a//raw.json','.',
])
def test_input_paths_are_owned_relative_and_canonical(tmp_path,path):
    with pytest.raises(ValueError):
        e.read_owned(tmp_path,dict(path=path,sha256='a'*64))


def test_byte_receipts_and_both_leaf_and_parent_links_are_rejected(tmp_path):
    reference = write_file(tmp_path,'raw.json',dict(value=1))
    assert e.parse(e.read_owned(tmp_path,reference)) == dict(value=1)
    with pytest.raises(ValueError):
        e.read_owned(tmp_path,dict(reference,sha256='0'*64))
    (tmp_path/'leaf.json').symlink_to(tmp_path/'raw.json')
    with pytest.raises(ValueError,match='Linked'):
        e.read_owned(tmp_path,dict(reference,path='leaf.json'))
    (tmp_path/'parent').symlink_to(tmp_path,target_is_directory=True)
    with pytest.raises(ValueError,match='Linked'):
        e.read_owned(tmp_path,dict(reference,path='parent/raw.json'))
    with pytest.raises(ValueError):
        e.read_owned(tmp_path,reference,maximum=1)


def fixture_record(folder,bundle,*,physical=False):
    """A schema-shaped software fixture, signed solely by TEST_KEY above."""
    protocol_id='T01'
    protocol=next(r for r in test_readiness.definitions()['protocols'] if r['id']==protocol_id)
    bound=e.binding(bundle)
    record=domains.make_record(bundle,'installed-equipment',{})
    source=write_file(folder,'record.json',record)
    raw=write_file(folder,'source.json',dict(kind='unit-test-source',physical_evidence=False))
    procedure_data=dict(schema='osr-wheel-LIM-approved-procedure/1',revision='UNIT-TEST-PROCEDURE-1',
        protocol_id=protocol_id,binding=deepcopy(bound),required_cases={'empty':2},
        required_prerequisites=list(PREREQUISITES),
        criterion_channels={'installed_mass_kg':['installed_mass_kg'],
                            'clearance_m':['clearance_m']},derived_observables=['CG_and_inertia'])
    procedure=dict(revision=procedure_data['revision'],protocol_id=protocol_id,binding=deepcopy(bound),
        source=write_file(folder,'procedure.json',procedure_data),approved_at='2026-10-20T00:00:00Z')
    envelope=dict(schema='osr-wheel-LIM-evidence-envelope/1',binding=deepcopy(bound),protocol_id=protocol_id,
        provenance_kind='physical-measurement' if physical else 'numerical-validation',record=source,
        raw_files=[raw],started_at='2026-10-21T00:00:00Z',ended_at='2026-10-21T00:01:00Z',
        procedure=procedure,deviations=[],cases=['empty'],
        article=dict(as_built_candidate_id=bundle['candidate_id'],serials=['UNIT-TEST-NOT-A-REAL-ARTICLE'],
                     material_batches=['UNIT-TEST-NOT-A-REAL-LOT']),
        prerequisites=[],calibrations=[],approved_limits=[],derived_criteria=[],channel_instruments={},attestations={})
    for name in PREREQUISITES:
        row=dict(id=name,binding=deepcopy(bound),protocol_id=protocol_id,state='passed',
                 source=write_file(folder,'prerequisite-'+name+'.json',dict(id=name,test_only=True)))
        row['attestation']=sign(row,'independent-assessor');envelope['prerequisites'].append(row)
    envelope['attestations']['procedure']=sign(procedure,'procedure-approver')
    if physical:
        channels={r['name']:r['unit'] for r in protocol['measured_channels']}
        raw_files=[]
        for rep in range(2):
            samples=[]
            for time in (0.,.5,1.):
                values={name:0. for name in channels}
                values.update(time_s=time,installed_mass_kg=1000.,wheel_reaction_N=2451.6625,
                              I_xx_kg_m2=100.,I_yy_kg_m2=100.,I_zz_kg_m2=100.,clearance_m=.05)
                samples.append(values)
            raw_files.append(write_file(folder,'measurements-'+str(rep)+'.json',
                dict(schema='osr-wheel-LIM-measurements/1',binding=deepcopy(bound),article=deepcopy(envelope['article']),
                     channels=channels,case_id='empty',repetition=rep,samples=samples)))
        envelope['raw_files']=raw_files
        for channel,unit in channels.items():
            if channel=='time_s':
                continue
            certificate=write_file(folder,'calibration-'+channel+'.json',dict(channel=channel,instrument='UNIT-TEST-INSTRUMENT',test_only=True))
            row=dict(channel=channel,unit=unit,binding=deepcopy(bound),protocol_id=protocol_id,
                expanded_uncertainty=.001,coverage_factor=2.,instrument_serial='UNIT-TEST-INSTRUMENT',
                certificate=certificate,range=[-100000.,100000.],valid_from='2026-10-20T00:00:00Z',valid_until='2026-10-22T00:00:00Z')
            envelope['channel_instruments'][channel]=row['instrument_serial']
            row['attestation']=sign(row,'calibration-authority');envelope['calibrations'].append(row)
        for observable,names in procedure_data['criterion_channels'].items():
            for channel in names:
                derivation=write_file(folder,'derive-'+observable+'-'+channel+'.json',dict(observable=observable,channel=channel,test_only=True))
                row=dict(observable=observable,channel=channel,unit=channels[channel],statistic='max',comparison='le',
                    value=2000.,binding=deepcopy(bound),protocol_id=protocol_id,procedure_revision=procedure['revision'],
                    case_ids=['empty'],derivation='Unit-test criterion derivation only; not approved project limits',
                    derivation_source=derivation,approved_at='2026-10-20T00:00:00Z')
                row['attestation']=sign(row,'limit-approver');envelope['approved_limits'].append(row)
        derived=dict(schema='osr-wheel-LIM-derived-criterion/1',binding=deepcopy(bound),
            observable='CG_and_inertia',unit='SI tensor',procedure_sha256=procedure['source']['sha256'],
            raw_files=deepcopy(raw_files),article=deepcopy(envelope['article']),conclusion='passed',
            reviewed_at='2026-10-21T00:02:00Z',test_fixture_only=True)
        derived['attestation']=sign(derived,'independent-assessor')
        envelope['derived_criteria']=[write_file(folder,'derived-CG-and-inertia.json',derived)]
    return resign_envelope(envelope)


def test_default_authenticator_holds_even_complete_schema_shaped_numerical_input(tmp_path,bundle):
    envelope=fixture_record(tmp_path,bundle)
    result=e.assess(tmp_path,envelope,bundle)
    assert result['state']=='hold' and result['authenticated'] is False
    assert result['physical_protocol_screen_passed'] is False
    assert any('authenticated' in reason for reason in result['holds'])


def test_external_test_callback_screens_numerical_scope_without_issuing_release(tmp_path,bundle):
    envelope=fixture_record(tmp_path,bundle)
    result=e.assess(tmp_path,envelope,bundle,authenticator=test_only_authenticator)
    assert result['state']=='authenticated-for-declared-scope' and result['authenticated'] is True
    assert result['physical_protocol_screen_passed'] is False
    assert all(result[key] is False for key in e.FLAGS)


@pytest.mark.parametrize('kind',['synthetic-method-test','template','simulated','physical-measurement-fixture'])
def test_synthetic_or_template_provenance_refused_even_with_test_signatures(tmp_path,bundle,kind):
    envelope=fixture_record(tmp_path,bundle)
    envelope['provenance_kind']=kind;resign_envelope(envelope)
    with pytest.raises(ValueError,match='provenance'):
        e.assess(tmp_path,envelope,bundle,authenticator=test_only_authenticator)


def test_actual_physical_schema_fixture_needs_all_cases_calibrations_and_preapproved_limits(tmp_path,bundle):
    envelope=fixture_record(tmp_path,bundle,physical=True)
    result=e.assess(tmp_path,envelope,bundle,authenticator=test_only_authenticator)
    assert result['state']=='authenticated-for-declared-scope' and result['physical_protocol_screen_passed']
    assert len(result['metrics'])>=2*len(envelope['approved_limits'])
    assert all(metric['passed'] for metric in result['metrics'])
    assert all(result[key] is False for key in e.FLAGS)


def rewrite_derived(folder,envelope,**changes):
    for index,reference in enumerate(envelope.get('derived_criteria',[])):
        value=e.parse(e.read_owned(folder,reference))
        value.update(raw_files=deepcopy(envelope['raw_files']),article=deepcopy(envelope['article']),
                     binding=deepcopy(envelope['binding']),**changes)
        value.pop('attestation',None)
        value['attestation']=sign(value,'independent-assessor')
        envelope['derived_criteria'][index]=write_file(folder,reference['path'],value)


def test_reviewer_names_hashes_or_imported_verifier_fields_are_not_authentication(tmp_path,bundle):
    envelope=fixture_record(tmp_path,bundle)
    envelope['authenticator']={'command':'DO-NOT-EXECUTE','trusted':True}
    resign_envelope(envelope)
    result=e.assess(tmp_path,envelope,bundle)
    assert result['authenticated'] is False
    assert result['state']=='hold'
    assert not e.assess(tmp_path,envelope,bundle,authenticator=lambda a,r:'True')['authenticated']


def test_envelope_and_resealed_record_cannot_cross_candidate_binding(tmp_path,bundle):
    envelope=fixture_record(tmp_path,bundle)
    wrong=deepcopy(envelope)
    wrong['binding']['candidate_id']='a'*64
    resign_envelope(wrong)
    with pytest.raises(ValueError,match='candidate|binding'):
        e.assess(tmp_path,wrong,bundle,authenticator=test_only_authenticator)
    record=e.parse(e.read_owned(tmp_path,envelope['record']))
    record['candidate_id']='b'*64
    envelope['record']=write_file(tmp_path,'record.json',reseal_record(record))
    resign_envelope(envelope)
    with pytest.raises(ValueError,match='binding'):
        e.assess(tmp_path,envelope,bundle,authenticator=test_only_authenticator)


def test_replaced_raw_bytes_with_resealed_receipt_have_invalid_external_claims(tmp_path,bundle):
    envelope=fixture_record(tmp_path,bundle)
    envelope['raw_files'][0]=write_file(tmp_path,'source.json',dict(replacement='Not the signed source'))
    result=e.assess(tmp_path,envelope,bundle,authenticator=test_only_authenticator)
    assert result['state']=='hold' and result['authenticated'] is False
    assert any('signature' in reason for reason in result['holds'])


def test_physical_raw_article_binding_cannot_be_relabelled_by_envelope_signatures(tmp_path,bundle):
    envelope=fixture_record(tmp_path,bundle,physical=True)
    reference=envelope['raw_files'][0]
    packet=e.parse(e.read_owned(tmp_path,reference))
    packet['binding']['candidate_id']='c'*64
    envelope['raw_files'][0]=write_file(tmp_path,reference['path'],packet)
    rewrite_derived(tmp_path,envelope)
    resign_envelope(envelope)
    with pytest.raises(ValueError,match='binding|article'):
        e.assess(tmp_path,envelope,bundle,authenticator=test_only_authenticator)


@pytest.mark.parametrize('start',[-2.,1000.])
def test_synchronised_sample_timebase_must_lie_inside_the_declared_execution(tmp_path,bundle,start):
    envelope=fixture_record(tmp_path,bundle,physical=True)
    reference=envelope['raw_files'][0]
    packet=e.parse(e.read_owned(tmp_path,reference))
    for index,row in enumerate(packet['samples']):
        row['time_s']=start+index
    envelope['raw_files'][0]=write_file(tmp_path,reference['path'],packet)
    rewrite_derived(tmp_path,envelope);resign_envelope(envelope)
    with pytest.raises(ValueError,match='time|duration|execution'):
        e.assess(tmp_path,envelope,bundle,authenticator=test_only_authenticator)


@pytest.mark.parametrize('field',['serials','material_batches'])
@pytest.mark.parametrize('value',['NOT-A-LIST',[''],['DUPLICATE','DUPLICATE']])
def test_physical_article_identity_lists_cannot_be_replaced_by_truthy_placeholders(tmp_path,bundle,field,value):
    envelope=fixture_record(tmp_path,bundle,physical=True)
    envelope['article'][field]=value
    for index,reference in enumerate(envelope['raw_files']):
        packet=e.parse(e.read_owned(tmp_path,reference));packet['article']=deepcopy(envelope['article'])
        envelope['raw_files'][index]=write_file(tmp_path,reference['path'],packet)
    rewrite_derived(tmp_path,envelope);resign_envelope(envelope)
    try:
        result=e.assess(tmp_path,envelope,bundle,authenticator=test_only_authenticator)
    except ValueError:
        pass
    else:
        assert result['state']=='hold' and not result['physical_protocol_screen_passed']


def test_missing_case_or_repetition_cannot_be_hidden_by_reissued_fixture_approvals(tmp_path,bundle):
    envelope=fixture_record(tmp_path,bundle,physical=True)
    envelope['raw_files']=envelope['raw_files'][:1]
    rewrite_derived(tmp_path,envelope);resign_envelope(envelope)
    result=e.assess(tmp_path,envelope,bundle,authenticator=test_only_authenticator)
    assert result['state']=='hold' and not result['physical_protocol_screen_passed']
    assert any('case/repetition' in reason for reason in result['holds'])


@pytest.mark.parametrize('change',['missing-calibration','expired-calibration','late-limit','late-procedure','same-witness','open-deviation'])
def test_incomplete_or_post_run_approvals_remain_hold(tmp_path,bundle,change):
    envelope=fixture_record(tmp_path,bundle,physical=True)
    if change=='missing-calibration':
        envelope['calibrations']=envelope['calibrations'][1:]
    elif change=='expired-calibration':
        row=envelope['calibrations'][0];row['valid_until']='2026-10-20T12:00:00Z'
        row['attestation']=sign({k:v for k,v in row.items() if k!='attestation'},'calibration-authority')
    elif change=='late-limit':
        row=envelope['approved_limits'][0];row['approved_at']='2026-10-22T00:00:00Z'
        row['attestation']=sign({k:v for k,v in row.items() if k!='attestation'},'limit-approver')
    elif change=='late-procedure':
        envelope['procedure']['approved_at']='2026-10-22T00:00:00Z'
        envelope['attestations']['procedure']=sign(envelope['procedure'],'procedure-approver')
    elif change=='open-deviation':
        envelope['deviations']=[dict(id='UNIT-TEST-NCR',state='open')]
    resign_envelope(envelope)
    if change=='same-witness':
        claim={k:v for k,v in envelope.items() if k not in ('attestations','attestation')}
        envelope['attestations']['reviewer']=sign(claim,'independent-reviewer',envelope['attestations']['producer']['subject_id'])
    result=e.assess(tmp_path,envelope,bundle,authenticator=test_only_authenticator)
    assert result['state']=='hold' and result['authenticated'] is False
    assert result['physical_protocol_screen_passed'] is False


@pytest.mark.parametrize('comparison,value,channel',[
    ('le',1000.0005,'installed_mass_kg'),('ge',.0495,'clearance_m'),
])
def test_uncertainty_guard_band_rejects_apparently_passing_observation(tmp_path,bundle,comparison,value,channel):
    envelope=fixture_record(tmp_path,bundle,physical=True)
    limit=next(r for r in envelope['approved_limits'] if r['channel']==channel)
    limit.update(comparison=comparison,value=value)
    limit['attestation']=sign({k:v for k,v in limit.items() if k!='attestation'},'limit-approver')
    resign_envelope(envelope)
    result=e.assess(tmp_path,envelope,bundle,authenticator=test_only_authenticator)
    assert result['state']=='failed' and not result['authenticated']
    assert any(not metric['passed'] for metric in result['metrics'] if metric['channel']==channel)
    assert all(result[key] is False for key in e.FLAGS)


def test_failed_prerequisite_is_failure_not_a_missing_record(tmp_path,bundle):
    envelope=fixture_record(tmp_path,bundle)
    row=envelope['prerequisites'][0];row['state']='failed'
    row['attestation']=sign({k:v for k,v in row.items() if k!='attestation'},'independent-assessor')
    resign_envelope(envelope)
    result=e.assess(tmp_path,envelope,bundle,authenticator=test_only_authenticator)
    assert result['state']=='failed' and result['failures']


@pytest.mark.parametrize('change',['incomplete-set','cross-candidate','wrong-protocol','missing-source'])
def test_prerequisites_require_complete_applicable_source_bound_dispositions(tmp_path,bundle,change):
    envelope=fixture_record(tmp_path,bundle,physical=True)
    if change=='incomplete-set':
        envelope['prerequisites']=envelope['prerequisites'][:1]
    else:
        row=envelope['prerequisites'][0]
        if change=='cross-candidate':
            row['binding']['candidate_id']='f'*64
        elif change=='wrong-protocol':
            row['protocol_id']='T05'
        else:
            row['source']['sha256']='0'*64
        row['attestation']=sign({k:v for k,v in row.items() if k!='attestation'},'independent-assessor')
    resign_envelope(envelope)
    try:
        result=e.assess(tmp_path,envelope,bundle,authenticator=test_only_authenticator)
    except ValueError:
        assert change!='incomplete-set'
    else:
        assert result['state']=='hold' and not result['physical_protocol_screen_passed']


@pytest.mark.parametrize('change',['omitted','failed','cross-candidate','pre-run-review'])
def test_derived_observable_review_is_bound_and_independent_of_scalar_limits(tmp_path,bundle,change):
    envelope=fixture_record(tmp_path,bundle,physical=True)
    if change=='omitted':
        envelope['derived_criteria']=[]
    else:
        reference=envelope['derived_criteria'][0]
        value=e.parse(e.read_owned(tmp_path,reference));value.pop('attestation')
        if change=='failed':
            value['conclusion']='failed'
        elif change=='cross-candidate':
            value['binding']['candidate_id']='e'*64
        else:
            value['reviewed_at']='2026-10-20T00:00:00Z'
        value['attestation']=sign(value,'independent-assessor')
        envelope['derived_criteria']=[write_file(tmp_path,reference['path'],value)]
    resign_envelope(envelope)
    try:
        result=e.assess(tmp_path,envelope,bundle,authenticator=test_only_authenticator)
    except ValueError:
        assert change in ('cross-candidate','pre-run-review')
    else:
        assert result['authenticated'] is False and not result['physical_protocol_screen_passed']
        assert result['state']==('failed' if change=='failed' else 'hold')


def test_duplicate_content_record_is_rejected_even_under_two_envelope_paths(tmp_path,bundle):
    envelope=fixture_record(tmp_path,bundle)
    references=[write_file(tmp_path,'envelope-'+str(i)+'.json',envelope) for i in range(2)]
    manifest=dict(schema='osr-wheel-LIM-input-manifest/1',binding=e.binding(bundle),envelopes=references)
    with pytest.raises(ValueError,match='Duplicate evidence record'):
        e.load(tmp_path,manifest,bundle,authenticator=test_only_authenticator)


def test_manifest_cannot_mix_bindings_or_duplicate_envelope_paths(tmp_path,bundle):
    envelope=fixture_record(tmp_path,bundle)
    reference=write_file(tmp_path,'envelope.json',envelope)
    manifest=dict(schema='osr-wheel-LIM-input-manifest/1',binding=e.binding(bundle),envelopes=[reference,reference])
    with pytest.raises(ValueError,match='Unique'):
        e.load(tmp_path,manifest,bundle,authenticator=test_only_authenticator)
    manifest['binding']['body_candidate_id']='d'*64
    manifest['envelopes']=[reference]
    with pytest.raises(ValueError,match='binding'):
        e.load(tmp_path,manifest,bundle,authenticator=test_only_authenticator)


def derived_only_journey_fixture(folder,bundle):
    """Typed T08 software fixture: dummy signatures do not prove a journey."""
    envelope=fixture_record(folder,bundle,physical=True)
    protocol=next(r for r in test_readiness.definitions()['protocols'] if r['id']=='T08')
    bound=e.binding(bundle)
    envelope['protocol_id']='T08'
    procedure_data=dict(schema='osr-wheel-LIM-approved-procedure/1',revision='UNIT-TEST-T08-1',
        protocol_id='T08',binding=bound,required_cases={'empty':2},criterion_channels={},
        required_prerequisites=list(PREREQUISITES),
        derived_observables=[r['observable'] for r in protocol['acceptance_criteria']])
    envelope['procedure']=dict(revision=procedure_data['revision'],protocol_id='T08',binding=bound,
        source=write_file(folder,'procedure-T08.json',procedure_data),approved_at='2026-10-20T00:00:00Z')
    envelope['attestations']['procedure']=sign(envelope['procedure'],'procedure-approver')
    for row in envelope['prerequisites']:
        row['protocol_id']='T08'
        row['attestation']=sign({k:v for k,v in row.items() if k!='attestation'},'independent-assessor')
    channels={r['name']:r['unit'] for r in protocol['measured_channels']}
    typed_source=write_file(folder,'event-source.json',dict(test_fixture_only=True))
    files=[]
    for rep in range(2):
        samples=[]
        for index,time in enumerate((0.,.5,1.)):
            row={name:(dict(event_id='UNIT-TEST-EVENT-'+name,state='held',source=typed_source)
                if unit=='typed event' else time if name=='time_s' else 0.) for name,unit in channels.items()}
            samples.append(row)
        files.append(write_file(folder,'T08-measured-'+str(rep)+'.json',
            dict(schema='osr-wheel-LIM-measurements/1',binding=bound,article=envelope['article'],
                 channels=channels,case_id='empty',repetition=rep,samples=samples)))
    envelope.update(raw_files=files,calibrations=[],channel_instruments={},approved_limits=[],derived_criteria=[])
    for channel,unit in channels.items():
        if channel=='time_s' or unit=='typed event':
            continue
        row=dict(channel=channel,unit=unit,binding=bound,protocol_id='T08',expanded_uncertainty=.001,
            coverage_factor=2.,instrument_serial='UNIT-TEST-INSTRUMENT',
            certificate=write_file(folder,'T08-cert-'+channel+'.json',dict(test_fixture_only=True)),
            range=[-100000.,100000.],valid_from='2026-10-20T00:00:00Z',valid_until='2026-10-22T00:00:00Z')
        row['attestation']=sign(row,'calibration-authority');envelope['calibrations'].append(row)
        envelope['channel_instruments'][channel]=row['instrument_serial']
    for criterion in protocol['acceptance_criteria']:
        review=dict(schema='osr-wheel-LIM-derived-criterion/1',binding=bound,
            observable=criterion['observable'],unit=criterion['unit'],article=envelope['article'],
            raw_files=files,procedure_sha256=envelope['procedure']['source']['sha256'],
            conclusion='passed',reviewed_at='2026-10-21T00:02:00Z',test_fixture_only=True)
        review['attestation']=sign(review,'independent-assessor')
        envelope['derived_criteria'].append(write_file(folder,'T08-derived-'+criterion['observable']+'.json',review))
    return resign_envelope(envelope)


def test_all_derived_journey_protocol_does_not_require_invented_scalar_limits(tmp_path,bundle):
    envelope=derived_only_journey_fixture(tmp_path,bundle)
    result=e.assess(tmp_path,envelope,bundle,authenticator=test_only_authenticator)
    assert result['state']=='authenticated-for-declared-scope' and result['physical_protocol_screen_passed']
    assert all(result[key] is False for key in e.FLAGS)


def test_typed_journey_events_must_resolve_actual_owned_source_bytes(tmp_path,bundle):
    envelope=derived_only_journey_fixture(tmp_path,bundle)
    packet=e.parse(e.read_owned(tmp_path,envelope['raw_files'][0]))
    packet['samples'][0]['door_interlock']['source']['sha256']='0'*64
    envelope['raw_files'][0]=write_file(tmp_path,envelope['raw_files'][0]['path'],packet)
    rewrite_derived(tmp_path,envelope);resign_envelope(envelope)
    with pytest.raises(ValueError,match='bytes|size'):
        e.assess(tmp_path,envelope,bundle,authenticator=test_only_authenticator)
