"""Portable archival contracts; only temporary synthetic geometry and packets."""
from copy import deepcopy
import json
from pathlib import Path

import pytest

from engineering.design_search import implicit_geometry as g
from engineering.design_search import implicit_geometry_publication as p
from engineering.station_rail.common import encoded,identity


def reseal(value,key):value[key]=identity({k:v for k,v in value.items() if k!=key})


@pytest.fixture
def made(tmp_path):
    state=tmp_path/'source';state.mkdir();out=tmp_path/'packet'
    candidate=g.generate([.4,.4,.4],.2,.45,material_family='research_steel')
    result,vtk=g.sample(candidate,[16]*3,density_kg_m3=7850.,minimum_feature_m=.08)
    (state/'candidate.json').write_bytes(encoded(candidate));(state/'evaluation.json').write_bytes(encoded(result));(state/'occupancy.vtk').write_bytes(vtk)
    manifest=p.publish(state,expected_evaluation_id=result['evaluation_id'],output=out)
    return dict(state=state,out=out,candidate=candidate,result=result,vtk=vtk,manifest=manifest)


def test_publication_preserves_original_bytes_and_replay_holds(made):
    out=made['out'];m=made['manifest'];r=p.verify(out,expected_manifest_id=m['manifest_id'])
    assert r['verified'] and r['evaluation_id']==made['result']['evaluation_id']
    assert r['candidate_id']==made['candidate']['candidate_id']
    assert r['recorded_environment']==made['result']['numerical_environment']
    assert not r['native_evaluator_reuse'] and not r['recorded_environment_independently_attested']
    assert all(r[k] is False for k in g.FLAGS)
    for name in p.INPUTS:assert (out/name).read_bytes()==(made['state']/name).read_bytes()
    assert set(x.name for x in out.iterdir())==set(p.PAYLOAD)|{'manifest.json'}
    text=(out/'README.md').read_text();assert 'ideal-arithmetic' in text and 'not native-evaluator reuse' in text


def test_replay_environment_is_observed_separately_without_changing_historical_record(made,monkeypatch):
    current=deepcopy(made['result']['numerical_environment']);current['python']='3.12.99'
    before=(made['out']/'result.json').read_bytes();monkeypatch.setattr(g,'_environment',lambda:deepcopy(current))
    result=p.verify(made['out'],expected_manifest_id=made['manifest']['manifest_id'])
    assert result['recorded_environment']==made['result']['numerical_environment']
    assert result['replay_environment']==current and not result['environments_identical']
    assert (made['out']/'result.json').read_bytes()==before


def test_missing_wrong_or_untrusted_expected_identity_rejected(made,tmp_path):
    with pytest.raises(ValueError,match='expected evaluation identity'):
        p.publish(made['state'],expected_evaluation_id='0'*64,output=tmp_path/'other')
    for invalid in (None,'x'*64,'0'*64):
        with pytest.raises(ValueError,match='pinned manifest identity'):p.verify(made['out'],expected_manifest_id=invalid)


def test_existing_packet_never_overwritten(made):
    before={x.name:x.read_bytes() for x in made['out'].iterdir()}
    with pytest.raises(ValueError,match='destination'):p.publish(made['state'],expected_evaluation_id=made['result']['evaluation_id'],output=made['out'])
    assert {x.name:x.read_bytes() for x in made['out'].iterdir()}==before


@pytest.mark.parametrize('file',p.PAYLOAD)
def test_changed_or_missing_payload_rejected(made,file):
    path=made['out']/file;before=path.read_bytes();path.write_bytes(before+b' ')
    with pytest.raises(ValueError):p.verify(made['out'],expected_manifest_id=made['manifest']['manifest_id'])
    path.unlink()
    with pytest.raises(ValueError):p.verify(made['out'],expected_manifest_id=made['manifest']['manifest_id'])


def test_extra_files_and_symlink_payload_are_rejected(made,tmp_path):
    out=made['out'];extra=out/'extra';extra.write_text('x')
    with pytest.raises(ValueError,match='inventory'):p.verify(out,expected_manifest_id=made['manifest']['manifest_id'])
    extra.unlink();path=out/'occupancy.vtk';actual=path.read_bytes();path.unlink();external=tmp_path/'external';external.write_bytes(actual);path.symlink_to(external)
    with pytest.raises(ValueError,match='Symlink'):p.verify(out,expected_manifest_id=made['manifest']['manifest_id'])


