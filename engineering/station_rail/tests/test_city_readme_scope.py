"""Current city pages route to candidate-bound planning and keep results held."""
from hashlib import sha256
import importlib.util
import json
from pathlib import Path


def module():
    path=Path(__file__).resolve().parents[3]/'tools/automation/check-readmes.py'
    spec=importlib.util.spec_from_file_location('osr_check_readmes',path)
    value=importlib.util.module_from_spec(spec);spec.loader.exec_module(value);return value


def package(tmp_path):
    checker=module();checker.REPO_ROOT=tmp_path
    city=tmp_path/'cities/catalogue/region/country/city';current=city/'engineering/current';current.mkdir(parents=True)
    (city/'city.json').write_text('{}')
    frontdoor=('# City planning geography\n\n[Planning workspace](../../../../docs/workbench/planning/index.html) · '
               '[Current city hold](engineering/current/README.md)\n')
    package_readme=('# City planning hold\n\n[Planning workspace](../../../../../docs/workbench/planning/index.html)\n')
    summary=dict(schema='osr-current-city-hold/1',execution='held',performance_evaluated=False,totals=None,
        engineering_accepted=False,physical_accepted=False,installed_mass_complete=False,
        manufacturing_release=False,operating_release=False)
    (city/'README.md').write_text(frontdoor)
    (current/'README.md').write_text(package_readme)
    (current/'summary.json').write_text(json.dumps(summary))
    manifest=dict(schema='osr-current-city-publication/2',
        files_sha256={name:sha256((current/name).read_bytes()).hexdigest() for name in ('README.md','summary.json')},
        city_frontdoor_path=(city/'README.md').relative_to(tmp_path).as_posix(),
        city_frontdoor_sha256=sha256((city/'README.md').read_bytes()).hexdigest())
    (current/'manifest.json').write_text(json.dumps(manifest))
    return checker,city


def test_candidate_bound_city_hold_is_the_current_readme_contract(tmp_path):
    checker,city=package(tmp_path)
    text=(city/'README.md').read_text()
    assert checker.primary_city_readme(city/'README.md',text)==(text,[])


def test_current_city_pages_cannot_reintroduce_superseded_links(tmp_path):
    checker,city=package(tmp_path)
    text=(city/'README.md').read_text()+'\n[Old page](engineering/maglev/README.md)\n'
    _,errors=checker.primary_city_readme(city/'README.md',text)
    assert any('superseded design pages' in error for error in errors)


def test_city_performance_cannot_be_promoted_by_markdown_check(tmp_path):
    checker,city=package(tmp_path)
    summary_path=city/'engineering/current/summary.json'
    summary=json.loads(summary_path.read_text());summary['performance_evaluated']=True
    summary_path.write_text(json.dumps(summary))
    _,errors=checker.primary_city_readme(city/'README.md',(city/'README.md').read_text())
    assert any('cannot publish route performance or totals' in error for error in errors)
