"""A retained city record cannot be mislabeled as a v0.6 performance result."""
from hashlib import sha256
import importlib.util
import json
from pathlib import Path

import pytest


def module():
    path=Path(__file__).resolve().parents[3]/'tools/automation/check-readmes.py'
    spec=importlib.util.spec_from_file_location('osr_check_readmes',path)
    value=importlib.util.module_from_spec(spec);spec.loader.exec_module(value);return value


@pytest.fixture
def archive(tmp_path):
    m=module();m.REPO_ROOT=tmp_path
    city=tmp_path/'cities/catalogue/region/country/city';package=city/'engineering/current';package.mkdir(parents=True)
    (city/'city.json').write_text('{}')
    (city/'README.md').write_text('# Historical front page\n')
    for name in ('README.md','summary.json','manifest.json'):(package/name).write_text('Retained '+name+'\n')
    bindings={p.relative_to(tmp_path).as_posix():sha256(p.read_bytes()).hexdigest() for p in [city/'README.md',*(package/n for n in ('README.md','summary.json','manifest.json'))]}
    value=dict(schema='osr-v05-git-archive/1',revision=m.ARCHIVE_REVISION,physical_accepted=False,source_and_payload_sha256=bindings)
    value['archive_id']=sha256((json.dumps(value,sort_keys=True,separators=(',',':'))+'\n').encode()).hexdigest()
    receipt=tmp_path/m.ARCHIVE;receipt.parent.mkdir(parents=True);receipt.write_text(json.dumps(value))
    return m,city


def test_frozen_city_bytes_are_historical_without_parsing_them_as_current(archive):
    m,city=archive
    text=(city/'README.md').read_text()
    assert m.primary_city_readme(city/'README.md',text)==(text,[])


def test_modified_historical_city_cannot_bypass_archive_scope(archive):
    m,city=archive
    (city/'engineering/current/summary.json').write_text('{"family":"wheel_rail_station_lim"}')
    _,errors=m.primary_city_readme(city/'README.md',(city/'README.md').read_text())
    assert len(errors)==1
    assert 'historical v0.5 city bytes differ' in errors[0]


def test_forged_archive_is_rejected_before_classifying_city(archive):
    m,city=archive;path=m.REPO_ROOT/m.ARCHIVE
    value=json.loads(path.read_text());value['physical_accepted']=True;path.write_text(json.dumps(value))
    _,errors=m.primary_city_readme(city/'README.md',(city/'README.md').read_text())
    assert 'historical v0.5 city archive identity differs' in errors[0]
