"""Closed input, parent and disposition checks; no physical approval."""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import json
import pytest
from engineering.station_rail.common import encoded,identity
from engineering.design_search import flanged_system_cost_publication as p

ROOT=Path(__file__).resolve().parents[3]
TOPO='294de81f3b1cca8215a95704287cfedf74ddfac596232027dee3c030163fdc43'
FLANGE='c6c10afa4889de76b64a806d3b0d6fc9f13ae4d4d40981284a7161c94618605a'
PUBLISHED_STATE=ROOT/'docs/design-engine/flanged-system-cost-study/original'
STATE=PUBLISHED_STATE if PUBLISHED_STATE.is_dir() else ROOT/'build/flanged-system-evidence/final-three-v2'


def seal(d,key):d[key]=identity({k:v for k,v in d.items() if k!=key});return d


def fixture_raw():
    raw={name:('common-'+name).encode() for name in p.COMMON}
    for name in p.NAMES:
        prefix=name+'/';raw[prefix+'original-request.json']=b'original request';raw[prefix+'original-result.json']=b'original result'
        names={'baseline-manifest.json','baseline.json.gz','producer.py','worker.py',prefix+'original-request.json',prefix+'original-result.json'}
        req=dict(schema='osr-flanged-system-cost-private-request/1',gauge=name,
            limits=dict(address_space_bytes=1073741824,cpu_seconds=60,wall_seconds=60,blas_threads=1),
            input_sha256={k:sha256(raw[k]).hexdigest() for k in names},
            original_candidate_id='a'*64,physical_accepted=False,engineering_accepted=False,manufacturing_release=False,operating_release=False)
        seal(req,'request_id');raw[prefix+'request.json']=encoded(req);raw[prefix+'result.json.gz']=b'output'
        raw[prefix+'stdout.log']=b'ok';raw[prefix+'stderr.log']=b''
        e=dict(schema='osr-flanged-private-execution/1',request_id=req['request_id'],limits=deepcopy(req['limits']),execution='completed',returncode=0,wall_seconds=1.,
            actual_files={k[len(prefix):]:sha256(v).hexdigest() for k,v in raw.items() if k.startswith(prefix)},
            physical_accepted=False,engineering_accepted=False,manufacturing_release=False,operating_release=False)
        seal(e,'execution_id');raw[prefix+'execution.json']=encoded(e)
    return raw


def write_raw(folder,raw):
    folder.mkdir(parents=True)
    for name,data in raw.items():
        path=folder/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(data)


def test_completed_failed_and_timeout_attempts_preserve_disposition():
    raw=fixture_raw();name='baseline';req,execution=p._execution(raw,name)
    assert req['gauge']==name and execution['execution']=='completed'
    for status,code in [('failed',1),('wall-timeout',None)]:
        changed=dict(raw);changed.pop(name+'/result.json.gz');e=json.loads(changed[name+'/execution.json']);e.update(execution=status,returncode=code);e['actual_files'].pop('result.json.gz');seal(e,'execution_id');changed[name+'/execution.json']=encoded(e)
        assert p._execution(changed,name)[1]['execution']==status
        row=p._summary(None,name,req,e);assert row['evaluation_id'] is row['composition_candidate_id'] is None
        assert row['unadmitted_partial_result_present'] is False
    changed=dict(raw);e=json.loads(changed[name+'/execution.json']);e.update(execution='failed',returncode=1);seal(e,'execution_id');changed[name+'/execution.json']=encoded(e)
    assert p._execution(changed,name)[1]['execution']=='failed'
    assert p._summary(None,name,req,e)['unadmitted_partial_result_present'] is True


@pytest.mark.parametrize('damage',['request-id','result-hash','log-hash','input-hash','limits','promotion','outcome','missing','status'])
def test_attempt_tampering_and_false_promotion_are_rejected(damage):
    raw=fixture_raw();prefix='baseline/';req=json.loads(raw[prefix+'request.json']);exe=json.loads(raw[prefix+'execution.json'])
    if damage=='request-id':req['gauge']='thick-web';seal(req,'request_id');raw[prefix+'request.json']=encoded(req)
    elif damage=='result-hash':raw[prefix+'result.json.gz']=b'changed'
    elif damage=='log-hash':raw[prefix+'stderr.log']=b'changed'
    elif damage=='input-hash':raw['producer.py']=b'changed'
    elif damage=='limits':exe['limits']['cpu_seconds']=999;seal(exe,'execution_id');raw[prefix+'execution.json']=encoded(exe)
    elif damage=='promotion':exe['physical_accepted']=True;seal(exe,'execution_id');raw[prefix+'execution.json']=encoded(exe)
    elif damage=='outcome':exe['execution']='failed';seal(exe,'execution_id');raw[prefix+'execution.json']=encoded(exe)
    elif damage=='missing':raw.pop(prefix+'stderr.log')
    else:exe['execution']='accepted';seal(exe,'execution_id');raw[prefix+'execution.json']=encoded(exe)
    with pytest.raises((ValueError,KeyError)):p._execution(raw,'baseline')


