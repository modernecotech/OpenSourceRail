"""Disposable coordinator integration/forgery tests, never real qualification."""
from copy import deepcopy
from pathlib import Path
import gzip
import io
import json
import shutil
import tarfile

import pytest

from engineering.railway_completion import coordinator as c, evidence, domains
from engineering.railway_completion.tests import test_evidence as fixtures
from engineering.railway_twin import model, pipeline as parent
from engineering.station_rail.common import encoded, identity, digest


def read(path):
    raw=Path(path).read_bytes()
    return evidence.parse(gzip.decompress(raw) if str(path).endswith('.gz') else raw)


def write(path,value):
    raw=encoded(value)
    Path(path).write_bytes(gzip.compress(raw,mtime=0) if str(path).endswith('.gz') else raw)


def reseal(folder):
    manifest=read(folder/'manifest.json')
    manifest['files_sha256']=c._files(folder)
    manifest['manifest_id']=identity({k:v for k,v in manifest.items() if k!='manifest_id'})
    write(folder/'manifest.json',manifest)


@pytest.fixture(scope='module')
def package(tmp_path_factory):
    folder=tmp_path_factory.mktemp('completion-package')/'package'
    result=c.generate(folder)
    return folder,result


def clone(package,tmp_path):
    target=tmp_path/'tampered'
    shutil.copytree(package[0],target)
    return target


def test_empty_current_project_is_valid_but_explicitly_held_end_to_end(package):
    folder,result=package;report=read(folder/'report.json.gz')
    assert result['verified'] and result['authenticated_records']==0
    assert result['numerical_domains_supported']==result['admitted_force_maps']==result['numerical_arrivals']==0
    assert result['frontier_tasks']==19
    assert len(report['domain_results']['domains'])==5
    assert all(row['state']=='missing' for row in report['domain_results']['domains'].values())
    assert len(report['motion'])==4
    assert all(row['result']['forward_motion']['execution']=='not-run' for row in report['motion'])
    assert set(report['physical_protocol_records'])=={f'T{i:02}' for i in range(1,11)}
    assert all(not ids for ids in report['physical_protocol_records'].values())
    assert report['infrastructure_loads']['known_wayside_stock_weight_N']==pytest.approx(223773.6314,abs=1e-4)
    assert abs(report['infrastructure_loads']['force_residual_N'])<1e-4
    assert all(report[key] is False for key in c.FLAGS)


def test_strict_completion_returns_real_domain_journey_and_protocol_frontier(package):
    with pytest.raises(parent.IncompleteDesign) as caught:
        c.verify(package[0],require_complete=True)
    blockers=caught.value.blockers
    assert len(blockers)==19
    assert {row['kind'] for row in blockers}=={'engineering-input-or-design','force-driven-journey','authenticated-physical-programme'}
    assert all(row['state']!='passed' for row in blockers)


@pytest.mark.parametrize('mutation',[
    lambda report:report.update(engineering_complete=True),
    lambda report:report['domain_results']['domains']['installed-equipment'].update(physical_accepted=True),
    lambda report:report['infrastructure_loads'].update(known_wayside_stock_weight_N=0.),
    lambda report:report['infrastructure_loads']['supports'][0].update(known_dead_reaction_N=0.),
    lambda report:report['motion'][0]['result'].update(numerical_arrival_predicted=True),
    lambda report:report['physical_protocol_records']['T08'].append('a'*64),
])
def test_resealed_report_cannot_promote_flags_remove_loads_or_invent_completion(package,tmp_path,mutation):
    folder=clone(package,tmp_path);report=read(folder/'report.json.gz')
    mutation(report)
    report['evaluation_id']=identity({k:v for k,v in report.items() if k!='evaluation_id'})
    write(folder/'report.json.gz',report)
    manifest=read(folder/'manifest.json');manifest['evaluation_id']=report['evaluation_id']
    write(folder/'manifest.json',manifest);reseal(folder)
    with pytest.raises(ValueError,match='semantic|evaluation|candidate'):
        c.verify(folder)


