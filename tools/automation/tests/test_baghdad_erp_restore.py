"""Restore tooling must stay isolated and clean up after SQL loading failures."""
import gzip
import hashlib
import importlib.util
import subprocess
from pathlib import Path

import pytest

ROOT=Path(__file__).resolve().parents[3]
spec=importlib.util.spec_from_file_location('restore_probe',ROOT/'tools/automation/verify_baghdad_erp_restore.py')
restore=importlib.util.module_from_spec(spec);spec.loader.exec_module(restore)

@pytest.mark.parametrize('sql_failure',[False,True])
def test_restore_never_targets_live_database_and_removes_temporary_container(tmp_path,monkeypatch,sql_failure):
    backup=tmp_path/'backup.sql.gz';backup.write_bytes(gzip.compress(b'CREATE TABLE test (n INT);'))
    calls=[]
    def run(args,**kwargs):
        calls.append(args)
        if '--user=root' in args and 'restored' in args and '-i' in args and sql_failure:
            raise subprocess.CalledProcessError(1,args,stderr=b'isolated SQL load failed')
        return subprocess.CompletedProcess(args,0,b'',b'')
    monkeypatch.setattr(restore.subprocess,'run',run)
    expected={'records':{k:{'count':0,'sha256':hashlib.sha256(b'').hexdigest()} for k in restore.snapshot_queries()}}
    if sql_failure:
        with pytest.raises(subprocess.CalledProcessError):restore.verify(backup,expected)
    else:
        result=restore.verify(backup,expected)
        assert result['passed'] and result['removed'] and not result['source_database_modified']
    create=next(args for args in calls if args[:2]==['docker','run'])
    assert create[create.index('--network')+1]=='none' and '--publish' not in create and '-p' not in create
    name=create[create.index('--name')+1];assert name.startswith('osr-baghdad-restore-')
    for args in calls:
        if args[:2]==['docker','exec']:
            assert args[3 if args[2]=='-i' else 2]==name
    assert calls[-1]==['docker','rm','--force','--volumes',name]
