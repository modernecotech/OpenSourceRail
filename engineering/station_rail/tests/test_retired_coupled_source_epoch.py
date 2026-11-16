"""Journey C stays authenticated by pinned Git bytes, not current evaluators."""
import os
from pathlib import Path
import shutil
import subprocess
from types import SimpleNamespace

import pytest

from engineering.station_rail import retired_station_reference


def test_blobless_tree_keeps_unselected_bad_size_without_admitting_it(monkeypatch,tmp_path):
    reader=retired_station_reference
    commit='a'*40;missing='b'*40;present='c'*40
    def git(_root,args):
        if args[0]=='rev-parse':return (commit+'\n').encode()
        assert args[0]=='ls-tree'
        return (f'100644 blob {missing} BAD\tunselected.py\0'
                f'100644 blob {present} 4\tselected.py\0').encode()
    monkeypatch.setattr(reader,'_git',git)
    entries=reader._tree(tmp_path,commit)
    assert entries['unselected.py']==dict(git_blob=missing,size_bytes=-1)
    assert entries['selected.py']==dict(git_blob=present,size_bytes=4)
    with pytest.raises(reader.RetiredReferenceHold,match='Selected retired Git blob unavailable'):
        reader._blob(tmp_path,entries,'unselected.py')


def test_coupled_prefetch_fetches_selected_bad_sizes_then_checks_budget(monkeypatch,tmp_path):
    reader=retired_station_reference
    prefix='docs/design-engine/coupled-railway/'
    manifest=dict(schema='test',source_sha256={'source.py':'0'*64},
        files_sha256={'result.json':'1'*64})
    manifest['manifest_id']=reader.identity(manifest)
    path=tmp_path/prefix/'manifest.json';path.parent.mkdir(parents=True)
    path.write_bytes(reader.encoded(manifest))
    monkeypatch.setattr(reader,'COUPLED_PACKET_MANIFEST_ID',manifest['manifest_id'])
    selected=('source.py',prefix+'result.json',prefix+'manifest.json')
    oids={name:f'{index+1:040x}' for index,name in enumerate(selected)}
    calls=[0]
    def tree(_root,_commit):
        calls[0]+=1
        size=-1 if calls[0]==1 else 16
        return {**{name:dict(git_blob=oid,size_bytes=size) for name,oid in oids.items()},
            'unselected.py':dict(git_blob='f'*40,size_bytes=-1)}
    fetched=[]
    def run(command,**kwargs):
        if command[-3:-1]==['cat-file','-e']:return SimpleNamespace(returncode=1)
        assert command[-3:-1]==['cat-file','blob']
        fetched.append(command[-1]);return SimpleNamespace(returncode=0)
    monkeypatch.setattr(reader,'_tree',tree)
    monkeypatch.setattr(reader.subprocess,'run',run)
    monkeypatch.setattr(reader,'_verify_blobs',lambda root,records,commit:None)
    result=reader.prefetch_coupled_blobs(tmp_path)
    assert calls[0]==2
    assert set(fetched)==set(oids.values())
    assert result['pinned_blob_count']==3 and result['prefetched_blobs']==3


def test_coupled_packet_is_historical_without_current_evaluator(monkeypatch):
    from engineering.design_search import railway_publication

    monkeypatch.setattr(railway_publication, "verify", lambda *a, **kw:
                        pytest.fail("A retired packet cannot call the current evaluator"))
    result = retired_station_reference.verify_coupled_packet()

    assert result["manifest_id"] == retired_station_reference.COUPLED_PACKET_MANIFEST_ID
    assert result["source_epoch"] == "historical"
    assert result["analytical_replay"] is False
    assert result["numerical_reexecuted"] is False
    assert result["current_evaluator_admission"] is False
    assert all(
        result[name] is False
        for name in (
            "physical_accepted",
            "engineering_accepted",
            "manufacturing_release",
            "operating_release",
        )
    )

    assert result["native_solver_jobs"] == 0


@pytest.fixture
def packet_copy(tmp_path):
    root = retired_station_reference.ROOT
    # Three bounded copies of the 96 MiB packet also work when the checkout
    # and pytest scratch are on different filesystems. Never share writable
    # inodes with the source evidence.
    git_dir = subprocess.check_output(['git', 'rev-parse', '--absolute-git-dir'],
                                      cwd=root, text=True).strip()
    (tmp_path / '.git').write_text('gitdir: ' + git_dir + '\n')
    packet = Path('docs/design-engine/coupled-railway')
    support = Path(retired_station_reference.COUPLED_SOURCE_EPOCH)
    shutil.copytree(root / packet, tmp_path / packet, copy_function=shutil.copy2)
    shutil.copytree(root / support, tmp_path / support, copy_function=shutil.copy2)
    return tmp_path


def replace(path, data):
    temporary = path.with_name(path.name + '.tampered')
    temporary.write_bytes(data)
    os.replace(temporary, path)


@pytest.mark.parametrize(('relative', 'message'), [
    ('docs/design-engine/coupled-railway/summary.json', 'payload differs'),
    ('docs/design-engine/coupled-railway/README.md', 'payload differs'),
    (retired_station_reference.COUPLED_SOURCE_EPOCH +
     '/source/engineering/station_rail/braking.py', 'historical braking source bytes differ'),
])
def test_historical_packet_rejects_tampering(packet_copy, relative, message):
    path = packet_copy / relative
    replace(path, path.read_bytes() + b'\n')
    with pytest.raises(retired_station_reference.RetiredReferenceHold, match=message):
        retired_station_reference.verify_coupled_packet(packet_copy)


def test_historical_packet_rejects_wrong_source_commit(monkeypatch):
    current_commit = subprocess.check_output(
        ['git', 'rev-parse', 'HEAD'], cwd=retired_station_reference.ROOT,
        text=True).strip()
    monkeypatch.setattr(retired_station_reference, 'COUPLED_PACKET_COMMIT',
                        current_commit)
    with pytest.raises(retired_station_reference.RetiredReferenceHold,
                       match='Retired Git source bytes differ'):
        retired_station_reference.verify_coupled_packet()


def test_explicit_prefetch_is_source_bound_and_offline_when_blobs_are_present():
    result = retired_station_reference.prefetch_coupled_blobs()
    assert result['commit'] == retired_station_reference.COUPLED_PACKET_COMMIT
    assert result['prefetched_blobs'] == 0
    assert result['pinned_blob_count'] > 50
    assert result['physical_accepted'] is False
