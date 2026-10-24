"""Retired adapters cannot quietly re-enter source or compressed publications."""
import gzip
import pytest
from engineering.ferrite_maglev import architecture_audit,model

OWNED_PACKETS=[
    ('docs/design-engine/ferrite-maglev/corridor/result.json.gz',
     'engineering.ferrite_maglev.corridor','MAX_RAW',128*1024*1024),
    ('docs/design-engine/ferrite-maglev/moving-train/result.json.gz',
     'engineering.ferrite_maglev.moving_train','MAX_RAW',128*1024*1024),
    ('docs/design-engine/ferrite-maglev/assembled-body/native-mesh.json.gz',
     'engineering.ferrite_maglev.assembled_body','MAX_RAW',256*1024*1024),
    ('docs/design-engine/ferrite-maglev/full-dynamics/study.json.gz',
     'engineering.ferrite_maglev.full_dynamics','MAX_RAW',128*1024*1024),
    ('docs/design-engine/design-search/comparison.json.gz',
     'engineering.design_search.campaign','COMPARISON_MAX_BYTES',256*1024*1024),
]


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


@pytest.mark.parametrize('relative_path,publisher,bound_attribute,raw_limit',OWNED_PACKETS)
def test_owned_archive_bounds_match_actual_publishers(relative_path,publisher,bound_attribute,raw_limit):
    import importlib
    module=importlib.import_module(publisher)
    path=model.ROOT/relative_path
    assert architecture_audit.OWNED_GZIP_RAW_LIMITS[path]==getattr(module,bound_attribute)==raw_limit
    assert architecture_audit.DEFAULT_GZIP_RAW_LIMIT==64*1024*1024
    assert len(architecture_audit.OWNED_GZIP_RAW_LIMITS)==len(OWNED_PACKETS)==5


@pytest.mark.parametrize('relative_path,publisher,bound_attribute,raw_limit',OWNED_PACKETS)
def test_only_exact_owned_packet_receives_publisher_allowance(tmp_path,monkeypatch,relative_path,publisher,bound_attribute,raw_limit):
    owned=tmp_path/'owned'/relative_path
    arbitrary=tmp_path/'arbitrary'/relative_path
    monkeypatch.setattr(architecture_audit,'OWNED_GZIP_RAW_LIMITS',{owned:raw_limit})
    write_compressed_prefix(arbitrary,64*1024*1024+1)
    assert architecture_audit.gzip_raw_limit(arbitrary)==64*1024*1024
    with pytest.raises(ValueError,match='bounded evidence audit exceeded'):
        architecture_audit.scan([arbitrary])
    owned.parent.mkdir(parents=True,exist_ok=True);owned.write_bytes(arbitrary.read_bytes())
    assert architecture_audit.gzip_raw_limit(owned)==raw_limit
    assert architecture_audit.scan([owned])==[]
    alias=tmp_path/'alias.json.gz';alias.symlink_to(owned)
    assert architecture_audit.gzip_raw_limit(alias)==64*1024*1024
    with pytest.raises(ValueError,match='bounded evidence audit exceeded'):
        architecture_audit.scan([alias])
    parent_alias=tmp_path/'alias-folder';parent_alias.symlink_to(owned.parent,target_is_directory=True)
    assert architecture_audit.gzip_raw_limit(parent_alias/owned.name)==64*1024*1024
    with pytest.raises(ValueError,match='bounded evidence audit exceeded'):
        architecture_audit.scan([parent_alias/owned.name])
    # Even an exact allow-list key loses its allowance if the file or one of
    # its parent directories becomes a symlink.
    owned.unlink();owned.symlink_to(arbitrary)
    assert architecture_audit.gzip_raw_limit(owned)==64*1024*1024
    with pytest.raises(ValueError,match='bounded evidence audit exceeded'):
        architecture_audit.scan([owned])
    owned.unlink();owned.write_bytes(arbitrary.read_bytes())
    monkeypatch.setattr(architecture_audit,'OWNED_GZIP_RAW_LIMITS',{parent_alias/owned.name:raw_limit})
    assert architecture_audit.gzip_raw_limit(parent_alias/owned.name)==64*1024*1024
    with pytest.raises(ValueError,match='bounded evidence audit exceeded'):
        architecture_audit.scan([parent_alias/owned.name])


@pytest.mark.parametrize('relative_path,publisher,bound_attribute,raw_limit',OWNED_PACKETS)
def test_owned_packet_retired_token_after_64mib_is_still_scanned(tmp_path,monkeypatch,relative_path,publisher,bound_attribute,raw_limit):
    owned=tmp_path/'owned'/relative_path
    monkeypatch.setattr(architecture_audit,'OWNED_GZIP_RAW_LIMITS',{owned:raw_limit})
    write_compressed_prefix(owned,64*1024*1024,architecture_audit.TOKENS[0].encode())
    assert architecture_audit.scan([owned])==[str(owned)]


@pytest.mark.parametrize('relative_path,publisher,bound_attribute,raw_limit',OWNED_PACKETS)
def test_owned_packet_still_rejects_more_than_publisher_raw_limit(tmp_path,monkeypatch,relative_path,publisher,bound_attribute,raw_limit):
    owned=tmp_path/'owned'/relative_path
    monkeypatch.setattr(architecture_audit,'OWNED_GZIP_RAW_LIMITS',{owned:raw_limit})
    write_compressed_prefix(owned,raw_limit+1)
    with pytest.raises(ValueError,match='bounded evidence audit exceeded'):
        architecture_audit.scan([owned])


def test_early_retired_token_does_not_skip_remaining_archive_bytes(tmp_path,monkeypatch):
    owned=tmp_path/'comparison.json.gz'
    token=architecture_audit.TOKENS[0].encode()
    monkeypatch.setattr(architecture_audit,'OWNED_GZIP_RAW_LIMITS',{owned:2*1024*1024})
    owned.write_bytes(gzip.compress(token+b'x'*(2*1024*1024)))
    with pytest.raises(ValueError,match='bounded evidence audit exceeded'):
        architecture_audit.scan([owned])
