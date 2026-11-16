"""Active Arrow case/stage store, using the same Rust codec as campaign runs."""
import pytest

from engineering.design_search import case_node_store as store, railway_campaign as campaign
from engineering.station_rail.common import encoded


@pytest.fixture(autouse=True)
def codec_available():
    try:
        store._codec()
    except ValueError:
        pytest.skip('Build the Rust columnar case-node codec for this integration test')


def test_exact_case_round_trip_and_kind(tmp_path):
    path=store.path_for(tmp_path,'a'*64)
    value=dict(candidate_id='a'*64,evaluation_id='b'*64,row_id='c'*64,
               installed_mass_kg=None,trace=[-0.0,0.0,True,1,'🚆'])
    store.write(path,value,'case')
    assert store.read(path,'case')==value
    assert encoded(store.read(path,'case'))==encoded(value)
    assert not path.with_suffix('.parquet.pending').exists()
    with pytest.raises(ValueError,match='kind or payload digest'):
        store.read(path,'stage')
    with pytest.raises(ValueError,match='Fresh'):
        store.write(path,value,'case')


def test_completed_pending_is_validated_then_recovered(tmp_path):
    path=store.path_for(tmp_path,'b'*64)
    value=dict(candidate_id='b'*64,source_sha256={'producer':'c'*64},unknown=None)
    store.write(path,value,'stage')
    pending=path.with_suffix('.parquet.pending')
    path.rename(pending)
    seen=[]
    recovered=store.recover(path,'stage',lambda record:seen.append(record),maximum=store.MAX_CANONICAL_BYTES)
    assert recovered==value and seen==[value]
    assert store.read(path,'stage')==value
    assert not pending.exists()


def test_invalid_pending_is_retained_and_final_is_not_deleted(tmp_path):
    path=store.path_for(tmp_path,'c'*64)
    value={'candidate_id':'c'*64}
    store.write(path,value,'case')
    final=path.read_bytes()
    pending=path.with_suffix('.parquet.pending')
    pending.write_bytes(b'interrupted')
    assert store.read(path,'case')==value
    assert path.read_bytes()==final and pending.read_bytes()==b'interrupted'
    path.unlink()
    with pytest.raises(ValueError,match='Rust case-node codec rejected'):
        store.recover(path,'case',lambda record:None)
    assert pending.read_bytes()==b'interrupted' and not path.exists()


def test_pending_request_mismatch_is_not_published(tmp_path):
    path=store.path_for(tmp_path,'d'*64)
    value={'request':{'source_sha256':{'producer':'d'*64}}}
    store.write(path,value,'stage')
    pending=path.with_suffix('.parquet.pending')
    path.rename(pending)
    def reject(record):
        raise ValueError('source request differs')
    with pytest.raises(ValueError,match='source request differs'):
        store.recover(path,'stage',reject)
    assert pending.exists() and not path.exists()


def test_v2_state_rejects_legacy_case_file_but_accepts_other_host_codec(tmp_path,monkeypatch):
    epoch={'producer':'a'*64};contract='b'*64
    campaign._bind_state_source(tmp_path,contract,epoch)
    legacy=tmp_path/'cases/old.json';legacy.parent.mkdir();legacy.write_bytes(b'{}')
    with pytest.raises(ValueError,match='legacy or unexpected'):
        campaign._bind_state_source(tmp_path,contract,epoch)
    legacy.unlink()
    marker=(tmp_path/'source-contract.json').read_bytes()
    before=campaign.contract_identity({'example':True},epoch)
    monkeypatch.setattr(store,'codec_identity',lambda root=store.ROOT:{'osr-campaign-case-nodes':'0'*64})
    campaign._bind_state_source(tmp_path,contract,epoch)
    assert (tmp_path/'source-contract.json').read_bytes()==marker
    assert campaign.contract_identity({'example':True},epoch)==before
