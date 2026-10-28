"""Pure transport security tests; no synthetic fixture is physical evidence.

Actual semantic nine-journey replay and IFC reopen belong to the current tracked
helper and are deliberately not mocked into a successful publication here.
"""
from pathlib import Path
import ast,gzip,hashlib,importlib.util,io,json,tarfile
import pytest
SCRIPT=Path(__file__).resolve().parents[1]/'sourced-bolster-package.py'
spec=importlib.util.spec_from_file_location('sourced_bolster_package',SCRIPT);s=importlib.util.module_from_spec(spec);spec.loader.exec_module(s)

@pytest.fixture
def cell(tmp_path):
    root=tmp_path/'cell';root.mkdir();(root/'manifest.json').write_text('{}\n');(root/'nested').mkdir();(root/'nested/data.bin').write_bytes(b'recorded-data'*100)
    return root,s.inventory(root)


def descriptor(files,archive_sha='a'*64,archive_bytes=10):
    report=dict(verified=True,package_id='b'*64,execution='completed',semantic_replay_executed=True,cases=1,journeys=9,selection_purpose='next-experiment-only',**s.FLAGS)
    d=dict(schema='osr-sourced-bolster-cell-publication/1',archive_path=s.ARCHIVE,archive_sha256=archive_sha,archive_bytes=archive_bytes,
        raw_payload_bytes=sum(row['bytes'] for row in files.values()),files=files,package_id='b'*64,candidate_id='c'*64,body_candidate_id='d'*64,evaluation_id='e'*64,
        helper_path=s.HELPER,helper_sha256='f'*64,producer_path=s.PRODUCER,producer_sha256='1'*64,source_sha256={'engineering/source.py':'2'*64},semantic_verification=report,
        verification_scope='current-code-nine-journey-replay-and-IFC-reopen;native-recorded-integrity-only',**s.FLAGS)
    d['publication_id']=s.identity(d);return d


def seal(d):
    d.pop('publication_id',None);d['publication_id']=s.identity(d);return d


def tar_attack(path,files,*,name='manifest.json',kind='regular',duplicate=False,size=None,extra_tail=b''):
    with path.open('wb') as raw,gzip.GzipFile(filename='',mode='wb',fileobj=raw,mtime=0) as gz:
        with tarfile.open(fileobj=gz,mode='w|',format=tarfile.USTAR_FORMAT) as tar:
            for n in range(2 if duplicate else 1):
                item=tarfile.TarInfo(name);item.mode=0o644;payload=b'{}\n';item.size=len(payload) if size is None else size
                if kind=='symlink':item.type=tarfile.SYMTYPE;item.linkname='/etc/passwd';item.size=0
                elif kind=='hardlink':item.type=tarfile.LNKTYPE;item.linkname='manifest.json';item.size=0
                elif kind=='directory':item.type=tarfile.DIRTYPE;item.size=0
                tar.addfile(item,io.BytesIO(payload) if item.isfile() and item.size==len(payload) else None)
        gz.write(extra_tail)


def test_deterministic_roundtrip_and_inert_python(cell,tmp_path):
    folder,files=cell;(folder/'archived.py').write_text('raise RuntimeError("must never execute")\n');files=s.inventory(folder)
    a=tmp_path/'a.tar.gz';b=tmp_path/'b.tar.gz';s.create_archive(folder,a,files);s.create_archive(folder,b,files)
    assert a.read_bytes()==b.read_bytes()
    out=s.extract_archive(a,tmp_path/'unpacked',files)
    assert s.inventory(out)==files
    assert (out/'archived.py').read_bytes()==(folder/'archived.py').read_bytes()


@pytest.mark.parametrize('name',['../outside','/absolute','nested/../outside','nested//bad','./manifest.json','a\\b','..','a/./b'])
def test_bad_names_rejected(name):
    with pytest.raises(ValueError):s._name(name)


@pytest.mark.parametrize('kind',['symlink','hardlink','directory'])
def test_nonordinary_members_rejected(tmp_path,kind):
    archive=tmp_path/'bad.tar.gz';tar_attack(archive,{},kind=kind)
    files={'manifest.json':{'bytes':0,'sha256':hashlib.sha256(b'').hexdigest()}}
    with pytest.raises(ValueError):s.extract_archive(archive,tmp_path/'out',files)


def test_duplicate_and_unknown_archive_member_rejected(cell,tmp_path):
    folder,files=cell;archive=tmp_path/'bad.tar.gz';tar_attack(archive,files,duplicate=True)
    with pytest.raises(ValueError):s.extract_archive(archive,tmp_path/'out',files)
    archive.unlink();tar_attack(archive,files,name='unknown.txt')
    with pytest.raises(ValueError):s.extract_archive(archive,tmp_path/'out2',files)


