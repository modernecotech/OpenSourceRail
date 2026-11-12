"""Bounded source collection must not read unrelated city payloads."""
import gzip
import json
from pathlib import Path

import pytest

from engineering.outline import completion, design_completion
from engineering.station_rail.common import digest


def _write(root, name, raw=b'source'):
    path = root / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(raw)
    return path


def test_source_binding_reads_only_requested_city_payloads(tmp_path, monkeypatch):
    root = Path(tmp_path)
    common = (
        completion.PRODUCER, completion.POLICY, 'engineering/outline/city_inputs.py',
        'engineering/outline/city_service.py', 'engineering/outline/city_civil.py',
        'engineering/outline/city_project_cost.py', 'engineering/outline/design_completion.py',
        'engineering/outline/design_cache.py', 'engineering/outline/city_alignment.py',
        'engineering/outline/city_cost_inputs.py', 'engineering/outline/city-cost-inputs.toml',
        'engineering/outline/civil_evidence.py',
    )
    for name in common:
        _write(root, name)
    monkeypatch.setattr(design_completion, 'sources', lambda root: {})

    selected_source = 'geography/samawah/source.json'
    _write(root, selected_source, b'samawah source')
    selected_plan = json.dumps({'source_sha256': {selected_source: digest(root / selected_source)}}).encode()
    selected_plan_path = 'planning/samawah.json.gz'
    _write(root, selected_plan_path, gzip.compress(selected_plan))
    _write(root, 'geography/samawah.json', b'samawah geography')
    _write(root, 'geography/samawah-route.json', b'samawah route')

    # Invalid gzip makes an accidental read of an unrequested plan fail loudly.
    _write(root, 'planning/baghdad.json.gz', b'not-a-gzip-payload')
    geography = {
        'source_sha256': {'catalogue.json': 'catalogue-hash'},
        'rows': [
            {'slug': 'samawah', 'geography_path': 'geography/samawah.json',
             'route_geography_path': 'geography/samawah-route.json', 'plan_path': selected_plan_path},
            {'slug': 'baghdad', 'geography_path': 'geography/baghdad.json',
             'route_geography_path': 'geography/baghdad-route.json', 'plan_path': 'planning/baghdad.json.gz'},
        ],
    }

    sources = completion._sources(root, geography, {'sources': {}}, cities=['samawah'])

    assert selected_plan_path in sources
    assert selected_source in sources
    assert 'geography/samawah.json' in sources
    assert 'geography/samawah-route.json' in sources
    assert 'planning/baghdad.json.gz' not in sources
    assert 'geography/baghdad.json' not in sources

    _write(root, 'geography/baghdad.json', b'baghdad geography')
    _write(root, 'geography/baghdad-route.json', b'baghdad route')
    _write(root, 'planning/baghdad.json.gz', gzip.compress(b'{"source_sha256":{}}'))
    full_sources = completion._sources(root, geography, {'sources': {}})
    assert 'planning/baghdad.json.gz' in full_sources
    assert 'geography/baghdad.json' in full_sources


@pytest.mark.parametrize('cities', [[], ['unknown']])
def test_source_binding_rejects_unknown_or_empty_city_sets(tmp_path, monkeypatch, cities):
    monkeypatch.setattr(design_completion, 'sources', lambda root: {})
    geography = {'source_sha256': {}, 'rows': [{'slug': 'samawah', 'plan_path': 'missing.gz'}]}
    with pytest.raises(ValueError, match='Known, nonempty city set'):
        completion._sources(tmp_path, geography, {'sources': {}}, cities=cities)
