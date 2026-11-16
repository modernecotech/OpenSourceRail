"""Journey C stays authenticated by pinned Git bytes, not current evaluators."""
import os
from pathlib import Path
import shutil
import subprocess

import pytest

from engineering.station_rail import retired_station_reference


def test_coupled_packet_is_historical_without_current_evaluator(monkeypatch):
    from engineering.design_search import railway_publication

    monkeypatch.setattr(railway_publication, "verify", lambda *a, **kw:
                        pytest.fail("A retired packet cannot call the current evaluator"))
    result = retired_station_reference.verify_coupled_packet()

    assert result["manifest_id"] == retired_station_reference.COUPLED_PACKET_MANIFEST_ID
    assert result["source_epoch"] == "historical"
    assert result["analytical_replay"] is False
    assert result["numerical_reexecuted"] is False
    assert result["current_evaluator_admission"] is False
    assert all(
        result[name] is False
        for name in (
            "physical_accepted",
            "engineering_accepted",
            "manufacturing_release",
            "operating_release",
        )
    )

    assert result["native_solver_jobs"] == 0


@pytest.fixture
def packet_copy(tmp_path):
    root = retired_station_reference.ROOT
    # Three bounded copies of the 96 MiB packet also work when the checkout
    # and pytest scratch are on different filesystems. Never share writable
    # inodes with the source evidence.
    git_dir = subprocess.check_output(['git', 'rev-parse', '--absolute-git-dir'],
                                      cwd=root, text=True).strip()
    (tmp_path / '.git').write_text('gitdir: ' + git_dir + '\n')
    packet = Path('docs/design-engine/coupled-railway')
    support = Path(retired_station_reference.COUPLED_SOURCE_EPOCH)
    shutil.copytree(root / packet, tmp_path / packet, copy_function=shutil.copy2)
    shutil.copytree(root / support, tmp_path / support, copy_function=shutil.copy2)
    return tmp_path


def replace(path, data):
    temporary = path.with_name(path.name + '.tampered')
    temporary.write_bytes(data)
    os.replace(temporary, path)


@pytest.mark.parametrize(('relative', 'message'), [
    ('docs/design-engine/coupled-railway/summary.json', 'payload differs'),
    ('docs/design-engine/coupled-railway/README.md', 'documentation overlay differs'),
    (retired_station_reference.COUPLED_SOURCE_EPOCH +
     '/source/engineering/station_rail/braking.py', 'historical braking source bytes differ'),
])
def test_historical_packet_rejects_tampering(packet_copy, relative, message):
    path = packet_copy / relative
    replace(path, path.read_bytes() + b'\n')
    with pytest.raises(retired_station_reference.RetiredReferenceHold, match=message):
        retired_station_reference.verify_coupled_packet(packet_copy)


def test_historical_packet_rejects_wrong_source_commit(monkeypatch):
    current_commit = subprocess.check_output(
        ['git', 'rev-parse', 'HEAD'], cwd=retired_station_reference.ROOT,
        text=True).strip()
    monkeypatch.setattr(retired_station_reference, 'COUPLED_PACKET_COMMIT',
                        current_commit)
    with pytest.raises(retired_station_reference.RetiredReferenceHold,
                       match='Retired Git source bytes differ'):
        retired_station_reference.verify_coupled_packet()


def test_explicit_prefetch_is_source_bound_and_offline_when_blobs_are_present():
    result = retired_station_reference.prefetch_coupled_blobs()
    assert result['commit'] == retired_station_reference.COUPLED_PACKET_COMMIT
    assert result['prefetched_blobs'] == 0
    assert result['pinned_blob_count'] > 50
    assert result['physical_accepted'] is False