def test_payload_tamper_and_inventory_closure(cell,tmp_path):
    folder,files=cell;archive=tmp_path/'a.tar.gz';s.create_archive(folder,archive,files)
    changed=json.loads(json.dumps(files));changed['nested/data.bin']['sha256']='0'*64
    with pytest.raises(ValueError,match='identity'):s.extract_archive(archive,tmp_path/'bad',changed)
    changed=dict(files);changed.pop('nested/data.bin')
    with pytest.raises(ValueError):s.extract_archive(archive,tmp_path/'unknown',changed)
    (folder/'empty').mkdir()
    with pytest.raises(ValueError,match='empty'):s.inventory(folder)


@pytest.mark.parametrize('attack',['unknown','release','nested-release','identity','bool-size','total','path','helper','scope','replay','oversize','filehash'])
def test_descriptor_resealed_attacks_rejected(cell,attack):
    _,files=cell;d=descriptor(files)
    if attack=='unknown':d['accepted']=True
    elif attack=='release':d['operating_release']=True
    elif attack=='nested-release':d['semantic_verification']['physical_accepted']=True
    elif attack=='identity':d['publication_id']='0'*64
    elif attack=='bool-size':d['archive_bytes']=True
    elif attack=='total':d['raw_payload_bytes']+=1
    elif attack=='path':d['archive_path']='../elsewhere'
    elif attack=='helper':d['helper_path']='helper-source.py'
    elif attack=='scope':d['verification_scope']='fresh-native-solve-approved'
    elif attack=='replay':d['semantic_verification']['semantic_replay_executed']=False
    elif attack=='oversize':d['archive_bytes']=s.MAX_COMPRESSED+1
    elif attack=='filehash':d['files']['manifest.json']['sha256']='wrong'
    if attack!='identity':seal(d)
    with pytest.raises(ValueError):s.descriptor(d)


def test_payload_file_count_and_size_budgets(cell,tmp_path,monkeypatch):
    folder,files=cell;monkeypatch.setattr(s,'MAX_FILES',1)
    with pytest.raises(ValueError):s.inventory(folder)
    monkeypatch.setattr(s,'MAX_FILES',64);monkeypatch.setattr(s,'MAX_RAW',10)
    with pytest.raises(ValueError):s.inventory(folder)
    with pytest.raises(ValueError):s.extract_archive(tmp_path/'unused',tmp_path/'out',files)


def test_compressed_and_decompressed_limits(cell,tmp_path,monkeypatch):
    folder,files=cell;archive=tmp_path/'a.tar.gz';s.create_archive(folder,archive,files)
    monkeypatch.setattr(s,'MAX_COMPRESSED',1)
    with pytest.raises(ValueError):s.extract_archive(archive,tmp_path/'over',files)
    limited=s._Limited(io.BytesIO(b'Z'*101),100)
    with pytest.raises(ValueError):limited.read(101)


def test_duplicate_json_nonfinite_and_symlink_inputs(cell,tmp_path):
    folder,files=cell;bad=tmp_path/'bad.json';bad.write_text('{"x":1,"x":2}')
    with pytest.raises(ValueError):s._json(bad)
    bad.write_text('{"x":NaN}')
    with pytest.raises(ValueError):s._json(bad)
    alias=tmp_path/'alias';alias.symlink_to(folder,target_is_directory=True)
    with pytest.raises(ValueError):s.inventory(alias)
    (folder/'link').symlink_to(bad)
    with pytest.raises(ValueError):s.inventory(folder)


def test_publication_preserves_known_structural_neighbours_rejects_unknown(tmp_path):
    for name in s.NEIGHBOURS:(tmp_path/name).write_text('retained')
    assert s._publication_folder(tmp_path)==tmp_path
    (tmp_path/'unreviewed-extra').write_text('unknown')
    with pytest.raises(ValueError):s._publication_folder(tmp_path)


def test_no_output_inside_immutable_cell(cell):
    folder,_=cell
    with pytest.raises(ValueError,match='immutable'):s.publish(folder,folder/'publication')
    assert not (folder/'publication').exists()


def test_both_paths_delegate_explicit_replay_to_current_helper():
    tree=ast.parse(SCRIPT.read_text());calls=[n for n in ast.walk(tree) if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and isinstance(n.func.value,ast.Name) and n.func.value.id=='helper' and n.func.attr=='verify']
    assert len(calls)==2
    assert all(any(k.arg=='replay' and isinstance(k.value,ast.Constant) and k.value.value is True for k in c.keywords) for c in calls)
