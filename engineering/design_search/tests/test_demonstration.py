from copy import deepcopy
import pytest
from engineering.design_search import demonstration as demo, design_grammar, route_bundle


@pytest.fixture(scope='module')
def result():
    body=design_grammar.build(design_grammar.parameters())
    bundle=route_bundle.materialize(body,distance_m=1500.)
    return demo.evaluate(body,bundle,demo.specification())


def test_real_short_route_propagates_load_adversity_and_same_candidate_to_outputs(result):
    assert result['distance_m']==1500.
    assert {r['name'] for r in result['motion']}=={'empty','normal','crowd','adverse-normal'}
    cases={r['name']:r['result'] for r in result['motion']}
    assert all(v['candidate_id']==result['candidate_id'] for v in cases.values())
    assert all(v['scenario']['distance_m']==1500. for v in cases.values())
    assert cases['normal']['required_demand']!=cases['empty']['required_demand']
    assert cases['adverse-normal']['required_demand']!=cases['normal']['required_demand']
    assert result['civil']['candidate_id']==result['candidate_id']
    assert result['economics']['candidate_id']==result['candidate_id']
    assert result['economics']['whole_life_cost_USD'] is None


def test_absent_motor_and_fault_plants_never_become_executed_or_accepted(result):
    assert all(r['result']['forward_motion']['execution']=='not-run' for r in result['motion'])
    assert len(result['faults'])==3
    assert all(r['execution']=='not-run' for r in result['faults'])
    assert result['complete_installed_mass_kg'] is None
    assert all(result[k] is False for k in demo.FLAGS)
    assert result['next_experiments']['proposals']


def test_record_seal_detects_tampering_and_refuses_resealed_release(tmp_path):
    record=demo._seal(dict(output={'value':3},**demo.FLAGS))
    target=tmp_path/'record.json';demo._write(target,record)
    assert demo._read(target)==record
    record['output']['value']=4;demo._write(target,record)
    with pytest.raises(ValueError,match='Modified'):demo._read(target)
    record.pop('record_id');record['physical_accepted']=True
    demo._write(target,demo._seal(record))
    with pytest.raises(ValueError,match='acceptance'):demo._read(target)


def test_resealed_embedded_campaign_cannot_drop_required_faults():
    contract=dict(specification=demo.specification(),source_sha256=demo.sources())
    value=dict(contract=contract,contract_id=demo.identity(contract))
    demo._contract(value,demo.ROOT)
    value['contract']['specification']['faults']=[]
    value['contract_id']=demo.identity(value['contract'])
    with pytest.raises(ValueError,match='current campaign'):demo._contract(value,demo.ROOT)


def test_published_matrix_cannot_silently_drop_or_duplicate_bundle_requests():
    import gzip,json
    target=demo.ROOT/demo.OUTPUT
    value=json.loads(gzip.decompress((target/'cases.json.gz').read_bytes()))
    equipped=json.loads(gzip.decompress((target/'equipped.json.gz').read_bytes()))
    removed=value['rows'].pop()
    with pytest.raises(ValueError,match='complete disjoint'):demo._coverage(value,equipped,demo.ROOT)
    value['pending'].append(removed['request'])
    demo._coverage(value,equipped,demo.ROOT)  # Budget deferral stays explicit and resumable.
    value['pending'][-1]=value['rows'][0]['request']
    with pytest.raises(ValueError,match='complete disjoint'):demo._coverage(value,equipped,demo.ROOT)