def test_unexpected_resealed_payload_file_is_rejected(package,tmp_path):
    folder=clone(package,tmp_path)
    (folder/'unrequested.txt').write_text('This file is not a declared input or output.')
    reseal(folder)
    with pytest.raises(ValueError,match='inventory'):
        c.verify(folder)


def test_manifest_candidate_cannot_be_rebound_to_another_real_looking_id(package,tmp_path):
    folder=clone(package,tmp_path);manifest=read(folder/'manifest.json')
    manifest['candidate_id']='b'*64;write(folder/'manifest.json',manifest);reseal(folder)
    with pytest.raises(ValueError,match='candidate'):
        c.verify(folder)


@pytest.mark.parametrize('option,context',[('authenticator','authentication_context_id'),('artifact_verifier','verifier_context_id')])
def test_callbacks_require_explicit_trusted_application_context_identity(option,context):
    with pytest.raises(ValueError,match='context identity'):
        c.assess(**{option:lambda *args:True})
    with pytest.raises(ValueError,match='context identity'):
        c.assess(**{option:lambda *args:True,context:'not-a-content-identity'})


def test_changed_or_revoked_trust_context_prevents_cached_approval_reuse(package):
    with pytest.raises(ValueError,match='trust/replay context'):
        c.verify(package[0],authentication_context_id=identity('different-policy'))
    with pytest.raises(ValueError,match='trust/replay context'):
        c.verify(package[0],verifier_context_id=identity('different-replay-backend'))


def test_coordinator_selects_recorded_native_integrity_without_claiming_a_fresh_solver_run(tmp_path,monkeypatch):
    bundle=model.materialize()['bundle'];folder=tmp_path/'method-fixture';folder.mkdir()
    evaluation=identity('UNIT-TEST-NATIVE-RECORD-NOT-A-SOLVE')
    write(folder/'result.json',dict(evaluation_id=evaluation,request_id=identity('UNIT-TEST-REQUEST'),
        execution='completed',state='unit-test-fixture',trace=[]))
    write(folder/'input.json',dict(request=dict(bundle_id=bundle['candidate_id'],voltage_peak_V=0.,
        speed_m_s=0.,phase_direction=1)))
    calls=[];recorded=dict(python='UNIT-TEST-RECORDED-TOOL',python_sha256=identity('recorded-tool'))
    def verifier(path,**options):
        calls.append((Path(path),options))
        return dict(verified=True,recorded_tool_identity=recorded,
            current_tool_identity=dict(python='UNIT-TEST-DIFFERENT-READER'),toolchain_matches_current=False,
            require_current_tool=False,independent_execution_attempted=False,numerical_replay_executed=False,
            native_reuse_eligible=False,verification_scope='Recorded-tool archive integrity only; no solver executed')
    monkeypatch.setattr(c.motor,'verify',verifier)
    value=c.assess(motor_packages=[folder])
    assert len(calls)==1 and calls[0][1].get('require_current_tool') is False
    row=value['native_component_runs'][0]
    assert row['recorded_tool_identity']==recorded
    assert row['verification_mode']=='recorded-execution-integrity'
    assert row['numerical_replayed'] is False and row['current_tool_verified'] is False
    assert row['native_reuse_eligible'] is False
    assert 'current_tool_identity' not in row and 'toolchain_matches_current' not in row
    assert row['available_operating_map'] is False
    assert all(value[key] is False for key in c.FLAGS)


def quote_input(folder,bundle):
    """A signed test quote which must not become brake evidence."""
    envelope=fixtures.fixture_record(folder,bundle)
    record=domains.make_record(bundle,'independent-brakes',{})
    envelope['record']=fixtures.write_file(folder,'record.json',record)
    envelope.update(protocol_id='T10',provenance_kind='commercial-quote')
    procedure=evidence.parse(evidence.read_owned(folder,envelope['procedure']['source']))
    procedure['protocol_id']='T10'
    envelope['procedure'].update(protocol_id='T10',source=fixtures.write_file(folder,'procedure.json',procedure))
    envelope['attestations']['procedure']=fixtures.sign(envelope['procedure'],'procedure-approver')
    for row in envelope['prerequisites']:
        row['protocol_id']='T10'
        row['attestation']=fixtures.sign({k:v for k,v in row.items() if k!='attestation'},'independent-assessor')
    fixtures.resign_envelope(envelope)
    reference=fixtures.write_file(folder,'envelope.json',envelope)
    manifest=dict(schema='osr-wheel-LIM-input-manifest/1',binding=evidence.binding(bundle),envelopes=[reference])
    return manifest


