"""Actual Rust recovery and forged evidence; local studies never grant release."""
from copy import deepcopy
from pathlib import Path
import gzip
import json
import pytest
from engineering.ferrite_maglev import stopped_recovery as r


@pytest.fixture(scope='module')
def packet(tmp_path_factory):
    output=tmp_path_factory.mktemp('stopped-recovery')/'packet'
    r.publish(output)
    return output


def rehash(output,name,value):
    path=output/name;path.write_bytes(gzip.compress(r.encoded(value),mtime=0))
    m=json.loads((output/'manifest.json').read_text());m['files_sha256'][name]=r.digest(path.read_bytes())
    (output/'manifest.json').write_bytes(r.encoded(m))


def test_actual_complete_matrix_retains_epoch_fences_and_new_contracts(packet):
    r.verify(packet)
    value=r._read(packet/'study.json.gz',True)
    assert len(value['runs'])==44
    for run in value['runs']:
        result=run['result'];expected=run['case'] in r.PASS
        assert result['reconciliation_passed'] is expected
        assert result['new_authorities']==(len(run['request']['positions']) if expected else 0)
        assert result['old_contracts_fenced'] and result['snapshot_fenced']
        assert result['exact_event_replay_equal'] and not result['physical_output_authorised']
        assert not result['multi_controller_handover_implemented']


@pytest.mark.parametrize('mutation',['faked-recovery','changed-owner','changed-epoch','dropped-event','self-approval','concealed-hold'])
def test_rehashed_forged_results_and_transcripts_are_rejected(packet,tmp_path,mutation):
    import shutil
    output=tmp_path/'packet';shutil.copytree(packet,output)
    value=r._read(output/'study.json.gz',True)
    if mutation=='faked-recovery':value['runs'][3]['result']['reconciliation_passed']=True
    elif mutation=='changed-owner':value['runs'][0]['result']['retained_records'][0]['grant']['owner']['session']+=1
    elif mutation=='changed-epoch':value['runs'][0]['result']['retained_records'][0]['grant']['epoch']+=1
    elif mutation=='dropped-event':value['runs'][0]['result']['transcript'].pop()
    elif mutation=='self-approval':value['physical_release']=True
    else:value['open_gates']=[]
    rehash(output,'study.json.gz',value)
    with pytest.raises(ValueError):r.verify(output)


def test_source_staleness_and_extra_files_fail_before_execution(packet,tmp_path):
    import shutil
    output=tmp_path/'packet';shutil.copytree(packet,output)
    m=json.loads((output/'manifest.json').read_text());m['source_sha256'][__file__]='0'*64
    (output/'manifest.json').write_bytes(r.encoded(m))
    with pytest.raises(ValueError,match='source'):r.verify(output)
    (output/'extra').write_text('not owned')
    with pytest.raises(ValueError,match='inventory'):r.verify(output)


def test_symlink_payload_and_inflate_budgets_hold(packet,tmp_path,monkeypatch):
    import shutil
    output=tmp_path/'packet';shutil.copytree(packet,output)
    target=output/'study.json.gz';target.unlink();target.symlink_to(packet/'study.json.gz')
    with pytest.raises(ValueError):r.verify(output)
    monkeypatch.setattr(r,'MAX_RAW',10)
    with pytest.raises(ValueError,match='inflate'):r._read(packet/'study.json.gz',True)
