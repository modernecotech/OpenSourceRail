"""Current city dossiers restore useful front doors without mixing evidence."""
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import re
from urllib.parse import unquote,urlsplit

import pytest

from engineering.city_reports import publication as reports
from engineering.station_rail.common import encoded,identity
from engineering.station_rail import FLAGS

ROOT=Path(__file__).resolve().parents[1]


def test_published_city_pages_have_the_actual_map_and_city_calculations():
    index=json.loads((ROOT/reports.OUTPUT/'index.json').read_bytes())
    assert index['city_count']==len(index['cities'])==266
    for row in index['cities']:
        folder=ROOT/row['path'];front=(folder/'README.md').read_text()
        for section in ('## City and network','### Lines, service and fleet','## Energy and propulsion',
                        '## Civil works, depot and manufacture','## Workforce and construction programme',
                        '## Capital, operating costs and whole-life economics','## Site, engineering and delivery evidence'):
            assert section in front,(row['city']['slug'],section)
        assert '![{} current calculated railway network'.format(row['city']['name']) in front
        assert row['outline_evaluation_id'] in front
        svg=(folder/'engineering/outline/network.svg').read_text()
        assert row['packet_id'] in svg
        dossier=json.loads((folder/'engineering/outline/manifest.json').read_bytes())
        assert dossier['map_request']['packet_id']==row['packet_id']
        assert dossier['map_request_id']==identity(dossier['map_request'])
        packet=json.loads((folder/'engineering/outline/summary.json').read_bytes())
        assert packet['source_ids']['atlas_packet_id']==row['packet_id']
        assert packet['costs']['reconciliation']['all_fourteen_scopes_reconciled'] is True
        assert packet['physical_accepted'] is False
        manifest=json.loads((folder/'engineering/current/manifest.json').read_bytes())
        assert manifest['schema']==reports.CITY_SCHEMA
        assert manifest['city_frontdoor_sha256']==sha256(front.encode()).hexdigest()
        assert json.loads((folder/'engineering/current/summary.json').read_bytes())['totals'] is None


def test_all_catalogue_and_city_markdown_links_resolve():
    paths=[ROOT/'cities/catalogue/README.md']
    paths.extend(ROOT/row['path']/'README.md' for row in json.loads((ROOT/reports.OUTPUT/'index.json').read_bytes())['cities'])
    checked=0
    for p in paths:
        for target in re.findall(r'\]\(([^)]+)\)',p.read_text()):
            parts=urlsplit(target)
            if parts.scheme or parts.netloc or not parts.path:continue
            assert (p.parent/unquote(parts.path)).exists(),(p.relative_to(ROOT),target)
            checked+=1
    assert checked>500


def test_presentation_receipt_rejects_changed_outputs_and_changed_sources(tmp_path):
    source=tmp_path/'engineering/city_reports';source.mkdir(parents=True)
    (source/'render.py').write_text('renderer')
    target=tmp_path/'cities/city/README.md';target.parent.mkdir(parents=True);target.write_text('# City\n')
    manifest=dict(schema=reports.SCHEMA+'/publication',source_sha256=reports._sources(tmp_path),
        files_sha256={'cities/city/README.md':sha256(target.read_bytes()).hexdigest()},**FLAGS)
    manifest['manifest_id']=identity(manifest)
    p=tmp_path/reports.OUTPUT/'manifest.json';p.parent.mkdir(parents=True);p.write_bytes(encoded(manifest))
    assert reports._manifest(tmp_path)==manifest
    target.write_text('# Changed budget\n')
    with pytest.raises(ValueError,match='output differs'):reports._manifest(tmp_path)
    target.write_text('# City\n');(source/'render.py').write_text('different source')
    with pytest.raises(ValueError,match='source/identity'):reports._manifest(tmp_path)


def test_catalogue_generator_uses_city_dossiers_and_relative_targets():
    path=ROOT/'tools/automation/generate-city-geography-index.py'
    spec=importlib.util.spec_from_file_location('city_index_generator',path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    module.ROOT=ROOT;module.SOURCE=ROOT/'docs/design-engine/current/cities.json'
    text=module.generate()
    assert '[Baghdad](west-asia/Iraq/Baghdad/README.md)' in text
    assert '](cities/catalogue/' not in text
    assert 'Base installed US$' in text


def test_existing_outline_inputs_remain_bound_to_their_source_receipts():
    sources=json.loads((ROOT/'docs/design-engine/outline-completion/manifest.json').read_bytes())['source_sha256']
    for name in ('docs/design-engine/current/cities.json','docs/design-engine/current/planning/index.json','docs/design-engine/current/planning/manifest.json'):
        assert sha256((ROOT/name).read_bytes()).hexdigest()==sources[name]
    held=json.loads((ROOT/'docs/design-engine/current/cities.json').read_bytes())
    for name in ('engineering/station_rail/cities.py','engineering/development_baseline/cities.py'):
        assert sha256((ROOT/name).read_bytes()).hexdigest()==held['source_sha256'][name]
