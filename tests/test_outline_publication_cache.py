from copy import deepcopy
from hashlib import sha256
import json
import os
from pathlib import Path

import pytest

from engineering.outline import publication_cache as cache
from engineering.outline.completion_publication import PUBLICATION


@pytest.fixture
def epoch(tmp_path,monkeypatch):
    cache.clear();folder=tmp_path/PUBLICATION;folder.mkdir(parents=True)
    source=tmp_path/'source.py';source.write_text('source=1\n')
    (folder/'summary.json').write_text('{"value":1}')
    (folder/'city.json').write_text('{"city":"fixture"}')
    manifest={'source_sha256':{'source.py':sha256(source.read_bytes()).hexdigest()},
              'files_sha256':{n:sha256((folder/n).read_bytes()).hexdigest() for n in ('summary.json','city.json')}}
    (folder/'manifest.json').write_text(json.dumps(manifest))
    calls=[]
    def verify(out,root):
        calls.append(True)
        for n,sha in manifest['source_sha256'].items():
            if sha256((Path(root)/n).read_bytes()).hexdigest()!=sha:raise ValueError('source changed')
        for n,sha in manifest['files_sha256'].items():
            if sha256((Path(out)/n).read_bytes()).hexdigest()!=sha:raise ValueError('payload changed')
        return deepcopy(manifest),json.loads((folder/'summary.json').read_bytes())
    monkeypatch.setattr(cache.completion_publication,'verify',verify)
    return tmp_path,folder,calls


def test_verified_epoch_is_reused_but_returned_records_are_independent(epoch):
    root,_,calls=epoch
    m,c=cache.verified(root);c['value']=999;m['files_sha256'].clear()
    assert cache.verified(root)[1]['value']==1
    assert cache.json_member('city.json',root)=={'city':'fixture'}
    assert len(calls)==1


def test_same_size_payload_edit_with_restored_mtime_invalidates_cache(epoch):
    root,folder,calls=epoch;cache.verified(root)
    path=folder/'city.json';before=path.stat();path.write_bytes(path.read_bytes().replace(b'fixture',b'changed'))
    os.utime(path,ns=(before.st_atime_ns,before.st_mtime_ns))
    with pytest.raises(ValueError,match='payload changed'):cache.member('city.json',root)
    assert len(calls)==2


def test_source_edit_invalidates_a_warm_epoch(epoch):
    root,_,calls=epoch;cache.verified(root);(root/'source.py').write_text('source=2\n')
    with pytest.raises(ValueError,match='source changed'):cache.verified(root)
    assert len(calls)==2


def test_unknown_member_and_symlink_refused(epoch):
    root,folder,_=epoch;cache.verified(root)
    with pytest.raises(ValueError,match='Known published'):cache.member('../outside',root)
    (folder/'city.json').unlink();(folder/'city.json').symlink_to(root/'source.py')
    with pytest.raises(ValueError,match='Linked'):cache.member('city.json',root)


def test_unverified_manifest_cannot_stat_outside_root(epoch):
    root,folder,_=epoch;m=json.loads((folder/'manifest.json').read_bytes())
    m['source_sha256']['../outside']='0'*64;(folder/'manifest.json').write_text(json.dumps(m))
    with pytest.raises(ValueError,match='Repository-relative'):cache.verified(root)
