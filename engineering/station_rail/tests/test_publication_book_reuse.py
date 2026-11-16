"""Selected packet rebuilds reuse only a source-bound verified book."""
from contextlib import nullcontext
import json
import pytest

from engineering import performance,platform_book,readme_context
from engineering.station_rail import publication


@pytest.mark.parametrize('stale', (False,True))
def test_selected_rebuild_reuses_verified_book_and_rerenders_stale_book(tmp_path,monkeypatch,stale):
    calls=[]
    book_current=[not stale]
    output=tmp_path/'current'

    def publish(folder,*,root,_manage_output,_seal,_preflight_result):
        assert not _manage_output and not _seal
        (folder/'payload.txt').write_text('new')
        return dict(published=True,physical_accepted=False)

    def book(*,root,check=False):
        calls.append(('book',check))
        if check and not book_current[0]:raise ValueError('book source changed')
        if not check:book_current[0]=True
        return dict(verified=True,cached=check)

    monkeypatch.setattr(publication,'publish',publish)
    monkeypatch.setattr(publication,'_publication_preflight',lambda root:())
    monkeypatch.setattr(publication,'seal',lambda *args:calls.append(('seal',None)))
    monkeypatch.setattr(publication,'verify',lambda *args,**kwargs:dict(verified=True))
    monkeypatch.setattr(readme_context,'write_owned',lambda root:None)
    monkeypatch.setattr(readme_context,'audit',lambda root:dict(current=True))
    monkeypatch.setattr(readme_context,'markdown',lambda audit:'Current\n')
    monkeypatch.setattr(platform_book,'build',book)

    result=publication.build(root=tmp_path,output=output,force=True)
    assert result['verification']['verified'] is True
    assert calls==([('book',True),('book',False),('seal',None),('book',True)] if stale else
                   [('book',True),('seal',None),('book',True)])


@pytest.mark.parametrize('fail_at',('seal','verify'))
def test_late_selected_failure_restores_packet_and_book_pair(tmp_path,monkeypatch,fail_at):
    output=tmp_path/'current';output.mkdir()
    (output/'manifest.json').write_text('old manifest')
    (output/'payload.txt').write_text('old payload')
    pdf=tmp_path/'OpenSourceRail-Book.pdf';pdf.write_bytes(b'old pdf')
    receipt=tmp_path/'OpenSourceRail-Book.receipt.json';receipt.write_bytes(b'old receipt')
    monkeypatch.setattr(readme_context,'write_owned',lambda root:None)
    monkeypatch.setattr(readme_context,'audit',lambda root:dict(current=True))
    monkeypatch.setattr(readme_context,'markdown',lambda audit:'Current\n')

    def publish(folder,*,root,_manage_output,_seal,_preflight_result):
        (folder/'payload.txt').write_text('new payload')
        return dict(published=True)

    def book(*,root,check=False):
        if not check:
            pdf.write_bytes(b'new pdf')
            receipt.write_bytes(b'new receipt')
        elif pdf.read_bytes()==b'old pdf':
            raise ValueError('stale book')

    calls=[0]
    def verify(*args,**kwargs):
        calls[0]+=1
        if calls[0]==1:raise ValueError('stale selected packet')
        if fail_at=='verify':raise RuntimeError('final verifier failed')
        return dict(verified=True)

    def seal(*args):
        if fail_at=='seal':raise RuntimeError('final seal failed')
        (output/'manifest.json').write_text('new manifest')

    monkeypatch.setattr(publication,'publish',publish)
    monkeypatch.setattr(publication,'_publication_preflight',lambda root:())
    monkeypatch.setattr(publication,'seal',seal)
    monkeypatch.setattr(publication,'verify',verify)
    monkeypatch.setattr(platform_book,'build',book)
    with pytest.raises(RuntimeError,match='final (seal|verifier) failed'):
        publication.build(root=tmp_path,output=output)
    assert (output/'manifest.json').read_text()=='old manifest'
    assert (output/'payload.txt').read_text()=='old payload'
    assert pdf.read_bytes()==b'old pdf'
    assert receipt.read_bytes()==b'old receipt'
    failed=tuple((tmp_path/'build/v06-development/failed-current').iterdir())
    assert len(failed)==1
    assert (failed[0]/'payload.txt').read_text()=='new payload'


