"""Current comparison codec has an exact, bounded Rust Arrow round trip."""
from hashlib import sha256
from contextlib import nullcontext
import gzip
import json
import os
from pathlib import Path
import subprocess

import pytest

from engineering.station_rail.common import encoded
from engineering.design_search import railway_publication as publication


@pytest.fixture
def codec(monkeypatch):
    path=Path(os.environ.get('OSR_COMPARISON_CODEC',publication.ROOT/'target/debug/osr-campaign-columnar'))
    if not path.is_file():pytest.skip('Build osr-campaign-columnar with the columnar feature')
    monkeypatch.setenv('OSR_COMPARISON_CODEC',str(path))
    monkeypatch.setattr(publication,'disk_reservation',lambda *args,**kwargs:nullcontext())
    return path


def _rows():
    return [dict(candidate_id=f'candidate-{number}',body_candidate_id='body-a',
                 bundle_definition_id=f'bundle-{number}',row_id=f'row-{number}',
                 physical_journey_completed=False,complete_body_qualified=False,
                 unknown_mass_kg=None,detail={'sequence':number}) for number in (1,2,3)]


def test_exact_roundtrip_and_candidate_query(tmp_path,codec):
    rows=_rows()
    path=tmp_path/'comparison.parquet'
    receipt=publication._write_comparison(tmp_path,path,rows)
    expected=encoded(rows)
    assert receipt==dict(schema=publication.COMPARISON_SCHEMA,row_count=3,
                         canonical_sha256=sha256(expected).hexdigest())
    manifest=dict(schema='osr-coupled-railway-publication/2',comparison=receipt)
    assert list(publication._comparison_rows(tmp_path,tmp_path,manifest))==rows
    assert subprocess.run([str(codec),'read-comparison',str(path),receipt['canonical_sha256']],
                          capture_output=True,check=True).stdout==expected
    query=subprocess.run([str(codec),'query-comparison',str(path),receipt['canonical_sha256'],
                          'candidate-2'],capture_output=True,check=True)
    assert json.loads(query.stdout)==rows[1]


def test_tamper_order_and_inventory_sha_are_rejected(tmp_path,codec):
    rows=_rows()
    path=tmp_path/'comparison.parquet'
    receipt=publication._write_comparison(tmp_path,path,rows)
    wrong=dict(schema='osr-coupled-railway-publication/2',comparison=dict(receipt,canonical_sha256='0'*64))
    with pytest.raises(ValueError,match='scanner failed'):
        list(publication._comparison_rows(tmp_path,tmp_path,wrong))
    path.rename(tmp_path/'original.parquet')
    publication._write_comparison(tmp_path,path,list(reversed(rows)))
    original=dict(schema='osr-coupled-railway-publication/2',comparison=receipt)
    with pytest.raises(ValueError,match='scanner failed'):
        list(publication._comparison_rows(tmp_path,tmp_path,original))
    raw=bytearray(path.read_bytes());raw[len(raw)//2]^=1;path.write_bytes(raw)
    with pytest.raises(ValueError,match='scanner failed'):
        list(publication._comparison_rows(tmp_path,tmp_path,original))


def test_source_and_schema_receipts_are_required(tmp_path,codec,monkeypatch):
    rows=_rows();path=tmp_path/'comparison.parquet'
    receipt=publication._write_comparison(tmp_path,path,rows)
    manifest=dict(schema='osr-coupled-railway-publication/2',comparison=receipt)
    monkeypatch.setenv('OSR_COMPARISON_CODEC',str(tmp_path/'missing'))
    with pytest.raises(ValueError,match='Build the Rust'):
        list(publication._comparison_rows(tmp_path,tmp_path,manifest))
    monkeypatch.setenv('OSR_COMPARISON_CODEC',str(codec))
    with pytest.raises(ValueError,match='schema or inventory'):
        list(publication._comparison_rows(tmp_path,tmp_path,dict(manifest,comparison={})))
    assert all((publication.ROOT/name).is_file() for name in publication.COMPARISON_SOURCES)


def test_historical_v1_comparison_remains_read_only(tmp_path,codec):
    rows=_rows()
    legacy=tmp_path/'comparison.json.gz'
    legacy.write_bytes(gzip.compress(encoded(rows),mtime=0))
    manifest=dict(schema='osr-coupled-railway-publication/1')
    assert list(publication._comparison_rows(tmp_path,tmp_path,manifest))==rows
    assert legacy.read_bytes()==gzip.compress(encoded(rows),mtime=0)
