"""Native publication contracts use mocked checks, never fabricated physics."""
from copy import deepcopy
import gzip
import io
import json
import tarfile
import pytest

from engineering.railway_progress import methods,propulsion,structural_review,identity,digest,encoded,FLAGS


@pytest.fixture
def publication(tmp_path,monkeypatch):
    package=tmp_path/'MOCK-NOT-EXECUTED';package.mkdir()
    payload=dict(mock=True,physical_accepted=False,evaluation_id='a'*64)
    (package/'result.json').write_bytes(encoded(payload));host=dict(current='original-host')
    def check(folder,kind,root):
        value=json.loads((folder/'result.json').read_bytes())
        assert kind=='motor'
        return dict(verified=True,evaluation_id=value['evaluation_id'],recorded_tool_identity=dict(python='recorded'),
            current_tool_identity=host['current'],toolchain_matches_current=host['current']=='original-host',
            native_reuse_eligible=host['current']=='original-host',numerical_replayed=False,physical_accepted=False)
    monkeypatch.setattr(methods,'_check',check)
    folder=tmp_path/'publication';value=methods.publish([('control','motor',package)],folder)
    return folder,value,host,package


def reseal(folder,mutation):
    path=folder/'native-methods.json';value=json.loads(path.read_bytes());mutation(value)
    value['publication_id']=identity({k:v for k,v in value.items() if k!='publication_id'})
    path.write_bytes(encoded(value))


def test_real_dispatchers_always_request_recorded_integrity_without_native_reexecution(tmp_path,monkeypatch):
    calls=[]
    def check(folder,**kwargs):calls.append(kwargs);return dict(verified=True)
    monkeypatch.setattr(propulsion,'verify',check);monkeypatch.setattr(structural_review,'verify',check)
    methods._check(tmp_path,'motor',tmp_path);methods._check(tmp_path,'structure',tmp_path)
    assert len(calls)==2 and all(c['require_current_tool'] is False for c in calls)
    with pytest.raises(ValueError):methods._check(tmp_path,'invented-kind',tmp_path)


def test_portable_reopening_does_not_relabel_recorded_tool_as_current_tool(publication):
    folder,value,host,_=publication;host['current']='different-reader-host'
    actual=methods.verify(folder)
    assert actual['verified'] and actual['packages']==1 and not actual['physical_correlation']
    assert all(actual[k] is False for k in FLAGS)
    assert 'no new independent' in value['verification_scope']
    assert value['packages'][0]['validation']['numerical_replayed'] is False


@pytest.mark.parametrize('change',[
    lambda v:v['packages'].append(deepcopy(v['packages'][0])),
    lambda v:v['packages'][0].update(name='../outside'),
    lambda v:v['packages'][0].update(kind='qualified-vehicle'),
])
def test_resealed_duplicate_or_invalid_package_inventory_is_refused(publication,change):
    folder,_,_,_=publication;reseal(folder,change)
    with pytest.raises(ValueError,match='inventory'):methods.verify(folder)


@pytest.mark.parametrize('change',[
    lambda v:v['packages'][0]['validation'].update(evaluation_id='f'*64),
    lambda v:v['packages'][0]['validation'].update(recorded_tool_identity=dict(python='invented')),
    lambda v:v['packages'][0]['validation'].update(physical_accepted=True),
    lambda v:v.update(motor_comparison=dict(approved_operating_map=True)),
])
def test_resealed_native_evidence_cannot_change_recorded_identity_scope_or_comparison(publication,change):
    folder,_,_,_=publication;reseal(folder,change)
    with pytest.raises(ValueError):methods.verify(folder)


@pytest.mark.parametrize('mode',['extra','traversal','symlink','duplicate'])
def test_actual_archive_members_must_be_exactly_the_declared_ordinary_inventory(publication,mode):
    folder,_,_,_=publication;path=folder/'native-methods.tar.gz'
    with tarfile.open(path,'r:gz') as old:
        item=old.getmembers()[0];raw=old.extractfile(item).read()
    data=io.BytesIO()
    with tarfile.open(fileobj=data,mode='w') as archive:
        altered=deepcopy(item)
        if mode=='traversal':altered.name='../escape'
        if mode=='symlink':altered.type=tarfile.SYMTYPE;altered.linkname='/tmp/unowned';altered.size=0
        archive.addfile(altered,io.BytesIO(raw) if altered.isfile() else None)
        if mode=='duplicate':archive.addfile(item,io.BytesIO(raw))
        if mode=='extra':
            extra=tarfile.TarInfo('extra.txt');extra.size=1;archive.addfile(extra,io.BytesIO(b'X'))
    path.write_bytes(gzip.compress(data.getvalue(),mtime=0))
    reseal(folder,lambda v:v['files_sha256'].update({'native-methods.tar.gz':digest(path)}))
    with pytest.raises(ValueError,match='inventory'):methods.verify(folder)


def test_publication_bounds_and_source_packages_are_preserved(publication,tmp_path):
    folder,_,_,package=publication
    before=(package/'result.json').read_bytes();methods.verify(folder)
    assert (package/'result.json').read_bytes()==before
    with pytest.raises(ValueError):methods.publish([],tmp_path/'empty')
    with pytest.raises(ValueError):methods.publish([('same','motor',package)]*2,tmp_path/'duplicate')
    with pytest.raises(ValueError):methods.publish([(str(i),'motor',package) for i in range(13)],tmp_path/'too-many')
