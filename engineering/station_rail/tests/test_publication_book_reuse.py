"""Selected packet rebuilds reuse only a source-bound verified book."""
import pytest

from engineering import platform_book,readme_context
from engineering.station_rail import publication


@pytest.mark.parametrize('stale', (False,True))
def test_selected_rebuild_reuses_verified_book_and_rerenders_stale_book(tmp_path,monkeypatch,stale):
    calls=[]
    book_current=[not stale]
    output=tmp_path/'current'

    def publish(folder,*,root):
        folder.mkdir(parents=True)
        return dict(published=True,physical_accepted=False)

    def book(*,root,check=False):
        calls.append(('book',check))
        if check and not book_current[0]:raise ValueError('book source changed')
        if not check:book_current[0]=True
        return dict(verified=True,cached=check)

    monkeypatch.setattr(publication,'publish',publish)
    monkeypatch.setattr(publication,'seal',lambda *args:calls.append(('seal',None)))
    monkeypatch.setattr(publication,'verify',lambda *args,**kwargs:dict(verified=True))
    monkeypatch.setattr(readme_context,'write_owned',lambda root:None)
    monkeypatch.setattr(readme_context,'audit',lambda root:dict(current=True))
    monkeypatch.setattr(readme_context,'markdown',lambda audit:'Current\n')
    monkeypatch.setattr(platform_book,'build',book)

    result=publication.build(root=tmp_path,output=output,force=True)
    assert result['verification']['verified'] is True
    assert calls==([('seal',None),('book',True),('book',False),('seal',None),('book',True)] if stale else
                   [('seal',None),('book',True),('seal',None),('book',True)])
