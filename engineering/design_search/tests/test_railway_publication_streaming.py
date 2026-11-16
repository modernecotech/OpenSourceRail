"""Publication-only aggregate rows remain ordered and source authenticated."""
from hashlib import sha256

import pytest

from engineering.station_rail.common import encoded
from engineering.design_search import aggregate_store,canonical_stream,railway_publication as publication


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


def _projection_frames():
    rows=[dict(candidate_id='a'*64,body_candidate_id='d'*64,family_id='P1',row_id='1'*64,
               accounted_mass={'accounted_tare_kg_per_car':1200.0},
               stages=[{'stage':'installed_inventory','record_id':'x'}],
               physical_journey_completed=False,economics={}),
          dict(candidate_id='b'*64,body_candidate_id='d'*64,family_id='P2',row_id='2'*64,
               accounted_mass={'accounted_tare_kg_per_car':1300.0},
               stages=[{'stage':'motion'}],physical_journey_completed=False,economics={})]
    value=dict(schema='synthetic',contract_id='c'*64,source_sha256={'source.py':'e'*64},
               rows=rows,bundles=[{'candidate_id':row['candidate_id']} for row in rows])
    value['campaign_id']=canonical_stream.canonical_identity(value,semantic=True)
    value['run_id']=canonical_stream.canonical_identity(value)
    core=encoded(dict(value,rows=[]))
    refs=[dict(row_id=row['row_id'],case_bytes=len(encoded(row))) for row in rows]
    return value,core,refs,rows


def test_authenticated_aggregate_frames_project_semantics_in_one_pass():
    value,core,refs,rows=_projection_frames()
    sink=publication._SemanticProjectionSink(core,dict(value,rows=[]),refs)
    composer=aggregate_store._Composer(core,sink)
    for row in rows:composer.row(encoded(row))
    result=composer.finish()
    semantic,projection=sink.finish()
    assert result['aggregate_bytes']==len(encoded(value))
    assert semantic==value['campaign_id']==publication._streaming_semantic_id(dict(value,rows=[]),rows)
    assert projection==publication._row_projection(rows)


def test_projection_sink_rejects_changed_row_framing_before_completion():
    value,core,refs,rows=_projection_frames()
    sink=publication._SemanticProjectionSink(core,dict(value,rows=[]),refs)
    with pytest.raises(ValueError,match='prefix'):
        sink.write(b'changed')
    sink=publication._SemanticProjectionSink(core,dict(value,rows=[]),refs)
    offset=aggregate_store._core_offset(core)
    sink.write(core[:offset+1])
    with pytest.raises(ValueError,match='row length'):
        sink.write(encoded(rows[0])[:-2])
    sink=publication._SemanticProjectionSink(core,dict(value,rows=[]),refs)
    sink.write(core[:offset+1]);sink.write(encoded(rows[0])[:-1])
    with pytest.raises(ValueError,match='delimiter'):
        sink.write(b';')
    sink=publication._SemanticProjectionSink(core,dict(value,rows=[]),refs)
    sink.write(core[:offset+1]);sink.write(encoded(rows[0])[:-1])
    sink.write(b',');sink.write(encoded(rows[1])[:-1])
    with pytest.raises(ValueError,match='incomplete'):
        sink.finish()
    with pytest.raises(ValueError,match='tail framing'):
        sink.write(b'changed')


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