@pytest.mark.parametrize('interrupt', (False,True))
def test_book_only_refresh_reseals_links_and_recovers_partial_commit(tmp_path,monkeypatch,interrupt):
    output=tmp_path/'current';output.mkdir()
    original=dict(schema='test',source_sha256={'source':'old'},files_sha256={'payload':'old'},
        linked_artifacts_sha256={platform_book.BOOK:'old',platform_book.RECEIPT:'old'},
        selection_id='same selection',evaluation_id='same evaluation')
    original['manifest_id']=publication.identity(original)
    (output/'manifest.json').write_bytes(publication.encoded(original))
    (tmp_path/platform_book.BOOK).write_bytes(b'old pdf')
    (tmp_path/platform_book.RECEIPT).write_bytes(b'old receipt')
    original['linked_artifacts_sha256']={name:publication.digest(tmp_path/name) for name in
        (platform_book.BOOK,platform_book.RECEIPT)}
    original['manifest_id']=publication.identity({key:value for key,value in original.items() if key!='manifest_id'})
    (output/'manifest.json').write_bytes(publication.encoded(original))
    def reserve(root,target,*args,**kwargs):
        assert target.is_dir()
        return nullcontext()
    monkeypatch.setattr(performance,'disk_reservation',reserve)

    def book(*,root,output=None,receipt_output=None,check=False):
        if not check:
            output.write_bytes(b'new pdf')
            receipt_output.write_bytes(b'new receipt')
        return dict(verified=True)

    monkeypatch.setattr(platform_book,'build',book)
    monkeypatch.setattr(publication,'verify',lambda *args,**kwargs:dict(verified=True))
    if interrupt:
        real_replace=publication.os.replace
        calls=[0]
        def replace(src,dst):
            calls[0]+=1
            if calls[0]==4:raise RuntimeError('injected mid-commit interruption')
            return real_replace(src,dst)
        monkeypatch.setattr(publication.os,'replace',replace)
        with pytest.raises(RuntimeError,match='mid-commit'):
            publication._refresh_book_only(tmp_path,output,dict(verified=True))
        assert (tmp_path/platform_book.BOOK).read_bytes()==b'old pdf'
        assert (tmp_path/platform_book.RECEIPT).read_bytes()==b'old receipt'
        assert json.loads((output/'manifest.json').read_bytes())==original
        assert not (tmp_path/'build/v06-development/book-transaction').exists()
        assert len(tuple((tmp_path/'build/v06-development/failed-book').iterdir()))==1
    else:
        result=publication._refresh_book_only(tmp_path,output,dict(verified=True))
        updated=json.loads((output/'manifest.json').read_bytes())
        assert result['book_only'] is True
        assert (tmp_path/platform_book.BOOK).read_bytes()==b'new pdf'
        assert updated['source_sha256']==original['source_sha256']
        assert updated['files_sha256']==original['files_sha256']
        assert updated['selection_id']==original['selection_id']
        assert updated['evaluation_id']==original['evaluation_id']
        assert updated['linked_artifacts_sha256'][platform_book.BOOK]==publication.digest(tmp_path/platform_book.BOOK)


def test_book_only_admission_requires_intact_old_reader_and_changed_inputs(tmp_path,monkeypatch):
    output=tmp_path/'current';output.mkdir()
    pdf=tmp_path/platform_book.BOOK;pdf.write_bytes(b'old pdf')
    receipt_path=tmp_path/platform_book.RECEIPT
    receipt=dict(schema='osr-platform-ebook/3',source_sha256={'chapter':'old'},
        pdf_sha256=publication.digest(pdf),pages=156,**platform_book.FLAGS)
    receipt['receipt_id']=platform_book._identity(receipt)
    receipt_path.write_text(json.dumps(receipt))
    (output/'manifest.json').write_text(json.dumps({'linked_artifacts_sha256':{
        platform_book.BOOK:publication.digest(pdf),
        platform_book.RECEIPT:publication.digest(receipt_path)}}))
    monkeypatch.setattr(platform_book,'_pages',lambda path:156)
    monkeypatch.setattr(platform_book,'_inputs',lambda root:{'chapter':'new'})
    assert publication._book_only_change(tmp_path,output)
    receipt_path.write_text(json.dumps(dict(receipt,pages=155)))
    assert not publication._book_only_change(tmp_path,output)


def test_selected_preflight_reads_old_exports_before_replacement(tmp_path,monkeypatch):
    output=tmp_path/'current';cost=output/'exports/selected-vehicle-cost.json'
    cost.parent.mkdir(parents=True);cost.write_text('old cost')
    (output/'manifest.json').write_text('old manifest')
    monkeypatch.setattr(publication,'verify',lambda *args,**kwargs:(_ for _ in ()).throw(ValueError('stale')))
    monkeypatch.setattr(readme_context,'write_owned',lambda root:None)

    def preflight(root):
        assert cost.read_text()=='old cost'
        raise RuntimeError('preflight hold')

    monkeypatch.setattr(publication,'_publication_preflight',preflight)
    with pytest.raises(RuntimeError,match='preflight hold'):
        publication.build(root=tmp_path,output=output)
    assert cost.read_text()=='old cost'
    assert (output/'manifest.json').read_text()=='old manifest'
    assert not (tmp_path/'build/v06-development/failed-current').exists()
