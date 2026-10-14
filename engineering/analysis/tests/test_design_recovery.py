from pathlib import Path
import pytest
from engineering.design_engine.store import Store
from engineering.design_engine.recovery import checkpoint,restore
from engineering.analysis.tests.test_design_engine import minimal_request,sealed_attempt


def test_consistent_restart_restore_preserves_failed_attempts_and_corruption_fails(tmp_path):
    store=Store(tmp_path/'live');job=store.create(minimal_request());sealed_attempt(store,job)
    backup=tmp_path/'backup';checkpoint(store,backup)
    result=restore(backup,tmp_path/'restored')
    assert result['restored_jobs']==1 and result['active_jobs_started']is False
    restored=Store(tmp_path/'restored');assert restored.get(job['id'])['status']=='failed'
    with pytest.raises(ValueError):restore(backup,tmp_path/'live')
    (backup/'runs'/job['id']/'request.json').write_text('corrupt')
    with pytest.raises(ValueError,match='corrupt'):restore(backup,tmp_path/'another')


def test_active_worker_cannot_be_checkpointed_as_quiescent(tmp_path):
    store=Store(tmp_path/'live');store.create(minimal_request())
    with pytest.raises(ValueError,match='quiescent'):checkpoint(store,tmp_path/'backup')
