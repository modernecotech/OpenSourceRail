"""Independent stopping/ownership controls for the bounded capacity prototype."""
from copy import deepcopy
import json
import gzip
import pytest
from engineering.ferrite_maglev import line_capacity as lc


def test_stopping_oracle_includes_reaction_acceleration_sample_and_downhill():
    #20m/s,0.3s total reaction/sample, then20.3m/s at0.6m/s².
    expected=6000+45+343409+20000+500
    assert lc.stopping_envelope_mm(20000)==expected
    assert lc.stopping_envelope_mm(20000,age_ns=500_000_000)>expected
    assert lc.stopping_envelope_mm(20000,downhill_permille=10)>expected
    assert lc.stopping_envelope_mm(20000,reaction_ms=1000)>expected
    with pytest.raises(ValueError):lc.stopping_envelope_mm(20000,deceleration_mmps2=90,downhill_permille=10)
    with pytest.raises(ValueError):lc.stopping_envelope_mm(-1)


def test_repeated_route_has_real_berths_and_no_sink_or_switch():
    for mode in ('urban','suburban'):
        a=lc.load();railway,cfg,bounds,berths=lc.deployment(a,mode)
        assert 3<=len(railway['resources'])<=32
        assert len(berths)==a[mode+'_legs']+1
        assert all(r['point_asset_id'] is None and r['conflicts']==[r['id']] for r in railway['resources'])
        value,meta=lc.request(mode)
        assert meta['headway_s']==180 and len(value['frames'][-1]['positions'])==3
        assert len(value['frames'][-1]['positions'])==len(value['model']['trains'])
        assert value['model']['trains'][0]['config']['length_mm']==104500
        assert meta['horizon_s']>360+a[mode+'_runtime_s']
        for f in value['frames'][::100]:
            assert all(p['front_mm']<=value['model']['routes'][0]['segments'][-1]['end_mm'] for p in f['positions'])


@pytest.fixture(scope='module')
def binary():return lc.compile_replay()[0]


@pytest.mark.parametrize('mode',['urban','suburban'])
@pytest.mark.parametrize('case',lc.CASES)
def test_actual_rust_ledger_pipeline_and_negative_controls(binary,mode,case):
    run,_=lc.replay(binary,mode,case)
    assert run['control_pass'],json.dumps(run['replay'].get('failure'))
    r=run['replay']
    assert r['frames_executed']>0 and r['whole_line_capacity_accepted'] is False
    if case=='pipeline':
        assert r['study_pass'] and r['release_count']>0 and r['renewal_count']>r['reservation_count']
        assert r['maximum_active_trains']==3
        assert r['minimum_train_separation_mm']>0
        assert r['minimum_stopping_authority_margin_mm']>=0
        assert r['competing_owner_rejected'] and r['unidentified_tail_clear_rejected']
    elif case in {'delayed-clearance','extended-dwell'}:
        assert r['failure']['denied_before_front_entry']
        assert r['failure']['owner_retained']==101
    elif case in {'stale-position','rollback','integrity-loss','emergency-brake-loss'}:
        assert r['fault_fenced_resources']>0
        assert all(g['phase']=='Blocked' for g in r['retained_owners'] if g['train']==101)