def test_authenticated_quote_protocol_does_not_clear_brake_inputs(tmp_path):
    bundle=model.materialize()['bundle']
    manifest=quote_input(tmp_path,bundle)
    value=c.assess(input_root=tmp_path,input_manifest=manifest,
        authenticator=fixtures.test_only_authenticator,authentication_context_id=identity('UNIT-TEST-TRUST-CONTEXT'))
    assert len(value['assessments'])==1 and value['assessments'][0]['authenticated']
    assert value['assessments'][0]['protocol_id']=='T10'
    assert value['domain_results']['domains']['independent-brakes']['state']=='missing'
    assert value['domain_results']['numerical_domains_supported']==0
    assert not value['engineering_evidence_ready_for_independent_decision']
    assert all(value[key] is False for key in c.FLAGS)


def test_input_files_are_retained_and_revocation_is_reassessed(tmp_path):
    bundle=model.materialize()['bundle'];input_root=tmp_path/'external'
    input_root.mkdir();manifest=quote_input(input_root,bundle)
    context=identity('UNIT-TEST-TRUST-CONTEXT')
    package_root=tmp_path/'output'
    result=c.generate(package_root,input_root=input_root,input_manifest=manifest,
        authenticator=fixtures.test_only_authenticator,authentication_context_id=context)
    assert result['verified'] and result['authenticated_records']==1
    shutil.rmtree(input_root)
    assert c.verify(package_root,authenticator=fixtures.test_only_authenticator,authentication_context_id=context)['verified']
    with pytest.raises(ValueError,match='semantic'):
        c.verify(package_root,authenticator=lambda *args:False,authentication_context_id=context)


@pytest.fixture(scope='module')
def publication(package,tmp_path_factory):
    output=tmp_path_factory.mktemp('completion-publication')
    manifest=c.publish(package[0],output=output)
    return output,manifest


def test_disposable_publication_archive_replays_and_keeps_held_scope(publication):
    output,manifest=publication
    result=c.verify_publication(output=output)
    assert result['verified'] and result['frontier_tasks']==19
    assert result['publication_id']==manifest['publication_id']
    assert all(result[key] is False for key in c.FLAGS)


@pytest.mark.parametrize('change',['index','archive-name','archive-bytes','flag'])
def test_resealed_publication_index_cannot_relabel_archive_results(publication,tmp_path,change):
    source,original=publication;output=tmp_path/'pub';shutil.copytree(source,output)
    manifest=read(output/'manifest.json')
    if change=='index':manifest['validation']['numerical_domains_supported']=5
    elif change=='archive-name':manifest['archive']='../outside.tar.gz'
    elif change=='flag':manifest['physical_accepted']=True
    else:
        archive=output/manifest['archive'];archive.write_bytes(archive.read_bytes()+b'tamper')
    manifest['publication_id']=identity({k:v for k,v in manifest.items() if k!='publication_id'})
    write(output/'manifest.json',manifest)
    with pytest.raises(ValueError):c.verify_publication(output=output)


@pytest.mark.parametrize('name,kind',[('../escape.txt','file'),('/absolute.txt','file'),('link','symlink')])
def test_archive_rejects_traversal_absolute_paths_and_links(tmp_path,name,kind):
    buffer=io.BytesIO()
    with tarfile.open(fileobj=buffer,mode='w') as archive:
        item=tarfile.TarInfo(name)
        if kind=='symlink':item.type=tarfile.SYMTYPE;item.linkname='elsewhere'
        else:item.size=1
        archive.addfile(item,None if kind=='symlink' else io.BytesIO(b'x'))
    path=tmp_path/'bad.tar.gz';path.write_bytes(gzip.compress(buffer.getvalue(),mtime=0))
    with pytest.raises(ValueError,match='archive paths'):
        c.verify_archive(path)
