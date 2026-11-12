"""Native import custody is external, with read-only legacy discovery."""
from pathlib import Path
from types import SimpleNamespace
import gzip
import json

import pytest
from engineering.rustgis import adapter, revision
from engineering.station_rail.common import encoded


def test_default_store_is_external_root_scoped_state(tmp_path,monkeypatch):
    monkeypatch.delenv('OSR_RUSTGIS_IMPORT_STORE',raising=False)
    monkeypatch.setenv('XDG_STATE_HOME',str(tmp_path/'state'))
    a=revision.import_store(tmp_path/'source-a');b=revision.import_store(tmp_path/'source-b')
    assert a!=b and a.parent==tmp_path/'state/opensourcerail/rustgis-imports'
    assert not a.exists()
    monkeypatch.setenv('OSR_RUSTGIS_IMPORT_STORE',str(tmp_path/'explicit'))
    assert revision.import_store(tmp_path/'source-a')==tmp_path/'explicit'
    assert revision.import_store(tmp_path/'source-a',tmp_path/'override')==tmp_path/'override'


@pytest.mark.parametrize('kind',['inside','ancestor','relative','symlink-parent','symlink-leaf','file'])
def test_store_refuses_source_and_redirected_paths(tmp_path,kind):
    root=tmp_path/'source';root.mkdir()
    store=tmp_path/'imports'
    if kind=='inside':store=root/'build/imports'
    elif kind=='ancestor':store=tmp_path
    elif kind=='relative':store=Path('relative-imports')
    elif kind=='symlink-parent':
        (tmp_path/'link').symlink_to(root,target_is_directory=True);store=tmp_path/'link/imports'
    elif kind=='symlink-leaf':store.symlink_to(root,target_is_directory=True)
    else:store.write_text('not a directory')
    with pytest.raises(ValueError):revision.import_store(root,store)


def test_retained_legacy_lookup_does_not_change_receipt(tmp_path):
    root=tmp_path/'source';job='1'*32
    legacy=root/'build/rustgis-imports'/job;legacy.mkdir(parents=True)
    raw=b'{"retained":"original source epoch"}\n';(legacy/'manifest.json').write_bytes(raw)
    external=tmp_path/'imports'
    assert revision.import_directory(job,root=root,store=external)==legacy
    assert (legacy/'manifest.json').read_bytes()==raw and not external.exists()
    (external/job).mkdir(parents=True)
    with pytest.raises(ValueError,match='unambiguous'):
        revision.import_directory(job,root=root,store=external)


def test_retained_lookup_refuses_symlink(tmp_path):
    root=tmp_path/'source';root.mkdir();store=tmp_path/'imports';store.mkdir()
    (store/('a'*32)).symlink_to(root,target_is_directory=True)
    with pytest.raises(ValueError,match='Ordinary'):
        revision.import_directory('a'*32,root=root,store=store)


def test_study_input_uses_verified_service_store(tmp_path,monkeypatch):
    from engineering.outline import city_workflow,city_atlas_api
    from engineering.city_reports import maps
    root=tmp_path/'source';root.mkdir();job='a'*32
    folder=tmp_path/'external'/job/'artifacts';folder.mkdir(parents=True)
    workflow={'source_outline_evaluation_id':'b'*64}
    plan={'revision_sha256':'c'*64,'outline_context':{'seed':{'reference_candidate_ids':{'candidate_id':'d'*64}}}}
    (folder/'result.json.gz').write_bytes(gzip.compress(encoded(workflow),mtime=0))
    (folder/'planning.json').write_bytes(encoded(plan));(folder/'manifest.json').write_bytes(b'{}')
    checked=[]
    service=SimpleNamespace(root=root,status=lambda jid:{'state':'completed'},
        _job=lambda jid:folder.parent,_verify=lambda path:checked.append(path) or {'manifest_id':'e'*64})
    monkeypatch.setattr(city_atlas_api,'from_verified_study',lambda r,w:{'city':{'slug':'fixture'},'packet_id':'f'*64})
    monkeypatch.setattr(maps,'geojson_layers',lambda packet:{})
    packet,_,originals,_,manifest,binding=adapter.study_input(job,root=root,service=service)
    assert checked==[folder] and originals['sources/planning.json']==encoded(plan)
    assert binding['base_manifest_id']==manifest['manifest_id'] and binding['base_study_id']==job
    assert not (root/'build').exists()
    service.root=tmp_path/'other-source'
    with pytest.raises(ValueError,match='checkout differs'):
        adapter.study_input(job,root=root,service=service)


def test_import_api_reads_legacy_and_external_records(tmp_path,monkeypatch):
    from engineering.rustgis import api
    root=tmp_path/'source';root.mkdir();store=tmp_path/'external';job='a'*32
    folder=store/job;folder.mkdir(parents=True);(folder/'comparison.json').write_bytes(b'{"source":"external"}')
    class Handler:
        command='GET';path='/api/rustgis/imports/'+job+'/comparison.json'
        server=SimpleNamespace(rustgis_import_store=store)
        def respond(self,*args):self.response=args
    h=Handler();h.root=root
    monkeypatch.setattr(api,'_loopback',lambda *a,**k:True)
    assert api.handle_api(h) and h.response==(200,b'{"source":"external"}','application/json')
    folder.rename(root/'legacy-temp')
    legacy=root/'build/rustgis-imports'/job;legacy.parent.mkdir(parents=True)
    (root/'legacy-temp').rename(legacy)
    assert api.handle_api(h) and h.response[0]==200


def test_direct_verification_refuses_symlinked_folder(tmp_path):
    actual=tmp_path/'actual';actual.mkdir();link=tmp_path/'link'
    link.symlink_to(actual,target_is_directory=True)
    with pytest.raises(ValueError,match='Ordinary'):
        revision.verify_import(link,root=tmp_path/'source')


def test_authoritative_study_base_comes_from_verified_originals(tmp_path,monkeypatch):
    import zipfile
    root=tmp_path/'source';root.mkdir();job='a'*32
    binding={'kind':'study','base_study_id':job};base={'retained':'verified planning base'}
    packet={'city':{'slug':'fixture'},'packet_id':'b'*64}
    originals={'sources/planning.json':encoded(base)}
    manifest={'project':'fixture.rgis','revision_binding':binding}
    archive=tmp_path/'export.zip'
    with zipfile.ZipFile(archive,'w') as z:
        z.writestr('manifest.json',encoded(manifest));z.writestr('fixture.rgis',b'original project')
    monkeypatch.setattr(adapter,'study_input',lambda *a,**k:(packet,None,originals,{},None,binding))
    monkeypatch.setattr(adapter,'export_study',lambda *a,**k:{'archive':archive})
    result=revision.authoritative('fixture','b'*64,root=root,study_id=job,service=object())
    assert result==(base,binding,b'original project',manifest)
    assert not (root/'build').exists()
