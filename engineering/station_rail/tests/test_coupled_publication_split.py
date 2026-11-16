"""Current v0.7 source bindings stay separate from retained Journey C bytes."""
import pytest

from engineering.station_rail import publication, retired_station_reference
from engineering.station_rail.common import digest, encoded, identity


def test_linked_scope_keeps_current_and_historical_coupled_packets_distinct():
    scope = publication.linked_publication_scope()
    assert 'coupled-railway-v07' in scope['current_source_and_declared_payload']
    assert 'coupled-railway' in scope['retired_fixed_reference_integrity_only']
    assert 'coupled-railway-v07' not in retired_station_reference.PACKETS


def test_v07_linked_packet_requires_its_own_current_source(tmp_path):
    source = tmp_path / 'engineering' / 'current-source.py'
    source.parent.mkdir(parents=True)
    source.write_text('value = 1\n')
    folder = tmp_path / 'docs/design-engine/coupled-railway-v07'
    folder.mkdir(parents=True)
    payload = folder / 'summary.json'
    payload.write_bytes(encoded({'physical_accepted': False}))
    manifest = dict(schema='osr-coupled-railway-publication/2',
        source_sha256={'engineering/current-source.py': digest(source)},
        files_sha256={'summary.json': digest(payload)},
        physical_accepted=False, engineering_accepted=False,
        manufacturing_release=False, operating_release=False,
        selected_reference_changed=False)
    manifest['manifest_id'] = identity(manifest)
    (folder / 'manifest.json').write_bytes(encoded(manifest))
    bindings = publication._linked_packet_sources(
        tmp_path, 'coupled-railway-v07', publication.LINKED_PUBLICATIONS['coupled-railway-v07'])
    assert bindings['engineering/current-source.py'] == digest(source)
    assert bindings['docs/design-engine/coupled-railway-v07/summary.json'] == digest(payload)

    source.write_text('value = 2\n')
    with pytest.raises(ValueError, match='stale source'):
        publication._linked_packet_sources(
            tmp_path, 'coupled-railway-v07', publication.LINKED_PUBLICATIONS['coupled-railway-v07'])