def test_source_and_output_symlink_or_overlapping_directory_rejected(made,tmp_path):
    link=tmp_path/'source-link';link.symlink_to(made['state'],target_is_directory=True)
    with pytest.raises(ValueError,match='Symlink'):p.publish(link,expected_evaluation_id=made['result']['evaluation_id'],output=tmp_path/'other')
    with pytest.raises(ValueError,match='separate'):p.publish(made['state'],expected_evaluation_id=made['result']['evaluation_id'],output=made['state']/'child')


@pytest.mark.parametrize('attack',['promotion','recorded-environment','source','candidate','evaluation-id'])
def test_resealing_forged_manifest_cannot_bypass_external_pin(made,attack):
    out=made['out'];manifest=json.loads((out/'manifest.json').read_bytes());record=json.loads((out/'result.json').read_bytes())
    if attack=='promotion':record['physical_accepted']=True
    elif attack=='recorded-environment':record['recorded_environment']['python']='3.12.99'
    elif attack=='source':record['source_sha256'][g.PRODUCER]='0'*64
    elif attack=='candidate':record['candidate_id']='0'*64
    else:record['evaluation_id']='0'*64
    reseal(record,'publication_id');(out/'result.json').write_bytes(encoded(record))
    manifest['publication_id']=record['publication_id'];manifest['files_sha256']['result.json']=p.sha256((out/'result.json').read_bytes()).hexdigest();reseal(manifest,'manifest_id');(out/'manifest.json').write_bytes(encoded(manifest))
    with pytest.raises(ValueError,match='pinned manifest identity'):p.verify(out,expected_manifest_id=made['manifest']['manifest_id'])
    with pytest.raises(ValueError):p.verify(out,expected_manifest_id=manifest['manifest_id'])


def test_forged_producer_environment_and_mixed_sample_are_rejected_before_publishing(made,tmp_path):
    state=made['state'];candidate=json.loads((state/'candidate.json').read_bytes());evaluation=json.loads((state/'evaluation.json').read_bytes());old=evaluation['evaluation_id']
    evaluation['numerical_environment']['python']='3.12.99';reseal(evaluation,'evaluation_id');(state/'evaluation.json').write_bytes(encoded(evaluation))
    with pytest.raises(ValueError,match='expected evaluation identity'):p.publish(state,expected_evaluation_id=old,output=tmp_path/'other')
    evaluation['numerical_environment']['python']='not-python';reseal(evaluation,'evaluation_id');(state/'evaluation.json').write_bytes(encoded(evaluation))
    with pytest.raises(ValueError,match='recorded numerical environment'):p.publish(state,expected_evaluation_id=evaluation['evaluation_id'],output=tmp_path/'other')
    (state/'evaluation.json').write_bytes(encoded(made['result']));candidate['candidate_id']='0'*64;reseal(candidate,'definition_id');(state/'candidate.json').write_bytes(encoded(candidate))
    with pytest.raises(ValueError):p.publish(state,expected_evaluation_id=old,output=tmp_path/'other')


def test_forged_source_rejected_even_if_new_evaluation_identity_provided(made,tmp_path):
    state=made['state'];evaluation=json.loads((state/'evaluation.json').read_bytes());evaluation['source_sha256'][g.PRODUCER]='0'*64
    reseal(evaluation,'evaluation_id');(state/'evaluation.json').write_bytes(encoded(evaluation))
    with pytest.raises(ValueError,match='geometry source differs'):p.publish(state,expected_evaluation_id=evaluation['evaluation_id'],output=tmp_path/'other')


def test_noncanonical_and_duplicate_json_rejected(made):
    out=made['out'];raw=(out/'manifest.json').read_bytes();(out/'manifest.json').write_bytes(raw+b' ')
    with pytest.raises(ValueError,match='Canonical'):p.verify(out,expected_manifest_id=made['manifest']['manifest_id'])
    with pytest.raises(ValueError,match='Duplicate'):p._json(b'{"a":1,"a":2}\n')