def test_packet_rejects_edited_evidence_and_false_authority(tmp_path,monkeypatch,binary):
    result,execution=lc.study()
    assert result['executed_controls_pass']
    monkeypatch.setattr(lc,'study',lambda:(deepcopy(result),deepcopy(execution)))
    output=tmp_path/'packet';verified=lc.publish(output)
    assert verified['runs']==2*len(lc.ALL_CASES) and not verified['whole_line_capacity_accepted']
    manifest=json.loads((output/'manifest.json').read_text());original=(output/'README.md').read_bytes()
    (output/'README.md').write_text('All hardware accepted; no outstanding gates.')
    manifest['files_sha256']['README.md']=lc.digest((output/'README.md').read_bytes());(output/'manifest.json').write_bytes(lc.encoded(manifest))
    with pytest.raises(ValueError,match='presentation'):lc.verify(output)
    (output/'README.md').write_bytes(original);manifest['files_sha256']['README.md']=lc.digest(original);(output/'manifest.json').write_bytes(lc.encoded(manifest))
    original_study=(output/'study.json.gz').read_bytes();altered=deepcopy(result);altered['progressive_contract']['snapshot_reconciliation_implemented']=True
    (output/'study.json.gz').write_bytes(gzip.compress(lc.encoded(altered),mtime=0));manifest['files_sha256']['study.json.gz']=lc.digest((output/'study.json.gz').read_bytes());(output/'manifest.json').write_bytes(lc.encoded(manifest))
    with pytest.raises(ValueError,match='scope'):lc.verify(output)
    (output/'study.json.gz').write_bytes(original_study);manifest['files_sha256']['study.json.gz']=lc.digest(original_study);(output/'manifest.json').write_bytes(lc.encoded(manifest))
    manifest=json.loads((output/'manifest.json').read_text());manifest['whole_line_capacity_accepted']=True
    (output/'manifest.json').write_bytes(lc.encoded(manifest))
    with pytest.raises(ValueError,match='authority'):lc.verify(output)
    manifest['whole_line_capacity_accepted']=False;(output/'manifest.json').write_bytes(lc.encoded(manifest))
    (output/'overview.svg').write_bytes(b'<svg/>')
    with pytest.raises(ValueError,match='checksum'):lc.verify(output)


def test_forged_control_claim_and_wrong_braking_maximum_rejected(binary):
    value,_=lc.request('urban','pipeline');run,_=lc.replay(binary,'urban','pipeline')
    forged=deepcopy(run['replay']);forged['maximum_stopping_envelope_mm']-=1
    assert not lc._check_replay(forged,value,'pipeline')
    forged=deepcopy(run['replay']);forged['competing_owner_rejected']=False
    assert not lc._check_replay(forged,value,'pipeline')


def test_bounded_raw_inflate_rejects_decompression_expansion(monkeypatch):
    monkeypatch.setattr(lc,'MAX_RAW',1024)
    with pytest.raises(ValueError,match='bounded'):lc._inflate(gzip.compress(b'0'*1025,mtime=0))


@pytest.mark.parametrize('mode',['urban','suburban'])
@pytest.mark.parametrize('case',lc.JOINT_CASES)
def test_actual_station_launch_and_progressive_authority_composition(binary,mode,case):
    run,_=lc.replay(binary,mode,case);r=run['replay']
    assert run['control_pass'],json.dumps(r.get('failure'))
    assert r['durable_event_replay_equal'] and r['journal_records']>0
    if case in {'joint-600','joint-replay'}:
        assert r['maximum_active_trains']==3 and r['committed_launches']>3 and r['cleared_launches']>=3
    if case=='joint-180':
        assert r['failure']['kind']=='station-prepare-rejected'
        assert r['failure']['stopped_before_departure']
        assert r['failure']['atomic_no_partial_allocation']
    if case in {'joint-restart','joint-stale-arrival','joint-receiving-fault'}:
        assert any(l['phase']=='Held' and l['arrival_protected'] for l in r['retained_launches'])


@pytest.mark.parametrize('mode',['urban','suburban'])
@pytest.mark.parametrize('case',lc.CONTRACT_CASES)
def test_explicit_progressive_departure_contract_and_braking_plant(binary,mode,case):
    run,_=lc.replay(binary,mode,case);r=run['replay']
    assert run['control_pass'],json.dumps(r.get('failure'))
    assert r['protocol']=='osr-progressive-departure/1' and r['durable_event_replay_equal']
    if case in {'contract-180','contract-journal'}:
        assert r['maximum_active_trains']==3 and r['minimum_stopping_authority_margin_mm']>=0
    if case=='contract-closed-arrival':
        assert r['braking_plant_pass'] and r['failure']['stopping_has_no_next_sample_credit']
        for plant in r['braking_plants']:
            assert plant['final_speed_m_s']==0
            assert all(p['front_m']*1000+20000<=plant['owned_authority_end_mm'] for p in plant['trace'])
        assert any(d['phase']=='HeldStopped' for d in r['retained_contracts'])
