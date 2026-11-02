from copy import deepcopy
import gzip
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import tarfile
from types import SimpleNamespace

import pytest

SCRIPT=Path(__file__).resolve().parents[1]/'sourced-ifc-reuse.py'
SPEC=importlib.util.spec_from_file_location('sourced_ifc_reuse',SCRIPT)
m=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(m)


def seal(value,key):
    value[key]=m.identity({k:v for k,v in value.items()if k!=key});return value


def write(path,value):
    path.parent.mkdir(parents=True,exist_ok=True);raw=m.encoded(value)
    path.write_bytes(gzip.compress(raw,mtime=0)if path.suffix=='.gz'else raw)


def archive(path,files):
    stream=io.BytesIO()
    with tarfile.open(fileobj=stream,mode='w',format=tarfile.USTAR_FORMAT)as t:
        for name,raw in files.items():
            info=tarfile.TarInfo(name);info.size=len(raw);info.mtime=0
            t.addfile(info,io.BytesIO(raw))
    path.write_bytes(gzip.compress(stream.getvalue(),mtime=0))


@pytest.fixture
def fixture(tmp_path,monkeypatch):
    root=tmp_path/'root';root.mkdir()
    (root/'narrow.py').write_text('same geometry');(root/'native.py').write_text('same IFC adapter')
    (root/'cost.py').write_text('new cost')
    narrow={'narrow.py':m.digest(root/'narrow.py')}
    old_epoch={**narrow,'cost.py':hashlib.sha256(b'old cost').hexdigest()}
    epoch={**narrow,'cost.py':m.digest(root/'cost.py')}
    old=tmp_path/'old';new=tmp_path/'new';original=tmp_path/'publication';original.mkdir()
    plan=[dict(vehicle_id=vid,case=i)for vid in m.VEHICLES for i in range(6)]
    calls=[];files={};rows=[]
    for state,source in ((old,old_epoch),(new,epoch)):
        state.mkdir();archive(state/'input-sources.tar.gz',{'narrow.py':b'same geometry','cost.py':b'old cost'if state==old else b'new cost'})
        cases=[]
        for req in plan:
            cases.append(dict(request=req,path='cases/'+m.identity(dict(request=req,source=source))+'.json.gz',
                candidate_id=m.identity(req),evaluation_id=m.identity(dict(req=req,source=source))))
        write(state/'latest.json',seal(dict(schema='osr-sourced-cell-run/1',source_sha256=source,cases=cases,pending=[],**m.FLAGS),'run_id'))
        for vid in m.VEHICLES:
            cid=m.identity(dict(vehicle=vid));registry=dict(candidate_id=cid,registry_id=m.identity(dict(registry=vid)))
            v=seal(dict(candidate_id=cid,vehicle_id=vid,registry=registry,source_sha256=narrow,geometry=dict(length=17),**m.FLAGS),'evaluation_id')
            write(state/'vehicles'/(vid+'.json.gz'),seal(dict(candidate_id=cid,vehicle=v,**m.FLAGS),'evaluation_id'))
    native_source=lambda v:{**v['source_sha256'],'native.py':m.digest(root/'native.py')}
    for vid in m.VEHICLES:
        v=m.read(old/'vehicles'/(vid+'.json.gz'))['vehicle'];raw=('IFC fixture '+vid).encode();files[vid+'.ifc']=raw
        receipt=seal(dict(schema='osr-reference-cell-ifc/1',candidate_id=v['candidate_id'],registry_id=v['registry']['registry_id'],
            source_sha256=native_source(v),file=vid+'.ifc',file_sha256=hashlib.sha256(raw).hexdigest(),
            reopened=dict(occurrences=5),complete_installed_geometry=False,**m.FLAGS),'receipt_id')
        files[vid+'.ifc.receipt.json']=m.encoded(receipt)
        validation=dict(verified=True,candidate_id=v['candidate_id'],receipt_id=receipt['receipt_id'],actual_reopened=True,native_reuse_eligible=False,**m.FLAGS)
        rows.append(dict(vehicle_id=vid,candidate_id=v['candidate_id'],registry_id=v['registry']['registry_id'],
            reopened=receipt['reopened'],validation=validation,files_sha256={n:hashlib.sha256(files[n]).hexdigest()for n in (vid+'.ifc',vid+'.ifc.receipt.json')}))
    archive(original/m.ARCHIVE,files)
    publication=seal(dict(schema='osr-sourced-vehicle-geometry/1',run_id=m.read(old/'latest.json')['run_id'],
        source_sha256=old_epoch,vehicles=rows,files_sha256={m.ARCHIVE:m.digest(original/m.ARCHIVE)},scope='Unqualified fixture primitives',**m.FLAGS),'publication_id')
    write(original/m.RECORD,publication)
    def reopen(v,path):
        calls.append(v['vehicle_id']);r=m.read(path.with_suffix('.ifc.receipt.json'))
        return dict(verified=True,candidate_id=v['candidate_id'],receipt_id=r['receipt_id'],actual_reopened=True,native_reuse_eligible=False,**m.FLAGS)
    native=SimpleNamespace(_source=native_source,verify_ifc=reopen,export_ifc=lambda *a:pytest.fail('IFC export prohibited'))
    canonical=SimpleNamespace(verify=lambda state,output,root:dict(verified=True,source='canonical-replay'))
    coordinator=SimpleNamespace(sources=lambda root:deepcopy(epoch),plan=lambda:deepcopy(plan))
    monkeypatch.setattr(m,'_modules',lambda root:(coordinator,canonical,native))
    return SimpleNamespace(root=root,old=old,new=new,original=original,output=tmp_path/'output',
        calls=calls,native=native,coordinator=coordinator,files=files,publication=publication)


