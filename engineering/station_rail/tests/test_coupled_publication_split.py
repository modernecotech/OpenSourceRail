"""The completed coupled experiment retains exact source and payload bytes."""
from pathlib import Path
import tarfile

import pytest

from engineering.station_rail import publication, retained_v07_coupled


def test_coupled_v07_is_source_pinned_research():
    scope = publication.linked_publication_scope()
    assert 'coupled-railway-v07' not in scope['current_source_and_declared_payload']
    assert 'coupled-railway-v07' in scope['historical_source_epoch_integrity_only']
    proof = retained_v07_coupled.verify()
    assert proof['verified'] is True
    assert proof['original_source_count'] == 66
    assert proof['current_evaluator_admission'] is False
    assert proof['physical_accepted'] is False


def test_coupled_v07_source_archive_damage_is_rejected(tmp_path, monkeypatch):
    damaged = tmp_path / 'sources.tar.gz'
    damaged.write_bytes(b'not an archive')
    monkeypatch.setattr(retained_v07_coupled, 'ARCHIVE', Path(damaged))
    with pytest.raises((ValueError, OSError, tarfile.TarError)):
        retained_v07_coupled.verify()
