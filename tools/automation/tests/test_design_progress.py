"""Reporting cannot borrow old acceptance, mutate the queue or prune CAD evidence."""
import importlib.util
import json
from pathlib import Path
import time

import pytest

from engineering.continuous_design import service

SPEC=importlib.util.spec_from_file_location('design_progress',Path(__file__).parents[1]/'design-progress.py')
reporter=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(reporter)


def workspace(path, baseline='a'*64):
    store=service.Store(path)
    (path/'active.json').write_text(json.dumps(dict(baseline_sha256=baseline)))
    (path/'status.json').write_text(json.dumps(dict(baseline_sha256=baseline,state='running',heartbeat_unix=time.time())))
    return store


def candidate(store,key,baseline,*,passed=True,native=True,mass=100):
    store.db.execute('INSERT INTO jobs(key,baseline,lane,task,status,created,finished) VALUES(?,?,?,?,?,?,?)',
        (key,baseline,'mechanical',json.dumps(dict(kind='mechanical-detail')),'completed',1,2))
    store.db.execute('''INSERT INTO observations(key,baseline,lane,kind,context,concept,study_pass,level,mass,
        objectives,failures,native_confirmed,finished) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)''',
        (key,baseline,'mechanical','mechanical-detail','metro','frame',int(passed),'analytical_screening',mass,'{}','[]',int(native),2))
    confirmation=key+'-confirmation'
    store.db.execute('INSERT INTO jobs(key,baseline,lane,task,status,created) VALUES(?,?,?,?,?,?)',
        (confirmation,baseline,'mechanical','{}','completed',1))
    store.db.execute('INSERT INTO promotions VALUES(?,?,?,?,?,?)',(key,baseline,'metro',confirmation,'test',1))
    store.db.commit()


def test_read_only_snapshot_excludes_old_failed_and_unconfirmed_candidates(tmp_path):
    store=workspace(tmp_path)
    candidate(store,'old','b'*64,mass=1)
    candidate(store,'failed','a'*64,passed=False,mass=2)
    candidate(store,'analytical','a'*64,native=False,mass=3)
    candidate(store,'confirmed','a'*64,mass=100)
    before=list(store.db.iterdump())
    report,selected=reporter.collect(tmp_path)
    assert selected['mechanical'][0]['key']=='confirmed'
    assert report['research']['counts']['evaluated']==3
    assert report['research']['counts']['rejected']==1
    assert list(store.db.iterdump())==before


def test_changed_heartbeat_epoch_is_visible(tmp_path):
    store=workspace(tmp_path)
    (tmp_path/'status.json').write_text(json.dumps(dict(baseline_sha256='b'*64,state='running',heartbeat_unix=time.time())))
    report,_=reporter.collect(tmp_path)
    assert report['runner_state']=='epoch transition'
    store.db.close()


def test_expired_heartbeat_does_not_report_a_running_engine(tmp_path):
    store=workspace(tmp_path)
    (tmp_path/'status.json').write_text(json.dumps(dict(baseline_sha256='a'*64,state='running',heartbeat_unix=time.time()-3600)))
    report,_=reporter.collect(tmp_path)
    assert report['runner_state']=='stale heartbeat; runner activity unconfirmed'
    store.db.close()


def test_presentation_hash_and_epoch_containment_are_required(tmp_path):
    baseline='a'*64
    folder=tmp_path/'epochs'/baseline/'attempts'/'candidate'/'001'
    folder.mkdir(parents=True)
    (folder/'result.json').write_text('{}')
    receipt=dict(key='candidate',baseline_sha256=baseline,files_sha256={'result.json':reporter.sha(folder/'result.json')})
    (folder/'receipt.json').write_text(json.dumps(receipt))
    row=dict(folder=str(folder),baseline=baseline,key='candidate',receipt_sha=reporter.sha(folder/'receipt.json'))
    assert reporter.verified(row,tmp_path,('result.json',))[0]==folder
    (folder/'result.json').write_text('{"changed":true}')
    with pytest.raises(ValueError,match='changed presentation input'):
        reporter.verified(row,tmp_path,('result.json',))
    with pytest.raises(ValueError,match='outside declared epoch'):
        reporter.verified(dict(row,baseline='b'*64),tmp_path,('result.json',))


