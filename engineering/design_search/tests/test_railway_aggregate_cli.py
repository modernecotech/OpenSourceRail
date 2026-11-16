"""Current-source CLI uses a scoped, verified v2 parent path."""
from contextlib import contextmanager
from pathlib import Path

from engineering.development_baseline import entrypoint
from engineering.design_search import railway_publication, railway_refinement_current_verifier


def test_current_verifier_receives_scoped_v2_parent(tmp_path,monkeypatch,capsys):
    parent=tmp_path/'.aggregate-parent-result.json';parent.write_bytes(b'fixture')
    events=[]
    @contextmanager
    def scoped(root):
        events.append('enter')
        try:yield tmp_path,{},parent
        finally:
            events.append('exit')
            parent.unlink()
    monkeypatch.setattr(railway_publication,'current_context',scoped)
    monkeypatch.setattr(railway_refinement_current_verifier,'verify',
        lambda root,*,parent_result,candidate_id:events.append((Path(parent_result),candidate_id)) or {'verified':True})
    code=entrypoint.main(['design','railway','refine-current-verify','--parent-v2-current','--candidate-id','a'*64],root=tmp_path)
    assert code==0 and events==['enter',(parent,'a'*64),'exit'] and not parent.exists()
    assert '"verified": true' in capsys.readouterr().out


def test_historical_refinement_rejects_v2_parent_switch(tmp_path,capsys):
    code=entrypoint.main(['design','railway','refine','--parent-v2-current','--candidate-id','a'*64],root=tmp_path)
    assert code==3
    assert 'only for current-source refinement' in capsys.readouterr().out
