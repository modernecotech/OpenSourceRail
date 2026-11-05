"""Retired recipes cannot silently construct a current propulsion baseline."""
from pathlib import Path
import pytest
from engineering.station_rail import design_space as s,retired_station_reference as retired


@pytest.mark.parametrize('entry',['parent','assemble','build'])
def test_retired_recipe_refuses_before_constructing_or_writing(entry,tmp_path):
    out=tmp_path/'must-not-exist'
    with pytest.raises(retired.RetiredReferenceHold,match='explicit candidate campaign'):
        getattr(s,entry)(root=tmp_path,**({'output':out} if entry=='build' else {}))
    assert not out.exists() and not list(tmp_path.iterdir())


def test_verification_delegates_strict_retirement_and_never_replays(monkeypatch,tmp_path):
    source=tmp_path/s.PRODUCER;source.parent.mkdir(parents=True);source.write_bytes(Path(s.__file__).read_bytes())
    calls=[]
    def check(root):
        calls.append(root)
        return dict(retired_manifest_ids={'v06-design-space':'a'*64},reference_commit=retired.COMMIT,
            retention_id=retired.EXPECTED_RECEIPT_ID,dependency_sha256={'retained-packet':'b'*64})
    monkeypatch.setattr(retired,'verify',check)
    monkeypatch.setattr(s,'assemble',lambda *a,**kw:pytest.fail('No current numerical replay allowed'))
    v=s.verify(tmp_path)
    assert calls==[tmp_path.resolve()] and v['verified'] and v['retired']
    assert v['reference_commit']==retired.COMMIT and v['manifest_id']=='a'*64
    assert all(v[k] is False for k in ('current_evaluator_admission','numerical_reexecuted',
        'physical_equivalence_proven','physical_accepted','engineering_accepted',
        'configuration_adopted','manufacturing_release','operating_release'))


def test_an_arbitrary_resealed_packet_is_not_accepted(monkeypatch,tmp_path):
    monkeypatch.setattr(retired,'verify',lambda *a:pytest.fail('Custom path must fail before verification'))
    with pytest.raises(retired.RetiredReferenceHold,match='exact pinned'):
        s.verify(tmp_path,output=tmp_path/'other')


def test_missing_or_modified_retained_evidence_remains_a_hold(monkeypatch,tmp_path):
    source=tmp_path/s.PRODUCER;source.parent.mkdir(parents=True);source.write_bytes(Path(s.__file__).read_bytes())
    def failed(root):raise retired.RetiredReferenceHold('Missing exact old history')
    monkeypatch.setattr(retired,'verify',failed)
    with pytest.raises(retired.RetiredReferenceHold,match='Missing exact old history'):s.verify(tmp_path)