def test_snapshot_rejects_extra_missing_and_symlink_files(tmp_path):
    raw=fixture_raw();folder=tmp_path/'state';write_raw(folder,raw)
    assert p._snapshot(folder)==raw
    (folder/'extra').write_text('extra')
    with pytest.raises(ValueError):p._snapshot(folder)
    (folder/'extra').unlink();(folder/'baseline'/'stderr.log').unlink()
    with pytest.raises(ValueError):p._snapshot(folder)
    (folder/'baseline'/'stderr.log').symlink_to(folder/'baseline'/'stdout.log')
    with pytest.raises(ValueError):p._snapshot(folder)


def test_pinned_parent_checks_source_and_identity(tmp_path):
    source=tmp_path/'producer.py';source.write_text('source');folder=tmp_path/'packet';folder.mkdir()
    manifest=seal(dict(schema='parent/1',source_sha256={'producer.py':sha256(source.read_bytes()).hexdigest()},
        physical_accepted=False,engineering_accepted=False,manufacturing_release=False,operating_release=False),'manifest_id')
    (folder/'manifest.json').write_bytes(encoded(manifest))
    assert p._parent(tmp_path,'packet','parent/1',manifest['manifest_id'])[0]==manifest
    with pytest.raises(ValueError):p._parent(tmp_path,'packet','parent/1','0'*64)
    source.write_text('changed')
    with pytest.raises(ValueError):p._parent(tmp_path,'packet','parent/1',manifest['manifest_id'])


def test_duplicate_noncanonical_and_nonfinite_json_rejected():
    for b in (b'{"a":1,"a":1}\n',b'{"a": NaN}\n',b'{ "a":1}\n',b'[]\n'):
        with pytest.raises(ValueError):p._json(b)


def test_declared_producer_epoch_must_match_executing_source(tmp_path):
    source=tmp_path/p.PRODUCER;source.parent.mkdir(parents=True);source.write_bytes(Path(p.__file__).read_bytes())
    assert p._producer_epoch(tmp_path)==sha256(source.read_bytes()).hexdigest()
    source.write_bytes(source.read_bytes()+b'\n# changed\n')
    with pytest.raises(ValueError,match='producer differs'):p._producer_epoch(tmp_path)


def test_closed_publication_payload_cannot_hide_extra_or_changed_files(tmp_path):
    raw=fixture_raw();folder=tmp_path/'publication';folder.mkdir();write_raw(folder/'original',raw)
    rows=[dict(gauge=x,execution='failed',candidate_id='a'*64,request_id='b'*64,execution_id='c'*64,evaluation_id=None,composition_candidate_id=None) for x in p.NAMES]
    result=p._record(rows,{'source':'d'*64},{'topology_manifest_id':'e'*64},dict(python='observed'));(folder/'result.json').write_bytes(encoded(result));(folder/'README.md').write_text(p._readme(result));(folder/'manifest.json').write_bytes(b'{}\n')
    manifest=seal(dict(schema='osr-flanged-system-cost-publication/1',publication_id=result['publication_id'],parent_publications=result['parent_publications'],source_sha256=result['source_sha256'],files_sha256=p._payload(folder),**p.FLAGS),'manifest_id')
    (folder/'manifest.json').write_bytes(encoded(manifest));assert p._check(folder,manifest['manifest_id'])[1]==result
    (folder/'extra').write_text('outside contract')
    with pytest.raises(ValueError):p._check(folder,manifest['manifest_id'])
    (folder/'extra').unlink();(folder/'original'/'baseline'/'stdout.log').write_bytes(b'modified')
    with pytest.raises(ValueError):p._check(folder,manifest['manifest_id'])


def test_original_parent_inputs_are_bound_to_both_published_manifests():
    raw=p._snapshot(STATE);binding=p._parents(ROOT,TOPO,FLANGE,raw)
    assert binding['topology_manifest_id']==TOPO and binding['flanged_manifest_id']==FLANGE
    altered=dict(raw);altered['baseline/original-request.json']+=b' '
    with pytest.raises(ValueError):p._parents(ROOT,TOPO,FLANGE,altered)
    altered=dict(raw);altered['baseline.json.gz']+=b' '
    with pytest.raises(ValueError):p._parents(ROOT,TOPO,FLANGE,altered)
    with pytest.raises(ValueError):p._parents(ROOT,'0'*64,FLANGE,raw)
    with pytest.raises(ValueError):p._parents(ROOT,TOPO,'0'*64,raw)


def test_actual_attempts_have_same_candidate_context_and_no_promoted_status():
    raw=p._snapshot(STATE);rows,source,binding=p._audit(raw,ROOT,TOPO,FLANGE,replay=False)
    assert [r['execution'] for r in rows]==['completed']*3
    assert len({r['candidate_id'] for r in rows})==len({r['composition_candidate_id'] for r in rows})==3
    assert len({r['baseline_id'] for r in rows})==len({r['load_context_id'] for r in rows})==1
    assert all(r['whole_life_ranking_allowed'] is False and r['whole_life_comparison_ready'] is False for r in rows)
    assert source[p.PRODUCER]==sha256(Path(p.__file__).read_bytes()).hexdigest()
    assert binding['topology_manifest_id']==TOPO
