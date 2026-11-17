"""Offline controls for latest-release resolution and bounded archive reads."""
import importlib.util
import sys
import types
from hashlib import sha256
from io import BytesIO
import json
from pathlib import Path
import tarfile

import pytest

SOURCE = Path(__file__).resolve().parents[1]/'toolchain_release.py'
SPEC = importlib.util.spec_from_file_location('toolchain_release_under_test', SOURCE)
release = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(release)


class _Response(BytesIO):
    def __init__(self, raw, status=200, headers=None):
        super().__init__(raw)
        self.status = status
        self.headers = headers or {}


def _opener(payloads):
    def open_request(request, timeout):
        value=payloads[request.full_url]
        if callable(value):
            value=value(request)
        return _Response(*value) if isinstance(value,tuple) else _Response(value)
    return open_request


def _release_payload(digest):
    return dict(tag_name='v1.2.3',draft=False,prerelease=False,
        immutable=False,published_at='2026-11-15T00:00:00Z',
        assets=[dict(name='tool-1.2.3-linux-x86_64.tar.gz',state='uploaded',
            digest='sha256:'+digest,size=5,id=42,
            browser_download_url='https://github.com/example/tool/releases/download/v1.2.3/tool-1.2.3-linux-x86_64.tar.gz')])


def test_latest_asset_seals_tag_commit_and_exact_asset():
    payloads={
        'https://api.github.com/repos/example/tool/releases/latest':json.dumps(_release_payload('a'*64)).encode(),
        'https://api.github.com/repos/example/tool/git/ref/tags/v1.2.3':json.dumps(dict(object=dict(type='commit',sha='b'*40))).encode(),
    }
    resolved=release.latest_asset('example/tool','tool-{version}-linux-x86_64.tar.gz',opener=_opener(payloads))
    assert resolved['version']=='v1.2.3'
    assert resolved['commit']=='b'*40
    assert resolved['asset_sha256']=='a'*64
    assert resolved['bytes']==5


def test_release_metadata_uses_actions_token_without_changing_release_identity(monkeypatch):
    monkeypatch.setenv('GITHUB_TOKEN','fixture-token')
    def authenticated(request):
        assert request.get_header('Authorization') == 'Bearer fixture-token'
        return json.dumps(_release_payload('a'*64)).encode()
    value=release._json('https://api.github.com/repos/example/tool/releases/latest',
                        opener=_opener({'https://api.github.com/repos/example/tool/releases/latest':authenticated}))
    assert value['tag_name']=='v1.2.3'


def test_latest_asset_rejects_unhashed_release():
    data=_release_payload('a'*64)
    data['assets'][0]['digest']=None
    payloads={'https://api.github.com/repos/example/tool/releases/latest':json.dumps(data).encode()}
    with pytest.raises(ValueError,match='digest'):
        release.latest_asset('example/tool','tool-{version}-linux-x86_64.tar.gz',opener=_opener(payloads))


def test_download_checks_bytes_and_keeps_bad_partial(tmp_path):
    raw=b'bytes'
    asset=dict(url='https://github.com/example/tool/releases/download/v1.2.3/file',
               bytes=len(raw),asset_sha256=sha256(raw).hexdigest())
    archive=tmp_path/'file'
    assert release.download_asset(asset,archive,opener=_opener({asset['url']:raw}))==archive
    assert archive.read_bytes()==raw
    bad=tmp_path/'bad'
    with pytest.raises(ValueError,match='checksum'):
        release.download_asset(asset,bad,opener=_opener({asset['url']:b'other'}))
    assert (tmp_path/'bad.partial').exists()


def test_download_resumes_only_exact_http_range(tmp_path):
    raw=b'complete'
    asset=dict(url='https://github.com/example/tool/releases/download/v1.2.3/file',
               bytes=len(raw),asset_sha256=sha256(raw).hexdigest())
    archive=tmp_path/'file'
    partial=tmp_path/'file.partial'
    partial.write_bytes(raw[:3])
    def answer(request):
        assert request.get_header('Range')=='bytes=3-'
        return raw[3:],206,{'Content-Range':'bytes 3-7/8'}
    assert release.download_asset(asset,archive,opener=_opener({asset['url']:answer}))==archive
    assert archive.read_bytes()==raw
    other=archive.with_name('other')
    other_partial=archive.with_name('other.partial')
    other_partial.write_bytes(raw[:3])
    with pytest.raises(ValueError,match='range'):
        release.download_asset(asset,other,
            opener=_opener({asset['url']:(raw[3:],200,{})}))
    assert other_partial.read_bytes()==raw[:3]


def test_tar_member_hash_is_streamed_and_exact(tmp_path):
    archive=tmp_path/'tool.tar.gz'
    with tarfile.open(archive,'w:gz') as tar:
        raw=b'executable'
        member=tarfile.TarInfo('tool/bin/tool-cli')
        member.size=len(raw)
        tar.addfile(member,BytesIO(raw))
    assert release.tar_member_sha256(archive,'tool/bin/tool-cli')==sha256(b'executable').hexdigest()
    with pytest.raises(ValueError,match='lacks expected'):
        release.tar_member_sha256(archive,'tool/bin/absent')


def test_native_install_uses_verified_resumable_download(tmp_path,monkeypatch):
    package=types.ModuleType('toolchain_native_test_pkg')
    package.__path__=[]
    package.FLAGS={}
    package.identity=lambda value:'unused'
    monkeypatch.setitem(sys.modules,package.__name__,package)
    source=Path(__file__).resolve().parents[1]/'design_search/craft_backends/native.py'
    spec=importlib.util.spec_from_file_location(package.__name__+'.native',source)
    native=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(native)
    pin=dict(directory='tool-v1.2.3',asset='tool.tar.gz',
             url='https://github.com/example/tool/file',bytes=5,asset_sha256='a'*64)
    monkeypatch.setattr(native,'pin',lambda name:pin)
    monkeypatch.setattr(native,'executable',lambda name,tool_root:tmp_path/'bin/tool-cli')
    calls=[]
    def download(value,path):
        calls.append((value,path))
        path.write_bytes(b'bytes')
    monkeypatch.setattr(native,'download_asset',download)
    (tmp_path/'tool-v1.2.3/dist').mkdir(parents=True)
    result=native.install('solidcraft',tmp_path,refresh=False)
    assert result['tool']=='solidcraft'
    assert calls==[(pin,tmp_path/'tool-v1.2.3/tool.tar.gz')]
