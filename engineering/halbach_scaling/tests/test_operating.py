import json
from pathlib import Path
import os
import pytest
from engineering.halbach_scaling import operating as o, candidates, screen
from engineering.halbach_scaling.common import identity,write,inventory,unaccepted
from engineering.halbach_scaling import FLAGS
ROOT=Path(os.environ.get('OSR_HALBACH_EVIDENCE_ROOT',candidates.ROOT))


def test_profile_schedule_preserves_fixed_mass_and_new_solve_budget():
    all_candidates=candidates.candidates(ROOT)
    d=next(b for b in all_candidates if b['parameters'].get('winding_layout')=='differential')
    u=next(b for b in all_candidates if b['parameters']['periods']==2)
    points=o.schedule([d,u])
    assert len(points)==18
    assert sum(not(p['gap_m']==.012 and p['temperature_C']==80 and p['current_A']==0) for p in points)==16
    assert {p['gap_m'] for p in points}=={.012,.028,.044,.060}
    assert {p['temperature_C'] for p in points}=={20,80}
    assert {p['current_A'] for p in points}=={-15,0,15}


def test_rehashed_complete_result_without_worker_execution_is_refused(tmp_path,monkeypatch):
    all_candidates=candidates.candidates(ROOT);bundles=[next(b for b in all_candidates if b['parameters'].get('winding_layout')=='differential'),next(b for b in all_candidates if b['parameters']['periods']==2)]
    sources={'fixture.py':'bound'};monkeypatch.setattr(o,'source_snapshot',lambda root:sources)
    schedule=o.schedule(bundles)
    request=dict(bundles=bundles,source_sha256=sources,budget=o.BUDGET,schedule=schedule,baseline_rows=[],**FLAGS)
    request['request_id']=identity(request)
    rows=[dict(point=p,case=f'point-{i:02d}',reused_nominal=False,result=dict(candidate_id=p['candidate_id'],execution_status='completed')) for i,p in enumerate(schedule)]
    value=dict(request_id=request['request_id'],source_sha256=sources,rows=rows,new_field_points=16,**FLAGS)
    p=schedule[0];b=bundles[0];directory=tmp_path/'point-00';directory.mkdir()
    entry=dict(candidate=b,scenario=screen._scenario(b,p['gap_m'],p['temperature_C'],{}),settings=screen.SETTINGS,source_sha256=screen.source_snapshot(ROOT))
    write(directory/'input.json',entry);write(tmp_path/'request.json',request);write(tmp_path/'result.json',value)
    write(tmp_path/'manifest.json',dict(source_sha256=sources,files_sha256=inventory(tmp_path,('manifest.json',)),**FLAGS))
    with pytest.raises(ValueError,match='execution receipt required'):o.verify(tmp_path,root=ROOT)


def test_nested_release_claims_never_become_qualification():
    for key in ('physical_accepted','configuration_adopted','manufacturing_release','stable_hover_established'):
        with pytest.raises(ValueError):unaccepted({'nested':[{'physical_accepted':False}|{key:True}]})
