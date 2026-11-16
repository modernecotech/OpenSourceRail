"""A receipt hint may only rule out a current-parent refinement fail closed."""
from contextlib import contextmanager
from pathlib import Path

import pytest

from engineering.station_rail.common import encoded,identity
from engineering.design_search import railway_publication as publication
from engineering.design_search import railway_refinement_current as producer


@pytest.fixture
def preflight(tmp_path,monkeypatch):
    folder=tmp_path/'build/coupled-railway'/('c'*64)
    folder.mkdir(parents=True)
    pointer=dict(aggregate_sha256='d'*64,run_id='a'*64)
    value=dict(contract_id='c'*64,run_id='a'*64)
    projection=dict(aggregate_sha256='d'*64)
    monkeypatch.setattr(publication.engine,'current_aggregate',lambda *a,**kw:(folder,pointer))
    candidates=tmp_path/'build/coupled-railway/refinements'/producer.CANDIDATE_ID
    def add(parent='e'*64,**changes):
        request=dict(schema='osr-current-source-railway-refinement-request/1',
            body_candidate_id=producer.CANDIDATE_ID,parent_result_sha256=parent,
            parent_contract_id=value['contract_id'],parent_campaign_id='b'*64,
            parent_run_id=value['run_id'],source_sha256={'engineering/source.py':'f'*64})
        request.update(changes)
        target=candidates/identity(request);target.mkdir(parents=True)
        (target/'request.json').write_bytes(encoded(request))
        return target,request
    return tmp_path,folder,value,projection,candidates,add


def test_missing_and_nonmatching_requests_skip_full_parent(preflight):
    root,folder,value,projection,_,add=preflight
    assert publication._potential_current_refinement(root,folder,value,projection) is False
    add()
    assert publication._potential_current_refinement(root,folder,value,projection) is False


def test_matching_request_requires_full_verifier(preflight):
    root,folder,value,projection,_,add=preflight
    add(parent='d'*64)
    assert publication._potential_current_refinement(root,folder,value,projection) is True
    projection['aggregate_sha256']='0'*64
    with pytest.raises(ValueError,match='Active aggregate changed'):
        publication._potential_current_refinement(root,folder,value,projection)


def test_publication_miss_does_not_materialize_full_parent(tmp_path,monkeypatch):
    out=tmp_path/'publication';out.mkdir()
    value=dict(contract_id='c'*64,run_id='a'*64,campaign_id='b'*64)
    @contextmanager
    def streaming(root):yield tmp_path,value,dict(aggregate_sha256='d'*64)
    monkeypatch.setattr(publication,'streaming_publication_context',streaming)
    monkeypatch.setattr(publication,'_potential_current_refinement',lambda *a,**kw:False)
    def forbidden(*a,**kw):pytest.fail('Nonmatching requests must not materialize the full parent')
    monkeypatch.setattr(publication,'current_context',forbidden)
    class StopBeforeWrite(Exception):pass
    monkeypatch.setattr(publication,'_retain_previous_publication',lambda *a,**kw:(_ for _ in ()).throw(StopBeforeWrite()))
    with pytest.raises(StopBeforeWrite):publication.build(tmp_path,out)


def test_malformed_or_overbudget_request_is_a_hold(preflight):
    root,folder,value,projection,_,add=preflight
    target,_=add()
    (target/'request.json').write_bytes(b'{')
    with pytest.raises(ValueError,match='malformed'):
        publication._potential_current_refinement(root,folder,value,projection)
    (target/'request.json').write_bytes(b'x'*(publication.MAX_REFINEMENT_PREFLIGHT_BYTES+1))
    with pytest.raises(ValueError,match='budget'):
        publication._potential_current_refinement(root,folder,value,projection)


def test_symlink_and_traversal_receipts_are_a_hold(preflight):
    root,folder,value,projection,candidates,add=preflight
    target,_=add()
    request_path=target/'request.json'
    outside=root/'outside.json';outside.write_bytes(request_path.read_bytes())
    request_path.unlink();request_path.symlink_to(outside)
    with pytest.raises(ValueError,match='unsafe'):
        publication._potential_current_refinement(root,folder,value,projection)
    request_path.unlink();outside.unlink();target.rmdir()
    add(source_sha256={'../outside.py':'f'*64})
    with pytest.raises(ValueError,match='domain'):
        publication._potential_current_refinement(root,folder,value,projection)
    for item in candidates.iterdir():
        (item/'request.json').unlink();item.rmdir()
    candidates.rmdir();candidates.symlink_to(root)
    with pytest.raises(ValueError,match='symlink'):
        publication._potential_current_refinement(root,folder,value,projection)
