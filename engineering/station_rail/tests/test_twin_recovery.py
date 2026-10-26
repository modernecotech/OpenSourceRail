from copy import deepcopy
import pytest
from engineering.station_rail import twin_recovery as r


def fixture():
    parts=[dict(id='part',twin_frame='vehicle',volume_m3=1.)]
    native=dict(candidate_id='candidate',part_count=1,rows=[dict(id='part',native_volume_m3=1.)],native_volume_m3=1.,reopened_volume_m3=1.,step_volume_m3=1.)
    actual=[dict(id='part',candidate_id='candidate',occurrence_id='part',frame='vehicle',physical_accepted=False,complete_installed_twin=False,volume_m3=1.001)]
    return parts,native,actual


def test_every_occurrence_must_match_identity_and_native_volume():
    p,n,a=fixture();assert r.check_occurrences('candidate',p,n,a)['part_count']==1
    for key,value in [('volume_m3',1.1),('occurrence_id','other'),('frame','station'),('physical_accepted',True)]:
        bad=deepcopy(a);bad[0][key]=value
        with pytest.raises(ValueError):r.check_occurrences('candidate',p,n,bad)
    with pytest.raises(ValueError):r.check_occurrences('candidate',p,n,[])
    with pytest.raises(ValueError):r.check_occurrences('candidate',p,n,a+a)


def test_native_BRep_or_reopened_mismatch_is_not_recovered():
    p,n,a=fixture();n['rows'][0]['native_volume_m3']=1.02
    with pytest.raises(ValueError,match='Native BRep'):r.check_occurrences('candidate',p,n,a)
    p,n,a=fixture();n['step_volume_m3']=1.01
    with pytest.raises(ValueError,match='STEP'):r.check_occurrences('candidate',p,n,a)


def test_only_exact_ifc_timeout_is_eligible_and_budget_cannot_expand(tmp_path):
    for error in (ValueError(r.TIMEOUT),TimeoutError('Different timeout'),TimeoutError('Native CAD failed')):
        with pytest.raises(ValueError,match='exact'):r.recover(tmp_path,error)
    with pytest.raises(ValueError,match='at most240s'):r.recover(tmp_path,TimeoutError(r.TIMEOUT),timeout_s=241)
    assert not list(tmp_path.iterdir())


def test_unsealed_prior_export_does_not_invent_a_timeout(tmp_path,monkeypatch):
    candidate={'candidate_id':'candidate'}
    monkeypatch.setattr(r.campaign,'compare',lambda *args,**kwargs:dict(candidates=[candidate],results=[],confirmations=[]))
    monkeypatch.setattr(r,'_check_existing',lambda *args:None)
    folder=tmp_path/'build/v06-loop/twins/campaign/candidate';folder.mkdir(parents=True)
    with pytest.raises(ValueError,match='no cause assumed'):r.ensure_all('campaign',root=tmp_path)
    assert not list(folder.iterdir())
