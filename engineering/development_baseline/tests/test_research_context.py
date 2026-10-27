"""Retained PM research cannot consume or impersonate the wheel selection."""
from copy import deepcopy
from pathlib import Path
from hashlib import sha256
import subprocess

import pytest

from engineering import research_context as research
from engineering import research_ancestry
from engineering.station_rail.common import identity
from engineering.suspension_closure import operating_point
from engineering.thermal_closure import comfort_fixes

ROOT = Path(__file__).resolve().parents[3]


@pytest.fixture(scope='module')
def retained():
    return research.retained_comfort(ROOT)


def test_explicit_archive_keeps_physical_ids_and_does_not_change_current_selection(retained):
    selector = ROOT / 'engineering/development-baseline.toml'
    before = selector.read_bytes()
    value = research.require_retained_maglev(retained, ROOT)
    assert value['research_configuration_id'] == identity(value['configuration'])
    assert value['vehicle']['candidate_id'] == research.CONFIGURATION['vehicle_candidate_id']
    assert value['vehicle']['magnet_component_id'] == research.CONFIGURATION['magnet_component_id']
    assert value['family'] == 'pm_maglev_station_powered'
    assert value['development_default'] is False
    assert 'selection_id' not in value
    assert value['vehicle']['mass']['installed_tare_kg_per_car'] is None
    assert all(value[key] is False for key in research.FLAGS)
    assert value['ancestry_source_sha256'] == value['vehicle']['source_sha256']
    assert 'engineering/development-baseline.toml' not in value['source_sha256']
    assert selector.read_bytes() == before
    value['vehicle']['mass']['accounted_tare_kg_per_car'] = 0
    assert research.retained_comfort(ROOT)['vehicle'] == retained['vehicle']


def test_wrong_family_or_revision_is_rejected_before_reading_any_payload(tmp_path, monkeypatch):
    def forbidden(*args, **kwargs):
        pytest.fail('Incompatible research request read physical evidence')
    monkeypatch.setattr(research, 'describe', forbidden)
    with pytest.raises(ValueError, match='compatible physical family'):
        research.retained_maglev(tmp_path, family='wheel_rail_station_lim', source_revision=research.REVISION)
    with pytest.raises(ValueError, match='pinned source revision'):
        research.retained_maglev(tmp_path, family='pm_maglev_station_powered', source_revision='0' * 40)


@pytest.mark.parametrize('target', ['family', 'configuration', 'vehicle', 'sources', 'acceptance'])
def test_resealed_or_mixed_retained_context_is_rejected(retained, target):
    value = deepcopy(retained)
    if target == 'family':
        value['family'] = 'wheel_rail_station_lim'
    elif target == 'configuration':
        value['configuration']['magnet_component_id'] = 'a' * 64
        value['research_configuration_id'] = identity(value['configuration'])
    elif target == 'vehicle':
        value['vehicle']['candidate_id'] = 'b' * 64
    elif target == 'sources':
        value['source_sha256'][research.CODE] = 'c' * 64
    else:
        value['physical_accepted'] = True
    with pytest.raises(ValueError, match='Retained PM-maglev'):
        research.require_retained_maglev(value, ROOT)


@pytest.mark.parametrize('entry', ['context', 'native-run', 'subject', 'evaluate', 'capture-run'])
def test_old_entrypoints_reject_wheel_context_before_solver_or_output(tmp_path, entry):
    wrong = dict(family='wheel_rail_station_lim', vehicle=dict(candidate_id='d' * 64))
    calls = {
        'context': lambda: operating_point.context(tmp_path, research_context=wrong),
        'native-run': lambda: operating_point.run(tmp_path / 'native', root=tmp_path, research_context=wrong),
        'subject': lambda: comfort_fixes.subject(tmp_path, research_context=wrong),
        'evaluate': lambda: comfort_fixes.evaluate(tmp_path, research_context=wrong),
        'capture-run': lambda: comfort_fixes.run(tmp_path / 'capture', root=tmp_path, research_context=wrong),
    }
    with pytest.raises(ValueError, match='compatible physical family'):
        calls[entry]()
    assert not list(tmp_path.iterdir())


