"""Retired adapters cannot quietly re-enter source or compressed publications."""
import gzip
import pytest
from engineering.ferrite_maglev import architecture_audit,model


def test_current_tree_contains_only_current_vehicle_sources():
    assert architecture_audit.verify(model.ROOT)['current_only']


def test_old_identity_in_plain_or_compressed_evidence_is_rejected(tmp_path):
    for suffix in ('.py','.json.gz'):
        p=tmp_path/('receipt'+suffix)
        raw=('configuration='+architecture_audit.TOKENS[0]).encode()
        p.write_bytes(gzip.compress(raw) if suffix.endswith('.gz') else raw)
        assert architecture_audit.scan([p])==[str(p)]


def test_geographic_comparisons_and_accessibility_terms_are_permitted(tmp_path):
    p=tmp_path/'requirements.md';p.write_text('Accessible wheelchair entry. Compare urban rail coverage with London and Paris.')
    assert not architecture_audit.scan([p])


def write_compressed_prefix(path,prefix_bytes,tail=b''):
    """Large raw evidence fixture with bounded memory and small disk footprint."""
    path.parent.mkdir(parents=True,exist_ok=True)
    block=b'x'*(1024*1024)
    with path.open('wb') as target,gzip.GzipFile(fileobj=target,mode='wb',compresslevel=1,mtime=0) as stream:
        count,remainder=divmod(prefix_bytes,len(block))
        for _ in range(count):stream.write(block)
        stream.write(block[:remainder]);stream.write(tail)


@pytest.mark.parametrize('packet,publisher',[('corridor','corridor'),('moving-train','moving_train')])
def test_owned_archive_bounds_match_actual_publishers(packet,publisher):
    import importlib
    module=importlib.import_module('engineering.ferrite_maglev.'+publisher)
    path=model.ROOT/'docs/design-engine/ferrite-maglev'/packet/'result.json.gz'
    assert architecture_audit.OWNED_GZIP_RAW_LIMITS[path]==module.MAX_RAW==128*1024*1024
    assert len(architecture_audit.OWNED_GZIP_RAW_LIMITS)==2


@pytest.mark.parametrize('packet',['corridor','moving-train'])
def test_only_exact_owned_packet_receives_128mib_allowance(tmp_path,monkeypatch,packet):
    owned=tmp_path/'owned'/packet/'result.json.gz'
    arbitrary=tmp_path/'arbitrary'/packet/'result.json.gz'
    monkeypatch.setattr(architecture_audit,'OWNED_GZIP_RAW_LIMITS',{owned:128*1024*1024})
    write_compressed_prefix(arbitrary,64*1024*1024+1)
    assert architecture_audit.gzip_raw_limit(arbitrary)==64*1024*1024
    with pytest.raises(ValueError,match='bounded evidence audit exceeded'):
        architecture_audit.scan([arbitrary])
    owned.parent.mkdir(parents=True,exist_ok=True);owned.write_bytes(arbitrary.read_bytes())
    assert architecture_audit.gzip_raw_limit(owned)==128*1024*1024
    assert architecture_audit.scan([owned])==[]
    alias=tmp_path/'alias.json.gz';alias.symlink_to(owned)
    assert architecture_audit.gzip_raw_limit(alias)==64*1024*1024
    with pytest.raises(ValueError,match='bounded evidence audit exceeded'):
        architecture_audit.scan([alias])


@pytest.mark.parametrize('packet',['corridor','moving-train'])
def test_owned_packet_retired_token_after_64mib_is_still_scanned(tmp_path,monkeypatch,packet):
    owned=tmp_path/'owned'/packet/'result.json.gz'
    monkeypatch.setattr(architecture_audit,'OWNED_GZIP_RAW_LIMITS',{owned:128*1024*1024})
    write_compressed_prefix(owned,64*1024*1024,architecture_audit.TOKENS[0].encode())
    assert architecture_audit.scan([owned])==[str(owned)]


@pytest.mark.parametrize('packet',['corridor','moving-train'])
def test_owned_packet_still_rejects_more_than_128mib(tmp_path,monkeypatch,packet):
    owned=tmp_path/'owned'/packet/'result.json.gz'
    monkeypatch.setattr(architecture_audit,'OWNED_GZIP_RAW_LIMITS',{owned:128*1024*1024})
    write_compressed_prefix(owned,128*1024*1024+1)
    with pytest.raises(ValueError,match='bounded evidence audit exceeded'):
        architecture_audit.scan([owned])