def run(f):return m.reuse(f.old,f.new,f.original,f.output,root=f.root)


def test_preserves_archive_and_receipts_reopens_once_and_binds_new_run(fixture):
    f=fixture;before=(f.original/m.ARCHIVE).read_bytes();record=run(f)
    assert f.calls==list(m.VEHICLES)
    assert (f.output/m.ARCHIVE).read_bytes()==before==(f.original/m.ARCHIVE).read_bytes()
    assert record['run_id']==m.read(f.new/'latest.json')['run_id']!=f.publication['run_id']
    assert record['publication_id']!=f.publication['publication_id']
    assert record['reuse']['original_publication_id']==f.publication['publication_id']
    assert record['reuse']['IFC_export_executed'] is False and record['reuse']['raw_receipts_modified'] is False
    assert record['reuse']['actual_IFC_reopen_count']==5
    assert all(record[k]is False for k in m.FLAGS)
    assert m.verify(f.new,f.output,root=f.root)==dict(verified=True,source='canonical-replay')
    with pytest.raises(ValueError,match='already exist'):run(f)


@pytest.mark.parametrize('change',['candidate','registry','geometry','source','equipment'])
def test_rejects_changed_new_vehicle_even_when_self_sealed(fixture,change):
    f=fixture;p=f.new/'vehicles/V1.json.gz';e=m.read(p);v=e['vehicle']
    if change=='candidate':v['candidate_id']='0'*64
    elif change=='registry':v['registry']['registry_id']='0'*64
    elif change=='geometry':v['geometry']['length']=18
    elif change=='source':v['source_sha256']['narrow.py']='0'*64
    else:e['candidate_id']='0'*64
    seal(v,'evaluation_id');seal(e,'evaluation_id');write(p,e)
    with pytest.raises(ValueError):run(f)
    assert not (f.output/m.RECORD).exists()


@pytest.mark.parametrize('change',['pending','duplicate','physical-cell','stale-epoch','run-seal','release'])
def test_rejects_incomplete_mixed_or_stale_new_run(fixture,change):
    f=fixture;p=f.new/'latest.json';r=m.read(p)
    if change=='pending':r['pending']=[{}]
    elif change=='duplicate':r['cases'][1]=deepcopy(r['cases'][0])
    elif change=='physical-cell':r['cases'][0]['candidate_id']='0'*64
    elif change=='stale-epoch':r['source_sha256']['cost.py']='0'*64
    elif change=='release':r['operating_release']=True
    if change!='run-seal':seal(r,'run_id')
    else:r['run_id']='0'*64
    write(p,r)
    with pytest.raises(ValueError):run(f)


