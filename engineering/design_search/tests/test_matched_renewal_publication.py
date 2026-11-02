from pathlib import Path
import pytest
from engineering.design_search import matched_renewal_publication as p


def fake_state(path):
    path.mkdir()
    for epoch,names in p.EPOCHS.items():
        d=path/epoch;d.mkdir()
        for name in names:(d/name).write_text(epoch+'/'+name)
    return path


def test_worker_epoch_inventory_rejects_missing_extra_and_symlink(tmp_path):
    state=fake_state(tmp_path/'state');raw=p._snapshot(state);assert len(raw)==sum(map(len,p.EPOCHS.values()))
    extra=state/'epoch-v5'/'extra';extra.write_text('x')
    with pytest.raises(ValueError,match='inventory'):p._snapshot(state)
    extra.unlink();target=state/'epoch-v5'/'worker.py';target.unlink();target.symlink_to(state/'epoch-v4'/'worker.py')
    with pytest.raises(ValueError,match='[Ss]ymlink|ordinary'):p._snapshot(state)


def setup_stub(tmp_path,monkeypatch):
    state=fake_state(tmp_path/'state');parent=tmp_path/'parent';parent.mkdir();target=tmp_path/'result'
    record={'source_sha256':{},'evaluation_id':'a'*64,'parent_publication_manifest_id':'b'*64,
        'topology_manifest_id':'c'*64,'flanged_span_manifest_id':'d'*64}
    execution={'execution_id':'e'*64,'runtime_observed_after_worker':{'python':'test'}}
    monkeypatch.setattr(p,'_replay',lambda *args:(record,execution))
    monkeypatch.setattr(p.prior,'_check',lambda *args:({},{}))
    monkeypatch.setattr(p.research.cost.base,'_source_check',lambda *args:None)
    common=dict(root=p.ROOT,parent_folder=parent,expected_parent_manifest_id='b'*64,expected_topology_manifest_id='c'*64,
        expected_flanged_manifest_id='d'*64,expected_request_id='f'*64,expected_evaluation_id='a'*64)
    return state,target,record,execution,common


def test_closed_publication_and_replay_reject_tampering(tmp_path,monkeypatch):
    state,target,record,execution,common=setup_stub(tmp_path,monkeypatch)
    m=p.publish(state,output=target,**common);result=p.verify(output=target,expected_manifest_id=m['manifest_id'],**common)
    assert result['verified'] and not result['physical_accepted'] and not result['whole_life_ranking_allowed']
    with pytest.raises(FileExistsError):p.publish(state,output=target,**common)
    with pytest.raises(ValueError,match='identity'):p.verify(output=target,expected_manifest_id='0'*64,**common)
    (target/'original/epoch-v3/worker.log').write_text('altered')
    with pytest.raises(ValueError,match='payload'):p.verify(output=target,expected_manifest_id=m['manifest_id'],**common)


def test_closed_inventory_rejects_extra_and_empty_directories(tmp_path,monkeypatch):
    state,target,_,_,common=setup_stub(tmp_path,monkeypatch);m=p.publish(state,output=target,**common)
    extra=target/'extra';extra.mkdir()
    with pytest.raises(ValueError,match='directory inventory'):p._check(target,m['manifest_id'])
    extra.rmdir();(target/'extra').write_text('x')
    with pytest.raises(ValueError,match='file inventory'):p._check(target,m['manifest_id'])


def test_changed_input_during_replay_prevents_publish(tmp_path,monkeypatch):
    state,target,record,execution,common=setup_stub(tmp_path,monkeypatch)
    def mutate(*args):
        (state/'epoch-v5/worker.log').write_text('changed while replaying')
        return record,execution
    monkeypatch.setattr(p,'_replay',mutate)
    with pytest.raises(ValueError,match='changed during replay'):p.publish(state,output=target,**common)
    assert not target.exists()


def test_replay_requires_identical_full_result(monkeypatch):
    monkeypatch.setattr(p,'_validate',lambda *args:({'x':1},{'execution_id':'e'}))
    monkeypatch.setattr(p.research,'compare',lambda *args,**kwargs:{'x':2})
    with pytest.raises(ValueError,match='replay differs'):
        p._replay(Path('/'),Path('/'),'a'*64,'b'*64,'c'*64,'d'*64,'e'*64,{})


def test_external_pins_must_be_sha256():
    with pytest.raises(ValueError,match='trusted SHA256'):
        p._validate({},Path('/'),Path('/'),'not-trusted','b'*64,'c'*64,'d'*64,'e'*64)
