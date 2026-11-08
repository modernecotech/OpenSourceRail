"""Offline native-v2 boundaries; no containers, apps or physical evidence."""
from copy import deepcopy
import gzip
from importlib.util import spec_from_file_location,module_from_spec
import json
from pathlib import Path
import sys
import pytest
from engineering.pilot_delivery import review

ROOT=Path(__file__).resolve().parents[1]
FIXTURE=ROOT/'tools/automation/native-v06'
sys.path.insert(0,str(FIXTURE))
import candidate_contracts as c


@pytest.fixture(scope='module')
def source(tmp_path_factory):
    path=tmp_path_factory.mktemp('candidate-fixture')
    proposal=ROOT/'docs/design-engine/reconciled-pilot-bogie-detail/delivery/proposal.json.gz'
    value=json.loads(gzip.decompress(proposal.read_bytes()))
    spec=spec_from_file_location('native_candidate_test_helpers',Path(__file__).with_name('test_pilot_delivery_review.py'))
    helper=module_from_spec(spec);spec.loader.exec_module(helper)
    pack=helper.pack(path,value);out=path/'export';review.export_review_pack(pack,path,out)
    input_value=c.load_input(ROOT,out,proposal,value['items'][0]['id'])
    return input_value,out,proposal


def reseal(value):
    value['input_id']=c.digest({k:v for k,v in value.items() if k!='input_id'});return value


def test_native_v2_uses_actual_source_price_component_and_partial_documents(source):
    value,out,proposal=source
    assert c.validate_input(value)==value and c.load_input(ROOT,out,proposal,value['component_id'])==value
    assert not value['review_pack']['coverage']['complete']
    assert value['review_pack']['components'][0]['stock_lines'][0]['rate']!=1
    context=c.project_context(value,project='DISPOSABLE-P',company='DISPOSABLE-C')
    assert context['identities']==value['identities'] and context['source_parts']==value['source_context']['source_parts']
    assert context['project']=='DISPOSABLE-P' and context['sha256']!=value['source_context']['sha256']
    assert all(context[k] is False for k in c.FLAGS)


@pytest.mark.parametrize('attack',['component','source','authority','candidate','coverage','context'])
def test_native_v2_rejects_source_or_coverage_spoofing_even_if_input_resealed(source,attack):
    value=deepcopy(source[0])
    if attack=='component':value['component_id']='invented'
    elif attack=='source':value['source_occurrence']['quantity_per_train']+=1
    elif attack=='authority':value['physical_accepted']=True
    elif attack=='candidate':value['identities']['candidate_id']='0'*64
    elif attack=='coverage':value['artifact_inventory']=[]
    else:value['source_context']['company']='changed'
    with pytest.raises(ValueError):c.validate_input(reseal(value))


def test_candidate_fixture_requires_all_explicit_selection_arguments_and_never_changes_v1_default(source,monkeypatch):
    spec=spec_from_file_location('native_runner_v2_test',ROOT/'tools/automation/v06-platform-native.py')
    runner=module_from_spec(spec);spec.loader.exec_module(runner)
    monkeypatch.setattr(runner,'invoke',lambda *a,**kw:(_ for _ in ()).throw(AssertionError('No process/service expected')))
    with pytest.raises(ValueError):runner.campaign_input(source[1],None,None)
    assert runner.campaign_input()['schema']=='osr-v06-platform-fixture/1'
    value=runner.campaign_input(source[1],source[2],source[0]['component_id'])
    assert value['schema']=='osr-v06-platform-fixture/2'


def test_no_fabricated_success_receipt_or_whole_train_promotion(source):
    value=source[0]
    result=dict(schema='osr-v06-native-platform-result/2',execution='planned',input_id=value['input_id'],source_sha256={},
        identities=value['identities'],checks={k:True for k in c.REQUIRED},uncovered=[],cleanup={'verified':True},**c.FLAGS)
    with pytest.raises(ValueError,match='executed'):c.verify_result(result,value,{})
    result['execution']='executed';result['document_coverage']={'complete':True}
    with pytest.raises(ValueError,match='Partial'):c.verify_result(result,value,{})


def test_changed_artifact_bytes_refuse_before_native_input_is_built(source,tmp_path):
    import shutil
    value,out,proposal=source;copy=tmp_path/'changed';shutil.copytree(out,copy)
    first=value['artifact_inventory'][0]['path'];(copy/first).write_bytes(b'changed')
    with pytest.raises(ValueError):c.load_input(ROOT,copy,proposal,value['component_id'])
