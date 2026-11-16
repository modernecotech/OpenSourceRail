"""Publication-only aggregate rows remain ordered and source authenticated."""
from hashlib import sha256

import pytest

from engineering.station_rail.common import encoded
from engineering.design_search import railway_publication as publication


def test_streaming_semantic_identity_matches_canonical_campaign():
    rows=[dict(candidate_id='a',row_id='one',reused=7,detail={'reused':9,'x':[1,2]}),
          dict(candidate_id='b',row_id='two',detail={'new_native_jobs':3,'x':None})]
    core=dict(schema='synthetic',rows=[],run_id='f'*64,bundles=[{'candidate_id':'a'},{'candidate_id':'b'}],
              source_sha256={'case':'e'*64},native={'reused':4,'b':True})
    full=dict(core,rows=rows)
    assert publication._streaming_semantic_id(core,rows)==publication.engine.semantic_id(full)
    visited=[]
    assert publication._streaming_semantic_id(core,rows,visited.append)==publication.engine.semantic_id(full)
    assert visited==rows
    assert core['rows']==[] and rows[0]['reused']==7


def test_projection_keeps_only_summary_and_p1_inventory_fields():
    rows=[dict(candidate_id='a',body_candidate_id='body',family_id='P1',
               accounted_mass={'accounted_tare_kg_per_car':1200.0},
               stages=[{'stage':'installed_inventory','record_id':'x'}],
               physical_journey_completed=False,economics={}),
          dict(candidate_id='b',body_candidate_id='body',family_id='P2',
               accounted_mass={'accounted_tare_kg_per_car':1300.0},
               stages=[{'stage':'motion'}],physical_journey_completed=False,economics={})]
    projected=publication._row_projection(iter(rows))
    accumulated=publication._new_row_projection()
    for row in rows:publication._add_row_projection(accumulated,row)
    assert publication._finalize_row_projection(accumulated)==projected
    assert projected['body']=={'body':{'count':2,'tare':1200.0}}
    assert projected['p1']=={'body':{'candidate_id':'a','stages':rows[0]['stages']}}
    assert projected['stages']==2 and projected['cost_count']==0
    assert projected['completion']==publication.completion_summary(rows)
    assert all('economics' not in item for item in projected['p1'].values())


def test_reopened_case_rejects_changed_shard(tmp_path,monkeypatch):
    cases=tmp_path/'cases';cases.mkdir()
    context='a'*64;path=cases/(context+'.parquet')
    path.write_bytes(b'original')
    row=dict(candidate_id='candidate',case_context_id=context,row_id='b'*64)
    raw=encoded(row)
    ref=dict(ordinal=0,case_context_id=context,parquet_name=path.name,
             parquet_sha256=sha256(path.read_bytes()).hexdigest(),
             case_bytes=len(raw),case_sha256=sha256(raw).hexdigest(),row_id=row['row_id'])
    monkeypatch.setattr(publication.aggregate_store,'_case_bytes',lambda *args,**kwargs:(path,row,raw))
    reader=publication._VerifiedRows(tmp_path,cases,[ref])
    assert list(reader)==[row]
    path.write_bytes(b'changed')
    with pytest.raises(ValueError,match='shard order or bytes'):
        list(reader)
    path.write_bytes(b'original')
    reader.refs=(dict(ref,ordinal=1),)
    with pytest.raises(ValueError,match='shard order or bytes'):
        list(reader)
