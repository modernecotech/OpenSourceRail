"""Compiler intermediates are disposable only after retained evidence is sealed."""
from pathlib import Path

import pytest

from engineering.run_cache import cleanup_cargo_targets,sweep_terminal_runs
from engineering.station_rail.common import digest,encoded,identity


TAG = ('Signature: 8a477f597d28d172789f06886806bc55\n'
       '# This file is a cache directory tag created by cargo.\n')


def run(tmp_path):
    state = tmp_path/'run';state.mkdir()
    (state/'result.json').write_text('retained result')
    (state/'native-build.log').write_text('compiler diagnostics')
    target = state/'native-target';target.mkdir()
    (target/'CACHEDIR.TAG').write_text(TAG)
    (target/'release').mkdir();(target/'release/kernel').write_bytes(b'compiled')
    evidence = {n:digest(state/n) for n in ('result.json','native-build.log')}
    return state,target,evidence


def test_terminal_run_removes_only_owned_compiler_cache(tmp_path):
    state,target,evidence=run(tmp_path)
    (state/'native-runs').mkdir()
    (state/'native-runs/receipt.json').write_text('immutable receipt')
    assert cleanup_cargo_targets(state,['native-target'],evidence)==['native-target']
    assert not target.exists()
    assert (state/'result.json').read_text()=='retained result'
    assert (state/'native-runs/receipt.json').read_text()=='immutable receipt'
    assert cleanup_cargo_targets(state,['native-target'],evidence)==[]


def test_changed_or_missing_evidence_retains_compiler_cache(tmp_path):
    state,target,evidence=run(tmp_path)
    (state/'result.json').write_text('tampered')
    with pytest.raises(ValueError,match='evidence changed'):
        cleanup_cargo_targets(state,['native-target'],evidence)
    assert target.exists()


def test_unmarked_or_linked_target_is_retained(tmp_path):
    state,target,evidence=run(tmp_path)
    (target/'CACHEDIR.TAG').unlink()
    with pytest.raises(ValueError,match='marker required'):
        cleanup_cargo_targets(state,['native-target'],evidence)
    (target/'CACHEDIR.TAG').write_text(TAG)
    outside=tmp_path/'keep';outside.write_text('external')
    (target/'release/external').symlink_to(outside)
    with pytest.raises(ValueError,match='external or special'):
        cleanup_cargo_targets(state,['native-target'],evidence)
    assert outside.read_text()=='external' and target.exists()


def test_arbitrary_path_cannot_be_cleaned(tmp_path):
    state,target,evidence=run(tmp_path)
    for name in ('../keep','native-runs','/tmp/native-target'):
        with pytest.raises(ValueError,match='Unrecognised'):
            cleanup_cargo_targets(state,[name],evidence)
    assert target.exists()


def test_old_terminal_sweep_previews_then_removes_only_cache(tmp_path):
    runs=tmp_path/'runs';runs.mkdir()
    state,target,evidence=run(runs)
    (state/'native-build.json').write_text('sealed build')
    (state/'coordinator.lock').touch()
    manifest=dict(schema='osr-station-pair-run/1',files_sha256={'result.json':evidence['result.json']})
    manifest['manifest_id']=identity(manifest)
    (state/'manifest.json').write_bytes(encoded(manifest))
    preview=sweep_terminal_runs(runs,minimum_age_hours=0)
    assert preview['eligible_or_removed']==1 and target.exists()
    result=sweep_terminal_runs(runs,apply=True,minimum_age_hours=0)
    assert result['eligible_or_removed']==1 and not target.exists()
    assert (state/'result.json').read_text()=='retained result'


def test_sweep_retains_unfinished_run(tmp_path):
    runs=tmp_path/'runs';runs.mkdir()
    _,target,_=run(runs)
    result=sweep_terminal_runs(runs,apply=True,minimum_age_hours=0)
    assert result['held']==1 and result['eligible_or_removed']==0 and target.exists()
