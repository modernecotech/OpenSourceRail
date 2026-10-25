"""README context edits preserve numerical evidence and document-local prose."""
from hashlib import sha256
import json
from pathlib import Path
import subprocess

import pytest

from engineering.maglev_research import readme_context as r


def test_owned_block_is_idempotent_and_preserves_title_and_local_scope():
    name = 'deployment/README.md'
    original = '# Development deployment\n\nExact local scope, commands and qualifications.\n'
    changed = r.render(original, name)
    assert changed.startswith('# Development deployment\n\n')
    assert changed.endswith('Exact local scope, commands and qualifications.\n')
    assert r.INTRODUCTION in changed
    assert '[Project introduction](../README.md)' in changed
    assert r.render(changed, name) == changed
    stale = changed.replace('OpenSourceRail develops', 'Outdated text develops')
    assert r.render(stale, name) == changed


@pytest.mark.parametrize('name', [
    'README.md', 'cities/catalogue/README.md',
    'cities/catalogue/west-asia/Iraq/Baghdad/README.md',
    'docs/design-engine/ferrite-maglev/full-dynamics/README.md',
    'engineering/assurance/v053-pole-return-research/archive/README.md',
])
def test_nonowned_source_and_generated_readmes_are_never_edited(name):
    with pytest.raises(ValueError, match='outside the thirteen'):
        r.render('# Existing evidence\n', name)


@pytest.mark.parametrize('text', [
    '# Title\n'+r.START, '# Title\n'+r.END,
    '# Title\n'+r.START+r.START+r.END+r.END,
])
def test_malformed_owned_markers_are_refused(text):
    with pytest.raises(ValueError, match='one complete'):
        r.render(text, 'engineering/README.md')


def fixture_repository(tmp_path, monkeypatch):
    names = list(r.OWNED) + [
        'README.md', 'cities/catalogue/README.md',
        'cities/catalogue/west-asia/Iraq/City With Space/README.md',
        'cities/catalogue/west-asia/Iraq/City With Space/engineering/maglev/README.md',
        'docs/design-engine/ferrite-maglev/full-dynamics/README.md',
        'engineering/assurance/frozen/archive/README.md',
    ]
    for name in names:
        path = tmp_path/name
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_text('# Original local title\n\nLocal technical or archived scope.\n')
    brief = tmp_path/names[-4]
    brief.write_text('# City brief\n\n[Current package](engineering/maglev/README.md)\n')
    package = tmp_path/names[-3]
    # Explicitly exercise percent-encoded spaces and ordinary parent traversal.
    import os
    relative = Path(os.path.relpath(tmp_path/'engineering/ferrite_maglev/README.md',package.parent)).as_posix()
    package.write_text('# City package\n\n[Primary planning method]('+relative+')\n')
    monkeypatch.setattr(r, 'inventory', lambda root: sorted(names))
    return names


def test_write_and_audit_cover_generated_and_archived_routes_without_rewriting(tmp_path, monkeypatch):
    names = fixture_repository(tmp_path, monkeypatch)
    retained = {name:(tmp_path/name).read_bytes() for name in names if name not in r.OWNED}
    assert len(r.write_owned(tmp_path)) == 13
    assert r.write_owned(tmp_path) == []
    for name,original in retained.items():
        assert (tmp_path/name).read_bytes() == original
    report = r.audit(tmp_path)
    assert report['current']
    assert report['owned_introductions_current'] == 13
    assert report['readme_count'] == len(names)
    assert report['existing_context_routes'] + report['central_context_routes'] == len(names)
    rows = {row['path']:row for row in report['readmes']}
    brief = 'cities/catalogue/west-asia/Iraq/City With Space/README.md'
    assert rows[brief]['existing_context_route'][-1] == 'engineering/ferrite_maglev/README.md'
    assert rows['engineering/assurance/frozen/archive/README.md']['coverage_context_required']
    text = r.markdown(report)
    assert 'City%20With%20Space' in text
    assert 'Via this coverage page' in text


def test_numerical_binding_stops_all_owned_writes_before_mutation(tmp_path, monkeypatch):
    names = fixture_repository(tmp_path, monkeypatch)
    receipt = tmp_path/'docs/design-engine/ferrite-maglev/full-dynamics/manifest.json'
    receipt.write_text(json.dumps({'source_sha256':{'engineering/README.md':'0'*64}}))
    before = {name:(tmp_path/name).read_bytes() for name in names}
    with pytest.raises(ValueError,match='alter numerical evidence'):
        r.write_owned(tmp_path)
    assert all((tmp_path/name).read_bytes() == value for name,value in before.items())


