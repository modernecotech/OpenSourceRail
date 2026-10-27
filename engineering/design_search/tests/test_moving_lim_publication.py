"""Actual archived component packages cannot acquire rehashed extra claims."""
from pathlib import Path
import gzip,io,json,shutil,tarfile
import pytest
from engineering.design_search import moving_lim_publication as p

ROOT=Path(__file__).resolve().parents[3]
PACKET=ROOT/p.OUTPUT


def _reseal(folder,mutate):
    report=p._read(folder/'assessment.json');mutate(report)
    report.pop('publication_id');report['publication_id']=p.identity(report)
    (folder/'assessment.json').write_bytes(p.encoded(report));(folder/'README.md').write_text(p._readme(report))
    manifest=p._read(folder/'manifest.json');manifest['publication_id']=report['publication_id']
    manifest['files_sha256']={f.name:p.digest(f) for f in folder.iterdir() if f.name!='manifest.json'}
    manifest.pop('manifest_id');manifest['manifest_id']=p.identity(manifest)
    (folder/'manifest.json').write_bytes(p.encoded(manifest))


def test_actual_archive_replays_independent_accounting_and_remains_small():
    result=p.verify(PACKET)
    assert result['sealed_packages']==5 and not result['operating_map_admitted']
    assert (PACKET/'native-runs.tar.gz').stat().st_size<5*1024*1024
    assessment=p._read(PACKET/'assessment.json')
    assert assessment['attempted_cases']==6
    assert assessment['comparisons']['spatial_time_convergence_established'] is False


def test_rehashed_force_claim_is_rejected_against_actual_archived_trace(tmp_path):
    packet=tmp_path/'packet';shutil.copytree(PACKET,packet)
    def change(report):report['rows'][1]['last']['thrust_N']+=1.
    _reseal(packet,change)
    with pytest.raises(ValueError,match='assessment differs from immutable runs'):p.verify(packet)


def test_duplicate_archive_member_is_rejected_even_with_rehashed_receipts(tmp_path):
    packet=tmp_path/'packet';shutil.copytree(PACKET,packet);stream=io.BytesIO()
    with tarfile.open(fileobj=io.BytesIO((packet/'native-runs.tar.gz').read_bytes()),mode='r:gz') as old,tarfile.open(fileobj=stream,mode='w') as new:
        members=old.getmembers()
        for item in members:new.addfile(item,io.BytesIO(old.extractfile(item).read()))
        item=members[0];new.addfile(item,io.BytesIO(old.extractfile(item).read()))
    archive=gzip.compress(stream.getvalue(),mtime=0);(packet/'native-runs.tar.gz').write_bytes(archive)
    _reseal(packet,lambda report:report.update(archive_sha256=p.sha256(archive).hexdigest()))
    with pytest.raises(ValueError,match='unique bounded'):p.verify(packet)


def test_regenerating_current_packet_preserves_exact_old_native_bytes(tmp_path):
    runs=tmp_path/'runs';runs.mkdir()
    with tarfile.open(PACKET/'native-runs.tar.gz') as tar:
        for member in tar:
            target=runs/member.name;target.parent.mkdir(parents=True,exist_ok=True)
            target.write_bytes(tar.extractfile(member).read())
    output=tmp_path/'published';first=p.publish(runs,output)
    archive=(output/'native-runs.tar.gz').read_bytes()
    second=p.publish(runs,output,replace=True)
    assert second['publication_id']==first['publication_id']
    assert (output/'native-runs.tar.gz').read_bytes()==archive
