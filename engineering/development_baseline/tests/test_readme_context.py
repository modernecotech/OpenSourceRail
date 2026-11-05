"""Current documentation context preserves historical scope and source identity."""
from hashlib import sha256
from pathlib import Path
import pytest
from engineering import readme_context as context


def test_current_entrypoints_describe_reference_vehicle_and_variable_propulsion():
    text = '# Tools\n\nLocal implementation details.\n'
    updated = context.render(text, 'tools/README.md')
    assert updated.startswith('# Tools\n')
    assert 'passive steel-wheel bogies' in updated
    assert 'no installed propulsion architecture or powered length is selected' in updated
    assert 'candidate-specific design variables' in updated
    assert 'prototype validation' in updated
    assert 'maglev' not in updated.lower()
    assert updated.endswith('Local implementation details.\n')
    assert context.render(updated, 'tools/README.md') == updated


def test_separate_magnetic_method_entrypoint_uses_current_context_without_archive_route():
    name = 'engineering/ferrite_maglev/README.md'
    updated = context.render('# Retained method\n\nOriginal method details.\n', name)
    assert 'OpenSourceRail v0.6 develops' in updated
    assert 'docs/archives/v0.5-maglev/README.md' not in updated
    assert context.category(name) == 'historical-method-entrypoint'
    assert updated.endswith('Original method details.\n')


def test_legacy_import_is_the_same_module_and_keeps_monkeypatch_compatibility(monkeypatch):
    from engineering.maglev_research import readme_context as old
    assert old is context
    monkeypatch.setattr(old, 'inventory', lambda root: ['README.md'])
    assert context.inventory(None) == ['README.md']


def test_coverage_binds_neutral_publisher_and_lists_current_entrypoints(tmp_path, monkeypatch):
    (tmp_path / 'README.md').write_text('# Project\n')
    monkeypatch.setattr(context, 'inventory', lambda root: ['README.md'])
    result = context.audit(tmp_path)
    assert result['current']
    assert result['source_sha256'] == {
        'engineering/readme_context.py': sha256(Path(context.__file__).read_bytes()).hexdigest()
    }
    rendered = context.markdown(result)
    assert '-m engineering.readme_context --check' in rendered
    assert 'maintained v0.6 entrypoints' in rendered
    assert 'engineering.maglev_research' not in rendered


def test_owned_context_cannot_overwrite_source_bound_evidence(tmp_path, monkeypatch):
    name = 'tools/README.md'
    target = tmp_path / name
    target.parent.mkdir()
    target.write_text('# Tools\n\nSource-bound original.\n')
    monkeypatch.setattr(context, 'OWNED', (name,))
    monkeypatch.setattr(context, 'inventory', lambda root: [name])
    monkeypatch.setattr(context, 'bindings', lambda root, names: {name: ['retained-receipt']})
    with pytest.raises(ValueError, match='alter numerical evidence'):
        context.write_owned(tmp_path)
    assert target.read_text() == '# Tools\n\nSource-bound original.\n'


def test_current_front_door_readmes_describe_current_workflows_without_old_app_labels():
    root = Path(context.__file__).resolve().parents[1]
    paths = (
        root / 'README.md',
        root / 'docs/open-source-rail-overview.md',
        root / 'docs/ARCHITECTURE.md',
        root / 'docs/first-adoptable-product.md',
        root / 'docs/capabilities/README.md',
        root / 'docs/capabilities/directory.md',
        root / 'docs/workbench/planning/README.md',
        root / 'engineering/trip_dynamics/README.md',
        root / 'docs/archives/pre-comfort-default/README.md',
    )
    forbidden = ('v0.4', 'v0.5', 'legacy', 'city studio', 'sim gui', 'occ gui')
    for path in paths:
        text = path.read_text().lower()
        assert not any(label in text for label in forbidden), path.relative_to(root)