def test_tampered_retained_readme_cannot_be_reported_preserved(tmp_path, monkeypatch):
    names = fixture_repository(tmp_path, monkeypatch)
    r.write_owned(tmp_path)
    receipt = tmp_path/'docs/design-engine/ferrite-maglev/full-dynamics/manifest.json'
    receipt.write_text(json.dumps({'files_sha256':{'README.md':'0'*64}}))
    report = r.audit(tmp_path)
    assert not report['current']
    assert not report['current_source_packet_readmes_preserved']
    with pytest.raises(ValueError,match='current README audit'):
        r.markdown(report)


def test_unknown_readme_requires_explicit_ownership(tmp_path, monkeypatch):
    names = fixture_repository(tmp_path, monkeypatch)
    r.write_owned(tmp_path)
    name = 'new-product/README.md'
    (tmp_path/name).parent.mkdir()
    (tmp_path/name).write_text('# New product\n')
    names.append(name)
    report = r.audit(tmp_path)
    assert not report['current']
    assert any('ownership decision' in error for error in report['errors'])


def test_existing_document_link_resolution_stays_local_and_supports_spaces(tmp_path):
    name = 'docs/README.md'
    target = tmp_path/'A Folder/README.md'
    target.parent.mkdir()
    target.write_text('# Local\n')
    text = '[local](../A%20Folder/README.md) [external](https://example.com/README.md) [escape](../../out.md)'
    assert r.local_links(tmp_path,name,text) == ['A Folder/README.md']


def test_inventory_includes_new_readmes_before_git_staging(monkeypatch):
    calls = []
    def output(command, cwd):
        calls.append(command)
        return (b'docs/new/README.md\0' if '--others' in command else b'README.md\0')
    monkeypatch.setattr(r.subprocess, 'check_output', output)
    assert r.inventory() == ['README.md', 'docs/new/README.md']
    assert any('--others' in command and '--exclude-standard' in command for command in calls)


def test_publication_self_receipt_is_excluded_to_avoid_circular_source_claims(tmp_path, monkeypatch):
    names = fixture_repository(tmp_path, monkeypatch)
    r.write_owned(tmp_path)
    name = (r.OUTPUT/'README.md').as_posix()
    path = tmp_path/name
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text('# Current research programme\n')
    names.append(name)
    (path.parent/'manifest.json').write_text(json.dumps({'files_sha256':{'README.md':'0'*64}}))
    report = r.audit(tmp_path)
    assert report['current']
    row = next(row for row in report['readmes'] if row['path'] == name)
    assert row['category'] == 'current-research-programme'
    assert row['retained_bindings'] == []


def test_repository_coverage_accounts_for_all_current_readmes_and_receipts():
    report = r.audit()
    assert report['readme_count'] >= 600
    assert report['current'], report['errors']
    assert report['owned_introductions_current'] == 13
    assert report['current_source_packet_readmes_preserved']
    assert report['categories']['generated-city-brief'] == 266
    assert report['categories']['generated-city-package'] == 266
    published = {
        name.decode() for name in subprocess.check_output([
            'git', 'ls-files', '-z', '--cached', '--others', '--exclude-standard',
            '--', 'docs/design-engine', 'engineering/assurance'], cwd=r.ROOT).split(b'\0')
        if name and 'README' in Path(name.decode()).name and name.decode().endswith('.md')
    }
    programme = 'docs/design-engine/ferrite-maglev/research-closure/README.md'
    expected = {
        'retained-design-evidence': {name for name in published
            if name.startswith('docs/design-engine/') and name != programme},
        'retained-assurance-evidence': {name for name in published
            if name.startswith('engineering/assurance/')},
    }
    for category, paths in expected.items():
        assert {row['path'] for row in report['readmes'] if row['category'] == category} == paths
        assert report['categories'][category] == len(paths)
    assert len(expected['retained-design-evidence']) >= 45
    assert len(expected['retained-assurance-evidence']) >= 7
    assert 'docs/design-engine/design-search/README.md' in expected['retained-design-evidence']
    assert any(name.startswith('docs/design-engine/design-search-twins/') and name.endswith('/bim/README.md')
               for name in expected['retained-design-evidence'])
    assert any(name.startswith('engineering/assurance/v053-design-search-replay/')
               for name in expected['retained-assurance-evidence'])
    assert next(row for row in report['readmes'] if row['path'] == 'engineering/design_search/README.md')['category'] == 'candidate-design-method'
    assert sum(report['categories'].values()) == report['readme_count']