def test_mutating_or_native_entrypoints_require_explicit_context(tmp_path):
    with pytest.raises(ValueError, match='Explicit retained PM-maglev research context'):
        operating_point.run(tmp_path / 'native', root=tmp_path)
    with pytest.raises(ValueError, match='Explicit retained PM-maglev research context'):
        comfort_fixes.run(tmp_path / 'capture', root=tmp_path)
    with pytest.raises(ValueError, match='Explicit retained PM-maglev research configuration'):
        operating_point.worker({'research_configuration': {'family': 'wheel_rail_station_lim'}}, tmp_path)
    assert not list(tmp_path.iterdir())


def test_ancestral_producer_and_live_input_have_independent_integrity_checks(tmp_path, monkeypatch):
    # A private local history exercises real Git lookup without network access.
    def git(*arguments):
        return subprocess.run(['git', '-C', str(tmp_path), *arguments],
                              check=True, capture_output=True, text=True).stdout.strip()
    git('init', '--quiet')
    producer = tmp_path / 'producer.py'
    data = tmp_path / 'material.json'
    producer.write_text('retained numerical producer\n')
    data.write_text('{"density": 2710}\n')
    bindings = {p.name: sha256(p.read_bytes()).hexdigest() for p in (producer, data)}
    git('add', 'producer.py', 'material.json')
    git('-c', 'user.name=Research fixture', '-c', 'user.email=fixture@example.invalid',
        '-c', 'core.hooksPath=/dev/null', '-c', 'commit.gpgsign=false',
        'commit', '--quiet', '-m', 'Immutable numerical ancestry fixture')
    revision = git('rev-parse', 'HEAD')
    producer.write_text('new independent evaluator\n')
    result = research_ancestry.verify(tmp_path, bindings, source_revision=revision)
    assert result['ancestry_source_sha256'] == bindings
    assert 'producer.py' not in result['source_sha256']
    assert result['source_sha256']['material.json'] == bindings['material.json']
    assert research_ancestry.CODE in result['source_sha256']

    # Historical data cannot authorize today's evaluator to read mutated input.
    data.write_text('{"density": 0}\n')
    with pytest.raises(ValueError, match='Retained live input differs'):
        research_ancestry.verify(tmp_path, bindings, source_revision=revision)
    data.write_text('{"density": 2710}\n')
    wrong = {**bindings, 'producer.py': 'a' * 64}
    with pytest.raises(ValueError, match='producer ancestry differs'):
        research_ancestry.verify(tmp_path, wrong, source_revision=revision)
    with pytest.raises(ValueError, match='ancestry unavailable locally'):
        research_ancestry.verify(tmp_path, bindings, source_revision='0' * 40)

    # Exercise the public cached-reader guard with real ancestry verification.
    from engineering.comfort_options import systems
    verifier = tmp_path / 'verifier.py'
    verifier.write_text('original verifier source\n')
    monkeypatch.setattr(research_ancestry, '__file__', str(verifier))
    monkeypatch.setattr(systems, 'ANCESTRY_REVISION', revision)
    live = research_ancestry.verify(tmp_path, bindings, source_revision=revision)['source_sha256']
    cached = dict(ancestry_source_sha256=bindings,
                  source_sha256={**live, 'engineering/comfort_options/systems.py':
                                 sha256(Path(systems.__file__).read_bytes()).hexdigest()})
    monkeypatch.setattr(systems, '_parent', lambda root: deepcopy(cached))
    assert systems.parent_evidence(tmp_path)['source_sha256'] == cached['source_sha256']
    verifier.write_text('changed verifier source\n')
    with pytest.raises(ValueError, match='projection source changed'):
        systems.parent_evidence(tmp_path)


def test_ancestry_live_inputs_reject_symlinked_parent_directories(tmp_path):
    checkout = tmp_path / 'checkout'
    checkout.mkdir()
    outside = tmp_path / 'outside'
    outside.mkdir()
    data = outside / 'material.json'
    data.write_text('{"density": 2710}\n')
    (checkout / 'materials').symlink_to(outside, target_is_directory=True)
    bindings = {'materials/material.json': sha256(data.read_bytes()).hexdigest()}
    with pytest.raises(ValueError, match='Ordinary retained source required'):
        research_ancestry.verify(checkout, bindings, source_revision='a' * 40)
