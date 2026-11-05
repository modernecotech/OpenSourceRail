"""Compact native epochs survive cleanup without becoming new solver results."""
import io
import json
import shutil
import tarfile

import pytest

from engineering.design_search import architecture_publication as publication


def test_shallow_reference_fetch_needs_a_visible_ref(tmp_path):
    """An object fetched before another FETCH_HEAD must remain discoverable."""
    import subprocess
    from hashlib import sha256
    from engineering.station_rail.retired_station_reference import COMMIT
    git=lambda *args:subprocess.check_output(['git',*args],cwd=publication.ROOT,text=True).strip()
    head=git('rev-parse','HEAD')
    objects=git('rev-parse','--git-path','objects')
    if not publication.Path(objects).is_absolute():objects=str((publication.ROOT/objects).resolve())
    subprocess.run(['git','init',str(tmp_path)],check=True,capture_output=True)
    (tmp_path/'.git/objects/info/alternates').write_text(objects+'\n')
    (tmp_path/'.git/shallow').write_text(head+'\n'+COMMIT+'\n')
    subprocess.run(['git','update-ref','refs/heads/main',head],cwd=tmp_path,check=True)
    name='engineering/station_rail/brief.toml'
    raw=subprocess.check_output(['git','show',COMMIT+':'+name],cwd=publication.ROOT)
    wanted=sha256(raw).hexdigest()
    with pytest.raises(ValueError,match='Historical source bytes unavailable'):
        publication._source_bytes(tmp_path,name,wanted)
    subprocess.run(['git','update-ref','refs/osr/retired-station-reference',COMMIT],cwd=tmp_path,check=True)
    assert publication._source_bytes(tmp_path,name,wanted)==(raw,False)


@pytest.fixture
def prior(tmp_path):
    target=tmp_path/'prior'
    shutil.copytree(publication.ROOT/publication.OUTPUT,target)
    return target


def _reseal_payload(folder):
    manifest=json.loads((folder/'manifest.json').read_bytes())
    manifest['files_sha256']={p.relative_to(folder).as_posix():publication.digest(p)
        for p in folder.rglob('*') if p.is_file() and p!=folder/'manifest.json'}
    manifest['manifest_id']=publication.identity({k:v for k,v in manifest.items() if k!='manifest_id'})
    (folder/'manifest.json').write_bytes(publication.encoded(manifest))


def test_exact_thirteen_archives_and_original_dispositions_carry_forward(tmp_path):
    previous=publication.ROOT/publication.OUTPUT
    out=tmp_path/'next'
    rows,bindings,snapshots=publication.carry_native_packages(previous,out)
    original=json.loads((previous/'native-index.json').read_bytes())
    assert rows==original
    assert len(rows)==13 and {r['name'] for r in rows}==publication.NATIVE_NAMES
    assert all((out/r['archive']).read_bytes()==(previous/r['archive']).read_bytes() for r in rows)
    assert next(r for r in rows if r['name']=='joint-smoke-r1')['original_manifest_absent'] is True
    for h,record in snapshots.items():
        assert publication.digest(out/record['artifact'])==h
    for name,h in bindings.items():
        assert publication.digest(publication.ROOT/name)==h
    assert any('failed' in str(r['raw_result']).lower() or 'parse_error' in r['raw_result'] for r in rows)


def test_tampered_archive_refuses_copy(prior,tmp_path):
    row=json.loads((prior/'native-index.json').read_bytes())[0]
    path=prior/row['archive'];path.write_bytes(path.read_bytes()+b'changed')
    with pytest.raises(ValueError,match='publication payload differs'):
        publication.carry_native_packages(prior,tmp_path/'next')
    assert not (tmp_path/'next').exists()


def test_resealed_historical_source_still_requires_original_hash(prior,tmp_path):
    record=next(iter(json.loads((prior/'historical-source-index.json').read_bytes()).values()))
    (prior/record['artifact']).write_bytes(b'modified original producer')
    _reseal_payload(prior)
    with pytest.raises(ValueError,match='Historical producer snapshot differs'):
        publication.carry_native_packages(prior,tmp_path/'next')


def test_resealed_omitted_field_index_must_match_raw_receipt(prior,tmp_path):
    row=json.loads((prior/'native-index.json').read_bytes())[0]
    path=prior/row['archive']
    with tarfile.open(path,'r:gz') as tar:
        entries={m.name:tar.extractfile(m).read() for m in tar.getmembers()}
    index=json.loads(entries['archive-index.json'])
    key=next(iter(index['omitted_sha256']));index['omitted_sha256'][key]='0'*64
    entries['archive-index.json']=publication.encoded(index)
    with tarfile.open(path,'w:gz') as tar:
        for name,raw in entries.items():
            member=tarfile.TarInfo(name);member.size=len(raw);tar.addfile(member,io.BytesIO(raw))
    _reseal_payload(prior)
    with pytest.raises(ValueError,match='raw receipt coverage differs'):
        publication.carry_native_packages(prior,tmp_path/'next')


def test_missing_matching_interruption_preserves_previous_publication(prior,tmp_path,monkeypatch):
    before={p.relative_to(prior):p.read_bytes() for p in prior.rglob('*') if p.is_file()}
    monkeypatch.setattr(publication.engine,'evaluate_campaign',lambda root:dict(state='complete',contract_id='a'*64))
    with pytest.raises(ValueError,match='Matching-source interruption'):
        publication.build(root=tmp_path,output=prior)
    assert {p.relative_to(prior):p.read_bytes() for p in prior.rglob('*') if p.is_file()}==before
    assert not list(tmp_path.glob('.osr-architecture-*'))


def test_staged_failure_does_not_replace_current_packet(prior,tmp_path,monkeypatch):
    before=publication.digest(prior/'manifest.json')
    monkeypatch.setattr(publication,'_publication_inputs',lambda root:({},{}))
    def fail(root,out,value,first,previous):
        (out/'partial').write_text('unverified staging output')
        raise ValueError('staged verification failed')
    monkeypatch.setattr(publication,'_build_stage',fail)
    with pytest.raises(ValueError,match='staged verification failed'):
        publication.build(root=tmp_path,output=prior)
    assert publication.digest(prior/'manifest.json')==before
    assert not list(tmp_path.glob('.osr-architecture-*'))
