"""Current documentation context preserves historical scope and source identity."""
from hashlib import sha256
from pathlib import Path
import pytest
from engineering import readme_context as context


def test_current_entrypoints_describe_wheel_lim_without_historical_hardware_labels():
    text = '# Tools\n\nLocal implementation details.\n'
    updated = context.render(text, 'tools/README.md')
    assert updated.startswith('# Tools\n')
    assert 'Passive steel-wheel bogies' in updated and 'Station LIMs' in updated
    assert 'maglev' not in updated.lower()
    assert updated.endswith('Local implementation details.\n')
    assert context.render(updated, 'tools/README.md') == updated


def test_retained_method_entrypoints_keep_explicit_history_and_exact_archive_route():
    name = 'engineering/ferrite_maglev/README.md'
    updated = context.render('# Retained method\n\nOriginal method details.\n', name)
    assert 'historical magnetic-suspension research' in updated
    assert '../../docs/archives/v0.5-maglev/README.md' in updated
    assert context.category(name) == 'historical-method-entrypoint'
    assert updated.endswith('Original method details.\n')


def test_legacy_import_is_the_same_module_and_keeps_monkeypatch_compatibility(monkeypatch):
    from engineering.maglev_research import readme_context as old
    assert old is context
    monkeypatch.setattr(old, 'inventory', lambda root: ['README.md'])
    assert context.inventory(None) == ['README.md']


def test_coverage_binds_neutral_publisher_and_labels_city_history(tmp_path, monkeypatch):
    (tmp_path / 'README.md').write_text('# Project\n')
    monkeypatch.setattr(context, 'inventory', lambda root: ['README.md'])
    result = context.audit(tmp_path)
    assert result['current']
    assert result['source_sha256'] == {
        'engineering/readme_context.py': sha256(Path(context.__file__).read_bytes()).hexdigest()
    }
    rendered = context.markdown(result)
    assert '-m engineering.readme_context --check' in rendered
    assert 'city performance packages remain historical' in rendered
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
