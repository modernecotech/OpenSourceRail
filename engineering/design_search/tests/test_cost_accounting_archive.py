"""Original-accounting byte preservation; no producer/evaluator is executed."""
from copy import deepcopy
import io
import json
from pathlib import Path
import shutil
import tarfile

import pytest

from engineering.design_search import cost_accounting_archive as a, portable_gzip
from engineering.station_rail.common import encoded,identity

ROOT=Path(__file__).resolve().parents[3]


@pytest.fixture(scope='module')
def original(tmp_path_factory):
    # The complete fixture comes from the pinned offline Git commit. Its output
    # remains in pytest's temporary tree, never in the working publication.
    out=tmp_path_factory.mktemp('cost-archive')/'packet'
    manifest=a.build(ROOT,out)
    return out,manifest


def copy_packet(original,tmp_path):
    out=tmp_path/'packet';shutil.copytree(original[0],out);return out


def reseal(out,manifest):
    manifest['archive_sha256']=a._hash((out/a.ARCHIVE).read_bytes())
    manifest['manifest_id']=identity({k:v for k,v in manifest.items() if k!='manifest_id'})
    (out/'manifest.json').write_bytes(encoded(manifest))


def members(out):
    with tarfile.open(out/a.ARCHIVE,'r:gz') as tar:
        return [(m.name,tar.extractfile(m).read()) for m in tar.getmembers()]


def replace_tar(out,entries,special=None):
    stream=io.BytesIO()
    with tarfile.open(fileobj=stream,mode='w',format=tarfile.USTAR_FORMAT) as tar:
        for index,(name,raw) in enumerate(entries):
            item=tarfile.TarInfo(name);item.mode=0o644;item.size=len(raw)
            if special is not None and index==0:item.type=tarfile.SYMTYPE;item.linkname='/outside';item.size=0
            tar.addfile(item,None if item.issym() else io.BytesIO(raw))
    (out/a.ARCHIVE).write_bytes(portable_gzip.compress(stream.getvalue()))


def test_exact_original_sources_totals_and_deterministic_portable_archive(original,tmp_path):
    out,manifest=original
    assert a.verify(out)==manifest
    assert manifest['original_git_commit']==a.COMMIT
    assert len(manifest['original_declared_source_sha256'])==17
    archived=dict(members(out));assert len(archived)==18
    record=json.loads(archived[a.RECORD])
    assert a._hash(archived[a.RECORD])==a.RECORD_SHA256
    for name,wanted in record['source_sha256'].items():assert a._hash(archived[name])==wanted
    assert manifest['original_summary']['cost_line_ids']==[row['line_id'] for row in record['cost_line_items']]
    assert manifest['original_summary']['model_based_whole_life_NPV_iqd']==record['model_based_whole_life_NPV_iqd']
    assert manifest['original_summary']['scope_totals_iqd']==record['scope_totals_iqd']
    assert len(manifest['known_correction_reasons'])==3
    assert manifest['numerical_reexecuted'] is False
    assert manifest['current_cost_result'] is False
    assert manifest['recursive_dependency_coverage_complete'] is False
    second=tmp_path/'second';a.build(ROOT,second)
    assert (second/a.ARCHIVE).read_bytes()==(out/a.ARCHIVE).read_bytes()
    assert (second/'manifest.json').read_bytes()==(out/'manifest.json').read_bytes()
    assert (out/a.ARCHIVE).read_bytes()[:10]==b'\x1f\x8b\x08\x00\x00\x00\x00\x00\x02\xff'


def test_verification_and_existing_build_need_no_git_or_current_producer_equality(original,monkeypatch):
    def forbid(*_args,**_kwargs):pytest.fail('Offline verification must not read Git or execute producer code')
    monkeypatch.setattr(a,'_git_file',forbid)
    monkeypatch.setattr(a.subprocess,'run',forbid)
    assert a.verify(original[0])==original[1]
    assert a.build('/a/nonexistent/current/source/root',original[0])==original[1]


@pytest.mark.parametrize('attack',('traversal','duplicate','symlink','missing-source','changed-source','changed-record'))
def test_resealed_archive_cannot_hide_unsafe_or_incomplete_original_bytes(original,tmp_path,attack):
    out=copy_packet(original,tmp_path);manifest=deepcopy(original[1]);entries=members(out)
    if attack=='traversal':entries[0]=('../escape.py',entries[0][1])
    elif attack=='duplicate':entries[-1]=entries[0]
    elif attack=='missing-source':entries[-1]=('unexpected.py',entries[-1][1])
    elif attack=='changed-source':
        index=next(i for i,(name,_) in enumerate(entries) if name!=a.RECORD)
        name,raw=entries[index];entries[index]=(name,raw+b'\n# changed\n')
    elif attack=='changed-record':
        index=next(i for i,(name,_) in enumerate(entries) if name==a.RECORD)
        entries[index]=(a.RECORD,entries[index][1]+b' ')
    replace_tar(out,entries,special=True if attack=='symlink' else None);reseal(out,manifest)
    with pytest.raises(ValueError):a.verify(out)
    assert not (tmp_path/'escape.py').exists()


def test_duplicate_json_keys_scope_promotion_and_changed_summary_are_rejected(original,tmp_path):
    out=copy_packet(original,tmp_path)
    raw=(out/'manifest.json').read_bytes()
    (out/'manifest.json').write_bytes(b'{"schema":"duplicate",'+raw[1:])
    with pytest.raises(ValueError,match='Duplicate JSON key'):a.verify(out)
    for key,value in [('physical_accepted',True),('numerical_reexecuted',True),('original_summary',{})]:
        manifest=deepcopy(original[1]);manifest[key]=value;reseal(out,manifest)
        with pytest.raises(ValueError,match='sources, summary or scope'):a.verify(out)


def test_existing_invalid_packet_is_not_overwritten_and_symlink_paths_fail(original,tmp_path):
    out=copy_packet(original,tmp_path);(out/a.ARCHIVE).write_bytes(b'broken')
    with pytest.raises(ValueError):a.build(ROOT,out)
    assert (out/a.ARCHIVE).read_bytes()==b'broken'
    link=tmp_path/'link';link.symlink_to(original[0],target_is_directory=True)
    with pytest.raises(ValueError,match='symlink'):a.verify(link)


def test_decompression_budget_and_unexpected_payload_are_rejected(original,tmp_path,monkeypatch):
    out=copy_packet(original,tmp_path)
    monkeypatch.setattr(a,'MAX_TAR',1024)
    with pytest.raises(ValueError,match='Decompressed accounting archive'):a.verify(out)
    monkeypatch.undo();(out/'unexpected').write_text('extra')
    with pytest.raises(ValueError,match='inventory'):a.verify(out)