def test_rejects_tampered_archive_and_retains_original_evidence(fixture):
    f=fixture;(f.original/m.ARCHIVE).write_bytes(b'tampered')
    with pytest.raises(ValueError):run(f)
    assert (f.original/m.ARCHIVE).read_bytes()==b'tampered'
    assert not f.calls


def test_rejects_wrong_receipt_even_when_archive_and_wrapper_resealed(fixture):
    f=fixture;r=json.loads(f.files['V1.ifc.receipt.json']);r['registry_id']='0'*64;seal(r,'receipt_id')
    f.files['V1.ifc.receipt.json']=m.encoded(r);archive(f.original/m.ARCHIVE,f.files)
    f.publication['vehicles'][0]['files_sha256']['V1.ifc.receipt.json']=hashlib.sha256(f.files['V1.ifc.receipt.json']).hexdigest()
    f.publication['files_sha256'][m.ARCHIVE]=m.digest(f.original/m.ARCHIVE);seal(f.publication,'publication_id');write(f.original/m.RECORD,f.publication)
    with pytest.raises(ValueError,match='receipt contract'):run(f)


def test_rejects_mutation_during_actual_reopening(fixture):
    f=fixture;original=f.native.verify_ifc
    def mutate(v,path):
        result=original(v,path)
        if v['vehicle_id']=='V5':(f.new/'vehicles/V5.json.gz').write_bytes(b'changed after read')
        return result
    f.native.verify_ifc=mutate
    with pytest.raises(ValueError,match='changed during IFC reuse'):run(f)


def test_rejects_reopener_that_changes_raw_receipt(fixture):
    f=fixture;original=f.native.verify_ifc
    def mutate(v,path):
        result=original(v,path);path.with_suffix('.ifc.receipt.json').write_bytes(b'changed');return result
    f.native.verify_ifc=mutate
    with pytest.raises(ValueError,match='modified original'):run(f)


def test_rejects_symlinks_and_overlapping_outputs(fixture):
    f=fixture;link=f.output;link.symlink_to(f.original,target_is_directory=True)
    with pytest.raises(ValueError,match='Unlinked'):run(f)
    link.unlink()
    with pytest.raises(ValueError,match='disjoint'):m.reuse(f.old,f.new,f.original,f.original,root=f.root)


@pytest.mark.parametrize('kind',[tarfile.SYMTYPE,tarfile.DIRTYPE,tarfile.GNUTYPE_LONGNAME,tarfile.XHDTYPE])
def test_rejects_nonordinary_headers_before_payload_allocation(tmp_path,kind):
    info=tarfile.TarInfo('member');info.type=kind;info.size=10**11
    p=tmp_path/'bad.gz';p.write_bytes(gzip.compress(info.tobuf()+bytes(10240),mtime=0))
    with pytest.raises(ValueError,match='bounded archive'):m._consume_archive(p,{'member':'0'*64},maximum_members=1)


def test_rejects_oversized_declared_file_and_json_expansion(tmp_path):
    info=tarfile.TarInfo('member');info.size=m.MAX_RAW+1
    p=tmp_path/'bad.gz';p.write_bytes(gzip.compress(info.tobuf()+bytes(10240),mtime=0))
    with pytest.raises(ValueError,match='bounded archive'):m._consume_archive(p,{'member':'0'*64},maximum_members=1)
    p.write_bytes(gzip.compress(b' '*100,mtime=0))
    with pytest.raises(ValueError,match='expansion'):m.read(p,maximum=50)


def test_rejects_stale_actual_narrow_source_before_reopening(fixture):
    f=fixture;(f.root/'narrow.py').write_text('changed physical generator')
    with pytest.raises(ValueError,match='Stale narrow source'):run(f)
    assert not f.calls


def test_requires_explicit_no_acceptance_from_reopening(fixture):
    f=fixture;original=f.native.verify_ifc
    def missing(v,path):
        result=original(v,path);result.pop('physical_accepted');return result
    f.native.verify_ifc=missing
    with pytest.raises(ValueError,match='unreleased IFC reopening'):run(f)
