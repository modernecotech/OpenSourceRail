"""Research fixtures follow their checkout and reject accidental source mixing."""
import os
from pathlib import Path
import subprocess
import sys

import pytest

from engineering.research_test_support import evidence_root


def fixture_tree(root, *, source='same producer'):
    (root / 'engineering').mkdir(parents=True)
    (root / 'engineering/producer.py').write_text(source)
    (root / 'evidence.json').write_text('{"physical_accepted":false}')
    return root


def test_default_root_is_the_caller_checkout_without_a_developer_installation(tmp_path):
    checkout = tmp_path / 'arbitrary checkout with spaces'
    checkout.mkdir()
    assert evidence_root(checkout, required=('absent-fixture.json',),
                         sources=('engineering/producer.py',), environ={}) == checkout


def test_explicit_override_requires_existing_fixtures_and_identical_producers(tmp_path):
    checkout = fixture_tree(tmp_path / 'source')
    override = fixture_tree(tmp_path / 'fixture')
    arguments = dict(required=('evidence.json',), sources=('engineering/producer.py',),
                     environ={'OSR_EVIDENCE_ROOT': str(override)})
    assert evidence_root(checkout, **arguments) == override
    (override / 'engineering/producer.py').write_text('different evaluator')
    with pytest.raises(ValueError, match='source provenance differs'):
        evidence_root(checkout, **arguments)
    (override / 'engineering/producer.py').write_text('same producer')
    (override / 'evidence.json').unlink()
    with pytest.raises(ValueError, match='fixture/source missing'):
        evidence_root(checkout, **arguments)


@pytest.mark.parametrize('value', ['', '.', 'relative/fixtures'])
def test_invalid_override_never_falls_back_to_another_checkout(tmp_path, value):
    with pytest.raises(ValueError, match='absolute fixture root'):
        evidence_root(tmp_path, required=('evidence.json',), sources=('producer.py',),
                      environ={'OSR_EVIDENCE_ROOT': value})


def test_suite_specific_override_cannot_hide_a_conflicting_shared_root(tmp_path):
    with pytest.raises(ValueError, match='Conflicting explicit'):
        evidence_root(tmp_path, required=('evidence.json',), sources=('producer.py',),
            variable='OSR_SUSPENSION_EVIDENCE_ROOT', environ={
                'OSR_EVIDENCE_ROOT': str(tmp_path / 'first'),
                'OSR_SUSPENSION_EVIDENCE_ROOT': str(tmp_path / 'second')})


def test_unset_environment_uses_relocated_helper_in_an_isolated_process(tmp_path):
    """Only the test helper is available; the original checkout cannot be imported."""
    checkout = tmp_path / 'independent checkout'
    helper = checkout / 'engineering/research_test_support.py'
    helper.parent.mkdir(parents=True)
    original = Path(__file__).resolve().parents[2] / 'research_test_support.py'
    helper.write_bytes(original.read_bytes())
    run = """from pathlib import Path
from engineering.research_test_support import evidence_root
checkout = Path.cwd()
root = evidence_root(checkout, required=('unneeded.json',), sources=('unneeded.py',))
assert root == checkout
print(root)
"""
    environment = {key: value for key, value in os.environ.items()
                   if key not in ('OSR_EVIDENCE_ROOT', 'OSR_SUSPENSION_EVIDENCE_ROOT', 'PYTHONPATH')}
    result = subprocess.run([sys.executable, '-I', '-c',
        "import sys; sys.path.insert(0, '.'); " + run], cwd=checkout, env=environment,
        capture_output=True, text=True, check=True, timeout=15)
    assert result.stdout.strip() == str(checkout)


def test_actual_envelope_test_fixture_uses_relocated_checkout_without_a_developer_tree(tmp_path):
    """Exercise the fixture that previously hard-coded the author's checkout."""
    original = Path(__file__).resolve().parents[3]
    checkout = tmp_path / 'relocated research checkout'
    test_relative = 'engineering/comfort_options/tests/test_envelope.py'
    for relative in ('engineering/research_test_support.py', test_relative):
        target = checkout / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes((original / relative).read_bytes())
    # This local package excludes any installed engineering checkout. The stub
    # validates fixture routing only and supplies no physical calculation.
    (checkout / 'engineering/__init__.py').write_text('')
    (checkout / 'engineering/comfort_options/__init__.py').write_text('')
    (checkout / 'engineering/comfort_options/envelope.py').write_text(
        'from pathlib import Path\n'
        'def options(*, root):\n'
        '    assert root == Path(__file__).resolve().parents[2]\n'
        '    return ["relocated-fixture-root"]\n')
    code = """import importlib.util
from pathlib import Path
path = Path('engineering/comfort_options/tests/test_envelope.py')
spec = importlib.util.spec_from_file_location('relocated_envelope_tests', path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
assert module.rows.__wrapped__() == ['relocated-fixture-root']
print('actual test fixture uses the relocated checkout')
"""
    environment = {key: value for key, value in os.environ.items()
                   if key not in ('OSR_EVIDENCE_ROOT', 'OSR_SUSPENSION_EVIDENCE_ROOT', 'PYTHONPATH')}
    result = subprocess.run([sys.executable, '-I', '-c',
        "import sys; sys.path.insert(0, '.'); " + code], cwd=checkout, env=environment,
        capture_output=True, text=True, check=True, timeout=15)
    assert result.stdout.strip() == 'actual test fixture uses the relocated checkout'
