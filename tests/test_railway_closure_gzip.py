"""Portable gzip transport retains exact outer hashes and canonical inner JSON."""
import gzip,json,zlib
import pytest
from engineering.railway_closure import publication
from engineering.station_rail.common import encoded


def test_python_312_and_313_gzip_envelopes_have_same_canonical_study():
    value={'schema':'osr-gzip-portability-control/1','quantities':[1.25,0.,False],'material':'钢'}
    payload=encoded(value)
    legacy=zlib.compress(payload,9,wbits=31)  # Python3.12 mtime=0 path.
    current=bytearray(legacy);current[9]=255   # Python3.13 portable OS header.
    assert bytes(current)!=legacy
    assert publication.study_value(legacy)==publication.study_value(bytes(current))==value


def test_noncanonical_inner_bytes_are_still_rejected():
    raw=gzip.compress(json.dumps({'mass_kg':12.5},indent=2).encode(),mtime=0)
    with pytest.raises(ValueError,match='Canonical study encoding'):publication.study_value(raw)


def test_decision_view_verification_does_not_recompress_study(monkeypatch):
    monkeypatch.setattr(publication,'summary',lambda study:study)
    monkeypatch.setattr(publication,'readme',lambda study:'test view')
    monkeypatch.setattr(publication,'frontier',lambda study:{})
    monkeypatch.setattr(publication,'requirement_context',lambda study:{})
    def no_recompression(*args,**kwargs):raise AssertionError('Runtime gzip bytes are not scientific identity')
    monkeypatch.setattr(publication.gzip,'compress',no_recompression)
    assert 'study.json.gz' not in publication.artifacts({'study_id':'control'},include_study=False)