def test_deltas_do_not_reuse_a_previous_epoch_and_render_failure_is_explicit(tmp_path):
    store=workspace(tmp_path)
    candidate(store,'first','a'*64,native=False)
    first=reporter.snapshot(tmp_path)
    assert set(first['render_errors'])=={'mechanical','civil'}
    report=reporter.read(tmp_path/'progress/latest.json')
    assert report['delta'] is None
    candidate(store,'second','a'*64,native=False)
    reporter.snapshot(tmp_path)
    report=reporter.read(tmp_path/'progress/latest.json')
    assert report['delta']['evaluated']==1
    (tmp_path/'active.json').write_text(json.dumps(dict(baseline_sha256='b'*64)))
    reporter.snapshot(tmp_path)
    report=reporter.read(tmp_path/'progress/latest.json')
    assert report['delta'] is None and report['research']['counts']['evaluated']==0
    assert store.db.execute('SELECT COUNT(*) FROM jobs').fetchone()[0]==4


def test_retention_removes_only_owned_reports_and_preserves_attempts(tmp_path):
    snapshots=tmp_path/'snapshots';snapshots.mkdir()
    for index in range(4):
        folder=snapshots/f'20261018T12000{index}Z-abcdef00';folder.mkdir()
        (folder/'snapshot.json').write_text(json.dumps(dict(schema=reporter.SCHEMA)))
    unrelated=snapshots/'20261018T110000Z-abcdef00';unrelated.mkdir()
    (unrelated/'snapshot.json').write_text('{"schema":"another-owner"}')
    attempts=tmp_path/'attempts';attempts.mkdir();(attempts/'model.FCStd').write_bytes(b'preserve')
    reporter.prune(tmp_path,keep=2)
    assert len(list(snapshots.iterdir()))==3 and unrelated.exists()
    assert (attempts/'model.FCStd').read_bytes()==b'preserve'
    assert (snapshots/'20261018T120003Z-abcdef00').exists()


def test_report_escapes_provider_text_and_keeps_scope_visible(tmp_path):
    store=workspace(tmp_path)
    reporter.snapshot(tmp_path)
    report=reporter.read(tmp_path/'progress/latest.json')
    report['open_needs']=[dict(lane='software',item_id='<script>alert(1)</script>')]
    html=reporter.html_report(report)
    assert '<script>' not in html and '&lt;script&gt;' in html
    assert 'equivalent 1D' in html and 'release remain open' in html
    store.db.close()


def test_hourly_unit_is_bounded_and_quotes_percent_paths(tmp_path):
    units=reporter.unit_text(tmp_path/'100% workspace')
    assert 'OnCalendar=hourly' in units[reporter.UNIT+'.timer']
    assert 'Persistent=true' in units[reporter.UNIT+'.timer']
    service_unit=units[reporter.UNIT+'.service']
    assert '100%% workspace' in service_unit and 'MemoryMax=1G' in service_unit
    assert 'TimeoutStartSec=5min' in service_unit and '--notify' in service_unit


def test_geometry_renderer_hides_embedded_solids_independent_of_drawing_order():
    import numpy as np
    triangle=[[0,0],[1,0],[0,1]]
    front=[1.,0.,0.];behind=[0.,0.,1.]
    first=reporter.rasterize([triangle,triangle],[[1,1,1],[2,2,2]],[behind,front],width=50,height=50)
    second=reporter.rasterize([triangle,triangle],[[2,2,2],[1,1,1]],[front,behind],width=50,height=50)
    assert np.array_equal(first,second)
    assert (first==front).all(axis=2).sum()>500
    assert not (first==behind).all(axis=2).any()
